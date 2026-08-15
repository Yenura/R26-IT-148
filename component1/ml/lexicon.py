"""
Comprehensive IT Skill Lexicon, Certifications & Education Regex patterns.
Used for information extraction from CV text (Component 1).
"""

from typing import Dict, List, Set

SKILL_LEXICON: Dict[str, List[str]] = {
    "Software Engineering": [
        "python", "java", "c++", "c#", ".net", "git", "oop", "object oriented programming",
        "rest api", "restful api", "data structures", "algorithms", "design patterns",
        "unit testing", "code review", "agile", "scrum", "software development", "refactoring"
    ],
    "Frontend": [
        "html", "html5", "css", "css3", "javascript", "typescript", "react", "react.js",
        "angular", "vue", "vue.js", "next.js", "tailwind", "tailwind css", "bootstrap",
        "redux", "webpack", "responsive design", "sass", "less", "accessibility", "dom"
    ],
    "Backend": [
        "node.js", "express", "express.js", "django", "flask", "fastapi", "spring boot",
        "ruby on rails", "asp.net", "php", "laravel", "microservices", "rest", "graphql",
        "grpc", "jwt", "oauth", "session management", "web sockets", "middleware"
    ],
    "Data Science": [
        "python", "r", "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn",
        "statistics", "statistical modeling", "hypothesis testing", "jupyter", "exploratory data analysis",
        "data cleaning", "feature engineering", "data visualization", "tableau", "power bi"
    ],
    "Machine Learning": [
        "tensorflow", "pytorch", "keras", "scikit-learn", "machine learning", "deep learning",
        "neural networks", "cnn", "rnn", "computer vision", "model deployment", "model training",
        "supervising learning", "unsupervised learning", "reinforcement learning", "hyperparameter tuning"
    ],
    "DevOps": [
        "docker", "kubernetes", "jenkins", "ci/cd", "continuous integration", "continuous deployment",
        "terraform", "ansible", "github actions", "gitlab ci", "bash", "shell scripting",
        "linux", "helm", "infrastructure as code", "iac"
    ],
    "Cloud": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp", "google cloud platform",
        "ec2", "s3", "lambda", "cloudformation", "iam", "serverless", "cloud architecture",
        "virtual private cloud", "vpc", "cost optimization"
    ],
    "Database": [
        "mysql", "postgresql", "mongodb", "oracle", "sql server", "redis", "sql", "nosql",
        "cassandra", "dynamodb", "indexing", "query optimization", "database design",
        "replication", "backup and recovery", "transactions", "stored procedures"
    ],
    "Mobile": [
        "android", "kotlin", "java", "flutter", "dart", "react native", "swift", "ios",
        "xcode", "android studio", "mobile application development", "app store", "play store",
        "core data", "jetpack compose"
    ],
    "QA": [
        "selenium", "cypress", "playwright", "junit", "testng", "postman", "api testing",
        "automation testing", "manual testing", "test automation", "test case design",
        "bug tracking", "jira", "bdd", "cucumber", "regression testing"
    ],
    "Data Engineering": [
        "apache spark", "spark", "kafka", "apache kafka", "airflow", "apache airflow",
        "etl", "elt", "data pipeline", "data warehousing", "snowflake", "bigquery",
        "redshift", "hadoop", "hdfs", "dbt", "data lake"
    ],
    "SRE": [
        "prometheus", "grafana", "kubernetes", "docker", "linux", "monitoring",
        "observability", "incident response", "incident management", "sli", "slo", "sla",
        "chaos engineering", "alerting", "log management", "elk stack"
    ],
    "Cybersecurity": [
        "siem", "soc", "splunk", "penetration testing", "pen testing", "vulnerability assessment",
        "firewalls", "ids", "ips", "kali linux", "network security", "owasp", "ethical hacking",
        "cryptography", "cissp", "ceh", "threat intelligence"
    ],
    "UI/UX": [
        "figma", "adobe xd", "sketch", "wireframe", "wireframing", "prototype", "prototyping",
        "user research", "usability testing", "interaction design", "user interface",
        "user experience", "design systems", "information architecture"
    ],
    "Networking": [
        "ccna", "ccnp", "cisco", "tcp/ip", "dns", "dhcp", "routing", "switching", "vpn",
        "firewall", "bgp", "ospf", "vlan", "network automation", "wireshark", "subnetting"
    ],
    "Business/Systems Analyst": [
        "requirements gathering", "requirements analysis", "uml", "bpmn", "business analysis",
        "system analysis", "jira", "confluence", "sql", "use cases", "user stories",
        "process modeling", "gap analysis", "agile", "stakeholder management"
    ],
    "AI/NLP": [
        "nlp", "natural language processing", "transformers", "bert", "sbert", "llm",
        "large language models", "hugging face", "text classification", "tokenization",
        "named entity recognition", "ner", "embeddings", "rag", "vector databases", "langchain"
    ],
    "Blockchain": [
        "solidity", "ethereum", "web3", "web3.js", "smart contracts", "blockchain",
        "hyperledger", "cryptocurrency", "hardhat", "truffle", "dapps", "erc20", "erc721", "defi"
    ],
    "Embedded": [
        "c", "c++", "arduino", "raspberry pi", "microcontrollers", "rtos", "embedded linux",
        "stm32", "iot", "firmware", "i2c", "spi", "uart", "device drivers", "assembly"
    ]
}

CERTIFICATIONS_LIST: List[str] = [
    "aws certified", "aws certified solutions architect", "aws certified developer",
    "azure certified", "microsoft certified", "google cloud certified", "gcp certified",
    "ccna", "ccnp", "comptia", "comptia security+", "cissp", "ceh", "certified ethical hacker",
    "oracle certified", "cisco certified", "pmp", "scrum master", "csm", "cisa", "cism",
    "ckad", "certified kubernetes administrator", "cka"
]

ALL_TECHNICAL_SKILLS: Set[str] = set()
for cat_skills in SKILL_LEXICON.values():
    for s in cat_skills:
        ALL_TECHNICAL_SKILLS.add(s.lower())
