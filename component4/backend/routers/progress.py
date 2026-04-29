"""Router: Progress Tracking endpoints"""

from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
from models.schemas import ProgressUpdateRequest

router = APIRouter()


@router.post("/update", summary="Update skill learning progress")
async def update_progress(payload: ProgressUpdateRequest, request: Request):
    db  = request.app.state.db
    doc = {
        "candidate_id": payload.candidate_id,
        "skill":        payload.skill,
        "status":       payload.status,
        "notes":        payload.notes,
        "updated_at":   datetime.utcnow(),
    }
    await db.progress_tracking.replace_one(
        {"candidate_id": payload.candidate_id, "skill": payload.skill},
        doc,
        upsert=True,
    )
    return {"success": True, "message": "Progress updated", "data": doc}


@router.get("/{candidate_id}", summary="Get full progress for a candidate")
async def get_progress(candidate_id: str, request: Request):
    db   = request.app.state.db
    docs = await db.progress_tracking.find(
        {"candidate_id": candidate_id},
        projection={"_id": 0},
    ).to_list(length=100)

    stats = {
        "not_started": sum(1 for d in docs if d["status"] == "not_started"),
        "in_progress":  sum(1 for d in docs if d["status"] == "in_progress"),
        "completed":    sum(1 for d in docs if d["status"] == "completed"),
        "total":        len(docs),
    }
    pct = (stats["completed"] / stats["total"] * 100) if stats["total"] else 0
    stats["completion_pct"] = round(pct, 1)

    return {"success": True, "candidate_id": candidate_id,
            "stats": stats, "skills": docs}


@router.delete("/{candidate_id}", summary="Reset progress for a candidate")
async def reset_progress(candidate_id: str, request: Request):
    db  = request.app.state.db
    res = await db.progress_tracking.delete_many({"candidate_id": candidate_id})
    return {"success": True, "deleted": res.deleted_count}
