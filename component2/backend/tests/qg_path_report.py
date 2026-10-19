"""Report: how does the live QG model path behave across all 20 roles?

With per-question gating and by-type routing (MCQ/Descriptive from the model,
Coding always from the curated bank), quantify per role:
  1. raw generated vs. per-question gate pass rate, by type
  2. the served mix from the *real* session path, and how many served
     questions came from the model vs. the curated bank.
"""
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
os.environ.setdefault(
    "MODELS_DIR", str(pathlib.Path(__file__).parent.parent.parent / "models")
)

from services.qg_engine import (  # noqa: E402
    _get_qg_generator, _is_good_question,
)
from services.ml_engine import InterviewService  # noqa: E402

models_dir = os.environ["MODELS_DIR"]
svc = InterviewService(models_dir)

print("Loading generator ...")
gen = _get_qg_generator()
print(f"active backend: model_type={gen._model_type!r}, "
      f"params={sum(p.numel() for p in gen._model.parameters()):,}\n")

roles = sorted(svc.job_requirements)


def _count(rows, qtype):
    return sum(1 for q in rows if q.get("question_type") == qtype)


# ── 1. Per-question gate pass rate (Coding is never generated) ─────────────
print("Per-question gate pass rate (MCQ + Descriptive only; Coding is bank-sourced)")
print(f"{'Role':<30}{'MCQ gate':>12}{'Desc gate':>12}{'pass %':>9}")
print("-" * 63)
raw_tot = gate_tot = 0
t0 = time.time()
for role in roles:
    skills = svc.job_requirements[role]
    raw = gen.generate_for_session(
        job_role=role, skills=skills, num_mcq=3, num_desc=2, num_code=0
    ) or []
    good = [q for q in raw if _is_good_question(q, role, skills)]
    raw_tot += len(raw)
    gate_tot += len(good)
    print(f"{role:<30}{_count(good, 'MCQ'):>4}/{_count(raw, 'MCQ'):<7}"
          f"{_count(good, 'Descriptive'):>4}/{_count(raw, 'Descriptive'):<7}"
          f"{len(good) / max(len(raw), 1):>8.0%}")
print("-" * 63)
print(f"raw: {raw_tot}   passed gate: {gate_tot} ({gate_tot / max(raw_tot, 1):.0%})"
      f"   elapsed {time.time() - t0:.0f}s\n")


# ── 2. Served mix + model share, via the real session path ─────────────────
print("Served sessions (real create_interview_session path, 10 questions/role)")
print(f"{'Role':<30}{'MCQ':>5}{'Desc':>5}{'Code':>5}{'model':>7}{'bank':>6}")
print("-" * 63)
t1 = time.time()
model_served = all_served = 0
model_roles = 0
for role in roles:
    s = svc.create_interview_session(
        candidate_id="qg-report", job_role=role, num_questions=10
    )
    qc = s["question_count"]
    src = s["question_source"]
    model_served += src["model"]
    all_served += len(s["questions"])
    model_roles += 1 if src["model"] else 0
    print(f"{role:<30}{qc['mcq']:>5}{qc['descriptive']:>5}{qc['coding']:>5}"
          f"{src['model']:>7}{src['bank']:>6}")
print("-" * 63)
print(f"roles serving >=1 model question: {model_roles}/{len(roles)}   "
      f"model questions served: {model_served}/{all_served} "
      f"({model_served / max(all_served, 1):.0%})   elapsed {time.time() - t1:.0f}s")
