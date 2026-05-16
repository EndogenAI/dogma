"""
tests/test_scaffold_agent.py

Unit and integration tests for scripts/scaffold_agent.py

Tests cover:
- Agent file generation with valid args
- Frontmatter schema validation
- Tool selection by posture
- Slug generation from name
- File naming and path resolution
- Dry-run functionality
- Conflict detection (file already exists)
"""

import subprocess
import sys
from unittest.mock import patch

import pytest

# Import business logic functions directly
from scripts.scaffold_agent import (
    build_tools_yaml,
    infer_executive,
    slugify,
    validate_name_unique,
)


class TestMain:
    """Unit tests for main() CLI function."""

    def test_main_missing_required_args(self, monkeypatch):
        """Test main() exits 2 when required args missing."""
        monkeypatch.setattr("sys.argv", ["scaffold_agent.py"])

        from scripts.scaffold_agent import main

        with pytest.raises(SystemExit) as excinfo:
            main()
        # argparse exits with 2 for missing required args
        assert excinfo.value.code == 2

    def test_main_description_too_long(self, monkeypatch):
        """Test main() exits 1 when description > 200 chars."""
        long_desc = "A" * 201
        monkeypatch.setattr("sys.argv", ["scaffold_agent.py", "--name", "Test", "--description", long_desc])

        from scripts.scaffold_agent import main

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

    def test_main_dry_run_success(self, monkeypatch, capsys):
        """Test main() with --dry-run prints without writing."""
        monkeypatch.setattr(
            "sys.argv", ["scaffold_agent.py", "--name", "Test Agent", "--description", "Test description", "--dry-run"]
        )

        from scripts.scaffold_agent import main

        main()  # Should not raise
        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out


class TestSlugify:
    """Tests for slugify() function."""

    def test_basic_slugification(self):
        """Display name is converted to lowercase-kebab-case."""
        assert slugify("Research Foo") == "research-foo"
        assert slugify("Executive Agent") == "executive-agent"

    def test_special_characters_removed(self):
        """Special characters are replaced with hyphens."""
        assert slugify("Test & Agent") == "test-agent"
        assert slugify("Agent (Beta)") == "agent-beta"

    def test_multiple_spaces_collapsed(self):
        """Multiple spaces collapse to single hyphen."""
        assert slugify("Research   Foo") == "research-foo"

    def test_leading_trailing_hyphens_stripped(self):
        """Leading and trailing hyphens are removed."""
        assert slugify("  Agent  ") == "agent"

    def test_mixed_case_lowercased(self):
        """Mixed case is converted to lowercase."""
        assert slugify("MyAgent") == "myagent"
        assert slugify("LOUD AGENT") == "loud-agent"

    def test_numbers_preserved(self):
        """Numbers are preserved in slug."""
        assert slugify("Agent 2000") == "agent-2000"


class TestBuildToolsYaml:
    """Tests for build_tools_yaml() function."""

    def test_readonly_posture(self):
        """readonly posture includes only read-only tools."""
        yaml = build_tools_yaml("readonly")
        assert "- search" in yaml
        assert "- read" in yaml
        assert "- changes" in yaml
        assert "- usages" in yaml
        assert "- edit" not in yaml
        assert "- execute" not in yaml

    def test_creator_posture(self):
        """creator posture includes search, read, edit, web."""
        yaml = build_tools_yaml("creator")
        assert "- search" in yaml
        assert "- read" in yaml
        assert "- edit" in yaml
        assert "- web" in yaml
        assert "- execute" not in yaml

    def test_full_posture(self):
        """full posture includes all tools including execute and terminal."""
        yaml = build_tools_yaml("full")
        assert "- search" in yaml
        assert "- read" in yaml
        assert "- edit" in yaml
        assert "- execute" in yaml
        assert "- terminal" in yaml
        assert "- agent" in yaml

    def test_invalid_posture_exits(self):
        """Invalid posture raises SystemExit."""
        with pytest.raises(SystemExit) as excinfo:
            build_tools_yaml("invalid")
        assert excinfo.value.code == 1


class TestInferExecutive:
    """Tests for infer_executive() function."""

    def test_with_area(self):
        """Area parameter generates 'Executive <Area>' hint."""
        result = infer_executive("Research Foo", "research")
        assert result == "Executive Research"

    def test_without_area(self):
        """Without area, returns placeholder comment."""
        result = infer_executive("Standalone Agent", None)
        assert "executive" in result.lower()


class TestValidateNameUnique:
    """Tests for validate_name_unique() function."""

    def test_unique_name_passes(self, tmp_path, monkeypatch):
        """Unique agent name does not raise."""
        # Mock AGENTS_DIR to point to empty temp dir
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        with patch("scripts.scaffold_agent.AGENTS_DIR", agents_dir):
            validate_name_unique("New Agent")  # Should not raise

    def test_duplicate_name_exits(self, tmp_path, monkeypatch):
        """Duplicate agent name raises SystemExit."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        # Create existing agent with same name
        existing = agents_dir / "test-agent.agent.md"
        existing.write_text("---\nname: Test Agent\n---\n")

        with patch("scripts.scaffold_agent.AGENTS_DIR", agents_dir):
            with pytest.raises(SystemExit) as excinfo:
                validate_name_unique("Test Agent")
            assert excinfo.value.code == 1


@pytest.mark.integration
class TestScaffoldAgentIntegration:
    """Integration tests using subprocess (smoke tests)."""

    def test_cli_dry_run(self):
        """Integration test: --dry-run prints without writing."""
        result = subprocess.run(
            [
                sys.executable,
                "scripts/scaffold_agent.py",
                "--name",
                "Test Agent",
                "--description",
                "Test description",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "DRY RUN" in result.stdout
        assert "name: Test Agent" in result.stdout

    def test_cli_description_too_long(self):
        """Integration test: Description >200 chars fails."""
        long_desc = "A" * 201

        result = subprocess.run(
            [sys.executable, "scripts/scaffold_agent.py", "--name", "Test Agent", "--description", long_desc],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "200" in result.stderr

    def test_cli_posture_selection(self):
        """Integration test: Posture affects tool list."""
        result = subprocess.run(
            [
                sys.executable,
                "scripts/scaffold_agent.py",
                "--name",
                "Readonly Test",
                "--description",
                "Test readonly posture",
                "--posture",
                "readonly",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "- search" in result.stdout
        assert "- read" in result.stdout
        # Should NOT have execute
        assert "- execute" not in result.stdout
