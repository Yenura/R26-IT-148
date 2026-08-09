"""
Evaluate QG Model v2 (canonical dataset)
----------------------------------------
Loads the trained v2 model and reports real generation metrics on the val set:
  - BLEU-1..4 (n-gram precision with brevity penalty) + smoothed BLEU-4
  - ROUGE-L (LCS F1)
  - Format-validity rate per question type (MCQ / Descriptive / Coding)
  - Greedy vs beam search (width 3)

Usage:
  python evaluate_qg_model_v2.py [--num_samples 556] [--beam_samples 150]

Output: models/qg_evaluation_results_v2.json
"""

import io
import json
import random
import sys
from pathlib import Path

import torch

if not getattr(sys.stdout, "encoding", None) or "utf" not in sys.stdout.encoding.lower():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import train_qg_model_v2 as t  # noqa: E402

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
MODEL_DIR = MODELS_DIR / "qg_model_v2"
DATASET_PATH = MODELS_DIR / "qg_dataset_v2.json"

V1_BASELINE = {"bleu_4": 0.076, "rouge_l": 0.174, "bleu_1": None}
SEED = 42


def _avg(seq):
    return sum(seq) / max(len(seq), 1)


def _gen(model, tokenizer, src_text, decode_fn, **kw):
    src = torch.tensor([tokenizer.encode(src_text, add_special=True)], dtype=torch.long)
    ids = decode_fn(model, src, tokenizer, **kw)
    return tokenizer.decode(ids)


