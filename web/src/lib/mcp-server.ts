/**
 * Minimal browser MCP PoC server facade (Phase 2).
 *
 * Purpose:
 * - Provide a tiny browser-side entrypoint for MCP handshake + tool registration.
 * - Keep transport posture aligned with SSE/fetch (no WebSocket).
 *
 * Scope:
 * - Registers `ping` plus Phase 3 inspector tools.
 * - Provides safe DOM querying, console log inspection, component-state snapshots,
 *   and constrained UI action triggering.
 */

import {
  installConsoleBuffer,
  type ConsoleBufferApi,
  type ConsoleEntry,
  type ConsoleLevel,
} from './console-buffer';

export type PingResult = { status: 'ok' };

export type DomElementSummary = {
  tag: string;
  id: string;
  className: string;
  text: string;
};

export type QueryDomResult = {
  elements: DomElementSummary[];
  count: number;
};

export type GetConsoleLogsResult = {
  entries: ConsoleEntry[];
  count: number;
};

export type GetComponentStateResult = {
  component?: string;
  state: Record<string, unknown> | unknown;
  count: number;
};

export type TriggerActionInput =
  | { type: 'click'; selector: string }
  | {
      type: 'input';
      selector: string;
      value: string;
      eventType?: 'input' | 'change' | 'both';
    };

export type TriggerActionResult = {
  ok: boolean;
  action: TriggerActionInput['type'];
  selector: string;
};

export type BrowserMcpServerOptions = {
  /** Same-origin endpoint root used for optional fetch/SSE handshake checks. */
  endpoint?: string;
  /** Off by default so app startup does not depend on live SSE during Phase 2 PoC. */
  enableSseProbe?: boolean;
  /** Console entry retention bound for get_console_logs. */
  maxConsoleEntries?: number;
};

type BridgeSessionResponse = {
  sessionId: string;
  pollMaxSeconds?: number;
  toolNames?: string[];
};

type BridgeToolRequest = {
  requestId: string;
  toolName: string;
  arguments?: unknown;
};

type ToolName =
  | 'ping'
  | 'query_dom'
  | 'get_console_logs'
  | 'get_component_state'
  | 'trigger_action';

type ComponentSnapshotter = () => unknown;

type ToolResult =
  | PingResult
  | QueryDomResult
  | GetConsoleLogsResult
  | GetComponentStateResult
  | TriggerActionResult;

type ToolHandler = (input?: unknown) => ToolResult | Promise<ToolResult>;

const MAX_SELECTOR_LENGTH = 256;
const MAX_QUERY_RESULTS = 100;
const MAX_INPUT_VALUE_LENGTH = 5000;

function ensureString(value: unknown, fieldName: string): string {
  if (typeof value !== 'string') {
    throw new Error(`${fieldName} must be a string`);
  }
  return value;
}

function sanitizeSelector(selector: unknown): string {
  const value = ensureString(selector, 'selector').trim();
  if (!value) {
    throw new Error('selector cannot be empty');
  }
  if (value.length > MAX_SELECTOR_LENGTH) {
    throw new Error(`selector too long (max ${MAX_SELECTOR_LENGTH})`);
  }
  if (/[\n\r\0]/.test(value)) {
    throw new Error('selector contains invalid control characters');
  }
  return value;
}

function truncateText(value: string, max = 200): string {
  const normalized = value.replace(/\s+/g, ' ').trim();
  if (normalized.length <= max) return normalized;
  return `${normalized.slice(0, max - 1)}...`;
}

export class BrowserMcpServer {
  private readonly endpoint: string;
  private readonly enableSseProbe: boolean;
  private readonly tools = new Map<ToolName, ToolHandler>();
  private readonly consoleBuffer: ConsoleBufferApi;
  private readonly componentRegistry = new Map<string, ComponentSnapshotter>();
  private eventSource: EventSource | null = null;
  private bridgeSessionId: string | null = null;
  private bridgeLoop: Promise<void> | null = null;
  private bridgeAbortController: AbortController | null = null;
  private started = false;

  constructor(options: BrowserMcpServerOptions = {}) {
    this.endpoint = options.endpoint ?? 'http://localhost:8000/mcp';
    this.enableSseProbe = options.enableSseProbe ?? false;
    this.consoleBuffer = installConsoleBuffer({
      maxEntries: options.maxConsoleEntries,
    });

    this.registerTool('ping', async () => ({ status: 'ok' }));
    this.registerTool('query_dom', (input) => this.queryDom(input));
    this.registerTool('get_console_logs', (input) => this.getConsoleLogs(input));
    this.registerTool('get_component_state', (input) => this.getComponentState(input));
    this.registerTool('trigger_action', (input) => this.triggerAction(input));
  }

  // Start optional transport probing hooks for local diagnostics.
  async start(): Promise<void> {
    if (this.started) return;
    this.started = true;

    const bridgeRegistered = await this.registerBridgeSession();
    if (bridgeRegistered) {
      this.bridgeAbortController = new AbortController();
      this.bridgeLoop = this.runBridgeLoop(this.bridgeAbortController.signal);
    }

    if (!this.enableSseProbe) return;

    // SSE alignment: EventSource over HTTP, no WebSocket transport in this phase.
    this.eventSource = new EventSource(`${this.endpoint}/events`);
    this.eventSource.onerror = () => {
      this.eventSource?.close();
      this.eventSource = null;
    };
  }

