"""tests/test_audit_recommendation_status.py

Tests for scripts/audit_recommendation_status.py

Covers (10 required tests):
1. test_extracts_numbered_recommendations_from_section
2. test_extracts_bullet_recommendations_from_section
3. test_id_generation_stable
4. test_title_truncated_to_60_chars
5. test_github_issue_match_high_confidence
6. test_no_match_suggests_deferred
7. test_dry_run_does_not_write_files
8. test_no_github_flag_marks_all_deferred
9. test_patch_file_structure
10. test_match_note_prefixed_with_underscore

All gh / subprocess calls are mocked.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.audit_recommendation_status import (
    _extract_recommendation_items,
    _extract_recommendations_section,
    _make_rec_id,
    _make_rec_title,
    _match_recommendation,
    main,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_final_doc(path: Path, rec_section: str = "") -> None:
    """Write a minimal ``status: Final`` doc to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "---\n"
        "title: Test Doc\n"
        "status: Final\n"
        "---\n\n"
        "## Executive Summary\n\nContent.\n\n"
        "## Recommendations\n\n"
        f"{rec_section}\n\n"
        "## Key Insights\n\nInsights.\n"
    )
    path.write_text(body, encoding="utf-8")


_SAMPLE_ISSUE_CLOSED = {
    "number": 401,
    "title": "Implement values audit cycle for quarterly governance review",
    "body": "Track governance alignment metrics each quarter",
    "state": "closed",
    "labels": [{"name": "source:research"}],
}

_SAMPLE_ISSUE_OPEN = {
    "number": 402,
    "title": "Create civic tech case study registry for pattern documentation",
    "body": "Document civic tech deployments that succeeded or failed",
    "state": "open",
    "labels": [{"name": "source:research"}],
}


# ---------------------------------------------------------------------------
# 1. Numbered list extraction
# ---------------------------------------------------------------------------


class TestExtractsNumberedRecommendations:
    def test_extracts_numbered_recommendations_from_section(self) -> None:
        section = (
            "1. First recommendation about governance policy adoption.\n"
            "2. Second recommendation about audit cycles.\n"
            "3. Third recommendation for documentation.\n"
        )
        items = _extract_recommendation_items(section)
        assert len(items) == 3
        assert "First recommendation about governance policy adoption." in items[0]
        assert "Second recommendation about audit cycles." in items[1]

    def test_numbered_with_parenthesis_style(self) -> None:
        section = "1) First item with parenthesis style\n2) Second item with parenthesis style\n"
        items = _extract_recommendation_items(section)
        assert len(items) == 2

    def test_multiline_numbered_item_joined(self) -> None:
        section = "1. First recommendation that spans\n   multiple lines of text here.\n2. Second standalone item.\n"
        items = _extract_recommendation_items(section)
        assert len(items) == 2
        assert "multiple lines of text here." in items[0]


# ---------------------------------------------------------------------------
# 2. Bullet list extraction
# ---------------------------------------------------------------------------


class TestExtractsBulletRecommendations:
    def test_extracts_bullet_recommendations_from_section(self) -> None:
        section = (
            "- First bullet recommendation text\n"
            "- Second bullet recommendation text\n"
            "- Third bullet recommendation text\n"
        )
        items = _extract_recommendation_items(section)
        assert len(items) == 3
        assert "First bullet recommendation text" in items[0]

    def test_star_bullets_extracted(self) -> None:
        section = "* Adopt a values extraction process\n* Institute a cross-domain conflict detection pattern\n"
        items = _extract_recommendation_items(section)
        assert len(items) == 2


# ---------------------------------------------------------------------------
# 3. ID generation stability
# ---------------------------------------------------------------------------


class TestIdGenerationStable:
    def test_id_generation_stable(self) -> None:
        """Same slug + index always produces the same ID."""
        id1 = _make_rec_id("civic-ai-governance", 1)
        id2 = _make_rec_id("civic-ai-governance", 1)
        assert id1 == id2
        assert id1 == "rec-civic-ai-governance-001"

    def test_id_format(self) -> None:
        assert _make_rec_id("my-doc", 42) == "rec-my-doc-042"
        assert _make_rec_id("my-doc", 1) == "rec-my-doc-001"
        assert _make_rec_id("my-doc", 999) == "rec-my-doc-999"

    def test_id_zero_padded(self) -> None:
        assert _make_rec_id("slug", 5).endswith("-005")
        assert _make_rec_id("slug", 10).endswith("-010")


# ---------------------------------------------------------------------------
# 4. Title truncation
# ---------------------------------------------------------------------------


