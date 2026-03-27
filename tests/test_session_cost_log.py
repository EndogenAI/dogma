"""Tests for scripts/session_cost_log.py"""

import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts.session_cost_log import REQUIRED_RECORD_KEYS, log_session_cost, main, read_log


@pytest.fixture
def temp_log_file(tmp_path, monkeypatch):
    """Use a temporary log file for tests."""
    log_file = tmp_path / "session_cost_log.json"
    monkeypatch.setenv("SESSION_COST_LOG_FILE", str(log_file))
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
    assert set(record.keys()) == set(REQUIRED_RECORD_KEYS)
    assert record["session_id"] == "main/2026-03-27"
    assert record["model"] == "claude-sonnet-4"
    assert record["tokens_in"] == 1500
    assert record["tokens_out"] == 800
    assert record["phase"] == "Phase 1"
    assert record["timestamp"] == "2026-03-27T14:30:00Z"
    assert "synthetic" not in record


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
    monkeypatch.setenv("SESSION_COST_LOG_FILE", str(log_file))

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

    with pytest.raises(ValueError, match="zero-token records require synthetic=true"):
        log_session_cost("session", "model", 0, 0, "phase", "2026-03-27T10:00:00Z")


@pytest.mark.io
def test_log_session_cost_allows_zero_with_synthetic(temp_log_file):
    """Zero-token records are accepted only when explicitly marked synthetic."""
    log_session_cost(
        "synthetic-session",
        "model",
        0,
        0,
        "phase",
        "2026-03-27T10:00:00Z",
        synthetic=True,
    )

    records = read_log()
    assert len(records) == 1
    assert records[0].get("synthetic") is True


@pytest.mark.io
def test_read_log_exclude_synthetic_filter(temp_log_file):
    """read_log(exclude_synthetic=True) should return non-synthetic records only."""
    log_session_cost("real-session", "model", 10, 5, "phase", "2026-03-27T10:00:00Z")
    log_session_cost(
        "synthetic-session",
        "model",
        0,
        0,
        "phase",
        "2026-03-27T11:00:00Z",
        synthetic=True,
    )

    all_records = read_log()
    filtered = read_log(exclude_synthetic=True)
    assert len(all_records) == 2
    assert len(filtered) == 1
    assert filtered[0]["session_id"] == "real-session"


@pytest.mark.io
def test_env_var_path_override_applies_without_reimport(tmp_path, monkeypatch):
    """Function calls should honor SESSION_COST_LOG_FILE set after import."""
    log_file = tmp_path / "override.json"
    monkeypatch.setenv("SESSION_COST_LOG_FILE", str(log_file))

    log_session_cost("env-test", "model-a", 12, 6, "Phase 1", "2026-03-27T09:00:00Z")

    assert log_file.exists()
    records = json.loads(log_file.read_text(encoding="utf-8"))
    assert records[0]["session_id"] == "env-test"


@pytest.mark.io
def test_cli_success(tmp_path):
    """CLI writes record successfully when SESSION_COST_LOG_FILE env var is set."""
    log_file = tmp_path / "session_cost_log.json"
    repo_log_file = Path(__file__).parent.parent / "session_cost_log.json"
    repo_log_before = repo_log_file.read_bytes() if repo_log_file.exists() else None
    env = os.environ.copy()
    env["SESSION_COST_LOG_FILE"] = str(log_file)

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
        env=env,
    )

    assert result.returncode == 0
    assert "Logged session cost" in result.stdout
    assert log_file.exists(), "Log file should be written to SESSION_COST_LOG_FILE path"
    if repo_log_before is None:
        assert not repo_log_file.exists()
    else:
        assert repo_log_file.read_bytes() == repo_log_before


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


def test_main_zero_requires_synthetic(temp_log_file, monkeypatch, capsys):
    """CLI main returns 1 for zero-token records unless --synthetic is provided."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "session_cost_log.py",
            "--session",
            "zero-session",
            "--model",
            "test-model",
            "--tokens-in",
            "0",
            "--tokens-out",
            "0",
            "--phase",
            "Phase",
            "--timestamp",
            "2026-03-27T17:30:00Z",
        ],
    )

    rc = main()
    assert rc == 1
    assert not temp_log_file.exists()
    captured = capsys.readouterr()
    assert "zero-token records require synthetic=true" in captured.err


@pytest.mark.io
def test_main_zero_with_synthetic_flag(temp_log_file, monkeypatch):
    """CLI main accepts zero-token records when --synthetic is passed."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "session_cost_log.py",
            "--session",
            "zero-synthetic-session",
            "--model",
            "test-model",
            "--tokens-in",
            "0",
            "--tokens-out",
            "0",
            "--phase",
            "Phase",
            "--timestamp",
            "2026-03-27T17:30:00Z",
            "--synthetic",
        ],
    )

    rc = main()
    assert rc == 0
    records = read_log()
    assert len(records) == 1
    assert records[0].get("synthetic") is True


def test_main_invalid_values_return_1(temp_log_file, monkeypatch, capsys):
    """Direct main() call with invalid values returns 1 and does not write a file."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "session_cost_log.py",
            "--session",
            "invalid-session",
            "--model",
            "test-model",
            "--tokens-in",
            "-1",
            "--tokens-out",
            "5",
            "--phase",
            "Phase",
            "--timestamp",
            "2026-03-27T17:30:00Z",
        ],
    )

    rc = main()
    assert rc == 1
    assert not temp_log_file.exists()
    captured = capsys.readouterr()
    assert "tokens_in must be a non-negative integer" in captured.err


@pytest.mark.io
def test_read_log_rejects_noncanonical_record_schema(temp_log_file):
    """Existing records must use required keys plus supported optional keys only."""
    temp_log_file.write_text(
        json.dumps(
            [
                {
                    "session_id": "bad-session",
                    "model": "test-model",
                    "tokens_in": 1,
                    "tokens_out": 2,
                    "phase": "Phase",
                    "timestamp": "2026-03-27T18:00:00Z",
                    "extra": True,
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unsupported keys"):
        read_log()


@pytest.mark.io
def test_read_log_normalizes_legacy_zero_token_record(temp_log_file):
    """Legacy zero-token rows without synthetic should normalize to synthetic=True on read."""
    temp_log_file.write_text(
        json.dumps(
            [
                {
                    "session_id": "legacy-zero",
                    "model": "test-model",
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "phase": "legacy",
                    "timestamp": "2026-03-27T18:00:00Z",
                }
            ]
        ),
        encoding="utf-8",
    )

    records = read_log()
    assert len(records) == 1
    assert records[0]["session_id"] == "legacy-zero"
    assert records[0].get("synthetic") is True


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
