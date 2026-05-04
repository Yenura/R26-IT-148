"""Pydantic schemas for Component 4 — rebuilt for new 10K dataset"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ── Input schemas ──────────────────────────────────────────────────────────────

class SkillGapRequest(BaseModel):
    candidate_id:      str
    candidate_name:    str
    job_role:          str
    skills:            List[str]
    experience_years:  int           = Field(ge=0, default=2)
    education:         Optional[str] = "B.Sc. Computer Science"
    certifications:    Optional[str] = "None"
    certifications_count: Optional[int] = Field(ge=0, default=0)
    projects_count:    Optional[int] = Field(ge=0, default=0)
    job_level:         Optional[str] = "Mid-Level"   # Junior|Mid-Level|Senior|Lead|Principal / Staff
    work_mode:         Optional[str] = "Hybrid"       # On-Site|Hybrid|Remote
    # Scores from other components
    cv_matching_score: Optional[float] = Field(None, ge=0, le=100)
    interview_score:   Optional[float] = Field(None, ge=0, le=100)
    mcq_score:         Optional[float] = None
    descriptive_score: Optional[float] = None
    coding_score:      Optional[float] = None
    weak_topics:       Optional[List[str]] = []
    failed_mcq_topics: Optional[List[str]] = []


class ProgressUpdateRequest(BaseModel):
    candidate_id: str
    skill:        str
    status:       str   # "not_started" | "in_progress" | "completed"
    notes:        Optional[str] = ""


class CareerPathRequest(BaseModel):
    candidate_id:    str
    current_role:    str
    target_role:     Optional[str] = None
    skills:          List[str]
    experience_years: int
    job_level:       Optional[str] = "Mid-Level"


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
    candidate_id:           str
    candidate_name:         str
    job_role:               str
    job_level:              Optional[str]
    work_mode:              Optional[str]
    cv_matching_score:      Optional[float]
    interview_score:        Optional[float]
    skill_match_pct:        float
    gap_score:              float
    gap_severity:           str
    missing_required:       List[str]
    missing_optional:       List[str]
    present_skills:         List[str]
    technical_gaps:         List[str]
    ml_ai_gaps:             List[str]
    cloud_devops_gaps:      List[str]
    security_gaps:          List[str]
    data_gaps:              List[str]
    knowledge_gaps:         List[str]
    problem_solving_gaps:   List[str]
    resources:              List[ResourceRec]
    roadmap_nodes:          List[SkillNode]
    learning_plan:          List[Dict[str, Any]]
    career_path_suggestions: List[str]
    improvement_suggestions:  List[str]
    predicted_hire:         bool
    hire_probability:       float
    analysis_timestamp:     datetime
    certifications_count:   Optional[int]
    projects_count:         Optional[int]


class ProgressRecord(BaseModel):
    candidate_id: str
    skill:        str
    status:       str
    notes:        str
    updated_at:   datetime
