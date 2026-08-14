"""Component 1 — NLP skill/experience/education extraction and role configs."""

import re

TECH_FIELDS = [
    "computer", "software", "information", "data", "machine", "intelligence",
    "artificial", "engineering", "science", "mathematics", "statistics",
    "security", "network", "electronics", "electrical", "cloud",
]

SKILLS_LEXICON = [
    "Data Structures & Algorithms", "PyTorch/TensorFlow", "Cloud Solutions", "Network Security",
    "Penetration Testing", "Responsive Design", "Cost Optimization", "Backup & Recovery",
    "Incident Response", "Query Optimization", "Architecture Design", "Feature Engineering",
    "Machine Learning", "Deep Learning", "Microservices", "Web Performance", "AWS/Azure/GCP",
    "iOS/Android", "React Native", "React", "Python", "Java", "JavaScript", "TypeScript",
    "Kubernetes", "Terraform", "Docker", "Jenkins", "Ansible", "Linux", "Bash",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "BigQuery", "Kafka",
    "Databricks", "Flutter", "Dart", "Swift", "Kotlin", "Firebase", "Node.js",
    "HTML/CSS", "CSS", "HTML", "REST APIs", "GraphQL", "WebSockets", "Git", "SQL",
    "OOP", "Statistics", "Pandas", "NumPy", "Matplotlib", "Jupyter", "TensorFlow",
    "PyTorch", "Scikit-learn", "MLOps", "MLflow", "SIEM", "Firewalls", "IDS/IPS",
    "OWASP", "AWS", "Azure", "GCP", "Pulumi", "Istio", "Prometheus", "C++", "C#",
    "Go", "R", "RabbitMQ", "System Design", "CI/CD", "Accessibility", "Replication",
]

EDUCATION_PATTERNS = [
    (4, [r"\bph\.?d\b", r"\bdoctorate\b", r"doctor of philosophy"]),
    (3, [r"\bm\.?s\b", r"\bm\.?sc\b", r"\bmaster(?:'?s| of)?\b", r"\bm\.?eng\b",
         r"\bm\.?ba\b", r"\bmtech\b", r"\bm\.?tech\b"]),
    (2, [r"\bb\.?s\b", r"\bb\.?sc\b", r"\bbachelor(?:'?s| of)?\b", r"\bb\.?eng\b",
         r"\bb\.?tech\b", r"\bb\.?ba\b", r"\bundergraduate\b", r"\bdegree\b"]),
    (1, [r"\bdiploma\b", r"\bhnd\b", r"\bcertificate\b", r"\bassociate\b", r"\bfoundation\b"]),
]

YEARS_PATTERNS = [
    r"(\d+(?:\.\d+)?)[ \t]*\+?[ \t]*(?:years|year|yrs|yr)\b",
    r"(\d+(?:\.\d+)?)[ \t]*\+?[ \t]*(?:years|yrs)[ \t]*(?:of|of relevant|) experience",
]


def extract_skills(text: str):
    text_l = text.lower()
    matched = []
    for phrase in sorted(SKILLS_LEXICON, key=len, reverse=True):
        p = phrase.lower()
        if len(p) < 4:
            if re.search(r"\b" + re.escape(p) + r"\b", text_l):
                matched.append(phrase)
        elif p in text_l:
            matched.append(phrase)
    seen, out = set(), []
    for s in matched:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def extract_experience_years(text: str):
    best = 0.0
    for pat in YEARS_PATTERNS:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            try:
                v = float(m.group(1))
            except (ValueError, TypeError):
                continue
            if v > best:
                best = v
    return min(best, 40.0)


def extract_education(text: str):
    text_l = text.lower()
    for level, pats in EDUCATION_PATTERNS:
        for pat in pats:
            m = re.search(pat, text_l)
            if m:
                field_matches = [f for f in TECH_FIELDS if f in text_l]
                return level, field_matches
    return 1, []


def education_relevance(level, fields, role):
    role_field_hints = {
        "Software_Engineer": ["software", "computer", "engineering"],
        "Data_Scientist": ["data", "statistics", "mathematics", "machine"],
        "Machine_Learning_Engineer": ["machine", "data", "computer", "intelligence"],
        "DevOps_Engineer": ["computer", "information", "network"],
        "Cybersecurity_Analyst": ["security", "network", "computer"],
        "Cloud_Solutions_Architect": ["computer", "information", "network", "cloud"],
        "Database_Administrator": ["computer", "information", "data"],
        "Frontend_Developer": ["software", "computer", "engineering"],
        "Backend_Developer": ["software", "computer", "engineering"],
        "Mobile_App_Developer": ["software", "computer", "engineering"],
        "Full_Stack_Developer": ["software", "computer", "engineering"],
        "QA_Test_Automation_Engineer": ["software", "computer", "engineering"],
        "Data_Engineer": ["data", "computer", "information"],
        "Site_Reliability_Engineer": ["computer", "information", "network"],
        "UI_UX_Designer": ["design", "art", "engineering"],
        "Network_Engineer": ["network", "electronics", "electrical"],
        "Business_Systems_Analyst": ["business", "information", "engineering"],
        "AI_NLP_Engineer": ["artificial", "intelligence", "machine", "data"],
        "Blockchain_Developer": ["computer", "software", "engineering"],
        "Embedded_Systems_Engineer": ["electronics", "electrical", "engineering"],
    }
    hints = role_field_hints.get(role, TECH_FIELDS)
    if any(h in fields for h in hints):
        return 1.0
    if fields:
        return 0.75
    return 0.6


