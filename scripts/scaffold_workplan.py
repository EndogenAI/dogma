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
    <slug>       — Required positional argument. A dash-separated slug for the workplan,
                   e.g. "formalize-workflows". The slug is converted to a title by replacing
                   dashes with spaces and applying title-casing.
    --ci          — Optional. Comma-separated CI values (e.g. "Tests,Auto-validate").
                    Overrides the default value.
    --issues      — Optional. Comma-separated issue numbers (e.g. "42,43").
                    Overrides the default (no linked issues).
    --interactive — Optional. Prompt for missing CI and issue values interactively.
                    By default the script runs silently using built-in defaults.

Outputs:
    docs/plans/YYYY-MM-DD-<slug>.md  — New workplan file at workspace root.
    Prints the created file path to stdout on success.

Usage:
    # Non-interactive (agent-safe default):
    uv run python scripts/scaffold_workplan.py formalize-workflows
    # Creates: docs/plans/2026-03-06-formalize-workflows.md using built-in defaults

    # With explicit values (preferred for agents):
    uv run python scripts/scaffold_workplan.py formalize-workflows --ci "Tests,Auto-validate" --issues "42,43"

    # Interactive (human use only):
    uv run python scripts/scaffold_workplan.py formalize-workflows --interactive

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

ALLOWED_CI_VALUES: frozenset[str] = frozenset({"Tests", "Auto-validate", "Lint"})
DEFAULT_CI = "Tests, Auto-validate"


def _get_root() -> Path:
    """Return the workspace root (parent of scripts/).  Monkeypatched in tests."""
    return Path(__file__).resolve().parent.parent


def _prompt(msg: str, default: str) -> str:
    """Display *msg* and return user input, or *default* if non-interactive or empty.

    Non-interactive detection: ``sys.stdin.isatty()`` returns False (e.g. CI or tests).
    """
    if not sys.stdin.isatty():
        return default
    response = input(msg).strip()
    return response if response else default


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
**CI**: {ci}
**Status**: Not started

### Phase 2 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- <!-- list deliverables -->

**Depends on**: Phase 1
**CI**: {ci}
**Status**: Not started

### Phase 3 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- <!-- list deliverables -->

**Depends on**: Phase 2
**CI**: {ci}
**Status**: Not started

### Phase 4 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- <!-- list deliverables -->

**Depends on**: Phase 3
**CI**: {ci}
**Status**: Not started

### Phase 5 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- Fleet integration (if adding new agents/skills: run `uv run python scripts/check_fleet_integration.py --dry-run`)
- Session startup integration (archive session, update scratchpad summary)
- <!-- add other deliverables -->

**Depends on**: Phase 4
**CI**: {ci}
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
    parser.add_argument(
        "--ci",
        type=str,
        default=None,
        help="Comma-separated CI values (e.g. 'Tests,Auto-validate'). Bypasses interactive prompt.",
    )
    parser.add_argument(
        "--issues",
        type=str,
        default=None,
        help="Comma-separated issue numbers (e.g. '42,43'). Overrides the default (no linked issues).",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        default=False,
        help="Prompt for missing CI and issue values interactively. Default: use built-in defaults silently.",
    )
    args = parser.parse_args()

    slug = args.slug.strip().lower()
    if not slug:
        print("ERROR: slug must not be empty.", file=sys.stderr)
        return 1

    today = date.today().isoformat()
    branch = _git_branch()
    title = slug_to_title(slug)

    # --- CI strategy: flag, interactive prompt, or silent default ---
    if args.ci is not None:
        ci_raw = args.ci
    elif args.interactive:
        ci_raw = _prompt(
            f"CI options (comma-separated, choose from: Tests, Auto-validate, Lint) [{DEFAULT_CI}]: ",
            DEFAULT_CI,
        )
    else:
        ci_raw = DEFAULT_CI
    ci_tokens = [t.strip() for t in ci_raw.split(",") if t.strip()]
    invalid_ci = [t for t in ci_tokens if t not in ALLOWED_CI_VALUES]
    if invalid_ci:
        print(f"ERROR: invalid CI values: {invalid_ci}. Allowed: Tests, Auto-validate, Lint.", file=sys.stderr)
        return 1
    ci_value = ", ".join(ci_tokens) if ci_tokens else DEFAULT_CI

    # --- Linked issues: flag, interactive prompt, or silent default ---
    if args.issues is not None:
        issues_raw = args.issues
    elif args.interactive:
        issues_raw = _prompt("Linked issue numbers (comma-separated, e.g. 42,43) [none]: ", "")
    else:
        issues_raw = ""
    issue_numbers: list[int] = []
    if issues_raw.strip():
        invalid_issues: list[str] = []
        for token in issues_raw.split(","):
            token = token.strip()
            if token:
                try:
                    value = int(token)
                    if value <= 0:
                        invalid_issues.append(token)
                    else:
                        issue_numbers.append(value)
                except ValueError:
                    invalid_issues.append(token)
        # Deduplicate while preserving order
        issue_numbers = list(dict.fromkeys(issue_numbers))
        if invalid_issues:
            print(f"ERROR: issue numbers must be positive integers: {invalid_issues}", file=sys.stderr)
            return 1

    root = _get_root()
    plans_dir = root / "docs" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{today}-{slug}.md"
    target = plans_dir / filename

    if target.exists():
        print(
            f"WARNING: {target.relative_to(root)} already exists. Remove it manually if you want to regenerate.",
            file=sys.stderr,
        )
        return 1

    content = TEMPLATE.format(title=title, branch=branch, date=today, ci=ci_value)
    if issue_numbers:
        closes = ", ".join(f"Closes #{n}" for n in issue_numbers)
        content += f"\n## PR Description Template\n\n<!-- Copy to PR description when opening the PR -->\n\n{closes}\n"
    target.write_text(content, encoding="utf-8")

    rel = target.relative_to(root)
    print(f"Created: {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
