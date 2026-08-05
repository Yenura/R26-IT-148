"""Role classifier — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

PROPOSED MODEL: SBERT (all-MiniLM-L6-v2) → sklearn LogisticRegression
BASELINE MODEL: TF-IDF → sklearn LogisticRegression

Auto-falls back to the TF-IDF baseline if:
  - sentence-transformers is not installed, OR
  - the SBERT artifact is not found in MODEL_DIR.

Usage
-----
# At app startup (once):
    predictor = Predictor(model_dir=MODEL_DIR)

# Per request:
    result = predictor.predict(resume_text)
    result.job_role, result.confidence, result.alternatives
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import joblib
import numpy as np

logger = logging.getLogger("component1.predictor")


@dataclass
class PredictionResult:
    job_role:       str
    confidence:     float
    alternatives:   List[dict]   = field(default_factory=list)  # [{"role": ..., "confidence": ...}]
    model_used:     str          = "unknown"


class Predictor:
    """Wraps the trained role classifier.

    Parameters
    ----------
    model_dir : path to the directory containing saved model artifacts.
    """

    SBERT_CLASSIFIER_FILE  = "sbert_classifier.joblib"
    TFIDF_CLASSIFIER_FILE  = "tfidf_classifier.joblib"
    TFIDF_VECTORIZER_FILE  = "tfidf_vectorizer.joblib"
    LABEL_CLASSES_FILE     = "label_classes.joblib"
    SBERT_MODEL_NAME       = "all-MiniLM-L6-v2"

    def __init__(self, model_dir: str | Path = "models"):
        self.model_dir = Path(model_dir)
        self._clf     = None
        self._vectorizer = None   # TF-IDF only
        self._classes:  List[str] = []
        self._sbert_model = None
        self._mode   = "none"     # "sbert" | "tfidf" | "none"
        self._load()

    # ── Loading ────────────────────────────────────────────────────────────────

    def _load(self):
        """Load the best available model."""
        label_path = self.model_dir / self.LABEL_CLASSES_FILE
        if label_path.exists():
            self._classes = joblib.load(label_path)

        # 1. Try SBERT
        sbert_path = self.model_dir / self.SBERT_CLASSIFIER_FILE
        if sbert_path.exists():
            try:
                from sentence_transformers import SentenceTransformer
                self._sbert_model = SentenceTransformer(self.SBERT_MODEL_NAME)
                self._clf         = joblib.load(sbert_path)
                self._mode        = "sbert"
                logger.info("Predictor: loaded SBERT classifier from %s", sbert_path)
                return
            except ImportError:
                logger.warning("sentence-transformers not installed; falling back to TF-IDF")
            except Exception as exc:
                logger.warning("SBERT load failed (%s); falling back to TF-IDF", exc)

        # 2. Try TF-IDF baseline
        tfidf_clf_path = self.model_dir / self.TFIDF_CLASSIFIER_FILE
        tfidf_vec_path = self.model_dir / self.TFIDF_VECTORIZER_FILE
        if tfidf_clf_path.exists() and tfidf_vec_path.exists():
            try:
                self._clf        = joblib.load(tfidf_clf_path)
                self._vectorizer = joblib.load(tfidf_vec_path)
                self._mode       = "tfidf"
                logger.info("Predictor: loaded TF-IDF classifier from %s", tfidf_clf_path)
                return
            except Exception as exc:
                logger.warning("TF-IDF load failed: %s", exc)

        logger.warning("Predictor: no trained model found in %s. Predictions will be random.", self.model_dir)
        self._mode = "none"

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict(self, text: str) -> PredictionResult:
        """Predict the job role for the given resume text.

        Returns a PredictionResult with the top role, its confidence, and the
        next two alternatives (top-3 total).
        """
        if self._mode == "none" or not self._classes:
            return self._fallback_prediction()

        proba = self._get_proba(text)
        top3_idx = np.argsort(proba)[::-1][:3]
        top_role  = self._classes[top3_idx[0]]
        top_conf  = float(proba[top3_idx[0]])
        alternatives = [
            {"role": self._classes[i], "confidence": float(proba[i])}
            for i in top3_idx[1:]
        ]
        return PredictionResult(
            job_role=top_role,
            confidence=top_conf,
            alternatives=alternatives,
            model_used=self._mode,
        )

    def _get_proba(self, text: str) -> np.ndarray:
        if self._mode == "sbert":
            embedding = self._sbert_model.encode([text])
            return self._clf.predict_proba(embedding)[0]
        else:  # tfidf
            X = self._vectorizer.transform([text])
            return self._clf.predict_proba(X)[0]

    def _fallback_prediction(self) -> PredictionResult:
        """Return a uniform-random prediction when no model is available."""
        import random
        from data.role_requirements import ALL_ROLES
        role = random.choice(ALL_ROLES)
        return PredictionResult(
            job_role=role,
            confidence=1.0 / len(ALL_ROLES),
            alternatives=[],
            model_used="none",
        )

    @property
    def is_ready(self) -> bool:
        return self._mode in ("sbert", "tfidf")

    @property
    def mode(self) -> str:
        return self._mode
