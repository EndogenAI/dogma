# Workplan: Sprint 20 — RAG & Observability

**Branch**: `feat/sprint-20-rag-observability`
**Date**: 2026-03-28
**Orchestrator**: Executive Orchestrator
**Milestone**: 21
**Closes**: #498, #499, #496, #500
**Tracks**: #497 (umbrella — progress comments only)

---

## Objective

Instrument the MCP server with OpenTelemetry spans, build the metrics capture/report pipeline with a CI quality gate, and lay the groundwork for RAG integration under the EndogenAI observability harness. Issue #496 (RAG integration) is large (L) and explicitly planned to span beyond Sprint 20 if capacity is tight; Phases 1–2 establish the observability foundation that gates all downstream work. Issue #500 (DeepEval/RAGAS) is capacity-conditional and may be deferred to Sprint 21.

**Governing axiom**: Endogenous-First — survey `mcp_server/dogma_server.py`, `scripts/capture_mcp_metrics.py`, and `docs/metrics/` before any instrumentation or pipeline work.

**Prerequisites (closed)**: #495 (MCP quality metrics research) ✅ 2026-03-28 · #494 (E2E test suite) ✅ 2026-03-28 (PR #502)

---

## Phase Plan

### Phase 0 — Workplan Review ⬜
**Agent**: Review
**Deliverables**:
- `## Workplan Review Output` in scratchpad, APPROVED verdict

**Depends on**: workplan committed
**CI**: n/a (review only)
**Status**: ✅ Complete — APPROVED

---

### Phase 1 — OTel MCP Instrumentation ⬜
**Agent**: Executive Scripter
**Issues**: #498
**Deliverables**:
- `mcp_server/dogma_server.py` instrumented with OTel spans:
  - `gen_ai.operation.name=execute_tool`
  - `gen_ai.tool.name` (per-tool attribute)
  - `error.type=tool_error` on exceptions
  - `mcp.server.operation.duration` histogram
- Unit tests covering span emission for happy-path and error cases (existing `tests/test_mcp_server_telemetry.py` extended or new test file)
- `docs/guides/mcp-observability.md` — brief note documenting OTel semconv attributes used and how to verify locally

**Depends on**: Phase 0 APPROVED · #495 ✅
**CI**: `uv run pytest tests/ -m "not slow and not integration" -q`
**Status**: ⬜ Not started

---

### Phase 1 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 1 Review Output` in scratchpad, APPROVED verdict

**Depends on**: Phase 1 deliverables committed
**Gate**: Phase 2 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 2 — Metrics Capture/Report Pipeline + CI Quality Gate ⬜
**Agent**: Executive Scripter
**Issues**: #499
**Deliverables**:
- `scripts/capture_mcp_metrics.py` — captures faithfulness, error rate, and latency metrics from the E2E harness run
- `scripts/report_mcp_metrics.py` — formats metrics as Markdown report + structured JSON
- CI quality gate in `.github/workflows/tests.yml`:
  - Fail if faithfulness < 0.75
  - Fail if error rate > 5%
- Baseline report committed to `docs/metrics/mcp-quality-baseline-sprint-20.md` (or `.json`)
- Progress comment posted on #497

**Depends on**: Phase 1 Review APPROVED · #498
**CI**: `uv run python scripts/capture_mcp_metrics.py --dry-run` · CI gate step
**Status**: ⬜ Not started

---

### Phase 2 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 2 Review Output` in scratchpad, APPROVED verdict

**Depends on**: Phase 2 deliverables committed
**Gate**: Phase 3 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 3 — RAG Integration Architecture (Part 1: Survey + ADR) ⬜
**Agent**: Executive Researcher → Executive Docs
**Issues**: #496 (sub-phase: architecture analysis + ADR only)
**Deliverables**:
- Survey of EndogenAI/rag repo: data flow, retrieval mechanism, embedding model, chunking strategy — findings in scratchpad (≤ 1000 tokens)
- ADR committed to `docs/decisions/ADR-NNN-rag-mcp-integration.md` — decision: wrap RAG as MCP tool vs. sidecar vs. in-process library; records chosen approach, alternatives, and rationale
- Progress comment posted on #497

**Depends on**: Phase 2 Review APPROVED · #499 (metrics pipeline must exist to measure integration delta) · #494 ✅
**CI**: n/a
**Note**: Phase 3 covers analysis + ADR only. RAG implementation (Part 2) and validation/delta measurement (Part 3) are explicitly flagged for Sprint 21 if capacity is tight — see Capacity Note below.
**Status**: ⬜ Not started

