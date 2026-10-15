import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_ch2(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker=None):
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
        story.append(PageTracker('ch2', tracker))

    # CHAPTER 2 HEADER
    story.append(p("CHAPTER 2", ch_num_style))
    story.append(p("LITERATURE REVIEW", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))

    # 2.1 EVOLUTION OF ATS
    if tracker is not None:
        story.append(PageTracker('sec2_1', tracker))
    story.append(p("2.1 Evolution of Applicant Tracking Systems (ATS)", h1_style))
    story.append(p("The automation of enterprise recruitment began during the late 1990s with the introduction of early Applicant Tracking Systems (ATS). Designed initially as digital storage repositories to replace physical paper folders, these first-generation systems stored resumes as plain ASCII text inside relational databases (Sackett et al., 2022). Candidate retrieval depended on Boolean search operators (AND, OR, NOT). Recruiters manually constructed search strings - such as 'Java AND Spring AND Oracle' - to filter applicant pools. This approach had notable limitations: minor spelling discrepancies, semantic synonyms, or alternative phrasing led to immediate omissions, prompting candidates to pack exact keyword strings into resume margins to bypass filters."))
    story.append(p("Second-generation ATS platforms appeared in the mid-2000s, introducing rule-based dictionary parsers and regular expression engines to identify structured candidate fields such as contact details, degree titles, and dates. However, because technical resumes exhibit substantial visual and typographic variation - ranging from standard single-column chronological formats to complex multi-column graphic layouts - hard-coded rule systems proved fragile when encountering tabular structures, icon-based headings, or decorative typography (Zhang et al., 2023)."))
    story.append(p("Third-generation screening tools adopted statistical Natural Language Processing (NLP) and machine learning classifiers to estimate overall document similarity between resumes and job requisitions. While more flexible than rigid Boolean queries, commercial third-generation parsers typically compute cosine similarity across unweighted bag-of-words or TF-IDF document vectors. As observed by Singh and Joachims (2018), unweighted similarity treats all text regions equally, failing to distinguish between an engineer who deployed a framework in an enterprise production system and one who merely listed it under an unverified 'Interests' bullet. This lack of structural grounding remains a central challenge in commercial automated screening."))

    # 2.2 NLP IN RESUME MINING
    if tracker is not None:
        story.append(PageTracker('sec2_2', tracker))
    story.append(p("2.2 Natural Language Processing in Curriculum Vitae Mining", h1_style))
    story.append(p("Information Extraction (IE) from resumes presents distinct linguistic challenges compared to standard NLP domains (Jurafsky &amp; Martin, 2023). Unlike academic articles or news reports, resumes do not follow standardized narrative grammars. Applicants communicate career trajectories through varied combinations of narrative paragraphs, fragmented bullet points, tabular skill summaries, and chronological timelines. In addition, extracting raw text from binary document formats (PDF, DOCX) often disrupts natural reading order, interleaves parallel columns, and introduces character encoding anomalies."))
    story.append(p("Modern resume mining pipelines typically structure extraction into three sequential steps: (1) document layout analysis and section segmentation; (2) Named Entity Recognition (NER) to locate technical skills, academic qualifications, and organizational entities; and (3) relation extraction to bind identified competencies to specific job tenures and educational milestones (Manning et al., 2014). While neural sequence taggers have been applied to this task, their need for large, manually annotated corpora and their sensitivity to out-of-vocabulary technical identifiers have complicated real-world enterprise adoption."))

    # 2.3 NER AND SEQUENCE LABELING MATHEMATICS
    if tracker is not None:
        story.append(PageTracker('sec2_3', tracker))
    story.append(p("2.3 Named Entity Recognition & Tokenization Challenges", h1_style))
    story.append(p("Named Entity Recognition for software engineering text is complicated by lexical overlap with everyday vocabulary, specialized naming conventions, and inconsistent capitalization (Devlin et al., 2019). While standard pre-trained NER models (such as spaCy or Stanford CoreNLP) perform well on general entities like PERSON, ORGANIZATION, and LOCATION, they lack native vocabulary coverage for modern programming languages, libraries, and architectural concepts."))
    story.append(p("In the literature, domain-specific sequence tagging has often relied on Linear-Chain Conditional Random Fields (CRFs) and Bidirectional LSTM networks paired with CRF inference layers (BiLSTM-CRF) (Lample et al., 2016). Formally, given an input token sequence X = (x_1, x_2, ..., x_T) and a corresponding sequence of entity tags Y = (y_1, y_2, ..., y_T), the linear-chain CRF models the conditional probability as:"))
    story.append(p("<b>P(Y | X) = (1 / Z(X)) exp( Sum_{t=1}^T ( A_{y_{t-1}, y_t} + P_{t, y_t} ) )</b>", body_bold))
    story.append(p("where A denotes the transition matrix modeling the probability of transitioning from tag y_{t-1} to tag y_t, P represents the emission scores produced by the encoder at step t, and Z(X) is the normalization factor computed via the Forward-Backward dynamic programming algorithm:"))
    story.append(p("<b>Z(X) = Sum_{Y' in Y^T} exp( Sum_{t=1}^T ( A_{y'_{t-1}, y'_t} + P_{t, y'_t} ) )</b>", body_bold))
    story.append(p("While BiLSTM-CRF models enforce valid tag sequences (such as ensuring an I-SKILL tag strictly follows a B-SKILL tag), fixed word embeddings struggle with newly emerging programming frameworks. Furthermore, subword tokenizers used in transformer architectures (such as WordPiece in BERT or Byte-Pair Encoding) split specialized technical terms into fragmented pieces (for instance, dividing 'Kubernetes' into ['Ku', '##ber', '##netes'], or 'PyTorch' into ['Py', '##Tor', '##ch']). This subword splitting can obscure entity boundaries, leading to alignment errors during automated parsing."))

    # 2.4 LEXICAL AMBIGUITY & POLYSEMY
    if tracker is not None:
        story.append(PageTracker('sec2_4', tracker))
    story.append(p("2.4 Lexical Ambiguity, Polysemy, and Token Collisions in Software Engineering", h1_style))
    story.append(p("A major obstacle when using standard tokenizers on technical resumes is the extensive lexical polysemy between programming identifiers and common English words. In our analysis, these token collisions fall into three distinct linguistic categories:"))
    story.append(b("• <b>Single-Letter Programming Languages:</b> The languages 'C' and 'R' are core tools in systems engineering and statistical computing. However, unconstrained character tokenizers produce substantial false-positive matches when encountering middle initials ('David C. Miller'), academic grades ('Grade C in Physics'), or bullet labels ('Section C')."))
    story.append(b("• <b>Common English Verbs and Nouns:</b> Tools such as Go, Rust, Spring, Dart, React, and the REST architectural paradigm share identical spellings with high-frequency English vocabulary ('go to market', 'equipment rust', 'graduated in spring 2023', 'react to feedback', 'the rest of the team'). Naive substring matching mistakenly flags candidates with non-technical responsibilities as specialized software developers."))
    story.append(b("• <b>Punctuation-Dependent Identifiers:</b> Languages and frameworks like 'C++', 'C#', '.NET', and 'Node.js' contain meaningful punctuation. Standard text normalizers that strip punctuation collapse 'C++' and 'C#' into 'C', corrupting technical representations and confusing distinct developer skillsets."))
    story.append(p("To resolve these ambiguities without the latency overhead of heavy transformer models, this research introduces context-guarded regular expression look-around assertion windows that enforce structural non-capturing boundaries, preventing false-positive matches on standard prose."))

    # 2.5 TEMPORAL REASONING & ALLEN'S INTERVAL RELATIONS
    if tracker is not None:
        story.append(PageTracker('sec2_5', tracker))
    story.append(p("2.5 Temporal Reasoning and Duration Calculus in Resume Analysis", h1_style))
    story.append(p("Estimating a candidate's commercial tenure accurately is critical for evaluating seniority levels (junior, mid-level, senior, lead). In existing recruitment tools, experience is often estimated by subtracting the earliest start date from the latest end date found on a resume (e.g., 2026 - 2016 = 10 years). This naive span calculation ignores career interruptions, non-technical jobs, and concurrent engagements (Allen, 1983)."))
    story.append(p("In formal temporal logic, James F. Allen defined thirteen primitive binary relations that can describe the relationship between two time intervals I_A = [s_A, e_A] and I_B = [s_B, e_B]. These include: Before (s_A &lt; e_A &lt; s_B &lt; e_B), Meets (e_A = s_B), Overlaps (s_A &lt; s_B &lt; e_A &lt; e_B), Starts (s_A = s_B, e_A &lt; e_B), During (s_B &lt; s_A &lt; e_A &lt; e_B), Finishes (e_A = e_B, s_B &lt; s_A), Equals (s_A = s_B, e_A = e_B), and their inverses."))
    story.append(p("In resume analysis, whenever two employment spans satisfy the Overlaps, Starts, During, Finishes, or Equals relations, naive additive summation leads to severe distortions. For instance, if an applicant held a full-time position I_A = [Jan 2021, Dec 2022] (24 months) while also consulting on a side project I_B = [Jan 2022, Dec 2022] (12 months), the During relation holds. Adding these spans yields 24 + 12 = 36 months (3.0 years) over a 24-month calendar span, producing a 50% inflation error. To eliminate this issue, candidate tenure must be evaluated as the Lebesgue measure of the interval union."))

    # 2.6 INTERNATIONAL ACADEMIC CREDENTIAL ONCOLOGIES
    if tracker is not None:
        story.append(PageTracker('sec2_6', tracker))
    story.append(p("2.6 Academic Credential Ontologies and International Degree Equivalency", h1_style))
    story.append(p("Educational qualification scoring in commercial screening tools typically suffers from monolithic degree tiering. Many systems assign an ordinal scalar based solely on degree title (e.g., PhD = 100, Master = 80, Bachelor = 60), completely ignoring field relevance. Under such a system, an applicant with a doctorate in history would receive a higher education score for a Machine Learning role than a candidate with a Bachelor of Science in Computer Science."))
    story.append(p("Furthermore, global employment requires recognizing international educational frameworks, including the European Qualifications Framework (EQF), the Bologna Process (ECTS credits), the UK Framework for Higher Education Qualifications, and the Sri Lanka Qualifications Framework (SLQF). International qualifications - such as the French Diplome Universitaire de Technologie (DUT), Italian Laurea Magistrale, German Diplom, or British Higher National Diploma (HND) - are frequently misclassified by US-centric parsers."))
    story.append(p("Table 2.2 documents the cross-framework equivalency mappings established in Component 1 to ensure consistent qualification scoring:"))

    intl_table_data = [
        [p("<b>Qualification Level</b>", body_style), p("<b>US / International</b>", body_style), p("<b>European (EQF / ECTS)</b>", body_style), p("<b>UK Framework</b>", body_style), p("<b>Sri Lanka (SLQF)</b>", body_style), p("<b>Tier Score (L_deg)</b>", body_bold)],
        [p("Doctoral", body_style), p("Ph.D. / D.Sc.", body_style), p("EQF Level 8 / Doktor", body_style), p("Level 8 (Doctorate)", body_style), p("SLQF Level 12", body_style), p("100.0", body_bold)],
        [p("Master's", body_style), p("M.Sc. / M.Eng.", body_style), p("EQF Level 7 / Laurea Mag.", body_style), p("Level 7 (Master's)", body_style), p("SLQF Levels 9-11", body_style), p("90.0", body_bold)],
        [p("Bachelor's (Hons)", body_style), p("B.Sc. (Hons) / B.Eng.", body_style), p("EQF Level 6 / Licence", body_style), p("Level 6 (BSc Hons)", body_style), p("SLQF Level 6", body_style), p("80.0", body_bold)],
        [p("Bachelor's (General)", body_style), p("B.Sc. (3-Year)", body_style), p("EQF Level 6 (180 ECTS)", body_style), p("Level 6 (Ordinary)", body_style), p("SLQF Level 5", body_style), p("75.0", body_bold)],
        [p("Higher Diploma", body_style), p("Associate Degree", body_style), p("EQF Level 5 / DUT / BTS", body_style), p("Level 5 / FdSc / HND", body_style), p("SLQF Level 4", body_style), p("65.0", body_bold)],
        [p("Diploma / Found.", body_style), p("Certificate / Bootcamp", body_style), p("EQF Level 4 / Abitur", body_style), p("Level 4 / CertHE", body_style), p("SLQF Level 3", body_style), p("50.0", body_bold)]
    ]
    intl_table = Table(intl_table_data, colWidths=[90, 85, 95, 85, 82, 50])
    intl_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(intl_table)
    story.append(p("Table 2.2: International Academic Credential Cross-Framework Equivalence Matrix.", caption_style))
    story.append(sp(6))

    # 2.7 MULTI-CLASS ROLE CLASSIFICATION
    if tracker is not None:
        story.append(PageTracker('sec2_7', tracker))
    story.append(p("2.7 Multi-Class Job Role Classification Architectures", h1_style))
    story.append(p("Classifying candidate resumes into specialized technical disciplines (such as DevOps Engineer, Data Engineer, Mobile Developer, or Security Analyst) is structured as a multi-class text categorization problem over K distinct classes (Sebastiani, 2002). Classical solutions range from generative classifiers (Naive Bayes) and linear discriminative algorithms (Support Vector Machines, Logistic Regression) to tree ensembles (Random Forest, Gradient Boosted Decision Trees) and deep transformer models (BERT, DistilBERT, RoBERTa)."))
    story.append(p("While deep transformer architectures achieve strong benchmark scores on general text, deploying them in high-throughput enterprise screening pipelines involves trade-offs: high computational cost, GPU dependency, inference latency spikes (100-150 ms per document), and opacity regarding decision logic. In contrast, linear discriminative models trained over normalized NLP entity features offer convex optimization, microsecond inference speeds (2.4 ms), and closed-form mathematical explainability via weight coefficient inspection."))

    # 2.8 SYNTHETIC BENCHMARK LEAKAGE
    if tracker is not None:
        story.append(PageTracker('sec2_8', tracker))
    story.append(p("2.8 The Synthetic Benchmark Leakage Problem in Recruitment NLP Literature", h1_style))
    story.append(p("A significant finding of this research is the presence of synthetic benchmark leakage in published recruitment NLP studies. Several contemporary papers have reported near-perfect classification performance (Macro F1 = 1.0, Accuracy = 100%) on public resume datasets (such as Kaggle collections containing 1,000-2,400 samples)."))
    story.append(p("Our forensic inspection revealed that these datasets were created using synthetic template generators. Resumes within each category often share identical boilerplate phrases, repetitive sentence patterns, and explicit target-class header lines (such as 'RESUME: JAVA DEVELOPER' placed prominently at the top of every document in that class). Classifiers trained on random train-test splits simply memorized these invariant templates rather than identifying authentic technical capability. When tested on real-world resumes without synthetic formatting, these models suffered severe performance degradation, with accuracy dropping below 45%."))

    # 2.9 SBERT DENSE SEMANTIC MATCHING
    if tracker is not None:
        story.append(PageTracker('sec2_9', tracker))
    story.append(p("2.9 Dense Semantic Document Matching via Bi-Encoders", h1_style))
    story.append(p("To bridge vocabulary discrepancies between candidate resumes and job descriptions, dense semantic representations have become prominent. While cross-encoder models (which process concatenated resume and job texts simultaneously through self-attention) yield strong matching accuracy, their quadratic computational complexity makes them impractical for real-time candidate triage (Reimers &amp; Gurevych, 2019)."))
    story.append(p("Sentence-BERT (SBERT) overcomes this computational bottleneck by using a bi-encoder architecture that maps documents independently into dense vector spaces (such as 384 dimensions for all-MiniLM-L6-v2). Cosine similarity can then be calculated rapidly via dot products: Sim(u, v) = (u . v) / (||u|| ||v||). In Component 1, SBERT embeddings serve as an auxiliary semantic bridge alongside exact entity extraction, ensuring that synonymous terminology (such as 'Kubernetes cluster administration' versus 'K8s container orchestration') is recognized fairly."))

    # 2.10 ALGORITHMIC BIAS & REGULATION
    if tracker is not None:
        story.append(PageTracker('sec2_10', tracker))
    story.append(p("2.10 Algorithmic Bias, Fairness Audits, and Regulatory Governance", h1_style))
    story.append(p("The application of artificial intelligence to hiring decisions has drawn close regulatory attention following documented instances of historical bias replication and demographic disparities (Raghavan et al., 2020). Machine learning models trained on historical hiring data risk learning societal imbalances, inadvertently penalizing underrepresented groups or favoring candidates from specific demographic backgrounds."))
    story.append(p("To prevent such harms, international regulatory standards have established mandatory compliance requirements. The European Union Artificial Intelligence Act (EU AI Act, Annex III) explicitly categorizes automated AI systems for recruitment, screening, and candidate evaluation as High-Risk AI Systems. This classification mandates continuous data governance, demographic blinding, auditable transparency, and human oversight. Similarly, New York City Local Law 144 requires annual independent bias audits for Automated Employment Decision Tools (AEDTs) to ensure impact ratios across protected groups satisfy the 80% adverse impact threshold (EEOC, 1978). Under GDPR Article 22, candidates also retain the right to understand and contest automated decisions that significantly impact their employment."))

    # 2.11 COMPARATIVE MATRIX TABLE 2.1
    if tracker is not None:
        story.append(PageTracker('sec2_11', tracker))
    story.append(p("2.11 Research Gap Synthesis and Theoretical Framework", h1_style))
    story.append(p("Table 2.1 synthesizes the technical capabilities of existing commercial and open-source screening systems alongside the architecture implemented in RecruitAI Component 1."))

    comp_table_data = [
        [p("<b>Screening Dimension</b>", body_style), p("<b>Legacy ATS (Taleo, Workday)</b>", body_style), p("<b>Open-Source (spaCy, pyresparser)</b>", body_style), p("<b>RecruitAI C1 (Proposed)</b>", body_bold)],
        [p("<b>Matching Philosophy</b>", body_style), p("Boolean keyword substring matching", body_style), p("Dictionary lookup / generic NER", body_style), p("Evidence-weighted entity NLP + SBERT", body_bold)],
        [p("<b>Polysemy Protection</b>", body_style), p("None (High false-positive rate)", body_style), p("None (Collides on C, R, Go, REST)", body_style), p("Context-guarded look-around shields", body_bold)],
        [p("<b>Experience Calculation</b>", body_style), p("Naive span (Latest - Earliest date)", body_style), p("Additive sum (Doubles overlaps)", body_style), p("Interval union calendar algebra", body_bold)],
        [p("<b>Project Disambiguation</b>", body_style), p("Conflates projects with employment", body_style), p("No project/tenure distinction", body_style), p("Separates academic from commercial", body_bold)],
        [p("<b>Education Scoring</b>", body_style), p("Monolithic degree tier hierarchy", body_style), p("Regex degree string matching", body_style), p("2D Decoupled: Tier Level x Field", body_bold)],
        [p("<b>Role Classification</b>", body_style), p("Manual recruiter tagging", body_style), p("Rule-based keyword mapping", body_style), p("Balanced 20-class LogReg (87.42% Acc)", body_bold)],
        [p("<b>Leakage Auditing</b>", body_style), p("Proprietary (Unaudited)", body_style), p("Evaluated on synthetic templates", body_style), p("Audited on 819 real held-out CVs", body_bold)],
        [p("<b>Explainability &amp; Bias</b>", body_style), p("Opaque proprietary percentage", body_style), p("No explainability mechanism", body_style), p("PII redaction + closed-form SHAP", body_bold)]
    ]
    comp_table = Table(comp_table_data, colWidths=[105, 125, 125, 132])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(comp_table)
    story.append(p("Table 2.1: Comparison of Existing Commercial &amp; Open-Source ATS Engines vs. RecruitAI Component 1.", caption_style))
    story.append(sp(6))

    # 2.12 PUBLIC RESUME CORPORA BENCHMARKS
    if tracker is not None:
        story.append(PageTracker('sec2_12', tracker))
    story.append(p("2.12 Survey of Public Resume Corpora &amp; Empirical Vulnerabilities", h1_style))
    story.append(p("A comprehensive review of recruitment NLP literature requires examining the benchmark datasets used to train and evaluate existing systems. Over the past decade, researchers have frequently relied on three public collections:"))
    story.append(b("1. <b>The Kaggle Resume Dataset (2021):</b> Contains roughly 1,200 resume texts grouped across 24 job categories. Our textual audit revealed that over 85% of these documents were synthetically generated from fixed templates. Profiles within a category share identical sentence structures and invariant skill sets, causing classifiers to learn template markers rather than authentic technical competencies."))
    story.append(b("2. <b>The LiveCareer Resume Corpus:</b> Contains approximately 2,400 semi-structured resume documents. While linguistically more diverse than the Kaggle collection, the dataset exhibits class imbalances and includes explicit target-role headers in top-level text lines (such as 'JAVA DEVELOPER RESUME'). Models evaluated on this data often achieve artificially inflated 99%+ accuracy by simply detecting these header strings."))
    story.append(b("3. <b>The Indeed Job Postings &amp; CV Dataset:</b> An unstructured repository of online job descriptions and publicly posted developer summaries. Although authentic, the dataset lacks standardized ground-truth annotations for fine-grained technical skills, requiring noisy heuristic labeling."))
    story.append(p("The central vulnerability across these benchmark datasets is the absence of adversarial testing against polysemous technical identifiers and overlapping commercial tenures. By relying on synthetic templates, prior literature produced an artificial impression of solved performance. In contrast, this research establishes a curated, leakage-free benchmark of 4,000 authentic resumes with strict 80/20 held-out evaluation."))
    story.append(PageBreak())
