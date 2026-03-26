# `orientation\_snapshot`

scripts/orientation_snapshot.py

Pre-computed session orientation digest for agent session start.

Purpose:
    Generate a concise (< 200 lines) orientation context snapshot at
    .cache/github/orientation-snapshot.md. Designed to be run once at session
    start so agents have pre-fetched orientation data without issuing multiple
    gh/git API calls during the session.

    Captures:
    - Open issues count by priority label
    - Last 5 commits on current branch
    - Active branches with last commit date
    - Current milestone summary (if any)
    - Latest ## Session Summary section from the active branch scratchpad (optional)

Inputs:
    --branch BRANCH    Include the active scratchpad session summary for this branch
    --output PATH      Override the output file path
                       (default: .cache/github/orientation-snapshot.md)
    --dry-run          Print the snapshot to stdout without writing the file

Outputs:
    .cache/github/orientation-snapshot.md   Pre-computed orientation digest

Usage:
    uv run python scripts/orientation_snapshot.py
    uv run python scripts/orientation_snapshot.py --branch feat/my-feature
    uv run python scripts/orientation_snapshot.py --dry-run

Exit codes:
    0   Snapshot written (or printed) successfully
    1   Unexpected error

## Usage

```bash
    uv run python scripts/orientation_snapshot.py
    uv run python scripts/orientation_snapshot.py --branch feat/my-feature
    uv run python scripts/orientation_snapshot.py --dry-run
```

<!-- hash:ea9daa88dd74a4bb -->
