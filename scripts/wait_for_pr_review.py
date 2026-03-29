#!/usr/bin/env python3
"""Wait for a GitHub PR review (e.g., Copilot auto-review) to land.

Polls `gh pr view <pr> --json latestReviews` at regular intervals until at
least one review is present or the timeout is reached. Useful in agent
workflows where the next step (triage, reply, re-request) cannot begin until
the automated review exists.

Usage:
    uv run python scripts/wait_for_pr_review.py <pr-number> [--timeout-secs 600] [--repo EndogenAI/dogma]

Arguments:
    pr-number           Pull request number to watch
    --timeout-secs      Maximum wait time in seconds (default: 600 = 10 minutes)
    --repo              Repository in format owner/repo (default: EndogenAI/dogma)
    --interval-secs     Poll interval in seconds (default: 15)
    --min-reviews       Minimum number of reviews to wait for (default: 1)

Exit Codes:
    0                   At least --min-reviews review(s) have landed
    1                   Timeout reached before any review landed
    2                   PR not found or gh CLI error

Examples:
    # Wait for Copilot review on PR 510
    uv run python scripts/wait_for_pr_review.py 510

    # Wait with 5-minute timeout, checking every 10 seconds
    uv run python scripts/wait_for_pr_review.py 510 --timeout-secs 300 --interval-secs 10

Environment:
    Requires `gh` CLI with appropriate GitHub token in GITHUB_TOKEN or via `gh auth`.
"""

import argparse
import json
import subprocess
import sys
import time


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Wait for a GitHub PR review to land.")
    parser.add_argument("pr", type=int, help="Pull request number")
    parser.add_argument(
        "--timeout-secs",
        type=int,
        default=600,
        help="Maximum wait time in seconds (default: 600)",
    )
    parser.add_argument(
        "--repo",
        default="EndogenAI/dogma",
        help="Repository in format owner/repo (default: EndogenAI/dogma)",
    )
    parser.add_argument(
        "--interval-secs",
        type=int,
        default=15,
        help="Poll interval in seconds (default: 15)",
    )
    parser.add_argument(
        "--min-reviews",
        type=int,
        default=1,
        help="Minimum number of reviews to wait for (default: 1)",
    )
    return parser.parse_args()


def get_review_count(pr: int, repo: str) -> int | None:
    """Fetch the current number of reviews on a PR.

    Args:
        pr: Pull request number
        repo: Repository in format owner/repo

    Returns:
        Number of reviews, or None if fetch fails (PR not found or CLI error)
    """
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "view",
                str(pr),
                "--repo",
                repo,
                "--json",
                "latestReviews",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        return len(data.get("latestReviews", []))
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
        return None


def main() -> int:
    """Poll for PR review and return exit code.

    Returns:
        0 if min_reviews reviews landed within timeout
        1 if timeout reached
        2 if PR not found or persistent fetch error
    """
    args = parse_args()
    deadline = time.monotonic() + args.timeout_secs
    consecutive_errors = 0
    max_consecutive_errors = 3

    print(
        f"Waiting for {args.min_reviews} review(s) on PR #{args.pr} "
        f"(repo={args.repo}, timeout={args.timeout_secs}s, interval={args.interval_secs}s)"
    )

    while time.monotonic() < deadline:
        count = get_review_count(args.pr, args.repo)

        if count is None:
            consecutive_errors += 1
            print(f"  Could not fetch review count (attempt {consecutive_errors})")
            if consecutive_errors >= max_consecutive_errors:
                print(f"✗ {max_consecutive_errors} consecutive fetch errors — PR not found or gh CLI error")
                return 2
        else:
            consecutive_errors = 0
            if count >= args.min_reviews:
                print(f"✓ {count} review(s) landed on PR #{args.pr}")
                return 0
            print(f"  {count}/{args.min_reviews} review(s) present — waiting...")

        time.sleep(args.interval_secs)

    print(f"✗ Timeout reached after {args.timeout_secs}s — no review landed on PR #{args.pr}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
