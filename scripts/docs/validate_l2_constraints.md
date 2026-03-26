# `validate\_l2\_constraints`

scripts/validate_l2_constraints.py
-----------------------------------
Validates data/l2-constraints.yml against the L2 constraints JSON Schema.

Purpose:
    Ensures the L2 constraints YAML file conforms to the expected schema.
    Run this before committing changes to data/l2-constraints.yml to catch
    structural errors early (Programmatic-First, Enforcement-Proximity).

Inputs:
    Positional argument: path to the YAML file to validate
    (default: data/l2-constraints.yml)

Outputs:
    Prints "VALID: <path>" on success.
    Prints schema violation details on failure.

Usage example:
    uv run python scripts/validate_l2_constraints.py data/l2-constraints.yml
    uv run python scripts/validate_l2_constraints.py  # uses default path

Exit codes:
    0 — file is valid
    1 — schema violation
    2 — file not found or YAML parse error

References:
    - AGENTS.md § Guardrails
    - data/l2-constraints.yml

## Usage

```bash
    uv run python scripts/validate_l2_constraints.py data/l2-constraints.yml
    uv run python scripts/validate_l2_constraints.py  # uses default path
```

<!-- hash:3696ccaf49135dd6 -->
