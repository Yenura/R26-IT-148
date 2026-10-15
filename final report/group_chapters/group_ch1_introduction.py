import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_group_ch1(story, styles, p, b, sp, make_box, caption_style, fig_dir):
    PRIMARY = colors.HexColor("#1A365D")
    SECONDARY = colors.HexColor("#2B6CB0")
    DARK_TEXT = colors.HexColor("#2D3748")

    ch_num_style = styles['ChapterNumber']
    ch_title_style = styles['ChapterTitle']
    h1_style = styles['Heading1_Custom']
    h2_style = styles['Heading2_Custom']
    body_style = styles['Body_Custom']
    body_bold = styles['Body_Bold']

    story.append(p("CHAPTER 1", ch_num_style))
    story.append(p("INTRODUCTION AND ECOSYSTEM CONTEXT", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    story.append(p("1.1 Context and Global Technical Recruitment Landscape", h1_style))
    story.append(p("Modern enterprise technical recruitment operates under an acute paradox: while global industrial demand for highly specialized software engineering and cloud architecture talent continues to surge, corporate talent acquisition funnels are increasingly paralyzed by exponential application volume and severe information asymmetry. The widespread digitization of job application portals, automated one-click submission features, and generative resume assistants have led to candidate submission surges where a single multinational engineering requisition routinely attracts thousands of heterogeneous resumes within days of publication (Sackett et al., 2022)."))
    story.append(p("To prevent human recruitment panels from suffering cognitive exhaustion during initial document triage, organizations universally deploy automated Applicant Tracking Systems (ATS) as frontline filters. Benchmark studies indicate that over 98% of Fortune 500 enterprises and 75% of high-growth technology corporations utilize automated parsers to screen candidate intake (Zhang et al., 2023). However, legacy ATS platforms suffer from foundational structural flaws: they rely predominantly on crude lexical keyword counts and substring matching. This induces severe dual failure modes: qualified engineers utilizing non-standard phrasing or emphasizing architectural impact are prematurely rejected, while opportunistic candidates who superficially game filters through keyword stuffing bypass preliminary screening despite lacking authentic technical competency."))

    story.append(p("1.2 The Rejection Dead-End Failure Mode", h1_style))
    story.append(p("Beyond document screening inaccuracies, traditional hiring pipelines suffer from operational fragmentation and a pervasive industrial failure mode: <i>the rejection dead-end</i>. In conventional recruitment workflows, the hiring process functions as a disconnected, terminating funnel. Candidates transition between disparate tools - from third-party resume parsers to standalone multiple-choice coding platforms and subjective interview panels. Disparate scores are combined through ad-hoc, unvalidated spreadsheets without mathematical justification or fairness auditing (Singh et al., 2018)."))
    story.append(p("Most critically, when a candidate fails to meet the final shortlisting threshold, the interaction abruptly terminates. Unsuccessful applicants receive cold, automated rejection emails ('We have decided to move forward with other candidates') devoid of diagnostic feedback. This uninformative dead-end wastes valuable candidate assessment telemetry, damages employer branding, and deprives motivated engineers of actionable insights needed to bridge skill deficits. In an era where technological stacks evolve continuously, converting candidate assessment from a terminal filter into a constructive, closed-loop talent developmental pipeline represents a transformative industrial necessity."))

    # FIGURE 1.1: MACRO ARCHITECTURE
    fig_macro = os.path.join(fig_dir, "fig6_macro_architecture.png")
    if os.path.exists(fig_macro):
        story.append(sp(4))
        story.append(Image(fig_macro, width=460, height=230))
        story.append(p("Figure 1.1: Multi-Microservice Architecture of the Integrated RecruitAI Ecosystem (Project: R26-IT-148).", caption_style))
        story.append(sp(4))

    story.append(p("1.3 The RecruitAI Ecosystem Vision", h1_style))
    story.append(p("To resolve these systemic challenges, this research presents <b>RecruitAI</b> (Research Project Identifier: <b>R26-IT-148</b>), an enterprise-grade, event-driven multi-microservice artificial intelligence recruitment and predictive career progression ecosystem. Built upon decoupled FastAPI microservices and an interactive React web portal, RecruitAI unifies four interoperable analytical components:"))
    story.append(b("• <b>Component 1 (Port 8001 - Lead: D. T. D. Perera, IT22089236):</b> Automated Semantic Resume Screening and IT Job Role Classification. Acts as the intake intelligence gateway, executing layout-aware document ingestion, boundary-guarded Named Entity Recognition (NER), chronological interval union algebra, two-dimensional academic decoupling, and balanced 20-role multinomial logistic classification."))
    story.append(b("• <b>Component 2 (Port 8002 - Lead: Dulnith K. D., IT22094872):</b> Autonomous Multi-Modal Technical Interview System. Dynamically extracts contextual interview questions via Retrieval-Augmented Generation (RAIGS), transcribes verbal candidate responses via Whisper STT, scores open-ended semantic comprehension via Sentence-BERT, and validates coding execution in an AST-secured Python sandbox."))
    story.append(b("• <b>Component 3 (Port 8003 - Lead: K. G. Savinda N. Perera, IT22027610):</b> Candidate Suitability Scoring and Listwise Ranking Engine. Synthesizes independent CV and interview vectors through transparent Multi-Attribute Utility Theory (MAUT), applies soft prerequisite gating, evaluates rankings against a listwise LightGBM LambdaMART comparator, and enforces demographic fairness audits."))
    story.append(b("• <b>Component 4 (Port 8004 - Lead: Yenura S. Karunanayaka, IT22306272):</b> Skill Gap Diagnostics and Career Pathfinding System. Captures unshortlisted candidate profiles, executes two-stage fuzzy/semantic gap analytics against 20 canonical IT roles, predicts hireability probabilities via a 67-feature GBDT ensemble, and synthesizes personalized learning roadmaps alongside a Directed Acyclic Graph (DAG) career mobility lattice."))

    # FIGURE 1.2: CANDIDATE LIFECYCLE FLOW
    fig_flow = os.path.join(fig_dir, "fig9_integrated_lifecycle_flow.png")
    if os.path.exists(fig_flow):
        story.append(sp(4))
        story.append(Image(fig_flow, width=460, height=216))
        story.append(p("Figure 1.2: End-to-End RecruitAI Candidate Lifecycle, Analytical State Flow, and Remedial Career Routing.", caption_style))
        story.append(sp(4))

    story.append(p("1.4 Research Objectives", h1_style))
    story.append(p("The primary objective of the RecruitAI initiative is to conceptualize, formalize, implement, and empirically validate an auditable, bias-mitigated, and closed-loop recruitment ecosystem that replaces keyword matching with dense semantic understanding and transforms candidate rejection into developmental mobility. The specific technical objectives are allocated as follows:"))
    story.append(b("<b>Objective 1 (Component 1 Lead):</b> Engineer a format-agnostic resume ingestion engine with boundary-guarded NER covering 400+ technical skills, calendar interval algebra resolving concurrent tenure overlaps, two-dimensional educational decoupling, and balanced 20-class role classification achieving &gt;85% test accuracy."))
    story.append(b("<b>Objective 2 (Component 2 Lead):</b> Construct an autonomous multi-modal interview platform that adaptively retrieves role-aligned questions, performs speech transcription (&lt;10% WER), executes dense semantic grading correlating strongly with human panels (r &gt; 0.85), and secures code execution with zero escape vulnerabilities."))
    story.append(b("<b>Objective 3 (Component 3 Lead):</b> Formulate an auditable Candidate Suitability Scoring (CSS) engine with soft gating that balances document screening and live assessment, verified against a listwise LambdaMART comparator (NDCG@5 &gt; 0.94), while mathematically guaranteeing demographic parity (Delta_DP &lt; 0.02)."))
    story.append(b("<b>Objective 4 (Component 4 Lead):</b> Implement an intelligent career diagnostics engine combining high-dimensional skill gap extraction with a 67-feature GBDT hireability model (ROC-AUC &gt; 0.95), mapping missing competencies into realistic monthly curricula (paced at 2 skills/month) and navigating a multi-tier DAG career lattice."))

    story.append(p("1.5 Research Questions & Formal Hypotheses", h1_style))
    story.append(p("The integrated research group investigates five fundamental research questions:"))
    story.append(b("<b>RQ1:</b> Can context-guarded regex assertions and set-theoretic date union algebra eliminate polysemous skill collisions and tenure inflation in enterprise resume ingestion without sacrificing throughput?<br/><i>Hypothesis H1:</i> Non-capturing regex assertions reduce false-positive skill matches by &gt;95%, while interval union math bounds reported tenure strictly within calendar elapsed limits."))
    story.append(b("<b>RQ2:</b> To what extent does Sentence-BERT rubric similarity align with human engineering panels during open-ended verbal technical assessments?<br/><i>Hypothesis H2:</i> Dense bi-encoder embeddings achieve Pearson correlation r &gt; 0.85 against expert grading rubrics, significantly outperforming lexical TF-IDF baselines."))
    story.append(b("<b>RQ3:</b> Can a transparent linear multi-attribute ranking engine achieve ranking fidelity competitive with non-linear Learning-to-Rank models while providing closed-form SHAP explainability?<br/><i>Hypothesis H3:</i> Linear CSS achieves within 1% NDCG@5 of LightGBM LambdaMART while guaranteeing exact, instantaneous attribution."))
    story.append(b("<b>RQ4:</b> Can tabular gradient boosting accurately model candidate hireability under enterprise policy benchmarks to synthesize realistic, paced career roadmaps?<br/><i>Hypothesis H4:</i> A 67-feature GBDT ensemble achieves ROC-AUC &gt; 0.97, effectively prioritizing missing competencies for developmental sequencing."))
    story.append(b("<b>RQ5:</b> Does unifying screening, interviewing, ranking, and remedial upskilling into a closed loop mitigate candidate attrition and eliminate the rejection dead-end?<br/><i>Hypothesis H5:</i> Automated routing of unshortlisted applicants achieves 100% remedial roadmap generation, converting discarded talent into future pipeline candidates."))

    story.append(p("1.6 Team Member Allocation and Responsibilities", h1_style))
    story.append(p("Table 1.1 documents the individual student assignments, institutional registration identifiers, assigned research components, and primary algorithmic contributions across Research Group R26-IT-148:"))

    team_data = [
        [p("<b>Student Name</b>", body_style), p("<b>Student ID</b>", body_style), p("<b>Component Assignment</b>", body_style), p("<b>Core Models &amp; Algorithmic Scope</b>", body_style)],
        [p("<b>D. T. D. Perera</b><br/>(Group Leader)", body_style), p("IT22089236", body_style), p("Component 1: Automated Resume Screening &amp; Role Classification", body_style), p("Boundary-Guarded NER, Temporal Interval Union Algebra, Decoupled 2D Education Model, Balanced Multinomial Logistic Regression (20 Roles)", body_style)],
        [p("<b>Dulnith K. D.</b>", body_style), p("IT22094872", body_style), p("Component 2: Autonomous Multi-Modal Technical Interview System", body_style), p("RAIGS Adaptive Q-Bank (18.7k Qs), Whisper STT Transcription, Sentence-BERT (all-mpnet-base-v2) Rubric Grading, AST-Secured Python Sandbox", body_style)],
        [p("<b>K. G. Savinda N. Perera</b>", body_style), p("IT22027610", body_style), p("Component 3: Candidate Suitability Scoring &amp; Listwise Ranking", body_style), p("Multi-Attribute CSS Formulation, Soft Near-Miss Gating, LightGBM LambdaMART LTR Comparator, Demographic Parity &amp; Equal Opportunity Audits", body_style)],
        [p("<b>Yenura S. Karunanayaka</b>", body_style), p("IT22306272", body_style), p("Component 4: Skill Gap Diagnostics &amp; Career Pathfinding", body_style), p("Fuzzy/Semantic Gap Analysis, 67-Feature GBDT Hireability Ensemble (300 Trees), Paced Roadmap Engine (2 skills/mo), DAG Career Lattice", body_style)]
    ]
    team_table = Table(team_data, colWidths=[105, 75, 145, 162])
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(team_table)
    story.append(p("Table 1.1: Research Group R26-IT-148 Member Allocations, Assigned Components, and Technical Scopes.", caption_style))
    story.append(sp(6))

    story.append(p("1.7 Summary of Primary Technical Contributions", h1_style))
    story.append(p("The integrated intellectual and engineering contributions of this group dissertation encompass:"))
    story.append(b("1. <b>Unified Microservice Architecture:</b> A containerized, event-driven ecosystem communicating across designated TCP ports (8000-8004) with sub-15ms gateway latency."))
    story.append(b("2. <b>Polysemy-Protected Entity Parsing:</b> An NER taxonomy of 400+ skills with context look-around assertion shielding eliminating single-letter token collisions (C, R, Go, REST)."))
    story.append(b("3. <b>Lebesgue Interval Union Calculus:</b> Set-theoretic interval math resolving concurrent freelance/corporate tenures and separating commercial experience from projects."))
    story.append(b("4. <b>Autonomous Multi-Modal Examination:</b> An adaptive interview engine combining Whisper speech recognition, SBERT semantic rubric grading, and sandboxed coding."))
    story.append(b("5. <b>Fairness-Audited Listwise Ranking:</b> A transparent linear suitability formulation benchmarked against LightGBM LambdaMART and audited for demographic neutrality."))
    story.append(b("6. <b>Tabular GBDT Hireability Modeling:</b> A 67-feature gradient boosted classifier predicting hireability probability with 0.9763 ROC-AUC across 20,000 candidate profiles."))
    story.append(b("7. <b>Closed-Loop Career Mobility DAG:</b> A directed acyclic graph transforming candidate rejection into personalized, paced developmental roadmaps."))
    story.append(b("8. <b>Full Production Verification:</b> A comprehensive suite of automated tests verifying end-to-end reliability and cross-service data integrity."))

    story.append(p("1.8 Dissertation Organization and Roadmap", h1_style))
    story.append(p("The remainder of this dissertation is organized as follows: Chapter 2 reviews foundational literature across ATS parsing, interview NLP, Learning-to-Rank, and career modeling. Chapter 3 presents the overall system architecture, inter-service contracts, and persistence topology. Chapter 4 details the mathematical formulations and algorithms across all four analytical components. Chapter 5 documents the engineering implementation, technology stack, and testing protocols. Chapter 6 provides comprehensive empirical results, per-component evaluations, and case studies. Chapter 7 examines ethical AI governance and threats to validity. Chapter 8 concludes the dissertation with future research trajectories."))
    story.append(PageBreak())
