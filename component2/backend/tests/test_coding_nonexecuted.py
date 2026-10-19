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
import re
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

#: Banks whose questions are graded without executing code.  SQL lives in its
#: own file -- its answer keys are proven with ``sqlite3`` at build time, which
#: is a different kind of evidence from the compiled-language banks -- so "the
#: non-executed bank" is the union of these.
NON_EXEC_BANKS = (
    MODELS_DIR / "coding_bank_nonexecuted.json",
    MODELS_DIR / "coding_bank_sql.json",
)
NON_EXEC_BANK = NON_EXEC_BANKS[0]


def _non_executed_banks_present() -> bool:
    return any(path.exists() for path in NON_EXEC_BANKS)


def _load_non_executed():
    """Every available non-executed question, across all bank files."""
    questions = []
    for path in NON_EXEC_BANKS:
        if path.exists():
            questions.extend(json.loads(path.read_text(encoding="utf-8")))
    return questions


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
@pytest.mark.skipif(not _non_executed_banks_present(), reason="non-executed bank not built")
def test_non_executed_bank_is_well_formed():
    questions = _load_non_executed()
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


@pytest.mark.skipif(not _non_executed_banks_present(), reason="non-executed bank not built")
def test_every_supported_language_has_questions():
    """role_profiles.NON_EXECUTED_LANGUAGES is a promise -- hold it."""
    questions = _load_non_executed()
    have = {q["language"] for q in questions}
    missing = [l for l in role_profiles.NON_EXECUTED_LANGUAGES if l not in have]
    assert not missing, f"declared as supported but has no questions: {missing}"


@pytest.mark.skipif(not _non_executed_banks_present(), reason="non-executed bank not built")
def test_complete_function_accepts_equivalent_spellings():
    """A right answer must not score 0 for writing `x += 1` instead of `x = x + 1`.

    Complete-the-function is graded by exact match, so the accepted list has to
    carry the equivalent spellings -- otherwise this becomes the same silent
    zero-scoring bug that was just fixed in the execution sandbox.
    """
    questions = _load_non_executed()
    with_variants = 0
    for q in questions:
        if q["format"] != "Complete Function":
            continue
        if len(q["accepted_answers"]) > 1:
            with_variants += 1
        for spelling in q["accepted_answers"]:
            result = _grade_non_executed(q, {"answer_text": spelling}, "Complete Function")
            assert result["code_score"] == 100.0, f"{q['id']}: {spelling!r} scored 0"

    assert with_variants >= 10, (
        "the equivalent-spelling expansion looks switched off "
        f"(only {with_variants} questions carry more than one answer)"
    )


@pytest.mark.skipif(not _non_executed_banks_present(), reason="non-executed bank not built")
def test_whitespace_and_semicolons_never_change_a_complete_function_answer():
    questions = _load_non_executed()
    cf = [q for q in questions if q["format"] == "Complete Function"]
    assert cf
    q = cf[0]
    answer = q["accepted_answers"][0]
    for typed in (answer, answer.strip(), f"   {answer}  ", answer.rstrip(";"), answer + ";"):
        assert _grade_non_executed(q, {"answer_text": typed}, "Complete Function")["code_score"] == 100.0, \
            f"{q['id']}: {typed!r} scored 0"


@pytest.mark.skipif(not _non_executed_banks_present(), reason="non-executed bank not built")
def test_python_find_the_bug_correct_option_produces_valid_python():
    """The marked line must be a whole statement, not a fragment.

    This also catches a distractor that was accidentally *also* correct in a way
    that breaks the snippet -- the failure mode found by hand during review.
    """
    questions = _load_non_executed()
    marker = re.compile(r"^(\s*)#\s*\?\?\?.*$", re.M)
    checked = 0
    for q in questions:
        if q["format"] != "Find the Bug" or q["language"] != "Python":
            continue
        correct = q["options"][q["correct_answer_index"]]["text"]
        filled = marker.sub(lambda m: m.group(1) + correct.strip(), q["code"], count=1)
        try:
            compile(filled, "<question>", "exec")
        except SyntaxError as e:  # pragma: no cover - failure detail
            raise AssertionError(f"{q['id']}: correct option does not yield valid Python: {e}")
        checked += 1
    assert checked > 0


@pytest.mark.skipif(not _non_executed_banks_present(), reason="non-executed bank not built")
def test_every_role_language_can_actually_be_served():
    """A role's resolved language must have enough questions to fill a session."""
    questions = _load_non_executed()
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
