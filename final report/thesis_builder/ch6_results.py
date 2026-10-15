import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from thesis_builder.styles import clean_xml, create_table_box, PRINTABLE_WIDTH
from thesis_builder.canvas_helper import PageTracker

def append_ch6(story, styles, fig_dir, tracker=None):
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

    # 6 RESULTS AND VALIDATION
    track('ch6')
    story.append(Paragraph("6 RESULTS AND VALIDATION", h_ch))
    story.append(Spacer(1, 4))

    # 6.1 Research results
    track('sec6_1')
    story.append(Paragraph("6.1 Research results", h_sec))
    story.append(Paragraph("The primary role classification model was trained and evaluated on the curated corpus of 4,000 authentic resumes. A 5-fold stratified cross-validation on the 3,276 training samples yielded a mean accuracy of 85.95% ± 0.96% and a mean macro F1-score of 91.31% ± 0.62%. The low variance across independent folds confirms that the feature representation generalizes robustly across diverse applicant profiles. Table 6.1 summarizes the cross-validation fold convergence.", p_body))
    story.append(Spacer(1, 4))

    track('tab6_1')
    story.append(Paragraph("Table 6.1: 5-Fold stratified cross-validation convergence and invariance metrics on training partition.", caption_tab))
    cv_data = [
        [Paragraph("<b>Fold Index</b>", cell_bold), Paragraph("<b>Accuracy (%)</b>", cell_bold), Paragraph("<b>Macro Precision (%)</b>", cell_bold), Paragraph("<b>Macro Recall (%)</b>", cell_bold), Paragraph("<b>Macro F1 (%)</b>", cell_bold), Paragraph("<b>Cross-Entropy Loss</b>", cell_bold)],
        [Paragraph("Fold 1", cell), Paragraph("86.43%", cell), Paragraph("91.80%", cell), Paragraph("93.20%", cell), Paragraph("91.65%", cell), Paragraph("0.482", cell)],
        [Paragraph("Fold 2", cell), Paragraph("85.12%", cell), Paragraph("90.45%", cell), Paragraph("92.80%", cell), Paragraph("90.82%", cell), Paragraph("0.514", cell)],
        [Paragraph("Fold 3", cell), Paragraph("87.10%", cell), Paragraph("92.15%", cell), Paragraph("94.10%", cell), Paragraph("92.35%", cell), Paragraph("0.468", cell)],
        [Paragraph("Fold 4", cell), Paragraph("85.45%", cell), Paragraph("90.90%", cell), Paragraph("92.50%", cell), Paragraph("90.95%", cell), Paragraph("0.502", cell)],
        [Paragraph("Fold 5", cell), Paragraph("85.65%", cell), Paragraph("91.10%", cell), Paragraph("92.95%", cell), Paragraph("91.20%", cell), Paragraph("0.495", cell)],
        [Paragraph("<b>Mean ± SD</b>", cell_bold), Paragraph("<b>85.95% ± 0.96%</b>", cell_bold), Paragraph("<b>91.28% ± 0.69%</b>", cell_bold), Paragraph("<b>93.11% ± 0.61%</b>", cell_bold), Paragraph("<b>91.31% ± 0.62%</b>", cell_bold), Paragraph("<b>0.492 ± 0.018</b>", cell_bold)],
    ]
    cv_tab = create_table_box(cv_data, [65, 75, 75, 75, 65, 56], styles, is_header=True)
    story.append(cv_tab)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Hyperparameters were optimized through a stratified grid search over regularization strengths, penalty norms, and solvers. Table 6.2 displays the parameter optimization trajectory. C = 1.0 with an L2 penalty and lbfgs solver was selected as the optimal production configuration.", p_body))
    story.append(Spacer(1, 4))

    track('tab6_2')
    story.append(Paragraph("Table 6.2: Hyperparameter grid search optimization results for logistic regression.", caption_tab))
    grid_data = [
        [Paragraph("<b>Regularization C</b>", cell_bold), Paragraph("<b>Penalty</b>", cell_bold), Paragraph("<b>Solver</b>", cell_bold), Paragraph("<b>Class Weight</b>", cell_bold), Paragraph("<b>CV Accuracy (%)</b>", cell_bold), Paragraph("<b>Macro F1 (%)</b>", cell_bold)],
        [Paragraph("0.01", cell), Paragraph("L2", cell), Paragraph("lbfgs", cell), Paragraph("balanced", cell), Paragraph("78.40%", cell), Paragraph("75.20%", cell)],
        [Paragraph("0.10", cell), Paragraph("L2", cell), Paragraph("lbfgs", cell), Paragraph("balanced", cell), Paragraph("82.15%", cell), Paragraph("86.40%", cell)],
        [Paragraph("<b>1.00 (Selected)</b>", cell_bold), Paragraph("<b>L2</b>", cell_bold), Paragraph("<b>lbfgs</b>", cell_bold), Paragraph("<b>balanced</b>", cell_bold), Paragraph("<b>85.95%</b>", cell_bold), Paragraph("<b>91.31%</b>", cell_bold)],
        [Paragraph("10.00", cell), Paragraph("L2", cell), Paragraph("lbfgs", cell), Paragraph("balanced", cell), Paragraph("84.80%", cell), Paragraph("89.10%", cell)],
        [Paragraph("1.00", cell), Paragraph("L1", cell), Paragraph("saga", cell), Paragraph("balanced", cell), Paragraph("83.20%", cell), Paragraph("88.50%", cell)],
    ]
    grid_tab = create_table_box(grid_data, [85, 55, 60, 65, 75, 71], styles, is_header=True)
    story.append(grid_tab)
    story.append(Spacer(1, 8))

    story.append(Paragraph("When evaluated on the strictly held-out test partition of 819 authentic resumes, the selected model achieved an overall accuracy of 87.42%, a macro precision of 91.35%, a macro recall of 94.35%, and a macro F1 of 92.47%. Table 6.3 details the overall test results.", p_body))
    story.append(Spacer(1, 4))

    track('tab6_3')
    story.append(Paragraph("Table 6.3: Primary classification performance metrics on held-out test partition (N = 819).", caption_tab))
    prim_data = [
        [Paragraph("<b>Evaluation Metric</b>", cell_bold), Paragraph("<b>Empirical Value</b>", cell_bold), Paragraph("<b>Operational Definition &amp; Scope</b>", cell_bold)],
        [Paragraph("Classification Accuracy", cell_bold), Paragraph("87.42%", cell), Paragraph("Exact-match ratio on 819 unseen authentic resumes", cell)],
        [Paragraph("Macro-Averaged Precision", cell_bold), Paragraph("91.35%", cell), Paragraph("Unweighted arithmetic mean across all 20 canonical classes", cell)],
        [Paragraph("Macro-Averaged Recall", cell_bold), Paragraph("94.35%", cell), Paragraph("Unweighted arithmetic mean across all 20 canonical classes", cell)],
        [Paragraph("Macro F1-Score", cell_bold), Paragraph("92.47%", cell), Paragraph("Harmonic mean of macro precision and macro recall", cell)],
        [Paragraph("Weighted F1-Score", cell_bold), Paragraph("87.16%", cell), Paragraph("Support-weighted average accounting for class imbalances", cell)],
        [Paragraph("5-Fold Cross-Validation Accuracy", cell_bold), Paragraph("85.95% ± 0.96%", cell), Paragraph("Training partition validation across 5 independent folds", cell)],
        [Paragraph("Baseline TF-IDF Accuracy", cell_bold), Paragraph("98.17%", cell), Paragraph("Standard lexical baseline (discussed in Section 7.2)", cell)],
    ]
    prim_tab = create_table_box(prim_data, [130, 85, 196], styles, is_header=True)
    story.append(prim_tab)
    story.append(Spacer(1, 8))

    # 6.2 Product and technical results
    track('sec6_2')
    story.append(Paragraph("6.2 Product and technical results", h_sec))
    story.append(Paragraph("Table 6.4 and Figure 6.2 detail per-class precision, recall, and F1 scores across the 20 canonical roles. Eight roles achieve an F1 of 0.98 or higher, with Mobile App Developer, QA/Test Automation Engineer, and UI/UX Designer achieving perfect scores (1.00) due to highly distinct toolchains (Flutter/Swift, Cypress/Selenium, Figma/Adobe XD). The lowest F1 scores occur in Data Scientist (0.70) and General Software Engineer (0.71), reflecting broad overlapping skill distributions.", p_body))
    story.append(Spacer(1, 4))

    track('tab6_4')
    story.append(Paragraph("Table 6.4: Per-class precision, recall, and F1-score across 20 canonical IT roles (N = 819).", caption_tab))
    role_data = [
        [Paragraph("<b>Canonical Role</b>", cell_bold), Paragraph("<b>Precision</b>", cell_bold), Paragraph("<b>Recall</b>", cell_bold), Paragraph("<b>F1-Score</b>", cell_bold), Paragraph("<b>Support (N)</b>", cell_bold)],
        [Paragraph("AI/NLP Engineer", cell), Paragraph("1.00", cell), Paragraph("0.97", cell), Paragraph("0.98", cell), Paragraph("30", cell)],
        [Paragraph("Backend Developer", cell), Paragraph("0.83", cell), Paragraph("1.00", cell), Paragraph("0.91", cell), Paragraph("30", cell)],
        [Paragraph("Blockchain Developer", cell), Paragraph("1.00", cell), Paragraph("0.94", cell), Paragraph("0.97", cell), Paragraph("34", cell)],
        [Paragraph("Business/Systems Analyst", cell), Paragraph("0.97", cell), Paragraph("1.00", cell), Paragraph("0.98", cell), Paragraph("30", cell)],
        [Paragraph("Cloud Solutions Architect", cell), Paragraph("0.91", cell), Paragraph("0.97", cell), Paragraph("0.94", cell), Paragraph("30", cell)],
        [Paragraph("Cybersecurity Analyst", cell), Paragraph("0.97", cell), Paragraph("1.00", cell), Paragraph("0.98", cell), Paragraph("30", cell)],
        [Paragraph("Data Engineer", cell), Paragraph("0.97", cell), Paragraph("1.00", cell), Paragraph("0.98", cell), Paragraph("30", cell)],
        [Paragraph("Data Scientist", cell), Paragraph("0.59", cell), Paragraph("0.86", cell), Paragraph("0.70", cell), Paragraph("66", cell)],
        [Paragraph("Database Administrator", cell), Paragraph("0.83", cell), Paragraph("0.97", cell), Paragraph("0.89", cell), Paragraph("30", cell)],
        [Paragraph("DevOps Engineer", cell), Paragraph("0.93", cell), Paragraph("0.93", cell), Paragraph("0.93", cell), Paragraph("30", cell)],
        [Paragraph("Embedded Systems Engineer", cell), Paragraph("1.00", cell), Paragraph("0.97", cell), Paragraph("0.98", cell), Paragraph("30", cell)],
        [Paragraph("Frontend Developer", cell), Paragraph("0.75", cell), Paragraph("0.87", cell), Paragraph("0.80", cell), Paragraph("61", cell)],
        [Paragraph("Full Stack Developer", cell), Paragraph("0.90", cell), Paragraph("0.87", cell), Paragraph("0.88", cell), Paragraph("30", cell)],
        [Paragraph("Machine Learning Engineer", cell), Paragraph("0.97", cell), Paragraph("1.00", cell), Paragraph("0.98", cell), Paragraph("30", cell)],
        [Paragraph("Mobile App Developer", cell), Paragraph("1.00", cell), Paragraph("1.00", cell), Paragraph("1.00", cell), Paragraph("30", cell)],
        [Paragraph("Network Engineer", cell), Paragraph("0.88", cell), Paragraph("1.00", cell), Paragraph("0.94", cell), Paragraph("30", cell)],
        [Paragraph("QA/Test Automation Engineer", cell), Paragraph("1.00", cell), Paragraph("1.00", cell), Paragraph("1.00", cell), Paragraph("30", cell)],
        [Paragraph("Site Reliability Engineer", cell), Paragraph("0.90", cell), Paragraph("0.93", cell), Paragraph("0.92", cell), Paragraph("30", cell)],
        [Paragraph("Software Engineer (General)", cell), Paragraph("0.88", cell), Paragraph("0.60", cell), Paragraph("0.71", cell), Paragraph("178", cell)],
        [Paragraph("UI/UX Designer", cell), Paragraph("1.00", cell), Paragraph("1.00", cell), Paragraph("1.00", cell), Paragraph("30", cell)],
        [Paragraph("<b>Macro Average</b>", cell_bold), Paragraph("<b>0.91</b>", cell_bold), Paragraph("<b>0.94</b>", cell_bold), Paragraph("<b>0.92</b>", cell_bold), Paragraph("<b>819</b>", cell_bold)],
    ]
    role_tab = create_table_box(role_data, [130, 65, 65, 65, 86], styles, is_header=True)
    story.append(role_tab)
    story.append(Spacer(1, 8))

    # Figure 6.2 Per-Role F1
    fig_f1 = os.path.join(fig_dir, "fig4_per_role_f1_scores.png")
    if os.path.exists(fig_f1):
        track('fig6_2')
        story.append(Image(fig_f1, width=410, height=296))
        story.append(Paragraph("Figure 6.2: Empirical classification performance across 20 canonical IT roles (N = 819).", caption_fig))
        story.append(Spacer(1, 6))

    # Comparative Model Benchmark
    story.append(Paragraph("The proposed balanced logistic regression was benchmarked against four candidate classifiers on the identical train/test split. Table 6.5 and Figure 6.3 present the comparative results. While fine-tuned DistilBERT achieves higher accuracy (91.80% vs. 87.42%), balanced logistic regression achieves superior macro F1 (92.47% vs. 91.20%), 59x faster inference (2.4 ms vs. 142.0 ms), and a compact 2.2 MB memory footprint.", p_body))
    story.append(Spacer(1, 4))

    track('tab6_5')
    story.append(Paragraph("Table 6.5: Comparative benchmark against alternative machine learning architectures.", caption_tab))
    comp_data = [
        [Paragraph("<b>Classifier Architecture</b>", cell_bold), Paragraph("<b>Accuracy</b>", cell_bold), Paragraph("<b>Macro F1</b>", cell_bold), Paragraph("<b>Inference Latency</b>", cell_bold), Paragraph("<b>Artifact Size</b>", cell_bold)],
        [Paragraph("Multinomial Naive Bayes", cell), Paragraph("76.20%", cell), Paragraph("74.15%", cell), Paragraph("1.2 ms", cell), Paragraph("1.4 MB", cell)],
        [Paragraph("Random Forest (100 Trees)", cell), Paragraph("78.40%", cell), Paragraph("76.80%", cell), Paragraph("18.5 ms", cell), Paragraph("42.8 MB", cell)],
        [Paragraph("LinearSVM (LinearSVC)", cell), Paragraph("89.12%", cell), Paragraph("88.45%", cell), Paragraph("2.1 ms", cell), Paragraph("2.1 MB", cell)],
        [Paragraph("DistilBERT (Fine-Tuned)", cell), Paragraph("91.80%", cell), Paragraph("91.20%", cell), Paragraph("142.0 ms", cell), Paragraph("268.0 MB", cell)],
        [Paragraph("<b>Balanced LogReg (Proposed)</b>", cell_bold), Paragraph("<b>87.42%</b>", cell_bold), Paragraph("<b>92.47%</b>", cell_bold), Paragraph("<b>2.4 ms</b>", cell_bold), Paragraph("<b>2.2 MB</b>", cell_bold)],
    ]
    comp_tab = create_table_box(comp_data, [125, 65, 65, 85, 71], styles, is_header=True)
    story.append(comp_tab)
    story.append(Spacer(1, 8))

    # Figure 6.3 Architecture Comparison
    fig_arch = os.path.join(fig_dir, "fig3_model_benchmark_comparison.png")
    if os.path.exists(fig_arch):
        track('fig6_3')
        story.append(Image(fig_arch, width=410, height=205))
        story.append(Paragraph("Figure 6.3: Model architecture comparison: classification accuracy vs. inference latency.", caption_fig))
        story.append(Spacer(1, 6))

    # Latency Breakdown Table 6.7 and Figure 6.5
    track('tab6_7')
    story.append(Paragraph("Table 6.7: Stage-by-stage latency benchmarking over 50 iterations (Total: 151.35 ms).", caption_tab))
    lat_data = [
        [Paragraph("<b>Pipeline Stage</b>", cell_bold), Paragraph("<b>Functional Scope</b>", cell_bold), Paragraph("<b>Mean Latency</b>", cell_bold), Paragraph("<b>Share (%)</b>", cell_bold)],
        [Paragraph("1. Section Segmentation", cell), Paragraph("Layout-aware regex slicing &amp; header detection", cell), Paragraph("0.06 ms", cell), Paragraph("0.04%", cell)],
        [Paragraph("2. Entity &amp; Feature Extraction", cell), Paragraph("Skill taxonomy, regex look-arounds, date math", cell), Paragraph("76.23 ms", cell), Paragraph("50.37%", cell)],
        [Paragraph("3. Role Classification", cell), Paragraph("67-feature matrix compilation &amp; model inference", cell), Paragraph("41.67 ms", cell), Paragraph("27.53%", cell)],
        [Paragraph("4. Job Description Parsing", cell), Paragraph("Taxonomy and keyword parsing of requisition", cell), Paragraph("30.53 ms", cell), Paragraph("20.17%", cell)],
        [Paragraph("5. SBERT Semantic Matching", cell), Paragraph("384-dimensional dense cosine embedding", cell), Paragraph("2.75 ms", cell), Paragraph("1.82%", cell)],
        [Paragraph("6. Tri-Pillar Scoring", cell), Paragraph("S_skill, S_exp, S_edu composite calculation", cell), Paragraph("0.09 ms", cell), Paragraph("0.06%", cell)],
        [Paragraph("<b>Total End-to-End Pipeline</b>", cell_bold), Paragraph("<b>Ingestion to verified scores &amp; roadmap</b>", cell_bold), Paragraph("<b>151.35 ms</b>", cell_bold), Paragraph("<b>100.0%</b>", cell_bold)],
    ]
    lat_tab = create_table_box(lat_data, [115, 155, 75, 66], styles, is_header=True)
    story.append(lat_tab)
    story.append(Spacer(1, 6))

    fig_lat = os.path.join(fig_dir, "fig1_latency_breakdown.png")
    if os.path.exists(fig_lat):
        track('fig6_5')
        story.append(Image(fig_lat, width=410, height=202))
        story.append(Paragraph("Figure 6.5: End-to-end pipeline processing latency breakdown across all six stages.", caption_fig))
        story.append(Spacer(1, 6))

    # 6.3 User or stakeholder validation
    track('sec6_3')
    story.append(Paragraph("6.3 User or stakeholder validation", h_sec))
    story.append(Paragraph("To evaluate how Component 1 behaves on real-world edge cases, four representative candidate profiles were evaluated. Table 6.8 summarizes the screening predictions and Tri-Pillar scores.", p_body))
    story.append(Spacer(1, 4))

    track('tab6_8')
    story.append(Paragraph("Table 6.8: Comparative case study predictions, tri-pillar scoring, and outcomes.", caption_tab))
    case_data = [
        [Paragraph("<b>Candidate Profile</b>", cell_bold), Paragraph("<b>Predicted Role (Confidence)</b>", cell_bold), Paragraph("<b>S_skill</b>", cell_bold), Paragraph("<b>S_exp</b>", cell_bold), Paragraph("<b>S_edu</b>", cell_bold), Paragraph("<b>S_cv</b>", cell_bold), Paragraph("<b>Screening Outcome</b>", cell_bold)],
        [Paragraph("1. Senior Full Stack (Concurrent Jobs)", cell), Paragraph("Full Stack Dev (0.94)", cell), Paragraph("91.20", cell), Paragraph("95.00", cell), Paragraph("80.00", cell), Paragraph("90.10", cell), Paragraph("Shortlisted (Direct to C2)", cell)],
        [Paragraph("2. CS Graduate (Project Heavy)", cell), Paragraph("Backend Dev (0.88)", cell), Paragraph("78.50", cell), Paragraph("0.00", cell), Paragraph("80.00", cell), Paragraph("55.25", cell), Paragraph("Junior Pool / C4 Roadmap", cell)],
        [Paragraph("3. Physics Ph.D. Switcher", cell), Paragraph("Data Scientist (0.81)", cell), Paragraph("82.00", cell), Paragraph("30.00", cell), Paragraph("50.00", cell), Paragraph("60.00", cell), Paragraph("Technical Interview (C2)", cell)],
        [Paragraph("4. Keyword-Stuffed Profile", cell), Paragraph("Software Eng (0.42)", cell), Paragraph("39.20", cell), Paragraph("10.00", cell), Paragraph("10.00", cell), Paragraph("24.60", cell), Paragraph("Automated Disqualification", cell)],
    ]
    case_tab = create_table_box(case_data, [100, 85, 42, 42, 42, 42, 58], styles, is_header=True)
    story.append(case_tab)
    story.append(Spacer(1, 8))

    story.append(Paragraph("In Case 1, a candidate holding a full-time corporate role while consulting concurrently was credited with 5.0 years instead of an inflated 7.0 years. In Case 2, university capstone projects were recognized for skill evidence (w = 0.70) while commercial tenure remained strictly at 0.0 years. In Case 3, a candidate with a doctorate in physics was scored at 50.0 rather than 100.0 due to quantitative non-technical field relevance (M_field = 0.50). In Case 4, an unverified bullet list of 45 keywords was penalized by isolated evidence weighting (w = 0.40), dropping S_skill to 39.20 and triggering automated disqualification.", p_body))

    # 6.4 Integration results
    track('sec6_4')
    story.append(Paragraph("6.4 Integration results", h_sec))
    story.append(Paragraph("Within the wider RecruitAI platform, Component 1 verified seamless inter-service integration. The extracted profile payload was consumed by Component 2 to generate role-tailored coding challenges. The uncollapsed vector S_C1 = [S_skill, S_exp, S_edu] was consumed by Component 3 for LambdaMART listwise ranking, achieving an NDCG@5 of 0.9437. Unshortlisted candidates were routed to Component 4, which synthesized 4-milestone learning roadmaps. Figure 6.6 illustrates empirical benchmark performance across all four components.", p_body))
    story.append(Spacer(1, 4))

    fig_bench = os.path.join(fig_dir, "fig10_cross_component_benchmarks.png")
    if os.path.exists(fig_bench):
        track('fig6_6')
        story.append(Image(fig_bench, width=410, height=266))
        story.append(Paragraph("Figure 6.6: Cross-component empirical benchmark comparison across the four RecruitAI microservices.", caption_fig))
        story.append(Spacer(1, 6))

    # 6.5 Summary of findings
    track('sec6_5')
    story.append(Paragraph("6.5 Summary of findings", h_sec))
    story.append(Paragraph("Permutation feature importance analysis across 50 shuffling iterations demonstrated that technical skills contribute 85.9% of classification power, followed by education (11.8%) and experience tenure (2.3%). Figure 6.4 contrasts permutation importance with the deployed Tri-Pillar weights.", p_body))
    story.append(Spacer(1, 4))

    fig_feat = os.path.join(fig_dir, "fig2_feature_importance_weights.png")
    if os.path.exists(fig_feat):
        track('fig6_4')
        story.append(Image(fig_feat, width=410, height=181))
        story.append(Paragraph("Figure 6.4: Empirical feature importance contributions vs. deployed tri-pillar weights.", caption_fig))
        story.append(Spacer(1, 6))

    # Feature Ablation Table 6.6
    track('tab6_6')
    story.append(Paragraph("Table 6.6: Feature subset extraction ablation study on real applicant CV profiles.", caption_tab))
    abl_data = [
        [Paragraph("<b>Feature Subset Evaluated</b>", cell_bold), Paragraph("<b>Accuracy (%)</b>", cell_bold), Paragraph("<b>Precision (%)</b>", cell_bold), Paragraph("<b>Recall (%)</b>", cell_bold), Paragraph("<b>Macro F1 (%)</b>", cell_bold)],
        [Paragraph("Skills Only (S_skill and domain lexicons)", cell), Paragraph("94.50%", cell), Paragraph("96.00%", cell), Paragraph("94.50%", cell), Paragraph("93.69%", cell)],
        [Paragraph("Experience Only (S_exp and tenure vectors)", cell), Paragraph("10.00%", cell), Paragraph("7.40%", cell), Paragraph("10.00%", cell), Paragraph("4.62%", cell)],
        [Paragraph("Education Only (S_edu and degree levels)", cell), Paragraph("12.50%", cell), Paragraph("12.61%", cell), Paragraph("12.50%", cell), Paragraph("8.14%", cell)],
        [Paragraph("<b>Combined Tri-Pillar Representation</b>", cell_bold), Paragraph("<b>91.50%</b>", cell_bold), Paragraph("<b>91.21%</b>", cell_bold), Paragraph("<b>91.50%</b>", cell_bold), Paragraph("<b>90.43%</b>", cell_bold)],
    ]
    abl_tab = create_table_box(abl_data, [165, 60, 60, 60, 66], styles, is_header=True)
    story.append(abl_tab)
    story.append(Spacer(1, 6))

    # Leakage Audit Figure 6.1
    fig_leak = os.path.join(fig_dir, "fig5_synthetic_leakage_audit.png")
    if os.path.exists(fig_leak):
        track('fig6_1')
        story.append(Image(fig_leak, width=410, height=202))
        story.append(Paragraph("Figure 6.1: Forensic evaluation: synthetic leakage vs. genuine real-world evaluation.", caption_fig))
        story.append(Spacer(1, 6))

    # Confusion Matrix Clustering Table 6.9
    track('tab6_9')
    story.append(Paragraph("Table 6.9: Primary off-diagonal error clusters in 20x20 classification matrix.", caption_tab))
    err_data = [
        [Paragraph("<b>Error Cluster</b>", cell_bold), Paragraph("<b>Main Confusions Observed</b>", cell_bold), Paragraph("<b>Error Rate</b>", cell_bold), Paragraph("<b>Root Cause Analysis</b>", cell_bold)],
        [Paragraph("Web Stack Triad", cell), Paragraph("Full Stack ↔ Frontend / Backend", cell), Paragraph("11.8%", cell), Paragraph("Resumes frequently list both React and Node.js duties", cell)],
        [Paragraph("Data &amp; AI Continuum", cell), Paragraph("Data Scientist ↔ Data / ML Engineer", cell), Paragraph("14.2%", cell), Paragraph("Data scientists deploy PySpark, SQL, and Docker models", cell)],
        [Paragraph("Cloud &amp; Infrastructure", cell), Paragraph("DevOps ↔ SRE / Cloud Architect", cell), Paragraph("4.5%", cell), Paragraph("Shared Kubernetes, Docker, and Terraform vocabularies", cell)],
        [Paragraph("Generalist Residual", cell), Paragraph("Software Engineer ↔ All Roles", cell), Paragraph("18.4%", cell), Paragraph("Generalist profiles lack specialized technical jargon", cell)],
    ]
    err_tab = create_table_box(err_data, [105, 115, 55, 136], styles, is_header=True)
    story.append(err_tab)
    story.append(PageBreak())
