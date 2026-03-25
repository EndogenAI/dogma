"""check_branch_sync.py — Verify that the current branch is in sync with origin/main.

Purpose:
    Detects whether the current local branch has fallen behind a remote base branch
    (default: origin/main). If behind, lists the commits that are missing and
    optionally rebases the local branch onto the remote base.

    Implements the Branch Sync Gate from AGENTS.md § Session-Start Encoding
    Checkpoint and the Executive Orchestrator § 1. Orient step. Encodes the
    L2→L3 fix for recurring merge conflicts identified in the 2026-03-24
    session retrospective (closes #435).

Inputs:
    --remote REMOTE   Remote name to check against (default: origin)
    --base BRANCH     Base branch to compare to (default: main)
    --rebase          If behind, run `git rebase <remote>/<base>` automatically
    --quiet           Suppress progress output; still exit 1 if behind

Outputs:
    Stdout: human-readable sync status or list of commits the branch is behind by.
    With --rebase: status message after successful rebase.

Exit codes:
    0   Branch is in sync (up to date with remote base)
    1   Branch is behind remote base (commits listed on stdout unless --quiet)
    2   Error: git command failed or unexpected I/O error

Usage examples:
    # Check sync, exit 1 if behind
    uv run python scripts/check_branch_sync.py

    # Check against a different remote/base
    uv run python scripts/check_branch_sync.py --remote upstream --base develop

    # Auto-rebase if behind
    uv run python scripts/check_branch_sync.py --rebase

    # Silent CI gate mode
    uv run python scripts/check_branch_sync.py --quiet
"""

from __future__ import annotations

import argparse
import subprocess
import sys


def _run(cmd: list[str], *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the CompletedProcess result."""
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
    )


def fetch_remote(remote: str) -> None:
    """Fetch the latest state from the remote (silent)."""
    result = _run(["git", "fetch", remote])
    if result.returncode != 0:
        print(
            f"ERROR: git fetch {remote} failed:\n{result.stderr.strip()}",
            file=sys.stderr,
        )
        sys.exit(2)


def get_behind_commits(remote: str, base: str) -> list[str]:
    """Return one-line commit summaries that remote/base has but HEAD does not."""
    ref = f"{remote}/{base}"
    result = _run(["git", "log", f"HEAD..{ref}", "--oneline"])
    if result.returncode != 0:
        print(
            f"ERROR: git log HEAD..{ref} failed:\n{result.stderr.strip()}",
            file=sys.stderr,
        )
        sys.exit(2)
    lines = result.stdout.strip().splitlines()
    return [line for line in lines if line]


def rebase_onto(remote: str, base: str) -> None:
    """Rebase HEAD onto remote/base. Exits 2 on failure."""
    ref = f"{remote}/{base}"
    result = _run(["git", "rebase", ref], capture=False)
    if result.returncode != 0:
        print(
            f"ERROR: git rebase {ref} failed. Resolve conflicts, then continue.",
            file=sys.stderr,
        )
        sys.exit(2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the current branch is in sync with origin/main.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Remote name to check against (default: origin)",
    )
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch to compare to (default: main)",
    )
    parser.add_argument(
        "--rebase",
        action="store_true",
        help="Automatically rebase onto remote/base if behind",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output; still exit 1 if behind",
    )
    args = parser.parse_args(argv)

    if not args.quiet:
        print(f"Fetching {args.remote}...")
    fetch_remote(args.remote)

    behind = get_behind_commits(args.remote, args.base)

    if not behind:
        if not args.quiet:
            print(f"✓ Branch is up to date with {args.remote}/{args.base}.")
        return 0

    ref = f"{args.remote}/{args.base}"
    if not args.quiet:
        print(f"✗ Branch is {len(behind)} commit(s) behind {ref}. Missing commits:")
        for commit in behind:
            print(f"  {commit}")

    if args.rebase:
        if not args.quiet:
            print(f"\nRebasing onto {ref}...")
        rebase_onto(args.remote, args.base)
        if not args.quiet:
            print("✓ Rebase complete.")
        return 0

    if not args.quiet:
        print(f"\nRun `git rebase {ref}` to sync, or re-run with --rebase to do it automatically.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
