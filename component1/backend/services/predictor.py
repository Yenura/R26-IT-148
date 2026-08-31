"""
Role Classifier Service — Component 1
IT22089236 | D T D Perera | R26-IT-148

Loads the feature-based LogisticRegression classifier (cv_classifier.pkl)
and returns top IT job role predictions with calibrated confidence probabilities,
explainable scores, and low-confidence review recommendation flags.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np

from ml.feature_engineering import extract_cv_features

logger = logging.getLogger("component1.predictor")

# Low confidence threshold configuration
LOW_CONFIDENCE_THRESHOLD = 0.35
AMBIGUITY_MARGIN_THRESHOLD = 0.08


@dataclass
class PredictionResult:
    job_role: str
    confidence: float
    alternatives: List[Dict[str, Any]] = field(default_factory=list)  # [{"role": ..., "probability": ...}]
    feature_scores: Dict[str, float] = field(default_factory=dict)     # {"S_edu": ..., "S_exp": ..., "S_skill": ...}
    extracted_info: Dict[str, Any] = field(default_factory=dict)
    manual_review_recommended: bool = False
    review_reason: Optional[str] = None
    model_used: str = "cv_classifier_feature_lr"


class Predictor:
    """Wraps the feature-based LogisticRegression role classifier."""

    FEATURE_MODEL_FILE = "cv_classifier.pkl"
    LABEL_ENCODER_FILE = "label_encoder.pkl"
    TFIDF_MODEL_FILE = "tfidf_baseline.pkl"
    TFIDF_VEC_FILE = "tfidf_vectorizer.pkl"
    METADATA_FILE = "model_metadata.json"

    def __init__(self, model_dir: str | Path = "models"):
        self.model_dir = Path(model_dir)
        self._clf = None
        self._label_encoder = None
        self._classes: List[str] = []
        self._mode = "none"
        self._metadata: Dict[str, Any] = {}
        self._load()

    @property
    def mode(self) -> str:
        return self._mode

    def _load(self):
        """Load the feature-based LogisticRegression model and metadata."""
        # Find valid model directory across candidate paths
        candidate_dirs = [
            self.model_dir,
            Path(__file__).parent.parent / "models",
            Path(__file__).parent.parent.parent / "component1" / "models",
            Path.cwd() / "models",
            Path.cwd() / "component1" / "models",
        ]
        resolved_dir = self.model_dir
        for d in candidate_dirs:
            if d.exists() and (d / self.FEATURE_MODEL_FILE).exists():
                resolved_dir = d
                break
        self.model_dir = resolved_dir

        cv_model_path = self.model_dir / self.FEATURE_MODEL_FILE
        tfidf_path = self.model_dir / self.TFIDF_MODEL_FILE
        encoder_path = self.model_dir / self.LABEL_ENCODER_FILE
        meta_path = self.model_dir / self.METADATA_FILE

        if meta_path.exists():
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    self._metadata = json.load(f)
            except Exception as e:
                logger.warning("Could not read model metadata: %s", e)

        # Load pre-fitted TF-IDF vectorizer if available for matcher sharing
        vec_path = self.model_dir / self.TFIDF_VEC_FILE
        if vec_path.exists():
            try:
                self._vectorizer = joblib.load(vec_path)
            except Exception as e:
                self._vectorizer = None
        else:
            self._vectorizer = None

        self._tfidf_clf = None
        if tfidf_path.exists():
            try:
                self._tfidf_clf = joblib.load(tfidf_path)
            except Exception as e:
                self._tfidf_clf = None

        if cv_model_path.exists() and encoder_path.exists():
            try:
                self._clf = joblib.load(cv_model_path)
                self._label_encoder = joblib.load(encoder_path)
                self._classes = list(self._label_encoder.classes_)
                if self._tfidf_clf is not None and self._vectorizer is not None:
                    self._mode = "hybrid_ensemble"
                    logger.info("Predictor: loaded Hybrid Ensemble (Feature LR + TF-IDF) from %s", self.model_dir)
                else:
                    self._mode = "feature_lr"
                    logger.info("Predictor: loaded feature-based LogisticRegression from %s", cv_model_path)
                return
            except Exception as exc:
                logger.warning("Feature LR load failed (%s); trying fallback", exc)

        # Fallback to TF-IDF if present
        if self._tfidf_clf is not None and encoder_path.exists() and self._vectorizer is not None:
            try:
                self._clf = self._tfidf_clf
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
        """Runs prediction on CV text and returns top 3 roles + probabilities + features."""
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
            "S_edu": feat_dict["s_edu"] * 100.0 if feat_dict["s_edu"] <= 1.0 else feat_dict["s_edu"],
            "S_exp": feat_dict["s_exp"] * 100.0 if feat_dict["s_exp"] <= 1.0 else feat_dict["s_exp"],
            "S_skill": feat_dict["s_skill"] * 100.0 if feat_dict["s_skill"] <= 1.0 else feat_dict["s_skill"]
        }

        # Domain relevance check: If candidate has no detected IT skills and 0% overlap across all roles
        max_overlap = max(feat_dict.get("role_overlaps", {}).values()) if feat_dict.get("role_overlaps") else 0.0
        has_it_education = any(m != "None" and m != "General IT" for m in extracted_info.get("education", []))
        
        if len(extracted_info.get("detected_skills", [])) == 0 and max_overlap < 0.05 and not has_it_education:
            return PredictionResult(
                job_role="Unmatched / Non-IT",
                confidence=0.0,
                alternatives=[],
                feature_scores=feature_scores,
                extracted_info=extracted_info,
                model_used="domain_gatekeeper"
            )

        if self._clf is not None and self._label_encoder is not None and len(self._classes) > 0:
            if self._mode == "hybrid_ensemble" and self._tfidf_clf is not None and self._vectorizer is not None:
                probs_feat = self._clf.predict_proba(feat_vec.reshape(1, -1))[0]
                probs_tfidf = self._tfidf_clf.predict_proba(self._vectorizer.transform([resume_text]))[0]
                # High-discrimination ensemble blend
                probs = 0.50 * probs_tfidf + 0.50 * probs_feat
            elif self._mode == "tfidf_lr" and self._vectorizer is not None:
                probs = self._clf.predict_proba(self._vectorizer.transform([resume_text]))[0]
            else:
                probs = self._clf.predict_proba(feat_vec.reshape(1, -1))[0]

            top_indices = np.argsort(probs)[::-1]

            best_idx = top_indices[0]
            second_idx = top_indices[1] if len(top_indices) > 1 else best_idx

            predicted_role = str(self._classes[best_idx])
            confidence = float(probs[best_idx])
            second_conf = float(probs[second_idx])

            # Check low confidence / ambiguity
            manual_review = False
            review_reason = None
            if confidence < LOW_CONFIDENCE_THRESHOLD:
                manual_review = True
                review_reason = f"Primary predicted role has lower confidence ({confidence*100:.1f}%). Multi-domain skill profile detected."
            elif (confidence - second_conf) < AMBIGUITY_MARGIN_THRESHOLD:
                manual_review = True
                review_reason = f"Close competition between '{predicted_role}' ({confidence*100:.1f}%) and '{self._classes[second_idx]}' ({second_conf*100:.1f}%)."

            alternatives = [
                {
                    "role": str(self._classes[idx]),
                    "probability": round(float(probs[idx]), 4),
                    "confidence": round(float(probs[idx]), 4)
                }
                for idx in top_indices[:5]
            ]

            return PredictionResult(
                job_role=predicted_role,
                confidence=round(confidence, 4),
                alternatives=alternatives,
                feature_scores=feature_scores,
                extracted_info=extracted_info,
                manual_review_recommended=manual_review,
                review_reason=review_reason,
                model_used=self._mode
            )

        # Fallback if no model file loaded: use max skill overlap role
        overlaps = feat_dict["role_overlaps"]
        sorted_roles = sorted(overlaps.items(), key=lambda x: x[1], reverse=True)
        best_role, best_score = sorted_roles[0]

        alternatives = [
            {"role": r, "probability": round(s, 4), "confidence": round(s, 4)}
            for r, s in sorted_roles[:5]
        ]

        return PredictionResult(
            job_role=best_role if best_score > 0 else "Unmatched / Non-IT",
            confidence=round(best_score, 4),
            alternatives=alternatives,
            feature_scores=feature_scores,
            extracted_info=extracted_info,
            manual_review_recommended=(best_score < 0.30),
            review_reason="Model running in heuristic rule mode" if best_score < 0.30 else None,
            model_used="heuristic_regex"
        )
