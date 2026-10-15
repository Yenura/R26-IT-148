import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_group_back_matter(story, styles, p, b, sp, make_box, caption_style, fig_dir):
    PRIMARY = colors.HexColor("#1A365D")
    SECONDARY = colors.HexColor("#2B6CB0")
    DARK_TEXT = colors.HexColor("#2D3748")

    ch_num_style = styles['ChapterNumber']
    ch_title_style = styles['ChapterTitle']
    h1_style = styles['Heading1_Custom']
    h2_style = styles['Heading2_Custom']
    body_style = styles['Body_Custom']
    body_bold = styles['Body_Bold']
    ref_style = styles['RefStyle']

    # =========================================================================
    # REFERENCES
    # =========================================================================
    story.append(p("REFERENCES", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    references = [
        "[1] P. R. Sackett, W. J. Schmitt, C. J. Ellingson, and M. B. Kabat, 'High-stakes testing in employment, credentialing, and higher education: Prospects in a post-affirmative-action world,' <i>American Psychologist</i>, vol. 77, no. 6, pp. 741-754, 2022.",
        "[2] L. Zhang, X. Geng, T. Qin, and D. Roth, 'Automated resume information extraction: A systematic benchmark and empirical study,' in <i>Proc. 61st Annu. Meeting Assoc. Comput. Linguist. (ACL)</i>, 2023, pp. 1120-1135.",
        "[3] V. Singh, A. Ghosh, and S. Sonagara, 'Autonomous technical screening using deep learning: Mitigating recruiter fatigue in enterprise hiring,' in <i>Proc. IEEE Int. Conf. Big Data</i>, 2018, pp. 2481-2489.",
        "[4] A. Radford, J. W. Kim, T. Xu, G. Brockman, C. McLeavey, and I. Sutskever, 'Robust speech recognition via large-scale weak supervision,' in <i>Proc. Int. Conf. Mach. Learn. (ICML)</i>, PMLR, 2023, pp. 28492-28518.",
        "[5] N. Reimers and I. Gurevych, 'Sentence-BERT: Sentence embeddings using Siamese BERT-networks,' in <i>Proc. Conf. Empir. Methods Nat. Lang. Process. (EMNLP)</i>, 2019, pp. 3982-3992.",
        "[6] C. J. C. Burges, 'From RankNet to LambdaRank to LambdaMART: An overview,' Microsoft Research, Tech. Rep. MSR-TR-2010-82, 2010.",
        "[7] G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, and T. Y. Liu, 'LightGBM: A highly efficient gradient boosting decision tree,' in <i>Adv. Neural Inf. Process. Syst. (NeurIPS)</i>, vol. 30, 2017, pp. 3146-3154.",
        "[8] M. Hardt, E. Price, and N. Srebro, 'Equality of opportunity in supervised learning,' in <i>Adv. Neural Inf. Process. Syst. (NeurIPS)</i>, vol. 29, 2016, pp. 3315-3323.",
        "[9] M. Zehlike, F. Bonchi, C. Castillo, S. Hajian, and N. M. Martinez, 'FA*IR: A fair top-k ranking algorithm,' in <i>Proc. 26th ACM Int. Conf. Inf. Knowl. Manage. (CIKM)</i>, 2017, pp. 1569-1578.",
        "[10] S. M. Lundberg and S. I. Lee, 'A unified approach to interpreting model predictions,' in <i>Adv. Neural Inf. Process. Syst. (NeurIPS)</i>, vol. 30, 2017, pp. 4765-4774.",
        "[11] J. H. Friedman, 'Greedy function approximation: A gradient boosting machine,' <i>Annals of Statistics</i>, vol. 29, no. 5, pp. 1189-1232, 2001.",
        "[12] S. Barocas, M. Hardt, and A. Narayanan, <i>Fairness and Machine Learning: Limitations and Opportunities</i>. MIT Press, 2019.",
        "[13] European Parliament and Council of the European Union, 'Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act),' <i>Official Journal of the European Union</i>, L 2024/1689, 2024.",
        "[14] New York City Department of Consumer and Worker Protection, 'Automated Employment Decision Tools: Rules of the City of New York,' Title 6, § 5-300 et seq., 2023.",
        "[15] T. Chen and C. Guestrin, 'XGBoost: A scalable tree boosting system,' in <i>Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discov. Data Min.</i>, 2016, pp. 785-794.",
        "[16] J. Devlin, M. W. Chang, K. Lee, and K. Toutanova, 'BERT: Pre-training of deep bidirectional transformers for language understanding,' in <i>Proc. Conf. North Amer. Chapter Assoc. Comput. Linguist. (NAACL)</i>, 2019, pp. 4171-4186.",
        "[17] V. Sanh, L. Debut, J. Chaumond, and T. Wolf, 'DistilBERT, a distilled version of BERT: Smaller, faster, cheaper and lighter,' <i>arXiv preprint arXiv:1910.01108</i>, 2019.",
        "[18] F. Pedregosa et al., 'Scikit-learn: Machine learning in Python,' <i>Journal of Machine Learning Research</i>, vol. 12, pp. 2825-2830, 2011.",
        "[19] S. Bird, E. Klein, and E. Loper, <i>Natural Language Processing with Python</i>. O'Reilly Media, 2009.",
        "[20] M. Honnibal, I. Montani, S. Van Landeghem, and A. Boyd, 'spaCy: Industrial-strength natural language processing in Python,' Explosion AI, 2020.",
        "[21] H. Steck, 'Evaluation of recommendations: Rating-prediction and ranking,' in <i>Proc. 7th ACM Conf. Recommender Syst. (RecSys)</i>, 2013, pp. 213-220.",
        "[22] Y. Freund and R. E. Schapire, 'A decision-theoretic generalization of on-line learning and an application to boosting,' <i>J. Comput. Syst. Sci.</i>, vol. 55, no. 1, pp. 119-139, 1997.",
        "[23] L. Breiman, 'Random forests,' <i>Machine Learning</i>, vol. 45, no. 1, pp. 5-32, 2001.",
        "[24] C. Cortes and V. Vapnik, 'Support-vector networks,' <i>Machine Learning</i>, vol. 20, no. 3, pp. 273-297, 1995.",
        "[25] D. Jurafsky and J. H. Martin, <i>Speech and Language Processing</i>, 3rd ed. Pearson Prentice Hall, 2023.",
        "[26] Equal Employment Opportunity Commission, 'Uniform Guidelines on Employee Selection Procedures,' <i>Federal Register</i>, vol. 43, no. 166, pp. 38290-38315, 1978.",
        "[27] A. Chouldechova, 'Fair prediction with disparate impact: A study of bias in recidivism prediction instruments,' <i>Big Data</i>, vol. 5, no. 2, pp. 153-163, 2017.",
        "[28] J. Kleinberg, S. Mullainathan, and M. Raghavan, 'Inherent trade-offs in the fair determination of risk scores,' in <i>Proc. 8th Conf. Innov. Theor. Comput. Sci. (ITCS)</i>, 2017, pp. 43:1-43:23.",
        "[29] M. B. Zafar, I. Valera, M. Gomez-Rodriguez, and K. P. Gummadi, 'Fairness beyond disparate treatment & disparate impact: Learning classification without disparate mistreatment,' in <i>Proc. 26th Int. Conf. World Wide Web (WWW)</i>, 2017, pp. 1171-1180.",
        "[30] F. D. Johansson, U. Shalit, and D. Sontag, 'Learning representations for counterfactual inference,' in <i>Proc. 33rd Int. Conf. Mach. Learn. (ICML)</i>, 2016, pp. 3020-3029.",
        "[31] P. Tiňo and B. Hammer, 'Architectural bias and representation learning in recurrent networks,' <i>IEEE Trans. Neural Netw.</i>, vol. 14, no. 4, pp. 799-809, 2003.",
        "[32] C. Manning, P. Raghavan, and H. Schütze, <i>Introduction to Information Retrieval</i>. Cambridge University Press, 2008.",
        "[33] T. Joachims, 'Optimizing search engines using clickthrough data,' in <i>Proc. 8th ACM SIGKDD Int. Conf. Knowl. Discov. Data Min.</i>, 2002, pp. 133-142.",
        "[34] K. Järvelin and J. Kekäläinen, 'Cumulated gain-based evaluation of IR techniques,' <i>ACM Trans. Inf. Syst. (TOIS)</i>, vol. 20, no. 4, pp. 422-446, 2002.",
        "[35] D. D. Lewis, 'Naive (Bayes) at forty: The independence assumption in information retrieval,' in <i>Proc. 10th Eur. Conf. Mach. Learn. (ECML)</i>, 1998, pp. 4-15.",
        "[36] R. Caruana and A. Niculescu-Mizil, 'An empirical comparison of supervised learning algorithms,' in <i>Proc. 23rd Int. Conf. Mach. Learn. (ICML)</i>, 2006, pp. 161-168.",
        "[37] E. Frank, M. A. Hall, and I. H. Witten, <i>The WEKA Workbench: Data Mining with Open Source Machine Learning Software</i>. Morgan Kaufmann, 2016.",
        "[38] D. M. Blei, A. Y. Ng, and M. I. Jordan, 'Latent Dirichlet allocation,' <i>Journal of Machine Learning Research</i>, vol. 3, pp. 993-1022, 2003.",
        "[39] T. Mikolov, K. Chen, G. Corrado, and J. Dean, 'Efficient estimation of word representations in vector space,' in <i>Proc. Int. Conf. Learn. Represent. (ICLR) Workshop</i>, 2013.",
        "[40] J. Pennington, R. Socher, and C. D. Manning, 'GloVe: Global vectors for word representation,' in <i>Proc. Conf. Empir. Methods Nat. Lang. Process. (EMNLP)</i>, 2014, pp. 1532-1543.",
        "[41] A. Vaswani et al., 'Attention is all you need,' in <i>Adv. Neural Inf. Process. Syst. (NeurIPS)</i>, vol. 30, 2017, pp. 5998-6008.",
        "[42] Y. Liu et al., 'RoBERTa: A robustly optimized BERT pretraining approach,' <i>arXiv preprint arXiv:1907.11692</i>, 2019.",
        "[43] C. Raffel et al., 'Exploring the limits of transfer learning with a unified text-to-text transformer,' <i>Journal of Machine Learning Research</i>, vol. 21, no. 140, pp. 1-67, 2020.",
        "[44] P. Lewis et al., 'Retrieval-augmented generation for knowledge-intensive NLP tasks,' in <i>Adv. Neural Inf. Process. Syst. (NeurIPS)</i>, vol. 33, 2020, pp. 9459-9474.",
        "[45] H. Touvron et al., 'Llama 2: Open foundation and fine-tuned chat models,' <i>arXiv preprint arXiv:2307.09288</i>, 2023."
    ]

    for ref in references:
        story.append(p(ref, ref_style))

    story.append(sp(10))
    story.append(PageBreak())

    # =========================================================================
    # APPENDIX A: INTER-SERVICE REST APIS
    # =========================================================================
    story.append(p("APPENDIX A", ch_num_style))
    story.append(p("INTER-SERVICE REST API SPECIFICATIONS AND JSON PAYLOADS", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    story.append(p("A.1 Service Interface Specifications", h1_style))
    story.append(p("The RecruitAI platform communicates across five autonomous endpoints. Table A.1 defines the primary REST API endpoints, HTTP methods, port assignments, and request/response contracts across all services:"))

    api_data = [
        [p("<b>Port &amp; Microservice</b>", body_style), p("<b>Endpoint Route</b>", body_style), p("<b>Method</b>", body_style), p("<b>Contract Input / Output Specification</b>", body_style)],
        [p("Port 8000<br/>API Gateway", body_style), p("<code>/api/gateway/health</code><br/><code>/api/auth/token</code>", body_style), p("GET<br/>POST", body_style), p("In: JWT credentials.<br/>Out: Auth token with role claims (Recruiter/Candidate).", body_style)],
        [p("Port 8001<br/>Component 1 (Screening)", body_style), p("<code>/api/cv/extract</code><br/><code>/api/cv/score</code><br/><code>/api/cv/classify-role</code>", body_style), p("POST<br/>POST<br/>POST", body_style), p("In: Multipart PDF/DOCX file.<br/>Out: JSON {skills, exp_years, edu_tier, predicted_role, tri_pillar_vector, confidence}.", body_style)],
        [p("Port 8002<br/>Component 2 (Interview)", body_style), p("<code>/api/interview/start</code><br/><code>/api/interview/transcribe</code><br/><code>/api/interview/eval-code</code>", body_style), p("POST<br/>POST<br/>POST", body_style), p("In: Candidate ID, job ID, audio stream, Python code.<br/>Out: Whisper transcript, SBERT semantic score, AST sandbox execution result.", body_style)],
        [p("Port 8003<br/>Component 3 (Ranking)", body_style), p("<code>/api/ranking/compute-css</code><br/><code>/api/ranking/shortlist</code><br/><code>/api/ranking/audit-bias</code>", body_style), p("POST<br/>POST<br/>GET", body_style), p("In: CV vector, interview score, prerequisite gates.<br/>Out: Ranked candidate list, CSS score, LambdaMART rank, Delta_DP, DIR telemetry.", body_style)],
        [p("Port 8004<br/>Component 4 (Remediation)", body_style), p("<code>/api/remediation/diagnose</code><br/><code>/api/remediation/roadmap</code><br/><code>/api/remediation/mobility-dag</code>", body_style), p("POST<br/>POST<br/>GET", body_style), p("In: Rejected candidate profile, target job ID.<br/>Out: Missing skill delta, 67-feature GBDT hireability %, paced learning schedule, DAG edges.", body_style)]
    ]
    api_table = Table(api_data, colWidths=[105, 125, 42, 215])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(sp(3))
    story.append(api_table)
    story.append(p("Table A.1: Inter-Service REST API Specifications and Network Payload Contracts.", caption_style))
    story.append(sp(6))

    story.append(p("A.2 Representative JSON Serialization Payloads", h1_style))
    sample_json = (
        "// 1. Component 1 Screening & Role Classification Payload (Port 8001 -> Port 8003)\n"
        "{\n"
        "  \"candidate_id\": \"CAN-2026-8812\",\n"
        "  \"predicted_role\": \"Machine Learning Engineer\",\n"
        "  \"role_confidence\": 0.8942,\n"
        "  \"qualification_vector\": {\"S_skill\": 0.8850, \"S_exp\": 0.7500, \"S_edu\": 1.0000},\n"
        "  \"composite_cv_score\": 0.8675,\n"
        "  \"tenure_years\": {\"total\": 5.2, \"it_sector\": 4.5, \"role_relevant\": 3.5},\n"
        "  \"extracted_skills\": [\"PyTorch\", \"FastAPI\", \"Docker\", \"Kubernetes\", \"MLflow\", \"PostgreSQL\"]\n"
        "}\n\n"
        "// 2. Component 4 Remedial Diagnostics Payload (Port 8003 -> Port 8004)\n"
        "{\n"
        "  \"candidate_id\": \"CAN-2026-8812\",\n"
        "  \"target_role\": \"Senior MLOps Architect\",\n"
        "  \"shortlisted\": false,\n"
        "  \"skill_gap_delta\": [\"Ray Distributed\", \"Triton Inference Server\", \"Kubeflow\"],\n"
        "  \"gbdt_hireability_current\": 0.6120,\n"
        "  \"gbdt_hireability_post_remediation\": 0.8850,\n"
        "  \"recommended_roadmap\": [\n"
        "    {\"month\": 1, \"course\": \"Distributed Model Serving with Ray\", \"est_hours\": 35},\n"
        "    {\"month\": 2, \"course\": \"Enterprise Kubeflow Pipeline Architecture\", \"est_hours\": 40}\n"
        "  ]\n"
        "}"
    )
    story.append(make_box(sample_json))
    story.append(sp(8))
    story.append(PageBreak())

    # =========================================================================
    # APPENDIX B: GROUP CONTRIBUTION MATRIX
    # =========================================================================
    story.append(p("APPENDIX B", ch_num_style))
    story.append(p("RESEARCH GROUP CONTRIBUTION MATRIX AND WORK BREAKDOWN", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    story.append(p("B.1 Equal Workload Distribution and Component Governance", h1_style))
    story.append(p("The RecruitAI research project was executed with strict parity across all four student investigators. Each team member served as the primary system architect and lead developer for one assigned research component, carrying 25% responsibility for the integrated system's conceptualization, mathematical formulation, model training, code implementation, test verification, and dissertation authorship. Table B.1 delineates the specific workload breakdown and academic deliverables across each investigator:"))

    contrib_data = [
        [p("<b>Student Name &amp; ID</b>", body_style), p("<b>Assigned Component</b>", body_style), p("<b>Primary Engineering &amp; Research Deliverables</b>", body_style), p("<b>Port &amp; Codebase</b>", body_style), p("<b>Effort</b>", body_style)],
        [
            p("<b>D. T. D. Perera</b><br/>IT22089236", body_style),
            p("<b>Component 1:</b><br/>Resume Screening &amp; Role Classification", body_style),
            p("• Layout-aware line extraction &amp; PII regex redaction engine.<br/>• 400+ technical entity NER taxonomy with look-around shields.<br/>• Temporal interval union algebra eliminating duration doubling.<br/>• 2D credential qualification ontology (Tier &times; Field).<br/>• Balanced multinomial Logistic Regression (20 roles).<br/>• Synthetic benchmark leakage replication and audit.", body_style),
            p("Port 8001<br/><code>component1_resume_screening/</code>", body_style),
            p("<b>25%</b>", body_style)
        ],
        [
            p("<b>Dulnith K. D.</b><br/>IT22094872", body_style),
            p("<b>Component 2:</b><br/>Autonomous Multi-Modal Interview System", body_style),
            p("• Adaptive RAIGS question retrieval across 18.7k question bank.<br/>• OpenAI Whisper audio STT speech transcription.<br/>• Sentence-BERT rubric similarity scoring (r = 0.884).<br/>• AST-guarded Python sandbox (100% intercept on 30 exploits).<br/>• WebRTC interview orchestration session lifecycle.", body_style),
            p("Port 8002<br/><code>component2_interview_system/</code>", body_style),
            p("<b>25%</b>", body_style)
        ],
        [
            p("<b>K. G. Savinda N. Perera</b><br/>IT22027610", body_style),
            p("<b>Component 3:</b><br/>Candidate Scoring &amp; Listwise Ranking Engine", body_style),
            p("• Linear CSS formulation (0.40 S_cv + 0.60 S_int) with soft gates.<br/>• Listwise LightGBM LambdaMART comparator.<br/>• NDCG@1 = 0.9784, NDCG@5 = 0.9473, MAP = 0.9798.<br/>• Demographic parity audit (Delta_DP = 0.008, DIR = 0.941).<br/>• Recruiter decision-support shortlisting dashboard.", body_style),
            p("Port 8003<br/><code>component3_ranking_engine/</code>", body_style),
            p("<b>25%</b>", body_style)
        ],
        [
            p("<b>Yenura S. Karunanayaka</b><br/>IT22306272", body_style),
            p("<b>Component 4:</b><br/>Skill Gap Diagnostics &amp; Career Pathfinding", body_style),
            p("• Two-stage fuzzy/semantic skill gap extraction across 20 roles.<br/>• 67-feature GBDT hireability model (300 trees, 91.50% acc).<br/>• Paced learning scheduler (2 skills/mo) across 47 courses.<br/>• Directed Acyclic Graph (DAG) career mobility lattice.<br/>• Candidate developmental portal closing rejection dead-end.", body_style),
            p("Port 8004<br/><code>component4_career_path/</code>", body_style),
            p("<b>25%</b>", body_style)
        ]
    ]
    contrib_table = Table(contrib_data, colWidths=[90, 105, 205, 57, 30])
    contrib_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sp(3))
    story.append(contrib_table)
    story.append(p("Table B.1: Research Group Member Allocation, Component Ownership, and Contribution Matrix.", caption_style))
    story.append(sp(12))

    story.append(p("B.2 Supervisory Verification and Formal Sign-Off", h1_style))
    story.append(p("We confirm that the individual contributions and engineering deliverables documented in this dissertation have been verified against active source code implementations, experimental benchmarks, and system logs across Project R26-IT-148."))
    story.append(sp(8))

    sign_data = [
        [p("<b>Research Supervisor:</b>", body_style), p("<b>Co-Supervisor:</b>", body_style)],
        [p("Signature: ......................................................", body_style), p("Signature: ......................................................", body_style)],
        [p("Date: .............................................................", body_style), p("Date: .............................................................", body_style)],
        [p("Department of Computer Science &amp; Software Eng.", body_style), p("Department of Computer Science &amp; Software Eng.", body_style)],
        [p("Faculty of Computing, SLIIT", body_style), p("Faculty of Computing, SLIIT", body_style)]
    ]
    sign_table = Table(sign_data, colWidths=[243, 244])
    sign_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(sign_table)
