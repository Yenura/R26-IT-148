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
from db import save_session, get_session, save_result, get_result, update_session_status

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
            num_questions=request.num_questions,
            employer_skills=request.required_skills or None,
        )
        
        # Persist interview session to MongoDB
        save_session(session)
        
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
                options=q.get("options"),
                test_cases=q.get("test_cases"),
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
        
        session_id = submission.get("session_id")
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        # Enrich answer payload with question_type and correctness
        question_map = {
            q["id"]: q for q in session.get("questions", [])
            if q.get("id")
        }
        processed_answers = []

        for answer in submission.get("answers", []):
            question_id = answer.get("question_id")
            question = question_map.get(question_id)
            if not question:
                continue

            question_type = question.get("question_type")
            processed_answer = {
                "question_id": question_id,
                "question_type": question_type,
                "topic": question.get("topic", "Unknown")
            }

            if question_type == "MCQ":
                candidate_choice = answer.get("selected_option")
                if candidate_choice is None:
                    candidate_choice = answer.get("answer")
                correct_choice = question.get("correct_option")
                processed_answer["selected_option"] = candidate_choice
                processed_answer["correct_option"] = correct_choice
                processed_answer["is_correct"] = candidate_choice == correct_choice
                processed_answer["score"] = 100 if processed_answer["is_correct"] else 0

            elif question_type == "Descriptive":
                answer_text = answer.get("answer_text") or answer.get("answer") or ""
                reference_text = question.get("answer_text") or question.get("expected_answer") or ""
                evaluation_result = services["evaluation_service"].evaluate_descriptive(
                    reference=reference_text,
                    candidate=answer_text
                )
                processed_answer.update({
                    "answer_text": answer_text,
                    "final_score": evaluation_result.get("final_score", 0),
                    "similarity": evaluation_result.get("similarity", 0),
                    "keyword_coverage": evaluation_result.get("keyword_coverage", 0)
                })

            elif question_type == "Coding":
                code_text = answer.get("code_text") or answer.get("answer") or answer.get("code") or ""
                evaluation_result = services["evaluation_service"].evaluate_coding(
                    code_text=code_text,
                    test_cases=question.get("test_cases", []) or []
                )
                processed_answer.update({
                    "code_text": code_text,
                    "language": answer.get("language", "Python"),
                    "code_score": evaluation_result.get("code_score", 0),
                    "syntax_valid": evaluation_result.get("syntax_valid", False),
                    "test_pass_rate": evaluation_result.get("test_pass_rate", 0),
                    "tests_passed": evaluation_result.get("tests_passed", 0),
                    "total_tests": evaluation_result.get("total_tests", len(question.get("test_cases", []) or [])),
                    "quality_score": evaluation_result.get("quality_score", 0)
                })

            processed_answers.append(processed_answer)

        evaluation_payload = {
            "candidate_id": submission.get("candidate_id"),
            "session_id": session_id,
            "job_role": submission.get("job_role"),
            "answers": processed_answers
        }
        
        result = interview_service.evaluate_interview(
            session_id=session_id,
            interview_data=evaluation_payload
        )

        save_result(result)
        update_session_status(session_id, "completed")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting answers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{interview_id}", response_model=EvaluationResponse)
async def fetch_interview_result(interview_id: str, services: Dict = Depends(get_services)):
    """
    Get evaluation result for an interview
    
    Args:
        interview_id: Interview result ID
        
    Returns:
        Evaluation response with score details
    """
    try:
        result = get_result(interview_id)
        if not result:
            raise HTTPException(status_code=404, detail="Interview result not found")

        return EvaluationResponse(
            success=True,
            message="Interview result retrieved",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Error retrieving result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}", response_model=Dict)
async def fetch_interview_session(session_id: str):
    """
    Get interview session by ID
    
    Args:
        session_id: Interview session ID

    Returns:
        Interview session payload
    """
    try:
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")

        return {
            "success": True,
            "session": session
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving interview session: {e}")
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
