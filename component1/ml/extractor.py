"""
Advanced Hybrid CV Information Extractor — Component 1
AI Resume Screening & IT Job Role Classification
IT22094872 | Dulnith K.D. | R26-IT-148

Capabilities:
1. PII Redaction & Text Normalization preserving C++, C#, .NET, Node.js, Next.js
2. Layout & Multi-Heading Section Segmentation (Experience, Education, Skills, Projects, Certs)
3. Employment Record Extraction (title, company, dates, duration, responsibilities, tech)
4. Date Parsing & Non-overlapping Interval Merging (Total Experience)
5. Target-Job Role-Relevant Experience calculation (Total vs Role-Relevant tenure)
6. Multi-Signal Seniority Detection (Intern, Junior, Mid, Senior, Lead, Principal, Architect)
7. Contextual Skill Evidence Engine (HIGH, MEDIUM, LOW)
8. Deep Education & Recognized Certification Extraction vs Unverified Training
9. Project & Metric-Driven Achievement Extraction
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from ml.lexicon import (
        ALL_TECHNICAL_SKILLS,
        CANONICAL_CERTIFICATIONS,
        CERTIFICATIONS_LIST,
        RELATED_SKILLS_GRAPH,
        SKILL_ALIASES,
        SKILL_LEXICON,
    )
except ImportError:
    from component1.ml.lexicon import (
        ALL_TECHNICAL_SKILLS,
        CANONICAL_CERTIFICATIONS,
        CERTIFICATIONS_LIST,
        RELATED_SKILLS_GRAPH,
        SKILL_ALIASES,
        SKILL_LEXICON,
    )


CURRENT_YEAR = 2026.0

# ── Precompiled Regexes ────────────────────────────────────────────────────────
_EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
_PHONE_RE = re.compile(r'\+?\d[\d\s\-\(\)]{8,}\d')
_URL_RE = re.compile(r'https?://\S+|www\.\S+')
_ZIP_RE = re.compile(r'\b\d{5}(?:[-\s]\d{4})?\b')
_SPACE_RE = re.compile(r'[ \t]+')

_PHD_RE = re.compile(r'\b(ph\.?d\.?|doctor of philosophy|doctorate|d\.?phil)\b', re.I)
_MSC_RE = re.compile(r'\b(m\.?sc\.?|m\.?s\.?|master(?:[\'’]?s)?|m\.?tech\.?|m\.?eng\.?|mca|postgraduate|pgd|post[\s-]graduate)\b', re.I)
_BSC_RE = re.compile(r'\b(b\.?sc\.?|b\.?s\.?|bachelor(?:[\'’]?s)?|b\.?tech\.?|b\.?e\.?|b\.?eng\.?|bca|bit|bcs|undergraduate|degree(?:\s+in)?)\b', re.I)
_DIP_RE = re.compile(r'\b(diploma|higher national diploma|hnd|nvq|national diploma|ndt|higher diploma|associate degree)\b', re.I)

# Skill matching patterns (escaped with boundary protection)
_SKILL_PATTERNS = {
    skill: re.compile(r'(?:\b|_)' + re.escape(skill) + r'(?:\b|_)', re.I)
    for skill in ALL_TECHNICAL_SKILLS
}

_CERT_PATTERNS = [
    (cert, re.compile(r'(?:\b|_)' + re.escape(cert) + r'(?:\b|_)', re.I))
    for cert in CERTIFICATIONS_LIST
]

_ACTION_VERBS = {
    "developed", "built", "engineered", "designed", "architected",
    "implemented", "maintained", "deployed", "optimized", "scaled",
    "configured", "tested", "automated", "authored", "led", "spearheaded",
    "orchestrated", "refactored", "migrated", "mentored", "directed", "managed"
}

_LEADERSHIP_VERBS = {
    "led", "lead", "spearheaded", "mentored", "managed", "directed",
    "architected", "orchestrated", "headed", "supervised", "oversaw"
}

# ── Role Compatibility Matrix (Target Role <-> Past Titles) ────────────────────
ROLE_COMPATIBILITY: Dict[str, Dict[str, float]] = {
    "Software Engineer": {
        "software engineer": 1.0, "software developer": 1.0, "full stack developer": 0.95,
        "backend developer": 0.90, "frontend developer": 0.85, "systems engineer": 0.85,
        "application developer": 0.90, "programmer": 0.85, "qa engineer": 0.50, "devops": 0.60
    },
    "Backend Developer": {
        "backend developer": 1.0, "backend engineer": 1.0, "software engineer": 0.85,
        "full stack developer": 0.85, "api developer": 0.95, "database administrator": 0.70,
        "frontend developer": 0.35, "devops engineer": 0.65, "data engineer": 0.75
    },
    "Frontend Developer": {
        "frontend developer": 1.0, "frontend engineer": 1.0, "web developer": 0.95,
        "ui developer": 0.95, "full stack developer": 0.85, "ui/ux designer": 0.70,
        "backend developer": 0.35, "software engineer": 0.80
    },
    "Full Stack Developer": {
        "full stack developer": 1.0, "full stack engineer": 1.0, "software engineer": 0.90,
        "backend developer": 0.85, "frontend developer": 0.85, "web developer": 0.85
    },
    "Data Scientist": {
        "data scientist": 1.0, "machine learning engineer": 0.90, "data analyst": 0.80,
        "ai engineer": 0.85, "statistician": 0.85, "business intelligence": 0.70,
        "data engineer": 0.75, "software engineer": 0.50
    },
    "Machine Learning Engineer": {
        "machine learning engineer": 1.0, "ml engineer": 1.0, "data scientist": 0.90,
        "ai engineer": 0.95, "nlp engineer": 0.90, "computer vision engineer": 0.90,
        "software engineer": 0.70, "data engineer": 0.75
    },
    "DevOps Engineer": {
        "devops engineer": 1.0, "site reliability engineer": 0.95, "sre": 0.95,
        "cloud engineer": 0.90, "infrastructure engineer": 0.90, "systems administrator": 0.80,
        "software engineer": 0.65, "backend developer": 0.60
    },
    "Cloud Solutions Architect": {
        "cloud solutions architect": 1.0, "cloud architect": 1.0, "cloud engineer": 0.85,
        "solutions architect": 0.95, "enterprise architect": 0.90, "devops engineer": 0.80,
        "systems engineer": 0.75
    },
    "Site Reliability Engineer": {
        "site reliability engineer": 1.0, "sre": 1.0, "devops engineer": 0.95,
        "infrastructure engineer": 0.90, "systems engineer": 0.85, "linux administrator": 0.80
    },
    "Database Administrator": {
        "database administrator": 1.0, "dba": 1.0, "database engineer": 0.95,
        "data engineer": 0.80, "sql developer": 0.85, "backend developer": 0.60
    },
    "Data Engineer": {
        "data engineer": 1.0, "big data engineer": 1.0, "etl developer": 0.95,
        "database developer": 0.80, "data scientist": 0.75, "backend developer": 0.70
    },
    "Cybersecurity Analyst": {
        "cybersecurity analyst": 1.0, "security engineer": 0.95, "soc analyst": 0.95,
        "penetration tester": 0.90, "information security analyst": 0.95, "network engineer": 0.70
    },
    "Network Engineer": {
        "network engineer": 1.0, "network administrator": 0.95, "network architect": 0.95,
        "systems administrator": 0.75, "infrastructure engineer": 0.80, "security engineer": 0.70
    },
    "QA/Test Automation Engineer": {
        "qa engineer": 1.0, "test automation engineer": 1.0, "quality assurance": 0.95,
        "sdet": 1.0, "software tester": 0.90, "software engineer": 0.70
    },
    "Mobile App Developer": {
        "mobile developer": 1.0, "android developer": 1.0, "ios developer": 1.0,
        "react native developer": 1.0, "flutter developer": 1.0, "software engineer": 0.80
    },
    "UI/UX Designer": {
        "ui/ux designer": 1.0, "product designer": 0.95, "ux researcher": 0.90,
        "ui designer": 0.95, "web designer": 0.85, "frontend developer": 0.65
    },
    "Business/Systems Analyst": {
        "business analyst": 1.0, "systems analyst": 1.0, "product owner": 0.85,
        "scrum master": 0.75, "it consultant": 0.80, "project manager": 0.75
    },
    "AI/NLP Engineer": {
        "nlp engineer": 1.0, "ai engineer": 0.95, "machine learning engineer": 0.90,
        "data scientist": 0.85, "research engineer": 0.85
    },
    "Blockchain Developer": {
        "blockchain developer": 1.0, "smart contract engineer": 1.0, "web3 developer": 0.95,
        "crypto engineer": 0.90, "software engineer": 0.75, "backend developer": 0.75
    },
    "Embedded Systems Engineer": {
        "embedded systems engineer": 1.0, "firmware engineer": 1.0, "embedded software": 0.95,
        "hardware engineer": 0.85, "iot engineer": 0.90, "systems engineer": 0.80
    }
}


def clean_text(text: str) -> str:
    """Clean CV text by removing PII while strictly preserving technical symbols (C++, C#, .NET, Node.js)."""
    if not text:
        return ""

    text = _EMAIL_RE.sub(' ', text)
    text = _PHONE_RE.sub(' ', text)
    text = _URL_RE.sub(' ', text)
    text = _ZIP_RE.sub(' ', text)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return '\n'.join(lines).strip()


# ── Section Segmentation ───────────────────────────────────────────────────────

SECTION_PATTERNS = {
    "experience": re.compile(
        r'^(?:professional\s+experience|work\s+experience|employment\s+history|career\s+history|'
        r'work\s+history|professional\s+background|relevant\s+experience|practical\s+experience|experience)\b',
        re.I
    ),
    "education": re.compile(
        r'^(?:educational\s+background|academic\s+background|educational\s+qualifications?|'
        r'academic\s+qualifications?|education|academics?|schooling|degrees?)\b',
        re.I
    ),
    "skills": re.compile(
        r'^(?:technical\s+skills?|core\s+competencies|technologies|tech\s+stack|programming\s+languages?|'
        r'key\s+skills?|skills\s+and\s+abilities|areas\s+of\s+expertise|skills?)\b',
        re.I
    ),
    "projects": re.compile(
        r'^(?:key\s+projects?|academic\s+projects?|personal\s+projects?|technical\s+projects?|'
        r'portfolio|projects?)\b',
        re.I
    ),
    "certifications": re.compile(
        r'^(?:licenses\s+and\s+certifications|professional\s+certifications?|credentials?|'
        r'certifications?|accreditations?)\b',
        re.I
    ),
    "summary": re.compile(
        r'^(?:executive\s+summary|professional\s+summary|career\s+objective|profile|summary|about\s+me)\b',
        re.I
    )
}


def extract_sections(text: str) -> Dict[str, str]:
    """Segment document text into semantic sections using comprehensive heading aliases."""
    if not text:
        return {}

    lines = text.splitlines()
    sections: Dict[str, List[str]] = {
        "header": [], "summary": [], "experience": [], "education": [],
        "skills": [], "projects": [], "certifications": [], "other": []
    }

    current_sec = "header"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        matched_section = None
        for sec_name, pat in SECTION_PATTERNS.items():
            if pat.match(stripped):
                matched_section = sec_name
                break

        if matched_section:
            current_sec = matched_section
            continue

        sections[current_sec].append(stripped)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


# ── Employment Record & Experience Extraction ──────────────────────────────────

_MONTH_MAP = {
    'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
    'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
    'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
    'nov': 11, 'november': 11, 'dec': 12, 'december': 12
}


def _parse_date_range(text: str) -> Optional[Tuple[float, float, bool]]:
    """Parse start date, end date, and is_current flag from string in years (decimal)."""
    m_re = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
    date_pat = (
        r'\b(?:(' + m_re + r')\s+)?(20[0-2]\d|19[8-9]\d)\s*(?:-|–|—|to)\s*'
        r'(?:(' + m_re + r')\s+)?(present|current|now|till\s+date|ongoing|20[0-2]\d|19[8-9]\d)\b'
    )
    m = re.search(date_pat, text, re.I)
    if m:
        sm_str, sy_str, em_str, ey_str = m.groups()
        start_yr = int(sy_str)
        start_month = _MONTH_MAP.get(sm_str.lower()[:3], 1) if sm_str else 1
        start_val = start_yr + (start_month - 1) / 12.0

        is_current = any(w in ey_str.lower() for w in ('present', 'current', 'now', 'till', 'ongoing'))
        if is_current:
            end_val = CURRENT_YEAR
        else:
            end_yr = int(ey_str)
            end_month = _MONTH_MAP.get(em_str.lower()[:3], 12) if em_str else 12
            end_val = end_yr + (end_month - 1) / 12.0

        if end_val >= start_val and (end_val - start_val) <= 40.0:
            return start_val, end_val, is_current

    # Numeric "MM/YYYY - MM/YYYY"
    m_num = re.search(
        r'\b(\d{1,2})[\/\.-](20[0-2]\d|19[8-9]\d)\s*(?:-|–|—|to)\s*'
        r'(?:(\d{1,2})[\/\.-](20[0-2]\d|19[8-9]\d)|(present|current|now|ongoing))\b',
        text, re.I
    )
    if m_num:
        sm, sy, em, ey, curr = m_num.groups()
        start_val = int(sy) + (int(sm) - 1) / 12.0
        if curr:
            return start_val, CURRENT_YEAR, True
        elif ey and em:
            end_val = int(ey) + (int(em) - 1) / 12.0
            if end_val >= start_val and (end_val - start_val) <= 40.0:
                return start_val, end_val, False

    return None


def extract_employment_records(text: str, target_role: str = "Software Engineer") -> List[Dict[str, Any]]:
    """Extract individual employment records with title, company, dates, responsibilities, and role relevance."""
    sections = extract_sections(text)
    exp_text = sections.get("experience", "")
    if not exp_text:
        # Fallback to whole text if sections not partitioned
        exp_text = text

    lines = exp_text.splitlines()
    records: List[Dict[str, Any]] = []
    current_record: Optional[Dict[str, Any]] = None

    title_indicators = [
        "developer", "engineer", "architect", "lead", "analyst", "administrator",
        "consultant", "intern", "manager", "specialist", "scientist", "programmer", "designer",
        "accountant", "auditor", "bookkeeper", "cashier", "chef", "cook", "nurse", "officer",
        "executive", "representative", "associate", "coordinator", "assistant", "teacher",
        "trainee", "director", "head", "supervisor"
    ]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        date_res = _parse_date_range(stripped)
        is_title_line = any(re.search(r'\b' + re.escape(ind) + r'\b', stripped.lower()) for ind in title_indicators)

        if is_title_line and not stripped.startswith(('•', '-', '*', '—')):
            # Push previous record
            if current_record and current_record.get("job_title"):
                records.append(current_record)

            title_candidate = stripped
            company_candidate = "Technology Organization"

            # Parse title & company if "at" or "|" or "-" separates them
            for sep in [" at ", " @ ", " - ", " | ", ", "]:
                if sep in stripped:
                    parts = stripped.split(sep, 1)
                    if any(re.search(r'\b' + re.escape(ind) + r'\b', parts[0].lower()) for ind in title_indicators):
                        title_candidate = parts[0].strip()
                        company_candidate = parts[1].strip()
                        break
                    elif any(re.search(r'\b' + re.escape(ind) + r'\b', parts[1].lower()) for ind in title_indicators):
                        title_candidate = parts[1].strip()
                        company_candidate = parts[0].strip()
                        break

            start_v, end_v, is_curr = date_res if date_res else (0.0, 0.0, False)
            duration_months = round(max(0.0, (end_v - start_v) * 12.0), 1) if date_res else 12.0

            current_record = {
                "job_title": title_candidate,
                "company": company_candidate,
                "start_year": round(start_v, 2),
                "end_year": round(end_v, 2),
                "duration_months": duration_months,
                "is_current": is_curr,
                "has_explicit_dates": bool(date_res),
                "responsibilities": [],
                "technologies": []
            }
        elif date_res and current_record and not current_record.get("has_explicit_dates"):
            # Update dates of the current title record
            start_v, end_v, is_curr = date_res
            current_record["start_year"] = round(start_v, 2)
            current_record["end_year"] = round(end_v, 2)
            current_record["duration_months"] = round(max(0.0, (end_v - start_v) * 12.0), 1)
            current_record["is_current"] = is_curr
            current_record["has_explicit_dates"] = True
        else:
            if current_record:
                # Add responsibility bullet
                clean_bullet = re.sub(r'^[•\-\*\—\>\s]+', '', stripped).strip()
                if len(clean_bullet) > 10:
                    current_record["responsibilities"].append(clean_bullet)
                    # Check technologies inside bullet
                    bullet_l = clean_bullet.lower()
                    for cat_skills in SKILL_LEXICON.values():
                        for s in cat_skills:
                            if s in bullet_l and s not in current_record["technologies"]:
                                current_record["technologies"].append(SKILL_ALIASES.get(s, s))

    if current_record and current_record.get("job_title"):
        records.append(current_record)

    # Non-IT role keywords for zero-relevance filtering
    non_it_keywords = {
        "accountant", "accounting", "auditor", "bookkeeper", "cashier", "financial analyst",
        "chef", "cook", "baker", "waiter", "waitress", "bartender", "culinary",
        "nurse", "doctor", "physician", "pharmacist", "therapist", "medical",
        "driver", "chauffeur", "delivery", "warehouse", "logistics coordinator",
        "sales representative", "sales executive", "retail associate", "store manager",
        "teacher", "history", "english literature", "tutor", "counselor",
        "lawyer", "attorney", "paralegal", "legal assistant",
        "construction", "electrician", "plumber", "carpenter"
    }

    general_it_keywords = {
        "software", "developer", "engineer", "programmer", "architect", "analyst", "devops",
        "data", "frontend", "backend", "fullstack", "full stack", "cloud", "security",
        "admin", "dba", "sre", "qa", "tester", "mobile", "ios", "android", "ai", "ml", "tech"
    }

    # Compute role relevance for each employment record
    compat_map = ROLE_COMPATIBILITY.get(target_role, {})
    for rec in records:
        t_low = rec["job_title"].lower()
        rel_factor = 0.0  # default zero relevance for unverified/non-IT roles

        # Check explicit compatibility mapping for target role
        for role_key, score in compat_map.items():
            if role_key in t_low:
                rel_factor = max(rel_factor, score)

        # If not explicitly mapped, check whether it is a non-IT role or general IT role
        if rel_factor == 0.0:
            is_non_it = any(re.search(r'\b' + re.escape(kw) + r'\b', t_low) for kw in non_it_keywords)
            has_it_kw = any(re.search(r'\b' + re.escape(kw) + r'\b', t_low) for kw in general_it_keywords)
            if has_it_kw and not is_non_it:
                rel_factor = 0.70
            elif is_non_it:
                rel_factor = 0.0
            else:
                # Check technologies in this employment period
                if len(rec.get("technologies", [])) >= 2:
                    rel_factor = 0.60
                else:
                    rel_factor = 0.0

        rec["relevance_to_target_role"] = round(rel_factor, 2)
        rec["relevant_months"] = round(rec["duration_months"] * rel_factor, 1)

    return records


def extract_experience_years(text: str) -> float:
    """High-accuracy multi-strategy experience extraction with chronological date interval merging."""
    if not text:
        return 0.0

    lowered = text.lower()
    candidates: List[float] = []

    # 1. Explicit experience statements
    explicit_patterns = [
        r'(?:total\s+|professional\s+|work\s+|industry\s+)?experience\s*[:\-]?\s*(?:over\s+|more\s+than\s+)?(\d+(?:\.\d+)?)\s*\+?\s*(years?|yrs?|months?|mos?)',
        r'(\d+(?:\.\d+)?)\s*\+?\s*(years?|yrs?|months?|mos?)\s+(?:of\s+)?(?:experience|work|industry|field|background)',
        r'with\s+(\d+(?:\.\d+)?)\s*\+?\s*(years?|yrs?|months?|mos?)(?:\'?s?)?\s+(?:industry|professional|work)?\s*experience',
        r'(?:worked|working)\s+(?:for\s+)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
        r'over\s+(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+in\b',
        r'(?:intern|internship|trainee|developer|engineer|analyst|associate|lead|manager|consultant)\s*\((\d+(?:\.\d+)?)\s*(years?|yrs?|months?|mos?)\)',
    ]
    for pattern in explicit_patterns:
        for m in re.finditer(pattern, lowered):
            try:
                val = float(m.group(1))
                unit = m.group(2) if len(m.groups()) >= 2 else "years"
                if unit and 'm' in unit.lower():
                    val = val / 12.0
                if 0.1 <= val <= 45.0:
                    candidates.append(round(val, 2))
            except (ValueError, IndexError):
                pass

    # 2. Extract sections & non-overlapping intervals
    sections = extract_sections(text)
    work_text = sections.get("experience", "")

    # Fallback if no explicit work section header: exclude lines clearly belonging to education or school
    if not work_text:
        filtered_lines = []
        is_edu = False
        for l in text.splitlines():
            ll = l.strip().lower()
            if re.match(r'^(?:educational\s+background|academic\s+background|educational\s+qualifications?|academic\s+qualifications?|education|academics?|schooling|degrees?)\b', ll):
                is_edu = True
                continue
            elif re.match(r'^(?:projects?|key\s+projects?|skills?|certifications?)\b', ll):
                is_edu = False
            if is_edu:
                continue
            if any(kw in ll for kw in ['school', 'ordinary level', 'advanced level', 'g.c.e', 'o/l', 'a/l', 'sliit', 'bsc', 'msc', 'bachelor', 'undergraduate', 'university', 'college', 'degree', 'hospital management']):
                continue
            filtered_lines.append(l.strip())
        work_text = '\n'.join(filtered_lines)

    intervals: List[Tuple[float, float]] = []

    # 3. Numeric Date Ranges (e.g. "01/2020 - 05/2023", "2018.06 - 2022.08")
    for sm, sy, em, ey in re.findall(r'\b(\d{1,2})[\/\.-](20[0-2]\d|19[8-9]\d)\s*(?:-|–|—|to)\s*(\d{1,2})[\/\.-](20[0-2]\d|19[8-9]\d)\b', work_text.lower()):
        try:
            start_val = int(sy) + (int(sm) - 1) / 12.0
            end_val = int(ey) + (int(em) - 1) / 12.0
            if end_val >= start_val and (end_val - start_val) <= 40:
                intervals.append((start_val, end_val))
        except (ValueError, TypeError):
            pass

    for sy, sm, ey, em in re.findall(r'\b(20[0-2]\d|19[8-9]\d)[\/\.-](\d{1,2})\s*(?:-|–|—|to)\s*(20[0-2]\d|19[8-9]\d)[\/\.-](\d{1,2})\b', work_text.lower()):
        try:
            start_val = int(sy) + (int(sm) - 1) / 12.0
            end_val = int(ey) + (int(em) - 1) / 12.0
            if end_val >= start_val and (end_val - start_val) <= 40:
                intervals.append((start_val, end_val))
        except (ValueError, TypeError):
            pass

    # 4. Standard Date Ranges (e.g. "Jan 2020 - Dec 2023", "2021 - Present")
    m_re = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
    date_pat = (
        r'\b(?:(' + m_re + r')\s+)?(20[0-2]\d|19[8-9]\d)\s*(?:-|–|—|to)\s*'
        r'(?:(' + m_re + r')\s+)?(present|current|now|till\s+date|ongoing|20[0-2]\d|19[8-9]\d)\b'
    )

    for sm, sy, em, ey in re.findall(date_pat, work_text.lower()):
        try:
            start_yr = int(sy)
            end_yr = int(CURRENT_YEAR) if any(w in str(ey).lower() for w in ('present', 'current', 'now', 'till', 'ongoing')) else int(ey)
            if start_yr <= end_yr and (end_yr - start_yr) <= 40:
                intervals.append((float(start_yr), float(end_yr)))
        except (ValueError, TypeError):
            pass


    # Merge intervals
    if intervals:
        intervals.sort(key=lambda x: x[0])
        merged: List[List[float]] = []
        for s, e in intervals:
            if not merged:
                merged.append([s, e])
            else:
                if s <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], e)
                else:
                    merged.append([s, e])
        total_span = sum(e - s for s, e in merged)
        if total_span > 0:
            candidates.append(round(total_span, 1))

    # 3. Month patterns
    month_patterns = [
        r'(\d{1,2})\s*\+?\s*(?:months?|mos?)\s+(?:of\s+)?(?:experience|work|internship)',
        r'(?:intern|internship|developer|engineer|analyst|associate)\s*\((\d{1,2})\s*(?:months?|mos?)\)',
        r'\b(\d{1,2})\s*(?:months?|mos?)\s+(?:internship|contract|tenure)\b',
    ]
    for pattern in month_patterns:
        for m in re.findall(pattern, work_text.lower()):
            try:
                val = float(m) / 12.0
                if 0.15 <= val <= 5.0:
                    candidates.append(round(val, 2))
            except ValueError:
                pass

    if candidates:
        return max(candidates)

    return 0.0


