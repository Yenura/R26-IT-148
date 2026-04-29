"""
Component 4: Skill Gap Analysis & Career Development
ML Training Script

Dataset: AI_Resume_Screening.csv
- Skills, Experience, Education, Certifications, Job Role, AI Score, Recruiter Decision
- Uses skills gap identification + classification model
"""

import pandas as pd
import numpy as np
import os
import json
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    f1_score, roc_auc_score, precision_score, recall_score
)
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# ─────────────────────────────────────────────
# 1. PATHS
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "Data_set", "AI_Resume_Screening.csv")
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")
REPORTS_DIR = os.path.join(BASE_DIR, "..", "reports")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 2. JOB ROLE SKILL REQUIREMENTS (Ground Truth)
# ─────────────────────────────────────────────
JOB_REQUIREMENTS = {
    "Data Scientist": {
        "required": ["Python", "Machine Learning", "SQL", "Deep Learning"],
        "optional": ["TensorFlow", "Pytorch", "NLP"],
        "min_experience": 2,
        "preferred_education": ["PhD", "M.Tech", "MBA"]
    },
    "AI Researcher": {
        "required": ["Python", "TensorFlow", "NLP", "Pytorch"],
        "optional": ["Deep Learning", "Machine Learning"],
        "min_experience": 1,
        "preferred_education": ["PhD", "M.Tech"]
    },
    "Software Engineer": {
        "required": ["Java", "SQL", "C++"],
        "optional": ["React", "Python"],
        "min_experience": 1,
        "preferred_education": ["B.Tech", "B.Sc", "M.Tech"]
    },
    "Cybersecurity Analyst": {
        "required": ["Cybersecurity", "Networking", "Linux"],
        "optional": ["Ethical Hacking"],
        "min_experience": 1,
        "preferred_education": ["B.Tech", "M.Tech", "B.Sc"]
    }
}

SKILL_CATEGORIES = {
    "Technical": ["Python", "Java", "C++", "SQL", "React", "Linux"],
    "ML/AI": ["TensorFlow", "Pytorch", "Machine Learning", "Deep Learning", "NLP"],
    "Security": ["Cybersecurity", "Networking", "Ethical Hacking", "Linux"],
}

LEARNING_RESOURCES = {
    "Python": {
        "course": "Python for Everybody - Coursera",
        "url": "https://coursera.org/specializations/python",
        "duration": "3 months",
        "level": "Beginner"
    },
    "Machine Learning": {
        "course": "Machine Learning Specialization - Andrew Ng",
        "url": "https://coursera.org/specializations/machine-learning-introduction",
        "duration": "3 months",
        "level": "Intermediate"
    },
    "Deep Learning": {
        "course": "Deep Learning Specialization - deeplearning.ai",
        "url": "https://coursera.org/specializations/deep-learning",
        "duration": "4 months",
        "level": "Intermediate"
    },
    "TensorFlow": {
        "course": "TensorFlow Developer Certificate - Google",
        "url": "https://coursera.org/professional-certificates/tensorflow-in-practice",
        "duration": "2 months",
        "level": "Intermediate"
    },
    "Pytorch": {
        "course": "PyTorch for Deep Learning - Udemy",
        "url": "https://pytorch.org/tutorials",
        "duration": "2 months",
        "level": "Intermediate"
    },
    "NLP": {
        "course": "NLP Specialization - deeplearning.ai",
        "url": "https://coursera.org/specializations/natural-language-processing",
        "duration": "3 months",
        "level": "Advanced"
    },
    "SQL": {
        "course": "SQL for Data Science - Coursera",
        "url": "https://coursera.org/learn/sql-for-data-science",
        "duration": "1 month",
        "level": "Beginner"
    },
    "Java": {
        "course": "Java Programming Masterclass - Udemy",
        "url": "https://udemy.com/course/java-the-complete-java-developer-course",
        "duration": "2 months",
        "level": "Beginner"
    },
    "React": {
        "course": "React - The Complete Guide - Udemy",
        "url": "https://udemy.com/course/react-the-complete-guide-incl-redux",
        "duration": "2 months",
        "level": "Intermediate"
    },
    "C++": {
        "course": "C++ Programming Course - freeCodeCamp",
        "url": "https://freecodecamp.org/news/learn-c-plus-plus-in-31-hours",
        "duration": "2 months",
        "level": "Beginner"
    },
    "Cybersecurity": {
        "course": "Google Cybersecurity Professional Certificate",
        "url": "https://coursera.org/professional-certificates/google-cybersecurity",
        "duration": "6 months",
        "level": "Beginner"
    },
    "Networking": {
        "course": "CompTIA Network+ Study Course",
        "url": "https://comptia.org/certifications/network",
        "duration": "3 months",
        "level": "Beginner"
    },
    "Ethical Hacking": {
        "course": "Certified Ethical Hacker (CEH) - EC-Council",
        "url": "https://eccouncil.org/train-certify/certified-ethical-hacker-ceh",
        "duration": "4 months",
        "level": "Advanced"
    },
    "Linux": {
        "course": "Linux Foundation Certified SysAdmin",
        "url": "https://training.linuxfoundation.org/certification/lfcs",
        "duration": "2 months",
        "level": "Intermediate"
    }
}

