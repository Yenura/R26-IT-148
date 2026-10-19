"""
Diagnose why the Coding question type collapses in the T5 QG model.

Checks, per question type:
  1. Row counts (is Coding under-represented?)
  2. <unk> rate on targets (tokenizer coverage of code symbols/newlines)
  3. Which characters become <unk> (top offenders)
  4. Source/target token-length percentiles and % truncated at your limits

Usage (from component2/):
  python ml/diagnose_coding_targets.py \
      --data models/qg_dataset_v2.json --split train \
      --tokenizer models/t5_qg \
      --type-col type --src-col input --tgt-col output \
      --max-src 64 --max-tgt 128

Accepts .jsonl, .csv, or the repo's JSON dataset ({train:[...], val:[...]};
pick a split with --split). Column names default to the v2 dataset
(type/input/output) and the limits default to the train_t5_qg_v2 settings
(max-src 64, max-tgt 128).
"""
import argparse
import collections
import json

import numpy as np
from transformers import AutoTokenizer


def load_rows(path, split=None):
    if path.endswith(".csv"):
        import csv
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    if path.endswith(".json"):
        with open(path, encoding="utf-8") as f:
            obj = json.load(f)
        if isinstance(obj, dict) and any(isinstance(v, list) for v in obj.values()):
            if split is None:
                split = next(k for k, v in obj.items() if isinstance(v, list))
            rows = obj.get(split)
            if not isinstance(rows, list):
                raise SystemExit(f"split {split!r} not in {path}; have {sorted(obj)}")
            print(f"(dataset split: {split!r})")
            return rows
        return obj
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def pct(a, q):
    return float(np.percentile(a, q)) if len(a) else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--split", default=None)
    ap.add_argument("--type-col", default="type")
    ap.add_argument("--src-col", default="input")
    ap.add_argument("--tgt-col", default="output")
    ap.add_argument("--max-src", type=int, default=64)
    ap.add_argument("--max-tgt", type=int, default=128)
    args = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(args.tokenizer)
    unk_id = tok.unk_token_id
    rows = load_rows(args.data, args.split)
    print(f"Loaded {len(rows)} rows from {args.data}; unk_id={unk_id}\n")

    by_type = collections.defaultdict(list)
    for r in rows:
        by_type[str(r.get(args.type_col, "?")).lower()].append(r)
    grand_total = sum(len(v) for v in by_type.values())

    for qtype, items in sorted(by_type.items(), key=lambda kv: -len(kv[1])):
        src_lens, tgt_lens = [], []
        unk_tokens = total_tokens = 0
        bad_chars = collections.Counter()
        rows_with_unk = 0

        for r in items:
            src, tgt = str(r[args.src_col]), str(r[args.tgt_col])
            s_ids = tok(src, add_special_tokens=True)["input_ids"]
            t_ids = tok(tgt, add_special_tokens=True)["input_ids"]
            src_lens.append(len(s_ids))
            tgt_lens.append(len(t_ids))

            u = sum(1 for i in t_ids if i == unk_id)
            unk_tokens += u
            total_tokens += len(t_ids)
            rows_with_unk += u > 0

            # Per-character check: which chars alone tokenize to unk
            for ch in set(tgt):
                if ch.isspace() and ch != "\n":
                    continue
                ids = tok(ch, add_special_tokens=False)["input_ids"]
                if ids and all(i == unk_id for i in ids):
                    bad_chars[repr(ch)] += tgt.count(ch)
            if "\n" in tgt:
                bad_chars["'\\n' (present in target)"] += tgt.count("\n")

        n = len(items)
        print(f"=== {qtype}  (n={n}, {n/grand_total:.0%} of rows) ===")
        print(f"  <unk> rate on targets : {unk_tokens / max(total_tokens, 1):.2%} "
              f"({rows_with_unk}/{n} rows contain >=1 unk)")
        print(f"  target tokens p50/p90/max : {pct(tgt_lens, 50):.0f} / "
              f"{pct(tgt_lens, 90):.0f} / {max(tgt_lens)}"
              f"   truncated at {args.max_tgt}: "
              f"{np.mean(np.array(tgt_lens) > args.max_tgt):.1%}")
        print(f"  source tokens p50/p90/max : {pct(src_lens, 50):.0f} / "
              f"{pct(src_lens, 90):.0f} / {max(src_lens)}"
              f"   truncated at {args.max_src}: "
              f"{np.mean(np.array(src_lens) > args.max_src):.1%}")
        if bad_chars:
            top = ", ".join(f"{c}x{k}" for c, k in bad_chars.most_common(12))
            print(f"  chars lost to <unk>/newline: {top}")
        print()

    print("How to read this:")
    print("  - High <unk> rate or many lost chars on Coding only -> tokenizer fix")
    print("    (train SentencePiece with code symbols, or escape { } < \\n).")
    print("  - Coding truncated % >> MCQ/Descriptive -> raise max-tgt or shorten targets.")
    print("  - Low row count for Coding -> oversample/augment before anything else.")


if __name__ == "__main__":
    main()
