# `check\_branch\_sync`

check_branch_sync.py — Verify that the current branch is in sync with origin/main.

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

## Usage

```bash
    # Check sync, exit 1 if behind
    uv run python scripts/check_branch_sync.py

    # Check against a different remote/base
    uv run python scripts/check_branch_sync.py --remote upstream --base develop

    # Auto-rebase if behind
    uv run python scripts/check_branch_sync.py --rebase

    # Silent CI gate mode
    uv run python scripts/check_branch_sync.py --quiet
```

<!-- hash:70a02fe69b6bdfea -->
