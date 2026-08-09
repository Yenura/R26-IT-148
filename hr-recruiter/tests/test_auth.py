from tests.conftest import auth_header


def test_register_and_login(client):
    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "HR User",
            "email": "hr@example.com",
            "password": "password123",
        },
    )
    assert register.status_code == 201
    token = register.json()["access_token"]
    assert token

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "hr@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_register_duplicate_email(client, recruiter_token):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Duplicate",
            "email": "recruiter@example.com",
            "password": "password123",
        },
    )
    assert res.status_code == 409


def test_login_wrong_password(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "recruiter@example.com", "password": "wrong"},
    )
    assert res.status_code == 401


def test_me_with_valid_token(client, recruiter_token):
    res = client.get("/api/v1/auth/me", headers=auth_header(recruiter_token))
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "recruiter@example.com"
    assert body["full_name"] == "Recruiter One"


def test_me_without_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_with_garbage_token(client):
    res = client.get("/api/v1/auth/me", headers=auth_header("not.a.jwt"))
    assert res.status_code == 401
