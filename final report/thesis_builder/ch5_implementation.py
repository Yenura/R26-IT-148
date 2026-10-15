import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from thesis_builder.styles import clean_xml, create_table_box, create_code_box, PRINTABLE_WIDTH
from thesis_builder.canvas_helper import PageTracker

def append_ch5(story, styles, fig_dir, tracker=None):
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

    # 5 IMPLEMENTATION INTEGRATION AND TESTING
    track('ch5')
    story.append(Paragraph("5 IMPLEMENTATION INTEGRATION AND TESTING", h_ch))
    story.append(Spacer(1, 4))

    # 5.1 Development environment and technology stack
    track('sec5_1')
    story.append(Paragraph("5.1 Development environment and technology stack", h_sec))
    story.append(Paragraph("Component 1 is engineered as an asynchronous microservice implemented in Python 3.12 and served by Uvicorn ASGI workers on dedicated TCP Port 8001. The technology stack was selected to guarantee high ingestion throughput, deterministic mathematical explainability, and zero external GPU dependency:", p_body))
    story.append(Paragraph("• <b>FastAPI &amp; Pydantic v2:</b> Delivers asynchronous request processing, automatic JSON schema validation, and OpenAPI 3.0 documentation for all document ingestion and evaluation endpoints.", p_bullet))
    story.append(Paragraph("• <b>scikit-learn 1.4.2:</b> Provides high-performance implementations of Multinomial Logistic Regression, sublinear TF-IDF vectorization, Stratified K-Fold cross-validation, and classification metrics.", p_bullet))
    story.append(Paragraph("• <b>sentence-transformers 3.0:</b> Drives the all-MiniLM-L6-v2 bi-encoder model, executing dense semantic document embeddings in microsecond CPU time.", p_bullet))
    story.append(Paragraph("• <b>pdfplumber &amp; PyPDF2:</b> Performs spatial layout reconstruction, bounding-box coordinate clustering, and typography normalizations on multi-column PDF files.", p_bullet))
    story.append(Paragraph("• <b>MongoDB Atlas &amp; Motor:</b> Asynchronous document store for persisting parsed candidate JSON profiles, extracted feature vectors, and evaluation audits.", p_bullet))

    # 5.2 Component implementation
    track('sec5_2')
    story.append(Paragraph("5.2 Component implementation", h_sec))
    story.append(Paragraph("The codebase is organized into modular packages ensuring clean separation of concerns:", p_body))
    dir_tree = """component1/
├── ml/                               # Machine Learning & NLP Core
│   ├── extractor.py                  # CandidateIntelligenceEngine (1,850 LOC)
│   ├── skills.py                     # 400+ Skill Taxonomy & Look-Around Patterns
│   ├── lexicon.py                    # 20 IT Roles & Core Requirement Matrices
│   ├── feature_engineering.py        # Dense 67-Feature Matrix Constructor
│   ├── train.py                      # Classifier Training & 5-Fold Stratified CV
│   ├── evaluate.py                   # Performance Metrics & Confusion Matrices
│   ├── matcher.py                    # Sentence-BERT Dense Semantic Matcher
│   └── roadmap.py                    # Learning Pathway & Curriculum Engine
├── backend/                          # FastAPI Microservice (Port 8001)
│   ├── main.py                       # App Runner, CORS, Lifespan Preloaders
│   ├── routers/                      # REST Endpoints (/parse, /classify, /screen)
│   └── services/                     # In-Memory Predictor & Database Services
├── models/                           # Serialized Artifacts (.pkl, metadata.json)
└── tests/                            # Automated Pytest Suite (195 Assertions)"""
    story.append(create_code_box(dir_tree, styles))
    story.append(Spacer(1, 6))

    story.append(Paragraph("The listing below illustrates the production implementation of context-guarded regular expression compilation in extractor.py, implementing the boundary rules of Algorithm 4.1:", p_body))
    code_extractor = """class CandidateIntelligenceEngine:
    def _build_skill_pattern(self, skill: str) -> re.Pattern:
        esc = re.escape(skill)
        # Single-letter languages: require boundary punctuation/whitespace
        if skill.lower() in {"c", "r"}:
            return re.compile(
                r"(?<=[\\s,;(\\[])" + esc + r"(?=[/\\s,;)\\]+]|$)(?!\\w)",
                re.IGNORECASE
            )
        # Ambiguous verbs & framework names
        elif skill.lower() in {"go", "rust", "spring", "dart", "solid", "less"}:
            return re.compile(
                r"(?i)(?:^|[\\n•|;:(\\[])\\s*" + esc + r"(?=\\s*(?:[,\\n•|;:)\\]]|$))"
            )
        # Architectural style: require RESTful or explicit API reference
        elif skill.lower() == "rest":
            return re.compile(r"(?i)\\b(?:RESTful|REST\\s+API|REST\\s+services)\\b")
        # Standard technical identifiers
        return re.compile(r"(?i)\\b" + esc + r"\\b")"""
    story.append(create_code_box(code_extractor, styles))
    story.append(Spacer(1, 6))

    story.append(Paragraph("The listing below implements the calendar interval union algebra in extractor.py, sorting employment timestamps and merging overlapping periods:", p_body))
    code_date = """def calculate_deduplicated_tenure(intervals: list[tuple[datetime, datetime]]) -> float:
    if not intervals:
        return 0.0
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_intervals[0]]
    for current_start, current_end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]
        if current_start <= last_end:
            # Overlapping or contiguous interval: merge
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            merged.append((current_start, current_end))
    total_months = sum((end.year - start.year) * 12 + (end.month - start.month)
                       for start, end in merged)
    return round(max(0.0, total_months / 12.0), 2)"""
    story.append(create_code_box(code_date, styles))
    story.append(Spacer(1, 6))

    story.append(Paragraph("The listing below extracts the dense 67-dimensional feature vector in feature_engineering.py:", p_body))
    code_feat = """def extract_dense_features(parsed_profile: dict) -> np.ndarray:
    features = np.zeros(67, dtype=np.float32)
    skills = parsed_profile.get("skills", [])
    total_skills = max(1, len(skills))
    # 0-19: Domain Skill Densities across 20 IT domains
    domain_counts = count_skills_per_domain(skills)
    for i, count in enumerate(domain_counts[:20]):
        features[i] = count / total_skills
    # 20-39: Domain Lexicon Salience
    for i, role in enumerate(CANONICAL_ROLES[:20]):
        req = ROLE_REQUIREMENTS[role]["required_skills"]
        features[20 + i] = len(set(skills).intersection(req)) / max(1, len(req))
    # 40-44: Experience Seniority Vectors
    tenure = parsed_profile.get("verified_tenure", {})
    features[40] = min(tenure.get("total_years", 0.0) / 10.0, 1.0)
    features[41] = min(tenure.get("it_years", 0.0) / 10.0, 1.0)
    features[42] = min(tenure.get("role_years", 0.0) / 10.0, 1.0)
    features[43] = 1.0 if tenure.get("total_years", 0.0) >= 5.0 else 0.0
    features[44] = 1.0 if tenure.get("total_years", 0.0) >= 2.0 else 0.0
    # 45-49: Educational Attainment
    edu = parsed_profile.get("education", {})
    features[45] = edu.get("tier_level", 50.0) / 100.0
    features[46] = edu.get("field_multiplier", 0.20)
    features[47] = 1.0 if edu.get("has_honors", False) else 0.0
    features[48] = 1.0 if edu.get("is_accredited", True) else 0.0
    features[49] = features[45] * features[46]
    return features"""
    story.append(create_code_box(code_feat, styles))
    story.append(Spacer(1, 6))

    # 5.3 Integration with the other components
    track('sec5_3')
    story.append(Paragraph("5.3 Integration with the other components", h_sec))
    story.append(Paragraph("Component 1 exposes four RESTful HTTP endpoints documented through OpenAPI 3.0. Table 5.1 details the API contracts.", p_body))
    story.append(Spacer(1, 4))

    track('tab5_1')
    story.append(Paragraph("Table 5.1: Component 1 microservice RESTful API specification (Port 8001).", caption_tab))
    api_data = [
        [Paragraph("<b>Route</b>", cell_bold), Paragraph("<b>Verb</b>", cell_bold), Paragraph("<b>Request Input Format</b>", cell_bold), Paragraph("<b>Response Output Payload</b>", cell_bold)],
        [Paragraph("/api/v1/cv/parse", cell), Paragraph("POST", cell), Paragraph("Multipart: PDF/DOCX file", cell), Paragraph("JSON: entities, skills, tenure, degrees", cell)],
        [Paragraph("/api/v1/cv/classify", cell), Paragraph("POST", cell), Paragraph("JSON: {text: string}", cell), Paragraph("JSON: primary role, top 4 softmax probabilities", cell)],
        [Paragraph("/api/v1/cv/screen", cell), Paragraph("POST", cell), Paragraph("Multipart: CV + target role/JD", cell), Paragraph("JSON: S_skill, S_exp, S_edu, S_cv, roadmap", cell)],
        [Paragraph("/api/v1/cv/roles", cell), Paragraph("GET", cell), Paragraph("None", cell), Paragraph("JSON: list of 20 canonical IT roles", cell)],
    ]
    api_tab = create_table_box(api_data, [95, 45, 125, 146], styles, is_header=True)
    story.append(api_tab)
    story.append(Spacer(1, 8))

    story.append(Paragraph("The emitted Tri-Pillar vector S_C1 = [S_skill, S_exp, S_edu] provides the primary input contract to Component 3 (Port 8003) for listwise candidate ranking, while the extracted candidate profile is streamed to Component 2 (Port 8002) for generating role-tailored technical interview questions.", p_body))

    # 5.4 Verification and software testing
    track('sec5_4')
    story.append(Paragraph("5.4 Verification and software testing", h_sec))
    story.append(Paragraph("The microservice is thoroughly validated by an automated test suite comprising 195 unit, regression, and integration tests. Table 5.2 summarizes the test suite distribution.", p_body))
    story.append(Spacer(1, 4))

    track('tab5_2')
    story.append(Paragraph("Table 5.2: Automated Pytest verification suite breakdown (195 passed tests).", caption_tab))
    test_data = [
        [Paragraph("<b>Test Module</b>", cell_bold), Paragraph("<b>Tests</b>", cell_bold), Paragraph("<b>Functional Scope &amp; Target Verification</b>", cell_bold), Paragraph("<b>Result</b>", cell_bold)],
        [Paragraph("test_api.py", cell), Paragraph("14", cell), Paragraph("FastAPI routing, multipart uploads, error handlers", cell), Paragraph("14/14 Pass", cell)],
        [Paragraph("test_candidate_intelligence_engine.py", cell), Paragraph("13", cell), Paragraph("Date parsing, concurrent employment deduplication", cell), Paragraph("13/13 Pass", cell)],
        [Paragraph("test_component1.py", cell), Paragraph("10", cell), Paragraph("PII redaction, layout extraction, ligature repair", cell), Paragraph("10/10 Pass", cell)],
        [Paragraph("test_extractor.py", cell), Paragraph("32", cell), Paragraph("Boundary-guarded regex patterns and token shielding", cell), Paragraph("32/32 Pass", cell)],
        [Paragraph("test_international_education.py", cell), Paragraph("51", cell), Paragraph("51 international degree frameworks (DUT, Licence, HND)", cell), Paragraph("51/51 Pass", cell)],
        [Paragraph("test_job_specific_scores.py", cell), Paragraph("4", cell), Paragraph("Target-role matching and domain requirement caps", cell), Paragraph("4/4 Pass", cell)],
        [Paragraph("test_matcher.py", cell), Paragraph("9", cell), Paragraph("Sentence-BERT cosine similarity bounds in [0, 1]", cell), Paragraph("9/9 Pass", cell)],
        [Paragraph("test_predictor.py", cell), Paragraph("10", cell), Paragraph("Softmax probability sums, fallback prediction handling", cell), Paragraph("10/10 Pass", cell)],
        [Paragraph("test_scorer.py", cell), Paragraph("52", cell), Paragraph("Tri-Pillar bounds across all 20 canonical IT roles", cell), Paragraph("52/52 Pass", cell)],
        [Paragraph("<b>Total Suite</b>", cell_bold), Paragraph("<b>195</b>", cell_bold), Paragraph("<b>Complete microservice end-to-end verification</b>", cell_bold), Paragraph("<b>100% (79.6s)</b>", cell_bold)],
    ]
    test_tab = create_table_box(test_data, [130, 40, 171, 70], styles, is_header=True)
    story.append(test_tab)
    story.append(Spacer(1, 8))

    # 5.5 Deployment and operation
    track('sec5_5')
    story.append(Paragraph("5.5 Deployment and operation", h_sec))
    story.append(Paragraph("Component 1 is deployed as a standalone Docker container running Python 3.12-slim on standard x86 CPU hardware. The image size is 340 MB, and runtime resident memory consumption remains under 350 MB RAM during continuous operation. With an end-to-end processing latency of 151.35 ms per resume, a single 4-core virtual machine processes approximately 1,600 resumes per hour. When orchestrated under Kubernetes with horizontal pod autoscalers (HPA), the service scales dynamically to process peak enterprise cohorts exceeding 50,000 resumes per day without GPU hardware requirements.", p_body))
    story.append(PageBreak())
