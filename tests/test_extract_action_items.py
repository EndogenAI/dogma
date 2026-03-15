"""tests/test_extract_action_items.py

Tests for scripts/extract_action_items.py
"""

from __future__ import annotations

from pathlib import Path

from scripts.extract_action_items import (
    deduplicate,
    extract_all_action_items,
    render_markdown_table,
)


class TestExtractAllActionItems:
    """Happy path and edge-case tests for extraction."""

    def test_finds_checkbox_items(self, tmp_path: Path) -> None:
        doc = tmp_path / "research-doc.md"
        doc.write_text("# Research\n\n- [ ] Implement value fidelity hook\n- [ ] Write tests\n")
        items = extract_all_action_items(tmp_path)
        assert len(items) == 2
        assert items[0] == ("research-doc.md", "Implement value fidelity hook")
        assert items[1] == ("research-doc.md", "Write tests")

    def test_finds_action_keyword_items(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("# Doc\n\n**Action:** Encode this pattern into AGENTS.md\n")
        items = extract_all_action_items(tmp_path)
        assert len(items) == 1
        assert items[0][1] == "Encode this pattern into AGENTS.md"

    def test_finds_recommendation_keyword_items(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("# Doc\n\n**Recommendation:** Use BM25 for deduplication\n")
        items = extract_all_action_items(tmp_path)
        assert len(items) == 1
        assert "BM25" in items[0][1]

    def test_finds_items_in_recommendations_section(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        content = (
            "# Doc\n\n## Recommendations\n\n"
            "- Run weekly metrics\n- Encode fidelity checks\n\n"
            "## Next\n\nOther content\n"
        )
        doc.write_text(content)
        items = extract_all_action_items(tmp_path)
        texts = [item for _, item in items]
        assert any("weekly metrics" in t for t in texts)
        assert any("fidelity checks" in t for t in texts)

    def test_empty_dir_returns_empty(self, tmp_path: Path) -> None:
        items = extract_all_action_items(tmp_path)
        assert items == []

    def test_multiple_docs(self, tmp_path: Path) -> None:
        (tmp_path / "a.md").write_text("- [ ] Task A\n")
        (tmp_path / "b.md").write_text("- [ ] Task B\n")
        items = extract_all_action_items(tmp_path)
        sources = {src for src, _ in items}
        assert "a.md" in sources
        assert "b.md" in sources

    def test_no_items_in_doc(self, tmp_path: Path) -> None:
        (tmp_path / "empty.md").write_text("# Just a heading\n\nSome prose only.\n")
        items = extract_all_action_items(tmp_path)
        assert items == []


class TestDeduplicate:
    """Deduplication logic tests."""

    def test_exact_duplicates_collapsed(self) -> None:
        items = [
            ("doc1.md", "Implement fidelity hook"),
            ("doc2.md", "Implement fidelity hook"),
        ]
        result = deduplicate(items, threshold=0.8)
        assert len(result) == 1

    def test_near_duplicates_collapsed(self) -> None:
        items = [
            ("doc1.md", "Add value fidelity check to session validator"),
            ("doc2.md", "Add fidelity check to session validator"),
        ]
        result = deduplicate(items, threshold=0.5)
        assert len(result) == 1

    def test_distinct_items_preserved(self) -> None:
        items = [
            ("doc1.md", "Implement BM25 deduplication"),
            ("doc2.md", "Write GitHub Actions workflow for CI"),
        ]
        result = deduplicate(items, threshold=0.8)
        assert len(result) == 2

    def test_empty_input(self) -> None:
        assert deduplicate([], threshold=0.8) == []

    def test_single_item(self) -> None:
        items = [("doc.md", "Single action item")]
        result = deduplicate(items, threshold=0.8)
        assert len(result) == 1


class TestRenderMarkdownTable:
    """Table rendering tests."""

    def test_renders_header_and_rows(self) -> None:
        rows = [("doc.md", "Do something", None)]
        table = render_markdown_table(rows)
        assert "| Source Doc |" in table
        assert "doc.md" in table
        assert "Do something" in table

    def test_empty_table_has_header(self) -> None:
        table = render_markdown_table([])
        assert "| Source Doc |" in table

    def test_pipe_escaped_in_content(self) -> None:
        rows = [("doc.md", "A | B task", None)]
        table = render_markdown_table(rows)
        assert r"A \| B task" in table
