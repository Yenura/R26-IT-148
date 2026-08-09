"""Start all backend servers as detached processes."""
import subprocess
import sys
import os
import time

PYTHON = sys.executable
ROOT = os.path.dirname(os.path.abspath(__file__))

servers = [
    {"name": "C0", "dir": os.path.join(ROOT, "recruit-ai", "backend"), "port": 8000},
    {"name": "C2", "dir": os.path.join(ROOT, "component2", "backend"), "port": 8002},
    {"name": "C3", "dir": os.path.join(ROOT, "component3", "backend"), "port": 8003},
    {"name": "C4", "dir": os.path.join(ROOT, "component4", "backend"), "port": 8004},
]

log_dir = os.path.join(ROOT, "server_logs")
os.makedirs(log_dir, exist_ok=True)

procs = []
for s in servers:
    log_path = os.path.join(log_dir, f"{s['name']}.log")
    log_file = open(log_path, "w")
    cmd = [PYTHON, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(s["port"])]
    p = subprocess.Popen(cmd, cwd=s["dir"], stdout=log_file, stderr=log_file,
                         creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW)
    procs.append((s["name"], s["port"], p, log_file))
    print(f"Started {s['name']} (PID {p.pid}) on port {s['port']}, log: {log_path}")

time.sleep(10)

import urllib.request
for name, port, p, lf in procs:
    if p.poll() is not None:
        lf.close()
        print(f"  {name} CRASHED (exit {p.returncode})")
        with open(os.path.join(log_dir, f"{name}.log")) as f:
            print(f"  {f.read()[-500:]}")
        continue
    try:
        r = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3)
        print(f"  {name} port {port}: OK")
    except Exception as e:
        lf.close()
        print(f"  {name} port {port}: FAIL ({e})")
        with open(os.path.join(log_dir, f"{name}.log")) as f:
            print(f"  LOG: {f.read()[-500:]}")
