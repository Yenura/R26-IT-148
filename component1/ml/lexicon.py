"""
Comprehensive IT Skill Lexicon, Certifications Taxonomy, Aliases & Related Skills Graph
Component 1: AI Resume Screening & IT Job Role Classification
IT22089236 | D T D Perera | R26-IT-148

Covers 20 Canonical IT Roles:
- Software Engineer, Frontend Developer, Backend Developer, Full Stack Developer
- Mobile App Developer, DevOps Engineer, Cloud Solutions Architect, Site Reliability Engineer
- Data Scientist, Machine Learning Engineer, Data Engineer, AI/NLP Engineer
- Database Administrator, Cybersecurity Analyst, Network Engineer, QA/Test Automation Engineer
- UI/UX Designer, Business/Systems Analyst, Blockchain Developer, Embedded Systems Engineer
"""

from typing import Dict, List, Set

SKILL_LEXICON: Dict[str, List[str]] = {
    "Software Engineering": [
        "python", "java", "c++", "c#", ".net", "go", "rust", "c", "scala", "git",
        "oop", "object oriented programming", "rest api", "restful api", "rest apis",
        "data structures", "algorithms", "design patterns", "clean code", "solid principles",
        "unit testing", "code review", "agile", "scrum", "software development",
        "system design", "refactoring", "multithreading", "concurrency", "design systems",
        "clean architecture", "domain driven design", "event sourcing", "cqrs", "protobuf",
        "protocol buffers", "grpc", "openapi", "swagger"
    ],
    "Frontend": [
        "html", "html5", "css", "css3", "javascript", "typescript", "react", "react.js", "reactjs",
        "angular", "vue", "vue.js", "vuejs", "next.js", "nextjs", "nuxt.js", "svelte",
        "tailwind", "tailwind css", "tailwindcss", "bootstrap", "sass", "less", "styled-components",
        "redux", "zustand", "mobx", "webpack", "vite", "babel", "responsive design",
        "web performance", "accessibility", "a11y", "dom", "cross-browser compatibility",
        "remix", "astro", "solidjs", "qwik", "storybook", "turborepo", "pnpm", "tanstack query",
        "framer motion", "webassembly", "wasm", "pwa"
    ],
    "Backend": [
        "node.js", "nodejs", "express", "express.js", "expressjs", "django", "flask", "fastapi",
        "spring boot", "spring framework", "ruby on rails", "asp.net", "asp.net core", ".net core",
        "php", "laravel", "nest.js", "nestjs", "microservices", "rest", "rest api", "rest apis",
        "graphql", "grpc", "jwt", "oauth", "oauth2", "session management", "websockets",
        "middleware", "message queues", "celery", "event driven architecture", "rabbitmq", "kafka",
        "fastify", "strapi", "fiber", "gin", "actix-web", "axum", "tokio", "quarkus", "micronaut",
        "temporal", "hasura", "apollo server"
    ],
    "Data Science": [
        "python", "r", "pandas", "numpy", "scipy", "matplotlib", "seaborn", "scikit-learn",
        "statistics", "statistical modeling", "hypothesis testing", "probability",
        "jupyter", "jupyter notebook", "exploratory data analysis", "eda", "data cleaning",
        "feature engineering", "data visualization", "tableau", "power bi", "excel",
        "polars", "duckdb", "dask", "statsmodels", "umap", "tsne", "optuna", "feature store"
    ],
    "Machine Learning": [
        "tensorflow", "pytorch", "keras", "scikit-learn", "machine learning", "deep learning",
        "neural networks", "cnn", "rnn", "lstm", "computer vision", "opencv", "model deployment",
        "model training", "supervised learning", "unsupervised learning", "reinforcement learning",
        "hyperparameter tuning", "mlops", "mlflow", "wandb", "onnx", "tensorrt",
        "xgboost", "lightgbm", "catboost", "shap", "lime", "peft", "lora", "qlora", "jax"
    ],
    "DevOps": [
        "docker", "kubernetes", "k8s", "jenkins", "ci/cd", "continuous integration",
        "continuous deployment", "terraform", "ansible", "github actions", "gitlab ci",
        "bash", "shell scripting", "linux", "unix", "helm", "infrastructure as code",
        "iac", "cloudformation", "vagrant", "packer", "argo cd", "gitops",
        "pulumi", "podman", "buildah", "harbor", "vault", "consul", "crossplane", "flux"
    ],
    "Cloud": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp", "google cloud platform",
        "ec2", "s3", "lambda", "cloudformation", "iam", "serverless", "cloud architecture",
        "virtual private cloud", "vpc", "cost optimization", "cloudwatch", "azure devops",
        "eks", "ecs", "fargate", "cloud storage", "route 53",
        "finops", "aws cdk", "azure bicep", "anthos", "cloudflare workers"
    ],
    "Database": [
        "mysql", "postgresql", "postgres", "mongodb", "oracle", "sql server", "mssql", "redis",
        "sql", "nosql", "cassandra", "dynamodb", "indexing", "query optimization",
        "database design", "replication", "sharding", "backup and recovery", "transactions",
        "acid", "stored procedures", "prisma", "hibernate", "sqlalchemy", "elasticsearch",
        "cockroachdb", "timescaledb", "scylladb", "neo4j", "arangodb", "supabase", "firebase", "clickhouse"
    ],
    "Mobile": [
        "android", "kotlin", "java", "flutter", "dart", "react native", "swift", "ios",
        "swiftui", "objective-c", "xcode", "android studio", "mobile application development",
        "app store", "play store", "core data", "jetpack compose", "mobile ui", "sqlite",
        "swiftdata", "combine", "rxjava", "coroutines", "koin", "dagger hilt", "fastlane", "expo"
    ],
    "QA": [
        "selenium", "cypress", "playwright", "junit", "testng", "pytest", "postman",
        "api testing", "automation testing", "manual testing", "test automation",
        "test case design", "bug tracking", "jira", "bdd", "cucumber", "regression testing",
        "load testing", "jmeter", "performance testing", "ci testing",
        "vitest", "allure", "k6", "gatling", "pact", "testrail", "robot framework"
    ],
    "Data Engineering": [
        "apache spark", "spark", "pyspark", "kafka", "apache kafka", "airflow",
        "apache airflow", "etl", "elt", "data pipeline", "data warehousing", "snowflake",
        "bigquery", "redshift", "hadoop", "hdfs", "dbt", "data lake", "delta lake",
        "databricks", "data ingestion", "batch processing", "stream processing",
        "apache flink", "apache beam", "kafka streams", "debezium", "apache iceberg", "apache hudi", "prefect", "dagster", "trino"
    ],
    "SRE": [
        "prometheus", "grafana", "kubernetes", "docker", "linux", "monitoring",
        "observability", "incident response", "incident management", "sli", "slo", "sla",
        "chaos engineering", "alerting", "log management", "elk stack", "splunk",
        "datadog", "high availability", "disaster recovery", "load balancing",
        "opentelemetry", "jaeger", "loki", "thanos", "linkerd", "envoy", "traefik", "pagerduty"
    ],
    "Cybersecurity": [
        "siem", "soc", "splunk", "penetration testing", "pen testing", "vulnerability assessment",
        "vulnerability management", "firewalls", "ids", "ips", "kali linux", "network security",
        "owasp", "owasp top 10", "ethical hacking", "cryptography", "cissp", "ceh",
        "threat intelligence", "incident response", "wireshark", "burp suite", "metasploit",
        "identity and access management", "zero trust",
        "snort", "suricata", "wazuh", "crowdstrike", "sentinel", "soar", "mitre att&ck", "soc 2", "iso 27001", "threat modeling"
    ],
    "UI/UX": [
        "figma", "adobe xd", "sketch", "wireframe", "wireframing", "prototype",
        "prototyping", "user research", "usability testing", "interaction design",
        "user interface", "user experience", "design systems", "information architecture",
        "user persona", "journey mapping", "visual design", "design thinking",
        "miro", "balsamiq", "framer", "zeplin", "design tokens", "heuristic evaluation"
    ],
    "Networking": [
        "ccna", "ccnp", "cisco", "tcp/ip", "dns", "dhcp", "routing", "switching", "vpn",
        "firewall", "bgp", "ospf", "vlan", "network automation", "wireshark", "subnetting",
        "sd-wan", "network security", "lan", "wan", "network troubleshooting",
        "mpls", "wireguard", "ipsec", "juniper", "palo alto", "fortinet"
    ],
    "Business/Systems Analyst": [
        "requirements gathering", "requirements analysis", "uml", "bpmn", "business analysis",
        "system analysis", "jira", "confluence", "sql", "use cases", "user stories",
        "process modeling", "gap analysis", "agile", "stakeholder management",
        "business process modeling", "functional specifications", "acceptance criteria",
        "swot analysis", "feasibility study", "cost benefit analysis", "user journey", "dfd"
    ],
    "AI/NLP": [
        "nlp", "natural language processing", "transformers", "bert", "sbert", "llm",
        "large language models", "hugging face", "text classification", "tokenization",
        "named entity recognition", "ner", "embeddings", "rag", "vector databases",
        "langchain", "prompt engineering", "gpt", "fine-tuning", "gensim", "spacy",
        "llamaindex", "ollama", "vllm", "chromadb", "pinecone", "weaviate", "qdrant", "milvus", "faiss"
    ],
    "Blockchain": [
        "solidity", "ethereum", "web3", "web3.js", "smart contracts", "blockchain",
        "hyperledger", "cryptocurrency", "hardhat", "truffle", "dapps", "erc20",
        "erc721", "defi", "nft", "consensus algorithms", "ethers.js",
        "foundry", "wagmi", "viem", "alchemy", "infura", "polygon", "arbitrum", "solana"
    ],
    "Embedded": [
        "c", "c++", "arduino", "raspberry pi", "microcontrollers", "rtos", "free rtos",
        "embedded linux", "stm32", "iot", "firmware", "i2c", "spi", "uart",
        "device drivers", "assembly", "pcb design", "embedded systems",
        "freertos", "zephyr", "esp-idf", "esp32", "embedded c", "embedded c++", "yocto", "can bus", "modbus", "ble", "mqtt"
    ],
    "Systems & IT Support": [
        "active directory", "windows server", "troubleshooting", "hardware", "desktop support",
        "network support", "helpdesk", "itil", "service desk", "systems administration",
        "nas", "network attached storage", "data migration", "vmware", "hyper-v",
        "patch management", "sharepoint", "outlook", "office 365", "o365", "powershell",
        "mcse", "comptia a+", "comptia network+", "remote desktop", "itsm"
    ]
}


