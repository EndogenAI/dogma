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
| Frontend | **Svelte** (repo root `web/`, Vite dev server — scaffold via `npm init vite web -- --template svelte`) |
| Backend | **FastAPI sidecar** (`web/server.py`) — MCP stdio transport unchanged |
| Data viz | **LayerCake** (~6 KB gzip, copy-paste components) — selected over svelte-chartjs (~62 KB Chart.js dependency) |
| Data | Real-time = SSE from sidecar; Static = pre-computed JSON from `.cache/mcp-metrics/metrics.json` |
| CORS | **Hardcoded** `allow_origins=["http://localhost:5173"]` for MVP; env-var escape hatch deferred to #506 (V2) |
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

### Phase 1 — Research Sprint (10-Step Model-Swap Cadence) ⬜

**Depends on**: Phase 0 APPROVED
**Rate-limit risk**: HIGH — multiple model swaps; deliberate pause points between substeps
**Status**: Not started

**Cadence**: Alternates between Sonnet 4.5 (scouting/execution) and Sonnet 4.6 High Reasoning
(synthesis/gap-detection/planning). Each substep pauses for human confirmation before proceeding.

---

#### Phase 1A — Initial Research Scouting ⬜
**Model**: Claude Sonnet 4.5
**Agent**: Research Scout
**Task**: Fetch and cache external sources:
  - MCP Inspector GitHub repo (README, architecture, license)
  - MCP ecosystem survey (npm packages, GitHub topics, Anthropic blog)
  - Svelte ecosystem: SvelteKit vs Vite, data viz libraries
  - Observability UX patterns (dashboards, real-time vs static)
**Output**: Raw findings appended to scratchpad under `## Phase 1A Output`
**Pause**: ✋ Human confirmation before Phase 1B

---

#### Phase 1B — Initial Gap Detection ⬜
**Model**: Claude Sonnet 4.6 High Reasoning
**Agent**: Research Synthesizer
**Task**: Analyze Phase 1A findings; identify knowledge gaps:
  - What's unclear about MCP Inspector extensibility?
  - Which Svelte data viz library is unvetted for low-resource devices?
  - What observability patterns are mentioned but not detailed?
**Output**: Gap list appended to scratchpad under `## Phase 1B Output — Knowledge Gaps`
**Pause**: ✋ Surface questions to human before Phase 1C

---

#### Phase 1C — Secondary Scouting ⬜
**Model**: Claude Sonnet 4.5
**Agent**: Research Scout
**Task**: Target fetch for Phase 1B gaps:
  - Deep dive MCP Inspector source code (src/ directory scan)
  - Benchmark reports for Svelte data viz libraries
  - Observability UX case studies (Grafana, Datadog, Honeycomb patterns)
**Output**: Secondary findings appended to scratchpad under `## Phase 1C Output`
**Pause**: ✋ Human confirmation before Phase 1D

---

#### Phase 1D — Initial Synthesis ⬜
**Model**: Claude Sonnet 4.6 High Reasoning
**Agent**: Research Synthesizer
**Task**: Synthesize Phases 1A + 1C into preliminary findings:
  - MCP Inspector: build-on-top vs. build-alongside recommendation (DRAFT)
  - Svelte stack: SvelteKit vs Vite + data viz library shortlist
  - Observability UX: real-time/static coexistence pattern candidates
**Output**: Draft synthesis appended to scratchpad under `## Phase 1D Output — Draft Findings`
**Pause**: ✋ Surface findings + open questions to human before Phase 1E

---

#### Phase 1E — Tertiary Gap Detection ⬜
**Model**: Claude Sonnet 4.6 High Reasoning
**Agent**: Research Synthesizer
**Task**: Review Phase 1D synthesis; identify final-round gaps:
  - Implementation blockers (license conflicts, architectural constraints)
  - Tech stack uncertainties (Svelte + FastAPI integration gotchas)
  - Deferred scope candidates (features to punt to V2)
**Output**: Final gap list appended to scratchpad under `## Phase 1E Output — Final Gaps`
**Pause**: ✋ Human confirmation of gap list before Phase 1F

---

#### Phase 1F — Tertiary Scouting ⬜
**Model**: Claude Sonnet 4.5
**Agent**: Research Scout
**Task**: Resolve Phase 1E final gaps:
  - License compatibility check (MCP Inspector MIT, dogma MIT)
  - Svelte + FastAPI CORS/SSE integration examples
  - V2 scope precedent from other MCP tooling
**Output**: Final findings appended to scratchpad under `## Phase 1F Output`
**Pause**: ✋ Human confirmation before Phase 1G

---

