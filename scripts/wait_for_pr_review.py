#!/usr/bin/env python3
"""Wait for all requested GitHub PR reviews to land.

Polls `gh pr view <pr> --json reviewRequests,reviews` at regular intervals.
Uses `reviewRequests` (pending reviewers) as the denominator signal: when it
is empty and at least one new qualifying review has appeared since startup, all
requested reviews have completed.

Algorithm:
  1. Snapshot baseline state at startup (existing review IDs, initial pending list).
  2. Exit 0 when `reviewRequests` is empty AND at least one new qualifying review appeared.
  3. Edge case — `initial_pending` was already empty at startup:
       - qualifying reviews > 0 at startup  → exit 0 immediately (already complete)
       - qualifying reviews == 0 at startup → fall through to `--min-reviews` fallback
  4. `--min-reviews` fallback: activated only when auto-detect has no denominator
     (initial_pending was empty AND no reviews at startup, or baseline fetch failed).
     Waits until `new_qualifying_reviews >= min_reviews`.

Reviews with an empty body (thread-resolve events) are excluded by default via
--min-body-len (default: 1). Filter by state with --states.

Usage:
    uv run python scripts/wait_for_pr_review.py <pr-number> [--timeout-secs 600] [--repo EndogenAI/dogma]

Arguments:
    pr-number           Pull request number to watch
    --timeout-secs      Maximum wait time in seconds (default: 600 = 10 minutes)
    --repo              Repository in format owner/repo (default: EndogenAI/dogma)
    --interval-secs     Poll interval in seconds (default: 15)
    --min-reviews       Fallback: minimum new reviews when auto-detect unavailable (default: 1)
    --min-body-len      Minimum body character length for a review to count (default: 1).
                        Set to 0 to count all reviews including empty-body entries.
    --states            Space-separated list of review states to accept. If omitted,
                        all states are accepted. Options: APPROVED CHANGES_REQUESTED
                        COMMENTED DISMISSED PENDING.

Exit Codes:
    0                   Review threshold met (all pending reviewers resolved, or --min-reviews count reached)
    1                   Timeout reached before the --min-reviews threshold was met
    2                   PR not found, gh CLI missing, or persistent fetch error

Examples:
    # Wait for all requested reviews on PR 510
    uv run python scripts/wait_for_pr_review.py 510

    # Wait only for APPROVED or CHANGES_REQUESTED reviews
    uv run python scripts/wait_for_pr_review.py 510 --states APPROVED CHANGES_REQUESTED

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
    parser = argparse.ArgumentParser(description="Wait for all requested GitHub PR reviews to land.")
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
        help="Fallback: minimum new reviews when auto-detect has no denominator (default: 1)",
    )
    parser.add_argument(
        "--min-body-len",
        type=int,
        default=1,
        help="Minimum body character length for a review to count (default: 1). "
        "Set to 0 to include empty-body entries.",
    )
    parser.add_argument(
        "--states",
        nargs="*",
        default=None,
        metavar="STATE",
        help="Space-separated list of review states to accept "
        "(APPROVED CHANGES_REQUESTED COMMENTED DISMISSED PENDING). "
        "If omitted, all states are accepted.",
    )
    return parser.parse_args()


def get_pr_state(pr: int, repo: str) -> dict | None:
    """Fetch current reviewRequests and reviews for a PR.

    Calls ``gh pr view <pr> --repo <repo> --json reviewRequests,reviews``.

    Args:
        pr: Pull request number.
        repo: Repository in format owner/repo.

    Returns:
        dict with keys:
            ``pending``: list of login/name strings for reviewers who haven't reviewed yet.
            ``reviews``: list of dicts with keys ``id``, ``body``, ``state``, ``author``.
        Returns None on any error (gh CLI missing, non-zero exit, bad JSON, missing key).
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
                "reviewRequests,reviews",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        pending = [r.get("login") or r.get("name", "") for r in data["reviewRequests"]]
        reviews = [
            {
                "id": r["id"],
                "body": r.get("body", ""),
                "state": r["state"],
                "author": r["author"]["login"],
            }
            for r in data["reviews"]
        ]
        return {"pending": pending, "reviews": reviews}
    except FileNotFoundError:
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
        return None


