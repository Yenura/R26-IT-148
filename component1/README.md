# Component 1 — Automated Resume Screening & Role Matching

**Project:** AI-Driven Recruitment Ecosystem for Intelligent Job Matching and Predictive Career Development
**Project Code:** R26-IT-148
**Component:** 1 of 4 — Automated Resume Screening & Role Matching
**Student:** Dulnith K.D. | IT22094872
**Institution:** Sri Lanka Institute of Information Technology (SLIIT)
**Supervisor:** *(supervisor name)*

---

## Overview

Component 1 is the **entry point** of the recruitment pipeline. It accepts candidate resumes (PDF, DOCX, or plain text), extracts structured features, classifies the candidate into one of **20 canonical IT job roles**, measures the semantic similarity between the resume and a supplied job description, and produces a scored **CV feature vector** consumed by Component 3's ranking engine.

### Research Focus

Two ML models are proposed and compared:

| Model | Approach | Purpose |
|-------|----------|---------|
| **PROPOSED** | Sentence-BERT (`all-MiniLM-L6-v2`) → Logistic Regression | Role classification (20 classes) |
| **BASELINE**  | TF-IDF (unigrams+bigrams) → Logistic Regression | Role classification ablation |
| **JD Matcher** | SBERT cosine similarity (resume vs. JD) | Resume-to-JD semantic matching |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AI-Driven Recruitment Ecosystem                      │
│                             R26-IT-148                                   │
└──────────┬──────────────────────────────────────────┬───────────────────┘
           │ Company Flow                             │ Candidate Flow
           │ (post job + required skills/exp/edu)     │ (register + upload CV)
           ▼                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              COMPONENT 1 — Resume Screening & Role Matching              │
│                        IT22094872 | Dulnith K.D.                        │
│                                                                          │
│   CV Parsing (PDF/DOCX/TXT)                                              │
│       ↓                                                                  │
│   Entity Extraction (edu_level, experience_years, skills)               │
│       ↓                                                                  │
│   Role Classifier (SBERT→LogReg PROPOSED | TF-IDF→LogReg BASELINE)     │
│       ↓                                                                  │
│   JD Semantic Matcher (SBERT cosine similarity)                          │
│       ↓                                                                  │
│   Scorer: S_edu | S_exp | S_skill | jd_similarity_score                 │
│       ↓                                                                  │
│   CV Feature Vector (JSON) ─────────────────────────────────────────────┤
│   stored in MongoDB (resumes.cv_analyses)                               │
└──────────────────────────────────────────────┬──────────────────────────┘
                                               │
                                    Resume Matching Results
                                               │
                                               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│         COMPONENT 3 — AI Ranking & Recommendation Engine                 │
│                      Consumes: edu_level, edu_relevance,                 │
│                                years_experience, skill_score_raw         │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
component1/
├── data/
│   ├── __init__.py
│   └── role_requirements.py      # 20-role skill table, REQUIRED_YEARS, EDU_LEVEL_SCORES
├── backend/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app, port 8001, lifespan startup
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic v2 request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── parser.py             # PDF/DOCX/TXT text extraction
│   │   ├── extractor.py          # Regex entity extraction (edu, exp, skills)
│   │   ├── predictor.py          # SBERT/TF-IDF classifier wrapper
│   │   ├── matcher.py            # Resume ↔ JD cosine similarity
│   │   └── scorer.py             # S_edu, S_exp, S_skill, cv_matching_score
│   └── routers/
│       ├── __init__.py
│       └── cv.py                 # All API endpoints
├── ml/
│   ├── generate_data.py          # Synthetic dataset (150/role × 20 roles)
│   ├── train.py                  # Training pipeline (proposed + baseline)
│   └── evaluate.py               # Held-out test set evaluation
├── models/                       # Saved artifacts (.gitignored)
│   └── README.md
├── results/                      # Evaluation report + confusion matrix charts
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   │   ├── sample_swe_resume.txt
│   │   └── sample_ds_resume.txt
│   ├── test_extractor.py
│   ├── test_scorer.py
│   ├── test_predictor.py
│   ├── test_matcher.py
│   └── test_api.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md                     ← this file
```

---

## Installation

```bash
# From the repo root
cd component1

# Create and activate a virtual environment (Python 3.12)
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # Linux/macOS

# Install core dependencies
pip install -r requirements.txt

