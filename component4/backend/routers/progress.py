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
    priority: Optional[str] = "High"


@router.post("/update", summary="Update skill learning progress")
async def update_progress(payload: ProgressUpdateRequest, request: Request):
    db = request.app.state.db
    from services.ml_engine import RESOURCES
    
    existing = await db.progress_tracking.find_one({
        "candidate_id": payload.candidate_id,
        "skill": payload.skill
    })
    
    sk_name = payload.skill.strip()
    
    # Auto-resolve course if missing
    course_name = payload.course_name or (existing.get("course_name") if existing else None)
    course_url = payload.course_url or (existing.get("course_url") if existing else None)
    duration = existing.get("duration", "4 weeks") if existing else "4 weeks"
    level = existing.get("level", "Intermediate") if existing else "Intermediate"
    
    if not course_name or not course_url:
        res = RESOURCES.get(sk_name)
        if not res:
            for rk, rv in RESOURCES.items():
                if rk.lower() in sk_name.lower() or sk_name.lower() in rk.lower():
                    res = rv
                    break
        if res:
            course_name = res.get("course")
            course_url = res.get("url")
            duration = res.get("duration", duration)
            level = res.get("level", level)
        else:
            course_name = f"{sk_name} Practical Mastery & Architecture"
            course_url = "https://www.coursera.org/search?query=" + sk_name.replace(" ", "+")
    
    priority = payload.priority or (existing.get("priority", "High") if existing else "High")
    source_role = payload.source_role or (existing.get("source_role", "Target Learning Goal") if existing else "Target Learning Goal")
    deficit_reason = existing.get("deficit_reason", f"Target competency for {source_role}") if existing else f"Target competency for {source_role}"
    tips = existing.get("improvement_tips", f"Master core syntax, patterns, and practical implementation for {sk_name}.") if existing else f"Master core syntax, patterns, and practical implementation for {sk_name}."

    doc = {
        "candidate_id": payload.candidate_id,
        "skill": sk_name,
        "status": payload.status,
        "priority": priority,
        "notes": payload.notes or (existing.get("notes", "") if existing else ""),
        "source_role": source_role,
        "source_company": existing.get("source_company", "Target Employer") if existing else "Target Employer",
        "deficit_reason": deficit_reason,
        "course_name": course_name,
        "course_url": course_url,
        "duration": duration,
        "level": level,
        "improvement_tips": tips,
        "updated_at": datetime.now(timezone.utc),
    }
    
    await db.progress_tracking.replace_one(
        {"candidate_id": payload.candidate_id, "skill": sk_name},
        doc,
        upsert=True,
    )
    return {"success": True, "message": "Progress updated", "data": doc}


