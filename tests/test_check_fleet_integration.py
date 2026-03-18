"""
test_check_fleet_integration.py — Tests for check_fleet_integration.py

Tests cover:
- Happy path: new agents/skills with proper references
- Error cases: new agents/skills missing from AGENTS.md
- File I/O: reading agent/skill frontmatter, parsing AGENTS.md
- Exit codes: 0 on success, 1 on gaps, 2 on I/O error
- Dry-run mode: preview warnings without side effects
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the module is imported for coverage tracking
import scripts.check_fleet_integration as check_fleet_integration_module  # noqa: F401
from scripts.check_fleet_integration import (
    _check_reference_in_agents,
    _find_agent_names,
    _find_skill_names,
    _git_diff_names,
    _read_agents_md,
    main,
)


@pytest.mark.io
class TestReadAgentsMd:
    """Test _read_agents_md()."""

    def test_read_agents_md_success(self, tmp_path):
        """Test successful read of AGENTS.md."""
        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("# AGENTS.md\n\nSome content", encoding="utf-8")
        with patch("scripts.check_fleet_integration._get_root", return_value=tmp_path):
            result = _read_agents_md(tmp_path)
        assert "Some content" in result

    def test_read_agents_md_missing(self, tmp_path):
        """Test read when AGENTS.md does not exist."""
        with patch("scripts.check_fleet_integration._get_root", return_value=tmp_path):
            result = _read_agents_md(tmp_path)
        assert result == ""

    def test_read_agents_md_io_error(self, tmp_path, mocker):
        """Test read with I/O error."""
        mocker.patch.object(Path, "read_text", side_effect=OSError("Permission denied"))
        result = _read_agents_md(tmp_path)
        assert result == ""


@pytest.mark.io
class TestFindAgentNames:
    """Test _find_agent_names()."""

    def test_find_agent_names_success(self, tmp_path):
        """Test extraction of agent name from frontmatter."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        agent_file = agents_dir / "test-agent.agent.md"
        agent_file.write_text(
            '---\nname: Test Agent\ndescription: "A test"\ntools: [search, read]\n---\n# Agent',
            encoding="utf-8",
        )
        with patch("scripts.check_fleet_integration._get_root", return_value=tmp_path):
            names = _find_agent_names(".github/agents/test-agent.agent.md", tmp_path)
        assert names == ["Test Agent"]

    def test_find_agent_names_quoted(self, tmp_path):
        """Test extraction with quoted name."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        agent_file = agents_dir / "test-agent.agent.md"
        agent_file.write_text(
            '---\nname: "Quoted Agent"\n---\n# Agent',
            encoding="utf-8",
        )
        with patch("scripts.check_fleet_integration._get_root", return_value=tmp_path):
            names = _find_agent_names(".github/agents/test-agent.agent.md", tmp_path)
        assert names == ["Quoted Agent"]

    def test_find_agent_names_missing_file(self, tmp_path):
        """Test with missing agent file — returns None (I/O error)."""
        with patch("scripts.check_fleet_integration._get_root", return_value=tmp_path):
            names = _find_agent_names(".github/agents/nonexistent.agent.md", tmp_path)
        assert names is None

    def test_find_agent_names_no_frontmatter(self, tmp_path):
        """Test with file missing frontmatter."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        agent_file = agents_dir / "test-agent.agent.md"
        agent_file.write_text("# Just a heading\nNo frontmatter here", encoding="utf-8")
        with patch("scripts.check_fleet_integration._get_root", return_value=tmp_path):
            names = _find_agent_names(".github/agents/test-agent.agent.md", tmp_path)
        assert names == []


