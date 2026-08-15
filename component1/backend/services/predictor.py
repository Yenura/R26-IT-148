"""
Role Classifier Service — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Loads the feature-based LogisticRegression classifier (cv_classifier.pkl)
and returns top IT job role predictions with confidence probabilities and explainable scores.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np

from ml.feature_engineering import extract_cv_features

logger = logging.getLogger("component1.predictor")


@dataclass
class PredictionResult:
    job_role: str
    confidence: float
    alternatives: List[Dict[str, float]] = field(default_factory=list)  # [{"role": ..., "probability": ...}]
    feature_scores: Dict[str, float] = field(default_factory=dict)     # {"S_edu": ..., "S_exp": ..., "S_skill": ...}
    extracted_info: Dict[str, Any] = field(default_factory=dict)
    model_used: str = "cv_classifier_feature_lr"


class Predictor:
    """Wraps the feature-based LogisticRegression role classifier."""

    FEATURE_MODEL_FILE = "cv_classifier.pkl"
    LABEL_ENCODER_FILE = "label_encoder.pkl"
    TFIDF_MODEL_FILE = "tfidf_baseline.pkl"
    TFIDF_VEC_FILE = "tfidf_vectorizer.pkl"

    def __init__(self, model_dir: str | Path = "models"):
        self.model_dir = Path(model_dir)
        self._clf = None
        self._label_encoder = None
        self._classes: List[str] = []
        self._mode = "none"
        self._load()

    @property
    def mode(self) -> str:
        return self._mode

    def _load(self):
        """Load the feature-based LogisticRegression model or fallback."""
        cv_model_path = self.model_dir / self.FEATURE_MODEL_FILE
        encoder_path = self.model_dir / self.LABEL_ENCODER_FILE

        if cv_model_path.exists() and encoder_path.exists():
            try:
                self._clf = joblib.load(cv_model_path)
                self._label_encoder = joblib.load(encoder_path)
                self._classes = list(self._label_encoder.classes_)
                self._mode = "feature_lr"
                logger.info("Predictor: loaded feature-based LogisticRegression from %s", cv_model_path)
                return
            except Exception as exc:
                logger.warning("Feature LR load failed (%s); trying fallback", exc)

        # Fallback to TF-IDF if present
        tfidf_path = self.model_dir / self.TFIDF_MODEL_FILE
        if tfidf_path.exists() and encoder_path.exists():
            try:
                self._clf = joblib.load(tfidf_path)
                self._label_encoder = joblib.load(encoder_path)
                self._classes = list(self._label_encoder.classes_)
                self._mode = "tfidf_lr"
                logger.info("Predictor: loaded TF-IDF baseline from %s", tfidf_path)
                return
            except Exception as exc:
                logger.warning("TF-IDF baseline load failed: %s", exc)

        self._mode = "lightweight_regex"
        logger.info("Predictor operating in lightweight_regex mode")

    def predict(self, resume_text: str, target_role: Optional[str] = None) -> PredictionResult:
        """Runs prediction on CV text and returns role predictions + features."""
        # 1. Feature extraction
        feat_dict = extract_cv_features(resume_text, target_role=target_role or "Software Engineer")
        feat_vec = feat_dict["feature_vector"]

        extracted_info = {
            "experience_years": feat_dict["experience_years"],
            "education": feat_dict["education_info"].get("majors", []),
            "education_level": feat_dict["education_info"].get("level_name", "None"),
            "detected_skills": feat_dict["detected_skills"],
            "detected_certs": feat_dict["detected_certs"]
        }

        feature_scores = {
            "S_edu": feat_dict["s_edu"],
            "S_exp": feat_dict["s_exp"],
            "S_skill": feat_dict["s_skill"]
        }

        if self._clf is not None and self._label_encoder is not None and len(self._classes) > 0:
            probs = self._clf.predict_proba(feat_vec.reshape(1, -1))[0]
            top_indices = np.argsort(probs)[::-1]

            best_idx = top_indices[0]
            predicted_role = str(self._classes[best_idx])
            confidence = float(probs[best_idx])

            alternatives = [
                {"role": str(self._classes[idx]), "probability": round(float(probs[idx]), 4)}
                for idx in top_indices[:5]
            ]

            return PredictionResult(
                job_role=predicted_role,
                confidence=round(confidence, 4),
                alternatives=alternatives,
                feature_scores=feature_scores,
                extracted_info=extracted_info,
                model_used=self._mode
            )

        # Fallback if no model file loaded: use max skill overlap role
        overlaps = feat_dict["role_overlaps"]
        sorted_roles = sorted(overlaps.items(), key=lambda x: x[1], reverse=True)
        best_role, best_score = sorted_roles[0]

        alternatives = [{"role": r, "probability": round(s, 4)} for r, s in sorted_roles[:5]]

        return PredictionResult(
            job_role=best_role,
            confidence=round(best_score if best_score > 0 else 0.50, 4),
            alternatives=alternatives,
            feature_scores=feature_scores,
            extracted_info=extracted_info,
            model_used="heuristic_regex"
        )
