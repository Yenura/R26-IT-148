"""Pydantic schemas for auth, resume, jobs, export."""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ── Auth ────────────────────────────────────────────────────────
class CompanyRegister(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200)
    email: str = Field(..., min_length=5, max_length=200)
    password: str = Field(..., min_length=6, max_length=200)
    industry: str = Field(default="", max_length=200)
    website: str = Field(default="", max_length=500)


class CandidateRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    email: str = Field(..., min_length=5, max_length=200)
    password: str = Field(..., min_length=6, max_length=200)


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=200)
    password: str = Field(..., max_length=200)


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
    full_name: str | None = Field(default=None, max_length=200)
    company_name: str | None = Field(default=None, max_length=200)
    industry: str | None = Field(default=None, max_length=200)
    website: str | None = Field(default=None, max_length=500)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


# ── Jobs ────────────────────────────────────────────────────────
class JobCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=300)
    job_role: str = Field(default="", max_length=200)
    job_level: str = Field(default="", max_length=100)
    department: str = Field(default="", max_length=200)
    employment_type: str = Field(default="Full-time", max_length=50)
    location: str = Field(default="", max_length=200)
    experience_required: int = 0
    education_required: str = Field(default="", max_length=200)
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    description: str = Field(default="", max_length=10000)
    responsibilities: str = Field(default="", max_length=10000)
    salary_range: str = Field(default="", max_length=100)
    status: str = Field(default="open", max_length=20)
    interview_required: bool = False
    interview_question_count: int = 10

    @field_validator("experience_required", mode="before")
    @classmethod
    def parse_exp(cls, v):
        if v is None or v == "":
            return 0
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0

    @field_validator("interview_question_count", mode="before")
    @classmethod
    def parse_iq_count(cls, v):
        if v is None or v == "":
            return 10
        try:
            return max(3, min(30, int(v)))
        except (ValueError, TypeError):
            return 10


class JobUpdate(BaseModel):
    title: str | None = None
    job_role: str | None = None
    job_level: str | None = None
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
    job_role: str = ""
    job_level: str = ""
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
    candidate_id: str = Field(..., min_length=1, max_length=100)
    candidate_name: str = Field(default="", max_length=200)
    resume_id: str = Field(default="", max_length=100)


class ResumeUpdate(BaseModel):
    candidate_name: str | None = Field(default=None, max_length=200)
    email: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)
    linkedin: str | None = Field(default=None, max_length=500)
    github: str | None = Field(default=None, max_length=500)
    skills: list[str] | None = None
    education: str | None = Field(default=None, max_length=500)
    experience_years: float | None = None
    projects: list[str] | None = None
    academic_projects: list[dict] | None = None
    personal_projects: list[dict] | None = None
    project_experience_years: float | None = None
    certifications: list[str] | None = None
    languages: list[str] | None = None
    tools: list[str] | None = None
    frameworks: list[str] | None = None


# ── Interview Scores ─────────────────────────────────────────────
class InterviewScoresCreate(BaseModel):
    candidate_id: str = Field(..., min_length=1, max_length=100)
    job_id: str = Field(default="", max_length=100)
    session_id: str = Field(default="", max_length=200)
    job_role: str = Field(default="", max_length=200)
    mcq_score: float = Field(default=0, ge=0, le=100)
    descriptive_score: float = Field(default=0, ge=0, le=100)
    coding_score: float = Field(default=0, ge=0, le=100)
    interview_score: float = Field(default=0, ge=0, le=100)
    grade: str = Field(default="", max_length=10)
