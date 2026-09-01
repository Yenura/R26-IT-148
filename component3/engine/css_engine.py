"""
CSS Scoring Engine - Component 3
IT22027610 | Perera K.G.S.N | R26-IT-148

Implements Equations 1-8 for all 10 IT job roles.
"""

import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.role_configs import (EDU_LEVEL_SCORES, EDU_LEVEL_NAMES,
                                ROLE_CV_WEIGHTS, ROLE_INTERVIEW_WEIGHTS,
                                ROLE_REQUIREMENTS, REQUIRED_YEARS, ROLES)
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class JobRequirementProfile:
    job_id:              str
    job_role:            str
    job_title:           str
    min_edu:             int   = 2
    min_exp_years:       float = 2.0
    min_skill_threshold: float = 0.38
    min_code_threshold:  float = 0.25
    w_edu:   float = 0.20
    w_exp:   float = 0.30
    w_skill: float = 0.50
    w_mcq:   float = 0.20
    w_desc:  float = 0.30
    w_code:  float = 0.50
    W_CV:    float = 0.40
    W_INT:   float = 0.60
    required_years: float = 3.0

    def validate(self):
        assert abs(self.w_edu+self.w_exp+self.w_skill-1.0)<1e-4, "CV weights must sum to 1.0"
        assert abs(self.w_mcq+self.w_desc+self.w_code-1.0)<1e-4, "INT weights must sum to 1.0"
        assert abs(self.W_CV+self.W_INT-1.0)<1e-4, "Master weights must sum to 1.0"

    @classmethod
    def from_role(cls, role: str):
        """Create a default profile from role config."""
        cv_w  = ROLE_CV_WEIGHTS[role]
        int_w = ROLE_INTERVIEW_WEIGHTS[role]
        req   = ROLE_REQUIREMENTS[role]
        return cls(
            job_id=f"JOB_{role}",
            job_role=role,
            job_title=role.replace("_", " "),
            min_edu=req["min_edu"],
            min_exp_years=req["min_exp"],
            min_skill_threshold=req["min_skill"],
            min_code_threshold=req["min_code"],
            w_edu=cv_w["w_edu"],
            w_exp=cv_w["w_exp"],
            w_skill=cv_w["w_skill"],
            w_mcq=int_w["w_mcq"],
            w_desc=int_w["w_desc"],
            w_code=int_w["w_code"],
            W_CV=0.40, W_INT=0.60,
            required_years=REQUIRED_YEARS[role],
        )


@dataclass
class CandidateFeatures:
    candidate_id:     str
    job_role:         str
    edu_level:        int
    edu_relevance:    float
    years_experience: float
    skill_score_raw:  float
    P_mcq:  float
    P_desc: float
    P_code: float
    gender:    Optional[str] = None
    age_group: Optional[str] = None


@dataclass
class CandidateScore:
    candidate_id: str
    job_role:     str
    S_edu:  float = 0.0
    S_exp:  float = 0.0
    S_skill: float = 0.0
    S_cv:   float = 0.0
    P_mcq:  float = 0.0
    P_desc: float = 0.0
    P_code: float = 0.0
    S_int:  float = 0.0
    CSS:    float = 0.0
    passed_hard_filter: bool = True
    filter_fail_reason: str  = ""
    rank: int = 0


