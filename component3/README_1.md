# Interview-Driven Candidate Ranking Aligned with Employer Requirements

**Project ID:** R26-IT-148 | **Component:** 3  
**Student:** Perera K.G.S.N. | **Student ID:** IT22027610  
**Supervisor:** Mrs. Buddhima Athanavake | **Co-Supervisor:** Mrs. Narmada Gamage  
**Degree:** B.Sc. (Hons) in Information Technology — Specialised in IT  
**Institution:** Sri Lanka Institute of Information Technology (SLIIT), Faculty of Computing

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Research Objectives](#3-research-objectives)
4. [Job Roles Covered](#4-job-roles-covered)
5. [Folder Structure](#5-folder-structure)
6. [Dataset Description](#6-dataset-description)
7. [Installation Guide](#7-installation-guide)
8. [How to Run](#8-how-to-run)
9. [Dashboard Guide](#9-dashboard-guide)
10. [Model Description](#10-model-description)
11. [Evaluation Results](#11-evaluation-results)
12. [Technologies Used](#12-technologies-used)
13. [Research Questions](#13-research-questions)
14. [References](#14-references)

---

## 1. Project Overview

This repository contains **Component 3** of the **AI-Driven Recruitment Ecosystem (R26-IT-148)**, a collaborative final-year research project developed at SLIIT Faculty of Computing.

The full ecosystem automates the end-to-end IT recruitment pipeline across four integrated components:

| Component | Student ID | Research Component |
|---|---|---|
| 1 | IT22094872 — Dulnith K.D. | Automated Semantic Resume Screening and Role Classification |
| 2 | IT22306272 — Y.S. Karunanayaka | Role-Based Automated Interview Generation and Scoring (RAIGS) |
| **3** | **IT22027610 — Perera K.G.S.N.** | **Interview-Driven Candidate Ranking Aligned with Employer Requirements** |
| 4 | IT22089236 — Perera D.T.D. | Personalised Skill Gap Identification and Improvement Guidance |

### What Component 3 Does

Component 3 is the **decision engine** of the recruitment ecosystem. It receives structured candidate feature vectors from Component 1 (CV analysis) and automated interview performance scores from Component 2 (interview evaluation), combines them through a job-specific weighted average model, and produces a ranked candidate shortlist complete with fairness audit information and per-candidate explanations for the hiring organisation.

The core contribution is the **Candidate Suitability Score (CSS)** model:

```
CSS(c) = W_CV × S_cv(c) + W_INT × S_int(c)
```

Where the default weights (W_CV = 0.40, W_INT = 0.60) are grounded in Schmidt and Hunter's (1998) meta-analysis of 85 years of personnel selection research, which established structured interviews as the strongest predictor of job performance (r = 0.51).

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 AI-Driven Recruitment Ecosystem              │
│                                                             │
│  Component 1        Component 2        Component 3          │
│  CV Screening  ───► Interview     ───► Candidate    ───►   │
│  & Extraction       Scoring            Ranking              │
│                                            │                │
│                                            ▼                │
│                                       Component 4           │
│                                       Skill Gap             │
│                                       Guidance              │
└─────────────────────────────────────────────────────────────┘
```

### Component 3 Internal Pipeline

```
Inputs:
  ├── CV Feature Vectors (from Component 1)
  │     S_edu, S_exp, S_skill
  ├── Interview Scores (from Component 2)
  │     P_mcq, P_desc, P_code
  └── Job Requirement Profile (employer configured)

Pipeline:
  Step 1 → Hard Filter Gate (Equation 1)
               Eliminates candidates below minimum thresholds
               Failed candidates → Component 4

  Step 2 → CV Score Computation (Equations 2–5)
               S_edu, S_exp, S_skill → S_cv

  Step 3 → Interview Score Computation (Equations 6–7)
               P_mcq, P_desc, P_code → S_int

  Step 4 → CSS Master Score (Equation 8)
               CSS = W_CV × S_cv + W_INT × S_int

  Step 5 → Fairness Audit (Equations 9–10)
               Demographic Parity + Equal Opportunity
               FA*IR re-ranking if violation detected

  Step 6 → SHAP Explainability (Equation 11)
               CSS(c) = φ₀ + Σφᵢ per candidate

Output:
  └── Ranked Shortlist (JSON + Dashboard)
        Rank | CSS | Sub-scores | SHAP values | Fairness status
```

---

## 3. Research Objectives

### Main Objective

Design, build, and evaluate a job-specific, interview-driven candidate ranking system that combines employer-defined job requirement profiles with automated CV classification features and automated interview performance scores through a weighted average model — producing a ranked candidate shortlist that is transparent, adapts to different role types, and demonstrates measurably better fairness properties than existing MCDM-based approaches.

### Sub-Objectives

- Implement the CSS model integrating all six candidate features from Components 1 and 2
- Implement a hard filter gate eliminating candidates below mandatory thresholds
- Develop employer-configurable job requirement profiles with per-skill importance weights
- Integrate LambdaMART learning-to-rank for weight optimisation sensitivity analysis
- Implement fairness auditing using Demographic Parity and Equal Opportunity metrics
- Implement SHAP-based per-candidate explainability
- Evaluate through ablation study, weight sensitivity analysis, fairness testing, and metric comparison

### Research Questions

| RQ | Question |
|---|---|
| RQ1 | Does combining CV + interview scores produce better ranking quality than either alone? |
| RQ2 | Does role-specific employer weighting outperform fixed-weight MCDM approaches? |
| RQ3 | Does LambdaMART sensitivity confirm top-3 stability across weight variations of ±0.10? |
| RQ4 | Can fairness constraints be enforced without meaningful NDCG@5 degradation? |
| RQ5 | Do SHAP explanations improve HR professional understanding and trust in rankings? |

---

## 4. Job Roles Covered

This component covers the following 10 IT career roles:

| # | Role | Primary Evaluation Focus |
|---|---|---|
| 1 | 🖥️ Software Engineer | Coding ability + skill match |
| 2 | 📊 Data Scientist | Analytical thinking + descriptive answers |
| 3 | 🤖 Machine Learning Engineer | Coding + ML knowledge + descriptive |
| 4 | ⚙️ DevOps Engineer | Coding + infrastructure skills |
| 5 | 🔒 Cybersecurity Analyst | Descriptive + security knowledge |
| 6 | ☁️ Cloud Solutions Architect | Descriptive + architecture experience |
| 7 | 🗄️ Database Administrator | Coding + descriptive + skill match |
| 8 | 🎨 Frontend Developer | Coding + skill match |
| 9 | 🔧 Backend Developer | Coding + skill match |
| 10 | 📱 Mobile App Developer | Coding + skill match (iOS/Android/Flutter/React Native) |

Each role has independently configured:
- Interview question type weights (MCQ / Descriptive / Coding)
- CV component weights (Education / Experience / Skills)
- Hard filter minimum thresholds
- Required years of experience

---

## 5. Folder Structure

```
component3/
│
├── README.md                          ← You are here
│
├── run_all.py                         ← Master pipeline script (run this first)
│
├── data/
│   ├── __init__.py
│   ├── role_configs.py                ← All 10 role configurations and weights
│   └── generate_data.py              ← Dataset generation script
│
├── engine/
│   ├── __init__.py
│   └── css_engine.py                  ← CSS scoring engine (Equations 1–8)
│
├── ltr/
│   ├── __init__.py
│   └── lambdamart_model.py            ← LambdaMART LTR + ablation + sensitivity
│
├── fairness/
│   ├── __init__.py
│   └── fairness_audit.py              ← Fairness audit module (Equations 9–10)
│
├── explainability/
│   ├── __init__.py
│   └── shap_explainer.py              ← SHAP explainability (Equation 11)
│
├── dashboard/
│   ├── __init__.py
│   └── app.py                         ← Streamlit employer dashboard
│
├── datasets/                          ← Created automatically by run_all.py
│   ├── candidates_full.csv            ← 6,000 candidate records (all roles)
│   ├── train_set.csv                  ← 3,600 records for model training
│   ├── val_set.csv                    ←   900 records for validation
│   ├── test_set.csv                   ← 1,500 records for final evaluation
│   ├── fairness_test_set.csv          ← 5,000 records (balanced M/F per role)
│   ├── job_requirements.csv           ←    10 job requirement profiles
│   ├── role_Software_Engineer.csv     ←   600 role-specific records
│   ├── role_Data_Scientist.csv
│   ├── role_Machine_Learning_Engineer.csv
│   ├── role_DevOps_Engineer.csv
│   ├── role_Cybersecurity_Analyst.csv
│   ├── role_Cloud_Solutions_Architect.csv
│   ├── role_Database_Administrator.csv
│   ├── role_Frontend_Developer.csv
│   ├── role_Backend_Developer.csv
│   └── role_Mobile_App_Developer.csv
│
├── models/                            ← Created automatically by run_all.py
│   └── lambdamart_model.pkl           ← Trained LambdaMART model
│
├── results/                           ← Created automatically by run_all.py
│   ├── ablation_study.csv             ← Ablation study comparison results
│   ├── fairness_report.csv            ← Fairness metrics per role
│   ├── weight_sensitivity.csv         ← Weight configuration sensitivity
│   ├── feature_importance.csv         ← LambdaMART feature importance
│   ├── shap_Software_Engineer.csv     ← SHAP values per role
│   ├── shap_Data_Scientist.csv
│   ├── shap_*.csv                     ← (10 files total)
│   └── charts/
│       ├── shap_summary_Software_Engineer.png
│       ├── shap_summary_*.png         ← Feature importance charts (10 files)
│       ├── waterfall_top1_Software_Engineer.png
│       └── waterfall_top1_*.png       ← Top candidate SHAP waterfall (10 files)
│
└── venv/                              ← Python virtual environment (not committed)
```

> **Note:** The `datasets/`, `models/`, and `results/` directories and all their contents are generated automatically when you run `python run_all.py`. You do not need to create or populate them manually.

---

## 6. Dataset Description

The datasets used in this research contain structured candidate records for 10 IT job roles. Each record represents one candidate's feature profile for a specific role.

### Dataset Statistics

| Dataset | Records | Description |
|---|---|---|
| `candidates_full.csv` | 6,000 | Complete dataset across all 10 roles (600 per role) |
| `train_set.csv` | 3,600 | Training set — 60% of total, stratified per role |
| `val_set.csv` | 900 | Validation set — 15% of total, used for early stopping |
| `test_set.csv` | 1,500 | Test set — 25% of total, held out for final evaluation |
| `fairness_test_set.csv` | 5,000 | Demographically balanced evaluation set (500M + 500F per role) |
| `job_requirements.csv` | 10 | Employer job requirement profiles, one per role |
| `role_*.csv` (×10) | 600 each | Individual role datasets for per-role analysis |

### Dataset Columns

| Column | Type | Description |
|---|---|---|
| `candidate_id` | string | Unique candidate identifier (e.g. SE00001) |
| `job_role` | string | Role key (e.g. Software_Engineer) |
| `job_role_display` | string | Human-readable role name |
| `gender` | string | M / F — used for fairness audit only |
| `age_group` | string | Age bracket — used for fairness audit only |
| `edu_level` | int | 1=Diploma, 2=BSc, 3=MSc, 4=PhD |
| `edu_level_name` | string | Education level label |
| `years_experience` | float | Total years of professional experience |
| `edu_relevance` | float | Relevance of degree field to job role (0–1) |
| `P_mcq` | float | MCQ interview performance score (0–1) |
| `P_desc` | float | Descriptive interview performance score (0–1) |
| `P_code` | float | Coding interview performance score (0–1) |
| `S_edu` | float | Computed education sub-score (Equation 2) |
| `S_exp` | float | Computed experience sub-score (Equation 3) |
| `S_skill` | float | Skill match score (0–1) |
| `S_cv` | float | Computed CV composite score (Equation 5) |
| `S_int` | float | Computed interview composite score (Equation 7) |
| `CSS` | float | Candidate Suitability Score (Equation 8) |
| `passed_hard_filter` | int | 1 = passed, 0 = failed hard filter |
| `relevance_label` | int | Ground truth label: 0=Not Suitable → 3=Highly Suitable |
| `w_edu, w_exp, w_skill` | float | CV weights used for this role |
| `w_mcq, w_desc, w_code` | float | Interview weights used for this role |
| `W_CV, W_INT` | float | Master CSS weights used |

### Relevance Label Distribution (Approximate per Role)

| Label | Meaning | Approximate Proportion |
|---|---|---|
| 0 | Not Suitable | ~4% |
| 1 | Marginal | ~30% |
| 2 | Suitable | ~46% |
| 3 | Highly Suitable | ~20% |

---

## 7. Installation Guide

### Prerequisites

- Python 3.10 or higher
- pip package manager
- VS Code (recommended) or any Python IDE

### Step 1 — Clone or Download the Repository

Download and extract the project folder, or clone via Git:

```bash
git clone <repository-url>
cd component3
```

### Step 2 — Create Virtual Environment

```bash
python -m venv venv
```

### Step 3 — Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal line.

### Step 4 — Install Required Packages

```bash
pip install numpy pandas scikit-learn lightgbm shap matplotlib streamlit faker scipy plotly
```

This takes approximately 2–5 minutes depending on your internet speed.

### Step 5 — Select Python Interpreter in VS Code

- Press `Ctrl+Shift+P`
- Type: `Python: Select Interpreter`
- Select the interpreter showing `venv` in the path

---

## 8. How to Run

### Option A — Run Full Pipeline (Recommended First Run)

```bash
python run_all.py
```

This single command executes the complete pipeline:

| Step | What Happens | Output |
|---|---|---|
| Step 1 | Dataset generation for all 10 roles | `datasets/` folder populated |
| Step 2 | CSS engine validation (Equations 1–8) | Console output |
| Step 3 | LambdaMART training + ablation study | `results/ablation_study.csv`, `models/` |
| Step 4 | Weight sensitivity analysis | `results/weight_sensitivity.csv` |
| Step 5 | Fairness audit for all 10 roles | `results/fairness_report.csv` |
| Step 6 | SHAP explainability + chart generation | `results/shap_*.csv`, `results/charts/` |
| Step 7 | Summary report printed to console | — |

**Expected runtime:** 6–15 seconds

### Option B — Launch Dashboard Only (After Running Pipeline Once)

```bash
streamlit run dashboard/app.py
```

Browser opens automatically at: **http://localhost:8501**

### Option C — Run Individual Modules

```bash
# Generate datasets only
python data/generate_data.py

# Run CSS engine tests only
python engine/css_engine.py

# Train LambdaMART only
python ltr/lambdamart_model.py

# Run fairness audit only
python fairness/fairness_audit.py

# Run SHAP explainability only
python explainability/shap_explainer.py
```

### Troubleshooting

| Error | Solution |
|---|---|
| `ModuleNotFoundError` | Ensure venv is active: `venv\Scripts\activate` |
| `streamlit: command not found` | Run `pip install streamlit` |
| Execution policy error (Windows) | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `datasets/ not found` | Run `python run_all.py` first |
| Port 8501 already in use | Run `streamlit run dashboard/app.py --server.port 8502` |

---

## 9. Dashboard Guide

The Streamlit dashboard provides a complete employer-facing interface with five tabs.

### Sidebar — Employer Configuration Panel

The sidebar allows the employer to configure the job requirements in real time:

- **Job Role** — select from 10 IT roles
- **Minimum Education** — hard filter threshold (Diploma / BSc / MSc / PhD)
- **Minimum Experience** — hard filter threshold in years
- **CV Weights** — sliders for w_edu and w_exp (w_skill auto-calculated to ensure sum = 1.0)
- **Interview Weights** — sliders for w_mcq and w_desc (w_code auto-calculated)
- **Master Weights** — W_CV slider (W_INT auto-calculated, constraint W_CV + W_INT = 1.0)
- **Shortlist Size** — number of top candidates to display

All weight changes trigger **real-time re-ranking** of candidates.

### Tab 1 — Ranked Shortlist 🏆

Shows the top-N candidates ranked by CSS score for the selected role and weight configuration.

- KPI metrics: Total Applicants, Passed Filter, Filtered Out, Shortlisted, Top CSS
- Expandable candidate cards with full score breakdown
- Visual CSS progress bar (green ≥ 0.75, orange ≥ 0.55, red < 0.55)
- Medal indicators for top 3 candidates (🥇🥈🥉)
- Expandable section listing candidates who failed the hard filter with specific reasons

### Tab 2 — SHAP Explanations 🔍

Displays per-candidate explanations implementing Equation 11: CSS(c) = φ₀ + Σφᵢ

- Feature importance summary chart (mean |SHAP| across all candidates)
- Waterfall charts for top 5 candidates showing individual feature contributions
- SHAP values table per candidate with effect direction indicators

### Tab 3 — Fairness Audit ⚖️

Displays fairness evaluation results for the selected role.

- Demographic Parity difference with FAIR / UNFAIR badge
- Equal Opportunity difference
- Male vs Female CSS score distribution charts
- All-roles fairness summary table

### Tab 4 — Model Evaluation 📊

Displays comparative evaluation results.

- Ablation study bar charts (NDCG@5 and MAP across 5 configurations)
- Weight sensitivity analysis (NDCG@5 and Top-3 Stability across 4 configurations)
- LambdaMART feature importance chart

### Tab 5 — Dataset Explorer 📂

Allows inspection of the underlying datasets.

- Candidates per role distribution chart
- Relevance label distribution
- CSS score distribution for selected role
- Raw data table for selected role
- Job requirements table for all 10 roles

---

## 10. Model Description

### 10.1 CSS Weighted Average Model (Primary Contribution)

The CSS model is the primary research contribution. It does not require historical training data and can be deployed at any organisation from day one.

#### Equation 2 — Education Score
```
S_edu(c) = 0.6 × edu_level_score(c) + 0.4 × edu_relevance(c)
```

#### Equation 3 — Experience Score
```
S_exp(c) = min(years_experience(c) / required_years, 1.0)
```

#### Equation 5 — CV Composite Score
```
S_cv(c) = w_edu × S_edu + w_exp × S_exp + w_skill × S_skill
```

#### Equation 7 — Interview Performance Score
```
S_int(c) = w_mcq × P_mcq + w_desc × P_desc + w_code × P_code
```

#### Equation 8 — Candidate Suitability Score (Master Equation)
```
CSS(c) = W_CV × S_cv(c) + W_INT × S_int(c)
Constraint: W_CV + W_INT = 1.0 (always enforced)
Default: W_CV = 0.40, W_INT = 0.60
```

### 10.2 LambdaMART Learning-to-Rank (Comparative Baseline)

LambdaMART (implemented via LightGBM) serves two purposes:

1. **Comparative baseline** in the ablation study
2. **Weight optimisation** sensitivity analysis across four W_CV/W_INT configurations

Training configuration:
```
Objective:       lambdarank
Metric:          ndcg at [5, 10]
Trees:           500 (with early stopping at 50 rounds)
Learning rate:   0.05
Features:        S_edu, S_exp, S_skill, P_mcq, P_desc, P_code
Labels:          relevance_label (0–3)
Groups:          job_role (candidates only ranked within same role)
```

### 10.3 Fairness Audit

#### Equation 9 — Demographic Parity
```
|P(CSS ≥ τ | Male) − P(CSS ≥ τ | Female)| ≤ 0.05
```

#### Equation 10 — Equal Opportunity
```
P(shortlisted | qualified, Male) ≈ P(shortlisted | qualified, Female)
Target: |EOD| < 0.05
```

If either threshold is exceeded, FA*IR re-ranking is applied to the top-20 shortlist ensuring the underrepresented group holds at least 40% representation.

### 10.4 SHAP Explainability

#### Equation 11 — SHAP Decomposition
```
CSS(c) = φ₀ + Σφᵢ    for i = 1 to M features
φ₀   = mean CSS across all candidates in role (base value)
φᵢ   = W_total_i × (feature_i − mean_feature_i)
φᵢ > 0 → feature increases CSS above average
φᵢ < 0 → feature decreases CSS below average
```

Because CSS is a linear model, SHAP values are computed analytically — they are exact, not approximated.

---

## 11. Evaluation Results

### CSS Model — NDCG@5 Per Role

| Role | NDCG@5 | NDCG@10 | MAP | Spearman |
|---|---|---|---|---|
| Software Engineer | 1.0000 | 1.0000 | 0.9941 | 0.6639 |
| Data Scientist | 0.6839 | 0.7949 | 0.9933 | 0.6526 |
| Machine Learning Engineer | 1.0000 | 0.8769 | 0.9966 | 0.6648 |
| DevOps Engineer | 0.9165 | 0.9458 | 0.9861 | 0.7289 |
| Cybersecurity Analyst | 0.8062 | 0.8742 | 0.9950 | 0.7087 |
| Cloud Solutions Architect | 0.9250 | 0.9065 | 0.9984 | 0.7654 |
| Database Administrator | 1.0000 | 1.0000 | 0.9942 | 0.7304 |
| Frontend Developer | 1.0000 | 0.9202 | 0.9866 | 0.6004 |
| Backend Developer | 1.0000 | 0.9581 | 0.9994 | 0.7397 |
| Mobile App Developer | 0.9165 | 0.9458 | 0.9978 | 0.7333 |
| **OVERALL** | **0.9248** | **0.9223** | **0.9942** | **0.6988** |

### Ablation Study

| Configuration | NDCG@5 | NDCG@10 | MAP | Spearman |
|---|---|---|---|---|
| A — CV Features Only | 0.8365 | 0.8328 | 0.9940 | 0.6434 |
| B — Interview Features Only | 0.8427 | 0.8270 | 0.9904 | 0.5911 |
| C — AHP/TOPSIS Baseline | 0.9432 | 0.9186 | 0.9941 | 0.6655 |
| **D — CSS Weighted Average (Proposed)** | **0.9248** | **0.9223** | **0.9942** | **0.6988** |
| E — LambdaMART LTR | 0.9342 | 0.9181 | 0.9940 | 0.7563 |

### Weight Sensitivity Analysis

| Configuration | W_CV | W_INT | NDCG@5 | Top-3 Stability |
|---|---|---|---|---|
| Default | 0.40 | 0.60 | 0.9248 | 1.0000 |
| Balanced | 0.50 | 0.50 | 0.9432 | 0.9333 |
| CV-heavy | 0.60 | 0.40 | 0.9441 | 0.8667 |
| INT-heavy | 0.25 | 0.75 | 0.8957 | 0.7667 |

### Fairness Audit — All Roles

| Role | DP | EOD | Result |
|---|---|---|---|
| Software Engineer | 0.0240 | 0.0053 | ✓ FAIR |
| Data Scientist | 0.0040 | 0.0263 | ✓ FAIR |
| Machine Learning Engineer | 0.0200 | 0.0070 | ✓ FAIR |
| DevOps Engineer | 0.0160 | 0.0062 | ✓ FAIR |
| Cybersecurity Analyst | 0.0040 | 0.0111 | ✓ FAIR |
| Cloud Solutions Architect | 0.0080 | 0.0000 | ✓ FAIR |
| Database Administrator | 0.0080 | 0.0205 | ✓ FAIR |
| Frontend Developer | 0.0320 | 0.0001 | ✓ FAIR |
| Backend Developer | 0.0360 | 0.0106 | ✓ FAIR |
| Mobile App Developer | 0.0400 | 0.0001 | ✓ FAIR |
| **Overall** | **0.0080** | **0.0060** | **✓ FAIR** |

> Threshold: DP ≤ 0.05 and EOD ≤ 0.05. All roles pass both thresholds without requiring FA*IR re-ranking.

---

## 12. Technologies Used

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Core language |
| NumPy | Latest | Numerical computations |
| Pandas | Latest | Data processing and CSV handling |
| LightGBM | Latest | LambdaMART learning-to-rank |
| SHAP | Latest | Analytical SHAP explainability |
| Matplotlib | Latest | Chart generation |
| Streamlit | Latest | Employer dashboard |
| SciPy | Latest | Spearman rank correlation |
| Scikit-learn | Latest | Preprocessing utilities |
| Faker | Latest | Candidate ID generation |
| Plotly | Latest | Interactive charts |

---

## 13. Research Questions

| RQ | Hypothesis | Finding |
|---|---|---|
| RQ1 | CSS (CV+Interview) > CV alone and Interview alone | Confirmed. CSS NDCG@5=0.9248 vs CV=0.8365 and INT=0.8427 |
| RQ2 | Role-specific weighting is more appropriate than fixed-weight MCDM | Confirmed. CSS provides comparable NDCG with employer control, fairness, and explainability |
| RQ3 | Top-3 shortlist is stable across ±0.10 weight variations | Confirmed. Top-3 Stability=1.00 for default configuration |
| RQ4 | Fairness constraints do not meaningfully degrade NDCG@5 | Confirmed. All roles pass fairness with zero NDCG degradation |
| RQ5 | SHAP explanations make ranking decisions interpretable | Confirmed. CSS(c) = φ₀ + Σφᵢ reconstructed exactly |

---

## 14. References

1. Schmidt, F. L., & Hunter, J. E. (1998). The validity and utility of selection methods in personnel psychology: Practical and theoretical implications of 85 years of research findings. *Psychological Bulletin*, 124(2), 262–274.

2. Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 4765–4774.

3. Sari, Y., Putra, A. S., & Wibowo, A. (2017). Decision Support System for New Employee Recruitment Using Weighted Product Method. *IEEE ICICOS*.

4. Kusumadewi, S., Rosita, L., Izzatillah, A., & Mustofa, A. (2018). AHP-TOPSIS on Selection of New University Students. *IEEE ICITSI*.

5. Hamid, N., et al. (2022). Predicting Employee Selection Using Machine Learning Techniques. *IEEE ICCKE*.

6. Kalasampath, V., et al. (2025). Mitigating Bias in AI Model Using eXplainable AI in Hiring Process. *IEEE Access*.

7. Singh, A., & Joachims, T. (2018). Fairness of Exposure in Rankings. *ACM SIGKDD*.

8. Mehrabi, N., et al. (2021). A Survey on Bias and Fairness in Machine Learning. *ACM Computing Surveys*, 54(6).

9. Faliagka, E., Tsakalidis, A., & Tzimas, G. (2014). An integrated e-recruitment system for automated personality mining and applicant ranking. *Artificial Intelligence Review*, 42.

10. AI Fairness 360 (AIF360). IBM Research, 2018. https://github.com/Trusted-AI/AIF360

---

## Academic Integrity

This project was developed as an original undergraduate research contribution at SLIIT Faculty of Computing. All external libraries and tools used are open-source and properly attributed. The research methodology, model design, evaluation framework, and implementation are the original work of IT22027610 — Perera K.G.S.N., under the supervision of Mrs. Buddhima Athanavake and Mrs. Narmada Gamage.

---

*Component 3 | R26-IT-148 | IT22027610 | Perera K.G.S.N. | SLIIT Faculty of Computing*
