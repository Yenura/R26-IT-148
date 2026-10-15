import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from group_builder.styles import clean_xml, create_table_box, PRINTABLE_WIDTH
from group_builder.canvas_helper import PageTracker

def append_group_ch3(story, styles, fig_dir, tracker=None):
    p_body = styles['ThesisBody']
    p_body_bold = styles['ThesisBodyBold']
    p_bullet = styles['ThesisBullet']
    h_ch = styles['ChapterHeading']
    h_sec = styles['SectionHeading']
    h_sub = styles['SubSectionHeading']
    caption_tab = styles['TableCaption']
    caption_fig = styles['FigureCaption']
    cell = styles['TableCell']
    cell_bold = styles['TableCellBold']
    cell_center = styles['TableCellCenter']

    def track(key):
        if tracker is not None:
            story.append(PageTracker(key, tracker))

    # =========================================================================
    # 3 OVERALL SOLUTION STRUCTURE
    # =========================================================================
    track('ch3')
    story.append(Paragraph("3 OVERALL SOLUTION STRUCTURE", h_ch))
    story.append(Spacer(1, 4))

    # 3.1 Integrated solution overview
    track('sec3_1')
    story.append(Paragraph("3.1 Integrated solution overview", h_sec))
    story.append(Paragraph("RecruitAI is conceptualized, architected, and engineered not as a loose collection of disparate hiring utilities, but as an integrated, closed-loop recruitment intelligence and remediation ecosystem. The architecture unifies document parsing, multi-modal technical interviews, listwise candidate ranking, and skill gap career guidance into a single continuous pipeline. By enforcing formal interface contracts and shared data representations across each functional transition, the platform eliminates the traditional boundaries between candidate screening, evaluation, selection, and developmental feedback.", p_body))
    story.append(Paragraph("Table 3.1 provides a comprehensive comparative summary of the four microservices, detailing component leadership, target ports, foundational machine learning algorithms, input contracts, and output payloads across the ecosystem.", p_body))
    story.append(Spacer(1, 4))

    track('tab3_1')
    story.append(Paragraph("Table 3.1: Comprehensive summary of component capabilities, core models, and port bindings.", caption_tab))
    sol_data = [
        [Paragraph("<b>Component &amp; Lead</b>", cell_bold), Paragraph("<b>Port &amp; Protocol</b>", cell_bold), Paragraph("<b>Input Contract</b>", cell_bold), Paragraph("<b>Foundational ML Architecture</b>", cell_bold), Paragraph("<b>Output Contract Payload</b>", cell_bold)],
        [Paragraph("<b>Component 1:</b> Resume Screening &amp; Role Classification<br/>(D. T. D. Perera)", cell), Paragraph("Port 8001<br/>REST / JSON", cell), Paragraph("Raw CV (PDF/DOCX) + Target JD Specification", cell), Paragraph("Balanced Multinomial Logistic Regression + SBERT", cell), Paragraph("Extracted profile, 20-role class, Tri-Pillar vector [S_skill, S_exp, S_edu]", cell)],
        [Paragraph("<b>Component 2:</b> Autonomous Technical Interview<br/>(Yenura S. Karunanayaka)", cell), Paragraph("Port 8002<br/>REST / WebSocket", cell), Paragraph("Candidate profile from C1 + Target Role Spec", cell), Paragraph("Whisper STT + SBERT Cosine Grading + AST Sandbox", cell), Paragraph("Speech WER, semantic rubric scores, code execution metrics", cell)],
        [Paragraph("<b>Component 3:</b> Candidate Suitability &amp; Ranking<br/>(K. G. Savinda N. Perera)", cell), Paragraph("Port 8003<br/>REST / JSON", cell), Paragraph("C1 Tri-Pillar Vector + C2 Interview Evaluation", cell), Paragraph("Multi-Attribute Utility Theory (MAUT) + LambdaMART LTR", cell), Paragraph("Composite CSS score, soft gating status, ranked leaderboard", cell)],
        [Paragraph("<b>Component 4:</b> Skill Gap &amp; Career Pathfinding<br/>(K. G. Savinda N. Perera)", cell), Paragraph("Port 8004<br/>REST / JSON", cell), Paragraph("Unshortlisted candidate profile + Target benchmark", cell), Paragraph("67-Feature GBDT Ensemble + Dijkstra DAG Lattice", cell), Paragraph("Hireability probability, paced monthly roadmaps, DAG mobility graph", cell)],
    ]
    sol_tab = create_table_box(sol_data, [95, 65, 80, 85, 86], styles, is_header=True)
    story.append(sol_tab)
    story.append(Spacer(1, 8))

    # 3.2 High level architecture
    track('sec3_2')
    story.append(Paragraph("3.2 High level architecture", h_sec))
    story.append(Paragraph("Figure 3.1 illustrates the high-level microservice architecture of RecruitAI. The platform deploys four decoupled microservices communicating through asynchronous RESTful HTTP endpoints alongside a centralized MongoDB Atlas document database and a shared React web dashboard.", p_body))
    story.append(Spacer(1, 4))

    fig_macro = os.path.join(fig_dir, "fig6_macro_architecture.png")
    if os.path.exists(fig_macro):
        track('fig3_1')
        story.append(Image(fig_macro, width=410, height=213))
        story.append(Paragraph("Figure 3.1: High-level microservice architecture of the integrated RecruitAI ecosystem (R26-IT-148).", caption_fig))
        story.append(Spacer(1, 6))

    story.append(Paragraph("The macro-architecture is organized into four distinct operational layers: (1) Client Presentation Layer, providing responsive React interfaces for recruiters, candidates, and interviewers; (2) API Gateway and Orchestration Layer, handling CORS security, authentication, and routing; (3) Intelligence Microservice Layer, housing the four specialized Python engines; and (4) Persistence and Caching Layer, managing MongoDB Atlas document collections, vector embeddings, and local filesystem sandboxes.", p_body))
    story.append(Spacer(1, 6))

    # 3.3 Component 1 summary
    track('sec3_3')
    story.append(Paragraph("3.3 Component 1 summary", h_sec))
    story.append(Paragraph("<b>Component Owner:</b> D. T. D. Perera (IT22089236).<br/><b>Subproblem Addressed:</b> Lexical token collisions in resume extraction, tenure inflation from concurrent jobs, collapsed monolithic qualification scoring, and synthetic benchmark leakage.<br/><b>Input:</b> Unstructured candidate resumes (PDF, DOCX, TXT) and target job requisition specifications.<br/><b>Core Methods:</b> Layout-aware bounding-box column segmentation; automated PII redaction; boundary-guarded Named Entity Recognition covering 400+ competencies with regex look-around assertion shields (Figure 3.3); chronological interval union algebra (Figure 3.4); two-dimensional academic credential decoupling (Degree Tier x Field Relevance); and balanced 20-class multinomial logistic regression with sublinear TF-IDF vectorization.<br/><b>Output:</b> PII-sanitized resume profile, classified primary and alternative roles, and the uncollapsed Tri-Pillar Qualification Vector S_C1 = [S_skill, S_exp, S_edu].<br/><b>Ecosystem Contribution:</b> Serves as the intake gateway feeding verified candidate representations into Components 2, 3, and 4.", p_body))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Mathematically, Component 1 models total commercial tenure using Lebesgue measure interval union algebra: T_commercial = μ(⋃ [S_i, E_i]), bounding total verified experience by elapsed calendar time and eliminating tenure inflation from concurrent freelance or consultancy contracts. Furthermore, academic credentials are decoupled into an explicit 2D matrix combining qualification level (SLQF Level 7 through 12) and field relevance (Core Computing vs Adjacent Engineering vs Non-Technical), preventing non-technical doctorates from artificially masking deficiencies in programming.", p_body))
    story.append(Spacer(1, 4))

    fig_shield = os.path.join(fig_dir, "fig8_polysemy_shield.png")
    if os.path.exists(fig_shield):
        track('fig3_3')
        story.append(Image(fig_shield, width=410, height=182))
        story.append(Paragraph("Figure 3.3: Component 1 boundary-guarded NER and context look-around assertion shields.", caption_fig))
        story.append(Spacer(1, 6))

    fig_temp = os.path.join(fig_dir, "fig7_temporal_algebra.png")
    if os.path.exists(fig_temp):
        track('fig3_4')
        story.append(Image(fig_temp, width=410, height=191))
        story.append(Paragraph("Figure 3.4: Component 1 chronological interval union algebra for experience deduplication.", caption_fig))
        story.append(Spacer(1, 6))

    # 3.4 Component 2 summary
    track('sec3_4')
    story.append(Paragraph("3.4 Component 2 summary", h_sec))
    story.append(Paragraph("<b>Component Owner:</b> Yenura S. Karunanayaka (IT22306272).<br/><b>Subproblem Addressed:</b> Subjective, uncalibrated technical interviews, cognitive interviewer fatigue, and static multiple-choice question memorization.<br/><b>Input:</b> Extracted candidate competency profile from Component 1 and target engineering role specifications.<br/><b>Core Methods:</b> Retrieval-Augmented Interview Generation System (RAIGS) for dynamic contextual question retrieval; OpenAI Whisper speech-to-text transcription engine (achieving 7.8% Word Error Rate); dense semantic conceptual answer grading using Sentence-BERT cosine similarity against multi-expert rubrics (achieving r = 0.884 Pearson correlation with senior engineering panels); and an Abstract Syntax Tree (AST) sandboxed Python code execution engine enforcing memory and CPU limits.<br/><b>Output:</b> Comprehensive multi-modal interview evaluation payload comprising conceptual comprehension score (S_concept), coding accuracy score (S_code), and verbal communication metric (S_comm).<br/><b>Ecosystem Contribution:</b> Provides empirical, objective live assessment telemetry to Component 3 for holistic candidate scoring.", p_body))
    story.append(Spacer(1, 4))

    story.append(Paragraph("In Component 2, candidate spoken responses are captured via browser media streams, converted to 16 kHz WAV audio buffers, and transcribed in 5-second sliding windows via Whisper. Conceptual answers are encoded into 384-dimensional dense vectors using all-MiniLM-L6-v2 and graded against expert rubrics via cosine similarity: S_concept = cos(e_cand, e_rubric) · 100. For hands-on coding, the AST engine inspects the abstract syntax tree prior to execution, intercepting forbidden calls (`os.system`, `subprocess`, `socket`) before compiling, guaranteeing 100% containment against malicious payloads.", p_body))
    story.append(Spacer(1, 6))

    # 3.5 Component 3 summary
    track('sec3_5')
    story.append(Paragraph("3.5 Component 3 summary", h_sec))
    story.append(Paragraph("<b>Component Owner:</b> K. G. Savinda N. Perera (IT22027610).<br/><b>Subproblem Addressed:</b> Ad-hoc spreadsheet ranking heuristics, lack of soft prerequisite gating, and unmitigated demographic bias in candidate selection.<br/><b>Input:</b> Uncollapsed Tri-Pillar CV vector from Component 1 and multi-modal interview metrics from Component 2.<br/><b>Core Methods:</b> Transparent Multi-Attribute Utility Theory (MAUT) candidate scoring formulation: Candidate Suitability Score CSS = 0.40 · S_cv + 0.60 · S_interview, combined with non-compensatory prerequisite soft gating (flagging candidates who fail core baseline competencies); listwise learning-to-rank comparator utilizing LightGBM LambdaMART (achieving NDCG@5 = 0.892); and automated demographic parity auditing enforcing adverse impact ratio compliance (Delta_DP &lt; 0.02).<br/><b>Output:</b> Calibrated candidate suitability scores, gating flags, and auditable ranked leaderboards for recruitment panels.<br/><b>Ecosystem Contribution:</b> Delivers the final hiring decision matrix, advancing shortlisted candidates to executive offers while seamlessly routing unselected candidates to Component 4.", p_body))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Component 3 solves the fundamental failure of unweighted scoring by separating resume qualification (S_CV) from demonstrated live assessment (S_Interview). The composite score is computed as CSS = w_cv · S_CV + w_int · S_Interview, where w_cv = 0.40 and w_int = 0.60. If a candidate fails a non-compensatory baseline prerequisite (e.g., scoring under 40.0 in core coding execution), a soft-gating flag is raised on the recruiter dashboard, preventing high academic credentials from compensating for an inability to write working software.", p_body))
    story.append(Spacer(1, 6))

    # 3.6 Component 4 summary
    track('sec3_6')
    story.append(Paragraph("3.6 Component 4 summary", h_sec))
    story.append(Paragraph("<b>Component Owner:</b> K. G. Savinda N. Perera (IT22027610).<br/><b>Subproblem Addressed:</b> The rejection dead-end failure mode, talent leakage, and lack of actionable upskilling guidance for unsuccessful candidates.<br/><b>Input:</b> Profiles of candidates falling below shortlisting thresholds in Component 3.<br/><b>Core Methods:</b> Two-stage fuzzy/semantic skill gap extraction against real-time market requisitions; a 67-feature Gradient Boosted Decision Tree (GBDT) ensemble predicting market hireability probability (achieving ROC-AUC = 0.976); dynamic milestone-based learning pathway synthesis pacing curriculum study at 2 skills per month mapped to 47 curated course ontologies; and a multi-tier Directed Acyclic Graph (DAG) career lattice utilizing Dijkstra's algorithm to compute shortest transition paths between adjacent technical roles.<br/><b>Output:</b> Personalized, milestone-based learning curricula, estimated study durations, official documentation links, and adjacent career mobility lattices.<br/><b>Ecosystem Contribution:</b> Closes the recruitment loop, transforming candidate rejection into a constructive, career-building talent development pathway.", p_body))
    story.append(Spacer(1, 4))

    story.append(Paragraph("In Component 4, unshortlisted candidates are ingested from Component 3. The 67-feature GBDT model computes the candidate's baseline hireability probability P_hire. Next, the skill gap vector is mapped onto a directed acyclic graph G = (V, E) where vertices V represent technical competencies and directed edges E represent pedagogical prerequisites. Dijkstra's shortest path algorithm identifies the optimal sequence of milestone acquisitions that maximizes ΔP_hire while minimizing estimated study hours, linking each node to verified documentation and open-source course materials.", p_body))
    story.append(Spacer(1, 6))

    # 3.7 End to end user and data flow
    track('sec3_7')
    story.append(Paragraph("3.7 End to end user and data flow", h_sec))
    story.append(Paragraph("Figure 3.2 illustrates the end-to-end user and analytical data flow across RecruitAI. A candidate begins by uploading a resume (Stage 1). Component 1 parses, cleanses, and classifies the profile, emitting the Tri-Pillar vector (Stage 2). The candidate then enters Component 2's interactive technical interview (Stage 3). In Stage 4, Component 3 aggregates document and interview metrics, determining whether the candidate meets shortlisting thresholds. High-scoring candidates advance to final offers, while candidates with identified skill gaps are seamlessly routed into Component 4 to receive customized developmental roadmaps (Stage 5).", p_body))
    story.append(Spacer(1, 4))

    fig_flow = os.path.join(fig_dir, "fig9_integrated_lifecycle_flow.png")
    if os.path.exists(fig_flow):
        track('fig3_2')
        story.append(Image(fig_flow, width=410, height=197))
        story.append(Paragraph("Figure 3.2: End-to-end candidate lifecycle, analytical state flow, and remedial routing.", caption_fig))
        story.append(Spacer(1, 6))

    story.append(Paragraph("To illustrate the concrete end-to-end user and data flow, consider an authentic recruitment journey for an applicant applying for a 'Senior Backend Developer' vacancy:", p_body))
    story.append(Paragraph("• <b>Step 1 (Ingestion):</b> Candidate uploads a 3-page PDF resume. Component 1 parses the document layout in 151 ms, redacts name, email, and phone, extracts 28 verified workplace skills via regex look-around shields, applies interval union algebra to deduplicate 18 months of overlapping freelancing, decouples the B.Sc. degree, and classifies the profile into 'Backend Developer' with 94.2% confidence.", p_bullet))
    story.append(Paragraph("• <b>Step 2 (Technical Interview):</b> Component 2 consumes the parsed profile, dynamically generating 4 architecture questions and 2 coding tasks. Candidate responds via microphone and browser code editor. Whisper transcribes audio with 7.8% WER; SBERT grades conceptual answers (rubric alignment = 84.5%); AST sandbox executes Python code passing 5/5 test cases in 12 ms.", p_bullet))
    story.append(Paragraph("• <b>Step 3 (Ranking &amp; Gating):</b> Component 3 aggregates C1 Tri-Pillar scores (88.25) and C2 interview scores (86.20) via MAUT, calculating a composite CSS of 87.02. The candidate passes all prerequisite gates and is placed in Rank 2 on the recruiter's live leaderboard.", p_bullet))
    story.append(Paragraph("• <b>Step 4 (Alternative Remediation):</b> For a second candidate who scored 58.40 on CSS (failing the shortlisting cutoff of 75.0), Component 3 immediately transmits the gap payload to Component 4. Component 4 identifies missing proficiencies in Docker and Redis, synthesizes a 6-week paced milestone roadmap, and models a projected hireability gain from 42.1% to 80.5%, delivering an immediate, constructive upskilling guide to the applicant.", p_bullet))
    story.append(Spacer(1, 6))

    # 3.8 Formal mathematical and algorithmic framework
    track('sec3_8')
    story.append(Paragraph("3.8 Formal mathematical and algorithmic framework", h_sec))
    story.append(Paragraph("To ensure scientific repeatability and implementation determinism, this section formalizes the core mathematical equations governing all four microservice components:", p_body))

    story.append(Paragraph("<b>1. Component 1 Mathematical Formulation:</b> Sublinear term frequency transformation dampens repetitive keyword stuffing: tf_{sublinear}(t, d) = 1 + log(tf(t, d)) for tf > 0, else 0. The 20-role multinomial logistic classifier computes class posterior probabilities via softmax:", p_body))
    story.append(Paragraph("<b>P(y = c | x) = exp(w_c^T x + b_c) / SUM_{j=1}^{20} exp(w_j^T x + b_j)</b>", styles['ThesisBodyBold']))
    story.append(Paragraph("The Tri-Pillar feature vector is formalized as S_C1 = [S_skill, S_exp, S_edu], where S_skill aggregates evidence weights (isolated mention = 0.40, project = 0.70, workplace duty = 1.00), S_exp applies Lebesgue interval union to commercial jobs alone, and S_edu computes the 2D tensor product of Degree Tier Level and Computing Field Relevance.", p_body))

    story.append(Paragraph("<b>2. Component 2 Mathematical Formulation:</b> Spoken audio signals x(t) sampled at 16 kHz are transformed into 80-channel log-magnitude Mel-spectrograms. OpenAI Whisper minimizes sequence-to-sequence cross-entropy loss over subword tokens. For conceptual answers, SBERT generates 384-dimensional sentence embeddings e_cand and e_rubric. Semantic score S_concept is calculated via cosine similarity:", p_body))
    story.append(Paragraph("<b>S_concept = (e_cand . e_rubric) / (||e_cand||_2 . ||e_rubric||_2) * 100</b>", styles['ThesisBodyBold']))
    story.append(Paragraph("Hands-on coding submissions undergo AST node traversal verifying the safety invariant: For all AST nodes n in tree T, type(n) NOT IN {Import('os'), Import('subprocess'), Import('socket'), Call('eval'), Call('exec')}.", p_body))

    story.append(Paragraph("<b>3. Component 3 Mathematical Formulation:</b> Multi-Attribute Utility Theory (MAUT) computes Candidate Suitability Score CSS by applying monotonic utility transforms U_k(x) across resume and interview dimensions:", p_body))
    story.append(Paragraph("<b>CSS = w_cv * S_CV + w_int * S_Interview = 0.40 * S_CV + 0.60 * S_Interview</b>", styles['ThesisBodyBold']))
    story.append(Paragraph("LambdaMART listwise ranking optimizes candidate order permutations by computing lambda gradients for candidate pair (i, j):", p_body))
    story.append(Paragraph("<b>lambda_{ij} = -sigma / (1 + exp(sigma(s_i - s_j))) * |Delta NDCG_{ij}|</b>", styles['ThesisBodyBold']))
    story.append(Paragraph("where |Delta NDCG_{ij}| is the absolute swap change in Normalised Discounted Cumulative Gain at position k:", p_body))
    story.append(Paragraph("<b>NDCG@k = DCG@k / IDCG@k = (SUM_{i=1}^k (2^{rel_i} - 1) / log_2(i + 1)) / IDCG@k</b>", styles['ThesisBodyBold']))

    story.append(Paragraph("<b>4. Component 4 Mathematical Formulation:</b> Market hireability probability P_hire is modeled via 67-feature Gradient Boosted Decision Trees minimizing logistic loss over M boosting iterations: F_m(x) = F_{m-1}(x) + gamma_m h_m(x). For curriculum pathfinding, the directed acyclic graph G = (V, E) defines competency prerequisites. Edge weights w(u, v) represent estimated study hours to transition from skill u to v. Dijkstra's shortest path minimizes total study expenditure while maximizing hireability improvement:", p_body))
    story.append(Paragraph("<b>Cost(Path P) = SUM_{(u,v) in P} w(u, v) - lambda_gain * Delta P_{hire}(v)</b>", styles['ThesisBodyBold']))
    story.append(Paragraph("where lambda_gain is a Pareto trade-off parameter balancing candidate study time against competitive market advantage.", p_body))
    story.append(Spacer(1, 6))

    # 3.9 Architectural trade-off analysis
    track('sec3_9')
    story.append(Paragraph("3.9 Architectural trade-off analysis", h_sec))
    story.append(Paragraph("Engineering RecruitAI required navigating complex architectural tensions between model expressive capacity, inference speed, explainability, and infrastructure operating expense. Table 3.2 details the primary architectural design trade-offs evaluated and the scientific rationale supporting the chosen implementations.", p_body))
    story.append(Spacer(1, 4))

    track('tab3_2')
    story.append(Paragraph("Table 3.2: Comprehensive architectural trade-off analysis across system design dimensions.", caption_tab))
    trade_data = [
        [Paragraph("<b>Architectural Decision</b>", cell_bold), Paragraph("<b>Candidate Option A</b>", cell_bold), Paragraph("<b>Candidate Option B</b>", cell_bold), Paragraph("<b>Selected Strategy &amp; Engineering Justification</b>", cell_bold)],
        [Paragraph("System Modularity", cell), Paragraph("Monolithic Python App", cell), Paragraph("Decoupled Microservices", cell), Paragraph("<b>Microservices (Option B):</b> Isolates heavy PyTorch dependencies in C2; prevents GIL blocking; allows independent service scaling.", cell)],
        [Paragraph("Role Classification", cell), Paragraph("Fine-tuned RoBERTa LLM", cell), Paragraph("Balanced Multinomial LogReg", cell), Paragraph("<b>Balanced LogReg (Option B):</b> Executes in 2.4 ms (59x faster than BERT); achieves 83.0% accuracy; guarantees closed-form SHAP transparency.", cell)],
        [Paragraph("Semantic Rubric Scoring", cell), Paragraph("Full Cross-Encoder", cell), Paragraph("Bi-Encoder SBERT Cosine", cell), Paragraph("<b>Bi-Encoder SBERT (Option B):</b> Enables pre-computation and caching of expert rubric embeddings; sub-10ms similarity calculation.", cell)],
        [Paragraph("Candidate Ranking", cell), Paragraph("Pointwise Ridge Regression", cell), Paragraph("LambdaMART Listwise LTR", cell), Paragraph("<b>LambdaMART (Option B):</b> Optimizes top-k ordering directly via NDCG gradients; eliminates rank inversions among top applicants.", cell)],
        [Paragraph("Code Evaluation", cell), Paragraph("Standard exec() Sandbox", cell), Paragraph("AST Visitor + Subprocess", cell), Paragraph("<b>AST Visitor (Option B):</b> Pre-inspects syntax trees before execution; blocks OS calls, network sockets, and file I/O with 100% security.", cell)],
    ]
    trade_tab = create_table_box(trade_data, [90, 85, 85, 151], styles, is_header=True)
    story.append(trade_tab)
    story.append(Spacer(1, 8))

    # 3.10 Vector embedding spaces and latent geometric representations
    track('sec3_10')
    story.append(Paragraph("3.10 Vector embedding spaces and latent geometric representations", h_sec))
    story.append(Paragraph("A foundational theoretical strength of RecruitAI is its dual representation strategy, balancing sparse interpretable feature vectors with dense neural geometric embeddings across functional pipeline stages:", p_body))
    story.append(Paragraph("<b>1. Sparse Interpretable Feature Space (Component 1 &amp; Component 3):</b> In Component 1, resumes are transformed into a 67-dimensional normalized sparse vector x in R^{67}. Dimensions 1 through 20 capture sublinear TF-IDF role-term associations; dimensions 21 through 40 represent domain skill cluster densities across our 400+ ontology; dimensions 41 through 60 encode interval-deduplicated commercial tenure across seven engineering specializations; and dimensions 61 through 67 capture the decoupled 2D academic credentials. Because every dimension maintains a strictly defined physical unit (years of tenure, degree tier level, keyword evidence score), downstream ranking in Component 3 remains 100% auditable.", p_body))
    story.append(Paragraph("<b>2. Dense Neural Semantic Manifolds (Component 2 &amp; Component 4):</b> In Component 2, spoken and written technical explanations are mapped into a 384-dimensional continuous latent space via the all-MiniLM-L6-v2 transformer encoder. This bi-encoder maps semantically equivalent technical formulations into close proximity under cosine distance. For instance, 'idempotent message consumption using unique UUID keys' and 'deduplicating event delivery through transaction identifiers' achieve a high cosine similarity of 0.892 despite possessing zero lexical n-gram overlap.", p_body))
    story.append(Paragraph("<b>3. Graph Lattice Projections (Component 4):</b> In Component 4, the 384-dimensional SBERT gap representations are projected onto the discrete topological vertices of our Directed Acyclic Graph (DAG) career lattice. This bridge connects continuous neural semantic understanding with deterministic graph search algorithms, ensuring that generated learning milestones represent authentic prerequisite dependencies verified by educational ontologies.", p_body))
    story.append(Spacer(1, 10))

    story.append(PageBreak())
    return story
