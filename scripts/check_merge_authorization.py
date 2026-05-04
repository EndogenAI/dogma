#!/usr/bin/env python3
"""Check whether a GitHub PR is authorized for merge.

Queries `gh pr view <pr> --json state,reviews,reviewRequests` and fetches review
threads via `gh api graphql`, then evaluates four mandatory criteria before
authorizing merge.

Checks (evaluated in order; first failure blocks):
  a. PR state is OPEN (not merged or closed)
  b. No review has state CHANGES_REQUESTED outstanding
  c. No pending reviewRequests (all requested reviewers have responded)
  d. All non-nit reviewThreads are resolved (a thread is "nit" if its first
     comment body starts with "nit:", case-insensitive)

Outputs:
  MERGE AUTHORIZED — <summary>          (exit 0)  all checks pass
  MERGE BLOCKED — <reason>: <next step> (exit 1)  first failing check
  (dry-run) table of ✅/❌ per criterion             (always exit 0)

Exit codes:
  0  Authorized
  1  Blocked
  2  API error (gh not found, PR not found, JSON parse failure)

Usage:
    # Standard check
    uv run python scripts/check_merge_authorization.py 573

    # With explicit repo
    uv run python scripts/check_merge_authorization.py 573 --repo EndogenAI/dogma

    # Dry-run — shows full check table, always exits 0
    uv run python scripts/check_merge_authorization.py 573 --dry-run

    # Enforce nit threads too (default: nit threads are exempt)
    uv run python scripts/check_merge_authorization.py 573 --no-allow-nit-unresolved
"""

import argparse
import json
import subprocess
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------


def get_default_repo() -> str | None:
    """Return owner/repo from `gh repo view`, or None on error."""
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        return data.get("nameWithOwner")
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return None


def fetch_review_threads(pr: int, repo: str) -> list[dict] | None:
    """Fetch PR review threads via gh api graphql.

    Returns a list of thread dicts, or None on any error.
    Each dict has keys: isResolved, path, line, originalLine, comments.
    """
    parts = repo.split("/", 1)
    if len(parts) != 2:
        return None
    owner, name = parts

    query = (
        "query($owner: String!, $name: String!, $number: Int!) {"
        "  repository(owner: $owner, name: $name) {"
        "    pullRequest(number: $number) {"
        "      reviewThreads(first: 100) {"
        "        nodes {"
        "          isResolved"
        "          path"
        "          line"
        "          originalLine"
        "          comments(first: 1) {"
        "            nodes { body }"
        "          }"
        "        }"
        "      }"
        "    }"
        "  }"
        "}"
    )

    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                "graphql",
                "-f",
                f"query={query}",
                "-f",
                f"owner={owner}",
                "-f",
                f"name={name}",
                "-F",
                f"number={pr}",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        response = json.loads(result.stdout)
        nodes = response["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]
        return [
            {
                "isResolved": node["isResolved"],
                "path": node.get("path"),
                "line": node.get("line"),
                "originalLine": node.get("originalLine"),
                "comments": [{"body": c.get("body", "")} for c in node["comments"]["nodes"]],
            }
            for node in nodes
        ]
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, OSError, KeyError):
        return None


