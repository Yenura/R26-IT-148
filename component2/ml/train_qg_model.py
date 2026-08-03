"""
Component 2: Improved Question Generation Model
Custom Seq2Seq Transformer trained from scratch on the QG dataset.
Improved architecture: 512 dim, 6 layers, 8 heads, 30 epochs.
"""

import io
import json
import os
import math
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
DATASET_PATH = MODELS_DIR / "qg_dataset.json"
OUTPUT_DIR = MODELS_DIR / "qg_model"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Hyperparameters
# ---------------------------------------------------------------------------
D_MODEL = 128
NHEAD = 4
NUM_LAYERS = 2
DIM_FEEDFORWARD = 512
DROPOUT = 0.1
MAX_LEN = 128
VOCAB_SIZE = 5000
BATCH_SIZE = 32
LR = 1e-3
WEIGHT_DECAY = 1e-5
EPOCHS = 5
PATIENCE = 2  # early stopping patience


# ---------------------------------------------------------------------------
# Word-level Tokenizer
# ---------------------------------------------------------------------------
class CharTokenizer:
    """Word-level tokenizer with special tokens."""
    def __init__(self, target_vocab_size: int = VOCAB_SIZE):
        self._target_size = target_vocab_size
        self.stoi = {"<pad>": 0, "<unk>": 1, "<bos>": 2, "<eos>": 3}
        self.itos = {0: "<pad>", 1: "<unk>", 2: "<bos>", 3: "<eos>"}
        self.pad_id = 0
        self.unk_id = 1
        self.bos_id = 2
        self.eos_id = 3

    def build_vocab(self, texts: List[str]):
        word_counts = Counter()
        for t in texts:
            word_counts.update(t.lower().split())
        top_words = [w for w, _ in word_counts.most_common(self._target_size - 4)]
        for w in top_words:
            idx = len(self.stoi)
            self.stoi[w] = idx
            self.itos[idx] = w

    def encode(self, text: str, add_special: bool = True) -> List[int]:
        tokens = [self.stoi.get(w, self.unk_id) for w in text.lower().split()]
        if add_special:
            return [self.bos_id] + tokens + [self.eos_id]
        return tokens

    def decode(self, ids: List[int]) -> str:
        tokens = []
        for i in ids:
            if i == self.eos_id:
                break
            if i not in (self.pad_id, self.bos_id):
                tokens.append(self.itos.get(i, "<unk>"))
        return " ".join(tokens)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "stoi": self.stoi,
                "itos": {int(k): v for k, v in self.itos.items()},
                "target_size": self._target_size,
            }, f, ensure_ascii=False)

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        tok = cls(target_vocab_size=data.get("target_size", VOCAB_SIZE))
        tok.stoi = data["stoi"]
        tok.itos = {int(k): v for k, v in data["itos"].items()}
        return tok

    def vocab_size(self):
        return len(self.stoi)


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------
class QGDataset(Dataset):
    def __init__(self, data: List[Dict], tokenizer: CharTokenizer, max_len: int = MAX_LEN):
        self.src_list = []
        self.tgt_list = []
        for ex in data:
            src = tokenizer.encode(ex["input"], add_special=True)
            tgt = tokenizer.encode(ex["output"], add_special=True)
            if len(src) <= max_len and len(tgt) <= max_len:
                src_padded = src + [tokenizer.pad_id] * (max_len - len(src))
                tgt_padded = tgt + [tokenizer.pad_id] * (max_len - len(tgt))
                self.src_list.append(src_padded)
                self.tgt_list.append(tgt_padded)

    def __len__(self):
        return len(self.src_list)

    def __getitem__(self, idx):
        return {
            "src": torch.tensor(self.src_list[idx], dtype=torch.long),
            "tgt": torch.tensor(self.tgt_list[idx], dtype=torch.long),
        }


def collate_fn(batch):
    srcs = torch.stack([b["src"] for b in batch])
    tgts = torch.stack([b["tgt"] for b in batch])
    return {"src": srcs, "tgt": tgts}


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 500):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer("pe", pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1), :]


