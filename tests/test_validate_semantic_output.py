"""
tests/test_validate_semantic_output.py
----------------------------------------
Tests for scripts/validate_semantic_output.py — L1 semantic output validator.

Covers:
- exit 0: valid bullets format within ceiling
- exit 0: valid table format within ceiling
- exit 0: valid single-line format within ceiling
- exit 1: prose text when bullets expected
- exit 1: prose text when single-line expected (multi-line prose)
- exit 2: text exceeds ceiling (85 words when ceiling=20)
- edge case: exactly at ceiling passes (exit 0)
- edge case: empty input returns exit 1
- token estimation helper
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loader
# ---------------------------------------------------------------------------


def _load_module(name: str, rel_path: str):
    repo_root = Path(__file__).parent.parent
    spec = importlib.util.spec_from_file_location(name, repo_root / rel_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def vso():
    return _load_module("validate_semantic_output", "scripts/validate_semantic_output.py")


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------


def test_estimate_tokens_basic(vso):
    """Token estimation returns a positive integer for non-empty text."""
    result = vso.estimate_tokens("hello world")
    assert isinstance(result, int)
    assert result > 0


def test_estimate_tokens_empty(vso):
    """Empty string returns 0 tokens."""
    assert vso.estimate_tokens("") == 0


def test_estimate_tokens_approximation(vso):
    """75-word text should yield ~100 tokens (ceil(75/0.75) = 100)."""
    # 75 words
    text = " ".join(["word"] * 75)
    result = vso.estimate_tokens(text)
    assert result == 100


# ---------------------------------------------------------------------------
# Format checks
# ---------------------------------------------------------------------------


def test_is_bullets_valid(vso):
    """Text with bullet lines is detected as bullets."""
    text = "- First item\n- Second item\n- Third item"
    assert vso.check_format(text, "bullets") is True


def test_is_bullets_asterisk_valid(vso):
    """Asterisk bullets are also accepted."""
    text = "* item one\n* item two"
    assert vso.check_format(text, "bullets") is True


def test_is_bullets_rejects_prose(vso):
    """Plain prose is not bullets."""
    text = "This is a paragraph without any bullet points whatsoever."
    assert vso.check_format(text, "bullets") is False


def test_is_table_valid(vso):
    """Markdown table with header and row passes."""
    text = "| Col A | Col B |\n|-------|-------|\n| val1  | val2  |"
    assert vso.check_format(text, "table") is True


def test_is_table_rejects_prose(vso):
    """Prose without table pipes fails table format."""
    text = "Some prose without any table formatting."
    assert vso.check_format(text, "table") is False


def test_is_single_line_valid(vso):
    """Single non-empty line passes."""
    text = "APPROVED"
    assert vso.check_format(text, "single-line") is True


def test_is_single_line_rejects_multiline(vso):
    """Multi-line text fails single-line format."""
    text = "Line one.\nLine two."
    assert vso.check_format(text, "single-line") is False


# ---------------------------------------------------------------------------
# validate() — exit 0
# ---------------------------------------------------------------------------


def test_validate_bullets_within_ceiling(vso, capsys):
    """Bullets format within ceiling exits 0."""
    text = "- item one\n- item two\n- item three"
    rc = vso.validate(text, "bullets", 50)
    assert rc == 0
    out = capsys.readouterr().out
    assert "OK" in out


def test_validate_table_within_ceiling(vso, capsys):
    """Table format within ceiling exits 0."""
    text = "| A | B |\n|---|---|\n| 1 | 2 |"
    rc = vso.validate(text, "table", 50)
    assert rc == 0


def test_validate_single_line_within_ceiling(vso, capsys):
    """Single-line format within ceiling exits 0."""
    rc = vso.validate("APPROVED", "single-line", 10)
    assert rc == 0


# ---------------------------------------------------------------------------
# validate() — exit 1 (format mismatch)
# ---------------------------------------------------------------------------


def test_validate_prose_when_bullets_expected(vso, capsys):
    """Prose text when bullets expected exits 1."""
    text = "This is a long prose response with no bullet points. The agent should have used bullets here."
    rc = vso.validate(text, "bullets", 200)
    assert rc == 1
    err = capsys.readouterr().err
    assert "FORMAT MISMATCH" in err


def test_validate_multiline_when_single_line_expected(vso, capsys):
    """Multi-line text when single-line expected exits 1."""
    text = "First line.\nSecond line."
    rc = vso.validate(text, "single-line", 100)
    assert rc == 1


# ---------------------------------------------------------------------------
# validate() — exit 2 (ceiling exceeded)
# ---------------------------------------------------------------------------


def test_validate_ceiling_exceeded_85_words(vso, capsys):
    """85-word text with ceiling=20 exits 2."""
    # 85 words → ceil(85/0.75) = 114 tokens > 20
    text = "- " + " ".join(["word"] * 84)
    rc = vso.validate(text, "bullets", 20)
    assert rc == 2
    err = capsys.readouterr().err
    assert "CEILING EXCEEDED" in err


def test_validate_exactly_at_ceiling_passes(vso, capsys):
    """Text exactly at ceiling exits 0."""
    # 3 words → ceil(3/0.75) = 4 tokens
    text = "- one two"  # 3 words; 1 bullet line
    rc = vso.validate(text, "bullets", 4)
    assert rc == 0


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


def test_cli_valid_bullets(vso, capsys):
    """CLI exits 0 for valid bullets within ceiling."""
    text = "- item a\n- item b"
    rc = vso.main(["--format", "bullets", "--ceiling", "50", text])
    assert rc == 0
    out = capsys.readouterr().out
    assert "OK" in out


def test_cli_format_mismatch(vso, capsys):
    """CLI exits 1 for format mismatch."""
    text = "This is plain prose not bullets."
    rc = vso.main(["--format", "bullets", "--ceiling", "200", text])
    assert rc == 1


def test_cli_ceiling_exceeded(vso, capsys):
    """CLI exits 2 for text exceeding ceiling."""
    # Generate 85-word bullet text
    text = "- " + " ".join(["word"] * 84)
    rc = vso.main(["--format", "bullets", "--ceiling", "20", text])
    assert rc == 2
