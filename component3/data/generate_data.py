"""
Synthetic Dataset Generator & Dataset Ingestion - Component 3
IT22027610 | Perera K.G.S.N | R26-IT-148

Generates and standardizes realistic data for all 20 IT job roles.
Integrates user-provided Excel datasets with full normalization.

Total: 600 candidates per role × 20 roles = 12,000 records
Split: Train (7,200) / Val (1,800) / Test (3,000) / Fairness (10,000)
"""

import numpy as np
import pandas as pd
import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.role_configs import (
    ROLES, ROLE_DISPLAY_NAMES, ROLE_EDU_DISTRIBUTION,
    ROLE_EXP_DISTRIBUTION, ROLE_REQUIREMENTS, REQUIRED_YEARS,
    ROLE_CV_WEIGHTS, ROLE_INTERVIEW_WEIGHTS, ROLE_RELEVANCE_THRESHOLDS,
    EDU_LEVEL_SCORES, EDU_LEVEL_NAMES
)

np.random.seed(42)
random.seed(42)

RECORDS_PER_ROLE = 600   # 600 × 20 = 12,000 total

EXCEL_ROLE_MAPPING = {
    "AI_NLP_Engineer": "AI_NLP_Engineer.xlsx",
    "Blockchain_Developer": "Blockchain_Developer.xlsx",
    "Business_Systems_Analyst": "Business_Systems_Analyst.xlsx",
    "Cybersecurity_Analyst": "Cybersecurity_Analyst.xlsx",
    "Data_Engineer": "Data_Engineer.xlsx",
    "Embedded_Systems_Engineer": "Embedded_Systems_Engineer.xlsx",
    "Network_Engineer": "Network_Engineer.xlsx",
    "QA_Test_Automation_Engineer": "QA_Test_Automation_Engineer (2).xlsx",
    "Site_Reliability_Engineer": "Site_Reliability_Engineer.xlsx",
    "UI_UX_Designer": "UI_UX_Designer.xlsx",
}

ROLE_PREFIX_MAP = {
    "Software_Engineer":         "SE",
    "Data_Scientist":            "DS",
    "Machine_Learning_Engineer": "ML",
    "DevOps_Engineer":           "DO",
    "Cybersecurity_Analyst":     "CA",
    "Cloud_Solutions_Architect": "CS",
    "Database_Administrator":    "DB",
    "Frontend_Developer":        "FE",
    "Backend_Developer":         "BE",
    "Mobile_App_Developer":      "MA",
    "Full_Stack_Developer":      "FS",
    "QA_Test_Automation_Engineer": "QA",
    "Data_Engineer":             "DE",
    "Site_Reliability_Engineer": "SR",
    "UI_UX_Designer":            "UX",
    "Network_Engineer":          "NE",
    "Business_Systems_Analyst":  "BA",
    "AI_NLP_Engineer":           "AI",
    "Blockchain_Developer":      "BC",
    "Embedded_Systems_Engineer": "EM",
}


# ─────────────────────────────────────────────
# FEATURE GENERATORS
# ─────────────────────────────────────────────

def gen_edu_level(role):
    dist = ROLE_EDU_DISTRIBUTION[role]
    return int(np.random.choice([1, 2, 3, 4], p=dist))


def gen_experience(role):
    mean, std = ROLE_EXP_DISTRIBUTION[role]
    return max(0.0, round(float(np.random.normal(mean, std)), 1))


def gen_edu_relevance(role, edu_level):
    base_by_role = {
        "Software_Engineer":         0.65,
        "Data_Scientist":            0.75,
        "Machine_Learning_Engineer": 0.75,
        "DevOps_Engineer":           0.55,
        "Cybersecurity_Analyst":     0.60,
        "Cloud_Solutions_Architect": 0.58,
        "Database_Administrator":    0.60,
        "Frontend_Developer":        0.58,
        "Backend_Developer":         0.62,
        "Mobile_App_Developer":      0.58,
        "Full_Stack_Developer":      0.60,
        "QA_Test_Automation_Engineer": 0.55,
        "Data_Engineer":             0.62,
        "Site_Reliability_Engineer": 0.55,
        "UI_UX_Designer":            0.70,
        "Network_Engineer":          0.58,
        "Business_Systems_Analyst":  0.68,
        "AI_NLP_Engineer":           0.75,
        "Blockchain_Developer":      0.60,
        "Embedded_Systems_Engineer": 0.62,
    }
    base = base_by_role[role] + (EDU_LEVEL_SCORES[edu_level] - 0.6) * 0.15
    return float(np.clip(base + np.random.normal(0, 0.14), 0.10, 1.0))


