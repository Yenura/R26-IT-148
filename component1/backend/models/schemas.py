"""Pydantic v2 schemas for Component 1 — Resume Screening & Role Matching
IT22094872 | Dulnith K.D. | R26-IT-148

Style mirrors component4/backend/models/schemas.py (pydantic v2, field_validator).
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data.role_requirements import ALL_ROLES

VALID_JOB_ROLES: set = set(ALL_ROLES)

# ── Helpers ────────────────────────────────────────────────────────────────────

_CANDIDATE_ID_RE = re.compile(r'^[A-Za-z0-9\-_]+$')


def _sanitise_candidate_id(v: str) -> str:
    v = v.strip()
    if not _CANDIDATE_ID_RE.match(v):
        raise ValueError(
            "candidate_id may only contain letters, digits, hyphens, and underscores"
        )
    return v


def _sanitise_text(v: str) -> str:
    return re.sub(r'[$.]', '', v).strip()


# ── Sub-models ─────────────────────────────────────────────────────────────────

class RoleAlternative(BaseModel):
    role:       str
    confidence: float = Field(..., ge=0.0, le=1.0)


# ── Request schemas ────────────────────────────────────────────────────────────

class CVTextRequest(BaseModel):
    """Analyze a CV supplied as raw text."""
    text:             str  = Field(..., min_length=10, description="Raw resume/CV text")
    candidate_id:     Optional[str] = Field(None, max_length=50)
    candidate_name:   Optional[str] = Field(None, max_length=100)
    job_description:  Optional[str] = Field(None, description="Job posting text for JD-matching")

    @field_validator("candidate_id")
    @classmethod
    def validate_candidate_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _sanitise_candidate_id(v)

    @field_validator("candidate_name")
    @classmethod
    def validate_candidate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = _sanitise_text(v)
        if not cleaned:
            raise ValueError("candidate_name cannot be empty after sanitisation")
        return cleaned

    @field_validator("text", "job_description")
    @classmethod
    def sanitise_text_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.strip()


class ClassifyRequest(BaseModel):
    """Classify a CV text into one of the 20 roles without persistence."""
    text: str = Field(..., min_length=10)

    @field_validator("text")
    @classmethod
    def clean_text(cls, v: str) -> str:
        return v.strip()


class BatchCandidateItem(BaseModel):
    """A single candidate in a batch ranking request."""
    candidate_id:   Optional[str] = Field(None, max_length=50)
    candidate_name: Optional[str] = Field(None, max_length=100)
    text:           str           = Field(..., min_length=10, description="CV text")

    @field_validator("candidate_id")
    @classmethod
    def validate_candidate_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _sanitise_candidate_id(v)


class BatchRankRequest(BaseModel):
    """Batch ranking: given a JD + multiple CVs, return ranked results."""
    job_description: str                    = Field(..., min_length=10)
    candidates:      List[BatchCandidateItem] = Field(..., min_length=1, max_length=100)


# ── Response schemas ───────────────────────────────────────────────────────────

class CVAnalysisResponse(BaseModel):
    """Full CV analysis result — the canonical output contract for Component 1."""
    candidate_id:         str
    candidate_name:       str

    # Role classification
    job_role:             str
    role_confidence:      float = Field(..., ge=0.0, le=1.0)
    role_alternatives:    List[RoleAlternative]

    # Parsed CV fields
    education:            str
    edu_level:            int   = Field(..., ge=1, le=4)
    edu_relevance:        float = Field(..., ge=0.0, le=1.0)
    experience_years:     float = Field(..., ge=0.0)
    skills:               List[str]

    # Scores (mirrors CandidateFeatures in component3/engine/css_engine.py)
    S_edu:                float = Field(..., ge=0.0, le=1.0)
    S_exp:                float = Field(..., ge=0.0, le=1.0)
    S_skill:              float = Field(..., ge=0.0, le=1.0)
    skill_score_raw:      float = Field(..., ge=0.0, le=1.0)   # alias for S_skill; consumed by Component 3

    jd_similarity_score:  Optional[float] = Field(None, ge=0.0, le=1.0)
    cv_matching_score:    float = Field(..., ge=0.0, le=100.0)

    analysis_timestamp:   datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ClassifyResponse(BaseModel):
    job_role:          str
    role_confidence:   float
    role_alternatives: List[RoleAlternative]


class BatchRankItem(BaseModel):
    rank:                 int
    candidate_id:         str
    candidate_name:       str
    job_role:             str
    role_confidence:      float
    cv_matching_score:    float
    jd_similarity_score:  Optional[float]
    S_edu:                float
    S_exp:                float
    S_skill:              float
    skill_score_raw:      float


class BatchRankResponse(BaseModel):
    job_description_snippet: str
    total_candidates:        int
    ranked_candidates:       List[BatchRankItem]


class RoleInfo(BaseModel):
    role:            str
    required_skills: List[str]
    required_years:  float


class RolesListResponse(BaseModel):
    total: int
    roles: List[RoleInfo]


class PaginatedCVList(BaseModel):
    total:  int
    skip:   int
    limit:  int
    items:  List[Dict[str, Any]]


class DeleteResponse(BaseModel):
    deleted:      bool
    candidate_id: str
    message:      str
