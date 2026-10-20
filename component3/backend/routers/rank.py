"""Component 3 — ranking router."""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.concurrency import run_in_threadpool
from slowapi import Limiter
from slowapi.util import get_remote_address

from auth_guard import require_identity, require_owner_or_service

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
async def compute_rank(request: Request, payload: RankRequest, identity: dict = Depends(require_identity)):
    service = get_service()
    try:
        job, ranked = service.rank(
            payload.job_role, payload.candidates,
            w_cv=payload.w_cv, w_int=payload.w_int, use_ltr=payload.use_ltr)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if payload.include_skill_gap:
        candidates_with_skills = [r["input"] for r in ranked if r["input"].skills]
        if candidates_with_skills:
            tasks = [
                _fetch_skill_gap(c, payload.job_role)
                for c in candidates_with_skills
            ]
            results = await asyncio.gather(*tasks)
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
    try:
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
    except Exception as e:
        logger.warning("Store ranking error (non-fatal): %s", e)

    return {"success": True, "job_id": job_id, "data": out}


@router.get("/rank/results/{job_id}", summary="Fetch ranked list for a job")
async def get_results(job_id: str, request: Request, identity: dict = Depends(require_identity)):
    doc = await request.app.state.store.find_one("rankings", {"job_id": job_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Ranking not found")
    return {"success": True, "data": doc}


@router.post("/rank/weights", summary="Set employer scoring weights")
@limiter.limit("20/minute")
async def set_weights(payload: RankWeightsRequest, request: Request, identity: dict = Depends(require_identity)):
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


@router.get("/rank/explain/{candidate_id}", summary="Explain a candidate's ranking across jobs")
async def explain_candidate(candidate_id: str, request: Request, identity: dict = Depends(require_identity)):
    require_owner_or_service(identity, candidate_id)
    docs = await request.app.state.store.find_all("ranked_candidates", {"candidate_id": candidate_id})
    if not docs:
        raise HTTPException(status_code=404, detail="Candidate not ranked yet")
    service = get_service()
    explanations = []
    for d in docs:
        ranking = await request.app.state.store.find_one("rankings", {"job_id": d["job_id"]})
        if not ranking:
            continue
        candidate = next((c for c in ranking.get("ranked_candidates", []) if c.get("candidate_id") == candidate_id), None)
        if candidate is None:
            continue
        job_prof = JobRequirementProfile.from_role(ranking.get("job_role", "Software_Engineer"))
        job_prof.W_CV, job_prof.W_INT = ranking.get("w_cv", 0.4), ranking.get("w_int", 0.6)
        contributions = [
            {"feature": name, "value": candidate.get(k, 0),
             "weight": w,
             "contribution": round(candidate.get(k, 0) * w, 4)}
            for name, k, w in [
                ("S_edu", "S_edu", job_prof.w_edu * job_prof.W_CV),
                ("S_exp", "S_exp", job_prof.w_exp * job_prof.W_CV),
                ("S_skill", "S_skill", job_prof.w_skill * job_prof.W_CV),
                ("P_mcq", "P_mcq", job_prof.w_mcq * job_prof.W_INT),
                ("P_desc", "P_desc", job_prof.w_desc * job_prof.W_INT),
                ("P_code", "P_code", job_prof.w_code * job_prof.W_INT),
            ]
        ]
        explanations.append({
            "job_id": d.get("job_id"),
            "job_role": ranking.get("job_role"),
            "rank": d.get("rank"),
            "css": candidate.get("CSS"),
            "contributions": contributions,
            "top_drivers": sorted(contributions, key=lambda x: x["contribution"], reverse=True)[:3],
        })
    return {"success": True, "candidate_id": candidate_id, "explanations": explanations}


@router.get("/rank/jobs", summary="List supported roles")
async def list_roles():
    return {"success": True, "roles": get_service().roles(), "count": len(get_service().roles())}

def _normalize_role_match(role_str: str) -> str:
    """Normalize role string by trimming, lowercasing, and mapping common technical titles."""
    if not role_str:
        return "Software_Engineer"
    r = str(role_str).strip().lower().replace(" ", "_").replace("-", "_")
    if "software" in r or "developer" in r or "full_stack" in r or "backend" in r or "frontend" in r:
        return "Software_Engineer"
    if "data_sci" in r or "machine_learn" in r or "ai" in r:
        return "Data_Scientist"
    if "data_eng" in r or "etl" in r or "pipeline" in r:
        return "Data_Engineer"
    if "devops" in r or "sre" in r or "infra" in r:
        return "DevOps_Engineer"
    if "cloud" in r or "aws" in r or "azure" in r:
        return "Cloud_Architect"
    if "sec" in r or "cyber" in r:
        return "Security_Engineer"
    if "qa" in r or "test" in r:
        return "QA_Engineer"
    if "mobile" in r or "android" in r or "ios" in r:
        return "Mobile_Developer"
    if "frontend" in r or "ui" in r:
        return "Frontend_Developer"
    if "backend" in r:
        return "Backend_Developer"
    return "Software_Engineer"


import time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

_PIPELINE_CACHE: Dict[str, Any] = {}
_PIPELINE_TTL = 0.0

def _is_doc_for_job(doc: dict, job_id: str, job: Optional[dict], job_keys: list) -> bool:
    if not doc or not isinstance(doc, dict):
        return False
    doc_job_id = str(doc.get('job_id') or '').strip()
    if doc_job_id and any(str(k).strip() == doc_job_id for k in job_keys):
        return True
    from bson import ObjectId
    if ObjectId.is_valid(job_id) and doc_job_id == str(ObjectId(job_id)):
        return True
    doc_role = str(doc.get('job_role') or doc.get('job_title') or '').strip().lower()
    if job and doc_role:
        j_title = str(job.get('title', '')).strip().lower()
        j_role = str(job.get('job_role', '')).strip().lower()
        if (j_title and doc_role == j_title) or (j_role and doc_role == j_role):
            return True
    return False

class PipelineBatchRequest(BaseModel):
    job_ids: List[str]

async def _get_rank_db(request: Request):
    store = getattr(request.app.state, 'store', None)
    db = getattr(store, '_db', None) if store is not None else None
    if db is None:
        try:
            import motor.motor_asyncio
            try:
                import dns.resolver
                _res = dns.resolver.Resolver()
                _res.nameservers = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
                dns.resolver.default_resolver = _res
            except Exception:
                pass
            client = motor.motor_asyncio.AsyncIOMotorClient(
                os.environ["MONGODB_URI"],
                serverSelectionTimeoutMS=15000
            )
            db = client[os.getenv("DB_NAME", "HR")]
        except Exception:
            pass
    return db

async def _compute_single_job_pipeline(db, job_id: str):
    cached = _PIPELINE_CACHE.get(job_id)
    if cached and time.time() - cached[0] < _PIPELINE_TTL:
        return cached[1]

    from bson import ObjectId
    job = None
    if ObjectId.is_valid(job_id):
        try:
            job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        except Exception:
            pass
    if job is None:
        job = await db.jobs.find_one({"id": job_id})
    if job is None:
        job = await db.jobs.find_one({"_id": job_id})
        
    job_title = job.get("title", "Software Engineer") if job else "Software Engineer"
    raw_role = (job.get("job_role") if job else None) or job_title
    job_role = _normalize_role_match(raw_role)
    service = get_service()
    supported_roles = service.roles()
    if job_role not in supported_roles:
        job_role = "Software_Engineer"
        for r in supported_roles:
            if r.lower() in job_title.lower() or job_title.lower() in r.lower():
                job_role = r
                break

    required_skills = job.get("required_skills", ["Python", "SQL", "Git"]) if job else ["Python", "SQL"]
    exp_required = float((job.get("experience_required") or 2.0) if job else 2.0)
    
    # 2. Fetch candidates for this job using indexed $in lookups
    job_keys = [job_id, str(job_id)]
    if ObjectId.is_valid(job_id):
        job_keys.append(ObjectId(job_id))

    role_keys = []
    if job:
        j_t = job.get("title")
        j_r = job.get("job_role")
        if j_t and j_t not in job_keys:
            job_keys.append(j_t)
            role_keys.append(j_t)
        if j_r and j_r not in job_keys:
            job_keys.append(j_r)
            role_keys.append(j_r)

    apps_task = db.applications.find({"job_id": {"$in": job_keys}}).to_list(300)
    preds_task = db.predictions.find({"job_id": {"$in": job_keys}}).to_list(300)
    scores_task = db.interview_scores.find({"job_id": {"$in": job_keys}}).to_list(300)
    
    if role_keys:
        results_task = db.results.find({"$or": [{"job_id": {"$in": job_keys}}, {"job_role": {"$in": role_keys}}]}).to_list(300)
    else:
        results_task = db.results.find({"job_id": {"$in": job_keys}}).to_list(300)

    raw_apps, raw_preds, raw_scores, raw_results = await asyncio.gather(
        apps_task, preds_task, scores_task, results_task
    )

    seen_candidates = set()
    applicants = []

    for app in raw_apps:
        cid = str(app.get("candidate_id", ""))
        if cid and cid not in seen_candidates:
            seen_candidates.add(cid)
            applicants.append({
                "candidate_id": cid,
                "candidate_name": app.get("candidate_name", ""),
                "resume_id": app.get("resume_id", ""),
            })

    for pred in raw_preds:
        cid = str(pred.get("candidate_id", ""))
        if cid and cid not in seen_candidates:
            seen_candidates.add(cid)
            applicants.append({
                "candidate_id": cid,
                "candidate_name": pred.get("candidate_name", ""),
                "resume_id": pred.get("resume_id", ""),
            })

    for sc in raw_scores:
        cid = str(sc.get("candidate_id", ""))
        if cid and cid not in seen_candidates:
            seen_candidates.add(cid)
            applicants.append({
                "candidate_id": cid,
                "candidate_name": sc.get("candidate_name", ""),
                "resume_id": sc.get("resume_id", ""),
            })

    for res in raw_results:
        cid = str(res.get("candidate_id", ""))
        if cid and cid not in seen_candidates:
            seen_candidates.add(cid)
            applicants.append({
                "candidate_id": cid,
                "candidate_name": res.get("candidate_name", ""),
                "resume_id": res.get("resume_id", ""),
            })

    if not applicants:
        empty_res = {"success": True, "job_id": job_id, "data": [], "message": "No applicants have applied or completed interviews for this position yet."}
        _PIPELINE_CACHE[job_id] = (time.time(), empty_res)
        return empty_res

    # 3. Parallel batch-fetch users, resumes, predictions, and interview scores using indexed $in
    candidate_ids = [str(app.get("candidate_id") or app.get("_id", "CAND")) for app in applicants]
    valid_oids = [ObjectId(c) for c in candidate_ids if ObjectId.is_valid(c)]
    all_cids = list(set(candidate_ids + [str(v) for v in valid_oids]))
    all_query_ids = list(all_cids) + valid_oids

    user_map = {}
    resume_map = {}
    pred_map = {}
    scores_map = {}

    u_task = db.users.find({"_id": {"$in": valid_oids}}).to_list(200) if valid_oids else asyncio.sleep(0, result=[])
    r_task = db.resumes.find({"candidate_id": {"$in": all_query_ids}}).sort("created_at", -1).to_list(200)
    p_task = db.predictions.find({"candidate_id": {"$in": all_query_ids}}).sort("created_at", -1).to_list(200)
    s_task = db.interview_scores.find({"candidate_id": {"$in": all_query_ids}}).sort("created_at", -1).to_list(200)
    res_task = db.results.find({"candidate_id": {"$in": all_query_ids}}).sort("created_at", -1).to_list(200)
    cva_task = db.cv_analyses.find({"candidate_id": {"$in": all_query_ids}}).sort("analysis_timestamp", -1).to_list(200)

    u_list, r_list, p_list, s_list, res_list, cva_list = await asyncio.gather(
        u_task, r_task, p_task, s_task, res_task, cva_task
    )

    for u in (u_list or []):
        user_map[str(u["_id"])] = u.get("full_name") or u.get("name") or u.get("email") or "Candidate"

    for r in r_list:
        cid = str(r.get("candidate_id", ""))
        if cid and cid not in resume_map:
            resume_map[cid] = r
        if str(r.get("_id", "")) not in resume_map:
            resume_map[str(r["_id"])] = r

    for p in p_list:
        cid = str(p.get("candidate_id", ""))
        if cid and cid not in pred_map and _is_doc_for_job(p, job_id, job, job_keys):
            pred_map[cid] = p

    for s in s_list:
        cid = str(s.get("candidate_id", ""))
        if cid and cid not in scores_map and _is_doc_for_job(s, job_id, job, job_keys):
            scores_map[cid] = s

    for res in res_list:
        cid = str(res.get("candidate_id", ""))
        if cid and cid not in scores_map and _is_doc_for_job(res, job_id, job, job_keys):
            scores_map[cid] = res

    cva_map = {}
    for ca in (cva_list or []):
        cid = str(ca.get("candidate_id", ""))
        if cid and cid not in cva_map and _is_doc_for_job(ca, job_id, job, job_keys):
            cva_map[cid] = ca

    # 4. Build candidate inputs and calculate exact scores
    scored_candidates = []
    for app in applicants:
        candidate_id = str(app.get("candidate_id") or app.get("_id", "CAND"))
        candidate_name = app.get("candidate_name") or user_map.get(candidate_id) or (resume_map.get(candidate_id, {}).get("candidate_name")) or "Candidate"
        
        resume = resume_map.get(candidate_id)
        pred_doc = pred_map.get(candidate_id)
        latest_score = scores_map.get(candidate_id)
        cva_doc = cva_map.get(candidate_id)

        resume_skills = app.get("resume_skills", []) or (resume.get("skills", []) if resume else [])
        experience_years = app.get("experience_years", 0) or (resume.get("experience_years", 0) if resume else 0)
        edu_level = 2

        if resume:
            edu_str = str(resume.get("education", "")).lower()
            if "phd" in edu_str or "doctorate" in edu_str:
                edu_level = 4
            elif "master" in edu_str or "m.sc" in edu_str or "mba" in edu_str:
                edu_level = 3
            elif "bachelor" in edu_str or "b.sc" in edu_str or "b.tech" in edu_str:
                edu_level = 2
            elif "diploma" in edu_str:
                edu_level = 1
            else:
                edu_level = 2

        # Determine whether candidate completed CV Match and/or Interview
        cand_has_cv = bool(pred_doc is not None or (resume is not None and resume_skills))
        cand_has_interview = bool(latest_score is not None and (latest_score.get("interview_score") is not None or latest_score.get("overall_score") is not None))

        # CV Sub-Scores
        s_skill = None
        s_exp = None
        s_edu = None
        s_cv = None

        if cand_has_cv:
            if cva_doc and (cva_doc.get("cv_matching_score") is not None or cva_doc.get("optional_legacy_score") is not None or cva_doc.get("S_skill") is not None):
                s_skill = round(float(cva_doc.get("S_skill") or cva_doc.get("s_skill") or (cva_doc.get("component_1_scores") or {}).get("S_skill", 70)) / 100.0, 4)
                s_exp = round(float(cva_doc.get("S_exp") or cva_doc.get("s_exp") or (cva_doc.get("component_1_scores") or {}).get("S_exp", 70)) / 100.0, 4)
                s_edu = round(float(cva_doc.get("S_edu") or cva_doc.get("s_edu") or (cva_doc.get("component_1_scores") or {}).get("S_edu", 80)) / 100.0, 4)
                raw_cv = cva_doc.get("cv_matching_score") or cva_doc.get("optional_legacy_score")
                if raw_cv is not None:
                    s_cv = round(float(raw_cv) / 100.0, 4)
                else:
                    s_cv = round(0.50 * s_skill + 0.30 * s_exp + 0.20 * s_edu, 4)
            elif pred_doc and pred_doc.get("skill_score") is not None:
                s_skill = round(float(pred_doc["skill_score"]) / 100.0, 4)
                if pred_doc.get("experience_score") is not None:
                    s_exp = round(float(pred_doc["experience_score"]) / 100.0, 4)
                else:
                    s_exp = round(min(float(experience_years or 2.0) / max(exp_required, 1.0), 1.0), 4)
                if pred_doc.get("education_score") is not None:
                    s_edu = round(float(pred_doc["education_score"]) / 100.0, 4)
                else:
                    edu_weights = {1: 0.60, 2: 0.75, 3: 0.85, 4: 1.00}
                    s_edu = round(0.60 * edu_weights.get(edu_level, 0.75) + 0.40 * 0.90, 4)
                if pred_doc.get("overall_score") is not None:
                    s_cv = round(float(pred_doc["overall_score"]) / 100.0, 4)
                else:
                    s_cv = round(0.50 * s_skill + 0.30 * s_exp + 0.20 * s_edu, 4)
            elif app.get("cv_score") is not None or app.get("overall_score") is not None:
                s_cv = round(float(app.get("cv_score") or app.get("overall_score") or 0) / 100.0, 4)
                s_skill = round(float(app.get("skill_score") or 70) / 100.0, 4)
                s_exp = round(float(app.get("experience_score") or 70) / 100.0, 4)
                s_edu = round(float(app.get("education_score") or 80) / 100.0, 4)
            elif resume_skills and required_skills:
                matched = sum(1 for s in required_skills if any(s.lower() in rs.lower() or rs.lower() in s.lower() for rs in resume_skills))
                s_skill = round(float(matched) / max(len(required_skills), 1), 4)
                s_exp = round(min(float(experience_years or 2.0) / max(exp_required, 1.0), 1.0), 4)
                edu_weights = {1: 0.60, 2: 0.75, 3: 0.85, 4: 1.00}
                s_edu = round(0.60 * edu_weights.get(edu_level, 0.75) + 0.40 * 0.90, 4)
                s_cv = round(0.50 * s_skill + 0.30 * s_exp + 0.20 * s_edu, 4)
            else:
                s_skill = 0.70
                s_exp = 0.70
                s_edu = 0.80
                s_cv = 0.72

        # Interview Sub-Scores
        p_mcq = None
        p_desc = None
        p_code = None
        s_int = None

        if cand_has_interview:
            p_mcq = round(float(latest_score.get("mcq_score", 0) or 0) / 100.0, 4)
            p_desc = round(float(latest_score.get("descriptive_score", 0) or 0) / 100.0, 4)
            p_code = round(float(latest_score.get("coding_score", 0) or 0) / 100.0, 4)
            has_actual_code = any(bool(cd.get("code_text", "").strip()) for cd in latest_score.get("coding_details", [])) if latest_score.get("coding_details") else (p_code > 0.045)
            if not has_actual_code and p_mcq == 0 and p_desc == 0:
                p_code = 0.0
            if latest_score.get("interview_score") is not None:
                s_int = round(float(latest_score["interview_score"]) / 100.0, 4)
                if not has_actual_code and p_mcq == 0 and p_desc == 0:
                    s_int = 0.0
            else:
                s_int = round(0.20 * p_mcq + 0.30 * p_desc + 0.50 * p_code, 4)

        # Master Composite Scoring System (CSS) calculation
        if cand_has_cv and cand_has_interview:
            css = round(0.40 * s_cv + 0.60 * s_int, 4)
        elif cand_has_cv:
            css = round(s_cv, 4)
        elif cand_has_interview:
            css = round(s_int, 4)
        else:
            css = 0.50

        integ_raw = (latest_score.get("integrity_score")
                     if isinstance(latest_score, dict) else None)
        if integ_raw is None and isinstance(latest_score, dict):
            integ_raw = (latest_score.get("proctoring") or {}).get("integrity_score")
        try:
            integ_val = (round(max(0.0, min(100.0, float(integ_raw))), 1)
                         if integ_raw is not None else None)
        except (TypeError, ValueError):
            integ_val = None

        # Hard Filter Validation
        passed_hard_filter = True
        filter_fail_reason = ""
        if cand_has_cv and s_skill is not None and s_skill < 0.38:
            passed_hard_filter = False
            filter_fail_reason = f"Skill alignment ({s_skill*100:.0f}%) below minimum threshold (38%)"
        elif cand_has_interview and p_code is not None and p_code < 0.25:
            passed_hard_filter = False
            filter_fail_reason = f"Live coding score ({p_code*100:.0f}%) below minimum threshold (25%)"

        # Strengths & Weaknesses
        strengths = []
        weaknesses = []

        if s_skill is not None:
            if s_skill >= 0.75:
                strengths.append(f"Strong CV skill match ({s_skill*100:.0f}%)")
            elif s_skill < 0.50:
                weaknesses.append(f"Low CV skill alignment ({s_skill*100:.0f}%)")

        if s_exp is not None:
            if s_exp >= 0.75:
                strengths.append("Solid years of relevant experience")
            elif s_exp < 0.40:
                weaknesses.append("Limited industry experience")

        if p_code is not None:
            if p_code >= 0.80:
                strengths.append(f"Top-tier live coding & unit test pass rate ({p_code*100:.0f}%)")
            elif p_code < 0.50:
                weaknesses.append(f"Failed live coding test cases ({p_code*100:.0f}%)")

        if p_mcq is not None:
            if p_mcq >= 0.80:
                strengths.append(f"High conceptual MCQ score ({p_mcq*100:.0f}%)")
            elif p_mcq < 0.50:
                weaknesses.append(f"Low conceptual MCQ marks ({p_mcq*100:.0f}%)")

        if p_desc is not None:
            if p_desc >= 0.80:
                strengths.append(f"Clear architectural & descriptive explanations ({p_desc*100:.0f}%)")
            elif p_desc < 0.50:
                weaknesses.append(f"Weak descriptive theory answers ({p_desc*100:.0f}%)")

        if not passed_hard_filter:
            verdict = "Disqualified"
            badge_color = "#ef4444"
            reasoning = f"Failed mandatory role filter: {filter_fail_reason}."
        elif css >= 0.80:
            verdict = "Highly Qualified"
            badge_color = "#10b981"
            if cand_has_cv and cand_has_interview:
                reasoning = f"Top-ranked candidate with {s_int*100:.0f}% interview performance and {s_cv*100:.0f}% CV fit. Excellent coding and conceptual marks."
            elif cand_has_cv:
                reasoning = f"Top-tier CV profile match ({s_cv*100:.0f}%). Pending AI technical interview evaluation."
            else:
                reasoning = f"Top-tier AI technical interview performance ({s_int*100:.0f}%). Pending CV Match evaluation."
        elif css >= 0.65:
            verdict = "Recommended"
            badge_color = "#3b82f6"
            reasoning = f"Strong contender with {css*100:.0f}% overall fit. Good alignment across technical criteria with minor gaps."
        elif css >= 0.50:
            verdict = "Qualified"
            badge_color = "#f59e0b"
            reasoning = f"Moderate fit ({css*100:.0f}% Overall Fit). Demonstrates foundation but requires upskilling in key technical areas."
        else:
            verdict = "Disqualified"
            badge_color = "#ef4444"
            reasoning = f"Low score ({css*100:.0f}%). Significant deficits across technical requirements."

        integ = integ_val

        scored_candidates.append({
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "has_cv": cand_has_cv,
            "interview_completed": cand_has_interview,
            "integrity_score": integ,
            "CSS": css,
            "composite_fit_score": round(css * 100, 2),
            "final_score": round(css * 100, 2),
            "blended_score": round(css * 100, 2),
            "overall_score": round(css * 100, 2),
            "S_cv": s_cv,
            "cv_score": round(s_cv * 100, 2) if s_cv is not None else None,
            "S_int": s_int,
            "interview_score": round(s_int * 100, 2) if s_int is not None else None,
            "S_edu": s_edu,
            "education_score": round(s_edu * 100, 2) if s_edu is not None else None,
            "S_exp": s_exp,
            "experience_score": round(s_exp * 100, 2) if s_exp is not None else None,
            "S_skill": s_skill,
            "skill_score": round(s_skill * 100, 2) if s_skill is not None else None,
            "P_mcq": p_mcq,
            "mcq_score": round(p_mcq * 100, 2) if p_mcq is not None else None,
            "P_desc": p_desc,
            "descriptive_score": round(p_desc * 100, 2) if p_desc is not None else None,
            "P_code": p_code,
            "coding_score": round(p_code * 100, 2) if p_code is not None else None,
            "passed_hard_filter": passed_hard_filter,
            "filter_fail_reason": filter_fail_reason,
            "verdict": verdict,
            "recommendation": verdict,
            "badge_color": badge_color,
            "reasoning": reasoning,
            "strengths": strengths if strengths else ["Profile matches basic prerequisites"],
            "weaknesses": weaknesses if weaknesses else ["No critical deficits detected"],
        })

    # Priority Sorting: Completed Both (Tier 1, score desc) > Incomplete (Tier 2, score desc)
    completed = sorted(
        [c for c in scored_candidates if c.get("has_cv") and c.get("interview_completed")],
        key=lambda x: x.get("CSS", 0),
        reverse=True
    )
    incomplete = sorted(
        [c for c in scored_candidates if not (c.get("has_cv") and c.get("interview_completed"))],
        key=lambda x: x.get("CSS", 0),
        reverse=True
    )

    out = completed + incomplete
    for i, c in enumerate(out):
        c["rank"] = i + 1
    res_data = {"success": True, "job_id": job_id, "job_role": job_role, "data": out}
    _PIPELINE_CACHE[job_id] = (time.time(), res_data)
    return res_data

@router.get("/rank/pipeline/{job_id}", summary="Rank real applicants for a job")
@router.post("/rank/pipeline/{job_id}", summary="Rank real applicants for a job")
async def rank_pipeline(request: Request, job_id: str, identity: dict = Depends(require_identity)):
    """Fetch real applicants from MongoDB, build candidate inputs, and rank them."""
    try:
        db = await _get_rank_db(request)
        if db is None:
            raise HTTPException(status_code=503, detail="Database connection unavailable")
        return await _compute_single_job_pipeline(db, job_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("rank_pipeline fatal error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/rank/pipeline/batch", summary="Batch rank real applicants for multiple jobs")
async def rank_pipeline_batch(request: Request, payload: PipelineBatchRequest, identity: dict = Depends(require_identity)):
    """Batch compute candidate rankings across multiple jobs concurrently."""
    try:
        db = await _get_rank_db(request)
        if db is None:
            raise HTTPException(status_code=503, detail="Database connection unavailable")
        
        job_ids = [str(jid).strip() for jid in payload.job_ids if str(jid).strip()]
        if not job_ids:
            return {"success": True, "data": {}}
            
        tasks = [_compute_single_job_pipeline(db, jid) for jid in job_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        batch_data = {}
        for jid, res in zip(job_ids, results):
            if isinstance(res, Exception):
                logger.warning("Batch pipeline failed for job %s: %s", jid, res)
                batch_data[jid] = []
            else:
                batch_data[jid] = res.get("data", [])
                
        return {"success": True, "data": batch_data}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("rank_pipeline_batch fatal error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
