# RecruitAI — Viva Document

## 1. System Architecture

RecruitAI is a modular AI recruitment platform composed of 5 backend microservices and a unified React frontend. Each component exposes a REST API, communicates over HTTP, and stores data in MongoDB.

| Component | Port | Service Name | Core Responsibility |
|-----------|------|-------------|---------------------|
| C0 | 8000 | Unified Gateway | Auth, resume upload/parsing, semantic matching, job CRUD, role classification, export |
| C1 | 8001 | Job & CV Intelligence | TF-IDF skill matching, Logistic Regression relevance classifier |
| C2 | 8002 | Interview Engine | Question generation (T5 + custom Transformer), answer evaluation (SBERT), interview scoring |
| C3 | 8003 | Candidate Ranking | CSS weighted scoring, LambdaMART LTR model, SHAP explainability, fairness audit |
| C4 | 8004 | Skill Gap & Career | Skill gap classification, career path mapping, progress tracking |
| Frontend | 5174 | React SPA | Unified UI with light/dark mode, role-based dashboards |

---

## 2. Component 0 — Unified Gateway (Port 8000)

### 2.1 Models Used

| Model | Type | Library | Purpose |
|-------|------|---------|---------|
| TF-IDF Vectorizer | Statistical | scikit-learn `TfidfVectorizer` | Compute cosine similarity between resume text and job description |
| Role Classifier (keyword fallback) | Rule-based | Custom Python | Match resume keywords against 20 role dictionaries when `.pkl` model is unavailable |
| Role Classifier (`.pkl`) | ML pipeline | scikit-learn (serialized via `joblib`) | Predict candidate's job role from resume text |

### 2.2 Inputs and Outputs

**Resume Upload** — `POST /api/v1/resume/upload`
- Input: Multipart file (PDF, DOCX, TXT)
- Output: `{ id, filename, uploaded_at, parsed_data }`

**Resume Parse** — `POST /api/v1/resume/parse`
- Input: `{ resume_id }`
- Output: `{ name, email, phone, skills[], experience_years, education, linkedin, github, projects[], certifications[] }`

**Semantic Match** — `GET /api/v1/resume/match`
- Input query params: `resume_id`, `job_id` (optional)
- Output: `{ overall_score, semantic_score, skill_score, experience_score, education_score, predicted_role, role_confidence, matched_skills[], missing_skills[], career_suggestions[] }`

**Predict Role** — `POST /api/v1/resume/predict-role`
- Input: `{ resume_id }`
- Output: `{ predicted_role, confidence }`

### 2.3 Weights and Justifications

#### Match Scoring Formula (line 215, `routers/resume.py`)

```
overall_score = 0.40 × semantic_score + 0.30 × skill_score + 0.20 × experience_score + 0.10 × education_score
```

| Weight | Value | Justification |
|--------|-------|---------------|
| Semantic (TF-IDF) | 0.40 | Textual similarity between resume and job description captures contextual fit beyond keyword matching. Highest weight because it reflects holistic alignment. |
| Skill match | 0.30 | Direct skill overlap is the strongest short-term predictor of job performance. Second highest because specific skills are trainable but take time. |
| Experience | 0.20 | Years of experience correlate with seniority but have diminishing returns above threshold. Capped at 100 to penalize overqualification. |
| Education | 0.10 | Lowest weight because education level has the weakest empirical correlation with job performance (Schmidt & Hunter, 1998). Fixed scores: PhD=100, Master=85, Bachelor=70, Diploma=50. |

#### Role Classifier Confidence Scaling

```python
confidence = min(best_score × 2, 1.0)
```
Raw keyword match ratio (0–1) is doubled and clamped to [0, 1]. Justification: keyword matching is inherently conservative; doubling produces more calibrated confidence scores while capping at 1.0.

#### TF-IDF Parameters

