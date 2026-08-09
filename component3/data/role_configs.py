"""
Role Configurations - Component 3
IT22027610 | Perera K.G.S.N | R26-IT-148

Defines all 20 job roles with:
  - Role-specific required skills
  - Interview weight profiles
  - CV weight profiles
  - Hard filter thresholds
  - Required years of experience
  - Ground truth relevance logic per role
"""

# ─────────────────────────────────────────────────────────────────
# 20 ROLE DEFINITIONS
# ─────────────────────────────────────────────────────────────────

ROLES = [
    "Software_Engineer",
    "Data_Scientist",
    "Machine_Learning_Engineer",
    "DevOps_Engineer",
    "Cybersecurity_Analyst",
    "Cloud_Solutions_Architect",
    "Database_Administrator",
    "Frontend_Developer",
    "Backend_Developer",
    "Mobile_App_Developer",
    "Full_Stack_Developer",
    "QA_Test_Automation_Engineer",
    "Data_Engineer",
    "Site_Reliability_Engineer",
    "UI_UX_Designer",
    "Network_Engineer",
    "Business_Systems_Analyst",
    "AI_NLP_Engineer",
    "Blockchain_Developer",
    "Embedded_Systems_Engineer",
]

ROLE_DISPLAY_NAMES = {
    "Software_Engineer":         "Software Engineer",
    "Data_Scientist":            "Data Scientist",
    "Machine_Learning_Engineer": "Machine Learning Engineer",
    "DevOps_Engineer":           "DevOps Engineer",
    "Cybersecurity_Analyst":     "Cybersecurity Analyst",
    "Cloud_Solutions_Architect": "Cloud Solutions Architect",
    "Database_Administrator":    "Database Administrator",
    "Frontend_Developer":        "Frontend Developer",
    "Backend_Developer":         "Backend Developer",
    "Mobile_App_Developer":      "Mobile App Developer",
    "Full_Stack_Developer":      "Full Stack Developer",
    "QA_Test_Automation_Engineer": "QA/Test Automation Engineer",
    "Data_Engineer":             "Data Engineer",
    "Site_Reliability_Engineer": "Site Reliability Engineer (SRE)",
    "UI_UX_Designer":            "UI/UX Designer",
    "Network_Engineer":          "Network Engineer",
    "Business_Systems_Analyst":  "Business/Systems Analyst",
    "AI_NLP_Engineer":           "AI/NLP Engineer",
    "Blockchain_Developer":      "Blockchain Developer",
    "Embedded_Systems_Engineer": "Embedded Systems Engineer",
}

ROLE_ICONS = {
    "Software_Engineer":         "🖥️",
    "Data_Scientist":            "📊",
    "Machine_Learning_Engineer": "🤖",
    "DevOps_Engineer":           "⚙️",
    "Cybersecurity_Analyst":     "🔒",
    "Cloud_Solutions_Architect": "☁️",
    "Database_Administrator":    "🗄️",
    "Frontend_Developer":        "🎨",
    "Backend_Developer":         "🔧",
    "Mobile_App_Developer":      "📱",
    "Full_Stack_Developer":      "🌐",
    "QA_Test_Automation_Engineer": "🧪",
    "Data_Engineer":             "📈",
    "Site_Reliability_Engineer": "🏗️",
    "UI_UX_Designer":            "✏️",
    "Network_Engineer":          "🌐",
    "Business_Systems_Analyst":  "📋",
    "AI_NLP_Engineer":           "🧠",
    "Blockchain_Developer":      "⛓️",
    "Embedded_Systems_Engineer": "🔌",
}

