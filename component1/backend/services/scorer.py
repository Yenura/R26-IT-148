"""CV scoring engine — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Calculates three separate, independent scores for Component 1:
1. S_skill (0–100): Skill Match Score based on job requirements & importance weights.
2. S_exp (0–100): Experience Match Score based on candidate vs required years.
3. S_edu (0–100): Education Match Score based on degree level & domain relevance.

These three scores are output independently to be passed to Component 3, which owns
the final weighted-average candidate ranking model.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data.role_requirements import (
    EDU_LEVEL_SCORES,
    REQUIRED_YEARS,
    REQUIRED_SKILLS,
    ROLE_CV_WEIGHTS,
)

logger = logging.getLogger("component1.scorer")


@dataclass
class Component1Scores:
    S_skill: float  # 0.0 to 100.0
    S_exp:   float  # 0.0 to 100.0
    S_edu:   float  # 0.0 to 100.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "S_skill": round(self.S_skill, 2),
            "S_exp": round(self.S_exp, 2),
            "S_edu": round(self.S_edu, 2),
        }


@dataclass
class SkillAnalysis:
    matched_count: int
    required_count: int
    percentage: float
    matched_skills: List[str]
    missing_skills: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matched_count": self.matched_count,
            "required_count": self.required_count,
            "percentage": round(self.percentage, 2),
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
        }


@dataclass
class ExperienceAnalysis:
    candidate_years: float
    required_years: float
    relevant_years: float
    score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_years": round(self.candidate_years, 2),
            "required_years": round(self.required_years, 2),
            "relevant_years": round(self.relevant_years, 2),
            "score": round(self.score, 2),
        }


@dataclass
class EducationAnalysis:
    candidate_education: List[str]
    required_education: List[str]
    education_match: str
    score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_education": self.candidate_education,
            "required_education": self.required_education,
            "education_match": self.education_match,
            "score": round(self.score, 2),
        }


@dataclass
class CVScores:
    # Three primary independent scores (0–100)
    component_1_scores: Component1Scores

    # Direct accessors (0–100)
    S_skill: float
    S_exp:   float
    S_edu:   float

    # Detailed breakdown objects
    skill_analysis: SkillAnalysis
    experience_analysis: ExperienceAnalysis
    education_analysis: EducationAnalysis

    # Component 3 raw alias (0.0 to 1.0)
    skill_score_raw: float

    # Optional legacy / similarity metrics (clearly distinguished)
    jd_similarity_score: Optional[float] = None
    optional_legacy_score: Optional[float] = None
    cv_matching_score: Optional[float] = None  # alias for backwards compatibility


def calculate_skill_score(
    candidate_skills: List[str],
    required_skills_spec: Union[List[str], List[Dict[str, Any]]],
) -> tuple[float, SkillAnalysis]:
    """Calculate S_skill (0-100) and skill match details against specific job requirement."""
    if not required_skills_spec:
        # Default fallback if job has no explicit required skills
        analysis = SkillAnalysis(
            matched_count=0,
            required_count=0,
            percentage=100.0 if candidate_skills else 0.0,
            matched_skills=candidate_skills,
            missing_skills=[],
        )
        return 100.0 if candidate_skills else 0.0, analysis

    cand_set = {s.strip().lower() for s in candidate_skills if s and s.strip()}
    
    # Check if spec is weighted list of dicts [{"skill": "Python", "importance": 1.0}, ...]
    is_weighted = isinstance(required_skills_spec[0], dict) if required_skills_spec else False

    matched_skills: List[str] = []
    missing_skills: List[str] = []
    total_weight = 0.0
    matched_weight = 0.0

    for item in required_skills_spec:
        if isinstance(item, dict):
            s_name = item.get("skill", "").strip()
            weight = float(item.get("importance", 1.0))
        else:
            s_name = str(item).strip()
            weight = 1.0

        if not s_name:
            continue

        s_lower = s_name.lower()
        total_weight += weight

        # Substring or exact match against candidate skills
        if any(s_lower == c or s_lower in c or c in s_lower for c in cand_set):
            matched_skills.append(s_name)
            matched_weight += weight
        else:
            missing_skills.append(s_name)

    required_count = len(matched_skills) + len(missing_skills)
    matched_count = len(matched_skills)

    if total_weight > 0:
        raw_score = (matched_weight / total_weight) * 100.0
    else:
        raw_score = 0.0

    s_skill = max(0.0, min(100.0, raw_score))

    analysis = SkillAnalysis(
        matched_count=matched_count,
        required_count=required_count,
        percentage=round(s_skill, 2),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
    )
    return round(s_skill, 2), analysis


def calculate_experience_score(
    candidate_years: float,
    required_years: float,
    relevant_years: Optional[float] = None,
) -> tuple[float, ExperienceAnalysis]:
    """Calculate S_exp (0-100) using experience ratio capped at 100."""
    eff_years = relevant_years if relevant_years is not None else candidate_years
    eff_years = max(0.0, float(eff_years))
    req_years = max(0.0, float(required_years))

    if req_years == 0:
        s_exp = 100.0
    else:
        ratio = eff_years / req_years
        s_exp = min(ratio, 1.0) * 100.0

    s_exp = max(0.0, min(100.0, s_exp))

    analysis = ExperienceAnalysis(
        candidate_years=candidate_years,
        required_years=required_years,
        relevant_years=eff_years,
        score=round(s_exp, 2),
    )
    return round(s_exp, 2), analysis


def calculate_education_score(
    candidate_edu: Union[str, List[str]],
    edu_level: int,
    required_education: Optional[List[str]] = None,
) -> tuple[float, EducationAnalysis]:
    """Calculate S_edu (0-100) comparing degree level & domain relevance."""
    cand_edu_list = candidate_edu if isinstance(candidate_edu, list) else ([candidate_edu] if candidate_edu else [])
    req_edu_list = required_education or [
        "BSc Information Technology",
        "BSc Computer Science",
        "BSc Software Engineering",
    ]

    # Map edu_level (1=Diploma, 2=BSc, 3=MSc, 4=PhD) to score (0-100)
    base_level_scores = {1: 60.0, 2: 80.0, 3: 95.0, 4: 100.0}
    base_score = base_level_scores.get(edu_level, 40.0)

    # Check for direct degree or IT discipline match
    cand_text = " ".join(cand_edu_list).lower()
    it_keywords = ["computer", "it", "software", "information technology", "data", "cyber", "system", "ai", "engineering"]
    
    is_it_field = any(k in cand_text for k in it_keywords)

    if is_it_field:
        if edu_level >= 2:
            s_edu = 100.0
            match_status = "FULL_MATCH"
        else:
            s_edu = 70.0
            match_status = "PARTIAL_MATCH (DIPLOMA)"
    else:
        if cand_text:
            s_edu = 40.0
            match_status = "NON_RELEVANT_DEGREE"
        else:
            s_edu = 20.0
            match_status = "NOT_PROVIDED"

    s_edu = max(0.0, min(100.0, s_edu))

    analysis = EducationAnalysis(
        candidate_education=cand_edu_list,
        required_education=req_edu_list,
        education_match=match_status,
        score=round(s_edu, 2),
    )
    return round(s_edu, 2), analysis


def score(
    role: str = "Software Engineer",
    edu_level: int = 2,
    experience_years: float = 0.0,
    skills: Optional[List[str]] = None,
    jd_similarity_score: Optional[float] = None,
    required_skills_spec: Optional[Union[List[str], List[Dict[str, Any]]]] = None,
    required_years: Optional[float] = None,
    required_education: Optional[List[str]] = None,
    candidate_education: Optional[Union[str, List[str]]] = None,
) -> CVScores:
    """Core Component 1 scoring function.
    Calculates THREE SEPARATE, INDEPENDENT SCORES: S_skill, S_exp, S_edu (0-100).
    """
    cand_skills = skills or []
    cand_edu = candidate_education or (f"BSc Level {edu_level}" if edu_level >= 2 else "Diploma Level 1")

    # 1. Required skills spec lookup if not provided
    if required_skills_spec is None:
        required_skills_spec = REQUIRED_SKILLS.get(role, [])

    # 2. Required years lookup if not provided
    if required_years is None:
        required_years = REQUIRED_YEARS.get(role, 3.0)

    # 3. Required education lookup if not provided
    if required_education is None:
        required_education = [
            "BSc Information Technology",
            "BSc Computer Science",
            "BSc Software Engineering",
        ]

    # Calculate 3 independent scores
    s_skill_val, skill_analysis = calculate_skill_score(cand_skills, required_skills_spec)
    s_exp_val, exp_analysis = calculate_experience_score(experience_years, required_years)
    s_edu_val, edu_analysis = calculate_education_score(cand_edu, edu_level, required_education)

    c1_scores = Component1Scores(
        S_skill=s_skill_val,
        S_exp=s_exp_val,
        S_edu=s_edu_val,
    )

    # Component 3 raw alias (0.0 to 1.0)
    skill_score_raw = round(s_skill_val / 100.0, 4)

    # Optional legacy score for backward compatibility only
    if jd_similarity_score is not None:
        legacy_score = (
            0.35 * (s_skill_val / 100.0) +
            0.25 * (s_exp_val / 100.0) +
            0.15 * (s_edu_val / 100.0) +
            0.25 * float(jd_similarity_score)
        ) * 100.0
    else:
        cv_w = ROLE_CV_WEIGHTS.get(role, {"w_edu": 0.20, "w_exp": 0.30, "w_skill": 0.50})
        legacy_score = (
            cv_w["w_edu"] * (s_edu_val / 100.0) +
            cv_w["w_exp"] * (s_exp_val / 100.0) +
            cv_w["w_skill"] * (s_skill_val / 100.0)
        ) * 100.0
    legacy_score = round(max(0.0, min(100.0, legacy_score)), 2)

    return CVScores(
        component_1_scores=c1_scores,
        S_skill=s_skill_val,
        S_exp=s_exp_val,
        S_edu=s_edu_val,
        skill_analysis=skill_analysis,
        experience_analysis=exp_analysis,
        education_analysis=edu_analysis,
        skill_score_raw=skill_score_raw,
        jd_similarity_score=round(float(jd_similarity_score), 4) if jd_similarity_score is not None else None,
        optional_legacy_score=legacy_score,
        cv_matching_score=legacy_score,
    )

