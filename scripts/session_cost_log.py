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
- synthetic (bool, optional): Explicit marker required for zero-token records

**Outputs**:
- Appends one JSON record to `session_cost_log.json` at workspace root
- Measured records contain six canonical fields; synthetic records add `synthetic: true`

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
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE_ENV_VAR = "SESSION_COST_LOG_FILE"
REQUIRED_RECORD_KEYS = (
    "session_id",
    "model",
    "tokens_in",
    "tokens_out",
    "phase",
    "timestamp",
)
OPTIONAL_RECORD_KEYS = ("synthetic",)
DEFAULT_LOG_FILE = REPO_ROOT / "session_cost_log.json"
LOG_FILE = DEFAULT_LOG_FILE


def resolve_log_file(log_file: str | Path | None = None) -> Path:
    """Resolve the active session cost log path.

    Precedence:
    1. Explicit function argument
    2. SESSION_COST_LOG_FILE environment variable
    3. Module default/monkeypatched LOG_FILE
    """
    if log_file is not None:
        return Path(log_file)

    env_override = os.getenv(LOG_FILE_ENV_VAR)
    if env_override:
        return Path(env_override)

    return Path(LOG_FILE)


def _validate_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _validate_non_negative_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value


def build_record(
    session_id: str,
    model: str,
    tokens_in: int,
    tokens_out: int,
    phase: str,
    timestamp: str,
    synthetic: bool = False,
) -> dict[str, Any]:
    """Build and validate a session cost record with optional synthetic marker."""
    normalized_tokens_in = _validate_non_negative_int(tokens_in, "tokens_in")
    normalized_tokens_out = _validate_non_negative_int(tokens_out, "tokens_out")
    if not isinstance(synthetic, bool):
        raise ValueError("synthetic must be a boolean")
    if normalized_tokens_in == 0 and normalized_tokens_out == 0 and not synthetic:
        raise ValueError("zero-token records require synthetic=true")

    record = {
        "session_id": _validate_non_empty_string(session_id, "session_id"),
        "model": _validate_non_empty_string(model, "model"),
        "tokens_in": normalized_tokens_in,
        "tokens_out": normalized_tokens_out,
        "phase": _validate_non_empty_string(phase, "phase"),
        "timestamp": _validate_non_empty_string(timestamp, "timestamp"),
    }
    if synthetic:
        record["synthetic"] = True

    return record


def validate_record(record: Any, *, index: int | None = None) -> dict[str, Any]:
    """Validate an existing record against required+optional schema boundaries."""
    prefix = f"record at index {index}" if index is not None else "record"
    if not isinstance(record, dict):
        raise ValueError(f"{prefix} must be a JSON object")

    keys = set(record.keys())
    required = set(REQUIRED_RECORD_KEYS)
    optional = set(OPTIONAL_RECORD_KEYS)
    missing = required - keys
    unknown = keys - (required | optional)
    if missing:
        expected = ", ".join(REQUIRED_RECORD_KEYS)
        raise ValueError(f"{prefix} is missing required keys; expected: {expected}")
    if unknown:
        raise ValueError(f"{prefix} contains unsupported keys: {', '.join(sorted(unknown))}")

    synthetic_present = "synthetic" in record
    if synthetic_present and not isinstance(record["synthetic"], bool):
        raise ValueError(f"{prefix} field 'synthetic' must be a boolean when present")

    return build_record(
        session_id=record["session_id"],
        model=record["model"],
        tokens_in=record["tokens_in"],
        tokens_out=record["tokens_out"],
        phase=record["phase"],
        timestamp=record["timestamp"],
        synthetic=(
            record["synthetic"] if synthetic_present else (record["tokens_in"] == 0 and record["tokens_out"] == 0)
        ),
    )


def log_session_cost(
    session_id: str,
    model: str,
    tokens_in: int,
    tokens_out: int,
    phase: str,
    timestamp: str,
    synthetic: bool = False,
    log_file: str | Path | None = None,
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
    target_log_file = resolve_log_file(log_file)
    record = build_record(session_id, model, tokens_in, tokens_out, phase, timestamp, synthetic=synthetic)

    # Read existing records
    records = read_log(log_file=target_log_file)

    # Append new record
    records.append(record)

    # Write back
    target_log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_log_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def read_log(log_file: str | Path | None = None, *, exclude_synthetic: bool = False) -> list[dict[str, Any]]:
    """
    Read all session cost records from the log file.

    Returns:
        List of session cost records (empty list if file doesn't exist)

    Args:
        log_file: Optional explicit path to JSON log file
        exclude_synthetic: If True, omit records marked synthetic
    """
    target_log_file = resolve_log_file(log_file)
    if not target_log_file.exists():
        return []

    with open(target_log_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    if not isinstance(records, list):
        raise ValueError("session cost log must contain a JSON array")

    validated = [validate_record(record, index=index) for index, record in enumerate(records)]
    if exclude_synthetic:
        return [record for record in validated if not record.get("synthetic", False)]
    return validated


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
        "--synthetic",
        action="store_true",
        help="Mark record as synthetic (required for zero-token records)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print record without writing to disk",
    )

    args = parser.parse_args()

    try:
        record = build_record(
            args.session,
            args.model,
            args.tokens_in,
            args.tokens_out,
            args.phase,
            args.timestamp,
            synthetic=args.synthetic,
        )

        if args.dry_run:
            print("DRY RUN — would append:")
            print(json.dumps(record, indent=2))
            return 0

        log_session_cost(
            record["session_id"],
            record["model"],
            record["tokens_in"],
            record["tokens_out"],
            record["phase"],
            record["timestamp"],
            synthetic=bool(record.get("synthetic", False)),
        )
        print(f"Logged session cost: {args.session} / {args.phase}")
        return 0

    except (ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
