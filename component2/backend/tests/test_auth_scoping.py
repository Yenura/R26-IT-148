"""Auth + session-isolation regression tests — C2 interview backend.

Mounts the real interview router with stubbed session storage.
Locks in the C-6 fixes: sessions are identity-bound, cross-user
submit/read is rejected, anonymous callers get 401. The ML scoring
path is never executed here (it is covered by live probes instead).
"""
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BACKEND = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.util import get_remote_address

import routers.interview as iv


FAKE_SESSION = {
    "session_id": "INT_TEST123",
    "candidate_id": "6ad1e540c902fc853771c715",
    "job_role": "Software Engineer",
    "questions": [],
    "is_practice": True,
    "status": "active",
}
FAKE_RESULT = {
    "interview_id": "RES_TEST123",
    "candidate_id": "6ad1e540c902fc853771c715",
    "session_id": "INT_TEST123",
    "job_role": "Software Engineer",
    "interview_score": 80,
    "grade": "Good",
}


async def _fake_get_session(session_id: str):
    if session_id == FAKE_SESSION["session_id"]:
        return dict(FAKE_SESSION)
    return None


async def _fake_get_result(interview_id: str):
    if interview_id == FAKE_RESULT["interview_id"]:
        return dict(FAKE_RESULT)
    return None


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setattr(iv, "get_session", _fake_get_session)
    monkeypatch.setattr(iv, "get_result", _fake_get_result)
    app = FastAPI()
    app.state.limiter = Limiter(key_func=get_remote_address)
    app.include_router(iv.router)
    return app


def _token(uid, role="candidate"):
    from jose import jwt
    exp = datetime.now(timezone.utc) + timedelta(hours=1)
    return jwt.encode({"sub": str(uid), "role": role, "exp": exp},
                      "recruitai-dev-secret-key-change-in-prod", algorithm="HS256")


def _auth(uid, role="candidate"):
    return {"Authorization": f"Bearer {_token(uid, role)}"}


A = "6ad1e536bc602ce18892e8a6"
B = "6ad1e540c902fc853771c715"


class TestSessionIsolation:
    def test_start_anonymous_401(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.post("/api/v1/interview/start",
                   json={"candidate_id": "ghost", "job_role": "Software Engineer",
                         "num_questions": 1})
        assert r.status_code == 401

    def test_session_anonymous_401(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get("/api/v1/interview/session/INT_TEST123").status_code == 401

    def test_session_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/v1/interview/session/INT_TEST123", headers=_auth(A))
        assert r.status_code == 403

    def test_session_owner_200(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/v1/interview/session/INT_TEST123", headers=_auth(B))
        assert r.status_code == 200
        assert r.json()["session"]["session_id"] == "INT_TEST123"

    def test_submit_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.post("/api/v1/interview/submit",
                   json={"session_id": "INT_TEST123", "candidate_id": "EVE",
                         "answers": []},
                   headers=_auth(A))
        assert r.status_code == 403

    def test_result_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/v1/interview/result/RES_TEST123", headers=_auth(A))
        assert r.status_code == 403

    def test_result_owner_200(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/v1/interview/result/RES_TEST123", headers=_auth(B))
        assert r.status_code == 200

    def test_code_run_anonymous_401(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.post("/api/v1/interview/code/run",
                   json={"code_text": "print(1)", "test_cases": []})
        assert r.status_code == 401

    def test_proctoring_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/v1/interview/proctoring/RES_TEST123", headers=_auth(A))
        # 403 owner-check fires before the missing-proctoring 404
        assert r.status_code == 403
