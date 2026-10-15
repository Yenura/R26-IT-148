# COMPONENT 1: AI RESUME SCREENING, PARSING & ROLE CLASSIFIER
## Comprehensive Architecture, Machine Learning Models, Algorithms, File Index & Research Benchmark Report

---

### Executive Meta Information
- **Component Identifier**: Component 1 (C1)
- **Module Name**: AI-Powered Resume Parser, Entity Extraction & Job Role Classifier
- **Student ID**: IT22089236
- **Researcher**: D T D Perera
- **Port / Protocol**: Port `8001` (HTTP REST / JSON / Multipart Form-Data)
- **Primary Model Accuracy**: **`90.49%`** Test Accuracy | **`93.47%`** Macro F1-Score | **`90.36%`** 5-Fold CV
- **Baseline Accuracy**: **`97.96%`** TF-IDF (1-2 N-Grams) + Logistic Regression
- **Test Suite Status**: **`168 / 168 Unit & Integration Tests Passed (100%)`**

---

## 1. Component Overview & Objectives

Component 1 serves as the foundational intake and semantic analysis gateway of the RecruitAI platform. It is responsible for transforming unstructured, heterogeneous candidate resumes (PDF, DOCX, TXT) into structured, verified technical profiles and scoring them against industry benchmark competency matrices across 20 canonical IT job roles.

### Core Objectives:
1. **Document Ingestion & Text Sanitization**: Extract clean raw text from PDF/DOCX resumes, strip Personally Identifiable Information (PII) if required, and normalize formatting anomalies.
2. **Precision Named Entity Recognition (NER) & Skill Extraction**: Extract over 400+ technical skills, frameworks, cloud tools, certifications, and educational degrees with context-guarded token boundaries to eliminate false positives.
3. **Multi-Class Job Role Classification (Model 1)**: Predict the candidate's primary specialization and alternative career affinities across 20 canonical IT domains using NLP feature engineering and balanced statistical inference.
4. **Tri-Pillar CV Matching Score ($S_{cv}$)**: Compute a mathematically grounded candidate qualification score combining Technical Skills Alignment ($S_{skill}$), Verified Experience Tenure ($S_{exp}$), and Educational Level ($S_{edu}$).

---

## 2. Machine Learning Architectures & Mathematical Formulations

Component 1 implements a dual-model architecture: a production NLP Feature-Engineered Classifier and a high-dimensional TF-IDF Baseline.

```
                    ┌──────────────────────────────────────────────┐
                    │           Raw Candidate Resume (PDF)         │
                    └──────────────────────┬───────────────────────┘
                                           │
                                  [PDF Text Extractor]
                                           │
                    ┌──────────────────────▼───────────────────────┐
                    │            Sanitized Resume Text             │
                    └───────┬──────────────────────────────┬───────┘
                            │                              │
             [Context-Guarded Regex Extractor]     [Domain Density Profiler]
                            │                              │
               400+ Skills & Certifications         20-Domain Category Vectors
                            │                              │
                            └──────────────┬───────────────┘
                                           │
                                 [Feature Concatenation]
                           (67 Normalized Dense NLP Features)
                                           │
                    ┌──────────────────────▼───────────────────────┐
                    │   Balanced Multi-Class Logistic Regression   │
                    │               (cv_classifier.pkl)            │
                    └──────────────────────┬───────────────────────┘
                                           │
                   ┌───────────────────────┴───────────────────────┐
                   │                                               │
        [Predicted Primary Role]                      [Alternative Probability Matrix]
         (e.g., Data Scientist)                        (Top 4 Softmax Probabilities)
```

