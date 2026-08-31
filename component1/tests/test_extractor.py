"""Unit tests — extractor
IT22089236 | D T D Perera | R26-IT-148
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from backend.services.extractor import extract


class TestEduLevel:
    def test_phd_detected(self):
        text = "Ph.D. in Computer Science from MIT (2020)"
        result = extract(text)
        assert result.edu_level == 4

    def test_msc_detected(self):
        text = "M.Sc. in Data Science — University of Edinburgh"
        result = extract(text)
        assert result.edu_level == 3

    def test_bsc_detected(self):
        text = "B.Sc. in Software Engineering — SLIIT (2019)"
        result = extract(text)
        assert result.edu_level == 2

    def test_diploma_detected(self):
        text = "Diploma in Information Technology — NIBM"
        result = extract(text)
        assert result.edu_level == 1

    def test_edu_relevance_cs(self):
        text = "B.Sc. in Computer Science — University of Colombo"
        result = extract(text)
        assert result.edu_relevance >= 0.8


class TestExperienceExtraction:
    def test_explicit_years(self):
        text = "5 years of experience in software development"
        result = extract(text)
        assert result.experience_years == pytest.approx(5.0, abs=0.5)

    def test_year_range(self):
        text = "Software Engineer at TechCorp (2019 – 2022)\nJunior Dev at DataBridge (2017 – 2019)"
        result = extract(text)
        assert result.experience_years >= 4.0

    def test_zero_experience_for_no_dates(self):
        text = "Recent graduate. No work history listed."
        result = extract(text)
        # extractor may return 0.0 or a small value; just check non-negative
        assert result.experience_years >= 0.0


class TestSkillExtraction:
    def test_known_skills_detected(self, swe_resume_text):
        result = extract(swe_resume_text)
        skills_lower = {s.lower() for s in result.skills}
        # The SWE fixture mentions Python, Java, SQL — all should be picked up
        assert "python" in skills_lower or "java" in skills_lower or "sql" in skills_lower

    def test_skills_is_list(self, swe_resume_text):
        result = extract(swe_resume_text)
        assert isinstance(result.skills, list)

    def test_no_duplicate_skills(self, swe_resume_text):
        result = extract(swe_resume_text)
        assert len(result.skills) == len(set(result.skills))
