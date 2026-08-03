"""
Build QG Training Dataset
Merges existing QG data + LeetCode problems into a unified training set.
Output: models/qg_dataset.json
"""

import csv
import json
import os
import random
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent))
from data_loader import InterviewDataLoader

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR.parent / "Data_set"
MODELS_DIR = BASE_DIR / "models"
OUTPUT_PATH = MODELS_DIR / "qg_dataset.json"

# Role-skill mapping for generating diverse inputs
ROLES = {
    "Software Engineer": ["Java", "Python", "C++", "SQL", "React", "REST APIs"],
    "Data Scientist": ["Python", "Machine Learning", "SQL", "Deep Learning", "Statistics"],
    "AI Researcher": ["TensorFlow", "NLP", "Pytorch", "Deep Learning", "Python"],
    "Cybersecurity Analyst": ["Cybersecurity", "Networking", "Linux", "Ethical Hacking"],
    "Frontend Developer": ["React", "JavaScript", "CSS", "HTML", "TypeScript"],
    "Backend Developer": ["Python", "Java", "Node.js", "APIs", "SQL"],
    "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux"],
    "Database Administrator": ["SQL", "NoSQL", "MongoDB", "PostgreSQL", "Indexing"],
    "Cloud Solutions Architect": ["AWS", "GCP", "Azure", "Cloud Architecture"],
    "Mobile App Developer": ["React Native", "Flutter", "Kotlin", "Swift"],
}

DIFFICULTIES = ["Easy", "Medium", "Hard"]


def _assign_role_skill(category: str) -> tuple:
    """Assign a plausible role and skill list based on question category."""
    cat_lower = (category or "").lower()
    for role, skills in ROLES.items():
        for skill in skills:
            if skill.lower() in cat_lower or cat_lower in skill.lower():
                return role, skills
    # Default
    return "Software Engineer", ROLES["Software Engineer"]


def _format_descriptive(example: dict) -> dict:
    """Convert a descriptive Q&A example to QG training format."""
    q = example.get("question_text", "")
    a = example.get("answer_text", "")
    cat = example.get("category", "General")
    diff = example.get("difficulty", "Medium")
    role, skills = _assign_role_skill(cat)
    skill_str = ", ".join(skills[:4])

    input_text = f"[Descriptive] {role} | {skill_str} | {diff}"
    keywords = example.get("keywords", [])[:5]
    kw_str = ", ".join(keywords) if keywords else ", ".join(s.lower() for s in skills[:3])
    output_text = f"Q: {q}\nA: {a}\nK: {kw_str}"

    return {
        "input": input_text,
        "output": output_text,
        "type": "descriptive",
        "difficulty": diff,
    }


def _format_mcq(example: dict) -> dict:
    """Convert an MCQ example to QG training format."""
    q = example.get("question_text", "")
    options = example.get("options", [])
    correct_idx = example.get("correct_option", 0)
    cat = example.get("category", "General")
    diff = example.get("difficulty", "Medium")
    role, skills = _assign_role_skill(cat)
    skill_str = ", ".join(skills[:4])

    input_text = f"[MCQ] {role} | {skill_str} | {diff}"
    # Handle both list-of-strings and list-of-dicts formats
    if options and isinstance(options[0], dict):
        opt_str = " | ".join(o.get("text", "") for o in options[:4])
    else:
        opt_str = " | ".join(str(o) for o in options[:4])
    output_text = f"Q: {q}\nO: {opt_str}\nA: {correct_idx}"

    return {
        "input": input_text,
        "output": output_text,
        "type": "mcq",
        "difficulty": diff,
    }


def _format_coding(example: dict) -> dict:
    """Convert a coding example to QG training format."""
    q = example.get("question_text", "")
    test_cases = example.get("test_cases", [])
    lang = example.get("language", "Python")
    complexity = example.get("expected_complexity", "O(n)")
    cat = example.get("category", "Algorithms")
    diff = example.get("difficulty", "Medium")
    role, skills = _assign_role_skill(cat)
    skill_str = ", ".join(skills[:4])

    input_text = f"[Coding] {role} | {skill_str} | {diff}"
    tc_str = json.dumps(test_cases[:3], ensure_ascii=False)
    output_text = f"Q: {q}\nL: {lang}\nT: {tc_str}\nC: {complexity}"

    return {
        "input": input_text,
        "output": output_text,
        "type": "coding",
        "difficulty": diff,
    }


# ---------------------------------------------------------------------------
# RAIGS generated dataset (component2/raigs/RAIGS_generated_questions.csv)
# ---------------------------------------------------------------------------
RAIGS_CSV_PATH = BASE_DIR / "raigs" / "RAIGS_generated_questions.csv"
LEVEL_TO_DIFFICULTY = {"Intern": "Easy", "Associate": "Medium", "Senior": "Hard"}
_RAIGS_TYPE_TAG = {"mcq": "MCQ", "descriptive": "Descriptive", "coding": "Coding"}


