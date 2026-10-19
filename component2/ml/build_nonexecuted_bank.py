"""Build the non-executable Coding bank (`component2/models/coding_bank_nonexecuted.json`).

Some interview coding questions cannot be graded by running code: the sandbox
only speaks Python, yet roles need Java / C++ / JavaScript / Go / Rust.  This
script produces questions that are graded by *comparing text* -- a missing line,
an expected stdout, or a chosen fix -- so no execution is ever involved.

Three formats:

* ``Complete Function`` -- dataset ground truth.  One line is lifted out of a
  canonical solution (humaneval-x for python/cpp/java/js/go, lbpp for rust) and
  the candidate must reproduce it.  The answer is therefore a verbatim line of
  a reference solution, so it is right by construction.
* ``Predict Output`` -- authored by construction.  Short deterministic snippets
  whose stdout is stated up front.
* ``Find the Bug`` -- authored by construction.  A single line is wanted, with
  distractors that are wrong for a reason we can name.

Usage (from ``component2/``):
    python ml/build_nonexecuted_bank.py
    python ml/build_nonexecuted_bank.py --out models/coding_bank_nonexecuted.json
    python ml/build_nonexecuted_bank.py --validate          # validate the file only
    python ml/build_nonexecuted_bank.py --runtime-verify    # dev: run Predict Output
"""
from __future__ import annotations

import argparse
import ast
import base64
import io
import json
import pickle
import random
import re
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

_SCRATCH = Path(r"C:\Users\ASUS\AppData\Local\Temp\opencode\datasets")
_MODELS = Path(__file__).resolve().parents[1] / "models"

LANGS = ["Python", "Java", "C++", "JavaScript", "Go", "Rust"]
LANG_TAG = {
    "Python": "PY",
    "Java": "JAVA",
    "C++": "CPP",
    "JavaScript": "JS",
    "Go": "GO",
    "Rust": "RUST",
}
MARKER = "# ??? MISSING LINE ???"
MARKER_CLIKE = "// ??? MISSING LINE ???"
FORMATS = ("Complete Function", "Predict Output", "Find the Bug")

MAX_PER_LANG = 50          # cap on dataset-derived Complete Function questions
MIN_ANSWER_CHARS = 6       # "not trivially short"

HUMANEVAL_DIRS = {
    "Python": "python",
    "C++": "cpp",
    "Java": "java",
    "JavaScript": "js",
    "Go": "go",
}


def normalize_code(line: str) -> str:
    return re.sub(r"\s+", "", line).lower().rstrip(";")


def normalize_output(text: str) -> str:
    return text.strip()


def marker_for(language: str) -> str:
    return MARKER if language == "Python" else MARKER_CLIKE


def leading_ws(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]


# ---------------------------------------------------------------------------
# Source loading
# ---------------------------------------------------------------------------
def load_humaneval(language: str) -> list[dict]:
    """Rows for one humaneval-x language: keys prompt/canonical_solution/declaration."""
    sub = HUMANEVAL_DIRS[language]
    path = _SCRATCH / "humaneval_x" / "data" / sub / "data" / "humaneval.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    out: list[dict] = []
    for row in rows:
        out.append(
            {
                "source": f"humaneval-x/{sub}",
                "task": row["task_id"].split("/")[-1],
                "prompt": row["prompt"],
                "body": row["canonical_solution"],
                "declaration": row.get("declaration", ""),
                "statement": None,
            }
        )
    return out


class _StrOnlyUnpickler(pickle.Unpickler):
    """Unpickler refusing every GLOBAL opcode (plain data only)."""

    def find_class(self, module, name):  # noqa: ANN001
        raise pickle.UnpicklingError(f"refusing global {module}.{name}")


def lbpp_decode(value: str):
    raw = base64.b64decode(value)
    try:
        data = zlib.decompress(raw, 15)
    except zlib.error:
        data = zlib.decompress(raw)
    obj = _StrOnlyUnpickler(io.BytesIO(data)).load()
    return json.loads(obj) if isinstance(obj, str) else obj


def load_lbpp(language: str) -> list[dict]:
    """Rows for one lbpp language: keys prompt(empty)/body/statement/signature."""
    import pandas as pd

    sub = {"Python": "python", "C++": "cpp", "Java": "java",
           "JavaScript": "js", "Go": "go", "Rust": "rust"}[language]
    df = pd.read_parquet(_SCRATCH / "lbpp" / sub / "test.parquet")
    out: list[dict] = []
    for _, row in df.iterrows():
        try:
            completion = lbpp_decode(row["completion"])
        except Exception:  # noqa: BLE001
            continue
        out.append(
            {
                "source": f"lbpp/{sub}",
                "task": str(row["task_id"]).split("/")[-1],
                "prompt": "",
                "body": completion,
                "declaration": str(row.get("signature", "") or ""),
                "statement": str(row["instruction"]).strip(),
                "title": str(row.get("title", "") or ""),
            }
        )
    return out


# ---------------------------------------------------------------------------
# Problem statements
# ---------------------------------------------------------------------------
def _dedent_block(text: str) -> str:
    lines = text.strip("\n").split("\n")
    stripped = [ln.strip() for ln in lines]
    while stripped and not stripped[0]:
        stripped.pop(0)
    while stripped and not stripped[-1]:
        stripped.pop()
    return "\n".join(stripped)


def _strip_star_lines(block: str) -> str:
    lines = []
    for ln in block.split("\n"):
        ln = re.sub(r"^\s*\*+\s?", "", ln)
        lines.append(ln)
    return "\n".join(lines)


def statement_from_prompt(language: str, prompt: str) -> str | None:
    """The human-readable problem statement embedded in a humaneval-x prompt."""
    if language == "Python":
        try:
            tree = ast.parse(prompt)
        except SyntaxError:
            return None
        fn = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)), None)
        if fn and fn.body:
            first = fn.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                if isinstance(first.value.value, str):
                    return _dedent_block(first.value.value)
        return None

    if language in ("C++", "JavaScript"):
        m = re.search(r"/\*(.*?)\*/", prompt, re.DOTALL)
        if not m:
            return None
        return _dedent_block(_strip_star_lines(m.group(1)))

    if language == "Java":
        m = re.search(r"/\*\*(.*?)\*/", prompt, re.DOTALL)
        if not m:
            m = re.search(r"/\*(.*?)\*/", prompt, re.DOTALL)
        if not m:
            return None
        return _dedent_block(_strip_star_lines(m.group(1)))

    if language == "Go":
        # longest run of consecutive `//` lines
        best: list[str] = []
        run: list[str] = []
        for ln in prompt.split("\n"):
            if ln.lstrip().startswith("//"):
                run.append(re.sub(r"^\s*//\s?", "", ln))
            else:
                if len(run) > len(best):
                    best = run
                run = []
        if len(run) > len(best):
            best = run
        if not best:
            return None
        return _dedent_block("\n".join(best))

    return None


# ---------------------------------------------------------------------------
# Line classification (for dataset-derived "Complete Function")
# ---------------------------------------------------------------------------
def _balance(line: str, language: str) -> tuple[int, int]:
    """(brace_delta, paren_delta) for a line, ignoring strings and comments."""
    text = _code_only(line, language)
    braces = text.count("{") - text.count("}")
    parens = (text.count("(") - text.count(")")) + (text.count("[") - text.count("]"))
    return braces, parens


def _classify_brace_line(stripped: str, language: str) -> str:
    """Rough kind of the block a `{` on this line opens."""
    if language == "JavaScript":
        if "=>" in stripped or re.search(r"\bfunction\b", stripped):
            return "fn"
    if language == "Rust":
        if re.search(r"\bfn\b", stripped):
            return "fn"
    if language == "Go":
        if re.search(r"\bfunc\b", stripped):
            return "fn"
    if language in ("Java", "C++"):
        if "(" in stripped and ")" in stripped and not re.match(
            r"^\s*(if|for|while|switch|catch|else|do|try)\b", stripped
        ):
            return "fn"
    if re.search(r"\b(class|struct|interface|enum|impl|trait|package|namespace)\b", stripped):
        return "type"
    return "block"


def _is_unbraced_header(prev: str) -> bool:
    return bool(re.match(r"^(if|for|while|else|do)\b", prev)) and not prev.endswith("{") and not prev.endswith(";")


def _code_only(line: str, language: str) -> str:
    """The line with string literals and trailing `//` comments removed."""
    out: list[str] = []
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == "/" and i + 1 < n and line[i + 1] == "/":
            break
        if c == '"' or c == "`":
            i += 1
            while i < n and line[i] != c:
                i += 2 if line[i] == "\\" else 1
            i += 1
            continue
        if c == "'" and language != "Rust":
            i += 1
            while i < n and line[i] != "'":
                i += 2 if line[i] == "\\" else 1
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _brace_marks(lines: list[str], language: str) -> list[tuple[int, str | None, int]]:
    """(pre_len, pre_top, block_delta) for each line."""
    stack: list[str] = []
    marks: list[tuple[int, str | None, int]] = []
    for line in lines:
        pre_len = len(stack)
        pre_top = stack[-1] if stack else None
        for ch in _code_only(line, language):
            if ch == "{":
                stack.append(_classify_brace_line(line.strip(), language))
            elif ch == "}" and stack:
                stack.pop()
        marks.append((pre_len, pre_top, len(stack) - pre_len))
    return marks


def _c_like_candidates(lines: list[str], body_start: int, language: str) -> list[int]:
    """Indices of C-like lines that are one self-contained statement."""
    marks = _brace_marks(lines, language)
    cands: list[int] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i < body_start or not stripped:
            continue
        pre_len, pre_top, b_delta = marks[i]
        if pre_top not in ("fn", "block") or b_delta != 0:
            continue
        if not stripped.endswith(";"):
            continue
        _, p_delta = _balance(line, language)
        if p_delta != 0:
            continue
        if stripped.startswith(("}", "{", "case ", "default:", "#")):
            continue
        if len(normalize_code(stripped)) < MIN_ANSWER_CHARS:
            continue
        j = i - 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        if j >= 0 and _is_unbraced_header(lines[j].strip()):
            continue
        cands.append(i)
    return cands


