import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from thesis_builder.styles import clean_xml, create_table_box, create_code_box, PRINTABLE_WIDTH
from thesis_builder.canvas_helper import PageTracker

def append_ch4(story, styles, fig_dir, tracker=None):
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

    # 4 PRODUCT AND SOLUTION DESIGN
    track('ch4')
    story.append(Paragraph("4 PRODUCT AND SOLUTION DESIGN", h_ch))
    story.append(Spacer(1, 4))

    # 4.1 Requirements
    track('sec4_1')
    story.append(Paragraph("4.1 Requirements", h_sec))
    story.append(Paragraph("The design of Component 1 is governed by formal functional (FR) and non-functional (NFR) engineering requirements:", p_body))
    story.append(Paragraph("<b>FR1 (Layout-Aware Ingestion &amp; PII Redaction):</b> Ingest unstructured resumes in PDF, DOCX, and TXT formats; reconstruct reading order across multi-column layouts; normalize ligatures; and redact candidate PII (names, emails, phones, addresses, profile links) prior to feature generation.", p_bullet))
    story.append(Paragraph("<b>FR2 (Boundary-Guarded NER):</b> Extract competencies from a taxonomy of over 400 canonical IT skills across seven domains, deploying look-around assertion shields to eliminate polysemous false positives on ambiguous identifiers.", p_bullet))
    story.append(Paragraph("<b>FR3 (Temporal Experience Disambiguation):</b> Formalize a calendar interval union algorithm to deduplicate concurrent employment contracts and strictly separate academic coursework projects from commercial corporate tenure.", p_bullet))
    story.append(Paragraph("<b>FR4 (Two-Dimensional Credential Decoupling):</b> Evaluate academic qualifications through a decoupled matrix multiplying degree attainment tier by disciplinary field relevance.", p_bullet))
    story.append(Paragraph("<b>FR5 (Contextual Evidence Weighting):</b> Score technical skills hierarchically based on document context, penalizing isolated keyword mentions (w = 0.40) relative to verified workplace execution (w = 1.00).", p_bullet))
    story.append(Paragraph("<b>FR6 (Multi-Class Role Classification):</b> Predict the candidate's primary IT role and top alternative roles across 20 canonical specializations using balanced statistical inference.", p_bullet))
    story.append(Paragraph("<b>FR7 (Tri-Pillar Output &amp; Roadmap Synthesis):</b> Emit the uncollapsed qualification vector S_C1 = [S_skill, S_exp, S_edu] via RESTful API, and synthesize a four-milestone learning roadmap for deficient competencies.", p_bullet))
    story.append(Paragraph("<b>NFR1 (Real-Time Throughput):</b> Machine learning model inference latency must remain strictly below 5.0 milliseconds per resume on standard CPU hardware.", p_bullet))
    story.append(Paragraph("<b>NFR2 (Lightweight Footprint):</b> Memory footprint must not exceed 500 MB RAM during peak ingestion, eliminating external GPU dependencies.", p_bullet))
    story.append(Paragraph("<b>NFR3 (Architectural Explainability):</b> Every role classification and qualification score must produce a closed-form, mathematically auditable explanation for hiring managers.", p_bullet))

    # 4.2 Component architecture within the complete solution
    track('sec4_2')
    story.append(Paragraph("4.2 Component architecture within the complete solution", h_sec))
    story.append(Paragraph("Figure 4.1 illustrates the end-to-end analytical state transition flow of a candidate through the RecruitAI platform. Component 1 functions as the front-line intelligence gateway, receiving raw documents and delivering verified profiles to downstream microservices.", p_body))
    story.append(Spacer(1, 4))

    fig_life = os.path.join(fig_dir, "fig9_integrated_lifecycle_flow.png")
    if os.path.exists(fig_life):
        track('fig4_1')
        story.append(Image(fig_life, width=410, height=197))
        story.append(Paragraph("Figure 4.1: End-to-end RecruitAI candidate lifecycle and analytical state flow.", caption_fig))
        story.append(Spacer(1, 6))

    story.append(Paragraph("Inside Component 1, processing executes across six pipelined stages: (1) layout-aware ingestion and PII stripping; (2) boundary-guarded entity recognition; (3) interval union experience deduplication; (4) two-dimensional academic credential evaluation; (5) balanced multinomial logistic role classification; and (6) dense semantic matching with Tri-Pillar scoring.", p_body))

    # 4.3 Design alternatives and decisions
    track('sec4_3')
    story.append(Paragraph("4.3 Design alternatives and decisions", h_sec))
    story.append(Paragraph("During system design, three critical architectural trade-offs were evaluated:", p_body))
    story.append(Paragraph("<b>1. Linear Classifier vs. Deep Transformer:</b> While fine-tuned transformers (e.g., DistilBERT) achieve marginally higher accuracy (91.80% vs. 87.42%), their heavy inference latency (142.0 ms vs. 2.4 ms) and 268 MB memory requirement present substantial barriers to high-throughput intake. Furthermore, deep transformers operate as black-box models, preventing closed-form explanations. Balanced logistic regression was selected because it delivers 59x higher throughput, sub-3ms latency, and closed-form SHAP feature attributions.", p_bullet))
    story.append(Paragraph("<b>2. Regex Look-Around Shields vs. Statistical CRF NER:</b> Training statistical CRF taggers requires immense hand-labeled technical corpora and degrades on unseen libraries. Context-guarded regular expression look-arounds execute in sub-millisecond time, guarantee zero subtoken collisions on known polysemous words (C, R, Go, REST), and allow continuous taxonomy updates without retraining.", p_bullet))
    story.append(Paragraph("<b>3. Tri-Pillar Uncollapsed Vector vs. Monolithic Score:</b> Monolithic matching scores conceal candidate deficiencies and allow high educational degrees to mask absent technical skills. Component 1 decouples candidate qualifications into three orthogonal pillars (S_skill, S_exp, S_edu), preserving distinct analytical dimensions for downstream ranking in Component 3.", p_bullet))

    # 4.4 Detailed design
    track('sec4_4')
    story.append(Paragraph("4.4 Detailed design", h_sec))
    story.append(Paragraph("This section presents the mathematical formulations and algorithms underpinning Component 1.", p_body))

    # Algorithm 4.1
    story.append(Paragraph("<b>Algorithm 4.1: Boundary-Guarded Technical Skill Pattern Compiler</b>", p_body_bold))
    algo41_text = """Algorithm 4.1: Boundary-Guarded Technical Skill Pattern Compiler
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
    story.append(create_code_box(algo41_text, styles))
    story.append(Spacer(1, 6))

    # Algorithm 4.2
    story.append(Paragraph("<b>Algorithm 4.2: Chronological Interval Union and Deduplication</b>", p_body_bold))
    algo42_text = """Algorithm 4.2: Chronological Interval Union and Deduplication
