# `scaffold\_workplan`

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

## Usage

```bash
    # Non-interactive (agent-safe default):
    uv run python scripts/scaffold_workplan.py formalize-workflows
    # Creates: docs/plans/2026-03-06-formalize-workflows.md using built-in defaults

    # With explicit values (preferred for agents):
    uv run python scripts/scaffold_workplan.py formalize-workflows --ci "Tests,Auto-validate" --issues "42,43"

    # Interactive (human use only):
    uv run python scripts/scaffold_workplan.py formalize-workflows --interactive
```

<!-- hash:19868640e020674e -->
