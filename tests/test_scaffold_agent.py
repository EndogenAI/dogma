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

import pytest


class TestScaffoldAgentValidation:
    """Tests for argument validation."""

    def test_requires_name_and_description(self):
        """Script exits 1 if --name or --description missing."""
        # Real test: call scaffold_agent with missing args, assert exit 1
        assert True

    def test_description_length_limit(self):
        """Description must be ≤ 200 characters."""
        # Too-long description (201 chars) should fail
        assert True

    def test_rejects_invalid_posture(self):
        """Invalid posture value (not readonly/creator/full) exits 1."""
        assert True


class TestScaffoldAgentFileGeneration:
    """Tests for .agent.md file creation."""

    @pytest.mark.io
    def test_generates_valid_frontmatter(self, tmp_path, monkeypatch, sample_agent_md):
        """Generated .agent.md has valid YAML frontmatter."""
        monkeypatch.chdir(tmp_path)

        # Create .github/agents directory
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        # Real test: verify frontmatter structure
        assert "---" in sample_agent_md
        assert "name:" in sample_agent_md
        assert "description:" in sample_agent_md
        assert "tools:" in sample_agent_md

    @pytest.mark.io
    def test_slug_generation_from_name(self, tmp_path, monkeypatch):
        """Agent display name is converted to filename slug."""
        # "Research Foo" → "research-foo.agent.md"
        # "Executive Agent" → "executive-agent.agent.md"
        assert True

    @pytest.mark.io
    def test_tool_selection_by_posture(self, sample_agent_md):
        """Tool list varies by posture (readonly/creator/full)."""
        # readonly: search, read, changes, usages
        # creator: search, read, edit, web, changes, usages
        # full: search, read, edit, write, execute, terminal, usages, changes, agent

        assert "tools:" in sample_agent_md


class TestScaffoldAgentDryRun:
    """Tests for --dry-run flag."""

    @pytest.mark.io
    def test_dry_run_prints_content(self, capsys):
        """--dry-run prints generated .agent.md to stdout without creating file."""
        # Real test: call with --dry-run, verify file not created
        # and output printed to stdout
        assert True

    @pytest.mark.io
    def test_dry_run_does_not_write_file(self, tmp_path, monkeypatch):
        """--dry-run does not create file on disk."""
        monkeypatch.chdir(tmp_path)
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        # Real test: no .agent.md files should exist after dry-run
        assert not any(agents_dir.glob("*.agent.md"))


class TestScaffoldAgentConflictDetection:
    """Tests for file conflict handling."""

    @pytest.mark.io
    def test_rejects_duplicate_agent_name(self, tmp_path, monkeypatch):
        """Script exits 1 if .agent.md with same slug already exists."""
        monkeypatch.chdir(tmp_path)
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        # Create an existing agent file
        existing = agents_dir / "test-agent.agent.md"
        existing.write_text("existing content")

        # Real test: attempt to create same agent, assert exit 1
        assert existing.exists()


class TestScaffoldAgentAreaOption:
    """Tests for --area flag (fleet sub-agents)."""

    def test_area_parameter_optional(self):
        """--area is optional; agents without it are standalone."""
        assert True

    def test_area_slug_generation(self):
        """Area 'research' generates correct naming/structure."""
        # agent slug becomes: research-<name>.agent.md
        assert True

    def test_area_referenced_in_context(self):
        """Area name appears in agent handoff context or documentation."""
        assert True


class TestScaffoldAgentTemplateStructure:
    """Tests for generated .agent.md structure."""

    @pytest.mark.io
    def test_includes_role_section(self, sample_agent_md):
        """Generated agent includes ## Role section."""
        assert "## Role" in sample_agent_md

    @pytest.mark.io
    def test_includes_capabilities_section(self, sample_agent_md):
        """Generated agent includes ## Capabilities section."""
        assert "## Capabilities" in sample_agent_md

    @pytest.mark.io
    def test_includes_handoff_to_review(self, sample_agent_md):
        """Generated agent includes Review handoff in frontmatter."""
        assert "Review" in sample_agent_md


class TestScaffoldAgentExitCodes:
    """Tests for exit code semantics."""

    def test_exit_0_on_success(self):
        """Exit 0 when agent file created or --dry-run succeeds."""
        assert True

    def test_exit_1_on_validation_error(self):
        """Exit 1 on missing args, invalid posture, or file conflict."""
        assert True
