---
title: WebMCP Browser Integration — Implementation Patterns and Security Constraints
status: Final
closes_issue: 514
x-governs:
  - local-compute-first
  - tool-governance
  - security-guardrails
created: 2026-03-29
sources:
  - https://spec.modelcontextprotocol.io/
  - https://developer.chrome.com/docs/extensions/reference/webmcp/
  - https://www.anthropic.com/engineering/building-effective-agents
  - https://github.com/modelcontextprotocol/servers
recommendations:
  - id: rec-webmcp-browser-001
    title: "Use SSE transport for browser MCP servers (not WebSocket or stdio)"
    status: accepted
    effort: Low
    linked_issue: 515
    decision_ref: Phase 0 gap analysis (Sprint 23 workplan)
  - id: rec-webmcp-browser-002
    title: "Apply mcp_server/_security.py SSRF patterns to all browser MCP tool implementations"
    status: accepted
    effort: Low
    linked_issue: 515
    decision_ref: null
  - id: rec-webmcp-browser-003
    title: "Register browser MCP tools with explicit read/write capability markers"
    status: accepted
    effort: Low
    linked_issue: 516
    decision_ref: null
---

# WebMCP Browser Integration — Implementation Patterns and Security Constraints

## 1. Executive Summary

This research documents browser-based MCP server implementation patterns, transport specifications, and security constraints to support Sprint 23's WebMCP Inspector implementation. The primary governing axioms are **Local-Compute-First** ([MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first)) — minimize cloud dependency and token burn — and **Algorithms-Before-Tokens** ([MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens)) — encode repeatable patterns into deterministic infrastructure.

**Key findings**:
1. **SSE is the canonical browser MCP transport** — Server-Sent Events (SSE) are browser-native, CORS-compatible, unidirectional, and already validated in dogma's web dashboard (`web/server.py` + `web/src/lib/api.ts`)
2. **Security patterns are established** — Dogma's `mcp_server/_security.py` provides SSRF guards (`validate_url`), path traversal prevention (`validate_repo_path`), and scheme allowlisting that apply directly to browser MCP implementations
3. **Tool registration follows FastMCP patterns** — Browser tools register via `@mcp.tool()` decorators with explicit schemas; capability gating via tool naming (e.g., `browser_read_dom` vs. `browser_interact_click`)
4. **WebMCP is not a dependency** — Chrome's WebMCP extension (March 2026) requires Chrome 146.0.7672.0+ and experimental flags; building a TypeScript MCP server is architecturally simpler and more portable

**Recommendations**:
- R1: Use SSE (`EventSource` + FastAPI `StreamingResponse`) as the browser MCP transport
- R2: Apply `_security.py` SSRF patterns to all browser tool implementations
- R3: Register tools with explicit read/write capability markers for governance

**Sprint 23 applicability**: This research validates Phase 2's "Build Own" decision — implementing a TypeScript browser MCP server using SSE transport is architecturally aligned with dogma's existing MCP patterns and requires no external dependencies.

---

## 2. Hypothesis Validation

**H1**: Browser MCP servers can use the same transport patterns as desktop MCP servers (stdio, SSE, HTTP).

**Validation Method**: Compare MCP transport specifications against browser capabilities (subprocess spawning, EventSource API, fetch API).

**Result**: ✅ **PARTIALLY SUPPORTED** — Browsers support SSE (`EventSource`) and HTTP (`fetch`), but NOT stdio (no subprocess spawning). SSE is the canonical browser transport.

**Evidence**:
- MCP specification (spec.modelcontextprotocol.io) defines three transports: stdio, SSE, and HTTP with streamable responses
- Dogma's web dashboard already uses SSE successfully (`web/server.py` FastAPI `StreamingResponse` + `web/src/lib/api.ts` `EventSource`)
- Chrome DevTools Protocol (CDP) and WebMCP documentation confirm SSE as the browser-compatible MCP transport

**Canonical example — SSE transport (from dogma web dashboard)**:

```typescript
// web/src/lib/api.ts — EventSource client
export function subscribeStream(
  onData: (snapshot: MetricsSnapshot) => void,
  onError?: (err: Event) => void,
): () => void {
  const source = new EventSource('http://localhost:8000/api/metrics/stream');
  source.onmessage = (event: MessageEvent) => {
    const snapshot = JSON.parse(event.data) as MetricsSnapshot;
    onData(snapshot);
  };
  if (onError) source.onerror = onError;
  return () => source.close();
}
```

