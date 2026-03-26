# `check\_fleet\_integration`

check_fleet_integration.py — Validate that new agents and skills are documented in AGENTS.md.

Purpose:
    Reads new files from git diff (agents, skills), checks that they are cross-referenced
    in AGENTS.md, and warns if new files lack proper documentation or linkage. Implements
    the Fleet Integration Checklist as a programmatic gate.

Inputs:
    --branch <branch>  — Optional. Git branch to compare against (default: main).
    --dry-run          — Optional. Show what would be validated without modifying state.

Outputs:
    Prints a summary of findings to stdout:
    - List of new agent/skill files detected
    - List of agents properly referenced in AGENTS.md
    - List of integration gaps (new files not referenced)
    Exit code 0 if all new files are documented; exit code 1 if gaps found.

Usage:
    # Non-interactive (default):
    uv run python scripts/check_fleet_integration.py

    # Against a specific branch:
    uv run python scripts/check_fleet_integration.py --branch main

    # Dry-run to preview findings:
    uv run python scripts/check_fleet_integration.py --dry-run

Exit codes:
    0 — success: all new files are integrated
    1 — integration gaps found or invalid arguments
    2 — git error or file I/O error

## Usage

```bash
    # Non-interactive (default):
    uv run python scripts/check_fleet_integration.py

    # Against a specific branch:
    uv run python scripts/check_fleet_integration.py --branch main

    # Dry-run to preview findings:
    uv run python scripts/check_fleet_integration.py --dry-run
```

<!-- hash:a60c02f06f6fdc9c -->
