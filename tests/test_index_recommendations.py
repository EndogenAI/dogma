"""tests/test_index_recommendations.py

Tests for scripts/index_recommendations.py

Covers:
- Happy path: doc with valid recommendations block
- Multiple docs: some with, some without recommendations
- Missing recommendations block warns but does not fail
- Malformed YAML warns and skips (exit 0)
- --dry-run does not write
- --check mode: stale exits 1, fresh exits 0
- Idempotency: two runs produce identical output
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.index_recommendations import (
    _is_stale,
    main,
    scan_docs,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_doc(path: Path, *, status: str = "Final", recommendations=None) -> None:
    """Write a minimal synthesis doc to *path* with valid YAML frontmatter."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fm_data: dict = {"title": "Test Doc", "status": status}
    if recommendations is not None:
        fm_data["recommendations"] = recommendations
    fm_yaml = yaml.dump(fm_data, default_flow_style=False, allow_unicode=True)
    body = f"---\n{fm_yaml}---\n\n## Executive Summary\n\nContent here.\n\n## Recommendations\n\nRec text.\n"
    path.write_text(body, encoding="utf-8")


SAMPLE_RECS = [
    {
        "id": "rec-test-doc-001",
        "title": "First recommendation",
        "status": "adopted",
        "linked_issue": 42,
        "decision_ref": "",
    },
    {
        "id": "rec-test-doc-002",
        "title": "Second recommendation",
        "status": "deferred",
        "linked_issue": None,
        "decision_ref": "",
    },
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestHappyPathSingleDoc:
    """A single doc with a valid 2-entry recommendations block → 2 registry entries."""

    @pytest.mark.io
    def test_happy_path_single_doc(self, tmp_path: Path, capsys) -> None:
        docs_dir = tmp_path / "research"
        doc = docs_dir / "test-doc.md"
        _write_doc(doc, recommendations=SAMPLE_RECS)

        exit_code = main(["--docs-dir", str(docs_dir), "--dry-run"])
        assert exit_code == 0

        out = capsys.readouterr().out
        assert "rec-test-doc-001" in out
        assert "rec-test-doc-002" in out

    @pytest.mark.io
    def test_records_contain_doc_slug(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "research"
        doc = docs_dir / "my-synthesis.md"
        _write_doc(doc, recommendations=SAMPLE_RECS)

        records, _, _, _ = scan_docs(docs_dir)
        assert all(r["doc_slug"] == "my-synthesis" for r in records)

    @pytest.mark.io
    def test_records_have_required_keys(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "research"
        doc = docs_dir / "my-synthesis.md"
        _write_doc(doc, recommendations=SAMPLE_RECS)

        records, _, _, _ = scan_docs(docs_dir)
        for r in records:
            for key in ("doc", "doc_slug", "id", "title", "status", "linked_issue", "decision_ref"):
                assert key in r, f"Missing key: {key}"


class TestMultipleDocs:
    """3 docs: 2 with recommendations, 1 without → 2 docs contribute entries."""

    @pytest.mark.io
    def test_multiple_docs(self, tmp_path: Path, capsys) -> None:
        docs_dir = tmp_path / "research"

        _write_doc(docs_dir / "doc-alpha.md", recommendations=SAMPLE_RECS[:1])
        _write_doc(docs_dir / "doc-beta.md", recommendations=SAMPLE_RECS)
        _write_doc(docs_dir / "doc-gamma.md", recommendations=None)  # no block

        records, warnings, _, _ = scan_docs(docs_dir)
        # 3 entries: 1 from alpha + 2 from beta
        assert len(records) == 3
        # 1 warning for gamma
        assert len(warnings) == 1
        assert "doc-gamma.md" in warnings[0]

    @pytest.mark.io
    def test_non_final_docs_excluded(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "research"
        _write_doc(docs_dir / "draft-doc.md", status="Draft", recommendations=SAMPLE_RECS)
        _write_doc(docs_dir / "final-doc.md", status="Final", recommendations=SAMPLE_RECS[:1])

        records, _, _, _ = scan_docs(docs_dir)
        assert len(records) == 1
        assert records[0]["doc_slug"] == "final-doc"

    @pytest.mark.io
    def test_recurses_into_nested_research_dirs_and_excludes_sources(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "research"
        _write_doc(docs_dir / "nested" / "doc-nested.md", recommendations=SAMPLE_RECS[:1])
        _write_doc(docs_dir / "sources" / "source-note.md", recommendations=SAMPLE_RECS[:1])
        _write_doc(docs_dir / "OPEN_RESEARCH.md", recommendations=SAMPLE_RECS[:1])

        records, _, _, _ = scan_docs(docs_dir)

        assert len(records) == 1
        assert records[0]["doc_slug"] == "nested/doc-nested"
        assert records[0]["doc"].endswith("nested/doc-nested.md")


class TestMissingRecommendationsBlock:
    """Doc without recommendations: key → exits 0, warning printed."""

    @pytest.mark.io
    def test_missing_recommendations_block_warns_not_fails(self, tmp_path: Path, capsys) -> None:
        docs_dir = tmp_path / "research"
        _write_doc(docs_dir / "no-recs.md", recommendations=None)

        exit_code = main(["--docs-dir", str(docs_dir), "--dry-run"])
        assert exit_code == 0

        out = capsys.readouterr().out
        assert "WARNING" in out
        assert "no-recs.md" in out

    @pytest.mark.io
    def test_missing_recs_returns_empty_records(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "research"
        _write_doc(docs_dir / "no-recs.md", recommendations=None)

        records, warnings, _, _ = scan_docs(docs_dir)
        assert records == []
        assert len(warnings) == 1

    @pytest.mark.io
    def test_explicit_empty_recommendations_list_is_not_treated_as_missing_block(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "research"
        _write_doc(docs_dir / "empty-list.md", recommendations=[])
        _write_doc(docs_dir / "missing-block.md", recommendations=None)

        records, warnings, docs_scanned, docs_with_recs = scan_docs(docs_dir)

        assert records == []
        assert docs_scanned == 2
        assert docs_with_recs == 1
        assert len(warnings) == 1
        assert "missing-block.md" in warnings[0]


class TestMalformedRecommendationEntries:
    """Malformed recommendation entries are warned and skipped deterministically."""

    @pytest.mark.io
    def test_non_dict_recommendation_entry_warns_and_is_skipped(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "research"
        _write_doc(
            docs_dir / "mixed-entries.md",
            recommendations=["bad-entry", SAMPLE_RECS[0]],
        )

        records, warnings, _, docs_with_recs = scan_docs(docs_dir)

        assert docs_with_recs == 1
        assert len(records) == 1
        assert records[0]["id"] == SAMPLE_RECS[0]["id"]
        assert any("malformed recommendation entry" in warning for warning in warnings)


class TestMalformedYaml:
    """Doc with unparseable YAML frontmatter → warns and skips (exit 0)."""

    @pytest.mark.io
    def test_malformed_yaml_warns_and_skips(self, tmp_path: Path, capsys) -> None:
        docs_dir = tmp_path / "research"
        bad_doc = docs_dir / "broken.md"
        bad_doc.parent.mkdir(parents=True, exist_ok=True)
        # Write intentionally broken YAML (unclosed list triggers yaml.YAMLError)
        bad_doc.write_text(
            "---\ntitle: Synthesis\nkey: [unclosed list\n---\n# Body",
            encoding="utf-8",
        )

        exit_code = main(["--docs-dir", str(docs_dir), "--dry-run"])
        # Should exit 0 — malformed docs are warned and skipped
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "WARNING" in captured.out or "Malformed" in captured.out or "WARNING" in captured.err


class TestDryRun:
    """--dry-run does not write any file."""

    @pytest.mark.io
    def test_dry_run_does_not_write(self, tmp_path: Path, capsys, mocker) -> None:
        docs_dir = tmp_path / "research"
        registry_path = tmp_path / "data" / "recommendations-registry.yml"
        _write_doc(docs_dir / "doc.md", recommendations=SAMPLE_RECS)

        # Patch the registry path to our temp location
        mocker.patch("scripts.index_recommendations._REGISTRY_PATH", registry_path)
        exit_code = main(["--docs-dir", str(docs_dir), "--dry-run"])

        assert exit_code == 0
        assert not registry_path.exists(), "Registry must not be written in --dry-run mode"

    @pytest.mark.io
    def test_dry_run_prints_would_write(self, tmp_path: Path, capsys) -> None:
        docs_dir = tmp_path / "research"
        _write_doc(docs_dir / "doc.md", recommendations=SAMPLE_RECS)

        exit_code = main(["--docs-dir", str(docs_dir), "--dry-run"])
        out = capsys.readouterr().out
        assert exit_code == 0
        assert "[DRY RUN]" in out


class TestCheckMode:
    """--check exits 1 if stale, 0 if fresh."""

    @pytest.mark.io
    def test_check_mode_stale(self, tmp_path: Path, capsys, mocker) -> None:
        docs_dir = tmp_path / "research"
        registry_path = tmp_path / "data" / "recommendations-registry.yml"
        _write_doc(docs_dir / "doc.md", recommendations=SAMPLE_RECS)

        # Registry is absent → stale
        mocker.patch("scripts.index_recommendations._REGISTRY_PATH", registry_path)
        exit_code = main(["--docs-dir", str(docs_dir), "--check"])

        assert exit_code == 1
        out = capsys.readouterr().out
        assert "STALE" in out

    @pytest.mark.io
    def test_check_mode_fresh(self, tmp_path: Path, capsys, mocker) -> None:
        docs_dir = tmp_path / "research"
        registry_path = tmp_path / "data" / "recommendations-registry.yml"
        _write_doc(docs_dir / "doc.md", recommendations=SAMPLE_RECS)

        # First write the registry for real
        mocker.patch("scripts.index_recommendations._REGISTRY_PATH", registry_path)
        main(["--docs-dir", str(docs_dir)])
        capsys.readouterr()  # discard output

        # Now check — should be fresh
        exit_code = main(["--docs-dir", str(docs_dir), "--check"])

        assert exit_code == 0
        out = capsys.readouterr().out
        assert "OK" in out

    @pytest.mark.io
    def test_check_mode_stale_after_doc_change(self, tmp_path: Path, capsys, mocker) -> None:
        docs_dir = tmp_path / "research"
        registry_path = tmp_path / "data" / "recommendations-registry.yml"
        _write_doc(docs_dir / "doc.md", recommendations=SAMPLE_RECS[:1])

        mocker.patch("scripts.index_recommendations._REGISTRY_PATH", registry_path)
        main(["--docs-dir", str(docs_dir)])
        capsys.readouterr()

        # Now add another recommendation to the doc — registry is stale
        _write_doc(docs_dir / "doc.md", recommendations=SAMPLE_RECS)

        exit_code = main(["--docs-dir", str(docs_dir), "--check"])

        assert exit_code == 1


class TestIdempotency:
    """Running twice produces identical output (ignoring generated_at timestamp)."""

    @pytest.mark.io
    def test_idempotency(self, tmp_path: Path, mocker) -> None:
        docs_dir = tmp_path / "research"
        registry_path = tmp_path / "data" / "recommendations-registry.yml"
        _write_doc(docs_dir / "doc.md", recommendations=SAMPLE_RECS)

        mocker.patch("scripts.index_recommendations._REGISTRY_PATH", registry_path)
        main(["--docs-dir", str(docs_dir)])
        content_first = registry_path.read_text(encoding="utf-8")

        # Remove generated_at line for comparison
        def _strip_ts(text: str) -> str:
            return "\n".join(line for line in text.splitlines() if "generated_at" not in line)

        main(["--docs-dir", str(docs_dir)])
        content_second = registry_path.read_text(encoding="utf-8")

        assert _strip_ts(content_first) == _strip_ts(content_second)


class TestRegistryFormat:
    """The written YAML registry has the expected structure."""

    @pytest.mark.io
    def test_registry_has_top_level_keys(self, tmp_path: Path, mocker) -> None:
        docs_dir = tmp_path / "research"
        registry_path = tmp_path / "data" / "recommendations-registry.yml"
        _write_doc(docs_dir / "doc.md", recommendations=SAMPLE_RECS)

        mocker.patch("scripts.index_recommendations._REGISTRY_PATH", registry_path)
        main(["--docs-dir", str(docs_dir)])

        text = registry_path.read_text(encoding="utf-8")
        yaml_text = "\n".join(line for line in text.splitlines() if not line.startswith("#"))
        data = yaml.safe_load(yaml_text)
        assert "generated_at" in data
        assert "docs_scanned" in data
        assert "docs_with_recommendations" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    @pytest.mark.io
    def test_registry_header_comment(self, tmp_path: Path, mocker) -> None:
        docs_dir = tmp_path / "research"
        registry_path = tmp_path / "data" / "recommendations-registry.yml"
        _write_doc(docs_dir / "doc.md", recommendations=SAMPLE_RECS)

        mocker.patch("scripts.index_recommendations._REGISTRY_PATH", registry_path)
        main(["--docs-dir", str(docs_dir)])

        text = registry_path.read_text(encoding="utf-8")
        assert text.startswith("# Auto-generated by scripts/index_recommendations.py")

    @pytest.mark.io
    def test_creates_data_dir_if_missing(self, tmp_path: Path, mocker) -> None:
        docs_dir = tmp_path / "research"
        registry_path = tmp_path / "nonexistent" / "subdir" / "registry.yml"
        _write_doc(docs_dir / "doc.md", recommendations=SAMPLE_RECS)

        mocker.patch("scripts.index_recommendations._REGISTRY_PATH", registry_path)
        exit_code = main(["--docs-dir", str(docs_dir)])

        assert exit_code == 0
        assert registry_path.exists()


class TestIsStaleHelper:
    """Unit tests for the _is_stale comparison helper."""

    def test_stale_when_registry_missing(self) -> None:
        assert _is_stale({"recommendations": [{"id": "x"}]}, None) is True

    def test_not_stale_when_identical(self) -> None:
        recs = [{"doc": "a", "id": "x", "title": "T", "status": "adopted", "linked_issue": "1", "decision_ref": ""}]
        current = {
            "docs_scanned": 1,
            "docs_with_recommendations": 1,
            "recommendations": recs,
        }
        existing = {
            "docs_scanned": 1,
            "docs_with_recommendations": 1,
            "recommendations": recs,
        }
        assert _is_stale(current, existing) is False

    def test_stale_when_record_added(self) -> None:
        recs1 = [{"doc": "a", "id": "x", "title": "T", "status": "adopted", "linked_issue": "1", "decision_ref": ""}]
        recs2 = recs1 + [
            {"doc": "b", "id": "y", "title": "T2", "status": "deferred", "linked_issue": "", "decision_ref": ""}
        ]
        current = {
            "docs_scanned": 2,
            "docs_with_recommendations": 2,
            "recommendations": recs2,
        }
        existing = {
            "docs_scanned": 1,
            "docs_with_recommendations": 1,
            "recommendations": recs1,
        }
        assert _is_stale(current, existing) is True

    def test_stale_when_registry_count_metadata_changes(self) -> None:
        recs = [{"doc": "a", "id": "x", "title": "T", "status": "adopted", "linked_issue": "1", "decision_ref": ""}]
        current = {
            "docs_scanned": 2,
            "docs_with_recommendations": 1,
            "recommendations": recs,
        }
        existing = {
            "docs_scanned": 1,
            "docs_with_recommendations": 1,
            "recommendations": recs,
        }
        assert _is_stale(current, existing) is True


class TestCheckModeMetadataStaleness:
    """--check also detects stale count metadata when recommendation rows are unchanged."""

    @pytest.mark.io
    def test_check_mode_stale_when_only_registry_counts_change(self, tmp_path: Path, capsys, mocker) -> None:
        docs_dir = tmp_path / "research"
        registry_path = tmp_path / "data" / "recommendations-registry.yml"
        _write_doc(docs_dir / "doc.md", recommendations=SAMPLE_RECS[:1])

        mocker.patch("scripts.index_recommendations._REGISTRY_PATH", registry_path)
        main(["--docs-dir", str(docs_dir)])
        capsys.readouterr()

        existing = yaml.safe_load(
            "\n".join(
                line for line in registry_path.read_text(encoding="utf-8").splitlines() if not line.startswith("#")
            )
        )
        existing["docs_scanned"] = existing["docs_scanned"] + 1
        registry_path.write_text(
            "# Auto-generated by scripts/index_recommendations.py — do not edit manually\n"
            "# Run: uv run python scripts/index_recommendations.py\n"
            + yaml.dump(existing, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

        exit_code = main(["--docs-dir", str(docs_dir), "--check"])

        assert exit_code == 1
        assert "STALE" in capsys.readouterr().out
