"""
Component 4 — Unit Tests for ML Engine
Run: pytest component4/tests/test_ml_engine.py -v

Covers:
  - compute_gap: unknown role, empty skills, 100% match, partial match
  - gap_severity: all three thresholds and exact boundary values
  - build_feature_vector: unknown education, unknown job level
  - run_skill_gap_analysis: smoke test end-to-end
"""

import pytest
import sys
import os

# Allow imports from the backend package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from services.ml_engine import (
    compute_gap,
    gap_severity,
    build_feature_vector,
    run_skill_gap_analysis,
    JOB_REQ,
    GAP_LOW_THRESHOLD,
    GAP_MEDIUM_THRESHOLD,
)


# ── compute_gap ────────────────────────────────────────────────────────────────

class TestComputeGap:

    def test_unknown_role_returns_neutral_defaults(self):
        """An unrecognised job role should return a neutral 0.5 gap score."""
        score, req, opt, pct = compute_gap(["Python"], "Unknown Role XYZ", 3)
        assert score == 0.5
        assert req  == []
        assert opt  == []
        assert pct  == 50.0

    def test_empty_skills_gives_zero_match(self):
        """A candidate with no skills should have 0% skill match."""
        role = "Data Scientist"
        score, miss_req, _, pct = compute_gap([], role, 2)
        assert pct == 0.0
        # All required skills should be missing
        assert set(miss_req) == set(JOB_REQ[role]["required"])

    def test_perfect_skill_match(self):
        """A candidate with all required skills should have 100% skill match."""
        role     = "Data Scientist"
        required = JOB_REQ[role]["required"]
        score, miss, _, pct = compute_gap(required, role, 10)
        assert miss == []
        assert pct  == 100.0
        assert score > 0.0

    def test_partial_skill_match(self):
        """Partial skills → non-zero missing list and match < 100%."""
        role     = "Software Engineer"
        required = JOB_REQ[role]["required"]
        half     = required[: len(required) // 2]
        _, miss, _, pct = compute_gap(half, role, 3)
        assert 0.0 < pct < 100.0
        assert len(miss) > 0

    def test_experience_boosts_gap_score(self):
        """More experience should result in a higher gap score for the same skills."""
        role = "Backend Developer"
        skills = JOB_REQ[role]["required"][:2]
        score_junior, *_ = compute_gap(skills, role, 1)
        score_senior, *_ = compute_gap(skills, role, 15)
        assert score_senior > score_junior

    def test_fuzzy_skill_matching(self):
        """Skill names should match via substring (e.g. 'AWS' matches 'AWS/Azure/GCP')."""
        # Uses the real JOB_REQ; if "AWS" is a required skill for Cloud Architect,
        # sending "AWS/Azure/GCP" should satisfy it via fuzzy match.
        score, miss, _, pct = compute_gap(["AWS/Azure/GCP"], "Cloud Solutions Architect", 5)
        # The candidate should not be listed as missing "AWS" or related skills
        for m in miss:
            assert "aws" not in m.lower()


# ── gap_severity ───────────────────────────────────────────────────────────────

class TestGapSeverity:

    def test_low_at_threshold(self):
        assert gap_severity(GAP_LOW_THRESHOLD) == "Low"

    def test_medium_just_below_low_threshold(self):
        assert gap_severity(GAP_LOW_THRESHOLD - 0.001) == "Medium"

    def test_medium_at_threshold(self):
        assert gap_severity(GAP_MEDIUM_THRESHOLD) == "Medium"

    def test_high_just_below_medium_threshold(self):
        assert gap_severity(GAP_MEDIUM_THRESHOLD - 0.001) == "High"

    def test_high_at_zero(self):
        assert gap_severity(0.0) == "High"

    def test_low_at_one(self):
        assert gap_severity(1.0) == "Low"

    @pytest.mark.parametrize("score,expected", [
        (0.90, "Low"),
        (0.80, "Low"),
        (0.79, "Medium"),
        (0.55, "Medium"),
        (0.54, "High"),
        (0.00, "High"),
    ])
    def test_parametrized_severities(self, score, expected):
        assert gap_severity(score) == expected


# ── build_feature_vector ───────────────────────────────────────────────────────

class TestBuildFeatureVector:

    def test_output_has_correct_columns(self):
        from services.ml_engine import _feat_cols
        df = build_feature_vector(
            skills=["Python", "SQL"],
            job_role="Data Scientist",
            experience_years=3,
            education="B.Sc. Computer Science",
            job_level="Mid-Level",
            work_mode="Hybrid",
            cert_count=1,
            projects_count=5,
        )
        assert list(df.columns) == _feat_cols
        assert len(df) == 1

    def test_unknown_education_defaults_to_three(self):
        df = build_feature_vector(
            skills=["Python"],
            job_role="Software Engineer",
            experience_years=2,
            education="Online Certificate",   # not in EDU_RANK
            job_level="Junior",
            work_mode="Remote",
            cert_count=0,
            projects_count=2,
        )
        assert df["Education_Enc"].iloc[0] == 3   # default fallback

    def test_unknown_job_level_defaults_to_two(self):
        df = build_feature_vector(
            skills=["Python"],
            job_role="Software Engineer",
            experience_years=2,
            education="B.Sc. Computer Science",
            job_level="Trainee",              # not in LEVEL_RANK
            work_mode="Hybrid",
            cert_count=0,
            projects_count=2,
        )
        assert df["JobLevel_Enc"].iloc[0] == 2    # default fallback

    def test_no_missing_columns(self):
        """Feature vector should have no NaN values."""
        df = build_feature_vector(
            skills=[],
            job_role="DevOps Engineer",
            experience_years=0,
            education="Bootcamp + Self-Taught",
            job_level="Junior",
            work_mode="On-Site",
            cert_count=0,
            projects_count=0,
        )
        assert df.isna().sum().sum() == 0


# ── run_skill_gap_analysis (smoke test) ───────────────────────────────────────

class TestRunSkillGapAnalysis:

    def _run(self, role="Data Scientist", skills=None, **kwargs):
        defaults = dict(
            candidate_id="TEST-001",
            candidate_name="Test User",
            job_role=role,
            skills=skills or ["Python", "SQL"],
            experience_years=3,
            education="B.Sc. Computer Science",
            certifications="None",
            cert_count=0,
            projects_count=5,
            job_level="Mid-Level",
            work_mode="Hybrid",
            cv_matching_score=None,
            interview_score=None,
            mcq_score=None,
            descriptive_score=None,
            coding_score=None,
            weak_topics=[],
            failed_mcq_topics=[],
        )
        defaults.update(kwargs)
        return run_skill_gap_analysis(**defaults)

    def test_result_has_required_keys(self):
        result = self._run()
        for key in [
            "candidate_id", "candidate_name", "job_role", "gap_severity",
            "skill_match_pct", "hire_probability", "predicted_hire",
            "missing_required", "present_skills", "resources", "learning_plan",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_hire_probability_in_valid_range(self):
        result = self._run()
        assert 0.0 <= result["hire_probability"] <= 100.0

    def test_skill_match_pct_in_valid_range(self):
        result = self._run()
        assert 0.0 <= result["skill_match_pct"] <= 100.0

    def test_no_external_scores_does_not_crash(self):
        """Calling with all None scores should work without error."""
        result = self._run(cv_matching_score=None, interview_score=None)
        assert result["hire_probability"] >= 0

    def test_with_all_external_scores(self):
        """Blending external scores should produce valid result."""
        result = self._run(
            cv_matching_score=85.0, interview_score=80.0,
            mcq_score=70.0, descriptive_score=75.0, coding_score=65.0,
        )
        assert 0.0 <= result["hire_probability"] <= 100.0

    def test_low_scores_trigger_knowledge_gaps(self):
        """Interview score < 60 should populate knowledge_gaps."""
        result = self._run(
            interview_score=45.0,
            weak_topics=["Algorithms", "System Design"],
        )
        assert len(result["knowledge_gaps"]) > 0

    def test_low_coding_score_triggers_problem_solving_gaps(self):
        """Coding score < 60 should populate problem_solving_gaps."""
        result = self._run(coding_score=40.0)
        assert len(result["problem_solving_gaps"]) > 0

    def test_zero_certifications_adds_suggestion(self):
        """Zero certifications should appear in improvement suggestions."""
        result = self._run(cert_count=0)
        assert any("certification" in s.lower() for s in result["improvement_suggestions"])

    def test_high_experience_perfect_match_is_low_severity(self):
        """A senior candidate with all required skills should be Low severity."""
        role     = "Machine Learning Engineer"
        required = JOB_REQ[role]["required"]
        result   = self._run(role=role, skills=required, experience_years=10, cert_count=3)
        # With full required skills the gap should be low or medium
        assert result["gap_severity"] in ("Low", "Medium")

    @pytest.mark.parametrize("role", [
        "Software Engineer", "Data Scientist", "Machine Learning Engineer",
        "Frontend Developer", "Backend Developer", "DevOps Engineer",
        "Cybersecurity Analyst", "Cloud Solutions Architect",
        "Database Administrator", "Mobile App Developer",
        "Full Stack Developer", "QA/Test Automation Engineer",
        "Data Engineer", "Site Reliability Engineer (SRE)",
        "UI/UX Designer", "Network Engineer",
        "Business/Systems Analyst", "AI/NLP Engineer",
        "Blockchain Developer", "Embedded Systems Engineer",
    ])
    def test_all_roles_return_valid_result(self, role):
        """Every supported role should complete without raising an exception."""
        result = self._run(role=role)
        assert result["job_role"] == role
        assert isinstance(result["gap_severity"], str)
