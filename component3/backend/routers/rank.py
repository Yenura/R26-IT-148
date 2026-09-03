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
async def get_results(job_id: str, request: Request):
    doc = await request.app.state.store.find_one("rankings", {"job_id": job_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Ranking not found")
    return {"success": True, "data": doc}


@router.post("/rank/weights", summary="Set employer scoring weights")
@limiter.limit("20/minute")
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


@router.get("/rank/explain/{candidate_id}", summary="Explain a candidate's ranking across jobs")
async def explain_candidate(candidate_id: str, request: Request):
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


import time
_PIPELINE_CACHE: dict = {}
_PIPELINE_TTL = 30.0

@router.get("/rank/pipeline/{job_id}", summary="Rank real applicants for a job")
@router.post("/rank/pipeline/{job_id}", summary="Rank real applicants for a job")
async def rank_pipeline(request: Request, job_id: str):
    """Fetch real applicants from MongoDB, build candidate inputs, and rank them."""
    cached = _PIPELINE_CACHE.get(job_id)
    if cached and time.time() - cached[0] < _PIPELINE_TTL:
        return cached[1]

    try:
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
                    os.getenv("MONGODB_URI", "mongodb+srv://admin:PxUm8dLzq5jqlHYN@coordinator.ljarc.mongodb.net/HR"),
                    serverSelectionTimeoutMS=15000
                )
                db = client[os.getenv("DB_NAME", "HR")]
            except Exception:
                pass
        if db is None:
            raise HTTPException(status_code=503, detail="Database connection unavailable")

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
        job_role = job_title.replace(" ", "_")
        service = get_service()
        supported_roles = service.roles()
        if job_role not in supported_roles:
            job_role = "Software_Engineer"
            for r in supported_roles:
                if r.lower() in job_title.lower() or job_title.lower() in r.lower():
                    job_role = r
                    break

        required_skills = job.get("required_skills", ["Python", "SQL", "Git"]) if job else ["Python", "SQL"]
        
        # 2. Fetch candidates for this job (Applications + CV Match + Interviewed + Results) in parallel
        # Strict job-ID scoping: only documents explicitly linked to THIS job posting.
        # Title/role-based fallbacks were removed — they matched candidates from other
        # companies' jobs sharing the same title (e.g. every "Software Engineer" posting),
        # making brand-new jobs appear to already have applicants.
        query_conditions = [{"job_id": job_id}, {"job_id": str(job_id)}]
        if ObjectId.is_valid(job_id):
            query_conditions.append({"job_id": ObjectId(job_id)})

        apps_task = db.applications.find({"$or": query_conditions}).to_list(300)
        preds_task = db.predictions.find({"$or": query_conditions}).to_list(300)
        scores_task = db.interview_scores.find({"$or": query_conditions}).to_list(300)
        results_task = db.results.find({"$or": query_conditions}).to_list(300)

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
            return {"success": True, "job_id": job_id, "data": [], "message": "No applicants have applied or completed interviews for this position yet."}

        # 3. Parallel batch-fetch users, resumes, predictions, and interview scores for all candidates
        candidate_ids = [str(app.get("candidate_id") or app.get("_id", "CAND")) for app in applicants]
        cand_filters = [{"candidate_id": {"$in": candidate_ids}}]
        valid_oids = [ObjectId(c) for c in candidate_ids if ObjectId.is_valid(c)]
        if valid_oids:
            cand_filters.append({"candidate_id": {"$in": valid_oids}})
            cand_filters.append({"_id": {"$in": valid_oids}})

        user_map = {}
        resume_map = {}
        pred_map = {}
        scores_map = {}

        u_task = db.users.find({"_id": {"$in": valid_oids}}).to_list(200) if valid_oids else asyncio.sleep(0, result=[])
        r_task = db.resumes.find({"$or": cand_filters}).sort("created_at", -1).to_list(200)
        p_task = db.predictions.find({"$or": cand_filters}).sort("created_at", -1).to_list(200)
        s_task = db.interview_scores.find({"$or": cand_filters}).sort("created_at", -1).to_list(200)
        res_task = db.results.find({"$or": cand_filters}).sort("created_at", -1).to_list(200)

        u_list, r_list, p_list, s_list, res_list = await asyncio.gather(
            u_task, r_task, p_task, s_task, res_task
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
            if cid and (cid not in pred_map or str(p.get("job_id")) == str(job_id)):
                pred_map[cid] = p

        for s in s_list:
            cid = str(s.get("candidate_id", ""))
            if cid and (cid not in scores_map or str(s.get("job_id")) == str(job_id)):
                scores_map[cid] = s

        for res in res_list:
            cid = str(res.get("candidate_id", ""))
            if cid and (cid not in scores_map or str(res.get("job_id")) == str(job_id)):
                scores_map[cid] = res

        # 4. Build candidate inputs
        candidates = []
        for app in applicants:
            candidate_id = str(app.get("candidate_id") or app.get("_id", "CAND"))
            candidate_name = app.get("candidate_name") or user_map.get(candidate_id) or (resume_map.get(candidate_id, {}).get("candidate_name")) or "Candidate"
            
            resume_skills = app.get("resume_skills", [])
            experience_years = app.get("experience_years", 0)
            edu_level = 2
            
            if not resume_skills:
                resume = resume_map.get(candidate_id)
                if resume:
                    resume_skills = resume.get("skills", [])
                    experience_years = resume.get("experience_years", 0)
                    edu_str = resume.get("education", "").lower()
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

            if not resume_skills:
                resume_skills = ["Python", "SQL", "Git"]

            # Real interview scores from completed interviews
            latest_score = scores_map.get(candidate_id)
            if latest_score:
                mcq_score = (float(latest_score.get("mcq_score", 0) or 0)) / 100
                descriptive_score = (float(latest_score.get("descriptive_score", 0) or 0)) / 100
                coding_score = (float(latest_score.get("coding_score", 0) or 0)) / 100
                int_score_num = float(latest_score.get("interview_score", 0) or 0)
                # No coding section administered (non-coding roles) vs scored zero:
                # only an explicit coding_total == 0 proves the section was absent.
                # Docs without the field keep legacy behavior (gate applies).
                _ct = latest_score.get("coding_total", None)
                has_coding = True if _ct is None else int(_ct or 0) > 0
            else:
                mcq_score = 0.0
                descriptive_score = 0.0
                coding_score = 0.0
                int_score_num = None
                # No interview data at all: keep legacy behavior (gates apply),
                # so uninterviewed candidates cannot outrank interviewed ones.
                has_coding = True
            
            # Skill matching and CV 3-pillar scores from predictions
            pred_doc = pred_map.get(candidate_id)
            s_skill_val = None
            s_exp_val = None
            s_edu_val = None
            if pred_doc:
                if pred_doc.get("skill_score") is not None:
                    s_skill_val = float(pred_doc["skill_score"]) / 100.0
                if pred_doc.get("experience_score") is not None:
                    s_exp_val = float(pred_doc["experience_score"]) / 100.0
                if pred_doc.get("education_score") is not None:
                    s_edu_val = float(pred_doc["education_score"]) / 100.0
            
            if s_skill_val is None:
                matched = sum(1 for s in required_skills if any(s.lower() in rs.lower() or rs.lower() in s.lower() for rs in resume_skills)) if resume_skills else 0
                s_skill_val = matched / max(len(required_skills), 1)

            candidates.append(CandidateInput(
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                job_role=job_role,
                years_experience=float(experience_years or 2.0),
                edu_level=int(edu_level),
                skill_score_raw=float(s_skill_val),
                S_edu=s_edu_val,
                S_exp=s_exp_val,
                S_skill=s_skill_val,
                P_mcq=float(mcq_score),
                P_desc=float(descriptive_score),
                P_code=float(coding_score),
                has_coding=has_coding,
                skills=resume_skills,
                interview_score=int_score_num,
            ))
        
        if not candidates:
            return {"success": True, "job_id": job_id, "data": [], "message": "No valid candidates"}
        
        try:
            job_obj, ranked = service.rank(
                job_role, candidates,
                w_cv=0.4, w_int=0.6, use_ltr=True)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except Exception:
            job_obj, ranked = service.rank(
                "Software_Engineer", candidates,
                w_cv=0.4, w_int=0.6, use_ltr=True)
        
        out = []
        for r in ranked:
            s_cv = round(r["S_cv"], 4)
            s_int = round(r["S_int"], 4)
            cand_inp = r.get("input")
            cand_has_interview = (cand_inp and cand_inp.interview_score is not None) or (s_int > 0.0)
            
            if cand_has_interview:
                css = round(0.40 * s_cv + 0.60 * s_int, 4)
            else:
                css = s_cv
            s_edu = round(r.get("S_edu", 0), 4)
            s_exp = round(r.get("S_exp", 0), 4)
            s_skill = round(r.get("S_skill", 0), 4)
            p_mcq = round(r.get("P_mcq", 0), 4)
            p_desc = round(r.get("P_desc", 0), 4)
            p_code = round(r.get("P_code", 0), 4)
            
            strengths = []
            weaknesses = []
            
            if s_skill >= 0.75:
                strengths.append(f"Strong CV skill match ({s_skill*100:.0f}%)")
            elif s_skill < 0.50:
                weaknesses.append(f"Low CV skill alignment ({s_skill*100:.0f}%)")
                
            if s_exp >= 0.75:
                strengths.append("Solid years of relevant experience")
            elif s_exp < 0.40:
                weaknesses.append("Limited industry experience")
                
            if p_code >= 0.80:
                strengths.append(f"Top-tier live coding & unit test pass rate ({p_code*100:.0f}%)")
            elif p_code < 0.50:
                weaknesses.append(f"Failed live coding test cases ({p_code*100:.0f}%)")
                
            if p_mcq >= 0.80:
                strengths.append(f"High conceptual MCQ score ({p_mcq*100:.0f}%)")
            elif p_mcq < 0.50:
                weaknesses.append(f"Low conceptual MCQ marks ({p_mcq*100:.0f}%)")
                
            if p_desc >= 0.80:
                strengths.append(f"Clear architectural & descriptive explanations ({p_desc*100:.0f}%)")
            elif p_desc < 0.50:
                weaknesses.append(f"Weak descriptive theory answers ({p_desc*100:.0f}%)")
                
            if not r["passed_hard_filter"]:
                if r["CSS"] > 0:
                    verdict = "Near-Miss (Conditional)"
                    badge_color = "#f59e0b"
                    reasoning = f"Near-miss candidate: {r.get('filter_fail_reason', 'Slightly below threshold')}. CSS score penalized but still ranked."
                else:
                    verdict = "Disqualified (Filter Failed)"
                    badge_color = "#ef4444"
                    reasoning = f"Failed mandatory role filter: {r.get('filter_fail_reason', 'Did not meet prerequisites')}."
            elif css >= 0.80:
                verdict = "Highly Recommended"
                badge_color = "#22c55e"
                reasoning = f"Top-ranked candidate with {s_int*100:.0f}% interview performance and {s_cv*100:.0f}% CV fit. Excellent coding and conceptual marks."
            elif css >= 0.65:
                verdict = "Recommended"
                badge_color = "#3b82f6"
                reasoning = f"Strong contender with {s_int*100:.0f}% interview score. Good alignment across technical criteria with minor gaps."
            elif css >= 0.50:
                verdict = "Potential Match"
                badge_color = "#f59e0b"
                reasoning = f"Moderate fit ({css*100:.0f}% Composite). Demonstrates foundation but requires upskilling in: {', '.join(weaknesses[:2]) if weaknesses else 'key areas'}."
            else:
                verdict = "Not Recommended"
                badge_color = "#ef4444"
                reasoning = f"Low composite score ({css*100:.0f}%). Significant deficits in technical interview marks and required CV skills."
            
            out.append({
                "rank": r["rank"],
                "candidate_id": r["candidate_id"],
                "candidate_name": r["candidate_name"],
                "CSS": css,
                "final_score": round(css * 100, 2),
                "blended_score": round(css * 100, 2),
                "S_cv": s_cv,
                "cv_score": round(s_cv * 100, 2),
                "S_int": s_int,
                "interview_score": round(s_int * 100, 2),
                "S_edu": s_edu,
                "education_score": round(s_edu * 100, 2),
                "S_exp": s_exp,
                "experience_score": round(s_exp * 100, 2),
                "S_skill": s_skill,
                "skill_score": round(s_skill * 100, 2),
                "P_mcq": p_mcq,
                "mcq_score": round(p_mcq * 100, 2),
                "P_desc": p_desc,
                "descriptive_score": round(p_desc * 100, 2),
                "P_code": p_code,
                "coding_score": round(p_code * 100, 2),
                "ltr_score": r.get("ltr_score"),
                "passed_hard_filter": r["passed_hard_filter"],
                "filter_fail_reason": r.get("filter_fail_reason", ""),
                "verdict": verdict,
                "badge_color": badge_color,
                "reasoning": reasoning,
                "strengths": strengths if strengths else ["Basic profile compatibility"],
                "weaknesses": weaknesses if weaknesses else ["No critical deficits detected"],
            })
        
        res_data = {"success": True, "job_id": job_id, "job_role": job_role, "data": out}
        _PIPELINE_CACHE[job_id] = (time.time(), res_data)
        return res_data
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("rank_pipeline fatal error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
