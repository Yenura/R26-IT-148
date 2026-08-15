"""
Career Recommender Engine — Component 4
Recommends next roles and transition paths based on Jaccard & weighted skill similarity.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from src.preprocessing.skill_normalizer import normalize_skills
from src.gap_analysis.similarity import jaccard_similarity

ROOT_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = ROOT_DIR / "models"
JOB_REQ_FILE = MODELS_DIR / "job_requirements.json"
CAREER_PATHS_FILE = MODELS_DIR / "career_paths.json"


def load_data():
    reqs = {}
    paths = {}
    transitions = {}
    if JOB_REQ_FILE.exists():
        with open(JOB_REQ_FILE, "r", encoding="utf-8") as f:
            reqs = json.load(f)
    if CAREER_PATHS_FILE.exists():
        with open(CAREER_PATHS_FILE, "r", encoding="utf-8") as f:
            cp = json.load(f)
            paths = cp.get("career_paths", {})
            transitions = cp.get("role_transitions", {})
    return reqs, paths, transitions


def recommend_career_paths(current_skills: List[str], current_role: str = "Backend Developer") -> Dict[str, Any]:
    """
    Computes recommendations for career transitions based on skill overlap and Jaccard similarity.
    Provides explainability (matched vs missing skills, match percentage, and reason).
    """
    norm_skills = normalize_skills(current_skills)
    user_skill_set = {s.lower() for s in norm_skills}

    reqs, paths, transitions = load_data()
    role_list = list(reqs.keys()) if reqs else [
        "Software Engineer", "Data Scientist", "Machine Learning Engineer", "DevOps Engineer",
        "Cloud Solutions Architect", "Database Administrator", "Frontend Developer", "Backend Developer",
        "Mobile App Developer", "Full Stack Developer", "QA/Test Automation Engineer", "Data Engineer",
        "Site Reliability Engineer", "Cybersecurity Analyst", "UI/UX Designer", "Network Engineer",
        "Business/Systems Analyst", "AI/NLP Engineer", "Blockchain Developer", "Embedded Systems Engineer"
    ]

    recommendations = []

    for target_role in role_list:
        if target_role == current_role:
            continue

        target_info = reqs.get(target_role, {})
        req_skills = target_info.get("required", [])
        opt_skills = target_info.get("optional", [])
        all_req = req_skills + opt_skills
        if not all_req:
            continue

        norm_target_req = normalize_skills(req_skills)
        norm_target_all = normalize_skills(all_req)

        target_set = {s.lower() for s in norm_target_req}

        matched = [s for s in norm_target_req if s.lower() in user_skill_set]
        missing = [s for s in norm_target_req if s.lower() not in user_skill_set]

        j_sim = jaccard_similarity(norm_skills, norm_target_req)
        match_percentage = round((len(matched) / max(len(norm_target_req), 1)) * 100.0, 1)

        if match_percentage >= 30.0:
            recommendations.append({
                "role": target_role,
                "match_percentage": match_percentage,
                "jaccard_similarity": j_sim,
                "matched_skills": matched,
                "missing_skills": missing,
                "reason": f"Candidate has {len(matched)} matching skills ({', '.join(matched[:3])}) and needs {len(missing)} missing skills ({', '.join(missing[:3])})."
            })

    # Sort by match_percentage descending, then jaccard_similarity descending
    recommendations.sort(key=lambda x: (x["match_percentage"], x["jaccard_similarity"]), reverse=True)

    vertical_progression = paths.get(current_role, ["Junior", "Mid-Level", "Senior", "Lead", "Principal"])

    return {
        "current_role": current_role,
        "recommendations": recommendations[:5],
        "vertical_progression": vertical_progression
    }
