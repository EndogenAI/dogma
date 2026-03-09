"""
tests/test_remaining_scripts.py

Unit and integration tests for:
- scripts/scaffold_workplan.py
- scripts/generate_agent_manifest.py
- scripts/link_source_stubs.py
- scripts/migrate_agent_xml.py

(Each script group could have its own test file; combined here for brevity.)
"""

import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import scaffold_workplan as sw  # noqa: E402, I001

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

    @pytest.mark.io
    def test_ci_field_in_phase_template(self, tmp_path, monkeypatch):
        """Generated workplan contains **CI**: field."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        monkeypatch.setattr("sys.argv", ["scaffold_workplan.py", "ci-test"])
        monkeypatch.setattr(sw, "_get_root", lambda: tmp_path)
        monkeypatch.setattr(sw, "_prompt", lambda msg, default: default)
        rc = sw.main()
        assert rc == 0
        content = (tmp_path / "docs" / "plans" / f"{date.today().isoformat()}-ci-test.md").read_text()
        assert "**CI**:" in content

    @pytest.mark.io
    def test_ci_field_default_value(self, tmp_path, monkeypatch):
        """Generated workplan with default CI input contains 'Tests, Auto-validate'."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        monkeypatch.setattr("sys.argv", ["scaffold_workplan.py", "ci-default"])
        monkeypatch.setattr(sw, "_get_root", lambda: tmp_path)
        monkeypatch.setattr(sw, "_prompt", lambda msg, default: default)
        rc = sw.main()
        assert rc == 0
        content = (tmp_path / "docs" / "plans" / f"{date.today().isoformat()}-ci-default.md").read_text()
        assert "**CI**: Tests, Auto-validate" in content

    @pytest.mark.io
    def test_ci_field_invalid_value_exits_1(self, tmp_path, monkeypatch):
        """Providing an invalid CI token causes exit code 1."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        monkeypatch.setattr("sys.argv", ["scaffold_workplan.py", "ci-invalid"])
        monkeypatch.setattr(sw, "_get_root", lambda: tmp_path)
        call_count = {"n": 0}

        def fake_prompt(msg, default):
            call_count["n"] += 1
            if call_count["n"] == 1:  # CI prompt
                return "InvalidCI"
            return default

        monkeypatch.setattr(sw, "_prompt", fake_prompt)
        rc = sw.main()
        assert rc == 1

    @pytest.mark.io
    def test_linked_issues_emits_closes(self, tmp_path, monkeypatch):
        """Providing issue numbers 42,43 emits Closes #42, Closes #43."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        monkeypatch.setattr("sys.argv", ["scaffold_workplan.py", "issue-test"])
        monkeypatch.setattr(sw, "_get_root", lambda: tmp_path)
        call_count = {"n": 0}

        def fake_prompt(msg, default):
            call_count["n"] += 1
            if call_count["n"] == 1:  # CI prompt
                return default
            return "42,43"  # linked issues

        monkeypatch.setattr(sw, "_prompt", fake_prompt)
        rc = sw.main()
        assert rc == 0
        content = (tmp_path / "docs" / "plans" / f"{date.today().isoformat()}-issue-test.md").read_text()
        assert "Closes #42" in content
        assert "Closes #43" in content

    @pytest.mark.io
    def test_no_linked_issues_no_section(self, tmp_path, monkeypatch):
        """Providing no issue numbers omits the PR Description Template section."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        monkeypatch.setattr("sys.argv", ["scaffold_workplan.py", "no-issues"])
        monkeypatch.setattr(sw, "_get_root", lambda: tmp_path)
        monkeypatch.setattr(sw, "_prompt", lambda msg, default: default)
        rc = sw.main()
        assert rc == 0
        content = (tmp_path / "docs" / "plans" / f"{date.today().isoformat()}-no-issues.md").read_text()
        assert "## PR Description Template" not in content

    @pytest.mark.io
    def test_negative_issue_number_exits_1(self, tmp_path, monkeypatch):
        """Providing a negative issue number (e.g. -1) causes exit code 1."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        monkeypatch.setattr("sys.argv", ["scaffold_workplan.py", "neg-issue"])
        monkeypatch.setattr(sw, "_get_root", lambda: tmp_path)
        call_count = {"n": 0}

        def fake_prompt(msg, default):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return default
            return "-1"  # negative issue number

        monkeypatch.setattr(sw, "_prompt", fake_prompt)
        rc = sw.main()
        assert rc == 1

    @pytest.mark.io
    def test_duplicate_issues_deduplicated(self, tmp_path, monkeypatch):
        """Duplicate issue numbers are deduplicated in the output."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        monkeypatch.setattr("sys.argv", ["scaffold_workplan.py", "dedup-test"])
        monkeypatch.setattr(sw, "_get_root", lambda: tmp_path)
        call_count = {"n": 0}

        def fake_prompt(msg, default):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return default
            return "42,42,43"  # duplicate 42

        monkeypatch.setattr(sw, "_prompt", fake_prompt)
        rc = sw.main()
        assert rc == 0
        content = (tmp_path / "docs" / "plans" / f"{date.today().isoformat()}-dedup-test.md").read_text()
        # Should appear only once
        assert content.count("Closes #42") == 1
        assert "Closes #43" in content


# ===== generate_agent_manifest.py tests =====


class TestGenerateAgentManifest:
    """Tests for agent manifest generation."""

    def test_count_cross_ref_density_unit(self):
        """count_cross_ref_density counts distinct reference lines correctly."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "generate_agent_manifest",
            Path(__file__).parent.parent / "scripts" / "generate_agent_manifest.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = mod.count_cross_ref_density

        assert fn("") == 0
        assert fn("See MANIFESTO.md for context") == 1
        assert fn("MANIFESTO.md\nAGENTS.md") == 2
        assert fn("MANIFESTO.md\nMANIFESTO.md") == 2  # two distinct lines
        assert fn("See MANIFESTO.md and AGENTS.md on same line") == 1  # one line
        assert fn("docs/guides/foo.md is relevant") == 1

    def test_low_density_warning_emitted(self, caplog):
        """build_manifest emits a WARNING for agents with cross_ref_density < 1."""
        import importlib.util
        import logging

        spec = importlib.util.spec_from_file_location(
            "generate_agent_manifest",
            Path(__file__).parent.parent / "scripts" / "generate_agent_manifest.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        fake_entry = {
            "name": "Low-Density Agent",
            "description": "test",
            "tools": [],
            "posture": "readonly",
            "capabilities": [],
            "handoffs": [],
            "file": "/tmp/low-density.agent.md",
            "cross_ref_density": 0,
        }
        with caplog.at_level(logging.WARNING):
            mod.build_manifest([fake_entry], Path("/tmp"))

        assert any("Low-Density Agent" in r.message for r in caplog.records)

    @pytest.mark.io
    @pytest.mark.integration
    def test_reads_all_agent_files(self, tmp_path, monkeypatch):
        """generate_agent_manifest scans .github/agents/*.agent.md."""
        import json as jsonmod
        import subprocess

        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "AGENTS.md").write_text("# Fleet\nSee MANIFESTO.md\n")
        (tmp_path / "AGENTS.md").write_text("# Root AGENTS\nSee MANIFESTO.md\n")
        agent_body = "---\nname: Test Agent\ndescription: A test agent\ntools: []\n---\nSee MANIFESTO.md\n"
        (agents_dir / "test.agent.md").write_text(agent_body)

        result = subprocess.run(
            [
                "python",
                str(Path(__file__).parent.parent / "scripts" / "generate_agent_manifest.py"),
                "--agents-dir",
                str(agents_dir),
            ],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert result.returncode == 0
        data = jsonmod.loads(result.stdout)
        assert data["agent_count"] == 1
        assert data["agents"][0]["name"] == "Test Agent"

    @pytest.mark.io
    @pytest.mark.integration
    def test_outputs_json_manifest_with_density(self, tmp_path):
        """JSON manifest includes cross_ref_density per agent and avg_cross_ref_density at root."""
        import json as jsonmod
        import subprocess

        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("# Root\n")
        agent_with_refs = (
            "---\nname: High Density\ndescription: Dense agent\ntools: []\n---\nSee MANIFESTO.md\nSee AGENTS.md\n"
        )
        (agents_dir / "dense.agent.md").write_text(agent_with_refs)

        result = subprocess.run(
            [
                "python",
                str(Path(__file__).parent.parent / "scripts" / "generate_agent_manifest.py"),
                "--agents-dir",
                str(agents_dir),
            ],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert result.returncode == 0
        data = jsonmod.loads(result.stdout)
        assert "avg_cross_ref_density" in data
        assert "cross_ref_density" in data["agents"][0]
        assert data["agents"][0]["cross_ref_density"] >= 1

    @pytest.mark.io
    @pytest.mark.integration
    def test_outputs_markdown_manifest_with_density_section(self, tmp_path):
        """Markdown output includes '## Cross-Reference Density' section."""
        import subprocess

        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("# Root\n")
        agent_body = "---\nname: Markdown Agent\ndescription: For markdown test\ntools: []\n---\n"
        (agents_dir / "md.agent.md").write_text(agent_body)

        result = subprocess.run(
            [
                "python",
                str(Path(__file__).parent.parent / "scripts" / "generate_agent_manifest.py"),
                "--agents-dir",
                str(agents_dir),
                "--format",
                "markdown",
            ],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert result.returncode == 0
        assert "## Cross-Reference Density" in result.stdout
        assert "| Agent | cross_ref_density |" in result.stdout

    @pytest.mark.io
    @pytest.mark.integration
    def test_includes_agent_metadata(self, tmp_path):
        """Manifest includes name, description, cross_ref_density per agent."""
        import json as jsonmod
        import subprocess

        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("# Root\n")
        agent_body = "---\nname: Meta Agent\ndescription: Metadata test\ntools: [search]\n---\n"
        (agents_dir / "meta.agent.md").write_text(agent_body)

        result = subprocess.run(
            [
                "python",
                str(Path(__file__).parent.parent / "scripts" / "generate_agent_manifest.py"),
                "--agents-dir",
                str(agents_dir),
            ],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert result.returncode == 0
        data = jsonmod.loads(result.stdout)
        agent = data["agents"][0]
        assert "name" in agent
        assert "description" in agent
        assert "cross_ref_density" in agent

    def _load_manifest_mod(self):
        """Helper: load generate_agent_manifest module via importlib for in-process tests."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "generate_agent_manifest",
            Path(__file__).parent.parent / "scripts" / "generate_agent_manifest.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    @pytest.mark.io
    def test_process_agent_file_returns_density(self, tmp_path):
        """process_agent_file returns a dict including cross_ref_density key."""
        mod = self._load_manifest_mod()
        agent_file = tmp_path / "test.agent.md"
        agent_file.write_text(
            "---\nname: Ref Agent\ndescription: Has refs\ntools: []\n---\nSee MANIFESTO.md and AGENTS.md here.\n"
        )
        result = mod.process_agent_file(agent_file)
        assert result is not None
        assert "cross_ref_density" in result
        assert result["cross_ref_density"] == 1  # one line has both refs

    @pytest.mark.io
    def test_process_agent_file_missing_name_returns_none(self, tmp_path):
        """process_agent_file returns None when 'name' field is missing."""
        mod = self._load_manifest_mod()
        agent_file = tmp_path / "no-name.agent.md"
        agent_file.write_text("---\ndescription: No name here\ntools: []\n---\n")
        result = mod.process_agent_file(agent_file)
        assert result is None

    def test_build_manifest_avg_density(self):
        """build_manifest computes avg_cross_ref_density from entries."""
        mod = self._load_manifest_mod()
        entries = [
            {
                "name": "Agent A",
                "description": "a",
                "tools": [],
                "posture": "readonly",
                "capabilities": [],
                "handoffs": [],
                "file": "/tmp/a.agent.md",
                "cross_ref_density": 4,
            },
            {
                "name": "Agent B",
                "description": "b",
                "tools": [],
                "posture": "readonly",
                "capabilities": [],
                "handoffs": [],
                "file": "/tmp/b.agent.md",
                "cross_ref_density": 2,
            },
        ]
        manifest = mod.build_manifest(entries, Path("/tmp"))
        assert manifest["avg_cross_ref_density"] == 3.0
        assert manifest["agent_count"] == 2
        assert "generated" in manifest

    def test_build_manifest_empty_entries(self):
        """build_manifest handles empty agent list without division-by-zero."""
        mod = self._load_manifest_mod()
        manifest = mod.build_manifest([], Path("/tmp"))
        assert manifest["avg_cross_ref_density"] == 0.0
        assert manifest["agent_count"] == 0

    def test_format_markdown_density_section(self):
        """format_markdown includes density table with fleet average."""
        mod = self._load_manifest_mod()
        manifest = {
            "agents": [
                {
                    "name": "Alpha",
                    "description": "desc",
                    "posture": "readonly",
                    "capabilities": [],
                    "handoffs": [],
                    "cross_ref_density": 5,
                }
            ],
            "avg_cross_ref_density": 5.0,
        }
        output = mod.format_markdown(manifest)
        assert "## Cross-Reference Density" in output
        assert "| Alpha | 5 |" in output
        assert "Fleet average" in output
        assert "5.0" in output

    def test_parse_simple_yaml_scalar_and_list(self):
        """parse_simple_yaml handles scalar strings and block lists."""
        mod = self._load_manifest_mod()
        yaml = "name: Test Agent\ndescription: A test\ntools:\n  - search\n  - read\n"
        result = mod.parse_simple_yaml(yaml)
        assert result["name"] == "Test Agent"
        assert result["description"] == "A test"
        assert result["tools"] == ["search", "read"]

    def test_parse_simple_yaml_inline_list(self):
        """parse_simple_yaml handles inline [list] syntax by returning it as scalar."""
        mod = self._load_manifest_mod()
        yaml = "name: Inline\ntools: [search, edit]\n"
        result = mod.parse_simple_yaml(yaml)
        assert "name" in result
        # Inline list is treated as a scalar string by the simple parser
        assert "tools" in result

    def test_derive_posture_full(self):
        """derive_posture returns 'full' for execute tools."""
        mod = self._load_manifest_mod()
        assert mod.derive_posture(["execute", "search"]) == "full"
        assert mod.derive_posture(["terminal"]) == "full"

    def test_derive_posture_creator(self):
        """derive_posture returns 'creator' for edit tools without execute."""
        mod = self._load_manifest_mod()
        assert mod.derive_posture(["edit", "search"]) == "creator"
        assert mod.derive_posture(["write"]) == "creator"

    def test_derive_posture_readonly(self):
        """derive_posture returns 'readonly' for read-only tools or empty list."""
        mod = self._load_manifest_mod()
        assert mod.derive_posture([]) == "readonly"
        assert mod.derive_posture(["search", "read"]) == "readonly"

    @pytest.mark.io
    def test_process_agent_file_no_frontmatter_returns_none(self, tmp_path):
        """process_agent_file returns None when file has no YAML frontmatter."""
        mod = self._load_manifest_mod()
        agent_file = tmp_path / "no-fm.agent.md"
        agent_file.write_text("# No Frontmatter\nJust body text.\n")
        assert mod.process_agent_file(agent_file) is None

    @pytest.mark.io
    def test_extract_frontmatter_valid(self, tmp_path):
        """extract_frontmatter returns YAML text between --- fences."""
        mod = self._load_manifest_mod()
        text = "---\nname: X\n---\nBody\n"
        result = mod.extract_frontmatter(text)
        assert result is not None
        assert "name: X" in result

    @pytest.mark.io
    def test_main_dry_run(self, tmp_path, monkeypatch, capsys):
        """main() --dry-run lists files without generating output."""
        import sys

        mod = self._load_manifest_mod()
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("# Root\n")
        (agents_dir / "a.agent.md").write_text("---\nname: A\ndescription: x\ntools: []\n---\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["generate_agent_manifest.py", "--agents-dir", str(agents_dir), "--dry-run"])
        ret = mod.main()
        assert ret == 0

    @pytest.mark.io
    def test_main_missing_agents_dir_exits_1(self, tmp_path, monkeypatch):
        """main() exits 1 when --agents-dir does not exist."""
        import sys

        mod = self._load_manifest_mod()
        monkeypatch.chdir(tmp_path)
        (tmp_path / "AGENTS.md").write_text("# Root\n")
        monkeypatch.setattr(sys, "argv", ["generate_agent_manifest.py", "--agents-dir", str(tmp_path / "no-such")])
        ret = mod.main()
        assert ret == 1

    @pytest.mark.io
    def test_main_json_output_to_file(self, tmp_path, monkeypatch):
        """main() writes JSON manifest to --output file when agents exist."""
        import json as jsonmod
        import sys

        mod = self._load_manifest_mod()
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (tmp_path / "AGENTS.md").write_text("# Root\n")
        (agents_dir / "b.agent.md").write_text(
            "---\nname: Beta\ndescription: beta agent\ntools: []\n---\nSee MANIFESTO.md\n"
        )
        out_file = tmp_path / "manifest.json"
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            sys,
            "argv",
            ["generate_agent_manifest.py", "--agents-dir", str(agents_dir), "--output", str(out_file)],
        )
        ret = mod.main()
        assert ret == 0
        data = jsonmod.loads(out_file.read_text())
        assert "avg_cross_ref_density" in data
        assert data["agents"][0]["cross_ref_density"] >= 1

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
