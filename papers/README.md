# RecruitAI: Complete 6-Page IEEE Research Paper Suite

This repository houses the complete suite of **five publication-ready, 6-page IEEE conference research papers** developed for the **RecruitAI (AI-Driven Recruitment Ecosystem)** research initiative at the **Faculty of Computing, Sri Lanka Institute of Information Technology (SLIIT)**.

---

## 👥 Research Team & Student Identifiers

All five research papers prominently feature the full research team:
- **Yenura S. Karunanayaka** — Student ID: `IT22306272` (`it22306272@my.sliit.lk`)
- **K.G. Savinda N. Perera** — Student ID: `IT22027610` (`it22027610@my.sliit.lk`)
- **D.T. Tharindu Perera** — Student ID: `IT22089236` (`it22089236@my.sliit.lk`)

---

## 📚 Complete Research Paper Index

| Paper Directory | Paper Title | Core Scientific Focus & Innovation |
|:---|:---|:---|
| [`papers/integrated_system_paper/`](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/papers/integrated_system_paper) | **RecruitAI: An End-to-End Fair and Explainable Talent Acquisition Ecosystem Integrating Multi-Modal Evaluation, Learning-to-Rank, and Skill-Gap Remediation** | **Integrated Ecosystem (C1 + C2 + C3 + C4)**: Unifying boundary-guarded parsing ($S_{cv}$), dynamic multi-modal interviewing ($S_{int}$), dual-engine ranking (CSS + LambdaMART), and closed-loop DAG career progression with exact closed-form SHAP explainability. |
| [`papers/component1_resume_screening/`](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/papers/component1_resume_screening) | **Context-Aware Resume Parsing, Boundary-Guarded NER, and Multi-Class Specialization for Automated Technical Screening** | **Component 1**: Document layout normalization, automated PII masking, boundary-guarded NER over 400+ technical competencies, sublinear TF-IDF classification across 20 roles (90.49\% accuracy, 93.47\% Macro F1), and Tri-Pillar qualification modeling ($S_{cv}$). |
| [`papers/component2_interview_system/`](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/papers/component2_interview_system) | **Autonomous Multi-Modal Technical Interview System: Dynamic Question Synthesis, SBERT Semantic Grading, and Sandboxed Code Verification** | **Component 2**: 18,757 question corpus, RAIGS adaptive question selection, Sentence-BERT (`all-mpnet-base-v2`) 768-dim semantic grading ($r = 0.884$ with human experts), containerized AST code sandboxing, and role-adaptive composite scoring ($S_{int}$). |
| [`papers/component3_candidate_ranking/`](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/papers/component3_candidate_ranking) | **Auditable and Equitable Candidate Ranking: Combining Multi-Criteria Gating with LambdaMART Learning-to-Rank and Exact SHAP Attribution** | **Component 3**: Deterministic prerequisite gating, soft near-miss penalty ($\gamma \in [0.70, 0.95]$), Candidate Suitability Score ($CSS$), 800-tree LightGBM LambdaMART LTR benchmark (NDCG@1: 97.84\%, NDCG@5: 94.37\%), FA*IR demographic parity auditing ($|DP| = 0.008$), and exact linear SHAP attribution. |
| [`papers/component4_skill_gap_career/`](file:///c:/Users/thari/Desktop/My%20Project/R26-IT-148/papers/component4_skill_gap_career) | **Data-Driven Skill-Gap Diagnostics and Automated Career Mobility: Gradient-Boosted Hireability Prediction and DAG Curriculum Synthesis** | **Component 4**: 20,000-record dataset with 67 engineered features, Gradient Boosting hireability classification (ROC-AUC 0.9763, Accuracy 91.50\%), two-stage fuzzy skill gap triage, hybrid hireability ensemble ($0.60P_{ML} + 0.40S_{ext}$), 47-course catalog, 2 skills/month pacing, and Directed Acyclic Graph (DAG) career pathing. |

---

## 🎨 Professional Vector Diagrams (Native TikZ)

Every research paper includes an embedded **TikZ vector architecture diagram** that renders sharply in any resolution, perfectly matches IEEE publication fonts, and compiles natively in Overleaf and standard TeX distributions with **zero missing graphic file errors**:
- `integrated_system_paper/main.tex`: Full-width end-to-end 4-tier pipeline diagram.
- `component1_resume_screening/main.tex`: Layout normalization, NER boundary guard assertions, and TF-IDF classification head.
- `component2_interview_system/main.tex`: RAIGS selection, three-tier examination (MCQ, SBERT, AST Sandbox), and composite scoring.
- `component3_candidate_ranking/main.tex`: Prerequisite gating, MAUT vs. LambdaMART dual branches, FA*IR auditing, and SHAP waterfalls.
- `component4_skill_gap_career/main.tex`: Fuzzy gap extraction, severity classification, 2-skills/month timeline, and DAG career lattice.

---

## 🚀 How to Compile in Overleaf

For any of the 5 papers:
1. Navigate into that paper's subdirectory (e.g., `papers/integrated_system_paper/`).
2. Select all files in that directory (`main.tex`, `IEEEtran.cls`, `references.bib`, `README.md`) and create a `.zip` archive.
3. On [Overleaf](https://www.overleaf.com), click **New Project $\rightarrow$ Upload Project** and upload your zip file.
4. Set compiler to `pdfLaTeX` and click **Recompile**.
