"""Unit tests — predictor
IT22089236 | D T D Perera | R26-IT-148
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
    """Test predictor fallback when no models are present."""

    def test_predictor_returns_valid_role_no_model(self, tmp_path):
        """With no model artifacts, predictor falls back to valid role."""
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
        assert hasattr(result, "manual_review_recommended")


class TestPredictorWithTrainedModel:
    """Test predictor with the trained primary feature-based classifier."""

    @pytest.fixture(scope="class")
    def trained_predictor(self):
        models_dir = Path(__file__).parent.parent / "models"
        if not (models_dir / "cv_classifier.pkl").exists():
            pytest.skip("Model not trained yet. Run 'python ml/train.py' first.")
        return Predictor(model_dir=models_dir)

    def test_returns_valid_role(self, trained_predictor, swe_resume_text):
        result = trained_predictor.predict(swe_resume_text)
        assert result.job_role in ROLE_SET

    def test_confidence_in_range(self, trained_predictor, swe_resume_text):
        result = trained_predictor.predict(swe_resume_text)
        assert 0.0 <= result.confidence <= 1.0

    def test_alternatives_count(self, trained_predictor, swe_resume_text):
        result = trained_predictor.predict(swe_resume_text)
        assert 1 <= len(result.alternatives) <= 5

    def test_alternatives_roles_valid(self, trained_predictor, swe_resume_text):
        result = trained_predictor.predict(swe_resume_text)
        for alt in result.alternatives:
            assert alt["role"] in ROLE_SET

    def test_all_proba_sum_approx_one(self, trained_predictor, swe_resume_text):
        result = trained_predictor.predict(swe_resume_text)
        total_p = sum(a.get("probability", a.get("confidence", 0.0)) for a in result.alternatives)
        assert 0.0 < total_p <= 1.05

    def test_scores_present_in_result(self, trained_predictor, swe_resume_text):
        result = trained_predictor.predict(swe_resume_text)
        assert "S_skill" in result.feature_scores
        assert "S_exp" in result.feature_scores
        assert "S_edu" in result.feature_scores
