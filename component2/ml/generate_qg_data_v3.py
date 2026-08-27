"""
Generate high-quality QG training data for Component 2.
Uses the 20 canonical IT roles and their required skills to produce
realistic interview questions with proper distractors and answers.

Output: component2/models/qg_dataset_v3.json
"""
import json
import random
import hashlib
from pathlib import Path
from typing import List, Dict

# ── Role definitions ─────────────────────────────────────────────────────────
ROLES = {
    "Software Engineer": ["python", "java", "c++", "data structures", "algorithms", "rest apis", "git", "oop", "sql", "unit testing"],
    "Data Scientist": ["python", "r", "statistics", "machine learning", "pandas", "numpy", "matplotlib", "sql", "jupyter", "data cleaning"],
    "Machine Learning Engineer": ["python", "tensorflow", "pytorch", "scikit-learn", "deep learning", "mlops", "docker", "sql", "model deployment", "feature engineering"],
    "DevOps Engineer": ["linux", "docker", "kubernetes", "ci/cd", "jenkins", "terraform", "aws", "bash", "ansible", "monitoring"],
    "Cloud Solutions Architect": ["aws", "azure", "gcp", "terraform", "kubernetes", "microservices", "networking", "iam", "serverless", "cost optimisation"],
    "Database Administrator": ["sql", "postgresql", "mysql", "mongodb", "query optimisation", "backup", "replication", "indexing", "performance tuning", "transactions"],
    "Frontend Developer": ["html", "css", "javascript", "react", "typescript", "responsive design", "rest apis", "git", "accessibility", "webpack"],
    "Backend Developer": ["python", "java", "node.js", "rest apis", "sql", "microservices", "docker", "redis", "git", "authentication"],
    "Mobile App Developer": ["flutter", "react native", "dart", "swift", "kotlin", "firebase", "rest apis", "ios", "android", "app lifecycle"],
    "Cybersecurity Analyst": ["network security", "siem", "penetration testing", "firewalls", "intrusion detection", "python", "owasp", "vulnerability assessment", "threat intelligence", "iam"],
    "Full Stack Developer": ["javascript", "react", "node.js", "python", "sql", "rest apis", "graphql", "docker", "git", "css"],
    "QA/Test Automation Engineer": ["selenium", "pytest", "junit", "test case design", "api testing", "ci/cd", "bdd", "regression testing", "jira", "python"],
    "Data Engineer": ["python", "sql", "spark", "airflow", "kafka", "etl", "data warehousing", "hdfs", "dbt", "cloud storage"],
    "Site Reliability Engineer": ["kubernetes", "prometheus", "grafana", "linux", "python", "terraform", "slo/sli", "incident management", "chaos engineering", "go"],
    "UI/UX Designer": ["figma", "wireframing", "prototyping", "user research", "usability testing", "interaction design", "design systems", "adobe xd", "accessibility", "typography"],
    "Network Engineer": ["tcp/ip", "routing protocols", "bgp", "ospf", "switching", "vlan", "vpn", "firewalls", "dns", "network automation"],
    "Business/Systems Analyst": ["requirements gathering", "uml", "bpmn", "stakeholder management", "jira", "use cases", "sql", "process modeling", "gap analysis", "agile"],
    "AI/NLP Engineer": ["python", "transformers", "pytorch", "hugging face", "nlp", "embeddings", "ner", "llm", "rag", "vector databases"],
    "Blockchain Developer": ["solidity", "ethereum", "smart contracts", "web3.js", "hardhat", "erc standards", "defi", "consensus mechanisms", "cryptography", "dapps"],
    "Embedded Systems Engineer": ["c", "c++", "rtos", "microcontrollers", "firmware", "i2c", "spi", "uart", "device drivers", "interrupts"],
}

