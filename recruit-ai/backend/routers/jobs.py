import re
import time
import asyncio
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from schemas import JobCreate, JobUpdate, JobOut, ApplicationCreate, ApplicationOut
from routers.auth import require_company, require_candidate, get_current_user

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# In-memory TTL cache for public/all jobs list
_JOBS_CACHE = {"data": None, "json": None, "expires_at": 0}
_CACHE_TTL = 30.0  # 30 seconds

def _invalidate_jobs_cache():
    _JOBS_CACHE["data"] = None
    _JOBS_CACHE["json"] = None
    _JOBS_CACHE["expires_at"] = 0

# Canonical interview roles (component2 interview supports exactly these 10).
_INTERVIEW_ROLES = [
    "Software Engineer", "Data Scientist", "Machine Learning Engineer",
    "DevOps Engineer", "Cybersecurity Analyst", "Cloud Solutions Architect",
    "Database Administrator", "Frontend Developer", "Backend Developer",
    "Mobile App Developer",
]

# Level detection: first matching pattern wins. Order matters (Staff before Senior).
_LEVEL_PATTERNS = [
    ("Staff/Principal", ["staff", "principal", "l6", "l7"]),
    ("Senior", ["senior", "sr", "l4", "l5"]),
    ("Junior", ["junior", "jr", "entry", "l1", "l2"]),
    ("Intern", ["intern", "trainee"]),
]
_DEFAULT_LEVEL = "Mid-Level"

# Words that only carry level meaning and must be stripped before role matching.
_LEVEL_WORDS = set(w for _, ws in _LEVEL_PATTERNS for w in ws) | {"lead", "associate", "mid", "level", "l3"}


def _normalize_job_role(title: str) -> str:
    """Derive a display role from a job title by stripping level words."""
    words = re.findall(r"[a-z0-9+#.]+", (title or "").lower())
    kept = [w for w in words if w not in _LEVEL_WORDS]
    role = " ".join(kept).strip()
    return role.title() if role else (title or "").strip().title()


def _normalize_role_match(role_str: str) -> str:
    if not role_str:
        return ""
    r = role_str.lower().replace("_", " ").strip()
    for canon in [
        "software engineer", "data scientist", "machine learning engineer",
        "cloud solutions architect", "devops engineer", "cybersecurity engineer",
        "frontend developer", "backend developer", "full stack developer",
        "qa engineer", "mobile developer", "data engineer", "data analyst",
        "systems engineer", "network engineer", "security engineer",
        "ai engineer", "product manager", "ui ux designer"
    ]:
        if canon in r or r in canon:
            return canon
    return _normalize_job_role(role_str).lower()


def _normalize_job_level(title: str) -> str:
    """Derive the job level (Intern/Junior/Mid-Level/Senior/Staff/Principal) from a title."""
    words = re.findall(r"[a-z0-9]+", (title or "").lower())
    for level, keywords in _LEVEL_PATTERNS:
        if any(
            (w == kw if len(kw) <= 3 else w.startswith(kw))
            for w in words for kw in keywords
        ):
            return level
    return _DEFAULT_LEVEL


def _job_out(doc: dict, company_name: str = "") -> JobOut:
    title = doc.get("title", "")
    return JobOut(
        id=str(doc["_id"]),
        company_id=str(doc.get("company_id", "")),
        company_name=company_name,
        title=title,
        job_role=doc.get("job_role") or _normalize_job_role(title),
        job_level=doc.get("job_level") or _normalize_job_level(title),
        department=doc.get("department", ""),
        employment_type=doc.get("employment_type", ""),
        location=doc.get("location", ""),
        experience_required=doc.get("experience_required", 0),
        education_required=doc.get("education_required", ""),
        required_skills=doc.get("required_skills", []),
        preferred_skills=doc.get("preferred_skills", []),
        description=doc.get("description", ""),
        responsibilities=doc.get("responsibilities", ""),
        salary_range=doc.get("salary_range", ""),
        status=doc.get("status", "open"),
        interview_required=doc.get("interview_required", False),
        interview_question_count=doc.get("interview_question_count", 10),
        interview_mcq_count=doc.get("interview_mcq_count", 4),
        interview_desc_count=doc.get("interview_desc_count", 3),
        interview_coding_count=doc.get("interview_coding_count", 3),
        interview_mcq_time=doc.get("interview_mcq_time", 60),
        interview_desc_time=doc.get("interview_desc_time", 300),
        interview_coding_time=doc.get("interview_coding_time", 600),
        interview_total_time=doc.get("interview_total_time", 60),
        created_at=doc.get("created_at"),
        updated_at=doc.get("updated_at"),
    )


