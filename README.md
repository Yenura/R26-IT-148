# AI-Driven Recruitment Ecosystem
### Intelligent Candidate Matching, Automated Multi-Modal Technical Assessments & Predictive Career Development

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18_%2B_Vite-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB_Atlas-47A248.svg?logo=mongodb&logoColor=white)](https://mongodb.com)
[![LightGBM](https://img.shields.io/badge/ML-LightGBM_LambdaMART-FF6F00.svg)](https://lightgbm.readthedocs.io)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![PyTorch](https://img.shields.io/badge/Deep_Learning-PyTorch-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org)
[![Tests](https://img.shields.io/badge/Tests-168%20Passed%20(100%25)-brightgreen.svg)](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/component1/tests/)

> **SLIIT Final-Year Research Project (R26-IT-148)**  
> An enterprise-grade, high-performance multi-microservice AI recruitment and career platform that unites automated CV parsing and NER extraction, dynamic speech-to-text technical interviews, listwise Learning-to-Rank (LTR) candidate selection, and priority-weighted skill gap career pathways into one unified SaaS platform.

---

## 📚 Technical Documentation Index

Detailed, research-grade technical documentation for each component is available in the [`/docs`](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/docs) directory:

| Component | Technical Document | Primary Machine Learning Model | Key Metric / Accuracy |
| :--- | :--- | :--- | :--- |
| **Master Index** | [PROJECT_COMPONENT_DOCUMENTATION_INDEX.md](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/docs/PROJECT_COMPONENT_DOCUMENTATION_INDEX.md) | Platform Architecture & Integration | Multi-Microservice Gateway |
| **Component 1** | [COMPONENT_1_TECHNICAL_DOCUMENTATION.md](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/docs/COMPONENT_1_TECHNICAL_DOCUMENTATION.md) | Balanced Logistic Regression (`cv_classifier.pkl`) | **`90.49%`** Acc \| **`93.47%`** F1 |
| **Component 2** | [COMPONENT_2_TECHNICAL_DOCUMENTATION.md](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/docs/COMPONENT_2_TECHNICAL_DOCUMENTATION.md) | Sentence-BERT (`all-mpnet-base-v2`) + Whisper STT | **`r = 0.884`** \| **`7.2%`** WER |
| **Component 3** | [COMPONENT_3_TECHNICAL_DOCUMENTATION.md](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/docs/COMPONENT_3_TECHNICAL_DOCUMENTATION.md) | LightGBM LambdaMART Listwise LTR | **`NDCG@1 = 0.9784`** \| **`MAP = 0.9776`** |
| **Component 4** | [COMPONENT_4_TECHNICAL_DOCUMENTATION.md](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/docs/COMPONENT_4_TECHNICAL_DOCUMENTATION.md) | Multi-Model GBDT Ensemble (`train_model.py`) | **`91.50%`** Acc \| **`97.63%`** ROC-AUC |

---

## ⚡ Fast Run — 1-Click Launch (Recommended)

You can launch the entire ecosystem (all 5 backend microservices + React frontend + automated browser launch) with a single command:

### Option A: PowerShell / CMD (Terminal)
```powershell
.\start_all.ps1
# or
.\start_all.bat
```

### Option B: Windows Explorer (1-Click Double Click)
Open Windows File Explorer, navigate to the project directory, and double-click:
```cmd
start_all.bat
```

### Option C: Python Master Launcher
```bash
# Using project virtual environment
.\.venv\Scripts\python.exe start_all.py

# Or using system python
python start_all.py
```

> **What happens during 1-Click Launch?**
> 1. Starts all 5 FastAPI backend microservices concurrently (Ports `8000`, `8001`, `8002`, `8003`, `8004`).
> 2. Starts the Vite React frontend server (Port `5174`).
> 3. Executes automated health probes until all microservices report `[ONLINE & HEALTHY]`.
> 4. Automatically opens your default web browser to `http://localhost:5174`.
> 5. Press **Ctrl + C** in the terminal at any time to gracefully terminate all services together.

---

## 🧭 System Architecture & Service Ports

The ecosystem is built on a decoupled, asynchronous microservices architecture with a shared MongoDB Atlas data layer and a high-performance React single-page frontend:

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │            User (Candidate / Corporate Recruiter)      │
                                  └───────────────────────────┬────────────────────────────┘
                                                              │
                                                [Vite + React Single-Page Web App]
                                                     (Port 5174 / Host Strict)
                                                              │
                                  ┌───────────────────────────▼────────────────────────────┐
                                  │           RecruitAI Unified API Gateway / Router       │
                                  │                     (Port 8000)                        │
                                  └───────┬───────────────────┬───────────────────┬────────┘
                                          │                   │                   │
                     ┌────────────────────▼─────┐   ┌─────────▼─────────┐   ┌─────▼────────────────────┐
                     │   Component 1 (Port 8001)│   │Component 2 (Port 8002)│Component 4 (Port 8004)   │
                     │  Resume Parsing & NER    │   │Technical Interview│   │Skill Gap Sandbox & GBDT  │
                     │  S_skill, S_exp, S_edu   │   │P_mcq, P_desc, P_code│Career Progression Pathways │
                     └────────────────────┬─────┘   └─────────┬─────────┘   └──────────────────────────┘
                                          │                   │
                                          └─────────┬─────────┘
                                                    │
                                        ┌───────────▼───────────┐
                                        │ Component 3 (Port 8003)│
                                        │ LambdaMART LTR & CSS  │
                                        │  0.40·S_cv + 0.60·S_int│
                                        └───────────┬───────────┘
                                                    │
                                  ┌─────────────────▼──────────────────┐
                                  │      MongoDB Atlas Cluster         │
                                  │ (Resumes, Sessions, Ranks, Taxonomies)│
                                  └────────────────────────────────────┘
```

| Service | Component Name | Port | Health Check URL | Primary Responsibilities |
| :--- | :--- | :---: | :--- | :--- |
| **Frontend** | React UI Platform | **5174** | `http://localhost:5174` | Candidate & Recruiter Dashboards, Sandbox, Visualizations |
| **C0 Gateway** | Unified Core Backend | **8000** | `http://localhost:8000/health` | Auth, Job Board, Resumes, Gateway Aggregator |
| **Component 1** | CV Intelligence & Roles | **8001** | `http://localhost:8001/health` | PDF/DOCX Parsing, 400+ Skill Extraction, $S_{skill}, S_{exp}, S_{edu}$ |
| **Component 2** | AI Technical Interview | **8002** | `http://localhost:8002/health` | RAIGS Question Bank (18,757 Qs), SBERT Grader, Whisper STT |
| **Component 3** | Candidate Ranking LTR | **8003** | `http://localhost:8003/health` | LightGBM LambdaMART LTR, CSS Fusion ($40\% S_{cv} + 60\% S_{int}$) |
| **Component 4** | Skill Gap & Career | **8004** | `http://localhost:8004/health` | GBDT Hireability ($91.5\%$), What-If Sandbox, Career Pathfinding |

---

## 🔬 Research Components & Mathematical Formulations

### Component 1: Automated Resume Screening & Role Classification
- **Primary Model**: 67-Dimensional Feature Engineering + Balanced Multinomial Logistic Regression (`cv_classifier.pkl`).
- **Baseline Model**: Sublinear TF-IDF (1-2 N-Grams) + Logistic Regression (`tfidf_baseline.pkl`).
- **Key Empirical Metrics**: **`90.49%` Test Accuracy**, **`93.47%` Macro F1**, **`90.36%` 5-Fold Cross-Validation** on 736 independent test resumes across 20 canonical IT roles.
- **Context-Guarded Entity Extraction**: Regular expression token boundaries with look-arounds preventing false positives on ambiguous single letters (`C`, `R`, `Go`, `REST`, `Spring`, `Dart`, `Less`).
- **Date Interval Merging**: Timeline interval merging for concurrent employment records to eliminate false tenure inflation.
- **Tri-Pillar Scoring Formulation**:
  $$S_{cv} = 0.50 \cdot S_{skill} + 0.30 \cdot S_{exp} + 0.20 \cdot S_{edu}$$
  $$\text{where } S_{skill}, S_{exp}, S_{edu} \in [0.0, 100.0]$$

---

### Component 2: AI-Driven Technical Interview Evaluation
- **Tri-Modal Assessment**:
  - **Foundational Concepts ($P_{mcq}$)**: Automated multiple-choice evaluation.
  - **Descriptive / Spoken Theory ($P_{desc}$)**: Sentence-BERT (`all-mpnet-base-v2`, 768-dim embeddings) dense semantic cosine similarity combined with key concept recall.
  - **Algorithmic Coding ($P_{code}$)**: AST syntax validation, secure execution sandbox with restricted imports, and automated unit test assertion suites.
- **Speech-to-Text Transcription**: OpenAI Whisper engine with technical vocabulary prompting (**`7.2%` Word Error Rate**).
- **Question Corpus**: **`18,757 Verified Technical Questions`** across 20 canonical IT roles.
- **Role-Tailored Scoring Formulation**:
  $$S_{int} = w_{mcq} \cdot P_{mcq} + w_{desc} \cdot P_{desc} + w_{code} \cdot P_{code}$$
  *(e.g., Software Engineer: $20\% / 30\% / 50\%$; Cloud Solutions Architect: $45\% / 55\% / 0\%$)*.

---

### Component 3: Multi-Criteria Candidate Scoring (CSS) & LambdaMART LTR
- **Machine Learning Ranker**: **LightGBM LambdaMART** (`objective='lambdarank'`) optimizing listwise ranking metrics using pairwise Lambda gradients ($\lambda_{ij} = -\sigma / (1 + e^{\sigma(s_i - s_j)}) \cdot |\Delta \text{NDCG}_{ij}|$).
- **Candidate Scoring System (CSS)**:
  $$\text{CSS} = 0.40 \cdot S_{cv} + 0.60 \cdot S_{int}$$
- **Empirical Weight Justification**: Work-sample assessments and live technical interviews demonstrate higher predictive validity ($r \approx 0.58$) for software engineering job performance than self-reported resumes alone ($r \approx 0.35$). The $40/60$ split prevents resume inflation while rewarding proven industry tenure.
- **Empirical Benchmarks (3,000 Candidates / 20 Roles)**:
  - **NDCG@1**: **`0.9784 (97.84%)`**
  - **NDCG@3**: **`0.9842 (98.42%)`**
  - **NDCG@5**: **`0.9437 (94.37%)`**
  - **Mean Average Precision (MAP)**: **`0.9776 (97.76%)`**
  - **Spearman Rank Correlation ($\rho$)**: **`0.6232`** ($p < 0.001$).
- **Fairness & Explainability**: TreeSHAP feature attributions and automated EEOC Four-Fifths rule disparate impact auditing.

---

### Component 4: Skill Gap Intelligence & Multi-Model Hireability Ensemble
- **Machine Learning Classifier**: Multi-Model Supervised Learning Ensemble evaluated on **20,000 Verified Candidate Records**:
  - **Gradient Boosted Decision Trees (GBDT)**: **`91.50%` Accuracy**, **`97.63%` ROC-AUC**, **`86.72%` Macro F1**.
  - **Random Forest (RF)**: **`90.85%` Accuracy**, **`97.12%` ROC-AUC**.
  - **Logistic Regression (LR)**: **`89.40%` Accuracy**, **`96.50%` ROC-AUC**.
- **Interactive "What-If" Simulation Sandbox**: Sub-8ms real-time skill delta projection ($\Delta \text{Score} = S_{\text{sim}} - S_{\text{current}}$).
- **Career Pathfinding**: Directed Acyclic Graph (DAG) topological learning milestone generation and cosine transition graph mapping for adjacent career moves.

---

## 🚀 Manual Step-by-Step Installation

If you prefer to configure and run the services individually:

### 1. Prerequisites
- **Python 3.10 – 3.12**
- **Node.js 18+** and `npm`
- **MongoDB Atlas** or Local MongoDB (Port 27017)
- **Git**

### 2. Python Virtual Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-username/R26-IT-148.git
cd R26-IT-148

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install dependencies across all components
pip install -r recruit-ai/backend/requirements.txt
pip install -r component1/backend/requirements.txt
pip install -r component2/backend/requirements.txt
pip install -r component3/backend/requirements.txt
pip install -r component4/backend/requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 4. Running Microservices Individually
Open separate terminals and run each service:
```bash
# C0 Unified Gateway Backend (Port 8000)
cd recruit-ai/backend && uvicorn main:app --port 8000 --reload

# Component 1 (Port 8001)
cd component1/backend && uvicorn main:app --port 8001 --reload

# Component 2 (Port 8002)
cd component2/backend && uvicorn main:app --port 8002 --reload

# Component 3 (Port 8003)
cd component3/backend && uvicorn main:app --port 8003 --reload

# Component 4 (Port 8004)
cd component4/backend && uvicorn main:app --port 8004 --reload

# React Frontend (Port 5174)
cd frontend && npm run dev
```

---

## 🔑 Pre-Configured Demo Accounts

| Role | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Candidate (Job Seeker)** | `candidate@demo.com` | `Candidate@123` | CV Upload, Match Scoring, AI Interview Sandbox, Skill Gap Simulator, Career Roadmap |
| **Recruiter / Employer** | `recruiter@demo.com` | `Recruiter@123` | Post Jobs, Pipeline Management, LambdaMART Candidate Ranking, Dossier Export |

---

## 🧪 Automated Testing & Verification Suite

The repository contains automated test suites covering parsing boundaries, mathematical formulas, and ML inference:

```bash
# Run Component 1 Test Suite (168 Tests)
pytest component1/tests/ -v

# Run Model Accuracy Audit Script across all 4 Components
python show_accuracy.py
```

### Test Suite Execution Output:
```
============================== 168 passed in 106.10s ==============================
Result: 100% Pass Rate (0 Failures, 0 Errors)
```

---

## 📦 Project Directory Structure

```
R26-IT-148/
├── docs/                                  # Comprehensive Technical Documentation (4 Components + Index)
│   ├── COMPONENT_1_TECHNICAL_DOCUMENTATION.md
│   ├── COMPONENT_2_TECHNICAL_DOCUMENTATION.md
│   ├── COMPONENT_3_TECHNICAL_DOCUMENTATION.md
│   ├── COMPONENT_4_TECHNICAL_DOCUMENTATION.md
│   └── PROJECT_COMPONENT_DOCUMENTATION_INDEX.md
│
├── start_all.bat                          # Windows 1-Click Master Launcher
├── start_all.ps1                          # PowerShell 1-Click Master Launcher
├── start_all.py                           # Python Master Launcher
├── start_servers.py                       # Backend Microservices Daemon Launcher
├── show_accuracy.py                       # Automated Multi-Component ML Accuracy Verifier
├── README.md                              # Master System Documentation
│
├── recruit-ai/                            # Unified API Gateway & Core Backend (Port 8000)
│   └── backend/
│       ├── main.py                        # FastAPI Gateway Entrypoint & MongoDB Connection
│       ├── config.py                      # Environment Variables & JWT Settings
│       ├── routers/                       # Auth, Jobs, Resumes, Rankings, Exports
│       └── services/                      # Document Ingestion, SBERT Matching, Auth Services
│
├── component1/                            # Component 1: Resume Screening & NER (Port 8001)
│   ├── backend/                           # FastAPI Router, Scorer Service, Predictor Wrapper
│   ├── ml/                                # Extractor, Feature Engineering, Training & Evaluation
│   ├── models/                            # Serialized Models (cv_classifier.pkl, label_encoder.pkl)
│   └── tests/                             # 168 Unit, Bounds, and Integration Tests
│
├── component2/                            # Component 2: AI Technical Interview (Port 8002)
│   ├── backend/                           # FastAPI Router, Session Store, Audio Stream Handler
│   ├── ml/                                # RAIGS Q-Generator, SBERT Grader, Whisper Transcriber
│   └── models/                            # 18,757 Question Bank Corpus & T5 Checkpoints
│
├── component3/                            # Component 3: LambdaMART Candidate Ranking (Port 8003)
│   ├── backend/                           # FastAPI Ranking Router & Pipeline Aggregator
│   ├── ltr/                               # LightGBM LambdaMART Listwise Model
│   ├── engine/                            # Candidate Scoring System (CSS) & Hard Filters
│   └── explainability/                    # TreeSHAP Feature Attributions & Fairness Auditor
│
├── component4/                            # Component 4: Skill Gap & Career Pathways (Port 8004)
│   ├── backend/                           # FastAPI Analytics Router
│   ├── ml/                                # 20k GBDT Ensemble Classifier Training Scripts
│   └── src/                               # DAG Gap Analyzer, What-If Simulator, Career Pathfinder
│
└── frontend/                              # React 18 + Vite Production Frontend (Port 5174)
    ├── src/
    │   ├── pages/                         # CandidateDashboard, CompanyDashboard, CVMatch, Ranking, Interview, SkillGap
    │   ├── components/                    # PageHeader, StatCard, ScoreMeter, UploadZone, ErrorBoundary
    │   └── api.js                         # Axios Client with In-Memory Caching & Fast Retries
    └── dist/                              # High-Performance Production Build
```

---

## 📜 License & Academic Acknowledgments

- **Academic Institution:** Sri Lanka Institute of Information Technology (SLIIT)
- **Course / Degree:** B.Sc. (Hons) in Information Technology
- **Project Code:** R26-IT-148
- **Project Title:** AI-Driven Recruitment Ecosystem & Predictive Career Development
- **License:** MIT License — See [`LICENSE`](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/LICENSE) for details.
