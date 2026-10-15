import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_group_ch4(story, styles, p, b, sp, make_box, caption_style, fig_dir):
    PRIMARY = colors.HexColor("#1A365D")
    SECONDARY = colors.HexColor("#2B6CB0")
    DARK_TEXT = colors.HexColor("#2D3748")

    ch_num_style = styles['ChapterNumber']
    ch_title_style = styles['ChapterTitle']
    h1_style = styles['Heading1_Custom']
    h2_style = styles['Heading2_Custom']
    body_style = styles['Body_Custom']
    body_bold = styles['Body_Bold']

    story.append(p("CHAPTER 4", ch_num_style))
    story.append(p("DETAILED COMPONENT FORMULATIONS AND MATHEMATICAL MODELS", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    # =========================================================================
    # 4.1 COMPONENT 1: D. T. D. PERERA (IT22089236)
    # =========================================================================
    story.append(p("4.1 Component 1: Automated Resume Screening & Role Classification", h1_style))
    story.append(p("<b>Component Lead: D. T. D. Perera (IT22089236) | Microservice Port: 8001</b>", body_bold))
    story.append(p("Component 1 operates as the intake intelligence gateway of RecruitAI. It transforms raw, heterogeneous candidate resumes (PDF, DOCX) into mathematically auditable feature representations while eliminating polysemous token collisions and tenure inflation."))

    story.append(p("<i>4.1.1 Boundary-Guarded NER and Polysemy Shielding:</i> Technical competency extraction covers over 400 canonical IT skills organized across 7 core software engineering disciplines. To prevent the severe token collisions detailed in Chapter 2, skill patterns in extractor.py are compiled using context-guarded non-capturing look-around assertions. Single-letter languages (C, R) enforce leading delimiter look-behinds `(?&lt;=[\\s,;(\\[])` and trailing look-aheads `(?=[/\\s,;)\\]+]|$)` that exclude conversational prose. Short verb identifiers (Go, Rust, Spring, REST) are shielded with phrase guards that differentiate technical skills from colloquial English (Figure 4.1)."))

    fig_shield = os.path.join(fig_dir, "fig8_polysemy_shield.png")
    if os.path.exists(fig_shield):
        story.append(sp(3))
        story.append(Image(fig_shield, width=450, height=200))
        story.append(p("Figure 4.1: Context-Guarded Regex Look-Around Shielding vs. Naive Substring Tokenizers (Component 1).", caption_style))
        story.append(sp(3))

    story.append(p("<i>4.1.2 Lebesgue Interval Union Algebra:</i> To eliminate tenure inflation caused by concurrent employment (e.g., freelance consulting running parallel to a full-time corporate role), Component 1 models candidate work history as a finite set of closed intervals in time: I_i = [t_start^(i), t_end^(i)]. Rather than summing durations naively, true commercial tenure is computed as the Lebesgue measure of the union of all intervals: E_tot = mu(Union_{i=1}^M [t_start^(i), t_end^(i)]) = Sum_{k=1}^K (e_k - s_k), where {[s_k, e_k]} represents the sorted, disjoint merged intervals (Figure 4.2). Furthermore, academic and coursework projects are algorithmically filtered from commercial tenure and routed into technical skill evidence."))

    fig_temp = os.path.join(fig_dir, "fig7_temporal_algebra.png")
    if os.path.exists(fig_temp):
        story.append(sp(3))
        story.append(Image(fig_temp, width=450, height=208))
        story.append(p("Figure 4.2: Temporal Experience Disambiguation: Concurrent Employment Interval Merging (Component 1).", caption_style))
        story.append(sp(3))

    story.append(p("<i>4.1.3 Decoupled Two-Dimensional Academic Credential Model:</i> To prevent non-technical degree inflation, academic credentials are decoupled into two orthogonal dimensions: Degree Attainment Tier Level (L_deg in {50, 65, 80, 90, 100} for Foundation, Higher Diploma, Bachelor's, Master's, Doctorate) and Disciplinary Field Relevance Multiplier (M_field in {0.20, 0.50, 0.75, 1.00} for Non-Technical, Quantitative, Adjacent Technical, Core Computing):"))
    story.append(p("<b>S_edu = L_deg x M_field</b>", body_bold))
    story.append(p("Under this matrix, an accredited B.Sc. in Software Engineering receives 80.0 x 1.00 = 80.0, while a Ph.D. in Literature receives 100.0 x 0.20 = 20.0, restoring equitable evaluation."))

    story.append(p("<i>4.1.4 Balanced Multinomial Logistic Role Classification:</i> Candidate profiles are mapped across 20 canonical IT job roles using a balanced multinomial Logistic Regression classifier trained with sublinear TF-IDF vectorization (10,000 max features, sublinear_tf=True, L2 penalty with C=1.0). Evaluated on 819 authentic held-out resumes, the classifier achieves <b>87.42% accuracy</b>, <b>92.47% Macro F1</b>, and executes inference in just <b>2.4 ms</b> per candidate."))

    # =========================================================================
    # 4.2 COMPONENT 2: DULNITH K. D. (IT22094872)
    # =========================================================================
    story.append(p("4.2 Component 2: Autonomous Multi-Modal Technical Interview System", h1_style))
    story.append(p("<b>Component Lead: Dulnith K. D. (IT22094872) | Microservice Port: 8002</b>", body_bold))
    story.append(p("Component 2 conducts autonomous, multi-modal technical examinations dynamically aligned with the candidate's target job role and verified resume profile, evaluating verbal, theoretical, and practical coding capabilities."))

    story.append(p("<i>4.2.1 Retrieval-Augmented Interview Generation (RAIGS):</i> Rather than administering canned static question sets, Component 2 deploys the RAIGS algorithm across a curated 18,757-question corpus spanning 20 technical roles. Questions are retrieved by maximizing a multi-factor score: RAIGS_Score(q) = 0.60 Rel(q, R_tgt) + 0.20 Rec(q) + 0.20 Diff(q, theta), where Rel computes cosine similarity between question metadata and target role competencies, Rec enforces question rotation to prevent memorization, and Diff dynamically adapts difficulty to candidate seniority theta."))

    story.append(p("<i>4.2.2 Speech Transcription & Dense SBERT Rubric Grading:</i> Candidate spoken responses are recorded and transcribed using OpenAI's Whisper STT model, achieving an empirical Word Error Rate (WER) of 7.20%. To grade open-ended answers against authoritative engineering rubrics without requiring verbatim phrase matches, candidate answers and reference rubrics are projected into dense 768-dimensional embeddings using Sentence-BERT (`all-mpnet-base-v2`):"))
    story.append(p("<b>P_desc = 0.70 x cos(e_ans, e_rubric) + 0.30 x Recall_keywords</b>", body_bold))
    story.append(p("This dense semantic similarity grading achieves a strong correlation of <b>r = 0.884</b> against expert human grading panels, with a Mean Absolute Error of 0.038."))

    story.append(p("<i>4.2.3 AST-Secured Sandboxed Code Execution:</i> Practical programming questions require candidates to author executable Python code. Code submissions are inspected using Python's Abstract Syntax Tree (ast module) to intercept forbidden imports (e.g., `os`, `sys`, `subprocess`, `socket`). Approved code executes inside an isolated subprocess capped at 2.0 seconds execution time and 128 MB RAM, evaluated against hidden unit test assertions with a 100% security intercept rate."))
    story.append(p("The composite interview score is formulated as S_int = w_mcq P_mcq + w_desc P_desc + w_code P_code, calibrated per engineering discipline."))

    # =========================================================================
    # 4.3 COMPONENT 3: K. G. SAVINDA N. PERERA (IT22027610)
    # =========================================================================
    story.append(p("4.3 Component 3: Candidate Suitability Scoring and Listwise Ranking Engine", h1_style))
    story.append(p("<b>Component Lead: K. G. Savinda N. Perera (IT22027610) | Microservice Port: 8003</b>", body_bold))
    story.append(p("Component 3 synthesizes multi-source evaluation metrics into auditable, bias-audited candidate rankings, bridging intake screening with final hiring decisions."))

    story.append(p("<i>4.3.1 Prerequisite Gating and Soft Near-Miss Penalties:</i> To protect organizational hiring standards, candidate profiles undergo deterministic prerequisite validation: S_cv &gt;= 40%, S_int &gt;= 35%, and mandatory core skill coverage. However, recognizing that rigid binary cutoffs unfairly eliminate high-potential candidates who marginally miss a threshold, Component 3 introduces a continuous soft penalty factor: if a candidate achieves 38% on S_cv with exceptional interview scores (85%), a soft attenuation penalty is applied rather than instantaneous disqualification."))

    story.append(p("<i>4.3.2 Transparent Linear CSS Formulation:</i> Under Multi-Attribute Utility Theory (MAUT), qualified candidates receive an official Candidate Suitability Score (CSS):"))
    story.append(p("<b>CSS = w_cv . S_cv + w_int . S_int = 0.40 . S_cv + 0.60 . S_int</b>", body_bold))
    story.append(p("Weights are role-calibrated: coding-intensive roles weight live technical performance higher (w_int = 0.65), while architectural leadership roles place greater weight on proven commercial employment history (w_cv = 0.50)."))

    story.append(p("<i>4.3.3 Listwise LambdaMART Ranking Comparator:</i> To validate the ranking efficacy of our linear CSS formulation against non-linear Learning-to-Rank models, an offline LightGBM LambdaMART model was trained over 6,000 multi-source applicant profiles across 20 roles (800 trees, 31 leaves, pairwise lambda-gradients). The LambdaMART comparator achieves NDCG@1 = 0.9784, NDCG@5 = 0.9473, and MAP = 0.9798. Linear CSS captures 99.6% of this ranking fidelity while executing in under 0.1 ms with zero black-box obscurity."))

    story.append(p("<i>4.3.4 Closed-Form SHAP Explainability &amp; Fairness Auditing:</i> Linear CSS provides exact, instantaneous closed-form SHAP attributions: phi_i(x) = w_i . (x_i - E[x_i]). Recruiters are provided with full mathematical visibility into why candidate A ranked above candidate B. Furthermore, the ranking engine is audited for algorithmic fairness under the 80% Four-Fifths rule, achieving Demographic Parity disparity Delta_DP = 0.008 and Equal Opportunity disparity Delta_EO = 0.006, well within statutory non-discrimination limits."))

    # =========================================================================
    # 4.4 COMPONENT 4: YENURA S. KARUNANAYAKA (IT22306272)
    # =========================================================================
    story.append(p("4.4 Component 4: Skill Gap Diagnostics and Career Pathfinding System", h1_style))
    story.append(p("<b>Component Lead: Yenura S. Karunanayaka (IT22306272) | Microservice Port: 8004</b>", body_bold))
    story.append(p("Component 4 closes the recruitment loop by capturing unshortlisted candidate profiles and converting rejection telemetry into personalized, predictive career development."))

    story.append(p("<i>4.4.1 Two-Stage Fuzzy and Semantic Skill Gap Diagnostics:</i> When a candidate fails to attain the requisition shortlisting rank, Component 4 extracts the exact delta between candidate competencies and target role requirements using two-stage fuzzy string matching and semantic token alignment: G_s = (1 / |S_req|) Sum_{s in S_req} w_s . (1 - max_{c in C_cand} FuzzRatio(s, c)), identifying missing, partial, and mastered competencies."))

    story.append(p("<i>4.4.2 Tabular GBDT Hireability Ensemble:</i> Candidate hireability probability is predicted using a 300-tree Gradient Boosted Decision Tree (GBDT) ensemble trained across 67 dense features spanning skill match ratios, tenure adequacy, degree tier, and interview component scores. Evaluated over 20,000 candidate records, the GBDT model achieves an empirical accuracy of <b>91.50%</b> and an <b>ROC-AUC of 0.9763</b>, providing an authoritative probability estimate of candidate job-readiness under enterprise policy benchmarks."))

    story.append(p("<i>4.4.3 Paced Learning Roadmaps &amp; 47-Course Curriculum:</i> Rather than overwhelming candidates with exhaustive, unranked skill inventories, Component 4 prioritizes missing skills by GBDT feature importance and maps them to a curated catalog of 47 technical courses. Learning modules are paced realistically at exactly 2 skills per month: T_months = ceil(|G_missing| / 2), preventing cognitive burnout and maximizing completion rates."))

    story.append(p("<i>4.4.4 Directed Acyclic Graph (DAG) Career Lattice:</i> To facilitate lateral transitions and internal talent mobility, professional IT roles are formalized as a Directed Acyclic Graph (DAG) G = (V, E), where vertices V represent canonical roles across Junior, Mid, Senior, and Lead tiers, and directed edges E define valid career mobility paths weighted by competency transferability. Candidates can explore lateral transitions (e.g., Software Engineer &rarr; DevOps Engineer) that maximize existing skill equity while minimizing remedial retraining time."))
    story.append(PageBreak())