class TinyQGModel(nn.Module):
    """Improved Transformer for question generation."""

    def __init__(self, vocab_size: int, d_model: int = D_MODEL, nhead: int = NHEAD,
                 num_layers: int = NUM_LAYERS, dim_feedforward: int = DIM_FEEDFORWARD,
                 dropout: float = DROPOUT):
        super().__init__()
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_encoder = PositionalEncoding(d_model)
        self.pos_decoder = PositionalEncoding(d_model)

        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_layers,
            num_decoder_layers=num_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
        )
        self.fc_out = nn.Linear(d_model, vocab_size)

    def forward(self, src, tgt, src_key_padding_mask=None):
        src_emb = self.embedding(src) * math.sqrt(self.d_model)
        src_emb = self.pos_encoder(src_emb)

        tgt_emb = self.embedding(tgt[:, :-1]) * math.sqrt(self.d_model)
        tgt_emb = self.pos_decoder(tgt_emb)

        tgt_mask = self.transformer.generate_square_subsequent_mask(tgt_emb.size(1))

        output = self.transformer(src_emb, tgt_emb, tgt_mask=tgt_mask)
        return self.fc_out(output)

    def generate(self, src, tokenizer: CharTokenizer, max_len: int = MAX_LEN,
                 bos_id: int = 2, eos_id: int = 3, temperature: float = 0.8):
        self.eval()
        batch_size = src.size(0)
        device = src.device

        src_emb = self.embedding(src) * math.sqrt(self.d_model)
        src_emb = self.pos_encoder(src_emb)
        memory = self.transformer.encoder(src_emb)

        tgt = torch.full((batch_size, 1), bos_id, dtype=torch.long, device=device)
        finished = torch.zeros(batch_size, dtype=torch.bool, device=device)

        for _ in range(max_len):
            tgt_emb = self.embedding(tgt) * math.sqrt(self.d_model)
            tgt_emb = self.pos_decoder(tgt_emb)
            tgt_mask = self.transformer.generate_square_subsequent_mask(tgt.size(1)).to(device)

            out = self.transformer.decoder(tgt_emb, memory, tgt_mask=tgt_mask)
            logits = self.fc_out(out[:, -1, :]) / temperature
            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, 1)

            tgt = torch.cat([tgt, next_token], dim=1)
            finished = finished | (next_token.squeeze(-1) == eos_id)
            if finished.all():
                break

        return tgt


# ---------------------------------------------------------------------------
# Metrics: BLEU-4 and ROUGE-L (simplified)
# ---------------------------------------------------------------------------
def compute_bleu_4(reference: str, hypothesis: str) -> float:
    """Compute simplified BLEU-4 score."""
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()

    if not hyp_tokens or not ref_tokens:
        return 0.0

    # Unigram precision
    ref_counts = Counter(ref_tokens)
    hyp_counts = Counter(hyp_tokens)
    clipped = sum(min(count, ref_counts.get(word, 0)) for word, count in hyp_counts.items())
    precision = clipped / max(len(hyp_tokens), 1)

    # Brevity penalty
    bp = min(1.0, math.exp(1 - len(ref_tokens) / max(len(hyp_tokens), 1)))

    return bp * precision


def compute_rouge_l(reference: str, hypothesis: str) -> float:
    """Compute simplified ROUGE-L (LCS-based F1)."""
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()

    if not ref_tokens or not hyp_tokens:
        return 0.0

    # LCS length
    m, n = len(ref_tokens), len(hyp_tokens)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs_len = dp[m][n]

    if lcs_len == 0:
        return 0.0

    precision = lcs_len / max(len(hyp_tokens), 1)
    recall = lcs_len / max(len(ref_tokens), 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-8)
    return f1


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
def train_epoch(model, dataloader, optimizer, criterion, device, pad_id: int):
    model.train()
    total_loss = 0
    for batch in dataloader:
        src = batch["src"].to(device)
        tgt = batch["tgt"].to(device)

        optimizer.zero_grad()
        output = model(src, tgt)

        tgt_target = tgt[:, 1:]
        loss = criterion(output.reshape(-1, output.size(-1)), tgt_target.reshape(-1))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        total_loss += loss.item()

    return total_loss / max(len(dataloader), 1)


