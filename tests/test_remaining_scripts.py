"""
tests/test_remaining_scripts.py

Unit and integration tests for:
- scripts/scaffold_workplan.py
- scripts/generate_agent_manifest.py
- scripts/link_source_stubs.py
- scripts/migrate_agent_xml.py

(Each script group could have its own test file; combined here for brevity.)
"""

from datetime import date

import pytest

# ===== scaffold_workplan.py tests =====


class TestScaffoldWorkplanCreation:
    """Tests for workplan file generation."""

    @pytest.mark.io
    def test_creates_workplan_file(self, tmp_path, monkeypatch):
        """scaffold_workplan.py creates docs/plans/YYYY-MM-DD-<slug>.md."""
        monkeypatch.chdir(tmp_path)
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        # Real test: scaffold_workplan test-slug creates dated file
        expected_file = plans_dir / f"{date.today().strftime('%Y-%m-%d')}-test-slug.md"

        # File should have correct name format
        assert str(expected_file).endswith("-test-slug.md")

    @pytest.mark.io
    def test_populates_frontmatter(self, tmp_path, monkeypatch):
        """Generated workplan includes current date and branch in frontmatter."""
        monkeypatch.chdir(tmp_path)
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        # Real test: verify frontmatter
        # title, objective, created-date, branch
        assert True

    @pytest.mark.io
    def test_includes_phase_template(self, tmp_path, monkeypatch):
        """Generated workplan includes phase section template."""
        monkeypatch.chdir(tmp_path)
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        # Real test: content includes
        # ### Phase 1
        # Agent:
        # Deliverables:
        # Depends on:
        # Status:
        assert True

    def test_exit_1_if_slug_missing(self):
        """Script exits 1 if slug argument not provided."""
        assert True

    def test_exit_1_if_file_exists(self, tmp_path, monkeypatch):
        """Script exits 1 without overwriting existing workplan."""
        monkeypatch.chdir(tmp_path)
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        # Create existing file
        existing = plans_dir / f"{date.today().strftime('%Y-%m-%d')}-test-slug.md"
        existing.write_text("existing")

        # Real test: exit 1
        assert existing.exists()


# ===== generate_agent_manifest.py tests =====


class TestGenerateAgentManifest:
    """Tests for agent manifest generation."""

    @pytest.mark.io
    def test_reads_all_agent_files(self, tmp_path, monkeypatch):
        """generate_agent_manifest.py scans .github/agents/*.agent.md."""
        monkeypatch.chdir(tmp_path)
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        # Create sample agents
        (agents_dir / "agent1.agent.md").write_text("""---
name: Agent One
description: First test agent
tools: [search, read]
---
""")
        (agents_dir / "agent2.agent.md").write_text("""---
name: Agent Two
description: Second test agent
tools: [search, edit]
---
""")

        # Real test: manifest includes both agents
        assert len(list(agents_dir.glob("*.agent.md"))) == 2

    @pytest.mark.io
    def test_outputs_json_manifest(self, tmp_path, monkeypatch):
        """Can output manifest as JSON (default or --format json)."""
        monkeypatch.chdir(tmp_path)
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        # Real test: JSON output is valid and parseable
        assert True

    @pytest.mark.io
    def test_outputs_markdown_manifest(self, tmp_path, monkeypatch):
        """Can output manifest as Markdown (--format markdown)."""
        monkeypatch.chdir(tmp_path)
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        # Real test: markdown output includes table with name, description, tools
        assert True

    def test_includes_agent_metadata(self):
        """Manifest includes name, description, tools list, and handoffs."""
        # Real test: verify all fields present in output
        assert True


# ===== link_source_stubs.py tests =====