# ─────────────────────────────────────────────
# 3. DATA LOADING & PREPROCESSING
# ─────────────────────────────────────────────
print("=" * 60)
print("COMPONENT 4: SKILL GAP ANALYSIS - ML TRAINING")
print("=" * 60)
print(f"\n[1] Loading dataset from: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

print(f"    Dataset shape: {df.shape}")
print(f"    Columns: {list(df.columns)}")
print(f"\n    Sample rows:\n{df.head(3).to_string()}")

# Clean column names
df.columns = df.columns.str.strip()

# Parse skills list
df['Skills_List'] = df['Skills'].apply(
    lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
)
df['Skill_Count'] = df['Skills_List'].apply(len)

# Binary encode decision
df['Decision_Binary'] = (df['Recruiter Decision'] == 'Hire').astype(int)

# Normalize AI Score to 0-1
df['AI_Score_Norm'] = df['AI Score (0-100)'] / 100.0

# Education encoding
edu_map = {'PhD': 5, 'M.Tech': 4, 'MBA': 3, 'B.Tech': 2, 'B.Sc': 1}
df['Education_Enc'] = df['Education'].map(edu_map).fillna(2)

# Certification encoding
df['Has_Cert'] = (df['Certifications'] != 'None').astype(int)

print(f"\n    Job Roles: {df['Job Role'].value_counts().to_dict()}")
print(f"    Hire/Reject: {df['Recruiter Decision'].value_counts().to_dict()}")

# ─────────────────────────────────────────────
# 4. SKILL GAP COMPUTATION
# ─────────────────────────────────────────────
print("\n[2] Computing Skill Gaps...")

def compute_skill_gap(row):
    """
    Returns:
      - gap_score: 0-1 (1 = no gap, 0 = full gap)
      - missing_required: list of missing required skills
      - missing_optional: list of missing optional skills
      - skill_match_pct: percentage of required skills matched
    """
    role = row['Job Role']
    candidate_skills = set([s.lower() for s in row['Skills_List']])
    
    if role not in JOB_REQUIREMENTS:
        return 0.5, [], [], 50.0
    
    req = JOB_REQUIREMENTS[role]
    required_skills = [s.lower() for s in req['required']]
    optional_skills = [s.lower() for s in req['optional']]
    
    missing_req = [s for s in required_skills if s not in candidate_skills]
    missing_opt = [s for s in optional_skills if s not in candidate_skills]
    
    if len(required_skills) > 0:
        match_pct = (len(required_skills) - len(missing_req)) / len(required_skills) * 100
    else:
        match_pct = 100.0
    
    # Gap score: weighted (required=70%, optional=30%)
    req_score = (len(required_skills) - len(missing_req)) / max(len(required_skills), 1)
    opt_score = (len(optional_skills) - len(missing_opt)) / max(len(optional_skills), 1)
    gap_score = 0.7 * req_score + 0.3 * opt_score
    
    # Experience gap
    min_exp = req['min_experience']
    exp_ok = row['Experience (Years)'] >= min_exp
    
    # Combined
    final_gap = 0.8 * gap_score + 0.2 * float(exp_ok)
    
    return final_gap, missing_req, missing_opt, match_pct

results = df.apply(compute_skill_gap, axis=1)
df['Gap_Score'] = results.apply(lambda x: x[0])
df['Missing_Required'] = results.apply(lambda x: x[1])
df['Missing_Optional'] = results.apply(lambda x: x[2])
df['Skill_Match_Pct'] = results.apply(lambda x: x[3])

# Gap Severity Level
def gap_severity(gap_score):
    if gap_score >= 0.85:
        return 'Low'
    elif gap_score >= 0.60:
        return 'Medium'
    else:
        return 'High'

df['Gap_Severity'] = df['Gap_Score'].apply(gap_severity)
print(f"    Gap Severity Distribution:\n{df['Gap_Severity'].value_counts().to_string()}")

# ─────────────────────────────────────────────
# 5. FEATURE ENGINEERING FOR ML MODEL
# ─────────────────────────────────────────────
print("\n[3] Feature Engineering...")

# One-hot encode job roles
role_dummies = pd.get_dummies(df['Job Role'], prefix='role')

# One-hot encode skills
all_skills = ['Python', 'Java', 'C++', 'SQL', 'React', 'Linux',
              'TensorFlow', 'Pytorch', 'Machine Learning', 'Deep Learning', 'NLP',
              'Cybersecurity', 'Networking', 'Ethical Hacking']

for skill in all_skills:
    df[f'skill_{skill.lower().replace(" ", "_").replace("+", "plus")}'] = (
        df['Skills_List'].apply(lambda s: int(skill in s))
    )

skill_cols = [c for c in df.columns if c.startswith('skill_')]

feature_cols = (
    ['Experience (Years)', 'Education_Enc', 'Has_Cert',
     'Skill_Count', 'AI_Score_Norm', 'Gap_Score', 'Skill_Match_Pct']
    + list(role_dummies.columns)
    + skill_cols
)

X = pd.concat([df[['Experience (Years)', 'Education_Enc', 'Has_Cert',
                    'Skill_Count', 'AI_Score_Norm', 'Gap_Score', 'Skill_Match_Pct']],
               role_dummies, df[skill_cols]], axis=1)
y = df['Decision_Binary']

print(f"    Feature matrix shape: {X.shape}")
print(f"    Target distribution: {y.value_counts().to_dict()}")

# ─────────────────────────────────────────────
# 6. MODEL TRAINING
# ─────────────────────────────────────────────
print("\n[4] Training Models...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=150, max_depth=8, min_samples_split=5,
        random_state=42, class_weight='balanced'
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=100, learning_rate=0.1, max_depth=5,
        random_state=42
    ),
    "Logistic Regression": LogisticRegression(
        max_iter=1000, random_state=42, class_weight='balanced'
    )
}

