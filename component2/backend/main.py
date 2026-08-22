"""
Component 2: AI Interview System - FastAPI Application
Main entry point for the interview backend service
Port: 8002
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from contextlib import asynccontextmanager
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from db import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

# Import routers
from routers.interview import router as interview_router

# ====================================================================
# LIFESPAN CONTEXT MANAGER
# ====================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown
    """
    # Startup
    logger.info("=" * 70)
    logger.info("Component 2: AI Interview System - Starting")
    logger.info("=" * 70)
    
    # Verify models directory exists
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    if not os.path.exists(models_dir):
        logger.warning(f"⚠ Models directory not found: {models_dir}")
        logger.info("Please run: python ml/build_qg_dataset.py && python ml/train_qg_model.py")
    else:
        logger.info(f"✓ Models directory found: {models_dir}")

    # Connect to MongoDB
    try:
        mongodb = get_db()
        logger.info(f"✓ Connected to MongoDB database: {mongodb.name}")
    except Exception as e:
        logger.error(f"✗ Unable to connect to MongoDB: {e}")
        raise
    
    logger.info("✓ Interview system ready on http://localhost:8002")
    logger.info("✓ API Documentation: http://localhost:8002/docs")
    
    yield
    
    # Shutdown
    logger.info("Component 2: AI Interview System - Shutting down")


# ====================================================================
# CREATE FASTAPI APP
# ====================================================================

app = FastAPI(
    title="AI Interview System",
    description="Component 2: Interview Generation & Evaluation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)
app.state.limiter = limiter

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )

app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# ====================================================================
# MIDDLEWARE
# ====================================================================

# CORS Configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://localhost:5177,http://localhost:5178"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


# ====================================================================
# EXCEPTION HANDLERS
# ====================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "details": str(exc)
        }
    )


# ====================================================================
# INCLUDE ROUTERS
# ====================================================================

app.include_router(interview_router)


# ====================================================================
# ROOT ENDPOINTS
# ====================================================================

@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "service": "Component 2: AI Interview System",
        "version": "1.0.0",
        "status": "running",
        "port": 8002,
        "documentation": {
            "swagger": "http://localhost:8002/docs",
            "redoc": "http://localhost:8002/redoc",
            "openapi": "http://localhost:8002/openapi.json"
        }
    }


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "component": "Component 2: AI Interview System",
        "version": "1.0.0"
    }


@app.get("/info", tags=["info"])
async def info():
    """Get system information"""
    return {
        "name": "AI Interview Generation & Evaluation System",
        "component": "Component 2",
        "port": 8002,
        "endpoints": {
            "start_interview": "POST /api/v1/interview/start",
            "submit_answers": "POST /api/v1/interview/submit",
            "get_result": "GET /api/v1/interview/result/{interview_id}",
            "question_bank": "GET /api/v1/interview/questions/{job_role}",
            "available_jobs": "GET /api/v1/interview/jobs",
            "health": "GET /api/v1/interview/health"
        },
        "features": {
            "question_generation": "Generates MCQ, Descriptive, and Coding questions",
            "semantic_scoring": "SBERT-based semantic similarity for descriptive answers",
            "automatic_evaluation": "MCQ, Descriptive, and Coding answer evaluation",
            "interview_scoring": "Combined interview score with grade bands",
            "weak_area_detection": "Identifies candidate weak areas based on performance"
        }
    }


# ====================================================================
# MAIN ENTRY POINT
# ====================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
