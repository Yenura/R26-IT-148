"""Auth + session-isolation regression tests — C0 gateway.

Mounts the real auth/resume/jobs routers on a minimal app with an
in-memory fake DB (no Mongo, no lifespan). Locks in the C-2..C-5 fixes:
anonymous callers get 401, cross-user access 403/404, owners succeed.
"""
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BACKEND = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND))

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("JWT_SECRET", "recruitai-dev-secret-key-change-in-prod")

import pytest
from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.util import get_remote_address

from security import hash_password
from routers import auth as auth_router
from routers import resume as resume_router
from routers import jobs as jobs_router


# ── Fake async Mongo ────────────────────────────────────────────────
def _match(doc, flt):
    for k, v in flt.items():
        if k == "$or":
            if not any(_match(doc, sub) for sub in v):
                return False
        elif isinstance(v, dict):
            for op, ov in v.items():
                if op == "$in":
                    if doc.get(k) not in ov:
                        return False
                elif op == "$gt":
                    if not (doc.get(k) is not None and doc.get(k) > ov):
                        return False
                elif op == "$ne":
                    if doc.get(k) == ov:
                        return False
                else:
                    return False
        elif doc.get(k) != v:
            return False
    return True


class FakeCursor:
    def __init__(self, docs):
        self._docs = list(docs)

    def sort(self, *a, **k):
        return self

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    def skip(self, n):
        self._docs = self._docs[n:]
        return self

    async def to_list(self, length=None):
        return self._docs[:length] if length else list(self._docs)

    def __aiter__(self):
        async def gen():
            for d in self._docs:
                yield d
        return gen()


class FakeCollection:
    def __init__(self):
        self.docs = []

    async def find_one(self, flt, *a, **k):
        for d in self.docs:
            if _match(d, flt):
                return dict(d)
        return None

    def find(self, flt=None, *a, **k):
        return FakeCursor([d for d in self.docs if _match(d, flt or {})])

    async def insert_one(self, doc):
        doc = dict(doc)
        doc.setdefault("_id", ObjectId())
        self.docs.append(doc)

        class R:
            inserted_id = doc["_id"]
        return R()

    async def update_one(self, flt, update, upsert=False):
        for d in self.docs:
            if _match(d, flt):
                d.update(update.get("$set", {}))
                for k in update.get("$unset", {}):
                    d.pop(k, None)

                class R:
                    modified_count = 1
                return R()
        if upsert:
            doc = dict(update.get("$set", {}))
            doc.setdefault("_id", ObjectId())
            self.docs.append(doc)
        return type("R", (), {"modified_count": 0})()

    async def delete_one(self, flt):
        before = len(self.docs)
        self.docs = [d for d in self.docs if not _match(d, flt)]
        return type("R", (), {"deleted_count": before - len(self.docs)})()

    async def delete_many(self, flt):
        return await self.delete_one(flt)


class FakeDB(dict):
    def __getattr__(self, name):
        if name not in self:
            self[name] = FakeCollection()
        return self[name]


def _make_app():
    app = FastAPI()
    app.state.limiter = Limiter(key_func=get_remote_address)
    app.include_router(auth_router.router, prefix="/api/v1/auth")
    app.include_router(resume_router.router, prefix="/api/v1/resume")
    app.include_router(jobs_router.router, prefix="/api/v1/jobs")
    app.state.db = FakeDB()
    return app


def _token(uid, role="candidate"):
    from jose import jwt
    exp = datetime.now(timezone.utc) + timedelta(hours=1)
    return jwt.encode({"sub": str(uid), "role": role, "exp": exp},
                      "recruitai-dev-secret-key-change-in-prod", algorithm="HS256")


@pytest.fixture()
def app():
    return _make_mock_app()


