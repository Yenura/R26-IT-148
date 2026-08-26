"""100% Accuracy Verification Tests for S_exp and S_edu
IT22094872 | Dulnith K.D. | R26-IT-148

Validates 100% accuracy across all diverse international candidate formats:
- S_edu: PhD, MSc, MS, MEng, MTech, BSc, BS, B.S., B.Eng, B.Tech, BIT, BCS, Bachelor's
- S_exp: Explicit statements, Month-Year spans, Present tenures, Multi-tenure jobs,
         Internship + Senior role shadowing resolution, and Seniority tolerance fit.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from backend.services.extractor import extract
from backend.services.scorer import score, calculate_education_score, calculate_experience_score
from ml.extractor import extract_experience_years, extract_education_level


class TestEducation100PercentAccuracy:
    """Verifies that all qualified IT/CS/SE graduates achieve 100% S_edu."""

    @pytest.mark.parametrize("degree_phrase", [
        "Ph.D. in Artificial Intelligence from MIT",
        "Doctorate in Computer Science",
        "M.Sc. in Data Science — University of Edinburgh",
        "MS in Software Engineering, Carnegie Mellon",
        "M.S. in Computer Science",
        "Master of Science in Information Technology",
        "Master's Degree in Computing",
        "B.Sc. in Software Engineering — SLIIT (2019)",
        "BSc (Hons) in Information Technology",
        "B.S. in Computer Science",
        "BS in Software Engineering",
        "Bachelor of Science in IT",
        "Bachelor's in Computer Science",
        "B.Eng. Software Engineering",
        "B.Tech in Computer Science & Engineering",
        "BIT from University of Colombo School of Computing",
        "BCS Professional Graduate Diploma in IT",
        "Degree in Software Engineering from University of Westminster",
    ])
    def test_all_degree_variations_achieve_100_percent_s_edu(self, degree_phrase):
        # 1. Extraction
        features = extract(degree_phrase)
        assert features.edu_level >= 2, f"Expected edu_level >= 2 for '{degree_phrase}', got {features.edu_level}"

        # 2. Scoring
        result = score(
            role="Software Engineer",
            edu_level=features.edu_level,
            experience_years=3.0,
            skills=["Python", "FastAPI"],
            candidate_education=features.education,
        )
        assert result.S_edu == 100.0, f"Expected S_edu = 100.0 for '{degree_phrase}', got {result.S_edu}"
        assert result.education_analysis.education_match in ("FULL_MATCH", "QUALIFIED (BSC)", "QUALIFIED (MSC)", "QUALIFIED (PHD)")


class TestExperience100PercentAccuracy:
    """Verifies that all qualified candidates achieve 100% S_exp across all tenure formats."""

    def test_explicit_total_experience_100_percent(self):
        cv = "Summary: Total Experience: 5.5 Years in full stack web development using Python and React."
        features = extract(cv)
        assert features.experience_years >= 5.0
        result = score(role="Software Engineer", edu_level=2, experience_years=features.experience_years, skills=["Python"])
        assert result.S_exp == 100.0

    def test_month_year_date_range_100_percent(self):
        cv = "Experience: Jan 2020 - Dec 2023 at Tech Solutions Inc as Software Engineer."
        features = extract(cv)
        assert features.experience_years >= 3.0
        result = score(role="Software Engineer", edu_level=2, experience_years=features.experience_years, skills=["Python"])
        assert result.S_exp == 100.0

    def test_present_tenure_100_percent(self):
        cv = "Senior Software Engineer (2021 - Present) leading microservices architecture."
        features = extract(cv)
        assert features.experience_years >= 4.0
        result = score(role="Software Engineer", edu_level=2, experience_years=features.experience_years, skills=["Python"])
        assert result.S_exp == 100.0

    def test_internship_does_not_shadow_senior_role(self):
        """Fixes critical bug where an earlier internship shadowed subsequent professional roles."""
        cv = """
        Employment History:
        Senior Software Engineer (2020 - Present) - Building distributed cloud services
        Software Engineering Intern (1 year) - Worked on legacy systems
        """
        features = extract(cv)
        # Should correctly extract senior career span (5-6 years), NOT just 1 year
        assert features.experience_years >= 5.0, f"Expected >= 5.0 years, got {features.experience_years}"
        result = score(role="Software Engineer", edu_level=2, experience_years=features.experience_years, skills=["Python"])
        assert result.S_exp == 100.0

    def test_numeric_date_interval_extraction(self):
        cv = "Professional Experience: 01/2020 - 05/2023 Software Developer at FinTech"
        years = extract_experience_years(cv)
        assert years >= 3.0
        s_exp, analysis = calculate_experience_score(candidate_years=years, required_years=3.0)
        assert s_exp == 100.0

    def test_multi_tenure_merged_date_ranges(self):
        cv = """
        Work Experience:
        - Lead Backend Developer at CloudCorp: 2021 to 2024
        - Junior Software Engineer at StartUpX: 2018 to 2021
        """
        years = extract_experience_years(cv)
        # Non-overlapping range: 2018 to 2024 -> 6 years total
        assert years >= 5.5
        s_exp, analysis = calculate_experience_score(candidate_years=years, required_years=3.0)
        assert s_exp == 100.0

    def test_seniority_benchmark_tolerance(self):
        """Candidates within 15% of required years (e.g. 2.7+ yrs for a 3.0 yr role) achieve 100% fit."""
        s_exp, analysis = calculate_experience_score(candidate_years=2.7, required_years=3.0)
        assert s_exp == 100.0
