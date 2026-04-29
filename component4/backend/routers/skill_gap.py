"""Router: Skill Gap Analysis endpoints"""

from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
from models.schemas import SkillGapRequest
from services.ml_engine import run_skill_gap_analysis

router = APIRouter()


@router.post("/analyze", summary="Run full skill gap analysis for a candidate")
async def analyze_skill_gap(payload: SkillGapRequest, request: Request):
    db = request.app.state.db

    result = run_skill_gap_analysis(
        candidate_id      = payload.candidate_id,
        candidate_name    = payload.candidate_name,
        job_role          = payload.job_role,
        skills            = payload.skills,
        experience_years  = payload.experience_years,
        education         = payload.education,
        certifications    = payload.certifications or "None",
        cv_matching_score = payload.cv_matching_score,
        interview_score   = payload.interview_score,
        mcq_score         = payload.mcq_score,
        descriptive_score = payload.descriptive_score,
        coding_score      = payload.coding_score,
        weak_topics       = payload.weak_topics or [],
        failed_mcq_topics = payload.failed_mcq_topics or [],
    )

    # Persist to MongoDB
    doc = {**result, "created_at": datetime.utcnow()}
    await db.skill_gap_reports.replace_one(
        {"candidate_id": payload.candidate_id, "job_role": payload.job_role},
        doc,
        upsert=True,
    )

    return {"success": True, "data": result}


@router.get("/report/{candidate_id}", summary="Fetch latest skill gap report")
async def get_report(candidate_id: str, request: Request):
    db  = request.app.state.db
    doc = await db.skill_gap_reports.find_one(
        {"candidate_id": candidate_id},
        sort=[("created_at", -1)],
        projection={"_id": 0},
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"success": True, "data": doc}


@router.get("/reports", summary="List all skill gap reports (paginated)")
async def list_reports(request: Request, skip: int = 0, limit: int = 20):
    db   = request.app.state.db
    docs = await db.skill_gap_reports.find(
        {}, projection={"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    total = await db.skill_gap_reports.count_documents({})
    return {"success": True, "total": total, "data": docs}


@router.delete("/report/{candidate_id}", summary="Delete a candidate's report")
async def delete_report(candidate_id: str, request: Request):
    db = request.app.state.db
    res = await db.skill_gap_reports.delete_many({"candidate_id": candidate_id})
    return {"success": True, "deleted": res.deleted_count}
