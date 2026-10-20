# Component 2: AI Interview Generation & Evaluation

## Overview

**Component 2** is a complete AI-driven interview system that generates, administers, and automatically evaluates candidate interviews across three question types: MCQ, Descriptive, and Coding. It uses a **custom-trained QG Transformer model** for question generation and advanced NLP techniques (SBERT) for semantic evaluation.

**Port:** 8002  
**Status:** Ready for Integration  
**Version:** 2.0.0

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Component 2: Interview System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐  │
│  │   FastAPI        │  │   React          │  │  ML Models  │  │
│  │   Backend        │  │   Frontend       │  │  (SBERT +   │  │
│  │   (port 8002)    │  │   (port 5174)    │  │   QG Model) │  │
│  └──────────────────┘  └──────────────────┘  └─────────────┘  │
│         ▲                      ▲                    ▲            │
│         └──────────┬───────────┴────────────────────┘            │
│                    │                                              │
│         HTTP APIs (REST)                                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Services Layer                              │  │
│  │  • Interview Service (session management)                │  │
│  │  • QG Engine (custom Transformer question generation)    │  │
│  │  • Answer Evaluation Service (ML inference)              │  │
│  │  • Question Selector (relevance scoring)                 │  │
│  │  • Scoring Engine (composite scoring)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Data Layer                                  │  │
│  │  • QG Datasets (v1: 20,161 / v2: 4,996 train)           │  │
│  │  • Trained QG Model (Transformer)                        │  │
│  │  • Static Question Bank (fallback)                       │  │
│  │  • Scoring Configs (role-based weights)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 1️⃣ Custom QG Model for Question Generation
- **Custom-trained Transformer** — Seq2Seq model trained from scratch
- **Training datasets:** v1 20,161 train / 2,241 val; v2 4,996 train / 556 val
- **Data sources:** `raigs/RAIGS_generated_questions.csv` (AI-generated questions)
- **3 question types:** MCQ (30%), Descriptive (40%), Coding (30%)
- **Fallback:** Static question bank when model unavailable (18,757 questions)

### 2️⃣ Semantic Similarity Scoring (SBERT)
- Uses **Sentence-BERT (all-mpnet-base-v2)** for descriptive answer evaluation
- **Cosine similarity** between reference and candidate answers
- **Keyword coverage bonus** to reward use of technical terms

### 3️⃣ Automatic Evaluation
- **MCQ:** Binary correct/incorrect with optional negative marking
- **Descriptive:** Semantic matching + keyword bonus
- **Coding:** Test case pass rate + code quality assessment

### 4️⃣ Composite Scoring
- Configurable weights per job role
- Role-specific scoring profiles (Software Engineer, Data Scientist, etc.)
- Grade bands (Excellent, Good, Average, Below Average, Poor)

### 5️⃣ Weak Area Identification
- Detects low-scoring topics automatically
- Provides improvement recommendations
- Links to learning resources

---

## Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12 (recommended)
- Node.js 16+
- npm or yarn
- ~3GB free disk space (for SBERT model)

> Note: Python 3.14 is not supported by the current backend dependencies because prebuilt `numpy`/`pandas` wheels are not yet available.

### Backend Setup

```bash
# 1. Navigate to backend directory
cd component2/backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate the environment
# macOS/Linux
source venv/bin/activate

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download SBERT model (first run only)
# This happens automatically when backend starts

# 6. Point at the shared Atlas database
# Copy .env.example to .env and set MONGODB_URI to the shared cluster
# (DB recruit_ai is used by all components; sessions/results are persisted there).
```

### ML Pipeline Initialization

```bash
# 1. Navigate to ML directory
cd component2/ml

# 2. Build the QG training datasets (v1 + v2)
python build_qg_dataset.py

# 3. Train the QG models (optional — pretrained checkpoints ship in models/)
python train_qg_model.py        # v1  (models/qg_model/)
python train_qg_model_v2.py     # v2  (models/qg_model_v2/, preferred at runtime)

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd component2/frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# Frontend will be available at http://localhost:5174
```

---

## API Endpoints

### Base URL
```
http://localhost:8002/api/v1
```

### Interview Endpoints

#### 1. Start Interview
```http
POST /interview/start
Content-Type: application/json

{
  "candidate_id": "CAND-001",
  "job_role": "Software Engineer",
  "required_skills": ["Java", "SQL", "Python"],
  "num_questions": 10
}

Response:
{
  "session_id": "INT_20240101120000_CAN1",
  "candidate_id": "CAND-001",
  "job_role": "Software Engineer",
  "questions": [...],
  "question_count": {
    "mcq": 3,
    "descriptive": 4,
    "coding": 3
  },
  "total_questions": 10,
  "status": "created"
}
```

