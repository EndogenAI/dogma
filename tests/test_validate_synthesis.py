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

from pathlib import Path

import pytest


def _minimal_d3_text(
    *,
    include_url: bool = True,
    headings: list[str] | None = None,
    extra_frontmatter: str = "",
    padding_lines: int = 60,
):
    """Return a minimal D3 document that can satisfy the validator."""
    fm_lines = [
        "---",
        *(["url: https://example.com/source"] if include_url else []),
        "cache_path: .cache/sources/example-source.md",
        "slug: example-source",
        "title: Example Source",
    ]
    if extra_frontmatter:
        fm_lines.append(extra_frontmatter.rstrip("\n"))
    fm_lines.append("---")

    section_headings = headings or [
        "## Citation",
        "## Research Question",
        "## Theoretical Framework",
        "## Methodology",
        "## Key Claims",
        "## Critical Assessment",
        "## Cross-Source Connections",
        "## Project Relevance",
    ]

    body_parts = ["# Example Source"]
    for heading in section_headings:
        body_parts.extend([heading, "", f"Details for {heading}.", ""])
    body_parts.extend(f"Supporting line {i}." for i in range(1, padding_lines + 1))

    return "\n".join(fm_lines + [""] + body_parts) + "\n"


class TestValidateSynthesisD3Detection:
    """Tests for D3 per-source synthesis detection."""

    @pytest.mark.io
    def test_identifies_d3_by_path(self, tmp_path):
        """File path containing /sources/ is identified as D3 by the validator."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "example.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text("# Example\n")

        vs = _import_vs()
        assert vs.is_d3(d3_file)

    @pytest.mark.io
    def test_identifies_d4_by_path(self, tmp_path):
        """File path outside /sources/ is treated as a D4 synthesis candidate."""
        d4_file = tmp_path / "docs" / "research" / "example-synthesis.md"
        d4_file.parent.mkdir(parents=True)
        d4_file.write_text("# Synthesis\n")

        vs = _import_vs()
        assert not vs.is_d3(d4_file)
        assert vs.is_d4_synthesis_doc(d4_file)

    @pytest.mark.io
    def test_nested_research_doc_is_treated_as_d4_synthesis(self, tmp_path):
        """Nested docs/research paths still count as D4 synthesis docs."""
        d4_file = tmp_path / "docs" / "research" / "nested" / "example-synthesis.md"
        d4_file.parent.mkdir(parents=True)
        d4_file.write_text("# Synthesis\n")

        vs = _import_vs()
        assert vs.is_d4_synthesis_doc(d4_file)

    @pytest.mark.io
    def test_open_research_file_is_not_treated_as_d4_synthesis(self, tmp_path):
        """OPEN_RESEARCH.md under docs/research is excluded from D4 synthesis checks."""
        open_research = tmp_path / "docs" / "research" / "OPEN_RESEARCH.md"
        open_research.parent.mkdir(parents=True)
        open_research.write_text("# Open Research\n")

        vs = _import_vs()
        assert not vs.is_d4_synthesis_doc(open_research)


class TestValidateSynthesisD3Checks:
    """Tests for D3 per-source validation rules."""

    @pytest.mark.io
    def test_d3_current_required_sections_pass_validation(self, tmp_path):
        """D3 validation accepts the current eight required section headings."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text(_minimal_d3_text())

        vs = _import_vs()
        passed, failures = vs.validate(d3_file, min_lines=80)
        assert passed, failures
        assert failures == []

    @pytest.mark.io
    def test_d3_accepts_keyword_variants_for_current_sections(self, tmp_path):
        """D3 fuzzy matching accepts the current keyword variants defined in the validator."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text(
            _minimal_d3_text(
                headings=[
                    "## Citation",
                    "## Research Question",
                    "## Theoretical Notes",
                    "## Source Type",
                    "## Key Findings",
                    "## Critical Assessment",
                    "## Connection to Other Sources",
                    "## Relevance to EndogenAI",
                ]
            )
        )

        vs = _import_vs()
        passed, failures = vs.validate(d3_file, min_lines=80)
        assert passed, failures

    @pytest.mark.io
    def test_d3_missing_url_fails(self, tmp_path):
        """D3 without a url/source_url frontmatter field fails validation."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text(_minimal_d3_text(include_url=False))

        vs = _import_vs()
        passed, failures = vs.validate(d3_file, min_lines=80)
        assert not passed
        assert any("URL field" in failure for failure in failures), failures

    @pytest.mark.io
    def test_d3_missing_current_required_section_reports_actual_gap(self, tmp_path):
        """D3 gap reporting names the current missing required section."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text(
            _minimal_d3_text(
                headings=[
                    "## Citation",
                    "## Research Question",
                    "## Theoretical Framework",
                    "## Methodology",
                    "## Key Claims",
                    "## Critical Assessment",
                    "## Project Relevance",
                ]
            )
        )

        vs = _import_vs()
        passed, failures = vs.validate(d3_file, min_lines=80)
        assert not passed
        assert any("Cross-Source Connections" in failure for failure in failures), failures


class TestValidateSynthesisD4Checks:
    """Tests for D4 issue synthesis validation rules."""

    @pytest.mark.io
    def test_d4_standard_layout_with_recommendations_passes_validation(self, tmp_path):
        """D4 validation passes for the current numbered layout plus recommendations block."""
        d4_file = tmp_path / "docs" / "research" / "agent-patterns.md"
        d4_file.parent.mkdir(parents=True)
        block = (
            "recommendations:\n"
            "  - id: rec-agent-patterns-001\n"
            "    title: Adopt the gate\n"
            "    status: adopted\n"
            "    linked_issue: 101\n"
            '    decision_ref: ""\n'
        )
        d4_file.write_text(_minimal_d4_text(status="Final", extra_frontmatter=block))

        vs = _import_vs()
        passed, failures = vs.validate(d4_file, min_lines=80)
        assert passed, failures

    @pytest.mark.io
    def test_d4_missing_required_headings_fails_even_with_four_h2s(self, tmp_path):
        """D4 still requires executive-summary keywords, not just any four headings."""
        d4_file = tmp_path / "docs" / "research" / "test.md"
        d4_file.parent.mkdir(parents=True)
        content = """---
