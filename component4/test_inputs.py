import requests

BASE = 'http://localhost:8000/api/v1'
OK  = "[PASS]"
ERR = "[FAIL]"

def test(label, r, expected=200):
    status = OK if r.status_code == expected else ERR
    print(f"  {status}  {label}: HTTP {r.status_code}")
    return r

print("\n=== BACKEND INPUT VALIDATION TESTS ===\n")

# 1 Long candidate name
long_name = "Tharindra Bandara Perera Wickramasinghe"
r = test(f"Long name ({len(long_name)} chars)",
    requests.post(f"{BASE}/skill-gap/analyze", json={
        "candidate_id": "INPUT-TEST-001",
        "candidate_name": long_name,
        "job_role": "Data Scientist",
        "skills": ["Python", "SQL"],
        "experience_years": 3,
        "education": "B.Tech",
        "certifications": "None",
    }))
if r.status_code == 200:
    print(f"       Stored: {r.json()['data']['candidate_name']}")

# 2 Short name (2 chars)
r = test("Short name (2 chars)",
    requests.post(f"{BASE}/skill-gap/analyze", json={
        "candidate_id": "INPUT-TEST-002",
        "candidate_name": "Jo",
        "job_role": "AI Researcher",
        "skills": ["Python", "TensorFlow"],
        "experience_years": 1,
        "education": "B.Sc",
        "certifications": "None",
    }))

# 3 Special chars in name
special_name = "Mary O'Brien St. Claire"
r = test("Special chars in name",
    requests.post(f"{BASE}/skill-gap/analyze", json={
        "candidate_id": "INPUT-TEST-003",
        "candidate_name": special_name,
        "job_role": "Software Engineer",
        "skills": ["Java", "SQL", "C++"],
        "experience_years": 5,
        "education": "M.Tech",
        "certifications": "AWS Certified",
        "cv_matching_score": 88.5,
        "interview_score": 91.0,
    }))
if r.status_code == 200:
    print(f"       Stored: {r.json()['data']['candidate_name']}")

# 4 Score boundaries 0 and 100
r = test("Score boundaries (0 and 100)",
    requests.post(f"{BASE}/skill-gap/analyze", json={
        "candidate_id": "INPUT-TEST-004",
        "candidate_name": "Score Boundary Test",
        "job_role": "Data Scientist",
        "skills": ["Python"],
        "experience_years": 0,
        "education": "B.Sc",
        "certifications": "None",
        "cv_matching_score": 0,
        "interview_score": 100,
        "mcq_score": 0,
        "coding_score": 100,
    }))

# 5 Null/None scores (optional fields)
r = test("Null scores (optional fields)",
    requests.post(f"{BASE}/skill-gap/analyze", json={
        "candidate_id": "INPUT-TEST-005",
        "candidate_name": "Null Score Test",
        "job_role": "Cybersecurity Analyst",
        "skills": ["Cybersecurity", "Linux"],
        "experience_years": 2,
        "education": "B.Tech",
        "certifications": "None",
        "cv_matching_score": None,
        "interview_score": None,
    }))

# 6 All 4 job roles accepted
for role in ["Data Scientist", "AI Researcher", "Software Engineer", "Cybersecurity Analyst"]:
    skill_map = {
        "Data Scientist": ["Python"],
        "AI Researcher": ["TensorFlow"],
        "Software Engineer": ["Java"],
        "Cybersecurity Analyst": ["Linux"],
    }
    r = test(f"Job role: {role}",
        requests.post(f"{BASE}/skill-gap/analyze", json={
            "candidate_id": f"ROLE-{role[:4]}",
            "candidate_name": "Role Test",
            "job_role": role,
            "skills": skill_map[role],
            "experience_years": 2,
            "education": "B.Tech",
            "certifications": "None",
        }))

# 7 Missing candidate_id should 422
r = test("Empty candidate_id (expect 422)",
    requests.post(f"{BASE}/skill-gap/analyze", json={
        "candidate_id": "",
        "candidate_name": "Test",
        "job_role": "Data Scientist",
        "skills": ["Python"],
        "experience_years": 2,
        "education": "B.Tech",
        "certifications": "None",
    }), expected=422)

# 8 Education options
for edu in ["B.Sc", "B.Tech", "MBA", "M.Tech", "PhD"]:
    r = test(f"Education: {edu}",
        requests.post(f"{BASE}/skill-gap/analyze", json={
            "candidate_id": f"EDU-{edu}",
            "candidate_name": "Edu Test",
            "job_role": "Data Scientist",
            "skills": ["Python"],
            "experience_years": 2,
            "education": edu,
            "certifications": "None",
        }))

print("\n=== ALL INPUT TESTS COMPLETE ===\n")
