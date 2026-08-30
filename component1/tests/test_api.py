"""API integration tests — Component 1
IT22089236 | D T D Perera | R26-IT-148

Uses FastAPI TestClient with mocked MongoDB and a real TF-IDF (or fallback) predictor.
Mongo-persisted endpoints are marked requires_mongo and skipped if DB is unavailable.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from data.role_requirements import ALL_ROLES, REQUIRED_SKILLS, REQUIRED_YEARS

ROLE_SET = set(ALL_ROLES)


def _make_mock_app():
    """Create a TestClient with mocked DB and real (TF-IDF or fallback) predictor."""
    os.environ.setdefault("MODEL_DIR", str(Path(__file__).parent.parent / "models"))
    os.environ.setdefault("DB_NAME", "resumes_test")

    from backend.main import app
    from backend.services.predictor import Predictor
    from backend.services.matcher import JDMatcher

    model_dir = Path(os.environ["MODEL_DIR"])
    predictor = Predictor(model_dir=model_dir)
    matcher   = JDMatcher(
        sbert_model=getattr(predictor, "_sbert_model", None),
        tfidf_vectorizer=getattr(predictor, "_vectorizer", None),
    )

    # Mock DB (in-memory store)
    _store = {}

    async def mock_replace_one(filter_, doc, upsert=False):
        _store[filter_.get("candidate_id", "unknown")] = doc
        return MagicMock(upserted_id="mock_id")

    async def mock_find_one(filter_, projection=None):
        key = filter_.get("candidate_id")
        return _store.get(key)

    async def mock_delete_one(filter_):
        key = filter_.get("candidate_id")
        deleted = 1 if key in _store else 0
        _store.pop(key, None)
        return MagicMock(deleted_count=deleted)

    async def mock_count_documents(filter_=None):
        return len(_store)

    async def mock_command(cmd):
        return {"ok": 1}

    mock_collection = MagicMock()
    mock_collection.replace_one = mock_replace_one
    mock_collection.find_one    = mock_find_one
    mock_collection.delete_one  = mock_delete_one
    mock_collection.count_documents = mock_count_documents
    mock_collection.find        = MagicMock(return_value=AsyncMock())
    mock_collection.create_index = AsyncMock()

    mock_db = MagicMock()
    mock_db.__getitem__ = lambda self, key: mock_collection
    mock_db.cv_analyses = mock_collection
    mock_db.command = mock_command

    app.state.db        = mock_db
    app.state.predictor = predictor
    app.state.matcher   = matcher

    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture(scope="module")
def client():
    return _make_mock_app()


# ── /api/v1/roles ──────────────────────────────────────────────────────────────

class TestRolesEndpoint:
    def test_roles_returns_200(self, client):
        r = client.get("/api/v1/cv/roles")
        assert r.status_code == 200

    def test_roles_returns_20(self, client):
        r = client.get("/api/v1/cv/roles")
        data = r.json()
        assert data["total"] == 20
        assert len(data["roles"]) == 20

    def test_all_role_names_exact(self, client):
        r = client.get("/api/v1/cv/roles")
        returned_names = {role["role"] for role in r.json()["roles"]}
        assert returned_names == ROLE_SET

    def test_each_role_has_required_skills(self, client):
        r = client.get("/api/v1/cv/roles")
        for role_data in r.json()["roles"]:
            assert len(role_data["required_skills"]) > 0

    def test_each_role_has_required_years(self, client):
        r = client.get("/api/v1/cv/roles")
        for role_data in r.json()["roles"]:
            assert role_data["required_years"] > 0


# ── /api/v1/cv/classify ───────────────────────────────────────────────────────

class TestClassifyEndpoint:
    def test_classify_returns_200(self, client, swe_resume_text):
        r = client.post("/api/v1/cv/classify", json={"text": swe_resume_text})
        assert r.status_code == 200

    def test_classify_role_is_valid(self, client, swe_resume_text):
        r = client.post("/api/v1/cv/classify", json={"text": swe_resume_text})
        assert r.json()["job_role"] in ROLE_SET

    def test_classify_confidence_in_range(self, client, swe_resume_text):
        r = client.post("/api/v1/cv/classify", json={"text": swe_resume_text})
        conf = r.json()["role_confidence"]
        assert 0.0 <= conf <= 1.0

    def test_classify_alternatives_list(self, client, swe_resume_text):
        r = client.post("/api/v1/cv/classify", json={"text": swe_resume_text})
        alts = r.json()["role_alternatives"]
        assert isinstance(alts, list)

    def test_classify_empty_text_422(self, client):
        r = client.post("/api/v1/cv/classify", json={"text": ""})
        assert r.status_code == 422


# ── /api/v1/cv/analyze ────────────────────────────────────────────────────────

class TestAnalyzeEndpoint:
    def test_analyze_returns_201(self, client, swe_resume_text):
        r = client.post("/api/v1/cv/analyze", json={
            "text": swe_resume_text,
            "candidate_name": "John Smith",
        })
        assert r.status_code == 201

    def test_analyze_role_in_20(self, client, swe_resume_text):
        r = client.post("/api/v1/cv/analyze", json={
            "text": swe_resume_text,
            "candidate_name": "John Smith",
        })
        assert r.json()["job_role"] in ROLE_SET

    def test_analyze_scores_in_range(self, client, swe_resume_text):
        r = client.post("/api/v1/cv/analyze", json={
            "text": swe_resume_text,
            "candidate_name": "John Smith",
        })
        data = r.json()
        assert 0.0 <= data["S_edu"] <= 100.0
        assert 0.0 <= data["S_exp"] <= 100.0
        assert 0.0 <= data["S_skill"] <= 100.0
        assert 0.0 <= data["skill_score_raw"] <= 1.0
        assert "component_1_scores" in data
        assert "S_skill" in data["component_1_scores"]

    def test_analyze_no_jd_gives_null_similarity(self, client, swe_resume_text):
        r = client.post("/api/v1/cv/analyze", json={
            "text": swe_resume_text,
            "candidate_name": "Test",
        })
        assert r.json()["jd_similarity_score"] is None

    def test_analyze_with_jd_gives_similarity_score(self, client, swe_resume_text, sample_jd_swe):
        r = client.post("/api/v1/cv/analyze", json={
            "text": swe_resume_text,
            "candidate_name": "John Smith",
            "job_description": sample_jd_swe,
        })
        data = r.json()
        assert data["jd_similarity_score"] is not None
        assert 0.0 <= data["jd_similarity_score"] <= 1.0

    def test_analyze_invalid_candidate_id_422(self, client, swe_resume_text):
        r = client.post("/api/v1/cv/analyze", json={
            "text": swe_resume_text,
            "candidate_id": "invalid id with spaces!",
        })
        assert r.status_code == 422

    def test_analyze_has_timestamp(self, client, swe_resume_text):
        r = client.post("/api/v1/cv/analyze", json={
            "text": swe_resume_text,
            "candidate_name": "Alice",
        })
        assert "analysis_timestamp" in r.json()


# ── /api/v1/cv/rank ───────────────────────────────────────────────────────────

class TestRankEndpoint:
    def test_rank_returns_200(self, client, swe_resume_text, ds_resume_text, sample_jd_swe):
        payload = {
            "job_description": sample_jd_swe,
            "candidates": [
                {"text": swe_resume_text, "candidate_name": "SWE Candidate"},
                {"text": ds_resume_text, "candidate_name": "DS Candidate"},
            ],
        }
        r = client.post("/api/v1/cv/rank", json=payload)
        assert r.status_code == 200

    def test_rank_results_contains_component_1_scores(self, client, swe_resume_text, ds_resume_text, sample_jd_swe):
        payload = {
            "job_description": sample_jd_swe,
            "candidates": [
                {"text": swe_resume_text, "candidate_name": "Candidate A"},
                {"text": ds_resume_text,  "candidate_name": "Candidate B"},
            ],
        }
        r = client.post("/api/v1/cv/rank", json=payload)
        ranked = r.json()["ranked_candidates"]
        for c in ranked:
            assert "component_1_scores" in c
            assert 0.0 <= c["S_skill"] <= 100.0

    def test_rank_jd_similarity_populated(self, client, swe_resume_text, sample_jd_swe):
        payload = {
            "job_description": sample_jd_swe,
            "candidates": [{"text": swe_resume_text, "candidate_name": "A"}],
        }
        r = client.post("/api/v1/cv/rank", json=payload)
        for c in r.json()["ranked_candidates"]:
            assert c["jd_similarity_score"] is not None

    def test_rank_total_matches_input(self, client, swe_resume_text, ds_resume_text, sample_jd_swe):
        payload = {
            "job_description": sample_jd_swe,
            "candidates": [
                {"text": swe_resume_text, "candidate_name": "A"},
                {"text": ds_resume_text,  "candidate_name": "B"},
            ],
        }
        r = client.post("/api/v1/cv/rank", json=payload)
        assert r.json()["total_candidates"] == 2

    def test_rank_assigns_sequential_ranks(self, client, swe_resume_text, ds_resume_text, sample_jd_swe):
        payload = {
            "job_description": sample_jd_swe,
            "candidates": [
                {"text": swe_resume_text, "candidate_name": "A"},
                {"text": ds_resume_text,  "candidate_name": "B"},
            ],
        }
        r = client.post("/api/v1/cv/rank", json=payload)
        ranks = [c["rank"] for c in r.json()["ranked_candidates"]]
        assert ranks == [1, 2]


# ── Health ────────────────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_root_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_root_component_field(self, client):
        r = client.get("/")
        assert r.json()["component"] == 1
