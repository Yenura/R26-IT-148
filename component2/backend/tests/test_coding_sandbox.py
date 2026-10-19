"""Regression tests for the coding sandbox and the external coding bank.

Three real bugs motivated these.  All of them silently zeroed a *correct*
candidate, which is the worst possible failure mode for a hiring product:

1. Test-case inputs are stored as Python-literal *source* (``"[2, 7]"``,
   ``"'abc'"``), but the sandbox injected strings with ``repr``, so
   ``nums="[2,7,11,15]"`` became the string ``'[2,7,11,15]'``.  Every curated
   Coding question was ungradeable, and so was the candidate who solved it.
2. The sandbox wrote the candidate script with the platform default codec, so
   any non-ASCII character (an arrow in a docstring, an accent in a comment)
   raised ``UnicodeEncodeError`` on write and the submission scored 0.
3. The import guard blocked ``sys``; because nearly every stdlib module imports
   ``sys`` internally, ``import re`` / ``import collections`` / ``import json``
   also scored 0.

They also pin the shape of the generated external bank, which is built by
``ml/build_coding_bank.py`` from humaneval-x (apache-2.0) and lbpp
(apache-2.0) and appended at load time.
"""
import json
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from routers.interview import _output_matches, _py_source, _run_code_in_sandbox  # noqa: E402
from services.ml_engine import InterviewService  # noqa: E402

MODELS_DIR = BACKEND.parent / "models"
EXTERNAL_BANK = MODELS_DIR / "coding_bank_external.json"


# ---------------------------------------------------------------------------
# Input injection
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "value,expected",
    [
        ("[2, 7, 11, 15]", "[2, 7, 11, 15]"),   # literal source -> list, not str
        ("9", "9"),                             # literal source -> int
        ("'abc'", "'abc'"),                     # literal source -> str
        ("-1.5", "-1.5"),
        ("True", "True"),
        ("{'a': 1}", "{'a': 1}"),
        ("hello", "'hello'"),                   # genuine string stays a string
        (7, "7"),                               # native JSON types still work
        ([1, 2], "[1, 2]"),
        (True, "True"),
    ],
)
def test_py_source_renders_python_source(value, expected):
    assert _py_source(value) == expected


def test_literal_source_string_reaches_the_candidate_as_its_value():
    """The curated bank convention: '[2,7,11,15]' is a list, not a string."""
    out = _run_code_in_sandbox(
        "print(type(nums).__name__)\nprint(nums[0] + nums[1])",
        {"nums": "[2, 7, 11, 15]"},
    )
    assert out == "list\n9"


def test_two_sum_from_the_curated_bank_now_grades_correctly():
    """The exact entry that exposed the bug (LC_1 stored str inputs)."""
    code = (
        "seen = {}\n"
        "for i, n in enumerate(nums):\n"
        "    if target - n in seen:\n"
        "        print([seen[target - n], i])\n"
        "        break\n"
        "    seen[n] = i\n"
    )
    out = _run_code_in_sandbox(code, {"nums": "[2,7,11,15]", "target": "9"})
    assert _output_matches(out, "[0,1]")


# ---------------------------------------------------------------------------
# Output comparison
# ---------------------------------------------------------------------------
def test_output_matches_ignores_set_and_dict_order_but_not_list_order():
    assert _output_matches("{'a', 'b'}", "{'b', 'a'}")
    assert _output_matches("{'a': 1, 'b': 2}", "{'b': 2, 'a': 1}")
    assert not _output_matches("[1, 2]", "[2, 1]")
    assert _output_matches("[1, 2]", "[1,2]")


def test_output_matches_keeps_numeric_and_bool_leniency():
    assert _output_matches("5.0", "5")
    assert _output_matches("true", "True")
    assert not _output_matches("abc", "abd")


# ---------------------------------------------------------------------------
# Sandbox behaviour
# ---------------------------------------------------------------------------
def test_non_ascii_source_does_not_silently_zero_the_candidate():
    code = '"""arrow -> \u2192 and limit \u2264 10"""\nprint("noted")'
    assert _run_code_in_sandbox(code, {}) == "noted"


