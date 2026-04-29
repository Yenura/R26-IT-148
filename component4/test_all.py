"""
Component 4 — Full End-to-End Test Script
Adds 5 sample candidates and verifies all API endpoints.
"""
import requests, json, sys

BASE = "http://localhost:8004/api/v1"
OK   = "\033[92m[PASS]\033[0m"
ERR  = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"

passed = 0
failed = 0

def chk(label, r):
    global passed, failed
    if r.status_code in (200, 201):
        print(f"  {OK}  {label} — {r.status_code}")
        passed += 1
        return r.json()
    else:
        print(f"  {ERR}  {label} — {r.status_code}: {r.text[:120]}")
        failed += 1
        return None

# ── 1. Health check ───────────────────────────────────────────────────────────
print("\n=== HEALTH CHECK ===")
r = requests.get("http://localhost:8004/health")
chk("GET /health", r)

# ── 2. Add 5 candidates ───────────────────────────────────────────────────────
print("\n=== ADDING TEST CANDIDATES ===")

CANDIDATES = [
    {
        "candidate_id": "TEST-001",
        "candidate_name": "Tharindra Perera",
        "job_role": "Data Scientist",
        "skills": ["Python", "SQL"],
        "experience_years": 2,
        "education": "B.Tech",
        "certifications": "None",
        "cv_matching_score": 50.0,
        "interview_score": 55.0,
        "mcq_score": 60.0,
        "descriptive_score": 50.0,
        "coding_score": 35.0,
        "weak_topics": ["Model Evaluation", "Feature Engineering"],
        "failed_mcq_topics": ["Cross Validation", "Decision Trees"],
    },
    {
        "candidate_id": "TEST-002",
        "candidate_name": "Kasun Silva",
        "job_role": "AI Researcher",
        "skills": ["Python", "TensorFlow", "NLP", "Pytorch"],
        "experience_years": 5,
        "education": "M.Tech",
        "certifications": "AWS Certified",
        "cv_matching_score": 85.0,
        "interview_score": 88.0,
        "mcq_score": 90.0,
        "descriptive_score": 82.0,
        "coding_score": 75.0,
        "weak_topics": [],
        "failed_mcq_topics": [],
    },
    {
        "candidate_id": "TEST-003",
        "candidate_name": "Nimali Fernando",
        "job_role": "Software Engineer",
        "skills": ["Java", "React"],
        "experience_years": 3,
        "education": "B.Sc",
        "certifications": "Google ML",
        "cv_matching_score": 60.0,
        "interview_score": 62.0,
        "mcq_score": 70.0,
        "descriptive_score": 58.0,
        "coding_score": 45.0,
        "weak_topics": ["System Design"],
        "failed_mcq_topics": ["Data Structures"],
    },
    {
        "candidate_id": "TEST-004",
        "candidate_name": "Amara Dissanayake",
        "job_role": "Cybersecurity Analyst",
        "skills": ["Cybersecurity", "Networking", "Linux", "Ethical Hacking"],
        "experience_years": 7,
        "education": "M.Tech",
        "certifications": "AWS Certified",
        "cv_matching_score": 95.0,
        "interview_score": 91.0,
        "mcq_score": 95.0,
        "descriptive_score": 88.0,
        "coding_score": 80.0,
        "weak_topics": [],
        "failed_mcq_topics": [],
    },
    {
        "candidate_id": "TEST-005",
        "candidate_name": "Ruwan Jayasinghe",
        "job_role": "Data Scientist",
        "skills": ["Python", "Machine Learning", "Deep Learning", "SQL"],
        "experience_years": 4,
        "education": "PhD",
        "certifications": "Deep Learning Specialization",
        "cv_matching_score": 78.0,
        "interview_score": 72.0,
        "mcq_score": 75.0,
        "descriptive_score": 70.0,
        "coding_score": 65.0,
        "weak_topics": ["NLP Applications"],
        "failed_mcq_topics": [],
    },
]

for c in CANDIDATES:
    r = requests.post(f"{BASE}/skill-gap/analyze", json=c)
    res = chk(f"POST /analyze — {c['candidate_name']}", r)
    if res:
        d = res["data"]
        print(f"         Role: {d['job_role']} | Severity: {d['gap_severity']} | "
              f"Hire Prob: {d['hire_probability']}% | Match: {d['skill_match_pct']}%")
        if d["missing_required"]:
            print(f"         Missing Required: {', '.join(d['missing_required'])}")
        if d["improvement_suggestions"]:
            print(f"         Suggestion 1: {d['improvement_suggestions'][0][:70]}")

# ── 3. Verify reports ─────────────────────────────────────────────────────────
print("\n=== VERIFYING REPORTS ===")
r = requests.get(f"{BASE}/skill-gap/reports")
res = chk("GET /skill-gap/reports", r)
if res:
    print(f"         Total reports in DB: {res['total']}")

