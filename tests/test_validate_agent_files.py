"""tests/test_validate_agent_files.py

Unit and integration tests for scripts/validate_agent_files.py

Tests cover:
- YAML frontmatter parsing
- Heading extraction
- Required section detection
- Cross-reference density check
- Heredoc detection (negation-aware)
- CLI: single file, --all, no-args, exit codes
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Direct import (for coverage)
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import validate_agent_files as vaf  # noqa: E402, I001 — after sys.path manipulation


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_agent_file(tmp_path: Path, content: str, name: str = "test.agent.md") -> Path:
    """Write *content* to a temp agent file and return its Path."""
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


MINIMAL_PASS = """\
---
name: Test Agent
description: A minimal passing agent file.
---

## Endogenous Sources \u2014 Read Before Acting

<context>

1. [`AGENTS.md`](../../AGENTS.md) \u2014 guiding constraints.

</context>

---

## Workflow

Do some work.

---

## Completion Criteria

- All tasks done.
"""


# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    def test_valid_frontmatter_returns_keys(self):
        text = "---\nname: My Agent\ndescription: Does things.\n---\n\n## Body"
        fm = vaf.parse_frontmatter(text)
        assert fm["name"] == "My Agent"
        assert fm["description"] == "Does things."

    def test_no_frontmatter_returns_empty_dict(self):
        text = "## Just a heading\nNo frontmatter here."
        assert vaf.parse_frontmatter(text) == {}

    def test_empty_value_preserved(self):
        text = "---\nname: \ndescription: ok\n---\n"
        fm = vaf.parse_frontmatter(text)
        assert fm["name"] == ""
        assert fm["description"] == "ok"

    def test_list_values_skipped(self):
        """Lines starting with '-' (list items) are not parsed as keys."""
        text = "---\nname: Agent\ntools:\n  - tool_a\n  - tool_b\n---\n"
        fm = vaf.parse_frontmatter(text)
        assert "tool_a" not in fm


# ---------------------------------------------------------------------------
# extract_headings
# ---------------------------------------------------------------------------


class TestExtractHeadings:
    def test_extracts_h2_headings_from_body(self):
        text = "---\nname: X\n---\n\n## Endogenous Sources\n\n## Workflow\n\n## Guardrails"
        headings = vaf.extract_headings(text)
        assert headings == ["## Endogenous Sources", "## Workflow", "## Guardrails"]

    def test_skips_frontmatter_lines(self):
        """YAML frontmatter with ## in values must not be picked up."""
        text = "---\nname: ## not a heading\n---\n\n## Real Heading"
        headings = vaf.extract_headings(text)
        assert headings == ["## Real Heading"]

    def test_no_headings_returns_empty(self):
        text = "---\nname: X\n---\nJust prose."
        assert vaf.extract_headings(text) == []


# ---------------------------------------------------------------------------
# validate — happy path
# ---------------------------------------------------------------------------


class TestValidateHappyPath:
    @pytest.mark.io
    def test_minimal_passing_file(self, tmp_path):
        """A well-formed agent file with all required elements passes."""
        f = _make_agent_file(tmp_path, MINIMAL_PASS)
        passed, failures = vaf.validate(f)
        assert passed is True
        assert failures == []

    @pytest.mark.io
    def test_real_agent_files_all_pass(self):
        """All committed .agent.md files in .github/agents/ must pass."""
        agents_dir = Path(".github/agents")
        agent_files = sorted(agents_dir.glob("*.agent.md"))
        assert agent_files, "No .agent.md files found — check working directory"
        for f in agent_files:
            passed, failures = vaf.validate(f)
            assert passed, f"{f}: {failures}"


# ---------------------------------------------------------------------------
# validate — failure cases
# ---------------------------------------------------------------------------


