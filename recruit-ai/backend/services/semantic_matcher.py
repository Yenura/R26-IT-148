"""TF-IDF based semantic similarity for resume-job matching."""
import hashlib
from functools import lru_cache
from typing import Optional

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None


@lru_cache(maxsize=1024)
def _cached_tfidf_sim(hash_a: str, hash_b: str, text_a: str, text_b: str) -> float:
    if TfidfVectorizer is None or cosine_similarity is None:
        return 0.0
    try:
        vec = TfidfVectorizer(max_features=5000)
        tfidf = vec.fit_transform([text_a, text_b])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return float(max(0.0, min(sim * 100, 100.0)))
    except Exception:
        return 0.0


class SemanticMatcher:
    def __init__(self):
        pass

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        if not text_a or not text_b:
            return 0.0
        text_a_str = text_a.strip()
        text_b_str = text_b.strip()
        if not text_a_str or not text_b_str:
            return 0.0

        # Fast hash keys for LRU cache lookup
        ha = hashlib.md5(text_a_str.encode("utf-8", errors="ignore")).hexdigest()
        hb = hashlib.md5(text_b_str.encode("utf-8", errors="ignore")).hexdigest()
        return _cached_tfidf_sim(ha, hb, text_a_str, text_b_str)
