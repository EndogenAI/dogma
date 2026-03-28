---
title: MCP Inspector Landscape and Build-vs-Extend Decision
status: Final
research_issue: 0
closes_issue: 0
date: 2026-03-28
sources:
  - https://github.com/modelcontextprotocol/inspector
  - https://www.npmjs.com/package/@modelcontextprotocol/inspector
  - https://www.npmjs.com/package/@modelcontextprotocol/sdk
  - https://www.npmjs.com/package/@modelcontextprotocol/ext-apps
  - mcp_server/dogma_server.py
  - data/mcp-metrics-schema.yml
recommendations:
  - id: R1
    title: Build-alongside Inspector; do not fork or extend
    status: accepted-for-adoption
    linked_issue: ""
  - id: R2
    title: Reference Inspector proxy bridge as conceptual input only
    status: accepted-for-adoption
    linked_issue: ""
  - id: R3
    title: Seed a GitHub issue for Inspector protocol compatibility as V2 scope
    status: accepted-for-adoption
    linked_issue: ""
---

# MCP Inspector Landscape and Build-vs-Extend Decision

## Executive Summary

This research asked whether the MCP Inspector or any existing `@modelcontextprotocol` npm
package could serve as a foundation for the dogmaMCP observability dashboard. Phase 1 found
that the Inspector is an interactive testing tool — write-capable, form-driven, and structurally
orthogonal to a read-only metrics dashboard. No existing MCP npm package addresses production
observability. The dogmaMCP dashboard is a novel use case; the correct posture is
**build-alongside**: an independent Svelte SPA consuming dogma's existing OTel metrics stream,
with no code dependency on the Inspector.

## Hypothesis Validation

**Expected**: The MCP Inspector might be extendable or forkable as a protocol-fluent foundation,
providing an existing connection layer between the UI and the MCP server.

**Found**: The Inspector is disqualified by use-case mismatch, not technical inadequacy. It is
explicitly interactive — it invokes tools, reads resources, and conducts sampling. It is
write-capable by design. The `@modelcontextprotocol/ext-apps` package (3.9M downloads) similarly
targets interactive UIs, not observability. The 616K-download `inspector` package is a REPL for
MCP protocol development, not a metrics aggregation substrate. Searching the MCP npm namespace
found no read-only dashboard or observability package.

**Verdict: Hypothesis disconfirmed.** Fork and extend are not viable postures. Build-alongside
is the correct decision.

## Pattern Catalog

**Canonical example: Inspector interactive test workflow vs. dogmaMCP observability workflow**

The MCP Inspector operates as a developer REPL:

1. Developer opens the React UI
2. Developer selects a tool from the server's registered tool list
3. Developer fills an input form and submits — the Node.js proxy bridge translates this to
   a `tools/call` MCP message over stdio, SSE, or streamable-http
4. The server's response is rendered inline

This is an agent-driven, write-capable, synchronous request-response loop.

The dogmaMCP dashboard operates as a passive observer:

1. Dashboard connects to FastAPI SSE endpoint
2. OTel-instrumented tool invocations emit events via `_run_with_mcp_telemetry` in
   `mcp_server/dogma_server.py`
3. Events accumulate in a bounded frontend buffer; latency and error metrics render
   continuously without user interaction

These workflows are structurally orthogonal: Inspector is `agent → server` (write); the
dogmaMCP dashboard is `server → observer` (read). They share only the concept of the proxy
bridge as a protocol translation layer — a conceptual reference applicable to V2 live-connection
features, not shared code.

**Anti-pattern: Forking an interactive debug tool to build a production observability dashboard**

Forking MCP Inspector to produce the dogmaMCP dashboard would:

- Inherit React and Node.js dependencies into a Svelte/FastAPI stack, creating a permanent
  cross-framework maintenance boundary
- Couple dashboard evolution to Inspector's upstream protocol API changes — any refactor of
  the proxy bridge or tool-invocation flow affects the fork
- Require stripping write-capable features (sampling, resource reads, tool invocation forms)
  that are load-bearing in the Inspector codebase and not cleanly separable
- Violate Minimal Posture ([MANIFESTO.md §1](../../MANIFESTO.md)): the fork ships interactive
  write capabilities that the governance tool must never expose

The failure mode is tool-repurposing debt. Inspector is a well-maintained interactive test
harness; inheriting it to build an observability dashboard produces two incompatible products
under one module boundary. The correct response to "does a partial overlap exist?" is not
"fork and strip" but "build clean and reference."

## Recommendations

1. **Build-alongside Inspector** — Implement `web/` as an independent Svelte SPA consuming
   `mcp_server/dogma_server.py`'s OTel metrics via FastAPI SSE. Import no
   `@modelcontextprotocol/inspector` code. Rationale: Inspector is write-capable and React-based;
   inheriting it costs more than building a focused, read-only dashboard from scratch.

2. **Reference Inspector's proxy bridge conceptually only** — The Node.js proxy bridge
   (protocol translation between UI and MCP server over stdio/SSE/streamable-http) is a useful
   architectural reference for any V2 live-connection or protocol introspection feature. For MVP,
   FastAPI SSE is the connection layer; protocol translation is out of scope. Rationale:
   Algorithms-Before-Tokens ([MANIFESTO.md §2](../../MANIFESTO.md)) — encode the V2 reference
   as a tracked issue, not as partial code in the MVP.

3. **Seed a GitHub issue for Inspector protocol compatibility (V2 scope)** — Track the question
   of whether the dashboard should eventually connect to the MCP server directly for live
   protocol introspection, reusing the proxy bridge concept. Keep it out of MVP scope.
   Rationale: Endogenous-First — encoding V2 decisions as issues makes them visible to future
   sessions and prevents rediscovery.

## Sources

1. `https://github.com/modelcontextprotocol/inspector` — MCP Inspector source; React UI +
   Node.js proxy; MIT license. Confirmed interactive, write-capable test harness.
2. `https://www.npmjs.com/package/@modelcontextprotocol/inspector` — 616K weekly downloads;
   no observability or metrics-persistence features.
3. `https://www.npmjs.com/package/@modelcontextprotocol/sdk` — 130.6M downloads; core MCP
   protocol SDK; not a UI or dashboard foundation.
4. `https://www.npmjs.com/package/@modelcontextprotocol/ext-apps` — 3.9M downloads; targets
   interactive UI applications, not observability dashboards.
5. `mcp_server/dogma_server.py` — Existing OTel instrumentation: `_TRACER`, `_METER`,
   `_OP_DURATION_HISTOGRAM`, `_run_with_mcp_telemetry`. Confirms the data source for MVP.
6. `data/mcp-metrics-schema.yml` — Governing schema for metrics consumed by the dashboard;
   read at implementation start; pin consumed fields; V2 for versioning.
