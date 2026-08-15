"""Unit & Integration Tests — Component 1 Independent Scores & Job-Specific Matching
IT22094872 | Dulnith K.D. | R26-IT-148

Tests 3 independent scores: S_skill, S_exp, S_edu for Component 3 candidate ranking contract.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from backend.services.scorer import score, calculate_skill_score, calculate_experience_score, calculate_education_score


def test_1_backend_developer_partial_match():
    """TEST 1:
    Job: Backend Developer
    Required: Python, FastAPI, PostgreSQL, Docker (4 skills), 3 years experience, BSc IT
    Candidate: Python, FastAPI, PostgreSQL (3 skills), 2 years experience, BSc IT
    Expected: S_skill = 75.0, S_exp ≈ 66.67, S_edu = 100.0
    """
    req_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    req_years = 3.0
    req_edu = ["BSc Information Technology"]

    cand_skills = ["Python", "FastAPI", "PostgreSQL"]
    cand_years = 2.0
    cand_edu = "BSc Information Technology"

    result = score(
        role="Backend Developer",
        edu_level=2,
        experience_years=cand_years,
        skills=cand_skills,
        required_skills_spec=req_skills,
        required_years=req_years,
        required_education=req_edu,
        candidate_education=cand_edu,
    )

    assert result.S_skill == 75.0, f"Expected S_skill 75.0, got {result.S_skill}"
    assert result.S_exp == pytest.approx(66.67, abs=0.1), f"Expected S_exp ≈ 66.67, got {result.S_exp}"
    assert result.S_edu == 100.0, f"Expected S_edu 100.0, got {result.S_edu}"

    # Verify component_1_scores data contract
    assert "S_skill" in result.component_1_scores.to_dict()
    assert "S_exp" in result.component_1_scores.to_dict()
    assert "S_edu" in result.component_1_scores.to_dict()


def test_2_backend_developer_full_match_and_experience_cap():
    """TEST 2:
    Job: Backend Developer
    Required: Python, FastAPI, PostgreSQL, Docker, 3 years experience, BSc IT
    Candidate: Python, FastAPI, PostgreSQL, Docker, 5 years experience, BSc IT
    Expected: S_skill = 100.0, S_exp = 100.0 (capped from 166.67), S_edu = 100.0
    """
    req_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    req_years = 3.0
    req_edu = ["BSc Information Technology"]

    cand_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    cand_years = 5.0
    cand_edu = "BSc Information Technology"

    result = score(
        role="Backend Developer",
        edu_level=2,
        experience_years=cand_years,
        skills=cand_skills,
        required_skills_spec=req_skills,
        required_years=req_years,
        required_education=req_edu,
        candidate_education=cand_edu,
    )

    assert result.S_skill == 100.0, f"Expected S_skill 100.0, got {result.S_skill}"
    assert result.S_exp == 100.0, f"Expected S_exp 100.0 (capped), got {result.S_exp}"
    assert result.S_edu == 100.0, f"Expected S_edu 100.0, got {result.S_edu}"


def test_3_job_specific_matching_data_scientist():
    """TEST 3:
    Different target role (Data Scientist vs Backend Developer).
    Candidate with Backend skills applying to Data Scientist receives lower S_skill.
    Proves job-specific matching.
    """
    ds_skills = ["Python", "Pandas", "Machine Learning", "Statistics"]
    cand_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]

    ds_result = score(
        role="Data Scientist",
        edu_level=2,
        experience_years=2.0,
        skills=cand_skills,
        required_skills_spec=ds_skills,
        required_years=3.0,
    )

    # Only Python matches among 4 DS skills -> 25%
    assert ds_result.S_skill == 25.0, f"Expected S_skill 25.0 for Data Scientist job, got {ds_result.S_skill}"


def test_weighted_skill_matching():
    """Test skill matching with importance weights."""
    weighted_spec = [
        {"skill": "Python", "importance": 1.0},
        {"skill": "FastAPI", "importance": 1.0},
        {"skill": "PostgreSQL", "importance": 0.8},
        {"skill": "Docker", "importance": 0.7},
        {"skill": "Git", "importance": 0.5},
    ]  # Total weight = 4.0

    cand_skills = ["Python", "FastAPI", "PostgreSQL", "Git"]  # Weight = 1.0 + 1.0 + 0.8 + 0.5 = 3.3
    # Score = (3.3 / 4.0) * 100 = 82.5

    s_skill, analysis = calculate_skill_score(cand_skills, weighted_spec)
    assert s_skill == pytest.approx(82.5, abs=0.1)
    assert analysis.matched_count == 4
    assert "Docker" in analysis.missing_skills
