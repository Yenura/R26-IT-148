"""
Evaluate fine-tuned T5 (models/qg_model_t5) on the canonical val set
--------------------------------------------------------------------
Same metrics as evaluate_qg_model_v2.py: BLEU-1..4 (+smoothed BLEU-4),
ROUGE-L, format-validity rate, greedy vs beam(3).

Usage:
  python evaluate_t5.py [--num_samples 556] [--beam_samples 150]

Output: models/qg_evaluation_results_t5.json
"""

import io
import json
import random
import sys
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

if not getattr(sys.stdout, "encoding", None) or "utf" not in sys.stdout.encoding.lower():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import train_qg_model_v2 as t  # noqa: E402

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
MODEL_DIR = MODELS_DIR / "qg_model_t5"
DATASET_PATH = MODELS_DIR / "qg_dataset_v2.json"
SEED = 42
MAX_NEW = 128


def _gen(model, tokenizer, src_text, greedy=True):
    enc = tokenizer(src_text, return_tensors="pt", truncation=True, max_length=64)
    with torch.no_grad():
        if greedy:
            out = model.generate(**enc, max_new_tokens=MAX_NEW, num_beams=1,
                                 early_stopping=True)
        else:
            out = model.generate(**enc, max_new_tokens=MAX_NEW, num_beams=3,
                                 early_stopping=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)


def _avg(seq):
    return sum(seq) / max(len(seq), 1)


