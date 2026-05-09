# AI-Driven Recruitment Ecosystem
### Intelligent Job Matching & Predictive Career Development

> A 4-component full-stack AI system built with FastAPI, React, MongoDB, scikit-learn, SBERT, LightGBM, and Streamlit.
> Each component handles one stage of the recruitment pipeline and integrates into a single working ecosystem.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [System Flow](#system-flow)
3. [Datasets](#datasets)
4. [Component 1 — Job & CV Intelligence](#component-1--job--cv-intelligence)
5. [Component 2 — AI Interview Generation & Evaluation](#component-2--ai-interview-generation--evaluation)
6. [Component 3 — Candidate Ranking](#component-3--candidate-ranking)
7. [Component 4 — Skill Gap Analysis & Career Development](#component-4--skill-gap-analysis--career-development)
8. [Full Project Structure](#full-project-structure)
9. [Technology Stack](#technology-stack)
10. [Database Schema](#database-schema)
11. [Setup & Installation](#setup--installation)
12. [Environment Variables](#environment-variables)
13. [API Ports Reference](#api-ports-reference)
14. [Integration Map](#integration-map)

---

## System Overview

| Component | Responsibility | Port |
|-----------|---------------|------|
| **Component 1** | Job & CV Intelligence / CV Matching | 8001 |
| **Component 2** | AI Interview Generation & Evaluation | 8002 |
| **Component 3** | Interview-Driven Candidate Ranking | Streamlit |
| **Component 4** | Skill Gap Analysis & Career Development | 8000 |
| **Frontend** | Unified React/Vite UI (C2 & C4) | 5174 |

---

## System Flow

```
Candidate Registers & Uploads CV
            │
            ▼
 ┌─────────────────────────────┐
 │  Component 1                │
 │  Job & CV Intelligence      │
 │  • NLP skill extraction     │
 │  • TF-IDF / SBERT matching  │
 │  • CV Matching Score (0-100)│
 └────────────┬────────────────┘
              │  cv_matching_score + extracted_skills
              ▼
 ┌─────────────────────────────┐
 │  Component 2                │
 │  AI Interview System        │
 │  • Generate MCQ/Descriptive │
 │    & Coding questions       │
 │  • Evaluate via SBERT       │
 │  • Interview Score (0-100)  │
 └────────────┬────────────────┘
              │  interview_score + mcq/descriptive/coding scores
              ▼
 ┌────────────────────────────────────────┐
 │  Component 3              Component 4  │
 │  Candidate Ranking   ←──► Skill Gap   │
 │  • CSS formula            Analysis    │
 │  • LambdaMART LTR         • Gap Report │
 │  • SHAP explainability    • Career Path│
 │  • Fairness audit         • ML hire   │
 │  • Streamlit dashboard      probability│
 └────────────────────────────────────────┘
```

---

## Datasets

### Component 2 & 4 Dataset
**File:** `Data_set/job_dataset_real_titles_10000.csv`
**Records:** 10,000 candidates · 22 columns

| Column | Description |
|--------|-------------|
| Job Role | One of 10 IT job roles |
| Required Skills | Pipe-delimited required skill list |
| Skills | Pipe-delimited candidate skills |
| Experience (Years) | Work experience |
| Education | Highest qualification |
| Job Level | Junior / Mid-Level / Senior / Lead / Principal |
| Work Mode | On-Site / Hybrid / Remote |
| Certifications | Certification names |
| Certifications Count | Number of certs |
| Projects Count | Portfolio project count |
| Salary (USD/Year) | Annual salary (used as hire proxy) |

**10 Job Roles:**
`Software Engineer` · `Data Scientist` · `Machine Learning Engineer` · `Frontend Developer` · `Backend Developer` · `DevOps Engineer` · `Cybersecurity Analyst` · `Cloud Solutions Architect` · `Database Administrator` · `Mobile App Developer`

### Component 2 Question Bank
**Directory:** `Data_set/DataSet for questions/`
Contains role-specific MCQ, Descriptive, and Coding question banks.

### Component 3 Datasets
**Directory:** `component3/datasets/`

| File | Records | Purpose |
|------|---------|---------|
| `candidates_full.csv` | ~5,000 | Main training/ranking data |
| `fairness_test_set.csv` | ~3,000 | Gender fairness evaluation |
| `job_requirements.csv` | 10 roles | Role-specific thresholds |
| `role_<RoleName>.csv` | ~500 each | Per-role candidate subsets |
| `train_set.csv` / `val_set.csv` / `test_set.csv` | Split | LambdaMART training splits |

---

## Component 1 — Job & CV Intelligence

### Goal
Process job descriptions and candidate CVs to compute a **CV Matching Score (0–100)**.

### ML Tasks
- Clean and preprocess skill text
- Extract skills, experience, education using NLP (spaCy NER + regex)
- TF-IDF cosine similarity and SBERT semantic embeddings for CV–JD matching
- Output: `cv_matching_score` (0–100)

### Key Algorithms

| Task | Method |
|------|--------|
| Skill extraction | spaCy NER / regex |
| CV–JD matching | TF-IDF cosine similarity + SBERT |
| Classification | Random Forest / Logistic Regression |
| Evaluation | Accuracy, F1, ROC-AUC |

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| ML | Python, scikit-learn, spaCy, sentence-transformers (SBERT), pandas, numpy, joblib |
| Backend | FastAPI, Uvicorn, Pydantic v2, Motor, python-dotenv |
| Database | MongoDB Atlas |

### API Endpoints (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/match/cv` | Upload CV + job role → match score |
| GET | `/api/v1/jobs` | List available job postings |
| POST | `/api/v1/jobs` | Post a new job |
| GET | `/api/v1/match/report/{id}` | CV match report for a candidate |

### Output to Other Components
```json
{
  "candidate_id": "CAND-001",
  "cv_matching_score": 72.5,
  "extracted_skills": ["Python", "SQL", "React"],
  "experience_years": 3,
  "education": "B.Sc. Computer Science"
}
```

---

## Component 2 — AI Interview Generation & Evaluation

### Goal
Generate AI-based interview questions (MCQ, Descriptive, Coding) and automatically score candidate answers using SBERT semantic similarity.

### ML Pipeline

**Files:** `component2/ml/`
| Script | Purpose |
|--------|---------|
| `train_pipeline.py` | Full ML training pipeline |
| `question_selector.py` | Role-based question selection logic |
| `answer_evaluator.py` | SBERT-based answer scoring |
| `data_loader.py` | Question bank loader |

**SBERT Model:** `all-MiniLM-L6-v2`

### Question Types

| Type | Generation | Evaluation |
|------|-----------|------------|
| MCQ | Role-specific knowledge bank | Exact match + negative marking (−0.25) |
| Descriptive | JD keyword extraction | SBERT cosine similarity vs model answer |
| Coding | Role-specific problem bank | Test case execution + code quality check |

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| ML | Python, sentence-transformers (SBERT), PyTorch, scikit-learn, scipy, pandas, numpy |
| Backend | FastAPI 0.109.0, Uvicorn 0.27.0, Pydantic v2 2.5.3, Motor 3.3.2 |
| Auth | python-jose (JWT), passlib + bcrypt |
| Database | MongoDB Atlas (`interview_system` DB) |

### Frontend Pages (React/Vite — Port 5174)

| Page | File | Description |
|------|------|-------------|
| Dashboard | `Dashboard.jsx` | Candidate overview and session status |
| Start Interview | `StartInterview.jsx` | Role selection + session initialisation |
| Interview Interface | `InterviewInterface.jsx` | Live question/answer UI for all 3 types |
| Results | `Results.jsx` | Scores breakdown + weak area report |

### API Endpoints (Port 8002)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/interview/start` | Generate questions for a candidate |
| POST | `/api/v1/interview/submit` | Submit answers → auto-score |
| GET | `/api/v1/interview/result/{interview_id}` | Get all interview scores |
| GET | `/api/v1/interview/questions/{job_role}` | Question bank by role |
| GET | `/api/v1/interview/jobs` | Available job roles |
| GET | `/api/v1/interview/health` | Service health check |

### Output to Other Components
```json
{
  "candidate_id": "CAND-001",
  "interview_score": 65.0,
  "mcq_score": 80.0,
  "descriptive_score": 55.0,
  "coding_score": 40.0,
  "weak_topics": ["Overfitting", "Cross Validation"],
  "failed_mcq_topics": ["Decision Trees", "Regularization"]
}
```

---

## Component 3 — Candidate Ranking

### Goal
Combine CV Matching Score and Interview Score into a **Composite Suitability Score (CSS)** and rank candidates with SHAP explainability and fairness audit.

### Ranking Formula

```
CSS(c) = W_CV × S_cv  +  W_INT × S_int

  S_cv  = w_edu×S_edu + w_exp×S_exp + w_skill×S_skill
  S_int = w_mcq×P_mcq + w_desc×P_desc + w_code×P_code

Default weights:  W_CV = 0.40,  W_INT = 0.60
```

### SHAP Explainability (Equation 11)

```
CSS(c) = φ₀ + Σφᵢ
  φ₀ = mean CSS across all candidates in the role
  φᵢ = SHAP contribution of feature i
```

### Fairness Audit

| Metric | Formula | Threshold |
|--------|---------|-----------|
| Demographic Parity | `|P(CSS≥τ|M) − P(CSS≥τ|F)| ≤ 0.05` | ≤ 0.05 |
| Equal Opportunity | `P(shortlisted|qualified,M) ≈ P(shortlisted|qualified,F)` | ≤ 0.05 |

If violated → **FA\*IR re-ranking** applied automatically.

### ML Models

| Model | Artifact | Purpose |
|-------|---------|---------|
| **LambdaMART** | `component3/models/lambdamart_model.pkl` | Learning-to-rank (LightGBM backend) |
| **CSS Engine** | `component3/engine/css_engine.py` | Weighted composite score formula |
| **SHAP Explainer** | `component3/explainability/shap_explainer.py` | Per-feature SHAP values |
| **Fairness Auditor** | `component3/fairness/fairness_audit.py` | DP + EOD audit + FA*IR rerank |

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| ML / Ranking | Python, LightGBM (LambdaMART), SHAP, scikit-learn, pandas, numpy, scipy |
| Dashboard | **Streamlit** (Python-only — NOT React) |
| Charts | matplotlib |
| Data | CSV files (no live DB — offline ranking engine) |

### Evaluation Metrics

| Metric | Value |
|--------|-------|
| NDCG@5 | Measured per role |
| MAP | Mean Average Precision |
| Top-3 Stability | Consistency across weight configs |

### Streamlit Dashboard Pages

| Tab | Content |
|-----|---------|
| 🏆 Ranked Shortlist | CSS-ranked candidates, KPI tiles, expandable cards |
| 🔍 SHAP Explanations | Waterfall charts + feature importance summary |
| ⚖️ Fairness Audit | DP/EOD metrics, gender distribution plots |
| 📊 Model Evaluation | Ablation study, weight sensitivity, feature importance |
| 📂 Dataset Explorer | Role-level data browser, label distribution |

### Run Component 3 Dashboard
```powershell
cd component3
streamlit run dashboard/app.py
```

---

## Component 4 — Skill Gap Analysis & Career Development

### Goal
Identify skill gaps, predict hire probability using ML, and generate personalised career guidance for candidates who need development.

### ML Pipeline

**Training Script:** `component4/ml/train_model.py`
**Dataset:** `Data_set/job_dataset_real_titles_10000.csv` (10,000 records)

**Feature Engineering:**

| Raw Column | Feature Transformation |
|-----------|----------------------|
| Education | Ordinal integer: Bootcamp=1 → PhD=6 |
| Job Level | Ordinal integer: Junior=1 → Principal=5 |
| Work Mode | Ordinal integer: On-Site=1, Hybrid=2, Remote=3 |
| Job Role | One-hot encoded (10 role columns) |
| Required Skills | Binary flags for 40 canonical skills |
| Certifications Count | Numeric + `Has_Cert` binary flag |
| Projects Count | Numeric |
| Experience (Years) | Numeric |

**Total: 57 features**

**Target:** Top 25% salary tier = `1` (hire-worthy), rest = `0`

### Model Results

| Model | Accuracy | F1 Score | ROC-AUC |
|-------|---------|---------|---------|
| Random Forest | ~95% | ~91% | ~99% |
| Gradient Boosting | ~95% | ~91% | ~99% |
| **Logistic Regression ✅** | **95.75%** | **91.80%** | **99.36%** |

**Winner selected by AUC. Saved as:** `component4/models/skill_gap_classifier.pkl`

### Saved Model Artifacts (`component4/models/`)

| File | Purpose |
|------|---------|
| `skill_gap_classifier.pkl` | Best model (Logistic Regression) |
| `random_forest_model.pkl` | Random Forest artefact |
| `gradient_boosting_model.pkl` | Gradient Boosting artefact |
| `logistic_regression_model.pkl` | Logistic Regression artefact |
| `feature_columns.pkl` | Ordered feature column names (57 cols) |
| `role_columns.pkl` | One-hot role column names |
| `all_skills.pkl` | 40 canonical skills list |
| `job_requirements.json` | Required/optional skills + min exp per role |
| `learning_resources.json` | Skill → course name + URL mapping |
| `skill_categories.json` | Skill → domain category mapping |
| `career_paths.json` | Role progression + lateral move paths |
| `training_stats.json` | Accuracy, AUC, dataset hash, sklearn version |

### Gap Analysis Logic

```
gap_score = SKILL_GAP_WEIGHT × (REQ_WEIGHT × req_score + OPT_WEIGHT × opt_score)
            + EXP_WEIGHT × experience_score

  SKILL_GAP_WEIGHT = 0.80  |  REQ_WEIGHT = 0.70  |  OPT_WEIGHT = 0.30
  EXP_WEIGHT = 0.20

Severity:  Low    → gap_score ≥ 0.80
           Medium → gap_score ≥ 0.55
           High   → gap_score < 0.55

Hire Prob = 0.60 × ML_probability + 0.40 × avg(CV_score, Interview_score)
```

### Gap Categories

| Category | Skills Covered |
|---------|--------------|
| Technical | Python, TypeScript, Java, C++, Go, Rust, Kotlin, Scala |
| Web | React, REST APIs, GraphQL, HTML/CSS, Vue.js |
| ML/AI | Machine Learning, Deep Learning, TensorFlow, PyTorch, NLP, MLOps |
| Cloud/DevOps | AWS, Azure, GCP, Terraform, Docker, Kubernetes, CI/CD |
| Security | Cybersecurity, Networking, Linux, Ethical Hacking, Penetration Testing |
| Data/DB | SQL, PostgreSQL, MongoDB, Apache Spark, Kafka, Airflow |

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| ML | Python 3.12, scikit-learn, pandas, numpy, joblib |
| Backend | FastAPI, Uvicorn, Pydantic v2 (field validators), Motor, asyncio.gather |
| Frontend | React 18, Vite 5, React Router v6, Recharts, Axios, Lucide React |
| Database | MongoDB Atlas (`HR` database) |

### Frontend Pages (React/Vite — Port 5174)

| Page | Route | Features |
|------|-------|---------|
| Dashboard | `/` | 8 KPI tiles, Severity pie, Role bar, Skills gap bar, Job Level bar, Leaderboard |
| Analyse CV | `/analyze` | 3-tab form: Candidate Info / Interview Scores / Weak Topics |
| Gap Report | `/report/:id` | Radar chart, Skill snapshot, 6 gap categories, Learning plan timeline |
| Career Path | `/career` | Career level nodes, lateral moves, 9 curated learning resources per role |
| My Progress | `/progress` | Per-skill status toggle (Not Started / In Progress / Completed) |
| Leaderboard | `/leaderboard` | Top candidates ranked by hire probability |

### API Endpoints (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/skill-gap/analyze` | Run ML analysis → save to MongoDB |
| GET | `/api/v1/skill-gap/report/{id}` | Fetch latest gap report |
| GET | `/api/v1/skill-gap/reports` | All reports (paginated) |
| DELETE | `/api/v1/skill-gap/report/{id}` | Delete a report |
| GET | `/api/v1/skill-gap/roles` | List 10 supported job roles |
| POST | `/api/v1/career/path` | Generate career path nodes |
| GET | `/api/v1/career/resources/{role}` | 9 curated learning resources |
| GET | `/api/v1/career/roadmap/{id}` | Saved roadmap for a candidate |
| POST | `/api/v1/progress/update` | Update skill learning status |
| GET | `/api/v1/progress/{id}` | Get progress + completion % |
| DELETE | `/api/v1/progress/{id}` | Reset all progress |
| GET | `/api/v1/analytics/summary` | Dashboard aggregate stats (parallel queries) |
| GET | `/api/v1/analytics/leaderboard` | Top unique candidates by hire probability |
| GET | `/api/v1/analytics/role-insights/{role}` | Role-level statistics |
| GET | `/health` | Backend health + MongoDB ping |

### Sample Request
```json
POST http://localhost:8000/api/v1/skill-gap/analyze
{
  "candidate_id": "CAND-001",
  "candidate_name": "Jane Smith",
  "job_role": "Data Scientist",
  "job_level": "Mid-Level",
  "work_mode": "Hybrid",
  "skills": ["Python", "SQL"],
  "experience_years": 3,
  "education": "B.Sc. Computer Science",
  "certifications": "None",
  "certifications_count": 0,
  "projects_count": 5,
  "cv_matching_score": 72.5,
  "interview_score": 65.0,
  "mcq_score": 80.0,
  "descriptive_score": 55.0,
  "coding_score": 40.0,
  "weak_topics": ["Overfitting", "Bias-Variance"],
  "failed_mcq_topics": ["Decision Trees", "Regularization"]
}
```

---

## Full Project Structure

```
AI-Driven-Recruitment-Ecosystem/
│
├── Data_set/
│   ├── job_dataset_real_titles_10000.csv   ← C2 & C4 training data (10K rows)
│   ├── job_dataset_job_titles_10000.csv    ← Alternate title format
│   └── DataSet for questions/              ← C2 question bank CSVs
│
├── component2/                             ← AI Interview System
│   ├── ml/
│   │   ├── train_pipeline.py              ← SBERT training pipeline
│   │   ├── question_selector.py           ← Role-based question selection
│   │   ├── answer_evaluator.py            ← SBERT semantic scoring
│   │   └── data_loader.py                 ← Question bank loader
│   ├── backend/                           ← FastAPI — port 8002
│   │   ├── main.py
│   │   ├── .env.example
│   │   ├── requirements.txt
│   │   ├── models/                        ← Pydantic schemas
│   │   ├── routers/interview.py           ← All interview endpoints
│   │   └── services/                      ← Business logic
│   └── frontend/                          ← React/Vite UI
│       └── src/pages/
│           ├── Dashboard.jsx
│           ├── StartInterview.jsx
│           ├── InterviewInterface.jsx
│           └── Results.jsx
│
├── component3/                             ← Candidate Ranking
│   ├── engine/css_engine.py               ← CSS formula + hard filter
│   ├── ltr/lambdamart_model.py            ← LightGBM LambdaMART
│   ├── explainability/shap_explainer.py   ← SHAP waterfall + summary
│   ├── fairness/fairness_audit.py         ← DP + EOD + FA*IR reranking
│   ├── dashboard/app.py                   ← Streamlit dashboard (5 tabs)
│   ├── data/role_configs.py               ← Role weights & thresholds
│   ├── models/lambdamart_model.pkl        ← Trained LambdaMART model
│   ├── datasets/                          ← Training CSV files (10 roles)
│   └── results/                           ← Ablation, sensitivity, FI CSVs
│
├── component4/                             ← Skill Gap & Career Dev
│   ├── ml/
│   │   └── train_model.py                 ← Trains 3 classifiers, saves artifacts
│   ├── models/                            ← .pkl + .json artifacts (12 files)
│   ├── backend/                           ← FastAPI — port 8000
│   │   ├── main.py                        ← Lifespan, CORS, MongoDB indexes
│   │   ├── .env / .env.example
│   │   ├── models/schemas.py              ← Pydantic + validators
│   │   ├── services/ml_engine.py          ← Core inference engine
│   │   └── routers/
│   │       ├── skill_gap.py
│   │       ├── career.py
│   │       ├── progress.py
│   │       └── analytics.py
│   ├── frontend/                          ← React/Vite UI
│   │   └── src/pages/
│   │       ├── Dashboard.jsx
│   │       ├── Analyze.jsx
│   │       ├── Report.jsx
│   │       ├── CareerPath.jsx
│   │       ├── Progress.jsx
│   │       └── Leaderboard.jsx
│   └── tests/
│       └── test_ml_engine.py              ← 41 unit tests (pytest)
│
└── README.md
```

---

## Technology Stack

| Layer | Component 1 | Component 2 | Component 3 | Component 4 |
|-------|------------|------------|------------|------------|
| Language | Python 3.10+ | Python 3.10+ | Python 3.10+ | Python 3.12 |
| API Framework | FastAPI | FastAPI 0.109.0 | — (no REST API) | FastAPI |
| Server | Uvicorn | Uvicorn 0.27.0 | — | Uvicorn |
| Port | 8001 | 8002 | Streamlit | 8000 |
| ML Models | SBERT, TF-IDF, RF/LR | SBERT (PyTorch) | LambdaMART (LightGBM) | LR ✅, RF, GB |
| NLP | spaCy NER | sentence-transformers | — | joblib fuzzy match |
| Explainability | — | — | SHAP | — |
| Fairness | — | — | DP + EOD + FA*IR | — |
| Frontend | React (shared) | React/Vite | **Streamlit** | React 18 + Vite 5 |
| Charts | Recharts | Recharts | matplotlib | Recharts |
| Database | MongoDB Atlas | MongoDB Atlas | CSV files | MongoDB Atlas |
| Validation | Pydantic v2 | Pydantic v2 | — | Pydantic v2 (validators) |
| Auth | — | JWT + bcrypt | — | — |
| Async DB | Motor | Motor | — | Motor + asyncio.gather |

---

## Database Schema

**MongoDB Atlas** · Database: `HR`

### Collections

| Collection | Component | Purpose |
|-----------|-----------|---------|
| `candidates` | C1 | Candidate profiles + CV text |
| `jobs` | C1 | Employer job postings |
| `cv_match_reports` | C1 | CV matching scores |
| `interview_sessions` | C2 | Generated questions per candidate |
| `interview_results` | C2 | Scores per question type |
| `skill_gap_reports` | C4 | Full gap analysis per candidate |
| `career_paths` | C4 | Career milestone data |
| `progress_tracking` | C4 | Per-skill learning status |

### MongoDB Indexes (Component 4 — auto-created on startup)

| Collection | Index | Purpose |
|-----------|-------|---------|
| `skill_gap_reports` | `candidate_id` | Fast single-candidate lookup |
| `skill_gap_reports` | `hire_probability` (desc) | Leaderboard sort |
| `skill_gap_reports` | `job_role` | Analytics aggregation |
| `skill_gap_reports` | `created_at` (desc) | Latest-report queries |
| `progress_tracking` | `(candidate_id, skill)` unique | Prevent duplicate progress rows |

### `skill_gap_reports` Document Schema
```json
{
  "candidate_id": "CAND-001",
  "candidate_name": "Jane Smith",
  "job_role": "Data Scientist",
  "job_level": "Mid-Level",
  "work_mode": "Hybrid",
  "cv_matching_score": 72.5,
  "interview_score": 65.0,
  "skill_match_pct": 50.0,
  "gap_score": 0.567,
  "gap_severity": "Medium",
  "missing_required": ["Machine Learning", "Deep Learning"],
  "missing_optional": ["TensorFlow", "NLP"],
  "present_skills": ["Python", "SQL"],
  "technical_gaps": [],
  "ml_ai_gaps": ["Machine Learning", "Deep Learning"],
  "cloud_devops_gaps": [],
  "security_gaps": [],
  "data_gaps": [],
  "knowledge_gaps": ["Overfitting"],
  "problem_solving_gaps": ["Algorithm Design"],
  "predicted_hire": true,
  "hire_probability": 61.3,
  "certifications_count": 0,
  "projects_count": 5,
  "analysis_timestamp": "2026-05-09T07:45:00Z"
}
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ installed
- MongoDB Atlas account (or local MongoDB)
- `pip` and `npm` available in PATH

### Step 1 — Train Component 4 ML Model (run once)
```powershell
python component4\ml\train_model.py
```
Expected output: `Logistic Regression selected (AUC=0.9936)` → saves 12 artifacts to `component4/models/`

### Step 2 — Train Component 2 ML Models (run once)
```powershell
cd component2\ml
python train_pipeline.py
```

### Step 3 — Configure Environment Variables

**Component 2:**
```powershell
copy component2\backend\.env.example component2\backend\.env
```

**Component 4:**
```powershell
copy component4\backend\.env.example component4\backend\.env
```
Edit `.env` and set your MongoDB URI.

**Component 4 Frontend:**
```powershell
copy component4\frontend\.env.example component4\frontend\.env.local
```

### Step 4 — Start Backends

**Component 2** (port 8002):
```powershell
cd component2\backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

**Component 4** (port 8000):
```powershell
cd component4\backend
pip install fastapi uvicorn motor pydantic python-dotenv scikit-learn pandas numpy joblib
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 5 — Start Component 3 Streamlit Dashboard
```powershell
cd component3
pip install streamlit lightgbm shap scikit-learn pandas numpy matplotlib scipy
streamlit run dashboard/app.py
```

### Step 6 — Start Frontend (Component 4)
```powershell
cd component4\frontend
npm install
npm run dev
```
Open: **http://localhost:5174**

### Step 7 — Run Unit Tests (Component 4)
```powershell
cd component4\backend
pip install pytest
python -m pytest ..\tests\test_ml_engine.py -v
```
Expected: **41 passed in ~3s**

---

## Environment Variables

### Component 2 (`component2/backend/.env`)
```env
API_HOST=0.0.0.0
API_PORT=8002
MODELS_DIR=./models
DATABASE_URL=mongodb://localhost:27017/interview_system
SBERT_MODEL=all-MiniLM-L6-v2
MCQ_PENALTY=0.25
ENABLE_NEGATIVE_MARKING=true
ENABLE_CODE_QUALITY_CHECK=true
COMPONENT1_URL=http://localhost:8001
COMPONENT4_URL=http://localhost:8000
```

### Component 4 Backend (`component4/backend/.env`)
```env
MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net
DB_NAME=HR
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

### Component 4 Frontend (`component4/frontend/.env.local`)
```env
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

---

## API Ports Reference

| Service | URL | Swagger Docs |
|---------|-----|-------------|
| Component 1 Backend | http://localhost:8001 | http://localhost:8001/docs |
| Component 2 Backend | http://localhost:8002 | http://localhost:8002/docs |
| Component 3 Dashboard | http://localhost:8501 | — (Streamlit) |
| Component 4 Backend | http://localhost:8000 | http://localhost:8000/docs |
| Frontend (C2 + C4) | http://localhost:5174 | — |

---

## Integration Map

```
Component 1  ──── cv_matching_score ──────────────────────► Component 3 (CSS)
Component 1  ──── cv_matching_score + extracted_skills ───► Component 4 (analyze)

Component 2  ──── interview_score ────────────────────────► Component 3 (CSS)
Component 2  ──── interview_score + mcq/descriptive/     ──► Component 4 (analyze)
                  coding_score + weak_topics

Component 4  ──── hire_probability + gap_severity ────────► Component 3 (shortlist)
                  (via GET /api/v1/skill-gap/reports)
```

### Data Flow: Full POST to Component 4
```
POST http://localhost:8000/api/v1/skill-gap/analyze
Body: { candidate_id, job_role, skills, cv_matching_score, interview_score, ... }
  ↓
Pydantic validates all fields (schemas.py)
  ↓
run_skill_gap_analysis() in ml_engine.py
  ├─ compute_gap()           → gap_score, missing_required, skill_match_pct
  ├─ build_feature_vector()  → 57-column DataFrame
  ├─ classifier.predict_proba() → hire probability
  ├─ blend with CV/interview scores
  ├─ categorise missing skills into 6 domains
  ├─ build learning plan (monthly phases)
  └─ build career path suggestions
  ↓
Save to MongoDB (skill_gap_reports)
  ↓
Return full JSON report to frontend
```

---

## Test Coverage (Component 4)

| Test Class | Tests | Coverage |
|-----------|-------|---------|
| `TestComputeGap` | 6 | Unknown role, empty skills, 100% match, partial, experience, fuzzy |
| `TestGapSeverity` | 12 | All boundaries, parametrized (0.0 → 1.0) |
| `TestBuildFeatureVector` | 4 | Column shape, unknown edu/level, no NaN |
| `TestRunSkillGapAnalysis` | 19 | All 10 roles, edge cases, score blending |
| **Total** | **41** | **100% pass** |

---

*AI-Driven Recruitment Ecosystem — Project R26-IT-148*
*FastAPI · React · MongoDB · scikit-learn · SBERT · LightGBM · SHAP · Streamlit*
