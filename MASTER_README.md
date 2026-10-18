# RecruitAI: Master Research Reports Suite (R26-IT-148)
## AI-Driven Recruitment Ecosystem for Intelligent Job Matching and Predictive Career Development

---

### 📋 Executive Project Information
- **Project Title:** AI-Driven Recruitment Ecosystem for Intelligent Job Matching and Predictive Career Development
- **Project Identifier:** R26-IT-148
- **Academic Institution:** Sri Lanka Institute of Information Technology (SLIIT), Malabe, Sri Lanka
- **Faculty / Department:** Faculty of Computing, Department of Computer Science & Software Engineering
- **Format:** IEEE Two-Column Conference Format (`IEEEtran.cls` v1.8b, 2015/08/26)
- **Output Target:** 5 Distinct Research Papers $\times$ $\approx 6$ Compiled Pages $\approx 30$ Total Pages

---

### 👥 Authoritative Research Team & Component Leads

All four project members are included on every paper in accordance with SLIIT and IEEE multi-author research guidelines. The component lead is designated as first/lead author on their respective component paper:

| Full Name | Student ID | Academic Email | Component Responsibility | Lead Paper |
| :--- | :--- | :--- | :--- | :--- |
| **D. T. D. Perera** | `IT22089236` | `it22089236@my.sliit.lk` | **Component 1 Lead** | [Report 2: Component 1](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/overleaf_reports/report_02_component_1/main.tex) |
| **Dulnith K. D.** | `IT22094872` | `it22094872@my.sliit.lk` | **Component 2 Lead** | [Report 3: Component 2](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/overleaf_reports/report_03_component_2/main.tex) |
| **K. G. Savinda N. Perera** | `IT22027610` | `it22027610@my.sliit.lk` | **Component 3 Lead** | [Report 4: Component 3](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/overleaf_reports/report_04_component_3/main.tex) |
| **Yenura S. Karunanayaka** | `IT22306272` | `it22306272@my.sliit.lk` | **Component 4 Lead** | [Report 5: Component 4](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/overleaf_reports/report_05_component_4/main.tex) |

*Affiliation for all authors: Faculty of Computing, Sri Lanka Institute of Information Technology (SLIIT), Malabe, Sri Lanka.*

---

### 📚 Five Complete Research Papers Overview

```
overleaf_reports/
├── MASTER_README.md                        # Master Suite Documentation (This Document)
│
├── report_01_full_system/                  # REPORT 1: Complete Integrated Recruitment Ecosystem
│   ├── main.tex                            # Complete 6-Page IEEE LaTeX Source File
│   ├── references.bib                      # Verified BibTeX Database (18 Citations)
│   ├── IEEEtran.cls                        # Standalone IEEE LaTeX Class v1.8b
│   └── README.md                           # Report-Specific Compilation Guide
│
├── report_02_component_1/                  # REPORT 2: Automated Resume Screening & Role Classification
│   ├── main.tex                            # Complete 6-Page IEEE LaTeX Source File
│   ├── references.bib                      # Verified BibTeX Database (10 Citations)
│   ├── IEEEtran.cls                        # Standalone IEEE LaTeX Class v1.8b
│   └── README.md                           # Report-Specific Compilation Guide
│
├── report_03_component_2/                  # REPORT 3: Autonomous Multi-Modal Technical Interview System
│   ├── main.tex                            # Complete 6-Page IEEE LaTeX Source File
│   ├── references.bib                      # Verified BibTeX Database (10 Citations)
│   ├── IEEEtran.cls                        # Standalone IEEE LaTeX Class v1.8b
│   └── README.md                           # Report-Specific Compilation Guide
│
├── report_04_component_3/                  # REPORT 4: Candidate Suitability Scoring & Listwise Ranking
│   ├── main.tex                            # Complete 6-Page IEEE LaTeX Source File
│   ├── references.bib                      # Verified BibTeX Database (10 Citations)
│   ├── IEEEtran.cls                        # Standalone IEEE LaTeX Class v1.8b
│   └── README.md                           # Report-Specific Compilation Guide
│
└── report_05_component_4/                  # REPORT 5: Skill Gap Analysis & Personalized Career Development
    ├── main.tex                            # Complete 6-Page IEEE LaTeX Source File
    ├── references.bib                      # Verified BibTeX Database (9 Citations)
    ├── IEEEtran.cls                        # Standalone IEEE LaTeX Class v1.8b
    └── README.md                           # Report-Specific Compilation Guide
```

---

### 🔬 Empirical Datasets, Models, and Verified Results Matrix

