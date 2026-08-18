"""Router: Progress Tracking endpoints with Applied Job & Interview Deficit Integration"""

from fastapi import APIRouter, Request, HTTPException
from datetime import datetime, timezone
from bson import ObjectId
from typing import Any, Dict, Optional, List
from pydantic import BaseModel

router = APIRouter()


class ProgressUpdateRequest(BaseModel):
    candidate_id: str
    skill: str
    status: str
    notes: Optional[str] = ""
    source_role: Optional[str] = None
    course_name: Optional[str] = None
    course_url: Optional[str] = None


@router.post("/update", summary="Update skill learning progress")
async def update_progress(payload: ProgressUpdateRequest, request: Request):
    db = request.app.state.db
    
    existing = await db.progress_tracking.find_one({
        "candidate_id": payload.candidate_id,
        "skill": payload.skill
    })
    
    doc = {
        "candidate_id": payload.candidate_id,
        "skill": payload.skill,
        "status": payload.status,
        "notes": payload.notes or (existing.get("notes", "") if existing else ""),
        "source_role": payload.source_role or (existing.get("source_role", "") if existing else ""),
        "course_name": payload.course_name or (existing.get("course_name", "") if existing else ""),
        "course_url": payload.course_url or (existing.get("course_url", "") if existing else ""),
        "improvement_tips": existing.get("improvement_tips", "") if existing else "",
        "updated_at": datetime.now(timezone.utc),
    }
    
    await db.progress_tracking.replace_one(
        {"candidate_id": payload.candidate_id, "skill": payload.skill},
        doc,
        upsert=True,
    )
    return {"success": True, "message": "Progress updated", "data": doc}


@router.post("/sync-from-applied-interviews/{candidate_id}", summary="Auto-sync weak skills directly from candidate's applied jobs and interview results")
async def sync_progress_from_applied_interviews(candidate_id: str, request: Request):
    """
    Scans candidate applied jobs and interview results, identifies weak skills & knowledge gaps,
    and populates the Progress Matrix with structured learning paths.
    """
    db = request.app.state.db
    from services.ml_engine import RESOURCES, JOB_REQ

    # 1. Fetch applications
    applications = []
    cursor = db.applications.find({"candidate_id": candidate_id}).sort("applied_at", -1)
    async for app in cursor:
        applications.append(app)
    if not applications:
        try:
            cursor = db.applications.find({"candidate_id": ObjectId(candidate_id)}).sort("applied_at", -1)
            async for app in cursor:
                applications.append(app)
        except Exception:
            pass

    # 2. Fetch candidate resume
    resume = await db.resumes.find_one({"candidate_id": candidate_id}, sort=[("created_at", -1)])
    if not resume:
        try:
            resume = await db.resumes.find_one({"candidate_id": ObjectId(candidate_id)}, sort=[("created_at", -1)])
        except Exception:
            pass

    cand_skills_lower = {s.strip().lower() for s in (resume.get("skills", []) if resume else [])}

    # Fetch existing progress entries to preserve candidate status (e.g. in_progress, completed)
    existing_map = {}
    async for doc in db.progress_tracking.find({"candidate_id": candidate_id}):
        existing_map[doc["skill"].lower()] = doc

    synced_count = 0
    now = datetime.now(timezone.utc)

    for app in applications:
        job_id = str(app.get("job_id", ""))
        job = None
        try:
            job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        except Exception:
            pass
        if not job:
            job = await db.jobs.find_one({"_id": job_id})
        if not job:
            continue

        job_title = job.get("title", "Software Engineer")
        required_skills = job.get("required_skills", [])

        # Fetch Company name
        comp_name = job.get("company_name", "")
        if not comp_name and job.get("company_id"):
            try:
                comp_user = await db.users.find_one({"_id": ObjectId(job["company_id"])})
                if comp_user:
                    comp_name = comp_user.get("company_name", comp_user.get("full_name", "Tech Employer"))
            except Exception:
                pass
        if not comp_name:
            comp_name = "Applied Employer"

        # Fetch Interview Results for this role
        interview_res = await db.results.find_one({
            "candidate_id": candidate_id,
            "$or": [{"job_role": job_title}, {"job_role": job.get("title", "")}]
        }, sort=[("created_at", -1)])

        weak_skills_found = []

        # A. Extract weak topics from interview
        if interview_res:
            for wt in interview_res.get("weak_topics", []):
                weak_skills_found.append({
                    "skill": wt,
                    "reason": f"Low score in {job_title} technical interview ({comp_name})",
                    "priority": "High"
                })
            for fmt in interview_res.get("failed_mcq_topics", []):
                if not any(w["skill"].lower() == fmt.lower() for w in weak_skills_found):
                    weak_skills_found.append({
                        "skill": fmt,
                        "reason": f"Missed core MCQ questions in {job_title} interview",
                        "priority": "High"
                    })

            # Check question-level details
            for mcq in interview_res.get("mcq_details", []):
                if not mcq.get("is_correct"):
                    t = mcq.get("topic") or mcq.get("category")
                    if t and not any(w["skill"].lower() == t.lower() for w in weak_skills_found):
                        weak_skills_found.append({
                            "skill": t,
                            "reason": f"Incorrect conceptual answer in {job_title} interview",
                            "priority": "Medium"
                        })

            for desc in interview_res.get("descriptive_details", []):
                score = desc.get("score", desc.get("similarity_score", 100))
                if score < 60:
                    t = desc.get("topic") or desc.get("category")
                    if t and not any(w["skill"].lower() == t.lower() for w in weak_skills_found):
                        weak_skills_found.append({
                            "skill": t,
                            "reason": f"Incomplete technical explanation ({score}%) in {job_title} interview",
                            "priority": "High"
                        })

            for code in interview_res.get("coding_details", []):
                score = code.get("score", 100)
                if score < 70:
                    t = code.get("topic") or "Algorithms & Live Coding"
                    if not any(w["skill"].lower() == t.lower() for w in weak_skills_found):
                        weak_skills_found.append({
                            "skill": t,
                            "reason": f"Failed automated test cases in {job_title} coding challenge",
                            "priority": "Critical"
                        })

        # B. Extract missing skills from CV for this job
        for req_s in required_skills:
            if req_s.lower() not in cand_skills_lower and not any(req_s.lower() in cs for cs in cand_skills_lower):
                if not any(w["skill"].lower() == req_s.lower() for w in weak_skills_found):
                    weak_skills_found.append({
                        "skill": req_s,
                        "reason": f"Required prerequisite for {job_title} @ {comp_name}, not present on CV",
                        "priority": "High"
                    })

        # Upsert each weak skill into progress_tracking
        for item in weak_skills_found:
            sk_name = item["skill"].strip()
            sk_key = sk_name.lower()
            
            # Lookup learning resource
            res = RESOURCES.get(sk_name)
            if not res:
                for rk, rv in RESOURCES.items():
                    if rk.lower() in sk_name.lower() or sk_name.lower() in rk.lower():
                        res = rv
                        break
            if not res:
                res = {
                    "course": f"{sk_name} Practical Mastery & Interview Prep",
                    "url": "https://www.coursera.org/search?query=" + sk_name.replace(" ", "+"),
                    "duration": "4 weeks",
                    "level": "Intermediate",
                }

            existing = existing_map.get(sk_key)
            status = existing.get("status", "not_started") if existing else "not_started"
            notes = existing.get("notes", "") if existing else ""

            doc = {
                "candidate_id": candidate_id,
                "skill": sk_name,
                "status": status,
                "priority": item["priority"],
                "source_role": job_title,
                "source_company": comp_name,
                "deficit_reason": item["reason"],
                "course_name": res["course"],
                "course_url": res["url"],
                "duration": res["duration"],
                "level": res["level"],
                "improvement_tips": f"Review key syntax, architectural patterns, and practical implementation for {sk_name} to succeed in future {job_title} interviews.",
                "notes": notes,
                "updated_at": now,
            }

            await db.progress_tracking.replace_one(
                {"candidate_id": candidate_id, "skill": sk_name},
                doc,
                upsert=True
            )
            existing_map[sk_key] = doc
            synced_count += 1

    # Fetch updated list
    docs = await db.progress_tracking.find(
        {"candidate_id": candidate_id},
        projection={"_id": 0}
    ).to_list(length=100)

    stats = {
        "not_started": sum(1 for d in docs if d["status"] == "not_started"),
        "in_progress": sum(1 for d in docs if d["status"] == "in_progress"),
        "completed": sum(1 for d in docs if d["status"] == "completed"),
        "total": len(docs),
    }
    pct = (stats["completed"] / stats["total"] * 100) if stats["total"] else 0
    stats["completion_pct"] = round(pct, 1)

    return {
        "success": True,
        "candidate_id": candidate_id,
        "synced_count": synced_count,
        "stats": stats,
        "skills": docs
    }


