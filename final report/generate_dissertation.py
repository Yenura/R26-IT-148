import os
import sys
import re
import html
import PyPDF2
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable, Preformatted
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(CURRENT_DIR, "figures")
PDF_OUTPUT_PATH = os.path.join(CURRENT_DIR, "IT22089236_DRAFT.pdf")

# ----------------------------------------------------------------------
# Numbered Canvas for Running Headers and Footers with "Page X of Y"
# ----------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        # Suppress header and footer on Cover Page (Page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1A365D")) # SLIIT Deep Navy
        
        # Running Header
        self.drawString(54, 785, "RecruitAI — Automated Semantic Resume Screening & Role Classification")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawRightString(541, 785, "D. T. D. Perera | IT22089236 | R26-IT-148")
        
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.6)
        self.line(54, 778, 541, 778)

        # Running Footer
        self.line(54, 45, 541, 45)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawString(54, 32, "Faculty of Computing | Sri Lanka Institute of Information Technology (SLIIT)")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(541, 32, page_str)
        
        self.restoreState()

def clean_xml(text):
    """Escapes XML entities for ReportLab Paragraphs safely."""
    text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', text)
    text = re.sub(r'<(?=[0-9\s=])', '&lt;', text)
    text = re.sub(r'(?<=[0-9\s=])>', '&gt;', text)
    return text

