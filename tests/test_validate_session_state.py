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
