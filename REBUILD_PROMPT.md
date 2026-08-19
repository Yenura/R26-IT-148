# RecruitAI — Full System Build Prompt

Build a complete AI-powered recruitment platform called **RecruitAI** with the following specification. Every detail below is required — do not skip, simplify, or substitute.

---

## 1. Tech Stack

### Backend
- **Python 3.12**, FastAPI, uvicorn
- **MongoDB** via `motor` (async) and `pymongo` (sync where needed)
- **JWT auth** via `python-jose` (HS256), passwords hashed with `bcrypt`
- **ML**: `scikit-learn` (TF-IDF + LogisticRegression classifier), `sentence-transformers` (all-MiniLM-L6-v2 for semantic matching, with TF-IDF fallback if SBERT is slow), `pandas`, `numpy`
- **PDF parsing**: `PyMuPDF` (fitz), `pdfminer.six`, `python-docx`
- **Export**: `csv` module, `openpyxl` (Excel), `reportlab` (PDF)
- **NLP**: `nltk` (stopwords, WordNetLemmatizer)

### Frontend
- **React 19** + **Vite 8** + **React Router v7**
- **Recharts** for charts (BarChart, PieChart)
- **react-hot-toast** for notifications
- **lucide-react** for icons
- **axios** for HTTP
- CSS variables for dark/light theme (no Tailwind, no CSS framework)

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Frontend (React)                    │
│                  Port 5174 (dev)                     │
│                                                     │
│  Landing → Auth → Candidate Dashboard / Company DB  │
│  Pipeline: CVMatch, Interview, Ranking, SkillGap,   │
│            CareerPath, Progress, Leaderboard         │
└──────────┬──────────┬──────────┬──────────┬─────────┘
           │          │          │          │
     ┌─────▼──┐  ┌────▼───┐  ┌──▼────┐  ┌──▼────┐
     │C1:8001 │  │C2:8002 │  │C3:8003│  │C4:8004│
     │CV Match│  │Interview│  │Ranking│  │SkillGap│
     └────────┘  └────────┘  └───────┘  └───────┘
           │          │          │          │
     ┌─────▼──────────▼──────────▼──────────▼─────────┐
     │         Unified Backend (Port 8000)              │
     │  Auth, Jobs, Resume Upload/Parse, Export         │
     └─────────────────────┬───────────────────────────┘
                           │
                     ┌─────▼─────┐
                     │  MongoDB   │
                     │  27017     │
                     └───────────┘
