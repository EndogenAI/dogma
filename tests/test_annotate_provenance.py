"""
tests/test_annotate_provenance.py
----------------------------------
Tests for scripts/annotate_provenance.py — x-governs: frontmatter annotation tool.

Covers:
- Happy path: file without x-governs: gets annotated when body mentions an axiom
- Idempotency: file already annotated is skipped unchanged
- --dry-run: no files written; stdout shows proposed annotation
- Missing registry: exits with code 1
- Valid file with no axiom mentions: exits 0, skipped output
- Missing manifesto: exits with code 1

All tests use tmp_path fixtures for file I/O isolation (hermetic).
Coverage target: ≥80% of scripts/annotate_provenance.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loader fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def ap_mod():
    """Load scripts/annotate_provenance.py via importlib for in-process testing."""
    spec = importlib.util.spec_from_file_location(
        "annotate_provenance",
        Path(__file__).parent.parent / "scripts" / "annotate_provenance.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_MANIFESTO_CONTENT = """\
# Manifesto

## Core Axioms

### 1. Endogenous-First

Explanation of endogenous-first.

### 2. Algorithms Before Tokens

Explanation of algorithms before tokens.

### 3. Local Compute-First

Explanation of local compute-first.

### Programmatic-First

Explanation of programmatic-first.

### Documentation-First

Explanation of documentation-first.
"""

_REGISTRY_CONTENT = """\
concepts:
  - concept: "Endogenous-First"
    canonical_source: "MANIFESTO.md"
    aliases: ["endogenous-first"]
    applications: []
    governs_source: "MANIFESTO.md"
  - concept: "Programmatic-First"
    canonical_source: "AGENTS.md"
    aliases: ["programmatic-first"]
    applications: []
    governs_source: "AGENTS.md"
