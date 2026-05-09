"""
Component 2: Interview System - FastAPI Router
Handles HTTP endpoints for interview management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
import logging

from models.schemas import (
    InterviewRequest, InterviewSession, InterviewQuestion,
    AnswerSubmission, InterviewScoreResult, EvaluationResponse,
    ErrorResponse, DifficultyEnum, QuestionTypeEnum
)
from services.ml_engine import get_interview_service, get_evaluation_service

router = APIRouter(prefix="/api/v1/interview", tags=["interview"])
logger = logging.getLogger(__name__)


# ====================================================================
# DEPENDENCY INJECTION
# ====================================================================

def get_services():
    """Get services - resolve models directory relative to this file"""
    import os
    _backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir   = os.path.join(_backend_dir, "trained_models")
    return {
        "interview_service": get_interview_service(models_dir),
        "evaluation_service": get_evaluation_service(models_dir)
    }


# ====================================================================
# ENDPOINTS
# ====================================================================

@router.post("/start", response_model=InterviewSession)
async def start_interview(request: InterviewRequest, services: Dict = Depends(get_services)):
    """
    Create and start a new interview session
    
    Args:
        request: Interview creation request with candidate_id, job_role, skills, num_questions
        
    Returns:
        Interview session with questions
    """
    try:
        interview_service = services["interview_service"]
        
        # Validate job role
        available_jobs = interview_service.get_available_jobs()
        if request.job_role not in available_jobs:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid job role. Available: {', '.join(available_jobs)}"
            )
        
        # Create session
        session = interview_service.create_interview_session(
            candidate_id=request.candidate_id,
            job_role=request.job_role,
            num_questions=request.num_questions
        )
        
        # Convert to response model
        questions = [
            InterviewQuestion(
                id=q.get("id"),
                sequence=q.get("sequence", 0),
                question_text=q.get("question_text"),
                question_type=QuestionTypeEnum(q.get("question_type", "MCQ")),
                difficulty=DifficultyEnum(q.get("difficulty", "Easy")),
                category=q.get("category", ""),
                topic=q.get("topic", ""),
                time_limit_seconds=q.get("time_limit", 900)
            )
            for q in session.get("questions", [])
        ]
        
        return InterviewSession(
            session_id=session["session_id"],
            candidate_id=session["candidate_id"],
            job_role=session["job_role"],
            required_skills=session["required_skills"],
            questions=questions,
            question_count=session["question_count"],
            total_questions=session["total_questions"],
            created_at=session["created_at"],
            status=session["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=InterviewScoreResult)
async def submit_answers(submission: Dict, services: Dict = Depends(get_services)):
    """
    Submit answers and get evaluation results
    
    Args:
        submission: Dictionary with candidate_id, session_id, job_role, answers
        
    Returns:
        Interview score result with grades and weak areas
    """
    try:
        interview_service = services["interview_service"]
        
        # Evaluate interview
        result = interview_service.evaluate_interview(
            session_id=submission.get("session_id"),
            interview_data=submission
        )
        
        return InterviewScoreResult(
            interview_id=result["interview_id"],
            candidate_id=result["candidate_id"],
            session_id=result["session_id"],
            job_role=result["job_role"],
            mcq_score=result["mcq_score"],
            descriptive_score=result["descriptive_score"],
            coding_score=result["coding_score"],
            interview_score=result["interview_score"],
            grade=result["grade"],
            mcq_total=result["mcq_total"],
            descriptive_total=result["descriptive_total"],
            coding_total=result["coding_total"],
            weak_topics=result.get("weak_topics", []),
            weights_used=result["weights_used"],
            created_at=result["created_at"]
        )
        
    except Exception as e:
        logger.error(f"Error submitting answers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{interview_id}", response_model=EvaluationResponse)
async def get_result(interview_id: str, services: Dict = Depends(get_services)):
    """
    Get evaluation result for an interview
    
    Args:
        interview_id: Interview result ID
        
    Returns:
        Evaluation response with score details
    """
    try:
        # In production, fetch from database
        # For now, return mock data
        
        return EvaluationResponse(
            success=True,
            message="Interview result retrieved",
            data={
                "interview_id": interview_id,
                "candidate_id": "CAND-001",
                "session_id": "INT-001",
                "job_role": "Software Engineer",
                "interview_score": 78.5,
                "grade": "Good",
                "mcq_score": 80,
                "descriptive_score": 75,
                "coding_score": 80,
                "weak_topics": ["Algorithms", "System Design"]
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/questions/{job_role}", response_model=Dict)
async def get_question_bank(job_role: str, services: Dict = Depends(get_services)):
    """
    Get question bank for a specific job role
    
    Args:
        job_role: Target job role
        
    Returns:
        Question bank grouped by type and difficulty
    """
    try:
        interview_service = services["interview_service"]
        
        # Validate job role
        available_jobs = interview_service.get_available_jobs()
        if job_role not in available_jobs:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid job role. Available: {', '.join(available_jobs)}"
            )
        
        # Get required skills
        required_skills = interview_service.get_job_skills(job_role)
        
        # Filter questions by relevance
        question_bank = interview_service.question_bank
        relevant_questions = [
            q for q in question_bank
            if any(
                skill.lower() in q.get("category", "").lower() 
                or skill.lower() in q.get("topic", "").lower()
                for skill in required_skills
            )
        ]
        
        # Group by type and difficulty
        grouped = {
            "MCQ": {"Easy": [], "Medium": [], "Hard": []},
            "Descriptive": {"Easy": [], "Medium": [], "Hard": []},
            "Coding": {"Easy": [], "Medium": [], "Hard": []}
        }
        
        for q in relevant_questions:
            qtype = q.get("question_type", "Descriptive")
            difficulty = q.get("difficulty", "Easy")
            
            if qtype in grouped and difficulty in grouped[qtype]:
                grouped[qtype][difficulty].append({
                    "id": q.get("id"),
                    "question": q.get("question_text", "")[:100] + "...",
                    "difficulty": difficulty,
                    "category": q.get("category")
                })
        
        return {
            "success": True,
            "job_role": job_role,
            "required_skills": required_skills,
            "question_bank": grouped,
            "total_questions": len(relevant_questions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving question bank: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=Dict)
async def get_available_jobs(services: Dict = Depends(get_services)):
    """
    Get list of available job roles
    
    Returns:
        List of job roles and their required skills
    """
    try:
        interview_service = services["interview_service"]
        
        jobs = {}
        for job_role in interview_service.get_available_jobs():
            skills = interview_service.get_job_skills(job_role)
            jobs[job_role] = skills
        
        return {
            "success": True,
            "jobs": jobs,
            "total_jobs": len(jobs)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict)
async def health_check(services: Dict = Depends(get_services)):
    """
    Health check endpoint
    
    Returns:
        Health status
    """
    try:
        interview_service = services["interview_service"]
        available_jobs = len(interview_service.get_available_jobs())
        question_count = len(interview_service.question_bank) if interview_service.question_bank else 0
        
        return {
            "status": "healthy",
            "available_jobs": available_jobs,
            "questions_in_bank": question_count,
            "component": "Component 2: AI Interview System",
            "port": 8002
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
