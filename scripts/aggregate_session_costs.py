#!/usr/bin/env python3
"""
aggregate_session_costs.py — Group baseline session-cost data by model and phase.

Purpose:
    Produce the lean Phase 1 aggregation output for baseline-data seeding. The accepted
    source boundary is exact six-field records from session_cost_log.json only:
    session_id, model, tokens_in, tokens_out, phase, timestamp.

Inputs:
    - session_cost_log.json records via scripts/session_cost_log.py
    - --log-file: optional path override for the source JSON log
    - --start-date: optional inclusive lower date bound (YYYY-MM-DD)
    - --end-date: optional inclusive upper date bound (YYYY-MM-DD)

Outputs:
    - JSON aggregate to stdout grouped by model and phase
    - Explicit source boundary metadata for later Phase 2 snapshot seeding
    - No writes, no snapshot generation, no downstream side effects

Usage:
    uv run python scripts/aggregate_session_costs.py
    uv run python scripts/aggregate_session_costs.py --start-date 2026-03-27 --end-date 2026-03-28
    uv run python scripts/aggregate_session_costs.py --log-file /tmp/session_cost_log.json

Exit codes:
    0: Success
    1: Invalid input or malformed source records
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    from scripts.session_cost_log import REQUIRED_RECORD_KEYS, read_log, resolve_log_file, validate_record
except ModuleNotFoundError:
    from session_cost_log import REQUIRED_RECORD_KEYS, read_log, resolve_log_file, validate_record

SOURCE_BOUNDARY = {
    "accepted_source": "Exact six-field session_cost_log records only",
    "required_keys": list(REQUIRED_RECORD_KEYS),
    "malformed_entry_policy": "fail-fast",
}
OUTPUT_BOUNDARY = "Grouped aggregate data for later Phase 2 seeding only; no Phase 2 side effects."


def parse_date_arg(raw_value: str | None, flag_name: str) -> date | None:
    """Parse a YYYY-MM-DD CLI date argument."""
    if raw_value is None:
        return None

    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise ValueError(f"{flag_name} must be YYYY-MM-DD") from exc


def record_date(record: dict[str, Any]) -> date:
    """Extract the UTC date component from a canonical session-cost record."""
    timestamp = record["timestamp"]
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date()
    except ValueError as exc:
        raise ValueError(f"invalid timestamp in record {record['session_id']}: {timestamp}") from exc


def aggregate_records(
    records: list[dict[str, Any]],
    *,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict[str, Any]]:
    """Aggregate validated records by model and phase within inclusive date bounds."""
    if start_date and end_date and start_date > end_date:
        raise ValueError("start date must be less than or equal to end date")

    grouped: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {"record_count": 0, "tokens_in": 0, "tokens_out": 0}
    )

    for index, raw_record in enumerate(records):
        record = validate_record(raw_record, index=index)
        current_date = record_date(record)
        if start_date and current_date < start_date:
            continue
        if end_date and current_date > end_date:
            continue

        key = (record["model"], record["phase"])
        grouped[key]["record_count"] += 1
        grouped[key]["tokens_in"] += record["tokens_in"]
        grouped[key]["tokens_out"] += record["tokens_out"]

    return [
        {
            "model": model,
            "phase": phase,
            "record_count": summary["record_count"],
            "tokens_in": summary["tokens_in"],
            "tokens_out": summary["tokens_out"],
        }
        for model, phase in sorted(grouped.keys())
        for summary in [grouped[(model, phase)]]
    ]


def aggregate_log(
    *,
    log_file: str | Path | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict[str, Any]:
    """Read the canonical source log and return the Phase 1 aggregation payload."""
    resolved_log_file = resolve_log_file(log_file)
    records = read_log(log_file=resolved_log_file)
    return {
        "source_boundary": SOURCE_BOUNDARY,
        "output_boundary": OUTPUT_BOUNDARY,
        "log_file": str(resolved_log_file),
        "date_range": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "bounds": "inclusive",
        },
        "groups": aggregate_records(records, start_date=start_date, end_date=end_date),
    }


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Aggregate session cost records by model and phase")
    parser.add_argument("--log-file", help="Optional path override for session_cost_log.json")
    parser.add_argument("--start-date", help="Inclusive lower date bound (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="Inclusive upper date bound (YYYY-MM-DD)")
    args = parser.parse_args()

    try:
        payload = aggregate_log(
            log_file=args.log_file,
            start_date=parse_date_arg(args.start_date, "--start-date"),
            end_date=parse_date_arg(args.end_date, "--end-date"),
        )
        print(json.dumps(payload, indent=2))
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
