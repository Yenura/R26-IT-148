"""
Component 2: Proper T5 question-generation training.

Fixes the flaws of the previous pipeline:
  * checkpoint selected by *generation* quality (ROUGE-L / BLEU-4), never by
    teacher-forced token accuracy or validation loss alone;
  * real corpus BLEU-4 (4-gram precisions + brevity penalty) and ROUGE-L F1,
    computed with actual beam/greedy decoding;
  * field-validity + exact-match rates, so a "high BLEU" model that cannot be
    parsed by the app is still reported as unusable;
  * the tokenizer is saved with the *installed* transformers so the artifact
    reloads (the old t5_qg/tokenizer_config.json was written by transformers
    5.15.1 with an ``extra_special_tokens`` list that 4.57.6 rejects);
  * best checkpoint, history.json and spot-check samples are all written to disk
    and the best checkpoint is reloaded at the end to prove it loads.

Why a small from-scratch model
------------------------------
This box is CPU-only with ~7.6 GB RAM. The full 77M flan-t5-small measures
~24 s/train-step (hours per epoch) -- infeasible. Depth-truncating it to keep
the pretrained weights does NOT work: truncation leaves the retained layers'
output mismatched with the pretrained final layer-norm / lm_head, so the model
is functionally broken (loss ~ln(32128)=10.4, degenerate "Künstler Künstler"
output). Measured in ml/ab_init_test.py, a compact 256-d / 3+3 from-scratch T5
reaches a lower loss faster than either warm-started variant, and runs ~3x
faster, so it fits ~2 epochs instead of <1. Raise --d-model/--enc-layers/
--dec-layers (and lower --batch-size) on a machine with more RAM/GPU.

Usage
-----
    python -m ml.train_t5_qg_v2 --max-steps 900 --batch-size 8 --grad-accum 4
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import math
import os
import random
import sys
import time
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import T5Config, T5ForConditionalGeneration, AutoTokenizer
from transformers.optimization import Adafactor

if not getattr(sys.stdout, "encoding", None) or "utf" not in sys.stdout.encoding.lower():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
DEFAULT_DATASET = MODELS_DIR / "qg_dataset_v2.json"
DEFAULT_OUT = MODELS_DIR / "t5_qg"
PRETRAINED = "google/flan-t5-small"

# Marker each question type must emit for the app's parser to accept it.
REQUIRED_MARKERS = {
    "[MCQ]": ("Q:", "O:", "A:"),
    "[Descriptive]": ("Q:", "A:"),
    "[Coding]": ("Q:", "L:", "T:"),
}


# ─────────────────────────────────────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────────────────────────────────────
def _ngrams(tokens, n):
    return collections.Counter(tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1))


def corpus_bleu4(hyps, refs):
    """Standard corpus BLEU-4: geometric mean of clipped 1..4-gram precisions
    times a brevity penalty. Returns a score in [0, 100]."""
    max_n = 4
    clipped = [0] * (max_n + 1)
    total = [0] * (max_n + 1)
    hyp_len = ref_len = 0
    for h, r in zip(hyps, refs):
        hyp_len += len(h)
        ref_len += len(r)
        for n in range(1, max_n + 1):
            hc = _ngrams(h, n)
            rc = _ngrams(r, n)
            total[n] += sum(hc.values())
            clipped[n] += sum(min(c, rc.get(g, 0)) for g, c in hc.items())
    if hyp_len == 0:
        return 0.0
    bp = 1.0 if hyp_len > ref_len else math.exp(1 - ref_len / max(hyp_len, 1))
    log_p = 0.0
    for n in range(1, max_n + 1):
        if total[n] == 0 or clipped[n] == 0:
            return 0.0
        log_p += math.log(clipped[n] / total[n])
    return bp * math.exp(log_p / max_n) * 100.0


def _lcs_len(a, b):
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            cur[j] = prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def rouge_l_f1(hyp, ref, beta=1.0):
    """ROUGE-L F-measure (beta=1) from the longest common subsequence."""
    if not hyp or not ref:
        return 0.0
    l = _lcs_len(hyp, ref)
    if l == 0:
        return 0.0
    p = l / len(hyp)
    r = l / len(ref)
    b2 = beta * beta
    return (1 + b2) * p * r / (r + b2 * p)


def field_valid(qtype, text):
    """True when the app's parser could turn this generation into a question."""
    needed = REQUIRED_MARKERS.get(qtype, ("Q:",))
    upper = text.upper()
    return all(m in upper for m in needed) and len(text.strip()) > 0


