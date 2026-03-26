# `validate\_session\_state`

scripts/validate_session_state.py

Validator for Phase/gate transitions in scratchpad session files, and YAML
phase-status block parser for structured session state tracking.

Purpose:
    Two modes of operation:

    1. FSM validation (default): Enforce proper sequencing of phase execution
       and review gates. Detects phase skipping, missing review gates between
       domains, and FSM violations.

    2. YAML phase-status (--yaml-state): Parse the ## Session State YAML block
       written by prune_scratchpad.py --init, validate its structure, and print
       a human-readable phase status table.

Checks (FSM mode):
    1. All phases follow numerically (no skipping: 1→2→3, not 1→3).
    2. Each Phase N is followed by a Review gate before proceeding to next domain.
    3. No duplicate phases.
    4. Session contains at least Phase 1 (session started).

YAML block schema (--yaml-state, Candidate C extended):
    branch:        string
    date:          string or null  (optional, ISO date)
    active_phase:  string or null
    active_issues: list            (optional, GitHub issue numbers)
    blockers:      list            (optional, open blocker strings)
    last_agent:    string or null  (optional, last delegated agent)
    phases:        list of {name: str, status: str, commit: str}

Inputs:
    [file ...]         Path to session .md file (positional, optional).
    --yaml-state       Parse and display the ## Session State YAML block.

Outputs:
    stdout: Human-readable pass/fail summary (FSM) or phase table (--yaml-state).

Exit codes:
    0  All checks passed / YAML block valid.
    1  One or more checks failed / YAML block missing or malformed.

Usage examples:
    uv run python scripts/validate_session_state.py .tmp/branch/2026-03-11.md
    uv run python scripts/validate_session_state.py --yaml-state .tmp/branch/2026-03-16.md

## Usage

```bash
    uv run python scripts/validate_session_state.py .tmp/branch/2026-03-11.md
    uv run python scripts/validate_session_state.py --yaml-state .tmp/branch/2026-03-16.md
```

<!-- hash:d37db911c05d24b4 -->
