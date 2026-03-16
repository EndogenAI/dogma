"""
token_spin_detector.py — Detect runaway repeated command invocations (token spinning).

Purpose
-------
Context rot from unmanaged token accumulation degrades reasoning quality.
Token-spinning — an agent repeatedly invoking the same tool/command without
progress — is a specific failure mode documented in Xu et al. (2512.05470):
quadratic attention cost means even moderate repetition carries outsized
token overhead.

This script reads the PREEXEC governor audit log produced by
preexec_audit_log.py and detects "spinning": the same command executed
≥N times within a sliding time window.  It is *detection-only*: it never
blocks command execution.  Blocking layers can be added later by callers
that act on the exit code.

This script was introduced as part of Sprint 13 (automation-observability,
issue #156) per the Programmatic-First principle in AGENTS.md.

Inputs
------
- --log FILE           Path to the audit log (default: .tmp/preexec_audit.log)
- --threshold N        Invocations of the same command within the window to
                       consider "spinning" (default: 5)
- --window SECONDS     Sliding window size in seconds (default: 60)
- --check              Exit 0 if no spinning detected; exit 2 if spinning found.
                       Offending commands are printed to stderr.
- --dry-run            Print what would be flagged without changing the exit code.

Outputs
-------
- Spinning commands printed to stderr when detected in --check mode.
- --dry-run: same output as --check but always exits 0.

Usage Examples
--------------
# Check for spinning with defaults (exits 2 if spinning found)
uv run python scripts/token_spin_detector.py --check

# Use a custom threshold and window
uv run python scripts/token_spin_detector.py --check --threshold 3 --window 30

# Dry run: show what would be flagged, always exit 0
uv run python scripts/token_spin_detector.py --dry-run

# Point at a non-default audit log
uv run python scripts/token_spin_detector.py --check --log .tmp/other.log

Exit Codes
----------
0  No spinning detected (or --dry-run)
1  Usage / IO error
2  Spinning detected (--check mode only)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG = REPO_ROOT / ".tmp" / "preexec_audit.log"
DEFAULT_THRESHOLD = 5
DEFAULT_WINDOW = 60  # seconds


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


def _parse_timestamp(ts: str) -> float:
    """Parse an ISO-8601 UTC timestamp string into a POSIX float."""
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return dt.timestamp()


def _normalise_command(command: str) -> str:
    """Normalise a command string to its first two tokens for grouping."""
    tokens = command.strip().split()
    return " ".join(tokens[:2]) if len(tokens) >= 2 else (tokens[0] if tokens else "")


def load_entries(log_path: Path) -> list[dict]:
    """Load and parse all valid JSON-line entries from *log_path*."""
    if not log_path.exists():
        return []
    entries = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "timestamp" in entry and "command" in entry:
            entries.append(entry)
    return entries


def detect_spinning(
    entries: list[dict],
    threshold: int,
    window: float,
    now: float | None = None,
) -> list[tuple[str, int]]:
    """
    Return a list of (normalised_command, count) pairs where the command
    appears ≥ *threshold* times within the most-recent *window* seconds.

    *now* defaults to the current UTC time; pass an explicit value for testing.
    """
    if now is None:
        now = datetime.now(tz=timezone.utc).timestamp()

    cutoff = now - window
    counts: dict[str, int] = defaultdict(int)

    for entry in entries:
        try:
            ts = _parse_timestamp(entry["timestamp"])
        except (ValueError, KeyError):
            continue
        if ts >= cutoff:
            key = _normalise_command(entry["command"])
            counts[key] += 1

    return [(cmd, cnt) for cmd, cnt in counts.items() if cnt >= threshold]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="token_spin_detector.py",
        description="Detect runaway repeated command invocations in the PREEXEC audit log.",
    )
    parser.add_argument(
        "--log",
        default=str(DEFAULT_LOG),
        help=f"Path to audit log file (default: {DEFAULT_LOG})",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help=f"Invocations within window to flag as spinning (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--window",
        type=float,
        default=DEFAULT_WINDOW,
        help=f"Sliding window in seconds (default: {DEFAULT_WINDOW})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 2 if spinning detected; 0 if clean.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Print what would be flagged without changing exit code.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.check and not args.dry_run:
        parser.error("Specify --check or --dry-run.")

    log_path = Path(args.log)

    try:
        entries = load_entries(log_path)
    except OSError as exc:
        print(f"Error reading audit log: {exc}", file=sys.stderr)
        return 1

    spinning = detect_spinning(entries, args.threshold, args.window)

    if spinning:
        for cmd, count in spinning:
            print(
                f"SPIN DETECTED: '{cmd}' invoked {count} times within {args.window}s window",
                file=sys.stderr,
            )
        if args.check and not args.dry_run:
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