# Bidirectional alias mapping: Raw CV variant -> Canonical Skill Name
SKILL_ALIASES: Dict[str, str] = {
    # IT Support & Systems
    "activedirectory": "active directory",
    "ad": "active directory",
    "win server": "windows server",
    "troubleshoot": "troubleshooting",
    "network attached storage": "nas",
    "a+": "comptia a+",
    "net+": "comptia network+",
    "sec+": "comptia security+",
    # Frontend
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "node js": "node.js",
    "next.js": "next.js",
    "nextjs": "next.js",
    "next js": "next.js",
    "vue.js": "vue",
    "vuejs": "vue",
    "vue js": "vue",
    "angularjs": "angular",
    "angular js": "angular",
    "tailwind": "tailwind css",
    "tailwindcss": "tailwind css",
    "tailwind-css": "tailwind css",
    "bootstrap5": "bootstrap",
    "bootstrap 5": "bootstrap",
    # Backend & Languages
    "py": "python",
    "python3": "python",
    "python 3": "python",
    "js": "javascript",
    "ts": "typescript",
    "golang": "go",
    "cplusplus": "c++",
    "cpp": "c++",
    "csharp": "c#",
    "c sharp": "c#",
    ".net core": ".net",
    "dotnet": ".net",
    "net core": ".net",
    "asp.net": "asp.net",
    "asp net": "asp.net",
    "asp.net core": "asp.net",
    "fast api": "fastapi",
    "fastapi": "fastapi",
    "express": "express.js",
    "expressjs": "express.js",
    "express.js": "express.js",
    "spring": "spring boot",
    "springboot": "spring boot",
    "rest": "rest apis",
    "rest api": "rest apis",
    "rest apis": "rest apis",
    "restful api": "rest apis",
    "restful apis": "rest apis",
    "restful": "rest apis",
    # Cloud & DevOps
    "amazon web services": "aws",
    "amazon aws": "aws",
    "google cloud platform": "gcp",
    "google cloud": "gcp",
    "microsoft azure": "azure",
    "ms azure": "azure",
    "k8s": "kubernetes",
    "ci/cd": "ci/cd",
    "ci / cd": "ci/cd",
    "ci-cd": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    # Databases
    "postgre": "postgresql",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "ms sql": "sql server",
    "mssql": "sql server",
    "microsoft sql server": "sql server",
    # Data & AI/ML
    "sklearn": "scikit-learn",
    "tf": "tensorflow",
    "pt": "pytorch",
    "torch": "pytorch",
    "eda": "exploratory data analysis",
    "nlp": "nlp",
    "natural language processing": "nlp",
    "llms": "llm",
    "large language models": "llm",
    # QA & Security
    "selenium webdriver": "selenium",
    "pen testing": "penetration testing",
    "pentesting": "penetration testing",
    "cyber security": "cybersecurity"
}

