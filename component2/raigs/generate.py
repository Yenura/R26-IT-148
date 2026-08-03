"""
RAIGS Question Dataset Generator
Generates MCQ / Descriptive / Coding questions across 20 IT roles x 3 levels
(Intern / Associate / Senior) using topic-bank + template combinatorial generation.

This mirrors the existing template-expansion approach used in ml/data_loader.py
(MCQ templates 5->30, coding templates 3->15) but scaled to hit the volumes
defined in RAIGS_question_taxonomy.csv.
"""
import csv
import itertools
import json
import random

random.seed(42)

# ---------------------------------------------------------------------------
# ROLE DEFINITIONS: topics list per role (used across MCQ/Descriptive/Coding)
# ---------------------------------------------------------------------------
ROLES = {
    "Software Engineer": dict(coding=True, topics=[
        "object-oriented design", "design patterns", "SOLID principles", "unit testing",
        "version control workflows", "code review practices", "REST API design",
        "data structures", "algorithm complexity", "memory management", "concurrency",
        "debugging strategies", "software architecture", "dependency injection",
        "clean code principles", "refactoring", "continuous integration",
        "exception handling", "logging and monitoring", "technical debt",
        "microservices vs monoliths", "API versioning", "caching strategies",
        "database indexing", "message queues", "load balancing", "code documentation",
        "test-driven development", "static code analysis", "build tools",
    ]),
    "Data Scientist": dict(coding=True, topics=[
        "exploratory data analysis", "hypothesis testing", "regression analysis",
        "feature engineering", "data cleaning", "statistical significance",
        "A/B testing", "clustering algorithms", "dimensionality reduction",
        "model evaluation metrics", "bias-variance tradeoff", "cross-validation",
        "data visualization principles", "time series analysis", "sampling methods",
        "outlier detection", "correlation vs causation", "data pipelines",
        "SQL for analytics", "probability distributions", "confidence intervals",
        "experiment design", "data storytelling", "missing data imputation",
        "predictive modeling", "Bayesian inference", "data ethics", "cohort analysis",
        "big data tools", "reporting dashboards",
    ]),
    "Machine Learning Engineer": dict(coding=True, topics=[
        "supervised vs unsupervised learning", "neural network architectures",
        "gradient descent optimization", "overfitting and regularization",
        "model deployment pipelines", "feature scaling", "hyperparameter tuning",
        "ensemble methods", "convolutional neural networks", "recurrent neural networks",
        "transformer architectures", "transfer learning", "model versioning",
        "MLOps practices", "model monitoring in production", "data drift detection",
        "loss functions", "activation functions", "batch normalization",
        "model compression", "distributed training", "vector embeddings",
        "reinforcement learning basics", "explainable AI", "ML pipeline orchestration",
        "GPU acceleration", "model serving frameworks", "A/B testing for models",
        "fairness in ML models", "attention mechanisms",
    ]),
    "DevOps Engineer": dict(coding=True, topics=[
        "CI/CD pipelines", "containerization with Docker", "Kubernetes orchestration",
        "infrastructure as code", "configuration management", "monitoring and alerting",
        "log aggregation", "blue-green deployments", "canary releases",
        "auto-scaling strategies", "secrets management", "service mesh",
        "disaster recovery planning", "cloud cost optimization", "GitOps workflows",
        "artifact repositories", "shell scripting", "network configuration",
        "load balancer setup", "incident response", "SLA/SLO/SLI definitions",
        "immutable infrastructure", "rolling deployments", "container security",
        "Terraform/CloudFormation", "build automation", "chaos engineering",
        "observability practices", "on-call practices", "environment parity",
    ]),
    "Cloud Solutions Architect": dict(coding=True, topics=[
        "cloud service models (IaaS/PaaS/SaaS)", "multi-cloud strategy",
        "cloud migration planning", "high availability design", "disaster recovery",
        "cost optimization strategies", "cloud networking (VPC/subnets)",
        "identity and access management", "serverless architecture",
        "auto-scaling design", "data residency and compliance", "cloud storage tiers",
        "hybrid cloud architecture", "cloud security posture", "well-architected framework",
        "landing zone design", "cloud-native patterns", "event-driven architecture",
        "API gateway design", "content delivery networks", "cloud governance",
        "resource tagging strategy", "capacity planning", "cloud SLA management",
        "vendor lock-in mitigation", "infrastructure automation", "edge computing",
        "cloud backup strategies", "network peering", "cloud monitoring tools",
    ]),
    "Database Administrator": dict(coding=True, topics=[
        "normalization and denormalization", "indexing strategies", "query optimization",
        "backup and recovery", "replication strategies", "sharding", "transaction isolation levels",
        "database security", "stored procedures", "database migrations",
        "performance tuning", "deadlock handling", "ACID properties", "connection pooling",
        "partitioning strategies", "high availability clustering", "data warehousing basics",
        "NoSQL vs SQL tradeoffs", "capacity planning", "database monitoring",
        "disaster recovery planning", "schema design", "vacuum/maintenance operations",
        "read replicas", "database versioning", "encryption at rest", "role-based access control",
        "query execution plans", "database auditing", "data archiving strategies",
    ]),
    "Frontend Developer": dict(coding=True, topics=[
        "responsive design", "component-based architecture", "state management",
        "CSS layout systems (flexbox/grid)", "accessibility (a11y)", "browser rendering pipeline",
        "performance optimization", "cross-browser compatibility", "client-side routing",
        "form validation", "DOM manipulation", "web accessibility standards",
        "progressive web apps", "lazy loading", "frontend build tools",
        "CSS preprocessors", "component testing", "design systems",
        "web performance metrics", "hooks and lifecycle methods", "event handling",
        "browser storage (local/session)", "SEO fundamentals for frontend", "animation performance",
        "code splitting", "TypeScript in frontend", "internationalization", "theming systems",
        "web security (XSS/CSRF)", "micro-frontends",
    ]),
    "Backend Developer": dict(coding=True, topics=[
        "API design principles", "authentication and authorization", "database schema design",
        "caching layers", "rate limiting", "message queue integration", "server-side validation",
        "error handling strategies", "logging and observability", "session management",
        "middleware architecture", "background job processing", "webhooks",
        "API security best practices", "database connection management", "scalability patterns",
        "idempotency in APIs", "pagination strategies", "data serialization",
        "microservices communication", "transaction management", "input sanitization",
        "load testing", "service versioning", "dependency management",
        "environment configuration", "graceful shutdown handling", "health check endpoints",
        "API documentation", "rate of change management",
    ]),
    "Mobile App Developer": dict(coding=True, topics=[
        "mobile UI design principles", "app lifecycle management", "state management in mobile",
        "offline-first architecture", "push notifications", "mobile performance optimization",
        "cross-platform frameworks", "native vs hybrid development", "app store deployment",
        "mobile security practices", "local data storage", "battery optimization",
        "responsive layouts for mobile", "gesture handling", "background task management",
        "API integration in mobile apps", "mobile testing strategies", "crash reporting",
        "app permissions handling", "deep linking", "mobile CI/CD",
        "memory management on mobile", "accessibility on mobile", "biometric authentication",
        "in-app purchases", "mobile analytics", "app versioning strategy",
        "network handling on mobile", "UI animation on mobile", "app localization",
    ]),
    "Full Stack Developer": dict(coding=True, topics=[
        "end-to-end application architecture", "frontend-backend integration",
        "REST vs GraphQL APIs", "authentication flows across stack", "state management across layers",
        "database design for full stack apps", "deployment pipelines for full stack apps",
        "monorepo vs polyrepo", "server-side rendering", "API contract design",
        "full stack testing strategy", "environment configuration management",
        "session and token management", "caching across layers", "error handling end-to-end",
        "responsive UI with backend constraints", "websocket integration",
        "build and bundling tools", "full stack security practices", "third-party API integration",
        "data validation across layers", "performance profiling full stack",
        "developer tooling setup", "CI/CD for full stack apps", "feature flag management",
        "logging across the stack", "scalability considerations", "code organization patterns",
        "full stack debugging techniques", "documentation across teams",
    ]),
    "QA/Test Automation Engineer": dict(coding=True, topics=[
        "test case design", "test automation frameworks", "regression testing strategy",
        "unit vs integration vs e2e testing", "test data management", "bug lifecycle management",
        "exploratory testing", "performance testing", "API testing", "UI test automation",
        "continuous testing in CI/CD", "test coverage analysis", "mocking and stubbing",
        "cross-browser testing", "mobile testing strategy", "load and stress testing",
        "test reporting", "risk-based testing", "boundary value analysis",
        "equivalence partitioning", "test environment management", "flaky test management",
        "accessibility testing", "security testing basics", "smoke and sanity testing",
        "test plan documentation", "defect triage process", "test automation ROI",
        "behavior-driven development", "shift-left testing",
    ]),
    "Data Engineer": dict(coding=True, topics=[
        "ETL pipeline design", "data warehousing concepts", "data lake architecture",
        "batch vs streaming processing", "data modeling", "data quality assurance",
        "workflow orchestration", "schema evolution", "partitioning strategies for big data",
        "data pipeline monitoring", "distributed computing frameworks", "data ingestion strategies",
        "data governance", "columnar storage formats", "data pipeline testing",
        "SQL performance tuning", "data lineage tracking", "incremental data loading",
        "data pipeline scalability", "message broker integration", "data pipeline security",
        "metadata management", "data deduplication", "backfilling strategies",
        "cost optimization for data pipelines", "data catalog design", "real-time data processing",
        "data pipeline error handling", "data serialization formats", "capacity planning for pipelines",
    ]),
    "Site Reliability Engineer (SRE)": dict(coding=True, topics=[
        "service level objectives", "error budgets", "incident management process",
        "postmortem culture", "on-call rotation design", "toil reduction",
        "capacity planning", "chaos engineering practices", "monitoring and alerting design",
        "automation for reliability", "load shedding strategies", "circuit breaker patterns",
        "distributed systems reliability", "root cause analysis", "runbook creation",
        "system observability", "graceful degradation", "failover strategies",
        "rate limiting for reliability", "dependency mapping", "reliability testing",
        "SLI/SLA definition", "escalation policies", "production readiness reviews",
        "performance regression detection", "infrastructure resilience", "backup verification",
        "deployment risk mitigation", "resource utilization monitoring", "self-healing systems",
    ]),
    "Cybersecurity Analyst": dict(coding=False, topics=[
        "threat intelligence", "vulnerability assessment", "incident response process",
        "security information and event management (SIEM)", "phishing detection",
        "network security fundamentals", "malware analysis basics", "penetration testing concepts",
        "security compliance frameworks", "risk assessment methodology", "access control models",
        "encryption fundamentals", "security awareness training", "endpoint security",
        "firewall configuration principles", "intrusion detection systems", "data loss prevention",
        "zero trust architecture", "security auditing", "identity and access management",
        "social engineering tactics", "security policy development", "digital forensics basics",
        "cloud security fundamentals", "patch management", "security incident triage",
        "regulatory compliance (GDPR/HIPAA)", "insider threat detection", "security metrics reporting",
        "disaster recovery for security incidents",
    ]),
    "UI/UX Designer": dict(coding=False, topics=[
        "user research methods", "wireframing and prototyping", "usability testing",
        "information architecture", "interaction design principles", "design systems",
        "accessibility in design", "user personas", "user journey mapping",
        "visual hierarchy", "color theory in UI", "typography principles",
        "responsive design principles", "design critique process", "A/B testing for design",
        "heuristic evaluation", "card sorting", "design handoff to developers",
        "mobile-first design", "onboarding flow design", "empathy mapping",
        "design thinking process", "microinteractions", "dark patterns and ethics",
        "design tool workflows", "content strategy in UX", "user feedback loops",
        "conversion-focused design", "inclusive design principles", "brand consistency in design",
    ]),
    "Network Engineer": dict(coding=True, topics=[
        "OSI model layers", "TCP/IP fundamentals", "routing protocols",
        "switching concepts", "VLAN configuration", "network security basics",
        "firewall rules design", "load balancing for networks", "VPN configuration",
        "DNS configuration", "DHCP management", "network monitoring tools",
        "bandwidth management", "network troubleshooting methodology", "wireless network design",
        "SD-WAN concepts", "network redundancy design", "QoS configuration",
        "subnetting and IP addressing", "network access control", "packet analysis",
        "BGP/OSPF routing", "network automation scripting", "network capacity planning",
        "cloud networking integration", "network documentation practices", "latency troubleshooting",
        "network segmentation", "port security", "IPv6 transition strategies",
    ]),
    "Business/Systems Analyst": dict(coding=False, topics=[
        "requirements gathering techniques", "stakeholder management", "business process modeling",
        "gap analysis", "use case documentation", "user story writing",
        "SWOT analysis", "cost-benefit analysis", "data flow diagrams",
        "system requirements specification", "change management process", "risk analysis",
        "agile vs waterfall methodologies", "process improvement techniques", "root cause analysis",
        "stakeholder interviews", "business rules documentation", "functional vs non-functional requirements",
        "UAT planning", "prioritization frameworks (MoSCoW)", "workflow diagramming",
        "KPI definition", "feasibility studies", "vendor evaluation criteria",
        "system integration analysis", "documentation standards", "business case development",
        "requirements traceability matrix", "process automation opportunities", "reporting and analytics needs",
    ]),
    "AI/NLP Engineer": dict(coding=True, topics=[
        "tokenization strategies", "word embeddings", "language model architectures",
        "named entity recognition", "sentiment analysis techniques", "text classification",
        "sequence-to-sequence models", "attention mechanisms", "transformer fine-tuning",
        "prompt engineering", "retrieval-augmented generation", "text summarization techniques",
        "part-of-speech tagging", "language model evaluation metrics", "bias in language models",
        "few-shot and zero-shot learning", "text preprocessing pipelines", "semantic search",
        "conversational AI design", "model distillation for NLP", "multilingual NLP challenges",
        "hallucination mitigation", "NLP model deployment", "vector databases for NLP",
        "text generation quality evaluation", "speech-to-text integration", "NLP data annotation",
        "context window management", "NLP model latency optimization", "ethical considerations in NLP",
    ]),
    "Blockchain Developer": dict(coding=True, topics=[
        "smart contract development", "consensus mechanisms", "blockchain architecture fundamentals",
        "gas optimization", "token standards (ERC-20/ERC-721)", "decentralized application design",
        "blockchain security vulnerabilities", "wallet integration", "cross-chain interoperability",
        "blockchain scalability solutions", "cryptographic hashing", "public vs private blockchains",
        "smart contract testing", "oracles in blockchain", "decentralized finance concepts",
        "blockchain node setup", "transaction fee mechanisms", "smart contract upgradeability",
        "blockchain governance models", "NFT development", "layer 2 scaling solutions",
        "blockchain data storage tradeoffs", "reentrancy attack prevention", "blockchain auditing practices",
        "sharding in blockchain", "distributed ledger concepts", "web3 integration",
        "blockchain regulatory considerations", "signature verification", "blockchain deployment pipelines",
    ]),
    "Embedded Systems Engineer": dict(coding=True, topics=[
        "microcontroller architecture", "real-time operating systems", "firmware development",
        "interrupt handling", "memory-constrained programming", "hardware-software interfacing",
        "communication protocols (I2C/SPI/UART)", "power management design", "embedded debugging techniques",
        "bootloader design", "sensor integration", "embedded security practices",
        "circuit-level troubleshooting", "embedded C programming practices", "device driver development",
        "watchdog timers", "embedded testing strategies", "signal processing basics",
        "PCB design fundamentals", "low-level memory management", "cross-compilation toolchains",
        "embedded system scalability", "firmware update mechanisms (OTA)", "real-time scheduling",
        "hardware abstraction layers", "embedded system power optimization", "fault tolerance in embedded systems",
        "sensor calibration", "embedded network protocols", "embedded system documentation",
    ]),
}

