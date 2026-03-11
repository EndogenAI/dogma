"""
tests/test_weave_links.py

Unit and IO tests for scripts/weave_links.py — programmatic documentation
link injection via YAML concept registry.

Coverage targets:
- load_registry: missing required field (KeyError), valid registry entry count
- is_already_linked: true/false cases
- find_mentions: unlinked term, already-linked, alias detection
- inject_link: wraps correctly, idempotency, dry_run, already-wrapped, no match
- weave_file: IO dry-run leaves file unchanged, injection count > 0, scope guard
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import weave_links as wl  # noqa: E402

# ---------------------------------------------------------------------------
# load_registry
# ---------------------------------------------------------------------------


class TestLoadRegistry:
    def test_missing_concept_field_raises_key_error(self, tmp_path):
        yml = tmp_path / "reg.yml"
        yml.write_text("concepts:\n  - canonical_source: MANIFESTO.md\n    aliases: []\n")
        with pytest.raises(KeyError, match="concept"):
            wl.load_registry(yml)

    def test_missing_canonical_source_raises_key_error(self, tmp_path):
        yml = tmp_path / "reg.yml"
        yml.write_text("concepts:\n  - concept: Foo\n    aliases: []\n")
        with pytest.raises(KeyError, match="canonical_source"):
            wl.load_registry(yml)

    def test_missing_aliases_raises_key_error(self, tmp_path):
        yml = tmp_path / "reg.yml"
        yml.write_text("concepts:\n  - concept: Foo\n    canonical_source: MANIFESTO.md\n")
        with pytest.raises(KeyError, match="aliases"):
            wl.load_registry(yml)

    def test_valid_registry_returns_correct_count(self, tmp_path):
        yml = tmp_path / "reg.yml"
        yml.write_text(
            "concepts:\n"
            "  - concept: Foo\n"
            "    canonical_source: src.md\n"
            "    aliases: [foo]\n"
            "  - concept: Bar\n"
            "    canonical_source: bar.md\n"
            "    aliases: []\n"
        )
        entries = wl.load_registry(yml)
        assert len(entries) == 2

    def test_optional_scopes_not_required(self, tmp_path):
        yml = tmp_path / "reg.yml"
        yml.write_text("concepts:\n  - concept: Foo\n    canonical_source: src.md\n    aliases: []\n")
        entries = wl.load_registry(yml)
        assert entries[0].get("scopes") is None

    def test_empty_concepts_list(self, tmp_path):
        yml = tmp_path / "reg.yml"
        yml.write_text("concepts: []\n")
        entries = wl.load_registry(yml)
        assert entries == []

    def test_unsafe_canonical_source_raises_value_error(self, tmp_path):
        """javascript: scheme in canonical_source must be rejected (OWASP A03)."""
        yml = tmp_path / "reg.yml"
        yml.write_text("concepts:\n  - concept: Foo\n    canonical_source: 'javascript:alert(1)'\n    aliases: []\n")
        with pytest.raises(ValueError, match="Unsafe canonical_source"):
            wl.load_registry(yml)

    def test_https_canonical_source_accepted(self, tmp_path):
        """https:// canonical_source is a valid external link."""
        yml = tmp_path / "reg.yml"
        yml.write_text(
            "concepts:\n  - concept: Foo\n    canonical_source: 'https://example.com/doc'\n    aliases: []\n"
        )
        entries = wl.load_registry(yml)
        assert entries[0]["canonical_source"] == "https://example.com/doc"


# ---------------------------------------------------------------------------
# is_already_linked
# ---------------------------------------------------------------------------


class TestIsAlreadyLinked:
    def test_returns_true_when_link_present(self):
        line = "See [Endogenous-First](MANIFESTO.md) for details."
        assert wl.is_already_linked(line, "MANIFESTO.md") is True

    def test_returns_false_when_no_link(self):
        line = "See Endogenous-First for details."
        assert wl.is_already_linked(line, "MANIFESTO.md") is False

    def test_returns_false_for_different_target(self):
        line = "See [Endogenous-First](OTHER.md) for details."
        assert wl.is_already_linked(line, "MANIFESTO.md") is False

    def test_returns_true_for_nested_path(self):
        line = "See [D4 synthesis](docs/guides/agents.md) reference."
        assert wl.is_already_linked(line, "docs/guides/agents.md") is True


# ---------------------------------------------------------------------------
# find_mentions
# ---------------------------------------------------------------------------


