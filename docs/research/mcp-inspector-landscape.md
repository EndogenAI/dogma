---
title: MCP Inspector Landscape and Build-vs-Extend Decision
status: Final
research_type: secondary
research_issue: 0
closes_issue: 0
date: 2026-03-28
sources:
  - https://github.com/modelcontextprotocol/inspector
  - https://www.npmjs.com/package/@modelcontextprotocol/inspector
  - https://www.npmjs.com/package/@modelcontextprotocol/sdk
  - https://www.npmjs.com/package/@modelcontextprotocol/ext-apps
  - https://spec.modelcontextprotocol.io/specification/basic/transports/
  - https://modelcontextprotocol.io/docs/tools/inspector
  - https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/
  - https://opentelemetry.io/docs/what-is-opentelemetry/
  - https://github.com/open-telemetry/opentelemetry-python
  - https://github.com/PrefectHQ/fastmcp
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
  - id: R4
    title: Align dogma dashboard telemetry with OTel MCP Semantic Conventions
    status: accepted-for-adoption
    linked_issue: ""
---

# MCP Inspector Landscape and Build-vs-Extend Decision

## Executive Summary

This research asked whether the MCP Inspector or any existing `@modelcontextprotocol` npm
package could serve as a foundation for the dogmaMCP observability dashboard. The Inspector is
an interactive testing tool — write-capable, form-driven, and structurally orthogonal to a
read-only metrics dashboard. No existing MCP npm package addresses production observability.
The dogmaMCP dashboard is a novel use case; the correct posture is **build-alongside**: an
independent Svelte SPA consuming dogma's existing OTel metrics stream, with no code dependency
on the Inspector.

An expanded scouting pass (March 2026) surfaced two findings that materially strengthen this
decision and open a forward-compatibility path: (1) The CNCF/OTel project has published official
**MCP Semantic Conventions** (status: Development) defining standardized metric names, histogram
buckets, and trace attributes for MCP operations — validating dogma's OTel-first instrumentation
and providing a concrete attribute alignment target for V2. (2) FastMCP (PrefectHQ, 24k stars,
~70% MCP server market share) ships no native observability hooks — confirming that the
possible production-grade MCP telemetry gap dogma's dashboard addresses is real and currently
unfilled by the dominant MCP server framework.

## Hypothesis Validation

**Expected**: The MCP Inspector might be extendable or forkable as a protocol-fluent foundation,
providing an existing connection layer between the UI and the MCP server.

**Found**: The Inspector is disqualified by use-case mismatch, not technical inadequacy. It is
explicitly interactive — it invokes tools, reads resources, and conducts sampling. It is
write-capable by design. The `@modelcontextprotocol/ext-apps` package (3.9M downloads) similarly
targets interactive UIs, not observability. The 616K-download `inspector` package is a REPL for
MCP protocol development, not a metrics aggregation substrate. Searching the MCP npm namespace
found no read-only dashboard or observability package.