def normalize(s):
    return " ".join(s.lower().split())


def compute_metrics(records):
    """records: list of dicts with keys qtype, ref, hyp."""
    hyps = [normalize(r["hyp"]).split() for r in records]
    refs = [normalize(r["ref"]).split() for r in records]
    out = {
        "n": len(records),
        "bleu4": round(corpus_bleu4(hyps, refs), 2),
        "rouge_l": round(
            100.0 * sum(rouge_l_f1(h, r) for h, r in zip(hyps, refs)) / max(len(records), 1), 2
        ),
        "exact_match": round(
            100.0 * sum(normalize(r["hyp"]) == normalize(r["ref"]) for r in records) / max(len(records), 1), 2
        ),
        "field_valid": round(
            100.0 * sum(field_valid(r["qtype"], r["hyp"]) for r in records) / max(len(records), 1), 2
        ),
    }
    by_type = {}
    for t in sorted({r["qtype"] for r in records}):
        sub = [r for r in records if r["qtype"] == t]
        sh = [normalize(r["hyp"]).split() for r in sub]
        sr = [normalize(r["ref"]).split() for r in sub]
        by_type[t] = {
            "n": len(sub),
            "bleu4": round(corpus_bleu4(sh, sr), 2),
            "rouge_l": round(100.0 * sum(rouge_l_f1(h, r) for h, r in zip(sh, sr)) / len(sub), 2),
            "field_valid": round(100.0 * sum(field_valid(r["qtype"], r["hyp"]) for r in sub) / len(sub), 2),
        }
    out["by_type"] = by_type
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────────────────────
class QGDataset(Dataset):
    def __init__(self, examples, tokenizer, max_src=64, max_tgt=128):
        self.items = []
        for ex in examples:
            src = tokenizer(ex["input"], max_length=max_src, truncation=True, padding=False)["input_ids"]
            tgt = tokenizer(ex["output"], max_length=max_tgt, truncation=True, padding=False)["input_ids"]
            if len(src) < 2 or len(tgt) < 2:
                continue
            self.items.append((src, tgt, ex["input"].split("]")[0] + "]"))

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]


def make_collate(pad_id):
    def collate(batch):
        srcs = [torch.tensor(x[0]) for x in batch]
        tgts = [torch.tensor(x[1]) for x in batch]
        input_ids = torch.nn.utils.rnn.pad_sequence(srcs, batch_first=True, padding_value=pad_id)
        attn = (input_ids != pad_id).long()
        labels = torch.nn.utils.rnn.pad_sequence(tgts, batch_first=True, padding_value=-100)
        return input_ids, attn, labels
    return collate


def stratified_subset(examples, n, seed=0):
    """Pick `n` examples spread evenly across question types."""
    buckets = collections.defaultdict(list)
    for ex in examples:
        buckets[ex["input"].split("]")[0] + "]"].append(ex)
    rng = random.Random(seed)
    for v in buckets.values():
        rng.shuffle(v)
    picked, i = [], 0
    keys = list(buckets)
    while len(picked) < n and any(buckets[k] for k in keys):
        k = keys[i % len(keys)]
        if buckets[k]:
            picked.append(buckets[k].pop())
        i += 1
    rng.shuffle(picked)
    return picked[:n]


# ─────────────────────────────────────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────────────────────────────────────
def build_model(enc_layers, dec_layers, tokenizer, init="scratch",
                d_model=256, d_ff=512, heads=4):
    """Build the QG model.

    init="scratch" (default): compact T5, random weights. Measured on this
        CPU-only box (ml/ab_init_test.py) to converge *faster* than every
        warm-started alternative while running ~2-3x faster, so it fits ~2
        epochs instead of <1.
    init="warm": flan-t5-small truncated to enc_layers/dec_layers. Requires
        d_model=512/d_ff=1024/heads=6 to be key-compatible, but depth truncation
        leaves the pretrained final layer-norm and lm_head mismatched, so the
        result is functionally broken (loss ~ln(vocab), degenerate output). Kept
        only for reproducible comparison.
    """
    if init == "warm":
        cfg = T5Config(
            vocab_size=32128, d_model=512, d_ff=1024, d_kv=64, num_heads=6,
            num_layers=enc_layers, num_decoder_layers=dec_layers,
            decoder_start_token_id=0, pad_token_id=0, eos_token_id=1,
            tie_word_embeddings=True, feed_forward_proj="gated-gelu",
        )
        model = T5ForConditionalGeneration(cfg)
        src = T5ForConditionalGeneration.from_pretrained(PRETRAINED)
        sd = src.state_dict()
        new = {}
        for k, v in sd.items():
            if k.startswith("encoder.block.") and int(k.split(".")[2]) >= enc_layers:
                continue
            if k.startswith("decoder.block.") and int(k.split(".")[2]) >= dec_layers:
                continue
            new[k] = v
        del src, sd
        missing, unexpected = model.load_state_dict(new, strict=False)
        del new
        return model, list(missing), list(unexpected)

    cfg = T5Config(
        vocab_size=32128, d_model=d_model, d_ff=d_ff, d_kv=64, num_heads=heads,
        num_layers=enc_layers, num_decoder_layers=dec_layers,
        decoder_start_token_id=0, pad_token_id=0, eos_token_id=1,
        tie_word_embeddings=True,
    )
    return T5ForConditionalGeneration(cfg), [], []