def _go_candidates(lines: list[str], body_start: int, language: str) -> list[int]:
    """Go statements end without `;`, so the rule is looser than C-like."""
    marks = _brace_marks(lines, language)
    cands: list[int] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i < body_start or not stripped:
            continue
        pre_len, pre_top, b_delta = marks[i]
        if pre_top not in ("fn", "block") or b_delta != 0:
            continue
        if stripped.startswith(("}", "{")) or stripped.endswith(("{", ",", "(")):
            continue
        _, p_delta = _balance(line, language)
        if p_delta != 0:
            continue
        if len(normalize_code(stripped)) < MIN_ANSWER_CHARS:
            continue
        if re.match(r"^(case|default|func|type|import|package|var|const)\b", stripped):
            continue
        cands.append(i)
    return cands


def _python_candidates(code: str, body_start: int) -> list[int]:
    """Line numbers (1-based) that are exactly one self-contained statement."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    out: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.stmt):
            continue
        lineno = getattr(node, "lineno", None)
        end = getattr(node, "end_lineno", None)
        if lineno is None or end is None or lineno != end:
            continue
        if lineno <= body_start:
            continue
        out.add(lineno)
    return sorted(out)


def _python_equivalent(line: str) -> list[str]:
    """Genuinely equivalent spellings of a python statement."""
    extra: list[str] = []
    ws = leading_ws(line)
    body = line.strip()
    m = re.match(r"^([A-Za-z_]\w*(?:\[[^\]]+\]|\.\w+)*)\s*=\s*\1\s*([+-])\s*(.+)$", body)
    if m:
        extra.append(f"{ws}{m.group(1)} {m.group(2)}= {m.group(3)}")
    return extra


# ---------------------------------------------------------------------------
# Format A: Complete Function
# ---------------------------------------------------------------------------
def _signature_name(line: str) -> str | None:
    """The function name on a K&R/arrow signature line, else None."""
    m = re.search(r"const\s+(\w+)\s*=", line)
    if m:
        return m.group(1)
    m = re.search(r"\b(?:def|func|fn)\s+(\w+)\s*[<(]", line)
    if m:
        return m.group(1)
    if re.match(r"^\s*(if|for|while|switch|case|else|do|catch|return|using|import|"
                r"#|package|struct|class|enum|interface|impl|trait|pub|static)\b", line):
        return None
    m = re.search(r"([A-Za-z_]\w*)\s*\(", line)
    if m and m.group(1) not in {"if", "for", "while", "switch", "return", "sizeof", "new", "catch"}:
        return m.group(1)
    return None


def _function_name(declaration: str, prompt: str, language: str) -> str | None:
    if language == "Python":
        try:
            tree = ast.parse(prompt)
            fn = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)), None)
            if fn is not None:
                return fn.name
        except SyntaxError:
            pass
    for text in (prompt, declaration):
        for line in reversed([ln for ln in text.split("\n") if ln.strip()]):
            stripped = line.rstrip()
            if not (stripped.endswith("{") or "=>" in stripped):
                continue
            name = _signature_name(stripped)
            if name:
                return name
    return None


def _topic(name: str | None, fallback: str) -> str:
    if name:
        return name.replace("_", " ").strip()
    return fallback


def _difficulty(nbody: int) -> str:
    if nbody <= 6:
        return "Easy"
    if nbody <= 14:
        return "Medium"
    return "Hard"


def build_complete_function(
    language: str,
    rows: list[dict],
    statement_of,
    max_questions: int = MAX_PER_LANG,
) -> tuple[list[dict], dict]:
    stats = {"language": language, "rows": len(rows), "emitted": 0, "skipped": []}
    out: list[dict] = []

    for row in rows:
        if len(out) >= max_questions:
            break
        prompt = row["prompt"]
        body = row["body"]
        code = prompt + body
        statement = statement_of(row)
        if not statement:
            stats["skipped"].append((row["task"], "no problem statement"))
            continue

        lines = code.split("\n")
        body_start = prompt.count("\n")  # 0-based index of first body line
        name = _function_name(row.get("declaration", ""), prompt, language)
        topic = _topic(name, row.get("title") or "complete the function")

        if language == "Python":
            cands = [ln for ln in _python_candidates(code, body_start) if ln - 1 < len(lines)]
            cand_idx = [ln - 1 for ln in cands]
        else:
            cand_idx = _go_candidates(lines, body_start, language) if language == "Go" else _c_like_candidates(
                lines, body_start, language
            )
        if not cand_idx:
            stats["skipped"].append((row["task"], "no removable single-line statement"))
            continue

        chosen = _pick_line(lines, cand_idx, language, body_start)
        if chosen is None:
            stats["skipped"].append((row["task"], "no unambiguous removable line"))
            continue

        i, answer = chosen
        new_lines = list(lines)
        new_lines[i] = leading_ws(lines[i]) + marker_for(language)
        while new_lines and not new_lines[-1].strip():
            new_lines.pop()
        new_code = "\n".join(new_lines)

        answers = [answer] + (_python_equivalent(answer) if language == "Python" else [])
        # de-duplicate while keeping order
        seen = set()
        answers = [a for a in answers if not (a in seen or seen.add(a))]

        out.append(
            {
                "id": None,  # assigned by assign_ids()
                "question_type": "Coding",
                "format": "Complete Function",
                "language": language,
                "difficulty": _difficulty(len([l for l in body.split('\n') if l.strip()])),
                "category": "Algorithms",
                "topic": topic,
                "question_text": (
                    f"{statement}\n\nThe function below is missing one line, marked with a "
                    "comment. Write the missing line."
                ),
                "code": new_code,
                "accepted_answers": answers,
                "time_limit": 300,
                "_source": row["source"],
                "_task": row["task"],
            }
        )

    stats["emitted"] = len(out)
    return out, stats


def _pick_line(lines, cand_idx, language, body_start):
    """Choose the most interesting unambiguous line, or None."""
    scored: list[tuple[int, int, int, str]] = []
    n = len(lines)
    for i in cand_idx:
        raw = lines[i]
        answer = raw.rstrip()
        stripped = raw.strip()
        norm = normalize_code(answer)
        if not norm or len(norm) < MIN_ANSWER_CHARS:
            continue
        if stripped.startswith(("#", "//", "/*", "*")):
            continue
        # the answer must not survive elsewhere in the code (the blank is blank)
        probe = list(lines)
        probe[i] = leading_ws(raw) + marker_for(language)
        if norm in normalize_code("\n".join(probe)):
            continue
        score = _line_score(stripped)
        # prefer lines near the middle of the body
        mid = body_start + (n - body_start) / 2
        distance = abs(i - mid)
        scored.append((-score, distance, i, answer))
    if not scored:
        return None
    scored.sort()
    _, _, i, answer = scored[0]
    return i, answer


def _line_score(stripped: str) -> int:
    score = 0
    if re.search(r"(<=|>=|==|!=|<|>)", stripped):
        score += 3
    if re.search(r"(^|[^=!<>])[+\-*/%](?!=)", stripped):
        score += 2
    if re.search(r"(?<![=!<>])=(?!=)", stripped):
        score += 2
    if "return" in stripped:
        score += 1
    if re.search(r"\b(for|while|if|else)\b", stripped):
        score += 1
    return score


# ---------------------------------------------------------------------------
# Formats B and C: authored by construction
# ---------------------------------------------------------------------------
# Predict Output: (language, topic, difficulty, code, expected stdout)
PREDICT_OUTPUT: list[tuple[str, str, str, str, str]] = [
    # ------------------------------ Python ------------------------------
    (
        "Python", "integer division", "Medium",
        """a = 7
