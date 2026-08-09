from tests.conftest import auth_header

JOB = {
    "title": "Backend Engineer",
    "description": "Build REST APIs and services.",
    "job_role": "Software Engineer",
    "job_level": "Mid-Level",
    "work_mode": "Hybrid",
    "location": "Colombo",
    "skills_required": ["Python", "FastAPI", "SQL"],
}


def _create_job(client, token):
    res = client.post("/api/v1/jobs", json=JOB, headers=auth_header(token))
    assert res.status_code == 201, res.text
    return res.json()


def test_create_job_normalises_role(client, recruiter_token):
    job = _create_job(client, recruiter_token)
    assert job["role_key"] == "Software_Engineer"
    assert job["job_role"] == "Software Engineer"
    assert job["status"] == "open"


def test_create_job_rejects_unknown_role(client, recruiter_token):
    payload = {**JOB, "job_role": "Astronaut"}
    res = client.post("/api/v1/jobs", json=payload, headers=auth_header(recruiter_token))
    assert res.status_code == 422


def test_create_job_requires_auth(client):
    assert client.post("/api/v1/jobs", json=JOB).status_code == 401


def test_list_jobs(client, recruiter_token):
    _create_job(client, recruiter_token)
    res = client.get("/api/v1/jobs", headers=auth_header(recruiter_token))
    assert res.status_code == 200
    assert any(j["title"] == "Backend Engineer" for j in res.json())


def test_list_jobs_filter_by_role(client, recruiter_token):
    _create_job(client, recruiter_token)
    ok = client.get(
        "/api/v1/jobs", params={"role_key": "software_engineer"},
        headers=auth_header(recruiter_token),
    )
    assert ok.status_code == 200 and ok.json()
    none = client.get(
        "/api/v1/jobs", params={"role_key": "astronaut"},
        headers=auth_header(recruiter_token),
    )
    assert none.status_code == 200 and none.json() == []


def test_get_and_update_job(client, recruiter_token):
    job = _create_job(client, recruiter_token)
    get = client.get(f"/api/v1/jobs/{job['id']}", headers=auth_header(recruiter_token))
    assert get.status_code == 200

    upd = client.patch(
        f"/api/v1/jobs/{job['id']}",
        json={"status": "closed", "job_role": "Backend Developer"},
        headers=auth_header(recruiter_token),
    )
    assert upd.status_code == 200
    body = upd.json()
    assert body["status"] == "closed"
    assert body["role_key"] == "Backend_Developer"


def test_other_recruiter_cannot_touch_job(client, recruiter_token):
    other = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Other", "email": "other@example.com", "password": "password123"},
    ).json()["access_token"]
    job = _create_job(client, other)
    res = client.patch(
        f"/api/v1/jobs/{job['id']}", json={"status": "closed"},
        headers=auth_header(other),
    )
    assert res.status_code == 200
    forbidden = client.get(
        f"/api/v1/jobs/{job['id']}", headers=auth_header(recruiter_token)
    )
    assert forbidden.status_code == 404


def test_apply_and_dedupe(client, recruiter_token):
    job = _create_job(client, recruiter_token)
    app_payload = {
        "candidate_id": "cand_001",
        "candidate_name": "Jane Doe",
        "experience_years": 4,
        "education": "B.Sc. Computer Science",
        "skills": ["Python", "SQL"],
        "mcq_score": 80,
        "descriptive_score": 70,
        "coding_score": 90,
    }
    first = client.post(
        f"/api/v1/jobs/{job['id']}/apply", json=app_payload,
        headers=auth_header(recruiter_token),
    )
    assert first.status_code == 201, first.text
    dup = client.post(
        f"/api/v1/jobs/{job['id']}/apply", json=app_payload,
        headers=auth_header(recruiter_token),
    )
    assert dup.status_code == 409


def test_apply_closed_job_rejected(client, recruiter_token):
    job = _create_job(client, recruiter_token)
    client.patch(
        f"/api/v1/jobs/{job['id']}", json={"status": "closed"},
        headers=auth_header(recruiter_token),
    )
    res = client.post(
        f"/api/v1/jobs/{job['id']}/apply",
        json={"candidate_id": "cand_002", "candidate_name": "John Roe", "experience_years": 3},
        headers=auth_header(recruiter_token),
    )
    assert res.status_code == 422


def test_delete_job(client, recruiter_token):
    job = _create_job(client, recruiter_token)
    res = client.delete(f"/api/v1/jobs/{job['id']}", headers=auth_header(recruiter_token))
    assert res.status_code == 204
    assert client.get(
        f"/api/v1/jobs/{job['id']}", headers=auth_header(recruiter_token)
    ).status_code == 404
