"""Component 3 — Interview-Driven Candidate Ranking API (port 8003)."""

import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from db import create_store

load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger("component3")

PORT = int(os.getenv("PORT", "8003"))
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://localhost:5177,http://localhost:5178"
).split(",")

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = await create_store()
    yield


app = FastAPI(
    title="Component 3 – Candidate Ranking API",
    version="1.0.0",
    description="CSS (Equations 1-8) + LambdaMART LTR candidate ranking (port 8003).",
    lifespan=lifespan,
)
app.state.limiter = limiter

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )

app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import rank  # noqa: E402

app.include_router(rank.router, prefix="/api/v1", tags=["Ranking"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "component": 3,
            "service": "Interview-Driven Candidate Ranking", "port": PORT}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "store": type(app.state.store).__name__,
            "ltr": getattr(app.state, "ltr_loaded", True), "port": PORT}
