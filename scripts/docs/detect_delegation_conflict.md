# `detect\_delegation\_conflict`

scripts/detect_delegation_conflict.py — Pre-delegation conflict detection.

Reads a proposed delegation scope and checks it against L2 constraints
(data/l2-constraints.yml) and decision-routing rules (data/decision-tables.yml).
Exits 0 when no conflicts are found, 1 when one or more constraint violations
are detected, and 2 on configuration errors (missing YAML files, parse errors).

Inputs:
    --scope  : str   — delegation scope description (required unless reading from stdin)
    --stdin  : flag  — read a JSON object {"scope": "..."} from stdin instead
    --data-dir: str  — directory containing decision-tables.yml and l2-constraints.yml
                       (default: data/ relative to repo root)

Outputs (stdout, JSON):
    {"safe": true, "conflicts": []}
    {"safe": false, "conflicts": [{"id": str, "description": str}, ...]}

Exit codes:
    0 — safe (no conflicts)
    1 — conflicts found
    2 — configuration error (missing file, YAML parse failure, bad input)

Usage examples:
    uv run python scripts/detect_delegation_conflict.py --scope "git push --force to main"
    echo '{"scope": "commit secrets to repo"}' | uv run python scripts/detect_delegation_conflict.py --stdin

## Usage

```bash
    uv run python scripts/detect_delegation_conflict.py --scope "git push --force to main"
    echo '{"scope": "commit secrets to repo"}' | uv run python scripts/detect_delegation_conflict.py --stdin
```

<!-- hash:8870ba88016107b8 -->
