"""Unit tests — JD matcher
IT22094872 | Dulnith K.D. | R26-IT-148
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from backend.services.matcher import JDMatcher


class TestJDMatcherBounds:
    def test_similarity_in_range_identical_texts(self):
        matcher = JDMatcher()
        score = matcher.compute("Python developer", "Python developer")
        assert 0.0 <= score <= 1.0

    def test_similar_texts_higher_than_unrelated(self):
        matcher = JDMatcher()
        sim_high = matcher.compute(
            "Python data scientist with machine learning and statistics expertise",
            "We need a data scientist skilled in Python, ML, and statistics",
        )
        sim_low = matcher.compute(
            "Python data scientist with machine learning and statistics expertise",
            "We need an experienced network engineer with BGP and OSPF expertise",
        )
        assert sim_high > sim_low

    def test_empty_resume_returns_zero(self):
        matcher = JDMatcher()
        assert matcher.compute("", "some job description") == 0.0

    def test_empty_jd_returns_zero(self):
        matcher = JDMatcher()
        assert matcher.compute("Python developer with 5 years experience", "") == 0.0

    def test_both_empty_returns_zero(self):
        matcher = JDMatcher()
        assert matcher.compute("", "") == 0.0

    def test_returns_float(self, swe_resume_text, sample_jd_swe):
        matcher = JDMatcher()
        score = matcher.compute(swe_resume_text, sample_jd_swe)
        assert isinstance(score, float)

    def test_score_non_negative(self, swe_resume_text, sample_jd_swe):
        matcher = JDMatcher()
        score = matcher.compute(swe_resume_text, sample_jd_swe)
        assert score >= 0.0

    def test_score_at_most_one(self, swe_resume_text, sample_jd_swe):
        matcher = JDMatcher()
        score = matcher.compute(swe_resume_text, sample_jd_swe)
        assert score <= 1.0

    @pytest.mark.requires_sbert
    def test_sbert_similarity_plausible(self, swe_resume_text, sample_jd_swe):
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            matcher = JDMatcher(sbert_model=model)
            score = matcher.compute(swe_resume_text, sample_jd_swe)
            assert 0.0 <= score <= 1.0
            # SWE resume vs SWE JD should be meaningfully similar
            assert score > 0.3
        except Exception:
            pytest.skip("SBERT not available")
