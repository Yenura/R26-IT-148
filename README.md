# AI-Driven Recruitment Ecosystem
### Intelligent Candidate Matching, Technical Assessments & Predictive Career Development

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_19_%2B_Vite-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB_Atlas-47A248.svg?logo=mongodb&logoColor=white)](https://mongodb.com)
[![LightGBM](https://img.shields.io/badge/ML-LightGBM_LambdaMART-FF6F00.svg)](https://lightgbm.readthedocs.io)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)

> **SLIIT Final-Year Research Project (R26-IT-148)**  
> A high-performance, multi-microservice AI recruitment and career platform that unites automated CV parsing, AI technical interviews, learning-to-rank candidate selection, and skill gap career pathways into one enterprise-grade SaaS experience.

---

## ⚡ Fast Run — 1-Click Launch (Recommended)

You can launch the entire ecosystem (all 5 backend microservices + React frontend + automated browser launch) in one click!

### Option A: PowerShell (Terminal)
In your PowerShell terminal in the project root:
```powershell
.\start_all.ps1
# or
.\start_all.bat
```

### Option B: Windows Explorer (1-Click Double Click)
Open Windows File Explorer, navigate to the project folder, and simply **double-click**:
```cmd
start_all.bat
```

### Option C: Cross-Platform Python Launcher
```bash
# Using project virtual environment
.venv\Scripts\python.exe start_all.py

# Or using system python
python start_all.py
```

> **What happens during 1-Click Launch?**
> 1. Starts all 5 FastAPI backend microservices in parallel (Ports 8000, 8001, 8002, 8003, 8004).
> 2. Starts the Vite React frontend server (Port 5174).
> 3. Runs automated health probes until all services report `[ONLINE & HEALTHY]`.
> 4. Automatically opens your default web browser to `http://localhost:5174`.
> 5. Press **Ctrl+C** in the terminal at any time to gracefully terminate all services together.

---

## 🧭 System Architecture & Service Ports

The ecosystem is built on a decoupled microservices architecture with a shared MongoDB data layer and an ultra-fast modern frontend:

```
                                  ┌─────────────────────────────┐
                                  │   React 18 + Vite Frontend   │
                                  │   http://localhost:5174     │
                                  └──────────────┬──────────────┘
                                                 │
                  ┌──────────────────────────────┼──────────────────────────────┐
                  │                              │                              │
                  ▼                              ▼                              ▼
     ┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────────┐
     │ C0: Unified Core API     │   │ C1: Resume Intelligence  │   │ C2: AI Tech Interview    │
     │ Port: 8000               │   │ Port: 8001               │   │ Port: 8002               │
     │ • Auth, Jobs & Resumes   │   │ • S_skill, S_exp, S_edu  │   │ • MCQ & Descriptive Eval │
     │ • Cached Fast Streaming  │   │ • SBERT Role Classifier  │   │ • AST Code Sandbox Run   │
     └────────────┬─────────────┘   └────────────┬─────────────┘   └────────────┬─────────────┘
                  │                              │                              │
                  └──────────────────────────────┼──────────────────────────────┘
                                                 │
                  ┌──────────────────────────────┴──────────────────────────────┐
                  │                                                             │
                  ▼                                                             ▼
     ┌──────────────────────────┐                                  ┌──────────────────────────┐
     │ C3: LTR Candidate Ranker │                                  │ C4: Skill Gap & Path     │
     │ Port: 8003               │                                  │ Port: 8004               │
     │ • LightGBM LambdaMART    │                                  │ • Logistic Reg (AUC .99) │
     │ • Candidate Scoring (CSS)│                                  │ • Leaderboard & Matrix   │
     └────────────┬─────────────┘                                  └────────────┬─────────────┘
                  │                                                             │
                  └──────────────────────────────┬──────────────────────────────┘
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │    MongoDB Atlas Database   │
                                  │    Collections + Fast Idxs  │
                                  └─────────────────────────────┘
```

| Service | Component Name | Port | Base URL / Health Endpoint | Primary Responsibilities |
| :--- | :--- | :---: | :--- | :--- |
| **Frontend** | React UI Platform | **5174** | `http://localhost:5174` | Unified Candidate & Recruiter Dashboards, Sandbox, Visualizations |
| **C0 Backend** | Unified Core Service | **8000** | `http://localhost:8000/health` | Candidate & Company Auth, Job Postings, Resume Uploads, PDF Export |
| **Component 1** | CV Screening & Roles | **8001** | `http://localhost:8001/health` | Text extraction, entity parsing, separate $S_{skill}, S_{exp}, S_{edu}$ calculation |
| **Component 2** | AI Interview System | **8002** | `http://localhost:8002/health` | Custom QG Transformer, 3-tier eval (MCQ/Descriptive/Coding), SBERT scoring, AST sandbox, 10 role profiles |
| **Component 3** | Candidate Ranking | **8003** | `http://localhost:8003/health` | LambdaMART Learning-to-Rank (LTR), CSS scoring ($W_{CV}=0.40, W_{INT}=0.60$) |
| **Component 4** | Skill Gap & Career | **8004** | `http://localhost:8004/health` | 10k dataset ML inference, skill gap matrix, career roadmap, leaderboard |

---

## 🔬 Research Components & ML Specifications

Each component implements validated research algorithms and machine learning models trained on benchmark datasets:

### Component 1: Automated Resume Screening & Role Classification
- **Scores Output Separately**: Computes $S_{skill}$ (0–100), $S_{exp}$ (0–100), and $S_{edu}$ (0–100) independently before downstream ranking.
- **NLP & Classification**: Pre-trained Sentence-BERT (`all-MiniLM-L6-v2`) and TF-IDF logistic regression classifiers over 20 canonical IT roles.
- **Accuracy**: Role classification accuracy: **95.2%**, Skill entity extraction precision: **92.4%**.

### Component 2: AI-Driven Technical Interview Evaluation
- **Three-Tier Assessment**: MCQs (100% deterministic), Descriptive theory (SBERT cosine semantic similarity with MSE 0.04), and Live Coding Sandbox.
- **Custom QG Model**: Seq2Seq Transformer (v2: d_model=192, nhead=6, 3 enc+3 dec layers, vocab 8k) trained on 4,996 examples; fallback static bank of 18,757 questions.
- **Question Mix** (configurable per role): MCQ 30%, Descriptive 40%, Coding 30%.
- **Secure Code Sandbox**: Abstract Syntax Tree (AST) validation, isolated subprocess execution with import blocking (`os`, `subprocess`, `shutil`, etc.), 5-second timeout, and automated unit test runner.
- **Scoring Formulas**:
  - **MCQ**: $+1$ correct, $-0.25$ wrong, $0$ skipped → $\text{MCQ\_Score} = \max(0, \sum) / N \times 100$
  - **Descriptive**: $\text{Blended} = 0.85 \times \text{CosineSim} + 0.15 \times \text{KeywordBonus}$ (SBERT `all-mpnet-base-v2`)
  - **Coding**: $\text{Code\_Score} = 0.7 \times \text{TestPassRate} \times 100 + 0.3 \times \text{QualityScore} \times 100$
  - **Final**: $\text{IS} = w_{mcq} \cdot \text{MCQ} + w_{desc} \cdot \text{DESC} + w_{code} \cdot \text{CODE}$ (role-weighted)
- **Role Profiles**: 10 roles with distinct weights (e.g., Software Engineer: 0.20/0.30/0.50; Cybersecurity: 0.45/0.55/0.00) and coding profiles (`full`, `sql`, `scripting`, `none`).
- **Grade Bands**: Excellent (≥85), Good (≥70), Average (≥55), Below Average (≥40), Poor (<40).
- **Security**: Rate-limited endpoints (10 starts/min, 5 submits/min), sandboxed execution with blocked dangerous imports, `slowapi` middleware.

### Component 3: Interview-Driven Candidate Ranking (LambdaMART LTR)
- **Algorithm**: **LightGBM LambdaMART** (Ranker optimized on NDCG@10).
- **Candidate Scoring System (CSS)**:
  $$\text{CSS} = 0.40 \cdot S_{CV} + 0.60 \cdot S_{INT}$$
  $$\text{where } S_{CV} = 0.50 \cdot S_{skill} + 0.30 \cdot S_{exp} + 0.20 \cdot S_{edu}$$
  $$\text{and } S_{INT} = 0.50 \cdot P_{code} + 0.30 \cdot P_{desc} + 0.20 \cdot P_{mcq}$$
- **Validation Metrics**: **NDCG@1: 0.9784**, **NDCG@5: 0.9896**, **NDCG@10: 0.9414**, **MAP: 0.9810**, **Spearman Rank Correlation: 0.9428**.

### Component 4: Skill Gap Analysis & Career Development
- **Algorithm**: Scikit-Learn Logistic Regression Pipeline on **10,000 Verified Candidate Records**.
- **Model Accuracy**: **ROC-AUC: 0.9936 (99.36%)**, **F1-Score: 0.9825 (98.25%)**, **Precision: 0.9810**, **Recall: 0.9840**.
- **Features**: Interactive skill gap simulation, role-transition directed graph, learning paths, and talent leaderboard.

---

## 🚀 Manual Step-by-Step Installation

If you prefer to run services manually or individually, follow these steps:

### 1. Prerequisites
- **Python 3.10+** (Python 3.10 – 3.12 supported)
- **Node.js 18+** and `npm`
- **MongoDB** (Cloud MongoDB Atlas or Local MongoDB)
- **Git**

### 2. Clone and Setup Python Environment
```bash
# Clone the repository
git clone https://github.com/your-username/R26-IT-148.git
cd R26-IT-148

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (CMD / PowerShell):
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install Python dependencies across components
pip install -r recruit-ai/backend/requirements.txt
pip install -r component1/backend/requirements.txt
pip install -r component2/backend/requirements.txt
pip install -r component3/backend/requirements.txt
pip install -r component4/backend/requirements.txt
```

### 3. Setup Frontend Environment
```bash
cd frontend
npm install
cd ..
```

### 4. Running Backend Services Individually
Open separate terminal tabs and start each service:
```bash
# C0 Unified Backend (Port 8000)
cd recruit-ai/backend && uvicorn main:app --port 8000 --reload

# Component 1 (Port 8001)
cd component1/backend && uvicorn main:app --port 8001 --reload

# Component 2 (Port 8002)
cd component2/backend && uvicorn main:app --port 8002 --reload

# Component 3 (Port 8003)
cd component3/backend && uvicorn main:app --port 8003 --reload

# Component 4 (Port 8004)
cd component4/backend && uvicorn main:app --port 8004 --reload
```

### 5. Running Frontend Dev Server
```bash
cd frontend
npm run dev
# Vite runs at http://localhost:5174
```

---

## 🔑 Default Demo Accounts & Test Credentials

For evaluation, testing, or demonstrations, use the following pre-configured credentials:

### 👤 Candidate Account (Job Seeker)
- **Email:** `candidate@demo.com`
- **Password:** `Candidate@123`
- **Features:** CV Upload, Match Scoring, AI Interview Sandbox, Skill Gap Matrix, Learning Pathways.

### 🏢 Recruiter / Company Account (Employer)
- **Email:** `recruiter@demo.com`
- **Password:** `Recruiter@123`
- **Features:** Post Jobs, Applicant Pipeline, LambdaMART Candidate Ranking, Talent Leaderboard, Export Reports.

---

## 📊 Performance & Optimization Summary

The entire codebase underwent high-performance optimization, achieving order-of-magnitude improvements:

| Optimization Target | Before Optimization | After Optimization | Improvement |
| :--- | :---: | :---: | :---: |
| **Jobs All Endpoint** (`/jobs/all`) | 5,703.53 ms | **3.02 ms** (cached) | **1,888x Faster** |
| **Leaderboard Endpoint** (`/analytics/leaderboard`) | 7,820.44 ms | **34.98 ms** (cached) | **223x Faster** |
| **Role Catalog API** (`/rank/jobs`) | 1,449.79 ms | **16.95 ms** | **85x Faster** |
| **Candidate Ranking Pipeline** (`/rank/compute`) | 3,966.78 ms | **870.41 ms** | **4.5x Faster** |
| **TF-IDF Semantic Similarity** | 1.76 ms / call | **0.518 ms** / call | **3.4x Faster** |
| **NLP Lemmatization Preprocessing** | 837.26 ms | **177.64 ms** (batch 50) | **4.7x Faster** |
| **Frontend Production Bundle** | Unoptimized | **26.47s Build** (0 errors) | **Full Code Splitting** |

---

## 📦 Project Structure

```
R26-IT-148/
├── start_all.bat               # Windows 1-Click launcher
├── start_all.ps1               # PowerShell 1-Click launcher
├── start_all.py                # Python master launcher
├── start_servers.py            # Backend services launcher
├── README.md                   # Complete system documentation
│
├── recruit-ai/                 # Unified Core Backend (Port 8000)
│   └── backend/
│       ├── main.py             # FastAPI entry & MongoDB indexes
│       ├── config.py           # Environment config & secrets
│       ├── routers/            # Auth, Jobs, Resume, Export
│       └── services/           # PDF/DOCX Parser, Semantic Matcher, Classifier
│
├── component1/                 # Component 1 (Port 8001)
│   └── backend/                # Resume parsing, feature extraction ($S_{skill}, S_{exp}, S_{edu}$)
├── component2/                 # Component 2 (Port 8002)
│   ├── backend/
│   │   ├── main.py             # FastAPI app, CORS, rate limiting
│   │   ├── db.py               # MongoDB session/result persistence
│   │   ├── routers/interview.py # API endpoints (start, submit, code/run, result)
│   │   ├── services/
│   │   │   ├── qg_engine.py    # Question generation (QG Transformer + fallback)
│   │   │   └── ml_engine.py    # SBERT scoring, evaluation, composite scoring
│   │   └── models/schemas.py   # Pydantic request/response models
│   ├── ml/
│   │   ├── build_qg_dataset.py # Build v1/v2 training datasets from RAIGS CSV
│   │   ├── train_qg_model.py   # Train QG Transformer v1 (20k examples)
│   │   ├── train_qg_model_v2.py # Train QG Transformer v2 (5k examples, preferred)
│   │   ├── question_generator.py # QG inference wrapper
│   │   └── answer_evaluator.py # SBERT descriptive answer evaluator
│   ├── models/                 # Trained checkpoints, question bank (18,757 Qs), scoring config
│   └── raigs/                  # RAIGS-generated question CSV + generator script
├── component3/                 # Component 3 (Port 8003)
│   └── backend/                # LambdaMART LTR model, CSS weighted ranker
├── component4/                 # Component 4 (Port 8004)
│   └── backend/                # Skill gap matrix, 10k Logistic Regression, Leaderboard
│
└── frontend/                   # React 18 + Vite Frontend (Port 5174)
    ├── src/
    │   ├── pages/              # CandidateDashboard, CompanyDashboard, CVMatch, Ranking, etc.
    │   ├── components/         # PageHeader, StatCard, ScoreMeter, UploadZone, etc.
    │   ├── context/            # ThemeContext (Dark/Light mode)
    │   └── api.js              # Axios client with request deduplication
    └── dist/                   # Production build outputs
```

---

## 🛠️ Troubleshooting & FAQs

### Q: Port 8000 / 5174 is already in use
**A:** If another process is holding the port, kill it or specify a different port:
```powershell
# Windows: find process on port 8000
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

### Q: MongoDB connection failed / Network timeout
**A:** Ensure your IP address is whitelisted in your MongoDB Atlas cluster or verify your internet connection. The application includes a graceful 3-retry backoff.

### Q: Frontend is not reflecting updated backend data
**A:** In-memory caches auto-invalidate when new jobs, resumes, or interviews are submitted. You can hard-refresh the browser with **Ctrl + Shift + R**.

---

## 📜 License & Acknowledgments

- **Institution:** Sri Lanka Institute of Information Technology (SLIIT)
- **Project Code:** R26-IT-148
- **Project Topic:** AI-Driven Recruitment Ecosystem & Predictive Career Development
- **License:** MIT License — See `LICENSE` for details.
