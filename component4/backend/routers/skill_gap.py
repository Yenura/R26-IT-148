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
import pickle
import numpy as np

# Load LambdaMART model from Component 3 if available
_LAMBDAMART_MODEL = None
_C3_MODEL_PATH = os.path.normpath(os.path.join(str(COMPONENT_ROOT), "..", "component3", "models", "lambdamart_model.pkl"))
if os.path.exists(_C3_MODEL_PATH):
    try:
        with open(_C3_MODEL_PATH, "rb") as f:
            _LAMBDAMART_MODEL = pickle.load(f)
    except Exception:
        pass

# Role CV and Interview weights from Component 3 CSS Engine
ROLE_CV_WEIGHTS = {
    "Software_Engineer":         {"w_edu": 0.20, "w_exp": 0.30, "w_skill": 0.50},
    "Data_Scientist":            {"w_edu": 0.30, "w_exp": 0.30, "w_skill": 0.40},
    "Machine_Learning_Engineer": {"w_edu": 0.25, "w_exp": 0.30, "w_skill": 0.45},
    "DevOps_Engineer":           {"w_edu": 0.15, "w_exp": 0.40, "w_skill": 0.45},
    "Cybersecurity_Analyst":     {"w_edu": 0.20, "w_exp": 0.35, "w_skill": 0.45},
    "Cloud_Solutions_Architect": {"w_edu": 0.20, "w_exp": 0.40, "w_skill": 0.40},
    "Database_Administrator":    {"w_edu": 0.20, "w_exp": 0.40, "w_skill": 0.40},
    "Frontend_Developer":        {"w_edu": 0.15, "w_exp": 0.30, "w_skill": 0.55},
    "Backend_Developer":         {"w_edu": 0.20, "w_exp": 0.30, "w_skill": 0.50},
    "Mobile_App_Developer":      {"w_edu": 0.15, "w_exp": 0.30, "w_skill": 0.55},
    "Full_Stack_Developer":      {"w_edu": 0.15, "w_exp": 0.30, "w_skill": 0.55},
    "QA_Test_Automation_Engineer": {"w_edu": 0.15, "w_exp": 0.35, "w_skill": 0.50},
    "Data_Engineer":             {"w_edu": 0.20, "w_exp": 0.35, "w_skill": 0.45},
    "Site_Reliability_Engineer": {"w_edu": 0.15, "w_exp": 0.40, "w_skill": 0.45},
    "UI_UX_Designer":            {"w_edu": 0.20, "w_exp": 0.25, "w_skill": 0.55},
    "Network_Engineer":          {"w_edu": 0.20, "w_exp": 0.35, "w_skill": 0.45},
    "Business_Systems_Analyst":  {"w_edu": 0.25, "w_exp": 0.35, "w_skill": 0.40},
    "AI_NLP_Engineer":           {"w_edu": 0.25, "w_exp": 0.30, "w_skill": 0.45},
    "Blockchain_Developer":      {"w_edu": 0.15, "w_exp": 0.30, "w_skill": 0.55},
    "Embedded_Systems_Engineer": {"w_edu": 0.20, "w_exp": 0.35, "w_skill": 0.45},
}