title: Test Synthesis
status: Draft
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

        vs = _import_vs()
        passed, failures = vs.validate(d4_file, min_lines=4)
        assert not passed
        assert any("Executive Summary" in failure for failure in failures), failures
        assert any("Hypothesis Validation" in failure for failure in failures), failures
        assert any("Pattern Catalog" in failure for failure in failures), failures

    @pytest.mark.io
    def test_d4_validate_uses_top_level_yaml_for_required_fields(self, tmp_path):
        """Nested recommendations keys do not satisfy missing top-level title/status."""
        d4_file = tmp_path / "docs" / "research" / "masked-top-level-fields.md"
        d4_file.parent.mkdir(parents=True)
        d4_file.write_text(
            """---
recommendations:
  - id: rec-masked-001
    title: Nested recommendation title
    status: adopted
    linked_issue: 101
    decision_ref: ""
---

## 1. Executive Summary

Summary.

## 2. Hypothesis Validation

Validation.

## 3. Pattern Catalog

Patterns.

## 4. Recommendations

Recommendations.

"""
            + "\n".join(f"Line {i}." for i in range(80))
            + "\n"
        )

        vs = _import_vs()
        passed, failures = vs.validate(d4_file, min_lines=80)

        assert not passed
        assert any("Missing or empty frontmatter field: 'title'" == failure for failure in failures), failures
        assert any("Missing or empty frontmatter field: 'status'" == failure for failure in failures), failures


