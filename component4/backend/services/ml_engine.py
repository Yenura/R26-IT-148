"""
Component 4 — ML Inference Engine (10K Dataset)
Loads trained artefacts at startup and exposes run_skill_gap_analysis().
"""

import os
import json
import logging
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

# ── Scoring weight constants (avoids magic numbers) ────────────────────────────
REQ_WEIGHT          = 0.70   # required-skills portion of gap score
OPT_WEIGHT          = 0.30   # optional-skills portion of gap score
SKILL_GAP_WEIGHT    = 0.80   # skill score vs experience score blend
EXP_WEIGHT          = 0.20
ML_WEIGHT           = 0.60   # ML probability vs external scores blend
EXT_SCORE_WEIGHT    = 0.40

GAP_LOW_THRESHOLD    = 0.80
GAP_MEDIUM_THRESHOLD = 0.55

LOW_INTERVIEW_THRESHOLD = 60
LOW_SCORE_THRESHOLD     = 60

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE   = os.path.dirname(os.path.abspath(__file__))
MODELS  = os.path.join(_HERE, "..", "..", "models")


# ── Safe artifact loader ───────────────────────────────────────────────────────
def _load_artifact(filename: str, required: bool = True):
    """Load a joblib artifact from the models directory with clear error reporting."""
    path = os.path.join(MODELS, filename)
    if not os.path.exists(path):
        if required:
            logger.critical("[STARTUP] Missing model artifact: %s", path)
            raise FileNotFoundError(
                f"Required model artifact not found: {path}\n"
                f"Run: python component4/ml/train_model.py to regenerate."
            )
        logger.warning("[STARTUP] Optional model artifact missing: %s — using fallback", path)
        return None
    artifact = joblib.load(path)
    logger.info("Loaded artifact: %s", filename)
    return artifact


def _load_json(filename: str, required: bool = True) -> dict:
    """Load a JSON knowledge file from the models directory."""
    path = os.path.join(MODELS, filename)
    if not os.path.exists(path):
        if required:
            logger.critical("[STARTUP] Missing knowledge file: %s", path)
            raise FileNotFoundError(f"Required knowledge file not found: {path}")
        logger.warning("[STARTUP] Optional knowledge file missing: %s — using empty", path)
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Load ML artefacts ──────────────────────────────────────────────────────────
_clf       = _load_artifact("skill_gap_classifier.pkl", required=False)
_feat_cols = _load_artifact("feature_columns.pkl", required=False)
_role_cols = _load_artifact("role_columns.pkl", required=False)
ALL_SKILLS = _load_artifact("all_skills.pkl", required=False) or []

# ── Load knowledge files ───────────────────────────────────────────────────────
JOB_REQ   = _load_json("job_requirements.json", required=False)
RESOURCES = _load_json("learning_resources.json", required=False)
SKILL_CAT = _load_json("skill_categories.json", required=False)
_CP_DATA  = _load_json("career_paths.json", required=False)

CAREER_PATHS     = _CP_DATA.get("career_paths", {})
ROLE_TRANSITIONS = _CP_DATA.get("role_transitions", {})

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

    # Fuzzy match — exact match or substring with minimum length guard
    # Also decompose compound skills like "Swift/Kotlin or Flutter"
    import re as _re
    def fuzzy_has(skill, cand_set):
        # First try decomposing compound skills
        parts = _re.split(r'[/|,]|\s+or\s+', skill)
        parts = [p.strip() for p in parts if p.strip()]
        for part in parts:
            pl = part.lower()
            for c in cand_set:
                if pl == c:
                    return True
                if len(pl) >= 3 and len(c) >= 3 and (pl in c or c in pl):
                    return True
        # Also try the full skill string
        sl = skill.lower()
        for c in cand_set:
            if sl == c:
                return True
            if len(sl) >= 3 and len(c) >= 3 and (sl in c or c in sl):
                return True
        return False

    miss_req = [s for s in required if not fuzzy_has(s, candidate_lower)]
    miss_opt = [s for s in optional if not fuzzy_has(s, candidate_lower)]

    match_pct = ((len(required) - len(miss_req)) / max(len(required), 1)) * 100

    req_score = (len(required) - len(miss_req)) / max(len(required), 1)
    opt_score = (len(optional) - len(miss_opt)) / max(len(optional), 1) if optional else 1.0
    gap_score = REQ_WEIGHT * req_score + OPT_WEIGHT * opt_score

    # Blend in experience score
    min_exp   = req.get("min_experience", 2)
    exp_score = min(experience_years / max(min_exp, 1), 1.0)
    gap_score = SKILL_GAP_WEIGHT * gap_score + EXP_WEIGHT * exp_score

    return gap_score, miss_req, miss_opt, match_pct


