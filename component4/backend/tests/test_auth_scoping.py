"""Auth + session-isolation regression tests — C4 skill-gap backend.

Mounts the real progress/skill_gap/career routers with an in-memory
fake DB. Locks in the H-8 fixes: per-candidate reads/writes/deletes
require identity and owner-or-company role; the reports dump is
company/service-only; the cross-user fallback is gone.
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

from routers import progress as progress_router
from routers import skill_gap as skill_gap_router
from routers import career as career_router


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

    async def find_one(self, flt=None, *a, **k):
        for d in self.docs:
            if _match(d, flt or {}):
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

    async def replace_one(self, flt, doc, upsert=False):
        for i, d in enumerate(self.docs):
            if _match(d, flt):
                self.docs[i] = dict(doc)
                return type("R", (), {"modified_count": 1})()
        if upsert:
            self.docs.append(dict(doc))
        return type("R", (), {"modified_count": 0})()

    async def update_one(self, flt, update, upsert=False):
        for d in self.docs:
            if _match(d, flt):
                d.update(update.get("$set", {}))
                for k in update.get("$unset", {}):
                    d.pop(k, None)
                return type("R", (), {"modified_count": 1})()
        if upsert:
            doc = dict(update.get("$set", {}))
            doc.setdefault("_id", ObjectId())
            self.docs.append(doc)
        return type("R", (), {"modified_count": 0})()

    async def count_documents(self, flt=None):
        return sum(1 for d in self.docs if _match(d, flt or {}))

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
    app.include_router(progress_router.router, prefix="/api/v1/progress")
    app.include_router(skill_gap_router.router, prefix="/api/v1/skill-gap")
    app.include_router(career_router.router, prefix="/api/v1/career")
    app.state.db = FakeDB()
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


@pytest.fixture()
def app():
    app = _make_app()
    db = app.state.db
    now = datetime.now(timezone.utc)
    db.progress_tracking.docs.append({
        "candidate_id": B, "skill": "Python", "status": "in_progress",
        "updated_at": now,
    })
    db.skill_gap_reports.docs.append({
        "candidate_id": B, "job_role": "Software Engineer",
        "created_at": now,
    })
    return app


# ── progress ────────────────────────────────────────────────────────
class TestProgressIsolation:
    def test_get_anonymous_401(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get(f"/api/v1/progress/{B}").status_code == 401

    def test_get_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get(f"/api/v1/progress/{B}", headers=_auth(A)).status_code == 403

    def test_get_own_200(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get(f"/api/v1/progress/{B}", headers=_auth(B))
        assert r.status_code == 200
        assert r.json()["stats"]["total"] == 1

    def test_update_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.post("/api/v1/progress/update",
                   json={"candidate_id": B, "skill": "Go", "status": "not_started"},
                   headers=_auth(A))
        assert r.status_code == 403

    def test_update_own_200(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.post("/api/v1/progress/update",
                   json={"candidate_id": B, "skill": "Go", "status": "not_started"},
                   headers=_auth(B))
        assert r.status_code == 200

    def test_delete_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.delete(f"/api/v1/progress/{B}/Python", headers=_auth(A)).status_code == 403


# ── skill gap reports ───────────────────────────────────────────────
class TestSkillGapReports:
    def test_report_anonymous_401(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get(f"/api/v1/skill-gap/report/{B}").status_code == 401

    def test_report_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get(f"/api/v1/skill-gap/report/{B}", headers=_auth(A)).status_code == 403

    def test_report_own_200(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get(f"/api/v1/skill-gap/report/{B}", headers=_auth(B)).status_code == 200

    def test_reports_dump_candidate_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get("/api/v1/skill-gap/reports", headers=_auth(A)).status_code == 403

    def test_reports_dump_company_200(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get("/api/v1/skill-gap/reports", headers=_auth(A, "company"))
        assert r.status_code == 200
        assert r.json()["total"] == 1

    def test_delete_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.delete(f"/api/v1/skill-gap/report/{B}", headers=_auth(A)).status_code == 403

    def test_analyze_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.post("/api/v1/skill-gap/analyze",
                   json={"candidate_id": B, "candidate_name": "User B",
                         "job_role": "Software Engineer", "skills": ["Python"]},
                   headers=_auth(A))
        assert r.status_code == 403


# ── career roadmap ──────────────────────────────────────────────────
class TestCareerRoadmap:
    def test_roadmap_anonymous_401(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get(f"/api/v1/career/roadmap/{B}").status_code == 401

    def test_roadmap_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get(f"/api/v1/career/roadmap/{B}", headers=_auth(A)).status_code == 403
