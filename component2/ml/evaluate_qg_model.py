"""
Component 2: Question Generation Model - Evaluation
Computes BLEU, ROUGE, and qualitative metrics on held-out test set.
"""

import json
import random
import sys
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
DATASET_PATH = MODELS_DIR / "qg_dataset.json"

random.seed(42)


def compute_bleu(reference: str, hypothesis: str) -> float:
    """Simple BLEU-like precision metric (1-gram precision with brevity penalty)."""
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()
    if not hyp_tokens:
        return 0.0

    # Count matches
    ref_counts = {}
    for t in ref_tokens:
        ref_counts[t] = ref_counts.get(t, 0) + 1

    match_count = 0
    for t in hyp_tokens:
        if ref_counts.get(t, 0) > 0:
            match_count += 1
            ref_counts[t] -= 1

    precision = match_count / len(hyp_tokens)

    # Brevity penalty
    bp = min(1.0, len(ref_tokens) / max(len(hyp_tokens), 1))
    return bp * precision


def compute_rouge_l(reference: str, hypothesis: str) -> float:
    """ROUGE-L: longest common subsequence based F1."""
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()

    # LCS length
    m, n = len(ref_tokens), len(hyp_tokens)
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


def evaluate_model(model, tokenizer, test_samples: List[Dict], device="cpu") -> Dict:
    """Evaluate model on a set of test samples."""
    import torch
    from tqdm import tqdm

    model.eval()
    bleu_scores = []
    rouge_scores = []
    results = []

    for sample in tqdm(test_samples, desc="Evaluating"):
        input_text = sample["input"]
        reference = sample["output"]

        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=256,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3,
            )

        hypothesis = tokenizer.decode(outputs[0], skip_special_tokens=True)

        bleu = compute_bleu(reference, hypothesis)
        rouge = compute_rouge_l(reference, hypothesis)

        bleu_scores.append(bleu)
        rouge_scores.append(rouge)

        results.append({
            "input": input_text,
            "reference": reference,
            "hypothesis": hypothesis,
            "bleu": bleu,
            "rouge_l": rouge,
        })

    return {
        "num_samples": len(test_samples),
        "average_bleu": sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0,
        "average_rouge_l": sum(rouge_scores) / len(rouge_scores) if rouge_scores else 0,
        "results": results[:5],  # Show first 5
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default=str(MODELS_DIR / "qg_model"))
    parser.add_argument("--num_samples", type=int, default=100)
    parser.add_argument("--subsample_types", nargs="+", default=["mcq", "descriptive", "coding"])
    args = parser.parse_args()

    print("=" * 60)
    print("Question Generation Model - Evaluation")
    print("=" * 60)
    print(f"  Model: {args.model_path}")
    print(f"  Samples per type: {args.num_samples}")
    print()

    # Load dataset
    with open(DATASET_PATH) as f:
        data = json.load(f)
    val_raw = data["val"]

    # Filter by type
    type_map = {"mcq": "mcq", "descriptive": "descriptive", "coding": "coding"}
    filtered = [s for s in val_raw if s.get("type") in [type_map[t] for t in args.subsample_types]]
    filtered = random.sample(filtered, min(args.num_samples, len(filtered)))
    print(f"Test samples: {len(filtered)}")
    for t in args.subsample_types:
        count = sum(1 for s in filtered if s.get("type") == type_map[t])
        print(f"  {t}: {count}")

    # Load model
    try:
        from transformers import BartForConditionalGeneration, BartTokenizerFast
        tokenizer = BartTokenizerFast.from_pretrained(args.model_path)
        model = BartForConditionalGeneration.from_pretrained(args.model_path)
        device = "cuda" if __import__("torch").cuda.is_available() else "cpu"
        model.to(device)
        print(f"Model loaded on {device} ({model.num_parameters():,} params)")
    except Exception as e:
        print(f"Error loading model from {args.model_path}: {e}")
        print("Falling back to untrained BART-base for comparison...")
        from transformers import BartForConditionalGeneration, BartTokenizerFast
        tokenizer = BartTokenizerFast.from_pretrained("facebook/bart-base")
        model = BartForConditionalGeneration.from_pretrained("facebook/bart-base")
        device = "cpu"
        model.to(device)

    # Evaluate
    print("\nEvaluating...")
    results = evaluate_model(model, tokenizer, filtered, device)

    print(f"\nResults:")
    print(f"  Samples:     {results['num_samples']}")
    print(f"  Avg BLEU:    {results['average_bleu']:.4f}")
    print(f"  Avg ROUGE-L: {results['average_rouge_l']:.4f}")

    print(f"\nSample outputs:")
    for r in results["results"]:
        print(f"\n  Input:  {r['input'][:80]}")
        print(f"  Ref:    {r['reference'][:80]}")
        print(f"  Hyp:    {r['hypothesis'][:80]}")
        print(f"  BLEU:   {r['bleu']:.3f} | ROUGE-L: {r['rouge_l']:.3f}")

    output_path = MODELS_DIR / "qg_evaluation_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
