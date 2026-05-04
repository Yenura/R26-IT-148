"""
Component 4 — ML Training Script (New Dataset)
Dataset: Data_set/job_dataset_real_titles_10000.csv  (10,000 records, 22 columns)
Trains a Random Forest classifier that predicts hire probability from job/skills features.
Saves all artefacts to component4/models/
"""

import os, sys, json, warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score,
    classification_report, confusion_matrix
)
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DS_PATH = os.path.join(ROOT, "Data_set", "job_dataset_real_titles_10000.csv")
OUT_DIR = os.path.join(ROOT, "component4", "models")
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("  Component 4 — ML Model Training (New 10K Dataset)")
print("=" * 60)

# ── 1. Load Dataset ───────────────────────────────────────────────────────────
df = pd.read_csv(DS_PATH)
print(f"\n[INFO] Loaded {len(df)} records, {len(df.columns)} columns")

# ── 2. Feature Engineering ───────────────────────────────────────────────────
# Education encoding — map to ordinal rank
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

# Job Level encoding
LEVEL_RANK = {
    "Junior":           1,
    "Mid-Level":        2,
    "Senior":           3,
    "Lead":             4,
    "Principal / Staff":5,
}

# Work Mode encoding
WORK_MODE_RANK = {
    "On-Site": 1,
    "Hybrid":  2,
    "Remote":  3,
}

df["Education_Enc"]   = df["Education"].map(EDU_RANK).fillna(3)
df["JobLevel_Enc"]    = df["Job Level"].map(LEVEL_RANK).fillna(2)
df["WorkMode_Enc"]    = df["Work Mode"].map(WORK_MODE_RANK).fillna(2)
df["Has_Cert"]        = df["Certifications"].notna().astype(int)
df["Cert_Count"]      = df["Certifications Count"].fillna(0).astype(int)

# Salary tier (target proxy: higher salary = "hire-worthy")
salary_75pct = df["Salary (USD/Year)"].quantile(0.75)
df["Target"]  = (df["Salary (USD/Year)"] >= salary_75pct).astype(int)

print(f"[INFO] Target distribution (high-salary tier as hire proxy):")
print(f"       Hire (1): {df['Target'].sum()} | Reject (0): {(df['Target']==0).sum()}")

# ── Top skills extracted from dataset ─────────────────────────────────────────
# Parse "Required Skills" and "Skills" columns
def extract_top_skills(df, col, n=30):
    from collections import Counter
    ctr = Counter()
    for val in df[col].dropna():
        for s in str(val).split("|"):
            s = s.strip()
            if s:
                ctr[s] += 1
    return [s for s, _ in ctr.most_common(n)]

TOP_REQUIRED = extract_top_skills(df, "Required Skills", 25)
TOP_SKILLS   = extract_top_skills(df, "Skills", 30)

# Unified canonical skill list (union of both columns, top 40)
ALL_SKILLS_SET = list({s for s in TOP_REQUIRED + TOP_SKILLS})[:40]
print(f"[INFO] Canonical skill list ({len(ALL_SKILLS_SET)} skills): {ALL_SKILLS_SET[:10]}...")

def skill_flags(text, skill_list):
    vals = {}
    lower = str(text).lower() if pd.notna(text) else ""
    for s in skill_list:
        vals[f"skill_{s.lower().replace(' ','_').replace('/','_').replace('+','plus').replace('-','_')}"] = int(s.lower() in lower)
    return vals

skill_df = df["Required Skills"].fillna("").apply(lambda x: pd.Series(skill_flags(x, ALL_SKILLS_SET)))
df = pd.concat([df, skill_df], axis=1)

# Role one-hot
roles = sorted(df["Job Role"].unique())
for r in roles:
    df[f"role_{r.replace(' ','_').replace('/','_')}"] = (df["Job Role"] == r).astype(int)

role_cols = [f"role_{r.replace(' ','_').replace('/','_')}" for r in roles]
skill_feat_cols = [c for c in df.columns if c.startswith("skill_")]