# ── Knowledge base for realistic question generation ─────────────────────────
# Each skill has: description, common pitfalls, best practices, comparisons
SKILL_KB = {
    "python": {
        "desc": "a high-level programming language known for readability and versatility",
        "pitfalls": ["mutable default arguments", "late binding closures", "GIL limitations", "global interpreter lock contention"],
        "practices": ["use virtual environments", "follow PEP 8", "type hints for clarity", "comprehensions over loops"],
        "compare": ["java", "javascript", "ruby"],
        "tools": ["pip", "virtualenv", "pytest", "black", "mypy"],
    },
    "java": {
        "desc": "a strongly-typed, object-oriented language for enterprise applications",
        "pitfalls": ["null pointer exceptions", "memory leaks in collections", "thread safety issues", "over-engineering with patterns"],
        "practices": ["use Optional instead of null", "prefer immutability", "leverage streams API", "dependency injection"],
        "compare": ["python", "c#", "kotlin"],
        "tools": ["maven", "gradle", "junit", "spring boot", "intellij"],
    },
    "javascript": {
        "desc": "a dynamic, prototype-based language for web development",
        "pitfalls": ["type coercion bugs", "callback hell", "this keyword confusion", "event loop blocking"],
        "practices": ["use async/await", "prefer const/let over var", "strict equality checks", "modular code structure"],
        "compare": ["typescript", "python", "java"],
        "tools": ["npm", "webpack", "eslint", "jest", "react"],
    },
    "react": {
        "desc": "a JavaScript library for building user interfaces with a component-based architecture",
        "pitfalls": ["unnecessary re-renders", "stale closures in useEffect", "prop drilling", "missing dependency arrays"],
        "practices": ["use React.memo wisely", "custom hooks for logic reuse", "context for global state", "key prop optimization"],
        "compare": ["vue", "angular", "svelte"],
        "tools": ["next.js", "redux", "react router", "react query", "storybook"],
    },
    "docker": {
        "desc": "a platform for building, shipping, and running applications in containers",
        "pitfalls": ["running as root in containers", "large image sizes", "not using multi-stage builds", "hardcoding secrets in images"],
        "practices": ["use .dockerignore", "multi-stage builds", "non-root users", "minimal base images"],
        "compare": ["virtual machines", "podman", "lxc"],
        "tools": ["docker compose", "dockerfile", "docker hub", "buildx"],
    },
    "kubernetes": {
        "desc": "an orchestration platform for automating deployment, scaling, and management of containerized applications",
        "pitfalls": ["over-complicating with too many microservices", "not setting resource limits", "ignoring pod disruption budgets", "misconfigured liveness probes"],
        "practices": ["use namespaces for isolation", "horizontal pod autoscaling", "rolling deployments", "network policies"],
        "compare": ["docker swarm", "nomad", "ecs"],
        "tools": ["kubectl", "helm", "istio", "argocd", "prometheus"],
    },
    "aws": {
        "desc": "Amazon Web Services, a comprehensive cloud computing platform",
        "pitfalls": ["over-provisioning instances", "not using IAM properly", "ignoring cost monitoring", "single region deployment"],
        "practices": ["least privilege IAM", "use managed services", "cloudformation for IaC", "multi-AZ for resilience"],
        "compare": ["azure", "gcp", "on-premise"],
        "tools": ["lambda", "s3", "ec2", "rds", "cloudformation"],
    },
    "sql": {
        "desc": "a domain-specific language for managing data in relational databases",
        "pitfalls": ["N+1 query problems", "missing indexes", "not using EXPLAIN", "sql injection vulnerabilities"],
        "practices": ["use parameterized queries", "index frequently queried columns", "avoid SELECT *", "use connection pooling"],
        "compare": ["nosql", "graphql", "orm"],
        "tools": ["postgresql", "mysql", "sqlite", "pgadmin", "dbeaver"],
    },
    "machine learning": {
        "desc": "a subset of AI that enables systems to learn from data and improve over time",
        "pitfalls": ["overfitting to training data", "data leakage", "ignoring class imbalance", "not validating properly"],
        "practices": ["cross-validation", "feature scaling", "regularization", "hyperparameter tuning"],
        "compare": ["deep learning", "rule-based systems", "statistical modeling"],
        "tools": ["scikit-learn", "tensorflow", "pytorch", "jupyter", "mlflow"],
    },
    "git": {
        "desc": "a distributed version control system for tracking code changes",
        "pitfalls": ["force pushing to shared branches", "large binary files in repo", "not writing meaningful commit messages", "merge conflicts from long-lived branches"],
        "practices": ["feature branch workflow", "conventional commits", "regular pulls", "rebase before merge"],
        "compare": ["svn", "mercurial", "perforce"],
        "tools": ["github", "gitlab", "bitbucket", "git flow", "tig"],
    },
    "ci/cd": {
        "desc": "Continuous Integration and Continuous Deployment practices for automating software delivery",
        "pitfalls": ["flaky tests blocking pipelines", "not testing in production-like environments", "manual approval bottlenecks", "ignoring pipeline security"],
        "practices": ["fast feedback loops", "parallel test execution", "canary deployments", "infrastructure as code"],
        "compare": ["manual deployment", "continuous delivery", "continuous experimentation"],
        "tools": ["jenkins", "github actions", "gitlab ci", "circleci", "argocd"],
    },
    "terraform": {
        "desc": "an infrastructure-as-code tool for provisioning and managing cloud resources",
        "pitfalls": ["state file management", "not using modules for reuse", "hardcoding secrets", "drift detection gaps"],
        "practices": ["remote state storage", "workspace isolation", "plan before apply", "version pinning"],
        "compare": ["cloudformation", "pulumi", "ansible"],
        "tools": ["terraform cloud", "terragrunt", "tflint", "checkov"],
    },
    "rest apis": {
        "desc": "architectural style for designing networked applications using HTTP methods",
        "pitfalls": ["not versioning APIs", "returning excessive data", "ignoring HTTP status codes", "no rate limiting"],
        "practices": ["proper status codes", "pagination for lists", "hateoas for discoverability", "OpenAPI documentation"],
        "compare": ["graphql", "grpc", "soap"],
        "tools": ["postman", "swagger", "fastapi", "express"],
    },
    "microservices": {
        "desc": "an architectural pattern where applications are built as a collection of small, independent services",
        "pitfalls": ["distributed monolith", "data consistency issues", "too many services too early", "complex deployment"],
        "practices": ["domain-driven design", "api gateway pattern", "circuit breaker", "event-driven communication"],
        "compare": ["monolith", "serverless", "modular monolith"],
        "tools": ["kubernetes", "docker", "consul", "kafka", "istio"],
    },
    "linux": {
        "desc": "an open-source operating system kernel forming the basis of many server and embedded systems",
        "pitfalls": ["running services as root", "not monitoring disk usage", "ignoring log rotation", "weak SSH configurations"],
        "practices": ["least privilege users", "regular updates", "log monitoring", "firewall configuration"],
        "compare": ["windows server", "macos", "freebsd"],
        "tools": ["bash", "systemd", "cron", "grep", "awk"],
    },
    "security": {
        "desc": "the practice of protecting systems, networks, and data from digital attacks",
        "pitfalls": ["security through obscurity", "ignoring OWASP top 10", "not patching regularly", "weak authentication"],
        "practices": ["defense in depth", "principle of least privilege", "regular security audits", "incident response planning"],
        "compare": ["compliance-only approach", "reactive security", "zero trust"],
        "tools": ["siem", "nessus", "burp suite", "metasploit", "wireshark"],
    },
    "agile": {
        "desc": "an iterative approach to project management and software development",
        "pitfalls": ["ceremony overload", "not delivering working software", "poor backlog refinement", "ignoring retrospective actions"],
        "practices": ["sprint planning", "daily standups", "continuous improvement", "user stories over tasks"],
        "compare": ["waterfall", "kanban", "scrumban"],
        "tools": ["jira", "trello", "azure devops", "linear"],
    },
    "testing": {
        "desc": "the process of evaluating software to find defects and ensure quality",
        "pitfalls": ["testing implementation details", "brittle tests", "not testing edge cases", "ignoring test maintenance"],
        "practices": ["test pyramid", "behavior-driven development", "mutation testing", "test data management"],
        "compare": ["manual testing", "exploratory testing", "formal verification"],
        "tools": ["pytest", "jest", "selenium", "cypress", "junit"],
    },
    "networking": {
        "desc": "the practice of connecting computers and sharing resources across nodes",
        "pitfalls": ["single point of failure", "not monitoring traffic", "misconfigured DNS", "ignoring network segmentation"],
        "practices": ["redundant paths", "network monitoring", "regular backups", "security-first design"],
        "compare": ["overlay networks", "software-defined networking", "traditional networking"],
        "tools": ["wireshark", "nmap", "tcpdump", "prometheus", "snmp"],
    },
    "data structures": {
        "desc": "fundamental building blocks for organizing and storing data efficiently",
        "pitfalls": ["choosing wrong data structure", "ignoring time complexity", "not considering memory layout", "over-engineering"],
        "practices": ["understand Big-O", "choose based on access patterns", "prefer standard library", "profile before optimizing"],
        "compare": ["arrays vs linked lists", "hash tables vs trees", "stacks vs queues"],
        "tools": ["algorithms textbooks", "leetcode", "visualgo", "big-o cheat sheet"],
    },
    "algorithms": {
        "desc": "step-by-step procedures for solving computational problems",
        "pitfalls": ["premature optimization", "not considering edge cases", "ignoring space complexity", "reinventing the wheel"],
        "practices": ["understand common patterns", "test with edge cases", "analyze complexity", "use established solutions"],
        "compare": ["brute force", "divide and conquer", "dynamic programming"],
        "tools": ["leetcode", "algorithm design manuals", "complexity analyzers"],
    },
}

