# MCP Metrics Baseline — 2026-03-30

**Report Date**: 2026-03-30
**Input**: .cache/mcp-metrics/tool_calls.jsonl
**Total Records**: 2

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Calls | 2 |
| Success Rate | 0.0% |
| Mean Duration | 0.0 ms |

## Per-Tool Breakdown

| Tool | Call Count | Success % | Mean (ms) | P95 (ms) | Max (ms) |
|------|-----------|-----------|-----------|----------|----------|
| query_docs | 2 | 0.0% | 0.0 | N/A | 0.0 |

## Top 5 Slowest Calls

| Tool | Duration (ms) | Timestamp | Status |
|------|--------------|-----------|--------|
| query_docs | 0.0 | 2026-03-31T02:17:34.405079+00:00 | error |
| query_docs | 0.0 | 2026-03-31T02:17:34.404647+00:00 | error |

---

## Notes

This baseline report was generated from a minimal dataset (2 error records only). Both records show `latency_ms: 0.003` and `0.004` in the JSONL; the report rendered them as `0.0 ms` due to 1-decimal-place rounding in the reporter's output formatting (not a parsing issue). Sub-ms latencies are now rendered with 3 decimal places after the precision fix in `report_mcp_metrics_v2.py`.

**To generate updated reports**:
```bash
# Generate from current data
uv run python scripts/report_mcp_metrics_v2.py --output docs/metrics/mcp-report-$(date +%Y-%m-%d).md

# Or to stdout
uv run python scripts/report_mcp_metrics_v2.py
```

**Expected usage pattern**:
1. MCP server runs and populates `.cache/mcp-metrics/tool_calls.jsonl` with tool-call observations
2. Run `report_mcp_metrics_v2.py` periodically to generate snapshots
3. Compare reports over time to track performance trends
