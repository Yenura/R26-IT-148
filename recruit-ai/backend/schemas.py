"""Pydantic schemas for auth, resume, jobs, export."""
import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ── Email hygiene ───────────────────────────────────────────────────
# Format is enforced everywhere an email is collected; deliverability
# (disposable block + MX lookup) only at registration so login and
# password-reset can never lock out — or enumerate — existing users.
_DISPOSABLE_DOMAINS = frozenset({
    "mailinator.com", "guerrillamail.com", "guerrillamail.org", "10minutemail.com",
    "10minutemail.net", "tempmail.com", "temp-mail.org", "throwawaymail.com",
    "yopmail.com", "yopmail.fr", "yopmail.net", "sharklasers.com", "grr.la",
    "guerrillamailblock.com", "pokemail.net", "spam4.me", "dispostable.com",
    "maildrop.cc", "harakirimail.com", "trashmail.com", "trashmail.net",
    "trashmail.org", "wegwerfmail.de", "wegwerfmail.net", "wegwerfmail.org",
    "getnada.com", "nada.ltd", "mohmal.com", "emailondeck.com", "fakeinbox.com",
    "mailnesia.com", "mintemail.com", "mytemp.email", "tempail.com", "tmpmail.org",
    "moakt.com", "tmail.ws", "dropmail.me", "emailfake.com", "fakemail.net",
    "inboxkitten.com", "spamgourmet.com", "33mail.com", "e4ward.com",
})

_EMAIL_RE = re.compile(r'^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$')


def check_email_format(v: str) -> str:
    v = v.strip().lower()
    if len(v) > 254:
        raise ValueError("Email is too long")
    if not _EMAIL_RE.match(v):
        raise ValueError("Invalid email format")
    local, _, domain = v.partition("@")
    if not local or local.startswith(".") or local.endswith(".") or ".." in local:
        raise ValueError("Invalid email format")
    if not domain or ".." in domain or domain[0] in ".-" or domain[-1] in ".-":
        raise ValueError("Invalid email format")
    return v


def check_email_domain(v: str) -> str:
    """Block disposable domains and verify the domain accepts mail (MX/A).
    Fails open when DNS itself is unreachable so registration stays available."""
    domain = v.partition("@")[2]
    if domain in _DISPOSABLE_DOMAINS:
        raise ValueError("Disposable email addresses are not allowed")
    try:
        import dns.resolver
        import dns.exception
        try:
            answers = dns.resolver.resolve(domain, "MX", lifetime=5)
            if len(answers) > 0:
                return v
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
        try:
            answers = dns.resolver.resolve(domain, "A", lifetime=5)
            if len(answers) > 0:
                return v
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
        raise ValueError("Email domain does not accept mail")
    except ValueError:
        raise
    except Exception:
        return v


def check_website(v: str) -> str:
    v = (v or "").strip()
    if v and not re.match(r'^https?://[^\s/$.?#].[^\s]*$', v, re.IGNORECASE):
        raise ValueError("Website must start with http:// or https://")
    return v


# ── Auth ────────────────────────────────────────────────────────
class CompanyRegister(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200)
    email: str = Field(..., min_length=5, max_length=200)
    password: str = Field(..., min_length=6, max_length=200)
    industry: str = Field(default="", max_length=200)
    website: str = Field(default="", max_length=500)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return check_email_domain(check_email_format(v))

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: str) -> str:
        return check_website(v)


class CandidateRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    email: str = Field(..., min_length=5, max_length=200)
    password: str = Field(..., min_length=6, max_length=200)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return check_email_domain(check_email_format(v))


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=200)
    password: str = Field(..., max_length=200)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return check_email_format(v)


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

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return check_website(v)


