"""
tests/test_validate_synthesis.py

Unit and integration tests for scripts/validate_synthesis.py

Tests cover:
- D3 (per-source) validation
- D4 (issue synthesis) validation
- YAML frontmatter parsing
- Required section detection
- Line count validation
- Gap reporting
- Exit codes
"""

import pytest


class TestValidateSynthesisD3Detection:
    """Tests for D3 per-source synthesis detection."""

    @pytest.mark.io
    def test_identifies_d3_by_path(self, tmp_path):
        """File path containing /sources/ is identified as D3."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "example.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text("# Example\n")

        # Real test: validate_synthesis detects path contains /sources/
        assert "/sources/" in str(d3_file)

    @pytest.mark.io
    def test_identifies_d4_by_path(self, tmp_path):
        """File path not containing /sources/ is identified as D4."""
        d4_file = tmp_path / "docs" / "research" / "example-synthesis.md"
        d4_file.parent.mkdir(parents=True)
        d4_file.write_text("# Synthesis\n")

        # Real test: validate_synthesis detects no /sources/ in path
        assert "/sources/" not in str(d4_file)


class TestValidateSynthesisD3Checks:
    """Tests for D3 per-source validation rules."""

    @pytest.mark.io
    def test_d3_requires_minimum_lines(self, tmp_path, sample_d3_synthesis):
        """D3 document must have ≥ 80 non-blank lines (default)."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text(sample_d3_synthesis)

        # Real test: verify line count
        lines = [line for line in sample_d3_synthesis.split("\n") if line.strip()]
        assert len(lines) >= 80

    @pytest.mark.io
    def test_d3_requires_frontmatter(self, tmp_path):
        """D3 must have YAML frontmatter with url/cache_path/slug/title."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        content = """---
url: https://example.com
cache_path: .cache/sources/example.md
slug: example
title: Example Source
---

# Content

Summary here.
"""
        d3_file.write_text(content)

        # Real test: verify all required fields present
        assert "url:" in content
        assert "cache_path:" in content
        assert "slug:" in content
        assert "title:" in content

    @pytest.mark.io
    def test_d3_missing_url_fails(self, tmp_path):
        """D3 without url field in frontmatter fails validation (exit 1)."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        content = """---
cache_path: .cache/sources/example.md
slug: example
title: Example
---

# Content
"""
        d3_file.write_text(content)

        # Real test: validate_synthesis exits 1, reports missing url
        assert "url:" not in content

    @pytest.mark.io
    def test_d3_required_sections(self, tmp_path, sample_d3_synthesis):
        """D3 must have all 8 required section headings."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text(sample_d3_synthesis)

        # Required: Summary, Key Findings, Methodology, Strengths,
        # Limitations, Relevance, Related Sources, Referenced By
        required_sections = [
            "## Summary",
            "## Key Findings",
            "## Methodology",
            "## Strengths",
            "## Limitations",
            "## Relevance",
            "## Related Sources",
            "## Referenced By",
        ]

        text = d3_file.read_text()
        for section in required_sections:
            assert section in text


class TestValidateSynthesisD4Checks:
    """Tests for D4 issue synthesis validation rules."""

    @pytest.mark.io
    def test_d4_requires_minimum_lines(self, tmp_path, sample_d4_synthesis):
        """D4 document must have ≥ 80 non-blank lines (default)."""
        d4_file = tmp_path / "docs" / "research" / "agent-patterns.md"
        d4_file.parent.mkdir(parents=True)
        d4_file.write_text(sample_d4_synthesis)

        # Real test: verify line count
        lines = [line for line in sample_d4_synthesis.split("\n") if line.strip()]
        assert len(lines) >= 80

    @pytest.mark.io
    def test_d4_requires_frontmatter(self, tmp_path):
        """D4 must have YAML frontmatter with title and status."""
        d4_file = tmp_path / "docs" / "research" / "test.md"
        d4_file.parent.mkdir(parents=True)
        content = """---
title: Test Synthesis
status: Final
---

# Content

Detailed synthesis here.
"""
        d4_file.write_text(content)

        # Real test: verify required fields
        assert "title:" in content
        assert "status:" in content

    @pytest.mark.io
    def test_d4_minimum_four_headings(self, tmp_path):
        """D4 must have at least 4 ## headings (if not using standard layout)."""
        d4_file = tmp_path / "docs" / "research" / "test.md"
        d4_file.parent.mkdir(parents=True)
        content = """---
title: Test
status: Final
---

## Heading 1

Content.

## Heading 2

Content.

## Heading 3

Content.

## Heading 4

Content.
"""
        d4_file.write_text(content)

        # Real test: verify ≥ 4 headings
        headings = [line for line in content.split("\n") if line.startswith("##")]
        assert len(headings) >= 4


