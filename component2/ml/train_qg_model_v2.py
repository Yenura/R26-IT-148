"""
Train QG Model v2 (canonical dataset)
-------------------------------------
Larger custom Seq2Seq Transformer trained on qg_dataset_v2.json:
  d_model=192, 6 heads, 3 enc + 3 dec layers, ff=768, vocab 8000.
Warmup + cosine LR, val-loss checkpointing, greedy + beam search helpers.

Artifacts -> models/qg_model_v2/{model_v2.pt, tokenizer_v2.json, config.json}
Runtime swap (P5) can later load via load_trained_model().
"""

import io
import json
import math
import os
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

if not getattr(sys.stdout, "encoding", None) or "utf" not in sys.stdout.encoding.lower():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
DATASET_PATH = Path(os.environ.get("QG_DATASET", str(MODELS_DIR / "qg_dataset_v2.json")))
OUTPUT_DIR = Path(os.environ.get("QG_OUTPUT", str(MODELS_DIR / "qg_model_v2")))

# ---------------------------------------------------------------------------
# Hyperparameters
# ---------------------------------------------------------------------------
D_MODEL = 192
NHEAD = 6
NUM_LAYERS = 3
DIM_FEEDFORWARD = 768
DROPOUT = 0.1
SRC_MAX_LEN = 24
TGT_MAX_LEN = 160
VOCAB_SIZE = 8000
BATCH_SIZE = 32
LR = 3e-4
WEIGHT_DECAY = 1e-5
EPOCHS = 20
PATIENCE = 8
WARMUP_STEPS = 200
GRAD_CLIP = 1.0
SEED = 42

MODEL_CFG = {
    "d_model": D_MODEL,
    "nhead": NHEAD,
    "num_layers": NUM_LAYERS,
    "dim_feedforward": DIM_FEEDFORWARD,
    "dropout": DROPOUT,
    "vocab_size": VOCAB_SIZE,
    "src_max_len": SRC_MAX_LEN,
    "tgt_max_len": TGT_MAX_LEN,
}


# ---------------------------------------------------------------------------
# Word-level tokenizer (same contract as v1)
# ---------------------------------------------------------------------------
class CharTokenizer:
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
# Model (same architecture contract as v1, standalone)
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


class TinyQGModelV2(nn.Module):
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
            d_model=d_model, nhead=nhead,
            num_encoder_layers=num_layers, num_decoder_layers=num_layers,
            dim_feedforward=dim_feedforward, dropout=dropout, batch_first=True,
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

    def generate(self, src, tokenizer: CharTokenizer, max_len: int = TGT_MAX_LEN,
                 temperature: float = 0.8):
        self.eval()
        device = src.device
        src_emb = self.embedding(src) * math.sqrt(self.d_model)
        src_emb = self.pos_encoder(src_emb)
        memory = self.transformer.encoder(src_emb)
        tgt = torch.full((src.size(0), 1), tokenizer.bos_id, dtype=torch.long, device=device)
        finished = torch.zeros(src.size(0), dtype=torch.bool, device=device)
        for _ in range(max_len):
            tgt_emb = self.embedding(tgt) * math.sqrt(self.d_model)
            tgt_emb = self.pos_decoder(tgt_emb)
            tgt_mask = self.transformer.generate_square_subsequent_mask(tgt.size(1)).to(device)
            out = self.transformer.decoder(tgt_emb, memory, tgt_mask=tgt_mask)
            logits = self.fc_out(out[:, -1, :]) / temperature
            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, 1)
            tgt = torch.cat([tgt, next_token], dim=1)
            finished = finished | (next_token.squeeze(-1) == tokenizer.eos_id)
            if finished.all():
                break
        return tgt


def load_trained_model(model_dir: str, device="cpu"):
    """Reconstruct TinyQGModelV2 + tokenizer from a trained v2 artifact dir."""
    model_dir = Path(model_dir)
    with open(model_dir / "config.json", encoding="utf-8") as f:
        cfg = json.load(f)
    tokenizer = CharTokenizer.load(str(model_dir / "tokenizer_v2.json"))
    model = TinyQGModelV2(
        vocab_size=cfg["vocab_size"], d_model=cfg["d_model"], nhead=cfg["nhead"],
        num_layers=cfg["num_layers"], dim_feedforward=cfg["dim_feedforward"],
        dropout=cfg.get("dropout", DROPOUT),
    )
    model.load_state_dict(torch.load(model_dir / "model_v2.pt", map_location=device))
    model.eval()
    return model, tokenizer