b = 2
print(a // b + a / b)""",
        "6.5",
    ),
    (
        "Python", "modulo with negatives", "Hard",
        """print(-7 % 3, 7 % -3)""",
        "2 -2",
    ),
    (
        "Python", "string repetition", "Easy",
        """x = "2"
y = 3
print(x * y)""",
        "222",
    ),
    (
        "Python", "operator precedence", "Medium",
        """print(2 + 3 * 4 ** 2 // 8)""",
        "8",
    ),
    (
        "Python", "truthiness", "Medium",
        """print(bool("0"), bool(0.0), bool([0]))""",
        "True False True",
    ),
    (
        "Python", "floor division", "Medium",
        """print(7 // -2)""",
        "-4",
    ),
    (
        "Python", "negative list indexing", "Easy",
        """a = [10, 20, 30]
print(a[-1] + a[0])""",
        "40",
    ),
    (
        "Python", "string slicing", "Medium",
        """s = "abcdef"
print(s[1:4] + s[-2:])""",
        "bcdef",
    ),
    (
        "Python", "chained comparison", "Medium",
        """print(1 < 2 < 3, 3 > 2 > 1, 1 < 2 > 3)""",
        "True True False",
    ),
    (
        "Python", "arbitrary precision integers", "Medium",
        """print(2 ** 70)""",
        "1180591620717411303424",
    ),
    (
        "Python", "bankers rounding", "Hard",
        """print(round(2.5), round(3.5), round(0.5))""",
        "2 4 0",
    ),
    (
        "Python", "float precision", "Medium",
        """print(0.1 + 0.2 == 0.3)""",
        "False",
    ),
    (
        "Python", "string concatenation precedence", "Easy",
        """print("ab" + "c" * 2)""",
        "abcc",
    ),
    (
        "Python", "enumerate loop accumulation", "Medium",
        """nums = [5, 6, 7]
total = 0
for i, n in enumerate(nums):
    total += i * n
print(total)""",
        "20",
    ),
    (
        "Python", "boolean operators returning operands", "Hard",
        """print(1 and 0 or 3)""",
        "3",
    ),
    (
        "Python", "list aliasing", "Easy",
        """a = [1, 2, 3]
b = a
b.append(4)
print(len(a))""",
        "4",
    ),
    # ---------------------------- JavaScript ----------------------------
    (
        "JavaScript", "loose vs strict equality", "Hard",
        """console.log([] == false, [] === false);""",
        "true false",
    ),
    (
        "JavaScript", "numeric and string addition", "Medium",
        """console.log(1 + 2 + "3");""",
        "33",
    ),
    (
        "JavaScript", "subtraction coerces strings", "Hard",
        """console.log("1" - 1 + "1");""",
        "01",
    ),
    (
        "JavaScript", "typeof null", "Medium",
        """console.log(typeof null === "object");""",
        "true",
    ),
    (
        "JavaScript", "NaN comparisons", "Medium",
        """console.log(NaN === NaN, isNaN("abc"));""",
        "false true",
    ),
    (
        "JavaScript", "array slice and join", "Easy",
        """const a = [1, 2, 3, 4];
console.log(a.slice(1, 3).join("-"));""",
        "2-3",
    ),
    (
        "JavaScript", "var hoisting", "Hard",
        """function f() {
  return typeof x;
  var x = 5;
}
console.log(f());""",
        "undefined",
    ),
    (
        "JavaScript", "pre and post increment", "Hard",
        """let i = 5;
console.log(i++ + ++i);""",
        "12",
    ),
    (
        "JavaScript", "float equality", "Medium",
        """console.log(0.1 + 0.2 === 0.3);""",
        "false",
    ),
    (
        "JavaScript", "map with parseInt", "Hard",
        """console.log(["1", "2", "3"].map(parseInt).join(","));""",
        "1,NaN,NaN",
    ),
    (
        "JavaScript", "default sort order", "Hard",
        """console.log([10, 9, 100].sort().join(","));""",
        "10,100,9",
    ),
    (
        "JavaScript", "boolean and object coercion", "Hard",
        """console.log(true + true, [] + {});""",
        "2 [object Object]",
    ),
    (
        "JavaScript", "modulo sign", "Medium",
        """console.log(-7 % 3);""",
        "-1",
    ),
    (
        "JavaScript", "var closure capture", "Hard",
        """let fns = [];
for (var k = 0; k < 3; k++) fns.push(() => k);
console.log(fns.map(f => f()).join(","));""",
        "3,3,3",
    ),
    (
        "JavaScript", "null and undefined equality", "Medium",
        """console.log(null == undefined, null === undefined);""",
        "true false",
    ),
    (
        "JavaScript", "string plus and minus", "Medium",
        """let s = "5";
console.log(s + 1, s - 1);""",
        "51 4",
    ),
    # -------------------------------- Java ------------------------------
    (
        "Java", "integer division", "Medium",
        """public class Main {
    public static void main(String[] args) {
        int a = 7, b = 2;
        System.out.println(a / b + a % b);
    }
}""",
        "4",
    ),
    (
        "Java", "pre and post increment", "Hard",
        """public class Main {
    public static void main(String[] args) {
        int i = 5;
        System.out.println(i++ + ++i);
    }
}""",
        "12",
    ),
    (
        "Java", "integer overflow", "Medium",
        """public class Main {
    public static void main(String[] args) {
        int x = Integer.MAX_VALUE;
        System.out.println(x + 1);
    }
}""",
        "-2147483648",
    ),
    (
        "Java", "string concatenation", "Medium",
        """public class Main {
    public static void main(String[] args) {
        System.out.println(1 + 2 + "" + 3 + 4);
    }
}""",
        "334",
    ),
    (
        "Java", "char arithmetic", "Medium",
        """public class Main {
    public static void main(String[] args) {
        System.out.println('a' + 1);
    }
}""",
        "98",
    ),
    (
        "Java", "char narrowing cast", "Easy",
        """public class Main {
    public static void main(String[] args) {
        System.out.println((char) ('a' + 2));
    }
}""",
        "c",
    ),
    (
        "Java", "integer division assigned to double", "Hard",
        """public class Main {
    public static void main(String[] args) {
        double r = 5 / 2;
        System.out.println(r);
    }
}""",
        "2.0",
    ),
    (
        "Java", "nested ternary", "Hard",
        """public class Main {
    public static void main(String[] args) {
        int x = 5;
        System.out.println(x > 3 ? x > 4 ? "A" : "B" : "C");
    }
}""",
        "A",
    ),
    (
        "Java", "string equality", "Hard",
        """public class Main {
    public static void main(String[] args) {
        String a = "hi";
        String b = new String("hi");
        System.out.println(a.equals(b) + " " + (a == b));
    }
}""",
        "true false",
    ),
    (
        "Java", "modulo with negatives", "Hard",
        """public class Main {
    public static void main(String[] args) {
        System.out.println(-7 % 3 + " " + 7 % -3);
    }
}""",
        "-1 1",
    ),
    (
        "Java", "float equality", "Medium",
        """public class Main {
    public static void main(String[] args) {
        System.out.println(0.1 + 0.2 == 0.3);
    }
}""",
        "false",
    ),
    (
        "Java", "left shift", "Easy",
        """public class Main {
    public static void main(String[] args) {
        System.out.println(1 << 3);
    }
}""",
        "8",
    ),
    (
        "Java", "post increment in array index", "Hard",
        """public class Main {
    public static void main(String[] args) {
        int[] a = {10, 20, 30};
        int i = 0;
        System.out.println(a[i++] + a[i]);
    }
}""",
        "30",
    ),
    (
        "Java", "double remainder", "Medium",
        """public class Main {
    public static void main(String[] args) {
        System.out.println(5.5 % 2);
    }
}""",
        "1.5",
    ),
    (
        "Java", "unsigned right shift", "Hard",
        """public class Main {
    public static void main(String[] args) {
        System.out.println(-1 >>> 28);
    }
}""",
        "15",
    ),
    (
        "Java", "truncating division", "Medium",
        """public class Main {
    public static void main(String[] args) {
        System.out.println(-7 / 2);
    }
}""",
        "-3",
    ),
    # -------------------------------- C++ -------------------------------
    (
        "C++", "integer division", "Easy",
        """#include <iostream>
int main() {
    int a = 7, b = 2;
    std::cout << a / b << std::endl;
    return 0;
}""",
        "3",
    ),
    (
        "C++", "char arithmetic", "Medium",
        """#include <iostream>
int main() {
    std::cout << 'a' + 1 << std::endl;
    return 0;
}""",
        "98",
    ),
    (
        "C++", "pre and post increment", "Hard",
        """#include <iostream>
int main() {
    int i = 5;
    int a = i++;
    int b = ++i;
    std::cout << a + b << std::endl;
    return 0;
}""",
        "12",
    ),
    (
        "C++", "unsigned wraparound", "Hard",
        """#include <iostream>
#include <cstdint>
int main() {
    std::uint32_t x = 0;
    x = x - 1;
    std::cout << x << std::endl;
    return 0;
}""",
        "4294967295",
    ),
    (
        "C++", "float to int truncation", "Medium",
        """#include <iostream>
int main() {
    double d = 3.99;
    std::cout << int(d) << std::endl;
    return 0;
}""",
        "3",
    ),
    (
        "C++", "char cast", "Easy",
        """#include <iostream>
int main() {
    std::cout << (char) ('A' + 2) << std::endl;
    return 0;
}""",
        "C",
    ),
    (
        "C++", "operator precedence", "Medium",
        """#include <iostream>
int main() {
    std::cout << 2 + 3 * 4 % 5 << std::endl;
    return 0;
}""",
        "4",
    ),
    (
        "C++", "float equality", "Medium",
        """#include <iostream>
int main() {
    std::cout << (0.1 + 0.2 == 0.3) << std::endl;
    return 0;
}""",
        "0",
    ),
    (
        "C++", "truncating division", "Medium",
        """#include <iostream>
int main() {
    std::cout << (-7) / 2 << std::endl;
    return 0;
}""",
        "-3",
    ),
    (
        "C++", "modulo sign", "Medium",
        """#include <iostream>
int main() {
    std::cout << (-7) % 3 << std::endl;
    return 0;
}""",
        "-1",
    ),
    (
        "C++", "bool printing", "Easy",
        """#include <iostream>
int main() {
    std::cout << (3 > 2) << std::endl;
    return 0;
}""",
        "1",
    ),
    (
        "C++", "comma operator", "Hard",
        """#include <iostream>
int main() {
    int x = (1, 2, 3);
    std::cout << x << std::endl;
    return 0;
}""",
        "3",
    ),
    (
        "C++", "mixed type division", "Medium",
        """#include <iostream>
int main() {
    int a = 7;
    double b = 2;
    std::cout << a / b << std::endl;
    return 0;
}""",
        "3.5",
    ),
    (
        "C++", "string concatenation", "Easy",
        """#include <iostream>
#include <string>
int main() {
    std::string s = "ab";
    std::cout << s + std::to_string(3) << std::endl;
    return 0;
}""",
        "ab3",
    ),
    (
        "C++", "ternary common type", "Hard",
        """#include <iostream>
int main() {
    std::cout << (true ? 1 : 2.5) << std::endl;
    return 0;
}""",
        "1",
    ),
    (
        "C++", "char to int promotion", "Medium",
        """#include <iostream>
int main() {
    char c = 'A';
    std::cout << c + 0 << std::endl;
    return 0;
}""",
        "65",
    ),
    (
        "C++", "left shift", "Easy",
        """#include <iostream>
int main() {
    std::cout << (1 << 4) << std::endl;
    return 0;
}""",
        "16",
    ),
    # --------------------------------- Go -------------------------------
    (
        "Go", "integer division and modulo", "Easy",
        """package main

import "fmt"

func main() {
\ta, b := 7, 2
\tfmt.Println(a/b, a%b)
}""",
        "3 1",
    ),
    (
        "Go", "mixed numeric division", "Medium",
        """package main

import "fmt"

func main() {
\tvar x int = 3
\tvar y float64 = 2
\tfmt.Println(float64(x) / y)
}""",
        "1.5",
    ),
    (
        "Go", "slice append length", "Hard",
        """package main

import "fmt"

func main() {
\ts := []int{1, 2, 3}
\tt := append(s, 4)
\tfmt.Println(len(s), len(t))
}""",
        "3 4",
    ),
    (
        "Go", "slice printing", "Medium",
        """package main

import "fmt"

func main() {
\ts := []int{1, 2, 3, 4}
\tfmt.Println(s[1:3])
}""",
        "[2 3]",
    ),
    (
        "Go", "short variable declaration shadowing", "Hard",
        """package main

import "fmt"

func main() {
\tx := 1
\tif true {
\t\tx := 2
\t\t_ = x
\t}
\tfmt.Println(x)
}""",
        "1",
    ),
    (
        "Go", "truncating division", "Medium",
        """package main

import "fmt"

func main() {
\tfmt.Println(-7/2, -7%2)
}""",
        "-3 -1",
    ),
    (
        "Go", "string length vs runes", "Hard",
        """package main

import "fmt"

func main() {
\ts := "héllo"
\tfmt.Println(len([]rune(s)))
}""",
        "5",
    ),
    (
        "Go", "zero values", "Easy",
        """package main

import "fmt"

func main() {
\tvar s string
\tvar n int
\tfmt.Println(s == "", n)
}""",
        "true 0",
    ),
    (
        "Go", "map missing key", "Hard",
        """package main

import "fmt"

func main() {
\tm := map[string]int{"a": 1}
\tv, ok := m["b"]
\tfmt.Println(v, ok)
}""",
        "0 false",
    ),
    (
        "Go", "rune literal arithmetic", "Medium",
        """package main

import "fmt"

func main() {
\tfmt.Println('a' + 1)
}""",
        "98",
    ),
    (
        "Go", "float literal division", "Easy",
        """package main

import "fmt"

func main() {
\tfmt.Println(7.0 / 2)
}""",
        "3.5",
    ),
    (
        "Go", "slice aliasing", "Hard",
        """package main

import "fmt"

func main() {
\ta := []int{1, 2, 3}
\tb := a[0:2]
\tb[0] = 99
\tfmt.Println(a[0])
}""",
        "99",
    ),
    (
        "Go", "string index is a byte", "Hard",
        """package main

import "fmt"

func main() {
\ts := "Go"
\tfmt.Println(s[0])
}""",
        "71",
    ),
    (
        "Go", "int8 overflow", "Hard",
        """package main

import "fmt"

func main() {
\tvar x int8 = 127
\tx++
\tfmt.Println(x)
}""",
        "-128",
    ),
    (
        "Go", "bitwise operators", "Medium",
        """package main

import "fmt"

func main() {
\tfmt.Println(6&3, 6|3, 6^3)
}""",
        "2 7 5",
    ),
    (
        "Go", "float to int conversion", "Medium",
        """package main

import "fmt"

func main() {
\tvar f float64 = 3.9
\tfmt.Println(int(f))
}""",
        "3",
    ),
    (
        "Go", "left shift", "Easy",
        """package main

import "fmt"

func main() {
\tfmt.Println(1 << 4)
}""",
        "16",
    ),
    (
        "Go", "nil slice append", "Medium",
        """package main

import "fmt"

func main() {
\tvar s []int
\ts = append(s, 5)
\tfmt.Println(len(s), s[0])
}""",
        "1 5",
    ),
    # -------------------------------- Rust ------------------------------
    (
        "Rust", "integer division", "Easy",
        """fn main() {
    let a = 7;
    let b = 2;
    println!("{}", a / b);
}""",
        "3",
    ),
    (
        "Rust", "float division", "Easy",
        """fn main() {
    println!("{}", 7 as f64 / 2 as f64);
}""",
        "3.5",
    ),
    (
        "Rust", "remainder sign", "Medium",
        """fn main() {
    println!("{}", -7 % 3);
}""",
        "-1",
    ),
    (
        "Rust", "operator precedence", "Easy",
        """fn main() {
    println!("{}", 2 + 3 * 4);
}""",
        "14",
    ),
    (
        "Rust", "explicit wrapping arithmetic", "Hard",
        """fn main() {
    let x: u8 = 255;
    println!("{}", x.wrapping_add(1));
}""",
        "0",
    ),
    (
        "Rust", "owned string concatenation", "Medium",
        """fn main() {
    let s = String::from("ab");
    println!("{}", s + "c");
}""",
        "abc",
    ),
    (
        "Rust", "printing booleans", "Easy",
        """fn main() {
    println!("{}", 3 > 2);
}""",
        "true",
    ),
    (
        "Rust", "vector index and length", "Hard",
        """fn main() {
    let v = vec![1, 2, 3];
    println!("{}", v[1] + v.len() as i32);
}""",
        "5",
    ),
    (
        "Rust", "char to byte cast", "Medium",
        """fn main() {
    let c = 'A';
    println!("{}", c as u8);
}""",
        "65",
    ),
    (
        "Rust", "left shift", "Easy",
        """fn main() {
    println!("{}", 1 << 3);
}""",
        "8",
    ),
    (
        "Rust", "tuple field access", "Easy",
        """fn main() {
    let t = (1, 2, 3);
    println!("{}", t.1);
}""",
        "2",
    ),
    (
        "Rust", "float equality", "Medium",
        """fn main() {
    println!("{}", 0.1 + 0.2 == 0.3);
}""",
        "false",
    ),
    (
        "Rust", "float to int cast truncates", "Medium",
        """fn main() {
    let x = 3.9_f64;
    println!("{}", x as i32);
}""",
        "3",
    ),
    (
        "Rust", "inclusive range sum", "Medium",
        """fn main() {
    let s: i32 = (1..=4).sum();
    println!("{}", s);
}""",
        "10",
    ),
    (
        "Rust", "get with default", "Hard",
        """fn main() {
    let v = vec![1, 2, 3];
    println!("{}", v.get(5).unwrap_or(&0));
}""",
        "0",
    ),
    (
        "Rust", "string byte length vs chars", "Hard",
        """fn main() {
    let s = "héllo";
    println!("{} {}", s.len(), s.chars().count());
}""",
        "6 5",
    ),
    (
        "Rust", "float precision formatting", "Medium",
        """fn main() {
    println!("{:.2}", 7 as f64 / 2 as f64);
}""",
        "3.50",
    ),
    (
        "Rust", "iterator filter count", "Hard",
        """fn main() {
    let v = vec![1, 2, 3];
    println!("{}", v.iter().filter(|&&x| x > 1).count());
}""",
        "2",
    ),
    (
        "Rust", "string equality", "Easy",
        """fn main() {
    let a = String::from("hi");
    let b = String::from("hi");
    println!("{}", a == b);
}""",
        "true",
    ),
    (
        "Rust", "reversing chars", "Medium",
        """fn main() {
    let s = "abc";
    println!("{}", s.chars().rev().collect::<String>());
}""",
        "cba",
    ),
]