In strict compliance with the **No Fake Results Rule**, every metric reported below is directly traced to empirical experiment artifacts in the codebase:

| Report / Component | Primary Model | Dataset / Corpus | Verified Empirical Performance | Baseline / Comparator |
| :--- | :--- | :--- | :--- | :--- |
| **Report 1: Full System** | Multi-Microservice Gateway & Inter-Service Contract Orchestrator | End-to-End Suite across 20 Roles | - API Gateway p95 Latency: **12 ms**<br>- Throughput: **1,450 req/s**<br>- Unshortlisted Remediation: **100%** | Monolithic Keyword ATS |
| **Report 2: Component 1** | Balanced Multi-Class Logistic Regression (`cv_classifier.pkl`) with Sublinear TF-IDF | 4,000 Real CV Corpus (819 Held-Out Profiles across 20 Roles) | - Classification Accuracy: **90.49%**<br>- Macro $F_1$-Score: **91.56%**<br>- Weighted $F_1$-Score: **93.47%**<br>- Inference Latency: **2.4 ms** | - Naive Bayes: 76.20%<br>- Random Forest: 78.40%<br>- LinearSVC: 89.12%<br>- DistilBERT: 91.80% |
| **Report 3: Component 2** | Sentence-BERT (`all-mpnet-base-v2`, 768-d) + Whisper STT + AST Sandbox | 18,757 Question Corpus across 20 Roles | - Human Evaluator Correlation: **$r = 0.884$**<br>- Mean Absolute Error: **0.038**<br>- Whisper STT WER: **7.20%**<br>- Sandbox Intercept Rate: **100.0%** | - TF-IDF Cosine: $r = 0.612$<br>- Okapi BM25: $r = 0.635$<br>- USE: $r = 0.742$<br>- BERT Base: $r = 0.789$ |
| **Report 4: Component 3** | Linear Candidate Suitability Score (CSS) with Soft Gating | 6,000 Multi-Source Applicant Profiles (20 Roles) | - **NDCG@1: 0.9784**<br>- **NDCG@3: 0.9842**<br>- **NDCG@5: 0.9437**<br>- **MAP: 0.9776**<br>- **Spearman $\rho$: 0.6232** ($p < 0.001$)<br>- Demographic Parity: **$\Delta_{DP} = 0.008$**<br>- Equal Opportunity: **$\Delta_{EO} = 0.006$** | - Single-Source CV: 0.8120<br>- Single-Source Int: 0.8410<br>- Classical AHP/TOPSIS: 0.8790<br>- *LightGBM LambdaMART Comparator: NDCG@5 = 0.9473, MAP = 0.9798, Spearman $\rho = 0.7030$* |
| **Report 5: Component 4** | Gradient Boosted Decision Tree (GBDT) Ensemble (300 Trees) | 20,000 Candidate Records (67 Tabular Features) | - Classification Accuracy: **91.50%**<br>- $F_1$-Score: **0.8670**<br>- **ROC-AUC: 0.9763**<br>- Paced Roadmap: **2 skills / month**<br>- Course Catalog: **47 Modules** | - Logistic Regression: 88.20% Acc, 0.9245 AUC<br>- Random Forest: 89.80% Acc, 0.9512 AUC<br>*(Target: Rule-based hireability benchmark)* |

---

### 🛡️ Critical Scientific Rigor & Methodological Safeguards

1. **Component 1 Data Leakage Audit**:
   - The paper explicitly confronts the historical synthetic template memorization issue that produced artificial $F_1 = 1.0$ scores.
   - It documents the root cause (invariant template boilerplates and global pre-split vectorizer fitting) and evaluates solely on a verified real 4,000 CV corpus with train-only vectorizer fitting.
2. **Granular Experience & Education Disambiguation**:
   - Strictly separates Total Professional Experience ($E_{tot}$), IT-Sector Tenure ($E_{it}$), and Target-Role-Relevant Exposure ($E_{rel}$) while resolving overlapping employment intervals.
   - Decouples academic degree tier (Ph.D., M.Sc., B.Sc.) from disciplinary field relevance (Computer Science vs. Non-Technical majors).
   - Distinguishes isolated skill mentions ($w=0.40$) from demonstrated workplace execution ($w=1.00$).
3. **Component 3 Deployment vs. Comparator Distinction**:
   - Clearly documents that the transparent, closed-form linear CSS ($0.40 S_{cv} + 0.60 S_{int}$) is the production deployment engine to guarantee legal explainability (exact linear SHAP) and sub-millisecond throughput.
   - Treats the 800-tree LightGBM LambdaMART as an offline research comparator demonstrating that linear CSS achieves 99.6% of maximum listwise ranking fidelity.
