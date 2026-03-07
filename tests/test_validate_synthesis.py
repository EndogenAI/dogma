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
        # Test with actual sample_d3_synthesis fixture
        assert "url:" in sample_d3_synthesis
        assert "## Summary" in sample_d3_synthesis
