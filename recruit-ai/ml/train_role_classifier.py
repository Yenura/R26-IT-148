"""
Train a 20-role resume classifier (TF-IDF + Logistic Regression).

Generates synthetic resume data from role keywords, trains a pipeline,
and saves it to recruit-ai/backend/models/role_classifier.pkl.

Usage:
    python recruit-ai/ml/train_role_classifier.py
"""

import os
import random
import sys
import numpy as np

# ── Role definitions ──────────────────────────────────────────────────────────
ROLES = {
    "Software Engineer": [
        "python", "java", "c++", "algorithms", "data structures", "oop",
        "git", "rest api", "sql", "system design", "docker", "microservices",
    ],
    "Data Scientist": [
        "python", "r", "statistics", "machine learning", "pandas", "numpy",
        "matplotlib", "sql", "jupyter", "deep learning", "feature engineering",
    ],
    "Machine Learning Engineer": [
        "python", "tensorflow", "pytorch", "scikit-learn", "deep learning",
        "mlops", "docker", "sql", "neural network", "model deployment",
    ],
    "DevOps Engineer": [
        "linux", "docker", "kubernetes", "ci/cd", "jenkins", "terraform",
        "aws", "azure", "bash", "ansible", "monitoring", "nginx",
    ],
    "Cybersecurity Analyst": [
        "network security", "siem", "penetration testing", "firewalls",
        "ids/ips", "python", "owasp", "incident response", "vulnerability",
    ],
    "Cloud Solutions Architect": [
        "aws", "azure", "gcp", "terraform", "kubernetes", "microservices",
        "networking", "security", "cost optimization", "cloud architecture",
    ],
    "Database Administrator": [
        "sql", "postgresql", "mysql", "mongodb", "query optimization",
        "backup", "replication", "indexing", "high availability", "redis",
    ],
    "Frontend Developer": [
        "html", "css", "javascript", "react", "typescript", "responsive",
        "rest api", "git", "vue", "angular", "webpack", "accessibility",
    ],
    "Backend Developer": [
        "python", "java", "node.js", "rest api", "sql", "microservices",
        "docker", "redis", "git", "django", "flask", "fastapi",
    ],
    "Mobile App Developer": [
        "ios", "android", "flutter", "react native", "dart", "swift",
        "kotlin", "firebase", "rest api", "mobile development",
    ],
    "Full Stack Developer": [
        "react", "node.js", "python", "sql", "rest api", "docker",
        "git", "html", "css", "typescript", "mongodb", "postgresql",
    ],
    "QA/Test Automation Engineer": [
        "selenium", "pytest", "jest", "ci/cd", "api testing", "python",
        "postman", "test strategy", "automation", "cypress",
    ],
    "Data Engineer": [
        "python", "sql", "spark", "kafka", "airflow", "etl",
        "aws", "gcp", "data modeling", "hadoop", "bigquery",
    ],
    "Site Reliability Engineer": [
        "linux", "kubernetes", "prometheus", "grafana", "terraform",
        "python", "go", "ci/cd", "incident response", "monitoring",
    ],
    "UI/UX Designer": [
        "figma", "sketch", "adobe xd", "css", "html", "prototyping",
        "user research", "wireframing", "accessibility", "design systems",
    ],
    "Network Engineer": [
        "tcp/ip", "cisco", "routing", "switching", "firewalls", "vpn",
        "dns", "linux", "python", "network automation",
    ],
    "Business/Systems Analyst": [
        "sql", "requirements gathering", "uml", "bpmn", "agile", "jira",
        "stakeholder management", "data analysis", "process modeling",
    ],
    "AI/NLP Engineer": [
        "python", "tensorflow", "pytorch", "nlp", "transformers",
        "hugging face", "spacy", "deep learning", "language model",
    ],
    "Blockchain Developer": [
        "solidity", "ethereum", "web3.js", "smart contracts", "rust",
        "c++", "cryptography", "dapps", "defi",
    ],
    "Embedded Systems Engineer": [
        "c", "c++", "rust", "rtos", "microcontrollers", "arm",
        "linux kernel", "communication protocols", "firmware", "iot",
    ],
}