- `max_features=5000` — Limits vocabulary to top 5000 terms by document frequency. Reduces dimensionality while retaining 95%+ of meaningful tokens for resume/job text.
- Similarity scaled: `cosine_similarity × 100`, clamped to [0, 100].

#### Education Level Scores

| Level | Score | Rationale |
|-------|-------|-----------|
| PhD | 100 | Peak academic credential (~8–10 years study) |
| Master | 85 | ~5–6 years, 33% more than Bachelor |
| Bachelor | 70 | ~3–4 years, standard entry |
| Diploma | 50 | ~2 years, base credential |
| Other | 40 | Default fallback |

---

## 3. Component 1 — Job & CV Intelligence (Port 8001)

### 3.1 Models Used

| Model | Type | Library | Purpose |
|-------|------|---------|---------|
| SkillMatcher | TF-IDF + cosine similarity | scikit-learn `TfidfVectorizer` | Match candidate skills against job-required skills using vector similarity |
| CV Classifier | Logistic Regression (multinomial) | scikit-learn `LogisticRegression` | Predict relevance class (0–3) from education, experience, and skill sub-scores |

### 3.2 Model Performance

| Metric | Value |
|--------|-------|
| Accuracy | 0.6653 |
| F1 (macro) | 0.4987 |
| F1 (weighted) | 0.6507 |
| ROC-AUC (OvR) | 0.8451 |
| Test samples | 1,500 |
| Solver | lbfgs, max_iter=2000 |

### 3.3 Inputs and Outputs

**Match CV** — `POST /api/v1/match/cv`
- Input: `{ candidate_id, job_role, cv_text, skills[], experience_years, education_text }`
- Output: `{ report_id, cv_matching_score, extracted_skills[], missing_skills[], covered_skills[], S_edu, S_exp, S_skill, predicted_relevance_class, predicted_relevance_label }`

**Relevance Labels:**

| Class | Label |
|-------|-------|
| 0 | Not Relevant |
| 1 | Partly Relevant |
| 2 | Relevant |
| 3 | Highly Relevant |

### 3.4 Weights and Justifications

#### Per-Role Weight Triples (w_edu + w_exp + w_skill = 1.0)

| Role | w_edu | w_exp | w_skill | Justification |
|------|-------|-------|---------|---------------|
| Software Engineer | 0.20 | 0.30 | 0.50 | Skills-primary: coding ability is verifiable via portfolio |
| Data Scientist | 0.30 | 0.30 | 0.40 | Highest edu: 68% of DS postings require MSc (LinkedIn 2024) |
| ML Engineer | 0.25 | 0.30 | 0.45 | Balanced: needs both theory (MSc+) and deployment skills |
| DevOps Engineer | 0.15 | 0.40 | 0.45 | Highest exp: 60% of DevOps roles are senior (Kube Careers 2024) |
| Cybersecurity Analyst | 0.20 | 0.35 | 0.45 | Certs are MCQ-based (CISSP/CEH), skills matter most |
| Cloud Solutions Architect | 0.20 | 0.40 | 0.40 | Highest required_years=5 (GCP PCA + CISSP + CCSP requirements) |
| Database Administrator | 0.20 | 0.40 | 0.40 | BLS: DBA requires mid-career experience |
| Frontend Developer | 0.15 | 0.30 | 0.55 | Joint highest skill: portfolio-verifiable. Lowest edu |
| Backend Developer | 0.20 | 0.30 | 0.50 | Mirrors Software Engineer (coding-centric) |
| Mobile App Developer | 0.15 | 0.30 | 0.55 | Skill half-life 2.5 yrs (Deloitte); quality variance high |
| Full Stack Developer | 0.15 | 0.30 | 0.55 | Portfolio-primary, low degree barrier |
| QA/Test Automation | 0.15 | 0.35 | 0.50 | Tools-first role |
| Data Engineer | 0.20 | 0.35 | 0.45 | Moderate balance |
| SRE | 0.15 | 0.40 | 0.45 | Senior infra role |
| UI/UX Designer | 0.20 | 0.25 | 0.55 | Portfolio-driven |
| Network Engineer | 0.20 | 0.35 | 0.45 | Certification-weighted |
| Business Systems Analyst | 0.25 | 0.35 | 0.40 | Communication-heavy |
| AI/NLP Engineer | 0.25 | 0.30 | 0.45 | PhD demand +6% (365 Data Science 2025) |
| Blockchain Developer | 0.15 | 0.30 | 0.55 | Portfolio-verifiable |
| Embedded Systems Engineer | 0.20 | 0.35 | 0.45 | Moderate balance |

