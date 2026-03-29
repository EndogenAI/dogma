/**
 * api.js — MCP Dashboard API Client
 *
 * Provides two data-access patterns for the dogmaMCP/FastAPI sidecar
 * (web/server.py) running at http://localhost:8000:
 *
 *   1. Snapshot polling  — `getSnapshot()` issues a single HTTP GET to
 *      `/api/metrics` and returns the full metrics JSON payload.  Falls
 *      back to `src/assets/fixture.json` when the sidecar is unreachable
 *      and marks the connection as offline.
 *
 *   2. SSE streaming     — `subscribeStream(onData, onError)` opens a
 *      persistent EventSource to `/api/metrics/stream`.  Each server-sent
 *      event carries the same metrics JSON envelope as the snapshot
 *      endpoint, emitted whenever the sidecar detects new telemetry.
 *      Returns an unsubscribe function that closes the EventSource.
 *
 * Offline state is tracked via the module-level `_isOffline` flag.
 * `isOffline()` is exported so Svelte components can reactively derive
 * banner visibility.  The flag is set on every fetch failure or SSE error
 * and cleared on the next successful response or stream open.
 *
 * Usage:
 *   import { getSnapshot, subscribeStream, isOffline } from './api.js';
 *
 *   // Polling
 *   const data = await getSnapshot();
 *
 *   // Streaming
 *   const unsub = subscribeStream(
 *     (data) => { // handle data
 *     },
 *     ()     => { // handle error
 *     }
 *   );
 *   onDestroy(unsub);
 */
import fixtureData from '../assets/fixture.json';

/** @type {boolean} True when the sidecar is unreachable; initialised to true
 *  so the first render before any fetch completes is treated as offline. */
let _isOffline = true;

/**
 * Returns the current offline state.
 * Reactive use: call inside a `$derived` block or within a polling interval
 * so changes to `_isOffline` propagate to Svelte's reactivity system.
 * @returns {boolean}
 */
export function isOffline() { return _isOffline; }

/**
 * Fetch a complete metrics snapshot from the sidecar.
 *
 * On success: clears the offline flag and returns parsed JSON.
 * On failure: sets the offline flag and returns fixture data so the UI
 *             remains functional in disconnected development environments.
 *
 * @returns {Promise<object>} Metrics payload or fixture fallback.
 */
export async function getSnapshot() {
  try {
    const resp = await fetch('http://localhost:8000/api/metrics');
    if (!resp.ok) throw new Error('fetch failed');
    _isOffline = false;
    return resp.json();
  } catch {
    _isOffline = true;
    return fixtureData;
  }
}

/**
 * Open a persistent SSE connection to the sidecar's metrics stream.
 *
 * The stream emits the same JSON envelope as `getSnapshot()` whenever the
 * sidecar records new telemetry events.  The EventSource is closed when the
 * returned unsubscribe function is called (typically in `onDestroy`).
 *
 * Offline behaviour: the `onerror` handler sets the offline flag before
 * calling `onError`, so callers can stop polling until the banner clears.
 *
 * @param {(data: object) => void} onData  - Called for every SSE message.
 * @param {() => void}            onError - Called when the stream errors.
 * @returns {() => void} Unsubscribe function — call to close the EventSource.
 */
export function subscribeStream(onData, onError) {
  const es = new EventSource('http://localhost:8000/api/metrics/stream');
  es.onopen = () => { _isOffline = false; };
  es.onmessage = (e) => { onData(JSON.parse(e.data)); };
  es.onerror = () => {
    _isOffline = true;
    onError();
  };
  return () => es.close(); // returns unsubscribe fn
}
