"""
Component 4 — Full End-to-End Test (New 10K Dataset)
Tests all 10 job roles and new fields: job_level, work_mode, projects_count, certifications_count
"""
import requests, json, sys

BASE = "http://127.0.0.1:8000/api/v1"
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
        print(f"  {ERR}  {label} — {r.status_code}: {r.text[:140]}")
        failed += 1
        return None

# ── 1. Health ─────────────────────────────────────────────────────────────────
print("\n=== HEALTH CHECK ===")
chk("GET /", requests.get("http://127.0.0.1:8000/"))
chk("GET /health", requests.get("http://127.0.0.1:8000/health"))

# ── 2. Roles endpoint ─────────────────────────────────────────────────────────
print("\n=== ROLES ===")
r = requests.get(f"{BASE}/skill-gap/roles")
res = chk("GET /skill-gap/roles", r)
if res:
    print(f"         {res['count']} roles: {res['roles']}")

# ── 3. Add 10 candidates (one per role) ───────────────────────────────────────
print("\n=== ADDING TEST CANDIDATES (10 roles) ===")

CANDIDATES = [
    {
        "candidate_id": "T-001", "candidate_name": "Ashan Perera",
        "job_role": "Software Engineer", "job_level": "Senior", "work_mode": "Hybrid",
        "skills": ["Python", "REST APIs", "Microservices", "Docker"],
        "experience_years": 6, "education": "B.Sc. Computer Science",
        "certifications": "AWS Certified", "certifications_count": 1, "projects_count": 12,
        "cv_matching_score": 78.0, "interview_score": 72.0,
        "mcq_score": 75.0, "descriptive_score": 68.0, "coding_score": 70.0,
        "weak_topics": [], "failed_mcq_topics": [],
    },
    {
        "candidate_id": "T-002", "candidate_name": "Nimali Silva",
        "job_role": "Data Scientist", "job_level": "Mid-Level", "work_mode": "Remote",
        "skills": ["Python", "SQL", "Statistics"],
        "experience_years": 3, "education": "M.Sc. Data Science",
        "certifications": "Coursera ML Specialization", "certifications_count": 1, "projects_count": 7,
        "cv_matching_score": 55.0, "interview_score": 60.0,
        "mcq_score": 65.0, "descriptive_score": 55.0, "coding_score": 45.0,
        "weak_topics": ["Feature Engineering"], "failed_mcq_topics": ["Cross Validation"],
    },
    {
        "candidate_id": "T-003", "candidate_name": "Kasun Fernando",
        "job_role": "Machine Learning Engineer", "job_level": "Senior", "work_mode": "Remote",
        "skills": ["Python", "PyTorch/TensorFlow", "MLOps", "Feature Engineering", "Docker"],
        "experience_years": 7, "education": "M.Sc. Machine Learning",
        "certifications": "Deep Learning Specialization | AWS Certified Data Engineer",
        "certifications_count": 2, "projects_count": 18,
        "cv_matching_score": 90.0, "interview_score": 88.0,
        "mcq_score": 92.0, "descriptive_score": 85.0, "coding_score": 80.0,
        "weak_topics": [], "failed_mcq_topics": [],
    },
    {
        "candidate_id": "T-004", "candidate_name": "Sachini Dias",
        "job_role": "Frontend Developer", "job_level": "Junior", "work_mode": "On-Site",
        "skills": ["React", "TypeScript", "HTML/CSS"],
        "experience_years": 1, "education": "B.Sc. Software Engineering",
        "certifications": "None", "certifications_count": 0, "projects_count": 4,
        "cv_matching_score": 50.0, "interview_score": 48.0,
        "mcq_score": 55.0, "descriptive_score": 42.0, "coding_score": 38.0,
        "weak_topics": ["Web Performance", "Accessibility"], "failed_mcq_topics": ["CSS Grid"],
    },
    {
        "candidate_id": "T-005", "candidate_name": "Ruwan Jayasinghe",
        "job_role": "Backend Developer", "job_level": "Lead", "work_mode": "Hybrid",
        "skills": ["Python", "PostgreSQL", "REST APIs", "Microservices", "Docker", "Kubernetes"],
        "experience_years": 10, "education": "M.Sc. Computer Science",
        "certifications": "AWS Certified Solutions Architect | Google Cloud Professional",
        "certifications_count": 2, "projects_count": 25,
        "cv_matching_score": 95.0, "interview_score": 93.0,
        "mcq_score": 95.0, "descriptive_score": 90.0, "coding_score": 88.0,
        "weak_topics": [], "failed_mcq_topics": [],
    },
    {
        "candidate_id": "T-006", "candidate_name": "Dilhara Rathnayake",
        "job_role": "DevOps Engineer", "job_level": "Mid-Level", "work_mode": "Remote",
        "skills": ["Docker", "Kubernetes", "Terraform", "CI/CD"],
        "experience_years": 4, "education": "B.Sc. Information Technology",
        "certifications": "HashiCorp Terraform Associate", "certifications_count": 1, "projects_count": 9,
        "cv_matching_score": 68.0, "interview_score": 65.0,
        "mcq_score": 70.0, "descriptive_score": 62.0, "coding_score": 55.0,
        "weak_topics": ["Cloud Security"], "failed_mcq_topics": [],
    },
    {
        "candidate_id": "T-007", "candidate_name": "Amara Wickramasinghe",
        "job_role": "Cybersecurity Analyst", "job_level": "Senior", "work_mode": "On-Site",
        "skills": ["Cybersecurity", "Networking", "Incident Response", "Cloud Security", "Linux"],
        "experience_years": 8, "education": "M.Sc. Cybersecurity",
        "certifications": "CISSP | CEH", "certifications_count": 2, "projects_count": 15,
        "cv_matching_score": 92.0, "interview_score": 89.0,
        "mcq_score": 90.0, "descriptive_score": 88.0, "coding_score": 75.0,
        "weak_topics": [], "failed_mcq_topics": [],
    },
    {
        "candidate_id": "T-008", "candidate_name": "Prabath Kumara",
        "job_role": "Cloud Solutions Architect", "job_level": "Principal / Staff", "work_mode": "Remote",
        "skills": ["AWS/Azure/GCP", "Terraform", "Cloud Security", "Architecture Design", "Networking"],
        "experience_years": 14, "education": "M.Sc. Information Systems",
        "certifications": "AWS Solutions Architect Professional | Google Cloud Architect",
        "certifications_count": 3, "projects_count": 30,
        "cv_matching_score": 98.0, "interview_score": 96.0,
        "mcq_score": 98.0, "descriptive_score": 95.0, "coding_score": 85.0,
        "weak_topics": [], "failed_mcq_topics": [],
    },
    {
        "candidate_id": "T-009", "candidate_name": "Tharushi Mallawarachchi",
        "job_role": "Database Administrator", "job_level": "Mid-Level", "work_mode": "Hybrid",
        "skills": ["SQL", "PostgreSQL"],
        "experience_years": 3, "education": "B.Sc. Computer Science",
        "certifications": "None", "certifications_count": 0, "projects_count": 6,
        "cv_matching_score": 52.0, "interview_score": 55.0,
        "mcq_score": 58.0, "descriptive_score": 50.0, "coding_score": 42.0,
        "weak_topics": ["Performance Tuning"], "failed_mcq_topics": ["Query Optimization"],
    },
    {
        "candidate_id": "T-010", "candidate_name": "Chamara Bandara",
        "job_role": "Mobile App Developer", "job_level": "Senior", "work_mode": "Hybrid",
        "skills": ["React Native", "TypeScript", "REST APIs", "Firebase"],
        "experience_years": 6, "education": "B.Sc. Software Engineering",
        "certifications": "Google Associate Android Developer", "certifications_count": 1, "projects_count": 14,
        "cv_matching_score": 80.0, "interview_score": 77.0,
        "mcq_score": 82.0, "descriptive_score": 74.0, "coding_score": 70.0,
        "weak_topics": [], "failed_mcq_topics": [],
    },
]

