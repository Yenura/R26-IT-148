"""Script to simulate candidate job application and interview completion for testing Skill Gap and Progress integration."""
import os
import sys
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://admin:PxUm8dLzq5jqlHYN@coordinator.ljarc.mongodb.net/HR")
DB_NAME = os.getenv("DB_NAME", "HR")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

def test_integration():
    now = datetime.now(timezone.utc)
    
    # 1. Find candidate Alex Chen
    user = db.users.find_one({"email": "alex.chen@gmail.com"})
    if not user:
        print("Candidate Alex Chen not found.")
        return
    candidate_id = str(user["_id"])
    print(f"Testing for Candidate: {user['full_name']} (ID: {candidate_id})")

    # 2. Find Google Software Engineer job
    google_user = db.users.find_one({"email": "careers@google.com"})
    google_job = db.jobs.find_one({"title": "Software Engineer", "company_id": google_user["_id"]})
    if not google_job:
        print("Google Software Engineer job not found.")
        return
    job_id = str(google_job["_id"])
    print(f"Found Job: {google_job['title']} @ Google (ID: {job_id})")

    # 3. Create application in db.applications
    resume = db.resumes.find_one({"candidate_id": candidate_id})
    resume_id = str(resume["_id"]) if resume else ""

    app_doc = {
        "job_id": job_id,
        "candidate_id": candidate_id,
        "candidate_name": user["full_name"],
        "resume_id": resume_id,
        "status": "applied",
        "applied_at": now,
    }
    db.applications.replace_one(
        {"candidate_id": candidate_id, "job_id": job_id},
        app_doc,
        upsert=True
    )
    print("Created application record.")

    # 4. Create Interview evaluation result in db.results with specific strengths & weaknesses (e.g. strong in Python & REST APIs, poor in SQL & Docker)
    session_id = f"INT_{now.strftime('%Y%m%d%H%M%S')}_{candidate_id[:6]}"
    interview_id = f"RES_{now.strftime('%Y%m%d%H%M%S')}_{candidate_id[:6]}"

    result_doc = {
        "interview_id": interview_id,
        "session_id": session_id,
        "candidate_id": candidate_id,
        "job_role": "Software Engineer",
        "overall_score": 68.5,
        "interview_score": 68.5,
        "mcq_score": 60.0,
        "descriptive_score": 65.0,
        "coding_score": 85.0,
        "grade": "Average",
        "mcq_details": [
            {"topic": "Python Core", "is_correct": True, "score": 100},
            {"topic": "SQL Queries", "is_correct": False, "score": 0},
            {"topic": "REST APIs", "is_correct": True, "score": 100},
            {"topic": "SQL Optimization", "is_correct": False, "score": 0},
        ],
        "descriptive_details": [
            {"topic": "REST APIs", "similarity_score": 88.0, "score": 88.0},
            {"topic": "SQL Transactions", "similarity_score": 42.0, "score": 42.0},
        ],
        "coding_details": [
            {"topic": "Python Algorithms", "tests_passed": 3, "total_tests": 3, "score": 100.0},
            {"topic": "SQL Query Design", "tests_passed": 1, "total_tests": 3, "score": 33.3},
        ],
        "weak_topics": ["SQL Queries", "SQL Transactions", "SQL Query Design"],
        "failed_mcq_topics": ["SQL Queries", "SQL Optimization"],
        "created_at": now,
        "completed_at": now,
    }

    db.results.replace_one(
        {"candidate_id": candidate_id, "job_role": "Software Engineer"},
        result_doc,
        upsert=True
    )
    print("Created detailed interview evaluation with Python strength & SQL weakness.")

    # Also update interview_scores collection
    db.interview_scores.replace_one(
        {"candidate_id": candidate_id, "job_id": job_id},
        {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "session_id": session_id,
            "job_role": "Software Engineer",
            "mcq_score": 60.0,
            "descriptive_score": 65.0,
            "coding_score": 85.0,
            "interview_score": 68.5,
            "grade": "Average",
            "created_at": now,
        },
        upsert=True
    )

    print("Test setup completed successfully.")

if __name__ == "__main__":
    test_integration()
