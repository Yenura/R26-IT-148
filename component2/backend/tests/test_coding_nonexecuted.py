"""Non-executed Coding formats: grading, answer-key secrecy, and coverage.

The candidate's declared language (JavaScript / Java / C++ / Go / Rust) has no
hardened runner, so those Coding questions are graded *without executing code*
using one of three formats.  What must hold:

* the grade comes from the answer key, never from running the candidate's code;
* the answer key never reaches the candidate through ``/interview/start``
  (``accepted_answers`` / ``correct_answer_index`` are absent from the response
  model, so a leaked key would be a shipped answer, not a test failure);
* every language we claim to support actually has questions in the bank.

Run via pytest: python -m pytest tests/test_coding_nonexecuted.py -v
"""
import json
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from models.schemas import InterviewQuestion  # noqa: E402
from routers.interview import _grade_non_executed, _normalize_code_answer  # noqa: E402
from services import role_profiles  # noqa: E402

MODELS_DIR = BACKEND.parent / "models"
NON_EXEC_BANK = MODELS_DIR / "coding_bank_nonexecuted.json"


# ---------------------------------------------------------------------------
# Answer normalisation
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("i += 1", "i+=1"),
        ("i+=1", "i+=1"),
        ("  i  +=  1  ", "i+=1"),
        ("i += 1;", "i+=1"),
        ("Return True", "returntrue"),
        ("", ""),
    ],
)
def test_normalize_code_answer(raw, expected):
    assert _normalize_code_answer(raw) == expected


# ---------------------------------------------------------------------------
# Find the Bug: option selection, no execution
# ---------------------------------------------------------------------------
def test_find_the_bug_grades_the_selected_option():
    q = {"format": "Find the Bug", "language": "Java", "correct_answer_index": 2}
    assert _grade_non_executed(q, {"selected_option": 2}, "Find the Bug")["code_score"] == 100.0
    assert _grade_non_executed(q, {"selected_option": 0}, "Find the Bug")["code_score"] == 0.0


def test_find_the_bug_accepts_a_correct_index_of_zero():
    """Option 0 is a real answer, not a missing one."""
    q = {"format": "Find the Bug", "language": "JavaScript", "correct_answer_index": 0}
    result = _grade_non_executed(q, {"selected_option": 0}, "Find the Bug")
    assert result["is_correct"] is True
    assert result["code_score"] == 100.0


def test_find_the_bug_handles_missing_or_garbage_answers():
    q = {"format": "Find the Bug", "correct_answer_index": 1}
    for answer in ({}, {"selected_option": None}, {"selected_option": "not a number"}):
        assert _grade_non_executed(q, answer, "Find the Bug")["code_score"] == 0.0


# ---------------------------------------------------------------------------
# Predict Output / Complete Function: exact match on a normalised answer
# ---------------------------------------------------------------------------
def test_predict_output_matches_normalised_output():
    q = {"format": "Predict Output", "language": "Go", "accepted_answers": ["14"]}
    assert _grade_non_executed(q, {"answer_text": " 14 "}, "Predict Output")["code_score"] == 100.0
    assert _grade_non_executed(q, {"answer_text": "15"}, "Predict Output")["code_score"] == 0.0


def test_predict_output_keeps_float_and_bool_leniency():
    q = {"format": "Predict Output", "accepted_answers": ["5"]}
    assert _grade_non_executed(q, {"answer_text": "5.0"}, "Predict Output")["code_score"] == 100.0
    q = {"format": "Predict Output", "accepted_answers": ["true"]}
    assert _grade_non_executed(q, {"answer_text": "True"}, "Predict Output")["code_score"] == 100.0


def test_complete_function_ignores_whitespace_and_trailing_semicolon():
    q = {"format": "Complete Function", "language": "C++", "accepted_answers": ["i += 1"]}
    for typed in ("i += 1", "i+=1", "  i  +=  1;", "I += 1"):
        assert _grade_non_executed(q, {"answer_text": typed}, "Complete Function")["code_score"] == 100.0
    assert _grade_non_executed(q, {"answer_text": "i -= 1"}, "Complete Function")["code_score"] == 0.0


