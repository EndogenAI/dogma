---
title: Svelte Ecosystem Selection for dogmaMCP Web Dashboard
status: Final
research_issue: 0
closes_issue: 0
date: 2026-03-28
sources:
  - https://layercake.graphics
  - https://www.npmjs.com/package/svelte-chartjs
  - https://www.npmjs.com/package/chart.js
  - https://vitejs.dev/guide
  - https://fastapi.tiangolo.com/advanced/custom-response
  - https://github.com/sveltejs/template
  - data/mcp-metrics-schema.yml
  - scripts/capture_mcp_metrics.py
  - mcp_server/dogma_server.py
recommendations:
  - id: R1
    title: Use LayerCake for all data visualisation
    status: accepted-for-adoption
    linked_issue: ""
  - id: R2
    title: Scaffold with npm init vite selecting the svelte template
    status: accepted-for-adoption
    linked_issue: ""
  - id: R3
    title: FastAPI sidecar SSE with CORS locked to localhost:5173 for MVP
    status: accepted-for-adoption
    linked_issue: ""
  - id: R4
    title: Implement Live/Stale reactive state machine for SSE connection health
    status: accepted-for-adoption
    linked_issue: ""
  - id: R5
    title: Use activeTab reactive variable for tab navigation; no routing library
    status: accepted-for-adoption
    linked_issue: ""
---

# Svelte Ecosystem Selection for dogmaMCP Web Dashboard

## Executive Summary

Phase 1 surveyed the Svelte/Vite toolchain, data visualisation options, and FastAPI
SSE integration pattern for the dogmaMCP web dashboard. LayerCake (~6 KB gzip, copy-paste
components) wins over svelte-chartjs (~62 KB Chart.js peer dependency) by 56 KB — nearly double
the 30 KB threshold. The correct scaffold is `npm init vite` with the svelte template; the
`sveltejs/template` repository was archived in February 2023 and must not be used. FastAPI's
`StreamingResponse` drives the real-time invocation feed via SSE; a separate REST
`GET /snapshot` endpoint drives tab-level metrics aggregates. A Live/Stale reactive state machine
governs connection health visibility.

## Hypothesis Validation

**Expected**: svelte-chartjs would be the natural charting choice via Chart.js familiarity;
SvelteKit might offer useful structure; `sveltejs/template` would be the scaffold entry point.

**Found**:

- **svelte-chartjs disqualified by bundle weight.** 57.3 kB unpacked, plus a ~62 KB Chart.js
  peer dependency, versus LayerCake's ~6 KB. For a governance tool running on developer
  laptops (Local Compute-First, [MANIFESTO.md §3](../../MANIFESTO.md)), shipping the full
  Chart.js runtime for sparklines and line charts is unjustifiable. The 56 KB delta exceeds the
  30 KB budget threshold by 87%.
- **SvelteKit disqualified by unnecessary complexity.** SSR, file-based routing, and adapter
  configuration are overhead for an MVP with two tabs. A reactive `activeTab` variable is
  sufficient and eliminates the framework surface entirely.
- **`sveltejs/template` is a known footgun.** The repository was archived February 2023. Using
  it produces deprecated boilerplate with no upgrade path. The active scaffold path is
  `npm init vite`.
- **FastAPI SSE + REST coexistence confirmed viable.** SSE drives the append-only invocation
  feed; REST `GET /snapshot` serves pre-aggregated metrics on a 30s poll. These are independent
  data paths and must not be merged.

**Verdict**: All four hypotheses revised. LayerCake, Vite scaffold, SSE/REST separation, and
`activeTab` nav are confirmed as the correct implementation choices.

## Pattern Catalog

**Canonical example: LayerCake copy-paste chart component lifecycle**

LayerCake components live in the consuming project — they are not imported from a package at
runtime. The workflow is:

```bash
npm install layercake
# Copy components into src/charts/
# e.g. src/charts/Line.svelte, src/charts/LatencyHistogram.svelte
```

Inside a Svelte page:

```svelte
<script>
  import LayerCake from 'layercake';
  import Svg from 'layercake/layouts/Svg.svelte';
  import Line from './charts/Line.svelte';
</script>

<LayerCake data={latencySeries} x="ts" y="p95">
  <Svg>
    <Line />
  </Svg>
</LayerCake>
```

The chart component (`Line.svelte`) is owned by the project. It can be modified freely — there
is no upstream package API to remain compatible with. This directly implements Endogenous-First
([MANIFESTO.md §1](../../MANIFESTO.md)): visualisation logic becomes part of the dogma
codebase, visible and auditable, not a transient runtime dependency.

---

**Canonical example: FastAPI SSE + Svelte EventSource integration with CORS**

FastAPI side (`web/server.py`):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # TODO(v2): read CORS_ALLOWED_ORIGINS from env
    allow_methods=["GET"],
)

async def event_generator(queue):
    while True:
        event = await queue.get()
        yield f"data: {json.dumps(event)}\n\n"

@app.get("/events")
async def stream():
    return StreamingResponse(event_generator(shared_queue), media_type="text/event-stream")
```

Svelte side (`web/src/lib/InvocationFeed.svelte`):

```svelte
<script>
  import { onMount, onDestroy } from 'svelte';

  let events = [];
  let source;
  let status = 'CONNECTING';

  onMount(() => {
    connect();
  });

  function connect(delay = 0) {
    setTimeout(() => {
      source = new EventSource('/events');
      source.onopen = () => { status = 'LIVE'; };
      source.onmessage = (e) => {
        events = [...events.slice(-49), JSON.parse(e.data)];
      };
      source.onerror = () => {
        status = 'STALE';
        source.close();
        connect(Math.min((delay || 2000) * 2, 30000));  // 2s → 4s → 8s, cap 30s
      };
    }, delay);
  }

  onDestroy(() => source?.close());
