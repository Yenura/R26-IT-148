"""Resume upload, parsing, NLP preprocessing, and semantic matching."""
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from slowapi import Limiter
from slowapi.util import get_remote_address

from schemas import ResumeOut, ResumeUpdate, PredictionOut, InterviewScoresCreate
from routers.auth import get_current_user, require_company, require_candidate
from services.resume_parser import parse_resume_file, extract_entities
from services.role_classifier import RoleClassifier

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def _oid_or_404(raw_id: str):
    """Parse an ObjectId or raise 404 (never 500 on malformed ids)."""
    from bson import ObjectId
    if not ObjectId.is_valid(raw_id):
        raise HTTPException(status_code=404, detail="Resume not found")
    return ObjectId(raw_id)


async def _company_candidate_ids(db, company_id: str) -> set:
    """Candidate ids that applied to any of this company's jobs (str + ObjectId forms)."""
    from bson import ObjectId
    comp_filters = [{"company_id": str(company_id)}]
    if ObjectId.is_valid(str(company_id)):
        comp_filters.append({"company_id": ObjectId(company_id)})
    jobs = await db.jobs.find({"$or": comp_filters}, {"_id": 1}).to_list(1000)
    job_ids = [str(j["_id"]) for j in jobs]
    if not job_ids:
        return set()
    apps = await db.applications.find(
        {"$or": [{"job_id": {"$in": job_ids}}, {"job_id": {"$in": [j["_id"] for j in jobs]}}]},
        {"candidate_id": 1},
    ).to_list(10000)
    ids = set()
    for a in apps:
        cid = a.get("candidate_id")
        if cid:
            ids.add(str(cid))
            if ObjectId.is_valid(str(cid)):
                ids.add(ObjectId(cid))
    return ids


async def _can_company_view_candidate(db, company_id: str, candidate_id: str) -> bool:
    """True if the candidate applied to at least one of the company's jobs."""
    if not candidate_id:
        return False
    job_ids = await _company_job_ids(db, company_id)
    if not job_ids:
        return False
    app = await db.applications.find_one(
        {"job_id": {"$in": job_ids}, "candidate_id": str(candidate_id)}
    )
    return app is not None


async def _company_job_ids(db, company_id: str) -> list:
    from bson import ObjectId
    comp_filters = [{"company_id": str(company_id)}]
    if ObjectId.is_valid(str(company_id)):
        comp_filters.append({"company_id": ObjectId(company_id)})
    jobs = await db.jobs.find({"$or": comp_filters}, {"_id": 1}).to_list(1000)
    return [str(j["_id"]) for j in jobs] + [j["_id"] for j in jobs]

_classifier: RoleClassifier | None = None


def _get_classifier() -> RoleClassifier:
    global _classifier
    if _classifier is None:
        _classifier = RoleClassifier()
    return _classifier


def _resume_out(doc: dict) -> ResumeOut:
    edu = doc.get("education", "")
    if (not edu or len(edu.strip()) < 3) and doc.get("raw_text"):
        try:
            ent = extract_entities(doc.get("raw_text", ""))
            edu = ent.get("education", "")
        except Exception:
            pass

    return ResumeOut(
        id=str(doc["_id"]),
        candidate_id=doc.get("candidate_id", ""),
        filename=doc.get("filename", ""),
        candidate_name=doc.get("candidate_name", ""),
        email=doc.get("email", ""),
        phone=doc.get("phone", ""),
        address=doc.get("address", ""),
        linkedin=doc.get("linkedin", ""),
        github=doc.get("github", ""),
        skills=doc.get("skills", []),
        education=edu,
        experience_years=doc.get("experience_years", 0),
        projects=doc.get("projects", []),
        academic_projects=doc.get("academic_projects", []),
        personal_projects=doc.get("personal_projects", []),
        project_experience_years=doc.get("project_experience_years", 0),
        certifications=doc.get("certifications", []),
        languages=doc.get("languages", []),
        tools=doc.get("tools", []),
        frameworks=doc.get("frameworks", []),
        raw_text=doc.get("raw_text", ""),
        created_at=doc.get("created_at"),
    )


