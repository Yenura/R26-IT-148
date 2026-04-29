# Component 4 – Skill Gap Analysis & Career Development

AI-Driven Recruitment Ecosystem | Component 4 of 4

## What this component does

Uses outputs from **Component 1** (CV Matching Score + extracted skills) and **Component 2** (Interview Score + answer evaluation) to:

1. Identify skill gaps (technical, ML/AI, security, knowledge, problem-solving)
2. Generate a personalised learning plan with course recommendations
3. Build a skill roadmap (graph structure)
4. Suggest career growth paths and lateral moves
5. Track learning progress per skill
6. Provide an analytics dashboard and leaderboard

## ML Pipeline

| Step | Detail |
|------|--------|
| Dataset | `AI_Resume_Screening.csv` (1000 rows) |
| Features | Skills (one-hot), experience, education, certifications, AI score, gap score |
| Target | Recruiter Decision (Hire/Reject) |
| Models | Random Forest ✅ (F1=1.00), Gradient Boosting, Logistic Regression |
| Evaluation | Accuracy, F1, Precision, Recall, ROC-AUC, 5-fold CV |
| Outputs | `models/skill_gap_classifier.pkl`, evaluation plots in `reports/` |

## Project Structure

```
component4/
├── ml/
│   └── train_skill_gap_model.py      # ML training script
├── models/                           # Saved .pkl + .json artefacts
├── reports/                          # Evaluation plots + JSON report
├── backend/
│   ├── main.py                       # FastAPI app (port 8004)
│   ├── .env                          # MongoDB URI
│   ├── models/schemas.py             # Pydantic schemas
│   ├── services/ml_engine.py         # ML inference + gap logic
│   └── routers/
│       ├── skill_gap.py              # /api/v1/skill-gap/*
│       ├── career.py                 # /api/v1/career/*
│       ├── progress.py               # /api/v1/progress/*
│       └── analytics.py             # /api/v1/analytics/*
└── frontend/
    └── src/
        ├── App.jsx
        ├── api.js
        ├── index.css
        └── pages/
            ├── Dashboard.jsx
            ├── Analyze.jsx
            ├── Report.jsx
            ├── CareerPath.jsx
            ├── Progress.jsx
            └── Leaderboard.jsx
```

## Setup & Run

### 1. Train ML model
```powershell
cd "AI-Driven-Recruitment-Ecosystem-for-Intelligent-Job-Matching-and-Predictive-Career-Development"
python component4\ml\train_skill_gap_model.py
```

### 2. Start Backend (port 8004)
```powershell
cd component4\backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8004
```
API docs: http://localhost:8004/docs

### 3. Start Frontend (port 5174)
```powershell
cd component4\frontend
npm install
npm run dev
```
UI: http://localhost:5174

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/skill-gap/analyze` | Run full skill gap analysis |
| GET  | `/api/v1/skill-gap/report/{id}` | Fetch candidate report |
| GET  | `/api/v1/skill-gap/reports` | List all reports |
| POST | `/api/v1/career/path` | Generate career path |
| GET  | `/api/v1/career/resources/{role}` | Role learning resources |
| POST | `/api/v1/progress/update` | Update skill status |
| GET  | `/api/v1/progress/{id}` | Get candidate progress |
| GET  | `/api/v1/analytics/summary` | Dashboard analytics |
| GET  | `/api/v1/analytics/leaderboard` | Top candidates |

## Database (MongoDB)

Collections: `skill_gap_reports`, `career_paths`, `progress_tracking`

```
MONGODB_URI=mongodb+srv://admin:PxUm8dLzq5jqlHYN@coordinator.ljarc.mongodb.net/HR
```
