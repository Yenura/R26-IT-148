"""Pytest conftest — Component 1
IT22089236 | D T D Perera | R26-IT-148

Provides shared fixtures and configures test DB isolation.
Mongo tests are skipped if MongoDB is unreachable.
SBERT tests are skipped if sentence-transformers is unavailable.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Ensure component1/ root is on sys.path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ── Test environment ───────────────────────────────────────────────────────────
# Use a dedicated test DB so tests never touch the production "resumes" DB.
os.environ.setdefault("DB_NAME", "resumes_test")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def swe_resume_text():
    return (FIXTURES_DIR / "sample_swe_resume.txt").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def ds_resume_text():
    return (FIXTURES_DIR / "sample_ds_resume.txt").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def sample_jd_swe():
    return (
        "We are looking for a Software Engineer with strong Python and Java skills, "
        "experience in REST API design, OOP, data structures, algorithms, and SQL. "
        "Familiarity with Git, unit testing, and Agile methodologies is required."
    )


@pytest.fixture(scope="session")
def sample_jd_ds():
    return (
        "Data Scientist needed with expertise in statistics, machine learning, "
        "feature engineering, Python, pandas, NumPy, SQL, and data visualisation. "
        "Experience with hypothesis testing and A/B experiments is a plus."
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_mongo: mark test as requiring a live MongoDB connection"
    )
    config.addinivalue_line(
        "markers", "requires_sbert: mark test as requiring sentence-transformers"
    )


def pytest_runtest_setup(item):
    """Skip marked tests if prerequisites are unavailable."""
    if item.get_closest_marker("requires_mongo"):
        _check_mongo()
    if item.get_closest_marker("requires_sbert"):
        _check_sbert()


def _check_mongo():
    try:
        import pymongo
        client = pymongo.MongoClient(
            os.environ["MONGODB_URI"],
            serverSelectionTimeoutMS=1000,
        )
        client.admin.command("ping")
    except Exception:
        pytest.skip("MongoDB not reachable — skipping Mongo tests")


def _check_sbert():
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        pytest.skip("sentence-transformers not installed — skipping SBERT tests")
