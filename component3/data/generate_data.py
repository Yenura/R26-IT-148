"""
Synthetic Dataset Generator - Component 3
IT22027610 | Perera K.G.S.N | R26-IT-148

Generates realistic synthetic data for 10 specific IT job roles.
Each candidate has role-relevant features with realistic correlations.

Total: 600 candidates per role × 10 roles = 6,000 records
Split: Train(3600) / Val(900) / Test(1500) / Fairness(500)
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

RECORDS_PER_ROLE = 600   # 600 × 10 = 6,000 total


# ─────────────────────────────────────────────
# FEATURE GENERATORS
# ─────────────────────────────────────────────

def gen_edu_level(role):
    dist = ROLE_EDU_DISTRIBUTION[role]
    return int(np.random.choice([1, 2, 3, 4], p=dist))


def gen_experience(role):
    mean, std = ROLE_EXP_DISTRIBUTION[role]
    return max(0.0, round(np.random.normal(mean, std), 1))


def gen_edu_relevance(role, edu_level):
    """
    How relevant the candidate's degree is to the role.
    Research roles (DS, MLE) have higher relevance on average.
    """
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
    }
    base = base_by_role[role] + (EDU_LEVEL_SCORES[edu_level] - 0.6) * 0.15
    return float(np.clip(base + np.random.normal(0, 0.14), 0.10, 1.0))


def gen_skill_score(role, edu_level, experience):
    """
    Skill score correlated with education + experience.
    Higher for roles where skills are easily demonstrated.
    """
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
    }
    base = (role_base[role] +
            EDU_LEVEL_SCORES[edu_level] * 0.18 +
            min(experience / 10.0, 1.0) * 0.20)
    return float(np.clip(base + np.random.normal(0, 0.12), 0.05, 1.0))


def gen_mcq_score(role, skill, edu_level):
    """MCQ: knowledge-based, correlates with skill and education."""
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
    }
    base = role_base[role] + skill * 0.30 + EDU_LEVEL_SCORES[edu_level] * 0.12
    return float(np.clip(base + np.random.normal(0, 0.10), 0.0, 1.0))


def gen_desc_score(role, skill, experience):
    """Descriptive: analytical/communication, correlates with skill + experience."""
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
    }
    base = role_base[role] + skill * 0.28 + min(experience / 8.0, 1.0) * 0.18
    return float(np.clip(base + np.random.normal(0, 0.12), 0.0, 1.0))


def gen_code_score(role, skill, experience, edu_level):
    """
    Coding: practical ability.
    Highest weight for SE, Frontend, Backend, Mobile, DevOps, MLE.
    Lower for Cloud Architect, Cybersecurity Analyst (more descriptive roles).
    """
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
# Role-specific hiring logic → labels 0-3
# ─────────────────────────────────────────────

def assign_relevance(role, css, s_skill, p_code, p_desc, s_exp, s_edu, p_mcq):
    """
    Role-specific ground truth relevance labels (0-3).
    Based on domain knowledge of what each role values most.
    """
    dom = ROLE_RELEVANCE_THRESHOLDS[role]["dominance"]

    if dom == "code_skill":
        # SE, DevOps, Frontend, Backend, Mobile
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
        # DS, Cybersecurity, Cloud Architect
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
        # Cloud Architect - experience matters a lot too
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
        # MLE, DBA - balanced
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

    # 12% noise - simulates real-world imperfection
    if random.random() < 0.12:
        label = int(np.clip(label + random.choice([-1, 1]), 0, 3))

    return label


# ─────────────────────────────────────────────
# MAIN GENERATOR
# ─────────────────────────────────────────────

def generate_candidates(role, n=RECORDS_PER_ROLE):
    req_years = REQUIRED_YEARS[role]
    cv_w      = ROLE_CV_WEIGHTS[role]
    int_w     = ROLE_INTERVIEW_WEIGHTS[role]
    records   = []

    # Prefix for candidate IDs
    prefix_map = {
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
    }
    pfx = prefix_map[role]

    for i in range(n):
        gender    = np.random.choice(["M", "F"], p=[0.58, 0.42])
        age_group = np.random.choice(
            ["22-25", "26-30", "31-35", "36-40", "40+"],
            p=[0.28, 0.32, 0.22, 0.12, 0.06]
        )

        # Generate raw features
        edu_level    = gen_edu_level(role)
        years_exp    = gen_experience(role)
        edu_rel      = gen_edu_relevance(role, edu_level)
        s_skill      = gen_skill_score(role, edu_level, years_exp)
        p_mcq        = gen_mcq_score(role, s_skill, edu_level)
        p_desc       = gen_desc_score(role, s_skill, years_exp)
        p_code       = gen_code_score(role, s_skill, years_exp, edu_level)

        # Compute scored values (Equations 2-8)
        s_edu  = compute_s_edu(edu_level, edu_rel)
        s_exp  = compute_s_exp(years_exp, req_years)
        s_cv   = compute_s_cv(s_edu, s_exp, s_skill, cv_w)
        s_int  = compute_s_int(p_mcq, p_desc, p_code, int_w)
        css    = compute_css(s_cv, s_int)

        # Hard filter
        passed = hard_filter(role, edu_level, years_exp, s_skill, p_code)

        # Ground truth label
        rel = assign_relevance(role, css, s_skill, p_code, p_desc,
                                s_exp, s_edu, p_mcq)

        records.append({
            "candidate_id":     f"{pfx}{i+1:05d}",
            "job_role":         role,
            "job_role_display": ROLE_DISPLAY_NAMES[role],

            # Demographics (fairness only)
            "gender":           gender,
            "age_group":        age_group,

            # CV raw inputs
            "edu_level":        edu_level,
            "edu_level_name":   EDU_LEVEL_NAMES[edu_level],
            "years_experience": years_exp,
            "edu_relevance":    round(edu_rel,   4),

            # Interview raw inputs
            "P_mcq":            round(p_mcq,  4),
            "P_desc":           round(p_desc, 4),
            "P_code":           round(p_code, 4),

            # Computed sub-scores
            "S_edu":            round(s_edu,  4),
            "S_exp":            round(s_exp,  4),
            "S_skill":          round(s_skill,4),
            "S_cv":             round(s_cv,   4),
            "S_int":            round(s_int,  4),
            "CSS":              round(css,    4),

            # Filter & label
            "passed_hard_filter": int(passed),
            "relevance_label":    rel,

            # Weights used
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


def generate_fairness_dataset(n_per_group=250):
    """
    Demographically balanced dataset for fairness testing.
    250 male + 250 female per role = 500 × 10 = 5,000 total.
    Tests each role separately.
    """
    all_records = []

    for role in ROLES:
        req_years = REQUIRED_YEARS[role]
        cv_w      = ROLE_CV_WEIGHTS[role]
        int_w     = ROLE_INTERVIEW_WEIGHTS[role]
        pfx       = role[:2].upper()

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
                    "candidate_id":       f"FA{role[:2].upper()}{gender}{j+1:04d}",
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
    """Job requirement profiles for all 10 roles."""
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
# RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")
    os.makedirs(OUT, exist_ok=True)

    print("=" * 65)
    print("  GENERATING DATASETS — 10 IT Roles | Component 3")
    print("  IT22027610 | Perera K.G.S.N | R26-IT-148")
    print("=" * 65)

    all_dfs = []
    for role in ROLES:
        df = generate_candidates(role, RECORDS_PER_ROLE)
        all_dfs.append(df)
        vc = df["relevance_label"].value_counts().sort_index().to_dict()
        pf = df["passed_hard_filter"].mean() * 100
        print(f"  {role:<30} n={len(df)} | filter={pf:.0f}% | labels={vc}")

    full_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\n  Total: {len(full_df):,} candidates")

    # Train / Val / Test split (60/15/25) per role
    train_l, val_l, test_l = [], [], []
    for role in ROLES:
        rdf = full_df[full_df["job_role"]==role].sample(frac=1, random_state=42)
        n   = len(rdf)
        t1, t2 = int(n*0.60), int(n*0.75)
        train_l.append(rdf.iloc[:t1])
        val_l.append(rdf.iloc[t1:t2])
        test_l.append(rdf.iloc[t2:])

    train_df = pd.concat(train_l, ignore_index=True)
    val_df   = pd.concat(val_l,   ignore_index=True)
    test_df  = pd.concat(test_l,  ignore_index=True)

    print(f"\n  Train: {len(train_df):,} | Val: {len(val_df):,} | Test: {len(test_df):,}")

    # Per-role datasets for individual training
    print("\n  Saving per-role datasets...")
    for role in ROLES:
        role_df = full_df[full_df["job_role"] == role]
        safe    = role.replace(" ", "_")
        role_df.to_csv(f"{OUT}/role_{safe}.csv", index=False)

    # Fairness dataset
    print("\n  Generating fairness dataset (250M+250F per role)...")
    fair_df = generate_fairness_dataset(250)
    print(f"  Fairness: {len(fair_df):,} | Gender: {fair_df['gender'].value_counts().to_dict()}")

    # Job requirements
    jobs_df = generate_job_requirements()

    # Save all
    full_df.to_csv(f"{OUT}/candidates_full.csv",       index=False)
    train_df.to_csv(f"{OUT}/train_set.csv",             index=False)
    val_df.to_csv(f"{OUT}/val_set.csv",                 index=False)
    test_df.to_csv(f"{OUT}/test_set.csv",               index=False)
    fair_df.to_csv(f"{OUT}/fairness_test_set.csv",      index=False)
    jobs_df.to_csv(f"{OUT}/job_requirements.csv",       index=False)

    print("\n  Files saved:")
    for fname in ["candidates_full.csv","train_set.csv","val_set.csv",
                  "test_set.csv","fairness_test_set.csv","job_requirements.csv"]:
        size = os.path.getsize(f"{OUT}/{fname}") // 1024
        rows = len(pd.read_csv(f"{OUT}/{fname}"))
        print(f"    {fname:<35} {rows:>6} rows | {size} KB")
    print(f"\n  Per-role CSVs: datasets/role_<rolename>.csv  (10 files)")
    print("=" * 65)
