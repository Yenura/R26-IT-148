"""Skill synonym/alias mapping for question relevance matching."""

# Maps skill names to their aliases (lowercase) for fuzzy matching
SKILL_ALIASES = {
    # Frontend
    "react": ["reactjs", "react.js", "frontend", "web development", "ui", "jsx", "hooks"],
    "vue": ["vuejs", "vue.js", "frontend", "web development", "ui"],
    "angular": ["angularjs", "frontend", "web development", "ui"],
    "javascript": ["js", "es6", "ecmascript", "frontend", "web development", "browser"],
    "typescript": ["ts", "frontend", "web development", "javascript"],
    "html": ["html5", "frontend", "web development", "markup"],
    "css": ["css3", "frontend", "web development", "styling", "sass", "scss", "tailwind"],
    "sass": ["scss", "css", "frontend", "web development", "styling"],
    "tailwind": ["tailwindcss", "css", "frontend", "web development", "styling"],
    "nextjs": ["next.js", "react", "frontend", "web development", "ssr"],
    "svelte": ["frontend", "web development", "ui"],

    # Backend
    "python": ["django", "flask", "fastapi", "backend", "scripting", "automation"],
    "java": ["spring", "backend", "jvm", "enterprise"],
    "node.js": ["nodejs", "node", "express", "backend", "javascript", "npm"],
    "go": ["golang", "backend", "concurrency", "microservices"],
    "rust": ["backend", "systems programming", "memory safety"],
    "php": ["laravel", "backend", "web development"],
    "ruby": ["rails", "backend", "web development"],
    "c#": ["csharp", "dotnet", ".net", "backend", "enterprise"],
    "rest apis": ["rest", "api", "http", "web services", "backend", "microservices"],
    "graphql": ["api", "backend", "web services"],
    "grpc": ["api", "backend", "microservices", "protobuf"],

    # Database
    "sql": ["database", "relational", "queries", "postgresql", "mysql", "rdbms"],
    "postgresql": ["postgres", "sql", "database", "relational"],
    "mysql": ["sql", "database", "relational"],
    "mongodb": ["nosql", "database", "document", "nosql"],
    "redis": ["cache", "database", "nosql", "in-memory"],
    "elasticsearch": ["search", "database", "nosql", "full-text search"],
    "dynamodb": ["nosql", "database", "aws", "amazon"],
    "cassandra": ["nosql", "database", "distributed"],

    # DevOps / Cloud
    "docker": ["containers", "containerization", "devops", "microservices"],
    "kubernetes": ["k8s", "containers", "devops", "orchestration", "cloud"],
    "aws": ["amazon web services", "cloud", "ec2", "s3", "lambda", "infrastructure"],
    "azure": ["microsoft azure", "cloud", "microsoft"],
    "gcp": ["google cloud", "cloud", "google cloud platform"],
    "terraform": ["infrastructure as code", "iac", "devops", "cloud", "provisioning"],
    "ci/cd": ["continuous integration", "continuous deployment", "pipeline", "devops", "jenkins", "github actions"],
    "jenkins": ["ci/cd", "devops", "automation", "pipeline"],
    "github actions": ["ci/cd", "devops", "automation", "pipeline"],
    "ansible": ["devops", "configuration management", "automation", "provisioning"],
    "linux": ["ubuntu", "centos", "devops", "server", "shell", "bash"],
    "nginx": ["web server", "reverse proxy", "devops", "load balancing"],
    "prometheus": ["monitoring", "devops", "observability", "metrics"],
    "grafana": ["monitoring", "devops", "observability", "dashboard"],

    # Data / ML
    "machine learning": ["ml", "ai", "data science", "models", "prediction"],
    "deep learning": ["dl", "neural networks", "ai", "machine learning", "cnn", "rnn"],
    "tensorflow": ["ml", "deep learning", "ai", "keras"],
    "pytorch": ["ml", "deep learning", "ai", "torch"],
    "nlp": ["natural language processing", "ai", "text processing", "transformers"],
    "data analysis": ["analytics", "data science", "statistics", "visualization"],
    "pandas": ["data analysis", "python", "data science", "data manipulation"],
    "numpy": ["data analysis", "python", "data science", "numerical computing"],
    "spark": ["big data", "data engineering", "distributed computing", "apache spark"],
    "airflow": ["data engineering", "workflow", "orchestration", "etl"],
    "etl": ["data engineering", "data pipeline", "data warehousing"],

    # Mobile
    "react native": ["mobile", "cross-platform", "ios", "android", "javascript"],
    "flutter": ["mobile", "cross-platform", "ios", "android", "dart"],
    "ios": ["mobile", "swift", "apple", "iphone"],
    "android": ["mobile", "kotlin", "java", "google"],
    "swift": ["ios", "mobile", "apple"],
    "kotlin": ["android", "mobile", "jvm"],

    # Security
    "cybersecurity": ["security", "infosec", "information security"],
    "networking": ["network", "tcp/ip", "dns", "firewall", "infrastructure"],
    "encryption": ["cryptography", "security", "ssl", "tls"],
    "penetration testing": ["pentest", "ethical hacking", "security", "vulnerability"],
    "siem": ["security", "monitoring", "log analysis", "threat detection"],

    # General
    "git": ["version control", "github", "gitlab", "bitbucket", "source control"],
    "agile": ["scrum", "sprint", "project management", "kanban"],
    "oop": ["object oriented", "object-oriented programming", "inheritance", "polymorphism"],
    "data structures": ["algorithms", "computer science", "arrays", "linked lists", "trees"],
    "algorithms": ["data structures", "computer science", "complexity", "sorting"],
    "design patterns": ["software engineering", "architecture", "oop", "solid"],
    "microservices": ["distributed systems", "service-oriented", "architecture", "api"],
    "testing": ["unit testing", "integration testing", "qa", "test automation"],
    "selenium": ["test automation", "qa", "web testing", "browser automation"],
    "pytest": ["testing", "python", "qa", "unit testing"],
    "jest": ["testing", "javascript", "qa", "unit testing"],
}

def expand_skill(skill: str) -> set:
    """Expand a skill to include its aliases for matching."""
    key = skill.lower().strip()
    aliases = SKILL_ALIASES.get(key, set())
    return {key} | set(aliases)

def skill_matchesAny(skill: str, targets: list[str]) -> bool:
    """Check if a skill matches any of the target strings (category, topic, text)."""
    expanded = expand_skill(skill)
    for target in targets:
        t = target.lower().strip()
        if any(alias in t for alias in expanded):
            return True
    return False