def gen_skill_score(role, edu_level, experience):
    role_base = {
        "Software_Engineer":         0.45,
        "Data_Scientist":            0.42,
        "Machine_Learning_Engineer": 0.43,
        "DevOps_Engineer":           0.44,
        "Cybersecurity_Analyst":     0.42,
        "Cloud_Solutions_Architect": 0.44,
        "Database_Administrator":    0.43,
        "Frontend_Developer":        0.48,
        "Backend_Developer":         0.46,
        "Mobile_App_Developer":      0.46,
        "Full_Stack_Developer":      0.46,
        "QA_Test_Automation_Engineer": 0.42,
        "Data_Engineer":             0.44,
        "Site_Reliability_Engineer": 0.44,
        "UI_UX_Designer":            0.40,
        "Network_Engineer":          0.42,
        "Business_Systems_Analyst":  0.40,
        "AI_NLP_Engineer":           0.43,
        "Blockchain_Developer":      0.45,
        "Embedded_Systems_Engineer": 0.44,
    }
    base = (role_base[role] +
            EDU_LEVEL_SCORES[edu_level] * 0.18 +
            min(experience / 10.0, 1.0) * 0.20)
    return float(np.clip(base + np.random.normal(0, 0.12), 0.05, 1.0))


def gen_mcq_score(role, skill, edu_level):
    role_base = {
        "Software_Engineer":         0.40,
        "Data_Scientist":            0.42,
        "Machine_Learning_Engineer": 0.40,
        "DevOps_Engineer":           0.38,
        "Cybersecurity_Analyst":     0.43,
        "Cloud_Solutions_Architect": 0.40,
        "Database_Administrator":    0.41,
        "Frontend_Developer":        0.40,
        "Backend_Developer":         0.40,
        "Mobile_App_Developer":      0.40,
        "Full_Stack_Developer":      0.40,
        "QA_Test_Automation_Engineer": 0.42,
        "Data_Engineer":             0.40,
        "Site_Reliability_Engineer": 0.38,
        "UI_UX_Designer":            0.38,
        "Network_Engineer":          0.40,
        "Business_Systems_Analyst":  0.42,
        "AI_NLP_Engineer":           0.42,
        "Blockchain_Developer":      0.40,
        "Embedded_Systems_Engineer": 0.40,
    }
    base = role_base[role] + skill * 0.30 + EDU_LEVEL_SCORES[edu_level] * 0.12
    return float(np.clip(base + np.random.normal(0, 0.10), 0.0, 1.0))


def gen_desc_score(role, skill, experience):
    role_base = {
        "Software_Engineer":         0.38,
        "Data_Scientist":            0.42,
        "Machine_Learning_Engineer": 0.40,
        "DevOps_Engineer":           0.36,
        "Cybersecurity_Analyst":     0.42,
        "Cloud_Solutions_Architect": 0.44,
        "Database_Administrator":    0.38,
        "Frontend_Developer":        0.36,
        "Backend_Developer":         0.38,
        "Mobile_App_Developer":      0.37,
        "Full_Stack_Developer":      0.38,
        "QA_Test_Automation_Engineer": 0.38,
        "Data_Engineer":             0.38,
        "Site_Reliability_Engineer": 0.36,
        "UI_UX_Designer":            0.42,
        "Network_Engineer":          0.38,
        "Business_Systems_Analyst":  0.44,
        "AI_NLP_Engineer":           0.40,
        "Blockchain_Developer":      0.38,
        "Embedded_Systems_Engineer": 0.38,
    }
    base = role_base[role] + skill * 0.28 + min(experience / 8.0, 1.0) * 0.18
    return float(np.clip(base + np.random.normal(0, 0.12), 0.0, 1.0))


