# `audit\_structural\_compliance`

scripts/audit_structural_compliance.py

Audit `.agent.md` files for mandatory BDI XML wrappers and heading alignment.

Inputs:
    --target-dir: directory to scan (default `.github/agents/`)
    --format: `text` or `json`

Outputs:
    Report of files with missing tag pairs or misaligned section headings.

Usage:
    uv run python scripts/audit_structural_compliance.py
    uv run python scripts/audit_structural_compliance.py --format json

## Usage

```bash
    uv run python scripts/audit_structural_compliance.py
    uv run python scripts/audit_structural_compliance.py --format json
```

<!-- hash:5d46b21528b4e5eb -->
