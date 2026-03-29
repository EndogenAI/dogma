<script lang="ts">
  /**
   * Line.svelte — Sparkline chart component.
   *
   * Renders a compact SVG polyline (sparkline) for a series of numeric data
   * points.  Intended for inline use inside metric cards, not as a standalone
   * chart.  The viewport is fixed at 140×40 px — parent containers should
   * add any desired spacing or responsive sizing externally.
   *
   * Props:
   *   data  The data series to plot.  Only the `y` value is used for
   *         positioning; `x` is accepted for schema compatibility but the
   *         points are evenly distributed along the horizontal axis regardless
   *         of `x` values.  Defaults to [] (renders a flat midline when empty
   *         or single point).
   *
   * Rendering details:
   *   - Y-axis is auto-scaled to the [minY, maxY] range of the supplied data.
   *   - A 3 px top/bottom gutter prevents the polyline from touching the SVG
   *     boundary (avoids clipping at extreme values).
   *   - When all values are equal (range = 0) a flat midline is drawn to
   *     avoid division-by-zero.
   *   - Stroke: #4f8ef7 (matches the dashboard's primary accent colour).
   */
  import type { DataPoint } from '../lib/types';

  let { data = [] }: { data?: DataPoint[] } = $props();

  /** SVG viewport width in pixels. */
  const W = 140;
  /** SVG viewport height in pixels. */
  const H = 40;

  /**
   * Compute the `points` attribute string for the SVG `<polyline>`.
   *
   * Maps each datum to (x, y) coordinates where:
   *   - x is linearly distributed across [0, W] based on index
   *   - y is scaled to [gutter, H - gutter] based on the data range
   *
   * Falls back to a flat midline when data has 0 or 1 points.
   */
  let points = $derived.by(() => {
    if (data.length <= 1) {
      return `0,${H / 2} ${W},${H / 2}`;
    }
    const ys = data.map((d) => d.y);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const range = maxY - minY || 1; // guard against flat series (all equal values)
    return data
      .map((d, i) => {
        const x = (i / (data.length - 1)) * W;
        // Invert y: SVG y=0 is top; subtract from H so higher values appear higher
        const y = H - ((d.y - minY) / range) * (H - 6) - 3;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(' ');
  });
</script>

<svg width={W} height={H} style="display:block;overflow:visible">
  <polyline
    {points}
    fill="none"
    stroke="#4f8ef7"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  />
</svg>
