"""Start all backend servers as detached processes."""
import subprocess
import sys
import os
import time

PYTHON = sys.executable
ROOT = os.path.dirname(os.path.abspath(__file__))

servers = [
    {"name": "C0", "dir": os.path.join(ROOT, "recruit-ai", "backend"), "port": 8000},
    {"name": "C1", "dir": os.path.join(ROOT, "component1", "backend"), "port": 8001},
    {"name": "C2", "dir": os.path.join(ROOT, "component2", "backend"), "port": 8002},
    {"name": "C3", "dir": os.path.join(ROOT, "component3", "backend"), "port": 8003},
    {"name": "C4", "dir": os.path.join(ROOT, "component4", "backend"), "port": 8004},
]

log_dir = os.path.join(ROOT, "server_logs")
os.makedirs(log_dir, exist_ok=True)

env = {
    **os.environ,
    "PYTHONUNBUFFERED": "1",
    "MONGODB_URI": "mongodb+srv://admin:PxUm8dLzq5jqlHYN@coordinator.ljarc.mongodb.net/HR",
    "DB_NAME": "HR"
}
procs = []
for s in servers:
    log_path = os.path.join(log_dir, f"{s['name']}.log")
    log_file = open(log_path, "w", buffering=1)
    cmd = [PYTHON, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(s["port"])]
    p = subprocess.Popen(cmd, cwd=s["dir"], env=env, stdout=log_file, stderr=log_file, close_fds=False)
    procs.append((s["name"], s["port"], p, log_file))
    print(f"Started {s['name']} (PID {p.pid}) on port {s['port']}, log: {log_path}")

print("Waiting for servers to initialize...")
import urllib.request

ready = set()
for attempt in range(25):
    for name, port, p, lf in procs:
        if name in ready:
            continue
        if p.poll() is not None:
            print(f"  {name} CRASHED (exit {p.returncode})")
            ready.add(name)
            continue
        try:
            r = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2)
            if r.status == 200:
                print(f"  {name} port {port}: OK")
                ready.add(name)
        except Exception:
            pass
    if len(ready) == len(procs):
        break
    time.sleep(2)

print("\nAll backend servers online and being monitored. Running continuously...")
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("Shutting down servers...")
    for name, port, p, lf in procs:
        p.terminate()
        lf.close()


