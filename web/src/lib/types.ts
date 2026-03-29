/**
 * types.ts — shared TypeScript interfaces for the MCP Dashboard.
 *
 * All components accept a `MetricsSnapshot` as their primary `data` prop.
 * The shape mirrors the FastAPI sidecar's `/api/metrics` response and the
 * fixture at `src/assets/fixture.json`.
 */

/** Per-tool telemetry aggregates. */
export interface ToolStats {
  invocation_count: number;
  error_count: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
}

/** Top-level metrics envelope returned by `/api/metrics`. */
export interface MetricsSnapshot {
  snapshot_ts: string;
  tools: Record<string, ToolStats>;
}

/** Connection status union — drives the nav-bar health dot. */
export type ConnStatus = 'LIVE' | 'STALE' | 'ERROR';

/** (x, y) data point for sparkline / chart components. */
export interface DataPoint {
  x: number;
  y: number;
}