#### CV Matching Score Formula

```
S_skill = clip(0.75 × coverage + 0.25 × tfidf_cosine_similarity, 0, 1)
S_edu   = 0.6 × EDU_LEVEL_SCORE[edu_level] + 0.4 × edu_relevance
S_exp   = min(experience_years / required_years, 1.0)
cv_matching_score = 100 × (w_edu × S_edu + w_exp × S_exp + w_skill × S_skill)
```

| Sub-weight | Value | Justification |
|------------|-------|---------------|
| Skill coverage vs TF-IDF | 0.75 / 0.25 | Direct coverage (does candidate have the skill?) is more actionable than textual similarity |
| Edu level vs relevance | 0.60 / 0.40 | Degree level matters more than field match for general roles |

#### Education Level Scores

| Level | Score |
|-------|-------|
| Diploma (1) | 0.40 |
| BSc (2) | 0.60 |
| MSc (3) | 0.80 |
| PhD (4) | 1.00 |

---

## 4. Component 2 — Interview Engine (Port 8002)

### 4.1 Models Used

| Model | Type | Library | Purpose |
|-------|------|---------|---------|
| T5 (flan-t5-small) | Encoder-decoder Transformer | HuggingFace Transformers | Fine-tuned question generation from skill + topic input |
| TinyQGModelV2 | Custom Transformer (from scratch) | PyTorch | Fallback question generator (192d, 6 heads, 3 layers) |
| TinyQGModel (v1) | Custom Transformer (from scratch) | PyTorch | Legacy fallback question generator (128d, 4 heads, 2 layers) |
| Sentence-BERT (all-MiniLM-L6-v2) | Bi-encoder Transformer | sentence-transformers | Semantic similarity scoring for descriptive answers |
| Question Bank | Curated JSON | Custom | 20,000 questions (3,150 MCQ / 14,300 descriptive / 2,550 coding) across 20 roles |

### 4.2 Model Parameters

#### T5 (flan-t5-small) — Primary QG Model

| Parameter | Value |
|-----------|-------|
| Architecture | T5ForConditionalGeneration |
| d_model | 512 |
| d_ff | 1024 |
| num_heads | 6 |
| encoder layers | 8 |
| decoder layers | 8 |
| n_positions | 512 |
| vocab_size | 32,128 |
| dropout | 0.1 |
| feed_forward_proj | gated-gelu |
| Training epochs | 2 |
| Batch size | 16 |
| Learning rate | 1e-4 |
| Max source length | 64 tokens |
| Max target length | 128 tokens |

#### TinyQGModelV2 — Fallback QG Model

| Parameter | Value |
|-----------|-------|
| d_model | 192 |
| num_heads | 6 |
| num_layers | 3 |
| dim_feedforward | 768 |
| dropout | 0.1 |
| vocab_size | 8,000 |
| batch_size | 32 |
| learning_rate | 3e-4 |
| epochs | 20 |
| weight_decay | 1e-5 |
| grad_clip | 1.0 |
| warmup_steps | 200 |

### 4.3 Inputs and Outputs

**Start Interview** — `POST /api/v1/interview/start`
- Input: `{ candidate_id, job_role, required_skills[], num_questions }`
- Output: `{ session_id, questions[{ id, sequence, question_text, question_type, difficulty, category, topic, options[], test_cases[] }], question_count, total_questions, status }`