# ---------------------------------------------------------------------------
# Dataset (pads src/tgt to separate lengths)
# ---------------------------------------------------------------------------
class QGDatasetV2(Dataset):
    """Stores raw (unpadded) token ids; collate_fn pads per batch.

    Per-batch padding keeps the decoder self-attention cost tied to the
    actual lengths in the batch instead of a fixed MAX_LEN.
    """
    def __init__(self, data: List[Dict], tokenizer: CharTokenizer,
                 src_max_len: int = SRC_MAX_LEN, tgt_max_len: int = TGT_MAX_LEN):
        self.src_list = []
        self.tgt_list = []
        for ex in data:
            src = tokenizer.encode(ex["input"], add_special=True)
            tgt = tokenizer.encode(ex["output"], add_special=True)
            if len(src) > src_max_len or len(tgt) > tgt_max_len:
                continue
            self.src_list.append(src)
            self.tgt_list.append(tgt)

    def __len__(self):
        return len(self.src_list)

    def __getitem__(self, idx):
        return {"src": self.src_list[idx], "tgt": self.tgt_list[idx]}


def collate_fn_v2(batch, pad_id: int = 0):
    src_max = max(len(b["src"]) for b in batch)
    tgt_max = max(len(b["tgt"]) for b in batch)
    srcs = torch.zeros(len(batch), src_max, dtype=torch.long)
    tgts = torch.zeros(len(batch), tgt_max, dtype=torch.long)
    for i, b in enumerate(batch):
        srcs[i, :len(b["src"])] = torch.tensor(b["src"], dtype=torch.long)
        tgts[i, :len(b["tgt"])] = torch.tensor(b["tgt"], dtype=torch.long)
    return {"src": srcs, "tgt": tgts}


class BucketedBatchSampler:
    """Groups samples by target length so each batch has similar lengths.

    This drastically cuts wasted padding compute on CPU: short batches train
    in O(short_len^2) instead of O(MAX_LEN^2).
    """
    def __init__(self, lengths: List[int], batch_size: int, shuffle: bool = True,
                 seed: int = SEED, drop_last: bool = True):
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.seed = seed
        self.drop_last = drop_last
        self.batches = []
        order = sorted(range(len(lengths)), key=lambda i: lengths[i])
        for i in range(0, len(order) - batch_size + 1, batch_size):
            self.batches.append(order[i:i + batch_size])

    def __iter__(self):
        rng = random.Random(self.seed)
        batches = list(self.batches)
        if self.shuffle:
            rng.shuffle(batches)
            for b in batches:
                rng.shuffle(b)
        yield from batches

    def __len__(self):
        return len(self.batches)


# ---------------------------------------------------------------------------
# Training / validation helpers
# ---------------------------------------------------------------------------
def train_epoch_v2(model, dataloader, optimizer, criterion, device, pad_id: int,
                   scheduler=None):
    model.train()
    total_loss = 0.0
    for batch in dataloader:
        src = batch["src"].to(device)
        tgt = batch["tgt"].to(device)

        optimizer.zero_grad()
        output = model(src, tgt)

        tgt_target = tgt[:, 1:]
        loss = criterion(output.reshape(-1, output.size(-1)), tgt_target.reshape(-1))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
        optimizer.step()
        if scheduler is not None:
            scheduler.step()

        total_loss += loss.item()
    return total_loss / max(len(dataloader), 1)


@torch.no_grad()
def evaluate_v2(model, dataloader, criterion, device, pad_id: int):
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    for batch in dataloader:
        src = batch["src"].to(device)
        tgt = batch["tgt"].to(device)
        output = model(src, tgt)
        tgt_target = tgt[:, 1:]
        loss = criterion(output.reshape(-1, output.size(-1)), tgt_target.reshape(-1))
        total_loss += loss.item()

        preds = output.argmax(-1)
        mask = tgt_target != pad_id
        correct += (preds[mask] == tgt_target[mask]).sum().item()
        total += mask.sum().item()
    return total_loss / max(len(dataloader), 1), correct / max(total, 1)


