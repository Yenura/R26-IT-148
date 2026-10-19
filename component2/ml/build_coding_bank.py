"""Build print-based Coding bank entries from external datasets.

Converts function-call-style coding problems into the bank's print-based
schema, where a candidate is given named input variables and prints the
result:

    {
      "id": "HEX_0", "question_type": "Coding", "language": "Python",
      "question_text": "<problem>\\n\\nWrite a Python script ... prints the result.",
      "test_cases": [{"input": {"numbers": "[1.0, 2.0]"}, "expected_output": "False"}]
    }

`input` values are stored as Python-literal *source* strings (repr), which is
the convention the curated bank already uses (see ml/probe_coding_contract.py).

Every generated question is verified before it is written: the shipped
reference solution must pass 100% of its own test cases through the real
sandbox (`routers.interview._run_code_in_sandbox`).

Sources (both commercial-friendly):
  * humaneval-x / python  -- apache-2.0
  * lbpp / python         -- apache-2.0

Usage:
    python ml/build_coding_bank.py --dataset all
"""
from __future__ import annotations

import argparse
import ast
import base64
import contextlib
import copy
import json
import os
import pickle
import re
import sys
import tempfile
import zlib
from pathlib import Path

_SCRATCH = Path(r"C:\Users\ASUS\AppData\Local\Temp\opencode\datasets")
_MODELS = Path(__file__).resolve().parents[1] / "models"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from routers.interview import _output_matches, _run_code_in_sandbox  # noqa: E402

MAX_TEST_CASES = 5
BOILERPLATE = (
    "Write a Python script that solves the problem using the provided input "
    "variable(s): {vars}, and prints the result."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _expected_text(value) -> str:
    """Text a `print(value)` would emit for the expected result."""
    if isinstance(value, str):
        return value
    return repr(value)


def _input_source(value) -> str | None:
    """Repr of a value, only if it round-trips as a Python literal."""
    src = repr(value)
    try:
        ast.literal_eval(src)
    except (ValueError, SyntaxError):
        return None
    return src


def _parse_signature(*snippets: str) -> tuple[str, list[str]]:
    """(function_name, positional_param_names) from the first parseable snippet.

    ``declaration`` is often a bare signature with no body, so it cannot be
    parsed alone; the prompt/completion carries the body.  We try each snippet
    and, as a last resort, append a ``pass`` body.
    """
    last_err: Exception | None = None
    for snippet in snippets:
        for candidate in (snippet, snippet.rstrip() + "\n    pass\n"):
            try:
                tree = ast.parse(candidate)
            except SyntaxError as e:
                last_err = e
                continue
            fn = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)), None)
            if fn is not None:
                return fn.name, [a.arg for a in fn.args.args]
    raise SyntaxError(f"no function signature found: {last_err}")


def _docstring_of(source: str) -> str:
    """The first function docstring in `source`, or the whole text as fallback."""
    try:
        tree = ast.parse(source)
        fn = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)), None)
        for node in (fn.body if fn else []):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    return node.value.value.strip()
    except SyntaxError:
        pass
    return source.strip()


def _sandbox_reference(source: str, fn_name: str, params: list[str]) -> str:
    """A reference solution that runs inside the sandbox.

    The sandbox blocks ``typing`` for candidate code by default, so we drop
    ``typing`` imports and strip annotations from the signature -- neither is
    needed to compute the result.
    """
    src = re.sub(
        r"^\s*(from\s+typing\s+import\s+.*|import\s+typing)\s*$", "", source, flags=re.MULTILINE
    )
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if line.lstrip().startswith(f"def {fn_name}("):
            indent = line[: len(line) - len(line.lstrip())]
            lines[i] = f"{indent}def {fn_name}({', '.join(params)}):"
            break
    return f"{chr(10).join(lines)}\nprint({fn_name}({', '.join(params)}))\n"


