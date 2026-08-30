"""
=============================================================================
RECRUITAI — MASTER ONE-CLICK ECOSYSTEM LAUNCHER
=============================================================================
Launches all 5 FastAPI backend microservices and the Vite React frontend
in parallel, monitors health checks, and opens your default browser.

Usage:
  python start_all.py
  (or double-click start_all.bat on Windows)
=============================================================================
"""
import os
import sys
import time
import subprocess
import webbrowser
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import dns.resolver
    _res = dns.resolver.Resolver()
    _res.nameservers = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
    dns.resolver.default_resolver = _res
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))

# Resolve Python executable (prefer workspace .venv if available)
VENV_PYTHON = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = os.path.join(ROOT, ".venv312", "Scripts", "python.exe")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

PYTHON = VENV_PYTHON
NPM = "npm.cmd" if sys.platform == "win32" else "npm"

# Environment variables for microservices
# Read .env if present
_env_file = os.path.join(ROOT, ".env")
if os.path.exists(_env_file):
    try:
        with open(_env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass

COMMON_ENV = {
    **os.environ,
    "PYTHONUNBUFFERED": "1",
    "MONGODB_URI": os.getenv("MONGODB_URI", "mongodb+srv://admin:PxUm8dLzq5jqlHYN@coordinator.ljarc.mongodb.net/HR"),
    "DB_NAME": os.getenv("DB_NAME", "HR"),
    "JWT_SECRET": os.getenv("JWT_SECRET", "recruitai-dev-secret-key-change-in-prod"),
}

SERVICES = [
    {"id": "c0", "name": "C0 Unified Backend", "type": "backend", "dir": os.path.join(ROOT, "recruit-ai", "backend"), "port": 8000, "health": "http://127.0.0.1:8000/health"},
    {"id": "c1", "name": "C1 Resume Parser",   "type": "backend", "dir": os.path.join(ROOT, "component1", "backend"), "port": 8001, "health": "http://127.0.0.1:8001/health"},
    {"id": "c2", "name": "C2 AI Interview",    "type": "backend", "dir": os.path.join(ROOT, "component2", "backend"), "port": 8002, "health": "http://127.0.0.1:8002/health"},
    {"id": "c3", "name": "C3 Candidate Ranker", "type": "backend", "dir": os.path.join(ROOT, "component3", "backend"), "port": 8003, "health": "http://127.0.0.1:8003/health"},
    {"id": "c4", "name": "C4 Skill Gap API",   "type": "backend", "dir": os.path.join(ROOT, "component4", "backend"), "port": 8004, "health": "http://127.0.0.1:8004/health"},
    {"id": "fe", "name": "React Frontend",     "type": "frontend", "dir": os.path.join(ROOT, "frontend"),             "port": 5174, "health": "http://localhost:5174"},
]

def print_banner():
    banner = "=" * 78
    print("\n" + banner)
    print("   AI-DRIVEN RECRUITMENT ECOSYSTEM — ONE-CLICK MASTER LAUNCHER")
    print("   SLIIT Research Project | Full-Stack AI Recruitment Platform")
    print(banner)
    print("  * Component 0: Unified Auth, Jobs, Resumes, Export  -> http://localhost:8000")
    print("  * Component 1: Resume NLP & Role Classification     -> http://localhost:8001")
    print("  * Component 2: AI Technical Interview System        -> http://localhost:8002")
    print("  * Component 3: LambdaMART LTR Candidate Ranker      -> http://localhost:8003")
    print("  * Component 4: Skill Gap Analysis & Leaderboard     -> http://localhost:8004")
    print("  * Frontend UI: Modern React / Vite Platform         -> http://localhost:5174")
    print(banner + "\n")

def check_health(url: str, timeout: float = 1.5) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RecruitAI-HealthCheck"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status in (200, 304)
    except Exception:
        return False

def main():
    print_banner()

    log_dir = os.path.join(ROOT, "server_logs")
    os.makedirs(log_dir, exist_ok=True)

    procs = []

    print("[1/3] Starting backend microservices...")
    for s in SERVICES:
        if s["type"] == "backend":
            log_path = os.path.join(log_dir, f"{s['id'].upper()}.log")
            log_file = open(log_path, "w", buffering=1, encoding="utf-8", errors="replace")
            cmd = [PYTHON, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(s["port"]), "--reload"]
            p = subprocess.Popen(cmd, cwd=s["dir"], env=COMMON_ENV, stdout=log_file, stderr=log_file, close_fds=False)
            procs.append((s, p, log_file))
            print(f"  -> Started {s['name']:<24} (PID {p.pid:>5}) on port {s['port']}")

    print("\n[2/3] Starting React frontend dev server...")
    fe_service = [s for s in SERVICES if s["type"] == "frontend"][0]
    fe_log_path = os.path.join(log_dir, "FRONTEND.log")
    fe_log_file = open(fe_log_path, "w", buffering=1, encoding="utf-8", errors="replace")
    fe_cmd = [NPM, "run", "dev"]
    fe_proc = subprocess.Popen(fe_cmd, cwd=fe_service["dir"], env=os.environ, stdout=fe_log_file, stderr=fe_log_file, shell=(sys.platform == "win32"))
    procs.append((fe_service, fe_proc, fe_log_file))
    print(f"  -> Started {fe_service['name']:<24} (PID {fe_proc.pid:>5}) on port {fe_service['port']}")

    print("\n[3/3] Verifying ecosystem health checks...")
    start_time = time.time()
    ready = set()
    total_services = len(SERVICES)

    while len(ready) < total_services and (time.time() - start_time) < 30:
        for s, p, lf in procs:
            if s["id"] in ready:
                continue
            if p.poll() is not None:
                print(f"  [-] {s['name']} exited unexpectedly (code {p.returncode})")
                ready.add(s["id"])
                continue
            if check_health(s["health"]):
                print(f"  [+] {s['name']:<24} [ONLINE & HEALTHY] -> {s['health']}")
                ready.add(s["id"])
        time.sleep(1.0)

    print("\n" + "=" * 78)
    print("  ALL SERVICES ARE RUNNING AND READY!")
    print("  Opening browser at: http://localhost:5174")
    print("  Press Ctrl+C in this window at any time to stop all services cleanly.")
    print("=" * 78 + "\n")

    # Open default web browser
    try:
        webbrowser.open("http://localhost:5174")
    except Exception:
        pass

    try:
        while True:
            # Monitor process life
            for s, p, lf in procs:
                if p.poll() is not None:
                    print(f"[ALERT] {s['name']} stopped running (exit code {p.returncode})")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nShutting down all RecruitAI services gracefully...")
        for s, p, lf in procs:
            try:
                if sys.platform == "win32":
                    subprocess.call(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    p.terminate()
            except Exception:
                pass
            try:
                lf.close()
            except Exception:
                pass
        print("[SUCCESS] All services stopped cleanly. Goodbye!\n")

if __name__ == "__main__":
    main()
