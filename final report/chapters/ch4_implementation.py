import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_ch4(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker=None):
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
        story.append(PageTracker('ch4', tracker))

    # CHAPTER 4 HEADER
    story.append(p("CHAPTER 4", ch_num_style))
    story.append(p("IMPLEMENTATION DETAILS AND SOFTWARE ENGINEERING", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))

    # 4.1 MICROSERVICE ARCHITECTURE & TECH STACK
    if tracker is not None:
        story.append(PageTracker('sec4_1', tracker))
    story.append(p("4.1 Microservice Architecture and Technology Stack", h1_style))
    story.append(p("Component 1 is implemented as an asynchronous microservice in Python 3.12 using the FastAPI framework. The service runs as an independent component on dedicated TCP Port 8001, providing non-blocking RESTful endpoints managed by Uvicorn ASGI workers. Key architectural choices in the software stack include:"))
    story.append(b("• <b>FastAPI &amp; Pydantic v2:</b> Enforces strict request validation, type safety, automatic JSON serialization, and OpenAPI 3.0 schema generation for all document upload and screening endpoints."))
    story.append(b("• <b>scikit-learn 1.4.2:</b> Provides optimized implementations of Multinomial Logistic Regression, TF-IDF vectorization, Stratified K-Fold cross-validation, and classification metrics."))
    story.append(b("• <b>sentence-transformers 3.0:</b> Drives the all-MiniLM-L6-v2 bi-encoder model, computing 384-dimensional dense semantic document embeddings in memory."))
    story.append(b("• <b>pdfplumber &amp; PyPDF2:</b> Extracts raw character coordinates, spatial bounding box geometries, and font metrics from complex multi-column PDF resumes."))
    story.append(b("• <b>MongoDB Atlas &amp; Motor:</b> Asynchronous document store for persisting parsed candidate JSON structures, extracted feature vectors, and evaluation scores."))

    # 4.2 MODULAR DIRECTORY DECOMPOSITION
    if tracker is not None:
        story.append(PageTracker('sec4_2', tracker))
    story.append(p("4.2 Modular Directory Decomposition", h1_style))
    story.append(p("The codebase is structured into modular packages adhering to clear separation of concerns:"))

    dir_box = """component1/
├── ml/                               # Machine Learning & NLP Core
│   ├── extractor.py                  # CandidateIntelligenceEngine (83 KB, 1,850 LOC)
│   ├── skills.py                     # Canonical 400+ Skill Taxonomy & Regex Patterns
│   ├── lexicon.py                    # 20 Canonical IT Roles & Requirement Matrices
│   ├── feature_engineering.py        # Dense 67-Feature Matrix Constructor
│   ├── train.py                      # Classifier Training & 5-Fold Stratified CV
│   ├── evaluate.py                   # Performance Metrics & Confusion Matrices
│   ├── matcher.py                    # Sentence-BERT Dense Semantic Cosine Matcher
│   └── roadmap.py                    # Backend Learning Pathway & Syllabus Engine
├── backend/                          # FastAPI Microservice (Port 8001)
│   ├── main.py                       # ASGI App Runner, CORS, Lifespan Preloaders
│   ├── routers/                      # REST Endpoints (/parse, /classify, /screen)
│   └── services/                     # In-Memory Predictor & Database Services
├── models/                           # Serialized Artifacts (.pkl, metadata.json)
├── results/                          # Confusion Matrices, Classification Reports
└── tests/                            # Pytest Automated Test Suite (195 Assertions)"""
    story.append(make_box(dir_box))
    story.append(sp(6))

    # 4.3 PRODUCTION IMPLEMENTATION IN EXTRACTOR.PY
    if tracker is not None:
        story.append(PageTracker('sec4_3', tracker))
    story.append(p("4.3 Token Shielding RegEx Lookahead Mechanics in extractor.py", h1_style))
    story.append(p("The core extraction logic resides in the CandidateIntelligenceEngine class in component1/ml/extractor.py. The following code excerpt demonstrates how context-guarded look-around assertion patterns are compiled:"))

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
    story.append(make_box(code_extractor))
    story.append(sp(6))

    # 4.4 DATE ARITHMETIC & CALENDAR MATH ENGINE
    if tracker is not None:
        story.append(PageTracker('sec4_4', tracker))
    story.append(p("4.4 Date Arithmetic and Calendar Math Engine", h1_style))
    story.append(p("The temporal algebra engine extracts date tokens using a multi-pattern parser, converts calendar month strings into numeric month timestamps, sorts intervals chronologically, and calculates the disjoint interval union:"))

    code_date = """def calculate_deduplicated_tenure(intervals: list[tuple[datetime, datetime]]) -> float:
    if not intervals:
        return 0.0
    # Sort intervals by start timestamp
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_intervals[0]]
    for current_start, current_end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]
        if current_start <= last_end:
            # Overlapping or contiguous interval: merge
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            merged.append((current_start, current_end))
    # Sum deduplicated elapsed calendar months
    total_months = sum((end.year - start.year) * 12 + (end.month - start.month) 
                       for start, end in merged)
    return round(max(0.0, total_months / 12.0), 2)"""
    story.append(make_box(code_date))
    story.append(sp(6))

    # 4.5 FEATURE ENGINEERING IMPLEMENTATION
    story.append(p("4.5 Dense Feature Vector Extraction in feature_engineering.py", h1_style))
    story.append(p("The following production code listing illustrates the construction of the 67 normalized dense NLP features in component1/ml/feature_engineering.py:"))

    code_feat = """def extract_dense_features(parsed_profile: dict) -> np.ndarray:
    features = np.zeros(67, dtype=np.float32)
    skills = parsed_profile.get("skills", [])
    total_skills = max(1, len(skills))
    
    # 0-19: Domain Skill Densities across 20 IT domains
    domain_counts = count_skills_per_domain(skills)
    for i, count in enumerate(domain_counts[:20]):
        features[i] = count / total_skills
        
    # 20-39: Domain Lexicon Cosine Overlaps
    for i, role in enumerate(CANONICAL_ROLES[:20]):
        req_skills = ROLE_REQUIREMENTS[role]["required_skills"]
        overlap = len(set(skills).intersection(req_skills))
        features[20 + i] = overlap / max(1, len(req_skills))
        
    # 40-44: Experience Seniority Vectors
    tenure = parsed_profile.get("verified_tenure", {})
    features[40] = min(tenure.get("total_years", 0.0) / 10.0, 1.0)
    features[41] = min(tenure.get("it_years", 0.0) / 10.0, 1.0)
    features[42] = min(tenure.get("role_years", 0.0) / 10.0, 1.0)
    features[43] = 1.0 if tenure.get("total_years", 0.0) >= 5.0 else 0.0 # Senior flag
    features[44] = 1.0 if tenure.get("total_years", 0.0) >= 2.0 else 0.0 # Mid flag
    
    # 45-49: Educational Attainment
    edu = parsed_profile.get("education", {})
    features[45] = edu.get("tier_level", 50.0) / 100.0
    features[46] = edu.get("field_multiplier", 0.20)
    features[47] = 1.0 if edu.get("has_honors", False) else 0.0
    features[48] = 1.0 if edu.get("is_accredited", True) else 0.0
    features[49] = (features[45] * features[46]) # S_edu normalized
    
    # 50-54: Professional Certifications
    certs = parsed_profile.get("certifications", [])
    features[50] = min(len(certs) / 5.0, 1.0)
    features[51] = 1.0 if any("aws" in c.lower() for c in certs) else 0.0
    features[52] = 1.0 if any("security" in c.lower() or "cissp" in c.lower() for c in certs) else 0.0
    features[53] = 1.0 if any("pmp" in c.lower() or "agile" in c.lower() for c in certs) else 0.0
    features[54] = 1.0 if any("google" in c.lower() or "gcp" in c.lower() for c in certs) else 0.0
    
    # 55-66: Text Structure & Syntactic Metrics
    features[55] = min(len(parsed_profile.get("raw_text", "").split()) / 1000.0, 2.0)
    # Remaining layout metrics (bullet counts, action verbs, section completeness)
    return features"""
    story.append(make_box(code_feat))
    story.append(sp(6))

    # 4.6 MONGODB DOCUMENT MODELING & SCHEMAS
    if tracker is not None:
        story.append(PageTracker('sec4_6', tracker))
    story.append(p("4.6 MongoDB Document Modeling and Schemas", h1_style))
    story.append(p("Parsed resumes and candidate evaluations are stored in MongoDB Atlas using Pydantic document schemas. The CandidateEvaluationDocument schema captures the uncollapsed profile:"))

    code_schema = """class CandidateEvaluationDocument(BaseModel):
    candidate_id: str = Field(..., description="Unique anonymized candidate ID")
    sanitized_text: str = Field(..., description="PII-redacted clean resume text")
    predicted_role: str = Field(..., description="Primary classified IT role")
    role_confidence: float = Field(..., ge=0.0, le=1.0)
    alternative_roles: list[dict[str, float]] = Field(default_factory=list)
    tri_pillar_scores: TriPillarScoreModel
    verified_tenure: VerifiedTenureModel
    extracted_entities: ExtractedEntitiesModel
    created_at: datetime = Field(default_factory=datetime.utcnow)"""
    story.append(make_box(code_schema))
    story.append(sp(6))

    # 4.7 RESTFUL API SPECIFICATION
    if tracker is not None:
        story.append(PageTracker('sec4_7', tracker))
    story.append(p("4.7 RESTful API Specification (Port 8001)", h1_style))
    story.append(p("Component 1 provides four production HTTP endpoints documented via OpenAPI 3.0. Table 4.1 summarizes the endpoint specifications:"))

    api_table_data = [
        [p("<b>Endpoint Route</b>", body_style), p("<b>HTTP Verb</b>", body_style), p("<b>Input Contract</b>", body_style), p("<b>Output Contract / Response</b>", body_style)],
        [p("`/api/v1/cv/parse`", body_style), p("POST", body_style), p("Multipart form-data: PDF/DOCX file", body_style), p("Structured JSON: extracted entities, skills, tenure, degrees.", body_style)],
        [p("`/api/v1/cv/classify`", body_style), p("POST", body_style), p("JSON: `{text: string}`", body_style), p("JSON: predicted primary role + top 4 softmax probabilities.", body_style)],
        [p("`/api/v1/cv/screen`", body_style), p("POST", body_style), p("Multipart: CV file + target role / JD", body_style), p("Full evaluation: S_skill, S_exp, S_edu, S_cv, roadmap.", body_style)],
        [p("`/api/v1/cv/roles`", body_style), p("GET", body_style), p("None (Public schema)", body_style), p("JSON list of all 20 canonical supported IT roles.", body_style)]
    ]
    api_table = Table(api_table_data, colWidths=[110, 52, 145, 180])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(api_table)
    story.append(p("Table 4.1: Component 1 Microservice RESTful API Endpoints &amp; Request Contracts (Port 8001).", caption_style))
    story.append(sp(6))

    # 4.8 AUTOMATED PYTEST SUITE
    if tracker is not None:
        story.append(PageTracker('sec4_8', tracker))
    story.append(p("4.8 Automated Pytest Verification Suite (195 Tests)", h1_style))
    story.append(p("Software stability and mathematical invariance are validated through an automated Pytest test suite containing 195 unit, regression, and integration test assertions. Table 4.2 presents the test coverage breakdown:"))

    test_table_data = [
        [p("<b>Test Module Name</b>", body_style), p("<b>Assertions</b>", body_style), p("<b>Scope of Verification</b>", body_style), p("<b>Pass Rate</b>", body_bold)],
        [p("`test_api.py`", body_style), p("14", body_style), p("FastAPI routes, multipart uploads, error handlers", body_style), p("100% (14/14)", body_bold)],
        [p("`test_candidate_intelligence_engine.py`", body_style), p("13", body_style), p("Date parsing, concurrent overlap deduplication", body_style), p("100% (13/13)", body_bold)],
        [p("`test_component1.py`", body_style), p("10", body_style), p("PII sanitization, layout extraction, ligature repair", body_style), p("100% (10/10)", body_bold)],
        [p("`test_extractor.py`", body_style), p("32", body_style), p("Boundary-guarded regex shields, token collisions", body_style), p("100% (32/32)", body_bold)],
        [p("`test_international_education.py`", body_style), p("51", body_style), p("51 international degrees (DUT, Licence, Laurea, etc.)", body_style), p("100% (51/51)", body_bold)],
        [p("`test_job_specific_scores.py`", body_style), p("4", body_style), p("Target role matching, domain requirement caps", body_style), p("100% (4/4)", body_bold)],
        [p("`test_matcher.py`", body_style), p("9", body_style), p("SBERT cosine similarity bounds [0.0, 1.0]", body_style), p("100% (9/9)", body_bold)],
        [p("`test_predictor.py`", body_style), p("10", body_style), p("Softmax sum validation (sum p_i = 1.0), fallbacks", body_style), p("100% (10/10)", body_bold)],
        [p("`test_scorer.py`", body_style), p("52", body_style), p("Mathematical bounds for S_skill, S_exp, S_edu across 20 roles", body_style), p("100% (52/52)", body_bold)],
        [p("<b>TOTAL SUITE SUMMARY</b>", body_bold), p("<b>195</b>", body_bold), p("<b>Full End-to-End Microservice Verification</b>", body_bold), p("<b>100% (79.60s)</b>", body_bold)]
    ]
    test_table = Table(test_table_data, colWidths=[160, 48, 209, 70])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(test_table)
    story.append(p("Table 4.2: Automated Pytest Unit &amp; Integration Test Coverage Breakdown (195 Tests Passed in 79.60s).", caption_style))
    story.append(sp(6))

    # 4.9 MATCHER IMPLEMENTATION
    if tracker is not None:
        story.append(PageTracker('sec4_9', tracker))
    story.append(p("4.9 Dense Semantic Matching Implementation in matcher.py", h1_style))
    story.append(p("The dense semantic matcher in component1/ml/matcher.py maps resume summaries and job requisitions into 384-dimensional vector spaces to compute cosine similarity:"))

    code_matcher = """class CandidateSimilarityMatcher:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self._embedding_cache = {}

    def compute_similarity(self, resume_summary: str, jd_text: str) -> float:
        if not resume_summary.strip() or not jd_text.strip():
            return 0.0
        # Compute dense embeddings with L2 normalization
        u = self.model.encode(resume_summary, normalize_embeddings=True)
        v = self.model.encode(jd_text, normalize_embeddings=True)
        # Dot product of normalized vectors equals cosine similarity
        cosine_sim = float(np.dot(u, v))
        # Bound similarity into [0.0, 1.0] range
        return round(max(0.0, min(1.0, cosine_sim)), 4)"""
    story.append(make_box(code_matcher))
    story.append(sp(6))

    # 4.10 ROADMAP ENGINE IMPLEMENTATION
    if tracker is not None:
        story.append(PageTracker('sec4_10', tracker))
    story.append(p("4.10 Structured Curriculum Engine in roadmap.py", h1_style))
    story.append(p("The backend learning roadmap engine groups missing candidate skills into structured developmental milestones:"))

    code_roadmap = """class StructuredCurriculumEngine:
    def generate_roadmap(self, missing_skills: list[str], target_role: str) -> dict:
        curriculum = {
            "Milestone 1: Foundations & Core Languages": [],
            "Milestone 2: Frameworks & Architectural Libraries": [],
            "Milestone 3: Cloud, Persistence & DevOps": [],
            "Milestone 4: Capstone Engineering Project": []
        }
        total_hours = 0
        for skill in missing_skills:
            info = SKILL_ONTOLOGY.get(skill.lower(), {"tier": 2, "hours": 20, "docs": ""})
            tier_name = self._map_tier_to_name(info["tier"])
            item = {
                "skill": skill,
                "estimated_study_hours": info["hours"],
                "official_documentation": info["docs"],
                "recommended_project": self._suggest_mini_project(skill, target_role)
            }
            curriculum[tier_name].append(item)
            total_hours += info["hours"]
        return {"curriculum": curriculum, "total_estimated_hours": total_hours}"""
    story.append(make_box(code_roadmap))
    story.append(PageBreak())