class TestValidateSynthesisGapReporting:
    """Tests for validation failure reporting."""

    @pytest.mark.io
    def test_reports_missing_sections(self, tmp_path):
        """validate() returns the current missing-section failure messages for D3 docs."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "missing-sections.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text(
            _minimal_d3_text(
                headings=[
                    "## Citation",
                    "## Research Question",
                    "## Methodology",
                ]
            )
        )

        vs = _import_vs()
        passed, failures = vs.validate(d3_file, min_lines=80)
        assert not passed
        assert any("Theoretical Framework" in failure for failure in failures), failures
        assert any("Critical Assessment" in failure for failure in failures), failures
        assert any("Project Relevance" in failure for failure in failures), failures

    @pytest.mark.io
    def test_reports_missing_frontmatter_fields(self, tmp_path):
        """validate() reports the specific missing D3 frontmatter fields."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "missing-frontmatter.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text("---\ntitle: Example Source\n---\n\n# Example\n\n## Citation\n\nDetails.\n")

        vs = _import_vs()
        passed, failures = vs.validate(d3_file, min_lines=1)
        assert not passed
        assert any("cache_path" in failure for failure in failures), failures
        assert any("slug" in failure for failure in failures), failures
        assert any("URL field" in failure for failure in failures), failures

    @pytest.mark.io
    def test_reports_line_count_shortfall(self, tmp_path):
        """validate() reports the actual and required non-blank line counts."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "too-short.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text(_minimal_d3_text(padding_lines=2))

        vs = _import_vs()
        passed, failures = vs.validate(d3_file, min_lines=80)
        assert not passed
        assert any("Line count too low" in failure and "minimum: 80" in failure for failure in failures), failures


class TestValidateSynthesisMinLinesFlag:
    """Tests for --min-lines override."""

    @pytest.mark.io
    def test_accepts_custom_min_lines(self, tmp_path):
        """validate() respects a caller-provided min_lines threshold."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "custom-min-lines.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text(_minimal_d3_text(padding_lines=10))

        vs = _import_vs()
        passed_default, failures_default = vs.validate(d3_file, min_lines=80)
        passed_custom, failures_custom = vs.validate(d3_file, min_lines=20)

        assert not passed_default
        assert any("Line count too low" in failure for failure in failures_default), failures_default
        assert passed_custom, failures_custom

    def test_rejects_invalid_min_lines(self, monkeypatch):
        """argparse rejects a non-integer --min-lines value with usage error exit code 2."""
        vs = _import_vs()
        monkeypatch.setattr(
            "sys.argv",
            ["validate_synthesis.py", "dummy.md", "--min-lines", "not-an-int"],
        )

        with pytest.raises(SystemExit) as excinfo:
            vs.main()

        assert excinfo.value.code == 2