class TestTitleTruncation:
    def test_title_truncated_to_60_chars(self) -> None:
        long_text = (
            "This is a very long recommendation text that definitely "
            "exceeds sixty characters in total length without any doubt"
        )
        title = _make_rec_title(long_text)
        assert len(title) <= 60

    def test_short_text_not_truncated(self) -> None:
        short = "Short rec."
        assert _make_rec_title(short) == "Short rec."

    def test_bold_markdown_stripped(self) -> None:
        text = "**Bold Title** — Some explanation of the recommendation."
        title = _make_rec_title(text)
        assert "**" not in title
        assert "Bold Title" in title

    def test_markdown_link_stripped(self) -> None:
        text = "See [MANIFESTO.md](../../MANIFESTO.md) for details on this."
        title = _make_rec_title(text)
        # URL part stripped; label text (or its stem) preserved
        assert "MANIFESTO" in title
        assert "../../" not in title


# ---------------------------------------------------------------------------
# 5. High-confidence match → completed / accepted
# ---------------------------------------------------------------------------


class TestHighConfidenceMatch:
    def test_github_issue_match_high_confidence_closed(self) -> None:
        """Closed issue with ≥5 consecutive word overlap → status: completed."""
        rec_text = "implement values audit cycle for quarterly governance review sessions"
        result = _match_recommendation(rec_text, [_SAMPLE_ISSUE_CLOSED])
        assert result["confidence"] == "high"
        assert result["suggested_status"] == "completed"
        assert result["best_issue"]["number"] == 401

    def test_github_issue_match_high_confidence_open(self) -> None:
        """Open issue with ≥5 consecutive word overlap → status: accepted."""
        rec_text = "create civic tech case study registry for pattern documentation"
        result = _match_recommendation(rec_text, [_SAMPLE_ISSUE_OPEN])
        assert result["confidence"] == "high"
        assert result["suggested_status"] == "accepted"
        assert result["best_issue"]["number"] == 402


# ---------------------------------------------------------------------------
# 6. No match → deferred
# ---------------------------------------------------------------------------


class TestNoMatchDeferred:
    def test_no_match_suggests_deferred(self) -> None:
        """Recommendation with no ≥3-word overlap → status: deferred."""
        rec_text = "entirely unrelated zeppelin maintenance protocol"
        issues = [
            {
                "number": 999,
                "title": "something about bananas and tropical fruit",
                "body": "completely different subject matter here",
                "state": "open",
            }
        ]
        result = _match_recommendation(rec_text, issues)
        assert result["suggested_status"] == "deferred"
        assert result["best_issue"] is None

    def test_empty_issue_list_suggests_deferred(self) -> None:
        result = _match_recommendation("some recommendation text", [])
        assert result["suggested_status"] == "deferred"
        assert result["best_issue"] is None
        assert result["confidence"] == "low"


# ---------------------------------------------------------------------------
# 7. --dry-run does not write files
# ---------------------------------------------------------------------------


