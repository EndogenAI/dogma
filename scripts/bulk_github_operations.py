"""
scripts/bulk_github_operations.py — Batch GitHub issue/PR write operations.

Purpose
-------
Execute a list of GitHub issue and PR write operations (create, edit, close)
from a structured spec file, with rate-limit throttling between calls.
All operations route through the ``gh`` CLI via subprocess with list-of-args
(never shell=True). A ``--dry-run`` flag prints every planned command without
executing any ``gh`` calls — mandatory safety gate before a bulk run.

Inputs
------
- Operation spec: JSON or YAML file passed via ``--input FILE``, or JSON
  piped to stdin. Each operation is a dict with keys:
  - ``op``: one of ``issue-create``, ``issue-edit``, ``issue-close``, ``pr-edit``
  - ``target``: issue/PR number (integer), or null for ``issue-create``
  - ``params``: dict of operation-specific parameters (see below)

  Supported params per operation:

  issue-create  title (str), body (str), labels (list[str]),
                milestone (str|int), assignee (str)
  issue-edit    add-labels (list[str]), remove-labels (list[str]),
                labels (list[str] — alias for add-labels),
                milestone (str|int), assignee (str)
  issue-close   (no params required)
  pr-edit       add-labels (list[str]), remove-labels (list[str]),
                labels (list[str] — alias for add-labels),
                milestone (str|int), assignee (str)

Outputs
-------
- stdout: JSON array of result objects, one per operation::

    [{"op": "issue-close", "target": 42, "status": "ok", "error": null}, ...]

  Dry-run results have ``status == "dry-run"`` and include a ``"cmd"`` field
  showing the exact command that *would* be run.
- stderr: one progress line per operation (``[OK]``, ``[FAIL]``, ``[DRY-RUN]``)

Flags
-----
--input PATH          JSON or YAML file containing the operation list.
                      Omit to read JSON from stdin.
--dry-run             Print planned commands; make no gh calls. Exit 0.
--rate-limit-delay N  Seconds to sleep between operations. Default: 0.5.
--help                Show this help and exit.

Exit codes
----------
0  All operations succeeded (or --dry-run completed).
1  One or more operations failed.
2  Invalid input (parse error, unknown op type, missing required param).

Usage examples
--------------
# Dry-run from a JSON spec file
uv run python scripts/bulk_github_operations.py --input ops.json --dry-run

# Execute from a YAML spec file with 1 s between ops
uv run python scripts/bulk_github_operations.py --input ops.yaml --rate-limit-delay 1.0

# Pipe JSON spec from stdin
echo '[{"op":"issue-close","target":99,"params":{}}]' | \\
    uv run python scripts/bulk_github_operations.py --dry-run

# Dry-run, then re-run for real (two-step safety pattern)
uv run python scripts/bulk_github_operations.py --input ops.json --dry-run
uv run python scripts/bulk_github_operations.py --input ops.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_OPS = frozenset({"issue-create", "issue-edit", "issue-close", "pr-edit"})

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Batch GitHub issue/PR write operations with rate-limit throttling.",
    )
    parser.add_argument(
        "--input",
        metavar="FILE",
        default=None,
        help="JSON or YAML file containing the operation list. Omit to read JSON from stdin.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print planned commands without executing any gh calls. Exit 0.",
    )
    parser.add_argument(
        "--rate-limit-delay",
        type=float,
        default=0.5,
        metavar="SECONDS",
        help="Seconds to sleep between operations (default: 0.5).",
    )
    return parser


# ---------------------------------------------------------------------------
# Input loading
# ---------------------------------------------------------------------------


def _load_operations(input_path: str | None) -> list[dict[str, Any]]:
    """Load operation spec from file (JSON or YAML) or stdin (JSON only).

    Returns the parsed list of operation dicts.
    Raises ValueError with a human-readable message on parse errors.
    """
    if input_path is not None:
        path = Path(input_path)
        if not path.exists():
            raise ValueError(f"Input file not found: {input_path}")
        raw = path.read_text(encoding="utf-8")
        suffix = path.suffix.lower()
        if suffix in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore[import]

                data = yaml.safe_load(raw)
            except Exception as exc:
                raise ValueError(f"YAML parse error in {input_path}: {exc}") from exc
        else:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON parse error in {input_path}: {exc}") from exc
    else:
        raw = sys.stdin.read()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON parse error reading stdin: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError("Operation spec must be a JSON/YAML array (list) of operation dicts.")
    return data


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_operations(ops: list[dict[str, Any]]) -> list[str]:
    """Return a list of validation error messages (empty = valid)."""
    errors: list[str] = []
    for i, op_spec in enumerate(ops):
        if not isinstance(op_spec, dict):
            errors.append(f"Operation {i}: must be a dict, got {type(op_spec).__name__}")
            continue
        op = op_spec.get("op")
        if not op:
            errors.append(f"Operation {i}: missing required key 'op'")
            continue
        if op not in VALID_OPS:
            errors.append(f"Operation {i}: unknown op '{op}'. Valid ops: {sorted(VALID_OPS)}")
            continue
        target = op_spec.get("target")
        if op != "issue-create" and target is None:
            errors.append(f"Operation {i} ({op}): 'target' (issue/PR number) is required")
            continue
        params = op_spec.get("params", {})
        if op == "issue-create" and not params.get("title"):
            errors.append(f"Operation {i} (issue-create): 'params.title' is required")
    return errors


# ---------------------------------------------------------------------------
# Command building
# ---------------------------------------------------------------------------


def _build_gh_cmd(op_spec: dict[str, Any]) -> list[str]:
    """Build a gh CLI command list for one operation dict.

    Does NOT validate — call _validate_operations first.
    """
    op = op_spec["op"]
    target = op_spec.get("target")
    params = op_spec.get("params", {}) or {}

    if op == "issue-create":
        cmd = ["gh", "issue", "create", "--title", params["title"]]
        if "body" in params:
            cmd += ["--body", params["body"]]
        for label in params.get("labels", []):
            cmd += ["--label", str(label)]
        if "milestone" in params:
            cmd += ["--milestone", str(params["milestone"])]
        if "assignee" in params:
            cmd += ["--assignee", str(params["assignee"])]
        return cmd

    if op == "issue-edit":
        cmd = ["gh", "issue", "edit", str(target)]
        # "labels" is an alias for "add-labels"
        add_labels = params.get("add-labels", params.get("labels", []))
        for label in add_labels:
            cmd += ["--add-label", str(label)]
        for label in params.get("remove-labels", []):
            cmd += ["--remove-label", str(label)]
        if "milestone" in params:
            cmd += ["--milestone", str(params["milestone"])]
        if "assignee" in params:
            cmd += ["--assignee", str(params["assignee"])]
        return cmd

    if op == "issue-close":
        return ["gh", "issue", "close", str(target)]

    if op == "pr-edit":
        cmd = ["gh", "pr", "edit", str(target)]
        add_labels = params.get("add-labels", params.get("labels", []))
        for label in add_labels:
            cmd += ["--add-label", str(label)]
        for label in params.get("remove-labels", []):
            cmd += ["--remove-label", str(label)]
        if "milestone" in params:
            cmd += ["--milestone", str(params["milestone"])]
        if "assignee" in params:
            cmd += ["--assignee", str(params["assignee"])]
        return cmd

    # Unreachable after validation, but makes type-checker happy
    raise ValueError(f"Unhandled op: {op}")  # pragma: no cover


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def _run_operation(
    op_spec: dict[str, Any],
    dry_run: bool,
) -> dict[str, Any]:
    """Execute (or simulate) a single operation. Returns a result dict."""
    import subprocess

    op = op_spec.get("op", "")
    target = op_spec.get("target")

    try:
        cmd = _build_gh_cmd(op_spec)
    except Exception as exc:
        return {"op": op, "target": target, "status": "failed", "error": str(exc)}

    if dry_run:
        print(f"[DRY-RUN] {' '.join(cmd)}", file=sys.stderr)
        return {"op": op, "target": target, "status": "dry-run", "error": None, "cmd": cmd}

    result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip()
        print(f"[FAIL] {op} target={target}: {err}", file=sys.stderr)
        return {"op": op, "target": target, "status": "failed", "error": err}

    print(f"[OK] {op} target={target}", file=sys.stderr)
    return {"op": op, "target": target, "status": "ok", "error": None}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # --- Load ---
    try:
        ops = _load_operations(args.input)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    # --- Validate ---
    errors = _validate_operations(ops)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 2

    # --- Execute ---
    results: list[dict[str, Any]] = []
    any_failed = False

    for i, op_spec in enumerate(ops):
        result = _run_operation(op_spec, dry_run=args.dry_run)
        results.append(result)
        if result["status"] == "failed":
            any_failed = True
        if not args.dry_run and i < len(ops) - 1:
            time.sleep(args.rate_limit_delay)

    # --- Output ---
    print(json.dumps(results, indent=2))
    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
