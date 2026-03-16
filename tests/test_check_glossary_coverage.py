"""tests/test_check_glossary_coverage.py

Unit tests for scripts/check_glossary_coverage.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_glossary_coverage import (
    check_coverage,
    extract_bold_terms,
    extract_glossary_entries,
    fix_glossary,
    main,
    term_in_glossary,
)

# ---------------------------------------------------------------------------
# extract_bold_terms
# ---------------------------------------------------------------------------


class TestExtractBoldTerms:
    def test_basic_extraction(self):
        text = "This is **Endogenous-First** principle."
        assert "Endogenous-First" in extract_bold_terms(text)

    def test_multiple_terms(self):
        text = "Use **Algorithms Before Tokens** and **Local Compute-First** always."
        terms = extract_bold_terms(text)
        assert "Algorithms Before Tokens" in terms
        assert "Local Compute-First" in terms

    def test_skips_single_character(self):
        text = "**a** should be skipped"
        terms = extract_bold_terms(text)
        assert "a" not in terms

    def test_no_terms(self):
        text = "No bold here."
        assert extract_bold_terms(text) == set()

    def test_strips_whitespace(self):
        text = "**  SpacedTerm  ** should be stripped"
        terms = extract_bold_terms(text)
        assert "SpacedTerm" in terms


# ---------------------------------------------------------------------------
# term_in_glossary
# ---------------------------------------------------------------------------


class TestTermInGlossary:
    def test_exact_match(self):
        entries = {"endogenous-first", "minimal posture"}
        assert term_in_glossary("Endogenous-First", entries) is True

    def test_not_found(self):
        entries = {"local compute-first"}
        assert term_in_glossary("Unknown Term", entries) is False

    def test_partial_match_entry_contains_term(self):
        entries = {"endogenous-first core axiom"}
        assert term_in_glossary("Endogenous-First", entries) is True

    def test_case_insensitive(self):
        entries = {"algorithms before tokens"}
        assert term_in_glossary("Algorithms Before Tokens", entries) is True


# ---------------------------------------------------------------------------
# extract_glossary_entries
# ---------------------------------------------------------------------------


class TestExtractGlossaryEntries:
    def test_extracts_headings(self):
        text = "## My Term\n\nDefinition.\n\n## Another Term\n\nDef.\n"
        entries = extract_glossary_entries(text)
        assert "my term" in entries
        assert "another term" in entries

    def test_extracts_bold_terms(self):
        text = "**Special Term** — some definition."
        entries = extract_glossary_entries(text)
        assert "special term" in entries


# ---------------------------------------------------------------------------
# check_coverage
# ---------------------------------------------------------------------------


class TestCheckCoverage:
    @pytest.mark.io
    def test_happy_path_all_covered(self, tmp_path):
        """All bold terms in target doc present in glossary → no missing terms."""
        doc = tmp_path / "test_doc.md"
        doc.write_text("This is **MyTerm** and **AnotherTerm**.\n")
        glossary = tmp_path / "glossary.md"
        glossary.write_text("## MyTerm\n\nDef.\n\n## AnotherTerm\n\nDef.\n")

        all_terms, missing, _ = check_coverage([doc], glossary)
        assert "MyTerm" in all_terms
        assert "AnotherTerm" in all_terms
        assert len(missing) == 0

    @pytest.mark.io
    def test_missing_term_reported(self, tmp_path):
        """Bold term not in glossary → appears in missing set."""
        doc = tmp_path / "test_doc.md"
        doc.write_text("Use **GapTerm** here.\n")
        glossary = tmp_path / "glossary.md"
        glossary.write_text("## SomethingElse\n\nDef.\n")

        all_terms, missing, _ = check_coverage([doc], glossary)
        assert "GapTerm" in missing

    @pytest.mark.io
    def test_nonexistent_doc_skipped_gracefully(self, tmp_path):
        """Non-existent target file is skipped — no crash."""
        nonexistent = tmp_path / "no_such_file.md"
        glossary = tmp_path / "glossary.md"
        glossary.write_text("## Term\n\nDef.\n")

        all_terms, missing, scanned = check_coverage([nonexistent], glossary)
        assert all_terms == set()
        assert missing == set()
        # Non-existent file is not counted as scanned
        assert scanned == 0

    @pytest.mark.io
    def test_missing_glossary_all_terms_missing(self, tmp_path):
        """If glossary doesn't exist, all found terms are reported missing."""
        doc = tmp_path / "doc.md"
        doc.write_text("Use **Alpha** and **Beta**.\n")
        nonexistent_glossary = tmp_path / "no_glossary.md"

        all_terms, missing, _ = check_coverage([doc], nonexistent_glossary)
        assert "Alpha" in missing
        assert "Beta" in missing


