"""tests/test_validate_session.py

Tests for scripts/validate_session.py
"""

from __future__ import annotations

from pathlib import Path

from scripts.validate_session import check_value_fidelity, validate_session_file


class TestValidateSessionFile:
    """Test suite for validate_session_file."""

    def test_valid_complete_session(self, tmp_path: Path) -> None:
        """Test a completely valid session file."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom**: Endogenous-First — primary endogenous source: `MANIFESTO.md`.

---

## Orchestration Plan

### Phase 1 — Documentation

---

## Pre-Compact Checkpoint

All phases complete.

---

## Session Summary

Phase 1 done.
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}. Messages: {messages}"
        assert not messages or all("✓" in str(m) or "OK" in str(m) for m in messages)

    def test_missing_session_start(self, tmp_path: Path) -> None:
        """Test detection of missing ## Session Start section."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Orchestration Plan

### Phase 1

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 1
        assert any("Session Start" in str(m) for m in messages)

    def test_missing_governing_axiom(self, tmp_path: Path) -> None:
        """Test detection of missing governing axiom citation."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

Some session notes without axiom.

---

## Orchestration Plan

### Phase 1

---

## Pre-Compact Checkpoint

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 2  # Encoding drift
        assert any("Governing axiom" in str(m) for m in messages)

    def test_missing_endogenous_source(self, tmp_path: Path) -> None:
        """Test detection of missing endogenous source citation."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom**: Endogenous-First

Some session notes from external sources only.

---

## Orchestration Plan

### Phase 1

---

