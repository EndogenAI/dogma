# Workplan: WebMCP Browser Inspector

**Branch**: `feat/sprint-23-webmcp-inspector`
**Date**: 2026-03-29
**Orchestrator**: Executive Orchestrator
**Closes Issues**: #513 (epic), #514 (research), #515 (implementation), #516 (integration), #517 (docs/tests)

---

## Objective

Implement MCP-based browser inspector capability that allows VS Code Copilot to programmatically query DOM state, console logs, and Svelte component state from the running dashboard frontend. This enables agent-inspectable UIs without manual DevTools copy/paste, using MCP as the bridge between browser and VS Code session.

---

## Phase Plan

### Phase 0 — Gap Analysis & Deep Dive Research ✅
**Agent**: Executive Orchestrator + Executive Planner
**Deliverables**:
- Gap analysis: survey existing MCP tooling, identify what's unknown
- Deep dive research: review MCP protocol spec, browser security constraints, existing implementations
- Replanning: adjust phase scope based on findings (may split/merge phases)
- Workplan doc reviewed by Review agent (APPROVED verdict in scratchpad)

**Depends on**: nothing
**Gate**: Phase 1 does not begin until replanning complete and workplan APPROVED
**Status**: ✅ Complete (2026-03-29) — gap analysis complete, research findings returned by Scout, replanning recommendation (proceed with Build Own), Review APPROVED

### Phase 1 — WebMCP Ecosystem Research ⬜
**Agent**: Executive Researcher
**Deliverables**:
- `docs/research/webmcp-browser-integration.md` (Status: Final)
- Survey findings: browser MCP server libraries, VS Code dynamic MCP client support, security/CORS considerations
- Pattern catalog: existing WebMCP implementations, transport specs (WebSocket/SSE)

**Depends on**: Phase 0 APPROVED
**CI**: validate_synthesis
**Status**: Not started

### Phase 1 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 1 Review Output` with verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 1 deliverables committed
**Gate**: Phase 2 does not begin until APPROVED
**Status**: Not started

### Phase 2 — Proof-of-Concept Browser MCP Server ⬜
**Agent**: Executive Scripter
**Deliverables**:
- `web/src/lib/mcp-server.ts` — minimal TypeScript MCP server (SSE/fetch transport)
- Single tool: `ping()` → returns `{"status": "ok"}`
- Integration into `App.svelte` (starts MCP server on mount)
- Manual test: curl MCP handshake endpoint

**Depends on**: Phase 1 Review APPROVED
**CI**: ruff (if Python), eslint (if linting configured)
**Status**: Not started

### Phase 2 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 2 Review Output` with verdict

**Depends on**: Phase 2 deliverables committed
**Gate**: Phase 3 does not begin until APPROVED
**Status**: Not started

### Phase 3 — Inspector Tools Implementation ⬜
**Agent**: Executive Scripter
**Deliverables**:
- Tool: `query_dom(selector)` → returns `{elements: [...], count: N}`
- Tool: `get_console_logs(level?)` → returns recent console entries (buffered in-memory)
- Tool: `get_component_state(component?)` → returns Svelte store values
- Tool: `trigger_action(event)` → simulates click/input for testing
- `web/src/lib/console-buffer.ts` — intercepts console.log/error
- Tool registration in `mcp-server.ts`

**Depends on**: Phase 2 Review APPROVED
**CI**: TypeScript compile, linting
**Status**: Not started

### Phase 3 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 3 Review Output` with verdict

**Depends on**: Phase 3 deliverables committed
**Gate**: Phase 4 does not begin until APPROVED
**Status**: Not started

### Phase 4 — VS Code MCP Client Integration ⬜
**Agent**: Executive Automator
**Deliverables**:
- Research: Can `.vscode/mcp.json` support runtime-discovered servers?
- If yes: `.vscode/mcp.json` entry for WebMCP connection (with env var for URL)
- If no: Document workaround (manual MCP client invocation via tool)
- Integration test: VS Code Copilot can invoke `query_dom()` against running dashboard

**Depends on**: Phase 3 Review APPROVED
**CI**: manual verification (no automated test for VS Code MCP client)
**Status**: Not started

### Phase 4 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 4 Review Output` with verdict

**Depends on**: Phase 4 deliverables committed
**Gate**: Phase 5 does not begin until APPROVED
**Status**: Not started

### Phase 5 — Documentation ⬜
**Agent**: Executive Docs
**Deliverables**:
- `docs/guides/webmcp-browser-inspector.md` — usage guide for Copilot sessions
- Update `mcp_server/README.md` with WebMCP browser server section
- Update `docs/mcp/` (if separate API docs exist)
- Add canonical examples to `docs/research/webmcp-browser-integration.md`

**Depends on**: Phase 4 Review APPROVED
**CI**: lychee, validate_synthesis (if touching research docs)
**Status**: Not started

### Phase 5 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 5 Review Output` with verdict

**Depends on**: Phase 5 deliverables committed
**Gate**: Phase 6 does not begin until APPROVED
**Status**: Not started

### Phase 6 — Testing ⬜
**Agent**: Executive Scripter
**Deliverables**:
- `tests/test_mcp_browser_server.py` — unit tests for TypeScript server (if feasible via pytest-playwright or similar)
- Manual test checklist in `docs/guides/webmcp-browser-inspector.md`
- Integration validation: all 4 tools invocable from VS Code

**Depends on**: Phase 5 Review APPROVED
**CI**: pytest fast suite
**Status**: Not started

### Phase 6 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 6 Review Output` with verdict

**Depends on**: Phase 6 deliverables committed
**Gate**: Phase 7 does not begin until APPROVED
**Status**: Not started

### Phase 7 — PR & Close ⬜
**Agent**: GitHub
**Deliverables**:
- Branch pushed to origin
- PR created linking all closed issues
- Issue #XXX commented with completion summary
- Session scratchpad archived

**Depends on**: Phase 6 Review APPROVED
**CI**: All checks passing
**Status**: Not started

---

## Acceptance Criteria

- [ ] All 7 phases complete and committed
- [ ] Research doc validates WebMCP is viable (or documents constraints if not)
- [ ] At least 1 MCP tool successfully invocable from VS Code Copilot against running dashboard
- [ ] Documentation includes usage guide and canonical examples
- [ ] PR created and all CI checks passing
- [ ] Issue progress comments posted at session close

---

## Dependencies & Constraints

- **Endogenous-First**: Check existing MCP tooling (`mcp_server/dogma_server.py`) for patterns before reaching external
- **Research-First**: Phase 1 gates all implementation — if WebMCP libraries don't exist, document the gap and propose alternatives
- **Security**: Browser MCP server must not expose dangerous operations (no `eval()`, no arbitrary DOM writes without sandboxing)