candidate_ids = []
for c in CANDIDATES:
    r = requests.post(f"{BASE}/skill-gap/analyze", json=c)
    res = chk(f"POST /analyze — {c['candidate_name']} ({c['job_role']})", r)
    if res:
        d = res["data"]
        candidate_ids.append(c["candidate_id"])
        print(f"         Level: {d.get('job_level','?')} | Mode: {d.get('work_mode','?')} | "
              f"Severity: {d['gap_severity']} | Hire: {d['hire_probability']}% | Match: {d['skill_match_pct']}%")
        if d["missing_required"]:
            print(f"         Missing Required: {', '.join(d['missing_required'][:3])}")

# ── 4. Verify reports ─────────────────────────────────────────────────────────
print("\n=== VERIFYING REPORTS ===")
r = requests.get(f"{BASE}/skill-gap/reports")
res = chk("GET /skill-gap/reports", r)
if res:
    print(f"         Total reports in DB: {res['total']}")

for cid in ["T-001", "T-003", "T-007", "T-008"]:
    r = requests.get(f"{BASE}/skill-gap/report/{cid}")
    chk(f"GET /skill-gap/report/{cid}", r)

# ── 5. Career paths ───────────────────────────────────────────────────────────
print("\n=== CAREER PATHS ===")
for cand in CANDIDATES[:4]:
    r = requests.post(f"{BASE}/career/path", json={
        "candidate_id":    cand["candidate_id"],
        "current_role":    cand["job_role"],
        "skills":          cand["skills"],
        "experience_years": cand["experience_years"],
        "job_level":       cand.get("job_level", "Mid-Level"),
    })
    res = chk(f"POST /career/path — {cand['candidate_id']}", r)
    if res:
        d = res["data"]
        print(f"         Level: {d['current_level']} | Next: {d['next_milestones'][0] if d['next_milestones'] else 'Top'}")