BASE_FEATS = [
    "Experience (Years)", "Education_Enc", "JobLevel_Enc",
    "WorkMode_Enc", "Has_Cert", "Cert_Count", "Projects Count",
]

FEATURE_COLS = BASE_FEATS + role_cols + skill_feat_cols

print(f"[INFO] Total feature columns: {len(FEATURE_COLS)}")

X = df[FEATURE_COLS].fillna(0)
y = df["Target"]

# ── 3. Train / Test Split ─────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"[INFO] Train: {len(X_train)} | Test: {len(X_test)}")

# ── 4. Train Models ───────────────────────────────────────────────────────────
models = {
    "Random Forest":       RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1),
    "Gradient Boosting":   GradientBoostingClassifier(n_estimators=150, max_depth=5, random_state=42),
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
}

results = {}
for name, clf in models.items():
    clf.fit(X_train, y_train)
    y_pred  = clf.predict(X_test)
    y_prob  = clf.predict_proba(X_test)[:, 1]
    acc     = accuracy_score(y_test, y_pred)
    f1      = f1_score(y_test, y_pred)
    auc     = roc_auc_score(y_test, y_prob)
    results[name] = {"acc": acc, "f1": f1, "auc": auc, "clf": clf}
    print(f"\n[{name}]  Acc={acc:.4f}  F1={f1:.4f}  AUC={auc:.4f}")

# Best model
best_name = max(results, key=lambda k: results[k]["auc"])
best_clf  = results[best_name]["clf"]
print(f"\n[BEST] {best_name} selected (AUC={results[best_name]['auc']:.4f})")

print("\nClassification Report:")
print(classification_report(y_test, best_clf.predict(X_test)))

# ── 5. Save artefacts ─────────────────────────────────────────────────────────
joblib.dump(best_clf,                                       os.path.join(OUT_DIR, "skill_gap_classifier.pkl"))
joblib.dump(results["Random Forest"]["clf"],                os.path.join(OUT_DIR, "random_forest_model.pkl"))
joblib.dump(results["Gradient Boosting"]["clf"],            os.path.join(OUT_DIR, "gradient_boosting_model.pkl"))
joblib.dump(results["Logistic Regression"]["clf"],          os.path.join(OUT_DIR, "logistic_regression_model.pkl"))
joblib.dump(FEATURE_COLS,                                   os.path.join(OUT_DIR, "feature_columns.pkl"))
joblib.dump(role_cols,                                      os.path.join(OUT_DIR, "role_columns.pkl"))
joblib.dump(ALL_SKILLS_SET,                                 os.path.join(OUT_DIR, "all_skills.pkl"))

# ── 6. Build knowledge JSON files ─────────────────────────────────────────────

# job_requirements.json  — required/optional skills + min experience per role
# Derived from dataset medians and top required skills per role
def role_requirements(df, role, top_n=5):
    sub = df[df["Job Role"] == role]
    req_skills = extract_top_skills(sub, "Required Skills", top_n)
    opt_skills = extract_top_skills(sub, "Skills", top_n)
    # exclude overlap
    opt_skills = [s for s in opt_skills if s not in req_skills][:4]
    med_exp = int(sub["Experience (Years)"].median())
    return {
        "required": req_skills,
        "optional": opt_skills,
        "min_experience": max(1, med_exp - 2),
    }

JOB_REQ = {r: role_requirements(df, r) for r in roles}
with open(os.path.join(OUT_DIR, "job_requirements.json"), "w") as f:
    json.dump(JOB_REQ, f, indent=2)
print(f"\n[SAVED] job_requirements.json ({len(JOB_REQ)} roles)")

