"""
T5-based Question Generation Model for Component 2.
Fine-tunes google/t5-small on the merged QG dataset.

Artifacts -> component2/models/t5_qg/
"""
import io
import json
import os
import sys
import random
import math
from pathlib import Path
from typing import Dict, List

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    T5ForConditionalGeneration,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)

# Force UTF-8
if not getattr(sys.stdout, "encoding", None) or "utf" not in sys.stdout.encoding.lower():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
DATASET_PATH = Path(os.environ.get("QG_DATASET", str(MODELS_DIR / "qg_dataset_merged.json")))
OUTPUT_DIR = MODELS_DIR / "t5_qg"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Hyperparameters ──────────────────────────────────────────────────────────
MODEL_NAME = "google/flan-t5-small"  # 60M params, instruction-tuned, already cached
MAX_SRC_LEN = 64
MAX_TGT_LEN = 128
BATCH_SIZE = 4
LR = 3e-4
WARMUP_RATIO = 0.1
EPOCHS = 10
PATIENCE = 4
GRAD_ACCUM = 4
WEIGHT_DECAY = 0.01
SEED = 42

random.seed(SEED)
torch.manual_seed(SEED)


# ── Dataset ──────────────────────────────────────────────────────────────────
class QGDataset(Dataset):
    def __init__(self, examples: List[dict], tokenizer, max_src: int, max_tgt: int):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_src = max_src
        self.max_tgt = max_tgt

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ex = self.examples[idx]
        src = ex["input"]
        tgt = ex["output"]

        src_enc = self.tokenizer(
            src, max_length=self.max_src, padding="max_length",
            truncation=True, return_tensors="pt"
        )
        tgt_enc = self.tokenizer(
            tgt, max_length=self.max_tgt, padding="max_length",
            truncation=True, return_tensors="pt"
        )

        labels = tgt_enc["input_ids"].squeeze()
        labels[labels == self.tokenizer.pad_token_id] = -100

        return {
            "input_ids": src_enc["input_ids"].squeeze(),
            "attention_mask": src_enc["attention_mask"].squeeze(),
            "labels": labels,
        }


# ── Metrics ──────────────────────────────────────────────────────────────────
def compute_bleu_4(reference: str, hypothesis: str) -> float:
    import re
    from collections import Counter
    ref_tokens = re.findall(r"\w+", reference.lower())
    hyp_tokens = re.findall(r"\w+", hypothesis.lower())
    if not hyp_tokens or not ref_tokens:
        return 0.0
    ref_ngrams = Counter()
    hyp_ngrams = Counter()
    for n in range(1, 5):
        for i in range(len(ref_tokens) - n + 1):
            ref_ngrams[tuple(ref_tokens[i:i+n])] += 1
        for i in range(len(hyp_tokens) - n + 1):
            hyp_ngrams[tuple(hyp_tokens[i:i+n])] += 1
    clipped = sum(min(c, ref_ngrams.get(ng, 0)) for ng, c in hyp_ngrams.items())
    total = sum(hyp_ngrams.values())
    if total == 0:
        return 0.0
    precision = clipped / total
    if precision == 0:
        return 0.0
    brevity = min(1.0, math.exp(1 - len(ref_tokens) / max(len(hyp_tokens), 1)))
    return precision * brevity


def compute_rouge_l(ref: str, hyp: str) -> float:
    import re
    ref_tokens = re.findall(r"\w+", ref.lower())
    hyp_tokens = re.findall(r"\w+", hyp.lower())
    if not ref_tokens or not hyp_tokens:
        return 0.0
    lcs_len = _lcs_length(ref_tokens, hyp_tokens)
    return lcs_len / max(len(ref_tokens), 1)


def _lcs_length(a, b):
    m, n = len(a), len(b)
    if m == 0 or n == 0:
        return 0
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                curr[j] = prev[j-1] + 1
            else:
                curr[j] = max(curr[j-1], prev[j])
        prev, curr = curr, [0] * (n + 1)
    return prev[n]


