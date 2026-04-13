"""Tests for scripts/query_sessions.py"""

import json

# Import the script module
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import query_sessions


@pytest.mark.io
def test_collect_session_files_all_branches(tmp_path):
    """Test collecting session files from all branches."""
    # Create mock structure
    tmp_dir = tmp_path / ".tmp"
    branch1 = tmp_dir / "main"
    branch2 = tmp_dir / "feat-test"
    branch1.mkdir(parents=True)
    branch2.mkdir(parents=True)

    # Create session files
    (branch1 / "2026-04-01.md").write_text("# Session 1")
    (branch1 / "2026-04-02.md").write_text("# Session 2")
    (branch1 / "_index.md").write_text("# Index")
    (branch2 / "2026-04-03.md").write_text("# Session 3")

    # Create pyproject.toml to mark repo root
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")

    with patch("query_sessions.find_repo_root", return_value=tmp_path):
        files = query_sessions.collect_session_files(tmp_path, "all")

    assert len(files) == 3
    assert all(f.name != "_index.md" for f in files)


@pytest.mark.io
def test_collect_session_files_specific_branch(tmp_path):
    """Test collecting session files from a specific branch."""
    tmp_dir = tmp_path / ".tmp"
    branch1 = tmp_dir / "main"
    branch2 = tmp_dir / "feat-test"
    branch1.mkdir(parents=True)
    branch2.mkdir(parents=True)

    (branch1 / "2026-04-01.md").write_text("# Session 1")
    (branch2 / "2026-04-03.md").write_text("# Session 3")

    files = query_sessions.collect_session_files(tmp_path, "main")

    assert len(files) == 1
    assert files[0].parent.name == "main"


@pytest.mark.io
def test_collect_session_files_no_tmp_dir(tmp_path):
    """Test collecting session files when .tmp doesn't exist."""
    files = query_sessions.collect_session_files(tmp_path, "all")
    assert files == []


def test_chunk_markdown_basic():
    """Test basic markdown chunking."""
    text = """## Heading One

Paragraph one with some content here.

Paragraph two with more content.

## Heading Two

Final paragraph with sufficient content.
"""
    chunks = query_sessions.chunk_markdown(text, ".tmp/main/2026-04-01.md")

    assert len(chunks) >= 3
    assert all("text" in c for c in chunks)
    assert all("start_line" in c for c in chunks)
    assert all("end_line" in c for c in chunks)
    assert all("branch" in c for c in chunks)
    assert chunks[0]["branch"] == "main"


def test_chunk_markdown_with_code_fence():
    """Test chunking preserves code fences as atomic units."""
    text = """## Code Example

Some text before.

```python
def hello():
    return "world"
```

Text after.
"""
    chunks = query_sessions.chunk_markdown(text, ".tmp/feat-test/2026-04-01.md")

    # Check that fence appears as a single chunk
    fence_chunks = [c for c in chunks if "```" in c["text"]]
    assert len(fence_chunks) >= 1


def test_chunk_markdown_skips_trivial():
    """Test that chunks with ≤3 words are skipped."""
    text = """## Heading

Hi there.

This is a longer paragraph with more than three words.
"""
    chunks = query_sessions.chunk_markdown(text, ".tmp/main/2026-04-01.md")

    # "Hi there." should be skipped (2 words)
    assert all(len(c["text"].split()) > 3 for c in chunks)


def test_chunk_markdown_empty():
    """Test chunking empty text returns empty list."""
    chunks = query_sessions.chunk_markdown("", ".tmp/main/2026-04-01.md")
    assert chunks == []


def test_search_sessions_returns_results():
    """Test that search returns scored results."""
    from rank_bm25 import BM25Okapi

    chunks = [
        {"text": "memory governance session", "file": "test1.md", "start_line": 1, "end_line": 1},
        {"text": "something else entirely", "file": "test2.md", "start_line": 1, "end_line": 1},
        {"text": "memory and governance discussion", "file": "test3.md", "start_line": 1, "end_line": 1},
    ]

    tokenized = [c["text"].lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized)

    results = query_sessions.search_sessions("memory governance", bm25, chunks, top_n=2)

    assert len(results) <= 2
    assert all("memory" in r["text"].lower() or "governance" in r["text"].lower() for r in results)


def test_search_sessions_empty_chunks():
    """Test search with no chunks returns empty list."""
    from rank_bm25 import BM25Okapi

    bm25 = BM25Okapi([[""]])
    results = query_sessions.search_sessions("test", bm25, [], top_n=5)

    assert results == []


def test_format_text_with_results():
    """Test text formatting of results."""
    results = [
        {
            "text": "This is a test chunk with some content",
            "file": ".tmp/main/2026-04-01.md",
            "start_line": 10,
            "end_line": 12,
        }
    ]

    output = query_sessions.format_text(results)

    assert ".tmp/main/2026-04-01.md:10-12" in output
    assert "This is a test chunk" in output


def test_format_text_no_results():
    """Test text formatting with no results."""
    output = query_sessions.format_text([])
    assert "No results found" in output


def test_format_json():
    """Test JSON formatting."""
    results = [{"text": "Test content", "file": "test.md", "start_line": 1, "end_line": 2, "branch": "main"}]

    output = query_sessions.format_json(results)
    parsed = json.loads(output)

    assert len(parsed) == 1
    assert parsed[0]["text"] == "Test content"


@pytest.mark.io
def test_main_success(tmp_path, capsys):
    """Test main function success path."""
    # Setup
    tmp_dir = tmp_path / ".tmp"
    branch = tmp_dir / "main"
    branch.mkdir(parents=True)
    # Create content with multiple paragraphs (>3 words each) to ensure chunks are created
    session_content = """## Test Session

This is test content for searching with plenty of words.

Additional paragraph with test keyword and more substantial content here.

Final section containing enough words to pass the chunking threshold.
"""
    (branch / "2026-04-01.md").write_text(session_content)
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")

    with patch("query_sessions.find_repo_root", return_value=tmp_path):
        with patch("sys.argv", ["query_sessions.py", "test", "--branch", "all"]):
            exit_code = query_sessions.main()

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "test" in captured.out.lower()


@pytest.mark.io
def test_main_no_session_files(tmp_path, capsys):
    """Test main function when no session files exist."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")

    with patch("query_sessions.find_repo_root", return_value=tmp_path):
        with patch("sys.argv", ["query_sessions.py", "test", "--branch", "nonexistent"]):
            exit_code = query_sessions.main()

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "No session files found" in captured.err


@pytest.mark.io
def test_main_json_output(tmp_path, capsys):
    """Test main function with JSON output."""
    tmp_dir = tmp_path / ".tmp"
    branch = tmp_dir / "main"
    branch.mkdir(parents=True)
    # Create content with multiple paragraphs to ensure chunks are created
    session_content = """## Test Session

JSON output test content with plenty of words for chunking.

Another paragraph with the test keyword and sufficient length.
"""
    (branch / "2026-04-01.md").write_text(session_content)
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")

    with patch("query_sessions.find_repo_root", return_value=tmp_path):
        with patch("sys.argv", ["query_sessions.py", "test", "--output", "json"]):
            exit_code = query_sessions.main()

    assert exit_code == 0
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert isinstance(parsed, list)
