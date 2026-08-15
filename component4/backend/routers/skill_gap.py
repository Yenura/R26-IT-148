"""Router: Skill Gap Analysis endpoints"""

import sys, os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from slowapi import Limiter
from slowapi.util import get_remote_address

COMPONENT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(COMPONENT_ROOT))

from models.schemas import SkillGapRequest
from services.ml_engine import run_skill_gap_analysis
from src.gap_analysis.skill_gap import analyze_skill_gap

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class SimpleSkillGapRequest(BaseModel):
    current_skills: Optional[List[str]] = None
    target_role: Optional[str] = None
    # Component 1 integration fields (Option 2)
    predicted_role: Optional[str] = None
    detected_skills: Optional[List[str]] = None


@router.post("", summary="Skill Gap Analysis (Simple JSON or Option 2 Component 1 Integration)")
@router.post("/", summary="Skill Gap Analysis (Simple JSON or Option 2 Component 1 Integration)")
async def simple_skill_gap(payload: Dict[str, Any]):
    """
    Accepts Option 1 (current_skills + target_role) or Option 2 (Component 1 output).
    """
    current_skills = payload.get("current_skills") or payload.get("detected_skills") or payload.get("skills") or []
    target_role = payload.get("target_role") or payload.get("predicted_role") or payload.get("job_role") or "Data Scientist"

    if not current_skills:
        current_skills = ["Python", "SQL"]

    res = analyze_skill_gap(current_skills=current_skills, target_role=target_role)

    missing_formatted = [
        {
            "skill": m["skill"],
            "priority": m["priority"],
            "priority_score": m["priority_score"]
        }
        for m in res["missing_skills"]
    ]

    return {
        "target_role": res["target_role"],
        "skill_coverage": res["skill_coverage_percentage"],
        "matched_skills": res["matched_skills"],
        "missing_skills": missing_formatted
    }


@router.post("/simulate", summary="Run 'What-If' skill acquisition simulation")
async def simulate_skill_acquisition(payload: Dict[str, Any]):
    current_skills = payload.get("current_skills") or []
    acquired_skills = payload.get("acquired_skills") or []
    target_role = payload.get("target_role") or "Data Scientist"

    combined_skills = list(set(current_skills + acquired_skills))

    res_orig = analyze_skill_gap(current_skills=current_skills, target_role=target_role)
    res_sim = analyze_skill_gap(current_skills=combined_skills, target_role=target_role)

    orig_pct = res_orig["skill_coverage_percentage"]
    sim_pct = res_sim["skill_coverage_percentage"]

    return {
        "target_role": target_role,
        "original_coverage": orig_pct,
        "simulated_coverage": sim_pct,
        "coverage_improvement": round(sim_pct - orig_pct, 2),
        "matched_skills": res_sim["matched_skills"],
        "remaining_missing_skills": [m["skill"] for m in res_sim["missing_skills"]]
    }


@router.get("/graph", summary="Get skill dependency DAG graph")
async def get_skill_dependency_graph():
    from src.recommendation.learning_path import SKILL_DEPENDENCY_GRAPH
    nodes = []
    edges = []
    seen_nodes = set()

    for target, deps in SKILL_DEPENDENCY_GRAPH.items():
        if target not in seen_nodes:
            seen_nodes.add(target)
            nodes.append({"id": target, "label": target})
        for dep in deps:
            if dep not in seen_nodes:
                seen_nodes.add(dep)
                nodes.append({"id": dep, "label": dep})
            edges.append({"source": dep, "target": target})

    return {"success": True, "nodes": nodes, "edges": edges}


@router.post("/analyze", summary="Run full skill gap analysis for a candidate")
@limiter.limit("10/minute")
async def analyze_skill_gap_full(request: Request, payload: SkillGapRequest):
    db = request.app.state.db

    # ── Validation ────────────────────────────────────────────────────────────
    if not payload.candidate_id.strip():
        raise HTTPException(status_code=422, detail="candidate_id cannot be empty")
    if not payload.candidate_name.strip():
        raise HTTPException(status_code=422, detail="candidate_name cannot be empty")
    if not payload.skills:
        raise HTTPException(status_code=422, detail="At least one skill is required")
    for score_field, val in [
        ("cv_matching_score", payload.cv_matching_score),
        ("interview_score",   payload.interview_score),
        ("mcq_score",         payload.mcq_score),
        ("descriptive_score", payload.descriptive_score),
        ("coding_score",      payload.coding_score),
    ]:
        if val is not None and not (0 <= val <= 100):
            raise HTTPException(status_code=422, detail=f"{score_field} must be 0-100")

    # Derive cert_count
    cert_count = payload.certifications_count or 0
    if cert_count == 0 and payload.certifications and payload.certifications != "None":
        cert_count = len([c.strip() for c in payload.certifications.split("|") if c.strip()])

    result = await run_in_threadpool(
        run_skill_gap_analysis,
        candidate_id      = payload.candidate_id.strip(),
        candidate_name    = payload.candidate_name.strip(),
        job_role          = payload.job_role,
        skills            = payload.skills,
        experience_years  = payload.experience_years,
        education         = payload.education or "B.Sc. Computer Science",
        certifications    = payload.certifications or "None",
        cert_count        = cert_count,
        projects_count    = payload.projects_count or 0,
        job_level         = payload.job_level or "Mid-Level",
        work_mode         = payload.work_mode or "Hybrid",
        cv_matching_score = payload.cv_matching_score,
        interview_score   = payload.interview_score,
        mcq_score         = payload.mcq_score,
        descriptive_score = payload.descriptive_score,
        coding_score      = payload.coding_score,
        weak_topics       = payload.weak_topics or [],
        failed_mcq_topics = payload.failed_mcq_topics or [],
    )

    doc = {**result, "created_at": datetime.now(timezone.utc)}
    await db.skill_gap_reports.insert_one(doc)
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
async def list_reports(request: Request, skip: int = 0, limit: int = 50):
    db    = request.app.state.db
    docs  = await db.skill_gap_reports.find(
        {}, projection={"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    total = await db.skill_gap_reports.count_documents({})
    return {"success": True, "total": total, "data": docs}


@router.delete("/report/{candidate_id}", summary="Delete a candidate's report")
async def delete_report(candidate_id: str, request: Request):
    db  = request.app.state.db
    res = await db.skill_gap_reports.delete_many({"candidate_id": candidate_id})
    return {"success": True, "deleted": res.deleted_count}


@router.get("/roles", summary="List all supported job roles")
async def list_roles():
    from services.ml_engine import JOB_REQ
    return {"success": True, "roles": sorted(JOB_REQ.keys()), "count": len(JOB_REQ)}
