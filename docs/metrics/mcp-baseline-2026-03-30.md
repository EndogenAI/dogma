# MCP Metrics Report

**Report Date**: 2026-03-31 07:55 UTC
**Input**: .cache/mcp-metrics/tool_calls.jsonl
**Total Records**: 2

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Calls | 2 |
| Success Rate | 0.0% |
| Mean Duration | 0.006 ms |

## Per-Tool Breakdown

| Tool | Call Count | Success % | Mean (ms) | P95 (ms) | Max (ms) |
|------|-----------|-----------|-----------|----------|----------|
| query_docs | 2 | 0.0% | 0.006 | N/A | 0.008 |

## Error Summary

| Tool | Error Count | Error Types | Sample Messages |
|------|-------------|-------------|------------------|
| query_docs | 2 | RuntimeError (1), tool_error (1) | No error_message captured |

## Top 5 Slowest Calls

| Tool | Duration (ms) | Timestamp | Status |
|------|--------------|-----------|--------|
| query_docs | 0.008 | 2026-03-31T07:41:48.071077+00:00 | error |
| query_docs | 0.004 | 2026-03-31T07:41:48.071502+00:00 | error |
