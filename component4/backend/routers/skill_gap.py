"""Router: Skill Gap Analysis endpoints"""

import sys, os, asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from slowapi import Limiter
from slowapi.util import get_remote_address

COMPONENT_ROOT = Path(__file__).parent.parent.parent
BACKEND_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(COMPONENT_ROOT))
sys.path.insert(0, str(BACKEND_ROOT))

try:
    from models.schemas import SkillGapRequest
except ImportError:
    from backend.models.schemas import SkillGapRequest
from services.ml_engine import run_skill_gap_analysis
from src.gap_analysis.skill_gap import analyze_skill_gap
import time

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# In-memory high performance TTL cache for applied jobs analysis
_APPLIED_JOBS_CACHE: Dict[str, Any] = {}
_CACHE_TTL_SECS = 45.0

def get_cached_applied_jobs(candidate_id: str):
    entry = _APPLIED_JOBS_CACHE.get(candidate_id)
    if entry:
        ts, data = entry
        if time.time() - ts < _CACHE_TTL_SECS:
            return data
    return None

def set_cached_applied_jobs(candidate_id: str, data: dict):
    _APPLIED_JOBS_CACHE[candidate_id] = (time.time(), data)

def invalidate_applied_jobs_cache(candidate_id: Optional[str] = None):
    if candidate_id and candidate_id in _APPLIED_JOBS_CACHE:
        del _APPLIED_JOBS_CACHE[candidate_id]
    elif not candidate_id:
        _APPLIED_JOBS_CACHE.clear()


class SimpleSkillGapRequest(BaseModel):
    current_skills: Optional[List[str]] = None
    target_role: Optional[str] = None
    # Component 1 integration fields (Option 2)
    predicted_role: Optional[str] = None
    detected_skills: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    job_role: Optional[str] = None


class SimulateRequest(BaseModel):
    candidate_id: Optional[str] = None
    target_role: Optional[str] = None
    job_role: Optional[str] = None
    role: Optional[str] = None
    acquired_skills: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    simulated_skills: Optional[List[str]] = None
    current_skills: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    opening_required_skills: Optional[List[str]] = None


@router.post("", summary="Skill Gap Analysis (Simple JSON or Option 2 Component 1 Integration)")
@router.post("/", summary="Skill Gap Analysis (Simple JSON or Option 2 Component 1 Integration)")
async def simple_skill_gap(payload: SimpleSkillGapRequest):
    """
    Accepts Option 1 (current_skills + target_role) or Option 2 (Component 1 output).
    """
    current_skills = payload.current_skills or payload.detected_skills or payload.skills or []
    target_role = payload.target_role or payload.predicted_role or payload.job_role or "Data Scientist"

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
async def simulate_skill_acquisition(payload: SimulateRequest, request: Request = None):
    db = getattr(request.app.state, "db", None) if request else None

    candidate_id = payload.candidate_id
    target_role = payload.target_role or payload.job_role or payload.role or "Software Engineer"
    acquired_skills = payload.acquired_skills or payload.skills or payload.simulated_skills or []
    current_skills = payload.current_skills
    custom_required = payload.required_skills or payload.opening_required_skills

    # If current_skills not explicitly provided, load candidate's real CV skills from db
    if current_skills is None and candidate_id and db is not None:
        from bson import ObjectId
        resume = await db.resumes.find_one({"candidate_id": candidate_id}, sort=[("created_at", -1)])
        if not resume:
            try:
                resume = await db.resumes.find_one({"candidate_id": ObjectId(candidate_id)}, sort=[("created_at", -1)])
            except Exception:
                pass
        if resume:
            current_skills = resume.get("skills", [])
        else:
            current_skills = []
    elif current_skills is None:
        current_skills = []

    combined_skills = list(set(current_skills + acquired_skills))

    res_orig = analyze_skill_gap(current_skills=current_skills, target_role=target_role, custom_required=custom_required)
    res_sim = analyze_skill_gap(current_skills=combined_skills, target_role=target_role, custom_required=custom_required)

    orig_pct = res_orig["skill_coverage_percentage"]
    sim_pct = res_sim["skill_coverage_percentage"]
    diff = round(max(0.0, sim_pct - orig_pct), 2)

    remaining_missing = [m["skill"] for m in res_sim["missing_skills"]]
    resources = []
    try:
        from services.ml_engine import RESOURCES as _RESOURCES
    except Exception:
        _RESOURCES = {}
    for sk in remaining_missing:
        r = _RESOURCES.get(sk) or {
            "course": f"{sk} Fundamentals & Mastery",
            "url": f"https://www.coursera.org/search?query={sk.replace(' ', '+')}",
            "duration": "3-4 weeks",
            "level": "Intermediate"
        }
        resources.append({"skill": sk, **r})

    data_dict = {
        "target_role": target_role,
        "original_coverage": orig_pct,
        "simulated_coverage": sim_pct,
        "coverage_improvement": diff,
        "simulated_matched": res_sim["matched_skills"],
        "matched_skills": res_sim["matched_skills"],
        "remaining_missing": remaining_missing,
        "remaining_missing_skills": remaining_missing,
        "resources": resources,
        "learning_plan": [
            {"step": i + 1, "skill": sk, "action": f"Acquire {sk} to unlock higher job match"}
            for i, sk in enumerate(remaining_missing)
        ],
    }

    return {"success": True, **data_dict, "data": data_dict}


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
@limiter.limit("10/minute")
async def delete_report(candidate_id: str, request: Request):
    db  = request.app.state.db
    res = await db.skill_gap_reports.delete_many({"candidate_id": candidate_id})
    return {"success": True, "deleted": res.deleted_count}


