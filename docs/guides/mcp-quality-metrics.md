# MCP Quality Metrics Runbook

## Purpose

This runbook explains how to capture MCP quality metrics, generate a baseline report, evaluate gate thresholds, and respond to degradation.

The implementation for this runbook is produced by:
- scripts/capture_mcp_metrics.py
- scripts/report_mcp_metrics.py
- scripts/check_mcp_quality_gate.py
- mcp_server/dogma_server.py telemetry wrappers

## Inputs and Outputs

Input observations:
- `.cache/mcp-metrics/tool_calls.jsonl`

Per-tool metric artifacts:
- `docs/metrics/mcp-quality-<tool>-<date>.json`

Consolidated report:
- `docs/metrics/mcp-quality-baseline-<date>.md`

Quality gate result:
- PASS/FAIL from `scripts/check_mcp_quality_gate.py`

## Canonical Commands

Generate per-tool metrics:

```bash
uv run python scripts/capture_mcp_metrics.py \
  --all \
  --input-jsonl .cache/mcp-metrics/tool_calls.jsonl \
  --output-dir docs/metrics \
  --date 2026-03-27 \
  --window-calls 100
```

Generate markdown report:

```bash
uv run python scripts/report_mcp_metrics.py \
  --input-glob "docs/metrics/mcp-quality-*-2026-03-27.json" \
  --output docs/metrics/mcp-quality-baseline-2026-03-27.md
```

Run the quality gate:

```bash
uv run python scripts/check_mcp_quality_gate.py \
  --input-glob "docs/metrics/mcp-quality-*-2026-03-27.json" \
  --window-calls 100
```

## Threshold Definitions

Required window contract:
- Metrics must represent exactly the last 100 calls per tool.
- Gate fails if artifact `window_calls` is not 100.
- Gate fails if `sample_size` is not exactly 100.

Primary fail conditions:
- `faithfulness < 0.75`
- `error_rate_pct > 5.0`

Target/monitoring thresholds:
- `faithfulness >= 0.80`
- `answer_relevance >= 0.75`
- `context_precision >= 0.70`
- `latency_p95 <= 2.0s`
- `mean_severity <= 1.5`
- `umux_lite_equivalent >= 68`

## Interpreting Report Output

Columns map to metric surfaces:
- Performance: samples, latency p95, error percentage
- Semantic: faithfulness, answer relevance, context precision
- Classical quality: correctness, completeness, precision
- Defect: mean severity
- Usability proxy: UMUX-lite equivalent

Interpretation posture:
- Use per-tool rows as the primary signal.
- Use cross-tool comparisons only after checking each row meets the window contract.
- Treat a gate FAIL as a phase blocker for downstream optimization comparisons.

## Degradation Response

When the gate fails:
1. Confirm window contract (sample_size and window_calls) before any diagnosis.
2. Identify failing tool rows and failing dimensions.
3. Check MCP telemetry emission path in mcp_server/dogma_server.py for missing/invalid fields.
4. Re-run capture and report after remediation.
5. Record failure mode and remediation in issue comments before unblocking phase progression.

Suggested triage by failure type:
- Faithfulness low: inspect retrieval/context inputs and response quality scoring pipeline.
- Error rate high: inspect tool handler failures and error classification (`error.type=tool_error`).
- Latency high: inspect tool execution hot paths and sampling conditions.
- Usability proxy low: inspect output format/actionability and severity distribution.

## CI Integration Design (Sprint 2 Wiring)

Stage mapping:
- PR pre-merge quality gate stage:
  - Run `scripts/check_mcp_quality_gate.py` against latest artifacts.
  - Block merge on FAIL.

Recommended CI sequence:
1. Build/test scripts and telemetry wrappers
2. Capture/locate latest metrics artifacts
3. Run quality gate script
4. Publish markdown report artifact for reviewer inspection

Notes:
- This sprint intentionally ships the scripts and thresholds first.
- Full workflow wiring under `.github/workflows/` is deferred to Sprint 2.

## Known Limitations

- The current baseline for 2026-03-27 is synthetic-seeded for pipeline verification.
- Replace synthetic observation generation with live MCP trace capture in the next baseline run.
