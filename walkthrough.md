# Walkthrough: Master Research Reports Suite (R26-IT-148)

We have created the complete, publication-ready suite of **five (5) IEEE conference research reports** for project **R26-IT-148** (*AI-Driven Recruitment Ecosystem for Intelligent Job Matching and Predictive Career Development*), organized in an Overleaf-ready project structure with authoritative member data, verified empirical metrics, and self-contained native TikZ vector diagrams.

---

## 👥 Authoritative Author Team

| Full Name | Student ID | Academic Email | Role | Lead Paper |
| :--- | :--- | :--- | :--- | :--- |
| **D. T. Tharindu Perera** | `IT22089236` | `it22089236@my.sliit.lk` | **Component 1 Lead** | [Report 2: Component 1](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/overleaf_reports/report_02_component_1/main.tex) |
| **Dulnith K. D.** | `IT22094872` | `it22094872@my.sliit.lk` | **Component 2 Lead** | [Report 3: Component 2](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/overleaf_reports/report_03_component_2/main.tex) |
| **K. G. Savinda N. Perera** | `IT22027610` | `it22027610@my.sliit.lk` | **Component 3 Lead** | [Report 4: Component 3](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/overleaf_reports/report_04_component_3/main.tex) |
| **Yenura S. Karunanayaka** | `IT22306272` | `it22306272@my.sliit.lk` | **Component 4 Lead** | [Report 5: Component 4](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/overleaf_reports/report_05_component_4/main.tex) |

*Affiliation: Faculty of Computing, Sri Lanka Institute of Information Technology (SLIIT), Malabe, Sri Lanka.*

---

## 📁 Overleaf Project Structure

The suite is housed under `overleaf_reports/` with complete independent compilability for each subfolder:

```
overleaf_reports/
├── MASTER_README.md                        # Master Suite Documentation
├── report_01_full_system/                  # REPORT 1: Complete Integrated Recruitment Ecosystem
│   ├── main.tex                            # ~6-page IEEE LaTeX Source File
│   ├── references.bib                      # Verified BibTeX Database (18 Citations)
│   ├── IEEEtran.cls                        # Standalone Official IEEE LaTeX Class v1.8b
│   └── README.md                           # Report-Specific Compilation Guide
├── report_02_component_1/                  # REPORT 2: Automated Resume Screening & Role Classification
│   ├── main.tex                            # ~6-page IEEE LaTeX Source File
│   ├── references.bib                      # Verified BibTeX Database (10 Citations)
│   ├── IEEEtran.cls                        # Standalone Official IEEE LaTeX Class v1.8b
│   └── README.md                           # Report-Specific Compilation Guide
├── report_03_component_2/                  # REPORT 3: Autonomous Multi-Modal Technical Interview System
│   ├── main.tex                            # ~6-page IEEE LaTeX Source File
│   ├── references.bib                      # Verified BibTeX Database (10 Citations)
│   ├── IEEEtran.cls                        # Standalone Official IEEE LaTeX Class v1.8b
│   └── README.md                           # Report-Specific Compilation Guide
├── report_04_component_3/                  # REPORT 4: Candidate Suitability Scoring & Listwise Ranking
│   ├── main.tex                            # ~6-page IEEE LaTeX Source File
│   ├── references.bib                      # Verified BibTeX Database (10 Citations)
│   ├── IEEEtran.cls                        # Standalone Official IEEE LaTeX Class v1.8b
│   └── README.md                           # Report-Specific Compilation Guide
└── report_05_component_4/                  # REPORT 5: Skill Gap Analysis & Personalized Career Development
    ├── main.tex                            # ~6-page IEEE LaTeX Source File
    ├── references.bib                      # Verified BibTeX Database (9 Citations)
    ├── IEEEtran.cls                        # Standalone Official IEEE LaTeX Class v1.8b
    └── README.md                           # Report-Specific Compilation Guide
```

---

## 📊 Summary of Created Research Reports

### 1. Report 1: Complete System Paper
- **Title:** *AI-Driven Recruitment Ecosystem for Intelligent Job Matching and Predictive Career Development*
- **Scope:** Complete RecruitAI ecosystem coordinating Component 1 + Component 2 + Component 3 + Component 4 via the unified FastAPI Gateway (Port 8000).
- **Key Diagrams (TikZ):**
  - `Fig. 1`: Full multi-microservice architecture (Gateway, Ports 8000–8004, React 18, MongoDB Atlas).
  - `Fig. 2`: End-to-end recruitment lifecycle and candidate state machine.
  - `Fig. 3`: Directed Acyclic Graph (DAG) career lattice depicting vertical and lateral mobility.
- **Empirical Tables:** Microservice deployment telemetry (p95 latency, throughput), verified cross-component empirical benchmarks.

### 2. Report 2: Component 1 Paper
- **Title:** *Automated Semantic Resume Screening and IT Job Role Classification*
- **Scope:** Ingestion of PDF/DOCX resumes, 400+ NER competencies, sublinear TF-IDF role classification, and uncollapsed tri-pillar qualification vector ($S_{skill}, S_{exp}, S_{edu}$).
- **Scientific Integrity:**
  - Explains and addresses the historical synthetic template memorization leakage ($F_1 = 1.0$ artifact).
  - Evaluated on a real 4,000 CV corpus (819 held-out test profiles across 20 roles): **90.49% accuracy, 91.56% macro-$F_1$, 93.47% weighted-$F_1$**.
  - Strict separation of Total Professional Experience ($E_{tot}$), IT-Sector Experience ($E_{it}$), and Role-Relevant Experience ($E_{rel}$) with interval overlap resolution.
  - Decouples degree level (Tier 1 Ph.D. to Diploma) from disciplinary field relevance.
  - Weights technical skills by evidence strength (isolated keyword listing vs. demonstrated employment usage).
