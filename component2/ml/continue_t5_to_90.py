"""Resume T5 training from checkpoint to 90% token_acc."""
import json, os, random, math, sys
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import T5ForConditionalGeneration, AutoTokenizer, get_linear_schedule_with_warmup

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
DATASET_PATH = MODELS_DIR / "qg_dataset_merged.json"
OUTPUT_DIR = MODELS_DIR / "t5_qg"
EPOCHS = 15
LR = 1.5e-4
BATCH = 8
GRAD_ACCUM = 2
MAX_SRC=64; MAX_TGT=128
PATIENCE=5; TARGET=0.90

class QGDataset(Dataset):
    def __init__(self, exs, tok, ms, mt):
        self.exs=exs;self.tok=tok;self.ms=ms;self.mt=mt
    def __len__(self): return len(self.exs)
    def __getitem__(self,i):
        ex=self.exs[i]
        se=self.tok(ex["input"], max_length=self.ms, padding="max_length", truncation=True, return_tensors="pt")
        te=self.tok(ex["output"], max_length=self.mt, padding="max_length", truncation=True, return_tensors="pt")
        labels=te["input_ids"].squeeze()
        labels[labels==self.tok.pad_token_id]=-100
        return {"input_ids":se["input_ids"].squeeze(),"attention_mask":se["attention_mask"].squeeze(),"labels":labels}

def main():
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}, resuming {OUTPUT_DIR}", flush=True)
    tok=AutoTokenizer.from_pretrained(OUTPUT_DIR)
    print("Tokenizer loaded", flush=True)
    model=T5ForConditionalGeneration.from_pretrained(OUTPUT_DIR)
    print("Model loaded", flush=True)
    model.to(device)
    print(f"Loaded checkpoint params {sum(p.numel() for p in model.parameters()):,}", flush=True)
    data=json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    train, val = data["train"], data["val"]
    print(f"train {len(train)} val {len(val)}", flush=True)
    # resume history if exists
    hist_path=OUTPUT_DIR/"history.json"
    hist=json.loads(hist_path.read_text()) if hist_path.exists() else {"train_loss":[],"val_loss":[],"val_token_acc":[],"bleu1":[],"rouge_l":[]}
    print(f"Current best tok_acc {max(hist['val_token_acc']) if hist['val_token_acc'] else 0:.4f}", flush=True)

    train_ds=QGDataset(train,tok,MAX_SRC,MAX_TGT)
    val_ds=QGDataset(val,tok,MAX_SRC,MAX_TGT)
    train_loader=DataLoader(train_ds,batch_size=BATCH,shuffle=True)
    val_loader=DataLoader(val_ds,batch_size=BATCH)

    total_steps=len(train_loader)*EPOCHS//GRAD_ACCUM
    warmup=int(total_steps*0.1)
    optimizer=torch.optim.AdamW(model.parameters(),lr=LR,weight_decay=0.01)
    scheduler=get_linear_schedule_with_warmup(optimizer,warmup,total_steps)

    best=max(hist["val_token_acc"]) if hist["val_token_acc"] else 0
    patience=0
    for epoch in range(1, EPOCHS+1):
        model.train(); total_loss=0; optimizer.zero_grad()
        for step,batch in enumerate(train_loader):
            input_ids=batch["input_ids"].to(device)
            attention_mask=batch["attention_mask"].to(device)
            labels=batch["labels"].to(device)
            out=model(input_ids=input_ids,attention_mask=attention_mask,labels=labels)
            loss=out.loss/GRAD_ACCUM
            loss.backward()
            total_loss+=out.loss.item()
            if (step+1)%GRAD_ACCUM==0 or (step+1)==len(train_loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
                optimizer.step(); scheduler.step(); optimizer.zero_grad()
        train_loss=total_loss/len(train_loader)
        # val
        model.eval(); val_loss=0; correct=0; total=0
        with torch.no_grad():
            for batch in val_loader:
                input_ids=batch["input_ids"].to(device)
                attention_mask=batch["attention_mask"].to(device)
                labels=batch["labels"].to(device)
                out=model(input_ids=input_ids,attention_mask=attention_mask,labels=labels)
                val_loss+=out.loss.item()
                preds=out.logits.argmax(-1)
                mask=labels!=-100
                correct+=(preds[mask]==labels[mask]).sum().item()
                total+=mask.sum().item()
        val_loss/=max(len(val_loader),1)
        tok_acc=correct/max(total,1)
        hist["train_loss"].append(train_loss)
        hist["val_loss"].append(val_loss)
        hist["val_token_acc"].append(tok_acc)
        hist["bleu1"].append(0); hist["rouge_l"].append(0)
        marker=""
        if tok_acc>best:
            best=tok_acc; patience=0
            model.save_pretrained(OUTPUT_DIR); tok.save_pretrained(OUTPUT_DIR)
            marker=" <-- saved"
        else: patience+=1
        print(f"Epoch {epoch}/{EPOCHS} train {train_loss:.4f} val {val_loss:.4f} tok_acc {tok_acc:.4f}{marker} lr {scheduler.get_last_lr()[0]:.2e}", flush=True)
        Path(OUTPUT_DIR/"history.json").write_text(json.dumps(hist,indent=2))
        if tok_acc>=TARGET:
            print(f"\nTARGET {TARGET:.0%} REACHED at {tok_acc:.4f} (epoch {epoch})")
            break
        if patience>=PATIENCE:
            print(f"Early stop patience {PATIENCE}")
            break
    print(f"Done best {best:.4f}")

if __name__=="__main__":
    main()