def _pred_out(doc: dict) -> PredictionOut:
    return PredictionOut(
        id=str(doc.get("_id", "pred_1")),
        resume_id=doc.get("resume_id", ""),
        candidate_id=doc.get("candidate_id", ""),
        job_id=doc.get("job_id", ""),
        target_role=doc.get("target_role", ""),
        predicted_role=doc.get("predicted_role", ""),
        role_confidence=doc.get("role_confidence", 0),
        semantic_score=doc.get("semantic_score", 0),
        skill_score=doc.get("skill_score", 0),
        experience_score=doc.get("experience_score", 0),
        education_score=doc.get("education_score", 0),
        overall_score=doc.get("overall_score", 0),
        matched_skills=doc.get("matched_skills", []),
        missing_skills=doc.get("missing_skills", []),
        extra_skills=doc.get("extra_skills", []),
        career_suggestions=doc.get("career_suggestions", []),
        created_at=doc.get("created_at"),
    )


@limiter.limit("10/minute")
@router.post("", response_model=ResumeOut, status_code=201)
@router.post("/", response_model=ResumeOut, status_code=201)
@router.post("/upload", response_model=ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    request: Request = None,
    user: dict = Depends(get_current_user),
):
    if not file.filename.lower().endswith((".pdf", ".docx", ".doc", ".txt")):
        raise HTTPException(status_code=400, detail="Supported formats: PDF, DOCX, TXT")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    raw_text = parse_resume_file(content, file.filename)
    if not raw_text or not raw_text.strip():
        raw_text = f"Candidate Resume ({file.filename}) submitted by {user.get('full_name', 'Candidate')}."
    entities = extract_entities(raw_text)
    now = datetime.now(timezone.utc)
    doc = {
        "candidate_id": str(user["_id"]),
        "filename": file.filename,
        "candidate_name": entities.get("name", user.get("full_name", "")),
        "email": entities.get("email", user.get("email", "")),
        "phone": entities.get("phone", ""),
        "address": entities.get("address", ""),
        "linkedin": entities.get("linkedin", ""),
        "github": entities.get("github", ""),
        "skills": entities.get("skills", []),
        "education": entities.get("education", ""),
        "experience_years": entities.get("experience_years", 0),
        "projects": entities.get("projects", []),
        "academic_projects": entities.get("academic_projects", []),
        "personal_projects": entities.get("personal_projects", []),
        "project_experience_years": entities.get("project_experience_years", 0),
        "certifications": entities.get("certifications", []),
        "languages": entities.get("languages", []),
        "tools": entities.get("tools", []),
        "frameworks": entities.get("frameworks", []),
        "raw_text": raw_text,
        "created_at": now,
    }
    result = await request.app.state.db.resumes.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _resume_out(doc)


@router.get("", response_model=list[ResumeOut])
@router.get("/", response_model=list[ResumeOut])
@limiter.limit("60/minute")
async def list_resumes(request: Request, user: dict = Depends(get_current_user)):
    db = request.app.state.db
    if user.get("role") == "company":
        # Companies see only candidates who applied to their own jobs.
        cand_ids = await _company_candidate_ids(db, str(user["_id"]))
        if not cand_ids:
            return []
        cursor = db.resumes.find({"candidate_id": {"$in": list(cand_ids)}}).sort("created_at", -1).limit(100)
    else:
        cursor = db.resumes.find({"candidate_id": str(user["_id"])}).sort("created_at", -1)
        results = [_resume_out(doc) async for doc in cursor]
        return results
    return [_resume_out(doc) async for doc in cursor]


@router.get("/predictions", response_model=list[PredictionOut])
@limiter.limit("60/minute")
async def list_predictions(request: Request, user: dict = Depends(get_current_user)):
    cursor = request.app.state.db.predictions.find({"candidate_id": str(user["_id"])}).sort("created_at", -1)
    return [_pred_out(doc) async for doc in cursor]


@router.get("/predict-role")
async def predict_role(
    request: Request,
    resume_id: str = "",
    user: dict = Depends(get_current_user),
):
    db = request.app.state.db
    if resume_id:
        from bson import ObjectId
        resume_doc = await db.resumes.find_one({"_id": _oid_or_404(resume_id), "candidate_id": str(user["_id"])})
    else:
        resume_doc = await db.resumes.find_one(
            {"candidate_id": str(user["_id"])},
            sort=[("created_at", -1)]
        )
    if not resume_doc:
        raise HTTPException(status_code=404, detail="No resume found")
    classifier = _get_classifier()
    role, confidence = classifier.predict(
        resume_doc.get("raw_text", ""),
        resume_doc.get("skills", [])
    )
    return {"predicted_role": role, "confidence": round(confidence, 4)}


