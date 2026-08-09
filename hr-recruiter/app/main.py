"""hr-recruiter FastAPI application.

HR recruiter service: recruiter accounts, job posting CRUD, and CSS-ranked
candidate shortlists. Component 1/2/3/4 are not modified:
- component3 CSS engine is imported read-only via ``app.engine_link``
- component4 skill-gap reports are read (read-only) from its Mongo database
- this app's own data lives in its own database (``DB_NAME``)
"""

import logging
from contextlib import asynccontextmanager

import motor.motor_asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.routers import auth, jobs, ranking

logger = logging.getLogger("hr-recruiter")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = motor.motor_asyncio.AsyncIOMotorClient(
        config.MONGODB_URI,
        tz_aware=True,
        serverSelectionTimeoutMS=5000,
    )
    db = client[config.DB_NAME]
    reports_db = client[config.REPORTS_DB]

    try:
        await db.command("ping")
        await reports_db.command("ping")
    except Exception as exc:
        await client.close()
        raise RuntimeError(
            f"MongoDB connection failed for {config.MONGODB_URI.split('@')[-1]!r}"
        ) from exc

    await db.recruiters.create_index("email", unique=True)
    await db.job_postings.create_index([("recruiter_id", 1), ("created_at", -1)])
    await db.applications.create_index(
        [("job_id", 1), ("candidate_id", 1)], unique=True
    )

    app.state.db = db
    app.state.reports_db = reports_db
    logger.info("hr-recruiter connected: %s / %s", config.MONGODB_URI.split("@")[-1], config.DB_NAME)

    try:
        yield
    finally:
        client.close()


app = FastAPI(
    title="HR Recruiter API",
    version="1.0.0",
    description=(
        "Recruiter accounts, job posting CRUD, and CSS-engine ranked shortlists "
        "using component3's scoring engine (read-only) and component4 reports (read-only)."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(ranking.router, prefix="/api/v1/jobs", tags=["Ranking"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
