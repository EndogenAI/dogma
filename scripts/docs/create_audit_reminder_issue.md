# `create\_audit\_reminder\_issue`

scripts/create_audit_reminder_issue.py

Create the annual AI dependency audit reminder GitHub issue.

Called by .github/workflows/annual-ai-audit.yml to avoid passing a multi-line
body via --body "..." on the command line (AGENTS.md guardrail).

Purpose:
    Writes the annual audit reminder body to a temp file, checks for an
    existing open reminder issue to avoid duplicates, and creates the GitHub
    issue via `gh issue create --body-file`.

Inputs:
    None (reads current year from system date)
    Requires: GH_TOKEN env var (or gh auth status passing)

Outputs:
    GitHub issue created (or skipped if already exists)
    Prints issue URL on success or "SKIP: issue already open: #N" on duplicate

Exit codes:
    0   Issue created or duplicate detected (both are success)
    1   gh CLI not available or issue creation failed
    2   I/O error writing temp file

Usage example:
    uv run python scripts/create_audit_reminder_issue.py

## Usage

```bash
    uv run python scripts/create_audit_reminder_issue.py
```

<!-- hash:6245cd1c45ccf695 -->
