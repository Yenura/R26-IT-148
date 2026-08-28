"""
CV Scoring Engine — Component 1: Advanced Accuracy & Deep CV Understanding
IT22094872 | Dulnith K.D. | R26-IT-148

Calculates three separate, independent scores for Component 1:
1. S_skill (0–100): Skill Match Score based on required & preferred coverage, evidence levels, and related skills.
2. S_exp (0–100): Experience Match Score based on role-relevant experience, seniority fit, and responsibilities.
3. S_edu (0–100): Education Match Score based on degree level, domain relevance, and verified certifications.

These three scores are output independently to be passed to Component 3, which owns
the final weighted-average candidate ranking model. DO NOT COLLAPSE THEM.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data.role_requirements import (
    EDU_LEVEL_SCORES,
    REQUIRED_YEARS,
    REQUIRED_SKILLS,
    ROLE_CV_WEIGHTS,
)
from ml.lexicon import CANONICAL_CERTIFICATIONS, RELATED_SKILLS_GRAPH, SKILL_ALIASES

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
    matched_preferred_skills: List[str] = field(default_factory=list)
    related_skills: List[str] = field(default_factory=list)
    evidence_breakdown: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matched_count": self.matched_count,
            "required_count": self.required_count,
            "percentage": round(self.percentage, 2),
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "matched_preferred_skills": self.matched_preferred_skills,
            "related_skills": self.related_skills,
            "evidence_breakdown": self.evidence_breakdown,
        }


@dataclass
class ExperienceAnalysis:
    candidate_years: float
    required_years: float
    relevant_years: float
    score: float
    candidate_seniority: str = "Mid"
    target_seniority: str = "Mid"
    seniority_fit: str = "MATCH"
    seniority_evidence: List[str] = field(default_factory=list)
    employment_records: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_years": round(self.candidate_years, 2),
            "required_years": round(self.required_years, 2),
            "relevant_years": round(self.relevant_years, 2),
            "score": round(self.score, 2),
            "candidate_seniority": self.candidate_seniority,
            "target_seniority": self.target_seniority,
            "seniority_fit": self.seniority_fit,
            "seniority_evidence": self.seniority_evidence,
            "employment_records": self.employment_records,
        }


@dataclass
class EducationAnalysis:
    candidate_education: List[str]
    required_education: List[str]
    education_match: str
    score: float
    degree_level: str = "BSc"
    field_relevance: str = "HIGH"
    verified_certifications: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_education": self.candidate_education,
            "required_education": self.required_education,
            "education_match": self.education_match,
            "score": round(self.score, 2),
            "degree_level": self.degree_level,
            "field_relevance": self.field_relevance,
            "verified_certifications": self.verified_certifications,
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

    # Optional legacy / similarity metrics
    jd_similarity_score: Optional[float] = None
    optional_legacy_score: Optional[float] = None
    cv_matching_score: Optional[float] = None


SENIORITY_RANKS = {
    "intern": 1,
    "junior": 2,
    "mid": 3,
    "senior": 4,
    "lead": 5,
    "architect": 6,
    "principal": 6
}


def calculate_skill_score(
    candidate_skills: List[str],
    required_skills_spec: Union[List[str], List[Dict[str, Any]]],
    preferred_skills_spec: Optional[List[str]] = None,
    skill_evidence: Optional[Dict[str, Any]] = None,
) -> tuple[float, SkillAnalysis]:
    """Calculate S_skill (0-100) using coverage, preferred bonus, evidence levels, and related skills."""
    if not required_skills_spec:
        analysis = SkillAnalysis(
            matched_count=0,
            required_count=0,
            percentage=100.0 if candidate_skills else 0.0,
            matched_skills=candidate_skills,
            missing_skills=[],
        )
        return (100.0 if candidate_skills else 0.0), analysis

    cand_set = {SKILL_ALIASES.get(s.strip().lower(), s.strip().lower()) for s in candidate_skills if s and s.strip()}
    evidence_dict = skill_evidence or {}

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

        s_canonical = SKILL_ALIASES.get(s_name.lower(), s_name.lower())
        total_weight += weight

        # Check exact or substring alias match
        is_match = (
            s_canonical in cand_set or
            any(s_canonical == c or s_canonical in c or c in s_canonical for c in cand_set)
        )

        if is_match:
            matched_skills.append(s_name)
            matched_weight += weight
        else:
            missing_skills.append(s_name)

    required_count = len(matched_skills) + len(missing_skills)
    matched_count = len(matched_skills)

    # Base required coverage (0 - 100)
    req_coverage = (matched_weight / total_weight * 100.0) if total_weight > 0 else 0.0

    # Preferred skills matching
    matched_pref: List[str] = []
    if preferred_skills_spec:
        for pref in preferred_skills_spec:
            pref_norm = SKILL_ALIASES.get(pref.strip().lower(), pref.strip().lower())
            if pref_norm in cand_set or any(pref_norm == c or pref_norm in c for c in cand_set):
                matched_pref.append(pref)
        pref_ratio = len(matched_pref) / max(1, len(preferred_skills_spec))
        pref_bonus = min(15.0, pref_ratio * 15.0)
    else:
        pref_bonus = 0.0

    # Related skills bonus (complementary graph)
    matched_norms = {SKILL_ALIASES.get(m.lower(), m.lower()) for m in matched_skills}
    related_matches: List[str] = []
    for miss in missing_skills:
        miss_norm = SKILL_ALIASES.get(miss.lower(), miss.lower())
        related_nodes = RELATED_SKILLS_GRAPH.get(miss_norm, [])
        for rel in related_nodes:
            if rel in cand_set and rel not in matched_norms and rel not in related_matches:
                related_matches.append(rel)

    related_bonus = min(5.0, len(related_matches) * 1.5)

    # Evidence strength bonus (High vs Medium vs Low)
    high_ev_count = 0
    for s in matched_skills:
        s_norm = SKILL_ALIASES.get(s.lower(), s.lower())
        ev = evidence_dict.get(s_norm, {})
        if ev.get("evidence_strength") == "high":
            high_ev_count += 1
    evidence_bonus = (high_ev_count / max(1, matched_count)) * 10.0 if matched_count > 0 else 0.0

    # Final S_skill normalization
    if not preferred_skills_spec:
        # Standard requirement coverage when no preferred skills specified
        if high_ev_count > 0 or related_matches:
            raw_score = min(100.0, req_coverage + evidence_bonus + related_bonus)
        else:
            raw_score = req_coverage
    else:
        raw_score = req_coverage * 0.70 + pref_bonus + evidence_bonus + related_bonus

    s_skill = max(0.0, min(100.0, raw_score))

    analysis = SkillAnalysis(
        matched_count=matched_count,
        required_count=required_count,
        percentage=round(s_skill, 2),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        matched_preferred_skills=matched_pref,
        related_skills=related_matches,
        evidence_breakdown={
            "high_evidence_count": high_ev_count,
            "total_matched": matched_count,
            "evidence_bonus_points": round(evidence_bonus, 2),
            "related_skills_bonus_points": round(related_bonus, 2)
        }
    )
    return round(s_skill, 2), analysis


def calculate_experience_score(
    candidate_years: float,
    required_years: float,
    relevant_years: Optional[float] = None,
    candidate_seniority: str = "Mid",
    target_seniority: str = "Mid",
    seniority_evidence: Optional[List[str]] = None,
    employment_records: Optional[List[Dict[str, Any]]] = None,
) -> tuple[float, ExperienceAnalysis]:
    """Calculate S_exp (0-100) comparing Role-Relevant Experience, Seniority, and Responsibilities."""
    cand_yrs = max(0.0, float(candidate_years))
    req_yrs = max(0.1, float(required_years))
    rel_yrs = max(0.0, float(relevant_years)) if relevant_years is not None else cand_yrs

    # Zero experience edge case
    if cand_yrs <= 0.0:
        return 0.0, ExperienceAnalysis(
            candidate_years=0.0,
            required_years=round(req_yrs, 2),
            relevant_years=0.0,
            score=0.0,
            candidate_seniority=candidate_seniority,
            target_seniority=target_seniority,
            seniority_fit="NO_EXPERIENCE",
            seniority_evidence=[],
            employment_records=[]
        )

    recs = employment_records or []

    # If no employment records provided, use standard ratio benchmark
    if not recs:
        if rel_yrs >= req_yrs or rel_yrs >= (req_yrs * 0.85):
            s_exp = 100.0
        else:
            s_exp = min(1.0, rel_yrs / req_yrs) * 100.0
        sen_match = "BENCHMARK_FIT"
    else:
        # Multi-signal evaluation for full candidate profiles
        # 1. Relevant experience fit (0 - 50 pts)
        if rel_yrs >= req_yrs or rel_yrs >= (req_yrs * 0.85):
            rel_fit = 50.0
        else:
            rel_fit = (rel_yrs / req_yrs) * 50.0

        # 2. Seniority fit (0 - 25 pts)
        c_rank = SENIORITY_RANKS.get(candidate_seniority.lower(), 3)
        t_rank = SENIORITY_RANKS.get(target_seniority.lower(), 3)

        if c_rank >= t_rank:
            seniority_pts = 25.0
            sen_match = "FULL_SENIORITY_MATCH"
        elif c_rank == (t_rank - 1):
            seniority_pts = 18.0
            sen_match = "ADJACENT_GROWTH_FIT"
        elif c_rank == (t_rank - 2):
            seniority_pts = 10.0
            sen_match = "POTENTIAL_TRAINEE_FIT"
        else:
            seniority_pts = 5.0
            sen_match = "UNDERQUALIFIED_FOR_LEVEL"

        # 3. Responsibility & Technology fit (0 - 25 pts)
        total_bullets = sum(len(r.get("responsibilities", [])) for r in recs)
        total_techs = sum(len(r.get("technologies", [])) for r in recs)

        bullet_pts = min(15.0, 5.0 + total_bullets * 1.5)
        tech_pts = min(10.0, 4.0 + total_techs * 1.0)

        raw_score = rel_fit + seniority_pts + bullet_pts + tech_pts
        s_exp = max(0.0, min(100.0, raw_score))



    analysis = ExperienceAnalysis(
        candidate_years=round(cand_yrs, 2),
        required_years=round(req_yrs, 2),
        relevant_years=round(rel_yrs, 2),
        score=round(s_exp, 2),
        candidate_seniority=candidate_seniority,
        target_seniority=target_seniority,
        seniority_fit=sen_match,
        seniority_evidence=seniority_evidence or [],
        employment_records=recs
    )
    return round(s_exp, 2), analysis


def calculate_education_score(
    candidate_edu: Union[str, List[str]],
    edu_level: int,
    required_education: Optional[List[str]] = None,
    verified_certifications: Optional[List[Dict[str, Any]]] = None,
) -> tuple[float, EducationAnalysis]:
    """Calculate S_edu (0-100) using degree level, domain relevance, and verified certifications."""
    cand_edu_list = candidate_edu if isinstance(candidate_edu, list) else ([candidate_edu] if candidate_edu else [])
    req_edu_list = required_education or [
        "BSc Information Technology",
        "BSc Computer Science",
        "BSc Software Engineering",
    ]

    cand_text = " ".join(cand_edu_list).lower()
    it_keywords = [
        "computer", "it", "software", "information technology", "data", "cyber",
        "system", "ai", "engineering", "tech", "computing", "analytics", "science",
        "network", "cloud", "security", "web", "developer", "applied", "bcs", "bit",
        "b.sc", "bsc", "bachelor", "msc", "m.sc", "phd", "university", "institute", "college"
    ]
    
    is_it_field = any(k in cand_text for k in it_keywords)
    non_relevant_keywords = ["fine arts", "history", "literature", "music", "philosophy", "theology", "culinary", "drama"]
    is_explicitly_non_relevant = any(k in cand_text for k in non_relevant_keywords)

    certs = verified_certifications or []
    cert_bonus = 15.0 if len(certs) >= 1 else 0.0

    if is_explicitly_non_relevant:
        base_score = 40.0 if edu_level >= 2 else 30.0
        match_status = "NON_RELEVANT_DEGREE"
        f_rel = "LOW"
    elif edu_level >= 2 or is_it_field:
        if edu_level >= 2 or any(deg in cand_text for deg in ("bsc", "b.sc", "bachelor", "msc", "m.sc", "master", "phd", "b.tech", "b.eng", "bit", "bcs")):
            base_score = 100.0
            match_status = "FULL_MATCH"
            f_rel = "HIGH"
        else:
            base_score = 85.0
            match_status = "PARTIAL_MATCH (DIPLOMA)"
            f_rel = "HIGH"
    elif edu_level == 1:
        base_score = 80.0
        match_status = "QUALIFIED (DIPLOMA)"
        f_rel = "MEDIUM"
    else:
        base_score = 70.0
        match_status = "EXPERIENCE_EQUIVALENT"
        f_rel = "MEDIUM"

    raw_score = min(100.0, base_score + (cert_bonus if base_score < 100.0 else 0.0))
    s_edu = max(0.0, min(100.0, raw_score))

    analysis = EducationAnalysis(
        candidate_education=cand_edu_list,
        required_education=req_edu_list,
        education_match=match_status,
        score=round(s_edu, 2),
        degree_level="PhD" if edu_level >= 4 else ("MSc" if edu_level == 3 else ("BSc" if edu_level == 2 else "Diploma")),
        field_relevance=f_rel,
        verified_certifications=certs
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
    # Deep understanding optional parameters
    preferred_skills_spec: Optional[List[str]] = None,
    role_relevant_experience_years: Optional[float] = None,
    candidate_seniority: str = "Mid",
    target_seniority: str = "Mid",
    seniority_evidence: Optional[List[str]] = None,
    employment_records: Optional[List[Dict[str, Any]]] = None,
    skill_evidence: Optional[Dict[str, Any]] = None,
    verified_certifications: Optional[List[Dict[str, Any]]] = None,
) -> CVScores:
    """Core Component 1 scoring function.
    Calculates THREE SEPARATE, INDEPENDENT SCORES: S_skill, S_exp, S_edu (0-100).
    """
    cand_skills = skills or []
    cand_edu = candidate_education or (f"BSc Level {edu_level}" if edu_level >= 2 else "Diploma Level 1")

    # 1. Requirements lookup if not provided
    if required_skills_spec is None:
        required_skills_spec = REQUIRED_SKILLS.get(role, [])

    if required_years is None:
        required_years = REQUIRED_YEARS.get(role, 3.0)

    if required_education is None:
        required_education = [
            "BSc Information Technology",
            "BSc Computer Science",
            "BSc Software Engineering",
        ]

    # Compute Pillar 1: S_skill
    s_skill, skill_analysis = calculate_skill_score(
        candidate_skills=cand_skills,
        required_skills_spec=required_skills_spec,
        preferred_skills_spec=preferred_skills_spec,
        skill_evidence=skill_evidence,
    )

    # Compute Pillar 2: S_exp
    s_exp, exp_analysis = calculate_experience_score(
        candidate_years=experience_years,
        required_years=required_years,
        relevant_years=role_relevant_experience_years,
        candidate_seniority=candidate_seniority,
        target_seniority=target_seniority,
        seniority_evidence=seniority_evidence,
        employment_records=employment_records,
    )

    # Compute Pillar 3: S_edu
    s_edu, edu_analysis = calculate_education_score(
        candidate_edu=cand_edu,
        edu_level=edu_level,
        required_education=required_education,
        verified_certifications=verified_certifications,
    )

    c1_scores = Component1Scores(
        S_skill=round(s_skill, 2),
        S_exp=round(s_exp, 2),
        S_edu=round(s_edu, 2),
    )

    weights = ROLE_CV_WEIGHTS.get(role, {"w_skill": 0.50, "w_exp": 0.30, "w_edu": 0.20})
    w_skill = weights["w_skill"]
    w_exp   = weights["w_exp"]
    w_edu   = weights["w_edu"]

    cv_match = (s_skill * w_skill) + (s_exp * w_exp) + (s_edu * w_edu)
    cv_match = max(0.0, min(100.0, cv_match))

    return CVScores(
        component_1_scores=c1_scores,
        S_skill=round(s_skill, 2),
        S_exp=round(s_exp, 2),
        S_edu=round(s_edu, 2),
        skill_analysis=skill_analysis,
        experience_analysis=exp_analysis,
        education_analysis=edu_analysis,
        skill_score_raw=round(s_skill / 100.0, 4),
        jd_similarity_score=jd_similarity_score,
        optional_legacy_score=round(cv_match, 2),
        cv_matching_score=round(cv_match, 2),
    )
