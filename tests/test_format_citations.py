"""
test_format_citations.py — Tests for scripts/format_citations.py

Covers:
- Happy path: renders full reference list from bibliography.yaml
- Happy path: --key renders a single entry
- Happy path: --inline returns tag in [AuthorYear] format
- Happy path: --list shows all keys
- Error: bibliography not found → exit 1
- Error: --key not found → exit 1
- Error: --inline not found → exit 1
- Output format checks for article, book, techreport, web types
- ACM format: numbered references [N]
- Multiple authors formatted correctly
- DOI link included when present
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
REAL_BIBLIOGRAPHY = REPO_ROOT / "docs" / "research" / "bibliography.yaml"

_MINIMAL_BIB = """\
- id: testarticle
  type: article
  title: "Test Article Title"
  authors:
    - "Alice A. Author"
    - "Bob B. Coauthor"
  year: 2024
  venue: "Journal of Testing"
  volume: 1
  issue: 2
  pages: "10-20"
  doi: "10.1234/test.2024"

- id: testbook
  type: book
  title: "Test Book Title"
  authors:
    - "Carol C. Writer"
  year: 2020
  publisher: "Test Press"
  address: "Boston, MA"

- id: testweb
  type: web
  title: "Test Web Resource"
  authors:
    - "Dave D. Blogger"
  year: 2023
  venue: "Blog"
  url: "https://example.com/post"
  retrieved: "2026-03-07"

- id: testreport
  type: techreport
  title: "Test Technical Report"
  authors:
    - "Eve E. Researcher"
  year: 2018
  venue: "Lab Tech Report TR-001"
  url: "https://example.com/tr"
"""


def write_bib(tmp_path: Path, content: str) -> Path:
    bib = tmp_path / "bibliography.yaml"
    bib.write_text(content, encoding="utf-8")
    return bib


def run_format(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/format_citations.py", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


class TestFormatCitationsHappyPath:
    def test_renders_full_list(self, tmp_path):
        bib = write_bib(tmp_path, _MINIMAL_BIB)
        result = run_format(["--bibliography", str(bib)])
        assert result.returncode == 0
        assert "## References" in result.stdout
        assert "[1]" in result.stdout
        assert "[2]" in result.stdout

    def test_article_format_includes_year_and_venue(self, tmp_path):
        bib = write_bib(tmp_path, _MINIMAL_BIB)
        result = run_format(["--bibliography", str(bib), "--key", "testarticle"])
        assert result.returncode == 0
        out = result.stdout
        assert "2024" in out
        assert "Journal of Testing" in out
        assert "Test Article Title" in out

    def test_article_includes_doi(self, tmp_path):
        bib = write_bib(tmp_path, _MINIMAL_BIB)
        result = run_format(["--bibliography", str(bib), "--key", "testarticle"])
        assert "doi.org/10.1234/test.2024" in result.stdout

    def test_book_format_includes_publisher(self, tmp_path):
        bib = write_bib(tmp_path, _MINIMAL_BIB)
        result = run_format(["--bibliography", str(bib), "--key", "testbook"])
        assert "Test Press" in result.stdout
        assert "Boston, MA" in result.stdout

    def test_web_format_includes_url(self, tmp_path):
        bib = write_bib(tmp_path, _MINIMAL_BIB)
        result = run_format(["--bibliography", str(bib), "--key", "testweb"])
        assert "https://example.com/post" in result.stdout
        assert "Retrieved 2026-03-07" in result.stdout

    def test_techreport_format(self, tmp_path):
        bib = write_bib(tmp_path, _MINIMAL_BIB)
        result = run_format(["--bibliography", str(bib), "--key", "testreport"])
        assert "TR-001" in result.stdout
        assert "https://example.com/tr" in result.stdout

    def test_multiple_authors_formatted(self, tmp_path):
        bib = write_bib(tmp_path, _MINIMAL_BIB)
        result = run_format(["--bibliography", str(bib), "--key", "testarticle"])
        # Both authors should appear
        assert "Alice" in result.stdout
        assert "Bob" in result.stdout

    def test_inline_tag_format(self, tmp_path):
        bib = write_bib(tmp_path, _MINIMAL_BIB)
        result = run_format(["--bibliography", str(bib), "--inline", "testarticle"])
        assert result.returncode == 0
        out = result.stdout.strip()
        assert out.startswith("[")
        assert out.endswith("]")
        assert "2024" in out

    def test_list_shows_all_keys(self, tmp_path):
        bib = write_bib(tmp_path, _MINIMAL_BIB)
        result = run_format(["--bibliography", str(bib), "--list"])
        assert result.returncode == 0
        assert "testarticle" in result.stdout
        assert "testbook" in result.stdout
        assert "testweb" in result.stdout
        assert "testreport" in result.stdout

    @pytest.mark.io
    def test_renders_real_bibliography(self):
        """Smoke test: render the actual bibliography.yaml in the repo."""
        if not REAL_BIBLIOGRAPHY.exists():
            pytest.skip("bibliography.yaml not present")
        result = run_format(["--bibliography", str(REAL_BIBLIOGRAPHY)])
        assert result.returncode == 0
        assert "## References" in result.stdout


class TestFormatCitationsErrors:
    def test_exits_1_if_bibliography_not_found(self, tmp_path):
        result = run_format(["--bibliography", str(tmp_path / "nonexistent.yaml")])
        assert result.returncode == 1
        assert "not found" in result.stderr

    def test_exits_1_if_key_not_found(self, tmp_path):
        bib = write_bib(tmp_path, _MINIMAL_BIB)
        result = run_format(["--bibliography", str(bib), "--key", "nonexistent"])
        assert result.returncode == 1
        assert "not found" in result.stderr

    def test_exits_1_if_inline_key_not_found(self, tmp_path):
        bib = write_bib(tmp_path, _MINIMAL_BIB)
        result = run_format(["--bibliography", str(bib), "--inline", "missing"])
        assert result.returncode == 1
        assert "not found" in result.stderr
