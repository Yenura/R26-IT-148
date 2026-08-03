"""Evaluate TinyQGModel on held-out validation set."""
import json
import random
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

sys.path.insert(0, "ml")
from train_qg_model import TinyQGModel, CharTokenizer, QGDataset, collate_fn

random.seed(42)

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
DATASET_PATH = MODELS_DIR / "qg_dataset.json"
MODEL_DIR = MODELS_DIR / "qg_model"


def compute_bleu(reference: str, hypothesis: str) -> float:
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()
    if not hyp_tokens or not ref_tokens:
        return 0.0
    ref_counts = {}
    for t in ref_tokens:
        ref_counts[t] = ref_counts.get(t, 0) + 1
    match_count = 0
    for t in hyp_tokens:
        if ref_counts.get(t, 0) > 0:
            match_count += 1
            ref_counts[t] -= 1
    precision = match_count / len(hyp_tokens)
    bp = min(1.0, len(ref_tokens) / max(len(hyp_tokens), 1))
    return bp * precision


def compute_rouge_l(reference: str, hypothesis: str) -> float:
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()
    m, n = len(ref_tokens), len(hyp_tokens)
    if m == 0 or n == 0:
        return 0.0
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs = dp[m][n]
    precision = lcs / max(len(hyp_tokens), 1)
    recall = lcs / max(len(ref_tokens), 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-8)
    return f1


def main():
    print("=" * 60)
    print("TinyQGModel - Evaluation")
    print("=" * 60)

    # Load model
    tokenizer = CharTokenizer.load(str(MODEL_DIR / "tokenizer.json"))
    model = TinyQGModel(vocab_size=tokenizer.vocab_size())
    model.load_state_dict(torch.load(str(MODEL_DIR / "model.pt"), map_location="cpu"))
    model.eval()
    print(f"Model: {sum(p.numel() for p in model.parameters()):,} params")
    print(f"Vocab: {tokenizer.vocab_size()}")

    # Load validation dataset
    with open(DATASET_PATH) as f:
        data = json.load(f)

    val_raw = data["val"]
    val_raw_balanced = (
        [s for s in val_raw if s.get("type") == "mcq"][:50]
        + [s for s in val_raw if s.get("type") == "descriptive"][:100]
        + [s for s in val_raw if s.get("type") == "coding"][:50]
    )
    random.shuffle(val_raw_balanced)
    print(f"Test samples: {len(val_raw_balanced)}")
    for t in ["mcq", "descriptive", "coding"]:
        count = sum(1 for s in val_raw_balanced if s.get("type") == t)
        print(f"  {t}: {count}")

    # Evaluate
    bleu_scores = []
    rouge_scores = []
    results = []

    for i, sample in enumerate(val_raw_balanced):
        input_text = sample["input"]
        reference = sample["output"]

        src = tokenizer.encode(input_text, add_special=True)
        src_tensor = torch.tensor([src], dtype=torch.long)

        with torch.no_grad():
            output_ids = model.generate(src_tensor, tokenizer, max_len=64, temperature=0.8)

        hypothesis = tokenizer.decode(output_ids[0].tolist())

        bleu = compute_bleu(reference, hypothesis)
        rouge = compute_rouge_l(reference, hypothesis)
        bleu_scores.append(bleu)
        rouge_scores.append(rouge)

        results.append({
            "type": sample.get("type"),
            "input": input_text[:80],
            "reference": reference[:120],
            "hypothesis": hypothesis[:120],
            "bleu": bleu,
            "rouge_l": rouge,
        })

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(val_raw_balanced)}] processed...")

    avg_bleu = sum(bleu_scores) / len(bleu_scores)
    avg_rouge = sum(rouge_scores) / len(rouge_scores)

    print(f"\nResults:")
    print(f"  Samples:      {len(results)}")
    print(f"  Avg BLEU:     {avg_bleu:.4f}")
    print(f"  Avg ROUGE-L:  {avg_rouge:.4f}")

    print(f"\nSample outputs:")
    for r in results[:5]:
        print(f"\n  Type:   {r['type']}")
        print(f"  Ref:    {r['reference'][:80]}")
        print(f"  Hyp:    {r['hypothesis'][:80]}")
        print(f"  BLEU:   {r['bleu']:.3f} | ROUGE-L: {r['rouge_l']:.3f}")

    # Save
    output_path = MODELS_DIR / "qg_evaluation_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "num_samples": len(results),
            "average_bleu": avg_bleu,
            "average_rouge_l": avg_rouge,
            "results": results[:10],
        }, f, indent=2)
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
