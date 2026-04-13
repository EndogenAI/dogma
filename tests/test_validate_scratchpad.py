"""tests/test_validate_scratchpad.py

Test suite for scripts/validate_scratchpad.py — validates scratchpad schema enforcement.

Covers:
    - Valid scratchpad passes all checks
    - Missing required sections fail
    - Invalid YAML in Session State fails
    - Date mismatch (filename vs. Session State) fails
    - Skipped heading levels fail
    - Skipped phase numbers fail
    - Exit codes (0 on pass, 1 on fail)
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def valid_scratchpad(tmp_path: Path) -> Path:
    """Create a minimal valid scratchpad file."""
    branch_dir = tmp_path / "feat-test-branch"
    branch_dir.mkdir(parents=True, exist_ok=True)

    scratchpad = branch_dir / "2026-04-13.md"
    scratchpad.write_text("""# Session — feat-test-branch / 2026-04-13

## Session State

```yaml
branch: feat-test-branch
date: '2026-04-13'
active_phase: "Phase 1"
active_issues: [123]
blockers: []
last_agent: "Executive Orchestrator"
phases:
  - name: "Phase 1"
    status: "In Progress"
```

## Audit Trail

| Agent | Decision | Justification | Time |
|-------|----------|---------------|------|
| Executive Orchestrator | Start Phase 1 | Workplan approved | 10:00 |

## Telemetry

| Metric | Value |
|--------|-------|
| Phases complete | 0 |
| Delegations made | 0 |
""")

    return scratchpad


@pytest.fixture
def scratchpad_missing_section(tmp_path: Path) -> Path:
    """Scratchpad missing required section (Telemetry)."""
    branch_dir = tmp_path / "feat-test-branch"
    branch_dir.mkdir(parents=True, exist_ok=True)

    scratchpad = branch_dir / "2026-04-13.md"
    scratchpad.write_text("""# Session — feat-test-branch / 2026-04-13

## Session State

