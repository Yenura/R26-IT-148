"""Component 3 — API schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class CandidateInput(BaseModel):
    candidate_id: str = Field(..., min_length=1)
    candidate_name: str = ""
    job_role: Optional[str] = None
    edu_level: int = 2
    edu_relevance: float = 0.8
    years_experience: float = 0.0
    skill_score_raw: float = 0.0
    S_edu: Optional[float] = None
    S_exp: Optional[float] = None
    S_skill: Optional[float] = None
    P_mcq: float = 0.0
    P_desc: float = 0.0
    P_code: float = 0.0
    gender: Optional[str] = None
    age_group: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    cv_matching_score: Optional[float] = None
    interview_score: Optional[float] = None
    mcq_score: Optional[float] = None
    descriptive_score: Optional[float] = None
    coding_score: Optional[float] = None
    # False when the candidate's interview had no coding section (non-coding
    # roles). Engine then skips the coding gate and redistributes its weight.
    has_coding: bool = True


class RankRequest(BaseModel):
    job_id: Optional[str] = None
    job_role: str = Field(..., min_length=1)
    candidates: List[CandidateInput] = Field(..., min_length=1)
    w_cv: float = 0.40
    w_int: float = 0.60
    use_ltr: bool = True
    include_skill_gap: bool = False


class RankWeightsRequest(BaseModel):
    job_role: str = Field(..., min_length=1)
    w_cv: float = 0.40
    w_int: float = 0.60


class RankedCandidate(BaseModel):
    rank: int
    candidate_id: str
    candidate_name: str = ""
    S_edu: float
    S_exp: float
    S_skill: float
    S_cv: float
    S_int: float
    CSS: float
    P_mcq: float
    P_desc: float
    P_code: float
    ltr_score: Optional[float] = None
    passed_hard_filter: bool
    filter_fail_reason: str = ""
    hire_probability: Optional[float] = None
    predicted_hire: Optional[bool] = None
