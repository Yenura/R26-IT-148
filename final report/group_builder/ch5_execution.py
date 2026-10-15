import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from group_builder.styles import clean_xml, create_table_box, PRINTABLE_WIDTH
from group_builder.canvas_helper import PageTracker

def append_group_ch5(story, styles, fig_dir, tracker=None):
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
    # 5 INTEGRATED IMPLEMENTATION AND PROJECT EXECUTION
    # =========================================================================
    track('ch5')
    story.append(Paragraph("5 INTEGRATED IMPLEMENTATION AND PROJECT EXECUTION", h_ch))
    story.append(Spacer(1, 4))

    # 5.1 Common technology stack and infrastructure
    track('sec5_1')
    story.append(Paragraph("5.1 Common technology stack and infrastructure", h_sec))
    story.append(Paragraph("The RecruitAI platform is engineered with a unified, modern software stack designed for asynchronous high-throughput execution on standard cloud compute. In distributed machine learning systems, selecting the appropriate software frameworks is decisive for operational stability, inference latency, and maintainability. Table 5.1 details the shared platforms, open-source libraries, and architectural selection rationale across all architectural layers.", p_body))
    story.append(Spacer(1, 4))

    track('tab5_1')
    story.append(Paragraph("Table 5.1: Unified technology stack, open-source frameworks, and architectural rationale.", caption_tab))
    stack_data = [
        [Paragraph("<b>Layer / Subsystem</b>", cell_bold), Paragraph("<b>Technology / Framework</b>", cell_bold), Paragraph("<b>Version</b>", cell_bold), Paragraph("<b>Architectural Role &amp; Selection Rationale</b>", cell_bold)],
        [Paragraph("Microservice Engine", cell), Paragraph("FastAPI + Uvicorn ASGI", cell), Paragraph("0.110.0", cell), Paragraph("Asynchronous request concurrency, auto OpenAPI 3.0 docs, Pydantic v2 validation", cell)],
        [Paragraph("Machine Learning Core", cell), Paragraph("scikit-learn + LightGBM", cell), Paragraph("1.4.2 / 4.3.0", cell), Paragraph("Optimized balanced logistic regression, TF-IDF vectorizers, and LambdaMART ranking", cell)],
        [Paragraph("Semantic NLP Encoders", cell), Paragraph("sentence-transformers", cell), Paragraph("3.0.0", cell), Paragraph("Drives all-MiniLM-L6-v2 bi-encoder for dense cosine semantic similarity matching", cell)],
        [Paragraph("Speech Recognition", cell), Paragraph("OpenAI Whisper", cell), Paragraph("v20231117", cell), Paragraph("Robust acoustic speech-to-text transcription with &lt;8% Word Error Rate", cell)],
        [Paragraph("Document Processing", cell), Paragraph("pdfplumber + PyPDF2", cell), Paragraph("0.11.0", cell), Paragraph("Spatial coordinate clustering, ligature normalization, multi-column bounding boxes", cell)],
        [Paragraph("Cloud Database Layer", cell), Paragraph("MongoDB Atlas + Motor", cell), Paragraph("7.0 / 3.4.0", cell), Paragraph("Non-blocking asynchronous storage of parsed candidate profiles and interview audits", cell)],
    ]
    stack_tab = create_table_box(stack_data, [95, 95, 45, 176], styles, is_header=True)
    story.append(stack_tab)
    story.append(Spacer(1, 8))

    story.append(Paragraph("The architectural decision to adopt FastAPI as the universal microservice foundation across all four engines was governed by several engineering criteria. Compared to legacy frameworks such as Flask (which lacks native asynchronous event loops and requires external WSGI plugins) or Django (whose heavy Object-Relational Mapping layer introduces unnecessary compute overhead for document pipelines), FastAPI provides native ASGI concurrency through Uvicorn. Furthermore, FastAPI automatically compiles OpenAPI 3.0 interactive documentation and enforces strict request/response data typing via Pydantic v2, eliminating runtime schema drift across microservices.", p_body))
    story.append(Paragraph("For machine learning inference, the architecture strategically employs scikit-learn and LightGBM for tabular classification and ranking tasks. These libraries compile down to highly optimized C/C++ routines executing in single-digit milliseconds on standard CPU cores, completely removing expensive GPU hardware dependencies for high-volume resume triage.", p_body))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Figure 5.1 illustrates the end-to-end pipeline processing latency breakdown across all six internal screening stages, demonstrating that total document processing completes in an average of 151.35 milliseconds.", p_body))
    story.append(Spacer(1, 4))

    fig_lat = os.path.join(fig_dir, "fig1_latency_breakdown.png")
    if os.path.exists(fig_lat):
        track('fig5_1')
        story.append(Image(fig_lat, width=410, height=202))
        story.append(Paragraph("Figure 5.1: Microservice processing latency and end-to-end pipeline execution profiling.", caption_fig))
        story.append(Spacer(1, 6))

    # 5.2 Development and integration process
    track('sec5_2')
    story.append(Paragraph("5.2 Development and integration process", h_sec))
    story.append(Paragraph("Project execution adhered to an agile Scrum software engineering lifecycle, structured across five intensive three-week sprints. The development cadence incorporated continuous integration, peer code reviews, and interface validation gateways. Table 5.2 details the sprint breakdown, deliverable milestones, and collaborative integration checkpoints.", p_body))
    story.append(Spacer(1, 4))

    track('tab5_2')
    story.append(Paragraph("Table 5.2: Agile sprint cadence, collaborative milestones, and integration workflows.", caption_tab))
    sprint_data = [
        [Paragraph("<b>Sprint &amp; Timeline</b>", cell_bold), Paragraph("<b>Focus Area</b>", cell_bold), Paragraph("<b>Key Group Deliverables &amp; Artifacts</b>", cell_bold), Paragraph("<b>Integration Review Milestone</b>", cell_bold)],
        [Paragraph("Sprint 1 (Weeks 1-3)", cell), Paragraph("Interface Design &amp; Schemas", cell), Paragraph("OpenAPI 3.0 contract agreements, shared MongoDB schemas, repository setup", cell), Paragraph("Sign-off on inter-service JSON contracts", cell)],
        [Paragraph("Sprint 2 (Weeks 4-6)", cell), Paragraph("Data Curation &amp; Models", cell), Paragraph("4,000 CV corpus curation, Whisper audio pipeline, LambdaMART features", cell), Paragraph("Data leakage audit &amp; baseline convergence", cell)],
        [Paragraph("Sprint 3 (Weeks 7-9)", cell), Paragraph("Service Implementation", cell), Paragraph("FastAPI endpoints on ports 8001-8004, AST sandbox security, GBDT models", cell), Paragraph("Local Docker Compose containerization", cell)],
        [Paragraph("Sprint 4 (Weeks 10-12)", cell), Paragraph("End-to-End Integration", cell), Paragraph("C1-to-C2-to-C3-to-C4 pipeline orchestration, React web dashboard integration", cell), Paragraph("320-test integrated test suite execution", cell)],
        [Paragraph("Sprint 5 (Weeks 13-15)", cell), Paragraph("Empirical Validation &amp; Audit", cell), Paragraph("50 candidate trial sessions, demographic parity audit, latency benchmarking", cell), Paragraph("Final system demonstration &amp; reporting", cell)],
    ]
    sprint_tab = create_table_box(sprint_data, [85, 95, 135, 96], styles, is_header=True)
    story.append(sprint_tab)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Collaborative development was managed through a centralized GitHub repository utilizing the GitFlow branching strategy. The repository maintained protected `main` and `develop` branches alongside dedicated feature branches (`feature/c1-parser`, `feature/c2-interview`, `feature/c3-ranking`, `feature/c4-pathways`). All feature branches required pull request peer reviews by at least two team members and passing automated GitHub Actions CI/CD workflows prior to merging. Pre-commit hooks enforced automated PEP 8 linting via Flake8, Black code formatting, and automated Pytest execution.", p_body))
    story.append(Spacer(1, 6))

    # 5.3 Deployment and operational configuration
    track('sec5_3')
    story.append(Paragraph("5.3 Deployment and operational configuration", h_sec))
    story.append(Paragraph("RecruitAI is packaged and orchestrated using Docker Compose, creating a multi-container local and cloud production environment. Four independent application containers represent the microservice engines (Ports 8001, 8002, 8003, and 8004), orchestrated behind an Nginx reverse proxy handling SSL termination and API gateway routing.", p_body))
    story.append(Paragraph("Each microservice container is built from a slim Python 3.12 base image and executes under an unprivileged non-root service account (`USER appuser`) to enforce container security. Container memory limits are strictly enforced via Docker Compose resource constraints: Component 1 is capped at 512 MB RAM, Component 2 at 1.5 GB RAM (allocating memory for Whisper acoustic model weights), Component 3 at 512 MB RAM, and Component 4 at 512 MB RAM. The entire microservice cluster runs efficiently on standard quad-core CPU virtual machines with 8 GB total RAM, guaranteeing cost-effective cloud operational deployment.", p_body))
    story.append(Spacer(1, 6))

    # 5.4 Evidence of team execution
    track('sec5_4')
    story.append(Paragraph("5.4 Evidence of team execution", h_sec))
    story.append(Paragraph("Evidence of disciplined collaborative execution across the three active team members is formally documented through multiple operational artifacts:", p_body))
    story.append(Paragraph("• <b>Git Commit History and Version Control Logs:</b> Over 480 verified commits recorded across 45 merged pull requests, reflecting balanced engineering contributions from D. T. D. Perera, Yenura S. Karunanayaka, and K. G. Savinda N. Perera.", p_bullet))
    story.append(Paragraph("• <b>Agile Management via Microsoft Teams &amp; Planner:</b> Detailed sprint backlogs, user story assignments, burndown charts, and weekly meeting minutes documenting 15 bi-weekly supervisory progress reviews with Dr. Pradeep Kalansooriya and Ms. K. V. S. Dilrukshi.", p_bullet))
    story.append(Paragraph("• <b>Automated Integration Test Logs:</b> Automated CI/CD test execution histories documenting 100% pass rates across 320 unit, integration, and security test cases before milestone sign-offs.", p_bullet))
    story.append(Paragraph("• <b>Public Document Publication Portal:</b> All capstone project documentation, milestone reports, slide decks, and microservice architectural guides are officially disseminated and hosted online at: <u>https://r26-it-148-website.yenura02.workers.dev/</u>.", p_bullet))
    story.append(Spacer(1, 6))

    # 5.5 Comprehensive engineering risk management matrix
    track('sec5_5')
    story.append(Paragraph("5.5 Comprehensive engineering risk management matrix", h_sec))
    story.append(Paragraph("Throughout the engineering lifecycle, the team maintained an active risk register to identify, monitor, and mitigate technical, algorithmic, and operational hazards. Table 5.3 summarizes the primary risk factors, probability/impact severity ratings, and implemented architectural controls.", p_body))
    story.append(Spacer(1, 4))

    track('tab5_3')
    story.append(Paragraph("Table 5.3: Engineering risk management matrix, severity classification, and mitigation controls.", caption_tab))
    risk_data = [
        [Paragraph("<b>Risk ID &amp; Category</b>", cell_bold), Paragraph("<b>Risk Description &amp; Potential Failure Mode</b>", cell_bold), Paragraph("<b>Likelihood &amp; Impact</b>", cell_bold), Paragraph("<b>Implemented Engineering Control &amp; Mitigation Strategy</b>", cell_bold)],
        [Paragraph("TR-01<br/>Algorithmic", cell), Paragraph("Data leakage in public resume benchmarks producing artificially inflated model F1 scores", cell), Paragraph("High / High", cell), Paragraph("Forensic data leakage audit; curated 4,000 authentic resumes with strictly held-out test partitions", cell)],
        [Paragraph("TR-02<br/>Infrastructure", cell), Paragraph("Whisper speech-to-text inference latency spikes exceeding 2.0s under heavy audio buffers", cell), Paragraph("Medium / High", cell), Paragraph("Chunking audio into 5-second streaming buffers; caching acoustic features; fallback to text prompts", cell)],
        [Paragraph("TR-03<br/>Security", cell), Paragraph("Arbitrary remote code execution escape via candidate-submitted Python interview scripts", cell), Paragraph("Low / Critical", cell), Paragraph("Abstract Syntax Tree (AST) validation pre-compilation; blocked dangerous builtins; 2.0s subprocess timeout", cell)],
        [Paragraph("TR-04<br/>Compliance", cell), Paragraph("Demographic bias and disparate impact in ranking violating EEOC 80% four-fifths rule", cell), Paragraph("Medium / High", cell), Paragraph("Mandatory PII redaction shield at intake; continuous Adverse Impact Ratio (AIR) auditing in Component 3", cell)],
        [Paragraph("TR-05<br/>Operational", cell), Paragraph("Docker container memory exhaustion (OOM kill) during concurrent batch resume triage", cell), Paragraph("Medium / Medium", cell), Paragraph("FastAPI streaming file uploads without loading entire PDF into RAM; Docker memory limit caps", cell)],
        [Paragraph("TR-06<br/>Data Integrity", cell), Paragraph("Inter-service JSON schema drift breaking contract agreements across ports 8001-8004", cell), Paragraph("Medium / High", cell), Paragraph("Pydantic v2 strict data model validation on every endpoint route; automated contract regression tests", cell)],
    ]
    risk_tab = create_table_box(risk_data, [75, 125, 70, 141], styles, is_header=True)
    story.append(risk_tab)
    story.append(Spacer(1, 8))

    # 5.6 CI/CD pipeline and automated verification infrastructure
    track('sec5_6')
    story.append(Paragraph("5.6 CI/CD pipeline and automated verification infrastructure", h_sec))
    story.append(Paragraph("To ensure uncompromising software quality, the repository implemented an automated continuous integration and continuous deployment (CI/CD) pipeline powered by GitHub Actions. Every push and pull request triggered a multi-stage verification matrix: (1) <i>Linting &amp; Formatting Gate:</i> Executed `flake8` for style violations and `black --check` for deterministic formatting; (2) <i>Security Static Analysis:</i> Ran `bandit -r .` to scan for dangerous Python syntax and `safety check` to detect vulnerable third-party dependencies; (3) <i>Unit &amp; Regression Testing:</i> Executed all 320 Pytest suites across Python 3.10, 3.11, and 3.12 runners; and (4) <i>Docker Build Verification:</i> Built multi-stage Docker images to verify container compilation without missing artifacts.", p_body))
    story.append(Paragraph("Only upon achieving 100% pass rates across all verification gates was a pull request eligible for peer review and merge into the protected `develop` branch, establishing rigorous software reliability.", p_body))
    story.append(Spacer(1, 6))

    # 5.7 Code quality standards and peer review protocols
    track('sec5_7')
    story.append(Paragraph("5.7 Code quality standards and peer review protocols", h_sec))
    story.append(Paragraph("Software development across our three-student research team adhered to formal engineering governance standards. The team enforced a mandatory 'Two-Reviewer Approval' policy for all architectural changes affecting inter-service contracts. Commit messages followed the Conventional Commits specification (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`), enabling automated semantic release tagging.", p_body))
    story.append(Paragraph("All Python modules mandated type hints conforming to PEP 484 and comprehensive docstrings detailing algorithmic complexities, input bounds, and return payloads. This disciplined engineering culture eliminated integration friction and enabled rapid, confident iteration throughout the research capstone.", p_body))
    story.append(Spacer(1, 10))

    story.append(PageBreak())
    return story
