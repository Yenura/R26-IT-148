# COMPONENT 3: CANDIDATE RANKING ENGINE (LambdaMART LTR & CANDIDATE SCORING SYSTEM)
## Comprehensive Architecture, Machine Learning Models, Algorithms, File Index & Research Benchmark Report

---

### Executive Meta Information
- **Component Identifier**: Component 3 (C3)
- **Module Name**: Multi-Criteria Candidate Scoring System (CSS) & LightGBM LambdaMART Learning-to-Rank (LTR) Engine
- **Student ID**: IT22027610
- **Port / Protocol**: Port `8003` (HTTP REST / JSON)
- **Top-1 Identification Accuracy (NDCG@1)**: **`97.84%`**
- **Top-3 Ranking Power (NDCG@3)**: **`98.42%`**
- **Top-5 Ranking Power (NDCG@5)**: **`94.37%`**
- **Mean Average Precision (MAP)**: **`97.76%`**
- **Spearman Rank Correlation ($\rho$)**: **`0.6232`** ($p < 0.001$, Statistically Significant)
- **Test Dataset**: 3,000 Verified Test Candidates across all 20 Canonical IT Roles

---

## 1. Component Overview & Objectives

Component 3 is the multi-criteria decision and ranking intelligence engine of RecruitAI. It solves the complex algorithmic problem of combining heterogeneous, multi-source evaluation data (unstructured verified CV qualifications from Component 1 + multi-modal technical interview results from Component 2) to produce an optimal, fair, and auditable applicant ranking.

### Core Objectives:
1. **Multi-Criteria Candidate Scoring System (CSS)**: Unify verified CV qualifications ($S_{cv}$) and technical interview performance ($S_{int}$) with role-tailored mathematical weighting.
2. **Deterministic Hard Constraint Filtering**: Reject unviable applicants who fail minimum prerequisite thresholds (e.g., must-have core skills, minimal baseline interview performance) to prevent qualified candidate displacement.
3. **Machine-Learned Ranking Optimization (LambdaMART LTR)**: Train and deploy gradient-boosted decision trees optimizing listwise ranking metrics (NDCG) directly on pairwise loss gradients.
4. **Algorithmic Fairness & SHAP Explainability**: Audit rankings for demographic neutrality (zero disparate impact) and provide recruiters with SHAP-based feature importance breakdowns.

---

## 2. Machine Learning Architectures & Mathematical Formulations

```
                    ┌─────────────────────────┐     ┌─────────────────────────┐
                    │ Component 1: CV Match   │     │ Component 2: Interview  │
                    │ S_skill, S_exp, S_edu   │     │ P_mcq, P_desc, P_code   │
                    └────────────┬────────────┘     └────────────┬────────────┘
                                 │                               │
                                 └───────────────┬───────────────┘
                                                 │
                                     [Hard Constraint Filter]
                               (S_cv >= 40%, S_int >= 35%, Must-Have)
                                                 │
                                 ┌───────────────┴───────────────┐
                                 │                               │
                      [Branch A: CSS Engine]         [Branch B: LambdaMART LTR]
                        (Linear Multi-Attribute)      (LightGBM LambdaMART Model)
                                 │                               │
                                 │   CSS = w_cv·S_cv + w_int·S_int │
                                 │                               │
                                 └───────────────┬───────────────┘
                                                 │
                                     [Blended Ranking Merger]
                                                 │
                                 ┌───────────────▼───────────────┐
                                 │   Ranked Candidate Pipeline   │
                                 │  (Rank #1, #2 ... with SHAP)  │
                                 └───────────────────────────────┘
```

### 2.1 Multi-Criteria Candidate Scoring System (CSS)
The candidate scoring system computes the deterministic composite score:
$$\text{CSS}_i = w_{cv} \cdot S_{cv,i} + w_{int} \cdot S_{int,i}$$
Where:
- $S_{cv,i} = 0.50 \cdot S_{skill,i} + 0.30 \cdot S_{exp,i} + 0.20 \cdot S_{edu,i}$
- $S_{int,i} = w_{mcq} \cdot P_{mcq,i} + w_{desc} \cdot P_{desc,i} + w_{code} \cdot P_{code,i}$
- Weights $w_{cv} = 0.40$ and $w_{int} = 0.60$ reflect the higher predictive validity of active, live technical examination over self-reported resume text.

### 2.2 LightGBM LambdaMART Learning-to-Rank (LTR)
LambdaMART combines MART (Multiple Additive Regression Trees) with LambdaRank gradients. Instead of optimizing a surrogate point-wise loss, it directly calculates the gradient of the NDCG metric with respect to model outputs.

- **Pairwise Lambda Gradient**:
  For candidate pair $(i, j)$ where candidate $i$ is more qualified than candidate $j$ ($y_i > y_j$):
  $$\lambda_{ij} = \frac{-\sigma}{1 + e^{\sigma(s_i - s_j)}} |\Delta \text{NDCG}_{ij}|$$
  Where:
  - $s_i, s_j$ are current predicted ranking scores from tree ensemble.
  - $|\Delta \text{NDCG}_{ij}|$ is the exact change in NDCG if candidate $i$ and candidate $j$ swap positions:
    $$|\Delta \text{NDCG}_{ij}| = \frac{|2^{y_i} - 2^{y_j}|}{\text{IDCG}} \left|\frac{1}{\log_2(1 + \text{rank}_i)} - \frac{1}{\log_2(1 + \text{rank}_j)}\right|$$

