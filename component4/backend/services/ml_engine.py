"""
ML inference engine for Component 4.
Loads trained models + knowledge files at startup.
"""

import os, json, joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE    = os.path.dirname(os.path.abspath(__file__))
MODELS   = os.path.join(_HERE, "..", "..", "models")
REPORTS  = os.path.join(_HERE, "..", "..", "reports")

# ── Load artefacts ─────────────────────────────────────────────────────────────
_clf          = joblib.load(os.path.join(MODELS, "skill_gap_classifier.pkl"))
_feat_cols    = joblib.load(os.path.join(MODELS, "feature_columns.pkl"))
_role_cols    = joblib.load(os.path.join(MODELS, "role_columns.pkl"))

with open(os.path.join(MODELS, "job_requirements.json"))  as f: JOB_REQ   = json.load(f)
with open(os.path.join(MODELS, "learning_resources.json")) as f: RESOURCES = json.load(f)
with open(os.path.join(MODELS, "skill_categories.json"))   as f: SKILL_CAT = json.load(f)

# Canonical skill list (must match training order)
ALL_SKILLS = [
    "Python", "Java", "C++", "SQL", "React", "Linux",
    "TensorFlow", "Pytorch", "Machine Learning", "Deep Learning", "NLP",
    "Cybersecurity", "Networking", "Ethical Hacking"
]

EDU_MAP = {"PhD": 5, "M.Tech": 4, "MBA": 3, "B.Tech": 2, "B.Sc": 1}

CAREER_PATHS: Dict[str, List[str]] = {
    "Data Scientist":       ["Junior Data Scientist", "Data Scientist",
                             "Senior Data Scientist", "Lead Data Scientist", "Chief Data Officer"],
    "AI Researcher":        ["ML Engineer", "AI Researcher",
                             "Senior AI Researcher", "Research Scientist", "AI Director"],
    "Software Engineer":    ["Junior Developer", "Software Engineer",
                             "Senior Engineer", "Tech Lead", "Engineering Manager"],
    "Cybersecurity Analyst":["Security Analyst (L1)", "Cybersecurity Analyst",
                             "Senior Security Analyst", "Security Architect", "CISO"],
}

ROLE_TRANSITIONS: Dict[str, List[str]] = {
    "Data Scientist":       ["AI Researcher", "ML Engineer", "Data Engineer"],
    "AI Researcher":        ["Data Scientist", "Research Engineer"],
    "Software Engineer":    ["Data Scientist", "DevOps Engineer", "Full-Stack Developer"],
    "Cybersecurity Analyst":["Security Engineer", "Penetration Tester"],
}


# ── Helper: compute skill gap ──────────────────────────────────────────────────

def _parse_skills(skills: List[str]) -> set:
    return {s.strip() for s in skills}


def compute_gap(
    skills: List[str],
    job_role: str,
    experience_years: int,
) -> Tuple[float, List[str], List[str], float]:
    """
    Returns (gap_score 0-1, missing_required, missing_optional, skill_match_pct)
    Higher gap_score = better fit.
    """
    candidate = {s.lower() for s in skills}

    if job_role not in JOB_REQ:
        return 0.5, [], [], 50.0

    req      = JOB_REQ[job_role]
    required = [s.lower() for s in req["required"]]
    optional = [s.lower() for s in req["optional"]]

    miss_req = [s for s in required if s not in candidate]
    miss_opt = [s for s in optional if s not in candidate]

    match_pct = ((len(required) - len(miss_req)) / max(len(required), 1)) * 100

    req_score = (len(required) - len(miss_req)) / max(len(required), 1)
    opt_score = (len(optional) - len(miss_opt)) / max(len(optional), 1)
    gap_score = 0.7 * req_score + 0.3 * opt_score

    exp_ok    = experience_years >= req.get("min_experience", 1)
    gap_score = 0.8 * gap_score + 0.2 * float(exp_ok)

    # Re-capitalise missing lists for display
    miss_req_display = [s.title() for s in miss_req]
    miss_opt_display = [s.title() for s in miss_opt]

    return gap_score, miss_req_display, miss_opt_display, match_pct


def gap_severity(score: float) -> str:
    if score >= 0.85: return "Low"
    if score >= 0.60: return "Medium"
    return "High"


# ── Build feature vector ───────────────────────────────────────────────────────