def build_dissertation(body_leading=14.2, spacer_scale=1.02, body_size=9.6):
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    PRIMARY = colors.HexColor("#1A365D")   # Deep SLIIT Navy
    SECONDARY = colors.HexColor("#2B6CB0") # Slate Blue
    ACCENT = colors.HexColor("#C53030")    # Crimson
    DARK_TEXT = colors.HexColor("#2D3748") # Charcoal
    LIGHT_BG = colors.HexColor("#F8FAFC")
    BORDER_COL = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=23, leading=29,
        alignment=1, textColor=PRIMARY, spaceAfter=14
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=12, leading=17,
        alignment=1, textColor=SECONDARY, spaceAfter=22
    )

    ch_num_style = ParagraphStyle(
        'ChapterNumber', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=15,
        textColor=ACCENT, spaceBefore=12, spaceAfter=3, keepWithNext=True
    )

    ch_title_style = ParagraphStyle(
        'ChapterTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=17, leading=21,
        textColor=PRIMARY, spaceAfter=12, keepWithNext=True
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=15,
        textColor=PRIMARY, spaceBefore=11 * spacer_scale, spaceAfter=5 * spacer_scale, keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10.5, leading=13.5,
        textColor=SECONDARY, spaceBefore=8 * spacer_scale, spaceAfter=4 * spacer_scale, keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=body_size, leading=body_leading,
        textColor=DARK_TEXT, alignment=4, spaceAfter=6.5 * spacer_scale
    )

    body_bold = ParagraphStyle(
        'Body_Bold', parent=body_style,
        fontName='Helvetica-Bold'
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=body_size - 0.2, leading=body_leading - 0.5,
        textColor=DARK_TEXT, leftIndent=14, firstLineIndent=-9, spaceAfter=4 * spacer_scale
    )

    caption_style = ParagraphStyle(
        'CaptionStyle', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8.5, leading=11,
        alignment=1, textColor=colors.HexColor("#4A5568"), spaceBefore=3, spaceAfter=7 * spacer_scale
    )

    code_pre_style = ParagraphStyle(
        'CodePreStyle', parent=styles['Normal'],
        fontName='Courier', fontSize=7.6, leading=9.8,
        textColor=colors.HexColor("#1A202C")
    )

    ref_style = ParagraphStyle(
        'RefStyle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.0, leading=10.8,
        textColor=DARK_TEXT, leftIndent=18, firstLineIndent=-18, spaceAfter=4.5 * spacer_scale
    )

    styles.add(title_style)
    styles.add(subtitle_style)
    styles.add(ch_num_style)
    styles.add(ch_title_style)
    styles.add(h1_style)
    styles.add(h2_style)
    styles.add(body_style)
    styles.add(body_bold)
    styles.add(bullet_style)
    styles.add(caption_style)
    styles.add(code_pre_style)
    styles.add(ref_style)

    def p(text, style=body_style):
        return Paragraph(clean_xml(text), style)

    def b(text):
        return Paragraph(clean_xml(text), bullet_style)

    def sp(h=10):
        return Spacer(1, h * spacer_scale)

    def make_box(text, bg=LIGHT_BG, border=BORDER_COL):
        pf = Preformatted(text, code_pre_style)
        t = Table([[pf]], colWidths=[487])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('BOX', (0,0), (-1,-1), 1, border),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    story = []

    # =========================================================================
    # FRONT MATTER: PAGES 1 TO 7
    # =========================================================================
    # PAGE 1: TITLE PAGE
    story.append(sp(20))
    story.append(p("SRI LANKA INSTITUTE OF INFORMATION TECHNOLOGY", ParagraphStyle('InstTitle', fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, textColor=PRIMARY)))
    story.append(p("FACULTY OF COMPUTING | DEPARTMENT OF COMPUTER SCIENCE &amp; SOFTWARE ENGINEERING", ParagraphStyle('DeptTitle', fontName='Helvetica', fontSize=9.5, leading=13, alignment=1, textColor=SECONDARY)))
    story.append(sp(35))

    story.append(p("AI-DRIVEN RECRUITMENT ECOSYSTEM FOR INTELLIGENT JOB MATCHING AND PREDICTIVE CAREER DEVELOPMENT", ParagraphStyle('ProjTitle', fontName='Helvetica-Bold', fontSize=15, leading=20, alignment=1, textColor=SECONDARY)))
    story.append(sp(12))
    story.append(p("RESEARCH COMPONENT 1 FINAL DISSERTATION DRAFT", ParagraphStyle('SubSub', fontName='Helvetica-Bold', fontSize=11, leading=15, alignment=1, textColor=ACCENT)))
    story.append(sp(22))

    story.append(p("AUTOMATED SEMANTIC RESUME SCREENING AND IT JOB ROLE CLASSIFICATION", title_style))
    story.append(p("An Auditable Multi-Stage Ingestion Pipeline with Boundary-Guarded Named Entity Recognition, Granular Experience Disambiguation, Two-Dimensional Credential Decoupling, and Balanced Multinomial Logistic Role Classification", subtitle_style))
    story.append(sp(35))

    meta_table_data = [
        [p("<b>Author / Researcher:</b>", body_style), p("D. T. D. Perera", body_bold)],
        [p("<b>Student Identification Number:</b>", body_style), p("IT22089236", body_bold)],
        [p("<b>Academic Degree Program:</b>", body_style), p("B.Sc. (Hons) in Information Technology Specializing in Software Engineering", body_style)],
        [p("<b>Assigned Research Component:</b>", body_style), p("Component 1: Automated Semantic Resume Screening &amp; Role Classification", body_style)],
        [p("<b>Research Group Identifier:</b>", body_style), p("R26-IT-148", body_bold)],
        [p("<b>Academic Year &amp; Semester:</b>", body_style), p("Year 4, Semester 2 (Comprehensive Final Dissertation)", body_style)],
        [p("<b>Faculty / Department:</b>", body_style), p("Department of Computer Science &amp; Software Engineering, Faculty of Computing", body_style)],
        [p("<b>Academic Institution:</b>", body_style), p("Sri Lanka Institute of Information Technology (SLIIT), Malabe, Sri Lanka", body_style)],
        [p("<b>Date of Submission:</b>", body_style), p("October 2026", body_style)]
    ]
    meta_table = Table(meta_table_data, colWidths=[175, 312])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(sp(20))
    story.append(p("<i>A dissertation draft submitted in partial fulfillment of the requirements for the degree of Bachelor of Science (Honours) in Information Technology at the Sri Lanka Institute of Information Technology.</i>", caption_style))
    story.append(PageBreak())

    # PAGE 2: DECLARATION
    story.append(p("DECLARATION OF ORIGINALITY", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))
    story.append(p("I hereby declare that this dissertation titled <b>'Automated Semantic Resume Screening and IT Job Role Classification'</b> is the record of authentic research work carried out by me under research project identifier <b>R26-IT-148</b> in partial fulfillment of the requirements for the Bachelor of Science (Honours) in Information Technology degree at the Sri Lanka Institute of Information Technology (SLIIT)."))
    story.append(p("I confirm that the content presented in this report is my original intellectual work and has not been submitted previously in whole or in part for the award of any other degree, diploma, or academic fellowship at this or any other tertiary educational institution."))
    story.append(p("All algorithms, mathematical models, experimental methodologies, dataset evaluation figures, and software source codes described in this dissertation are authentic. In strict compliance with academic research integrity, no experimental results, F1-scores, accuracy figures, or citations have been fabricated or artificially altered. Where information and secondary models have been derived from published academic literature, they have been comprehensively cited in the references section."))
    story.append(sp(20))

    dec_table = Table([
        [p("<b>Candidate Name:</b>", body_style), p("D. T. D. Perera", body_bold)],
        [p("<b>Candidate Student ID:</b>", body_style), p("IT22089236", body_bold)],
        [p("<b>Signature of Candidate:</b>", body_style), p("....................................................................", body_style)],
        [p("<b>Date:</b>", body_style), p("October 10, 2026", body_style)],
    ], colWidths=[150, 337])
    dec_table.setStyle(TableStyle([('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    story.append(dec_table)
    story.append(sp(25))

    story.append(p("SUPERVISOR ENDORSEMENT", h1_style))
    story.append(p("This is to certify that this research dissertation titled <b>'Automated Semantic Resume Screening and IT Job Role Classification'</b> is a bona fide record of research work conducted by <b>D. T. D. Perera (IT22089236)</b> under our supervision and guidance in the Faculty of Computing, Sri Lanka Institute of Information Technology."))
    story.append(sp(18))

    sup_table = Table([
        [p("<b>Research Supervisor:</b>", body_style), p("<b>Co-Supervisor:</b>", body_style)],
        [p("Signature: ......................................................", body_style), p("Signature: ......................................................", body_style)],
        [p("Date: .............................................................", body_style), p("Date: .............................................................", body_style)],
    ], colWidths=[243, 244])
    sup_table.setStyle(TableStyle([('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    story.append(sup_table)
    story.append(PageBreak())

    # PAGE 3: ABSTRACT
    story.append(p("ABSTRACT", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))
    story.append(p("Traditional automated curriculum vitae (CV) screening pipelines in high-volume enterprise information technology (IT) hiring suffer from severe structural breakdowns. Legacy Applicant Tracking Systems (ATS) predominantly execute lexical substring matching and crude keyword frequency counts. This creates two pervasive industry failure modes: qualified engineers whose resumes utilize non-standard phrasing or focus on architectural achievements are prematurely rejected, while opportunistic applicants who game filters via white-font keyword stuffing or template repetition bypass initial screening without authentic competency. Furthermore, prior academic literature in automated resume parsing and role classification has frequently suffered from fatal methodological flaws—most notably synthetic data leakage, wherein classifiers evaluated on template-generated resumes memorized invariant boilerplate paragraphs and target-label headers, reporting artificial F1 = 1.0 performance that collapsed completely upon exposure to authentic applicant resumes."))
    story.append(p("To address these critical industry challenges and academic gaps, this dissertation presents the design, mathematical formulation, implementation, and empirical validation of <b>Component 1: Automated Semantic Resume Screening and IT Job Role Classification</b>, operating as the intake intelligence gateway of the enterprise <b>RecruitAI</b> ecosystem (Research Identifier: R26-IT-148). Built upon a decoupled FastAPI microservice running on Port 8001, the system processes heterogeneous, unstructured PDF and DOCX documents through a multi-stage semantic ingestion pipeline."))
    story.append(p("The research introduces four foundational contributions: (1) an end-to-end format-agnostic document ingestion engine incorporating layout-aware line segmentation and boundary-guarded Named Entity Recognition (NER) covering over 400 canonical IT competencies across 7 technical disciplines, protected by context-guarded regex look-arounds that eliminate polysemous token collisions for single-letter and ambiguous tools (e.g., C, R, Go, Spring, REST); (2) a formal temporal interval union algebra that eliminates concurrent employment duration doubling, filters self-directed academic projects from professional tenure, and disambiguates total tenure, IT-sector tenure, and target-role-relevant exposure; (3) a two-dimensional credential qualification ontology that decouples academic degree attainment levels from disciplinary field relevance (Core Computing, Adjacent Quantitative, Non-Technical); and (4) an evidence-weighted technical skill scoring hierarchy that distinguishes isolated keyword mentions (w = 0.40) from demonstrated workplace execution (w = 1.00)."))
    story.append(p("To classify applicant specialization across 20 canonical IT engineering roles, we engineer dense normalized NLP feature matrices and train a balanced multinomial Logistic Regression classifier with sublinear TF-IDF vectorization. Evaluated on a strictly held-out independent test partition of 819 genuine resumes from a curated 4,000-CV real-world corpus, our primary classifier achieves an empirical accuracy of <b>87.42%</b>, a macro-averaged precision of <b>91.35%</b>, a macro-averaged recall of <b>94.35%</b>, and a macro-F1 score of <b>92.47%</b> (with weighted-F1 reaching <b>93.47%</b> and 5-fold stratified cross-validation yielding <b>85.95% ± 0.96%</b>). Inference executes in <b>2.4 ms</b> per candidate, outperforming deep transformers by 59x in throughput while guaranteeing closed-form mathematical explainability. The microservice generates an uncollapsed Tri-Pillar Qualification Vector (S_skill, S_exp, S_edu) providing an interpretable contract to downstream candidate ranking and interview orchestration engines."))
    story.append(sp(8))
    story.append(p("<b>Keywords:</b> Resume Parsing, Named Entity Recognition, Job Role Classification, Polysemy Protection, Experience Disambiguation, Field Relevance, Data Leakage Audit, Tri-Pillar Candidate Scoring, RecruitAI, Logistic Regression.", body_style))
    story.append(PageBreak())

    # PAGE 4: ACKNOWLEDGEMENTS
    story.append(p("ACKNOWLEDGEMENTS", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))
    story.append(p("First and foremost, I express my deepest gratitude to the Almighty for granting me the wisdom, perseverance, and intellectual strength to successfully undertake and complete this final year research dissertation."))
    story.append(p("I wish to convey my sincere appreciation and profound gratitude to our research supervisor and co-supervisor at the Faculty of Computing, Sri Lanka Institute of Information Technology (SLIIT). Their invaluable academic mentorship, rigorous critiques, and continuous guidance throughout the conceptualization, model training, leakage auditing, and evaluation phases of this research were instrumental in maintaining the highest standards of scientific rigor."))
    story.append(p("I also extend my sincere thanks to the Dean of the Faculty of Computing, the Head of the Department of Computer Science &amp; Software Engineering, and the academic and technical staff of SLIIT for providing the state-of-the-art computational infrastructure, laboratories, and supportive academic environment necessary to conduct this intensive machine learning research."))
    story.append(p("A special note of appreciation goes to my esteemed research colleagues and fellow project team members in Research Group <b>R26-IT-148</b>: <b>Dulnith K. D. (IT22094872)</b>, <b>K. G. Savinda N. Perera (IT22027610)</b>, and <b>Yenura S. Karunanayaka (IT22306272)</b>. Their exemplary collaboration, seamless inter-service microservice contract alignment, and tireless dedication made the realization of the integrated RecruitAI ecosystem possible."))
    story.append(p("Finally, my deepest and most heartfelt debt of gratitude is dedicated to my beloved parents and family members. Their unconditional love, constant sacrifices, moral support, and endless encouragement have been the bedrock of my educational journey. I dedicate this research work to them."))
    story.append(sp(25))
    story.append(p("DEDICATION", h1_style))
    story.append(p("<i>This dissertation is dedicated to all aspiring software engineers, researchers, and students who strive tirelessly to bridge the gap between academic theory and transformative industrial software solutions.</i>", caption_style))
    story.append(PageBreak())

    # PAGE 5: TABLE OF CONTENTS
    story.append(p("TABLE OF CONTENTS", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))
    # Compact styles for front matter tables
    toc_item_style = ParagraphStyle(
        'TOCItem_Compact', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.0, leading=10.0,
        textColor=DARK_TEXT, spaceAfter=0, spaceBefore=0
    )
    toc_bold_style = ParagraphStyle(
        'TOCBold_Compact', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.0, leading=10.0,
        textColor=PRIMARY, spaceAfter=0, spaceBefore=0
    )
    toc_page_style = ParagraphStyle(
        'TOCPage_Compact', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.0, leading=10.0,
        alignment=2, textColor=DARK_TEXT, spaceAfter=0, spaceBefore=0
    )
    toc_page_bold = ParagraphStyle(
        'TOCPageBold_Compact', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.0, leading=10.0,
        alignment=2, textColor=PRIMARY, spaceAfter=0, spaceBefore=0
    )

    lof_item_style = ParagraphStyle(
        'LOFItem_Compact', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.8, leading=9.8,
        textColor=DARK_TEXT, spaceAfter=0, spaceBefore=0
    )
    lof_bold_style = ParagraphStyle(
        'LOFBold_Compact', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.8, leading=9.8,
        textColor=PRIMARY, spaceAfter=0, spaceBefore=0
    )
    lof_page_style = ParagraphStyle(
        'LOFPage_Compact', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.8, leading=9.8,
        alignment=2, textColor=DARK_TEXT, spaceAfter=0, spaceBefore=0
    )
    lof_page_bold = ParagraphStyle(
        'LOFPageBold_Compact', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.8, leading=9.8,
        alignment=2, textColor=PRIMARY, spaceAfter=0, spaceBefore=0
    )

    def ptoc(text, is_bold=False):
        return Paragraph(clean_xml(text), toc_bold_style if is_bold else toc_item_style)

    def ptoc_page(text, is_bold=False):
        return Paragraph(clean_xml(text), toc_page_bold if is_bold else toc_page_style)

    def plof(text, is_bold=False):
        return Paragraph(clean_xml(text), lof_bold_style if is_bold else lof_item_style)

    def plof_page(text, is_bold=False):
        return Paragraph(clean_xml(text), lof_page_bold if is_bold else lof_page_style)

    toc_data = [
        [ptoc("<b>Chapter / Section Title</b>", True), ptoc_page("<b>Page</b>", True)],
        [ptoc("Declaration of Originality"), ptoc_page("ii")],
        [ptoc("Abstract"), ptoc_page("iii")],
        [ptoc("Acknowledgements &amp; Dedication"), ptoc_page("iv")],
        [ptoc("List of Figures"), ptoc_page("vii")],
        [ptoc("List of Tables"), ptoc_page("vii")],
        [ptoc("List of Abbreviations &amp; Acronyms"), ptoc_page("viii")],
        [ptoc("<b>1. Introduction</b>", True), ptoc_page("<b>9</b>", True)],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;1.1 Context and Global Recruitment Landscape"), ptoc_page("9")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;1.2 Economic and Talent Toll of Recruitment Bottlenecks"), ptoc_page("10")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;1.3 Systemic Failure Modes in Current ATS Platforms"), ptoc_page("10")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;1.4 Research Motivation &amp; Problem Formulation"), ptoc_page("11")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;1.5 Research Objectives &amp; Specific C1 Scope"), ptoc_page("11")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;1.6 Research Questions and Formal Hypotheses"), ptoc_page("12")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;1.7 Research Methodology &amp; Engineering Lifecycle"), ptoc_page("13")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;1.8 Scope, Boundaries, and Delimitations"), ptoc_page("13")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;1.9 Summary of Primary Technical Contributions"), ptoc_page("13")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;1.10 Dissertation Organization and Roadmap"), ptoc_page("13")],
        [ptoc("<b>2. Literature Review</b>", True), ptoc_page("<b>14</b>", True)],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.1 Evolution of Applicant Tracking Systems (ATS)"), ptoc_page("14")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.2 NLP in Curriculum Vitae Mining"), ptoc_page("14")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.3 Named Entity Recognition &amp; Tokenization Challenges"), ptoc_page("14")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.4 Lexical Ambiguity, Polysemy, &amp; Token Collisions"), ptoc_page("15")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.5 Temporal Reasoning and Duration Calculus"), ptoc_page("15")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.6 Academic Credential Ontologies &amp; Degree Harmonization"), ptoc_page("16")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.7 Multi-Class Job Role Classification Architectures"), ptoc_page("16")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.8 The Synthetic Benchmark Leakage Crisis"), ptoc_page("17")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.9 Dense Semantic Document Matching via Bi-Encoders"), ptoc_page("17")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.10 Algorithmic Bias, Fairness Audits, &amp; Regulatory Governance"), ptoc_page("17")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.11 Research Gap Synthesis and Theoretical Framework"), ptoc_page("17")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;2.12 Survey of Public Resume Corpora &amp; Empirical Vulnerabilities"), ptoc_page("18")],
        [ptoc("<b>3. Methodology and Architectural Design</b>", True), ptoc_page("<b>19</b>", True)],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.1 RecruitAI Integrated System Architecture"), ptoc_page("19")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.2 Component 1 Ingestion Pipeline Subsystems"), ptoc_page("19")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.3 Layout-Aware Document Ingestion &amp; Text Sanitization"), ptoc_page("19")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.4 Automated PII Redaction Subsystem"), ptoc_page("20")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.5 Boundary-Guarded NER &amp; Polysemy Shielding"), ptoc_page("20")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.6 Temporal Experience Algebra &amp; Overlap Interval Merging"), ptoc_page("21")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.7 Commercial Employment vs. Project Disambiguation"), ptoc_page("22")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.8 Decoupled Credential Qualification Model"), ptoc_page("22")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.9 Contextual Evidence-Weighted Skill Scoring"), ptoc_page("23")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.10 Sublinear TF-IDF &amp; Balanced Logistic Classifier"), ptoc_page("24")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.11 Dense Semantic JD Matching via Sentence-BERT"), ptoc_page("24")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.12 Tri-Pillar Scoring Formulation"), ptoc_page("25")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.13 Backend Structured Learning Roadmap Synthesis"), ptoc_page("25")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.14 Canonical Role Benchmark Competencies"), ptoc_page("25")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;3.15 Pareto Sensitivity Analysis of Tri-Pillar Weights"), ptoc_page("26")],
        [ptoc("<b>4. Implementation Details and Software Engineering</b>", True), ptoc_page("<b>28</b>", True)],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;4.1 Microservice Architecture and Technology Stack"), ptoc_page("28")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;4.2 Modular Directory Decomposition"), ptoc_page("28")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;4.3 Token Shielding RegEx Lookahead Mechanics"), ptoc_page("28")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;4.4 Date Arithmetic and Calendar Math Engine"), ptoc_page("29")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;4.5 Dense Feature Vector Extraction in feature_engineering.py"), ptoc_page("29")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;4.6 MongoDB Document Modeling and Schemas"), ptoc_page("30")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;4.7 RESTful API Specification (Port 8001)"), ptoc_page("30")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;4.8 Automated Pytest Verification Suite (195 Tests)"), ptoc_page("31")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;4.9 Dense Semantic Matching Implementation in matcher.py"), ptoc_page("31")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;4.10 Structured Curriculum Engine in roadmap.py"), ptoc_page("32")],
        [ptoc("<b>5. Empirical Results, Validation, and Benchmarking</b>", True), ptoc_page("<b>33</b>", True)],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.1 Dataset Architecture: Curated 4,000 Real CV Corpus"), ptoc_page("33")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.2 Forensic Audit of Synthetic Data Leakage"), ptoc_page("33")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.3 Model Training &amp; 5-Fold Stratified Cross-Validation"), ptoc_page("34")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.4 Primary Classification Results on Held-Out Test Set"), ptoc_page("34")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.5 Granular Per-Class Metrics across all 20 Roles"), ptoc_page("35")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.6 Comparative Model Architecture Benchmarking"), ptoc_page("36")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.7 Feature Permutation Importance Analysis"), ptoc_page("37")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.8 Extraction Ablation Experiments"), ptoc_page("37")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.9 Mathematical Justification for 3-Pillar Weights"), ptoc_page("37")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.10 End-to-End Pipeline Latency Benchmarks (151.35ms)"), ptoc_page("38")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.11 Qualitative Candidate Profile Case Studies"), ptoc_page("39")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;5.12 Full 20x20 Confusion Matrix &amp; Error Cluster Analysis"), ptoc_page("40")],
        [ptoc("<b>6. Discussion, Ethics &amp; Algorithmic Fairness</b>", True), ptoc_page("<b>41</b>", True)],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;6.1 Discussion of Empirical Findings"), ptoc_page("41")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;6.2 PII Redaction &amp; Privacy Compliance"), ptoc_page("41")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;6.3 Algorithmic Transparency &amp; Closed-Form SHAP Explanations"), ptoc_page("41")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;6.4 Regulatory Compliance: EU AI Act &amp; NYC Local Law 144"), ptoc_page("42")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;6.5 Threats to Validity and System Limitations"), ptoc_page("42")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;6.6 Industrial Deployment and Scalability Analysis"), ptoc_page("43")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;6.7 Failure Mode Taxonomy &amp; Edge Case Handling"), ptoc_page("43")],
        [ptoc("<b>7. Conclusion and Future Work</b>", True), ptoc_page("<b>44</b>", True)],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;7.1 Summary of Research Achievements"), ptoc_page("44")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;7.2 Practical Industrial Impact"), ptoc_page("44")],
        [ptoc("&nbsp;&nbsp;&nbsp;&nbsp;7.3 Future Research Directions"), ptoc_page("44")],
        [ptoc("<b>References</b> (60 Academic Citations)", True), ptoc_page("<b>46</b>", True)],
        [ptoc("<b>Appendix A: Comprehensive 20 Canonical IT Job Roles Taxonomy</b>", True), ptoc_page("<b>49</b>", True)],
        [ptoc("<b>Appendix B: Complete OpenAPI 3.0 REST Specification (Port 8001)</b>", True), ptoc_page("<b>51</b>", True)],
        [ptoc("<b>Appendix C: Automated 195-Test Pytest Execution and Verification Log</b>", True), ptoc_page("<b>53</b>", True)]
    ]
    toc_table = Table(toc_data, colWidths=[430, 57])
    toc_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, PRIMARY),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0.8),
        ('TOPPADDING', (0,0), (-1,-1), 0.8),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # PAGE 7: LIST OF FIGURES & TABLES
    story.append(p("LIST OF FIGURES", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=8))

    fig_list_data = [
        [plof("<b>Figure Number &amp; Title</b>", True), plof_page("<b>Page</b>", True)],
        [plof("Figure 1.1: Multi-Microservice Architecture of the RecruitAI Ecosystem"), plof_page("11")],
        [plof("Figure 3.1: Context-Guarded Regex Look-Around Shielding vs. Naive Substring Tokenizers"), plof_page("20")],
        [plof("Figure 3.2: Temporal Experience Disambiguation: Concurrent Employment Interval Merging"), plof_page("21")],
        [plof("Figure 5.5: Forensic Evaluation: Artificial Synthetic Leakage vs. Genuine Real-World Evaluation"), plof_page("33")],
        [plof("Figure 5.4: Empirical Classification Performance Across 20 Canonical IT Roles (N=819)"), plof_page("35")],
        [plof("Figure 5.3: Model Architecture Comparison: Classification Accuracy vs. Inference Latency"), plof_page("36")],
        [plof("Figure 5.2: Empirical Feature Importance Contributions vs. Deployed 3-Pillar Weights"), plof_page("37")],
        [plof("Figure 5.1: Pipeline Processing Latency Breakdown Across All Six Stages (Total: 151.35 ms)"), plof_page("38")]
    ]
    fig_table = Table(fig_list_data, colWidths=[430, 57])
    fig_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, PRIMARY),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.0),
        ('TOPPADDING', (0,0), (-1,-1), 1.0),
    ]))
    story.append(fig_table)
    story.append(sp(12))

    story.append(p("LIST OF TABLES", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=8))

    tab_list_data = [
        [plof("<b>Table Number &amp; Title</b>", True), plof_page("<b>Page</b>", True)],
        [plof("Table 1.1: Enterprise Technical Recruitment Funnel Drop-Off Metrics and ATS Failure Points"), plof_page("9")],
        [plof("Table 2.2: International Academic Degree Framework Harmonization Matrix"), plof_page("16")],
        [plof("Table 2.1: Comprehensive Survey of Commercial and Open-Source Resume Screening Engines"), plof_page("17")],
        [plof("Table 3.1: Academic Degree Tier Level and Disciplinary Field Relevance Scoring Matrix"), plof_page("22")],
        [plof("Table 3.2: Dense 67-Dimensional Feature Vector Specification"), plof_page("24")],
        [plof("Table 3.3: Canonical IT Job Role Benchmark Competencies and Core Skills Lexicon"), plof_page("25")],
        [plof("Table 4.1: Component 1 Microservice RESTful API Specification (Port 8001)"), plof_page("30")],
        [plof("Table 4.2: Automated Pytest Verification Suite Breakdown (195 Passed Tests)"), plof_page("31")],
        [plof("Table 5.0: 5-Fold Stratified Cross-Validation Convergence and Invariance Metrics"), plof_page("34")],
        [plof("Table 5.0b: Hyperparameter Grid Search Optimization"), plof_page("34")],
        [plof("Table 5.1: Primary Classification Performance Metrics on Held-Out Test Partition (N=819)"), plof_page("34")],
        [plof("Table 5.2: Per-Class Precision, Recall, and F1-Score Across 20 Canonical IT Roles"), plof_page("35")],
        [plof("Table 5.3: Comparative Benchmark Against Alternative Machine Learning Architectures"), plof_page("36")],
        [plof("Table 5.4: Feature Subset Extraction Ablation Study on Real Applicant CV Profiles"), plof_page("37")],
        [plof("Table 5.5: Stage-by-Stage Latency Benchmarking Over 50 Iterations (Total: 151.35 ms)"), plof_page("38")],
        [plof("Table 5.6: Comparative Case Study Predictions, Tri-Pillar Scoring, and Outcomes"), plof_page("40")],
        [plof("Table 5.7: Primary Off-Diagonal Error Clusters in 20x20 Classification Matrix"), plof_page("40")],
        [plof("Table 6.0: Representative Closed-Form Feature Attribution Log-Odds Weights"), plof_page("41")],
        [plof("Table 6.1: Global AI Regulatory Compliance Mapping (EU AI Act, NYC LL144, GDPR)"), plof_page("42")]
    ]
    tab_table = Table(tab_list_data, colWidths=[430, 57])
    tab_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, PRIMARY),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.0),
        ('TOPPADDING', (0,0), (-1,-1), 1.0),
    ]))
    story.append(tab_table)
    story.append(PageBreak())

    # PAGE 7: ABBREVIATIONS
    story.append(p("LIST OF ABBREVIATIONS &amp; ACRONYMS", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))

    abbr_data = [
        [p("<b>ATS</b>", body_bold), p("Applicant Tracking System", body_style)],
        [p("<b>NLP</b>", body_bold), p("Natural Language Processing", body_style)],
        [p("<b>NER</b>", body_bold), p("Named Entity Recognition", body_style)],
        [p("<b>PII</b>", body_bold), p("Personally Identifiable Information", body_style)],
        [p("<b>TF-IDF</b>", body_bold), p("Term Frequency - Inverse Document Frequency", body_style)],
        [p("<b>SBERT</b>", body_bold), p("Sentence Bidirectional Encoder Representations from Transformers", body_style)],
        [p("<b>OCR</b>", body_bold), p("Optical Character Recognition", body_style)],
        [p("<b>REST</b>", body_bold), p("Representational State Transfer", body_style)],
        [p("<b>API</b>", body_bold), p("Application Programming Interface", body_style)],
        [p("<b>CV</b>", body_bold), p("Curriculum Vitae / Resume", body_style)],
        [p("<b>JD</b>", body_bold), p("Job Description / Requisition Specification", body_style)],
        [p("<b>SLIIT</b>", body_bold), p("Sri Lanka Institute of Information Technology", body_style)],
        [p("<b>SRE</b>", body_bold), p("Site Reliability Engineering", body_style)],
        [p("<b>QA</b>", body_bold), p("Quality Assurance", body_style)],
        [p("<b>SVM</b>", body_bold), p("Support Vector Machine", body_style)],
        [p("<b>BERT</b>", body_bold), p("Bidirectional Encoder Representations from Transformers", body_style)],
        [p("<b>DistilBERT</b>", body_bold), p("Distilled Bidirectional Encoder Representations from Transformers", body_style)],
        [p("<b>CSV</b>", body_bold), p("Comma Separated Values", body_style)],
        [p("<b>JSON</b>", body_bold), p("JavaScript Object Notation", body_style)],
        [p("<b>SHAP</b>", body_bold), p("SHapley Additive exPlanations", body_style)],
        [p("<b>LTR</b>", body_bold), p("Learning-to-Rank", body_style)],
        [p("<b>LambdaMART</b>", body_bold), p("Lambda Multiple Additive Regression Trees", body_style)],
        [p("<b>NDCG</b>", body_bold), p("Normalized Discounted Cumulative Gain", body_style)],
        [p("<b>MAP</b>", body_bold), p("Mean Average Precision", body_style)],
        [p("<b>DAG</b>", body_bold), p("Directed Acyclic Graph", body_style)],
        [p("<b>GBDT</b>", body_bold), p("Gradient Boosted Decision Trees", body_style)],
        [p("<b>C1</b>", body_bold), p("Component 1 (Automated Resume Screening &amp; Role Classification)", body_style)],
        [p("<b>C2</b>", body_bold), p("Component 2 (Autonomous Multi-Modal Technical Interview System)", body_style)],
        [p("<b>C3</b>", body_bold), p("Component 3 (Candidate Suitability Scoring &amp; Listwise Ranking)", body_style)],
        [p("<b>C4</b>", body_bold), p("Component 4 (Skill Gap Diagnostics &amp; Career Pathfinding)", body_style)]
    ]
    abbr_table = Table(abbr_data, colWidths=[90, 397])
    abbr_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
    ]))
    story.append(abbr_table)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 1 TO 7 TEXT GENERATOR
    # =========================================================================
    # We will import or inline the detailed chapter text modules
    from dissertation_chapters import append_all_chapters
    append_all_chapters(story, styles, p, b, sp, make_box, caption_style, ref_style, FIG_DIR)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Read generated PDF page count using PyPDF2
    reader = PyPDF2.PdfReader(PDF_OUTPUT_PATH)
    actual_pages = len(reader.pages)
    print(f"Build completed! Actual Page Count: {actual_pages} pages.")
    return actual_pages

if __name__ == "__main__":
    pages = build_dissertation()
    print(f"Final PDF generated at: {PDF_OUTPUT_PATH} with {pages} pages.")