@pytest.mark.io
class TestFindSkillNames:
    """Test _find_skill_names()."""

    def test_find_skill_names_success(self, tmp_path):
        """Test extraction of skill name from frontmatter."""
        skills_dir = tmp_path / ".github" / "skills" / "test-skill"
        skills_dir.mkdir(parents=True)
        skill_file = skills_dir / "SKILL.md"
        skill_file.write_text(
            '---\nname: test-skill\ndescription: "A test skill"\n---\n# Skill',
            encoding="utf-8",
        )
        with patch("scripts.check_fleet_integration._get_root", return_value=tmp_path):
            names = _find_skill_names(".github/skills/test-skill/SKILL.md", tmp_path)
        assert names == ["test-skill"]

    def test_find_skill_names_missing_file(self, tmp_path):
        """Test with missing skill file — returns None (I/O error)."""
        with patch("scripts.check_fleet_integration._get_root", return_value=tmp_path):
            names = _find_skill_names(".github/skills/nonexistent/SKILL.md", tmp_path)
        assert names is None


class TestCheckReferenceInAgents:
    """Test _check_reference_in_agents()."""

    def test_reference_backtick(self):
        """Test detection of backtick-quoted reference."""
        name = "Test Agent"
        agents_md = "## Agents\n\nThe `Test Agent` performs validation."
        assert _check_reference_in_agents(name, agents_md) is True

    def test_reference_bold(self):
        """Test detection of bold reference."""
        name = "Review"
        agents_md = "Key agents: **Review** validates changes."
        assert _check_reference_in_agents(name, agents_md) is True

    def test_reference_italic(self):
        """Test detection of italic reference."""
        name = "GitHub Agent"
        agents_md = "Use the *GitHub Agent* for commits."
        assert _check_reference_in_agents(name, agents_md) is True

    def test_reference_quoted(self):
        """Test detection of double-quoted reference."""
        name = "Executive Docs"
        agents_md = 'The "Executive Docs" agent maintains documentation.'
        assert _check_reference_in_agents(name, agents_md) is True

    def test_reference_not_found(self):
        """Test when reference is not found."""
        name = "Nonexistent Agent"
        agents_md = "## Agents\n\nThe **Review** agent validates changes."
        assert _check_reference_in_agents(name, agents_md) is False

    def test_reference_empty_name(self):
        """Test with empty name."""
        name = ""
        agents_md = "## Agents\n\nContent here."
        assert _check_reference_in_agents(name, agents_md) is False

    def test_reference_special_chars(self):
        """Test with special regex characters in name."""
        name = "Agent++ Validator"
        agents_md = "The `Agent++ Validator` checks code."
        assert _check_reference_in_agents(name, agents_md) is True


class TestGitDiffNames:
    """Test _git_diff_names()."""

    def test_git_diff_names_success(self, mocker):
        """Test successful git diff parsing."""
        output = ".github/agents/new-agent.agent.md\n.github/skills/new-skill/SKILL.md\n"
        mocker.patch("subprocess.run", return_value=MagicMock(returncode=0, stdout=output))
        result = _git_diff_names("main")
        assert ".github/agents/new-agent.agent.md" in result
        assert ".github/skills/new-skill/SKILL.md" in result

    def test_git_diff_names_no_new_files(self, mocker):
        """Test when git diff has no output."""
        mocker.patch("subprocess.run", return_value=MagicMock(returncode=0, stdout=""))
        result = _git_diff_names("main")
        assert result == []

    def test_git_diff_names_git_error(self, mocker):
        """Test when git command fails — returns None to distinguish from empty diff."""
        mocker.patch("subprocess.run", return_value=MagicMock(returncode=1, stdout="", stderr="fatal: not a git repo"))
        result = _git_diff_names("main")
        assert result is None

    def test_git_diff_names_git_timeout(self, mocker):
        """Test when git command times out — returns None."""
        mocker.patch("subprocess.run", side_effect=subprocess.TimeoutExpired("git", 10))
        result = _git_diff_names("main")
        assert result is None

    def test_git_diff_names_strips_origin_prefix(self, mocker):
        """Test that user-supplied origin/ prefix is stripped to avoid doubling."""
        output = ".github/agents/new-agent.agent.md\n"
        mock_run = mocker.patch("subprocess.run", return_value=MagicMock(returncode=0, stdout=output))
        _git_diff_names("origin/main")
        called_args = mock_run.call_args[0][0]
        assert "origin/origin/main" not in " ".join(called_args)
        assert "origin/main...HEAD" in " ".join(called_args)


