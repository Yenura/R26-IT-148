"""Pydantic v2 schemas for Component 1 — Resume Screening & Role Matching
IT22094872 | Dulnith K.D. | R26-IT-148

Style mirrors component4/backend/models/schemas.py (pydantic v2, field_validator).
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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
    cleaned = re.sub(r'[$.]', '', str(v or "")).strip()
    return cleaned or "Candidate"


# ── Sub-models ─────────────────────────────────────────────────────────────────

class RoleAlternative(BaseModel):
    role:        str
    confidence:  float = Field(default=0.0, ge=0.0, le=1.0)
    probability: Optional[float] = None


# ── Request schemas ────────────────────────────────────────────────────────────

class CVTextRequest(BaseModel):
    """Analyze a CV supplied as raw text."""
    text:             str           = Field(default="", min_length=10, description="Raw resume/CV text")
    resume_text:      Optional[str] = Field(None, description="Alternative field name for raw resume text")
    raw_text:         Optional[str] = Field(None, description="Alternative field name for raw resume text")
    cv_text:          Optional[str] = Field(None, description="Alternative field name for raw resume text")
    candidate_id:     Optional[str] = Field(None, max_length=50)
    candidate_name:   Optional[str] = Field(None, max_length=100)
    job_description:  Optional[str] = Field(None, description="Job posting text for JD-matching")
    target_role:      Optional[str] = Field(None, description="Target job role for requirements scoring")
    job_role:         Optional[str] = Field(None, description="Alternative field name for target role")

    @model_validator(mode="before")
    @classmethod
    def resolve_text_field(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("text"):
                data["text"] = data.get("raw_text") or data.get("resume_text") or data.get("cv_text") or ""
            if not data.get("target_role") and data.get("job_role"):
                data["target_role"] = data["job_role"]
        return data

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


class Component1ScoresModel(BaseModel):
    S_skill: float = Field(..., ge=0.0, le=100.0)
    S_exp:   float = Field(..., ge=0.0, le=100.0)
    S_edu:   float = Field(..., ge=0.0, le=100.0)


class SkillAnalysisModel(BaseModel):
    matched_count: int
    required_count: int
    percentage: float
    matched_skills: List[str]
    missing_skills: List[str]
    matched_preferred_skills: Optional[List[str]] = None
    related_skills: Optional[List[str]] = None
    evidence_breakdown: Optional[Dict[str, Any]] = None


class ExperienceAnalysisModel(BaseModel):
    candidate_years: float
    required_years: float
    relevant_years: float
    score: float
    total_professional_experience_months: Optional[float] = None
    it_sector_experience_months: Optional[float] = None
    target_role_relevant_experience_months: Optional[float] = None
    it_experience_years: Optional[float] = None
    total_experience_years: Optional[float] = None
    candidate_seniority: Optional[str] = "Mid"
    target_seniority: Optional[str] = "Mid"
    seniority_fit: Optional[str] = "MATCH"
    seniority_evidence: Optional[List[str]] = None
    employment_records: Optional[List[Dict[str, Any]]] = None


class EducationAnalysisModel(BaseModel):
    candidate_education: List[str]
    required_education: List[str]
    education_match: str
    score: float
    degree_level: Optional[str] = "BSc"
    degree_field: Optional[str] = "General IT"
    field_relevance: Optional[str] = "HIGH"
    education_relevance_score: Optional[float] = None
    relevant_certifications: Optional[List[Dict[str, Any]]] = None
    verified_certifications: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None



class JobRequirementSpec(BaseModel):
    job_id: str = "JOB001"
    company: Optional[str] = "Company Inc."
    position: Optional[str] = "Software Engineer"
    required_skills: Optional[List[Any]] = None
    required_experience_years: Optional[float] = 3.0
    required_education: Optional[List[str]] = None


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
    """Batch ranking: given a JD or job_id + multiple CVs, return ranked results."""
    job_id:          Optional[str] = Field(None)
    job_description: Optional[str] = Field(None)
    job_spec:        Optional[JobRequirementSpec] = Field(None)
    candidates:      List[BatchCandidateItem] = Field(..., min_length=1, max_length=100)


# ── Response schemas ───────────────────────────────────────────────────────────

class CVAnalysisResponse(BaseModel):
    """Full CV analysis result — the canonical output contract for Component 1."""
    candidate_id:         str
    candidate_name:       str
    job_id:               Optional[str] = "JOB001"

    # Role classification
    job_role:             str
    role_confidence:      float = Field(..., ge=0.0, le=1.0)
    role_alternatives:    List[RoleAlternative]
    manual_review_recommended: bool = False
    review_reason:        Optional[str] = None

    # Parsed CV fields
    education:            str
    edu_level:            int   = Field(..., ge=1, le=4)
    edu_relevance:        float = Field(..., ge=0.0, le=1.0)
    experience_years:     float = Field(..., ge=0.0)
    skills:               List[str]
    skill_evidence:       Optional[Dict[str, Any]] = None

    # Three Independent Scores for Component 3 (0-100)
    component_1_scores:   Component1ScoresModel
    S_skill:              float = Field(..., ge=0.0, le=100.0)
    S_exp:                float = Field(..., ge=0.0, le=100.0)
    S_edu:                float = Field(..., ge=0.0, le=100.0)

    # Lowercase aliases for client compatibility
    s_skill:              Optional[float] = Field(None, ge=0.0, le=100.0)
    s_exp:                Optional[float] = Field(None, ge=0.0, le=100.0)
    s_edu:                Optional[float] = Field(None, ge=0.0, le=100.0)

    @model_validator(mode="before")
    @classmethod
    def populate_score_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for k in ("skill", "exp", "edu"):
                cap_k = f"S_{k}"
                low_k = f"s_{k}"
                if cap_k in data and low_k not in data:
                    data[low_k] = data[cap_k]
                elif low_k in data and cap_k not in data:
                    data[cap_k] = data[low_k]
        return data

    # Detailed Analysis Breakdowns
    skill_analysis:       SkillAnalysisModel
    experience_analysis:  ExperienceAnalysisModel
    education_analysis:   EducationAnalysisModel

    # Legacy & raw aliases for backward compatibility
    skill_score_raw:      float = Field(..., ge=0.0, le=1.0)   # 0-1 alias for Component 3 compatibility
    jd_similarity_score:  Optional[float] = Field(None, ge=0.0, le=1.0)
    optional_legacy_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    cv_matching_score:    float = Field(..., ge=0.0, le=100.0)
    role_relevant_experience_years: Optional[float] = None
    detected_seniority:   Optional[str] = None
    detected_certs:       Optional[List[str]] = None
    verified_certifications: Optional[List[Dict[str, Any]]] = None
    projects:             Optional[List[Dict[str, Any]]] = None
    employment_records:   Optional[List[Dict[str, Any]]] = None
    target_job_profile:   Optional[Dict[str, Any]] = None
    cross_evidence_validation: Optional[Dict[str, Any]] = None
    overall_analysis_confidence: Optional[float] = None
    status:               str = "READY_FOR_COMPONENT_3"
    analysis_timestamp:   datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ClassifyResponse(BaseModel):
    job_role:                  str
    role_confidence:           float
    role_alternatives:         List[RoleAlternative]
    manual_review_recommended: bool = False
    review_reason:             Optional[str] = None


class BatchRankItem(BaseModel):
    rank:                 int
    candidate_id:         str
    candidate_name:       str
    job_role:             str
    role_confidence:      float
    component_1_scores:   Component1ScoresModel
    S_skill:              float
    S_exp:                float
    S_edu:                float
    skill_analysis:       SkillAnalysisModel
    experience_analysis:  ExperienceAnalysisModel
    education_analysis:   EducationAnalysisModel
    cv_matching_score:    Optional[float] = None
    jd_similarity_score:  Optional[float] = None
    status:               Optional[str] = "READY_FOR_COMPONENT_3"
    manual_review_recommended: bool = False


class BatchRankResponse(BaseModel):
    job_id:                   Optional[str] = "JOB001"
    job_description_snippet:  Optional[str] = None
    total_candidates:         int
    ranked_candidates:        List[BatchRankItem]
    total:                    Optional[int] = None
    candidates:               Optional[List[BatchRankItem]] = None

    @model_validator(mode="before")
    @classmethod
    def populate_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "total_candidates" in data and "total" not in data:
                data["total"] = data["total_candidates"]
            if "total" in data and "total_candidates" not in data:
                data["total_candidates"] = data["total"]
            if "ranked_candidates" in data and "candidates" not in data:
                data["candidates"] = data["ranked_candidates"]
            if "candidates" in data and "ranked_candidates" not in data:
                data["ranked_candidates"] = data["candidates"]
        return data


class RoleInfo(BaseModel):
    role:            str
    required_skills: List[str]
    required_years:  float


class RolesListResponse(BaseModel):
    total: int
    roles: List[RoleInfo]


class PaginatedCVList(BaseModel):
    total:    int
    skip:     Optional[int] = 0
    page:     Optional[int] = 1
    limit:    int
    items:    List[Any] = []
    analyses: Optional[List[Any]] = None

    @model_validator(mode="before")
    @classmethod
    def populate_items_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "items" in data and "analyses" not in data:
                data["analyses"] = data["items"]
            if "analyses" in data and "items" not in data:
                data["items"] = data["analyses"]
        return data


class DeleteResponse(BaseModel):
    success:      bool
    candidate_id: str
    message:      str
