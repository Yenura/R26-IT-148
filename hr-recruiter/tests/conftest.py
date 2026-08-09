"""Shared fixtures for hr-recruiter tests.

All tests use isolated databases (``DB_NAME`` / ``REPORTS_DB``) so component4's
real ``HR`` database is never written.
"""

import os

os.environ.setdefault("DB_NAME", "hr_recruiter_test")
os.environ.setdefault("REPORTS_DB", "hr_recruiter_test_reports")
os.environ.setdefault("JWT_SECRET", "test-secret-not-for-production")
os.environ.setdefault("TOKEN_EXPIRE_MINUTES", "60")

import pytest
from fastapi.testclient import TestClient

from app import config
from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def _cleanup():
    yield
    try:
        import pymongo

        mongo = pymongo.MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=3000)
        mongo.drop_database(config.DB_NAME)
        mongo.drop_database(config.REPORTS_DB)
        mongo.close()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def _clean_collections():
    try:
        import pymongo

        mongo = pymongo.MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=3000)
        db = mongo[config.DB_NAME]
        db.recruiters.delete_many({})
        db.job_postings.delete_many({})
        db.applications.delete_many({})
        reports_db = mongo[config.REPORTS_DB]
        reports_db[config.REPORTS_COLLECTION].delete_many({})
        mongo.close()
    except Exception:
        pass
    yield


@pytest.fixture()
def recruiter_token(client) -> str:
    res = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Recruiter One",
            "email": "recruiter@example.com",
            "password": "secret123",
            "organization": "Acme Corp",
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
