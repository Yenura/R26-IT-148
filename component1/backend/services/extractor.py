"""
Entity extractor service — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Extracts structured fields from raw resume text using regex + keyword matching,
alias normalization, contextual evidence scoring, employment record decomposition,
role-relevant experience estimation, and seniority detection.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data.role_requirements import REQUIRED_SKILLS
from ml.extractor import (
    clean_text,
    extract_education_level,
    extract_education_details,
    extract_experience_years,
    extract_experience_details,
    extract_skills_and_certifications,
    extract_projects,
    SKILL_ALIASES,
)

logger = logging.getLogger("component1.extractor")


@dataclass
class ExtractedFeatures:
    # Core legacy fields for backward compatibility
    edu_level:                 int   = 2         # 1=Diploma, 2=BSc, 3=MSc, 4=PhD
    edu_relevance:             float = 0.5
    education:                 str   = ""
    experience_years:          float = 0.0
    skills:                    List[str] = field(default_factory=list)
    skill_evidence:            Dict[str, Any] = field(default_factory=dict)
    detected_certs:            List[str] = field(default_factory=list)
    
    # Deep understanding fields
    role_relevant_experience_years: float = 0.0
    seniority:                 str = "Mid"
    seniority_confidence:      float = 0.8
    seniority_evidence:        List[str] = field(default_factory=list)
    employment_records:        List[Dict[str, Any]] = field(default_factory=list)
    verified_certifications:   List[Dict[str, Any]] = field(default_factory=list)
    projects:                  List[Dict[str, Any]] = field(default_factory=list)
    specializations:           List[str] = field(default_factory=list)
    academic_honors:           str = "Standard"


def extract(text: str, target_role: str = "Software Engineer") -> ExtractedFeatures:
    """Extract complete structured features from resume text with deep understanding."""
    from ml.feature_engineering import compute_s_edu
    cleaned = clean_text(text)
    
    # 1. Experience & Employment Records
    exp_details = extract_experience_details(text, target_role=target_role)
    total_exp = exp_details["total_experience_years"]
    relevant_exp = exp_details["role_relevant_experience_years"]
    records = exp_details["employment_records"]
    seniority = exp_details["seniority"]
    sen_conf = exp_details["seniority_confidence"]
    sen_ev = exp_details["seniority_evidence"]

    # 2. Education & Qualifications
    edu_info = extract_education_level(text)
    edu_full = extract_education_details(text)
    level_score = edu_info.get("level_score", 0.60)
    edu_level = 2
    if level_score >= 1.0:
        edu_level = 4
    elif level_score >= 0.8:
        edu_level = 3
    elif level_score >= 0.6:
        edu_level = 2
    else:
        edu_level = 1

    majors = edu_info.get("majors", [])
    specializations = edu_info.get("specializations", [])
    academic_honors = edu_info.get("academic_honors", "Standard")
    
    # Precise role-to-specialization alignment score
    edu_relevance = compute_s_edu(edu_info, target_role=target_role)

    # Locate human readable education qualification sentence
    edu_sentence = ""
    lines = text.splitlines()
    edu_section_lines = []
    in_edu = False
    for line in lines:
        stripped = line.strip()
        if re.match(r'^(?:education|educational\s+qualifications?|academics?|academic\s+background)\b', stripped, re.I):
            in_edu = True
            continue
        elif in_edu and re.match(r'^(?:certifications?|projects?|skills?|experience|work|employment|leadership|languages?)\b', stripped, re.I):
            in_edu = False
        if in_edu and stripped:
            edu_section_lines.append(stripped)

    degree_kw = (
        "bachelor", "b.sc", "bsc", "b.s", "b.eng", "b.tech", "bit", "bcs",
        "msc", "m.sc", "m.s", "master of", "master's", "masters in",
        "phd", "ph.d", "doctorate", "diploma", "hnd", "higher national diploma"
    )

    for line in edu_section_lines:
        line_l = line.lower()
        if "scrum master" not in line_l and any(kw in line_l for kw in degree_kw):
            edu_sentence = line.strip()
            break

    if not edu_sentence:
        for line in lines:
            line_l = line.lower()
            if "scrum master" not in line_l and any(kw in line_l for kw in degree_kw):
                edu_sentence = line.strip()
                break

    if not edu_sentence or len(edu_sentence) < 5:
        spec_suffix = f" (Specializing in {specializations[0]})" if specializations else ""
        edu_sentence = f"{edu_info.get('level_name', 'BSc')} in {majors[0] if majors else 'Information Technology'}{spec_suffix}"

    # 3. Skills & Evidence
    skills_certs = extract_skills_and_certifications(text)
    projects = extract_projects(text)

    return ExtractedFeatures(
        edu_level=edu_level,
        edu_relevance=round(edu_relevance, 2),
        education=edu_sentence,
        experience_years=relevant_exp,
        skills=skills_certs["detected_skills"],
        skill_evidence=skills_certs.get("skill_evidence", {}),
        detected_certs=skills_certs.get("detected_certs", []),
        role_relevant_experience_years=relevant_exp,
        seniority=seniority,
        seniority_confidence=sen_conf,
        seniority_evidence=sen_ev,
        employment_records=records,
        verified_certifications=edu_full.get("verified_certifications", []),
        projects=projects,
        specializations=specializations,
        academic_honors=academic_honors
    )
