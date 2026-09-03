"""Resume upload, parsing, NLP preprocessing, and semantic matching."""
import os
import re
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from slowapi import Limiter
from slowapi.util import get_remote_address

from schemas import ResumeOut, ResumeUpdate, PredictionOut, InterviewScoresCreate
from routers.auth import get_current_user, require_company, require_candidate
from services.resume_parser import parse_resume_file, extract_entities
from services.semantic_matcher import SemanticMatcher
from services.role_classifier import RoleClassifier

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

_matcher: SemanticMatcher | None = None
_classifier: RoleClassifier | None = None


def _get_matcher() -> SemanticMatcher:
    global _matcher
    if _matcher is None:
        _matcher = SemanticMatcher()
    return _matcher


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
async def list_resumes(request: Request, user: dict = Depends(get_current_user)):
    db = request.app.state.db
    if user.get("role") == "company":
        cursor = db.resumes.find().sort("created_at", -1).limit(100)
    else:
        cursor = db.resumes.find({"candidate_id": str(user["_id"])}).sort("created_at", -1)
        results = [_resume_out(doc) async for doc in cursor]
        return results
    return [_resume_out(doc) async for doc in cursor]


@router.get("/predictions", response_model=list[PredictionOut])
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
        resume_doc = await db.resumes.find_one({"_id": ObjectId(resume_id), "candidate_id": str(user["_id"])})
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
            if not resume_doc:
                resume_doc = await db.resumes.find_one({"_id": ObjectId(resume_id)})
        except Exception:
            pass

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
        resume_doc = await db.resumes.find_one({}, sort=[("created_at", -1)])
    if not resume_doc:
        resume_doc = {
            "_id": "default_resume",
            "candidate_id": str(user.get("_id", "candidate_1")),
            "candidate_name": user.get("name", "Applicant"),
            "skills": ["Python", "React", "JavaScript", "SQL", "Git", "Docker"],
            "experience_years": 3.0,
            "education": "BSc Computer Science",
            "raw_text": "Experienced Software Engineer with proficiency in Python, React, JavaScript, SQL, Git, and Docker."
        }

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
    job_text = ""
    job_skills_original = []
    job_skills_lower = []
    required_years = 0.0

    if job_doc:
        job_text = f"{job_doc.get('title', '')} {job_doc.get('description', '')}"
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
        job_text = f"{target_role} required skills and experience"
        job_skills_original = role_data["skills"]
        job_skills_lower = [s.strip().lower() for s in job_skills_original]
        required_years = float(role_data["exp"])
    else:
        # Fallback to predicted role from classifier
        classifier = _get_classifier()
        p_role, _ = classifier.predict(resume_text, cand_skills_raw)
        matched_target = target_role if (target_role and target_role in CANONICAL_ROLE_REQS) else p_role
        role_data = CANONICAL_ROLE_REQS.get(matched_target, CANONICAL_ROLE_REQS.get("Software Engineer", {"skills": ["Python", "SQL", "Git"], "exp": 2}))
        job_text = f"{matched_target} required skills"
        job_skills_original = role_data["skills"]
        job_skills_lower = [s.strip().lower() for s in job_skills_original]
        required_years = float(role_data["exp"])

    # Semantic: TF-IDF cosine similarity
    matcher = _get_matcher()
    semantic_score = matcher.compute_similarity(resume_text, job_text) if job_text else 0

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

    if required_years > 0:
        experience_score = min(exp_years / required_years * 100, 100)
    elif exp_years > 0:
        experience_score = min(50 + exp_years * 5, 100)
    else:
        experience_score = 75.0

    # Education: detect level + field relevance
    edu = str(resume_doc.get("education", "")).lower()
    if "phd" in edu or "doctorate" in edu or "ph.d" in edu:
        edu_level = 100
    elif "master" in edu or "m.sc" in edu or "m.sc." in edu or "mba" in edu or "mtech" in edu or "m.tech" in edu:
        edu_level = 85
    elif "bachelor" in edu or "b.sc" in edu or "b.sc." in edu or "b.tech" in edu or "btech" in edu or "b.e." in edu or "degree" in edu:
        edu_level = 75
    elif "diploma" in edu or "associate" in edu:
        edu_level = 60
    elif edu.strip():
        edu_level = 50
    else:
        edu_level = 70
    education_score = float(edu_level)

    # Weighted overall: 3-pillar formula 50% Skills + 30% Experience + 20% Education
    overall_score = round(0.50 * skill_score + 0.30 * experience_score + 0.20 * education_score, 2)

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

    match_target_key = job_id or target_role or ""
    now = datetime.now(timezone.utc)
    res_id_str = str(resume_doc.get("_id", "demo_resume_01"))

    doc = {
        "resume_id": res_id_str,
        "candidate_id": str(user["_id"]),
        "job_id": match_target_key,
        "predicted_role": final_predicted,
        "role_confidence": round(confidence, 4),
        "semantic_score": round(semantic_score, 2),
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

    try:
        await db.predictions.update_one(
            {"resume_id": res_id_str, "job_id": match_target_key},
            {"$set": doc},
            upsert=True
        )
        if job_id and job_doc:
            await db.applications.update_one(
                {"candidate_id": str(user["_id"]), "job_id": str(job_id)},
                {"$set": {
                    "job_id": str(job_id),
                    "candidate_id": str(user["_id"]),
                    "candidate_name": user.get("full_name") or user.get("name") or "Candidate",
                    "candidate_email": user.get("email", ""),
                    "resume_id": res_id_str,
                    "job_title": job_doc.get("title", ""),
                    "company_id": str(job_doc.get("company_id", "")),
                    "company_name": job_doc.get("company_name", ""),
                    "cv_score": round(overall_score, 2),
                    "overall_score": round(overall_score, 2),
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
        if not doc:
            doc = await request.app.state.db.resumes.find_one({"_id": ObjectId(resume_id)})
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
    doc = await db.resumes.find_one({"_id": ObjectId(resume_id), "candidate_id": str(user["_id"])})
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
    doc = await db.resumes.find_one({"_id": ObjectId(resume_id), "candidate_id": str(user["_id"])})
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
async def save_interview_scores(payload: InterviewScoresCreate, request: Request):
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
        "mcq_total": payload.mcq_total,
        "descriptive_total": payload.descriptive_total,
        "coding_total": payload.coding_total,
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
    cursor = db.interview_scores.find({"candidate_id": candidate_id}).sort("created_at", -1)
    scores = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        scores.append(doc)
    return scores

@router.get("/interview-detail/{candidate_id}")
async def get_interview_detail(candidate_id: str, request: Request, user: dict = Depends(get_current_user)):
    db = request.app.state.db
    cursor = db.results.find({"candidate_id": candidate_id}).sort("created_at", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results
