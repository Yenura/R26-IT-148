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
BACKEND_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(COMPONENT_ROOT))
sys.path.insert(0, str(BACKEND_ROOT))

try:
    from models.schemas import SkillGapRequest
except ImportError:
    from backend.models.schemas import SkillGapRequest
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


@router.get("/applied-jobs/{candidate_id}", summary="Get multi-job skill gap & interview analysis for candidate applied jobs")
async def get_applied_jobs_skill_gap(candidate_id: str, request: Request):
    """
    Evaluates skill gap, strengths, and weaknesses for every job the candidate applied for,
    integrating Component 1 CV parsing/matching and Component 2 AI Interview question-level topic scores.
    """
    db = request.app.state.db
    from bson import ObjectId
    from services.ml_engine import RESOURCES, JOB_REQ, compute_gap

    # 1. Fetch candidate applications
    applications = []
    cursor = db.applications.find({"candidate_id": candidate_id}).sort("applied_at", -1)
    async for app in cursor:
        applications.append(app)
    if not applications:
        try:
            cursor = db.applications.find({"candidate_id": ObjectId(candidate_id)}).sort("applied_at", -1)
            async for app in cursor:
                applications.append(app)
        except Exception:
            pass

    # 2. Fetch candidate resume
    resume = await db.resumes.find_one({"candidate_id": candidate_id}, sort=[("created_at", -1)])
    if not resume:
        try:
            resume = await db.resumes.find_one({"candidate_id": ObjectId(candidate_id)}, sort=[("created_at", -1)])
        except Exception:
            pass

    cand_skills = resume.get("skills", []) if resume else []
    cand_name = resume.get("candidate_name", "") if resume else ""
    cand_exp = resume.get("experience_years", 0) if resume else 0
    cand_edu = resume.get("education", "B.Sc. Computer Science") if resume else "B.Sc. Computer Science"

    if not cand_name:
        user_doc = await db.users.find_one({"_id": ObjectId(candidate_id)}) if ObjectId.is_valid(candidate_id) else await db.users.find_one({"_id": candidate_id})
        if user_doc:
            cand_name = user_doc.get("full_name", user_doc.get("email", "Candidate"))

    reports = []

    # If no applications found, create a baseline report from resume so candidate gets instant insights
    if not applications and cand_skills:
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
            "composite_score": analysis.get("hire_probability", 0.7) * 100,
            "strengths": [{"skill": s, "source": "CV Skill Profile", "details": f"Verified proficiency in {s}"} for s in analysis.get("matched_skills", [])[:5]],
            "weaknesses": [{"skill": s, "source": "Target Role Gap", "details": f"Missing critical skill for {target_role}", "severity": "High"} for s in analysis.get("missing_required", [])[:4]],
            "topic_performance": [],
            "interview_breakdown": None,
            "course_recommendations": analysis.get("learning_resources", []),
            "career_suggestions": analysis.get("career_suggestions", []),
            "is_baseline": True
        })

    for app in applications:
        job_id = str(app.get("job_id", ""))
        job = None
        try:
            job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        except Exception:
            pass
        if not job:
            job = await db.jobs.find_one({"_id": job_id})
        
        if not job:
            continue

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

        # Fetch CV Match / Prediction from C1/C0
        pred = await db.predictions.find_one({
            "candidate_id": candidate_id,
            "$or": [{"job_id": job_id}, {"job_id": str(job.get("_id", ""))}, {"predicted_role": job_title}]
        }, sort=[("created_at", -1)])

        cv_matching_score = pred.get("overall_score") if pred else None
        if cv_matching_score is None and cand_skills and job_skills:
            # Calculate CV match score directly if prediction not stored
            matched_cv_count = len([s for s in job_skills if any(s.lower() in cs.lower() or cs.lower() in s.lower() for cs in cand_skills)])
            cv_matching_score = round((matched_cv_count / max(len(job_skills), 1)) * 100, 1)

        # Fetch Component 2 Interview Results & Sessions
        interview_res = await db.results.find_one({
            "candidate_id": candidate_id,
            "$or": [{"job_role": job_title}, {"job_role": job.get("title", "")}]
        }, sort=[("created_at", -1)])

        session = await db.sessions.find_one({
            "candidate_id": candidate_id,
            "$or": [{"job_role": job_title}, {"job_role": job.get("title", "")}]
        }, sort=[("created_at", -1)])

        # Also check interview_scores table
        score_doc = await db.interview_scores.find_one({
            "candidate_id": candidate_id,
            "$or": [{"job_id": job_id}, {"job_role": job_title}]
        }, sort=[("created_at", -1)])

        interview_completed = interview_res is not None or (session and session.get("status") == "completed") or score_doc is not None
        interview_score = None
        mcq_score = None
        descriptive_score = None
        coding_score = None
        grade = "N/A"
        weak_topics = []
        failed_mcq_topics = []
        topic_scores = {}  # topic -> list of percentage scores

        if interview_res:
            interview_score = interview_res.get("interview_score", 0)
            mcq_score = interview_res.get("mcq_score", 0)
            descriptive_score = interview_res.get("descriptive_score", 0)
            coding_score = interview_res.get("coding_score", 0)
            grade = interview_res.get("grade", "Average")
            weak_topics = interview_res.get("weak_topics", [])
            failed_mcq_topics = interview_res.get("failed_mcq_topics", [])

            # Extract MCQ topic performance
            for mcq in interview_res.get("mcq_details", []):
                t = mcq.get("topic") or mcq.get("category") or "General"
                is_corr = mcq.get("is_correct", False)
                topic_scores.setdefault(t, []).append(100 if is_corr else 0)

            # Extract Descriptive topic performance
            for desc in interview_res.get("descriptive_details", []):
                t = desc.get("topic") or desc.get("category") or "General"
                s = desc.get("score") or desc.get("similarity_score") or 50
                topic_scores.setdefault(t, []).append(float(s))

            # Extract Coding topic performance
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

        # Compile topic performance summaries
        topic_performance = []
        interview_strengths = []
        interview_weaknesses = []

        for topic_name, scores in topic_scores.items():
            avg_topic_score = round(sum(scores) / len(scores), 1)
            is_strong = avg_topic_score >= 70
            status_label = "Strong" if is_strong else "Needs Improvement"
            topic_performance.append({
                "topic": topic_name,
                "score": avg_topic_score,
                "status": status_label
            })
            if is_strong:
                interview_strengths.append({
                    "skill": topic_name,
                    "source": "AI Interview Verified",
                    "details": f"Scored {avg_topic_score}% on interview questions for {topic_name}"
                })
            else:
                interview_weaknesses.append({
                    "skill": topic_name,
                    "source": "Interview Deficit",
                    "details": f"Poor score in interview ({avg_topic_score}%) — missed key technical concepts",
                    "severity": "High" if avg_topic_score < 50 else "Medium"
                })

        for wt in weak_topics:
            if not any(w["skill"].lower() == wt.lower() for w in interview_weaknesses):
                interview_weaknesses.append({
                    "skill": wt,
                    "source": "Interview Weak Topic",
                    "details": f"Identified as knowledge gap during technical interview",
                    "severity": "High"
                })

        # Run ML engine analysis
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

        # CV Strengths & Weaknesses
        cv_strengths = []
        cv_weaknesses = []
        matched_cv_skills = analysis.get("matched_skills", [])
        missing_required = analysis.get("missing_required", [])
        missing_optional = analysis.get("missing_optional", [])

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

        # Combined strengths and weaknesses
        all_strengths = interview_strengths + cv_strengths
        all_weaknesses = interview_weaknesses + cv_weaknesses

        # Compute composite fit percentage
        if interview_score is not None and cv_matching_score is not None:
            composite_fit = round(0.55 * interview_score + 0.45 * cv_matching_score, 1)
        elif interview_score is not None:
            composite_fit = round(interview_score, 1)
        elif cv_matching_score is not None:
            composite_fit = round(cv_matching_score, 1)
        else:
            composite_fit = round((analysis.get("skill_match_pct", 50)), 1)

        # Target course recommendations specifically addressing these weaknesses
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

        reports.append({
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
            "composite_score": composite_fit,
            "interview_breakdown": {
                "mcq_score": mcq_score,
                "descriptive_score": descriptive_score,
                "coding_score": coding_score,
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
        })

    return {"success": True, "candidate_id": candidate_id, "total_applied_jobs": len(reports), "reports": reports}

