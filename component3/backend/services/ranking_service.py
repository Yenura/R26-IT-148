"""Component 3 — candidate ranking service (CSS engine + LambdaMART LTR)."""

import os
import sys
import json
import pickle
import logging

_C3_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, _C3_ROOT)

from engine.css_engine import (JobRequirementProfile, CandidateFeatures,
                               CSSEngine)  # noqa: E402
from ltr.lambdamart_model import FEATURE_COLS  # noqa: E402
from data.role_configs import ROLES, ROLE_DISPLAY_NAMES, REQUIRED_YEARS  # noqa: E402

logger = logging.getLogger("component3")

_HERE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(_C3_ROOT, "models")
TEST_CSV = os.path.join(_C3_ROOT, "datasets", "test_set.csv")

COMPONENT4_URL = os.getenv("COMPONENT4_URL", "http://127.0.0.1:8004")


class RankingService:
    def __init__(self):
        self.ltr = None
        pkl = os.path.join(MODELS_DIR, "lambdamart_model.pkl")
        if os.path.exists(pkl):
            try:
                with open(pkl, "rb") as f:
                    data = pickle.load(f)
                if isinstance(data, dict) and "model" in data:
                    self.ltr = data["model"]
                    self.ltr.scaler = data.get("scaler")
                else:
                    self.ltr = data
                logger.info("LambdaMART LTR model loaded")
            except Exception as exc:
                logger.warning("Failed to load LTR model: %s", exc)
        self._shap = None
        try:
            import shap
            self._shap = shap
        except ImportError:
            pass
        self._background = None

    def roles(self):
        return {r: ROLE_DISPLAY_NAMES.get(r, r) for r in ROLES}

    def _normalize_role(self, role_str: str) -> str:
        if not role_str:
            return "Software_Engineer"
        if role_str in ROLES:
            return role_str
        formatted = role_str.strip().replace(" ", "_")
        if formatted in ROLES:
            return formatted
        for r in ROLES:
            if (r.lower() == formatted.lower() or
                r.lower() == role_str.lower() or
                r.replace("_", "").lower() == role_str.replace(" ", "").replace("_", "").lower()):
                return r
        for r in ROLES:
            if r.lower() in role_str.lower() or role_str.lower() in r.lower():
                return r
        return role_str

    def _build_features(self, c, job):
        eng = CSSEngine(job)
        s_edu = round(max(0.0, min(1.0, float(c.S_edu))), 4) if c.S_edu is not None else eng.s_edu(c.edu_level, c.edu_relevance)
        s_exp = round(max(0.0, min(1.0, float(c.S_exp))), 4) if c.S_exp is not None else eng.s_exp(c.years_experience)
        s_skill = round(max(0.0, min(1.0, float(c.S_skill))), 4) if c.S_skill is not None else round(max(0.0, min(1.0, c.skill_score_raw)), 4)
        return s_edu, s_exp, s_skill

    def rank(self, job_role, candidates, w_cv=0.40, w_int=0.60, use_ltr=True):
        job_role = self._normalize_role(job_role)
        if job_role not in ROLES:
            raise ValueError(
                f"Invalid job_role. Available: {sorted(ROLES)}")
        if abs(w_cv + w_int - 1.0) > 1e-4:
            raise ValueError("w_cv + w_int must equal 1.0")
        job = JobRequirementProfile.from_role(job_role)
        job.W_CV, job.W_INT = w_cv, w_int
        job.validate()
        eng = CSSEngine(job)

        rows = []
        for c in candidates:
            role = c.job_role or job_role
            s_edu, s_exp, s_skill = self._build_features(c, job)
            f = CandidateFeatures(
                candidate_id=c.candidate_id,
                job_role=role,
                edu_level=c.edu_level,
                edu_relevance=c.edu_relevance,
                years_experience=c.years_experience,
                skill_score_raw=s_skill,
                P_mcq=max(0.0, min(1.0, c.P_mcq)),
                P_desc=max(0.0, min(1.0, c.P_desc)),
                P_code=max(0.0, min(1.0, c.P_code)),
                gender=c.gender,
                age_group=c.age_group,
                has_coding=bool(getattr(c, "has_coding", True)),
            )
            s = eng.score_one(f)
            rows.append({
                "candidate_id": c.candidate_id,
                "candidate_name": c.candidate_name,
                "job_role": role,
                "S_edu": s_edu,
                "S_exp": s_exp,
                "S_skill": s_skill,
                "S_cv": s.S_cv,
                "S_int": s.S_int,
                "CSS": s.CSS,
                "P_mcq": s.P_mcq,
                "P_desc": s.P_desc,
                "P_code": s.P_code,
                "passed_hard_filter": s.passed_hard_filter,
                "filter_fail_reason": s.filter_fail_reason,
                "w_cv": w_cv,
                "w_int": w_int,
                "required_years": job.required_years,
                "input": c,
            })

        if use_ltr and self.ltr is not None:
            import numpy as np
            import pandas as pd
            df_ltr = pd.DataFrame([{
                "S_edu": r["S_edu"], "S_exp": r["S_exp"], "S_skill": r["S_skill"],
                "P_mcq": r["P_mcq"], "P_desc": r["P_desc"], "P_code": r["P_code"]
            } for r in rows])
            ltr_scores = self.ltr.predict(df_ltr)
            for r, sc in zip(rows, ltr_scores):
                r["ltr_score"] = round(float(sc), 4)

        def _rank_key(r):
            css = r["CSS"]
            ltr = r.get("ltr_score") or 0
            return (css, ltr)

        passed = sorted([r for r in rows if r["passed_hard_filter"]],
                        key=_rank_key, reverse=True)
        near_miss = sorted([r for r in rows if not r["passed_hard_filter"] and r["CSS"] > 0],
                          key=_rank_key, reverse=True)
        failed = [r for r in rows if not r["passed_hard_filter"] and r["CSS"] <= 0]
        for i, r in enumerate(passed, 1):
            r["rank"] = i
        for i, r in enumerate(near_miss, len(passed) + 1):
            r["rank"] = i
        for r in failed:
            r["rank"] = 0
        return job, passed + near_miss + failed


_service = None


def get_service():
    global _service
    if _service is None:
        _service = RankingService()
    return _service
