"""Test the backend API endpoint directly (simulating the HTTP call)."""
import sys, os, json
os.environ["ENABLE_QG_MODEL"] = "true"
sys.path.insert(0, ".")

from services.ml_engine import get_interview_service
from db import save_session

svc = get_interview_service("../models")
print(f"Jobs: {len(svc.get_available_jobs())}")
print(f"Bank: {len(svc.question_bank) if svc.question_bank else 0}")

# Simulate what the start endpoint does
session = svc.create_interview_session(
    candidate_id="test001",
    job_role="Software Engineer",
    num_questions=3,
    employer_skills=["Java", "Python"],
)
print(f"Session: {session['session_id']}")
questions = session.get("questions", [])
print(f"Questions: {len(questions)}")
for q in questions:
    print(f"  [{q['question_type']:12s}] {q['question_text'][:80]}")
    # Check that all required fields exist for the schema
    print(f"    id={q.get('id')} seq={q.get('sequence')} diff={q.get('difficulty')}")
    print(f"    options={len(q.get('options', [])) if q.get('options') else 0}")
    print(f"    test_cases={len(q.get('test_cases', [])) if q.get('test_cases') else 0}")