def build_feature_vector(
    skills: List[str],
    job_role: str,
    experience_years: int,
    education: str,
    certifications: str,
    ai_score_norm: float,
    gap_score: float,
    skill_match_pct: float,
) -> pd.DataFrame:

    row: Dict[str, Any] = {
        "Experience (Years)": experience_years,
        "Education_Enc":      EDU_MAP.get(education, 2),
        "Has_Cert":           int(certifications != "None"),
        "Skill_Count":        len(skills),
        "AI_Score_Norm":      ai_score_norm,
        "Gap_Score":          gap_score,
        "Skill_Match_Pct":    skill_match_pct,
    }

    # One-hot role
    for col in _role_cols:
        role_label = col.replace("role_", "")
        row[col] = int(job_role == role_label)

    # Skill flags
    candidate_lower = {s.lower() for s in skills}
    for skill in ALL_SKILLS:
        col = f"skill_{skill.lower().replace(' ', '_').replace('+', 'plus')}"
        row[col] = int(skill.lower() in candidate_lower)

    df = pd.DataFrame([row])
    # Align to training columns
    for c in _feat_cols:
        if c not in df.columns:
            df[c] = 0
    return df[_feat_cols]


# ── Main inference function ────────────────────────────────────────────────────

def run_skill_gap_analysis(
    candidate_id: str,
    candidate_name: str,
    job_role: str,
    skills: List[str],
    experience_years: int,
    education: str,
    certifications: str,
    cv_matching_score: float | None,
    interview_score:   float | None,
    mcq_score:         float | None,
    descriptive_score: float | None,
    coding_score:      float | None,
    weak_topics:       List[str],
    failed_mcq_topics: List[str],
) -> Dict[str, Any]:

    # ── 1. Gap computation ────────────────────────────────────────────────────
    gap_score, miss_req, miss_opt, skill_match_pct = compute_gap(
        skills, job_role, experience_years
    )
    severity = gap_severity(gap_score)

    # Derive an AI score proxy from cv + interview scores if available
    ai_proxy = 0.5
    if cv_matching_score is not None and interview_score is not None:
        ai_proxy = (cv_matching_score * 0.5 + interview_score * 0.5) / 100.0
    elif cv_matching_score is not None:
        ai_proxy = cv_matching_score / 100.0
    elif interview_score is not None:
        ai_proxy = interview_score / 100.0

    # ── 2. ML prediction ─────────────────────────────────────────────────────
    fv          = build_feature_vector(
        skills, job_role, experience_years, education,
        certifications, ai_proxy, gap_score, skill_match_pct
    )
    hire_prob   = float(_clf.predict_proba(fv)[0][1])
    predicted   = hire_prob >= 0.5

    # ── 3. Categorise missing skills ─────────────────────────────────────────
    all_missing = set(m.lower() for m in miss_req + miss_opt)
    tech_gaps, ml_gaps, sec_gaps = [], [], []

    for skill in ALL_SKILLS:
        sl = skill.lower()
        if sl in all_missing:
            if skill in SKILL_CAT["Technical"]:
                tech_gaps.append(skill)
            elif skill in SKILL_CAT["ML/AI"]:
                ml_gaps.append(skill)
            elif skill in SKILL_CAT["Security"]:
                sec_gaps.append(skill)

    # ── 4. Interview-driven knowledge / problem-solving gaps ─────────────────
    knowledge_gaps, problem_solving_gaps = [], []

    if interview_score is not None and interview_score < 60:
        knowledge_gaps = weak_topics if weak_topics else [
            f"Core {job_role} Concepts",
            "Theoretical Foundations",
        ]

    if descriptive_score is not None and descriptive_score < 60:
        knowledge_gaps = list(set(knowledge_gaps + weak_topics))

    if coding_score is not None and coding_score < 60:
        problem_solving_gaps = [
            "Algorithm Design", "Data Structures", "Code Optimisation"
        ]

    # MCQ-specific gaps from failed topics
    if failed_mcq_topics:
        knowledge_gaps = list(set(knowledge_gaps + failed_mcq_topics))

    # ── 5. Resource recommendations ──────────────────────────────────────────
    priority_skills = []
    for s in miss_req:       priority_skills.append((s, "Critical"))
    for s in tech_gaps:      priority_skills.append((s, "High"))
    for s in ml_gaps:        priority_skills.append((s, "High"))
    for s in sec_gaps:       priority_skills.append((s, "High"))
    for s in miss_opt:       priority_skills.append((s, "Medium"))

    seen = set()
    resources = []
    for skill, priority in priority_skills:
        if skill in seen: continue
        seen.add(skill)
        res = RESOURCES.get(skill, {
            "course": f"{skill} Fundamentals",
            "url":    "https://coursera.org",
            "duration": "4 weeks",
            "level": "Beginner",
        })
        resources.append({
            "skill": skill, "priority": priority,
            "course": res["course"], "url": res["url"],
            "duration": res["duration"], "level": res["level"],
        })

    # ── 6. Learning plan (monthly phases) ────────────────────────────────────
    phases, month = [], 1
    for chunk_start in range(0, len(resources), 2):
        chunk = resources[chunk_start: chunk_start + 2]
        phases.append({
            "phase": month,
            "title": f"Month {month}",
            "skills": [r["skill"] for r in chunk],
            "resources": chunk,
        })
        month += 1
    if not phases:
        phases = [{"phase": 1, "title": "Month 1",
                   "skills": ["Keep practising current skills"],
                   "resources": []}]

    # ── 7. Career path suggestions ────────────────────────────────────────────
    path = CAREER_PATHS.get(job_role, ["Junior", "Mid-level", "Senior", "Lead"])
    transitions = ROLE_TRANSITIONS.get(job_role, [])
    career_suggestions = [
        f"Follow the {job_role} growth track: {' -> '.join(path)}",
    ]
    if transitions:
        career_suggestions.append(
            f"Potential lateral moves: {', '.join(transitions)}"
        )
    if severity == "High":
        career_suggestions.append(
            "Focus on closing critical skill gaps before aiming for senior roles."
        )

    # ── 8. Improvement suggestions ────────────────────────────────────────────
    suggestions = []
    if miss_req:
        suggestions.append(
            f"Urgently learn required skills: {', '.join(miss_req[:3])}."
        )
    if interview_score is not None and interview_score < 70:
        suggestions.append(
            "Revise theoretical concepts — your interview score indicates knowledge gaps."
        )
    if coding_score is not None and coding_score < 60:
        suggestions.append(
            "Practice LeetCode / HackerRank daily to improve problem-solving ability."
        )
    if mcq_score is not None and mcq_score < 60:
        suggestions.append(
            f"Review these topics from MCQ failures: {', '.join(failed_mcq_topics[:3]) if failed_mcq_topics else 'core domain concepts'}."
        )
    if not certifications or certifications == "None":
        suggestions.append(
            "Consider earning an industry certification to strengthen your profile."
        )
    if experience_years < JOB_REQ.get(job_role, {}).get("min_experience", 1):
        suggestions.append(
            f"Gain more hands-on experience; at least "
            f"{JOB_REQ[job_role]['min_experience']} year(s) preferred for {job_role}."
        )

    # ── 9. Roadmap graph nodes ────────────────────────────────────────────────
    candidate_set = {s.lower() for s in skills}
    nodes = []
    for skill in ALL_SKILLS:
        sl = skill.lower()
        if sl in candidate_set:
            status = "has"
        elif sl in {m.lower() for m in miss_req}:
            status = "missing_required"
        else:
            status = "missing_optional"

        cat = "Other"
        for c_name, c_skills in SKILL_CAT.items():
            if skill in c_skills:
                cat = c_name
                break

        nodes.append({"id": skill, "label": skill,
                      "status": status, "category": cat})

    return {
        "candidate_id":           candidate_id,
        "candidate_name":         candidate_name,
        "job_role":               job_role,
        "cv_matching_score":      cv_matching_score,
        "interview_score":        interview_score,
        "skill_match_pct":        round(skill_match_pct, 2),
        "gap_score":              round(gap_score, 4),
        "gap_severity":           severity,
        "missing_required":       miss_req,
        "missing_optional":       miss_opt,
        "present_skills":         list(skills),
        "technical_gaps":         tech_gaps,
        "ml_ai_gaps":             ml_gaps,
        "security_gaps":          sec_gaps,
        "knowledge_gaps":         knowledge_gaps,
        "problem_solving_gaps":   problem_solving_gaps,
        "resources":              resources,
        "roadmap_nodes":          nodes,
        "learning_plan":          phases,
        "career_path_suggestions": career_suggestions,
        "improvement_suggestions": suggestions,
        "predicted_hire":         predicted,
        "hire_probability":       round(hire_prob * 100, 2),
        "analysis_timestamp":     datetime.utcnow().isoformat(),
    }