# ── Training ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 60, flush=True)
    print(f"T5 Question Generation Fine-tuning", flush=True)
    print(f"Model: {MODEL_NAME} (60M params)", flush=True)
    print(f"Dataset: {DATASET_PATH}", flush=True)
    print(f"Output: {OUTPUT_DIR}", flush=True)
    print("=" * 60, flush=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Load tokenizer and model
    print(f"\n[1] Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
    model.to(device)
    print(f"   Parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Load dataset
    print(f"\n[2] Loading dataset...")
    data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    train_examples = data["train"]
    val_examples = data["val"]
    print(f"   Train: {len(train_examples)}, Val: {len(val_examples)}")

    train_ds = QGDataset(train_examples, tokenizer, MAX_SRC_LEN, MAX_TGT_LEN)
    val_ds = QGDataset(val_examples, tokenizer, MAX_SRC_LEN, MAX_TGT_LEN)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # Optimizer and scheduler
    total_steps = len(train_loader) * EPOCHS // GRAD_ACCUM
    warmup_steps = int(total_steps * WARMUP_RATIO)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)

    # Training loop
    print(f"\n[3] Training for {EPOCHS} epochs ({total_steps} steps, {warmup_steps} warmup)...")
    best_val_loss = float("inf")
    patience_counter = 0
    history = {"train_loss": [], "val_loss": [], "val_token_acc": [], "bleu1": [], "rouge_l": []}

    for epoch in range(1, EPOCHS + 1):
        # Train
        model.train()
        total_loss = 0
        optimizer.zero_grad()

        for step, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss / GRAD_ACCUM
            loss.backward()
            total_loss += outputs.loss.item()

            if (step + 1) % GRAD_ACCUM == 0 or (step + 1) == len(train_loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

        avg_train_loss = total_loss / len(train_loader)
        history["train_loss"].append(avg_train_loss)

        # Validate
        model.eval()
        val_loss = 0
        correct_tokens = 0
        total_tokens = 0
        bleu_scores = []
        rouge_scores = []

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["labels"].to(device)

                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                val_loss += outputs.loss.item()

                # Token accuracy
                preds = outputs.logits.argmax(-1)
                mask = labels != -100
                correct_tokens += (preds[mask] == labels[mask]).sum().item()
                total_tokens += mask.sum().item()

        avg_val_loss = val_loss / max(len(val_loader), 1)
        token_acc = correct_tokens / max(total_tokens, 1)
        history["val_loss"].append(avg_val_loss)
        history["val_token_acc"].append(token_acc)

        # Generation evaluation (subset) - only every 3 epochs
        if epoch % 3 == 0 or epoch == EPOCHS:
            model.eval()
            samples = random.sample(val_examples, min(20, len(val_examples)))
            for ex in samples:
                src = tokenizer(ex["input"], return_tensors="pt", max_length=MAX_SRC_LEN, truncation=True).to(device)
                out = model.generate(**src, max_length=MAX_TGT_LEN, num_beams=3, early_stopping=True)
                pred = tokenizer.decode(out[0], skip_special_tokens=True)
                ref = ex["output"]
                bleu_scores.append(compute_bleu_4(ref, pred))
                rouge_scores.append(compute_rouge_l(ref, pred))

            avg_bleu = sum(bleu_scores) / max(len(bleu_scores), 1)
            avg_rouge = sum(rouge_scores) / max(len(rouge_scores), 1)
        else:
            avg_bleu = history["bleu1"][-1] if history["bleu1"] else 0
            avg_rouge = history["rouge_l"][-1] if history["rouge_l"] else 0

        history["bleu1"].append(avg_bleu)
        history["rouge_l"].append(avg_rouge)

        marker = ""
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            model.save_pretrained(OUTPUT_DIR)
            tokenizer.save_pretrained(OUTPUT_DIR)
            marker = " <-- saved"
        else:
            patience_counter += 1

        lr_now = scheduler.get_last_lr()[0]
        print(f"Epoch {epoch:2d}/{EPOCHS} | train {avg_train_loss:.4f} | val {avg_val_loss:.4f} | "
              f"tok_acc {token_acc:.3f} | BLEU1 {avg_bleu:.3f} | ROUGE-L {avg_rouge:.3f} | "
              f"lr {lr_now:.2e}{marker}", flush=True)

        if patience_counter >= PATIENCE:
            print(f"\nEarly stopping at epoch {epoch} (patience={PATIENCE})")
            break

    # Save history
    history_path = OUTPUT_DIR / "history.json"
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")

    # Sample generations
    print(f"\n[4] Sample generations:")
    model.eval()
    for ex in random.sample(val_examples, min(5, len(val_examples))):
        src = tokenizer(ex["input"], return_tensors="pt", max_length=MAX_SRC_LEN, truncation=True).to(device)
        out = model.generate(**src, max_length=MAX_TGT_LEN, num_beams=3, early_stopping=True)
        pred = tokenizer.decode(out[0], skip_special_tokens=True)
        print(f"  IN:  {ex['input']}")
        print(f"  OUT: {pred[:200]}")
        print()

    # Save config
    config = {
        "model_name": MODEL_NAME,
        "max_src_len": MAX_SRC_LEN,
        "max_tgt_len": MAX_TGT_LEN,
        "epochs": EPOCHS,
        "best_val_loss": best_val_loss,
        "final_bleu1": history["bleu1"][-1],
        "final_rouge_l": history["rouge_l"][-1],
        "final_token_acc": history["val_token_acc"][-1],
    }
    (OUTPUT_DIR / "training_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Training complete!")
    print(f"Best val loss: {best_val_loss:.4f}")
    print(f"Final BLEU-1: {history['bleu1'][-1]:.4f}")
    print(f"Final ROUGE-L: {history['rouge_l'][-1]:.4f}")
    print(f"Final token acc: {history['val_token_acc'][-1]:.4f}")
    print(f"Saved to: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