evaluation_results = {}
best_model_name = None
best_f1 = 0.0

for name, model in models.items():
    print(f"\n    --- {name} ---")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    try:
        auc = roc_auc_score(y_test, y_prob)
    except Exception:
        auc = 0.0
    
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='f1_weighted')
    
    evaluation_results[name] = {
        "accuracy": round(acc, 4),
        "f1_score": round(f1, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "roc_auc": round(auc, 4),
        "cv_mean": round(cv_scores.mean(), 4),
        "cv_std": round(cv_scores.std(), 4),
        "classification_report": classification_report(y_test, y_pred)
    }
    
    print(f"      Accuracy:  {acc:.4f}")
    print(f"      F1-Score:  {f1:.4f}")
    print(f"      Precision: {prec:.4f}")
    print(f"      Recall:    {rec:.4f}")
    print(f"      ROC-AUC:   {auc:.4f}")
    print(f"      CV Mean:   {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    if f1 > best_f1:
        best_f1 = f1
        best_model_name = name

print(f"    [OK] Best Model: {best_model_name} (F1={best_f1:.4f})")

# ─────────────────────────────────────────────
# 7. SAVE BEST MODEL
# ─────────────────────────────────────────────
print("\n[5] Saving Models & Artifacts...")

best_model = models[best_model_name]
joblib.dump(best_model, os.path.join(MODELS_DIR, "skill_gap_classifier.pkl"))
joblib.dump(X.columns.tolist(), os.path.join(MODELS_DIR, "feature_columns.pkl"))
joblib.dump(role_dummies.columns.tolist(), os.path.join(MODELS_DIR, "role_columns.pkl"))

# Save all models
for name, model in models.items():
    fname = name.lower().replace(" ", "_") + "_model.pkl"
    joblib.dump(model, os.path.join(MODELS_DIR, fname))

# Save job requirements & resources
with open(os.path.join(MODELS_DIR, "job_requirements.json"), 'w') as f:
    json.dump(JOB_REQUIREMENTS, f, indent=2)

with open(os.path.join(MODELS_DIR, "learning_resources.json"), 'w') as f:
    json.dump(LEARNING_RESOURCES, f, indent=2)

with open(os.path.join(MODELS_DIR, "skill_categories.json"), 'w') as f:
    json.dump(SKILL_CATEGORIES, f, indent=2)

print(f"    [OK] Models saved to: {MODELS_DIR}")

# ─────────────────────────────────────────────
# 8. EVALUATION REPORT
# ─────────────────────────────────────────────
print("\n[6] Generating Evaluation Report...")

# Confusion matrix plot for best model
best_model_obj = models[best_model_name]
y_pred_best = best_model_obj.predict(X_test)
cm = confusion_matrix(y_test, y_pred_best)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Plot 1: Confusion Matrix
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Reject', 'Hire'],
            yticklabels=['Reject', 'Hire'],
            ax=axes[0])
axes[0].set_title(f'Confusion Matrix\n{best_model_name}')
axes[0].set_ylabel('Actual')
axes[0].set_xlabel('Predicted')

# Plot 2: Model Comparison (F1)
model_names = list(evaluation_results.keys())
f1_scores = [evaluation_results[m]['f1_score'] for m in model_names]
colors = ['#4CAF50' if n == best_model_name else '#2196F3' for n in model_names]
axes[1].bar(model_names, f1_scores, color=colors, edgecolor='white', linewidth=1.5)
axes[1].set_title('Model Comparison (F1-Score)')
axes[1].set_ylabel('F1 Score')
axes[1].set_ylim(0, 1.1)
for i, v in enumerate(f1_scores):
    axes[1].text(i, v + 0.01, f'{v:.3f}', ha='center', fontweight='bold')

# Plot 3: Feature Importance (if RF)
if best_model_name == "Random Forest" or best_model_name == "Gradient Boosting":
    importances = best_model_obj.feature_importances_
    indices = np.argsort(importances)[::-1][:12]
    feat_names = [X.columns[i][:20] for i in indices]
    axes[2].barh(feat_names[::-1], importances[indices[::-1]], color='#9C27B0')
    axes[2].set_title('Top Feature Importances')
    axes[2].set_xlabel('Importance')
else:
    coef = np.abs(best_model_obj.coef_[0])
    indices = np.argsort(coef)[::-1][:12]
    feat_names = [X.columns[i][:20] for i in indices]
    axes[2].barh(feat_names[::-1], coef[indices[::-1]], color='#9C27B0')
    axes[2].set_title('Top Feature Importances (|Coef|)')
    axes[2].set_xlabel('|Coefficient|')

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, 'model_evaluation.png'), dpi=120, bbox_inches='tight')
plt.close()
print(f"    [OK] Evaluation plot saved")

