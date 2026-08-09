"""Integration test for the ranked shortlist endpoint.

Skill-gap reports are seeded into the *test* reports database (never comp4's HR).
"""

from datetime import datetime, timezone

import pymongo

from app import config
from tests.conftest import auth_header

JOB = {
    "title": "Platform Engineer",
    "description": "Own the API platform and tooling.",
    "job_role": "Software Engineer",
    "job_level": "Mid-Level",
    "work_mode": "Hybrid",
}


def _create_job_with_apps(client, token, apps):
    job = client.post("/api/v1/jobs", json=JOB, headers=auth_header(token)).json()
    for app in apps:
        client.post(
            f"/api/v1/jobs/{job['id']}/apply", json=app, headers=auth_header(token)
        )
    return job


def _seed_report(client, candidate_id, skill_match_pct, interview_score, hire_probability):
    mongo = pymongo.MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=3000)
    coll = mongo[config.REPORTS_DB][config.REPORTS_COLLECTION]
    coll.insert_one({
        "candidate_id": candidate_id,
        "candidate_name": candidate_id,
        "job_role": "Software Engineer",
        "skill_match_pct": skill_match_pct,
        "interview_score": interview_score,
        "hire_probability": hire_probability,
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "missing_required": [],
        "missing_optional": [],
        "present_skills": [],
        "predicted_hire": True,
        "gap_score": 0.2,
        "gap_severity": "low",
        "resources": [],
        "roadmap_nodes": [],
        "learning_plan": [],
        "career_path_suggestions": [],
        "improvement_suggestions": [],
        "technical_gaps": [],
        "ml_ai_gaps": [],
        "cloud_devops_gaps": [],
        "security_gaps": [],
        "data_gaps": [],
        "knowledge_gaps": [],
        "problem_solving_gaps": [],
        "certifications_count": 0,
        "projects_count": 0,
    })
    mongo.close()


def test_ranked_list_sorted_with_reports(client, recruiter_token):
    apps = [
        {
            "candidate_id": "strong_cand",
            "candidate_name": "Ada Strong",
            "experience_years": 5,
            "education": "M.Sc. Computer Science",
            "mcq_score": 85, "descriptive_score": 80, "coding_score": 95,
        },
        {
            "candidate_id": "weak_cand",
            "candidate_name": "Ben Weak",
            "experience_years": 1,
            "education": "Diploma",
            "mcq_score": 50, "descriptive_score": 40, "coding_score": 45,
        },
    ]
    _seed_report(client, "strong_cand", 92, 87, 91.5)
    _seed_report(client, "weak_cand", 30, 45, 22.0)

    job = _create_job_with_apps(client, recruiter_token, apps)
    res = client.get(
        f"/api/v1/jobs/{job['id']}/candidates", headers=auth_header(recruiter_token)
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["job_role"] == "Software Engineer"
    assert body["total"] == 2

    by_id = {c["candidate_id"]: c for c in body["candidates"]}
    strong = by_id["strong_cand"]
    weak = by_id["weak_cand"]

    assert strong["rank"] == 1 and strong["passed_hard_filter"] is True
    assert strong["hire_probability"] == 91.5
    assert strong["report_available"] is True
    assert strong["CSS"] > weak["CSS"]

    assert weak["passed_hard_filter"] is False
    assert "Education" in weak["filter_fail_reason"]


def test_ranked_list_without_reports_falls_back(client, recruiter_token):
    apps = [
        {
            "candidate_id": "no_report_cand",
            "candidate_name": "Carol Noreport",
            "experience_years": 4,
            "education": "B.Sc. Computer Science",
            "cv_matching_score": 88,
            "mcq_score": 75, "descriptive_score": 70, "coding_score": 80,
        }
    ]
    job = _create_job_with_apps(client, recruiter_token, apps)
    res = client.get(
        f"/api/v1/jobs/{job['id']}/candidates", headers=auth_header(recruiter_token)
    )
    assert res.status_code == 200
    cand = res.json()["candidates"][0]
    assert cand["candidate_id"] == "no_report_cand"
    assert cand["report_available"] is False
    assert cand["passed_hard_filter"] is True
    assert cand["CSS"] > 0


def test_ranked_list_empty(client, recruiter_token):
    job = client.post(
        "/api/v1/jobs", json=JOB, headers=auth_header(recruiter_token)
    ).json()
    res = client.get(
        f"/api/v1/jobs/{job['id']}/candidates", headers=auth_header(recruiter_token)
    )
    assert res.status_code == 200
    assert res.json()["total"] == 0
    assert res.json()["candidates"] == []
