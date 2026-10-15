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
    story.append(p("This dissertation has presented the architectural design, mathematical formalization, software engineering implementation, and empirical validation of <b>Component 1: Automated Semantic Resume Screening and IT Job Role Classification</b>, operating as the intake intelligence gateway of the enterprise <b>RecruitAI</b> ecosystem (Research Identifier: R26-IT-148). Developed by <b>D. T. D. Perera (IT22089236)</b>, Component 1 successfully overcomes the pervasive failure modes of commercial Applicant Tracking Systems and resolves the synthetic benchmark leakage crisis identified in academic literature."))
    story.append(p("Through rigorous engineering and scientific experimentation, the research achieved all stated objectives:"))
    story.append(b("1. Engineered a layout-aware PDF/DOCX ingestion engine with automated PII sanitization ensuring demographic neutrality."))
    story.append(b("2. Formulated boundary-guarded NER look-around assertion windows protecting 400+ technical competencies and eliminating polysemous false-positive collisions on C, R, Go, Spring, and REST."))
    story.append(b("3. Implemented a chronological interval union algebra that eliminates tenure inflation from concurrent employment and disambiguates commercial tenure from academic projects."))
    story.append(b("4. Established a two-dimensional qualification ontology decoupling degree attainment tier level from disciplinary field relevance, preventing non-technical advanced degree inflation."))
    story.append(b("5. Designed an evidence-weighted skill scoring hierarchy that prioritizes verified commercial execution (w = 1.0) over isolated keyword stuffing (w = 0.40)."))
    story.append(b("6. Trained and deployed a balanced multinomial Logistic Regression classifier achieving 87.42% accuracy and 92.47% Macro F1 across 20 canonical IT roles on 819 held-out authentic resumes with 2.4 ms inference."))
    story.append(b("7. Conducted a forensic audit of synthetic recruitment benchmarks, exposing the template memorization artifacts responsible for historical F1 = 1.0 claims."))
    story.append(b("8. Validated software invariance through 195 automated Pytest assertions with 100% pass rate."))

    # 7.2 PRACTICAL INDUSTRIAL IMPACT
    if tracker is not None:
        story.append(PageTracker('sec7_2', tracker))
    story.append(p("7.2 Practical Industrial Impact", h1_style))
    story.append(p("The industrial deployment of Component 1 delivers transformative operational efficiencies to technology recruitment organizations. By replacing crude keyword filters with evidence-weighted semantic scoring, technology enterprises can reduce recruiter resume triage overhead by over 75% while simultaneously increasing candidate qualification accuracy. Most importantly, by replacing opaque rejection emails with structured milestone-based learning roadmaps, RecruitAI converts screening rejections into empowering developmental feedback."))

    # 7.3 FUTURE RESEARCH DIRECTIONS
    if tracker is not None:
        story.append(PageTracker('sec7_3', tracker))
    story.append(p("7.3 Future Research Directions", h1_style))
    story.append(p("While Component 1 establishes a robust intake foundation, several promising research trajectories warrant future investigation:"))
    story.append(b("• <b>Multi-Modal Visual Document Layout Analysis:</b> Incorporating vision-language transformers (such as LayoutLMv3) to jointly model typographical bounding boxes, document colors, and font styles for infographic and visual resumes."))
    story.append(b("• <b>Cross-Lingual Entity Extraction:</b> Extending regex shielding and taxonomy mappings to multilingual resumes (e.g., German, French, Japanese, Mandarin) via cross-lingual multilingual embeddings (mBERT, XLM-RoBERTa)."))
    story.append(b("• <b>LLM-in-the-Loop Interactive Verification:</b> Deploying lightweight instruction-tuned Large Language Models as secondary conversational verification agents to interactively clarify ambiguous career breaks directly with applicants."))
    story.append(PageBreak())
