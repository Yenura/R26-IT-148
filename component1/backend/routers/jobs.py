"""Component 1 — job posting router."""

from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone

from models.schemas import JobCreate, JobOut
from services.cv_service import get_service

router = APIRouter()


@router.get("/jobs", summary="List available job postings")
async def list_jobs(request: Request):
    default_jobs = get_service().jobs()
    posted = await request.app.state.store.find_all("jobs")
    items = []
    for role, spec in default_jobs.items():
        items.append({
            "id": f"job_{role}",
            "job_role": role,
            "title": role.replace("_", " "),
            "description": "",
            "required_skills": spec["required_skills"],
            "required_years": spec["required_years"],
            "min_edu": spec["min_edu"],
            "w_edu": spec["w_edu"],
            "w_exp": spec["w_exp"],
            "w_skill": spec["w_skill"],
            "source": "builtin",
        })
    items.extend(posted)
    return {"success": True, "count": len(items), "jobs": items}


@router.post("/jobs", response_model=JobOut, status_code=201,
             summary="Employer posts a new job")
async def create_job(payload: JobCreate, request: Request):
    doc = {
        **payload.model_dump(),
        "title": payload.title or payload.job_role.replace("_", " "),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "employer",
    }
    job_id = await request.app.state.store.insert_one("jobs", doc)
    if job_id:
        return JobOut(**doc)
    raise HTTPException(status_code=500, detail="Failed to store job")