def extract_experience_details(text: str, target_role: str = "Software Engineer") -> Dict[str, Any]:
    """Calculate Total Experience and Role-Relevant Experience separately against the target role."""
    records = extract_employment_records(text, target_role)
    total_exp_years = extract_experience_years(text)

    # Compute non-overlapping relevant experience
    if records:
        rec_total_years = sum(r.get("duration_months", 0.0) for r in records) / 12.0
        rec_relevant_years = sum(r.get("relevant_months", 0.0) for r in records) / 12.0
        if rec_total_years > 0:
            total_exp_years = round(max(total_exp_years, rec_total_years), 2)
            relevant_exp_years = round(rec_relevant_years, 2)
        else:
            relevant_exp_years = total_exp_years
    else:
        relevant_exp_years = total_exp_years

    seniority_info = detect_seniority(records, relevant_exp_years, text)

    return {
        "total_experience_years": round(total_exp_years, 2),
        "role_relevant_experience_years": round(relevant_exp_years, 2),
        "employment_records": records,
        "seniority": seniority_info["seniority"],
        "seniority_confidence": seniority_info["confidence"],
        "seniority_evidence": seniority_info["evidence"]
    }


def detect_seniority(records: List[Dict[str, Any]], relevant_years: float, text: str) -> Dict[str, Any]:
    """Multi-signal seniority detection combining title keywords, years of experience, and leadership signals."""
    lowered = text.lower()

    # Leadership verb counts
    lead_count = sum(1 for v in _LEADERSHIP_VERBS if re.search(r'\b' + re.escape(v) + r'\b', lowered))
    has_leadership = lead_count >= 2

    # Check job titles in records
    all_titles = " ".join([r.get("job_title", "").lower() for r in records])

    if any(kw in all_titles for kw in ["principal", "director", "head of", "distinguished", "vp "]):
        return {"seniority": "Principal", "confidence": 0.95, "evidence": ["Executive/Principal title in history"]}
    elif any(kw in all_titles for kw in ["architect", "chief"]):
        return {"seniority": "Architect", "confidence": 0.92, "evidence": ["Architectural title in history"]}
    elif any(kw in all_titles for kw in ["tech lead", "team lead", "engineering lead", "lead engineer"]):
        return {"seniority": "Lead", "confidence": 0.90, "evidence": ["Leadership/Lead title in history"]}
    elif any(kw in all_titles for kw in ["senior", "sr."]) or (relevant_years >= 5.0 and has_leadership):
        return {"seniority": "Senior", "confidence": 0.88, "evidence": [f"Senior title or tenure ({relevant_years}y) with leadership verbs"]}
    elif any(kw in all_titles for kw in ["intern", "trainee", "associate"]):
        return {"seniority": "Junior", "confidence": 0.85, "evidence": ["Intern/Junior/Associate level in title"]}
    else:
        # Infer based on relevant experience tenure
        if relevant_years >= 7.0:
            return {"seniority": "Lead" if has_leadership else "Senior", "confidence": 0.80, "evidence": [f"{relevant_years} years relevant experience"]}
        elif relevant_years >= 4.0:
            return {"seniority": "Senior", "confidence": 0.75, "evidence": [f"{relevant_years} years relevant experience"]}
        elif relevant_years >= 1.5:
            return {"seniority": "Mid", "confidence": 0.75, "evidence": [f"{relevant_years} years relevant experience"]}
        else:
            return {"seniority": "Junior", "confidence": 0.70, "evidence": [f"{relevant_years} years relevant experience"]}


