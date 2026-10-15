import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from group_builder.styles import clean_xml, create_table_box, PRINTABLE_WIDTH
from group_builder.canvas_helper import PageTracker

def append_group_ch4(story, styles, fig_dir, tracker=None):
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
    # 4 COMPONENT INTEGRATION AND COHESIVE OPERATION
    # =========================================================================
    track('ch4')
    story.append(Paragraph("4 COMPONENT INTEGRATION AND COHESIVE OPERATION", h_ch))
    story.append(Spacer(1, 4))

    # 4.1 Integration strategy
    track('sec4_1')
    story.append(Paragraph("4.1 Integration strategy", h_sec))
    story.append(Paragraph("To guarantee architectural decoupling, fault containment, and independent scalability, RecruitAI adopted an <i>interface-first integration strategy</i>. In complex machine learning engineering projects, attempting to integrate isolated algorithms at the conclusion of development routinely introduces severe integration bottlenecks, schema mismatches, and data drift. To eliminate these hazards, our team formally defined OpenAPI 3.0 REST contracts, shared JSON schemas, and mutual error codes during Sprint 1 before any machine learning models were trained.", p_body))
    
    story.append(Paragraph("Rather than deploying a single monolithic Python backend, RecruitAI partitions the ecosystem into four autonomous microservices. Each microservice operates within its own dedicated Python virtual environment, bound to distinct TCP ports: Port 8001 for Component 1 (Resume Screening), Port 8002 for Component 2 (Interview Evaluation), Port 8003 for Component 3 (Suitability Ranking), and Port 8004 for Component 4 (Career Pathfinding). This microservice boundary ensures that heavy neural dependencies in Component 2 (such as PyTorch and OpenAI Whisper) do not consume memory or introduce GIL (Global Interpreter Lock) contention with high-throughput tabular inference in Components 1, 3, and 4.", p_body))
    
    story.append(Paragraph("Inter-service communication is orchestrated asynchronously over HTTP REST utilizing standard JSON interchange payloads. To maintain system reliability under intermittent network or service delays, each microservice incorporates non-blocking asynchronous request handlers powered by FastAPI and Uvicorn. Long-term candidate telemetry, parsed feature vectors, and interview session audits are persisted in a centralized MongoDB Atlas cloud document database, allowing asynchronous polling and event-driven updates across components.", p_body))
    story.append(Spacer(1, 6))

    # 4.2 Interfaces data contracts and shared models
    track('sec4_2')
    story.append(Paragraph("4.2 Interfaces data contracts and shared models", h_sec))
    story.append(Paragraph("Table 4.1 documents the primary inter-microservice RESTful endpoints, caller/callee bindings, and shared JSON payload structures that govern ecosystem interoperability.", p_body))
    story.append(Spacer(1, 4))

    track('tab4_1')
    story.append(Paragraph("Table 4.1: Inter-microservice REST API contracts and shared JSON data payloads.", caption_tab))
    contract_data = [
        [Paragraph("<b>Endpoint Route &amp; Method</b>", cell_bold), Paragraph("<b>Producer Service</b>", cell_bold), Paragraph("<b>Consumer Service</b>", cell_bold), Paragraph("<b>Shared Payload Attributes &amp; Data Contract</b>", cell_bold)],
        [Paragraph("POST /api/v1/cv/screen", cell), Paragraph("Component 1<br/>(Port 8001)", cell), Paragraph("Frontend / Orchestrator", cell), Paragraph("Emits Tri-Pillar vector: {S_skill, S_exp, S_edu}, verified_tenure, predicted_role, and extracted_skills list", cell)],
        [Paragraph("POST /api/v1/interview/start", cell), Paragraph("Component 2<br/>(Port 8002)", cell), Paragraph("Frontend / Orchestrator", cell), Paragraph("Consumes candidate profile from C1; emits role-aligned dynamic questions and assessment session ID", cell)],
        [Paragraph("POST /api/v1/rank/evaluate", cell), Paragraph("Component 3<br/>(Port 8003)", cell), Paragraph("Component 1 &amp;<br/>Component 2", cell), Paragraph("Consumes C1 Tri-Pillar vector and C2 interview metrics; emits composite CSS, prerequisite gating flags, and rank", cell)],
        [Paragraph("POST /api/v1/pathways/generate", cell), Paragraph("Component 4<br/>(Port 8004)", cell), Paragraph("Component 3<br/>(Port 8003)", cell), Paragraph("Consumes unshortlisted candidate skill gaps; emits 4-milestone learning roadmap, study hours, and DAG lattice", cell)],
    ]
    contract_tab = create_table_box(contract_data, [95, 75, 75, 166], styles, is_header=True)
    story.append(contract_tab)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Data integrity across service boundaries is enforced via Pydantic v2 data models. When Component 1 emits a candidate profile, the payload is validated against strict schema types: skills are serialized as normalized string sets, tenure as a non-negative float bounded by calendar dates, and scores as normalized real numbers in the interval [0.0, 100.0]. Any payload failing type constraints is immediately rejected with HTTP 422 Unprocessable Entity, preventing silent data corruption across downstream pipelines.", p_body))
    story.append(Spacer(1, 6))

    # 4.3 Shared nonfunctional requirements
    track('sec4_3')
    story.append(Paragraph("4.3 Shared nonfunctional requirements", h_sec))
    story.append(Paragraph("To guarantee enterprise-grade operational stability, the RecruitAI ecosystem enforces uniform non-functional requirements (NFRs) across all microservices. Table 4.2 details the shared operational metrics, quality attributes, and architectural verification methods.", p_body))
    story.append(Spacer(1, 4))

    track('tab4_2')
    story.append(Paragraph("Table 4.2: Shared non-functional requirements, operational metrics, and verification methods.", caption_tab))
    nfr_data = [
        [Paragraph("<b>Quality Attribute</b>", cell_bold), Paragraph("<b>Target Operational Metric</b>", cell_bold), Paragraph("<b>Architectural Implementation &amp; Verification Method</b>", cell_bold)],
        [Paragraph("Throughput &amp; Latency", cell), Paragraph("CV screen &lt;200 ms; Interview latency &lt;1.5 s", cell), Paragraph("Sublinear TF-IDF + Logistic Regression (2.4 ms inference); SBERT bi-encoder caching", cell)],
        [Paragraph("Data Privacy &amp; Ethics", cell), Paragraph("100% PII stripping on intake", cell), Paragraph("Automated regex sanitization blinding names, emails, phones, and physical addresses", cell)],
        [Paragraph("Reliability &amp; Uptime", cell), Paragraph("99.9% availability during batch runs", cell), Paragraph("Stateless container design; automatic Kubernetes pod restarts; MongoDB connection pooling", cell)],
        [Paragraph("Explainability", cell), Paragraph("Zero black-box ranking decisions", cell), Paragraph("Closed-form SHAP attributions in C1; MAUT utility scoring in C3; SHAP tree explainers in C4", cell)],
        [Paragraph("Security Standards", cell), Paragraph("Zero remote code execution escapes", cell), Paragraph("AST-secured Python execution sandbox restricting OS system calls and networking", cell)],
    ]
    nfr_tab = create_table_box(nfr_data, [85, 110, 216], styles, is_header=True)
    story.append(nfr_tab)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Latency budgeting is strictly managed across the pipeline: Component 1 is allocated a maximum processing budget of 200 ms for document extraction and scoring; Component 2 is allocated 1,500 ms for speech transcription and rubric cosine grading; Component 3 executes listwise ranking in under 50 ms; and Component 4 constructs Dijkstra DAG pathways in under 100 ms. Consequently, total end-to-end processing across the four services completes comfortably within the target threshold of 2.5 seconds per candidate.", p_body))
    story.append(Spacer(1, 6))

    # 4.4 Integrated workflow and exception handling
    track('sec4_4')
    story.append(Paragraph("4.4 Integrated workflow and exception handling", h_sec))
    story.append(Paragraph("Robust distributed architectures require comprehensive exception handling and automated fallback mechanisms to manage network partitions, malformed user inputs, and unexpected compute failures. RecruitAI implements standardized error handling across all four microservices:", p_body))
    
    story.append(Paragraph("• <b>Malformed Document Ingestion Handling:</b> If an applicant uploads a corrupted binary file, password-protected PDF, or unparseable scanned raster image, Component 1 intercepts the extraction error, prevents worker crash, and returns HTTP 422 with a structured error payload advising the candidate to upload a valid text-based PDF or DOCX file.", p_bullet))
    story.append(Paragraph("• <b>Audio Stream Loss and Transcription Degradation:</b> During Component 2 technical interviews, if packet loss or microphone disconnects degrade audio streams, the Whisper worker logs the acoustic failure and initiates an automated graceful degradation protocol. The web dashboard prompts the candidate with text-based fallback input, ensuring that the interview session proceeds without disqualifying the applicant due to transient hardware faults.", p_bullet))
    story.append(Paragraph("• <b>Adversarial Code Injection Containment:</b> When candidate code submissions are evaluated in Component 2, the Abstract Syntax Tree (AST) analyzer intercepts dangerous syntax nodes (`os.system`, `subprocess.Popen`, `socket`, `eval`, `open`) prior to compilation. Sub-processes are isolated in a restricted execution namespace with rigid 2.0-second timeout limits and 128 MB memory quotas, eliminating remote code execution vulnerabilities.", p_bullet))
    story.append(Paragraph("• <b>Circuit Breaker and Service Isolation:</b> Inter-service HTTP requests between Component 3 and upstream services employ exponential backoff retries with circuit breaker thresholds. If Component 2 is temporarily unreachable, Component 3 calculates preliminary candidate suitability using S_CV alone, flagging the interview status as pending rather than aborting the pipeline.", p_bullet))
    story.append(Spacer(1, 6))

    # 4.5 Team contribution and dependency matrix
    track('sec4_5')
    story.append(Paragraph("4.5 Team contribution and dependency matrix", h_sec))
    story.append(Paragraph("The successful realization of RecruitAI is the result of structured collaborative software engineering executed across our three-student research team. Table 4.3 delineates the transparent distribution of research responsibilities, component leadership, and technical dependencies.", p_body))
    story.append(Spacer(1, 4))

    track('tab4_3')
    story.append(Paragraph("Table 4.3: Team responsibility, component allocation, and cross-service dependency matrix.", caption_tab))
    team_data = [
        [Paragraph("<b>Student Name &amp; ID</b>", cell_bold), Paragraph("<b>Component Allocation</b>", cell_bold), Paragraph("<b>Primary Development &amp; Research Tasks</b>", cell_bold), Paragraph("<b>Cross-Service Dependencies</b>", cell_bold)],
        [Paragraph("D. T. D. Perera<br/>(IT22089236)", cell), Paragraph("Component 1<br/>(Port 8001)", cell), Paragraph("PDF/DOCX ingestion, PII redaction, 400+ NER taxonomy, interval algebra, 20-role balanced logistic regression", cell), Paragraph("Feeds candidate profile to C2; feeds Tri-Pillar vector to C3; feeds skill gaps to C4", cell)],
        [Paragraph("Yenura S. Karunanayaka<br/>(IT22306272)", cell), Paragraph("Component 2<br/>(Port 8002)", cell), Paragraph("Dynamic question retrieval, Whisper STT integration, SBERT semantic grading rubric, AST Python code sandbox", cell), Paragraph("Consumes profile from C1; delivers interview metrics (S_concept, S_code) to C3", cell)],
        [Paragraph("K. G. Savinda N. Perera<br/>(IT22027610)", cell), Paragraph("Component 3 &amp;<br/>Component 4<br/>(Ports 8003 &amp; 8004)", cell), Paragraph("MAUT suitability scoring, soft prerequisite gating, LambdaMART ranking, 67-feature GBDT hireability, DAG lattice", cell), Paragraph("Fuses C1 and C2 into ranked list; routes unshortlisted profiles to C4 roadmaps", cell)],
    ]
    team_tab = create_table_box(team_data, [95, 75, 125, 116], styles, is_header=True)
    story.append(team_tab)
    story.append(Spacer(1, 8))

    # 4.6 Database architecture and distributed document schemas
    track('sec4_6')
    story.append(Paragraph("4.6 Database architecture and distributed document schemas", h_sec))
    story.append(Paragraph("The persistence tier is architected around MongoDB Atlas, utilizing asynchronous non-blocking drivers (Motor) to handle high-concurrency read/write operations without I/O blocking. Data is structured into four primary collections designed to isolate concerns while supporting atomic queries across recruitment lifecycles. Table 4.4 details the collections, schemas, and indexing strategies.", p_body))
    story.append(Spacer(1, 4))

    track('tab4_4')
    story.append(Paragraph("Table 4.4: MongoDB Atlas collections, document schemas, and indexing strategies.", caption_tab))
    db_data = [
        [Paragraph("<b>Collection Name</b>", cell_bold), Paragraph("<b>Primary Key &amp; Indexes</b>", cell_bold), Paragraph("<b>Core Stored Document Fields</b>", cell_bold), Paragraph("<b>TTL &amp; Retention Policy</b>", cell_bold)],
        [Paragraph("candidates", cell), Paragraph("candidate_id (UUID, Unique);<br/>Index: target_role", cell), Paragraph("pii_sanitized_profile, extracted_skills, tenure_years, tri_pillar_vector, intake_timestamp", cell), Paragraph("Permanent; GDPR self-service deletion on demand", cell)],
        [Paragraph("interviews", cell), Paragraph("session_id (UUID, Unique);<br/>Compound: candidate_id + role", cell), Paragraph("transcripts, wer_telemetry, sbert_rubric_scores, ast_sandbox_results, code_exit_code", cell), Paragraph("Raw audio blobs deleted after 7 days; JSON results retained", cell)],
        [Paragraph("rankings", cell), Paragraph("requisition_id (UUID);<br/>Index: css_score (Descending)", cell), Paragraph("candidate_id, maut_composite_css, gating_passed, rank_position, ndcg_audit_vector", cell), Paragraph("Archived after requisition closure (90 days)", cell)],
        [Paragraph("learning_paths", cell), Paragraph("pathway_id (UUID);<br/>Index: candidate_id", cell), Paragraph("gap_skills, baseline_p_hire, projected_p_hire, milestone_nodes, documentation_links", cell), Paragraph("Retained for 180 days to support active applicant study", cell)],
    ]
    db_tab = create_table_box(db_data, [85, 95, 140, 91], styles, is_header=True)
    story.append(db_tab)
    story.append(Spacer(1, 8))

    # 4.7 Inter-service telemetry and distributed tracing
    track('sec4_7')
    story.append(Paragraph("4.7 Inter-service telemetry and distributed tracing", h_sec))
    story.append(Paragraph("To ensure full operational visibility across the distributed microservice cluster, RecruitAI implements end-to-end distributed tracing. When a candidate submits an intake request, the API Gateway generates a unique correlation identifier: `X-Correlation-ID: TRACE-{UUID}`. This token is propagated across all downstream HTTP headers between Ports 8001, 8002, 8003, and 8004. Structured JSON log events record execution latency, memory usage, and model prediction metadata tagged with the correlation ID, allowing engineers to trace a candidate's complete multi-stage evaluation across services in real time.", p_body))
    story.append(Paragraph("Each microservice exposes standardized `/healthz` liveness probes and `/metrics` telemetry endpoints scraped by Prometheus. Health checks verify database connectivity, memory threshold limits, and model artifact availability, enabling automated container self-healing and alert dispatching under operational anomalies.", p_body))
    story.append(Spacer(1, 6))

    # 4.8 Multi-container Docker orchestration and deployment topology
    track('sec4_8')
    story.append(Paragraph("4.8 Multi-container Docker orchestration and deployment topology", h_sec))
    story.append(Paragraph("The platform is containerized using Docker Compose, establishing an isolated multi-container bridge network (`recruitai-net`). The deployment configuration comprises seven coordinated containers: (1) `c1-screening-svc` (Port 8001), (2) `c2-interview-svc` (Port 8002), (3) `c3-ranking-svc` (Port 8003), (4) `c4-pathways-svc` (Port 8004), (5) `mongo-cluster` (Port 27017), (6) `redis-cache` (Port 6379, handling audio streaming message queues), and (7) `nginx-gateway` (Port 80/443, handling SSL termination, rate limiting, and CORS routing).", p_body))
    story.append(Paragraph("Container resource allocations enforce strict isolation: Component 2 is granted access to host GPU devices (if available) or 4 CPU cores with 2 GB RAM for Whisper inference, while Components 1, 3, and 4 operate under lightweight quotas of 1 CPU core and 512 MB RAM each. This containerized design guarantees zero dependency conflicts and enables rapid one-command deployment (`docker-compose up -d`) across local developer workstations and enterprise cloud virtual machines.", p_body))
    story.append(Spacer(1, 6))

    # 4.9 Distributed resilience patterns circuit breaking and idempotency
    track('sec4_9')
    story.append(Paragraph("4.9 Distributed resilience patterns circuit breaking and idempotency", h_sec))
    story.append(Paragraph("To protect the ecosystem against cascading failures in high-volume production deployments, RecruitAI incorporates enterprise distributed resiliency patterns across inter-service calls:", p_body))
    story.append(Paragraph("<b>1. Circuit Breaker Implementation:</b> HTTP calls between Component 3 and upstream services (Components 1 and 2) are wrapped in stateful circuit breaker proxies. If a service experiences a 50% failure rate over a rolling 20-request window, the breaker trips to 'Open' status, failing fast and executing local fallback heuristics (such as ranking based on available CV vectors alone) while allowing the failing upstream microservice a 30-second cooldown period before entering 'Half-Open' canary probing.", p_body))
    story.append(Paragraph("<b>2. Idempotency Key Semantics:</b> To guard against duplicate submissions caused by mobile browser reconnections or network jitter, every candidate submission carries a client-generated UUID header: `X-Idempotency-Key: {UUID}`. FastAPI interceptors query Redis caches; if an operation with the identical token was processed within the preceding 120 seconds, the cached response payload is returned immediately without re-executing expensive machine learning inferences.", p_body))
    story.append(Paragraph("<b>3. Dead-Letter Queue (DLQ) Auditing:</b> Corrupted audio packets or malformed candidate payloads that trigger unhandled extraction errors are automatically shunted into a Redis-backed Dead-Letter Queue. System administrators receive automated alerts with full stack traces, ensuring that data pipeline faults are isolated and debugged without degrading active candidate interview sessions.", p_body))
    story.append(Spacer(1, 10))

    story.append(PageBreak())
    return story