#### 2. Submit Answers
```http
POST /interview/submit
Content-Type: application/json

{
  "candidate_id": "CAND-001",
  "session_id": "INT_20240101120000_CAN1",
  "job_role": "Software Engineer",
  "answers": [
    {
      "question_id": "Q_MCQ_001",
      "selected_option": 0,
      "is_correct": true
    },
    {
      "question_id": "Q_DESC_001",
      "answer_text": "Polymorphism allows...",
      "final_score": 85.5
    }
  ]
}

Response:
{
  "interview_id": "RES_20240101120500",
  "candidate_id": "CAND-001",
  "job_role": "Software Engineer",
  "interview_score": 78.5,
  "grade": "Good",
  "mcq_score": 80,
  "descriptive_score": 75,
  "coding_score": 80,
  "weak_topics": ["System Design", "Optimization"],
  "created_at": "2024-01-01T12:05:00"
}
```

#### 3. Get Result
```http
GET /interview/result/{interview_id}

Response:
{
  "interview_id": "RES_20240101120500",
  "candidate_id": "CAND-001",
  "interview_score": 78.5,
  "grade": "Good",
  ...
}
```

#### 4. Get Available Jobs
```http
GET /interview/jobs

Response:
{
  "jobs": {
    "Software Engineer": ["Java", "SQL", "C++", "React", "Python"],
    "Data Scientist": ["Python", "SQL", "Machine Learning", "Statistics"],
    "AI Researcher": ["Python", "TensorFlow", "NLP", "Pytorch"],
    "Cybersecurity Analyst": ["Cybersecurity", "Networking", "Linux", "Ethical Hacking"]
  },
  "total_jobs": 4
}
```

#### 5. Get Question Bank
```http
GET /interview/questions/{job_role}

Response:
{
  "job_role": "Software Engineer",
  "required_skills": ["Java", "SQL", "C++"],
  "question_bank": {
    "MCQ": {
      "Easy": [...],
      "Medium": [...],
      "Hard": [...]
    },
    "Descriptive": {...},
    "Coding": {...}
  }
}
```

#### 6. Health Check
```http
GET /interview/health

Response:
{
  "status": "healthy",
  "component": "Component 2: AI Interview System",
  "available_jobs": 4,
  "questions_in_bank": 200
}
```

---

## ML Models & Scoring

### QG Model (Question Generation)

Two trained checkpoints ship; runtime prefers v2 (see `question_generator._load_model_and_tokenizer`).

| Property | v1 (`train_qg_model.py`) | v2 (`train_qg_model_v2.py`) |
|----------|--------------------------|-----------------------------|
| Architecture | Seq2Seq Transformer | Seq2Seq Transformer |
| d_model | 128 | 192 |
| nhead | 4 | 6 |
| num_layers | 2 enc + 2 dec | 3 enc + 3 dec |
| dim_feedforward | 512 | 768 |
| vocab_size | 5,000 | 8,000 |
| src_max_len / tgt_max_len | — | 24 / 160 |
| Epochs | 5 | 20 |
| Dropout | — | 0.1 |

### Training Dataset

| Dataset | Train | Val |
|---------|-------|-----|
| `qg_dataset.json` (v1) | 20,161 | 2,241 |
| `qg_dataset_v2.json` (v2) | 4,996 | 556 |

### Scoring Formulas

#### MCQ Score
```
Score_MCQ(i) = +1   if correct
               -0.25 if wrong
                0   if skipped

MCQ_Score = max(0, Σ Score_MCQ(i)) / N_mcq × 100
```

#### Descriptive Score
```
CosineSim = (e_ref · e_candidate) / (‖e_ref‖ · ‖e_candidate‖)
Raw_Score = CosineSim × 100
KeywordBonus = matched_keywords / total_keywords
Blended = 0.85 × Raw_Score + 0.15 × KeywordBonus × 100

Desc_Score(i) = min(100, max(Raw_Score, Blended))
Descriptive_Score = Σ Desc_Score(i) / N_desc
```
Keyword bonus can only raise a score, never lower it, so correctly-rephrased answers aren't penalized.

