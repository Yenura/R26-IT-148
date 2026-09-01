"""
Job Description Requirement Extractor — Component 1
AI Resume Screening & IT Job Role Classification
IT22089236 | D T D Perera | R26-IT-148

Extracts structured job requirements from raw Job Description (JD) text:
- Target Job Title & Canonical Role Mapping
- Required Skills vs Preferred / Nice-to-Have Skills
- Required Years of Experience & Preferred Years
- Required Education Level & Major
- Preferred Certifications
- Core Responsibilities
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data.role_requirements import ALL_ROLES, REQUIRED_SKILLS, REQUIRED_YEARS
from ml.lexicon import ALL_TECHNICAL_SKILLS, CERTIFICATIONS_LIST, SKILL_ALIASES, SKILL_LEXICON

logger = logging.getLogger("component1.job_extractor")


@dataclass
class JobRequirements:
    job_title:                   str
    canonical_role:              str
    required_skills:             List[str] = field(default_factory=list)
    preferred_skills:            List[str] = field(default_factory=list)
    required_experience_years:   float = 3.0
    preferred_experience_years:  float = 5.0
    required_education:          List[str] = field(default_factory=list)
    required_seniority:          str = "Mid"
    preferred_certifications:    List[str] = field(default_factory=list)
    responsibilities:            List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_title": self.job_title,
            "canonical_role": self.canonical_role,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "required_experience_years": self.required_experience_years,
            "preferred_experience_years": self.preferred_experience_years,
            "required_education": self.required_education,
            "required_seniority": self.required_seniority,
            "preferred_certifications": self.preferred_certifications,
            "responsibilities": self.responsibilities,
        }


def extract_job_requirements(
    job_description: Optional[str] = None,
    job_spec: Optional[Dict[str, Any]] = None,
    target_role: Optional[str] = None,
) -> JobRequirements:
    """Extract or resolve job requirements from raw text, structured spec, or target role fallback."""
    # 1. If explicit structured spec provided
    if job_spec and isinstance(job_spec, dict):
        role = job_spec.get("role") or job_spec.get("canonical_role") or target_role or "Software Engineer"
        if role not in ALL_ROLES:
            role = map_title_to_canonical_role(role)

        req_skills = job_spec.get("required_skills") or REQUIRED_SKILLS.get(role, [])
        pref_skills = job_spec.get("preferred_skills") or []
        req_yrs = float(job_spec.get("required_experience_years") or REQUIRED_YEARS.get(role, 3.0))
        pref_yrs = float(job_spec.get("preferred_experience_years") or (req_yrs + 2.0))
        req_edu = job_spec.get("required_education") or ["BSc in Computer Science or related field"]
        sen = job_spec.get("required_seniority") or ("Senior" if req_yrs >= 5.0 else ("Junior" if req_yrs < 2.0 else "Mid"))

        return JobRequirements(
            job_title=job_spec.get("title") or job_spec.get("job_title") or role,
            canonical_role=role,
            required_skills=req_skills,
            preferred_skills=pref_skills,
            required_experience_years=req_yrs,
            preferred_experience_years=pref_yrs,
            required_education=req_edu,
            required_seniority=sen,
            preferred_certifications=job_spec.get("preferred_certifications", []),
            responsibilities=job_spec.get("responsibilities", [])
        )

    # 2. If raw JD text provided, parse it dynamically
    if job_description and job_description.strip():
        return _parse_raw_job_description(job_description, target_role=target_role)

    # 3. Default fallback to canonical role requirements
    resolved_role = target_role if (target_role and target_role in ALL_ROLES) else "Software Engineer"
    req_skills = REQUIRED_SKILLS.get(resolved_role, ["python", "git", "rest apis", "sql"])
    req_years = REQUIRED_YEARS.get(resolved_role, 3.0)

    return JobRequirements(
        job_title=resolved_role,
        canonical_role=resolved_role,
        required_skills=req_skills,
        preferred_skills=[],
        required_experience_years=req_years,
        preferred_experience_years=req_years + 2.0,
        required_education=["BSc in Computer Science, Software Engineering, or IT"],
        required_seniority="Senior" if req_years >= 5.0 else ("Junior" if req_years < 2.0 else "Mid"),
        preferred_certifications=[],
        responsibilities=[]
    )


def map_title_to_canonical_role(title: str) -> str:
    """Map arbitrary job title string to one of the 20 canonical IT roles."""
    if not title:
        return "Software Engineer"

    lowered = title.lower()

    # Exact role matches
    for role in ALL_ROLES:
        if role.lower() == lowered:
            return role

    mapping_rules = [
        (r'\b(machine\s+learning|ml\s+engineer)\b', "Machine Learning Engineer"),
        (r'\b(data\s+scientist|data\s+science)\b', "Data Scientist"),
        (r'\b(data\s+engineer|big\s+data)\b', "Data Engineer"),
        (r'\b(devops|dev\s+ops|site\s+reliability|sre)\b', "DevOps Engineer"),
        (r'\b(cloud\s+architect|cloud\s+solutions)\b', "Cloud Solutions Architect"),
        (r'\b(cybersecurity|security\s+analyst|infosec|soc\s+analyst)\b', "Cybersecurity Analyst"),
        (r'\b(database|dba|sql\s+developer)\b', "Database Administrator"),
        (r'\b(frontend|front-end|react\s+developer|ui\s+developer)\b', "Frontend Developer"),
        (r'\b(backend|back-end|api\s+developer|node\s+developer|python\s+developer)\b', "Backend Developer"),
        (r'\b(full\s*stack|full-stack|mern|mean)\b', "Full Stack Developer"),
        (r'\b(mobile|android|ios|flutter|react\s+native)\b', "Mobile App Developer"),
        (r'\b(qa|quality\s+assurance|test\s+automation|sdet|software\s+tester)\b', "QA/Test Automation Engineer"),
        (r'\b(ui\/ux|ux\s+designer|product\s+designer|interaction\s+designer)\b', "UI/UX Designer"),
        (r'\b(network\s+engineer|network\s+administrator|cisco)\b', "Network Engineer"),
        (r'\b(business\s+analyst|systems\s+analyst|product\s+owner)\b', "Business/Systems Analyst"),
        (r'\b(nlp|natural\s+language|ai\s+engineer|llm)\b', "AI/NLP Engineer"),
        (r'\b(blockchain|smart\s+contract|web3|solidity)\b', "Blockchain Developer"),
        (r'\b(embedded|firmware|iot|microcontroller|rtos)\b', "Embedded Systems Engineer"),
        (r'\b(site\s+reliability)\b', "Site Reliability Engineer"),
        (r'\b(software\s+engineer|software\s+developer|engineer)\b', "Software Engineer"),
    ]

    for pat, role in mapping_rules:
        if re.search(pat, lowered):
            return role

    return "Software Engineer"


def _parse_raw_job_description(text: str, target_role: Optional[str] = None) -> JobRequirements:
    """Parse unstructured job description text into structured requirements."""
    lowered = text.lower()
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # 1. Job title detection
    first_few_lines = " ".join(lines[:3])
    detected_role = target_role if (target_role and target_role in ALL_ROLES) else map_title_to_canonical_role(first_few_lines)

    # 2. Section segmentation within JD
    req_lines: List[str] = []
    pref_lines: List[str] = []
    resp_lines: List[str] = []
    curr_mode = "general"

    for line in lines:
        l_low = line.lower()
        if re.search(r'\b(?:preferred|nice\s+to\s+have|bonus|desired|plus)\b', l_low):
            curr_mode = "preferred"
            continue
        elif re.search(r'\b(?:requirements?|qualifications?|must\s+have|what\s+you(?:\'ll)?\s+need|who\s+you\s+are)\b', l_low):
            curr_mode = "required"
            continue
        elif re.search(r'\b(?:responsibilities|what\s+you(?:\'ll)?\s+do|key\s+duties|role\s+overview)\b', l_low):
            curr_mode = "responsibilities"
            continue

        if curr_mode == "required":
            req_lines.append(line)
        elif curr_mode == "preferred":
            pref_lines.append(line)
        elif curr_mode == "responsibilities":
            resp_lines.append(line)

    req_text = "\n".join(req_lines) if req_lines else text
    pref_text = "\n".join(pref_lines) if pref_lines else ""

    # 3. Required skills extraction
    req_skills: Set[str] = set()
    for cat_skills in SKILL_LEXICON.values():
        for s in cat_skills:
            if re.search(r'(?:\b|_)' + re.escape(s) + r'(?:\b|_)', req_text.lower()):
                req_skills.add(SKILL_ALIASES.get(s, s))

    # Add canonical role skills if JD had few skills parsed
    canonical_skills = REQUIRED_SKILLS.get(detected_role, [])
    if len(req_skills) < 3:
        for s in canonical_skills:
            req_skills.add(s)

    # 4. Preferred skills extraction
    pref_skills: Set[str] = set()
    if pref_text:
        for cat_skills in SKILL_LEXICON.values():
            for s in cat_skills:
                if re.search(r'(?:\b|_)' + re.escape(s) + r'(?:\b|_)', pref_text.lower()):
                    norm = SKILL_ALIASES.get(s, s)
                    if norm not in req_skills:
                        pref_skills.add(norm)

    # 5. Experience requirements
    exp_matches = re.findall(r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|work|industry)?', text, re.I)
    req_years = float(exp_matches[0]) if exp_matches else REQUIRED_YEARS.get(detected_role, 3.0)
    pref_years = float(exp_matches[1]) if len(exp_matches) > 1 else req_years + 2.0

    # 6. Seniority detection from JD (Title seniority prioritized)
    title_low = first_few_lines.lower()
    if re.search(r'\b(principal|director|head\s+of)\b', title_low):
        sen = "Principal"
    elif re.search(r'\b(lead|architect|tech\s+lead)\b', title_low):
        sen = "Lead"
    elif re.search(r'\b(senior|sr\.)\b', title_low) or req_years >= 5.0:
        sen = "Senior"
    elif re.search(r'\b(intern|entry\s+level|junior|associate)\b', title_low) or req_years <= 1.0:
        sen = "Junior"
    elif re.search(r'\b(principal|director)\b', lowered):
        sen = "Principal"
    elif re.search(r'\b(tech\s+lead|team\s+lead)\b', lowered):
        sen = "Lead"
    elif re.search(r'\b(senior|sr\.)\b', lowered):
        sen = "Senior"
    else:
        sen = "Mid"

    # 7. Preferred certifications
    pref_certs = []
    for cert in CERTIFICATIONS_LIST:
        if cert in lowered:
            pref_certs.append(cert.title())

    return JobRequirements(
        job_title=detected_role,
        canonical_role=detected_role,
        required_skills=sorted(list(req_skills)),
        preferred_skills=sorted(list(pref_skills)),
        required_experience_years=req_years,
        preferred_experience_years=pref_years,
        required_education=["BSc in Computer Science, Software Engineering, or related technical discipline"],
        required_seniority=sen,
        preferred_certifications=sorted(list(set(pref_certs))),
        responsibilities=[r.strip("•-* ") for r in resp_lines if len(r.strip("•-* ")) > 10][:6]
    )