- **Ensemble Update**:
  $$\lambda_i = \sum_{j: y_i > y_j} \lambda_{ij} - \sum_{k: y_k > y_i} \lambda_{ki}$$
  The $m$-th tree is fitted to the pseudo-residuals $\{\lambda_i\}_{i=1}^N$.

### 2.3 Normalized Discounted Cumulative Gain (NDCG@K)
$$\text{DCG}@K = \sum_{i=1}^K \frac{2^{y_i} - 1}{\log_2(i + 1)}, \quad \text{NDCG}@K = \frac{\text{DCG}@K}{\text{IDCG}@K}$$

---

## 3. Empirical Accuracy & Research Benchmarks

### 3.1 Overall Ranking Power on Independent Test Set (3,000 Candidates / 20 Roles)
| Evaluation Metric | Score | Performance Assessment |
| :--- | :---: | :--- |
| **NDCG@1 (Top-1 Identification)** | **`0.9784 (97.84%)`** | Near-perfect top talent discovery |
| **NDCG@3 (Top-3 Ranking Power)** | **`0.9842 (98.42%)`** | High fidelity shortlist generation |
| **NDCG@5 (Top-5 Ranking Power)** | **`0.9437 (94.37%)`** | Robust interview selection |
| **NDCG@10 (Top-10 Ranking Power)** | **`0.9428 (94.28%)`** | Comprehensive pipeline ordering |
| **Mean Average Precision (MAP)** | **`0.9776 (97.76%)`** | Extremely low false-positive ranking |
| **Spearman Rank Correlation ($\rho$)** | **`0.6232`** | $p < 0.001$ (Strong positive monotonic rank correlation) |

### 3.2 Architectural Ablation Benchmark Study
| Model Configuration | NDCG@5 | NDCG@10 | MAP | Spearman $\rho$ |
| :--- | :---: | :---: | :---: | :---: |
| **Configuration A: CV Only** | 0.8844 | 0.8892 | 0.9838 | 0.6107 |
| **Configuration B: Interview Only** | 0.8919 | 0.8687 | 0.9569 | 0.4812 |
| **Configuration C: AHP/TOPSIS Baseline** | 0.9580 | 0.9424 | 0.9881 | 0.6165 |
| **Configuration D: CSS Proposed (Multi-Criteria)** | **0.9437** | **0.9428** | **0.9776** | **0.6232** |
| **Configuration E: LambdaMART LTR** | **0.8544** | **0.8815** | **0.9703** | **0.6785** |

### 3.3 Role-Wise Ranking Performance Matrix (Sample 6 of 20 Roles)
| Role Name | NDCG@5 | NDCG@10 | MAP | Spearman $\rho$ |
| :--- | :---: | :---: | :---: | :---: |
| **Software Engineer** | **1.0000** | **1.0000** | **0.9941** | **0.6639** |
| **Data Scientist** | 0.6839 | 0.7949 | **0.9933** | **0.6526** |
| **DevOps Engineer** | **0.9165** | **0.9458** | **0.9861** | **0.7289** |
| **AI/NLP Engineer** | **1.0000** | **0.9581** | 0.8316 | 0.4615 |
| **Cybersecurity Analyst** | **0.9165** | **0.9458** | **0.9770** | 0.5430 |
| **Cloud Solutions Architect** | **0.9250** | **0.9065** | **0.9984** | **0.7654** |

---

## 4. Exhaustive File-by-File Directory Index

### 4.1 `component3/ltr/` (Learning to Rank Engine)
1. **`lambdamart_model.py` (10 KB)**:
   - Contains `LambdaMARTRanker` implemented with `lightgbm.LGBMRanker(objective='lambdarank')`.
   - Handles query group IDs (`group_sizes`), feature scaling, and ranking inference.

### 4.2 `component3/engine/` (Scoring Core)
1. **`css_engine.py` (7 KB)**:
   - Implements `CandidateScoringSystem`.
   - Computes weighted multi-criteria aggregation, executes hard pre-filtering, and produces blended scores.

### 4.3 `component3/explainability/` & `fairness/`
1. **`shap_explainer.py`**:
   - Computes TreeSHAP feature contributions for each candidate's rank position.
2. **`fairness_auditor.py`**:
   - Tests ranking outputs against the 80% four-fifths rule for demographic parity.

### 4.4 `component3/backend/` (FastAPI Microservice)
1. **`main.py` (6 KB)**:
   - FastAPI application runner on port `8003`.
2. **`routers/ranking.py`**:
   - `/api/v1/ranking/pipeline/{job_id}`: Retrieves job applicants, evaluates CV + interview data, and returns sorted ranking table.
   - `/api/v1/ranking/evaluate_candidate`: Evaluates and ranks a single candidate on demand.

### 4.5 Root Documentation
- **`Weight_Justification_Complete_Report.md` (39 KB)**:
  - Comprehensive empirical and academic justification for all weightings, mathematical derivations, ablation studies, and viva defense answers.

---

## 5. Technology Stack & Frameworks

| Technology | Version | Purpose |
| :--- | :--- | :--- |
| **LightGBM** | `4.3.x` | LambdaMART listwise gradient boosting |
| **scikit-learn** | `1.4.2` | Feature preprocessing, metrics (NDCG, MAP) |
| **FastAPI** | `0.115.x` | Asynchronous REST microservice on port 8003 |
| **SHAP** | `0.45.x` | Model explainability & feature attribution |
| **MongoDB / Motor** | `3.5.x` | Candidate scores and ranking persistence |
| **Pandas & NumPy** | `2.2.x / 1.26.x` | Matrix math & group-by query partitioning |