# learning_resources.json  — top skill → course mapping
LEARNING_RESOURCES = {
    # Programming
    "Python":                   {"course": "Python for Everybody – Coursera",              "url": "https://www.coursera.org/specializations/python",              "duration": "3 months", "level": "Beginner"},
    "Java":                     {"course": "Java Programming and Software Engineering",     "url": "https://www.coursera.org/specializations/java-programming",     "duration": "5 months", "level": "Beginner"},
    "C++":                      {"course": "C++ for C Programmers – Coursera",              "url": "https://www.coursera.org/learn/c-plus-plus-a",                  "duration": "2 months", "level": "Intermediate"},
    "Go":                       {"course": "Programming with Google Go – Coursera",         "url": "https://www.coursera.org/specializations/google-golang",        "duration": "3 months", "level": "Intermediate"},
    "Rust":                     {"course": "Rust Programming – Udemy",                      "url": "https://www.udemy.com/course/rust-fundamentals/",               "duration": "2 months", "level": "Intermediate"},
    "TypeScript":               {"course": "Understanding TypeScript – Udemy",              "url": "https://www.udemy.com/course/understanding-typescript/",        "duration": "6 weeks",  "level": "Intermediate"},
    # Data / DB
    "SQL":                      {"course": "SQL for Data Science – Coursera",               "url": "https://www.coursera.org/learn/sql-for-data-science",           "duration": "1 month",  "level": "Beginner"},
    "PostgreSQL":               {"course": "Learn PostgreSQL – freeCodeCamp (YouTube)",     "url": "https://www.youtube.com/watch?v=qw--VYLpxG4",                   "duration": "4 weeks",  "level": "Intermediate"},
    "MongoDB":                  {"course": "MongoDB Basics – MongoDB University",           "url": "https://learn.mongodb.com/",                                   "duration": "3 weeks",  "level": "Beginner"},
    # ML / AI
    "Machine Learning":         {"course": "Machine Learning Specialization – Andrew Ng",   "url": "https://www.coursera.org/specializations/machine-learning-introduction","duration": "3 months", "level": "Intermediate"},
    "Deep Learning":            {"course": "Deep Learning Specialization – deeplearning.ai","url": "https://www.coursera.org/specializations/deep-learning",        "duration": "4 months", "level": "Intermediate"},
    "TensorFlow":               {"course": "TensorFlow Developer Certificate – Coursera",   "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice","duration": "4 months","level": "Intermediate"},
    "PyTorch":                  {"course": "PyTorch for Deep Learning – fast.ai",           "url": "https://www.fast.ai/",                                         "duration": "3 months", "level": "Intermediate"},
    "NLP":                      {"course": "Natural Language Processing – Coursera",        "url": "https://www.coursera.org/specializations/natural-language-processing","duration": "4 months","level": "Advanced"},
    "MLOps":                    {"course": "MLOps Specialization – Coursera",               "url": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops","duration": "4 months","level": "Advanced"},
    "Feature Engineering":      {"course": "Feature Engineering – Kaggle Learn",            "url": "https://www.kaggle.com/learn/feature-engineering",             "duration": "2 weeks",  "level": "Intermediate"},
    "Statistics":               {"course": "Statistics with Python – Coursera",             "url": "https://www.coursera.org/specializations/statistics-with-python","duration": "3 months","level": "Beginner"},
    # Cloud / DevOps
    "AWS":                      {"course": "AWS Certified Cloud Practitioner – A Cloud Guru","url": "https://acloudguru.com/course/aws-certified-cloud-practitioner","duration": "3 months","level": "Beginner"},
    "Azure":                    {"course": "Azure Fundamentals (AZ-900) – Microsoft Learn", "url": "https://learn.microsoft.com/en-us/certifications/azure-fundamentals/","duration": "1 month","level": "Beginner"},
    "GCP":                      {"course": "Google Cloud Professional Data Engineer",        "url": "https://cloud.google.com/certification/data-engineer",          "duration": "3 months", "level": "Intermediate"},
    "Terraform":                {"course": "HashiCorp Terraform Associate – Udemy",          "url": "https://www.udemy.com/course/terraform-beginner-to-advanced/",  "duration": "2 months", "level": "Intermediate"},
    "Docker":                   {"course": "Docker & Kubernetes: The Complete Guide – Udemy","url": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/","duration": "3 months","level": "Intermediate"},
    "Kubernetes":               {"course": "Kubernetes for Developers – Linux Foundation",   "url": "https://training.linuxfoundation.org/training/kubernetes-for-developers/","duration": "2 months","level": "Advanced"},
    # Security
    "Cybersecurity":            {"course": "Google Cybersecurity Certificate – Coursera",   "url": "https://www.coursera.org/professional-certificates/google-cybersecurity","duration": "6 months","level": "Beginner"},
    "Networking":               {"course": "CompTIA Network+ – Professor Messer",            "url": "https://www.professormesser.com/network-plus/n10-008/",         "duration": "3 months", "level": "Beginner"},
    "Linux":                    {"course": "Linux Essentials – Cisco NetAcad",               "url": "https://www.netacad.com/courses/os-it/ndg-linux-essentials",    "duration": "2 months", "level": "Beginner"},
    "Ethical Hacking":          {"course": "Certified Ethical Hacker – EC-Council",          "url": "https://www.eccouncil.org/programs/certified-ethical-hacker-ceh/","duration": "4 months","level": "Advanced"},
    # Web
    "React":                    {"course": "React – The Complete Guide – Udemy",             "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/","duration": "3 months","level": "Intermediate"},
    "REST APIs":                {"course": "REST API Design, Development & Management",       "url": "https://www.udemy.com/course/rest-api/",                        "duration": "6 weeks",  "level": "Beginner"},
    "GraphQL":                  {"course": "GraphQL with React – Udemy",                     "url": "https://www.udemy.com/course/graphql-with-react-course/",       "duration": "5 weeks",  "level": "Intermediate"},
    "Microservices":            {"course": "Microservices with Node JS & React – Udemy",     "url": "https://www.udemy.com/course/microservices-with-node-js-and-react/","duration": "3 months","level": "Advanced"},
    # Data Engineering
    "Apache Spark":             {"course": "Apache Spark & Scala – Udemy",                   "url": "https://www.udemy.com/course/apache-spark-with-scala-hands-on-with-big-data/","duration": "2 months","level": "Intermediate"},
    "Kafka":                    {"course": "Apache Kafka Series – Udemy",                    "url": "https://www.udemy.com/course/apache-kafka/",                    "duration": "2 months", "level": "Intermediate"},
    "Airflow":                  {"course": "The Complete Hands-On Introduction to Apache Airflow","url": "https://www.udemy.com/course/the-complete-hands-on-course-to-master-apache-airflow/","duration": "1 month","level": "Intermediate"},
}
with open(os.path.join(OUT_DIR, "learning_resources.json"), "w") as f:
    json.dump(LEARNING_RESOURCES, f, indent=2)
print(f"[SAVED] learning_resources.json ({len(LEARNING_RESOURCES)} resources)")

# skill_categories.json — classify skills into categories
SKILL_CATEGORIES = {
    "Programming":     ["Python", "Java", "C++", "Go", "Rust", "TypeScript", "Kotlin", "Scala"],
    "Web":             ["React", "REST APIs", "GraphQL", "HTML5", "CSS3", "Vue.js", "Webpack", "TypeScript"],
    "Data/DB":         ["SQL", "PostgreSQL", "MongoDB", "Spark", "Airflow", "Kafka", "Power BI", "Tableau"],
    "ML/AI":           ["Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "MLOps",
                        "Feature Engineering", "Statistics", "LangChain", "Scikit-learn"],
    "Cloud/DevOps":    ["AWS", "Azure", "GCP", "Terraform", "Docker", "Kubernetes", "CI/CD", "Microservices"],
    "Security":        ["Cybersecurity", "Networking", "Linux", "Ethical Hacking", "Penetration Testing"],
    "Architecture":    ["System Design", "Microservices", "Event-Driven Architecture", "API Gateway"],
}
with open(os.path.join(OUT_DIR, "skill_categories.json"), "w") as f:
    json.dump(SKILL_CATEGORIES, f, indent=2)
print(f"[SAVED] skill_categories.json")

# career_paths.json — role progression tracks
CAREER_PATHS = {
    "Software Engineer":          ["Junior Developer","Software Engineer","Senior Engineer","Tech Lead","Engineering Manager","VP Engineering"],
    "Data Scientist":             ["Junior Data Scientist","Data Scientist","Senior Data Scientist","Lead Data Scientist","Principal Data Scientist","Chief Data Officer"],
    "Machine Learning Engineer":  ["ML Engineer (L1)","ML Engineer","Senior ML Engineer","Staff ML Engineer","Principal ML Engineer","Director of AI"],
    "Frontend Developer":         ["Junior Frontend Dev","Frontend Developer","Senior Frontend Dev","Lead Frontend Engineer","Principal Engineer","CTO"],
    "Backend Developer":          ["Junior Backend Dev","Backend Developer","Senior Backend Dev","Lead Backend Engineer","Principal Engineer","CTO"],
    "DevOps Engineer":            ["DevOps Engineer (L1)","DevOps Engineer","Senior DevOps","Lead DevOps","Platform Engineer","VP Infrastructure"],
    "Cybersecurity Analyst":      ["Security Analyst (L1)","Cybersecurity Analyst","Senior Security Analyst","Security Architect","CISO"],
    "Cloud Solutions Architect":  ["Cloud Engineer","Cloud Architect","Senior Cloud Architect","Principal Architect","VP Cloud"],
    "Database Administrator":     ["Junior DBA","Database Administrator","Senior DBA","Lead DBA","Data Architect"],
    "Mobile App Developer":       ["Junior Mobile Dev","Mobile Developer","Senior Mobile Dev","Lead Mobile Dev","Principal Engineer"],
}

ROLE_TRANSITIONS = {
    "Software Engineer":         ["Backend Developer","DevOps Engineer","Cloud Solutions Architect"],
    "Data Scientist":            ["Machine Learning Engineer","Backend Developer","Database Administrator"],
    "Machine Learning Engineer": ["Data Scientist","Backend Developer","DevOps Engineer"],
    "Frontend Developer":        ["Mobile App Developer","Software Engineer"],
    "Backend Developer":         ["Software Engineer","DevOps Engineer","Cloud Solutions Architect"],
    "DevOps Engineer":           ["Cloud Solutions Architect","Backend Developer","Database Administrator"],
    "Cybersecurity Analyst":     ["Cloud Solutions Architect","Database Administrator"],
    "Cloud Solutions Architect": ["DevOps Engineer","Backend Developer"],
    "Database Administrator":    ["Backend Developer","Data Scientist"],
    "Mobile App Developer":      ["Frontend Developer","Software Engineer"],
}

with open(os.path.join(OUT_DIR, "career_paths.json"), "w") as f:
    json.dump({"career_paths": CAREER_PATHS, "role_transitions": ROLE_TRANSITIONS}, f, indent=2)
print(f"[SAVED] career_paths.json ({len(CAREER_PATHS)} roles)")

# ── 7. Save stats for reference ───────────────────────────────────────────────
stats = {
    "dataset_size":     len(df),
    "feature_count":    len(FEATURE_COLS),
    "roles":            roles,
    "top_skills":       ALL_SKILLS_SET,
    "best_model":       best_name,
    "accuracy":         round(results[best_name]["acc"], 4),
    "f1_score":         round(results[best_name]["f1"],  4),
    "roc_auc":          round(results[best_name]["auc"], 4),
}
with open(os.path.join(OUT_DIR, "training_stats.json"), "w") as f:
    json.dump(stats, f, indent=2)

print(f"\n{'='*60}")
print(f"  Training complete! Best model: {best_name}")
print(f"  Accuracy: {stats['accuracy']}  F1: {stats['f1_score']}  AUC: {stats['roc_auc']}")
print(f"  Models saved to: {OUT_DIR}")
print(f"{'='*60}")