CANONICAL_ROLE_REQS = {
    "Software Engineer": {"skills": ["Python", "Java", "Data Structures", "Algorithms", "Git", "SQL"], "exp": 2},
    "Data Scientist": {"skills": ["Python", "Pandas", "Statistics", "Machine Learning", "SQL", "Data Visualization"], "exp": 2},
    "Machine Learning Engineer": {"skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "MLOps", "Docker", "TensorFlow"], "exp": 3},
    "DevOps Engineer": {"skills": ["Linux", "Docker", "Kubernetes", "CI/CD", "Terraform", "AWS", "Python"], "exp": 3},
    "Cloud Solutions Architect": {"skills": ["AWS", "Cloud Architecture", "Azure", "Kubernetes", "Networking", "Security"], "exp": 5},
    "Database Administrator": {"skills": ["SQL", "PostgreSQL", "MySQL", "Database Tuning", "Backup and Recovery", "Linux"], "exp": 3},
    "Frontend Developer": {"skills": ["JavaScript", "React", "HTML", "CSS", "TypeScript", "Tailwind", "Git"], "exp": 2},
    "Backend Developer": {"skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker", "Redis", "AWS"], "exp": 2},
    "Mobile App Developer": {"skills": ["Flutter", "Dart", "React Native", "iOS", "Android", "REST APIs"], "exp": 2},
    "Full Stack Developer": {"skills": ["JavaScript", "React", "Node.js", "SQL", "MongoDB", "Docker", "Git"], "exp": 3},
    "QA/Test Automation Engineer": {"skills": ["Selenium", "Python", "Test Automation", "Jest", "CI/CD", "Git"], "exp": 2},
    "Data Engineer": {"skills": ["Python", "SQL", "Spark", "Airflow", "ETL Pipelines", "Kafka"], "exp": 3},
    "Site Reliability Engineer": {"skills": ["Linux", "Kubernetes", "Prometheus", "Python", "Docker", "CI/CD"], "exp": 4},
    "Cybersecurity Analyst": {"skills": ["Network Security", "Ethical Hacking", "SIEM", "Linux", "Cryptography", "Python"], "exp": 3},
    "UI/UX Designer": {"skills": ["Figma", "Wireframing", "User Research", "Prototyping", "Design Systems"], "exp": 2},
    "Network Engineer": {"skills": ["Cisco", "Networking", "Firewalls", "Routing Protocols", "Linux"], "exp": 3},
    "Business/Systems Analyst": {"skills": ["Requirements Gathering", "SQL", "UML", "Data Analysis", "Agile"], "exp": 2},
    "AI/NLP Engineer": {"skills": ["Python", "NLP", "PyTorch", "Transformers", "Spacy"], "exp": 3},
    "Blockchain Developer": {"skills": ["Solidity", "Smart Contracts", "Ethereum", "Web3.js"], "exp": 3},
    "Embedded Systems Engineer": {"skills": ["C++", "C", "RTOS", "Microcontrollers"], "exp": 3},
}


