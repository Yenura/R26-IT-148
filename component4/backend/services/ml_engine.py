"""
Component 4 — ML Inference Engine (New 10K Dataset)
Loads trained artefacts at startup and exposes run_skill_gap_analysis().
"""

import os, json, joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE   = os.path.dirname(os.path.abspath(__file__))
MODELS  = os.path.join(_HERE, "..", "..", "models")
REPORTS = os.path.join(_HERE, "..", "..", "reports")

# ── Load ML artefacts ──────────────────────────────────────────────────────────
_clf       = joblib.load(os.path.join(MODELS, "skill_gap_classifier.pkl"))
_feat_cols = joblib.load(os.path.join(MODELS, "feature_columns.pkl"))
_role_cols = joblib.load(os.path.join(MODELS, "role_columns.pkl"))
ALL_SKILLS = joblib.load(os.path.join(MODELS, "all_skills.pkl"))

# ── Load knowledge files ───────────────────────────────────────────────────────
with open(os.path.join(MODELS, "job_requirements.json"))  as f: JOB_REQ   = json.load(f)
with open(os.path.join(MODELS, "learning_resources.json")) as f: RESOURCES = json.load(f)
with open(os.path.join(MODELS, "skill_categories.json"))   as f: SKILL_CAT = json.load(f)
with open(os.path.join(MODELS, "career_paths.json"))       as f: _CP_DATA  = json.load(f)

CAREER_PATHS     = _CP_DATA["career_paths"]
ROLE_TRANSITIONS = _CP_DATA["role_transitions"]

# ── Education ordinal map ──────────────────────────────────────────────────────
EDU_RANK = {
    "Bootcamp + Self-Taught":                1,
    "Associate Degree in Computer Science":  2,
    "B.Sc. Computer Science":               3,
    "B.Sc. Information Technology":         3,
    "B.Sc. Software Engineering":           3,
    "B.Sc. Mathematics":                    3,
    "B.Sc. Statistics":                     3,
    "B.Sc. Cognitive Science":              3,
    "B.Sc. Physics (CS minor)":             3,
    "B.Eng. Electrical Engineering":        3,
    "B.Eng. Electronics & Communication":   3,
    "MBA (IT / Analytics)":                 4,
    "M.Sc. Computer Science":               5,
    "M.Sc. Data Science":                   5,
    "M.Sc. Machine Learning":               5,
    "M.Sc. Cybersecurity":                  5,
    "M.Sc. Artificial Intelligence":        5,
    "M.Sc. Information Systems":            5,
    "Ph.D. Computer Science":               6,
    "Ph.D. Artificial Intelligence":        6,
    # Legacy / simplified keys (from old form inputs)
    "PhD":      6,
    "M.Tech":   5,
    "MBA":      4,
    "B.Tech":   3,
    "B.Sc":     3,
}

LEVEL_RANK    = {"Junior": 1, "Mid-Level": 2, "Senior": 3, "Lead": 4, "Principal / Staff": 5}
WORKMODE_RANK = {"On-Site": 1, "Hybrid": 2, "Remote": 3}


# ── Helper: normalise skill string ────────────────────────────────────────────
def _col_key(skill: str) -> str:
    return f"skill_{skill.lower().replace(' ', '_').replace('/', '_').replace('+', 'plus').replace('-', '_')}"


# ── Compute skill gap ─────────────────────────────────────────────────────────
def compute_gap(
    skills: List[str],
    job_role: str,
    experience_years: int,
) -> Tuple[float, List[str], List[str], float]:
    """
    Returns (gap_score 0-1, missing_required, missing_optional, skill_match_pct)
    gap_score closer to 1 = better fit.
    """
    candidate_lower = {s.strip().lower() for s in skills}

    if job_role not in JOB_REQ:
        return 0.5, [], [], 50.0

    req      = JOB_REQ[job_role]
    required = [s.strip() for s in req["required"]]
    optional = [s.strip() for s in req.get("optional", [])]

    # Fuzzy match — if any candidate skill is a substring of a required skill or vice-versa
    def fuzzy_has(skill, cand_set):
        sl = skill.lower()
        return any(sl in c or c in sl for c in cand_set)

    miss_req = [s for s in required if not fuzzy_has(s, candidate_lower)]
    miss_opt = [s for s in optional if not fuzzy_has(s, candidate_lower)]

    match_pct = ((len(required) - len(miss_req)) / max(len(required), 1)) * 100

    req_score = (len(required) - len(miss_req)) / max(len(required), 1)
    opt_score = (len(optional) - len(miss_opt)) / max(len(optional), 1) if optional else 1.0
    gap_score = 0.7 * req_score + 0.3 * opt_score

    # Bonus for experience
    min_exp   = req.get("min_experience", 2)
    exp_score = min(experience_years / max(min_exp, 1), 1.0)
    gap_score = 0.8 * gap_score + 0.2 * exp_score

    return gap_score, miss_req, miss_opt, match_pct


def gap_severity(score: float) -> str:
    if score >= 0.80: return "Low"
    if score >= 0.55: return "Medium"
    return "High"


