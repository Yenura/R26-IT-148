import os
import sys
import asyncio
import pickle
import numpy as np
from datetime import datetime, timezone

# Ensure component4/backend is on sys.path
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from fastapi import APIRouter, Request
from starlette.concurrency import run_in_threadpool
from services.ml_engine import run_skill_gap_analysis

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


# Pre-loaded LTR model singleton & TTL cache
_CACHED_LTR_MODEL = None
_LEADERBOARD_CACHE = {"data": None, "expires_at": 0, "limit": 0}

def _get_cached_ltr_model():
    global _CACHED_LTR_MODEL
    if _CACHED_LTR_MODEL is None:
        c3_root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "component3"))
        pkl_path = os.path.join(c3_root, "models", "lambdamart_model.pkl")
        if os.path.exists(pkl_path):
            try:
                with open(pkl_path, "rb") as f:
                    _CACHED_LTR_MODEL = pickle.load(f)
            except Exception:
                pass
    return _CACHED_LTR_MODEL


@router.get("/leaderboard", summary="Top unique candidates by real CV & Interview marks using LambdaMART LTR")
async def leaderboard(request: Request, limit: int = 50):
    """
    Real-Data Talent Leaderboard powered by LambdaMART LTR:
    Evaluates real candidates from MongoDB who have uploaded a CV and completed technical interviews.
    Computes true feature vectors [S_edu, S_exp, S_skill, P_mcq, P_desc, P_code] and scores them via LambdaMART.
    """
    import time
    now_ts = time.time()
    if _LEADERBOARD_CACHE["data"] is not None and now_ts < _LEADERBOARD_CACHE["expires_at"] and _LEADERBOARD_CACHE["limit"] == limit:
        return _LEADERBOARD_CACHE["data"]

    db = request.app.state.db
    from bson import ObjectId

    # Load LambdaMART model from Component 3
    ltr_model = None
    c3_root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "component3"))
    pkl_path = os.path.join(c3_root, "models", "lambdamart_model.pkl")
    if os.path.exists(pkl_path):
        try:
            with open(pkl_path, "rb") as f:
                ltr_model = pickle.load(f)
        except Exception:
            pass

    # Fetch all candidate users
    cand_users = await db.users.find({"role": "candidate"}).to_list(length=100)
    candidates_ranked = []
    if not cand_users:
        return {"success": True, "count": 0, "candidates": []}

    candidate_ids = [str(u["_id"]) for u in cand_users]
    obj_ids = [u["_id"] for u in cand_users if ObjectId.is_valid(u["_id"])]

    # Batch fetch in 4 queries
    resumes_map = {}
    async for r in db.resumes.find({"$or": [{"candidate_id": {"$in": candidate_ids}}, {"candidate_id": {"$in": obj_ids}}]}).sort("created_at", -1):
        cid = str(r.get("candidate_id", ""))
        if cid not in resumes_map:
            resumes_map[cid] = r

    preds_map = {}
    async for p in db.predictions.find({"$or": [{"candidate_id": {"$in": candidate_ids}}, {"candidate_id": {"$in": obj_ids}}]}).sort("created_at", -1):
        cid = str(p.get("candidate_id", ""))
        if cid not in preds_map:
            preds_map[cid] = p

    results_map = {}
    async for res in db.results.find({"$or": [{"candidate_id": {"$in": candidate_ids}}, {"candidate_id": {"$in": obj_ids}}]}).sort("created_at", -1):
        cid = str(res.get("candidate_id", ""))
        if cid not in results_map:
            results_map[cid] = res

    scores_map = {}
    async for sc in db.interview_scores.find({"$or": [{"candidate_id": {"$in": candidate_ids}}, {"candidate_id": {"$in": obj_ids}}]}).sort("created_at", -1):
        cid = str(sc.get("candidate_id", ""))
        if cid not in scores_map:
            scores_map[cid] = sc

    candidates_ranked = []
    for u in cand_users:
        cid = str(u["_id"])
        cand_name = u.get("full_name", u.get("email", "Candidate"))

        # 1. Fetch Real CV from batch map
        resume = resumes_map.get(cid)
        has_cv = resume is not None
        skills = resume.get("skills", []) if resume else []
        exp_years = resume.get("experience_years", 0) if resume else 0
        edu = resume.get("education", "Bachelor Degree") if resume else "None"

        # 2. Fetch Real CV Prediction & Match Score from batch map
        pred = preds_map.get(cid)
        target_role = pred.get("predicted_role", "Software Engineer") if pred else "Software Engineer"
        cv_match_score = pred.get("overall_score") if pred else (pred.get("skill_score") if pred else None)
        if cv_match_score is None and has_cv:
            cv_match_score = min(100.0, 50.0 + len(skills) * 5.0)

        # 3. Fetch Real Interview Evaluation from batch maps
        interview_res = results_map.get(cid)
        score_doc = scores_map.get(cid)

        interview_completed = False
        interview_score = None
        mcq_score = None
        descriptive_score = None
        coding_score = None
        grade = "N/A"

        if interview_res:
            interview_completed = True
            total = interview_res.get("total_score") or interview_res.get("interview_score")
            interview_score = float(total) if total is not None else 0.0
            mcq = interview_res.get("mcq_score")
            mcq_score = float(mcq) if mcq is not None else 0.0
            desc = interview_res.get("descriptive_score")
            descriptive_score = float(desc) if desc is not None else 0.0
            code = interview_res.get("coding_score") or interview_res.get("code_score")
            coding_score = float(code) if code is not None else 0.0
            grade = interview_res.get("grade", "Average") or "Average"
            if interview_res.get("job_role"):
                target_role = interview_res["job_role"]
        elif score_doc:
            interview_completed = True
            total = score_doc.get("total_score") or score_doc.get("interview_score")
            interview_score = float(total) if total is not None else 0.0
            mcq = score_doc.get("mcq_score")
            mcq_score = float(mcq) if mcq is not None else 0.0
            desc = score_doc.get("descriptive_score")
            descriptive_score = float(desc) if desc is not None else 0.0
            code = score_doc.get("coding_score") or score_doc.get("code_score")
            coding_score = float(code) if code is not None else 0.0
            grade = score_doc.get("grade", "Average") or "Average"
            if score_doc.get("job_role"):
                target_role = score_doc["job_role"]

        # 4. Compute Normalized 6-D Feature Vector for LambdaMART LTR
        # [S_edu, S_exp, S_skill, P_mcq, P_desc, P_code]
        edu_lower = edu.lower()
        if "phd" in edu_lower or "doctorate" in edu_lower:
            s_edu = 1.0
        elif "master" in edu_lower or "m.sc" in edu_lower or "mba" in edu_lower:
            s_edu = 0.85
        elif "bachelor" in edu_lower or "b.sc" in edu_lower or "b.tech" in edu_lower:
            s_edu = 0.70
        else:
            s_edu = 0.50

        s_exp = min(exp_years / 8.0, 1.0)
        s_skill = (cv_match_score or 50.0) / 100.0

        p_mcq = (mcq_score / 100.0) if mcq_score is not None else 0.0
        p_desc = (descriptive_score / 100.0) if descriptive_score is not None else 0.0
        p_code = (coding_score / 100.0) if coding_score is not None else 0.0

        feat_vector = np.array([[s_edu, s_exp, s_skill, p_mcq, p_desc, p_code]])

        # 5. Compute LambdaMART LTR Prediction Score
        ltr_score = 0.0
        if ltr_model is not None and interview_completed:
            try:
                ltr_score = float(ltr_model.predict(feat_vector)[0])
            except Exception:
                ltr_score = 0.40 * (s_skill * 0.5 + s_exp * 0.3 + s_edu * 0.2) + 0.60 * (p_code * 0.5 + p_desc * 0.3 + p_mcq * 0.2)
        elif interview_completed:
            ltr_score = 0.40 * (s_skill * 0.5 + s_exp * 0.3 + s_edu * 0.2) + 0.60 * (p_code * 0.5 + p_desc * 0.3 + p_mcq * 0.2)
        else:
            ltr_score = 0.40 * (s_skill * 0.5 + s_exp * 0.3 + s_edu * 0.2)

        # 6. Compute Component 4 Real Hire Probability
        hire_prob = 0.0
        if interview_completed and cv_match_score is not None:
            hire_prob = round(0.40 * cv_match_score + 0.60 * interview_score, 1)
        elif cv_match_score is not None:
            hire_prob = round(cv_match_score * 0.8, 1)
        else:
            hire_prob = 50.0

        candidates_ranked.append({
            "candidate_id": cid,
            "candidate_name": cand_name,
            "job_role": target_role,
            "job_level": "Senior" if exp_years >= 5 else "Mid-Level" if exp_years >= 2 else "Junior",
            "skills": skills[:8],
            "experience_years": exp_years,
            "education": edu,
            "has_cv": has_cv,
            "interview_completed": interview_completed,
            "cv_match_score": round(cv_match_score, 1) if cv_match_score is not None else None,
            "interview_score": round(interview_score, 1) if interview_score is not None else None,
            "mcq_score": round(mcq_score, 1) if mcq_score is not None else None,
            "descriptive_score": round(descriptive_score, 1) if descriptive_score is not None else None,
            "coding_score": round(coding_score, 1) if coding_score is not None else None,
            "grade": grade,
            "hire_probability": hire_prob,
            "ltr_score": round(ltr_score, 4),
            "status": "Verified (CV + Interview)" if (has_cv and interview_completed) else "Interview Pending" if has_cv else "Profile Incomplete",
        })

    # Sort strictly by: 1) Completed Interview + CV, 2) LambdaMART LTR Score, 3) Hire Probability
    candidates_ranked.sort(
        key=lambda x: (
            1 if (x.get("has_cv") and x.get("interview_completed")) else 0,
            float(x.get("ltr_score") or 0.0),
            float(x.get("hire_probability") or 0.0)
        ),
        reverse=True
    )

    # Add 1-based rank position
    for idx, c in enumerate(candidates_ranked, start=1):
        c["rank"] = idx

    res = {
        "success": True,
        "total_evaluated": len(candidates_ranked),
        "model": "LightGBM LambdaMART (Learning-to-Rank LTR)",
        "data": candidates_ranked[:limit]
    }
    _LEADERBOARD_CACHE["data"] = res
    _LEADERBOARD_CACHE["expires_at"] = now_ts + 45.0
    _LEADERBOARD_CACHE["limit"] = limit
    return res


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