@router.get("/match", response_model=PredictionOut)
@router.post("/match", response_model=PredictionOut)
@limiter.limit("20/minute")
async def match_resume(
    request: Request,
    resume_id: str = "",
    job_id: str = "",
    target_role: str = "",
    user: dict = Depends(get_current_user),
):
    db = request.app.state.db
    resume_doc = None
    if resume_id:
        from bson import ObjectId
        try:
            query = {"_id": ObjectId(resume_id)}
            if user.get("role") != "company":
                query["candidate_id"] = str(user["_id"])
            resume_doc = await db.resumes.find_one(query)
        except Exception:
            resume_doc = None

    if not resume_doc and user:
        from bson import ObjectId
        cand_filters = [{"candidate_id": str(user["_id"])}]
        if ObjectId.is_valid(str(user["_id"])):
            cand_filters.append({"candidate_id": ObjectId(user["_id"])})
        resume_doc = await db.resumes.find_one(
            {"$or": cand_filters},
            sort=[("created_at", -1)]
        )

    if not resume_doc:
        raise HTTPException(status_code=404, detail="No resume found")

    job_doc = None
    if job_id:
        from bson import ObjectId as Oid
        try:
            job_doc = await db.jobs.find_one({"_id": Oid(job_id)})
        except Exception:
            try:
                job_doc = await db.jobs.find_one({"id": job_id})
            except Exception:
                job_doc = None

    resume_text = resume_doc.get("raw_text", "") or resume_doc.get("text", "") or resume_doc.get("resume_text", "")
    cand_skills_raw = resume_doc.get("skills", [])
    if isinstance(cand_skills_raw, str):
        cand_skills_raw = [s.strip() for s in cand_skills_raw.split(",") if s.strip()]
    resume_skills_lower = [str(s).strip().lower() for s in cand_skills_raw if str(s).strip()]
    job_skills_original = []
    job_skills_lower = []
    required_years = 0.0

    if job_doc:
        raw_req_skills = job_doc.get("required_skills", [])
        if isinstance(raw_req_skills, str):
            raw_req_skills = [s.strip() for s in raw_req_skills.split(",") if s.strip()]
        job_skills_original = [str(s).strip() for s in raw_req_skills if str(s).strip()]
        job_skills_lower = [s.lower() for s in job_skills_original]
        try:
            required_years = float(job_doc.get("experience_required", 0) or 0)
        except (ValueError, TypeError):
            required_years = 2.0
    elif target_role and target_role in CANONICAL_ROLE_REQS:
        role_data = CANONICAL_ROLE_REQS[target_role]
        job_skills_original = role_data["skills"]
        job_skills_lower = [s.strip().lower() for s in job_skills_original]
        required_years = float(role_data["exp"])
    else:
        # Fallback to predicted role from classifier
        classifier = _get_classifier()
        p_role, _ = classifier.predict(resume_text, cand_skills_raw)
        matched_target = target_role if (target_role and target_role in CANONICAL_ROLE_REQS) else p_role
        role_data = CANONICAL_ROLE_REQS.get(matched_target, CANONICAL_ROLE_REQS.get("Software Engineer", {"skills": ["Python", "SQL", "Git"], "exp": 2}))
        job_skills_original = role_data["skills"]
        job_skills_lower = [s.strip().lower() for s in job_skills_original]
        required_years = float(role_data["exp"])

    # Skill matching: bidirectional substring match (fuzzy)
    def _skill_matches(job_skill: str, cand_skills: list) -> bool:
        """Check if a job skill matches any candidate skill via substring containment."""
        js = job_skill.lower().strip()
        for cs in cand_skills:
            cs_lower = cs.lower().strip()
            if js == cs_lower:
                return True
            # Substring match: "flutter" in "flutter sdk" or "flutter sdk" in "flutter"
            if len(js) >= 3 and len(cs_lower) >= 3:
                if js in cs_lower or cs_lower in js:
                    return True
        return False

    matched_original = []
    for orig, lower in zip(job_skills_original, job_skills_lower):
        if _skill_matches(lower, resume_skills_lower):
            matched_original.append(orig)
    missing = [s for s in job_skills_original if s not in matched_original]
    extra = [str(s) for s in cand_skills_raw if str(s).lower() not in job_skills_lower]
    skill_score = (len(matched_original) / len(job_skills_original) * 100) if job_skills_original else 85.0

    # Experience: ratio of candidate years to required, capped at 100
    try:
        exp_years = float(resume_doc.get("experience_years", 0) or 0)
    except (ValueError, TypeError):
        exp_years = 2.5

    if required_years <= 0 or exp_years >= required_years:
        experience_score = 100.0
    elif required_years > 0:
        experience_score = min(round((exp_years / required_years) * 100, 1), 100.0)
    else:
        experience_score = 75.0

    # Education: detect level + field relevance
    edu = str(resume_doc.get("education", "")).lower()
    if any(k in edu for k in ["phd", "doctorate", "ph.d", "master", "m.sc", "msc", "mba", "mtech", "bachelor", "b.sc", "bsc", "btech", "degree", "institute", "university", "college", "informatics", "lecturer"]) or (resume_doc.get("education") and len(str(resume_doc.get("education")).strip()) > 3):
        education_score = 100.0
    elif edu.strip():
        education_score = 80.0
    else:
        education_score = 70.0

    # Weighted overall: 3-pillar formula 50% Skills + 30% Experience + 20% Education
    overall_score = round(0.50 * skill_score + 0.30 * experience_score + 0.20 * education_score, 1)

    # Check if Component 1 deep ML analysis is available in db.cv_analyses for this candidate
    try:
        from bson import ObjectId
        c_filter = {"$or": [{"candidate_id": str(user["_id"])}]}
        if ObjectId.is_valid(str(user["_id"])):
            c_filter["$or"].append({"candidate_id": ObjectId(str(user["_id"]))})
        cva = await db.cv_analyses.find_one(c_filter, sort=[("analysis_timestamp", -1)])
        if cva and (cva.get("cv_matching_score") is not None or cva.get("optional_legacy_score") is not None or cva.get("S_skill") is not None):
            s_sk = cva.get("S_skill") or cva.get("s_skill") or (cva.get("component_1_scores") or {}).get("S_skill")
            s_ex = cva.get("S_exp") or cva.get("s_exp") or (cva.get("component_1_scores") or {}).get("S_exp")
            s_ed = cva.get("S_edu") or cva.get("s_edu") or (cva.get("component_1_scores") or {}).get("S_edu")
            raw_c = cva.get("cv_matching_score") or cva.get("optional_legacy_score")
            if s_sk is not None:
                skill_score = float(s_sk)
            if s_ex is not None:
                experience_score = float(s_ex)
            if s_ed is not None:
                education_score = float(s_ed)
            if raw_c is not None:
                overall_score = float(raw_c)
            else:
                overall_score = round(0.50 * skill_score + 0.30 * experience_score + 0.20 * education_score, 1)
    except Exception:
        pass

    classifier = _get_classifier()
    predicted_role, confidence = classifier.predict(resume_text, cand_skills_raw)
    final_predicted = target_role or (job_doc.get("title") if job_doc else None) or predicted_role

    career_suggestions = []
    if missing:
        career_suggestions.append(f"Learn {', '.join(missing[:3])} to improve fit")
    if experience_score < 60:
        career_suggestions.append("Gain more hands-on experience")
    if education_score < 60:
        career_suggestions.append("Consider pursuing a higher degree")
    career_suggestions.append(f"Best suited role: {final_predicted}")

    # job_id holds only real job references; role-based evaluations
    # are namespaced by target_role instead of polluting job_id.
    real_job_id = job_id if job_doc else ""
    target_role_key = target_role or ""
    now = datetime.now(timezone.utc)
    res_id_str = str(resume_doc.get("_id", "demo_resume_01"))

    doc = {
        "resume_id": res_id_str,
        "candidate_id": str(user["_id"]),
        "job_id": real_job_id,
        "target_role": target_role_key,
        "predicted_role": final_predicted,
        "role_confidence": round(confidence, 4),
        "skill_score": round(skill_score, 2),
        "experience_score": round(experience_score, 2),
        "education_score": round(education_score, 2),
        "overall_score": round(overall_score, 2),
        "matched_skills": matched_original,
        "missing_skills": missing,
        "extra_skills": extra,
        "career_suggestions": career_suggestions,
        "created_at": now,
    }

    cand_display_name = user.get("full_name") or user.get("name") or resume_doc.get("candidate_name") or "Candidate"
    doc["candidate_name"] = cand_display_name
    doc["job_role"] = final_predicted

    try:
        await db.predictions.update_one(
            {"resume_id": res_id_str, "job_id": real_job_id, "target_role": target_role_key},
            {"$set": doc},
            upsert=True
        )
        if job_id and job_doc:
            await db.applications.update_one(
                {"candidate_id": str(user["_id"]), "job_id": str(job_id)},
                {"$set": {
                    "job_id": str(job_id),
                    "candidate_id": str(user["_id"]),
                    "candidate_name": cand_display_name,
                    "candidate_email": user.get("email", ""),
                    "resume_id": res_id_str,
                    "job_title": job_doc.get("title", ""),
                    "job_role": job_doc.get("job_role") or job_doc.get("title", ""),
                    "company_id": str(job_doc.get("company_id", "")),
                    "company_name": job_doc.get("company_name", ""),
                    "cv_score": round(overall_score, 2),
                    "overall_score": round(overall_score, 2),
                    "skill_score": round(skill_score, 2),
                    "experience_score": round(experience_score, 2),
                    "education_score": round(education_score, 2),
                    "status": "cv_matched",
                    "applied_at": now,
                }},
                upsert=True
            )
    except Exception:
        pass

    return _pred_out(doc)


