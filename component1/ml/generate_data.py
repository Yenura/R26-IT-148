"""Synthetic resume dataset generator — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Generates N synthetic resume texts per role (default 150) covering all 20 canonical
roles. Applies realistic variation in:
  - Professional summaries
  - Skills sections
  - Experience descriptions (including date ranges)
  - Education backgrounds

Output
------
  data/synthetic_resumes.csv   — columns: role, text
  data/train.csv               — 60 % split
  data/val.csv                 — 15 % split
  data/test.csv                — 25 % split (held-out)

Run from inside component1/:
    python ml/generate_data.py
"""

from __future__ import annotations

import csv
import os
import random
import sys
from pathlib import Path
from typing import List

# Allow imports from component1 root
sys.path.insert(0, str(Path(__file__).parent.parent))
from data.role_requirements import ALL_ROLES, REQUIRED_SKILLS

random.seed(42)

N_PER_ROLE   = 150
TRAIN_RATIO  = 0.60
VAL_RATIO    = 0.15
# TEST_RATIO  = 0.25  (remainder)

OUT_DIR = Path(__file__).parent.parent / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Template banks ─────────────────────────────────────────────────────────────

SUMMARY_TEMPLATES = [
    "Experienced {role} with {n} years of hands-on expertise in {skill1} and {skill2}. "
    "Passionate about delivering high-quality solutions in fast-paced environments.",

    "Results-driven {role} skilled in {skill1}, {skill2}, and {skill3}. "
    "Proven track record of delivering scalable, production-ready systems over {n}+ years.",

    "Dynamic {role} with a strong background in {skill1} and {skill2}. "
    "Adept at collaborating with cross-functional teams to solve complex technical challenges.",

    "Detail-oriented {role} with {n} years of professional experience. "
    "Core competencies: {skill1}, {skill2}, {skill3}. Strong analytical and problem-solving skills.",

    "Motivated {role} bringing {n} years of industry experience in {skill1} and {skill2}. "
    "Committed to continuous learning and adopting best practices.",

    "Senior {role} with expertise across {skill1}, {skill2}, and {skill3}. "
    "Led multiple end-to-end projects and mentored junior team members.",

    "Junior {role} with 1 year of experience in {skill1} and {skill2}. "
    "Eager to grow and contribute to innovative projects.",
]

EDUCATION_TEMPLATES = [
    "B.Sc. in Computer Science — University of Colombo (2018)",
    "B.Sc. in Software Engineering — SLIIT (2019)",
    "B.Sc. in Information Technology — University of Moratuwa (2020)",
    "M.Sc. in Data Science — University of Edinburgh (2021)",
    "M.Sc. in Computer Science — University of Auckland (2020)",
    "B.Sc. in Computer Engineering — University of Kelaniya (2017)",
    "Diploma in Information Technology — NIBM (2016)",
    "B.Sc. in Electrical Engineering — University of Peradeniya (2018)",
    "M.Sc. in Artificial Intelligence — University of Manchester (2022)",
    "Ph.D. in Computer Science — University of Melbourne (2023)",
    "B.Sc. in Mathematics and Computer Science — University of Ruhuna (2019)",
    "HND in Computing — Pearson (2015)",
]

EXPERIENCE_TEMPLATES = [
    "{role} at TechCorp Pvt Ltd (Jan {start_yr} – Present)\n"
    "  • Developed and maintained {skill1} and {skill2} based services.\n"
    "  • Collaborated with agile teams to deliver sprint goals.\n"
    "  • Improved system performance by 30%% through {skill3} optimisation.",

    "Associate {role} at Innovatech Solutions (Jun {start_yr} – Dec {end_yr})\n"
    "  • Built RESTful APIs using {skill1}.\n"
    "  • Managed {skill2} deployments and CI/CD pipelines.\n"
    "  • Wrote unit and integration tests achieving 85%% code coverage.",

    "Junior {role} at DataBridge (Mar {start_yr} – Feb {end_yr})\n"
    "  • Implemented {skill1} modules for production workloads.\n"
    "  • Assisted in designing {skill2} architectures.\n"
    "  • Participated in code reviews and documentation efforts.",

    "Senior {role} at CloudBase Ltd (Aug {start_yr} – Present)\n"
    "  • Architected scalable {skill1} solutions serving 1M+ users.\n"
    "  • Mentored a team of 5 engineers in {skill2} best practices.\n"
    "  • Reduced infrastructure costs by 40%% using {skill3}.",

    "Contract {role} at Synapse Systems (Apr {start_yr} – Sep {end_yr})\n"
    "  • Delivered {skill1} feature sets within tight deadlines.\n"
    "  • Integrated {skill2} with third-party APIs.\n"
    "  • Documented all modules following company standards.",
]