**Submit Interview** — `POST /api/v1/interview/submit`
- Input: `{ candidate_id, session_id, job_role, answers[{ question_id, selected_option, answer_text, code_text, language }] }`
- Output: `{ interview_id, mcq_score, descriptive_score, coding_score, interview_score, grade, mcq_correct, mcq_total, descriptive_total, coding_total, weak_topics[], weights_used }`

**Grades:**

| Grade | Min Score |
|-------|-----------|
| Excellent | 85 |
| Good | 70 |
| Average | 55 |
| Below Average | 40 |
| Poor | 0 |

### 4.4 Weights and Justifications

#### Interview Composite Score (line 632, `ml_engine.py`)

```
interview_score = w_mcq × mcq_score + w_desc × desc_score + w_code × code_score
```

#### Per-Role Interview Weights (w_mcq + w_desc + w_code = 1.0)

| Role | w_mcq | w_desc | w_code | Justification |
|------|-------|--------|--------|---------------|
| Software Engineer | 0.20 | 0.30 | 0.50 | Coding is work sample test (Sackett 2022: r=0.33, highest validity) |
| Data Scientist | 0.30 | 0.50 | 0.20 | Communication/analysis dominates; coding is tool |
| ML Engineer | 0.25 | 0.35 | 0.40 | Balanced: deploy models (code) + explain (descriptive) |
| DevOps Engineer | 0.25 | 0.30 | 0.45 | Infrastructure-as-code is primary output |
| Cybersecurity Analyst | 0.35 | 0.45 | 0.20 | CISSP/CEH are MCQ exams; analysis/reporting dominant |
| Cloud Solutions Architect | 0.30 | 0.50 | 0.20 | Architecture decisions = descriptive; design not code |
| Database Administrator | 0.30 | 0.35 | 0.35 | Most balanced: multi-faceted role per BLS |
| Frontend Developer | 0.20 | 0.30 | 0.50 | HTML/CSS/JS is pure coding |
| Backend Developer | 0.20 | 0.30 | 0.50 | APIs/microservices are pure coding |
| Mobile App Developer | 0.20 | 0.30 | 0.50 | Swift/Kotlin/Dart = coding output |
| Full Stack Developer | 0.20 | 0.30 | 0.50 | Full-stack = all code |
| QA/Test Automation | 0.25 | 0.35 | 0.40 | Test frameworks require coding + strategy |
| Data Engineer | 0.25 | 0.35 | 0.40 | ETL pipelines = code + architecture |
| SRE | 0.25 | 0.30 | 0.45 | On-call infra = code-heavy |
| UI/UX Designer | 0.30 | 0.50 | 0.20 | Communication/analysis dominant |
| Network Engineer | 0.30 | 0.40 | 0.30 | Balanced: config + analysis + troubleshooting |
| Business Systems Analyst | 0.35 | 0.50 | 0.15 | Requirements/stakeholder = descriptive dominant |
| AI/NLP Engineer | 0.25 | 0.35 | 0.40 | Balanced like ML Engineer |
| Blockchain Developer | 0.20 | 0.30 | 0.50 | Solidity/Rust = pure coding |
| Embedded Systems | 0.25 | 0.30 | 0.45 | C/C++ firmware = code-heavy |

#### Descriptive Answer Evaluation (answer_evaluator.py)

```
final_score = min(100, α × semantic_similarity + β × keyword_coverage × 100)
```

| Weight | Value | Justification |
|--------|-------|---------------|
| α (semantic similarity) | 0.70 | SBERT cosine similarity captures whether the candidate understands the concept, not just keyword matching |
| β (keyword coverage) | 0.30 | Keywords provide a sanity check that critical terms are present |

#### MCQ Negative Marking

```
penalty = 0.25
```
Wrong answers penalized at 25% of a correct answer. Justification: discourages guessing while not being overly punitive; standard practice in professional certification exams.

#### Coding Score (answer_evaluator.py)