```python
# web/server.py — FastAPI StreamingResponse
@app.get("/api/metrics/stream")
async def stream_metrics():
    async def _generate():
        while True:
            snapshot = _build_snapshot()
            yield f"data: {json.dumps(snapshot)}\n\n"
            await asyncio.sleep(2)
    return StreamingResponse(_generate(), media_type="text/event-stream")
```

---

**H2**: Browser MCP tools must implement the same SSRF prevention patterns as desktop MCP tools.

**Validation Method**: Review dogma's `mcp_server/_security.py` implementation; assess applicability to browser tool scenarios (DOM queries, console log access, network requests).

**Result**: ✅ **STRONGLY SUPPORTED** — SSRF prevention is MORE critical in browser contexts because browsers have ambient credentials (cookies, localStorage, service workers) that SSRF exploits can exfiltrate.

**Evidence**:
- `mcp_server/_security.py` validates URLs against private IP ranges (RFC 1918, loopback, link-local) and enforces `https://` scheme allowlist
- Browser tools that fetch external URLs (e.g., a hypothetical `browser_fetch` tool) MUST apply the same `validate_url` checks before any `fetch()` call
- DOM query tools (`query_dom(selector)`) do not fetch external URLs but MUST sanitize CSS selectors to prevent injection attacks

**Canonical example — SSRF validation (from dogma MCP server)**:

```python
# mcp_server/_security.py
_ALLOWED_SCHEMES: frozenset[str] = frozenset({"https"})
_BLOCKED_IPV4_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),    # loopback
    ipaddress.ip_network("169.254.0.0/16"), # link-local
]

def validate_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError(f"URL scheme {parsed.scheme} not allowed")
    # DNS resolution check to prevent DNS rebinding attacks
    ip_str = socket.gethostbyname(parsed.hostname)
    ip = ipaddress.ip_address(ip_str)
    for network in _BLOCKED_IPV4_NETWORKS:
        if ip in network:
            raise ValueError(f"URL resolves to blocked IP: {ip_str}")
    return url
```

**Browser MCP application**: Any browser tool that calls external URLs must apply this pattern in TypeScript:

```typescript
// web/src/lib/mcp-security.ts (proposed)
const BLOCKED_NETWORKS = ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '127.0.0.0/8'];

export function validateUrl(url: string): void {
  const parsed = new URL(url);
  if (parsed.protocol !== 'https:') {
    throw new Error(`URL scheme ${parsed.protocol} not allowed`);
  }
  // Note: Browser JS cannot reliably perform DNS resolution checks client-side
  // This validation is a best-effort pre-check; server-side validation is required
  if (parsed.hostname === 'localhost' || parsed.hostname.startsWith('192.168.')) {
    throw new Error('URL resolves to blocked hostname');
  }
}
```

---

**H3**: VS Code can dynamically connect to browser MCP servers without `.vscode/mcp.json` configuration.

**Validation Method**: Review VS Code MCP client documentation and dogma's existing `.vscode/mcp.json` patterns.

**Result**: ⚠️ **CONDITIONALLY SUPPORTED** — VS Code MCP clients support runtime discovery via SSE endpoint URLs, but `.vscode/mcp.json` is the canonical configuration mechanism for team-shared server definitions.

**Evidence**:
- `.vscode/mcp.json` supports `type: "http"` entries with `url` field pointing to SSE endpoints
- Dogma's existing MCP configuration uses stdio transport for local governance tools
- Runtime discovery (without `.vscode/mcp.json`) is possible via VS Code extension APIs but not documented as a first-class pattern in the MCP specification

**Canonical example — HTTP MCP configuration**:

```json
// .vscode/mcp.json
{
  "servers": {
    "browser-inspector": {
      "type": "http",
      "url": "http://localhost:5173/mcp",
      "description": "Browser MCP server for dashboard inspection"
    }
  }
}
```

**Sprint 23 recommendation**: Use `.vscode/mcp.json` for Phase 4 integration; defer runtime discovery to V2.

---

## 3. Pattern Catalog

### Pattern 3.1: SSE Transport for Browser MCP Servers

