"""Router: Career Path & Learning Plan endpoints"""

from fastapi import APIRouter, Request, HTTPException
from models.schemas import CareerPathRequest
from services.ml_engine import JOB_REQ, RESOURCES, CAREER_PATHS, ROLE_TRANSITIONS, compute_gap

router = APIRouter()

LEVEL_THRESHOLDS = {
    "Junior":            (0, 2),
    "Mid-Level":         (2, 5),
    "Senior":            (5, 9),
    "Lead":              (9, 13),
    "Principal / Staff": (13, 99),
}


def _exp_to_level(exp: int) -> int:
    if exp < 2:  return 0
    if exp < 5:  return 1
    if exp < 9:  return 2
    if exp < 13: return 3
    return 4


@router.post("/path", summary="Generate career path for a candidate")
async def generate_career_path(payload: CareerPathRequest, request: Request):
    db   = request.app.state.db
    role = payload.current_role
    path = CAREER_PATHS.get(role, ["Junior", "Mid-Level", "Senior", "Lead", "Principal"])
    transitions = ROLE_TRANSITIONS.get(role, [])

    level_idx     = _exp_to_level(payload.experience_years)
    current_level = path[min(level_idx, len(path) - 1)]
    next_levels   = path[min(level_idx + 1, len(path) - 1):]

    gap_score, miss_req, miss_opt, match_pct = compute_gap(
        payload.skills, role, payload.experience_years
    )

    result = {
        "candidate_id":          payload.candidate_id,
        "current_role":          role,
        "target_role":           payload.target_role,
        "current_level":         current_level,
        "next_milestones":       next_levels,
        "lateral_options":       transitions,
        "skill_match_pct":       round(match_pct, 2),
        "missing_for_next_level": miss_req[:5],
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


@router.get("/resources/{job_role}", summary="Get curated learning resources for a job role")
async def get_resources(job_role: str):
    if job_role not in JOB_REQ:
        raise HTTPException(404, f"Job role '{job_role}' not found. Available: {sorted(JOB_REQ.keys())}")

    req = JOB_REQ[job_role]
    out = []
    for skill in req.get("required", []) + req.get("optional", []):
        res = RESOURCES.get(skill)
        if not res:
            # try partial match
            for rk, rv in RESOURCES.items():
                if rk.lower() in skill.lower() or skill.lower() in rk.lower():
                    res = rv
                    break
        if not res:
            res = {
                "course":   f"{skill} — Coursera",
                "url":      f"https://www.coursera.org/search?query={skill.replace(' ', '+')}",
                "duration": "4 weeks",
                "level":    "Beginner",
            }
        out.append({
            "skill":    skill,
            "priority": "Required" if skill in req.get("required", []) else "Optional",
            **res,
        })
    return {"success": True, "job_role": job_role, "resources": out}


@router.get("/roles", summary="List all roles with career paths")
async def list_career_roles():
    return {"success": True, "roles": sorted(CAREER_PATHS.keys())}


@router.get("/roadmap/{candidate_id}", summary="Get saved roadmap for a candidate")
async def get_roadmap(candidate_id: str, request: Request):
    db  = request.app.state.db
    doc = await db.skill_gap_reports.find_one(
        {"candidate_id": candidate_id},
        sort=[("created_at", -1)],
        projection={
            "_id": 0,
            "roadmap_nodes": 1, "learning_plan": 1,
            "career_path_suggestions": 1, "job_role": 1,
        },
    )
    if not doc:
        raise HTTPException(404, "No roadmap found for this candidate")
    return {"success": True, "data": doc}
