"""
Component 2: Role / language / coding-profile consistency.

Guards the invariants that used to be violated in production:

* A role with a non-zero coding weight MUST get a coding profile and an
  offerable language (Blockchain Developer and Site Reliability Engineer had a
  coding weight but a ``none`` profile).
* A role with a zero coding weight MUST NOT be treated as a coding role
  (Network Engineer was listed as both a language role and a non-coding role).
* The interview may only offer languages the execution sandbox can run; the
  sandbox is Python-only, so declaring Java/Kotlin/Solidity and then grading
  the answer as Python is exactly the bug this test prevents.
* The per-type question distribution must match the scoring weights it is
  graded with.

Run directly:   python tests/test_role_profiles.py
Run via pytest: python -m pytest tests/test_role_profiles.py -v
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from services import role_profiles  # noqa: E402
from services.ml_engine import InterviewService  # noqa: E402

MODELS_DIR = str(Path(__file__).parent.parent.parent / "models")
EXPECTED_JOB_COUNT = 20


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def service() -> InterviewService:
    return InterviewService(MODELS_DIR)


@pytest.fixture(scope="module")
def weights() -> dict:
    cfg = _load(Path(MODELS_DIR) / "interview_scoring_config.json")
    return cfg["interview_weights"]


@pytest.fixture(scope="module")
def roles() -> list:
    return list(_load(Path(MODELS_DIR) / "job_requirements.json").keys())


# ---------------------------------------------------------------------------
# Static map integrity
# ---------------------------------------------------------------------------

def test_maps_cover_exactly_the_configured_roles(roles):
    covered = set(role_profiles.ROLE_LANGUAGES) | set(role_profiles.NON_CODING_ROLES)
    assert covered == set(roles), f"role maps disagree with config: {covered ^ set(roles)}"
    assert len(roles) == EXPECTED_JOB_COUNT


def test_coding_and_non_coding_roles_do_not_overlap():
    overlap = set(role_profiles.ROLE_LANGUAGES) & set(role_profiles.NON_CODING_ROLES)
    assert not overlap, f"roles are both coding and non-coding: {overlap}"


def test_every_declared_language_list_is_non_empty():
    for role, langs in role_profiles.ROLE_LANGUAGES.items():
        assert langs, f"{role} is a coding role with no declared language"


# ---------------------------------------------------------------------------
# Weight <-> profile <-> language agreement
# ---------------------------------------------------------------------------

def test_coding_weight_matches_coding_role(service, roles, weights):
    for role in roles:
        weight = weights[role]["coding"]
        profile = service._determine_coding_profile(role, [])
        if weight > 0:
            assert profile != "none", f"{role}: weight {weight} but profile is none"
            assert role_profiles.is_coding_role(role), f"{role} has weight but no languages"
        else:
            assert profile == "none", f"{role}: weight 0 but profile is {profile}"
            assert not role_profiles.is_coding_role(role), f"{role} has no weight but languages"


def test_only_coding_roles_get_distribution_coding(service, roles):
    for role in roles:
        profile = service._determine_coding_profile(role, [])
        for total in (5, 10, 20):
            mcq, desc, code = service._get_question_distribution(role, profile, total)
            assert mcq + desc + code == total, f"{role}@{total}: {mcq}+{desc}+{code}"
            if profile == "none":
                assert code == 0, f"{role}@{total}: non-coding role got {code} coding questions"


def test_distribution_tracks_scoring_weights(service, weights):
    """The question mix must follow the same weights used to grade it."""
    for role, w in weights.items():
        profile = service._determine_coding_profile(role, [])
        _, _, code = service._get_question_distribution(role, profile, 20)
        if w["coding"] <= 0:
            assert code == 0, f"{role}: zero coding weight but {code} coding questions"
        else:
            assert code > 0, f"{role}: coding weight {w['coding']} but no coding questions"


# ---------------------------------------------------------------------------
# Executable-language guarantee
# ---------------------------------------------------------------------------

def test_offered_languages_are_executable(roles):
    executable = set(role_profiles.executable_languages())
    for role in roles:
        for lang in role_profiles.available_languages(role):
            assert lang in executable, f"{role} offers non-executable {lang}"


def test_every_coding_role_offers_python(roles):
    """Python is the only hardened runner, so it must always be offerable."""
    for role in roles:
        langs = role_profiles.available_languages(role)
        if role_profiles.is_coding_role(role):
            assert "Python" in langs, f"{role} offers no runnable language: {langs}"
        else:
            assert langs == [], f"non-coding {role} offers {langs}"


def test_resolve_language_never_returns_unsupported(roles):
    executable = set(role_profiles.executable_languages())
    for role in roles:
        for requested in ("Java", "Kotlin", "Solidity", "TypeScript", "Auto", "", None, "Python"):
            resolved = role_profiles.resolve_language(role, requested)
            if role_profiles.is_coding_role(role):
                assert resolved in executable, f"{role} + {requested!r} -> {resolved}"
            else:
                assert resolved is None, f"non-coding {role} resolved {resolved}"


# ---------------------------------------------------------------------------
# Language detection for the roles that used to be wrong
# ---------------------------------------------------------------------------

def test_detected_language_is_role_appropriate():
    assert role_profiles.detect_language("Blockchain Developer", []) == "Solidity"
    assert role_profiles.detect_language("Mobile App Developer", []) == "Kotlin"
    assert role_profiles.detect_language("Frontend Developer", []) == "JavaScript"
    assert role_profiles.detect_language("Data Engineer", []) == "Python"


def test_unknown_role_falls_back_to_skill_inference():
    # Solidity/Ethereum role we don't have an entry for.
    assert role_profiles.detect_language(
        "Smart Contract Auditor", ["Solidity", "Ethereum", "Web3.js"]
    ) == "Solidity"
    # Unknown role with only SQL-ish skills.
    assert role_profiles.determine_coding_profile(
        "Report Writer", ["SQL", "Reporting"]
    ) == "sql"
    # Unknown role with test-automation skills must be treated as coding, not SQL.
    assert role_profiles.determine_coding_profile(
        "Automation Tester", ["Selenium", "pytest", "CI/CD"]
    ) == "full"


def test_scoring_config_weight_overrides_skill_keywords():
    """A zero coding weight wins even when the skills look like a coding role."""
    assert role_profiles.determine_coding_profile(
        "Network Engineer", ["Python", "TCP/IP"], coding_weight=0.0
    ) == "none"
    assert role_profiles.determine_coding_profile(
        "Blockchain Developer", ["Solidity"], coding_weight=0.45
    ) == "full"