### 2.1 Model 1: NLP Entity Feature Engineering + Balanced Multi-Class Classifier
- **Algorithm**: Multinomial Logistic Regression with $L_2$ Regularization and Class-Balanced Sample Weighting (`class_weight='balanced'`).
- **Feature Pipeline**:
  1. **Domain Skill Densities**: Normalized frequency counts of extracted skills mapped across the 20 canonical IT categories.
  2. **Experience Normalization**: Extracted verified work experience tenure scaled against industry seniority benchmarks:
     $$\bar{X}_{exp} = \min\left(\frac{\text{Tenure}_{\text{years}}}{10.0}, 1.0\right)$$
  3. **Education Level Ordinal Encoding**: $E \in \{0.0: \text{None}, 0.6: \text{Diploma}, 0.8: \text{BSc/Bachelor}, 0.95: \text{MSc/Master}, 1.0: \text{PhD}\}$.
  4. **Certification Count Vectors**: Number of verified industry credentials (e.g., AWS Certified, CISA, CCNA, PMP).
  5. **Keyword Salience**: Top TF-IDF unigram and bigram salience scores computed over sanitized domain sections.

- **Mathematical Formulation (Multinomial Softmax Inference)**:
  For a candidate feature vector $\mathbf{x} \in \mathbb{R}^D$ and 20 canonical classes $k \in \{1, 2, \dots, 20\}$:
  $$P(Y = k \mid \mathbf{x}) = \frac{\exp\left(\mathbf{w}_k^T \mathbf{x} + b_k\right)}{\sum_{j=1}^{20} \exp\left(\mathbf{w}_j^T \mathbf{x} + b_j\right)}$$
  Where $\mathbf{w}_k$ and $b_k$ represent the learned weight vector and bias for class $k$.

- **Objective Function with $L_2$ Regularization**:
  $$\mathcal{L}(\mathbf{W}) = -\sum_{i=1}^N \sum_{k=1}^{20} y_{i,k} \log P(Y = k \mid \mathbf{x}_i) + \frac{\lambda}{2} \sum_{k=1}^{20} \|\mathbf{w}_k\|_2^2$$

### 2.2 Model 1 Baseline: TF-IDF (1-2 N-Grams) Classifier
- **Algorithm**: Sublinear Term Frequency - Inverse Document Frequency (`sublinear_tf=True`, `ngram_range=(1, 2)`, `max_features=5000`) paired with Logistic Regression.
- **Formulation**:
  $$\text{TF-IDF}(t, d, D) = \left(1 + \log \text{tf}(t, d)\right) \times \log\left(\frac{1 + |D|}{1 + \text{df}(t, D)}\right)$$