LEVELS = [
    ("Intern", 0.30, "at a foundational, learning-focused level suited for an intern who is building core understanding"),
    ("Associate", 0.40, "at a practical, applied level suited for an associate who handles real production tasks independently"),
    ("Senior", 0.30, "at an advanced, strategic level suited for a senior professional who owns architecture, tradeoffs, and mentorship"),
]

MCQ_TEMPLATES = [
    "Which of the following best describes {topic}?",
    "In the context of {role} work, what is the primary purpose of {topic}?",
    "Which statement about {topic} is most accurate?",
    "What is a key characteristic of {topic}?",
    "When applying {topic}, which of the following is a best practice?",
    "Which option correctly explains a common pitfall related to {topic}?",
    "What is the main benefit of using {topic} in a {role} context?",
    "Which of the following is NOT typically associated with {topic}?",
]

DESCRIPTIVE_TEMPLATES = [
    "Explain the concept of {topic} and why it matters {level_phrase}.",
    "Describe how you would approach {topic} {level_phrase}.",
    "What are the key considerations when working with {topic}, {level_phrase}?",
    "Walk through a real scenario where {topic} would be critical, {level_phrase}.",
    "Compare the tradeoffs involved in {topic} {level_phrase}.",
    "How would you troubleshoot an issue related to {topic}, {level_phrase}?",
    "What best practices would you apply when dealing with {topic}, {level_phrase}?",
    "Explain a mistake to avoid when working with {topic}, {level_phrase}.",
    "How does {topic} impact overall system/product quality, {level_phrase}?",
    "Describe how you would explain {topic} to a non-technical stakeholder.",
    "What metrics or signals would you use to evaluate {topic}?",
    "How would your approach to {topic} differ across team sizes or project scales?",
]

