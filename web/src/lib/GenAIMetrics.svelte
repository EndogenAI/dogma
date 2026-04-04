<script lang="ts">
  /**
   * GenAI Metrics tab — RAGAS quality metrics with threshold indicators.
   * 
   * Displays faithfulness, answer_relevancy, context_precision, context_recall
   * with visual threshold feedback (Phase 9D).
   */
  import type { MetricsSnapshot } from './types';

  let { data }: { data: MetricsSnapshot } = $props();

  // RAGAS baseline thresholds (0.0–1.0 scale)
  // Values from data/governance-thresholds.yml calibration_baseline section
  const THRESHOLDS = {
    faithfulness: { warning: 0.7, critical: 0.5 },
    answer_relevancy: { warning: 0.7, critical: 0.5 },
    context_precision: { warning: 0.7, critical: 0.5 },
    context_recall: { warning: 0.7, critical: 0.5 },
  };

  let toolsArray = $derived(
    Object.entries(data?.tools ?? {})
      .map(([name, stats]) => ({
        name,
        invocation_count: stats.invocation_count,
        faithfulness: stats.faithfulness ?? null,
        answer_relevancy: stats.answer_relevancy ?? null,
        context_precision: stats.context_precision ?? null,
        context_recall: stats.context_recall ?? null,
      }))
      .filter((t) => 
        t.faithfulness !== null ||
        t.answer_relevancy !== null ||
        t.context_precision !== null ||
        t.context_recall !== null
      )
      .sort((a, b) => b.invocation_count - a.invocation_count)
  );

  function statusClass(value: number | null): string {
    if (value === null) return 'na';
    if (value >= 0.7) return 'ok';
    if (value >= 0.5) return 'warn';
    return 'critical';
  }

  function formatMetric(value: number | null): string {
    return value !== null ? value.toFixed(3) : 'N/A';
  }

  function delta(value: number | null, threshold: number): string {
    if (value === null) return '';
    const diff = value - threshold;
    const sign = diff >= 0 ? '+' : '';
    return `${sign}${diff.toFixed(3)}`;
  }
</script>

<div class="genai-metrics">
  {#if toolsArray.length === 0}
    <div class="empty-state">
      <p>No RAGAS metrics available yet.</p>
      <p class="note">RAGAS metrics appear after Gen-AI tool invocations with instrumentation.</p>
    </div>
  {:else}
    <table>
      <thead>
        <tr>
          <th>Tool Name</th>
          <th class="num">Invocations</th>
          <th class="metric">Faithfulness<span class="threshold-note">↑0.7</span></th>
          <th class="metric">Answer Relevancy<span class="threshold-note">↑0.7</span></th>
          <th class="metric">Context Precision<span class="threshold-note">↑0.7</span></th>
          <th class="metric">Context Recall<span class="threshold-note">↑0.7</span></th>
        </tr>
      </thead>
      <tbody>
        {#each toolsArray as tool (tool.name)}
          <tr>
            <td class="name-cell">{tool.name}</td>
            <td class="num">{tool.invocation_count}</td>
            <td class="metric {statusClass(tool.faithfulness)}">
              <span class="value">{formatMetric(tool.faithfulness)}</span>
              {#if tool.faithfulness !== null}
                <span class="delta {tool.faithfulness >= THRESHOLDS.faithfulness.warning ? 'positive' : 'negative'}">
                  {delta(tool.faithfulness, THRESHOLDS.faithfulness.warning)}
                </span>
              {/if}
            </td>
            <td class="metric {statusClass(tool.answer_relevancy)}">
              <span class="value">{formatMetric(tool.answer_relevancy)}</span>
              {#if tool.answer_relevancy !== null}
                <span class="delta {tool.answer_relevancy >= THRESHOLDS.answer_relevancy.warning ? 'positive' : 'negative'}">
                  {delta(tool.answer_relevancy, THRESHOLDS.answer_relevancy.warning)}
                </span>
              {/if}
            </td>
            <td class="metric {statusClass(tool.context_precision)}">
              <span class="value">{formatMetric(tool.context_precision)}</span>
              {#if tool.context_precision !== null}
                <span class="delta {tool.context_precision >= THRESHOLDS.context_precision.warning ? 'positive' : 'negative'}">
                  {delta(tool.context_precision, THRESHOLDS.context_precision.warning)}
                </span>
              {/if}
            </td>
            <td class="metric {statusClass(tool.context_recall)}">
              <span class="value">{formatMetric(tool.context_recall)}</span>
              {#if tool.context_recall !== null}
                <span class="delta {tool.context_recall >= THRESHOLDS.context_recall.warning ? 'positive' : 'negative'}">
                  {delta(tool.context_recall, THRESHOLDS.context_recall.warning)}
                </span>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>

    <div class="legend">
      <strong>Threshold Indicators:</strong>
      <span class="legend-item"><span class="box ok"></span> ≥ 0.7 (OK)</span>
      <span class="legend-item"><span class="box warn"></span> 0.5–0.69 (Warning)</span>
      <span class="legend-item"><span class="box critical"></span> &lt; 0.5 (Critical)</span>
      <span class="legend-item"><span class="box na"></span> N/A (No data)</span>
    </div>
  {/if}
</div>

<style>
  .genai-metrics { padding: 1rem; overflow-x: auto; }

  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #666;
  }

  .empty-state .note {
    font-size: 0.85rem;
    color: #999;
    margin-top: 0.5rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }

  th, td {
    padding: 0.75rem 0.5rem;
    text-align: left;
    border-bottom: 1px solid #e0e0e0;
  }

  th {
    background: #f8f9fa;
    font-weight: 600;
    font-size: 0.8rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  th.num, td.num { text-align: right; }
  th.metric, td.metric { text-align: center; }

  .threshold-note {
    display: block;
    font-size: 0.7rem;
    color: #888;
    font-weight: 400;
    margin-top: 0.2rem;
  }

  .name-cell {
    font-weight: 500;
    color: #333;
  }

  td.ok { background-color: #e8f5e9; }
  td.warn { background-color: #fff3e0; }
  td.critical { background-color: #ffebee; }
  td.na { background-color: #fafafa; color: #999; }

  .value {
    font-weight: 600;
    font-size: 1rem;
  }

  .delta {
    display: block;
    font-size: 0.7rem;
    margin-top: 0.2rem;
  }

  .delta.positive { color: #2e7d32; }
  .delta.negative { color: #c62828; }

  .legend {
    margin-top: 1rem;
    padding: 0.75rem 1rem;
    background: #f8f9fa;
    border-radius: 4px;
    font-size: 0.85rem;
  }

  .legend-item {
    display: inline-block;
    margin-right: 1.5rem;
  }

  .box {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 1px solid #ccc;
    margin-right: 0.3rem;
    vertical-align: middle;
  }

  .box.ok { background-color: #e8f5e9; }
  .box.warn { background-color: #fff3e0; }
  .box.critical { background-color: #ffebee; }
  .box.na { background-color: #fafafa; }
</style>
