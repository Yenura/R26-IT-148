"""
Role Requirements — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Canonical 20-role requirement table used for scoring.

Integration notes
-----------------
* Role names are taken verbatim from component2/raigs/generate.py (ROLES dict keys).
* EDU_LEVEL_SCORES mirrors component3/data/role_configs.py exactly.
* REQUIRED_YEARS for the 10 overlapping roles mirrors component3 exactly so that
  S_exp scores are identical regardless of which component produces them.
* The 10 NEW roles (not in component3) define their own REQUIRED_YEARS and
  REQUIRED_SKILLS; these are documented in the README.
"""

from typing import Dict, List

# ── Education level scores (mirrors component3/data/role_configs.py) ───────────
EDU_LEVEL_SCORES: Dict[int, float] = {1: 0.40, 2: 0.60, 3: 0.80, 4: 1.00}
EDU_LEVEL_NAMES:  Dict[int, str]   = {1: "Diploma", 2: "BSc", 3: "MSc", 4: "PhD"}

# ── Required years of experience per role ──────────────────────────────────────
# Roles 1-10 (component3 overlap): values are identical to component3 REQUIRED_YEARS.
# Roles 11-20 (new): defined below with documented rationale.
REQUIRED_YEARS: Dict[str, float] = {
    # ── Component-3 aligned (10 roles) ────────────────────────────────────────
    "Software Engineer":          3.0,   # component3: Software_Engineer
    "Data Scientist":             2.5,   # component3: Data_Scientist
    "Machine Learning Engineer":  3.0,   # component3: Machine_Learning_Engineer
    "DevOps Engineer":            4.0,   # component3: DevOps_Engineer
    "Cloud Solutions Architect":  5.0,   # component3: Cloud_Solutions_Architect
    "Database Administrator":     3.0,   # component3: Database_Administrator
    "Frontend Developer":         2.0,   # component3: Frontend_Developer
    "Backend Developer":          3.0,   # component3: Backend_Developer
    "Mobile App Developer":       2.5,   # component3: Mobile_App_Developer
    "Cybersecurity Analyst":      3.0,   # component3: Cybersecurity_Analyst
    # ── New roles (10 roles) ───────────────────────────────────────────────────
    "Full Stack Developer":        3.0,   # Comparable to Backend Developer
    "QA/Test Automation Engineer": 2.5,   # Moderate; automation tooling learnable quickly
    "Data Engineer":               3.5,   # Pipeline expertise takes time to build
    "Site Reliability Engineer (SRE)": 4.0, # Operational maturity; similar to DevOps
    "UI/UX Designer":              2.5,   # Portfolio-driven; 2-3 years typical expectation
    "Network Engineer":            3.5,   # Certifications (CCNA/CCNP) + hands-on time
    "Business/Systems Analyst":    3.0,   # Domain knowledge accumulation
    "AI/NLP Engineer":             3.0,   # NLP specialisation; graduate-level entry common
    "Blockchain Developer":        3.0,   # Niche; similar depth to ML Engineer
    "Embedded Systems Engineer":   4.0,   # Hardware-software co-design; steep ramp
}

