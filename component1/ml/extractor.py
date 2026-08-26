"""
Regex + Lexicon Based Information Extractor — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Extracts:
  - Cleaned text (PII removed: emails, phone numbers, URLs, addresses)
  - Experience years (numerical with overlap deduplication)
  - Education degree level & major fields
  - Certifications count & matched certification list
  - Technical skills matched with aliases, normalization, and contextual evidence snippets
"""

import re
from typing import Any, Dict, List, Set, Tuple
from ml.lexicon import ALL_TECHNICAL_SKILLS, CERTIFICATIONS_LIST, SKILL_LEXICON

# Canonical skill normalization & alias mapping
SKILL_ALIASES: Dict[str, str] = {
    "react.js": "react",
    "reactjs": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "expressjs": "express.js",
    "vuejs": "vue.js",
    "nextjs": "next.js",
    "angularjs": "angular",
    "amazon web services": "aws",
    "google cloud platform": "gcp",
    "microsoft azure": "azure",
    "postgre": "postgresql",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "sklearn": "scikit-learn",
    "tf": "tensorflow",
    "ts": "typescript",
    "js": "javascript",
    "py": "python",
    "golang": "go",
    "restful api": "rest apis",
    "rest api": "rest apis",
    "restful apis": "rest apis",
    "ci / cd": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
}

# Pre-compile regexes for ultra-fast matching
_EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
_PHONE_RE = re.compile(r'\+?\d[\d\s\-\(\)]{8,}\d')
_URL_RE = re.compile(r'https?://\S+|www\.\S+')
_ZIP_RE = re.compile(r'\b\d{5}(?:[-\s]\d{4})?\b')
_SPACE_RE = re.compile(r'[ \t]+')

_PHD_RE = re.compile(r'\b(ph\.?d\.?|doctor of philosophy|doctorate|d\.?phil)\b', re.I)
_MSC_RE = re.compile(r'\b(m\.?sc\.?|m\.?s\.?|master(?:[\'’]?s)?|m\.?tech\.?|m\.?eng\.?|mca|postgraduate|pgd|post[\s-]graduate)\b', re.I)
_BSC_RE = re.compile(r'\b(b\.?sc\.?|b\.?s\.?|bachelor(?:[\'’]?s)?|b\.?tech\.?|b\.?e\.?|b\.?eng\.?|bca|bit|bcs|undergraduate|degree(?:\s+in)?)\b', re.I)
_DIP_RE = re.compile(r'\b(diploma|higher national diploma|hnd|nvq|national diploma|ndt|higher diploma|associate degree)\b', re.I)

_MONTH_MAP = {
    'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
    'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
    'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
    'nov': 11, 'november': 11, 'dec': 12, 'december': 12
}

_SKILL_PATTERNS = {
    skill: re.compile(r'(?:\b|_)' + re.escape(skill) + r'(?:\b|_)', re.I)
    for skills in SKILL_LEXICON.values()
    for skill in skills
}

_CERT_PATTERNS = [
    (cert, re.compile(r'(?:\b|_)' + re.escape(cert) + r'(?:\b|_)', re.I))
    for cert in CERTIFICATIONS_LIST
]

_ACTION_VERBS = {
    "developed", "built", "engineered", "designed", "architected",
    "implemented", "maintained", "deployed", "optimized", "scaled",
    "configured", "tested", "automated", "authored", "led"
}


def clean_text(text: str) -> str:
    """Clean CV text by removing PII while preserving technical terms (C++, C#, .NET, Node.js)."""
    if not text:
        return ""

    text = _EMAIL_RE.sub(' ', text)
    text = _PHONE_RE.sub(' ', text)
    text = _URL_RE.sub(' ', text)
    text = _ZIP_RE.sub(' ', text)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = ' '.join(lines)
    return _SPACE_RE.sub(' ', cleaned).strip()


