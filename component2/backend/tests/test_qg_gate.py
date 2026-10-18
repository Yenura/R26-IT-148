"""Tests for the QG quality gate.

The gate is the only thing standing between the weak neural QG model and the
candidate, so its rejections need to be pinned down. Two regressions motivated
these: the model looping on a phrase ("senior senior senior"), and the model
answering a different role's prompt ("network security" for a Software
Engineer), which the old gate accepted because it only checked structure.
"""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from services.qg_engine import _is_degenerate, _is_good_question  # noqa: E402


def _mcq(text, options=("alpha", "beta", "gamma", "delta"), idx=0):
    return {
        "question_type": "MCQ",
        "question_text": text,
        "options": [{"index": i, "text": o} for i, o in enumerate(options)],
        "correct_answer_index": idx,
    }


# --- _is_degenerate -------------------------------------------------------

def test_degenerate_detects_three_identical_words():
    assert _is_degenerate("Which of the following best describes a senior senior senior engineer?")
    assert _is_degenerate("the the the model")


def test_degenerate_detects_a_repeated_trigram():
    assert _is_degenerate(
        "Which of the following best describes a senior a risk when a risk when a risk when"
    )


def test_degenerate_accepts_a_normal_question():
    assert not _is_degenerate("Which of the following best describes SQL injection?")
    assert not _is_degenerate(
        "What is the purpose of access modifiers in Java and how do they differ?"
    )


def test_degenerate_allows_a_word_used_twice_non_adjacently():
    # "which ... which" is fine; only runs of three or repeated trigrams are not.
    assert not _is_degenerate("Which option is correct, and which one is not?")


# --- relevance ------------------------------------------------------------

def test_off_topic_question_is_rejected():
    """A Software Engineer prompt answered with network-security filler."""
    q = _mcq("Which of the following best describes a senior Data Engineer flag "
             "as a risk when network security is handled incorrectly?")
    skills = ["Java", "Python", "C++", "SQL", "React", "REST APIs", "OOP", "Design Patterns"]
    assert not _is_good_question(q, "Software Engineer", skills)


def test_on_topic_question_is_accepted():
    q = _mcq("Which of the following best describes a common pitfall when writing SQL joins?")
    skills = ["Java", "Python", "C++", "SQL", "React", "REST APIs", "OOP", "Design Patterns"]
    assert _is_good_question(q, "Software Engineer", skills)


def test_question_naming_the_role_is_accepted():
    q = _mcq("Which of the following would a senior Software Engineer review in a code review?")
    assert _is_good_question(q, "Software Engineer", ["Java", "Python"])


def test_degenerate_and_off_topic_question_is_rejected():
    q = _mcq("Which of the following best describes a senior senior senior Data Engineer?")
    assert not _is_good_question(q, "Software Engineer", ["Java"])


def test_coding_questions_are_not_relevance_gated():
    """Coding prompts carry algorithm tags, not role skills, so a coding question
    legitimately never names one; only its structure matters."""
    q = {
        "question_type": "Coding",
        "question_text": "Two Sum. Given an array of integers, return indices of the two numbers.",
        "test_cases": [{"input": {"nums": [2, 7], "target": 9}, "expected_output": "[0, 1]"}],
    }
    assert _is_good_question(q, "Software Engineer", ["Java", "Python"])


# --- back-compat: the gate still works without role/skills -----------------

def test_gate_still_usable_without_role_or_skills():
    q = _mcq("Which of the following best describes a primary key in a relational database?")
    assert _is_good_question(q)
    assert not _is_good_question(_mcq("a senior senior senior thing that matters a lot here"))