# Canonical recognized industry certifications with credential validation metadata
CANONICAL_CERTIFICATIONS: Dict[str, Dict[str, str]] = {
    "aws certified solutions architect": {"vendor": "AWS", "tier": "Associate/Professional", "domain": "Cloud"},
    "aws certified developer": {"vendor": "AWS", "tier": "Associate", "domain": "Cloud"},
    "aws certified sysops administrator": {"vendor": "AWS", "tier": "Associate", "domain": "DevOps/Cloud"},
    "aws certified cloud practitioner": {"vendor": "AWS", "tier": "Foundational", "domain": "Cloud"},
    "microsoft certified: azure fundamentals": {"vendor": "Microsoft", "tier": "Foundational", "domain": "Cloud"},
    "azure solutions architect expert": {"vendor": "Microsoft", "tier": "Expert", "domain": "Cloud"},
    "azure administrator associate": {"vendor": "Microsoft", "tier": "Associate", "domain": "Cloud"},
    "google cloud certified professional cloud architect": {"vendor": "Google", "tier": "Professional", "domain": "Cloud"},
    "certified kubernetes administrator": {"vendor": "CNCF", "tier": "Professional", "domain": "DevOps"},
    "certified kubernetes application developer": {"vendor": "CNCF", "tier": "Professional", "domain": "DevOps"},
    "cka": {"vendor": "CNCF", "tier": "Professional", "domain": "DevOps"},
    "ckad": {"vendor": "CNCF", "tier": "Professional", "domain": "DevOps"},
    "cisco certified network associate": {"vendor": "Cisco", "tier": "Associate", "domain": "Networking"},
    "ccna": {"vendor": "Cisco", "tier": "Associate", "domain": "Networking"},
    "ccnp": {"vendor": "Cisco", "tier": "Professional", "domain": "Networking"},
    "comptia security+": {"vendor": "CompTIA", "tier": "Professional", "domain": "Cybersecurity"},
    "comptia network+": {"vendor": "CompTIA", "tier": "Foundational", "domain": "Networking"},
    "comptia a+": {"vendor": "CompTIA", "tier": "Foundational", "domain": "IT Support"},
    "mcse": {"vendor": "Microsoft", "tier": "Professional", "domain": "Systems & IT Support"},
    "itil": {"vendor": "Axelos", "tier": "Foundational", "domain": "IT Service Management"},
    "pmp": {"vendor": "PMI", "tier": "Professional", "domain": "Project Management"},
    "certified information systems security professional": {"vendor": "ISC2", "tier": "Expert", "domain": "Cybersecurity"},
    "cissp": {"vendor": "ISC2", "tier": "Expert", "domain": "Cybersecurity"},
    "certified ethical hacker": {"vendor": "EC-Council", "tier": "Professional", "domain": "Cybersecurity"},
    "ceh": {"vendor": "EC-Council", "tier": "Professional", "domain": "Cybersecurity"},
    "certified scrummaster": {"vendor": "Scrum Alliance", "tier": "Professional", "domain": "Agile"},
    "csm": {"vendor": "Scrum Alliance", "tier": "Professional", "domain": "Agile"},
    "professional scrum master": {"vendor": "Scrum.org", "tier": "Professional", "domain": "Agile"},
    "psm": {"vendor": "Scrum.org", "tier": "Professional", "domain": "Agile"},
    "hashicorp certified: terraform associate": {"vendor": "HashiCorp", "tier": "Associate", "domain": "DevOps"},
    "oracle certified professional": {"vendor": "Oracle", "tier": "Professional", "domain": "Database/Java"}
}