#### Coding Score
```
Test_Pass_Rate = tests_passed / total_tests
Quality_Score = 0.5×SyntaxValid + 0.3×ComplexityScore + 0.2×Readability

Code_Score(i) = 0.7 × Test_Pass_Rate × 100 + 0.3 × Quality_Score × 100
Coding_Score = Σ Code_Score(i) / N_code
```

#### Interview Score
```
IS = w_mcq × MCQ_Score + w_desc × Descriptive_Score + w_code × Coding_Score
```
Weights come from `interview_scoring_config.json` (10 roles). When a question type is missing, weights are re-normalized across the available types. Sample:
```
Software Engineer:   mcq=0.20, desc=0.30, code=0.50
Data Scientist:      mcq=0.25, desc=0.35, code=0.40
DevOps Engineer:     mcq=0.40, desc=0.40, code=0.20
Cybersecurity:       mcq=0.45, desc=0.55, code=0.00
```

### Grade Bands
| Grade | Score Range | Description |
|-------|-------------|------------|
| Excellent | ≥ 85 | Outstanding performance |
| Good | ≥ 70 | Strong performance |
| Average | ≥ 55 | Acceptable performance |
| Below Average | ≥ 40 | Needs improvement |
| Poor | < 40 | Insufficient performance |

---

## Question Bank

### Data Sources
- **`raigs/RAIGS_generated_questions.csv`** — AI-generated MCQs (18,757 questions in `models/question_bank.json`, by role/level/topic)
- **`raigs/generate.py`** — offline question-generation pipeline that produced the CSV
- **Custom templates** — fallback bank used when the QG model is unavailable

### Training Datasets
- **`models/qg_dataset.json` (v1)** — 20,161 train / 2,241 val examples from the RAIGS CSV
- **`models/qg_dataset_v2.json` (v2)** — 4,996 train / 556 val examples

### Question Structure
```json
{
  "id": "Q_MCQ_001",
  "question_text": "What is polymorphism?",
  "question_type": "MCQ|Descriptive|Coding",
  "difficulty": "Easy|Medium|Hard",
  "category": "OOP|Algorithms|ML",
  "topic": "Inheritance|Data Structures",
  "keywords": ["polymorphism", "inheritance", "method"],
  "options": [...],  // MCQ only
  "answer_text": "...",  // Descriptive/ref
  "test_cases": [...]  // Coding only
}
```

---

## Role Profiles and Coding Profiles
The interview system derives a role's coding profile from the job role's `required_skills`. It scans the skill list for trigger keywords and maps roles to one of these profiles:

- `full` — full programming/coding profile
- `sql` — SQL-only coding profile
- `scripting` — scripting/configuration-based coding profile
- `none` — no coding questions

### Coding profile trigger keywords
The system looks for these skill keywords in `job_requirements` to decide whether coding is enabled:

`Python`, `Java`, `JavaScript`, `C++`, `C#`, `SQL`, `Kotlin`, `Swift`, `TypeScript`, `React`, `Vue`, `Node.js`, `Flutter`, `React Native`, `TensorFlow`, `PyTorch`, `HTML`, `CSS`

### Role profile mapping
| Role | MCQ | Descriptive | Coding | Coding profile | Notes |
|------|------|-------------|--------|----------------|-------|
| Software Engineer | 20% | 30% | 50% | `full` | Java/Python/C++/SQL/React |
| Data Scientist | 25% | 35% | 40% | `full` | Python/SQL/ML |
| Machine Learning Engineer | 20% | 30% | 50% | `full` | Python/TensorFlow/PyTorch |
| DevOps Engineer | 40% | 40% | 20% | `scripting` | Shell/YAML/CI-CD | 
| Cybersecurity Analyst | 45% | 55% | 0% | `none` | No coding questions |
| Cloud Solutions Architect | 45% | 55% | 0% | `none` | No coding questions |
| Database Administrator | 30% | 40% | 30% | `sql` | SQL-only coding |
| Frontend Developer | 20% | 30% | 50% | `full` | JS/TS/React/Vue/CSS |
| Backend Developer | 20% | 30% | 50% | `full` | Python/Java/Node.js/SQL |
| Mobile App Developer | 20% | 30% | 50% | `full` | Kotlin/Swift/Flutter |

### Profile behavior
- `full`: standard coding problems with input/output test-case validation.
- `sql`: SQL query and schema problems evaluated on result-set correctness.
- `scripting`: scripting and configuration tasks evaluated on structure and pipeline correctness.
- `none`: no coding interface is shown, and final score uses only MCQ + Descriptive weights.

