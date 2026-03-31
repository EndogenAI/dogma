/**
 * types.ts — shared TypeScript interfaces for the MCP Dashboard.
 *
 * All components accept a `MetricsSnapshot` as their primary `data` prop.
 * The shape mirrors the FastAPI sidecar's `/api/metrics` response and the
 * fixture at `src/assets/fixture.json`.
 */

/** Per-tool telemetry aggregates. */
export interface ErrorEvent {
  ts: string;
  latency_ms: number | null;
  error_type: string;
  message: string;
  faithfulness?: number | null;
  correctness?: number | null;
  severity_level?: number | null;
}

export interface ToolStats {
  invocation_count: number;
  error_count: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
  recent_errors?: ErrorEvent[];
}

/** Top-level metrics envelope returned by `/api/metrics`. */
export interface MetricsSnapshot {
  snapshot_ts: string;
  tools: Record<string, ToolStats>;
}

/** Connection status union — drives the nav-bar health dot. */
export type ConnStatus = 'LIVE' | 'STALE' | 'ERROR';

/** Browser-side MCP bridge lifecycle state. */
export type BridgeStatus = 'DISABLED' | 'CONNECTING' | 'CONNECTED' | 'ERROR';

/** (x, y) data point for sparkline / chart components. */
export interface DataPoint {
  x: number;
  y: number;
}
