# MCP Metrics Report

**Report Date**: 2026-03-31 20:50 UTC
**Input**: .cache/mcp-metrics/tool_calls.jsonl
**Total Records**: 14

This baseline report reflects the `dogma-governance` tool invocations captured via `_run_with_mcp_telemetry()` during the PR refresh run. The `dogma-browser-inspector` tools were also exercised for completeness, but they do not yet emit rows into `.cache/mcp-metrics/tool_calls.jsonl`.

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Calls | 14 |
| Success Rate | 100.0% |
| Mean Duration | 41.0 ms |

## Per-Tool Breakdown

| Tool | Call Count | Success % | Mean (ms) | P95 (ms) | Max (ms) |
|------|-----------|-----------|-----------|----------|----------|
| get_trace_health | 2 | 100.0% | 0.111 | N/A | 0.180 |
| validate_synthesis | 1 | 100.0% | 104.1 | N/A | 104.1 |
| query_docs | 1 | 100.0% | 146.8 | N/A | 146.8 |
| prune_scratchpad | 1 | 100.0% | 66.9 | N/A | 66.9 |
| detect_user_interrupt | 1 | 100.0% | 0.049 | N/A | 0.049 |
| normalize_path | 1 | 100.0% | 0.075 | N/A | 0.075 |
| resolve_env_path | 1 | 100.0% | 0.051 | N/A | 0.051 |
| route_inference_request | 1 | 100.0% | 3.2 | N/A | 3.2 |
| run_research_scout | 1 | 100.0% | 83.5 | N/A | 83.5 |
| scaffold_agent | 1 | 100.0% | 36.3 | N/A | 36.3 |
| scaffold_workplan | 1 | 100.0% | 44.2 | N/A | 44.2 |
| check_substrate | 1 | 100.0% | 61.9 | N/A | 61.9 |
| validate_agent_file | 1 | 100.0% | 27.4 | N/A | 27.4 |

## Error Summary

| Tool | Error Count | Error Types | Sample Messages |
|------|-------------|-------------|------------------|

## Top 5 Slowest Calls

| Tool | Duration (ms) | Timestamp | Status |
|------|--------------|-----------|--------|
| query_docs | 146.8 | 2026-03-31T20:50:25.329911+00:00 | success |
| validate_synthesis | 104.1 | 2026-03-31T20:50:25.180898+00:00 | success |
| run_research_scout | 83.5 | 2026-03-31T20:50:32.103115+00:00 | success |
| prune_scratchpad | 66.9 | 2026-03-31T20:50:25.398517+00:00 | success |
| check_substrate | 61.9 | 2026-03-31T20:50:55.151718+00:00 | success |