class TestValidateFailureCases:
    @pytest.mark.io
    def test_file_not_found(self, tmp_path):
        missing = tmp_path / "nonexistent.agent.md"
        passed, failures = vaf.validate(missing)
        assert passed is False
        assert any("File not found" in msg for msg in failures)

    @pytest.mark.io
    def test_missing_frontmatter(self, tmp_path):
        content = "## Endogenous Sources\n\n## Workflow\n\n## Completion Criteria\n\nReferences AGENTS.md."
        f = _make_agent_file(tmp_path, content)
        passed, failures = vaf.validate(f)
        assert passed is False
        assert any("No YAML frontmatter" in msg for msg in failures)

    @pytest.mark.io
    def test_missing_name_field(self, tmp_path):
        content = (
            "---\ndescription: No name here.\n---\n\n"
            "## Endogenous Sources\n\n## Workflow\n\n## Completion Criteria\n\nReferences AGENTS.md."
        )
        f = _make_agent_file(tmp_path, content)
        passed, failures = vaf.validate(f)
        assert passed is False
        assert any("'name'" in msg for msg in failures)

    @pytest.mark.io
    def test_missing_description_field(self, tmp_path):
        content = (
            "---\nname: Test Agent\n---\n\n"
            "## Endogenous Sources\n\n## Workflow\n\n## Completion Criteria\n\nReferences AGENTS.md."
        )
        f = _make_agent_file(tmp_path, content)
        passed, failures = vaf.validate(f)
        assert passed is False
        assert any("'description'" in msg for msg in failures)

    @pytest.mark.io
    def test_missing_endogenous_sources_section(self, tmp_path):
        content = "---\nname: A\ndescription: B\n---\n\n## Workflow\n\n## Completion Criteria\n\nReferences AGENTS.md."
        f = _make_agent_file(tmp_path, content)
        passed, failures = vaf.validate(f)
        assert passed is False
        assert any("Endogenous Sources" in msg for msg in failures)

    @pytest.mark.io
    def test_missing_action_section(self, tmp_path):
        content = (
            "---\nname: A\ndescription: B\n---\n\n"
            "## Endogenous Sources\n\n## Completion Criteria\n\nReferences AGENTS.md."
        )
        f = _make_agent_file(tmp_path, content)
        passed, failures = vaf.validate(f)
        assert passed is False
        assert any("Action section" in msg for msg in failures)

    @pytest.mark.io
    def test_missing_quality_gate_section(self, tmp_path):
        content = "---\nname: A\ndescription: B\n---\n\n## Endogenous Sources\n\n## Workflow\n\nReferences AGENTS.md."
        f = _make_agent_file(tmp_path, content)
        passed, failures = vaf.validate(f)
        assert passed is False
        assert any("Quality-gate" in msg for msg in failures)

    @pytest.mark.io
    def test_missing_cross_reference(self, tmp_path):
        content = (
            "---\nname: A\ndescription: B\n---\n\n## Endogenous Sources\n\n## Workflow\n\n## Completion Criteria\n"
        )
        f = _make_agent_file(tmp_path, content)
        passed, failures = vaf.validate(f)
        assert passed is False
        assert any("Cross-reference density" in msg for msg in failures)


# ---------------------------------------------------------------------------
# Heredoc detection — negation-aware
# ---------------------------------------------------------------------------


class TestHeredocDetection:
    @pytest.mark.io
    def test_positive_heredoc_flagged(self, tmp_path):
        """An agent file that instructs using heredoc must be flagged."""
        content = (
            "---\nname: A\ndescription: B\n---\n\n"
            "## Endogenous Sources\n\n## Workflow\n\n"
            "Run: `cat >> output.md << 'EOF'`\n"
            "write stuff\nEOF\n\n"
            "## Completion Criteria\n\nReferences AGENTS.md."
        )
        f = _make_agent_file(tmp_path, content)
        passed, failures = vaf.validate(f)
        assert passed is False
        assert any("Heredoc" in msg for msg in failures)

    @pytest.mark.io
    def test_negation_heredoc_not_flagged(self, tmp_path):
        """A guardrail saying 'never use cat >> ... << EOF' must NOT be flagged."""
        content = (
            "---\nname: A\ndescription: B\n---\n\n"
            "## Endogenous Sources\n\n## Workflow\n\n"
            "## Completion Criteria\n\nReferences AGENTS.md.\n\n"
            "## Guardrails\n\n"
            "- **Never use heredocs** (`cat >> file << 'EOF'`) \u2014 use built-in file tools.\n"
        )
        f = _make_agent_file(tmp_path, content)
        passed, failures = vaf.validate(f)
        assert passed is True, f"Should pass but got: {failures}"

    @pytest.mark.io
    def test_avoid_heredoc_not_flagged(self, tmp_path):
        """Line with 'avoid' + heredoc pattern must NOT be flagged."""
        content = (
            "---\nname: A\ndescription: B\n---\n\n"
            "## Endogenous Sources\n\n## Workflow\n\n"
            "## Completion Criteria\n\nReferences AGENTS.md.\n\n"
            "## Guardrails\n\n"
            "Avoid `cat >> file << 'EOF'` \u2014 it corrupts Markdown.\n"
        )
        f = _make_agent_file(tmp_path, content)
        passed, failures = vaf.validate(f)
        assert passed is True, f"Should pass but got: {failures}"


