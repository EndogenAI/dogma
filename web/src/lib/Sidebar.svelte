<script lang="ts">
  /**
   * Sidebar — connection state machine (LIVE → STALE → ERROR),
   * recent tool calls, and polling interval controls.
   *
   * Connection state machine:
   *   LIVE  — EventSource.onopen fired; green dot
   *   STALE — onerror fired; exponential backoff 2s→4s→8s→16s→30s; amber dot
   *   ERROR — 5 consecutive failures; red dot
   *
   * Props:
   *   data           — metrics snapshot
   *   connStatus     — $bindable; App.svelte nav bar reads this
   *   refreshInterval — $bindable; controls App.svelte polling interval
   *   onData         — callback(snapshot) when SSE delivers new data
   */
  import { onMount } from 'svelte';
  import { subscribeStream } from './api';
  import type { MetricsSnapshot, ConnStatus } from './types';

  interface Props {
    data: MetricsSnapshot;
    connStatus?: ConnStatus;
    refreshInterval?: number;
    onData?: ((s: MetricsSnapshot) => void) | null;
  }

  let {
    data,
    connStatus = $bindable('LIVE' as ConnStatus),
    refreshInterval = $bindable(10000),
    onData = null
  }: Props = $props();

  let failCount    = $state<number>(0);
  let lastUpdated  = $state<Date | null>(null);
  let backoffMs    = $state<number>(2000);
  let reconnectTimer = $state<ReturnType<typeof setTimeout> | null>(null);

  let recentTools = $derived(
    Object.entries(data?.tools ?? {})
      .map(([name, stats]) => ({ name, ...stats }))
      .sort((a, b) => b.invocation_count - a.invocation_count)
      .slice(0, 5)
  );

  let lastUpdatedStr = $derived.by(() => {
    if (!lastUpdated) return '';
    const diffMs = Date.now() - lastUpdated.getTime();
    const mins = Math.floor(diffMs / 60000);
    return mins === 0 ? 'just now' : `${mins} min ago`;
  });

  let currentUnsub: (() => void) | null = null;

  function connect(): void {
    if (currentUnsub) { currentUnsub(); currentUnsub = null; }

    currentUnsub = subscribeStream(
      (snapshot) => {
        connStatus = 'LIVE';
        failCount = 0;
        backoffMs = 2000;
        lastUpdated = new Date();
        if (onData) onData(snapshot);
      },
      () => {
        if (currentUnsub) { currentUnsub(); currentUnsub = null; }
        failCount = failCount + 1;
        if (failCount >= 5) {
          connStatus = 'ERROR';
        } else {
          connStatus = 'STALE';
          const delay = backoffMs;
          reconnectTimer = setTimeout(() => {
            backoffMs = Math.min(backoffMs * 2, 30000);
            connect();
          }, delay);
        }
      }
    );
  }

  onMount(() => {
    connect();
    return () => {
      if (currentUnsub) currentUnsub();
      if (reconnectTimer) clearTimeout(reconnectTimer);
    };
  });

  const INTERVALS = [
    { label: '5s',     value: 5000  },
    { label: '10s',    value: 10000 },
    { label: '30s',    value: 30000 },
    { label: 'Paused', value: 0     }
  ];
</script>

<aside class="sidebar">
  <!-- Connection status -->
  <div class="status-section">
    <span
      class="dot"
      class:dot-green={connStatus === 'LIVE'}
      class:dot-amber={connStatus === 'STALE'}
      class:dot-red={connStatus === 'ERROR'}
    ></span>
    {#if connStatus === 'LIVE'}
      <span class="status-label">Connected</span>
    {:else if connStatus === 'STALE'}
      <span class="status-label">Last updated {lastUpdatedStr}</span>
    {:else}
      <span class="status-label">Connection lost</span>
    {/if}
  </div>

  <!-- Recent tools -->
  <section class="section">
    <h4 class="section-title">Recent Tools</h4>
    <ul class="tool-list">
      {#each recentTools as tool (tool.name)}
        <li class="tool-entry">
          <span class="tool-name">{tool.name}</span>
          <span
            class="badge"
            class:badge-green={tool.error_count === 0}
            class:badge-red={tool.error_count > 0}
          >
            {tool.error_count === 0 ? '✓' : `${tool.error_count} err`}
          </span>
        </li>
      {/each}
    </ul>
  </section>

  <!-- Polling interval -->
  <section class="section">
    <h4 class="section-title">Polling Interval</h4>
    <p class="section-help">Applies to REST polling; live SSE updates continue.</p>
    <div class="refresh-btns">
      {#each INTERVALS as opt (opt.value)}
        <button
          type="button"
          class="refresh-btn"
          class:active={refreshInterval === opt.value}
          onclick={() => { refreshInterval = opt.value; }}
        >
          {opt.label}
        </button>
      {/each}
    </div>
  </section>
</aside>

<style>
  .sidebar {
    width: 100%;
    background: #f8f9fa;
    border-left: 1px solid #e0e0e0;
    padding: 1rem;
    font-size: 0.88rem;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .status-section {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #e0e0e0;
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .dot-green { background: #27ae60; box-shadow: 0 0 0 2px rgba(39,174,96,0.25); }
  .dot-amber { background: #e67e22; box-shadow: 0 0 0 2px rgba(230,126,34,0.25); }
  .dot-red   { background: #e74c3c; box-shadow: 0 0 0 2px rgba(231,76,60,0.25);  }

  .status-label { font-size: 0.82rem; color: #555; }

  .section { display: flex; flex-direction: column; gap: 0.5rem; }

  .section-help {
    margin: 0;
    font-size: 0.72rem;
    color: #7a7a7a;
  }

  .section-title {
    margin: 0;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #888;
  }

  .tool-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .tool-entry {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
  }

  .tool-name {
    font-size: 0.82rem;
    color: #333;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .badge {
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    flex-shrink: 0;
  }

  .badge-green { background: #d4edda; color: #155724; }
  .badge-red   { background: #f8d7da; color: #721c24; }

  .refresh-btns {
    display: flex;
    gap: 0.35rem;
    flex-wrap: wrap;
  }

  .refresh-btn {
    padding: 0.3rem 0.65rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: #fff;
    cursor: pointer;
    font-size: 0.8rem;
    color: #555;
    transition: all 0.15s;
  }

  .refresh-btn:hover { border-color: #4f8ef7; color: #4f8ef7; }

  .refresh-btn.active {
    background: #4f8ef7;
    border-color: #4f8ef7;
    color: #fff;
  }
</style>
