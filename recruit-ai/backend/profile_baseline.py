import time
import json
import urllib.request
import urllib.error
import sys

def benchmark_endpoint(name, url, method="GET", data=None, headers=None, iterations=3):
    headers = headers or {}
    if data and isinstance(data, dict):
        data_bytes = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif data and isinstance(data, bytes):
        data_bytes = data
    else:
        data_bytes = None

    durations = []
    status_code = None
    res_bytes = 0

    for _ in range(iterations):
        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=12) as resp:
                status_code = resp.getcode()
                body = resp.read()
                res_bytes = len(body)
            t1 = time.perf_counter()
            durations.append((t1 - t0) * 1000.0)
        except Exception as e:
            t1 = time.perf_counter()
            durations.append((t1 - t0) * 1000.0)
            status_code = f"ERR: {e}"

    avg_ms = sum(durations) / len(durations) if durations else 0
    min_ms = min(durations) if durations else 0
    max_ms = max(durations) if durations else 0
    return {
        "name": name,
        "url": url,
        "status": status_code,
        "avg_ms": round(avg_ms, 2),
        "min_ms": round(min_ms, 2),
        "max_ms": round(max_ms, 2),
        "payload_bytes": res_bytes
    }

def main():
    print("=" * 70, flush=True)
    print("RECRUITAI PERFORMANCE PROFILING — BASELINE AUDIT", flush=True)
    print("=" * 70, flush=True)

    # 1. Microservice Health Latency
    services = [
        ("C0 Unified Backend", "http://127.0.0.1:8000/health"),
        ("C1 Resume Parser", "http://127.0.0.1:8001/health"),
        ("C2 Tech Interview", "http://127.0.0.1:8002/health"),
        ("C3 LTR Ranker", "http://127.0.0.1:8003/health"),
        ("C4 Skill Gap / Analytics", "http://127.0.0.1:8004/health"),
        ("Frontend Dev Server", "http://localhost:5174"),
    ]

    print("\n[1] Health & Connectivity Latencies:", flush=True)
    for name, url in services:
        r = benchmark_endpoint(name, url, iterations=3)
        print(f"  - {r['name']:<26} {r['avg_ms']:>7.2f} ms  (min: {r['min_ms']:>6.2f} ms, status: {r['status']})", flush=True)

    # 2. Component 4 APIs
    print("\n[2] Component 4 API Benchmarks:", flush=True)
    c4_tests = [
        ("C4 Roles Listing", "http://127.0.0.1:8004/api/v1/skill-gap/roles", "GET", None),
        ("C4 Career Roles", "http://127.0.0.1:8004/api/v1/career/roles", "GET", None),
        ("C4 Skill Gap Analysis", "http://127.0.0.1:8004/api/v1/skill-gap", "POST", {
            "current_skills": ["Python", "FastAPI", "Docker", "SQL", "Git", "React"],
            "target_role": "Full Stack Developer",
            "experience_years": 3,
            "education": "B.Sc. Computer Science"
        }),
        ("C4 Career Recommendation", "http://127.0.0.1:8004/api/v1/career/recommendation", "POST", {
            "current_skills": ["Python", "Pandas", "SQL", "Scikit-Learn"],
            "current_role": "Data Scientist"
        }),
        ("C4 Learning Path", "http://127.0.0.1:8004/api/v1/career/learning-path", "POST", {
            "current_skills": ["Python", "SQL"],
            "target_role": "Machine Learning Engineer"
        }),
        ("C4 Leaderboard (50)", "http://127.0.0.1:8004/api/v1/analytics/leaderboard?limit=50", "GET", None),
    ]

    for name, url, method, data in c4_tests:
        r = benchmark_endpoint(name, url, method=method, data=data, iterations=3)
        print(f"  - {r['name']:<28} {r['avg_ms']:>7.2f} ms  (payload: {r['payload_bytes']} bytes, status: {r['status']})", flush=True)

    # 3. Component 3 APIs
    print("\n[3] Component 3 API Benchmarks:", flush=True)
    c3_tests = [
        ("C3 Target Roles", "http://127.0.0.1:8003/api/v1/rank/jobs", "GET", None),
        ("C3 CSS & LTR Ranking", "http://127.0.0.1:8003/api/v1/rank/compute", "POST", {
            "job_role": "Software_Engineer",
            "candidates": [
                {
                    "candidate_id": f"cand_{i}",
                    "candidate_name": f"Candidate {i}",
                    "s_edu": 85.0,
                    "s_exp": 70.0,
                    "s_skill": 90.0,
                    "p_mcq": 80.0,
                    "p_desc": 75.0,
                    "p_code": 85.0,
                    "experience_years": 3.5,
                    "education_level": "BSc",
                    "skills": ["Python", "SQL", "Docker", "Git"]
                }
                for i in range(10)
            ]
        })
    ]

    for name, url, method, data in c3_tests:
        r = benchmark_endpoint(name, url, method=method, data=data, iterations=3)
        print(f"  - {r['name']:<28} {r['avg_ms']:>7.2f} ms  (payload: {r['payload_bytes']} bytes, status: {r['status']})", flush=True)

    # 4. Component 2 APIs
    print("\n[4] Component 2 API Benchmarks:", flush=True)
    c2_tests = [
        ("C2 Available Roles", "http://127.0.0.1:8002/api/v1/interview/jobs", "GET", None),
    ]

    for name, url, method, data in c2_tests:
        r = benchmark_endpoint(name, url, method=method, data=data, iterations=3)
        print(f"  - {r['name']:<28} {r['avg_ms']:>7.2f} ms  (payload: {r['payload_bytes']} bytes, status: {r['status']})", flush=True)

    # 5. Component 0 APIs
    print("\n[5] Component 0 API Benchmarks:", flush=True)
    c0_tests = [
        ("C0 Jobs Listing (/jobs/all)", "http://127.0.0.1:8000/api/v1/jobs/all", "GET", None),
    ]

    for name, url, method, data in c0_tests:
        r = benchmark_endpoint(name, url, method=method, data=data, iterations=3)
        print(f"  - {r['name']:<28} {r['avg_ms']:>7.2f} ms  (payload: {r['payload_bytes']} bytes, status: {r['status']})", flush=True)

    print("\n" + "=" * 70, flush=True)

if __name__ == "__main__":
    main()
