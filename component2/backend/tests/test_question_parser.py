"""
Tests for the QG output parser in ml/question_generator.py.

Regression focus: the coding field parser used a non-greedy ``\\[.*?\\]`` which
truncated at the first ``]``, so any test case whose input contains a list
(e.g. "stones = [2,7,4,1,8,1]") failed to parse and the question became
unscorable. It now decodes the first JSON value and normalizes the trained
``{"input": {"raw": "x = <literal>"}}`` shape into ``{"x": <literal>}``, which is
what the interview router executes.

Run:  cd component2/backend && python -m pytest tests/test_question_parser.py -v
"""
import sys
from pathlib import Path

import pytest

COMPONENT2 = Path(__file__).resolve().parents[2]
for p in (str(COMPONENT2 / "ml"), str(COMPONENT2 / "backend")):
    if p not in sys.path:
        sys.path.insert(0, p)

from question_generator import (  # noqa: E402
    _parse_a,
    _parse_c,
    _parse_k,
    _parse_l,
    _parse_o,
    _parse_q,
    _parse_t,
    _normalize_test_case,
)

V2_CODING = (
    "Q: Last Stone Weight II. Given `stones`, smash two at a time.\n"
    "L: Python\n"
    'T: [{"input": {"raw": "stones = [2,7,4,1,8,1]"}, "expected_output": "1"}, '
    '{"input": {"raw": "stones = [31,26,33,21,40]"}, "expected_output": "5"}]\n'
    "C: O(n)"
)


def test_parse_t_handles_nested_brackets():
    """The old non-greedy regex truncated at the first ']' inside a list."""
    cases = _parse_t(V2_CODING)
    assert len(cases) == 2


def test_parse_t_unwraps_raw_into_named_literal():
    cases = _parse_t(V2_CODING)
    assert cases[0]["input"] == {"stones": [2, 7, 4, 1, 8, 1]}
    assert cases[1]["input"] == {"stones": [31, 26, 33, 21, 40]}
    assert cases[0]["expected_output"] == "1"


def test_parse_t_is_tolerated_by_scorer_literal_check():
    """The router only executes input dicts whose values are Python literals."""
    import ast

    for tc in _parse_t(V2_CODING):
        for v in tc["input"].values():
            ast.literal_eval(repr(v))  # must not raise


def test_parse_t_keeps_plain_dict_input_unchanged():
    text = 'T: [{"input": {"n": 5}, "expected_output": "25"}]'
    assert _parse_t(text)[0]["input"] == {"n": 5}


def test_parse_t_malformed_json_returns_empty():
    assert _parse_t("T: [not json at all") == []


def test_parse_t_drops_non_dict_entries():
    assert _parse_t('T: [1, 2, "x"]') == []


def test_parse_t_missing_marker_returns_empty():
    assert _parse_t("Q: no test cases here") == []


def test_normalize_test_case_ignores_non_raw_shapes():
    tc = {"input": {"n": 3}, "expected_output": "9"}
    assert _normalize_test_case(tc) is tc


def test_parse_other_fields():
    assert _parse_l(V2_CODING) == "Python"
    assert _parse_c(V2_CODING) == "O(n)"
    assert _parse_q(V2_CODING).startswith("Last Stone Weight II")

    mcq = "Q: Which? O: one | two | three A: 1"
    opts, idx = _parse_o(mcq)
    assert opts == ["one", "two", "three"]
    assert idx == 1

    desc = "Q: Why? A: Because it matters. K: alpha, beta"
    assert _parse_a(desc).startswith("Because")
    assert _parse_k(desc) == ["alpha", "beta"]
