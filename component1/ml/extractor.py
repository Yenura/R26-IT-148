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

_PHD_RE = re.compile(r'\b(ph\.?d\.?|doctor\s+of\s+philosophy|doctorate|d\.?phil|d\.?sc\.?|doctor\s+of\s+science|eng\.?d\.?|doctor\s+of\s+engineering|dr\.-ing\.?|dr\.?\s*rer\.?\s*nat\.?|dr\.?\s*techn\.?|docteur|doctorado|doktor|d\.?b\.?a\.?)\b', re.I)
_MSC_RE = re.compile(r'\b(m\.?sc\.?|m\.?s\.?|master(?:[\'’]?s)?|master\s+of\s+[a-z\s]+|m\.?tech\.?|m\.?eng\.?|m\.?phil\.?|mres|mca|msit|mit|m\.?ba\b|pgd|post[\s-]graduate|postgraduate\s+diploma|pgdip|pgcert|diplom-informatiker|diplom-ingenieur(?!\s*\(fh\))|dipl\.-inf\.?|dipl\.-ing\.?(?!\s*\(fh\))|magister|ma[iî]trise|laurea\s+magistrale|master\s+europ[eé]en|titulado\s+superior|dipl[oô]me\s+d[\'\s]*ing[eé]nieur)\b', re.I)
_BSC_RE = re.compile(r'\b(b\.?sc\.?|b\.?s\.?|bachelor(?:[\'’]?s)?|bachelor\s+of\s+[a-z\s]+|b\.?tech\.?|b\.?e\.?|b\.?eng\.?|bca|bit|bcs|b\.?app\.?sc\.?|bappsc|b\.?comp\.?|bcomp|b\.?math|laurea\s+triennale|grado\s+en|licenciatura|licentiate|dipl\.-ing\.?\s*\(fh\)|diplom-ingenieur\s*\(fh\)|ing[eé]nieur|baccalaureate|undergraduate|(?<!foundation\s)(?<!associate\s)degree(?:\s+in)?)\b', re.I)
_DIP_RE = re.compile(r'\b(diploma(?!\s*d[\'\s]*ing)|higher\s+national\s+diploma|hnd|hnc|nvq(?:\s*level\s*\d)?|national\s+diploma|ndt|higher\s+diploma|associate\s+degree|associate\s+of\s+(?:science|arts|applied\s+science)|a\.?a\.?s?|foundation\s+degree|fdsc|fda|bts|dut|brevet\s+de\s+technicien\s+sup[eé]rieur|dipl[oô]me\s+universitaire\s+de\s+technologie|certhe|diphe|technical\s+certificate)\b', re.I)

def _build_skill_pattern(skill: str) -> re.Pattern:
    """Compile high-accuracy regex with strict word and punctuation boundaries for special symbols."""
    s_low = skill.lower()
    if s_low in ["c++", "cpp", "cplusplus"]:
        return re.compile(r'(?<![a-zA-Z0-9+])c\+\+(?![a-zA-Z0-9+])|\bcplusplus\b|\bcpp\b', re.I)
    elif s_low in ["c#", "csharp", "c sharp"]:
        return re.compile(r'(?<![a-zA-Z0-9#])c\#(?![a-zA-Z0-9#])|\bcsharp\b|\bc\s*sharp\b', re.I)
    elif s_low in [".net", ".net core", "dotnet"]:
        return re.compile(r'(?<![a-zA-Z0-9])\.net(?:\s+core)?(?![a-zA-Z0-9])|\bdotnet\b|\bnet\s+core\b|\basp\.net\b', re.I)
    elif s_low == "c":
        # Guard against single letter 'c': require programming/language context or C/C++ pair or skills list boundary
        return re.compile(
            r'\b(?:c\s*[\/,]\s*c\+\+|c\+\+\s*[\/,]\s*c|c\s+(?:programming|language)|(?:programming|language)\s+in\s+c|embedded\s+c)\b|'
            r'(?:^|[,\n•|;:\(\[])\s*c\s*(?=[,\n•|;\)\]]|$)',
            re.I
        )
    elif s_low == "r":
        # Guard against single letter 'r': require programming/language context or data science pair
        return re.compile(
            r'\b(?:r\s+(?:programming|language|studio|package|scripting)|(?:programming|language)\s+in\s+r)\b|'
            r'(?:^|[,\n•|;:\(\[])\s*r\s*(?=[,\n•|;\)\]]|$)',
            re.I
        )
    elif s_low in ["go", "golang"]:
        # Guard against English verb 'go': require golang or programming context or tech list pair
        return re.compile(
            r'\b(?:golang|go\s+(?:programming|language|lang)|(?:programming|language)\s+in\s+go)\b|'
            r'(?:^|[,\n•|;:\(\[])\s*go\s*(?=[,\n•|;\)\]]|$)',
            re.I
        )
    elif s_low in ["rest", "rest api", "rest apis", "restful api", "restful apis"]:
        return re.compile(
            r'\brest(?:\s*apis?|\s*ful\s*apis?|\s*ful\s*web\s*services?|\s*ful)\b|\brest\/graphql\b|'
            r'(?:^|[,\n•|;:\(\[])\s*rest\s*(?=[,\n•|;\)\]]|$)',
            re.I
        )
    elif s_low == "less":
        return re.compile(
            r'\bless(?:\s+css|\s+preprocessor|\s*\/\s*sass|\s+stylesheet)\b|'
            r'(?:^|[,\n•|;:\(\[])\s*less\s*(?=[,\n•|;\)\]]|$)',
            re.I
        )
    elif s_low in ["spring", "spring boot", "spring framework"]:
        return re.compile(
            r'\bspring\s+(?:boot|framework|mvc|cloud|data|security|batch|web)\b|'
            r'(?:^|[,\n•|;:\(\[])\s*spring\s*(?=[,\n•|;\)\]]|$)',
            re.I
        )
    elif s_low == "dart":
        return re.compile(
            r'\bdart(?:\s+programming|\s+language|\s*\/\s*flutter)?\b|'
            r'(?:^|[,\n•|;:\(\[])\s*dart\s*(?=[,\n•|;\)\]]|$)',
            re.I
        )
    elif s_low in ["solid", "solid principles"]:
        return re.compile(r'\bsolid\s+(?:principles?|design)\b', re.I)
    elif s_low in ["ci/cd", "ci-cd", "ci / cd"]:
        return re.compile(r'\bci\/cd\b|\bci-cd\b|\bcontinuous\s+integration\b', re.I)
    elif s_low in ["node.js", "nodejs", "node js"]:
        return re.compile(r'\bnode\.js\b|\bnodejs\b|\bnode\s+js\b', re.I)
    elif s_low in ["react.js", "reactjs", "react js"]:
        return re.compile(r'\breact\.js\b|\breactjs\b|\breact\s+js\b|\breact\b', re.I)
    elif s_low in ["vue.js", "vuejs", "vue js"]:
        return re.compile(r'\bvue\.js\b|\bvuejs\b|\bvue\s+js\b|\bvue\b', re.I)
    elif s_low in ["next.js", "nextjs", "next js"]:
        return re.compile(r'\bnext\.js\b|\bnextjs\b|\bnext\s+js\b', re.I)
    elif s_low in ["express.js", "expressjs", "express js"]:
        return re.compile(r'\bexpress\.js\b|\bexpressjs\b|\bexpress\s+js\b', re.I)
    elif s_low in ["machine learning", "ml"]:
        return re.compile(r'\bmachine\s+learning\b|(?<![a-zA-Z0-9_])ml(?![a-zA-Z0-9_])', re.I)
    elif s_low in ["natural language processing", "nlp"]:
        return re.compile(r'\bnatural\s+language\s+processing\b|(?<![a-zA-Z0-9_])nlp(?![a-zA-Z0-9_])', re.I)
    else:
        return re.compile(r'(?:\b|_)' + re.escape(skill) + r'(?:\b|_)', re.I)


