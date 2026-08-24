"""Component 1 — FastAPI Backend Entry Point
IT22094872 | Dulnith K.D. | R26-IT-148

Run with:
    cd component1
    uvicorn backend.main:app --port 8001 --reload
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure component1/ root is on sys.path regardless of launch directory
_COMP1_ROOT = Path(__file__).parent.parent
if str(_COMP1_ROOT) not in sys.path:
    sys.path.insert(0, str(_COMP1_ROOT))

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("component1")

# ── Config ────────────────────────────────────────────────────────────────────
MONGODB_URI     = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    logger.critical("MONGODB_URI not set — copy .env.example to .env and fill credentials")
    raise SystemExit(1)
DB_NAME         = os.getenv("DB_NAME", "HR")
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5174",
).split(",")
MODEL_DIR = Path(os.getenv("MODEL_DIR", "models"))

# ── Lifespan: DB + model loading ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Component 1 — connecting to MongoDB…")

    # Motor client
    client = motor.motor_asyncio.AsyncIOMotorClient(
        MONGODB_URI,
        maxPoolSize=10,
        minPoolSize=2,
        serverSelectionTimeoutMS=5000,
    )
    db = client[DB_NAME]
    app.state.db = db

    try:
        await db.command("ping")
        logger.info("MongoDB connected: %s / %s", MONGODB_URI.split("@")[-1], DB_NAME)
    except Exception as exc:
        logger.warning("MongoDB not available: %s — DB operations will fail gracefully", exc)

    # Indexes (idempotent)
    try:
        await db.cv_analyses.create_index([("candidate_id", 1)], unique=True)
        await db.cv_analyses.create_index([("analysis_timestamp", -1)])
        await db.cv_analyses.create_index([("job_role", 1)])
        await db.cv_analyses.create_index([("cv_matching_score", -1)])
        logger.info("MongoDB indexes verified")
    except Exception as exc:
        logger.warning("Index creation skipped: %s", exc)

    # Load ML models once at startup
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from backend.services.predictor import Predictor
    from backend.services.matcher import JDMatcher

    predictor = Predictor(model_dir=MODEL_DIR)
    logger.info("Predictor loaded in mode: %s", predictor.mode)

    # Share SBERT / TF-IDF with the matcher to avoid loading models twice
    matcher = JDMatcher(
        sbert_model=getattr(predictor, "_sbert_model", None),
        tfidf_vectorizer=getattr(predictor, "_vectorizer", None),
    )
    logger.info("JDMatcher loaded in mode: %s", matcher.mode)

    app.state.predictor = predictor
    app.state.matcher   = matcher

    yield

    client.close()
    logger.info("MongoDB connection closed")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Component 1 — Resume Screening & Role Matching",
    version="1.0.0",
    description=(
        "Automated resume screening, 20-role classification (SBERT + LogisticRegression), "
        "and semantic JD-matching for the AI-Driven Recruitment Ecosystem (R26-IT-148)."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from backend.routers.cv import router as cv_router  # noqa: E402

app.include_router(cv_router, prefix="/api/v1/cv", tags=["CV Analysis"])
app.include_router(cv_router, prefix="/api/v1", tags=["Screen Resume"])




# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "component": 1,
        "service": "Resume Screening & Role Matching",
        "version": "1.0.0",
        "owner": "Dulnith K.D. — IT22094872",
    }


@app.get("/health", tags=["Health"])
async def health():
    try:
        await app.state.db.command("ping")
        db_status = "connected"
    except Exception as exc:
        db_status = f"error: {exc}"

    predictor = getattr(app.state, "predictor", None)
    return {
        "status": "ok",
        "database": db_status,
        "predictor_mode": predictor.mode if predictor else "not_loaded",
    }
