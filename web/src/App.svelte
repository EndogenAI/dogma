<script lang="ts">
  /**
   * MCP Dashboard — root shell.
   * Manages data state, SSE updates (via Sidebar), and polling.
   */
  import { onMount } from 'svelte';
  import { getSnapshot, isOffline } from './lib/api';
  import { BrowserMcpServer } from './lib/mcp-server';
  import type { MetricsSnapshot, ConnStatus } from './lib/types';
  import Overview from './lib/Overview.svelte';
  import Tools    from './lib/Tools.svelte';
  import Errors   from './lib/Errors.svelte';
  import Sidebar  from './lib/Sidebar.svelte';
  import fixtureData from './assets/fixture.json';

  let activeTab       = $state('overview');
  let data            = $state<MetricsSnapshot>(fixtureData as MetricsSnapshot);
  let connStatus      = $state<ConnStatus>('LIVE');
  let refreshInterval = $state<number>(10000);
  let offline         = $state<boolean>(true);
  let mcpServer       = $state<BrowserMcpServer | null>(null);

  /** Called by Sidebar when SSE delivers a new snapshot */
  function onData(snapshot: MetricsSnapshot): void {
    data = snapshot;
    offline = false;
  }

  onMount(() => {
    mcpServer = new BrowserMcpServer();
    void mcpServer.start();

    void (async () => {
      const snapshot = await getSnapshot();
      data = snapshot;
      offline = isOffline();
    })();

    return () => {
      if (mcpServer) {
        void mcpServer.stop();
      }
      mcpServer = null;
    };
  });

  // Re-create polling interval whenever refreshInterval changes
  $effect(() => {
    if (refreshInterval <= 0) return;
    const timer = setInterval(async () => {
      const snapshot = await getSnapshot();
      data = snapshot;
      offline = isOffline();
    }, refreshInterval);
    return () => clearInterval(timer);
  });

  let snapshotTs = $derived(
    data?.snapshot_ts
      ? new Date(data.snapshot_ts).toLocaleTimeString()
      : '--'
  );

  let healthDotClass = $derived(
    connStatus === 'LIVE' ? 'dot-green'
      : connStatus === 'STALE' ? 'dot-amber'
      : 'dot-red'
  );
</script>

<div class="app">
  <!-- Top navigation bar -->
  <nav class="topnav">
    <span class="app-title">MCP Dashboard</span>
    <span class="health-dot {healthDotClass}" title={connStatus}></span>
    <span class="ts-badge">Last updated: {snapshotTs}</span>
  </nav>

  <!-- Offline banner -->
  {#if offline}
    <div class="offline-banner" role="status">
      Offline — showing cached data
    </div>
  {/if}

  <!-- Main layout: content + sidebar -->
  <div class="layout">
    <main class="main-area">
      <!-- Tab bar -->
      <div class="tabs" role="tablist">
        <button
          type="button"
          class="tab"
          class:active={activeTab === 'overview'}
          role="tab"
          aria-selected={activeTab === 'overview'}
          onclick={() => { activeTab = 'overview'; }}
        >Overview</button>
        <button
          type="button"
          class="tab"
          class:active={activeTab === 'tools'}
          role="tab"
          aria-selected={activeTab === 'tools'}
          onclick={() => { activeTab = 'tools'; }}
        >Tools</button>
        <button
          type="button"
          class="tab"
          class:active={activeTab === 'errors'}
          role="tab"
          aria-selected={activeTab === 'errors'}
          onclick={() => { activeTab = 'errors'; }}
        >Errors</button>
      </div>

      <!-- Tab content -->
      <div class="tab-content">
        {#if activeTab === 'overview'}
          <Overview {data} />
        {:else if activeTab === 'tools'}
          <Tools {data} />
        {:else}
          <Errors {data} />
        {/if}
      </div>
    </main>

    <Sidebar {data} bind:connStatus bind:refreshInterval {onData} />
  </div>
</div>

<style>
  :global(*, *::before, *::after) { box-sizing: border-box; }
  :global(body) {
    margin: 0;
    font-family: system-ui, -apple-system, sans-serif;
    background: #fff;
    color: #1a1a2e;
  }

  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  /* ── Top nav ── */
  .topnav {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 1.25rem;
    background: #1a1a2e;
    color: #fff;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .app-title {
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.02em;
    margin-right: auto;
  }

  .health-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .dot-green { background: #27ae60; }
  .dot-amber { background: #e67e22; }
  .dot-red   { background: #e74c3c; }

  .ts-badge {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.65);
  }

  /* ── Offline banner ── */
  .offline-banner {
    background: #fff3cd;
    border-bottom: 1px solid #ffe69c;
    color: #856404;
    text-align: center;
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
    font-weight: 500;
  }

  /* ── Layout ── */
  .layout {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  .main-area {
    flex: 2;
    display: flex;
    flex-direction: column;
    overflow: auto;
    min-width: 0;
  }

  /* Sidebar receives flex: 1 via the Sidebar component itself — constrained here */
  :global(.sidebar) {
    flex: 1;
    max-width: 320px;
    overflow-y: auto;
  }

  /* ── Tabs ── */
  .tabs {
    display: flex;
    border-bottom: 2px solid #e0e0e0;
    padding: 0 1rem;
    background: #fff;
    position: sticky;
    top: 0;
    z-index: 5;
  }

  .tab {
    padding: 0.6rem 1.1rem;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 0.9rem;
    color: #666;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: color 0.15s, border-color 0.15s;
  }

  .tab:hover { color: #1a1a2e; }

  .tab.active {
    color: #4f8ef7;
    border-bottom-color: #4f8ef7;
    font-weight: 600;
  }

  .tab-content { flex: 1; overflow: auto; }

  /* ── Responsive: <900px stack sidebar below main ── */
  @media (max-width: 900px) {
    .layout { flex-direction: column; }
    :global(.sidebar) { max-width: 100%; border-left: none; border-top: 1px solid #e0e0e0; }
  }
</style>
