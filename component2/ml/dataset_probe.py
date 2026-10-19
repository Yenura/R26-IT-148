"""Probe candidate datasets: license, schema, size, sample rows.

Uses the HF datasets-server HTTP API + hub API. No `datasets`/pyarrow needed
for inspection. IPv4 is forced because the IPv6 route hangs in this env.

Usage:
    python ml/dataset_probe.py                 # probe the built-in candidate list
    python ml/dataset_probe.py owner/name ...  # probe specific ids
"""
from __future__ import annotations

import json
import socket
import sys
import textwrap
from typing import Any

# --- force IPv4: getaddrinfo returning an IPv6 address first hangs here -------
_orig_getaddrinfo = socket.getaddrinfo


def _v4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):  # noqa: A002
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


socket.getaddrinfo = _v4_getaddrinfo

import requests  # noqa: E402
from huggingface_hub import HfApi  # noqa: E402

SERVER = "https://datasets-server.huggingface.co"
TIMEOUT = 45

# id -> (why we're looking, the role/type it would serve)
CANDIDATES: dict[str, str] = {
    "olegshulyakov/doocs-leetcode-solutions": "multi-language coding bank (no tests)",
    "zai-org/humaneval-x": "multi-language coding w/ executable tests",
    "CohereLabs/lbpp": "multi-language coding w/ executable tests (test split)",
    "NTU-NLP-sg/xCodeEval": "largest multi-language coding corpus (heavy)",
    "RISys-Lab/Benchmarks_CyberSec_CyberMetrics": "cyber MCQ (10k)",
    "RISys-Lab/Benchmarks_CyberSec_SecEval": "security MCQ (2k, 9 domains)",
    "shimogerald/interview-coach-dataset": "interview Q&A (Descriptive)",
    "Vineeshsuiii/Software_Engineering_interview_datasets": "SWE interview Q&A (Descriptive)",
    "xlangai/spider": "text-to-SQL (DBA / Data Engineer)",
}

_api = HfApi()


def _get(path: str, **params: Any) -> dict | None:
    try:
        r = requests.get(f"{SERVER}/{path}", params=params, timeout=TIMEOUT)
    except Exception as e:  # noqa: BLE001
        return {"_error": f"{type(e).__name__}: {e}"}
    if r.status_code != 200:
        return {"_error": f"HTTP {r.status_code}: {r.text[:200]}"}
    try:
        return r.json()
    except Exception as e:  # noqa: BLE001
        return {"_error": f"bad json: {e}"}


def _license(ds_id: str) -> str:
    try:
        info = _api.dataset_info(ds_id, timeout=TIMEOUT)
    except Exception as e:  # noqa: BLE001
        return f"<lookup failed: {type(e).__name__}>"
    tags = getattr(info, "tags", None) or []
    lic = [t.split(":", 1)[1] for t in tags if t.startswith("license:")]
    return ",".join(lic) if lic else "<none declared>"


def probe(ds_id: str, why: str = "") -> dict:
    out: dict[str, Any] = {"id": ds_id, "why": why, "license": _license(ds_id)}

    splits = _get("splits", dataset=ds_id)
    if not splits or "_error" in splits:
        out["error"] = (splits or {}).get("_error", "no splits response")
        return out

    out["configs"] = [
        {"config": s["config"], "split": s["split"], "num_rows": s.get("num_examples")}
        for s in splits.get("splits", [])
    ]

    # first-rows gives the schema (features) + 100 sample rows for a split
    if out["configs"]:
        c = out["configs"][0]
        fr = _get("first-rows", dataset=ds_id, config=c["config"], split=c["split"])
        if fr and "_error" not in fr:
            feats = fr.get("features", [])
            out["features"] = [
                {"name": f.get("name"), "type": _fmt_type(f)} for f in feats
            ]
            rows = fr.get("rows", [])
            out["sample"] = [r.get("row") for r in rows[:3]]

        size = _get("size", dataset=ds_id)
        if size and "_error" not in size:
            out["bytes"] = size.get("size", {}).get("dataset", {}).get("num_bytes_original_files")

    return out


def _fmt_type(f: dict) -> str:
    t = f.get("type", {})
    if isinstance(t, dict):
        inner = t.get("type")
        if inner == "list":
            return f"list<{t.get('feature', {}).get('type', '?')}>"
        if inner == "struct":
            return "struct(" + ",".join(x.get("name", "?") for x in t.get("fields", [])) + ")"
        return inner or str(t)
    return str(t)


def _wrap(s: Any, indent: str = "      ", width: int = 96, maxlines: int = 4) -> str:
    if not isinstance(s, str):
        s = json.dumps(s, ensure_ascii=False)
    s = s.replace("\n", "\\n")
    lines = textwrap.wrap(s, width=width, break_long_words=True) or [""]
    if len(lines) > maxlines:
        lines = lines[:maxlines] + ["...(+%d chars)" % (len(s) - sum(len(l) for l in lines))]
    return ("\n" + indent).join(lines)


def main(argv: list[str]) -> int:
    targets = {a: CANDIDATES.get(a, "") for a in argv} if argv else CANDIDATES
    results = {}
    for ds_id, why in targets.items():
        print(f"\n=== {ds_id} ===")
        info = probe(ds_id, why)
        results[ds_id] = info
        print(f"  license : {info.get('license')}")
        if info.get("error"):
            print(f"  ERROR   : {info['error']}")
            continue
        print(f"  bytes   : {info.get('bytes')}")
        for c in info.get("configs", []):
            print(f"  split   : {c['config']} / {c['split']}  rows={c['num_rows']}")
        print(f"  features: {json.dumps(info.get('features'), ensure_ascii=False)}")
        for i, row in enumerate(info.get("sample", [])):
            print(f"  row[{i}]  : {_wrap(row)}")

    out_path = sys.argv[0].replace("dataset_probe.py", "dataset_probe_results.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
