"""
tests/test_agent_registry.py
-----------------------------
Tests for scripts/agent_registry.py — the capability-aware, filterable registry
of all fleet agents.

Coverage targets:
    - posture derivation (readonly / creator / full)
    - load_registry: empty dir, missing dir, normal agents, optional fields,
      missing name, bad frontmatter
    - apply_filters: by tool, tier, area, combined, no-match
    - render_markdown_table: normal, empty
    - render_json
    - main() CLI: --list, --json, --output, --filter-*, missing dir,
      empty registry, error returns
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import agent_registry  # noqa: E402

# ---------------------------------------------------------------------------
# Fixture agent content strings
# ---------------------------------------------------------------------------

MINIMAL_AGENT = """\
---
name: Test Agent
description: A minimal test agent for unit testing.
tools:
  - search
  - read
---
Body content here.
"""

CREATOR_AGENT = """\
---
name: Creator Agent
description: A creator-posture documentation agent.
tools:
  - edit
  - read
tier: executive
area: docs
---
Body.
"""

FULL_AGENT = """\
---
name: Full Agent
description: A full-posture scripting agent.
tools:
  - terminal
  - read
tier: specialist
area: scripts
---
Body.
"""

MISSING_NAME_AGENT = """\
---
description: An agent with no name field.
tools:
  - read
---
"""

BAD_FRONTMATTER = """\
Not starting with a YAML frontmatter fence.
"""

NO_TIER_AREA_AGENT = """\
---
name: Bare Agent
description: An agent with no tier or area.
tools:
  - read
