/**
 * Minimal browser MCP PoC server facade (Phase 2).
 *
 * Purpose:
 * - Provide a tiny browser-side entrypoint for MCP handshake + tool registration.
 * - Keep transport posture aligned with SSE/fetch (no WebSocket).
 *
 * Scope:
 * - Registers a single `ping` tool.
 * - `ping` returns { status: "ok" }.
 */

export type PingResult = { status: 'ok' };

export type BrowserMcpServerOptions = {
  /** Same-origin endpoint root used for optional fetch/SSE handshake checks. */
  endpoint?: string;
  /** Off by default so app startup does not depend on live SSE during Phase 2 PoC. */
  enableSseProbe?: boolean;
};

type ToolHandler = () => PingResult | Promise<PingResult>;

export class BrowserMcpServer {
  private readonly endpoint: string;
  private readonly enableSseProbe: boolean;
  private readonly tools = new Map<string, ToolHandler>();
  private eventSource: EventSource | null = null;
  private started = false;

  constructor(options: BrowserMcpServerOptions = {}) {
    this.endpoint = options.endpoint ?? '/mcp';
    this.enableSseProbe = options.enableSseProbe ?? false;

    this.registerTool('ping', async () => ({ status: 'ok' }));
  }

  async start(): Promise<void> {
    if (this.started) return;
    this.started = true;

    if (!this.enableSseProbe) return;

    // SSE alignment: EventSource over HTTP, no WebSocket transport in this phase.
    this.eventSource = new EventSource(`${this.endpoint}/events`);
    this.eventSource.onerror = () => {
      this.eventSource?.close();
      this.eventSource = null;
    };
  }

  async stop(): Promise<void> {
    this.eventSource?.close();
    this.eventSource = null;
    this.started = false;
  }

  async ping(): Promise<PingResult> {
    const handler = this.tools.get('ping');
    if (!handler) {
      throw new Error('ping tool not registered');
    }
    return await handler();
  }

  async callTool(name: 'ping'): Promise<PingResult> {
    if (name !== 'ping') {
      throw new Error(`Unknown tool: ${name}`);
    }
    return this.ping();
  }

  async probeHandshake(): Promise<boolean> {
    const response = await fetch(`${this.endpoint}/handshake`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    return response.ok;
  }

  private registerTool(name: 'ping', handler: ToolHandler): void {
    this.tools.set(name, handler);
  }
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
