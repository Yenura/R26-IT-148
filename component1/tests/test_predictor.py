"""Unit tests — predictor
IT22094872 | Dulnith K.D. | R26-IT-148
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import MagicMock, patch
import numpy as np

from backend.services.predictor import Predictor, PredictionResult
from data.role_requirements import ALL_ROLES


ROLE_SET = set(ALL_ROLES)


class TestPredictorFallback:
    """Test predictor with TF-IDF fallback (no SBERT required)."""

    def test_predictor_returns_valid_role_no_model(self, tmp_path):
        """With no model artifacts, predictor falls back to random but valid role."""
        pred = Predictor(model_dir=tmp_path)
        result = pred.predict("Python developer with 5 years experience in REST APIs")
        assert result.job_role in ROLE_SET

    def test_confidence_in_range_no_model(self, tmp_path):
        pred = Predictor(model_dir=tmp_path)
        result = pred.predict("Backend developer with SQL experience")
        assert 0.0 <= result.confidence <= 1.0

    def test_alternatives_list(self, tmp_path):
        pred = Predictor(model_dir=tmp_path)
        result = pred.predict("Data scientist with Python and statistics background")
        assert isinstance(result.alternatives, list)

    def test_prediction_result_fields(self, tmp_path):
        pred = Predictor(model_dir=tmp_path)
        result = pred.predict("Software engineer with Java experience")
        assert hasattr(result, "job_role")
        assert hasattr(result, "confidence")
        assert hasattr(result, "alternatives")
        assert hasattr(result, "model_used")


class TestPredictorWithTFIDF:
    """Test predictor with a real TF-IDF model (trained if available)."""

    @pytest.fixture(scope="class")
    def trained_predictor(self):
        models_dir = Path(__file__).parent.parent / "models"
        if not (models_dir / "tfidf_classifier.joblib").exists():
            pytest.skip("TF-IDF model not trained yet. Run 'python ml/train.py' first.")
        return Predictor(model_dir=models_dir)

    def test_returns_valid_role(self, trained_predictor, swe_resume_text):
        result = trained_predictor.predict(swe_resume_text)
        assert result.job_role in ROLE_SET

    def test_confidence_in_range(self, trained_predictor, swe_resume_text):
        result = trained_predictor.predict(swe_resume_text)
        assert 0.0 <= result.confidence <= 1.0

    def test_alternatives_count(self, trained_predictor, swe_resume_text):
        result = trained_predictor.predict(swe_resume_text)
        assert len(result.alternatives) <= 2

    def test_alternatives_roles_valid(self, trained_predictor, swe_resume_text):
        result = trained_predictor.predict(swe_resume_text)
        for alt in result.alternatives:
            assert alt["role"] in ROLE_SET
            assert 0.0 <= alt["confidence"] <= 1.0

    def test_all_proba_sum_approx_one(self, trained_predictor, swe_resume_text):
        """Confidence + alternatives should approximately sum to <= 1."""
        result = trained_predictor.predict(swe_resume_text)
        total = result.confidence + sum(a["confidence"] for a in result.alternatives)
        assert total <= 1.05  # slight tolerance for float arithmetic


class TestPredictorWithSBERT:
    """Test predictor with SBERT model (skip if not installed/trained)."""

    @pytest.mark.requires_sbert
    def test_sbert_predictor_valid_role(self, swe_resume_text):
        models_dir = Path(__file__).parent.parent / "models"
        if not (models_dir / "sbert_classifier.joblib").exists():
            pytest.skip("SBERT model not trained. Run 'python ml/train.py'.")
        pred = Predictor(model_dir=models_dir)
        if pred.mode != "sbert":
            pytest.skip("SBERT model loaded but mode is not sbert")
        result = pred.predict(swe_resume_text)
        assert result.job_role in ROLE_SET