class TestValidateSynthesisExitCodes:
    """Tests for exit code semantics."""

    @pytest.mark.io
    def test_exit_0_on_pass(self, tmp_path, monkeypatch, capsys):
        """CLI exits 0 and prints PASS when validation succeeds."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text(_minimal_d3_text())

        vs = _import_vs()
        monkeypatch.setattr("sys.argv", ["validate_synthesis.py", str(d3_file)])

        with pytest.raises(SystemExit) as excinfo:
            vs.main()

        out = capsys.readouterr().out
        assert excinfo.value.code == 0
        assert "PASS" in out

    @pytest.mark.io
    def test_exit_1_on_failure(self, tmp_path, monkeypatch, capsys):
        """CLI exits 1 and prints FAIL with specific reasons when validation fails."""
        d3_file = tmp_path / "docs" / "research" / "sources" / "test.md"
        d3_file.parent.mkdir(parents=True)
        d3_file.write_text("# Too short\nNot enough content.\n")

        vs = _import_vs()
        monkeypatch.setattr("sys.argv", ["validate_synthesis.py", str(d3_file)])

        with pytest.raises(SystemExit) as excinfo:
            vs.main()

        out = capsys.readouterr().out
        assert excinfo.value.code == 1
        assert "FAIL" in out
        assert "Line count too low" in out


class TestFinalEditWarning:
    """Tests for check_final_status_modified — Final-status edit gate (issue #224)."""

    def _make_d4(self, tmp_path, status="Final", extra_frontmatter=""):
        f = tmp_path / "docs" / "research" / "test.md"
        f.parent.mkdir(parents=True)
        f.write_text(f"---\ntitle: Test\nstatus: {status}\n{extra_frontmatter}---\n\n## Section\n\nBody.\n")
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
        repo_root = None
        for path in modified_paths:
            candidate = Path(path)
            if candidate.is_absolute():
                repo_root = candidate.parent.parent.parent
                break

        if repo_root is None:
            repo_root = Path.cwd()

        def _fake_run(cmd, **kwargs):
            class _R:
                def __init__(self, stdout, returncode=0):
                    self.stdout = stdout
                    self.returncode = returncode

            if len(cmd) >= 5 and cmd[0] == "git" and cmd[1] == "-C" and cmd[3] == "rev-parse":
                return _R(str(repo_root))
            if cmd == ["git", "-C", str(repo_root), "diff", "--name-only", "HEAD"]:
                return _R("\n".join(modified_strs))
            return _R("", returncode=1)

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

    @pytest.mark.io
    def test_warns_for_final_doc_with_recommendations_block(self, tmp_path, monkeypatch, capsys):
        """Nested recommendations[].status keys do not suppress the Final-status warning."""
        d4_file = self._make_d4(
            tmp_path,
            status="Final",
            extra_frontmatter=(
                "recommendations:\n"
                "  - id: rec-test-001\n"
                "    title: Keep warning logic stable\n"
                "    status: adopted\n"
                "    linked_issue: 101\n"
                '    decision_ref: ""\n'
            ),
        )
        vs = self._mock_git_diff(monkeypatch, [d4_file.resolve()])
        vs.check_final_status_modified(d4_file, allow_final_edit=False)
        assert "WARNING" in capsys.readouterr().out

    @pytest.mark.io
    def test_warns_when_git_diff_path_is_repo_relative_from_subdirectory(self, tmp_path, monkeypatch, capsys):
        """Repo-root-relative git diff paths still match when invoked from a subdirectory cwd."""
        repo_root = tmp_path / "repo"
        d4_file = self._make_d4(repo_root, status="Final")
        outside_cwd = tmp_path / "elsewhere"
        outside_cwd.mkdir()
        monkeypatch.chdir(outside_cwd)

        vs = self._import_vs()

        def _fake_run(cmd, **kwargs):
            class _R:
                def __init__(self, stdout, returncode=0):
                    self.stdout = stdout
                    self.returncode = returncode

            if cmd == ["git", "-C", str(d4_file.parent), "rev-parse", "--show-toplevel"]:
                return _R(str(repo_root))
            if cmd == ["git", "-C", str(repo_root), "diff", "--name-only", "HEAD"]:
                return _R("docs/research/test.md")
            return _R("", returncode=1)

        monkeypatch.setattr(vs.subprocess, "run", _fake_run)

        vs.check_final_status_modified(d4_file, allow_final_edit=False)
        assert "WARNING" in capsys.readouterr().out


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


def _minimal_d4_text(*, status="Final", extra_frontmatter="", body_lines=130, num_sources=4):
    """Return minimal D4 synthesis text that satisfies the m-tier gate by default.

    Defaults to body_lines=130 and num_sources=4 so that a doc without an
    explicit ``size:`` field passes the m-tier gate (130 lines / 4 sources).
    Pass smaller values to test failure scenarios.
    """
    sources_block = "sources:\n" + "".join(
        f"  - url: https://example.com/source-{i}\n    title: Source {i}\n" for i in range(1, num_sources + 1)
    )
    body = (
        "\n## 1. Executive Summary\n\nSummary.\n\n"
        "## 2. Hypothesis Validation\n\nValidation.\n\n"
        "## 3. Pattern Catalog\n\nPatterns.\n\n"
        "## 4. Recommendations\n\nRecommendations.\n\n"
    )
    padding = "\n".join(f"Line {i}." for i in range(body_lines))
    return f"---\ntitle: Test Synthesis\nstatus: {status}\n{sources_block}{extra_frontmatter}\n---\n{body}{padding}\n"


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


# ---------------------------------------------------------------------------
# Helpers for tier boundary tests (issue #477)
# ---------------------------------------------------------------------------


def _d4_with_exact_lines(
    tmp_path,
    *,
    size: str | None,
    num_sources: int,
    nonblank_lines: int,
    name: str = "tier-test.md",
):
    """Write a minimal D4 doc with exactly *nonblank_lines* non-blank lines.

    Uses ``vs.non_blank_line_count`` to measure the fixed overhead (frontmatter
    + required headings) and adds precisely enough padding lines to reach the
    requested total.
    """
    vs = _import_vs()
    size_fm = f"size: {size}\n" if size is not None else ""
    src_block = "sources:\n" + "".join(
        f"  - url: https://example.com/src-{i}\n    title: Src {i}\n" for i in range(1, num_sources + 1)
    )
    body = (
        "\n## 1. Executive Summary\n\nSummary.\n\n"
        "## 2. Hypothesis Validation\n\nValidation.\n\n"
        "## 3. Pattern Catalog\n\nPatterns.\n\n"
        "## 4. Recommendations\n\nRecommendations.\n\n"
    )
    base = f"---\ntitle: T\nstatus: Draft\n{size_fm}{src_block}---\n{body}"
    overhead = vs.non_blank_line_count(base)
    padding = "\n".join(f"P{i}." for i in range(max(0, nonblank_lines - overhead)))
    content = base + padding + "\n"
    f = tmp_path / "docs" / "research" / name
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content)
    return f