- **Key Diagrams (TikZ):**
  - `Fig. 1`: Multi-stage document ingestion and semantic extraction pipeline.
  - `Fig. 2`: Experience parsing decision tree (overlap resolution, IT filtering, role relevance).
  - `Fig. 3`: Education credential decoupling and skill evidence hierarchy.

### 3. Report 3: Component 2 Paper
- **Title:** *Autonomous Multi-Modal Technical Interview System with Semantic Evaluation and Sandbox Execution*
- **Scope:** Autonomous technical interview generation, administration, and rubric-based evaluation on Port 8002.
- **Scientific Highlights:**
  - 18,757-question corpus across 20 canonical IT roles.
  - Retrieval-Augmented Interview Generation and Selection (RAIGS) balancing relevance (60%), recency (20%), and difficulty match (20%).
  - Dense Sentence-BERT (`all-mpnet-base-v2`, 768-d) rubric evaluation achieving **$r = 0.884$** correlation with human technical evaluators.
  - Whisper STT speech transcription (**7.20% WER**).
  - AST-secured Python sandbox with 100% malicious call interception, 2.0s execution timeout, and 128MB ceiling.
  - Role-adaptive composite interview score $S_{int} = w_{mcq}P_{mcq} + w_{desc}P_{desc} + w_{code}P_{code}$.
- **Key Diagrams (TikZ):**
  - `Fig. 1`: Autonomous technical interview architecture and multi-modal assessment flow.
  - `Fig. 2`: RAIGS adaptive question retrieval and exam battery assembly pipeline.
  - `Fig. 3`: Semantic rubric grading pipeline for descriptive spoken responses.

### 4. Report 4: Component 3 Paper
- **Title:** *Candidate Suitability Scoring and Intelligent Candidate Ranking Using Listwise Learning-to-Rank*
- **Scope:** Multi-attribute candidate scoring and listwise candidate ranking on Port 8003.
- **Scientific Highlights:**
  - Ingestion of uncollapsed tri-pillar vector ($S_{skill}, S_{exp}, S_{edu}$) and interview scores ($P_{mcq}, P_{desc}, P_{code}$).
  - Two-stage decision model: prerequisite gating filter with soft near-miss penalty ($\gamma \in [0.85, 0.95]$) followed by linear Candidate Suitability Score ($CSS = 0.40 S_{cv} + 0.60 S_{int}$).
  - Benchmark on 6,000 candidate profiles across 20 roles: **NDCG@5 = 0.9437, NDCG@10 = 0.9428, MAP = 0.9776, Spearman $\rho = 0.6232$ ($p < 0.001$)**.
  - Verified against an 800-tree LightGBM LambdaMART comparator (**NDCG@5 = 0.9473, MAP = 0.9798, Spearman $\rho = 0.7030$**), proving linear CSS captures 99.6% of maximum listwise ranking fidelity.
  - Exact linear SHAP explainability ($\phi_i = w_i(x_i - \mathbb{E}[x_i])$).
  - Continuous algorithmic fairness audit: demographic parity difference ($\Delta_{DP} = 0.008$) and equal opportunity difference ($\Delta_{EO} = 0.006$), well within the 0.05 threshold.
- **Key Diagrams (TikZ):**
  - `Fig. 1`: Candidate Suitability Scoring (CSS) multi-criteria decision architecture.
  - `Fig. 2`: Prerequisite gating decision curve with soft near-miss penalty transition.
  - `Fig. 3`: Continuous algorithmic fairness verification workflow.

### 5. Report 5: Component 4 Paper
- **Title:** *Skill Gap Analysis and Personalized Career Development Using Gradient Boosted Decision Trees*
- **Scope:** Skill gap diagnosis, predictive hireability modeling, and career progression navigation on Port 8004.
- **Scientific Highlights:**
  - Two-stage fuzzy string and semantic matching isolating missing skills and computing gap severity index $G_s$.
  - 67-feature Gradient Boosted Decision Tree (GBDT) ensemble (300 trees): **91.50% accuracy, 0.8670 $F_1$-score, 0.9763 ROC-AUC**.
  - **Scientific Target Clarification:** Clearly documented as a rule-based hireability classification target under organizational policy benchmarks due to the absence of longitudinal multi-year post-hire corporate retention data.
  - Curated 47-course catalog generating structured monthly roadmaps paced realistically at 2 skills per month ($T = \lceil |\mathcal{G}| / 2 \rceil$).
  - Directed Acyclic Graph (DAG) career lattice modeling vertical promotions and lateral cross-skilling.
- **Key Diagrams (TikZ):**
  - `Fig. 1`: Skill gap analysis and personalized career development architecture.
  - `Fig. 2`: Two-stage fuzzy skill matching, gap severity computation, and monthly course synthesis.
  - `Fig. 3`: Directed Acyclic Graph (DAG) career progression lattice.

---

## 🚀 Overleaf Compilation Verification

Each folder contains its own official `IEEEtran.cls` (v1.8b), ensuring that zipping any folder or the entire suite results in clean compilation with `pdfLaTeX` on Overleaf with zero missing package or font warnings.
