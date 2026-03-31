<script lang="ts">
  /**
   * Errors tab — tools with error_count > 0, filterable.
   * Each row expands to show the individual failure events.
   */
  import type { MetricsSnapshot } from './types';

  let { data }: { data: MetricsSnapshot } = $props();

  let searchQuery = $state<string>('');
  let expanded = $state<Set<string>>(new Set());

  function toggle(name: string): void {
    const next = new Set(expanded);
    if (next.has(name)) next.delete(name);
    else next.add(name);
    expanded = next;
  }

  function fmtTs(ts: string): string {
    if (!ts) return '—';
    try {
      return new Date(ts).toLocaleString(undefined, {
        month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
      });
    } catch {
      return ts;
    }
  }

  let toolsWithErrors = $derived(
    Object.entries(data?.tools ?? {})
      .filter(([, stats]) => stats.error_count > 0)
      .map(([name, stats]) => ({
        name,
        error_count: stats.error_count,
        invocation_count: stats.invocation_count,
        errorRate: stats.invocation_count > 0
          ? (stats.error_count / stats.invocation_count * 100).toFixed(1)
          : '0.0',
        recent_errors: stats.recent_errors ?? [],
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
        {@const isOpen = expanded.has(tool.name)}
        <li class="error-item" class:open={isOpen}>
          <button
            type="button"
            class="error-summary"
            aria-expanded={isOpen}
            onclick={() => toggle(tool.name)}
          >
            <span class="chevron" aria-hidden="true">{isOpen ? '▾' : '▸'}</span>
            <span class="tool-name">{tool.name}</span>
            <span class="error-stats">
              <span class="error-count">{tool.error_count} error{tool.error_count !== 1 ? 's' : ''}</span>
              <span class="error-rate">{tool.errorRate}% error rate</span>
            </span>
          </button>

          {#if isOpen}
            <div class="error-events">
              {#if tool.recent_errors.length === 0}
                <p class="no-events">No individual failure records available.</p>
              {:else}
                <table class="events-table">
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Type</th>
                      <th>Latency</th>
                      <th>Faithfulness</th>
                      <th>Correctness</th>
                      <th>Severity</th>
                      <th>Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each tool.recent_errors as ev, i (i)}
                      <tr>
                        <td class="col-ts">{#if ev.ts}{fmtTs(ev.ts)}{:else}<span class="dim">no timestamp</span>{/if}</td>
                        <td><span class="badge badge-{ev.error_type}">{ev.error_type}</span></td>
                        <td class="col-lat">{ev.latency_ms != null ? `${ev.latency_ms} ms` : '—'}</td>
                        <td class="col-score">{ev.faithfulness != null ? ev.faithfulness.toFixed(2) : '—'}</td>
                        <td class="col-score">{ev.correctness != null ? ev.correctness.toFixed(2) : '—'}</td>
                        <td class="col-score col-sev" class:sev-high={ev.severity_level != null && ev.severity_level > 1}>{ev.severity_level != null ? ev.severity_level.toFixed(2) : '—'}</td>
                        <td class="col-msg">{ev.message || 'This error did not include any details.'}</td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              {/if}
            </div>
          {/if}
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
    background: #fff5f5;
    border: 1px solid #fcc;
    border-radius: 8px;
    overflow: hidden;
  }

  .error-item.open { border-color: #e88; }

  .error-summary {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    width: 100%;
    padding: 0.75rem 1rem;
    background: none;
    border: none;
    cursor: pointer;
    text-align: left;
    font-family: inherit;
  }

  .error-summary:hover { background: #fff0f0; }

  .chevron {
    font-size: 0.75rem;
    color: #c0392b;
    flex-shrink: 0;
  }

  .tool-name {
    font-weight: 600;
    color: #1a1a2e;
    font-size: 0.9rem;
    flex: 1;
  }

  .error-stats {
    display: flex;
    gap: 1rem;
    font-size: 0.82rem;
  }

  .error-count { color: #c0392b; font-weight: 700; }
  .error-rate { color: #888; }

  /* ── Expanded failure events ─────────────────────────────────────────── */

  .error-events {
    border-top: 1px solid #fcc;
    padding: 0.5rem 1rem 0.75rem;
  }

  .no-events {
    font-size: 0.82rem;
    color: #aaa;
    margin: 0;
    padding: 0.25rem 0;
  }

  .events-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
  }

  .events-table th {
    text-align: left;
    color: #888;
    font-weight: 500;
    padding: 0.25rem 0.5rem;
    border-bottom: 1px solid #fcc;
  }

  .events-table td {
    padding: 0.3rem 0.5rem;
    vertical-align: top;
    border-bottom: 1px solid #fff0f0;
  }

  .events-table tr:last-child td { border-bottom: none; }

  .col-ts { white-space: nowrap; color: #888; }
  .col-lat { white-space: nowrap; font-variant-numeric: tabular-nums; }
  .col-score { white-space: nowrap; font-variant-numeric: tabular-nums; text-align: right; }
  .col-sev.sev-high { color: #c0392b; font-weight: 700; }
  .col-msg { color: #333; font-family: ui-monospace, monospace; word-break: break-word; }
  .dim { color: #bbb; font-style: italic; }

  .badge {
    display: inline-block;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    white-space: nowrap;
    background: #fde8e8;
    color: #c0392b;
  }

  .badge-timeout     { background: #fff3cd; color: #856404; }
  .badge-network_error { background: #e8f0fe; color: #1a56db; }
  .badge-validation_error { background: #f0e8ff; color: #6f42c1; }
</style>