**Context**: Browser environments cannot spawn subprocesses (no stdio transport) but support EventSource API for unidirectional streaming.

**Pattern**: Implement MCP server as SSE endpoint using FastAPI `StreamingResponse` (server) + `EventSource` (client).

**Canonical example**:

```typescript
// web/src/lib/mcp-server.ts (proposed for Sprint 23 Phase 2)
import type { Tool } from '@modelcontextprotocol/sdk';

export class BrowserMCPServer {
  private tools: Map<string, Tool> = new Map();

  constructor() {
    this.registerTool('ping', async () => ({ status: 'ok' }));
  }

  registerTool(name: string, handler: (...args: any[]) => Promise<any>): void {
    this.tools.set(name, { name, handler });
  }

  // SSE endpoint handler (called by FastAPI route)
  async handleStream(writer: WritableStreamDefaultWriter): Promise<void> {
    const encoder = new TextEncoder();
    await writer.write(encoder.encode(`data: ${JSON.stringify({ type: 'hello' })}\n\n`));
    // Tool invocation loop listens for incoming JSON-RPC messages
  }
}
```

**Anti-pattern**: Using WebSocket for MCP transport in browsers — WebSocket requires bidirectional communication and complex handshake logic; SSE is simpler and sufficient for MCP's client-initiated request pattern.

**Dogma alignment**: This pattern matches `web/server.py` (FastAPI SSE) and requires no new dependencies.

---

### Pattern 3.2: Tool Registration with Capability Markers

**Context**: Browser MCP tools span read-only (DOM queries, console logs) and interactive (click simulation, form submission). Governance requires explicit capability markers.

**Pattern**: Prefix tool names with capability level (`browser_read_`, `browser_interact_`) and register with explicit schemas.

**Canonical example** (Sprint 23 Phase 3 tools):

```typescript
// web/src/lib/mcp-tools.ts (proposed)
import { z } from 'zod';

export const TOOLS = {
  browser_read_dom: {
    name: 'browser_read_dom',
    description: 'Query DOM elements by CSS selector (read-only)',
    schema: z.object({
      selector: z.string().describe('CSS selector (e.g., "div.metrics-card")'),
    }),
    handler: async (args: { selector: string }) => {
      const elements = document.querySelectorAll(args.selector);
      return {
        count: elements.length,
        elements: Array.from(elements).map((el) => ({
          tag: el.tagName,
          text: el.textContent?.slice(0, 200),
          classes: Array.from(el.classList),
        })),
      };
    },
  },

  browser_read_console: {
    name: 'browser_read_console',
    description: 'Retrieve recent console logs (read-only)',
    schema: z.object({
      level: z.enum(['log', 'warn', 'error', 'info']).optional(),
    }),
    handler: async (args: { level?: string }) => {
      // Assumes console-buffer.ts intercepts console methods
      return getConsoleBuffer(args.level);
    },
  },

  browser_interact_click: {
    name: 'browser_interact_click',
    description: 'Simulate click on DOM element (WRITE capability)',
    schema: z.object({
      selector: z.string().describe('CSS selector of element to click'),
    }),
    handler: async (args: { selector: string }) => {
      const el = document.querySelector(args.selector);
      if (!el) throw new Error(`Element not found: ${args.selector}`);
      (el as HTMLElement).click();
      return { clicked: true, selector: args.selector };
    },
  },
};
```

**Why capability prefixes matter**:
- `.vscode/mcp.json` can restrict tool access via `allowedTools` arrays
- Review gates can flag interactive tools as higher-risk during code review
- Capability gating scripts (`scripts/capability_gate.py`) can enforce read-only defaults

**Anti-pattern**: Generic tool names like `queryDom` without capability markers — this prevents fine-grained governance and audit trail analysis.

---

### Pattern 3.3: Console Log Buffering for Inspection

**Context**: Browser console logs are ephemeral — they disappear when the dev tools are closed or the page is refreshed. Agent inspection requires a persistent buffer.

**Pattern**: Intercept `console.log`, `console.warn`, `console.error` at app startup; buffer recent entries in memory; expose via MCP tool.

**Canonical example** (Sprint 23 Phase 3 deliverable):

