"""Download the in-scope candidate datasets into a scratch directory.

IPv4 is forced (the IPv6 route hangs here). Files land under --dest, which
defaults to the approved temp dir so nothing lands in the repo.
"""
from __future__ import annotations

import argparse
import socket
import sys
from pathlib import Path

_orig = socket.getaddrinfo


def _v4(host, port, family=0, type=0, proto=0, flags=0):  # noqa: A002
    return _orig(host, port, socket.AF_INET, type, proto, flags)


socket.getaddrinfo = _v4

from huggingface_hub import hf_hub_download  # noqa: E402

# (repo, [file paths in repo], local subdir)
PLAN: list[tuple[str, list[str], str]] = [
    (
        "zai-org/humaneval-x",
        [f"data/{lang}/data/humaneval.jsonl" for lang in ("python", "cpp", "java", "js", "go")],
        "humaneval_x",
    ),
    (
        "CohereLabs/lbpp",
        [f"{lang}/test.parquet" for lang in ("python", "cpp", "java", "js", "go", "rust")],
        "lbpp",
    ),
    (
        "shimogerald/interview-coach-dataset",
        ["data/train-00000-of-00001.parquet", "data/validation-00000-of-00001.parquet"],
        "interview_coach",
    ),
    (
        "RISys-Lab/Benchmarks_CyberSec_CyberMetrics",
        ["cyberMetric_10000/test-00000-of-00001.parquet"],
        "cybermetric",
    ),
    (
        "RISys-Lab/Benchmarks_CyberSec_SecEval",
        ["data/test-00000-of-00001.parquet", "data/val-00000-of-00001.parquet"],
        "seceval",
    ),
    (
        "xlangai/spider",
        ["spider/train-00000-of-00001.parquet", "spider/validation-00000-of-00001.parquet"],
        "spider",
    ),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default=r"C:\Users\ASUS\AppData\Local\Temp\opencode\datasets")
    args = ap.parse_args()
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    ok = fail = 0
    for repo, files, sub in PLAN:
        print(f"\n=== {repo} -> {dest / sub} ===", flush=True)
        for f in files:
            try:
                p = hf_hub_download(
                    repo_id=repo,
                    filename=f,
                    repo_type="dataset",
                    local_dir=str(dest / sub),
                )
                mb = Path(p).stat().st_size / 1e6
                print(f"  OK   {mb:8.2f} MB  {f}", flush=True)
                ok += 1
            except Exception as e:  # noqa: BLE001
                print(f"  FAIL {f}  {type(e).__name__}: {str(e)[:160]}", flush=True)
                fail += 1
    print(f"\ndone: {ok} files ok, {fail} failed -> {dest}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
