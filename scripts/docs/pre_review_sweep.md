# `pre\_review\_sweep`

scripts/pre_review_sweep.py

Pre-review sweep: scans changed files for known bad patterns before CI.

Purpose:
    Catch common antipatterns before they reach CI or code review. Extracts
    known guardrails from AGENTS.md and enforces them programmatically
    on modified files.

Patterns checked:
    1. Heredoc file writes (cat >> file << 'EOF')
    2. Terminal file I/O redirection (> file, >> file, | tee file)
    3. Fetch-before-check guardrail label reversals
    4. Direct Python file operations without File tools

Inputs:
    --changed-files <file>  File containing list of changed paths (one per line)
    --branch <ref>          Git ref for diff baseline (default: main)
    --fix                   If set, report fixes rather than just failures

Outputs:
    stdout: Human-readable pattern report with file:line:pattern

Exit codes:
    0  No patterns found.
    1  Pattern(s) found.

Usage examples:
    git diff --name-only main > /tmp/changed.txt
    uv run python scripts/pre_review_sweep.py --changed-files /tmp/changed.txt

    uv run python scripts/pre_review_sweep.py --branch origin/main

## Usage

```bash
    git diff --name-only main > /tmp/changed.txt
    uv run python scripts/pre_review_sweep.py --changed-files /tmp/changed.txt

    uv run python scripts/pre_review_sweep.py --branch origin/main
```

<!-- hash:0006543f14a9ccd9 -->
