"""
Regex + Lexicon Based Information Extractor — Component 1
Extracts:
  - Cleaned text (PII removed: emails, phone numbers, URLs, addresses)
  - Experience years (numerical)
  - Education degree level & major fields
  - Certifications count & matched certification list
  - Technical skills matched from the comprehensive lexicon
"""

import re
from typing import Any, Dict, List, Set
from ml.lexicon import ALL_TECHNICAL_SKILLS, CERTIFICATIONS_LIST, SKILL_LEXICON


def clean_text(text: str) -> str:
    """Clean CV text by removing PII (emails, phones, URLs) while preserving technical terms."""
    if not text:
        return ""
    
    # 1. Remove Email addresses
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', ' ', text)
    
    # 2. Remove Phone numbers (various formats)
    text = re.sub(r'\+?\d[\d\s\-\(\)]{8,}\d', ' ', text)
    
    # 3. Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    
    # 4. Remove physical address patterns (zip codes / standard street numbers if obvious)
    text = re.sub(r'\b\d{5}(?:[-\s]\d{4})?\b', ' ', text)
    
    # 5. Normalize whitespace while keeping technical terms intact (C++, C#, .NET, Node.js)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = ' '.join(lines)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    return cleaned.strip()


def extract_experience_years(text: str) -> float:
    """Regex-based experience extraction from CV text."""
    if not text:
        return 0.0

    lowered = text.lower()

    # Pattern 1: Explicit years of experience: e.g. "5+ years of experience", "3 years experience", "worked 4 yrs"
    exp_patterns = [
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|work|industry|field|background)',
        r'(?:experience|worked|working)\s+(?:for\s+)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+in\b',
        r'over\s+(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
    ]

    found_years = []
    for pattern in exp_patterns:
        matches = re.findall(pattern, lowered)
        for m in matches:
            try:
                val = float(m)
                if 0.0 < val <= 40.0:
                    found_years.append(val)
            except ValueError:
                pass

    if found_years:
        return max(found_years)

    # Pattern 2: Year ranges, e.g., "2018 - 2023", "Jan 2020 - Dec 2023", or "2019 - Present"
    month_regex = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)?'
    range_pattern = r'\b' + month_regex + r'\s*(20[0-2]\d|19[8-9]\d)\s*(?:-|–|to)\s*' + month_regex + r'\s*(present|current|20[0-2]\d|19[8-9]\d)\b'
    range_matches = re.findall(range_pattern, lowered)
    total_range_years = 0.0

    current_year = 2026
    for start_str, end_str in range_matches:
        try:
            start_yr = int(start_str)
            if end_str in ('present', 'current'):
                end_yr = current_year
            else:
                end_yr = int(end_str)
            
            diff = end_yr - start_yr
            if 0 < diff <= 30:
                total_range_years += diff
        except ValueError:
            pass

    if total_range_years > 0.0:
        return min(total_range_years, 30.0)

    # Fallback pattern: simple standalone "X years"
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
        return {"level_score": 0.0, "level_name": "None", "major": "None"}

    lowered = text.lower()

    # Degree patterns
    phd_patterns = [r'\bph\.?d\b', r'\bdoctor of philosophy\b', r'\bdoctorate\b']
    msc_patterns = [r'\bm\.?sc\b', r'\bmaster\b', r'\bpostgraduate diploma\b', r'\bm\.?tech\b', r'\bmca\b']
    bsc_patterns = [r'\bb\.?sc\b', r'\bbachelor\b', r'\bb\.?tech\b', r'\bb\.?e\b', r'\bbca\b', r'\bundergraduate\b']
    dip_patterns = [r'\bdiploma\b', r'\bhnd\b', r'\bnvq\b', r'\bhigher diploma\b', r'\bassociate degree\b']

    level_score = 0.0
    level_name = "None"

    if any(re.search(p, lowered) for p in phd_patterns):
        level_score = 1.00  # 4/4
        level_name = "PhD"
    elif any(re.search(p, lowered) for p in msc_patterns):
        level_score = 0.80  # 3/4
        level_name = "MSc"
    elif any(re.search(p, lowered) for p in bsc_patterns):
        level_score = 0.60  # 2/4
        level_name = "BSc"
    elif any(re.search(p, lowered) for p in dip_patterns):
        level_score = 0.40  # 1/4
        level_name = "Diploma"

    # Majors
    majors = []
    major_patterns = {
        "Computer Science": [r'computer science', r'\bcs\b'],
        "Software Engineering": [r'software engineering', r'\bse\b'],
        "Information Technology": [r'information technology', r'\bit\b'],
        "Data Science": [r'data science', r'analytics'],
        "Cybersecurity": [r'cybersecurity', r'cyber security', r'information security'],
        "Networking": [r'network engineering', r'telecommunications'],
        "Engineering": [r'computer engineering', r'electrical engineering']
    }

    for major_name, p_list in major_patterns.items():
        if any(re.search(p, lowered) for p in p_list):
            majors.append(major_name)

    return {
        "level_score": level_score,
        "level_name": level_name,
        "majors": majors if majors else ["General IT"]
    }


def extract_skills_and_certifications(text: str) -> Dict[str, Any]:
    """Extract detected skills and certifications from lexicon matching."""
    if not text:
        return {"detected_skills": [], "detected_certs": [], "skill_category_counts": {}}

    lowered = text.lower()
    
    detected_skills = set()
    category_counts = {}

    for category, skills in SKILL_LEXICON.items():
        count = 0
        for skill in skills:
            # Word boundary regex for exact matching while allowing technical characters
            pattern = r'(?:\b|_)' + re.escape(skill) + r'(?:\b|_)'
            if re.search(pattern, lowered):
                detected_skills.add(skill)
                count += 1
        category_counts[category] = count

    detected_certs = []
    for cert in CERTIFICATIONS_LIST:
        pattern = r'(?:\b|_)' + re.escape(cert) + r'(?:\b|_)'
        if re.search(pattern, lowered):
            detected_certs.append(cert.title())

    return {
        "detected_skills": sorted(list(detected_skills)),
        "detected_certs": sorted(list(set(detected_certs))),
        "skill_category_counts": category_counts
    }