---

## Frontend Pages

### 1. Dashboard (`/`)
- System overview
- Job roles available
- Key statistics
- Featured jobs

### 2. Start Interview (`/start`)
- Candidate registration
- Job role selection
- Question count configuration
- Interview tips

### 3. Interview Interface (`/interview/:sessionId`)
- Question display
- Answer input (MCQ, text, code)
- Progress tracking
- Timer
- Navigation between questions
- Submit button

### 4. Results (`/results/:interviewId`)
- Overall score display
- Component score breakdown
- Grade assignment
- Weak areas identified
- Recommendations
- Weight breakdown

---

## Integration with Other Components

### Component 1 → Component 2
```
CV Matching Score + Extracted Skills
        ↓
Generate role-specific questions based on required skills
```

### Component 2 → Component 3
```
Interview Score + MCQ/Descriptive/Coding Scores
        ↓
Use for ranking candidates
```

### Component 2 → Component 4
```
Interview Score + Weak Topics + Coding Performance
        ↓
Identify skill gaps and generate learning paths
```

---

## Configuration Files

### job_requirements.json
Maps job roles to required skills:
```json
{
  "Software Engineer": ["Java", "SQL", "C++", "React", "Python"],
  "Data Scientist": ["Python", "Machine Learning", "SQL", "Statistics"],
  ...
}
```

### interview_scoring_config.json
Role-based scoring weights:
```json
{
  "interview_weights": {
    "Software Engineer": {"mcq": 0.20, "descriptive": 0.30, "coding": 0.50},
    ...
  },
  "grade_bands": {
    "Excellent": {"min": 85},
    ...
  }
}
```

### SBERT parameters
Hardcoded in `ml/answer_evaluator.py` (`DescriptiveAnswerEvaluator`):
```python
model_name = "all-mpnet-base-v2"
alpha = 0.85   # weight for semantic similarity
beta  = 0.15   # weight for keyword coverage
```

---

## Troubleshooting

### Issue: QG model not found
**Solution:** Train the model:
```bash
cd component2/ml
python build_qg_dataset.py
python train_qg_model.py
```

### Issue: QG model generates poor quality questions
**Solution:** Retrain with larger architecture by editing `train_qg_model.py`:
```python
D_MODEL = 256
NHEAD = 4
NUM_LAYERS = 3
DIM_FEEDFORWARD = 1024
EPOCHS = 15
```
Requires GPU for reasonable training time.

### Issue: SBERT model download fails
**Solution:** Manually download and place in cache:
```bash
pip install sentence-transformers
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2')"
```

### Issue: Frontend cannot reach backend
**Solution:** Verify proxy in `vite.config.js`:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8002',
    changeOrigin: true,
  }
}
```

### Issue: Dataset encoding errors
**Solution:** CSV files use Latin-1 encoding. The data loader handles this automatically with fallback:
```python
try:
    df = pd.read_csv(path, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(path, encoding='latin-1')
```

---

## Performance Metrics

Based on testing with 200 questions and 50 candidates:

| Metric | Value |
|--------|-------|
| Avg Question Load | 45ms |
| Avg Answer Evaluation | 250ms (SBERT + scoring) |
| Avg Interview Duration | 20-30 min |
| Model Accuracy (MCQ) | 100% (rule-based) |
| Model F1 (Semantic) | 0.92 (cross-validation) |

---

## Future Enhancements

- [ ] GPU-accelerated QG model training
- [ ] Live code execution sandbox (LeetCode-like)
- [ ] Voice-based interview support
- [ ] Proctoring & anti-cheating measures
- [ ] Candidate progress tracking database
- [ ] Advanced NLP for paraphrase detection
- [ ] ML-based code plagiarism detection
- [ ] Interview scheduling & notifications
- [ ] Multi-language support

---

## Contributing

For component-specific contributions:
1. Update `ml/train_qg_model.py` for QG model changes
2. Update `ml/build_qg_dataset.py` for dataset changes
3. Update `backend/services/qg_engine.py` for backend integration
4. Update `backend/main.py` for API changes
5. Update `frontend/src/` for UI changes
6. Maintain backward compatibility with other components

---

## License

MIT License - Part of R26-IT-148 Research Project

---

## Contact & Support

- **Component Owner:** Team Member 2
- **Port:** 8002
- **Documentation:** See README.md (this file)
- **Issues:** Report in project repository

---

**Last Updated:** 2026-08-02  
**Status:** ✅ Production Ready
