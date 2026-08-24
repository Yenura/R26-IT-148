"""20-role classification model for resume role prediction."""
import os
import re
import json

ROLES = [
    "Software Engineer", "Data Scientist", "Machine Learning Engineer",
    "DevOps Engineer", "Cybersecurity Analyst", "Cloud Solutions Architect",
    "Database Administrator", "Frontend Developer", "Backend Developer",
    "Mobile App Developer", "Full Stack Developer", "QA/Test Automation Engineer",
    "Data Engineer", "Site Reliability Engineer", "UI/UX Designer",
    "Network Engineer", "Business/Systems Analyst", "AI/NLP Engineer",
    "Blockchain Developer", "Embedded Systems Engineer",
]

ROLE_KEYWORDS = {
    "Software Engineer": ["python", "java", "c++", "algorithms", "data structures", "oop", "git", "rest api", "sql"],
    "Data Scientist": ["python", "r", "statistics", "machine learning", "pandas", "numpy", "data analysis", "jupyter"],
    "Machine Learning Engineer": ["tensorflow", "pytorch", "deep learning", "mlops", "scikit-learn", "neural network"],
    "DevOps Engineer": ["docker", "kubernetes", "ci/cd", "jenkins", "terraform", "linux", "ansible", "bash"],
    "Cybersecurity Analyst": ["security", "penetration testing", "siem", "firewall", "owasp", "incident response"],
    "Cloud Solutions Architect": ["aws", "azure", "gcp", "terraform", "kubernetes", "microservices", "cloud"],
    "Database Administrator": ["sql", "postgresql", "mysql", "mongodb", "backup", "replication", "query optimization"],
    "Frontend Developer": ["react", "angular", "vue", "html", "css", "javascript", "typescript", "responsive"],
    "Backend Developer": ["node.js", "django", "flask", "fastapi", "spring", "rest api", "microservices"],
    "Mobile App Developer": ["flutter", "react native", "ios", "android", "swift", "kotlin", "dart", "firebase"],
    "Full Stack Developer": ["react", "node.js", "django", "postgresql", "mongodb", "html", "css", "javascript"],
    "QA/Test Automation Engineer": ["selenium", "pytest", "jest", "testing", "automation", "ci/cd", "qa"],
    "Data Engineer": ["spark", "kafka", "airflow", "etl", "data pipeline", "hadoop", "sql", "bigquery"],
    "Site Reliability Engineer": ["kubernetes", "prometheus", "grafana", "incident", "monitoring", "sre"],
    "UI/UX Designer": ["figma", "sketch", "adobe xd", "wireframe", "prototype", "user research", "design"],
    "Network Engineer": ["cisco", "tcp/ip", "dns", "vpn", "firewall", "routing", "switching", "network"],
    "Business/Systems Analyst": ["requirements", "stakeholder", "jira", "agile", "use case", "uml", "sql"],
    "AI/NLP Engineer": ["nlp", "transformer", "bert", "gpt", "text processing", "language model", "spacy"],
    "Blockchain Developer": ["solidity", "web3", "ethereum", "smart contract", "blockchain", "crypto"],
    "Embedded Systems Engineer": ["embedded", "c", "c++", "iot", "arduino", "raspberry pi", "rtos", "firmware"],
}


class RoleClassifier:
    def __init__(self):
        self._model = None
        self._vectorizer = None
        self._load_model()

    def _load_model(self):
        model_dir = os.path.join(os.path.dirname(__file__), "..", "models")
        try:
            import joblib
            path = os.path.join(model_dir, "role_classifier.pkl")
            if os.path.exists(path):
                data = joblib.load(path)
                if isinstance(data, dict) and "pipeline" in data:
                    self._model = data["pipeline"]
        except Exception:
            pass

    def _keyword_predict(self, text: str, skills: list[str]) -> tuple[str, float]:
        text_lower = text.lower()
        skill_lower = [s.lower() for s in skills]
        scores = {}
        for role, keywords in ROLE_KEYWORDS.items():
            score = 0
            for kw in keywords:
                if kw in text_lower or kw in skill_lower:
                    score += 1
            scores[role] = score / len(keywords) if keywords else 0
        best_role = max(scores, key=scores.get)
        best_score = scores[best_role]
        if best_score == 0:
            return "Software Engineer", 0.1
        confidence = min(best_score * 2, 1.0)
        return best_role, confidence

    def predict(self, text: str, skills: list[str] = None) -> tuple[str, float]:
        skills = skills or []
        if self._model is not None:
            try:
                import numpy as np
                combined = text + " " + " ".join(skills)
                pred = self._model.predict([combined])[0]
                proba = self._model.predict_proba([combined])[0]
                confidence = float(np.max(proba))
                return pred, confidence
            except Exception:
                pass
        return self._keyword_predict(text, skills)


ALL_20_ROLES = ROLES
