"""Launch MCP dashboard sidecar and Svelte dev server in parallel.

Purpose:
- Provide a single local entry point for dashboard development.

Behavior:
- Starts FastAPI sidecar with uvicorn targeting `web.server:app`.
- Starts frontend dev server with `npm run dev` in `web/`.
- Waits until interrupted, then terminates both child processes.

Development mode (--development / -d):
- Sidecar is launched with `--reload` (uvicorn auto-reloads on Python file changes).
- Frontend already uses Vite HMR by default — no additional flag needed.
- Add this flag when iterating on server.py or the Svelte UI source to avoid
  manually restarting the launcher on every change.

Usage:
- uv run --extra web python scripts/start_dashboard.py
- uv run --extra web python scripts/start_dashboard.py --development

Exit codes:
- 0: Clean shutdown after interrupt.
- 1: Startup failure or child process crash.
"""

from __future__ import annotations

import argparse
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


def _spawn_processes(repo_root: Path, *, development: bool = False) -> tuple[subprocess.Popen, subprocess.Popen]:
    """Start sidecar and frontend as child processes.

    Args:
        repo_root:   Absolute path to the repository root.
        development: When True, passes ``--reload`` to uvicorn so the
                     sidecar automatically restarts on Python source changes.
                     The frontend (Vite) already uses HMR unconditionally.
    """
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
    if development:
        sidecar_cmd.append("--reload")
    frontend_cmd = ["npm", "run", "dev"]

    # Pass through WEBMCP_CORS_ORIGINS environment variable if set
    import os

    sidecar_env = os.environ.copy()
    if "WEBMCP_CORS_ORIGINS" in os.environ:
        sidecar_env["WEBMCP_CORS_ORIGINS"] = os.environ["WEBMCP_CORS_ORIGINS"]

    sidecar = subprocess.Popen(sidecar_cmd, cwd=repo_root, env=sidecar_env)
    try:
        frontend = subprocess.Popen(frontend_cmd, cwd=web_dir)
    except OSError:
        _terminate(sidecar)
        raise
    return sidecar, frontend


def main() -> int:
    """Run dashboard launcher until interrupted or child failure."""
    parser = argparse.ArgumentParser(description="Launch MCP dashboard sidecar and Svelte dev server.")
    parser.add_argument(
        "-d",
        "--development",
        action="store_true",
        default=False,
        help=(
            "Enable development mode: sidecar runs with uvicorn --reload "
            "(auto-restarts on Python file changes). "
            "Frontend HMR is always active via Vite."
        ),
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    if not (repo_root / "web").exists():
        print("web/ directory not found; scaffold is required before launch.")
        return 1

    if args.development:
        print("Development mode: sidecar will reload on source changes.")

    try:
        sidecar, frontend = _spawn_processes(repo_root, development=args.development)
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
