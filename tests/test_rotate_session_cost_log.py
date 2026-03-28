"""Tests for scripts/rotate_session_cost_log.py."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.aggregate_session_costs import aggregate_log
from scripts.rotate_session_cost_log import (
    check_rotation_needed,
    load_records,
    load_rotation_metadata,
    parse_timestamp,
    perform_rotation,
    should_archive_record,
)


@pytest.fixture
def temp_archive_dir(tmp_path):
    """Create temporary archive directory."""
    archive_dir = tmp_path / ".cache" / "session_cost_archives"
    archive_dir.mkdir(parents=True, exist_ok=True)
    return archive_dir


@pytest.fixture
def temp_log_file(tmp_path):
    """Create temporary log file path."""
    return tmp_path / "session_cost_log.json"


@pytest.fixture
def sample_records():
    """Return a set of sample records spanning multiple days."""
    now = datetime.now(timezone.utc)
    return [
        {
            "session_id": "old/2026-02-01",
            "model": "claude-sonnet",
            "tokens_in": 100,
            "tokens_out": 50,
            "phase": "Phase 1",
            "timestamp": (now - timedelta(days=100)).isoformat(),
        },
        {
            "session_id": "old/2026-02-15",
            "model": "claude-sonnet",
            "tokens_in": 200,
            "tokens_out": 100,
            "phase": "Phase 2",
            "timestamp": (now - timedelta(days=95)).isoformat(),
        },
        {
            "session_id": "recent/2026-03-20",
            "model": "gpt-4",
            "tokens_in": 300,
            "tokens_out": 150,
            "phase": "Phase 1",
            "timestamp": (now - timedelta(days=8)).isoformat(),
        },
        {
            "session_id": "recent/2026-03-27",
            "model": "claude-sonnet",
            "tokens_in": 400,
            "tokens_out": 200,
            "phase": "Phase 3",
            "timestamp": (now - timedelta(days=1)).isoformat(),
        },
    ]


@pytest.mark.io
def test_parse_timestamp_iso_with_z():
    """parse_timestamp handles ISO 8601 with Z suffix."""
    ts = parse_timestamp("2026-03-27T14:30:00Z")
    assert ts.year == 2026
    assert ts.month == 3
    assert ts.day == 27


@pytest.mark.io
def test_parse_timestamp_iso_with_offset():
    """parse_timestamp handles ISO 8601 with +00:00 offset."""
    ts = parse_timestamp("2026-03-27T14:30:00+00:00")
    assert ts.year == 2026
    assert ts.month == 3


@pytest.mark.io
def test_parse_timestamp_invalid_raises():
    """parse_timestamp raises ValueError on invalid input."""
    with pytest.raises(ValueError):
        parse_timestamp("not-a-timestamp")


@pytest.mark.io
def test_should_archive_record_old_record():
    """should_archive_record returns True for records older than cutoff."""
    old_ts = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
    record = {
        "session_id": "test",
        "model": "claude",
        "tokens_in": 100,
        "tokens_out": 50,
        "phase": "Phase 1",
        "timestamp": old_ts,
    }
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    assert should_archive_record(record, cutoff) is True


@pytest.mark.io
def test_should_archive_record_recent_record():
    """should_archive_record returns False for records within retention window."""
    recent_ts = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    record = {
        "session_id": "test",
        "model": "claude",
        "tokens_in": 100,
        "tokens_out": 50,
        "phase": "Phase 1",
        "timestamp": recent_ts,
    }
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    assert should_archive_record(record, cutoff) is False


@pytest.mark.io
def test_should_archive_record_malformed_timestamp():
    """should_archive_record returns True for records with malformed timestamps."""
    record = {
        "session_id": "test",
        "model": "claude",
        "tokens_in": 100,
        "tokens_out": 50,
        "phase": "Phase 1",
        "timestamp": "not-a-timestamp",
    }
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    assert should_archive_record(record, cutoff) is True


@pytest.mark.io
def test_load_records_nonexistent_file():
    """load_records returns empty list when file doesn't exist."""
    result = load_records(Path("/nonexistent/path.json"))
    assert result == []