---
"""


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def write_agents(tmp_path: Path, files: dict[str, str]) -> Path:
    """Write agent file content dict to tmp_path and return that directory."""
    for filename, content in files.items():
        (tmp_path / filename).write_text(content, encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# Posture derivation
# ---------------------------------------------------------------------------


def test_derive_posture_readonly():
    assert agent_registry.derive_posture(["search", "read"]) == "readonly"


def test_derive_posture_readonly_empty():
    assert agent_registry.derive_posture([]) == "readonly"


def test_derive_posture_creator_edit():
    assert agent_registry.derive_posture(["edit", "read"]) == "creator"


def test_derive_posture_creator_write():
    assert agent_registry.derive_posture(["write"]) == "creator"


def test_derive_posture_full_terminal():
    assert agent_registry.derive_posture(["terminal", "read"]) == "full"


def test_derive_posture_full_execute():
    assert agent_registry.derive_posture(["execute"]) == "full"


def test_derive_posture_full_beats_creator():
    # terminal + edit → full wins over creator
    assert agent_registry.derive_posture(["terminal", "edit"]) == "full"


# ---------------------------------------------------------------------------
# load_registry
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_load_registry_missing_dir(tmp_path):
    entries, had_errors = agent_registry.load_registry(tmp_path / "nonexistent")
    assert entries == []
    assert had_errors is True


@pytest.mark.io
def test_load_registry_empty_dir(tmp_path):
    entries, had_errors = agent_registry.load_registry(tmp_path)
    assert entries == []
    assert had_errors is False


@pytest.mark.io
def test_load_registry_minimal_agent(tmp_path):
    write_agents(tmp_path, {"test.agent.md": MINIMAL_AGENT})
    entries, had_errors = agent_registry.load_registry(tmp_path)
    assert had_errors is False
    assert len(entries) == 1
    e = entries[0]
    assert e["name"] == "Test Agent"
    assert e["tier"] == "unset"
    assert e["area"] == "unset"
    assert e["posture"] == "readonly"
    assert set(e["tools"]) == {"search", "read"}


@pytest.mark.io
def test_load_registry_with_optional_fields(tmp_path):
    write_agents(tmp_path, {"creator.agent.md": CREATOR_AGENT})
    entries, had_errors = agent_registry.load_registry(tmp_path)
    assert had_errors is False
    assert len(entries) == 1
    e = entries[0]
    assert e["tier"] == "executive"
    assert e["area"] == "docs"
    assert e["posture"] == "creator"


@pytest.mark.io
def test_load_registry_full_agent(tmp_path):
    write_agents(tmp_path, {"full.agent.md": FULL_AGENT})
    entries, had_errors = agent_registry.load_registry(tmp_path)
    assert had_errors is False
    assert entries[0]["posture"] == "full"
    assert entries[0]["tier"] == "specialist"
    assert entries[0]["area"] == "scripts"


@pytest.mark.io
def test_load_registry_defaults_tier_area(tmp_path):
    write_agents(tmp_path, {"bare.agent.md": NO_TIER_AREA_AGENT})
    entries, _ = agent_registry.load_registry(tmp_path)
    assert entries[0]["tier"] == "unset"
    assert entries[0]["area"] == "unset"


@pytest.mark.io
def test_load_registry_missing_name_skipped(tmp_path):
    write_agents(tmp_path, {"noname.agent.md": MISSING_NAME_AGENT})
    entries, had_errors = agent_registry.load_registry(tmp_path)
    assert entries == []
    assert had_errors is True


@pytest.mark.io
def test_load_registry_bad_frontmatter_skipped(tmp_path):
    write_agents(tmp_path, {"bad.agent.md": BAD_FRONTMATTER})
    entries, had_errors = agent_registry.load_registry(tmp_path)
    assert entries == []
    assert had_errors is True


@pytest.mark.io
def test_load_registry_mixed_valid_and_invalid(tmp_path):
    write_agents(
        tmp_path,
        {
            "valid.agent.md": MINIMAL_AGENT,
            "bad.agent.md": BAD_FRONTMATTER,
        },
    )
    entries, had_errors = agent_registry.load_registry(tmp_path)
    assert len(entries) == 1
    assert had_errors is True


# ---------------------------------------------------------------------------
# apply_filters
# ---------------------------------------------------------------------------


def _make_entries() -> list[dict]:
    return [
        {
            "name": "A",
            "tier": "executive",
            "area": "research",
            "tools": ["search", "read"],
            "posture": "readonly",
            "file": "a.agent.md",
            "description": "",
        },
        {
            "name": "B",
            "tier": "specialist",
            "area": "scripts",
            "tools": ["edit", "terminal"],
            "posture": "full",
            "file": "b.agent.md",
            "description": "",
        },
        {
            "name": "C",
            "tier": "unset",
            "area": "docs",
            "tools": ["read"],
            "posture": "readonly",
            "file": "c.agent.md",
            "description": "",
        },
    ]


def test_filter_tool():
    result = agent_registry.apply_filters(_make_entries(), filter_tool="terminal")
    assert len(result) == 1
    assert result[0]["name"] == "B"


def test_filter_tier():
    result = agent_registry.apply_filters(_make_entries(), filter_tier="executive")
    assert [e["name"] for e in result] == ["A"]


def test_filter_area():
    result = agent_registry.apply_filters(_make_entries(), filter_area="docs")
    assert [e["name"] for e in result] == ["C"]


def test_filter_combined_tool_and_tier():
    result = agent_registry.apply_filters(_make_entries(), filter_tool="read", filter_tier="executive")
    assert [e["name"] for e in result] == ["A"]


def test_filter_no_match():
    result = agent_registry.apply_filters(_make_entries(), filter_tier="nonexistent")
    assert result == []


def test_filter_case_insensitive():
    result = agent_registry.apply_filters(_make_entries(), filter_tool="TERMINAL")
    assert len(result) == 1
    assert result[0]["name"] == "B"


def test_filter_no_args_returns_all():
    entries = _make_entries()
    result = agent_registry.apply_filters(entries)
    assert result == entries


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def test_render_markdown_table_structure():
    entries = [
        {
            "name": "Foo",
            "tier": "exec",
            "area": "docs",
            "posture": "readonly",
            "tools": ["search"],
            "file": "foo.agent.md",
            "description": "",
        }
    ]
    out = agent_registry.render_markdown_table(entries)
    lines = out.splitlines()
    assert len(lines) == 3  # header, separator, one data row
    assert "Name" in lines[0]
    assert "Foo" in lines[2]
    assert "search" in lines[2]
    assert lines[1].startswith("|")
    assert set(lines[1].replace("|", "").replace("-", "").replace(" ", "")) == set()


def test_render_markdown_table_empty():
    out = agent_registry.render_markdown_table([])
    lines = out.splitlines()
    assert len(lines) == 2  # header + separator, no data rows
    assert "Name" in lines[0]


def test_render_json_valid():
    entries = [
        {
            "name": "Foo",
            "tier": "exec",
            "area": "docs",
            "posture": "readonly",
            "tools": ["search"],
            "file": "foo.agent.md",
            "description": "",
        }
    ]
    out = agent_registry.render_json(entries)
    parsed = json.loads(out)
    assert isinstance(parsed, list)
    assert parsed[0]["name"] == "Foo"
    assert parsed[0]["tools"] == ["search"]


def test_render_json_empty():
    out = agent_registry.render_json([])
    assert json.loads(out) == []


# ---------------------------------------------------------------------------
# CLI (main())
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_main_list(tmp_path, capsys):
    write_agents(tmp_path, {"test.agent.md": MINIMAL_AGENT})
    rc = agent_registry.main(["--list", "--agents-dir", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Test Agent" in captured.out
    assert "|" in captured.out


@pytest.mark.io
def test_main_json(tmp_path, capsys):
    write_agents(tmp_path, {"test.agent.md": MINIMAL_AGENT})
    rc = agent_registry.main(["--json", "--agents-dir", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert any(e["name"] == "Test Agent" for e in parsed)


@pytest.mark.io
def test_main_output_file(tmp_path):
    write_agents(tmp_path, {"test.agent.md": MINIMAL_AGENT})
    out_file = tmp_path / "output.md"
    rc = agent_registry.main(["--list", "--agents-dir", str(tmp_path), "--output", str(out_file)])
    assert rc == 0
    assert out_file.exists()
    assert "Test Agent" in out_file.read_text()


@pytest.mark.io
def test_main_filter_tool(tmp_path, capsys):
    write_agents(tmp_path, {"test.agent.md": MINIMAL_AGENT, "full.agent.md": FULL_AGENT})
    rc = agent_registry.main(["--list", "--filter-tool", "terminal", "--agents-dir", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Full Agent" in captured.out
    assert "Test Agent" not in captured.out


@pytest.mark.io
def test_main_filter_tier(tmp_path, capsys):
    write_agents(tmp_path, {"creator.agent.md": CREATOR_AGENT, "full.agent.md": FULL_AGENT})
    rc = agent_registry.main(["--list", "--filter-tier", "executive", "--agents-dir", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Creator Agent" in captured.out
    assert "Full Agent" not in captured.out


@pytest.mark.io
def test_main_filter_area(tmp_path, capsys):
    write_agents(tmp_path, {"creator.agent.md": CREATOR_AGENT, "full.agent.md": FULL_AGENT})
    rc = agent_registry.main(["--list", "--filter-area", "scripts", "--agents-dir", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Full Agent" in captured.out
    assert "Creator Agent" not in captured.out


@pytest.mark.io
def test_main_missing_agents_dir():
    rc = agent_registry.main(["--list", "--agents-dir", "/nonexistent/path/to/agents"])
    assert rc == 1


@pytest.mark.io
def test_main_empty_registry_list(tmp_path, capsys):
    rc = agent_registry.main(["--list", "--agents-dir", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    # Header row still present even with no agents
    assert "Name" in captured.out


@pytest.mark.io
def test_main_default_renders_list(tmp_path, capsys):
    # No --list or --json flag → defaults to list
    write_agents(tmp_path, {"test.agent.md": MINIMAL_AGENT})
    rc = agent_registry.main(["--agents-dir", str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "|" in captured.out


@pytest.mark.io
def test_main_error_returns_1(tmp_path):
    # A file with no frontmatter → had_errors=True but one valid file too
    write_agents(tmp_path, {"valid.agent.md": MINIMAL_AGENT, "bad.agent.md": BAD_FRONTMATTER})
    rc = agent_registry.main(["--list", "--agents-dir", str(tmp_path)])
    assert rc == 1