class PasswordChange(BaseModel):
    current_password: str = Field(..., max_length=200)
    new_password: str = Field(..., min_length=6, max_length=200)


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., max_length=200)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return check_email_format(v)


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=20, max_length=200)
    new_password: str = Field(..., min_length=6, max_length=200)


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
    interview_mcq_count: int = 4
    interview_desc_count: int = 3
    interview_coding_count: int = 3
    interview_mcq_time: int = 60
    interview_desc_time: int = 300
    interview_coding_time: int = 600
    interview_total_time: int = 60

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

    @field_validator("interview_mcq_count", mode="before")
    @classmethod
    def parse_mcq_count(cls, v):
        if v is None or v == "":
            return 4
        try:
            return max(0, min(30, int(v)))
        except (ValueError, TypeError):
            return 4

    @field_validator("interview_desc_count", mode="before")
    @classmethod
    def parse_desc_count(cls, v):
        if v is None or v == "":
            return 3
        try:
            return max(0, min(30, int(v)))
        except (ValueError, TypeError):
            return 3

    @field_validator("interview_coding_count", mode="before")
    @classmethod
    def parse_coding_count(cls, v):
        if v is None or v == "":
            return 3
        try:
            return max(0, min(30, int(v)))
        except (ValueError, TypeError):
            return 3

    @field_validator("interview_mcq_time", mode="before")
    @classmethod
    def parse_mcq_time(cls, v):
        if v is None or v == "":
            return 60
        try:
            return max(10, min(300, int(v)))
        except (ValueError, TypeError):
            return 60

    @field_validator("interview_desc_time", mode="before")
    @classmethod
    def parse_desc_time(cls, v):
        if v is None or v == "":
            return 300
        try:
            return max(30, min(900, int(v)))
        except (ValueError, TypeError):
            return 300

    @field_validator("interview_coding_time", mode="before")
    @classmethod
    def parse_coding_time(cls, v):
        if v is None or v == "":
            return 600
        try:
            return max(60, min(1800, int(v)))
        except (ValueError, TypeError):
            return 600

    @field_validator("interview_total_time", mode="before")
    @classmethod
    def parse_total_time(cls, v):
        if v is None or v == "":
            return 60
        try:
            return max(10, min(180, int(v)))
        except (ValueError, TypeError):
            return 60


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=300)
    job_role: str | None = Field(default=None, max_length=200)
    job_level: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=200)
    employment_type: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=200)
    experience_required: int | None = None
    education_required: str | None = Field(default=None, max_length=200)
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None
    description: str | None = Field(default=None, max_length=10000)
    responsibilities: str | None = Field(default=None, max_length=10000)
    salary_range: str | None = Field(default=None, max_length=100)
    status: str | None = Field(default=None, max_length=20)
    interview_required: bool | None = None
    interview_question_count: int | None = None
    interview_mcq_count: int | None = None
    interview_desc_count: int | None = None
    interview_coding_count: int | None = None
    interview_mcq_time: int | None = None
    interview_desc_time: int | None = None
    interview_coding_time: int | None = None
    interview_total_time: int | None = None

    @field_validator("interview_question_count", mode="before")
    @classmethod
    def parse_iq_count(cls, v):
        if v is None or v == "":
            return None
        try:
            return max(3, min(30, int(v)))
        except (ValueError, TypeError):
            return None

    @field_validator("interview_mcq_count", mode="before")
    @classmethod
    def parse_mcq_count(cls, v):
        if v is None or v == "":
            return None
        try:
            return max(0, min(30, int(v)))
        except (ValueError, TypeError):
            return None

    @field_validator("interview_desc_count", mode="before")
    @classmethod
    def parse_desc_count(cls, v):
        if v is None or v == "":
            return None
        try:
            return max(0, min(30, int(v)))
        except (ValueError, TypeError):
            return None

    @field_validator("interview_coding_count", mode="before")
    @classmethod
    def parse_coding_count(cls, v):
        if v is None or v == "":
            return None
        try:
            return max(0, min(30, int(v)))
        except (ValueError, TypeError):
            return None

    @field_validator("interview_mcq_time", mode="before")
    @classmethod
    def parse_mcq_time(cls, v):
        if v is None or v == "":
            return None
        try:
            return max(10, min(300, int(v)))
        except (ValueError, TypeError):
            return None

    @field_validator("interview_desc_time", mode="before")
    @classmethod
    def parse_desc_time(cls, v):
        if v is None or v == "":
            return None
        try:
            return max(30, min(900, int(v)))
        except (ValueError, TypeError):
            return None

    @field_validator("interview_coding_time", mode="before")
    @classmethod
    def parse_coding_time(cls, v):
        if v is None or v == "":
            return None
        try:
            return max(60, min(1800, int(v)))
        except (ValueError, TypeError):
            return None

    @field_validator("interview_total_time", mode="before")
    @classmethod
    def parse_total_time(cls, v):
        if v is None or v == "":
            return None
        try:
            return max(10, min(180, int(v)))
        except (ValueError, TypeError):
            return None


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
    interview_mcq_count: int = 4
    interview_desc_count: int = 3
    interview_coding_count: int = 3
    interview_mcq_time: int = 60
    interview_desc_time: int = 300
    interview_coding_time: int = 600
    interview_total_time: int = 60
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
    target_role: str = ""
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
    candidate_email: str = ""
    resume_id: str = ""
    status: str = "applied"
    applied_at: datetime | None = None
    interview_score: float | None = None
    cv_score: float | None = None
    overall_score: float | None = None
    hire_probability: float | None = None
    integrity_score: float | None = None
    integrity_adjusted: bool = False
    skills: list[str] = []


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
    integrity_score: int | None = Field(default=None, ge=0, le=100)
