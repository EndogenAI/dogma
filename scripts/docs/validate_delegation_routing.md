# `validate\_delegation\_routing`

scripts/validate_delegation_routing.py

Validator for data/delegation-gate.yml structure and sovereignty rules.

Purpose:
    Enforce integrity of the delegation routing table and verify that no
    agent/executive is both delegator and delegatee (sovereignty principle).

Checks:
    1. YAML file is valid and parseable.
    2. Has 'delegation_routes' and 'governance_boundaries' top-level keys.
    3. delegation_routes contains valid delegation patterns (from → to agents).
    4. No agent appears as both delegator and delegatee (sovereignty rule).
    5. All referenced agents exist in canonical agent list.

Inputs:
    [file ...]  Path to delegation-gate.yml file (positional, optional).
    --check     If provided, run in check-only mode (exit 0 even if fails).

Outputs:
    stdout: Human-readable pass/fail summary with gap list.

Exit codes:
    0  All checks passed.
    1  One or more checks failed.

Usage examples:
    uv run python scripts/validate_delegation_routing.py data/delegation-gate.yml
    uv run python scripts/validate_delegation_routing.py --check data/delegation-gate.yml

## Usage

```bash
    uv run python scripts/validate_delegation_routing.py data/delegation-gate.yml
    uv run python scripts/validate_delegation_routing.py --check data/delegation-gate.yml
```

<!-- hash:1fbbed9348fd424d -->
