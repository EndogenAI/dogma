#!/usr/bin/env python3
"""
rotate_session_cost_log.py — Retention and Rotation for Session Cost Log

**Purpose**: Archive old session cost records to timestamped files; enforce retention window.

**Retention Policy**:
- Default window: 90 days from current date
- Records older than window are archived to `.cache/session_cost_archives/`
- Archived files are named: `session_cost_log_archive_YYYY-MM-DD_to_YYYY-MM-DD.json`
- Rotation trigger: size-based (≥10MB) OR time-based (≥30 days since last rotation)

**Inputs**:
- --retention-days: Retention window in days (default: 90)
- --size-threshold: Size limit in bytes (default: 10485760 = 10MB); rotation triggers if main file exceeds this
- --last-rotation-threshold-days: Days since last rotation before time-based rotation triggers (default: 30)
- --log-file: Path to session_cost_log.json (default: repo root)
- --dry-run: Print actions without writing
- --check-only: Advisory threshold check mode; reports rotation-needed status and intentionally exits 0

**Outputs**:
- Rotated records written to `.cache/session_cost_archives/session_cost_log_archive_<start>_to_<end>.json`
- Retention policy metadata written to `.cache/session_cost_archives/rotation_metadata.json`
- Main log file truncated to records within retention window
- Aggregation scripts remain compatible: read both active log and archive directory

**Exit Codes**:
- 0: Success (rotation completed or not needed); `--check-only` always returns 0 (advisory mode)
- 1: Invalid input, I/O error, or rotation failure
- 2: Retention window is invalid (e.g., negative days)

**Usage**:
    # Check if rotation is needed (advisory only, exit 0 always)
    uv run python scripts/rotate_session_cost_log.py --dry-run

    # Perform rotation with default policy (90-day retention, 10MB threshold)
    uv run python scripts/rotate_session_cost_log.py

    # Rotate with custom retention window (365 days)
    uv run python scripts/rotate_session_cost_log.py --retention-days 365

    # Rotate with custom size threshold (5MB)
    uv run python scripts/rotate_session_cost_log.py --size-threshold 5242880

    # Combine threshold overrides
    uv run python scripts/rotate_session_cost_log.py --retention-days 180 --size-threshold 20971520
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE_ENV_VAR = "SESSION_COST_LOG_FILE"
ARCHIVE_DIR = REPO_ROOT / ".cache" / "session_cost_archives"
ROTATION_METADATA_FILE = ARCHIVE_DIR / "rotation_metadata.json"

DEFAULT_LOG_FILE = REPO_ROOT / "session_cost_log.json"
DEFAULT_RETENTION_DAYS = 90
DEFAULT_SIZE_THRESHOLD_BYTES = 10 * 1024 * 1024  # 10 MB
DEFAULT_LAST_ROTATION_THRESHOLD_DAYS = 30


def resolve_log_file(log_file: str | Path | None = None) -> Path:
    """Resolve the active session cost log path.

    Precedence:
    1. Explicit function argument
    2. SESSION_COST_LOG_FILE environment variable
    3. Default at repo root
    """
    if log_file is not None:
        return Path(log_file)

    env_override = os.getenv(LOG_FILE_ENV_VAR)
    if env_override:
        return Path(env_override)

    return DEFAULT_LOG_FILE


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO 8601 timestamp (with or without Z suffix)."""
    ts = timestamp_str.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)


def should_archive_record(record: dict[str, Any], cutoff_date: datetime) -> bool:
    """Determine if a record is older than the cutoff date (should be archived)."""
    try:
        record_date = parse_timestamp(record.get("timestamp", ""))
        return record_date < cutoff_date
    except (ValueError, TypeError):
        # Malformed timestamp: consider it archivable to clean up bad data
        return True


def load_records(log_file: Path) -> list[dict[str, Any]]:
    """Load records from session cost log. Return empty list if file doesn't exist."""
    if not log_file.exists():
        return []

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            records = json.load(f)
            if not isinstance(records, list):
                raise ValueError("session cost log must contain a JSON array")
            return records
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid session cost log format: {e}")


