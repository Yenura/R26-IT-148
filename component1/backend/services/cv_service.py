"""Component 1 — CV matching service loading trained artifacts."""

import os
import sys
import pickle
import logging

sys.path.insert(0, os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ml")))

from models.schemas import CVMatchResponse

logger = logging.getLogger("component1")

_HERE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "models"))

RELEVANCE_LABELS = {0: "Not Relevant", 1: "Partly Relevant",
                    2: "Relevant", 3: "Highly Relevant"}


class CVService:
    def __init__(self):
        with open(os.path.join(MODELS_DIR, "matcher.pkl"), "rb") as f:
            self.matcher = pickle.load(f)
        clf_path = os.path.join(MODELS_DIR, "cv_classifier.pkl")
        self.classifier = None
        if os.path.exists(clf_path):
            with open(clf_path, "rb") as f:
                self.classifier = pickle.load(f)
        logger.info("CV service loaded (%d jobs)", len(self.matcher.jobs))

    def jobs(self):
        return self.matcher.jobs

    def classify(self, S_edu, S_exp, S_skill):
        if self.classifier is None:
            return 2, RELEVANCE_LABELS[2]
        import numpy as np
        clf, scaler, feats = (self.classifier["clf"], self.classifier["scaler"],
                              self.classifier["features"])
        X = scaler.transform(np.array([[S_edu, S_exp, S_skill]]))
        cls = int(clf.predict(X)[0])
        return cls, RELEVANCE_LABELS.get(cls, "Relevant")

    def match(self, request, report_id=None):
        res = self.matcher.analyze_cv(
            role=request.job_role,
            cv_text=request.cv_text,
            skills=request.skills,
            years=request.experience_years,
            education_text=request.education_text,
        )
        cls, label = self.classify(res["S_edu"], res["S_exp"], res["S_skill"])
        return CVMatchResponse(
            report_id=report_id or "",
            candidate_id=request.candidate_id,
            job_role=request.job_role,
            cv_matching_score=res["cv_matching_score"],
            extracted_skills=res["extracted_skills"],
            missing_skills=res["missing_skills"],
            covered_skills=res["covered_skills"],
            experience_years=res["experience_years"],
            edu_level=res["edu_level"],
            edu_level_name=res["edu_level_name"],
            edu_relevance=res["edu_relevance"],
            coverage=res["coverage"],
            S_edu=res["S_edu"],
            S_exp=res["S_exp"],
            S_skill=res["S_skill"],
            predicted_relevance_class=cls,
            predicted_relevance_label=label,
        )


_service = None


def get_service():
    global _service
    if _service is None:
        _service = CVService()
    return _service