# Skill matching patterns (escaped with boundary protection)
_SKILL_PATTERNS = {
    skill: _build_skill_pattern(skill)
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
        r'work\s+history|professional\s+background|relevant\s+experience|practical\s+experience|'
        r'industry\s+experience|experience|employment)\b',
        re.I
    ),
    "education": re.compile(
        r'^(?:educational\s+background|academic\s+background|educational\s+qualifications?|'
        r'academic\s+qualifications?|education|academics?|schooling|degrees?|qualifications?)\b',
        re.I
    ),
    "skills": re.compile(
        r'^(?:technical\s+skills?|core\s+competencies|technolog(?:y|ies)(?:\s+and\s+frameworks?)?|'
        r'frameworks?|tech\s+stack|programming\s+languages?|key\s+skills?|skills\s+and\s+abilities|'
        r'areas\s+of\s+expertise|software\s+skills?|skills?|tools?\s+and\s+technologies|'
        r'soft\s+skills?|technical\s+proficiencies?)\b',
        re.I
    ),
    "projects": re.compile(
        r'^(?:key\s+projects?|academic\s+projects?|personal\s+projects?|technical\s+projects?|'
        r'portfolio|projects?|notable\s+projects?)\b',
        re.I
    ),
    "certifications": re.compile(
        r'^(?:licenses\s+and\s+certifications|professional\s+certifications?|credentials?|'
        r'certifications?|accreditations?|courses?\s+and\s+certifications?|online\s+courses?)\b',
        re.I
    ),
    "summary": re.compile(
        r'^(?:executive\s+summary|professional\s+summary|career\s+objective|profile|summary|'
        r'about\s+me|overview)\b',
        re.I
    ),
    "references": re.compile(
        r'^(?:references?|referees?|non-related\s+references?|recommendations?)\b',
        re.I
    ),
    "activities": re.compile(
        r'^(?:clubs?\s+(?:&|and)\s+leadership(?:\s+skills?)?|extra[-\s]curricular(?:\s+activities)?|'
        r'co[-\s]curricular(?:\s+activities)?|volunteer\s+experience|volunteering|'
        r'memberships?|activities|leadership(?:\s+experience)?|community\s+involvement)\b',
        re.I
    ),
    "awards": re.compile(
        r'^(?:honors?\s+(?:&|and)\s+awards?|awards?\s+(?:&|and)\s+honors?|achievements?|'
        r'accomplishments?|competitions?|awards?|honors?)\b',
        re.I
    ),
    "publications": re.compile(
        r'^(?:publications?|research(?:\s+papers?)?|patents?|papers?)\b',
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
        "skills": [], "projects": [], "certifications": [], "activities": [],
        "references": [], "awards": [], "publications": [], "other": []
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
            end_val = end_yr + end_month / 12.0

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
            end_val = int(ey) + int(em) / 12.0
            if end_val >= start_val and (end_val - start_val) <= 40.0:
                return start_val, end_val, False

    return None


# ── Non-IT and IT Role Identification Lexicons ────────────────────────────────
NON_IT_KEYWORDS = {
    "accountant", "accounting", "auditor", "bookkeeper", "cashier", "financial analyst",
    "finance", "banker", "teller", "tax consultant", "investment analyst", "payroll",
    "chef", "cook", "baker", "waiter", "waitress", "bartender", "culinary", "hospitality", "hotel manager",
    "nurse", "doctor", "physician", "pharmacist", "therapist", "medical", "dentist", "surgeon",
    "driver", "chauffeur", "delivery", "warehouse", "logistics coordinator", "supply chain specialist",
    "sales representative", "sales executive", "retail associate", "store manager", "customer service",
    "receptionist", "office assistant", "administrative assistant", "secretary", "clerk",
    "teacher", "history teacher", "english literature", "tutor", "counselor", "professor", "lecturer",
    "lawyer", "attorney", "paralegal", "legal assistant",
    "construction", "electrician", "plumber", "carpenter", "painter", "mechanic",
    "civil engineer", "mechanical engineer", "chemical engineer", "production manager",
    "hr manager", "human resources", "recruiter", "talent acquisition", "security guard", "cleaner"
}

IT_TITLE_KEYWORDS = {
    "software", "developer", "engineer", "programmer", "architect", "analyst", "devops",
    "data", "frontend", "backend", "fullstack", "full stack", "cloud", "security",
    "admin", "dba", "sre", "qa", "tester", "mobile", "ios", "android", "ai", "ml", "tech",
    "sysadmin", "infrastructure", "systems", "network", "web", "ui/ux", "product designer",
    "scrum master", "product owner", "machine learning", "deep learning", "nlp", "blockchain"
}

# ── Certification Role Relevance Matrix ────────────────────────────────────────
CERTIFICATION_ROLE_RELEVANCE: Dict[str, Dict[str, float]] = {
    "aws certified solutions architect": {
        "Cloud Solutions Architect": 1.0, "DevOps Engineer": 0.95, "Site Reliability Engineer": 0.95,
        "Backend Developer": 0.85, "Software Engineer": 0.80, "Full Stack Developer": 0.80,
        "UI/UX Designer": 0.05, "Data Scientist": 0.40, "QA/Test Automation Engineer": 0.30
    },
    "aws certified developer": {
        "Cloud Solutions Architect": 0.90, "DevOps Engineer": 0.90, "Backend Developer": 0.95,
        "Software Engineer": 0.90, "Full Stack Developer": 0.90, "UI/UX Designer": 0.05
    },
    "aws certified sysops administrator": {
        "DevOps Engineer": 1.0, "Site Reliability Engineer": 0.95, "Cloud Solutions Architect": 0.90,
        "Systems Administrator": 0.95, "Software Engineer": 0.60, "UI/UX Designer": 0.0
    },
    "certified kubernetes administrator": {
        "DevOps Engineer": 1.0, "Site Reliability Engineer": 1.0, "Cloud Solutions Architect": 0.95,
        "Backend Developer": 0.75, "Software Engineer": 0.70, "UI/UX Designer": 0.0
    },
    "ccna": {
        "Network Engineer": 1.0, "Cybersecurity Analyst": 0.85, "Systems Administrator": 0.85,
        "DevOps Engineer": 0.65, "Software Engineer": 0.40, "Data Scientist": 0.05, "UI/UX Designer": 0.0
    },
    "ccnp": {
        "Network Engineer": 1.0, "Cybersecurity Analyst": 0.90, "Data Scientist": 0.05, "UI/UX Designer": 0.0
    },
    "cissp": {
        "Cybersecurity Analyst": 1.0, "Security Engineer": 1.0, "Cloud Solutions Architect": 0.80,
        "Software Engineer": 0.40, "UI/UX Designer": 0.0, "Data Scientist": 0.10
    },
    "ceh": {
        "Cybersecurity Analyst": 1.0, "Network Engineer": 0.75, "Software Engineer": 0.40, "UI/UX Designer": 0.0
    },
    "comptia security+": {
        "Cybersecurity Analyst": 1.0, "Network Engineer": 0.80, "Systems Administrator": 0.80,
        "Software Engineer": 0.40, "UI/UX Designer": 0.0
    },
    "tensorflow developer": {
        "Machine Learning Engineer": 1.0, "Data Scientist": 1.0, "AI/NLP Engineer": 1.0,
        "Software Engineer": 0.60, "Network Engineer": 0.0, "UI/UX Designer": 0.0
    },
    "pmp": {
        "Business/Systems Analyst": 1.0, "Software Engineer": 0.40, "UI/UX Designer": 0.30
    },
    "certified scrum master": {
        "Business/Systems Analyst": 1.0, "Software Engineer": 0.60, "Frontend Developer": 0.50
    }
}

# ── Education Field vs Role Relevance Matrix ──────────────────────────────────
EDUCATION_FIELD_ROLE_RELEVANCE: Dict[str, Dict[str, float]] = {
    "Software Engineer": {
        "Computer Science": 1.0, "Software Engineering": 1.0, "Information Technology": 1.0,
        "Computer Engineering": 1.0, "Information Systems": 0.90, "Data Science": 0.95,
        "Artificial Intelligence": 1.0, "Engineering": 0.85, "Mathematics": 0.65, "Physics": 0.60,
        "Accounting & Finance": 0.05, "Business Administration": 0.15, "Culinary & Hospitality": 0.0,
        "Medicine & Health": 0.0, "Arts & Humanities": 0.0, "Law": 0.0
    },
    "Backend Developer": {
        "Computer Science": 1.0, "Software Engineering": 1.0, "Information Technology": 1.0,
        "Computer Engineering": 1.0, "Information Systems": 0.90, "Data Science": 0.90,
        "Artificial Intelligence": 0.90, "Mathematics": 0.60, "Accounting & Finance": 0.05,
        "Culinary & Hospitality": 0.0
    },
    "Frontend Developer": {
        "Computer Science": 0.95, "Software Engineering": 1.0, "Information Technology": 1.0,
        "Interactive Media & HCI": 1.0, "Web Development": 1.0, "Graphic Design": 0.75,
        "Accounting & Finance": 0.05, "Culinary & Hospitality": 0.0
    },
    "Full Stack Developer": {
        "Computer Science": 1.0, "Software Engineering": 1.0, "Information Technology": 1.0,
        "Computer Engineering": 1.0, "Information Systems": 0.90, "Web Development": 1.0
    },
    "Data Scientist": {
        "Data Science": 1.0, "Statistics": 1.0, "Mathematics": 0.95, "Computer Science": 0.90,
        "Artificial Intelligence": 1.0, "Machine Learning": 1.0, "Physics": 0.80,
        "Information Technology": 0.80, "Economics / Econometrics": 0.70, "Accounting & Finance": 0.20,
        "Culinary & Hospitality": 0.0
    },
    "Machine Learning Engineer": {
        "Data Science": 1.0, "Artificial Intelligence": 1.0, "Machine Learning": 1.0,
        "Computer Science": 0.95, "Mathematics": 0.90, "Statistics": 0.90,
        "Software Engineering": 0.85, "Information Technology": 0.80
    },
    "DevOps Engineer": {
        "Computer Networks & Systems": 1.0, "Cloud & DevOps": 1.0, "Computer Science": 0.95,
        "Software Engineering": 0.95, "Information Technology": 0.95, "Computer Engineering": 0.95,
        "Networking": 0.95
    },
    "Cloud Solutions Architect": {
        "Cloud & DevOps": 1.0, "Computer Networks & Systems": 0.95, "Computer Science": 0.95,
        "Software Engineering": 0.95, "Information Technology": 0.95
    },
    "Cybersecurity Analyst": {
        "Cybersecurity": 1.0, "Information Security": 1.0, "Computer Networks & Systems": 0.95,
        "Networking": 0.95, "Computer Science": 0.90, "Information Technology": 0.90
    },
    "Network Engineer": {
        "Networking": 1.0, "Computer Networks & Systems": 1.0, "Telecommunications": 0.95,
        "Computer Engineering": 0.90, "Information Technology": 0.90, "Computer Science": 0.85
    },
    "Database Administrator": {
        "Business Information Systems": 1.0, "Information Technology": 1.0, "Computer Science": 0.95,
        "Software Engineering": 0.90, "Data Science": 0.90
    },
    "UI/UX Designer": {
        "Interactive Media & HCI": 1.0, "Graphic Design": 0.90, "Human Computer Interaction": 1.0,
        "Information Technology": 0.75, "Computer Science": 0.70
    },
    "Business/Systems Analyst": {
        "Business Information Systems": 1.0, "Information Technology": 0.95, "Management Information Systems": 1.0,
        "Computer Science": 0.85, "Business Administration": 0.75, "Accounting & Finance": 0.40
    },
    "QA/Test Automation Engineer": {
        "Computer Science": 1.0, "Software Engineering": 1.0, "Information Technology": 1.0,
        "Computer Engineering": 1.0, "Information Systems": 0.90, "Data Science": 0.85,
        "Accounting & Finance": 0.05, "Culinary & Hospitality": 0.0
    },
    "Data Engineer": {
        "Data Science": 1.0, "Computer Science": 1.0, "Software Engineering": 0.95,
        "Information Technology": 0.95, "Computer Engineering": 1.0, "Mathematics": 0.85, "Statistics": 0.85
    },
    "Site Reliability Engineer": {
        "Computer Networks & Systems": 1.0, "Cloud & DevOps": 1.0, "Computer Science": 0.95,
        "Software Engineering": 0.95, "Information Technology": 0.95, "Computer Engineering": 0.95
    },
    "Mobile App Developer": {
        "Computer Science": 1.0, "Software Engineering": 1.0, "Information Technology": 1.0,
        "Computer Engineering": 0.95, "Interactive Media & HCI": 0.90
    },
    "AI/NLP Engineer": {
        "Artificial Intelligence": 1.0, "Data Science": 1.0, "Machine Learning": 1.0,
        "Computer Science": 0.95, "Mathematics": 0.90, "Statistics": 0.90, "Software Engineering": 0.85
    },
    "Blockchain Developer": {
        "Computer Science": 1.0, "Software Engineering": 1.0, "Cybersecurity": 0.95,
        "Information Technology": 0.90, "Computer Engineering": 0.90
    },
    "Embedded Systems Engineer": {
        "Computer Engineering": 1.0, "Electrical Engineering": 1.0, "Electronic Engineering": 1.0,
        "Systems Engineering": 0.95, "Computer Science": 0.90, "Software Engineering": 0.85
    }
}


def _classify_relevance_category(score: float) -> str:
    """Classify numeric relevance score (0.0 - 1.0) into standard categories."""
    if score >= 0.80:
        return "HIGHLY_RELEVANT"
    elif score >= 0.60:
        return "RELEVANT"
    elif score >= 0.40:
        return "PARTIALLY_RELEVANT"
    elif score >= 0.10:
        return "WEAKLY_RELATED"
    else:
        return "IRRELEVANT"


def _merge_calendar_intervals(intervals: List[Tuple[float, float]]) -> float:
    """Merge overlapping [start_year, end_year] intervals and return total non-overlapping years."""
    if not intervals:
        return 0.0
    sorted_ivs = sorted(intervals, key=lambda x: x[0])
    merged: List[List[float]] = []
    for s, e in sorted_ivs:
        if s > e:
            continue
        if not merged:
            merged.append([s, e])
        else:
            if s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
    return sum(e - s for s, e in merged)


def extract_employment_records(text: str, target_role: str = "Software Engineer") -> List[Dict[str, Any]]:
    """Extract individual employment records with title, company, dates, responsibilities, and role relevance."""
    sections = extract_sections(text)
    exp_text = sections.get("experience", "")

    # If the document is structured with sections (e.g. education, projects, skills, activities, references)
    # but does NOT have an experience section, then the candidate has no professional employment history.
    has_other_sections = any(
        k in sections for k in ["education", "projects", "skills", "activities", "references", "certifications", "summary"]
    )
    if not exp_text:
        if has_other_sections:
            return []
        # Fallback to whole text ONLY if the document has NO standard section headings at all (completely unformatted text)
        exp_text = text

    lines = exp_text.splitlines()
    records: List[Dict[str, Any]] = []
    current_record: Optional[Dict[str, Any]] = None

    title_indicators = [
        "developer", "engineer", "architect", "lead", "analyst", "administrator",
        "consultant", "intern", "manager", "specialist", "scientist", "programmer", "designer",
        "accountant", "auditor", "bookkeeper", "cashier", "chef", "cook", "nurse", "officer",
        "executive", "representative", "associate", "coordinator", "assistant", "teacher",
        "trainee", "director", "head", "supervisor", "technician", "specialist"
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
                    bullet_l = clean_bullet.lower()
                    for cat_skills in SKILL_LEXICON.values():
                        for s in cat_skills:
                            if s in bullet_l and s not in current_record["technologies"]:
                                current_record["technologies"].append(SKILL_ALIASES.get(s, s))

    if current_record and current_record.get("job_title"):
        records.append(current_record)

    compat_map = ROLE_COMPATIBILITY.get(target_role, {})
    from data.role_requirements import REQUIRED_SKILLS
    target_req_skills = set(s.lower() for s in REQUIRED_SKILLS.get(target_role, []))

    ROLE_RESPONSIBILITY_KEYWORDS: Dict[str, Set[str]] = {
        "Backend Developer": {"api", "rest", "backend", "database", "microservices", "sql", "fastapi", "django", "flask", "spring", "server", "postgres", "postgresql", "redis", "kafka", "orm", "endpoint", "crud", "queries"},
        "Frontend Developer": {"react", "vue", "angular", "css", "html", "html5", "ui", "ux", "component", "components", "responsive", "web", "redux", "tailwind", "dom", "frontend", "typescript", "javascript", "browser", "figma"},
        "Full Stack Developer": {"react", "vue", "node", "node.js", "backend", "frontend", "api", "database", "fullstack", "full stack", "web", "rest", "sql", "python", "javascript", "microservices"},
        "Software Engineer": {"software", "architecture", "api", "algorithms", "data structures", "system", "systems", "backend", "frontend", "testing", "tests", "unit", "git", "ci/cd", "development", "web", "components", "react", "node", "node.js", "python", "java", "jira", "code", "services", "database", "sql"},
        "Machine Learning Engineer": {"machine learning", "ml", "deep learning", "model", "models", "tensorflow", "pytorch", "nlp", "training", "inference", "scikit-learn", "neural", "pipeline", "pandas", "dataset"},
        "Data Scientist": {"statistics", "data analysis", "machine learning", "pandas", "numpy", "visualization", "hypothesis", "predictive", "regression", "classification", "sql", "insights", "analytics", "experiments"},
        "DevOps Engineer": {"ci/cd", "docker", "kubernetes", "terraform", "pipeline", "aws", "cloud", "jenkins", "ansible", "deployment", "infrastructure", "linux", "monitoring"},
        "Cloud Solutions Architect": {"cloud", "aws", "azure", "gcp", "architecture", "infrastructure", "migration", "serverless", "security", "scalability", "cost optimization"},
        "Cybersecurity Analyst": {"security", "vulnerability", "siem", "soc", "penetration", "incident", "threat", "firewall", "compliance", "encryption", "audit", "forensics"},
        "Network Engineer": {"network", "cisco", "routing", "switching", "vpn", "bgp", "ospf", "lan", "wan", "firewall", "tcp/ip", "dns", "subnets"},
        "UI/UX Designer": {"wireframe", "prototype", "figma", "sketch", "user research", "usability", "design system", "persona", "mockup", "interaction design"},
        "QA/Test Automation Engineer": {"qa", "test", "testing", "selenium", "pytest", "junit", "automation", "uat", "manual", "defect", "jira", "regression", "bdd", "cucumber", "testrail", "postman", "cases", "validation"},
        "Data Engineer": {"pipeline", "etl", "spark", "airflow", "kafka", "hadoop", "sql", "data lake", "data warehouse", "snowflake", "bigquery", "streaming", "batch", "ingestion", "dbt"},
        "Site Reliability Engineer": {"sre", "reliability", "prometheus", "grafana", "monitoring", "alerting", "kubernetes", "incident", "sla", "slo", "sli", "infrastructure", "linux", "cloud", "docker"},
        "Database Administrator": {"database", "sql", "oracle", "mysql", "postgres", "postgresql", "dba", "backup", "recovery", "replication", "indexing", "performance", "tuning", "stored procedures"},
        "Mobile App Developer": {"mobile", "ios", "android", "swift", "kotlin", "flutter", "react native", "app", "ui", "sdk", "xcode", "gradle", "play store", "app store"},
        "Business/Systems Analyst": {"requirements", "business analyst", "systems analyst", "agile", "scrum", "jira", "confluence", "user stories", "use cases", "stakeholder", "process", "workflow", "functional", "specifications"},
        "AI/NLP Engineer": {"nlp", "natural language", "transformers", "bert", "llm", "embeddings", "ner", "text", "langchain", "prompt", "tokenization", "huggingface", "spacy", "genai"},
        "Blockchain Developer": {"blockchain", "solidity", "smart contract", "smart contracts", "ethereum", "web3", "crypto", "defi", "nft", "dapp", "consensus", "truffle", "hardhat"},
        "Embedded Systems Engineer": {"embedded", "microcontroller", "firmware", "c", "c++", "rtos", "arm", "iot", "sensor", "hardware", "pcb", "i2c", "spi", "uart", "device driver"}
    }

    target_keywords = ROLE_RESPONSIBILITY_KEYWORDS.get(target_role, {"software", "engineer", "development", "api", "system", "code", "testing"})

    for rec in records:
        t_low = rec["job_title"].lower()
        duration_m = rec.get("duration_months", 12.0)
        has_dates = rec.get("has_explicit_dates", False)
        resp_list = rec.get("responsibilities", [])
        tech_list = rec.get("technologies", [])

        is_explicit_non_it = any(re.search(r'\b' + re.escape(kw) + r'\b', t_low) for kw in NON_IT_KEYWORDS)
        has_it_title = any(re.search(r'\b' + re.escape(kw) + r'\b', t_low) for kw in IT_TITLE_KEYWORDS)

        is_it = has_it_title and not is_explicit_non_it
        if not is_it and not is_explicit_non_it:
            if len(tech_list) >= 2 or len(resp_list) >= 2:
                is_it = True

        if is_explicit_non_it or not is_it:
            rec.update({
                "industry_domain": "Non-IT / " + rec.get("job_title", "General"),
                "is_it_related": False,
                "category": "NON_IT",
                "title_similarity": 0.0,
                "responsibility_similarity": 0.0,
                "technology_similarity": 0.0,
                "skill_similarity": 0.0,
                "semantic_similarity": 0.0,
                "domain_relevance": 0.0,
                "target_role_relevance": 0.0,
                "relevance_to_target_role": 0.0,
                "relevance_category": "IRRELEVANT",
                "relevant_experience_months": 0.0,
                "relevant_months": 0.0,
                "extraction_confidence": 0.95 if has_dates else 0.70,
                "relevance_confidence": 0.98,
                "manual_review_recommended": False,
                "extracted_skills": tech_list,
                "explanation": f"Job title '{rec['job_title']}' is non-IT and has 0% relevance to target role '{target_role}'."
            })
            continue

        rec["industry_domain"] = "Information Technology"
        rec["is_it_related"] = True
        rec["category"] = "IT_RELEVANT"
        domain_relevance = 1.0

        title_sim = 0.0
        if target_role.lower() in t_low or t_low in target_role.lower():
            title_sim = 1.0
        elif any(re.search(r'\b' + re.escape(w) + r'\b', t_low) for w in target_role.lower().split()):
            title_sim = 0.90
        else:
            for role_key, score_val in compat_map.items():
                if role_key in t_low:
                    title_sim = max(title_sim, score_val)

        if title_sim == 0.0:
            if any(k in t_low for k in ["software engineer", "software developer", "engineer"]):
                title_sim = 0.70
            elif any(k in t_low for k in ["developer", "programmer"]):
                title_sim = 0.50
            elif has_it_title:
                title_sim = 0.40
            else:
                title_sim = 0.20

        resp_text = " ".join(resp_list).lower()
        resp_words = set(re.findall(r'\b[a-zA-Z\+\#\.\-]{2,}\b', resp_text))
        
        has_resp = len(resp_list) > 0
        if has_resp:
            overlap_resp = len(resp_words.intersection(target_keywords))
            resp_sim = min(1.0, overlap_resp / max(2, len(target_keywords) * 0.2))
            
            if target_role == "Backend Developer" and any(k in resp_text for k in ["react", "vue", "angular", "css", "html", "ui design"]) and not any(k in resp_text for k in ["api", "database", "sql", "backend", "server", "fastapi", "django"]):
                resp_sim = min(0.15, resp_sim)
            elif target_role == "Machine Learning Engineer" and not any(k in resp_text for k in ["machine learning", "ml", "deep learning", "model", "tensorflow", "pytorch", "scikit", "nlp", "pandas"]):
                resp_sim = min(0.15, resp_sim)
            elif target_role == "Software Engineer" and overlap_resp >= 2:
                resp_sim = max(resp_sim, 0.90)
        else:
            resp_sim = title_sim

        rec_techs = set(s.lower() for s in tech_list)
        has_tech = len(tech_list) > 0
        if has_tech:
            tech_matches = len(rec_techs.intersection(target_req_skills))
            tech_sim = min(1.0, tech_matches / max(2, len(target_req_skills) * 0.3))
            if tech_matches >= 2:
                tech_sim = 1.0
            elif tech_matches == 0:
                if target_role == "Backend Developer" and any(t in rec_techs for t in ["react", "vue", "html", "css", "figma"]):
                    tech_sim = 0.05
                elif target_role == "Software Engineer" and any(t in rec_techs for t in ["python", "java", "c++", "c#", "react", "node.js", "sql", "git", "jira"]):
                    tech_sim = 0.90
                else:
                    tech_sim = 0.30
        else:
            tech_sim = title_sim

        skill_matches = len(rec_techs.intersection(target_req_skills))
        skill_sim = min(1.0, skill_matches / max(2, len(target_req_skills) * 0.3)) if has_tech else title_sim

        semantic_sim = round((title_sim * 0.40) + (resp_sim * 0.60), 2)

        w_title = 0.20
        w_resp = 0.25 if has_resp else 0.0
        w_tech = 0.25 if has_tech else 0.0
        w_skill = 0.10 if has_tech else 0.0
        w_sem = 0.10
        w_domain = 0.10

        total_weight = w_title + w_resp + w_tech + w_skill + w_sem + w_domain
        if total_weight > 0:
            w_title /= total_weight
            w_resp /= total_weight
            w_tech /= total_weight
            w_skill /= total_weight
            w_sem /= total_weight
            w_domain /= total_weight

        hybrid_relevance = (
            (w_title * title_sim) +
            (w_resp * resp_sim) +
            (w_tech * tech_sim) +
            (w_skill * skill_sim) +
            (w_sem * semantic_sim) +
            (w_domain * domain_relevance)
        )

        if target_role in ["Software Engineer", "Full Stack Developer"] and title_sim >= 0.85:
            hybrid_relevance = max(hybrid_relevance, 0.90)
        elif target_role == "Full Stack Developer" and ("frontend" in t_low or "backend" in t_low or "web" in t_low or tech_sim >= 0.5):
            hybrid_relevance = max(hybrid_relevance, 0.85)

        hybrid_relevance = round(max(0.0, min(1.0, hybrid_relevance)), 2)
        rel_cat = _classify_relevance_category(hybrid_relevance)
        rel_months = round(duration_m * hybrid_relevance, 1)

        ext_conf = 0.95 if (has_dates and has_resp) else (0.80 if has_dates else 0.65)
        signal_spread = abs(title_sim - tech_sim) if has_tech else 0.0
        rel_conf = round(max(0.60, 0.95 - (signal_spread * 0.30)), 2)
        needs_review = (ext_conf < 0.70 or rel_conf < 0.65)

        if rel_cat == "HIGHLY_RELEVANT":
            explanation = f"Job title '{rec['job_title']}' and technical responsibilities are highly relevant ({int(hybrid_relevance*100)}%) to '{target_role}'."
        elif rel_cat == "RELEVANT":
            explanation = f"Job title '{rec['job_title']}' is directly relevant ({int(hybrid_relevance*100)}%) to '{target_role}'."
        elif rel_cat == "PARTIALLY_RELEVANT":
            explanation = f"Job title '{rec['job_title']}' shares partial technical overlap ({int(hybrid_relevance*100)}%) with '{target_role}'."
        elif rel_cat == "WEAKLY_RELATED":
            explanation = f"Job title '{rec['job_title']}' is weakly related ({int(hybrid_relevance*100)}%) to '{target_role}' with limited domain overlap."
        else:
            explanation = f"Job title '{rec['job_title']}' is not relevant to '{target_role}'."

        rec.update({
            "title_similarity": round(title_sim, 2),
            "responsibility_similarity": round(resp_sim, 2),
            "technology_similarity": round(tech_sim, 2),
            "skill_similarity": round(skill_sim, 2),
            "semantic_similarity": round(semantic_sim, 2),
            "domain_relevance": round(domain_relevance, 2),
            "target_role_relevance": hybrid_relevance,
            "relevance_to_target_role": hybrid_relevance,
            "relevance_category": rel_cat,
            "relevant_experience_months": rel_months,
            "relevant_months": rel_months,
            "extraction_confidence": ext_conf,
            "relevance_confidence": rel_conf,
            "manual_review_recommended": needs_review,
            "extracted_skills": tech_list,
            "explanation": explanation
        })

    return records


def extract_experience_years(text: str) -> float:
    """High-accuracy multi-strategy experience extraction with chronological date interval merging."""
    if not text:
        return 0.0

    lowered = text.lower()
    candidates: List[float] = []

    # 2. Extract sections & non-overlapping intervals
    sections = extract_sections(text)
    work_text = sections.get("experience", "")
    has_other_sections = any(
        k in sections for k in ["education", "projects", "skills", "activities", "references", "certifications", "summary"]
    )

    # 1. Explicit experience statements (search in summary or experience if structured)
    search_target = (sections.get("summary", "") + "\n" + sections.get("experience", "")) if has_other_sections else text
    search_target_low = search_target.lower()

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
        for m in re.finditer(pattern, search_target_low):
            try:
                val = float(m.group(1))
                unit = m.group(2) if len(m.groups()) >= 2 else "years"
                if unit and 'm' in unit.lower():
                    val = val / 12.0
                if 0.1 <= val <= 45.0:
                    candidates.append(round(val, 2))
            except (ValueError, IndexError):
                pass

    # Fallback if no explicit work section header: exclude lines clearly belonging to education or school
    if not work_text:
        if has_other_sections:
            # Document is structured into sections and has NO experience section. Candidate has NO employment experience.
            work_text = ""
        else:
            filtered_lines = []
            is_edu = False
            for l in text.splitlines():
                ll = l.strip().lower()
                if re.match(r'^(?:educational\s+background|academic\s+background|educational\s+qualifications?|academic\s+qualifications?|education|academics?|schooling|degrees?|qualifications?)\b', ll):
                    is_edu = True
                    continue
                elif re.match(r'^(?:projects?|key\s+projects?|skills?|certifications?|references?|activities|clubs?)\b', ll):
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
        total_span = _merge_calendar_intervals(intervals)
        if total_span > 0:
            candidates.append(round(total_span, 1))

    # 5. Month patterns
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

    return 0.0


def extract_experience_details(text: str, target_role: str = "Software Engineer") -> Dict[str, Any]:
    """Calculate Total Professional Experience, IT Experience, and Target-Role Relevant Experience separately."""
    records = extract_employment_records(text, target_role)
    total_exp_years = extract_experience_years(text)

    if records:
        # Build non-overlapping intervals for total professional experience
        all_intervals = [
            (r["start_year"], r["end_year"])
            for r in records
            if r.get("has_explicit_dates") and r.get("end_year", 0.0) >= r.get("start_year", 0.0)
        ]
        if all_intervals:
            merged_total_years = _merge_calendar_intervals(all_intervals)
        else:
            merged_total_years = sum(r.get("duration_months", 0.0) for r in records) / 12.0

        total_prof_years = round(max(total_exp_years, merged_total_years), 2)
        total_prof_months = round(total_prof_years * 12.0, 1)

        # Build non-overlapping intervals for IT sector experience
        it_records = [r for r in records if r.get("is_it_related", False)]
        it_intervals = [
            (r["start_year"], r["end_year"])
            for r in it_records
            if r.get("has_explicit_dates") and r.get("end_year", 0.0) >= r.get("start_year", 0.0)
        ]
        if it_intervals:
            it_years = round(_merge_calendar_intervals(it_intervals), 2)
        else:
            it_years = round(sum(r.get("duration_months", 0.0) for r in it_records) / 12.0, 2)
        it_months = round(it_years * 12.0, 1)

        # Target-role relevant experience: weighted sum of record durations
        relevant_months = round(sum(r.get("relevant_experience_months", 0.0) for r in records), 1)
        # Cap relevant months by IT timeline to prevent double-counting parallel jobs
        relevant_months = min(it_months, relevant_months)
        relevant_exp_years = round(relevant_months / 12.0, 2)
    else:
        # No employment records parsed from text
        total_prof_years = round(total_exp_years, 2)
        total_prof_months = round(total_prof_years * 12.0, 1)
        it_years = total_prof_years
        it_months = total_prof_months
        relevant_exp_years = total_prof_years
        relevant_months = total_prof_months

    seniority_info = detect_seniority(records, relevant_exp_years, text)

    return {
        "total_professional_experience_months": total_prof_months,
        "total_professional_experience_years": total_prof_years,
        "total_experience_years": total_prof_years,
        "it_sector_experience_months": it_months,
        "it_sector_experience_years": it_years,
        "it_experience_years": it_years,
        "target_role_relevant_experience_months": relevant_months,
        "target_role_relevant_experience_years": relevant_exp_years,
        "role_relevant_experience_years": relevant_exp_years,
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
        "Mathematics": (r'mathematics', r'applied mathematics', r'statistics', r'\bmath\b', r'actuarial'),
        "Engineering": (r'computer engineering', r'electrical engineering', r'electronic engineering', r'systems engineering', r'engineering')
    }

    non_it_major_patterns = {
        "Accounting & Finance": (r'accounting', r'finance', r'banking', r'commerce', r'accountancy', r'accountant'),
        "Business Administration": (r'business administration', r'\bmba\b', r'\bbba\b', r'marketing', r'management', r'human resources'),
        "Culinary & Hospitality": (r'culinary', r'hospitality', r'hotel management', r'catering', r'tourism'),
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


def extract_education_details(text: str, target_role: str = "Software Engineer") -> Dict[str, Any]:
    """Extract structured education details including degree, field relevance, coursework, and recognized certifications."""
    edu_info = extract_education_level(text)
    sections = extract_sections(text)
    edu_text = sections.get("education", text)
    edu_low = edu_text.lower()

    # 1. Institution extraction heuristics
    inst_match = re.search(r'\b(?:at|from|university\s+of|institute\s+of)\s+([A-Za-z\s]+(?:University|Institute|College|Academy|SLIIT|IIT))\b', edu_text, re.I)
    institution = inst_match.group(0).strip() if inst_match else "Recognized Higher Education Institution"

    # 2. Graduation year
    year_match = re.search(r'\b(20[0-2]\d|19[8-9]\d)\b', edu_text)
    grad_year = int(year_match.group(1)) if year_match else None

    # 3. Coursework extraction
    coursework: List[str] = []
    coursework_patterns = [
        r'(?:coursework|relevant\s+courses?|modules?|key\s+subjects?|subjects?)\s*[:\-]\s*([^\.\n]+)',
        r'(?:courses?|modules?)\s+included?\s*[:\-]?\s*([^\.\n]+)'
    ]
    for cp in coursework_patterns:
        m = re.search(cp, edu_low)
        if m:
            raw_courses = re.split(r'[,;•|/]', m.group(1))
            for c in raw_courses:
                c_clean = c.strip()
                if 3 <= len(c_clean) <= 40:
                    coursework.append(c_clean.title())

    # 4. Field relevance calculation
    majors = edu_info.get("majors", [])
    specializations = edu_info.get("specializations", [])
    all_fields = specializations + majors

    field_map = EDUCATION_FIELD_ROLE_RELEVANCE.get(target_role, {})
    best_field_rel = 0.20
    matched_field = majors[0] if majors else "General IT"
    for f in all_fields:
        if f in field_map:
            if field_map[f] > best_field_rel:
                best_field_rel = field_map[f]
                matched_field = f

    is_non_it = any(m in ["Accounting & Finance", "Business Administration", "Culinary & Hospitality", "Medicine & Health", "Arts & Humanities", "Law"] for m in majors)
    if is_non_it and not any(f in field_map for f in all_fields):
        best_field_rel = 0.05
        matched_field = majors[0] if majors else "Non-IT"

    # Coursework boost (e.g. Mathematics degree with Machine Learning / Data Science courses for Data Scientist)
    coursework_rel = 0.0
    has_coursework = len(coursework) > 0
    if has_coursework:
        cw_text = " ".join(coursework).lower()
        if target_role in ["Data Scientist", "Machine Learning Engineer"] and any(k in cw_text for k in ["machine learning", "statistics", "data science", "python", "deep learning", "probability", "data mining"]):
            coursework_rel = 1.0
            best_field_rel = max(best_field_rel, 0.90)
        elif target_role in ["Software Engineer", "Backend Developer", "Full Stack Developer"] and any(k in cw_text for k in ["algorithms", "data structures", "software engineering", "database", "operating systems", "oop", "web development"]):
            coursework_rel = 1.0
            best_field_rel = max(best_field_rel, 0.90)
        elif any(k in cw_text for k in ["it", "programming", "computer", "systems", "network"]):
            coursework_rel = 0.70
            best_field_rel = max(best_field_rel, 0.75)
        else:
            coursework_rel = 0.30

    if best_field_rel >= 0.80:
        field_rel_cat = "HIGH"
    elif best_field_rel >= 0.60:
        field_rel_cat = "RELEVANT"
    elif best_field_rel >= 0.40:
        field_rel_cat = "PARTIAL"
    elif best_field_rel >= 0.10:
        field_rel_cat = "LOW"
    else:
        field_rel_cat = "IRRELEVANT"

    # 5. Verified Certifications evaluated against target role
    skills_certs = extract_skills_and_certifications(text)
    verified_certs = []
    relevant_certs = []
    cert_max_rel = 0.0
    for cert in skills_certs.get("detected_certs", []):
        cert_l = cert.lower()
        cert_rel = 0.50
        issuing_body = "Industry Vendor"
        tier = "Professional"

        if cert_l in CANONICAL_CERTIFICATIONS:
            meta = CANONICAL_CERTIFICATIONS[cert_l]
            issuing_body = meta["vendor"]
            tier = meta["tier"]

        if cert_l in CERTIFICATION_ROLE_RELEVANCE:
            role_map = CERTIFICATION_ROLE_RELEVANCE[cert_l]
            cert_rel = role_map.get(target_role, 0.20)
        else:
            cert_rel = 0.50

        cert_max_rel = max(cert_max_rel, cert_rel)
        cert_obj = {
            "certification": cert,
            "issuing_body": issuing_body,
            "tier": tier,
            "is_verified_credential": True,
            "relevance_score": round(cert_rel, 2),
            "is_role_relevant": cert_rel >= 0.60
        }
        verified_certs.append(cert_obj)
        if cert_rel >= 0.60:
            relevant_certs.append(cert_obj)

    # 6. Hybrid Education Relevance Calculation
    deg_level_match = edu_info["level_score"]
    spec_rel = 1.0 if specializations else (0.80 if field_rel_cat in ["HIGH", "RELEVANT"] else 0.20)

    # Dynamic weights
    w_level = 0.25
    w_field = 0.35
    w_spec = 0.15 if specializations else 0.0
    w_course = 0.15 if has_coursework else 0.0
    w_cert = 0.10

    total_w = w_level + w_field + w_spec + w_course + w_cert
    if total_w > 0:
        w_level /= total_w
        w_field /= total_w
        w_spec /= total_w
        w_course /= total_w
        w_cert /= total_w

    edu_rel_composite = (
        (w_level * (deg_level_match / 0.60 if deg_level_match <= 0.60 else 1.0)) +
        (w_field * best_field_rel) +
        (w_spec * spec_rel) +
        (w_course * coursework_rel) +
        (w_cert * cert_max_rel)
    )
    edu_rel_composite = round(max(0.0, min(1.0, edu_rel_composite)) * 100.0, 1)

    # Confidence estimation
    ext_conf = 0.95 if (institution != "Recognized Higher Education Institution" and grad_year) else (0.80 if grad_year else 0.65)

    # Explanation construction
    deg_level = edu_info["level_name"]
    if field_rel_cat in ["HIGH", "RELEVANT"]:
        explanation = f"{deg_level} in {matched_field} is highly relevant to {target_role}."
    elif field_rel_cat == "PARTIAL":
        explanation = f"{deg_level} in {matched_field} shares foundational quantitative/analytical overlap with {target_role}."
    else:
        explanation = f"{deg_level} level is acceptable, but {matched_field} is not directly related to {target_role}."

    return {
        "qualification": f"{deg_level} in {matched_field}",
        "degree_level": deg_level,
        "degree_field": matched_field,
        "field": matched_field,
        "specialization": specializations[0] if specializations else "General",
        "specializations": specializations,
        "coursework": coursework,
        "degree_level_match": round(deg_level_match, 2),
        "level_score": edu_info["level_score"],
        "majors": edu_info["majors"],
        "field_relevance": field_rel_cat,
        "field_relevance_score": round(best_field_rel, 2),
        "specialization_relevance": round(spec_rel, 2),
        "coursework_relevance": round(coursework_rel, 2),
        "certification_relevance": round(cert_max_rel, 2),
        "education_relevance": edu_rel_composite,
        "extraction_confidence": ext_conf,
        "institution": institution,
        "graduation_year": grad_year,
        "verified_certifications": verified_certs,
        "relevant_certifications": relevant_certs,
        "explanation": explanation
    }


# ── Contextual Skills Extraction ───────────────────────────────────────────────

def extract_skills_and_certifications(text: str, target_role: str = "Software Engineer") -> Dict[str, Any]:
    """Extract detected skills, aliases, multi-source evidence levels, and certifications."""
    if not text:
        return {
            "detected_skills": [],
            "detected_certs": [],
            "skill_evidence": {},
            "skill_category_counts": {}
        }

    lowered = text.lower()
    sections = extract_sections(text)
    skills_sec = sections.get("skills", "").lower()
    exp_text = sections.get("experience", "").lower()
    proj_text = sections.get("projects", "").lower()
    edu_text = sections.get("education", "").lower()
    cert_text = sections.get("certifications", "").lower()
    sum_text = sections.get("summary", "").lower()

    detected_skills: Set[str] = set()
    skill_evidence: Dict[str, Any] = {}
    category_counts: Dict[str, int] = {}

    sentences = [s.strip() for s in re.split(r'[\.\n;•·]+', text) if len(s.strip()) > 8]

    for category, skills in SKILL_LEXICON.items():
        count = 0
        for skill in skills:
            pattern = _SKILL_PATTERNS.get(skill)
            if pattern and pattern.search(lowered):
                normalized = SKILL_ALIASES.get(skill, skill)
                detected_skills.add(normalized)
                count += 1

                # Multi-Source Evidence Tracking
                sources = []
                if pattern.search(skills_sec):
                    sources.append("skills")
                if pattern.search(exp_text):
                    sources.append("work_experience")
                if pattern.search(proj_text):
                    sources.append("projects")
                if pattern.search(cert_text):
                    sources.append("certifications")
                if pattern.search(edu_text):
                    sources.append("education")
                if pattern.search(sum_text):
                    sources.append("summary")

                matching_snippets = [s for s in sentences if pattern.search(s.lower())][:3]
                has_action = any(any(v in snip.lower() for v in _ACTION_VERBS) for snip in matching_snippets)

                # STAGE 5: Multi-Source Evidence Confidence
                if len(sources) >= 3 or ("work_experience" in sources and "projects" in sources) or ("work_experience" in sources and has_action):
                    confidence = 0.95
                    strength = "very_high"
                elif "work_experience" in sources or (len(sources) >= 2 and ("projects" in sources or "certifications" in sources)):
                    confidence = 0.85
                    strength = "high"
                elif "projects" in sources:
                    confidence = 0.70
                    strength = "medium"
                elif "certifications" in sources or "education" in sources:
                    confidence = 0.60
                    strength = "medium"
                elif sources == ["skills"]:
                    # Mentioned only once in skills list without proof -> LOW CONFIDENCE
                    confidence = 0.45
                    strength = "low"
                else:
                    confidence = 0.50
                    strength = "low"

                skill_evidence[normalized] = {
                    "skill": normalized,
                    "normalized_skill": normalized,
                    "canonical_skill": normalized.title() if len(normalized) > 3 else normalized.upper(),
                    "evidence_sources": sources,
                    "evidence_snippets": matching_snippets,
                    "evidence": matching_snippets,
                    "confidence": round(confidence, 2),
                    "evidence_strength": strength,
                    "evidence_level": strength.upper(),
                    "category": category,
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


def validate_cross_evidence(
    text: str,
    features: Any,
    target_role: str = "Software Engineer",
) -> Dict[str, Any]:
    """Perform multi-layer cross-evidence validation across skills, experience, education, and credentials."""
    skills = getattr(features, "skills", [])
    ev_dict = getattr(features, "skill_evidence", {})
    records = getattr(features, "employment_records", [])
    exp_years = getattr(features, "experience_years", 0.0)
    edu_str = getattr(features, "education", "")

    flags = []

    # 1. Skill Extraction Confidence
    if ev_dict:
        avg_skill_conf = sum(s.get("confidence", 0.5) for s in ev_dict.values()) / max(1, len(ev_dict))
    else:
        avg_skill_conf = 0.50
    skill_conf = round(avg_skill_conf, 2)

    # 2. Experience Extraction & Relevance Confidence
    has_dates = any(r.get("has_explicit_dates", False) for r in records)
    has_resp = any(len(r.get("responsibilities", [])) > 0 for r in records)
    if records and has_dates and has_resp:
        exp_ext_conf = 0.95
    elif records and has_dates:
        exp_ext_conf = 0.80
    elif exp_years == 0.0:
        exp_ext_conf = 0.90
    else:
        exp_ext_conf = 0.65

    if records:
        avg_rec_rel_conf = sum(r.get("relevance_confidence", 0.75) for r in records) / len(records)
    else:
        avg_rec_rel_conf = 0.85
    exp_rel_conf = round(avg_rec_rel_conf, 2)

    # 3. Education Extraction & Relevance Confidence
    if any(kw in edu_str.lower() for kw in ["bachelor", "bsc", "b.sc", "msc", "m.sc", "phd", "doctorate"]):
        edu_ext_conf = 0.95
    elif edu_str:
        edu_ext_conf = 0.80
    else:
        edu_ext_conf = 0.60

    edu_field_rel = getattr(features, "field_relevance", "HIGH")
    edu_rel_conf = 0.95 if edu_field_rel in ["HIGH", "RELEVANT"] else (0.80 if edu_field_rel == "PARTIAL" else 0.70)

    # 4. Overall Analysis Confidence Composite
    overall_conf = round(
        0.30 * skill_conf +
        0.25 * exp_ext_conf +
        0.20 * exp_rel_conf +
        0.15 * edu_ext_conf +
        0.10 * edu_rel_conf,
        2
    )

    # Cross-checks & Flags
    if len(skills) > 30 and sum(1 for s in ev_dict.values() if s.get("confidence", 0) >= 0.80) < 5:
        flags.append("High volume of skills listed with low practical employment evidence (potential keyword stuffing).")

    if exp_years >= 5.0 and len(records) == 0:
        flags.append("Experience tenure claimed in summary without verifiable segmented employment entries.")

    needs_manual_review = overall_conf < 0.70 or len(flags) > 0

    return {
        "skill_extraction_confidence": skill_conf,
        "experience_extraction_confidence": exp_ext_conf,
        "experience_relevance_confidence": exp_rel_conf,
        "education_extraction_confidence": edu_ext_conf,
        "education_relevance_confidence": edu_rel_conf,
        "overall_analysis_confidence": overall_conf,
        "manual_review_recommended": needs_manual_review,
        "validation_flags": flags
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


def extract_candidate_name(text: str) -> str:
    """Extract candidate full name from top lines of raw resume text."""
    if not text:
        return "Candidate Profile"
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:6]:
        # Skip contact info, urls, links, addresses, headers
        if re.search(r'[@\+]|\b(?:http|www|github|linkedin|resume|curriculum|vitae|profile|summary|education|skills|experience|phone|email)\b', line, re.I):
            continue
        cleaned = re.sub(r'[\(\[\{].*?[\)\]\}]', '', line).strip()
        cleaned = re.sub(r'^(?:name\s*[:\-]|profile\s*[:\-])\s*', '', cleaned, flags=re.I).strip()
        words = [w for w in re.split(r'[\s,·|•/]+', cleaned) if w.isalpha() and len(w) > 1]
        if 1 <= len(words) <= 4:
            return " ".join(words).title()
    return "Candidate Profile"


def extract_deep_cv_profile(text: str, target_role: str = "Software Engineer") -> Dict[str, Any]:
    """Consolidated deep extraction returning the full candidate understanding profile."""
    cleaned = clean_text(text)
    candidate_name = extract_candidate_name(text)
    skills_certs = extract_skills_and_certifications(text, target_role)
    exp_details = extract_experience_details(text, target_role)
    edu_details = extract_education_details(text, target_role)
    projects = extract_projects(text)

    return {
        "candidate_name": candidate_name,
        "cleaned_text": cleaned,
        "skills": skills_certs["detected_skills"],
        "skill_evidence": skills_certs["skill_evidence"],
        "detected_certs": skills_certs["detected_certs"],
        "experience": exp_details,
        "education": edu_details,
        "projects": projects
    }