@torch.no_grad()
def generate_texts(model, tokenizer, inputs, max_new=128, max_src=64, batch=8):
    model.eval()
    outs = []
    for i in range(0, len(inputs), batch):
        chunk = inputs[i:i + batch]
        enc = tokenizer(chunk, max_length=max_src, truncation=True, padding=True, return_tensors="pt")
        ids = model.generate(
            input_ids=enc["input_ids"], attention_mask=enc["attention_mask"],
            max_new_tokens=max_new, num_beams=1, do_sample=False,
        )
        outs.extend(tokenizer.batch_decode(ids, skip_special_tokens=True))
    model.train()
    return outs


def evaluate(model, tokenizer, eval_examples, max_src=64, max_new=128):
    inputs = [e["input"] for e in eval_examples]
    hyps = generate_texts(model, tokenizer, inputs, max_new=max_new, max_src=max_src)
    records = [
        {"qtype": e["input"].split("]")[0] + "]", "ref": e["output"], "hyp": h}
        for e, h in zip(eval_examples, hyps)
    ]
    return compute_metrics(records), records


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=str(DEFAULT_DATASET))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--init", choices=["scratch", "warm"], default="scratch",
                    help="scratch = compact random model (recommended here); warm = truncated flan-t5-small (broken, see docstring)")
    ap.add_argument("--enc-layers", type=int, default=3)
    ap.add_argument("--dec-layers", type=int, default=3)
    ap.add_argument("--d-model", type=int, default=256)
    ap.add_argument("--d-ff", type=int, default=512)
    ap.add_argument("--heads", type=int, default=4)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--lr", type=float, default=6e-4)
    ap.add_argument("--warmup-steps", type=int, default=100)
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--max-steps", type=int, default=900)
    ap.add_argument("--max-src", type=int, default=64)
    ap.add_argument("--max-tgt", type=int, default=128)
    ap.add_argument("--eval-every", type=int, default=150)
    ap.add_argument("--eval-size", type=int, default=96)
    ap.add_argument("--resume", action="store_true",
                    help="continue from the rolling --latest state (survives a killed run)")
    ap.add_argument("--latest", default="",
                    help="rolling resume-state dir; defaults to <out>_latest")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--smoke", action="store_true", help="tiny run to validate the pipeline")
    args = ap.parse_args()

    if args.smoke:
        args.max_steps, args.eval_every, args.eval_size, args.epochs = 4, 4, 9, 1

    random.seed(args.seed)
    torch.manual_seed(args.seed)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    tokenizer = AutoTokenizer.from_pretrained(PRETRAINED)
    pad_id = tokenizer.pad_token_id

    train_ds = QGDataset(data["train"], tokenizer, args.max_src, args.max_tgt)
    eval_examples = stratified_subset(data["val"], args.eval_size, seed=args.seed)

    print(f"dataset={args.dataset}  train={len(train_ds)}  eval={len(eval_examples)}", flush=True)

    model, missing, unexpected = build_model(
        args.enc_layers, args.dec_layers, tokenizer,
        init=args.init, d_model=args.d_model, d_ff=args.d_ff, heads=args.heads,
    )
    n_params = sum(p.numel() for p in model.parameters())
    print(f"arch: init={args.init} d_model={args.d_model} d_ff={args.d_ff} heads={args.heads} "
          f"enc={args.enc_layers} dec={args.dec_layers}  params={n_params:,}  "
          f"missing={len(missing)} unexpected={len(unexpected)}", flush=True)
    residual = [k for k in list(missing) + list(unexpected) if "lm_head" not in k]
    if args.init == "warm" and residual:
        raise SystemExit(f"warm start incomplete; unexpected/missing weights: {residual[:8]}")

    collate = make_collate(pad_id)
    loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                        collate_fn=collate, drop_last=True, num_workers=0)

    def make_optimizer(m):
        return Adafactor(m.parameters(), scale_parameter=False, relative_step=False,
                         warmup_init=False, lr=args.lr)

    def make_sched(o):
        return torch.optim.lr_scheduler.LambdaLR(
            o,
            lambda s: min((s + 1) / max(args.warmup_steps, 1), 1.0)
            * max(0.0, (args.max_steps - s) / max(args.max_steps - args.warmup_steps, 1)),
        )

    optimizer = make_optimizer(model)
    sched = make_sched(optimizer)

    history = []
    best = {"rouge_l": -1.0}
    samples = []
    global_step = 0
    latest_dir = Path(args.latest) if args.latest else Path(str(out_dir) + "_latest")
    t_start = time.time()

    # Resume a killed run. The rolling "latest" state (model + optimizer +
    # scheduler + step) is rewritten on every eval, so a kill costs at most one
    # eval interval instead of the entire run.
    base_metrics = {}
    if args.resume and (latest_dir / "state.json").is_file():
        st = json.loads((latest_dir / "state.json").read_text(encoding="utf-8"))
        # Load eagerly (no memory-map). On Windows an mmapped model.safetensors
        # cannot then be overwritten by save_pretrained (os error 1224), which
        # is exactly what a resume needs to do.
        from safetensors.torch import load_file

        sd = load_file(str(latest_dir / "model.safetensors"))
        info = model.load_state_dict(sd, strict=False)
        del sd
        # Tied weights (shared / embed_tokens / lm_head) are deduplicated by
        # save_pretrained, so they legitimately report as missing.
        tied = [k for k in info.missing_keys
                if k.endswith("embed_tokens.weight") or k == "lm_head.weight"]
        untied = [k for k in info.missing_keys if k not in tied]
        if untied or info.unexpected_keys:
            print(f"  resume WARNING: untied_missing={untied[:5]} "
                  f"unexpected={info.unexpected_keys[:5]}", flush=True)
        else:
            print(f"  resume: weights restored (tied keys skipped: {len(tied)})", flush=True)
        n_params = sum(p.numel() for p in model.parameters())
        optimizer = make_optimizer(model)
        sched = make_sched(optimizer)
        if (latest_dir / "optimizer.pt").is_file():
            optimizer.load_state_dict(torch.load(latest_dir / "optimizer.pt", map_location="cpu"))
        if (latest_dir / "scheduler.pt").is_file():
            sched.load_state_dict(torch.load(latest_dir / "scheduler.pt", map_location="cpu"))
        else:
            # No saved schedule: jump straight to the correct point of the curve
            # instead of restarting it from step 0.
            sched.last_epoch = global_step
            lam = sched.lr_lambdas[0]
            for pg in optimizer.param_groups:
                pg["lr"] = pg.get("initial_lr", args.lr) * lam(global_step)
        global_step = int(st.get("step", 0))
        history = st.get("history", [])
        best = st.get("best", best)
        samples = st.get("samples", [])
        base_metrics = st.get("baseline", {})
        print(f"resumed from {latest_dir} at step {global_step}  "
              f"(best field_valid={best.get('field_valid')}% @{best.get('step')})", flush=True)

    model.train()

    if not base_metrics:
        # baseline (untrained) quality, for an honest before/after
        base_metrics, base_records = evaluate(model, tokenizer, eval_examples, args.max_src, args.max_tgt)
        print(f"[baseline ] rouge_l={base_metrics['rouge_l']:6.2f} bleu4={base_metrics['bleu4']:6.2f} "
              f"field_valid={base_metrics['field_valid']:5.1f}%", flush=True)
        history.append({"step": 0, "phase": "baseline", **base_metrics})

    optimizer.zero_grad()
    stop = False
    for epoch in range(1, args.epochs + 1):
        for input_ids, attn, labels in loader:
            outputs = model(input_ids=input_ids, attention_mask=attn, labels=labels)
            loss = outputs.loss / args.grad_accum
            loss.backward()
            if (global_step + 1) % args.grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                sched.step()
                optimizer.zero_grad()
            global_step += 1

            if global_step % 25 == 0:
                el = time.time() - t_start
                print(f"  step {global_step:4d}  loss~{loss.item() * args.grad_accum:7.3f}  "
                      f"{el/60:5.1f}min  {global_step*args.batch_size/el:4.2f} ex/s", flush=True)

            if global_step % args.eval_every == 0 or global_step >= args.max_steps:
                metrics, records = evaluate(model, tokenizer, eval_examples, args.max_src, args.max_tgt)
                metrics["epoch"] = epoch
                history.append({"step": global_step, "phase": "train", **metrics})
                print(f"[eval @{global_step:4d}] rouge_l={metrics['rouge_l']:6.2f} bleu4={metrics['bleu4']:6.2f} "
                      f"field_valid={metrics['field_valid']:5.1f}% exact={metrics['exact_match']:5.1f}%", flush=True)
                # Select on usability first: a checkpoint the app cannot parse
                # (field_valid == 0) is worthless however high its ROUGE-L, so
                # rank by (field_valid, ROUGE-L) rather than ROUGE-L alone.
                score = (metrics["field_valid"], metrics["rouge_l"])
                if score > (best.get("field_valid", -1.0), best.get("rouge_l", -1.0)):
                    best = {"rouge_l": metrics["rouge_l"], "bleu4": metrics["bleu4"],
                            "step": global_step, "field_valid": metrics["field_valid"]}
                    model.save_pretrained(out_dir)
                    tokenizer.save_pretrained(out_dir)
                    samples = records[:24]
                    print(f"  saved best checkpoint -> {out_dir}", flush=True)
                # Rolling resume state, rewritten every eval: a kill costs at
                # most one eval interval.
                latest_dir.mkdir(parents=True, exist_ok=True)
                model.save_pretrained(latest_dir)
                tokenizer.save_pretrained(latest_dir)
                torch.save(optimizer.state_dict(), latest_dir / "optimizer.pt")
                torch.save(sched.state_dict(), latest_dir / "scheduler.pt")
                (latest_dir / "state.json").write_text(json.dumps({
                    "step": global_step, "history": history, "best": best,
                    "samples": samples, "baseline": base_metrics,
                }), encoding="utf-8")
            if global_step >= args.max_steps:
                stop = True
                break
        if stop:
            break

    # final full-val evaluation of the best saved checkpoint
    if (out_dir / "model.safetensors").is_file():
        del model
        reloaded = T5ForConditionalGeneration.from_pretrained(out_dir)
        reloader = AutoTokenizer.from_pretrained(out_dir)
        print("reloaded best checkpoint OK:", sum(p.numel() for p in reloaded.parameters()), "params", flush=True)
        full_eval = stratified_subset(data["val"], min(len(data["val"]), 256), seed=args.seed)
        final_metrics, final_records = evaluate(reloaded, reloader, full_eval, args.max_src, args.max_tgt)
    else:
        final_metrics, final_records = {"error": "no checkpoint saved"}, []

    report = {
        "config": vars(args),
        "params": n_params,
        "train_size": len(train_ds),
        "eval_size": len(eval_examples),
        "history": history,
        "best": best,
        "final_val": final_metrics,
        "elapsed_min": round((time.time() - t_start) / 60, 1),
        "baseline": base_metrics,
    }
    (out_dir / "history.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out_dir / "samples.json").write_text(
        json.dumps([{k: r[k] for k in ("qtype", "ref", "hyp")} for r in (samples or final_records)], indent=2),
        encoding="utf-8",
    )

    print("\n===== FINAL =====", flush=True)
    print(f"baseline rouge_l={base_metrics['rouge_l']:.2f} bleu4={base_metrics['bleu4']:.2f} "
          f"field_valid={base_metrics['field_valid']:.1f}%")
    print(f"final    rouge_l={final_metrics.get('rouge_l')} bleu4={final_metrics.get('bleu4')} "
          f"field_valid={final_metrics.get('field_valid')}%")
    for t, m in (final_metrics.get("by_type") or {}).items():
        print(f"   {t:<14} n={m['n']:<4} rouge_l={m['rouge_l']:6.2f} bleu4={m['bleu4']:6.2f} "
              f"field_valid={m['field_valid']:5.1f}%")
    print(f"elapsed={report['elapsed_min']} min  out={out_dir}")


if __name__ == "__main__":
    main()