ROLE_INTERVIEW_WEIGHTS = {
    "Software_Engineer":         {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "Data_Scientist":            {"w_mcq": 0.30, "w_desc": 0.50, "w_code": 0.20},
    "Machine_Learning_Engineer": {"w_mcq": 0.25, "w_desc": 0.35, "w_code": 0.40},
    "DevOps_Engineer":           {"w_mcq": 0.25, "w_desc": 0.30, "w_code": 0.45},
    "Cybersecurity_Analyst":     {"w_mcq": 0.35, "w_desc": 0.45, "w_code": 0.20},
    "Cloud_Solutions_Architect": {"w_mcq": 0.30, "w_desc": 0.50, "w_code": 0.20},
    "Database_Administrator":    {"w_mcq": 0.30, "w_desc": 0.35, "w_code": 0.35},
    "Frontend_Developer":        {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "Backend_Developer":         {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "Mobile_App_Developer":      {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "Full_Stack_Developer":      {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "QA_Test_Automation_Engineer": {"w_mcq": 0.25, "w_desc": 0.35, "w_code": 0.40},
    "Data_Engineer":             {"w_mcq": 0.25, "w_desc": 0.35, "w_code": 0.40},
    "Site_Reliability_Engineer": {"w_mcq": 0.25, "w_desc": 0.30, "w_code": 0.45},
    "UI_UX_Designer":            {"w_mcq": 0.30, "w_desc": 0.50, "w_code": 0.20},
    "Network_Engineer":          {"w_mcq": 0.30, "w_desc": 0.40, "w_code": 0.30},
    "Business_Systems_Analyst":  {"w_mcq": 0.35, "w_desc": 0.50, "w_code": 0.15},
    "AI_NLP_Engineer":           {"w_mcq": 0.25, "w_desc": 0.35, "w_code": 0.40},
    "Blockchain_Developer":      {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "Embedded_Systems_Engineer": {"w_mcq": 0.25, "w_desc": 0.30, "w_code": 0.45},
}

def _resolve_role_weights(job_title: str):
    clean = job_title.strip().replace(" ", "_")
    for k in ROLE_CV_WEIGHTS:
        if k.lower() == clean.lower() or k.replace("_", "").lower() == clean.replace("_", "").lower():
            return ROLE_CV_WEIGHTS[k], ROLE_INTERVIEW_WEIGHTS[k]
    for k in ROLE_CV_WEIGHTS:
        if k.lower() in clean.lower() or clean.lower() in k.lower():
            return ROLE_CV_WEIGHTS[k], ROLE_INTERVIEW_WEIGHTS[k]
    return {"w_edu": 0.20, "w_exp": 0.30, "w_skill": 0.50}, {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50}

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
    if not candidate_id or candidate_id in ("web-user", "candidate-user", "undefined", "null", "none"):
        return {"success": True, "candidate_id": candidate_id or "", "total_applied_jobs": 0, "reports": [], "data": []}

    cached = get_cached_applied_jobs(candidate_id)
    if cached:
        return cached

    db = request.app.state.db
    from bson import ObjectId
    from services.ml_engine import RESOURCES, JOB_REQ, compute_gap, _resolve_role_weights, _LAMBDAMART_MODEL

    cand_id_filters = [{"candidate_id": candidate_id}]
    if ObjectId.is_valid(candidate_id):
        cand_id_filters.append({"candidate_id": ObjectId(candidate_id)})
        cand_id_filters.append({"_id": ObjectId(candidate_id)})

    # Parallel batch fetch of candidate's core collections
    resumes_task = db.resumes.find({"$or": [{"candidate_id": candidate_id}] + ([{"candidate_id": ObjectId(candidate_id)}] if ObjectId.is_valid(candidate_id) else [])}).sort("created_at", -1).to_list(10)
    apps_task = db.applications.find({"$or": cand_id_filters}).sort("applied_at", -1).to_list(100)
    preds_task = db.predictions.find({"$or": cand_id_filters}).sort("created_at", -1).to_list(100)
    scores_task = db.interview_scores.find({"$or": cand_id_filters}).sort("created_at", -1).to_list(100)
    results_task = db.results.find({"$or": cand_id_filters}).sort("created_at", -1).to_list(100)
    sessions_task = db.sessions.find({"$or": cand_id_filters}).sort("created_at", -1).to_list(100)

    resumes_list, apps_list, preds_list, scores_list, results_list, sessions_list = await asyncio.gather(
        resumes_task, apps_task, preds_task, scores_task, results_task, sessions_task
    )

    resume = resumes_list[0] if resumes_list else None

    # Collect all job IDs from applications, predictions, scores, results
    raw_job_ids = set()
    for app in apps_list:
        jid = str(app.get("job_id", "")).strip()
        if jid:
            raw_job_ids.add(jid)
    for p in preds_list:
        jid = str(p.get("job_id", "")).strip()
        if jid:
            raw_job_ids.add(jid)
    for s in scores_list:
        jid = str(s.get("job_id", "")).strip()
        if jid:
            raw_job_ids.add(jid)
    for res in results_list:
        jid = str(res.get("job_id", "")).strip()
        if jid:
            raw_job_ids.add(jid)

    # Batch fetch all matching jobs in a single query
    job_docs_map = {}
    if raw_job_ids:
        job_query_oids = [ObjectId(jid) for jid in raw_job_ids if ObjectId.is_valid(jid)]
        job_query_filters = [{"_id": {"$in": list(raw_job_ids)}}]
        if job_query_oids:
            job_query_filters.append({"_id": {"$in": job_query_oids}})
        job_docs = await db.jobs.find({"$or": job_query_filters}).to_list(200)
        for jdoc in job_docs:
            job_docs_map[str(jdoc["_id"])] = jdoc

    # Batch fetch company names for all jobs
    company_ids = list({jdoc.get("company_id") for jdoc in job_docs_map.values() if jdoc.get("company_id")})
    company_names_map = {}
    if company_ids:
        comp_oids = [ObjectId(c) for c in company_ids if ObjectId.is_valid(c)]
        comp_filters = [{"_id": {"$in": company_ids}}]
        if comp_oids:
            comp_filters.append({"_id": {"$in": comp_oids}})
        comp_users = await db.users.find({"$or": comp_filters}).to_list(100)
        for u in comp_users:
            company_names_map[str(u["_id"])] = u.get("company_name", u.get("full_name", "Tech Employer"))

    # Build unique candidate_jobs list
    seen_job_ids = set()
    candidate_jobs = []

    for app in apps_list:
        jid = str(app.get("job_id", "")).strip()
        if jid and jid in job_docs_map and jid not in seen_job_ids:
            seen_job_ids.add(jid)
            candidate_jobs.append({
                "job_id": jid,
                "status": app.get("status", "applied"),
                "applied_at": app.get("applied_at")
            })

    for p in preds_list:
        jid = str(p.get("job_id", "")).strip()
        if jid and jid in job_docs_map and jid not in seen_job_ids:
            seen_job_ids.add(jid)
            candidate_jobs.append({
                "job_id": jid,
                "status": "cv_matched",
                "applied_at": p.get("created_at")
            })

    for s in scores_list:
        jid = str(s.get("job_id", "")).strip()
        if jid and jid in job_docs_map and jid not in seen_job_ids:
            seen_job_ids.add(jid)
            candidate_jobs.append({
                "job_id": jid,
                "status": "interviewed",
                "applied_at": s.get("created_at")
            })

    for res in results_list:
        jid = str(res.get("job_id", "")).strip()
        if jid and jid in job_docs_map and jid not in seen_job_ids:
            seen_job_ids.add(jid)
            candidate_jobs.append({
                "job_id": jid,
                "status": "interviewed",
                "applied_at": res.get("created_at")
            })

    # If new candidate has no applications, predictions, or interviews, return clean empty reports
    if not candidate_jobs and not resume:
        return {"success": True, "candidate_id": candidate_id, "total_applied_jobs": 0, "reports": []}

    cand_skills = resume.get("skills", []) if resume else []
    cand_name = resume.get("candidate_name", "") if resume else ""
    cand_exp = resume.get("experience_years", 0) if resume else 0
    cand_edu = resume.get("education", "B.Sc. Computer Science") if resume else "B.Sc. Computer Science"

    reports = []

    # If no specific jobs found, create a baseline report from resume so candidate gets instant insights
    if not candidate_jobs and cand_skills:
        pred = preds_list[0] if preds_list else None
        target_role = pred.get("predicted_role", "Software Engineer") if pred else "Software Engineer"
        interview_res = results_list[0] if results_list else None
        interview_score = interview_res.get("interview_score") if interview_res else None
        
        analysis = run_skill_gap_analysis(
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

    def process_app_sync(app):
        job_id = str(app.get("job_id", ""))
        job = job_docs_map.get(job_id)
        if not job:
            return None

        job_title = job.get("title", "Software Engineer")
        job_skills = job.get("required_skills", [])
        company_name = job.get("company_name") or company_names_map.get(str(job.get("company_id", "")), "Tech Employer")

        # In-memory lookup for predictions
        pred = next((p for p in preds_list if str(p.get("job_id")) == job_id or str(p.get("job_id")) == str(job.get("_id", "")) or p.get("predicted_role") == job_title), None)
        # In-memory lookup for interview results & scores
        interview_res = next((r for r in results_list if str(r.get("job_id")) == job_id or r.get("job_role") == job_title), None)
        session = next((s for s in sessions_list if str(s.get("job_id")) == job_id or s.get("job_role") == job_title), None)
        score_doc = next((s for s in scores_list if str(s.get("job_id")) == job_id or s.get("job_role") == job_title), None)

        # Resolve role weights for CSS engine
        cv_w, int_w = _resolve_role_weights(job_title)

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
            cv_matching_score = round(cv_w["w_skill"] * skill_score + cv_w["w_exp"] * experience_score + cv_w["w_edu"] * education_score, 1)
        else:
            cv_matching_score = round(float(cv_matching_score), 1)

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
            mcq_score = float(interview_res.get("mcq_score", 0))
            descriptive_score = float(interview_res.get("descriptive_score", 0))
            coding_score = float(interview_res.get("coding_score", 0))
            interview_score = round(int_w["w_mcq"] * mcq_score + int_w["w_desc"] * descriptive_score + int_w["w_code"] * coding_score, 1)
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
            mcq_score = float(score_doc.get("mcq_score", 0))
            descriptive_score = float(score_doc.get("descriptive_score", 0))
            coding_score = float(score_doc.get("coding_score", 0))
            interview_score = round(int_w["w_mcq"] * mcq_score + int_w["w_desc"] * descriptive_score + int_w["w_code"] * coding_score, 1)
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

        analysis = run_skill_gap_analysis(
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

        # Master CSS calculation (40% CV + 60% Interview) and LambdaMART score
        ltr_score = None
        if interview_completed and interview_score is not None:
            composite_fit = round(0.40 * cv_matching_score + 0.60 * interview_score, 1)
            if _LAMBDAMART_MODEL is not None:
                try:
                    X_cand = np.array([[education_score / 100.0, experience_score / 100.0, skill_score / 100.0,
                                       (mcq_score or 0.0) / 100.0, (descriptive_score or 0.0) / 100.0, (coding_score or 0.0) / 100.0]])
                    ltr_score = round(float(_LAMBDAMART_MODEL.predict(X_cand)[0]), 4)
                except Exception:
                    pass
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
            "ltr_score": ltr_score,
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

    for app in candidate_jobs:
        rep = process_app_sync(app)
        if rep is not None:
            reports.append(rep)

    resp_data = {"success": True, "candidate_id": candidate_id, "total_applied_jobs": len(reports), "reports": reports, "data": reports}
    set_cached_applied_jobs(candidate_id, resp_data)
    return resp_data
