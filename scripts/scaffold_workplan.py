"""
scaffold_workplan.py — Create a docs/plans/YYYY-MM-DD-<slug>.md workplan file from template.

Purpose:
    Scaffolds a new workplan file at docs/plans/YYYY-MM-DD-<slug>.md with today's date
    pre-filled, the current git branch embedded, and a standard multi-phase session
    template. Follows the workplan convention defined in AGENTS.md and
    docs/guides/session-management.md.

    The file is created only if it does not already exist. If it does, a warning is
    printed and the script exits without overwriting.

Inputs:
    <slug>  — Required positional argument. A dash-separated slug for the workplan,
              e.g. "formalize-workflows". The slug is converted to a title by replacing
              dashes with spaces and applying title-casing.

Outputs:
    docs/plans/YYYY-MM-DD-<slug>.md  — New workplan file at workspace root.
    Prints the created file path to stdout on success.

Usage:
    uv run python scripts/scaffold_workplan.py <slug>

    # Example
    uv run python scripts/scaffold_workplan.py formalize-workflows
    # Creates: docs/plans/2026-03-06-formalize-workflows.md

Exit codes:
    0 — success: file created
    1 — missing slug argument, file already exists, or cannot write target file
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

TEMPLATE = """\
# Workplan: {title}

**Branch**: `{branch}`
**Date**: {date}
**Orchestrator**: Executive Orchestrator

---

## Objective

<!-- One paragraph: what this session accomplishes -->

---

## Phase Plan

### Phase 1 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- <!-- list deliverables -->

**Depends on**: nothing
**Status**: Not started

---

## Acceptance Criteria

- [ ] All phases complete and committed
- [ ] All changes pushed and PR is up to date
"""


def _git_branch() -> str:
    """Return current git branch, or 'unknown' on failure."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            if branch:
                return branch
    except Exception:
        pass
    return "unknown"


def slug_to_title(slug: str) -> str:
    """Convert a dash-separated slug to a title-cased string."""
    return slug.replace("-", " ").title()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a docs/plans/YYYY-MM-DD-<slug>.md workplan file from template."
    )
    parser.add_argument(
        "slug",
        help="Dash-separated slug for the workplan, e.g. formalize-workflows",
    )
    args = parser.parse_args()

    slug = args.slug.strip().lower()
    if not slug:
        print("ERROR: slug must not be empty.", file=sys.stderr)
        return 1

    today = date.today().isoformat()
    branch = _git_branch()
    title = slug_to_title(slug)

    root = Path(__file__).parent.parent
    plans_dir = root / "docs" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{today}-{slug}.md"
    target = plans_dir / filename

    if target.exists():
        print(
            f"WARNING: {target.relative_to(root)} already exists. "
            "Remove it manually if you want to regenerate.",
            file=sys.stderr,
        )
        return 1

    content = TEMPLATE.format(title=title, branch=branch, date=today)
    target.write_text(content, encoding="utf-8")

    rel = target.relative_to(root)
    print(f"Created: {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
