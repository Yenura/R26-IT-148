"""
Component 2: Interview System - FastAPI Router
Handles HTTP endpoints for interview management
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Optional
from starlette.concurrency import run_in_threadpool
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
import sys
import json
import textwrap
import subprocess
import tempfile
import os
import ast

from models.schemas import (
    InterviewRequest, InterviewSession, InterviewQuestion,
    AnswerSubmission, InterviewScoreResult, EvaluationResponse,
    ErrorResponse, DifficultyEnum, QuestionTypeEnum
)
from services.ml_engine import get_interview_service, get_evaluation_service
from db import save_session, get_session, save_result, get_result, update_session_status

router = APIRouter(prefix="/api/v1/interview", tags=["interview"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


def _is_py_literal(value) -> bool:
    """True if the value is a safe Python literal (safe to inject as code)."""
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        ast.literal_eval(value)
        return True
    except (ValueError, SyntaxError):
        return False


def _output_matches(output: str, expected: str) -> bool:
    """Compare sandbox stdout to expected. Space-insensitive for collection types."""
    if output == expected:
        return True
    if expected[:1] in "[{(":
        return output.replace(" ", "") == expected.replace(" ", "")
    return False


def _run_code_in_sandbox(code_text: str, inp: dict) -> str:
    """Execute candidate code with injected inputs in a subprocess sandbox.

    Returns the stripped stdout of the run ("" on syntax/fatal errors).
    Injection mirrors scoring: inputs become variables the code reads,
    candidates print() the result.
    """
    inject = "".join(f"{k} = {v}\n" for k, v in inp.items())
    sandbox_wrapper = (
        "import sys as _sys\n"
        "from io import StringIO\n"
        "_blocked = {'os','subprocess','shutil','socket','pathlib','ctypes','multiprocessing','threading','signal','inspect','importlib'}\n"
        "_real_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__\n"
        "def _safe_import(name, *a, **kw):\n"
        "    if name in _blocked: raise ImportError(f'Blocked: {name}')\n"
        "    return _real_import(name, *a, **kw)\n"
        "__builtins__.__import__ = _safe_import\n"
        "_stdout = _sys.stdout\n"
        "_sys.stdout = StringIO()\n"
        "try:\n"
        + textwrap.indent(inject, "    ")
        + textwrap.indent(code_text, "    ") + "\n"
        "    _output = _sys.stdout.getvalue().strip()\n"
        "except Exception:\n"
        "    _output = ''\n"
        "finally:\n"
        "    _sys.stdout = _stdout\n"
        "print(_output)\n"
    )
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sandbox_wrapper)
            tmp = f.name
        result = subprocess.run(
            [sys.executable, tmp], capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return ""
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except Exception:
                pass


# ====================================================================
# DEPENDENCY INJECTION
# ====================================================================

def get_services():
    """Get services - resolve models directory relative to this file"""
    import os
    _backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir   = os.path.join(_backend_dir, "..", "models")
    return {
        "interview_service": get_interview_service(models_dir),
        "evaluation_service": get_evaluation_service(models_dir)
    }


# ====================================================================
# ENDPOINTS
# ====================================================================

@router.post("/start", response_model=InterviewSession)
@limiter.limit("10/minute")
async def start_interview(request: Request, interview_request: InterviewRequest, services: Dict = Depends(get_services)):
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
        if interview_request.job_role not in available_jobs:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid job role. Available: {', '.join(available_jobs)}"
            )
        
        # Create session (CPU-bound: question generation + filtering)
        session = await run_in_threadpool(
            interview_service.create_interview_session,
            candidate_id=interview_request.candidate_id,
            job_role=interview_request.job_role,
            num_questions=interview_request.num_questions,
            employer_skills=interview_request.required_skills or None,
            job_level=interview_request.job_level or "Mid-Level",
        )
        
        # Persist interview session to MongoDB
        await save_session(session)
        
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
        logger.error(f"Error starting interview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=InterviewScoreResult)
@limiter.limit("5/minute")
async def submit_answers(request: Request, submission: Dict, services: Dict = Depends(get_services)):
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
        session = await get_session(session_id)
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
                try:
                    candidate_choice = int(candidate_choice)
                except (TypeError, ValueError):
                    candidate_choice = -1
                correct_choice = question.get("correct_option") or question.get("correct_answer_index", 0)
                processed_answer["selected_option"] = candidate_choice
                processed_answer["correct_option"] = correct_choice
                processed_answer["is_correct"] = candidate_choice == correct_choice

            elif question_type == "Descriptive":
                answer_text = answer.get("answer_text") or answer.get("answer") or ""
                reference_text = question.get("answer_text") or question.get("expected_answer") or ""
                evaluation_result = await run_in_threadpool(
                    services["evaluation_service"].evaluate_descriptive,
                    reference=reference_text,
                    candidate=answer_text,
                )
                processed_answer.update({
                    "answer_text": answer_text,
                    "final_score": evaluation_result.get("final_score", 0),
                    "similarity": evaluation_result.get("similarity", 0),
                    "keyword_coverage": evaluation_result.get("keyword_coverage", 0)
                })

            elif question_type == "Coding":
                code_text = answer.get("code_text") or answer.get("answer") or answer.get("code") or ""
                test_cases = question.get("test_cases", []) or []
                syntax_valid = True
                try:
                    compile(code_text, "<string>", "exec")
                except SyntaxError:
                    syntax_valid = False
                # Only test cases with a real expected output AND Python-literal input
                # are verifiable. Placeholders ("result", "See answer", etc.) must not
                # silently fail correct code.
                verifiable_tests = []
                for tc in test_cases:
                    expected = str(tc.get("expected_output", "")).strip()
                    if not expected or expected.lower() in ("see answer", "result"):
                        continue
                    inp = tc.get("input") or {}
                    if isinstance(inp, dict) and inp and all(_is_py_literal(v) for v in inp.values()):
                        verifiable_tests.append((tc, inp))
                tests_passed = 0
                if verifiable_tests and syntax_valid:
                    for tc, inp in verifiable_tests:
                        expected = str(tc.get("expected_output", "")).strip()
                        output = _run_code_in_sandbox(code_text, inp)
                        if _output_matches(output, expected):
                            tests_passed += 1
                total_tests = len(verifiable_tests)
                if total_tests:
                    test_pass_rate = tests_passed / total_tests
                else:
                    test_pass_rate = None  # untestable question: never silently score 0
                lines = code_text.strip().split('\n')
                code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
                has_return = any(kw in code_text for kw in ['def ', 'class ', 'return'])
                quality_score = 0.5 * float(syntax_valid) + 0.3 * float(0 < code_lines < 200) + 0.2 * float(has_return)
                if test_pass_rate is None:
                    # No verifiable test case exists (placeholder/legacy data).
                    # Grade on structure alone; don't punish correct code.
                    # ponytail: ceiling is structural-only grading (syntax+shape), so a
                    # well-structured wrong answer can score high; upgrade = ensure the
                    # question bank never ships questions without executable test cases.
                    code_score = round(quality_score * 100, 2)
                else:
                    # Passing tests is ground truth for correctness: all pass = 100.
                    # Quality heuristics only break ties when no tests can run.
                    code_score = round(test_pass_rate * 100, 2)
                processed_answer.update({
                    "code_text": code_text,
                    "language": answer.get("language", "Python"),
                    "code_score": code_score,
                    "syntax_valid": syntax_valid,
                    "test_pass_rate": round(test_pass_rate, 4) if test_pass_rate is not None else None,
                    "tests_passed": tests_passed,
                    "total_tests": total_tests,
                    "quality_score": round(quality_score * 100, 2)
                })

            processed_answers.append(processed_answer)

        evaluation_payload = {
            "candidate_id": submission.get("candidate_id"),
            "session_id": session_id,
            "job_role": submission.get("job_role"),
            "answers": processed_answers
        }
        
        result = await run_in_threadpool(
            interview_service.evaluate_interview,
            session_id=session_id,
            interview_data=evaluation_payload,
        )

        await save_result(result)
        await update_session_status(session_id, "completed")
        
        # Send scores to C0 unified backend for ranking pipeline
        try:
            import urllib.request
            c0_url = os.environ.get("C0_URL", "http://127.0.0.1:8000")
            payload = json.dumps({
                "candidate_id": result["candidate_id"],
                "job_id": submission.get("job_id", ""),
                "session_id": session_id,
                "job_role": result["job_role"],
                "mcq_score": result["mcq_score"],
                "descriptive_score": result["descriptive_score"],
                "coding_score": result["coding_score"],
                "interview_score": result["interview_score"],
                "grade": result["grade"],
            }).encode()
            req = urllib.request.Request(
                f"{c0_url}/api/v1/resume/interview-scores",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            logger.warning(f"Failed to send scores to C0: {e}")

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
            mcq_correct=result["mcq_correct"],
            descriptive_total=result["descriptive_total"],
            coding_total=result["coding_total"],
            coding_tests_passed=result.get("coding_tests_passed", 0),
            weak_topics=result.get("weak_topics", []),
            weights_used=result["weights_used"],
            created_at=result["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting answers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code/run")
@limiter.limit("10/minute")
async def run_candidate_code(request: Request, payload: Dict):
    """
    Run candidate code against the question's test cases without scoring.
    Uses the exact same sandbox as submit, so what the candidate sees in
    testing is what the scorer checks. Returns outputs, never answers.
    """
    code_text = payload.get("code_text") or ""
    test_cases = payload.get("test_cases") or []
    syntax_valid = True
    try:
        compile(code_text, "<string>", "exec")
    except SyntaxError:
        syntax_valid = False

    results = []
    for tc in test_cases:
        expected = str(tc.get("expected_output", "")).strip()
        if not expected or expected.lower() in ("see answer", "result"):
            continue
        inp = tc.get("input") or {}
        if not (isinstance(inp, dict) and inp and all(_is_py_literal(v) for v in inp.values())):
            continue
        output = _run_code_in_sandbox(code_text, inp) if syntax_valid else ""
        results.append({
            "input": inp,
            "expected": expected,
            "output": output,
            "passed": _output_matches(output, expected) if output else False,
        })

    return {
        "syntax_valid": syntax_valid,
        "results": results,
    }


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
        result = await get_result(interview_id)
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
        session = await get_session(session_id)
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