# ── Build feature vector ──────────────────────────────────────────────────────
def build_feature_vector(
    skills: List[str],
    job_role: str,
    experience_years: int,
    education: str,
    job_level: str,
    work_mode: str,
    cert_count: int,
    projects_count: int,
) -> pd.DataFrame:

    row: Dict[str, Any] = {
        "Experience (Years)": experience_years,
        "Education_Enc":      EDU_RANK.get(education, 3),
        "JobLevel_Enc":       LEVEL_RANK.get(job_level, 2),
        "WorkMode_Enc":       WORKMODE_RANK.get(work_mode, 2),
        "Has_Cert":           int(cert_count > 0),
        "Cert_Count":         cert_count,
        "Projects Count":     projects_count,
    }

    # One-hot role
    for col in _role_cols:
        role_label = col.replace("role_", "").replace("_", " ")
        row[col] = int(job_role.replace(" ", "_").replace("/", "_") == col.replace("role_", ""))

    # Skill flags — match against ALL_SKILLS canonical list
    candidate_text = " | ".join(skills).lower()
    for skill in ALL_SKILLS:
        col = _col_key(skill)
        row[col] = int(skill.lower() in candidate_text or any(skill.lower() in s.lower() for s in skills))

    df = pd.DataFrame([row])
    for c in _feat_cols:
        if c not in df.columns:
            df[c] = 0
    return df[_feat_cols]


