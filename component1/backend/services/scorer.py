"""CV scoring engine — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Implements the sub-score equations that mirror component3/engine/css_engine.py.

Equations
---------
S_edu  = EDU_LEVEL_SCORES[edu_level]                             # {1:0.40, 2:0.60, 3:0.80, 4:1.00}
S_exp  = min(experience_years / REQUIRED_YEARS[role], 1.0)
S_skill = skill_score_raw = matched_skills / len(required_skills)

cv_matching_score (0–100):
  • WITH JD:    0.35 * S_skill + 0.25 * S_exp + 0.15 * S_edu + 0.25 * jd_similarity_score
  • WITHOUT JD: 0.50 * S_skill + 0.30 * S_exp + 0.20 * S_edu
  (weights match ROLE_CV_WEIGHTS defaults; exact formula documented in README)

For the 10 component-3 aligned roles the weighting follows ROLE_CV_WEIGHTS exactly
when no JD is supplied, so cv_matching_score agrees with Component 3's S_cv.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data.role_requirements import (
    EDU_LEVEL_SCORES,
    REQUIRED_YEARS,
    REQUIRED_SKILLS,
    ROLE_CV_WEIGHTS,
)

logger = logging.getLogger("component1.scorer")


@dataclass
class CVScores:
    S_edu:               float
    S_exp:               float
    S_skill:             float
    skill_score_raw:     float   # same as S_skill; field name consumed by Component 3
    jd_similarity_score: Optional[float]
    cv_matching_score:   float   # 0–100


def score(
    role:               str,
    edu_level:          int,
    experience_years:   float,
    skills:             List[str],
    jd_similarity_score: Optional[float] = None,
) -> CVScores:
    """Compute all sub-scores for a candidate.

    Parameters
    ----------
    role              : Exact role name string (one of the 20 canonical roles).
    edu_level         : 1=Diploma, 2=BSc, 3=MSc, 4=PhD.
    experience_years  : Extracted or stated years of experience.
    skills            : List of lower-cased matched skill strings.
    jd_similarity_score: If a JD was supplied, the cosine similarity (0–1); else None.
    """
    # ── S_edu ──────────────────────────────────────────────────────────────────
    S_edu = EDU_LEVEL_SCORES.get(edu_level, 0.40)

    # ── S_exp ──────────────────────────────────────────────────────────────────
    req_years = REQUIRED_YEARS.get(role, 3.0)
    S_exp = min(experience_years / req_years, 1.0) if req_years > 0 else 0.0

    # ── S_skill / skill_score_raw ──────────────────────────────────────────────
    req_skills = REQUIRED_SKILLS.get(role, [])
    if req_skills:
        skills_lower = {s.lower() for s in skills}
        matched = sum(1 for s in req_skills if s.lower() in skills_lower)
        S_skill = matched / len(req_skills)
    else:
        S_skill = 0.0
    skill_score_raw = S_skill  # alias for Component 3 compatibility

    # ── cv_matching_score ──────────────────────────────────────────────────────
    if jd_similarity_score is not None:
        # With JD: introduce semantic JD similarity as a first-class component
        # Weighting: skill=0.35, exp=0.25, edu=0.15, jd_sim=0.25
        cv_matching_score = (
            0.35 * S_skill +
            0.25 * S_exp   +
            0.15 * S_edu   +
            0.25 * float(jd_similarity_score)
        ) * 100.0
    else:
        # Without JD: use role-specific CV weights (mirrors Component 3's S_cv)
        cv_weights = ROLE_CV_WEIGHTS.get(
            role,
            {"w_edu": 0.20, "w_exp": 0.30, "w_skill": 0.50},
        )
        cv_matching_score = (
            cv_weights["w_edu"]   * S_edu   +
            cv_weights["w_exp"]   * S_exp   +
            cv_weights["w_skill"] * S_skill
        ) * 100.0

    # Clamp to [0, 100]
    cv_matching_score = max(0.0, min(100.0, cv_matching_score))

    return CVScores(
        S_edu=round(S_edu, 4),
        S_exp=round(S_exp, 4),
        S_skill=round(S_skill, 4),
        skill_score_raw=round(skill_score_raw, 4),
        jd_similarity_score=round(jd_similarity_score, 4) if jd_similarity_score is not None else None,
        cv_matching_score=round(cv_matching_score, 2),
    )
