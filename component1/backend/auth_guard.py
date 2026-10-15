"""Shared Auth Guard for RecruitAI Microservices.

Enforces JWT authentication and job/user-scoped data isolation.
"""
import os
import logging
from typing import Set, Dict, Any
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError
from bson import ObjectId

logger = logging.getLogger("auth_guard")

JWT_SECRET = os.getenv("JWT_SECRET", "recruitai-dev-secret-key-change-in-prod")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")


async def require_identity(request: Request) -> Dict[str, Any]:
    """Validate caller identity from Bearer JWT or shared internal service key."""
    # 1. Trusted internal service call with shared key
    int_key = os.getenv("INTERNAL_API_KEY", INTERNAL_API_KEY)
    header_key = request.headers.get("X-Internal-Key", "")
    if int_key and header_key and header_key == int_key:
        return {"sub": "internal_service", "role": "service", "email": "service@recruitai.internal"}

    # 2. Bearer token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
        )

    token = auth_header.split(" ", 1)[1].strip()
    secret = os.getenv("JWT_SECRET", JWT_SECRET)
    algo = os.getenv("JWT_ALGORITHM", JWT_ALGORITHM)

    try:
        payload = jwt.decode(token, secret, algorithms=[algo])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    sub = str(payload.get("sub", ""))
    role = str(payload.get("role", "candidate"))
    email = str(payload.get("email", ""))
    return {"sub": sub, "role": role, "email": email}


def require_owner(identity: Dict[str, Any], candidate_id: str) -> None:
    """Ensure candidate caller only accesses their own resources."""
    role = identity.get("role")
    if role in ("service", "admin", "company"):
        return
    sub = str(identity.get("sub", "")).strip()
    target = str(candidate_id or "").strip()
    if target and sub and target != sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: cannot access another candidate's data",
        )


def require_owner_or_service(identity: Dict[str, Any], candidate_id: str) -> None:
    """Ensure candidate caller is resource owner, or caller is a service/company."""
    role = identity.get("role")
    if role in ("service", "admin", "company"):
        return
    if role == "candidate":
        sub = str(identity.get("sub", "")).strip()
        target = str(candidate_id or "").strip()
        if target and sub and target != sub:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: cannot access another candidate's data",
            )


async def company_applicant_candidate_ids(db, company_id: str) -> Set[str]:
    """Retrieve all candidate IDs who have applied to jobs belonging to company_id."""
    candidate_ids: Set[str] = set()
    if db is None or not company_id:
        return candidate_ids

    try:
        comp_queries = [{"company_id": str(company_id)}]
        try:
            comp_queries.append({"company_id": ObjectId(company_id)})
        except Exception:
            pass

        company_jobs = await db.jobs.find({"$or": comp_queries}, {"_id": 1}).to_list(1000)
        job_ids = []
        for j in company_jobs:
            job_ids.append(str(j["_id"]))
            job_ids.append(j["_id"])

        if job_ids:
            cursor = db.applications.find({"job_id": {"$in": job_ids}}, {"candidate_id": 1})
            async for app in cursor:
                cid = app.get("candidate_id")
                if cid:
                    candidate_ids.add(str(cid))
    except Exception as exc:
        logger.warning(f"company_applicant_candidate_ids query error: {exc}")

    return candidate_ids
