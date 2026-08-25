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

_PHD_RE = re.compile(r'\b(ph\.?d|doctor of philosophy|doctorate)\b', re.I)
_MSC_RE = re.compile(r'\b(m\.?sc|master|postgraduate diploma|m\.?tech|mca)\b', re.I)
_BSC_RE = re.compile(r'\b(b\.?sc|bachelor|b\.?tech|b\.?e|bca|undergraduate)\b', re.I)
_DIP_RE = re.compile(r'\b(diploma|hnd|nvq|higher diploma|associate degree)\b', re.I)

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
    """Regex-based experience extraction from CV text with date range deduplication."""
    if not text:
        return 0.0

    lowered = text.lower()

    # Pattern 1: Explicit years of experience
    exp_patterns = [
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|work|industry|field|background)',
        r'(?:experience|worked|working)\s+(?:for\s+)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+in\b',
        r'over\s+(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
    ]

    found_years = []
    for pattern in exp_patterns:
        for m in re.findall(pattern, lowered):
            try:
                val = float(m)
                if 0.0 < val <= 40.0:
                    found_years.append(val)
            except ValueError:
                pass

    if found_years:
        return max(found_years)

    # Pattern 2: Year ranges
    month_regex = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)?'
    range_pattern = r'\b' + month_regex + r'\s*(20[0-2]\d|19[8-9]\d)\s*(?:-|–|to)\s*' + month_regex + r'\s*(present|current|20[0-2]\d|19[8-9]\d)\b'
    range_matches = re.findall(range_pattern, lowered)

    intervals = []
    current_year = 2026

    for start_str, end_str in range_matches:
        try:
            start_yr = int(start_str)
            end_yr = current_year if end_str in ('present', 'current') else int(end_str)
            if start_yr <= end_yr and (end_yr - start_yr) <= 35:
                intervals.append((start_yr, end_yr))
        except ValueError:
            pass

    if intervals:
        intervals.sort(key=lambda x: x[0])
        merged = []
        for start, end in intervals:
            if not merged:
                merged.append([start, end])
            else:
                prev = merged[-1]
                if start <= prev[1]:
                    prev[1] = max(prev[1], end)
                else:
                    merged.append([start, end])

        total_span = sum(end - start for start, end in merged)
        if total_span > 0:
            return float(min(total_span, 35.0))

    # Pattern 3: Simple standalone
    simple_matches = re.findall(r'\b(\d{1,2})\s*\+?\s*(?:years?|yrs?)\b', lowered)
    valid_simple = [float(m) for m in simple_matches if 0 < float(m) <= 40]
    if valid_simple:
        return max(valid_simple)

    return 0.0


def extract_education_level(text: str) -> Dict[str, Any]:
    """
    Extracts education degree level (PhD=4, MSc=3, BSc=2, Diploma=1, None=0)
    and degree field/major.
    """
    if not text:
        return {"level_score": 0.0, "level_name": "None", "major": "None", "majors": ["General IT"]}

    lowered = text.lower()

    level_score = 0.40
    level_name = "Diploma"

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

    # Majors
    majors = []
    major_patterns = {
        "Computer Science": (r'computer science', r'\bcs\b'),
        "Software Engineering": (r'software engineering', r'\bse\b'),
        "Information Technology": (r'information technology', r'\bit\b'),
        "Data Science": (r'data science', r'analytics'),
        "Cybersecurity": (r'cybersecurity', r'cyber security', r'information security'),
        "Networking": (r'network engineering', r'telecommunications'),
        "Engineering": (r'computer engineering', r'electrical engineering')
    }

    for major_name, p_tuple in major_patterns.items():
        if any(p in lowered for p in p_tuple):
            majors.append(major_name)

    return {
        "level_score": level_score,
        "level_name": level_name,
        "majors": majors if majors else ["General IT"]
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