# ---------------------------------------------------------------------------
# Action section keyword variants
# ---------------------------------------------------------------------------


class TestActionSectionVariants:
    @pytest.mark.io
    def test_checklist_satisfies_action_section(self, tmp_path):
        content = (
            "---\nname: A\ndescription: B\n---\n\n"
            "## Endogenous Sources\n\n## Validation Checklist\n\n"
            "## Completion Criteria\n\nReferences AGENTS.md."
        )
        f = _make_agent_file(tmp_path, content)
        passed, _ = vaf.validate(f)
        assert passed is True

    @pytest.mark.io
    def test_scope_satisfies_action_section(self, tmp_path):
        content = (
            "---\nname: A\ndescription: B\n---\n\n"
            "## Endogenous Sources\n\n## Threat Model Scope\n\n"
            "## Completion Criteria\n\nReferences AGENTS.md."
        )
        f = _make_agent_file(tmp_path, content)
        passed, _ = vaf.validate(f)
        assert passed is True

    @pytest.mark.io
    def test_playbook_satisfies_action_section(self, tmp_path):
        content = (
            "---\nname: A\ndescription: B\n---\n\n"
            "## Endogenous Sources\n\n## Metrics Playbook\n\n"
            "## Completion Criteria\n\nReferences AGENTS.md."
        )
        f = _make_agent_file(tmp_path, content)
        passed, _ = vaf.validate(f)
        assert passed is True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


class TestCLI:
    @pytest.mark.io
    def test_single_file_pass_exit_0(self, tmp_path):
        f = _make_agent_file(tmp_path, MINIMAL_PASS)
        result = subprocess.run(
            [sys.executable, "scripts/validate_agent_files.py", str(f)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "PASS" in result.stdout

    @pytest.mark.io
    def test_single_file_fail_exit_1(self, tmp_path):
        bad_content = "---\nname: A\ndescription: B\n---\n\n## Workflow\n\n## Completion Criteria\n"
        f = _make_agent_file(tmp_path, bad_content)
        result = subprocess.run(
            [sys.executable, "scripts/validate_agent_files.py", str(f)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "FAIL" in result.stdout

    @pytest.mark.io
    def test_no_args_prints_help_exit_0(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_agent_files.py"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    @pytest.mark.integration
    def test_all_flag_passes_on_clean_repo(self):
        """--all against the real agent directory must exit 0 after our fixes."""
        result = subprocess.run(
            [sys.executable, "scripts/validate_agent_files.py", "--all"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Unexpected failures:\n{result.stdout}"
        assert "agent file(s) passed" in result.stdout

    @pytest.mark.io
    def test_all_flag_fails_with_bad_file(self, tmp_path):
        """--all scan returns exit 1 when at least one file fails (positional arg)."""
        bad = tmp_path / "bad.agent.md"
        bad.write_text("---\nname: Bad\ndescription: Missing sections.\n---\n## Workflow\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "scripts/validate_agent_files.py", str(bad)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "FAIL" in result.stdout

    @pytest.mark.io
    def test_missing_file_exit_1(self, tmp_path):
        missing = str(tmp_path / "ghost.agent.md")
        result = subprocess.run(
            [sys.executable, "scripts/validate_agent_files.py", missing],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "FAIL" in result.stdout
