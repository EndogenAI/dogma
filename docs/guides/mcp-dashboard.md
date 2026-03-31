# MCP Dashboard

A browser observability dashboard for visualising MCP tool call telemetry from
`.cache/mcp-metrics/tool_calls.jsonl`.

---

## Prerequisites

- Python ≥ 3.10
- Node 20 (see `.nvmrc`)
- `uv` installed (`pip install uv` or `brew install uv`)
- `npm` installed (comes with Node 20)

---

## Quick Start

```bash
uv sync --extra web
uv run --extra web python scripts/start_dashboard.py
```

Then open `http://localhost:5173` in your browser.

The command launches two processes:
- **Svelte SPA** — served by Vite at `http://localhost:5173`
- **FastAPI sidecar** — served at `http://localhost:8000` (endpoints: `/api/metrics`, `/api/metrics/stream`, `/api/health`)

## VS Code MCP Client Status (Phase 4)

Phase 4 evaluated whether VS Code Copilot can connect to a browser MCP inspector
server through `.vscode/mcp.json` at runtime.

Result:
- VS Code MCP config supports local HTTP server entries.
- The current dashboard runtime does **not** expose an MCP transport endpoint
  (`/mcp` / `/mcp/handshake`) from the FastAPI sidecar.
- `query_dom` exists in `web/src/lib/mcp-server.ts`, but it is currently
  browser-local logic and is not exported over a network MCP endpoint.

Workaround path (until browser MCP transport is exposed):
1. Start dashboard: `uv run --extra web python scripts/start_dashboard.py`
2. Verify sidecar health: `curl -sf http://127.0.0.1:8000/api/health`
3. Verify missing MCP endpoint signal:
   - `curl -i http://127.0.0.1:8000/mcp/handshake` (expected: `404`)
4. In VS Code Copilot Chat, use the existing `dogma-governance` MCP server for
   repository tools; do not expect `query_dom` to appear until `/mcp` is
   implemented as a real MCP transport endpoint.

Manual verification note for `query_dom` from Copilot:
- The current dashboard runtime exposes an MCP HTTP transport endpoint
  (`/mcp` / `/mcp/handshake`) from the FastAPI sidecar.
- `query_dom` exists in `web/src/lib/mcp-server.ts` and can be reached by MCP
  clients via this HTTP bridge when configured in `.vscode/mcp.json`.

Verification path (with browser MCP transport exposed):
1. Start dashboard: `uv run --extra web python scripts/start_dashboard.py`
2. Verify sidecar health: `curl -sf http://127.0.0.1:8000/api/health`
3. Verify MCP handshake succeeds:
   - `curl -i http://127.0.0.1:8000/mcp/handshake` (expected: `200` with MCP
     handshake JSON payload)
4. In VS Code Copilot Chat, configure a `.vscode/mcp.json` HTTP server entry
   pointing to `http://127.0.0.1:8000/mcp` and expect `query_dom` to appear as
   an available MCP tool.

Manual verification note for `query_dom` from Copilot:
- Current expected outcome is a successful tool invocation via the MCP HTTP
  bridge.
- With `.vscode/mcp.json` configured to point to the dashboard MCP endpoint,
  test from Copilot: `Call query_dom with selector ".app-title"`.

## Data Source

The dashboard reads from `.cache/mcp-metrics/tool_calls.jsonl`.

- Records with `"source": "live"` are written by the instrumented MCP server
- Records with `"source": "synthetic"` are seed data

For the migration procedure, see [mcp_server/README.md#live-trace-capture](../../mcp_server/README.md#live-trace-capture).
For design rationale, see [docs/research/mcp-live-trace-design.md](../research/mcp-live-trace-design.md).

---

## Understanding the Tabs

### Overview

Aggregated statistics across all 8 canonical MCP tools:

- Total invocations
- Overall error rate (%)
- Average latency (ms)

### Tools

Per-tool breakdown for each of the 8 tracked tools:
`check_substrate`, `validate_agent_file`, `validate_synthesis`, `scaffold_agent`,
`scaffold_workplan`, `run_research_scout`, `query_docs`, `prune_scratchpad`.

Each row shows: invocation count, error count, average latency, and p95 latency.

### Errors

Filtered view showing only tools with non-zero error counts. Use this tab to quickly
identify degraded tools without scanning the full Tools table.

> **Note**: Before the live JSONL capture migration (`uv run python scripts/migrate_tool_calls.py`), the Errors tab may show "no timestamp" because the 800 synthetic seed records lack a `timestamp_utc` field. After running the migration and triggering one real tool call, the Errors tab will show real ISO-8601 timestamps and `error_type` values.

---

## Sidebar

The sidebar provides real-time connection status:

| Badge | Meaning |
|-------|---------|
| `LIVE` | SSE stream connected; data updates in real time |
| `STALE` | Connection lost; last-received snapshot displayed |
| `ERROR` | Sidecar unreachable; offline fallback active |

**Polling interval buttons** — control REST polling cadence: 5s / 10s / 30s / paused.
SSE updates remain live while connected.

---

## Offline Mode

When the sidecar at `http://localhost:8000` is unreachable, the dashboard automatically
loads the bundled fixture at `web/src/assets/fixture.json` and displays an
**"Offline — showing cached data"** banner.

No setup required — offline mode is automatic.

---

## Configuration

### CORS Origins (Production Deployment)

By default, the FastAPI sidecar allows requests only from `http://localhost:5173` (the local Vite dev server).

For production deployments where the frontend is served from a different origin, set the `WEBMCP_CORS_ORIGINS` environment variable:

```bash
# Single origin
export WEBMCP_CORS_ORIGINS="https://dashboard.example.com"
uv run --extra web python scripts/start_dashboard.py

# Multiple origins (comma-separated)
export WEBMCP_CORS_ORIGINS="http://example.com:5173,https://other.com"
uv run --extra web python scripts/start_dashboard.py
```

**⚠️ Security Warning**: Only set `WEBMCP_CORS_ORIGINS` if you understand CORS security implications. Allowing arbitrary origins can expose your MCP metrics to unauthorized clients. Always use specific, trusted origins — never use wildcards (`*`) in production.

**Default behavior**: If `WEBMCP_CORS_ORIGINS` is not set, the sidecar defaults to `http://localhost:5173` (no behavior change for local development).

---

## Development

### Development mode (recommended — hot reload for both frontend and sidecar)

Use the `--development` / `-d` flag to run both the Vite frontend (HMR always active) and
the FastAPI sidecar with `uvicorn --reload` (auto-restarts on Python file changes):

```bash
uv run --extra web python scripts/start_dashboard.py --development
# or
uv run --extra web python scripts/start_dashboard.py -d
```

This is the recommended workflow for iterating on `web/server.py` or the Svelte source.

### Manual sidecar + frontend (separate terminals)

If you need independent control of each process:

```bash
# Terminal 1 — sidecar with hot reload
uv run --extra web python -m uvicorn web.server:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Vite dev server (HMR always active)
cd web
npm run dev
```

### Quality checks

```bash
cd web
npm run check   # Svelte type check
npm run build   # Production build
```

---

## See Also

- [docs/decisions/ADR-009-webmcp-architecture.md](../decisions/ADR-009-webmcp-architecture.md) — architecture decision record for the SPA + FastAPI sidecar design
- [web/README.md](../../web/README.md) — developer guide for extending tabs and the sidecar API
- [mcp_server/README.md](../../mcp_server/README.md) — full MCP server tool reference
