"""
AirGuard AI - Single-Command Unified System Launcher
Boots:
1. FastAPI Backend & Predictive Engine (Port 8000)
2. Virtual IoT Sensor Fleet Simulator (Streams live multi-room telemetry)
3. React Vite Frontend Client (Port 5173)
"""

import sys
import os
import time
import subprocess
import requests

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(ROOT_DIR, ".venv", "Scripts", "python.exe")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable


def wait_for_backend(url="http://127.0.0.1:8000/health", timeout=20):
    print("[Launcher] Waiting for FastAPI backend to initialize...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=1.0)
            if r.status_code == 200:
                print(f"[Launcher] Backend is READY! (R^2 Models loaded: {r.json().get('models')})")
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def main():
    print("=" * 65)
    print("   AirGuard AI — Personal Air Quality Intelligence Platform   ")
    print("=" * 65)

    processes = []

    try:
        # 1. Start FastAPI Backend
        print("[Launcher] Starting FastAPI backend on http://127.0.0.1:8000...")
        backend_proc = subprocess.Popen(
            [VENV_PYTHON, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=ROOT_DIR
        )
        processes.append(backend_proc)

        if not wait_for_backend():
            print("[Launcher] Warning: Backend startup timed out, continuing...")

        # 2. Start Virtual Sensor Fleet Simulator
        print("[Launcher] Starting Virtual Multi-Room Sensor Fleet...")
        sim_proc = subprocess.Popen(
            [VENV_PYTHON, "-m", "simulator.run_simulation", "--url", "http://127.0.0.1:8000/api", "--interval", "2.0"],
            cwd=ROOT_DIR
        )
        processes.append(sim_proc)

        # 3. Start Frontend Dev Server
        print("[Launcher] Starting Vite React Frontend Client on http://localhost:5173...")
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        frontend_proc = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=os.path.join(ROOT_DIR, "frontend")
        )
        processes.append(frontend_proc)

        print("\n" + "=" * 65)
        print("  System Online & Streaming!")
        print("  - Web Dashboard:     http://localhost:5173")
        print("  - Backend API Docs:  http://127.0.0.1:8000/docs")
        print("  - WebSocket Stream:  ws://127.0.0.1:8000/ws/telemetry")
        print("=" * 65)
        print("  Press Ctrl+C to terminate all services.\n")

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[Launcher] Shutting down AirGuard AI system...")
        for p in processes:
            p.terminate()
            p.wait()
        print("[Launcher] All processes terminated cleanly.")


if __name__ == "__main__":
    main()
