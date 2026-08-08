"""Component 1 — CV matching router."""

import uuid
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone

from models.schemas import CVMatchRequest, CVMatchResponse
from services.cv_service import get_service

router = APIRouter()


@router.post("/match/cv", response_model=CVMatchResponse,
             summary="Match a CV to a job role")
async def match_cv(payload: CVMatchRequest, request: Request):
    service = get_service()
    if payload.job_role not in service.jobs():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid job_role. Available: {sorted(service.jobs().keys())}",
        )
    result = service.match(payload)
    report_id = str(uuid.uuid4())
    report = result.model_dump()
    report["id"] = report_id
    report["report_id"] = report_id
    report["created_at"] = datetime.now(timezone.utc).isoformat()
    await request.app.state.store.insert_one("match_reports", report)
    result.report_id = report_id
    return result


@router.get("/match/report/{report_id}", summary="Fetch a stored CV match report")
async def get_report(report_id: str, request: Request):
    doc = await request.app.state.store.find_one("match_reports", {"id": report_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Report not found")
    return doc