  async stop(): Promise<void> {
    this.bridgeAbortController?.abort();
    this.bridgeAbortController = null;
    try {
      await this.bridgeLoop;
    } catch {
      // Ignore shutdown races from aborted fetch calls.
    }
    this.bridgeLoop = null;
    this.bridgeSessionId = null;

    this.eventSource?.close();
    this.eventSource = null;
    this.started = false;
  }

  async ping(): Promise<PingResult> {
    const handler = this.tools.get('ping');
    if (!handler) {
      throw new Error('ping tool not registered');
    }
    return (await handler()) as PingResult;
  }

  async callTool(name: 'ping'): Promise<PingResult>;
  async callTool(name: 'query_dom', input: string): Promise<QueryDomResult>;
  async callTool(
    name: 'get_console_logs',
    input?: { level?: ConsoleLevel }
  ): Promise<GetConsoleLogsResult>;
  async callTool(
    name: 'get_component_state',
    input?: { component?: string }
  ): Promise<GetComponentStateResult>;
  async callTool(
    name: 'trigger_action',
    input: TriggerActionInput
  ): Promise<TriggerActionResult>;
  async callTool(name: ToolName, input?: unknown): Promise<ToolResult> {
    const handler = this.tools.get(name);
    if (!handler) {
      throw new Error(`Unknown tool: ${name}`);
    }
    return await handler(input);
  }

