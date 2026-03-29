<script>
  /**
   * Minimal SVG line chart.
   * Props: data = Array<{x: number, y: number}>
   * Renders a <polyline> scaled to the data range.
   */
  let { data = [] } = $props();

  const W = 140;
  const H = 40;

  let points = $derived.by(() => {
    if (data.length <= 1) {
      return `0,${H / 2} ${W},${H / 2}`;
    }
    const ys = data.map((d) => d.y);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const range = maxY - minY || 1;
    return data
      .map((d, i) => {
        const x = (i / (data.length - 1)) * W;
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
