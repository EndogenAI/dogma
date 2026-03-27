# `substrate\_distiller\_legacy`

Distill governance/rationale signals from Python sources.

Extracts substrate metadata from module, class, and function docstrings using the
Python AST and computes RDI (Rationale Density Indicator):

    RDI = rationale_token_count / max(implementation_token_count, 1)

Inputs:
- --path: Python file or directory to scan recursively for *.py files
- --format: json | markdown | table
- --threshold: debt threshold for RDI violations
- --fail-on-debt: return exit code 1 when violations are present
- --include-private: include private classes/functions (leading underscore)
- --summary-only: emit summary only

Outputs:
- Structured records containing x-governs, intent/rationale blocks, RDI, and status
- Human-readable table/markdown or machine-readable JSON

Exit codes:
- 0: success (or no violations)
- 1: violations present when --fail-on-debt is set
- 2: invalid args, path errors, or Python parse errors

Usage examples:
    uv run python scripts/substrate_distiller.py --path scripts --format json
    uv run python scripts/substrate_distiller.py --path scripts --fail-on-debt

## Usage

```bash
    uv run python scripts/substrate_distiller.py --path scripts --format json
    uv run python scripts/substrate_distiller.py --path scripts --fail-on-debt
```

<!-- hash:6480c9e6e0b0d585 -->