def gen_code_score(role, skill, experience, edu_level):
    role_base = {
        "Software_Engineer":         0.38,
        "Data_Scientist":            0.30,
        "Machine_Learning_Engineer": 0.36,
        "DevOps_Engineer":           0.35,
        "Cybersecurity_Analyst":     0.28,
        "Cloud_Solutions_Architect": 0.26,
        "Database_Administrator":    0.34,
        "Frontend_Developer":        0.40,
        "Backend_Developer":         0.40,
        "Mobile_App_Developer":      0.40,
        "Full_Stack_Developer":      0.40,
        "QA_Test_Automation_Engineer": 0.35,
        "Data_Engineer":             0.35,
        "Site_Reliability_Engineer": 0.35,
        "UI_UX_Designer":            0.20,
        "Network_Engineer":          0.30,
        "Business_Systems_Analyst":  0.20,
        "AI_NLP_Engineer":           0.36,
        "Blockchain_Developer":      0.40,
        "Embedded_Systems_Engineer": 0.38,
    }
    base = (role_base[role] +
            skill * 0.32 +
            min(experience / 8.0, 1.0) * 0.18 +
            EDU_LEVEL_SCORES[edu_level] * 0.05)
    return float(np.clip(base + np.random.normal(0, 0.13), 0.0, 1.0))


# ─────────────────────────────────────────────
# CSS EQUATIONS (1-8)
# ─────────────────────────────────────────────

def compute_s_edu(edu_level, edu_relevance):
    return round(0.6 * EDU_LEVEL_SCORES[edu_level] + 0.4 * edu_relevance, 4)


def compute_s_exp(years_exp, required_years):
    if required_years <= 0:
        return 1.0
    return round(min(years_exp / required_years, 1.0), 4)


def compute_s_cv(s_edu, s_exp, s_skill, cv_w):
    return round(cv_w["w_edu"]*s_edu + cv_w["w_exp"]*s_exp + cv_w["w_skill"]*s_skill, 4)


def compute_s_int(p_mcq, p_desc, p_code, int_w):
    return round(int_w["w_mcq"]*p_mcq + int_w["w_desc"]*p_desc + int_w["w_code"]*p_code, 4)


def compute_css(s_cv, s_int, W_CV=0.40, W_INT=0.60):
    return round(W_CV * s_cv + W_INT * s_int, 4)


# ─────────────────────────────────────────────
# HARD FILTER (Equation 1)
# ─────────────────────────────────────────────

def hard_filter(role, edu_level, years_exp, s_skill, p_code):
    req = ROLE_REQUIREMENTS[role]
    return (edu_level    >= req["min_edu"] and
            years_exp    >= req["min_exp"] and
            s_skill      >= req["min_skill"] and
            p_code       >= req["min_code"])


# ─────────────────────────────────────────────
# GROUND TRUTH RELEVANCE LABELS
# ─────────────────────────────────────────────

