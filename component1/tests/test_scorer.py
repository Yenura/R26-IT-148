"""Unit tests — scorer
IT22089236 | D T D Perera | R26-IT-148
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from backend.services.scorer import score
from data.role_requirements import ALL_ROLES


class TestScoreBounds:
    @pytest.mark.parametrize("role", ALL_ROLES[:5])
    def test_s_edu_in_range(self, role):
        result = score(role=role, edu_level=2, experience_years=3.0, skills=["python", "sql"])
        assert 0.0 <= result.S_edu <= 100.0

    @pytest.mark.parametrize("role", ALL_ROLES[:5])
    def test_s_exp_in_range(self, role):
        result = score(role=role, edu_level=2, experience_years=3.0, skills=[])
        assert 0.0 <= result.S_exp <= 100.0

    @pytest.mark.parametrize("role", ALL_ROLES[:5])
    def test_s_skill_in_range(self, role):
        result = score(role=role, edu_level=2, experience_years=3.0, skills=["python", "sql"])
        assert 0.0 <= result.S_skill <= 100.0

    @pytest.mark.parametrize("role", ALL_ROLES[:5])
    def test_cv_matching_score_in_range(self, role):
        result = score(role=role, edu_level=2, experience_years=3.0, skills=["python"])
        assert 0.0 <= result.cv_matching_score <= 100.0

    def test_skill_score_raw_alias(self):
        result = score(role="Software Engineer", edu_level=2, experience_years=3.0, skills=["python", "sql"])
        assert result.skill_score_raw == pytest.approx(result.S_skill / 100.0)

    def test_zero_experience_gives_zero_s_exp(self):
        result = score(role="Software Engineer", edu_level=2, experience_years=0.0, skills=[])
        assert result.S_exp == pytest.approx(0.0)

    def test_high_experience_capped_at_hundred(self):
        result = score(role="Software Engineer", edu_level=2, experience_years=100.0, skills=[])
        assert result.S_exp == pytest.approx(100.0)

    def test_no_jd_gives_none_similarity(self):
        result = score(role="Software Engineer", edu_level=2, experience_years=3.0, skills=["python"])
        assert result.jd_similarity_score is None

    def test_jd_similarity_included_in_score(self):
        result_no_jd  = score(role="Software Engineer", edu_level=2, experience_years=3.0, skills=["python"])
        result_with_jd = score(role="Software Engineer", edu_level=2, experience_years=3.0,
                               skills=["python"], jd_similarity_score=0.9)
        assert result_with_jd.jd_similarity_score == pytest.approx(0.9)
        assert result_with_jd.cv_matching_score >= result_no_jd.cv_matching_score * 0.5

    def test_edu_level_scores_match_component3(self):
        """S_edu values must match component3 EDU_LEVEL_SCORES exactly."""
        from data.role_requirements import EDU_LEVEL_SCORES
        expected = {1: 0.40, 2: 0.60, 3: 0.80, 4: 1.00}
        assert EDU_LEVEL_SCORES == expected

    def test_all_20_roles_scoreable(self):
        for role in ALL_ROLES:
            result = score(role=role, edu_level=2, experience_years=2.0, skills=["python"])
            assert 0.0 <= result.cv_matching_score <= 100.0

    def test_skill_match_collision_guards(self):
        """Verify that single-letter skills, short abbreviations, and false collisions do not cause false positives."""
        from backend.services.scorer import is_skill_match, calculate_skill_score

        # 1. C language must NOT match words containing the letter 'c'
        assert not is_skill_match("Docker", "C")
        assert not is_skill_match("React", "C")
        assert not is_skill_match("Statistics", "C")
        assert not is_skill_match("Machine Learning", "C")
        assert not is_skill_match("C++", "C")
        assert not is_skill_match("C#", "C")
        assert is_skill_match("C", "C")

        # 2. R language must NOT match words containing 'r'
        assert not is_skill_match("Docker", "R")
        assert not is_skill_match("Terraform", "R")
        assert is_skill_match("R", "R")

        # 3. Go must NOT match 'mongodb', 'django', 'algorithms'
        assert not is_skill_match("MongoDB", "Go")
        assert not is_skill_match("Django", "Go")
        assert not is_skill_match("Algorithms", "Go")
        assert is_skill_match("Go", "Golang")

        # 4. Java must NOT match JavaScript
        assert not is_skill_match("Java", "JavaScript")
        assert not is_skill_match("JavaScript", "Java")

        # 5. SQL must NOT match NoSQL
        assert not is_skill_match("SQL", "NoSQL")

        # 6. Real company job matching evaluation
        company_job_skills = ["React", "TypeScript", "Tailwind CSS", "Docker"]
        candidate_skills = ["C", "R", "Go", "Java"]
        # Candidate has none of the 4 required skills -> score must be 0.0!
        s_skill, analysis = calculate_skill_score(candidate_skills, company_job_skills)
        assert s_skill == 0.0
        assert analysis.matched_count == 0
        assert len(analysis.missing_skills) == 4

        # Candidate with real matching skills
        qualified_skills = ["React.js", "TypeScript", "Tailwind"]
        s_skill2, analysis2 = calculate_skill_score(qualified_skills, company_job_skills)
        assert analysis2.matched_count == 3  # React, TypeScript, Tailwind CSS match
        assert s_skill2 == 75.0
        assert "Docker" in analysis2.missing_skills
