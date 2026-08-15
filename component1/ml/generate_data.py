"""
Dataset Preparation & Synthetic/Augmented CV Dataset Generator — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Generates and normalizes resume dataset for all 20 canonical IT job roles.
Applies text cleaning and anonymization (PII stripping: emails, phones, URLs, addresses).

Output:
------
  data/normalized_resumes.csv — complete dataset (200 samples per role = 4,000 total)
  data/train.csv              — 70% stratified train split (2,800 samples)
  data/val.csv                — 15% stratified validation split (600 samples)
  data/test.csv               — 15% stratified held-out test split (600 samples)
"""

import csv
import os
import random
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Ensure component1 root is in path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from data.role_requirements import ALL_ROLES, REQUIRED_SKILLS
from ml.extractor import clean_text

random.seed(42)

N_PER_ROLE = 200  # 200 samples per role = 4,000 total resumes
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── Templates for Realistic Resume Generation ─────────────────────────────────

SUMMARY_TEMPLATES = [
    "Experienced {role} with {n} years of hands-on expertise in {skill1}, {skill2}, and {skill3}. "
    "Passionate about delivering scalable, production-grade solutions in fast-paced engineering teams.",

    "Results-driven {role} skilled in {skill1}, {skill2}, and {skill3}. "
    "Proven track record of building and optimizing enterprise systems over {n}+ years.",

    "Dynamic {role} with a strong background in {skill1} and {skill2}. "
    "Adept at collaborating with cross-functional teams to solve complex technical challenges.",

    "Detail-oriented {role} with {n} years of professional experience. "
    "Core competencies: {skill1}, {skill2}, {skill3}. Strong analytical and problem-solving skills.",

    "Motivated {role} bringing {n} years of industry experience in {skill1} and {skill2}. "
    "Committed to continuous learning, code quality, and engineering best practices.",

    "Senior {role} with expertise across {skill1}, {skill2}, and {skill3}. "
    "Led multiple end-to-end projects and mentored junior team members over {n} years.",

    "Junior {role} with 1-2 years of experience in {skill1} and {skill2}. "
    "Eager to grow and contribute to innovative software and data engineering initiatives.",
]

EDUCATION_TEMPLATES = [
    "B.Sc. in Computer Science — State University (2018)",
    "B.Sc. in Software Engineering — Institute of Technology (2019)",
    "B.Sc. in Information Technology — SLIIT (2020)",
    "M.Sc. in Data Science — Tech University (2021)",
    "M.Sc. in Computer Science — National University (2020)",
    "B.Sc. in Computer Engineering — Engineering College (2017)",
    "Diploma in Information Technology — Technical Institute (2016)",
    "B.Sc. in Electrical & Electronic Engineering (2018)",
    "M.Sc. in Artificial Intelligence — University of Technology (2022)",
    "Ph.D. in Computer Science — Research University (2023)",
    "HND in Computing — Technical College (2015)",
]

EXPERIENCE_TEMPLATES = [
    "{role} at TechCorp (Jan {start_yr} – Present)\n"
    "  • Developed and maintained {skill1} and {skill2} based services.\n"
    "  • Collaborated with agile teams to deliver sprint goals.\n"
    "  • Improved system performance by 30% through {skill3} optimization.",

    "Associate {role} at Innovatech Solutions (Jun {start_yr} – Dec {end_yr})\n"
    "  • Built RESTful APIs and modules using {skill1}.\n"
    "  • Managed {skill2} deployments and CI/CD pipelines.\n"
    "  • Wrote unit and integration tests achieving 85% code coverage.",

    "Junior {role} at DataBridge (Mar {start_yr} – Feb {end_yr})\n"
    "  • Implemented {skill1} modules for production workloads.\n"
    "  • Assisted in designing {skill2} architectures.\n"
    "  • Participated in code reviews and documentation efforts.",

    "Senior {role} at Global Cloud Systems (Feb {start_yr} – Present)\n"
    "  • Spearheaded technical strategy using {skill1}, {skill2}, and {skill3}.\n"
    "  • Reduced infrastructure downtime by 40% using observability and automated failover.\n"
    "  • Mentored junior engineers and conducted technical interviews.",
]