# ── MCQ Question Templates (role + skill aware) ──────────────────────────────
MCQ_TEMPLATES = [
    # Conceptual understanding
    "As a {role}, when would you choose {skill} over {compare}?",
    "What is the primary advantage of using {skill} in a {role} context?",
    "A {role} is evaluating {skill} for a new project. What is the main consideration?",
    "Which {skill} practice is most critical for a {role} working on production systems?",
    "What problem does {skill} solve that a {role} commonly encounters?",
    # Practical application
    "A {role} needs to implement {skill} in a high-traffic system. What approach should they take?",
    "During a code review, a {role} notices a {skill} anti-pattern. What should they recommend?",
    "A {role} is debugging a {skill}-related issue in production. What is the first step?",
    "What trade-off should a {role} consider when applying {skill} to a legacy codebase?",
    "A {role} is designing a system that heavily relies on {skill}. What architecture pattern fits best?",
    # Best practices
    "What is the most important {skill} best practice for a {role} to follow?",
    "A {role} team is adopting {skill}. What should they prioritize in the first sprint?",
    "Which {skill} configuration mistake do {role}s most commonly make?",
    "What monitoring approach should a {role} use for {skill}-based services?",
    "How should a {role} handle {skill} version upgrades in a production environment?",
    # Problem-solving
    "A {role} discovers a {skill} performance bottleneck. What optimization strategy comes first?",
    "What is the root cause of a common {skill} failure that {role}s should watch for?",
    "A {role} needs to migrate from {compare} to {skill}. What is the biggest risk?",
    "How should a {role} approach {skill} testing in a CI/CD pipeline?",
    "What security vulnerability related to {skill} should a {role} be most aware of?",
]