</script>
```

The `CORSMiddleware` `allow_origins` must explicitly list `http://localhost:5173`. Without it,
`EventSource` fails silently as a network error — not an SSE error — making it the hardest
integration failure mode to diagnose.

---

**Anti-pattern: Using svelte-chartjs when only sparklines and line charts are needed**

svelte-chartjs is a thin wrapper over Chart.js. Installing it ships the full Chart.js runtime
(~62 KB gzip), which includes every chart type — radar, bubble, polar area, doughnut — none of
which the dogmaMCP dashboard needs. Chart.js is nominally tree-shakeable, but its runtime core
is not eliminable. LayerCake produces zero additional runtime; chart code compiles to Svelte's
output. For a governance tool optimised for developer laptop performance (Local Compute-First,
[MANIFESTO.md §3](../../MANIFESTO.md)), the 56 KB penalty for svelte-chartjs has no offsetting
benefit.

---

**Anti-pattern: Merging SSE event stream and REST snapshot into a single data path**

Attempting to drive both the real-time invocation feed and the Overview tab metrics aggregates
from a single SSE stream requires the backend to compute running aggregates on every event,
pushes state management complexity to the frontend, and creates a single point of failure: a
stream disconnect freezes the entire UI simultaneously. The correct architecture separates
concerns. SSE is append-only (the raw event log). REST `GET /snapshot` serves
pre-aggregated metrics (P95 latency, error rate, tool call counts) on a 30s poll. The separation
means the Overview tab degrades gracefully — stale aggregate with a timestamp — independently
of the live invocation feed. Both paths are driven by the same OTel metrics persisted via
`scripts/capture_mcp_metrics.py`; they differ only in query pattern and update frequency.

## Recommendations

1. **Use LayerCake for all data visualisation** — Copy components into `web/src/charts/`. Do
   not install svelte-chartjs or chart.js. Rationale: 56 KB bundle saving; components are
   endogenous and auditable; SSR-compatible for V2 without architectural change.

2. **Scaffold with `npm init vite` selecting the svelte template** — Run:
   `npm init vite web -- --template svelte && cd web && npm install`.
   Do not use `sveltejs/template` (archived February 2023). Rationale: Vite is the current
   canonical path; the archived template is an active footgun that produces unupgradeable
   boilerplate.

3. **FastAPI sidecar SSE with CORS locked to localhost:5173 for MVP** — Hardcode
   `allow_origins=["http://localhost:5173"]` in `CORSMiddleware`. Add inline comment
   `TODO(v2): read CORS_ALLOWED_ORIGINS from env`. Rationale: The silent CORS failure mode on
   `EventSource` is the highest-probability integration blocker; making the MVP origin explicit
   eliminates it at zero cost.

4. **Implement Live/Stale reactive state machine** — States: `CONNECTING → LIVE` (green dot)
   `→ STALE` (amber indicator + "Last updated X min ago") `→ retry` (exponential backoff:
   2s → 4s → 8s, cap 30s). Rationale: Silent stale data violates the observability contract.
   Operators need visible confirmation that the feed is live before trusting metrics.

5. **Use `activeTab` reactive variable; no routing library** — A single
   `let activeTab = 'overview'` in `App.svelte`, toggled by tab bar click handlers. No
   SvelteKit, no client-side router. Rationale: Three tabs do not justify a router. SvelteKit
   introduces SSR, adapters, and build configuration overhead that the MVP does not need and
   that contradicts Local Compute-First ([MANIFESTO.md §3](../../MANIFESTO.md)).

## Sources

1. `https://layercake.graphics` — LayerCake official documentation; headless Svelte-native
   graphics framework; ~6 KB gzip; copy-paste component model; full SSR support.
2. `https://www.npmjs.com/package/svelte-chartjs` — 57.3 kB unpacked; Chart.js peer
   dependency required; ~62 KB gzip total; disqualified on bundle weight.
3. `https://www.npmjs.com/package/chart.js` — Chart.js peer dep of svelte-chartjs; full
   runtime including unused chart types; not tree-shaked to zero for MVP use case.
4. `https://vitejs.dev/guide` — Vite scaffold docs; `npm init vite` with svelte template
   confirmed active and maintained.
5. `https://fastapi.tiangolo.com/advanced/custom-response` — FastAPI `StreamingResponse`
   pattern for `text/event-stream`; keepalive comment syntax; CORS middleware configuration.
6. `https://github.com/sveltejs/template` — Official Svelte template repository; archived
   February 2023; deprecated; must not be used as scaffold.
7. `data/mcp-metrics-schema.yml` — dogma metrics schema; governs fields consumed by Overview
   tab; read at implementation start; pin consumed fields; V2 for versioning strategy.
8. `scripts/capture_mcp_metrics.py` — Produces `.cache/mcp-metrics/metrics.json`; 8 tools ×
   100 samples; primary data source for MVP dashboard.
9. `mcp_server/dogma_server.py` — OTel semconv attributes in use: `gen_ai.operation.name`,
   `gen_ai.tool.name`, `error.type`, `mcp.server.operation.duration`; confirms upstream data
   contract for SSE event schema.
