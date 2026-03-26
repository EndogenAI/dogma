# `generate\_agent\_manifest`

generate_agent_manifest.py
--------------------------
Purpose:
    Enumerate all .agent.md files in .github/agents/, extract name, description,
    tools, posture, capabilities, and handoffs from their YAML frontmatter, and
    emit a structured manifest to stdout (JSON or Markdown table). Enables
    lazy-loading of agent metadata — orchestrators can select the right agent
    from ~100-token stubs without paying the full ~5K-token cost of loading each
    agent body.

Inputs:
    .github/agents/*.agent.md files with YAML frontmatter blocks.

Outputs:
    JSON manifest (default) or Markdown table to stdout, or to --output file.
    Each agent entry contains:
        name               — display name from frontmatter
        description        — one-line summary from frontmatter
        tools              — list of tool names from frontmatter
        posture            — derived from tools: "readonly" | "creator" | "full"
        capabilities       — 2-5 short lowercase-hyphenated tags from description
        handoffs           — list of agent names this agent can hand off to
        file               — repo-relative path to the .agent.md file
        cross_ref_density  — int count of lines referencing MANIFESTO.md, AGENTS.md, or docs/guides/
    Summary line is always written to stderr:
        Generated manifest: N agents
    Fleet average: avg_cross_ref_density included in manifest root.
    Warnings to stderr: agents with cross_ref_density < 1 are flagged.

Connectivity Atlas Output:
    The manifest serves as a connectivity atlas for the agent fleet, enabling:
    - Lazy-loading of agent metadata (~100 tokens vs ~5K for full agents)
    - Fleet capability discovery and cross-delegation routing
    - Governance enforcement via cross-reference density signals
    - Automated handoff validation against actual downstream capabilities

Usage examples:
    # Print JSON manifest to stdout
    uv run python scripts/generate_agent_manifest.py

    # Write manifest to a file
    uv run python scripts/generate_agent_manifest.py --output .github/agents/manifest.json

    # Emit a Markdown table
    uv run python scripts/generate_agent_manifest.py --format markdown

    # Dry-run: list files that would be processed without generating output
    uv run python scripts/generate_agent_manifest.py --dry-run

    # Use a custom agents directory
    uv run python scripts/generate_agent_manifest.py --agents-dir path/to/agents/

Exit codes:
    0  Success
    1  Agents directory not found, or one or more files failed to parse

## Usage

```bash
    # Print JSON manifest to stdout
    uv run python scripts/generate_agent_manifest.py

    # Write manifest to a file
    uv run python scripts/generate_agent_manifest.py --output .github/agents/manifest.json

    # Emit a Markdown table
    uv run python scripts/generate_agent_manifest.py --format markdown

    # Dry-run: list files that would be processed without generating output
    uv run python scripts/generate_agent_manifest.py --dry-run

    # Use a custom agents directory
    uv run python scripts/generate_agent_manifest.py --agents-dir path/to/agents/
```

<!-- hash:8e926d26682499b8 -->
