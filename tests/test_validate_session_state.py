"""tests/test_validate_session_state.py

Tests for the YAML phase-status block parsing in scripts/validate_session_state.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_session_state import (
    display_phase_table,
    extract_yaml_state_block,
    main,
    parse_yaml_block,
    validate_yaml_state,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_YAML_SCRATCHPAD = """\
# Session — feat-test / 2026-03-16

_Created by prune_scratchpad.py._

## Session State

```yaml
branch: feat/sprint-14-substrate-tooling
active_phase: Phase 1
phases:
  - name: Phase 0 — Planning
    status: complete
    commit: 67c8ab2
  - name: Phase 1 — Scripting
    status: in-progress
    commit: ""
```

## Some Other Section

Content here.
"""

MISSING_BLOCK_SCRATCHPAD = """\
# Session — feat-test / 2026-03-16

## Some Section

No session state block here at all.
"""

MALFORMED_YAML_SCRATCHPAD = """\
# Session

## Session State

```yaml
: broken: yaml: {{phases: not a list
```

## End
"""

EMPTY_PHASES_SCRATCHPAD = """\
# Session

## Session State

```yaml
branch: feat/my-branch
active_phase: null
phases: []
```
"""


# ---------------------------------------------------------------------------
# extract_yaml_state_block
# ---------------------------------------------------------------------------


class TestExtractYamlStateBlock:
    def test_finds_block(self):
        result = extract_yaml_state_block(VALID_YAML_SCRATCHPAD)
        assert result is not None
        assert "branch: feat/sprint-14-substrate-tooling" in result

    def test_returns_none_when_missing(self):
        result = extract_yaml_state_block(MISSING_BLOCK_SCRATCHPAD)
        assert result is None

    def test_returns_none_on_empty_string(self):
        result = extract_yaml_state_block("")
        assert result is None

    def test_extracts_phases_content(self):
        result = extract_yaml_state_block(VALID_YAML_SCRATCHPAD)
        assert result is not None
        assert "Phase 0" in result
        assert "complete" in result


# ---------------------------------------------------------------------------
# parse_yaml_block
# ---------------------------------------------------------------------------


class TestParseYamlBlock:
    def test_valid_yaml_returns_dict(self):
        yaml_text = "branch: feat/test\nactive_phase: null\nphases: []\n"
        data, err = parse_yaml_block(yaml_text)
        assert err is None
        assert data is not None
        assert data["branch"] == "feat/test"
        assert data["phases"] == []

    def test_valid_yaml_with_phases(self):
        yaml_text = (
            "branch: feat/test\nactive_phase: Phase 1\n"
            "phases:\n  - name: Phase 0\n    status: complete\n    commit: abc1234\n"
        )
        data, err = parse_yaml_block(yaml_text)
        assert err is None
        assert len(data["phases"]) == 1
        assert data["phases"][0]["name"] == "Phase 0"

    def test_missing_branch_key_is_error(self):
        yaml_text = "active_phase: null\nphases: []\n"
        _, err = parse_yaml_block(yaml_text)
        assert err is not None
        assert "branch" in err

    def test_missing_active_phase_key_is_error(self):
        yaml_text = "branch: test\nphases: []\n"
        _, err = parse_yaml_block(yaml_text)
        assert err is not None
        assert "active_phase" in err

    def test_phases_non_list_is_error(self):
        yaml_text = "branch: test\nactive_phase: null\nphases: not-a-list\n"
        _, err = parse_yaml_block(yaml_text)
        assert err is not None

    def test_malformed_yaml_returns_error(self):
        yaml_text = "branch: [broken: {yaml\n"
        _, err = parse_yaml_block(yaml_text)
        assert err is not None

    def test_branch_null_is_error(self):
        """branch: (YAML null) must be rejected — detached HEAD edge case."""
        yaml_text = "branch: \nactive_phase: null\nphases: []\n"
        _, err = parse_yaml_block(yaml_text)
        assert err is not None
        assert "branch" in err.lower()

    def test_non_dict_phase_entry_is_error(self):
        """Phase entries that are not dicts (e.g. bare strings) must be rejected."""
        yaml_text = "branch: feat/test\nactive_phase: null\nphases:\n  - not-a-dict\n"
        _, err = parse_yaml_block(yaml_text)
        assert err is not None

    def test_phase_missing_name_is_error(self):
        """Phase dicts without a 'name' field must be rejected."""
        yaml_text = "branch: feat/test\nactive_phase: null\nphases:\n  - status: complete\n"
        _, err = parse_yaml_block(yaml_text)
        assert err is not None
        assert "name" in err


# ---------------------------------------------------------------------------
# display_phase_table
# ---------------------------------------------------------------------------


class TestDisplayPhaseTable:
    def test_renders_branch_and_phases(self, capsys):
        data = {
            "branch": "feat/test",
            "active_phase": "Phase 1",
            "phases": [
                {"name": "Phase 0 — Planning", "status": "complete", "commit": "abc1234"},
                {"name": "Phase 1 — Scripting", "status": "in-progress", "commit": ""},
            ],
        }
        display_phase_table(data)
        cap = capsys.readouterr()
        assert "feat/test" in cap.out
        assert "Phase 0 — Planning" in cap.out
        assert "complete" in cap.out
        assert "in-progress" in cap.out

    def test_empty_phases_prints_none(self, capsys):
        data = {"branch": "feat/test", "active_phase": None, "phases": []}
        display_phase_table(data)
        cap = capsys.readouterr()
        assert "(none)" in cap.out

    def test_null_active_phase_shown(self, capsys):
        data = {"branch": "feat/test", "active_phase": None, "phases": []}
        display_phase_table(data)
        cap = capsys.readouterr()
        assert "(none)" in cap.out


# ---------------------------------------------------------------------------
# validate_yaml_state
# ---------------------------------------------------------------------------


class TestValidateYamlState:
    @pytest.mark.io
    def test_valid_file_returns_true(self, tmp_path):
        f = tmp_path / "session.md"
        f.write_text(VALID_YAML_SCRATCHPAD)
        success, _ = validate_yaml_state(f)
        assert success is True

    @pytest.mark.io
    def test_missing_block_returns_false(self, tmp_path):
        f = tmp_path / "session.md"
        f.write_text(MISSING_BLOCK_SCRATCHPAD)
        success, msg = validate_yaml_state(f)
        assert success is False
        assert "not found" in msg.lower()

    @pytest.mark.io
    def test_file_not_found_returns_false(self, tmp_path):
        success, msg = validate_yaml_state(tmp_path / "nonexistent.md")
        assert success is False
        assert "not found" in msg.lower()


# ---------------------------------------------------------------------------
# main (CLI)
# ---------------------------------------------------------------------------


class TestMain:
    @pytest.mark.io
    def test_yaml_state_happy_path_exit_0(self, tmp_path):
        f = tmp_path / "session.md"
        f.write_text(VALID_YAML_SCRATCHPAD)
        rc = main(["--yaml-state", str(f)])
        assert rc == 0

    @pytest.mark.io
    def test_yaml_state_missing_block_exit_1(self, tmp_path):
        f = tmp_path / "session.md"
        f.write_text(MISSING_BLOCK_SCRATCHPAD)
        rc = main(["--yaml-state", str(f)])
        assert rc == 1

    @pytest.mark.io
    def test_yaml_state_empty_phases_exit_0(self, tmp_path):
        f = tmp_path / "session.md"
        f.write_text(EMPTY_PHASES_SCRATCHPAD)
        rc = main(["--yaml-state", str(f)])
        assert rc == 0

    @pytest.mark.io
    def test_yaml_state_file_not_found_exit_1(self, tmp_path):
        rc = main(["--yaml-state", str(tmp_path / "nonexistent.md")])
        assert rc == 1

    def test_no_files_exits_1(self, capsys):
        rc = main([])
        assert rc == 1


# ---------------------------------------------------------------------------
# Candidate C — extended schema tests
# ---------------------------------------------------------------------------

CANDIDATE_C_SCRATCHPAD = """\
# Session — feat-candidate-c / 2026-03-17