EDUCATION = [
    "B.Sc. Computer Science", "B.Sc. Software Engineering",
    "B.Sc. Information Technology", "M.Sc. Computer Science",
    "M.Sc. Data Science", "M.Sc. Machine Learning",
    "B.Sc. Electronic Engineering", "B.Sc. Computer Networks",
    "B.Sc. Design", "B.Sc. Information Systems",
]

EXPERIENCE_PHRASES = [
    "{y} years of experience in {skill}",
    "Worked with {skill} for {y} years",
    "Proficient in {skill}",
    "Strong background in {skill}",
    "Expertise in {skill} and related technologies",
    "Hands-on experience with {skill}",
    "Built production systems using {skill}",
]

PROJECT_PHRASES = [
    "Developed a {skill} application",
    "Built a {skill} pipeline",
    "Designed {skill} architecture",
    "Implemented {skill} solution",
    "Led migration to {skill}",
]


def _generate_resume(role: str, keywords: list[str]) -> str:
    """Generate a synthetic resume text for a given role."""
    rng = random.Random()
    parts = []

    # Education
    parts.append(f"Education: {rng.choice(EDUCATION)}")

    # Experience
    y = rng.randint(1, 12)
    parts.append(f"Experience: {y} years")
    selected = rng.sample(keywords, min(5, len(keywords)))
    for kw in selected:
        phrase = rng.choice(EXPERIENCE_PHRASES)
        parts.append(phrase.format(skill=kw, y=rng.randint(1, y)))

    # Projects
    for kw in rng.sample(keywords, min(3, len(keywords))):
        phrase = rng.choice(PROJECT_PHRASES)
        parts.append(phrase.format(skill=kw))

    # Skills section
    parts.append("Skills: " + ", ".join(selected))

    return ". ".join(parts) + "."


def main():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import Pipeline
    import joblib

    print("=" * 60)
    print("  20-Role Resume Classifier Training")
    print("=" * 60)

    # 1. Generate synthetic dataset
    texts, labels = [], []
    samples_per_role = 200
    for role, keywords in ROLES.items():
        for _ in range(samples_per_role):
            texts.append(_generate_resume(role, keywords))
            labels.append(role)

    print(f"[OK] Generated {len(texts)} synthetic resumes across {len(ROLES)} roles")

    # 2. Build pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=1.0,
            class_weight="balanced",
            multi_class="multinomial",
            solver="lbfgs",
            random_state=42,
        )),
    ])

    # 3. Cross-validate
    scores = cross_val_score(pipeline, texts, labels, cv=5, scoring="accuracy")
    print(f"[OK] 5-fold CV accuracy: {scores.mean():.3f} (+/- {scores.std():.3f})")

    # 4. Train on full dataset
    pipeline.fit(texts, labels)
    train_acc = pipeline.score(texts, labels)
    print(f"[OK] Full training accuracy: {train_acc:.3f}")

    # 5. Save
    out_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "models")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "role_classifier.pkl")
    joblib.dump({"pipeline": pipeline, "roles": list(ROLES.keys())}, out_path)
    print(f"[OK] Saved to {out_path}")
    print(f"  Model size: {os.path.getsize(out_path) / 1024:.1f} KB")

    # 6. Quick sanity check
    test_texts = [
        "Python, TensorFlow, PyTorch, deep learning, neural networks, model deployment",
        "React, JavaScript, TypeScript, HTML, CSS, responsive design, accessibility",
        "Docker, Kubernetes, Terraform, CI/CD, Linux, Ansible, monitoring",
        "SQL, PostgreSQL, query optimization, backup, replication, indexing",
    ]
    test_labels = [
        "Machine Learning Engineer",
        "Frontend Developer",
        "DevOps Engineer",
        "Database Administrator",
    ]
    print("\n[OK] Sanity checks:")
    for text, expected in zip(test_texts, test_labels):
        pred = pipeline.predict([text])[0]
        status = "PASS" if pred == expected else "FAIL"
        print(f"  {status}: '{text[:50]}...' -> {pred} (expected: {expected})")

    print("=" * 60)
    print("  Training complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
