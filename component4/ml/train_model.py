"""
Component 4 — ML Training Script (10K Dataset)
Dataset: Data_set/job_dataset_real_titles_10000.csv  (10,000 records, 22 columns)
Trains a classifier to predict hire probability from job/skills features.
Saves all artefacts to component4/models/

Usage:
    python component4/ml/train_model.py
"""

import os
import sys
import json
import warnings

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report
from sklearn.preprocessing import LabelEncoder  # noqa: F401 (kept for future use)

# L2 fix: silence only sklearn version warnings, not all warnings globally
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Accept either the 20k dataset (current) or legacy 10k filename
_DS_20K = os.path.join(ROOT, "Data_set", "job_dataset_20_roles_20000.csv")
_DS_10K = os.path.join(ROOT, "Data_set", "job_dataset_real_titles_10000.csv")
DS_PATH = _DS_20K if os.path.exists(_DS_20K) else _DS_10K
OUT_DIR = os.path.join(ROOT, "component4", "models")

# ── Ordinal encoding maps ──────────────────────────────────────────────────────
EDU_RANK = {
    "Bootcamp + Self-Taught":                 1,
    "Associate Degree in Computer Science":    2,
    "B.Sc. Computer Science":                 3,
    "B.Sc. Information Technology":           3,
    "B.Sc. Software Engineering":             3,
    "B.Sc. Mathematics":                      3,
    "B.Sc. Statistics":                       3,
    "B.Sc. Cognitive Science":                3,
    "B.Sc. Physics (CS minor)":               3,
    "B.Eng. Electrical Engineering":          3,
    "B.Eng. Electronics & Communication":     3,
    "MBA (IT / Analytics)":                   4,
    "M.Sc. Computer Science":                 5,
    "M.Sc. Data Science":                     5,
    "M.Sc. Machine Learning":                 5,
    "M.Sc. Cybersecurity":                    5,
    "M.Sc. Artificial Intelligence":          5,
    "M.Sc. Information Systems":              5,
    "Ph.D. Computer Science":                 6,
    "Ph.D. Artificial Intelligence":          6,
}

LEVEL_RANK = {
    "Junior":            1,
    "Mid-Level":         2,
    "Senior":            3,
    "Lead":              4,
    "Principal / Staff": 5,
}

WORK_MODE_RANK = {
    "On-Site": 1,
    "Hybrid":  2,
    "Remote":  3,
}

# ── Helper functions ───────────────────────────────────────────────────────────

def extract_top_skills(df: pd.DataFrame, col: str, n: int = 30) -> list:
    """Count and return the top-n skills from a pipe-delimited column."""
    from collections import Counter
    ctr = Counter()
    for val in df[col].dropna():
        for s in str(val).split("|"):
            s = s.strip()
            if s:
                ctr[s] += 1
    return [s for s, _ in ctr.most_common(n)]


def skill_flags(text: str, skill_list: list) -> dict:
    """Return binary presence flags for each skill in a pipe-delimited string."""
    lower = str(text).lower() if pd.notna(text) else ""
    return {
        f"skill_{s.lower().replace(' ','_').replace('/','_').replace('+','plus').replace('-','_')}": int(s.lower() in lower)
        for s in skill_list
    }


def role_requirements(df: pd.DataFrame, role: str, top_n: int = 5) -> dict:
    """Derive required/optional skills and min experience for a role."""
    sub        = df[df["Job Role"] == role]
    req_skills = extract_top_skills(sub, "Required Skills", top_n)
    opt_skills = [s for s in extract_top_skills(sub, "Skills", top_n) if s not in req_skills][:4]
    med_exp    = int(sub["Experience (Years)"].median())
    return {
        "required":       req_skills,
        "optional":       opt_skills,
        "min_experience": max(1, med_exp - 2),
    }


# ── Knowledge base constants ───────────────────────────────────────────────────

