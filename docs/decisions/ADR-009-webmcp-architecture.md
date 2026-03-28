---
Status: Accepted
Date: 2026-03-28
Deciders: EndogenAI core team
---

# ADR-009: MCP Web Dashboard Architecture

## Context
Issue #502 Phase 2 requires an architecture contract for the MCP Web Dashboard before implementation can proceed. Phase 1 research established that MCP Inspector remains a developer-focused, interactive MCP client and does not match the read-only observability scope required for dogmaMCP dashboard MVP. This ADR records the locked technical decisions so Phase 3-5 implementation can proceed without architecture drift.

## Decision Drivers

- Preserve Inspector's role as a developer tool while delivering a dedicated read-only observability dashboard.
- Keep MVP stack minimal and browser-native where possible.
- Encode explicit constraints that prevent scope creep in dashboard routing, visualization dependencies, and deployment-time configurability.
- Keep local development path deterministic for sprint execution.

## Decision

1. Build strategy: build dashboard alongside MCP Inspector, not by extending Inspector UI.
2. Data visualization library: use LayerCake for MVP charts. Do not use `svelte-chartjs` or `chart.js` for MVP.
3. Frontend scaffold command: use `npm init vite web -- --template svelte`. The archived `sveltejs/template` flow is not used.
4. CORS policy: hardcode `allow_origins=["http://localhost:5173"]` for MVP sidecar-to-Vite local development. Add inline `TODO(v2):` environment-variable escape hatch tracked in #506.
5. Streaming transport: use FastAPI `StreamingResponse` on server and browser-native `EventSource` in frontend.
6. Tab routing model: use local reactive variable `let activeTab = 'overview'`; no routing library for MVP.
7. Connection state machine: implement `LIVE -> STALE -> ERROR` lifecycle for stream status.
8. Offline fallback: use static fixture file at `web/src/assets/fixture.json` when live stream/snapshot is not yet available.

## Consequences

- MVP dependency surface stays smaller by avoiding routing and chart wrapper libraries.
- Frontend and sidecar integration path is explicit (`StreamingResponse` + `EventSource`) and testable.
- Local-only CORS posture is secure for MVP but intentionally non-configurable until #506 is implemented.
- Offline fixture path is a required artifact for early UX continuity during startup and disconnected operation.

## Alternatives considered

1. Extend MCP Inspector UI directly. Rejected because Inspector is optimized for interactive MCP testing/debugging, not read-only telemetry presentation.
2. Use `svelte-chartjs`/`chart.js` for MVP charts. Rejected to avoid additional wrapper/dependency surface in initial release.
3. Introduce routing library in MVP. Rejected because three-tab local state does not justify router complexity.

## References

- `docs/plans/2026-03-28-mcp-web-dashboard.md`
- `docs/research/mcp-inspector-landscape.md`
- `docs/research/svelte-ecosystem-for-webmcp.md`
