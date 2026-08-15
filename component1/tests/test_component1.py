"""
Unit Tests for Component 1 — AI Resume Screening & IT Job Role Classification
IT22094872 | Dulnith K.D. | R26-IT-148
"""

import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

import sys, os
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from ml.extractor import (
    clean_text,
    extract_education_level,
    extract_experience_years,
    extract_skills_and_certifications,
)
from ml.feature_engineering import (
    compute_s_edu,
    compute_s_exp,
    compute_s_skill,
    extract_cv_features,
)
from backend.services.predictor import Predictor
from backend.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_text_cleaning_and_pii_removal():
    raw_cv = """
    John Doe
    Email: john.doe@example.com
    Phone: +1 (555) 019-2834
    Website: https://johndoe.dev
    Location: 12345 Main St
    Experienced Backend Developer with Python, FastAPI, and PostgreSQL.
    """
    cleaned = clean_text(raw_cv)
    assert "john.doe@example.com" not in cleaned
    assert "+1 (555)" not in cleaned
    assert "https://johndoe.dev" not in cleaned
    assert "Python" in cleaned
    assert "FastAPI" in cleaned
    assert "PostgreSQL" in cleaned


def test_experience_extraction():
    text1 = "Worked for 5+ years of experience in software engineering."
    text2 = "Experience: Jan 2020 - Dec 2023 at Tech Corp."
    assert extract_experience_years(text1) == 5.0
    assert extract_experience_years(text2) == 3.0


def test_education_extraction():
    cv_phd = "Holds a Ph.D. in Computer Science from Stanford University."
    cv_bsc = "B.Sc. in Information Technology, SLIIT."
    
    edu_phd = extract_education_level(cv_phd)
    edu_bsc = extract_education_level(cv_bsc)

    assert edu_phd["level_name"] == "PhD"
    assert edu_phd["level_score"] == 1.00

    assert edu_bsc["level_name"] == "BSc"
    assert edu_bsc["level_score"] == 0.60


def test_skill_extraction():
    cv_text = "Proficient in Python, Django, Docker, Kubernetes, AWS, and MySQL."
    extracted = extract_skills_and_certifications(cv_text)
    detected = extracted["detected_skills"]

    assert "python" in detected
    assert "django" in detected
    assert "docker" in detected
    assert "kubernetes" in detected
    assert "aws" in detected
    assert "mysql" in detected


def test_feature_engineering_scores():
    skills = ["python", "java", "c++", "git", "rest apis", "sql"]
    s_skill = compute_s_skill(skills, "Software Engineer")
    s_exp = compute_s_exp(3.0, "Software Engineer")
    
    edu_info = {"level_score": 0.60, "majors": ["Software Engineering"]}
    s_edu = compute_s_edu(edu_info, "Software Engineer")

    assert 0.0 <= s_skill <= 1.0
    assert 0.0 <= s_exp <= 1.0
    assert 0.0 <= s_edu <= 1.0
    assert s_exp == 1.0  # 3.0 yrs / 3.0 yrs required = 1.0


def test_predictor_model_inference():
    predictor = Predictor(model_dir=ROOT / "models")
    cv_text = """
    Backend Developer with 4 years experience.
    Proficient in Python, FastAPI, Django, PostgreSQL, Docker, Redis, and REST APIs.
    B.Sc. in Computer Science.
    """
    pred = predictor.predict(cv_text)

    assert pred.job_role is not None
    assert pred.confidence > 0.0
    assert len(pred.alternatives) > 0
    assert "S_skill" in pred.feature_scores


def test_fastapi_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok"


def test_fastapi_screen_resume_endpoint(client):
    cv_content = """
    Experienced Backend Developer with 3 years of hands-on expertise in Python, FastAPI, PostgreSQL, Docker, and REST APIs.
    Education: B.Sc. in Computer Science, SLIIT (2020).
    Certifications: AWS Certified Solutions Architect.
    """
    file_bytes = io.BytesIO(cv_content.encode("utf-8"))

    response = client.post(
        "/api/v1/screen-resume",
        files={"file": ("sample_resume.txt", file_bytes, "text/plain")}
    )

    assert response.status_code == 200
    data = response.json()

    assert "predicted_role" in data
    assert "confidence" in data
    assert "screening_score" in data
    assert "scores" in data
    assert "detected_skills" in data
    assert "top_roles" in data
    assert data["screening_score"] > 0.0
