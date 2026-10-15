import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from thesis_builder.styles import clean_xml, create_table_box, create_code_box, PRINTABLE_WIDTH
from thesis_builder.canvas_helper import PageTracker

def append_ch3(story, styles, fig_dir, tracker=None):
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

    def track(key):
        if tracker is not None:
            story.append(PageTracker(key, tracker))

    # 3 RESEARCH METHODOLOGY
    track('ch3')
    story.append(Paragraph("3 RESEARCH METHODOLOGY", h_ch))
    story.append(Spacer(1, 4))

    # 3.1 Research design
    track('sec3_1')
    story.append(Paragraph("3.1 Research design", h_sec))
    story.append(Paragraph("This research follows the Design Science Research (DSR) paradigm formulated by Hevner et al. (2004) for information systems engineering. The methodology comprises six iterative phases: (1) <i>Problem Formulation:</i> Identifying empirical ATS failure modes through industrial recruitment audits; (2) <i>Data Corpus Curation &amp; Leakage Audit:</i> Assembling an authentic 4,000-CV corpus and auditing synthetic benchmark vulnerabilities; (3) <i>Algorithmic Modeling:</i> Mathematically formalizing boundary-guarded NER, interval union temporal algebra, and two-dimensional credential scoring; (4) <i>Model Training &amp; Hyperparameter Tuning:</i> Training a balanced multinomial logistic regression classifier using sublinear TF-IDF and dense feature spaces; (5) <i>Comparative Benchmarking &amp; Ablation:</i> Evaluating the proposed model against Naive Bayes, Random Forests, Linear SVM, and fine-tuned DistilBERT; and (6) <i>Microservice Engineering &amp; Verification:</i> Packaging the pipeline as an asynchronous FastAPI service on Port 8001 validated by 195 automated tests.", p_body))

    # 3.2 Data participants or study materials
    track('sec3_2')
    story.append(Paragraph("3.2 Data participants or study materials", h_sec))
    story.append(Paragraph("To eliminate the synthetic template memorization flaws prevalent in prior literature, an authentic corpus of 4,000 professional technical resumes was assembled from public technology employment repositories, open-source software developer profiles, and verified engineering career portals. The corpus encompasses 20 canonical information technology roles, spanning a wide diversity of document layouts (single-column, multi-column, tabular), typography, career trajectories, and multinational educational systems.", p_body))
    story.append(Paragraph("The corpus was partitioned using stratified sampling into a training partition of 3,276 resumes (80%) and a strictly held-out independent test partition of 819 resumes (20%). Each role class in the test set contains between 30 and 178 samples, reflecting real-world engineering labor market distributions (e.g., higher volume for General Software Engineers and Frontend Developers, specialized cohorts for Site Reliability and Blockchain Developers).", p_body))

    # 3.3 Experimental or study procedure
    track('sec3_3')
    story.append(Paragraph("3.3 Experimental or study procedure", h_sec))
    story.append(Paragraph("Model training and validation were executed under rigorous statistical protocols. A 5-fold stratified cross-validation was conducted exclusively across the 3,276 training resumes to evaluate model stability and prevent data snooping. Hyperparameter optimization was conducted via grid search over regularization strength C in {0.01, 0.1, 1.0, 10.0}, penalty norms (L1, L2, ElasticNet), and optimization solvers (lbfgs, saga). The final selected hyperparameters (C = 1.0, L2 penalty, lbfgs solver, balanced class weights) were subsequently evaluated once on the unseen 819 held-out test partition.", p_body))
    story.append(Paragraph("Each candidate resume is represented by a dense 67-dimensional normalized feature vector extracted across six analytical domains. Table 3.1 details the dense feature specification.", p_body))
    story.append(Spacer(1, 4))

    track('tab3_1')
    story.append(Paragraph("Table 3.1: Dense 67-dimensional feature vector specification for multi-class role classification.", caption_tab))
    feat_data = [
        [Paragraph("<b>Feature Indices</b>", cell_bold), Paragraph("<b>Category</b>", cell_bold), Paragraph("<b>Count</b>", cell_bold), Paragraph("<b>Mathematical Encoding &amp; Normalization</b>", cell_bold)],
        [Paragraph("0-19", cell), Paragraph("Domain Skill Densities", cell), Paragraph("20", cell), Paragraph("Skill counts per IT domain divided by total skills: d_k = n_k / max(1, N_skills)", cell)],
        [Paragraph("20-39", cell), Paragraph("Domain Lexicon Salience", cell), Paragraph("20", cell), Paragraph("Overlap ratio with required canonical skills for each role: o_k in [0, 1]", cell)],
        [Paragraph("40-44", cell), Paragraph("Experience Seniority", cell), Paragraph("5", cell), Paragraph("E_tot, E_it, E_rel scaled by min(T / 10, 1.0), plus senior (&gt;=5y) and mid (&gt;=2y) flags", cell)],
        [Paragraph("45-49", cell), Paragraph("Educational Attainment", cell), Paragraph("5", cell), Paragraph("L_deg in [0, 1], M_field in [0.2, 1.0], honors flag, accredited flag, S_edu normalized", cell)],
        [Paragraph("50-54", cell), Paragraph("Certifications", cell), Paragraph("5", cell), Paragraph("Count scaled by min(C / 5, 1.0), plus AWS, security, PMP/Agile, GCP flags", cell)],
        [Paragraph("55-66", cell), Paragraph("Syntactic &amp; Layout Metrics", cell), Paragraph("12", cell), Paragraph("Word count, action-verb density, bullet ratio, section completeness flags", cell)],
    ]
    feat_tab = create_table_box(feat_data, [65, 95, 40, 211], styles, is_header=True)
    story.append(feat_tab)
    story.append(Spacer(1, 6))

    # 3.4 Measures and evaluation metrics
    track('sec3_4')
    story.append(Paragraph("3.4 Measures and evaluation metrics", h_sec))
    story.append(Paragraph("To evaluate classification efficacy across imbalanced role distributions, both micro-averaged and macro-averaged metrics were calculated. Let TP_k, FP_k, and FN_k denote true positives, false positives, and false negatives for class k in {1, ..., K} (K = 20):", p_body))
    story.append(Paragraph("<b>Precision_macro = (1 / K) Σ_{k=1..K} [ TP_k / (TP_k + FP_k) ]</b>", p_body_bold))
    story.append(Paragraph("<b>Recall_macro = (1 / K) Σ_{k=1..K} [ TP_k / (TP_k + FN_k) ]</b>", p_body_bold))
    story.append(Paragraph("<b>Macro F1 = (1 / K) Σ_{k=1..K} [ 2 · Precision_k · Recall_k / (Precision_k + Recall_k) ]</b>", p_body_bold))
    story.append(Paragraph("In addition, pipeline performance was evaluated via wall-clock inference latency per candidate (ms) and cross-entropy loss under L2 penalty.", p_body))

    # Figure 3.1 Polysemy Shield
    fig_shield = os.path.join(fig_dir, "fig8_polysemy_shield.png")
    if os.path.exists(fig_shield):
        track('fig3_1')
        story.append(Spacer(1, 4))
        story.append(Image(fig_shield, width=410, height=182))
        story.append(Paragraph("Figure 3.1: Context-guarded regex look-around shielding vs. naive substring tokenizers.", caption_fig))
        story.append(Spacer(1, 6))

    # Figure 3.2 Temporal Algebra
    fig_temp = os.path.join(fig_dir, "fig7_temporal_algebra.png")
    if os.path.exists(fig_temp):
        track('fig3_2')
        story.append(Spacer(1, 4))
        story.append(Image(fig_temp, width=410, height=191))
        story.append(Paragraph("Figure 3.2: Temporal experience disambiguation: concurrent employment interval union.", caption_fig))
        story.append(Spacer(1, 6))

    # 3.5 Data analysis
    track('sec3_5')
    story.append(Paragraph("3.5 Data analysis", h_sec))
    story.append(Paragraph("Because the primary role classifier is a linear multinomial model followed by a softmax function, feature attributions can be computed in closed form without Monte Carlo sampling approximations (Lundberg &amp; Lee, 2017). For a candidate feature vector x and predicted class k, the exact attribution of feature j to log-odds is:", p_body))
    story.append(Paragraph("<b>φ_{k,j}(x) = w_{k,j} · ( x_j - E[X_j] )</b>", p_body_bold))
    story.append(Paragraph("where w_{k,j} represents the learned weight vector for class k, and E[X_j] is the empirical training expectation of feature j. This closed-form formulation delivers instantaneous, auditable explanations showing exactly which technical skills, experience metrics, or certifications pushed the role classification decision.", p_body))

    # 3.6 Ethics privacy security and responsible AI
    track('sec3_6')
    story.append(Paragraph("3.6 Ethics privacy security and responsible AI", h_sec))
    story.append(Paragraph("To enforce algorithmic fairness and mitigate demographic discrimination (gender, racial, ethnic, age, and geographical biases), Component 1 executes strict Personally Identifiable Information (PII) blinding at the ingestion boundary. Names, email addresses, phone numbers, postal addresses, and personal profile URLs are stripped before feature extraction, ensuring the classifier operates solely on validated competency and experience signals.", p_body))
    story.append(Paragraph("This architecture directly aligns with the transparency, data governance, and human oversight requirements of the European Union AI Act (Regulation EU 2024/1689, Annex III for high-risk employment systems), New York City Local Law 144 of 2021 (auditing automated employment decision tools), EEOC Uniform Guidelines on Employee Selection Procedures (1978), and GDPR Article 22 provisions for human review of automated decisions.", p_body))

    # 3.7 Reproducibility and research artefacts
    track('sec3_7')
    story.append(Paragraph("3.7 Reproducibility and research artefacts", h_sec))
    story.append(Paragraph("To ensure complete scientific reproducibility, all machine learning pipelines, preprocessing scripts, taxonomy dictionaries, and trained model weights were versioned and containerized using Docker under Python 3.12. Model weights are serialized in standard binary pickle format alongside JSON schema metadata. The service requires no external GPU, executing on standard x86 CPU hardware. An automated Pytest verification suite comprising 195 test assertions was executed to validate deterministic reproducibility across independent runtime environments.", p_body))
    story.append(PageBreak())
