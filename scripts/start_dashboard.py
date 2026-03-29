"""Launch MCP dashboard sidecar and Svelte dev server in parallel.

Purpose:
- Provide a single local entry point for dashboard development.

Behavior:
- Starts FastAPI sidecar with uvicorn targeting `web.server:app`.
- Starts frontend dev server with `npm run dev` in `web/`.
- Waits until interrupted, then terminates both child processes.

Usage:
- uv run --extra web python scripts/start_dashboard.py

Exit codes:
- 0: Clean shutdown after interrupt.
- 1: Startup failure or child process crash.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


def _terminate(proc: subprocess.Popen) -> None:
    """Attempt graceful shutdown, then force kill if needed."""
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def _spawn_processes(repo_root: Path) -> tuple[subprocess.Popen, subprocess.Popen]:
    """Start sidecar and frontend as child processes."""
    web_dir = repo_root / "web"
    sidecar_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "web.server:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]
    frontend_cmd = ["npm", "run", "dev"]

    sidecar = subprocess.Popen(sidecar_cmd, cwd=repo_root)
    try:
        frontend = subprocess.Popen(frontend_cmd, cwd=web_dir)
    except OSError:
        _terminate(sidecar)
        raise
    return sidecar, frontend


def main() -> int:
    """Run dashboard launcher until interrupted or child failure."""
    repo_root = Path(__file__).resolve().parents[1]
    if not (repo_root / "web").exists():
        print("web/ directory not found; scaffold is required before launch.")
        return 1

    try:
        sidecar, frontend = _spawn_processes(repo_root)
    except OSError as exc:
        print(f"Failed to start dashboard processes: {exc}")
        return 1

    print("MCP dashboard launcher started. Press Ctrl+C to stop.")
    exit_code = 0
    try:
        while True:
            if sidecar.poll() is not None or frontend.poll() is not None:
                sidecar_rc = sidecar.poll()
                frontend_rc = frontend.poll()
                if (sidecar_rc not in (None, 0)) or (frontend_rc not in (None, 0)):
                    print(
                        "A child process exited with failure "
                        f"(sidecar={sidecar_rc}, frontend={frontend_rc}); shutting down launcher."
                    )
                    exit_code = 1
                else:
                    print("A child process exited cleanly; shutting down launcher.")
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Interrupt received; stopping dashboard processes.")
    finally:
        _terminate(frontend)
        _terminate(sidecar)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
