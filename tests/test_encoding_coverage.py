"""tests/test_encoding_coverage.py

Tests for scripts/encoding_coverage.py — MANIFESTO F1-F4 encoding coverage.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = "scripts/encoding_coverage.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,  # repo root
    )


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


class TestHappyPath:
    def test_exits_zero_with_valid_inputs(self):
        result = _run("--manifesto", "MANIFESTO.md", "--agents", "AGENTS.md")
        assert result.returncode == 0, result.stderr

    def test_output_contains_table_header(self):
        result = _run("--manifesto", "MANIFESTO.md", "--agents", "AGENTS.md")
        assert "| Principle" in result.stdout
        assert "F1 Desc" in result.stdout
        assert "F4 Programmatic" in result.stdout

    def test_all_12_principles_present(self):
        result = _run("--manifesto", "MANIFESTO.md", "--agents", "AGENTS.md")
        expected = [
            "Endogenous-First",
            "Algorithms Before Tokens",
            "Local Compute-First",
            "Programmatic-First",
            "Documentation-First",
            "Adopt Over Author",
            "Self-Governance",
            "Compress Context",
            "Isolate Invocations",
            "Validate & Gate",
            "Minimal Posture",
            "Testing-First",
        ]
        for name in expected:
            assert name in result.stdout, f"Principle '{name}' missing from output"

    def test_score_column_format(self):
        """Every data row contains a score in N/4 format."""
        result = _run("--manifesto", "MANIFESTO.md", "--agents", "AGENTS.md")
        assert result.returncode == 0
        scores = re.findall(r"\d/4", result.stdout)
        # 12 principles → 12 score cells
        assert len(scores) >= 12, f"Expected ≥12 score cells, got {len(scores)}"

    def test_three_core_axioms_are_four_of_four(self):
        """Endogenous-First, ABT, and LCF are fully encoded (4/4)."""
        result = _run("--manifesto", "MANIFESTO.md", "--agents", "AGENTS.md")
        assert result.returncode == 0
        for axiom in ("Endogenous-First", "Algorithms Before Tokens", "Local Compute-First"):
            for line in result.stdout.splitlines():
                if axiom in line:
                    assert "4/4" in line, f"Expected '{axiom}' to score 4/4, got: {line.strip()}"
                    break
            else:
                pytest.fail(f"Row for '{axiom}' not found in output")

    def test_default_paths_used_when_no_args(self):
        """Default MANIFESTO.md and AGENTS.md are used when no --manifesto/--agents given."""
        result = _run()
        assert result.returncode == 0
        assert "Endogenous-First" in result.stdout

    def test_output_uses_tick_and_cross_symbols(self):
        result = _run("--manifesto", "MANIFESTO.md", "--agents", "AGENTS.md")
        assert "✓" in result.stdout
        assert "✗" in result.stdout


# ---------------------------------------------------------------------------
# Error-handling tests
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_missing_manifesto_exits_one(self, tmp_path: Path):
        result = _run(
            "--manifesto",
            str(tmp_path / "nonexistent.md"),
            "--agents",
            "AGENTS.md",
        )
        assert result.returncode == 1

    def test_missing_agents_exits_one(self, tmp_path: Path):
        result = _run(
            "--manifesto",
            "MANIFESTO.md",
            "--agents",
            str(tmp_path / "nonexistent.md"),
        )
        assert result.returncode == 1

    def test_missing_file_error_written_to_stderr(self, tmp_path: Path):
        result = _run(
            "--manifesto",
            str(tmp_path / "missing.md"),
            "--agents",
            "AGENTS.md",
        )
        assert "Error" in result.stderr or "not found" in result.stderr

    def test_both_missing_exits_one(self, tmp_path: Path):
        result = _run(
            "--manifesto",
            str(tmp_path / "a.md"),
            "--agents",
            str(tmp_path / "b.md"),
        )
        assert result.returncode == 1


# ---------------------------------------------------------------------------
# Unit tests for internal helpers (imported directly)
# ---------------------------------------------------------------------------


class TestExtractH3Section:
    def setup_method(self):
        from scripts.encoding_coverage import extract_h3_section

        self.extract = extract_h3_section

    def test_extracts_numbered_axiom_heading(self):
        text = "### 1. Endogenous-First\n\nSome body text here.\n\n### 2. Next\n"
        body = self.extract(text, "Endogenous-First")
        assert "Some body text here." in body
        assert "Next" not in body

    def test_extracts_with_parenthesised_suffix(self):
        text = "### Adopt Over Author (Avoid Reinventing the Wheel)\n\nBody here.\n### Next\n"
        body = self.extract(text, "Adopt Over Author")
        assert "Body here." in body

    def test_returns_empty_string_when_not_found(self):
        text = "### Some Other Section\n\nBody.\n"
        body = self.extract(text, "Does Not Exist")
        assert body == ""

    def test_terminates_at_h2_boundary(self):
        text = "### MyPrinciple\n\nSection body.\n\n## New Top-Level Section\n\nOther.\n"
        body = self.extract(text, "MyPrinciple")
        assert "Section body." in body
        assert "New Top-Level Section" not in body


class TestCheckCoverage:
    def setup_method(self):
        from scripts.encoding_coverage import check_coverage

        self.check = check_coverage

    def test_f2_detected_with_canonical_example_label(self):
        body = "Some description.\n\n**Canonical example**: Here is an example.\n"
        f1, f2, f3, f4 = self.check(body, "", "Principle X")
        assert f2 is True

    def test_f3_detected_with_anti_pattern_label(self):
        body = "Some description.\n\n**Anti-pattern**: Here is a bad practice.\n"
        _, _, f3, _ = self.check(body, "", "Principle X")
        assert f3 is True

    def test_f4_detected_with_programmatic_gate_label(self):
        body = "Some description.\n\n**Programmatic gate**: `scripts/my_script.py`.\n"
        _, _, _, f4 = self.check(body, "", "Principle X")
        assert f4 is True

    def test_f4_detected_via_agents_context(self):
        body = "Short description paragraph." + " x" * 20
        ctx = "Principle X is enforced via scripts/hook.py in CI."
        _, _, _, f4 = self.check(body, ctx, "Principle X")
        assert f4 is True

    def test_all_false_for_minimal_content(self):
        body = ""
        f1, f2, f3, f4 = self.check(body, "", "Unknown")
        assert f1 is False
        assert f2 is False
        assert f3 is False
        assert f4 is False
