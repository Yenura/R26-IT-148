"""hr-recruiter app configuration."""

import os

from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return int(raw)


MONGODB_URI   = os.getenv("MONGODB_URI", "mongodb+srv://admin:PxUm8dLzq5jqlHYN@coordinator.ljarc.mongodb.net/HR")
DB_NAME       = os.getenv("DB_NAME", "HR")

# Component 4's database is read-only (candidate skill-gap reports).
REPORTS_DB         = os.getenv("REPORTS_DB", "HR")
REPORTS_COLLECTION = os.getenv("REPORTS_COLLECTION", "skill_gap_reports")

JWT_SECRET        = os.getenv("JWT_SECRET", "dev-insecure-secret-change-me")
JWT_ALGORITHM     = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = _int_env("TOKEN_EXPIRE_MINUTES", 1440)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174",
).split(",")
