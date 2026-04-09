"""Start the local OTel observability stack (OTel Collector + Jaeger) via docker compose.

Usage: uv run python scripts/start_otel_stack.py [--stop]

Runs `docker compose up -d`, waits for Jaeger UI health at localhost:16686, then prints the URL.
Use --stop to run `docker compose down` instead.

Inputs:
    --stop  (flag) — tear down the stack instead of starting it

Outputs:
    stdout — status message with Jaeger UI URL on success

Exit codes:
    0 — stack started and Jaeger UI is ready (or stack successfully stopped)
    1 — Jaeger UI did not become ready within the timeout window
    2 — docker executable not found
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.error
import urllib.request

JAEGER_URL = "http://localhost:16686"
MAX_RETRIES = 20
RETRY_SLEEP = 1.0


def _run_compose(args: list[str]) -> None:
    """Run a docker compose subcommand, raising SystemExit(2) if docker is not found."""
    try:
        subprocess.run(["docker", "compose", *args], check=True)
    except FileNotFoundError:
        print("docker not found. Install Docker Desktop or the Docker CLI.", file=sys.stderr)
        sys.exit(2)


def _wait_for_jaeger(max_retries: int = MAX_RETRIES, sleep: float = RETRY_SLEEP) -> bool:
    """Poll Jaeger UI until it responds or retries are exhausted. Returns True on success."""
    for _ in range(max_retries):
        try:
            with urllib.request.urlopen(JAEGER_URL, timeout=2):
                return True
        except (urllib.error.URLError, OSError):
            time.sleep(sleep)
    return False


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Start or stop the local OTel observability stack (OTel Collector + Jaeger)."
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Stop the stack (docker compose down) instead of starting it.",
    )
    args = parser.parse_args(argv)

    if args.stop:
        _run_compose(["down"])
        print("OTel stack stopped.")
        sys.exit(0)

    _run_compose(["up", "-d"])
    # Actual timeout budget accounts for both urlopen timeout and sleep per retry
    timeout_budget = MAX_RETRIES * (2 + RETRY_SLEEP)
    if _wait_for_jaeger():
        print(f"OTel stack ready. Jaeger UI: {JAEGER_URL}")
        sys.exit(0)
    else:
        print(
            f"Jaeger UI did not become ready within ~{timeout_budget:.0f}s. Check `docker compose logs`.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