# ── Main inference ────────────────────────────────────────────────────────────
def run_skill_gap_analysis(
    candidate_id:      str,
    candidate_name:    str,
    job_role:          str,
    skills:            List[str],
    experience_years:  int,
    education:         str,
    certifications:    str,
    cert_count:        int,
    projects_count:    int,
    job_level:         str,
    work_mode:         str,
    cv_matching_score: float | None,
    interview_score:   float | None,
    mcq_score:         float | None,
    descriptive_score: float | None,
    coding_score:      float | None,
    weak_topics:       List[str],
    failed_mcq_topics: List[str],
) -> Dict[str, Any]:

    # ── 1. Skill gap computation ──────────────────────────────────────────────
    gap_score, miss_req, miss_opt, skill_match_pct = compute_gap(
        skills, job_role, experience_years
    )
    severity = gap_severity(gap_score)

    # ── 2. ML hire probability prediction ────────────────────────────────────
    fv = build_feature_vector(
        skills, job_role, experience_years, education,
        job_level, work_mode, cert_count, projects_count,
    )
    hire_prob = float(_clf.predict_proba(fv)[0][1])
    predicted = hire_prob >= 0.5

    # Blend with cv/interview score if available
    score_inputs = [x for x in [cv_matching_score, interview_score] if x is not None]
    if score_inputs:
        avg_score_norm = sum(score_inputs) / (len(score_inputs) * 100)
        hire_prob = 0.6 * hire_prob + 0.4 * avg_score_norm

    hire_prob = max(0.0, min(1.0, hire_prob))

    # ── 3. Categorise missing skills ─────────────────────────────────────────
    all_missing_lower = {m.lower() for m in miss_req + miss_opt}
    categorised: Dict[str, List[str]] = {cat: [] for cat in SKILL_CAT}

    for skill, cat_skills in SKILL_CAT.items():
        for s in cat_skills:
            if s.lower() in all_missing_lower:
                categorised[skill].append(s)

    tech_gaps  = categorised.get("Programming", []) + categorised.get("Web", [])
    ml_gaps    = categorised.get("ML/AI", [])
    cloud_gaps = categorised.get("Cloud/DevOps", [])
    sec_gaps   = categorised.get("Security", [])
    data_gaps  = categorised.get("Data/DB", [])

    # ── 4. Interview-driven gaps ──────────────────────────────────────────────
    knowledge_gaps, problem_solving_gaps = [], []

    if interview_score is not None and interview_score < 60:
        knowledge_gaps = weak_topics if weak_topics else [
            f"Core {job_role} Concepts", "Theoretical Foundations"
        ]

    if descriptive_score is not None and descriptive_score < 60:
        knowledge_gaps = list(set(knowledge_gaps + weak_topics))

    if coding_score is not None and coding_score < 60:
        problem_solving_gaps = ["Algorithm Design", "Data Structures", "Code Optimisation"]

    if failed_mcq_topics:
        knowledge_gaps = list(set(knowledge_gaps + failed_mcq_topics))

    # ── 5. Resource recommendations ──────────────────────────────────────────
    priority_skills = []
    for s in miss_req:        priority_skills.append((s, "Critical"))
    for s in ml_gaps:         priority_skills.append((s, "High"))
    for s in cloud_gaps:      priority_skills.append((s, "High"))
    for s in tech_gaps:       priority_skills.append((s, "High"))
    for s in sec_gaps:        priority_skills.append((s, "Medium"))
    for s in data_gaps:       priority_skills.append((s, "Medium"))
    for s in miss_opt:        priority_skills.append((s, "Low"))

    seen = set()
    resources = []
    for skill, priority in priority_skills:
        sk = skill.strip()
        if sk in seen:
            continue
        seen.add(sk)
        # Try exact match, then partial match
        res = RESOURCES.get(sk)
        if not res:
            for rk, rv in RESOURCES.items():
                if rk.lower() in sk.lower() or sk.lower() in rk.lower():
                    res = rv
                    break
        if not res:
            res = {
                "course": f"{sk} Fundamentals",
                "url": "https://www.coursera.org/search?query=" + sk.replace(" ", "+"),
                "duration": "4 weeks",
                "level": "Beginner",
            }
        resources.append({
            "skill": sk, "priority": priority,
            "course": res["course"], "url": res["url"],
            "duration": res["duration"], "level": res["level"],
        })

    # ── 6. Monthly learning plan ──────────────────────────────────────────────
    phases, month = [], 1
    for i in range(0, len(resources), 2):
        chunk = resources[i: i + 2]
        phases.append({
            "phase": month,
            "title": f"Month {month}",
            "skills": [r["skill"] for r in chunk],
            "resources": chunk,
        })
        month += 1
    if not phases:
        phases = [{"phase": 1, "title": "Month 1",
                   "skills": ["Maintain and deepen existing skills"],
                   "resources": []}]

    # ── 7. Career suggestions ─────────────────────────────────────────────────
    path = CAREER_PATHS.get(job_role, ["Junior", "Mid-Level", "Senior", "Lead", "Principal"])
    transitions = ROLE_TRANSITIONS.get(job_role, [])

    career_suggestions = [
        f"Follow the {job_role} growth track: {' → '.join(path[:5])}",
    ]
    if transitions:
        career_suggestions.append(f"Potential lateral moves: {', '.join(transitions)}")
    if severity == "High":
        career_suggestions.append("Focus on closing critical skill gaps before targeting senior roles.")
    if severity == "Low" and experience_years >= 5:
        career_suggestions.append("You are well-positioned — consider pursuing senior/lead certifications.")

    # ── 8. Improvement suggestions ────────────────────────────────────────────
    suggestions = []
    if miss_req:
        suggestions.append(f"Urgently learn required skills: {', '.join(miss_req[:3])}.")
    if interview_score is not None and interview_score < 70:
        suggestions.append("Revise theoretical concepts — your interview score indicates knowledge gaps.")
    if coding_score is not None and coding_score < 60:
        suggestions.append("Practice LeetCode / HackerRank daily to improve problem-solving ability.")
    if mcq_score is not None and mcq_score < 60:
        topics = ', '.join(failed_mcq_topics[:3]) if failed_mcq_topics else "core domain concepts"
        suggestions.append(f"Review MCQ failure topics: {topics}.")
    if cert_count == 0:
        suggestions.append("Earn an industry certification to strengthen your profile.")
    min_exp = JOB_REQ.get(job_role, {}).get("min_experience", 2)
    if experience_years < min_exp:
        suggestions.append(f"Gain more hands-on experience; {min_exp}+ years preferred for {job_role}.")
    if projects_count < 5:
        suggestions.append("Build more portfolio projects to demonstrate practical skills.")

    # ── 9. Roadmap skill nodes ────────────────────────────────────────────────
    candidate_lower = {s.lower() for s in skills}
    req_lower = {m.lower() for m in miss_req}
    nodes = []
    for skill in ALL_SKILLS[:25]:
        sl = skill.lower()
        if any(sl in c or c in sl for c in candidate_lower):
            status = "has"
        elif sl in req_lower or any(sl in r or r in sl for r in req_lower):
            status = "missing_required"
        else:
            status = "missing_optional"

        cat = "Other"
        for c_name, c_skills in SKILL_CAT.items():
            if any(skill.lower() in cs.lower() or cs.lower() in skill.lower() for cs in c_skills):
                cat = c_name
                break

        nodes.append({"id": skill, "label": skill, "status": status, "category": cat})

    return {
        "candidate_id":            candidate_id,
        "candidate_name":          candidate_name,
        "job_role":                job_role,
        "job_level":               job_level,
        "work_mode":               work_mode,
        "cv_matching_score":       cv_matching_score,
        "interview_score":         interview_score,
        "skill_match_pct":         round(skill_match_pct, 2),
        "gap_score":               round(gap_score, 4),
        "gap_severity":            severity,
        "missing_required":        miss_req,
        "missing_optional":        miss_opt,
        "present_skills":          list(skills),
        "technical_gaps":          tech_gaps,
        "ml_ai_gaps":              ml_gaps,
        "cloud_devops_gaps":       cloud_gaps,
        "security_gaps":           sec_gaps,
        "data_gaps":               data_gaps,
        "knowledge_gaps":          knowledge_gaps,
        "problem_solving_gaps":    problem_solving_gaps,
        "resources":               resources,
        "roadmap_nodes":           nodes,
        "learning_plan":           phases,
        "career_path_suggestions": career_suggestions,
        "improvement_suggestions": suggestions,
        "predicted_hire":          predicted,
        "hire_probability":        round(hire_prob * 100, 2),
        "analysis_timestamp":      datetime.utcnow().isoformat(),
        "certifications_count":    cert_count,
        "projects_count":          projects_count,
    }