@pytest.mark.io
class TestMain:
    """Test main() entry point."""

    def test_main_git_error_returns_exit_2(self, mocker, capsys):
        """Test main returns exit code 2 when git diff fails (None return)."""
        mocker.patch(
            "scripts.check_fleet_integration._git_diff_names",
            return_value=None,
        )
        mocker.patch.object(sys, "argv", ["check_fleet_integration.py"])
        exit_code = main()
        captured = capsys.readouterr()
        assert exit_code == 2
        assert "Could not determine new files from git" in captured.err

    def test_main_no_new_files(self, mocker, capsys):
        """Test main with no new files."""
        mocker.patch("scripts.check_fleet_integration._git_diff_names", return_value=[])
        mocker.patch.object(sys, "argv", ["check_fleet_integration.py"])
        exit_code = main()
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "No new files detected" in captured.out

    def test_main_success_with_referenced_agent(self, tmp_path, mocker, capsys):
        """Test main with new agent properly referenced."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        agent_file = agents_dir / "new-agent.agent.md"
        agent_file.write_text('---\nname: "New Agent"\n---\n', encoding="utf-8")

        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("## Agents\n\nThe **New Agent** does validation.", encoding="utf-8")

        mocker.patch(
            "scripts.check_fleet_integration._git_diff_names",
            return_value=[".github/agents/new-agent.agent.md"],
        )
        mocker.patch("scripts.check_fleet_integration._get_root", return_value=tmp_path)
        mocker.patch.object(sys, "argv", ["check_fleet_integration.py"])

        exit_code = main()
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "Referenced Entities" in captured.out or "✅" in captured.out

    def test_main_gap_with_unreferenced_agent(self, tmp_path, mocker, capsys):
        """Test main with new agent not referenced."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        agent_file = agents_dir / "new-agent.agent.md"
        agent_file.write_text('---\nname: "Not Referenced Agent"\n---\n', encoding="utf-8")

        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("## Agents\n\nSome content.", encoding="utf-8")

        mocker.patch(
            "scripts.check_fleet_integration._git_diff_names",
            return_value=[".github/agents/new-agent.agent.md"],
        )
        mocker.patch("scripts.check_fleet_integration._get_root", return_value=tmp_path)
        mocker.patch.object(sys, "argv", ["check_fleet_integration.py"])

        exit_code = main()
        captured = capsys.readouterr()
        assert exit_code == 1
        assert "Integration Gaps" in captured.out or "⚠️" in captured.out

    def test_main_dry_run(self, tmp_path, mocker, capsys):
        """Test main with dry-run flag."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        agent_file = agents_dir / "new-agent.agent.md"
        agent_file.write_text('---\nname: "Missing Agent"\n---\n', encoding="utf-8")

        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("## Agents\n\nNo references.", encoding="utf-8")

        mocker.patch(
            "scripts.check_fleet_integration._git_diff_names",
            return_value=[".github/agents/new-agent.agent.md"],
        )
        mocker.patch("scripts.check_fleet_integration._get_root", return_value=tmp_path)
        mocker.patch.object(sys, "argv", ["check_fleet_integration.py", "--dry-run"])

        exit_code = main()
        captured = capsys.readouterr()
        assert exit_code == 1
        assert "Dry-run mode" in captured.out

    def test_main_invalid_branch(self, mocker, capsys):
        """Test main with empty branch argument."""
        mocker.patch.object(sys, "argv", ["check_fleet_integration.py", "--branch", ""])
        exit_code = main()
        captured = capsys.readouterr()
        assert exit_code == 1
        assert "branch must not be empty" in captured.err

    def test_main_agents_md_read_error(self, mocker, capsys):
        """Test main when AGENTS.md cannot be read."""
        mocker.patch(
            "scripts.check_fleet_integration._git_diff_names",
            return_value=[".github/agents/new-agent.agent.md"],
        )
        mocker.patch("scripts.check_fleet_integration._read_agents_md", return_value="")
        mocker.patch.object(sys, "argv", ["check_fleet_integration.py"])

        exit_code = main()
        captured = capsys.readouterr()
        assert exit_code == 2
        assert "Could not read AGENTS.md" in captured.err