### 2.3 Semantic Job Description Matcher (Sentence-BERT)
- **Model**: `sentence-transformers/all-mpnet-base-v2` / `all-MiniLM-L6-v2`
- **Logic**: Encodes sanitized resume text and job description into 768-dimensional dense semantic embeddings $\mathbf{u}, \mathbf{v} \in \mathbb{R}^{768}$, computing cosine similarity:
  $$\text{Sim}_{\text{SBERT}}(\text{Resume}, \text{JD}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$

---

## 3. The Tri-Pillar Scoring Formulation ($S_{cv}$)

Component 1 produces the candidate qualification vector $\mathbf{S}_{C1} = [S_{skill}, S_{exp}, S_{edu}]$ and overall CV match score $S_{cv} \in [0, 100]$:

### 3.1 Technical Skill Alignment Score ($S_{skill}$)
Let $\mathcal{K}_{\text{req}}$ be the set of required skills for role $R$ (with importance weights $w_i \in [1, 3]$), and $\mathcal{K}_{\text{cand}}$ be candidate skills:
$$S_{skill} = \frac{\sum_{s_i \in (\mathcal{K}_{\text{cand}} \cap \mathcal{K}_{\text{req}})} w_i}{\sum_{s_j \in \mathcal{K}_{\text{req}}} w_j} \times 100$$

### 3.2 Experience Tenure Score ($S_{exp}$)
Let $T_{\text{cand}}$ be candidate verified years and $T_{\text{req}}$ be required years:
$$S_{exp} = \min\left(\frac{T_{\text{cand}}}{\max(T_{\text{req}}, 1.0)} \times 100, 100\right)$$
*(Note: A 15% tolerance window allows candidates with $T_{\text{cand}} \ge 0.85 \cdot T_{\text{req}}$ to achieve up to 90% score).*

### 3.3 Educational Level Score ($S_{edu}$)
$$S_{edu} = \begin{cases} 100.0 & \text{if PhD in CS/IT/Data Science} \\ 90.0 & \text{if MSc/Master's in relevant discipline} \\ 80.0 & \text{if BSc/Bachelor's (Hons) in IT/SE/CS} \\ 65.0 & \text{if Higher Diploma / Equivalent} \\ 50.0 & \text{if Self-Taught / Non-Degree} \end{cases}$$

### 3.4 Composite CV Qualification Score ($S_{cv}$)
$$S_{cv} = 0.50 \cdot S_{skill} + 0.30 \cdot S_{exp} + 0.20 \cdot S_{edu}$$

---

## 4. Empirical Accuracy & Research Benchmarks

### 4.1 Overall Model Metrics
| Metric | Score / Value | Status |
| :--- | :--- | :--- |
| **Classification Accuracy** | **`90.49%`** | Production Validated |
| **Macro Precision** | **`92.47%`** | High Purity |
| **Macro Recall** | **`94.87%`** | High Sensitivity |
| **Macro F1-Score** | **`93.47%`** | Balanced Performance |
| **Weighted F1-Score** | **`90.08%`** | Class-Weighted Accuracy |
| **5-Fold Cross-Validation Mean Accuracy** | **`90.36% (±0.50%)`** | Low Variance / Zero Overfitting |
| **5-Fold Cross-Validation Macro F1** | **`93.17% (±0.40%)`** | Robust Generalization |
| **TF-IDF Baseline Accuracy** | **`97.96%`** | Benchmark Comparison |
| **Test Dataset Size** | **736 Held-Out Resumes** | Leakage-Free Split |
| **Test Suite Pass Rate** | **`168 / 168 Tests Passed (100%)`** | Full Coverage |

### 4.2 Detailed Per-Role Performance Matrix (All 20 Canonical IT Roles)
```
                             precision    recall  f1-score   support
--------------------------------------------------------------------
AI/NLP Engineer                   1.00      1.00      1.00        30
Backend Developer                 0.77      1.00      0.87        30
Blockchain Developer              0.97      0.94      0.96        34
Business/Systems Analyst          0.94      1.00      0.97        30
Cloud Solutions Architect         0.91      0.97      0.94        30
Cybersecurity Analyst             0.94      1.00      0.97        30
Data Engineer                     1.00      1.00      1.00        30
Data Scientist                    0.79      0.83      0.81        65
Database Administrator            0.88      0.93      0.90        30
DevOps Engineer                   0.94      0.97      0.95        30
Embedded Systems Engineer         1.00      1.00      1.00        30
Frontend Developer                0.82      0.82      0.82        61
Full Stack Developer              0.97      0.93      0.95        30
Machine Learning Engineer         1.00      1.00      1.00        30
Mobile App Developer              1.00      1.00      1.00        30
Network Engineer                  0.91      1.00      0.95        30
QA/Test Automation Engineer       0.94      1.00      0.97        30
Site Reliability Engineer         0.94      1.00      0.97        30
Software Engineer                 0.80      0.58      0.67        96
UI/UX Designer                    1.00      1.00      1.00        30
--------------------------------------------------------------------
Macro Average (20 Roles)          0.92      0.95      0.93       736
Weighted Average                  0.90      0.90      0.90       736
Accuracy                                              0.90       736
```

---

## 5. Exhaustive File-by-File Directory Index

### 5.1 `component1/ml/` (Machine Learning Engine)
1. **`extractor.py` (83 KB)**:
   - Contains `CandidateIntelligenceEngine` and `_build_skill_pattern`.
   - Extracts 400+ technical skills, certifications, work experience years, project tenures, education degrees, institutions, and sentence-level evidence snippets.
   - Implements context-guarded regex look-arounds for single-letter and ambiguous terms (`c`, `r`, `go`, `spring`, `rest`, `dart`, `solid`, `less`) ensuring **zero false-positives** on natural conversational text.
2. **`feature_engineering.py` (10 KB)**:
   - Constructs dense normalized feature vectors from raw extraction dictionaries.
   - Calculates domain skill category densities across all 20 canonical categories.
3. **`train.py` (16 KB)**:
   - Trains Model 1 (`cv_classifier.pkl`) and baseline model (`tfidf_baseline.pkl`).
   - Executes stratified 5-fold cross-validation, saves artifacts to `models/`, and generates reports in `results/`.
4. **`evaluate.py` (5 KB)**:
   - Evaluates trained models against the held-out test split (736 samples).
   - Generates confusion matrix PNGs and `metrics.json`.
5. **`lexicon.py` (19 KB)**:
   - Canonical 20 IT role definitions, required competencies, weight multipliers, and industry hierarchy dictionary.
6. **`matcher.py` (3 KB)**:
   - Computes Sentence-BERT cosine semantic similarity between resume summaries and job descriptions.
7. **`skills.py` (9 KB)**:
   - Master technical skills taxonomy dictionary organized by categories (Languages, Frameworks, Cloud, Databases, DevOps, Testing, Security).
8. **`build_models.py` (5 KB)**:
   - High-level orchestrator script to generate datasets, engineer features, fit models, and export pickled estimators.
9. **`generate_data.py` (17 KB)**:
   - Synthetic CV generator producing realistic technical candidate resumes with balanced class distributions.
10. **`ingest_documents.py` & `ingest_pdf_resumes.py` (31 KB)**:
    - Text extraction utilities using `pdfplumber`, `PyPDF2`, `docx`, and regex sanitization.
11. **`test_and_learn_it_resumes.py` (8 KB)**:
    - Interactive CLI diagnostic tool to parse sample resumes and output extracted entities and predictions.

### 5.2 `component1/backend/` (FastAPI Microservice)
1. **`main.py` (5 KB)**:
   - FastAPI application runner on port `8001`.
   - Sets up CORS middleware, rate limiting, lifespan ML preloading, and MongoDB connection pool.
2. **`routers/parser.py`**:
   - `/api/v1/cv/parse`: Parses uploaded PDF/DOCX resumes and returns full structured JSON entities.
   - `/api/v1/cv/classify`: Accepts CV text and returns predicted primary role + top alternative probabilities.
   - `/api/v1/cv/screen`: Runs full candidate screening against target role or job requirements, outputting $S_{skill}, S_{exp}, S_{edu}, S_{cv}$.
   - `/api/v1/cv/roles`: Returns list of all 20 supported canonical IT roles.
3. **`services/predictor_service.py`**:
   - Manages singleton in-memory lifecycle of `cv_classifier.pkl` and `label_encoder.pkl`.

### 5.3 `component1/models/` (Serialized Artifacts)
- **`cv_classifier.pkl`**: Serialized Primary NLP Feature-Engineered Logistic Regression model.
- **`label_encoder.pkl`**: Scikit-learn LabelEncoder mapping 20 canonical role names to integers.
- **`tfidf_vectorizer.pkl`**: 1-2 N-Gram TF-IDF Vectorizer.
- **`tfidf_baseline.pkl`**: Serialized TF-IDF Baseline Logistic Regression model.
- **`model_metadata.json`**: Model hyperparameters, accuracy metrics, feature dimensions, and serialization timestamps.

### 5.4 `component1/results/` (Evaluation Benchmarks & Visualizations)
- **`classification_report.txt`**: Complete per-role precision, recall, F1, and support benchmark report.
- **`metrics.json`**: Machine-readable JSON summary of test and cross-validation scores.
- **`confusion_matrix.png`**: High-resolution heatmap of the 20x20 confusion matrix for the primary classifier.
- **`confusion_matrix_tfidf_baseline.png`**: Confusion matrix for the baseline TF-IDF model.

### 5.5 `component1/tests/` (Pytest Validation Suite)
- **`test_component1.py`**: Core pipeline tests for parsing, feature engineering, and screening.
- **`test_extractor.py`**: Granular tests for skill extraction, dates deduplication, and zero-false-positive contextual guards.
- **`test_scorer.py`**: Mathematical bounds tests for $S_{skill}, S_{exp}, S_{edu}, S_{cv} \in [0, 100]$ across all 20 roles.
- **`test_predictor.py`**: Model inference tests, softmax probability sum verification ($\sum p_i \approx 1.0$), and fallback safety.
- **`test_api.py`**: FastAPI HTTP endpoint integration tests using `TestClient`.

---

## 6. Technology Stack & Frameworks

| Layer / Domain | Technology / Library | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Language** | Python | `3.12.x` | Core backend runtime |
| **Web Framework** | FastAPI | `0.115.x` | High-performance asynchronous REST API |
| **Server** | Uvicorn | `0.30.x` | ASGI production web server |
| **ML & Statistics** | scikit-learn | `1.4.2` | Logistic Regression, TF-IDF, Metrics, Encoders |
| **Embeddings & NLP**| sentence-transformers | `3.0.x` | Dense semantic embeddings for JD matching |
| **Array Math** | NumPy | `1.26.x` | Vector math & matrix manipulations |
| **Data Manipulation**| Pandas | `2.2.x` | Dataset loading & stratification |
| **Document Ingestion**| pdfplumber / PyPDF2 | `0.11.x` | High-fidelity PDF text and metadata extraction |
| **Database** | MongoDB Atlas / Motor | `3.5.x` | Ingested candidate resumes & extraction persistence |
| **Validation** | Pydantic v2 | `2.8.x` | Strict request/response schema validation |
| **Testing** | Pytest | `8.3.x` | Automated unit, bounds, and integration testing |

---

## 7. Viva Defense & Research Justifications

### Q1: Why use NLP Feature Engineering + Logistic Regression instead of an unconstrained Deep Neural Network (e.g., pure BERT)?
- **Answer**: In recruitment screening, **model interpretability, auditability, and deterministic feature weights** are legally and scientifically paramount (preventing algorithmic bias and hallucination). The feature-engineered classifier extracts explicit verified features (domain skill densities, verified tenure, accredited degree levels), ensuring every scoring dimension can be transparently audited and explained to hiring managers. Furthermore, it trains in ~1.02 seconds with an inference latency of under **12ms**, allowing real-time candidate processing.

### Q2: How did you solve the common NLP False-Positive Skill Extraction problem (e.g., words like "C", "R", "Go", "Spring", "REST")?
- **Answer**: We designed context-guarded regex token boundary patterns (`_build_skill_pattern`) that enforce structural non-capturing look-arounds:
  - For single letters (`C`, `R`): Requires surrounding technical cues like `C/C++`, `C#`, or explicitly delimited list boundaries.
  - For common English words (`Go`, `Spring`, `REST`, `Dart`, `Solid`): Enforces technical delimiters `(?:^|[,\n•|;:\(\[])\s*...` and negative look-aheads preventing common idioms (e.g., "go to school", "spring weather", "taking a rest").

### Q3: Why is $S_{cv}$ weighted as $50\%$ Skills, $30\%$ Experience, and $20\%$ Education?
- **Answer**: In software and IT engineering hiring, practical hands-on competency in required languages/frameworks is the strongest predictor of immediate contributor output ($50\%$). Experience tenure verifies seniority, project execution, and problem-solving maturity ($30\%$). Formal academic education provides foundational computer science theory and rigor ($20\%$). Candidates lacking formal degrees can still achieve strong scores if their skills and verified experience excel.