@pytest.mark.io
def test_load_records_success(temp_log_file, sample_records):
    """load_records successfully loads and returns records from file."""
    temp_log_file.write_text(json.dumps(sample_records), encoding="utf-8")
    result = load_records(temp_log_file)
    assert len(result) == 4
    assert result[0]["session_id"] == "old/2026-02-01"


@pytest.mark.io
def test_load_records_invalid_json(temp_log_file):
    """load_records raises ValueError on invalid JSON."""
    temp_log_file.write_text("not valid json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid session cost log format"):
        load_records(temp_log_file)


@pytest.mark.io
def test_load_records_not_array(temp_log_file):
    """load_records raises ValueError when JSON is not an array."""
    temp_log_file.write_text(json.dumps({"key": "value"}), encoding="utf-8")
    with pytest.raises(ValueError, match="must contain a JSON array"):
        load_records(temp_log_file)


@pytest.mark.io
def test_load_rotation_metadata_nonexistent():
    """load_rotation_metadata returns default dict when file doesn't exist."""
    result = load_rotation_metadata()
    assert result["last_rotation"] is None
    assert result["archive_count"] == 0


@pytest.mark.io
def test_load_rotation_metadata_success(temp_archive_dir, monkeypatch):
    """load_rotation_metadata successfully loads metadata."""
    monkeypatch.setattr(
        "scripts.rotate_session_cost_log.ROTATION_METADATA_FILE",
        temp_archive_dir / "rotation_metadata.json",
    )
    metadata_file = temp_archive_dir / "rotation_metadata.json"
    test_metadata = {
        "last_rotation": "2026-03-27T10:00:00+00:00",
        "archive_count": 2,
        "total_archived_records": 500,
    }
    metadata_file.write_text(json.dumps(test_metadata), encoding="utf-8")
    result = load_rotation_metadata()
    assert result["archive_count"] == 2


@pytest.mark.io
def test_perform_rotation_empty_log(temp_log_file):
    """perform_rotation handles empty log file gracefully."""
    temp_log_file.write_text(json.dumps([]), encoding="utf-8")
    result = perform_rotation(temp_log_file, retention_days=90)
    assert result["success"] is True
    assert result["archived_count"] == 0


@pytest.mark.io
def test_perform_rotation_no_archivable_records(temp_log_file):
    """perform_rotation returns success when no records are old enough to archive."""
    recent_ts = datetime.now(timezone.utc).isoformat()
    records = [
        {
            "session_id": "test",
            "model": "claude",
            "tokens_in": 100,
            "tokens_out": 50,
            "phase": "Phase 1",
            "timestamp": recent_ts,
        }
    ]
    temp_log_file.write_text(json.dumps(records), encoding="utf-8")
    result = perform_rotation(temp_log_file, retention_days=90)
    assert result["success"] is True
    assert result["archived_count"] == 0


@pytest.mark.io
def test_perform_rotation_dry_run(temp_log_file, sample_records, monkeypatch):
    """perform_rotation with --dry-run does not write files."""
    monkeypatch.setattr(
        "scripts.rotate_session_cost_log.ARCHIVE_DIR",
        temp_log_file.parent / ".cache" / "session_cost_archives",
    )
    temp_log_file.write_text(json.dumps(sample_records), encoding="utf-8")
    result = perform_rotation(temp_log_file, retention_days=90, dry_run=True)
    assert result["success"] is True
    assert result["action"] == "DRY_RUN"
    assert result["archived_count"] == 2  # Two records old enough to archive
    # Verify main log file still has all 4 records
    retained = json.loads(temp_log_file.read_text())
    assert len(retained) == 4