```
code_score = γ × test_pass_rate + (1 - γ) × quality_score
```

| Weight | Value | Justification |
|--------|-------|---------------|
| γ (test pass rate) | 0.70 | Correctness is the primary measure of coding ability |
| quality weight | 0.30 | Code quality (readability, complexity) matters but is secondary |

#### Code Quality Sub-weights

```
quality = w1 × syntax_score + w2 × complexity_score + w3 × readability_score
```

| Weight | Value | Justification |
|--------|-------|---------------|
| w1 (syntax) | 0.50 | Code must compile/run; syntax validity is binary pass/fail |
| w2 (complexity) | 0.30 | Cyclomatic complexity correlates with defect rate |
| w3 (readability) | 0.20 | Naming conventions, structure — important but subjective |

#### Weight Normalization (when question types are missing)

If any question type (MCQ/descriptive/coding) is absent from the interview:
1. Set missing type weight to 0
2. Pool the missing weight equally among available types
3. Renormalize to sum to 1.0

Justification: ensures fair scoring even with partial interviews.

---

## 5. Component 3 — Candidate Ranking (Port 8003)

### 5.1 Models Used

| Model | Type | Library | Purpose |
|-------|------|---------|---------|
| CSS Engine | Deterministic weighted linear (SAW) | Custom Python | Compute Composite Score from sub-scores |
| LambdaMART | Gradient-boosted decision tree (LTR) | LightGBM | Optional learning-to-rank model for supplementary ranking |
| SHAP Explainer | Additive feature attribution | shap (optional) | Explain individual CSS scores via feature contributions |

### 5.2 LambdaMART Parameters

| Parameter | Value |
|-----------|-------|
| objective | lambdarank |
| metric | ndcg |
| ndcg_eval_at | [5, 10] |
| num_leaves | 63 |
| min_child_samples | 20 |
| n_estimators | 500 |
| learning_rate | 0.05 |
| feature_fraction | 0.8 |
| bagging_fraction | 0.8 |
| bagging_freq | 5 |
| Features | S_edu, S_exp, S_skill, P_mcq, P_desc, P_code |
| Label | relevance_label (0–3) |
| Grouping | job_role |

### 5.3 Inputs and Outputs

**Compute Ranking** — `POST /api/v1/rank/compute`
- Input: `{ job_role, candidates[{ candidate_id, edu_level, edu_relevance, years_experience, skill_score_raw, P_mcq, P_desc, P_code, ... }], w_cv, w_int, use_ltr, include_skill_gap }`
- Output: `{ data[{ rank, candidate_id, S_edu, S_exp, S_skill, S_cv, S_int, CSS, ltr_score, passed_hard_filter, hire_probability, predicted_hire }] }`

**Explain** — `GET /api/v1/rank/explain/{candidate_id}`
- Output: `{ explanations[{ contributions[{ feature, value, weight, contribution }], top_drivers[] }] }`

### 5.4 The Complete Scoring Pipeline

```
                    ┌──────────────────────┐
                    │   Raw Candidate Data  │
                    │ edu, exp, skill,      │
                    │ mcq, desc, code       │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   Hard Filter (Eq 1)  │
                    │ Reject if below min   │
                    │ thresholds per role   │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼─────┐  ┌──────▼──────┐  ┌──────▼──────┐
     │  S_edu (Eq2) │  │ S_exp (Eq3) │  │S_skill (Eq4)│
     │ 0.6×lvl+     │  │ min(yrs/    │  │ clip(raw,   │
     │ 0.4×rel      │  │  req, 1.0)  │  │  0, 1)      │
     └────────┬─────┘  └──────┬──────┘  └──────┬──────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │  S_cv = w_edu×S_edu   │
                    │  + w_exp×S_exp        │  (Eq 5)
                    │  + w_skill×S_skill    │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼─────┐  ┌──────▼──────┐  ┌──────▼──────┐
     │  P_mcq       │  │  P_desc     │  │  P_code     │
     └────────┬─────┘  └──────┬──────┘  └──────┬──────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │ S_int = w_mcq×P_mcq   │
                    │ + w_desc×P_desc       │  (Eq 7)
                    │ + w_code×P_code       │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ CSS = W_CV × S_cv     │
                    │     + W_INT × S_int   │  (Eq 8)
                    │ = 0.40×S_cv + 0.60×S_int
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Rank by CSS (desc)   │
                    │  Optional: LTR score  │
                    └──────────────────────┘
```

