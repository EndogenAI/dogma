#!/usr/bin/env python3
"""
aggregate_session_costs.py — Group baseline session-cost data by model+phase or by role.

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
    - JSON aggregate to stdout grouped by model and phase (default) or role
    - Explicit source boundary metadata for later Phase 2 snapshot seeding
    - No writes, no snapshot generation, no downstream side effects

Usage:
    uv run python scripts/aggregate_session_costs.py
    uv run python scripts/aggregate_session_costs.py --start-date 2026-03-27 --end-date 2026-03-28
    uv run python scripts/aggregate_session_costs.py --log-file /tmp/session_cost_log.json
    uv run python scripts/aggregate_session_costs.py --aggregate-by role

Exit codes:
    0: Success
    1: Invalid input or malformed source records
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import date, datetime
from functools import lru_cache
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
ROLE_OUTPUT_BOUNDARY = "Grouped role metrics only: agent_role, tokens_in, tokens_out, record_count; no extra metrics."

FALLBACK_AGENT_ROLES = {
    "executive-orchestrator",
    "executive-docs",
    "executive-researcher",
    "executive-scripter",
    "executive-automator",
    "executive-pm",
    "executive-fleet",
    "executive-planner",
    "github",
    "review",
}


@lru_cache(maxsize=1)
def known_agent_roles() -> set[str]:
    """Load known agent slugs from .github/agents, with a stable fallback set."""
    agents_dir = Path(__file__).resolve().parent.parent / ".github" / "agents"
    discovered_roles = {
        path.name.removesuffix(".agent.md")
        for path in agents_dir.glob("*.agent.md")
        if path.is_file() and path.name.endswith(".agent.md")
    }
    return discovered_roles or set(FALLBACK_AGENT_ROLES)


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


def derive_agent_role(session_id: str) -> str:
    """Derive agent role from session_id path prefix; unknown prefixes map to unknown."""
    role_candidate = session_id.split("/", 1)[0].strip().lower()
    return role_candidate if role_candidate in known_agent_roles() else "unknown"


def read_archived_records(archive_dir: str | Path | None = None) -> list[dict[str, Any]]:
    """
    Read all archived session cost records from .cache/session_cost_archives/.
    Archives are JSON arrays named session_cost_log_archive_<start>_to_<end>.json.
    Returns concatenated list of all archived records; returns empty list if no archives exist.
    """
    repo_root = Path(__file__).resolve().parent.parent
    if archive_dir is None:
        archive_dir = repo_root / ".cache" / "session_cost_archives"
    else:
        archive_dir = Path(archive_dir)

    if not archive_dir.exists():
        return []

    all_archived = []
    for archive_file in sorted(archive_dir.glob("session_cost_log_archive_*.json")):
        try:
            with open(archive_file, "r", encoding="utf-8") as f:
                archived_records = json.load(f)
                if isinstance(archived_records, list):
                    all_archived.extend(archived_records)
        except (json.JSONDecodeError, ValueError, IOError):
            # Skip malformed archives; continue processing others
            pass

    return all_archived


def aggregate_records(
    records: list[dict[str, Any]],
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    aggregate_by: str = "model-phase",
) -> list[dict[str, Any]]:
    """Aggregate validated records within inclusive date bounds using the selected mode."""
    if start_date and end_date and start_date > end_date:
        raise ValueError("start date must be less than or equal to end date")

    if aggregate_by not in {"model-phase", "role"}:
        raise ValueError("aggregate mode must be one of: model-phase, role")

    grouped: dict[Any, dict[str, Any]] = defaultdict(lambda: {"record_count": 0, "tokens_in": 0, "tokens_out": 0})

    for index, raw_record in enumerate(records):
        record = validate_record(raw_record, index=index)
        current_date = record_date(record)
        if start_date and current_date < start_date:
            continue
        if end_date and current_date > end_date:
            continue

        if aggregate_by == "role":
            key = derive_agent_role(record["session_id"])
        else:
            key = (record["model"], record["phase"])
        grouped[key]["record_count"] += 1
        grouped[key]["tokens_in"] += record["tokens_in"]
        grouped[key]["tokens_out"] += record["tokens_out"]

    if aggregate_by == "role":
        return [
            {
                "agent_role": agent_role,
                "record_count": grouped[agent_role]["record_count"],
                "tokens_in": grouped[agent_role]["tokens_in"],
                "tokens_out": grouped[agent_role]["tokens_out"],
            }
            for agent_role in sorted(grouped.keys())
        ]

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
    aggregate_by: str = "model-phase",
    include_archives: bool = True,
) -> dict[str, Any]:
    """Read the canonical source log and archives; return Phase 1 aggregation payload.

    Args:
        log_file: Optional path override for session_cost_log.json
        start_date: Inclusive lower date bound
        end_date: Inclusive upper date bound
        aggregate_by: Aggregation mode (model-phase or role)
        include_archives: If True (default), include archived records from .cache/session_cost_archives/
    """
    resolved_log_file = resolve_log_file(log_file)
    records = read_log(log_file=resolved_log_file)

    # Include archived records if requested
    if include_archives:
        repo_root = resolved_log_file.parent
        archive_dir = repo_root / ".cache" / "session_cost_archives"
        archived_records = read_archived_records(archive_dir)
        records.extend(archived_records)

    return {
        "source_boundary": SOURCE_BOUNDARY,
        "output_boundary": ROLE_OUTPUT_BOUNDARY if aggregate_by == "role" else OUTPUT_BOUNDARY,
        "log_file": str(resolved_log_file),
        "date_range": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "bounds": "inclusive",
        },
        "groups": aggregate_records(
            records,
            start_date=start_date,
            end_date=end_date,
            aggregate_by=aggregate_by,
        ),
    }


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Aggregate session cost records by model and phase")
    parser.add_argument("--log-file", help="Optional path override for session_cost_log.json")
    parser.add_argument("--start-date", help="Inclusive lower date bound (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="Inclusive upper date bound (YYYY-MM-DD)")
    parser.add_argument(
        "--aggregate-by",
        choices=["model-phase", "role"],
        default="model-phase",
        help="Aggregation mode: model-phase (default) or role",
    )
    parser.add_argument(
        "--no-archives",
        action="store_true",
        help="Exclude archived records; aggregate active log only",
    )
    args = parser.parse_args()

    try:
        payload = aggregate_log(
            log_file=args.log_file,
            start_date=parse_date_arg(args.start_date, "--start-date"),
            end_date=parse_date_arg(args.end_date, "--end-date"),
            aggregate_by=args.aggregate_by,
            include_archives=not args.no_archives,
        )
        print(json.dumps(payload, indent=2))
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
