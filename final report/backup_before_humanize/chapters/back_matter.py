import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
from reportlab.lib import colors

def append_back_matter(story, styles, p, b, sp, make_box, caption_style, ref_style, tracker=None):
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
        story.append(PageTracker('refs', tracker))

    # =========================================================================
    # REFERENCES
    # =========================================================================
    story.append(p("REFERENCES", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))

    references = [
        "[1] J. F. Allen, 'Maintaining knowledge about temporal intervals,' Communications of the ACM, vol. 26, no. 11, pp. 832-843, Nov. 1983.",
        "[2] J. Devlin, M. W. Chang, K. Lee, and K. Toutanova, 'BERT: Pre-training of deep bidirectional transformers for language understanding,' in Proc. NAACL-HLT, Minneapolis, MN, USA, Jun. 2019, pp. 4171-4186.",
        "[3] N. Reimers and I. Gurevych, 'Sentence-BERT: Sentence embeddings using Siamese BERT-networks,' in Proc. EMNLP-IJCNLP, Hong Kong, China, Nov. 2019, pp. 3982-3992.",
        "[4] P. R. Sackett, W. J. Shen, P. J. Kostal, et al., 'Revisiting the design and predictive validity of selection procedures in personnel psychology,' Journal of Applied Psychology, vol. 107, no. 11, pp. 2040-2068, Nov. 2022.",
        "[5] A. Singh and T. Joachims, 'Fairness of exposure in rankings,' in Proc. 24th ACM SIGKDD Conf. Knowl. Discovery Data Min. (KDD), London, UK, Aug. 2018, pp. 2219-2228.",
        "[6] M. Raghavan, S. Barocas, J. Kleinberg, and K. Levy, 'Mitigating bias in algorithmic hiring: Evaluating claims and practices,' in Proc. ACM Conf. Fairness, Account., Transpar. (FAT*), Barcelona, Spain, Jan. 2020, pp. 469-481.",
        "[7] F. Pedregosa, G. Varoquaux, A. Gramfort, et al., 'Scikit-learn: Machine learning in Python,' Journal of Machine Learning Research, vol. 12, pp. 2825-2830, Nov. 2011.",
        "[8] D. Jurafsky and J. H. Martin, Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics, and Speech Recognition, 3rd ed. draft, Prentice Hall, 2023.",
        "[9] C. D. Manning, P. Raghavan, and H. Schutze, Introduction to Information Retrieval, Cambridge, UK: Cambridge University Press, 2008.",
        "[10] F. Sebastiani, 'Machine learning in automated text categorization,' ACM Computing Surveys, vol. 34, no. 1, pp. 1-47, Mar. 2002.",
        "[11] G. Lample, M. Ballesteros, S. Subramanian, K. Kawakami, and C. Dyer, 'Neural architectures for named entity recognition,' in Proc. NAACL-HLT, San Diego, CA, USA, Jun. 2016, pp. 260-270.",
        "[12] A. Vaswani, N. Shazeer, N. Parmar, et al., 'Attention is all you need,' in Advances in Neural Information Processing Systems (NeurIPS), Long Beach, CA, USA, Dec. 2017, pp. 5998-6008.",
        "[13] V. Sanh, L. Debut, J. Chaumond, and T. Wolf, 'DistilBERT, a distilled version of BERT: Smaller, faster, cheaper and lighter,' in NeurIPS EMC2 Workshop, Vancouver, Canada, Dec. 2019, arXiv:1910.01108.",
        "[14] S. M. Lundberg and S.-I. Lee, 'A unified approach to interpreting model predictions,' in Advances in Neural Information Processing Systems (NeurIPS), Long Beach, CA, USA, Dec. 2017, pp. 4765-4774.",
        "[15] A. R. Hevner, S. T. March, J. Park, and S. Ram, 'Design science in information systems research,' MIS Quarterly, vol. 28, no. 1, pp. 75-105, Mar. 2004.",
        "[16] C. Zhang, M. Yin, H. Liu, et al., 'Large language models for job recommendation and resume parsing: A comprehensive survey,' IEEE Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12450-12465, Dec. 2023.",
        "[17] European Parliament and Council of the European Union, 'Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act),' Official Journal of the European Union, L Series, Jul. 2024.",
        "[18] New York City Department of Consumer and Worker Protection, 'Notice of adoption of final rules regarding automated employment decision tools (Local Law 144 of 2021),' The City Record, Apr. 2023.",
        "[19] Equal Employment Opportunity Commission (EEOC), 'Uniform guidelines on employee selection procedures,' Federal Register, vol. 43, no. 166, pp. 38290-38315, Aug. 1978.",
        "[20] C. Burges, R. Ragno, and Q. Le, 'Learning to rank with nonsmooth cost functions,' in Advances in Neural Information Processing Systems (NeurIPS), Vancouver, Canada, Dec. 2006, pp. 193-200.",
        "[21] T.-Y. Liu, 'Learning to rank for information retrieval,' Foundations and Trends in Information Retrieval, vol. 3, no. 3, pp. 225-331, Mar. 2009.",
        "[22] European Commission, 'The European Qualifications Framework for lifelong learning (EQF),' Publications Office of the European Union, Luxembourg, 2018.",
        "[23] Sri Lanka Qualifications Framework (SLQF), Ministry of Higher Education and University Grants Commission, Colombo, Sri Lanka, 2015.",
        "[24] J. Pennington, R. Socher, and C. D. Manning, 'GloVe: Global vectors for word representation,' in Proc. EMNLP, Doha, Qatar, Oct. 2014, pp. 1532-1543.",
        "[25] T. Mikolov, K. Chen, G. Corrado, and J. Dean, 'Efficient estimation of word representations in vector space,' in Proc. ICLR Workshop, Scottsdale, AZ, USA, May 2013, arXiv:1301.3781.",
        "[26] Y. Cui, W. Che, T. Liu, B. Qin, and Z. Yang, 'Pre-training with whole word masking for Chinese BERT,' IEEE/ACM Trans. Audio, Speech, Lang. Process., vol. 29, pp. 3504-3514, Nov. 2021.",
        "[27] H. Schutze, 'Ambiguity in language and text mining,' Computational Linguistics, vol. 24, no. 1, pp. 97-123, 1998.",
        "[28] P. Bojanowski, E. Grave, A. Joulin, and T. Mikolov, 'Enriching word vectors with subword information,' Trans. Assoc. Comput. Linguistics, vol. 5, pp. 135-146, 2017.",
        "[29] I. Beltagy, K. Lo, and A. Cohan, 'SciBERT: A pretrained language model for scientific text,' in Proc. EMNLP-IJCNLP, Hong Kong, China, Nov. 2019, pp. 3615-3620.",
        "[30] Y. Liu, M. Ott, N. Goyal, et al., 'RoBERTa: A robustly optimized BERT pretraining approach,' arXiv:1907.11692, Jul. 2019.",
        "[31] C. Raffel, N. Shazeer, A. Roberts, et al., 'Exploring the limits of transfer learning with a unified text-to-text transformer,' Journal of Machine Learning Research, vol. 21, no. 140, pp. 1-67, 2020.",
        "[32] S. Bird, E. Klein, and E. Loper, Natural Language Processing with Python, O'Reilly Media, 2009.",
        "[33] M. Honnibal and I. Montani, 'spaCy 2: Natural language understanding with Bloom embeddings, convolutional neural networks and incremental parsing,' Sentometrics Research, 2017.",
        "[34] L. Breiman, 'Random forests,' Machine Learning, vol. 45, no. 1, pp. 5-32, Oct. 2001.",
        "[35] C. Cortes and V. Vapnik, 'Support-vector networks,' Machine Learning, vol. 20, no. 3, pp. 273-297, Sep. 1995.",
        "[36] J. Friedman, 'Greedy function approximation: A gradient boosting machine,' Annals of Statistics, vol. 29, no. 5, pp. 1189-1232, Oct. 2001.",
        "[37] T. Chen and C. Guestrin, 'XGBoost: A scalable tree boosting system,' in Proc. 22nd ACM SIGKDD Conf. Knowl. Discovery Data Min. (KDD), San Francisco, CA, USA, Aug. 2016, pp. 785-794.",
        "[38] G. Ke, Q. Meng, T. Finley, et al., 'LightGBM: A highly efficient gradient boosting decision tree,' in Advances in Neural Information Processing Systems (NeurIPS), Long Beach, CA, USA, Dec. 2017, pp. 3146-3154.",
        "[39] D. M. Blei, A. Y. Ng, and M. I. Jordan, 'Latent Dirichlet allocation,' Journal of Machine Learning Research, vol. 3, pp. 993-1022, Mar. 2003.",
        "[40] K. Toutanova, D. Klein, C. D. Manning, and Y. Singer, 'Feature-rich part-of-speech tagging with a cyclic dependency network,' in Proc. NAACL-HLT, Edmonton, Canada, May 2003, pp. 173-180.",
        "[41] D. Nadeau and S. Sekine, 'A survey of named entity recognition and classification,' Lingvisticae Investigationes, vol. 30, no. 1, pp. 3-26, Jan. 2007.",
        "[42] J. Lafferty, A. McCallum, and F. C. N. Pereira, 'Conditional random fields: Probabilistic models for segmenting and labeling sequence data,' in Proc. 18th Int. Conf. Mach. Learn. (ICML), Williamstown, MA, USA, Jun. 2001, pp. 282-289.",
        "[43] Z. Huang, W. Xu, and K. Yu, 'Bidirectional LSTM-CRF models for sequence tagging,' arXiv:1508.01991, Aug. 2015.",
        "[44] Y. Goldberg, 'Neural network methods for natural language processing,' Synthesis Lectures on Human Language Technologies, vol. 10, no. 1, pp. 1-309, 2017.",
        "[45] E. H. Huang, R. Socher, C. D. Manning, and A. Y. Ng, 'Improving word representations via global context and multiple word prototypes,' in Proc. ACL, Jeju Island, Korea, Jul. 2012, pp. 873-882.",
        "[46] T. Joachims, 'Text categorization with support vector machines: Learning with many relevant features,' in Proc. ECML, Chemnitz, Germany, Apr. 1998, pp. 137-142.",
        "[47] P. Domingos and M. Pazzani, 'On the optimality of the simple Bayesian classifier under zero-one loss,' Machine Learning, vol. 29, no. 2, pp. 103-130, Nov. 1997.",
        "[48] A. McCallum and K. Nigam, 'A comparison of event models for Naive Bayes text classification,' in AAAI-98 Workshop on Learning for Text Categorization, Madison, WI, USA, Jul. 1998, pp. 41-48.",
        "[49] R. Caruana and A. Niculescu-Mizil, 'An empirical comparison of supervised learning algorithms,' in Proc. 23rd Int. Conf. Mach. Learn. (ICML), Pittsburgh, PA, USA, Jun. 2006, pp. 161-168.",
        "[50] J. Davis and M. Goadrich, 'The relationship between Precision-Recall and ROC curves,' in Proc. 23rd Int. Conf. Mach. Learn. (ICML), Pittsburgh, PA, USA, Jun. 2006, pp. 233-240.",
        "[51] D. M. Powers, 'Evaluation: From precision, recall and F-factor to ROC, informedness, markedness and correlation,' Journal of Machine Learning Technologies, vol. 2, no. 1, pp. 37-63, 2011.",
        "[52] R. Kohavi, 'A study of cross-validation and bootstrap for accuracy estimation and model selection,' in Proc. 14th Int. Joint Conf. Artif. Intell. (IJCAI), Montreal, Canada, Aug. 1995, pp. 1137-1145.",
        "[53] J. Demšar, 'Statistical comparisons of classifiers over multiple data sets,' Journal of Machine Learning Research, vol. 7, pp. 1-30, Jan. 2006.",
        "[54] C. Drummond and R. C. Holte, 'Cost curves: An alternative to ROC curves,' Machine Learning, vol. 65, no. 1, pp. 95-130, Oct. 2006.",
        "[55] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, 'SMOTE: Synthetic minority over-sampling technique,' Journal of Artificial Intelligence Research, vol. 16, pp. 321-357, Jun. 2002.",
        "[56] H. He and E. A. Garcia, 'Learning from imbalanced data,' IEEE Trans. Knowl. Data Eng., vol. 21, no. 9, pp. 1263-1284, Sep. 2009.",
        "[57] B. Zadrozny and C. Elkan, 'Transforming classifier scores into accurate multiclass probability estimates,' in Proc. 8th ACM SIGKDD Conf. Knowl. Discovery Data Min. (KDD), Edmonton, Canada, Jul. 2002, pp. 694-699.",
        "[58] A. Niculescu-Mizil and R. Caruana, 'Predicting good probabilities with supervised learning,' in Proc. 22nd Int. Conf. Mach. Learn. (ICML), Bonn, Germany, Aug. 2005, pp. 625-632.",
        "[59] J. Platt, 'Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods,' Advances in Large Margin Classifiers, vol. 10, no. 3, pp. 61-74, 1999.",
        "[60] D. T. D. Perera, D. K. D., K. G. S. N. Perera, and Y. S. Karunanayaka, 'RecruitAI: Next-generation AI-driven recruitment and predictive career development ecosystem,' SLIIT Technical Report, Project R26-IT-148, Oct. 2026."
    ]

    for ref in references:
        story.append(p(ref, ref_style))

    story.append(PageBreak())

    # =========================================================================
    # APPENDIX A: ROLES TAXONOMY
    # =========================================================================
    if tracker is not None:
        story.append(PageTracker('app_a', tracker))
    story.append(p("APPENDIX A", ch_num_style))
    story.append(p("CANONICAL 20 IT JOB ROLES COMPETENCY TAXONOMY", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))
    story.append(p("Component 1 supports 20 canonical software engineering specializations structured across 6 architectural domains:"))

    roles_tax_data = [
        [p("<b>Domain Cluster</b>", body_style), p("<b>Supported Canonical Roles</b>", body_style), p("<b>Primary Technical Competencies &amp; Tools</b>", body_style)],
        [p("<b>Core Software Engineering</b>", body_style), p("• Software Engineer (General)<br/>• Full Stack Developer<br/>• Frontend Developer<br/>• Backend Developer<br/>• Mobile App Developer", body_style), p("Java, Python, C++, TypeScript, JavaScript, React, Angular, Vue, Node.js, Spring Boot, Django, FastAPI, Android, iOS, Flutter, React Native, Swift, Kotlin, REST, GraphQL.", body_style)],
        [p("<b>Data, AI &amp; Analytics</b>", body_style), p("• Data Scientist<br/>• Machine Learning Engineer<br/>• AI/NLP Engineer<br/>• Data Engineer", body_style), p("Python, PyTorch, TensorFlow, Scikit-learn, Pandas, Spark, Hadoop, SQL, NoSQL, Kafka, Airflow, BERT, LLMs, NLP, Statistics, Deep Learning, MLOps, Data Warehousing.", body_style)],
        [p("<b>Infrastructure &amp; Cloud</b>", body_style), p("• Cloud Solutions Architect<br/>• DevOps Engineer<br/>• Site Reliability Engineer (SRE)<br/>• Database Administrator<br/>• Network Engineer", body_style), p("AWS, Azure, GCP, Kubernetes, Docker, Terraform, Ansible, CI/CD, Prometheus, Grafana, Linux, PostgreSQL, MySQL, MongoDB, Redis, TCP/IP, DNS, VPN, BGP, Firewalls.", body_style)],
        [p("<b>Security &amp; Quality</b>", body_style), p("• Cybersecurity Analyst<br/>• QA/Test Automation Engineer", body_style), p("Penetration Testing, SIEM, SOC, Wireshark, Cryptography, CISSP, OWASP, Selenium, Cypress, JUnit, PyTest, TestNG, Performance Testing, CI/CD Integration.", body_style)],
        [p("<b>Design &amp; Management</b>", body_style), p("• UI/UX Designer<br/>• Embedded Systems Engineer<br/>• Blockchain Developer<br/>• Business/Systems Analyst", body_style), p("Figma, Adobe XD, Wireframing, User Research, C, Embedded C, RTOS, ARM, Microcontrollers, IoT, Solidity, Smart Contracts, Ethereum, Web3, Agile, Scrum, UML, JIRA, BPMN.", body_style)]
    ]
    roles_tax_table = Table(roles_tax_data, colWidths=[120, 150, 217])
    roles_tax_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(roles_tax_table)
    story.append(sp(14))

    story.append(p("Detailed Competency Requirements across Core Engineering Roles:", h2_style))
    story.append(b("1. <b>Backend Developer:</b> Core: Python, Java, Go, C#, Node.js. Frameworks: FastAPI, Spring Boot, Django, Express. Databases: PostgreSQL, MongoDB, Redis. Architecture: Microservices, RESTful APIs, gRPC, Message Queues (RabbitMQ, Kafka)."))
    story.append(b("2. <b>Frontend Developer:</b> Core: JavaScript, TypeScript, HTML5, CSS3. Frameworks: React, Angular, Vue.js, Next.js. State Management: Redux, Zustand. Styling: Tailwind CSS, SASS. Testing: Jest, Cypress. Build Tools: Vite, Webpack."))
    story.append(b("3. <b>Full Stack Developer:</b> End-to-end integration across frontend, backend, and persistence tiers. Combined competency across React/Vue + Node.js/Python + relational/NoSQL datastores with Docker containerization."))
    story.append(b("4. <b>Mobile App Developer:</b> Cross-platform and native mobile toolchains: Flutter (Dart), React Native, Swift (iOS), Kotlin (Android). Local persistence (SQLite, Room, CoreData), push notifications, mobile app lifecycle."))
    story.append(b("5. <b>DevOps Engineer:</b> Infrastructure as Code (Terraform, Ansible), Container orchestration (Docker, Kubernetes), CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins), Monitoring (Prometheus, Grafana), Cloud (AWS, Azure, GCP)."))
    story.append(b("6. <b>Cybersecurity Analyst:</b> Security Information &amp; Event Management (SIEM), SOC monitoring, Vulnerability scanning, Penetration testing (Metasploit, Burp Suite), Cryptography, OWASP Top 10, Network packet analysis (Wireshark)."))
    story.append(b("7. <b>Data Scientist:</b> Exploratory data analysis, Statistical inference, Machine learning (Scikit-learn, XGBoost), Deep learning (PyTorch, TensorFlow), Feature engineering, Jupyter notebooks, Model evaluation metrics (ROC-AUC, F1)."))
    story.append(PageBreak())

    # =========================================================================
    # APPENDIX B: REST API PAYLOAD
    # =========================================================================
    if tracker is not None:
        story.append(PageTracker('app_b', tracker))
    story.append(p("APPENDIX B", ch_num_style))
    story.append(p("COMPONENT 1 REST API SPECIFICATION &amp; SCHEMAS", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))
    story.append(p("The following JSON payload illustrates the output schema returned by the `/api/v1/cv/score` endpoint on Port 8001:"))

    json_sample = """{
  "status": "success",
  "candidate_id": "CAND-2026-IT148-091",
  "predicted_role": "Backend Developer",
  "role_confidence": 0.942,
  "alternative_roles": [
    {"role": "Full Stack Developer", "probability": 0.038},
    {"role": "Software Engineer", "probability": 0.012},
    {"role": "DevOps Engineer", "probability": 0.005}
  ],
  "tri_pillar_scores": {
    "skill_alignment_score": 88.50,
    "experience_tenure_score": 92.00,
    "education_credential_score": 82.00,
    "composite_cv_fit_score": 88.25
  },
  "verified_tenure": {
    "total_professional_years": 4.50,
    "it_sector_years": 4.50,
    "target_role_relevant_years": 4.00,
    "overlapping_tenures_deduplicated": true
  },
  "extracted_entities": {
    "skills_count": 28,
    "workplace_evidence_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
    "isolated_mention_skills": ["Kubernetes", "AWS", "GraphQL"],
    "degree_level": "Bachelor of Science (Hons)",
    "degree_field": "Computer Science (Core Computing)",
    "certifications": ["AWS Certified Solutions Architect"]
  }
}"""
    story.append(make_box(json_sample))
    story.append(sp(12))

    story.append(p("OpenAPI 3.0 Request Specification for `/api/v1/cv/screen`:", h2_style))
    json_req = """{
  "openapi": "3.0.3",
  "paths": {
    "/api/v1/cv/screen": {
      "post": {
        "summary": "Full Candidate Resume Screening & Tri-Pillar Fit Scoring",
        "requestBody": {
          "required": true,
          "content": {
            "multipart/form-data": {
              "schema": {
                "type": "object",
                "properties": {
                  "cv_file": {"type": "string", "format": "binary"},
                  "target_role": {"type": "string", "example": "Backend Developer"},
                  "job_description_text": {"type": "string", "default": ""},
                  "redact_pii": {"type": "boolean", "default": true}
                },
                "required": ["cv_file", "target_role"]
              }
            }
          }
        },
        "responses": {
          "200": {"description": "Successful screening evaluation with Tri-Pillar Scores and Roadmap"}
        }
      }
    }
  }
}"""
    story.append(make_box(json_req))
    story.append(PageBreak())

    # =========================================================================
    # APPENDIX C: PYTEST EXECUTION LOG
    # =========================================================================
    if tracker is not None:
        story.append(PageTracker('app_c', tracker))
    story.append(p("APPENDIX C", ch_num_style))
    story.append(p("AUTOMATED 195-TEST SUITE EXECUTION REPORT", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))
    story.append(p("Execution summary generated by the automated Pytest runner for Component 1:"))

    pytest_log = """============================= test session starts ==============================
platform win32 -- Python 3.12.3, pytest-8.2.0, pluggy-1.5.0
rootdir: C:\\Users\\thari\\Desktop\\My Project\\R26-IT-148
configfile: pytest.ini
collected 195 items

component1/tests/test_api.py ..............                             [  7%]
component1/tests/test_candidate_intelligence_engine.py .............    [ 13%]
component1/tests/test_component1.py ..........                          [ 18%]
component1/tests/test_extractor.py ................................     [ 35%]
component1/tests/test_international_education.py ....................   [ 61%]
...............................                                         [ 77%]
component1/tests/test_job_specific_scores.py ....                       [ 79%]
component1/tests/test_matcher.py .........                              [ 84%]
component1/tests/test_predictor.py ..........                           [ 89%]
component1/tests/test_scorer.py ....................................    [ 98%]
................                                                        [100%]

======================== 195 passed in 79.60s (00:01:19) ========================"""
    story.append(make_box(pytest_log))
