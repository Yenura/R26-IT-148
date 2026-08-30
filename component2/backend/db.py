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

    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        logger.critical("MONGODB_URI not set — copy .env.example to .env and fill credentials")
        raise SystemExit(1)
    db_name = os.getenv("MONGODB_DB", os.getenv("DB_NAME", "HR"))

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        _mongo_db = client[db_name]
        logger.info("MongoDB connected for component2 persistence")
        # Create indexes (idempotent)
        _mongo_db["sessions"].create_index([("session_id", 1)], unique=True)
        _mongo_db["sessions"].create_index([("candidate_id", 1)])
        _mongo_db["sessions"].create_index([("created_at", -1)])
        _mongo_db["sessions"].create_index([("status", 1)])
        # TTL: auto-delete completed sessions after 30 days
        _mongo_db["sessions"].create_index(
            [("created_at", 1)],
            expireAfterSeconds=30 * 24 * 3600,
            partialFilterExpression={"status": "completed"},
        )
        _mongo_db["results"].create_index([("interview_id", 1)], unique=True)
        _mongo_db["results"].create_index([("candidate_id", 1)])
        _mongo_db["results"].create_index([("created_at", -1)])
        logger.info("C2 MongoDB indexes verified")
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


def _get_seen_question_ids_sync(candidate_id: str, limit: int = 1000) -> set:
    """Return question IDs the candidate has seen in past sessions."""
    mongo_db = _get_mongo_db()
    seen = set()
    if mongo_db is not None:
        for doc in mongo_db["sessions"].find(
            {"candidate_id": candidate_id},
            {"questions.id": 1}
        ).sort("created_at", -1).limit(limit):
            for q in doc.get("questions", []):
                qid = q.get("id")
                if qid:
                    seen.add(qid)
    else:
        for session in _memory_store["sessions"].values():
            if session.get("candidate_id") == candidate_id:
                for q in session.get("questions", []):
                    qid = q.get("id")
                    if qid:
                        seen.add(qid)
    return seen


async def get_seen_question_ids(candidate_id: str, limit: int = 1000) -> set:
    return await run_in_threadpool(_get_seen_question_ids_sync, candidate_id, limit)


def _link_candidate_application_sync(
    candidate_id: str,
    job_id: str,
    job_role: str,
    interview_score: float,
    mcq_score: float,
    desc_score: float,
    code_score: float
) -> None:
    mongo_db = _get_mongo_db()
    if mongo_db is None:
        return
    from bson import ObjectId
    from datetime import datetime, timezone

    cand_name = "Candidate User"
    resume_id = ""
    try:
        user_doc = mongo_db["users"].find_one({"_id": ObjectId(candidate_id)}) if ObjectId.is_valid(candidate_id) else mongo_db["users"].find_one({"_id": candidate_id})
        if user_doc:
            cand_name = user_doc.get("full_name", user_doc.get("email", "Candidate User"))
    except Exception:
        pass

    try:
        res_doc = mongo_db["resumes"].find_one({"candidate_id": candidate_id}, sort=[("created_at", -1)])
        if res_doc:
            resume_id = str(res_doc["_id"])
            if not cand_name or cand_name == "Candidate User":
                cand_name = res_doc.get("candidate_name", cand_name)
    except Exception:
        pass

    now = datetime.now(timezone.utc)

    # 1. Update or insert application for the specific job
    if job_id:
        try:
            job_oid = ObjectId(job_id) if ObjectId.is_valid(job_id) else job_id
            app_filter = {
                "$or": [
                    {"job_id": job_oid, "candidate_id": str(candidate_id)},
                    {"job_id": str(job_id), "candidate_id": str(candidate_id)},
                ]
            }
            app_update = {
                "$set": {
                    "job_id": job_oid if ObjectId.is_valid(job_id) else str(job_id),
                    "candidate_id": str(candidate_id),
                    "candidate_name": cand_name,
                    "resume_id": resume_id,
                    "status": "interview_completed",
                    "interview_completed": True,
                    "interview_score": round(interview_score, 2),
                    "mcq_score": round(mcq_score, 2),
                    "descriptive_score": round(desc_score, 2),
                    "coding_score": round(code_score, 2),
                    "applied_at": now,
                    "updated_at": now,
                }
            }
            mongo_db["applications"].update_one(app_filter, app_update, upsert=True)
            logger.info("Auto-linked application for candidate %s and job %s (Score: %.2f)", candidate_id, job_id, interview_score)
        except Exception as e:
            logger.warning("Failed to link application in db.py: %s", e)

    # 2. Update or insert into interview_scores
    try:
        score_doc = {
            "candidate_id": str(candidate_id),
            "candidate_name": cand_name,
            "job_id": str(job_id) if job_id else "",
            "job_role": job_role,
            "interview_score": round(interview_score, 2),
            "mcq_score": round(mcq_score, 2),
            "descriptive_score": round(desc_score, 2),
            "coding_score": round(code_score, 2),
            "created_at": now,
        }
        score_filter = {
            "candidate_id": str(candidate_id),
            "$or": [{"job_id": str(job_id)}, {"job_role": job_role}]
        } if job_id else {"candidate_id": str(candidate_id), "job_role": job_role}
        mongo_db["interview_scores"].update_one(score_filter, {"$set": score_doc}, upsert=True)
    except Exception as e:
        logger.warning("Failed to update interview_scores in db.py: %s", e)


async def link_candidate_application(
    candidate_id: str,
    job_id: str,
    job_role: str,
    interview_score: float,
    mcq_score: float,
    desc_score: float,
    code_score: float
) -> None:
    await run_in_threadpool(
        _link_candidate_application_sync,
        candidate_id,
        job_id,
        job_role,
        interview_score,
        mcq_score,
        desc_score,
        code_score
    )

