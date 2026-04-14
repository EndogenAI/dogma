"""tests/test_export_scratchpad.py

Test suite for scripts/export_scratchpad.py — validates export functionality
for scratchpad files in JSON, YAML, and Markdown formats.

Covers:
    - Export to JSON produces valid JSON
    - Export to YAML produces valid YAML
    - Round-trip: export → parse → structure preserved
    - --all mode exports multiple files
    - Invalid input fails gracefully
    - Metadata extraction
    - Phase extraction with consecutive numbering
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def valid_scratchpad(tmp_path: Path) -> Path:
    """Create a minimal valid scratchpad file with phases."""
    branch_dir = tmp_path / ".tmp" / "feat-test-branch"
    branch_dir.mkdir(parents=True, exist_ok=True)

    scratchpad = branch_dir / "2026-04-13.md"
    scratchpad.write_text("""# Session — feat-test-branch / 2026-04-13

## Session State

```yaml
branch: feat-test-branch
date: '2026-04-13'
active_phase: "Phase 2"
active_issues: [123, 456]
blockers: []
last_agent: "Executive Orchestrator"
phases:
  - name: "Phase 1"
    status: "Complete"
  - name: "Phase 2"
    status: "In Progress"
```

## Audit Trail

| Agent | Decision | Justification | Time |
|-------|----------|---------------|------|
| Executive Orchestrator | Start Phase 1 | Workplan approved | 10:00 |
| Review | Approve Phase 1 | All checks passed | 11:00 |

## Telemetry

| Metric | Value |
|--------|-------|
| Phases complete | 1 |
| Delegations made | 2 |
| Rate-limit events | 0 |
| Estimated tokens used | 15000 |

## Phase 1 Output

**Date**: 2026-04-13
**Agent**: Research Scout
**Deliverables**: Initial findings documented.

## Phase 2 Output

**Date**: 2026-04-13
**Agent**: Executive Scripter
**Status**: In progress.
""")

    return scratchpad


@pytest.fixture
def scratchpad_with_multiple_files(tmp_path: Path) -> Path:
    """Create multiple scratchpad files for --all testing."""
    base_dir = tmp_path / ".tmp"

    # Branch 1
    branch1 = base_dir / "feat-branch-1"
    branch1.mkdir(parents=True, exist_ok=True)
    (branch1 / "2026-04-13.md").write_text("""# Session — feat-branch-1 / 2026-04-13

## Session State

```yaml
branch: feat-branch-1
date: '2026-04-13'
active_phase: null
active_issues: []
blockers: []
last_agent: null
phases: []
```

## Audit Trail

| Agent | Decision | Justification | Time |
|-------|----------|---------------|------|

## Telemetry

| Metric | Value |
|--------|-------|
| Phases complete | 0 |
""")

    # Branch 2
    branch2 = base_dir / "feat-branch-2"
    branch2.mkdir(parents=True, exist_ok=True)
    (branch2 / "2026-04-14.md").write_text("""# Session — feat-branch-2 / 2026-04-14

## Session State

```yaml
branch: feat-branch-2
date: '2026-04-14'
active_phase: null
active_issues: []
blockers: []
last_agent: null
phases: []
```

## Audit Trail

| Agent | Decision | Justification | Time |
|-------|----------|---------------|------|

## Telemetry

