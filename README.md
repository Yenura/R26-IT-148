# AI-Driven Recruitment Ecosystem
### Intelligent Job Matching & Predictive Career Development

> A 4-component full-stack AI system built with FastAPI, React, MongoDB, and scikit-learn.  
> Each component handles one stage of the recruitment pipeline and integrates into a single working website.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [System Flow](#system-flow)
3. [Dataset](#dataset)
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
| **Component 3** | Interview-Driven Candidate Ranking | 8003 |
| **Component 4** | Skill Gap Analysis & Career Development | 8004 |
| **Frontend** | Unified React UI | 5174 |

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
 │  • TF-IDF / SBERT embeddings│
 │  • CV Matching Score (0-100)│
 └────────────┬────────────────┘
              │  cv_matching_score + extracted_skills
              ▼
 ┌─────────────────────────────┐
 │  Component 2                │
 │  AI Interview System        │
 │  • Generate MCQ/Descriptive │
 │  • Evaluate answers (SBERT) │
 │  • Interview Score (0-100)  │
 └────────────┬────────────────┘
              │  interview_score + mcq/descriptive/coding scores
              ▼
 ┌────────────────────────────────────────┐
 │  Component 3              Component 4  │
 │  Candidate Ranking   ←──► Skill Gap   │
 │  • Composite Score        Analysis    │
 │  • SHAP explainability    • Gap Report │
 │  • Ranked list            • Career Path│
 └────────────────────────────────────────┘
```

---

## Dataset

**File:** `Data_set/AI_Resume_Screening.csv`  
**Records:** 1000 candidates

| Column | Type | Description |
|--------|------|-------------|
| Resume_ID | int | Unique ID |
| Name | str | Candidate name |
| Skills | str | Comma-separated skills |
| Experience (Years) | int | Work experience |
| Education | str | Highest degree |
| Certifications | str | Certifications held |
| Job Role | str | Target role |
| Recruiter Decision | str | Hire / Reject |
| Salary Expectation ($) | int | Expected salary |
| Projects Count | int | Projects done |
| AI Score (0-100) | int | AI-generated score |

**Job Roles:** AI Researcher (257) · Data Scientist (255) · Cybersecurity Analyst (255) · Software Engineer (233)  
**Hire/Reject:** 812 Hire · 188 Reject

**Skills in dataset:** TensorFlow, NLP, Pytorch, Deep Learning, Machine Learning, Python, SQL, Java, C++, React, Linux, Cybersecurity, Networking, Ethical Hacking, AWS Certified, Google ML

---

## Component 1 — Job & CV Intelligence

### Goal
Process job descriptions and candidate CVs to compute a **CV Matching Score**.

### ML Tasks
- Clean and preprocess skills text
- Extract skills, experience, education using NLP
- TF-IDF or SBERT sentence embeddings for semantic matching
- Train classification/similarity model
- Output: `cv_matching_score` (0–100)

### Key Algorithms
| Task | Method |
|------|--------|
| Skill extraction | spaCy NER / regex |
| CV-JD matching | TF-IDF cosine similarity / SBERT |
| Classification | Random Forest / Logistic Regression |
| Evaluation | Accuracy, F1, ROC-AUC |

### API Endpoints (port 8001)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/match/cv` | Upload CV + job role → get match score |
| GET  | `/api/v1/jobs` | List available job postings |
| POST | `/api/v1/jobs` | Employer posts a new job |
| GET  | `/api/v1/match/report/{id}` | CV match report for a candidate |

### Output to other components
```json
{
  "candidate_id": "CAND-001",
  "cv_matching_score": 72.5,
  "extracted_skills": ["Python", "SQL", "React"],
  "experience_years": 3,
  "education": "B.Tech"
}
```

---

## Component 2 — AI Interview Generation & Evaluation

### Goal
Generate AI-based interview questions and automatically score candidate answers.

### Question Types
| Type | Generation | Evaluation |
|------|-----------|------------|
| MCQ | Based on job role requirements | Correct/Incorrect → MCQ Score |
| Descriptive | From job description keywords | SBERT semantic similarity |
| Coding | Role-specific problems | Test case execution / scoring rules |

### ML Tasks
- Question generation from job role knowledge base
- SBERT model for descriptive answer similarity
- Scoring engine for all 3 question types
- Output: `interview_score`, `mcq_score`, `descriptive_score`, `coding_score`

### API Endpoints (port 8002)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/interview/start` | Generate questions for a candidate |
| POST | `/api/v1/interview/submit` | Submit answers for evaluation |
| GET  | `/api/v1/interview/result/{id}` | Get interview scores |
| GET  | `/api/v1/interview/questions/{role}` | Get question bank by role |

### Output to other components
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
Combine CV Matching Score and Interview Score into a **Composite Suitability Score (CSS)** and rank candidates.

### Ranking Algorithm
```
CSS = (w1 × CV_Score) + (w2 × Interview_Score)
      + (w3 × Skills_Score) + (w4 × Experience_Score) + (w5 × Education_Score)

where w1 + w2 + w3 + w4 + w5 = 1.0  (employer-configurable weights)
```

### ML Tasks
- Weighted scoring formula
- Optional: LambdaMART / LightGBM learning-to-rank model
- SHAP explainability for each candidate score
- Fairness-aware adjustments (optional)

### Key Features
| Feature | Detail |
|---------|--------|
| Weight configuration | Employer can set weights via UI |
| Explainability | SHAP values per candidate |
| Ranking model | Gradient Boosting / LambdaMART |
| Output | Ranked list with scores |

### API Endpoints (port 8003)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/rank/compute` | Compute CSS + rank candidates |
| GET  | `/api/v1/rank/results/{job_id}` | Ranked list for a job |
| POST | `/api/v1/rank/weights` | Set employer scoring weights |
| GET  | `/api/v1/rank/explain/{candidate_id}` | SHAP explanation for a candidate |

### Output
```json
{
  "job_id": "JOB-001",
  "ranked_candidates": [
    {
      "rank": 1,
      "candidate_id": "CAND-005",
      "composite_score": 91.4,
      "cv_score": 88,
      "interview_score": 94,
      "shap_explanation": {...}
    }
  ]
}
```

---

## Component 4 — Skill Gap Analysis & Career Development

### Goal
Identify skill gaps and generate personalised career guidance using outputs from Components 1 & 2.

### Gap Identification Logic
| Low Score Source | Gap Category |
|-----------------|--------------|
| Low CV Matching Score | Missing required job skills |
| Low Interview Score | Weak theoretical knowledge |
| Low Coding Score | Problem-solving / algorithm gaps |
| Failed MCQ Topics | Specific knowledge gaps |

### Gap Categories
- **Technical Gaps** — Java, SQL, C++, React, Linux, Python
- **ML/AI Gaps** — TensorFlow, Pytorch, Machine Learning, Deep Learning, NLP
- **Security Gaps** — Cybersecurity, Networking, Ethical Hacking
- **Knowledge Gaps** — inferred from interview/MCQ failures
- **Problem-Solving Gaps** — inferred from low coding score

### ML Pipeline
| Step | Detail |
|------|--------|
| Dataset | `AI_Resume_Screening.csv` (1000 rows) |
| Features | 25 features: skills (one-hot), experience, education, gap score, AI score |
| Target | Recruiter Decision (Hire/Reject) |
| Best Model | Random Forest (F1 = 1.000, ROC-AUC = 1.000) |
| Cross-validation | 5-fold stratified |

### Model Results
| Model | Accuracy | F1 | ROC-AUC | CV Mean |
|-------|----------|-----|---------|---------|
| **Random Forest** ✅ | 1.000 | 1.000 | 1.000 | 1.000 |
| Gradient Boosting | 1.000 | 1.000 | 1.000 | 1.000 |
| Logistic Regression | 0.920 | 0.925 | 0.991 | 0.923 |

### Gap Severity Distribution (1000 candidates)
| Severity | Count | % |
|----------|-------|---|
| Medium | 522 | 52.2% |
| High | 327 | 32.7% |
| Low | 151 | 15.1% |

### Gap Score Formula
```
gap_score = 0.8 × (0.7 × required_match + 0.3 × optional_match) + 0.2 × experience_ok

Severity:  Low  → gap_score ≥ 0.85
           Medium → gap_score ≥ 0.60
           High   → gap_score < 0.60
```

### Job Role Requirements
| Role | Required Skills | Optional Skills | Min Exp |
|------|----------------|-----------------|---------|
| Data Scientist | Python, Machine Learning, SQL, Deep Learning | TensorFlow, Pytorch, NLP | 2 yrs |
| AI Researcher | Python, TensorFlow, NLP, Pytorch | Deep Learning, Machine Learning | 1 yr |
| Software Engineer | Java, SQL, C++ | React, Python | 1 yr |
| Cybersecurity Analyst | Cybersecurity, Networking, Linux | Ethical Hacking | 1 yr |

### API Endpoints (port 8004)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/skill-gap/analyze` | Run full ML skill gap analysis |
| GET  | `/api/v1/skill-gap/report/{id}` | Fetch gap report |
| GET  | `/api/v1/skill-gap/reports` | All reports (paginated) |
| DELETE | `/api/v1/skill-gap/report/{id}` | Delete report |
| POST | `/api/v1/career/path` | Generate career path milestones |
| GET  | `/api/v1/career/resources/{role}` | Learning resources by role |
| GET  | `/api/v1/career/roadmap/{id}` | Saved roadmap |
| POST | `/api/v1/progress/update` | Update skill learning status |
| GET  | `/api/v1/progress/{id}` | Get candidate progress |
| DELETE | `/api/v1/progress/{id}` | Reset progress |
| GET  | `/api/v1/analytics/summary` | Dashboard analytics |
| GET  | `/api/v1/analytics/leaderboard` | Top candidates |

### Frontend Pages (Component 4)
| Page | Route | Features |
|------|-------|----------|
| Dashboard | `/` | KPI tiles, severity pie, role bar, missing skills chart, mini leaderboard |
| Analyse CV | `/analyze` | 3-tab form: info / scores / topics |
| Gap Report | `/report/:id` | Radar chart, skill snapshot, gap categories, learning plan timeline, roadmap |
| Career Path | `/career` | Milestone track, lateral moves, resource cards |
| My Progress | `/progress` | SVG ring, per-skill status toggle |
| Leaderboard | `/leaderboard` | Podium top-3 + full ranked table |

### Outputs
- **Skill Gap Report** — per-category gaps with severity
- **Learning Plan** — phased monthly plan with course links
- **Skill Roadmap** — visual node graph (has / missing-required / missing-optional)
- **Career Milestones** — current level → next → lateral options
- **Progress Tracker** — Not Started / In Progress / Completed per skill
- **Hire Probability** — ML model prediction (0–100%)

---

## Full Project Structure

```
AI-Driven-Recruitment-Ecosystem/
│
├── Data_set/
│   └── AI_Resume_Screening.csv
│
├── component1/                        # Job & CV Intelligence
│   ├── ml/
│   ├── backend/                       # FastAPI — port 8001
│   └── frontend/                      # React pages
│
├── component2/                        # AI Interview
│   ├── ml/
│   ├── backend/                       # FastAPI — port 8002
│   └── frontend/
│
├── component3/                        # Candidate Ranking
│   ├── ml/
│   ├── backend/                       # FastAPI — port 8003
│   └── frontend/
│
├── component4/                        # Skill Gap & Career Dev
│   ├── ml/
│   │   └── train_skill_gap_model.py
│   ├── models/                        # .pkl + .json artefacts
│   ├── reports/                       # evaluation plots + JSON
│   ├── backend/
│   │   ├── main.py                    # FastAPI — port 8004
│   │   ├── .env
│   │   ├── requirements.txt
│   │   ├── models/schemas.py
│   │   ├── services/ml_engine.py
│   │   └── routers/
│   │       ├── skill_gap.py
│   │       ├── career.py
│   │       ├── progress.py
│   │       └── analytics.py
│   └── frontend/
│       ├── vite.config.js
│       └── src/
│           ├── App.jsx
│           ├── api.js
│           ├── index.css
│           └── pages/
│               ├── Dashboard.jsx
│               ├── Analyze.jsx
│               ├── Report.jsx
│               ├── CareerPath.jsx
│               ├── Progress.jsx
│               └── Leaderboard.jsx
│
└── README.md
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| ML / NLP | Python, scikit-learn, pandas, numpy, joblib, SBERT, spaCy |
| Backend | FastAPI, Uvicorn, Motor (async MongoDB), Pydantic |
| Frontend | React 18, Vite, React Router v6, Recharts, Axios, Lucide Icons |
| Database | MongoDB Atlas |
| Styling | Vanilla CSS — dark glassmorphism theme |
| Ranking | LightGBM / LambdaMART (Component 3) |
| Explainability | SHAP (Component 3) |

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
| `candidate_rankings` | C3 | Composite scores + rank |
| `skill_gap_reports` | C4 | Full gap analysis per candidate |
| `career_paths` | C4 | Career milestones |
| `progress_tracking` | C4 | Per-skill learning status |

### `skill_gap_reports` document
```json
{
  "candidate_id": "CAND-001",
  "candidate_name": "Jane Smith",
  "job_role": "Data Scientist",
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
  "security_gaps": [],
  "knowledge_gaps": ["Overfitting", "Cross Validation"],
  "problem_solving_gaps": ["Algorithm Design"],
  "resources": [...],
  "learning_plan": [...],
  "career_path_suggestions": [...],
  "improvement_suggestions": [...],
  "predicted_hire": true,
  "hire_probability": 61.3,
  "analysis_timestamp": "2026-04-29T06:45:00Z"
}
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB Atlas (URI below)

### 1 — Train Component 4 ML Model
```powershell
python component4\ml\train_skill_gap_model.py
```

### 2 — Start All Backends

**Component 1** (port 8001):
```powershell
cd component1\backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**Component 2** (port 8002):
```powershell
cd component2\backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

**Component 3** (port 8003):
```powershell
cd component3\backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8003
```

**Component 4** (port 8004):
```powershell
cd component4\backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8004
```

### 3 — Start Frontend
```powershell
cd component4\frontend
npm install
npm run dev
```
Open: **http://localhost:5174**

---

## Environment Variables

Each backend has a `.env` file:

```env
MONGODB_URI=mongodb+srv://admin:PxUm8dLzq5jqlHYN@coordinator.ljarc.mongodb.net/HR
DB_NAME=HR
```

Component ports:
```env
# component1/backend/.env
PORT=8001

# component2/backend/.env
PORT=8002

# component3/backend/.env
PORT=8003

# component4/backend/.env
PORT=8004
```

---

## API Ports Reference

| Service | URL | Swagger Docs |
|---------|-----|-------------|
| Component 1 Backend | http://localhost:8001 | http://localhost:8001/docs |
| Component 2 Backend | http://localhost:8002 | http://localhost:8002/docs |
| Component 3 Backend | http://localhost:8003 | http://localhost:8003/docs |
| Component 4 Backend | http://localhost:8004 | http://localhost:8004/docs |
| Frontend | http://localhost:5174 | — |

---

## Integration Map

```
Component 1  ──── cv_matching_score ────────────────────► Component 3
                                                               ▲
Component 1  ──── cv_matching_score + extracted_skills ──► Component 4

Component 2  ──── interview_score ──────────────────────► Component 3
                                                               ▲
Component 2  ──── interview_score + mcq/descriptive/    ──► Component 4
                  coding scores + weak_topics

Component 4  ──── hire_probability + gap_score ─────────► Component 3
                  (via GET /api/v1/skill-gap/reports)
```

### Full POST payload to Component 4
```json
POST http://localhost:8004/api/v1/skill-gap/analyze
{
  "candidate_id": "CAND-001",
  "candidate_name": "Jane Smith",
  "job_role": "Data Scientist",
  "skills": ["Python", "SQL"],
  "experience_years": 2,
  "education": "B.Tech",
  "certifications": "None",
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

## Sample Test Data

```json
{
  "candidate_id": "TEST-001",
  "candidate_name": "Test Candidate",
  "job_role": "Data Scientist",
  "skills": ["Python", "SQL"],
  "experience_years": 2,
  "education": "B.Tech",
  "certifications": "None",
  "cv_matching_score": 50.0,
  "interview_score": 55.0,
  "mcq_score": 60.0,
  "descriptive_score": 50.0,
  "coding_score": 35.0,
  "weak_topics": ["Model Evaluation", "Feature Engineering"],
  "failed_mcq_topics": ["Cross Validation", "Decision Trees"]
}
```

Expected Component 4 Output:
- Gap Severity: **High**
- Missing Required: `Machine Learning`, `Deep Learning`
- Hire Probability: ~45–65%
- Learning Plan: 2–3 phases
- Suggestions: 4–5 improvement items

---

*AI-Driven Recruitment Ecosystem — 4-member Research Group Project*  
*Built with FastAPI · React · MongoDB · scikit-learn · SBERT*
