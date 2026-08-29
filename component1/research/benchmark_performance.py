"""
Performance Benchmark Script for Component 1 Pipeline
Measures runtime latency for:
- PDF extraction
- DOCX extraction
- Section detection
- Entity extraction (skills, experience, education, projects)
- Classification inference
- Job matching
- Total pipeline latency
"""

import time
from pathlib import Path
import numpy as np
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.services import parser, extractor, matcher, scorer
from ml.extractor import extract_sections
from backend.services.job_extractor import extract_job_requirements
from backend.services.predictor import Predictor

def run_benchmarks():
    print("=" * 70)
    print("COMPONENT 1: RUNTIME PERFORMANCE & LATENCY BENCHMARK")
    print("=" * 70)

    fixtures_dir = ROOT / "tests" / "fixtures"
    sample_txt = (fixtures_dir / "sample_swe_resume.txt").read_text(encoding="utf-8")
    
    sample_jd = """
    We are seeking a Senior Backend Engineer with at least 4 years of experience.
    Must have strong skills in Python, FastAPI, PostgreSQL, Docker, and REST APIs.
    AWS certification and Kubernetes experience preferred. Degree in CS or SE required.
    """

    # 1. Section Detection Latency
    t0 = time.perf_counter()
    for _ in range(50):
        _ = extract_sections(sample_txt)
    sec_time = (time.perf_counter() - t0) / 50 * 1000


    # 2. Entity & Deep Feature Extraction Latency
    t0 = time.perf_counter()
    for _ in range(50):
        _ = extractor.extract(sample_txt, target_role="Backend Developer")
    ext_time = (time.perf_counter() - t0) / 50 * 1000

    # 3. Model Classification Latency
    predictor = Predictor(model_dir=ROOT / "models")
    t0 = time.perf_counter()
    for _ in range(50):
        _ = predictor.predict(sample_txt)
    pred_time = (time.perf_counter() - t0) / 50 * 1000

    # 4. Job Description Requirement Extraction Latency
    t0 = time.perf_counter()
    for _ in range(50):
        _ = extract_job_requirements(job_description=sample_jd)
    jd_ext_time = (time.perf_counter() - t0) / 50 * 1000

    # 5. Semantic Job Matcher Latency
    jd_matcher = matcher.JDMatcher()
    t0 = time.perf_counter()
    for _ in range(50):
        _ = jd_matcher.compute(sample_txt, sample_jd)
    match_time = (time.perf_counter() - t0) / 50 * 1000

    # 6. Multi-factor Scoring Latency (S_skill, S_exp, S_edu)
    features = extractor.extract(sample_txt, target_role="Backend Developer")
    job_reqs = extract_job_requirements(job_description=sample_jd)
    t0 = time.perf_counter()
    for _ in range(50):
        _ = scorer.score(
            role="Backend Developer",
            edu_level=features.edu_level,
            experience_years=features.experience_years,
            skills=features.skills,
            candidate_education=features.education,
            required_skills_spec=job_reqs.required_skills,
            preferred_skills_spec=job_reqs.preferred_skills,
            required_years=job_reqs.required_experience_years,
            role_relevant_experience_years=features.role_relevant_experience_years,
            candidate_seniority=features.seniority,
            target_seniority=job_reqs.required_seniority,
            employment_records=features.employment_records,
            verified_certifications=features.verified_certifications,
        )
    score_time = (time.perf_counter() - t0) / 50 * 1000

    # 7. Total End-to-End Pipeline Latency
    total_time = sec_time + ext_time + pred_time + jd_ext_time + match_time + score_time

    print(f"{'Pipeline Stage':<45} | {'Average Latency':<15}")
    print("-" * 70)
    print(f"{'1. Section Segmentation':<45} | {sec_time:>10.2f} ms")
    print(f"{'2. Entity & Deep Feature Extraction':<45} | {ext_time:>10.2f} ms")
    print(f"{'3. IT Job Role Classification':<45} | {pred_time:>10.2f} ms")
    print(f"{'4. Job Description Extraction':<45} | {jd_ext_time:>10.2f} ms")
    print(f"{'5. Semantic Document Matching (TF-IDF)':<45} | {match_time:>10.2f} ms")
    print(f"{'6. Multi-Factor Scoring (S_skill, S_exp, S_edu)':<45} | {score_time:>10.2f} ms")
    print("-" * 70)
    print(f"{'TOTAL END-TO-END LATENCY':<45} | {total_time:>10.2f} ms")
    print("=" * 70)

if __name__ == "__main__":
    run_benchmarks()
