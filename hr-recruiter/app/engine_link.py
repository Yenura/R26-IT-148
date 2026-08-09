"""Read-only bridge into Component 3's CSS scoring engine.

Component 3 is linked via ``sys.path`` and is never modified:
- ``component3/engine/css_engine.py`` -> ``CSSEngine``, ``CandidateFeatures``
- ``component3/data/role_configs.py`` -> role weights / thresholds / roles
"""

import os
import re
import sys
from typing import Optional

_HERE          = os.path.dirname(os.path.abspath(__file__))
_APP_ROOT      = os.path.dirname(_HERE)
WORKSPACE_ROOT = os.path.dirname(_APP_ROOT)
COMPONENT3_ROOT = os.path.join(WORKSPACE_ROOT, "component3")

if not os.path.isdir(COMPONENT3_ROOT):
    raise ImportError(
        "Cannot locate component3 for the CSS engine bridge. "
        f"Expected: {COMPONENT3_ROOT}"
    )

if COMPONENT3_ROOT not in sys.path:
    sys.path.insert(0, COMPONENT3_ROOT)

from engine.css_engine import (  # noqa: E402
    CSSEngine,
    CandidateFeatures,
    CandidateScore,
    JobRequirementProfile,
)
from data.role_configs import (  # noqa: E402
    EDU_LEVEL_NAMES,
    ROLES,
    ROLE_DISPLAY_NAMES,
)

VALID_ROLE_KEYS = tuple(ROLES)

# title-case display name -> snake_case engine key (covers component2/4 names)
ROLE_ALIASES = {display: key for key, display in ROLE_DISPLAY_NAMES.items()}
# also accept the raw snake_case key and a case-insensitive display name
for _key in ROLES:
    ROLE_ALIASES[_key] = _key
    ROLE_ALIASES[_key.lower()] = _key
    ROLE_ALIASES[_key.replace("_", " ").lower()] = _key


def normalise_role(role: str) -> str:
    """Return the canonical component3 role key for any component2/3/4 name."""
    if not isinstance(role, str):
        raise ValueError(f"Invalid job_role: {role!r}")
    key = ROLE_ALIASES.get(role)
    if key is None:
        key = ROLE_ALIASES.get(role.strip().lower())
    if key is None:
        raise ValueError(
            f"Unknown job_role {role!r}. Valid roles: "
            + ", ".join(ROLE_DISPLAY_NAMES.values())
        )
    return key


def role_display_name(role_key: str) -> str:
    return ROLE_DISPLAY_NAMES.get(role_key, role_key)


def edu_to_css(education: Optional[str]) -> int:
    """Map a free-text education string to component3's ordinal (1-4)."""
    if not education:
        return 1
    e = re.sub(r"[^a-z0-9]", "", education.lower())
    if any(k in e for k in ("phd", "doctor")):
        return 4
    if any(k in e for k in ("msc", "masters", "mtech", "mba", "meng")):
        return 3
    if any(k in e for k in ("bsc", "btech", "bachelor", "beng", "undergraduate")):
        return 2
    return 1


def build_features(
    candidate_id: str,
    role_key: str,
    experience_years: float,
    education: Optional[str],
    skill_score_raw: float,
    p_mcq: float,
    p_desc: float,
    p_code: float,
    edu_relevance: float = 0.8,
) -> CandidateFeatures:
    return CandidateFeatures(
        candidate_id=candidate_id,
        job_role=role_key,
        edu_level=edu_to_css(education),
        edu_relevance=max(0.0, min(1.0, edu_relevance)),
        years_experience=max(0.0, float(experience_years)),
        skill_score_raw=max(0.0, min(1.0, skill_score_raw)),
        P_mcq=max(0.0, min(1.0, p_mcq)),
        P_desc=max(0.0, min(1.0, p_desc)),
        P_code=max(0.0, min(1.0, p_code)),
    )


__all__ = [
    "CSSEngine",
    "CandidateFeatures",
    "CandidateScore",
    "JobRequirementProfile",
    "ROLE_ALIASES",
    "VALID_ROLE_KEYS",
    "build_features",
    "edu_to_css",
    "normalise_role",
    "role_display_name",
    "EDU_LEVEL_NAMES",
]
