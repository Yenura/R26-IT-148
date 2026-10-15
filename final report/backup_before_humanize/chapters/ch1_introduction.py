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
    story.append(p("In contemporary global enterprise talent acquisition, the information technology (IT) sector operates under an unprecedented combination of exponential applicant volume, hyper-specialized technical role demands, and acute cognitive fatigue among human hiring panels. The rapid expansion of enterprise cloud architectures, distributed microservices, containerization ecosystems, and artificial intelligence platforms has intensified the demand for specialized software engineering talent. However, this heightened demand is mirrored by an overwhelming supply of digital applications: a single technical requisition posted by a multinational technology enterprise routinely attracts thousands of heterogeneous resumes within days of publication (Sackett et al., 2022)."))
    story.append(p("Because human recruitment panels and engineering leads cannot manually scrutinize thousands of multi-page technical resumes within strict operational deadlines, organizations universally rely on automated Applicant Tracking Systems (ATS) to manage resume intake and perform preliminary candidate filtering. Recent talent acquisition benchmarks indicate that over 98% of Fortune 500 corporations and more than 75% of high-growth technology enterprises deploy automated parsing systems as their initial hiring gateway (Zhang et al., 2023). In this industrial ecosystem, the automated screening engine serves as an authoritative filter, deciding which candidates are elevated for interview assessment and which are discarded without human review."))
    story.append(p("The enterprise recruitment funnel can be modeled as a multi-stage probabilistic filter. For an initial applicant pool of N_0 candidates, applicants undergo successive evaluation stages: automated ATS parsing (N_1), recruiter screening (N_2), technical coding assessment (N_3), architecture interview (N_4), and final offer extension (N_5). Empirical metrics indicate that N_1 / N_0 routinely drops to 0.25 (a 75% rejection rate at the automated gateway), while N_5 / N_0 represents less than 0.01 (1%). When the initial ATS stage relies on brittle keyword counts, the error introduced at N_1 propagates catastrophically down the entire funnel, eliminating qualified talent before any human assessment can occur."))

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
    story.append(p("1.2 Economic and Talent Toll of Recruitment Bottlenecks", h1_style))
    story.append(p("Despite near-universal industrial adoption, legacy commercial screening tools introduce severe economic overhead and organizational friction. To quantify this toll, empirical investigations across enterprise engineering centers in South Asia and multinational offshore engineering markets demonstrate that human technical recruiters expend an average of 4.2 minutes per resume during manual triage, requiring over 140 recruiter-hours to screen a single candidate pool of 2,000 applicants. More critically, recruiter fatigue induces substantial decision variance: identical resumes evaluated at the beginning of an eight-hour screening shift receive significantly higher advancement rates than those evaluated toward the end (Sackett et al., 2022)."))
    story.append(p("When commercial keyword-based ATS engines are introduced to alleviate this manual burden, candidate quality often degrades rather than improves. An internal audit of 500 candidate profiles rejected by traditional keyword filters revealed that 28.4% possessed senior-level production competency in required software stacks but utilized alternative industry phrasing (such as 'distributed event streams' instead of 'Apache Kafka', or 'containerized orchestration' instead of 'Kubernetes'). Conversely, over 34% of applicants advancing to technical coding interviews failed foundational software design assessments, having bypassed keyword filters via superficial keyword packing. This operational breakdown imposes massive financial costs—averaging $4,129 per mis-hire and extending engineering vacancy cycles to 48 business days—demonstrating the urgent industrial necessity for a semantic, evidence-weighted screening engine."))

    # 1.3 SYSTEMIC FAILURE MODES
    if tracker is not None:
        story.append(PageTracker('sec1_3', tracker))
    story.append(p("1.3 Systemic Failure Modes in Current ATS Platforms", h1_style))
    story.append(p("Through exhaustive empirical analysis of enterprise hiring pipelines and forensic inspection of current natural language processing (NLP) screening models, this research identifies four critical structural failure modes in the state-of-the-art:"))
    story.append(b("<b>1. Syntactic Brittleness and Polysemous Token Collisions:</b> Conventional regular expressions and off-the-shelf NLP tokenizers fail catastrophically when encountering technical programming identifiers. Single-letter programming languages (such as 'C' or 'R'), short verbs ('Go', 'Rust'), framework names ('Spring'), and architectural paradigms ('REST') frequently collide with standard conversational English prose (e.g., 'go to market', 'in c-level meetings', 'spring semester', 'rest of the development team'). Without context-guarded token shielding, screening engines generate thousands of spurious false-positive skill hits."))
    story.append(b("<b>2. Temporal Experience Conflation and Duration Doubling:</b> Existing resume parsers extract chronological dates using crude subtraction without underlying temporal algebra. When candidates hold overlapping part-time positions, concurrent freelance consulting contracts, or simultaneous startup engagements, naive date arithmetic sums each interval independently, artificially doubling or tripling reported years of commercial experience. Furthermore, legacy parsers fail to distinguish casual academic coursework projects from verified corporate employment, allowing students to claim senior-level engineering tenure based on classroom assignments."))
    story.append(b("<b>3. Collapse of Multi-Dimensional Qualifications:</b> Commercial screening tools routinely collapse diverse candidate attributes (technical skills, commercial tenure, and educational attainment) into a single, opaque percentage match score. This monolithic collapse conflates unrelated non-technical degrees with accredited computer science qualifications, ignores whether a skill was deployed in enterprise production versus merely listed in an unverified bulleted inventory, and deprives human hiring managers of auditable mathematical explainability."))
    story.append(b("<b>4. The Synthetic Benchmark Leakage Problem in Academic Literature:</b> A substantial body of published academic literature in automated resume parsing and job role classification reports artificial, near-perfect classification performance (Macro F1 = 1.0). As demonstrated in our forensic audit, these published models were evaluated on synthetic datasets generated from rigid template engines. Classifiers simply memorized invariant template boilerplates and target-label header strings rather than candidate competencies, causing total model collapse when deployed on authentic real-world candidate resumes."))

    # 1.4 RESEARCH MOTIVATION & PROBLEM FORMULATION
    if tracker is not None:
        story.append(PageTracker('sec1_4', tracker))
    story.append(p("1.4 Research Motivation & Problem Formulation", h1_style))
    story.append(p("Mathematically, candidate evaluation in automated recruitment can be formalized as a multi-criteria decision-making (MCDM) problem over high-dimensional, unstructured, and partially verified candidate representations. Let a candidate resume document be denoted by D in the document space D_all. The extraction objective is to map D into a structured candidate representation vector C = (K_cand, T_cand, E_cand) and a target role classification y in {1, 2, ..., K}, while scoring candidate alignment against a multi-dimensional job requisition J = (K_req, T_req, E_req)."))
    story.append(p("Formally, we define the three primary evaluation spaces:"))
    story.append(b("• <b>Technical Competency Space K:</b> A discrete vocabulary of over 400 canonical software tools, programming languages, and frameworks K = {s_1, s_2, ..., s_M}, where each skill s_i possesses a contextual evidence score E(s_i) in [0.0, 1.0]."))
    story.append(b("• <b>Temporal Tenure Space T:</b> A set of verified, disjoint calendar intervals {[s_k, e_k]}_{k=1}^P in R_+ representing total commercial experience E_tot, IT-sector tenure E_it, and role-relevant tenure E_rel."))
    story.append(b("• <b>Academic Qualification Space E:</b> A two-dimensional tuple (L_deg, M_field) in [0, 100] x [0.2, 1.0] representing degree tier attainment and domain alignment."))
    story.append(p("In traditional systems, this mapping is approximated via an unweighted, opaque scalar function f(D, J) in [0, 1]. In contrast, authentic engineering recruitment requires a decoupled, transparent mapping where candidate technical skills, verified commercial employment tenure, and formal educational attainment are independently extracted, mathematically validated, and exposed as an uncollapsed vector S_C1 = [S_skill, S_exp, S_edu]. The motivation of this dissertation is to formulate, implement, and rigorously validate this end-to-end transformation."))

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
    story.append(p("1.5 Research Objectives & Specific C1 Scope", h1_style))
    story.append(p("The overarching mission of the <b>RecruitAI</b> research initiative (Project ID: R26-IT-148) is to engineer an end-to-end, fair, transparent, and multi-modal technical recruitment and predictive career development ecosystem uniting resume screening, autonomous technical interviews, listwise candidate ranking, and skill gap remediation. Within this four-component ecosystem, <b>Component 1 (C1)</b> serves as the foundational intake intelligence gateway."))
    story.append(p("The explicit scientific and software engineering objectives of Component 1 are defined as follows:"))
    story.append(b("<b>Objective 1: Format-Agnostic Layout-Aware Ingestion:</b> Implement a robust document processing pipeline supporting heterogeneous PDF and DOCX resumes that normalizes layout artifacts, segments sections via finite state automata, and redacts Personally Identifiable Information (PII) to prevent systemic demographic hiring bias."))
    story.append(b("<b>Objective 2: Boundary-Guarded Named Entity Recognition (NER):</b> Engineer a high-precision NER engine covering over 400 canonical IT competencies across 7 technical domains, incorporating context-guarded look-around assertion shields to eliminate polysemous false positives."))
    story.append(b("<b>Objective 3: Temporal Experience Algebra &amp; Disambiguation:</b> Formalize a calendar interval union algebra that resolves chronological date overlaps, separates academic projects from formal employment, and categorizes tenure into Total Experience (E_tot), IT-Sector Tenure (E_it), and Target-Role-Relevant Exposure (E_rel)."))
    story.append(b("<b>Objective 4: Two-Dimensional Academic Decoupling:</b> Establish an educational qualification ontology that strictly decouples academic degree attainment tier level (Ph.D., M.Sc., B.Sc., Diploma) from disciplinary field relevance (Core Computing, Adjacent Quantitative, Non-Technical)."))
    story.append(b("<b>Objective 5: Evidence-Weighted Technical Skill Scoring:</b> Formulate an evidence hierarchy that weights technical skills based on contextual usage, distinguishing isolated bullet point mentions (w = 0.40) from verified commercial employment duties (w = 1.00)."))
    story.append(b("<b>Objective 6: High-Fidelity 20-Class Role Classification:</b> Train, validate, and tune a balanced multinomial Logistic Regression model using sublinear TF-IDF vectorization across 20 canonical IT roles, achieving &gt;85% test accuracy on authentic held-out data with sub-5ms inference latency."))
    story.append(b("<b>Objective 7: Independent Tri-Pillar Output Contract:</b> Expose an uncollapsed feature vector (S_skill, S_exp, S_edu) on Port 8001 providing an interpretable, mathematically auditable contract for downstream ranking and interview orchestration."))

    # 1.6 RESEARCH QUESTIONS & HYPOTHESES
    if tracker is not None:
        story.append(PageTracker('sec1_6', tracker))
    story.append(p("1.6 Research Questions and Formal Hypotheses", h1_style))
    story.append(p("This dissertation investigates and resolves five foundational research questions:"))
    story.append(b("<b>RQ1:</b> Can context-guarded regular expression look-around assertion windows effectively eliminate subtoken collisions for polysemous programming language identifiers without sacrificing recall across diverse document layouts?<br/><i>Hypothesis H1:</i> Non-capturing regex assertions with structural boundaries reduce false-positive skill matches by &gt;95% on conversational English tokens compared to unshielded substring matching."))
    story.append(b("<b>RQ2:</b> To what extent does chronological interval union algebra prevent tenure inflation in technical resumes containing concurrent freelance and corporate employment records?<br/><i>Hypothesis H2:</i> Set-theoretic union date merging eliminates artificial duration inflation, bounding candidate commercial tenure strictly within calendar elapsed limits."))
    story.append(b("<b>RQ3:</b> Does decoupling academic degree tier level from disciplinary field relevance improve qualification scoring fidelity compared to monolithic degree tiering?<br/><i>Hypothesis H3:</i> Decoupled two-dimensional scoring prevents non-technical advanced degrees (e.g., Ph.D. in Literature) from scoring higher than computer science Bachelor degrees for software engineering roles."))
    story.append(b("<b>RQ4:</b> Can a balanced linear multinomial classifier with sublinear TF-IDF achieve classification accuracy comparable to fine-tuned deep transformers (DistilBERT) while delivering sub-5ms latency for enterprise ingestion?<br/><i>Hypothesis H4:</i> Balanced logistic regression achieves within 3% of DistilBERT accuracy while executing inference in &lt;3ms per resume, yielding a 50x throughput gain."))
    story.append(b("<b>RQ5:</b> Are the empirical feature importance contributions of technical skills, commercial tenure, and education consistent with the deployed 0.50 / 0.30 / 0.20 tri-pillar scoring weights?<br/><i>Hypothesis H5:</i> Permutation feature importance confirms skills as the primary discriminative signal (&gt;80%), while commercial tenure and education provide vital boundary constraints."))

    # 1.7 METHODOLOGY & ENGINEERING LIFECYCLE
    if tracker is not None:
        story.append(PageTracker('sec1_7', tracker))
    story.append(p("1.7 Research Methodology & Engineering Lifecycle", h1_style))
    story.append(p("This research adheres to the Design Science Research (DSR) methodology for information systems and applied machine learning (Hevner et al., 2004). The engineering lifecycle encompasses six iterative phases: (1) problem identification and empirical failure mode analysis across enterprise hiring pipelines; (2) mathematical formalization of extraction algebras and classification objectives; (3) design and implementation of modular microservice components in Python 3.12 and FastAPI; (4) experimental validation on a curated corpus of 4,000 authentic resumes; (5) rigorous forensic auditing of synthetic benchmark leakage; and (6) production deployment and automated testing with 195 Pytest assertions."))

    # 1.8 SCOPE, DELIMITATIONS & ETHICAL BOUNDARIES
    if tracker is not None:
        story.append(PageTracker('sec1_8', tracker))
    story.append(p("1.8 Scope, Boundaries, and Delimitations", h1_style))
    story.append(p("The scope of this research is strictly focused on text-based resume parsing, entity extraction, role classification, and qualification scoring for professional software engineering and IT roles across 20 canonical industry domains. The system accepts English-language resumes in PDF, DOCX, and TXT formats. Image-only raster scans requiring Optical Character Recognition (OCR), video resumes, and audio interviews are explicitly delimited from Component 1 and are handled by the multi-modal assessment systems in Component 2."))
    story.append(p("From an ethical and legal standpoint, Component 1 enforces automated PII redaction (names, phone numbers, email addresses, physical street addresses, and social links) prior to feature vector synthesis. This ensures that downstream role prediction and scoring are demographically blind, complying with the EU AI Act (Annex III) and NYC Local Law 144 governing automated employment decision tools."))

    # 1.9 PRIMARY TECHNICAL CONTRIBUTIONS
    if tracker is not None:
        story.append(PageTracker('sec1_9', tracker))
    story.append(p("1.9 Summary of Primary Technical Contributions", h1_style))
    story.append(p("The principal intellectual and engineering contributions presented in this dissertation are:"))
    story.append(b("1. <b>Layout-Aware Document Processing &amp; PII Redaction:</b> A production-grade ingestion engine resolving multi-column PDF layouts, character ligatures, and personally identifiable information."))
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
    story.append(p("The remainder of this dissertation is organized as follows: Chapter 2 provides an exhaustive literature review of automated screening engines, NLP information extraction, temporal logic, and forensic leakage analysis. Chapter 3 details the architectural methodology, mathematical formulations, and extraction criteria. Chapter 4 documents the software engineering implementation, microservice design, and testing protocols. Chapter 5 presents comprehensive empirical results, per-class evaluations, ablation studies, and latency benchmarks. Chapter 6 examines ethical governance, PII blinding, SHAP explainability, and regulatory compliance. Chapter 7 concludes the dissertation and outlines future research trajectories."))
    story.append(PageBreak())
