"""scripts/detect_delegation_conflict.py — Pre-delegation conflict detection.

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
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import]
except ModuleNotFoundError:  # pragma: no cover
    print(
        json.dumps({"safe": False, "conflicts": [], "error": "PyYAML not installed"}),
        flush=True,
    )
    sys.exit(2)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_DATA_DIR = _REPO_ROOT / "data"

# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

# Keywords mapped to constraint IDs from l2-constraints.yml.
# A scope string containing any keyword triggers the associated constraint check.
_SCOPE_KEYWORDS: list[tuple[list[str], str]] = [
    (["force", "force push", "--force"], "no-force-push-to-main"),
    (["heredoc", "<< 'eof'", "<<'eof'", "cat >>", "cat >"], "no-heredoc-writes"),
    ([">> file", "> file", "| tee", "| cat >>"], "no-terminal-file-io-redirect"),
    (["secret", "api key", "token", "credential", "password", "bearer"], "no-secrets-in-commits"),
    (["lockfile", "uv.lock", "package-lock"], "no-lockfile-hand-edits"),
    (['--body "', ' --body "', "--body '"], "no-multi-line-gh-body"),
]


def _load_yaml(path: Path) -> object:
    """Load a YAML file, raising ValueError on parse errors."""
    try:
        with path.open(encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML parse error in {path}: {exc}") from exc


def _build_constraint_index(data_dir: Path) -> dict[str, dict]:
    """Load l2-constraints.yml and return a dict keyed by constraint id."""
    path = data_dir / "l2-constraints.yml"
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    data = _load_yaml(path)
    if not isinstance(data, dict) or "constraints" not in data:
        raise ValueError(f"Unexpected schema in {path}: expected top-level 'constraints' key")
    index: dict[str, dict] = {}
    for entry in data["constraints"]:
        if isinstance(entry, dict) and "id" in entry:
            index[entry["id"]] = entry
    return index


def _build_decision_index(data_dir: Path) -> list[dict]:
    """Load decision-tables.yml and return the list of decision entries."""
    path = data_dir / "decision-tables.yml"
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    data = _load_yaml(path)
    if not isinstance(data, dict) or "decision_tables" not in data:
        raise ValueError(f"Unexpected schema in {path}: expected top-level 'decision_tables' key")
    return [e for e in data["decision_tables"] if isinstance(e, dict)]


def detect_conflicts(
    scope: str,
    data_dir: Path,
) -> tuple[bool, list[dict]]:
    """Detect constraint violations for the given delegation scope.

    Returns (safe: bool, conflicts: list[{"id": str, "description": str}]).
    """
    constraint_index = _build_constraint_index(data_dir)
    # decision_tables loaded for potential future keyword matching; currently
    # constraint matching drives detection.
    _build_decision_index(data_dir)

    scope_lower = scope.lower()
    conflicts: list[dict] = []
    seen_ids: set[str] = set()

    for keywords, constraint_id in _SCOPE_KEYWORDS:
        if constraint_id in seen_ids:
            continue
        if any(kw in scope_lower for kw in keywords):
            if constraint_id in constraint_index:
                entry = constraint_index[constraint_id]
                description = entry.get("description", "").strip().replace("\n", " ")
                conflicts.append({"id": constraint_id, "description": description})
                seen_ids.add(constraint_id)

    return (len(conflicts) == 0, conflicts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect pre-delegation constraint conflicts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--scope", help="Delegation scope description string.")
    group.add_argument(
        "--stdin",
        action="store_true",
        help='Read JSON {"scope": "..."} from stdin.',
    )
    parser.add_argument(
        "--data-dir",
        default=str(_DEFAULT_DATA_DIR),
        help="Directory containing decision-tables.yml and l2-constraints.yml.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    data_dir = Path(args.data_dir)

    # Resolve scope string
    if args.stdin:
        try:
            payload = json.load(sys.stdin)
            scope = payload.get("scope", "")
        except (json.JSONDecodeError, AttributeError) as exc:
            print(json.dumps({"safe": False, "conflicts": [], "error": f"Invalid JSON input: {exc}"}))
            return 2
    elif args.scope:
        scope = args.scope
    else:
        print(json.dumps({"safe": False, "conflicts": [], "error": "Provide --scope or --stdin."}))
        return 2

    if not scope.strip():
        print(json.dumps({"safe": False, "conflicts": [], "error": "Scope string is empty."}))
        return 2

    try:
        safe, conflicts = detect_conflicts(scope, data_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(json.dumps({"safe": False, "conflicts": [], "error": str(exc)}))
        return 2

    print(json.dumps({"safe": safe, "conflicts": conflicts}))
    return 0 if safe else 1


if __name__ == "__main__":
    sys.exit(main())