@router.get("/roles", summary="List all supported job roles")
async def list_roles():
    from services.ml_engine import JOB_REQ
    return {"success": True, "roles": sorted(JOB_REQ.keys()), "count": len(JOB_REQ)}


@router.get("/applied-jobs/{candidate_id}", summary="Get multi-job skill gap & interview analysis for candidate applied jobs")
async def get_applied_jobs_skill_gap(candidate_id: str, request: Request):
    """
    Evaluates skill gap, strengths, and weaknesses for every job the candidate applied for,
    integrating Component 1 CV parsing/matching and Component 2 AI Interview question-level topic scores.
    """
    cached = get_cached_applied_jobs(candidate_id)
    if cached:
        return cached

    db = request.app.state.db
    from bson import ObjectId
    from services.ml_engine import RESOURCES, JOB_REQ, compute_gap

    # 1. Fetch candidate jobs from Applications, CV Match Predictions, and Interview Scores
    seen_job_ids = set()
    candidate_jobs = []

    # Fetch candidate resume IDs first
    cand_resume_ids = []
    cand_id_filters = [{"candidate_id": candidate_id}]
    if ObjectId.is_valid(candidate_id):
        cand_id_filters.append({"candidate_id": ObjectId(candidate_id)})

    async for r in db.resumes.find({"$or": cand_id_filters}):
        cand_resume_ids.append(str(r["_id"]))

    # A. From Applications
    cursor = db.applications.find({"$or": cand_id_filters}).sort("applied_at", -1)
    async for app in cursor:
        jid = str(app.get("job_id", ""))
        if jid and jid not in seen_job_ids:
            seen_job_ids.add(jid)
            candidate_jobs.append({
                "job_id": jid,
                "status": app.get("status", "applied"),
                "applied_at": app.get("applied_at")
            })

    # B. From CV Match Predictions
    pred_query = list(cand_id_filters)
    if cand_resume_ids:
        pred_query.append({"resume_id": {"$in": cand_resume_ids}})

    pred_cursor = db.predictions.find({"$or": pred_query}).sort("created_at", -1)
    async for pred_doc in pred_cursor:
        jid = str(pred_doc.get("job_id", ""))
        if jid:
            job_found = None
            try:
                if ObjectId.is_valid(jid):
                    job_found = await db.jobs.find_one({"_id": ObjectId(jid)})
                if not job_found:
                    job_found = await db.jobs.find_one({"_id": jid})
            except Exception:
                pass
            if job_found:
                actual_jid = str(job_found["_id"])
                if actual_jid not in seen_job_ids:
                    seen_job_ids.add(actual_jid)
                    candidate_jobs.append({
                        "job_id": actual_jid,
                        "status": "cv_matched",
                        "applied_at": pred_doc.get("created_at")
                    })

    # C. From Interview Scores (C0 db.interview_scores)
    score_cursor = db.interview_scores.find({"$or": cand_id_filters}).sort("created_at", -1)
    async for sc_doc in score_cursor:
        jid = str(sc_doc.get("job_id", ""))
        if jid:
            job_found = None
            try:
                if ObjectId.is_valid(jid):
                    job_found = await db.jobs.find_one({"_id": ObjectId(jid)})
                if not job_found:
                    job_found = await db.jobs.find_one({"_id": jid})
            except Exception:
                pass
            if job_found:
                actual_jid = str(job_found["_id"])
                if actual_jid not in seen_job_ids:
                    seen_job_ids.add(actual_jid)
                    candidate_jobs.append({
                        "job_id": actual_jid,
                        "status": "interviewed",
                        "applied_at": sc_doc.get("created_at")
                    })

    # D. From Interview Results (C2 db.results)
    results_cursor = db.results.find({"$or": cand_id_filters}).sort("created_at", -1)
    async for res_doc in results_cursor:
        jid = str(res_doc.get("job_id", ""))
        if jid:
            job_found = None
            try:
                if ObjectId.is_valid(jid):
                    job_found = await db.jobs.find_one({"_id": ObjectId(jid)})
                if not job_found:
                    job_found = await db.jobs.find_one({"_id": jid})
            except Exception:
                pass
            if job_found:
                actual_jid = str(job_found["_id"])
                if actual_jid not in seen_job_ids:
                    seen_job_ids.add(actual_jid)
                    candidate_jobs.append({
                        "job_id": actual_jid,
                        "status": "interviewed",
                        "applied_at": res_doc.get("created_at")
                    })

    # 2. Fetch candidate resume strictly for this candidate
    resume = None
    try:
        if ObjectId.is_valid(candidate_id):
            resume = await db.resumes.find_one({"$or": [{"candidate_id": candidate_id}, {"candidate_id": ObjectId(candidate_id)}]}, sort=[("created_at", -1)])
        else:
            resume = await db.resumes.find_one({"candidate_id": candidate_id}, sort=[("created_at", -1)])
    except Exception:
        pass

    # If new candidate has no applications, predictions, or interviews, return clean empty reports
    if not candidate_jobs and not resume:
        return {"success": True, "candidate_id": candidate_id, "total_applied_jobs": 0, "reports": []}

    cand_skills = resume.get("skills", []) if resume else []
    cand_name = resume.get("candidate_name", "") if resume else ""
    cand_exp = resume.get("experience_years", 0) if resume else 0
    cand_edu = resume.get("education", "B.Sc. Computer Science") if resume else "B.Sc. Computer Science"

    if not cand_name:
        try:
            user_doc = await db.users.find_one({"_id": ObjectId(candidate_id)}) if ObjectId.is_valid(candidate_id) else await db.users.find_one({"_id": candidate_id})
            if user_doc:
                cand_name = user_doc.get("full_name", user_doc.get("email", "Candidate"))
        except Exception:
            pass

    reports = []

    # If no specific jobs found, create a baseline report from resume so candidate gets instant insights
    if not candidate_jobs and cand_skills:
        # Fallback to general skill gap for candidate's top predicted role
        pred = await db.predictions.find_one({"candidate_id": candidate_id}, sort=[("created_at", -1)])
        target_role = pred.get("predicted_role", "Software Engineer") if pred else "Software Engineer"
        
        # Check if interview exists
        interview_res = await db.results.find_one({"candidate_id": candidate_id, "job_role": target_role}, sort=[("created_at", -1)])
        interview_score = interview_res.get("interview_score") if interview_res else None
        
        analysis = await run_in_threadpool(
            run_skill_gap_analysis,
            candidate_id=candidate_id,
            candidate_name=cand_name or "Candidate",
            job_role=target_role,
            skills=cand_skills,
            experience_years=int(cand_exp),
            education=cand_edu,
            cv_matching_score=pred.get("overall_score") if pred else None,
            interview_score=interview_score,
            mcq_score=interview_res.get("mcq_score") if interview_res else None,
            descriptive_score=interview_res.get("descriptive_score") if interview_res else None,
            coding_score=interview_res.get("coding_score") if interview_res else None,
            weak_topics=interview_res.get("weak_topics", []) if interview_res else [],
            failed_mcq_topics=interview_res.get("failed_mcq_topics", []) if interview_res else [],
        )
        reports.append({
            "job_id": "general_baseline",
            "job_title": target_role,
            "company_name": "General Career Evaluation",
            "location": "Remote",
            "employment_type": "Full-time",
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "interview_completed": interview_res is not None,
            "interview_score": interview_score,
            "cv_score": pred.get("overall_score", 75) if pred else 75,
            "cv_breakdown": {
                "skill_score": pred.get("skill_score", 75) if pred else 75,
                "experience_score": pred.get("experience_score", 70) if pred else 70,
                "education_score": pred.get("education_score", 80) if pred else 80,
                "overall_score": pred.get("overall_score", 75) if pred else 75,
            },
            "composite_score": analysis.get("hire_probability", 0.7) * 100,
            "total_mark": analysis.get("hire_probability", 0.7) * 100,
            "strengths": [{"skill": s, "source": "CV Skill Profile", "details": f"Verified proficiency in {s}"} for s in analysis.get("matched_skills", [])[:5]],
            "weaknesses": [{"skill": s, "source": "Target Role Gap", "details": f"Missing critical skill for {target_role}", "severity": "High"} for s in analysis.get("missing_required", [])[:4]],
            "topic_performance": [],
            "interview_breakdown": None,
            "course_recommendations": analysis.get("learning_resources", []),
            "career_suggestions": analysis.get("career_suggestions", []),
            "is_baseline": True
        })

    async def process_app(app):
        job_id = str(app.get("job_id", ""))
        job = None
        try:
            job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        except Exception:
            pass
        if not job:
            job = await db.jobs.find_one({"_id": job_id})
        
        if not job:
            return None

        job_title = job.get("title", "Software Engineer")
        job_skills = job.get("required_skills", [])
        
        # Resolve company name
        company_name = job.get("company_name", "")
        if not company_name and job.get("company_id"):
            try:
                comp_user = await db.users.find_one({"_id": ObjectId(job["company_id"])})
                if comp_user:
                    company_name = comp_user.get("company_name", comp_user.get("full_name", "Tech Company"))
            except Exception:
                pass
        if not company_name:
            company_name = "Tech Employer"

        # Parallel database lookups for this application
        pred_or_conditions = [
            {"candidate_id": candidate_id, "job_id": job_id},
            {"candidate_id": candidate_id, "job_id": str(job.get("_id", ""))},
            {"candidate_id": candidate_id, "predicted_role": job_title},
        ]
        if ObjectId.is_valid(candidate_id):
            pred_or_conditions.append({"candidate_id": ObjectId(candidate_id), "job_id": job_id})
            pred_or_conditions.append({"candidate_id": ObjectId(candidate_id), "job_id": str(job.get("_id", ""))})
            pred_or_conditions.append({"candidate_id": ObjectId(candidate_id), "predicted_role": job_title})
        if cand_resume_ids:
            pred_or_conditions.append({"resume_id": {"$in": cand_resume_ids}, "job_id": job_id})
            pred_or_conditions.append({"resume_id": {"$in": cand_resume_ids}, "job_id": str(job.get("_id", ""))})
            pred_or_conditions.append({"resume_id": {"$in": cand_resume_ids}, "predicted_role": job_title})

        pred_task = db.predictions.find_one({"$or": pred_or_conditions}, sort=[("created_at", -1)])

        int_or_conditions = [
            {"candidate_id": candidate_id, "job_role": job_title},
            {"candidate_id": candidate_id, "job_role": job.get("title", "")},
            {"candidate_id": candidate_id, "job_id": job_id},
            {"candidate_id": candidate_id, "job_id": str(job.get("_id", ""))}
        ]
        if ObjectId.is_valid(candidate_id):
            int_or_conditions.append({"candidate_id": ObjectId(candidate_id), "job_role": job_title})
            int_or_conditions.append({"candidate_id": ObjectId(candidate_id), "job_id": job_id})

        interview_res_task = db.results.find_one({"$or": int_or_conditions}, sort=[("created_at", -1)])
        session_task = db.sessions.find_one({"$or": int_or_conditions}, sort=[("created_at", -1)])
        score_doc_task = db.interview_scores.find_one({"$or": int_or_conditions}, sort=[("created_at", -1)])

        pred, interview_res, session, score_doc = await asyncio.gather(
            pred_task, interview_res_task, session_task, score_doc_task
        )

        skill_score = pred.get("skill_score") if pred else None
        experience_score = pred.get("experience_score") if pred else None
        education_score = pred.get("education_score") if pred else None
        cv_matching_score = pred.get("overall_score") if pred else None

        if skill_score is None and cand_skills and job_skills:
            matched_cv_count = len([s for s in job_skills if any(s.lower() in cs.lower() or cs.lower() in s.lower() for cs in cand_skills)])
            skill_score = round((matched_cv_count / max(len(job_skills), 1)) * 100, 1)
        elif skill_score is None:
            skill_score = 75.0

        if experience_score is None:
            req_exp = float(job.get("experience_required", 2) or 2)
            experience_score = round(min((float(cand_exp or 2) / max(req_exp, 1)) * 100, 100), 1)

        if education_score is None:
            education_score = 80.0

        if cv_matching_score is None:
            cv_matching_score = round(0.50 * skill_score + 0.30 * experience_score + 0.20 * education_score, 1)

        interview_completed = interview_res is not None or (session and session.get("status") == "completed") or score_doc is not None
        interview_score = None
        mcq_score = None
        descriptive_score = None
        coding_score = None
        grade = "N/A"
        weak_topics = []
        failed_mcq_topics = []
        topic_scores = {}

        if interview_res:
            interview_score = interview_res.get("interview_score", 0)
            mcq_score = interview_res.get("mcq_score", 0)
            descriptive_score = interview_res.get("descriptive_score", 0)
            coding_score = interview_res.get("coding_score", 0)
            grade = interview_res.get("grade", "Average")
            weak_topics = interview_res.get("weak_topics", [])
            failed_mcq_topics = interview_res.get("failed_mcq_topics", [])

            for mcq in interview_res.get("mcq_details", []):
                t = mcq.get("topic") or mcq.get("category") or "General"
                is_corr = mcq.get("is_correct", False)
                topic_scores.setdefault(t, []).append(100 if is_corr else 0)

            for desc in interview_res.get("descriptive_details", []):
                t = desc.get("topic") or desc.get("category") or "General"
                s = desc.get("score") or desc.get("similarity_score") or 50
                topic_scores.setdefault(t, []).append(float(s))

            for code in interview_res.get("coding_details", []):
                t = code.get("topic") or "Coding & Algorithms"
                s = code.get("score") or 0
                topic_scores.setdefault(t, []).append(float(s))

        elif score_doc:
            interview_score = score_doc.get("interview_score", 0)
            mcq_score = score_doc.get("mcq_score", 0)
            descriptive_score = score_doc.get("descriptive_score", 0)
            coding_score = score_doc.get("coding_score", 0)
            grade = score_doc.get("grade", "Average")

        topic_performance = []
        interview_strengths = []
        interview_weaknesses = []

        for topic, scores in topic_scores.items():
            if not scores:
                continue
            avg_score = round(sum(scores) / len(scores), 1)
            is_strong = avg_score >= 70
            is_weak = avg_score < 50
            topic_performance.append({
                "topic": topic,
                "score": avg_score,
                "status": "Strong" if is_strong else ("Needs Improvement" if is_weak else "Moderate"),
                "total_questions": len(scores)
            })
            if is_strong:
                interview_strengths.append({
                    "skill": topic,
                    "source": "AI Interview Performance",
                    "details": f"Scored {avg_score}% in technical interview evaluation"
                })
            elif is_weak:
                interview_weaknesses.append({
                    "skill": topic,
                    "source": "AI Interview Weakness",
                    "details": f"Identified as knowledge gap during technical interview",
                    "severity": "High"
                })

        for wt in weak_topics:
            if not any(w["skill"].lower() == wt.lower() for w in interview_weaknesses):
                interview_weaknesses.append({
                    "skill": wt,
                    "source": "AI Interview Weakness",
                    "details": f"Identified as knowledge gap during technical interview",
                    "severity": "High"
                })

        analysis = await run_in_threadpool(
            run_skill_gap_analysis,
            candidate_id=candidate_id,
            candidate_name=cand_name or "Candidate",
            job_role=job_title,
            skills=cand_skills,
            experience_years=int(cand_exp),
            education=cand_edu,
            cv_matching_score=cv_matching_score,
            interview_score=interview_score,
            mcq_score=mcq_score,
            descriptive_score=descriptive_score,
            coding_score=coding_score,
            weak_topics=[w["skill"] for w in interview_weaknesses],
            failed_mcq_topics=failed_mcq_topics,
        )

        cv_strengths = []
        cv_weaknesses = []
        # The run_skill_gap_analysis returns "present_skills" (candidate's skills),
        # not "matched_skills". Use "missing_required" and "missing_optional" instead.
        present_skills = analysis.get("present_skills", [])
        missing_required = analysis.get("missing_required", [])
        missing_optional = analysis.get("missing_optional", [])

        # Compute matched skills: candidate skills that are NOT in missing lists
        missing_set = {s.lower() for s in missing_required + missing_optional}
        matched_cv_skills = [s for s in present_skills if s.lower() not in missing_set]

        for ms in matched_cv_skills:
            if not any(s["skill"].lower() == ms.lower() for s in interview_strengths):
                cv_strengths.append({
                    "skill": ms,
                    "source": "CV Skill Match",
                    "details": f"Required skill verified on candidate resume"
                })

        for mr in missing_required:
            if not any(w["skill"].lower() == mr.lower() for w in interview_weaknesses):
                cv_weaknesses.append({
                    "skill": mr,
                    "source": "CV Requirement Gap",
                    "details": f"Required by {company_name} job post, missing from CV profile",
                    "severity": "Critical"
                })

        for mo in missing_optional:
            if not any(w["skill"].lower() == mo.lower() for w in interview_weaknesses) and not any(w["skill"].lower() == mo.lower() for w in cv_weaknesses):
                cv_weaknesses.append({
                    "skill": mo,
                    "source": "Preferred Skill Gap",
                    "details": f"Preferred bonus skill not listed on CV",
                    "severity": "Low"
                })

        all_strengths = interview_strengths + cv_strengths
        all_weaknesses = interview_weaknesses + cv_weaknesses

        if interview_score is not None and cv_matching_score is not None:
            composite_fit = round(0.55 * interview_score + 0.45 * cv_matching_score, 1)
        elif interview_score is not None:
            composite_fit = round(interview_score, 1)
        elif cv_matching_score is not None:
            composite_fit = round(cv_matching_score, 1)
        else:
            composite_fit = round((analysis.get("skill_match_pct", 50)), 1)

        targeted_resources = []
        seen_res = set()
        for w in all_weaknesses:
            sk = w["skill"].strip()
            if sk.lower() in seen_res:
                continue
            seen_res.add(sk.lower())
            res = RESOURCES.get(sk)
            if not res:
                for rk, rv in RESOURCES.items():
                    if rk.lower() in sk.lower() or sk.lower() in rk.lower():
                        res = rv
                        break
            if not res:
                res = {
                    "course": f"{sk} Mastery & Interview Practice",
                    "url": "https://www.coursera.org/search?query=" + sk.replace(" ", "+"),
                    "duration": "4 weeks",
                    "level": "Intermediate",
                }
            targeted_resources.append({
                "skill": sk,
                "priority": w.get("severity", "High"),
                "source": w.get("source", "Skill Gap"),
                "course": res["course"],
                "url": res["url"],
                "duration": res["duration"],
                "level": res["level"],
                "improvement_tip": f"Practice {sk} core fundamentals and live coding problems to boost future interview scores."
            })

        return {
            "job_id": job_id,
            "job_title": job_title,
            "department": job.get("department", ""),
            "company_name": company_name,
            "location": job.get("location", "Remote"),
            "employment_type": job.get("employment_type", "Full-time"),
            "salary_range": job.get("salary_range", ""),
            "applied_at": str(app.get("applied_at", datetime.now(timezone.utc).isoformat())),
            "application_status": app.get("status", "applied"),
            "interview_completed": interview_completed,
            "interview_score": interview_score,
            "cv_score": cv_matching_score,
            "cv_breakdown": {
                "skill_score": skill_score,
                "experience_score": experience_score,
                "education_score": education_score,
                "overall_score": cv_matching_score,
            },
            "composite_score": composite_fit,
            "total_mark": composite_fit,
            "interview_breakdown": {
                "mcq_score": mcq_score,
                "descriptive_score": descriptive_score,
                "coding_score": coding_score,
                "interview_score": interview_score,
                "grade": grade,
            } if interview_completed else None,
            "topic_performance": topic_performance,
            "strengths": all_strengths,
            "weaknesses": all_weaknesses,
            "missing_required_skills": missing_required,
            "course_recommendations": targeted_resources,
            "career_suggestions": analysis.get("career_suggestions", []),
            "hire_probability": analysis.get("hire_probability", 0.5),
            "gap_severity": analysis.get("gap_severity", "Medium"),
        }

    if candidate_jobs:
        results = await asyncio.gather(*[process_app(app) for app in candidate_jobs])
        reports.extend([r for r in results if r is not None])

    resp_data = {"success": True, "candidate_id": candidate_id, "total_applied_jobs": len(reports), "reports": reports, "data": reports}
    set_cached_applied_jobs(candidate_id, resp_data)
    return resp_data