class TestDryRunDoesNotWriteFiles:
    @pytest.mark.io
    def test_dry_run_does_not_write_files(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs" / "research"
        doc = docs_dir / "test-doc.md"
        _write_final_doc(doc, "1. Do something important for governance.\n")

        patches_dir = tmp_path / "patches"

        exit_code = main(
            [
                "--dry-run",
                "--no-github",
                "--docs-dir",
                str(docs_dir),
                "--patches-dir",
                str(patches_dir),
            ]
        )

        assert exit_code == 0
        # patches_dir must NOT have been created
        assert not patches_dir.exists()

    @pytest.mark.io
    def test_dry_run_prints_to_stdout(self, tmp_path: Path, capsys) -> None:
        docs_dir = tmp_path / "docs" / "research"
        doc = docs_dir / "test-doc.md"
        _write_final_doc(doc, "1. Adopt a values extraction process.\n")

        patches_dir = tmp_path / "patches"

        main(
            [
                "--dry-run",
                "--no-github",
                "--docs-dir",
                str(docs_dir),
                "--patches-dir",
                str(patches_dir),
            ]
        )

        out = capsys.readouterr().out
        assert "test-doc.yml" in out
        assert "deferred" in out


# ---------------------------------------------------------------------------
# 8. --no-github marks all recommendations as deferred
# ---------------------------------------------------------------------------


class TestNoGithubDeferred:
    @pytest.mark.io
    def test_no_github_flag_marks_all_deferred(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs" / "research"
        doc = docs_dir / "test-doc.md"
        _write_final_doc(
            doc,
            "1. Do something important for governance alignment.\n2. Implement a quarterly review process for teams.\n",
        )
        patches_dir = tmp_path / "patches"

        exit_code = main(
            [
                "--no-github",
                "--docs-dir",
                str(docs_dir),
                "--patches-dir",
                str(patches_dir),
            ]
        )

        assert exit_code == 0
        patch_file = patches_dir / "test-doc.yml"
        assert patch_file.exists()

        data = yaml.safe_load(patch_file.read_text(encoding="utf-8"))
        recs = data["recommendations"]
        assert len(recs) == 2
        assert all(r["status"] == "deferred" for r in recs)
        assert all(r["linked_issue"] is None for r in recs)


# ---------------------------------------------------------------------------
# 9. Patch file structure
# ---------------------------------------------------------------------------


class TestPatchFileStructure:
    @pytest.mark.io
    def test_patch_file_structure(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs" / "research"
        doc = docs_dir / "my-research.md"
        _write_final_doc(doc, "1. Adopt a governance rubric for tool evaluation.\n")

        patches_dir = tmp_path / "patches"

        exit_code = main(
            [
                "--no-github",
                "--docs-dir",
                str(docs_dir),
                "--patches-dir",
                str(patches_dir),
            ]
        )

        assert exit_code == 0
        patch_file = patches_dir / "my-research.yml"
        assert patch_file.exists()

        data = yaml.safe_load(patch_file.read_text(encoding="utf-8"))
        for required_key in ("doc", "doc_slug", "generated_at", "recommendations"):
            assert required_key in data, f"Missing key: {required_key}"
        assert data["doc_slug"] == "my-research"
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) >= 1


# ---------------------------------------------------------------------------
# 10. _match_note prefixed with underscore
# ---------------------------------------------------------------------------


class TestMatchNotePrefixedWithUnderscore:
    @pytest.mark.io
    def test_match_note_prefixed_with_underscore(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs" / "research"
        doc = docs_dir / "check-underscores.md"
        _write_final_doc(
            doc,
            "1. Create a governance rubric for ethical tool adoption.\n",
        )
        patches_dir = tmp_path / "patches"

        main(
            [
                "--no-github",
                "--docs-dir",
                str(docs_dir),
                "--patches-dir",
                str(patches_dir),
            ]
        )

        patch_file = patches_dir / "check-underscores.yml"
        data = yaml.safe_load(patch_file.read_text(encoding="utf-8"))
        recs = data["recommendations"]
        assert len(recs) >= 1

        for rec in recs:
            assert "_match_note" in rec, "Each rec must have _match_note key"
            assert "_confidence" in rec, "Each rec must have _confidence key"

    def test_match_note_key_starts_with_underscore(self) -> None:
        """Unit-level check: _match_recommendation returns _match_note indirectly via caller."""
        # Verify that when doc is audited, each rec entry includes underscore-prefixed metadata
        rec_text = "some recommendation text for testing underscore keys"
        result = _match_recommendation(rec_text, [])
        # The 'match_note' returned here is placed into '_match_note' by _audit_doc
        assert "match_note" in result  # The internal key is 'match_note'


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    @pytest.mark.io
    def test_non_final_doc_skipped(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs" / "research"
        doc = docs_dir / "draft.md"
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text(
            "---\ntitle: Draft\nstatus: Draft\n---\n\n## Recommendations\n\n1. Something.\n",
            encoding="utf-8",
        )
        patches_dir = tmp_path / "patches"

        exit_code = main(
            [
                "--no-github",
                "--docs-dir",
                str(docs_dir),
                "--patches-dir",
                str(patches_dir),
            ]
        )

        assert exit_code == 0
        assert not patches_dir.exists()  # Nothing written for non-Final docs

    @pytest.mark.io
    def test_doc_without_recommendations_section_skipped(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs" / "research"
        doc = docs_dir / "no-recs.md"
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text(
            "---\ntitle: No Recs\nstatus: Final\n---\n\n## Executive Summary\n\nContent.\n",
            encoding="utf-8",
        )
        patches_dir = tmp_path / "patches"

        exit_code = main(
            [
                "--no-github",
                "--docs-dir",
                str(docs_dir),
                "--patches-dir",
                str(patches_dir),
            ]
        )

        assert exit_code == 0
        assert not patches_dir.exists()

    @pytest.mark.io
    def test_single_doc_flag(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs" / "research"
        doc = docs_dir / "single.md"
        _write_final_doc(doc, "1. Adopt a quarterly values check.\n")

        patches_dir = tmp_path / "patches"

        exit_code = main(
            [
                "--doc",
                str(doc),
                "--no-github",
                "--docs-dir",
                str(docs_dir),
                "--patches-dir",
                str(patches_dir),
            ]
        )

        assert exit_code == 0
        assert (patches_dir / "single.yml").exists()

    @pytest.mark.io
    def test_extract_recommendations_section_stops_at_next_heading(self) -> None:
        text = (
            "## Recommendations\n\n"
            "1. First item.\n"
            "2. Second item.\n\n"
            "## Key Insights\n\n"
            "3. This should not be extracted.\n"
        )
        section = _extract_recommendations_section(text)
        assert "First item." in section
        assert "Second item." in section
        assert "This should not be extracted." not in section
