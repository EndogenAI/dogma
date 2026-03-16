"""Tests for scripts/preexec_audit_log.py."""

from __future__ import annotations

import json

import pytest

from scripts.preexec_audit_log import (
    command_prefix,
    main,
    record_invocation,
    summarise_log,
)

# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------


def test_command_prefix_simple():
    assert command_prefix("uv run pytest") == "uv"


def test_command_prefix_empty():
    assert command_prefix("   ") == "(empty)"


def test_command_prefix_single_token():
    assert command_prefix("ls") == "ls"


# ---------------------------------------------------------------------------
# record_invocation
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_record_invocation_creates_file(tmp_path):
    log = tmp_path / "audit.log"
    record_invocation(log, "uv run pytest", "/repo", "1")
    assert log.exists()
    lines = log.read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["command"] == "uv run pytest"
    assert entry["cwd"] == "/repo"
    assert entry["governor_enabled"] == "1"
    assert "timestamp" in entry


@pytest.mark.io
def test_record_invocation_appends(tmp_path):
    log = tmp_path / "audit.log"
    record_invocation(log, "cmd-one", "/a", "1")
    record_invocation(log, "cmd-two", "/b", "0")
    lines = log.read_text().splitlines()
    assert len(lines) == 2


@pytest.mark.io
def test_record_invocation_creates_parent_dirs(tmp_path):
    log = tmp_path / "nested" / "deep" / "audit.log"
    record_invocation(log, "echo hello", "/tmp", "")
    assert log.exists()


# ---------------------------------------------------------------------------
# summarise_log
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_summarise_log_no_file(tmp_path, capsys):
    log = tmp_path / "missing.log"
    summarise_log(log)
    captured = capsys.readouterr()
    assert "No audit log found" in captured.err


@pytest.mark.io
def test_summarise_log_empty_file(tmp_path, capsys):
    log = tmp_path / "audit.log"
    log.write_text("")
    summarise_log(log)
    captured = capsys.readouterr()
    assert "empty" in captured.out


@pytest.mark.io
def test_summarise_log_counts(tmp_path, capsys):
    log = tmp_path / "audit.log"
    record_invocation(log, "uv run pytest", "/repo", "1")
    record_invocation(log, "uv run ruff", "/repo", "1")
    record_invocation(log, "uv run pytest", "/repo", "1")
    summarise_log(log)
    captured = capsys.readouterr()
    assert "uv" in captured.out
    # uv appears 3 times total (all three commands start with "uv")
    assert "3" in captured.out


@pytest.mark.io
def test_summarise_log_skips_malformed_lines(tmp_path, capsys):
    log = tmp_path / "audit.log"
    log.write_text('not-json\n{"timestamp":"2026-01-01T00:00:00Z","command":"ls"}\n')
    summarise_log(log)
    captured = capsys.readouterr()
    # Should not crash; valid entry counted
    assert "ls" in captured.out


# ---------------------------------------------------------------------------
# main() CLI
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_main_records_command(tmp_path):
    log = tmp_path / "audit.log"
    rc = main(["--log", str(log), "--command", "pytest"])
    assert rc == 0
    lines = log.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["command"] == "pytest"


@pytest.mark.io
def test_main_summary_mode(tmp_path, capsys):
    log = tmp_path / "audit.log"
    record_invocation(log, "git status", "/repo", "1")
    rc = main(["--log", str(log), "--summary"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "git" in captured.out


def test_main_missing_command_exits_error(tmp_path):
    log = tmp_path / "audit.log"
    with pytest.raises(SystemExit) as exc_info:
        main(["--log", str(log)])
    assert exc_info.value.code != 0


@pytest.mark.io
def test_main_uses_env_governor_value(tmp_path, monkeypatch):
    log = tmp_path / "audit.log"
    monkeypatch.setenv("PREEXEC_GOVERNOR_ENABLED", "sentinel-value")
    rc = main(["--log", str(log), "--command", "echo hi"])
    assert rc == 0
    entry = json.loads(log.read_text().splitlines()[0])
    assert entry["governor_enabled"] == "sentinel-value"


@pytest.mark.io
def test_main_explicit_governor_value_overrides_env(tmp_path, monkeypatch):
    log = tmp_path / "audit.log"
    monkeypatch.setenv("PREEXEC_GOVERNOR_ENABLED", "from-env")
    rc = main(["--log", str(log), "--command", "echo hi", "--governor-value", "explicit"])
    assert rc == 0
    entry = json.loads(log.read_text().splitlines()[0])
    assert entry["governor_enabled"] == "explicit"
