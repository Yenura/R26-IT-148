"""
Unit tests for the T5 question-generation evaluation metrics.

These lock in that the training/eval code uses *real* generation metrics
(corpus BLEU-4 with brevity penalty, ROUGE-L F1 from the LCS) rather than the
teacher-forced token accuracy the previous pipeline reported.

Run:  cd component2/backend && python -m pytest tests/test_t5_metrics.py -v
"""
import sys
from pathlib import Path

import pytest

COMPONENT2 = Path(__file__).resolve().parents[2]
if str(COMPONENT2) not in sys.path:
    sys.path.insert(0, str(COMPONENT2))

from ml.train_t5_qg_v2 import (  # noqa: E402
    corpus_bleu4,
    rouge_l_f1,
    field_valid,
    compute_metrics,
)


def test_bleu_identical_is_100():
    h = [["the", "cat", "sat", "on", "the", "mat"]]
    assert corpus_bleu4(h, h) == pytest.approx(100.0, abs=0.01)


def test_bleu_no_overlap_is_zero():
    hyp = [["alpha", "beta"]]
    ref = [["gamma", "delta"]]
    assert corpus_bleu4(hyp, ref) == 0.0


def test_bleu_short_hypothesis_uses_brevity_penalty():
    # shares a 1-gram but no 2-gram -> 0 (BLEU needs all four orders)
    hyp = [["the", "cat"]]
    ref = [["the", "dog"]]
    assert corpus_bleu4(hyp, ref) == 0.0


def test_bleu_partial_overlap_is_between_zero_and_100():
    # every n-gram order (1..4) has some clipped match, none is perfect
    hyp = [["a", "b", "c", "d", "e"]]
    ref = [["a", "b", "c", "d", "x"]]
    score = corpus_bleu4(hyp, ref)
    assert 0.0 < score < 100.0


def test_bleu_is_zero_when_a_4gram_order_has_no_match():
    # reference shares 1/2/3-grams but no 4-gram -> standard BLEU-4 == 0
    hyp = [["a", "b", "c", "d"]]
    ref = [["a", "b", "c", "x"]]
    assert corpus_bleu4(hyp, ref) == 0.0


def test_rouge_l_identical_is_100():
    toks = ["a", "b", "c", "d"]
    assert rouge_l_f1(toks, toks) == pytest.approx(1.0)


def test_rouge_l_disjoint_is_zero():
    assert rouge_l_f1(["a", "b"], ["x", "y"]) == 0.0


def test_rouge_l_partial_lcs():
    # lcs("abc","axc") == 2, p=r=2/3 -> F1 = 2/3
    assert rouge_l_f1(["a", "b", "c"], ["a", "x", "c"]) == pytest.approx(2 / 3)


def test_field_valid_mcq_requires_options_and_answer():
    assert field_valid("[MCQ]", "Q: What? O: a | b | c A: 1")
    assert not field_valid("[MCQ]", "Q: What? A: 1")          # no options
    assert not field_valid("[Descriptive]", "Q: Why?")         # no answer


def test_field_valid_is_case_insensitive():
    assert field_valid("[Descriptive]", "q: Why? a: Because.")


def test_compute_metrics_shape_and_by_type():
    records = [
        {"qtype": "[MCQ]", "ref": "Q: A? O: x | y A: 1", "hyp": "Q: A? O: x | y A: 1"},
        {"qtype": "[MCQ]", "ref": "Q: B? O: p | q A: 0", "hyp": "garbage output"},
        {"qtype": "[Descriptive]", "ref": "Q: C? A: because", "hyp": "Q: C? A: because"},
    ]
    m = compute_metrics(records)
    assert m["n"] == 3
    assert m["bleu4"] >= 0.0
    assert 0.0 <= m["rouge_l"] <= 100.0
    assert m["exact_match"] == pytest.approx(100.0 * 2 / 3, abs=0.01)
    assert m["field_valid"] == pytest.approx(100.0 * 2 / 3, abs=0.01)
    assert set(m["by_type"]) == {"[MCQ]", "[Descriptive]"}
    assert m["by_type"]["[MCQ]"]["field_valid"] == 50.0