def _cases_from_calls(recorded, params: list[str]) -> list[dict]:
    """Build test cases from captured (args, result) pairs.

    Cases with no injectable input are dropped: with nothing to inject there is
    no variable to reason about, so the expected output is a constant (trivially
    hardcodable) and the ``any(_is_py_literal ...)`` gate treats the case as
    unverifiable.
    """
    cases: list[dict] = []
    seen: set[str] = set()
    for args, result in recorded:
        if len(args) != len(params) or not args:
            continue
        inp: dict[str, str] = {}
        if any(_input_source(v) is None for v in args):
            continue
        for name, value in zip(params, args):
            inp[name] = _input_source(value)
        key = json.dumps([inp, _expected_text(result)], sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        cases.append({"input": inp, "expected_output": _expected_text(result)})
        if len(cases) >= MAX_TEST_CASES:
            break
    return cases


def _capture_calls(full_source: str, fn_name: str, test_code: str):
    """Run `test_code` with `fn_name` wrapped, returning [(args_tuple, result)]."""
    ns: dict = {}
    exec(full_source, ns)  # noqa: S102 - local dataset, trusted for this build
    if fn_name not in ns:
        raise KeyError(f"{fn_name} not defined by reference solution")
    original = ns[fn_name]
    recorded: list[tuple[tuple, object]] = []

    def wrapper(*args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        # Snapshot before the call: in-place solutions (e.g. lst.remove) would
        # otherwise rewrite the recorded input to its post-call state.
        snapshot = copy.deepcopy(args)
        result = original(*args, **kwargs)
        recorded.append((snapshot, result))
        return result

    ns[fn_name] = wrapper
    exec(test_code, ns)  # noqa: S102
    return recorded


def _make_question(qid: str, description: str, params: list[str], topic: str,
                   cases: list[dict], reference: str) -> dict:
    import inspect

    description = inspect.cleandoc(description) if description else ""
    return {
        "id": qid,
        "question_type": "Coding",
        "difficulty": "Medium",
        "category": "Algorithms",
        "topic": topic,
        "question_text": f"{description}\n\n{BOILERPLATE.format(vars=', '.join(params))}",
        "language": "Python",
        "time_limit": 900,
        "test_cases": cases,
        "_reference": reference,
    }


# ---------------------------------------------------------------------------
# humaneval-x / python  (apache-2.0)
# ---------------------------------------------------------------------------
def convert_humaneval_x() -> tuple[list[dict], dict]:
    path = _SCRATCH / "humaneval_x" / "data" / "python" / "data" / "humaneval.jsonl"
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    stats = {"source": "humaneval-x/python", "rows": len(rows), "ok": 0, "skipped": []}
    out: list[dict] = []

    for row in rows:
        task = row["task_id"].split("/")[-1]
        try:
            fn_name, params = _parse_signature(row["prompt"], row["declaration"])
            full = row["prompt"] + row["canonical_solution"]
            recorded = _capture_calls(full, fn_name, row["test"])
        except Exception as e:  # noqa: BLE001
            stats["skipped"].append((task, f"{type(e).__name__}: {e}"))
            continue

        cases = _cases_from_calls(recorded, params)
        if not cases:
            stats["skipped"].append((task, "no convertible test cases"))
            continue

        out.append(_make_question(
            f"HEX_{task}", _docstring_of(row["prompt"]), params,
            fn_name.replace("_", " "), cases,
            _sandbox_reference(full, fn_name, params),
        ))
        stats["ok"] += 1
    return out, stats


# ---------------------------------------------------------------------------
# lbpp / python  (apache-2.0)
# ---------------------------------------------------------------------------
class _StrOnlyUnpickler(pickle.Unpickler):
    """Unpickler that refuses any GLOBAL opcode (only plain data)."""

    def find_class(self, module, name):  # noqa: ANN001
        raise pickle.UnpicklingError(f"refusing global {module}.{name}")


def _lbpp_decode(value: str):
    """Decode an lbpp field: base64 -> zlib -> pickle -> JSON.

    The pickled object is itself a JSON document (a string, or a list for
    ``test_list``), so it needs one more parse.
    """
    raw = base64.b64decode(value)
    try:
        data = zlib.decompress(raw, 15)
    except zlib.error:
        data = zlib.decompress(raw)
    import io

    obj = _StrOnlyUnpickler(io.BytesIO(data)).load()
    return json.loads(obj) if isinstance(obj, str) else obj


def _cases_from_asserts(asserts: list[str], params: list[str], fn_name: str) -> list[dict]:
    """Kept for reference; lbpp now uses exec-based capture (see convert_lbpp)."""
    raise NotImplementedError


def convert_lbpp() -> tuple[list[dict], dict]:
    import inspect

    import pandas as pd

    df = pd.read_parquet(_SCRATCH / "lbpp" / "python" / "test.parquet")
    stats = {"source": "lbpp/python", "rows": len(df), "ok": 0, "skipped": []}
    out: list[dict] = []

    for _, row in df.iterrows():
        task = str(row["task_id"]).split("/")[-1]
        try:
            comp = _lbpp_decode(row["completion"])
            asserts = _lbpp_decode(row["test_list"])
            test_code = "\n".join(asserts) if isinstance(asserts, list) else str(asserts)
            target, params = _lbpp_target(comp, test_code, inspect)
            recorded = _capture_calls(comp, target, test_code)
        except Exception as e:  # noqa: BLE001
            stats["skipped"].append((task, f"{type(e).__name__}: {e}"))
            continue

        cases = _cases_from_calls(recorded, params)
        if not cases:
            stats["skipped"].append((task, "no convertible test cases"))
            continue

        out.append(_make_question(
            f"LBP_{task}", str(row["instruction"]).strip(), params,
            target.replace("_", " "), cases,
            _sandbox_reference(comp, target, params),
        ))
        stats["ok"] += 1
    return out, stats


def _lbpp_target(comp: str, test_code: str, inspect) -> tuple[str, list[str]]:
    """(function the tests actually call, its parameter names).

    lbpp's ``completion`` may define several helpers and the tests sometimes
    call a differently-named entry point, so we execute it and pick the
    function that appears as a call in the test code.
    """
    ns: dict = {}
    exec(comp, ns)  # noqa: S102 - local dataset
    candidates = [n for n, v in ns.items()
                  if callable(v) and not isinstance(v, type) and not n.startswith("_")]
    called = [n for n in candidates if re.search(rf"\b{re.escape(n)}\s*\(", test_code)]
    if not called:
        raise KeyError("no function from completion is called by the tests")
    name = called[-1]
    params = [p for p in inspect.signature(ns[name]).parameters]
    return name, params


# ---------------------------------------------------------------------------
# Verification through the real sandbox
# ---------------------------------------------------------------------------
def verify(questions: list[dict]) -> tuple[list[dict], list[tuple[str, str]]]:
    """Keep only questions whose reference solution passes every test case."""
    kept: list[dict] = []
    failures: list[tuple[str, str]] = []
    for q in questions:
        ref = q.pop("_reference")
        passed = 0
        detail = ""
        for tc in q["test_cases"]:
            # Pass the stored values through untouched: they are Python-literal
            # source, and _run_code_in_sandbox already interprets them.
            out = _run_code_in_sandbox(ref, tc["input"])
            if _output_matches(out, tc["expected_output"]):
                passed += 1
            elif not detail:
                detail = f"in={tc['input']} want={tc['expected_output']!r} got={out!r}"
        if passed == len(q["test_cases"]):
            kept.append(q)
        else:
            failures.append((q["id"], f"{passed}/{len(q['test_cases'])} pass; {detail}"))
    return kept, failures


CONVERTERS = {"humaneval-x": convert_humaneval_x, "lbpp": convert_lbpp}


@contextlib.contextmanager
def _scratch_cwd():
    """Run the build in a temp cwd.

    Some dataset reference solutions read or write files relative to the
    process cwd (lbpp's file-I/O exercises), which would litter the repo.
    """
    previous = os.getcwd()
    with tempfile.TemporaryDirectory(prefix="qgbank_") as tmp:
        os.chdir(tmp)
        try:
            yield
        finally:
            os.chdir(previous)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="all", choices=["humaneval-x", "lbpp", "all"])
    ap.add_argument("--out", default=str(_MODELS / "coding_bank_external.json"))
    args = ap.parse_args()

    names = list(CONVERTERS) if args.dataset == "all" else [args.dataset]
    all_q: list[dict] = []
    with _scratch_cwd():
        for name in names:
            questions, stats = CONVERTERS[name]()
            print(f"[{stats['source']}] rows={stats['rows']} converted={stats['ok']} "
                  f"skipped={len(stats['skipped'])}")
            for task, why in stats["skipped"][:6]:
                print(f"   skip {task}: {why}")
            all_q.extend(questions)

        kept, failures = verify(all_q)
    print(f"\nverification: {len(kept)}/{len(all_q)} questions pass 100% of their tests")
    for qid, why in failures[:12]:
        print(f"   FAIL {qid}: {why}")

    Path(args.out).write_text(json.dumps(kept, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {len(kept)} questions -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