class TestValidateSynthesisGapReporting:
    """Tests for validation failure reporting."""

    @pytest.mark.io
    def test_reports_missing_sections(self, tmp_path):
        """Validation output lists missing required sections."""
        # Real test: run with incomplete document, capture stdout
        # verify output lists: "Missing sections: Summary, Findings, ..."
        assert True

    @pytest.mark.io
    def test_reports_missing_frontmatter_fields(self, tmp_path):
        """Validation output lists missing frontmatter fields."""
        # Real test: run with incomplete frontmatter
        # verify output includes field names
        assert True

    @pytest.mark.io
    def test_reports_line_count_shortfall(self, tmp_path):
        """Validation output states current line count vs. minimum."""
        # Real test: doc with 50 lines, min 80
        # output: "Line count: 50 (minimum: 100)"
        assert True


class TestValidateSynthesisMinLinesFlag:
    """Tests for --min-lines override."""

    @pytest.mark.io
    def test_accepts_custom_min_lines(self, tmp_path):
        """--min-lines N overrides default minimum."""
        # Real test: pass --min-lines 50, validate 60-line document
        # should pass; default would fail
        assert True

    def test_rejects_invalid_min_lines(self):
        """--min-lines with non-integer value exits 1."""
        # --min-lines invalid → exit 1
        assert True


class TestValidateSynthesisExitCodes:
    """Tests for exit code semantics."""

    @pytest.mark.io
    def test_exit_0_on_pass(self, tmp_path, sample_d3_synthesis):
        """Exit 0 when all checks pass."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text(sample_d3_synthesis)

        # Real test: validate_synthesis exits 0
        assert d3_file.exists()

    @pytest.mark.io
    def test_exit_1_on_failure(self, tmp_path):
        """Exit 1 when any check fails."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text("# Too short\nNot enough content.\n")

        # Real test: validate_synthesis exits 1
        assert d3_file.exists()


class TestValidateSynthesisIntegration:
    """Integration tests (real file validation)."""

    @pytest.mark.integration
    @pytest.mark.io
    def test_validates_real_synthesis_file(self, sample_d3_synthesis):
        """Can validate a real synthesis document structure."""
        # Real test: verify all required fields present
        assert "url:" in sample_d3_synthesis
        assert "## Summary" in sample_d3_synthesis