@pytest.mark.parametrize("module", ["re", "collections", "json", "heapq", "bisect", "typing"])
def test_common_stdlib_is_importable(module):
    assert _run_code_in_sandbox(f"import {module}\nprint('OK')", {}) == "OK"


@pytest.mark.parametrize("module", ["os", "sys", "subprocess", "socket", "shutil", "urllib"])
def test_dangerous_modules_stay_blocked(module):
    assert _run_code_in_sandbox(f"import {module}\nprint('LEAK')", {}) == ""


def test_candidate_cannot_reach_the_filesystem():
    assert _run_code_in_sandbox("print(open('C:/Windows/win.ini').read()[:20])", {}) == ""


# ---------------------------------------------------------------------------
# External coding bank
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not EXTERNAL_BANK.exists(), reason="external bank not built")
def test_external_coding_bank_is_well_formed():
    questions = json.loads(EXTERNAL_BANK.read_text(encoding="utf-8"))
    assert questions, "external bank should not be empty"

    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids)), "question ids must be unique"

    for q in questions:
        assert q["question_type"] == "Coding"
        assert q["language"] == "Python"
        assert q["question_text"].strip()
        assert q["test_cases"], f"{q['id']} has no test cases"
        assert "_reference" not in q, "build-only key leaked into the shipped bank"
        for case in q["test_cases"]:
            assert case["input"], f"{q['id']} has an empty input dict"
            assert isinstance(case["expected_output"], str)


@pytest.mark.skipif(not EXTERNAL_BANK.exists(), reason="external bank not built")
def test_every_external_test_case_injects_as_valid_python():
    """Each stored input must render to valid Python source (the real risk)."""
    import ast

    questions = json.loads(EXTERNAL_BANK.read_text(encoding="utf-8"))
    for q in questions:
        for case in q["test_cases"]:
            source = "".join(f"{k} = {_py_source(v)}\n" for k, v in case["input"].items())
            try:
                ast.parse(source)
            except SyntaxError as e:  # pragma: no cover - failure detail
                raise AssertionError(f"{q['id']} injects invalid source: {source!r} ({e})")


@pytest.mark.skipif(not EXTERNAL_BANK.exists(), reason="external bank not built")
def test_external_questions_run_end_to_end_in_the_sandbox():
    """A real (small) question must be gradeable, not just well-formed."""
    by_id = {q["id"]: q for q in json.loads(EXTERNAL_BANK.read_text(encoding="utf-8"))}
    q = by_id.get("HEX_0")
    if q is None:
        pytest.skip("HEX_0 not present")

    case = q["test_cases"][0]
    solution = (
        "def has_close_elements(numbers, threshold):\n"
        "    for i, a in enumerate(numbers):\n"
        "        for j, b in enumerate(numbers):\n"
        "            if i != j and abs(a - b) < threshold:\n"
        "                return True\n"
        "    return False\n"
        "print(has_close_elements(numbers, threshold))\n"
    )
    out = _run_code_in_sandbox(solution, case["input"])
    assert _output_matches(out, case["expected_output"])


def test_loader_appends_external_questions_and_skips_duplicates():
    if not EXTERNAL_BANK.exists():
        pytest.skip("external bank not built")

    service = object.__new__(InterviewService)  # skip the heavy __init__
    service.models_dir = str(MODELS_DIR)
    service.question_bank = [{"id": "LC_1", "question_type": "Coding"}]

    # Pre-seed one id so the append has to skip it.
    seeded = json.loads(EXTERNAL_BANK.read_text(encoding="utf-8"))[0]["id"]
    service.question_bank.append({"id": seeded, "question_type": "Coding"})

    service._load_external_coding_bank()

    ids = [q["id"] for q in service.question_bank]
    assert len(ids) == len(set(ids)), "duplicates must not be appended"

    # Every question from every generated bank must now be present exactly once.
    for name in InterviewService.EXTERNAL_BANK_FILES:
        path = MODELS_DIR / name
        if not path.exists():
            continue
        for q in json.loads(path.read_text(encoding="utf-8")):
            assert q["id"] in ids, f"{q['id']} from {name} was not loaded"