@router.get("/{resume_id}", response_model=ResumeOut)
async def get_resume(resume_id: str, request: Request, user: dict = Depends(get_current_user)):
    from bson import ObjectId
    try:
        query = {"_id": ObjectId(resume_id)}
        if user.get("role") != "company":
            query["candidate_id"] = str(user["_id"])
        doc = await request.app.state.db.resumes.find_one(query)
    except Exception:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found")
    return _resume_out(doc)


@limiter.limit("20/minute")
@router.put("/{resume_id}", response_model=ResumeOut)
async def update_resume(resume_id: str, payload: ResumeUpdate, request: Request, user: dict = Depends(get_current_user)):
    from bson import ObjectId
    db = request.app.state.db
    doc = await db.resumes.find_one({"_id": _oid_or_404(resume_id), "candidate_id": str(user["_id"])})
    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found")
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if updates:
        await db.resumes.update_one({"_id": doc["_id"]}, {"$set": updates})
    updated = await db.resumes.find_one({"_id": doc["_id"]})
    return _resume_out(updated)


@limiter.limit("10/minute")
@router.delete("/{resume_id}", status_code=204)
async def delete_resume(resume_id: str, request: Request, user: dict = Depends(get_current_user)):
    from bson import ObjectId
    db = request.app.state.db
    doc = await db.resumes.find_one({"_id": _oid_or_404(resume_id), "candidate_id": str(user["_id"])})
    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found")
    await db.resumes.delete_one({"_id": doc["_id"]})
    await db.predictions.delete_many({"resume_id": resume_id})
    return None


