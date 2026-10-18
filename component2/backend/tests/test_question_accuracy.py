"""
Component 2: Question Accuracy Test

Validates that interview questions selected for a job role are actually
relevant to that role's job description and required skills.

Metrics per role:
  - skill_coverage  : % of job-description skills touched by >= 1 question
  - question_relevance : % of selected questions matching >= 1 required skill
  - off_topic       : selected questions matching NO required skill (fallback noise)
  - overall_accuracy: 0.4 * skill_coverage + 0.6 * question_relevance

Runs two passes:
  1. "role"  : synthetic JD built from the role's default skills
  2. "mock"  : realistic free-text JD excerpts (tests the JD -> skills extractor)

Run directly:   python tests/test_question_accuracy.py
Run via pytest: python -m pytest tests/test_question_accuracy.py -v -s
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.skill_aliases import skill_matchesAny  # noqa: E402
from services.ml_engine import InterviewService  # noqa: E402
from services.qg_engine import merge_skill_lists  # noqa: E402

MODELS_DIR = str(Path(__file__).parent.parent.parent / "models")

# The product is specified with exactly 20 job positions. Every layer must
# agree on this count (models config, backend API, frontend selectors).
EXPECTED_JOB_COUNT = 20

# Realistic mock job descriptions used for pass 2 (free-text extraction test).
MOCK_JDS = {
    "Frontend Developer": (
        "We are looking for a Frontend Developer to build responsive web apps. "
        "You will work with React, TypeScript and modern CSS. Experience with "
        "JavaScript, HTML, accessibility and REST APIs is required. Familiarity "
        "with Vue is a plus."
    ),
    "Backend Developer": (
        "Seeking a Backend Developer to design scalable services. Strong Python "
        "or Java, building REST APIs and microservices, SQL and database design. "
        "Experience with authentication and Node.js is a plus."
    ),
    "Data Scientist": (
        "Data Scientist needed for modelling and analysis. Must know Python, "
        "Machine Learning, statistics, Pandas, NumPy and SQL. Deep Learning "
        "experience is a bonus."
    ),
    "DevOps Engineer": (
        "DevOps Engineer to own our platform. Required: Docker, Kubernetes, "
        "CI/CD pipelines, AWS, Linux, Terraform and Git. Monitoring experience "
        "with Prometheus is desired."
    ),
    "UI/UX Designer": (
        "UI/UX Designer to craft delightful interfaces. Proficiency in Figma, "
        "user research, wireframing, prototyping and design systems. Usability "
        "testing experience required."
    ),
    "Mobile App Developer": (
        "Mobile App Developer for our iOS and Android apps. Experience with "
        "React Native or Flutter, Kotlin and Swift, plus mobile UI and "
        "performance optimization."
    ),
    "Cybersecurity Analyst": (
        "Cybersecurity Analyst to defend our network. Skills: networking, Linux, "
        "ethical hacking, SIEM, threat detection, encryption and vulnerability "
        "assessment."
    ),
}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _question_targets(q):
    targets = [
        str(q.get("category", "")),
        str(q.get("topic", "")),
        str(q.get("question_text", "")),
    ]
    keywords = q.get("keywords", [])
    if isinstance(keywords, list):
        targets.extend(str(k) for k in keywords)
    return targets


def compute_question_relevance(question, job_skills):
    """Fraction of job skills a single question matches (0.0 - 1.0)."""
    if not job_skills:
        return 0.0
    targets = _question_targets(question)
    matches = sum(1 for s in job_skills if skill_matchesAny(s, targets))
    return matches / len(job_skills)


def _evaluate_role(service, job_role, required_skills, num_mcq=4, num_desc=3, num_code=3,
                   job_level="Mid-Level", job_description=""):
    """Select questions the same way the live interview does, then score them."""
    difficulty = service._difficulty_for_level(job_level)

    coding_profile = service._determine_coding_profile(job_role, required_skills)
    weights = service.interview_configs.get("interview_weights", {}).get(job_role, {})
    is_non_coding = weights.get("coding", 1) == 0 or coding_profile == "none"

    exclude_ids = set()
    mcq = service._select_questions_by_type(
        "MCQ", num_mcq, required_skills, difficulty=difficulty, exclude_ids=exclude_ids
    )
    desc = service._select_questions_by_type(
        "Descriptive", num_desc, required_skills, difficulty=difficulty, exclude_ids=exclude_ids
    )
    code = []
    if not is_non_coding and num_code:
        code = service._select_questions_by_type(
            "Coding", num_code, required_skills,
            coding_profile=coding_profile, difficulty=difficulty, exclude_ids=exclude_ids,
        )

    all_q = mcq + desc + code
    if not all_q:
        return {"job_role": job_role, "error": "no questions selected", "questions": 0}

    # Skill coverage: job skills touched by >= 1 question.
    covered = set()
    for q in all_q:
        targets = _question_targets(q)
        for skill in required_skills:
            if skill_matchesAny(skill, targets):
                covered.add(skill)
    skill_coverage = len(covered) / max(len(required_skills), 1)

    # Question relevance: fraction of questions matching >= 1 required skill.
    rel_scores = [compute_question_relevance(q, required_skills) for q in all_q]
    relevant = [q for q, r in zip(all_q, rel_scores) if r > 0]
    off_topic = [q for q, r in zip(all_q, rel_scores) if r == 0]
    question_relevance = len(relevant) / len(all_q)

    overall = round(0.4 * skill_coverage + 0.6 * question_relevance, 4)
    return {
        "job_role": job_role,
        "job_description": job_description,
        "required_skills": required_skills,
        "skill_coverage": round(skill_coverage, 4),
        "question_relevance": round(question_relevance, 4),
        "avg_relevance": round(sum(rel_scores) / len(rel_scores), 4),
        "overall_accuracy": overall,
        "questions": len(all_q),
        "mcq": len(mcq),
        "descriptive": len(desc),
        "coding": len(code),
        "coding_profile": coding_profile,
        "non_coding_role": is_non_coding,
        "covered_skills": sorted(covered),
        "missing_skills": sorted(set(required_skills) - covered),
        "off_topic_samples": [
            {"type": q.get("question_type"), "category": q.get("category"),
             "text": (q.get("question_text") or "")[:90]}
            for q in off_topic[:3]
        ],
    }


def _run_pass(service, job_requirements, label, mode):
    """mode: 'role' builds JD from role defaults, 'mock' uses MOCK_JDS free text."""
    results = []
    if mode == "role":
        for role, defaults in job_requirements.items():
            jd = f"We are hiring a {role}. Required skills: {', '.join(defaults)}."
            jd_skills = service._extract_skills_from_description(jd)
            required = merge_skill_lists(defaults, jd_skills)
            results.append(_evaluate_role(service, role, required, job_description=jd))
    else:
        for role, jd in MOCK_JDS.items():
            jd_skills = service._extract_skills_from_description(jd)
            defaults = job_requirements.get(role, [])
            required = merge_skill_lists(defaults, jd_skills)
            r = _evaluate_role(service, role, required, job_description=jd)
            r["extracted_skills"] = jd_skills
            results.append(r)
    return results


def _summarize(results, label):
    valid = [r for r in results if "error" not in r]
    n = len(valid)
    avg_cov = sum(r["skill_coverage"] for r in valid) / n if n else 0
    avg_rel = sum(r["question_relevance"] for r in valid) / n if n else 0
    avg_acc = sum(r["overall_accuracy"] for r in valid) / n if n else 0

    print("=" * 92)
    print(f"QUESTION ACCURACY - PASS: {label}")
    print("=" * 92)
    print(f"Roles tested        : {len(results)}")
    print(f"Roles with questions: {n}")
    print(f"Avg skill coverage  : {avg_cov:.1%}")
    print(f"Avg question relev. : {avg_rel:.1%}")
    print(f"Avg overall accuracy: {avg_acc:.1%}")
    print()
    print(f"{'Role':<32}{'Cover':>7}{'Relev':>7}{'Acc':>7}{'Qs':>4}{'MCQ':>5}{'Desc':>6}{'Code':>6}  Profile")
    print("-" * 92)
    for r in sorted(valid, key=lambda x: x["overall_accuracy"]):
        print(f"{r['job_role']:<32}{r['skill_coverage']:>7.1%}{r['question_relevance']:>7.1%}"
              f"{r['overall_accuracy']:>7.1%}{r['questions']:>4}{r['mcq']:>5}{r['descriptive']:>6}"
              f"{r['coding']:>6}  {r['coding_profile']}")

    worst = sorted(valid, key=lambda x: x["overall_accuracy"])[:5]
    print()
    print("LOWEST ACCURACY ROLES")
    print("-" * 92)
    for r in worst:
        print(f"  {r['job_role']}: {r['overall_accuracy']:.1%}"
              f"  (coverage {r['skill_coverage']:.0%}, relevance {r['question_relevance']:.0%})")
        if r.get("missing_skills"):
            print(f"    uncovered skills: {r['missing_skills']}")
        for s in r.get("off_topic_samples", []):
            print(f"    OFF-TOPIC [{s['type']}] {s['category']}: {s['text']}")
    print()
    return valid, avg_cov, avg_rel, avg_acc


def run_accuracy_test(verbose=True):
    job_requirements = load_json(Path(MODELS_DIR) / "job_requirements.json")
    service = InterviewService(MODELS_DIR)

    # --- Job position count contract: exactly 20 positions must be present ---
    serving = service.get_available_jobs()
    assert len(job_requirements) == EXPECTED_JOB_COUNT, (
        f"job_requirements.json has {len(job_requirements)} positions, expected {EXPECTED_JOB_COUNT}"
    )
    assert len(serving) == EXPECTED_JOB_COUNT, (
        f"interview service exposes {len(serving)} positions, expected {EXPECTED_JOB_COUNT}"
    )
    assert set(serving) == set(job_requirements), (
        f"service roles differ from config: {set(serving) ^ set(job_requirements)}"
    )
    print(f"JOB POSITIONS: {len(job_requirements)}/{EXPECTED_JOB_COUNT} present "
          f"(config + service agree)")
    print()

    role_results = _run_pass(service, job_requirements, "ROLE DEFAULTS", "role")
    mock_results = _run_pass(service, job_requirements, "MOCK JOB DESCRIPTIONS", "mock")

    v1, cov1, rel1, acc1 = _summarize(role_results, "ROLE DEFAULTS")
    v2, cov2, rel2, acc2 = _summarize(mock_results, "MOCK JOB DESCRIPTIONS")

    # Non-coding roles must not receive coding questions.
    noncoding = [r for r in v1 if r["non_coding_role"]]
    leaked = [r["job_role"] for r in noncoding if r["coding"] > 0]
    print("NON-CODING ROLE CHECK")
    print("-" * 92)
    print(f"  Non-coding roles tested : {len(noncoding)}")
    print(f"  Roles leaking coding Qs : {leaked if leaked else 'none'}")
    print()

    assert len(v1) == len(job_requirements), f"role pass missing roles: {len(v1)}/{len(job_requirements)}"
    assert acc1 > 0.5, f"role-pass accuracy {acc1:.1%} below 50%"
    assert acc2 > 0.5, f"mock-pass accuracy {acc2:.1%} below 50%"
    assert not leaked, f"non-coding roles got coding questions: {leaked}"
    print("ALL ASSERTIONS PASSED")

    return {"role": role_results, "mock": mock_results,
            "summary": {"role_accuracy": acc1, "mock_accuracy": acc2}}


# ---- pytest entry points -------------------------------------------------

def test_system_has_exactly_20_job_positions():
    """The product spec requires exactly 20 job positions serviceable end to end."""
    job_requirements = load_json(Path(MODELS_DIR) / "job_requirements.json")
    service = InterviewService(MODELS_DIR)
    serving = service.get_available_jobs()
    assert len(job_requirements) == EXPECTED_JOB_COUNT, (
        f"config has {len(job_requirements)} positions, expected {EXPECTED_JOB_COUNT}"
    )
    assert len(serving) == EXPECTED_JOB_COUNT, (
        f"service exposes {len(serving)} positions, expected {EXPECTED_JOB_COUNT}"
    )
    assert set(serving) == set(job_requirements)


def test_question_accuracy_role_defaults():
    job_requirements = load_json(Path(MODELS_DIR) / "job_requirements.json")
    service = InterviewService(MODELS_DIR)
    results = _run_pass(service, job_requirements, "ROLE DEFAULTS", "role")
    valid = [r for r in results if "error" not in r]
    assert len(valid) == len(job_requirements)
    acc = sum(r["overall_accuracy"] for r in valid) / len(valid)
    assert acc > 0.5, f"role accuracy {acc:.1%} below 50%"


def test_question_accuracy_mock_descriptions():
    job_requirements = load_json(Path(MODELS_DIR) / "job_requirements.json")
    service = InterviewService(MODELS_DIR)
    results = _run_pass(service, job_requirements, "MOCK JOB DESCRIPTIONS", "mock")
    valid = [r for r in results if "error" not in r]
    assert valid, "no roles produced questions"
    acc = sum(r["overall_accuracy"] for r in valid) / len(valid)
    assert acc > 0.5, f"mock accuracy {acc:.1%} below 50%"


def test_non_coding_roles_get_no_coding_questions():
    job_requirements = load_json(Path(MODELS_DIR) / "job_requirements.json")
    service = InterviewService(MODELS_DIR)
    results = _run_pass(service, job_requirements, "ROLE DEFAULTS", "role")
    leaked = [r["job_role"] for r in results
              if r.get("non_coding_role") and r.get("coding", 0) > 0]
    assert not leaked, f"non-coding roles got coding questions: {leaked}"


if __name__ == "__main__":
    run_accuracy_test()
