# Architecture Decisions

This document records key architectural choices for the EndogenAI Workflows project.

---

## MCP as Preferred Tool Layer

**Status**: Active  
**Decided**: Sprint 21 (March 2026)  
**Closes**: [#429](https://github.com/cagostino/dogma/issues/429)

### Decision

The Model Context Protocol (MCP) is the **preferred tool layer** for exposing governance tools, validation scripts, and codebase operations to AI agents (VS Code Copilot, Claude Desktop, Cursor, or any MCP client).

### Rationale

MCP provides four structural advantages over agent-specific tool implementations:

1. **Deterministic Discovery** — Tools are registered once in `mcp_server/dogma_server.py` and visible to all connected clients via `tools/list`. No per-agent tool enumeration or rediscovery required.

2. **Client-Agnostic** — The same tool definitions work across VS Code Copilot, Claude Desktop, Cursor, and any future MCP-compatible client. No vendor lock-in.

3. **Local-First Enforcement** — MCP servers run locally and enforce governance constraints (path validation, SSRF checks, rate limits) at the tool boundary, before any AI model sees the result. This instantiates [MANIFESTO.md § 3 Local Compute-First](../../MANIFESTO.md#3-local-compute-first).

4. **Programmatic Gate Layer** — MCP tools act as T4 enforcement points (runtime validation) in the governance stack. They complement T2 (text constraints in AGENTS.md) and T3 (pre-commit hooks) by providing runtime, parameterized validation that static linting cannot cover.

### When to Use MCP

Use MCP tools for:
- **Session-start checks** (`check_substrate` — run before any phase work begins)
- **Validation gates** (`validate_agent_file`, `validate_synthesis` — programmatic equivalents of CI checks)
- **Scaffolding operations** (`scaffold_agent`, `scaffold_workplan` — template instantiation)
- **Research operations** (`run_research_scout`, `query_docs` — fetch/cache external sources with SSRF guards)
- **Scratchpad management** (`prune_scratchpad` — initialise or inspect session state)

### When NOT to Use MCP

Do not use MCP for:
- **Simple file reads** — use VS Code's `read_file` tool directly
- **Commits and pushes** — use `git` commands in terminal; MCP is not a git replacement
- **Interactive user input** — MCP tools are synchronous; use VS Code's `ask_questions` tool for human-in-the-loop prompts

### Implementation

The canonical MCP server is defined in [`mcp_server/dogma_server.py`](../../mcp_server/dogma_server.py). Full setup instructions and tool catalog are in [`mcp_server/README.md`](../../mcp_server/README.md).

VS Code configuration: [`.vscode/mcp.json`](../../.vscode/mcp.json)

### Cross-References

- [AGENTS.md § MCP Toolset](../../AGENTS.md#mcp-toolset) — full tool catalog and session-start integration
- [MANIFESTO.md § 3 Local Compute-First](../../MANIFESTO.md#3-local-compute-first) — foundational axiom for local tool preference
- [mcp_server/README.md](../../mcp_server/README.md) — MCP server setup and tool catalog

---

## Future Decisions

This document will grow as additional architectural decisions are formalized. Candidate topics:
- Scratchpad persistence strategy (per-day files vs. compaction)
- Test marker taxonomy (`@pytest.mark.io`, `@pytest.mark.integration`, `@pytest.mark.slow`)
- Rate-limit gate placement (pre-delegation vs. per-tool invocation)