# Required skills per role (shown to employers)
ROLE_REQUIRED_SKILLS = {
    "Software_Engineer":         "Python, Java, C++, Data Structures, Algorithms, REST APIs, Git, OOP, SQL",
    "Data_Scientist":            "Python, R, Statistics, Machine Learning, Pandas, NumPy, Matplotlib, SQL, Jupyter",
    "Machine_Learning_Engineer": "Python, TensorFlow, PyTorch, Scikit-learn, Deep Learning, MLOps, Docker, SQL",
    "DevOps_Engineer":           "Linux, Docker, Kubernetes, CI/CD, Jenkins, Terraform, AWS/Azure, Bash, Ansible",
    "Cybersecurity_Analyst":     "Network Security, SIEM, Penetration Testing, Firewalls, IDS/IPS, Python, OWASP",
    "Cloud_Solutions_Architect": "AWS/Azure/GCP, Terraform, Kubernetes, Microservices, Networking, Security, Cost Optimization",
    "Database_Administrator":    "SQL, PostgreSQL, MySQL, MongoDB, Query Optimization, Backup & Recovery, Replication",
    "Frontend_Developer":        "HTML, CSS, JavaScript, React, TypeScript, Responsive Design, REST APIs, Git",
    "Backend_Developer":         "Python/Java/Node.js, REST APIs, SQL, Microservices, Docker, Redis, Git",
    "Mobile_App_Developer":      "iOS/Android, Flutter, React Native, Dart, Swift/Kotlin, Firebase, REST APIs",
    "Full_Stack_Developer":      "React, Node.js, Python, SQL, REST APIs, Docker, Git, HTML/CSS, TypeScript",
    "QA_Test_Automation_Engineer": "Selenium, Pytest, Jest, CI/CD, API Testing, Test Strategy, Python, Postman",
    "Data_Engineer":             "Python, SQL, Spark, Kafka, Airflow, ETL, AWS/GCP, Data Modeling, Hadoop",
    "Site_Reliability_Engineer": "Linux, Kubernetes, Prometheus, Grafana, Terraform, Python, Go, CI/CD, incident Response",
    "UI_UX_Designer":            "Figma, Sketch, Adobe XD, CSS, HTML, Prototyping, User Research, Wireframing, Accessibility",
    "Network_Engineer":          "TCP/IP, Cisco, Routing, Switching, Firewalls, VPN, DNS, Linux, Python",
    "Business_Systems_Analyst":  "SQL, Requirements Gathering, UML, BPMN, Stakeholder Management, Agile, JIRA, Data Analysis",
    "AI_NLP_Engineer":           "Python, TensorFlow, PyTorch, NLP, Transformers, Hugging Face, spaCy, Deep Learning",
    "Blockchain_Developer":      "Solidity, Ethereum, Web3.js, Smart Contracts, Rust, C++, Cryptography, DApps",
    "Embedded_Systems_Engineer": "C, C++, Rust, RTOS, Microcontrollers, ARM, Linux Kernel, Communication Protocols",
}

