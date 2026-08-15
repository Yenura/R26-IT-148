"""
Unit Tests for Component 4 — Skill Gap Analysis & Career Development
IT22094872 | Dulnith K.D. | R26-IT-148
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "backend"))

from src.preprocessing.skill_normalizer import normalize_skill, normalize_skills
from src.gap_analysis.similarity import jaccard_similarity, weighted_skill_similarity
from src.gap_analysis.priority import compute_priority_score
from src.gap_analysis.skill_gap import analyze_skill_gap
from src.recommendation.career_recommender import recommend_career_paths
from src.recommendation.learning_path import generate_learning_path
from backend.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_1_skill_normalization():
    assert normalize_skill("py") == "Python"
    assert normalize_skill("js") == "JavaScript"
    assert normalize_skill("reactjs") == "React"


def test_2_skill_alias_handling():
    skills = ["js", "py", "react.js", "docker"]
    normalized = normalize_skills(skills)
    assert "JavaScript" in normalized
    assert "Python" in normalized
    assert "React" in normalized
    assert "Docker" in normalized


def test_3_skill_matching_and_gap_calculation():
    current = ["Python", "SQL", "Pandas"]
    target = "Data Scientist"
    result = analyze_skill_gap(current, target)
    
    assert result["target_role"] == "Data Scientist"
    assert "Python" in result["matched_skills"]
    assert "SQL" in result["matched_skills"]
    
    missing_names = result["missing_skill_names"]
    assert len(missing_names) > 0


def test_4_skill_coverage():
    current = ["Python", "SQL", "Pandas"]
    target = "Data Scientist"
    result = analyze_skill_gap(current, target)
    
    coverage = result["skill_coverage"]
    pct = result["skill_coverage_percentage"]
    assert 0.0 <= coverage <= 1.0
    assert 0.0 <= pct <= 100.0


def test_5_priority_calculation():
    score, category = compute_priority_score("Machine Learning", importance_level="high", market_freq_pct=90.0, dependency_score_pct=85.0)
    assert 0.0 <= score <= 100.0
    assert category in ["Critical", "High", "Medium", "Low"]


def test_6_jaccard_similarity():
    skills_a = ["Python", "SQL", "Pandas"]
    skills_b = ["Python", "SQL", "Machine Learning", "Statistics"]
    sim = jaccard_similarity(skills_a, skills_b)
    # Intersection = 2 (Python, SQL), Union = 5 (Python, SQL, Pandas, Machine Learning, Statistics) -> 2/5 = 0.4
    assert sim == 0.4


def test_7_career_recommendations():
    current_skills = ["Python", "SQL", "FastAPI", "PostgreSQL"]
    res = recommend_career_paths(current_skills, current_role="Backend Developer")
    
    assert res["current_role"] == "Backend Developer"
    assert len(res["recommendations"]) > 0
    rec = res["recommendations"][0]
    assert "role" in rec
    assert "match_percentage" in rec
    assert "missing_skills" in rec


def test_8_learning_path_generation():
    current_skills = ["Python", "SQL"]
    target_role = "Data Scientist"
    res = generate_learning_path(current_skills, target_role)
    
    assert res["target_role"] == "Data Scientist"
    path = res["learning_path"]
    assert len(path) > 0
    assert path[0]["step"] == 1
    assert "skill" in path[0]
    assert "priority" in path[0]


def test_9_api_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_10_api_skill_gap_endpoint(client):
    payload = {
        "current_skills": ["Python", "SQL", "Pandas"],
        "target_role": "Data Scientist"
    }
    response = client.post("/api/v1/skill-gap", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_role"] == "Data Scientist"
    assert "skill_coverage" in data
    assert "matched_skills" in data
    assert "missing_skills" in data


def test_11_api_career_recommendation_endpoint(client):
    payload = {
        "current_skills": ["Python", "SQL", "FastAPI", "PostgreSQL"],
        "current_role": "Backend Developer"
    }
    response = client.post("/api/v1/career-recommendation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["current_role"] == "Backend Developer"
    assert len(data["recommendations"]) > 0


def test_12_api_learning_path_endpoint(client):
    payload = {
        "current_skills": ["Python", "SQL"],
        "target_role": "Data Scientist"
    }
    response = client.post("/api/v1/learning-path", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_role"] == "Data Scientist"
    assert len(data["learning_path"]) > 0


def test_13_api_skill_gap_simulation(client):
    payload = {
        "current_skills": ["Python", "SQL"],
        "acquired_skills": ["Machine Learning", "Statistics"],
        "target_role": "Data Scientist"
    }
    response = client.post("/api/v1/skill-gap/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["simulated_coverage"] > data["original_coverage"]
    assert data["coverage_improvement"] > 0


def test_14_api_skill_dependency_graph(client):
    response = client.get("/api/v1/skill-gap/graph")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0