class CSSEngine:
    def __init__(self, job: JobRequirementProfile):
        self.job = job
        job.validate()

    def hard_filter(self, f: CandidateFeatures):
        """Equation 1 — Hard filter with soft penalty for near-miss candidates.
        
        Returns:
            (passed, reason, penalty_factor)
            - passed: True if all criteria met
            - reason: Description of failure reason
            - penalty_factor: 1.0 if passed, 0.0-0.9 for near-miss, 0.0 for far miss
        """
        j = self.job
        NEAR_MISS_THRESHOLD = 0.80  # Within 80% of threshold = near-miss
        
        if f.edu_level < j.min_edu:
            deficit = (j.min_edu - f.edu_level) / max(j.min_edu, 1)
            if deficit <= 0.20:
                return False, f"Education near-miss: {EDU_LEVEL_NAMES[f.edu_level]} < {EDU_LEVEL_NAMES[j.min_edu]}", 0.70
            return False, f"Education {EDU_LEVEL_NAMES[f.edu_level]} < min {EDU_LEVEL_NAMES[j.min_edu]}", 0.0
            
        if f.years_experience < j.min_exp_years:
            ratio = f.years_experience / j.min_exp_years
            if ratio >= NEAR_MISS_THRESHOLD:
                penalty = 0.70 + 0.25 * (ratio - NEAR_MISS_THRESHOLD) / (1 - NEAR_MISS_THRESHOLD)
                return False, f"Experience near-miss: {f.years_experience:.1f}y vs {j.min_exp_years:.1f}y required", penalty
            return False, f"Experience {f.years_experience:.1f}y < min {j.min_exp_years:.1f}y", 0.0
            
        if f.skill_score_raw < j.min_skill_threshold:
            ratio = f.skill_score_raw / j.min_skill_threshold
            if ratio >= NEAR_MISS_THRESHOLD:
                penalty = 0.70 + 0.25 * (ratio - NEAR_MISS_THRESHOLD) / (1 - NEAR_MISS_THRESHOLD)
                return False, f"Skill near-miss: {f.skill_score_raw:.2f} vs {j.min_skill_threshold:.2f} threshold", penalty
            return False, f"Skill {f.skill_score_raw:.2f} < threshold {j.min_skill_threshold:.2f}", 0.0
            
        if f.P_code < j.min_code_threshold:
            ratio = f.P_code / j.min_code_threshold
            if ratio >= NEAR_MISS_THRESHOLD:
                penalty = 0.70 + 0.25 * (ratio - NEAR_MISS_THRESHOLD) / (1 - NEAR_MISS_THRESHOLD)
                return False, f"Coding near-miss: {f.P_code:.2f} vs {j.min_code_threshold:.2f} threshold", penalty
            return False, f"Coding {f.P_code:.2f} < threshold {j.min_code_threshold:.2f}", 0.0
            
        return True, "", 1.0

    def s_edu(self, edu_level, edu_rel):
        """Equation 2"""
        return round(0.6*EDU_LEVEL_SCORES.get(edu_level,0.4) + 0.4*edu_rel, 4)

    def s_exp(self, yrs):
        """Equation 3"""
        ry = self.job.required_years
        return round(min(yrs/ry, 1.0) if ry > 0 else 1.0, 4)

    def s_cv(self, se, sx, ss):
        """Equation 5"""
        j = self.job
        return round(j.w_edu*se + j.w_exp*sx + j.w_skill*ss, 4)

    def s_int(self, pm, pd_, pc):
        """Equation 7"""
        j = self.job
        return round(j.w_mcq*pm + j.w_desc*pd_ + j.w_code*pc, 4)

    def css(self, scv, sint):
        """Equation 8 — MASTER"""
        w_cv  = self.job.W_CV
        w_int = 1.0 - w_cv   # constraint enforced
        return round(w_cv*scv + w_int*sint, 4)

    def score_one(self, f: CandidateFeatures) -> CandidateScore:
        res = CandidateScore(candidate_id=f.candidate_id,
                              job_role=f.job_role,
                              P_mcq=f.P_mcq, P_desc=f.P_desc, P_code=f.P_code)
        passed, reason, penalty = self.hard_filter(f)
        res.passed_hard_filter = passed
        res.filter_fail_reason = reason
        res.S_edu   = self.s_edu(f.edu_level, f.edu_relevance)
        res.S_exp   = self.s_exp(f.years_experience)
        res.S_skill = round(float(np.clip(f.skill_score_raw, 0, 1)), 4)
        res.S_cv    = self.s_cv(res.S_edu, res.S_exp, res.S_skill)
        res.S_int   = self.s_int(f.P_mcq, f.P_desc, f.P_code)
        res.CSS     = self.css(res.S_cv, res.S_int)
        if not passed:
            res.CSS = round(res.CSS * penalty, 4)
        return res

    def rank_pool(self, candidates: List[CandidateFeatures]) -> List[CandidateScore]:
        scored = [self.score_one(c) for c in candidates]
        passed = sorted([s for s in scored if s.passed_hard_filter],
                        key=lambda x: x.CSS, reverse=True)
        failed = [s for s in scored if not s.passed_hard_filter]
        for i, s in enumerate(passed):
            s.rank = i + 1
        return passed + failed


def score_dataframe(df: pd.DataFrame, job: JobRequirementProfile) -> pd.DataFrame:
    engine = CSSEngine(job)
    rows   = []
    for _, r in df.iterrows():
        f = CandidateFeatures(
            candidate_id=r["candidate_id"], job_role=r["job_role"],
            edu_level=int(r["edu_level"]), edu_relevance=float(r["edu_relevance"]),
            years_experience=float(r["years_experience"]),
            skill_score_raw=float(r["S_skill"]),
            P_mcq=float(r["P_mcq"]), P_desc=float(r["P_desc"]), P_code=float(r["P_code"]),
            gender=r.get("gender"), age_group=r.get("age_group"),
        )
        s = engine.score_one(f)
        rows.append({"candidate_id":s.candidate_id,"job_role":s.job_role,
                     "S_edu":s.S_edu,"S_exp":s.S_exp,"S_skill":s.S_skill,
                     "S_cv":s.S_cv,"P_mcq":s.P_mcq,"P_desc":s.P_desc,
                     "P_code":s.P_code,"S_int":s.S_int,"CSS":s.CSS,
                     "passed_hard_filter":int(s.passed_hard_filter),
                     "filter_fail_reason":s.filter_fail_reason})
    out = pd.DataFrame(rows).sort_values("CSS", ascending=False)
    out["rank"] = range(1, len(out)+1)
    return out
