"""Tests for scripts/session_cost_log.py"""

import json
import subprocess
from pathlib import Path

import pytest

from scripts.session_cost_log import log_session_cost, main, read_log


@pytest.fixture
def temp_log_file(tmp_path, monkeypatch):
    """Use a temporary log file for tests."""
    log_file = tmp_path / "session_cost_log.json"
    monkeypatch.setattr("scripts.session_cost_log.LOG_FILE", log_file)
    return log_file


@pytest.mark.io
def test_log_session_cost_happy_path(temp_log_file):
    """Happy path: log_session_cost writes record with all six fields."""
    log_session_cost(
        session_id="main/2026-03-27",
        model="claude-sonnet-4",
        tokens_in=1500,
        tokens_out=800,
        phase="Phase 1",
        timestamp="2026-03-27T14:30:00Z",
    )

    assert temp_log_file.exists()
    with open(temp_log_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    assert len(records) == 1
    record = records[0]
    assert record["session_id"] == "main/2026-03-27"
    assert record["model"] == "claude-sonnet-4"
    assert record["tokens_in"] == 1500
    assert record["tokens_out"] == 800
    assert record["phase"] == "Phase 1"
    assert record["timestamp"] == "2026-03-27T14:30:00Z"


@pytest.mark.io
def test_log_session_cost_append(temp_log_file):
    """Append: multiple calls append; prior records not overwritten."""
    log_session_cost("session-1", "model-a", 100, 50, "Phase 1", "2026-03-27T10:00:00Z")
    log_session_cost("session-2", "model-b", 200, 100, "Phase 2", "2026-03-27T11:00:00Z")
    log_session_cost("session-3", "model-a", 150, 75, "Phase 3", "2026-03-27T12:00:00Z")

    records = read_log()
    assert len(records) == 3
    assert records[0]["session_id"] == "session-1"
    assert records[1]["session_id"] == "session-2"
    assert records[2]["session_id"] == "session-3"


@pytest.mark.io
def test_read_log_returns_correct_count(temp_log_file):
    """read_log returns correct count after N writes."""
    # Initially empty
    assert read_log() == []

    # After 2 writes
    log_session_cost("s1", "m1", 10, 5, "p1", "2026-03-27T10:00:00Z")
    log_session_cost("s2", "m2", 20, 10, "p2", "2026-03-27T11:00:00Z")
    assert len(read_log()) == 2

    # After 3rd write
    log_session_cost("s3", "m3", 30, 15, "p3", "2026-03-27T12:00:00Z")
    assert len(read_log()) == 3


@pytest.mark.io
def test_dry_run_no_file_written(tmp_path, monkeypatch):
    """--dry-run: no file written, stdout contains expected record."""
    log_file = tmp_path / "session_cost_log.json"
    monkeypatch.setattr("scripts.session_cost_log.LOG_FILE", log_file)

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/session_cost_log.py",
            "--dry-run",
            "--session",
            "test-session",
            "--model",
            "test-model",
            "--tokens-in",
            "1000",
            "--tokens-out",
            "500",
            "--phase",
            "Test Phase",
            "--timestamp",
            "2026-03-27T14:00:00Z",
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 0
    assert "DRY RUN" in result.stdout
    assert "test-session" in result.stdout
    assert "test-model" in result.stdout
    assert not log_file.exists(), "Dry-run should not create log file"


def test_invalid_input_missing_field():
    """Invalid input: missing required field raises ValueError."""
    with pytest.raises(ValueError, match="session_id must be a non-empty string"):
        log_session_cost("", "model", 100, 50, "phase", "2026-03-27T10:00:00Z")

    with pytest.raises(ValueError, match="model must be a non-empty string"):
        log_session_cost("session", "", 100, 50, "phase", "2026-03-27T10:00:00Z")

    with pytest.raises(ValueError, match="tokens_in must be a non-negative integer"):
        log_session_cost("session", "model", -1, 50, "phase", "2026-03-27T10:00:00Z")

    with pytest.raises(ValueError, match="tokens_out must be a non-negative integer"):
        log_session_cost("session", "model", 100, -1, "phase", "2026-03-27T10:00:00Z")

    with pytest.raises(ValueError, match="phase must be a non-empty string"):
        log_session_cost("session", "model", 100, 50, "", "2026-03-27T10:00:00Z")

    with pytest.raises(ValueError, match="timestamp must be a non-empty string"):
        log_session_cost("session", "model", 100, 50, "phase", "")


@pytest.mark.io
def test_cli_success(tmp_path, monkeypatch):
    """CLI writes record successfully."""
    log_file = tmp_path / "session_cost_log.json"
    monkeypatch.setattr("scripts.session_cost_log.LOG_FILE", log_file)

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/session_cost_log.py",
            "--session",
            "cli-test",
            "--model",
            "test-model",
            "--tokens-in",
            "2000",
            "--tokens-out",
            "1000",
            "--phase",
            "CLI Phase",
            "--timestamp",
            "2026-03-27T15:00:00Z",
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 0
    assert "Logged session cost" in result.stdout


@pytest.mark.io
def test_main_success(temp_log_file, monkeypatch):
    """Direct main() call with full args writes record and exits 0."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "session_cost_log.py",
            "--session",
            "main-test/2026-03-27",
            "--model",
            "claude-sonnet-4",
            "--tokens-in",
            "1200",
            "--tokens-out",
            "600",
            "--phase",
            "Phase 2",
            "--timestamp",
            "2026-03-27T16:00:00Z",
        ],
    )

    rc = main()
    assert rc == 0
    assert temp_log_file.exists()

    records = read_log()
    assert len(records) == 1
    assert records[0]["session_id"] == "main-test/2026-03-27"
    assert records[0]["tokens_in"] == 1200


@pytest.mark.io
def test_main_dry_run(temp_log_file, monkeypatch, capsys):
    """Direct main() call with --dry-run does not write file, prints record."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "session_cost_log.py",
            "--dry-run",
            "--session",
            "dry-session",
            "--model",
            "test-model",
            "--tokens-in",
            "500",
            "--tokens-out",
            "250",
            "--phase",
            "Dry Phase",
            "--timestamp",
            "2026-03-27T17:00:00Z",
        ],
    )

    rc = main()
    assert rc == 0
    assert not temp_log_file.exists(), "Dry-run should not create file"

    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out
    assert "dry-session" in captured.out


def test_main_invalid_args(monkeypatch):
    """Direct main() call with missing --session raises SystemExit."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "session_cost_log.py",
            "--model",
            "test-model",
            "--tokens-in",
            "100",
            "--tokens-out",
            "50",
            "--phase",
            "Phase",
            "--timestamp",
            "2026-03-27T18:00:00Z",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2  # argparse exits with 2 for missing required arg
