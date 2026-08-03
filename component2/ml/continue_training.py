"""Continue training QG model from checkpoint for up to 5 more epochs."""
import json
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

sys.path.insert(0, "ml")
from train_qg_model import TinyQGModel, CharTokenizer, QGDataset, collate_fn, train_epoch, evaluate

device = torch.device("cpu")
tokenizer = CharTokenizer.load(str(Path("models/qg_model/tokenizer.json")))

model = TinyQGModel(vocab_size=tokenizer.vocab_size())
model.load_state_dict(torch.load("models/qg_model/model.pt", map_location=device))
print(f"Loaded model ({sum(p.numel() for p in model.parameters()):,} params)")

data = json.load(open("models/qg_dataset.json"))
train_ds = QGDataset(data["train"], tokenizer, max_len=64)
val_ds = QGDataset(data["val"], tokenizer, max_len=64)
train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, collate_fn=collate_fn)
val_loader = DataLoader(val_ds, batch_size=64, shuffle=False, collate_fn=collate_fn)

criterion = torch.nn.CrossEntropyLoss(ignore_index=tokenizer.pad_id)
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-5)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=5)

best_loss = float("inf")
for epoch in range(5):
    train_loss = train_epoch(model, train_loader, optimizer, criterion, device, tokenizer.pad_id)
    val_loss, val_acc = evaluate(model, val_loader, criterion, device)
    scheduler.step()
    print(f"Epoch {epoch+1:2d}/5 | Train: {train_loss:.4f} | Val: {val_loss:.4f} | Acc: {val_acc:.4f}")
    if val_loss < best_loss:
        best_loss = val_loss
        torch.save(model.state_dict(), "models/qg_model/model.pt")
        tokenizer.save("models/qg_model/tokenizer.json")
        print(f"  -> Saved (val loss: {val_loss:.4f})")
    if val_loss > 0.5 and epoch >= 2:
        print("  -> No improvement, stopping")
        break

print(f"Done. Best val loss: {best_loss}")
