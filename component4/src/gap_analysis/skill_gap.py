"""
Skill Gap Analysis Module — Component 4
Computes:
  - matched_skills
  - missing_skills (with priority and priority_score)
  - skill_coverage (0.0 – 1.0)
  - skill_coverage_percentage (0 – 100%)
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from src.preprocessing.skill_normalizer import normalize_skill, normalize_skills
from src.gap_analysis.priority import compute_priority_score

ROOT_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = ROOT_DIR / "models"
JOB_REQ_FILE = MODELS_DIR / "job_requirements.json"


def load_job_requirements() -> dict:
    if JOB_REQ_FILE.exists():
        with open(JOB_REQ_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def analyze_skill_gap(current_skills: List[str], target_role: str) -> Dict[str, Any]:
    """
    Main Skill Gap Engine function.
    Given current_skills and target_role:
      - Normalizes skills
      - Fetches required skills for target_role
      - Performs set difference for missing skills
      - Computes skill_coverage (0.0 - 1.0) and skill_coverage_percentage
      - Computes explainable priority_score for each missing skill
    """
    norm_curr = normalize_skills(current_skills)
    curr_set = {s.lower() for s in norm_curr}

    job_reqs = load_job_requirements()
    role_info = job_reqs.get(target_role, {})

    raw_req_skills = role_info.get("required", [])
    raw_opt_skills = role_info.get("optional", [])

    if not raw_req_skills and not raw_opt_skills:
        # Fallback default required skills for unknown roles
        raw_req_skills = ["Python", "SQL", "Git"]

    norm_req_skills = normalize_skills(raw_req_skills)
    norm_opt_skills = normalize_skills(raw_opt_skills)

    all_target_skills = norm_req_skills + [s for s in norm_opt_skills if s.lower() not in {r.lower() for r in norm_req_skills}]

    matched_skills = []
    missing_skills_info = []

    for s in norm_req_skills:
        if s.lower() in curr_set:
            matched_skills.append(s)
        else:
            p_score, p_cat = compute_priority_score(s, importance_level="high", market_freq_pct=85.0, dependency_score_pct=80.0)
            missing_skills_info.append({
                "skill": s,
                "priority": p_cat,
                "priority_score": p_score,
                "importance": "Required"
            })

    for s in norm_opt_skills:
        if s.lower() in curr_set:
            if s.lower() not in {m.lower() for m in matched_skills}:
                matched_skills.append(s)
        else:
            if s.lower() not in {m["skill"].lower() for m in missing_skills_info}:
                p_score, p_cat = compute_priority_score(s, importance_level="medium", market_freq_pct=50.0, dependency_score_pct=40.0)
                missing_skills_info.append({
                    "skill": s,
                    "priority": p_cat,
                    "priority_score": p_score,
                    "importance": "Optional"
                })

    # Sort missing skills by priority_score descending
    missing_skills_info.sort(key=lambda x: x["priority_score"], reverse=True)

    total_req_count = max(len(norm_req_skills), 1)
    matched_req_count = len([s for s in matched_skills if s.lower() in {r.lower() for r in norm_req_skills}])

    skill_coverage = round(matched_req_count / total_req_count, 4)
    skill_coverage_percentage = round(skill_coverage * 100.0, 2)

    return {
        "target_role": target_role,
        "skill_coverage": skill_coverage,
        "skill_coverage_percentage": skill_coverage_percentage,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills_info,
        "missing_skill_names": [m["skill"] for m in missing_skills_info]
    }
