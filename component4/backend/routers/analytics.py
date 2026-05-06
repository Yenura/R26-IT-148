"""Router: Analytics & Dashboard summary endpoints

Fixes applied (code review):
  - H4: Analytics summary now fires all 8 DB queries in parallel (asyncio.gather)
  - M4: Leaderboard deduplicates by candidate_id (latest report per candidate)
"""

import asyncio
from fastapi import APIRouter, Request

router = APIRouter()


# ── Private helpers — each runs one aggregation ───────────────────────────────

async def _get_severity(db) -> dict:
    cursor = db.skill_gap_reports.aggregate([
        {"$group": {"_id": "$gap_severity", "count": {"$sum": 1}}}
    ])
    return {d["_id"]: d["count"] async for d in cursor}


async def _get_averages(db) -> dict:
    cursor = db.skill_gap_reports.aggregate([
        {"$group": {
            "_id":           None,
            "avg_gap_score": {"$avg": "$gap_score"},
            "avg_match_pct": {"$avg": "$skill_match_pct"},
            "avg_hire_prob": {"$avg": "$hire_probability"},
            "avg_cv_score":  {"$avg": "$cv_matching_score"},
            "avg_interview": {"$avg": "$interview_score"},
            "avg_projects":  {"$avg": "$projects_count"},
            "avg_certs":     {"$avg": "$certifications_count"},
        }}
    ])
    async for d in cursor:
        return d
    return {}


async def _get_role_dist(db) -> dict:
    cursor = db.skill_gap_reports.aggregate([
        {"$group": {"_id": "$job_role", "count": {"$sum": 1}}}
    ])
    return {d["_id"]: d["count"] async for d in cursor}


async def _get_level_dist(db) -> dict:
    cursor = db.skill_gap_reports.aggregate([
        {"$group": {"_id": "$job_level", "count": {"$sum": 1}}}
    ])
    return {d["_id"]: d["count"] async for d in cursor}


async def _get_mode_dist(db) -> dict:
    cursor = db.skill_gap_reports.aggregate([
        {"$group": {"_id": "$work_mode", "count": {"$sum": 1}}}
    ])
    return {d["_id"]: d["count"] async for d in cursor}


async def _get_missing_skills(db) -> list:
    cursor = db.skill_gap_reports.aggregate([
        {"$unwind": "$missing_required"},
        {"$group":  {"_id": "$missing_required", "count": {"$sum": 1}}},
        {"$sort":   {"count": -1}},
        {"$limit":  10},
    ])
    return [{"skill": d["_id"], "count": d["count"]} async for d in cursor]


async def _get_hire_predictions(db) -> dict:
    cursor = db.skill_gap_reports.aggregate([
        {"$group": {"_id": "$predicted_hire", "count": {"$sum": 1}}}
    ])
    return {str(d["_id"]): d["count"] async for d in cursor}


async def _get_progress_summary(db) -> dict:
    total   = await db.progress_tracking.count_documents({})
    cursor  = db.progress_tracking.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ])
    by_status = {d["_id"]: d["count"] async for d in cursor}
    return {"total_entries": total, **by_status}


def _round_avg(avg_data: dict, key: str, dec: int = 1) -> float:
    """Safely round an average value from the aggregation result."""
    return round(avg_data.get(key, 0) or 0, dec)


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.get("/summary", summary="Aggregate analytics across all candidates")
async def analytics_summary(request: Request):
    db = request.app.state.db
    total = await db.skill_gap_reports.count_documents({})

    # H4 fix: run all queries in parallel
    (
        sev_data, avg_data, role_data, level_data,
        mode_data, missing_top, hire_data, prog_data,
    ) = await asyncio.gather(
        _get_severity(db),
        _get_averages(db),
        _get_role_dist(db),
        _get_level_dist(db),
        _get_mode_dist(db),
        _get_missing_skills(db),
        _get_hire_predictions(db),
        _get_progress_summary(db),
    )

    return {
        "success": True,
        "data": {
            "total_reports":          total,
            "gap_severity":           sev_data,
            "role_distribution":      role_data,
            "level_distribution":     level_data,
            "work_mode_distribution": mode_data,
            "hire_predictions":       hire_data,
            "averages": {
                "gap_score":        _round_avg(avg_data, "avg_gap_score", 3),
                "skill_match_pct":  _round_avg(avg_data, "avg_match_pct"),
                "hire_probability": _round_avg(avg_data, "avg_hire_prob"),
                "cv_score":         _round_avg(avg_data, "avg_cv_score"),
                "interview_score":  _round_avg(avg_data, "avg_interview"),
                "projects_count":   _round_avg(avg_data, "avg_projects"),
                "certifications":   _round_avg(avg_data, "avg_certs"),
            },
            "top_missing_skills": missing_top,
            "progress_tracking":  prog_data,
        },
    }


@router.get("/leaderboard", summary="Top unique candidates by hire probability")
async def leaderboard(request: Request, limit: int = 10):
    """
    M4 fix: Groups by candidate_id so each candidate appears only once,
    using their most recent report (sorted by created_at desc).
    """
    db = request.app.state.db
    pipeline = [
        {"$sort": {"created_at": -1}},
        {"$group": {
            "_id":             "$candidate_id",
            "candidate_name":  {"$first": "$candidate_name"},
            "job_role":        {"$first": "$job_role"},
            "job_level":       {"$first": "$job_level"},
            "work_mode":       {"$first": "$work_mode"},
            "hire_probability":{"$first": "$hire_probability"},
            "gap_severity":    {"$first": "$gap_severity"},
            "skill_match_pct": {"$first": "$skill_match_pct"},
        }},
        {"$sort":  {"hire_probability": -1}},
        {"$limit": limit},
        {"$project": {
            "_id":             0,
            "candidate_id":    "$_id",
            "candidate_name":  1,
            "job_role":        1,
            "job_level":       1,
            "work_mode":       1,
            "hire_probability":1,
            "gap_severity":    1,
            "skill_match_pct": 1,
        }},
    ]
    docs = await db.skill_gap_reports.aggregate(pipeline).to_list(length=limit)
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
        }},
    ]
    result = {}
    async for doc in db.skill_gap_reports.aggregate(pipeline):
        result = doc

    if not result:
        return {"success": True, "job_role": job_role, "data": {}}

    return {
        "success":  True,
        "job_role": job_role,
        "data": {
            "count":         result.get("count", 0),
            "avg_match":     round(result.get("avg_match",     0) or 0, 1),
            "avg_hire_prob": round(result.get("avg_hire_prob", 0) or 0, 1),
            "avg_gap_score": round(result.get("avg_gap",       0) or 0, 3),
        },
    }