# ── Descriptive Question Templates ───────────────────────────────────────────
DESC_TEMPLATES = [
    "Explain how a {role} would implement {skill} in a production environment. Include key considerations and potential pitfalls.",
    "Describe the role of {skill} in the daily workflow of a {role}. What are the best practices?",
    "A {role} is tasked with optimizing a {skill}-based system. Walk through the analysis and improvement process.",
    "Compare and contrast different approaches to {skill} that a {role} might use. When is each appropriate?",
    "What are the key metrics a {role} should track when working with {skill}? How do they influence decisions?",
    "Describe a scenario where a {role} would need to make a critical decision involving {skill}. What factors matter?",
    "How does {skill} integrate with other tools in a {role}'s toolkit? Explain the ecosystem.",
    "What are the common failure modes of {skill} that a {role} should be prepared to handle?",
    "Explain the evolution of {skill} and how it affects the modern {role} role.",
    "A {role} needs to explain {skill} to a non-technical stakeholder. How would they approach this?",
]

# ── Coding Question Templates ────────────────────────────────────────────────
CODING_TEMPLATES = [
    "Implement a function that uses {skill} to solve a common {role} problem. Include test cases.",
    "Write a {skill}-based solution for a data processing task a {role} would encounter.",
    "Create a utility function using {skill} that a {role} could add to their toolkit.",
    "Implement error handling for a {skill}-based operation that a {role} would use in production.",
    "Write a {skill} integration that connects two services, as a {role} would need.",
    "Design a class or module using {skill} principles that a {role} would build.",
    "Implement a caching strategy using {skill} for a {role}'s high-performance application.",
    "Write a monitoring check using {skill} that a {role} would deploy to production.",
]

