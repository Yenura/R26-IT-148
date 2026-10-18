"""
Short A/B of *valid* initializations for the compact QG model.

Depth-truncating flan-t5-small breaks it (the retained layers' output does not
match the pretrained final layer-norm / lm_head), giving loss ~ln(vocab)=10.4
and degenerate output. This script trains three valid variants for a few dozen
steps on the real v2 data and prints the loss curve so the full run can pick the
initialization that actually learns fastest on this CPU-only box.

Variants
  t22      : 512-d, pretrained enc[0:2] + pretrained dec[0:2]  (the broken one, for reference)
  e8d2     : 512-d, pretrained encoder (all 8 layers, valid) + random 2-layer decoder
  scratch  : 256-d, 2+2 layers, fully random
"""
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import torch
from torch.utils.data import DataLoader
from transformers import T5Config, T5ForConditionalGeneration, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ml.train_t5_qg_v2 import QGDataset, make_collate, PRETRAINED, MODELS_DIR  # noqa: E402

STEPS = 40
BATCH = 8
LR = 3e-4


def build(variant, tokenizer):
    if variant == "scratch":
        cfg = T5Config(vocab_size=32128, d_model=256, d_ff=512, d_kv=64, num_heads=4,
                       num_layers=2, num_decoder_layers=2, decoder_start_token_id=0,
                       pad_token_id=0, eos_token_id=1, tie_word_embeddings=True)
        return T5ForConditionalGeneration(cfg).train()

    nenc, ndec, copy_dec = (2, 2, True) if variant == "t22" else (8, 2, False)

    cfg = T5Config(vocab_size=32128, d_model=512, d_ff=1024, d_kv=64, num_heads=6,
                   num_layers=nenc, num_decoder_layers=ndec, decoder_start_token_id=0,
                   pad_token_id=0, eos_token_id=1, tie_word_embeddings=True,
                   feed_forward_proj="gated-gelu")
    model = T5ForConditionalGeneration(cfg)
    src = T5ForConditionalGeneration.from_pretrained(PRETRAINED)
    sd = src.state_dict()
    new = {}
    for k, v in sd.items():
        if k.startswith("encoder.block.") and int(k.split(".")[2]) >= nenc:
            continue
        if k.startswith("decoder.block."):
            if not copy_dec:
                continue
            if int(k.split(".")[2]) >= ndec:
                continue
        if k.startswith("decoder.") and not copy_dec and not k.startswith("decoder.block."):
            # decoder.embed_tokens is shared; drop the standalone copy
            if k == "decoder.embed_tokens.weight":
                continue
        new[k] = v
    del src, sd
    missing, unexpected = model.load_state_dict(new, strict=False)
    del new
    return model.train(), len(missing), len(unexpected)


def main():
    data = json.loads((MODELS_DIR / "qg_dataset_v2.json").read_text(encoding="utf-8"))
    tokenizer = AutoTokenizer.from_pretrained(PRETRAINED)
    ds = QGDataset(data["train"], tokenizer, 64, 128)
    loader = DataLoader(ds, batch_size=BATCH, shuffle=True, collate_fn=make_collate(tokenizer.pad_token_id), drop_last=True)
    print(f"train examples: {len(ds)}", flush=True)

    for variant in ("t22", "e8d2", "scratch"):
        print("\n" + "=" * 62, flush=True)
        built = build(variant, tokenizer)
        model = built[0] if isinstance(built, tuple) else built
        extra = f"  missing={built[1]} unexpected={built[2]}" if isinstance(built, tuple) else ""
        n = sum(p.numel() for p in model.parameters())
        print(f"variant={variant}  params={n:,}{extra}", flush=True)
        opt = torch.optim.AdamW(model.parameters(), lr=LR)
        t0 = time.time()
        it = iter(loader)
        for step in range(1, STEPS + 1):
            try:
                input_ids, attn, labels = next(it)
            except StopIteration:
                it = iter(loader)
                input_ids, attn, labels = next(it)
            out = model(input_ids=input_ids, attention_mask=attn, labels=labels)
            out.loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            opt.zero_grad()
            if step % 10 == 0 or step == 1:
                print(f"  step {step:3d}  loss={float(out.loss):7.3f}  "
                      f"{time.time()-t0:5.1f}s  ({step*BATCH/(time.time()-t0):4.2f} ex/s)", flush=True)
        del model, opt


if __name__ == "__main__":
    main()
