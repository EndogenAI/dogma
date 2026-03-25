"""scripts/create_audit_reminder_issue.py

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
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path


def _gh(*args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["gh", *args], capture_output=True, text=True)
    except FileNotFoundError:
        print("ERROR: gh CLI not found. Install from https://cli.github.com", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    year = date.today().year
    prev_year = year - 1

    title = f"chore: annual AI dependency audit due — NIST AI RMF GOVERN 6.1 ({year})"

    # Duplicate check: abort if an open issue with this title already exists
    result = _gh(
        "issue",
        "list",
        "--state",
        "open",
        "--search",
        title,
        "--json",
        "number",
        "-q",
        ".[0].number",
    )
    if result.returncode != 0:
        print(f"ERROR: gh issue list failed: {result.stderr}", file=sys.stderr)
        return 1

    existing = result.stdout.strip()
    if existing:
        print(f"SKIP: reminder issue already open: #{existing}")
        return 0

    body = f"""## Annual AI Dependency Audit — NIST AI RMF GOVERN 6.1

This issue is opened automatically on 1 January each year by the
`.github/workflows/annual-ai-audit.yml` workflow.

## What to do

1. Run the dependency scanner: `uv run python scripts/audit_ai_dependencies.py --dry-run`
2. Review changes against last year's inventory in `data/enisa-lock-in-scoring.yml`
3. Score any new providers on the 8 ENISA dimensions
4. Update `data/enisa-lock-in-scoring.yml` with new scores and rationale
5. Create `docs/research/ai-dependency-audit-{year}.md` using the prior year's doc as template
6. Update `next_review_due` in `data/enisa-lock-in-scoring.yml` to next year
7. Commit with: `chore(deps): annual AI dependency audit {year}`
8. Close this issue

## Reference

- Tooling: `scripts/audit_ai_dependencies.py`
- Scoring table: `data/enisa-lock-in-scoring.yml`
- Prior audit: `docs/research/ai-dependency-audit-{prev_year}.md`
- Governing axiom: [MANIFESTO.md § 3 Local-Compute-First](MANIFESTO.md#3-local-compute-first)
- Research source: `docs/research/ai-platform-lock-in-risks.md` Recommendation 7
"""

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp:
            tmp.write(body)
            tmp_path = tmp.name
    except OSError as exc:
        print(f"ERROR writing temp file: {exc}", file=sys.stderr)
        return 2

    try:
        create_result = _gh(
            "issue",
            "create",
            "--title",
            title,
            "--body-file",
            tmp_path,
            "--label",
            "type:chore,priority:medium",
        )
        if create_result.returncode != 0:
            print(f"ERROR: gh issue create failed: {create_result.stderr}", file=sys.stderr)
            return 1

        print(create_result.stdout.strip())
        return 0
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