# ── Answer generation helpers ────────────────────────────────────────────────
def generate_mcq_options(skill: str, role: str, kb: dict) -> List[dict]:
    """Generate 4 MCQ options: 1 correct + 3 plausible distractors."""
    correct = f"Applying {skill} according to established best practices, considering {role}-specific requirements and production constraints."
    
    distractors = [
        f"Treating {skill} as a standalone solution without considering its integration with the broader {role} toolkit and existing architecture.",
        f"Over-engineering the {skill} implementation by introducing unnecessary complexity that doesn't address the actual {role} problem domain.",
        f"Focusing solely on {skill} performance metrics while ignoring the {role}'s broader system reliability, maintainability, and team capability constraints.",
    ]
    
    options = [{"index": 0, "text": correct}]
    for i, d in enumerate(distractors):
        options.append({"index": i + 1, "text": d})
    
    random.shuffle(options)
    correct_idx = next(i for i, o in enumerate(options) if o["index"] == 0)
    for i, o in enumerate(options):
        o["index"] = i
    
    return options, correct_idx


def generate_mcq_answer(skill: str, role: str, kb: dict) -> str:
    """Generate a brief correct answer for MCQ."""
    practices = kb.get("practices", ["follow best practices"])
    pitfalls = kb.get("pitfalls", ["common mistakes"])
    return f"Correct application of {skill} involves {practices[0]}, while avoiding {pitfalls[0]}."


def generate_descriptive_answer(skill: str, role: str, kb: dict) -> str:
    """Generate a substantive reference answer for descriptive questions."""
    desc = kb.get("desc", f"an important technology for {role}")
    practices = kb.get("practices", ["best practices"])
    pitfalls = kb.get("pitfalls", ["common pitfalls"])
    tools = kb.get("tools", ["relevant tools"])
    
    return (
        f"{skill.title()} is {desc}. For a {role}, effective use of {skill} involves several key aspects:\n\n"
        f"1. Core Principles: {practices[0].title()} and {practices[1].title() if len(practices) > 1 else 'continuous learning'}.\n"
        f"2. Common Pitfalls: {pitfalls[0].title()} and {pitfalls[1].title() if len(pitfalls) > 1 else 'inadequate testing'}.\n"
        f"3. Tooling: Integration with {tools[0]} and {tools[1] if len(tools) > 1 else 'related tools'}.\n"
        f"4. Production Considerations: Monitor {skill}-based services for {pitfalls[0]}, implement proper logging, and ensure team knowledge sharing.\n"
        f"5. Continuous Improvement: Regular retrospectives on {skill} usage, staying updated with ecosystem changes, and measuring impact on {role} productivity."
    )


def generate_coding_solution(skill: str, role: str) -> dict:
    """Generate a coding problem with test cases."""
    problems = {
        "python": {
            "description": f"Write a Python function that processes a list of {role} metrics and returns aggregated statistics.",
            "template": "def process_metrics(metrics: list[dict]) -> dict:\n    '''Process metrics and return aggregated stats.'''\n    pass",
            "test_cases": [
                {"input": "[{'cpu': 80, 'mem': 60}, {'cpu': 90, 'mem': 70}]", "expected": "{'avg_cpu': 85.0, 'avg_mem': 65.0, 'count': 2}"},
                {"input": "[{'cpu': 50}]", "expected": "{'avg_cpu': 50.0, 'avg_mem': 0, 'count': 1}"},
            ],
            "complexity": "O(n)",
        },
        "sql": {
            "description": f"Write a SQL query to analyze {role} performance data from a metrics table.",
            "template": "SELECT role, AVG(efficiency) as avg_efficiency FROM performance_metrics WHERE date >= DATE_SUB(NOW(), INTERVAL 30 DAY) GROUP BY role HAVING avg_efficiency > 0.7 ORDER BY avg_efficiency DESC;",
            "test_cases": [
                {"input": "performance_metrics with 3 roles", "expected": "Filtered and sorted role performance"},
            ],
            "complexity": "O(n log n)",
        },
        "javascript": {
            "description": f"Write a JavaScript function to validate {role} configuration objects.",
            "template": "function validateConfig(config) {\n  // Validate config has required fields\n  return { valid: true, errors: [] };\n}",
            "test_cases": [
                {"input": "{name: 'test', version: '1.0'}", "expected": "{valid: true, errors: []}"},
                {"input": "{}", "expected": "{valid: false, errors: ['Missing required fields']}"},
            ],
            "complexity": "O(1)",
        },
    }
    
    default = {
        "description": f"Implement a {skill}-based solution for a common {role} task.",
        "template": f"// Implement {skill} solution\nfunction solution(input) {{\n  // Your code here\n}}",
        "test_cases": [
            {"input": "sample_input", "expected": "expected_output"},
        ],
        "complexity": "O(n)",
    }
    
    return problems.get(skill, default)


