"""
tests/test_query_docs.py

Unit and IO tests for scripts/query_docs.py — BM25 documentation corpus query CLI.

Coverage targets:
- chunk_markdown: empty, two-paragraph, short-excluded, code-fence, heading prefix
- build_corpus: unknown scope (KeyError), real file read
- run_query: empty corpus, synthetic corpus top-N
- format_output: text mode, json mode
- IO tests use @pytest.mark.io and operate on real repo files
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import query_docs as qd  # noqa: E402

# ---------------------------------------------------------------------------
# chunk_markdown
# ---------------------------------------------------------------------------


class TestChunkMarkdown:
    def test_empty_text_returns_empty(self):
        assert qd.chunk_markdown("", "f.md") == []

    def test_whitespace_only_returns_empty(self):
        assert qd.chunk_markdown("   \n\n  ", "f.md") == []

    def test_two_paragraphs_returns_two_chunks(self):
        text = "Para one has enough words here.\n\nPara two also has enough words."
        chunks = qd.chunk_markdown(text, "f.md")
        assert len(chunks) == 2
        # 1-indexed line numbers
        assert chunks[0]["start_line"] == 1
        assert chunks[0]["end_line"] == 1
        assert chunks[1]["start_line"] == 3
        assert chunks[1]["end_line"] == 3

    def test_chunk_three_words_or_fewer_excluded(self):
        # "one two" is 2 words — excluded; longer paragraph is included
        text = "one two\n\nThis paragraph has more than three words in it."
        chunks = qd.chunk_markdown(text, "f.md")
        assert len(chunks) == 1
        assert "more than three words" in chunks[0]["text"]

    def test_chunk_exactly_four_words_included(self):
        text = "one two three four"
        chunks = qd.chunk_markdown(text, "f.md")
        assert len(chunks) == 1

    def test_code_fence_is_single_chunk(self):
        text = "```python\nprint('hello world here')\nreturn value\n```"
        chunks = qd.chunk_markdown(text, "f.md")
        assert len(chunks) == 1
        assert "```" in chunks[0]["text"]

    def test_file_path_stored(self):
        text = "This paragraph has enough words to be included."
        chunks = qd.chunk_markdown(text, "docs/guides/testing.md")
        assert chunks[0]["file"] == "docs/guides/testing.md"

    def test_heading_prefix_applied_to_following_paragraph(self):
        text = "## My Section About Important Things\n\nContent paragraph with enough words."
        chunks = qd.chunk_markdown(text, "f.md")
        # At least one chunk should have the heading prefix
        assert any("[My Section About Important Things]" in c["text"] for c in chunks)

    def test_code_fence_line_numbers(self):
        text = "Intro paragraph with sufficient words here.\n\n```bash\necho hello world\n```"
        chunks = qd.chunk_markdown(text, "f.md")
        assert len(chunks) == 2
        # fence chunk starts at line 3 (1-indexed)
        fence_chunk = next(c for c in chunks if "```" in c["text"])
        assert fence_chunk["start_line"] == 3

    def test_multiline_paragraph_end_line(self):
        text = "Line one of paragraph.\nLine two of paragraph.\nLine three of paragraph."
        chunks = qd.chunk_markdown(text, "f.md")
        assert len(chunks) == 1
        assert chunks[0]["start_line"] == 1
        assert chunks[0]["end_line"] == 3


# ---------------------------------------------------------------------------
# build_corpus
# ---------------------------------------------------------------------------


class TestBuildCorpus:
    def test_unknown_scope_raises_key_error(self, tmp_path):
        with pytest.raises(KeyError, match="Unknown scope"):
            qd.build_corpus("nonexistent_scope", tmp_path)

    def test_missing_files_silently_skipped(self, tmp_path):
        # tmp_path has no MANIFESTO.md — should return empty corpus, not error
        result = qd.build_corpus("manifesto", tmp_path)
        assert result == []

    @pytest.mark.io
    def test_manifesto_scope_returns_chunks(self):
        repo_root = Path(__file__).parent.parent
        corpus = qd.build_corpus("manifesto", repo_root)
        assert len(corpus) > 0
        assert all(c["file"] == "MANIFESTO.md" for c in corpus)

    @pytest.mark.io
    def test_all_scope_returns_chunks_from_multiple_files(self):
        repo_root = Path(__file__).parent.parent
        corpus = qd.build_corpus("all", repo_root)
        files = {c["file"] for c in corpus}
        assert len(files) > 1

    @pytest.mark.io
    def test_toolchain_scope_returns_chunks(self):
        """Verify toolchain scope returns chunks from docs/toolchain/ directory."""
        repo_root = Path(__file__).parent.parent
        corpus = qd.build_corpus("toolchain", repo_root)
        assert len(corpus) > 0, "Should find toolchain files"
        # All chunks should be from toolchain docs
        for chunk in corpus:
            assert "toolchain" in chunk["file"].lower()

    @pytest.mark.io
    def test_skills_scope_returns_chunks(self):
        """Verify skills scope returns chunks from .github/skills/*/SKILL.md files."""
        repo_root = Path(__file__).parent.parent
        corpus = qd.build_corpus("skills", repo_root)
        assert len(corpus) > 0, "Should find skill files"
        # All chunks should be from SKILL.md files in .github/skills/
        for chunk in corpus:
            assert "skills" in chunk["file"].lower() and chunk["file"].endswith("SKILL.md")


# ---------------------------------------------------------------------------
# run_query
# ---------------------------------------------------------------------------


class TestRunQuery:
    def test_empty_corpus_returns_empty(self):
        assert qd.run_query("anything", [], 5) == []

    def test_top_n_limits_results(self):
        corpus = [
            {
                "text": f"chunk about topic {i} with enough content words",
                "file": "f.md",
                "start_line": i,
                "end_line": i,
            }
            for i in range(10)
        ]
        results = qd.run_query("chunk", corpus, 3)
        assert len(results) == 3

    def test_results_are_dicts_with_expected_keys(self):
        corpus = [
            {
                "text": "the endogenous first principle is foundational",
                "file": "MANIFESTO.md",
                "start_line": 1,
                "end_line": 1,
            }
        ]
        results = qd.run_query("endogenous", corpus, 5)
        assert len(results) == 1
        assert "text" in results[0]
        assert "file" in results[0]

    def test_top_n_larger_than_corpus_returns_all(self):
        corpus = [
            {
                "text": f"paragraph {i} with words",
                "file": "f.md",
                "start_line": i,
                "end_line": i,
            }
            for i in range(3)
        ]
        results = qd.run_query("paragraph", corpus, 10)
        assert len(results) == 3


# ---------------------------------------------------------------------------
# format_output
# ---------------------------------------------------------------------------


class TestFormatOutput:
    def test_text_mode_contains_file_header(self):
        results = [{"text": "hello world foo bar baz", "file": "f.md", "start_line": 1, "end_line": 3}]
        output = qd.format_output(results, "text")
        assert "f.md:1-3" in output

    def test_text_mode_contains_preview(self):
        results = [{"text": "hello world foo bar baz", "file": "f.md", "start_line": 1, "end_line": 1}]
        output = qd.format_output(results, "text")
        assert "hello world" in output

    def test_json_mode_parses_as_list(self):
        results = [{"text": "hello world foo bar baz", "file": "f.md", "start_line": 1, "end_line": 1}]
        output = qd.format_output(results, "json")
        data = json.loads(output)
        assert isinstance(data, list)
        assert data[0]["file"] == "f.md"

    def test_json_mode_empty_results(self):
        output = qd.format_output([], "json")
        data = json.loads(output)
        assert data == []

    def test_text_preview_truncated_at_200_chars(self):
        long_text = "x" * 300
        results = [{"text": long_text, "file": "f.md", "start_line": 1, "end_line": 1}]
        output = qd.format_output(results, "text")
        # Preview is at most 200 chars; header line adds extra chars
        preview_line = [ln for ln in output.splitlines() if "x" in ln][0]
        assert len(preview_line) <= 200


# ---------------------------------------------------------------------------
# IO tests — operate on real repo files
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_manifesto_query_returns_results():
    repo_root = Path(__file__).parent.parent
    corpus = qd.build_corpus("manifesto", repo_root)
    results = qd.run_query("endogenous first", corpus, 5)
    assert len(results) >= 1


@pytest.mark.io
def test_manifesto_query_json_parseable():
    repo_root = Path(__file__).parent.parent
    corpus = qd.build_corpus("manifesto", repo_root)
    results = qd.run_query("endogenous first", corpus, 5)
    output = qd.format_output(results, "json")
    data = json.loads(output)
    assert isinstance(data, list)
