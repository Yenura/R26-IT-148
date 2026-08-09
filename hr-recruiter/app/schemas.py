"""Pydantic schemas for the hr-recruiter API."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

ID_PATTERN = re.compile(r"^[A-Za-z0-9\-_]+$")


# ── Auth ───────────────────────────────────────────────────────────────────────

class RecruiterRegister(BaseModel):
    full_name:  str = Field(..., min_length=2, max_length=120)
    email:      str = Field(..., min_length=5, max_length=120)
    password:   str = Field(..., min_length=6, max_length=128)
    organization: Optional[str] = Field(None, max_length=120)

    @field_validator("email")
    @classmethod
    def valid_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email address")
        return v


class RecruiterLogin(BaseModel):
    email:    str = Field(..., min_length=5, max_length=120)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalise_email(cls, v: str) -> str:
        return v.strip().lower()


class RecruiterOut(BaseModel):
    id:            str
    full_name:     str
    email:         str
    organization:  Optional[str] = None
    created_at:    datetime


class Token(BaseModel):
    access_token: str
    token_type:   str = "bearer"


# ── Job postings ───────────────────────────────────────────────────────────────

JOB_STATUSES = {"open", "closed"}


class JobPostingCreate(BaseModel):
    title:          str = Field(..., min_length=2, max_length=200)
    description:    str = Field(..., min_length=5, max_length=5000)
    job_role:       str = Field(..., max_length=100)
    job_level:      str = Field(default="Mid-Level", max_length=40)
    work_mode:      str = Field(default="Hybrid", max_length=20)
    location:       Optional[str] = Field(None, max_length=120)
    skills_required: List[str] = Field(default_factory=list)
    status:         str = Field(default="open", max_length=10)

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in JOB_STATUSES:
            raise ValueError(f"status must be one of {sorted(JOB_STATUSES)}")
        return v

    @field_validator("skills_required")
    @classmethod
    def clean_skills(cls, v: List[str]) -> List[str]:
        return [s.strip() for s in v if s and s.strip()]


class JobPostingUpdate(BaseModel):
    title:            Optional[str] = Field(None, min_length=2, max_length=200)
    description:      Optional[str] = Field(None, min_length=5, max_length=5000)
    job_role:         Optional[str] = Field(None, max_length=100)
    job_level:        Optional[str] = Field(None, max_length=40)
    work_mode:        Optional[str] = Field(None, max_length=20)
    location:         Optional[str] = Field(None, max_length=120)
    skills_required:  Optional[List[str]] = None
    status:           Optional[str] = Field(None, max_length=10)

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        if v is not None:
            v = v.strip().lower()
            if v not in JOB_STATUSES:
                raise ValueError(f"status must be one of {sorted(JOB_STATUSES)}")
        return v

    @field_validator("skills_required")
    @classmethod
    def clean_skills(cls, v):
        if v is not None:
            return [s.strip() for s in v if s and s.strip()]
        return v


class JobPostingOut(BaseModel):
    id:             str
    recruiter_id:   str
    title:          str
    description:    str
    job_role:       str
    role_key:       str
    job_level:      str
    work_mode:      str
    location:       Optional[str] = None
    skills_required: List[str] = Field(default_factory=list)
    status:         str
    created_at:     datetime
    updated_at:     datetime


# ── Applications ───────────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    candidate_id:      str = Field(..., min_length=1, max_length=50)
    candidate_name:    str = Field(..., min_length=2, max_length=120)
    experience_years:  float = Field(ge=0, le=50, default=0)
    education:         Optional[str] = Field(None, max_length=150)
    skills:            List[str] = Field(default_factory=list)
    cv_matching_score: Optional[float] = Field(None, ge=0, le=100)
    mcq_score:         Optional[float] = Field(None, ge=0, le=100)
    descriptive_score: Optional[float] = Field(None, ge=0, le=100)
    coding_score:      Optional[float] = Field(None, ge=0, le=100)

    @field_validator("candidate_id")
    @classmethod
    def sanitise_candidate_id(cls, v: str) -> str:
        v = v.strip()
        if not ID_PATTERN.match(v):
            raise ValueError(
                "candidate_id may only contain letters, digits, hyphens, and underscores"
            )
        return v


class ApplicationOut(BaseModel):
    id:                 str
    job_id:             str
    candidate_id:       str
    candidate_name:     str
    experience_years:   float
    education:          Optional[str] = None
    skills:             List[str] = Field(default_factory=list)
    applied_at:         datetime


# ── Ranking ────────────────────────────────────────────────────────────────────

class RankedCandidate(BaseModel):
    rank:               int
    candidate_id:       str
    candidate_name:     str
    job_role:           str
    CSS:                float
    S_cv:               float
    S_int:              float
    S_edu:              float
    S_exp:              float
    S_skill:            float
    P_mcq:              float
    P_desc:             float
    P_code:             float
    passed_hard_filter: bool
    filter_fail_reason: str = ""
    hire_probability:   Optional[float] = None
    report_available:   bool = False


class RankedListResponse(BaseModel):
    job_id:     str
    job_title:  str
    job_role:   str
    total:      int
    candidates: List[RankedCandidate]