CERTIFICATION_TEMPLATES = [
    "AWS Certified Solutions Architect",
    "Azure Certified Developer",
    "Certified Kubernetes Administrator (CKA)",
    "CCNA Network Associate",
    "CompTIA Security+",
    "Certified Ethical Hacker (CEH)",
    "Scrum Master (CSM)",
    "Oracle Certified Professional"
]


def generate_single_resume(role: str, resume_id: str) -> Dict[str, str]:
    """Generate a single clean, anonymized resume text for a target role."""
    req_skills = REQUIRED_SKILLS.get(role, ["python", "sql", "git"])
    
    # Pick 3-5 role-specific skills
    skills_sample = random.sample(req_skills, k=min(len(req_skills), random.randint(3, 5)))
    s1 = skills_sample[0]
    s2 = skills_sample[1] if len(skills_sample) > 1 else s1
    s3 = skills_sample[2] if len(skills_sample) > 2 else s1

    # Random experience years (1 to 10)
    exp_years = random.randint(1, 10)
    start_yr = 2026 - exp_years
    end_yr = start_yr + max(1, exp_years - 1)

    summary = random.choice(SUMMARY_TEMPLATES).format(
        role=role, n=exp_years, skill1=s1, skill2=s2, skill3=s3
    )

    edu = random.choice(EDUCATION_TEMPLATES)
    exp = random.choice(EXPERIENCE_TEMPLATES).format(
        role=role, start_yr=start_yr, end_yr=end_yr, skill1=s1, skill2=s2, skill3=s3
    )

    cert = random.choice(CERTIFICATION_TEMPLATES) if random.random() > 0.4 else "None"

    # All skills section
    additional_skills = random.sample(req_skills, k=min(len(req_skills), random.randint(4, len(req_skills))))
    skills_str = ", ".join(sorted(list(set(skills_sample + additional_skills))))

    raw_text = f"""
SUMMARY
{summary}

TECHNICAL SKILLS
{skills_str}

WORK EXPERIENCE
{exp}

EDUCATION
{edu}

CERTIFICATIONS
{cert}
"""

    cleaned_resume_text = clean_text(raw_text)

    return {
        "resume_id": resume_id,
        "resume_text": cleaned_resume_text,
        "job_role": role,
        "education": edu,
        "experience_years": str(exp_years),
        "skills": skills_str,
        "source": "SLIIT_Component1_Dataset"
    }


def generate_dataset(n_per_role: int = N_PER_ROLE) -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
    """Generates the full dataset and splits into train, val, and test sets."""
    all_records = []
    id_counter = 1000

    for role in ALL_ROLES:
        for _ in range(n_per_role):
            resume_id = f"CV-{id_counter}"
            id_counter += 1
            rec = generate_single_resume(role, resume_id)
            all_records.append(rec)

    # Stratified shuffle split
    role_groups = {}
    for r in all_records:
        role_groups.setdefault(r["job_role"], []).append(r)

    train_recs, val_recs, test_recs = [], [], []

    for role, group in role_groups.items():
        random.shuffle(group)
        n_total = len(group)
        n_train = int(n_total * TRAIN_RATIO)
        n_val = int(n_total * VAL_RATIO)

        train_recs.extend(group[:n_train])
        val_recs.extend(group[n_train:n_train + n_val])
        test_recs.extend(group[n_train + n_val:])

    # Write files
    fieldnames = ["resume_id", "resume_text", "job_role", "education", "experience_years", "skills", "source"]

    def _write_csv(path: Path, data: List[Dict]):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    _write_csv(DATA_DIR / "normalized_resumes.csv", all_records)
    _write_csv(DATA_DIR / "train.csv", train_recs)
    _write_csv(DATA_DIR / "val.csv", val_recs)
    _write_csv(DATA_DIR / "test.csv", test_recs)

    print(f"Dataset generated successfully:")
    print(f"  Total records: {len(all_records)} ({n_per_role} per role across 20 roles)")
    print(f"  Train: {len(train_recs)}, Val: {len(val_recs)}, Test: {len(test_recs)}")

    return all_records, train_recs, val_recs, test_recs


if __name__ == "__main__":
    generate_dataset(N_PER_ROLE)
