<script lang="ts">
  /**
   * Tools tab — sortable table with inline latency bar chart on row click.
   */
  import type { MetricsSnapshot } from './types';

  let { data }: { data: MetricsSnapshot } = $props();

  let selectedTool = $state<string | null>(null);

  let toolsArray = $derived(
    Object.entries(data?.tools ?? {})
      .map(([name, stats]) => ({
        name,
        invocation_count: stats.invocation_count,
        avg_latency_ms: stats.avg_latency_ms,
        p95_latency_ms: stats.p95_latency_ms,
        error_count: stats.error_count,
        errorRate: stats.invocation_count > 0
          ? stats.error_count / stats.invocation_count * 100
          : 0
      }))
      .sort((a, b) => b.invocation_count - a.invocation_count)
  );

  let maxP95 = $derived(
    Math.max(...toolsArray.map((t) => t.p95_latency_ms), 1)
  );

  function badge(rate: number): { label: string; cls: string } {
    if (rate === 0) return { label: 'OK', cls: 'green' };
    if (rate < 10) return { label: 'WARN', cls: 'amber' };
    return { label: 'ERROR', cls: 'red' };
  }

  function toggle(name: string): void {
    selectedTool = selectedTool === name ? null : name;
  }
</script>

<div class="tools">
  <table>
    <thead>
      <tr>
        <th>Tool Name</th>
        <th class="num">Invocations</th>
        <th class="num">Avg Latency ms</th>
        <th class="num">Error Rate %</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {#each toolsArray as tool (tool.name)}
        <tr
          class="tool-row"
          class:selected={selectedTool === tool.name}
          onclick={() => toggle(tool.name)}
          role="button"
          tabindex="0"
          onkeydown={(e) => e.key === 'Enter' && toggle(tool.name)}
        >
          <td class="name-cell">{tool.name}</td>
          <td class="num">{tool.invocation_count}</td>
          <td class="num">{tool.avg_latency_ms}</td>
          <td class="num">{tool.errorRate.toFixed(1)}%</td>
          <td>
            <span class="badge badge-{badge(tool.errorRate).cls}">{badge(tool.errorRate).label}</span>
          </td>
        </tr>
        {#if selectedTool === tool.name}
          <tr class="detail-row">
            <td colspan="5">
              <div class="detail">
                <strong>Latency breakdown</strong>
                <div class="bar-chart">
                  <div class="bar-row">
                    <span class="bar-label">Avg</span>
                    <div class="bar bar-avg" style="width:{Math.round(tool.avg_latency_ms / maxP95 * 200)}px"></div>
                    <span class="bar-val">{tool.avg_latency_ms}ms</span>
                  </div>
                  <div class="bar-row">
                    <span class="bar-label">p95</span>
                    <div class="bar bar-p95" style="width:{Math.round(tool.p95_latency_ms / maxP95 * 200)}px"></div>
                    <span class="bar-val">{tool.p95_latency_ms}ms</span>
                  </div>
                </div>
              </div>
            </td>
          </tr>
        {/if}
      {/each}
    </tbody>
  </table>
</div>

<style>
  .tools { padding: 1rem; overflow-x: auto; }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
  }

  th {
    text-align: left;
    padding: 0.5rem 0.75rem;
    border-bottom: 2px solid #e0e0e0;
    color: #555;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  th.num, td.num { text-align: right; }

  td {
    padding: 0.6rem 0.75rem;
    border-bottom: 1px solid #f0f0f0;
    vertical-align: middle;
  }

  .tool-row {
    cursor: pointer;
    transition: background 0.1s;
  }

  .tool-row:hover { background: #f5f8ff; }
  .tool-row.selected { background: #eef3ff; }

  .name-cell { font-weight: 500; color: #1a1a2e; }

  .badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .badge-green { background: #d4edda; color: #155724; }
  .badge-amber { background: #fff3cd; color: #856404; }
  .badge-red   { background: #f8d7da; color: #721c24; }

  .detail-row td {
    background: #f9fbff;
    padding: 0.75rem 1.25rem;
    border-bottom: 2px solid #e0e0e0;
  }

  .detail strong { font-size: 0.82rem; color: #555; }

  .bar-chart {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-top: 0.5rem;
  }

  .bar-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .bar-label {
    width: 2.5rem;
    font-size: 0.75rem;
    color: #888;
  }

  .bar {
    height: 14px;
    border-radius: 3px;
    min-width: 4px;
  }

  .bar-avg { background: #4f8ef7; }
  .bar-p95 { background: #e67e22; }

  .bar-val {
    font-size: 0.75rem;
    color: #555;
    width: 4rem;
  }
</style>