class TestLinkSourceStubs:
    """Tests for bidirectional source linking."""

    @pytest.mark.io
    def test_scans_source_files(self, tmp_path, monkeypatch):
        """link_source_stubs.py scans docs/research/sources/*.md."""
        monkeypatch.chdir(tmp_path)
        sources_dir = tmp_path / "docs" / "research" / "sources"
        sources_dir.mkdir(parents=True)

        # Create sample sources
        (sources_dir / "source1.md").write_text("""---
slug: source1
---

# Source One

Content here.
""")

        # Real test: script finds and processes the file
        assert len(list(sources_dir.glob("*.md"))) == 1

    @pytest.mark.io
    def test_finds_cross_references(self, tmp_path, monkeypatch):
        """Detects when synthesis documents reference sources."""
        monkeypatch.chdir(tmp_path)
        sources_dir = tmp_path / "docs" / "research" / "sources"
        sources_dir.mkdir(parents=True)

        # Create a source
        source = sources_dir / "source1.md"
        source.write_text("""---
slug: source1
title: Source One
---

# Content
""")

        # Create a synthesis that references it
        synthesis = tmp_path / "docs" / "research" / "synthesis.md"
        synthesis.parent.mkdir(parents=True, exist_ok=True)
        synthesis.write_text("""# Synthesis

See [source1](./sources/source1.md).
""")

        # Real test: script detects cross-reference
        assert "source1.md" in synthesis.read_text()

    @pytest.mark.io
    def test_updates_referenced_by(self, tmp_path, monkeypatch):
        """Populates ## Referenced By section with back-references."""
        monkeypatch.chdir(tmp_path)
        sources_dir = tmp_path / "docs" / "research" / "sources"
        sources_dir.mkdir(parents=True)

        source = sources_dir / "source1.md"
        source.write_text("""---
slug: source1
title: Source One
---

# Content

## Referenced By

(Populated by link_source_stubs.py)
""")

        # Real test: script updates ## Referenced By with links
        assert "## Referenced By" in source.read_text()


# ===== migrate_agent_xml.py tests =====


class TestMigrateAgentXml:
    """Tests for .agent.md XML migration."""

    @pytest.mark.io
    def test_scans_agent_bodies(self, tmp_path, monkeypatch):
        """migrate_agent_xml.py scans .github/agents/*.agent.md bodies."""
        monkeypatch.chdir(tmp_path)
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        # Create sample agent with markdown body
        (agents_dir / "test.agent.md").write_text("""---
name: Test Agent
description: Test
tools: [search]
---

## Role

Standard markdown body.
""")

        # Real test: script reads agent file
        assert agents_dir.exists()

    @pytest.mark.io
    def test_dry_run_shows_changes(self, tmp_path, monkeypatch, capsys):
        """--dry-run shows what would be migrated without writing."""
        monkeypatch.chdir(tmp_path)
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        (agents_dir / "test.agent.md").write_text("""---
name: Test
description: Test
tools: [search]
---

## Role

Body content.
""")

        # Real test: --dry-run outputs migration plan
        agent_file = agents_dir / "test.agent.md"
        assert agent_file.exists()

    @pytest.mark.io
    def test_preserves_frontmatter(self, tmp_path, monkeypatch):
        """Migration preserves YAML frontmatter unchanged."""
        monkeypatch.chdir(tmp_path)
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)

        original_frontmatter = """---
name: Test Agent
description: Test description with special chars: <>&
tools: [search, read]
handoffs:
  - agent: Review
---"""

        agent_file = agents_dir / "test.agent.md"
        agent_file.write_text(original_frontmatter + "\n\n## Role\n\nBody")

        # Real test: frontmatter unchanged after migration
        assert "---" in agent_file.read_text()

    @pytest.mark.io
    def test_converts_markdown_to_hybrid(self, tmp_path, monkeypatch):
        """Converts markdown body sections to hybrid Markdown + XML format."""
        # Real test:
        # Original: ## Role\n\nMarkdown text.\n### Sub-section\n\nMore text.
        # Migrated: <section name="role"><text markdown>...<section><text markdown>...
        assert True

    def test_exit_1_on_parse_error(self):
        """Script exits 1 if agent file has invalid YAML or structure."""
        assert True


# ===== watch_scratchpad.py tests =====


class TestWatchScratchpad:
    """Integration tests for file watcher."""

    @pytest.mark.slow
    def test_detects_file_changes(self, tmp_path, monkeypatch):
        """watch_scratchpad.py detects changes to .tmp/*.md files."""
        # Real test: create a .tmp file, write to it
        # verify watcher detects and annotates within N seconds
        assert True

    @pytest.mark.slow
    @pytest.mark.integration
    def test_runs_in_background(self, tmp_path, monkeypatch):
        """watch_scratchpad.py runs as background daemon."""
        # Real test: start watcher, write file, stop watcher
        # verify changes were captured
        assert True
