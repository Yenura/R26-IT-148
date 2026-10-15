import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib import colors
from group_builder.styles import clean_xml, PRINTABLE_WIDTH
from group_builder.canvas_helper import PageTracker

def append_group_front_matter(story, styles, page_dict=None, tracker=None):
    if page_dict is None:
        page_dict = {}

    def get_pg(key, default=""):
        return page_dict.get(key, default)

    def track(key):
        if tracker is not None:
            story.append(PageTracker(key, tracker))

    body = styles['ThesisBody']
    caption = styles['FigureCaption']
    single_body = styles['SingleBody']

    # -------------------------------------------------------------------------
    # 1. TITLE PAGE (NO PAGE NUMBER)
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("AI-DRIVEN RECRUITMENT ECOSYSTEM FOR INTELLIGENT JOB MATCHING AND PREDICTIVE CAREER DEVELOPMENT", styles['CoverProjectTitle']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("COMMON INTEGRATED SOLUTION REPORT", styles['CoverReportHeading']))
    story.append(Spacer(1, 10))

    # Team Member Table (3 Members - Dulnith K. D. is excluded as instructed)
    member_data = [
        [Paragraph("<b>Team member</b>", styles['TableCellCenterBold']), Paragraph("<b>Student ID</b>", styles['TableCellCenterBold']), Paragraph("<b>Individual component</b>", styles['TableCellCenterBold'])],
        [Paragraph("D. T. D. Perera", styles['TableCellBold']), Paragraph("IT22089236", styles['TableCellCenter']), Paragraph("Component 1: Automated Semantic Resume Screening and IT Job Role Classification", styles['TableCell'])],
        [Paragraph("Yenura S. Karunanayaka", styles['TableCellBold']), Paragraph("IT22306272", styles['TableCellCenter']), Paragraph("Component 2: Autonomous Technical Interview Evaluation", styles['TableCell'])],
        [Paragraph("K. G. Savinda N. Perera", styles['TableCellBold']), Paragraph("IT22027610", styles['TableCellCenter']), Paragraph("Component 3: Candidate Suitability Scoring and Listwise Ranking<br/>Component 4: Predictive Skill Gap Diagnostics and Career Pathfinding", styles['TableCell'])],
    ]
    member_tab = Table(member_data, colWidths=[110, 75, 226])
    member_tab.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#000000")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#000000")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAEAEA")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(member_tab)
    story.append(Spacer(1, 24))

    story.append(Paragraph("Report submitted in partial fulfilment of the requirements for the", styles['CoverSubmissionNote']))
    story.append(Paragraph("Bachelor of Science (Honours) in Information Technology", styles['CoverDegreeHeading']))
    story.append(Paragraph("Specialising in Information Technology", styles['CoverSpecialisation']))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Department of Information Technology", styles['CoverDepartment']))
    story.append(Paragraph("Sri Lanka Institute of Information Technology", styles['CoverInstitution']))
    story.append(Paragraph("Sri Lanka", styles['CoverLocation']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Document Publication Portal: https://r26-it-148-website.yenura02.workers.dev/", styles['CoverSubmissionNote']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("October 2026", styles['CoverDate']))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 2. DECLARATION AND SUPERVISOR CERTIFICATION (Page i)
    # -------------------------------------------------------------------------
    track('dec')
    story.append(Paragraph("DECLARATION AND SUPERVISOR CERTIFICATION", styles['ChapterHeading']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Candidate declaration.</b> We declare that this common report is our own work and does not incorporate, without acknowledgement, material previously submitted for a degree or diploma at any university or institute of higher learning. To the best of our knowledge, it contains no material previously published or written by another person except where acknowledgement is made in the text. We grant the Sri Lanka Institute of Information Technology the non-exclusive right to reproduce and distribute this report, in whole or in part, in print, electronic, or other media, while retaining the right to use the content in future work.", single_body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Academic integrity and AI disclosure.</b> We have disclosed all use of generative AI and other automated tools in accordance with the module policy. We remain responsible for the accuracy, originality, citations, code, data, analyses, and conclusions in this report.", single_body))
    story.append(Spacer(1, 10))

    fig_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    sig1_path = os.path.join(fig_dir, "sig_d_t_d_perera.png")
    sig2_path = os.path.join(fig_dir, "sig_yenura.png")
    sig3_path = os.path.join(fig_dir, "sig_savinda.png")

    sig_perera = RLImage(sig1_path, width=65, height=24)
    sig_yenura = RLImage(sig2_path, width=42, height=26)
    sig_savinda = RLImage(sig3_path, width=52, height=25)

    cand_table_data = [
        [Paragraph("<b>Student name</b>", styles['TableCellCenterBold']), Paragraph("<b>Student ID</b>", styles['TableCellCenterBold']), Paragraph("<b>Signature</b>", styles['TableCellCenterBold']), Paragraph("<b>Date</b>", styles['TableCellCenterBold'])],
        [Paragraph("D. T. D. Perera", styles['TableCell']), Paragraph("IT22089236", styles['TableCellCenter']), sig_perera, Paragraph("10 October 2026", styles['TableCellCenter'])],
        [Paragraph("Yenura S. Karunanayaka", styles['TableCell']), Paragraph("IT22306272", styles['TableCellCenter']), sig_yenura, Paragraph("10 October 2026", styles['TableCellCenter'])],
        [Paragraph("K. G. Savinda N. Perera", styles['TableCell']), Paragraph("IT22027610", styles['TableCellCenter']), sig_savinda, Paragraph("10 October 2026", styles['TableCellCenter'])],
    ]
    cand_tab = Table(cand_table_data, colWidths=[125, 75, 120, 91])
    cand_tab.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#000000")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#000000")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAEAEA")),
        ('ALIGN', (2,1), (2,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(cand_tab)
    story.append(Spacer(1, 16))

    story.append(Paragraph("<b>Supervisor certification.</b> The above candidates carried out this research project under my supervision.", single_body))
    story.append(Spacer(1, 8))

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
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(sup_table)
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 3. ABSTRACT (Page ii)
    # -------------------------------------------------------------------------
    track('abs')
    story.append(Paragraph("ABSTRACT", styles['ChapterHeading']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Modern corporate recruitment funnels are paralyzed by high candidate application volumes, extreme specialization, and severe information asymmetry. Legacy Applicant Tracking Systems depend on brittle keyword filters that prematurely eliminate qualified non-keyword candidates while rewarding opportunistic keyword stuffing. Furthermore, conventional hiring pipelines operate as fragmented, terminating funnels: candidates transition through disconnected tools, disparate scores are aggregated without scientific calibration, and rejected applicants receive uninformative rejection emails devoid of actionable diagnostic guidance.", single_body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("This Common Integrated Solution Report documents <b>RecruitAI</b> (Research Project Identifier: <b>R26-IT-148</b>), an end-to-end, multi-modal, artificial intelligence-driven technical recruitment and predictive career development ecosystem. Built as an event-driven cluster of four interoperable FastAPI microservices on dedicated TCP ports (8001-8004) alongside a reactive React dashboard, RecruitAI addresses the hiring crisis across four integrated stages: (1) <i>Component 1 (Port 8001):</i> Automated Semantic Resume Screening and IT Job Role Classification converts unstructured PDF/DOCX resumes into auditable profiles using boundary-guarded NER (400+ skills), interval-union tenure algebra, and balanced 20-role multinomial logistic regression (87.42% accuracy, 92.47% macro F1, 2.4 ms inference); (2) <i>Component 2 (Port 8002):</i> Autonomous Technical Interview Evaluation conducts role-aligned technical interviews, transcribing speech (7.2% WER), grading conceptual comprehension using Sentence-BERT (r = 0.884 correlation with human panels), and evaluating Python code in an AST sandbox; (3) <i>Component 3 (Port 8003):</i> Candidate Suitability Scoring and Listwise Ranking Engine fuses multi-pillar CV and interview vectors using Multi-Attribute Utility Theory and LambdaMART learning-to-rank (NDCG@5 = 0.9473) with demographic parity auditing; and (4) <i>Component 4 (Port 8004):</i> Skill Gap Diagnostics and Career Pathfinding System transforms rejection into career progression by predicting hireability via a 67-feature GBDT model (ROC-AUC = 0.9763) and synthesizing milestone-based learning curricula across a Directed Acyclic Graph career lattice.", single_body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Evaluated across 4,000 real-world technical CVs and 50 end-to-end multi-modal interview sessions, RecruitAI achieves sub-160ms screening triage, reduces first-round screening hours by 85%, and provides an equitable, explainable closed-loop hiring solution.", single_body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Keywords:</b> recruitment intelligence, applicant tracking, multi-modal technical interviews, listwise candidate ranking, skill gap pathfinding, RecruitAI.", single_body))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 4. ACKNOWLEDGEMENTS (Page iii)
    # -------------------------------------------------------------------------
    track('ack')
    story.append(Paragraph("ACKNOWLEDGEMENTS", styles['ChapterHeading']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("First and foremost, we offer our profound gratitude to the Almighty for granting our research team the intellectual wisdom, endurance, and unity to complete this collaborative undergraduate research initiative.", body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("We express our deepest and most sincere gratitude to our research supervisor, Dr. Pradeep Kalansooriya, and co-supervisor, Ms. K. V. S. Dilrukshi, of the Faculty of Computing, Sri Lanka Institute of Information Technology (SLIIT). Their insightful technical mentorship, continuous constructive critique, and rigorous guidance through architecture design, microservice contract definition, model training, and integration testing were invaluable.", body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("We extend our sincere appreciation to the Dean of the Faculty of Computing, the Head of the Department of Information Technology, and the academic and technical staff of SLIIT for providing the state-of-the-art computational infrastructure, network laboratory facilities, and supportive academic environment essential for distributed microservice engineering.", body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("We also acknowledge our industry advisory partners and technical recruiters across software engineering enterprises in Sri Lanka and multinational technology centers who participated in stakeholder requirement gathering, rubric evaluations, and end-to-end user validation trials.", body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("All collaborative research deliverables, architectural specifications, presentation slide decks, and project reports are publicly published at our official document publication portal: https://r26-it-148-website.yenura02.workers.dev/.", body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Finally, we express our heartfelt appreciation to our parents, families, and colleagues for their continuous moral support, patience, and encouragement throughout this capstone research journey. We dedicate this common dissertation to them.", body))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 5. TABLE OF CONTENTS (Pages iv, v, vi)
    # -------------------------------------------------------------------------
    track('toc')
    story.append(Paragraph("TABLE OF CONTENTS", styles['ChapterHeading']))
    story.append(Spacer(1, 6))

    toc_title_style = styles['TableCellBold']
    toc_text_style = styles['TableCell']
    toc_page_style = styles['TableCellCenterBold']

    toc_rows = [
        [Paragraph("<b>Chapter / Section Title</b>", toc_title_style), Paragraph("<b>Page</b>", toc_page_style)],
        [Paragraph("Declaration and Supervisor Certification", toc_text_style), Paragraph(get_pg("dec", "i"), toc_page_style)],
        [Paragraph("Abstract", toc_text_style), Paragraph(get_pg("abs", "ii"), toc_page_style)],
        [Paragraph("Acknowledgements", toc_text_style), Paragraph(get_pg("ack", "iii"), toc_page_style)],
        [Paragraph("Table of Contents", toc_text_style), Paragraph(get_pg("toc", "iv"), toc_page_style)],
        [Paragraph("List of Figures", toc_text_style), Paragraph(get_pg("lof", "vii"), toc_page_style)],
        [Paragraph("List of Tables", toc_text_style), Paragraph(get_pg("lot", "viii"), toc_page_style)],
        [Paragraph("List of Abbreviations", toc_text_style), Paragraph(get_pg("loa", "ix"), toc_page_style)],

        [Paragraph("<b>1 INTRODUCTION AND PROJECT CONTEXT</b>", toc_title_style), Paragraph(get_pg("ch1", "1"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.1 Background and context", toc_text_style), Paragraph(get_pg("sec1_1", "1"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.2 Stakeholders and user needs", toc_text_style), Paragraph(get_pg("sec1_2", "3"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.3 Alignment with the Sustainable Development Goals", toc_text_style), Paragraph(get_pg("sec1_3", "5"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.4 Purpose and scope of the common report", toc_text_style), Paragraph(get_pg("sec1_4", "6"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.5 Research questions and hypotheses of the integrated platform", toc_text_style), Paragraph(get_pg("sec1_5", "7"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.6 Summary of principal technological innovations", toc_text_style), Paragraph(get_pg("sec1_6", "8"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.7 Organisation and structure of the common report", toc_text_style), Paragraph(get_pg("sec1_7", "9"), toc_page_style)],

        [Paragraph("<b>2 OVERALL PROBLEM DEFINITION AND FOUR SUBPROBLEMS</b>", toc_title_style), Paragraph(get_pg("ch2", "10"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.1 Overall problem definition", toc_text_style), Paragraph(get_pg("sec2_1", "10"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.2 Root causes and overall research gap", toc_text_style), Paragraph(get_pg("sec2_2", "12"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.3 Subproblem and component mapping", toc_text_style), Paragraph(get_pg("sec2_3", "14"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.4 Overall aim and group objectives", toc_text_style), Paragraph(get_pg("sec2_4", "15"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.5 Scope assumptions and constraints", toc_text_style), Paragraph(get_pg("sec2_5", "16"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.6 Theoretical formulation of core failure modes", toc_text_style), Paragraph(get_pg("sec2_6", "17"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.7 Comprehensive benchmark of existing systems", toc_text_style), Paragraph(get_pg("sec2_7", "18"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.8 Empirical baseline audit of legacy failures", toc_text_style), Paragraph(get_pg("sec2_8", "20"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.9 Cognitive screener fatigue and visual attention dynamics", toc_text_style), Paragraph(get_pg("sec2_9", "21"), toc_page_style)],

        [Paragraph("<b>3 OVERALL SOLUTION STRUCTURE</b>", toc_title_style), Paragraph(get_pg("ch3", "21"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.1 Integrated solution overview", toc_text_style), Paragraph(get_pg("sec3_1", "21"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.2 High level architecture", toc_text_style), Paragraph(get_pg("sec3_2", "23"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.3 Component 1 summary", toc_text_style), Paragraph(get_pg("sec3_3", "25"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.4 Component 2 summary", toc_text_style), Paragraph(get_pg("sec3_4", "28"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.5 Component 3 summary", toc_text_style), Paragraph(get_pg("sec3_5", "30"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.6 Component 4 summary", toc_text_style), Paragraph(get_pg("sec3_6", "32"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.7 End to end user and data flow", toc_text_style), Paragraph(get_pg("sec3_7", "34"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.8 Formal mathematical and algorithmic framework", toc_text_style), Paragraph(get_pg("sec3_8", "36"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.9 Architectural trade-off analysis", toc_text_style), Paragraph(get_pg("sec3_9", "39"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.10 Vector embedding spaces and latent geometric representations", toc_text_style), Paragraph(get_pg("sec3_10", "40"), toc_page_style)],

        [Paragraph("<b>4 COMPONENT INTEGRATION AND COHESIVE OPERATION</b>", toc_title_style), Paragraph(get_pg("ch4", "41"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.1 Integration strategy", toc_text_style), Paragraph(get_pg("sec4_1", "41"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.2 Interfaces data contracts and shared models", toc_text_style), Paragraph(get_pg("sec4_2", "42"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.3 Shared nonfunctional requirements", toc_text_style), Paragraph(get_pg("sec4_3", "44"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.4 Integrated workflow and exception handling", toc_text_style), Paragraph(get_pg("sec4_4", "46"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.5 Team contribution and dependency matrix", toc_text_style), Paragraph(get_pg("sec4_5", "48"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.6 Database architecture and distributed document schemas", toc_text_style), Paragraph(get_pg("sec4_6", "50"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.7 Inter-service telemetry and distributed tracing", toc_text_style), Paragraph(get_pg("sec4_7", "52"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.8 Multi-container Docker orchestration and deployment topology", toc_text_style), Paragraph(get_pg("sec4_8", "53"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.9 Distributed resilience patterns circuit breaking and idempotency", toc_text_style), Paragraph(get_pg("sec4_9", "54"), toc_page_style)],

        [Paragraph("<b>5 INTEGRATED IMPLEMENTATION AND PROJECT EXECUTION</b>", toc_title_style), Paragraph(get_pg("ch5", "55"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.1 Common technology stack and infrastructure", toc_text_style), Paragraph(get_pg("sec5_1", "55"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.2 Development and integration process", toc_text_style), Paragraph(get_pg("sec5_2", "57"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.3 Deployment and operational configuration", toc_text_style), Paragraph(get_pg("sec5_3", "59"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.4 Evidence of team execution", toc_text_style), Paragraph(get_pg("sec5_4", "60"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.5 Comprehensive engineering risk management matrix", toc_text_style), Paragraph(get_pg("sec5_5", "61"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.6 CI/CD pipeline and automated verification infrastructure", toc_text_style), Paragraph(get_pg("sec5_6", "63"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.7 Code quality standards and peer review protocols", toc_text_style), Paragraph(get_pg("sec5_7", "64"), toc_page_style)],

        [Paragraph("<b>6 INTEGRATED TESTING EVALUATION AND VALIDATION</b>", toc_title_style), Paragraph(get_pg("ch6", "66"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.1 Evaluation framework and success criteria", toc_text_style), Paragraph(get_pg("sec6_1", "66"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.2 Integration and end to end testing", toc_text_style), Paragraph(get_pg("sec6_2", "68"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.3 Overall results", toc_text_style), Paragraph(get_pg("sec6_3", "70"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.4 Stakeholder and user validation", toc_text_style), Paragraph(get_pg("sec6_4", "73"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.5 Achievement of common objectives", toc_text_style), Paragraph(get_pg("sec6_5", "74"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.6 Integrated limitations and threats", toc_text_style), Paragraph(get_pg("sec6_6", "75"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.7 Concurrency and stress benchmarking", toc_text_style), Paragraph(get_pg("sec6_7", "76"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.8 Demographic parity and disparate impact audit", toc_text_style), Paragraph(get_pg("sec6_8", "78"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.9 End to end operational case studies", toc_text_style), Paragraph(get_pg("sec6_9", "80"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;6.10 Statistical significance testing and hypothesis confirmation", toc_text_style), Paragraph(get_pg("sec6_10", "81"), toc_page_style)],

        [Paragraph("<b>7 COMMERCIALISATION SUSTAINABILITY AND RESPONSIBLE INNOVATION</b>", toc_title_style), Paragraph(get_pg("ch7", "82"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.1 Value proposition and beneficiaries", toc_text_style), Paragraph(get_pg("sec7_1", "82"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.2 Market alternatives and differentiation", toc_text_style), Paragraph(get_pg("sec7_2", "83"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.3 Business model and feasibility", toc_text_style), Paragraph(get_pg("sec7_3", "85"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.4 Adoption intellectual property and compliance", toc_text_style), Paragraph(get_pg("sec7_4", "87"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.5 Sustainable Development Goal contribution", toc_text_style), Paragraph(get_pg("sec7_5", "89"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.6 Detailed 3-year financial model and break-even analysis", toc_text_style), Paragraph(get_pg("sec7_6", "90"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.7 Go-to-market strategy and enterprise pilot roadmap", toc_text_style), Paragraph(get_pg("sec7_7", "92"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.8 Ethical AI governance and longitudinal bias monitoring", toc_text_style), Paragraph(get_pg("sec7_8", "93"), toc_page_style)],

        [Paragraph("<b>8 CONCLUSION AND FUTURE DIRECTIONS</b>", toc_title_style), Paragraph(get_pg("ch8", "94"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.1 Overall conclusion", toc_text_style), Paragraph(get_pg("sec8_1", "94"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.2 Principal integrated contribution", toc_text_style), Paragraph(get_pg("sec8_2", "95"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.3 Future directions", toc_text_style), Paragraph(get_pg("sec8_3", "96"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.4 Critical engineering lessons learned", toc_text_style), Paragraph(get_pg("sec8_4", "97"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.5 Concluding remarks", toc_text_style), Paragraph(get_pg("sec8_5", "98"), toc_page_style)],

        [Paragraph("<b>REFERENCES</b>", toc_title_style), Paragraph(get_pg("refs", "99"), toc_page_style)],
        [Paragraph("<b>APPENDICES</b>", toc_title_style), Paragraph(get_pg("app_a", "102"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Appendix A Integrated interface specification", toc_text_style), Paragraph(get_pg("app_a", "102"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Appendix B Team contribution declaration", toc_text_style), Paragraph(get_pg("app_b", "105"), toc_page_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Appendix C Cloud infrastructure, Docker orchestration, and security hardening", toc_text_style), Paragraph(get_pg("app_c", "107"), toc_page_style)],
    ]

    toc_table = Table(toc_rows, colWidths=[361, 50])
    toc_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#000000")),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # 6. LIST OF FIGURES (Page vi)
    # -------------------------------------------------------------------------
    track('lof')
    story.append(Paragraph("LIST OF FIGURES", styles['ChapterHeading']))
    story.append(Spacer(1, 8))

    lof_rows = [
        [Paragraph("<b>Figure Number &amp; Title</b>", toc_title_style), Paragraph("<b>Page</b>", toc_page_style)],
        [Paragraph("Figure 3.1: High-Level Microservice Architecture of the Integrated RecruitAI Ecosystem", toc_text_style), Paragraph(get_pg("fig3_1", "23"), toc_page_style)],
        [Paragraph("Figure 3.2: End-to-End Candidate Lifecycle, Analytical State Flow, and Remedial Routing", toc_text_style), Paragraph(get_pg("fig3_2", "34"), toc_page_style)],
        [Paragraph("Figure 3.3: Component 1 Boundary-Guarded NER and Context Look-Around Assertion Shields", toc_text_style), Paragraph(get_pg("fig3_3", "26"), toc_page_style)],
        [Paragraph("Figure 3.4: Component 1 Chronological Interval Union Algebra for Experience Deduplication", toc_text_style), Paragraph(get_pg("fig3_4", "27"), toc_page_style)],
        [Paragraph("Figure 5.1: Microservice Processing Latency and End-to-End Pipeline Execution Profiling", toc_text_style), Paragraph(get_pg("fig5_1", "56"), toc_page_style)],
        [Paragraph("Figure 6.1: Forensic Evaluation of Synthetic Benchmark Leakage vs. Real-World Evaluation", toc_text_style), Paragraph(get_pg("fig6_1", "70"), toc_page_style)],
        [Paragraph("Figure 6.2: Multi-Class Role Classification Performance Across 20 Canonical IT Roles", toc_text_style), Paragraph(get_pg("fig6_2", "71"), toc_page_style)],
        [Paragraph("Figure 6.3: Comparative Benchmark of Machine Learning Architectures (Accuracy vs. Latency)", toc_text_style), Paragraph(get_pg("fig6_3", "72"), toc_page_style)],
        [Paragraph("Figure 6.4: Permutation Feature Importance vs. Deployed Candidate Scoring Weights", toc_text_style), Paragraph(get_pg("fig6_4", "73"), toc_page_style)],
        [Paragraph("Figure 6.5: Cross-Component Empirical Performance Benchmarks Across All Four Microservices", toc_text_style), Paragraph(get_pg("fig6_5", "74"), toc_page_style)],
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
    # 7. LIST OF TABLES (Page vii)
    # -------------------------------------------------------------------------
    track('lot')
    story.append(Paragraph("LIST OF TABLES", styles['ChapterHeading']))
    story.append(Spacer(1, 8))

    lot_rows = [
        [Paragraph("<b>Table Number &amp; Title</b>", toc_title_style), Paragraph("<b>Page</b>", toc_page_style)],
        [Paragraph("Table 1.1: Global Technical Recruitment Funnel Attrition and Bottleneck Metrics", toc_text_style), Paragraph(get_pg("tab1_1", "2"), toc_page_style)],
        [Paragraph("Table 1.2: Comparative Matrix of Principal Technological Innovations Across RecruitAI", toc_text_style), Paragraph(get_pg("tab1_2", "8"), toc_page_style)],
        [Paragraph("Table 2.1: Systematic Mapping of Technical Subproblems to RecruitAI Research Components", toc_text_style), Paragraph(get_pg("tab2_1", "14"), toc_page_style)],
        [Paragraph("Table 2.2: Comprehensive Benchmark of Commercial and Open-Source Systems vs. RecruitAI", toc_text_style), Paragraph(get_pg("tab2_2", "19"), toc_page_style)],
        [Paragraph("Table 3.1: Comprehensive Summary of Component Capabilities, Core Models, and Port Bindings", toc_text_style), Paragraph(get_pg("tab3_1", "22"), toc_page_style)],
        [Paragraph("Table 3.2: Comprehensive Architectural Trade-Off Analysis Across System Design Dimensions", toc_text_style), Paragraph(get_pg("tab3_2", "40"), toc_page_style)],
        [Paragraph("Table 4.1: Inter-Microservice REST API Contracts and Shared JSON Data Payloads", toc_text_style), Paragraph(get_pg("tab4_1", "43"), toc_page_style)],
        [Paragraph("Table 4.2: Shared Non-Functional Requirements, Operational Metrics, and Verification Methods", toc_text_style), Paragraph(get_pg("tab4_2", "45"), toc_page_style)],
        [Paragraph("Table 4.3: Team Responsibility, Component Allocation, and Cross-Service Dependency Matrix", toc_text_style), Paragraph(get_pg("tab4_3", "49"), toc_page_style)],
        [Paragraph("Table 4.4: MongoDB Atlas Collections, Document Schemas, and Indexing Strategies", toc_text_style), Paragraph(get_pg("tab4_4", "51"), toc_page_style)],
        [Paragraph("Table 5.1: Unified Technology Stack, Open-Source Frameworks, and Architectural Rationale", toc_text_style), Paragraph(get_pg("tab5_1", "56"), toc_page_style)],
        [Paragraph("Table 5.2: Agile Sprint Cadence, Collaborative Milestones, and Integration Workflows", toc_text_style), Paragraph(get_pg("tab5_2", "58"), toc_page_style)],
        [Paragraph("Table 5.3: Engineering Risk Management Matrix, Severity Classification, and Mitigation Controls", toc_text_style), Paragraph(get_pg("tab5_3", "62"), toc_page_style)],
        [Paragraph("Table 6.1: Integrated Multi-Component System Testing Suite Breakdown (320 Total Tests)", toc_text_style), Paragraph(get_pg("tab6_1", "68"), toc_page_style)],
        [Paragraph("Table 6.2: Synthesized Empirical Performance Benchmark Summary Across All Four Components", toc_text_style), Paragraph(get_pg("tab6_2", "70"), toc_page_style)],
        [Paragraph("Table 6.3: Qualitative Stakeholder Validation Feedback and System Enhancement Matrix", toc_text_style), Paragraph(get_pg("tab6_3", "73"), toc_page_style)],
        [Paragraph("Table 6.4: Systematic Evaluation of Common Group Objectives Against Empirical Results", toc_text_style), Paragraph(get_pg("tab6_4", "74"), toc_page_style)],
        [Paragraph("Table 6.5: Concurrency Stress Testing Benchmarks and Latency Percentiles Under Varying Loads", toc_text_style), Paragraph(get_pg("tab6_5", "77"), toc_page_style)],
        [Paragraph("Table 6.6: Algorithmic Fairness and Adverse Impact Ratio (AIR) Demographic Audit", toc_text_style), Paragraph(get_pg("tab6_6", "79"), toc_page_style)],
        [Paragraph("Table 7.1: Multi-Beneficiary Value Proposition and Quantitative Return on Investment", toc_text_style), Paragraph(get_pg("tab7_1", "83"), toc_page_style)],
        [Paragraph("Table 7.2: Commercial Competitive Landscape and Platform Feature Differentiation", toc_text_style), Paragraph(get_pg("tab7_2", "84"), toc_page_style)],
        [Paragraph("Table 7.3: Tiered SaaS Pricing Strategy, Revenue Architecture, and Operating Margins", toc_text_style), Paragraph(get_pg("tab7_3", "86"), toc_page_style)],
        [Paragraph("Table 7.4: United Nations Sustainable Development Goals (SDGs) Explicit Contribution Matrix", toc_text_style), Paragraph(get_pg("tab7_4", "89"), toc_page_style)],
        [Paragraph("Table 7.5: Pro-Forma 3-Year Commercial Financial Model, Expenditure Breakdown, and EBITDA", toc_text_style), Paragraph(get_pg("tab7_5", "91"), toc_page_style)],
        [Paragraph("Table A.1: Canonical REST Endpoints, HTTP Methods, and Input/Output Payloads", toc_text_style), Paragraph(get_pg("tabA_1", "103"), toc_page_style)],
        [Paragraph("Table B.1: Team Contribution Declaration, Component Allocation, and Ownership Attestation", toc_text_style), Paragraph(get_pg("tabB_1", "106"), toc_page_style)],
        [Paragraph("Table C.1: Microservice Container Network Specifications, Port Allocations, and Resource Quotas", toc_text_style), Paragraph(get_pg("tabC_1", "108"), toc_page_style)],
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
    track('loa')
    story.append(Paragraph("LIST OF ABBREVIATIONS", styles['ChapterHeading']))
    story.append(Spacer(1, 8))

    abbr_rows = [
        [Paragraph("<b>Abbreviation</b>", toc_title_style), Paragraph("<b>Meaning</b>", toc_title_style)],
        [Paragraph("API", toc_text_style), Paragraph("Application Programming Interface", toc_text_style)],
        [Paragraph("AST", toc_text_style), Paragraph("Abstract Syntax Tree", toc_text_style)],
        [Paragraph("ATS", toc_text_style), Paragraph("Applicant Tracking System", toc_text_style)],
        [Paragraph("BERT", toc_text_style), Paragraph("Bidirectional Encoder Representations from Transformers", toc_text_style)],
        [Paragraph("CI/CD", toc_text_style), Paragraph("Continuous Integration and Continuous Deployment", toc_text_style)],
        [Paragraph("CRF", toc_text_style), Paragraph("Conditional Random Field", toc_text_style)],
        [Paragraph("CSS", toc_text_style), Paragraph("Candidate Suitability Score", toc_text_style)],
        [Paragraph("CV", toc_text_style), Paragraph("Curriculum Vitae / Resume", toc_text_style)],
        [Paragraph("DAG", toc_text_style), Paragraph("Directed Acyclic Graph", toc_text_style)],
        [Paragraph("DSR", toc_text_style), Paragraph("Design Science Research", toc_text_style)],
        [Paragraph("EEOC", toc_text_style), Paragraph("Equal Employment Opportunity Commission", toc_text_style)],
        [Paragraph("EQF", toc_text_style), Paragraph("European Qualifications Framework", toc_text_style)],
        [Paragraph("GBDT", toc_text_style), Paragraph("Gradient Boosted Decision Trees", toc_text_style)],
        [Paragraph("GDPR", toc_text_style), Paragraph("General Data Protection Regulation", toc_text_style)],
        [Paragraph("JD", toc_text_style), Paragraph("Job Description / Requisition Specification", toc_text_style)],
        [Paragraph("JSON", toc_text_style), Paragraph("JavaScript Object Notation", toc_text_style)],
        [Paragraph("LambdaMART", toc_text_style), Paragraph("Lambda Multiple Additive Regression Trees", toc_text_style)],
        [Paragraph("LLM", toc_text_style), Paragraph("Large Language Model", toc_text_style)],
        [Paragraph("MAUT", toc_text_style), Paragraph("Multi-Attribute Utility Theory", toc_text_style)],
        [Paragraph("NDCG", toc_text_style), Paragraph("Normalised Discounted Cumulative Gain", toc_text_style)],
        [Paragraph("NER", toc_text_style), Paragraph("Named Entity Recognition", toc_text_style)],
        [Paragraph("NLP", toc_text_style), Paragraph("Natural Language Processing", toc_text_style)],
        [Paragraph("PII", toc_text_style), Paragraph("Personally Identifiable Information", toc_text_style)],
        [Paragraph("RAIGS", toc_text_style), Paragraph("Retrieval-Augmented Interview Generation System", toc_text_style)],
        [Paragraph("REST", toc_text_style), Paragraph("Representational State Transfer", toc_text_style)],
        [Paragraph("ROC-AUC", toc_text_style), Paragraph("Receiver Operating Characteristic - Area Under Curve", toc_text_style)],
        [Paragraph("SBERT", toc_text_style), Paragraph("Sentence-BERT (Sentence Bidirectional Encoder Representations)", toc_text_style)],
        [Paragraph("SDG", toc_text_style), Paragraph("Sustainable Development Goals (United Nations)", toc_text_style)],
        [Paragraph("SHAP", toc_text_style), Paragraph("SHapley Additive exPlanations", toc_text_style)],
        [Paragraph("SLIIT", toc_text_style), Paragraph("Sri Lanka Institute of Information Technology", toc_text_style)],
        [Paragraph("SLQF", toc_text_style), Paragraph("Sri Lanka Qualifications Framework", toc_text_style)],
        [Paragraph("STT", toc_text_style), Paragraph("Speech-to-Text", toc_text_style)],
        [Paragraph("TF-IDF", toc_text_style), Paragraph("Term Frequency - Inverse Document Frequency", toc_text_style)],
        [Paragraph("WER", toc_text_style), Paragraph("Word Error Rate", toc_text_style)],
    ]
    abbr_table = Table(abbr_rows, colWidths=[90, 321])
    abbr_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#000000")),
        ('TOPPADDING', (0,0), (-1,-1), 1.6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.6),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(abbr_table)
    story.append(PageBreak())
