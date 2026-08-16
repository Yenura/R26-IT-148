"""Pydantic schemas for Component 4 — with full field validation (M2 fix)"""

import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# ── Allowed values ─────────────────────────────────────────────────────────────
VALID_JOB_ROLES = {
    "Software Engineer", "Data Scientist", "Machine Learning Engineer",
    "Frontend Developer", "Backend Developer", "DevOps Engineer",
    "Cybersecurity Analyst", "Cloud Solutions Architect",
    "Database Administrator", "Mobile App Developer",
    "Full Stack Developer", "QA/Test Automation Engineer",
    "Data Engineer", "Site Reliability Engineer (SRE)",
    "UI/UX Designer", "Network Engineer",
    "Business/Systems Analyst", "AI/NLP Engineer",
    "Blockchain Developer", "Embedded Systems Engineer",
}
VALID_JOB_LEVELS = {"Intern", "Junior", "Mid-Level", "Senior", "Staff/Principal", "Lead", "Principal / Staff"}
VALID_WORK_MODES = {"On-Site", "Hybrid", "Remote"}


# ── Input schemas ──────────────────────────────────────────────────────────────

class SkillGapRequest(BaseModel):
    # Identity — strict pattern, no special chars that enable injection
    candidate_id:   str = Field(..., min_length=1, max_length=50)
    candidate_name: str = Field(..., min_length=2, max_length=100)

    # Role / position
    job_role:  str = "Software Engineer"
    job_level: Optional[str] = "Mid-Level"
    work_mode: Optional[str] = "Hybrid"

    # Experience / profile
    experience_years:     int           = Field(ge=0, le=50, default=2)
    education:            Optional[str] = "B.Sc. Computer Science"
    certifications:       Optional[str] = "None"
    certifications_count: Optional[int] = Field(ge=0, le=20, default=0)
    projects_count:       Optional[int] = Field(ge=0, le=100, default=0)

    # Skills
    skills: List[str] = Field(default_factory=list)

    # Scores from other components (0–100)
    cv_matching_score: Optional[float] = Field(None, ge=0, le=100)
    interview_score:   Optional[float] = Field(None, ge=0, le=100)
    mcq_score:         Optional[float] = Field(None, ge=0, le=100)
    descriptive_score: Optional[float] = Field(None, ge=0, le=100)
    coding_score:      Optional[float] = Field(None, ge=0, le=100)

    # Interview gap topics
    weak_topics:       Optional[List[str]] = []
    failed_mcq_topics: Optional[List[str]] = []

    # ── Validators ─────────────────────────────────────────────────────────────

    @field_validator("candidate_id")
    @classmethod
    def sanitise_candidate_id(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r'^[A-Za-z0-9\-_]+$', v):
            raise ValueError(
                "candidate_id may only contain letters, digits, hyphens, and underscores"
            )
        return v

    @field_validator("candidate_name")
    @classmethod
    def sanitise_candidate_name(cls, v: str) -> str:
        v = v.strip()
        # Remove MongoDB operator characters
        v = re.sub(r'[$.]', '', v)
        if not v:
            raise ValueError("candidate_name cannot be empty after sanitisation")
        return v

    @field_validator("job_role")
    @classmethod
    def validate_job_role(cls, v: str) -> str:
        if v not in VALID_JOB_ROLES:
            raise ValueError(
                f"Invalid job_role '{v}'. Valid options: {sorted(VALID_JOB_ROLES)}"
            )
        return v

    @field_validator("job_level")
    @classmethod
    def validate_job_level(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in VALID_JOB_LEVELS:
            raise ValueError(
                f"Invalid job_level '{v}'. Valid options: {sorted(VALID_JOB_LEVELS)}"
            )
        return v

    @field_validator("work_mode")
    @classmethod
    def validate_work_mode(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in VALID_WORK_MODES:
            raise ValueError(
                f"Invalid work_mode '{v}'. Valid options: {sorted(VALID_WORK_MODES)}"
            )
        return v

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v: List[str]) -> List[str]:
        cleaned = [s.strip() for s in v if s.strip()]
        if len(cleaned) > 60:
            raise ValueError("Maximum 60 skills allowed per candidate")
        return cleaned

    @field_validator("weak_topics", "failed_mcq_topics")
    @classmethod
    def validate_topic_lists(cls, v: Optional[List[str]]) -> List[str]:
        if v is None:
            return []
        return [t.strip() for t in v if t.strip()][:20]  # cap at 20


class ProgressUpdateRequest(BaseModel):
    candidate_id: str = Field(..., min_length=1, max_length=50)
    skill:        str = Field(..., min_length=1, max_length=100)
    status:       str = Field(..., pattern=r'^(not_started|in_progress|completed)$')
    notes:        Optional[str] = Field("", max_length=500)

    @field_validator("notes")
    @classmethod
    def sanitise_notes(cls, v: Optional[str]) -> str:
        return re.sub(r'[$.]', '', v or "").strip()


class CareerPathRequest(BaseModel):
    candidate_id:    str = Field(..., min_length=1, max_length=50)
    current_role:    str
    target_role:     Optional[str] = None
    skills:          List[str]
    experience_years: int = Field(ge=0, le=50, default=2)
    job_level:       Optional[str] = "Mid-Level"

    @field_validator("current_role")
    @classmethod
    def validate_current_role(cls, v: str) -> str:
        if v not in VALID_JOB_ROLES:
            raise ValueError(f"Invalid current_role. Must be one of: {sorted(VALID_JOB_ROLES)}")
        return v


# ── Output / Sub schemas ───────────────────────────────────────────────────────

class ResourceRec(BaseModel):
    skill:    str
    course:   str
    url:      str
    duration: str
    level:    str
    priority: str   # "Critical" | "High" | "Medium" | "Low"


class SkillNode(BaseModel):
    id:       str
    label:    str
    status:   str   # "has" | "missing_required" | "missing_optional"
    category: str


class SkillGapReport(BaseModel):
    candidate_id:            str
    candidate_name:          str
    job_role:                str
    job_level:               Optional[str]
    work_mode:               Optional[str]
    cv_matching_score:       Optional[float]
    interview_score:         Optional[float]
    skill_match_pct:         float
    gap_score:               float
    gap_severity:            str
    missing_required:        List[str]
    missing_optional:        List[str]
    present_skills:          List[str]
    technical_gaps:          List[str]
    ml_ai_gaps:              List[str]
    cloud_devops_gaps:       List[str]
    security_gaps:           List[str]
    data_gaps:               List[str]
    knowledge_gaps:          List[str]
    problem_solving_gaps:    List[str]
    resources:               List[ResourceRec]
    roadmap_nodes:           List[SkillNode]
    learning_plan:           List[Dict[str, Any]]
    career_path_suggestions: List[str]
    improvement_suggestions: List[str]
    predicted_hire:          bool
    hire_probability:        float
    analysis_timestamp:      datetime
    certifications_count:    Optional[int]
    projects_count:          Optional[int]


class ProgressRecord(BaseModel):
    candidate_id: str
    skill:        str
    status:       str
    notes:        str
    updated_at:   datetime