# ── Main generation ──────────────────────────────────────────────────────────
def generate_dataset() -> List[dict]:
    """Generate the complete QG training dataset."""
    examples = []
    seen = set()
    
    for role, skills in ROLES.items():
        for skill in skills:
            kb = SKILL_KB.get(skill, {
                "desc": f"a technology used by {role}s",
                "pitfalls": ["common mistakes"],
                "practices": ["best practices"],
                "compare": ["alternatives"],
                "tools": ["related tools"],
            })
            
            # Generate MCQ questions (5 per skill)
            for _ in range(5):
                template = random.choice(MCQ_TEMPLATES)
                compare_skill = random.choice(kb.get("compare", [skill]))
                question = template.format(role=role, skill=skill, compare=compare_skill)
                options, correct_idx = generate_mcq_options(skill, role, kb)
                
                answer = generate_mcq_answer(skill, role, kb)
                
                example = {
                    "input": f"[MCQ] {role} | {skill} | {random.choice(['Easy', 'Medium', 'Hard'])}",
                    "output": f"Q: {question}\nO: " + " | ".join(o["text"] for o in options) + f"\nA: {correct_idx}",
                    "type": "mcq",
                    "role": role,
                    "skill": skill,
                    "difficulty": random.choice(["Easy", "Medium", "Hard"]),
                }
                
                key = hashlib.md5(example["input"].encode()).hexdigest()
                if key not in seen:
                    seen.add(key)
                    examples.append(example)
            
            # Generate Descriptive questions (4 per skill)
            for _ in range(4):
                template = random.choice(DESC_TEMPLATES)
                question = template.format(role=role, skill=skill)
                answer = generate_descriptive_answer(skill, role, kb)
                keywords = ", ".join(kb.get("practices", [])[:3])
                
                example = {
                    "input": f"[Descriptive] {role} | {skill} | {random.choice(['Medium', 'Hard'])}",
                    "output": f"Q: {question}\nA: {answer}\nK: {keywords}",
                    "type": "descriptive",
                    "role": role,
                    "skill": skill,
                    "difficulty": random.choice(["Medium", "Hard"]),
                }
                
                key = hashlib.md5(example["input"].encode()).hexdigest()
                if key not in seen:
                    seen.add(key)
                    examples.append(example)
            
            # Generate Coding questions (3 per skill, only for relevant skills)
            coding_skills = {"python", "java", "javascript", "sql", "c++", "go", "rust", "react", "node.js", "typescript"}
            if skill in coding_skills:
                for _ in range(3):
                    template = random.choice(CODING_TEMPLATES)
                    question = template.format(role=role, skill=skill)
                    problem = generate_coding_solution(skill, role)
                    
                    example = {
                        "input": f"[Coding] {role} | {skill} | {random.choice(['Medium', 'Hard'])}",
                        "output": f"Q: {question}\nL: {skill.title()}\nT: {json.dumps(problem['test_cases'])}\nC: {problem['complexity']}",
                        "type": "coding",
                        "role": role,
                        "skill": skill,
                        "difficulty": random.choice(["Medium", "Hard"]),
                    }
                    
                    key = hashlib.md5(example["input"].encode()).hexdigest()
                    if key not in seen:
                        seen.add(key)
                        examples.append(example)
    
    return examples


if __name__ == "__main__":
    print("Generating QG training dataset v3...")
    examples = generate_dataset()
    
    # Split 90/10
    random.shuffle(examples)
    split = int(len(examples) * 0.9)
    train = examples[:split]
    val = examples[split:]
    
    dataset = {"train": train, "val": val}
    
    out_path = Path("component2/models/qg_dataset_v3.json")
    out_path.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"Generated {len(examples)} examples ({len(train)} train, {len(val)} val)")
    
    # Stats
    from collections import Counter
    types = Counter(e["type"] for e in examples)
    roles = Counter(e["role"] for e in examples)
    diffs = Counter(e["difficulty"] for e in examples)
    
    print(f"By type: {dict(types)}")
    print(f"By difficulty: {dict(diffs)}")
    print(f"Roles: {len(roles)} (avg {len(examples)//len(roles)} per role)")
    print(f"Saved to: {out_path}")
