# `agent\_registry`

agent_registry.py
-----------------
Purpose:
    Enumerate all .github/agents/*.agent.md files, extract per-agent metadata
    (name, tier, tools, area, description, file), derive posture from the tools
    list, and expose a filterable, CLI-accessible registry.

Inputs:
    .github/agents/*.agent.md files with YAML frontmatter blocks.
    Optional: --agents-dir to override the default agents directory path.

Outputs:
    Markdown table or JSON array written to stdout (or --output file).
    Each entry contains: name, tier, area, posture, tools (list), file (path).
    Summary counts are not written; this script emits only the requested format.

Usage examples:
    # List all agents as a markdown table
    uv run python scripts/agent_registry.py --list

    # Filter by tool and print markdown table
    uv run python scripts/agent_registry.py --list --filter-tool terminal

    # Emit JSON array
    uv run python scripts/agent_registry.py --json

    # Filter by tier and write JSON to file
    uv run python scripts/agent_registry.py --json --filter-tier executive --output out.json

    # Filter by area
    uv run python scripts/agent_registry.py --list --filter-area research

Exit codes:
    0  Success (all discovered files parsed without error)
    1  Agents directory not found, or one or more files failed to parse

## Usage

```bash
    # List all agents as a markdown table
    uv run python scripts/agent_registry.py --list

    # Filter by tool and print markdown table
    uv run python scripts/agent_registry.py --list --filter-tool terminal

    # Emit JSON array
    uv run python scripts/agent_registry.py --json

    # Filter by tier and write JSON to file
    uv run python scripts/agent_registry.py --json --filter-tier executive --output out.json

    # Filter by area
    uv run python scripts/agent_registry.py --list --filter-area research
```

<!-- hash:78a0421a7990617d -->
