# `check\_problems\_panel`

Check and count all VS Code Problems panel diagnostic sources in this repo.

Provides the authoritative baseline count for each diagnostic category generated
by the agent/skill file fleet. Replaces ad-hoc grep for error counting.

Categories audited:
  A — `Attribute 'governs' is not supported`  (Copilot Chat prompts-diagnostics-provider)
      Source: any `governs:` key in .agent.md / SKILL.md YAML frontmatter.
      Fix:    rename governs: → x-governs: (issue #390)

  B — `Unknown tool 'X'`  (Copilot Chat MCP tool static validation)
      Source: tool references in `tools:` frontmatter whose namespaces are not
              known built-ins and not MCP server names from .vscode/mcp.json.
      Fix:    remove inactive extension tool refs from tools: lists.

Usage:
    uv run python scripts/check_problems_panel.py          # full audit + counts
    uv run python scripts/check_problems_panel.py --json   # machine-readable JSON

Exit codes:
    0 — no diagnostic sources found
    1 — diagnostic sources present (counts printed to stdout)
    2 — I/O or parse error

## Usage

```bash
    uv run python scripts/check_problems_panel.py          # full audit + counts
    uv run python scripts/check_problems_panel.py --json   # machine-readable JSON
```

<!-- hash:65917a5930cfdf9a -->