_Created by prune_scratchpad.py._

## Session State

```yaml
branch: feat/sprint-16-candidate-c
date: '2026-03-17'
active_phase: Phase 2
active_issues:
  - 307
  - 308
blockers:
  - Waiting for Review gate APPROVED
last_agent: Executive Orchestrator
phases:
  - name: Phase 1 — Governance
    status: complete
    commit: abc1234
  - name: Phase 2 — Claude Code
    status: in-progress
    commit: ''
```

## Session Start

Some content here.
"""

LEGACY_SCHEMA_SCRATCHPAD = """\
# Session — feat-legacy / 2026-03-01

## Session State

```yaml
branch: feat/legacy-branch
active_phase: null
phases: []
```
"""


class TestCandidateCSchema:
    """Tests for Candidate C extended YAML schema fields."""

    def test_extended_schema_parses_without_error(self):
        """Extended schema with all Candidate C fields passes parse_yaml_block."""
        yaml_content = """\
branch: feat/sprint-16-candidate-c
date: '2026-03-17'
active_phase: Phase 2
active_issues:
  - 307
  - 308
blockers:
  - Waiting for review
last_agent: Executive Orchestrator
phases:
  - name: Phase 1
    status: complete
    commit: abc1234
"""
        data, error = parse_yaml_block(yaml_content)
        assert error is None
        assert data is not None
        assert data["date"] == "2026-03-17"
        assert data["active_issues"] == [307, 308]
        assert data["blockers"] == ["Waiting for review"]
        assert data["last_agent"] == "Executive Orchestrator"

    def test_legacy_schema_backward_compat(self):
        """Old schema (branch + active_phase + phases only) still passes validation."""
        yaml_content = "branch: feat/legacy\nactive_phase: null\nphases: []\n"
        data, error = parse_yaml_block(yaml_content)
        assert error is None
        assert data is not None
        assert "date" not in data or data.get("date") is None

    def test_active_issues_non_list_is_error(self):
        """'active_issues' must be a list."""
        yaml_content = "branch: b\nactive_phase: null\nphases: []\nactive_issues: 307\n"
        _, error = parse_yaml_block(yaml_content)
        assert error is not None
        assert "active_issues" in error

    def test_blockers_non_list_is_error(self):
        """'blockers' must be a list."""
        yaml_content = "branch: b\nactive_phase: null\nphases: []\nblockers: some string\n"
        _, error = parse_yaml_block(yaml_content)
        assert error is not None
        assert "blockers" in error

    def test_last_agent_non_string_non_null_is_error(self):
        """'last_agent' must be a string or null."""
        yaml_content = "branch: b\nactive_phase: null\nphases: []\nlast_agent: 42\n"
        _, error = parse_yaml_block(yaml_content)
        assert error is not None
        assert "last_agent" in error

    def test_date_non_string_is_error(self):
        """'date' must be a string or null."""
        yaml_content = "branch: b\nactive_phase: null\nphases: []\ndate: 20260317\n"
        # YAML parses '20260317' as int if unquoted
        _, error = parse_yaml_block(yaml_content)
        assert error is not None
        assert "date" in error

    def test_display_shows_date_and_optional_fields(self, capsys):
        """display_phase_table renders date, last_agent, active_issues, blockers."""
        data = {
            "branch": "feat/candidate-c",
            "date": "2026-03-17",
            "active_phase": "Phase 2",
            "active_issues": [307, 308],
            "blockers": ["Review not yet APPROVED"],
            "last_agent": "Executive Orchestrator",
            "phases": [],
        }
        display_phase_table(data)
        out = capsys.readouterr().out
        assert "2026-03-17" in out
        assert "Executive Orchestrator" in out
        assert "307" in out
        assert "Review not yet APPROVED" in out

    def test_display_omits_empty_optional_fields(self, capsys):
        """display_phase_table omits date/last_agent/active_issues/blockers when empty."""
        data = {
            "branch": "feat/candidate-c",
            "active_phase": None,
            "phases": [],
        }
        display_phase_table(data)
        out = capsys.readouterr().out
        assert "Active issues" not in out
        assert "Blockers" not in out
        assert "Last agent" not in out

    @pytest.mark.io
    def test_full_candidate_c_scratchpad_passes_yaml_state(self, tmp_path):
        """A real scratchpad file with Candidate C extended schema passes --yaml-state."""
        f = tmp_path / "session.md"
        f.write_text(CANDIDATE_C_SCRATCHPAD)
        rc = main(["--yaml-state", str(f)])
        assert rc == 0

    @pytest.mark.io
    def test_legacy_scratchpad_still_passes_yaml_state(self, tmp_path):
        """A scratchpad file with old 3-field schema (no Candidate C fields) passes --yaml-state."""
        f = tmp_path / "session.md"
        f.write_text(LEGACY_SCHEMA_SCRATCHPAD)
        rc = main(["--yaml-state", str(f)])
        assert rc == 0
