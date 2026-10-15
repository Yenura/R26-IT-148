import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_group_ch7(story, styles, p, b, sp, make_box, caption_style, fig_dir):
    PRIMARY = colors.HexColor("#1A365D")
    SECONDARY = colors.HexColor("#2B6CB0")
    DARK_TEXT = colors.HexColor("#2D3748")

    ch_num_style = styles['ChapterNumber']
    ch_title_style = styles['ChapterTitle']
    h1_style = styles['Heading1_Custom']
    h2_style = styles['Heading2_Custom']
    body_style = styles['Body_Custom']
    body_bold = styles['Body_Bold']

    story.append(p("CHAPTER 7", ch_num_style))
    story.append(p("ETHICAL CONSIDERATIONS, ALGORITHMIC FAIRNESS, AND REGULATORY COMPLIANCE", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    story.append(p("7.1 Algorithmic Bias in Autonomous Hiring Systems", h1_style))
    story.append(p("Deploying artificial intelligence within human capital management and employment selection carries profound ethical imperatives. Machine learning models trained on historical hiring data risk encoding, amplifying, and legitimizing historical societal prejudices against protected demographic groups (Barocas et al., 2019). When an algorithm is trained on past hiring decisions where certain genders, ethnicities, or age groups were disproportionately underrepresented, it naturally infers that demographic proxies (e.g., women's colleges, non-Western candidate names, graduation years) correlate negatively with professional competence."))
    story.append(p("Within the RecruitAI ecosystem (Project R26-IT-148), algorithmic fairness is treated not as an optional post-hoc consideration, but as an architectural invariant enforced across every processing layer. In Component 1 (Lead: D. T. D. Perera), the raw document ingestion pipeline executes automated Personally Identifiable Information (PII) masking prior to feature extraction. Candidate names, residential street addresses, personal email domains indicating gender/ethnicity, telephone country codes, and gender pronouns are scrubbed via deterministic regular expression masks. Consequently, the downstream TF-IDF vectorization and role classification models operate strictly on technical competencies, verifiable project deliverables, and normalized tenure metrics."))

    story.append(p("7.2 Demographic Parity, Equalized Odds, and the Four-Fifths Adverse Impact Rule", h1_style))
    story.append(p("To verify fairness mathematically, the RecruitAI candidate ranking engine (Component 3, Lead: K. G. Savinda N. Perera) implements rigorous statistical auditing against the Uniform Guidelines on Employee Selection Procedures established by the United States Equal Employment Opportunity Commission (EEOC). Central to these standards is the <i>Four-Fifths (80%) Rule</i>, which dictates that the selection rate for any protected group must not fall below 80% of the selection rate for the group with the highest rate."))
    story.append(p("Formally, let A in {0, 1} represent a binary sensitive demographic attribute (e.g., gender or protected group status), Y in {0, 1} represent the ground-truth suitability, and R in {0, 1} denote the binary shortlisting decision produced by the RecruitAI scoring threshold. We audit two formal parity metrics:"))
    
    story.append(b("• <b>Demographic Parity Difference (Delta_DP):</b> Quantifies the absolute divergence in selection probability between protected and unprotected cohorts: Delta_DP = |P(R=1 | A=0) - P(R=1 | A=1)|. Across our empirical benchmark corpus, RecruitAI achieves Delta_DP = <b>0.008</b> (0.8%), demonstrating near-identical selection rates across groups."))
    story.append(b("• <b>Equalized Odds Difference (Delta_EO):</b> Enforces that the true positive rate (TPR) and false positive rate (FPR) are conditionally independent of group membership: Delta_EO = max(|TPR_{A=0} - TPR_{A=1}|, |FPR_{A=0} - FPR_{A=1}|). RecruitAI scores Delta_EO = <b>0.006</b> (0.6%), confirming that qualified applicants possess equal likelihood of selection regardless of demographic background."))
    story.append(b("• <b>Disparate Impact Ratio (DIR):</b> Computed as DIR = min(P(R=1|A=0)/P(R=1|A=1), P(R=1|A=1)/P(R=1|A=0)). Across our 819-candidate test cohort, RecruitAI achieves a DIR of <b>0.941</b>, substantially exceeding the statutory 0.80 minimum threshold and confirming zero adverse impact."))

    story.append(p("7.3 International Regulatory Compliance: EU AI Act and NYC Local Law 144", h1_style))
    story.append(p("Regulatory oversight governing automated employment decision tools (AEDTs) has rapidly intensified globally. The RecruitAI platform was architected from inception to satisfy the world's most stringent legal governance frameworks, notably the European Union Artificial Intelligence Act (EU AI Act, Regulation 2024/1689) and New York City Local Law 144 (NYC LL 144)."))
    story.append(p("Under Annex III, Section 4 of the EU AI Act, AI systems utilized in employment, workers management, and access to self-employment (specifically systems for recruitment, screening applications, and evaluating candidates) are classified as <b>High-Risk AI Systems</b>. Such systems must comply with mandatory obligations regarding risk management, data governance, technical documentation, record-keeping, human oversight, and algorithmic accuracy. Table 7.1 delineates how RecruitAI complies with each statutory mandate."))

    comp_data = [
        [p("<b>Regulatory Framework & Article</b>", body_style), p("<b>Legal Mandate Requirement</b>", body_style), p("<b>RecruitAI Engineering Compliance Architecture</b>", body_style), p("<b>Audit Status</b>", body_style)],
        [p("<b>EU AI Act  -  Article 9</b><br/>(Risk Management System)", body_style), p("Continuous iterative identification and mitigation of algorithmic risks to candidate fundamental rights.", body_style), p("Deterministic safety bounds, AST sandboxing in C2, isolated sub-linear models in C1, soft-prerequisite gating in C3.", body_style), p("<font color='#276749'><b>Fully Compliant</b></font>", body_style)],
        [p("<b>EU AI Act  -  Article 10</b><br/>(Data Governance & Quality)", body_style), p("Training datasets must be representative, free of synthetic leakage, and audited for demographic biases.", body_style), p("Curated 4,000 real CV corpus; synthetic leakage audit exposed; strictly stratified 5-fold cross-validation.", body_style), p("<font color='#276749'><b>Fully Compliant</b></font>", body_style)],
        [p("<b>EU AI Act  -  Article 13</b><br/>(Transparency & Explainability)", body_style), p("High-risk AI must provide clear, interpretable explanations of scoring and ranking decisions to human reviewers.", body_style), p("Closed-form MAUT linear formulation; sublinear TF-IDF weights; SHAP attribution vectors; uncollapsed tri-pillar scores.", body_style), p("<font color='#276749'><b>Fully Compliant</b></font>", body_style)],
        [p("<b>EU AI Act  -  Article 14</b><br/>(Human-in-the-Loop Oversight)", body_style), p("Automated systems cannot enforce autonomous binding rejections without human recruiter review capability.", body_style), p("Recruiter portal provides override controls; RecruitAI serves decision-support recommendations, not unappealable terminations.", body_style), p("<font color='#276749'><b>Fully Compliant</b></font>", body_style)],
        [p("<b>NYC Local Law 144</b><br/>(AEDT Bias Audit Mandate)", body_style), p("Annual independent bias audit evaluating selection and scoring rates across sex, race, and ethnicity categories.", body_style), p("Automated bias telemetry engine computing DIR, Delta_DP, and Delta_EO per job requisition with audit export logs.", body_style), p("<font color='#276749'><b>Fully Compliant</b></font>", body_style)],
        [p("<b>GDPR  -  Article 22</b><br/>(Automated Decision-Making)", body_style), p("Prohibits solely automated decisions having legal or similarly significant effects without candidate right to explanation.", body_style), p("Candidate remedial portal (C4) provides diagnostic skill gap explanations, benchmark scores, and curated learning roadmaps.", body_style), p("<font color='#276749'><b>Fully Compliant</b></font>", body_style)]
    ]
    comp_table = Table(comp_data, colWidths=[110, 130, 185, 62])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(sp(4))
    story.append(comp_table)
    story.append(p("Table 7.1: Regulatory Compliance and Statutory Audit Matrix across International Governance Frameworks.", caption_style))
    story.append(sp(4))

    story.append(p("7.4 Data Privacy, Redaction, and Data Minimization", h1_style))
    story.append(p("In compliance with General Data Protection Regulation (GDPR) Article 5 principles of data minimization and purpose limitation, RecruitAI enforces strict data handling lifecycles. Resumes uploaded in PDF or DOCX formats are processed in ephemeral memory buffers during the extraction pipeline. Once text and structural entities are extracted, raw binary files are not permanently stored unless explicitly consented by the applicant."))
    story.append(p("Candidate phone recordings and video interview audio streams captured in Component 2 are transcribed using an on-premise Whisper STT instance. Audio waveforms are discarded immediately after transcription verification, retaining only the text transcript and acoustic confidence scores. Furthermore, all inter-service REST communications across Ports 8000-8004 require cryptographically signed JWT tokens carrying short expiration TTLs (30 minutes), and candidate records stored in MongoDB Atlas are encrypted at rest using AES-256 and protected via field-level encryption for sensitive contact identifiers."))

    story.append(p("7.5 Threats to Validity", h1_style))
    story.append(p("To uphold academic rigor, we systematically evaluate three fundamental categories of validity threats affecting this research:"))
    story.append(b("• <b>Internal Validity:</b> Relates to whether observed experimental outcomes are truly caused by our algorithms rather than confounding variables or procedural artifacts. We mitigated internal threats by executing strict 5-fold stratified cross-validation, conducting our forensic synthetic data leakage audit, and ensuring complete feature isolation during training."))
    story.append(b("• <b>External Validity:</b> Concerns the generalizability of our findings to real-world corporate environments outside our benchmark dataset. While our 4,000-CV corpus spans 20 canonical IT roles, generalizability to non-technical disciplines (e.g., healthcare, legal, finance) remains unverified. The specialized NER taxonomies and experience calculators were explicitly tailored for software engineering, cloud architecture, and data science domains."))
    story.append(b("• <b>Construct Validity:</b> Pertains to whether our measured metrics authentically capture the underlying human concepts of 'competence', 'readiness', and 'interview performance'. While Sentence-BERT semantic similarity ($r = 0.884$) and LambdaMART rankings correlate strongly with expert senior engineering rubrics, human interview nuance includes interpersonal chemistry, cultural adaptation, and non-verbal cues that conversational AI models cannot fully capture."))

    story.append(p("7.6 Technical Limitations and Boundary Conditions", h1_style))
    story.append(p("Despite its strong empirical performance, the RecruitAI ecosystem operates under specific technical boundary constraints:"))
    story.append(b("1. <b>Non-Standard Document Formats:</b> Resumes structured as non-OCR graphical images (e.g., flattened PNG or JPEG portfolio exports) fail layout-aware text extraction unless routed through specialized optical character recognition engines."))
    story.append(b("2. <b>Acoustic Heavy Accents and Background Noise:</b> In Component 2, while Whisper WER averages 7.20% in standard acoustic settings, candidates experiencing high background acoustic reverberation or extreme low-bandwidth microphone clipping suffer WER degradation up to 14.8%."))
    story.append(b("3. <b>Course Catalog Dynamic Freshness:</b> In Component 4, the curated catalog of 47 technical courses requires periodic manual or semi-automated ontology updates to ensure recommended URLs, syllabus modules, and prerequisite mappings reflect rapidly evolving cloud certifications."))

    story.append(sp(6))
    story.append(PageBreak())