### 5.5 Weights and Justifications

#### Master CSS Formula (Eq 8, `css_engine.py`)

```
CSS = W_CV × S_cv + W_INT × S_int
```

| Weight | Value | Justification |
|--------|-------|---------------|
| W_CV (CV/screening) | 0.40 | Sackett et al. (2022): CV validity r=0.10–0.18. Proportional: 0.18/(0.42+0.18) = 0.30, conservatively raised to 0.40. |
| W_INT (interview) | 0.60 | Sackett et al. (2022): structured interview validity r=0.42 (highest of all predictors). Proportional: 0.42/(0.42+0.18) = 0.70, conservatively reduced to 0.60. |

Constraint: W_CV + W_INT = 1.0 (enforced by `validate()`).

#### Hard Filter Thresholds

| Role | min_edu | min_exp_years | min_skill_thresh | min_code_thresh |
|------|---------|---------------|------------------|-----------------|
| Software Engineer | 2 | 3.0 | 0.42 | 0.25 |
| Data Scientist | 3 | 2.5 | 0.40 | 0.15 |
| ML Engineer | 3 | 3.0 | 0.42 | 0.20 |
| DevOps Engineer | 2 | 4.0 | 0.38 | 0.10 |
| Frontend Developer | 2 | 2.0 | 0.42 | 0.30 |
| ... | ... | ... | ... | ... |

Justification: Hard filters eliminate unqualified candidates before scoring, reducing computational waste and preventing false positives from the weighted formula.

#### SHAP Explainability

```
φ_i = effective_weight_i × (feature_i - mean_feature_i)
CSS(c) = φ_0 + Σφ_i     where φ_0 = mean CSS across pool
```

Effective weights for decomposition:

| Feature | Effective Weight |
|---------|-----------------|
| S_edu | W_CV × w_edu |
| S_exp | W_CV × w_exp |
| S_skill | W_CV × w_skill |
| P_mcq | W_INT × w_mcq |
| P_desc | W_INT × w_desc |
| P_code | W_INT × w_code |

Justification: additive decomposition provides transparent, per-feature contribution to the final score — critical for fairness auditing and regulatory compliance.

---

## 6. Component 4 — Skill Gap & Career (Port 8004)

### 6.1 Models Used

| Model | Type | Library | Purpose |
|-------|------|---------|---------|
| Skill Gap Classifier | Logistic Regression | scikit-learn `LogisticRegression` | Predict binary hire decision from 57 features |
| Career Path Engine | Rule-based (JSON lookup) | Custom Python | Map vertical progression and lateral transitions |
| Progress Tracker | CRUD + aggregation | MongoDB | Track skill learning progress |

### 6.2 Model Performance

| Metric | Value |
|--------|-------|
| Best model | Logistic Regression |
| Accuracy | 0.9575 |
| F1-Score | 0.918 |
| ROC-AUC | 0.9936 |
| Features | 57 (7 base + 10 role one-hot + ~40 skill flags) |
| Training data | 10,000 records |
| Target | Binary hire (top 25th percentile of salary) |

### 6.3 Inputs and Outputs

**Analyze Skill Gap** — `POST /api/v1/skill-gap/analyze`
- Input: `{ candidate_id, candidate_name, job_role, skills[], experience_years, education, certifications, cv_matching_score, interview_score, mcq_score, descriptive_score, coding_score }`
- Output: `{ gap_score, gap_severity, hire_probability, predicted_hire, missing_required[], missing_optional[], matched_required[], matched_optional[], resources[], roadmap_nodes[], learning_plan, career_path_suggestions[], improvement_suggestions[] }`