# ── Education & Certification Extraction ───────────────────────────────────────

def extract_education_level(text: str) -> Dict[str, Any]:
    """Extract education degree level (PhD=4, MSc=3, BSc=2, Diploma=1) and major field."""
    if not text:
        return {"level_score": 0.0, "level_name": "None", "major": "None", "majors": ["General IT"]}

    lowered = text.lower()
    level_score = 0.60
    level_name = "BSc"

    if _PHD_RE.search(lowered):
        level_score = 1.00
        level_name = "PhD"
    elif _MSC_RE.search(lowered):
        level_score = 0.80
        level_name = "MSc"
    elif _BSC_RE.search(lowered):
        level_score = 0.60
        level_name = "BSc"
    elif _DIP_RE.search(lowered):
        level_score = 0.40
        level_name = "Diploma"
    elif any(w in lowered for w in ('university', 'college', 'institute', 'faculty', 'campus', 'graduated', 'alumni', 'degree')):
        level_score = 0.60
        level_name = "BSc"
    else:
        level_score = 0.40
        level_name = "Diploma"

    majors = []
    major_patterns = {
        "Computer Science": (r'computer science', r'\bcs\b', r'computing', r'computer studies', r'computer systems'),
        "Software Engineering": (r'software engineering', r'\bse\b', r'software development', r'software systems'),
        "Information Technology": (r'information technology', r'\bit\b', r'information systems', r'\bict\b', r'\bbit\b'),
        "Data Science": (r'data science', r'analytics', r'big data', r'data engineering', r'business intelligence'),
        "Cybersecurity": (r'cybersecurity', r'cyber security', r'information security', r'network security'),
        "Networking": (r'network engineering', r'telecommunications', r'computer networks', r'cloud architecture'),
        "Engineering": (r'computer engineering', r'electrical engineering', r'electronic engineering', r'systems engineering', r'engineering')
    }

    non_it_major_patterns = {
        "Accounting & Finance": (r'accounting', r'finance', r'banking', r'commerce', r'accountancy'),
        "Business Administration": (r'business administration', r'\bmba\b', r'\bbba\b', r'marketing', r'management', r'human resources'),
        "Culinary & Hospitality": (r'culinary', r'hospitality', r'hotel management', r'catering'),
        "Medicine & Health": (r'nursing', r'medicine', r'pharmacy', r'medical', r'healthcare'),
        "Arts & Humanities": (r'history', r'english', r'literature', r'philosophy', r'fine arts', r'psychology', r'sociology'),
        "Law": (r'law', r'\bllb\b', r'\bllm\b', r'legal studies')
    }

    # Deep Specialization / Concentration / Track Extraction
    specializations = []
    spec_patterns = {
        "Data Science & AI": (
            r'speciali[zs](?:ing|ation)?\s+in\s+data\s+science',
            r'speciali[zs](?:ing|ation)?\s+in\s+(?:ai|artificial intelligence|machine learning|deep learning)',
            r'track[:\s]+data\s+science', r'concentration[:\s]+data\s+science', r'major\s+in\s+data\s+science'
        ),
        "Cybersecurity": (
            r'speciali[zs](?:ing|ation)?\s+in\s+cyber\s*security',
            r'speciali[zs](?:ing|ation)?\s+in\s+information\s+security',
            r'track[:\s]+cyber\s*security', r'concentration[:\s]+security', r'major\s+in\s+cybersecurity'
        ),
        "Cloud & DevOps": (
            r'speciali[zs](?:ing|ation)?\s+in\s+cloud',
            r'speciali[zs](?:ing|ation)?\s+in\s+devops',
            r'track[:\s]+cloud', r'concentration[:\s]+cloud\s+computing'
        ),
        "Software Engineering": (
            r'speciali[zs](?:ing|ation)?\s+in\s+software\s+engineering',
            r'speciali[zs](?:ing|ation)?\s+in\s+software\s+development',
            r'track[:\s]+software', r'concentration[:\s]+software'
        ),
        "Computer Networks & Systems": (
            r'speciali[zs](?:ing|ation)?\s+in\s+network',
            r'speciali[zs](?:ing|ation)?\s+in\s+systems',
            r'track[:\s]+network', r'concentration[:\s]+telecommunications'
        ),
        "Interactive Media & HCI": (
            r'speciali[zs](?:ing|ation)?\s+in\s+interactive\s+media',
            r'speciali[zs](?:ing|ation)?\s+in\s+ui\/ux',
            r'speciali[zs](?:ing|ation)?\s+in\s+human\s+computer\s+interaction'
        ),
        "Business Information Systems": (
            r'speciali[zs](?:ing|ation)?\s+in\s+business\s+information',
            r'speciali[zs](?:ing|ation)?\s+in\s+management\s+information',
            r'track[:\s]+information\s+systems'
        )
    }

    for spec_name, p_tuple in spec_patterns.items():
        if any(re.search(p, lowered) for p in p_tuple):
            specializations.append(spec_name)

    # Academic classification / Honors
    academic_honors = "Standard"
    if any(re.search(p, lowered) for p in [r'first\s+class', r'summa\s+cum\s+laude', r'distinction', r'gpa\s*[:=]?\s*(?:3\.[7-9]|4\.0)']):
        academic_honors = "First Class Honours / Distinction"
    elif any(re.search(p, lowered) for p in [r'second\s+upper', r'magna\s+cum\s+laude', r'merit', r'gpa\s*[:=]?\s*3\.[3-6]']):
        academic_honors = "Second Class Upper"
    elif any(re.search(p, lowered) for p in [r'second\s+lower', r'cum\s+laude', r'gpa\s*[:=]?\s*3\.[0-2]']):
        academic_honors = "Second Class Lower"

    for major_name, p_tuple in major_patterns.items():
        if any(re.search(p, lowered) for p in p_tuple):
            majors.append(major_name)

    if not majors:
        for non_it_name, p_tuple in non_it_major_patterns.items():
            if any(re.search(p, lowered) for p in p_tuple):
                majors.append(non_it_name)

    return {
        "level_score": level_score,
        "level_name": level_name,
        "majors": majors if majors else ["General / Unspecified"],
        "specializations": specializations,
        "academic_honors": academic_honors
    }