# ── Required skills per role ───────────────────────────────────────────────────
# Lists are used for skill matching: S_skill = matched / total_required.
# Skill strings are lower-cased during matching; keep them lower-case here.
REQUIRED_SKILLS: Dict[str, List[str]] = {
    # ── Component-3 aligned (derived from component3 ROLE_REQUIRED_SKILLS) ───
    "Software Engineer": [
        "python", "java", "c++", "data structures", "algorithms",
        "rest apis", "git", "oop", "sql", "unit testing",
    ],
    "Data Scientist": [
        "python", "r", "statistics", "machine learning", "pandas",
        "numpy", "matplotlib", "sql", "jupyter", "data cleaning",
    ],
    "Machine Learning Engineer": [
        "python", "tensorflow", "pytorch", "scikit-learn", "deep learning",
        "mlops", "docker", "sql", "model deployment", "feature engineering",
    ],
    "DevOps Engineer": [
        "linux", "docker", "kubernetes", "ci/cd", "jenkins",
        "terraform", "aws", "bash", "ansible", "monitoring",
    ],
    "Cloud Solutions Architect": [
        "aws", "azure", "gcp", "terraform", "kubernetes",
        "microservices", "networking", "iam", "serverless", "cost optimisation",
    ],
    "Database Administrator": [
        "sql", "postgresql", "mysql", "mongodb", "query optimisation",
        "backup", "replication", "indexing", "performance tuning", "transactions",
    ],
    "Frontend Developer": [
        "html", "css", "javascript", "react", "typescript",
        "responsive design", "rest apis", "git", "accessibility", "webpack",
    ],
    "Backend Developer": [
        "python", "java", "node.js", "rest apis", "sql",
        "microservices", "docker", "redis", "git", "authentication",
    ],
    "Mobile App Developer": [
        "flutter", "react native", "dart", "swift", "kotlin",
        "firebase", "rest apis", "ios", "android", "app lifecycle",
    ],
    "Cybersecurity Analyst": [
        "network security", "siem", "penetration testing", "firewalls",
        "intrusion detection", "python", "owasp", "vulnerability assessment",
        "threat intelligence", "iam",
    ],
    # ── New roles ─────────────────────────────────────────────────────────────
    "Full Stack Developer": [
        "javascript", "react", "node.js", "python", "sql",
        "rest apis", "graphql", "docker", "git", "css",
    ],
    "QA/Test Automation Engineer": [
        "selenium", "pytest", "junit", "test case design", "api testing",
        "ci/cd", "bdd", "regression testing", "jira", "python",
    ],
    "Data Engineer": [
        "python", "sql", "spark", "airflow", "kafka",
        "etl", "data warehousing", "hdfs", "dbt", "cloud storage",
    ],
    "Site Reliability Engineer (SRE)": [
        "kubernetes", "prometheus", "grafana", "linux", "python",
        "terraform", "slo/sli", "incident management", "chaos engineering", "go",
    ],
    "UI/UX Designer": [
        "figma", "wireframing", "prototyping", "user research", "usability testing",
        "interaction design", "design systems", "adobe xd", "accessibility", "typography",
    ],
    "Network Engineer": [
        "tcp/ip", "routing protocols", "bgp", "ospf", "switching",
        "vlan", "vpn", "firewalls", "dns", "network automation",
    ],
    "Business/Systems Analyst": [
        "requirements gathering", "uml", "bpmn", "stakeholder management", "jira",
        "use cases", "sql", "process modeling", "gap analysis", "agile",
    ],
    "AI/NLP Engineer": [
        "python", "transformers", "pytorch", "hugging face", "nlp",
        "embeddings", "ner", "llm", "rag", "vector databases",
    ],
    "Blockchain Developer": [
        "solidity", "ethereum", "smart contracts", "web3.js", "hardhat",
        "erc standards", "defi", "consensus mechanisms", "cryptography", "dapps",
    ],
    "Embedded Systems Engineer": [
        "c", "c++", "rtos", "microcontrollers", "firmware",
        "i2c", "spi", "uart", "device drivers", "interrupts",
    ],
}

# ── CV weight profiles per role (used by scorer when no JD is supplied) ────────
# For the 10 component-3 aligned roles, weights mirror component3 ROLE_CV_WEIGHTS.
ROLE_CV_WEIGHTS: Dict[str, Dict[str, float]] = {
    # ── Component-3 aligned ────────────────────────────────────────────────────
    "Software Engineer":          {"w_edu": 0.20, "w_exp": 0.30, "w_skill": 0.50},
    "Data Scientist":             {"w_edu": 0.30, "w_exp": 0.30, "w_skill": 0.40},
    "Machine Learning Engineer":  {"w_edu": 0.25, "w_exp": 0.30, "w_skill": 0.45},
    "DevOps Engineer":            {"w_edu": 0.15, "w_exp": 0.40, "w_skill": 0.45},
    "Cloud Solutions Architect":  {"w_edu": 0.20, "w_exp": 0.40, "w_skill": 0.40},
    "Database Administrator":     {"w_edu": 0.20, "w_exp": 0.40, "w_skill": 0.40},
    "Frontend Developer":         {"w_edu": 0.15, "w_exp": 0.30, "w_skill": 0.55},
    "Backend Developer":          {"w_edu": 0.20, "w_exp": 0.30, "w_skill": 0.50},
    "Mobile App Developer":       {"w_edu": 0.15, "w_exp": 0.30, "w_skill": 0.55},
    "Cybersecurity Analyst":      {"w_edu": 0.20, "w_exp": 0.35, "w_skill": 0.45},
    # ── New roles ─────────────────────────────────────────────────────────────
    "Full Stack Developer":        {"w_edu": 0.15, "w_exp": 0.35, "w_skill": 0.50},
    "QA/Test Automation Engineer": {"w_edu": 0.15, "w_exp": 0.30, "w_skill": 0.55},
    "Data Engineer":               {"w_edu": 0.20, "w_exp": 0.35, "w_skill": 0.45},
    "Site Reliability Engineer (SRE)": {"w_edu": 0.15, "w_exp": 0.40, "w_skill": 0.45},
    "UI/UX Designer":              {"w_edu": 0.15, "w_exp": 0.25, "w_skill": 0.60},
    "Network Engineer":            {"w_edu": 0.20, "w_exp": 0.40, "w_skill": 0.40},
    "Business/Systems Analyst":    {"w_edu": 0.25, "w_exp": 0.35, "w_skill": 0.40},
    "AI/NLP Engineer":             {"w_edu": 0.25, "w_exp": 0.30, "w_skill": 0.45},
    "Blockchain Developer":        {"w_edu": 0.20, "w_exp": 0.30, "w_skill": 0.50},
    "Embedded Systems Engineer":   {"w_edu": 0.20, "w_exp": 0.40, "w_skill": 0.40},
}

# ── Ordered list of the canonical 20 role names ────────────────────────────────
# (same order as component2/raigs/generate.py ROLES dict)
ALL_ROLES: List[str] = list(REQUIRED_SKILLS.keys())