```typescript
// web/src/lib/console-buffer.ts (proposed)
type ConsoleEntry = {
  ts: string;
  level: 'log' | 'warn' | 'error' | 'info';
  message: string;
  args: any[];
};

const BUFFER_SIZE = 100;
const _buffer: ConsoleEntry[] = [];

const _original = {
  log: console.log,
  warn: console.warn,
  error: console.error,
  info: console.info,
};

export function initConsoleBuffer(): void {
  ['log', 'warn', 'error', 'info'].forEach((level) => {
    console[level] = (...args: any[]) => {
      _buffer.push({
        ts: new Date().toISOString(),
        level: level as any,
        message: args.map((a) => String(a)).join(' '),
        args,
      });
      if (_buffer.length > BUFFER_SIZE) _buffer.shift();
      _original[level](...args); // Call original
    };
  });
}

export function getConsoleBuffer(level?: string): ConsoleEntry[] {
  return level ? _buffer.filter((e) => e.level === level) : _buffer;
}
```

**Integration point**: Call `initConsoleBuffer()` in `App.svelte` `onMount()` before any component renders.

**Anti-pattern**: Relying on Chrome DevTools Protocol (CDP) for console access — CDP requires a separate WebSocket connection and is not available in production builds.

---

### Pattern 3.4: Svelte Store Inspection via MCP

**Context**: Svelte stores (`writable`, `derived`, `readable`) hold component state. Agent inspection requires exposing store values without coupling to Svelte internals.

**Pattern**: Register stores in a global registry at creation time; expose via MCP tool that queries the registry.

**Canonical example**:

```typescript
// web/src/lib/store-registry.ts (proposed)
import type { Writable, Readable } from 'svelte/store';

const _stores = new Map<string, Writable<any> | Readable<any>>();

export function registerStore(name: string, store: Writable<any> | Readable<any>): void {
  _stores.set(name, store);
}

export function getStoreSnapshot(name?: string): Record<string, any> {
  const snapshot: Record<string, any> = {};
  const targets = name ? [name] : Array.from(_stores.keys());
  targets.forEach((key) => {
    const store = _stores.get(key);
    if (store) {
      let value: any;
      store.subscribe((v) => { value = v; })(); // Immediate unsubscribe
      snapshot[key] = value;
    }
  });
  return snapshot;
}
```

```typescript
// Usage in app stores
import { writable } from 'svelte/store';
import { registerStore } from './store-registry';

export const metrics = writable<MetricsSnapshot>(fixtureData);
registerStore('metrics', metrics);
```

```typescript
// MCP tool
export const TOOLS = {
  browser_read_store: {
    name: 'browser_read_store',
    description: 'Get current value of Svelte store(s)',
    schema: z.object({
      name: z.string().optional().describe('Store name (omit for all stores)'),
    }),
    handler: async (args: { name?: string }) => {
      return getStoreSnapshot(args.name);
    },
  },
};
```

**Anti-pattern**: Directly accessing Svelte component `$$` internals — this is framework-private API and breaks across Svelte versions.

---

## 4. Security Constraints

### 4.1 SSRF Prevention (Mandatory)

**Constraint**: All browser MCP tools that fetch external URLs MUST validate URLs against private IP ranges and enforce `https://` scheme.

**Rationale**: Browsers have ambient network access and can be tricked into making requests to internal services (e.g., `http://localhost:6379/` to access Redis, `http://192.168.1.1/admin` to access router admin panels).

**Implementation**: Port `mcp_server/_security.py::validate_url` to TypeScript (see Pattern 3.2 canonical example).

**Acceptance test**: Attempt to invoke a hypothetical `browser_fetch` tool with `http://127.0.0.1/admin` — tool MUST reject with error `URL resolves to blocked hostname`.

---

### 4.2 CSS Selector Injection Prevention

**Constraint**: All DOM query tools MUST sanitize CSS selectors to prevent arbitrary script execution.

**Threat model**: Malicious selector strings like `'; DROP TABLE users; --` or `<script>alert('XSS')</script>` could bypass querySelector if not properly escaped.

**Mitigation**: Use `document.querySelector()` built-in escaping (it does NOT execute scripts) and validate selector format before invoking:

```typescript
function sanitizeSelector(selector: string): string {
  // Allowlist: alphanumeric, dots, hashes, brackets, spaces, commas
  if (!/^[a-zA-Z0-9\s.,#\[\]()>+~:*-]+$/.test(selector)) {
    throw new Error('Invalid CSS selector characters');
  }
  return selector;
}
```