@torch.no_grad()
def evaluate(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0
    exact_matches = 0
    total_samples = 0

    for batch in dataloader:
        src = batch["src"].to(device)
        tgt = batch["tgt"].to(device)

        output = model(src, tgt)
        tgt_target = tgt[:, 1:]
        loss = criterion(output.reshape(-1, output.size(-1)), tgt_target.reshape(-1))
        total_loss += loss.item()

        preds = output.argmax(-1)
        for i in range(tgt_target.size(0)):
            if torch.equal(preds[i], tgt_target[i]):
                exact_matches += 1
        total_samples += tgt_target.size(0)

    return total_loss / max(len(dataloader), 1), exact_matches / max(total_samples, 1)


@torch.no_grad()
def evaluate_generation(model, val_data, tokenizer, device, num_samples=50):
    """Evaluate generation quality with BLEU-4 and ROUGE-L."""
    model.eval()
    bleu_scores = []
    rouge_scores = []

    samples = random.sample(val_data, min(num_samples, len(val_data)))
    for ex in samples:
        src = tokenizer.encode(ex["input"], add_special=True)
        src_tensor = torch.tensor([src], dtype=torch.long).to(device)
        output_ids = model.generate(src_tensor, tokenizer, max_len=MAX_LEN)[0]
        pred_text = tokenizer.decode(output_ids.tolist())
        ref_text = ex["output"]

        bleu_scores.append(compute_bleu_4(ref_text, pred_text))
        rouge_scores.append(compute_rouge_l(ref_text, pred_text))

    return {
        "bleu_4": sum(bleu_scores) / max(len(bleu_scores), 1),
        "rouge_l": sum(rouge_scores) / max(len(rouge_scores), 1),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Improved Question Generation Model Training")
    print(f"Architecture: {D_MODEL}d, {NHEAD}h, {NUM_LAYERS}L, {DIM_FEEDFORWARD}ff")
    print(f"Training: {EPOCHS} epochs, batch={BATCH_SIZE}, lr={LR}")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Load dataset
    print("\n[1] Loading dataset...")
    with open(DATASET_PATH, encoding="utf-8") as f:
        data = json.load(f)
    train_raw = data["train"]
    val_raw = data["val"]
    print(f"  Train: {len(train_raw)} | Val: {len(val_raw)}")

    # Build tokenizer
    print("\n[2] Building tokenizer...")
    all_texts = [ex["input"] + " " + ex["output"] for ex in train_raw]
    tokenizer = CharTokenizer(target_vocab_size=VOCAB_SIZE)
    tokenizer.build_vocab(all_texts)
    print(f"  Vocab size: {tokenizer.vocab_size()}")

    # Create datasets
    train_ds = QGDataset(train_raw, tokenizer, max_len=MAX_LEN)
    val_ds = QGDataset(val_raw, tokenizer, max_len=MAX_LEN)
    print(f"  Train: {len(train_ds)} | Val: {len(val_ds)} (after length filtering)")

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE * 2, shuffle=False, collate_fn=collate_fn)

    # Create model
    print("\n[3] Creating model...")
    model = TinyQGModel(
        vocab_size=tokenizer.vocab_size(),
        d_model=D_MODEL,
        nhead=NHEAD,
        num_layers=NUM_LAYERS,
        dim_feedforward=DIM_FEEDFORWARD,
        dropout=DROPOUT,
    )
    param_count = sum(p.numel() for p in model.parameters())
    print(f"  Parameters: {param_count:,}")

    criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_id)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    # Train
    print("\n[4] Training...")
    best_loss = float("inf")
    patience_counter = 0
    history = {"train_loss": [], "val_loss": [], "val_acc": []}

    for epoch in range(EPOCHS):
        train_loss = train_epoch(model, train_loader, optimizer, criterion, device, tokenizer.pad_id)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        scheduler.step()

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        marker = ""
        if val_loss < best_loss:
            best_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), str(OUTPUT_DIR / "model.pt"))
            tokenizer.save(str(OUTPUT_DIR / "tokenizer.json"))
            marker = " <-- saved"
        else:
            patience_counter += 1

        print(f"  Epoch {epoch+1:2d}/{EPOCHS} | Train: {train_loss:.4f} | Val: {val_loss:.4f} | Acc: {val_acc:.4f}{marker}")

        if patience_counter >= PATIENCE:
            print(f"  Early stopping at epoch {epoch+1}")
            break

    print(f"\n[5] Best model saved to {OUTPUT_DIR}")

    # Load best model and evaluate generation quality
    print("\n[6] Evaluating generation quality...")
    model.load_state_dict(torch.load(str(OUTPUT_DIR / "model.pt"), map_location=device))
    gen_metrics = evaluate_generation(model, val_raw, tokenizer, device, num_samples=50)
    print(f"  BLEU-4:  {gen_metrics['bleu_4']:.4f}")
    print(f"  ROUGE-L: {gen_metrics['rouge_l']:.4f}")

    # Sample generations
    print("\n[7] Sample generations:")
    sample_inputs = [
        "[MCQ] Software Engineer | Java, Python, SQL | Medium",
        "[Descriptive] Backend Developer | Python, REST APIs | Medium",
        "[Coding] Software Engineer | Python | Easy",
    ]
    samples = []
    for inp_text in sample_inputs:
        src = tokenizer.encode(inp_text, add_special=True)
        src_tensor = torch.tensor([src], dtype=torch.long).to(device)
        output_ids = model.generate(src_tensor, tokenizer, max_len=MAX_LEN)[0]
        output_text = tokenizer.decode(output_ids.tolist())
        print(f"\n  Input:  {inp_text}")
        print(f"  Output: {output_text[:200]}")
        samples.append({"input": inp_text, "output": output_text})

    # Save evaluation results
    eval_results = {
        "num_samples": len(val_raw),
        "model_params": param_count,
        "architecture": {
            "d_model": D_MODEL,
            "nhead": NHEAD,
            "num_layers": NUM_LAYERS,
            "dim_feedforward": DIM_FEEDFORWARD,
            "dropout": DROPOUT,
            "vocab_size": tokenizer.vocab_size(),
        },
        "training": {
            "epochs": EPOCHS,
            "batch_size": BATCH_SIZE,
            "lr": LR,
            "best_val_loss": best_loss,
        },
        "generation_metrics": gen_metrics,
        "training_history": history,
        "sample_generations": samples,
    }

    results_path = MODELS_DIR / "qg_evaluation_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2, ensure_ascii=False)
    print(f"\n[8] Evaluation results saved to {results_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
