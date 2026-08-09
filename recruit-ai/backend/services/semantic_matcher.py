"""TF-IDF based semantic similarity for resume-job matching."""


class SemanticMatcher:
    def __init__(self):
        pass

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        if not text_a.strip() or not text_b.strip():
            return 0.0
        return self._tfidf_similarity(text_a, text_b)

    @staticmethod
    def _tfidf_similarity(text_a: str, text_b: str) -> float:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        try:
            vec = TfidfVectorizer(max_features=5000)
            tfidf = vec.fit_transform([text_a, text_b])
            sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return max(0.0, min(sim * 100, 100.0))
        except Exception:
            return 0.0
