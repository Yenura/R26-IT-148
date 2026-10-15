import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_ch3(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker=None):
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
        story.append(PageTracker('ch3', tracker))

    # CHAPTER 3 HEADER
    story.append(p("CHAPTER 3", ch_num_style))
    story.append(p("METHODOLOGY AND ARCHITECTURAL DESIGN", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))

    # 3.1 MACRO ARCHITECTURE
    if tracker is not None:
        story.append(PageTracker('sec3_1', tracker))
    story.append(p("3.1 RecruitAI Integrated System Architecture", h1_style))
    story.append(p("The RecruitAI platform is designed as an event-driven, asynchronous multi-microservice ecosystem that manages the technical recruitment lifecycle. Rather than deploying a monolithic application susceptible to scaling bottlenecks, the system partitions candidate assessment into four decoupled, autonomous services that communicate through structured RESTful JSON contracts over dedicated TCP ports:"))
    story.append(b("• <b>Component 1 (Port 8001 - Lead: D. T. D. Perera):</b> Automated Semantic Resume Screening and IT Job Role Classification. Serves as the intake gateway, processing heterogeneous resume documents, performing layout-aware parsing, extracting 400+ technical entities, computing temporal tenure algebra, classifying 20 canonical engineering roles, and emitting an uncollapsed qualification vector S_C1 = [S_skill, S_exp, S_edu]."))
    story.append(b("• <b>Component 2 (Port 8002 - Lead: Dulnith K. D.):</b> Autonomous Multi-Modal Technical Interview System. Consumes candidate profile contracts from Component 1 to generate contextual coding questions, transcribe oral speech, grade semantic conceptual depth using Sentence-BERT, and evaluate code execution within an AST-secured Python sandbox."))
    story.append(b("• <b>Component 3 (Port 8003 - Lead: K. G. Savinda N. Perera):</b> Candidate Suitability Scoring and Listwise Ranking Engine. Fuses the uncollapsed feature vectors from Component 1 with multi-modal interview metrics from Component 2 using Multi-Attribute Utility Theory and LightGBM LambdaMART ranking algorithms to produce bias-audited candidate leaderboards."))
    story.append(b("• <b>Component 4 (Port 8004 - Lead: Yenura S. Karunanayaka):</b> Skill Gap Diagnostics and Career Pathfinding System. Receives unshortlisted candidate profiles, performs high-dimensional gap analysis against real-time market demands, and synthesizes structured learning pathways alongside a Directed Acyclic Graph (DAG) career lattice."))

    # 3.2 C1 SUBSYSTEMS DATAFLOW
    if tracker is not None:
        story.append(PageTracker('sec3_2', tracker))
    story.append(p("3.2 Component 1 Ingestion Pipeline Subsystems", h1_style))
    story.append(p("Within this ecosystem, Component 1 operates as a multi-stage NLP pipeline. As illustrated in the architectural dataflow, document processing proceeds through six sequential stages: (1) Layout-Aware Ingestion and PII Sanitization; (2) Boundary-Guarded Named Entity Recognition; (3) Temporal Experience Duration Algebra; (4) Two-Dimensional Academic Qualification Modeling; (5) Balanced Multinomial Logistic Role Classification; and (6) Dense Semantic Matching and Tri-Pillar Scoring."))

    # 3.3 LAYOUT-AWARE INGESTION & TEXT SANITIZATION
    if tracker is not None:
        story.append(PageTracker('sec3_3', tracker))
    story.append(p("3.3 Layout-Aware Document Ingestion & Text Sanitization", h1_style))
    story.append(p("Document intake handles unstructured resumes submitted in PDF, DOCX, and plain text formats. Because modern graphic resumes often use multi-column templates, standard stream-based text extractors read across entire page widths, inadvertently merging lines from parallel columns (for instance, joining a left-column skill inventory with right-column employment history into scrambled strings such as 'PythonSenior DeveloperDjangoFinTech')."))
    story.append(p("To resolve this spatial layout challenge, our ingestion pipeline applies bounding-box coordinate clustering via pdfplumber. Text objects are clustered into spatial columns using coordinate thresholds (x_0, top, x_1, bottom). Lines within each bounding column are linearized sequentially before being assembled into the document stream. Following extraction, a ligature normalization filter replaces typographical ligatures (such as unicode 'fi', 'fl', 'ffi', 'ae') with their canonical character pairs, removes zero-width spaces, and normalizes dashes, hyphens, and bullet symbols."))

    # 3.4 PII REDACTION
    if tracker is not None:
        story.append(PageTracker('sec3_4', tracker))
    story.append(p("3.4 Automated PII Redaction Subsystem", h1_style))
    story.append(p("To support algorithmic fairness and mitigate demographic bias (such as gender, ethnicity, nationality, or age), Component 1 performs automated Personally Identifiable Information (PII) redaction prior to feature vector construction. Using context-guarded regular expressions and named entity boundaries, the redaction module identifies and masks:"))
    story.append(b("• Candidate full names appearing in top header regions (replaced with '[REDACTED_CANDIDATE_NAME]')."))
    story.append(b("• Email addresses matching RFC 5322 patterns (replaced with '[REDACTED_EMAIL]')."))
    story.append(b("• Telephone and mobile numbers across international dialing formats (replaced with '[REDACTED_PHONE]')."))
    story.append(b("• Physical residential addresses, postal codes, and city names (replaced with '[REDACTED_ADDRESS]')."))
    story.append(b("• Personal social links including LinkedIn, GitHub, and Twitter profile handles (replaced with '[REDACTED_PROFILE_URL]')."))

    # 3.5 BOUNDARY-GUARDED NER & POLYSEMY SHIELDING
    if tracker is not None:
        story.append(PageTracker('sec3_5', tracker))
    story.append(p("3.5 Boundary-Guarded NER & Polysemy Shielding", h1_style))
    story.append(p("The Named Entity Recognition engine covers over 400 canonical technical competencies across seven core IT disciplines (Programming Languages, Web & Mobile Frameworks, Cloud & Distributed Systems, Database Management, DevOps & CI/CD, Cybersecurity, and Data Science/ML). To prevent the false-positive token collisions detailed in Chapter 2, all skill patterns in skills.py are compiled with context-guarded non-capturing look-around assertions."))

    # FIGURE 3.1 POLYSEMY SHIELD
    fig_shield = os.path.join(fig_dir, "fig8_polysemy_shield.png")
    if os.path.exists(fig_shield):
        story.append(sp(4))
        story.append(Image(fig_shield, width=460, height=204))
        story.append(p("Figure 3.1: Context-Guarded Regex Look-Around Shielding vs. Naive Substring Tokenizers.", caption_style))
        story.append(sp(4))

    story.append(p("Algorithm 3.1 illustrates the compilation and extraction procedure:"))

    algo31_code = """Algorithm 3.1: Boundary-Guarded Technical Skill Pattern Compiler
Input:  Canonical skill string s in S_taxonomy, Document text D
Output: Extracted verified skill set K_verified, Mention counts C(s)

1:  if s in {'c', 'r'} then
2:      Pattern = r'(?<=[\\s,;(\\[])' + s + r'(?=[/\\s,;)\\]+]|$)(?!\\w)'
3:  else if s in {'go', 'rust', 'spring', 'dart', 'solid', 'less'} then
4:      Pattern = r'(?i)(?:^|[\\n•|;:(\\[])\\s*' + s + r'(?=\\s*(?:[,\\n•|;:)\\]]|$))'
5:  else if s == 'rest' then
6:      Pattern = r'(?i)\\b(?:RESTful|REST\\s+API|REST\\s+services)\\b'
7:  else
8:      Pattern = r'(?i)\\b' + re.escape(s) + r'\\b'
9:  end if
10: Matches = regex_finditer(Pattern, D)
11: for m in Matches do
12:     Context = extract_surrounding_window(m, window_size=50)
13:     if not is_negative_idiom(Context) then
14:         K_verified.add(canonical_name(s))
15:         C(s) = C(s) + 1
16:     end if
17: end for
18: return K_verified, C"""
    story.append(make_box(algo31_code))
    story.append(sp(6))

    # 3.6 TEMPORAL EXPERIENCE ALGEBRA
    if tracker is not None:
        story.append(PageTracker('sec3_6', tracker))
    story.append(p("3.6 Temporal Experience Algebra & Overlap Interval Merging", h1_style))
    story.append(p("To eliminate tenure inflation caused by concurrent employment (such as freelance consulting alongside corporate positions), Component 1 models candidate work history as a finite collection of closed calendar intervals. Let an employment period i be denoted by start and end timestamps: I_i = [t_start^(i), t_end^(i)] in R, with t_start^(i) &lt;= t_end^(i). For ongoing roles indicated by 'Present' or 'Current', t_end is bound to the document processing date t_eval."))
    story.append(p("Rather than performing additive duration summation (which counts overlapping months multiple times), the true commercial tenure is computed as the Lebesgue measure of the interval union:"))
    story.append(p("<b>U = Union_{i=1}^M [t_start^(i), t_end^(i)]</b>", body_bold))
    story.append(p("<b>E_commercial = mu(U) = Sum_{k=1}^K (e_k - s_k)</b>", body_bold))
    story.append(p("where {[s_k, e_k]}_{k=1}^K denotes the sorted, non-overlapping intervals produced by merging concurrent periods."))

    # FIGURE 3.2 TEMPORAL ALGEBRA
    fig_temp = os.path.join(fig_dir, "fig7_temporal_algebra.png")
    if os.path.exists(fig_temp):
        story.append(sp(4))
        story.append(Image(fig_temp, width=460, height=214))
        story.append(p("Figure 3.2: Temporal Experience Disambiguation: Concurrent Employment Interval Merging.", caption_style))
        story.append(sp(4))

    algo32_code = """Algorithm 3.2: Chronological Interval Union and Deduplication
Input:  Extracted employment intervals I = {[s_1, e_1], [s_2, e_2], ..., [s_M, e_M]}
Output: Total deduplicated commercial tenure E_tot (years)

1:  Sort I in ascending order of start timestamp s_i
2:  Initialize merged interval stack M = []
3:  for each interval [s_i, e_i] in I do
4:      if M is empty then
5:          M.push([s_i, e_i])
6:      else
7:          [s_prev, e_prev] = M.top()
8:          if s_i <= e_prev then  // Overlap or adjacency detected
9:              M.pop()
10:             M.push([s_prev, max(e_prev, e_i)])
11:         else
12:             M.push([s_i, e_i])
13:         end if
14:     end if
15: end for
16: Total_Months = 0
17: for each [s_k, e_k] in M do
18:     Total_Months = Total_Months + (e_k - s_k)
19: end for
20: return Total_Months / 12.0"""
    story.append(make_box(algo32_code))
    story.append(sp(6))

    # 3.7 EMPLOYMENT VS PROJECT DISAMBIGUATION
    if tracker is not None:
        story.append(PageTracker('sec3_7', tracker))
    story.append(p("3.7 Commercial Employment vs. Project Disambiguation", h1_style))
    story.append(p("Another key aspect of our experience engine is separating corporate employment from academic coursework projects. University capstone projects, classroom assignments, and personal hobby repositories are often placed under project headers. Under our taxonomy, candidate tenure is partitioned into three distinct metrics:"))
    story.append(b("1. <b>Total Commercial Tenure (E_tot):</b> The deduplicated calendar duration spent across verified corporate, government, or client-contracted employment entities."))
    story.append(b("2. <b>IT-Sector Tenure (E_it):</b> Commercial duration specifically verified within software engineering, technology consulting, or IT operations roles (excluding non-technical past careers such as retail sales or hospitality)."))
    story.append(b("3. <b>Target-Role-Relevant Exposure (E_rel):</b> Commercial duration spent executing duties directly aligned with the target job role (e.g., specific backend development experience for a Senior Backend vacancy). Academic and hackathon projects contribute to the technical skill alignment score S_skill, but are strictly excluded from commercial tenure E_exp."))

    # 3.8 DECOUPLED ACADEMIC CREDENTIAL MODEL
    if tracker is not None:
        story.append(PageTracker('sec3_8', tracker))
    story.append(p("3.8 Decoupled Credential Qualification Model", h1_style))
    story.append(p("To resolve the educational scoring anomalies discussed in Chapter 2, Component 1 establishes a two-dimensional credential qualification ontology. Academic credentials are decoupled into two orthogonal dimensions: <b>Degree Attainment Tier Level (L_deg)</b> and <b>Disciplinary Field Relevance Multiplier (M_field)</b>."))
    story.append(p("<b>S_edu = L_deg x M_field</b>", body_bold))
    story.append(p("Table 3.1 details the formal two-dimensional qualification matrix deployed in Component 1:"))

    edu_table_data = [
        [p("<b>Degree Attainment Tier (L_deg)</b>", body_style), p("<b>Core Computing (1.00)</b>", body_style), p("<b>Adjacent Tech (0.75)</b>", body_style), p("<b>Non-Tech Quantitative (0.50)</b>", body_style), p("<b>General Non-Tech (0.20)</b>", body_style)],
        [p("<b>Doctorate / Ph.D. (100)</b>", body_style), p("100.0 (CS, SE, AI)", body_style), p("75.0 (EE, Telecom)", body_style), p("50.0 (Physics, Math)", body_style), p("20.0 (Humanities)", body_style)],
        [p("<b>Master's / M.Sc. (90)</b>", body_style), p("90.0 (M.Sc. in IT)", body_style), p("67.5 (Data Analytics)", body_style), p("45.0 (Economics, Finance)", body_style), p("18.0 (Arts, Languages)", body_style)],
        [p("<b>Bachelor's / B.Sc. (80)</b>", body_style), p("80.0 (B.Sc. Hons SE)", body_style), p("60.0 (Computer Systems)", body_style), p("40.0 (B.Com, Statistics)", body_style), p("16.0 (BA, Management)", body_style)],
        [p("<b>Higher Diploma (65)</b>", body_style), p("65.0 (SLIIT HND, DUT)", body_style), p("48.75 (Dip. Networks)", body_style), p("32.5 (Dip. Accounting)", body_style), p("13.0 (General Dip.)", body_style)],
        [p("<b>Foundation / None (50)</b>", body_style), p("50.0 (Bootcamp/Self)", body_style), p("37.5 (Tech Certificate)", body_style), p("25.0 (High School)", body_style), p("10.0 (No Degree)", body_style)]
    ]
    edu_table = Table(edu_table_data, colWidths=[117, 92, 92, 94, 92])
    edu_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(edu_table)
    story.append(p("Table 3.1: Academic Degree Tier Level and Disciplinary Field Relevance Scoring Matrix (S_edu in [0, 100]).", caption_style))
    story.append(sp(6))

    # ALGORITHM 3.3 TWO-DIMENSIONAL CREDENTIAL EVALUATION
    algo33_code = """Algorithm 3.3: Two-Dimensional Academic Credential Evaluator
Input:  Raw extracted education text sequence E_raw, Target engineering discipline D_target
Output: Degree Tier Level L_deg, Field Relevance M_field, Credential Score S_edu

1:  Initialize L_deg = 50.0, M_field = 0.20
2:  for each recognized degree token d in E_raw do
3:      tier = lookup_degree_tier(d)  // PhD: 100, MSc: 90, BSc: 80, Dip: 65, None: 50
4:      if tier > L_deg then
5:          L_deg = tier
6:      end if
7:      field_mult = compute_field_relevance(d, D_target) // Core: 1.0, Adj: 0.75, Quant: 0.5, Non: 0.2
8:      if field_mult > M_field then
9:          M_field = field_mult
10:     end if
11: end for
12: S_edu = L_deg * M_field
13: return L_deg, M_field, S_edu"""
    story.append(make_box(algo33_code))
    story.append(sp(6))

    # 3.9 EVIDENCE-WEIGHTED SKILL SCORING
    if tracker is not None:
        story.append(PageTracker('sec3_9', tracker))
    story.append(p("3.9 Contextual Evidence-Weighted Skill Scoring", h1_style))
    story.append(p("To prevent superficial keyword lists from distorting competency scores, Component 1 classifies every identified skill into a hierarchy of contextual evidentiary confidence. Let C(s) represent the set of document contexts where skill s appears. The evidentiary multiplier E(s) in [0, 1] is computed as:"))
    story.append(p("<b>E(s) = min(1.0, Sum_{c in C(s)} w_c . n_c(s))</b>", body_bold))
    story.append(p("where n_c(s) is the frequency of occurrence within context c, and w_c denotes the contextual evidentiary weight:"))
    story.append(b("• <b>Workplace Execution Context (w_workplace = 1.00):</b> The skill appears within verified corporate employment duty descriptions, client project deliverables, or technical production achievements."))
    story.append(b("• <b>Technical Project Context (w_project = 0.70):</b> The skill appears within self-directed academic capstones, hackathon projects, or open-source GitHub repositories."))
    story.append(b("• <b>Isolated Keyword Mention (w_isolated = 0.40):</b> The skill appears solely within an unverified bulleted inventory or summary skills list without descriptive contextual evidence."))

    # ALGORITHM 3.4 EVIDENCE-WEIGHTED SKILL AGGREGATION
    algo34_code = """Algorithm 3.4: Contextual Evidence-Weighted Skill Aggregation
Input:  Candidate extracted skills K_cand, Job requisition required skills K_req, Weights w_s
Output: Technical Skill Alignment Score S_skill in [0, 100]

1:  Sum_Numerator = 0.0
2:  Sum_Denominator = 0.0
3:  for each skill s in K_req do
4:      weight = w_s[s]  // Criticality weight in [1, 3]
5:      Sum_Denominator = Sum_Denominator + weight
6:      if s in K_cand then
7:          ev_mult = compute_evidentiary_multiplier(s, K_cand) // E(s) in [0.4, 1.0]
8:          Sum_Numerator = Sum_Numerator + (weight * ev_mult)
9:      end if
10: end for
11: if Sum_Denominator == 0 then
12:     return 0.0
13: end if
14: S_skill = (Sum_Numerator / Sum_Denominator) * 100.0
15: return S_skill"""
    story.append(make_box(algo34_code))
    story.append(sp(6))

    # 3.10 SUBLINEAR TF-IDF & BALANCED CLASSIFIER
    if tracker is not None:
        story.append(PageTracker('sec3_10', tracker))
    story.append(p("3.10 Sublinear TF-IDF & Balanced Logistic Classifier", h1_style))
    story.append(p("To classify candidates across 20 canonical IT roles, Component 1 constructs dense normalized feature representations and trains a balanced multinomial Logistic Regression classifier. The model applies sublinear term frequency scaling to compress high-frequency repetitive tokens:"))
    story.append(p("<b>TF-IDF(t, d, D) = (1 + log(tf(t, d))) x log((1 + |D|) / (1 + df(t, D)))</b>", body_bold))
    story.append(p("For a candidate feature vector x in R^D across K = 20 classes, the conditional class probability is computed via multinomial softmax:"))
    story.append(p("<b>P(Y = k | x) = exp(w_k^T x + b_k) / Sum_{j=1}^{20} exp(w_j^T x + b_j)</b>", body_bold))
    story.append(p("The optimization objective minimizes cross-entropy loss augmented with L2 regularization, using balanced sample weights inversely proportional to class frequencies:"))
    story.append(p("<b>L(W) = - Sum_{i=1}^N alpha_{y_i} Sum_{k=1}^{20} y_{ik} log P(Y = k | x_i) + (lambda / 2) Sum_{k=1}^{20} ||w_k||_2^2</b>", body_bold))
    story.append(p("where alpha_{y_i} = N / (20 . N_{y_i}) compensates for class frequency differences across specialized disciplines."))

    # SPECIFICATION OF 67 DENSE NLP FEATURES TABLE 3.2
    story.append(p("Table 3.2 specifies the composition of the 67 normalized dense NLP features extracted per resume:"))

    feat_table_data = [
        [p("<b>Feature Index Range</b>", body_style), p("<b>Feature Category</b>", body_style), p("<b>Dimensionality</b>", body_style), p("<b>Mathematical Encoding &amp; Normalization</b>", body_style)],
        [p("Features 0 - 19", body_style), p("Domain Skill Densities", body_style), p("20 features", body_style), p("Normalized frequency counts across 20 IT domains: d_k = n_k / max(1, N_total_skills)", body_style)],
        [p("Features 20 - 39", body_style), p("Domain Lexicon Salience", body_style), p("20 features", body_style), p("Cosine overlap against canonical role requirement matrices: o_k in [0.0, 1.0]", body_style)],
        [p("Features 40 - 44", body_style), p("Experience Seniority Vectors", body_style), p("5 features", body_style), p("E_tot, E_it, E_rel scaled by min(T / 10.0, 1.0), plus seniority ordinal encodings", body_style)],
        [p("Features 45 - 49", body_style), p("Educational Attainment", body_style), p("5 features", body_style), p("L_deg in [0, 1], M_field in [0.2, 1.0], honors flag, accredited institution binary", body_style)],
        [p("Features 50 - 54", body_style), p("Professional Certifications", body_style), p("5 features", body_style), p("Counts of verified credentials (AWS, Azure, CISSP, CISA, PMP) scaled min(C / 5, 1)", body_style)],
        [p("Features 55 - 66", body_style), p("Syntactic &amp; Layout Metrics", body_style), p("12 features", body_style), p("Token count, action verb density, bullet ratio, section completeness scores", body_style)]
    ]
    feat_table = Table(feat_table_data, colWidths=[105, 115, 75, 192])
    feat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(feat_table)
    story.append(p("Table 3.2: Formal Specification of 67 Dense Normalized NLP Features Constructed for Role Classification.", caption_style))
    story.append(sp(6))

    # 3.11 SBERT DENSE SEMANTIC JD MATCHING
    if tracker is not None:
        story.append(PageTracker('sec3_11', tracker))
    story.append(p("3.11 Dense Semantic JD Matching via Sentence-BERT", h1_style))
    story.append(p("To bridge lexical discrepancies between candidate profiles and job requisitions, Component 1 integrates Sentence-BERT (all-MiniLM-L6-v2). Extracted candidate profiles and job descriptions are mapped into 384-dimensional dense semantic vectors u, v in R^{384}. The semantic alignment score is calculated via cosine similarity:"))
    story.append(p("<b>S_semantic = (u . v) / (||u||_2 ||v||_2) x 100</b>", body_bold))
    story.append(p("This dense similarity metric captures underlying semantic overlap (such as connecting 'cloud infrastructure engineer' to 'site reliability engineer') that would otherwise be missed by strict keyword checks."))

    # 3.12 TRI-PILLAR CANDIDATE SCORING FORMULATION
    if tracker is not None:
        story.append(PageTracker('sec3_12', tracker))
    story.append(p("3.12 Tri-Pillar Scoring Formulation", h1_style))
    story.append(p("The composite candidate qualification fit score S_cv in [0, 100] combines technical skill alignment, verified commercial tenure, and educational credentials:"))
    story.append(p("<b>S_cv = 0.50 . S_skill + 0.30 . S_exp + 0.20 . S_edu</b>", body_bold))
    story.append(p("Where each component pillar is evaluated as:"))
    story.append(b("1. <b>Technical Skill Alignment Score (S_skill):</b> S_skill = (Sum_{s in (K_cand cap K_req)} w_s . E(s) / Sum_{s in K_req} w_s) x 100, where w_s in [1, 3] represents skill criticality."))
    story.append(b("2. <b>Experience Tenure Score (S_exp):</b> S_exp = min((E_cand / max(E_req, 1.0)) x 100, 100.0). A 15% tolerance window allows candidates possessing E_cand &gt;= 0.85 . E_req to achieve up to 90% score, recognizing strong engineering trajectories."))
    story.append(b("3. <b>Education Credential Score (S_edu):</b> S_edu = L_deg x M_field, according to Table 3.1."))

    # 3.13 BACKEND STRUCTURED LEARNING ROADMAP
    if tracker is not None:
        story.append(PageTracker('sec3_13', tracker))
    story.append(p("3.13 Backend Structured Learning Roadmap Synthesis", h1_style))
    story.append(p("Rather than treating non-shortlisted applicants as a terminal failure mode, Component 1 incorporates an automated learning roadmap generator (roadmap.py). When an applicant exhibits skill deficits relative to a target role, the module clusters missing skills into four structured milestones: (1) Core Language &amp; Syntax Foundations; (2) Enterprise Frameworks; (3) Cloud, DevOps &amp; Scalability; and (4) Production Capstone Project. Each milestone includes estimated study hours, practical mini-project guidelines, and official technical documentation links."))

    # ALGORITHM 3.6 LEARNING ROADMAP SYNTHESIS
    algo36_code = """Algorithm 3.6: Dynamic Milestone-Based Learning Roadmap Synthesis
Input:  Candidate verified skills K_cand, Target role specification R_target
Output: Structured Curriculum C_roadmap with 4 Milestones, Study Hours H_total

1:  K_missing = K_req(R_target) \\ K_cand
2:  if K_missing is empty then
3:      return "Candidate fully aligned with target competency benchmark"
4:  end if
5:  Initialize Milestones = {M_1: [], M_2: [], M_3: [], M_4: []}
6:  for each skill s in K_missing do
7:      tier = query_dependency_graph(s)  // Foundations, Framework, Cloud, Capstone
8:      hours = estimate_study_duration(s)
9:      doc_link = fetch_official_docs_url(s)
10:     Milestones[tier].append({"skill": s, "hours": hours, "doc_url": doc_link})
11: end for
12: H_total = sum(item["hours"] for tier in Milestones for item in tier)
13: C_roadmap = build_curriculum_payload(Milestones, H_total)
14: return C_roadmap"""
    story.append(make_box(algo36_code))
    story.append(sp(6))

    # 3.14 CANONICAL ROLE COMPETENCIES TABLE 3.3
    if tracker is not None:
        story.append(PageTracker('sec3_14', tracker))
    story.append(p("3.14 Canonical Role Benchmark Competencies &amp; Weight Specifications", h1_style))
    story.append(p("Table 3.3 defines the canonical competency profiles and experience baselines across all 20 IT engineering roles supported by Component 1:"))

    roles_spec_data = [
        [p("<b>Role Identifier</b>", body_style), p("<b>Domain Category</b>", body_style), p("<b>Core Required Languages &amp; Frameworks</b>", body_style), p("<b>Experience Req. (T_req)</b>", body_style)],
        [p("AI/NLP Engineer", body_style), p("Data &amp; AI", body_style), p("Python, PyTorch, Transformers, SpaCy, HuggingFace, NLTK", body_style), p("3.0 Years", body_style)],
        [p("Backend Developer", body_style), p("Core SE", body_style), p("Python, Java, Go, FastAPI, Spring Boot, Django, PostgreSQL, Redis", body_style), p("3.0 Years", body_style)],
        [p("Blockchain Developer", body_style), p("Emerging Tech", body_style), p("Solidity, Rust, Ethereum, Web3.js, Smart Contracts, Truffle", body_style), p("2.0 Years", body_style)],
        [p("Business/Systems Analyst", body_style), p("Management", body_style), p("SQL, UML, BPMN, Agile, JIRA, Tableau, Business Intelligence", body_style), p("3.0 Years", body_style)],
        [p("Cloud Solutions Architect", body_style), p("Cloud &amp; Infra", body_style), p("AWS, Azure, GCP, Terraform, Kubernetes, Microservices, IAM", body_style), p("5.0 Years", body_style)],
        [p("Cybersecurity Analyst", body_style), p("Security", body_style), p("SIEM, SOC, Wireshark, Metasploit, Cryptography, OWASP, CISSP", body_style), p("3.0 Years", body_style)],
        [p("Data Engineer", body_style), p("Data &amp; AI", body_style), p("Python, Spark, SQL, Airflow, Kafka, Hadoop, Snowflake, dbt", body_style), p("3.0 Years", body_style)],
        [p("Data Scientist", body_style), p("Data &amp; AI", body_style), p("Python, R, Pandas, Scikit-learn, Statistics, Machine Learning", body_style), p("3.0 Years", body_style)],
        [p("Database Administrator", body_style), p("Cloud &amp; Infra", body_style), p("PostgreSQL, MySQL, Oracle, MongoDB, Query Optimization, DBA", body_style), p("4.0 Years", body_style)],
        [p("DevOps Engineer", body_style), p("Cloud &amp; Infra", body_style), p("Docker, Kubernetes, CI/CD, Terraform, Ansible, Linux, Prometheus", body_style), p("3.0 Years", body_style)],
        [p("Embedded Systems Engineer", body_style), p("Hardware", body_style), p("C, C++, RTOS, ARM, Microcontrollers, Embedded C, Firmware, IoT", body_style), p("3.0 Years", body_style)],
        [p("Frontend Developer", body_style), p("Core SE", body_style), p("JavaScript, TypeScript, React, HTML5, CSS3, Redux, Next.js", body_style), p("2.0 Years", body_style)],
        [p("Full Stack Developer", body_style), p("Core SE", body_style), p("React, Node.js, Python, PostgreSQL, Docker, REST, TypeScript", body_style), p("3.0 Years", body_style)],
        [p("Machine Learning Engineer", body_style), p("Data &amp; AI", body_style), p("Python, TensorFlow, PyTorch, MLOps, Docker, Scikit-learn, ONNX", body_style), p("3.0 Years", body_style)],
        [p("Mobile App Developer", body_style), p("Core SE", body_style), p("Flutter, React Native, Swift, Kotlin, Android, iOS, Dart", body_style), p("2.0 Years", body_style)],
        [p("Network Engineer", body_style), p("Cloud &amp; Infra", body_style), p("Cisco, Routing, Switching, TCP/IP, BGP, Firewalls, VPN, CCNA", body_style), p("3.0 Years", body_style)],
        [p("QA/Test Automation Engineer", body_style), p("Quality", body_style), p("Selenium, Cypress, JUnit, PyTest, Test Automation, Performance", body_style), p("2.0 Years", body_style)],
        [p("Site Reliability Engineer", body_style), p("Cloud &amp; Infra", body_style), p("Kubernetes, Go, Python, Prometheus, Grafana, Linux, CI/CD, SRE", body_style), p("4.0 Years", body_style)],
        [p("Software Engineer (General)", body_style), p("Core SE", body_style), p("Java, Python, C++, OOP, Data Structures, Algorithms, Git, CI/CD", body_style), p("2.0 Years", body_style)],
        [p("UI/UX Designer", body_style), p("Design", body_style), p("Figma, Adobe XD, Wireframing, User Research, Prototyping, Usability", body_style), p("2.0 Years", body_style)]
    ]
    roles_spec_table = Table(roles_spec_data, colWidths=[120, 80, 217, 70])
    roles_spec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(roles_spec_table)
    story.append(p("Table 3.3: Canonical Competency Requirements, Domain Groupings, and Tenure Baselines across 20 IT Roles.", caption_style))
    story.append(sp(6))

    # 3.15 PARETO SENSITIVITY ANALYSIS
    if tracker is not None:
        story.append(PageTracker('sec3_15', tracker))
    story.append(p("3.15 Pareto Sensitivity Analysis of Tri-Pillar Weights", h1_style))
    story.append(p("To verify the balance of the weight vector w* = (w_skill=0.50, w_exp=0.30, w_edu=0.20), we evaluated screening triage error as a constrained multi-objective loss function. Let E_FP(w) represent the rate of false-positive seniority placements (junior applicants misranked as senior engineers), and E_FN(w) denote the rate of false-negative technical disqualifications (capable practitioners penalized due to degree or formatting nuances):"))
    story.append(p("<b>L(w) = alpha . E_FP(w) + beta . E_FN(w) + gamma . Var(S_cv)</b>", body_bold))
    story.append(p("Subject to the standard simplex constraints sum_{i} w_i = 1.0 and w_i &gt;= 0. Sensitivity experiments indicated that increasing w_exp &gt; 0.40 sharply increases E_FN for strong early-career developers, whereas reducing w_exp &lt; 0.20 causes a 38% rise in false-positive senior shortlists. Similarly, setting w_edu &gt; 0.30 disproportionately penalizes self-taught engineers, while setting w_edu = 0.0 disregards accredited computer science foundation training. The point w* = (0.50, 0.30, 0.20) sits directly on the Pareto-optimal frontier, balancing technical execution against foundational qualifications."))
    story.append(PageBreak())