def main():
    torch.set_num_threads(6)
    args = dict([(a.split("=")[0], a.split("=")[1])
                 for a in sys.argv[1:] if "=" in a])
    num_samples = int(args.get("--num_samples", "556"))
    beam_samples = int(args.get("--beam_samples", "150"))

    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
    model = AutoModelForSeq2SeqLM.from_pretrained(str(MODEL_DIR))
    model.eval()
    print(f"Loaded T5 from {MODEL_DIR}")

    with open(DATASET_PATH, encoding="utf-8") as f:
        data = json.load(f)
    val = data["val"]
    random.seed(SEED)
    if num_samples < len(val):
        val = random.sample(val, num_samples)
    print(f"Val set: {len(data['val'])} | evaluating on {len(val)}")

    results = {"per_type": {}, "overall": {}}
    per_type = {}
    for ex in val:
        per_type.setdefault(ex["type"], []).append(ex)

    for etype, examples in per_type.items():
        g_bleus = {f"bleu_{n}": [] for n in range(1, 5)}
        b_bleus = {f"bleu_{n}": [] for n in range(1, 5)}
        g_sm, b_sm = [], []
        g_r, b_r = [], []
        g_f, b_f = [], []
        beam_pool = examples if len(examples) <= beam_samples else random.sample(examples, beam_samples)
        beam_ids = {id(ex) for ex in beam_pool}

        for ex in examples:
            ref = ex["output"]
            g = _gen(model, tokenizer, ex["input"], greedy=True)
            bs = _gen(model, tokenizer, ex["input"], greedy=False) if id(ex) in beam_ids else None

            for n in range(1, 5):
                g_bleus[f"bleu_{n}"].append(t.compute_bleu(ref, g)[f"bleu_{n}"])
                if bs is not None:
                    b_bleus[f"bleu_{n}"].append(t.compute_bleu(ref, bs)[f"bleu_{n}"])
            g_sm.append(t.compute_bleu4_smoothed(ref, g))
            g_r.append(t.compute_rouge_l(ref, g))
            g_f.append(1.0 if t._format_valid(etype, g) else 0.0)
            if bs is not None:
                b_sm.append(t.compute_bleu4_smoothed(ref, bs))
                b_r.append(t.compute_rouge_l(ref, bs))
                b_f.append(1.0 if t._format_valid(etype, bs) else 0.0)

        results["per_type"][etype] = {
            "n": len(examples),
            "greedy": {"bleu": {k: round(_avg(v), 4) for k, v in g_bleus.items()},
                       "bleu4_smoothed": round(_avg(g_sm), 4),
                       "rouge_l": round(_avg(g_r), 4),
                       "format_valid_rate": round(_avg(g_f), 4)},
            "beam": {"n": len(beam_pool),
                     "bleu": {k: round(_avg(v), 4) for k, v in b_bleus.items()},
                     "bleu4_smoothed": round(_avg(b_sm), 4),
                     "rouge_l": round(_avg(b_r), 4),
                     "format_valid_rate": round(_avg(b_f), 4)},
        }
        print(f"\n[{etype}] n={len(examples)}")
        print(f"  greedy: BLEU {results['per_type'][etype]['greedy']['bleu']} "
              f"sm4 {results['per_type'][etype]['greedy']['bleu4_smoothed']} "
              f"ROUGE-L {results['per_type'][etype]['greedy']['rouge_l']} "
              f"format {results['per_type'][etype]['greedy']['format_valid_rate']:.2f}")
        print(f"  beam:   BLEU {results['per_type'][etype]['beam']['bleu']} "
              f"sm4 {results['per_type'][etype]['beam']['bleu4_smoothed']} "
              f"ROUGE-L {results['per_type'][etype]['beam']['rouge_l']} "
              f"format {results['per_type'][etype]['beam']['format_valid_rate']:.2f}")

    agg = {"greedy": {"bleu": {k: [] for k in ("bleu_1", "bleu_2", "bleu_3", "bleu_4")},
                      "sm": [], "r": [], "f": []},
           "beam": {"bleu": {k: [] for k in ("bleu_1", "bleu_2", "bleu_3", "bleu_4")},
                    "sm": [], "r": [], "f": []}}
    for ex in val:
        ref = ex["output"]
        etype = ex["type"]
        g = _gen(model, tokenizer, ex["input"], greedy=True)
        b = _gen(model, tokenizer, ex["input"], greedy=False)
        for k in agg["greedy"]["bleu"]:
            agg["greedy"]["bleu"][k].append(t.compute_bleu(ref, g)[k])
            agg["beam"]["bleu"][k].append(t.compute_bleu(ref, b)[k])
        agg["greedy"]["sm"].append(t.compute_bleu4_smoothed(ref, g))
        agg["beam"]["sm"].append(t.compute_bleu4_smoothed(ref, b))
        agg["greedy"]["r"].append(t.compute_rouge_l(ref, g))
        agg["beam"]["r"].append(t.compute_rouge_l(ref, b))
        agg["greedy"]["f"].append(1.0 if t._format_valid(etype, g) else 0.0)
        agg["beam"]["f"].append(1.0 if t._format_valid(etype, b) else 0.0)

    results["overall"] = {
        "n": len(val),
        "greedy": {"bleu": {k: round(_avg(v), 4) for k, v in agg["greedy"]["bleu"].items()},
                   "bleu4_smoothed": round(_avg(agg["greedy"]["sm"]), 4),
                   "rouge_l": round(_avg(agg["greedy"]["r"]), 4),
                   "format_valid_rate": round(_avg(agg["greedy"]["f"]), 4)},
        "beam": {"bleu": {k: round(_avg(v), 4) for k, v in agg["beam"]["bleu"].items()},
                 "bleu4_smoothed": round(_avg(agg["beam"]["sm"]), 4),
                 "rouge_l": round(_avg(agg["beam"]["r"]), 4),
                 "format_valid_rate": round(_avg(agg["beam"]["f"]), 4)},
    }
    print("\n===== OVERALL =====")
    print(f"greedy: {results['overall']['greedy']}")
    print(f"beam:   {results['overall']['beam']}")

    samples = []
    for etype in ("mcq", "descriptive", "coding"):
        pool = [e for e in data["val"] if e["type"] == etype]
        if not pool:
            continue
        ex = pool[0]
        g = _gen(model, tokenizer, ex["input"], greedy=True)
        b = _gen(model, tokenizer, ex["input"], greedy=False)
        samples.append({"type": etype, "input": ex["input"], "reference": ex["output"],
                        "greedy": g, "beam": b})
        print(f"\n[{etype}] input: {ex['input']}")
        print(f"  ref:    {ex['output'][:160]}")
        print(f"  greedy: {g[:160]}")
        print(f"  beam:   {b[:160]}")

    results["model"] = {"name": "google/flan-t5-small (fine-tuned)",
                        "training": {"epochs": 2, "dataset": "qg_dataset_v2.json",
                                     "best_val_loss": 1.2837}}
    results["sample_generations"] = samples

    out = MODELS_DIR / "qg_evaluation_results_t5.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Saved -> {out}")


if __name__ == "__main__":
    main()
