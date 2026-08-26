"""Entity extractor — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Extracts structured fields from raw resume text using regex + keyword matching,
alias normalization, and contextual evidence scoring.

Fields extracted:
    edu_level    : int       — 1=Diploma, 2=BSc, 3=MSc, 4=PhD
    edu_relevance: float     — 0–1 (how relevant the degree is to CS/IT/Engineering)
    experience_years: float  — years of work experience (with date interval deduplication)
    skills       : List[str] — matched normalized skill keywords
    skill_evidence: Dict     — evidence snippets and strength per skill
    education    : str       — longest education sentence found (human-readable)
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data.role_requirements import REQUIRED_SKILLS
from ml.extractor import (
    clean_text,
    extract_education_level,
    extract_experience_years,
    extract_skills_and_certifications,
    SKILL_ALIASES,
)

logger = logging.getLogger("component1.extractor")


@dataclass
class ExtractedFeatures:
    edu_level:        int   = 2         # default BSc
    edu_relevance:    float = 0.5
    education:        str   = ""
    experience_years: float = 0.0
    skills:           List[str] = field(default_factory=list)
    skill_evidence:   Dict[str, Any] = field(default_factory=dict)
    detected_certs:   List[str] = field(default_factory=list)


def extract(text: str) -> ExtractedFeatures:
    """Extract structured features from raw resume text."""
    cleaned = clean_text(text)
    
    # 1. Experience
    exp_years = extract_experience_years(cleaned)
    
    # 2. Education
    edu_info = extract_education_level(cleaned)
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
    relevant_it = {"Computer Science", "Software Engineering", "Information Technology", "Data Science", "Cybersecurity", "Networking", "Engineering"}
    edu_relevance = 1.0 if any(m in relevant_it for m in majors) else (0.8 if majors else 0.5)

    # Locate degree line within EDUCATION section if present, or search for genuine degree qualifications
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

    # 1. Search in dedicated education section first
    for line in edu_section_lines:
        line_l = line.lower()
        if "scrum master" not in line_l and any(kw in line_l for kw in degree_kw):
            edu_sentence = line.strip()
            break

    # 2. If not found, search throughout full text avoiding non-academic lines (like scrum master)
    if not edu_sentence:
        for line in lines:
            line_l = line.lower()
            if "scrum master" not in line_l and any(kw in line_l for kw in degree_kw):
                edu_sentence = line.strip()
                break

    # 3. Fallback to constructed degree name if still empty or too short
    if not edu_sentence or len(edu_sentence) < 5:
        edu_sentence = f"{edu_info.get('level_name', 'BSc')} in {majors[0] if majors else 'Information Technology'}"

    # 3. Skills & Evidence
    skills_certs = extract_skills_and_certifications(cleaned)

    return ExtractedFeatures(
        edu_level=edu_level,
        edu_relevance=edu_relevance,
        education=edu_sentence,
        experience_years=exp_years,
        skills=skills_certs["detected_skills"],
        skill_evidence=skills_certs.get("skill_evidence", {}),
        detected_certs=skills_certs.get("detected_certs", [])
    )
