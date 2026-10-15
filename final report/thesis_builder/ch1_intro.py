import os
from reportlab.platypus import Paragraph, Spacer, Image, PageBreak
from thesis_builder.styles import clean_xml, create_table_box, PRINTABLE_WIDTH
from thesis_builder.canvas_helper import PageTracker

def append_ch1(story, styles, fig_dir, tracker=None):
    p_body = styles['ThesisBody']
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

    # 1 INTRODUCTION
    track('ch1')
    story.append(Paragraph("1 INTRODUCTION", h_ch))
    story.append(Spacer(1, 4))

    # 1.1 Overall project context
    track('sec1_1')
    story.append(Paragraph("1.1 Overall project context", h_sec))
    story.append(Paragraph("In modern corporate talent acquisition, software engineering recruitment has escalated into an acute operational challenge characterized by high application volumes, extreme domain specialization, and severe cognitive strain on human reviewers. As enterprises transition toward distributed cloud architectures, containerized microservices, high-throughput streaming systems, and applied machine learning pipelines, technical role specifications have become exceptionally granular. Simultaneously, the proliferation of one-click digital application portals and automated resume drafting utilities has lowered the marginal cost of applying for vacancies to near zero. As an empirical consequence, an individual engineering requisition published by a technology organization routinely attracts thousands of heterogeneous curriculum vitae (CV) documents within hours of posting (Sackett et al., 2022).", p_body))
    story.append(Paragraph("Because human hiring panels cannot manually scrutinize thousands of multi-page technical resumes within commercially viable hiring cycles, corporate recruitment universally deploys automated Applicant Tracking Systems (ATS) as front-line gatekeepers. Industry empirical benchmarks indicate that over 98% of Fortune 500 corporations and more than 75% of high-growth technology enterprises mandate algorithmic screening prior to human recruiter engagement (Zhang et al., 2023). In operational practice, this intake gatekeeper decides which candidates proceed to technical assessment and which are eliminated without manual review.", p_body))
    story.append(Paragraph("The enterprise hiring process is structurally modeled as a multi-stage funnel. Beginning with an intake cohort of N_0 applicants, each successive evaluation gate retains only a fraction of candidates: automated ATS parsing and filtering (N_1), recruiter portfolio triage (N_2), interactive technical assessment (N_3), architecture panel interview (N_4), and final executive offer negotiations (N_5). Table 1.1 delineates an illustrative attrition trajectory across 1,000 applications in a modern technical recruitment pipeline.", p_body))
    story.append(Spacer(1, 4))

    track('tab1_1')
    story.append(Paragraph("Table 1.1: Enterprise technical recruitment funnel drop-off metrics and ATS failure points.", caption_tab))
    funnel_data = [
        [Paragraph("<b>Funnel Stage</b>", cell_bold), Paragraph("<b>Volume (per 1,000 Apps)</b>", cell_bold), Paragraph("<b>Drop-Off (%)</b>", cell_bold), Paragraph("<b>Typical Failure Mode of Keyword ATS</b>", cell_bold)],
        [Paragraph("1. Ingestion &amp; Parsing", cell), Paragraph("1,000 applicants", cell), Paragraph("Baseline (0%)", cell), Paragraph("Multi-column layout gluing, character scrambling", cell)],
        [Paragraph("2. Automated ATS Screen", cell), Paragraph("250 applicants", cell), Paragraph("75.0% drop", cell), Paragraph("Premature rejection of qualified non-keyword CVs", cell)],
        [Paragraph("3. Recruiter Review", cell), Paragraph("60 applicants", cell), Paragraph("76.0% drop", cell), Paragraph("Recruiter fatigue, subjective scoring inconsistency", cell)],
        [Paragraph("4. Technical Assessment", cell), Paragraph("15 applicants", cell), Paragraph("75.0% drop", cell), Paragraph("Keyword-stuffed profiles fail basic coding tasks", cell)],
        [Paragraph("5. Interview &amp; Offer", cell), Paragraph("3 offers (1 hire)", cell), Paragraph("80.0% drop", cell), Paragraph("Substantial mis-hire replacement overhead", cell)],
    ]
    funnel_tab = create_table_box(funnel_data, [105, 95, 75, 136], styles, is_header=True)
    story.append(funnel_tab)
    story.append(Spacer(1, 8))

    story.append(Paragraph("To address this recruitment challenge holistically, the Sri Lanka Institute of Information Technology (SLIIT) research initiative <b>RecruitAI</b> (Research Project Identifier: <b>R26-IT-148</b>) formulates an integrated, multi-modal, artificial intelligence-driven recruitment ecosystem. All official research documents, presentation slides, and technical dissemination artifacts are hosted at our publication portal: https://r26-it-148-website.yenura02.workers.dev/. The platform couples four cooperating microservices: (1) Automated Resume Screening and IT Job Role Classification (Port 8001); (2) Autonomous Multi-Modal Technical Interview System (Port 8002); (3) Multi-Criteria Candidate Ranking Engine (Port 8003); and (4) Predictive Skill-Gap and Career Pathfinding System (Port 8004). Figure 1.1 illustrates the macro-architectural interaction topology.", p_body))
    story.append(Spacer(1, 4))

    # Figure 1.1
    fig_macro = os.path.join(fig_dir, "fig6_macro_architecture.png")
    if os.path.exists(fig_macro):
        track('fig1_1')
        story.append(Image(fig_macro, width=410, height=213))
        story.append(Paragraph("Figure 1.1: Multi-microservice architecture of the RecruitAI ecosystem (R26-IT-148).", caption_fig))
        story.append(Spacer(1, 6))

    # 1.2 Individual component context
    track('sec1_2')
    story.append(Paragraph("1.2 Individual component context", h_sec))
    story.append(Paragraph("Within the distributed RecruitAI platform, <b>Component 1 (Port 8001)</b>, developed by the author (D. T. D. Perera, Student ID: IT22089236), serves as the foundational intake intelligence gateway. Component 1 is tasked with converting completely unstructured, format-diverse resumes (PDF, DOCX, TXT) into auditable, mathematically verified candidate competency profiles. Because Component 1 functions at the entry boundary of the recruitment funnel, any extraction bias, syntactic parsing failure, or misclassification produced at this intake stage propagates downstream into Component 2's interview question generation and Component 3's candidate ranking matrix.", p_body))
    story.append(Paragraph("Component 1 executes layout-aware document ingestion, automated Personally Identifiable Information (PII) sanitization, boundary-guarded Named Entity Recognition (NER) across 400+ technical competencies, temporal experience algebra for chronological deduplication, two-dimensional academic credential evaluation, and 20-class multinomial logistic role classification. Most importantly, Component 1 rejects monolithic, opaque scalar scoring, exposing an uncollapsed Tri-Pillar Qualification Vector S_C1 = [S_skill, S_exp, S_edu] that guarantees auditable transparency.", p_body))

    # 1.3 Problem statement
    track('sec1_3')
    story.append(Paragraph("1.3 Problem statement", h_sec))
    story.append(Paragraph("Despite widespread enterprise adoption, conventional automated resume screening systems suffer from four systemic technical failure modes:", p_body))
    story.append(Paragraph("<b>1. Polysemous Token Collisions:</b> Software engineering vocabularies contain extensive lexical overlap with natural conversational English. Single-letter programming languages ('C', 'R'), common English verbs ('Go', 'Rust'), framework designations ('Spring'), and architectural paradigms ('REST') frequently collide with standard prose (e.g., 'go to production', 'spring internship', 'the rest of the team'). Without contextual boundary safeguards, naive tokenizers produce severe false-positive skill attributions.", p_bullet))
    story.append(Paragraph("<b>2. Temporal Experience Inflation:</b> Standard parsers compute professional tenure by naively subtracting start dates from end dates or summing distinct job spans. When applicants engage in concurrent freelance consulting, part-time startup advisory, and corporate roles, simple addition aggregates overlapping calendar spans independently, artificially inflating commercial experience by 50% to 100%. Furthermore, legacy parsers fail to distinguish academic course projects from commercial employment.", p_bullet))
    story.append(Paragraph("<b>3. Collapsed Monolithic Qualifications:</b> Commercial tools routinely compress heterogeneous candidate attributes (skills, tenure, and degrees) into a single scalar match percentage. This monolithic collapse obscures why a candidate scored poorly, equates non-technical doctorates with technical undergraduate degrees, and rewards superficial keyword stuffing over verified production usage.", p_bullet))
    story.append(Paragraph("<b>4. Synthetic Benchmark Leakage:</b> A substantial body of published literature in automated resume parsing reports near-perfect classification scores (F1 = 1.0) on public datasets. Forensic audit reveals that these corpora consist of template-generated synthetic resumes where models memorized invariant boilerplate paragraphs and explicit role headers rather than learning authentic competency semantics.", p_bullet))

    # 1.4 Research gap
    track('sec1_4')
    story.append(Paragraph("1.4 Research gap", h_sec))
    story.append(Paragraph("Existing commercial systems (such as Workday and Taleo) operate as closed-box proprietary engines that hide matching heuristics, while popular open-source packages (such as pyresparser and standard spaCy pipelines) rely on unweighted dictionary lookups that lack polysemy shielding and temporal algebra. Neither commercial nor open-source systems implement contextual evidence weighting to differentiate isolated skill mentions from workplace execution, nor do they decouple academic degree attainment level from disciplinary field relevance. This leaves an acute research gap for a fast, explainable, and scientifically validated intake screening microservice.", p_body))

    # 1.5 Aim and objectives
    track('sec1_5')
    story.append(Paragraph("1.5 Aim and objectives", h_sec))
    story.append(Paragraph("The primary aim of this research is to design, implement, and validate an auditable, high-throughput, and fair semantic resume screening and job role classification microservice that addresses the four structural failure modes identified above.", p_body))
    story.append(Paragraph("The specific research and engineering objectives are:", p_body))
    story.append(Paragraph("1. <b>Layout-Aware Ingestion and PII Sanitization:</b> Implement a multi-format ingestion pipeline supporting PDF and DOCX documents that normalizes multi-column layouts and redacts Personally Identifiable Information.", p_bullet))
    story.append(Paragraph("2. <b>Boundary-Guarded Named Entity Recognition:</b> Construct a domain ontology of over 400 IT competencies across seven disciplines, protected by context-guarded regular expression look-around assertions.", p_bullet))
    story.append(Paragraph("3. <b>Temporal Experience Algebra:</b> Formalize a calendar interval union algorithm that merges overlapping employment spans, separates coursework projects from corporate tenure, and computes disjoint commercial tenure.", p_bullet))
    story.append(Paragraph("4. <b>Two-Dimensional Credential Decoupling:</b> Develop an educational evaluation model that separates academic degree tier level from disciplinary field relevance.", p_bullet))
    story.append(Paragraph("5. <b>Contextual Evidence-Weighted Skill Scoring:</b> Formulate a hierarchical scoring scheme that assigns distinct evidentiary weights to isolated mentions (0.40), technical projects (0.70), and verified workplace execution (1.00).", p_bullet))
    story.append(Paragraph("6. <b>High-Fidelity 20-Class Role Classification:</b> Train, tune, and evaluate a balanced multinomial logistic regression classifier on 67 dense normalized features, targeting &gt;85% test accuracy on authentic held-out data with &lt;5 ms inference latency.", p_bullet))
    story.append(Paragraph("7. <b>Tri-Pillar Output Contract:</b> Expose the uncollapsed qualification vector S_C1 = [S_skill, S_exp, S_edu] via RESTful API on Port 8001 for downstream candidate ranking and interview orchestration.", p_bullet))

    # 1.6 Research questions or hypotheses
    track('sec1_6')
    story.append(Paragraph("1.6 Research questions or hypotheses", h_sec))
    story.append(Paragraph("This investigation addresses five formal research questions and testable hypotheses:", p_body))
    story.append(Paragraph("<b>RQ1:</b> Can context-guarded regular-expression look-around assertions eliminate token collisions for ambiguous technical identifiers without sacrificing extraction recall? <i>Hypothesis H1: Guarded patterns reduce false-positive matches on everyday conversational English by more than 95% compared with unguarded substring matching.</i>", p_bullet))
    story.append(Paragraph("<b>RQ2:</b> To what extent does interval-union calendar algebra eliminate tenure inflation caused by concurrent employment contracts? <i>Hypothesis H2: Merging overlapping employment intervals mathematically bounds calculated tenure by total elapsed calendar time, eliminating artificial inflation.</i>", p_bullet))
    story.append(Paragraph("<b>RQ3:</b> Does decoupling degree tier level from field relevance yield fairer qualification scoring than monolithic degree hierarchies? <i>Hypothesis H3: A two-dimensional qualification model prevents non-technical doctoral degrees from outscoring relevant computing bachelor's degrees for technical software roles.</i>", p_bullet))
    story.append(Paragraph("<b>RQ4:</b> Can a balanced linear classifier achieve classification performance competitive with deep transformer architectures while satisfying strict real-time latency constraints? <i>Hypothesis H4: Balanced multinomial logistic regression achieves classification accuracy within 3% of fine-tuned DistilBERT while executing in under 3 ms per inference.</i>", p_bullet))
    story.append(Paragraph("<b>RQ5:</b> Do empirical feature importance metrics support the deployed Tri-Pillar weights of 0.50 (skills), 0.30 (experience), and 0.20 (education)? <i>Hypothesis H5: Technical skills contribute over 80% of permutation feature importance in role classification, with experience and education acting as supporting constraints.</i>", p_bullet))

    # 1.7 Scope limitations and assumptions
    track('sec1_7')
    story.append(Paragraph("1.7 Scope limitations and assumptions", h_sec))
    story.append(Paragraph("The scope of Component 1 encompasses English-language technical resumes submitted in PDF, DOCX, and TXT formats for 20 canonical information technology roles. Scanned raster images requiring Optical Character Recognition (OCR), portfolio media, video presentations, and oral interviews are outside the scope of Component 1 and are delegated to Component 2. The pipeline assumes that candidate resumes represent authentic self-reported claims, relying on downstream interview validation to catch fraudulent assertions. PII redaction strips demographic identifiers at the ingestion boundary to satisfy regulatory governance under the EU AI Act (Annex III) and NYC Local Law 144.", p_body))

    # 1.8 Individual contribution
    track('sec1_8')
    story.append(Paragraph("1.8 Individual contribution", h_sec))
    story.append(Paragraph("The author, D. T. D. Perera (IT22089236), conducted the research and engineering work for Component 1, comprising: (1) design and implementation of the format-agnostic document ingestion and PII redaction pipeline; (2) compilation of the 400+ competency taxonomy and context-guarded regex shields; (3) formulation and coding of the interval union temporal algebra; (4) development of the two-dimensional academic credential ontology; (5) formulation of the evidence-weighted skill scoring algorithm; (6) engineering of the dense 67-feature vector space and balanced multinomial logistic classifier; (7) forensic auditing of synthetic benchmark leakage; (8) authoring of the 195-test automated Pytest verification suite; and (9) integration of the FastAPI microservice on Port 8001.", p_body))

    # 1.9 Thesis structure
    track('sec1_9')
    story.append(Paragraph("1.9 Thesis structure", h_sec))
    story.append(Paragraph("The remainder of this dissertation is organized as follows: Chapter 2 reviews related literature and existing systems. Chapter 3 establishes the research methodology, data corpora, and experimental protocols. Chapter 4 details the product and solution design. Chapter 5 documents the implementation, API contracts, and testing suite. Chapter 6 presents empirical results, per-class evaluations, and ablation studies. Chapter 7 discusses findings, limitations, and ethical implications. Chapter 8 evaluates commercialisation, business models, and sustainability. Chapter 9 concludes with research achievements and future directions, followed by References, Glossary, and Appendices.", p_body))
    story.append(PageBreak())
