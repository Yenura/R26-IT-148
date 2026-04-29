"""Router: Analytics & Dashboard summary endpoints"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/summary", summary="Aggregate summary across all candidates")
async def analytics_summary(request: Request):
    db = request.app.state.db

    total = await db.skill_gap_reports.count_documents({})

    # Gap severity breakdown
    pipeline_sev = [
        {"$group": {"_id": "$gap_severity", "count": {"$sum": 1}}}
    ]
    sev_cursor = db.skill_gap_reports.aggregate(pipeline_sev)
    sev_data   = {d["_id"]: d["count"] async for d in sev_cursor}

    # Avg scores
    pipeline_avg = [
        {"$group": {
            "_id": None,
            "avg_gap_score":    {"$avg": "$gap_score"},
            "avg_match_pct":    {"$avg": "$skill_match_pct"},
            "avg_hire_prob":    {"$avg": "$hire_probability"},
            "avg_cv_score":     {"$avg": "$cv_matching_score"},
            "avg_interview":    {"$avg": "$interview_score"},
        }}
    ]
    avg_cursor = db.skill_gap_reports.aggregate(pipeline_avg)
    avg_data   = {}
    async for d in avg_cursor:
        avg_data = d

    # Role distribution
    pipeline_role = [
        {"$group": {"_id": "$job_role", "count": {"$sum": 1}}}
    ]
    role_cursor = db.skill_gap_reports.aggregate(pipeline_role)
    role_data   = {d["_id"]: d["count"] async for d in role_cursor}

    # Most common missing skills
    pipeline_miss = [
        {"$unwind": "$missing_required"},
        {"$group": {"_id": "$missing_required", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 8},
    ]
    miss_cursor  = db.skill_gap_reports.aggregate(pipeline_miss)
    missing_top  = [{"skill": d["_id"], "count": d["count"]} async for d in miss_cursor]

    # Progress overview
    total_progress = await db.progress_tracking.count_documents({})
    pipeline_prog  = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    prog_cursor = db.progress_tracking.aggregate(pipeline_prog)
    prog_data   = {d["_id"]: d["count"] async for d in prog_cursor}

    return {
        "success": True,
        "data": {
            "total_reports":    total,
            "gap_severity":     sev_data,
            "role_distribution": role_data,
            "averages": {
                "gap_score":       round(avg_data.get("avg_gap_score",   0) or 0, 3),
                "skill_match_pct": round(avg_data.get("avg_match_pct",   0) or 0, 1),
                "hire_probability": round(avg_data.get("avg_hire_prob",  0) or 0, 1),
                "cv_score":        round(avg_data.get("avg_cv_score",    0) or 0, 1),
                "interview_score": round(avg_data.get("avg_interview",   0) or 0, 1),
            },
            "top_missing_skills":  missing_top,
            "progress_tracking": {
                "total_entries": total_progress,
                **prog_data
            },
        }
    }


@router.get("/leaderboard", summary="Top candidates by hire probability")
async def leaderboard(request: Request, limit: int = 10):
    db   = request.app.state.db
    docs = await db.skill_gap_reports.find(
        {},
        projection={"_id": 0, "candidate_id": 1, "candidate_name": 1,
                    "job_role": 1, "hire_probability": 1, "gap_severity": 1,
                    "skill_match_pct": 1},
    ).sort("hire_probability", -1).limit(limit).to_list(length=limit)
    return {"success": True, "data": docs}
