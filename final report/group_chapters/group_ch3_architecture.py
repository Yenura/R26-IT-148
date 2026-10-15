import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_group_ch3(story, styles, p, b, sp, make_box, caption_style, fig_dir):
    PRIMARY = colors.HexColor("#1A365D")
    SECONDARY = colors.HexColor("#2B6CB0")
    DARK_TEXT = colors.HexColor("#2D3748")

    ch_num_style = styles['ChapterNumber']
    ch_title_style = styles['ChapterTitle']
    h1_style = styles['Heading1_Custom']
    h2_style = styles['Heading2_Custom']
    body_style = styles['Body_Custom']
    body_bold = styles['Body_Bold']

    story.append(p("CHAPTER 3", ch_num_style))
    story.append(p("OVERALL SYSTEM ARCHITECTURE AND INTER-SERVICE INTEGRATION", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    story.append(p("3.1 Distributed Microservice Topology and Domain-Driven Design", h1_style))
    story.append(p("The RecruitAI platform is architected as an asynchronous, containerized multi-microservice ecosystem governed by domain-driven design principles. Rather than deploying a monolithic web application prone to single-point scaling bottlenecks, the system isolates each recruitment lifecycle stage into a dedicated, autonomous service running on an assigned TCP port:"))
    story.append(b("• <b>Unified API Gateway (Port 8000):</b> The central reverse proxy and client entry point. Governs JWT user authentication, role-based access control (Recruiter vs. Candidate), rate limiting, request validation, and orchestrates inter-service workflows."))
    story.append(b("• <b>Component 1 Microservice (Port 8001):</b> Automated Semantic Resume Screening and IT Job Role Classification. Ingests raw PDF/DOCX files, performs layout-aware extraction and PII redaction, executes boundary-guarded NER, calculates temporal experience algebra, predicts 20 canonical IT roles, and emits the candidate qualification vector."))
    story.append(b("• <b>Component 2 Microservice (Port 8002):</b> Autonomous Multi-Modal Technical Interview System. Manages live interview sessions, serves dynamically retrieved questions via RAIGS, processes audio via Whisper STT, performs dense rubric grading via SBERT, and executes untrusted code in an AST-secured sandbox."))
    story.append(b("• <b>Component 3 Microservice (Port 8003):</b> Candidate Suitability Scoring and Listwise Ranking Engine. Enforces prerequisite thresholds, calculates linear Candidate Suitability Scores (CSS), generates candidate leaderboards, benchmarks against LightGBM LambdaMART, and generates linear SHAP attributions."))
    story.append(b("• <b>Component 4 Microservice (Port 8004):</b> Skill Gap Diagnostics and Career Pathfinding System. Receives unshortlisted candidates, executes high-dimensional fuzzy and semantic skill gap analytics, computes hireability probabilities via tabular GBDT, and synthesizes personalized, paced learning roadmaps and DAG career transitions."))
    story.append(b("• <b>Interactive Web Frontend (Port 5174):</b> Single-Page Application (SPA) built on React 18, Vite, and TailwindCSS, providing responsive interfaces for recruiters (requisition management, leaderboards, SHAP waterfall charts) and candidates (resume upload, real-time interview room, diagnostic career roadmap)."))

    story.append(p("3.2 Inter-Service Dataflow and Candidate State Transitions", h1_style))
    story.append(p("Candidate processing follows a deterministic finite-state automaton across the five microservices:"))
    story.append(b("1. <i>Ingestion &amp; Parsing:</i> Candidate submits a resume via Port 5174. The Gateway routes the document to Port 8001. Component 1 strips PII, extracts 400+ technical skills, calculates deduplicated commercial tenure, evaluates academic credentials, predicts target role alignment, and stores the profile in MongoDB."))
    story.append(b("2. <i>Adaptive Examination:</i> Candidate enters the live assessment portal. Port 8002 loads the candidate's verified skill profile from Port 8001, dynamically generating a 10-question evaluation tailored to the target role. Audio and code submissions are graded in real time, yielding the composite interview vector S_int."))
    story.append(b("3. <i>Suitability Ranking &amp; Decision Gating:</i> The Gateway passes S_cv and S_int to Port 8003. Component 3 validates prerequisite rules (S_cv &gt;= 40%, S_int &gt;= 35%, must-have skill presence). Qualifying candidates receive an official Candidate Suitability Score (CSS = 0.40 S_cv + 0.60 S_int) and are positioned on the recruiter leaderboard."))
    story.append(b("4. <i>Remedial Career Diversion:</i> If a candidate fails prerequisite gating or ranks below the requisition hiring quota (unshortlisted), Port 8003 automatically dispatches an asynchronous event payload to Port 8004. Component 4 performs detailed gap diagnostics, predicts hireability probability via GBDT, and generates a structured monthly developmental roadmap paced at 2 skills per month, closing the recruitment loop."))

    story.append(p("3.3 Inter-Service REST Contracts and JSON Schema Specifications", h1_style))
    story.append(p("Inter-service communication is governed by strict Pydantic REST contracts enforcing strong typing and payload validation across all endpoints. Table 3.1 details the primary inter-service REST contracts:"))

    contract_data = [
        [p("<b>Source &rarr; Target Service</b>", body_style), p("<b>Endpoint &amp; HTTP Method</b>", body_style), p("<b>Core Request Payload</b>", body_style), p("<b>Validated Response Schema</b>", body_style)],
        [p("Gateway &rarr; C1 (Port 8001)", body_style), p("POST /api/v1/extract-cv-full", body_style), p("Multipart form-data: PDF/DOCX file, job_role_id", body_style), p("{candidate_id, skills[], E_tot, E_it, E_rel, L_deg, M_field, S_skill, S_exp, S_edu, S_cv}", body_style)],
        [p("Gateway &rarr; C2 (Port 8002)", body_style), p("POST /api/v1/interview/start", body_style), p("{candidate_id, role_id, target_seniority, cv_skills[]}", body_style), p("{session_id, questions[{q_id, type, prompt, max_time}]}", body_style)],
        [p("C2 &rarr; Gateway (Port 8000)", body_style), p("POST /api/v1/interview/complete", body_style), p("{session_id, audio_blobs[], code_snippets[]}", body_style), p("{P_mcq, P_desc, P_code, S_int, confidence, telemetry}", body_style)],
        [p("Gateway &rarr; C3 (Port 8003)", body_style), p("POST /api/v1/rank/evaluate", body_style), p("{candidate_id, S_cv, S_int, role_id, requisition_id}", body_style), p("{CSS, rank_tier, is_shortlisted, shap_values{}, gate_status}", body_style)],
        [p("C3 &rarr; C4 (Port 8004)", body_style), p("POST /api/v1/career/diagnose", body_style), p("{candidate_id, missing_skills[], current_skills[], target_role}", body_style), p("{gap_severity, hireability_prob, roadmap[{month, skills[], courses[]}], dag_moves[]}", body_style)]
    ]
    contract_table = Table(contract_data, colWidths=[105, 115, 120, 147])
    contract_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(contract_table)
    story.append(p("Table 3.1: Inter-Service RESTful API Communication Contracts across the RecruitAI Microservice Suite.", caption_style))
    story.append(sp(6))

    story.append(p("3.4 Shared Persistence and Data Modeling", h1_style))
    story.append(p("RecruitAI deploys MongoDB Atlas as its unified, distributed document persistence layer. The document-oriented model was selected over rigid relational schemas due to the high heterogeneity of semi-structured resume representations, dynamic question-bank structures, and hierarchical career roadmaps. Six primary collections are partitioned across the cluster:"))
    story.append(b("• <b>candidates:</b> Stores candidate biographical identifiers, redacted resume text, verified technical skills, temporal employment intervals, and educational credentials."))
    story.append(b("• <b>job_requisitions:</b> Contains enterprise job specifications, required vs. optional competencies, seniority benchmarks, and salary bands across 20 canonical roles."))
    story.append(b("• <b>interview_sessions:</b> Logs real-time interview telemetry, question prompts, Whisper audio transcriptions, code submissions, execution logs, and rubric scores."))
    story.append(b("• <b>rankings:</b> Maintains candidate suitability evaluations, composite CSS scores, leaderboard positions, and linear SHAP attribution vectors."))
    story.append(b("• <b>career_roadmaps:</b> Records personalized skill gap diagnostics, predicted hireability probabilities, sequenced learning modules, and DAG transition trajectories."))
    story.append(b("• <b>courses_catalog:</b> Contains metadata for 47 curated technical courses, mapping curriculum modules to canonical skill taxonomy tokens."))

    story.append(p("3.5 API Gateway Security, JWT Authentication, and Resiliency", h1_style))
    story.append(p("All external interactions are funneled through the central FastAPI Gateway on Port 8000. Security controls enforce asymmetric JWT (JSON Web Token) bearer authentication with 60-minute expiration windows. Role-Based Access Control (RBAC) separates recruiter operations (viewing leaderboards, triggering ranking audits, posting requisitions) from candidate actions (uploading CVs, completing interviews, viewing personal developmental roadmaps)."))
    story.append(p("To ensure system-wide resilience under peak application surges, the Gateway implements circuit breaker patterns and asynchronous retries with exponential backoff for inter-service HTTP calls. If downstream microservices experience temporary latency spikes, the Gateway gracefully buffers requests and returns asynchronous job tracking identifiers (HTTP 202 Accepted), ensuring uninterrupted intake operations."))
    story.append(PageBreak())
