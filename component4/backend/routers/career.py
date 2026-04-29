"""Router: Career Path & Learning Plan endpoints"""

from fastapi import APIRouter, Request, HTTPException
from models.schemas import CareerPathRequest
from services.ml_engine import (
    JOB_REQ, RESOURCES, CAREER_PATHS, ROLE_TRANSITIONS, compute_gap
)

router = APIRouter()


@router.post("/path", summary="Generate career path for a candidate")
async def generate_career_path(payload: CareerPathRequest, request: Request):
    db = request.app.state.db

    role = payload.current_role
    path = CAREER_PATHS.get(role, ["Junior", "Mid-level", "Senior", "Lead"])
    transitions = ROLE_TRANSITIONS.get(role, [])

    # Determine current level by experience
    level_idx = 0
    if payload.experience_years >= 8:
        level_idx = 3
    elif payload.experience_years >= 5:
        level_idx = 2
    elif payload.experience_years >= 2:
        level_idx = 1

    current_level = path[min(level_idx, len(path) - 1)]
    next_levels   = path[min(level_idx + 1, len(path) - 1):]

    # Skill gap for current role
    gap_score, miss_req, miss_opt, match_pct = compute_gap(
        payload.skills, role, payload.experience_years
    )

    result = {
        "candidate_id":    payload.candidate_id,
        "current_role":    role,
        "target_role":     payload.target_role,
        "current_level":   current_level,
        "next_milestones": next_levels,
        "lateral_options": transitions,
        "skill_match_pct": round(match_pct, 2),
        "missing_for_next_level": miss_req[:4],
        "path_nodes": [
            {"level": i + 1, "title": t, "current": t == current_level}
            for i, t in enumerate(path)
        ],
    }

    await db.career_paths.replace_one(
        {"candidate_id": payload.candidate_id},
        {**result},
        upsert=True,
    )
    return {"success": True, "data": result}


@router.get("/resources/{job_role}", summary="Get learning resources for a job role")
async def get_resources(job_role: str):
    if job_role not in JOB_REQ:
        raise HTTPException(404, f"Job role '{job_role}' not found")

    req = JOB_REQ[job_role]
    out = []
    for skill in req["required"] + req["optional"]:
        res = RESOURCES.get(skill)
        if res:
            out.append({"skill": skill, "priority": "Required" if skill in req["required"] else "Optional", **res})
    return {"success": True, "job_role": job_role, "resources": out}


@router.get("/roadmap/{candidate_id}", summary="Get saved roadmap for a candidate")
async def get_roadmap(candidate_id: str, request: Request):
    db  = request.app.state.db
    doc = await db.skill_gap_reports.find_one(
        {"candidate_id": candidate_id},
        sort=[("created_at", -1)],
        projection={"_id": 0, "roadmap_nodes": 1, "learning_plan": 1,
                    "career_path_suggestions": 1, "job_role": 1},
    )
    if not doc:
        raise HTTPException(404, "No roadmap found for candidate")
    return {"success": True, "data": doc}