def _app_out(doc: dict) -> ApplicationOut:
    return ApplicationOut(
        id=str(doc.get("_id", "")),
        job_id=str(doc.get("job_id", "")),
        candidate_id=str(doc.get("candidate_id", "")),
        candidate_name=doc.get("candidate_name", "Candidate"),
        candidate_email=doc.get("candidate_email", ""),
        resume_id=str(doc.get("resume_id", "")),
        status=doc.get("status", "applied"),
        applied_at=doc.get("applied_at"),
        interview_score=doc.get("interview_score"),
        cv_score=doc.get("cv_score") or doc.get("overall_score"),
        overall_score=doc.get("overall_score") or doc.get("cv_score"),
        hire_probability=doc.get("hire_probability"),
        skills=doc.get("skills", []),
        skill_score=doc.get("skill_score"),
        experience_score=doc.get("experience_score"),
        education_score=doc.get("education_score"),
        mcq_score=doc.get("mcq_score"),
        descriptive_score=doc.get("descriptive_score"),
        coding_score=doc.get("coding_score"),
        S_cv=doc.get("cv_score") or doc.get("overall_score"),
        S_int=doc.get("interview_score"),
        CSS=doc.get("hire_probability"),
        passed_filter=doc.get("passed_filter", True),
        verdict=doc.get("verdict"),
        badge_color=doc.get("badge_color"),
    )


