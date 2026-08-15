"""Job posting routes for companies."""
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status

from schemas import JobCreate, JobUpdate, JobOut, ApplicationCreate, ApplicationOut
from routers.auth import require_company, require_candidate, get_current_user

router = APIRouter()


def _job_out(doc: dict, company_name: str = "") -> JobOut:
    return JobOut(
        id=str(doc["_id"]),
        company_id=str(doc.get("company_id", "")),
        company_name=company_name,
        title=doc.get("title", ""),
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
        created_at=doc.get("created_at"),
        updated_at=doc.get("updated_at"),
    )


def _app_out(doc: dict) -> ApplicationOut:
    return ApplicationOut(
        id=str(doc["_id"]),
        job_id=str(doc.get("job_id", "")),
        candidate_id=doc.get("candidate_id", ""),
        candidate_name=doc.get("candidate_name", ""),
        resume_id=doc.get("resume_id", ""),
        status=doc.get("status", "applied"),
        applied_at=doc.get("applied_at"),
    )


async def _get_owned_job(db, job_id: str, company_id: str) -> dict:
    try:
        oid = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
    doc = await db.jobs.find_one({"_id": oid, "company_id": ObjectId(company_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return doc


@router.post("", response_model=JobOut, status_code=201)
@router.post("/", response_model=JobOut, status_code=201)
async def create_job(payload: JobCreate, request: Request, company: dict = Depends(require_company)):
    now = datetime.now(timezone.utc)
    doc = {
        "company_id": company["_id"],
        "title": payload.title.strip(),
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
        "created_at": now,
        "updated_at": now,
    }
    result = await request.app.state.db.jobs.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _job_out(doc)


@router.get("", response_model=list[JobOut])
@router.get("/", response_model=list[JobOut])
async def list_jobs(request: Request, company: dict = Depends(require_company)):
    cursor = request.app.state.db.jobs.find({"company_id": company["_id"]}).sort("created_at", -1)
    return [_job_out(doc) async for doc in cursor]


@router.get("/all", response_model=list[JobOut])
async def list_all_jobs(request: Request):
    db = request.app.state.db
    cursor = db.jobs.find({"status": "open"}).sort("created_at", -1)
    docs = [doc async for doc in cursor]
    if not docs:
        return []
    # Batch-fetch company names
    company_ids = list({doc.get("company_id") for doc in docs if doc.get("company_id")})
    company_names = {}
    if company_ids:
        users = await db.users.find({"_id": {"$in": company_ids}}).to_list(length=200)
        company_names = {str(u["_id"]): u.get("name", u.get("company_name", "")) for u in users}
    return [_job_out(doc, company_names.get(str(doc.get("company_id", "")), "")) for doc in docs]


@router.get("/public/{job_id}", response_model=JobOut)
async def get_job_public(job_id: str, request: Request):
    """Public endpoint — any authenticated user can view a job."""
    db = request.app.state.db
    try:
        oid = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
    doc = await db.jobs.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_out(doc)


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: str, request: Request, company: dict = Depends(require_company)):
    return _job_out(await _get_owned_job(request.app.state.db, job_id, str(company["_id"])))


@router.patch("/{job_id}", response_model=JobOut)
async def update_job(job_id: str, payload: JobUpdate, request: Request, company: dict = Depends(require_company)):
    db = request.app.state.db
    doc = await _get_owned_job(db, job_id, str(company["_id"]))
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    updates["updated_at"] = datetime.now(timezone.utc)
    await db.jobs.update_one({"_id": doc["_id"]}, {"$set": updates})
    return _job_out(await _get_owned_job(db, job_id, str(company["_id"])))


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str, request: Request, company: dict = Depends(require_company)):
    db = request.app.state.db
    doc = await _get_owned_job(db, job_id, str(company["_id"]))
    await db.jobs.delete_one({"_id": doc["_id"]})
    await db.applications.delete_many({"job_id": doc["_id"]})
    return None


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
    try:
        oid = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
    await _get_owned_job(db, job_id, str(company["_id"]))
    cursor = db.applications.find({"job_id": oid})
    return [_app_out(doc) async for doc in cursor]