def _raigs_row_to_qg(row: dict) -> dict:
    """Convert one RAIGS CSV row to QG training format.

    RAIGS provides question text, level, and topic per row. MCQ rows also
    carry options and a correct-answer index; descriptive/coding rows are
    question prompts only (no reference answer / test cases).
    """
    qtype = (row.get("type") or "").lower()
    qtext = (row.get("question_text") or "").strip()
    role = (row.get("role") or "").strip()
    topic = (row.get("topic") or "").strip()
    level = (row.get("level") or "").strip()
    difficulty = LEVEL_TO_DIFFICULTY.get(level, "Medium")
    tag = _RAIGS_TYPE_TAG.get(qtype, qtype.capitalize())

    input_text = f"[{tag}] {role} | {topic} | {difficulty}"
    if qtype == "mcq":
        options = []
        try:
            options = json.loads(row.get("options_json") or "[]")
        except (json.JSONDecodeError, ValueError):
            options = []
        if options and isinstance(options[0], dict):
            opt_str = " | ".join(o.get("text", "") for o in options[:4])
        else:
            opt_str = " | ".join(str(o) for o in options[:4])
        answer_idx = row.get("correct_answer_index", 0)
        output_text = f"Q: {qtext}\nO: {opt_str}\nA: {answer_idx}"
    else:
        output_text = f"Q: {qtext}"

    return {
        "input": input_text,
        "output": output_text,
        "type": qtype,
        "difficulty": difficulty,
    }


def _load_raigs_examples() -> List[dict]:
    """Load RAIGS generated questions and convert to QG training format."""
    if not os.path.isfile(RAIGS_CSV_PATH):
        print(f"[WARN] RAIGS CSV not found: {RAIGS_CSV_PATH}")
        return []
    examples = []
    with open(RAIGS_CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ex = _raigs_row_to_qg(row)
            if ex["input"] and ex["output"]:
                examples.append(ex)
    return examples


def build_dataset():
    """Build the complete QG training dataset."""
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("=" * 60)
    print("Building QG Training Dataset")
    print("=" * 60)

    loader = InterviewDataLoader(str(DATA_DIR))
    all_examples = []

    # 1. Load existing QG dataset (if present)
    existing_path = MODELS_DIR / "qg_dataset.json"
    if existing_path.exists():
        try:
            with open(existing_path, encoding="utf-8") as f:
                existing = json.load(f)
            train_existing = existing.get("train", [])
            all_examples.extend(train_existing)
            print(f"[OK] Loaded {len(train_existing)} existing QG examples")
        except Exception as e:
            print(f"[WARN] Could not load existing dataset: {e}")

    # 2. Load descriptive questions from CSVs
    try:
        csv_questions = loader.load_all_dataset_folder_csvs()
    except Exception as e:
        print(f"[WARN] Error loading CSV folder: {e}")
        csv_questions = []
    for q in csv_questions:
        all_examples.append(_format_descriptive(q))
    print(f"[OK] Converted {len(csv_questions)} CSV questions to QG format")

    # 3. Load LeetCode dataset (coding)
    leetcode_questions = loader.load_leetcode_dataset()
    for q in leetcode_questions:
        all_examples.append(_format_coding(q))
    print(f"[OK] Converted {len(leetcode_questions)} LeetCode problems to QG format")

    # 4. Add MCQ and Coding template questions from data_loader
    mcq_templates = loader.create_mcq_questions()
    coding_templates = loader.create_coding_questions()
    for q in mcq_templates:
        all_examples.append(_format_mcq(q))
    for q in coding_templates:
        all_examples.append(_format_coding(q))
    print(f"[OK] Added {len(mcq_templates)} MCQ + {len(coding_templates)} Coding templates")

    # 5. Add MCQ questions from question bank
    qbank_path = MODELS_DIR / "question_bank.json"
    if qbank_path.exists():
        with open(qbank_path, encoding="utf-8") as f:
            bank = json.load(f)
        mcq_count = 0
        for q in bank:
            if q.get("question_type") == "MCQ":
                all_examples.append(_format_mcq(q))
                mcq_count += 1
            elif q.get("question_type") == "Descriptive" and "answer_text" in q:
                all_examples.append(_format_descriptive(q))
            elif q.get("question_type") == "Coding":
                all_examples.append(_format_coding(q))
        print(f"[OK] Converted {mcq_count} MCQ + other questions from question bank")

    # 6. Add RAIGS generated questions (20 roles x 3 levels)
    raigs_examples = _load_raigs_examples()
    all_examples.extend(raigs_examples)
    print(f"[OK] Added {len(raigs_examples)} RAIGS generated questions")

    # 7. Deduplicate by input text
    seen = set()
    unique = []
    for ex in all_examples:
        key = ex["input"] + "|" + ex["output"][:100]
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    all_examples = unique
    print(f"\n[OK] Total unique examples: {len(all_examples)}")

    # 8. Count by type
    type_counts = {}
    for ex in all_examples:
        t = ex.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    for t, c in sorted(type_counts.items()):
        print(f"  - {t}: {c}")

    # 9. Shuffle and split (90/10)
    random.seed(42)
    random.shuffle(all_examples)
    split_idx = int(len(all_examples) * 0.9)
    train_set = all_examples[:split_idx]
    val_set = all_examples[split_idx:]

    dataset = {"train": train_set, "val": val_set}

    # 10. Save
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Saved to {OUTPUT_PATH}")
    print(f"  Train: {len(train_set)} | Val: {len(val_set)}")
    print("=" * 60)


if __name__ == "__main__":
    build_dataset()