**Acceptance test**: Attempt to invoke `browser_read_dom` with selector `<script>alert('XSS')</script>` — tool MUST reject with validation error.

---

### 4.3 Credential Exposure via Console Logs

**Constraint**: Console buffer MUST NOT capture sensitive data (API keys, tokens, passwords) inadvertently logged by application code.

**Mitigation**:
1. **Code hygiene**: Never log secrets to console (enforce via linting rule)
2. **Redaction**: Console buffer intercept redacts known secret patterns (e.g., `Bearer [REDACTED]`, `github_pat_[REDACTED]`)
3. **Limit buffer size**: 100 entries maximum to reduce exposure window

**Canonical redaction pattern**:

```typescript
function redactSecrets(message: string): string {
  return message
    .replace(/Bearer\s+[A-Za-z0-9_-]+/g, 'Bearer [REDACTED]')
    .replace(/github_pat_[A-Za-z0-9_]+/g, 'github_pat_[REDACTED]')
    .replace(/sk-[A-Za-z0-9]{32,}/g, 'sk-[REDACTED]');
}
```

**Acceptance test**: Log `Bearer abc123xyz` to console; invoke `browser_read_console` — returned message MUST show `Bearer [REDACTED]`.

---

### 4.4 CORS and Origin Validation

**Constraint**: Browser MCP server SSE endpoint MUST enforce CORS origin allowlist in production deployments.

**Development posture**: Hardcode `http://localhost:5173` for MVP (already in `web/server.py`)

```python
# web/server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # TODO(v2): env var
    allow_credentials=True,
)
```