def gap_severity(score: float) -> str:
    """Map a 0-1 gap score to a human-readable severity label."""
    if score >= GAP_LOW_THRESHOLD:    return "Low"
    if score >= GAP_MEDIUM_THRESHOLD: return "Medium"
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

    # One-hot role (skip if role columns not loaded)
    if _role_cols:
        for col in _role_cols:
            role_label = col.replace("role_", "").replace("_", " ")
            row[col] = int(job_role.replace(" ", "_").replace("/", "_") == col.replace("role_", ""))

    # Skill flags — match against ALL_SKILLS canonical list efficiently
    cand_skills_lower = [s.lower() for s in skills]
    cand_text = " | ".join(cand_skills_lower)
    cand_set = set(cand_skills_lower)
    for skill in ALL_SKILLS:
        col = _col_key(skill)
        sl = skill.lower()
        row[col] = int(sl in cand_set or sl in cand_text or any(sl in s for s in cand_skills_lower))

    df = pd.DataFrame([row])
    if _feat_cols:
        for c in _feat_cols:
            if c not in df.columns:
                df[c] = 0
        return df[_feat_cols]
    return df


# ── Main inference ────────────────────────────────────────────────────────────
def run_skill_gap_analysis(
    candidate_id:      str,
    candidate_name:    str,
    job_role:          str,
    skills:            List[str],
    experience_years:  int = 0,
    education:         str = "B.Sc. Computer Science",
    certifications:    str = "None",
    cert_count:        int = 0,
    projects_count:    int = 0,
    job_level:         str = "Mid-Level",
    work_mode:         str = "Hybrid",
    cv_matching_score: Optional[float] = None,
    interview_score:   Optional[float] = None,
    mcq_score:         Optional[float] = None,
    descriptive_score: Optional[float] = None,
    coding_score:      Optional[float] = None,
    weak_topics:       Optional[List[str]] = None,
    failed_mcq_topics: Optional[List[str]] = None,
) -> Dict[str, Any]:
    weak_topics = weak_topics or []
    failed_mcq_topics = failed_mcq_topics or []

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
    if _clf is not None:
        hire_prob = float(_clf.predict_proba(fv)[0][1])
    else:
        # Fallback: use skill match percentage as rough proxy
        hire_prob = min(1.0, skill_match_pct / 100 * 0.8 + 0.1)
    predicted = hire_prob >= 0.5

    # Blend ML probability with external CV/interview scores if available
    score_inputs = [x for x in [cv_matching_score, interview_score] if x is not None]
    if score_inputs:
        avg_score_norm = sum(score_inputs) / (len(score_inputs) * 100)
        hire_prob = ML_WEIGHT * hire_prob + EXT_SCORE_WEIGHT * avg_score_norm

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

    if interview_score is not None and interview_score < LOW_INTERVIEW_THRESHOLD:
        knowledge_gaps = weak_topics if weak_topics else [
            f"Core {job_role} Concepts", "Theoretical Foundations"
        ]

    if descriptive_score is not None and descriptive_score < LOW_SCORE_THRESHOLD:
        knowledge_gaps = list(set(knowledge_gaps + weak_topics))

    if coding_score is not None and coding_score < LOW_SCORE_THRESHOLD:
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
        "experience_years":        experience_years,
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
        "analysis_timestamp":      datetime.now(timezone.utc).isoformat(),
        "certifications_count":    cert_count,
        "projects_count":          projects_count,
    }
