import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_group_ch8(story, styles, p, b, sp, make_box, caption_style, fig_dir):
    PRIMARY = colors.HexColor("#1A365D")
    SECONDARY = colors.HexColor("#2B6CB0")
    DARK_TEXT = colors.HexColor("#2D3748")

    ch_num_style = styles['ChapterNumber']
    ch_title_style = styles['ChapterTitle']
    h1_style = styles['Heading1_Custom']
    h2_style = styles['Heading2_Custom']
    body_style = styles['Body_Custom']
    body_bold = styles['Body_Bold']

    story.append(p("CHAPTER 8", ch_num_style))
    story.append(p("CONCLUSION AND FUTURE RESEARCH TRAJECTORIES", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    story.append(p("8.1 Research Synthesis and Problem Resolution", h1_style))
    story.append(p("The contemporary enterprise technical recruitment paradigm has long been hindered by fragmented tooling, superficial lexical screening filters, non-standardized multi-modal evaluations, and an unconstructive rejection dead-end. Over 98% of Fortune 500 corporations rely on legacy Applicant Tracking Systems that prioritize crude keyword matches over authentic engineering capability, inadvertently rejecting qualified non-traditional applicants while admitting opportunistic candidates who exploit keyword-stuffing vulnerabilities. Furthermore, candidate assessment has historically operated as an uninformative terminal funnel, discarding valuable diagnostic telemetry upon rejection."))
    story.append(p("In this comprehensive group research project (<b>Research Identifier: R26-IT-148</b>), the research team successfully conceptualized, mathematically formulated, implemented, and empirically validated <b>RecruitAI</b>: an end-to-end, event-driven multi-microservice artificial intelligence recruitment ecosystem that transforms candidate assessment into an intelligent, fair, and predictive career development pipeline. Operating across four decoupled FastAPI microservices running on dedicated TCP ports (8001-8004) under a unified API Gateway (Port 8000), RecruitAI demonstrates that high-throughput automation can coexist with rigorous mathematical explainability, algorithmic fairness, and constructive career remediation."))

    story.append(p("8.2 Summary of Group Research Achievements and Contributions", h1_style))
    story.append(p("The research contributions realized by the four individual investigators across the RecruitAI ecosystem are synthesized below:"))

    story.append(p("<b>1. Component 1: Automated Resume Screening & Role Classification (D. T. D. Perera, IT22089236):</b>", body_bold))
    story.append(b("• Formulated an auditable multi-stage ingestion engine with boundary-guarded Named Entity Recognition covering 400+ canonical technical entities across 7 IT sub-disciplines, eliminating false-positive token collisions for polysemous technologies (e.g., 'C', 'Go', 'R', 'REST')."))
    story.append(b("• Developed a formal Lebesgue interval union algebra that eliminates concurrent employment duration doubling and disambiguates total tenure from IT-sector and target-role experience."))
    story.append(b("• Introduced a two-dimensional credential qualification ontology decoupling degree level from disciplinary field relevance, paired with an evidence-weighted skill scoring hierarchy (mentions at 0.40 vs. demonstrated projects at 1.00)."))
    story.append(b("• Trained a balanced multinomial Logistic Regression classifier across 20 canonical IT roles, achieving <b>87.42% accuracy</b>, <b>92.47% macro-F1</b>, <b>85.95% ± 0.96%</b> 5-fold cross-validation accuracy, and <b>2.4 ms</b> inference latency. Conducted a forensic audit exposing pervasive synthetic benchmark leakage in existing published literature."))

    story.append(p("<b>2. Component 2: Autonomous Multi-Modal Technical Interview System (Dulnith K. D., IT22094872):</b>", body_bold))
    story.append(b("• Engineered an adaptive question retrieval engine leveraging Retrieval-Augmented Ingestion and Generation (RAIGS) over an 18,700-item verified technical question repository, dynamically tailoring interview rigor to candidate CV claims."))
    story.append(b("• Deployed OpenAI Whisper speech-to-text transcription achieving a Word Error Rate (WER) of <b>7.20%</b> across diverse candidate accents, feeding into Sentence-BERT bi-encoder scoring that correlates at <b>r = 0.884</b> (MAE = 0.038) against senior human software engineering rubrics."))
    story.append(b("• Implemented an AST-secured Python sandbox that achieved <b>100% intercept</b> across 30 adversarial exploit test cases, guaranteeing secure automated code verification in sub-second execution windows."))

    story.append(p("<b>3. Component 3: Candidate Scoring and Listwise Ranking Engine (K. G. Savinda N. Perera, IT22027610):</b>", body_bold))
    story.append(b("• Formulated a mathematically auditable Composite Suitability Score (CSS = 0.40 S_cv + 0.60 S_int) with soft prerequisite gating, eliminating arbitrary spreadsheet scoring heuristics."))
    story.append(b("• Benchmarked candidate ranking against a listwise LightGBM LambdaMART comparator, achieving superior ranking utility on enterprise recruitment lists (<b>NDCG@1 = 0.9784</b>, <b>NDCG@5 = 0.9473</b>, <b>MAP = 0.9798</b>)."))
    story.append(b("• Established statutory fairness compliance with Demographic Parity Difference Delta_DP = <b>0.008</b>, Equalized Odds Difference Delta_EO = <b>0.006</b>, and Disparate Impact Ratio DIR = <b>0.941</b>, comfortably exceeding the EEOC 80% adverse impact threshold."))

    story.append(p("<b>4. Component 4: Skill Gap Diagnostics and Career Pathfinding (Yenura S. Karunanayaka, IT22306272):</b>", body_bold))
    story.append(b("• Closed the industrial rejection dead-end by routing 100% of unshortlisted applicants into an intelligent career remediation engine, eliminating candidate information asymmetry."))
    story.append(b("• Engineered a two-stage fuzzy/semantic skill gap analyzer paired with a 67-feature GBDT ensemble (300 trees) predicting hireability readiness at <b>91.50% accuracy</b> and <b>0.9763 ROC-AUC</b>."))
    story.append(b("• Formulated a paced pedagogical learning scheduler capping skill acquisition at 2 skills/month across 47 curated technical courses, alongside a Directed Acyclic Graph (DAG) career lattice mapping reachable lateral and promotional engineering transitions."))

    story.append(p("8.3 Industrial Impact and Operational Deployment", h1_style))
    story.append(p("When evaluated across simulated enterprise engineering hiring requisitions, the integrated RecruitAI ecosystem delivers transformative operational efficiency improvements:"))
    story.append(b("• <b>Time-to-Hire Acceleration:</b> Reduces corporate end-to-end recruitment cycle time from an enterprise average of <b>42 days</b> to <b>8.5 days</b>, representing a <b>79.8% reduction</b> in requisition fulfillment latency."))
    story.append(b("• <b>Recruiter Cognitive Load Reduction:</b> Automates preliminary resume parsing, role classification, and initial technical screening, reducing human recruiter review hours by <b>84.5%</b> while improving shortlisted candidate interview conversion rates from 22% to 68%."))
    story.append(b("• <b>Candidate Satisfaction & Talent Retention:</b> Provides 100% of rejected candidates with transparent, diagnostic skill gap reports and curated developmental roadmaps, preserving candidate goodwill and creating a pre-qualified internal talent pipeline for future hiring requisitions."))

    story.append(p("8.4 Future Research Trajectories", h1_style))
    story.append(p("While the RecruitAI platform establishes a comprehensive, validated foundation, future research endeavors will explore several promising horizons:"))
    story.append(b("• <b>Federated Multi-Tenant Learning:</b> Investigating privacy-preserving federated learning architectures allowing cross-enterprise model training without centralizing sensitive applicant resume databases, further mitigating localized demographic bias."))
    story.append(b("• <b>Dynamic Reinforcement Learning Interview Agents:</b> Transitioning from static question bank retrieval to conversational multi-turn Reinforcement Learning from Human Feedback (RLHF) agents capable of dynamically following up on candidate conceptual errors during oral examinations."))
    story.append(b("• <b>Real-Time Code Execution Observability:</b> Enhancing the AST sandbox with dynamic memory profiling, micro-benchmarking, and algorithmic time-complexity estimation to evaluate algorithmic efficiency alongside functional test passage."))
    story.append(b("• <b>Multilingual Cross-Lingual Parsing:</b> Extending Named Entity Recognition taxonomies and Whisper acoustic models to support non-English resumes and regional linguistic vernaculars across South Asian and Asia-Pacific enterprise markets."))

    story.append(sp(6))
    story.append(PageBreak())
