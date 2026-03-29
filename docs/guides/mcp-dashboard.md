# MCP Dashboard

A browser observability dashboard for visualising MCP tool call telemetry from
`.cache/mcp-metrics/tool_calls.jsonl`.

---

## Prerequisites

- Python ≥ 3.11
- Node 20 (see `.nvmrc`)
- `uv` installed (`pip install uv` or `brew install uv`)
- `npm` installed (comes with Node 20)

---

## Quick Start

```bash
uv run python scripts/start_dashboard.py
```

Then open `http://localhost:5173` in your browser.

The command launches two processes:
- **Svelte SPA** — served by Vite at `http://localhost:5173`
- **FastAPI sidecar** — served at `http://localhost:8000` (endpoints: `/api/metrics`, `/api/metrics/stream`, `/api/health`)

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

Each row shows: invocation count, error count, average latency, last-called timestamp.

### Errors

Filtered view showing only tools with non-zero error counts. Use this tab to quickly
identify degraded tools without scanning the full Tools table.

---

## Sidebar

The sidebar provides real-time connection status:

| Badge | Meaning |
|-------|---------|
| `LIVE` | SSE stream connected; data updates in real time |
| `STALE` | Connection lost; last-received snapshot displayed |
| `ERROR` | Sidecar unreachable; offline fallback active |

**Refresh rate slider** — controls the polling cadence: 5s / 10s / 30s / paused.

---

## Offline Mode

When the sidecar at `http://localhost:8000` is unreachable, the dashboard automatically
loads the bundled fixture at `web/src/assets/fixture.json` and displays an
**"Offline — showing cached data"** banner.

No setup required — offline mode is automatic.

---

## Configuration

CORS is hardcoded to `localhost:5173` for local development. This is intentional for the
MVP: no external hosts can reach the sidecar API.

V2 will add `DOGMA_DASHBOARD_ORIGIN` environment variable support to override the default
(tracked in #506).

---

## Development

### Frontend (Vite hot reload)

```bash
cd web
npm run dev
```

Vite will serve the SPA with hot module replacement. The sidecar does **not** restart
automatically in this mode — start it separately:

```bash
uv run python scripts/start_dashboard.py
```

The `start_dashboard.py` script restarts both processes when run again.

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
