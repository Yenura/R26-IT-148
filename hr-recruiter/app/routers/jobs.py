"""Job postings CRUD (owner-scoped) plus candidate applications."""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.engine_link import normalise_role, role_display_name
from app.routers.auth import get_current_recruiter
from app.schemas import (
    ApplicationCreate,
    ApplicationOut,
    JobPostingCreate,
    JobPostingOut,
    JobPostingUpdate,
)

router = APIRouter()


def job_out(doc: dict) -> JobPostingOut:
    return JobPostingOut(
        id=str(doc["_id"]),
        recruiter_id=str(doc["recruiter_id"]),
        title=doc["title"],
        description=doc["description"],
        job_role=doc["job_role"],
        role_key=doc["role_key"],
        job_level=doc["job_level"],
        work_mode=doc["work_mode"],
        location=doc.get("location"),
        skills_required=doc.get("skills_required", []),
        status=doc["status"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


async def _fetch_owned_job(db, job_id: str, recruiter_id: str) -> dict:
    try:
        oid = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
    doc = await db.job_postings.find_one({"_id": oid, "recruiter_id": ObjectId(recruiter_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return doc


@router.post(
    "",
    response_model=JobPostingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a job posting",
)
async def create_job(
    payload: JobPostingCreate,
    request: Request,
    recruiter: dict = Depends(get_current_recruiter),
):
    try:
        role_key = normalise_role(payload.job_role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    now = datetime.now(timezone.utc)
    doc = {
        "recruiter_id":   recruiter["_id"],
        "title":          payload.title.strip(),
        "description":    payload.description.strip(),
        "job_role":       role_display_name(role_key),
        "role_key":       role_key,
        "job_level":      payload.job_level,
        "work_mode":      payload.work_mode,
        "location":       payload.location,
        "skills_required": payload.skills_required,
        "status":         payload.status,
        "created_at":     now,
        "updated_at":     now,
    }
    result = await request.app.state.db.job_postings.insert_one(doc)
    doc["_id"] = result.inserted_id
    return job_out(doc)


@router.get(
    "",
    response_model=list[JobPostingOut],
    summary="List job postings (owned by the recruiter)",
)
async def list_jobs(
    request: Request,
    recruiter: dict = Depends(get_current_recruiter),
    status_filter: str | None = None,
    role_key: str | None = None,
):
    query: dict = {"recruiter_id": recruiter["_id"]}
    if status_filter:
        query["status"] = status_filter.strip().lower()
    if role_key:
        try:
            query["role_key"] = normalise_role(role_key)
        except ValueError:
            return []
    cursor = request.app.state.db.job_postings.find(query).sort("created_at", -1)
    return [job_out(doc) async for doc in cursor]


@router.get("/{job_id}", response_model=JobPostingOut, summary="Get one job posting")
async def get_job(
    job_id: str,
    request: Request,
    recruiter: dict = Depends(get_current_recruiter),
):
    return job_out(await _fetch_owned_job(request.app.state.db, job_id, str(recruiter["_id"])))


@router.patch("/{job_id}", response_model=JobPostingOut, summary="Update a job posting")
async def update_job(
    job_id: str,
    payload: JobPostingUpdate,
    request: Request,
    recruiter: dict = Depends(get_current_recruiter),
):
    db = request.app.state.db
    doc = await _fetch_owned_job(db, job_id, str(recruiter["_id"]))

    updates = payload.model_dump(exclude_unset=True)
    if "job_role" in updates and updates["job_role"] is not None:
        try:
            role_key = normalise_role(updates["job_role"])
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        updates["role_key"] = role_key
        updates["job_role"] = role_display_name(role_key)
    updates["updated_at"] = datetime.now(timezone.utc)

    await db.job_postings.update_one({"_id": doc["_id"]}, {"$set": updates})
    return job_out(await _fetch_owned_job(db, job_id, str(recruiter["_id"])))


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a job posting")
async def delete_job(
    job_id: str,
    request: Request,
    recruiter: dict = Depends(get_current_recruiter),
):
    db = request.app.state.db
    doc = await _fetch_owned_job(db, job_id, str(recruiter["_id"]))
    await db.job_postings.delete_one({"_id": doc["_id"]})
    await db.applications.delete_many({"job_id": doc["_id"]})
    return None


@router.post(
    "/{job_id}/apply",
    response_model=ApplicationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Record a candidate application for a job",
)
async def apply(
    job_id: str,
    payload: ApplicationCreate,
    request: Request,
    recruiter: dict = Depends(get_current_recruiter),
):
    db = request.app.state.db
    job = await _fetch_owned_job(db, job_id, str(recruiter["_id"]))
    if job["status"] != "open":
        raise HTTPException(status_code=422, detail="Job posting is closed for applications")

    existing = await db.applications.find_one(
        {"job_id": job["_id"], "candidate_id": payload.candidate_id}
    )
    if existing:
        raise HTTPException(status_code=409, detail="Candidate already applied to this job")

    now = datetime.now(timezone.utc)
    doc = {
        "job_id":           job["_id"],
        "job_role":         job["job_role"],
        "role_key":         job["role_key"],
        "candidate_id":     payload.candidate_id,
        "candidate_name":   payload.candidate_name.strip(),
        "experience_years": payload.experience_years,
        "education":        payload.education,
        "skills":           [s.strip() for s in payload.skills if s and s.strip()],
        "cv_matching_score": payload.cv_matching_score,
        "mcq_score":         payload.mcq_score,
        "descriptive_score": payload.descriptive_score,
        "coding_score":      payload.coding_score,
        "applied_at":        now,
    }
    result = await db.applications.insert_one(doc)
    doc["_id"] = result.inserted_id
    return ApplicationOut(
        id=str(doc["_id"]),
        job_id=str(doc["job_id"]),
        candidate_id=doc["candidate_id"],
        candidate_name=doc["candidate_name"],
        experience_years=doc["experience_years"],
        education=doc["education"],
        skills=doc["skills"],
        applied_at=doc["applied_at"],
    )
