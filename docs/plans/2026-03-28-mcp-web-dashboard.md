---
title: "MCP Web Dashboard — WebMCP Explorer"
date: 2026-03-28
branch: feat/mcp-web-dashboard
status: Active
governing_axiom: endogenous-first
milestone: "WebMCP"
closes_issues: []
---

# Workplan: MCP Web Dashboard — WebMCP Explorer

**Branch**: `feat/mcp-web-dashboard`
**Date**: 2026-03-28
**Governing axiom**: Endogenous-First — survey MCP Inspector upstream, existing corpus, and
Sprint 20 metrics output before any implementation
**Orchestrator**: Executive Orchestrator

---

## Objective

Build a local-first, Svelte-based web dashboard for dogmaMCP: a single-page application served
by a FastAPI sidecar process (`web/server.py`) that visualises both static snapshots and
real-time status of the MCP server's tool invocations, error rates, and latency metrics.
Positioned as the connective tissue that brings dogmaMCP together visually — and as a potential
OSS contribution to the MCP community if no adequate upstream inspector exists.

**This sprint is also framed as the foundation for WebMCP exploration** — a developer UX layer
that is IDE-agnostic and ultimately embeddable in IDEs (V2: VS Code webview; V3: inspector
protocol compatibility).

### Key Decisions Locked

| # | Decision |
|---|----------|
| Frontend | **Svelte** (repo root `web/`, Vite dev server) |
| Backend | **FastAPI sidecar** (`web/server.py`) — MCP stdio transport unchanged |
| Data | Real-time = SSE from sidecar; Static = pre-computed JSON from `docs/metrics/` |
| Interaction | **Read-only MVP**; interactive (manual E2E trigger) is deferred scope |
| IDE story | **MVP = browser URL** (`localhost:5173`); VS Code webview = V2 sprint |
| OSS gate | Research phase must survey MCP Inspector upstream before building anything |
| Isolation | `web/` is fully isolated — own `package.json`, own CI workflow (`web.yml`) |

### Architecture

```
MCP Server (stdio)
       │
       ↓ writes
.cache/mcp-metrics/metrics.json  ←— scripts/capture_mcp_metrics.py
       │
       ↓ reads
web/server.py  (FastAPI sidecar, localhost:8080)
  ├── GET /api/metrics          (snapshot JSON)
  ├── GET /api/metrics/stream   (SSE — real-time updates, configurable interval)
  └── GET /api/health           (server status + last metrics timestamp)
       │
       ↓ fetches
web/src/  (Svelte SPA, localhost:5173 via Vite dev)
  ├── Overview Tab   — summary cards + trend sparklines
  ├── Tools Tab      — per-tool breakdown table + latency histogram (click-to-expand)
  ├── Errors Tab     — error log, searchable/filterable by tool + date range
  └── Sidebar        — real-time panel: MCP server health, last 5 tool calls, refresh rate slider

scripts/start_dashboard.py      — single launcher for both processes
.vscode/tasks.json              — VS Code task: "Start MCP Dashboard"
```

---

## Phase Plan

### Phase 0 — Workplan Review ✅

**Agent**: Review
**Deliverables**: APPROVED verdict logged under `## Workplan Review Output` in scratchpad
**Depends on**: workplan committed
**Status**: ✅ Complete — APPROVED 2026-03-28

---

### Phase 1 — Research Sprint ⬜

**Agent**: Executive Researcher → Research Scout → Research Synthesizer
**Depends on**: Phase 0 APPROVED
**Rate-limit risk**: HIGH — three delegations; rest gap between A and B
**Status**: Not started

#### Delegation A — MCP Inspector + Upstream Survey (GATE for all implementation)