def _make_mock_app():
    app = _make_app()
    db = app.state.db
    # Seed: two candidates, one company + its job; B owns a resume.
    db.users.docs.extend([
        {"_id": ObjectId("6ad1e536bc602ce18892e8a6"), "email": "a@test.com",
         "password": hash_password("Pass@123"), "role": "candidate",
         "full_name": "User A"},
        {"_id": ObjectId("6ad1e540c902fc853771c715"), "email": "b@test.com",
         "password": hash_password("Pass@123"), "role": "candidate",
         "full_name": "User B"},
        {"_id": ObjectId("6ad1e540c902fc853771c716"), "email": "c@test.com",
         "password": hash_password("Pass@123"), "role": "company",
         "company_name": "Co C"},
        {"_id": ObjectId("6ad1e540c902fc853771c717"), "email": "d@test.com",
         "password": hash_password("Pass@123"), "role": "company",
         "company_name": "Co D"},
    ])
    db.resumes.docs.append({
        "_id": ObjectId("6ad1e550c902fc853771c717"),
        "candidate_id": "6ad1e540c902fc853771c715",
        "candidate_name": "User B", "skills": ["Python"],
        "raw_text": "B python dev", "created_at": datetime.now(timezone.utc),
    })
    db.jobs.docs.append({
        "_id": ObjectId("6ad1e58dc902fc853771c718"),
        "company_id": ObjectId("6ad1e540c902fc853771c716"),
        "title": "Backend Dev", "status": "open",
        "created_at": datetime.now(timezone.utc),
    })
    db.jobs.docs.append({
        "_id": ObjectId("6ad1e58dc902fc853771c719"),
        "company_id": ObjectId("6ad1e540c902fc853771c717"),
        "title": "Frontend Dev", "status": "open",
        "created_at": datetime.now(timezone.utc),
    })
    return app


def _auth(uid, role="candidate"):
    return {"Authorization": f"Bearer {_token(uid, role)}"}


A = "6ad1e536bc602ce18892e8a6"
B = "6ad1e540c902fc853771c715"
C = "6ad1e540c902fc853771c716"
RID_B = "6ad1e550c902fc853771c717"
JOB_C = "6ad1e58dc902fc853771c718"


# ── forgot/reset ────────────────────────────────────────────────────
class TestPasswordRecovery:
    def test_forgot_unknown_email_generic(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.post("/api/v1/auth/forgot-password", json={"email": "nobody@nowhere.test"})
        assert r.status_code == 200
        assert "dev_token" not in r.json()

    def test_forgot_bad_email_422(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.post("/api/v1/auth/forgot-password", json={"email": "not-an-email"}).status_code == 422

    def test_reset_bad_token_400(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.post("/api/v1/auth/reset-password",
                   json={"token": "AAAAAAAAAAAAAAAAAAAAAAAAAA", "new_password": "New@12345"})
        assert r.status_code == 400


# ── resume isolation (C-3, C-5) ─────────────────────────────────────
class TestResumeIsolation:
    def test_cross_resume_read_404(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get(f"/api/v1/resume/{RID_B}", headers=_auth(A)).status_code == 404

    def test_own_resume_read_200(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get(f"/api/v1/resume/{RID_B}", headers=_auth(B)).status_code == 200

    def test_cross_match_404(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.post(f"/api/v1/resume/match?resume_id={RID_B}", headers=_auth(A))
        assert r.status_code == 404

    def test_company_list_scoped(self, app):
        # Company C has no applicants: must see zero resumes, not the global dump.
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/v1/resume/", headers=_auth(C, "company"))
        assert r.status_code == 200
        assert r.json() == []


# ── interview scores (C-2) ──────────────────────────────────────────
class TestInterviewScores:
    def test_post_anonymous_401(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.post("/api/v1/resume/interview-scores",
                      json={"candidate_id": B, "interview_score": 99}).status_code == 401

    def test_post_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.post("/api/v1/resume/interview-scores",
                   json={"candidate_id": B, "interview_score": 99}, headers=_auth(A))
        assert r.status_code == 403

    def test_get_cross_user_404(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get(f"/api/v1/resume/interview-scores/{B}", headers=_auth(A)).status_code == 404


# ── job ownership (C-4) ─────────────────────────────────────────────
JOB_D = "6ad1e58dc902fc853771c719"


class TestJobOwnership:
    def test_patch_foreign_job_404(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        # Company C tries to rename Company D's job.
        r = c.patch(f"/api/v1/jobs/{JOB_D}",
                    json={"title": "PWNED"}, headers=_auth(C, "company"))
        assert r.status_code == 404

    def test_applicants_foreign_job_404(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get(f"/api/v1/jobs/{JOB_D}/applicants",
                  headers=_auth(C, "company"))
        assert r.status_code == 404

    def test_own_job_200(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get(f"/api/v1/jobs/{JOB_C}", headers=_auth(C, "company")).status_code == 200
