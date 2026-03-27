#!/usr/bin/env python3
"""
Session Cost Log — JSON-based Token Burn Tracking

**Purpose**: Record per-session token usage for cost analysis and trend monitoring.

**Inputs**:
- session_id (str): Unique session identifier (e.g., branch-slug/YYYY-MM-DD)
- model (str): Model name (e.g., "claude-sonnet-4")
- tokens_in (int): Input tokens consumed
- tokens_out (int): Output tokens generated
- phase (str): Phase or task name
- timestamp (str): ISO 8601 timestamp

**Outputs**:
- Appends one JSON record to `session_cost_log.json` at workspace root
- Each record contains all six fields

**Usage**:
    # Programmatic
    from scripts.session_cost_log import log_session_cost, read_log
    log_session_cost("main/2026-03-27", "claude-sonnet-4", 1500, 800, "Phase 1", "2026-03-27T14:30:00Z")
    records = read_log()

    # CLI
    uv run python scripts/session_cost_log.py --session main/2026-03-27 \
        --model claude-sonnet-4 --tokens-in 1500 --tokens-out 800 \
        --phase "Phase 1" --timestamp 2026-03-27T14:30:00Z

    # Dry-run (print without writing)
    uv run python scripts/session_cost_log.py --dry-run --session main/2026-03-27 \
        --model claude-sonnet-4 --tokens-in 1500 --tokens-out 800 \
        --phase "Phase 1" --timestamp 2026-03-27T14:30:00Z

**Exit Codes**:
- 0: Success
- 1: Invalid input or I/O error
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

LOG_FILE = Path("session_cost_log.json")


def log_session_cost(
    session_id: str,
    model: str,
    tokens_in: int,
    tokens_out: int,
    phase: str,
    timestamp: str,
) -> None:
    """
    Append one session cost record to the log file.

    Args:
        session_id: Unique session identifier
        model: Model name
        tokens_in: Input tokens consumed
        tokens_out: Output tokens generated
        phase: Phase or task name
        timestamp: ISO 8601 timestamp

    Raises:
        ValueError: If any required field is missing or invalid type
    """
    # Validate required fields
    if not session_id or not isinstance(session_id, str):
        raise ValueError("session_id must be a non-empty string")
    if not model or not isinstance(model, str):
        raise ValueError("model must be a non-empty string")
    if not isinstance(tokens_in, int) or tokens_in < 0:
        raise ValueError("tokens_in must be a non-negative integer")
    if not isinstance(tokens_out, int) or tokens_out < 0:
        raise ValueError("tokens_out must be a non-negative integer")
    if not phase or not isinstance(phase, str):
        raise ValueError("phase must be a non-empty string")
    if not timestamp or not isinstance(timestamp, str):
        raise ValueError("timestamp must be a non-empty string")

    record = {
        "session_id": session_id,
        "model": model,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "phase": phase,
        "timestamp": timestamp,
    }

    # Read existing records
    records = []
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)

    # Append new record
    records.append(record)

    # Write back
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def read_log() -> list[dict[str, Any]]:
    """
    Read all session cost records from the log file.

    Returns:
        List of session cost records (empty list if file doesn't exist)
    """
    if not LOG_FILE.exists():
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Log session token usage to JSON file")
    parser.add_argument("--session", required=True, help="Session ID")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--tokens-in", type=int, required=True, help="Input tokens")
    parser.add_argument("--tokens-out", type=int, required=True, help="Output tokens")
    parser.add_argument("--phase", required=True, help="Phase or task name")
    parser.add_argument("--timestamp", required=True, help="ISO 8601 timestamp")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print record without writing to disk",
    )

    args = parser.parse_args()

    try:
        record = {
            "session_id": args.session,
            "model": args.model,
            "tokens_in": args.tokens_in,
            "tokens_out": args.tokens_out,
            "phase": args.phase,
            "timestamp": args.timestamp,
        }

        if args.dry_run:
            print("DRY RUN — would append:")
            print(json.dumps(record, indent=2))
            return 0

        log_session_cost(
            args.session,
            args.model,
            args.tokens_in,
            args.tokens_out,
            args.phase,
            args.timestamp,
        )
        print(f"Logged session cost: {args.session} / {args.phase}")
        return 0

    except (ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
