"""Inspect the downloaded candidate datasets: rows, schema, sample, fit.

Reads the scratch dir populated by ml/dataset_download.py and prints a
fit-oriented summary (row counts, field shapes, and whether the coding
test format can be adapted to the print-based sandbox in
backend/routers/interview.py).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

# Windows console default encoding can't print some dataset glyphs (e.g. U+2011)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

DEST = Path(r"C:\Users\ASUS\AppData\Local\Temp\opencode\datasets")


def _clip(s, n: int = 220) -> str:
    s = str(s).replace("\n", "\\n")
    return s if len(s) <= n else s[:n] + f"...(+{len(s) - n})"


def _head(t: str) -> None:
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def humaneval_x() -> None:
    _head("HUMANEVAL-X  (apache-2.0) -- multi-language coding w/ executable tests")
    for lang in ("python", "cpp", "java", "js", "go"):
        p = DEST / "humaneval_x" / "data" / lang / "data" / "humaneval.jsonl"
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        print(f"\n  [{lang}] rows={len(rows)}  fields={list(rows[0].keys())}")
        r = rows[0]
        print(f"    task_id    : {r['task_id']}")
        print(f"    prompt     : {_clip(r['prompt'], 160)}")
        print(f"    declaration: {_clip(r.get('declaration', ''), 120)}")
        print(f"    test       : {_clip(r['test'], 200)}")
        # how many tests are assert-style (function-call) vs stdin/stdout
        asserts = sum("assert" in x["test"] for x in rows)
        print(f"    assert-style tests: {asserts}/{len(rows)}")


def lbpp() -> None:
    _head("LBPP  (apache-2.0) -- multi-language coding, test split only")
    for lang in ("python", "cpp", "java", "js", "go", "rust"):
        df = pd.read_parquet(DEST / "lbpp" / lang / "test.parquet")
        print(f"\n  [{lang}] rows={len(df)}  fields={list(df.columns)}")
        r = df.iloc[0]
        print(f"    task_id    : {r['task_id']}")
        print(f"    instruction: {_clip(r['instruction'], 200)}")
        print(f"    signature  : {_clip(r.get('signature', ''), 120)}")
        print(f"    test_list  : {_clip(r['test_list'], 200)}")
        print(f"    categories : {r.get('categories')}")


def interview_coach() -> None:
    _head("INTERVIEW-COACH  (MIT) -- interview Q&A for Descriptive")
    for split in ("train", "validation"):
        df = pd.read_parquet(DEST / "interview_coach" / f"data/{split}-00000-of-00001.parquet")
        print(f"\n  [{split}] rows={len(df)}  fields={list(df.columns)}")
        for i in range(min(2, len(df))):
            msgs = df.iloc[i]["messages"]
            if hasattr(msgs, "tolist"):
                msgs = msgs.tolist()
            q = next((m["content"] for m in msgs if m["role"] == "user"), "")
            a = next((m["content"] for m in msgs if m["role"] == "assistant"), "")
            print(f"    Q{i}: {_clip(q, 150)}")
            print(f"    A{i}: {_clip(a, 150)}")


def cybermetric() -> None:
    _head("CYBERMETRIC  (license: other/research) -- cyber MCQ")
    df = pd.read_parquet(DEST / "cybermetric" / "cyberMetric_10000/test-00000-of-00001.parquet")
    print(f"\n  rows={len(df)}  fields={list(df.columns)}")
    print(f"  solution values: {Counter(df['solution']).most_common()}")
    for i in range(2):
        r = df.iloc[i]
        print(f"    Q: {_clip(r['question'], 130)}")
        print(f"       {dict(r['answers'])} -> {r['solution']}")


def seceval() -> None:
    _head("SECEVAL  (CC-BY-NC-SA-4.0) -- security MCQ (NON-COMMERCIAL)")
    df = pd.read_parquet(DEST / "seceval" / "data/test-00000-of-00001.parquet")
    print(f"\n  rows={len(df)}  len(answer): {Counter(len(str(a)) for a in df['answer'])}")
    print(f"  (len>1 == multi-select, incompatible with single-answer MCQ)")
    topics = Counter(t for ts in df["topics"] for t in (ts.tolist() if hasattr(ts, "tolist") else ts))
    print(f"  topics: {topics.most_common(10)}")


def spider() -> None:
    _head("SPIDER  (CC-BY-SA-4.0) -- text-to-SQL")
    df = pd.read_parquet(DEST / "spider" / "spider/train-00000-of-00001.parquet")
    print(f"\n  rows={len(df)}  fields={list(df.columns)}")
    print(f"  distinct db_id: {df['db_id'].nunique()}")
    for i in range(2):
        r = df.iloc[i]
        print(f"    Q: {_clip(r['question'], 130)}")
        print(f"    SQL: {_clip(r['query'], 130)}")


if __name__ == "__main__":
    for fn in (humaneval_x, lbpp, interview_coach, cybermetric, seceval, spider):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            print(f"\n!! {fn.__name__} failed: {type(e).__name__}: {e}")