def assign_relevance(role, css, s_skill, p_code, p_desc, s_exp, s_edu, p_mcq):
    dom = ROLE_RELEVANCE_THRESHOLDS[role]["dominance"]

    if dom == "code_skill":
        ct = ROLE_RELEVANCE_THRESHOLDS[role]["code"]
        st = ROLE_RELEVANCE_THRESHOLDS[role]["skill"]
        if p_code >= ct[0] and s_skill >= st[0] and css >= 0.70:
            label = 3
        elif p_code >= ct[1] and s_skill >= st[1] and css >= 0.55:
            label = 2
        elif p_code >= ct[2] and s_skill >= st[2] and css >= 0.40:
            label = 1
        else:
            label = 0

    elif dom == "desc_skill":
        dt = ROLE_RELEVANCE_THRESHOLDS[role]["desc"]
        st = ROLE_RELEVANCE_THRESHOLDS[role]["skill"]
        if p_desc >= dt[0] and s_skill >= st[0] and css >= 0.68:
            label = 3
        elif p_desc >= dt[1] and s_skill >= st[1] and css >= 0.53:
            label = 2
        elif p_desc >= dt[2] and s_skill >= st[2] and css >= 0.38:
            label = 1
        else:
            label = 0

    elif dom == "desc_skill_exp":
        dt = ROLE_RELEVANCE_THRESHOLDS[role]["desc"]
        st = ROLE_RELEVANCE_THRESHOLDS[role]["skill"]
        if p_desc >= dt[0] and s_skill >= st[0] and s_exp >= 0.65 and css >= 0.70:
            label = 3
        elif p_desc >= dt[1] and s_skill >= st[1] and s_exp >= 0.45 and css >= 0.55:
            label = 2
        elif p_desc >= dt[2] and s_skill >= st[2] and css >= 0.40:
            label = 1
        else:
            label = 0

    elif dom == "code_skill_desc":
        ct = ROLE_RELEVANCE_THRESHOLDS[role]["code"]
        st = ROLE_RELEVANCE_THRESHOLDS[role]["skill"]
        dt = ROLE_RELEVANCE_THRESHOLDS[role]["desc"]
        if p_code >= ct[0] and s_skill >= st[0] and p_desc >= dt[0] and css >= 0.70:
            label = 3
        elif p_code >= ct[1] and s_skill >= st[1] and p_desc >= dt[1] and css >= 0.54:
            label = 2
        elif (p_code >= ct[2] or p_desc >= dt[2]) and s_skill >= st[2] and css >= 0.40:
            label = 1
        else:
            label = 0
    else:
        label = 1 if css >= 0.50 else 0

    if random.random() < 0.12:
        label = int(np.clip(label + random.choice([-1, 1]), 0, 3))

    return label


# ─────────────────────────────────────────────
# INGESTION & GENERATION
# ─────────────────────────────────────────────

def normalize_excel_dataset(file_path, role):
    """
    Ingests and normalizes an Excel dataset file to the standard 28-column format.
    """
    df_raw = pd.read_excel(file_path)
    req_years = REQUIRED_YEARS[role]
    cv_w = ROLE_CV_WEIGHTS[role]
    int_w = ROLE_INTERVIEW_WEIGHTS[role]

    records = []
    pfx = ROLE_PREFIX_MAP.get(role, role[:2].upper())

    for idx, row in df_raw.iterrows():
        cid = str(row.get("Candidate_ID") or f"{pfx}{idx+1:05d}")
        
        gender_raw = str(row.get("Gender", "M")).strip()
        gender = "F" if gender_raw.upper().startswith("F") else "M"
        
        age_group = str(row.get("Age_Group", "26-30"))
        
        edu_num = row.get("Education_Level_Num")
        if pd.isna(edu_num) or edu_num is None:
            edu_name = str(row.get("Education_Level", "BSc"))
            name_to_num = {"Diploma": 1, "BSc": 2, "MSc": 3, "PhD": 4}
            edu_level = name_to_num.get(edu_name, 2)
        else:
            edu_level = int(edu_num)
        edu_level_name = EDU_LEVEL_NAMES.get(edu_level, "BSc")

        years_exp = float(row.get("Years_Experience", 3.0))
        edu_rel = float(row.get("Education_Relevance", 0.70))

        p_mcq = float(row.get("MCQ_Score", 0.5))
        p_desc = float(row.get("Descriptive_Score", 0.5))
        p_code = float(row.get("Coding_Score", 0.5))
        s_skill = float(row.get("Skill_Match_Raw", row.get("S_skill", 0.5)))

        s_edu = compute_s_edu(edu_level, edu_rel)
        s_exp = compute_s_exp(years_exp, req_years)
        s_cv = compute_s_cv(s_edu, s_exp, s_skill, cv_w)
        s_int = compute_s_int(p_mcq, p_desc, p_code, int_w)
        css = compute_css(s_cv, s_int)

        passed = hard_filter(role, edu_level, years_exp, s_skill, p_code)
        
        rel_label = row.get("Relevance_Label")
        if pd.isna(rel_label) or rel_label is None:
            rel_label = assign_relevance(role, css, s_skill, p_code, p_desc, s_exp, s_edu, p_mcq)
        else:
            rel_label = int(rel_label)

        records.append({
            "candidate_id":     cid,
            "job_role":         role,
            "job_role_display": ROLE_DISPLAY_NAMES[role],
            "gender":           gender,
            "age_group":        age_group,
            "edu_level":        edu_level,
            "edu_level_name":   edu_level_name,
            "years_experience": round(years_exp, 1),
            "edu_relevance":    round(edu_rel, 4),
            "P_mcq":            round(p_mcq, 4),
            "P_desc":           round(p_desc, 4),
            "P_code":           round(p_code, 4),
            "S_edu":            round(s_edu, 4),
            "S_exp":            round(s_exp, 4),
            "S_skill":          round(s_skill, 4),
            "S_cv":             round(s_cv, 4),
            "S_int":            round(s_int, 4),
            "CSS":              round(css, 4),
            "passed_hard_filter": int(passed),
            "relevance_label":    rel_label,
            "w_edu":    cv_w["w_edu"],
            "w_exp":    cv_w["w_exp"],
            "w_skill":  cv_w["w_skill"],
            "w_mcq":    int_w["w_mcq"],
            "w_desc":   int_w["w_desc"],
            "w_code":   int_w["w_code"],
            "W_CV":     0.40,
            "W_INT":    0.60,
        })

    return pd.DataFrame(records)


