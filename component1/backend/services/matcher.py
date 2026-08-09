"""JD-Resume semantic matcher — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

PROPOSED: Sentence-BERT cosine similarity (resume embedding ↔ JD embedding).
FALLBACK : TF-IDF cosine similarity when sentence-transformers is unavailable.

This is the Semantic Matching Engine piece shown in the architecture diagram:
  Candidate CV text ──▶ SBERT embedding ──┐
                                           ├─▶ cosine similarity ──▶ jd_similarity_score
  Job Description   ──▶ SBERT embedding ──┘

The jd_similarity_score (0–1) is a first-class output fed into cv_matching_score
and exposed to Component 3's ranking engine.
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("component1.matcher")


class JDMatcher:
    """Computes semantic similarity between resume text and a job description.

    Parameters
    ----------
    sbert_model_name : The sentence-transformers model to use (PROPOSED path).
    tfidf_vectorizer : A pre-fitted TfidfVectorizer instance (FALLBACK path).
                       If None and sentence-transformers is unavailable, a fresh
                       vectorizer is fitted on-the-fly (less accurate).
    """

    SBERT_MODEL_NAME = "all-MiniLM-L6-v2"

    def __init__(
        self,
        sbert_model=None,            # pre-loaded SentenceTransformer (from predictor)
        tfidf_vectorizer=None,        # pre-fitted TfidfVectorizer (from predictor)
    ):
        self._sbert   = sbert_model
        self._tfidf   = tfidf_vectorizer
        self._mode    = "none"

        if sbert_model is not None:
            self._mode = "sbert"
            logger.info("JDMatcher: using SBERT (%s)", self.SBERT_MODEL_NAME)
        elif tfidf_vectorizer is not None:
            self._mode = "tfidf"
            logger.info("JDMatcher: using TF-IDF cosine fallback")
        else:
            logger.warning("JDMatcher: no model available, will try lazy SBERT load")

    def compute(self, resume_text: str, jd_text: str) -> float:
        """Return cosine similarity in [0, 1] between resume and JD.

        Falls back gracefully:
        1. SBERT (if sentence-transformers installed + model loaded)
        2. TF-IDF with pre-fitted vectorizer
        3. TF-IDF fitted on the fly from the two documents
        """
        if not resume_text or not jd_text:
            return 0.0

        if self._mode == "sbert" and self._sbert is not None:
            return self._sbert_similarity(resume_text, jd_text)

        if self._mode == "tfidf" and self._tfidf is not None:
            return self._tfidf_similarity(resume_text, jd_text)

        # Lazy SBERT attempt
        try:
            from sentence_transformers import SentenceTransformer
            if self._sbert is None:
                self._sbert = SentenceTransformer(self.SBERT_MODEL_NAME)
                self._mode  = "sbert"
            return self._sbert_similarity(resume_text, jd_text)
        except ImportError:
            pass
        except Exception as exc:
            logger.warning("Lazy SBERT failed: %s", exc)

        # On-the-fly TF-IDF
        return self._adhoc_tfidf_similarity(resume_text, jd_text)

    # ── Similarity implementations ─────────────────────────────────────────────

    def _sbert_similarity(self, text_a: str, text_b: str) -> float:
        embeddings = self._sbert.encode([text_a, text_b])
        sim = cosine_similarity(embeddings[0:1], embeddings[1:2])[0][0]
        return float(np.clip(sim, 0.0, 1.0))

    def _tfidf_similarity(self, text_a: str, text_b: str) -> float:
        vecs = self._tfidf.transform([text_a, text_b])
        sim  = cosine_similarity(vecs[0:1], vecs[1:2])[0][0]
        return float(np.clip(sim, 0.0, 1.0))

    def _adhoc_tfidf_similarity(self, text_a: str, text_b: str) -> float:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        try:
            vecs = vec.fit_transform([text_a, text_b])
            sim  = cosine_similarity(vecs[0:1], vecs[1:2])[0][0]
            return float(np.clip(sim, 0.0, 1.0))
        except Exception as exc:
            logger.warning("Ad-hoc TF-IDF similarity failed: %s", exc)
            return 0.0

    @property
    def mode(self) -> str:
        return self._mode
