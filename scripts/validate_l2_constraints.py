"""
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
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("Error: jsonschema is required. Install with: pip install jsonschema")
    sys.exit(1)
import yaml

_DEFAULT_PATH = Path(__file__).parent.parent / "data" / "l2-constraints.yml"

# JSON Schema for data/l2-constraints.yml
_SCHEMA: dict = {
    "type": "object",
    "required": ["constraints"],
    "additionalProperties": True,
    "properties": {
        "constraints": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id", "description", "enforcement", "severity"],
                "additionalProperties": True,
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "description": {"type": "string", "minLength": 1},
                    "enforcement": {
                        "type": "string",
                        "enum": ["pre-commit", "runtime", "review"],
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["blocking", "warning"],
                    },
                },
            },
        }
    },
}


def validate(path: Path) -> int:
    """Validate *path* against the L2 constraints schema.

    Returns:
        0 on success, 1 on schema violation, 2 on missing/unparseable file.
    """
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        return 2

    try:
        with path.open() as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        print(f"ERROR: YAML parse error in {path}: {exc}", file=sys.stderr)
        return 2

    try:
        jsonschema.validate(instance=data, schema=_SCHEMA)
    except jsonschema.ValidationError as exc:
        print(f"INVALID: {path}", file=sys.stderr)
        print(f"  Path:    {' -> '.join(str(p) for p in exc.absolute_path)}", file=sys.stderr)
        print(f"  Message: {exc.message}", file=sys.stderr)
        return 1
    except jsonschema.SchemaError as exc:
        print(f"ERROR: Internal schema error: {exc.message}", file=sys.stderr)
        return 1

    print(f"VALID: {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate data/l2-constraints.yml against JSON Schema.")
    parser.add_argument(
        "path",
        nargs="?",
        default=str(_DEFAULT_PATH),
        help="Path to YAML file to validate (default: data/l2-constraints.yml).",
    )
    args = parser.parse_args(argv)
    return validate(Path(args.path))


if __name__ == "__main__":
    sys.exit(main())
