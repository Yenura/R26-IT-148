"""
Build QG Training Dataset v2 (canonical format)
-----------------------------------------------
Only examples with COMPLETE output fields are kept so the model learns the
canonical per-type output contract instead of Q-only incoherent rows.

  MCQ         -> Q: <question>\nO: opt1 | opt2 | opt3 | opt4\nA: <idx>
  Descriptive -> Q: <question>\nA: <answer>\nK: kw1, kw2, kw3
  Coding      -> Q: <question>\nL: <lang>\nT: <test_cases json>\nC: <complexity>

Sources (every kept row carries all fields for its type):
  - RAIGS MCQ rows            (3,150, have options_json + answer index)
  - External descriptive Q&A  (information.csv + Software Questions.csv)
  - LeetCode coding problems  (1,825, with example test cases)
  - data_loader templates     (30 MCQ + 15 coding)
  - question_bank.json        (690 descriptive + 30 MCQ + 15 coding)

The 14,300 descriptive + 2,550 coding RAIGS rows are deliberately DROPPED:
they are question prompts only (no reference answer / test cases), which is
what made v1 never learn the output format.

Output: models/qg_dataset_v2.json  {"train": [...], "val": [...]}
Guard:  re-running over an existing file is refused unless SKIP_EXISTING=1
        (or --force) is passed, mirroring build_qg_dataset.py.
"""

import argparse
import csv
import io
import json
import os
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR.parent / "Data_set"
MODELS_DIR = BASE_DIR / "models"
RAIGS_CSV_PATH = BASE_DIR / "raigs" / "RAIGS_generated_questions.csv"
OUTPUT_PATH = MODELS_DIR / "qg_dataset_v2.json"

LEVEL_TO_DIFFICULTY = {"Intern": "Easy", "Associate": "Medium", "Senior": "Hard"}
TYPE_TAG = {"mcq": "MCQ", "descriptive": "Descriptive", "coding": "Coding"}


def _load_roles() -> Dict[str, List[str]]:
    """Pull the 20-role taxonomy from raigs/generate.py (skills = first topics)."""
    try:
        from generate import ROLES as raigs_roles  # noqa: E402
        return {
            role: [t for t in topics[:6] if isinstance(t, str)]
            for role, meta in raigs_roles.items()
            for topics in ([meta] if isinstance(meta, list) else [meta.get("topics", [])])
        }
    except Exception:
        return {
            "Software Engineer": ["object-oriented design", "data structures", "REST APIs", "unit testing"],
            "Data Scientist": ["Python", "Machine Learning", "SQL", "Statistics"],
            "Machine Learning Engineer": ["neural networks", "gradient descent", "MLOps", "transformers"],
            "DevOps Engineer": ["CI/CD", "Docker", "Kubernetes", "Linux"],
            "Cloud Solutions Architect": ["AWS", "GCP", "Azure", "Cloud Architecture"],
        }


ROLES = _load_roles()
DIFFICULTIES = ["Easy", "Medium", "Hard"]


def _assign_role(category: str) -> tuple:
    """Best-effort role + skills based on the question category/topic text."""
    cat_lower = (category or "").lower()
    for role, skills in ROLES.items():
        for skill in skills:
            if skill.lower() in cat_lower or cat_lower in skill.lower():
                return role, skills
    return "Software Engineer", ROLES["Software Engineer"]


def _input_text(qtype: str, role: str, middle: str, difficulty: str) -> str:
    tag = TYPE_TAG.get(qtype.lower(), qtype.capitalize())
    return f"[{tag}] {role} | {middle} | {difficulty}"


# ---------------------------------------------------------------------------
# Formatters (canonical output contract)
# ---------------------------------------------------------------------------
def _fmt_mcq(ex: dict, role: str, middle: str, diff: str) -> dict:
    q = (ex.get("question_text") or "").strip()
    options = ex.get("options") or []
    if options and isinstance(options[0], dict):
        opt_str = " | ".join(o.get("text", "").strip() for o in options[:4] if o.get("text"))
    else:
        opt_str = " | ".join(str(o).strip() for o in options[:4] if str(o).strip())
    if not q or not opt_str:
        return None
    answer_idx = ex.get("correct_option", ex.get("correct_answer_index", 0))
    output = f"Q: {q}\nO: {opt_str}\nA: {answer_idx}"
    return {"input": _input_text("mcq", role, middle, diff), "output": output, "type": "mcq", "difficulty": diff}


def _clip_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(".,;:") + "..."


def _fmt_descriptive(ex: dict, role: str, middle: str, diff: str) -> dict:
    q = (ex.get("question_text") or "").strip()
    a = (ex.get("answer_text") or "").strip()
    if not q or not a:
        return None
    # Cap long reference answers so targets stay learnable on CPU (most
    # descriptive answers are < 100 words; only multi-paragraph dumps exceed).
    a = _clip_words(a, 100)
    keywords = ex.get("keywords") or []
    if isinstance(keywords, list):
        kw_str = ", ".join(str(k).strip() for k in keywords[:5] if str(k).strip())
    else:
        kw_str = str(keywords)
    output = f"Q: {q}\nA: {a}\nK: {kw_str}"
    return {"input": _input_text("descriptive", role, middle, diff), "output": output, "type": "descriptive", "difficulty": diff}