"""


@pytest.fixture()
def manifesto(tmp_path):
    p = tmp_path / "MANIFESTO.md"
    p.write_text(_MANIFESTO_CONTENT, encoding="utf-8")
    return p


@pytest.fixture()
def registry(tmp_path):
    p = tmp_path / "link_registry.yml"
    p.write_text(_REGISTRY_CONTENT, encoding="utf-8")
    return p


def _make_axioms(ap_mod, manifesto, registry):
    return ap_mod.merge_axioms(
        ap_mod.load_axioms_from_manifesto(manifesto),
        ap_mod.load_axioms_from_registry(registry),
    )


# ---------------------------------------------------------------------------
# Happy path: file without x-governs: gets annotated
# ---------------------------------------------------------------------------


class TestHappyPath:
    def test_annotates_file_with_axiom_mention(self, ap_mod, manifesto, registry, tmp_path):
        target = tmp_path / "guide.md"
        target.write_text("# Guide\n\nThis follows Endogenous-First principles.\n", encoding="utf-8")

        axioms = _make_axioms(ap_mod, manifesto, registry)
        status, suggested = ap_mod.process_file(target, axioms, dry_run=False)

        assert status == "annotated"
        assert any("endogenous-first" in s for s in suggested)
        content = target.read_text()
        assert "x-governs:" in content
        assert "endogenous-first" in content

    def test_suggested_axioms_include_at_least_one(self, ap_mod, manifesto, registry, tmp_path):
        target = tmp_path / "doc.md"
        target.write_text("# Doc\n\nUses Algorithms Before Tokens approach.\n", encoding="utf-8")

        axioms = _make_axioms(ap_mod, manifesto, registry)
        status, suggested = ap_mod.process_file(target, axioms, dry_run=False)

        assert status == "annotated"
        assert len(suggested) >= 1

    def test_governs_inserted_into_existing_frontmatter(self, ap_mod, manifesto, registry, tmp_path):
        target = tmp_path / "agent.md"
        target.write_text(
            "---\nname: myagent\ndescription: test\n---\n\nEndogenous-First is key.\n",
            encoding="utf-8",
        )

        axioms = _make_axioms(ap_mod, manifesto, registry)
        ap_mod.process_file(target, axioms, dry_run=False)
        content = target.read_text()

        assert content.startswith("---\n")
        assert "x-governs:" in content
        assert "endogenous-first" in content
        # Original frontmatter keys preserved
        assert "name: myagent" in content

    def test_governs_prepended_when_no_frontmatter(self, ap_mod, manifesto, registry, tmp_path):
        target = tmp_path / "plain.md"
        target.write_text("# Title\n\nEndogenous-First is used here.\n", encoding="utf-8")

        axioms = _make_axioms(ap_mod, manifesto, registry)
        ap_mod.process_file(target, axioms, dry_run=False)
        content = target.read_text()

        assert content.startswith("---\n")
        assert "x-governs:" in content

    def test_multiple_axioms_annotated(self, ap_mod, manifesto, registry, tmp_path):
        target = tmp_path / "multi.md"
        target.write_text(
            "# Multi\n\nUses Endogenous-First and Programmatic-First.\n",
            encoding="utf-8",
        )

        axioms = _make_axioms(ap_mod, manifesto, registry)
        status, suggested = ap_mod.process_file(target, axioms, dry_run=False)

        assert status == "annotated"
        assert len(suggested) >= 2


# ---------------------------------------------------------------------------
# Idempotency: already-annotated file is skipped unchanged
# ---------------------------------------------------------------------------


class TestIdempotency:
    def test_skips_file_with_existing_governs(self, ap_mod, manifesto, registry, tmp_path):
        original = "---\nx-governs:\n  - endogenous-first\n---\n\nBody with Endogenous-First.\n"
        target = tmp_path / "annotated.md"
        target.write_text(original, encoding="utf-8")

        axioms = _make_axioms(ap_mod, manifesto, registry)
        status, suggested = ap_mod.process_file(target, axioms, dry_run=False)

        assert status == "skipped_existing"
        assert suggested == []

    def test_file_content_unchanged_when_skipped(self, ap_mod, manifesto, registry, tmp_path):
        original = "---\nx-governs:\n  - programmatic-first\n---\n\nBody.\n"
        target = tmp_path / "annotated.md"
        target.write_text(original, encoding="utf-8")

        axioms = _make_axioms(ap_mod, manifesto, registry)
        ap_mod.process_file(target, axioms, dry_run=False)

        assert target.read_text() == original

    def test_governs_not_duplicated_on_second_run(self, ap_mod, manifesto, registry, tmp_path):
        target = tmp_path / "doc.md"
        target.write_text("# Doc\n\nEndogenous-First.\n", encoding="utf-8")

        axioms = _make_axioms(ap_mod, manifesto, registry)
        ap_mod.process_file(target, axioms, dry_run=False)
        ap_mod.process_file(target, axioms, dry_run=False)

        content = target.read_text()
        assert content.count("x-governs:") == 1


# ---------------------------------------------------------------------------
# --dry-run: nothing written, stdout shows proposed annotation
# ---------------------------------------------------------------------------


class TestDryRun:
    def test_dry_run_does_not_write_file(self, ap_mod, manifesto, registry, tmp_path):
        original = "# Guide\n\nEndogenous-First is here.\n"
        target = tmp_path / "guide.md"
        target.write_text(original, encoding="utf-8")

        axioms = _make_axioms(ap_mod, manifesto, registry)
        status, suggested = ap_mod.process_file(target, axioms, dry_run=True)

        assert status == "annotated"
        assert suggested
        assert target.read_text() == original

    def test_dry_run_cli_prints_would_annotate(self, ap_mod, manifesto, registry, tmp_path, capsys):
        scope_dir = tmp_path / "scope"
        scope_dir.mkdir()
        (scope_dir / "guide.md").write_text("# Guide\n\nEndogenous-First.\n", encoding="utf-8")

        ret = ap_mod.main(
            [
                "--scope",
                str(scope_dir),
                "--dry-run",
                "--registry",
                str(registry),
                "--manifesto",
                str(manifesto),
            ]
        )

        assert ret == 0
        out = capsys.readouterr().out
        assert "DRY RUN" in out or "Would annotate" in out

    def test_dry_run_files_not_modified(self, ap_mod, manifesto, registry, tmp_path):
        scope_dir = tmp_path / "scope"
        scope_dir.mkdir()
        original = "# Guide\n\nEndogenous-First.\n"
        f = scope_dir / "guide.md"
        f.write_text(original, encoding="utf-8")

        ap_mod.main(
            [
                "--scope",
                str(scope_dir),
                "--dry-run",
                "--registry",
                str(registry),
                "--manifesto",
                str(manifesto),
            ]
        )

        assert f.read_text() == original


# ---------------------------------------------------------------------------
# Missing registry: exit code 1
# ---------------------------------------------------------------------------


class TestMissingRegistry:
    def test_missing_registry_returns_1(self, ap_mod, manifesto, tmp_path):
        scope_dir = tmp_path / "scope"
        scope_dir.mkdir()
        missing = tmp_path / "nonexistent.yml"

        ret = ap_mod.main(
            [
                "--scope",
                str(scope_dir),
                "--registry",
                str(missing),
                "--manifesto",
                str(manifesto),
            ]
        )

        assert ret == 1

    def test_missing_manifesto_returns_1(self, ap_mod, registry, tmp_path):
        scope_dir = tmp_path / "scope"
        scope_dir.mkdir()
        missing_manifesto = tmp_path / "no_manifesto.md"

        ret = ap_mod.main(
            [
                "--scope",
                str(scope_dir),
                "--registry",
                str(registry),
                "--manifesto",
                str(missing_manifesto),
            ]
        )

        assert ret == 1

    def test_missing_scope_returns_1(self, ap_mod, manifesto, registry, tmp_path):
        missing_scope = tmp_path / "nonexistent_dir"

        ret = ap_mod.main(
            [
                "--scope",
                str(missing_scope),
                "--registry",
                str(registry),
                "--manifesto",
                str(manifesto),
            ]
        )

        assert ret == 1


# ---------------------------------------------------------------------------
# Valid file with no axiom mentions: exit 0, report "no axiom mentions found"
# ---------------------------------------------------------------------------


class TestNoAxiomMentions:
    def test_no_mentions_returns_skipped(self, ap_mod, manifesto, registry, tmp_path):
        target = tmp_path / "blank.md"
        target.write_text("# Title\n\nSome content with no axiom references.\n", encoding="utf-8")

        axioms = _make_axioms(ap_mod, manifesto, registry)
        status, suggested = ap_mod.process_file(target, axioms, dry_run=False)

        assert status == "skipped_no_mentions"
        assert suggested == []
        assert "x-governs:" not in target.read_text()

    def test_no_mentions_cli_exits_0(self, ap_mod, manifesto, registry, tmp_path, capsys):
        scope_dir = tmp_path / "scope"
        scope_dir.mkdir()
        (scope_dir / "plain.md").write_text("# Plain\n\nNo special content.\n", encoding="utf-8")

        ret = ap_mod.main(
            [
                "--scope",
                str(scope_dir),
                "--registry",
                str(registry),
                "--manifesto",
                str(manifesto),
            ]
        )

        assert ret == 0
        out = capsys.readouterr().out
        assert "no axiom mentions found" in out or "skipped" in out.lower()

    def test_no_mentions_file_not_modified(self, ap_mod, manifesto, registry, tmp_path):
        original = "# Title\n\nNo axioms here.\n"
        target = tmp_path / "plain.md"
        target.write_text(original, encoding="utf-8")

        axioms = _make_axioms(ap_mod, manifesto, registry)
        ap_mod.process_file(target, axioms, dry_run=False)

        assert target.read_text() == original


# ---------------------------------------------------------------------------
# Helper unit tests
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_has_x_governs_annotation_list_form(self, ap_mod):
        text = "---\nx-governs:\n  - endogenous-first\n---\n\nBody.\n"
        assert ap_mod.has_x_governs_annotation(text) is True

    def test_has_x_governs_annotation_scalar_form(self, ap_mod):
        text = "---\nx-governs: endogenous-first\n---\n\nBody.\n"
        assert ap_mod.has_x_governs_annotation(text) is True

    def test_has_x_governs_annotation_false_when_missing(self, ap_mod):
        text = "---\nname: foo\n---\n\nBody.\n"
        assert ap_mod.has_x_governs_annotation(text) is False

    def test_has_x_governs_annotation_false_when_no_frontmatter(self, ap_mod):
        text = "# Title\n\nNo frontmatter.\n"
        assert ap_mod.has_x_governs_annotation(text) is False

    def test_load_axioms_from_manifesto(self, ap_mod, manifesto):
        axioms = ap_mod.load_axioms_from_manifesto(manifesto)
        norms = [a.norm_name for a in axioms]
        assert "endogenous-first" in norms
        assert "algorithms-before-tokens" in norms

    def test_merge_axioms_deduplicates(self, ap_mod):
        a1 = ap_mod.Axiom("Endogenous-First", "endogenous-first")
        a2 = ap_mod.Axiom("endogenous-first", "endogenous-first")
        merged = ap_mod.merge_axioms([a1], [a2])
        assert len([a for a in merged if a.norm_name == "endogenous-first"]) == 1

    def test_collect_files_single_file(self, ap_mod, tmp_path):
        f = tmp_path / "single.md"
        f.write_text("# test", encoding="utf-8")
        files = ap_mod.collect_files(f, no_recurse=False)
        assert files == [f]

    def test_collect_files_recurse(self, ap_mod, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "top.md").write_text("x", encoding="utf-8")
        (sub / "nested.md").write_text("x", encoding="utf-8")
        files = ap_mod.collect_files(tmp_path, no_recurse=False)
        assert any(f.name == "nested.md" for f in files)

    def test_collect_files_no_recurse(self, ap_mod, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "top.md").write_text("x", encoding="utf-8")
        (sub / "nested.md").write_text("x", encoding="utf-8")
        files = ap_mod.collect_files(tmp_path, no_recurse=True)
        assert not any(f.name == "nested.md" for f in files)
        assert any(f.name == "top.md" for f in files)
