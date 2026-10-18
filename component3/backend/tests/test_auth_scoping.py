"""Auth regression tests — C3 ranking backend.

Mounts the real rank router with an in-memory fake DB. Locks in the
H-8 wiring: compute/results/pipeline/weights require identity, explain
is owner-scoped, and the roles map stays open metadata.
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

from routers import rank as rank_router


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


class FakeDB(dict):
    def __getattr__(self, name):
        if name not in self:
            self[name] = FakeCollection()
        return self[name]


def _make_app():
    app = FastAPI()
    app.state.limiter = Limiter(key_func=get_remote_address)
    app.include_router(rank_router.router, prefix="/api/v1")
    app.state.db = FakeDB()
    app.state.store = None
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
    return _make_app()


class TestRankGuards:
    def test_jobs_open_metadata_200(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get("/api/v1/rank/jobs").status_code == 200

    def test_results_anonymous_401(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get("/api/v1/rank/results/somejob").status_code == 401

    def test_pipeline_anonymous_401(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        assert c.get("/api/v1/rank/pipeline/somejob").status_code == 401

    def test_explain_cross_user_403(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.get(f"/api/v1/rank/explain/{B}", headers=_auth(A))
        assert r.status_code == 403

    def test_weights_anonymous_401(self, app):
        c = TestClient(app, raise_server_exceptions=False)
        r = c.post("/api/v1/rank/weights",
                   json={"job_role": "Software Engineer", "w_cv": 0.4, "w_int": 0.6})
        assert r.status_code == 401
