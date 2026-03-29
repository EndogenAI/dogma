<script>
  /**
   * Overview tab — summary cards + top-3 sparklines.
    * Uses the local Line component for lightweight trend rendering.
    * Keep charting lightweight and LayerCake-compatible per ADR-009.
   */
  import Line from '../charts/Line.svelte';

  let { data } = $props();

  let toolsArray = $derived(
    Object.entries(data?.tools ?? {}).map(([name, stats]) => ({ name, ...stats }))
  );

  let totalInvocations = $derived(
    toolsArray.reduce((s, t) => s + t.invocation_count, 0)
  );

  let totalErrors = $derived(
    toolsArray.reduce((s, t) => s + t.error_count, 0)
  );

  let errorRate = $derived(
    totalInvocations > 0
      ? (totalErrors / totalInvocations * 100).toFixed(1)
      : '0.0'
  );

  let avgLatency = $derived(
    toolsArray.length > 0
      ? Math.round(toolsArray.reduce((s, t) => s + t.avg_latency_ms, 0) / toolsArray.length)
      : 0
  );

  let top3 = $derived(
    [...toolsArray]
      .sort((a, b) => b.invocation_count - a.invocation_count)
      .slice(0, 3)
  );
</script>

<div class="overview">
  <div class="cards">
    <div class="card">
      <div class="label">Total Invocations</div>
      <div class="value">{totalInvocations}</div>
    </div>
    <div class="card">
      <div class="label">Error Rate %</div>
      <div class="value">{errorRate}%</div>
    </div>
    <div class="card">
      <div class="label">Avg Latency ms</div>
      <div class="value">{avgLatency}</div>
    </div>
  </div>

  <h3>Top 3 Tools — Latency Trend</h3>
  <p class="note">Trend data available after live capture</p>

  <div class="sparklines">
    {#each top3 as tool (tool.name)}
      <div class="sparkline-item">
        <div class="tool-name">{tool.name}</div>
        <Line data={[{ x: 0, y: tool.avg_latency_ms }]} />
        <div class="latency">{tool.avg_latency_ms}ms avg · p95: {tool.p95_latency_ms}ms</div>
      </div>
    {/each}
  </div>
</div>

<style>
  .overview { padding: 1rem; }

  .cards {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
  }

  .card {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    min-width: 160px;
  }

  .label {
    font-size: 0.7rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-top: 0.25rem;
  }

  h3 { margin: 0 0 0.25rem; font-size: 1rem; color: #333; }

  .note {
    font-size: 0.8rem;
    color: #999;
    margin: 0 0 0.75rem;
  }

  .sparklines {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
  }

  .sparkline-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .tool-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #333;
  }

  .latency {
    font-size: 0.72rem;
    color: #666;
  }
</style>
