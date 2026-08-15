"""Unified RecruitAI Backend - Auth, Resume, Jobs, Export."""
import sys
import os
import logging
from contextlib import asynccontextmanager

# Ensure backend/ is on sys.path for absolute imports
sys.path.insert(0, os.path.dirname(__file__))

import motor.motor_asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import MONGODB_URI, DB_NAME, ALLOWED_ORIGINS
from routers import auth, jobs, resume, export

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s -- %(message)s")
logger = logging.getLogger("recruit-ai")

limiter = Limiter(key_func=get_remote_address)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = motor.motor_asyncio.AsyncIOMotorClient(
        MONGODB_URI, tz_aware=True, serverSelectionTimeoutMS=5000
    )
    db = client[DB_NAME]
    try:
        await db.command("ping")
    except Exception as exc:
        client.close()
        raise RuntimeError(f"MongoDB connection failed: {exc}") from exc

    await db.users.create_index("email", unique=True)
    await db.jobs.create_index([("company_id", 1), ("created_at", -1)])
    await db.resumes.create_index("candidate_id")
    await db.predictions.create_index("candidate_id")
    await db.applications.create_index([("job_id", 1), ("candidate_id", 1)], unique=True)

    app.state.db = db
    os.makedirs("uploads/avatars", exist_ok=True)
    logger.info("RecruitAI connected to MongoDB: %s/%s", MONGODB_URI.split("@")[-1], DB_NAME)
    try:
        yield
    finally:
        client.close()


app = FastAPI(
    title="RecruitAI Unified API",
    version="2.0.0",
    description="Company/Candidate auth, resume parsing, semantic matching, role classification, export.",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(export.router, prefix="/api/v1/export", tags=["Export"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "recruit-ai"}
