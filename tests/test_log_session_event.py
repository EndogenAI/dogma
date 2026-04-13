"""
Tests for scripts/log_session_event.py

Validates event logging, schema validation, JSONL append, and error handling.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.io
def test_log_phase_complete_event(tmp_path, monkeypatch):
    """Test logging a phase_complete event with all fields."""
    # Set up temp cache dir
    cache_dir = tmp_path / ".cache"
    cache_dir.mkdir()

    # Mock cache location
    script_path = Path(__file__).parent.parent / "scripts" / "log_session_event.py"

    # Patch the events file location by creating a wrapper
    test_script = tmp_path / "test_log_event.py"
    test_script.write_text(
        f"""
import sys
sys.path.insert(0, '{script_path.parent.parent}')
from scripts.log_session_event import main

# Patch cache dir
from pathlib import Path
import scripts.log_session_event as mod
_orig_parent = Path(__file__).parent.parent / ".cache"
def _patched_parent():
    return Path('{cache_dir}')

# Run
if __name__ == '__main__':
    # Monkey patch the cache dir lookup
    import scripts.log_session_event
    _old_file = scripts.log_session_event.__file__
    scripts.log_session_event.__file__ = '{script_path}'
    try:
        sys.exit(main())
    finally:
        scripts.log_session_event.__file__ = _old_file
"""
    )

    # Run the script
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--type",
            "phase_complete",
            "--branch",
            "feat-test",
            "--phase",
            "Phase 7",
            "--agent",
            "Executive Scripter",
            "--issue",
            "552",
            "--commit",
            "abc123",
            "--deliverables",
            "file1.py,file2.yml",
            "--notes",
            "Test event",
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    # Should succeed
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Verify file was created and contains valid JSON
    real_events = Path(__file__).parent.parent / ".cache" / "session-events.jsonl"
    assert real_events.exists(), "Events file not created"

    # Read and parse last line
    lines = real_events.read_text().strip().split("\n")
    last_event = json.loads(lines[-1])

    # Verify fields
    assert last_event["event_type"] == "phase_complete"
    assert last_event["branch"] == "feat-test"
    assert last_event["phase"] == "Phase 7"
    assert last_event["agent"] == "Executive Scripter"
    assert last_event["issue"] == 552
    assert last_event["commit_sha"] == "abc123"
    assert last_event["deliverables"] == ["file1.py", "file2.yml"]
    assert last_event["notes"] == "Test event"
    assert "timestamp" in last_event


@pytest.mark.io
def test_log_session_start_multiple_issues(tmp_path):
    """Test logging session_start with multiple issues."""
    script_path = Path(__file__).parent.parent / "scripts" / "log_session_event.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--type",
            "session_start",
            "--agent",
            "Executive Orchestrator",
            "--issue",
            "551,552",
            "--notes",
            "Sprint kickoff",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    # Check that event was logged
    events_file = Path(__file__).parent.parent / ".cache" / "session-events.jsonl"
    lines = events_file.read_text().strip().split("\n")
    last_event = json.loads(lines[-1])

    assert last_event["event_type"] == "session_start"
    assert last_event["issue"] == [551, 552]


@pytest.mark.io
def test_invalid_event_type():
    """Test that invalid event_type is rejected."""
    script_path = Path(__file__).parent.parent / "scripts" / "log_session_event.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--type",
            "invalid_event",
            "--agent",
            "Test",
        ],
        capture_output=True,
        text=True,
    )

    # Should fail
    assert result.returncode == 1
    assert "Invalid event_type" in result.stderr


@pytest.mark.io
def test_minimal_event():
    """Test logging event with only required fields."""
    script_path = Path(__file__).parent.parent / "scripts" / "log_session_event.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--type",
            "commit",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    # Verify minimal event has required fields
    events_file = Path(__file__).parent.parent / ".cache" / "session-events.jsonl"
    lines = events_file.read_text().strip().split("\n")
    last_event = json.loads(lines[-1])

    assert last_event["event_type"] == "commit"
    assert "timestamp" in last_event
    assert "branch" in last_event


@pytest.mark.io
def test_jsonl_append_preserves_existing():
    """Test that new events are appended without overwriting existing ones."""
    script_path = Path(__file__).parent.parent / "scripts" / "log_session_event.py"
    events_file = Path(__file__).parent.parent / ".cache" / "session-events.jsonl"

    # Get initial line count
    if events_file.exists():
        initial_count = len(events_file.read_text().strip().split("\n"))
    else:
        initial_count = 0

    # Log 2 events
    for i in range(2):
        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--type",
                "delegation",
                "--notes",
                f"Event {i}",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    # Verify count increased by 2
    final_count = len(events_file.read_text().strip().split("\n"))
    assert final_count == initial_count + 2


@pytest.mark.io
def test_schema_validation_missing_required():
    """Test that events with missing required fields are rejected."""
    # Note: Currently timestamp, event_type, and branch are always set
    # This test validates the validation logic exists
    from scripts.log_session_event import validate_event

    schema = {
        "required": ["timestamp", "event_type", "branch"],
        "properties": {"event_type": {"enum": ["session_start", "phase_complete"]}},
    }

    # Missing timestamp
    event = {"event_type": "session_start", "branch": "test"}
    is_valid, msg = validate_event(event, schema)
    assert not is_valid
    assert "timestamp" in msg


@pytest.mark.io
def test_deliverables_parsing():
    """Test that comma-separated deliverables are parsed correctly."""
    script_path = Path(__file__).parent.parent / "scripts" / "log_session_event.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--type",
            "phase_complete",
            "--deliverables",
            "file1.py, file2.yml, file3.md",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    events_file = Path(__file__).parent.parent / ".cache" / "session-events.jsonl"
    lines = events_file.read_text().strip().split("\n")
    last_event = json.loads(lines[-1])

    assert last_event["deliverables"] == ["file1.py", "file2.yml", "file3.md"]
