import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle

def append_group_front_matter(story, styles, p, b, sp, make_box, caption_style, fig_dir, page_map=None):
    PRIMARY = colors.HexColor("#1A365D")
    SECONDARY = colors.HexColor("#2B6CB0")
    ACCENT = colors.HexColor("#C53030")
    DARK_TEXT = colors.HexColor("#2D3748")

    title_style = styles['CoverTitle']
    subtitle_style = styles['CoverSubtitle']
    ch_title_style = styles['ChapterTitle']
    h1_style = styles['Heading1_Custom']
    body_style = styles['Body_Custom']
    body_bold = styles['Body_Bold']

    if page_map is None:
        page_map = {
            'ch1': 8, 'ch2': 12, 'ch3': 15, 'ch4': 18, 'ch5': 22, 'ch6': 24, 'ch7': 28, 'ch8': 31,
            'ref': 33, 'appA': 35, 'appB': 36,
            'fig1_1': 9, 'fig1_2': 10, 'fig4_1': 18, 'fig4_2': 19, 'fig6_1': 24, 'fig6_2': 25, 'fig6_3': 26,
            'tab1_1': 11, 'tab2_1': 14, 'tab3_1': 17, 'tab5_1': 23, 'tab6_1': 25, 'tab6_2': 26, 'tab6_3': 27,
            'tab7_1': 29, 'tabA_1': 35, 'tabB_1': 36
        }

    # =========================================================================
    # PAGE 1: TITLE PAGE
    # =========================================================================
    story.append(sp(12))
    story.append(p("SRI LANKA INSTITUTE OF INFORMATION TECHNOLOGY", ParagraphStyle('SLIITHead', fontName='Helvetica-Bold', fontSize=14, leading=17, alignment=1, textColor=PRIMARY)))
    story.append(p("FACULTY OF COMPUTING | DEPARTMENT OF COMPUTER SCIENCE &amp; SOFTWARE ENGINEERING", ParagraphStyle('DeptHead', fontName='Helvetica', fontSize=9, leading=12, alignment=1, textColor=SECONDARY)))
    story.append(sp(18))

    story.append(p("COMPREHENSIVE FINAL GROUP RESEARCH DISSERTATION", ParagraphStyle('DocType', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1, textColor=ACCENT)))
    story.append(sp(10))

    story.append(p("AI-DRIVEN RECRUITMENT ECOSYSTEM FOR INTELLIGENT JOB MATCHING AND PREDICTIVE CAREER DEVELOPMENT", ParagraphStyle('ProjTitleStyle', fontName='Helvetica-Bold', fontSize=18, leading=23, alignment=1, textColor=PRIMARY)))
    story.append(sp(8))
    story.append(p("An Integrated Event-Driven Multi-Microservice Platform Unifying Boundary-Guarded Resume Screening, Multi-Modal Technical Interviewing, Listwise Candidate Ranking, and Closed-Loop Skill Gap Remediation", ParagraphStyle('ProjSubStyle', fontName='Helvetica', fontSize=10.5, leading=14.5, alignment=1, textColor=SECONDARY)))
    story.append(sp(18))

    team_data = [
        [p("<b>Student Name</b>", body_style), p("<b>Student ID</b>", body_style), p("<b>Assigned Research Component</b>", body_style)],
        [p("<b>D. T. D. Perera</b>", body_style), p("IT22089236", body_bold), p("Component 1: Automated Semantic Resume Screening &amp; Role Classification", body_style)],
        [p("<b>Dulnith K. D.</b>", body_style), p("IT22094872", body_bold), p("Component 2: Autonomous Multi-Modal Technical Interview System", body_style)],
        [p("<b>K. G. Savinda N. Perera</b>", body_style), p("IT22027610", body_bold), p("Component 3: Candidate Suitability Scoring &amp; Listwise Ranking Engine", body_style)],
        [p("<b>Yenura S. Karunanayaka</b>", body_style), p("IT22306272", body_bold), p("Component 4: Skill Gap Diagnostics &amp; Career Pathfinding System", body_style)]
    ]
    team_table = Table(team_data, colWidths=[125, 80, 282])
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(team_table)
    story.append(sp(12))

    meta_info_data = [
        [p("<b>Research Group Identifier:</b>", body_style), p("R26-IT-148", body_bold)],
        [p("<b>Academic Program:</b>", body_style), p("B.Sc. (Hons) in Information Technology Specializing in Software Engineering", body_style)],
        [p("<b>Academic Year &amp; Semester:</b>", body_style), p("Year 4, Semester 2 (Comprehensive Final Dissertation)", body_style)],
        [p("<b>Academic Institution:</b>", body_style), p("Sri Lanka Institute of Information Technology (SLIIT), Malabe, Sri Lanka", body_style)],
        [p("<b>Date of Submission:</b>", body_style), p("October 2026", body_style)]
    ]
    meta_info_table = Table(meta_info_data, colWidths=[170, 317])
    meta_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_info_table)
    story.append(sp(10))
    story.append(p("<i>A dissertation draft submitted in partial fulfillment of the requirements for the degree of Bachelor of Science (Honours) in Information Technology at the Sri Lanka Institute of Information Technology.</i>", caption_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: DECLARATION OF ORIGINALITY
    # =========================================================================
    story.append(p("DECLARATION OF ORIGINALITY", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))
    story.append(p("We hereby declare that this dissertation titled <b>'AI-Driven Recruitment Ecosystem for Intelligent Job Matching and Predictive Career Development'</b> is the authentic record of original research and software development carried out by our research group under identifier <b>R26-IT-148</b> in partial fulfillment of the requirements for the Bachelor of Science (Honours) in Information Technology degree at the Sri Lanka Institute of Information Technology (SLIIT)."))
    story.append(p("We confirm that the intellectual work, system architectures, mathematical formulations, and source code presented in this report have not been submitted previously in whole or in part for any other academic degree, diploma, or qualification at this or any other tertiary institution."))
    story.append(p("All empirical results, machine learning evaluation figures, accuracy metrics, latency measurements, and citations documented in this dissertation are authentic and verified against active system codebases without fabrication. Where secondary literature, foundation models, or third-party libraries have been utilized, they have been comprehensively acknowledged in the references section."))
    story.append(sp(8))

    cand_dec_data = [
        [p("<b>Student Name</b>", body_style), p("<b>Student ID</b>", body_style), p("<b>Signature</b>", body_style), p("<b>Date</b>", body_style)],
        [p("<b>D. T. D. Perera</b>", body_style), p("IT22089236", body_style), p("......................................", body_style), p("October 10, 2026", body_style)],
        [p("<b>Dulnith K. D.</b>", body_style), p("IT22094872", body_style), p("......................................", body_style), p("October 10, 2026", body_style)],
        [p("<b>K. G. Savinda N. Perera</b>", body_style), p("IT22027610", body_style), p("......................................", body_style), p("October 10, 2026", body_style)],
        [p("<b>Yenura S. Karunanayaka</b>", body_style), p("IT22306272", body_style), p("......................................", body_style), p("October 10, 2026", body_style)]
    ]
    cand_dec_table = Table(cand_dec_data, colWidths=[130, 85, 160, 112])
    cand_dec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(cand_dec_table)
    story.append(sp(12))

    story.append(p("SUPERVISOR ENDORSEMENT", h1_style))
    story.append(p("This is to certify that this research dissertation titled <b>'AI-Driven Recruitment Ecosystem for Intelligent Job Matching and Predictive Career Development'</b> is a bona fide record of authentic research work carried out by research group <b>R26-IT-148</b> under our direct supervision in the Faculty of Computing, Sri Lanka Institute of Information Technology."))
    story.append(sp(10))

    sup_sign_data = [
        [p("<b>Research Supervisor:</b>", body_style), p("<b>Co-Supervisor:</b>", body_style)],
        [p("Signature: ......................................................", body_style), p("Signature: ......................................................", body_style)],
        [p("Date: .............................................................", body_style), p("Date: .............................................................", body_style)],
        [p("Department of Computer Science &amp; Software Eng.", body_style), p("Department of Computer Science &amp; Software Eng.", body_style)],
        [p("Faculty of Computing, SLIIT", body_style), p("Faculty of Computing, SLIIT", body_style)]
    ]
    sup_sign_table = Table(sup_sign_data, colWidths=[243, 244])
    sup_sign_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(sup_sign_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: EXECUTIVE ABSTRACT
    # =========================================================================
    story.append(p("EXECUTIVE ABSTRACT", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))
    story.append(p("Modern enterprise technical recruitment operates under severe structural friction. Legacy Applicant Tracking Systems (ATS) rely on brittle substring matching that prematurely rejects qualified non-traditional applicants while admitting opportunistic candidates who exploit keyword-stuffing tactics. Furthermore, technical assessment funnels function as disjointed, uncalibrated stages - combining independent resume filters, subjective interviews, and ad-hoc spreadsheets without mathematical justification. Most critically, unsuccessful applicants encounter a terminal <i>rejection dead-end</i>, receiving cold, automated rejections devoid of diagnostic feedback, thereby destroying candidate goodwill and wasting critical assessment telemetry."))
    story.append(p("To resolve these industry challenges, this dissertation presents <b>RecruitAI</b> (Research Identifier: <b>R26-IT-148</b>), an event-driven, multi-microservice artificial intelligence recruitment ecosystem that transforms candidate assessment into an intelligent, fair, and predictive career progression pipeline. Operating across four decoupled FastAPI microservices running on dedicated TCP ports (8001-8004) orchestrated by a unified API Gateway (Port 8000), RecruitAI unifies four specialized analytical pillars:"))
    story.append(b("• <b>Component 1 (Port 8001 - Lead: D. T. D. Perera, IT22089236):</b> Ingests heterogeneous resumes via layout-aware line extraction, extracts 400+ technical entities via boundary-guarded Named Entity Recognition, resolves overlapping tenure via formal interval union algebra, decouples degree level from discipline relevance, and classifies specialization across 20 canonical IT roles with balanced multinomial Logistic Regression (<b>87.42% accuracy</b>, <b>92.47% macro-F1</b>, <b>2.4 ms</b> latency)."))
    story.append(b("• <b>Component 2 (Port 8002 - Lead: Dulnith K. D., IT22094872):</b> Conducts autonomous multi-modal technical interviews, dynamically retrieving contextual questions from an 18,700-item repository via RAIGS, transcribing verbal responses via Whisper STT (<b>7.20% WER</b>), scoring conceptual depth via Sentence-BERT (<b>r = 0.884</b> against human rubrics), and safely executing candidate code within an AST-secured Python sandbox (<b>100% intercept</b> on 30 exploits)."))
    story.append(b("• <b>Component 3 (Port 8003 - Lead: K. G. Savinda N. Perera, IT22027610):</b> Unifies CV and interview vectors through Multi-Attribute Utility Theory (linear CSS = 0.40 S_cv + 0.60 S_int) with soft prerequisite gating, benchmarks rankings against listwise LightGBM LambdaMART (<b>NDCG@1 = 0.9784</b>, <b>NDCG@5 = 0.9473</b>, <b>MAP = 0.9798</b>), and enforces statutory demographic parity (<b>Delta_DP = 0.008</b>, <b>DIR = 0.941</b>)."))
    story.append(b("• <b>Component 4 (Port 8004 - Lead: Yenura S. Karunanayaka, IT22306272):</b> Closes the rejection dead-end by routing 100% of unshortlisted applicants into diagnostic skill gap analysis, predicting hireability readiness via a 67-feature GBDT ensemble (<b>91.50% accuracy</b>, <b>0.9763 ROC-AUC</b>), scheduling paced learning roadmaps (2 skills/month) across 47 curated courses, and navigating internal talent mobility via a Directed Acyclic Graph (DAG) career lattice."))
    story.append(p("The integrated platform reduces enterprise time-to-hire from 42 days to <b>8.5 days</b> (a 79.8% acceleration), lowers recruiter manual screening hours by <b>84.5%</b>, and achieves an end-to-end multi-microservice processing latency of <b>151.35 ms</b>, establishing a new benchmark for auditable, ethical, and closed-loop enterprise talent acquisition."))
    story.append(sp(6))
    story.append(p("<b>Keywords:</b> Artificial Intelligence in Recruitment, Applicant Tracking Systems, Named Entity Recognition, Speech-to-Text, Learning-to-Rank, LambdaMART, Skill Gap Diagnostics, GBDT, Career Mobility DAG, Algorithmic Fairness, EU AI Act, RecruitAI.", body_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: ACKNOWLEDGEMENTS & DEDICATION
    # =========================================================================
    story.append(p("ACKNOWLEDGEMENTS", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))
    story.append(p("First and foremost, we express our profound gratitude to the Almighty for granting us the intellect, resilience, and unity of purpose required to complete this comprehensive final year research dissertation."))
    story.append(p("We wish to convey our deepest academic gratitude to our research supervisor and co-supervisor at the Faculty of Computing, Sri Lanka Institute of Information Technology (SLIIT). Their invaluable mentorship, intellectual rigor, continuous constructive critiques, and methodological guidance throughout the architecture formulation, model validation, and leakage auditing stages were instrumental in elevating our research to international publication standards."))
    story.append(p("Our sincere appreciation extends to the Dean of the Faculty of Computing, the Head of the Department of Computer Science &amp; Software Engineering, and the entire academic and laboratory staff of SLIIT for providing the state-of-the-art computational infrastructure, high-performance computing clusters, and scholarly environment essential for carrying out this intensive machine learning research."))
    story.append(p("We commend the exceptional synergy, mutual trust, and unwavering dedication demonstrated by every member of Research Group <b>R26-IT-148</b>: <b>D. T. D. Perera (IT22089236)</b>, <b>Dulnith K. D. (IT22094872)</b>, <b>K. G. Savinda N. Perera (IT22027610)</b>, and <b>Yenura S. Karunanayaka (IT22306272)</b>. The seamless integration of four autonomous microservices into a unified platform stands as a testament to our collective commitment to engineering excellence."))
    story.append(p("Finally, we dedicate our deepest and most heartfelt debt of gratitude to our parents, guardians, and families. Their selfless sacrifices, unconditional love, patience, and unwavering moral support throughout our undergraduate journey have been our greatest source of inspiration."))
    story.append(sp(16))
    story.append(p("DEDICATION", h1_style))
    story.append(p("<i>This dissertation is dedicated to all future software engineers, researchers, and aspiring job seekers who deserve transparent, fair, and constructive recruitment pathways that recognize authentic potential and foster lifelong learning.</i>", caption_style))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: TABLE OF CONTENTS (Single Page Elegant Layout)
    # =========================================================================
    story.append(p("TABLE OF CONTENTS", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    toc_sub_style = ParagraphStyle(
        'TOC_Sub', parent=body_style,
        fontName='Helvetica', fontSize=8.5, leading=11,
        leftIndent=15, textColor=DARK_TEXT
    )

    toc_data = [
        [p("<b>Chapter / Section Title</b>", body_style), p("<b>Page</b>", body_style)],
        [p("Declaration of Originality and Supervisor Endorsement", body_style), p("ii", body_style)],
        [p("Executive Abstract", body_style), p("iii", body_style)],
        [p("Acknowledgements and Dedication", body_style), p("iv", body_style)],
        [p("Table of Contents", body_style), p("v", body_style)],
        [p("List of Figures and List of Tables", body_style), p("vi", body_style)],
        [p("List of Abbreviations and Acronyms", body_style), p("vii", body_style)],
        [p("<b>Chapter 1: Introduction and Ecosystem Context</b>", body_bold), p(f"<b>{page_map.get('ch1', 8)}</b>", body_bold)],
        [p("<b>Chapter 2: Literature Review and Theoretical Foundations</b>", body_bold), p(f"<b>{page_map.get('ch2', 12)}</b>", body_bold)],
        [p("<b>Chapter 3: Overall System Architecture and Inter-Service Integration</b>", body_bold), p(f"<b>{page_map.get('ch3', 15)}</b>", body_bold)],
        [p("<b>Chapter 4: Detailed Component Formulations and Mathematical Models</b>", body_bold), p(f"<b>{page_map.get('ch4', 18)}</b>", body_bold)],
        [p("• 4.1 Component 1: Resume Screening &amp; Role Classification (D. T. D. Perera)", toc_sub_style), p(f"{page_map.get('ch4', 18)}", body_style)],
        [p("• 4.2 Component 2: Autonomous Multi-Modal Technical Interview System (Dulnith K. D.)", toc_sub_style), p(f"{page_map.get('ch4', 18)+1}", body_style)],
        [p("• 4.3 Component 3: Candidate Scoring &amp; Listwise Ranking Engine (K. G. Savinda N. Perera)", toc_sub_style), p(f"{page_map.get('ch4', 18)+2}", body_style)],
        [p("• 4.4 Component 4: Skill Gap Diagnostics &amp; Career Pathfinding (Yenura S. Karunanayaka)", toc_sub_style), p(f"{page_map.get('ch4', 18)+3}", body_style)],
        [p("<b>Chapter 5: Implementation, Engineering Stack, and Deployment</b>", body_bold), p(f"<b>{page_map.get('ch5', 22)}</b>", body_bold)],
        [p("<b>Chapter 6: Empirical Results, Validation, and Integrated Benchmarking</b>", body_bold), p(f"<b>{page_map.get('ch6', 24)}</b>", body_bold)],
        [p("<b>Chapter 7: Ethical Considerations, Fairness, and Regulatory Compliance</b>", body_bold), p(f"<b>{page_map.get('ch7', 28)}</b>", body_bold)],
        [p("<b>Chapter 8: Conclusion and Future Research Trajectories</b>", body_bold), p(f"<b>{page_map.get('ch8', 31)}</b>", body_bold)],
        [p("<b>References</b>", body_bold), p(f"<b>{page_map.get('ref', 33)}</b>", body_bold)],
        [p("<b>Appendix A: Inter-Service REST API Specifications and JSON Contracts</b>", body_bold), p(f"<b>{page_map.get('appA', 35)}</b>", body_bold)],
        [p("<b>Appendix B: Research Group Contribution Matrix and Supervisory Sign-Off</b>", body_bold), p(f"<b>{page_map.get('appB', 36)}</b>", body_bold)]
    ]
    toc_table = Table(toc_data, colWidths=[437, 50])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.2),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: LIST OF FIGURES & LIST OF TABLES
    # =========================================================================
    story.append(p("LIST OF FIGURES", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=8))

    lof_data = [
        [p("<b>Figure Number &amp; Descriptive Title</b>", body_style), p("<b>Page</b>", body_style)],
        [p("Figure 1.1: Multi-Microservice Architecture of the Integrated RecruitAI Ecosystem (Project: R26-IT-148)", body_style), p(f"{page_map.get('fig1_1', 9)}", body_style)],
        [p("Figure 1.2: End-to-End RecruitAI Candidate Lifecycle, Analytical State Flow, and Remedial Career Routing", body_style), p(f"{page_map.get('fig1_2', 10)}", body_style)],
        [p("Figure 4.1: Multi-Stage Document Ingestion, Regex Look-Around Shielding, and Tri-Pillar Scoring Pipeline", body_style), p(f"{page_map.get('fig4_1', 18)}", body_style)],
        [p("Figure 4.2: Chronological Interval Union Algebra for Exact Experience Tenure Disambiguation", body_style), p(f"{page_map.get('fig4_2', 19)}", body_style)],
        [p("Figure 6.1: Forensic Replication Exposing Artificial Generalization Collapse in Synthetic Benchmark Classifiers", body_style), p(f"{page_map.get('fig6_1', 24)}", body_style)],
        [p("Figure 6.2: Multi-Model Benchmark Comparison: Accuracy, Precision, Recall, Macro F1, and Latency Across 20 Roles", body_style), p(f"{page_map.get('fig6_2', 25)}", body_style)],
        [p("Figure 6.3: End-to-End System Pipeline Latency Breakdown Across Microservice Processing Stages (151.35 ms total)", body_style), p(f"{page_map.get('fig6_3', 26)}", body_style)]
    ]
    lof_table = Table(lof_data, colWidths=[437, 50])
    lof_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(lof_table)
    story.append(sp(10))

    story.append(p("LIST OF TABLES", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=8))

    lot_data = [
        [p("<b>Table Number &amp; Descriptive Title</b>", body_style), p("<b>Page</b>", body_style)],
        [p("Table 1.1: Research Group Member Allocation, Responsibilities, and Research Component Matrix", body_style), p(f"{page_map.get('tab1_1', 11)}", body_style)],
        [p("Table 2.1: Cross-Component Research Gap Synthesis and Theoretical Foundations", body_style), p(f"{page_map.get('tab2_1', 14)}", body_style)],
        [p("Table 3.1: Inter-Microservice REST Communication Specifications and Network Protocols", body_style), p(f"{page_map.get('tab3_1', 17)}", body_style)],
        [p("Table 5.1: Comprehensive Test Suite Distribution and Pass Rates Across All Four Microservices (665 Tests)", body_style), p(f"{page_map.get('tab5_1', 23)}", body_style)],
        [p("Table 6.1: Cross-Component Empirical Performance Benchmarks Across All Four Research Pillars", body_style), p(f"{page_map.get('tab6_1', 25)}", body_style)],
        [p("Table 6.2: End-to-End System Processing Latency Profile Across All Processing Stages (151.35 ms)", body_style), p(f"{page_map.get('tab6_2', 26)}", body_style)],
        [p("Table 6.3: Multi-Candidate End-to-End Enterprise Scenario Walkthrough and Remedial Trajectories", body_style), p(f"{page_map.get('tab6_3', 27)}", body_style)],
        [p("Table 7.1: Regulatory Compliance and Statutory Audit Matrix across International Governance Frameworks", body_style), p(f"{page_map.get('tab7_1', 29)}", body_style)],
        [p("Table A.1: Inter-Service REST API Specifications and Network Payload Contracts", body_style), p(f"{page_map.get('tabA_1', 35)}", body_style)],
        [p("Table B.1: Research Group Member Allocation, Component Ownership, and Contribution Matrix", body_style), p(f"{page_map.get('tabB_1', 36)}", body_style)]
    ]
    lot_table = Table(lot_data, colWidths=[437, 50])
    lot_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(lot_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: LIST OF ABBREVIATIONS AND ACRONYMS
    # =========================================================================
    story.append(p("LIST OF ABBREVIATIONS AND ACRONYMS", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=8))

    abbr_data = [
        [p("<b>Acronym</b>", body_style), p("<b>Full Technical Description</b>", body_style), p("<b>Acronym</b>", body_style), p("<b>Full Technical Description</b>", body_style)],
        [p("<b>AEDT</b>", body_style), p("Automated Employment Decision Tool", body_style), p("<b>LLM</b>", body_style), p("Large Language Model", body_style)],
        [p("<b>API</b>", body_style), p("Application Programming Interface", body_style), p("<b>LTR</b>", body_style), p("Learning-to-Rank", body_style)],
        [p("<b>ASGI</b>", body_style), p("Asynchronous Server Gateway Interface", body_style), p("<b>MAP</b>", body_style), p("Mean Average Precision", body_style)],
        [p("<b>AST</b>", body_style), p("Abstract Syntax Tree", body_style), p("<b>MAUT</b>", body_style), p("Multi-Attribute Utility Theory", body_style)],
        [p("<b>ATS</b>", body_style), p("Applicant Tracking System", body_style), p("<b>NDCG</b>", body_style), p("Normalized Discounted Cumulative Gain", body_style)],
        [p("<b>BERT</b>", body_style), p("Bidirectional Encoder Representations from Transformers", body_style), p("<b>NER</b>", body_style), p("Named Entity Recognition", body_style)],
        [p("<b>CSS</b>", body_style), p("Composite Suitability Score", body_style), p("<b>NLP</b>", body_style), p("Natural Language Processing", body_style)],
        [p("<b>CV</b>", body_style), p("Curriculum Vitae", body_style), p("<b>PII</b>", body_style), p("Personally Identifiable Information", body_style)],
        [p("<b>DAG</b>", body_style), p("Directed Acyclic Graph", body_style), p("<b>RAIGS</b>", body_style), p("Retrieval-Augmented Ingestion and Generation System", body_style)],
        [p("<b>DIR</b>", body_style), p("Disparate Impact Ratio (80% Rule)", body_style), p("<b>REST</b>", body_style), p("Representational State Transfer", body_style)],
        [p("<b>EEOC</b>", body_style), p("Equal Employment Opportunity Commission", body_style), p("<b>RLHF</b>", body_style), p("Reinforcement Learning from Human Feedback", body_style)],
        [p("<b>FPR</b>", body_style), p("False Positive Rate", body_style), p("<b>ROC-AUC</b>", body_style), p("Receiver Operating Characteristic - Area Under Curve", body_style)],
        [p("<b>GBDT</b>", body_style), p("Gradient Boosted Decision Trees", body_style), p("<b>SBERT</b>", body_style), p("Sentence-BERT (Bi-Encoder Embeddings)", body_style)],
        [p("<b>GDPR</b>", body_style), p("General Data Protection Regulation", body_style), p("<b>SHAP</b>", body_style), p("SHapley Additive exPlanations", body_style)],
        [p("<b>HTML</b>", body_style), p("HyperText Markup Language", body_style), p("<b>SPA</b>", body_style), p("Single Page Application", body_style)],
        [p("<b>HTTP</b>", body_style), p("Hypertext Transfer Protocol", body_style), p("<b>STT</b>", body_style), p("Speech-to-Text", body_style)],
        [p("<b>IR</b>", body_style), p("Information Retrieval", body_style), p("<b>TF-IDF</b>", body_style), p("Term Frequency - Inverse Document Frequency", body_style)],
        [p("<b>JSON</b>", body_style), p("JavaScript Object Notation", body_style), p("<b>TPR</b>", body_style), p("True Positive Rate", body_style)],
        [p("<b>JWT</b>", body_style), p("JSON Web Token", body_style), p("<b>TTL</b>", body_style), p("Time-To-Live", body_style)],
        [p("<b>LambdaMART</b>", body_style), p("Lambda-Gradient Multiple Additive Regression Trees", body_style), p("<b>WER</b>", body_style), p("Word Error Rate", body_style)]
    ]
    abbr_table = Table(abbr_data, colWidths=[65, 178, 65, 179])
    abbr_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(abbr_table)
    story.append(PageBreak())
