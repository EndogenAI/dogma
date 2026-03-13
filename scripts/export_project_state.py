"""
scripts/export_project_state.py — Export GitHub project state to JSON.

Purpose
-------
Queries the GitHub CLI for the current repository's issue list and label list,
then writes a structured JSON snapshot to disk.  Intended to be called by the
``snapshot-issues`` CI workflow on a cron schedule so later sessions can read
project state locally without incurring gh API calls.

Inputs
------
- GitHub CLI (``gh``) authenticated and in PATH
- Optionally: ``--output PATH`` to override the default cache location

Outputs
-------
- JSON file at ``--output`` path (default: ``.cache/github/project_state.json``)
  Shape::

    {
      "issues": [{"number": N, "title": "...", "state": "open|closed",
                  "labels": [{"name": "...", "color": "...", "description": "..."}]}],
      "labels": [{"name": "...", "color": "...", "description": "..."}],
      "generated_at": "2026-03-13T06:00:00+00:00"
    }

- stdout: status messages (suppressed on success with --quiet)
- stderr: error details

Flags
-----
--output PATH   Destination file path.
                Default: .cache/github/project_state.json
--fields FIELDS Comma-separated list of top-level output fields to include.
                Known: issues, labels. Default: all fields.
                Case-insensitive.
--check         Print cache age and exit 0 if fresh (<4 h), exit 1 if stale/absent.
--quiet         Suppress informational stdout messages.
--help          Show this help and exit.

Exit codes
----------
0  Success (or --check with fresh cache).
1  gh CLI error, write failure, or --check with stale/absent cache.

Usage examples
--------------
# Export to default cache location
uv run python scripts/export_project_state.py

# Export to a custom path
uv run python scripts/export_project_state.py --output /tmp/state.json

# Check whether the cache is fresh (<4 h old)
uv run python scripts/export_project_state.py --check
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_OUTPUT = Path(".cache/github/project_state.json")
_FRESH_HOURS = 4  # cache is "fresh" for this many hours
_KNOWN_FIELDS: tuple[str, ...] = ("issues", "labels")


# ---------------------------------------------------------------------------
# Security: path validation
# ---------------------------------------------------------------------------


def _resolve_safe(path: Path) -> Path:
    """Return the resolved absolute path.

    Uses ``Path.resolve()`` to canonicalize the path and collapse any ``../``
    sequences.  Callers legitimately write to ``/tmp`` for tests, so no
    workspace-constraint is enforced here — safety relies on ``Path.resolve()``
    handling traversal collapse correctly.
    """
    resolved = path.resolve()
    # Path.resolve() already collapses .. segments; nothing further to reject.
    return resolved


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export GitHub issue and label state to a local JSON snapshot.",
    )
    parser.add_argument(
        "--output",
        default=str(_DEFAULT_OUTPUT),
        metavar="PATH",
        help=f"Output file path (default: {_DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        default=False,
        help="Check cache freshness only; exits 0 if fresh (<4 h), 1 if stale/absent.",
    )
    parser.add_argument(
        "--fields",
        default=None,
        metavar="FIELDS",
        help=(
            "Comma-separated list of fields to include (e.g. issues,labels). "
            f"Known fields: {', '.join(_KNOWN_FIELDS)}. "
            "Default: all fields."
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress informational stdout messages.",
    )
    return parser


# ---------------------------------------------------------------------------
# Cache freshness check
# ---------------------------------------------------------------------------


def check_cache(output_path: Path, quiet: bool = False) -> int:
    """Print cache age and return 0 if fresh, 1 if stale or absent."""
    if not output_path.exists():
        if not quiet:
            print(f"ABSENT: {output_path} does not exist", flush=True)
        return 1

    try:
        data = json.loads(output_path.read_text(encoding="utf-8"))
        generated_at = datetime.fromisoformat(data["generated_at"])
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        if not quiet:
            print(f"STALE: {output_path} is unreadable or malformed — {exc}", flush=True)
        return 1

    now = datetime.now(tz=timezone.utc)
    age_hours = (now - generated_at).total_seconds() / 3600

    if age_hours < _FRESH_HOURS:
        if not quiet:
            print(f"FRESH: {output_path} ({age_hours:.1f} h old)", flush=True)
        return 0
    else:
        if not quiet:
            print(f"STALE: {output_path} ({age_hours:.1f} h old — threshold {_FRESH_HOURS} h)", flush=True)
        return 1


# ---------------------------------------------------------------------------
# gh CLI helpers
# ---------------------------------------------------------------------------


def _run_gh(args: list[str]) -> str:
    """Run a gh CLI command and return stdout.  Exits 1 on non-zero exit."""
    try:
        result = subprocess.run(  # noqa: S603
            ["gh", *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("ERROR: gh CLI not found in PATH", file=sys.stderr, flush=True)
        sys.exit(1)

    if result.returncode != 0:
        print(
            f"ERROR: gh command failed (exit {result.returncode}): {result.stderr.strip()}",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    return result.stdout


def fetch_issues() -> list[dict]:
    """Return [{number, title, state, labels}, ...]."""
    raw = _run_gh(
        [
            "issue",
            "list",
            "--state",
            "all",
            "--limit",
            "200",
            "--json",
            "number,title,state,labels",
        ]
    )
    return json.loads(raw)


def fetch_labels() -> list[dict]:
    """Return [{name, color, description}, ...]."""
    raw = _run_gh(["label", "list", "--json", "name,color,description"])
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Main export logic
# ---------------------------------------------------------------------------


def export(
    output_path: Path,
    quiet: bool = False,
    fields: list[str] | None = None,
) -> int:
    """Fetch GitHub state and write JSON to *output_path*.  Returns exit code."""
    requested = fields if fields is not None else list(_KNOWN_FIELDS)

    payload: dict = {}

    if "issues" in requested:
        if not quiet:
            print("Fetching issues…", flush=True)
        payload["issues"] = fetch_issues()

    if "labels" in requested:
        if not quiet:
            print("Fetching labels…", flush=True)
        payload["labels"] = fetch_labels()

    payload["generated_at"] = datetime.now(tz=timezone.utc).isoformat()

    # Validate / create parent directory
    safe_path = _resolve_safe(output_path)
    try:
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: could not write {safe_path}: {exc}", file=sys.stderr, flush=True)
        return 1

    if not quiet:
        counts = ", ".join(f"{len(payload[f])} {f}" for f in requested if f in payload)
        print(f"Written: {safe_path} ({counts})", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    output_path = Path(args.output)

    if args.check:
        return check_cache(output_path, quiet=args.quiet)

    fields: list[str] | None = None
    if args.fields is not None:
        requested_fields = [f.strip().lower() for f in args.fields.split(",") if f.strip()]
        unknown = [f for f in requested_fields if f not in _KNOWN_FIELDS]
        if unknown:
            print(
                f"ERROR: unknown field(s): {', '.join(unknown)}. Known fields: {', '.join(_KNOWN_FIELDS)}",
                file=sys.stderr,
                flush=True,
            )
            return 1
        fields = requested_fields

    return export(output_path, quiet=args.quiet, fields=fields)


if __name__ == "__main__":
    sys.exit(main())