def extract_education_details(text: str) -> Dict[str, Any]:
    """Extract structured education details including institution, graduation year, degree, and recognized certifications."""
    edu_info = extract_education_level(text)
    sections = extract_sections(text)
    edu_text = sections.get("education", text)

    # Institution extraction heuristics
    inst_match = re.search(r'\b(?:at|from|university\s+of|institute\s+of)\s+([A-Za-z\s]+(?:University|Institute|College|Academy|SLIIT|IIT))\b', edu_text, re.I)
    institution = inst_match.group(0).strip() if inst_match else "Recognized Higher Education Institution"

    # Graduation year
    year_match = re.search(r'\b(20[0-2]\d|19[8-9]\d)\b', edu_text)
    grad_year = int(year_match.group(1)) if year_match else None

    # Verified Certifications vs Unverified Training
    skills_certs = extract_skills_and_certifications(text)
    verified_certs = []
    for cert in skills_certs.get("detected_certs", []):
        cert_l = cert.lower()
        if cert_l in CANONICAL_CERTIFICATIONS:
            meta = CANONICAL_CERTIFICATIONS[cert_l]
            verified_certs.append({
                "certification": cert,
                "issuing_body": meta["vendor"],
                "tier": meta["tier"],
                "is_verified_credential": True
            })
        else:
            verified_certs.append({
                "certification": cert,
                "issuing_body": "Industry Vendor",
                "tier": "Professional",
                "is_verified_credential": True
            })

    return {
        "degree_level": edu_info["level_name"],
        "level_score": edu_info["level_score"],
        "majors": edu_info["majors"],
        "institution": institution,
        "graduation_year": grad_year,
        "verified_certifications": verified_certs
    }


