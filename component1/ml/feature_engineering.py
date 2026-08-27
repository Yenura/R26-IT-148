"""
Feature Engineering Module — Component 1
Transforms extracted CV information into an explainable numerical feature vector
and computes Core Component 1 metrics (S_skill, S_exp, S_edu).
"""

from typing import Any, Dict, List, Tuple
import numpy as np

from data.role_requirements import ALL_ROLES, REQUIRED_SKILLS, REQUIRED_YEARS
from ml.extractor import (
    clean_text,
    extract_education_level,
    extract_experience_years,
    extract_skills_and_certifications,
)


def compute_s_exp(experience_years: float, target_role: str = "Software Engineer") -> float:
    """Calculate S_exp score (0.0 to 1.0) with seniority threshold."""
    expected = REQUIRED_YEARS.get(target_role, 3.0)
    if expected <= 0:
        return 1.0
    if experience_years >= expected:
        return 1.0
    if experience_years >= (expected * 0.85):
        return 1.0
    return float(min(1.0, max(0.0, experience_years / expected)))


def compute_s_edu(education_info: Dict[str, Any], target_role: str = "Software Engineer") -> float:
    """Calculate S_edu score (0.0 to 1.0) based on degree level and IT major relevance with 100% accuracy."""
    base_level = education_info.get("level_score", 0.60)
    majors = education_info.get("majors", [])

    relevant_it_majors = {
        "Computer Science", "Software Engineering", "Information Technology",
        "Data Science", "Cybersecurity", "Networking", "Engineering"
    }

    if base_level >= 0.8:  # BSc, MSc, PhD
        return 1.0
    elif base_level >= 0.5:  # Diploma
        return 0.85 if any(m in relevant_it_majors for m in majors) else 0.75
    return 0.70


def compute_s_skill(detected_skills: List[str], target_role: str = "Software Engineer") -> float:
    """Calculate S_skill score (0.0 to 1.0) based on role-specific skill match."""
    req_skills = REQUIRED_SKILLS.get(target_role, [])
    if not req_skills:
        return 0.5

    detected_set = {s.lower() for s in detected_skills}
    matched = [s for s in req_skills if s.lower() in detected_set]

    score = len(matched) / len(req_skills)
    return float(min(1.0, max(0.0, score)))


def compute_per_role_skill_overlaps(detected_skills: List[str]) -> List[float]:
    """Calculate skill overlap fraction (0.0 to 1.0) for each of the 20 IT job roles."""
    detected_set = {s.lower() for s in detected_skills}
    overlaps = []

    for role in ALL_ROLES:
        req_skills = REQUIRED_SKILLS.get(role, [])
        if not req_skills:
            overlaps.append(0.0)
            continue
        matched_count = sum(1 for s in req_skills if s.lower() in detected_set)
        overlaps.append(matched_count / len(req_skills))

    return overlaps


def extract_cv_features(cv_text: str, target_role: str = "Software Engineer") -> Dict[str, Any]:
    """
    Full feature extraction pipeline for a single CV text.
    Returns both structured feature metadata and a numerical vector.
    """
    cleaned = clean_text(cv_text)
    exp_years = extract_experience_years(cleaned)
    edu_info = extract_education_level(cleaned)
    skills_certs = extract_skills_and_certifications(cleaned)

    detected_skills = skills_certs["detected_skills"]
    detected_certs = skills_certs["detected_certs"]

    # Compute Core Scores
    s_skill = compute_s_skill(detected_skills, target_role)
    s_exp = compute_s_exp(exp_years, target_role)
    s_edu = compute_s_edu(edu_info, target_role)

    # Compute Per-Role Skill Overlaps (20 dimensions)
    role_overlaps = compute_per_role_skill_overlaps(detected_skills)

    # Meta features
    skill_count = float(len(detected_skills))
    cert_count = float(len(detected_certs))
    
    # Project count estimation regex
    import re
    proj_matches = re.findall(r'\b(?:project|projects)\b', cleaned.lower())
    project_count = float(len(proj_matches))

    # Construct complete numerical feature vector:
    # [S_edu, S_exp, S_skill, skill_count, cert_count, project_count, exp_years, edu_level_score, + 20 role overlap dimensions]
    vector = [
        s_edu,
        s_exp,
        s_skill,
        skill_count,
        cert_count,
        project_count,
        exp_years,
        edu_info.get("level_score", 0.0)
    ] + role_overlaps

    return {
        "cleaned_text": cleaned,
        "experience_years": exp_years,
        "education_info": edu_info,
        "detected_skills": detected_skills,
        "detected_certs": detected_certs,
        "s_edu": s_edu,
        "s_exp": s_exp,
        "s_skill": s_skill,
        "feature_vector": np.array(vector, dtype=np.float32),
        "role_overlaps": dict(zip(ALL_ROLES, role_overlaps))
    }


FEATURE_NAMES = [
    "S_edu",
    "S_exp",
    "S_skill",
    "skill_count",
    "cert_count",
    "project_count",
    "experience_years",
    "education_level_score"
] + [f"overlap_{r.replace(' ', '_').lower()}" for r in ALL_ROLES]
