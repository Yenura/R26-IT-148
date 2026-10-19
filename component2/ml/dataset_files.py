"""List downloadable files (name + size) for candidate dataset repos."""
from __future__ import annotations

import socket

_orig = socket.getaddrinfo


def _v4(host, port, family=0, type=0, proto=0, flags=0):  # noqa: A002
    return _orig(host, port, socket.AF_INET, type, proto, flags)


socket.getaddrinfo = _v4

from huggingface_hub import HfApi  # noqa: E402

REPOS = [
    "zai-org/humaneval-x",
    "CohereLabs/lbpp",
    "shimogerald/interview-coach-dataset",
    "RISys-Lab/Benchmarks_CyberSec_CyberMetrics",
    "RISys-Lab/Benchmarks_CyberSec_SecEval",
    "xlangai/spider",
    "olegshulyakov/doocs-leetcode-solutions",
]

api = HfApi()
for repo in REPOS:
    print(f"\n=== {repo} ===")
    try:
        files = api.list_repo_files(repo, repo_type="dataset")
    except Exception as e:  # noqa: BLE001
        print("  list failed:", type(e).__name__, e)
        continue
    for f in files:
        if f.startswith("."):
            continue
        try:
            path = api.hf_hub_url(repo, f, repo_type="dataset")
            meta = api.get_hf_file_metadata(path, timeout=30)
            mb = (meta.size or 0) / 1e6
            print(f"  {mb:8.2f} MB  {f}")
        except Exception as e:  # noqa: BLE001
            print(f"       ?  {f}   ({type(e).__name__})")