def _qualifying_reviews(
    reviews: list[dict],
    min_body_len: int,
    states: list[str] | None,
) -> list[dict]:
    """Return reviews that meet body-length and state criteria."""
    return [
        r for r in reviews if len(r.get("body", "")) >= min_body_len and (states is None or r.get("state") in states)
    ]


def main() -> int:
    """Poll for all requested PR reviews and return exit code.

    Returns:
        0 if all requested reviews landed (or fallback threshold met) within timeout.
        1 if timeout reached.
        2 if PR not found, gh CLI missing, or persistent fetch error.
    """
    args = parse_args()
    deadline = time.monotonic() + args.timeout_secs
    consecutive_errors = 0
    max_consecutive_errors = 3

    # --- Snapshot baseline state ---
    baseline_state = get_pr_state(args.pr, args.repo)
    if baseline_state is None:
        consecutive_errors += 1
        initial_pending = None
        baseline_review_ids: set[str] = set()
        baseline_qualifying: list[dict] = []
    else:
        initial_pending = baseline_state["pending"]
        baseline_qualifying = _qualifying_reviews(baseline_state["reviews"], args.min_body_len, args.states)
        baseline_review_ids = {r["id"] for r in baseline_qualifying}

    # --- Determine mode and denominator ---
    if initial_pending is not None and len(initial_pending) == 0:
        # No pending reviewers at startup
        if len(baseline_qualifying) >= args.min_reviews:
            # Already at or above the required review count
            print(f"✓ All {len(baseline_qualifying)} review(s) landed on PR #{args.pr}")
            return 0
        # Below --min-reviews threshold → fall through to fallback and keep polling
        use_fallback = True
        denominator = args.min_reviews
        print(
            f"(auto-detect unavailable: no pending reviewers at startup; "
            f"waiting for --min-reviews {args.min_reviews} total qualifying review(s), "
            f"{len(baseline_qualifying)} already present)"
        )
    else:
        # Either pending reviewers exist, or baseline fetch failed → use fallback if no denominator
        use_fallback = initial_pending is None
        denominator = len(initial_pending) if initial_pending is not None else args.min_reviews

    print(
        f"Waiting for {denominator} review(s) on PR #{args.pr} "
        f"(repo={args.repo}, timeout={args.timeout_secs}s, interval={args.interval_secs}s)"
    )

    latest_new_count = 0
    latest_total_count = len(baseline_qualifying)

    while time.monotonic() < deadline:
        state = get_pr_state(args.pr, args.repo)

        if state is None:
            consecutive_errors += 1
            print(f"  Could not fetch PR state (attempt {consecutive_errors})")
            if consecutive_errors >= max_consecutive_errors:
                print(f"✗ {max_consecutive_errors} consecutive fetch errors — PR not found or gh CLI error")
                return 2
        else:
            consecutive_errors = 0
            current_pending = state["pending"]
            current_qualifying = _qualifying_reviews(state["reviews"], args.min_body_len, args.states)
            new_reviews = [r for r in current_qualifying if r["id"] not in baseline_review_ids]
            new_count = len(new_reviews)
            latest_new_count = new_count
            pending_count = len(current_pending)

            total_so_far = len(current_qualifying)
            latest_total_count = total_so_far
            if use_fallback:
                remaining = max(0, denominator - total_so_far)
                print(f"  [{total_so_far}/{denominator}] {total_so_far} qualifying review(s), {remaining} more needed")
            else:
                display_count = min(new_count, denominator)
                landed = f"{new_count} new review(s) landed"
                print(f"  [{display_count}/{denominator}] {landed}, {pending_count} still pending")

            if use_fallback:
                # Count total qualifying reviews (baseline + new)
                total_count = len(current_qualifying)
                if total_count >= args.min_reviews:
                    print(f"✓ {total_count} review(s) landed on PR #{args.pr} (threshold: {args.min_reviews})")
                    return 0
            else:
                # Primary exit: all pending resolved AND at least one new review
                if pending_count == 0 and new_count >= 1:
                    print(f"✓ All {new_count} review(s) landed on PR #{args.pr}")
                    return 0

        time.sleep(args.interval_secs)

    if use_fallback:
        msg = f"{latest_total_count}/{denominator} qualifying review(s) present"
        print(f"✗ Timed out: {msg} — threshold not reached before timeout")
    else:
        print(f"✗ Timed out: {latest_new_count} of {denominator} new review(s) landed before timeout")
    return 1


if __name__ == "__main__":
    sys.exit(main())
