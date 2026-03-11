"""tests/test_validate_fsm_validators.py

Tests for FSM validators:
- scripts/validate_delegation_routing.py
- scripts/validate_session_state.py
- scripts/pre_review_sweep.py
"""

from __future__ import annotations

from pathlib import Path

from scripts.pre_review_sweep import scan_file
from scripts.validate_delegation_routing import validate as validate_delegation
from scripts.validate_session_state import validate as validate_session_state


class TestValidateDelegationRouting:
    """Test delegation routing validator."""

    def test_valid_delegation_file(self, tmp_path: Path) -> None:
        """Test a valid delegation-gate.yml file."""
        gate_file = tmp_path / "delegation-gate.yml"
        gate_file.write_text(
            """---
delegation_routes:
  Orchestrator:
    - Docs
    - Scripter
  Docs: []
  Scripter: []

governance_boundaries:
  orchestrator_only:
    - git push
"""
        )

        passed, messages = validate_delegation(gate_file)
        assert passed is True, f"Expected pass but got messages: {messages}"

    def test_missing_delegation_routes_key(self, tmp_path: Path) -> None:
        """Test detection of missing delegation_routes key."""
        gate_file = tmp_path / "delegation-gate.yml"
        gate_file.write_text(
            """---
governance_boundaries:
  test: value
"""
        )

        passed, messages = validate_delegation(gate_file)
        assert passed is False
        assert any("delegation_routes" in str(m) for m in messages)

    def test_missing_governance_boundaries_key(self, tmp_path: Path) -> None:
        """Test detection of missing governance_boundaries key."""
        gate_file = tmp_path / "delegation-gate.yml"
        gate_file.write_text(
            """---
delegation_routes:
  Orchestrator: []
"""
        )

        passed, messages = validate_delegation(gate_file)
        assert passed is False
        assert any("governance_boundaries" in str(m) for m in messages)

    def test_sovereignty_violation(self, tmp_path: Path) -> None:
        """Test detection of circular delegation (sovereignty violation)."""
        gate_file = tmp_path / "delegation-gate.yml"
        gate_file.write_text(
            """---
delegation_routes:
  Orchestrator:
    - Docs
  Docs:
    - Orchestrator

governance_boundaries: {}
"""
        )

        passed, messages = validate_delegation(gate_file)
        assert passed is False
        assert any("circular" in str(m).lower() or "cycle" in str(m).lower() for m in messages)

    def test_unknown_agent_reference(self, tmp_path: Path) -> None:
        """Test detection of unknown agent references."""
        gate_file = tmp_path / "delegation-gate.yml"
        gate_file.write_text(
            """---
delegation_routes:
  Orchestrator:
    - UnknownAgent

governance_boundaries: {}
"""
        )

        passed, messages = validate_delegation(gate_file)
        assert passed is False
        assert any("unknown" in str(m).lower() for m in messages)

    def test_invalid_yaml(self, tmp_path: Path) -> None:
        """Test handling of invalid YAML syntax."""
        gate_file = tmp_path / "delegation-gate.yml"
        gate_file.write_text(
            """---
invalid: yaml: syntax:
  - bad structure
"""
        )

        passed, messages = validate_delegation(gate_file)
        assert passed is False
        assert any("yaml" in str(m).lower() for m in messages)

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test handling of missing file."""
        missing_file = tmp_path / "nonexistent.yml"
        passed, messages = validate_delegation(missing_file)
        assert passed is False
        assert any("not found" in str(m).lower() for m in messages)


class TestValidateSessionState:
    """Test session state FSM validator."""

    def test_valid_session_with_phases(self, tmp_path: Path) -> None:
        """Test a valid session with properly sequenced phases."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

Test.

---

## Orchestration Plan

### Phase 1 — Documentation

---

### Phase 1 Review

---

### Phase 2 — Scripts

---

### Phase 2 Review

---

## Session Summary

Done.
"""
        )

        passed, messages = validate_session_state(session_file)
        assert passed is True, f"Expected pass but got messages: {messages}"

    def test_missing_phases(self, tmp_path: Path) -> None:
        """Test detection when no phases are found."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

No phases here.

## Session Summary
"""
        )

        passed, messages = validate_session_state(session_file)
        assert passed is False
        assert any("no phases" in str(m).lower() for m in messages)

    def test_phase_skipping(self, tmp_path: Path) -> None:
        """Test detection of skipped phases (1→3, missing 2)."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

### Phase 1

Content.

