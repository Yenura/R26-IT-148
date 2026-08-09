"""
Rebuild question_bank.json from RAIGS CSV for diverse fallback.
"""
import csv
import json
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "raigs", "RAIGS_generated_questions.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "question_bank.json")

LEVEL_MAP = {"Intern": "Easy", "Associate": "Medium", "Senior": "Hard"}

def main():
    bank = []
    with open(CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            qtype = row["type"].lower()
            difficulty = LEVEL_MAP.get(row.get("level", ""), "Medium")
            topic = row.get("topic", "General")

            if qtype == "mcq":
                options = json.loads(row["options_json"]) if row.get("options_json") else []
                question_type = "MCQ"
            elif qtype == "descriptive":
                options = []
                question_type = "Descriptive"
            elif qtype == "coding":
                options = []
                question_type = "Coding"
            else:
                continue

            entry = {
                "id": f"RAIGS_{row['id']}",
                "question_type": question_type,
                "difficulty": difficulty,
                "category": topic,
                "topic": topic,
                "question_text": row["question_text"],
            }
            if qtype == "mcq":
                entry["options"] = options
                entry["correct_answer_index"] = int(row.get("correct_answer_index", 0))

            bank.append(entry)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)

    print(f"Rebuilt question bank: {len(bank)} questions")
    from collections import Counter
    types = Counter(q["question_type"] for q in bank)
    cats = Counter(q["category"] for q in bank)
    print(f"  By type: {dict(types)}")
    print(f"  Categories: {len(cats)} unique")
    print(f"  Top 10: {cats.most_common(10)}")

if __name__ == "__main__":
    main()
