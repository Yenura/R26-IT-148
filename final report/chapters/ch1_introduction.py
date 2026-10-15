import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_ch1(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker=None):
    PRIMARY = colors.HexColor("#1A365D")
    SECONDARY = colors.HexColor("#2B6CB0")
    DARK_TEXT = colors.HexColor("#2D3748")

    ch_num_style = styles['ChapterNumber']
    ch_title_style = styles['ChapterTitle']
    h1_style = styles['Heading1_Custom']
    h2_style = styles['Heading2_Custom']
    body_style = styles['Body_Custom']
    body_bold = styles['Body_Bold']

    # Page tracking hook if available
    if tracker is not None:
        from generate_dissertation import PageTracker
        story.append(PageTracker('ch1', tracker))

    # CHAPTER 1 HEADER
    story.append(p("CHAPTER 1", ch_num_style))
    story.append(p("INTRODUCTION", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))

    # 1.1 CONTEXT AND GLOBAL RECRUITMENT LANDSCAPE
    if tracker is not None:
        story.append(PageTracker('sec1_1', tracker))
    story.append(p("1.1 Context and Global Recruitment Landscape", h1_style))
    story.append(p("Over the past decade, technical talent acquisition in the software engineering sector has experienced a profound shift driven by two opposing pressures: a rapid growth in specialized technical requisitions and a massive influx of digital applications. As modern engineering organizations transition toward distributed cloud architectures, containerized microservices, and specialized data engineering stacks, job specifications have become increasingly detailed. Concurrently, one-click online application workflows and generative resume drafting tools have drastically reduced the friction of submitting applications. Consequently, a single engineering opening posted by a multinational technology firm often attracts thousands of heterogeneous resumes within days of publication (Sackett et al., 2022)."))
    story.append(p("Human hiring panels and engineering leads cannot manually read and evaluate thousands of multi-page technical CVs within viable operational timelines. As a result, corporate recruitment universally relies on automated Applicant Tracking Systems (ATS) as front-line gatekeepers. Industry surveys report that more than 98% of Fortune 500 companies and roughly 75% of high-growth technology firms deploy automated screening parsers to filter incoming candidates before any recruiter reads a profile (Zhang et al., 2023). In practice, this automated triage layer acts as a critical filter: it determines which candidates proceed to technical assessment and which are discarded without manual review."))
    story.append(p("From an operational perspective, the technical hiring funnel functions as a multi-stage funnel. An initial pool of N_0 applicants passes through automated ATS triage (N_1), initial recruiter screening (N_2), technical coding assessment (N_3), architecture interviews (N_4), and final offer negotiations (N_5). In typical enterprise settings, N_1 / N_0 drops to approximately 0.25 (a 75% attrition rate at the automated gateway), whereas final offers (N_5 / N_0) represent less than 1% of total applications. When the initial automated screening step depends on brittle keyword counts or naive text parsing, errors introduced at stage N_1 propagate downstream, permanently eliminating capable candidates before human evaluation can occur."))

    # TABLE 1.1 RECRUITMENT FUNNEL METRICS
    funnel_table_data = [
        [p("<b>Recruitment Funnel Stage</b>", body_style), p("<b>Volume (per 1,000 Apps)</b>", body_style), p("<b>Typical Drop-off (%)</b>", body_style), p("<b>Legacy ATS Failure Mode</b>", body_style)],
        [p("1. Ingestion &amp; Parsing", body_style), p("1,000 applicants", body_style), p("0.0% (Intake baseline)", body_style), p("Multi-column layout gluing, text scrambling", body_style)],
        [p("2. Automated ATS Screen", body_style), p("250 applicants", body_style), p("75.0% automated drop", body_style), p("Premature rejection of qualified non-keyword CVs", body_style)],
        [p("3. Recruiter Review", body_style), p("60 applicants", body_style), p("76.0% manual screen drop", body_style), p("Recruiter fatigue, high scoring variance", body_style)],
        [p("4. Technical Assessment", body_style), p("15 applicants", body_style), p("75.0% technical drop", body_style), p("Keyword-stuffed candidates fail coding basics", body_style)],
        [p("5. On-site Interview &amp; Offer", body_style), p("3 offers (1 hire)", body_style), p("80.0% interview drop", body_style), p("High mis-hire cost ($4,129 average)", body_style)]
    ]
    funnel_table = Table(funnel_table_data, colWidths=[120, 115, 105, 147])
    funnel_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(funnel_table)
    story.append(p("Table 1.1: Enterprise Technical Recruitment Funnel Drop-Off Metrics and ATS Failure Points.", caption_style))
    story.append(sp(6))

    # 1.2 ECONOMIC AND TALENT TOLL
    if tracker is not None:
        story.append(PageTracker('sec1_2', tracker))
    story.append(p("1.2 Operational and Financial Costs of Screening Inefficiencies", h1_style))
    story.append(p("Although automated parsers are ubiquitous, traditional commercial tools introduce substantial friction into technical hiring. When recruiters perform manual triage, field studies in engineering centers across South Asia and multinational offshore teams indicate that reviewers spend an average of 4.2 minutes per resume. Screening a cohort of 2,000 applications thus requires approximately 140 hours of manual effort. Fatigue also leads to noticeable evaluation variance: resumes reviewed at the start of a screening shift frequently receive higher ratings than comparable resumes reviewed hours later under cognitive strain (Sackett et al., 2022)."))
    story.append(p("Conversely, delegating triage to legacy keyword-matching engines often degrades candidate quality rather than enhancing it. In our audit of 500 candidate profiles eliminated by standard keyword filters, 28.4% demonstrated proven production experience in the requisite engineering domains, but used alternative phrasings (such as describing 'distributed messaging pipelines' instead of explicitly writing 'Apache Kafka', or detailing 'container orchestration' without the literal keyword 'Kubernetes'). At the same time, over 34% of applicants who advanced to coding assessments struggled with basic software design principles, having passed initial screening by packing unverified skill lists into their resumes. This mismatch carries significant organizational costs, with industry estimates averaging $4,129 per technical mis-hire and extending requisition cycles to 48 business days. These figures highlight the pressing need for semantic, evidence-weighted document screening."))

    # 1.3 SYSTEMIC FAILURE MODES
    if tracker is not None:
        story.append(PageTracker('sec1_3', tracker))
    story.append(p("1.3 Structural Limitations in Current ATS Platforms", h1_style))
    story.append(p("Through systematic empirical analysis of hiring workflows and existing natural language processing (NLP) screening algorithms, this research identifies four primary structural limitations in contemporary tools:"))
    story.append(b("<b>1. Syntactic Brittleness and Polysemous Token Collisions:</b> General-purpose regular expressions and off-the-shelf NLP tokenizers frequently mishandle programming language names. Single-letter identifiers ('C', 'R'), common English verbs ('Go', 'Rust'), framework designations ('Spring'), and architectural terms ('REST') frequently collide with everyday conversational English (for example, 'go to market', 'in C-level discussions', 'graduated in spring', 'the rest of the team'). Without structural boundary safeguards, screening engines generate extensive false-positive skill detections."))
    story.append(b("<b>2. Temporal Experience Conflation and Duration Doubling:</b> Most resume parsers estimate professional tenure using naive subtraction between calendar years without underlying set-theoretic logic. When candidates maintain concurrent engagements - such as simultaneous freelance consulting, part-time research, and startup roles - simple date addition aggregates each interval independently, artificially inflating commercial experience by two or three times. Furthermore, legacy parsers fail to separate university course projects from verified employment tenure, allowing recent graduates to claim senior engineering experience based on classroom assignments."))
    story.append(b("<b>3. Collapse of Multi-Dimensional Qualifications:</b> Commercial screening engines routinely compress distinct candidate attributes - such as verified technical skills, commercial tenure, and educational attainment - into an opaque composite percentage match score. This unweighted reduction treats unrelated non-technical degrees on par with accredited computer science credentials, ignores whether an engineering tool was utilized in production or merely listed in a bulleted inventory, and deprives hiring managers of auditable mathematical justification."))
    story.append(b("<b>4. Synthetic Benchmark Leakage in Academic Literature:</b> A substantial body of published research in automated resume parsing and role classification claims near-perfect evaluation results (Macro F1 = 1.0). As our forensic audit demonstrates, these published models were trained and tested on synthetic datasets produced by rigid template engines. Classifiers simply memorized invariant boilerplate paragraphs and target-class headers rather than learning authentic competency patterns, leading to total classification failure when tested on authentic, unstructured resumes."))

    # 1.4 RESEARCH MOTIVATION & PROBLEM FORMULATION
    if tracker is not None:
        story.append(PageTracker('sec1_4', tracker))
    story.append(p("1.4 Research Motivation & Problem Formulation", h1_style))
    story.append(p("Mathematically, candidate evaluation in automated recruitment can be formulated as a multi-criteria decision problem over high-dimensional, unstructured, and partially verified candidate representations. Let an incoming resume document be denoted by D in the document space D_all. The extraction objective is to map D into a structured candidate representation vector C = (K_cand, T_cand, E_cand) and a predicted role label y in {1, 2, ..., K}, while evaluating alignment against a job requisition J = (K_req, T_req, E_req)."))
    story.append(p("We formalize three primary analytical domains:"))
    story.append(b("• <b>Technical Competency Space K:</b> A structured lexicon of over 400 canonical software tools, programming languages, and frameworks K = {s_1, s_2, ..., s_M}, where each extracted skill s_i is associated with an evidentiary weight E(s_i) in [0.0, 1.0] derived from its document context."))
    story.append(b("• <b>Temporal Experience Space T:</b> A collection of verified, non-overlapping calendar intervals {[s_k, e_k]}_{k=1}^P in R_+ that disambiguates total commercial tenure E_tot, IT-sector tenure E_it, and target-role-relevant exposure E_rel."))
    story.append(b("• <b>Academic Qualification Space E:</b> A two-dimensional tuple (L_deg, M_field) in [0, 100] x [0.2, 1.0] that decouples degree attainment tier from disciplinary field relevance."))
    story.append(p("While conventional screening systems approximate candidate suitability through an unweighted scalar score f(D, J) in [0, 1], rigorous technical recruitment demands a transparent and decoupled mapping. Here, technical competencies, verified commercial tenure, and academic credentials are independently extracted, mathematically validated, and exposed as an uncollapsed vector S_C1 = [S_skill, S_exp, S_edu]. The core motivation of this dissertation is to design, implement, and empirically validate this end-to-end framework."))

    # FIGURE 1.1 RECRUITAI MACRO ARCHITECTURE
    fig_path = os.path.join(fig_dir, "fig6_macro_architecture.png")
    if os.path.exists(fig_path):
        story.append(sp(6))
        story.append(Image(fig_path, width=460, height=239))
        story.append(p("Figure 1.1: Multi-Microservice Architecture of the RecruitAI Ecosystem (Research Project: R26-IT-148).", caption_style))
        story.append(sp(6))

    # 1.5 RESEARCH OBJECTIVES & SPECIFIC C1 SCOPE
    if tracker is not None:
        story.append(PageTracker('sec1_5', tracker))
    story.append(p("1.5 Research Objectives & Specific Scope of Component 1", h1_style))
    story.append(p("The overarching mission of the <b>RecruitAI</b> research initiative (Project ID: R26-IT-148) is to engineer an integrated, fair, and multi-modal technical hiring ecosystem combining resume screening, autonomous technical interviews, listwise candidate ranking, and skill gap remediation. Within this four-part platform, <b>Component 1 (C1)</b> serves as the primary intake intelligence gateway."))
    story.append(p("The specific scientific and software engineering objectives of Component 1 are defined as follows:"))
    story.append(b("<b>Objective 1: Format-Agnostic Layout-Aware Ingestion:</b> Implement a robust document ingestion pipeline for heterogeneous PDF and DOCX resumes that normalizes layout artifacts, parses section boundaries via finite state automata, and redacts Personally Identifiable Information (PII) to prevent demographic bias."))
    story.append(b("<b>Objective 2: Boundary-Guarded Named Entity Recognition (NER):</b> Engineer a high-precision NER engine covering over 400 technical competencies across 7 IT sub-disciplines, utilizing context-guarded look-around assertion windows to eliminate polysemous false positives."))
    story.append(b("<b>Objective 3: Temporal Experience Algebra &amp; Disambiguation:</b> Formalize a calendar interval union algebra that resolves overlapping employment dates, separates academic projects from formal employment, and categorizes tenure into Total Experience (E_tot), IT-Sector Tenure (E_it), and Target-Role-Relevant Exposure (E_rel)."))
    story.append(b("<b>Objective 4: Two-Dimensional Academic Decoupling:</b> Establish an educational qualification ontology that strictly separates academic degree attainment tier level (Ph.D., M.Sc., B.Sc., Diploma) from disciplinary field relevance (Core Computing, Adjacent Quantitative, Non-Technical)."))
    story.append(b("<b>Objective 5: Evidence-Weighted Technical Skill Scoring:</b> Formulate an evidence hierarchy that weights technical skills based on contextual usage, distinguishing isolated bullet point mentions (w = 0.40) from verified commercial employment duties (w = 1.00)."))
    story.append(b("<b>Objective 6: Balanced 20-Class Role Classification:</b> Train, validate, and tune a balanced multinomial Logistic Regression model using sublinear TF-IDF vectorization across 20 canonical IT roles, achieving &gt;85% test accuracy on authentic held-out data with sub-5ms inference latency."))
    story.append(b("<b>Objective 7: Independent Tri-Pillar Output Contract:</b> Expose an uncollapsed feature vector (S_skill, S_exp, S_edu) on Port 8001 providing an interpretable, mathematically auditable contract for downstream ranking and interview orchestration."))

    # 1.6 RESEARCH QUESTIONS & HYPOTHESES
    if tracker is not None:
        story.append(PageTracker('sec1_6', tracker))
    story.append(p("1.6 Research Questions and Formal Hypotheses", h1_style))
    story.append(p("This dissertation investigates and resolves five primary research questions:"))
    story.append(b("<b>RQ1:</b> Can context-guarded regular expression look-around assertion windows eliminate subtoken collisions for polysemous programming language identifiers without sacrificing recall across diverse document layouts?<br/><i>Hypothesis H1:</i> Non-capturing regex assertions with structural boundary checks reduce false-positive skill matches by &gt;95% on conversational English tokens compared to unshielded substring matching."))
    story.append(b("<b>RQ2:</b> To what extent does chronological interval union algebra prevent tenure inflation in technical resumes containing concurrent freelance and corporate employment records?<br/><i>Hypothesis H2:</i> Set-theoretic interval union merging eliminates artificial duration doubling, bounding candidate commercial tenure strictly within calendar elapsed limits."))
    story.append(b("<b>RQ3:</b> Does decoupling academic degree tier level from disciplinary field relevance improve qualification scoring fidelity compared to monolithic degree tiering?<br/><i>Hypothesis H3:</i> Decoupled two-dimensional scoring prevents non-technical advanced degrees (e.g., Ph.D. in Literature) from scoring higher than computer science Bachelor degrees for software engineering roles."))
    story.append(b("<b>RQ4:</b> Can a balanced linear multinomial classifier with sublinear TF-IDF achieve classification accuracy comparable to fine-tuned deep transformers (DistilBERT) while delivering sub-5ms latency for enterprise ingestion?<br/><i>Hypothesis H4:</i> Balanced logistic regression achieves within 3% of DistilBERT accuracy while executing inference in &lt;3ms per resume, yielding a 50x throughput gain."))
    story.append(b("<b>RQ5:</b> Are the empirical feature importance contributions of technical skills, commercial tenure, and education consistent with the deployed 0.50 / 0.30 / 0.20 tri-pillar scoring weights?<br/><i>Hypothesis H5:</i> Permutation feature importance confirms skills as the primary discriminative signal (&gt;80%), while commercial tenure and education provide vital boundary constraints."))

    # 1.7 METHODOLOGY & ENGINEERING LIFECYCLE
    if tracker is not None:
        story.append(PageTracker('sec1_7', tracker))
    story.append(p("1.7 Research Methodology & Engineering Lifecycle", h1_style))
    story.append(p("This research follows the Design Science Research (DSR) methodology for applied machine learning and information systems (Hevner et al., 2004). The engineering lifecycle encompasses six iterative phases: (1) problem analysis and empirical failure identification across existing enterprise pipelines; (2) mathematical formalization of extraction algebras and classification objectives; (3) software design and implementation of modular microservice components in Python 3.12 and FastAPI; (4) experimental validation on a curated corpus of 4,000 authentic resumes; (5) forensic auditing of synthetic benchmark leakage; and (6) production deployment verified by 195 automated Pytest assertions."))

    # 1.8 SCOPE, DELIMITATIONS & ETHICAL BOUNDARIES
    if tracker is not None:
        story.append(PageTracker('sec1_8', tracker))
    story.append(p("1.8 Scope, Boundaries, and Delimitations", h1_style))
    story.append(p("The scope of this research centers on text-based resume parsing, technical entity extraction, IT job role classification, and qualification scoring across 20 canonical software engineering specializations. The system processes English-language resumes in PDF, DOCX, and TXT formats. Rasterized image scans requiring Optical Character Recognition (OCR), video assessments, and conversational speech interviews fall outside the boundaries of Component 1 and are handled by the multi-modal interview subsystems in Component 2."))
    story.append(p("From an ethical and legal standpoint, Component 1 enforces automated PII redaction (names, phone numbers, email addresses, street addresses, and social profile links) prior to feature synthesis. This ensures that downstream role prediction and scoring are demographically blind, aligning with the EU AI Act (Annex III) and NYC Local Law 144 standards for automated employment decision tools."))

    # 1.9 PRIMARY TECHNICAL CONTRIBUTIONS
    if tracker is not None:
        story.append(PageTracker('sec1_9', tracker))
    story.append(p("1.9 Summary of Primary Technical Contributions", h1_style))
    story.append(p("The core scientific and engineering contributions presented in this dissertation are:"))
    story.append(b("1. <b>Layout-Aware Document Processing &amp; PII Redaction:</b> A robust ingestion pipeline that normalizes multi-column PDF layouts, resolves character ligatures, and sanitizes personal identifying data."))
    story.append(b("2. <b>Boundary-Guarded NER Engine:</b> A 400+ competency technical skill taxonomy protected by regex look-around assertion shields that eliminate false positive collisions on polysemous terms."))
    story.append(b("3. <b>Temporal Experience Union Algebra:</b> A mathematical interval union algorithm resolving overlapping concurrent employment and filtering academic projects from commercial tenure."))
    story.append(b("4. <b>Decoupled Two-Dimensional Academic Model:</b> A qualification ontology separating degree tier level from field relevance, preventing non-technical degree inflation."))
    story.append(b("5. <b>Contextual Evidence-Weighted Skill Scoring:</b> A hierarchical weighting system that rewards verified workplace execution (w = 1.0) over isolated keyword mentions (w = 0.40)."))
    story.append(b("6. <b>Balanced 20-Class Role Classifier:</b> A production multinomial Logistic Regression classifier achieving 87.42% accuracy and 92.47% Macro F1 on 819 held-out authentic resumes with 2.4ms inference."))
    story.append(b("7. <b>Forensic Leakage Audit of Academic Baselines:</b> An empirical demonstration of template memorization in published recruitment literature, resolving the historical F1 = 1.0 artifact."))
    story.append(b("8. <b>Automated Pytest Verification Suite:</b> A comprehensive suite of 195 unit and integration tests executing in 79.60s with 100% pass rate across all modules."))

    # 1.10 ROADMAP
    if tracker is not None:
        story.append(PageTracker('sec1_10', tracker))
    story.append(p("1.10 Dissertation Organization and Roadmap", h1_style))
    story.append(p("The remainder of this dissertation is organized as follows: Chapter 2 reviews foundational literature in ATS parsing, NLP entity extraction, temporal logic, and synthetic leakage vulnerabilities. Chapter 3 presents the architectural design, mathematical formalizations, and extraction algorithms. Chapter 4 documents the software engineering implementation, microservice design, and automated testing suite. Chapter 5 details empirical results, per-class metrics, ablation studies, and latency benchmarks. Chapter 6 examines algorithmic fairness, PII blinding, SHAP explainability, and regulatory compliance. Chapter 7 concludes the dissertation with key achievements and future research directions."))
    story.append(PageBreak())
