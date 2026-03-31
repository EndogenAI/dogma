# WebMCP Integration Guide

This guide documents the dogma project's WebMCP adoption strategy and current integration state. WebMCP (announced March 2026) enables turning any Chrome web page into an MCP server, allowing AI agents to interact with web-based UIs and data as structured MCP tools.

---

## Adopted Strategy (rec-webmcp-003)

Phase adoptions are gated by a **read-only first** principle:

**Phase 1 (Pilot — adopted)**:
- CSS selectors for page content extraction
- Page state queries and metadata retrieval
- **No** interactive capabilities (form submission, button clicks) until Security review

**Phase 2 (Gated Interactive — deferred)**:
- Form submission and button clicks
- Restricted to Executive Researcher role only
- Requires explicit human review before each interaction

Governance source: [webmcp-browser-integration-feasibility.md](../research/webmcp-browser-integration-feasibility.md) (rec-webmcp-003).

---

## Current Integration State

The dogma project ships a **local MCP web dashboard** (`web/`) that serves as the pilot substrate for read-only browser tooling:

- `mcp_server/tools/` — MCP tools exposed to browser-side agents
- `web/server.py` — FastAPI sidecar with CORS configured via `WEBMCP_CORS_ORIGINS` env var
- `.vscode/mcp.json` — MCP client configuration for VS Code
- `scripts/start_dashboard.py` — launch script for the dashboard

The `mcp_dogma-browser_*` tools (e.g., `get_component_state`, `query_dom`, `get_console_logs`) provide read-only access to the running dashboard page. Interactive tools are explicitly excluded pending Phase 2 governance review.

---

## Governance Gates

All browser tool access must pass through:

1. **`capability_gate.py`** — tool-level allow/deny list for `browser_read` vs. interactive tools
2. **`.mcp.json` restrictions** — MCP client config limits which tools are exposed
3. **Security review** before enabling any form-submission or click-action tools

---

## Related Issues

- Closed: [#430 WebMCP read-only browser tools pilot strategy](https://github.com/conorluddy/dogma/issues/430) — strategy adopted
- Closed: [#506 CORS Environment Variable for Production Deployments](https://github.com/conorluddy/dogma/issues/506) — implemented via `WEBMCP_CORS_ORIGINS`
- Closed: [#417 MCP viability](https://github.com/conorluddy/dogma/issues/417) — MCP confirmed active
- Open: Phase 2 interactive capabilities (to be opened after WebMCP full public release + security review)

---

## Setup

```bash
# Start the MCP dashboard (default: localhost:8000 frontend, localhost:5173 dev)
uv run --extra web python scripts/start_dashboard.py

# Override CORS for non-localhost deployments
WEBMCP_CORS_ORIGINS="https://your-host.example.com" uv run --extra web python scripts/start_dashboard.py
```

See [`mcp_server/README.md`](../../mcp_server/README.md) for full MCP server setup and prerequisites.