# Find the Bug: (language, topic, difficulty, intent, code, [(option, is_correct), ...])
FIND_THE_BUG: list[tuple[str, str, str, str, str, list[tuple[str, bool]]]] = [
    # ------------------------------ Python ------------------------------
    (
        "Python", "accumulator loop", "Easy",
        "Return the sum of all integers from 1 to n inclusive",
        """def sum_to(n):
    total = 0
    for i in range(1, n + 1):
        # ??? MISSING LINE ???
    return total""",
        [("total += i", True), ("total = i", False), ("total += n", False), ("total -= i", False)],
    ),
    (
        "Python", "maximum search", "Easy",
        "Return the largest value in nums",
        """def max_of(nums):
    best = nums[0]
    for x in nums:
        # ??? MISSING LINE ???
    return best""",
        [("if x > best: best = x", True), ("if x < best: best = x", False),
         ("best = x", False), ("if x > best: x = best", False)],
    ),
    (
        "Python", "membership test", "Easy",
        "Count how many characters of s are lowercase vowels",
        """def count_vowels(s):
    count = 0
    for ch in s:
        # ??? MISSING LINE ???
    return count""",
        [('if ch in "aeiou": count += 1', True), ('if ch in "aeiou": count = 1', False),
         ('if ch not in "aeiou": count += 1', False), ('if ch in "aeiou": count += 0', False)],
    ),
    (
        "Python", "string building", "Medium",
        "Return the characters of s in reverse order",
        """def reverse(s):
    out = ""
    for ch in s:
        # ??? MISSING LINE ???
    return out""",
        [("out = ch + out", True), ("out = out + ch", False),
         ("out += out", False), ("out = ch", False)],
    ),
    (
        "Python", "multiplicative accumulator", "Easy",
        "Return n factorial (1 * 2 * ... * n)",
        """def factorial(n):
    result = 1
    for i in range(1, n + 1):
        # ??? MISSING LINE ???
    return result""",
        [("result *= i", True), ("result *= n", False),
         ("result += i", False), ("result = i", False)],
    ),
    (
        "Python", "divisibility test", "Medium",
        "Return True when n is a prime number",
        """def is_prime(n):
    if n < 2:
        return False
    for d in range(2, n):
        # ??? MISSING LINE ???
    return True""",
        [("if n % d == 0: return False", True), ("if n % d == 0: return True", False),
         ("if n % d != 0: return False", False), ("if d % n == 0: return False", False)],
    ),
    (
        "Python", "arithmetic mean", "Medium",
        "Return the arithmetic mean of the numbers in nums",
        """def mean(nums):
    total = 0
    for x in nums:
        total += x
    # ??? MISSING LINE ???""",
        [("return total / len(nums)", True), ("return total / (len(nums) - 1)", False),
         ("return total * len(nums)", False), ("return len(nums) / total", False)],
    ),
    (
        "Python", "linear search", "Medium",
        "Return the index of the first occurrence of target, or -1",
        """def find_index(items, target):
    for i, x in enumerate(items):
        # ??? MISSING LINE ???
    return -1""",
        [("if x == target: return i", True), ("if x == target: return x", False),
         ("if i == target: return i", False), ("if x != target: return i", False)],
    ),
    (
        "Python", "parity filter", "Easy",
        "Count how many of the numbers in nums are even",
        """def count_even(nums):
    count = 0
    for x in nums:
        # ??? MISSING LINE ???
    return count""",
        [("if x % 2 == 0: count += 1", True), ("if x % 2 == 1: count += 1", False),
         ("if x / 2 == 0: count += 1", False), ("if x % 2 == 0: count = 1", False)],
    ),
    (
        "Python", "digit extraction", "Hard",
        "Return the sum of the decimal digits of n",
        """def digit_sum(n):
    n = abs(n)
    total = 0
    while n > 0:
        total += n % 10
        # ??? MISSING LINE ???
    return total""",
        [("n //= 10", True), ("n /= 10", False), ("n -= 10", False), ("n %= 10", False)],
    ),
    (
        "Python", "two pointers", "Hard",
        "Return True when s reads the same forwards and backwards",
        """def is_palindrome(s):
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return False
        # ??? MISSING LINE ???
    return True""",
        [("i, j = i + 1, j - 1", True), ("i, j = i + 1, j + 1", False),
         ("i, j = i - 1, j - 1", False), ("i, j = i, j", False)],
    ),
    (
        "Python", "euclidean algorithm", "Hard",
        "Return the greatest common divisor of a and b",
        """def gcd(a, b):
    while b != 0:
        # ??? MISSING LINE ???
    return a""",
        [("a, b = b, a % b", True), ("a, b = b, a / b", False),
         ("a, b = a % b, b", False), ("a, b = b, a // b", False)],
    ),
    (
        "Python", "sum of squares", "Easy",
        "Return the sum of the squares of the numbers in nums",
        """def sum_squares(nums):
    total = 0
    for x in nums:
        # ??? MISSING LINE ???
    return total""",
        [("total += x * x", True), ("total += x + x", False),
         ("total += x", False), ("total = x * x", False)],
    ),
    # -------------------------------- Java ------------------------------
    (
        "Java", "accumulator loop", "Easy",
        "Return the sum of all integers from 1 to n inclusive",
        """class Solution {
    public int sumTo(int n) {
        int total = 0;
        for (int i = 1; i <= n; i++) {
            // ??? MISSING LINE ???
        }
        return total;
    }
}""",
        [("total += i;", True), ("total = i;", False), ("total += n;", False), ("total -= i;", False)],
    ),
    (
        "Java", "maximum search", "Easy",
        "Return the largest value in nums",
        """class Solution {
    public int maxOf(int[] nums) {
        int best = nums[0];
        for (int x : nums) {
            // ??? MISSING LINE ???
        }
        return best;
    }
}""",
        [("if (x > best) best = x;", True), ("if (x < best) best = x;", False),
         ("best = x;", False), ("if (x > best) x = best;", False)],
    ),
    (
        "Java", "string building", "Medium",
        "Return the characters of s in reverse order",
        """class Solution {
    public String reverse(String s) {
        String out = "";
        for (int i = s.length() - 1; i >= 0; i--) {
            // ??? MISSING LINE ???
        }
        return out;
    }
}""",
        [("out += s.charAt(i);", True), ("out += s.charAt(0);", False),
         ("out += s.charAt(i - 1);", False), ("out = s.charAt(i) + out;", False)],
    ),
    (
        "Java", "substring search", "Hard",
        "Count how many characters of s are lowercase vowels",
        """class Solution {
    public int countVowels(String s) {
        int count = 0;
        String vowels = "aeiou";
        for (char c : s.toCharArray()) {
            // ??? MISSING LINE ???
        }
        return count;
    }
}""",
        [("if (vowels.indexOf(c) >= 0) count++;", True), ("if (vowels.indexOf(c) > 0) count++;", False),
         ("if (vowels.indexOf(c) >= 0) count = 1;", False), ("if (vowels.indexOf(c) < 0) count++;", False)],
    ),
    (
        "Java", "parity test", "Easy",
        "Return true when n is an even number",
        """class Solution {
    public boolean isEven(int n) {
        // ??? MISSING LINE ???
    }
}""",
        [("return n % 2 == 0;", True), ("return n % 2 == 1;", False),
         ("return n / 2 == 0;", False), ("return n % 2 != 0;", False)],
    ),
    (
        "Java", "multiplicative accumulator", "Easy",
        "Return n factorial (1 * 2 * ... * n)",
        """class Solution {
    public long factorial(int n) {
        long result = 1;
        for (int i = 1; i <= n; i++) {
            // ??? MISSING LINE ???
        }
        return result;
    }
}""",
        [("result *= i;", True), ("result *= n;", False),
         ("result += i;", False), ("result = i;", False)],
    ),
    (
        "Java", "linear search", "Medium",
        "Return the index of the first occurrence of target, or -1",
        """class Solution {
    public int indexOf(int[] arr, int target) {
        for (int i = 0; i < arr.length; i++) {
            // ??? MISSING LINE ???
        }
        return -1;
    }
}""",
        [("if (arr[i] == target) return i;", True), ("if (arr[i] == target) return arr[i];", False),
         ("if (i == target) return i;", False), ("if (arr[i] != target) return i;", False)],
    ),
    (
        "Java", "array accumulation", "Medium",
        "Return the sum of every element of arr",
        """class Solution {
    public int sum(int[] arr) {
        int total = 0;
        for (int i = 0; i < arr.length; i++) {
            // ??? MISSING LINE ???
        }
        return total;
    }
}""",
        [("total += arr[i];", True), ("total += arr[i + 1];", False),
         ("total += i;", False), ("total = arr[i];", False)],
    ),
    (
        "Java", "character counting", "Medium",
        "Count how many times target appears in s",
        """class Solution {
    public int countChar(String s, char target) {
        int count = 0;
        for (int i = 0; i < s.length(); i++) {
            // ??? MISSING LINE ???
        }
        return count;
    }
}""",
        [("if (s.charAt(i) == target) count++;", True), ("if (s.charAt(i) == target) count += i;", False),
         ("if (s.charAt(i) != target) count++;", False), ("if (s.charAt(i) == target) count = 1;", False)],
    ),
    (
        "Java", "floating point mean", "Hard",
        "Return the arithmetic mean of arr as a double",
        """class Solution {
    public double mean(int[] arr) {
        int total = 0;
        for (int x : arr) {
            total += x;
        }
        // ??? MISSING LINE ???
    }
}""",
        [("return (double) total / arr.length;", True), ("return total / arr.length;", False),
         ("return total / (arr.length - 1);", False), ("return (double) (total * arr.length);", False)],
    ),
    (
        "Java", "last element", "Easy",
        "Return the last element of arr",
        """class Solution {
    public int last(int[] arr) {
        // ??? MISSING LINE ???
    }
}""",
        [("return arr[arr.length - 1];", True), ("return arr[arr.length];", False),
         ("return arr[0];", False), ("return arr[arr.length / 2];", False)],
    ),
    (
        "Java", "string comparison", "Hard",
        "Return true when a and b hold the same characters",
        """class Solution {
    public boolean same(String a, String b) {
        // ??? MISSING LINE ???
    }
}""",
        [("return a.equals(b);", True), ("return a == b;", False),
         ("return a.compareTo(b) != 0;", False), ("return b.equals(a) == false;", False)],
    ),
    # -------------------------------- C++ -------------------------------
    (
        "C++", "accumulator loop", "Easy",
        "Return the sum of all integers from 1 to n inclusive",
        """int sum_to(int n) {
    int total = 0;
    for (int i = 1; i <= n; i++) {
        // ??? MISSING LINE ???
    }
    return total;
}""",
        [("total += i;", True), ("total = i;", False), ("total += n;", False), ("total -= i;", False)],
    ),
    (
        "C++", "maximum search", "Easy",
        "Return the largest value in nums",
        """int max_of(const std::vector<int>& nums) {
    int best = nums[0];
    for (int x : nums) {
        // ??? MISSING LINE ???
    }
    return best;
}""",
        [("if (x > best) best = x;", True), ("if (x < best) best = x;", False),
         ("best = x;", False), ("if (x > best) x = best;", False)],
    ),
    (
        "C++", "parity test", "Easy",
        "Return true when n is an even number",
        """bool is_even(int n) {
    // ??? MISSING LINE ???
}""",
        [("return n % 2 == 0;", True), ("return n % 2 == 1;", False),
         ("return n / 2 == 0;", False), ("return n % 2 != 0;", False)],
    ),
    (
        "C++", "string building", "Hard",
        "Return the characters of s in reverse order",
        """std::string reverse(const std::string& s) {
    std::string out;
    for (int i = (int) s.size() - 1; i >= 0; i--) {
        // ??? MISSING LINE ???
    }
    return out;
}""",
        [("out += s[i];", True), ("out += s[0];", False),
         ("out += s[i - 1];", False), ("out = s[i] + out;", False)],
    ),
    (
        "C++", "substring search", "Hard",
        "Count how many characters of s are lowercase vowels",
        """int count_vowels(const std::string& s) {
    int count = 0;
    const std::string vowels = "aeiou";
    for (char c : s) {
        // ??? MISSING LINE ???
    }
    return count;
}""",
        [("if (vowels.find(c) != std::string::npos) count++;", True),
         ("if (vowels.find(c) == std::string::npos) count++;", False),
         ("if (vowels.find(c) > 0) count++;", False),
         ("if (vowels.find(c) != std::string::npos) count = 1;", False)],
    ),
    (
        "C++", "multiplicative accumulator", "Easy",
        "Return n factorial (1 * 2 * ... * n)",
        """long long factorial(int n) {
    long long result = 1;
    for (int i = 1; i <= n; i++) {
        // ??? MISSING LINE ???
    }
    return result;
}""",
        [("result *= i;", True), ("result *= n;", False),
         ("result += i;", False), ("result = i;", False)],
    ),
    (
        "C++", "linear search", "Medium",
        "Return the index of the first occurrence of target, or -1",
        """int find_index(const std::vector<int>& items, int target) {
    for (int i = 0; i < (int) items.size(); i++) {
        // ??? MISSING LINE ???
    }
    return -1;
}""",
        [("if (items[i] == target) return i;", True), ("if (items[i] == target) return items[i];", False),
         ("if (i == target) return i;", False), ("if (items[i] != target) return i;", False)],
    ),
    (
        "C++", "array accumulation", "Medium",
        "Return the sum of every element of arr",
        """int sum(const std::vector<int>& arr) {
    int total = 0;
    for (int i = 0; i < (int) arr.size(); i++) {
        // ??? MISSING LINE ???
    }
    return total;
}""",
        [("total += arr[i];", True), ("total += arr[i + 1];", False),
         ("total += i;", False), ("total = arr[i];", False)],
    ),
    (
        "C++", "parity filter", "Easy",
        "Count how many of the numbers in nums are even",
        """int count_even(const std::vector<int>& nums) {
    int count = 0;
    for (int x : nums) {
        // ??? MISSING LINE ???
    }
    return count;
}""",
        [("if (x % 2 == 0) count++;", True), ("if (x % 2 != 0) count++;", False),
         ("if (x / 2 == 0) count++;", False), ("if (x % 2 == 0) count = 1;", False)],
    ),
    (
        "C++", "floating point mean", "Hard",
        "Return the arithmetic mean of arr as a double",
        """double mean(const std::vector<int>& arr) {
    int total = 0;
    for (int x : arr) {
        total += x;
    }
    // ??? MISSING LINE ???
}""",
        [("return (double) total / arr.size();", True), ("return total / arr.size();", False),
         ("return total / (arr.size() - 1);", False), ("return (double) (total * arr.size());", False)],
    ),
    (
        "C++", "last element", "Easy",
        "Return the last element of arr",
        """int last(const std::vector<int>& arr) {
    // ??? MISSING LINE ???
}""",
        [("return arr[arr.size() - 1];", True), ("return arr[arr.size()];", False),
         ("return arr[0];", False), ("return arr[arr.size() / 2];", False)],
    ),
    (
        "C++", "palindrome check", "Medium",
        "Return true when s reads the same forwards and backwards",
        """bool is_palindrome(const std::string& s) {
    std::string r(s.rbegin(), s.rend());
    // ??? MISSING LINE ???
}""",
        [("return s == r;", True), ("return s != r;", False),
         ("return s == s;", False), ("return r == r;", False)],
    ),
    (
        "C++", "euclidean algorithm", "Hard",
        "Return the greatest common divisor of a and b",
        """int gcd(int a, int b) {
    while (b != 0) {
        int t = a % b;
        a = b;
        // ??? MISSING LINE ???
    }
    return a;
}""",
        [("b = t;", True), ("b = a;", False), ("b = t + 1;", False), ("b = a % b;", False)],
    ),
    # ---------------------------- JavaScript ----------------------------
    (
        "JavaScript", "accumulator loop", "Easy",
        "Return the sum of all integers from 1 to n inclusive",
        """function sumTo(n) {
  let total = 0;
  for (let i = 1; i <= n; i++) {
    // ??? MISSING LINE ???
  }
  return total;
}""",
        [("total += i;", True), ("total = i;", False), ("total += n;", False), ("total -= i;", False)],
    ),
    (
        "JavaScript", "maximum search", "Easy",
        "Return the largest value in nums",
        """function maxOf(nums) {
  let best = nums[0];
  for (const x of nums) {
    // ??? MISSING LINE ???
  }
  return best;
}""",
        [("if (x > best) best = x;", True), ("if (x < best) best = x;", False),
         ("best = x;", False), ("if (x > best) x = best;", False)],
    ),
    (
        "JavaScript", "parity test", "Easy",
        "Return true when n is an even number",
        """function isEven(n) {
  // ??? MISSING LINE ???
}""",
        [("return n % 2 === 0;", True), ("return n % 2 === 1;", False),
         ("return n / 2 === 0;", False), ("return n % 2;", False)],
    ),
    (
        "JavaScript", "string building", "Medium",
        "Return the characters of s in reverse order",
        """function reverse(s) {
  let out = "";
  for (const ch of s) {
    // ??? MISSING LINE ???
  }
  return out;
}""",
        [("out = ch + out;", True), ("out = out + ch;", False),
         ("out += out + ch;", False), ("out = ch;", False)],
    ),
    (
        "JavaScript", "substring search", "Hard",
        "Count how many characters of s are lowercase vowels",
        """function countVowels(s) {
  let count = 0;
  for (const ch of s) {
    // ??? MISSING LINE ???
  }
  return count;
}""",
        [('if ("aeiou".includes(ch)) count++;', True), ('if ("aeiou".includes(ch)) count = 1;', False),
         ('if ("aeiou".indexOf(ch) > 0) count++;', False), ('if (!"aeiou".includes(ch)) count++;', False)],
    ),
    (
        "JavaScript", "multiplicative accumulator", "Easy",
        "Return n factorial (1 * 2 * ... * n)",
        """function factorial(n) {
  let result = 1;
  for (let i = 1; i <= n; i++) {
    // ??? MISSING LINE ???
  }
  return result;
}""",
        [("result *= i;", True), ("result *= n;", False),
         ("result += i;", False), ("result = i;", False)],
    ),
    (
        "JavaScript", "linear search", "Medium",
        "Return the index of the first occurrence of target, or -1",
        """function findIndex(items, target) {
  for (let i = 0; i < items.length; i++) {
    // ??? MISSING LINE ???
  }
  return -1;
}""",
        [("if (items[i] === target) return i;", True), ("if (items[i] === target) return items[i];", False),
         ("if (i === target) return i;", False), ("if (items[i] != target) return i;", False)],
    ),
    (
        "JavaScript", "array accumulation", "Medium",
        "Return the sum of every element of arr",
        """function sumArray(arr) {
  let total = 0;
  for (let i = 0; i < arr.length; i++) {
    // ??? MISSING LINE ???
  }
  return total;
}""",
        [("total += arr[i];", True), ("total += arr[i + 1];", False),
         ("total += i;", False), ("total = arr[i];", False)],
    ),
    (
        "JavaScript", "array filtering", "Medium",
        "Return a new array with only the even numbers of arr",
        """function evens(arr) {
  // ??? MISSING LINE ???
}""",
        [("return arr.filter(x => x % 2 === 0);", True), ("return arr.filter(x => x % 2 === 1);", False),
         ("return arr.map(x => x % 2 === 0);", False), ("return arr.filter(x => x / 2 === 0);", False)],
    ),
    (
        "JavaScript", "character counting", "Medium",
        "Count how many times target appears in s",
        """function countChar(s, target) {
  let count = 0;
  for (const ch of s) {
    // ??? MISSING LINE ???
  }
  return count;
}""",
        [("if (ch === target) count++;", True), ("if (ch === target) count = 1;", False),
         ("if (ch !== target) count++;", False), ("if (ch === target) count += 0;", False)],
    ),
    (
        "JavaScript", "palindrome check", "Medium",
        "Return true when s reads the same forwards and backwards",
        """function isPalindrome(s) {
  // ??? MISSING LINE ???
}""",
        [('return s === s.split("").reverse().join("");', True),
         ('return s.split("").reverse() === s;', False),
         ('return s === s.split("").join("");', False),
         ("return s === s.reverse();", False)],
    ),
    (
        "JavaScript", "arithmetic mean", "Medium",
        "Return the arithmetic mean of the numbers in arr",
        """function mean(arr) {
  let total = 0;
  for (const x of arr) total += x;
  // ??? MISSING LINE ???
}""",
        [("return total / arr.length;", True), ("return total / (arr.length - 1);", False),
         ("return total * arr.length;", False), ("return arr.length / total;", False)],
    ),
    (
        "JavaScript", "array mapping", "Easy",
        "Return a new array where every element of arr is doubled",
        """function doubled(arr) {
  // ??? MISSING LINE ???
}""",
        [("return arr.map(x => x * 2);", True), ("return arr.map(x => x + 2);", False),
         ("return arr.filter(x => x * 2);", False), ("return arr.map(x => 2);", False)],
    ),
    (
        "JavaScript", "last element with guard", "Hard",
        "Return the last element of arr, or null when arr is empty",
        """function lastOrNull(arr) {
  // ??? MISSING LINE ???
}""",
        [("return arr.length === 0 ? null : arr[arr.length - 1];", True),
         ("return arr[arr.length - 1];", False),
         ("return arr.length === 0 ? arr[0] : null;", False),
         ("return arr.length === 0 ? arr[arr.length - 1] : null;", False)],
    ),
    # --------------------------------- Go -------------------------------
    (
        "Go", "accumulator loop", "Easy",
        "Return the sum of all integers from 1 to n inclusive",
        """func SumTo(n int) int {
    total := 0
    for i := 1; i <= n; i++ {
        // ??? MISSING LINE ???
    }
    return total
}""",
        [("total += i", True), ("total = i", False), ("total += n", False), ("total -= i", False)],
    ),
    (
        "Go", "maximum search", "Easy",
        "Return the largest value in nums",
        """func MaxOf(nums []int) int {
    best := nums[0]
    for _, x := range nums {
        // ??? MISSING LINE ???
    }
    return best
}""",
        [("if x > best { best = x }", True), ("if x < best { best = x }", False),
         ("best = x", False), ("if x > best { x = best }", False)],
    ),
    (
        "Go", "parity test", "Easy",
        "Return true when n is an even number",
        """func IsEven(n int) bool {
    // ??? MISSING LINE ???
}""",
        [("return n%2 == 0", True), ("return n%2 == 1", False),
         ("return n/2 == 0", False), ("return n%2 != 0", False)],
    ),
    (
        "Go", "string building", "Medium",
        "Return the characters of s in reverse order (ASCII input)",
        """func Reverse(s string) string {
    out := ""
    for i := len(s) - 1; i >= 0; i-- {
        // ??? MISSING LINE ???
    }
    return out
}""",
        [("out += string(s[i])", True), ("out += string(s[0])", False),
         ("out += string(s[i-1])", False), ("out = string(s[i]) + out", False)],
    ),
    (
        "Go", "substring search", "Hard",
        "Count how many characters of s are lowercase vowels",
        """func CountVowels(s string) int {
    count := 0
    for _, c := range s {
        // ??? MISSING LINE ???
    }
    return count
}""",
        [('if strings.ContainsRune("aeiou", c) { count++ }', True),
         ('if strings.ContainsRune("aeiou", c) { count = 1 }', False),
         ('if !strings.ContainsRune("aeiou", c) { count++ }', False),
         ('if strings.IndexRune("aeiou", c) > 0 { count++ }', False)],
    ),
    (
        "Go", "multiplicative accumulator", "Easy",
        "Return n factorial (1 * 2 * ... * n)",
        """func Factorial(n int) int {
    result := 1
    for i := 1; i <= n; i++ {
        // ??? MISSING LINE ???
    }
    return result
}""",
        [("result *= i", True), ("result *= n", False),
         ("result += i", False), ("result = i", False)],
    ),
    (
        "Go", "linear search", "Medium",
        "Return the index of the first occurrence of target, or -1",
        """func FindIndex(items []int, target int) int {
    for i := 0; i < len(items); i++ {
        // ??? MISSING LINE ???
    }
    return -1
}""",
        [("if items[i] == target { return i }", True), ("if items[i] == target { return items[i] }", False),
         ("if i == target { return i }", False), ("if items[i] != target { return i }", False)],
    ),
    (
        "Go", "slice accumulation", "Medium",
        "Return the sum of every element of arr",
        """func Sum(arr []int) int {
    total := 0
    for i := 0; i < len(arr); i++ {
        // ??? MISSING LINE ???
    }
    return total
}""",
        [("total += arr[i]", True), ("total += arr[i+1]", False),
         ("total += i", False), ("total = arr[i]", False)],
    ),
    (
        "Go", "parity filter", "Easy",
        "Count how many of the numbers in nums are even",
        """func CountEven(nums []int) int {
    count := 0
    for _, x := range nums {
        // ??? MISSING LINE ???
    }
    return count
}""",
        [("if x%2 == 0 { count++ }", True), ("if x%2 != 0 { count++ }", False),
         ("if x/2 == 0 { count++ }", False), ("if x%2 == 0 { count = 1 }", False)],
    ),
    (
        "Go", "last element", "Easy",
        "Return the last element of arr",
        """func Last(arr []int) int {
    // ??? MISSING LINE ???
}""",
        [("return arr[len(arr)-1]", True), ("return arr[len(arr)]", False),
         ("return arr[0]", False), ("return arr[len(arr)/2]", False)],
    ),
    (
        "Go", "character counting", "Medium",
        "Count how many times target appears in s",
        """func CountChar(s string, target rune) int {
    count := 0
    for _, c := range s {
        // ??? MISSING LINE ???
    }
    return count
}""",
        [("if c == target { count++ }", True), ("if c == target { count = 1 }", False),
         ("if c != target { count++ }", False), ("if c == target { count += 0 }", False)],
    ),
    (
        "Go", "floating point mean", "Hard",
        "Return the arithmetic mean of the numbers in arr",
        """func Mean(arr []int) float64 {
    total := 0
    for _, x := range arr {
        total += x
    }
    // ??? MISSING LINE ???
}""",
        [("return float64(total) / float64(len(arr))", True),
         ("return float64(total / len(arr))", False),
         ("return float64(total) / float64(len(arr)-1)", False),
         ("return float64(total * len(arr))", False)],
    ),
    (
        "Go", "palindrome check", "Hard",
        "Return true when s reads the same forwards and backwards",
        """func IsPalindrome(s string) bool {
    r := []rune(s)
    for i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {
        if r[i] != r[j] {
            return false
        }
    }
    // ??? MISSING LINE ???
}""",
        [("return true", True), ("return false", False),
         ("return r[0] == r[len(r)-1]", False), ("return len(r) == 0", False)],
    ),
    (
        "Go", "euclidean algorithm", "Hard",
        "Return the greatest common divisor of a and b",
        """func Gcd(a, b int) int {
    for b != 0 {
        t := a % b
        a = b
        // ??? MISSING LINE ???
    }
    return a
}""",
        [("b = t", True), ("b = a", False), ("b = t + 1", False), ("b = a % b", False)],
    ),
    # ------------------------------- Rust -------------------------------
    (
        "Rust", "accumulator loop", "Easy",
        "Return the sum of all integers from 1 to n inclusive",
        """fn sum_to(n: i32) -> i32 {
    let mut total = 0;
    for i in 1..=n {
        // ??? MISSING LINE ???
    }
    total
}""",
        [("total += i;", True), ("total = i;", False), ("total += n;", False), ("total -= i;", False)],
    ),
    (
        "Rust", "maximum search", "Easy",
        "Return the largest value in nums",
        """fn max_of(nums: &[i32]) -> i32 {
    let mut best = nums[0];
    for &x in nums {
        // ??? MISSING LINE ???
    }
    best
}""",
        [("if x > best { best = x; }", True), ("if x < best { best = x; }", False),
         ("best = x;", False), ("if x > best { x = best; }", False)],
    ),
    (
        "Rust", "parity test", "Easy",
        "Return true when n is an even number",
        """fn is_even(n: i32) -> bool {
    // ??? MISSING LINE ???
}""",
        [("n % 2 == 0", True), ("n % 2 == 1", False),
         ("n / 2 == 0", False), ("n % 2 != 0", False)],
    ),
    (
        "Rust", "string building", "Medium",
        "Return the characters of s in reverse order",
        """fn reverse(s: &str) -> String {
    let mut out = String::new();
    for ch in s.chars().rev() {
        // ??? MISSING LINE ???
    }
    out
}""",
        [("out.push(ch);", True), ("out.insert(0, ch);", False),
         ("out.push_str(s);", False), ("out.push('a');", False)],
    ),
    (
        "Rust", "substring search", "Hard",
        "Count how many characters of s are lowercase vowels",
        """fn count_vowels(s: &str) -> usize {
    let mut count = 0;
    for ch in s.chars() {
        // ??? MISSING LINE ???
    }
    count
}""",
        [('if "aeiou".contains(ch) { count += 1; }', True),
         ('if "aeiou".contains(ch) { count = 1; }', False),
         ('if !"aeiou".contains(ch) { count += 1; }', False),
         ('if "aeiou".find(ch).unwrap_or(0) > 0 { count += 1; }', False)],
    ),
    (
        "Rust", "multiplicative accumulator", "Medium",
        "Return n factorial (1 * 2 * ... * n)",
        """fn factorial(n: u32) -> u64 {
    let mut result = 1u64;
    for i in 1..=n {
        // ??? MISSING LINE ???
    }
    result
}""",
        [("result *= i as u64;", True), ("result *= n as u64;", False),
         ("result += i as u64;", False), ("result = i as u64;", False)],
    ),
    (
        "Rust", "linear search", "Medium",
        "Return the index of the first occurrence of target, or -1",
        """fn find_index(items: &[i32], target: i32) -> i32 {
    for (i, &x) in items.iter().enumerate() {
        // ??? MISSING LINE ???
    }
    -1
}""",
        [("if x == target { return i as i32; }", True), ("if x == target { return x; }", False),
         ("if i as i32 == target { return i as i32; }", False),
         ("if x != target { return i as i32; }", False)],
    ),
    (
        "Rust", "slice accumulation", "Medium",
        "Return the sum of every element of arr",
        """fn sum(arr: &[i32]) -> i32 {
    let mut total = 0;
    for i in 0..arr.len() {
        // ??? MISSING LINE ???
    }
    total
}""",
        [("total += arr[i];", True), ("total += arr[i + 1];", False),
         ("total += i as i32;", False), ("total = arr[i];", False)],
    ),
    (
        "Rust", "parity filter", "Easy",
        "Count how many of the numbers in nums are even",
        """fn count_even(nums: &[i32]) -> usize {
    let mut count = 0;
    for &x in nums {
        // ??? MISSING LINE ???
    }
    count
}""",
        [("if x % 2 == 0 { count += 1; }", True), ("if x % 2 != 0 { count += 1; }", False),
         ("if x / 2 == 0 { count += 1; }", False), ("if x % 2 == 0 { count = 1; }", False)],
    ),
    (
        "Rust", "last element", "Easy",
        "Return the last element of arr",
        """fn last(arr: &[i32]) -> i32 {
    // ??? MISSING LINE ???
}""",
        [("arr[arr.len() - 1]", True), ("arr[arr.len()]", False),
         ("arr[0]", False), ("arr[arr.len() / 2]", False)],
    ),
    (
        "Rust", "character counting", "Medium",
        "Count how many times target appears in s",
        """fn count_char(s: &str, target: char) -> usize {
    let mut count = 0;
    for ch in s.chars() {
        // ??? MISSING LINE ???
    }
    count
}""",
        [("if ch == target { count += 1; }", True), ("if ch == target { count = 1; }", False),
         ("if ch != target { count += 1; }", False), ("if ch == target { count += 0; }", False)],
    ),
    (
        "Rust", "floating point mean", "Hard",
        "Return the arithmetic mean of the numbers in arr",
        """fn mean(arr: &[i32]) -> f64 {
    let mut total = 0;
    for &x in arr {
        total += x;
    }
    // ??? MISSING LINE ???
}""",
        [("total as f64 / arr.len() as f64", True), ("(total / arr.len() as i32) as f64", False),
         ("total as f64 / (arr.len() - 1) as f64", False), ("total as f64 * arr.len() as f64", False)],
    ),
    (
        "Rust", "palindrome check", "Medium",
        "Return true when s reads the same forwards and backwards",
        """fn is_palindrome(s: &str) -> bool {
    let r: String = s.chars().rev().collect();
    // ??? MISSING LINE ???
}""",
        [("s.to_string() == r", True), ("s.to_string() != r", False),
         ("r == r", False), ("s == s", False)],
    ),
    (
        "Rust", "euclidean algorithm", "Hard",
        "Return the greatest common divisor of a and b",
        """fn gcd(mut a: i64, mut b: i64) -> i64 {
    while b != 0 {
        let t = a % b;
        a = b;
        // ??? MISSING LINE ???
    }
    a
}""",
        [("b = t;", True), ("b = a;", False), ("b = t + 1;", False), ("b = a % b;", False)],
    ),
]


