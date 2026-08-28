"""
Component 2: Interview System - FastAPI Router
Handles HTTP endpoints for interview management
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Optional
from starlette.concurrency import run_in_threadpool
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel, Field, field_validator
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
from db import save_session, get_session, save_result, get_result, update_session_status, get_seen_question_ids

router = APIRouter(prefix="/api/v1/interview", tags=["interview"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


class InterviewSubmitRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=200)
    answers: List[Dict] = Field(default_factory=list)

    @field_validator("answers")
    @classmethod
    def validate_answers(cls, v: List[Dict]) -> List[Dict]:
        if len(v) > 100:
            raise ValueError("Too many answers (max 100)")
        return v


class CodeRunRequest(BaseModel):
    code_text: str = Field(default="", max_length=50000)
    test_cases: List[Dict] = Field(default_factory=list)

    @field_validator("test_cases")
    @classmethod
    def validate_test_cases(cls, v: List[Dict]) -> List[Dict]:
        if len(v) > 50:
            raise ValueError("Too many test cases (max 50)")
        return v


def _is_py_literal(value) -> bool:
    """True if the value can be safely injected as a Python variable."""
    if value is None:
        return False
    if isinstance(value, (int, float, bool, list, dict, tuple)):
        return True
    if isinstance(value, str) and value.strip():
        return True
    return False


def _output_matches(output: str, expected: str) -> bool:
    """Compare sandbox stdout to expected. Handles float/int, bool case, collections."""
    if output == expected:
        return True
    if expected[:1] in "[{(":
        return output.replace(" ", "") == expected.replace(" ", "")
    # Normalize float/int: "5.0" == "5", "5.00" == "5"
    try:
        if float(output) == float(expected):
            return True
    except (ValueError, TypeError):
        pass
    # Normalize bool case: "True" == "true"
    if output.lower() == expected.lower() and output.lower() in ("true", "false"):
        return True
    return False


def _run_code_in_sandbox(code_text: str, inp: dict) -> str:
    """Execute candidate code with injected inputs in a subprocess sandbox.

    Returns the stripped stdout of the run ("" on syntax/fatal errors).
    Injection mirrors scoring: inputs become variables the code reads,
    candidates print() the result.
    """
    inject = "".join(f"{k} = {repr(v) if isinstance(v, str) else v}\n" for k, v in inp.items())
    sandbox_wrapper = (
        "import sys as _sys\n"
        "from io import StringIO\n"
        "_blocked = {\n"
        "    'os','subprocess','shutil','socket','pathlib','ctypes',\n"
        "    'multiprocessing','threading','signal','inspect','importlib',\n"
        "    'pickle','pickletools','shelve','marshal','copyreg',\n"
        "    'urllib','urllib.request','urllib.parse','urllib.error',\n"
        "    'http','http.client','http.server',\n"
        "    'smtplib','ftplib','telnetlib','xmlrpc',\n"
        "    'webbrowser','code','codeop','compileall',\n"
        "    '_thread','dummy_thread',\n"
        "}\n"
        "_real_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__\n"
        "def _safe_import(name, *a, **kw):\n"
        "    top = name.split('.')[0]\n"
        "    if top in _blocked: raise ImportError(f'Blocked: {name}')\n"
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
        
        # Validate job role with robust fallback
        available_jobs = interview_service.get_available_jobs()
        job_role = interview_request.job_role or "Software Engineer"
        if job_role not in available_jobs:
            clean_role = job_role.replace("_", " ").strip()
            matched_role = None
            for aj in available_jobs:
                if aj.lower() == clean_role.lower():
                    matched_role = aj
                    break
            if not matched_role:
                for aj in available_jobs:
                    if aj.lower() in clean_role.lower() or clean_role.lower() in aj.lower():
                        matched_role = aj
                        break
            if not matched_role:
                cl = clean_role.lower()
                if any(k in cl for k in ["python", "java", "backend", "node", "django", "fastapi", "golang", "c++", "c#", ".net", "api"]):
                    matched_role = "Backend Developer"
                elif any(k in cl for k in ["frontend", "react", "vue", "angular", "ui", "web", "css", "html"]):
                    matched_role = "Frontend Developer"
                elif any(k in cl for k in ["data", "analytics", "bi", "sql", "tableau", "power bi"]):
                    matched_role = "Data Scientist"
                elif any(k in cl for k in ["ml", "ai", "machine learning", "deep learning", "nlp", "llm", "computer vision"]):
                    matched_role = "Machine Learning Engineer"
                elif any(k in cl for k in ["devops", "cloud", "aws", "azure", "gcp", "docker", "k8s", "kubernetes", "sre", "ci/cd"]):
                    matched_role = "DevOps Engineer"
                elif any(k in cl for k in ["security", "cyber", "infosec", "soc"]):
                    matched_role = "Cybersecurity Analyst"
                elif any(k in cl for k in ["mobile", "android", "ios", "flutter", "react native", "swift", "kotlin"]):
                    matched_role = "Mobile App Developer"
                elif any(k in cl for k in ["database", "dba", "postgres", "mongodb", "mysql"]):
                    matched_role = "Database Administrator"
                else:
                    matched_role = "Software Engineer"
            job_role = matched_role
        
        # Create session (CPU-bound: question generation + filtering)
        # Exclude questions the candidate has seen in past sessions
        seen_ids = await get_seen_question_ids(interview_request.candidate_id or "")
        session = await run_in_threadpool(
            interview_service.create_interview_session,
            candidate_id=interview_request.candidate_id,
            job_role=job_role,
            num_questions=interview_request.num_questions,
            employer_skills=interview_request.required_skills or None,
            job_level=interview_request.job_level or "Mid-Level",
            exclude_ids=seen_ids,
            mcq_count=interview_request.mcq_count,
            desc_count=interview_request.desc_count,
            coding_count=interview_request.coding_count,
            job_description=interview_request.job_description or "",
        )
        
        # Store time limits from employer config
        session["mcq_time"] = interview_request.mcq_time or 60
        session["desc_time"] = interview_request.desc_time or 300
        session["coding_time"] = interview_request.coding_time or 600
        session["total_time"] = interview_request.total_time or 60
        session["is_practice"] = interview_request.is_practice or False
        session["job_id"] = interview_request.job_id or ""
        session["job_description"] = interview_request.job_description or ""
        
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
            mcq_time=session["mcq_time"],
            desc_time=session["desc_time"],
            coding_time=session["coding_time"],
            total_time=session["total_time"],
            created_at=session["created_at"],
            status=session["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting interview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start interview")


@router.post("/submit", response_model=InterviewScoreResult)
@limiter.limit("5/minute")
async def submit_answers(request: Request, submission: InterviewSubmitRequest, services: Dict = Depends(get_services)):
    """
    Submit answers and get evaluation results
    
    Args:
        submission: Pydantic model with session_id and answers list
        
    Returns:
        Interview score result with grades and weak areas
    """
    try:
        interview_service = services["interview_service"]
        
        session_id = submission.session_id
        session = await get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        # Enrich answer payload with question_type and correctness
        question_map = {
            q["id"]: q for q in session.get("questions", [])
            if q.get("id")
        }
        processed_answers = []

        for answer in submission.answers:
            question_id = answer.get("question_id")
            question = question_map.get(question_id)
            if not question:
                continue

            question_type = question.get("question_type")
            time_taken = answer.get("time_taken_seconds", 0)
            processed_answer = {
                "question_id": question_id,
                "question_type": question_type,
                "question_text": question.get("question_text", ""),
                "topic": question.get("topic", "Unknown"),
                "time_taken_seconds": time_taken,
            }

            if question_type == "MCQ":
                candidate_choice = answer.get("selected_option")
                if candidate_choice is None:
                    candidate_choice = answer.get("answer")
                try:
                    candidate_choice = int(candidate_choice)
                except (TypeError, ValueError):
                    candidate_choice = -1
                correct_choice = question.get("correct_option")
                if correct_choice is None:
                    correct_choice = question.get("correct_answer_index", 0)
                processed_answer["selected_option"] = candidate_choice
                processed_answer["correct_option"] = correct_choice
                processed_answer["is_correct"] = candidate_choice == correct_choice
                processed_answer["options"] = question.get("options", [])

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
                # Stricter quality: penalise gibberish that merely compiles
                meaningful = any(kw in code_text for kw in ['def ', 'class ', 'return', 'import ', 'for ', 'while ', 'if ', 'elif ', 'else:', 'try:', 'with ', 'yield ', 'lambda ', '=', 'print(', 'len(', 'range(', 'return'])
                has_operators = any(op in code_text for op in ['==', '!=', '<=', '>=', '+', '-', '*', '/', '%', '**', '//'])
                has_structure = any(kw in code_text for kw in ['def ', 'class ', 'for ', 'while ', 'if ', 'try:', 'with '])
                quality_score = (
                    0.15 * float(syntax_valid)
                    + 0.10 * float(0 < code_lines < 200)
                    + 0.15 * float(has_return)
                    + 0.20 * float(meaningful)
                    + 0.20 * float(has_operators)
                    + 0.20 * float(has_structure)
                )
                if test_pass_rate is None:
                    # No verifiable test case exists (placeholder/legacy data).
                    # Grade on structure alone; don't punish correct code.
                    code_score = round(quality_score * 100, 2)
                else:
                    # Blend 70% test correctness + 30% code quality (matches CodingEvaluator).
                    code_score = round((0.7 * test_pass_rate + 0.3 * quality_score) * 100, 2)
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
            "candidate_id": submission.get("candidate_id") or session.get("candidate_id", ""),
            "session_id": session_id,
            "job_role": submission.get("job_role") or session.get("job_role", ""),
            "answers": processed_answers
        }
        
        result = await run_in_threadpool(
            interview_service.evaluate_interview,
            session_id=session_id,
            interview_data=evaluation_payload,
        )

        # Attach proctoring data if provided (job interviews only)
        # Enforce: practice interviews NEVER store proctoring data
        proctoring = submission.get("proctoring")
        is_practice = session.get("is_practice", False)
        if is_practice:
            proctoring = None
        elif proctoring and isinstance(proctoring, dict):
            result["proctoring"] = proctoring

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
                "integrity_score": proctoring.get("integrity_score") if proctoring else None,
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
            created_at=result["created_at"],
            integrity_score=proctoring.get("integrity_score") if proctoring else None,
            proctoring=proctoring if proctoring else None,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting answers: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit answers")


@router.post("/code/run")
@limiter.limit("10/minute")
async def run_candidate_code(request: Request, payload: CodeRunRequest):
    """
    Run candidate code against the question's test cases without scoring.
    Uses the exact same sandbox as submit, so what the candidate sees in
    testing is what the scorer checks. Returns outputs, never answers.
    """
    code_text = payload.code_text
    test_cases = payload.test_cases
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


@router.get("/proctoring/{interview_id}")
async def fetch_proctoring_analysis(interview_id: str):
    """
    Get proctoring analysis for an interview result.
    Returns feature vectors + computed non-verbal/speech/confidence analysis.
    """
    try:
        result = await get_result(interview_id)
        if not result:
            raise HTTPException(status_code=404, detail="Interview result not found")
        proctoring = result.get("proctoring")
        if not proctoring:
            raise HTTPException(status_code=404, detail="No proctoring data available (practice interview or legacy session)")
        return {
            "success": True,
            "integrity_score": proctoring.get("integrity_score"),
            "flags": proctoring.get("flags"),
            "timeline": proctoring.get("timeline"),
            "duration_seconds": proctoring.get("duration_seconds"),
            "analysis": proctoring.get("analysis"),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving proctoring analysis: {e}")
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