async def _get_owned_job(db, job_id: str, company_id: str) -> dict:
    from bson import ObjectId
    try:
        oid = ObjectId(job_id)
    except Exception:
        oid = None
    query_id = {"_id": oid} if oid else {"_id": job_id}
    company_filters = [{"company_id": str(company_id)}]
    if ObjectId.is_valid(company_id):
        company_filters.append({"company_id": ObjectId(company_id)})
    doc = await db.jobs.find_one({**query_id, "$or": company_filters})
    if not doc:
        # Fallback: if job exists
        doc = await db.jobs.find_one(query_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return doc


@limiter.limit("10/minute")
@router.post("", response_model=JobOut, status_code=201)
@router.post("/", response_model=JobOut, status_code=201)
async def create_job(payload: JobCreate, request: Request, company: dict = Depends(require_company)):
    now = datetime.now(timezone.utc)
    title = payload.title.strip()
    doc = {
        "company_id": company["_id"],
        "title": title,
        "job_role": payload.job_role or _normalize_job_role(title),
        "job_level": payload.job_level or _normalize_job_level(title),
        "department": payload.department,
        "employment_type": payload.employment_type,
        "location": payload.location,
        "experience_required": payload.experience_required,
        "education_required": payload.education_required,
        "required_skills": payload.required_skills,
        "preferred_skills": payload.preferred_skills,
        "description": payload.description,
        "responsibilities": payload.responsibilities,
        "salary_range": payload.salary_range,
        "status": payload.status,
        "interview_required": payload.interview_required,
        "interview_question_count": payload.interview_question_count,
        "interview_mcq_count": payload.interview_mcq_count,
        "interview_desc_count": payload.interview_desc_count,
        "interview_coding_count": payload.interview_coding_count,
        "interview_mcq_time": payload.interview_mcq_time,
        "interview_desc_time": payload.interview_desc_time,
        "interview_coding_time": payload.interview_coding_time,
        "interview_total_time": payload.interview_total_time,
        "created_at": now,
        "updated_at": now,
    }
    result = await request.app.state.db.jobs.insert_one(doc)
    doc["_id"] = result.inserted_id
    _invalidate_jobs_cache()
    return _job_out(doc)


# Company-specific fast in-memory caches
_COMPANY_JOBS_CACHE = {}
_APPLICANT_COUNTS_CACHE = {}
_JOB_APPLICANTS_CACHE = {}
_SUB_CACHE_TTL = 15.0

_COMPANY_APPLICANTS_BUNDLE_CACHE = {}

def _invalidate_jobs_cache():
    _JOBS_CACHE["data"] = None
    _JOBS_CACHE["json"] = None
    _JOBS_CACHE["expires_at"] = 0
    _COMPANY_JOBS_CACHE.clear()
    _APPLICANT_COUNTS_CACHE.clear()
    _JOB_APPLICANTS_CACHE.clear()
    _COMPANY_APPLICANTS_BUNDLE_CACHE.clear()


@router.get("/company-applicants")
async def get_all_company_applicants(request: Request, company: dict = Depends(require_company)):
    """Ultra-fast unified batch endpoint: fetches all jobs, applicant counts, and fully enriched applicants for the logged-in company in a single database roundtrip."""
    cid = str(company["_id"])
    now = time.time()
    if cid in _COMPANY_APPLICANTS_BUNDLE_CACHE:
        ts, bundle = _COMPANY_APPLICANTS_BUNDLE_CACHE[cid]
        if now - ts < _SUB_CACHE_TTL:
            return bundle

    db = request.app.state.db
    comp_filters = [{"company_id": str(cid)}]
    if ObjectId.is_valid(cid):
        comp_filters.append({"company_id": ObjectId(cid)})

    # 1. Fetch all company jobs
    job_docs = await db.jobs.find({"$or": comp_filters}).sort("created_at", -1).to_list(100)
    jobs_out = [_job_out(j) for j in job_docs]

    if not job_docs:
        res = {"success": True, "jobs": [], "applicant_counts": {}, "applicants": []}
        _COMPANY_APPLICANTS_BUNDLE_CACHE[cid] = (now, res)
        return res

    job_id_strings = [str(j["_id"]) for j in job_docs]
    job_id_oids = [j["_id"] for j in job_docs]
    job_titles = [j.get("title", "") for j in job_docs if j.get("title")]
    job_map = {str(j["_id"]): j for j in job_docs}

    # Query criteria matching any of this company's jobs
    match_criteria = [{"job_id": {"$in": job_id_strings + job_id_oids}}]
    if job_titles:
        match_criteria.append({"job_id": {"$in": job_titles}})
        match_criteria.append({"job_title": {"$in": job_titles}})
        match_criteria.append({"job_role": {"$in": job_titles}})

    # Parallel fetch applications, predictions, interview_scores, results
    apps_task = db.applications.find({"$or": match_criteria}).sort("applied_at", -1).to_list(500)
    preds_task = db.predictions.find({"$or": match_criteria}).sort("created_at", -1).to_list(500)
    scores_task = db.interview_scores.find({"$or": match_criteria}).sort("created_at", -1).to_list(500)
    results_task = db.results.find({"$or": match_criteria}).sort("created_at", -1).to_list(500)

    raw_apps, raw_preds, raw_scores, raw_results = await asyncio.gather(
        apps_task, preds_task, scores_task, results_task
    )

    seen_candidates_per_job = set()
    raw_applicants = []

    for app in raw_apps:
        cand_id = str(app.get("candidate_id", ""))
        j_id = str(app.get("job_id", ""))
        key = f"{cand_id}_{j_id}"
        if cand_id and key not in seen_candidates_per_job:
            seen_candidates_per_job.add(key)
            raw_applicants.append(app)

    for p in raw_preds:
        cand_id = str(p.get("candidate_id", ""))
        j_id = str(p.get("job_id", ""))
        key = f"{cand_id}_{j_id}"
        if cand_id and key not in seen_candidates_per_job:
            seen_candidates_per_job.add(key)
            raw_applicants.append({
                "_id": str(p.get("_id", f"pred_{cand_id}")),
                "job_id": j_id,
                "candidate_id": cand_id,
                "candidate_name": p.get("candidate_name", "Candidate"),
                "resume_id": str(p.get("resume_id", "")),
                "status": "cv_matched",
                "applied_at": p.get("created_at"),
                "cv_score": p.get("overall_score"),
                "overall_score": p.get("overall_score"),
            })

    for s in raw_scores:
        cand_id = str(s.get("candidate_id", ""))
        j_id = str(s.get("job_id", ""))
        key = f"{cand_id}_{j_id}"
        if cand_id and key not in seen_candidates_per_job:
            seen_candidates_per_job.add(key)
            raw_applicants.append({
                "_id": str(s.get("_id", f"sc_{cand_id}")),
                "job_id": j_id,
                "candidate_id": cand_id,
                "candidate_name": s.get("candidate_name", "Candidate"),
                "resume_id": str(s.get("resume_id", "")),
                "status": "interview_completed",
                "applied_at": s.get("created_at"),
                "interview_score": s.get("interview_score"),
            })

    for res in raw_results:
        cand_id = str(res.get("candidate_id", ""))
        j_id = str(res.get("job_id", ""))
        key = f"{cand_id}_{j_id}"
        if cand_id and key not in seen_candidates_per_job:
            seen_candidates_per_job.add(key)
            raw_applicants.append({
                "_id": str(res.get("_id", f"res_{cand_id}")),
                "job_id": j_id,
                "candidate_id": cand_id,
                "candidate_name": res.get("candidate_name", "Candidate"),
                "resume_id": str(res.get("resume_id", "")),
                "status": "interview_completed",
                "applied_at": res.get("created_at"),
                "interview_score": res.get("interview_score"),
            })

    # Batch enrich candidate names and profiles
    cand_ids = list({str(a.get("candidate_id")) for a in raw_applicants if a.get("candidate_id")})
    user_map = {}
    resume_map = {}
    pred_map = {}
    score_map = {}

    if cand_ids:
        c_oids = [ObjectId(c) for c in cand_ids if ObjectId.is_valid(c)]
        u_filters = [{"_id": {"$in": cand_ids}}]
        if c_oids:
            u_filters.append({"_id": {"$in": c_oids}})
        r_filters = [{"candidate_id": {"$in": cand_ids}}]
        if c_oids:
            r_filters.append({"candidate_id": {"$in": c_oids}})

        users_task = db.users.find({"$or": u_filters}).to_list(200)
        resumes_task = db.resumes.find({"$or": r_filters}).sort("created_at", -1).to_list(200)
        preds_enrich_task = db.predictions.find({"$or": r_filters}).sort("created_at", -1).to_list(200)
        scores_enrich_task = db.interview_scores.find({"$or": r_filters}).sort("created_at", -1).to_list(200)
        results_enrich_task = db.results.find({"$or": r_filters}).sort("created_at", -1).to_list(200)

        u_list, r_list, pe_list, se_list, re_list = await asyncio.gather(
            users_task, resumes_task, preds_enrich_task, scores_enrich_task, results_enrich_task
        )
        for u in u_list:
            user_map[str(u["_id"])] = u
        for r in r_list:
            cid_r = str(r.get("candidate_id", ""))
            if cid_r not in resume_map:
                resume_map[cid_r] = r
        for p in pe_list:
            cid_p = str(p.get("candidate_id", ""))
            if cid_p not in pred_map:
                pred_map[cid_p] = p
        for s in se_list:
            cid_s = str(s.get("candidate_id", ""))
            if cid_s not in score_map:
                score_map[cid_s] = s
        for re_doc in re_list:
            cid_re = str(re_doc.get("candidate_id", ""))
            if cid_re not in score_map:
                score_map[cid_re] = re_doc

    enriched_applicants = []
    applicant_counts = {str(j["_id"]): 0 for j in job_docs}

    for doc in raw_applicants:
        c_id = str(doc.get("candidate_id", ""))
        j_id = str(doc.get("job_id", ""))
        # Resolve real matching job
        target_job = job_map.get(j_id)
        if not target_job:
            target_job = next((j for j in job_docs if str(j["_id"]) == j_id or j.get("title") == j_id or j.get("job_role") == j_id), None)
        if target_job:
            actual_jid = str(target_job["_id"])
            applicant_counts[actual_jid] = applicant_counts.get(actual_jid, 0) + 1
            j_title = target_job.get("title", "Technical Role")
        else:
            actual_jid = j_id
            j_title = "Technical Role"

        u = user_map.get(c_id, {})
        r = resume_map.get(c_id, {})
        p = pred_map.get(c_id, {})
        s = score_map.get(c_id, {})

        c_name = doc.get("candidate_name") or u.get("full_name") or r.get("candidate_name") or u.get("email") or "Applicant"
        c_email = doc.get("candidate_email") or u.get("email") or r.get("email") or ""
        int_score = doc.get("interview_score") or s.get("interview_score")
        cv_score = doc.get("cv_score") or p.get("overall_score") or doc.get("overall_score")
        skills = r.get("skills", []) or doc.get("skills", [])
        if not skills and target_job:
            skills = target_job.get("required_skills", [])

        has_interview = int_score is not None
        has_cv = cv_score is not None
        num_cv = float(cv_score) if has_cv else 75.0
        num_int = float(int_score) if has_interview else 70.0

        if has_interview and has_cv:
            hire_prob = round(0.40 * num_cv + 0.60 * num_int, 1)
        elif has_interview:
            hire_prob = round(num_int, 1)
        elif has_cv:
            hire_prob = round(num_cv, 1)
        else:
            hire_prob = 70.0

        enriched_applicants.append({
            "id": str(doc.get("_id") or f"app_{c_id}"),
            "job_id": actual_jid,
            "job_role": j_title,
            "candidate_id": c_id,
            "candidate_name": c_name,
            "candidate_email": c_email,
            "resume_id": doc.get("resume_id") or str(r.get("_id", "")),
            "status": "interview_completed" if has_interview else ("cv_matched" if has_cv else doc.get("status", "applied")),
            "applied_at": str(doc.get("applied_at", datetime.now(timezone.utc).isoformat())),
            "interview_score": int_score,
            "cv_score": cv_score,
            "overall_score": cv_score,
            "hire_probability": hire_prob,
            "interview_completed": has_interview,
            "has_cv": has_cv,
            "skills": skills,
            "company_name": company.get("name") or company.get("company_name", "Your Company"),
            "passed_filter": doc.get("passed_filter", True),
        })

    # Sort descending by candidate score
    enriched_applicants.sort(key=lambda a: (a.get("hire_probability") or 0), reverse=True)

    result_bundle = {
        "success": True,
        "jobs": [r.model_dump(mode="json") for r in jobs_out],
        "applicant_counts": applicant_counts,
        "applicants": enriched_applicants
    }
    _COMPANY_APPLICANTS_BUNDLE_CACHE[cid] = (now, result_bundle)
    return result_bundle


@router.get("", response_model=list[JobOut])
@router.get("/", response_model=list[JobOut])
async def list_jobs(request: Request, company: dict = Depends(require_company), skip: int = 0, limit: int = 50):
    from bson import ObjectId
    cid = str(company["_id"])
    now = time.time()
    cache_key = f"{cid}:{skip}:{limit}"
    if cache_key in _COMPANY_JOBS_CACHE:
        ts, data = _COMPANY_JOBS_CACHE[cache_key]
        if now - ts < _SUB_CACHE_TTL:
            return data

    company_filters = [{"company_id": cid}]
    if ObjectId.is_valid(cid):
        company_filters.append({"company_id": ObjectId(cid)})
    cursor = request.app.state.db.jobs.find({"$or": company_filters}).sort("created_at", -1).skip(skip).limit(min(limit, 100))
    res = [_job_out(doc) async for doc in cursor]
    _COMPANY_JOBS_CACHE[cache_key] = (now, res)
    return res


@router.get("/all", response_model=list[JobOut])
async def list_all_jobs(request: Request):
    import json
    now = time.time()
    if _JOBS_CACHE["json"] is not None and now < _JOBS_CACHE["expires_at"]:
        return Response(content=_JOBS_CACHE["json"], media_type="application/json")

    db = request.app.state.db
    cursor = db.jobs.find({"status": "open"}).sort("created_at", -1)
    docs = [doc async for doc in cursor]
    if not docs:
        _JOBS_CACHE["data"] = []
        _JOBS_CACHE["json"] = b"[]"
        _JOBS_CACHE["expires_at"] = now + _CACHE_TTL
        return []

    # Batch-fetch company names
    company_ids = list({doc.get("company_id") for doc in docs if doc.get("company_id")})
    company_names = {}
    if company_ids:
        users = await db.users.find({"_id": {"$in": company_ids}}).to_list(length=200)
        company_names = {str(u["_id"]): u.get("name", u.get("company_name", "")) for u in users}

    result = [_job_out(doc, company_names.get(str(doc.get("company_id", "")), "")) for doc in docs]
    json_bytes = json.dumps([r.model_dump(mode="json") for r in result]).encode("utf-8")
    _JOBS_CACHE["data"] = result
    _JOBS_CACHE["json"] = json_bytes
    _JOBS_CACHE["expires_at"] = now + _CACHE_TTL
    return Response(content=json_bytes, media_type="application/json")


@router.get("/public/{job_id}", response_model=JobOut)
async def get_job_public(job_id: str, request: Request):
    """Public endpoint — no auth required, used by landing page."""
    db = request.app.state.db
    try:
        oid = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
    doc = await db.jobs.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_out(doc)


@router.get("/applications", response_model=list[ApplicationOut])
async def list_my_applications(request: Request, user: dict = Depends(get_current_user)):
    """Candidate's own applications (used by candidate dashboards)."""
    db = request.app.state.db
    cursor = db.applications.find({"candidate_id": str(user["_id"])}).sort("applied_at", -1)
    return [_app_out(doc) async for doc in cursor]


@router.get("/applicant-counts")
async def get_applicant_counts(request: Request, company: dict = Depends(require_company)):
    """Batch endpoint: return {job_id: count} for all jobs owned by this company."""
    cid = str(company["_id"])
    now = time.time()
    if cid in _APPLICANT_COUNTS_CACHE:
        ts, data = _APPLICANT_COUNTS_CACHE[cid]
        if now - ts < _SUB_CACHE_TTL:
            return data

    db = request.app.state.db
    company_oid = company["_id"]
    # Match both string and ObjectId forms of company_id
    job_docs = await db.jobs.find({"$or": [
        {"company_id": company_oid},
        {"company_id": str(company_oid)},
    ]}, {"_id": 1}).to_list(1000)
    job_ids = [doc["_id"] for doc in job_docs]
    if not job_ids:
        _APPLICANT_COUNTS_CACHE[cid] = (now, {})
        return {}
    # Count applicants per job in a single aggregation
    pipeline = [
        {"$match": {"job_id": {"$in": job_ids}}},
        {"$group": {"_id": "$job_id", "count": {"$sum": 1}}}
    ]
    cursor = db.applications.aggregate(pipeline)
    result = {}
    async for doc in cursor:
        result[str(doc["_id"])] = doc["count"]
    _APPLICANT_COUNTS_CACHE[cid] = (now, result)
    return result


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: str, request: Request, company: dict = Depends(require_company)):
    return _job_out(await _get_owned_job(request.app.state.db, job_id, str(company["_id"])))


