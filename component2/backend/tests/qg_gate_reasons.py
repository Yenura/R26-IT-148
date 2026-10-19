"""Break down *why* the per-question gate rejects generated questions.

Runs the live QG model for a handful of representative roles and tallies the
first failing gate condition per generated question. This is what tells us
whether the optional relevance lemmatization is worth it (it is not: failures
are dominated by broken option/answer text, not word-form mismatches).
"""
import collections
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
os.environ.setdefault(
    "MODELS_DIR", str(pathlib.Path(__file__).parent.parent.parent / "models")
)
import logging  # noqa: E402

logging.basicConfig(level=logging.ERROR)

import services.qg_engine as qe  # noqa: E402
from services.qg_engine import _get_qg_generator  # noqa: E402
from services.ml_engine import InterviewService  # noqa: E402

ROLES = [
    "Data Scientist", "Frontend Developer", "Cybersecurity Analyst",
    "DevOps Engineer", "UI/UX Designer", "Software Engineer",
]


def first_fail(q, role, skills):
    """First gate condition this question fails, mirroring _is_good_question."""
    if "<unk>" in json.dumps(q, ensure_ascii=False) or "<pad>" in json.dumps(q, ensure_ascii=False):
        return "unk/pad"
    qt = q.get("question_text") or ""
    if qe._is_degenerate(qt):
        return "degenerate-question"
    if qe._is_degenerate(q.get("answer_text") or "") or any(
        qe._is_degenerate(str(o.get("text", "")))
        for o in (q.get("options") or []) if isinstance(o, dict)
    ):
        return "degenerate-answer/options"
    if re.search(r"\s'\s", qt):
        return "bare-quote"
    if skills and q.get("question_type") in ("MCQ", "Descriptive"):
        low = qt.lower()
        sw = {w for s in skills if s for w in re.findall(r"[a-z0-9+#]{3,}", s.lower())}
        qw = set(re.findall(r"[a-z0-9+#]{3,}", low))
        if not ((role.lower() in low) or (qw & sw)):
            return "not-relevant"
    if len(qt) < 20:
        return "question-too-short"
    if q.get("question_type") == "MCQ":
        opts = q.get("options") or []
        ok = (
            isinstance(opts, list) and len(opts) >= 2
            and all(isinstance(o, dict) and o.get("text") for o in opts)
            and (q.get("correct_answer_index") is not None or q.get("correct_option") is not None)
        )
        return "pass" if ok else "mcq-structure"
    if q.get("question_type") == "Descriptive":
        ans = (q.get("answer_text") or "").strip()
        if len(ans) < 20:
            return "answer-too-short"
        if ans.startswith("This question covers"):
            return "placeholder-answer"
        return "pass"
    return "pass" if qe._is_good_question(q, role, skills) else "other"


def main():
    gen = _get_qg_generator()
    svc = InterviewService(os.environ["MODELS_DIR"])
    tally = collections.Counter()
    for role in ROLES:
        skills = svc.job_requirements[role]
        raw = gen.generate_for_session(
            job_role=role, skills=skills, num_mcq=4, num_desc=2, num_code=0
        ) or []
        for q in raw:
            tally[(q.get("question_type"), first_fail(q, role, skills))] += 1

    print("first failing gate condition (MCQ + Descriptive generated):")
    for (qtype, reason), n in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>4}  {qtype:<12} {reason}")
    total = sum(tally.values())
    passed = sum(n for (_, r), n in tally.items() if r == "pass")
    print(f"\npassed {passed}/{total} ({passed / max(total, 1):.0%})")


if __name__ == "__main__":
    main()
