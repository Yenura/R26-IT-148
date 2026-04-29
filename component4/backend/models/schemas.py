"""Pydantic schemas for Component 4"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ── Input schemas ──────────────────────────────────────────────────────────────

class SkillGapRequest(BaseModel):
    candidate_id: str
    candidate_name: str
    job_role: str
    skills: List[str]
    experience_years: int = Field(ge=0)
    education: str
    certifications: Optional[str] = "None"
    cv_matching_score: Optional[float] = Field(None, ge=0, le=100)   # from Component 1
    interview_score:   Optional[float] = Field(None, ge=0, le=100)   # from Component 2
    # Granular interview sub-scores (from Component 2)
    mcq_score:         Optional[float] = None
    descriptive_score: Optional[float] = None
    coding_score:      Optional[float] = None
    weak_topics:       Optional[List[str]] = []
    failed_mcq_topics: Optional[List[str]] = []

class ProgressUpdateRequest(BaseModel):
    candidate_id: str
    skill: str
    status: str   # "not_started" | "in_progress" | "completed"
    notes: Optional[str] = ""

class CareerPathRequest(BaseModel):
    candidate_id: str
    current_role: str
    target_role:  Optional[str] = None
    skills:       List[str]
    experience_years: int


# ── Output / Sub schemas ───────────────────────────────────────────────────────

class ResourceRec(BaseModel):
    skill:    str
    course:   str
    url:      str
    duration: str
    level:    str
    priority: str   # "Critical" | "High" | "Medium"

class SkillNode(BaseModel):
    id:       str
    label:    str
    status:   str   # "has" | "missing_required" | "missing_optional"
    category: str

class RoadmapEdge(BaseModel):
    from_:  str = Field(..., alias="from")
    to:     str
    label:  Optional[str] = ""

    class Config:
        populate_by_name = True

class SkillGapReport(BaseModel):
    candidate_id:         str
    candidate_name:       str
    job_role:             str
    cv_matching_score:    Optional[float]
    interview_score:      Optional[float]
    skill_match_pct:      float
    gap_score:            float
    gap_severity:         str
    missing_required:     List[str]
    missing_optional:     List[str]
    present_skills:       List[str]
    technical_gaps:       List[str]
    ml_ai_gaps:           List[str]
    security_gaps:        List[str]
    knowledge_gaps:       List[str]   # inferred from low interview score
    problem_solving_gaps: List[str]   # inferred from low coding score
    resources:            List[ResourceRec]
    roadmap_nodes:        List[SkillNode]
    learning_plan:        List[Dict[str, Any]]
    career_path_suggestions: List[str]
    improvement_suggestions:  List[str]
    predicted_hire:       bool
    hire_probability:     float
    analysis_timestamp:   datetime

class ProgressRecord(BaseModel):
    candidate_id: str
    skill:        str
    status:       str
    notes:        str
    updated_at:   datetime