### Phase 3

Content (skipped Phase 2).
"""
        )

        passed, messages = validate_session_state(session_file)
        assert passed is False
        assert any(
            "sequence" in str(m).lower()
            or "skipped" in str(m).lower()
            or "missing" in str(m).lower()
            for m in messages
        )

    def test_phase_does_not_start_at_1(self, tmp_path: Path) -> None:
        """Test detection when phases don't start at Phase 1."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

### Phase 2

Content without Phase 1.
"""
        )

        passed, messages = validate_session_state(session_file)
        assert passed is False
        assert any("phase 1" in str(m).lower() for m in messages)

    def test_missing_review_gate(self, tmp_path: Path) -> None:
        """Test detection of missing review gate marker after a phase."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

### Phase 1 — Documentation

Content.

### Phase 2 — Scripts

Next phase without Phase 1 Review gate marker.
"""
        )

        passed, messages = validate_session_state(session_file)
        # Should detect missing Review gate for Phase 1
        assert not passed  # Expect failure
        assert any("review" in str(m).lower() for m in messages)

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test handling of missing file."""
        missing_file = tmp_path / "nonexistent.md"
        passed, messages = validate_session_state(missing_file)
        assert passed is False
        assert any("not found" in str(m).lower() for m in messages)


class TestPreReviewSweep:
    """Test pre-review sweep pattern scanning."""

    def test_heredoc_detection(self, tmp_path: Path) -> None:
        """Test detection of heredoc pattern."""
        script_file = tmp_path / "test.sh"
        script_file.write_text("cat >> file << 'EOF'\nContent\nEOF")

        findings = scan_file(script_file)
        assert len(findings) > 0
        assert any("heredoc" in name for name, _, _ in findings)

    def test_heredoc_in_negation_ignored(self, tmp_path: Path) -> None:
        """Test that heredoc in negation context is ignored."""
        script_file = tmp_path / "test.sh"
        script_file.write_text("# Never use: cat >> file << 'EOF'")

        findings = scan_file(script_file)
        assert len(findings) == 0

    def test_fetch_before_check_detection(self, tmp_path: Path) -> None:
        """Test detection of fetch-before-check pattern."""
        doc_file = tmp_path / "test.md"
        doc_file.write_text("Fetch-before-check is wrong; use check-before-fetch.")

        findings = scan_file(doc_file)
        assert len(findings) > 0
        assert any("fetch-before-check" in name for name, _, _ in findings)

    def test_terminal_redirection_detection(self, tmp_path: Path) -> None:
        """Test detection of terminal redirection patterns."""
        bash_file = tmp_path / "test.sh"
        bash_file.write_text("echo hello > output.txt")

        findings = scan_file(bash_file)
        assert len(findings) > 0
        assert any("terminal" in name or "redirection" in name for name, _, _ in findings)

    def test_no_patterns_found(self, tmp_path: Path) -> None:
        """Test file with no bad patterns."""
        clean_file = tmp_path / "clean.py"
        clean_file.write_text("print('Hello')\n")

        findings = scan_file(clean_file)
        assert len(findings) == 0

    def test_line_numbers_accurate(self, tmp_path: Path) -> None:
        """Test that reported line numbers are correct."""
        bash_file = tmp_path / "test.sh"
        bash_file.write_text("#!/bin/bash\necho start\necho test > output.txt\necho end\n")

        findings = scan_file(bash_file)
        assert len(findings) > 0
        # Pattern should be on line 3
        assert any(line_num == 3 for _, line_num, _ in findings)

    def test_extension_filtering(self, tmp_path: Path) -> None:
        """Test that patterns are only checked for appropriate file types."""
        # .txt file with heredoc - should not be checked
        txt_file = tmp_path / "text.txt"
        txt_file.write_text("cat >> file << 'EOF'")

        findings = scan_file(txt_file)
        assert len(findings) == 0  # .txt is not in extensions list

    def test_unreadable_file_ignored(self, tmp_path: Path) -> None:
        """Test that unreadable files are gracefully ignored."""
        script_file = tmp_path / "test.py"
        script_file.write_text("valid content")

        # Make file unreadable (on systems that support chmod)
        try:
            import os
            os.chmod(script_file, 0o000)

            findings = scan_file(script_file)
            assert len(findings) == 0  # Should not crash, just return empty
        finally:
            # Restore permissions for cleanup
            try:
                import os
                os.chmod(script_file, 0o644)
            except Exception:
                pass