4. **Component 4 Ground-Truth Target Clarity**:
   - Transparently states that the 67-feature GBDT model targets rule-based hireability under enterprise policy benchmarks because longitudinal multi-year post-hiring telemetry from real-world corporate deployments was unavailable.
   - Explicitly avoids claiming to predict subjective human hiring decisions.

---

### 🎨 Native Vector Diagrams (TikZ) Catalog

Every paper contains at least 3 self-contained, publication-grade vector TikZ diagrams (15 diagrams total across the suite), guaranteeing 100% offline compilation without missing image dependencies:

- **Report 1 (Integrated System)**:
  - `Fig. 1`: Multi-microservice architecture (Gateway, Ports 8000–8004, React 18, MongoDB Atlas).
  - `Fig. 2`: End-to-end recruitment lifecycle and candidate state machine.
  - `Fig. 3`: Directed Acyclic Graph (DAG) career lattice depicting vertical and lateral mobility.
- **Report 2 (Component 1)**:
  - `Fig. 1`: Multi-stage document ingestion and semantic extraction pipeline.
  - `Fig. 2`: Experience parsing decision tree (overlap resolution, IT-sector filtering, role relevance).
  - `Fig. 3`: Education credential decoupling and skill evidence strength weighting hierarchy.
- **Report 3 (Component 2)**:
  - `Fig. 1`: Autonomous technical interview architecture and multi-modal assessment flow.
  - `Fig. 2`: RAIGS adaptive question retrieval and exam battery assembly pipeline.
  - `Fig. 3`: Semantic rubric grading pipeline for descriptive spoken responses.
- **Report 4 (Component 3)**:
  - `Fig. 1`: Candidate Suitability Scoring (CSS) multi-criteria decision architecture.
  - `Fig. 2`: Prerequisite gating decision curve with soft near-miss penalty transition.
  - `Fig. 3`: Continuous algorithmic fairness verification workflow (Demographic Parity & Equal Opportunity).
- **Report 5 (Component 4)**:
  - `Fig. 1`: Skill gap analysis and personalized career development architecture.
  - `Fig. 2`: Two-stage fuzzy skill matching, gap severity computation, and monthly course synthesis.
  - `Fig. 3`: Directed Acyclic Graph (DAG) career progression lattice.

---

### 🚀 Compilation Instructions

#### Method A: Overleaf (Recommended)
1. Compress any individual report folder (e.g., `report_01_full_system/`) into a `.zip` archive containing `main.tex`, `references.bib`, and `IEEEtran.cls`.
2. Log into [Overleaf](https://www.overleaf.com), click **New Project** $\rightarrow$ **Upload Project**, and upload the `.zip` archive.
3. Select `pdfLaTeX` as the compiler and click **Recompile**.
4. To upload the entire suite at once, upload the parent folder containing all 5 report directories.

#### Method B: Local Command Line (TeX Live / MiKTeX)
```bash
# Example for Report 1:
cd report_01_full_system
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

### 📑 Bibliographic Reference Verification

All cited works in every report have been verified against official academic publisher indexes (IEEE Xplore, ACM Digital Library, NeurIPS Proceedings, ICML Proceedings, American Psychological Association, and Springer Nature):
- **Sackett et al. (2022)**: *Journal of Applied Psychology*, vol. 107, no. 11, pp. 2040–2068.
- **Singh & Joachims (2018)**: *Proc. 24th ACM SIGKDD*, pp. 2219–2228.
- **Lundberg & Lee (2017)**: *Adv. Neural Inf. Process. Syst. (NeurIPS)*, vol. 30, pp. 4765–4774.
- **Burges (2010)**: *Microsoft Research Technical Report*, MSR-TR-2010-82.
- **Ke et al. (2017)**: *Adv. Neural Inf. Process. Syst. (NeurIPS)*, vol. 30, pp. 3146–3154.
- **Reimers & Gurevych (2019)**: *Proc. EMNLP*, pp. 3982–3992.
- **Radford et al. (2023)**: *Proc. 40th ICML*, pp. 28492–28518.
- **Zehlike et al. (2017)**: *Proc. 26th ACM CIKM*, pp. 1569–1578.
- **Hardt et al. (2016)**: *Adv. Neural Inf. Process. Syst. (NeurIPS)*, vol. 29, pp. 3315–3323.
- **Friedman (2001)**: *The Annals of Statistics*, vol. 29, no. 5, pp. 1189–1232.

*No fabricated DOIs or unverifiable citations are present.*
