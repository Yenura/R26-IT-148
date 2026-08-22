import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "recruit-ai", "backend"))

from services.resume_parser import parse_resume_file, extract_entities, preprocess_text
from services.role_classifier import RoleClassifier
from services.semantic_matcher import SemanticMatcher

sample_resume = """
ALEX MORGAN
alex.morgan@email.com | +1 (555) 019-2834 | San Francisco, CA
LinkedIn: linkedin.com/in/alexmorgan-dev | GitHub: github.com/alexmorgan

PROFESSIONAL SUMMARY
Senior Full Stack Engineer with 6+ years of experience building scalable distributed web applications,
high-throughput REST APIs, and microservices in Python, FastAPI, React, Node.js, and PostgreSQL.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, SQL, HTML, CSS, Bash
Frameworks: FastAPI, React, Node.js, Express, Django, Flask, Tailwind
Databases: PostgreSQL, Redis, MongoDB, MySQL
Cloud & DevOps: AWS (EC2, S3, RDS, Lambda), Docker, Kubernetes, CI/CD, Terraform, Linux
Tools & Practices: Git, Microservices, Agile, REST APIs, GraphQL, Unit Testing, JIRA

WORK EXPERIENCE
Senior Full Stack Developer | Acme Cloud Solutions | Jan 2022 – Present
- Architected and built high-performance microservices using Python FastAPI and React.
- Reduced API response latency by 45% through Redis caching and PostgreSQL query indexing.
- Led CI/CD automation pipeline using Docker and GitHub Actions.

Full Stack Software Engineer | Horizon Tech Labs | Mar 2019 – Dec 2021
- Developed responsive web interfaces using React, Redux, and TypeScript.
- Designed RESTful API endpoints and integrated PostgreSQL with SQLAlchemy ORM.
- Collaborated in an agile scrum team of 8 engineers.

EDUCATION
B.Sc. in Computer Science & Software Engineering | Tech University (2015 – 2019)
GPA: 3.8 / 4.0 | Dean's Honor List

PROJECTS
Cloud Task Orchestrator (Personal Project, 2023 - Present)
- Distributed job scheduler built with Python, Celery, Redis, and FastAPI.
"""

def profile_cv_pipeline():
    print("=" * 60)
    print("PROFILING CV EXTRACTION & MATCHING PIPELINE")
    print("=" * 60)

    # 1. Text extraction & Preprocessing
    t0 = time.perf_counter()
    for _ in range(50):
        preprocessed = preprocess_text(sample_resume)
    t1 = time.perf_counter()
    print(f"1. Preprocess Text (50 iterations): {(t1 - t0) * 1000 / 50:.3f} ms / call")

    # 2. Entity Extraction (Skills, Exp, Edu)
    t0 = time.perf_counter()
    for _ in range(50):
        entities = extract_entities(sample_resume)
    t1 = time.perf_counter()
    print(f"2. Extract Entities (50 iterations): {(t1 - t0) * 1000 / 50:.3f} ms / call")
    print(f"   - Extracted Skills ({len(entities.get('skills', []))}): {entities.get('skills', [])[:6]}...")
    print(f"   - Experience: {entities.get('experience_years')} yrs")
    print(f"   - Education: {entities.get('education')}")

    # 3. Role Classifier Loading & Inference
    t0 = time.perf_counter()
    clf = RoleClassifier()
    t1 = time.perf_counter()
    print(f"3. RoleClassifier Init: {(t1 - t0) * 1000:.3f} ms")

    t0 = time.perf_counter()
    for _ in range(100):
        role, conf = clf.predict(sample_resume, entities.get("skills", []))
    t1 = time.perf_counter()
    print(f"4. RoleClassifier Inference (100 iter): {(t1 - t0) * 1000 / 100:.3f} ms / call -> '{role}' (conf: {conf:.2f})")

    # 5. Semantic Matcher
    matcher = SemanticMatcher()
    t0 = time.perf_counter()
    for _ in range(50):
        sim = matcher.compute_similarity(sample_resume, "Full Stack Developer required skills: React, Python, PostgreSQL, Docker, AWS")
    t1 = time.perf_counter()
    print(f"5. SemanticMatcher (50 iter): {(t1 - t0) * 1000 / 50:.3f} ms / call -> Sim: {sim:.1f}%")

    print("=" * 60)

if __name__ == "__main__":
    profile_cv_pipeline()
