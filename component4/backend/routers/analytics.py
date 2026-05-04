"""Router: Analytics & Dashboard summary endpoints"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/summary", summary="Aggregate analytics across all candidates")
async def analytics_summary(request: Request):
    db = request.app.state.db

    total = await db.skill_gap_reports.count_documents({})

    # Gap severity breakdown
    sev_cursor = db.skill_gap_reports.aggregate([
        {"$group": {"_id": "$gap_severity", "count": {"$sum": 1}}}
    ])
    sev_data = {d["_id"]: d["count"] async for d in sev_cursor}

    # Average scores
    avg_cursor = db.skill_gap_reports.aggregate([
        {"$group": {
            "_id":            None,
            "avg_gap_score":  {"$avg": "$gap_score"},
            "avg_match_pct":  {"$avg": "$skill_match_pct"},
            "avg_hire_prob":  {"$avg": "$hire_probability"},
            "avg_cv_score":   {"$avg": "$cv_matching_score"},
            "avg_interview":  {"$avg": "$interview_score"},
            "avg_projects":   {"$avg": "$projects_count"},
            "avg_certs":      {"$avg": "$certifications_count"},
        }}
    ])
    avg_data = {}
    async for d in avg_cursor:
        avg_data = d

    # Role distribution
    role_cursor = db.skill_gap_reports.aggregate([
        {"$group": {"_id": "$job_role", "count": {"$sum": 1}}}
    ])
    role_data = {d["_id"]: d["count"] async for d in role_cursor}

    # Job level breakdown
    level_cursor = db.skill_gap_reports.aggregate([
        {"$group": {"_id": "$job_level", "count": {"$sum": 1}}}
    ])
    level_data = {d["_id"]: d["count"] async for d in level_cursor}

    # Work mode breakdown
    mode_cursor = db.skill_gap_reports.aggregate([
        {"$group": {"_id": "$work_mode", "count": {"$sum": 1}}}
    ])
    mode_data = {d["_id"]: d["count"] async for d in mode_cursor}

    # Top missing required skills
    miss_cursor = db.skill_gap_reports.aggregate([
        {"$unwind": "$missing_required"},
        {"$group": {"_id": "$missing_required", "count": {"$sum": 1}}},
        {"$sort":  {"count": -1}},
        {"$limit": 10},
    ])
    missing_top = [{"skill": d["_id"], "count": d["count"]} async for d in miss_cursor]

    # Predicted hire stats
    hire_cursor = db.skill_gap_reports.aggregate([
        {"$group": {"_id": "$predicted_hire", "count": {"$sum": 1}}}
    ])
    hire_data = {str(d["_id"]): d["count"] async for d in hire_cursor}

    # Progress overview
    total_progress = await db.progress_tracking.count_documents({})
    prog_cursor    = db.progress_tracking.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ])
    prog_data = {d["_id"]: d["count"] async for d in prog_cursor}

    def _r(val, dec=1):
        v = avg_data.get(val, 0) or 0
        return round(v, dec)

    return {
        "success": True,
        "data": {
            "total_reports":     total,
            "gap_severity":      sev_data,
            "role_distribution": role_data,
            "level_distribution": level_data,
            "work_mode_distribution": mode_data,
            "hire_predictions":  hire_data,
            "averages": {
                "gap_score":        _r("avg_gap_score", 3),
                "skill_match_pct":  _r("avg_match_pct"),
                "hire_probability": _r("avg_hire_prob"),
                "cv_score":         _r("avg_cv_score"),
                "interview_score":  _r("avg_interview"),
                "projects_count":   _r("avg_projects"),
                "certifications":   _r("avg_certs"),
            },
            "top_missing_skills": missing_top,
            "progress_tracking": {
                "total_entries": total_progress,
                **prog_data,
            },
        }
    }


@router.get("/leaderboard", summary="Top candidates by hire probability")
async def leaderboard(request: Request, limit: int = 10):
    db   = request.app.state.db
    docs = await db.skill_gap_reports.find(
        {},
        projection={
            "_id": 0, "candidate_id": 1, "candidate_name": 1,
            "job_role": 1, "job_level": 1, "hire_probability": 1,
            "gap_severity": 1, "skill_match_pct": 1, "work_mode": 1,
        },
    ).sort("hire_probability", -1).limit(limit).to_list(length=limit)
    return {"success": True, "data": docs}


@router.get("/role-insights/{job_role}", summary="Analytics for a specific job role")
async def role_insights(job_role: str, request: Request):
    db = request.app.state.db
    pipeline = [
        {"$match": {"job_role": job_role}},
        {"$group": {
            "_id":           None,
            "count":         {"$sum": 1},
            "avg_match":     {"$avg": "$skill_match_pct"},
            "avg_hire_prob": {"$avg": "$hire_probability"},
            "avg_gap":       {"$avg": "$gap_score"},
        }}
    ]
    cursor = db.skill_gap_reports.aggregate(pipeline)
    result = {}
    async for d in cursor:
        result = d
    if not result:
        return {"success": True, "job_role": job_role, "data": {}}
    return {
        "success":  True,
        "job_role": job_role,
        "data": {
            "count":        result.get("count", 0),
            "avg_match":    round(result.get("avg_match",     0) or 0, 1),
            "avg_hire_prob": round(result.get("avg_hire_prob", 0) or 0, 1),
            "avg_gap_score": round(result.get("avg_gap",       0) or 0, 3),
        }
    }