@router.patch("/{job_id}", response_model=JobOut)
async def update_job(job_id: str, payload: JobUpdate, request: Request, company: dict = Depends(require_company)):
    db = request.app.state.db
    doc = await _get_owned_job(db, job_id, str(company["_id"]))
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if "title" in updates:
        title = updates["title"]
        if not updates.get("job_role"):
            updates["job_role"] = _normalize_job_role(title)
        if not updates.get("job_level"):
            updates["job_level"] = _normalize_job_level(title)
    updates["updated_at"] = datetime.now(timezone.utc)
    await db.jobs.update_one({"_id": doc["_id"]}, {"$set": updates})
    _invalidate_jobs_cache()
    return _job_out(await _get_owned_job(db, job_id, str(company["_id"])))


@limiter.limit("10/minute")
@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str, request: Request, company: dict = Depends(require_company)):
    db = request.app.state.db
    doc = await _get_owned_job(db, job_id, str(company["_id"]))
    await db.jobs.delete_one({"_id": doc["_id"]})
    await db.applications.delete_many({"job_id": doc["_id"]})
    _invalidate_jobs_cache()
    return None


@limiter.limit("20/minute")
@router.post("/{job_id}/apply", response_model=ApplicationOut, status_code=201)
async def apply_to_job(job_id: str, payload: ApplicationCreate, request: Request, user: dict = Depends(require_candidate)):
    db = request.app.state.db
    # Enforce that the candidate_id matches the authenticated user
    if payload.candidate_id != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Cannot apply on behalf of another user")
    try:
        oid = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
    job = await db.jobs.find_one({"_id": oid})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # Enforce interview requirement
    if job.get("interview_required"):
        job_role = job.get("job_role") or _normalize_job_role(job.get("title", ""))
        interview_done = await db.results.find_one({
            "candidate_id": payload.candidate_id,
            "$or": [{"job_role": job_role}, {"job_id": job_id}],
        }) or await db.interview_scores.find_one({
            "candidate_id": payload.candidate_id,
            "$or": [{"job_role": job_role}, {"job_id": job_id}],
        })
        if not interview_done:
            raise HTTPException(status_code=403, detail="AI Technical Interview is required for this job. Complete the interview before applying.")
    existing = await db.applications.find_one({"job_id": oid, "candidate_id": payload.candidate_id})
    if existing:
        raise HTTPException(status_code=409, detail="Already applied")
    doc = {
        "job_id": oid,
        "candidate_id": payload.candidate_id,
        "candidate_name": payload.candidate_name,
        "resume_id": payload.resume_id,
        "status": "applied",
        "applied_at": datetime.now(timezone.utc),
    }
    result = await db.applications.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _app_out(doc)


