"""
preexec_audit_log.py — PREEXEC governor audit log writer and summariser.

Purpose
-------
Extend the PREEXEC governor concept by recording bash subshell invocations to
a structured audit log.  When PREEXEC_GOVERNOR_ENABLED is set in the environment,
the governor intercepts commands before execution.  This script provides the
*recording* half: each intercepted invocation is appended as a JSON line to the
audit log so that downstream tooling (e.g. token_spin_detector.py) can analyse
usage patterns without blocking execution.

The script is *audit-only*: it never blocks command execution.

This script was introduced as part of Sprint 13 (automation-observability,
issue #157) to provide structured visibility into PREEXEC governor activity.
Per the Programmatic-First principle in AGENTS.md, audit logging that was being
done ad-hoc across sessions is now encoded as a committed script.

Inputs
------
- --log FILE        Path to the audit log (default: .tmp/preexec_audit.log)
- --command TEXT    Command being audited (required unless --summary)
- --cwd TEXT        Working directory at invocation time (default: current $PWD)
- --governor-value  Value of PREEXEC_GOVERNOR_ENABLED env var (default: from env)
- --summary         Print a count of logged invocations grouped by command prefix

Outputs
-------
- Appends a single JSON line to the audit log on each non-summary invocation.
- --summary: prints a table of command-prefix counts to stdout.

Usage Examples
--------------
# Record a command invocation
uv run python scripts/preexec_audit_log.py --command "uv run pytest" --cwd /tmp

# Record with an explicit governor value
uv run python scripts/preexec_audit_log.py --command "bash -c 'ls'" --governor-value 1

# Summarise the audit log
uv run python scripts/preexec_audit_log.py --summary

# Summarise a non-default log
uv run python scripts/preexec_audit_log.py --summary --log .tmp/other.log

Exit Codes
----------
0  Success
1  Missing required argument / IO error
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG = REPO_ROOT / ".tmp" / "preexec_audit.log"


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_invocation(
    log_path: Path,
    command: str,
    cwd: str,
    governor_value: str,
) -> None:
    """Append one JSON line to *log_path* recording the invocation."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": _now_iso(),
        "command": command,
        "cwd": cwd,
        "governor_enabled": governor_value,
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def command_prefix(command: str) -> str:
    """Return the first token of a command string as its 'prefix'."""
    return command.strip().split()[0] if command.strip() else "(empty)"


def summarise_log(log_path: Path) -> None:
    """Print command-prefix counts from *log_path* to stdout."""
    if not log_path.exists():
        print(f"No audit log found at {log_path}", file=sys.stderr)
        return

    counts: Counter[str] = Counter()
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        counts[command_prefix(entry.get("command", ""))] += 1

    if not counts:
        print("(audit log is empty)")
        return

    width = max(len(p) for p in counts)
    print(f"{'Command prefix':<{width}}  Count")
    print("-" * (width + 8))
    for prefix, count in counts.most_common():
        print(f"{prefix:<{width}}  {count}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="preexec_audit_log.py",
        description="PREEXEC governor audit log writer / summariser.",
    )
    parser.add_argument(
        "--log",
        default=str(DEFAULT_LOG),
        help=f"Path to audit log file (default: {DEFAULT_LOG})",
    )
    parser.add_argument(
        "--command",
        default=None,
        help="Command being audited (required unless --summary).",
    )
    parser.add_argument(
        "--cwd",
        default=None,
        help="Working directory at invocation time (default: $PWD).",
    )
    parser.add_argument(
        "--governor-value",
        default=None,
        dest="governor_value",
        help="Value of PREEXEC_GOVERNOR_ENABLED (default: from env).",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print invocation counts grouped by command prefix.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    log_path = Path(args.log)

    if args.summary:
        summarise_log(log_path)
        return 0

    if not args.command:
        parser.error("--command is required unless --summary is set.")

    cwd = args.cwd or os.environ.get("PWD", os.getcwd())
    governor_value = args.governor_value
    if governor_value is None:
        governor_value = os.environ.get("PREEXEC_GOVERNOR_ENABLED", "")

    try:
        record_invocation(log_path, args.command, cwd, governor_value)
    except OSError as exc:
        print(f"Error writing audit log: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