for cid in ["TEST-001", "TEST-002", "TEST-003"]:
    r = requests.get(f"{BASE}/skill-gap/report/{cid}")
    chk(f"GET /skill-gap/report/{cid}", r)

# ── 4. Career path ────────────────────────────────────────────────────────────
print("\n=== CAREER PATH ===")
career_payloads = [
    {"candidate_id": "TEST-001", "current_role": "Data Scientist",
     "skills": ["Python", "SQL"], "experience_years": 2},
    {"candidate_id": "TEST-002", "current_role": "AI Researcher",
     "skills": ["Python", "TensorFlow", "NLP", "Pytorch"], "experience_years": 5},
    {"candidate_id": "TEST-004", "current_role": "Cybersecurity Analyst",
     "skills": ["Cybersecurity", "Networking", "Linux", "Ethical Hacking"], "experience_years": 7},
]
for cp in career_payloads:
    r = requests.post(f"{BASE}/career/path", json=cp)
    res = chk(f"POST /career/path — {cp['candidate_id']}", r)
    if res:
        d = res["data"]
        print(f"         Level: {d['current_level']} | Next: {d['next_milestones'][0] if d['next_milestones'] else 'Top'}")

# ── 5. Resources ──────────────────────────────────────────────────────────────
print("\n=== ROLE RESOURCES ===")
for role in ["Data Scientist", "AI Researcher", "Software Engineer", "Cybersecurity Analyst"]:
    r = requests.get(f"{BASE}/career/resources/{requests.utils.quote(role)}")
    res = chk(f"GET /career/resources/{role}", r)
    if res:
        print(f"         {len(res['resources'])} resources found")

# ── 6. Progress tracking ──────────────────────────────────────────────────────
print("\n=== PROGRESS TRACKING ===")
prog_updates = [
    {"candidate_id": "TEST-001", "skill": "Machine Learning", "status": "in_progress", "notes": "Taking Coursera"},
    {"candidate_id": "TEST-001", "skill": "Deep Learning",    "status": "not_started", "notes": ""},
    {"candidate_id": "TEST-001", "skill": "Python",           "status": "completed",   "notes": "Already know"},
    {"candidate_id": "TEST-002", "skill": "TensorFlow",       "status": "completed",   "notes": "Expert level"},
    {"candidate_id": "TEST-003", "skill": "SQL",              "status": "in_progress", "notes": "Practicing"},
    {"candidate_id": "TEST-005", "skill": "NLP",              "status": "in_progress", "notes": "Reading papers"},
]
for p in prog_updates:
    r = requests.post(f"{BASE}/progress/update", json=p)
    chk(f"POST /progress/update — {p['candidate_id']} / {p['skill']}", r)

for cid in ["TEST-001", "TEST-002"]:
    r = requests.get(f"{BASE}/progress/{cid}")
    res = chk(f"GET /progress/{cid}", r)
    if res:
        s = res["stats"]
        print(f"         Stats: {s['completed']} done, {s['in_progress']} in-progress, {s['not_started']} not started | {s['completion_pct']}% complete")

# ── 7. Analytics ──────────────────────────────────────────────────────────────
print("\n=== ANALYTICS ===")
r = requests.get(f"{BASE}/analytics/summary")
res = chk("GET /analytics/summary", r)
if res:
    d = res["data"]
    print(f"         Total Reports:    {d['total_reports']}")
    print(f"         Gap Severity:     {d['gap_severity']}")
    print(f"         Role Dist:        {d['role_distribution']}")
    avgs = d["averages"]
    print(f"         Avg Skill Match:  {avgs['skill_match_pct']}%")
    print(f"         Avg Hire Prob:    {avgs['hire_probability']}%")
    print(f"         Top Missing:      {[x['skill'] for x in d['top_missing_skills'][:4]]}")

r = requests.get(f"{BASE}/analytics/leaderboard?limit=5")
res = chk("GET /analytics/leaderboard", r)
if res:
    print("\n         === LEADERBOARD TOP 5 ===")
    for i, c in enumerate(res["data"], 1):
        print(f"         #{i} {c['candidate_name']:22s} | {c['job_role']:25s} | {c['hire_probability']}% | Gap: {c['gap_severity']}")

# ── 8. Summary ────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"  RESULTS: {passed} passed  |  {failed} failed")
print(f"  Frontend: http://localhost:5174")
print(f"  API Docs: http://localhost:8004/docs")
print(f"{'='*50}")
if failed == 0:
    print("  ALL CHECKS PASSED!")
else:
    print(f"  {failed} endpoint(s) need attention.")
    sys.exit(1)
