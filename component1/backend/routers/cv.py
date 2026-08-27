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
    job_id: Optional[str] = "JOB001",
    job_spec: Optional[Dict[str, Any]] = None,
    target_role: Optional[str] = None,
) -> CVAnalysisResponse:
    """Core pipeline: extract → classify → score → return 3 independent scores."""
    features = extractor.extract(text)
    pred     = predictor.predict(text)

    jd_sim: Optional[float] = None
    if job_description and job_description.strip():
        jd_sim = matcher.compute(text, job_description)

    req_skills = None
    req_years = None
    req_edu = None

    if job_spec:
        req_skills = job_spec.get("required_skills")
        req_years = job_spec.get("required_experience_years")
        req_edu = job_spec.get("required_education")

    scored_role = target_role if (target_role and target_role in ALL_ROLES) else pred.job_role

    scores = scorer.score(
        role=scored_role,
        edu_level=features.edu_level,
        experience_years=features.experience_years,
        skills=features.skills,
        jd_similarity_score=jd_sim,
        required_skills_spec=req_skills,
        required_years=req_years,
        required_education=req_edu,
        candidate_education=features.education,
    )

    return CVAnalysisResponse(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        job_id=job_id or "JOB001",
        job_role=pred.job_role,
        role_confidence=pred.confidence,
        role_alternatives=[
            RoleAlternative(
                role=a["role"],
                confidence=a.get("confidence", a.get("probability", 0.0)),
                probability=a.get("probability", a.get("confidence", 0.0)),
            )
            for a in pred.alternatives
        ],
        manual_review_recommended=getattr(pred, "manual_review_recommended", False),
        review_reason=getattr(pred, "review_reason", None),
        education=features.education,
        edu_level=features.edu_level,
        edu_relevance=features.edu_relevance,
        experience_years=features.experience_years,
        skills=features.skills,
        skill_evidence=getattr(features, "skill_evidence", {}),
        component_1_scores={
            "S_skill": scores.S_skill,
            "S_exp": scores.S_exp,
            "S_edu": scores.S_edu,
        },
        S_edu=scores.S_edu,
        S_exp=scores.S_exp,
        S_skill=scores.S_skill,
        skill_analysis=scores.skill_analysis.to_dict(),
        experience_analysis=scores.experience_analysis.to_dict(),
        education_analysis=scores.education_analysis.to_dict(),
        skill_score_raw=scores.skill_score_raw,
        jd_similarity_score=scores.jd_similarity_score,
        optional_legacy_score=scores.optional_legacy_score,
        cv_matching_score=scores.optional_legacy_score or 0.0,
        status="READY_FOR_COMPONENT_3",
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
        role_alternatives=[
            RoleAlternative(
                role=a["role"],
                confidence=a.get("confidence", a.get("probability", 0.0)),
                probability=a.get("probability", a.get("confidence", 0.0))
            )
            for a in pred.alternatives
        ],
        manual_review_recommended=getattr(pred, "manual_review_recommended", False),
        review_reason=getattr(pred, "review_reason", None),
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
    Parses, extracts entities, classifies role, computes 3 independent scores, persists to MongoDB.
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
        target_role=getattr(payload, "target_role", None),
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
    job_id:          Optional[str] = Form(None),
    predictor=Depends(_get_predictor),
    matcher=Depends(_get_matcher),
    db=Depends(_get_db),
):
    data = await file.read()
    text = parser.extract_text_from_bytes(data, file.filename or "resume.txt")
    if not text or not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from the uploaded file. Please ensure it is a valid PDF, DOCX, or TXT.")

    c_id   = _make_candidate_id(candidate_id)
    c_name = (candidate_name or "Unknown").strip()

    result = await _full_analysis(
        text=text,
        candidate_id=c_id,
        candidate_name=c_name,
        job_description=job_description,
        job_id=job_id or "JOB001",
        predictor=predictor,
        matcher=matcher,
    )
    await _upsert(db, result)
    return result


# ── POST /screen-resume / /api/v1/screen-resume ────────────────────────────────

