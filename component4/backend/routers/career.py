"""Router: Career Path & Learning Plan endpoints"""

from fastapi import APIRouter, Request, HTTPException
from models.schemas import CareerPathRequest
from services.ml_engine import JOB_REQ, RESOURCES, CAREER_PATHS, ROLE_TRANSITIONS, compute_gap

router = APIRouter()


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

    # Vertical progression: next levels within current role
    vertical_nodes = [
        {"level": i + 1, "title": t, "status": "current" if i == level_idx else "done" if i < level_idx else "upcoming"}
        for i, t in enumerate(path)
    ]

    # Horizontal transitions: lateral moves to other roles with skill analysis
    transition_options = []
    user_skills = set(s.lower() for s in payload.skills)
    for target_role in transitions:
        target_req = JOB_REQ.get(target_role, {})
        target_required = set(s.lower() for s in target_req.get("required", []))
        target_optional = set(s.lower() for s in target_req.get("optional", []))
        all_target = target_required | target_optional

        matching = user_skills & all_target
        missing_required = [s for s in target_req.get("required", []) if s.lower() not in user_skills]
        missing_optional = [s for s in target_req.get("optional", []) if s.lower() not in user_skills]

        readiness = (len(matching) / len(all_target) * 100) if all_target else 0
        transition_options.append({
            "target_role": target_role,
            "readiness_pct": round(readiness, 1),
            "matching_skills": sorted(matching),
            "missing_required": missing_required[:8],
            "missing_optional": missing_optional[:5],
            "difficulty": "Easy" if readiness >= 60 else "Medium" if readiness >= 35 else "Hard",
        })

    transition_options.sort(key=lambda t: t["readiness_pct"], reverse=True)

    # Gap analysis for current role
    gap_score, miss_req, miss_opt, match_pct = compute_gap(
        payload.skills, role, payload.experience_years
    )

    result = {
        "candidate_id":     payload.candidate_id,
        "current_role":     role,
        "target_role":      payload.target_role,
        "current_level":    current_level,
        "vertical_path":    vertical_nodes,
        "transitions":      transition_options,
        "skill_match_pct":  round(match_pct, 2),
        "missing_for_current": miss_req[:5],
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
