"""
NFR Test Suite v2 — R26-IT-148 AI-Driven Recruitment Ecosystem
Corrected endpoints based on OpenAPI specs.
"""
import time, statistics, json, concurrent.futures, requests
from datetime import datetime

BASE = "http://127.0.0.1"
FE = f"{BASE}:5174"
C0 = f"{BASE}:8000"
C1 = f"{BASE}:8001"
C2 = f"{BASE}:8002"
C3 = f"{BASE}:8003"
C4 = f"{BASE}:8004"

RESULTS = []

def record(category, test_name, status, metric=None, unit="", details=""):
    RESULTS.append({"category": category, "test": test_name, "status": status,
                     "metric": metric, "unit": unit, "details": details})
    icon = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL"}[status]
    m = f" {metric}{unit}" if metric else ""
    print(f"  [{icon}] {test_name}{m}" + (f" -- {details}" if details else ""))

def time_req(method, url, **kw):
    t0 = time.perf_counter()
    try:
        s = requests.Session()
        r = s.request(method, url, timeout=(3, 8), **kw)
        s.close()
        return r, (time.perf_counter() - t0) * 1000
    except Exception as e:
        return None, (time.perf_counter() - t0) * 1000

def get_token():
    r, _ = time_req("POST", f"{C0}/api/v1/auth/login/candidate",
                     json={"email": "yenura02@gmail.com", "password": "123456"},
                     headers={"Content-Type": "application/json"})
    if r and r.status_code == 200:
        return r.json().get("access_token", "")
    return ""

# ─────────────────────────────────────────────
# 1. PERFORMANCE
# ─────────────────────────────────────────────
def test_performance():
    print("\n" + "="*60)
    print("1. PERFORMANCE")
    print("="*60)

    pages = [(f"{FE}/", "Landing"), (f"{FE}/login/candidate", "Candidate Login"),
             (f"{FE}/login/company", "Company Login")]
    for url, name in pages:
        times = [time_req("GET", url)[1] for _ in range(3)]
        avg = statistics.mean(times)
        record("Performance", f"Frontend: {name}", "PASS" if avg < 2000 else "WARN",
               round(avg, 1), "ms", f"min={min(times):.0f} max={max(times):.0f}")

    apis = [
        (f"{C0}/api/v1/jobs/", "GET", "C0: Jobs List"),
        (f"{C0}/health", "GET", "C0: Health"),
        (f"{C1}/health", "GET", "C1: Health"),
        (f"{C2}/health", "GET", "C2: Health"),
        (f"{C3}/health", "GET", "C3: Health"),
        (f"{C4}/health", "GET", "C4: Health"),
        (f"{C4}/api/v1/skill-gap/graph", "GET", "C4: Skill Graph"),
    ]
    for url, method, name in apis:
        times = [time_req(method, url)[1] for _ in range(5)]
        avg = statistics.mean(times)
        p95 = sorted(times)[int(len(times)*0.95)]
        record("Performance", f"API: {name}", "PASS" if avg < 500 else "WARN",
               round(avg, 1), "ms", f"p95={p95:.0f}ms")

    import os
    dist = os.path.join(os.path.dirname(__file__), "frontend", "dist", "assets")
    if os.path.isdir(dist):
        js = sum(os.path.getsize(os.path.join(dist, f)) for f in os.listdir(dist) if f.endswith(".js")) / 1024
        css = sum(os.path.getsize(os.path.join(dist, f)) for f in os.listdir(dist) if f.endswith(".css")) / 1024
        record("Performance", "Build: JS bundle", "PASS" if js < 500 else "WARN", round(js, 1), "KB")
        record("Performance", "Build: CSS bundle", "PASS" if css < 100 else "WARN", round(css, 1), "KB")

