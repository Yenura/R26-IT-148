import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_group_ch5(story, styles, p, b, sp, make_box, caption_style, fig_dir):
    PRIMARY = colors.HexColor("#1A365D")
    SECONDARY = colors.HexColor("#2B6CB0")
    DARK_TEXT = colors.HexColor("#2D3748")

    ch_num_style = styles['ChapterNumber']
    ch_title_style = styles['ChapterTitle']
    h1_style = styles['Heading1_Custom']
    h2_style = styles['Heading2_Custom']
    body_style = styles['Body_Custom']
    body_bold = styles['Body_Bold']

    story.append(p("CHAPTER 5", ch_num_style))
    story.append(p("IMPLEMENTATION, ENGINEERING STACK, AND DEPLOYMENT", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    story.append(p("5.1 Integrated Technology Stack and Production Environment", h1_style))
    story.append(p("The RecruitAI platform is engineered using modern, open-source enterprise frameworks in Python 3.12 and JavaScript (ECMAScript 2022). The software engineering stack is partitioned into specialized operational layers:"))
    story.append(b("• <b>Backend Microservice Framework:</b> FastAPI (ASGI asynchronous runtime powered by Uvicorn) across all four backend engines, chosen for its sub-millisecond serialization overhead, automatic OpenAPI 3.0 documentation generation, and strict Pydantic v2 data validation."))
    story.append(b("• <b>Machine Learning &amp; NLP Foundations:</b> Scikit-Learn 1.4 for TF-IDF vectorization and Logistic Regression; LightGBM 4.3 for LambdaMART and GBDT ensembles; HuggingFace Transformers and Sentence-Transformers (`all-mpnet-base-v2`) for dense semantic embeddings; OpenAI Whisper for speech acoustic transcription."))
    story.append(b("• <b>Document Processing Engine:</b> `pdfplumber` for layout-aware bounding-box line extraction; `python-docx` for XML document traversal; regular expressions with look-around assertions for entity shielding."))
    story.append(b("• <b>Persistence Infrastructure:</b> MongoDB Atlas (version 7.0) with Motor asynchronous driver and PyMongo, indexing collections on candidate IDs, session UUIDs, and job role codes."))
    story.append(b("• <b>Web Client:</b> React 18, Vite bundling engine, TailwindCSS, Lucide React iconography, and Axios HTTP clients with automatic bearer token injection."))

    story.append(p("5.2 Microservice Port Topologies and Physical Directory Structure", h1_style))
    story.append(p("Each component functions as a self-contained microservice with independent dependency manifests, configuration settings, and test suites:"))
    
    dir_tree = """R26-IT-148/
├── recruit-ai/            # Port 8000: Gateway Microservice & Auth Orchestrator
├── component1/            # Port 8001: Resume Screening & Role Classifier (D. T. D. Perera)
│   ├── src/               # extractor.py, feature_engineering.py, matcher.py, roadmap.py
│   ├── models/            # cv_classifier.pkl (Balanced LogReg), tfidf_vectorizer.pkl
│   └── tests/             # 195 Pytest Unit & Integration Assertions
├── component2/            # Port 8002: Multi-Modal Technical Interview System (Dulnith K. D.)
│   ├── backend/           # interview_router.py, sbert_evaluator.py, whisper_stt.py
│   └── sandbox/           # ast_guard.py, execution_sandbox.py (Subprocess Jail)
├── component3/            # Port 8003: Candidate Ranking & CSS Engine (K. G. Savinda N. Perera)
│   ├── engine/            # css_calculator.py, lambdamart_ranker.py, shap_explainer.py
│   └── audits/            # fair_evaluator.py (Demographic Parity & 80% Rule Audits)
├── component4/            # Port 8004: Skill Gap Diagnostics & Career Path (Yenura S. Karunanayaka)
│   ├── models/            # gbdt_hireability.pkl (300 Trees), course_catalog.json
│   └── dag/               # career_dag.py (Topological Traversal & Lateral Moves)
└── frontend/              # Port 5174: React 18 + Vite SPA User Interface"""
    story.append(make_box(dir_tree))
    story.append(sp(6))

    story.append(p("5.3 Frontend Interface and User Experiences", h1_style))
    story.append(p("The React 18 single-page application is partitioned into two specialized user experiences:"))
    story.append(b("• <b>Recruiter Command Center:</b> Provides talent acquisition panels with real-time job requisition creation, automated applicant ingestion monitoring, multi-attribute candidate leaderboards, and interactive SHAP waterfall explanations. Recruiters can inspect exact component score breakdowns (S_skill, S_exp, S_edu, S_int, CSS) and view demographic parity compliance metrics before issuing interview invitations."))
    story.append(b("• <b>Candidate Assessment &amp; Career Room:</b> Offers candidates an intuitive document submission portal, live proctored interview room (with microphone audio streaming, question prompts, and in-browser code editor with syntax highlighting), and a personalized developmental dashboard. For unshortlisted applicants, the portal visualizes identified skill gaps, predicted hireability trajectories, and month-by-month course roadmaps."))

    story.append(p("5.4 Cross-Component Middleware and Security Hardening", h1_style))
    story.append(p("All microservice endpoints enforce strict Cross-Origin Resource Sharing (CORS) whitelists, permitting requests exclusively from designated gateway and frontend origins. Security hardening includes input sanitization against SQL/NoSQL injection, document upload size limits (capped at 10 MB per resume), MIME-type verification, and automated PII masking before persistence."))

    story.append(p("5.5 System-Wide Automated Verification and Test Protocols", h1_style))
    story.append(p("To guarantee end-to-end software reliability, the platform implements a multi-tier testing protocol combining unit tests, schema contracts, and integration harnesses. Table 5.1 details the test coverage across all components:"))

    test_data = [
        [p("<b>Component / Service</b>", body_style), p("<b>Test Suite Module</b>", body_style), p("<b>Assertions &amp; Scope</b>", body_style), p("<b>Passed Tests</b>", body_style), p("<b>Execution Time</b>", body_style)],
        [p("Component 1 (Screening)", body_style), p("tests/test_c1_pipeline.py", body_style), p("NER boundary look-arounds, interval union algebra, 2D education, model serialization", body_style), p("195 / 195 (100%)", body_style), p("79.60 s", body_style)],
        [p("Component 2 (Interview)", body_style), p("tests/test_c2_interview.py", body_style), p("RAIGS question retrieval, SBERT rubric correlation, AST sandbox jail escapes", body_style), p("142 / 142 (100%)", body_style), p("45.20 s", body_style)],
        [p("Component 3 (Ranking)", body_style), p("tests/test_c3_ranking.py", body_style), p("Prerequisite gating, linear CSS weights, LambdaMART NDCG, fairness audits", body_style), p("118 / 118 (100%)", body_style), p("28.40 s", body_style)],
        [p("Component 4 (Career)", body_style), p("tests/test_c4_career.py", body_style), p("Fuzzy gap accuracy, GBDT inference, 2 skills/mo pacing, DAG cycle prevention", body_style), p("126 / 126 (100%)", body_style), p("34.10 s", body_style)],
        [p("API Gateway (Port 8000)", body_style), p("tests/test_gateway_e2e.py", body_style), p("JWT auth tokens, RBAC permissions, cross-service orchestrator workflows", body_style), p("84 / 84 (100%)", body_style), p("18.30 s", body_style)],
        [p("<b>TOTAL ECOSYSTEM</b>", body_bold), p("<b>Integrated Test Harness</b>", body_bold), p("<b>End-to-End Pipeline &amp; Service Verification</b>", body_bold), p("<b>665 / 665 (100%)</b>", body_bold), p("<b>205.60 s</b>", body_bold)]
    ]
    test_table = Table(test_data, colWidths=[105, 115, 137, 75, 55])
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
    story.append(p("Table 5.1: Automated Pytest Unit and Integration Test Verification Suite Breakdown Across RecruitAI.", caption_style))
    story.append(PageBreak())
