"""
Fine-tune flan-t5-small on QG dataset v2.
Resumes from the existing checkpoint (2 epochs trained).
"""
import json
import os
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import T5ForConditionalGeneration, T5Tokenizer, get_linear_schedule_with_warmup

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "qg_model_t5")
DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "qg_dataset_raigs.json")
OUTPUT_DIR = MODEL_DIR  # overwrite in place

BATCH_SIZE = 8
LR = 5e-5
EPOCHS = 10
WARMUP_RATIO = 0.1
MAX_SRC = 64
MAX_TGT = 192
GRAD_ACCUM = 2
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class QGDataset(Dataset):
    def __init__(self, data, tokenizer, max_src, max_tgt):
        self.samples = []
        for item in data:
            src = tokenizer(
                item["input"],
                max_length=max_src,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            tgt = tokenizer(
                item["output"],
                max_length=max_tgt,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            labels = tgt["input_ids"].squeeze()
            labels[labels == tokenizer.pad_token_id] = -100
            self.samples.append({
                "input_ids": src["input_ids"].squeeze(),
                "attention_mask": src["attention_mask"].squeeze(),
                "labels": labels,
            })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


def evaluate(model, loader, tokenizer):
    model.eval()
    total_loss = 0
    count = 0
    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)
            out = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            total_loss += out.loss.item() * labels.size(0)
            count += labels.size(0)
    return total_loss / count if count else 0


def main():
    print(f"Device: {DEVICE}")

    tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR, legacy=False)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)
    model.to(DEVICE)

    with open(DATASET_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    train_ds = QGDataset(raw["train"], tokenizer, MAX_SRC, MAX_TGT)
    val_ds = QGDataset(raw["val"], tokenizer, MAX_SRC, MAX_TGT)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)

    print(f"Train: {len(train_ds)}, Val: {len(val_ds)}, Device: {DEVICE}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    total_steps = len(train_loader) * EPOCHS // GRAD_ACCUM
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)

    best_val_loss = float("inf")
    patience = 3
    patience_counter = 0

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0
        count = 0
        optimizer.zero_grad()

        for i, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)

            out = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = out.loss / GRAD_ACCUM
            loss.backward()
            total_loss += out.loss.item() * labels.size(0)
            count += labels.size(0)

            if (i + 1) % GRAD_ACCUM == 0 or i == len(train_loader) - 1:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

        train_loss = total_loss / count
        val_loss = evaluate(model, val_loader, tokenizer)
        print(f"Epoch {epoch}/{EPOCHS} — train_loss: {train_loss:.4f}  val_loss: {val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            model.save_pretrained(OUTPUT_DIR)
            tokenizer.save_pretrained(OUTPUT_DIR)
            print(f"  -> Saved (best val_loss: {val_loss:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch}")
                break

    # Save training history
    history_path = os.path.join(OUTPUT_DIR, "history.json")
    history = {}
    if os.path.exists(history_path):
        with open(history_path) as f:
            history = json.load(f)
    history.setdefault("train_loss", []).append(train_loss)
    history.setdefault("val_loss", []).append(val_loss)
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    print(f"\nDone. Best val_loss: {best_val_loss:.4f}")


if __name__ == "__main__":
    main()
