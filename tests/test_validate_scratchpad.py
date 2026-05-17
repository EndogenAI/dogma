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

# Import business logic functions for unit tests
from scripts.validate_scratchpad import (
    check_table_present,
    extract_session_state_yaml,
    find_section_bounds,
    main,
    validate_heading_hierarchy,
    validate_phase_numbering,
    validate_scratchpad,
    validate_telemetry_table,
)


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
# Unit Tests — Business Logic
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_find_section_bounds_finds_section(tmp_path):
    """Test that find_section_bounds correctly locates section boundaries."""
    content = """# Title

## Session State

Some content here.

## Audit Trail

More content.
"""
    bounds = find_section_bounds(content, "Session State")
    assert bounds is not None
    start, end = bounds
    assert "## Session State" in content[start:end]
    assert "## Audit Trail" not in content[start:end]


@pytest.mark.io
def test_find_section_bounds_returns_none_for_missing():
    """Test that find_section_bounds returns None for missing sections."""
    content = """# Title

## Session State

Some content.
"""
    assert find_section_bounds(content, "Missing Section") is None


@pytest.mark.io
def test_extract_session_state_yaml_valid():
    """Test that extract_session_state_yaml parses valid YAML."""
    content = """## Session State

```yaml
branch: feat-test
date: '2026-04-13'
active_phase: null
```
"""
    bounds = find_section_bounds(content, "Session State")
    assert bounds is not None
    data = extract_session_state_yaml(content, bounds[0], bounds[1])

    assert data is not None
    assert data["branch"] == "feat-test"
    assert data["date"] == "2026-04-13"


@pytest.mark.io
def test_extract_session_state_yaml_invalid():
    """Test that extract_session_state_yaml returns None for invalid YAML."""
    content = """## Session State

```yaml
branch: feat-test
date: [unclosed
```
"""
    bounds = find_section_bounds(content, "Session State")
    assert bounds is not None
    data = extract_session_state_yaml(content, bounds[0], bounds[1])

    assert data is None


@pytest.mark.io
def test_check_table_present_finds_table():
    """Test that check_table_present detects markdown tables."""
    content = """## Audit Trail

| Agent | Decision |
|-------|----------|
| Orchestrator | Start |
"""
    assert check_table_present(content, "Audit Trail") is True


@pytest.mark.io
def test_check_table_present_returns_false_for_no_table():
    """Test that check_table_present returns False when no table found."""
    content = """## Audit Trail

Just some text, no table.
"""
    assert check_table_present(content, "Audit Trail") is False


@pytest.mark.io
def test_validate_heading_hierarchy_valid():
    """Test that validate_heading_hierarchy accepts valid hierarchy."""
    content = """# Title

## Section 1

### Subsection 1.1

## Section 2
"""
    errors = validate_heading_hierarchy(content)
    assert len(errors) == 0


@pytest.mark.io
def test_validate_heading_hierarchy_detects_skip():
    """Test that validate_heading_hierarchy detects skipped levels."""
    content = """# Title

## Section 1

#### Skipped to H4
"""
    errors = validate_heading_hierarchy(content)
    assert len(errors) > 0
    assert "skipped" in errors[0].lower() or "violation" in errors[0].lower()


@pytest.mark.io
def test_validate_phase_numbering_consecutive():
    """Test that validate_phase_numbering accepts consecutive phases."""
    content = """## Phase 1 Output

Content.

## Phase 2 Output

More content.
"""
    errors = validate_phase_numbering(content)
    assert len(errors) == 0


@pytest.mark.io
def test_validate_phase_numbering_detects_gap():
    """Test that validate_phase_numbering detects gaps."""
    content = """## Phase 1 Output

Content.

## Phase 3 Output

Skipped Phase 2.
"""
    errors = validate_phase_numbering(content)
    assert len(errors) > 0
    assert "gap" in errors[0].lower() or "expected" in errors[0].lower()


@pytest.mark.io
def test_validate_telemetry_table_with_data():
    """Test that validate_telemetry_table accepts table with data rows."""
    content = """## Telemetry

| Metric | Value |
|--------|-------|
| Phases complete | 0 |
"""
    errors = validate_telemetry_table(content)
    assert len(errors) == 0


@pytest.mark.io
def test_validate_telemetry_table_no_data():
    """Test that validate_telemetry_table fails when table has no data rows."""
    content = """## Telemetry

| Metric | Value |
|--------|-------|
"""
    errors = validate_telemetry_table(content)
    assert len(errors) > 0
    assert "no data rows" in errors[0].lower()


@pytest.mark.io
def test_validate_scratchpad_valid(valid_scratchpad):
    """Test that validate_scratchpad accepts valid scratchpad."""
    is_valid, errors = validate_scratchpad(valid_scratchpad)

    assert is_valid is True
    assert len(errors) == 0


@pytest.mark.io
def test_validate_scratchpad_missing_section(scratchpad_missing_section):
    """Test that validate_scratchpad detects missing required section."""
    is_valid, errors = validate_scratchpad(scratchpad_missing_section)

    assert is_valid is False
    assert any("Telemetry" in err for err in errors)


@pytest.mark.io
def test_validate_scratchpad_invalid_yaml(scratchpad_invalid_yaml):
    """Test that validate_scratchpad detects invalid YAML."""
    is_valid, errors = validate_scratchpad(scratchpad_invalid_yaml)

    assert is_valid is False
    assert any("YAML" in err or "parse" in err.lower() for err in errors)


