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
from typing import Any, Dict, List, Optional, Set, Tuple
from ml.lexicon import ALL_TECHNICAL_SKILLS, CERTIFICATIONS_LIST, SKILL_LEXICON

# Canonical skill normalization & alias mapping
SKILL_ALIASES: Dict[str, str] = {
    "react.js": "react",
    "reactjs": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "expressjs": "express.js",
    "express": "express.js",
    "vuejs": "vue.js",
    "nextjs": "next.js",
    "next.js": "next.js",
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
    "fastapi": "fastapi",
    "fast api": "fastapi",
    "restful api": "rest apis",
    "rest api": "rest apis",
    "restful apis": "rest apis",
    "rest apis": "rest apis",
    "rest": "rest apis",
    "ci / cd": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    "tailwind": "tailwind css",
    "tailwindcss": "tailwind css",
    "tailwind css": "tailwind css",
    "ms sql": "sql server",
    "mssql": "sql server",
    "sql server": "sql server",
    "pytorch": "pytorch",
    "torch": "pytorch",
}

# Pre-compile regexes for ultra-fast matching
_EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
_PHONE_RE = re.compile(r'\+?\d[\d\s\-\(\)]{8,}\d')
_URL_RE = re.compile(r'https?://\S+|www\.\S+')
_ZIP_RE = re.compile(r'\b\d{5}(?:[-\s]\d{4})?\b')
_SPACE_RE = re.compile(r'[ \t]+')

_PHD_RE = re.compile(r'\b(ph\.?d|doctor of philosophy|doctorate|doctoral)\b', re.I)
_MSC_RE = re.compile(r'\b(m\.?sc|master of (?:science|technology|engineering|business|information)|masters?|postgraduate|m\.?tech|mca|mba)\b', re.I)
_BSC_RE = re.compile(r'\b(b\.?sc|bachelor|b\.?tech|b\.?e\b|b\.?eng|b\.?i\.?t|bca|bcomp|undergraduate|b\.?a\b)\b', re.I)
_DIP_RE = re.compile(r'\b(diploma|hnd|nvq|higher diploma|associate degree|foundation|advanced certificate)\b', re.I)

_MONTH_MAP = {
    'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
    'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6,
    'jul': 7, 'july': 7, 'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
    'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
}


def _parse_date_float(s: str) -> Optional[float]:
    s = s.strip().lower()
    if s in ('present', 'current', 'now', 'ongoing'):
        from datetime import datetime
        now = datetime.now()
        return now.year + (now.month - 1) / 12.0
    m = re.search(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,\'/-]+(\d{2,4})', s)
    if m:
        mon = _MONTH_MAP.get(m.group(1), 1)
        yr_str = m.group(2)
        yr = int(yr_str) if len(yr_str) == 4 else (2000 + int(yr_str))
        return yr + (mon - 1) / 12.0
    m2 = re.search(r'(\d{1,2})[/-](\d{4})', s)
    if m2:
        mon = max(1, min(12, int(m2.group(1))))
        yr = int(m2.group(2))
        return yr + (mon - 1) / 12.0
    m3 = re.search(r'\b(20[0-2]\d|19[8-9]\d)\b', s)
    if m3:
        return float(m3.group(1))
    return None

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
    """Regex-based experience extraction from CV text with section awareness and date range deduplication."""
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

    explicit_years = []
    for pattern in exp_patterns:
        for m in re.findall(pattern, lowered):
            try:
                val = float(m)
                if 0.5 <= val <= 40.0:
                    explicit_years.append(val)
            except ValueError:
                pass

    # Pattern 2: Extract date ranges from non-education lines
    date_range_re = re.compile(
        r'((?:jan[a-z]*|feb[a-z]*|mar[a-z]*|apr[a-z]*|may|jun[a-z]*|jul[a-z]*|aug[a-z]*|sep[a-z]*|oct[a-z]*|nov[a-z]*|dec[a-z]*|\d{1,2}[/-]\d{4}|\b20[0-2]\d|\b19[8-9]\d)[^–—\-\nto]*?)\s*(?:-|–|—|to)\s*'
        r'((?:jan[a-z]*|feb[a-z]*|mar[a-z]*|apr[a-z]*|may|jun[a-z]*|jul[a-z]*|aug[a-z]*|sep[a-z]*|oct[a-z]*|nov[a-z]*|dec[a-z]*|\d{1,2}[/-]\d{4}|\b20[0-2]\d|\b19[8-9]\d|present|current|now)\b[^–—\-\n]*)',
        re.I
    )

    lines = text.splitlines()
    intervals = []
    in_edu = False

    for line in lines:
        line_clean = line.strip().lower()
        if not line_clean:
            continue
        if re.match(r'^education|academic\s+background|qualifications?', line_clean):
            in_edu = True
            continue
        if re.match(r'^(?:work\s+|professional\s+|job\s+)?experience|employment|work\s+history|projects?|skills?', line_clean):
            in_edu = False
            continue

        # Skip lines clearly belonging to academic degree descriptions
        if in_edu or any(k in line_clean for k in ('university', 'college', 'bachelor', 'degree', 'passed finalist', 'gce', 'advance level', 'ordinary level', 'b.sc', 'm.sc', 'diploma')):
            continue

        for m in date_range_re.finditer(line):
            st = _parse_date_float(m.group(1))
            en = _parse_date_float(m.group(2))
            if st and en and 1980 <= st <= 2030 and st <= en and (en - st) <= 35:
                intervals.append((st, en))

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
            calc_val = round(total_span, 1)
            if explicit_years:
                return float(min(max(max(explicit_years), calc_val), 40.0))
            return float(min(calc_val, 40.0))

    if explicit_years:
        return float(min(max(explicit_years), 40.0))

    # Pattern 3: Simple standalone (e.g., "5 yrs in IT")
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