@pytest.mark.io
def test_perform_rotation_success(temp_log_file, sample_records, monkeypatch):
    """perform_rotation successfully archives old records and updates main log."""
    archive_dir = temp_log_file.parent / ".cache" / "session_cost_archives"
    monkeypatch.setattr("scripts.rotate_session_cost_log.ARCHIVE_DIR", archive_dir)
    monkeypatch.setattr(
        "scripts.rotate_session_cost_log.ROTATION_METADATA_FILE",
        archive_dir / "rotation_metadata.json",
    )

    temp_log_file.write_text(json.dumps(sample_records), encoding="utf-8")
    result = perform_rotation(temp_log_file, retention_days=90)

    assert result["success"] is True
    assert result["archived_count"] == 2
    assert result["retained_count"] == 2

    # Verify main log contains only recent records
    retained = json.loads(temp_log_file.read_text())
    assert len(retained) == 2
    assert all(s in [r["session_id"] for r in retained] for s in ["recent/2026-03-20", "recent/2026-03-27"])

    # Verify archive file was created
    archive_files = list(archive_dir.glob("session_cost_log_archive_*.json"))
    assert len(archive_files) == 1


@pytest.mark.io
def test_rotation_to_aggregation_integration(temp_log_file, sample_records, monkeypatch):
    """Rotation archives old rows and aggregate_log re-includes them by default."""
    archive_dir = temp_log_file.parent / ".cache" / "session_cost_archives"
    monkeypatch.setattr("scripts.rotate_session_cost_log.ARCHIVE_DIR", archive_dir)
    monkeypatch.setattr(
        "scripts.rotate_session_cost_log.ROTATION_METADATA_FILE",
        archive_dir / "rotation_metadata.json",
    )

    temp_log_file.write_text(json.dumps(sample_records), encoding="utf-8")
    rotation_result = perform_rotation(temp_log_file, retention_days=90)

    assert rotation_result["success"] is True
    assert rotation_result["archived_count"] == 2
    assert len(list(archive_dir.glob("session_cost_log_archive_*.json"))) == 1

    payload_with_archives = aggregate_log(log_file=temp_log_file)
    payload_no_archives = aggregate_log(log_file=temp_log_file, include_archives=False)

    assert sum(group["record_count"] for group in payload_with_archives["groups"]) == len(sample_records)
    assert sum(group["record_count"] for group in payload_no_archives["groups"]) == rotation_result["retained_count"]


@pytest.mark.io
def test_perform_rotation_invalid_retention_days():
    """perform_rotation raises ValueError for negative retention_days."""
    with pytest.raises(ValueError, match="retention_days must be non-negative"):
        perform_rotation(Path("/tmp/dummy.json"), retention_days=-1)


@pytest.mark.io
def test_check_rotation_needed_nonexistent_file():
    """check_rotation_needed returns False for nonexistent log file."""
    result = check_rotation_needed(
        Path("/nonexistent/log.json"), size_threshold_bytes=10000000, last_rotation_threshold_days=30
    )
    assert result["rotation_needed"] is False


@pytest.mark.io
def test_check_rotation_needed_exceeds_size_threshold(temp_log_file, sample_records):
    """check_rotation_needed returns True when file size exceeds threshold."""
    temp_log_file.write_text(json.dumps(sample_records), encoding="utf-8")
    # Set a very low threshold so the file exceeds it
    result = check_rotation_needed(temp_log_file, size_threshold_bytes=10, last_rotation_threshold_days=30)
    assert result["rotation_needed"] is True
    assert result["trigger"] == "size"


@pytest.mark.io
def test_check_rotation_needed_within_thresholds(temp_log_file, sample_records):
    """check_rotation_needed returns False when all thresholds are within limits."""
    temp_log_file.write_text(json.dumps(sample_records), encoding="utf-8")
    # Set a high threshold and recent last_rotation
    result = check_rotation_needed(
        temp_log_file,
        size_threshold_bytes=10485760,
        last_rotation_threshold_days=30,  # 10MB threshold
    )
    assert result["rotation_needed"] is False
