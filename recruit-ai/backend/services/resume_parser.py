"""Resume file parsing and NLP entity extraction."""
import re
from datetime import datetime
from typing import Any


def parse_resume_file(content: bytes, filename: str) -> str:
    """Extract text from PDF, DOCX, or TXT files."""
    name_lower = filename.lower()
    if name_lower.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")
    if name_lower.endswith(".pdf"):
        return _parse_pdf(content)
    if name_lower.endswith((".docx", ".doc")):
        return _parse_docx(content)
    return content.decode("utf-8", errors="ignore")


def _parse_pdf(content: bytes) -> str:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except ImportError:
        pass
    try:
        from pdfminer.high_level import extract_text
        import io
        return extract_text(io.BytesIO(content))
    except ImportError:
        return ""


def _parse_docx(content: bytes) -> str:
    try:
        from docx import Document
        import io
        doc = Document(io.BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except ImportError:
        return ""


# ── NLP Preprocessing ──────────────────────────────────────────
STOPWORDS = set("a an the and or but in on at to for of with is it its this that was were be been "
                "being have has had do does did will would could should may might can shall from "
                "by as into through during before after above below between out off over under "
                "again further then once here there when where why how all each every both few "
                "more most other some such no nor not only own same so than too very s t just "
                "don now d ll m o re ve y ain aren couldn didn doesn hadn hasn haven isn ma "
                "mightn mustn needn shan shouldn wasn weren won wouldn".split())


def preprocess_text(text: str) -> str:
    """Lowercase, remove punctuation, remove stopwords, tokenize, lemmatize."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s#+./]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    try:
        import nltk
        from nltk.stem import WordNetLemmatizer
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(t) for t in tokens]
    except (ImportError, LookupError):
        pass
    return " ".join(tokens)


# ── Entity Extraction ───────────────────────────────────────────
SKILLS_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "kotlin", "swift",
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "ci/cd",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "git", "linux", "bash", "rest api", "graphql", "microservices",
    "html", "css", "sass", "bootstrap", "tailwind",
    "pandas", "numpy", "scikit-learn", "matplotlib", "jupyter",
    "figma", "sketch", "adobe xd",
    "blockchain", "solidity", "web3",
    "embedded", "iot", "arduino", "raspberry pi",
    "agile", "scrum", "jira",
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"[\+]?[\d\s\-\(\)]{7,15}")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-]+", re.I)
GITHUB_RE = re.compile(r"github\.com/[\w\-]+", re.I)
YEARS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?\s+(?:of\s+)?(?:experience|work|professional))|(?:experience|worked)\s*:?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", re.I)
EDU_RE = re.compile(r"(ph\.?d|doctorate|m\.?s\.?c?|master|b\.?s\.?c?|bachelor|b\.?tech|diploma|m\.?tech|mba)", re.I)
CERT_RE = re.compile(r"(?:certification|certificate|certified)[\s:]+([^\n]+)", re.I)
LANG_RE = re.compile(r"(?:language|fluent|proficient)[\s:]+([^\n]+)", re.I)

# ── Date patterns ───────────────────────────────────────────────
MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6,
    "jul": 7, "july": 7, "aug": 8, "august": 8, "sep": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
DATE_RANGE_RE = re.compile(
    r"((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
    r"aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"\s+\d{4})\s*[-–—to]+\s*"
    r"((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
    r"aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"\s+\d{4}|present|current|now)",
    re.I
)
# Also match "2022 - 2023" or "2022 - Present"
YEAR_RANGE_RE = re.compile(
    r"(\d{4})\s*[-–—to]+\s*(\d{4}|present|current|now)",
    re.I
)

# ── Project section patterns ────────────────────────────────────
PROJECT_SECTION_RE = re.compile(
    r"(?:academic\s+projects?|personal\s+projects?|projects?|capstone|thesis|"
    r"dissertation|coursework|portfolio|side\s+projects?|open[\s-]?source)"
    r"[\s:]*\n",
    re.I
)
ACADEMIC_KEYWORDS = {
    "thesis", "dissertation", "capstone", "coursework", "academic", "university",
    "college", "research", "paper", "study", "assignment", "lab", "seminar",
    "class", "school", "degree", "bachelor", "master", "phd",
}
PERSONAL_KEYWORDS = {
    "personal", "side project", "open source", "hobby", "freelance",
    "portfolio", "github", "contributed", "maintained",
}


def _parse_date(date_str: str) -> datetime | None:
    """Parse a date string like 'January 2023', 'Jan 2023', or just '2023'."""
    date_str = date_str.strip().lower()
    if date_str in ("present", "current", "now"):
        return datetime.now()
    parts = date_str.split()
    if len(parts) == 2:
        month_str, year_str = parts
        month = MONTH_MAP.get(month_str[:3])
        if month:
            try:
                return datetime(int(year_str), month, 1)
            except (ValueError, TypeError):
                pass
    elif len(parts) == 1:
        # Year only — assume January
        try:
            return datetime(int(parts[0]), 1, 1)
        except (ValueError, TypeError):
            pass
    return None


def _calc_duration_months(start: datetime, end: datetime) -> float:
    """Calculate duration in months between two dates."""
    months = (end.year - start.year) * 12 + (end.month - start.month)
    return max(months, 0.5)  # minimum 0.5 months (2 weeks)


def _extract_projects_with_dates(text: str) -> tuple[list[dict], list[dict]]:
    """Extract academic and personal projects with date ranges.
    
    Returns:
        (academic_projects, personal_projects) — each is a list of dicts:
        [{"name": str, "duration_months": float, "dates": str}, ...]
    """
    lines = text.split("\n")
    academic_projects = []
    personal_projects = []
    seen = set()
    
    # Section header patterns to skip
    SECTION_HEADER_RE = re.compile(
        r"^(?:academic\s+)?projects?\s*:?\s*$|"
        r"^(?:personal|side|open[\s-]?source)\s+projects?\s*:?\s*$",
        re.I
    )

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Skip section headers
        if SECTION_HEADER_RE.match(line_stripped):
            continue

        # Look for date ranges on this line
        date_match = DATE_RANGE_RE.search(line_stripped)
        if not date_match:
            date_match = YEAR_RANGE_RE.search(line_stripped)
        
        # Check for single date (e.g., "March 2023") if no range found
        single_date = None
        if not date_match:
            single_date_match = re.search(
                r"((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
                r"aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
                r"\s+\d{4})",
                line_stripped, re.I
            )
            if single_date_match:
                single_date = single_date_match.group(1)

        if not date_match and not single_date:
            continue

        # Extract the project name (the line with the date, or the line before)
        name_line = line_stripped
        # Remove date range from the name
        name_line = DATE_RANGE_RE.sub("", name_line).strip()
        name_line = YEAR_RANGE_RE.sub("", name_line).strip()
        name_line = re.sub(r"^[-–—•\*\s]+", "", name_line).strip()
        name_line = re.sub(r"[-–—•\*\s]+$", "", name_line).strip()
        
        if not name_line or len(name_line) < 3:
            continue
        if name_line in seen:
            continue
        seen.add(name_line)

        # Parse dates — use the match from THIS line if available
        dm = date_match  # prefer the date on the same line
        
        if dm:
            groups = dm.groups()
            start_str = groups[0] if groups else ""
            end_str = groups[1] if len(groups) > 1 else ""
            start_date = _parse_date(start_str)
            end_date = _parse_date(end_str) if end_str else None
            if start_date and end_date:
                duration = _calc_duration_months(start_date, end_date)
                date_display = f"{start_str} - {end_str}"
            elif start_date:
                duration = 0
                date_display = start_str
            else:
                duration = 0
                date_display = ""
        elif single_date:
            # Single date found, no range
            start_date = _parse_date(single_date)
            duration = 0
            date_display = single_date if start_date else ""
        else:
            duration = 0
            date_display = ""

        project = {
            "name": name_line,
            "duration_months": duration,
            "dates": date_display,
        }

        # Classify as academic or personal
        name_lower = name_line.lower()
        is_academic = any(kw in name_lower for kw in ACADEMIC_KEYWORDS)
        is_personal = any(kw in name_lower for kw in PERSONAL_KEYWORDS)

        # If neither detected, check section header
        if not is_academic and not is_personal:
            for j in range(i - 1, max(i - 5, -1), -1):
                header = lines[j].strip().lower()
                if "academic" in header or "thesis" in header or "capstone" in header:
                    is_academic = True
                    break
                elif "personal" in header or "side" in header or "open source" in header:
                    is_personal = True
                    break

        if is_academic:
            academic_projects.append(project)
        elif is_personal:
            personal_projects.append(project)
        else:
            personal_projects.append(project)

    return academic_projects, personal_projects


def extract_entities(text: str) -> dict[str, Any]:
    """Extract structured entities from resume text."""
    entities: dict[str, Any] = {
        "name": "", "email": "", "phone": "", "address": "",
        "linkedin": "", "github": "", "skills": [], "education": "",
        "experience_years": 0, "projects": [],
        "academic_projects": [], "personal_projects": [],
        "project_experience_years": 0,
        "certifications": [], "languages": [], "tools": [], "frameworks": [],
    }

    lines = text.strip().split("\n")
    non_empty = [l.strip() for l in lines if l.strip()]
    if non_empty:
        first_line = non_empty[0]
        if not EMAIL_RE.search(first_line) and not PHONE_RE.search(first_line):
            entities["name"] = first_line[:100]

    emails = EMAIL_RE.findall(text)
    if emails:
        entities["email"] = emails[0]

    phones = PHONE_RE.findall(text)
    if phones:
        entities["phone"] = phones[0].strip()

    linkedin = LINKEDIN_RE.findall(text)
    if linkedin:
        entities["linkedin"] = "https://" + linkedin[0]

    github = GITHUB_RE.findall(text)
    if github:
        entities["github"] = "https://" + github[0]

    text_lower = text.lower()
    text_normalized = re.sub(r"\s+", " ", text_lower)
    found_skills = []
    for skill in SKILLS_KEYWORDS:
        if re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", text_normalized):
            found_skills.append(skill.title())
    entities["skills"] = list(dict.fromkeys(found_skills))

    edu_match = EDU_RE.search(text)
    if edu_match:
        entities["education"] = edu_match.group(0).title()

    years_matches = YEARS_RE.findall(text)
    years_values = []
    for g1, g2 in years_matches:
        if g1:
            years_values.append(float(g1))
        if g2:
            years_values.append(float(g2))
    if years_values:
        raw_years = max(years_values)
        entities["experience_years"] = min(raw_years, 40)

    # Extract projects with dates and classify
    academic_projects, personal_projects = _extract_projects_with_dates(text)
    entities["academic_projects"] = academic_projects
    entities["personal_projects"] = personal_projects

    # Also keep flat project names for backward compat
    all_project_names = [p["name"] for p in academic_projects + personal_projects]
    entities["projects"] = all_project_names[:10]

    # Calculate total project experience in years
    total_months = sum(p["duration_months"] for p in academic_projects + personal_projects)
    entities["project_experience_years"] = round(total_months / 12, 1) if total_months > 0 else 0

    # Add project experience to experience_years if no work experience found
    if entities["experience_years"] == 0 and entities["project_experience_years"] > 0:
        entities["experience_years"] = entities["project_experience_years"]

    certs = CERT_RE.findall(text)
    entities["certifications"] = [c.strip() for c in certs[:5]]

    langs = LANG_RE.findall(text)
    entities["languages"] = [l.strip() for l in langs[:5]]

    return entities
