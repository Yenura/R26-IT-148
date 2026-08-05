"""CV API router — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Endpoints
---------
POST /api/v1/cv/analyze   — Parse + extract + classify + score + persist
POST /api/v1/cv/classify  — Classify only (no persistence)
POST /api/v1/cv/rank      — Batch ranking by JD similarity + cv_matching_score
GET  /api/v1/cv           — Paginated list of stored analyses
GET  /api/v1/cv/{candidate_id} — Single stored analysis
DELETE /api/v1/cv/{candidate_id}
GET  /api/v1/roles         — 20 canonical roles + required skills
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.models.schemas import (
    BatchRankItem,
    BatchRankRequest,
    BatchRankResponse,
    ClassifyRequest,
    ClassifyResponse,
    CVAnalysisResponse,
    CVTextRequest,
    DeleteResponse,
    PaginatedCVList,
    RoleAlternative,
    RoleInfo,
    RolesListResponse,
)
from backend.services import extractor, parser, scorer
from data.role_requirements import ALL_ROLES, REQUIRED_SKILLS, REQUIRED_YEARS

logger = logging.getLogger("component1.router.cv")
router = APIRouter()

_CANDIDATE_ID_RE = re.compile(r'^[A-Za-z0-9\-_]+$')


# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_predictor(request: Request):
    return request.app.state.predictor


def _get_matcher(request: Request):
    return request.app.state.matcher


def _get_db(request: Request):
    return request.app.state.db


def _make_candidate_id(provided: Optional[str] = None) -> str:
    if provided and _CANDIDATE_ID_RE.match(provided):
        return provided
    return str(uuid.uuid4()).replace("-", "_")


async def _full_analysis(
    text: str,
    candidate_id: str,
    candidate_name: str,
    job_description: Optional[str],
    predictor,
    matcher,
) -> CVAnalysisResponse:
    """Core pipeline: extract → classify → score → return."""
    features = extractor.extract(text)
    pred     = predictor.predict(text)

    jd_sim: Optional[float] = None
    if job_description and job_description.strip():
        jd_sim = matcher.compute(text, job_description)

    scores = scorer.score(
        role=pred.job_role,
        edu_level=features.edu_level,
        experience_years=features.experience_years,
        skills=features.skills,
        jd_similarity_score=jd_sim,
    )

    return CVAnalysisResponse(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        job_role=pred.job_role,
        role_confidence=pred.confidence,
        role_alternatives=[RoleAlternative(**a) for a in pred.alternatives],
        education=features.education,
        edu_level=features.edu_level,
        edu_relevance=features.edu_relevance,
        experience_years=features.experience_years,
        skills=features.skills,
        S_edu=scores.S_edu,
        S_exp=scores.S_exp,
        S_skill=scores.S_skill,
        skill_score_raw=scores.skill_score_raw,
        jd_similarity_score=scores.jd_similarity_score,
        cv_matching_score=scores.cv_matching_score,
        analysis_timestamp=datetime.now(timezone.utc),
    )


# ── GET /api/v1/roles ──────────────────────────────────────────────────────────

@router.get("/roles", response_model=RolesListResponse, summary="List all 20 canonical roles")
async def list_roles():
    """Return all 20 canonical job roles with their required skills and experience."""
    roles = [
        RoleInfo(
            role=role,
            required_skills=REQUIRED_SKILLS[role],
            required_years=REQUIRED_YEARS[role],
        )
        for role in ALL_ROLES
    ]
    return RolesListResponse(total=len(roles), roles=roles)


# ── POST /api/v1/cv/classify ───────────────────────────────────────────────────

@router.post("/classify", response_model=ClassifyResponse, summary="Role classification only")
async def classify_cv(
    payload: ClassifyRequest,
    predictor=Depends(_get_predictor),
):
    """Classify a resume text into one of the 20 canonical roles.
    Does not persist the result.
    """
    pred = predictor.predict(payload.text)
    return ClassifyResponse(
        job_role=pred.job_role,
        role_confidence=pred.confidence,
        role_alternatives=[RoleAlternative(**a) for a in pred.alternatives],
    )


# ── POST /api/v1/cv/analyze (JSON body) ───────────────────────────────────────

@router.post("/analyze", response_model=CVAnalysisResponse, status_code=status.HTTP_201_CREATED,
             summary="Analyze a CV (text or file upload)")
async def analyze_cv_text(
    payload: CVTextRequest,
    predictor=Depends(_get_predictor),
    matcher=Depends(_get_matcher),
    db=Depends(_get_db),
):
    """Analyze a CV supplied as raw text.
    Parses, extracts entities, classifies role, computes scores, persists to MongoDB.
    If `job_description` is provided, also computes `jd_similarity_score`.
    """
    candidate_id   = _make_candidate_id(payload.candidate_id)
    candidate_name = payload.candidate_name or "Unknown"
    text           = parser.extract_text_from_raw(payload.text)

    result = await _full_analysis(
        text=text,
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        job_description=payload.job_description,
        predictor=predictor,
        matcher=matcher,
    )
    await _upsert(db, result)
    return result


# ── POST /api/v1/cv/analyze-file (multipart form) ─────────────────────────────

@router.post("/analyze-file", response_model=CVAnalysisResponse, status_code=status.HTTP_201_CREATED,
             summary="Analyze a CV uploaded as a file (PDF / DOCX / TXT)")
async def analyze_cv_file(
    file:            UploadFile = File(...),
    candidate_id:    Optional[str] = Form(None),
    candidate_name:  Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    predictor=Depends(_get_predictor),
    matcher=Depends(_get_matcher),
    db=Depends(_get_db),
):
    data = await file.read()
    text = parser.extract_text_from_bytes(data, file.filename or "resume.txt")
    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from the uploaded file")

    c_id   = _make_candidate_id(candidate_id)
    c_name = (candidate_name or "Unknown").strip()

    result = await _full_analysis(
        text=text,
        candidate_id=c_id,
        candidate_name=c_name,
        job_description=job_description,
        predictor=predictor,
        matcher=matcher,
    )
    await _upsert(db, result)
    return result


# ── POST /api/v1/cv/rank ───────────────────────────────────────────────────────

@router.post("/rank", response_model=BatchRankResponse, summary="Batch rank candidates against a JD")
async def rank_candidates(
    payload:   BatchRankRequest,
    predictor=Depends(_get_predictor),
    matcher=Depends(_get_matcher),
    db=Depends(_get_db),
):
    """Given a job description + a list of CVs, rank candidates by cv_matching_score descending.

    This is the integration point for Component 3's ranking engine:
    it returns jd_similarity_score for every candidate alongside cv_matching_score.
    """
    results: List[CVAnalysisResponse] = []
    for candidate in payload.candidates:
        text = parser.extract_text_from_raw(candidate.text)
        c_id   = _make_candidate_id(candidate.candidate_id)
        c_name = candidate.candidate_name or "Unknown"
        analysis = await _full_analysis(
            text=text,
            candidate_id=c_id,
            candidate_name=c_name,
            job_description=payload.job_description,
            predictor=predictor,
            matcher=matcher,
        )
        results.append(analysis)
        await _upsert(db, analysis)

    # Sort by cv_matching_score descending, then jd_similarity_score descending
    results.sort(
        key=lambda r: (r.cv_matching_score, r.jd_similarity_score or 0.0),
        reverse=True,
    )

    ranked = [
        BatchRankItem(
            rank=i + 1,
            candidate_id=r.candidate_id,
            candidate_name=r.candidate_name,
            job_role=r.job_role,
            role_confidence=r.role_confidence,
            cv_matching_score=r.cv_matching_score,
            jd_similarity_score=r.jd_similarity_score,
            S_edu=r.S_edu,
            S_exp=r.S_exp,
            S_skill=r.S_skill,
            skill_score_raw=r.skill_score_raw,
        )
        for i, r in enumerate(results)
    ]

    return BatchRankResponse(
        job_description_snippet=payload.job_description[:200],
        total_candidates=len(ranked),
        ranked_candidates=ranked,
    )


# ── GET /api/v1/cv ────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedCVList, summary="Paginated list of stored CV analyses")
async def list_cvs(
    skip:  int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(_get_db),
):
    total = await db.cv_analyses.count_documents({})
    cursor = db.cv_analyses.find({}, {"_id": 0}).skip(skip).limit(limit).sort("analysis_timestamp", -1)
    items  = await cursor.to_list(length=limit)
    return PaginatedCVList(total=total, skip=skip, limit=limit, items=items)


# ── GET /api/v1/cv/{candidate_id} ────────────────────────────────────────────

@router.get("/{candidate_id}", response_model=CVAnalysisResponse, summary="Get stored CV analysis")
async def get_cv(candidate_id: str, db=Depends(_get_db)):
    doc = await db.cv_analyses.find_one({"candidate_id": candidate_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found")
    return doc


# ── DELETE /api/v1/cv/{candidate_id} ─────────────────────────────────────────

@router.delete("/{candidate_id}", response_model=DeleteResponse, summary="Delete stored CV analysis")
async def delete_cv(candidate_id: str, db=Depends(_get_db)):
    result = await db.cv_analyses.delete_one({"candidate_id": candidate_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found")
    return DeleteResponse(deleted=True, candidate_id=candidate_id, message="Analysis deleted.")


# ── DB helper ─────────────────────────────────────────────────────────────────

async def _upsert(db, result: CVAnalysisResponse):
    """Upsert (insert or replace) a CV analysis document."""
    doc = result.model_dump()
    # Convert datetime to ISO string for MongoDB storage
    if isinstance(doc.get("analysis_timestamp"), datetime):
        doc["analysis_timestamp"] = doc["analysis_timestamp"].isoformat()
    await db.cv_analyses.replace_one(
        {"candidate_id": result.candidate_id},
        doc,
        upsert=True,
    )