class TestD4SizeTierChecks:
    """Tests for XS\u2013XXL dynamic size tier validation (issue #477)."""

    @pytest.mark.io
    def test_xs_tier_at_floor_passes(self, tmp_path):
        """D4 with size: xs at exactly 80 non-blank lines and 2 sources passes."""
        vs = _import_vs()
        d4 = _d4_with_exact_lines(tmp_path, size="xs", num_sources=2, nonblank_lines=80)
        passed, failures = vs.validate(d4)
        assert passed, failures

    @pytest.mark.io
    def test_xs_tier_below_floor_fails_line_count(self, tmp_path):
        """D4 with size: xs and 79 non-blank lines fails with tier FAIL message."""
        vs = _import_vs()
        d4 = _d4_with_exact_lines(tmp_path, size="xs", num_sources=2, nonblank_lines=79)
        passed, failures = vs.validate(d4)
        assert not passed
        assert any("size 'xs' requires \u226580 non-blank lines" in f for f in failures), failures

    @pytest.mark.io
    def test_m_tier_at_floor_passes(self, tmp_path):
        """D4 with size: m at exactly 130 non-blank lines and 4 sources passes."""
        vs = _import_vs()
        d4 = _d4_with_exact_lines(tmp_path, size="m", num_sources=4, nonblank_lines=130)
        passed, failures = vs.validate(d4)
        assert passed, failures

    @pytest.mark.io
    def test_m_tier_below_floor_fails_line_count(self, tmp_path):
        """D4 with size: m and 129 non-blank lines fails with tier FAIL message."""
        vs = _import_vs()
        d4 = _d4_with_exact_lines(tmp_path, size="m", num_sources=4, nonblank_lines=129)
        passed, failures = vs.validate(d4)
        assert not passed
        assert any("size 'm' requires \u2265130 non-blank lines" in f for f in failures), failures

    @pytest.mark.io
    def test_xs_source_count_too_low_fails(self, tmp_path):
        """D4 with size: xs and only 1 source fails the source gate."""
        vs = _import_vs()
        d4 = _d4_with_exact_lines(tmp_path, size="xs", num_sources=1, nonblank_lines=80)
        passed, failures = vs.validate(d4)
        assert not passed
        assert any("size 'xs' requires \u22652 sources" in f for f in failures), failures

    @pytest.mark.io
    def test_m_source_count_too_low_fails(self, tmp_path):
        """D4 with size: m and only 3 sources fails the source gate."""
        vs = _import_vs()
        d4 = _d4_with_exact_lines(tmp_path, size="m", num_sources=3, nonblank_lines=130)
        passed, failures = vs.validate(d4)
        assert not passed
        assert any("size 'm' requires \u22654 sources" in f for f in failures), failures

    @pytest.mark.io
    def test_default_tier_m_below_floor_fails(self, tmp_path):
        """D4 without size: field defaults to m-tier; 129 lines fails."""
        vs = _import_vs()
        d4 = _d4_with_exact_lines(tmp_path, size=None, num_sources=4, nonblank_lines=129)
        passed, failures = vs.validate(d4)
        assert not passed
        assert any("size 'm' requires \u2265130 non-blank lines" in f for f in failures), failures

    @pytest.mark.io
    def test_default_tier_m_at_floor_passes(self, tmp_path):
        """D4 without size: field defaults to m-tier and passes at 130 lines / 4 sources."""
        vs = _import_vs()
        d4 = _d4_with_exact_lines(tmp_path, size=None, num_sources=4, nonblank_lines=130)
        passed, failures = vs.validate(d4)
        assert passed, failures
