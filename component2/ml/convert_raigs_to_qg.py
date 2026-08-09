"""
Convert RAIGS CSV to QG training dataset format.
Also merges with existing qg_dataset_v2.json for maximum data.
"""
import csv
import json
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "raigs", "RAIGS_generated_questions.csv")
V2_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "qg_dataset_v2.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "qg_dataset_raigs.json")

LEVEL_MAP = {"Intern": "Easy", "Associate": "Medium", "Senior": "Hard"}

def mcq_output(row):
    options = json.loads(row["options_json"]) if row.get("options_json") else []
    opt_text = "|".join(o["text"] for o in options)
    correct = row.get("correct_answer_index", "0")
    return f"Q: {row['question_text']}\nO: {opt_text}\nA: {correct}"

def descriptive_output(row):
    return f"Q: {row['question_text']}"

def coding_output(row):
    return f"Q: {row['question_text']}\nL: Python\nT: []\nC: O(n)"

def main():
    samples = []
    with open(CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            qtype = row["type"].lower()
            difficulty = LEVEL_MAP.get(row.get("level", ""), "Medium")
            role = row["role"]
            topic = row.get("topic", "")

            input_text = f"[{qtype.title()}] {role} | {topic} | {difficulty}"

            if qtype == "mcq":
                output = mcq_output(row)
            elif qtype == "descriptive":
                output = descriptive_output(row)
            elif qtype == "coding":
                output = coding_output(row)
            else:
                continue

            samples.append({
                "input": input_text,
                "output": output,
                "type": qtype,
                "difficulty": difficulty,
            })

    print(f"RAIGS samples: {len(samples)}")

    # Merge with existing v2 dataset
    if os.path.exists(V2_PATH):
        with open(V2_PATH, encoding="utf-8") as f:
            v2 = json.load(f)
        existing = v2.get("train", []) + v2.get("val", [])
        print(f"Existing v2 samples: {len(existing)}")
        samples.extend(existing)
        print(f"Total merged: {len(samples)}")

    # Split 90/10
    import random
    random.seed(42)
    random.shuffle(samples)
    split = int(len(samples) * 0.9)
    dataset = {"train": samples[:split], "val": samples[split:]}

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"Saved: {OUTPUT_PATH}")
    print(f"  Train: {len(dataset['train'])}")
    print(f"  Val: {len(dataset['val'])}")

    # Stats
    from collections import Counter
    types = Counter(s["type"] for s in samples)
    print(f"  By type: {dict(types)}")

if __name__ == "__main__":
    main()
