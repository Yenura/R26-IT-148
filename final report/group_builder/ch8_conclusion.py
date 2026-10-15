import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from group_builder.styles import clean_xml, create_table_box, PRINTABLE_WIDTH
from group_builder.canvas_helper import PageTracker

def append_group_ch8(story, styles, fig_dir, tracker=None):
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

    # =========================================================================
    # 8 CONCLUSION AND FUTURE DIRECTIONS
    # =========================================================================
    track('ch8')
    story.append(Paragraph("8 CONCLUSION AND FUTURE DIRECTIONS", h_ch))
    story.append(Spacer(1, 4))

    # 8.1 Overall conclusion
    track('sec8_1')
    story.append(Paragraph("8.1 Overall conclusion", h_sec))
    story.append(Paragraph("This common integrated research report has presented the engineering design, system integration, algorithmic formulation, and empirical evaluation of the RecruitAI ecosystem (Research Project Identifier: R26-IT-148): an end-to-end artificial intelligence recruitment platform unifying automated semantic resume screening, autonomous multi-modal technical interviewing, multi-attribute candidate ranking, and predictive career pathfinding.", p_body))
    story.append(Paragraph("The research directly resolved the overarching crisis of contemporary technical recruitment: the profound disconnection between high-volume intake triage, authentic technical capability evaluation, listwise hiring decisions, and candidate remediation. Prior to this research, corporate talent acquisition operated as an adversarial 'black hole,' eliminating over 75% of applicants via brittle keyword matching, consuming hundreds of engineering hours in unstructured initial technical interviews, and abandoning disqualified candidates without diagnostic feedback.", p_body))
    story.append(Paragraph("Through the cohesive integration of four decoupled microservices, RecruitAI proves that automated talent acquisition can achieve high throughput without sacrificing fairness, transparency, or human agency. The empirical findings demonstrate that resumes can be parsed, sanitized of demographic PII, and categorized across 20 canonical IT roles in 151.35 milliseconds with 83.0% real-world accuracy; technical candidates can be autonomously interviewed with speech transcription below 8% WER and secure AST coding evaluation; hiring panels receive normalized candidate rankings (NDCG@5 = 0.892) grounded in Multi-Attribute Utility Theory and LambdaMART; and non-shortlisted candidates receive deterministic, acyclic learning roadmaps that elevate their simulated hireability by +38.4%. RecruitAI successfully transforms recruitment from a destructive filter into an empowering, circular talent pipeline.", p_body))
    story.append(Spacer(1, 4))

    # 8.2 Principal integrated contribution
    track('sec8_2')
    story.append(Paragraph("8.2 Principal integrated contribution", h_sec))
    story.append(Paragraph("The principal scientific and technological contributions produced by the research team extend significantly beyond the sum of the four individual components:", p_body))

    story.append(Paragraph("<b>1. The Closed-Loop Recruitment and Remediation Paradigm:</b> In traditional industrial hiring, rejection is terminal and silent. RecruitAI is the first integrated architecture to establish a circular talent feedback loop. By passing unshortlisted candidate representations directly from the ranking engine (Component 3) into the diagnostic career pathfinder (Component 4), the ecosystem automatically converts recruitment failure into structured upskilling, democratizing access to technical careers while creating a pre-qualified talent bench for subsequent hiring cycles.", p_bullet))
    story.append(Paragraph("<b>2. Architectural Decoupling with Strict Contract Determinism:</b> The team demonstrated that multi-modal artificial intelligence systems in high-stakes domains do not require monolithic, opaque deep neural networks. By partitioning the system into four autonomous microservices communicating via OpenAPI 3.0 REST contracts and Pydantic schemas, each service operates within its optimal computational paradigm: linear classification for sub-second intake triage (Port 8001), neural speech and AST sandboxing for interview evaluation (Port 8002), listwise learning-to-rank for decision support (Port 8003), and graph algorithms for career mobility (Port 8004).", p_bullet))
    story.append(Paragraph("<b>3. Systematic Forensic Auditing of Benchmark Leakage:</b> The group's empirical investigation proved that published state-of-the-art recruitment screening models reporting perfect F1 scores suffered from severe synthetic benchmark leakage and boilerplate memorization. By constructing an authentic, noise-injected evaluation corpus of 4,000 real-world resumes, the team established genuine, reproducible benchmarks for enterprise-grade talent software.", p_bullet))
    story.append(Paragraph("<b>4. Multi-Layered Algorithmic Fairness and Regulatory Compliance:</b> Rather than treating ethical compliance as a post-hoc audit, RecruitAI embeds compliance into every architectural layer. Automated PII scrubbing eliminates demographic bias at ingestion; interval union algebra prevents tenure inflation; AST sandboxing guarantees code execution safety; and deterministic MAUT formulation satisfies the stringent transparency and human-oversight mandates of the EU AI Act (High-Risk Annex III) and NYC Local Law 144.", p_bullet))
    story.append(Spacer(1, 4))

    # 8.3 Future directions
    track('sec8_3')
    story.append(Paragraph("8.3 Future directions", h_sec))
    story.append(Paragraph("To build upon the successful validation of the RecruitAI ecosystem, the research team outlines four prioritized future research and engineering trajectories:", p_body))

    story.append(Paragraph("<b>1. Multi-Modal Vision-Language Document Understanding:</b> While the current pipeline handles text-based PDF and DOCX files through layout-aware coordinate clustering, future iterations will integrate multi-modal document transformers (such as LayoutLMv3 or Donut). This will enable native parsing of complex graphic resumes, infographics, and visual portfolio submissions without relying on preliminary text extraction layers.", p_bullet))
    story.append(Paragraph("<b>2. Cross-Lingual and Multi-Dialect Acoustic Modeling:</b> Future enhancements to Component 2 will incorporate fine-tuned multilingual speech models (Whisper-large-v3 and MMS) trained on accented regional dialects (such as South Asian English accents and bilingual code-switching). This will ensure equitable interview evaluation across non-native English speakers in emerging technology hubs.", p_bullet))
    story.append(Paragraph("<b>3. Real-World Longitudinal Placement Validation:</b> While the current evaluation demonstrates high cross-validation accuracy and simulated hireability gains (+38.4%), longitudinal field trials tracking candidates over 12-month employment cycles will be conducted with partner enterprise firms. This will empirically quantify whether candidates recommended by RecruitAI exhibit superior long-term on-the-job retention and performance.", p_bullet))
    story.append(Paragraph("<b>4. Cryptographic Credential Verification and Blockchain Integration:</b> To eliminate fraudulent academic and employment claims entirely, future iterations will connect Component 1 with national education databases and decentralized identity protocols (W3C Verifiable Credentials). Verified digital diplomas and cryptographic employer signatures will be verified directly against national qualifications frameworks (SLQF and EQF) prior to semantic scoring.", p_bullet))
    story.append(Spacer(1, 6))

    # 8.4 Critical engineering lessons learned
    track('sec8_4')
    story.append(Paragraph("8.4 Critical engineering lessons learned", h_sec))
    story.append(Paragraph("The collaborative design and execution of RecruitAI yielded invaluable systems engineering and applied machine learning insights:", p_body))
    story.append(Paragraph("• <i>The Superiority of Interface-First Contracts:</i> Defining OpenAPI 3.0 specifications and Pydantic schemas in Sprint 1 prevented countless hours of schema drift and serialization friction. Contract tests caught payload deviations before model integration, proving that distributed AI systems require rigorous software engineering foundations.", p_bullet))
    story.append(Paragraph("• <i>Pragmatism in Model Selection:</i> Deep neural networks and LLMs are frequently over-prescribed in contemporary research. Our findings prove that balanced linear classifiers (LogReg) operating on dense domain features outperform multi-billion-parameter LLMs in latency, throughput, cost, and explainability for high-volume intake triage.", p_bullet))
    story.append(Paragraph("• <i>Security is Non-Negotiable in Automated Evaluation:</i> Implementing AST abstract syntax inspection proved vital. Sandboxing candidate code cannot rely on simple string filtering; lexical code analysis at the AST level is essential to guarantee complete containment against adversarial injection exploits.", p_bullet))
    story.append(Spacer(1, 6))

    # 8.5 Concluding remarks
    track('sec8_5')
    story.append(Paragraph("8.5 Concluding remarks", h_sec))
    story.append(Paragraph("In conclusion, the RecruitAI ecosystem represents a transformative step forward for the global knowledge economy. By aligning algorithmic precision with ethical responsibility, the research proves that corporate talent acquisition can be automated without dehumanization. Candidates are no longer discarded into silence; they are evaluated on merit, verified on authentic code, and empowered with clear, constructive pathways to achieve their professional potential. RecruitAI models a future where artificial intelligence and human talent work in transparent, mutually elevating harmony.", p_body))
    story.append(Spacer(1, 10))

    story.append(PageBreak())
    return story
