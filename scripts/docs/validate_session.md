# `validate\_session`

scripts/validate_session.py

Post-commit scratchpad audit validator for session files.

Purpose:
    Enforce a minimum structural bar on session scratchpad files (.tmp/*/*.md)
    to prevent encoding drift during multi-phase sessions. Validates that
    critical session metadata and checkpoint records are present.

Checks (7-point audit):
    1. ## Session Start present (mandatory session initialization).
    2. ## Session Start contains governing axiom citation (checks for "Governing axiom:" pattern).
    3. ## Session Start contains endogenous source citation (checks for MANIFESTO.md, AGENTS.md,
       docs/, or scripts/ references).
    4. ## Orchestration Plan present (tracks phases scheduled for this session).
    5. Phase records tracked (all planned phases have ### Phase N headings).
    6. Pre-Compact Checkpoint present (mandatory pre-compaction marker).
    7. ## Session Summary present (mandatory session close marker).

Inputs:
    [file ...]  One or more session .md files to audit (positional, optional).
    --all       Scan all session files in .tmp/*/*.md.
    --branch    Only scan files on the current git branch.

Outputs:
    stdout:  Human-readable pass/fail summary with specific gap list per file.

Exit codes:
    0  All checks passed.
    1  One or more structural checks failed.
    2  Encoding drift detected (e.g., axiom not explicitly cited, source not linked).

Usage examples:
    # Validate a single session file
    uv run python scripts/validate_session.py .tmp/feat-branch/2026-03-11.md

    # Validate all session files
    uv run python scripts/validate_session.py --all

    # Validate only current branch
    uv run python scripts/validate_session.py --branch

## Usage

```bash
    # Validate a single session file
    uv run python scripts/validate_session.py .tmp/feat-branch/2026-03-11.md

    # Validate all session files
    uv run python scripts/validate_session.py --all

    # Validate only current branch
    uv run python scripts/validate_session.py --branch
```

<!-- hash:874e21e4992f4234 -->