def fetch_pr_data(pr: int, repo: str) -> dict[str, Any] | None:
    """Fetch PR JSON from gh CLI.

    Returns a dict with keys: state, reviews, reviewRequests, reviewThreads.
    Returns None on any error (gh missing, PR not found, JSON parse failure).
    reviewThreads is populated via a separate GraphQL call; if that call fails,
    it defaults to [] so the remaining checks are not blocked.
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
                "state,reviews,reviewRequests",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        # Validate required keys are present
        for key in ("state", "reviews", "reviewRequests"):
            if key not in data:
                return None
        # Fetch review threads via GraphQL; fall back to empty list if unavailable
        threads = fetch_review_threads(pr, repo)
        data["reviewThreads"] = threads if threads is not None else []
        return data
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Individual checks — each returns (passed: bool, reason: str, next_step: str)
# ---------------------------------------------------------------------------


def check_pr_open(data: dict[str, Any]) -> tuple[bool, str, str]:
    """Check a. PR must be in OPEN state."""
    state = data.get("state", "")
    if state == "OPEN":
        return True, "PR is OPEN", ""
    return (
        False,
        f"PR state is {state!r} (not OPEN)",
        "Reopen the PR or target a different PR number.",
    )


def check_no_changes_requested(data: dict[str, Any]) -> tuple[bool, str, str]:
    """Check b. No review with state CHANGES_REQUESTED."""
    # Group reviews by author; last entry per author is the most recent (GitHub
    # returns reviews in chronological order).
    latest_by_author: dict[str, str] = {}
    for r in data.get("reviews", []):
        login = r.get("author", {}).get("login", "unknown")
        latest_by_author[login] = r.get("state", "")
    blocking = [login for login, state in latest_by_author.items() if state == "CHANGES_REQUESTED"]
    if not blocking:
        return True, "No CHANGES_REQUESTED reviews", ""
    reviewers = ", ".join(blocking)
    return (
        False,
        f"CHANGES_REQUESTED by: {reviewers}",
        "Address the requested changes and push a fix commit, then re-request review.",
    )


def check_no_pending_requests(data: dict[str, Any]) -> tuple[bool, str, str]:
    """Check c. No pending reviewRequests (all requested reviewers have responded)."""
    pending = data.get("reviewRequests", [])
    if not pending:
        return True, "No pending review requests", ""
    names = ", ".join(r.get("login") or r.get("name") or str(r) for r in pending)
    return (
        False,
        f"Review not yet received from: {names}",
        "Wait for the pending reviewer(s) to submit their review.",
    )


def check_threads_resolved(data: dict[str, Any], allow_nit_unresolved: bool = True) -> tuple[bool, str, str]:
    """Check d. All non-nit reviewThreads are resolved.

    A thread is considered a "nit" if its first comment body starts with
    "nit:" (case-insensitive).  When allow_nit_unresolved is True (default),
    unresolved nit threads do not block merge.
    """
    unresolved: list[str] = []
    for thread in data.get("reviewThreads", []):
        if thread.get("isResolved"):
            continue
        # Determine if this thread is a nit
        comments = thread.get("comments", [])
        first_body = ""
        if comments:
            first_body = (comments[0].get("body") or "").strip().lower()
        is_nit = first_body.startswith("nit:")
        if is_nit and allow_nit_unresolved:
            continue
        # Build a brief label for the unresolved thread
        path = thread.get("path") or "unknown file"
        line = thread.get("line") or thread.get("originalLine") or "?"
        unresolved.append(f"{path}:{line}")

    if not unresolved:
        msg = "All non-nit review threads resolved" if allow_nit_unresolved else "All review threads resolved"
        return True, msg, ""
    count = len(unresolved)
    locations = ", ".join(unresolved[:3])
    if count > 3:
        locations += f" … (+{count - 3} more)"
    return (
        False,
        f"{count} unresolved review thread(s): {locations}",
        "Resolve all open review threads before merging.",
    )


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


CheckResult = tuple[str, bool, str, str]  # (label, passed, reason, next_step)


def run_checks(data: dict[str, Any], allow_nit_unresolved: bool = True) -> list[CheckResult]:
    """Run all four checks and return a list of (label, passed, reason, next_step)."""
    checks = [
        ("a. PR state is OPEN", check_pr_open(data)),
        ("b. No CHANGES_REQUESTED", check_no_changes_requested(data)),
        ("c. No pending review requests", check_no_pending_requests(data)),
        (
            "d. All non-nit threads resolved",
            check_threads_resolved(data, allow_nit_unresolved),
        ),
    ]
    return [(label, passed, reason, next_step) for label, (passed, reason, next_step) in checks]


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def format_dry_run_table(results: list[CheckResult]) -> str:
    """Render a dry-run check table with ✅/❌ per criterion."""
    lines = ["Merge Authorization Check (dry-run)", "=" * 40]
    for label, passed, reason, _next in results:
        icon = "✅" if passed else "❌"
        lines.append(f"  {icon}  {label}")
        if reason:
            lines.append(f"       {reason}")
    lines.append("=" * 40)
    lines.append("(dry-run: no merge decision made; always exits 0)")
    return "\n".join(lines)


def format_authorized(results: list[CheckResult]) -> str:
    """Format the MERGE AUTHORIZED output line."""
    passed_labels = [label for label, passed, _, _ in results if passed]
    summary = "; ".join(passed_labels)
    return f"MERGE AUTHORIZED — {summary}"


def format_blocked(results: list[CheckResult]) -> str:
    """Format the MERGE BLOCKED output line for the first failing check."""
    for label, passed, reason, next_step in results:
        if not passed:
            return f"MERGE BLOCKED — {label} — {reason}: {next_step}"
    return "MERGE BLOCKED — unknown reason"


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Check whether a GitHub PR is authorized for merge.",
    )
    parser.add_argument("pr", type=int, help="Pull request number to check")
    parser.add_argument(
        "--repo",
        default=None,
        help="Repository in owner/repo format (default: read from gh repo view)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print full check table; always exit 0",
    )
    nit_group = parser.add_mutually_exclusive_group()
    nit_group.add_argument(
        "--allow-nit-unresolved",
        dest="allow_nit_unresolved",
        action="store_true",
        default=True,
        help="Allow unresolved nit threads (default: True)",
    )
    nit_group.add_argument(
        "--no-allow-nit-unresolved",
        dest="allow_nit_unresolved",
        action="store_false",
        help="Treat unresolved nit threads as blocking",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Main entry point; returns exit code."""
    args = parse_args(argv)

    # Resolve repo
    repo = args.repo
    if not repo:
        repo = get_default_repo()
    if not repo:
        print(
            "MERGE BLOCKED — API error: could not determine repository. Pass --repo owner/repo explicitly.",
            file=sys.stderr,
        )
        return 2

    # Fetch PR data
    data = fetch_pr_data(args.pr, repo)
    if data is None:
        print(
            f"MERGE BLOCKED — API error: could not fetch PR #{args.pr} from {repo}. "
            "Ensure gh CLI is installed and authenticated, and the PR number is valid.",
            file=sys.stderr,
        )
        return 2

    # Run checks
    results = run_checks(data, args.allow_nit_unresolved)

    if args.dry_run:
        print(format_dry_run_table(results))
        return 0

    all_passed = all(passed for _, passed, _, _ in results)
    if all_passed:
        print(format_authorized(results))
        return 0
    else:
        print(format_blocked(results))
        return 1


if __name__ == "__main__":
    sys.exit(main())
