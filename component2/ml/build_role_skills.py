"""Build a per-role skill profile from real LinkedIn job postings.

Source: Kaggle ``asaniczka/data-science-job-postings-and-skills`` (ODC-By,
commercial use permitted with attribution).  It is the only licence-clean set
with a machine-extracted ``skills`` column; the larger
``1-3m-linkedin-jobs-and-skills`` set is not downloadable with the current
credentials, and the Upwork set has no skills column (free-text descriptions
only, which would require guessing the vocabulary we are trying to learn).

The output is *evidence*, not a replacement for the curated list in
``job_requirements.json``: it records, per role, how many real postings mention
each skill.  ``--apply`` can then supplement the curated list, but only for
roles with enough postings and only with skills above a frequency floor.

Coverage caveat: this dataset is data/ML-focused, so it can only speak to the
data-adjacent roles (see the report it writes).  It is silent on frontend,
mobile, embedded, security and networking roles, and the report says so rather
than inventing skills for them.

Usage
-----
    python ml/build_role_skills.py                 # report only
    python ml/build_role_skills.py --apply         # also write the supplement
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
DEFAULT_DATA = (
    Path(r"C:\Users\ASUS\AppData\Local\Temp\opencode\datasets\kaggle")
    / "data-science-job-postings-and-skills"
)

SOURCE = "asaniczka/data-science-job-postings-and-skills"
SOURCE_URL = "https://www.kaggle.com/datasets/asaniczka/data-science-job-postings-and-skills"
LICENCE = "ODC-By-1.0 (Open Data Commons Attribution License)"
ATTRIBUTION = (
    "Skills profiles derived from the Kaggle dataset "
    f"'{SOURCE}' by asaniczka, licensed {LICENCE}."
)

# Title -> role, most specific first.  A title that matches nothing is left
# unassigned rather than guessed: a wrong skill profile is worse than a missing
# one.
ROLE_PATTERNS: List[Tuple[str, str]] = [
    ("AI/NLP Engineer", r"\b(nlp|natural language|llm|large language|conversational ai|speech|computer vision)\b"),
    ("Data Scientist", r"\b(data scientist|decision scientist|machine learning scientist)\b"),
    ("Machine Learning Engineer", r"\b(machine learning|ml|deep learning|ai) (engineer|engineering)\b|\bmlops\b"),
    ("Data Engineer", r"\b(data engineer|etl|analytics engineer|data platform|data warehouse)\b"),
    ("Database Administrator", r"\b(database administrator|dba|database engineer|database developer)\b"),
    ("Site Reliability Engineer", r"\b(site reliability|sre)\b"),
    ("DevOps Engineer", r"\bdevops\b|\bplatform engineer\b|\binfrastructure engineer\b"),
    ("QA/Test Automation Engineer", r"\b(qa|quality assurance|test automation|sdet|automation test)\b"),
    ("Cybersecurity Analyst", r"\b(security analyst|cyber ?security|soc analyst|penetration test)\b"),
    ("Network Engineer", r"\bnetwork (engineer|administrator|architect)\b"),
    ("Cloud Solutions Architect", r"\b(cloud|solutions?) architect\b|\bcloud engineer\b"),
    ("Embedded Systems Engineer", r"\bembedded\b|\bfirmware\b"),
    ("Blockchain Developer", r"\b(blockchain|solidity|web3)\b"),
    ("Mobile App Developer", r"\b(android|ios|mobile) (developer|engineer)\b|\bmobile app\b"),
    ("Full Stack Developer", r"\bfull ?stack\b"),
    ("Frontend Developer", r"\bfront ?end\b|\breact (developer|engineer)\b|\bui developer\b"),
    ("Backend Developer", r"\bback ?end\b|\bapi developer\b|\bserver[- ]side\b"),
    ("UI/UX Designer", r"\b(ui|ux|product) designer\b"),
    ("Business/Systems Analyst", r"\b(business|systems) analyst\b|\bbusiness systems\b"),
    ("Software Engineer", r"\bsoftware (engineer|developer)\b|\bprogrammer\b"),
]

_COMPILED = [(role, re.compile(pat, re.I)) for role, pat in ROLE_PATTERNS]

# Entries that are not skills at all: soft attributes, degrees and institutions.
# Matching a question against "Computer Science" or "Flexibility" tells us
# nothing about the role, and including them would pollute the relevance filter.
NOISE = {
    "communication", "communication skills", "teamwork", "leadership",
    "problem solving", "problem-solving", "analytical skills",
    "written communication", "verbal communication", "time management",
    "collaboration", "attention to detail", "organizational skills",
    "interpersonal skills", "critical thinking", "presentation skills",
    "project management", "agile", "scrum", "english", "microsoft office",
    "microsoft office suite", "excel", "powerpoint", "word",
    "computer science", "information systems", "engineering", "mathematics",
    "physics", "statistics degree", "bachelor's degree", "master's degree",
    "phd", "msc", "bsc", "degree", "flexibility", "autonomy", "self-starter",
    "detail oriented", "fast-paced environment", "remote", "full-time",
    "contract", "benefits", "experience", "product ownership",
    "teamfirst mentality", "team-first mentality", "ownership",
}

# Skill spellings that mean the same thing; keep the canonical form.
CANONICAL = {
    "amazon web services": "AWS", "aws": "AWS", "gcp": "GCP",
    "google cloud platform": "GCP", "azure": "Azure",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "mongo": "MongoDB", "mongodb": "MongoDB",
    "k8s": "Kubernetes", "kubernetes": "Kubernetes",
    "ml": "Machine Learning", "machine learning": "Machine Learning",
    "dl": "Deep Learning", "deep learning": "Deep Learning",
    "nlp": "NLP", "natural language processing": "NLP",
    "sql": "SQL", "python": "Python", "java": "Java", "scala": "Scala",
    "spark": "Spark", "apache spark": "Spark", "airflow": "Airflow",
    "apache airflow": "Airflow", "snowflake": "Snowflake",
    "databricks": "Databricks", "kafka": "Kafka", "apache kafka": "Kafka",
    "scikitlearn": "Scikit-learn", "scikit learn": "Scikit-learn",
    "scikit-learn": "Scikit-learn", "sklearn": "Scikit-learn",
    "tensorflow": "TensorFlow", "pytorch": "PyTorch", "hadoop": "Hadoop",
    "apache hadoop": "Hadoop", "snowflake": "Snowflake", "tableau": "Tableau",
    "power bi": "Power BI", "powerbi": "Power BI", "redshift": "Redshift",
    "amazon redshift": "Redshift", "hive": "Hive", "apache hive": "Hive",
    "mongodb": "MongoDB", "mysql": "MySQL", "oracle": "Oracle",
    "sql server": "SQL Server", "microsoft sql server": "SQL Server",
    "pl/sql": "PL/SQL", "plsql": "PL/SQL", "terraform": "Terraform",
}


def classify(title: str) -> str | None:
    """Map a job title to one of the 20 roles, or None when it is ambiguous."""
    text = str(title or "").strip()
    if not text:
        return None
    for role, pattern in _COMPILED:
        if pattern.search(text):
            return role
    return None


def parse_skills(raw: str) -> List[Tuple[str, str]]:
    """Split the dataset's comma-separated skill column into (key, surface) pairs.

    The key is the canonical lowercase identity, so "Power BI" and "PowerBI"
    count as one skill; the surface form is kept so the report can display the
    spelling that actually occurs.
    """
    out: List[Tuple[str, str]] = []
    for part in str(raw or "").split(","):
        name = part.strip()
        if not name or len(name) > 40:
            continue
        key = re.sub(r"\s+", " ", name.lower()).strip()
        if key in NOISE:
            continue
        canon = CANONICAL.get(key)
        if canon is not None:
            out.append((canon.lower(), canon))
        else:
            out.append((key, name))
    return out


def _count_role(group: pd.DataFrame) -> Tuple[Counter, Dict[str, Counter]]:
    """Count skills once per posting, merging spellings of the same skill."""
    per_key: Counter = Counter()
    surfaces: Dict[str, Counter] = {}

    for raw in group["job_skills"]:
        seen = set()
        for key, surface in parse_skills(raw):
            surfaces.setdefault(key, Counter())[surface] += 1
            if key in seen:
                continue
            seen.add(key)
            per_key[key] += 1

    return per_key, surfaces


def _confidence(n: int) -> str:
    """How much this dataset can be trusted for a role.

    The corpus is data/ML-focused, so a small sample is not merely small -- it is
    usually a handful of data-flavoured postings for a role that is really about
    something else.  The thresholds are about sample size *and* that skew.
    """
    if n >= 300:
        return "high"
    if n >= 100:
        return "medium"
    if n >= 50:
        return "low"
    return "none"


def build(data_dir: Path, min_postings: int, top: int) -> Dict:
    postings = pd.read_csv(data_dir / "job_postings.csv", usecols=["job_link", "job_title"])
    skills = pd.read_csv(data_dir / "job_skills.csv")

    frame = postings.merge(skills, on="job_link", how="inner")
    frame["role"] = frame["job_title"].map(classify)

    assigned = frame[frame["role"].notna()]
    print(f"postings read      : {len(frame):,}")
    print(f"assigned to a role : {len(assigned):,} ({len(assigned) / max(len(frame), 1):.1%})")

    profiles: Dict[str, Dict] = {}
    for role, group in assigned.groupby("role"):
        n = len(group)
        counts, surfaces = _count_role(group)
        floor = max(3, int(n * 0.05))
        observed: List[Tuple[str, int]] = []
        for key, c in counts.most_common():
            if c < floor:
                break
            display = surfaces[key].most_common(1)[0][0] if surfaces.get(key) else key
            observed.append((display, c))
            if len(observed) >= top:
                break
        profiles[str(role)] = {
            "postings": int(n),
            "confidence": _confidence(n),
            "observed": [s for s, _ in observed],
            "evidence": {s: c for s, c in observed},
            "share": {s: round(c / n, 3) for s, c in observed},
            "usable": bool(n >= min_postings),
        }

    return {
        "_provenance": {
            "source": SOURCE,
            "url": SOURCE_URL,
            "licence": LICENCE,
            "attribution": ATTRIBUTION,
            "method": (
                "job_title classified into the role taxonomy by regex; skills "
                "counted once per posting from the dataset's machine-extracted "
                "skills column; generic soft skills removed"
            ),
            "min_postings_for_use": min_postings,
            "rows_read": int(len(frame)),
            "rows_assigned": int(len(assigned)),
        },
        "roles": profiles,
    }


def bank_coverage(profiles: Dict, bank_path: Path, min_hits: int = 1) -> Dict[str, Dict]:
    """Which observed market skills the question bank can actually assess.

    The relevance filter in ``ml_engine`` matches a skill as a substring of a
    question's category/topic/text.  A skill with no matching question cannot
    improve selection -- adding it to ``job_requirements.json`` would only add
    noise to the employer's view of the role.  This is the measurement that
    decides whether applying the enrichment is worth anything.
    """
    if not bank_path.exists():
        return {}

    bank = json.loads(bank_path.read_text(encoding="utf-8"))
    haystack = [
        " ".join(
            str(q.get(field, "")) for field in ("category", "topic", "question_text")
        ).lower()
        for q in bank
    ]

    out: Dict[str, Dict] = {}
    for role, data in profiles.items():
        if not data["usable"]:
            continue
        covered, blind = [], []
        for skill in data["observed"]:
            needle = skill.lower()
            hits = sum(1 for hay in haystack if needle in hay)
            (covered if hits >= min_hits else blind).append({"skill": skill, "questions": hits})
        out[role] = {
            "covered": covered,
            "blind_spots": blind,
            "coverage": round(len(covered) / max(len(covered) + len(blind), 1), 3),
        }
    return out


def compare_with_curated(profiles: Dict, curated: Dict[str, List[str]]) -> Dict[str, Dict]:
    """What the market asks for that the curated list does not cover."""
    out: Dict[str, Dict] = {}
    for role, data in profiles.items():
        if not data["usable"]:
            continue
        have = {s.lower() for s in curated.get(role, [])}
        missing = [s for s in data["observed"] if s.lower() not in have]
        extra = [s for s in curated.get(role, []) if s.lower() not in {o.lower() for o in data["observed"]}]
        out[role] = {
            "market_only": missing,
            "curated_only": extra,
            "postings": data["postings"],
        }
    return out


def write_report(path: Path, profiles: Dict, diff: Dict, curated: Dict,
                 coverage: Dict[str, Dict]) -> None:
    lines = [
        "# Per-role skills observed in real job postings",
        "",
        f"Source: `{SOURCE}` — {LICENCE}.",
        "",
        ATTRIBUTION,
        "",
        "Generated by `component2/ml/build_role_skills.py`. Do not hand-edit.",
        "",
        "## Why this is evidence, not a replacement",
        "",
        "`job_requirements.json` stays the curated, reviewed list. This report "
        "records what real postings actually ask for so drift is visible. The "
        "dataset is data/ML-focused: roles it cannot speak to are listed as "
        "**no signal** rather than given invented skills.",
        "",
        "## Coverage",
        "",
        "| Role | Postings | Confidence |",
        "|---|---|---|",
    ]
    for role in sorted(profiles):
        d = profiles[role]
        lines.append(f"| {role} | {d['postings']:,} | {d['confidence']} |")

    unassigned = [r for r in curated if r not in profiles]
    lines += ["", f"Roles with no postings at all: {', '.join(sorted(unassigned)) or '—'}.", ""]

    lines += ["## Market skills missing from the curated list", ""]
    if not diff:
        lines.append("_No role had enough postings._")
    for role in sorted(diff):
        d = diff[role]
        lines += [
            f"### {role} — {d['postings']:,} postings",
            "",
            f"* Asked for in the market, absent from `job_requirements.json`: "
            f"{', '.join(d['market_only']) or '—'}",
            f"* Curated but not prominent in these postings: "
            f"{', '.join(d['curated_only']) or '—'}",
            "",
        ]

    if coverage:
        lines += [
            "## Can the question bank actually assess these skills?",
            "",
            "A skill with no matching question cannot improve selection: the "
            "relevance filter matches a skill as a substring of a question's "
            "category/topic/text, so adding an uncovered skill to "
            "`job_requirements.json` would only add noise. This is why the "
            "enrichment is **not** applied to selection automatically.",
            "",
            "| Role | Observed skills covered by the bank | Blind spots |",
            "|---|---|---|",
        ]
        for role in sorted(coverage):
            c = coverage[role]
            lines.append(
                f"| {role} | {len(c['covered'])}/{len(c['covered']) + len(c['blind_spots'])} "
                f"({c['coverage']:.0%}) | {', '.join(b['skill'] for b in c['blind_spots']) or '—'} |"
            )
        lines.append("")

        for role in sorted(coverage):
            c = coverage[role]
            if not c["blind_spots"]:
                continue
            lines += [
                f"### {role} — blind spots worth adding to the bank",
                "",
                ", ".join(f"{b['skill']} ({b['questions']} questions)" for b in c["blind_spots"]),
                "",
            ]

    lines += [
        "## Top observed skills per role",
        "",
    ]
    for role in sorted(profiles):
        d = profiles[role]
        if not d["usable"]:
            continue
        top = ", ".join(f"{s} ({d['share'][s]:.0%})" for s in d["observed"][:12])
        lines += [f"### {role}", "", top, ""]

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--min-postings", type=int, default=300,
                    help="postings needed before a role's profile is applied")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--apply", action="store_true",
                    help="also write models/role_skills_external.json")
    args = ap.parse_args()

    if not (args.data / "job_postings.csv").exists():
        raise SystemExit(f"dataset not found at {args.data}")

    curated_path = MODELS / "job_requirements.json"
    curated = json.loads(curated_path.read_text(encoding="utf-8"))

    profiles = build(args.data, args.min_postings, args.top)
    diff = compare_with_curated(profiles["roles"], curated)
    coverage = bank_coverage(profiles["roles"], MODELS / "question_bank.json")

    report = MODELS / "role_skills_report.md"
    write_report(report, profiles["roles"], diff, curated, coverage)
    print(f"\nwrote {report}")

    unusable = [r for r, d in profiles["roles"].items() if not d["usable"]]
    print(f"roles with usable signal: {len(profiles['roles']) - len(unusable)}")
    print(f"roles without enough postings: {', '.join(sorted(unusable)) or '—'}")
    for role in sorted(coverage):
        c = coverage[role]
        print(f"  {role:28s} bank covers {c['coverage']:.0%} of observed skills")

    if args.apply:
        out = MODELS / "role_skills_external.json"
        payload = {**profiles, "_comparison": diff, "_bank_coverage": coverage}
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
