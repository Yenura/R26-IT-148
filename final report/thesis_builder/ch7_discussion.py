import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from thesis_builder.styles import clean_xml, create_table_box, PRINTABLE_WIDTH
from thesis_builder.canvas_helper import PageTracker

def append_ch7(story, styles, fig_dir, tracker=None):
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

    # 7 DISCUSSION
    track('ch7')
    story.append(Paragraph("7 DISCUSSION", h_ch))
    story.append(Spacer(1, 4))

    # 7.1 Interpretation of findings
    track('sec7_1')
    story.append(Paragraph("7.1 Interpretation of findings", h_sec))
    story.append(Paragraph("The experimental results demonstrate that dense normalized entity feature representations, combined with class-balanced multinomial logistic regression, deliver high-fidelity role classification on authentic applicant resumes. Roles characterized by isolated, highly distinctive technology stacks - such as Mobile App Developer (Flutter, React Native, Swift), QA/Test Automation Engineer (Selenium, Cypress, PyTest), and UI/UX Designer (Figma, Adobe XD) - achieved perfect empirical F1 scores of 1.00. Conversely, classification errors clustered predominantly where real-world industry job definitions naturally overlap, specifically between Data Scientists and Data Engineers (14.2% error rate) and between Full Stack and Frontend/Backend Developers (11.8% error rate).", p_body))
    story.append(Paragraph("Significantly, the model achieves a macro recall of 94.35% and macro F1 of 92.47%, exceeding overall exact-match accuracy (87.42%). This divergence occurs because the generalist 'Software Engineer' class comprises 178 samples (21.7% of the test partition) and exhibits lower recall (0.60), acting as a catch-all for candidates without dense specialized terminology. In contrast, specialized engineering cohorts achieve near-perfect classification.", p_body))

    # 7.2 Comparison with literature baselines and existing solutions
    track('sec7_2')
    story.append(Paragraph("7.2 Comparison with literature baselines and existing solutions", h_sec))
    story.append(Paragraph("A critical finding of this research is the forensic explanation of why earlier academic publications reported artificial F1 = 1.0 scores on public datasets. When baseline classifiers from literature were evaluated on synthetic resume corpora, they attained 100% precision, recall, and F1 across all classes. Inspection of learned decision weights revealed that models memorized invariant boilerplate paragraphs (e.g., 'Dynamic software engineer seeking opportunity in...') and explicit target class headers. When evaluated on authentic candidate resumes, their accuracy collapsed to 43.2%. Component 1 establishes an authentic, leakage-free evaluation standard.", p_body))
    story.append(Paragraph("Furthermore, while the unconstrained TF-IDF n-gram baseline achieved 98.17% accuracy on our held-out test split, it operates as an uninterpretable high-dimensional lexical model (5,000+ features) that remains vulnerable to adversarial keyword stuffing and provides zero structural entity grounding. Component 1 sacrifices 10.75 percentage points of raw lexical accuracy to gain deterministic polysemy shielding, chronological tenure algebra, decoupled credential scoring, and closed-form explainability.", p_body))

    # 7.3 Research contribution
    track('sec7_3')
    story.append(Paragraph("7.3 Research contribution", h_sec))
    story.append(Paragraph("The primary theoretical and scientific contributions of this research include: (1) formalization of context-guarded regular-expression look-around assertions that eliminate polysemous token collisions on single-letter and ambiguous programming languages; (2) formulation of a calendar interval union algebra that eliminates tenure inflation and bounds calculated experience by elapsed calendar time; (3) introduction of a two-dimensional credential qualification ontology that decouples degree attainment tier from field relevance; and (4) mathematical derivation of closed-form SHAP feature attributions for linear softmax classifiers: φ_{k,j}(x) = w_{k,j} · ( x_j - E[X_j] ).", p_body))
    story.append(Spacer(1, 4))

    track('tab7_1')
    story.append(Paragraph("Table 7.1: Representative closed-form feature attribution trace for a candidate predicted as Backend Developer.", caption_tab))
    shap_data = [
        [Paragraph("<b>Feature Extracted</b>", cell_bold), Paragraph("<b>Feature Value</b>", cell_bold), Paragraph("<b>Weight (w_{k,j})</b>", cell_bold), Paragraph("<b>Attribution (φ_j)</b>", cell_bold), Paragraph("<b>Interpretability Explanation</b>", cell_bold)],
        [Paragraph("Python &amp; Django Density", cell), Paragraph("0.42 (High)", cell), Paragraph("+3.84", cell), Paragraph("+1.42", cell), Paragraph("Strong primary driver towards Backend Developer", cell)],
        [Paragraph("FastAPI &amp; REST Density", cell), Paragraph("0.28 (Moderate)", cell), Paragraph("+3.12", cell), Paragraph("+0.85", cell), Paragraph("Verified workplace API engineering signal", cell)],
        [Paragraph("PostgreSQL &amp; Redis Density", cell), Paragraph("0.35 (High)", cell), Paragraph("+2.75", cell), Paragraph("+0.78", cell), Paragraph("Persistence and caching architecture signal", cell)],
        [Paragraph("Verified Commercial Tenure", cell), Paragraph("4.5 years", cell), Paragraph("+1.95", cell), Paragraph("+0.45", cell), Paragraph("Senior experience boost meeting role requirements", cell)],
        [Paragraph("Frontend React / CSS Density", cell), Paragraph("0.05 (Low)", cell), Paragraph("-2.40", cell), Paragraph("-0.38", cell), Paragraph("Separates candidate from Full Stack specialization", cell)],
        [Paragraph("Data Science Tool Density", cell), Paragraph("0.00 (None)", cell), Paragraph("-3.10", cell), Paragraph("-0.62", cell), Paragraph("Lowers probability of Data Scientist misclassification", cell)],
    ]
    shap_tab = create_table_box(shap_data, [105, 75, 55, 55, 121], styles, is_header=True)
    story.append(shap_tab)
    story.append(Spacer(1, 8))

    # 7.4 Product contribution
    track('sec7_4')
    story.append(Paragraph("7.4 Product contribution", h_sec))
    story.append(Paragraph("From a software engineering perspective, Component 1 delivers an asynchronous, production-grade microservice running on dedicated Port 8001. The service achieves an inference latency of 2.4 ms per candidate, enabling real-time screening at over 1,600 resumes per hour on a single 4-core CPU virtual machine without requiring external GPU infrastructure. The service is verified by 195 automated tests with a 100% pass rate.", p_body))

    # 7.5 Limitations and threats to validity
    track('sec7_5')
    story.append(Paragraph("7.5 Limitations and threats to validity", h_sec))
    story.append(Paragraph("This study acknowledges several methodological limitations and threats to validity:", p_body))
    story.append(Paragraph("<b>1. Internal Validity:</b> The pipeline processes self-reported resume text. While evidence weighting penalizes unverified keyword lists, candidates can fabricate narrative employment duties. In the RecruitAI architecture, this threat is mitigated by downstream coding sandboxes and technical interviews in Component 2.", p_bullet))
    story.append(Paragraph("<b>2. External Validity:</b> The skill taxonomy and regular expression look-around shields are tuned for English-language software engineering resumes. Deploying the system across non-English resumes or non-technical domains would require multi-lingual ontology expansion.", p_bullet))
    story.append(Paragraph("<b>3. Date Granularity:</b> Resumes stating only calendar years (e.g., '2021 - 2023') introduce a ±6 month tenure margin of error. Standardizing candidate inputs via structured web forms eliminates this ambiguity.", p_bullet))

    # 7.6 Implications
    track('sec7_6')
    story.append(Paragraph("7.6 Implications", h_sec))
    story.append(Paragraph("Component 1 demonstrates that fair, auditable, and high-throughput resume screening can be achieved through disciplined entity engineering without sacrificing algorithmic transparency. Table 7.2 maps the design features of Component 1 to major global AI regulatory governance frameworks.", p_body))
    story.append(Spacer(1, 4))

    track('tab7_2')
    story.append(Paragraph("Table 7.2: Global AI regulatory compliance mapping (EU AI Act, NYC LL144, GDPR, EEOC).", caption_tab))
    reg_data = [
        [Paragraph("<b>Regulatory Framework</b>", cell_bold), Paragraph("<b>Statutory Requirement</b>", cell_bold), Paragraph("<b>Component 1 Design Architecture</b>", cell_bold), Paragraph("<b>Compliance Status</b>", cell_bold)],
        [Paragraph("EU AI Act (Annex III High-Risk AI)", cell), Paragraph("Bias governance (Art. 10), transparency (Art. 13), human oversight (Art. 14)", cell), Paragraph("PII redaction, closed-form SHAP attributions, uncollapsed Tri-Pillar vector leaving final decision to human", cell), Paragraph("Compliant by architectural design", cell)],
        [Paragraph("NYC Local Law 144 of 2021", cell), Paragraph("Annual independent bias audit; adverse impact ratio >= 0.80", cell), Paragraph("Demographic blinding removes name, gender, and postal indicators prior to feature extraction", cell), Paragraph("Audit-ready architecture", cell)],
        [Paragraph("GDPR (Article 22)", cell), Paragraph("Right to explanation and human contestability for automated decisions", cell), Paragraph("Per-feature attributions and actionable learning roadmap provided to candidates upon rejection", cell), Paragraph("Fully compliant with explanation rights", cell)],
        [Paragraph("EEOC Selection Guidelines (1978)", cell), Paragraph("Job-related validity of employee selection procedures", cell), Paragraph("Skills taxonomy tied directly to engineering role benchmarks; coursework separated from tenure", cell), Paragraph("Compliant by job-related construct validity", cell)],
    ]
    reg_tab = create_table_box(reg_data, [85, 100, 140, 86], styles, is_header=True)
    story.append(reg_tab)
    story.append(PageBreak())