class TestFindMentions:
    def make_entry(self, concept="Endogenous-First", source="MANIFESTO.md", aliases=None):
        return {
            "concept": concept,
            "canonical_source": source,
            "aliases": aliases or [],
        }

    def test_unlinked_term_detected(self):
        text = "The Endogenous-First principle is key to the system."
        entry = self.make_entry()
        results = wl.find_mentions(text, entry)
        assert len(results) == 1
        assert results[0][1] == "Endogenous-First"

    def test_already_linked_term_skipped(self):
        text = "The [Endogenous-First](MANIFESTO.md) principle is foundational."
        entry = self.make_entry()
        results = wl.find_mentions(text, entry)
        assert len(results) == 0

    def test_alias_detected(self):
        text = "The endogenous first principle guides our work here."
        entry = self.make_entry(aliases=["endogenous first"])
        results = wl.find_mentions(text, entry)
        assert len(results) == 1
        assert results[0][1] == "endogenous first"

    def test_case_insensitive_match(self):
        text = "ENDOGENOUS-FIRST is mentioned here in uppercase."
        entry = self.make_entry()
        results = wl.find_mentions(text, entry)
        assert len(results) == 1

    def test_multiple_lines_multiple_mentions(self):
        text = "Endogenous-First on line one.\nEndogenous-First on line two."
        entry = self.make_entry()
        results = wl.find_mentions(text, entry)
        assert len(results) == 2

    def test_one_report_per_line(self):
        # Both concept and alias appear on same line — only one report
        text = "Endogenous-First and endogenous first both appear here."
        entry = self.make_entry(aliases=["endogenous first"])
        results = wl.find_mentions(text, entry)
        assert len(results) == 1


# ---------------------------------------------------------------------------
# inject_link
# ---------------------------------------------------------------------------


class TestInjectLink:
    def make_entry(self, concept="Endogenous-First", source="MANIFESTO.md", aliases=None):
        return {
            "concept": concept,
            "canonical_source": source,
            "aliases": aliases or [],
        }

    def test_unlinked_term_wrapped_correctly(self):
        text = "The Endogenous-First principle is important."
        entry = self.make_entry()
        new_text, diffs = wl.inject_link(text, entry, dry_run=False)
        assert "[Endogenous-First](MANIFESTO.md)" in new_text
        assert len(diffs) > 0

    def test_only_first_occurrence_per_paragraph_wrapped(self):
        text = "Endogenous-First here and Endogenous-First again."
        entry = self.make_entry()
        new_text, _ = wl.inject_link(text, entry, dry_run=False)
        count = new_text.count("[Endogenous-First](MANIFESTO.md)")
        assert count == 1

    def test_idempotent_second_call_zero_diff(self):
        text = "The Endogenous-First principle is important."
        entry = self.make_entry()
        first_text, _ = wl.inject_link(text, entry, dry_run=False)
        _, second_diffs = wl.inject_link(first_text, entry, dry_run=False)
        assert second_diffs == []

    def test_dry_run_returns_original_text(self):
        text = "The Endogenous-First principle is important."
        entry = self.make_entry()
        new_text, diffs = wl.inject_link(text, entry, dry_run=True)
        assert new_text == text
        assert len(diffs) > 0

    def test_already_wrapped_produces_no_change(self):
        text = "The [Endogenous-First](MANIFESTO.md) principle is important."
        entry = self.make_entry()
        new_text, diffs = wl.inject_link(text, entry, dry_run=False)
        assert new_text == text
        assert diffs == []

    def test_no_match_returns_original(self):
        text = "Some completely unrelated content about other topics."
        entry = self.make_entry()
        new_text, diffs = wl.inject_link(text, entry, dry_run=False)
        assert new_text == text
        assert diffs == []

    def test_alias_injected_with_matched_case(self):
        text = "The endogenous first principle guides our work."
        entry = self.make_entry(aliases=["endogenous first"])
        new_text, diffs = wl.inject_link(text, entry, dry_run=False)
        assert "(MANIFESTO.md)" in new_text
        assert len(diffs) > 0

    def test_diff_lines_use_minus_plus_format(self):
        text = "The Endogenous-First principle is important."
        entry = self.make_entry()
        _, diffs = wl.inject_link(text, entry, dry_run=False)
        assert any(d.startswith("- ") for d in diffs)
        assert any(d.startswith("+ ") for d in diffs)

    def test_separate_paragraphs_each_get_injection(self):
        text = "Endogenous-First is key.\n\nEndogenous-First again here."
        entry = self.make_entry()
        new_text, diffs = wl.inject_link(text, entry, dry_run=False)
        count = new_text.count("[Endogenous-First](MANIFESTO.md)")
        assert count == 2  # one per paragraph