- Deep dive on [MCP Inspector](https://github.com/modelcontextprotocol/inspector): what it
  does, coverage gaps, license, extensibility
- Survey MCP ecosystem for any other dashboard/inspector tools
- **Key question**: build-on-top vs. build-alongside vs. build-from-scratch?
- Output: `docs/research/mcp-inspector-landscape.md` (Status: Final) + explicit
  build-vs-extend recommendation that gates Phase 2+

#### Delegation B — Svelte Ecosystem (gates implementation tech choices)

- SvelteKit vs. bare Svelte + Vite for a local dev server SPA (no SSR needed)
- Data viz libraries: LayerCake, Chart.js Svelte wrapper, D3 bindings, Recharts port —
  which fits best for latency histograms + sparklines on low-resource devices
- Key mental model shifts for React-background developers (reactivity model, stores vs
  context, Svelte component lifecycle vs React hooks)
- Output: `docs/research/svelte-ecosystem-for-webmcp.md` (Status: Final)

#### Delegation C — Observability UX Patterns

- Real-time vs static observability UX best practices — side-by-side coexistence patterns
- Dashboard layout patterns for developer tooling (tabs + stacked sidebar)
- MCP-centered data visualization patterns (tool invocation timelines, error waterfalls,
  latency percentile charts)
- Output: key decisions encoded back into Phase 3 scope in this workplan

#### Phase 1 Close: Knowledge Gap Identification

After all three delegations, Research Scout explicitly surfaces: *"What do we still not know
that would block implementation?"* — gaps logged in scratchpad under `## Knowledge Gaps`
before Phase 1 Review is requested.

### Phase 1 Review ⬜

**Agent**: Review
**Deliverables**: APPROVED verdict; build-vs-extend recommendation confirmed; tech stack locked
**Depends on**: Phase 1 deliverables committed
**Gate**: Phase 2 does not begin until APPROVED and build-vs-extend decision is recorded
**Status**: Not started

---

### Phase 2 — Architecture + Schema Design ⬜

**Agent**: Executive Scripter + Executive Docs
**Depends on**: Phase 1 Review APPROVED; build-vs-extend decision from Phase 1
**Status**: Not started

**Deliverables**:

- `web/` directory scaffold:
  - `package.json` (Svelte + Vite)
  - `.nvmrc` (Node version pin)
  - `web/README.md` (local developer guide)
- `web/server.py` FastAPI sidecar stub (endpoint signatures + docstrings; no logic yet)
- `data/mcp-metrics-schema.yml` extended with dashboard-facing fields (extend existing, do
  not replace)
- `scripts/start_dashboard.py` — launcher stub (starts sidecar + `npm run dev` in parallel)
- `.vscode/tasks.json` entry: **Start MCP Dashboard**
- `.github/workflows/web.yml` — CI stub: `npm install`, `npm run build`, `npm run check`
  (isolated from `tests.yml`)
- `docs/decisions/ADR-009-webmcp-architecture.md` — records build-vs-extend decision,
  sidecar pattern rationale, `web/` isolation strategy

### Phase 2 Review ⬜

**Agent**: Review
**Deliverables**: APPROVED; schema extension is backward-compatible; no Node/Python pipeline bleed
**Depends on**: Phase 2 deliverables committed
**Status**: Not started

---

### Phase 3 — Sidecar Implementation ⬜

**Agent**: Executive Scripter
**Depends on**: Phase 2 Review APPROVED
**Status**: Not started

**Deliverables**:

- `web/server.py` complete:
  - `GET /api/metrics` — reads `.cache/mcp-metrics/metrics.json`, returns snapshot
  - `GET /api/metrics/stream` — SSE, polls metrics file at configurable interval, pushes
    updates; graceful close on client disconnect
  - `GET /api/health` — returns `{"ok": bool, "last_updated": str, "tool_count": int}`
  - CORS configured for `localhost:5173`; no external origins permitted
- `tests/test_web_server.py` — pytest coverage ≥ 80%:
  - Mock metrics file reads
  - SSE stream yields updates
  - Health endpoint returns expected shape
  - CORS headers present on all routes
- `tests/fixtures/mcp-metrics-sample.json` — realistic sample fixture (all 12 tools
  represented)

### Phase 3 Review ⬜

**Agent**: Review
**Deliverables**: APPROVED; no hardcoded paths; CORS restricted to localhost; SSE closes cleanly
**Depends on**: Phase 3 deliverables committed
**Status**: Not started

---

### Phase 4 — Svelte Frontend Implementation ⬜

**Agent**: Executive Scripter (Svelte focus)
**Depends on**: Phase 3 Review APPROVED
**Status**: Not started

**Deliverables** (`web/src/`):

- `App.svelte` — root layout: top nav (health indicator + last-updated badge) + tabbed
  main area + stacked sidebar
- `lib/Overview.svelte` — summary cards (total invocations, error rate %, avg latency ms),
  trend sparklines (7-day if available, else session)
- `lib/Tools.svelte` — per-tool table: name | invocations | avg latency | error rate | last
  invoked | status badge (green/yellow/red); click row to expand latency histogram
- `lib/Errors.svelte` — error log list; search by tool name; filter by date range; expand
  row for message + error type
- `lib/Sidebar.svelte` — real-time panel: MCP server health indicator, last 5 tool calls
  with status icons, refresh rate slider (5s / 10s / 30s / paused)
- `lib/api.js` — fetch wrapper: `getSnapshot()` (REST), `subscribeStream(callback)` (SSE)
- **Offline fallback**: if sidecar unreachable on load, dashboard reads from a bundled
  sample JSON and displays a "Offline — showing cached data" banner
- Responsive layout: sidebar collapses at < 900px width

### Phase 4 Review ⬜

**Agent**: Review
**Deliverables**: APPROVED; all three tabs render with sample fixture; offline fallback confirmed;
no external CDN calls in production build
**Depends on**: Phase 4 deliverables committed
**Status**: Not started

---

### Phase 5 — Integration, Docs, CI ⬜

**Agent**: Executive Docs + CI Monitor
**Depends on**: Phase 4 Review APPROVED
**Status**: Not started

**Deliverables**:

- `docs/guides/mcp-dashboard.md` — setup guide: prerequisites (Python, Node), one-command
  start, how to read each tab, how to configure refresh interval
- `mcp_server/README.md` — cross-reference to dashboard guide
- `README.md` — "MCP Dashboard" section with quick-start (`scripts/start_dashboard.py`)
- `.github/workflows/web.yml` — finalised CI: lint + build + type-check (Svelte); fails PR
  if build breaks; isolated from `tests.yml`
- `web/README.md` — developer guide: how to add a new tab, how to extend the sidecar API

### Phase 5 Review ⬜

**Agent**: Review
**Deliverables**: APPROVED; CI workflow passes on branch; all docs cross-linked
**Depends on**: Phase 5 deliverables committed
**Status**: Not started

---

### Phase 6 — Session Close ⬜

**Agent**: GitHub
**Depends on**: Phase 5 Review APPROVED
**Status**: Not started

**Deliverables**:

- All changes pushed to `feat/mcp-web-dashboard`
- PR opened: `feat(web): MCP dashboard MVP — WebMCP Explorer`
- Fleet integration check run: `uv run python scripts/check_fleet_integration.py --dry-run`
- Session scratchpad archived; `## Session Summary` written

---

## Deferred Scope

| Scope | When |
|-------|------|
| Interactive — manual E2E test trigger from dashboard UI | V2 sprint |
| VS Code webview extension | V2 sprint |
| MCP Inspector protocol compatibility | Research output dependent |
| Historical metrics rolling window (> 7 days) | After sidecar stabilises |
| Multi-provider routing viz (local vs external model) | After `route_inference_request` metrics land |
| Authentication / multi-user | If/when dogma is deployed as a shared service |

---

## Acceptance Criteria

- [ ] `web/` directory exists with Svelte + Vite scaffold and isolated `package.json`
- [ ] `web/server.py` sidecar serves `/api/metrics` (snapshot) and `/api/metrics/stream` (SSE)
- [ ] `scripts/start_dashboard.py` starts both processes with a single command
- [ ] Dashboard loads at `localhost:5173` with sample fixture data
- [ ] Three tabs functional: Overview, Tools, Errors
- [ ] Sidebar shows real-time status with configurable refresh rate
- [ ] Offline fallback: dashboard loads from bundled JSON when sidecar unreachable
- [ ] `tests/test_web_server.py` passes at ≥ 80% coverage
- [ ] CORS restricted to `localhost:5173` only
- [ ] `web.yml` CI workflow passes (build + type-check)
- [ ] `docs/guides/mcp-dashboard.md` committed and cross-linked from `mcp_server/README.md`
- [ ] `docs/decisions/ADR-009-webmcp-architecture.md` committed with build-vs-extend decision
- [ ] PR open on `feat/mcp-web-dashboard`; CI green

## PR Description Template

```
feat(web): MCP dashboard MVP — WebMCP Explorer

Adds a Svelte + FastAPI sidecar dashboard for dogmaMCP telemetry.
Serves at localhost:5173. Start with: uv run python scripts/start_dashboard.py

- web/ — Svelte SPA (Overview, Tools, Errors tabs + real-time sidebar)
- web/server.py — FastAPI sidecar (REST snapshot + SSE real-time)
- scripts/start_dashboard.py — single launcher
- docs/decisions/ADR-009-webmcp-architecture.md
- docs/guides/mcp-dashboard.md
- .github/workflows/web.yml — isolated CI
```