def generate_candidates(role, n=RECORDS_PER_ROLE):
    req_years = REQUIRED_YEARS[role]
    cv_w      = ROLE_CV_WEIGHTS[role]
    int_w     = ROLE_INTERVIEW_WEIGHTS[role]
    records   = []
    pfx = ROLE_PREFIX_MAP.get(role, role[:2].upper())

    for i in range(n):
        gender    = np.random.choice(["M", "F"], p=[0.58, 0.42])
        age_group = np.random.choice(
            ["22-25", "26-30", "31-35", "36-40", "40+"],
            p=[0.28, 0.32, 0.22, 0.12, 0.06]
        )

        edu_level    = gen_edu_level(role)
        years_exp    = gen_experience(role)
        edu_rel      = gen_edu_relevance(role, edu_level)
        s_skill      = gen_skill_score(role, edu_level, years_exp)
        p_mcq        = gen_mcq_score(role, s_skill, edu_level)
        p_desc       = gen_desc_score(role, s_skill, years_exp)
        p_code       = gen_code_score(role, s_skill, years_exp, edu_level)

        s_edu  = compute_s_edu(edu_level, edu_rel)
        s_exp  = compute_s_exp(years_exp, req_years)
        s_cv   = compute_s_cv(s_edu, s_exp, s_skill, cv_w)
        s_int  = compute_s_int(p_mcq, p_desc, p_code, int_w)
        css    = compute_css(s_cv, s_int)

        passed = hard_filter(role, edu_level, years_exp, s_skill, p_code)
        rel = assign_relevance(role, css, s_skill, p_code, p_desc,
                                s_exp, s_edu, p_mcq)

        records.append({
            "candidate_id":     f"{pfx}{i+1:05d}",
            "job_role":         role,
            "job_role_display": ROLE_DISPLAY_NAMES[role],
            "gender":           gender,
            "age_group":        age_group,
            "edu_level":        edu_level,
            "edu_level_name":   EDU_LEVEL_NAMES[edu_level],
            "years_experience": years_exp,
            "edu_relevance":    round(edu_rel, 4),
            "P_mcq":            round(p_mcq, 4),
            "P_desc":           round(p_desc, 4),
            "P_code":           round(p_code, 4),
            "S_edu":            round(s_edu, 4),
            "S_exp":            round(s_exp, 4),
            "S_skill":          round(s_skill, 4),
            "S_cv":             round(s_cv, 4),
            "S_int":            round(s_int, 4),
            "CSS":              round(css, 4),
            "passed_hard_filter": int(passed),
            "relevance_label":    rel,
            "w_edu":    cv_w["w_edu"],
            "w_exp":    cv_w["w_exp"],
            "w_skill":  cv_w["w_skill"],
            "w_mcq":    int_w["w_mcq"],
            "w_desc":   int_w["w_desc"],
            "w_code":   int_w["w_code"],
            "W_CV":     0.40,
            "W_INT":    0.60,
        })

    return pd.DataFrame(records)