```

---

## 3. Database Collections (MongoDB)

### `users`
```json
{
  "_id": ObjectId,
  "email": "string (unique)",
  "password_hash": "string",
  "role": "company" | "candidate",
  "full_name": "string",
  "company_name": "string (company only)",
  "industry": "string",
  "website": "string",
  "created_at": datetime
}
```

### `jobs`
```json
{
  "_id": ObjectId,
  "company_id": "string (user _id)",
  "title": "string",
  "description": "string",
  "department": "string",
  "location": "string",
  "employment_type": "Full-time|Part-time|Contract|Internship",
  "required_skills": ["string"],
  "experience_required": number (years),
  "status": "open|closed",
  "created_at": datetime
}
```

### `applications`
```json
{
  "_id": ObjectId,
  "job_id": "string",
  "candidate_id": "string",
  "candidate_name": "string",
  "resume_id": "string",
  "status": "applied|reviewed|accepted|rejected",
  "created_at": datetime
}
```

### `resumes`
```json
{
  "_id": ObjectId,
  "candidate_id": "string",
  "filename": "string",
  "candidate_name": "string",
  "email": "string",
  "phone": "string",
  "address": "string",
  "linkedin": "string",
  "github": "string",
  "skills": ["string"],
  "education": "string",
  "experience_years": number,
  "projects": ["string"],
  "certifications": ["string"],
  "languages": ["string"],
  "tools": ["string"],
  "frameworks": ["string"],
  "raw_text": "string (full extracted text)",
  "created_at": datetime
}
```

### `predictions`
```json
{
  "_id": ObjectId,
  "resume_id": "string",
  "candidate_id": "string",
  "job_id": "string",
  "predicted_role": "string",
  "role_confidence": float,
  "semantic_score": float,
  "skill_score": float,
  "experience_score": float,
  "education_score": float,
  "overall_score": float,
  "matched_skills": ["string"],
  "missing_skills": ["string"],
  "extra_skills": ["string"],
  "career_suggestions": ["string"],
  "created_at": datetime
}
```

### Component collections (in same MongoDB):
- `interview_sessions` — C2 interview sessions with questions
- `interview_results` — C2 scored results
- `rankings` — C3 ranking results per job
- `skill_gap_reports` — C4 skill gap analyses
- `career_roadmaps` — C4 career paths
- `progress` — C4 skill progress tracking

---

## 4. Canonical 20 Job Roles

These exact 20 roles must be supported across ALL components:

1. Software Engineer
2. Data Scientist
3. Machine Learning Engineer
4. DevOps Engineer
5. Cybersecurity Analyst
6. Cloud Solutions Architect
7. Database Administrator
8. Frontend Developer
9. Backend Developer
10. Mobile App Developer
11. Full Stack Developer
12. QA/Test Automation Engineer
13. Data Engineer
14. Site Reliability Engineer (SRE)
15. UI/UX Designer
16. Network Engineer
17. Business/Systems Analyst
18. AI/NLP Engineer
19. Blockchain Developer
20. Embedded Systems Engineer

---

## 5. Unified Backend (Port 8000)

### Auth Endpoints
```
POST /api/v1/auth/register/company
  Body: { company_name, email, password, industry?, website? }
  Returns: { access_token, role: "company", user_id }

POST /api/v1/auth/login/company
  Body: { email, password }
  Returns: { access_token, role: "company", user_id }

POST /api/v1/auth/register/candidate
  Body: { full_name (min 2 chars), email, password }
  Returns: { access_token, role: "candidate", user_id }

POST /api/v1/auth/login/candidate
  Body: { email, password }
  Returns: { access_token, role: "candidate", user_id }

GET /api/v1/auth/me
  Header: Authorization: Bearer <token>
  Returns: UserOut { id, email, role, name }
```

### Jobs Endpoints
```
POST /api/v1/jobs/
  Auth: company
  Body: { title, description?, department?, location?, employment_type?, required_skills?: [], experience_required? }
  Returns: JobOut

