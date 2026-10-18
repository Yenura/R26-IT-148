"""Decisive test: can the saved T5 checkpoint reproduce a TRAINING example?
If not, the checkpoint is dead regardless of teacher-forced token accuracy."""
import json
import os
import pathlib
import torch
from transformers import AutoTokenizer, T5ForConditionalGeneration

MODELS = pathlib.Path(__file__).parent.parent.parent / "models"
T5 = str(MODELS / "t5_qg")

data = json.loads((MODELS / "qg_dataset_merged.json").read_text(encoding="utf-8"))
train = data["train"] if isinstance(data, dict) else data
print("train examples:", len(train))
ex = train[0]
print("\nGOLD INPUT :", ex["input"][:160])
print("GOLD OUTPUT:", ex["output"][:200])

tok = AutoTokenizer.from_pretrained(T5, extra_special_tokens={})
model = T5ForConditionalGeneration.from_pretrained(T5, dtype=torch.float32)
model.eval()

ids = tok(ex["input"], return_tensors="pt", max_length=64, truncation=True)

# 1) teacher-forced accuracy on the gold label
labels = tok(ex["output"], return_tensors="pt", max_length=128, truncation=True)["input_ids"]
with torch.no_grad():
    logits = model(input_ids=ids["input_ids"], attention_mask=ids["attention_mask"],
                   labels=labels).logits
preds = logits.argmax(-1)
mask = labels != tok.pad_token_id
acc = (preds[mask] == labels[mask]).float().mean().item() if mask.any() else 0.0
print(f"\nteacher-forced token acc vs gold: {acc:.3f}")

# 2) free-running greedy generation from the same input
with torch.no_grad():
    out = model.generate(input_ids=ids["input_ids"], attention_mask=ids["attention_mask"],
                         max_length=80, num_beams=1, do_sample=False)
gen = tok.decode(out[0], skip_special_tokens=True)
print("free-running generation        :", gen[:220])

# 3) does it at least echo gold tokens when given a gold prefix? (copy ability)
prefix = ex["output"][:40]
pfx_ids = tok(ex["input"] + " " + prefix, return_tensors="pt", max_length=96, truncation=True)["input_ids"]
with torch.no_grad():
    out2 = model.generate(input_ids=pfx_ids, max_length=80, num_beams=1, do_sample=False)
print("with gold prefix               :", tok.decode(out2[0], skip_special_tokens=True)[:220])