## Pre-Compact Checkpoint

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 2  # Encoding drift
        assert any("endogenous source" in str(m).lower() for m in messages)

    def test_missing_orchestration_plan(self, tmp_path: Path) -> None:
        """Test detection of missing ## Orchestration Plan section."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom**: Endogenous-First — primary endogenous source: `MANIFESTO.md`.

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 1
        assert any("Orchestration Plan" in str(m) for m in messages)

    def test_missing_phase_records(self, tmp_path: Path) -> None:
        """Test detection of missing phase records (### Phase N headings)."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom**: Endogenous-First — primary endogenous source: `MANIFESTO.md`.

---

## Orchestration Plan

Some planning notes without phase headings.

---

## Pre-Compact Checkpoint

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 1
        assert any("phase records" in str(m).lower() for m in messages)

    def test_missing_pre_compact_checkpoint(self, tmp_path: Path) -> None:
        """Test detection of missing ## Pre-Compact Checkpoint section."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom**: Endogenous-First — primary endogenous source: `MANIFESTO.md`.

---

## Orchestration Plan

### Phase 1

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 1
        assert any("Pre-Compact Checkpoint" in str(m) for m in messages)

    def test_context_window_checkpoint_alternative(self, tmp_path: Path) -> None:
        """Test that ## Context Window Checkpoint is accepted as alternative to Pre-Compact Checkpoint."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom**: Endogenous-First — primary endogenous source: `MANIFESTO.md`.

---

## Orchestration Plan

### Phase 1

---

## Context Window Checkpoint

Context limit approaching.

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 0

    def test_missing_session_summary(self, tmp_path: Path) -> None:
        """Test detection of missing ## Session Summary section."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom**: Endogenous-First — primary endogenous source: `MANIFESTO.md`.

---

## Orchestration Plan

### Phase 1

---

## Pre-Compact Checkpoint
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 1
        assert any("Session Summary" in str(m) for m in messages)

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test handling of non-existent file."""
        missing_file = tmp_path / "nonexistent.md"

        exit_code, messages = validate_session_file(missing_file)
        assert exit_code == 1
        assert any("not found" in str(m).lower() for m in messages)

    def test_multiple_phases(self, tmp_path: Path) -> None:
        """Test session with multiple phases tracked."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom**: Endogenous-First — primary endogenous source: `MANIFESTO.md`.

---

## Orchestration Plan

### Phase 1 — Documentation

---

### Phase 2 — Scripts

---

### Phase 3 — Tests

---

## Pre-Compact Checkpoint

All phases tracked.

---

## Session Summary

Three phases executed.
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 0

    def test_endogenous_source_agents_md(self, tmp_path: Path) -> None:
        """Test that AGENTS.md reference counts as endogenous source."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom**: Endogenous-First — primary endogenous source: `AGENTS.md §Phase-Gate-Sequence`.

---

## Orchestration Plan

### Phase 1

---

## Pre-Compact Checkpoint

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 0

    def test_endogenous_source_docs_folder(self, tmp_path: Path) -> None:
        """Test that docs/ reference counts as endogenous source."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom**: Endogenous-First — primary endogenous source: `docs/guides/session-management.md`.

---

## Orchestration Plan

### Phase 1

---

## Pre-Compact Checkpoint

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 0

    def test_endogenous_source_scripts_folder(self, tmp_path: Path) -> None:
        """Test that scripts/ reference counts as endogenous source."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom**: Endogenous-First — primary endogenous source: `scripts/validate_agent_files.py`.

---

## Orchestration Plan

### Phase 1

---

## Pre-Compact Checkpoint

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 0

    def test_empty_session_start(self, tmp_path: Path) -> None:
        """Test handling of empty ## Session Start section."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

## Orchestration Plan

### Phase 1

---

## Pre-Compact Checkpoint

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code >= 1  # Should fail on structural or axiom check

    def test_multiple_failures_combined(self, tmp_path: Path) -> None:
        """Test file with both structural and encoding drift failures."""
        session_file = tmp_path / "session.md"
        session_file.write_text(
            """# Session

## Session Start

Some notes without axiom or endogenous source.

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code >= 1
        assert len(messages) >= 2  # At least axiom + endogenous source failures


class TestValidateSessionIntegration:
    """Integration tests using actual temp files."""

    def test_realistic_session_structure(self, tmp_path: Path) -> None:
        """Test a realistic multi-phase session structure."""
        session_file = tmp_path / "realistic.md"
        session_file.write_text(
            """# Session — feat-branch / 2026-03-11

## Session Start

**Governing axiom**: Programmatic-First — primary endogenous source: `docs/plans/2026-03-10-workplan.md`.

On branch `feat`. Workplan review complete. Ready to begin.

---

## Orchestration Plan

### Phase 1 — Documentation (Execute)

**Issues**: #116, #126

---

### Phase 2 — Scripts (Execute)

**Issues**: #121, #122

---

## Phase 1 Review — Review Gate

Status: ✅ APPROVED

---

## Pre-Compact Checkpoint

Session progressing normally. Phase 1 complete, Phase 2 running.

---

## Session Summary

Made progress on documentation and scripts. Ready for next phase.
"""
        )

        exit_code, messages = validate_session_file(session_file)
        assert exit_code == 0

    def test_governance_axiom_variations(self, tmp_path: Path) -> None:
        """Test recognition of different governance axiom formats."""
        session_file = tmp_path / "axiom_variants.md"
        session_file.write_text(
            """# Session

## Session Start

**Governing axiom:** Endogenous-First

Source: MANIFESTO.md

---

## Orchestration Plan

### Phase 1

---

## Pre-Compact Checkpoint

---

## Session Summary
"""
        )

        exit_code, messages = validate_session_file(session_file)
        # Should pass with "Governing axiom:" present (note the colon)
        assert exit_code == 0


class TestCheckValueFidelity:
    """Tests for the constitutional AI value fidelity hook (OQ-4)."""

    def _well_formed(self, tmp_path: Path) -> Path:
        f = tmp_path / "session.md"
        f.write_text(
            """## Session Start

**Governing axiom**: Endogenous-First — primary endogenous source: MANIFESTO.md.

See also MANIFESTO.md §1 for full axiom definition.

## Session Summary

Phase 1 complete. Next session: continue Phase 2 implementation.
"""
        )
        return f

    def test_well_formed_session_passes(self, tmp_path: Path) -> None:
        f = self._well_formed(tmp_path)
        warnings = check_value_fidelity(f)
        assert warnings == [], f"Expected no warnings, got: {warnings}"

    def test_missing_session_start_warns(self, tmp_path: Path) -> None:
        f = tmp_path / "session.md"
        f.write_text("## Other Section\n\nContent with MANIFESTO.md and MANIFESTO.md refs.\n")
        warnings = check_value_fidelity(f)
        msgs = [w.message for w in warnings]
        assert any("Session Start" in m for m in msgs)

    def test_missing_governing_axiom_warns(self, tmp_path: Path) -> None:
        f = tmp_path / "session.md"
        f.write_text(
            "## Session Start\n\nSome content without the required phrase. "
            "MANIFESTO.md and MANIFESTO.md mentioned.\n\n"
            "## Session Summary\n\nNext session: continue work.\n"
        )
        warnings = check_value_fidelity(f)
        msgs = [w.message for w in warnings]
        assert any("Governing axiom" in m for m in msgs)

    def test_insufficient_manifesto_citations_warns(self, tmp_path: Path) -> None:
        f = tmp_path / "session.md"
        f.write_text(
            "## Session Start\n\n**Governing axiom**: Endogenous-First — source: MANIFESTO.md.\n\n"
            "## Session Summary\n\nNext session: Phase 2.\n"
        )
        # Only 1 MANIFESTO.md reference — should warn
        warnings = check_value_fidelity(f)
        msgs = [w.message for w in warnings]
        assert any("MANIFESTO" in m for m in msgs)

    def test_two_manifesto_citations_silent(self, tmp_path: Path) -> None:
        f = self._well_formed(tmp_path)  # has 2 references
        warnings = check_value_fidelity(f)
        fidelity_warnings = [w for w in warnings if "MANIFESTO" in w.message]
        assert fidelity_warnings == []

    def test_summary_without_forward_ref_warns(self, tmp_path: Path) -> None:
        f = tmp_path / "session.md"
        f.write_text(
            "## Session Start\n\n**Governing axiom**: Endogenous-First. MANIFESTO.md §1. MANIFESTO.md.\n\n"
            "## Session Summary\n\nPhase 1 complete. All items addressed.\n"
        )
        warnings = check_value_fidelity(f)
        msgs = [w.message for w in warnings]
        assert any("forward reference" in m for m in msgs)

    def test_no_summary_section_no_forward_ref_warning(self, tmp_path: Path) -> None:
        """If no ## Session Summary exists, forward-ref check is skipped."""
        f = tmp_path / "session.md"
        f.write_text("## Session Start\n\n**Governing axiom**: Endogenous-First. MANIFESTO.md. MANIFESTO.md.\n")
        warnings = check_value_fidelity(f)
        msgs = [w.message for w in warnings]
        assert not any("forward reference" in m for m in msgs)

    def test_file_not_found_returns_error(self, tmp_path: Path) -> None:
        warnings = check_value_fidelity(tmp_path / "missing.md")
        assert len(warnings) == 1
        assert warnings[0].severity == "error"
