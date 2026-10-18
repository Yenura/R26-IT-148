"""Report: how does the live QG model path behave across all 20 roles?

For each role, ask the QG model for a mini-session, then quantify:
  raw generated / pass quality gate / relevance to the role's skills /
  whether generate_questions_qg returned questions or fell back to the bank.
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
    _get_qg_generator, _is_good_question, generate_questions_qg,
)
from services.ml_engine import InterviewService  # noqa: E402
from services.skill_aliases import skill_matchesAny  # noqa: E402

models_dir = os.environ["MODELS_DIR"]
svc = InterviewService(models_dir)

print("Loading generator ...")
gen = _get_qg_generator()
print(f"active backend: model_type={gen._model_type!r}, "
      f"params={sum(p.numel() for p in gen._model.parameters()):,}\n")


def relevance(q, skills):
    targets = [str(q.get("category", "")), str(q.get("topic", "")), str(q.get("question_text", ""))]
    return any(skill_matchesAny(s, targets) for s in skills)


roles = sorted(svc.job_requirements)
rows = []
raw_total = good_total = 0
fell_back = 0
t_start = time.time()

for role in roles:
    skills = svc.job_requirements[role]
    profile = svc._determine_coding_profile(role, skills)
    weights = svc.interview_configs.get("interview_weights", {}).get(role, {})
    ncode = 0 if (weights.get("coding", 1) == 0 or profile == "none") else 1

    raw = gen.generate_for_session(
        job_role=role, skills=skills, num_mcq=2, num_desc=1, num_code=ncode
    ) or []
    good = [q for q in raw if _is_good_question(q)]
    raw_total += len(raw)
    good_total += len(good)

    final = generate_questions_qg(
        job_role=role, skills=skills, num_mcq=2, num_desc=1, num_code=ncode,
        coding_profile=profile,
    )
    used_model = final is not None
    if not used_model:
        fell_back += 1

    src = final if used_model else []
    rel = sum(1 for q in src if relevance(q, skills))
    rows.append({
        "role": role, "profile": profile, "raw": len(raw), "good": len(good),
        "model_used": used_model, "returned": len(src),
        "relevant": rel, "sample": (src[0].get("question_text", "")[:70] if src else ""),
    })

print(f"{'Role':<30}{'Prof':<10}{'raw':>4}{'gate':>5}{'model?':>8}{'kept':>5}{'rel':>5}  sample")
print("-" * 110)
for r in rows:
    print(f"{r['role']:<30}{r['profile']:<10}{r['raw']:>4}{r['good']:>5}"
          f"{('yes' if r['model_used'] else 'FALLBACK'):>8}{r['returned']:>5}{r['relevant']:>5}  {r['sample']}")

n = len(rows)
print("-" * 110)
print(f"roles: {n}   total raw: {raw_total}   passed gate: {good_total} "
      f"({good_total/max(raw_total,1):.0%})   model-used roles: {n-fell_back}/{n} "
      f"({(n-fell_back)/n:.0%})   fell back to bank: {fell_back}/{n}")
print(f"elapsed: {time.time()-t_start:.0f}s")
