---
Status: Accepted
Date: 2026-03-27
Deciders: EndogenAI core team
---

# ADR-008: MCP Quality Metrics Framework

## Title
MCP Quality Metrics Framework

## Status
Accepted

## Context
Issue #495 requires a Phase 3 design contract that is directly implementable by the #498 and #499 workstreams. The survey findings in docs/research/mcp-quality-metrics-survey.md establish a multi-surface framework that combines OTel MCP semantic conventions for telemetry with semantic and quality scoring for MCP tool calls. The design decision here is to encode those findings into a stable contract artifact and implementation sequence for this sprint.

## Decision Drivers

- #495 requires measurable, enforceable thresholds before implementation can proceed.
- #498 and #499 need a shared field contract to avoid implementation drift.
- Local-Compute-First constraints require avoiding cloud-only evaluation dependencies for baseline gating.
- Sprint scope must stay bounded while preserving a clear path for deferred evaluation enhancements (#500).

## Decision
1. Adopt OTel MCP semantic conventions for tool-call telemetry in the MCP server implementation (#498).
2. Implement capture/report workflow plus CI quality gate as the operational contract for MCP quality management (#499).
3. Defer DeepEval plus weekly RAGAS workflow from #500 out of the current sprint; this remains planned follow-on work and is not in the present implementation scope.

### Dimension Definitions and Quantitative Proxies
1. Correctness (0.0-1.0): proportion of assertions where tool output matches expected result for the test case.
2. Completeness (0.0-1.0): proportion of expected fields/behaviors present in tool output (false-negative complement).
3. Precision (0.0-1.0): proportion of asserted findings that are valid (false-positive complement).
4. Performance: P95 latency from OTel `mcp.server.operation.duration` normalized to ms, plus tool error rate percentage.
5. Semantic quality: RAGAS faithfulness, answer relevance, context precision (all 0.0-1.0).
6. Defect severity: Nielsen-adapted 0-4 ordinal rubric with `severity_level_mean` and 0..4 distribution counts.
7. Usability proxy: UMUX-Lite equivalent target score, used as agent-facing perceived quality signal.

### Threshold Contract
1. Fail gate if faithfulness < 0.75 over evaluation window of 100 calls.
2. Fail gate if tool error rate > 5.0% over evaluation window of 100 calls.
3. Target thresholds: faithfulness >= 0.80, answer relevance >= 0.75, context precision >= 0.70.
4. Performance target: latency P95 <= 2.0s baseline.
5. Quality targets: DeepEval task completion >= 0.75, mean severity <= 1.5, UMUX-Lite equivalent >= 68.

### Canonical Tool Set Coverage
The schema and implementation are scoped to the 8 canonical governance tools provided by `mcp_server/dogma_server.py` (excluding auxiliary utility tools such as path resolution and routing helpers):
- check_substrate
- validate_agent_file
- validate_synthesis
- scaffold_agent
- scaffold_workplan
- run_research_scout
- query_docs
- prune_scratchpad

### Field-Level Contract (Plan Traceability)
The schema contract required by the sprint plan is implemented as per-tool JSON artifacts emitted by `scripts/capture_mcp_metrics.py`. Each artifact includes:
- `tool_name`
- `timestamp_utc`
- a nested `metrics` object that contains per-dimension summaries (for example: `metrics.correctness`, `metrics.completeness`, `metrics.precision`, `metrics.performance`, `metrics.semantic_quality`, `metrics.defect_severity`, `metrics.usability_proxy`), with fields defined in `data/mcp-metrics-schema.yml`.

The earlier planning-only flat contract that listed `metric_dimension`, `value`, `test_case_id`, and `methodology_notes` as required top-level keys is superseded by this implemented schema. For exact field names and structure, `data/mcp-metrics-schema.yml` and `scripts/capture_mcp_metrics.py` are the authoritative references.

## Consequences
1. Step 1: instrument mcp_server/dogma_server.py.
2. Step 2: implement scripts/capture_mcp_metrics.py and scripts/report_mcp_metrics.py.
3. Step 3: implement quality gate script.
4. Step 4: baseline capture phase.
5. The data schema in data/mcp-metrics-schema.yml becomes the contract between telemetry emission, capture/report scripts, and CI quality gates.
6. Sprint scope remains bounded while preserving forward compatibility for #500.

## Alternatives considered
1. Implement #498, #499, and #500 in one sprint. Rejected because it increases implementation and validation risk, and blurs phase boundaries.
2. Use ad hoc metrics without OTel semconv alignment. Rejected because it weakens interoperability, traceability, and long-term maintainability.
3. Delay all design contracts until implementation starts. Rejected because #498 and #499 require explicit interfaces and thresholds before coding begins.