  // Treat network failures as unreachable handshake, not fatal errors.
  async probeHandshake(): Promise<boolean> {
    try {
      const response = await fetch(`${this.endpoint}/handshake`, {
        method: 'GET',
        headers: { Accept: 'application/json' },
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  registerComponentState(component: string, snapshotter: ComponentSnapshotter): void {
    const name = ensureString(component, 'component').trim();
    if (!name) {
      throw new Error('component cannot be empty');
    }
    this.componentRegistry.set(name, snapshotter);
  }

  unregisterComponentState(component: string): void {
    this.componentRegistry.delete(component);
  }

  // Query DOM with selector validation and bounded response payloads.
  private queryDom(input: unknown): QueryDomResult {
    const selector = sanitizeSelector(input);
    let nodes: Element[];

    try {
      nodes = Array.from(document.querySelectorAll(selector));
    } catch {
      throw new Error('invalid CSS selector');
    }

    const elements = nodes.slice(0, MAX_QUERY_RESULTS).map((node) => {
      const element = node as HTMLElement;
      return {
        tag: node.tagName.toLowerCase(),
        id: node.id ?? '',
        className: node.getAttribute('class') ?? '',
        text: truncateText(element.innerText ?? node.textContent ?? ''),
      };
    });

    return {
      elements,
      count: nodes.length,
    };
  }

  // Return buffered console entries, optionally filtered by level.
  private getConsoleLogs(input?: unknown): GetConsoleLogsResult {
    const level =
      input && typeof input === 'object' && 'level' in input
        ? (input as { level?: unknown }).level
        : undefined;

    let normalizedLevel: ConsoleLevel | undefined;
    if (level !== undefined) {
      const value = ensureString(level, 'level').toLowerCase();
      if (!['debug', 'info', 'log', 'warn', 'error'].includes(value)) {
        throw new Error('invalid console level');
      }
      normalizedLevel = value as ConsoleLevel;
    }

    const entries = this.consoleBuffer.getEntries(normalizedLevel);
    return {
      entries,
      count: entries.length,
    };
  }

  // Return one registered component snapshot or all registered snapshots.
  private getComponentState(input?: unknown): GetComponentStateResult {
    const component =
      input && typeof input === 'object' && 'component' in input
        ? (input as { component?: unknown }).component
        : undefined;

    if (component !== undefined) {
      const key = ensureString(component, 'component').trim();
      const snapshotter = this.componentRegistry.get(key);
      if (!snapshotter) {
        throw new Error(`component not registered: ${key}`);
      }
      return {
        component: key,
        state: snapshotter(),
        count: 1,
      };
    }

    const state: Record<string, unknown> = {};
    for (const [name, snapshotter] of this.componentRegistry.entries()) {
      state[name] = snapshotter();
    }

    return {
      state,
      count: Object.keys(state).length,
    };
  }

  // Trigger constrained UI actions for testing (click/input only).
  private triggerAction(input: unknown): TriggerActionResult {
    if (!input || typeof input !== 'object') {
      throw new Error('event payload must be an object');
    }

    const payload = input as Record<string, unknown>;
    const actionType = ensureString(payload.type, 'type').toLowerCase();
    if (actionType !== 'click' && actionType !== 'input') {
      throw new Error('unsupported action type');
    }

    const selector = sanitizeSelector(payload.selector);
    const element = document.querySelector(selector);
    if (!element) {
      throw new Error(`element not found for selector: ${selector}`);
    }

    if (actionType === 'click') {
      if (!(element instanceof HTMLElement)) {
        throw new Error('target element is not clickable');
      }
      element.click();
      return { ok: true, action: 'click', selector };
    }

    if (!(element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement)) {
      throw new Error('input action requires input or textarea element');
    }

    const value = ensureString(payload.value, 'value');
    if (value.length > MAX_INPUT_VALUE_LENGTH) {
      throw new Error(`value too long (max ${MAX_INPUT_VALUE_LENGTH})`);
    }

    const eventTypeRaw = payload.eventType ?? 'both';
    const eventType = ensureString(eventTypeRaw, 'eventType').toLowerCase();
    if (!['input', 'change', 'both'].includes(eventType)) {
      throw new Error('eventType must be input, change, or both');
    }

    element.value = value;
    if (eventType === 'input' || eventType === 'both') {
      element.dispatchEvent(new Event('input', { bubbles: true }));
    }
    if (eventType === 'change' || eventType === 'both') {
      element.dispatchEvent(new Event('change', { bubbles: true }));
    }

    return { ok: true, action: 'input', selector };
  }

  private registerTool(name: ToolName, handler: ToolHandler): void {
    this.tools.set(name, handler);
  }

  private async registerBridgeSession(): Promise<boolean> {
    try {
      const response = await fetch(`${this.endpoint}/browser/session`, {
        method: 'POST',
        headers: { Accept: 'application/json' },
      });
      if (!response.ok) {
        return false;
      }

      const payload = (await response.json()) as Partial<BridgeSessionResponse>;
      if (typeof payload.sessionId !== 'string' || !payload.sessionId) {
        return false;
      }

      this.bridgeSessionId = payload.sessionId;
      return true;
    } catch {
      return false;
    }
  }

  private async runBridgeLoop(signal: AbortSignal): Promise<void> {
    while (this.started && this.bridgeSessionId && !signal.aborted) {
      try {
        const sessionId = this.bridgeSessionId;
        if (!sessionId) {
          break;
        }

        const response = await fetch(
          `${this.endpoint}/browser/poll?session_id=${encodeURIComponent(sessionId)}`,
          {
            method: 'GET',
            headers: { Accept: 'application/json' },
            signal,
          }
        );

        if (response.status === 204) {
          continue;
        }

        if (!response.ok) {
          this.bridgeSessionId = null;
          const rebound = await this.registerBridgeSession();
          if (!rebound) {
            await this.sleep(1000, signal);
          }
          continue;
        }

        const payload = (await response.json()) as Partial<BridgeToolRequest>;
        if (typeof payload.requestId !== 'string' || typeof payload.toolName !== 'string') {
          await this.sleep(250, signal);
          continue;
        }

        await this.fulfillBridgeRequest(payload as BridgeToolRequest, signal);
      } catch {
        if (signal.aborted) {
          return;
        }
        await this.sleep(1000, signal);
      }
    }
  }

  private async fulfillBridgeRequest(request: BridgeToolRequest, signal: AbortSignal): Promise<void> {
    if (!this.bridgeSessionId) {
      return;
    }

    const responsePayload: Record<string, unknown> = {
      sessionId: this.bridgeSessionId,
      requestId: request.requestId,
      ok: false,
    };

    try {
      if (!isToolName(request.toolName)) {
        throw new Error(`Unknown tool: ${request.toolName}`);
      }

      // query_dom's callTool overload expects a bare selector string,
      // but MCP arguments arrive as {selector: string}. Unwrap it.
      let toolInput: unknown = request.arguments;
      if (request.toolName === 'query_dom') {
        toolInput = (request.arguments as Record<string, unknown>).selector;
      }

      responsePayload.result = await this.callTool(request.toolName, toolInput);
      responsePayload.ok = true;
    } catch (error) {
      responsePayload.error = error instanceof Error ? error.message : 'Unknown bridge error';
    }

    await fetch(`${this.endpoint}/browser/respond`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(responsePayload),
      signal,
    });
  }

  private async sleep(delayMs: number, signal: AbortSignal): Promise<void> {
    await new Promise<void>((resolve) => {
      let settled = false;
      let timeoutId = 0;

      const finish = () => {
        if (settled) {
          return;
        }
        settled = true;
        window.clearTimeout(timeoutId);
        signal.removeEventListener('abort', onAbort);
        resolve();
      };

      const onAbort = () => {
        finish();
      };

      timeoutId = window.setTimeout(finish, delayMs);
      signal.addEventListener('abort', onAbort, { once: true });
    });
  }
}

function isToolName(value: string): value is ToolName {
  return [
    'ping',
    'query_dom',
    'get_console_logs',
    'get_component_state',
    'trigger_action',
  ].includes(value);
}

/**
 * Manual verification helper for Phase 2:
 * 1) await verifyHandshakeAndPing(server)
 * 2) confirm { handshake: boolean, ping: { status: "ok" } }
 */
export async function verifyHandshakeAndPing(server: BrowserMcpServer): Promise<{
  handshake: boolean;
  ping: PingResult;
}> {
  const handshake = await server.probeHandshake();
  const ping = await server.ping();
  return { handshake, ping };
}