**Production posture** (deferred to #506): Use environment variable `ALLOWED_ORIGINS` and reject all requests from untrusted origins.

**Threat**: Without CORS enforcement, any malicious site can connect to the MCP SSE endpoint and invoke tools.

---

## 5. Recommendations

### R1: Use SSE transport for Browser MCP (Accepted — Sprint 23 Phase 2)

**Status**: Accepted  
**Effort**: Low  
**Linked issue**: #515 (Phase 2 PoC)  
**Decision reference**: Phase 0 gap analysis (Sprint 23 workplan)

**Rationale**: SSE is browser-native, CORS-compatible, unidirectional, and already validated in dogma's web dashboard. WebSocket adds bidirectional complexity with no MCP benefit; stdio is impossible in browsers.

**Implementation**: Use FastAPI `StreamingResponse` + browser `EventSource` (Pattern 3.1).

**Acceptance**: Phase 2 deliverable includes `web/src/lib/mcp-server.ts` with SSE endpoint handler and single `ping()` tool.

---

### R2: Apply mcp_server/_security.py SSRF patterns to all browser MCP tools (Accepted — Sprint 23 Phase 3)

**Status**: Accepted  
**Effort**: Low  
**Linked issue**: #515 (Phase 3 tools)

**Rationale**: Browsers have ambient credentials and network access. SSRF exploits can exfiltrate cookies, localStorage, and access internal services.

**Implementation**: Port `validate_url` to TypeScript (see Security Constraint 4.1); apply to all tools that fetch external URLs.

**Acceptance**: All browser MCP tools that call external URLs validate against private IP ranges; acceptance test rejects `http://127.0.0.1/`.

---

### R3: Register browser MCP tools with explicit read/write capability markers (Accepted — Sprint 23 Phase 3)

**Status**: Accepted  
**Effort**: Low  
**Linked issue**: #516 (VS Code integration)

**Rationale**: Capability prefixes (`browser_read_`, `browser_interact_`) enable fine-grained governance and audit trail analysis.

**Implementation**: Prefix all tool names (Pattern 3.2); document capability levels in tool descriptions.

**Acceptance**: `.vscode/mcp.json` can restrict Phase 3 tools via `allowedTools: ["browser_read_*"]` pattern.

---

## 6. Open Questions

1. **WebMCP public release timeline** — Chrome WebMCP extension announced March 17, 2026; repository not public as of March 29. Monitor `https://developer.chrome.com/docs/extensions/reference/webmcp/` for updates.

2. **VS Code dynamic MCP client support** — Can `.vscode/mcp.json` be updated at runtime without restarting VS Code? Phase 4 integration may require testing.

3. **Tool invocation latency** — SSE transport introduces HTTP round-trip overhead. Measure P95 latency for `browser_read_dom` in Phase 3; compare against direct console access baseline.

4. **Multi-tab inspection** — How should browser MCP handle multiple dashboard tabs open simultaneously? Phase 3 scope assumes single-tab; multi-tab deferred to V2.

5. **Security audit gate for production** — Should browser MCP tools be restricted to `localhost` origins only? Phase 4 integration should include security review before any non-localhost deployment.

---

## 7. Sources

### Endogenous Cross-References

1. **[docs/research/webmcp-browser-integration-feasibility.md](webmcp-browser-integration-feasibility.md)** — March 23, 2026 feasibility study; established WebMCP not publicly available, validated MCP local-first alignment
2. **[mcp_server/dogma_server.py](../../mcp_server/dogma_server.py)** — Production MCP server (stdio transport, 12 tools, FastMCP framework)
3. **[mcp_server/_security.py](../../mcp_server/_security.py)** — SSRF prevention (`validate_url`), path traversal prevention (`validate_repo_path`)
4. **[web/server.py](../../web/server.py)** — FastAPI sidecar with SSE transport (`StreamingResponse`)
5. **[web/src/lib/api.ts](../../web/src/lib/api.ts)** — Browser SSE client (`EventSource`)
6. **[docs/plans/2026-03-29-sprint-23-webmcp-inspector.md](../plans/2026-03-29-sprint-23-webmcp-inspector.md)** — Sprint 23 workplan (Phase 0 gap analysis, Phase 1 research, Phase 2-4 implementation)
7. **[docs/decisions/ADR-009-webmcp-architecture.md](../decisions/ADR-009-webmcp-architecture.md)** — MCP Web Dashboard architecture decision (SSE transport, LayerCake charts, CORS policy)
8. **[MANIFESTO.md § Local-Compute-First](../../MANIFESTO.md#3-local-compute-first)** — Minimize cloud dependency and token burn
9. **[MANIFESTO.md § Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens)** — Encode repeatable patterns into deterministic infrastructure
10. **[AGENTS.md § Security Guardrails](../../AGENTS.md#security-guardrails)** — SSRF prevention, secrets hygiene, two-stage gate for irreversible actions

### External Sources

11. **Model Context Protocol Specification** — https://spec.modelcontextprotocol.io/ — Defines stdio, SSE, and HTTP transports; client/server topology; tool/resource APIs
12. **Chrome WebMCP Extension Documentation** — https://developer.chrome.com/docs/extensions/reference/webmcp/ — Chrome 146.0.7672.0+ required; experimental flags; web page → MCP server pattern
13. **Building Effective AI Agents (Anthropic)** — https://www.anthropic.com/engineering/building-effective-agents — Agent patterns, workflow decomposition, tool design
14. **MCP Servers Repository** — https://github.com/modelcontextprotocol/servers — Official MCP server implementations (filesystem, GitHub, Postgres, browser automation via Puppeteer)
15. **FastAPI StreamingResponse Documentation** — https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse — SSE implementation pattern
16. **MDN EventSource API** — https://developer.mozilla.org/en-US/docs/Web/API/EventSource — Browser-native SSE client
17. **Svelte Stores Documentation** — https://svelte.dev/docs/svelte-store — `writable`, `readable`, `derived` APIs; subscription patterns

---

## 8. Acceptance Criteria

This research synthesis is accepted when:
- ✅ All 5 required headings present (Executive Summary, Hypothesis Validation, Pattern Catalog, Recommendations, Sources)
- ✅ Pattern Catalog contains ≥3 patterns with canonical examples (SSE transport, tool registration, console buffering, store inspection)
- ✅ Recommendations section includes 3 explicit, actionable recommendations linked to Sprint 23 phases
- ✅ Security Constraints section documents SSRF, CSS selector injection, credential exposure, CORS policies
- ✅ Sources section cites ≥10 endogenous sources + ≥7 external sources
- ✅ YAML frontmatter includes `status: Final`, `closes_issue: 514`, `x-governs` axioms
- ✅ Document validates via `uv run python scripts/validate_synthesis.py docs/research/webmcp-browser-integration.md`

---

**Status**: Final  
**Closes**: #514 (WebMCP Ecosystem Research)  
**Sprint**: 23  
**Phase**: 1
