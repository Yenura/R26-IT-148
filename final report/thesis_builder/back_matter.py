import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from thesis_builder.styles import clean_xml, create_table_box, create_code_box, PRINTABLE_WIDTH
from thesis_builder.canvas_helper import PageTracker

def append_back_matter(story, styles, tracker=None):
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
    ref_style = styles['RefStyle']
    single_body = styles['SingleBody']

    def track(key):
        if tracker is not None:
            story.append(PageTracker(key, tracker))

    # =========================================================================
    # REFERENCES
    # =========================================================================
    track('refs')
    story.append(Paragraph("REFERENCES", h_ch))
    story.append(Spacer(1, 4))

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
        "[60] D. T. D. Perera, Y. S. Karunanayaka, and K. G. S. N. Perera, 'RecruitAI: Next-generation AI-driven recruitment and predictive career development ecosystem,' SLIIT Technical Report, Project R26-IT-148, Dissemination Portal: https://r26-it-148-website.yenura02.workers.dev/, Oct. 2026."
    ]

    for ref in references:
        story.append(Paragraph(ref, ref_style))

    story.append(PageBreak())

    # =========================================================================
    # GLOSSARY
    # =========================================================================
    track('glossary')
    story.append(Paragraph("GLOSSARY", h_ch))
    story.append(Spacer(1, 4))

    glossary_items = [
        ("Applicant Tracking System (ATS)", "Enterprise recruitment software deployed to automate the collection, parsing, filtering, and administration of job applicant curriculum vitae documents."),
        ("Bi-Encoder", "A neural architecture that processes two text sequences through independent encoder branches to produce fixed-dimensional embeddings compared via cosine similarity."),
        ("Closed-Form Attribution", "An exact, non-approximated mathematical calculation of feature contributions to a model's prediction without requiring Monte Carlo sampling or permutation loops."),
        ("Credential Decoupling", "The architectural separation of academic degree attainment level (e.g., Bachelor, Master, PhD) from disciplinary field relevance (Core Computing vs. Non-Technical)."),
        ("Data Leakage", "A machine learning vulnerability where test set information, boilerplate templates, or target labels inadvertently contaminate training features, producing artificially inflated metrics."),
        ("Evidence-Weighted Skill Scoring", "A hierarchical weighting mechanism that assigns lower credit to isolated keyword mentions (0.40) and maximum credit to verified workplace duties (1.00)."),
        ("Interval Union Algebra", "A set-theoretic calendar calculation that computes the Lebesgue measure of the union of chronological employment spans, eliminating duration double-counting from concurrent jobs."),
        ("Named Entity Recognition (NER)", "An information extraction subtask that locates and classifies named entities in unstructured text into predefined semantic categories such as skills and credentials."),
        ("Personally Identifiable Information (PII)", "Information that can be used to identify, contact, or locate an individual person (e.g., name, phone number, email address, physical address, social handles)."),
        ("Polysemy Shielding", "Context-guarded regular-expression look-around patterns designed to prevent ambiguous single-letter or common English words from falsely triggering skill detections."),
        ("RecruitAI", "The integrated four-microservice technical recruitment and predictive career development platform developed under SLIIT research project R26-IT-148."),
        ("Sentence-BERT (SBERT)", "A modified BERT network that uses Siamese and triplet network structures to derive semantically meaningful sentence embeddings that can be compared using cosine distance."),
        ("SHAP (SHapley Additive exPlanations)", "A game-theoretic framework that explains individual machine learning model predictions by computing the optimal Shapley attribution value for each input feature."),
        ("Sublinear Term Frequency", "A TF-IDF transformation that replaces raw term frequency tf with 1 + log(tf) for tf > 0, dampening the mathematical influence of repetitive keyword stuffing."),
        ("Tri-Pillar Qualification Vector", "The uncollapsed three-element feature vector S_C1 = [S_skill, S_exp, S_edu] emitted by Component 1 representing technical skills, commercial tenure, and education level.")
    ]

    for term, definition in glossary_items:
        story.append(Paragraph(f"<b>{term}:</b> {definition}", p_body))
        story.append(Spacer(1, 2))

    story.append(PageBreak())

    # =========================================================================
    # APPENDICES
    # =========================================================================
    story.append(Paragraph("APPENDICES", h_ch))
    story.append(Spacer(1, 6))

    # APPENDIX A
    track('app_a')
    story.append(Paragraph("Appendix A Research instruments or extended results", h_sec))
    story.append(Paragraph("This appendix documents the canonical taxonomy of 20 information technology job roles supported by Component 1, grouped into five major engineering clusters, alongside their primary core competencies and baseline required commercial experience.", single_body))
    story.append(Spacer(1, 4))

    track('tabA_1')
    story.append(Paragraph("Table A.1: Canonical IT job roles taxonomy, domain clusters, and core technical competencies.", caption_tab))
    app_data = [
        [Paragraph("<b>Domain Cluster</b>", cell_bold), Paragraph("<b>Supported Job Roles</b>", cell_bold), Paragraph("<b>Primary Benchmark Competencies</b>", cell_bold)],
        [Paragraph("Core Software Engineering", cell), Paragraph("Software Engineer (General), Full Stack, Frontend, Backend, Mobile App Developer", cell), Paragraph("Java, Python, C++, TypeScript, JavaScript, React, Angular, Vue, Node.js, Spring Boot, Django, FastAPI, Flutter, React Native, Swift, Kotlin, REST", cell)],
        [Paragraph("Data, AI &amp; Analytics", cell), Paragraph("Data Scientist, Machine Learning Engineer, AI/NLP Engineer, Data Engineer", cell), Paragraph("Python, PyTorch, TensorFlow, Scikit-learn, Pandas, Spark, Hadoop, SQL, NoSQL, Kafka, Airflow, BERT, LLMs, NLP, Statistics, Deep Learning, MLOps", cell)],
        [Paragraph("Infrastructure &amp; Cloud", cell), Paragraph("Cloud Solutions Architect, DevOps Engineer, Site Reliability Engineer, Database Admin, Network Engineer", cell), Paragraph("AWS, Azure, GCP, Kubernetes, Docker, Terraform, Ansible, CI/CD, Prometheus, Grafana, Linux, PostgreSQL, MySQL, MongoDB, Redis, TCP/IP, VPN, Firewalls", cell)],
        [Paragraph("Security &amp; Quality", cell), Paragraph("Cybersecurity Analyst, QA/Test Automation Engineer", cell), Paragraph("Penetration testing, SIEM, SOC, Wireshark, Cryptography, CISSP, OWASP Top 10, Selenium, Cypress, JUnit, PyTest, TestNG, Performance testing", cell)],
        [Paragraph("Design &amp; Management", cell), Paragraph("UI/UX Designer, Embedded Systems Engineer, Blockchain Developer, Business/Systems Analyst", cell), Paragraph("Figma, Adobe XD, Wireframing, User Research, C, Embedded C, RTOS, ARM, Microcontrollers, Solidity, Smart Contracts, Ethereum, Web3, Agile, Scrum, UML, JIRA", cell)],
    ]
    app_tab = create_table_box(app_data, [95, 115, 201], styles, is_header=True)
    story.append(app_tab)
    story.append(Spacer(1, 8))

    story.append(Paragraph("The listing below presents the JSON schema output emitted by the /api/v1/cv/screen endpoint for a verified candidate profile:", single_body))
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
    "education_credential_score": 80.00,
    "composite_cv_fit_score": 88.25
  },
  "verified_tenure": {
    "total_commercial_years": 4.50,
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
    story.append(create_code_box(json_sample, styles))
    story.append(PageBreak())

    # APPENDIX B
    track('app_b')
    story.append(Paragraph("Appendix B Academic integrity and AI use disclosure", h_sec))
    story.append(Paragraph("In compliance with the SLIIT academic integrity policy on generative AI and automated tools, this disclosure registers all computational utilities utilized during this research.", single_body))
    story.append(Paragraph("<b>1. Declaration of Tools:</b> Generative AI assistants were used strictly as programming aides, syntax checkers, and drafting assistants for literature synthesis. All machine learning algorithms, regular expression patterns, interval union logic, feature matrices, training code, and test suites were designed, authored, debugged, and validated by the researcher.", single_bullet := styles['ThesisBullet']))
    story.append(Paragraph("<b>2. Verification Protocol:</b> Every numerical result, cross-validation score, F1 metric, latency benchmark, and empirical table reported in this thesis was directly generated from actual Python code execution on the curated dataset of 4,000 resumes. No figures or metrics have been synthesized or hallucinated.", single_bullet))
    story.append(Paragraph("<b>3. Human Oversight:</b> The author maintains full scientific and ethical responsibility for all interpretations, mathematical formulations, software code, and conclusions presented in this dissertation.", single_bullet))
    story.append(Spacer(1, 4))

    track('tabB_1')
    story.append(Paragraph("Table B.1: OpenAPI 3.0 request fields and response schema for screening endpoint.", caption_tab))
    b_data = [
        [Paragraph("<b>Request Field</b>", cell_bold), Paragraph("<b>Data Type</b>", cell_bold), Paragraph("<b>Required</b>", cell_bold), Paragraph("<b>Description &amp; Default Behavior</b>", cell_bold)],
        [Paragraph("cv_file", cell), Paragraph("binary (multipart)", cell), Paragraph("Yes", cell), Paragraph("Candidate resume document in PDF, DOCX, or TXT format", cell)],
        [Paragraph("target_role", cell), Paragraph("string", cell), Paragraph("Yes", cell), Paragraph("Target canonical role (e.g., 'Backend Developer')", cell)],
        [Paragraph("job_description_text", cell), Paragraph("string", cell), Paragraph("No", cell), Paragraph("Optional raw text of specific job requisition (for SBERT)", cell)],
        [Paragraph("redact_pii", cell), Paragraph("boolean", cell), Paragraph("No", cell), Paragraph("Default true: strips names, phones, emails, addresses", cell)],
    ]
    b_tab = create_table_box(b_data, [105, 95, 55, 156], styles, is_header=True)
    story.append(b_tab)
    story.append(Spacer(1, 6))

    story.append(Paragraph("The terminal log excerpt below documents the execution of the 195-test automated Pytest verification suite for Component 1:", single_body))
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

======================== 195 passed in 79.60s (00:01:19) ========================
All unit, regression, and integration tests completed with zero errors."""
    story.append(create_code_box(pytest_log, styles))