@router.post("/sync-from-applied-interviews/{candidate_id}", summary="Auto-sync weak skills directly from candidate's applied jobs and interview results")
async def sync_progress_from_applied_interviews(candidate_id: str, request: Request):
    """
    Scans candidate applied jobs, interview results, CV match history and skill gap reports,
    identifies weak skills & knowledge gaps, and populates the Progress Matrix with structured learning paths.
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
    weak_skills_found = []

    # A. Check Applied Jobs
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

        # Extract weak topics from interview
        if interview_res:
            for wt in interview_res.get("weak_topics", []):
                if not any(w["skill"].lower() == wt.lower() for w in weak_skills_found):
                    weak_skills_found.append({
                        "skill": wt,
                        "source_role": job_title,
                        "source_company": comp_name,
                        "reason": f"Low score in {job_title} technical interview ({comp_name})",
                        "priority": "High"
                    })
            for fmt in interview_res.get("failed_mcq_topics", []):
                if not any(w["skill"].lower() == fmt.lower() for w in weak_skills_found):
                    weak_skills_found.append({
                        "skill": fmt,
                        "source_role": job_title,
                        "source_company": comp_name,
                        "reason": f"Missed core MCQ questions in {job_title} interview",
                        "priority": "High"
                    })

            for desc in interview_res.get("descriptive_details", []):
                score = desc.get("score", desc.get("similarity_score", 100))
                if score < 60:
                    t = desc.get("topic") or desc.get("category")
                    if t and not any(w["skill"].lower() == t.lower() for w in weak_skills_found):
                        weak_skills_found.append({
                            "skill": t,
                            "source_role": job_title,
                            "source_company": comp_name,
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
                            "source_role": job_title,
                            "source_company": comp_name,
                            "reason": f"Failed automated test cases in {job_title} coding challenge",
                            "priority": "Critical"
                        })

        # Extract missing skills from CV for this job
        for req_s in required_skills:
            if req_s.lower() not in cand_skills_lower and not any(req_s.lower() in cs for cs in cand_skills_lower):
                if not any(w["skill"].lower() == req_s.lower() for w in weak_skills_found):
                    weak_skills_found.append({
                        "skill": req_s,
                        "source_role": job_title,
                        "source_company": comp_name,
                        "reason": f"Required competency for {job_title} @ {comp_name}, not yet listed on CV",
                        "priority": "High"
                    })

    # B. Check Latest Skill Gap Reports if no weak skills from applied jobs yet
    if len(weak_skills_found) < 3:
        async for rpt in db.skill_gap_reports.find({"candidate_id": candidate_id}).sort("created_at", -1).limit(3):
            role_name = rpt.get("job_role", "Software Engineer")
            for ms in rpt.get("missing_required", []):
                if not any(w["skill"].lower() == ms.lower() for w in weak_skills_found):
                    weak_skills_found.append({
                        "skill": ms,
                        "source_role": role_name,
                        "source_company": "Role Benchmark",
                        "reason": f"Core required competency for {role_name} career path",
                        "priority": "Critical"
                    })
            for opt in rpt.get("missing_optional", []):
                if not any(w["skill"].lower() == opt.lower() for w in weak_skills_found):
                    weak_skills_found.append({
                        "skill": opt,
                        "source_role": role_name,
                        "source_company": "Role Benchmark",
                        "reason": f"High-impact differentiator for {role_name}",
                        "priority": "Medium"
                    })

    # C. Fallback: If still empty, seed curated foundational goals from candidate resume/role
    if not weak_skills_found:
        target_role = "Software Engineer"
        if resume and resume.get("job_role"):
            target_role = resume.get("job_role")
        
        req = JOB_REQ.get(target_role) or JOB_REQ.get("Software Engineer", {})
        default_skills = req.get("required", ["Docker", "Kubernetes", "CI/CD", "System Design", "SQL", "Redis"])
        for s in default_skills[:6]:
            if s.lower() not in cand_skills_lower:
                weak_skills_found.append({
                    "skill": s,
                    "source_role": target_role,
                    "source_company": "Industry Benchmark",
                    "reason": f"High-demand competency for {target_role} professionals",
                    "priority": "High"
                })

    # Upsert each skill into progress_tracking
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
                "course": f"{sk_name} Professional Certification & Mastery",
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
            "priority": item.get("priority", "High"),
            "source_role": item.get("source_role", "Software Engineer"),
            "source_company": item.get("source_company", "Hiring Employer"),
            "deficit_reason": item.get("reason", f"Target competency for {item.get('source_role', 'Software Engineer')}"),
            "course_name": res["course"],
            "course_url": res["url"],
            "duration": res["duration"],
            "level": res["level"],
            "improvement_tips": f"Review key syntax, architectural patterns, and practical hands-on exercises for {sk_name}.",
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
    ).sort("updated_at", -1).to_list(length=100)

    stats = {
        "not_started": sum(1 for d in docs if d.get("status") == "not_started"),
        "in_progress": sum(1 for d in docs if d.get("status") == "in_progress"),
        "completed": sum(1 for d in docs if d.get("status") == "completed"),
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
    candidate_id = "web-user"
    try:
        body = await request.json()
        if isinstance(body, dict) and body.get("candidate_id"):
            candidate_id = str(body["candidate_id"]).strip()
    except Exception:
        pass

    return await sync_progress_from_applied_interviews(candidate_id, request)


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


@router.delete("/{candidate_id}/{skill}", summary="Delete a specific progress skill goal")
async def delete_progress_skill(candidate_id: str, skill: str, request: Request):
    db = request.app.state.db
    res = await db.progress_tracking.delete_one({"candidate_id": candidate_id, "skill": skill})
    return {"success": True, "deleted": res.deleted_count > 0, "skill": skill}


@router.delete("/{candidate_id}", summary="Reset all progress for a candidate")
async def reset_progress(candidate_id: str, request: Request):
    db = request.app.state.db
    res = await db.progress_tracking.delete_many({"candidate_id": candidate_id})
    return {"success": True, "deleted": res.deleted_count}