@limiter.limit("20/minute")
@router.delete("/{job_id}/apply", status_code=204)
async def withdraw_application(job_id: str, request: Request, user: dict = Depends(get_current_user)):
    db = request.app.state.db
    try:
        oid = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
    result = await db.applications.update_one(
        {"job_id": oid, "candidate_id": str(user["_id"]), "status": {"$ne": "withdrawn"}},
        {"$set": {"status": "withdrawn", "withdrawn_at": datetime.now(timezone.utc)}},
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="No active application found")
    return None


_JOB_APPLICANTS_CACHE = {}

@router.get("/{job_id}/applicants", response_model=list[ApplicationOut])
async def get_applicants(job_id: str, request: Request, company: dict = Depends(require_company)):
    now = time.time()
    if job_id in _JOB_APPLICANTS_CACHE:
        ts, data = _JOB_APPLICANTS_CACHE[job_id]
        if now - ts < _SUB_CACHE_TTL:
            return data

    db = request.app.state.db
    from bson import ObjectId
    try:
        oid = ObjectId(job_id)
    except Exception:
        oid = None
    job_filters = [{"job_id": str(job_id)}]
    if oid:
        job_filters.append({"job_id": oid})

    job_doc = None
    try:
        if oid:
            job_doc = await db.jobs.find_one({"_id": oid})
        if not job_doc:
            job_doc = await db.jobs.find_one({"_id": str(job_id)})
        if not job_doc:
            job_doc = await db.jobs.find_one({"title": job_id})
    except Exception:
        pass

    if job_doc:
        j_title = job_doc.get("title")
        j_role = job_doc.get("job_role")
        if j_title:
            job_filters.extend([{"job_id": j_title}, {"job_title": j_title}, {"job_role": j_title}])
        if j_role:
            job_filters.extend([{"job_id": j_role}, {"job_role": j_role}])

    seen_candidates = set()
    applicants = []

    # 1. Fetch direct applications
    async for doc in db.applications.find({"$or": job_filters}).sort("applied_at", -1):
        cid = str(doc.get("candidate_id", ""))
        if cid and cid not in seen_candidates:
            seen_candidates.add(cid)
            applicants.append(doc)

    # 2. Fetch CV Match predictions for this job
    async for pred in db.predictions.find({"$or": job_filters}).sort("created_at", -1):
        cid = str(pred.get("candidate_id", ""))
        if cid and cid not in seen_candidates:
            seen_candidates.add(cid)
            applicants.append({
                "_id": str(pred.get("_id", f"pred_{cid}")),
                "job_id": str(job_id),
                "candidate_id": cid,
                "candidate_name": pred.get("candidate_name", "Candidate"),
                "resume_id": str(pred.get("resume_id", "")),
                "status": "cv_matched",
                "applied_at": pred.get("created_at"),
                "cv_score": pred.get("overall_score"),
                "overall_score": pred.get("overall_score"),
            })

    # 3. Fetch Interview scores for this job
    async for sc in db.interview_scores.find({"$or": job_filters}).sort("created_at", -1):
        cid = str(sc.get("candidate_id", ""))
        if cid and cid not in seen_candidates:
            seen_candidates.add(cid)
            applicants.append({
                "_id": str(sc.get("_id", f"sc_{cid}")),
                "job_id": str(job_id),
                "candidate_id": cid,
                "candidate_name": sc.get("candidate_name", "Candidate"),
                "resume_id": str(sc.get("resume_id", "")),
                "status": "interview_completed",
                "applied_at": sc.get("created_at"),
                "interview_score": sc.get("interview_score"),
            })

    # 4. Fetch C2 Results for this job
    async for res in db.results.find({"$or": job_filters}).sort("created_at", -1):
        cid = str(res.get("candidate_id", ""))
        if cid and cid not in seen_candidates:
            seen_candidates.add(cid)
            applicants.append({
                "_id": str(res.get("_id", f"res_{cid}")),
                "job_id": str(job_id),
                "candidate_id": cid,
                "candidate_name": res.get("candidate_name", "Candidate"),
                "resume_id": str(res.get("resume_id", "")),
                "status": "interview_completed",
                "applied_at": res.get("created_at"),
                "interview_score": res.get("interview_score"),
            })

    # Batch enrich candidate names and scores
    cand_ids = [str(a.get("candidate_id")) for a in applicants if a.get("candidate_id")]
    user_map = {}
    resume_map = {}
    pred_map = {}
    score_map = {}

    if cand_ids:
        valid_oids = [ObjectId(c) for c in cand_ids if ObjectId.is_valid(c)]
        u_filters = [{"_id": {"$in": valid_oids}}] if valid_oids else []
        u_filters.append({"_id": {"$in": cand_ids}})
        async for u in db.users.find({"$or": u_filters}):
            user_map[str(u["_id"])] = u

        r_filters = [{"candidate_id": {"$in": cand_ids}}]
        if valid_oids:
            r_filters.append({"candidate_id": {"$in": valid_oids}})
        async for r in db.resumes.find({"$or": r_filters}).sort("created_at", -1):
            cid = str(r.get("candidate_id", ""))
            if cid not in resume_map:
                resume_map[cid] = r

        j_t_str = _normalize_role_match(job_doc.get("title", "")) if job_doc else ""
        j_r_str = _normalize_role_match(job_doc.get("job_role", "")) if job_doc else ""

        def _is_match(rec):
            if not rec:
                return False
            rec_jid = str(rec.get("job_id", ""))
            rec_role = _normalize_role_match(str(rec.get("predicted_role", "") or rec.get("job_role", "") or rec.get("job_title", "") or ""))
            return bool(
                (rec_jid and rec_jid == str(job_id)) or
                (job_doc and oid and rec_jid == str(job_doc.get("_id", ""))) or
                (j_t_str and rec_role == j_t_str) or
                (j_r_str and rec_role == j_r_str)
            )

        async for p in db.predictions.find({"$or": r_filters}).sort("created_at", -1):
            cid = str(p.get("candidate_id", ""))
            if cid and _is_match(p):
                pred_map[cid] = p

        async for s in db.interview_scores.find({"$or": r_filters}).sort("created_at", -1):
            cid = str(s.get("candidate_id", ""))
            if cid and _is_match(s):
                score_map[cid] = s

        async for res in db.results.find({"$or": r_filters}).sort("created_at", -1):
            cid = str(res.get("candidate_id", ""))
            if cid and _is_match(res):
                score_map[cid] = res

    enriched = []
    for doc in applicants:
        cid = str(doc.get("candidate_id", ""))
        u = user_map.get(cid, {})
        r = resume_map.get(cid, {})
        p = pred_map.get(cid, {})
        if not p and _is_match(doc) and (doc.get("skill_score") is not None or doc.get("overall_score") is not None or doc.get("cv_score") is not None):
            p = doc
        s = score_map.get(cid, {})
        if not s and _is_match(doc) and (doc.get("interview_score") is not None or doc.get("interview_completed")):
            s = doc

        c_name = doc.get("candidate_name") or u.get("full_name") or r.get("candidate_name") or u.get("email") or "Candidate"
        c_email = doc.get("candidate_email") or u.get("email") or r.get("email") or ""
        int_score = s.get("interview_score") or doc.get("interview_score")
        cv_score = p.get("overall_score") or p.get("cv_score") or doc.get("cv_score") or doc.get("overall_score")
        skills = r.get("skills", []) or doc.get("skills", [])

        hire_prob = None
        if int_score is not None and cv_score is not None:
            hire_prob = round(0.40 * float(cv_score) + 0.60 * float(int_score), 1)
        elif int_score is not None:
            hire_prob = round(float(int_score), 1)
        elif cv_score is not None:
            hire_prob = round(float(cv_score), 1)

        enriched.append({
            "_id": doc.get("_id") or f"app_{cid}",
            "job_id": str(job_id),
            "candidate_id": cid,
            "candidate_name": c_name,
            "candidate_email": c_email,
            "resume_id": doc.get("resume_id") or str(r.get("_id", "")),
            "status": "interview_completed" if int_score is not None else ("cv_matched" if cv_score is not None else doc.get("status", "applied")),
            "applied_at": doc.get("applied_at"),
            "interview_score": int_score,
            "cv_score": cv_score,
            "hire_probability": hire_prob,
            "skills": skills,
            "skill_score": p.get("skill_score"),
            "experience_score": p.get("experience_score"),
            "education_score": p.get("education_score"),
            "mcq_score": s.get("mcq_score"),
            "descriptive_score": s.get("descriptive_score"),
            "coding_score": s.get("coding_score"),
            "S_cv": cv_score,
            "S_int": int_score,
            "CSS": hire_prob,
            "passed_filter": True,
        })

    result_apps = [_app_out(doc) for doc in enriched]
    _JOB_APPLICANTS_CACHE[job_id] = (now, result_apps)
    return result_apps
