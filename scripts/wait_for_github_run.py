#!/usr/bin/env python3
"""Wait for GitHub Actions run to complete and return exit code matching conclusion.

Polls GitHub Actions run status at regular intervals until completion or timeout.
Useful for CI workflows where the agent must wait for a build to finish before
proceeding (e.g., after pushing a commit, before merging a PR).

Usage:
    uv run python scripts/wait_for_github_run.py <run-id> [--timeout-secs 150] [--repo EndogenAI/dogma]

Arguments:
    run-id              GitHub Actions run ID (e.g., from `gh run list` output)
    --timeout-secs      Maximum wait time in seconds (default: 150 = 2.5 minutes)
    --repo              Repository in format owner/repo (default: EndogenAI/dogma)
    --interval-secs     Poll interval in seconds (default: 5)

Exit Codes:
    0                   Run completed with conclusion="success"
    1                   Run completed with conclusion="failure" or timeout reached
    2                   Run not found or invalid run ID

Examples:
    # Wait for most recent CI run on current branch
    uv run python scripts/wait_for_github_run.py $(gh run list --limit 1 -q '.[0].databaseId')

    # Wait for a specific run with 5-minute timeout
    uv run python scripts/wait_for_github_run.py 22890618155 --timeout-secs 300

Environment:
    Requires `gh` CLI with appropriate GitHub token in GITHUB_TOKEN or via `gh auth`.
"""

import argparse
import json
import subprocess
import sys
import time


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Wait for GitHub Actions run to complete.")
    parser.add_argument("run_id", help="GitHub Actions run ID")
    parser.add_argument(
        "--timeout-secs",
        type=int,
        default=150,
        help="Maximum wait time in seconds (default: 150)",
    )
    parser.add_argument(
        "--repo",
        default="EndogenAI/dogma",
        help="Repository in format owner/repo (default: EndogenAI/dogma)",
    )
    parser.add_argument(
        "--interval-secs",
        type=int,
        default=5,
        help="Poll interval in seconds (default: 5)",
    )
    return parser.parse_args()


def get_run_status(run_id, repo):
    """Fetch current status and conclusion of a GitHub Actions run.

    Args:
        run_id: GitHub Actions run ID
        repo: Repository in format owner/repo

    Returns:
        Tuple (status, conclusion) or (None, None) if fetch fails
        status: "in_progress" | "completed" | ...
        conclusion: "success" | "failure" | ... | None (if still in progress)
    """
    try:
        result = subprocess.run(
            [
                "gh",
                "run",
                "view",
                run_id,
                "--repo",
                repo,
                "--json",
                "status,conclusion",
                "-q",
                "{status, conclusion}",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None, None

        # Parse JSON output
        data = json.loads(result.stdout.strip())
        return data.get("status"), data.get("conclusion")
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None, None


def main():
    """Poll GitHub Actions run until completion or timeout."""
    args = parse_args()

    max_polls = args.timeout_secs // args.interval_secs
    poll_count = 0

    print(f"Waiting for run {args.run_id} to complete...")
    print(f"Timeout: {args.timeout_secs}s, Interval: {args.interval_secs}s")

    while poll_count < max_polls:
        poll_count += 1
        status, conclusion = get_run_status(args.run_id, args.repo)

        if status is None:
            print(f"[{poll_count}/{max_polls}] Error: Could not fetch run status")
            time.sleep(args.interval_secs)
            continue

        print(f"[{poll_count}/{max_polls}] Status: {status}, Conclusion: {conclusion}")

        if status == "completed":
            if conclusion == "success":
                print("✓ Run completed successfully")
                return 0
            else:
                print(f"✗ Run completed with conclusion: {conclusion}")
                return 1

        time.sleep(args.interval_secs)

    print(f"✗ Timeout reached after {args.timeout_secs}s ({max_polls} polls)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