```yaml
branch: feat-test-branch
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
""")

    return scratchpad


@pytest.fixture
def scratchpad_invalid_yaml(tmp_path: Path) -> Path:
    """Scratchpad with invalid YAML in Session State."""
    branch_dir = tmp_path / "feat-test-branch"
    branch_dir.mkdir(parents=True, exist_ok=True)

    scratchpad = branch_dir / "2026-04-13.md"
    scratchpad.write_text("""# Session — feat-test-branch / 2026-04-13

## Session State

```yaml
branch: feat-test-branch
date: '2026-04-13'
active_phase: [unclosed bracket
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

    return scratchpad


@pytest.fixture
def scratchpad_date_mismatch(tmp_path: Path) -> Path:
    """Scratchpad with filename date != Session State date."""
    branch_dir = tmp_path / "feat-test-branch"
    branch_dir.mkdir(parents=True, exist_ok=True)

    scratchpad = branch_dir / "2026-04-13.md"
    scratchpad.write_text("""# Session — feat-test-branch / 2026-04-13

## Session State

```yaml
branch: feat-test-branch
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

    return scratchpad


@pytest.fixture
def scratchpad_skip_heading(tmp_path: Path) -> Path:
    """Scratchpad with heading hierarchy violation (H1 → H3)."""
    branch_dir = tmp_path / "feat-test-branch"
    branch_dir.mkdir(parents=True, exist_ok=True)

    scratchpad = branch_dir / "2026-04-13.md"
    scratchpad.write_text("""# Session — feat-test-branch / 2026-04-13

## Session State

```yaml
branch: feat-test-branch
date: '2026-04-13'
active_phase: null
active_issues: []
blockers: []
last_agent: null
phases: []
```

#### Skipped to H4

## Audit Trail

| Agent | Decision | Justification | Time |
|-------|----------|---------------|------|

## Telemetry

| Metric | Value |
|--------|-------|
| Phases complete | 0 |
""")

    return scratchpad


@pytest.fixture
def scratchpad_phase_gap(tmp_path: Path) -> Path:
    """Scratchpad with non-consecutive phase numbers (Phase 1, Phase 3)."""
    branch_dir = tmp_path / "feat-test-branch"
    branch_dir.mkdir(parents=True, exist_ok=True)

    scratchpad = branch_dir / "2026-04-13.md"
    scratchpad.write_text("""# Session — feat-test-branch / 2026-04-13

## Session State

```yaml
branch: feat-test-branch
date: '2026-04-13'
active_phase: "Phase 3"
active_issues: [123]
blockers: []
last_agent: "Executive Orchestrator"
phases:
  - name: "Phase 1"
    status: "Complete"
  - name: "Phase 3"
    status: "In Progress"
```

## Phase 1 Output

Completed Phase 1.

## Phase 3 Output

Skipped Phase 2.

## Audit Trail

| Agent | Decision | Justification | Time |
|-------|----------|---------------|------|

## Telemetry

| Metric | Value |
|--------|-------|
| Phases complete | 1 |
""")

    return scratchpad


@pytest.fixture
def scratchpad_missing_yaml_field(tmp_path: Path) -> Path:
    """Scratchpad with Session State missing required field (active_issues)."""
    branch_dir = tmp_path / "feat-test-branch"
    branch_dir.mkdir(parents=True, exist_ok=True)

    scratchpad = branch_dir / "2026-04-13.md"
    scratchpad.write_text("""# Session — feat-test-branch / 2026-04-13

## Session State

```yaml
branch: feat-test-branch
date: '2026-04-13'
active_phase: null
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

    return scratchpad


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_valid_scratchpad_passes(valid_scratchpad: Path) -> None:
    """Valid scratchpad passes all checks."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(valid_scratchpad)], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "PASS" in result.stdout


@pytest.mark.io
def test_missing_section_fails(scratchpad_missing_section: Path) -> None:
    """Scratchpad missing required section fails."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_missing_section)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "Telemetry" in result.stdout


@pytest.mark.io
def test_invalid_yaml_fails(scratchpad_invalid_yaml: Path) -> None:
    """Scratchpad with invalid YAML fails."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_invalid_yaml)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "YAML" in result.stdout or "parse" in result.stdout.lower()


@pytest.mark.io
def test_date_mismatch_fails(scratchpad_date_mismatch: Path) -> None:
    """Scratchpad with date mismatch fails."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_date_mismatch)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "date" in result.stdout.lower()


@pytest.mark.io
def test_heading_skip_fails(scratchpad_skip_heading: Path) -> None:
    """Scratchpad with skipped heading level fails."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_skip_heading)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "hierarchy" in result.stdout.lower() or "skipped" in result.stdout.lower()


@pytest.mark.io
def test_phase_gap_fails(scratchpad_phase_gap: Path) -> None:
    """Scratchpad with non-consecutive phase numbers fails."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_phase_gap)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "Phase" in result.stdout and ("gap" in result.stdout.lower() or "expected" in result.stdout.lower())


@pytest.mark.io
def test_missing_yaml_field_fails(scratchpad_missing_yaml_field: Path) -> None:
    """Scratchpad with missing required YAML field fails."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_missing_yaml_field)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "active_issues" in result.stdout


@pytest.mark.io
def test_check_only_mode(valid_scratchpad: Path) -> None:
    """--check-only mode returns exit code only (no output) on valid file."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(valid_scratchpad), "--check-only"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Should have minimal or no output in check-only mode


@pytest.mark.io
def test_all_mode(tmp_path: Path) -> None:
    """--all mode validates all scratchpad files."""
    # Create .tmp/ directory structure that --all mode expects
    tmp_dir = tmp_path / ".tmp"
    branch1 = tmp_dir / "feat-branch1"
    branch1.mkdir(parents=True, exist_ok=True)
    (branch1 / "2026-04-13.md").write_text("""# Session — feat-branch1 / 2026-04-13

## Session State

```yaml
branch: feat-branch1
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

    # Run from tmp_path so script finds .tmp/ subdirectory
    # Use absolute path to script since we're not in repo root
    repo_root = Path(__file__).parent.parent
    script_path = repo_root / "scripts" / "validate_scratchpad.py"

    result = subprocess.run(
        ["uv", "run", "python", str(script_path), "--all"], capture_output=True, text=True, cwd=tmp_path
    )

    # Should find and validate the file
    assert result.returncode == 0
    assert "feat-branch1" in result.stdout or "1 passed" in result.stdout
