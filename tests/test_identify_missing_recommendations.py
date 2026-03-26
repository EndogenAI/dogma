"""Tests for scripts/identify_missing_recommendations.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import scripts.identify_missing_recommendations as imr

# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------


def test_parse_frontmatter_valid_with_recommendations_list() -> None:
    content = "---\ntitle: Test\nstatus: Final\nrecommendations:\n  - id: rec-001\n    title: First\n---\n## Body\n"
    fm = imr.parse_frontmatter(content)
    assert fm["title"] == "Test"
    assert fm["status"] == "Final"
    assert isinstance(fm["recommendations"], list)
    assert len(fm["recommendations"]) == 1
    assert fm["recommendations"][0]["id"] == "rec-001"


def test_parse_frontmatter_thematic_break_in_body_not_mistaken_for_frontmatter_end() -> None:
    content = (
        "---\n"
        "title: Thematic\n"
        "status: Final\n"
        "---\n"
        "## Section\n"
        "\n"
        "Text before break.\n"
        "\n"
        "---\n"
        "\n"
        "Text after thematic break.\n"
    )
    fm = imr.parse_frontmatter(content)
    assert fm["title"] == "Thematic"
    assert fm["status"] == "Final"


def test_parse_frontmatter_no_frontmatter_returns_empty_dict() -> None:
    content = "# Just a heading\n\nSome body text.\n"
    assert imr.parse_frontmatter(content) == {}


def test_parse_frontmatter_malformed_yaml_returns_empty_dict() -> None:
    content = "---\ntitle: [\nunclosed bracket\n---\n## Body\n"
    assert imr.parse_frontmatter(content) == {}


# ---------------------------------------------------------------------------
# extract_body_content
# ---------------------------------------------------------------------------


def test_extract_body_content_strips_frontmatter() -> None:
    content = "---\ntitle: Test\n---\n## Body Heading\n\nBody text here.\n"
    body = imr.extract_body_content(content)
    assert body.startswith("## Body Heading")
    assert "title:" not in body


# ---------------------------------------------------------------------------
# has_recommendations_section
# ---------------------------------------------------------------------------


def test_has_recommendations_section_returns_true_when_present() -> None:
    body = "## Summary\n\nText.\n\n## Recommendations\n\n- Do this.\n"
    assert imr.has_recommendations_section(body) is True


def test_has_recommendations_section_returns_false_when_absent() -> None:
    body = "## Summary\n\nText.\n\n## Methodology\n\nNo recs.\n"
    assert imr.has_recommendations_section(body) is False


# ---------------------------------------------------------------------------
# count_recommendations_in_frontmatter
# ---------------------------------------------------------------------------


def test_count_recommendations_in_frontmatter_returns_correct_count() -> None:
    fm: dict = {"title": "Test", "recommendations": [{"id": "r1"}, {"id": "r2"}]}
    assert imr.count_recommendations_in_frontmatter(fm) == 2


def test_count_recommendations_in_frontmatter_returns_zero_when_key_missing() -> None:
    fm: dict = {"title": "Test", "status": "Final"}
    assert imr.count_recommendations_in_frontmatter(fm) == 0


# ---------------------------------------------------------------------------
# inventory_research_docs
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_inventory_research_docs_skips_non_final_and_captures_final(tmp_path: Path) -> None:
    research_dir = tmp_path / "research"
    research_dir.mkdir()

    # Draft doc — must be skipped
    (research_dir / "draft.md").write_text(
        "---\ntitle: Draft\nstatus: Draft\n---\n## Body\n",
        encoding="utf-8",
    )

    # Final doc WITH body Recommendations section and frontmatter list
    (research_dir / "final-with.md").write_text(
        "---\ntitle: With Recs\nstatus: Final\nrecommendations:\n  - id: r1\n    title: Rec\n---\n"
        "## Summary\n\n## Recommendations\n\n- Do this.\n",
        encoding="utf-8",
    )

    # Final doc WITHOUT body Recommendations section
    (research_dir / "final-without.md").write_text(
        "---\ntitle: Without Recs\nstatus: Final\n---\n## Summary\n\nNo recs section.\n",
        encoding="utf-8",
    )

    records = imr.inventory_research_docs(research_dir)
    filenames = [r["filename"] for r in records]

    assert not any("draft" in f for f in filenames), "Draft docs must be skipped"
    assert len(records) == 2

    with_rec = next(r for r in records if "final-with" in r["filename"])
    without_rec = next(r for r in records if "final-without" in r["filename"])

    assert with_rec["has_body_recommendations"] is True
    assert with_rec["recommendation_count"] == 1
    assert without_rec["has_body_recommendations"] is False
    assert without_rec["recommendation_count"] == 0


# ---------------------------------------------------------------------------
# subprocess / exit codes
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_subprocess_exit_code_valid_against_real_repo() -> None:
    """Script exits 0 or 1 when run against the real docs/research/ (not a crash)."""
    script_path = Path(__file__).parent.parent / "scripts" / "identify_missing_recommendations.py"
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode in {0, 1}, (
        f"Script crashed with unexpected exit code {result.returncode}.\nstderr: {result.stderr}"
    )
