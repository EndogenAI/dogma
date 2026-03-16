"""Tests for scripts/token_spin_detector.py."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.token_spin_detector import (
    _normalise_command,
    _parse_timestamp,
    detect_spinning,
    load_entries,
    main,
)

# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------


def _ts(offset_seconds: float = 0.0) -> str:
    """Return an ISO-8601 UTC timestamp *offset_seconds* before now."""
    epoch = datetime.now(tz=timezone.utc).timestamp() - offset_seconds
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _make_entry(command: str, offset_seconds: float = 0.0) -> dict:
    return {"timestamp": _ts(offset_seconds), "command": command, "cwd": "/repo"}


def _write_entries(log: Path, entries: list[dict]) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# _normalise_command
# ---------------------------------------------------------------------------


def test_normalise_command_two_tokens():
    assert _normalise_command("uv run pytest") == "uv run"


def test_normalise_command_one_token():
    assert _normalise_command("ls") == "ls"


def test_normalise_command_empty():
    assert _normalise_command("") == ""


# ---------------------------------------------------------------------------
# _parse_timestamp
# ---------------------------------------------------------------------------


def test_parse_timestamp_roundtrip():
    ts_str = "2026-03-15T12:00:00Z"
    result = _parse_timestamp(ts_str)
    assert isinstance(result, float)
    assert result > 0


# ---------------------------------------------------------------------------
# load_entries
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_load_entries_missing_file(tmp_path):
    log = tmp_path / "missing.log"
    assert load_entries(log) == []


@pytest.mark.io
def test_load_entries_skips_malformed(tmp_path):
    log = tmp_path / "audit.log"
    log.write_text('not-json\n{"timestamp":"2026-01-01T00:00:00Z","command":"ls"}\n')
    entries = load_entries(log)
    assert len(entries) == 1
    assert entries[0]["command"] == "ls"


@pytest.mark.io
def test_load_entries_skips_missing_fields(tmp_path):
    log = tmp_path / "audit.log"
    # Entry with no 'command' key is filtered out
    log.write_text(json.dumps({"timestamp": "2026-01-01T00:00:00Z"}) + "\n")
    entries = load_entries(log)
    assert entries == []


# ---------------------------------------------------------------------------
# detect_spinning
# ---------------------------------------------------------------------------


def test_no_spinning_below_threshold():
    entries = [_make_entry("uv run pytest") for _ in range(4)]
    result = detect_spinning(entries, threshold=5, window=60)
    assert result == []


def test_spinning_at_threshold():
    entries = [_make_entry("uv run pytest") for _ in range(5)]
    result = detect_spinning(entries, threshold=5, window=60)
    assert len(result) == 1
    assert result[0][0] == "uv run"
    assert result[0][1] == 5


def test_spinning_above_threshold():
    entries = [_make_entry("uv run pytest") for _ in range(8)]
    result = detect_spinning(entries, threshold=5, window=60)
    assert result[0][1] == 8


def test_no_spinning_outside_window():
    """Entries older than the window do not count."""
    # 5 entries, all 120 seconds old — outside a 60s window
    entries = [_make_entry("uv run pytest", offset_seconds=120) for _ in range(5)]
    result = detect_spinning(entries, threshold=5, window=60)
    assert result == []


def test_spinning_only_counts_within_window():
    """3 entries inside window + 3 outside = does not reach threshold of 5."""
    inside = [_make_entry("uv run pytest", offset_seconds=10) for _ in range(3)]
    outside = [_make_entry("uv run pytest", offset_seconds=120) for _ in range(3)]
    result = detect_spinning(inside + outside, threshold=5, window=60)
    assert result == []


def test_multiple_commands_independent():
    entries = [_make_entry("uv run pytest") for _ in range(5)] + [_make_entry("git status") for _ in range(2)]
    result = detect_spinning(entries, threshold=5, window=60)
    assert len(result) == 1
    cmds = [r[0] for r in result]
    assert "uv run" in cmds
    assert "git status" not in cmds


# ---------------------------------------------------------------------------
# main() CLI
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_main_check_no_spinning(tmp_path):
    log = tmp_path / "audit.log"
    entries = [_make_entry("uv run pytest") for _ in range(3)]
    _write_entries(log, entries)
    rc = main(["--check", "--log", str(log), "--threshold", "5"])
    assert rc == 0


@pytest.mark.io
def test_main_check_spin_detected(tmp_path, capsys):
    log = tmp_path / "audit.log"
    entries = [_make_entry("uv run pytest") for _ in range(5)]
    _write_entries(log, entries)
    rc = main(["--check", "--log", str(log), "--threshold", "5"])
    assert rc == 2
    captured = capsys.readouterr()
    assert "SPIN DETECTED" in captured.err


@pytest.mark.io
def test_main_dry_run_does_not_exit_2(tmp_path, capsys):
    log = tmp_path / "audit.log"
    entries = [_make_entry("uv run pytest") for _ in range(10)]
    _write_entries(log, entries)
    rc = main(["--dry-run", "--log", str(log), "--threshold", "5"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "SPIN DETECTED" in captured.err


@pytest.mark.io
def test_main_missing_log_returns_0(tmp_path):
    log = tmp_path / "nonexistent.log"
    rc = main(["--check", "--log", str(log)])
    assert rc == 0


def test_main_no_mode_flag_exits_error(tmp_path):
    log = tmp_path / "audit.log"
    log.write_text("")
    with pytest.raises(SystemExit) as exc_info:
        main(["--log", str(log)])
    assert exc_info.value.code != 0


@pytest.mark.io
def test_main_custom_window_and_threshold(tmp_path):
    log = tmp_path / "audit.log"
    # 3 invocations within a 30s window; threshold = 3 → should flag
    entries = [_make_entry("git diff", offset_seconds=5) for _ in range(3)]
    _write_entries(log, entries)
    rc = main(["--check", "--log", str(log), "--threshold", "3", "--window", "30"])
    assert rc == 2
