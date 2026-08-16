"""Resume upload, parsing, NLP preprocessing, and semantic matching."""
import os
import re
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File

from schemas import ResumeOut, ResumeUpdate, PredictionOut
from routers.auth import get_current_user, require_company
from services.resume_parser import parse_resume_file, extract_entities
from services.semantic_matcher import SemanticMatcher
from services.role_classifier import RoleClassifier

router = APIRouter()

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
        education=doc.get("education", ""),
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
        id=str(doc["_id"]),
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


@router.get("/", response_model=list[ResumeOut])
async def list_resumes(request: Request, user: dict = Depends(get_current_user)):
    cursor = request.app.state.db.resumes.find({"candidate_id": str(user["_id"])}).sort("created_at", -1)
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
        resume_doc = await db.resumes.find_one({"_id": ObjectId(resume_id)})
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
async def match_resume(
    request: Request,
    resume_id: str = "",
    job_id: str = "",
    target_role: str = "",
    user: dict = Depends(get_current_user),
):
    db = request.app.state.db
    if resume_id:
        from bson import ObjectId
        resume_doc = await db.resumes.find_one({"_id": ObjectId(resume_id)})
    else:
        resume_doc = await db.resumes.find_one(
            {"candidate_id": str(user["_id"])},
            sort=[("created_at", -1)]
        )
    if not resume_doc:
        raise HTTPException(status_code=404, detail="No resume found")

    job_doc = None
    if job_id:
        from bson import ObjectId as Oid
        job_doc = await db.jobs.find_one({"_id": Oid(job_id)})

    resume_text = resume_doc.get("raw_text", "")
    resume_skills_lower = [s.strip().lower() for s in resume_doc.get("skills", [])]
    job_text = ""
    job_skills_original = []
    job_skills_lower = []
    required_years = 0

    if job_doc:
        job_text = f"{job_doc.get('title', '')} {job_doc.get('description', '')}"
        job_skills_original = job_doc.get("required_skills", [])
        job_skills_lower = [s.strip().lower() for s in job_skills_original]
        required_years = job_doc.get("experience_required", 0) or 0
    elif target_role and target_role in CANONICAL_ROLE_REQS:
        role_data = CANONICAL_ROLE_REQS[target_role]
        job_text = f"{target_role} required skills and experience"
        job_skills_original = role_data["skills"]
        job_skills_lower = [s.strip().lower() for s in job_skills_original]
        required_years = role_data["exp"]
    else:
        # Fallback to predicted role from classifier
        classifier = _get_classifier()
        p_role, _ = classifier.predict(resume_text, resume_doc.get("skills", []))
        role_data = CANONICAL_ROLE_REQS.get(p_role, CANONICAL_ROLE_REQS["Software Engineer"])
        job_text = f"{p_role} required skills"
        job_skills_original = role_data["skills"]
        job_skills_lower = [s.strip().lower() for s in job_skills_original]
        required_years = role_data["exp"]

    # Semantic: TF-IDF cosine similarity
    matcher = _get_matcher()
    semantic_score = matcher.compute_similarity(resume_text, job_text) if job_text else 0

    # Skill matching: exact case-insensitive match
    import re
    matched_original = []
    for orig, lower in zip(job_skills_original, job_skills_lower):
        if lower in resume_skills_lower:
            matched_original.append(orig)
    missing = [s for s in job_skills_original if s not in matched_original]
    extra = [s for s in resume_doc.get("skills", []) if s.lower() not in job_skills_lower]
    skill_score = len(matched_original) / len(job_skills_original) * 100 if job_skills_original else 0

    # Experience: ratio of candidate years to required, capped at 100
    exp_years = resume_doc.get("experience_years", 0) or 0
    if required_years > 0:
        experience_score = min(exp_years / required_years * 100, 100)
    elif exp_years > 0:
        experience_score = min(50 + exp_years * 5, 100)
    else:
        experience_score = 0

    # Education: detect level + field relevance
    edu = resume_doc.get("education", "").lower()
    if "phd" in edu or "doctorate" in edu or "ph.d" in edu:
        edu_level = 100
    elif "master" in edu or "m.sc" in edu or "m.sc." in edu or "mba" in edu or "mtech" in edu or "m.tech" in edu:
        edu_level = 85
    elif "bachelor" in edu or "b.sc" in edu or "b.sc." in edu or "b.tech" in edu or "btech" in edu or "b.e." in edu:
        edu_level = 70
    elif "diploma" in edu or "associate" in edu:
        edu_level = 50
    elif edu.strip():
        edu_level = 40
    else:
        edu_level = 0
    education_score = edu_level

    # Weighted overall: skills most important, then experience, then semantic, then education
    if job_doc:
        overall_score = 0.35 * skill_score + 0.25 * experience_score + 0.25 * semantic_score + 0.15 * education_score
    else:
        overall_score = 0.40 * semantic_score + 0.30 * skill_score + 0.20 * experience_score + 0.10 * education_score

    classifier = _get_classifier()
    predicted_role, confidence = classifier.predict(resume_text, resume_doc.get("skills", []))

    career_suggestions = []
    if missing:
        career_suggestions.append(f"Learn {', '.join(missing[:3])} to improve fit")
    if experience_score < 60:
        career_suggestions.append("Gain more hands-on experience")
    if education_score < 60:
        career_suggestions.append("Consider pursuing a higher degree")
    career_suggestions.append(f"Best suited role: {predicted_role}")

    now = datetime.now(timezone.utc)
    doc = {
        "resume_id": str(resume_doc["_id"]),
        "candidate_id": str(user["_id"]),
        "job_id": job_id,
        "predicted_role": predicted_role,
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
    result = await db.predictions.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _pred_out(doc)


@router.get("/{resume_id}", response_model=ResumeOut)
async def get_resume(resume_id: str, request: Request, user: dict = Depends(get_current_user)):
    from bson import ObjectId
    try:
        doc = await request.app.state.db.resumes.find_one({"_id": ObjectId(resume_id), "candidate_id": str(user["_id"])})
    except Exception:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found")
    return _resume_out(doc)


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


@router.post("/interview-scores")
async def save_interview_scores(payload: dict, request: Request, user: dict = Depends(require_company)):
    db = request.app.state.db
    candidate_id = payload.get("candidate_id", "")
    if not candidate_id:
        raise HTTPException(status_code=400, detail="candidate_id required")
    doc = {
        "candidate_id": candidate_id,
        "job_id": payload.get("job_id", ""),
        "session_id": payload.get("session_id", ""),
        "job_role": payload.get("job_role", ""),
        "mcq_score": payload.get("mcq_score", 0),
        "descriptive_score": payload.get("descriptive_score", 0),
        "coding_score": payload.get("coding_score", 0),
        "interview_score": payload.get("interview_score", 0),
        "grade": payload.get("grade", ""),
        "created_at": datetime.now(timezone.utc),
    }
    await db.interview_scores.insert_one(doc)
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
