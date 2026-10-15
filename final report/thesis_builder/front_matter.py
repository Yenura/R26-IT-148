import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib import colors
from thesis_builder.styles import clean_xml, PRINTABLE_WIDTH
from thesis_builder.canvas_helper import PageTracker

def append_front_matter(story, styles, page_dict=None):
    if page_dict is None:
        page_dict = {}

    def get_pg(key, default=""):
        return page_dict.get(key, default)

    body = styles['ThesisBody']
    body_bold = styles['ThesisBodyBold']
    caption = styles['FigureCaption']
    single_body = styles['SingleBody']

    # -------------------------------------------------------------------------
    # 1. TITLE PAGE (NO PAGE NUMBER)
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 15))
    story.append(Paragraph("AI-DRIVEN RECRUITMENT ECOSYSTEM FOR INTELLIGENT JOB MATCHING AND PREDICTIVE CAREER DEVELOPMENT", styles['CoverMainTitle']))
    story.append(Spacer(1, 20))

    story.append(Paragraph("INDIVIDUAL THESIS", styles['CoverDegreeHeading']))
    story.append(Spacer(1, 25))

    story.append(Paragraph("D. T. D. Perera", styles['CoverMainTitle']))
    story.append(Paragraph("(IT22089236)", styles['CoverSubtitle']))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Individual component:</b> Automated Semantic Resume Screening and IT Job Role Classification", styles['CoverSubtitle']))
    story.append(Paragraph("<b>Group ID:</b> R26-IT-148", styles['CoverSubtitle']))
    story.append(Spacer(1, 30))

    story.append(Paragraph("Report submitted in partial fulfilment of the requirements for the", styles['CoverSubmissionNote']))
    story.append(Paragraph("Bachelor of Science (Honours) in Information Technology", styles['CoverDegreeHeading']))
    story.append(Paragraph("Specialising in Information Technology", styles['CoverSubtitle']))
    story.append(Spacer(1, 18))

    story.append(Paragraph("Department of Information Technology", styles['CoverInstitution']))
    story.append(Paragraph("Sri Lanka Institute of Information Technology", styles['CoverInstitution']))
    story.append(Paragraph("Sri Lanka", styles['CoverDepartment']))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Document Publication Portal: https://r26-it-148-website.yenura02.workers.dev/", styles['CoverSubmissionNote']))
    story.append(Paragraph("October 2026", styles['CoverDepartment']))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 2. DECLARATION AND SUPERVISOR CERTIFICATION (Page i)
    # -------------------------------------------------------------------------
    story.append(Paragraph("DECLARATION AND SUPERVISOR CERTIFICATION", styles['ChapterHeading']))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Candidate declaration.</b> I declare that this thesis is my own work and does not incorporate, without acknowledgement, material previously submitted for a degree or diploma at any university or institute of higher learning. To the best of my knowledge, it contains no material previously published or written by another person except where acknowledgement is made in the text. I grant the Sri Lanka Institute of Information Technology the non-exclusive right to reproduce and distribute this thesis, in whole or in part, in print, electronic, or other media, while retaining the right to use the content in future work.", single_body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Academic integrity and AI disclosure.</b> I have disclosed all use of generative AI and other automated tools in accordance with the module policy. I remain responsible for the accuracy, originality, citations, code, data, analyses, and conclusions in this thesis.", single_body))
    story.append(Spacer(1, 14))

    fig_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    sig1_path = os.path.join(fig_dir, "sig_d_t_d_perera.png")
    sig_perera = RLImage(sig1_path, width=75, height=28)

    cand_table_data = [
        [Paragraph("<b>Student name:</b>", styles['TableCellBold']), Paragraph("D. T. D. Perera", styles['TableCell'])],
        [Paragraph("<b>Student ID:</b>", styles['TableCellBold']), Paragraph("IT22089236", styles['TableCell'])],
        [Paragraph("<b>Signature:</b>", styles['TableCellBold']), sig_perera],
        [Paragraph("<b>Date:</b>", styles['TableCellBold']), Paragraph("10 October 2026", styles['TableCell'])],
    ]
    cand_table = Table(cand_table_data, colWidths=[110, 301])
    cand_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(cand_table)
    story.append(Spacer(1, 18))

    story.append(Paragraph("<b>Supervisor certification.</b> The above candidate carried out this research for the bachelor's degree thesis under my supervision.", single_body))
    story.append(Spacer(1, 10))

    sup_table_data = [
        [Paragraph("<b>Role and name</b>", styles['TableCellCenterBold']), Paragraph("<b>Signature</b>", styles['TableCellCenterBold']), Paragraph("<b>Date</b>", styles['TableCellCenterBold'])],
        [Paragraph("Supervisor: Dr. Pradeep Kalansooriya", styles['TableCell']), Paragraph("", styles['TableCell']), Paragraph("", styles['TableCell'])],
        [Paragraph("Co-supervisor: Ms. K. V. S. Dilrukshi", styles['TableCell']), Paragraph("", styles['TableCell']), Paragraph("", styles['TableCell'])],
    ]
    sup_table = Table(sup_table_data, colWidths=[201, 110, 100])
    sup_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#000000")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#000000")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAEAEA")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(sup_table)
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 3. ABSTRACT (Page ii)
    # -------------------------------------------------------------------------
    story.append(Paragraph("ABSTRACT", styles['ChapterHeading']))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Automated resume screening is intended to alleviate cognitive fatigue and streamline recruitment in high-volume enterprise hiring. However, contemporary commercial and open-source Applicant Tracking Systems (ATS) predominantly rely on naive keyword matching and unweighted boolean substring queries. These legacy mechanisms suffer from pervasive failure modes: highly qualified engineers who express their competencies through nuanced architectural descriptions are prematurely discarded, while opportunistic applicants pad curriculum vitae with unverified buzzwords to game screening filters. Moreover, recent academic literature in automated resume classification frequently exhibits severe synthetic benchmark leakage, reporting near-perfect F1 scores on template-generated datasets where models merely memorize invariant boilerplate prose and class headers.", single_body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("This dissertation presents the design, mathematical formalization, software engineering implementation, and empirical validation of Component 1 of the RecruitAI ecosystem (Research Identifier: R26-IT-148): Automated Semantic Resume Screening and IT Job Role Classification. Operating as an asynchronous FastAPI microservice on dedicated TCP port 8001, the system ingests heterogeneous PDF, DOCX, and TXT resumes and converts them into structured, mathematically auditable candidate profiles. The research delivers four foundational technical contributions: first, a format-agnostic, layout-aware ingestion pipeline featuring automated Personally Identifiable Information (PII) redaction and boundary-guarded Named Entity Recognition (NER) for over 400 canonical IT competencies across seven engineering domains, incorporating regular expression look-around shields that completely suppress polysemous token collisions on ambiguous single-letter and common words (such as C, R, Go, Rust, Spring, and REST); second, a formal temporal interval union algebra that eliminates tenure inflation from concurrent employment contracts and strictly separates self-directed academic projects from commercial corporate tenure; third, a two-dimensional credential qualification ontology that decouples degree attainment tier from disciplinary field relevance; and fourth, an evidence-weighted skill scoring hierarchy that distinguishes isolated keyword mentions (weight 0.40) from verified workplace execution (weight 1.00), emitting an uncollapsed Tri-Pillar Qualification Vector (S_skill, S_exp, S_edu).", single_body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Candidate role classification across 20 canonical IT roles is performed using a balanced multinomial logistic regression model trained on 67 dense normalized features with sublinear TF-IDF vectorization. Evaluated on a strictly held-out test partition of 819 authentic resumes from a curated 4,000-resume corpus, the classifier achieves 87.42% accuracy, 91.35% macro precision, 94.35% macro recall, and 92.47% macro F1 (weighted F1: 87.16%), with 5-fold stratified cross-validation yielding 85.95% ± 0.96% accuracy. Inference executes in 2.4 ms per resume (approximately 59 times faster than fine-tuned DistilBERT, 142.0 ms), while guaranteeing closed-form SHAP feature attribution transparency. The microservice is verified by 195 automated Pytest checks with a 100% pass rate, establishing a production-ready, fair, and explainable intake gateway for enterprise technical recruitment.", single_body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Keywords:</b> resume parsing, named entity recognition, job role classification, polysemy protection, experience disambiguation, data leakage audit, tri-pillar scoring, RecruitAI, logistic regression.", single_body))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 4. ACKNOWLEDGEMENTS (Page iii)
    # -------------------------------------------------------------------------
    story.append(Paragraph("ACKNOWLEDGEMENTS", styles['ChapterHeading']))
    story.append(Spacer(1, 10))

    story.append(Paragraph("First and foremost, I offer my profound gratitude to the Almighty for granting me the intellectual resilience, wisdom, and strength to complete this undergraduate research dissertation.", body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("I express my sincere and heartfelt gratitude to my research supervisor, Dr. Pradeep Kalansooriya, and co-supervisor, Ms. K. V. S. Dilrukshi, at the Faculty of Computing, Sri Lanka Institute of Information Technology (SLIIT). Their meticulous technical reviews, constructive critique, and continuous academic mentorship through every phase of system design, statistical modeling, data leakage auditing, and experimental validation were essential in maintaining scientific rigor.", body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("I also extend my sincere thanks to the Dean of the Faculty of Computing, the Head of the Department of Information Technology, and the entire academic and administrative staff of SLIIT for providing the state-of-the-art laboratory facilities, computing infrastructure, and supportive intellectual environment required to conduct this machine learning research.", body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Special recognition and gratitude are owed to my project teammates in Research Group R26-IT-148: Yenura S. Karunanayaka (IT22306272) and K. G. Savinda N. Perera (IT22027610). Their exceptional collaboration, constructive technical debates, and dedicated work on aligning our respective microservice contracts made the realized vision of the RecruitAI ecosystem possible. All collaborative research deliverables, presentation slides, and technical document artifacts are published on our official dissemination portal: https://r26-it-148-website.yenura02.workers.dev/.", body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Finally, my deepest debt of gratitude goes to my parents and family for their unwavering love, sacrifices, encouragement, and patience throughout my undergraduate studies. I dedicate this work to them.", body))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 5. TABLE OF CONTENTS (Pages iv, v, vi)
    # -------------------------------------------------------------------------
    story.append(Paragraph("TABLE OF CONTENTS", styles['ChapterHeading']))
    story.append(Spacer(1, 6))

    toc_title_style = styles['TableCellBold']
    toc_text_style = styles['TableCell']
    toc_page_style = styles['TableCellCenterBold']

    toc_rows = [
        [Paragraph("<b>Item / Chapter / Section</b>", toc_title_style), Paragraph("<b>Page</b>", toc_page_style)],
        [Paragraph("Declaration and Supervisor Certification", toc_text_style), Paragraph(get_pg("dec", "i"), toc_page_style)],
        [Paragraph("Abstract", toc_text_style), Paragraph(get_pg("abs", "ii"), toc_page_style)],
        [Paragraph("Acknowledgements", toc_text_style), Paragraph(get_pg("ack", "iii"), toc_page_style)],
        [Paragraph("Table of Contents", toc_text_style), Paragraph(get_pg("toc", "iv"), toc_page_style)],
        [Paragraph("List of Figures", toc_text_style), Paragraph(get_pg("lof", "vii"), toc_page_style)],
        [Paragraph("List of Tables", toc_text_style), Paragraph(get_pg("lot", "viii"), toc_page_style)],
        [Paragraph("List of Abbreviations", toc_text_style), Paragraph(get_pg("loa", "ix"), toc_page_style)],
        
        [Paragraph("<b>1 INTRODUCTION</b>", toc_title_style), Paragraph(get_pg("ch1", "1"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.1 Overall project context", toc_text_style), Paragraph(get_pg("sec1_1", "1"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.2 Individual component context", toc_text_style), Paragraph(get_pg("sec1_2", "2"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.3 Problem statement", toc_text_style), Paragraph(get_pg("sec1_3", "2"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.4 Research gap", toc_text_style), Paragraph(get_pg("sec1_4", "3"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.5 Aim and objectives", toc_text_style), Paragraph(get_pg("sec1_5", "3"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.6 Research questions or hypotheses", toc_text_style), Paragraph(get_pg("sec1_6", "4"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.7 Scope limitations and assumptions", toc_text_style), Paragraph(get_pg("sec1_7", "4"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.8 Individual contribution", toc_text_style), Paragraph(get_pg("sec1_8", "5"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.9 Thesis structure", toc_text_style), Paragraph(get_pg("sec1_9", "5"), toc_page_style)],

        [Paragraph("<b>2 LITERATURE REVIEW AND RELATED WORK</b>", toc_title_style), Paragraph(get_pg("ch2", "6"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.1 Review method and scope", toc_text_style), Paragraph(get_pg("sec2_1", "6"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.2 Domain and theoretical foundations", toc_text_style), Paragraph(get_pg("sec2_2", "7"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.3 Related research", toc_text_style), Paragraph(get_pg("sec2_3", "8"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.4 Existing systems products and techniques", toc_text_style), Paragraph(get_pg("sec2_4", "9"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.5 Gap synthesis and conceptual framework", toc_text_style), Paragraph(get_pg("sec2_5", "11"), toc_page_style)],

        [Paragraph("<b>3 RESEARCH METHODOLOGY</b>", toc_title_style), Paragraph(get_pg("ch3", "12"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.1 Research design", toc_text_style), Paragraph(get_pg("sec3_1", "12"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.2 Data participants or study materials", toc_text_style), Paragraph(get_pg("sec3_2", "13"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.3 Experimental or study procedure", toc_text_style), Paragraph(get_pg("sec3_3", "14"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.4 Measures and evaluation metrics", toc_text_style), Paragraph(get_pg("sec3_4", "15"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.5 Data analysis", toc_text_style), Paragraph(get_pg("sec3_5", "16"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.6 Ethics privacy security and responsible AI", toc_text_style), Paragraph(get_pg("sec3_6", "17"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.7 Reproducibility and research artefacts", toc_text_style), Paragraph(get_pg("sec3_7", "18"), toc_page_style)],

        [Paragraph("<b>4 PRODUCT AND SOLUTION DESIGN</b>", toc_title_style), Paragraph(get_pg("ch4", "19"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.1 Requirements", toc_text_style), Paragraph(get_pg("sec4_1", "19"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.2 Component architecture within the complete solution", toc_text_style), Paragraph(get_pg("sec4_2", "20"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.3 Design alternatives and decisions", toc_text_style), Paragraph(get_pg("sec4_3", "22"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.4 Detailed design", toc_text_style), Paragraph(get_pg("sec4_4", "23"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.5 Standards and professional practice", toc_text_style), Paragraph(get_pg("sec4_5", "25"), toc_page_style)],

        [Paragraph("<b>5 IMPLEMENTATION INTEGRATION AND TESTING</b>", toc_title_style), Paragraph(get_pg("ch5", "26"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.1 Development environment and technology stack", toc_text_style), Paragraph(get_pg("sec5_1", "26"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.2 Component implementation", toc_text_style), Paragraph(get_pg("sec5_2", "27"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.3 Integration with the other components", toc_text_style), Paragraph(get_pg("sec5_3", "29"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.4 Verification and software testing", toc_text_style), Paragraph(get_pg("sec5_4", "30"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.5 Deployment and operation", toc_text_style), Paragraph(get_pg("sec5_5", "31"), toc_page_style)],

        [Paragraph("<b>6 RESULTS AND VALIDATION</b>", toc_title_style), Paragraph(get_pg("ch6", "32"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.1 Research results", toc_text_style), Paragraph(get_pg("sec6_1", "32"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.2 Product and technical results", toc_text_style), Paragraph(get_pg("sec6_2", "33"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.3 User or stakeholder validation", toc_text_style), Paragraph(get_pg("sec6_3", "35"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.4 Integration results", toc_text_style), Paragraph(get_pg("sec6_4", "36"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.5 Summary of findings", toc_text_style), Paragraph(get_pg("sec6_5", "37"), toc_page_style)],

        [Paragraph("<b>7 DISCUSSION</b>", toc_title_style), Paragraph(get_pg("ch7", "38"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.1 Interpretation of findings", toc_text_style), Paragraph(get_pg("sec7_1", "38"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.2 Comparison with literature baselines and existing solutions", toc_text_style), Paragraph(get_pg("sec7_2", "39"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.3 Research contribution", toc_text_style), Paragraph(get_pg("sec7_3", "40"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.4 Product contribution", toc_text_style), Paragraph(get_pg("sec7_4", "41"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.5 Limitations and threats to validity", toc_text_style), Paragraph(get_pg("sec7_5", "41"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.6 Implications", toc_text_style), Paragraph(get_pg("sec7_6", "42"), toc_page_style)],

        [Paragraph("<b>8 COMMERCIALISATION AND SUSTAINABILITY</b>", toc_title_style), Paragraph(get_pg("ch8", "43"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.1 Value proposition and target users", toc_text_style), Paragraph(get_pg("sec8_1", "43"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.2 Market and competitive position", toc_text_style), Paragraph(get_pg("sec8_2", "44"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.3 Business or sustainability model", toc_text_style), Paragraph(get_pg("sec8_3", "45"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.4 Scalability intellectual property and compliance", toc_text_style), Paragraph(get_pg("sec8_4", "46"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.5 Contribution to the Sustainable Development Goals", toc_text_style), Paragraph(get_pg("sec8_5", "47"), toc_page_style)],

        [Paragraph("<b>9 CONCLUSION AND FUTURE DIRECTIONS</b>", toc_title_style), Paragraph(get_pg("ch9", "48"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;9.1 Conclusion", toc_text_style), Paragraph(get_pg("sec9_1", "48"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;9.2 Achievement of objectives", toc_text_style), Paragraph(get_pg("sec9_2", "48"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;9.3 Individual research and product contributions", toc_text_style), Paragraph(get_pg("sec9_3", "49"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;9.4 Future directions", toc_text_style), Paragraph(get_pg("sec9_4", "50"), toc_page_style)],

        [Paragraph("<b>REFERENCES</b>", toc_title_style), Paragraph(get_pg("refs", "51"), toc_page_style)],
        [Paragraph("<b>GLOSSARY</b>", toc_title_style), Paragraph(get_pg("glossary", "54"), toc_page_style)],
        [Paragraph("<b>APPENDICES</b>", toc_title_style), Paragraph(get_pg("app_a", "55"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Appendix A Research instruments or extended results", toc_text_style), Paragraph(get_pg("app_a", "55"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Appendix B Academic integrity and AI use disclosure", toc_text_style), Paragraph(get_pg("app_b", "57"), toc_page_style)],
    ]

    toc_table = Table(toc_rows, colWidths=[361, 50])
    toc_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#000000")),
        ('TOPPADDING', (0,0), (-1,-1), 1.6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.6),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 6. LIST OF FIGURES (Page vii)
    # -------------------------------------------------------------------------
    story.append(Paragraph("LIST OF FIGURES", styles['ChapterHeading']))
    story.append(Spacer(1, 8))

    lof_rows = [
        [Paragraph("<b>Figure Number &amp; Title</b>", toc_title_style), Paragraph("<b>Page</b>", toc_page_style)],
        [Paragraph("Figure 1.1: Multi-Microservice Architecture of the RecruitAI Ecosystem (R26-IT-148)", toc_text_style), Paragraph(get_pg("fig1_1", "2"), toc_page_style)],
        [Paragraph("Figure 3.1: Context-Guarded Regex Look-Around Shielding vs. Naive Substring Tokenizers", toc_text_style), Paragraph(get_pg("fig3_1", "15"), toc_page_style)],
        [Paragraph("Figure 3.2: Temporal Experience Disambiguation: Concurrent Employment Interval Union", toc_text_style), Paragraph(get_pg("fig3_2", "16"), toc_page_style)],
        [Paragraph("Figure 4.1: End-to-End RecruitAI Candidate Lifecycle and Analytical State Flow", toc_text_style), Paragraph(get_pg("fig4_1", "21"), toc_page_style)],
        [Paragraph("Figure 6.1: Forensic Evaluation: Synthetic Leakage vs. Genuine Real-World Evaluation", toc_text_style), Paragraph(get_pg("fig6_1", "33"), toc_page_style)],
        [Paragraph("Figure 6.2: Empirical Classification Performance Across 20 Canonical IT Roles (N=819)", toc_text_style), Paragraph(get_pg("fig6_2", "34"), toc_page_style)],
        [Paragraph("Figure 6.3: Model Architecture Comparison: Classification Accuracy vs. Inference Latency", toc_text_style), Paragraph(get_pg("fig6_3", "35"), toc_page_style)],
        [Paragraph("Figure 6.4: Empirical Feature Importance Contributions vs. Deployed Tri-Pillar Weights", toc_text_style), Paragraph(get_pg("fig6_4", "36"), toc_page_style)],
        [Paragraph("Figure 6.5: End-to-End Pipeline Processing Latency Breakdown Across All Six Stages", toc_text_style), Paragraph(get_pg("fig6_5", "37"), toc_page_style)],
        [Paragraph("Figure 6.6: Cross-Component Empirical Benchmark Comparison Across the Four Microservices", toc_text_style), Paragraph(get_pg("fig6_6", "38"), toc_page_style)]
    ]
    lof_table = Table(lof_rows, colWidths=[361, 50])
    lof_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#000000")),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(lof_table)
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 7. LIST OF TABLES (Page viii)
    # -------------------------------------------------------------------------
    story.append(Paragraph("LIST OF TABLES", styles['ChapterHeading']))
    story.append(Spacer(1, 8))

    lot_rows = [
        [Paragraph("<b>Table Number &amp; Title</b>", toc_title_style), Paragraph("<b>Page</b>", toc_page_style)],
        [Paragraph("Table 1.1: Enterprise Technical Recruitment Funnel Drop-Off Metrics and ATS Failure Points", toc_text_style), Paragraph(get_pg("tab1_1", "1"), toc_page_style)],
        [Paragraph("Table 2.1: Comprehensive Survey of Commercial and Open-Source Resume Screening Engines", toc_text_style), Paragraph(get_pg("tab2_1", "9"), toc_page_style)],
        [Paragraph("Table 2.2: International Academic Degree Framework Harmonization Matrix", toc_text_style), Paragraph(get_pg("tab2_2", "10"), toc_page_style)],
        [Paragraph("Table 3.1: Dense 67-Dimensional Feature Vector Specification", toc_text_style), Paragraph(get_pg("tab3_1", "14"), toc_page_style)],
        [Paragraph("Table 4.1: Academic Degree Tier Level and Disciplinary Field Relevance Scoring Matrix", toc_text_style), Paragraph(get_pg("tab4_1", "24"), toc_page_style)],
        [Paragraph("Table 4.2: Canonical IT Job Role Benchmark Competencies and Core Skills Lexicon", toc_text_style), Paragraph(get_pg("tab4_2", "25"), toc_page_style)],
        [Paragraph("Table 5.1: Component 1 Microservice RESTful API Specification (Port 8001)", toc_text_style), Paragraph(get_pg("tab5_1", "29"), toc_page_style)],
        [Paragraph("Table 5.2: Automated Pytest Verification Suite Breakdown (195 Passed Tests)", toc_text_style), Paragraph(get_pg("tab5_2", "30"), toc_page_style)],
        [Paragraph("Table 6.1: 5-Fold Stratified Cross-Validation Convergence and Invariance Metrics", toc_text_style), Paragraph(get_pg("tab6_1", "32"), toc_page_style)],
        [Paragraph("Table 6.2: Hyperparameter Grid Search Optimization Results for Logistic Regression", toc_text_style), Paragraph(get_pg("tab6_2", "32"), toc_page_style)],
        [Paragraph("Table 6.3: Primary Classification Performance Metrics on Held-Out Test Partition (N=819)", toc_text_style), Paragraph(get_pg("tab6_3", "33"), toc_page_style)],
        [Paragraph("Table 6.4: Per-Class Precision, Recall, and F1-Score Across 20 Canonical IT Roles", toc_text_style), Paragraph(get_pg("tab6_4", "34"), toc_page_style)],
        [Paragraph("Table 6.5: Comparative Benchmark Against Alternative Machine Learning Architectures", toc_text_style), Paragraph(get_pg("tab6_5", "35"), toc_page_style)],
        [Paragraph("Table 6.6: Feature Subset Extraction Ablation Study on Real Applicant CV Profiles", toc_text_style), Paragraph(get_pg("tab6_6", "36"), toc_page_style)],
        [Paragraph("Table 6.7: Stage-by-Stage Latency Benchmarking Over 50 Iterations (Total: 151.35 ms)", toc_text_style), Paragraph(get_pg("tab6_7", "37"), toc_page_style)],
        [Paragraph("Table 6.8: Comparative Case Study Predictions, Tri-Pillar Scoring, and Outcomes", toc_text_style), Paragraph(get_pg("tab6_8", "38"), toc_page_style)],
        [Paragraph("Table 6.9: Primary Off-Diagonal Error Clusters in 20x20 Classification Matrix", toc_text_style), Paragraph(get_pg("tab6_9", "39"), toc_page_style)],
        [Paragraph("Table 7.1: Representative Closed-Form Feature Attribution Log-Odds Weights", toc_text_style), Paragraph(get_pg("tab7_1", "40"), toc_page_style)],
        [Paragraph("Table 7.2: Global AI Regulatory Compliance Mapping (EU AI Act, NYC LL144, GDPR, EEOC)", toc_text_style), Paragraph(get_pg("tab7_2", "41"), toc_page_style)],
        [Paragraph("Table 8.1: Target Customer Segments and Value Propositions for Commercial Deployment", toc_text_style), Paragraph(get_pg("tab8_1", "44"), toc_page_style)],
        [Paragraph("Table 8.2: Commercial Competitive Landscape and Feature Differentiation Matrix", toc_text_style), Paragraph(get_pg("tab8_2", "45"), toc_page_style)],
        [Paragraph("Table 8.3: Three-Tier SaaS Commercial Pricing and Revenue Model", toc_text_style), Paragraph(get_pg("tab8_3", "46"), toc_page_style)],
        [Paragraph("Table 8.4: Infrastructure Unit Economics and Inference Cost Comparison (10,000 Screens)", toc_text_style), Paragraph(get_pg("tab8_4", "46"), toc_page_style)],
        [Paragraph("Table 8.5: Alignment with United Nations Sustainable Development Goals (SDGs)", toc_text_style), Paragraph(get_pg("tab8_5", "47"), toc_page_style)],
        [Paragraph("Table 9.1: Systematic Evaluation of Research Objectives and Hypotheses Against Empirical Results", toc_text_style), Paragraph(get_pg("tab9_1", "49"), toc_page_style)],
        [Paragraph("Table A.1: Canonical IT Job Roles Taxonomy, Domain Clusters, and Core Competencies", toc_text_style), Paragraph(get_pg("tabA_1", "55"), toc_page_style)],
        [Paragraph("Table B.1: OpenAPI 3.0 Request Fields and Response Schema for Screening Endpoint", toc_text_style), Paragraph(get_pg("tabB_1", "57"), toc_page_style)],
    ]
    lot_table = Table(lot_rows, colWidths=[361, 50])
    lot_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#000000")),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(lot_table)
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 8. LIST OF ABBREVIATIONS (Page ix)
    # -------------------------------------------------------------------------
    story.append(Paragraph("LIST OF ABBREVIATIONS", styles['ChapterHeading']))
    story.append(Spacer(1, 8))

    abbr_rows = [
        [Paragraph("<b>Abbreviation</b>", toc_title_style), Paragraph("<b>Meaning</b>", toc_title_style)],
        [Paragraph("API", toc_text_style), Paragraph("Application Programming Interface", toc_text_style)],
        [Paragraph("ATS", toc_text_style), Paragraph("Applicant Tracking System", toc_text_style)],
        [Paragraph("BERT", toc_text_style), Paragraph("Bidirectional Encoder Representations from Transformers", toc_text_style)],
        [Paragraph("CRF", toc_text_style), Paragraph("Conditional Random Field", toc_text_style)],
        [Paragraph("CSV", toc_text_style), Paragraph("Comma-Separated Values", toc_text_style)],
        [Paragraph("CV", toc_text_style), Paragraph("Curriculum Vitae / Resume", toc_text_style)],
        [Paragraph("DistilBERT", toc_text_style), Paragraph("Distilled Bidirectional Encoder Representations from Transformers", toc_text_style)],
        [Paragraph("DSR", toc_text_style), Paragraph("Design Science Research", toc_text_style)],
        [Paragraph("EEOC", toc_text_style), Paragraph("Equal Employment Opportunity Commission", toc_text_style)],
        [Paragraph("EQF", toc_text_style), Paragraph("European Qualifications Framework", toc_text_style)],
        [Paragraph("GBDT", toc_text_style), Paragraph("Gradient Boosted Decision Trees", toc_text_style)],
        [Paragraph("GDPR", toc_text_style), Paragraph("General Data Protection Regulation", toc_text_style)],
        [Paragraph("JD", toc_text_style), Paragraph("Job Description / Requisition Specification", toc_text_style)],
        [Paragraph("JSON", toc_text_style), Paragraph("JavaScript Object Notation", toc_text_style)],
        [Paragraph("LambdaMART", toc_text_style), Paragraph("Lambda Multiple Additive Regression Trees", toc_text_style)],
        [Paragraph("LTR", toc_text_style), Paragraph("Learning-to-Rank", toc_text_style)],
        [Paragraph("NDCG", toc_text_style), Paragraph("Normalised Discounted Cumulative Gain", toc_text_style)],
        [Paragraph("NER", toc_text_style), Paragraph("Named Entity Recognition", toc_text_style)],
        [Paragraph("NLP", toc_text_style), Paragraph("Natural Language Processing", toc_text_style)],
        [Paragraph("OCR", toc_text_style), Paragraph("Optical Character Recognition", toc_text_style)],
        [Paragraph("PII", toc_text_style), Paragraph("Personally Identifiable Information", toc_text_style)],
        [Paragraph("QA", toc_text_style), Paragraph("Quality Assurance", toc_text_style)],
        [Paragraph("REST", toc_text_style), Paragraph("Representational State Transfer", toc_text_style)],
        [Paragraph("SBERT", toc_text_style), Paragraph("Sentence-BERT (Sentence Bidirectional Encoder Representations from Transformers)", toc_text_style)],
        [Paragraph("SDG", toc_text_style), Paragraph("Sustainable Development Goals (United Nations)", toc_text_style)],
        [Paragraph("SHAP", toc_text_style), Paragraph("SHapley Additive exPlanations", toc_text_style)],
        [Paragraph("SLIIT", toc_text_style), Paragraph("Sri Lanka Institute of Information Technology", toc_text_style)],
        [Paragraph("SLQF", toc_text_style), Paragraph("Sri Lanka Qualifications Framework", toc_text_style)],
        [Paragraph("SRE", toc_text_style), Paragraph("Site Reliability Engineering", toc_text_style)],
        [Paragraph("SVM", toc_text_style), Paragraph("Support Vector Machine", toc_text_style)],
        [Paragraph("TF-IDF", toc_text_style), Paragraph("Term Frequency - Inverse Document Frequency", toc_text_style)],
        [Paragraph("UI/UX", toc_text_style), Paragraph("User Interface / User Experience", toc_text_style)],
    ]
    abbr_table = Table(abbr_rows, colWidths=[90, 321])
    abbr_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#000000")),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(abbr_table)
    story.append(PageBreak())
