"""Pydantic schemas for auth, resume, jobs, export."""
from datetime import datetime
from pydantic import BaseModel, Field


# ── Auth ────────────────────────────────────────────────────────
class CompanyRegister(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)
    industry: str = ""
    website: str = ""


class CandidateRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = ""
    user_id: str = ""


class UserOut(BaseModel):
    id: str
    email: str
    role: str
    name: str = ""
    company_name: str = ""
    industry: str = ""
    website: str = ""
    avatar_url: str = ""
    created_at: datetime | None = None


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    company_name: str | None = None
    industry: str | None = None
    website: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


# ── Jobs ────────────────────────────────────────────────────────
class JobCreate(BaseModel):
    title: str = Field(..., min_length=2)
    department: str = ""
    employment_type: str = "Full-time"
    location: str = ""
    experience_required: int = 0
    education_required: str = ""
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    description: str = ""
    responsibilities: str = ""
    salary_range: str = ""
    status: str = "open"
    interview_required: bool = False
    interview_question_count: int = Field(default=10, ge=3, le=30)


class JobUpdate(BaseModel):
    title: str | None = None
    department: str | None = None
    employment_type: str | None = None
    location: str | None = None
    experience_required: int | None = None
    education_required: str | None = None
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None
    description: str | None = None
    responsibilities: str | None = None
    salary_range: str | None = None
    status: str | None = None
    interview_required: bool | None = None
    interview_question_count: int | None = None


class JobOut(BaseModel):
    id: str
    company_id: str
    company_name: str = ""
    title: str
    department: str = ""
    employment_type: str = ""
    location: str = ""
    experience_required: int = 0
    education_required: str = ""
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    description: str = ""
    responsibilities: str = ""
    salary_range: str = ""
    status: str = "open"
    interview_required: bool = False
    interview_question_count: int = 10
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ── Resume ──────────────────────────────────────────────────────
class ResumeOut(BaseModel):
    id: str
    candidate_id: str
    filename: str = ""
    candidate_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    linkedin: str = ""
    github: str = ""
    skills: list[str] = []
    education: str = ""
    experience_years: float = 0
    projects: list[str] = []
    academic_projects: list[dict] = []
    personal_projects: list[dict] = []
    project_experience_years: float = 0
    certifications: list[str] = []
    languages: list[str] = []
    tools: list[str] = []
    frameworks: list[str] = []
    raw_text: str = ""
    created_at: datetime | None = None


class PredictionOut(BaseModel):
    id: str
    resume_id: str
    candidate_id: str
    job_id: str = ""
    predicted_role: str = ""
    role_confidence: float = 0
    semantic_score: float = 0
    skill_score: float = 0
    experience_score: float = 0
    education_score: float = 0
    overall_score: float = 0
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    extra_skills: list[str] = []
    career_suggestions: list[str] = []
    created_at: datetime | None = None


class ApplicationOut(BaseModel):
    id: str
    job_id: str
    candidate_id: str
    candidate_name: str = ""
    resume_id: str = ""
    status: str = "applied"
    applied_at: datetime | None = None


class ApplicationCreate(BaseModel):
    candidate_id: str
    candidate_name: str = ""
    resume_id: str = ""


class ResumeUpdate(BaseModel):
    candidate_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    linkedin: str | None = None
    github: str | None = None
    skills: list[str] | None = None
    education: str | None = None
    experience_years: float | None = None
    projects: list[str] | None = None
    academic_projects: list[dict] | None = None
    personal_projects: list[dict] | None = None
    project_experience_years: float | None = None
    certifications: list[str] | None = None
    languages: list[str] | None = None
    tools: list[str] | None = None
    frameworks: list[str] | None = None