def build_predict_output() -> list[dict]:
    out: list[dict] = []
    for language, topic, difficulty, code, expected in PREDICT_OUTPUT:
        out.append(
            {
                "id": None,
                "question_type": "Coding",
                "format": "Predict Output",
                "language": language,
                "difficulty": difficulty,
                "category": "Algorithms",
                "topic": topic,
                "question_text": f"What does this {language} code print?",
                "code": code,
                "accepted_answers": [expected],
                "time_limit": 300,
            }
        )
    return out


def build_find_the_bug() -> list[dict]:
    out: list[dict] = []
    for idx, (language, topic, difficulty, intent, code, options) in enumerate(FIND_THE_BUG):
        texts = [text for text, _ in options]
        correct = next(i for i, (_, ok) in enumerate(options) if ok)
        if sum(1 for _, ok in options if ok) != 1:
            raise ValueError(f"find-the-bug entry {idx} must have exactly one correct option")
        rng = random.Random(1000 + idx)
        order = list(range(len(texts)))
        rng.shuffle(order)
        shuffled = [texts[i] for i in order]
        correct_index = order.index(correct)
        out.append(
            {
                "id": None,
                "question_type": "Coding",
                "format": "Find the Bug",
                "language": language,
                "difficulty": difficulty,
                "category": "Algorithms",
                "topic": topic,
                "question_text": (
                    f"{intent}. The snippet below does not work. "
                    "Which line should replace the marked line to fix it?"
                ),
                "code": code,
                "options": [{"index": i, "text": t} for i, t in enumerate(shuffled)],
                "correct_answer_index": correct_index,
                "time_limit": 300,
            }
        )
    return out


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate(questions: list[dict]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for q in questions:
        qid = q.get("id", "<missing id>")
        def bad(msg: str) -> None:
            errors.append(f"{qid}: {msg}")

        if not qid or qid in seen_ids:
            bad("duplicate or missing id")
        seen_ids.add(qid)
        if q.get("question_type") != "Coding":
            bad("question_type must be Coding")
        fmt = q.get("format")
        if fmt not in FORMATS:
            bad(f"bad format {fmt!r}")
        if q.get("language") not in LANGS:
            bad(f"bad language {q.get('language')!r}")
        for field in ("question_text", "code", "topic"):
            if not str(q.get(field) or "").strip():
                bad(f"empty {field}")
        if q.get("time_limit") != 300:
            bad("time_limit must be 300")

        marker = marker_for(q.get("language", ""))
        if fmt == "Complete Function":
            answers = q.get("accepted_answers") or []
            if not answers:
                bad("no accepted_answers")
            if q.get("code", "").count(marker) != 1:
                bad("marker must appear exactly once")
            if answers:
                canon = normalize_code(answers[0])
                if not canon:
                    bad("empty normalised canonical answer")
                if len(canon) < MIN_ANSWER_CHARS:
                    bad("canonical answer trivially short")
                elif canon in normalize_code(q.get("code", "")):
                    bad("canonical answer still present in code")
            if "options" in q:
                bad("Complete Function must not carry options")
        elif fmt == "Predict Output":
            answers = q.get("accepted_answers") or []
            if len(answers) != 1 or not norm_ans(answers):
                bad("Predict Output needs exactly one non-empty answer")
            if "options" in q:
                bad("Predict Output must not carry options")
        elif fmt == "Find the Bug":
            options = q.get("options") or []
            if len(options) < 3:
                bad("Find the Bug needs >= 3 options")
            texts = [o.get("text", "") for o in options]
            if len(set(texts)) != len(texts):
                bad("duplicate option text")
            cai = q.get("correct_answer_index")
            if not isinstance(cai, int) or not (0 <= cai < len(options)):
                bad("correct_answer_index out of range")
            if q.get("code", "").count(marker) != 1:
                bad("marker must appear exactly once")
            if "accepted_answers" in q:
                bad("Find the Bug must not carry accepted_answers")
    return errors


def norm_ans(answers) -> bool:
    return bool(answers) and bool(normalize_output(str(answers[0])))


def assign_ids(questions: list[dict]) -> None:
    counters: dict[str, int] = {}
    for q in questions:
        tag = LANG_TAG[q["language"]]
        counters[tag] = counters.get(tag, 0) + 1
        q["id"] = f"NEX_{tag}_{counters[tag]:03d}"


def build_all() -> tuple[list[dict], list[dict]]:
    questions: list[dict] = []
    report: list[dict] = []

    for language in LANGS:
        rows = load_lbpp(language) if language == "Rust" else load_humaneval(language)

        def statement_of(row, language=language):
            if row.get("statement"):
                return row["statement"]
            return statement_from_prompt(language, row["prompt"])

        dataset_q, stats = build_complete_function(language, rows, statement_of)
        report.append(stats)
        questions.extend(dataset_q)

    questions.extend(build_predict_output())
    questions.extend(build_find_the_bug())
    assign_ids(questions)
    return questions, report


def print_report(questions: list[dict], stats: list[dict]) -> None:
    langs = sorted({q["language"] for q in questions})
    print("\nper-language / per-format counts")
    header = "language".ljust(12) + "".join(f.ljust(19) for f in FORMATS) + "total"
    print(header)
    for lang in LANGS:
        row = []
        total = 0
        for fmt in FORMATS:
            n = sum(1 for q in questions if q["language"] == lang and q["format"] == fmt)
            total += n
            row.append(str(n).ljust(19))
        print(lang.ljust(12) + "".join(row) + str(total))
    print(
        "TOTAL".ljust(12)
        + "".join(str(sum(1 for q in questions if q["format"] == f)).ljust(19) for f in FORMATS)
        + str(len(questions))
    )
    print("\ndataset conversion")
    for s in stats:
        print(
            f"  {s['language']:<11} rows={s['rows']:<4} emitted={s['emitted']:<4} "
            f"skipped={len(s['skipped'])}"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(_MODELS / "coding_bank_nonexecuted.json"))
    ap.add_argument("--validate", action="store_true", help="validate the file at --out and exit")
    ap.add_argument("--runtime-verify", action="store_true",
                    help="dev aid: run Predict Output snippets on local runtimes")
    args = ap.parse_args()

    if args.validate:
        data = json.loads(Path(args.out).read_text(encoding="utf-8"))
        errors = validate(data)
        _report_validation(errors, data)
        return 1 if errors else 0

    questions, stats = build_all()
    if args.runtime_verify:
        _runtime_verify(questions)
    errors = validate(questions)
    if errors:
        print(f"validation FAILED with {len(errors)} error(s):", file=sys.stderr)
        for err in errors[:40]:
            print(f"  - {err}", file=sys.stderr)
        return 1

    payload = [{k: v for k, v in q.items() if not k.startswith("_")} for q in questions]
    Path(args.out).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"validation passed for {len(questions)} questions")
    print_report(questions, stats)
    print(f"\nwrote {len(payload)} questions -> {args.out}")
    return 0


