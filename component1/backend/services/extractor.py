"""Entity extractor — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Extracts structured fields from raw resume text using regex + keyword matching.
These extracted values feed the scorer and can assist (not replace) the ML classifier.

Fields extracted:
    edu_level    : int       — 1=Diploma, 2=BSc, 3=MSc, 4=PhD
    edu_relevance: float     — 0–1 (how relevant the degree is to CS/IT/Engineering)
    experience_years: float  — years of work experience
    skills       : List[str] — matched skill keywords
    education    : str       — longest education sentence found (human-readable)
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import List

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data.role_requirements import REQUIRED_SKILLS

logger = logging.getLogger("component1.extractor")

# ── Education patterns ─────────────────────────────────────────────────────────

_PHD_RE    = re.compile(r'\b(ph\.?d\.?|doctor of philosophy|doctorate)\b', re.I)
_MSC_RE    = re.compile(
    r'\b(m\.?sc\.?|m\.?s\.?|master of science|master of (engineering|business|arts|technology)|m\.?(eng|tech|ba|mba|comp)\.?)\b',
    re.I,
)
_BSC_RE    = re.compile(
    r'\b(b\.?sc\.?|b\.?s\.?|b\.?eng\.?|b\.?tech\.?|bachelor of (science|engineering|technology|computer)|b\.?comp\.?|b\.?it\.?|hnd)\b',
    re.I,
)
_DIPLOMA_RE = re.compile(r'\b(diploma|certificate|higher national certificate|hnc)\b', re.I)

# Degree subjects relevant to CS/IT/Engineering (for edu_relevance)
_RELEVANT_SUBJECTS = {
    "computer science", "software engineering", "information technology",
    "information systems", "computer engineering", "electrical engineering",
    "electronics engineering", "data science", "artificial intelligence",
    "machine learning", "cybersecurity", "network engineering",
    "telecommunications", "mathematics", "statistics",
    "computing", "it", "cs", "software development",
}

# ── Experience patterns ────────────────────────────────────────────────────────

_YEAR_RANGE_RE  = re.compile(
    r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}\s*[-–—to]+\s*'
    r'(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}|present|current|now)',
    re.I,
)
_YEAR_ONLY_RE   = re.compile(r'\b(\d{4})\s*[-–—to]+\s*(\d{4}|present|current|now)\b', re.I)
_EXPLICIT_EXP_RE = re.compile(
    r'(\d+\.?\d*)\s*\+?\s*(?:year|yr)s?\s+(?:of\s+)?(?:experience|exp|work(?:ing)?)',
    re.I,
)

# ── Skill keyword bank ─────────────────────────────────────────────────────────
# Flat union of all role skill lists, plus extra common synonyms.

_EXTRA_SKILLS = [
    "python", "java", "c", "c++", "c#", "go", "golang", "rust", "scala",
    "javascript", "typescript", "html", "css", "sql", "nosql",
    "react", "react.js", "vue", "vue.js", "angular", "next.js", "nuxt.js",
    "django", "flask", "fastapi", "spring", "spring boot", "express", "express.js",
    "node.js", "graphql", "rest", "rest apis", "rest api", "grpc",
    "docker", "kubernetes", "helm", "terraform", "ansible", "puppet", "chef",
    "aws", "azure", "gcp", "cloud", "serverless", "lambda",
    "git", "github", "gitlab", "ci/cd", "jenkins", "github actions",
    "mongodb", "postgresql", "mysql", "redis", "elasticsearch", "cassandra", "firebase", "sqlite",
    "kafka", "rabbitmq", "celery",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "scikit-learn", "tensorflow", "pytorch", "keras", "hugging face",
    "nlp", "cv", "computer vision", "llm", "gpt", "bert", "sbert",
    "linux", "bash", "shell scripting", "powershell",
    "flutter", "dart", "swift", "kotlin", "react native", "android", "ios",
    "figma", "sketch", "adobe xd", "invision",
    "solidity", "web3", "blockchain",
    "siem", "penetration testing", "firewalls", "vulnerability assessment",
    "machine learning", "deep learning", "data science",
    "etl", "spark", "airflow", "dbt", "hadoop",
    "prometheus", "grafana", "elk", "datadog",
    "agile", "scrum", "kanban", "jira", "confluence",
    "mvc", "mvvm", "rest api design", "api integration", "microservices", "microservices architecture",
    "lightgbm", "xgboost", "svm", "logistic regression", "cosine similarity",
    "postman", "cloudinary", "android studio", "vs code",
]

_ALL_SKILLS_LOWER: set = set()
for _role, _skills in REQUIRED_SKILLS.items():
    for _s in _skills:
        _ALL_SKILLS_LOWER.add(_s.lower())
for _s in _EXTRA_SKILLS:
    _ALL_SKILLS_LOWER.add(_s.lower())


@dataclass
class ExtractedFeatures:
    edu_level:        int   = 2         # default BSc
    edu_relevance:    float = 0.5
    education:        str   = ""
    experience_years: float = 0.0
    skills:           List[str] = field(default_factory=list)


def extract(text: str) -> ExtractedFeatures:
    """Extract structured features from raw resume text."""
    result = ExtractedFeatures()
    result.edu_level, result.edu_relevance, result.education = _extract_education(text)
    result.experience_years = _extract_experience_years(text)
    result.skills = _extract_skills(text)
    return result


# ── Private helpers ────────────────────────────────────────────────────────────

def _extract_education(text: str):
    """Return (edu_level: int, edu_relevance: float, education_str: str)."""
    level = 1  # start at Diploma; if no degree keyword found at all, keep Diploma

    if _PHD_RE.search(text):
        level = 4
    elif _MSC_RE.search(text):
        level = 3
    elif _BSC_RE.search(text):
        level = 2
    elif _DIPLOMA_RE.search(text):
        level = 1

    # Find the most informative education line/sentence for the human-readable field
    edu_sentence = ""
    for line in text.splitlines():
        if any(kw in line.lower() for kw in (
            "bachelor", "master", "phd", "ph.d", "msc", "bsc", "b.sc", "m.sc",
            "diploma", "degree", "university", "college", "engineer",
        )):
            stripped = line.strip()
            if len(stripped) > len(edu_sentence):
                edu_sentence = stripped

    # edu_relevance: check for relevant subjects in full text
    text_lower = text.lower()
    if any(subj in text_lower for subj in _RELEVANT_SUBJECTS):
        relevance = 0.9
    else:
        relevance = 0.4

    return level, relevance, edu_sentence[:200] if edu_sentence else "Unknown"


def _extract_experience_years(text: str) -> float:
    """Infer total years of experience from the resume text."""
    # 1. Explicit statement: "5+ years of experience"
    explicit = _EXPLICIT_EXP_RE.search(text)
    if explicit:
        try:
            return min(float(explicit.group(1)), 50.0)
        except ValueError:
            pass

    # 2. Sum up year ranges (e.g. "Jan 2019 – Mar 2022")
    total_months = 0
    seen_ranges = set()

    # First try month-year ranges
    for m in _YEAR_RANGE_RE.finditer(text):
        start_yr = int(m.group(0)[-4:])  # last 4 digits are start year
        end_str = m.group(0).lower()
        if 'present' in end_str or 'current' in end_str or 'now' in end_str:
            import datetime
            end_yr = datetime.date.today().year
        else:
            # Extract end year (last 4-digit number)
            nums = re.findall(r'\d{4}', m.group(0))
            end_yr = int(nums[-1]) if nums else 0
        range_key = (start_yr, end_yr)
        if range_key not in seen_ranges and 1970 <= start_yr <= end_yr <= 2035:
            seen_ranges.add(range_key)
            total_months += (end_yr - start_yr) * 12

    # Then try plain year ranges
    for m in _YEAR_ONLY_RE.finditer(text):
        start_yr = int(m.group(1))
        end_str = m.group(2).lower()
        if end_str in ("present", "current", "now"):
            import datetime
            end_yr = datetime.date.today().year
        else:
            try:
                end_yr = int(end_str)
            except ValueError:
                continue
        range_key = (start_yr, end_yr)
        if range_key not in seen_ranges and 1970 <= start_yr <= end_yr <= 2035:
            seen_ranges.add(range_key)
            total_months += (end_yr - start_yr) * 12

    if total_months > 0:
        # Deduplicate by keeping at most 40 years and rounding to 0.5
        years = min(round(total_months / 12 * 2) / 2, 40.0)
        return years

    return 0.0


def _extract_skills(text: str) -> List[str]:
    """Return deduplicated list of matched skill keywords from the resume text."""
    text_lower = text.lower()
    # Also normalize common separators (bullets, pipes, semicolons) to spaces
    # so multi-word skills like "React Native" match even if PDF inserts chars
    text_normalized = re.sub(r'[·•|;/]', ' ', text_lower)
    text_normalized = re.sub(r'\s+', ' ', text_normalized)

    matched = []
    # Sort by length descending so longer skills match first (e.g. "react native" before "react")
    for skill in sorted(_ALL_SKILLS_LOWER, key=len, reverse=True):
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_normalized) or re.search(pattern, text_lower):
            # Deduplicate: don't add "react" if "react native" already matched
            skill_parts = skill.split()
            if len(skill_parts) > 1:
                # Multi-word skill: check it's not already covered
                if not any(skill_parts[0] in m for m in matched):
                    matched.append(skill)
            else:
                # Single-word skill: check it's not a substring of an already-matched multi-word skill
                if not any(skill in m.split() and len(m.split()) > 1 for m in matched):
                    matched.append(skill)
    return matched