SKILLS_PREFIX = [
    "Technical Skills:", "Core Skills:", "Key Technologies:", "Skills & Tools:",
    "Competencies:", "Technologies:", "Expertise:",
]


def _pick_skills(role: str, n: int = 5) -> List[str]:
    pool = REQUIRED_SKILLS.get(role, [])
    if len(pool) >= n:
        return random.sample(pool, n)
    return pool + random.sample(pool, n - len(pool)) if pool else []


def _generate_resume(role: str) -> str:
    skills = _pick_skills(role, 6)
    if len(skills) < 3:
        skills = (skills * 3)[:6]

    n_years   = random.randint(1, 8)
    start_yr  = 2024 - n_years
    end_yr    = start_yr + random.randint(1, max(1, n_years - 1))

    summary_tmpl = random.choice(SUMMARY_TEMPLATES)
    summary = summary_tmpl.format(
        role=role,
        n=n_years,
        skill1=skills[0],
        skill2=skills[1] if len(skills) > 1 else skills[0],
        skill3=skills[2] if len(skills) > 2 else skills[0],
    )

    exp_tmpl = random.choice(EXPERIENCE_TEMPLATES)
    experience = exp_tmpl.format(
        role=role,
        start_yr=start_yr,
        end_yr=end_yr,
        skill1=skills[0],
        skill2=skills[1] if len(skills) > 1 else skills[0],
        skill3=skills[2] if len(skills) > 2 else skills[0],
    )

    education = random.choice(EDUCATION_TEMPLATES)
    skills_header = random.choice(SKILLS_PREFIX)
    skills_line   = ", ".join(skills)

    # Add extra random skills for realism
    extra = random.sample(
        ["Git", "Linux", "Agile", "Scrum", "Jira", "REST APIs", "SQL", "Python", "Docker"],
        k=random.randint(2, 5),
    )
    all_skills_line = skills_line + ", " + ", ".join(extra)

    resume = (
        f"PROFESSIONAL SUMMARY\n{summary}\n\n"
        f"{skills_header}\n{all_skills_line}\n\n"
        f"WORK EXPERIENCE\n{experience}\n\n"
        f"EDUCATION\n{education}\n"
    )
    return resume


def generate(n_per_role: int = N_PER_ROLE):
    records = []
    for role in ALL_ROLES:
        for _ in range(n_per_role):
            text = _generate_resume(role)
            records.append({"role": role, "text": text})

    random.shuffle(records)

    # Write full dataset
    full_path = OUT_DIR / "synthetic_resumes.csv"
    _write_csv(full_path, records)
    print(f"[generate_data] Total records: {len(records)} → {full_path}")

    # Split per role to maintain class balance
    train_rows, val_rows, test_rows = [], [], []
    for role in ALL_ROLES:
        role_records = [r for r in records if r["role"] == role]
        n = len(role_records)
        n_train = int(n * TRAIN_RATIO)
        n_val   = int(n * VAL_RATIO)
        train_rows.extend(role_records[:n_train])
        val_rows.extend(role_records[n_train:n_train + n_val])
        test_rows.extend(role_records[n_train + n_val:])

    random.shuffle(train_rows)
    random.shuffle(val_rows)
    random.shuffle(test_rows)

    _write_csv(OUT_DIR / "train.csv", train_rows)
    _write_csv(OUT_DIR / "val.csv",   val_rows)
    _write_csv(OUT_DIR / "test.csv",  test_rows)

    print(f"[generate_data] Train: {len(train_rows)} | Val: {len(val_rows)} | Test: {len(test_rows)}")
    return train_rows, val_rows, test_rows


def _write_csv(path: Path, rows: list):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["role", "text"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    generate()
