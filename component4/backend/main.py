"""
Component 4: Skill Gap Analysis & Career Development
FastAPI Backend — main.py
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import motor.motor_asyncio

load_dotenv()

app = FastAPI(
    title="Component 4 – Skill Gap & Career Development API",
    version="1.0.0",
    description="AI-driven skill gap analysis and personalised career path generation."
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MongoDB ────────────────────────────────────────────────────────────────────
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME     = os.getenv("DB_NAME", "HR")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db     = client[DB_NAME]

# Attach db to app state so routers can access it
app.state.db = db

# ── Routers ────────────────────────────────────────────────────────────────────
from routers import skill_gap, career, progress, analytics

app.include_router(skill_gap.router,  prefix="/api/v1/skill-gap",   tags=["Skill Gap Analysis"])
app.include_router(career.router,     prefix="/api/v1/career",      tags=["Career Guidance"])
app.include_router(progress.router,   prefix="/api/v1/progress",    tags=["Progress Tracking"])
app.include_router(analytics.router,  prefix="/api/v1/analytics",   tags=["Analytics"])

# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "component": 4, "service": "Skill Gap & Career Development"}

@app.get("/health", tags=["Health"])
async def health():
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    return {"status": "ok", "database": db_status}