CODING_TEMPLATES = [
    "Write a function/program that demonstrates or applies {topic}.",
    "Implement a small module that solves a problem related to {topic}.",
    "Given a scenario involving {topic}, write code to handle it correctly, including edge cases.",
    "Write a script that automates a task related to {topic}.",
    "Debug and fix a piece of code with a common issue related to {topic}.",
    "Implement a test suite validating correct behavior for {topic}.",
]


def build_rows():
    rows = []
    qid = 1
    for role, cfg in ROLES.items():
        topics = cfg["topics"]
        coding_enabled = cfg["coding"]
        for level, pct, level_phrase in LEVELS:
            if coding_enabled:
                mcq_n, desc_n, code_n = round(150 * pct), round(700 * pct), round(150 * pct)
            else:
                mcq_n, desc_n, code_n = round(200 * pct), round(800 * pct), 0

            # MCQ
            mcq_pool = list(itertools.product(topics, MCQ_TEMPLATES))
            random.shuffle(mcq_pool)
            mcq_cycled = list(itertools.islice(itertools.cycle(mcq_pool), mcq_n))
            for i, (topic, tmpl) in enumerate(mcq_cycled):
                text = tmpl.format(topic=topic, role=role)
                if i >= len(mcq_pool):
                    text += f" (variant {i // len(mcq_pool) + 1})"
                options = [
                    {"index": 0, "text": f"Correct application of {topic}"},
                    {"index": 1, "text": f"A common misconception about {topic}"},
                    {"index": 2, "text": f"An unrelated concept to {topic}"},
                    {"index": 3, "text": f"A partially correct but incomplete view of {topic}"},
                ]
                rows.append([qid, role, level, "mcq", text, json.dumps(options), 0, topic])
                qid += 1

            # Descriptive
            desc_pool = list(itertools.product(topics, DESCRIPTIVE_TEMPLATES))
            random.shuffle(desc_pool)
            desc_cycled = list(itertools.islice(itertools.cycle(desc_pool), desc_n))
            for i, (topic, tmpl) in enumerate(desc_cycled):
                text = tmpl.format(topic=topic, role=role, level_phrase=level_phrase)
                if i >= len(desc_pool):
                    text += f" (variant {i // len(desc_pool) + 1})"
                rows.append([qid, role, level, "descriptive", text, "", "", topic])
                qid += 1

            # Coding
            if coding_enabled and code_n > 0:
                code_pool = list(itertools.product(topics, CODING_TEMPLATES))
                random.shuffle(code_pool)
                code_cycled = list(itertools.islice(itertools.cycle(code_pool), code_n))
                for i, (topic, tmpl) in enumerate(code_cycled):
                    text = tmpl.format(topic=topic, role=role)
                    if i >= len(code_pool):
                        text += f" (variant {i // len(code_pool) + 1})"
                    rows.append([qid, role, level, "coding", text, "", "", topic])
                    qid += 1
    return rows


if __name__ == "__main__":
    rows = build_rows()
    out_path = "/mnt/user-data/outputs/RAIGS_generated_questions.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "role", "level", "type", "question_text", "options_json", "correct_answer_index", "topic"])
        writer.writerows(rows)
    print(f"Total rows generated: {len(rows)}")
    print(f"Saved to {out_path}")