def load_rotation_metadata() -> dict[str, Any]:
    """Load rotation metadata from archive directory. Return empty dict if file doesn't exist."""
    if not ROTATION_METADATA_FILE.exists():
        return {"last_rotation": None, "archive_count": 0, "total_archived_records": 0}

    try:
        with open(ROTATION_METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {"last_rotation": None, "archive_count": 0, "total_archived_records": 0}


def update_rotation_metadata(metadata: dict[str, Any], rotation_info: dict[str, Any]) -> None:
    """Update and persist rotation metadata."""
    metadata["last_rotation"] = datetime.now(timezone.utc).isoformat()
    metadata["archive_count"] = metadata.get("archive_count", 0) + 1
    metadata["total_archived_records"] = metadata.get("total_archived_records", 0) + len(
        rotation_info.get("archived_records", [])
    )
    metadata["latest_archive"] = rotation_info.get("archive_file")

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(ROTATION_METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def perform_rotation(
    log_file: Path,
    retention_days: int,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Rotate session cost log: archive old records, update main log.

    Returns:
        Dict with keys: success, archived_count, retained_count, archive_file, message
    """
    if retention_days < 0:
        raise ValueError("retention_days must be non-negative")

    # Load current records
    try:
        records = load_records(log_file)
    except ValueError as e:
        return {"success": False, "message": str(e), "archived_count": 0, "retained_count": 0}

    if not records:
        return {
            "success": True,
            "message": "No records to rotate",
            "archived_count": 0,
            "retained_count": 0,
            "archive_file": None,
        }

    # Calculate cutoff date
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

    # Split records
    to_archive = [r for r in records if should_archive_record(r, cutoff_date)]
    to_retain = [r for r in records if not should_archive_record(r, cutoff_date)]

    if not to_archive:
        return {
            "success": True,
            "message": f"No records older than {retention_days} days",
            "archived_count": 0,
            "retained_count": len(to_retain),
            "archive_file": None,
        }

    # Generate archive filename from parseable timestamps only.
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    parsed_timestamps = []
    for record in to_archive:
        timestamp = record.get("timestamp", "")
        try:
            parsed_timestamps.append(parse_timestamp(timestamp))
        except (ValueError, TypeError):
            continue

    start_date = min(parsed_timestamps) if parsed_timestamps else None
    end_date = max(parsed_timestamps) if parsed_timestamps else None

    if start_date and end_date:
        start_str = start_date.date().isoformat()
        end_str = end_date.date().isoformat()
        archive_file = ARCHIVE_DIR / f"session_cost_log_archive_{start_str}_to_{end_str}.json"
    else:
        now_str = datetime.now(timezone.utc).date().isoformat()
        archive_file = ARCHIVE_DIR / f"session_cost_log_archive_{now_str}.json"

    if dry_run:
        return {
            "success": True,
            "message": f"[DRY RUN] Would archive {len(to_archive)} records, retain {len(to_retain)}",
            "archived_count": len(to_archive),
            "retained_count": len(to_retain),
            "archive_file": str(archive_file),
            "action": "DRY_RUN",
        }

    # Write archive
    try:
        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(to_archive, f, indent=2)
    except IOError as e:
        return {
            "success": False,
            "message": f"Failed to write archive file: {e}",
            "archived_count": 0,
            "retained_count": len(to_retain),
        }

    # Write retained records back to main log
    try:
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(to_retain, f, indent=2)
    except IOError as e:
        return {
            "success": False,
            "message": f"Failed to update main log file: {e}",
            "archived_count": len(to_archive),
            "retained_count": len(to_retain),
        }

    # Update metadata
    try:
        metadata = load_rotation_metadata()
        update_rotation_metadata(
            metadata,
            {"archived_records": to_archive, "archive_file": str(archive_file)},
        )
    except Exception as e:
        # Non-fatal: continue if metadata update fails
        print(f"Warning: Failed to update rotation metadata: {e}", file=sys.stderr)

    return {
        "success": True,
        "message": f"Archived {len(to_archive)} records, retained {len(to_retain)}",
        "archived_count": len(to_archive),
        "retained_count": len(to_retain),
        "archive_file": str(archive_file),
    }


def check_rotation_needed(
    log_file: Path,
    size_threshold_bytes: int,
    last_rotation_threshold_days: int,
) -> dict[str, Any]:
    """Check if rotation is needed based on size or time thresholds."""
    if not log_file.exists():
        return {"rotation_needed": False, "reason": "Log file does not exist"}

    # Check size threshold
    file_size = log_file.stat().st_size
    if file_size >= size_threshold_bytes:
        return {
            "rotation_needed": True,
            "reason": f"File size ({file_size} bytes) exceeds threshold ({size_threshold_bytes} bytes)",
            "trigger": "size",
        }

    # Check time threshold
    try:
        metadata = load_rotation_metadata()
        last_rotation_str = metadata.get("last_rotation")
        if last_rotation_str:
            last_rotation = datetime.fromisoformat(last_rotation_str)
            days_since_rotation = (datetime.now(timezone.utc) - last_rotation).days
            if days_since_rotation >= last_rotation_threshold_days:
                reason = (
                    f"Last rotation {days_since_rotation} days ago (threshold: {last_rotation_threshold_days} days)"
                )
                return {
                    "rotation_needed": True,
                    "reason": reason,
                    "trigger": "time",
                }
    except Exception:
        # If we can't read metadata, don't fail: just skip time-based check
        pass

    return {
        "rotation_needed": False,
        "reason": "No rotation thresholds exceeded",
    }


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Rotate session cost log with retention and archival")
    parser.add_argument(
        "--retention-days",
        type=int,
        default=DEFAULT_RETENTION_DAYS,
        help=f"Retention window in days (default: {DEFAULT_RETENTION_DAYS})",
    )
    parser.add_argument(
        "--size-threshold",
        type=int,
        default=DEFAULT_SIZE_THRESHOLD_BYTES,
        help=f"Size limit in bytes for size-based rotation trigger (default: {DEFAULT_SIZE_THRESHOLD_BYTES})",
    )
    parser.add_argument(
        "--last-rotation-threshold-days",
        type=int,
        default=DEFAULT_LAST_ROTATION_THRESHOLD_DAYS,
        help=f"Days since last rotation before time-based trigger (default: {DEFAULT_LAST_ROTATION_THRESHOLD_DAYS})",
    )
    parser.add_argument("--log-file", help="Path to session_cost_log.json")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Check if rotation is needed (advisory; always exits 0)",
    )

    args = parser.parse_args()

    log_file = resolve_log_file(args.log_file)

    try:
        if args.check_only:
            result = check_rotation_needed(log_file, args.size_threshold, args.last_rotation_threshold_days)
            print(json.dumps(result, indent=2))
            return 0

        result = perform_rotation(log_file, args.retention_days, dry_run=args.dry_run)

        if result["success"]:
            msg = result.get("message", "Rotation completed")
            print(msg)
            return 0
        else:
            msg = result.get("message", "Rotation failed")
            print(f"Error: {msg}", file=sys.stderr)
            return 1

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