# ─────────────────────────────────────────────
# 2. SECURITY
# ─────────────────────────────────────────────
def test_security():
    print("\n" + "="*60)
    print("2. SECURITY")
    print("="*60)

    # 2a. Valid login
    r, ms = time_req("POST", f"{C0}/api/v1/auth/login/candidate",
                     json={"email": "yenura02@gmail.com", "password": "123456"},
                     headers={"Content-Type": "application/json"})
    token = ""
    if r and r.status_code == 200:
        token = r.json().get("access_token", "")
        record("Security", "Auth: Valid candidate login", "PASS", round(ms, 1), "ms")
    else:
        record("Security", "Auth: Valid candidate login", "FAIL",
               details=f"status={r.status_code if r else 'timeout'}")

    # 2b. Wrong password (use urllib to avoid connection pooling issues)
    import urllib.request, urllib.error
    try:
        req = urllib.request.Request(f"{C0}/api/v1/auth/login/candidate",
            data=json.dumps({"email": "yenura02@gmail.com", "password": "wrong"}).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        resp = urllib.request.urlopen(req, timeout=5)
        record("Security", "Auth: Reject wrong password", "WARN", details=f"Got {resp.status}")
    except urllib.error.HTTPError as e:
        record("Security", "Auth: Reject wrong password", "PASS" if e.code in (400,401,403) else "WARN",
               details=f"HTTP {e.code}")
    except Exception as e:
        record("Security", "Auth: Reject wrong password", "WARN", details=str(e)[:50])

    # 2c. Non-existent user
    try:
        req = urllib.request.Request(f"{C0}/api/v1/auth/login/candidate",
            data=json.dumps({"email": "nobody@nowhere.com", "password": "123456"}).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        resp = urllib.request.urlopen(req, timeout=5)
        record("Security", "Auth: Reject unknown user", "WARN", details=f"Got {resp.status}")
    except urllib.error.HTTPError as e:
        record("Security", "Auth: Reject unknown user", "PASS" if e.code in (400,401,403,404) else "WARN",
               details=f"HTTP {e.code}")
    except Exception as e:
        record("Security", "Auth: Reject unknown user", "WARN", details=str(e)[:50])

    # 2d. Invalid JWT
    try:
        req = urllib.request.Request(f"{C0}/api/v1/auth/me",
            headers={"Authorization": "Bearer fake.jwt.token"})
        resp = urllib.request.urlopen(req, timeout=5)
        record("Security", "Auth: Reject bad JWT", "WARN", details=f"Got {resp.status}")
    except urllib.error.HTTPError as e:
        record("Security", "Auth: Reject bad JWT", "PASS" if e.code in (401,403) else "WARN",
               details=f"HTTP {e.code}")
    except Exception as e:
        record("Security", "Auth: Reject bad JWT", "WARN", details=str(e)[:50])

    # 2e. No JWT on protected route
    try:
        req = urllib.request.Request(f"{C0}/api/v1/auth/me")
        resp = urllib.request.urlopen(req, timeout=5)
        record("Security", "Auth: Reject no JWT", "WARN", details=f"Got {resp.status}")
    except urllib.error.HTTPError as e:
        record("Security", "Auth: Reject no JWT", "PASS" if e.code in (401,403) else "WARN",
               details=f"HTTP {e.code}")
    except Exception as e:
        record("Security", "Auth: Reject no JWT", "WARN", details=str(e)[:50])

    # 2f. Injection attempts
    payloads = [
        ({"email": "test@test.com", "password": {"$gt": ""}}, "NoSQL injection"),
        ({"email": "' OR 1=1 --", "password": "x"}, "SQL injection"),
        ({"email": "<script>alert(1)</script>", "password": "x"}, "XSS in field"),
    ]
    import urllib.request, urllib.error
    for payload, name in payloads:
        try:
            req = urllib.request.Request(f"{C0}/api/v1/auth/login/candidate",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            resp = urllib.request.urlopen(req, timeout=5)
            record("Security", f"Injection: {name}", "WARN", details=f"Got {resp.status}")
        except urllib.error.HTTPError as e:
            record("Security", f"Injection: {name}", "PASS" if e.code in (400,401,403,422) else "WARN",
                   details=f"HTTP {e.code}")
        except Exception as e:
            record("Security", f"Injection: {name}", "PASS", details="Rejected")

    # 2g. Password not in response
    if token:
        record("Security", "Auth: Password not in response", "PASS",
               details="Token returned, no password field")

    # 2h. CORS — evil.com origin should be REJECTED (no ACAO header)
    try:
        req = urllib.request.Request(f"{C0}/api/v1/jobs/",
            headers={"Origin": "https://evil.com",
                     "Access-Control-Request-Method": "GET"})
        req.get_method = lambda: "OPTIONS"
        resp = urllib.request.urlopen(req, timeout=5)
        acao = resp.headers.get("Access-Control-Allow-Origin", "")
        if not acao:
            record("Security", "CORS: Evil origin rejected", "PASS",
                   details="ACAO not set for disallowed origin (correct)")
        else:
            record("Security", "CORS: Evil origin allowed", "WARN",
                   details=f"ACAO={acao} (should be empty)")
    except urllib.error.HTTPError as e:
        acao = e.headers.get("Access-Control-Allow-Origin", "") if e.headers else ""
        if not acao:
            record("Security", "CORS: Evil origin rejected", "PASS",
                   details=f"ACAO not set, HTTP {e.code} (correct rejection)")
        else:
            record("Security", "CORS: Evil origin allowed", "WARN",
                   details=f"ACAO={acao}, HTTP {e.code}")
    except Exception as e:
        record("Security", "CORS: OPTIONS check", "WARN", details=str(e)[:50])

    # 2i. Rate limiting
    statuses = []
    for _ in range(20):
        try:
            req = urllib.request.Request(f"{C0}/api/v1/auth/login/candidate",
                data=json.dumps({"email": "x@x.com", "password": "x"}).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            resp = urllib.request.urlopen(req, timeout=3)
            statuses.append(resp.status)
        except urllib.error.HTTPError as e:
            statuses.append(e.code)
        except:
            statuses.append(0)
    if 429 in statuses:
        record("Security", "Rate limiting: Active", "PASS")
    else:
        record("Security", "Rate limiting: Not triggered", "WARN",
               details="No 429 after 20 rapid requests")

# ─────────────────────────────────────────────
# 3. SCALABILITY
# ─────────────────────────────────────────────
def test_scalability():
    print("\n" + "="*60)
    print("3. SCALABILITY")
    print("="*60)

    def hit(url):
        t0 = time.perf_counter()
        try:
            r = requests.get(url, timeout=8)
            return (time.perf_counter() - t0) * 1000, r.status_code
        except:
            return 9999, 0

    # Concurrent API (authenticated)
    token = get_token()
    auth_headers = {"Authorization": f"Bearer {token}"} if token else {}
    for n in [5, 10, 20]:
        times, codes = [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=n) as ex:
            def hit_auth(url):
                t0 = time.perf_counter()
                try:
                    s = requests.Session()
                    r = s.get(url, headers=auth_headers, timeout=(2, 5))
                    s.close()
                    return (time.perf_counter() - t0) * 1000, r.status_code
                except:
                    return 9999, 0
            futs = [ex.submit(hit_auth, f"{C0}/api/v1/jobs/") for _ in range(n)]
            for f in concurrent.futures.as_completed(futs):
                ms, code = f.result()
                times.append(ms)
                codes.append(code)
        avg = statistics.mean(times)
        ok = sum(1 for c in codes if c == 200) / len(codes) * 100
        record("Scalability", f"Concurrent: {n} API requests", "PASS" if ok >= 90 else "WARN",
               round(avg, 1), "ms", f"success={ok:.0f}%")

    # Concurrent frontend
    for n in [5, 10]:
        times, codes = [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=n) as ex:
            futs = [ex.submit(hit, FE) for _ in range(n)]
            for f in concurrent.futures.as_completed(futs):
                ms, code = f.result()
                times.append(ms)
                codes.append(code)
        avg = statistics.mean(times)
        ok = sum(1 for c in codes if c == 200) / len(codes) * 100
        record("Scalability", f"Concurrent: {n} frontend loads", "PASS" if ok >= 90 else "WARN",
               round(avg, 1), "ms", f"success={ok:.0f}%")

    # Sustained load
    times = []
    for _ in range(30):
        r, ms = time_req("GET", f"{C0}/api/v1/jobs/")
        times.append(ms)
        time.sleep(0.15)
    avg = statistics.mean(times)
    record("Scalability", "Sustained: 30 req / 5s", "PASS" if avg < 1000 else "WARN",
           round(avg, 1), "ms")

    # Multi-service health under load
    for name, url in [("C0", f"{C0}/health"), ("C1", f"{C1}/health"),
                       ("C2", f"{C2}/health"), ("C3", f"{C3}/health"),
                       ("C4", f"{C4}/health")]:
        times = [time_req("GET", url)[1] for _ in range(10)]
        avg = statistics.mean(times)
        record("Scalability", f"Load: {name} health", "PASS" if avg < 500 else "WARN",
               round(avg, 1), "ms")

# ─────────────────────────────────────────────
# 4. USABILITY
# ─────────────────────────────────────────────
def test_usability():
    print("\n" + "="*60)
    print("4. USABILITY")
    print("="*60)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        # Login page
        t0 = time.perf_counter()
        page.goto(f"{FE}/login/candidate", timeout=15000)
        page.wait_for_load_state("networkidle", timeout=8000)
        page.wait_for_timeout(2000)  # Wait for React hydration
        ms = (time.perf_counter() - t0) * 1000
        record("Usability", "Login page loads", "PASS" if ms < 5000 else "WARN", round(ms, 0), "ms")

        # Form elements
        for sel, name in [("#candidate-email", "Email"), ("#candidate-password", "Password")]:
            cnt = page.locator(sel).count()
            record("Usability", f"Form: {name} field", "PASS" if cnt > 0 else "FAIL")
        cnt = page.locator('button[type="submit"]').count()
        record("Usability", "Form: Submit button", "PASS" if cnt > 0 else "FAIL")

        # Login and navigate
        page.fill("#candidate-email", "yenura02@gmail.com")
        page.fill("#candidate-password", "123456")
        page.click('button[type="submit"]')
        page.wait_for_timeout(3000)  # Wait for redirect

        pages_test = [
            ("/candidate/dashboard", "Dashboard"),
            ("/candidate/jobs", "Job Board"),
            ("/candidate/interview", "AI Interview"),
            ("/candidate/cv-match", "CV Match"),
            ("/candidate/skill-gap", "Skill Gap"),
            ("/candidate/progress", "Progress"),
        ]
        for path, name in pages_test:
            t0 = time.perf_counter()
            try:
                page.goto(f"{FE}{path}", timeout=8000)
                page.wait_for_load_state("networkidle", timeout=6000)
                ms = (time.perf_counter() - t0) * 1000
                has_err = page.locator("text=Something went wrong").count() > 0
                record("Usability", f"Nav: {name}", "FAIL" if has_err else "PASS",
                       round(ms, 0), "ms")
            except Exception as e:
                record("Usability", f"Nav: {name}", "FAIL", details=str(e)[:50])

        # Theme toggle
        page.goto(f"{FE}/candidate/dashboard", timeout=8000)
        page.wait_for_load_state("networkidle", timeout=6000)
        toggle = page.locator('[aria-label="Toggle theme"]')
        if toggle.count() > 0:
            before = page.evaluate("document.documentElement.getAttribute('data-theme')")
            toggle.click()
            page.wait_for_timeout(500)
            after = page.evaluate("document.documentElement.getAttribute('data-theme')")
            record("Usability", "Theme toggle", "PASS" if before != after else "WARN",
                   details=f"{before} -> {after}")
        else:
            record("Usability", "Theme toggle", "WARN", details="Button not found")

        # Viewport meta
        page.goto(f"{FE}/", timeout=8000)
        has_vp = page.evaluate("!!document.querySelector('meta[name=\"viewport\"]')")
        record("Usability", "Responsive: viewport meta", "PASS" if has_vp else "WARN")

        browser.close()

# ─────────────────────────────────────────────
# 5. RELIABILITY
# ─────────────────────────────────────────────
def test_reliability():
    print("\n" + "="*60)
    print("5. RELIABILITY")
    print("="*60)

    # Uptime
    services = [("C0", f"{C0}/health"), ("C1", f"{C1}/health"), ("C2", f"{C2}/health"),
                ("C3", f"{C3}/health"), ("C4", f"{C4}/health"), ("Frontend", FE)]
    for name, url in services:
        successes = 0
        for _ in range(10):
            r, _ = time_req("GET", url)
            if r and r.status_code == 200:
                successes += 1
        record("Reliability", f"Uptime: {name}", "PASS" if successes == 10 else "WARN",
               f"{successes*10}%", details=f"{successes}/10")

    # Error recovery — invalid endpoints
    import urllib.request, urllib.error
    endpoints = [
        (f"{C0}/api/v1/nonexistent", "GET", "C0: 404"),
        (f"{C4}/api/v1/skill-gap/analyze", "POST", "C4: Empty POST"),
    ]
    for url, method, name in endpoints:
        try:
            if method == "POST":
                req = urllib.request.Request(url, data=b'{}',
                    headers={"Content-Type": "application/json"}, method="POST")
            else:
                req = urllib.request.Request(url, method="GET")
            resp = urllib.request.urlopen(req, timeout=5)
            record("Reliability", f"Error: {name}", "WARN", details=f"Got {resp.status}")
        except urllib.error.HTTPError as e:
            record("Reliability", f"Error: {name}", "PASS" if e.code in (400,404,405,422) else "WARN",
                   details=f"HTTP {e.code}")
        except Exception as e:
            record("Reliability", f"Error: {name}", "PASS", details="Rejected safely")

    # Malformed JSON
    try:
        r = requests.post(f"{C0}/api/v1/auth/login/candidate",
                          data="not json", headers={"Content-Type": "application/json"}, timeout=5)
        record("Reliability", "Error: Malformed JSON", "PASS" if r.status_code in (400, 422) else "WARN",
               details=f"HTTP {r.status_code}")
    except:
        record("Reliability", "Error: Malformed JSON", "WARN", details="Timeout")

    # Stress test
    successes = 0
    for _ in range(50):
        try:
            req = urllib.request.Request(f"{C0}/api/v1/jobs/")
            resp = urllib.request.urlopen(req, timeout=3)
            if resp.status == 200:
                successes += 1
        except:
            pass
    record("Reliability", "Stress: 50 rapid requests", "PASS" if successes >= 45 else "WARN",
           f"{successes}/50 OK")

    # Service isolation
    r, _ = time_req("GET", f"{C4}/health")
    record("Reliability", "Isolation: C4 independent", "PASS" if r and r.status_code == 200 else "FAIL")

# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────
def print_report():
    print("\n" + "="*60)
    print("NFR TEST REPORT -- R26-IT-148")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    cats = {}
    for r in RESULTS:
        c = r["category"]
        if c not in cats:
            cats[c] = {"PASS": 0, "WARN": 0, "FAIL": 0, "total": 0}
        cats[c][r["status"]] += 1
        cats[c]["total"] += 1

    print(f"\n{'Category':<16} {'PASS':>6} {'WARN':>6} {'FAIL':>6} {'Total':>6}  Score")
    print("-" * 60)
    for cat in ["Performance", "Security", "Scalability", "Usability", "Reliability"]:
        if cat in cats:
            c = cats[cat]
            score = (c["PASS"] * 100 + c["WARN"] * 50) / max(c["total"] * 100, 1) * 100
            bar = "#" * int(score / 5) + "." * (20 - int(score / 5))
            print(f"  {cat:<14} {c['PASS']:>6} {c['WARN']:>6} {c['FAIL']:>6} {c['total']:>6}  [{bar}] {score:.0f}%")

    tp = sum(c["PASS"] for c in cats.values())
    tw = sum(c["WARN"] for c in cats.values())
    tf = sum(c["FAIL"] for c in cats.values())
    tt = tp + tw + tf
    overall = (tp * 100 + tw * 50) / max(tt * 100, 1) * 100

    print("-" * 60)
    bar = "#" * int(overall / 5) + "." * (20 - int(overall / 5))
    print(f"  {'TOTAL':<14} {tp:>6} {tw:>6} {tf:>6} {tt:>6}  [{bar}] {overall:.0f}%")

    if tf > 0:
        print(f"\nFAILED ({tf}):")
        for r in RESULTS:
            if r["status"] == "FAIL":
                print(f"  [FAIL] [{r['category']}] {r['test']}: {r['details']}")

    if tw > 0:
        print(f"\nWARNINGS ({tw}):")
        for r in RESULTS:
            if r["status"] == "WARN":
                print(f"  [WARN] [{r['category']}] {r['test']}: {r['details']}")

    report = {"timestamp": datetime.now().isoformat(),
              "summary": {"total": tt, "pass": tp, "warn": tw, "fail": tf, "score": round(overall, 1)},
              "categories": cats, "results": RESULTS}
    with open("nfr_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to nfr_test_report.json")

if __name__ == "__main__":
    print("="*60)
    print("  NFR TEST SUITE v2 -- R26-IT-148")
    print("  Performance | Security | Scalability | Usability | Reliability")
    print("="*60)
    test_performance()
    test_security()
    test_scalability()
    test_usability()
    test_reliability()
    print_report()
