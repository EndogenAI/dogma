"""Tests for validate_synthesis.check_axiom_citations.

Covers Issue #249: warn-only check for bare axiom names without MANIFESTO.md §-reference.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from validate_synthesis import check_axiom_citations  # noqa: E402


def test_bare_axiom_name_emits_warn(capsys: pytest.CaptureFixture[str]) -> None:
    """D4 line with bare axiom name (no §-ref) should print WARN and NOT raise SystemExit."""
    lines = ["The Endogenous-First principle drives this."]
    # Must not raise
    check_axiom_citations(lines, "docs/research/example.md")
    captured = capsys.readouterr()
    assert "WARN: bare axiom name without §-reference" in captured.out
    assert "line 1" in captured.out
    assert "docs/research/example.md" in captured.out


def test_axiom_with_section_ref_no_warn(capsys: pytest.CaptureFixture[str]) -> None:
    """D4 line with axiom name AND MANIFESTO.md §-ref should produce no WARN."""
    lines = ["The Endogenous-First axiom (MANIFESTO.md §1) applies here."]
    check_axiom_citations(lines, "docs/research/example.md")
    captured = capsys.readouterr()
    assert "WARN" not in captured.out


def test_algorithms_before_tokens_bare(capsys: pytest.CaptureFixture[str]) -> None:
    """Algorithms Before Tokens without §-ref should warn."""
    lines = ["Algorithms Before Tokens is applied here."]
    check_axiom_citations(lines, "docs/research/example.md")
    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "bare axiom name without §-reference" in captured.out
    assert "docs/research/example.md" in captured.out


def test_algorithms_before_tokens_with_ref_no_warn(capsys: pytest.CaptureFixture[str]) -> None:
    """Algorithms Before Tokens with §-ref should not warn."""
    lines = ["Algorithms Before Tokens (MANIFESTO.md §2) governs this."]
    check_axiom_citations(lines, "docs/research/example.md")
    captured = capsys.readouterr()
    assert "WARN" not in captured.out


def test_multiple_axioms_multiple_warns(capsys: pytest.CaptureFixture[str]) -> None:
    """Multiple bare axioms across lines should each emit a WARN."""
    lines = [
        "Endogenous-First is first.",
        "Algorithms Before Tokens is second.",
        "Local Compute-First is third.",
    ]
    check_axiom_citations(lines, "docs/research/example.md")
    captured = capsys.readouterr()
    assert captured.out.count("WARN") == 3


def test_no_axiom_names_no_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Lines with no axiom names should produce no output."""
    lines = ["This is a normal sentence with no special phrases."]
    check_axiom_citations(lines, "docs/research/example.md")
    captured = capsys.readouterr()
    assert captured.out == ""