# ---------------------------------------------------------------------------
# weave_file
# ---------------------------------------------------------------------------


class TestWeaveFile:
    def make_registry(self, concept="Programmatic-First", source="AGENTS.md", aliases=None, scopes=None):
        entry = {
            "concept": concept,
            "canonical_source": source,
            "aliases": aliases or [],
        }
        if scopes:
            entry["scopes"] = scopes
        return [entry]

    @pytest.mark.io
    def test_dry_run_leaves_file_unchanged(self, tmp_path):
        md = tmp_path / "test.md"
        original = "The Programmatic-First principle is crucial here.\n"
        md.write_text(original)
        registry = self.make_registry()
        wl.weave_file(md, registry, dry_run=True, repo_root=tmp_path)
        assert md.read_text() == original

    @pytest.mark.io
    def test_injection_count_positive(self, tmp_path):
        md = tmp_path / "docs" / "test.md"
        md.parent.mkdir(parents=True)
        md.write_text("The Programmatic-First principle is crucial here.\n")
        registry = self.make_registry()
        count = wl.weave_file(md, registry, dry_run=False, repo_root=tmp_path)
        assert count > 0

    @pytest.mark.io
    def test_file_modified_when_not_dry_run(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("The Programmatic-First principle is crucial here.\n")
        registry = self.make_registry()
        wl.weave_file(md, registry, dry_run=False, repo_root=tmp_path)
        new_content = md.read_text()
        assert "[Programmatic-First](AGENTS.md)" in new_content

    @pytest.mark.io
    def test_scope_guard_skips_out_of_scope_file(self, tmp_path):
        # File is in "scripts/" — registry entry scope is "docs/" only
        md = tmp_path / "scripts" / "test.md"
        md.parent.mkdir(parents=True)
        md.write_text("The Programmatic-First principle is crucial here.\n")
        registry = self.make_registry(scopes=["docs/"])
        count = wl.weave_file(md, registry, dry_run=False, repo_root=tmp_path)
        assert count == 0

    @pytest.mark.io
    def test_scope_guard_allows_in_scope_file(self, tmp_path):
        md = tmp_path / "docs" / "guide.md"
        md.parent.mkdir(parents=True)
        md.write_text("The Programmatic-First principle is crucial here.\n")
        registry = self.make_registry(scopes=["docs/"])
        count = wl.weave_file(md, registry, dry_run=False, repo_root=tmp_path)
        assert count > 0

    @pytest.mark.io
    def test_no_injection_when_already_linked(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("The [Programmatic-First](AGENTS.md) principle is key.\n")
        registry = self.make_registry()
        count = wl.weave_file(md, registry, dry_run=False, repo_root=tmp_path)
        assert count == 0

    @pytest.mark.io
    def test_idempotent_double_call(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("The Programmatic-First principle is crucial here.\n")
        registry = self.make_registry()
        wl.weave_file(md, registry, dry_run=False, repo_root=tmp_path)
        first_content = md.read_text()
        count2 = wl.weave_file(md, registry, dry_run=False, repo_root=tmp_path)
        assert count2 == 0
        assert md.read_text() == first_content

    @pytest.mark.io
    def test_scope_file_outside_repo_root_skipped(self, tmp_path):
        """File not under repo_root raises ValueError on relative_to — entry is skipped."""
        import tempfile

        other = Path(tempfile.mkdtemp())
        md = other / "test.md"
        md.write_text("The Programmatic-First principle is crucial here.\n")
        registry = self.make_registry(scopes=["docs/"])
        # tmp_path != other, so relative_to will raise ValueError → continue
        count = wl.weave_file(md, registry, dry_run=False, repo_root=tmp_path)
        assert count == 0


# ---------------------------------------------------------------------------
# main() — CLI smoke tests
# ---------------------------------------------------------------------------


class TestMain:
    @pytest.mark.io
    def test_main_dry_run_exits_zero(self, tmp_path, monkeypatch):
        """main() with --dry-run against a temp file with a match exits 0."""
        md = tmp_path / "docs" / "guide.md"
        md.parent.mkdir(parents=True)
        md.write_text("The Programmatic-First principle is important.\n")

        reg = tmp_path / "data" / "reg.yml"
        reg.parent.mkdir(parents=True)
        reg.write_text("concepts:\n  - concept: Programmatic-First\n    canonical_source: AGENTS.md\n    aliases: []\n")

        monkeypatch.chdir(tmp_path)
        # Stub find_repo_root to return tmp_path
        monkeypatch.setattr(wl, "find_repo_root", lambda: tmp_path)
        import sys

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "weave_links.py",
                "--scope",
                str(md),
                "--registry",
                str(reg),
                "--dry-run",
            ],
        )
        with pytest.raises(SystemExit) as exc:
            wl.main()
        assert exc.value.code == 0

    @pytest.mark.io
    def test_main_missing_registry_exits_one(self, tmp_path, monkeypatch):
        """main() exits 1 when registry file does not exist."""
        monkeypatch.setattr(wl, "find_repo_root", lambda: tmp_path)
        import sys

        monkeypatch.setattr(
            sys,
            "argv",
            ["weave_links.py", "--registry", str(tmp_path / "nonexistent.yml")],
        )
        with pytest.raises(SystemExit) as exc:
            wl.main()
        assert exc.value.code == 1

    @pytest.mark.io
    def test_main_scope_outside_repo_root_exits_one(self, tmp_path, monkeypatch):
        """main() exits 1 when --scope resolves outside the repo root (OWASP A01)."""
        import tempfile

        outside = Path(tempfile.mkdtemp())
        monkeypatch.setattr(wl, "find_repo_root", lambda: tmp_path)
        import sys

        monkeypatch.setattr(
            sys,
            "argv",
            ["weave_links.py", "--scope", str(outside)],
        )
        with pytest.raises(SystemExit) as exc:
            wl.main()
        assert exc.value.code == 1


# ---------------------------------------------------------------------------
# Idempotency Guard
# ---------------------------------------------------------------------------


class TestIdempotencyGuard:
    def test_is_file_already_woven_returns_false_for_new_file(self, tmp_path):
        """A file without the marker is not yet woven."""
        md = tmp_path / "new.md"
        md.write_text("# Heading\n\nContent here.")
        assert wl.is_file_already_woven(md) is False

    def test_is_file_already_woven_returns_true_for_marked_file(self, tmp_path):
        """A file with the idempotency marker is already woven."""
        md = tmp_path / "woven.md"
        md.write_text("# Heading\n\nContent here.\n\n<!-- WOVEN_LINK_COMPLETE -->")
        assert wl.is_file_already_woven(md) is True

    def test_add_woven_marker_appends_marker_to_file(self, tmp_path):
        """add_woven_marker appends the marker at EOF."""
        content = "# Heading\n\nContent here."
        marked = wl.add_woven_marker(content)
        assert "<!-- WOVEN_LINK_COMPLETE -->" in marked
        assert marked.endswith("<!-- WOVEN_LINK_COMPLETE -->")

    def test_add_woven_marker_idempotent(self, tmp_path):
        """Adding the marker twice produces same result."""
        content = "# Heading\n\nContent here."
        marked_once = wl.add_woven_marker(content)
        marked_twice = wl.add_woven_marker(marked_once)
        assert marked_once == marked_twice

    def test_filter_sections_returns_full_text_when_no_filter(self):
        """With no section_filter, returns full text and was_filtered=False."""
        text = "# Heading\n\nContent here."
        result_text, was_filtered = wl.filter_sections(text, None)
        assert result_text == text
        assert was_filtered is False

    def test_filter_sections_extracts_matching_section(self):
        """With filter='References', extracts only ## References section."""
        text = "# Overview\n\nIntro.\n\n## References\n\nRef content here.\n\n## Notes\n\nOther content."
        result_text, was_filtered = wl.filter_sections(text, "References")
        assert "## References" in result_text
        assert "## Notes" not in result_text
        assert was_filtered is True

    def test_filter_sections_case_insensitive_match(self):
        """Section filter matches case-insensitively."""
        text = "# Overview\n\n## REFERENCES\n\nRef content.\n\n## Notes\n\nOther."
        result_text, was_filtered = wl.filter_sections(text, "references")
        assert "## REFERENCES" in result_text
        assert was_filtered is True

    def test_filter_sections_returns_full_text_if_no_match(self):
        """If section not found, returns full text and was_filtered=False."""
        text = "# Overview\n\nContent.\n\n## Other\n\nMore."
        result_text, was_filtered = wl.filter_sections(text, "References")
        assert result_text == text
        assert was_filtered is False
