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


@router.get("/rank/pipeline/{job_id}", summary="Rank real applicants for a job")
@router.post("/rank/pipeline/{job_id}", summary="Rank real applicants for a job")
async def rank_pipeline(request: Request, job_id: str):
    """Fetch real applicants from MongoDB, build candidate inputs, and rank them."""
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
        
        # 2. Fetch candidates for this job (Applications + CV Match + Interviewed)
        query_conditions = [{"job_id": job_id}, {"job_id": str(job_id)}]
        if ObjectId.is_valid(job_id):
            query_conditions.append({"job_id": ObjectId(job_id)})
            
        seen_candidates = set()
        applicants = []
        
        # A. Applications
        async for app in db.applications.find({"$or": query_conditions}):
            cid = str(app.get("candidate_id", ""))
            if cid and cid not in seen_candidates:
                seen_candidates.add(cid)
                applicants.append({
                    "candidate_id": cid,
                    "candidate_name": app.get("candidate_name", "Candidate"),
                    "resume_id": app.get("resume_id", ""),
                })

        # B. CV Match Predictions
        async for pred in db.predictions.find({"$or": query_conditions}):
            cid = str(pred.get("candidate_id", ""))
            if cid and cid not in seen_candidates:
                seen_candidates.add(cid)
                applicants.append({
                    "candidate_id": cid,
                    "candidate_name": pred.get("candidate_name", "Candidate"),
                    "resume_id": pred.get("resume_id", ""),
                })

        # C. Interview Scores
        async for sc in db.interview_scores.find({"$or": query_conditions}):
            cid = str(sc.get("candidate_id", ""))
            if cid and cid not in seen_candidates:
                seen_candidates.add(cid)
                applicants.append({
                    "candidate_id": cid,
                    "candidate_name": sc.get("candidate_name", "Candidate"),
                    "resume_id": sc.get("resume_id", ""),
                })

        # Fallback to all candidate resumes in the talent pool if no candidates interacted with this job yet
        if not applicants:
            resume_cursor = db.resumes.find().sort("created_at", -1)
            resumes_list = await resume_cursor.to_list(length=50)
            if not resumes_list:
                c1_cursor = db.cv_analyses.find().sort("analysis_timestamp", -1)
                resumes_list = await c1_cursor.to_list(length=50)
                
            applicants = [
                {
                    "candidate_id": str(r.get("candidate_id", r.get("_id", "unknown"))),
                    "candidate_name": r.get("candidate_name", r.get("filename", "Candidate")),
                    "resume_skills": r.get("skills", []),
                    "experience_years": r.get("experience_years", 2),
                    "education": r.get("education", "BSc IT"),
                }
                for r in resumes_list
            ]

        if not applicants:
            return {"success": True, "job_id": job_id, "data": [], "message": "No applicants or resumes found"}

        # 3. Batch-fetch resumes, predictions, and interview scores for all candidates
        candidate_ids = [app.get("candidate_id") or str(app.get("_id", "CAND")) for app in applicants]
        resume_map = {}
        async for r in db.resumes.find({"candidate_id": {"$in": candidate_ids}}):
            resume_map[r.get("candidate_id", "")] = r
        
        pred_map = {}
        async for p in db.predictions.find({"candidate_id": {"$in": candidate_ids}}).sort("created_at", -1):
            cid = p.get("candidate_id", "")
            if cid not in pred_map or p.get("job_id") == job_id:
                pred_map[cid] = p

        scores_map = {}
        async for s in db.interview_scores.find({"candidate_id": {"$in": candidate_ids}}).sort("created_at", -1):
            cid = s.get("candidate_id", "")
            if cid not in scores_map or s.get("job_id") == job_id:
                scores_map[cid] = s
        
        async for res in db.results.find({"candidate_id": {"$in": candidate_ids}}).sort("created_at", -1):
            cid = res.get("candidate_id", "")
            if cid not in scores_map or res.get("job_id") == job_id:
                scores_map[cid] = res

        # 4. Build candidate inputs
        candidates = []
        for app in applicants:
            candidate_id = app.get("candidate_id") or str(app.get("_id", "CAND"))
            candidate_name = app.get("candidate_name") or app.get("name") or "Candidate"
            
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

            # Default or fallback interview scores
            mcq_score = 0.8
            descriptive_score = 0.75
            coding_score = 0.85
            latest_score = scores_map.get(candidate_id)
            if latest_score:
                mcq_score = (latest_score.get("mcq_score", 80) or 80) / 100
                descriptive_score = (latest_score.get("descriptive_score", 75) or 75) / 100
                coding_score = (latest_score.get("coding_score", 85) or 85) / 100
            
            # Skill matching from predictions or bidirectional check
            pred_doc = pred_map.get(candidate_id)
            if pred_doc and pred_doc.get("skill_score") is not None:
                skill_score_raw = pred_doc.get("skill_score", 80) / 100
            else:
                matched = sum(1 for s in required_skills if any(s.lower() in rs.lower() or rs.lower() in s.lower() for rs in resume_skills)) if resume_skills else 0
                skill_score_raw = matched / max(len(required_skills), 1)
            
            if pred_doc and pred_doc.get("experience_score") is not None and not experience_years:
                exp_req = float((job.get("experience_required") or 2.0) if job else 2.0)
                experience_years = (pred_doc.get("experience_score", 60) / 100) * exp_req

            candidates.append(CandidateInput(
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                job_role=job_role,
                years_experience=float(experience_years or 2.0),
                edu_level=int(edu_level),
                skill_score_raw=float(skill_score_raw),
                P_mcq=float(mcq_score),
                P_desc=float(descriptive_score),
                P_code=float(coding_score),
                skills=resume_skills,
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
            css = round(r["CSS"], 4)
            s_cv = round(r["S_cv"], 4)
            s_int = round(r["S_int"], 4)
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
        
        return {"success": True, "job_id": job_id, "job_role": job_role, "data": out}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("rank_pipeline fatal error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
