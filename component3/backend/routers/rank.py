"""Component 3 — ranking router."""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone

import requests
from fastapi import APIRouter, HTTPException, Request
from starlette.concurrency import run_in_threadpool
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.schemas import (RankRequest, RankWeightsRequest, RankedCandidate,
                            CandidateInput)
from services.ranking_service import get_service

from engine.css_engine import JobRequirementProfile

router = APIRouter()
logger = logging.getLogger("component3")
limiter = Limiter(key_func=get_remote_address)

COMPONENT4_URL = os.getenv("COMPONENT4_URL", "http://127.0.0.1:8004")

EDU_STR = {1: "Diploma", 2: "B.Sc. Computer Science",
           3: "M.Sc. Computer Science", 4: "Ph.D. Computer Science"}


def _skill_gap_report(c: CandidateInput, job_role: str):
    resp = requests.post(
        f"{COMPONENT4_URL}/api/v1/skill-gap/analyze",
        json={
            "candidate_id": c.candidate_id,
            "candidate_name": c.candidate_name or c.candidate_id,
            "job_role": job_role.replace("_", " "),
            "skills": c.skills,
            "experience_years": int(c.years_experience),
            "education": EDU_STR.get(c.edu_level, "B.Sc. Computer Science"),
            "certifications": "None",
            "certifications_count": 0,
            "projects_count": 0,
            "job_level": "Mid-Level",
            "work_mode": "Hybrid",
            "cv_matching_score": c.cv_matching_score,
            "interview_score": c.interview_score,
            "mcq_score": c.mcq_score,
            "descriptive_score": c.descriptive_score,
            "coding_score": c.coding_score,
            "weak_topics": [],
            "failed_mcq_topics": [],
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("data", {})


async def _fetch_skill_gap(c, job_role):
    """Fetch skill gap for a single candidate, returning (c, report) or (c, None)."""
    try:
        report = await run_in_threadpool(_skill_gap_report, c, job_role)
        return c, report
    except Exception as exc:
        logger.warning("Skill-gap call failed for %s: %s", c.candidate_id, exc)
        return c, None


@router.post("/rank/compute", summary="Compute CSS and rank candidates")
@limiter.limit("20/minute")
async def compute_rank(request: Request, payload: RankRequest):
    service = get_service()
    try:
        job, ranked = service.rank(
            payload.job_role, payload.candidates,
            w_cv=payload.w_cv, w_int=payload.w_int, use_ltr=payload.use_ltr)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if payload.include_skill_gap:
        # Parallelize skill-gap calls across all candidates
        candidates_with_skills = [r["input"] for r in ranked if r["input"].skills]
        if candidates_with_skills:
            tasks = [
                _fetch_skill_gap(c, payload.job_role)
                for c in candidates_with_skills
            ]
            results = await asyncio.gather(*tasks)
            # Map results back to ranked list
            sg_map = {c.candidate_id: report for c, report in results if report}
            for r in ranked:
                report = sg_map.get(r["candidate_id"])
                if report:
                    r["hire_probability"] = report.get("hire_probability")
                    r["predicted_hire"] = report.get("predicted_hire")

    out = []
    for r in ranked:
        out.append(RankedCandidate(
            rank=r["rank"],
            candidate_id=r["candidate_id"],
            candidate_name=r["candidate_name"],
            S_edu=r["S_edu"],
            S_exp=r["S_exp"],
            S_skill=r["S_skill"],
            S_cv=r["S_cv"],
            S_int=r["S_int"],
            CSS=r["CSS"],
            P_mcq=r["P_mcq"],
            P_desc=r["P_desc"],
            P_code=r["P_code"],
            ltr_score=r.get("ltr_score"),
            passed_hard_filter=r["passed_hard_filter"],
            filter_fail_reason=r["filter_fail_reason"],
            hire_probability=r.get("hire_probability"),
            predicted_hire=r.get("predicted_hire"),
        ).model_dump())

    job_id = payload.job_id or f"JOB_{payload.job_role}"
    await request.app.state.store.delete("rankings", {"job_id": job_id})
    await request.app.state.store.delete("ranked_candidates", {"job_id": job_id})
    doc = {
        "job_id": job_id,
        "job_role": payload.job_role,
        "job_title": job.job_title,
        "w_cv": payload.w_cv,
        "w_int": payload.w_int,
        "use_ltr": payload.use_ltr,
        "weights": {
            "w_edu": job.w_edu, "w_exp": job.w_exp, "w_skill": job.w_skill,
            "w_mcq": job.w_mcq, "w_desc": job.w_desc, "w_code": job.w_code,
        },
        "ranked_candidates": out,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await request.app.state.store.insert_one("rankings", doc)

    # Bulk insert ranked candidates
    bulk_docs = [
        {
            "candidate_id": r["candidate_id"],
            "job_id": job_id,
            "job_role": payload.job_role,
            "rank": r["rank"],
            "CSS": r["CSS"],
        }
        for r in ranked
    ]
    await request.app.state.store.insert_many("ranked_candidates", bulk_docs)

    return {"success": True, "job_id": job_id, "data": out}


@router.get("/rank/results/{job_id}", summary="Fetch ranked list for a job")
async def get_results(job_id: str, request: Request):
    doc = await request.app.state.store.find_one("rankings", {"job_id": job_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Ranking not found")
    return {"success": True, "data": doc}


@router.post("/rank/weights", summary="Set employer scoring weights")
async def set_weights(payload: RankWeightsRequest, request: Request):
    if payload.job_role not in get_service().roles():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid job_role. Available: {sorted(get_service().roles())}")
    if abs(payload.w_cv + payload.w_int - 1.0) > 1e-4:
        raise HTTPException(status_code=400, detail="w_cv + w_int must equal 1.0")
    doc = {
        "job_role": payload.job_role,
        "w_cv": payload.w_cv,
        "w_int": payload.w_int,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    weight_id = await request.app.state.store.insert_one("weight_profiles", doc)
    return {"success": True, "weight_id": weight_id, "data": doc}


@router.get("/rank/explain/{candidate_id}",
            summary="Explain a candidate's ranking across jobs")
async def explain_candidate(candidate_id: str, request: Request):
    docs = await request.app.state.store.find_all(
        "ranked_candidates", {"candidate_id": candidate_id})
    if not docs:
        raise HTTPException(status_code=404, detail="Candidate not ranked yet")
    service = get_service()
    explanations = []
    for d in docs:
        ranking = await request.app.state.store.find_one(
            "rankings", {"job_id": d["job_id"]})
        if not ranking:
            continue
        candidate = next(
            (c for c in ranking["ranked_candidates"]
             if c["candidate_id"] == candidate_id), None)
        if candidate is None:
            continue
        job = JobRequirementProfile.from_role(ranking["job_role"])
        job.W_CV, job.W_INT = ranking["w_cv"], ranking["w_int"]
        contributions = [
            {"feature": name, "value": candidate[k],
             "weight": w,
             "contribution": round(candidate[k] * w, 4)}
            for name, k, w in [
                ("S_edu", "S_edu", job.w_edu * job.W_CV),
                ("S_exp", "S_exp", job.w_exp * job.W_CV),
                ("S_skill", "S_skill", job.w_skill * job.W_CV),
                ("P_mcq", "P_mcq", job.w_mcq * job.W_INT),
                ("P_desc", "P_desc", job.w_desc * job.W_INT),
                ("P_code", "P_code", job.w_code * job.W_INT),
            ]
        ]
        explanations.append({
            "job_id": d["job_id"],
            "job_role": ranking["job_role"],
            "rank": d["rank"],
            "css": candidate["CSS"],
            "contributions": contributions,
            "top_drivers": sorted(
                contributions, key=lambda x: x["contribution"], reverse=True)[:3],
        })
    return {"success": True, "candidate_id": candidate_id,
            "explanations": explanations}


@router.get("/rank/jobs", summary="List supported roles")
async def list_roles():
    return {"success": True, "roles": get_service().roles(),
            "count": len(get_service().roles())}


@router.get("/rank/pipeline/{job_id}", summary="Rank real applicants for a job")
@limiter.limit("10/minute")
async def rank_pipeline(request: Request, job_id: str):
    """Fetch real applicants from C0 MongoDB, build candidate inputs, and rank them."""
    import motor.motor_asyncio
    from models.schemas import CandidateInput
    
    # Connect to same MongoDB as C0
    c0_mongo_uri = os.environ.get("C0_MONGODB_URI", os.environ.get("MONGODB_URI", "mongodb://localhost:27017"))
    c0_db_name = os.environ.get("C0_DB_NAME", "recruit_ai")
    client = motor.motor_asyncio.AsyncIOMotorClient(c0_mongo_uri)
    db = client[c0_db_name]
    
    try:
        # 1. Fetch job details
        from bson import ObjectId
        try:
            job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        except Exception:
            raise HTTPException(status_code=404, detail="Job not found")
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job_role = job.get("title", "").replace(" ", "_")
        required_skills = job.get("required_skills", [])
        
        # 2. Fetch applications for this job
        cursor = db.applications.find({"job_id": ObjectId(job_id)})
        applicants = await cursor.to_list(length=200)
        
        if not applicants:
            return {"success": True, "job_id": job_id, "data": [], "message": "No applicants"}
        
        # 3. Build candidate inputs from applicant + resume + interview data
        candidates = []
        for app in applicants:
            candidate_id = app.get("candidate_id", "")
            candidate_name = app.get("candidate_name", "")
            
            # Fetch resume data
            resume_skills = []
            experience_years = 0
            edu_level = 2
            resume = await db.resumes.find_one({"candidate_id": candidate_id})
            if resume:
                resume_skills = resume.get("skills", [])
                experience_years = resume.get("experience_years", 0)
                edu_str = resume.get("education", "").lower()
                if "phd" in edu_str or "doctorate" in edu_str:
                    edu_level = 5
                elif "master" in edu_str or "m.sc" in edu_str or "mba" in edu_str:
                    edu_level = 4
                elif "bachelor" in edu_str or "b.sc" in edu_str or "b.tech" in edu_str:
                    edu_level = 3
                elif "diploma" in edu_str:
                    edu_level = 2
                else:
                    edu_level = 1
            
            # Fetch interview scores
            mcq_score = 0
            descriptive_score = 0
            coding_score = 0
            scores = await db.interview_scores.find({"candidate_id": candidate_id}).sort("created_at", -1).to_list(length=1)
            if scores:
                latest = scores[0]
                mcq_score = latest.get("mcq_score", 0) / 100
                descriptive_score = latest.get("descriptive_score", 0) / 100
                coding_score = latest.get("coding_score", 0) / 100
            
            # Calculate skill match
            matched = sum(1 for s in required_skills if any(s.lower() in rs.lower() for rs in resume_skills)) if resume_skills else 0
            skill_score_raw = matched / max(len(required_skills), 1)
            
            candidates.append(CandidateInput(
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                job_role=job_role,
                years_experience=experience_years,
                edu_level=edu_level,
                skill_score_raw=skill_score_raw,
                P_mcq=mcq_score,
                P_desc=descriptive_score,
                P_code=coding_score,
                skills=resume_skills,
            ))
        
        if not candidates:
            return {"success": True, "job_id": job_id, "data": [], "message": "No valid candidates"}
        
        # 4. Rank candidates
        service = get_service()
        try:
            job_obj, ranked = service.rank(
                job_role, candidates,
                w_cv=0.4, w_int=0.6, use_ltr=True)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        
        out = []
        for r in ranked:
            out.append({
                "rank": r["rank"],
                "candidate_id": r["candidate_id"],
                "candidate_name": r["candidate_name"],
                "CSS": round(r["CSS"], 4),
                "S_cv": round(r["S_cv"], 4),
                "S_int": round(r["S_int"], 4),
                "P_mcq": r["P_mcq"],
                "P_desc": r["P_desc"],
                "P_code": r["P_code"],
                "ltr_score": r.get("ltr_score"),
                "passed_hard_filter": r["passed_hard_filter"],
            })
        
        return {"success": True, "job_id": job_id, "job_role": job_role, "data": out}
    finally:
        client.close()