def _report_validation(errors: list[str], data: list[dict]) -> None:
    if errors:
        print(f"validation FAILED with {len(errors)} error(s):", file=sys.stderr)
        for err in errors[:40]:
            print(f"  - {err}", file=sys.stderr)
    else:
        fmt_counts = {f: sum(1 for q in data if q.get("format") == f) for f in FORMATS}
        print(f"validation passed for {len(data)} questions: {fmt_counts}")


# ---------------------------------------------------------------------------
# Dev aid: run the Predict Output snippets where a local runtime exists
# ---------------------------------------------------------------------------
_RUNTIME: dict[str, tuple[str, str]] = {
    "Python": ("python", ".py"),
    "JavaScript": ("node", ".js"),
    "Java": ("java", ".java"),
}


def _runtime_verify(questions: list[dict]) -> None:
    bad = 0
    for q in questions:
        if q["format"] != "Predict Output":
            continue
        lang = q["language"]
        if lang not in _RUNTIME:
            continue
        try:
            got = _run_snippet(lang, q["code"])
        except Exception as exc:  # noqa: BLE001
            print(f"  ! {q['id']} could not run: {exc}", file=sys.stderr)
            continue
        want = q["accepted_answers"][0]
        if normalize_output(got) != normalize_output(want):
            bad += 1
            print(f"  MISMATCH {q['id']} want={want!r} got={got!r}", file=sys.stderr)
    print(f"runtime verification: {bad} mismatch(es)")


def _run_snippet(language: str, code: str) -> str:
    exe, suffix = _RUNTIME[language]
    with tempfile.TemporaryDirectory(prefix="nexv_") as tmp:
        if language == "Java":
            name = re.search(r"class\s+(\w+)", code)
            fname = (name.group(1) if name else "Main") + suffix
            path = Path(tmp) / fname
            path.write_text(code, encoding="utf-8")
            subprocess.run(["javac", str(path)], cwd=tmp, check=True, capture_output=True, timeout=120)
            proc = subprocess.run(["java", "-cp", tmp, path.stem], capture_output=True, timeout=120)
        else:
            path = Path(tmp) / ("snippet" + suffix)
            path.write_text(code, encoding="utf-8")
            proc = subprocess.run([exe, str(path)], capture_output=True, timeout=120)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode("utf-8", "replace")[:300])
        return proc.stdout.decode("utf-8", "replace")


if __name__ == "__main__":
    raise SystemExit(main())
