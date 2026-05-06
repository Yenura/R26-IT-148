"""
Role Configurations - Component 3
IT22027610 | Perera K.G.S.N | R26-IT-148

Defines all 10 job roles with:
  - Role-specific required skills
  - Interview weight profiles
  - CV weight profiles
  - Hard filter thresholds
  - Required years of experience
  - Ground truth relevance logic per role
"""

# ─────────────────────────────────────────────────────────────────
# 10 ROLE DEFINITIONS
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
}

EDU_LEVEL_SCORES = {1: 0.40, 2: 0.60, 3: 0.80, 4: 1.00}
EDU_LEVEL_NAMES  = {1: "Diploma", 2: "BSc", 3: "MSc", 4: "PhD"}