# ── Contextual Skills Extraction ───────────────────────────────────────────────

def extract_skills_and_certifications(text: str) -> Dict[str, Any]:
    """Extract detected skills, aliases, contextual evidence levels (HIGH, MEDIUM, LOW), and certifications."""
    if not text:
        return {
            "detected_skills": [],
            "detected_certs": [],
            "skill_evidence": {},
            "skill_category_counts": {}
        }

    lowered = text.lower()
    sections = extract_sections(text)
    exp_text = sections.get("experience", "").lower()
    proj_text = sections.get("projects", "").lower()
    edu_text = sections.get("education", "").lower()

    detected_skills: Set[str] = set()
    skill_evidence: Dict[str, Any] = {}
    category_counts: Dict[str, int] = {}

    sentences = [s.strip() for s in re.split(r'[\.\n;•·]+', text) if len(s.strip()) > 10]

    for category, skills in SKILL_LEXICON.items():
        count = 0
        for skill in skills:
            pattern = _SKILL_PATTERNS.get(skill)
            if pattern and pattern.search(lowered):
                normalized = SKILL_ALIASES.get(skill, skill)
                detected_skills.add(normalized)
                count += 1

                # Determine Context & Evidence Level
                in_exp = pattern.search(exp_text) is not None
                in_proj = pattern.search(proj_text) is not None
                in_edu = pattern.search(edu_text) is not None

                matching_snippets = [s for s in sentences if pattern.search(s.lower())][:2]

                has_action = any(any(v in snip.lower() for v in _ACTION_VERBS) for snip in matching_snippets)

                if (in_exp or in_proj) and has_action:
                    strength = "high"
                elif in_exp or in_proj or in_edu:
                    strength = "medium"
                else:
                    strength = "low"

                skill_evidence[normalized] = {
                    "skill": normalized,
                    "canonical_skill": normalized.title() if len(normalized) > 3 else normalized.upper(),
                    "evidence_strength": strength,
                    "evidence_level": strength.upper(),
                    "evidence": matching_snippets,
                    "evidence_snippets": matching_snippets
                }


        category_counts[category] = count

    detected_certs = []
    for cert, pattern in _CERT_PATTERNS:
        if pattern.search(lowered):
            detected_certs.append(cert.title())

    return {
        "detected_skills": sorted(list(detected_skills)),
        "detected_certs": sorted(list(set(detected_certs))),
        "skill_evidence": skill_evidence,
        "skill_category_counts": category_counts
    }


