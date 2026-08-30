import re
import time
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status
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
    """Derive the canonical interview role from a free-text job title."""
    t = re.sub(r"[^a-z0-9 ]", " ", (title or "").lower())
    for word in _LEVEL_WORDS:
        t = t.replace(word, " ")
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        return ""
    twords = t.split()
    best_role, best_score = "", 0
    for role in _INTERVIEW_ROLES:
        rwords = role.lower().split()
        score = sum(1 for rw in rwords if any(tw.startswith(rw) or rw.startswith(tw) for tw in twords))
        if score > best_score:
            best_role, best_score = role, score
    return best_role if best_score else (title or "").strip()


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


@router.get("", response_model=list[JobOut])
@router.get("/", response_model=list[JobOut])
async def list_jobs(request: Request, company: dict = Depends(require_company), skip: int = 0, limit: int = 50):
    from bson import ObjectId
    cid = company["_id"]
    company_filters = [{"company_id": str(cid)}]
    if ObjectId.is_valid(cid):
        company_filters.append({"company_id": ObjectId(cid)})
    cursor = request.app.state.db.jobs.find({"$or": company_filters}).sort("created_at", -1).skip(skip).limit(min(limit, 100))
    return [_job_out(doc) async for doc in cursor]


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
    db = request.app.state.db
    company_oid = company["_id"]
    # Match both string and ObjectId forms of company_id
    job_docs = await db.jobs.find({"$or": [
        {"company_id": company_oid},
        {"company_id": str(company_oid)},
    ]}, {"_id": 1}).to_list(1000)
    job_ids = [doc["_id"] for doc in job_docs]
    if not job_ids:
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


@router.get("/{job_id}/applicants", response_model=list[ApplicationOut])
async def get_applicants(job_id: str, request: Request, company: dict = Depends(require_company)):
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

        async for p in db.predictions.find({"$or": r_filters}).sort("created_at", -1):
            cid = str(p.get("candidate_id", ""))
            if cid not in pred_map or str(p.get("job_id")) == str(job_id):
                pred_map[cid] = p

        async for s in db.interview_scores.find({"$or": r_filters}).sort("created_at", -1):
            cid = str(s.get("candidate_id", ""))
            if cid not in score_map or str(s.get("job_id")) == str(job_id):
                score_map[cid] = s

        async for res in db.results.find({"$or": r_filters}).sort("created_at", -1):
            cid = str(res.get("candidate_id", ""))
            if cid not in score_map or str(res.get("job_id")) == str(job_id):
                score_map[cid] = res

    enriched = []
    for doc in applicants:
        cid = str(doc.get("candidate_id", ""))
        u = user_map.get(cid, {})
        r = resume_map.get(cid, {})
        p = pred_map.get(cid, {})
        s = score_map.get(cid, {})

        c_name = doc.get("candidate_name") or u.get("full_name") or r.get("candidate_name") or u.get("email") or "Candidate"
        c_email = doc.get("candidate_email") or u.get("email") or r.get("email") or ""
        int_score = doc.get("interview_score") or s.get("interview_score")
        cv_score = doc.get("cv_score") or p.get("overall_score") or doc.get("overall_score")
        skills = r.get("skills", [])

        hire_prob = None
        if int_score is not None and cv_score is not None:
            hire_prob = round(0.55 * float(int_score) + 0.45 * float(cv_score), 1)
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
            "overall_score": cv_score,
            "hire_probability": hire_prob,
            "skills": skills,
        })

    return [_app_out(doc) for doc in enriched]
