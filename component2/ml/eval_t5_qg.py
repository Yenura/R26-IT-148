"""
Evaluate the trained T5 question-generation checkpoint the honest way:
real beam/greedy generation -> corpus BLEU-4, ROUGE-L F1, field-validity,
exact-match, per question type, plus human-readable spot-checks.

Also documents why the *old* checkpoint was unusable (its tokenizer config was
written by transformers 5.15.1 and cannot be loaded by 4.57.6).

Run:  python -m ml.eval_t5_qg
Out:  models/t5_qg_eval.md   (+ JSON summary on stdout)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"


def load_requirements(models_dir: Path):
    p = models_dir / "job_requirements.json"
    if not p.exists():
        return {}
    raw = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    for role, v in raw.items():
        if isinstance(v, dict):
            out[role] = v.get("skills") or v.get("required_skills") or []
        else:
            out[role] = v
    return out


def named_skills(qtext: str, skills) -> list:
    """Which of the role's skills the question names.

    A generated question normally names exactly one -- the training prompts
    carry a single skill -- so "1 of 8" is success, not 12%.
    """
    low = qtext.lower()
    return [s for s in skills if s and s.lower() in low]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=str(MODELS_DIR / "t5_qg"))
    ap.add_argument("--old-model", default=str(MODELS_DIR / "_t5_qg_dead_checkpoint"))
    ap.add_argument("--dataset", default=str(MODELS_DIR / "qg_dataset_v2.json"))
    ap.add_argument("--max-eval", type=int, default=400)
    ap.add_argument("--out", default=str(MODELS_DIR / "t5_qg_eval.md"))
    args = ap.parse_args()

    import torch
    from transformers import AutoTokenizer, T5ForConditionalGeneration
    from ml.train_t5_qg_v2 import compute_metrics, generate_texts

    model_dir = Path(args.model)
    print(f"loading {model_dir} ...", flush=True)
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model = T5ForConditionalGeneration.from_pretrained(str(model_dir))
    model.eval()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"loaded OK ({n_params:,} params, {time.time()-t0:.1f}s)", flush=True)

    data = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    val = data["val"][: args.max_eval]

    t0 = time.time()
    hyps = generate_texts(model, tokenizer, [e["input"] for e in val], max_new=128, max_src=64, batch=16)
    records = [
        {"qtype": e["input"].split("]")[0] + "]", "input": e["input"], "ref": e["output"], "hyp": h}
        for e, h in zip(val, hyps)
    ]
    metrics = compute_metrics(records)
    print(f"generated {len(records)} in {time.time()-t0:.1f}s -> "
          f"rouge_l={metrics['rouge_l']} bleu4={metrics['bleu4']}", flush=True)

    # ── App-path probes (uses the exact QuestionGenerator the backend uses) ──
    probes = []
    try:
        sys.path.insert(0, str(BASE_DIR / "backend"))
        sys.path.insert(0, str(BASE_DIR / "ml"))
        from question_generator import QuestionGenerator
        reqs = load_requirements(MODELS_DIR)
        gen = QuestionGenerator(model_path=str(model_dir), fallback_bank=[])
        print("app generator available:", gen.is_available, gen.backend, flush=True)
        for role in ["Software Engineer", "Data Scientist", "Cybersecurity Analyst", "Business/Systems Analyst"]:
            skills = reqs.get(role, [])[:8]
            if not skills:
                continue
            qs = gen.generate_for_session(role, skills, num_mcq=2, num_desc=1, num_code=0)
            for q in qs:
                qt = q.get("question_text", "")
                probes.append({
                    "role": role,
                    "type": q.get("question_type"),
                    "question": qt,
                    "names_skill": ", ".join(named_skills(qt, skills)[:2]) or "-",
                })
    except Exception as exc:  # pragma: no cover
        print("app-path probe failed:", exc, flush=True)

    # ── Why the old checkpoint was unusable ─────────────────────────────────
    old_note = "n/a"
    old_dir = Path(args.old_model)
    if old_dir.exists():
        try:
            AutoTokenizer.from_pretrained(str(old_dir))
            old_note = "tokenizer loaded (unexpected)"
        except Exception as exc:
            old_note = f"AutoTokenizer/from_pretrained FAILED: {type(exc).__name__}: {exc}"
    else:
        old_note = "old checkpoint not present"

    # ── Markdown report ─────────────────────────────────────────────────────
    L = []
    L.append("# T5 question-generation — evaluation report\n")
    L.append(f"- model: `{model_dir}`  ({n_params:,} params)")
    L.append(f"- eval set: first {len(records)} of {len(data['val'])} `{Path(args.dataset).name}` validation rows")
    L.append("- generation: greedy (num_beams=1), max_new_tokens=128, prompt truncated to 64 tokens")
    L.append("- metrics: corpus BLEU-4 (clipped 1-4 gram + brevity penalty), ROUGE-L F1 (LCS), "
             "field-validity vs the app's parser, exact-match\n")

    L.append("## Overall\n")
    L.append("| metric | value |")
    L.append("|---|---|")
    L.append(f"| BLEU-4 | {metrics['bleu4']} |")
    L.append(f"| ROUGE-L F1 | {metrics['rouge_l']} |")
    L.append(f"| field-valid % | {metrics['field_valid']} |")
    L.append(f"| exact-match % | {metrics['exact_match']} |")
    L.append(f"| n | {metrics['n']} |\n")

    L.append("## By question type\n")
    L.append("| type | n | BLEU-4 | ROUGE-L | field-valid % |")
    L.append("|---|---|---|---|---|")
    for t, m in metrics["by_type"].items():
        L.append(f"| {t} | {m['n']} | {m['bleu4']} | {m['rouge_l']} | {m['field_valid']} |")
    L.append("")
    # Connect the metric to what the app actually does: the QG gate is
    # all-or-nothing, so a batch survives only if every question parses.
    bt = metrics["by_type"]

    def _fv(t):
        return (bt.get(t, {}).get("field_valid") or 0.0) / 100.0

    batch_pass = _fv("[MCQ]") ** 2 * _fv("[Descriptive]") * _fv("[Coding]")
    L.append(f"- implied all-pass rate for a 2 MCQ + 1 descriptive + 1 coding batch: "
             f"~{100 * batch_pass:.1f}% (upper bound - the real gate, `_is_good_question`, is stricter)\n")

    hist = model_dir / "history.json"
    if hist.exists():
        rep = json.loads(hist.read_text(encoding="utf-8"))
        b = rep.get("baseline", {})
        L.append("## Training progression (generation metrics, not teacher-forced)\n")
        L.append(f"- untrained baseline: ROUGE-L {b.get('rouge_l')} / BLEU-4 {b.get('bleu4')} "
                 f"/ field-valid {b.get('field_valid')}%")
        L.append("")
        L.append("| step | phase | ROUGE-L | BLEU-4 | field-valid % | exact % |")
        L.append("|---|---|---|---|---|---|")
        for h in rep.get("history", []):
            em = h.get("exact_match")
            L.append(f"| {h.get('step')} | {h.get('phase')} | {h.get('rouge_l')} | {h.get('bleu4')} "
                     f"| {h.get('field_valid')} | {'-' if em is None else em} |")
        L.append("")
        L.append(f"- best checkpoint: step {rep.get('best', {}).get('step')} "
                 f"(ROUGE-L {rep.get('best', {}).get('rouge_l')})")
        L.append(f"- training wall-clock: {rep.get('elapsed_min')} min\n")

    L.append("## Spot-checks (prompt / reference / generated)\n")
    for t in ("[MCQ]", "[Descriptive]", "[Coding]"):
        sub = [r for r in records if r["qtype"] == t][:3]
        if not sub:
            continue
        L.append(f"### {t}\n")
        for r in sub:
            L.append(f"- **prompt**: `{r['input']}`")
            L.append(f"  - reference: {r['ref'][:220].replace(chr(10), ' / ')}")
            L.append(f"  - generated: {r['hyp'][:220].replace(chr(10), ' / ')}")
        L.append("")

    if probes:
        L.append("## App-path probes (real backend QuestionGenerator)\n")
        L.append("| role | type | role skill named | question |")
        L.append("|---|---|---|---|")
        for p in probes:
            q = p["question"][:140].replace("|", "/")
            L.append(f"| {p['role']} | {p['type']} | {p['names_skill']} | {q} |")
        L.append("")

    L.append("## Why the previous checkpoint was unusable\n")
    L.append(f"- `{old_dir}`: {old_note}")
    L.append("- its `tokenizer_config.json` had `extra_special_tokens` as a *list* (transformers 5.15.1 "
             "format); transformers 4.57.6 expects a dict, so `AutoTokenizer.from_pretrained` raised "
             "`AttributeError: 'list' object has no attribute 'keys'`.")
    L.append("- the saved weights were trained under that mismatch, so even forcing the tokenizer load "
             "produced degenerate output.\n")

    Path(args.out).write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {args.out}", flush=True)

    summary = {"overall": {k: metrics[k] for k in ("bleu4", "rouge_l", "field_valid", "exact_match", "n")},
               "by_type": metrics["by_type"], "params": n_params}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