def test_complete_function_accepts_any_listed_answer():
    q = {"format": "Complete Function", "accepted_answers": ["x = x + 1", "x += 1"]}
    for typed in ("x += 1", "x = x + 1"):
        assert _grade_non_executed(q, {"answer_text": typed}, "Complete Function")["is_correct"] is True


def test_an_empty_answer_never_matches():
    for fmt, key in (("Predict Output", "answer_text"), ("Complete Function", "answer_text")):
        q = {"format": fmt, "accepted_answers": [""]}
        assert _grade_non_executed(q, {key: ""}, fmt)["code_score"] == 0.0


def test_non_executed_grade_never_claims_to_have_run_code():
    """The result must be self-describing, so scoring cannot confuse the paths."""
    for fmt, answer in (
        ("Find the Bug", {"selected_option": 0}),
        ("Predict Output", {"answer_text": "x"}),
        ("Complete Function", {"answer_text": "x"}),
    ):
        result = _grade_non_executed({"format": fmt, "accepted_answers": ["x"]}, answer, fmt)
        assert result["non_executed"] is True
        assert result["syntax_valid"] is True
        assert result["test_pass_rate"] is None


# ---------------------------------------------------------------------------
# The answer key must never be sent to the candidate
# ---------------------------------------------------------------------------
def test_response_schema_does_not_leak_the_answer_key():
    question = InterviewQuestion(
        id="NEX_X_1", sequence=1, question_text="?", question_type="Coding",
        difficulty="Medium", category="Algorithms", topic="t",
        language="Rust", format="Find the Bug",
        options=[{"index": 0, "text": "a"}, {"index": 1, "text": "b"}],
    )
    payload = question.model_dump()
    assert "accepted_answers" not in payload
    assert "correct_answer_index" not in payload
    assert payload["format"] == "Find the Bug"
    assert [o["text"] for o in payload["options"]] == ["a", "b"]


# ---------------------------------------------------------------------------
# Coverage: every language we claim must have questions
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not NON_EXEC_BANK.exists(), reason="non-executed bank not built")
def test_non_executed_bank_is_well_formed():
    questions = json.loads(NON_EXEC_BANK.read_text(encoding="utf-8"))
    assert questions

    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids)), "question ids must be unique"

    for q in questions:
        assert q["question_type"] == "Coding"
        assert q["format"] in role_profiles.NON_EXECUTED_FORMATS, q["id"]
        assert q["language"] in role_profiles.NON_EXECUTED_LANGUAGES, q["id"]
        assert q["question_text"].strip()
        assert q["code"].strip()
        if q["format"] == "Find the Bug":
            assert q["correct_answer_index"] in range(len(q["options"])), q["id"]
            assert len(q["options"]) >= 3, q["id"]
        else:
            assert q["accepted_answers"], q["id"]
            assert all(a.strip() for a in q["accepted_answers"]), q["id"]


@pytest.mark.skipif(not NON_EXEC_BANK.exists(), reason="non-executed bank not built")
def test_every_supported_language_has_questions():
    """role_profiles.NON_EXECUTED_LANGUAGES is a promise -- hold it."""
    questions = json.loads(NON_EXEC_BANK.read_text(encoding="utf-8"))
    have = {q["language"] for q in questions}
    missing = [l for l in role_profiles.NON_EXECUTED_LANGUAGES if l not in have]
    assert not missing, f"declared as supported but has no questions: {missing}"


@pytest.mark.skipif(not NON_EXEC_BANK.exists(), reason="non-executed bank not built")
def test_every_role_language_can_actually_be_served():
    """A role's resolved language must have enough questions to fill a session."""
    questions = json.loads(NON_EXEC_BANK.read_text(encoding="utf-8"))
    per_language = {}
    for q in questions:
        per_language.setdefault(q["language"], []).append(q)

    python_bank = json.loads((MODELS_DIR / "question_bank.json").read_text(encoding="utf-8"))
    python_coding = [q for q in python_bank if q.get("question_type") == "Coding"]
    per_language.setdefault("Python", []).extend(python_coding)

    for role in role_profiles.ROLE_LANGUAGES:
        if not role_profiles.is_coding_role(role):
            continue
        language = role_profiles.resolve_language(role, None)
        assert language, f"{role} resolves to no language"
        assert per_language.get(language), f"{role} -> {language} has no questions"
