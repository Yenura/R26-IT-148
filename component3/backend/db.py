"""Component 3 — storage layer (MongoDB when reachable, in-memory fallback)."""

import os
import uuid
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("component3")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "RANKING")


class MemoryStore:
    def __init__(self):
        self._cols = {}

    async def ping(self):
        return True

    def _col(self, name):
        return self._cols.setdefault(name, [])

    async def insert_one(self, name, doc):
        _id = doc.get("id") or str(uuid.uuid4())
        doc["id"] = _id
        self._col(name).append(doc)
        return _id

    async def insert_many(self, name, docs):
        ids = []
        for doc in docs:
            _id = doc.get("id") or str(uuid.uuid4())
            doc["id"] = _id
            self._col(name).append(doc)
            ids.append(_id)
        return ids

    async def update_one(self, name, query, values):
        for doc in self._col(name):
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(values)
                return True
        return False

    async def find_one(self, name, query):
        for doc in self._col(name):
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

    async def find_all(self, name, query=None):
        docs = self._col(name)
        if not query:
            return docs
        return [d for d in docs if all(d.get(k) == v for k, v in query.items())]

    async def delete(self, name, query):
        col = self._col(name)
        before = len(col)
        self._cols[name] = [d for d in col
                            if not all(d.get(k) == v for k, v in query.items())]
        return before - len(self._cols[name])


class MongoStore:
    def __init__(self, client, db_name):
        self._db = client[db_name]

    async def ping(self):
        await self._db.command("ping")
        return True

    async def insert_one(self, name, doc):
        if "id" not in doc:
            res = await self._db[name].insert_one(doc)
            doc.pop("_id", None)
            doc["id"] = str(res.inserted_id)
        else:
            await self._db[name].insert_one(doc)
            doc.pop("_id", None)
        return doc["id"]

    async def insert_many(self, name, docs):
        if not docs:
            return []
        # Ensure each doc has an id
        for doc in docs:
            if "id" not in doc:
                doc["id"] = str(uuid.uuid4())
        await self._db[name].insert_many(docs)
        return [doc["id"] for doc in docs]

    async def update_one(self, name, query, values):
        res = await self._db[name].update_one(query, {"$set": values})
        return res.modified_count > 0

    async def find_one(self, name, query):
        doc = await self._db[name].find_one(query, projection={"_id": 0})
        return doc

    async def find_all(self, name, query=None):
        cursor = self._db[name].find(query or {}, projection={"_id": 0})
        return await cursor.to_list(length=None)

    async def delete(self, name, query):
        res = await self._db[name].delete_many(query)
        return res.deleted_count


async def create_store():
    try:
        import motor.motor_asyncio
        client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGODB_URI, serverSelectionTimeoutMS=3000)
        await client.admin.command("ping")
        logger.info("MongoDB connected: %s/%s", MONGODB_URI.split("@")[-1], DB_NAME)
        return MongoStore(client, DB_NAME)
    except Exception as exc:
        logger.warning("MongoDB unavailable (%s) — using in-memory store", exc)
        return MemoryStore()