@pytest.mark.io
def test_validate_scratchpad_date_mismatch(scratchpad_date_mismatch):
    """Test that validate_scratchpad detects date mismatch."""
    is_valid, errors = validate_scratchpad(scratchpad_date_mismatch)

    assert is_valid is False
    assert any("date" in err.lower() for err in errors)


@pytest.mark.io
def test_validate_scratchpad_heading_skip(scratchpad_skip_heading):
    """Test that validate_scratchpad detects heading hierarchy violation."""
    is_valid, errors = validate_scratchpad(scratchpad_skip_heading)

    assert is_valid is False
    assert any("hierarchy" in err.lower() or "skipped" in err.lower() for err in errors)


@pytest.mark.io
def test_validate_scratchpad_phase_gap(scratchpad_phase_gap):
    """Test that validate_scratchpad detects phase numbering gap."""
    is_valid, errors = validate_scratchpad(scratchpad_phase_gap)

    assert is_valid is False
    assert any("Phase" in err and ("gap" in err.lower() or "expected" in err.lower()) for err in errors)


@pytest.mark.io
def test_validate_scratchpad_missing_yaml_field(scratchpad_missing_yaml_field):
    """Test that validate_scratchpad detects missing YAML field."""
    is_valid, errors = validate_scratchpad(scratchpad_missing_yaml_field)

    assert is_valid is False
    assert any("active_issues" in err for err in errors)


@pytest.mark.io
def test_main_function_callable():
    """Test that main() function is callable."""
    assert callable(main)


@pytest.mark.io
def test_main_with_valid_file_returns_0(valid_scratchpad):
    """Test that main() returns 0 when validating a valid file."""
    import sys

    # Mock sys.argv to pass the file path
    old_argv = sys.argv
    try:
        sys.argv = ["validate_scratchpad.py", str(valid_scratchpad)]
        exit_code = main()
        assert exit_code == 0
    finally:
        sys.argv = old_argv


@pytest.mark.io
def test_main_with_invalid_file_returns_1(scratchpad_missing_section):
    """Test that main() returns 1 when validating an invalid file."""
    import sys

    # Mock sys.argv to pass the file path
    old_argv = sys.argv
    try:
        sys.argv = ["validate_scratchpad.py", str(scratchpad_missing_section)]
        exit_code = main()
        assert exit_code == 1
    finally:
        sys.argv = old_argv


@pytest.mark.io
def test_main_with_no_args_returns_2(capsys):
    """Test that main() returns 2 when no arguments provided."""
    import sys

    # Mock sys.argv with no file argument
    old_argv = sys.argv
    try:
        sys.argv = ["validate_scratchpad.py"]
        exit_code = main()
        assert exit_code == 2
    finally:
        sys.argv = old_argv


@pytest.mark.io
def test_validate_scratchpad_nonexistent_file():
    """Test that validate_scratchpad handles non-existent files."""
    nonexistent = Path("/tmp/nonexistent-file-12345.md")
    is_valid, errors = validate_scratchpad(nonexistent)

    assert is_valid is False
    assert any("not found" in err.lower() for err in errors)


# ---------------------------------------------------------------------------
# Integration Tests — CLI (keep 1-2 subprocess tests as smoke tests)
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.io
def test_cli_valid_scratchpad_passes(valid_scratchpad: Path) -> None:
    """Integration test: Valid scratchpad passes all checks via CLI."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(valid_scratchpad)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "PASS" in result.stdout


@pytest.mark.integration
@pytest.mark.io
def test_cli_missing_section_fails(scratchpad_missing_section: Path) -> None:
    """Integration test: Scratchpad missing required section fails via CLI."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_missing_section)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "Telemetry" in result.stdout


@pytest.mark.integration
@pytest.mark.io
def test_cli_invalid_yaml_fails(scratchpad_invalid_yaml: Path) -> None:
    """Integration test: Scratchpad with invalid YAML fails via CLI."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_invalid_yaml)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "YAML" in result.stdout or "parse" in result.stdout.lower()


@pytest.mark.integration
@pytest.mark.io
def test_cli_date_mismatch_fails(scratchpad_date_mismatch: Path) -> None:
    """Integration test: Scratchpad with date mismatch fails via CLI."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_date_mismatch)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "date" in result.stdout.lower()


@pytest.mark.integration
@pytest.mark.io
def test_cli_heading_skip_fails(scratchpad_skip_heading: Path) -> None:
    """Integration test: Scratchpad with skipped heading level fails via CLI."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_skip_heading)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "hierarchy" in result.stdout.lower() or "skipped" in result.stdout.lower()


@pytest.mark.integration
@pytest.mark.io
def test_cli_phase_gap_fails(scratchpad_phase_gap: Path) -> None:
    """Integration test: Scratchpad with non-consecutive phase numbers fails via CLI."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_phase_gap)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "Phase" in result.stdout and ("gap" in result.stdout.lower() or "expected" in result.stdout.lower())


@pytest.mark.integration
@pytest.mark.io
def test_cli_missing_yaml_field_fails(scratchpad_missing_yaml_field: Path) -> None:
    """Integration test: Scratchpad with missing required YAML field fails via CLI."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(scratchpad_missing_yaml_field)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "active_issues" in result.stdout


@pytest.mark.integration
@pytest.mark.io
def test_cli_check_only_mode(valid_scratchpad: Path) -> None:
    """Integration test: --check-only mode returns exit code only (no output) on valid file."""
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_scratchpad.py", str(valid_scratchpad), "--check-only"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Should have minimal or no output in check-only mode


@pytest.mark.integration
@pytest.mark.io
def test_cli_all_mode(tmp_path: Path) -> None:
    """Integration test: --all mode validates all scratchpad files."""
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