---

### Phase 3 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 3 Review Output` in scratchpad, APPROVED verdict

**Depends on**: Phase 3 deliverables committed
**Gate**: Phase 4 (conditional) does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 4 — DeepEval / UMUX-Lite / RAGAS Loop ⬜ *(capacity-conditional)*
**Agent**: Executive Scripter
**Issues**: #500
**Deliverables**:
- DeepEval integration wired into E2E harness (faithfulness + answer relevancy metrics)
- UMUX-Lite formula implemented as utility function in `scripts/capture_mcp_metrics.py`
- Weekly 5% RAGAS sample loop (script or CI schedule step)
- Runbook in `docs/guides/mcp-eval-runbook.md` covering how to trigger and interpret each eval type

**Depends on**: Phase 3 Review APPROVED · #499 (metrics pipeline must be live)
**CI**: `uv run pytest tests/ -m "not slow" -q`
**Status**: ⬜ Not started — **DEFER TO SPRINT 21 IF CAPACITY EXCEEDED**

---

### Phase 4 Review — Review Gate ⬜ *(conditional)*
**Agent**: Review
**Deliverables**:
- `## Phase 4 Review Output` in scratchpad, APPROVED verdict

**Depends on**: Phase 4 deliverables committed (if Phase 4 runs)
**Status**: ⬜ Not started

---

### Phase 5 — Session Close ⬜
**Agent**: Executive Orchestrator
**Deliverables**:
- Session summary in scratchpad
- Issue body checkboxes updated for all completed issues (#498, #499, and whichever of #496/#500 completed)
- Progress comment posted on #497 (umbrella tracker)
- Branch pushed, PR opened targeting `main`
- All completed issues listed in PR body as `Closes #NNN`

**Depends on**: All active Review gates APPROVED
**CI**: n/a
**Status**: ⬜ Not started

---

## Capacity Note

**#496 — RAG Integration (Effort: L)**  
This is a multi-sub-phase issue. Phase 3 of this workplan covers only the architecture survey + ADR (the minimum deliverable for Sprint 20). RAG tool implementation (Part 2) and validation + delta measurement against the metrics baseline (Part 3) are **explicitly planned to carry into Sprint 21**. Do not attempt all three sub-phases in this sprint unless Phase 1 and Phase 2 complete ahead of schedule.

**#500 — DeepEval/UMUX-Lite/RAGAS (Effort: M, Optional)**  
Phase 4 is capacity-conditional. If Phase 3 (#496 ADR) exhausts sprint capacity, Phase 4 is deferred entirely to Sprint 21 without impacting any blocking dependencies.

---

## Acceptance Criteria

### #498 — OTel Instrumentation
- [ ] `mcp_server/dogma_server.py` emits `gen_ai.operation.name=execute_tool` span on every tool call
- [ ] `gen_ai.tool.name` attribute set per-tool
- [ ] `error.type=tool_error` recorded on exception paths
- [ ] `mcp.server.operation.duration` histogram recorded
- [ ] Unit tests cover happy-path span emission and error-path span emission
- [ ] `docs/guides/mcp-observability.md` note committed

### #499 — Metrics Pipeline + CI Gate
- [ ] `scripts/capture_mcp_metrics.py` captures faithfulness, error rate, latency from E2E run
- [ ] `scripts/report_mcp_metrics.py` produces Markdown + JSON output
- [ ] CI gate fails build if faithfulness < 0.75 or error rate > 5%
- [ ] Baseline report committed to `docs/metrics/`
- [ ] Progress comment posted on #497

### #496 — RAG Integration (Sprint 20 scope: ADR only)
- [ ] EndogenAI/rag repo surveyed; findings in scratchpad
- [ ] ADR committed to `docs/decisions/` — decision on integration pattern recorded with alternatives and rationale
- [ ] Progress comment posted on #497
- [ ] RAG implementation and delta validation flagged for Sprint 21

### #500 — DeepEval/UMUX-Lite/RAGAS *(if capacity)*
- [ ] DeepEval faithfulness + answer relevancy integrated into E2E harness
- [ ] UMUX-Lite formula implemented in `scripts/capture_mcp_metrics.py`
- [ ] Weekly 5% RAGAS sample loop scripted or scheduled
- [ ] Runbook committed to `docs/guides/mcp-eval-runbook.md`
