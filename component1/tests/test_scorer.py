"""Unit tests — scorer
IT22094872 | Dulnith K.D. | R26-IT-148
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
        assert 0.0 <= result.S_edu <= 1.0

    @pytest.mark.parametrize("role", ALL_ROLES[:5])
    def test_s_exp_in_range(self, role):
        result = score(role=role, edu_level=2, experience_years=3.0, skills=[])
        assert 0.0 <= result.S_exp <= 1.0

    @pytest.mark.parametrize("role", ALL_ROLES[:5])
    def test_s_skill_in_range(self, role):
        result = score(role=role, edu_level=2, experience_years=3.0, skills=["python", "sql"])
        assert 0.0 <= result.S_skill <= 1.0

    @pytest.mark.parametrize("role", ALL_ROLES[:5])
    def test_cv_matching_score_in_range(self, role):
        result = score(role=role, edu_level=2, experience_years=3.0, skills=["python"])
        assert 0.0 <= result.cv_matching_score <= 100.0

    def test_skill_score_raw_alias(self):
        result = score(role="Software Engineer", edu_level=2, experience_years=3.0, skills=["python", "sql"])
        assert result.skill_score_raw == result.S_skill

    def test_zero_experience_gives_zero_s_exp(self):
        result = score(role="Software Engineer", edu_level=2, experience_years=0.0, skills=[])
        assert result.S_exp == pytest.approx(0.0)

    def test_high_experience_capped_at_one(self):
        result = score(role="Software Engineer", edu_level=2, experience_years=100.0, skills=[])
        assert result.S_exp == pytest.approx(1.0)

    def test_no_jd_gives_none_similarity(self):
        result = score(role="Software Engineer", edu_level=2, experience_years=3.0, skills=["python"])
        assert result.jd_similarity_score is None

    def test_jd_similarity_included_in_score(self):
        result_no_jd  = score(role="Software Engineer", edu_level=2, experience_years=3.0, skills=["python"])
        result_with_jd = score(role="Software Engineer", edu_level=2, experience_years=3.0,
                               skills=["python"], jd_similarity_score=0.9)
        assert result_with_jd.jd_similarity_score == pytest.approx(0.9)
        # Higher JD similarity should push cv_matching_score up
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
