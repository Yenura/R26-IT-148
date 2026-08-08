"""Component 1 — Job & CV Intelligence API (port 8001)."""

import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import create_store

load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger("component1")

PORT = int(os.getenv("PORT", "8001"))
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174"
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = await create_store()
    yield


app = FastAPI(
    title="Component 1 – Job & CV Intelligence API",
    version="1.0.0",
    description="CV parsing, skill extraction and TF-IDF CV↔job matching (port 8001).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

from routers import match, jobs  # noqa: E402

app.include_router(match.router, prefix="/api/v1", tags=["CV Matching"])
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "component": 1, "service": "Job & CV Intelligence",
            "port": PORT}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "store": type(app.state.store).__name__,
            "port": PORT}
