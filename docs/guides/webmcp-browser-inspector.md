# WebMCP Browser Inspector Guide

Use this guide during Copilot sessions to inspect the MCP Dashboard frontend via the Phase 3 browser inspector tools.

---

## Purpose

The browser inspector facade in [web/src/lib/mcp-server.ts](../../web/src/lib/mcp-server.ts) provides local tool calls for:
- `ping` (baseline/debug connectivity check)
- `query_dom`
- `get_console_logs`
- `get_component_state`
- `trigger_action`

This is useful for reproducible UI state checks without manual DevTools copy/paste.

## Current Integration Posture

- Phase 3 tools are implemented and callable in-browser.
- The sidecar now exposes an HTTP MCP bridge at `http://127.0.0.1:8000/mcp` plus a diagnostic handshake endpoint at `http://127.0.0.1:8000/mcp/handshake`.
- The dashboard page must still run `BrowserMcpServer.start()` so the browser can register itself as the tool executor behind that bridge.
- VS Code can treat this as a separate HTTP MCP server from the existing stdio `dogma-governance` server.

See [docs/guides/mcp-dashboard.md](mcp-dashboard.md#vs-code-mcp-client-status-phase-4) for the Phase 4 transport limitation details.

## Topology

There are two MCP surfaces involved:

1. `dogma-governance`
  - transport: stdio
  - purpose: repository governance, validation, scaffolding, scratchpad tooling
2. `webmcp-browser-inspector`
  - transport: HTTP at `http://127.0.0.1:8000/mcp`
  - purpose: bridge browser-local inspector tools to VS Code through the dashboard sidecar

These are separate MCP servers. The new sidecar work does not replace `dogma-governance`; it adds a second server dedicated to browser inspection.

## Phase 6 Manual Test Checklist

Run these steps in order and record pass/fail for each item.

### Environment boot

- [ ] Run `uv sync --extra web`.
- [ ] Start runtime: `uv run --extra web python scripts/start_dashboard.py`.
- [ ] Open `http://localhost:5173`.
- [ ] In DevTools console, initialize inspector:

```typescript
const { BrowserMcpServer } = await import('/src/lib/mcp-server.ts');
const inspector = new BrowserMcpServer();
await inspector.start();
```

### Tool checks

- [ ] `ping` returns `{ status: 'ok' }`:

```typescript
await inspector.callTool('ping');
```

- [ ] `query_dom` returns at least one `.app-title` element with `count >= 1`:

```typescript
await inspector.callTool('query_dom', '.app-title');
```

- [ ] `get_console_logs` returns at least one `info` entry after writing an info log:

```typescript
console.info('phase6-manual-check');
await inspector.callTool('get_console_logs', { level: 'info' });
```

- [ ] `get_component_state` returns registered snapshot data and `count >= 1`:

```typescript
inspector.registerComponentState('dashboard', () => ({
  title: document.querySelector('.app-title')?.textContent?.trim() ?? null,
}));
await inspector.callTool('get_component_state', { component: 'dashboard' });
```

- [ ] `trigger_action` click returns `{ ok: true, action: 'click' }` for an existing tab selector:

```typescript
await inspector.callTool('trigger_action', {
  type: 'click',
  selector: '.tab:nth-child(2)'
});
```

### VS Code bridge availability check

- [ ] Confirm sidecar health is reachable:

```bash
curl -sf http://127.0.0.1:8000/api/health
```

- [ ] Confirm MCP handshake endpoint is reachable and returns bridge state:

```bash
curl -sf http://127.0.0.1:8000/mcp/handshake
```

- [ ] Confirm the dashboard page has registered with the sidecar:

Expected handshake fields after `await inspector.start()`:

```json
{
  "ok": true,
  "browserConnected": true,
  "toolCount": 5
}
```

- [ ] Optional: add an HTTP MCP entry in `.vscode/mcp.json` for the browser bridge:

```json
{
  "servers": {
    "webmcp-browser-inspector": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

Expected outcome: local browser tool invocation works directly, `GET /mcp/handshake` returns bridge state, and the sidecar advertises a browser-connected MCP bridge once the page registers.

## Integration Validation Status (Phase 6)

| Capability | Status | Evidence |
|---|---|---|
| Local browser `ping` tool invocation | Validated (manual) | `await inspector.callTool('ping')` returns `{ status: 'ok' }` |
| Local browser `query_dom` tool invocation | Validated (manual) | `.app-title` query returns element summary + count |
| Local browser `get_console_logs` tool invocation | Validated (manual) | `info` log appears in returned entries |
| Local browser `get_component_state` tool invocation | Validated (manual) | registered `dashboard` snapshot is returned |
| Local browser `trigger_action` tool invocation | Validated (manual) | click/input actions return `{ ok: true }` on valid targets |
| Sidecar MCP transport export | Implemented | `GET /mcp/handshake` returns browser bridge state; `POST /mcp` serves JSON-RPC tool routing |
| VS Code MCP invocation through the browser bridge | Implemented; local invocation verification pending | configure `.vscode/mcp.json` with `type: "http"` and `url: "http://127.0.0.1:8000/mcp"` |

---

## Setup

1. Install web extras:

```bash
uv sync --extra web
```

2. Start dashboard runtime:

```bash
uv run --extra web python scripts/start_dashboard.py
```

3. Open `http://localhost:5173`.

4. In browser DevTools console, initialize a local inspector instance:

```typescript
const { BrowserMcpServer } = await import('/src/lib/mcp-server.ts');
const inspector = new BrowserMcpServer();
await inspector.start();
```

Optional: add a component-state snapshot provider for tool tests:

```typescript
inspector.registerComponentState('dashboard', () => ({
  title: document.querySelector('.app-title')?.textContent?.trim() ?? null,
  activeTab: document.querySelector('.tab.active')?.textContent?.trim() ?? null,
}));
```

Optional autostart during dev hot-reload sessions:

```typescript
localStorage.setItem('webmcp.inspector.autostart', '1');
// or open the app with ?inspector=1
```

---

## Tool Invocation Examples

### query_dom

```typescript
await inspector.callTool('query_dom', '.app-title');
```

Expected shape:

```json
{
  "elements": [
    {
      "tag": "span",
      "id": "",
      "className": "app-title",
      "text": "MCP Dashboard"
    }
  ],
  "count": 1
}
```

### get_console_logs

Generate logs first:

```typescript
console.info('webmcp guide smoke-check');
await inspector.callTool('get_console_logs', { level: 'info' });
```

Expected shape:

```json
{
  "entries": [
    {
      "id": 1,
      "timestamp": "2026-03-29T00:00:00.000Z",
      "level": "info",
      "message": "webmcp guide smoke-check",
      "args": ["webmcp guide smoke-check"]
    }
  ],
  "count": 1
}
```

### get_component_state

```typescript
await inspector.callTool('get_component_state');
await inspector.callTool('get_component_state', { component: 'dashboard' });
```

Expected shape:

```json
{
  "state": {
    "dashboard": {
      "title": "MCP Dashboard",
      "activeTab": "Overview"
    }
  },
  "count": 1
}
```

### trigger_action

Click tab:

```typescript
await inspector.callTool('trigger_action', {
  type: 'click',
  selector: '.tab:nth-child(2)'
});
```

Input event:

```typescript
await inspector.callTool('trigger_action', {
  type: 'input',
  selector: 'input[type="text"]',
  value: 'test value',
  eventType: 'both'
});
```

Expected shape:

```json
{
  "ok": true,
  "action": "click",
  "selector": ".tab:nth-child(2)"
}
```

---

## Copilot Session Prompt Examples

Use these in Copilot Chat after you have a browser inspector session running:

```text
Validate dashboard header rendering by calling query_dom with selector ".app-title" and summarize count + text.
```

```text
Call get_console_logs at level "error" and list the latest 5 entries with timestamps.
```

```text
Call get_component_state for component "dashboard" and report current activeTab.
```

```text
Call trigger_action with click on ".tab:nth-child(3)" and then verify Errors tab heading is present via query_dom.
```

---

## Troubleshooting

### `Unknown tool` from callTool

Cause: tool name mismatch.

Fix:
- Use exact names: `query_dom`, `get_console_logs`, `get_component_state`, `trigger_action`.

### `invalid CSS selector`

Cause: selector parsing failed in `querySelectorAll`.

Fix:
- Retry with a minimal valid selector such as `.app-title` or `.tab`.

### `component not registered`

Cause: `get_component_state` was called with a component key that has no snapshotter.

Fix:
- Register first with `registerComponentState(name, snapshotter)`.
- Or call `get_component_state` without a `component` argument.

### `element not found for selector`

Cause: target element is not present when `trigger_action` runs.

Fix:
- Verify element existence with `query_dom` first.
- Re-run after the UI has rendered.

### Copilot cannot call browser inspector tools directly

Cause: the dashboard page has not registered with the sidecar bridge yet, or VS Code has not been pointed at the HTTP MCP endpoint.

Fix:
- Ensure the dashboard is open and `await inspector.start()` has run.
- Check `curl -sf http://127.0.0.1:8000/mcp/handshake` and confirm `browserConnected: true`.
- Add the `webmcp-browser-inspector` HTTP server entry to `.vscode/mcp.json` if it is not already present.

---

## Related Docs

- [docs/guides/mcp-dashboard.md](mcp-dashboard.md)
- [docs/mcp/api-reference.md](../mcp/api-reference.md)
- [mcp_server/README.md](../../mcp_server/README.md)
- [docs/research/webmcp-browser-integration.md](../research/webmcp-browser-integration.md)