# ---------------------------------------------------------------------------
# Decoding: greedy + beam search
# ---------------------------------------------------------------------------
@torch.no_grad()
def greedy_search(model, src, tokenizer, max_len: int = TGT_MAX_LEN):
    model.eval()
    device = src.device
    src_emb = model.embedding(src) * math.sqrt(model.d_model)
    src_emb = model.pos_encoder(src_emb)
    memory = model.transformer.encoder(src_emb)

    tgt = torch.tensor([[tokenizer.bos_id]], dtype=torch.long, device=device)
    for _ in range(max_len):
        tgt_emb = model.embedding(tgt) * math.sqrt(model.d_model)
        tgt_emb = model.pos_decoder(tgt_emb)
        tgt_mask = model.transformer.generate_square_subsequent_mask(tgt.size(1)).to(device)
        out = model.transformer.decoder(tgt_emb, memory, tgt_mask=tgt_mask)
        logits = model.fc_out(out[:, -1, :])
        next_token = logits.argmax(-1).unsqueeze(-1)
        tgt = torch.cat([tgt, next_token], dim=1)
        if next_token.item() == tokenizer.eos_id:
            break
    return tgt[0].tolist()


@torch.no_grad()
def beam_search(model, src, tokenizer, beam_width: int = 3,
                max_len: int = TGT_MAX_LEN, len_penalty: float = 0.6):
    model.eval()
    device = src.device
    src_emb = model.embedding(src) * math.sqrt(model.d_model)
    src_emb = model.pos_encoder(src_emb)
    memory = model.transformer.encoder(src_emb)

    bos, eos = tokenizer.bos_id, tokenizer.eos_id
    beams = [([bos], 0.0)]

    def score(b):
        return b[1] / (len(b[0]) ** len_penalty)

    for _ in range(max_len):
        candidates = []
        for seq, cum in beams:
            if seq[-1] == eos:
                candidates.append((seq, cum))
                continue
            tgt = torch.tensor([seq], dtype=torch.long, device=device)
            tgt_emb = model.embedding(tgt) * math.sqrt(model.d_model)
            tgt_emb = model.pos_decoder(tgt_emb)
            tgt_mask = model.transformer.generate_square_subsequent_mask(tgt.size(1)).to(device)
            out = model.transformer.decoder(tgt_emb, memory, tgt_mask=tgt_mask)
            log_probs = torch.log_softmax(model.fc_out(out[:, -1, :]), dim=-1)
            topk = torch.topk(log_probs, beam_width, dim=-1)
            for i in range(beam_width):
                tok = topk.indices[0, i].item()
                lp = topk.values[0, i].item()
                candidates.append((seq + [tok], cum + lp))
        candidates.sort(key=score, reverse=True)
        beams = candidates[:beam_width]
        if all(b[0][-1] == eos for b in beams):
            break
    return max(beams, key=score)[0]


# ---------------------------------------------------------------------------
# BLEU + ROUGE-L metrics
# ---------------------------------------------------------------------------
def _ngrams(tokens, n):
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def _bleu_n(ref, hyp, n):
    if not hyp or not ref:
        return 0.0
    hyp_ng = Counter(_ngrams(hyp, n))
    ref_ng = Counter(_ngrams(ref, n))
    clipped = sum(min(c, ref_ng.get(ng, 0)) for ng, c in hyp_ng.items())
    prec = clipped / max(sum(hyp_ng.values()), 1)
    bp = math.exp(min(0.0, 1.0 - len(ref) / max(len(hyp), 1)))
    return bp * prec


def compute_bleu(reference: str, hypothesis: str, max_n: int = 4) -> Dict[str, float]:
    ref = reference.lower().split()
    hyp = hypothesis.lower().split()
    return {f"bleu_{n}": _bleu_n(ref, hyp, n) for n in range(1, max_n + 1)}


