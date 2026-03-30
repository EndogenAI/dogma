# WebMCP Browser Inspector Guide

Use this guide during Copilot sessions to inspect the MCP Dashboard frontend via the Phase 3 browser inspector tools.

---

## Purpose

The browser inspector facade in [web/src/lib/mcp-server.ts](../../web/src/lib/mcp-server.ts) provides local tool calls for:
- `query_dom`
- `get_console_logs`
- `get_component_state`
- `trigger_action`

This is useful for reproducible UI state checks without manual DevTools copy/paste.

## Current Integration Posture

- Phase 3 tools are implemented and callable in-browser.
- Phase 4 confirmed there is no exported HTTP MCP transport endpoint yet (`/mcp` is not exposed by `web/server.py`).
- For now, use local in-browser invocation as the operational workaround.

See [docs/guides/mcp-dashboard.md](mcp-dashboard.md#vs-code-mcp-client-status-phase-4) for the Phase 4 transport limitation details.

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

### VS Code transport limitation check

- [ ] Confirm sidecar health is reachable:

```bash
curl -sf http://127.0.0.1:8000/api/health
```

- [ ] Confirm MCP handshake endpoint is still missing (expected `404`):

```bash
curl -i http://127.0.0.1:8000/mcp/handshake
```

Expected outcome: local browser tool invocation works, but VS Code cannot invoke browser tools via MCP transport until `/mcp` is implemented.

## Integration Validation Status (Phase 6)

| Capability | Status | Evidence |
|---|---|---|
| Local browser `ping` tool invocation | Validated (manual) | `await inspector.callTool('ping')` returns `{ status: 'ok' }` |
| Local browser `query_dom` tool invocation | Validated (manual) | `.app-title` query returns element summary + count |
| Local browser `get_console_logs` tool invocation | Validated (manual) | `info` log appears in returned entries |
| Local browser `get_component_state` tool invocation | Validated (manual) | registered `dashboard` snapshot is returned |
| Local browser `trigger_action` tool invocation | Validated (manual) | click/input actions return `{ ok: true }` on valid targets |
| VS Code MCP transport to browser inspector | Blocked (known limitation) | `GET /mcp/handshake` returns `404`; no exported HTTP MCP endpoint |

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

Cause: Phase 4 limitation; no network MCP endpoint exported.

Fix:
- Continue with local in-browser invocation workflow.
- Track transport endpoint implementation before attempting `.vscode/mcp.json` HTTP wiring.

---

## Related Docs

- [docs/guides/mcp-dashboard.md](mcp-dashboard.md)
- [docs/mcp/api-reference.md](../mcp/api-reference.md)
- [mcp_server/README.md](../../mcp_server/README.md)
- [docs/research/webmcp-browser-integration.md](../research/webmcp-browser-integration.md)