GET /api/v1/jobs/
  Auth: company
  Returns: list[JobOut] (company's own jobs)

GET /api/v1/jobs/all
  Public
  Returns: list[JobOut] (all open jobs)

GET /api/v1/jobs/{job_id}
  Auth: company
  Returns: JobOut

PATCH /api/v1/jobs/{job_id}
  Auth: company
  Body: JobUpdate (partial)
  Returns: JobOut

DELETE /api/v1/jobs/{job_id}
  Auth: company
  Returns: 204

POST /api/v1/jobs/{job_id}/apply
  Auth: candidate
  Body: { candidate_id, candidate_name, resume_id }
  Returns: ApplicationOut

GET /api/v1/jobs/{job_id}/applicants
  Auth: company
  Returns: list[ApplicationOut]
```

### Resume Endpoints
```
POST /api/v1/resume/upload
  Auth: any
  Multipart: file (PDF/DOCX/TXT, max 10MB)
  Returns: ResumeOut (parsed entities)

GET /api/v1/resume/
  Auth: any
  Returns: list[ResumeOut] (user's resumes)

GET /api/v1/resume/{resume_id}
  Auth: any
  Returns: ResumeOut

GET /api/v1/resume/predictions
  Auth: any
  Returns: list[PredictionOut]

POST /api/v1/resume/parse
  Auth: any
  Body: { text: string }
  Returns: ResumeOut (from pasted text)

POST /api/v1/resume/match
  Auth: any
  Query: resume_id, job_id (optional)
  Returns: PredictionOut (scores, matched/missing skills)

GET /api/v1/resume/predict-role
  Auth: any
  Query: resume_id
  Returns: { predicted_role, confidence }
```

### Export Endpoints
```
GET /api/v1/export/csv?type=resumes|predictions
GET /api/v1/export/excel?type=resumes|predictions
GET /api/v1/export/pdf?type=resumes|predictions
  Auth: any
  Returns: File stream
```

---

## 6. Resume Parser (NLP Pipeline)

### File Parsing
- PDF: Try PyMuPDF (`fitz`) first, fallback to `pdfminer.six`
- DOCX: `python-docx` — join paragraph texts
- TXT: Direct UTF-8 decode

### NLP Preprocessing
1. Lowercase
2. Remove non-alphanumeric (keep `#+./`)
3. Remove stopwords (English)
4. Tokenize (split)
5. Lemmatize (nltk WordNetLemmatizer, graceful fallback if missing)

### Entity Extraction (regex-based)
- **Name**: First non-empty line (if not email/phone)
- **Email**: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- **Phone**: `[\+]?[\d\s\-\(\)]{7,15}`
- **LinkedIn**: `linkedin\.com/in/[\w\-]+`
- **GitHub**: `github\.com/[\w\-]+`
- **Skills**: Match against 87 keyword list (python, java, javascript, typescript, react, angular, vue, node.js, django, flask, fastapi, spring, sql, postgresql, mysql, mongodb, redis, aws, azure, gcp, docker, kubernetes, terraform, jenkins, ci/cd, machine learning, deep learning, nlp, computer vision, tensorflow, pytorch, git, linux, bash, rest api, graphql, microservices, html, css, sass, bootstrap, tailwind, pandas, numpy, scikit-learn, matplotlib, jupyter, figma, sketch, adobe xd, blockchain, solidity, web3, embedded, iot, arduino, raspberry pi, agile, scrum, jira)
- **Education**: `(ph.?d|doctorate|m.?s.?c?|master|b.?s.?c?|bachelor|b.?tech|diploma|m.?tech|mba)`
- **Experience Years**: `(\d+(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)` — **cap at 50 max**
- **Projects**: `(?:project|capstone)[\s:]+([^\n]+)`
- **Certifications**: `(?:certification|certificate|certified)[\s:]+([^\n]+)`
- **Languages**: `(?:language|fluent|proficient)[\s:]+([^\n]+)`

---

## 7. Semantic Matcher

Use **TF-IDF cosine similarity** (scikit-learn TfidfVectorizer + cosine_similarity).

Do NOT use sentence-transformers at runtime — it takes 60+ seconds to load on CPU. Use TF-IDF only:
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vec = TfidfVectorizer(max_features=5000)
tfidf = vec.fit_transform([text_a, text_b])
sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
return max(0.0, min(sim * 100, 100.0))
```

---

## 8. Role Classifier (ML Model)

### Training Script
Create `ml/train_role_classifier.py` that:
1. Generates 4000 synthetic resumes (200 per role, 20 roles)
2. Each resume has: random skills from role-specific skill sets, random education, random experience (1-20 years)
3. Trains TF-IDF + LogisticRegression (max_iter=1000)
4. Saves model to `models/role_classifier.pkl` (should be ~1MB)
5. Reports cross-validation accuracy (should be ~100%)

### Inference
```python
import pickle
model = pickle.load(open("models/role_classifier.pkl", "rb"))
# model.predict(tfidf_vectorized_text) → role name
# model.predict_proba(...) → confidence
```

### Keyword Fallback
If model unavailable, match against role-specific keyword dictionaries.

---

## 9. Component 1 — CV Matching (Port 8001)

### Endpoints
```
POST /api/v1/match/cv
  Body: { job_role, candidateSkills, candidateExperience, candidateEducation }
  Returns: { match_score, skill_match, experience_match, education_match, report_id }

GET /api/v1/match/report/{report_id}
  Returns: Stored report
```

### Skills Database
`skills.py` must contain:
- `ROLES` dict: 20 roles → list of required skills
- `role_field_hints`: 20 roles → education/experience hints
- `JOBS_DEFAULT`: Default job descriptions per role

### Scoring Formula
```
match_score = 0.40 * skill_score + 0.30 * experience_score + 0.20 * education_score + 0.10 * bonus
```

---

## 10. Component 2 — Interview System (Port 8002)

### Endpoints
```
POST /api/v1/interview/start
  Body: { candidate_id, job_role, required_skills: [], num_questions: int }
  Returns: { session_id, questions: [{ id, question, question_type, options?, difficulty, topic }] }

POST /api/v1/interview/submit
  Body: { candidate_id, session_id, job_role, answers: [{ question_id, selected_option|answer_text|code_text }] }
  Returns: { interview_id, mcq_score, descriptive_score, coding_score, interview_score, grade, weak_topics, weights_used }

GET /api/v1/interview/result/{interview_id}
  Returns: EvaluationResponse

GET /api/v1/interview/session/{session_id}
  Returns: session data

GET /api/v1/interview/questions/{job_role}
  Returns: Question bank for role

GET /api/v1/interview/jobs
  Returns: { jobs: { role: [skills] } }
```

### Question Types
- **MCQ**: 4 options, one correct, scored 100/0
- **Descriptive**: Free text, scored by TF-IDF similarity to reference answer (0-100)
- **Coding**: Code text, scored by syntax validity + test case matching (0-100)

### Question Bank
Generate questions per role from `ml/build_qg_dataset.py`:
- 50+ questions per role
- Mix of MCQ, Descriptive, Coding
- Multiple difficulties (Easy, Medium, Hard)

### Grading
```
Weights (default): { mcq: 0.25, descriptive: 0.35, coding: 0.40 }
interview_score = w_mcq * mcq_score + w_desc * desc_score + w_code * code_score
```

Grade bands: A+ (90+), A (80+), B+ (70+), B (60+), C+ (50+), C (40+), D (30+), F (<30)

---

## 11. Component 3 — Ranking (Port 8003)

### Endpoints
```
POST /api/v1/rank/compute
  Body: { job_role, candidates: [{ candidate_id, candidate_name, skills, experience_years, education, cv_score?, interview_score? }], w_cv: 0.6, w_int: 0.4, use_ltr: false, include_skill_gap: false }
  Returns: { ranked_candidates: [{ candidate_id, candidate_name, composite_score, cv_score, interview_score, skill_gap_score }], job_id, weights }

GET /api/v1/rank/results/{job_id}
  Returns: Stored ranking

POST /api/v1/rank/weights
  Body: { job_role, w_cv, w_int }
  Returns: Saved weight profile

GET /api/v1/rank/explain/{candidate_id}
  Returns: { feature_contributions: [{ feature, contribution }] }

GET /api/v1/rank/jobs
  Returns: { roles: { key: display_name } }  (dict, NOT list)
```

### Scoring
```
composite_score = w_cv * cv_score + w_int * interview_score
```

### Hard Filters
- Education below minimum → auto-reject with reason
- Experience below minimum → penalty

---

## 12. Component 4 — Skill Gap / Career / Progress / Analytics (Port 8004)

### Skill Gap
```
POST /api/v1/skill-gap/analyze
  Body: { candidate_id, candidate_name, job_role, skills: [], experience_years, education, semantic_score?, skill_score?, experience_score?, education_score? }
  Returns: { data: { gap_score, hire_probability, severity, missing_skills, roadmap_nodes, learning_plan: [{ skill, resources: [{ title, url, platform }] }] } }

GET /api/v1/skill-gap/report/{candidate_id}
GET /api/v1/skill-gap/reports?skip=0&limit=10
DELETE /api/v1/skill-gap/report/{candidate_id}
GET /api/v1/skill-gap/roles
```

### Career Path
```
POST /api/v1/career/path
  Body: { candidate_id, current_role, target_role, skills: [], experience_years }
  Returns: { path_nodes: [{ role, description, skills_to_learn, duration }], lateral_options: [{ role }], skill_gap }

GET /api/v1/career/resources/{job_role}
  Returns: { courses: [{ title, url, platform, skill }] }

GET /api/v1/career/roles
  Returns: { roles: [{ id, name, category }] }

GET /api/v1/career/roadmap/{candidate_id}
  Returns: Saved roadmap (from latest skill gap report, field: roadmap_nodes)
```

### Progress
```
POST /api/v1/progress/update
  Body: { candidate_id, skill, status: "not_started"|"in_progress"|"completed", notes? }
  Returns: Updated progress

GET /api/v1/progress/{candidate_id}
  Returns: { progress: [{ skill, status, notes }], stats: { not_started, in_progress, completed, total, completion_pct } }

DELETE /api/v1/progress/{candidate_id}
```

### Analytics
```
GET /api/v1/analytics/summary
  Returns: { total_reports, severity_distribution, avg_hire_prob, avg_gap_score, top_missing_skills, progress_summary }

GET /api/v1/analytics/leaderboard?limit=10
  Returns: { leaderboard: [{ candidate_id, candidate_name, job_role, hire_probability }] }

GET /api/v1/analytics/role-insights/{job_role}
  Returns: { count, avg_match, avg_hire_prob, avg_gap_score }
```

---

## 13. Frontend Structure

### File Structure
```
frontend/
├── index.html
├── package.json          (react, react-dom, react-router-dom, recharts, react-hot-toast, lucide-react, axios)
├── vite.config.js
└── src/
    ├── main.jsx          (BrowserRouter, ThemeProvider, PipelineProvider, Toaster)
    ├── App.jsx           (Routes, Sidebar, lazy-loaded pages)
    ├── index.css         (CSS variables for dark/light, all component styles)
    ├── api.js            (axios instances C0-C4 with JWT interceptor)
    ├── chartTheme.js     (Recharts theme-aware tooltip/axis colors)
    ├── context/
    │   ├── ThemeContext.jsx   (dark/light toggle, localStorage)
    │   └── PipelineContext.jsx
    └── pages/
        ├── Landing.jsx
        ├── auth/
        │   ├── CompanyLogin.jsx
        │   ├── CompanyRegister.jsx
        │   ├── CandidateLogin.jsx
        │   └── CandidateRegister.jsx
        ├── CandidateDashboard.jsx
        ├── CompanyDashboard.jsx
        ├── JobBoard.jsx
        ├── Interview.jsx
        ├── CVMatch.jsx
        ├── Ranking.jsx
        ├── SkillGap.jsx
        ├── CareerPath.jsx
        ├── Progress.jsx
        └── Leaderboard.jsx
```

### Routing
```
/                          → Landing
/login/company             → CompanyLogin
/register/company          → CompanyRegister
/login/candidate           → CandidateLogin
/register/candidate        → CandidateRegister
/candidate/dashboard       → CandidateDashboard (private, role=candidate)
/candidate/jobs            → JobBoard (private, role=candidate)
/candidate/interview       → Interview (private, role=candidate)
/company/dashboard         → CompanyDashboard (private, role=company)
/pipeline/cv-match         → CVMatch (private)
/pipeline/ranking          → Ranking (private)
/pipeline/skill-gap        → SkillGap (private)
/pipeline/career-path      → CareerPath (private)
/pipeline/progress         → Progress (private)
/pipeline/leaderboard      → Leaderboard (private)
```

### Sidebar Navigation
- **Candidate sees**: Dashboard, Browse Jobs, Interview, CV Match, Skill Gap, Career Path, Progress
- **Company sees**: Dashboard, Ranking, Leaderboard
- **No sidebar** on Landing/Auth pages
- Sidebar has: dark/light toggle, sign out button, collapsible

### Design System (CSS Variables)
```css
:root {
  --bg: #0a0a14;
  --surface: #12122a;
  --card: #141430;
  --border: #1e1e3a;
  --accent: #7c6cff;
  --accent-2: #00e4b8;
  --text: #e8e8ff;
  --text-muted: #6a6a8e;
  --danger: #ff5c7a;
  --warn: #ffb347;
  --input-bg: #12122a;
}

[data-theme="light"] {
  --bg: #f4f4f8;
  --surface: #ffffff;
  --card: #ffffff;
  --border: #e0e0e8;
  --text: #1a1a2e;
  --text-muted: #6a6a8e;
  --input-bg: #f0f0f5;
}
```

### Key UI Requirements
- All pages use `className="fade-in"` for enter animation
- Stats use `className="stat"` with `.stat-label` and `.stat-value`
- Cards use `className="card"`
- Chips use `className="chip"`
- Buttons: `.btn` (primary), `.btn-ghost` (secondary), `.btn-sm` (small), `.btn-success` (green)
- Tables use `className="table"`
- All charts use `getChartTheme()` for theme-aware tooltip/axis colors
- Toast notifications for all actions
- Loading states on all async operations
- Empty states with icons when no data

### Landing Page
- Hero: "Hire Smarter. Grow Faster." with two CTAs
- "I'm Hiring" → /register/company
- "I'm Looking for Work" → /register/candidate
- Login links below
- How It Works: 4 feature cards
- 20 supported roles as chips

### Candidate Dashboard
- Stats: Resumes count, Jobs Available, Match Scores
- Upload Resume (file input, PDF/DOCX/TXT)
- Quick Actions: Browse Jobs, Take Interview, Skill Gap
- Recent Jobs list with Apply button
- Recent Match Scores

### Job Board
- Search bar (title, location, department)
- Job cards with: title, location, type, department, skills chips, Apply button
- Apply requires resume uploaded

### Company Dashboard
- Stats: Posted Jobs, Active Positions, Departments
- Post New Job form (title, department, location, type, skills, description)
- Job listings with Applicants button and Delete

### Interview Page
Three steps:
1. **Setup**: Select role from dropdown, see skills tested, Start button
2. **Quiz**: Progress bar, question type badge (MCQ/Descriptive/Coding), answer input, Previous/Next/Submit
3. **Result**: Overall score, grade, score breakdown bar chart, weak areas chips

### CV Match
- Select resume + optional target job
- Run Match button
- Results: Overall/Semantic/Skills/Experience scores, predicted role, matched/missing skills, career suggestions

### Skill Gap
- Form: name, target role, skills, experience, education
- Results: Gap score, Hire probability, Severity, Missing skills, Learning plan with resources

### Career Path
- Form: current role → target role, skills, experience
- Results: Step-by-step timeline with role nodes, skills to learn, lateral options

### Progress
- SVG completion ring, Not Started/In Progress/Completed counts
- Update form: skill name, status dropdown
- Skills list with status icons

### Leaderboard
- Medal icons (gold/silver/bronze) for top 3
- Candidate cards with hire probability

---

## 14. Docker Setup

### Dockerfile (multi-stage)
```dockerfile
# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python dependencies
FROM python:3.12-slim AS deps
WORKDIR /app
COPY recruit-ai/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist
COPY recruit-ai/backend/ /app/recruit-ai/backend/
COPY component1/ /app/component1/
COPY component2/ /app/component2/
COPY component3/ /app/component3/
COPY component4/ /app/component4/
EXPOSE 8000 8001 8002 8003 8004
CMD ["python", "-m", "uvicorn", "recruit-ai.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: "3.8"
services:
  mongodb:
    image: mongo:7
    ports: ["27017:27017"]
  backend:
    build: .
    ports: ["8000:8000"]
    depends_on: [mongodb]
    environment:
      MONGO_URI: mongodb://mongodb:27017
      JWT_SECRET: your-secret-key
  frontend:
    image: nginx:alpine
    ports: ["5174:80"]
    volumes: ["./frontend/dist:/usr/share/nginx/html"]
  c1:
    build: .
    command: python -m uvicorn component1.backend.main:app --port 8001
    ports: ["8001:8001"]
  c2:
    build: .
    command: python -m uvicorn component2.backend.main:app --port 8002
    ports: ["8002:8002"]
  c3:
    build: .
    command: python -m uvicorn component3.backend.main:app --port 8003
    ports: ["8003:8003"]
  c4:
    build: .
    command: python -m uvicorn component4.backend.main:app --port 8004
    ports: ["8004:8004"]
```

---

## 15. Requirements

### recruit-ai/backend/requirements.txt
```
fastapi
uvicorn
motor
pymongo
bcrypt
python-jose[cryptography]
python-multipart
scikit-learn
pandas
numpy
PyMuPDF
pdfminer.six
python-docx
openpyxl
reportlab
nltk
```

### component2/backend/requirements.txt
```
fastapi
uvicorn
pymongo
pydantic
```

### component4/backend/requirements.txt
```
fastapi
uvicorn
pymongo
pydantic
scikit-learn
pandas
numpy
```

---

## 16. Testing

### Smoke Test
Check all 6 services respond:
- C1 health: GET http://localhost:8001/health
- C2 health: GET http://localhost:8002/health
- C3 health: GET http://localhost:8003/health
- C4 health: GET http://localhost:8004/health
- Unified: GET http://localhost:8000/health
- Frontend: GET http://localhost:5174 (returns HTML with #root)

### Contract Test
Full pipeline:
1. Create job via C1
2. Match CV via C1
3. Start + submit interview via C2
4. Rank candidates via C3
5. Analyze skill gap via C4
6. Get career path via C4
7. Update + get progress via C4
8. Get leaderboard via C4

---

## 17. Key Implementation Notes

1. **No SBERT at runtime** — use TF-IDF for semantic similarity. SBERT takes 60+ seconds to load on CPU.
2. **Experience years capped at 50** — regex can match false positives like "148 years".
3. **All db calls in C2 must be `await`ed** — they are async functions.
4. **`/api/v1/rank/jobs` returns a dict** `{ roles: { key: display_name } }`, not a list.
5. **`/api/v1/resume/match` job_id is optional** — match works without a target job.
6. **Frontend uses `React.lazy`** for code splitting — main bundle stays under 260KB.
7. **CSS variables** for theming — no inline hex colors for theme-dependent elements.
8. **JWT stored in localStorage** as `recruitai.token`, role as `recruitai.role`.
9. **CORS**: Backend must allow `http://localhost:5174` with credentials.
10. **MongoDB indexes**: Create on `users.email` (unique), `jobs.company_id`, `resumes.candidate_id`, `predictions.candidate_id`.

---

## 18. What "Done" Looks Like

- [ ] `npm run build` succeeds with no errors
- [ ] All 6 services start and respond to health checks
- [ ] Candidate can register, login, upload resume, browse jobs, apply, take interview
- [ ] Company can register, login, post jobs, see applicants
- [ ] CV match returns meaningful scores
- [ ] Interview returns MCQ/Descriptive/Coding questions and scores them
- [ ] Ranking computes composite scores
- [ ] Skill gap analysis returns missing skills and learning plan
- [ ] Career path shows step-by-step transition
- [ ] Progress tracking works with status updates
- [ ] Leaderboard shows top candidates
- [ ] Export (CSV/Excel/PDF) works
- [ ] Dark/light theme toggle works
- [ ] All 20 roles supported consistently across all components
- [ ] 93+ tests passing (smoke + contract + enhanced)
