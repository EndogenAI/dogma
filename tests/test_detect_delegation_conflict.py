"""tests/test_detect_delegation_conflict.py — Tests for scripts/detect_delegation_conflict.py.

Covers:
    - Conflict-free scope: exits 0 and returns safe=true with empty conflicts list.
    - Single constraint violation: exits 1 with one entry in conflicts.
    - Multi-conflict scope: exits 1 with ≥2 entries in conflicts.
    - Missing YAML file: exits 2 with an error message.
"""

from __future__ import annotations

import importlib
import json
import textwrap
from pathlib import Path

import pytest

# Load the module under test
_mod = importlib.import_module("scripts.detect_delegation_conflict")
main = _mod.main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_yaml(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content), encoding="utf-8")


def _make_data_dir(tmp_path: Path) -> Path:
    """Scaffold a minimal data dir with both required YAML files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    _write_yaml(
        data_dir / "l2-constraints.yml",
        """\
        constraints:
          - id: "no-force-push-to-main"
            description: "Never git push --force to main."
            enforcement: "runtime"
            severity: "blocking"

          - id: "no-heredoc-writes"
            description: "Never use heredocs to write Markdown content."
            enforcement: "pre-commit"
            severity: "blocking"

          - id: "no-secrets-in-commits"
            description: "Never commit secrets, API keys, or credentials."
            enforcement: "pre-commit"
            severity: "blocking"
        """,
    )

    _write_yaml(
        data_dir / "decision-tables.yml",
        """\
        decision_tables:
          - situation: "A task has been performed interactively more than twice"
            action: "Encode as a script."
            rationale: "Programmatic-First Principle."
            agent: "Executive Scripter"
        """,
    )

    return data_dir


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_conflict_free_scope_exits_0(tmp_path: Path) -> None:
    """A benign scope produces safe=true and exits 0."""
    data_dir = _make_data_dir(tmp_path)
    exit_code = main(["--scope", "delegate a research task to the Scout agent", "--data-dir", str(data_dir)])
    assert exit_code == 0


@pytest.mark.io
def test_conflict_free_scope_output_is_safe(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Output JSON for a safe scope has safe=true and an empty conflicts list."""
    data_dir = _make_data_dir(tmp_path)
    main(["--scope", "run pytest on the test suite", "--data-dir", str(data_dir)])
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["safe"] is True
    assert result["conflicts"] == []


@pytest.mark.io
def test_single_violation_exits_1(tmp_path: Path) -> None:
    """A scope containing a no-force-push trigger exits 1."""
    data_dir = _make_data_dir(tmp_path)
    exit_code = main(["--scope", "git push --force to main branch", "--data-dir", str(data_dir)])
    assert exit_code == 1


@pytest.mark.io
def test_single_violation_conflict_list(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Single constraint violation populates conflicts with one entry."""
    data_dir = _make_data_dir(tmp_path)
    main(["--scope", "git push --force to main branch", "--data-dir", str(data_dir)])
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["safe"] is False
    assert len(result["conflicts"]) == 1
    assert result["conflicts"][0]["id"] == "no-force-push-to-main"


@pytest.mark.io
def test_multi_conflict_exits_1(tmp_path: Path) -> None:
    """A scope triggering two constraints exits 1."""
    data_dir = _make_data_dir(tmp_path)
    exit_code = main(["--scope", "git push --force and commit secret api key", "--data-dir", str(data_dir)])
    assert exit_code == 1


@pytest.mark.io
def test_multi_conflict_two_items(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Multi-conflict scope produces at least 2 entries in conflicts."""
    data_dir = _make_data_dir(tmp_path)
    main(["--scope", "git push --force and commit secret api key", "--data-dir", str(data_dir)])
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["safe"] is False
    assert len(result["conflicts"]) >= 2


@pytest.mark.io
def test_missing_l2_constraints_file_exits_2(tmp_path: Path) -> None:
    """Missing l2-constraints.yml exits 2."""
    data_dir = tmp_path / "empty_data"
    data_dir.mkdir()
    # Write only decision-tables.yml (omit l2-constraints.yml)
    _write_yaml(
        data_dir / "decision-tables.yml",
        """\
        decision_tables:
          - situation: "any"
            action: "do something"
            rationale: "reason"
            agent: "Orchestrator"
        """,
    )
    exit_code = main(["--scope", "run anything", "--data-dir", str(data_dir)])
    assert exit_code == 2


@pytest.mark.io
def test_missing_decision_tables_file_exits_2(tmp_path: Path) -> None:
    """Missing decision-tables.yml exits 2."""
    data_dir = tmp_path / "partial_data"
    data_dir.mkdir()
    _write_yaml(
        data_dir / "l2-constraints.yml",
        """\
        constraints:
          - id: "no-force-push-to-main"
            description: "Never force push to main."
            enforcement: "runtime"
            severity: "blocking"
        """,
    )
    exit_code = main(["--scope", "run anything", "--data-dir", str(data_dir)])
    assert exit_code == 2


@pytest.mark.io
def test_empty_scope_exits_2(tmp_path: Path) -> None:
    """An empty scope string exits 2."""
    data_dir = _make_data_dir(tmp_path)
    exit_code = main(["--scope", "   ", "--data-dir", str(data_dir)])
    assert exit_code == 2


@pytest.mark.io
def test_no_scope_arg_exits_2(tmp_path: Path) -> None:
    """Providing neither --scope nor --stdin exits 2."""
    data_dir = _make_data_dir(tmp_path)
    exit_code = main(["--data-dir", str(data_dir)])
    assert exit_code == 2