ROLES = [
    "Software_Engineer", "Data_Scientist", "Machine_Learning_Engineer",
    "DevOps_Engineer", "Cybersecurity_Analyst", "Cloud_Solutions_Architect",
    "Database_Administrator", "Frontend_Developer", "Backend_Developer",
    "Mobile_App_Developer", "Full_Stack_Developer", "QA_Test_Automation_Engineer",
    "Data_Engineer", "Site_Reliability_Engineer", "UI_UX_Designer",
    "Network_Engineer", "Business_Systems_Analyst", "AI_NLP_Engineer",
    "Blockchain_Developer", "Embedded_Systems_Engineer",
]

JOBS_DEFAULT = {
    role: {
        "required_skills": [
            s.strip() for s in REQUIRED_SKILLS_TEXT.split(",")
            if s.strip()
        ],
        "required_years": REQUIRED_YEARS,
        "min_edu": MIN_EDU,
        "w_edu": W_EDU,
        "w_exp": W_EXP,
        "w_skill": W_SKILL,
    }
    for role, (REQUIRED_SKILLS_TEXT, REQUIRED_YEARS, MIN_EDU, W_EDU, W_EXP, W_SKILL) in {
        "Software_Engineer": (
            "Python, Java, C++, Data Structures, Algorithms, REST APIs, Git, OOP, SQL",
            3.0, 2, 0.20, 0.30, 0.50),
        "Data_Scientist": (
            "Python, R, Statistics, Machine Learning, Pandas, NumPy, Matplotlib, SQL, Jupyter",
            2.5, 3, 0.30, 0.30, 0.40),
        "Machine_Learning_Engineer": (
            "Python, TensorFlow, PyTorch, Scikit-learn, Deep Learning, MLOps, Docker, SQL",
            3.0, 3, 0.25, 0.30, 0.45),
        "DevOps_Engineer": (
            "Linux, Docker, Kubernetes, CI/CD, Jenkins, Terraform, AWS/Azure, Bash, Ansible",
            4.0, 2, 0.15, 0.40, 0.45),
        "Cybersecurity_Analyst": (
            "Network Security, SIEM, Penetration Testing, Firewalls, IDS/IPS, Python, OWASP",
            3.0, 2, 0.20, 0.35, 0.45),
        "Cloud_Solutions_Architect": (
            "AWS/Azure/GCP, Terraform, Kubernetes, Microservices, Networking, Security, Cost Optimization",
            5.0, 2, 0.20, 0.40, 0.40),
        "Database_Administrator": (
            "SQL, PostgreSQL, MySQL, MongoDB, Query Optimization, Backup & Recovery, Replication",
            3.0, 2, 0.20, 0.40, 0.40),
        "Frontend_Developer": (
            "HTML, CSS, JavaScript, React, TypeScript, Responsive Design, REST APIs, Git",
            2.0, 2, 0.15, 0.30, 0.55),
        "Backend_Developer": (
            "Python/Java/Node.js, REST APIs, SQL, Microservices, Docker, Redis, Git",
            3.0, 2, 0.20, 0.30, 0.50),
        "Mobile_App_Developer": (
            "iOS/Android, Flutter, React Native, Dart, Swift/Kotlin, Firebase, REST APIs",
            2.5, 2, 0.15, 0.30, 0.55),
        "Full_Stack_Developer": (
            "React, Node.js, Python, SQL, REST APIs, Docker, Git, HTML/CSS, TypeScript",
            3.0, 2, 0.15, 0.30, 0.55),
        "QA_Test_Automation_Engineer": (
            "Selenium, Pytest, Jest, CI/CD, API Testing, Test Strategy, Python, Postman",
            2.0, 2, 0.15, 0.35, 0.50),
        "Data_Engineer": (
            "Python, SQL, Spark, Kafka, Airflow, ETL, AWS/GCP, Data Modeling, Hadoop",
            3.0, 2, 0.20, 0.35, 0.45),
        "Site_Reliability_Engineer": (
            "Linux, Kubernetes, Prometheus, Grafana, Terraform, Python, Go, CI/CD, Incident Response",
            4.0, 2, 0.15, 0.40, 0.45),
        "UI_UX_Designer": (
            "Figma, Sketch, Adobe XD, CSS, HTML, Prototyping, User Research, Wireframing, Accessibility",
            2.0, 2, 0.20, 0.25, 0.55),
        "Network_Engineer": (
            "TCP/IP, Cisco, Routing, Switching, Firewalls, VPN, DNS, Linux, Python",
            3.0, 2, 0.20, 0.35, 0.45),
        "Business_Systems_Analyst": (
            "SQL, Requirements Gathering, UML, BPMN, Stakeholder Management, Agile, JIRA, Data Analysis",
            3.0, 2, 0.25, 0.35, 0.40),
        "AI_NLP_Engineer": (
            "Python, TensorFlow, PyTorch, NLP, Transformers, Hugging Face, spaCy, Deep Learning",
            3.0, 3, 0.25, 0.30, 0.45),
        "Blockchain_Developer": (
            "Solidity, Ethereum, Web3.js, Smart Contracts, Rust, C++, Cryptography, DApps",
            2.5, 2, 0.15, 0.30, 0.55),
        "Embedded_Systems_Engineer": (
            "C, C++, Rust, RTOS, Microcontrollers, ARM, Linux Kernel, Communication Protocols",
            3.0, 2, 0.20, 0.35, 0.45),
    }.items()
}

EDU_LEVEL_SCORES = {1: 0.40, 2: 0.60, 3: 0.80, 4: 1.00}
EDU_LEVEL_NAMES = {1: "Diploma", 2: "BSc", 3: "MSc", 4: "PhD"}
