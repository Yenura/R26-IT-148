import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from group_builder.styles import clean_xml, create_table_box, PRINTABLE_WIDTH
from group_builder.canvas_helper import PageTracker

def append_group_ch1(story, styles, fig_dir, tracker=None):
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
    cell_center = styles['TableCellCenter']

    def track(key):
        if tracker is not None:
            story.append(PageTracker(key, tracker))

    # =========================================================================
    # 1 INTRODUCTION AND PROJECT CONTEXT
    # =========================================================================
    track('ch1')
    story.append(Paragraph("1 INTRODUCTION AND PROJECT CONTEXT", h_ch))
    story.append(Spacer(1, 4))

    # 1.1 Background and context
    track('sec1_1')
    story.append(Paragraph("1.1 Background and context", h_sec))
    story.append(Paragraph("Global enterprise talent acquisition within the software engineering and information technology (IT) sectors has encountered an unprecedented operational bottleneck. Over the past decade, rapid industrial acceleration across distributed cloud architectures, containerized microservices, high-throughput streaming systems, and modern artificial intelligence platforms has created immense commercial demand for specialized technical competencies. Concurrently, the ubiquity of one-click digital recruitment boards, professional networking platforms, and automated generative resume builders has driven application volumes to historic highs. A single advertised engineering vacancy published by a multinational technology enterprise routinely attracts thousands of heterogeneous candidate resumes within hours of publication (Sackett et al., 2022).", p_body))
    
    story.append(Paragraph("Historically, talent acquisition relied upon human recruiters conducting manual document appraisals, reading candidate curricula vitae line-by-line to evaluate professional credentials and career progression. During the early 2000s, the introduction of first-generation Applicant Tracking Systems (ATS) introduced Boolean keyword matching, indexing resumes against rigid lexical queries. While this transition relieved recruiters of printing physical paper submissions, it introduced acute operational fragilities: keyword stuffing became pervasive, candidates with unconventional phrasing were discarded, and candidates possessing genuine competence were routinely overlooked. In contemporary recruitment environments, over 98% of Fortune 500 corporations and more than 75% of high-growth technology enterprises mandate algorithmic document triage prior to any human review (Zhang et al., 2023).", p_body))
    
    story.append(Paragraph("The introduction of commercial Large Language Models (LLMs) and deep neural transformers has further compounded these intake challenges. Job seekers frequently utilize generative tools to synthesize embellished, keyword-optimized resumes that effortlessly bypass rudimentary ATS filters. Consequently, human recruitment panels report acute cognitive fatigue. Eye-tracking studies in recruitment research demonstrate that human screeners allocate an average of only 6.0 to 7.4 seconds skimming an individual curriculum vitae before assigning an initial acceptance or rejection decision. Such compressed evaluation windows invariably introduce severe heuristic biases, gender and ethnic discrimination, and uncalibrated evaluation variances.", p_body))
    
    story.append(Paragraph("Once candidates navigate initial screening, enterprise recruitment funnels encounter a secondary systemic bottleneck: technical capability verification. Coordinating live, multi-round technical interviews between senior software engineers and candidate cohorts consumes substantial engineering hours. Senior engineers frequently spend between 5 and 15 hours per week conducting introductory technical assessments, diverting high-value engineering capacity away from core product development. Moreover, human interviewers exhibit documented scoring discrepancies driven by fatigue, subjective personal rapport, and inconsistent rubric application (Raghavan et al., 2020).", p_body))
    
    story.append(Paragraph("Finally, when corporate hiring decisions are finalized, disqualified applicants encounter the pervasive 'black hole' of automated recruitment: silent rejection or generic, uninformative automated rejection emails. Applicants receive zero actionable intelligence regarding their specific technical deficiencies, leaving them incapable of targeted career remediation. Table 1.1 delineates typical applicant attrition and operational failure points observed across an intake cohort of 1,000 applications in modern engineering hiring.", p_body))
    story.append(Spacer(1, 4))

    track('tab1_1')
    story.append(Paragraph("Table 1.1: Global technical recruitment funnel attrition and bottleneck metrics.", caption_tab))
    funnel_data = [
        [Paragraph("<b>Recruitment Stage</b>", cell_bold), Paragraph("<b>Candidate Cohort</b>", cell_bold), Paragraph("<b>Attrition (%)</b>", cell_bold), Paragraph("<b>Operational Bottlenecks &amp; Failure Modes</b>", cell_bold)],
        [Paragraph("1. Resume Ingestion &amp; Parsing", cell), Paragraph("1,000 applicants", cell), Paragraph("Baseline (0%)", cell), Paragraph("Multi-column layout scrambling; character encoding corruption; font ligature errors", cell)],
        [Paragraph("2. Algorithmic ATS Triage", cell), Paragraph("250 applicants", cell), Paragraph("75.0% drop", cell), Paragraph("Keyword mismatch disqualifications; keyword stuffing exploits; unverified tenure", cell)],
        [Paragraph("3. Recruiter Review", cell), Paragraph("60 applicants", cell), Paragraph("76.0% drop", cell), Paragraph("Severe cognitive fatigue (6-7s skim); inconsistent manual scoring variances", cell)],
        [Paragraph("4. Technical Assessment", cell), Paragraph("15 applicants", cell), Paragraph("75.0% drop", cell), Paragraph("Keyword-stuffed candidates fail coding basics; high engineering interviewer time drain", cell)],
        [Paragraph("5. Architecture Interview &amp; Offer", cell), Paragraph("3 offers (1 hire)", cell), Paragraph("80.0% drop", cell), Paragraph("High cost of mis-hires ($4,129 average replacement overhead); 0% feedback to rejected", cell)],
    ]
    funnel_tab = create_table_box(funnel_data, [105, 85, 75, 146], styles, is_header=True)
    story.append(funnel_tab)
    story.append(Spacer(1, 8))

    # 1.2 Stakeholders and user needs
    track('sec1_2')
    story.append(Paragraph("1.2 Stakeholders and user needs", h_sec))
    story.append(Paragraph("Developing an integrated recruitment intelligence ecosystem requires a comprehensive analysis of all key stakeholders participating across the talent acquisition lifecycle. Through empirical stakeholder engagement sessions, structured interviews with senior technical recruiters, and surveys conducted across software engineering candidates, the research team identified four primary stakeholder cohorts and their critical operational needs:", p_body))
    
    story.append(Paragraph("<b>1. Corporate Hiring Teams and Enterprise Talent Acquisition Leaders:</b> Corporate recruiters manage dozens of simultaneous job requisitions, processing thousands of heterogeneous applications weekly. Their core operational needs include: (a) automated, sub-second resume parsing capable of handling multi-column layouts without text corruption; (b) elimination of false-positive candidate recommendations driven by keyword stuffing or polysemous acronym collisions; (c) mathematically transparent, auditable qualification scoring that decouples skills, tenure, and academic credentials; and (d) strict adherence to international employment fairness regulations and privacy standards.", p_bullet))
    
    story.append(Paragraph("<b>2. Lead Software Engineers and Technical Interview Panels:</b> Senior software engineers and engineering directors conduct technical evaluations to verify hands-on coding proficiency and system design acumen. Their primary needs comprise: (a) automated pre-qualification of technical competencies prior to live human interview rounds; (b) standardized, objective multi-modal interview scoring that eliminates subjective interviewer bias; and (c) secure, sandboxed execution environments capable of executing candidate code submissions safely without exposing internal infrastructure to arbitrary code injection attacks.", p_bullet))
    
    story.append(Paragraph("<b>3. Candidate Job Seekers and Software Engineering Practitioners:</b> Technical professionals applying for engineering roles require a recruitment process founded on equity, merit, and transparency. Candidate user needs include: (a) protection against demographic, racial, gender, and institutional bias through automated Personally Identifiable Information (PII) masking; (b) objective evaluation of demonstrated competencies rather than superficial keyword matching; and (c) actionable, diagnostic feedback detailing identified skill gaps and clear, milestone-driven learning roadmaps when an application is unsuccessful.", p_bullet))
    
    story.append(Paragraph("<b>4. Higher Educational Institutions and Technical Training Bootcamps:</b> Universities, polytechnics, and vocational coding academies need aggregated empirical data regarding market demand trends. Their operational needs center on: (a) identifying persistent curricular skill gaps that hinder graduate employability; and (b) aligning academic learning outcomes with contemporary enterprise technology expectations.", p_bullet))
    story.append(Spacer(1, 6))

    # 1.3 Alignment with the Sustainable Development Goals
    track('sec1_3')
    story.append(Paragraph("1.3 Alignment with the Sustainable Development Goals", h_sec))
    story.append(Paragraph("The RecruitAI research project is explicitly designed to advance the 2030 Agenda for Sustainable Development adopted by the United Nations General Assembly. Rather than treating social impact as an external consideration, algorithmic fairness, economic inclusion, and transparent governance are engineered into the architectural foundation of the platform. Specifically, the ecosystem contributes directly to three United Nations Sustainable Development Goals (SDGs):", p_body))
    
    story.append(Paragraph("• <b>SDG 8: Decent Work and Economic Growth (Target 8.5 - Full and Productive Employment):</b> Target 8.5 seeks to achieve full and productive employment and decent work for all women and men, including young people and persons with disabilities, alongside equal pay for work of equal value. RecruitAI directly advances this goal by optimizing the job-matching efficiency of the knowledge economy. By replacing opaque keyword filters with verified competency scoring and listwise ranking, qualified job seekers are matched to appropriate employment opportunities without arbitrary rejection. Furthermore, Component 4's diagnostic pathfinding provides unshortlisted candidates with structured upskilling pathways, fostering continuous professional development and long-term economic mobility.", p_bullet))
    
    story.append(Paragraph("• <b>SDG 9: Industry, Innovation, and Infrastructure (Target 9.5 - Enhance Scientific Research and Innovation):</b> Target 9.5 calls for upgrading technological capabilities across industrial sectors, fostering innovation, and increasing research and development capacity. RecruitAI contributes to this objective by delivering an open, modular, and containerized artificial intelligence architecture that executes high-throughput inference on standard CPU infrastructure without requiring expensive high-end GPU hardware. This lightweight computational design democratizes enterprise-grade recruitment AI, allowing educational institutions, non-profit organizations, and small-to-medium enterprises (SMEs) in developing nations to deploy state-of-the-art talent intelligence tools.", p_bullet))
    
    story.append(Paragraph("• <b>SDG 10: Reduced Inequalities (Target 10.3 - Ensure Equal Opportunity and Reduce Inequalities of Outcome):</b> Target 10.3 mandates eliminating discriminatory laws, policies, and practices while promoting appropriate legislation and action. Contemporary hiring algorithms frequently perpetuate historic human biases against minority demographics, non-elite universities, and non-traditional career paths. RecruitAI enforces automated, multi-entity PII redaction (names, phone numbers, email addresses, residential locations, and gender pronouns) before semantic scoring commences. By blinding the decision pipeline to demographic attributes and relying on transparent Multi-Attribute Utility Theory (MAUT), the system ensures equal opportunity across diverse applicant cohorts.", p_bullet))
    story.append(Spacer(1, 6))

    # 1.4 Purpose and scope of the common report
    track('sec1_4')
    story.append(Paragraph("1.4 Purpose and scope of the common report", h_sec))
    story.append(Paragraph("The purpose of this Common Integrated Solution Report is to present the overarching architectural design, component interactions, integration data contracts, shared non-functional requirements, unified implementation, and end-to-end empirical validation of the RecruitAI ecosystem (Project Identifier: R26-IT-148). While individual research theses authored by team members provide exhaustive algorithmic proofs and isolated experiments for their respective components, this report documents the synergistic solution as a unified, cohesive software engineering artifact.", p_body))
    
    story.append(Paragraph("The operational scope of the integrated common report encompasses four interoperable microservice subsystems engineered to deliver a closed-loop talent acquisition platform:", p_body))
    story.append(Paragraph("1. <b>Component 1 (Automated Semantic Resume Screening and IT Job Role Classification):</b> Authored by D. T. D. Perera (IT22089236), focusing on layout-aware parsing, context-guarded regex shields, chronological interval union algebra, two-dimensional academic credential decoupling, and balanced 20-class multinomial role prediction.", p_bullet))
    story.append(Paragraph("2. <b>Component 2 (Autonomous Technical Interview Evaluation):</b> Authored by Yenura S. Karunanayaka (IT22306272), focusing on real-time speech transcription via OpenAI Whisper, SBERT semantic answer rubric grading, and secure abstract syntax tree (AST) code sandboxing.", p_bullet))
    story.append(Paragraph("3. <b>Component 3 (Candidate Suitability Scoring and Listwise Ranking):</b> Authored by K. G. Savinda N. Perera (IT22027610), focusing on Multi-Attribute Utility Theory (MAUT) score normalization, hard and soft credential gating, and LambdaMART listwise learning-to-rank.", p_bullet))
    story.append(Paragraph("4. <b>Component 4 (Predictive Skill Gap Diagnostics and Career Pathfinding):</b> Authored by K. G. Savinda N. Perera (IT22027610), focusing on 67-feature gradient boosted hireability prediction, directed acyclic graph (DAG) competency lattices, and Dijkstra shortest-path learning roadmap generation.", p_bullet))
    
    story.append(Paragraph("The boundaries of this common report cover technical recruitment within 20 canonical software engineering and IT job classifications, processing English-language documentation and audio transcripts, communicating via asynchronous RESTful HTTP endpoints, and deployed within containerized environments. Excluded from this scope are executive-level non-technical recruitment, non-English resumes, physical biometrics, and active video emotion tracking.", p_body))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Document Publication and Dissemination Portal:</b> In compliance with university and research dissemination standards, all collaborative research reports, presentation slide decks, architectural schemas, and project documentation deliverables are publicly published at the official publication portal: <u>https://r26-it-148-website.yenura02.workers.dev/</u>.", p_body))
    story.append(Spacer(1, 6))

    # 1.5 Research questions and hypotheses of the integrated platform
    track('sec1_5')
    story.append(Paragraph("1.5 Research questions and hypotheses of the integrated platform", h_sec))
    story.append(Paragraph("The research initiative investigates five overarching technical research questions (RQs) that evaluate whether an integrated, decoupled multi-microservice architecture can overcome the structural failure modes of modern recruitment without incurring unmanageable computational latency:", p_body))

    story.append(Paragraph("<b>RQ1 (Cross-Service Representation Fidelity):</b> Can unstructured, multi-column curriculum vitae documents be parsed and transformed into structured mathematical vectors with zero token collision and exact chronological tenure deduplication, without losing critical semantic context needed downstream? <i>Hypothesis H1: Layout-aware bounding-box extraction combined with regular expression look-around assertion shields reduces false-positive skill detections by more than 90% compared to unguarded dictionary parsing, while interval union algebra bounds computed tenure by elapsed calendar time.</i>", p_bullet))
    
    story.append(Paragraph("<b>RQ2 (Multi-Modal Assessment Concordance):</b> To what extent does autonomous speech-to-text transcription paired with Sentence-BERT semantic cosine grading and sandboxed AST code execution correlate with senior human technical interviewers? <i>Hypothesis H2: Dense bi-encoder semantic rubric comparison achieves a Pearson correlation r &ge; 0.85 with human expert panels while AST sandboxing enforces 100% containment of unauthorized system calls.</i>", p_bullet))
    
    story.append(Paragraph("<b>RQ3 (Listwise Ranking Superiority and Fairness):</b> Does listwise learning-to-rank (LambdaMART) combined with Multi-Attribute Utility Theory (MAUT) produce fairer, higher-fidelity candidate shortlists than commercial heuristic ATS filters, while satisfying legal demographic parity thresholds? <i>Hypothesis H3: Multi-attribute normalization and listwise gradient optimization achieve NDCG@5 &ge; 0.88 while maintaining an Adverse Impact Ratio &ge; 0.85 across gender and educational background cohorts.</i>", p_bullet))
    
    story.append(Paragraph("<b>RQ4 (Remedial Closed-Loop Utility):</b> Can unshortlisted candidate skill deficiencies be mapped onto directed acyclic competency graphs such that Dijkstra shortest-path traversal synthesizes pedagogically sound roadmaps that measurably elevate candidate hireability? <i>Hypothesis H4: Milestone-based learning roadmaps generated via DAG lattices increase simulated candidate hireability by at least 30% while guaranteeing zero cyclic dependency deadlocks.</i>", p_bullet))
    
    story.append(Paragraph("<b>RQ5 (Decoupled Architectural Operational Viability):</b> Can an asynchronous four-microservice cluster execute intake screening, technical interview evaluation, candidate ranking, and roadmap synthesis under standard CPU compute constraints while satisfying strict sub-15-second response limits? <i>Hypothesis H5: Decoupled FastAPI services communicating over asynchronous REST endpoints execute complete end-to-end candidate evaluations within 2.5 seconds on dual-core CPU compute without mandatory GPU acceleration for screening and ranking.</i>", p_bullet))
    story.append(Spacer(1, 6))

    # 1.6 Summary of principal technological innovations
    track('sec1_6')
    story.append(Paragraph("1.6 Summary of principal technological innovations", h_sec))
    story.append(Paragraph("The RecruitAI platform introduces five foundational software engineering and applied machine learning innovations that differentiate the ecosystem from existing academic prototypes and commercial enterprise suites. Table 1.2 synthesizes these innovations across the four microservices.", p_body))
    story.append(Spacer(1, 4))

    track('tab1_2')
    story.append(Paragraph("Table 1.2: Comparative matrix of principal technological innovations across the RecruitAI ecosystem.", caption_tab))
    innov_data = [
        [Paragraph("<b>Component &amp; Lead</b>", cell_bold), Paragraph("<b>Architectural Innovation</b>", cell_bold), Paragraph("<b>Legacy Industry Standard</b>", cell_bold), Paragraph("<b>Empirical Breakthrough Achieved</b>", cell_bold)],
        [Paragraph("Component 1<br/>D. T. D. Perera", cell), Paragraph("Boundary-guarded NER &amp; Lebesgue interval union algebra", cell), Paragraph("Naive regex &amp; linear date summation", cell), Paragraph("0% token collisions on C/Go/Rust; 100% elimination of tenure overlap inflation", cell)],
        [Paragraph("Component 1<br/>D. T. D. Perera", cell), Paragraph("Decoupled 2D credential matrix (Tier x Field)", cell), Paragraph("Monolithic degree tier hierarchies", cell), Paragraph("Prevents non-technical doctorates from outscoring relevant technical BSc degrees", cell)],
        [Paragraph("Component 2<br/>Y. S. Karunanayaka", cell), Paragraph("Streaming Whisper STT &amp; SBERT rubric cosine grading", cell), Paragraph("Static multiple choice questions", cell), Paragraph("7.8% Word Error Rate; r = 0.884 correlation with senior technical human panels", cell)],
        [Paragraph("Component 2<br/>Y. S. Karunanayaka", cell), Paragraph("AST-secured Python execution containment sandbox", cell), Paragraph("Unsecured local eval() or mock tests", cell), Paragraph("Zero remote code execution escapes; 100% interception of malicious system calls", cell)],
        [Paragraph("Component 3<br/>K. G. S. N. Perera", cell), Paragraph("MAUT utility scoring &amp; LambdaMART listwise ranking", cell), Paragraph("Unweighted spreadsheet heuristics", cell), Paragraph("NDCG@5 = 0.892; adverse impact ratio AIR = 0.94 satisfying EEOC 80% rule", cell)],
        [Paragraph("Component 4<br/>K. G. S. N. Perera", cell), Paragraph("Dijkstra shortest-path DAG career remediation lattice", cell), Paragraph("Terminal silent rejection emails", cell), Paragraph("Zero cyclic graph deadlocks; +38.4% simulated hireability boost for applicants", cell)],
    ]
    innov_tab = create_table_box(innov_data, [95, 105, 95, 116], styles, is_header=True)
    story.append(innov_tab)
    story.append(Spacer(1, 8))

    # 1.7 Organisation and structure of the common report
    track('sec1_7')
    story.append(Paragraph("1.7 Organisation and structure of the common report", h_sec))
    story.append(Paragraph("The remainder of this Common Integrated Solution Report is structured into seven comprehensive technical chapters designed to document the full research and engineering lifecycle:", p_body))
    
    story.append(Paragraph("• <b>Chapter 2 (Overall Problem Definition and Four Subproblems):</b> Establishes the industrial context, details the root causes of recruitment failure, formalizes the four research subproblems, and provides a comparative benchmark against existing commercial and academic systems.", p_bullet))
    story.append(Paragraph("• <b>Chapter 3 (Overall Solution Structure):</b> Details the macro-microservice architecture, provides comprehensive technical summaries of Components 1 through 4, presents the formal mathematical formulations across all models, and evaluates architectural trade-offs.", p_bullet))
    story.append(Paragraph("• <b>Chapter 4 (Component Integration and Cohesive Operation):</b> Documents the inter-service integration strategy, OpenAPI 3.0 REST data contracts, Pydantic schemas, shared MongoDB Atlas models, distributed tracing, and fault-tolerant exception handling.", p_bullet))
    story.append(Paragraph("• <b>Chapter 5 (Integrated Implementation and Project Execution):</b> Reviews the technology stack, agile Scrum engineering cadence, multi-container Docker deployment configuration, risk management matrix, and CI/CD verification pipelines.", p_bullet))
    story.append(Paragraph("• <b>Chapter 6 (Integrated Testing, Evaluation, and Validation):</b> Presents empirical results across 4,000 authentic resumes and 50 live interviews, details ablation findings, examines synthetic benchmark leakage, and documents extensive stakeholder validation.", p_bullet))
    story.append(Paragraph("• <b>Chapter 7 (Commercialisation, Sustainability, and Responsible Innovation):</b> Formulates the SaaS business model, analyzes financial feasibility, examines international regulatory compliance (EU AI Act, NYC LL144, GDPR), and details alignment with UN SDGs.", p_bullet))
    story.append(Paragraph("• <b>Chapter 8 (Conclusion and Future Directions):</b> Synthesizes the core research achievements, discusses critical engineering lessons learned, identifies technical limitations, and charts future research trajectories.", p_bullet))
    story.append(Paragraph("• <b>References and Appendices:</b> Provides full academic citations, formal OpenAPI endpoint specifications, team contribution attestations, and cloud infrastructure deployment scripts.", p_bullet))
    story.append(Spacer(1, 10))

    story.append(PageBreak())
    return story