# ---------------------------------------------------------------------------
# fix_glossary
# ---------------------------------------------------------------------------


class TestFixGlossary:
    @pytest.mark.io
    def test_fix_adds_stubs(self, tmp_path):
        """--fix creates stub entries for missing terms."""
        glossary = tmp_path / "glossary.md"
        glossary.write_text("# Glossary\n\n## ExistingTerm\n\nDef.\n")

        fix_glossary({"NewTerm"}, glossary)
        content = glossary.read_text()
        assert "## NewTerm" in content

    @pytest.mark.io
    def test_fix_is_idempotent(self, tmp_path):
        """Running fix twice doesn't duplicate stubs."""
        glossary = tmp_path / "glossary.md"
        glossary.write_text("# Glossary\n")

        fix_glossary({"DupTerm"}, glossary)
        fix_glossary({"DupTerm"}, glossary)
        content = glossary.read_text()
        assert content.count("## DupTerm") == 1

    @pytest.mark.io
    def test_fix_empty_set_no_change(self, tmp_path):
        """Empty missing set → glossary unchanged."""
        glossary = tmp_path / "glossary.md"
        original = "# Glossary\n\n## Term\n\nDef.\n"
        glossary.write_text(original)

        fix_glossary(set(), glossary)
        assert glossary.read_text() == original

    @pytest.mark.io
    def test_fix_multiple_terms(self, tmp_path):
        """Multiple missing terms → all stubs appended."""
        glossary = tmp_path / "glossary.md"
        glossary.write_text("# Glossary\n")

        fix_glossary({"TermA", "TermB", "TermC"}, glossary)
        content = glossary.read_text()
        assert "## TermA" in content
        assert "## TermB" in content
        assert "## TermC" in content


# ---------------------------------------------------------------------------
# main (integration)
# ---------------------------------------------------------------------------


class TestMain:
    @pytest.mark.io
    def test_check_exits_1_on_gap(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text("Use **MissingTerm** here.\n")
        glossary = tmp_path / "glossary.md"
        glossary.write_text("## OtherTerm\n\nDef.\n")

        result = main(["--files", str(doc), "--glossary", str(glossary), "--check"])
        assert result == 1

    @pytest.mark.io
    def test_check_exits_0_when_covered(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text("Use **CoveredTerm** here.\n")
        glossary = tmp_path / "glossary.md"
        glossary.write_text("## CoveredTerm\n\nDef.\n")

        result = main(["--files", str(doc), "--glossary", str(glossary), "--check"])
        assert result == 0

    @pytest.mark.io
    def test_no_check_exits_0_even_with_gaps(self, tmp_path):
        """Without --check, missing terms do not cause exit 1."""
        doc = tmp_path / "doc.md"
        doc.write_text("Use **GapTerm** here.\n")
        glossary = tmp_path / "glossary.md"
        glossary.write_text("## SomethingElse\n\nDef.\n")

        result = main(["--files", str(doc), "--glossary", str(glossary)])
        assert result == 0

    @pytest.mark.io
    def test_fix_flag_adds_stubs(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text("Use **NewEntry** here.\n")
        glossary = tmp_path / "glossary.md"
        glossary.write_text("# Glossary\n")

        main(["--files", str(doc), "--glossary", str(glossary), "--fix"])
        content = glossary.read_text()
        assert "## NewEntry" in content