# Optional: install SBERT (enables proposed model and improved JD matching)
pip install sentence-transformers
```

Copy `.env.example` to `.env` and set `MONGODB_URI` if needed.

---

## How to Run

### 1. Train the models

```bash
# From inside component1/
python ml/train.py
# Options:
#   --n-per-role N   Number of synthetic resumes per role (default: 150)
#   --skip-sbert     Skip SBERT training (TF-IDF baseline only)
```

This generates:
- `data/synthetic_resumes.csv`, `data/train.csv`, `data/val.csv`, `data/test.csv`
- `models/tfidf_classifier.joblib`, `models/tfidf_vectorizer.joblib`
- `models/sbert_classifier.joblib` (if sentence-transformers installed)
- `models/label_classes.joblib`
- `results/evaluation_report.txt`, `results/confusion_matrix_*.png`

### 2. Start the API server

```bash
# From inside component1/
uvicorn backend.main:app --port 8001 --reload
```

Swagger UI: [http://localhost:8001/docs](http://localhost:8001/docs)

### 3. Run tests

```bash
# From inside component1/
python -m pytest tests/ -v
# SBERT tests auto-skip if sentence-transformers not installed
# Mongo tests auto-skip if MongoDB is unreachable
```

### 4. Evaluate saved models

```bash
python ml/evaluate.py --model both
```

---

## API Reference

Base URL: `http://localhost:8001`

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/health` | DB + model status |
| GET | `/api/v1/cv/roles` | All 20 roles + required skills |
| POST | `/api/v1/cv/classify` | Classify text → role (no persistence) |
| POST | `/api/v1/cv/analyze` | Full CV analysis (JSON text body) |
| POST | `/api/v1/cv/analyze-file` | Full CV analysis (multipart file upload) |
| POST | `/api/v1/cv/rank` | Batch rank candidates against a JD |
| GET | `/api/v1/cv` | Paginated list of stored analyses |
| GET | `/api/v1/cv/{candidate_id}` | Single stored analysis |
| DELETE | `/api/v1/cv/{candidate_id}` | Delete stored analysis |

### CV Analysis Output Contract

```json
{
  "candidate_id": "john_smith_001",
  "candidate_name": "John Smith",
  "job_role": "Software Engineer",
  "role_confidence": 0.87,
  "role_alternatives": [
    {"role": "Backend Developer", "confidence": 0.06},
    {"role": "Full Stack Developer", "confidence": 0.04}
  ],
  "education": "B.Sc. in Computer Science — University of Colombo (2017)",
  "edu_level": 2,
  "edu_relevance": 0.9,
  "experience_years": 5.0,
  "skills": ["python", "java", "sql", "rest apis", "git"],
  "S_edu": 0.6,
  "S_exp": 1.0,
  "S_skill": 0.7,
  "skill_score_raw": 0.7,
  "jd_similarity_score": 0.82,
  "cv_matching_score": 79.25,
  "analysis_timestamp": "2026-08-05T15:30:00Z"
}
```

---

## Model Description

### Role Classifier

#### PROPOSED: SBERT + Logistic Regression
- **Embedding**: `all-MiniLM-L6-v2` (sentence-transformers) — 384-dimensional sentence embeddings.
- **Classifier**: `sklearn.linear_model.LogisticRegression` (multinomial, lbfgs solver, C=1.0).
- **Training data**: 3,000 synthetic resumes (150/role × 20 roles), 60/15/25 split.
- **Inference**: `predict_proba` → top-1 role + confidence + top-2 alternatives.

#### BASELINE: TF-IDF + Logistic Regression
- **Features**: `TfidfVectorizer(max_features=10000, ngram_range=(1,2), sublinear_tf=True)`.
- **Classifier**: Same LogisticRegression configuration as proposed.
- **Purpose**: Ablation baseline to quantify the benefit of semantic SBERT embeddings over bag-of-words.

### JD-Resume Matcher (Semantic Matching Engine)

- **Proposed**: SBERT cosine similarity between resume embedding and JD embedding.
- **Fallback**: TF-IDF cosine similarity (computed on-the-fly or with pre-fitted vectorizer).
- **Output**: `jd_similarity_score` ∈ [0, 1] — directly feeds into `cv_matching_score`.

---

## Scoring Formulas

All formulas mirror `component3/engine/css_engine.py` for the 10 overlapping roles.

```
S_edu  = EDU_LEVEL_SCORES[edu_level]        # {1:0.40, 2:0.60, 3:0.80, 4:1.00}
S_exp  = min(experience_years / REQUIRED_YEARS[role], 1.0)
S_skill = skill_score_raw = matched_skills / len(required_skills[role])
```

**cv_matching_score (0–100):**

| Condition | Formula |
|-----------|---------|
| With JD supplied | `(0.35×S_skill + 0.25×S_exp + 0.15×S_edu + 0.25×jd_similarity_score) × 100` |
| Without JD | `(w_skill×S_skill + w_exp×S_exp + w_edu×S_edu) × 100` (role-specific weights) |

---

## 20-Role Taxonomy

The 20 canonical role names are identical to those in `component2/raigs/generate.py`:

| # | Role | New in C1? |
|---|------|-----------|
| 1 | Software Engineer | No (Component 3 aligned) |
| 2 | Data Scientist | No |
| 3 | Machine Learning Engineer | No |
| 4 | DevOps Engineer | No |
| 5 | Cloud Solutions Architect | No |
| 6 | Database Administrator | No |
| 7 | Frontend Developer | No |
| 8 | Backend Developer | No |
| 9 | Mobile App Developer | No |
| 10 | Cybersecurity Analyst | No |
| 11 | Full Stack Developer | **Yes (new)** |
| 12 | QA/Test Automation Engineer | **Yes (new)** |
| 13 | Data Engineer | **Yes (new)** |
| 14 | Site Reliability Engineer (SRE) | **Yes (new)** |
| 15 | UI/UX Designer | **Yes (new)** |
| 16 | Network Engineer | **Yes (new)** |
| 17 | Business/Systems Analyst | **Yes (new)** |
| 18 | AI/NLP Engineer | **Yes (new)** |
| 19 | Blockchain Developer | **Yes (new)** |
| 20 | Embedded Systems Engineer | **Yes (new)** |

> **Integration note for the team:** Component 3's `role_configs.py` currently defines only the first 10 roles. The 10 new roles added by Component 1 will need to be added to Component 3's config for full end-to-end scoring. This is flagged as a team integration follow-up.

Required skills and years for the 10 new roles are defined in `data/role_requirements.py` and documented with rationale in that file's inline comments.

---

## Evaluation Results

*Populated automatically after running `python ml/train.py`.*

See `results/evaluation_report.txt` for:
- Accuracy and Macro-F1 for both models
- Per-role precision / recall / F1
- Confusion matrix charts (`results/confusion_matrix_*.png`)

Expected performance (20-class synthetic dataset, 150 samples/role):

| Model | Accuracy (approx.) | Macro-F1 (approx.) |
|-------|-------------------|-------------------|
| TF-IDF + LogReg (Baseline) | ~0.85–0.92 | ~0.85–0.92 |
| SBERT + LogReg (Proposed) | ~0.90–0.97 | ~0.90–0.97 |

> Note: On the synthetic dataset (generated from templates), both models achieve high accuracy because the vocabulary is strongly correlated to role labels. The SBERT model's advantage over TF-IDF is more pronounced on real, diverse resumes where semantic understanding matters.

---

## Background Literature / References

The SBERT-based approach is grounded in the following published work. These are listed as background literature; precise publication details were verified to the best of our ability but should be independently confirmed before formal submission.

1. **Reimers, N., & Gurevych, I. (2019).** Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP 2019).* — Introduces the SBERT framework that we use for both the role classifier embeddings and the JD-matching cosine similarity score.

2. **Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019).** BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. *Proceedings of NAACL-HLT 2019.* — Foundational transformer pre-training work underlying SBERT.

3. **Bhatia, P., Arumae, K., & Celikkaya, B. (2019).** End-to-End Resume Parsing and Finding Candidates for a Job Description using BERT. *(Listed as background literature — the exact venue/year could not be independently verified; cited with a note of uncertainty.)* — Describes a BERT-based pipeline for resume-to-JD matching similar to our approach.

4. **Manning, C. D., Raghavan, P., & Schütze, H. (2008).** Introduction to Information Retrieval. Cambridge University Press. — Provides the theoretical basis for TF-IDF and cosine similarity used in the baseline model.

> If any citation above cannot be confirmed for your formal submission, please note it explicitly as "background literature — publication details unverified" rather than as a confirmed reference.

---

## Research Questions

1. Does SBERT embedding-based classification outperform TF-IDF bag-of-words classification for multi-class (20-role) IT resume categorisation?
2. How accurately does cosine similarity between SBERT resume and JD embeddings reflect a human assessor's perception of candidate-job fit?
3. How well do the S_edu, S_exp, and S_skill sub-scores computed by Component 1 correlate with the final rankings produced by Component 3?

---

## Technologies

| Technology | Version | Role |
|------------|---------|------|
| Python | 3.12 | Core language |
| FastAPI | ~0.115 | REST API framework |
| Pydantic v2 | ~2.7 | Data validation & serialisation |
| Motor | ~3.4 | Async MongoDB driver |
| sentence-transformers | ~3.0 | SBERT embeddings (proposed) |
| scikit-learn | ~1.5 | TF-IDF + Logistic Regression |
| pdfplumber | ~0.11 | PDF text extraction |
| python-docx | ~1.1 | DOCX text extraction |
| MongoDB | any | Candidate analysis storage |
| pytest | ~8.0 | Test suite |
