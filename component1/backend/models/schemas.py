"""Component 1 — API schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class CVMatchRequest(BaseModel):
    candidate_id: str = Field(..., min_length=1)
    job_role: str = Field(..., min_length=1)
    cv_text: str = ""
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education_text: Optional[str] = None


class CVMatchResponse(BaseModel):
    report_id: str
    candidate_id: str
    job_role: str
    cv_matching_score: float
    extracted_skills: List[str]
    missing_skills: List[str]
    covered_skills: List[str]
    experience_years: float
    edu_level: int
    edu_level_name: str
    edu_relevance: float
    coverage: float
    S_edu: float
    S_exp: float
    S_skill: float
    predicted_relevance_class: int
    predicted_relevance_label: str


class JobCreate(BaseModel):
    job_role: str = Field(..., min_length=1)
    title: str = ""
    description: str = ""
    required_skills: List[str]
    required_years: float = 2.0
    min_edu: int = 2
    w_edu: float = 0.20
    w_exp: float = 0.30
    w_skill: float = 0.50


class JobOut(JobCreate):
    id: str
