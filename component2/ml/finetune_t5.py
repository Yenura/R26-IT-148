"""
Fine-tune T5 (flan-t5-small) on the canonical QG dataset v2
-----------------------------------------------------------
Seq2Seq fine-tuning of the cached google/flan-t5-small on
qg_dataset_v2.json. Input  = canonical `[TYPE] role | topic | difficulty`
target = canonical `Q: ...` output with type-specific fields.

CPU-only, RAM-constrained machine (7.6 GB):
  - batch 16, threads 4  (~8.7 s/step -> ~45 min/epoch)
  - max_src 64, max_tgt 128

Artifacts -> models/qg_model_t5/
Usage:
  python finetune_t5.py [--epochs 2] [--batch_size 16] [--threads 4]
                        [--max_train N] [--resume]
"""

import io
import json
import math
import random
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, get_linear_schedule_with_warmup

if not getattr(sys.stdout, "encoding", None) or "utf" not in sys.stdout.encoding.lower():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
DATASET_PATH = MODELS_DIR / "qg_dataset_v2.json"
SAVE_DIR = MODELS_DIR / "qg_model_t5"

MODEL_NAME = "google/flan-t5-small"
MAX_SRC = 64
MAX_TGT = 128
LR = 1e-4
WARMUP_STEPS = 200
GRAD_CLIP = 1.0
SEED = 42


class Seq2SeqDS(Dataset):
    def __init__(self, examples):
        self.examples = examples

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ex = self.examples[idx]
        return ex["input"], ex["output"]


def collate(batch, tokenizer):
    src, tgt = zip(*batch)
    enc = tokenizer(list(src), return_tensors="pt", padding=True,
                    truncation=True, max_length=MAX_SRC)
    dec = tokenizer(list(tgt), return_tensors="pt", padding=True,
                    truncation=True, max_length=MAX_TGT)
    return enc, dec


def main():
    random.seed(SEED)
    torch.manual_seed(SEED)

    args = dict([(a.split("=")[0], a.split("=")[1])
                 for a in sys.argv[1:] if "=" in a])
    epochs = int(args.get("--epochs", "2"))
    batch_size = int(args.get("--batch_size", "16"))
    threads = int(args.get("--threads", "4"))
    max_train = int(args.get("--max_train", "0")) or None

    torch.set_num_threads(threads)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"Fine-tuning {MODEL_NAME} on canonical QG dataset")
    print(f"threads={threads} batch={batch_size} epochs={epochs}")
    print("=" * 60)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    print(f"Params: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M")

    with open(DATASET_PATH, encoding="utf-8") as f:
        data = json.load(f)
    train_raw = data["train"]
    val_raw = data["val"]
    if max_train and max_train < len(train_raw):
        random.seed(SEED)
        train_raw = random.sample(train_raw, max_train)
    print(f"Train: {len(train_raw)} | Val: {len(val_raw)}")

    train_ds = Seq2SeqDS(train_raw)
    val_ds = Seq2SeqDS(val_raw)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              collate_fn=lambda b: collate(b, tokenizer),
                              num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size * 2, shuffle=False,
                            collate_fn=lambda b: collate(b, tokenizer),
                            num_workers=0)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    total_steps = epochs * len(train_loader)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=min(WARMUP_STEPS, total_steps // 10),
        num_training_steps=total_steps)

    best_val = float("inf")
    start_epoch = 0
    history = {"train_loss": [], "val_loss": []}

    if "--resume" in sys.argv and (SAVE_DIR / "history.json").exists():
        with open(SAVE_DIR / "history.json", encoding="utf-8") as f:
            history = json.load(f)
        start_epoch = len(history["val_loss"])
        best_val = min(history["val_loss"]) if history["val_loss"] else float("inf")
        model = AutoModelForSeq2SeqLM.from_pretrained(str(SAVE_DIR))
        print(f"[RESUME] from epoch {start_epoch} (best val {best_val:.4f})")

    for epoch in range(start_epoch, epochs):
        model.train()
        total_loss = 0.0
        t0 = time.time()
        for step, (enc, dec) in enumerate(train_loader):
            dec_input = dec["input_ids"][:, :-1]
            labels = dec["input_ids"][:, 1:].masked_fill(
                dec["attention_mask"][:, 1:] == 0, -100)

            optimizer.zero_grad()
            out = model(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"],
                        decoder_input_ids=dec_input, labels=labels)
            out.loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
            optimizer.step()
            scheduler.step()

            total_loss += out.loss.item()
            if (step + 1) % 100 == 0:
                el = time.time() - t0
                print(f"  epoch {epoch+1} step {step+1}/{len(train_loader)} "
                      f"loss {out.loss.item():.4f} ({el:.0f}s)")

        train_loss = total_loss / max(len(train_loader), 1)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for enc, dec in val_loader:
                dec_input = dec["input_ids"][:, :-1]
                labels = dec["input_ids"][:, 1:].masked_fill(
                    dec["attention_mask"][:, 1:] == 0, -100)
                out = model(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"],
                            decoder_input_ids=dec_input, labels=labels)
                val_loss += out.loss.item()
        val_loss /= max(len(val_loader), 1)

        history["train_loss"].append(round(train_loss, 4))
        history["val_loss"].append(round(val_loss, 4))
        with open(SAVE_DIR / "history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        marker = ""
        if val_loss < best_val:
            best_val = val_loss
            model.save_pretrained(str(SAVE_DIR))
            tokenizer.save_pretrained(str(SAVE_DIR))
            with open(SAVE_DIR / "train_config.json", "w", encoding="utf-8") as f:
                json.dump({"model": MODEL_NAME, "epochs": epochs,
                           "batch_size": batch_size, "lr": LR,
                           "max_src": MAX_SRC, "max_tgt": MAX_TGT,
                           "dataset": str(DATASET_PATH)}, f, indent=2)
            marker = " <-- saved"

        print(f"Epoch {epoch+1}/{epochs} | train {train_loss:.4f} | val {val_loss:.4f} "
              f"| lr {optimizer.param_groups[0]['lr']:.2e}{marker}")

    print(f"\nBest val loss: {best_val:.4f} -> {SAVE_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
