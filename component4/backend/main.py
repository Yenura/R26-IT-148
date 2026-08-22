"""
Component 4: Skill Gap Analysis & Career Development
FastAPI Backend — main.py

Fixes applied (code review):
  - C2: Restricted CORS to env-configured origins only
  - C3: MongoDB managed via lifespan context (startup/shutdown + connection pool)
  - L4: DB indexes created on startup
  - Structured logging added
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
import motor.motor_asyncio

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("component4")

limiter = Limiter(key_func=get_remote_address)

# ── Config ────────────────────────────────────────────────────────────────────
MONGODB_URI     = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    logger.critical("MONGODB_URI not set — copy .env.example to .env and fill credentials")
    raise SystemExit(1)
DB_NAME         = os.getenv("DB_NAME", "HR")
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://localhost:5177,http://localhost:5178"
).split(",")


# ── Lifespan: manages DB connection pool + index creation ────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: open DB on startup, close cleanly on shutdown."""
    logger.info("Starting up — connecting to MongoDB...")
    client = motor.motor_asyncio.AsyncIOMotorClient(
        MONGODB_URI,
        maxPoolSize=10,
        minPoolSize=2,
        serverSelectionTimeoutMS=5000,
    )
    db = client[DB_NAME]
    app.state.db = db

    # Verify connection
    try:
        await db.command("ping")
        logger.info("MongoDB connected: %s / %s", MONGODB_URI.split("@")[-1], DB_NAME)
    except Exception as exc:
        logger.critical("MongoDB connection failed: %s", exc)

    # Ensure indexes exist (idempotent)
    await db.skill_gap_reports.create_index([("candidate_id", 1)])
    await db.skill_gap_reports.create_index([("hire_probability", -1)])
    await db.skill_gap_reports.create_index([("job_role", 1)])
    await db.skill_gap_reports.create_index([("created_at", -1)])
    await db.progress_tracking.create_index(
        [("candidate_id", 1), ("skill", 1)], unique=True
    )
    logger.info("MongoDB indexes verified")

    yield  # ← application runs here

    # Shutdown
    client.close()
    logger.info("MongoDB connection closed")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Component 4 – Skill Gap & Career Development API",
    version="2.0.0",
    description=(
        "AI-driven skill gap analysis and personalised career path generation. "
        "Trained on 10,000-record dataset (Logistic Regression, AUC 0.9936)."
    ),
    lifespan=lifespan,
)
app.state.limiter = limiter

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )

app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# ── CORS (C2 fix: explicit origins, not wildcard) ─────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
from routers import skill_gap, career, progress, analytics  # noqa: E402

app.include_router(skill_gap.router, prefix="/api/v1/skill-gap", tags=["Skill Gap Analysis"])
app.include_router(skill_gap.router, prefix="/api/v1", tags=["Skill Gap Direct"])
app.include_router(career.router,    prefix="/api/v1/career",    tags=["Career Guidance"])
app.include_router(career.router,    prefix="/api/v1",           tags=["Career Guidance Direct"])
app.include_router(progress.router,  prefix="/api/v1/progress",  tags=["Progress Tracking"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "component": 4,
        "service": "Skill Gap & Career Development",
        "version": "2.0.0",
    }


@app.get("/health", tags=["Health"])
async def health():
    try:
        await app.state.db.command("ping")
        db_status = "connected"
    except Exception as exc:
        db_status = f"error: {exc}"
        logger.warning("Health check: DB ping failed — %s", exc)
    return {"status": "ok", "database": db_status}
