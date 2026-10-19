"""Empirically check the Coding test_cases / sandbox contract.

Question: the bank stores inputs as JSON strings (e.g. "nums": "[2,7,11,15]").
The sandbox injects `repr(v)` for strings and the raw value otherwise.  So does
the existing bank's Two Sum actually grade a correct solution as correct?
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from routers.interview import _is_py_literal, _output_matches, _run_code_in_sandbox  # noqa: E402

BANK = Path(__file__).resolve().parents[1] / "models" / "question_bank.json"
items = json.loads(BANK.read_text(encoding="utf-8"))
lc1 = next(i for i in items if i["id"] == "LC_1")
tc = lc1["test_cases"][0]
inp = tc["input"]
print("bank input      :", inp)
print("all py-literal? :", all(_is_py_literal(v) for v in inp.values()))
print("expected output :", tc["expected_output"])

# A correct Two Sum that treats nums as a list.
correct_list = """
seen = {}
for i, n in enumerate(nums):
    if target - n in seen:
        print([seen[target - n], i])
        break
    seen[n] = i
"""

# A solution that treats nums as the *string* the current injection produces.
correct_string = """
import ast
arr = ast.literal_eval(nums) if isinstance(nums, str) else nums
seen = {}
for i, n in enumerate(arr):
    if target - n in seen:
        print([seen[target - n], i])
        break
    seen[n] = i
"""

for label, code in (("treat-nums-as-list", correct_list), ("treat-nums-as-string", correct_string)):
    out = _run_code_in_sandbox(code, inp)
    print(f"{label:22s} stdout={out!r}  match={_output_matches(out, tc['expected_output'])}")

# What does the injection actually produce?
inject = "".join(f"{k} = {repr(v) if isinstance(v, str) else v}\n" for k, v in inp.items())
print("\ninjected source  :", inject.strip().replace("\n", " | "))

# Now show it with a real list value (what we would emit from humaneval-x).
inp2 = {"nums": [2, 7, 11, 15], "target": 9}
inject2 = "".join(f"{k} = {repr(v) if isinstance(v, str) else v}\n" for k, v in inp2.items())
print("injected (list)  :", inject2.strip().replace("\n", " | "))
print("list py-literal? :", all(_is_py_literal(v) for v in inp2.values()))
print("list solution    :", repr(_run_code_in_sandbox(correct_list, inp2)),
      "match =", _output_matches(_run_code_in_sandbox(correct_list, inp2), "9" if False else "[0, 1]"))