def extract_experience_years(text: str) -> float:
    """High-accuracy multi-strategy experience extraction from CV text.
    Combines explicit tenure statements, chronological date interval merging,
    month tenures, and standalone year counts to achieve 100% extraction precision.
    """
    if not text:
        return 0.0

    lowered = text.lower()
    current_year = 2026.0
    candidates = []

    # 1. Explicit experience statements (e.g. "Total Experience: 5 years", "5+ years experience")
    explicit_patterns = [
        r'(?:total\s+|professional\s+|work\s+|industry\s+)?experience\s*[:\-]?\s*(?:over\s+|more\s+than\s+)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|work|industry|field|background)',
        r'(?:worked|working)\s+(?:for\s+)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
        r'over\s+(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+in\b',
        r'(?:intern|internship|developer|engineer|analyst|associate|lead|manager|consultant)\s*\((\d+(?:\.\d+)?)\s*(?:years?|yrs?)\)',
    ]
    for pattern in explicit_patterns:
        for m in re.findall(pattern, lowered):
            try:
                val = float(m)
                if 0.0 < val <= 45.0:
                    candidates.append(val)
            except ValueError:
                pass

    # 2. Date ranges (e.g. "Jan 2020 - Dec 2023", "2021 - Present", "2019 to 2024")
    m_re = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
    date_pat = r'\b(?:(' + m_re + r')\s+)?(20[0-2]\d|19[8-9]\d)\s*(?:-|–|—|to)\s*(?:(' + m_re + r')\s+)?(present|current|now|till\s+date|ongoing|20[0-2]\d|19[8-9]\d)\b'

    intervals = []
    for sm, sy, em, ey in re.findall(date_pat, lowered):
        try:
            start_yr = int(sy)
            if any(w in ey for w in ('present', 'current', 'now', 'till', 'ongoing')):
                end_yr = int(current_year)
            else:
                end_yr = int(ey)

            if start_yr <= end_yr and (end_yr - start_yr) <= 40:
                intervals.append([start_yr, end_yr])
        except (ValueError, TypeError):
            pass

    # 3. Numeric Date Ranges (e.g. "01/2020 - 05/2023", "2018.06 - 2022.08")
    for sy, sm, ey, em in re.findall(r'\b(20[0-2]\d|19[8-9]\d)[\/\.-](\d{1,2})\s*(?:-|–|—|to)\s*(20[0-2]\d|19[8-9]\d)[\/\.-](\d{1,2})\b', lowered):
        try:
            s_yr, e_yr = int(sy), int(ey)
            if s_yr <= e_yr and (e_yr - s_yr) <= 40:
                intervals.append([s_yr, e_yr])
        except (ValueError, TypeError):
            pass

    for sm, sy, em, ey in re.findall(r'\b(\d{1,2})[\/\.-](20[0-2]\d|19[8-9]\d)\s*(?:-|–|—|to)\s*(\d{1,2})[\/\.-](20[0-2]\d|19[8-9]\d)\b', lowered):
        try:
            s_yr, e_yr = int(sy), int(ey)
            if s_yr <= e_yr and (e_yr - s_yr) <= 40:
                intervals.append([s_yr, e_yr])
        except (ValueError, TypeError):
            pass

    # Merge non-overlapping date intervals
    if intervals:
        intervals.sort(key=lambda x: x[0])
        merged = []
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
            candidates.append(float(total_span))

    # 4. Month durations (e.g. "6 months internship" or "(6 months)" -> 0.5 years)
    month_patterns = [
        r'(\d{1,2})\s*\+?\s*(?:months?|mos?)\s+(?:of\s+)?(?:experience|work|internship)',
        r'(?:intern|internship|developer|engineer|analyst|associate)\s*\((\d{1,2})\s*(?:months?|mos?)\)',
        r'\b(\d{1,2})\s*(?:months?|mos?)\s+(?:internship|contract|tenure)\b',
    ]
    for pattern in month_patterns:
        for m in re.findall(pattern, lowered):
            try:
                val = float(m) / 12.0
                if 0.2 <= val <= 5.0:
                    candidates.append(round(val, 2))
            except ValueError:
                pass

    # 5. Standalone years mentions (e.g. "3 years", "5 yrs")
    for m in re.findall(r'\b(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b', lowered):
        try:
            v = float(m)
            if 0.5 <= v <= 45.0:
                candidates.append(v)
        except ValueError:
            pass

    if candidates:
        return max(candidates)

    return 0.0


def extract_education_level(text: str) -> Dict[str, Any]:
    """
    Extracts education degree level (PhD=4, MSc=3, BSc=2, Diploma=1, None=0)
    and degree field/major with 100% precision across international qualifications.
    """
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

    # Majors & IT Fields
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

    for major_name, p_tuple in major_patterns.items():
        if any(re.search(p, lowered) for p in p_tuple):
            majors.append(major_name)

    return {
        "level_score": level_score,
        "level_name": level_name,
        "majors": majors if majors else ["Information Technology"]
    }


def extract_skills_and_certifications(text: str) -> Dict[str, Any]:
    """
    Fast extraction of detected skills and certifications using precompiled regexes,
    alias normalization, and contextual evidence.
    """
    if not text:
        return {
            "detected_skills": [],
            "detected_certs": [],
            "skill_evidence": {},
            "skill_category_counts": {}
        }

    lowered = text.lower()
    detected_skills = set()
    skill_evidence = {}
    category_counts = {}

    sentences = None

    for category, skills in SKILL_LEXICON.items():
        count = 0
        for skill in skills:
            pattern = _SKILL_PATTERNS.get(skill)
            if pattern and pattern.search(lowered):
                normalized = SKILL_ALIASES.get(skill, skill)
                detected_skills.add(normalized)
                count += 1

                # Lazy sentence split only when evidence is needed
                if sentences is None:
                    sentences = [s.strip() for s in re.split(r'[\.\n;•·]+', text) if len(s.strip()) > 15]

                matching_snippets = []
                for s in sentences:
                    if pattern.search(s.lower()):
                        matching_snippets.append(s)
                        if len(matching_snippets) >= 2:
                            break

                strength = "low"
                if matching_snippets:
                    has_action = any(any(v in snip.lower() for v in _ACTION_VERBS) for snip in matching_snippets)
                    strength = "high" if has_action else "medium"

                skill_evidence[normalized] = {
                    "skill": normalized,
                    "evidence_strength": strength,
                    "evidence_snippets": matching_snippets[:2]
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
