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

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ── Target Job Profile ─────────────────────────────────────────────────────────

@dataclass
class TargetJobProfile:
    """Structured Target Job Profile for multi-layer candidate intelligence matching."""
    job_title: str
    canonical_role: str
    seniority: str
    required_skills: List[str]
    preferred_skills: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    required_experience_years: Optional[float] = None
    preferred_experience_years: Optional[float] = None
    required_education: List[str] = field(default_factory=list)
    preferred_education: List[str] = field(default_factory=list)
    required_certifications: List[str] = field(default_factory=list)
    domain: str = "Information Technology"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_title": self.job_title,
            "canonical_role": self.canonical_role,
            "seniority": self.seniority,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "technologies": self.technologies,
            "responsibilities": self.responsibilities,
            "required_experience_years": self.required_experience_years,
            "preferred_experience_years": self.preferred_experience_years,
            "required_education": self.required_education,
            "preferred_education": self.preferred_education,
            "required_certifications": self.required_certifications,
            "domain": self.domain,
        }


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
    "Site Reliability Engineer": 4.0, # Operational maturity; similar to DevOps
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
    "Site Reliability Engineer": [
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
    "Site Reliability Engineer": {"w_edu": 0.15, "w_exp": 0.40, "w_skill": 0.45},
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


# ── Preferred skills per role ──────────────────────────────────────────────────
PREFERRED_SKILLS: Dict[str, List[str]] = {
    "Software Engineer": ["docker", "ci/cd", "microservices", "redis", "aws"],
    "Data Scientist": ["deep learning", "nlp", "tensorflow", "pytorch", "bigquery"],
    "Machine Learning Engineer": ["kubernetes", "ray", "onnx", "fastapi", "cuda"],
    "DevOps Engineer": ["helm", "prometheus", "grafana", "istio", "vault"],
    "Cloud Solutions Architect": ["finops", "cloud security", "saml", "multi-cloud"],
    "Database Administrator": ["redis", "elasticsearch", "cassandra", "sharding"],
    "Frontend Developer": ["next.js", "tailwind css", "graphql", "jest", "vite"],
    "Backend Developer": ["fastapi", "grpc", "kafka", "redis", "postgresql"],
    "Mobile App Developer": ["ci/cd", "fastlane", "clean architecture", "bloc", "swiftui"],
    "Cybersecurity Analyst": ["cissp", "ceh", "wireshark", "splunk", "mitre att&ck"],
    "Full Stack Developer": ["next.js", "tailwind css", "postgresql", "docker", "ci/cd"],
    "QA/Test Automation Engineer": ["playwright", "cypress", "postman", "gatling", "k6"],
    "Data Engineer": ["snowflake", "databricks", "presto", "trino", "delta lake"],
    "Site Reliability Engineer": ["opentelemetry", "datadog", "chaos engineering", "ansible"],
    "UI/UX Designer": ["design tokens", "micro-interactions", "heuristic evaluation", "storyboarding"],
    "Network Engineer": ["ccna", "ccnp", "sd-wan", "ansible", "palo alto"],
    "Business/Systems Analyst": ["tableau", "power bi", "agile", "user stories", "swagger"],
    "AI/NLP Engineer": ["langchain", "llamaindex", "faiss", "pinecone", "fine-tuning"],
    "Blockchain Developer": ["rust", "solana", "truffle", "subgraph", "zero knowledge"],
    "Embedded Systems Engineer": ["arm cortex", "linux kernel", "pcb layout", "oscilloscope", "ble"],
}

# ── Role Domain Mapping ────────────────────────────────────────────────────────
ROLE_DOMAINS: Dict[str, str] = {
    "Software Engineer": "Software Engineering & Architecture",
    "Data Scientist": "Data Science & Artificial Intelligence",
    "Machine Learning Engineer": "Machine Learning & MLOps",
    "DevOps Engineer": "Cloud Infrastructure & DevOps",
    "Cloud Solutions Architect": "Cloud Infrastructure & Enterprise Architecture",
    "Database Administrator": "Database Engineering & Storage Systems",
    "Frontend Developer": "Frontend Engineering & User Interface",
    "Backend Developer": "Backend Systems & Distributed APIs",
    "Mobile App Developer": "Mobile Software Engineering",
    "Cybersecurity Analyst": "Cybersecurity & Information Security",
    "Full Stack Developer": "Full Stack Web Engineering",
    "QA/Test Automation Engineer": "Quality Assurance & Test Automation",
    "Data Engineer": "Data Engineering & Analytics Infrastructure",
    "Site Reliability Engineer": "Reliability Engineering & Cloud Infrastructure",
    "UI/UX Designer": "Product Design & User Experience",
    "Network Engineer": "Network Engineering & Telecommunications",
    "Business/Systems Analyst": "Business Systems & Requirements Analysis",
    "AI/NLP Engineer": "Artificial Intelligence & NLP",
    "Blockchain Developer": "Decentralized Systems & Blockchain",
    "Embedded Systems Engineer": "Embedded Systems & Firmware Engineering",
}


def build_target_job_profile(
    role_name: str = "Software Engineer",
    jd_text: Optional[str] = None,
    custom_spec: Optional[Dict[str, Any]] = None,
) -> TargetJobProfile:
    """Build a comprehensive, structured Target Job Profile for multi-layer candidate intelligence matching."""
    canonical = role_name if role_name in REQUIRED_SKILLS else "Software Engineer"
    spec = custom_spec or {}

    req_skills = spec.get("required_skills") or REQUIRED_SKILLS.get(canonical, [])
    pref_skills = spec.get("preferred_skills") or PREFERRED_SKILLS.get(canonical, [])
    req_years = spec.get("required_experience_years") or REQUIRED_YEARS.get(canonical, 3.0)
    domain = spec.get("domain") or ROLE_DOMAINS.get(canonical, "Information Technology")

    # Common education baselines per role
    req_edu = spec.get("required_education") or [
        "BSc Computer Science",
        "BSc Information Technology",
        "BSc Software Engineering",
    ]
    if canonical in ["Data Scientist", "AI/NLP Engineer"]:
        req_edu = ["BSc Data Science", "BSc Computer Science", "BSc Mathematics", "BSc Statistics"]
    elif canonical in ["Network Engineer", "Cybersecurity Analyst"]:
        req_edu = ["BSc Computer Networks", "BSc Cybersecurity", "BSc Information Technology"]

    pref_edu = spec.get("preferred_education") or ["MSc Computer Science", "MSc Software Engineering"]
    seniority = spec.get("seniority", "Mid")

    return TargetJobProfile(
        job_title=spec.get("job_title", canonical),
        canonical_role=canonical,
        seniority=seniority,
        required_skills=list(req_skills),
        preferred_skills=list(pref_skills),
        technologies=list(req_skills[:6] + pref_skills[:4]),
        responsibilities=spec.get("responsibilities", [
            f"Design, build, and maintain production systems for {canonical} domain",
            "Collaborate with cross-functional technical teams and adhere to code quality standards",
            "Participate in architecture reviews, code testing, and technical documentation"
        ]),
        required_experience_years=float(req_years),
        preferred_experience_years=float(req_years) + 2.0,
        required_education=req_edu,
        preferred_education=pref_edu,
        required_certifications=spec.get("required_certifications", []),
        domain=domain,
    )

