# `validate\_cascade`

validate_cascade.py — Validate T1→T5 governance cascade encoding for a client deployment.

Purpose:
    Checks that the encoding chain (MANIFESTO → AGENTS.md → agents → skills → session)
    is intact and that each tier references its parent tier. Implements
    client-manifesto-adoption-pattern.md Recommendation 2.

Inputs:
    --tier <1-5>           : Run only this tier's check (default: all)
    files                  : Optional paths (for tier 1: client-values.yml path)
    --repo-root <path>     : Repo root (default: cwd)
    --strict               : Exit 1 on any gap (default: advisory, exits 0)

Outputs:
    Prints per-tier status: PASS / WARN / FAIL
    Exit 0 if no FAIL; exit 1 if --strict and any WARN/FAIL; exit 1 if any FAIL

Usage:
    uv run python scripts/validate_cascade.py
    uv run python scripts/validate_cascade.py --tier 1 client-values.yml
    uv run python scripts/validate_cascade.py --strict

## Usage

```bash
    uv run python scripts/validate_cascade.py
    uv run python scripts/validate_cascade.py --tier 1 client-values.yml
    uv run python scripts/validate_cascade.py --strict
```

<!-- hash:1c110d69e4c3d691 -->
