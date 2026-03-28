---
title: "Q2 Baseline Infrastructure — Phase 1: MCP Quality Metrics Framework"
date: 2026-03-27
branch: feat/q2-baseline-infrastructure
closes_issue: 495
sprint: Q2 Sprint 1
status: draft
---

# Q2 Baseline Infrastructure — Phase 1: MCP Quality Metrics Framework

## Objective

Deliver the MCP Quality Metrics Framework (#495) — the measurement gate required by all subsequent Q2 optimization experiments. By sprint end, every one of the 8 dogmaMCP tools will have a documented baseline score across 5 metric dimensions (Correctness, Completeness, Precision, Usability, Performance), with reproducible scripts, a data schema, and CI integration.

**Governing axiom**: Algorithms-Before-Tokens  
**Why this first**: #495 is a hard gate on #493 (format optimization) and #496 (RAG integration). Both require an adherence/quality measurement capability before their delta measurements are possible. Science-grade primary research (#497) requires independent, pre-measured baselines.

## Chicken-and-Egg Resolution

Research informs metric definitions (which define the data schema, which constrains the scripts). Resolution: preflight and model-switch checkpoint first (Phase 1), cross-cutting research scouting and synthesis next (Phase 2), then design (Phase 3), then implementation (Phase 4), then baseline capture (Phase 5). Documentation consolidates completed work (natural retrospective exception — Phase 6 trails implementation).

## MCP Tools in Scope (8 canonical)

1. `check_substrate`
2. `validate_agent_file`
3. `validate_synthesis`
4. `scaffold_agent`
5. `scaffold_workplan`
6. `run_research_scout`
7. `query_docs`
8. `prune_scratchpad`

## Metric Dimensions (5 per #495 spec)

| Dimension | Measurement Approach (TBD in Phase 2/3) |
|-----------|----------------------------------------|
| **Correctness** | Boolean pass/fail per test case — does tool do what it claims? |
| **Completeness** | False negative rate — does it catch all cases it should? |
| **Precision** | False positive rate — does it avoid false positives? |
| **Usability** | Qualitative rubric or quantitative proxy — is output actionable? |
| **Performance** | Latency (ms), error rate, token usage (where applicable) |

## Phase Structure

### Phase 0 — Workplan Review

**Agent**: Review  
**Deliverables**: APPROVED verdict logged under `## Workplan Review Output` in scratchpad  
**Depends on**: This workplan committed  
**Gate**: Phase 1 does not begin until APPROVED  
**Status**: ✅ Complete — APPROVED

---

### Phase 1 — Preflight + STOP Checkpoint (Pre-Research Model Switch)

**Agent**: Executive Orchestrator  
**Deliverables**: Explicit pause marker in scratchpad before research delegation  
**Depends on**: Phase 0 APPROVED  
**Gate**: Phase 2A does not begin until pause is acknowledged  
**Status**: ✅ Complete — STOP issued (awaiting model-switch acknowledgement)

**Purpose:**
- Satisfy phase-ordering constraints by reserving Phase 1 for preflight/setup
- Pause immediately before research to allow model switching per user request
- Record exact next action so context is stable across model handoff

### Phase 2A — Research Scout: Qualitative Quantification + MCP QA/QC Survey

**Agent**: Executive Researcher  
**Deliverables**: Scout findings package in scratchpad + cached sources list  
**Depends on**: Phase 1 complete  
**Gate**: Phase 2B does not start until scout findings are logged  
**Status**: ✅ Complete

**Research questions:**
1. Which human-centered design (HCD), universal design (UD), and human-computer interaction (HCI) methods are valid for quantifying qualitative usability evidence?
2. What MCP-centered quality control/assurance patterns exist for tool reliability, determinism, and regression detection?
3. What quality metric frameworks exist for MCP/agentic tools? (RAGAS, LangSmith, Evals frameworks)
4. How does EndogenAI/rag#33 define its query benchmark suite and what is portable to dogma MCP quality testing?
5. What is the existing dogma test suite and docs/metrics coverage for MCP tools?

**Scope constraint**: Do NOT design schemas or write scripts in this phase. Return findings only.  
**Output ceiling**: ≤ 2,000 tokens compressed scout findings.

**Acceptance criteria:**
- [x] At least 3 external sources surveyed across HCD/UD/HCI qualitative quantification
- [x] At least 2 MCP QA/QC references surveyed for tool-level quality assurance patterns
- [x] rag#33 query suite reviewed; applicable queries identified
- [x] Existing dogma test suite and docs/metrics gaps documented
- [x] Candidate quantitative proxies for qualitative usability proposed with rationale

### Phase 2B — Formal Synthesis + Recommendations

**Agent**: Executive Researcher  
**Deliverables**: `docs/research/mcp-quality-metrics-survey.md` (Status: Final) with explicit recommendations section  
**Depends on**: Phase 2A complete  
**Gate**: Phase 2C does not start until synthesis doc committed  
**Status**: ✅ Complete — `fe36389`

**Acceptance criteria:**
- [x] D4 synthesis includes: Executive Summary, Hypothesis Validation, Pattern Catalog, Recommendations, Sources
- [x] Recommendations include measurable candidate metrics for usability/qualitative dimensions
- [x] Recommendations map directly to #495 implementation decisions

### Phase 2C — STOP Checkpoint (Post-Research Model Switch)

**Agent**: Executive Orchestrator  
**Deliverables**: Explicit pause marker in scratchpad after research completes  
**Depends on**: Phase 2B complete  
**Gate**: Phase 2D does not start until pause is acknowledged  
**Status**: ✅ Complete

**Purpose:**
- Pause immediately after research phase completion to allow model switching per user request
- Record stabilized handoff state before entering design/implementation phases

### Phase 2D — Issue Follow-Through: Comments + New Issues

**Agent**: Executive PM  
**Deliverables**:
- New progress comments on #493, #494, #495, #496, #497 with research implications
- New issues created for out-of-scope but required follow-ups discovered in synthesis (#498, #499, #500)
- Sprint incorporation decision recorded: include #498 and #499 in this sprint; defer #500 to follow-up sprint  
**Depends on**: Phase 2C complete  
**Gate**: Phase 2 Review does not start until comments/issues are posted and verified  
**Status**: ✅ Complete

**Acceptance criteria:**
- [x] Progress comment posted to each issue #493–#497 summarizing synthesis impact
- [x] Any unresolved recommendations converted into actionable GitHub issues with labels
- [x] New issues linked back to #497 umbrella (or relevant child issue)

### Phase 2 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 2 Review Output` in scratchpad, verdict APPROVED  
**Depends on**: Phase 1 and Phase 2A-2D deliverables committed  
**Gate**: Phase 3 does not begin until APPROVED  
**Status**: ✅ Complete — APPROVED

---

### Phase 3 — Design: Metric Definitions + Data Schema

**Agent**: Executive Scripter (design spec only — no implementation)  
**Deliverables**:
- `data/mcp-metrics-schema.yml` — YAML schema for metric storage
- `docs/decisions/ADR-008-mcp-quality-metrics-framework.md` — architecture decision record
- Design mapping for #498: OTel MCP semconv fields in `mcp_server/dogma_server.py` (span attrs + duration histogram)  
**Depends on**: Phase 2 Review APPROVED  
**Gate**: Phase 3 Review does not start until deliverables committed  
**Status**: ✅ Complete

**Design constraints:**
- Schema must support: tool name, metric dimension, value, test case ID, timestamp, methodology notes
- Schema/ADR must include OTel MCP semconv mapping (`gen_ai.tool.name`, `gen_ai.operation.name=execute_tool`, `error.type=tool_error`, `mcp.server.operation.duration`)
- Each Correctness/Completeness/Precision score stored as float 0.0–1.0
- Usability stored as enum (actionable/partial/unclear) OR float proxy
- Performance stored as latency_ms + error_rate_pct
- Schema versioned (v1 initial) to support future format changes without data loss

**Acceptance criteria:**
- [x] `data/mcp-metrics-schema.yml` with JSON Schema or YAML structure, all 5 dimensions represented
- [x] ADR documents: dimension definitions, quantitative proxies, rationale for schema choices
- [x] ADR references Phase 2 survey findings (endogenous source)
- [x] Schema supports all 8 MCP tools

### Phase 3 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 3 Review Output` in scratchpad, verdict APPROVED  
**Depends on**: Phase 3 deliverables committed  
**Gate**: Phase 4 does not begin until APPROVED  
**Status**: ✅ Complete — APPROVED

---

### Phase 4 — Implementation: Measurement Scripts + Infrastructure

**Agent**: Executive Scripter  
**Deliverables**:
- `scripts/capture_mcp_metrics.py` — runs measurement suite against specified MCP tool(s)
- `scripts/report_mcp_metrics.py` — generates human-readable report from stored measurements
- `scripts/check_mcp_quality_gate.py` (or extension to `scripts/check_phase_gate.py`) — enforces fail rule: faithfulness <0.75 OR tool_error >5% over last 100 calls
- `tests/test_capture_mcp_metrics.py` — unit tests (≥80% coverage, per Testing-First Requirement)
- `docs/metrics/` directory created (or confirmed existing)
- `mcp_server/dogma_server.py` instrumented with OTel MCP semconv per #498  
**Depends on**: Phase 3 Review APPROVED  
**Gate**: Phase 4 Review does not start until deliverables committed  
**Status**: ✅ Complete

**Implementation constraints:**
- `capture_mcp_metrics.py` supports `--tool <name>` (single) and `--all` (all 8 tools)
- `capture_mcp_metrics.py` outputs to `docs/metrics/mcp-quality-<tool>-<date>.json`
- `capture_mcp_metrics.py --dry-run` previews without writing (Tier 0/1/3 validation ladder)
- `report_mcp_metrics.py` reads from `docs/metrics/` and outputs Markdown table
- All scripts open with docstring (purpose, inputs, outputs, usage example per AGENTS.md)
- No hardcoded test cases yet — stub structure with placeholder assertions sufficient for Phase 3
- Full test cases added in Phase 4 when baseline data is available

**Acceptance criteria:**
- [x] `capture_mcp_metrics.py` with `--dry-run`, `--tool`, `--all` flags
- [x] `report_mcp_metrics.py` generating Markdown summary table
- [x] Quality gate script enforces fail condition (faithfulness <0.75 OR tool_error >5% over last 100 calls)
- [x] `mcp_server/dogma_server.py` emits OTel MCP semconv fields for all current tools
- [x] Tests passing: `uv run pytest tests/test_capture_mcp_metrics.py -v`
- [x] Ruff clean: `uv run ruff check scripts/capture_mcp_metrics.py scripts/report_mcp_metrics.py`

**Deferred from this sprint:**
- #500 (DeepEval + UMUX-Lite + weekly RAGAS workflow) is tracked as follow-up and not required to close this sprint's #495 baseline deliverables

### Phase 4 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 4 Review Output` in scratchpad, verdict APPROVED  
**Depends on**: Phase 4 deliverables committed  
**Gate**: Phase 5 does not begin until APPROVED  
**Status**: ✅ Complete — APPROVED

---

### Phase 5 — Baseline Capture: Run Metrics Against All 8 Tools

**Agent**: Executive Scripter (execution) + Executive Researcher (analysis)  
**Deliverables**:
- `docs/metrics/mcp-quality-baseline-2026-03-27.json` — baseline measurement data
- `docs/metrics/mcp-quality-baseline-2026-03-27.md` — human-readable report (via report script)  
**Depends on**: Phase 4 Review APPROVED  
**Gate**: Phase 5 Review does not start until deliverables committed  
**Status**: ✅ Complete

**Execution constraints:**
- Run `scripts/capture_mcp_metrics.py --all` against live MCP server
- Document any measurement gaps (tools that cannot be measured automatically yet)
- Record methodology notes in each measurement record (e.g., "Usability scored by rubric — HUMAN_EVAL")
- Initial baseline may have partial coverage; document gaps explicitly rather than leaving blank

**Acceptance criteria:**
- [x] Baseline JSON committed to `docs/metrics/`
- [x] All 8 tools have at least Performance metrics captured (latency + error rate)
- [x] Correctness, Completeness, Precision have test cases for at least 4 of 8 tools
- [x] Usability has a rubric applied to at least 4 of 8 tools
- [x] Gaps explicitly documented (not silent)
- [x] Markdown report generated and committed

### Phase 5 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 5 Review Output` in scratchpad, verdict APPROVED  
**Depends on**: Phase 5 deliverables committed  
**Gate**: Phase 6 does not begin until APPROVED  
**Status**: ✅ Complete — APPROVED

---

### Phase 6 — Documentation: Runbook + CI Integration Design

**Agent**: Executive Docs  
**Deliverables**:
- `docs/guides/mcp-quality-metrics.md` — runbook for interpreting quality dashboard and identifying degradation
- `docs/guides/mcp-quality-metrics.md` to include: how to run, how to read output, degradation thresholds, how to add new tools  
**Note**: Full CI integration (`.github/workflows/` changes) deferred to Sprint 2; this phase documents the CI design and produces a runbook so the circuit-breaker pattern (run on PR) can be implemented next sprint.  
**Depends on**: Phase 5 Review APPROVED  
**Gate**: Phase 6 Review does not start until deliverables committed  
**Status**: ⏳ In progress

**Acceptance criteria:**
- [ ] `docs/guides/mcp-quality-metrics.md` committed
- [ ] Runbook covers: run command, output interpretation, threshold definitions, degradation response
- [ ] CI design documented (even if not yet wired): which checks gate which PR stage

### Phase 6 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 6 Review Output` in scratchpad, verdict APPROVED  
**Depends on**: Phase 6 deliverables committed  
**Gate**: Phase 7 does not begin until APPROVED  
**Status**: ⬜ Not started

---

### Phase 7 — Commit & Push

**Agent**: GitHub  
**Deliverables**:
- All changes pushed to `feat/q2-baseline-infrastructure`
- PR opened: "feat(metrics): MCP quality metrics framework — #495 baseline"
- `Closes #495` in PR body  
**Depends on**: Phase 6 Review APPROVED  
**Gate**: Session closes when PR URL returned  
**Status**: ⬜ Not started

---

## Deferred to Sprint 2

- #494 E2E integration test suite (shares infrastructure with #495 but scoped separately to keep optimizations independently measurable)
- Full CI wiring (`.github/workflows/mcp-quality-check.yml`)
- #493 format optimization baseline (depends on #495 adherence metrics)
- #496 RAG integration (depends on #495 + #494)

## Open Questions (from issues)

1. **Usability quantitative proxy**: rubric enum vs float proxy — resolved by Phase 2 research
2. **Per-tool vs aggregate**: both; per-tool primary, aggregate summary in report
3. **Baseline thresholds**: TBD from Phase 4 data; set after first baseline run, not before
4. **Token usage for non-LLM tools**: record execution time + subprocess timing; mark as N/A for token metrics where inapplicable
5. **CI latency ceiling**: TBD from Phase 3/4 execution data

## Issue Updates Required During Sprint

- Phase 2D: comment on #493, #494, #495, #496, #497 with synthesis implications
- Phase 2D: create new scoped follow-up issues as needed from recommendations
- Sprint completion: #495 checkboxes + #497 sprint status update with linked artifacts

## Estimated Effort

| Phase | Effort | Agent |
|-------|--------|-------|
| Phase 1 Preflight + pre-research STOP checkpoint | XS | Executive Orchestrator |
| Phase 2A Research scouting | M | Executive Researcher |
| Phase 2B Formal synthesis + recommendations | S | Executive Researcher |
| Phase 2C Post-research STOP checkpoint | XS | Executive Orchestrator |
| Phase 2D Issue follow-through | S | Executive PM |
| Phase 3 Design | S | Executive Scripter |
| Phase 4 Implementation | M | Executive Scripter |
| Phase 5 Baseline Capture | S | Executive Scripter |
| Phase 6 Documentation | S | Executive Docs |
| Phase 7 Commit | XS | GitHub |

Total: ~3 sessions depending on research depth and issue follow-through volume.
