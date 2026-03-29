<script lang="ts">
  /**
   * Errors tab — tools with error_count > 0, filterable.
   */
  import type { MetricsSnapshot } from './types';

  let { data }: { data: MetricsSnapshot } = $props();

  let searchQuery = $state<string>('');

  let toolsWithErrors = $derived(
    Object.entries(data?.tools ?? {})
      .filter(([, stats]) => stats.error_count > 0)
      .map(([name, stats]) => ({
        name,
        error_count: stats.error_count,
        invocation_count: stats.invocation_count,
        errorRate: stats.invocation_count > 0
          ? (stats.error_count / stats.invocation_count * 100).toFixed(1)
          : '0.0'
      }))
      .sort((a, b) => b.error_count - a.error_count)
  );

  let filtered = $derived(
    toolsWithErrors.filter((t) =>
      t.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );
</script>

<div class="errors">
  <div class="search-row">
    <input
      type="search"
      placeholder="Filter by tool name…"
      bind:value={searchQuery}
      class="search-input"
    />
  </div>

  {#if toolsWithErrors.length === 0}
    <div class="empty-state">No errors recorded.</div>
  {:else if filtered.length === 0}
    <div class="empty-state">No tools match "{searchQuery}".</div>
  {:else}
    <ul class="error-list">
      {#each filtered as tool (tool.name)}
        <li class="error-item">
          <div class="tool-name">{tool.name}</div>
          <div class="error-stats">
            <span class="error-count">{tool.error_count} error{tool.error_count !== 1 ? 's' : ''}</span>
            <span class="error-rate">{tool.errorRate}% error rate</span>
          </div>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .errors { padding: 1rem; }

  .search-row { margin-bottom: 1rem; }

  .search-input {
    width: 100%;
    max-width: 360px;
    padding: 0.4rem 0.75rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 0.9rem;
    outline: none;
  }

  .search-input:focus { border-color: #4f8ef7; }

  .empty-state {
    color: #888;
    font-size: 0.9rem;
    padding: 2rem 0;
  }

  .error-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .error-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #fff5f5;
    border: 1px solid #fcc;
    border-radius: 8px;
    padding: 0.75rem 1rem;
  }

  .tool-name {
    font-weight: 600;
    color: #1a1a2e;
    font-size: 0.9rem;
  }

  .error-stats {
    display: flex;
    gap: 1rem;
    font-size: 0.82rem;
  }

  .error-count { color: #c0392b; font-weight: 700; }
  .error-rate { color: #888; }
</style>