| Metric | Value |
|--------|-------|
| Phases complete | 0 |
""")

    return base_dir


@pytest.mark.io
def test_export_json_valid(valid_scratchpad: Path, tmp_path: Path) -> None:
    """Export to JSON produces valid JSON."""
    output = tmp_path / "export.json"

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/export_scratchpad.py",
            str(valid_scratchpad),
            "--format",
            "json",
            "-o",
            str(output),
        ],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0, f"Export failed: {result.stderr}"
    assert output.exists(), "Output file not created"

    # Parse JSON
    data = json.loads(output.read_text())

    # Validate structure
    assert "metadata" in data
    assert "session_state" in data
    assert "audit_trail" in data
    assert "telemetry" in data
    assert "phases" in data

    # Validate metadata
    assert data["metadata"]["branch"] == "feat-test-branch"
    assert data["metadata"]["date"] == "2026-04-13"
    assert "exported_at" in data["metadata"]

    # Validate session state
    assert data["session_state"]["branch"] == "feat-test-branch"
    assert data["session_state"]["date"] == "2026-04-13"
    assert data["session_state"]["active_phase"] == "Phase 2"
    assert data["session_state"]["active_issues"] == [123, 456]

    # Validate audit trail
    assert len(data["audit_trail"]) == 2
    assert data["audit_trail"][0]["agent"] == "Executive Orchestrator"
    assert data["audit_trail"][1]["agent"] == "Review"

    # Validate telemetry
    assert data["telemetry"]["Phases complete"] == "1"
    assert data["telemetry"]["Estimated tokens used"] == "15000"

    # Validate phases
    assert len(data["phases"]) == 2
    assert data["phases"][0]["phase_num"] == 1
    assert data["phases"][0]["title"] == "Phase 1 Output"
    assert "Research Scout" in data["phases"][0]["content"]
    assert data["phases"][1]["phase_num"] == 2


@pytest.mark.io
def test_export_yaml_valid(valid_scratchpad: Path, tmp_path: Path) -> None:
    """Export to YAML produces valid YAML."""
    output = tmp_path / "export.yml"

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/export_scratchpad.py",
            str(valid_scratchpad),
            "--format",
            "yaml",
            "-o",
            str(output),
        ],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0, f"Export failed: {result.stderr}"
    assert output.exists(), "Output file not created"

    # Parse YAML
    data = yaml.safe_load(output.read_text())

    # Validate structure (same as JSON)
    assert "metadata" in data
    assert "session_state" in data
    assert "audit_trail" in data
    assert "telemetry" in data
    assert "phases" in data


@pytest.mark.io
def test_export_markdown_passthrough(valid_scratchpad: Path, tmp_path: Path) -> None:
    """Export to Markdown is a clean pass-through copy."""
    output = tmp_path / "export.md"

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/export_scratchpad.py",
            str(valid_scratchpad),
            "--format",
            "markdown",
            "-o",
            str(output),
        ],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0, f"Export failed: {result.stderr}"
    assert output.exists(), "Output file not created"

    # Content should be identical
    original_content = valid_scratchpad.read_text()
    exported_content = output.read_text()
    assert exported_content == original_content


@pytest.mark.io
def test_round_trip_json_structure_preserved(valid_scratchpad: Path, tmp_path: Path) -> None:
    """Round-trip: export JSON → parse → structure preserved."""
    output = tmp_path / "export.json"

    # Export
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/export_scratchpad.py",
            str(valid_scratchpad),
            "--format",
            "json",
            "-o",
            str(output),
        ],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0

    # Parse and validate structure
    data = json.loads(output.read_text())

    # Critical structure checks (round-trip guarantee)
    assert data["metadata"]["branch"] == "feat-test-branch"
    assert data["session_state"]["active_phase"] == "Phase 2"
    assert len(data["audit_trail"]) == 2
    assert len(data["phases"]) == 2
    assert "Phases complete" in data["telemetry"]


@pytest.mark.io
def test_export_all_mode(scratchpad_with_multiple_files: Path, tmp_path: Path, monkeypatch) -> None:
    """--all mode exports multiple files."""
    # Run from repo root, script resolves .tmp/ paths from CWD
    repo_root = Path(__file__).parent.parent

    # Change to tmp directory so --all finds the .tmp/*/*.md files
    monkeypatch.chdir(tmp_path)

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            str(repo_root / "scripts" / "export_scratchpad.py"),
            "--all",
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    # Smoke test: --all mode runs without error
    assert result.returncode == 0, f"Export failed: {result.stderr}"


@pytest.mark.io
def test_export_invalid_file_fails(tmp_path: Path) -> None:
    """Invalid scratchpad fails gracefully."""
    # Create invalid scratchpad (missing required sections)
    invalid = tmp_path / ".tmp" / "feat-invalid" / "2026-04-13.md"
    invalid.parent.mkdir(parents=True, exist_ok=True)
    invalid.write_text("""# Session — feat-invalid / 2026-04-13

## Session State

```yaml
branch: feat-invalid
date: '2026-04-13'
```

## Audit Trail

| Agent | Decision | Justification | Time |
|-------|----------|---------------|------|
""")

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/export_scratchpad.py",
            str(invalid),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    # Should fail validation
    assert result.returncode == 1
    assert "validation failed" in result.stderr


@pytest.mark.io
def test_export_stdout_default(valid_scratchpad: Path) -> None:
    """Export to stdout by default (no -o flag)."""
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/export_scratchpad.py",
            str(valid_scratchpad),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 0

    # Validate stdout contains valid JSON
    data = json.loads(result.stdout)
    assert "metadata" in data
    assert "session_state" in data


@pytest.mark.io
def test_export_file_not_found(tmp_path: Path) -> None:
    """Export fails gracefully for non-existent file."""
    nonexistent = tmp_path / "nonexistent.md"

    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/export_scratchpad.py",
            str(nonexistent),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    assert result.returncode == 2
    assert "File not found" in result.stderr
