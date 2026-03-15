"""tests/test_generate_script_docs.py

Tests for scripts/generate_script_docs.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_script_docs import (
    _render_doc,
    extract_module_docstring,
    run,
)


class TestExtractModuleDocstring:
    def test_extracts_docstring(self, tmp_path: Path) -> None:
        py_file = tmp_path / "sample.py"
        py_file.write_text('"""This is the module docstring."""\n\nx = 1\n')
        assert extract_module_docstring(py_file) == "This is the module docstring."

    def test_no_docstring_returns_empty(self, tmp_path: Path) -> None:
        py_file = tmp_path / "nodoc.py"
        py_file.write_text("x = 1\n")
        assert extract_module_docstring(py_file) == ""

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        assert extract_module_docstring(tmp_path / "missing.py") == ""

    def test_syntax_error_returns_empty(self, tmp_path: Path) -> None:
        py_file = tmp_path / "broken.py"
        py_file.write_text("def (\n")
        assert extract_module_docstring(py_file) == ""


class TestRenderDoc:
    def test_contains_title(self) -> None:
        content = _render_doc("my_script", "Some docstring content.")
        assert "my\\_script" in content

    def test_contains_docstring(self) -> None:
        content = _render_doc("s", "Purpose: do things")
        assert "Purpose: do things" in content

    def test_contains_hash_comment(self) -> None:
        content = _render_doc("s", "doc")
        assert "<!-- hash:" in content

    def test_no_docstring_shows_placeholder(self) -> None:
        content = _render_doc("s", "")
        assert "_No module docstring found._" in content


class TestRunGeneration:
    def test_generates_docs_for_scripts(self, tmp_path: Path) -> None:
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        docs_dir = tmp_path / "docs"

        (scripts_dir / "tool.py").write_text('"""Tool docstring."""\n')
        (scripts_dir / "helper.py").write_text('"""Helper docstring."""\n')

        result = run(scripts_dir=scripts_dir, docs_dir=docs_dir)
        assert result == 0
        assert (docs_dir / "tool.md").exists()
        assert (docs_dir / "helper.md").exists()

    def test_dry_run_does_not_write(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        docs_dir = tmp_path / "docs"

        (scripts_dir / "tool.py").write_text('"""Tool docstring."""\n')

        result = run(scripts_dir=scripts_dir, docs_dir=docs_dir, dry_run=True)
        assert result == 0
        assert not (docs_dir / "tool.md").exists()
        captured = capsys.readouterr()
        assert "[DRY RUN]" in captured.out

    def test_check_detects_stale(self, tmp_path: Path) -> None:
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        (scripts_dir / "tool.py").write_text('"""New docstring."""\n')
        # Write doc with wrong (stale) hash
        (docs_dir / "tool.md").write_text("# tool\n\nOld content\n<!-- hash:aaaaaaaaaaaaaaaa -->\n")

        result = run(scripts_dir=scripts_dir, docs_dir=docs_dir, check=True)
        assert result == 1

    def test_check_passes_when_up_to_date(self, tmp_path: Path) -> None:
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        docstring = "Up to date docstring."
        (scripts_dir / "tool.py").write_text(f'"""{docstring}"""\n')

        # First generate the doc
        run(scripts_dir=scripts_dir, docs_dir=docs_dir)

        # Now check should pass
        result = run(scripts_dir=scripts_dir, docs_dir=docs_dir, check=True)
        assert result == 0

    def test_check_missing_doc_is_stale(self, tmp_path: Path) -> None:
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        (scripts_dir / "tool.py").write_text('"""Docstring."""\n')
        # No corresponding .md file exists

        result = run(scripts_dir=scripts_dir, docs_dir=docs_dir, check=True)
        assert result == 1
