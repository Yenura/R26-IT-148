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


# ── Role Specialization & Focus Area Compatibility Matrix ───────────────────────
ROLE_SPECIALIZATION_COMPATIBILITY: Dict[str, Dict[str, float]] = {
    "Data Scientist": {
        "Data Science & AI": 1.00, "Data Science": 1.00, "Computer Science": 0.88,
        "Software Engineering": 0.80, "Information Technology": 0.75, "Engineering": 0.65
    },
    "Machine Learning Engineer": {
        "Data Science & AI": 1.00, "Data Science": 1.00, "Computer Science": 0.90,
        "Software Engineering": 0.85, "Information Technology": 0.75
    },
    "AI/NLP Engineer": {
        "Data Science & AI": 1.00, "Data Science": 1.00, "Computer Science": 0.90,
        "Software Engineering": 0.85, "Information Technology": 0.75
    },
    "Cybersecurity Analyst": {
        "Cybersecurity": 1.00, "Networking": 0.90, "Computer Networks & Systems": 0.95,
        "Computer Science": 0.85, "Information Technology": 0.85, "Software Engineering": 0.75
    },
    "DevOps Engineer": {
        "Cloud & DevOps": 1.00, "Computer Networks & Systems": 0.95, "Networking": 0.90,
        "Software Engineering": 0.90, "Computer Science": 0.88, "Information Technology": 0.85
    },
    "Cloud Solutions Architect": {
        "Cloud & DevOps": 1.00, "Computer Networks & Systems": 0.95, "Networking": 0.90,
        "Software Engineering": 0.90, "Computer Science": 0.90, "Information Technology": 0.85
    },
    "Site Reliability Engineer": {
        "Cloud & DevOps": 1.00, "Computer Networks & Systems": 0.95, "Networking": 0.90,
        "Software Engineering": 0.90, "Computer Science": 0.90, "Information Technology": 0.85
    },
    "Software Engineer": {
        "Software Engineering": 1.00, "Computer Science": 1.00, "Information Technology": 0.90,
        "Data Science & AI": 0.85, "Cybersecurity": 0.80, "Engineering": 0.80
    },
    "Backend Developer": {
        "Software Engineering": 1.00, "Computer Science": 1.00, "Cloud & DevOps": 0.90,
        "Information Technology": 0.90, "Data Science & AI": 0.80
    },
    "Frontend Developer": {
        "Interactive Media & HCI": 1.00, "Software Engineering": 1.00, "Computer Science": 0.95,
        "Information Technology": 0.90
    },
    "Full Stack Developer": {
        "Software Engineering": 1.00, "Computer Science": 1.00, "Information Technology": 0.90
    },
    "UI/UX Designer": {
        "Interactive Media & HCI": 1.00, "Computer Science": 0.85, "Information Technology": 0.85
    },
    "Database Administrator": {
        "Business Information Systems": 1.00, "Data Science & AI": 0.95, "Computer Science": 0.95,
        "Software Engineering": 0.90, "Information Technology": 0.90
    },
    "Data Engineer": {
        "Data Science & AI": 1.00, "Computer Science": 0.95, "Software Engineering": 0.90,
        "Information Technology": 0.85
    },
    "Network Engineer": {
        "Computer Networks & Systems": 1.00, "Networking": 1.00, "Cybersecurity": 0.90,
        "Information Technology": 0.85, "Computer Science": 0.80
    },
    "Mobile App Developer": {
        "Software Engineering": 1.00, "Computer Science": 0.95, "Information Technology": 0.85
    },
    "Business/Systems Analyst": {
        "Business Information Systems": 1.00, "Information Technology": 0.95,
        "Computer Science": 0.85, "Software Engineering": 0.85, "Business Administration": 0.70
    },
    "QA/Test Automation Engineer": {
        "Software Engineering": 1.00, "Computer Science": 0.95, "Information Technology": 0.90
    },
    "Blockchain Developer": {
        "Software Engineering": 1.00, "Computer Science": 1.00, "Cybersecurity": 0.90
    },
    "Embedded Systems Engineer": {
        "Engineering": 1.00, "Computer Networks & Systems": 0.95, "Computer Science": 0.85
    }
}


def compute_s_edu(education_info: Dict[str, Any], target_role: str = "Software Engineer") -> float:
    """Calculate S_edu score (0.0 to 1.0) based on degree level, field, and exact academic specialization."""
    base_level = education_info.get("level_score", 0.60)
    majors = education_info.get("majors", [])
    specializations = education_info.get("specializations", [])
    honors = education_info.get("academic_honors", "Standard")

    all_fields = specializations + majors
    compat_map = ROLE_SPECIALIZATION_COMPATIBILITY.get(target_role, {})

    best_relevance = 0.20
    for field in all_fields:
        if field in compat_map:
            best_relevance = max(best_relevance, compat_map[field])

    # If it's a recognized Non-IT major (Accounting, Culinary, etc.) with no IT overlap
    is_non_it = any(m in ["Accounting & Finance", "Business Administration", "Culinary & Hospitality", "Medicine & Health", "Arts & Humanities", "Law"] for m in majors)
    if is_non_it and not any(f in compat_map for f in all_fields):
        best_relevance = 0.20

    # Scale by Degree Level & Specialization Alignment
    if base_level >= 1.0:      # PhD
        score = 0.80 + 0.20 * best_relevance
    elif base_level >= 0.8:    # MSc
        score = 0.65 + 0.35 * best_relevance
    elif base_level >= 0.6:    # BSc
        score = 0.50 + 0.45 * best_relevance
    elif base_level >= 0.4:    # Diploma
        score = 0.30 + 0.40 * best_relevance
    else:
        score = 0.10 * best_relevance

    # Academic classification / Honors bonus
    if "First Class" in honors or "Distinction" in honors:
        score += 0.05
    elif "Second Class Upper" in honors:
        score += 0.02

    # Scale non-IT degree down
    if best_relevance <= 0.25:
        score = min(0.35, score * 0.40)

    return float(min(1.0, max(0.0, round(score, 4))))


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
    from ml.extractor import extract_experience_details
    cleaned = clean_text(cv_text)
    exp_details = extract_experience_details(cleaned, target_role=target_role)
    total_exp_years = exp_details["total_experience_years"]
    relevant_exp_years = exp_details["role_relevant_experience_years"]
    
    edu_info = extract_education_level(cleaned)
    skills_certs = extract_skills_and_certifications(cleaned)

    detected_skills = skills_certs["detected_skills"]
    detected_certs = skills_certs["detected_certs"]

    # Compute Core Scores using Role-Relevant Experience and Education Relevance
    s_skill = compute_s_skill(detected_skills, target_role)
    s_exp = compute_s_exp(relevant_exp_years, target_role)
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
    # [S_edu, S_exp, S_skill, skill_count, cert_count, project_count, relevant_exp_years, edu_level_score, + 20 role overlap dimensions]
    vector = [
        s_edu,
        s_exp,
        s_skill,
        skill_count,
        cert_count,
        project_count,
        relevant_exp_years,
        edu_info.get("level_score", 0.0)
    ] + role_overlaps

    return {
        "cleaned_text": cleaned,
        "experience_years": relevant_exp_years,
        "total_experience_years": total_exp_years,
        "role_relevant_experience_years": relevant_exp_years,
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