def evaluate(num_samples: int, beam_samples: int):
    model, tokenizer = t.load_trained_model(str(MODEL_DIR), device="cpu")
    torch.set_num_threads(6)
    model.eval()

    with open(DATASET_PATH, encoding="utf-8") as f:
        data = json.load(f)
    val = data["val"]
    print(f"Val set: {len(val)} | evaluating on {min(num_samples, len(val))}")

    random.seed(SEED)
    if num_samples < len(val):
        val = random.sample(val, num_samples)

    results = {"per_type": {}, "overall": {}}
    per_type = {}

    for ex in val:
        etype = ex["type"]
        if etype not in per_type:
            per_type[etype] = []
        per_type[etype].append(ex)

    for etype, examples in per_type.items():
        greedy_bleus = {"bleu_1": [], "bleu_2": [], "bleu_3": [], "bleu_4": []}
        greedy_bleu4_sm = []
        greedy_rouge = []
        greedy_fmt = []

        beam_bleus = {"bleu_1": [], "bleu_2": [], "bleu_3": [], "bleu_4": []}
        beam_bleu4_sm = []
        beam_rouge = []
        beam_fmt = []

        beam_pool = examples if len(examples) <= beam_samples else random.sample(examples, beam_samples)
        beam_examples = {id(ex) for ex in beam_pool}

        for ex in examples:
            max_len = min(t.TGT_MAX_LEN, len(ex["output"].split()) + 40)
            ref = ex["output"]

            g = _gen(model, tokenizer, ex["input"], t.greedy_search, max_len=max_len)
            bs = _gen(model, tokenizer, ex["input"], t.beam_search,
                      beam_width=3, max_len=max_len) if id(ex) in beam_examples else None

            bleus = t.compute_bleu(ref, g)
            for k in greedy_bleus:
                greedy_bleus[k].append(bleus[k])
            greedy_bleu4_sm.append(t.compute_bleu4_smoothed(ref, g))
            greedy_rouge.append(t.compute_rouge_l(ref, g))
            greedy_fmt.append(1.0 if t._format_valid(etype, g) else 0.0)

            if bs is not None:
                bbleus = t.compute_bleu(ref, bs)
                for k in beam_bleus:
                    beam_bleus[k].append(bbleus[k])
                beam_bleu4_sm.append(t.compute_bleu4_smoothed(ref, bs))
                beam_rouge.append(t.compute_rouge_l(ref, bs))
                beam_fmt.append(1.0 if t._format_valid(etype, bs) else 0.0)

        results["per_type"][etype] = {
            "n": len(examples),
            "greedy": {
                "bleu": {k: round(_avg(v), 4) for k, v in greedy_bleus.items()},
                "bleu4_smoothed": round(_avg(greedy_bleu4_sm), 4),
                "rouge_l": round(_avg(greedy_rouge), 4),
                "format_valid_rate": round(_avg(greedy_fmt), 4),
            },
            "beam": {
                "n": len(beam_pool),
                "bleu": {k: round(_avg(v), 4) for k, v in beam_bleus.items()},
                "bleu4_smoothed": round(_avg(beam_bleu4_sm), 4),
                "rouge_l": round(_avg(beam_rouge), 4),
                "format_valid_rate": round(_avg(beam_fmt), 4),
            },
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

    # Overall: aggregate per-sample (weighted by type count)
    agg = {"greedy": {"bleu": {k: [] for k in ("bleu_1", "bleu_2", "bleu_3", "bleu_4")},
                      "bleu4_smoothed": [], "rouge_l": [], "format_valid_rate": []},
           "beam": {"bleu": {k: [] for k in ("bleu_1", "bleu_2", "bleu_3", "bleu_4")},
                    "bleu4_smoothed": [], "rouge_l": [], "format_valid_rate": []}}
    for ex in val:
        etype = ex["type"]
        max_len = min(t.TGT_MAX_LEN, len(ex["output"].split()) + 40)
        ref = ex["output"]
        g = _gen(model, tokenizer, ex["input"], t.greedy_search, max_len=max_len)
        b = _gen(model, tokenizer, ex["input"], t.beam_search, beam_width=3, max_len=max_len)

        for k in agg["greedy"]["bleu"]:
            agg["greedy"]["bleu"][k].append(t.compute_bleu(ref, g)[k])
            agg["beam"]["bleu"][k].append(t.compute_bleu(ref, b)[k])
        agg["greedy"]["bleu4_smoothed"].append(t.compute_bleu4_smoothed(ref, g))
        agg["beam"]["bleu4_smoothed"].append(t.compute_bleu4_smoothed(ref, b))
        agg["greedy"]["rouge_l"].append(t.compute_rouge_l(ref, g))
        agg["beam"]["rouge_l"].append(t.compute_rouge_l(ref, b))
        agg["greedy"]["format_valid_rate"].append(1.0 if t._format_valid(etype, g) else 0.0)
        agg["beam"]["format_valid_rate"].append(1.0 if t._format_valid(etype, b) else 0.0)

    results["overall"] = {
        "n": len(val),
        "greedy": {"bleu": {k: round(_avg(v), 4) for k, v in agg["greedy"]["bleu"].items()},
                   "bleu4_smoothed": round(_avg(agg["greedy"]["bleu4_smoothed"]), 4),
                   "rouge_l": round(_avg(agg["greedy"]["rouge_l"]), 4),
                   "format_valid_rate": round(_avg(agg["greedy"]["format_valid_rate"]), 4)},
        "beam": {"bleu": {k: round(_avg(v), 4) for k, v in agg["beam"]["bleu"].items()},
                 "bleu4_smoothed": round(_avg(agg["beam"]["bleu4_smoothed"]), 4),
                 "rouge_l": round(_avg(agg["beam"]["rouge_l"]), 4),
                 "format_valid_rate": round(_avg(agg["beam"]["format_valid_rate"]), 4)},
    }
    print("\n===== OVERALL =====")
    print(f"greedy: {results['overall']['greedy']}")
    print(f"beam:   {results['overall']['beam']}")

    # Sample generations (one per type, greedy)
    samples = []
    for etype in ("mcq", "descriptive", "coding"):
        pool = [e for e in val if e["type"] == etype]
        if not pool:
            continue
        ex = pool[0]
        max_len = min(t.TGT_MAX_LEN, len(ex["output"].split()) + 40)
        g = _gen(model, tokenizer, ex["input"], t.greedy_search, max_len=max_len)
        b = _gen(model, tokenizer, ex["input"], t.beam_search, beam_width=3, max_len=max_len)
        samples.append({"type": etype, "input": ex["input"], "reference": ex["output"],
                        "greedy": g, "beam": b})
        print(f"\n[{etype}] input: {ex['input']}")
        print(f"  ref:    {ex['output'][:160]}")
        print(f"  greedy: {g[:160]}")
        print(f"  beam:   {b[:160]}")

    results["model"] = {
        "params": 6195776,
        "architecture": t.MODEL_CFG,
        "training": {
            "epochs": 20,
            "dataset": "qg_dataset_v2.json (canonical, 5552 examples)",
            "best_val_loss": 3.5171,
        },
    }
    results["baseline_v1"] = V1_BASELINE
    results["sample_generations"] = samples

    out = MODELS_DIR / "qg_evaluation_results_v2.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Saved -> {out}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a.startswith("--num_samples=")]
    bargs = [a for a in sys.argv[1:] if a.startswith("--beam_samples=")]
    ns = int(args[0].split("=")[1]) if args else 556
    bs = int(bargs[0].split("=")[1]) if bargs else 150
    evaluate(num_samples=ns, beam_samples=bs)
