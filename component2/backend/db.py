"""
Component 2: Interview System - Persistence Layer
Provides MongoDB-backed storage with in-memory fallback for local runs.
All DB operations are sync pymongo wrapped in run_in_threadpool for async safety.
"""

from __future__ import annotations

import logging
import os
from copy import deepcopy
from functools import partial
from typing import Any, Dict, Optional

from pymongo import MongoClient
from pymongo.database import Database
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

_mongo_db: Optional[Database] = None
_memory_store = {
    "sessions": {},
    "results": {},
}


class _InMemoryDB:
    """Small shim so startup logging can read .name."""
    name = "component2_in_memory"


def _get_mongo_db() -> Optional[Database]:
    """Connect to MongoDB once and cache the handle."""
    global _mongo_db
    if _mongo_db is not None:
        return _mongo_db

    mongo_uri = os.getenv("MONGODB_URI", "mongodb+srv://admin:PxUm8dLzq5jqlHYN@coordinator.ljarc.mongodb.net/HR")
    db_name = os.getenv("MONGODB_DB", os.getenv("DB_NAME", "HR"))

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        _mongo_db = client[db_name]
        logger.info("MongoDB connected for component2 persistence")
        return _mongo_db
    except Exception as exc:
        logger.warning("MongoDB unavailable, falling back to in-memory store: %s", exc)
        return None


def get_db() -> Any:
    mongo_db = _get_mongo_db()
    return mongo_db if mongo_db is not None else _InMemoryDB()


# ── Sync helpers (run via run_in_threadpool) ───────────────────

def _save_session_sync(session: Dict[str, Any]) -> None:
    session_id = session.get("session_id")
    if not session_id:
        raise ValueError("session_id is required")
    mongo_db = _get_mongo_db()
    if mongo_db is not None:
        mongo_db["sessions"].replace_one({"session_id": session_id}, session, upsert=True)
        return
    _memory_store["sessions"][session_id] = deepcopy(session)


def _get_session_sync(session_id: str) -> Optional[Dict[str, Any]]:
    mongo_db = _get_mongo_db()
    if mongo_db is not None:
        doc = mongo_db["sessions"].find_one({"session_id": session_id})
        if not doc:
            return None
        doc.pop("_id", None)
        return doc
    session = _memory_store["sessions"].get(session_id)
    return deepcopy(session) if session else None


def _update_session_status_sync(session_id: str, status: str) -> None:
    mongo_db = _get_mongo_db()
    if mongo_db is not None:
        mongo_db["sessions"].update_one(
            {"session_id": session_id},
            {"$set": {"status": status}},
            upsert=False,
        )
        return
    session = _memory_store["sessions"].get(session_id)
    if session:
        session["status"] = status


def _save_result_sync(result: Dict[str, Any]) -> None:
    interview_id = result.get("interview_id")
    if not interview_id:
        raise ValueError("interview_id is required")
    mongo_db = _get_mongo_db()
    if mongo_db is not None:
        mongo_db["results"].replace_one({"interview_id": interview_id}, result, upsert=True)
        return
    _memory_store["results"][interview_id] = deepcopy(result)


def _get_result_sync(interview_id: str) -> Optional[Dict[str, Any]]:
    mongo_db = _get_mongo_db()
    if mongo_db is not None:
        doc = mongo_db["results"].find_one({"interview_id": interview_id})
        if not doc:
            return None
        doc.pop("_id", None)
        return doc
    result = _memory_store["results"].get(interview_id)
    return deepcopy(result) if result else None


# ── Async wrappers (non-blocking) ─────────────────────────────

async def save_session(session: Dict[str, Any]) -> None:
    await run_in_threadpool(_save_session_sync, session)


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    return await run_in_threadpool(_get_session_sync, session_id)


async def update_session_status(session_id: str, status: str) -> None:
    await run_in_threadpool(_update_session_status_sync, session_id, status)


async def save_result(result: Dict[str, Any]) -> None:
    await run_in_threadpool(_save_result_sync, result)


async def get_result(interview_id: str) -> Optional[Dict[str, Any]]:
    return await run_in_threadpool(_get_result_sync, interview_id)
