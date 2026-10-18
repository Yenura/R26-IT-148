"""Unit tests — C3 _build_features scale normalization (H-4).

C1 emits S_* on 0–100; the CSS engine works in 0–1. Values above 1 must
be normalized so raw C1 scores can never blow through hard-filter
thresholds. No server, DB, or model load required.
"""
import sys
from pathlib import Path

BACKEND = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND))

from services.ranking_service import RankingService
from models.schemas import CandidateInput


def _features(**kw):
    c = CandidateInput(candidate_id="t1", **kw)
    # Unbound call: the explicit-score branch touches neither self nor job.
    return RankingService._build_features(object(), c, None)


def test_c1_scale_normalized():
    s_edu, s_exp, s_skill = _features(S_edu=81.0, S_exp=100.0, S_skill=16.67)
    assert (s_edu, s_exp, s_skill) == (0.81, 1.0, 0.1667)


def test_unit_scale_untouched():
    assert _features(S_edu=0.81, S_exp=1.0, S_skill=0.1667) == (0.81, 1.0, 0.1667)


def test_mixed_scales():
    s_edu, s_exp, s_skill = _features(S_edu=0.5, S_exp=75.0, S_skill=1.0)
    assert (s_edu, s_exp, s_skill) == (0.5, 0.75, 1.0)


def test_boundary_one_stays_one():
    assert _features(S_edu=1.0, S_exp=1.0, S_skill=1.0) == (1.0, 1.0, 1.0)