Input:  Extracted employment intervals I = {[s_1, e_1], [s_2, e_2], ..., [s_M, e_M]}
Output: Total deduplicated commercial tenure E_tot (years)

1:  Sort I in ascending order of start timestamp s_i
2:  Initialize merged interval stack M = []
3:  for each interval [s_i, e_i] in I do
4:      if M is empty then
5:          M.push([s_i, e_i])
6:      else
7:          [s_prev, e_prev] = M.top()
8:          if s_i <= e_prev then  // Overlap or contiguous interval detected
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
    story.append(create_code_box(algo42_text, styles))
    story.append(Spacer(1, 6))

    # Two-Dimensional Credential Decoupling
    story.append(Paragraph("Academic qualifications are decoupled into degree attainment tier level L_deg in [0, 100] and disciplinary field relevance multiplier M_field in [0.2, 1.0]. The composite credential score is their product: <b>S_edu = L_deg · M_field</b>. Table 4.1 presents the evaluation matrix.", p_body))
    story.append(Spacer(1, 4))

    track('tab4_1')
    story.append(Paragraph("Table 4.1: Academic degree tier level and disciplinary field relevance scoring matrix (S_edu in [0, 100]).", caption_tab))
    mat_data = [
        [Paragraph("<b>Degree Level (L_deg)</b>", cell_bold), Paragraph("<b>Core Computing (1.00)</b>", cell_bold), Paragraph("<b>Adjacent Tech (0.75)</b>", cell_bold), Paragraph("<b>Quantitative Non-Tech (0.50)</b>", cell_bold), Paragraph("<b>General Non-Tech (0.20)</b>", cell_bold)],
        [Paragraph("Doctorate / Ph.D. (100)", cell), Paragraph("100.0 (CS, SE, AI)", cell), Paragraph("75.0 (EE, Telecom)", cell), Paragraph("50.0 (Physics, Math)", cell), Paragraph("20.0 (Humanities)", cell)],
        [Paragraph("Master's / M.Sc. (90)", cell), Paragraph("90.0 (M.Sc. in IT)", cell), Paragraph("67.5 (Data Analytics)", cell), Paragraph("45.0 (Finance, Econ)", cell), Paragraph("18.0 (Arts, Languages)", cell)],
        [Paragraph("Bachelor's (Hons) (80)", cell), Paragraph("80.0 (B.Sc. Hons SE)", cell), Paragraph("60.0 (Computer Systems)", cell), Paragraph("40.0 (B.Com, Statistics)", cell), Paragraph("16.0 (BA, Management)", cell)],
        [Paragraph("Higher Diploma (65)", cell), Paragraph("65.0 (SLIIT HND, DUT)", cell), Paragraph("48.75 (Dip. Networks)", cell), Paragraph("32.5 (Dip. Accounting)", cell), Paragraph("13.0 (General Dip.)", cell)],
        [Paragraph("Foundation / None (50)", cell), Paragraph("50.0 (Bootcamp/Self)", cell), Paragraph("37.5 (Tech Cert)", cell), Paragraph("25.0 (High School)", cell), Paragraph("10.0 (No Degree)", cell)],
    ]
    mat_tab = create_table_box(mat_data, [85, 80, 80, 85, 81], styles, is_header=True)
    story.append(mat_tab)
    story.append(Spacer(1, 6))

    # Contextual Evidence Weighting
    story.append(Paragraph("To suppress keyword stuffing, every extracted skill mention s is assigned an evidentiary weight E(s) = min( 1.0, Σ_{c in C(s)} w_c · n_c(s) ), where w_c corresponds to: (1) Workplace execution (w = 1.00); (2) Technical project (w = 0.70); and (3) Isolated mention (w = 0.40). The technical skill alignment score is computed as:", p_body))
    story.append(Paragraph("<b>S_skill = ( Σ_{s ∈ K_cand ∩ K_req} w_s · E(s) / Σ_{s ∈ K_req} w_s ) · 100</b>", p_body_bold))
    story.append(Paragraph("where w_s in [1, 3] represents skill criticality for the target job role.", p_body))

    # Tri-Pillar Formulation
    story.append(Paragraph("The overall composite CV fit score S_cv in [0, 100] combines the three pillars through calibrated weights: <b>S_cv = 0.50 · S_skill + 0.30 · S_exp + 0.20 · S_edu</b>, where experience tenure score S_exp = min( (E_cand / max(E_req, 1.0)) · 100, 100 ) with a 15% tolerance margin for rapid career progression.", p_body))
    story.append(Spacer(1, 4))

    # Table 4.2 Canonical IT Roles
    track('tab4_2')
    story.append(Paragraph("Table 4.2: Canonical IT job role benchmark competencies, domain groupings, and experience baselines.", caption_tab))
    canon_data = [
        [Paragraph("<b>Job Role</b>", cell_bold), Paragraph("<b>Domain Group</b>", cell_bold), Paragraph("<b>Core Canonical Skills</b>", cell_bold), Paragraph("<b>T_req</b>", cell_bold)],
        [Paragraph("AI/NLP Engineer", cell), Paragraph("Data &amp; AI", cell), Paragraph("Python, PyTorch, Transformers, spaCy, HuggingFace", cell), Paragraph("3.0 yrs", cell)],
        [Paragraph("Backend Developer", cell), Paragraph("Core SE", cell), Paragraph("Python, Java, Go, FastAPI, Spring Boot, PostgreSQL, Redis", cell), Paragraph("3.0 yrs", cell)],
        [Paragraph("Cloud Solutions Architect", cell), Paragraph("Cloud &amp; Infra", cell), Paragraph("AWS, Azure, GCP, Terraform, Kubernetes, Microservices", cell), Paragraph("5.0 yrs", cell)],
        [Paragraph("Cybersecurity Analyst", cell), Paragraph("Security", cell), Paragraph("SIEM, SOC, Wireshark, Metasploit, Cryptography, OWASP", cell), Paragraph("3.0 yrs", cell)],
        [Paragraph("Data Engineer", cell), Paragraph("Data &amp; AI", cell), Paragraph("Python, Spark, SQL, Airflow, Kafka, Hadoop, Snowflake", cell), Paragraph("3.0 yrs", cell)],
        [Paragraph("DevOps Engineer", cell), Paragraph("Cloud &amp; Infra", cell), Paragraph("Docker, Kubernetes, CI/CD, Terraform, Ansible, Linux", cell), Paragraph("3.0 yrs", cell)],
        [Paragraph("Frontend Developer", cell), Paragraph("Core SE", cell), Paragraph("JavaScript, TypeScript, React, HTML5, CSS3, Redux, Next.js", cell), Paragraph("2.0 yrs", cell)],
        [Paragraph("Full Stack Developer", cell), Paragraph("Core SE", cell), Paragraph("React, Node.js, Python, PostgreSQL, Docker, REST, TypeScript", cell), Paragraph("3.0 yrs", cell)],
        [Paragraph("Mobile App Developer", cell), Paragraph("Core SE", cell), Paragraph("Flutter, React Native, Swift, Kotlin, Android, iOS, Dart", cell), Paragraph("2.0 yrs", cell)],
        [Paragraph("Site Reliability Engineer", cell), Paragraph("Cloud &amp; Infra", cell), Paragraph("Kubernetes, Go, Python, Prometheus, Grafana, Linux, CI/CD", cell), Paragraph("4.0 yrs", cell)],
    ]
    canon_tab = create_table_box(canon_data, [95, 75, 195, 46], styles, is_header=True)
    story.append(canon_tab)
    story.append(Spacer(1, 6))

    # 4.5 Standards and professional practice
    track('sec4_5')
    story.append(Paragraph("4.5 Standards and professional practice", h_sec))
    story.append(Paragraph("The software engineering implementation adheres strictly to industrial best practices: (1) <i>Code Standards:</i> PEP 8 compliance, comprehensive type hinting with Pydantic v2 schemas; (2) <i>API Standards:</i> RESTful HTTP semantics, OpenAPI 3.0 auto-documentation, CORS security; (3) <i>Security Standards:</i> OWASP Top 10 compliance, input validation on multipart file uploads, sanitization against injection attacks; and (4) <i>Testing Protocols:</i> 100% pass rate across 195 automated unit, regression, and integration tests.", p_body))
    story.append(PageBreak())