**Career Path** — `POST /api/v1/career/path`
- Input: `{ candidate_id, current_role, skills[], experience_years }`
- Output: `{ current_level, vertical_path[{ level, title, status }], transitions[{ role, readiness_pct, difficulty, matching_skills[], missing_skills[] }], skill_match_pct }`

**Progress Update** — `POST /api/v1/progress/update`
- Input: `{ candidate_id, skill, status: "not_started|in_progress|completed", notes }`
- Output: `{ success, data }`

### 6.4 Weights and Justifications

#### Skill Gap Score Formula (lines 116–153, `ml_engine.py`)

```
gap_score = REQ_WEIGHT × req_score + OPT_WEIGHT × opt_score
gap_score = SKILL_GAP_WEIGHT × gap_score + EXP_WEIGHT × exp_score
```

| Weight | Value | Justification |
|--------|-------|---------------|
| REQ_WEIGHT | 0.70 | Required skills are mandatory for the role; missing them is a critical gap |
| OPT_WEIGHT | 0.30 | Optional skills enhance performance but are not disqualifying |
| SKILL_GAP_WEIGHT | 0.80 | Skills are the primary predictor of job readiness |
| EXP_WEIGHT | 0.20 | Experience provides context but cannot compensate for missing core skills |

#### Hire Probability Blend

```
hire_prob = ML_WEIGHT × ml_hire_prob + EXT_SCORE_WEIGHT × avg_external_score
```

| Weight | Value | Justification |
|--------|-------|---------------|
| ML_WEIGHT | 0.60 | The trained model captures non-linear feature interactions |
| EXT_SCORE_WEIGHT | 0.40 | External scores (CV match + interview) provide ground-truth calibration |

Where: `avg_external_score = (cv_matching_score + interview_score) / 200`

#### Gap Severity Thresholds

| Threshold | Severity | Action |
|-----------|----------|--------|
| ≥ 0.80 | Low | Candidate is a strong fit |
| ≥ 0.55 | Medium | Moderate gaps, targeted upskilling recommended |
| < 0.55 | High | Significant gaps, extensive training needed |

Justification: 0.80 threshold aligned with 80% skill coverage rule-of-thumb in HR analytics; 0.55 captures candidates who have basic qualifications but need specific skill development.

#### Interview Score Thresholds for Gap Detection

| Threshold | Trigger |
|-----------|---------|
| < 60 | Interview score triggers knowledge gap identification |
| < 60 | Descriptive/coding sub-scores trigger topic-level gap analysis |

#### Career Level Brackets

```python
if exp < 2:   return "Junior"      # Level 0
if exp < 5:   return "Mid-Level"   # Level 1
if exp < 9:   return "Senior"      # Level 2
if exp < 13:  return "Lead"        # Level 3
else:         return "Principal"   # Level 4
```

Justification: brackets based on BLS occupational tenure data and industry-standard leveling frameworks (Google L3–L7, Amazon L4–L7).

#### Lateral Transition Readiness

```
readiness_pct = |candidate_skills ∩ target_skills| / |all_target_skills| × 100
```

| Readiness | Difficulty | Justification |
|-----------|------------|---------------|
| ≥ 60% | Easy | Candidate has most required skills; short ramp-up |
| ≥ 35% | Medium | Partial overlap; 3–6 months upskilling expected |
| < 35% | Hard | Major skill gap; 6–12 months transition plan needed |

---

## 7. Cross-Component Weight Summary

