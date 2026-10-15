import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_ch7(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker=None):
    PRIMARY = colors.HexColor("#1A365D")
    SECONDARY = colors.HexColor("#2B6CB0")
    DARK_TEXT = colors.HexColor("#2D3748")

    ch_num_style = styles['ChapterNumber']
    ch_title_style = styles['ChapterTitle']
    h1_style = styles['Heading1_Custom']
    h2_style = styles['Heading2_Custom']
    body_style = styles['Body_Custom']
    body_bold = styles['Body_Bold']

    # Page tracking hook
    if tracker is not None:
        from generate_dissertation import PageTracker
        story.append(PageTracker('ch7', tracker))

    # CHAPTER 7 HEADER
    story.append(p("CHAPTER 7", ch_num_style))
    story.append(p("CONCLUSION AND FUTURE WORK", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))

    # 7.1 SUMMARY OF RESEARCH ACHIEVEMENTS
    if tracker is not None:
        story.append(PageTracker('sec7_1', tracker))
    story.append(p("7.1 Summary of Research Achievements", h1_style))
    story.append(p("This dissertation has detailed the design, mathematical formalization, software engineering implementation, and empirical validation of <b>Component 1: Automated Semantic Resume Screening and IT Job Role Classification</b>, operating as the intake intelligence gateway of the enterprise <b>RecruitAI</b> ecosystem (Research Project Identifier: R26-IT-148). Developed by <b>D. T. D. Perera (IT22089236)</b>, Component 1 addresses the structural failure modes of legacy Applicant Tracking Systems and resolves the synthetic benchmark leakage issue identified in academic literature."))
    story.append(p("Through systematic software engineering and rigorous empirical validation, this research completed all stated objectives:"))
    story.append(b("1. Implemented a layout-aware PDF and DOCX document ingestion engine with automated PII sanitization to support demographic neutrality."))
    story.append(b("2. Formulated boundary-guarded NER look-around assertion patterns protecting 400+ technical competencies, eliminating polysemous token collisions on C, R, Go, Spring, and REST."))
    story.append(b("3. Developed a chronological interval union algebra that eliminates duration inflation from concurrent employment and separates corporate engineering tenure from university coursework projects."))
    story.append(b("4. Formulated a two-dimensional qualification ontology that decouples academic degree tier level from disciplinary field relevance, preventing unweighted score inflation from non-technical advanced degrees."))
    story.append(b("5. Structured an evidence-weighted technical skill scoring hierarchy that prioritizes verified workplace execution (w = 1.0) over isolated keyword mentions (w = 0.40)."))
    story.append(b("6. Trained and deployed a balanced multinomial Logistic Regression classifier achieving 87.42% accuracy and 92.47% Macro F1 across 20 canonical IT engineering roles on 819 held-out authentic resumes with 2.4 ms inference latency."))
    story.append(b("7. Conducted a forensic audit of published recruitment benchmarks, demonstrating that reported F1 = 1.0 scores stemmed from template memorization rather than authentic model generalization."))
    story.append(b("8. Validated microservice reliability and numerical invariance through 195 automated Pytest assertions achieving a 100% pass rate in 79.60 seconds."))

    # 7.2 PRACTICAL INDUSTRIAL IMPACT
    if tracker is not None:
        story.append(PageTracker('sec7_2', tracker))
    story.append(p("7.2 Practical Industrial Impact", h1_style))
    story.append(p("The deployment of Component 1 offers significant operational improvements for enterprise software engineering recruitment. By replacing brittle keyword filters with evidence-weighted semantic parsing, organizations can reduce manual recruiter triage time by over 75% while simultaneously improving shortlisting accuracy. Furthermore, by replacing generic rejection notices with milestone-based learning roadmaps, RecruitAI converts screening rejections into constructive developmental feedback for aspiring software engineers."))

    # 7.3 FUTURE RESEARCH DIRECTIONS
    if tracker is not None:
        story.append(PageTracker('sec7_3', tracker))
    story.append(p("7.3 Future Research Directions", h1_style))
    story.append(p("While Component 1 establishes an auditable and performant intake engine, several promising research trajectories remain open for future work:"))
    story.append(b("• <b>Multi-Modal Visual Document Layout Analysis:</b> Integrating vision-language transformer architectures (such as LayoutLMv3) to jointly evaluate bounding boxes, typographical hierarchies, and visual design elements in creative developer portfolios."))
    story.append(b("• <b>Cross-Lingual Entity Extraction:</b> Extending the boundary-guarded taxonomies to support multilingual resumes (e.g., German, French, Japanese, and Mandarin) using cross-lingual transfer representations (such as XLM-RoBERTa)."))
    story.append(b("• <b>Interactive Verification Agents:</b> Deploying lightweight, instruction-tuned conversational models as secondary agents to interactively clarify ambiguous employment gaps directly with applicants."))
    story.append(PageBreak())