def load_or_generate_all_roles(datasets_dir):
    """Loads all 20 role datasets, prioritizing provided Excel files, and outputs normalized DataFrames."""
    role_dfs = {}
    for role in ROLES:
        excel_name = EXCEL_ROLE_MAPPING.get(role)
        excel_path = os.path.join(datasets_dir, excel_name) if excel_name else None
        
        if excel_path and os.path.exists(excel_path):
            df = normalize_excel_dataset(excel_path, role)
            print(f"  [OK] Loaded Excel: {excel_name:<35} -> {role} ({len(df)} rows)")
        else:
            csv_path = os.path.join(datasets_dir, f"role_{role}.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                print(f"  [OK] Loaded CSV:   role_{role}.csv{' ':<24} -> {role} ({len(df)} rows)")
            else:
                df = generate_candidates(role, RECORDS_PER_ROLE)
                print(f"  [OK] Generated:    {role:<35} ({len(df)} rows)")
        role_dfs[role] = df
    return role_dfs


def generate_fairness_dataset(n_per_group=250):
    """
    Demographically balanced dataset for fairness testing.
    250 male + 250 female per role = 500 × 20 = 10,000 total.
    """
    all_records = []

    for role in ROLES:
        req_years = REQUIRED_YEARS[role]
        cv_w      = ROLE_CV_WEIGHTS[role]
        int_w     = ROLE_INTERVIEW_WEIGHTS[role]
        pfx       = ROLE_PREFIX_MAP.get(role, role[:2].upper())

        for gender in ["M", "F"]:
            for j in range(n_per_group):
                edu_level = gen_edu_level(role)
                years_exp = gen_experience(role)
                edu_rel   = gen_edu_relevance(role, edu_level)
                s_skill   = gen_skill_score(role, edu_level, years_exp)
                p_mcq     = gen_mcq_score(role, s_skill, edu_level)
                p_desc    = gen_desc_score(role, s_skill, years_exp)
                p_code    = gen_code_score(role, s_skill, years_exp, edu_level)

                s_edu  = compute_s_edu(edu_level, edu_rel)
                s_exp  = compute_s_exp(years_exp, req_years)
                s_cv   = compute_s_cv(s_edu, s_exp, s_skill, cv_w)
                s_int  = compute_s_int(p_mcq, p_desc, p_code, int_w)
                css    = compute_css(s_cv, s_int)

                passed = hard_filter(role, edu_level, years_exp, s_skill, p_code)
                rel    = assign_relevance(role, css, s_skill, p_code, p_desc,
                                          s_exp, s_edu, p_mcq)

                all_records.append({
                    "candidate_id":       f"FA{pfx}{gender}{j+1:04d}",
                    "job_role":           role,
                    "gender":             gender,
                    "age_group":          np.random.choice(["22-25","26-30","31-35","36+"]),
                    "edu_level":          edu_level,
                    "edu_level_name":     EDU_LEVEL_NAMES[edu_level],
                    "years_experience":   years_exp,
                    "edu_relevance":      round(edu_rel, 4),
                    "P_mcq":              round(p_mcq,   4),
                    "P_desc":             round(p_desc,  4),
                    "P_code":             round(p_code,  4),
                    "S_edu":              round(s_edu,   4),
                    "S_exp":              round(s_exp,   4),
                    "S_skill":            round(s_skill, 4),
                    "S_cv":               round(s_cv,    4),
                    "S_int":              round(s_int,   4),
                    "CSS":                round(css,     4),
                    "passed_hard_filter": int(passed),
                    "relevance_label":    rel,
                    "shortlisted":        int(css >= 0.55),
                })

    return pd.DataFrame(all_records)


def generate_job_requirements():
    """Job requirement profiles for all 20 roles."""
    from data.role_configs import (ROLE_REQUIRED_SKILLS, ROLE_REQUIREMENTS,
                                    REQUIRED_YEARS, ROLE_CV_WEIGHTS,
                                    ROLE_INTERVIEW_WEIGHTS, EDU_LEVEL_NAMES)
    rows = []
    for i, role in enumerate(ROLES):
        req  = ROLE_REQUIREMENTS[role]
        cv_w = ROLE_CV_WEIGHTS[role]
        in_w = ROLE_INTERVIEW_WEIGHTS[role]
        rows.append({
            "job_id":              f"JOB{i+1:03d}",
            "job_role":            role,
            "job_title":           ROLE_DISPLAY_NAMES[role],
            "required_skills":     ROLE_REQUIRED_SKILLS[role],
            "min_edu":             req["min_edu"],
            "min_edu_name":        EDU_LEVEL_NAMES[req["min_edu"]],
            "min_exp_years":       req["min_exp"],
            "required_exp_years":  REQUIRED_YEARS[role],
            "min_skill_threshold": req["min_skill"],
            "min_code_threshold":  req["min_code"],
            "w_edu":               cv_w["w_edu"],
            "w_exp":               cv_w["w_exp"],
            "w_skill":             cv_w["w_skill"],
            "w_mcq":               in_w["w_mcq"],
            "w_desc":              in_w["w_desc"],
            "w_code":              in_w["w_code"],
            "W_CV":                0.40,
            "W_INT":               0.60,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────

if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")
    os.makedirs(OUT, exist_ok=True)

    print("=" * 65)
    print("  GENERATING & INGESTING DATASETS — 20 IT Roles | Component 3")
    print("  IT22027610 | Perera K.G.S.N | R26-IT-148")
    print("=" * 65)

    role_dfs = load_or_generate_all_roles(OUT)
    
    # Save each role CSV
    for role, df in role_dfs.items():
        safe = role.replace(" ", "_")
        df.to_csv(f"{OUT}/role_{safe}.csv", index=False)

    full_df = pd.concat(list(role_dfs.values()), ignore_index=True)
    print(f"\n  Total Candidates: {len(full_df):,} across {len(ROLES)} roles")

    # Train / Val / Test split (60/15/25) per role
    train_l, val_l, test_l = [], [], []
    for role in ROLES:
        rdf = full_df[full_df["job_role"] == role].sample(frac=1, random_state=42)
        n = len(rdf)
        t1, t2 = int(n * 0.60), int(n * 0.75)
        train_l.append(rdf.iloc[:t1])
        val_l.append(rdf.iloc[t1:t2])
        test_l.append(rdf.iloc[t2:])

    train_df = pd.concat(train_l, ignore_index=True)
    val_df   = pd.concat(val_l,   ignore_index=True)
    test_df  = pd.concat(test_l,  ignore_index=True)

    print(f"  Train: {len(train_df):,} | Val: {len(val_df):,} | Test: {len(test_df):,}")

    print("\n  Generating Fairness Dataset (250M + 250F per role)...")
    fair_df = generate_fairness_dataset(250)
    print(f"  Fairness Set: {len(fair_df):,} records")

    jobs_df = generate_job_requirements()

    # Save master datasets
    full_df.to_csv(f"{OUT}/candidates_full.csv",       index=False)
    train_df.to_csv(f"{OUT}/train_set.csv",             index=False)
    val_df.to_csv(f"{OUT}/val_set.csv",                 index=False)
    test_df.to_csv(f"{OUT}/test_set.csv",               index=False)
    fair_df.to_csv(f"{OUT}/fairness_test_set.csv",      index=False)
    jobs_df.to_csv(f"{OUT}/job_requirements.csv",       index=False)

    print("\n  All 20 Role Datasets & Master Splits Saved Successfully:")
    for fname in ["candidates_full.csv", "train_set.csv", "val_set.csv",
                  "test_set.csv", "fairness_test_set.csv", "job_requirements.csv"]:
        size = os.path.getsize(f"{OUT}/{fname}") // 1024
        rows = len(pd.read_csv(f"{OUT}/{fname}"))
        print(f"    {fname:<35} {rows:>6} rows | {size:>5} KB")
    print(f"\n  Per-role CSVs: datasets/role_<rolename>.csv (20 files)")
    print("=" * 65)