@router.post("/parse", response_model=ResumeOut)
async def parse_resume_text(
    request: Request,
    text: str = "",
    user: dict = Depends(get_current_user),
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text required")
    entities = extract_entities(text)
    now = datetime.now(timezone.utc)
    doc = {
        "candidate_id": str(user["_id"]),
        "filename": "pasted.txt",
        "candidate_name": entities.get("name", ""),
        "email": entities.get("email", ""),
        "phone": entities.get("phone", ""),
        "skills": entities.get("skills", []),
        "education": entities.get("education", ""),
        "experience_years": entities.get("experience_years", 0),
        "raw_text": text,
        "created_at": now,
    }
    result = await request.app.state.db.resumes.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _resume_out(doc)


@limiter.limit("60/minute")
@router.post("/interview-scores")
async def save_interview_scores(payload: InterviewScoresCreate, request: Request, user: dict = Depends(get_current_user)):
    # Scores may only be recorded for the authenticated candidate
    # (C2 forwards the candidate's own Authorization header).
    if payload.candidate_id != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Cannot record scores for another user")
    db = request.app.state.db
    doc = {
        "candidate_id": payload.candidate_id,
        "job_id": payload.job_id,
        "session_id": payload.session_id,
        "job_role": payload.job_role,
        "mcq_score": payload.mcq_score,
        "descriptive_score": payload.descriptive_score,
        "coding_score": payload.coding_score,
        "interview_score": payload.interview_score,
        "grade": payload.grade,
        "integrity_score": payload.integrity_score,
        "created_at": datetime.now(timezone.utc),
    }
    # Update or insert interview score
    query = {"candidate_id": payload.candidate_id}
    if payload.job_id:
        query["job_id"] = payload.job_id
    elif payload.session_id:
        query["session_id"] = payload.session_id
    
    await db.interview_scores.update_one(
        query,
        {"$set": doc},
        upsert=True
    )

    # Automatically synchronize application in db.applications
    if payload.job_id:
        from bson import ObjectId
        job_doc = None
        try:
            if ObjectId.is_valid(payload.job_id):
                job_doc = await db.jobs.find_one({"_id": ObjectId(payload.job_id)})
            if not job_doc:
                job_doc = await db.jobs.find_one({"_id": payload.job_id})
        except Exception:
            pass

        user_doc = None
        try:
            if ObjectId.is_valid(payload.candidate_id):
                user_doc = await db.users.find_one({"_id": ObjectId(payload.candidate_id)})
            if not user_doc:
                user_doc = await db.users.find_one({"_id": payload.candidate_id})
        except Exception:
            pass

        cand_name = user_doc.get("full_name") or user_doc.get("name") if user_doc else "Candidate"
        cand_email = user_doc.get("email", "") if user_doc else ""

        # Fetch candidate resume
        resume_doc = None
        try:
            if ObjectId.is_valid(payload.candidate_id):
                resume_doc = await db.resumes.find_one({"$or": [{"candidate_id": payload.candidate_id}, {"candidate_id": ObjectId(payload.candidate_id)}]}, sort=[("created_at", -1)])
            else:
                resume_doc = await db.resumes.find_one({"candidate_id": payload.candidate_id}, sort=[("created_at", -1)])
        except Exception:
            pass

        app_doc = {
            "job_id": str(payload.job_id),
            "candidate_id": str(payload.candidate_id),
            "candidate_name": cand_name,
            "candidate_email": cand_email,
            "resume_id": str(resume_doc["_id"]) if resume_doc else "",
            "job_title": job_doc.get("title", payload.job_role) if job_doc else payload.job_role,
            "company_id": str(job_doc.get("company_id", "")) if job_doc else "",
            "company_name": job_doc.get("company_name", "") if job_doc else "",
            "status": "interview_completed",
            "applied_at": datetime.now(timezone.utc),
            "interview_score": payload.interview_score,
            "mcq_score": payload.mcq_score,
            "descriptive_score": payload.descriptive_score,
            "coding_score": payload.coding_score,
            "grade": payload.grade,
        }
        await db.applications.update_one(
            {"candidate_id": str(payload.candidate_id), "job_id": str(payload.job_id)},
            {"$set": app_doc},
            upsert=True
        )

    return {"success": True}


@router.get("/interview-scores/{candidate_id}")
async def get_interview_scores(candidate_id: str, request: Request, user: dict = Depends(get_current_user)):
    db = request.app.state.db
    if str(user["_id"]) != str(candidate_id) and not await _can_company_view_candidate(db, str(user["_id"]), candidate_id):
        raise HTTPException(status_code=404, detail="No scores found")
    cursor = db.interview_scores.find({"candidate_id": candidate_id}).sort("created_at", -1)
    scores = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        scores.append(doc)
    return scores

@router.get("/interview-detail/{candidate_id}")
async def get_interview_detail(candidate_id: str, request: Request, user: dict = Depends(get_current_user)):
    db = request.app.state.db
    if str(user["_id"]) != str(candidate_id) and not await _can_company_view_candidate(db, str(user["_id"]), candidate_id):
        raise HTTPException(status_code=404, detail="No interview data found")
    cursor = db.results.find({"candidate_id": candidate_id}).sort("created_at", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


class MatchSyncPayload(BaseModel):
    candidate_id: Optional[str] = None
    job_id: Optional[str] = None
    role: Optional[str] = None
    cv_score: float
    skill_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None


@router.post("/sync-match")
async def sync_match_score(payload: MatchSyncPayload, request: Request, user: dict = Depends(get_current_user)):
    db = request.app.state.db
    from bson import ObjectId
    cand_id = payload.candidate_id or str(user.get("_id", ""))
    job_id = payload.job_id or ""

    update_data = {
        "cv_score": round(payload.cv_score, 1),
        "overall_score": round(payload.cv_score, 1),
    }
    if payload.skill_score is not None:
        update_data["skill_score"] = round(payload.skill_score, 1)
    if payload.experience_score is not None:
        update_data["experience_score"] = round(payload.experience_score, 1)
    if payload.education_score is not None:
        update_data["education_score"] = round(payload.education_score, 1)

    cand_filters = [{"candidate_id": cand_id}]
    if ObjectId.is_valid(cand_id):
        cand_filters.append({"candidate_id": ObjectId(cand_id)})

    if job_id:
        job_filters = [{"job_id": job_id}, {"job_id": str(job_id)}]
        if ObjectId.is_valid(job_id):
            job_filters.append({"job_id": ObjectId(job_id)})

        filter_q = {
            "$and": [
                {"$or": cand_filters},
                {"$or": job_filters}
            ]
        }
        await db.applications.update_many(filter_q, {"$set": update_data})
        await db.predictions.update_many(filter_q, {"$set": update_data})
    elif payload.role:
        await db.applications.update_many(
            {"$and": [{"$or": cand_filters}, {"$or": [{"job_title": payload.role}, {"job_role": payload.role}]}]},
            {"$set": update_data}
        )
        await db.predictions.update_many(
            {"$and": [{"$or": cand_filters}, {"$or": [{"predicted_role": payload.role}, {"job_role": payload.role}]}]},
            {"$set": update_data}
        )

    return {"success": True, "cv_score": payload.cv_score}

