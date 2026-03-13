"""
tests/test_export_project_state.py

Unit tests for scripts/export_project_state.py.

Coverage targets
----------------
- Happy path: writes expected JSON structure to output path
- --check with fresh file: prints "fresh" and exits 0
- --check with stale file: exits 1
- --check with absent file: exits 1
- gh CLI failure (non-zero exit): script exits 1
- Missing parent dir: auto-created
- --quiet suppresses stdout output on happy path

Markers
-------
@pytest.mark.io   — tests that perform file I/O
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import export_project_state  # noqa: E402

# ---------------------------------------------------------------------------
# Sample gh CLI responses
# ---------------------------------------------------------------------------

SAMPLE_ISSUES = [
    {
        "number": 1,
        "title": "Test issue",
        "state": "open",
        "labels": [{"name": "type:bug", "color": "d73a4a", "description": ""}],
    },
    {
        "number": 2,
        "title": "Closed issue",
        "state": "closed",
        "labels": [],
    },
]

SAMPLE_LABELS = [
    {"name": "type:bug", "color": "d73a4a", "description": "Something isn't working"},
    {"name": "priority:high", "color": "e4e669", "description": "This sprint"},
]


def _make_mock_run(issues: list | None = None, labels: list | None = None, returncode: int = 0):
    """Build a side_effect function for subprocess.run that returns gh responses."""
    _issues = issues if issues is not None else SAMPLE_ISSUES
    _labels = labels if labels is not None else SAMPLE_LABELS

    def _side_effect(cmd, **kwargs):
        mock = MagicMock()
        mock.returncode = returncode
        mock.stderr = "gh error" if returncode != 0 else ""
        if returncode != 0:
            mock.stdout = ""
            return mock
        # Determine which gh subcommand was called
        if "issue" in cmd:
            mock.stdout = json.dumps(_issues)
        else:
            mock.stdout = json.dumps(_labels)
        return mock

    return _side_effect


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_export_writes_json(tmp_path):
    """Happy path: writes valid JSON with correct structure to output path."""
    output = tmp_path / "state.json"

    with patch("subprocess.run", side_effect=_make_mock_run()):
        rc = export_project_state.main(["--output", str(output)])

    assert rc == 0
    assert output.exists()
    data = json.loads(output.read_text())
    assert "issues" in data
    assert "labels" in data
    assert "generated_at" in data
    assert len(data["issues"]) == 2
    assert len(data["labels"]) == 2
    assert data["issues"][0]["number"] == 1


@pytest.mark.io
def test_export_creates_parent_dir(tmp_path):
    """Missing parent directories are auto-created."""
    output = tmp_path / "nested" / "deep" / "state.json"
    assert not output.parent.exists()

    with patch("subprocess.run", side_effect=_make_mock_run()):
        rc = export_project_state.main(["--output", str(output)])

    assert rc == 0
    assert output.exists()


@pytest.mark.io
def test_export_quiet_suppresses_output(tmp_path, capsys):
    """--quiet flag suppresses informational stdout messages."""
    output = tmp_path / "state.json"

    with patch("subprocess.run", side_effect=_make_mock_run()):
        rc = export_project_state.main(["--output", str(output), "--quiet"])

    assert rc == 0
    captured = capsys.readouterr()
    assert captured.out == ""


# ---------------------------------------------------------------------------
# --check flag
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_check_fresh_file_exits_0(tmp_path, capsys):
    """--check exits 0 when cached file is less than 4 hours old."""
    output = tmp_path / "state.json"
    fresh_time = datetime.now(tz=timezone.utc) - timedelta(hours=1)
    data = {
        "issues": [],
        "labels": [],
        "generated_at": fresh_time.isoformat(),
    }
    output.write_text(json.dumps(data), encoding="utf-8")

    rc = export_project_state.main(["--output", str(output), "--check"])

    assert rc == 0
    captured = capsys.readouterr()
    assert "FRESH" in captured.out


@pytest.mark.io
def test_check_stale_file_exits_1(tmp_path, capsys):
    """--check exits 1 when cached file is older than 4 hours."""
    output = tmp_path / "state.json"
    stale_time = datetime.now(tz=timezone.utc) - timedelta(hours=6)
    data = {
        "issues": [],
        "labels": [],
        "generated_at": stale_time.isoformat(),
    }
    output.write_text(json.dumps(data), encoding="utf-8")

    rc = export_project_state.main(["--output", str(output), "--check"])

    assert rc == 1
    captured = capsys.readouterr()
    assert "STALE" in captured.out


@pytest.mark.io
def test_check_absent_file_exits_1(tmp_path, capsys):
    """--check exits 1 when cached file does not exist."""
    output = tmp_path / "nonexistent.json"
    assert not output.exists()

    rc = export_project_state.main(["--output", str(output), "--check"])

    assert rc == 1
    captured = capsys.readouterr()
    assert "ABSENT" in captured.out


@pytest.mark.io
def test_check_malformed_json_exits_1(tmp_path, capsys):
    """--check exits 1 when cached file is malformed JSON."""
    output = tmp_path / "state.json"
    output.write_text("NOT JSON", encoding="utf-8")

    rc = export_project_state.main(["--output", str(output), "--check"])

    assert rc == 1
    captured = capsys.readouterr()
    assert "STALE" in captured.out


# ---------------------------------------------------------------------------
# gh CLI failure
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_gh_cli_failure_exits_1(tmp_path):
    """When gh returns non-zero exit code, script exits 1."""
    output = tmp_path / "state.json"

    with patch("subprocess.run", side_effect=_make_mock_run(returncode=1)):
        with pytest.raises(SystemExit) as exc_info:
            export_project_state.main(["--output", str(output)])

    assert exc_info.value.code == 1


@pytest.mark.io
def test_gh_not_found_exits_1(tmp_path):
    """When gh CLI is not in PATH, script exits 1."""
    output = tmp_path / "state.json"

    with patch("subprocess.run", side_effect=FileNotFoundError("gh not found")):
        with pytest.raises(SystemExit) as exc_info:
            export_project_state.main(["--output", str(output)])

    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# --fields filtering
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_fields_single_issues(tmp_path):
    """--fields issues produces output with only issues key (no labels)."""
    output = tmp_path / "state.json"

    with patch("subprocess.run", side_effect=_make_mock_run()):
        rc = export_project_state.main(["--output", str(output), "--fields", "issues"])

    assert rc == 0
    data = json.loads(output.read_text())
    assert "issues" in data
    assert "labels" not in data
    assert "generated_at" in data


@pytest.mark.io
def test_fields_issues_and_labels(tmp_path):
    """--fields issues,labels produces output with both keys and no extras."""
    output = tmp_path / "state.json"

    with patch("subprocess.run", side_effect=_make_mock_run()):
        rc = export_project_state.main(["--output", str(output), "--fields", "issues,labels"])

    assert rc == 0
    data = json.loads(output.read_text())
    assert "issues" in data
    assert "labels" in data
    assert "generated_at" in data
    # No unexpected top-level keys
    assert set(data.keys()) == {"issues", "labels", "generated_at"}


@pytest.mark.io
def test_fields_unknown_exits_1(tmp_path, capsys):
    """--fields unknown_field exits 1 with an error message naming the unknown field."""
    output = tmp_path / "state.json"

    rc = export_project_state.main(["--output", str(output), "--fields", "unknown_field"])

    assert rc == 1
    captured = capsys.readouterr()
    assert "unknown" in captured.err.lower()
    assert "unknown_field" in captured.err


@pytest.mark.io
def test_no_fields_all_present(tmp_path):
    """Default (no --fields) includes all known fields — backward-compat regression."""
    output = tmp_path / "state.json"

    with patch("subprocess.run", side_effect=_make_mock_run()):
        rc = export_project_state.main(["--output", str(output)])

    assert rc == 0
    data = json.loads(output.read_text())
    assert "issues" in data
    assert "labels" in data
    assert "generated_at" in data