@router.post("/screen-resume", summary="Screen CV file or text and return 3 independent scores for Component 3")
async def screen_resume(
    file: Optional[UploadFile] = File(None),
    job_id: Optional[str] = Form(None),
    candidate_id: Optional[str] = Form(None),
    candidate_name: Optional[str] = Form(None),
    predictor=Depends(_get_predictor),
    matcher=Depends(_get_matcher),
):
    """Screen uploaded CV file (PDF, DOCX, or TXT) against a job posting and return:
    - Component 1 Scores (S_skill, S_exp, S_edu)
    - Detailed skill, experience, and education matching breakdowns
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    filename = file.filename.lower()
    if not (filename.endswith(".pdf") or filename.endswith(".docx") or filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or TXT.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        text = parser.extract_text_from_bytes(contents, filename=file.filename)
    except Exception:
        raise HTTPException(status_code=422, detail="Failed to parse the uploaded file.")

    if not text or len(text.strip()) < 5:
        raise HTTPException(status_code=422, detail="Could not extract meaningful text from the uploaded file.")

    c_id = _make_candidate_id(candidate_id)
    c_name = (candidate_name or "Candidate").strip()
    j_id = job_id or "JOB001"

    features = extractor.extract(text)
    pred = predictor.predict(text)

    scores = scorer.score(
        role=pred.job_role,
        edu_level=features.edu_level,
        experience_years=features.experience_years,
        skills=features.skills,
        candidate_education=features.education,
    )

    return {
        "candidate_id": c_id,
        "candidate_name": c_name,
        "job_id": j_id,
        "predicted_role": pred.job_role,
        "confidence": pred.confidence,
        "screening_score": scores.optional_legacy_score or 0.0,
        "detected_skills": features.skills,
        "skill_evidence": getattr(features, "skill_evidence", {}),
        "scores": {
            "S_skill": scores.S_skill,
            "S_exp": scores.S_exp,
            "S_edu": scores.S_edu,
        },
        "component_1_scores": {
            "S_skill": scores.S_skill,
            "S_exp": scores.S_exp,
            "S_edu": scores.S_edu,
        },
        "skill_match": scores.skill_analysis.to_dict(),
        "experience_match": scores.experience_analysis.to_dict(),
        "education_match": scores.education_analysis.to_dict(),
        "status": "READY_FOR_COMPONENT_3",
        "manual_review_recommended": getattr(pred, "manual_review_recommended", False),
        "review_reason": getattr(pred, "review_reason", None),
        "top_roles": [
            {"role": alt["role"], "probability": alt.get("probability", alt.get("confidence", 0.0))}
            for alt in pred.alternatives[:5]
        ]
    }


# ── POST /screen-batch / /api/v1/screen-batch ────────────────────────────────

@router.post("/screen-batch", summary="Screen multiple candidate CVs against a job requirement")
async def screen_batch(
    payload: BatchRankRequest,
    predictor=Depends(_get_predictor),
    matcher=Depends(_get_matcher),
    db=Depends(_get_db),
):
    """Batch process multiple candidates applying for a particular job.
    Returns array of candidates with independent Component 1 scores (S_skill, S_exp, S_edu).
    """
    job_id = payload.job_id or "JOB001"
    job_spec_dict = payload.job_spec.model_dump() if payload.job_spec else None

    results = []
    for candidate in payload.candidates:
        text = parser.extract_text_from_raw(candidate.text)
        c_id = _make_candidate_id(candidate.candidate_id)
        c_name = candidate.candidate_name or "Unknown"

        analysis = await _full_analysis(
            text=text,
            candidate_id=c_id,
            candidate_name=c_name,
            job_description=payload.job_description,
            job_id=job_id,
            job_spec=job_spec_dict,
            predictor=predictor,
            matcher=matcher,
        )
        if db is not None:
            try:
                await _upsert(db, analysis)
            except Exception:
                pass
        results.append(analysis)

    return [
        {
            "candidate_id": r.candidate_id,
            "candidate_name": r.candidate_name,
            "job_id": job_id,
            "predicted_role": r.job_role,
            "component_1_scores": {
                "S_skill": r.S_skill,
                "S_exp": r.S_exp,
                "S_edu": r.S_edu,
            },
            "S_skill": r.S_skill,
            "S_exp": r.S_exp,
            "skill_match": r.skill_analysis.model_dump() if hasattr(r.skill_analysis, 'model_dump') else (r.skill_analysis if isinstance(r.skill_analysis, dict) else getattr(r.skill_analysis, 'dict', lambda: {})()),
            "experience_match": r.experience_analysis.model_dump() if hasattr(r.experience_analysis, 'model_dump') else (r.experience_analysis if isinstance(r.experience_analysis, dict) else getattr(r.experience_analysis, 'dict', lambda: {})()),
            "education_match": r.education_analysis.model_dump() if hasattr(r.education_analysis, 'model_dump') else (r.education_analysis if isinstance(r.education_analysis, dict) else getattr(r.education_analysis, 'dict', lambda: {})()),
            "status": "READY_FOR_COMPONENT_3",
        }
        for r in results
    ]


# ── POST /api/v1/cv/rank ───────────────────────────────────────────────────────

@router.post("/rank", response_model=BatchRankResponse, summary="Batch process candidates against a JD for Component 3 handoff")
async def rank_candidates(
    payload:   BatchRankRequest,
    predictor=Depends(_get_predictor),
    matcher=Depends(_get_matcher),
    db=Depends(_get_db),
):
    """Given a job specification/description + a list of CVs, compute 3 independent scores per candidate."""
    results: List[CVAnalysisResponse] = []
    job_id = payload.job_id or "JOB001"
    job_spec_dict = payload.job_spec.model_dump() if payload.job_spec else None

    for candidate in payload.candidates:
        text = parser.extract_text_from_raw(candidate.text)
        c_id   = _make_candidate_id(candidate.candidate_id)
        c_name = candidate.candidate_name or "Unknown"
        analysis = await _full_analysis(
            text=text,
            candidate_id=c_id,
            candidate_name=c_name,
            job_description=payload.job_description,
            job_id=job_id,
            job_spec=job_spec_dict,
            predictor=predictor,
            matcher=matcher,
        )
        results.append(analysis)
        if db is not None:
            try:
                await _upsert(db, analysis)
            except Exception:
                pass

    ranked = [
        BatchRankItem(
            rank=i + 1,
            candidate_id=r.candidate_id,
            candidate_name=r.candidate_name,
            job_role=r.job_role,
            role_confidence=r.role_confidence,
            component_1_scores=r.component_1_scores,
            S_edu=r.S_edu,
            S_exp=r.S_exp,
            S_skill=r.S_skill,
            skill_analysis=r.skill_analysis,
            experience_analysis=r.experience_analysis,
            education_analysis=r.education_analysis,
            cv_matching_score=r.optional_legacy_score,
            jd_similarity_score=r.jd_similarity_score,
            status="READY_FOR_COMPONENT_3",
        )
        for i, r in enumerate(results)
    ]

    return BatchRankResponse(
        job_id=job_id,
        job_description_snippet=(payload.job_description[:200] if payload.job_description else "Job Requirement Profile"),
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
    if isinstance(doc.get("analysis_timestamp"), datetime):
        doc["analysis_timestamp"] = doc["analysis_timestamp"].isoformat()
    await db.cv_analyses.replace_one(
        {"candidate_id": result.candidate_id},
        doc,
        upsert=True,
    )