# ── 6. Resources for all 10 roles ─────────────────────────────────────────────
print("\n=== RESOURCES (all 10 roles) ===")
roles = [
    "Software Engineer", "Data Scientist", "Machine Learning Engineer",
    "Frontend Developer", "Backend Developer", "DevOps Engineer",
    "Cybersecurity Analyst", "Cloud Solutions Architect",
    "Database Administrator", "Mobile App Developer",
]
for role in roles:
    r = requests.get(f"{BASE}/career/resources/{requests.utils.quote(role)}")
    res = chk(f"GET /career/resources/{role}", r)
    if res:
        print(f"         {len(res['resources'])} resources found")

# ── 7. Progress tracking ──────────────────────────────────────────────────────
print("\n=== PROGRESS TRACKING ===")
prog_updates = [
    {"candidate_id": "T-001", "skill": "Kubernetes",         "status": "in_progress", "notes": "Studying CKA"},
    {"candidate_id": "T-002", "skill": "Feature Engineering", "status": "in_progress", "notes": "Kaggle course"},
    {"candidate_id": "T-002", "skill": "Machine Learning",    "status": "completed",   "notes": "Done"},
    {"candidate_id": "T-004", "skill": "Web Performance",     "status": "not_started", "notes": ""},
    {"candidate_id": "T-005", "skill": "GraphQL",             "status": "completed",   "notes": "Production use"},
    {"candidate_id": "T-009", "skill": "Performance Tuning",  "status": "in_progress", "notes": "Oracle docs"},
]
for p in prog_updates:
    r = requests.post(f"{BASE}/progress/update", json=p)
    chk(f"POST /progress/update — {p['candidate_id']} / {p['skill']}", r)

for cid in ["T-001", "T-002", "T-009"]:
    r = requests.get(f"{BASE}/progress/{cid}")
    res = chk(f"GET /progress/{cid}", r)
    if res:
        s = res["stats"]
        print(f"         {s['completed']} done, {s['in_progress']} in-progress, {s['not_started']} not started | {s['completion_pct']}%")

# ── 8. Analytics ──────────────────────────────────────────────────────────────
print("\n=== ANALYTICS ===")
r = requests.get(f"{BASE}/analytics/summary")
res = chk("GET /analytics/summary", r)
if res:
    d = res["data"]
    print(f"         Total Reports:       {d['total_reports']}")
    print(f"         Gap Severity:        {d['gap_severity']}")
    print(f"         Role Distribution:   {d['role_distribution']}")
    print(f"         Level Distribution:  {d.get('level_distribution', {})}")
    avgs = d["averages"]
    print(f"         Avg Skill Match:     {avgs['skill_match_pct']}%")
    print(f"         Avg Hire Prob:       {avgs['hire_probability']}%")
    print(f"         Avg Projects:        {avgs['projects_count']}")
    print(f"         Avg Certifications:  {avgs['certifications']}")
    print(f"         Top Missing Skills:  {[x['skill'] for x in d['top_missing_skills'][:5]]}")

r = requests.get(f"{BASE}/analytics/leaderboard?limit=5")
res = chk("GET /analytics/leaderboard", r)
if res:
    print("\n         === TOP 5 CANDIDATES ===")
    for i, c in enumerate(res["data"], 1):
        print(f"         #{i} {c['candidate_name']:24s} | {c['job_role']:28s} | {c['hire_probability']}% | Gap: {c['gap_severity']}")

# ── 9. Role insights ──────────────────────────────────────────────────────────
print("\n=== ROLE INSIGHTS ===")
for role in ["Data Scientist", "Cybersecurity Analyst"]:
    r = requests.get(f"{BASE}/analytics/role-insights/{requests.utils.quote(role)}")
    res = chk(f"GET /analytics/role-insights/{role}", r)
    if res and res.get("data"):
        d = res["data"]
        print(f"         {role}: {d['count']} reports | {d['avg_hire_prob']}% hire prob | {d['avg_match']}% skill match")

# ── 10. Summary ───────────────────────────────────────────────────────────────
print(f"\n{'='*55}")
print(f"  RESULTS: {passed} passed  |  {failed} failed")
print(f"  Frontend: http://localhost:5174")
print(f"  API Docs: http://127.0.0.1:8000/docs")
print(f"{'='*55}")
if failed == 0:
    print("  [OK] ALL CHECKS PASSED -- 100% operational!")
else:
    print(f"  [!!] {failed} endpoint(s) need attention.")
    sys.exit(1)