# ── Projects & Achievements Extraction ─────────────────────────────────────────

def extract_projects(text: str) -> List[Dict[str, Any]]:
    """Extract individual project entries and metrics-based achievements."""
    sections = extract_sections(text)
    proj_text = sections.get("projects", "")
    if not proj_text:
        return []

    lines = proj_text.splitlines()
    projects: List[Dict[str, Any]] = []
    curr_proj: Optional[Dict[str, Any]] = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if not stripped.startswith(('•', '-', '*', '—')) and len(stripped) < 80:
            if curr_proj:
                projects.append(curr_proj)
            curr_proj = {
                "project_title": stripped,
                "technologies": [],
                "highlights": []
            }
        elif curr_proj:
            curr_proj["highlights"].append(stripped)
            for cat_skills in SKILL_LEXICON.values():
                for s in cat_skills:
                    if s in stripped.lower() and s not in curr_proj["technologies"]:
                        curr_proj["technologies"].append(SKILL_ALIASES.get(s, s))

    if curr_proj:
        projects.append(curr_proj)

    return projects


def extract_deep_cv_profile(text: str, target_role: str = "Software Engineer") -> Dict[str, Any]:
    """Consolidated deep extraction returning the full candidate understanding profile."""
    cleaned = clean_text(text)
    skills_certs = extract_skills_and_certifications(text)
    exp_details = extract_experience_details(text, target_role)
    edu_details = extract_education_details(text)
    projects = extract_projects(text)

    return {
        "cleaned_text": cleaned,
        "skills": skills_certs["detected_skills"],
        "skill_evidence": skills_certs["skill_evidence"],
        "detected_certs": skills_certs["detected_certs"],
        "experience": exp_details,
        "education": edu_details,
        "projects": projects
    }