def compute_bleu4_smoothed(reference: str, hypothesis: str) -> float:
    ref = reference.lower().split()
    hyp = hypothesis.lower().split()
    if not hyp or not ref:
        return 0.0
    precisions = []
    for n in range(1, 5):
        hyp_ng = Counter(_ngrams(hyp, n))
        ref_ng = Counter(_ngrams(ref, n))
        clipped = sum(min(c, ref_ng.get(ng, 0)) for ng, c in hyp_ng.items())
        total = max(sum(hyp_ng.values()), 1)
        precisions.append((clipped + 1.0) / (total + 1.0))
    geo = math.exp(sum(math.log(p) for p in precisions) / 4.0)
    bp = math.exp(min(0.0, 1.0 - len(ref) / max(len(hyp), 1)))
    return bp * geo


def compute_rouge_l(reference: str, hypothesis: str) -> float:
    ref = reference.lower().split()
    hyp = hypothesis.lower().split()
    if not ref or not hyp:
        return 0.0
    m, n = len(ref), len(hyp)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs = dp[m][n]
    if lcs == 0:
        return 0.0
    prec = lcs / len(hyp)
    rec = lcs / len(ref)
    return 2 * prec * rec / max(prec + rec, 1e-8)


# ---------------------------------------------------------------------------
# Format validity (mirrors question_generator parsers)
# ---------------------------------------------------------------------------
def _format_valid(example_type: str, output: str) -> bool:
    import re
    if example_type == "mcq":
        o = re.search(r"[Oo]:\s*(.+?)(?:\s*[QqAaKkLlCcTt]:|$)", output)
        a = re.search(r"[Aa]:\s*(\d+)", output)
        if not o or not a:
            return False
        opts = [x.strip() for x in o.group(1).split("|") if x.strip()]
        return len(opts) >= 2
    if example_type == "descriptive":
        a = re.search(r"[Aa]:\s*(.+?)(?:\s*[QqKkOoLlCcTt]:|$)", output)
        k = re.search(r"[Kk]:\s*(.+?)(?:\s*[QqAaOoLlCcTt]:|$)", output)
        return bool(a and a.group(1).strip() and k)
    if example_type == "coding":
        l = re.search(r"[Ll]:\s*(.+?)(?:\s*[QqAaKkOoCcTt]:|$)", output)
        t = re.search(r"[Tt]:\s*(\[.*?\])", output, re.DOTALL)
        c = re.search(r"[Cc]:\s*(.+?)$", output)
        if not (l and t and c):
            return False
        try:
            import json as _json
            return isinstance(_json.loads(t.group(1)), list)
        except Exception:
            return False
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    random.seed(SEED)
    torch.manual_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.set_num_threads(6)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("QG Model v2 Training (canonical dataset)")
    print(f"Arch: {D_MODEL}d, {NHEAD}h, {NUM_LAYERS}L, {DIM_FEEDFORWARD}ff | vocab {VOCAB_SIZE}")
    print(f"Device: {device} | epochs={EPOCHS} | lr={LR} | batch={BATCH_SIZE}")
    print("=" * 60)

    with open(DATASET_PATH, encoding="utf-8") as f:
        data = json.load(f)
    train_raw, val_raw = data["train"], data["val"]
    print(f"\nTrain: {len(train_raw)} | Val: {len(val_raw)}")

    all_texts = [ex["input"] + " " + ex["output"] for ex in train_raw]
    tokenizer = CharTokenizer(target_vocab_size=VOCAB_SIZE)
    tokenizer.build_vocab(all_texts)
    print(f"Vocab size: {tokenizer.vocab_size()}")

    train_ds = QGDatasetV2(train_raw, tokenizer)
    val_ds = QGDatasetV2(val_raw, tokenizer)
    print(f"After length filtering: Train {len(train_ds)} | Val {len(val_ds)}")

    train_sampler = BucketedBatchSampler(
        [len(s) for s in train_ds.tgt_list], BATCH_SIZE, shuffle=True)
    train_loader = DataLoader(train_ds, batch_sampler=train_sampler, collate_fn=collate_fn_v2)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE * 2, shuffle=False,
                            collate_fn=lambda b: collate_fn_v2(b, tokenizer.pad_id))

    model = TinyQGModelV2(
        vocab_size=tokenizer.vocab_size(), d_model=D_MODEL, nhead=NHEAD,
        num_layers=NUM_LAYERS, dim_feedforward=DIM_FEEDFORWARD, dropout=DROPOUT,
    )
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")

    criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_id)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)

    steps_per_epoch = max(len(train_loader), 1)
    total_steps = EPOCHS * steps_per_epoch
    warmup = min(WARMUP_STEPS, total_steps // 10)

    def lr_lambda(step):
        if step < warmup:
            return step / max(warmup, 1)
        progress = (step - warmup) / max(total_steps - warmup, 1)
        return 0.5 * (1.0 + math.cos(math.pi * min(progress, 1.0)))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    start_epoch = 0
    best_loss = float("inf")
    patience_counter = 0
    history = {"train_loss": [], "val_loss": [], "val_token_acc": [], "bleu1": [], "rouge_l": []}

    resume = "--resume" in sys.argv
    if resume and (OUTPUT_DIR / "model_v2.pt").exists():
        model.load_state_dict(torch.load(str(OUTPUT_DIR / "model_v2.pt"), map_location=device))
        if (OUTPUT_DIR / "optimizer.pt").exists():
            optimizer.load_state_dict(torch.load(str(OUTPUT_DIR / "optimizer.pt"), map_location=device))
        if (OUTPUT_DIR / "history.json").exists():
            with open(OUTPUT_DIR / "history.json", encoding="utf-8") as f:
                history = json.load(f)
            start_epoch = len(history["val_loss"])
            best_loss = min(history["val_loss"]) if history["val_loss"] else float("inf")
        print(f"[RESUME] continuing from epoch {start_epoch} (best val loss {best_loss:.4f})")

    for epoch in range(start_epoch, EPOCHS):
        train_loss = train_epoch_v2(model, train_loader, optimizer, criterion, device,
                                    tokenizer.pad_id, scheduler=scheduler)
        val_loss, val_acc = evaluate_v2(model, val_loader, criterion, device, tokenizer.pad_id)
        cur_lr = optimizer.param_groups[0]["lr"]

        gen_bleu, gen_rouge = 0.0, 0.0
        if (epoch - start_epoch) % 2 == 0 or epoch == EPOCHS - 1:
            subset = random.sample(val_raw, min(16, len(val_raw)))
            for ex in subset:
                src = torch.tensor([tokenizer.encode(ex["input"], add_special=True)], dtype=torch.long).to(device)
                out_ids = greedy_search(model, src, tokenizer, max_len=min(140, TGT_MAX_LEN))
                pred = tokenizer.decode(out_ids)
                gen_bleu += _bleu_n(ex["output"].lower().split(), pred.lower().split(), 1)
                gen_rouge += compute_rouge_l(ex["output"], pred)
            gen_bleu /= len(subset)
            gen_rouge /= len(subset)

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_token_acc"].append(val_acc)
        history["bleu1"].append(gen_bleu)
        history["rouge_l"].append(gen_rouge)

        marker = ""
        if val_loss < best_loss:
            best_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), str(OUTPUT_DIR / "model_v2.pt"))
            torch.save(optimizer.state_dict(), str(OUTPUT_DIR / "optimizer.pt"))
            tokenizer.save(str(OUTPUT_DIR / "tokenizer_v2.json"))
            with open(OUTPUT_DIR / "config.json", "w", encoding="utf-8") as f:
                json.dump({**MODEL_CFG, "vocab_size": tokenizer.vocab_size()}, f, indent=2)
            with open(OUTPUT_DIR / "history.json", "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
            marker = " <-- saved"
        else:
            patience_counter += 1

        print(f"Epoch {epoch+1:2d}/{EPOCHS} | train {train_loss:.4f} | val {val_loss:.4f} | "
              f"tok_acc {val_acc:.3f} | BLEU1 {gen_bleu:.3f} | ROUGE-L {gen_rouge:.3f} | "
              f"lr {cur_lr:.2e}{marker}")

        if patience_counter >= PATIENCE:
            print(f"  Early stopping at epoch {epoch+1}")
            break

    print(f"\nBest val loss: {best_loss:.4f} -> {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