def _fmt_coding(ex: dict, role: str, middle: str, diff: str) -> dict:
    q = (ex.get("question_text") or "").strip()
    if not q:
        return None
    q = _clip_words(q, 60)
    lang = ex.get("language") or "Python"
    test_cases = (ex.get("test_cases") or [])[:2]
    complexity = ex.get("expected_complexity") or "O(n)"
    tc_str = json.dumps(test_cases, ensure_ascii=False)
    output = f"Q: {q}\nL: {lang}\nT: {tc_str}\nC: {complexity}"
    return {"input": _input_text("coding", role, middle, diff), "output": output, "type": "coding", "difficulty": diff}


# ---------------------------------------------------------------------------
# RAIGS CSV (MCQ rows only)
# ---------------------------------------------------------------------------
def _raigs_examples() -> List[dict]:
    if not os.path.isfile(RAIGS_CSV_PATH):
        print(f"[WARN] RAIGS CSV not found: {RAIGS_CSV_PATH}")
        return []
    examples = []
    with open(RAIGS_CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            qtype = (row.get("type") or "").lower()
            if qtype != "mcq":
                continue  # drop Q-only descriptive/coding rows
            role = (row.get("role") or "").strip()
            topic = (row.get("topic") or "").strip() or "General"
            diff = LEVEL_TO_DIFFICULTY.get((row.get("level") or "").strip(), "Medium")
            try:
                options = json.loads(row.get("options_json") or "[]")
            except (json.JSONDecodeError, ValueError):
                options = []
            ex = _fmt_mcq({
                "question_text": row.get("question_text", ""),
                "options": options,
                "correct_option": row.get("correct_answer_index", 0),
            }, role, topic, diff)
            if ex:
                examples.append(ex)
    print(f"[OK] RAIGS MCQ examples: {len(examples)}")
    return examples


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def build_dataset(force: bool = False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    print("=" * 60)
    print("Building QG Training Dataset v2 (canonical)")
    print("=" * 60)

    if OUTPUT_PATH.exists() and not force and os.environ.get("SKIP_EXISTING", "0") != "1":
        print(f"[WARN] {OUTPUT_PATH} already exists. Pass --force or set SKIP_EXISTING=1 to rebuild.")
        sys.exit(1)

    from data_loader import InterviewDataLoader
    loader = InterviewDataLoader(str(DATA_DIR))
    all_examples: List[dict] = []

    # 1. RAIGS MCQs (3,150)
    all_examples.extend(_raigs_examples())

    # 2. External descriptive Q&A (information.csv + Software Questions.csv + generic)
    for q in loader.load_all_dataset_folder_csvs():
        cat = q.get("category") or q.get("language") or "General"
        role, skills = _assign_role(cat)
        middle = q.get("topic") or ", ".join(skills[:4])
        ex = _fmt_descriptive(q, role, middle, q.get("difficulty") or "Medium")
        if ex:
            all_examples.append(ex)

    # 3. LeetCode coding problems (1,825)
    for q in loader.load_leetcode_dataset():
        role, skills = _assign_role(q.get("category") or "Algorithms")
        ex = _fmt_coding(q, role, q.get("topic") or ", ".join(skills[:4]), q.get("difficulty") or "Medium")
        if ex:
            all_examples.append(ex)

    # 4. Templates (30 MCQ + 15 coding)
    for q in loader.create_mcq_questions():
        role, skills = _assign_role(q.get("category") or "General")
        ex = _fmt_mcq(q, role, q.get("topic") or ", ".join(skills[:4]), q.get("difficulty") or "Medium")
        if ex:
            all_examples.append(ex)
    for q in loader.create_coding_questions():
        role, skills = _assign_role(q.get("category") or "Algorithms")
        ex = _fmt_coding(q, role, q.get("topic") or ", ".join(skills[:4]), q.get("difficulty") or "Medium")
        if ex:
            all_examples.append(ex)

    # 5. Question bank (690 descriptive + 30 MCQ + 15 coding)
    bank_path = MODELS_DIR / "question_bank.json"
    if bank_path.exists():
        with open(bank_path, encoding="utf-8") as f:
            bank = json.load(f)
        for q in bank:
            qtype = (q.get("question_type") or "").lower()
            role, skills = _assign_role(q.get("category") or q.get("topic") or "General")
            middle = q.get("topic") or ", ".join(skills[:4])
            diff = q.get("difficulty") or "Medium"
            if qtype == "mcq":
                ex = _fmt_mcq(q, role, middle, diff)
            elif qtype == "descriptive" and q.get("answer_text"):
                ex = _fmt_descriptive(q, role, middle, diff)
            elif qtype == "coding":
                ex = _fmt_coding(q, role, middle, diff)
            else:
                ex = None
            if ex:
                all_examples.append(ex)

    # 6. Dedup
    seen = set()
    unique = []
    for ex in all_examples:
        key = ex["input"] + "|" + ex["output"][:100]
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    all_examples = unique

    # 7. Report
    print(f"\n[OK] Total unique examples: {len(all_examples)}")
    type_counts = Counter(ex["type"] for ex in all_examples)
    diff_counts = Counter(ex["difficulty"] for ex in all_examples)
    for t, c in sorted(type_counts.items()):
        print(f"  - {t}: {c}")
    print(f"  Difficulty: {dict(diff_counts)}")

    # 8. Split 90/10
    random.seed(42)
    random.shuffle(all_examples)
    split_idx = int(len(all_examples) * 0.9)
    dataset = {"train": all_examples[:split_idx], "val": all_examples[split_idx:]}

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved to {OUTPUT_PATH}")
    print(f"  Train: {len(dataset['train'])} | Val: {len(dataset['val'])}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build canonical QG dataset v2")
    parser.add_argument("--force", action="store_true", help="Rebuild even if output exists")
    args = parser.parse_args()
    build_dataset(force=args.force)
