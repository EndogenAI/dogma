"""
enrich_research_issues.py — Detect and enrich bare-bones type:research GitHub issues.

Bare-bones heuristic: body length ≤ 300 chars AND no "## Acceptance Criteria" heading.

Usage:
    uv run python scripts/enrich_research_issues.py --dry-run   # inspect only (default)
    uv run python scripts/enrich_research_issues.py --apply     # post enrichment comment

Exit codes:
    0 — completed (0 or more issues found)
    1 — GitHub API error or authentication failure
    2 — script usage error (bad args)
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]

BARE_BONES_MAX_BODY = 300
ACCEPTANCE_CRITERIA_HEADING = "## Acceptance Criteria"

ENRICHMENT_COMMENT = """\
## Enrichment Prompt

This issue appears to be a bare-bones research note. To run a full secondary research
sprint, follow the workflow in `.github/skills/secondary-research-sprint/SKILL.md`:

1. Fetch the URL and update this issue body with a summary, key claims, and acceptance
   criteria (Step 1 of the skill)
2. Run corpus check (`scripts/query_docs.py`) before scouting (Step 2)
3. Produce a D4 synthesis doc at `docs/research/<slug>.md` (Steps 3-4)
4. Close this issue after synthesis is committed (Step 5)

**Auto-detected as bare-bones** (body ≤ 300 chars, no acceptance criteria).
"""


def fetch_research_issues() -> list[dict]:
    """Fetch open type:research issues via gh CLI. Returns list of issue dicts."""
    result = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--label",
            "type:research",
            "--state",
            "open",
            "--json",
            "number,title,body,labels",
            "--limit",
            "100",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def filter_bare_bones(issues: list[dict]) -> list[dict]:
    """Return issues matching the bare-bones heuristic."""
    result = []
    for issue in issues:
        body = issue.get("body") or ""
        if len(body) <= BARE_BONES_MAX_BODY and ACCEPTANCE_CRITERIA_HEADING not in body:
            result.append(issue)
    return result


def post_enrichment_comment(issue_number: int) -> None:
    """Post the enrichment comment on a single issue."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".md",
        prefix="enrich_",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(ENRICHMENT_COMMENT)
        tmp_path = tmp.name

    # Validate temp file is non-empty before posting
    if not Path(tmp_path).stat().st_size:
        print(f"  ERROR: temp file is empty for issue #{issue_number}", file=sys.stderr)
        Path(tmp_path).unlink(missing_ok=True)
        return

    subprocess.run(
        ["gh", "issue", "comment", str(issue_number), "--body-file", tmp_path],
        check=True,
    )
    Path(tmp_path).unlink(missing_ok=True)
    print(f"  ✓ Posted enrichment comment on #{issue_number}")


def print_dry_run_table(issues: list[dict]) -> None:
    """Print a formatted table of bare-bones issues."""
    if not issues:
        print("No bare-bones type:research issues found.")
        return
    print(f"{'#':<8} {'Title'}")
    print("-" * 60)
    for issue in issues:
        print(f"#{issue['number']:<7} {issue['title']}")
    print(f"\nTotal: {len(issues)} bare-bones issue(s) found.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Detect and enrich bare-bones type:research GitHub issues.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print matching issues without posting comments (default)",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Post enrichment comment on each bare-bones issue",
    )
    args = parser.parse_args(argv)

    # --apply overrides the dry-run default
    dry_run = not args.apply

    try:
        issues = fetch_research_issues()
    except subprocess.CalledProcessError as exc:
        print(
            f"ERROR: gh CLI failed (exit {exc.returncode}): {exc.stderr}",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: unexpected failure fetching issues: {exc}", file=sys.stderr)
        return 1

    bare_bones = filter_bare_bones(issues)

    if dry_run:
        print_dry_run_table(bare_bones)
        return 0

    # --apply mode
    if not bare_bones:
        print("No bare-bones type:research issues found. Nothing to do.")
        return 0

    print(f"Enriching {len(bare_bones)} bare-bones issue(s)...")
    for issue in bare_bones:
        num = issue["number"]
        title = issue["title"]
        print(f"  → #{num}: {title}")
        try:
            post_enrichment_comment(num)
        except subprocess.CalledProcessError as exc:
            print(
                f"  ERROR posting comment on #{num} (exit {exc.returncode})",
                file=sys.stderr,
            )
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