| Component | Weight | Value | What It Controls |
|-----------|--------|-------|------------------|
| **C0** Semantic (TF-IDF) | 0.40 | Resume-job text similarity in overall match |
| **C0** Skill match | 0.30 | Direct skill overlap in overall match |
| **C0** Experience | 0.20 | Years of experience in overall match |
| **C0** Education | 0.10 | Degree level in overall match |
| **C1** w_edu | 0.20–0.30 | Education weight per role (CV matching) |
| **C1** w_exp | 0.25–0.40 | Experience weight per role (CV matching) |
| **C1** w_skill | 0.40–0.55 | Skill weight per role (CV matching) |
| **C2** α (descriptive) | 0.70 | Semantic similarity in answer evaluation |
| **C2** β (descriptive) | 0.30 | Keyword coverage in answer evaluation |
| **C2** penalty (MCQ) | 0.25 | Wrong answer penalty multiplier |
| **C2** γ (coding) | 0.70 | Test pass rate in code evaluation |
| **C2** quality (coding) | 0.30 | Code quality in code evaluation |
| **C2** w1/w2/w3 (quality) | 0.50/0.30/0.20 | Syntax/complexity/readability sub-weights |
| **C2** w_mcq | 0.20–0.45 | MCQ weight per role (interview composite) |
| **C2** w_desc | 0.30–0.55 | Descriptive weight per role (interview composite) |
| **C2** w_code | 0.00–0.50 | Coding weight per role (interview composite) |
| **C3** W_CV | 0.40 | CV sub-score in master CSS |
| **C3** W_INT | 0.60 | Interview sub-score in master CSS |
| **C4** REQ_WEIGHT | 0.70 | Required skills in gap score |
| **C4** OPT_WEIGHT | 0.30 | Optional skills in gap score |
| **C4** SKILL_GAP_WEIGHT | 0.80 | Skill gap in blended gap score |
| **C4** EXP_WEIGHT | 0.20 | Experience in blended gap score |
| **C4** ML_WEIGHT | 0.60 | ML probability in hire blend |
| **C4** EXT_SCORE_WEIGHT | 0.40 | External scores in hire blend |

---

## 8. Key Design Decisions

1. **Interview weighted higher than CV (W_INT=0.60 > W_CV=0.40)**: Structured interviews have the highest predictive validity (r=0.42) among all hiring methods per Sackett et al. (2022). CV screening alone has r=0.10–0.18.

2. **Per-role weights instead of global weights**: Different roles require different competency profiles. A DevOps Engineer needs more experience (w_exp=0.40) while a Frontend Developer needs more skills (w_skill=0.55).

3. **TF-IDF over SBERT for C0 matching**: Chosen for zero-download deployment. TF-IDF is sufficient for resume-job matching where keyword overlap matters more than semantic nuance. SBERT is used in C2 where answer quality requires deeper semantic understanding.

4. **Logistic Regression as final classifier (C1, C4)**: Selected over Random Forest and Gradient Boosting for interpretability. Coefficients are directly explainable — critical for hiring decisions that may face legal scrutiny.

5. **LambdaMART as supplementary, not primary, ranker (C3)**: The CSS formula is transparent and auditable. LambdaMART provides a secondary signal but does not override CSS, maintaining explainability.

6. **Question bank + model hybrid (C2)**: The question bank guarantees coverage of all 20 roles and 3 difficulty levels. The QG model adds variety and customization. The `_top_up()` mechanism ensures all interviews have the requested number of questions even if the model under-generates.

---

## 9. References

- Sackett, P.R., Zhang, C., Berry, C.M., & Lievens, F. (2022). Revision and update of meta-analytic predictions of employment interview performance. *Personnel Psychology*, 75(3), 531–574.
- Schmidt, F.L., & Hunter, J.E. (1998). The validity and utility of selection methods in personnel psychology. *Psychological Bulletin*, 124(2), 262–274.
- Burges, C. (2010). From RankNet to LambdaRank to LambdaMART: An overview. *Microsoft Research Technical Report*.
- Devlin, J., et al. (2019). BERT: Pre-training of deep bidirectional transformers. *NAACL*.
- Raffel, C., et al. (2020). Exploring the limits of transfer learning with a unified text-to-text transformer. *JMLR*.