#### Phase 1G — Secondary Synthesis + Final Recommendations ⬜
**Model**: Claude Sonnet 4.6 High Reasoning
**Agent**: Research Synthesizer
**Task**: Produce final research outputs:
  - `docs/research/mcp-inspector-landscape.md` (Status: Final)
  - `docs/research/svelte-ecosystem-for-webmcp.md` (Status: Final)
  - Build-vs-extend decision (FINAL) that gates Phase 2+
  - Tech stack locked: Svelte + Vite, data viz library chosen, sidecar pattern confirmed
**Output**: Two committed research docs + decision record in scratchpad
**Pause**: ✋ Surface final recommendations to human before Phase 1H

---

#### Phase 1H — Recommendation Issue/Comment Creation ⬜
**Model**: Claude Sonnet 4.5
**Agent**: Executive PM
**Task**: Seed GitHub issues for deferred scope:
  - Interactive dashboard (manual E2E trigger) → new issue
  - VS Code webview extension → new issue
  - MCP Inspector protocol compatibility → new issue (if relevant)
**Output**: 2–3 new issues created; numbers logged in scratchpad
**Pause**: ✋ Human confirmation before Phase 1I

---

#### Phase 1I — Sprint Replanning + Workplan Update ⬜
**Model**: Claude Sonnet 4.6 High Reasoning
**Agent**: Executive Planner
**Task**: Update this workplan based on Phase 1G recommendations:
  - Adjust Phase 2–5 scope if build-on-top changes architecture
  - Lock tech stack decisions into Phase 2 deliverables
  - Update deferred scope table with new issue numbers from Phase 1H
  - Refine effort estimates if research surfaced complexity
**Output**: `docs/plans/2026-03-28-mcp-web-dashboard.md` updated and committed
**Pause**: ✋ Human approval of updated workplan before Phase 1J

---

#### Phase 1J — Phase 1 Review Gate ⬜
**Model**: Auto (Review agent)
**Agent**: Review
**Task**: Validate Phase 1 outputs:
  - Two research docs committed with Status: Final
  - Build-vs-extend decision explicitly recorded
  - Workplan updated and internally consistent
  - Deferred scope issues seeded
**Output**: APPROVED verdict logged under `## Phase 1 Review Output` in scratchpad
**Gate**: Phase 2 does not begin until APPROVED
**Status**: Not started



---

### Phase 2 — Architecture + Schema Design ✅

**Agent**: Executive Scripter + Executive Docs
**Depends on**: Phase 1 Review APPROVED; build-vs-extend decision from Phase 1
**Status**: ✅ Complete — commits `3e3303c`, `2dbce54`

**Deliverables**:

- `web/` directory scaffold:
  - `package.json` (scaffolded via `npm init vite web -- --template svelte && cd web && npm install`;
    do NOT use `sveltejs/template` — archived Feb 2023)
  - `.nvmrc` (Node version pin)
  - `web/README.md` (local developer guide)
- `web/server.py` FastAPI sidecar stub (endpoint signatures + docstrings; no logic yet)
- `data/mcp-metrics-schema.yml` extended with dashboard-facing fields (extend existing, do
  not replace)
- `scripts/start_dashboard.py` — launcher stub (starts sidecar + `npm run dev` in parallel)
- `.vscode/tasks.json` entry: **Start MCP Dashboard**
- `.github/workflows/web.yml` — CI stub: `npm install`, `npm run build`, `npm run check`
  (isolated from `tests.yml`)
- `docs/decisions/ADR-009-webmcp-architecture.md` — records build-alongside-Inspector decision
  AND all 7 locked technical decisions: LayerCake for data viz; `npm init vite --template svelte`
  scaffold; hardcoded `allow_origins=["http://localhost:5173"]` CORS; FastAPI `StreamingResponse`
  → browser `EventSource` for SSE; `activeTab` reactive variable (no routing library);
  LIVE → STALE → ERROR connection state machine; `web/src/assets/fixture.json` offline fallback

### Phase 2 Review ✅

**Agent**: Review
**Deliverables**: APPROVED; schema extension is backward-compatible; no Node/Python pipeline bleed
**Depends on**: Phase 2 deliverables committed
**Status**: ✅ Complete — APPROVED after 1 fix cycle

---

### Phase 3 — Sidecar Implementation ✅

**Agent**: Executive Scripter
**Depends on**: Phase 2 Review APPROVED
**Status**: ✅ Complete — commit `37839a7`

**Deliverables**:

- `web/server.py` complete:
  - `GET /api/metrics` — reads `.cache/mcp-metrics/metrics.json`, returns snapshot
  - `GET /api/metrics/stream` — SSE via `fastapi.responses.StreamingResponse` with
    `media_type="text/event-stream"`; polls metrics file at configurable interval, pushes
    updates; graceful close on client disconnect
  - `GET /api/health` — returns `{"ok": bool, "last_updated": str, "tool_count": int}`
  - CORS hardcoded: `allow_origins=["http://localhost:5173"]`; no external origins permitted;
    inline comment `# TODO(v2): read CORS_ALLOWED_ORIGINS from env (#506)`
- `tests/test_web_server.py` — pytest coverage ≥ 80%:
  - Mock metrics file reads
  - SSE stream yields updates
  - Health endpoint returns expected shape
  - CORS headers present on all routes
- `tests/fixtures/mcp-metrics-sample.json` — pytest server mock fixture (all 12 tools represented)
- `web/src/assets/fixture.json` — offline fallback fixture (all 12 tools represented); loaded by
  `api.js` via static Vite `import` before first successful SSE connection

### Phase 3 Review ✅

**Agent**: Review
**Deliverables**: APPROVED; no hardcoded paths; CORS restricted to localhost; SSE closes cleanly
**Depends on**: Phase 3 deliverables committed
**Status**: ✅ Complete — APPROVED

---

### Phase 4 — Svelte Frontend Implementation ✅

**Agent**: Executive Scripter (Svelte focus)
**Depends on**: Phase 3 Review APPROVED
**Status**: ✅ Complete — commits `50d92f6` (UI) + `64456e3` (.gitignore fix)

**Deliverables** (`web/src/`):

- `App.svelte` — root layout: top nav (health indicator + last-updated badge) + tabbed main
  area + stacked sidebar; tab switching via `let activeTab = 'overview'` reactive variable;
  no routing library; no SvelteKit router
- `lib/Overview.svelte` — summary cards (total invocations, error rate %, avg latency ms),
  trend sparklines (7-day if available, else session); sparklines rendered via LayerCake
  (install `layercake`; copy chart component to `web/src/charts/`); do NOT install
  `svelte-chartjs` or `chart.js`
- `lib/Tools.svelte` — per-tool table: name | invocations | avg latency | error rate | last
  invoked | status badge (green/yellow/red); click row to expand latency histogram rendered
  via LayerCake; do NOT install `svelte-chartjs` or `chart.js`
- `lib/Errors.svelte` — error log list; search by tool name; filter by date range; expand
  row for message + error type
- `lib/Sidebar.svelte` — real-time panel implementing LIVE → STALE → ERROR connection state
  machine: `LIVE` (green dot) on `EventSource.onopen`; `STALE` (amber + 'Last updated X min ago')
  on `EventSource.onerror`; exponential backoff reconnect 2 s → 4 s → 8 s, cap 30 s; successful
  reconnect resets to LIVE; connection exhaustion renders ERROR state; last 5 tool calls with
  status icons; refresh rate slider (5s / 10s / 30s / paused)
- `lib/api.js` — fetch wrapper: `getSnapshot()` (REST), `subscribeStream(callback)` (SSE via
  browser-native `EventSource`; no frontend SSE library needed); `getSnapshot()` falls back to
  `import fixture from '../assets/fixture.json'` before first successful connection; displays
  'Offline — showing cached data' banner when fallback is active
- Responsive layout: sidebar collapses at < 900px width

### Phase 4 Review ✅

**Agent**: Review
**Deliverables**: APPROVED; all three tabs render with sample fixture; offline fallback confirmed;
no external CDN calls in production build
**Depends on**: Phase 4 deliverables committed
**Status**: ✅ Complete — APPROVED

---

### Phase 5 — Integration, Docs, CI ✅

**Agent**: Executive Docs + CI Monitor
**Depends on**: Phase 4 Review APPROVED
**Status**: ✅ Complete — commit `5f228ae`

**Deliverables**:

- `docs/guides/mcp-dashboard.md` ✅ — setup guide committed
- `mcp_server/README.md` ✅ — MCP Dashboard cross-reference added
- `README.md` ✅ — MCP Dashboard section with quick-start added
- `.github/workflows/web.yml` ✅ — **already finalised in Phase 2** (npm install + build + check); no further changes required
- `web/README.md` ✅ — Extending the Dashboard section (add tab + sidecar API) added

### Phase 5 Review ✅

**Agent**: Review
**Deliverables**: APPROVED; CI workflow passes on branch; all docs cross-linked
**Depends on**: Phase 5 deliverables committed
**Status**: ✅ Complete — APPROVED (after workplan Phase 5 status fix)

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
| MCP Inspector protocol compatibility | #505 (V2 sprint) |
| CORS environment variable for production deployments | #506 (V2 sprint) |
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
