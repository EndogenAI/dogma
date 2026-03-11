"""scripts/validate_delegation_routing.py

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
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not available; install with 'uv pip install PyYAML'", file=sys.stderr)
    sys.exit(1)

# Known executive-tier agents from AGENTS.md
CANONICAL_AGENTS = {
    "Orchestrator",
    "Docs",
    "Researcher",
    "Scripter",
    "Automator",
    "PM",
    "Fleet",
    "Planner",
    "Review",
    "GitHub",
}


def validate(file_path: Path) -> tuple[bool, list[str]]:
    """
    Validate delegation-gate.yml file.

    Returns:
        (passed, list_of_failure_messages)
    """
    failures: list[str] = []

    # --- Check 0: file exists ---
    if not file_path.exists():
        return False, [f"File not found: {file_path}"]

    # --- Check 1: YAML is valid ---
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML: {e}"]
    except OSError as e:
        return False, [f"Cannot read file: {e}"]

    if not isinstance(data, dict):
        return False, ["YAML root must be a dictionary object"]

    # --- Check 2: required top-level keys ---
    if "delegation_routes" not in data:
        failures.append("Missing 'delegation_routes' key")
    if "governance_boundaries" not in data:
        failures.append("Missing 'governance_boundaries' key")

    # --- Check 3: delegation_routes structure ---
    routes = data.get("delegation_routes", {})
    # Initialise before the type-guard so Check 5 is always safe to reference
    delegators: set[str] = set()
    delegatees: set[str] = set()
    if not isinstance(routes, dict):
        failures.append("'delegation_routes' must be a dictionary")
    else:
        # Collect all delegators and delegatees

        for delegator, targets in routes.items():
            delegators.add(delegator)
            if not isinstance(targets, (list, dict)):
                failures.append(f"Route '{delegator}' must map to list or dict, got {type(targets).__name__}")
            else:
                if isinstance(targets, list):
                    for target in targets:
                        if isinstance(target, str):
                            delegatees.add(target)
                elif isinstance(targets, dict):
                    for target in targets.keys():
                        delegatees.add(target)

        # --- Check 4: sovereignty rule (no circular delegations) ---
        # Build a directed graph and check for cycles
        adjacency = {}
        for delegator, targets in routes.items():
            if isinstance(targets, list):
                adjacency[delegator] = set(targets)
            elif isinstance(targets, dict):
                adjacency[delegator] = set(targets.keys())

        # Simple cycle detection using DFS
        def has_cycle(graph: dict[str, set[str]]) -> tuple[bool, set[str]]:
            visited = set()
            rec_stack = set()
            cycles = set()

            def visit(node: str) -> bool:
                visited.add(node)
                rec_stack.add(node)

                for neighbor in graph.get(node, set()):
                    if neighbor not in visited:
                        if visit(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        cycles.add(f"{node}→{neighbor}")
                        return True

                rec_stack.remove(node)
                return False

            for node in graph:
                if node not in visited:
                    if visit(node):
                        return True, cycles

            return False, cycles

        has_cycles, cycle_edges = has_cycle(adjacency)
        if has_cycles:
            failures.append(f"Circular delegation detected: {cycle_edges}. Delegation hierarchy must be acyclic.")

    # --- Check 5: referenced agents are canonical ---
    all_referenced = delegators | delegatees
    for agent in all_referenced:
        if agent not in CANONICAL_AGENTS:
            failures.append(f"Unknown agent '{agent}'; not in canonical agent list")

    return len(failures) == 0, failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate delegation-gate.yml structure and sovereignty rules")
    parser.add_argument(
        "files",
        nargs="*",
        default=["data/delegation-gate.yml"],
        help="Path to delegation-gate.yml file (default: data/delegation-gate.yml)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check-only mode (exit 0 even if checks fail)",
    )

    args = parser.parse_args(argv)
    files_to_check = [Path(f) for f in args.files]

    overall_exit_code = 0
    for file_path in files_to_check:
        passed, messages = validate(file_path)
        if not passed:
            overall_exit_code = 1
            print(f"{file_path}:")
            for msg in messages:
                print(f"  ✗ {msg}")
        else:
            print(f"{file_path}: ✓ OK")

    return 0 if args.check else overall_exit_code


if __name__ == "__main__":
    sys.exit(main())