The MCP transport spec confirms this structurally: standard transports (stdio, HTTP+SSE,
streamable-http) have no built-in telemetry intercept. stdio logs only go to stderr; SSE
stream content is JSON-RPC payloads with no metrics hook. Custom transport layers are permitted
but must preserve JSON-RPC format — there is no standard mechanism to inject OTel spans at the
protocol layer. Application-layer instrumentation (dogma's `_run_with_mcp_telemetry`) is the
correct and only viable attachment point.

**Verdict: Hypothesis disconfirmed.** Fork and extend are not viable postures. Build-alongside
is the correct decision. The ecosystem gap remains unfilled by any published package, including
the dominant FastMCP framework.

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

**Canonical example: OTel MCP Semantic Conventions — the emerging standard alignment surface**

The OpenTelemetry project has published official MCP Semantic Conventions
(`opentelemetry.io/docs/specs/semconv/gen-ai/mcp/`, status: Development) that define:

- Four official histograms: `mcp.client.operation.duration`, `mcp.server.operation.duration`,
  `mcp.client.session.duration`, `mcp.server.session.duration` — all in seconds
- Standard span attributes: `mcp.method.name`, `mcp.session.id`, `mcp.protocol.version`,
  `gen_ai.tool.name`, `gen_ai.tool.call.arguments`
- Trace context propagation pattern: W3C `traceparent`/`tracestate` via `params._meta` property
  bag (no native MCP propagation yet; under active specification at modelcontextprotocol#246)
- Transport type: via `network.transport` attribute (`pipe` for stdio, `tcp` for HTTP transports)

Dogma's current `_OP_DURATION_HISTOGRAM` is a direct precursor to `mcp.server.operation.duration`.
Aligning the attribute names in a V2 pass would make dogma's instrumentation compatible with any
OTel-native dashboard (Grafana, Jaeger, Prometheus) without code changes to the sidecar.

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
   Rationale: Endogenous-First ([MANIFESTO.md §1](../../MANIFESTO.md)) — encoding V2 decisions
   as issues makes them visible to future sessions and prevents rediscovery.

4. **Align dogma dashboard telemetry with OTel MCP Semantic Conventions (V2 scope)** — The
   official OTel MCP conventions define `mcp.server.operation.duration` and `mcp.session.id`
   among other standard attributes. Renaming dogma's `_OP_DURATION_HISTOGRAM` to the official
   attribute name in a V2 pass would make the dashboard compatible with any OTLP-native
   visualization backend at zero additional code cost. Track via a GitHub issue; do not block
   MVP on this alignment. Rationale: Algorithms-Before-Tokens
   ([MANIFESTO.md §2](../../MANIFESTO.md)) — encode the alignment intent now; defer
   implementation until the conventions reach stable status.

## Sources

1. `https://github.com/modelcontextprotocol/inspector` — MCP Inspector source; React UI +
   Node.js proxy; 9.2k stars, MIT license. Confirmed interactive, write-capable test harness;
   no observability export API. Session-token auth enforced (CVE-2025-49596 patched).
2. `https://www.npmjs.com/package/@modelcontextprotocol/inspector` — 616K weekly downloads;
   no observability or metrics-persistence features.
3. `https://www.npmjs.com/package/@modelcontextprotocol/sdk` — 130.6M downloads; core MCP
   protocol SDK; not a UI or dashboard foundation.
4. `https://www.npmjs.com/package/@modelcontextprotocol/ext-apps` — 3.9M downloads; targets
   interactive UI applications, not observability dashboards.
5. `https://spec.modelcontextprotocol.io/specification/basic/transports/` — MCP 2024-11-05
   transport spec; confirms stdio/SSE/streamable-http have no built-in telemetry hook;
   application-layer instrumentation is the correct attachment point.
6. `https://modelcontextprotocol.io/docs/tools/inspector` — Official Inspector docs; ports 6274
   (UI) and 6277 (proxy); CLI mode available; no structured metric export.
7. `https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/` — **OTel MCP Semantic Conventions**
   (status: Development); defines four histograms and standardized span attributes for MCP;
   identifies `mcp.server.operation.duration` as the canonical V2 alignment target for dogma.
8. `https://opentelemetry.io/docs/what-is-opentelemetry/` — OTel overview; CNCF project,
   Traces and Metrics signals stable; vendor-agnostic, supports OTLP, Jaeger, Prometheus export.
9. `https://github.com/open-telemetry/opentelemetry-python` — OTel Python SDK (2.4k stars);
   stable Traces and Metrics signals; Logs in active development; OTLP export over gRPC/HTTP.
10. `https://github.com/PrefectHQ/fastmcp` — FastMCP (24.1k stars, 1M downloads/day); powers
    ~70% of MCP servers; no native observability/telemetry hooks — confirms the ecosystem gap
    dogma's dashboard fills.
11. `mcp_server/dogma_server.py` — Existing OTel instrumentation: `_TRACER`, `_METER`,
    `_OP_DURATION_HISTOGRAM`, `_run_with_mcp_telemetry`. Confirms the data source for MVP.
12. `data/mcp-metrics-schema.yml` — Governing schema for metrics consumed by the dashboard;
    pin consumed fields for MVP; V2 for versioning and OTel convention alignment.