CERTIFICATIONS_LIST: List[str] = sorted(list(CANONICAL_CERTIFICATIONS.keys()), key=len, reverse=True)

# Complementary / Related Skills Graph
# Enables semantic partial credit when candidate possesses a related/complementary skill
RELATED_SKILLS_GRAPH: Dict[str, List[str]] = {
    # Languages & Frameworks
    "python": ["django", "flask", "fastapi", "pandas", "numpy", "scikit-learn"],
    "javascript": ["typescript", "react", "node.js", "vue", "angular", "express.js"],
    "typescript": ["javascript", "react", "angular", "node.js", "next.js"],
    "react": ["javascript", "typescript", "redux", "next.js", "html", "css"],
    "node.js": ["javascript", "express.js", "typescript", "rest apis", "backend"],
    "fastapi": ["python", "rest apis", "pydantic", "docker"],
    "django": ["python", "postgresql", "rest apis"],
    "spring boot": ["java", "microservices", "rest apis", "hibernate"],
    # Cloud & Infra
    "aws": ["cloud", "docker", "kubernetes", "terraform", "ci/cd"],
    "azure": ["cloud", "docker", "kubernetes", "ci/cd"],
    "gcp": ["cloud", "kubernetes", "bigquery", "docker"],
    "docker": ["kubernetes", "ci/cd", "linux", "devops"],
    "kubernetes": ["docker", "helm", "devops", "cloud", "ci/cd"],
    "ci/cd": ["github actions", "jenkins", "gitlab ci", "docker"],
    # Databases
    "sql": ["postgresql", "mysql", "sql server", "oracle", "database design"],
    "postgresql": ["sql", "database design", "indexing", "relational database"],
    "mysql": ["sql", "database design", "indexing", "relational database"],
    "mongodb": ["nosql", "document database", "redis"],
    # Data & ML
    "machine learning": ["deep learning", "python", "scikit-learn", "pandas", "statistics"],
    "deep learning": ["pytorch", "tensorflow", "neural networks", "machine learning"],
    "pytorch": ["deep learning", "python", "neural networks"],
    "tensorflow": ["deep learning", "python", "keras", "neural networks"],
    "nlp": ["transformers", "bert", "hugging face", "python", "text classification"],
    "apache spark": ["pyspark", "big data", "hadoop", "data pipeline", "kafka"],
    "kafka": ["stream processing", "message queues", "rabbitmq", "data engineering"],
    # Security & Networking
    "penetration testing": ["vulnerability assessment", "ethical hacking", "kali linux", "owasp"],
    "cybersecurity": ["network security", "siem", "firewalls", "soc", "ids"],
    "network security": ["firewalls", "vpn", "cisco", "ccna", "cybersecurity"]
}

ALL_TECHNICAL_SKILLS: Set[str] = set()
for cat_skills in SKILL_LEXICON.values():
    for s in cat_skills:
        ALL_TECHNICAL_SKILLS.add(s.lower())
for alias in SKILL_ALIASES.keys():
    ALL_TECHNICAL_SKILLS.add(alias.lower())