# Interview weight profiles - role-specific
# Coding matters most for engineers, descriptive for analysts/architects
ROLE_INTERVIEW_WEIGHTS = {
    "Software_Engineer":         {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "Data_Scientist":            {"w_mcq": 0.30, "w_desc": 0.50, "w_code": 0.20},
    "Machine_Learning_Engineer": {"w_mcq": 0.25, "w_desc": 0.35, "w_code": 0.40},
    "DevOps_Engineer":           {"w_mcq": 0.25, "w_desc": 0.30, "w_code": 0.45},
    "Cybersecurity_Analyst":     {"w_mcq": 0.35, "w_desc": 0.45, "w_code": 0.20},
    "Cloud_Solutions_Architect": {"w_mcq": 0.30, "w_desc": 0.50, "w_code": 0.20},
    "Database_Administrator":    {"w_mcq": 0.30, "w_desc": 0.35, "w_code": 0.35},
    "Frontend_Developer":        {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "Backend_Developer":         {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "Mobile_App_Developer":      {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "Full_Stack_Developer":      {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "QA_Test_Automation_Engineer": {"w_mcq": 0.25, "w_desc": 0.35, "w_code": 0.40},
    "Data_Engineer":             {"w_mcq": 0.25, "w_desc": 0.35, "w_code": 0.40},
    "Site_Reliability_Engineer": {"w_mcq": 0.25, "w_desc": 0.30, "w_code": 0.45},
    "UI_UX_Designer":            {"w_mcq": 0.30, "w_desc": 0.50, "w_code": 0.20},
    "Network_Engineer":          {"w_mcq": 0.30, "w_desc": 0.40, "w_code": 0.30},
    "Business_Systems_Analyst":  {"w_mcq": 0.35, "w_desc": 0.50, "w_code": 0.15},
    "AI_NLP_Engineer":           {"w_mcq": 0.25, "w_desc": 0.35, "w_code": 0.40},
    "Blockchain_Developer":      {"w_mcq": 0.20, "w_desc": 0.30, "w_code": 0.50},
    "Embedded_Systems_Engineer": {"w_mcq": 0.25, "w_desc": 0.30, "w_code": 0.45},
}

# CV weight profiles - role-specific
ROLE_CV_WEIGHTS = {
    "Software_Engineer":         {"w_edu": 0.20, "w_exp": 0.30, "w_skill": 0.50},
    "Data_Scientist":            {"w_edu": 0.30, "w_exp": 0.30, "w_skill": 0.40},
    "Machine_Learning_Engineer": {"w_edu": 0.25, "w_exp": 0.30, "w_skill": 0.45},
    "DevOps_Engineer":           {"w_edu": 0.15, "w_exp": 0.40, "w_skill": 0.45},
    "Cybersecurity_Analyst":     {"w_edu": 0.20, "w_exp": 0.35, "w_skill": 0.45},
    "Cloud_Solutions_Architect": {"w_edu": 0.20, "w_exp": 0.40, "w_skill": 0.40},
    "Database_Administrator":    {"w_edu": 0.20, "w_exp": 0.40, "w_skill": 0.40},
    "Frontend_Developer":        {"w_edu": 0.15, "w_exp": 0.30, "w_skill": 0.55},
    "Backend_Developer":         {"w_edu": 0.20, "w_exp": 0.30, "w_skill": 0.50},
    "Mobile_App_Developer":      {"w_edu": 0.15, "w_exp": 0.30, "w_skill": 0.55},
    "Full_Stack_Developer":      {"w_edu": 0.15, "w_exp": 0.30, "w_skill": 0.55},
    "QA_Test_Automation_Engineer": {"w_edu": 0.15, "w_exp": 0.35, "w_skill": 0.50},
    "Data_Engineer":             {"w_edu": 0.20, "w_exp": 0.35, "w_skill": 0.45},
    "Site_Reliability_Engineer": {"w_edu": 0.15, "w_exp": 0.40, "w_skill": 0.45},
    "UI_UX_Designer":            {"w_edu": 0.20, "w_exp": 0.25, "w_skill": 0.55},
    "Network_Engineer":          {"w_edu": 0.20, "w_exp": 0.35, "w_skill": 0.45},
    "Business_Systems_Analyst":  {"w_edu": 0.25, "w_exp": 0.35, "w_skill": 0.40},
    "AI_NLP_Engineer":           {"w_edu": 0.25, "w_exp": 0.30, "w_skill": 0.45},
    "Blockchain_Developer":      {"w_edu": 0.15, "w_exp": 0.30, "w_skill": 0.55},
    "Embedded_Systems_Engineer": {"w_edu": 0.20, "w_exp": 0.35, "w_skill": 0.45},
}

# Hard filter minimum requirements per role
ROLE_REQUIREMENTS = {
    "Software_Engineer":         {"min_edu": 2, "min_exp": 1.5, "min_skill": 0.40, "min_code": 0.30},
    "Data_Scientist":            {"min_edu": 3, "min_exp": 1.0, "min_skill": 0.38, "min_code": 0.20},
    "Machine_Learning_Engineer": {"min_edu": 3, "min_exp": 1.5, "min_skill": 0.42, "min_code": 0.30},
    "DevOps_Engineer":           {"min_edu": 2, "min_exp": 2.0, "min_skill": 0.40, "min_code": 0.28},
    "Cybersecurity_Analyst":     {"min_edu": 2, "min_exp": 1.5, "min_skill": 0.38, "min_code": 0.15},
    "Cloud_Solutions_Architect": {"min_edu": 2, "min_exp": 3.0, "min_skill": 0.42, "min_code": 0.15},
    "Database_Administrator":    {"min_edu": 2, "min_exp": 1.5, "min_skill": 0.38, "min_code": 0.25},
    "Frontend_Developer":        {"min_edu": 2, "min_exp": 1.0, "min_skill": 0.38, "min_code": 0.30},
    "Backend_Developer":         {"min_edu": 2, "min_exp": 1.5, "min_skill": 0.40, "min_code": 0.30},
    "Mobile_App_Developer":      {"min_edu": 2, "min_exp": 1.0, "min_skill": 0.38, "min_code": 0.30},
    "Full_Stack_Developer":      {"min_edu": 2, "min_exp": 1.5, "min_skill": 0.40, "min_code": 0.30},
    "QA_Test_Automation_Engineer": {"min_edu": 2, "min_exp": 1.0, "min_skill": 0.38, "min_code": 0.25},
    "Data_Engineer":             {"min_edu": 2, "min_exp": 1.5, "min_skill": 0.40, "min_code": 0.28},
    "Site_Reliability_Engineer": {"min_edu": 2, "min_exp": 2.0, "min_skill": 0.42, "min_code": 0.30},
    "UI_UX_Designer":            {"min_edu": 2, "min_exp": 1.0, "min_skill": 0.35, "min_code": 0.10},
    "Network_Engineer":          {"min_edu": 2, "min_exp": 1.5, "min_skill": 0.38, "min_code": 0.20},
    "Business_Systems_Analyst":  {"min_edu": 2, "min_exp": 1.5, "min_skill": 0.35, "min_code": 0.10},
    "AI_NLP_Engineer":           {"min_edu": 3, "min_exp": 1.5, "min_skill": 0.42, "min_code": 0.30},
    "Blockchain_Developer":      {"min_edu": 2, "min_exp": 1.0, "min_skill": 0.38, "min_code": 0.30},
    "Embedded_Systems_Engineer": {"min_edu": 2, "min_exp": 1.5, "min_skill": 0.40, "min_code": 0.30},
}

# Required years of experience per role (for S_exp calculation)
REQUIRED_YEARS = {
    "Software_Engineer":         3.0,
    "Data_Scientist":            2.5,
    "Machine_Learning_Engineer": 3.0,
    "DevOps_Engineer":           4.0,
    "Cybersecurity_Analyst":     3.0,
    "Cloud_Solutions_Architect": 5.0,
    "Database_Administrator":    3.0,
    "Frontend_Developer":        2.0,
    "Backend_Developer":         3.0,
    "Mobile_App_Developer":      2.5,
    "Full_Stack_Developer":      3.0,
    "QA_Test_Automation_Engineer": 2.0,
    "Data_Engineer":             3.0,
    "Site_Reliability_Engineer": 4.0,
    "UI_UX_Designer":            2.0,
    "Network_Engineer":          3.0,
    "Business_Systems_Analyst":  3.0,
    "AI_NLP_Engineer":           3.0,
    "Blockchain_Developer":      2.5,
    "Embedded_Systems_Engineer": 3.0,
}

# Education level distribution per role
# [Diploma, BSc, MSc, PhD]
ROLE_EDU_DISTRIBUTION = {
    "Software_Engineer":         [0.05, 0.55, 0.35, 0.05],
    "Data_Scientist":            [0.02, 0.30, 0.50, 0.18],
    "Machine_Learning_Engineer": [0.02, 0.28, 0.52, 0.18],
    "DevOps_Engineer":           [0.08, 0.60, 0.28, 0.04],
    "Cybersecurity_Analyst":     [0.05, 0.55, 0.35, 0.05],
    "Cloud_Solutions_Architect": [0.03, 0.45, 0.42, 0.10],
    "Database_Administrator":    [0.07, 0.58, 0.30, 0.05],
    "Frontend_Developer":        [0.10, 0.65, 0.22, 0.03],
    "Backend_Developer":         [0.05, 0.58, 0.33, 0.04],
    "Mobile_App_Developer":      [0.10, 0.65, 0.22, 0.03],
    "Full_Stack_Developer":      [0.08, 0.62, 0.26, 0.04],
    "QA_Test_Automation_Engineer": [0.10, 0.60, 0.25, 0.05],
    "Data_Engineer":             [0.05, 0.55, 0.33, 0.07],
    "Site_Reliability_Engineer": [0.05, 0.58, 0.30, 0.07],
    "UI_UX_Designer":            [0.12, 0.60, 0.22, 0.06],
    "Network_Engineer":          [0.08, 0.58, 0.28, 0.06],
    "Business_Systems_Analyst":  [0.05, 0.55, 0.32, 0.08],
    "AI_NLP_Engineer":           [0.02, 0.28, 0.50, 0.20],
    "Blockchain_Developer":      [0.08, 0.55, 0.30, 0.07],
    "Embedded_Systems_Engineer": [0.06, 0.55, 0.32, 0.07],
}

# Experience distribution (mean, std) per role
ROLE_EXP_DISTRIBUTION = {
    "Software_Engineer":         (4.0, 2.5),
    "Data_Scientist":            (3.5, 2.0),
    "Machine_Learning_Engineer": (3.5, 2.0),
    "DevOps_Engineer":           (5.0, 2.5),
    "Cybersecurity_Analyst":     (4.5, 2.5),
    "Cloud_Solutions_Architect": (6.0, 2.5),
    "Database_Administrator":    (4.5, 2.5),
    "Frontend_Developer":        (3.0, 2.0),
    "Backend_Developer":         (4.0, 2.5),
    "Mobile_App_Developer":      (3.0, 2.0),
    "Full_Stack_Developer":      (3.5, 2.0),
    "QA_Test_Automation_Engineer": (3.0, 2.0),
    "Data_Engineer":             (4.0, 2.5),
    "Site_Reliability_Engineer": (5.0, 2.5),
    "UI_UX_Designer":            (3.0, 2.0),
    "Network_Engineer":          (4.5, 2.5),
    "Business_Systems_Analyst":  (4.0, 2.5),
    "AI_NLP_Engineer":           (3.5, 2.0),
    "Blockchain_Developer":      (3.0, 2.0),
    "Embedded_Systems_Engineer": (4.0, 2.5),
}

# Ground truth thresholds for relevance label assignment per role
# (code_thresh, skill_thresh, desc_thresh, edu_thresh, mcq_thresh)
ROLE_RELEVANCE_THRESHOLDS = {
    "Software_Engineer":         {"code": (0.75, 0.55, 0.35), "skill": (0.70, 0.55, 0.35),
                                   "desc": None,               "dominance": "code_skill"},
    "Data_Scientist":            {"code": None,                "skill": (0.68, 0.52, 0.35),
                                   "desc": (0.75, 0.58, 0.38), "dominance": "desc_skill"},
    "Machine_Learning_Engineer": {"code": (0.70, 0.52, 0.32), "skill": (0.72, 0.56, 0.36),
                                   "desc": (0.68, 0.52, 0.32), "dominance": "code_skill_desc"},
    "DevOps_Engineer":           {"code": (0.72, 0.54, 0.33), "skill": (0.72, 0.56, 0.36),
                                   "desc": None,               "dominance": "code_skill"},
    "Cybersecurity_Analyst":     {"code": None,                "skill": (0.70, 0.54, 0.35),
                                   "desc": (0.74, 0.57, 0.37), "dominance": "desc_skill"},
    "Cloud_Solutions_Architect": {"code": None,                "skill": (0.72, 0.55, 0.35),
                                   "desc": (0.76, 0.58, 0.38), "dominance": "desc_skill_exp"},
    "Database_Administrator":    {"code": (0.70, 0.52, 0.32), "skill": (0.70, 0.54, 0.35),
                                   "desc": (0.68, 0.52, 0.32), "dominance": "code_skill_desc"},
    "Frontend_Developer":        {"code": (0.74, 0.55, 0.35), "skill": (0.72, 0.55, 0.35),
                                   "desc": None,               "dominance": "code_skill"},
    "Backend_Developer":         {"code": (0.74, 0.55, 0.35), "skill": (0.70, 0.54, 0.35),
                                   "desc": None,               "dominance": "code_skill"},
    "Mobile_App_Developer":      {"code": (0.73, 0.54, 0.34), "skill": (0.71, 0.54, 0.34),
                                   "desc": None,               "dominance": "code_skill"},
    "Full_Stack_Developer":      {"code": (0.74, 0.55, 0.35), "skill": (0.70, 0.54, 0.35),
                                   "desc": None,               "dominance": "code_skill"},
    "QA_Test_Automation_Engineer": {"code": (0.70, 0.52, 0.32), "skill": (0.68, 0.52, 0.32),
                                   "desc": (0.70, 0.55, 0.35), "dominance": "code_skill_desc"},
    "Data_Engineer":             {"code": (0.72, 0.54, 0.33), "skill": (0.70, 0.54, 0.35),
                                   "desc": None,               "dominance": "code_skill"},
    "Site_Reliability_Engineer": {"code": (0.72, 0.54, 0.33), "skill": (0.72, 0.56, 0.36),
                                   "desc": None,               "dominance": "code_skill"},
    "UI_UX_Designer":            {"code": None,                "skill": (0.65, 0.50, 0.32),
                                   "desc": (0.72, 0.55, 0.35), "dominance": "desc_skill"},
    "Network_Engineer":          {"code": (0.70, 0.52, 0.32), "skill": (0.70, 0.54, 0.35),
                                   "desc": (0.70, 0.55, 0.35), "dominance": "code_skill_desc"},
    "Business_Systems_Analyst":  {"code": None,                "skill": (0.65, 0.50, 0.32),
                                   "desc": (0.75, 0.58, 0.38), "dominance": "desc_skill"},
    "AI_NLP_Engineer":           {"code": (0.70, 0.52, 0.32), "skill": (0.72, 0.56, 0.36),
                                   "desc": (0.68, 0.52, 0.32), "dominance": "code_skill_desc"},
    "Blockchain_Developer":      {"code": (0.74, 0.55, 0.35), "skill": (0.70, 0.54, 0.35),
                                   "desc": None,               "dominance": "code_skill"},
    "Embedded_Systems_Engineer": {"code": (0.74, 0.55, 0.35), "skill": (0.70, 0.54, 0.35),
                                   "desc": None,               "dominance": "code_skill"},
}

EDU_LEVEL_SCORES = {1: 0.40, 2: 0.60, 3: 0.80, 4: 1.00}
EDU_LEVEL_NAMES  = {1: "Diploma", 2: "BSc", 3: "MSc", 4: "PhD"}