# Plot 4: Gap Distribution
fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))
colors_map = {'Low': '#4CAF50', 'Medium': '#FF9800', 'High': '#F44336'}
severity_counts = df['Gap_Severity'].value_counts()
axes2[0].pie(severity_counts, labels=severity_counts.index,
             colors=[colors_map[s] for s in severity_counts.index],
             autopct='%1.1f%%', startangle=90, pctdistance=0.85)
axes2[0].set_title('Skill Gap Severity Distribution')

role_gap = df.groupby('Job Role')['Gap_Score'].mean()
axes2[1].bar(role_gap.index, role_gap.values, color=['#2196F3', '#9C27B0', '#FF5722', '#009688'])
axes2[1].set_title('Average Gap Score by Job Role')
axes2[1].set_ylabel('Avg Gap Score (Higher = Better Match)')
axes2[1].set_ylim(0, 1)
for i, v in enumerate(role_gap.values):
    axes2[1].text(i, v + 0.01, f'{v:.2f}', ha='center', fontweight='bold')
axes2[1].tick_params(axis='x', rotation=15)

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, 'gap_distribution.png'), dpi=120, bbox_inches='tight')
plt.close()

# Save JSON report
report = {
    "best_model": best_model_name,
    "best_f1": best_f1,
    "models": evaluation_results,
    "dataset_info": {
        "total_records": len(df),
        "job_roles": df['Job Role'].value_counts().to_dict(),
        "hire_rate": float(df['Decision_Binary'].mean()),
        "avg_skill_match_pct": float(df['Skill_Match_Pct'].mean()),
        "gap_severity_distribution": df['Gap_Severity'].value_counts().to_dict()
    }
}

with open(os.path.join(REPORTS_DIR, "evaluation_report.json"), 'w') as f:
    json.dump(report, f, indent=2)

print(f"    [OK] Evaluation report saved")
print("\n" + "=" * 60)
print("[DONE] ML TRAINING COMPLETE!")
print(f"   Best Model: {best_model_name}")
print(f"   F1-Score:   {best_f1:.4f}")
print(f"   Models dir: {MODELS_DIR}")
print(f"   Reports:    {REPORTS_DIR}")
print("=" * 60)