LEARNING_RESOURCES = {
    "Python":           {"course": "Python for Everybody – Coursera",              "url": "https://www.coursera.org/specializations/python",              "duration": "3 months", "level": "Beginner"},
    "Java":             {"course": "Java Programming and Software Engineering",     "url": "https://www.coursera.org/specializations/java-programming",     "duration": "5 months", "level": "Beginner"},
    "C++":              {"course": "C++ for C Programmers – Coursera",              "url": "https://www.coursera.org/learn/c-plus-plus-a",                  "duration": "2 months", "level": "Intermediate"},
    "Go":               {"course": "Programming with Google Go – Coursera",         "url": "https://www.coursera.org/specializations/google-golang",        "duration": "3 months", "level": "Intermediate"},
    "Rust":             {"course": "Rust Programming – Udemy",                      "url": "https://www.udemy.com/course/rust-fundamentals/",               "duration": "2 months", "level": "Intermediate"},
    "TypeScript":       {"course": "Understanding TypeScript – Udemy",              "url": "https://www.udemy.com/course/understanding-typescript/",        "duration": "6 weeks",  "level": "Intermediate"},
    "SQL":              {"course": "SQL for Data Science – Coursera",               "url": "https://www.coursera.org/learn/sql-for-data-science",           "duration": "1 month",  "level": "Beginner"},
    "PostgreSQL":       {"course": "Learn PostgreSQL – freeCodeCamp (YouTube)",     "url": "https://www.youtube.com/watch?v=qw--VYLpxG4",                   "duration": "4 weeks",  "level": "Intermediate"},
    "MongoDB":          {"course": "MongoDB Basics – MongoDB University",           "url": "https://learn.mongodb.com/",                                   "duration": "3 weeks",  "level": "Beginner"},
    "Machine Learning": {"course": "Machine Learning Specialization – Andrew Ng",   "url": "https://www.coursera.org/specializations/machine-learning-introduction", "duration": "3 months", "level": "Intermediate"},
    "Deep Learning":    {"course": "Deep Learning Specialization – deeplearning.ai","url": "https://www.coursera.org/specializations/deep-learning",        "duration": "4 months", "level": "Intermediate"},
    "TensorFlow":       {"course": "TensorFlow Developer Certificate – Coursera",   "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice", "duration": "4 months", "level": "Intermediate"},
    "PyTorch":          {"course": "PyTorch for Deep Learning – fast.ai",           "url": "https://www.fast.ai/",                                         "duration": "3 months", "level": "Intermediate"},
    "NLP":              {"course": "Natural Language Processing – Coursera",        "url": "https://www.coursera.org/specializations/natural-language-processing", "duration": "4 months", "level": "Advanced"},
    "MLOps":            {"course": "MLOps Specialization – Coursera",               "url": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops", "duration": "4 months", "level": "Advanced"},
    "Feature Engineering": {"course": "Feature Engineering – Kaggle Learn",        "url": "https://www.kaggle.com/learn/feature-engineering",             "duration": "2 weeks",  "level": "Intermediate"},
    "Statistics":       {"course": "Statistics with Python – Coursera",             "url": "https://www.coursera.org/specializations/statistics-with-python", "duration": "3 months", "level": "Beginner"},
    "AWS":              {"course": "AWS Certified Cloud Practitioner – A Cloud Guru","url": "https://acloudguru.com/course/aws-certified-cloud-practitioner", "duration": "3 months", "level": "Beginner"},
    "Azure":            {"course": "Azure Fundamentals (AZ-900) – Microsoft Learn", "url": "https://learn.microsoft.com/en-us/certifications/azure-fundamentals/", "duration": "1 month", "level": "Beginner"},
    "GCP":              {"course": "Google Cloud Professional Data Engineer",        "url": "https://cloud.google.com/certification/data-engineer",          "duration": "3 months", "level": "Intermediate"},
    "Terraform":        {"course": "HashiCorp Terraform Associate – Udemy",          "url": "https://www.udemy.com/course/terraform-beginner-to-advanced/",  "duration": "2 months", "level": "Intermediate"},
    "Docker":           {"course": "Docker & Kubernetes: The Complete Guide – Udemy","url": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/", "duration": "3 months", "level": "Intermediate"},
    "Kubernetes":       {"course": "Kubernetes for Developers – Linux Foundation",   "url": "https://training.linuxfoundation.org/training/kubernetes-for-developers/", "duration": "2 months", "level": "Advanced"},
    "Cybersecurity":    {"course": "Google Cybersecurity Certificate – Coursera",   "url": "https://www.coursera.org/professional-certificates/google-cybersecurity", "duration": "6 months", "level": "Beginner"},
    "Networking":       {"course": "CompTIA Network+ – Professor Messer",            "url": "https://www.professormesser.com/network-plus/n10-008/",         "duration": "3 months", "level": "Beginner"},
    "Linux":            {"course": "Linux Essentials – Cisco NetAcad",               "url": "https://www.netacad.com/courses/os-it/ndg-linux-essentials",    "duration": "2 months", "level": "Beginner"},
    "Ethical Hacking":  {"course": "Certified Ethical Hacker – EC-Council",          "url": "https://www.eccouncil.org/programs/certified-ethical-hacker-ceh/", "duration": "4 months", "level": "Advanced"},
    "React":            {"course": "React – The Complete Guide – Udemy",             "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "duration": "3 months", "level": "Intermediate"},
    "REST APIs":        {"course": "REST API Design, Development & Management",       "url": "https://www.udemy.com/course/rest-api/",                        "duration": "6 weeks",  "level": "Beginner"},
    "GraphQL":          {"course": "GraphQL with React – Udemy",                     "url": "https://www.udemy.com/course/graphql-with-react-course/",       "duration": "5 weeks",  "level": "Intermediate"},
    "Microservices":    {"course": "Microservices with Node JS & React – Udemy",     "url": "https://www.udemy.com/course/microservices-with-node-js-and-react/", "duration": "3 months", "level": "Advanced"},
    "Apache Spark":     {"course": "Apache Spark & Scala – Udemy",                   "url": "https://www.udemy.com/course/apache-spark-with-scala-hands-on-with-big-data/", "duration": "2 months", "level": "Intermediate"},
    "Kafka":            {"course": "Apache Kafka Series – Udemy",                    "url": "https://www.udemy.com/course/apache-kafka/",                    "duration": "2 months", "level": "Intermediate"},
    "Airflow":          {"course": "The Complete Hands-On Introduction to Apache Airflow","url": "https://www.udemy.com/course/the-complete-hands-on-course-to-master-apache-airflow/", "duration": "1 month", "level": "Intermediate"},
}

SKILL_CATEGORIES = {
    "Programming":  ["Python", "Java", "C++", "Go", "Rust", "TypeScript", "Kotlin", "Scala"],
    "Web":          ["React", "REST APIs", "GraphQL", "HTML5", "CSS3", "Vue.js", "Webpack", "TypeScript"],
    "Data/DB":      ["SQL", "PostgreSQL", "MongoDB", "Spark", "Airflow", "Kafka", "Power BI", "Tableau"],
    "ML/AI":        ["Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "MLOps",
                     "Feature Engineering", "Statistics", "LangChain", "Scikit-learn"],
    "Cloud/DevOps": ["AWS", "Azure", "GCP", "Terraform", "Docker", "Kubernetes", "CI/CD", "Microservices"],
    "Security":     ["Cybersecurity", "Networking", "Linux", "Ethical Hacking", "Penetration Testing"],
    "Architecture": ["System Design", "Microservices", "Event-Driven Architecture", "API Gateway"],
}

CAREER_PATHS = {
    "Software Engineer":          ["Junior Developer", "Software Engineer", "Senior Engineer", "Tech Lead", "Engineering Manager", "VP Engineering"],
    "Data Scientist":             ["Junior Data Scientist", "Data Scientist", "Senior Data Scientist", "Lead Data Scientist", "Principal Data Scientist", "Chief Data Officer"],
    "Machine Learning Engineer":  ["ML Engineer (L1)", "ML Engineer", "Senior ML Engineer", "Staff ML Engineer", "Principal ML Engineer", "Director of AI"],
    "Frontend Developer":         ["Junior Frontend Dev", "Frontend Developer", "Senior Frontend Dev", "Lead Frontend Engineer", "Principal Engineer", "CTO"],
    "Backend Developer":          ["Junior Backend Dev", "Backend Developer", "Senior Backend Dev", "Lead Backend Engineer", "Principal Engineer", "CTO"],
    "DevOps Engineer":            ["DevOps Engineer (L1)", "DevOps Engineer", "Senior DevOps", "Lead DevOps", "Platform Engineer", "VP Infrastructure"],
    "Cybersecurity Analyst":      ["Security Analyst (L1)", "Cybersecurity Analyst", "Senior Security Analyst", "Security Architect", "CISO"],
    "Cloud Solutions Architect":  ["Cloud Engineer", "Cloud Architect", "Senior Cloud Architect", "Principal Architect", "VP Cloud"],
    "Database Administrator":     ["Junior DBA", "Database Administrator", "Senior DBA", "Lead DBA", "Data Architect"],
    "Mobile App Developer":       ["Junior Mobile Dev", "Mobile Developer", "Senior Mobile Dev", "Lead Mobile Dev", "Principal Engineer"],
    "Full Stack Developer":       ["Junior Full Stack Dev", "Full Stack Developer", "Senior Full Stack Dev", "Lead Full Stack Engineer", "Principal Engineer", "CTO"],
    "QA/Test Automation Engineer": ["Junior QA Engineer", "QA Engineer", "Senior QA Engineer", "Lead QA Engineer", "QA Architect", "VP Quality"],
    "Data Engineer":              ["Junior Data Engineer", "Data Engineer", "Senior Data Engineer", "Lead Data Engineer", "Data Architect", "VP Data"],
    "Site Reliability Engineer": ["Junior SRE", "SRE", "Senior SRE", "Lead SRE", "Staff SRE", "VP Infrastructure"],
    "UI/UX Designer":             ["Junior UX Designer", "UX Designer", "Senior UX Designer", "Lead UX Designer", "Principal Designer", "VP Design"],
    "Network Engineer":           ["Junior Network Engineer", "Network Engineer", "Senior Network Engineer", "Network Architect", "VP Network Infrastructure"],
    "Business/Systems Analyst":   ["Junior Analyst", "Business Analyst", "Senior Business Analyst", "Lead Analyst", "Director of Business Analysis"],
    "AI/NLP Engineer":            ["Junior AI Engineer", "AI Engineer", "Senior AI Engineer", "Lead AI Engineer", "Principal AI Engineer", "VP AI"],
    "Blockchain Developer":       ["Junior Blockchain Dev", "Blockchain Developer", "Senior Blockchain Dev", "Lead Blockchain Engineer", "Blockchain Architect"],
    "Embedded Systems Engineer":  ["Junior Embedded Engineer", "Embedded Engineer", "Senior Embedded Engineer", "Lead Embedded Engineer", "Embedded Architect"],
}

ROLE_TRANSITIONS = {
    "Software Engineer":         ["Backend Developer", "DevOps Engineer", "Cloud Solutions Architect", "Full Stack Developer"],
    "Data Scientist":            ["Machine Learning Engineer", "Backend Developer", "Database Administrator", "Data Engineer"],
    "Machine Learning Engineer": ["Data Scientist", "Backend Developer", "DevOps Engineer", "AI/NLP Engineer"],
    "Frontend Developer":        ["Mobile App Developer", "Software Engineer", "Full Stack Developer", "UI/UX Designer"],
    "Backend Developer":         ["Software Engineer", "DevOps Engineer", "Cloud Solutions Architect", "Data Engineer"],
    "DevOps Engineer":           ["Cloud Solutions Architect", "Backend Developer", "Database Administrator", "Site Reliability Engineer"],
    "Cybersecurity Analyst":     ["Cloud Solutions Architect", "Database Administrator", "Network Engineer"],
    "Cloud Solutions Architect": ["DevOps Engineer", "Backend Developer", "Site Reliability Engineer"],
    "Database Administrator":    ["Backend Developer", "Data Scientist", "Data Engineer"],
    "Mobile App Developer":      ["Frontend Developer", "Software Engineer", "Full Stack Developer"],
    "Full Stack Developer":      ["Software Engineer", "Backend Developer", "Frontend Developer", "DevOps Engineer"],
    "QA/Test Automation Engineer": ["Backend Developer", "DevOps Engineer", "Software Engineer"],
    "Data Engineer":             ["Data Scientist", "Backend Developer", "Machine Learning Engineer"],
    "Site Reliability Engineer": ["DevOps Engineer", "Cloud Solutions Architect", "Backend Developer"],
    "UI/UX Designer":            ["Frontend Developer", "Business/Systems Analyst"],
    "Network Engineer":          ["Cybersecurity Analyst", "Cloud Solutions Architect", "DevOps Engineer"],
    "Business/Systems Analyst":  ["Project Manager", "Product Manager", "Data Analyst"],
    "AI/NLP Engineer":           ["Machine Learning Engineer", "Data Scientist", "Software Engineer"],
    "Blockchain Developer":      ["Backend Developer", "Software Engineer", "Embedded Systems Engineer"],
    "Embedded Systems Engineer": ["Software Engineer", "Backend Developer", "Network Engineer"],
}


# ── Main training pipeline ─────────────────────────────────────────────────────
def main():
    """Run the full ML training pipeline: load → engineer → train → save."""
    import hashlib
    from datetime import datetime
    import sklearn

    os.makedirs(OUT_DIR, exist_ok=True)

    print("=" * 60)
    print("  Component 4 — ML Model Training (10K Dataset)")
    print("=" * 60)

    # 1. Load dataset
    if not os.path.exists(DS_PATH):
        print(f"[ERROR] Dataset not found: {DS_PATH}")
        sys.exit(1)

    df = pd.read_csv(DS_PATH)
    print(f"\n[INFO] Loaded {len(df)} records, {len(df.columns)} columns")

    # 2. Feature engineering
    df["Education_Enc"] = df["Education"].map(EDU_RANK).fillna(3)
    df["JobLevel_Enc"]  = df["Job Level"].map(LEVEL_RANK).fillna(2)
    df["WorkMode_Enc"]  = df["Work Mode"].map(WORK_MODE_RANK).fillna(2)
    df["Has_Cert"]      = df["Certifications"].notna().astype(int)
    df["Cert_Count"]    = df["Certifications Count"].fillna(0).astype(int)

    # Target: top 25% salary tier as hire proxy
    salary_75pct = df["Salary (USD/Year)"].quantile(0.75)
    df["Target"] = (df["Salary (USD/Year)"] >= salary_75pct).astype(int)
    print(f"[INFO] Target: Hire={df['Target'].sum()} | Reject={(df['Target']==0).sum()}")

    # Skill feature flags
    TOP_REQUIRED    = extract_top_skills(df, "Required Skills", 25)
    TOP_SKILLS      = extract_top_skills(df, "Skills", 30)
    ALL_SKILLS_SET  = list({s for s in TOP_REQUIRED + TOP_SKILLS})[:40]
    print(f"[INFO] Canonical skills ({len(ALL_SKILLS_SET)}): {ALL_SKILLS_SET[:10]}...")

    skill_df = df["Required Skills"].fillna("").apply(
        lambda x: pd.Series(skill_flags(x, ALL_SKILLS_SET))
    )
    df = pd.concat([df, skill_df], axis=1)

    # Role one-hot
    roles     = sorted(df["Job Role"].unique())
    role_cols = []
    for r in roles:
        col = f"role_{r.replace(' ','_').replace('/','_')}"
        df[col] = (df["Job Role"] == r).astype(int)
        role_cols.append(col)

    skill_feat_cols = [c for c in df.columns if c.startswith("skill_")]
    BASE_FEATS = [
        "Experience (Years)", "Education_Enc", "JobLevel_Enc",
        "WorkMode_Enc", "Has_Cert", "Cert_Count", "Projects Count",
    ]
    FEATURE_COLS = BASE_FEATS + role_cols + skill_feat_cols
    print(f"[INFO] Total features: {len(FEATURE_COLS)}")

    X = df[FEATURE_COLS].fillna(0)
    y = df["Target"]

    # 3. Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"[INFO] Train: {len(X_train)} | Test: {len(X_test)}")

    # 4. Train models
    models = {
        "Random Forest":       RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1),
        "Gradient Boosting":   GradientBoostingClassifier(n_estimators=150, max_depth=5, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    }

    results = {}
    for name, clf in models.items():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        y_prob = clf.predict_proba(X_test)[:, 1]
        results[name] = {
            "acc": accuracy_score(y_test, y_pred),
            "f1":  f1_score(y_test, y_pred),
            "auc": roc_auc_score(y_test, y_prob),
            "clf": clf,
        }
        print(f"\n[{name}]  Acc={results[name]['acc']:.4f}  F1={results[name]['f1']:.4f}  AUC={results[name]['auc']:.4f}")

    best_name = max(results, key=lambda k: results[k]["auc"])
    best_clf  = results[best_name]["clf"]
    print(f"\n[BEST] {best_name} selected (AUC={results[best_name]['auc']:.4f})")
    print("\nClassification Report:")
    print(classification_report(y_test, best_clf.predict(X_test)))

    # 5. Save artefacts
    joblib.dump(best_clf,                               os.path.join(OUT_DIR, "skill_gap_classifier.pkl"))
    joblib.dump(results["Random Forest"]["clf"],        os.path.join(OUT_DIR, "random_forest_model.pkl"))
    joblib.dump(results["Gradient Boosting"]["clf"],    os.path.join(OUT_DIR, "gradient_boosting_model.pkl"))
    joblib.dump(results["Logistic Regression"]["clf"],  os.path.join(OUT_DIR, "logistic_regression_model.pkl"))
    joblib.dump(FEATURE_COLS,                           os.path.join(OUT_DIR, "feature_columns.pkl"))
    joblib.dump(role_cols,                              os.path.join(OUT_DIR, "role_columns.pkl"))
    joblib.dump(ALL_SKILLS_SET,                         os.path.join(OUT_DIR, "all_skills.pkl"))

    # 6. Build and save knowledge JSON files
    JOB_REQ = {r: role_requirements(df, r) for r in roles}
    with open(os.path.join(OUT_DIR, "job_requirements.json"), "w")  as f: json.dump(JOB_REQ, f, indent=2)
    with open(os.path.join(OUT_DIR, "learning_resources.json"), "w") as f: json.dump(LEARNING_RESOURCES, f, indent=2)
    with open(os.path.join(OUT_DIR, "skill_categories.json"), "w")   as f: json.dump(SKILL_CATEGORIES, f, indent=2)
    with open(os.path.join(OUT_DIR, "career_paths.json"), "w")       as f:
        json.dump({"career_paths": CAREER_PATHS, "role_transitions": ROLE_TRANSITIONS}, f, indent=2)
    print(f"\n[SAVED] Knowledge files: {len(JOB_REQ)} roles, {len(LEARNING_RESOURCES)} resources")

    # 7. Training metadata (M3 fix: reproducibility record)
    stats = {
        "dataset_path":    DS_PATH,
        "dataset_size":    len(df),
        "dataset_hash":    hashlib.md5(open(DS_PATH, "rb").read()).hexdigest(),
        "feature_count":   len(FEATURE_COLS),
        "roles":           roles,
        "top_skills":      ALL_SKILLS_SET,
        "best_model":      best_name,
        "accuracy":        round(results[best_name]["acc"], 4),
        "f1_score":        round(results[best_name]["f1"],  4),
        "roc_auc":         round(results[best_name]["auc"], 4),
        "train_date":      datetime.now().isoformat(),
        "python_version":  sys.version,
        "sklearn_version": sklearn.__version__,
    }
    with open(os.path.join(OUT_DIR, "training_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  Training complete! Best model: {best_name}")
    print(f"  Accuracy: {stats['accuracy']}  F1: {stats['f1_score']}  AUC: {stats['roc_auc']}")
    print(f"  Saved to: {OUT_DIR}")
    print(f"{'='*60}")


# ── H3 fix: __main__ guard prevents accidental execution on import ────────────
if __name__ == "__main__":
    main()