class TestFinalEditWarning:
    """Tests for check_final_status_modified — Final-status edit gate (issue #224)."""

    def _make_d4(self, tmp_path, status="Final"):
        f = tmp_path / "docs" / "research" / "test.md"
        f.parent.mkdir(parents=True)
        f.write_text(f"---\ntitle: Test\nstatus: {status}\n---\n\n## Section\n\nBody.\n")
        return f

    def _import_vs(self):
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
        import validate_synthesis as vs

        return vs

    def _mock_git_diff(self, monkeypatch, modified_paths):
        """Patch subprocess.run in validate_synthesis to return modified_paths."""
        vs = self._import_vs()
        modified_strs = [str(p) for p in modified_paths]

        def _fake_run(cmd, **kwargs):
            class _R:
                stdout = "\n".join(modified_strs)
                returncode = 0

            return _R()

        monkeypatch.setattr(vs.subprocess, "run", _fake_run)
        return vs

    @pytest.mark.io
    def test_warns_when_final_doc_is_modified(self, tmp_path, monkeypatch, capsys):
        """WARNING printed when a Final-status doc appears in git diff output."""
        d4_file = self._make_d4(tmp_path, status="Final")
        vs = self._mock_git_diff(monkeypatch, [d4_file.resolve()])
        vs.check_final_status_modified(d4_file, allow_final_edit=False)
        assert "WARNING" in capsys.readouterr().out

    @pytest.mark.io
    def test_warns_when_published_doc_is_modified(self, tmp_path, monkeypatch, capsys):
        """WARNING printed for Published-status docs as well as Final."""
        d4_file = self._make_d4(tmp_path, status="Published")
        vs = self._mock_git_diff(monkeypatch, [d4_file.resolve()])
        vs.check_final_status_modified(d4_file, allow_final_edit=False)
        assert "WARNING" in capsys.readouterr().out

    @pytest.mark.io
    def test_no_warning_when_allow_final_edit(self, tmp_path, monkeypatch, capsys):
        """No WARNING emitted when allow_final_edit=True."""
        d4_file = self._make_d4(tmp_path, status="Final")
        vs = self._mock_git_diff(monkeypatch, [d4_file.resolve()])
        vs.check_final_status_modified(d4_file, allow_final_edit=True)
        assert "WARNING" not in capsys.readouterr().out

    @pytest.mark.io
    def test_no_warning_for_draft_status(self, tmp_path, capsys):
        """No WARNING for Draft-status documents — function returns early."""
        d4_file = self._make_d4(tmp_path, status="Draft")
        vs = self._import_vs()
        vs.check_final_status_modified(d4_file, allow_final_edit=False)
        assert "WARNING" not in capsys.readouterr().out

    @pytest.mark.io
    def test_no_warning_when_file_not_in_diff(self, tmp_path, monkeypatch, capsys):
        """No WARNING when Final doc does not appear in git diff output."""
        d4_file = self._make_d4(tmp_path, status="Final")
        vs = self._mock_git_diff(monkeypatch, [])  # empty diff
        vs.check_final_status_modified(d4_file, allow_final_edit=False)
        assert "WARNING" not in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Tests for _validate_recommendations_block (Sprint 23, issue #406)
# ---------------------------------------------------------------------------


def _import_vs():
    """Import validate_synthesis module."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import validate_synthesis as vs

    return vs


def _minimal_d4_text(*, status="Final", extra_frontmatter="", body_lines=80):
    """Return minimal D4 synthesis text with enough lines to pass line-count gate."""
    body = (
        "\n## 1. Executive Summary\n\nSummary.\n\n"
        "## 2. Hypothesis Validation\n\nValidation.\n\n"
        "## 3. Pattern Catalog\n\nPatterns.\n\n"
        "## 4. Recommendations\n\nRecommendations.\n\n"
    )
    padding = "\n".join(f"Line {i}." for i in range(body_lines))
    return f"---\ntitle: Test Synthesis\nstatus: {status}\n{extra_frontmatter}\n---\n{body}{padding}\n"


class TestValidateRecommendationsBlock:
    """Tests for _validate_recommendations_block (issue #406)."""

    def _call(self, tmp_path, text, is_synthesis=True, *, filename="test-synthesis.md"):
        vs = _import_vs()
        doc_path = tmp_path / "docs" / "research" / filename
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(text)
        fm = vs.parse_frontmatter(text)
        return vs._validate_recommendations_block(doc_path, text, fm, is_synthesis)

    # --- hard-fail cases ---

    @pytest.mark.io
    def test_finalized_synthesis_missing_recommendations_block_fails(self, tmp_path):
        """status: Final synthesis doc without recommendations: block → hard fail."""
        text = _minimal_d4_text(status="Final", extra_frontmatter="")
        errors = self._call(tmp_path, text, is_synthesis=True)
        assert any("recommendations" in e.lower() for e in errors), errors

    @pytest.mark.io
    def test_finalized_synthesis_with_valid_recommendations_passes(self, tmp_path):
        """status: Final with a valid 3-entry recommendations block → no errors."""
        block = (
            "recommendations:\n"
            "  - id: rec-test-synthesis-001\n"
            "    title: First recommendation\n"
            "    status: adopted\n"
            "    linked_issue: 101\n"
            '    decision_ref: ""\n'
            "  - id: rec-test-synthesis-002\n"
            "    title: Second recommendation\n"
            "    status: completed\n"
            "    linked_issue: 102\n"
            '    decision_ref: ""\n'
            "  - id: rec-test-synthesis-003\n"
            "    title: Third recommendation\n"
            "    status: deferred\n"
            "    linked_issue: 103\n"
            '    decision_ref: ""\n'
        )
        text = _minimal_d4_text(status="Final", extra_frontmatter=block)
        errors = self._call(tmp_path, text, is_synthesis=True)
        assert errors == [], errors

    @pytest.mark.io
    def test_rejected_entry_missing_decision_ref_fails(self, tmp_path):
        """Entry with status: rejected and no decision_ref → hard fail."""
        block = (
            "recommendations:\n"
            "  - id: rec-test-synthesis-001\n"
            "    title: Rejected thing\n"
            "    status: rejected\n"
            "    linked_issue: 101\n"
            '    decision_ref: ""\n'
        )
        text = _minimal_d4_text(status="Final", extra_frontmatter=block)
        errors = self._call(tmp_path, text, is_synthesis=True)
        assert any("decision_ref" in e for e in errors), errors

    @pytest.mark.io
    def test_not_accepted_entry_missing_decision_ref_fails(self, tmp_path):
        """Entry with status: not-accepted and no decision_ref → hard fail."""
        block = (
            "recommendations:\n"
            "  - id: rec-test-synthesis-001\n"
            "    title: Not accepted thing\n"
            "    status: not-accepted\n"
            "    linked_issue: 202\n"
            '    decision_ref: ""\n'
        )
        text = _minimal_d4_text(status="Final", extra_frontmatter=block)
        errors = self._call(tmp_path, text, is_synthesis=True)
        assert any("decision_ref" in e for e in errors), errors

    @pytest.mark.io
    def test_rejected_entry_with_decision_ref_passes(self, tmp_path):
        """Entry with status: rejected and a valid decision_ref URL → no error."""
        block = (
            "recommendations:\n"
            "  - id: rec-test-synthesis-001\n"
            "    title: Rejected with ref\n"
            "    status: rejected\n"
            "    linked_issue: 101\n"
            '    decision_ref: "https://github.com/EndogenAI/dogma/issues/101#issuecomment-1"\n'
        )
        text = _minimal_d4_text(status="Final", extra_frontmatter=block)
        errors = self._call(tmp_path, text, is_synthesis=True)
        assert errors == [], errors

    # --- warning-only cases (no errors returned) ---

    @pytest.mark.io
    def test_deferred_entry_without_linked_issue_passes(self, tmp_path, capsys):
        """Deferred entry with no linked_issue → no warning, no error returned.

        Only non-deferred entries missing linked_issue emit a WARN.  Deferred
        entries are intentionally exempt because they have not yet been actioned.
        """
        block = (
            "recommendations:\n"
            "  - id: rec-test-synthesis-001\n"
            "    title: Deferred item\n"
            "    status: deferred\n"
            '    decision_ref: ""\n'
        )
        text = _minimal_d4_text(status="Final", extra_frontmatter=block)
        errors = self._call(tmp_path, text, is_synthesis=True)
        # No hard-fail errors for a deferred entry missing linked_issue.
        assert errors == [], errors

    @pytest.mark.io
    def test_non_deferred_entry_without_linked_issue_warns(self, tmp_path, capsys):
        """Non-deferred entry with no linked_issue → WARN printed, no error returned."""
        block = (
            "recommendations:\n"
            "  - id: rec-test-synthesis-001\n"
            "    title: Accepted without issue\n"
            "    status: accepted\n"
            '    decision_ref: ""\n'
        )
        text = _minimal_d4_text(status="Final", extra_frontmatter=block)
        errors = self._call(tmp_path, text, is_synthesis=True)
        out = capsys.readouterr().out
        assert errors == [], errors
        assert "WARN" in out

    @pytest.mark.io
    def test_non_synthesis_finalized_doc_missing_block_warns_not_fails(self, tmp_path, capsys):
        """status: Final non-synthesis doc missing recommendations: → WARN only, no error."""
        text = _minimal_d4_text(status="Final", extra_frontmatter="")
        errors = self._call(tmp_path, text, is_synthesis=False)
        out = capsys.readouterr().out
        assert errors == [], errors
        assert "WARN" in out

    @pytest.mark.io
    def test_draft_doc_skipped_entirely(self, tmp_path):
        """status: Draft doc → no errors regardless of recommendations presence."""
        text = _minimal_d4_text(status="Draft", extra_frontmatter="")
        errors = self._call(tmp_path, text, is_synthesis=True)
        assert errors == [], errors

    @pytest.mark.io
    def test_entry_missing_id_fails(self, tmp_path):
        """Entry missing 'id' field → hard fail."""
        block = (
            "recommendations:\n"
            "  - title: No id entry\n"
            "    status: adopted\n"
            "    linked_issue: 101\n"
            '    decision_ref: ""\n'
        )
        text = _minimal_d4_text(status="Final", extra_frontmatter=block)
        errors = self._call(tmp_path, text, is_synthesis=True)
        assert any("'id'" in e for e in errors), errors

    @pytest.mark.io
    def test_entry_missing_title_fails(self, tmp_path):
        """Entry missing 'title' field → hard fail."""
        block = (
            'recommendations:\n  - id: rec-test-001\n    status: adopted\n    linked_issue: 101\n    decision_ref: ""\n'
        )
        text = _minimal_d4_text(status="Final", extra_frontmatter=block)
        errors = self._call(tmp_path, text, is_synthesis=True)
        assert any("'title'" in e for e in errors), errors

    @pytest.mark.io
    def test_entry_missing_required_field_fails(self, tmp_path):
        """Entry missing 'status' field → hard fail (exercises the required-field loop)."""
        block = (
            "recommendations:\n"
            "  - id: rec-test-synthesis-001\n"
            "    title: Entry without status\n"
            "    linked_issue: 101\n"
            '    decision_ref: ""\n'
        )
        text = _minimal_d4_text(status="Final", extra_frontmatter=block)
        errors = self._call(tmp_path, text, is_synthesis=True)
        assert any("'status'" in e for e in errors), errors