@router.post("/populate", summary="Auto-populate progress from latest skill gap report")
async def populate_progress(request: Request):
    db = request.app.state.db
    report = await db.skill_gap_reports.find_one(
        sort=[("created_at", -1)],
    )
    if not report:
        raise HTTPException(404, "No skill gap reports found. Run a skill gap analysis first.")
    candidate_id = report.get("candidate_id", "web-user")
    skills = report.get("missing_required", []) + report.get("missing_optional", [])
    existing = {
        doc["skill"] async for doc in db.progress_tracking.find(
            {"candidate_id": candidate_id}, projection={"skill": 1, "_id": 0}
        )
    }
    inserted = 0
    for skill in skills:
        if skill not in existing:
            await db.progress_tracking.insert_one({
                "candidate_id": candidate_id,
                "skill": skill,
                "status": "not_started",
                "notes": "",
                "updated_at": datetime.now(timezone.utc),
            })
            inserted += 1
    return {"success": True, "populated": inserted, "candidate_id": candidate_id}


@router.get("/{candidate_id}", summary="Get full progress for a candidate")
async def get_progress(candidate_id: str, request: Request):
    db = request.app.state.db
    docs = await db.progress_tracking.find(
        {"candidate_id": candidate_id},
        projection={"_id": 0},
    ).sort("updated_at", -1).to_list(length=100)

    stats = {
        "not_started": sum(1 for d in docs if d.get("status") == "not_started"),
        "in_progress": sum(1 for d in docs if d.get("status") == "in_progress"),
        "completed": sum(1 for d in docs if d.get("status") == "completed"),
        "total": len(docs),
    }
    pct = (stats["completed"] / stats["total"] * 100) if stats["total"] else 0
    stats["completion_pct"] = round(pct, 1)

    return {"success": True, "candidate_id": candidate_id, "stats": stats, "skills": docs}


@router.delete("/{candidate_id}", summary="Reset progress for a candidate")
async def reset_progress(candidate_id: str, request: Request):
    db = request.app.state.db
    res = await db.progress_tracking.delete_many({"candidate_id": candidate_id})
    return {"success": True, "deleted": res.deleted_count}
