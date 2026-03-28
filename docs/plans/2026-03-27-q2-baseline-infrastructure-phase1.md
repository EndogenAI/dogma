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

Research informs metric definitions (which define the data schema, which constrains the scripts). Resolution: Research first (Phase 1), then design (Phase 2), then implementation (Phase 3), then baseline capture (Phase 4). Documentation consolidates completed work (natural retrospective exception — Phase 5 trails implementation).

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

| Dimension | Measurement Approach (TBD in Phase 1/2) |
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
**Status**: ⬜ Not started

---

### Phase 1 — Research: Survey Metrics Patterns

**Agent**: Executive Researcher  
**Deliverables**: `docs/research/mcp-quality-metrics-survey.md` (Status: Final)  
**Depends on**: Phase 0 APPROVED  
**Gate**: Phase 1 Review does not start until deliverable committed  
**Status**: ⬜ Not started

**Research questions:**
1. What quality metric frameworks exist for MCP/agentic tools? (RAGAS, LangSmith, Evals frameworks)
2. How does EndogenAI/rag#33 define its query benchmark suite — what's applicable to MCP tools?
3. What is the existing dogma test suite coverage for MCP tools? (scan `tests/` for MCP-relevant tests)
4. What quantitative proxy best captures "Usability" for non-LLM tools (e.g., `validate_agent_file`)?
5. Survey existing `docs/metrics/` for any prior MCP measurement artifacts

**Scope constraint**: Do NOT design the schema or write scripts. Return findings only.  
**Output ceiling**: ≤ 2,000 tokens compressed findings.

**Acceptance criteria:**
- [ ] At least 2 external frameworks surveyed (with cache check via `fetch_source.py --check` first)
- [ ] rag#33 query suite reviewed; applicable queries identified
- [ ] Existing dogma test suite gaps for MCP tools documented
- [ ] Quantitative proxy for "Usability" proposed with rationale
- [ ] docs/research/mcp-quality-metrics-survey.md committed with Status: Final

### Phase 1 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 1 Review Output` in scratchpad, verdict APPROVED  
**Depends on**: Phase 1 deliverable committed  
**Gate**: Phase 2 does not begin until APPROVED  
**Status**: ⬜ Not started

---

### Phase 2 — Design: Metric Definitions + Data Schema

**Agent**: Executive Scripter (design spec only — no implementation)  
**Deliverables**:
- `data/mcp-metrics-schema.yml` — YAML schema for metric storage
- `docs/decisions/ADR-NNN-mcp-quality-metrics-framework.md` — architecture decision record  
**Depends on**: Phase 1 Review APPROVED  
**Gate**: Phase 2 Review does not start until deliverables committed  
**Status**: ⬜ Not started

**Design constraints:**
- Schema must support: tool name, metric dimension, value, test case ID, timestamp, methodology notes
- Each Correctness/Completeness/Precision score stored as float 0.0–1.0
- Usability stored as enum (actionable/partial/unclear) OR float proxy
- Performance stored as latency_ms + error_rate_pct
- Schema versioned (v1 initial) to support future format changes without data loss

**Acceptance criteria:**
- [ ] `data/mcp-metrics-schema.yml` with JSON Schema or YAML structure, all 5 dimensions represented
- [ ] ADR documents: dimension definitions, quantitative proxies, rationale for schema choices
- [ ] ADR references Phase 1 survey findings (endogenous source)
- [ ] Schema supports all 8 MCP tools

### Phase 2 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 2 Review Output` in scratchpad, verdict APPROVED  
**Depends on**: Phase 2 deliverables committed  
**Gate**: Phase 3 does not begin until APPROVED  
**Status**: ⬜ Not started

---

### Phase 3 — Implementation: Measurement Scripts + Infrastructure

**Agent**: Executive Scripter  
**Deliverables**:
- `scripts/capture_mcp_metrics.py` — runs measurement suite against specified MCP tool(s)
- `scripts/report_mcp_metrics.py` — generates human-readable report from stored measurements
- `tests/test_capture_mcp_metrics.py` — unit tests (≥80% coverage, per Testing-First Requirement)
- `docs/metrics/` directory created (or confirmed existing)  
**Depends on**: Phase 2 Review APPROVED  
**Gate**: Phase 3 Review does not start until deliverables committed  
**Status**: ⬜ Not started

**Implementation constraints:**
- `capture_mcp_metrics.py` supports `--tool <name>` (single) and `--all` (all 8 tools)
- `capture_mcp_metrics.py` outputs to `docs/metrics/mcp-quality-<tool>-<date>.json`
- `capture_mcp_metrics.py --dry-run` previews without writing (Tier 0/1/3 validation ladder)
- `report_mcp_metrics.py` reads from `docs/metrics/` and outputs Markdown table
- All scripts open with docstring (purpose, inputs, outputs, usage example per AGENTS.md)
- No hardcoded test cases yet — stub structure with placeholder assertions sufficient for Phase 3
- Full test cases added in Phase 4 when baseline data is available

**Acceptance criteria:**
- [ ] `capture_mcp_metrics.py` with `--dry-run`, `--tool`, `--all` flags
- [ ] `report_mcp_metrics.py` generating Markdown summary table
- [ ] Tests passing: `uv run pytest tests/test_capture_mcp_metrics.py -v`
- [ ] Ruff clean: `uv run ruff check scripts/capture_mcp_metrics.py scripts/report_mcp_metrics.py`

### Phase 3 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 3 Review Output` in scratchpad, verdict APPROVED  
**Depends on**: Phase 3 deliverables committed  
**Gate**: Phase 4 does not begin until APPROVED  
**Status**: ⬜ Not started

---

### Phase 4 — Baseline Capture: Run Metrics Against All 8 Tools

**Agent**: Executive Scripter (execution) + Executive Researcher (analysis)  
**Deliverables**:
- `docs/metrics/mcp-quality-baseline-2026-03-27.json` — baseline measurement data
- `docs/metrics/mcp-quality-baseline-2026-03-27.md` — human-readable report (via report script)  
**Depends on**: Phase 3 Review APPROVED  
**Gate**: Phase 4 Review does not start until deliverables committed  
**Status**: ⬜ Not started

**Execution constraints:**
- Run `scripts/capture_mcp_metrics.py --all` against live MCP server
- Document any measurement gaps (tools that cannot be measured automatically yet)
- Record methodology notes in each measurement record (e.g., "Usability scored by rubric — HUMAN_EVAL")
- Initial baseline may have partial coverage; document gaps explicitly rather than leaving blank

**Acceptance criteria:**
- [ ] Baseline JSON committed to `docs/metrics/`
- [ ] All 8 tools have at least Performance metrics captured (latency + error rate)
- [ ] Correctness, Completeness, Precision have test cases for at least 4 of 8 tools
- [ ] Usability has a rubric applied to at least 4 of 8 tools
- [ ] Gaps explicitly documented (not silent)
- [ ] Markdown report generated and committed

### Phase 4 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 4 Review Output` in scratchpad, verdict APPROVED  
**Depends on**: Phase 4 deliverables committed  
**Gate**: Phase 5 does not begin until APPROVED  
**Status**: ⬜ Not started

---

### Phase 5 — Documentation: Runbook + CI Integration Design

**Agent**: Executive Docs  
**Deliverables**:
- `docs/guides/mcp-quality-metrics.md` — runbook for interpreting quality dashboard and identifying degradation
- `docs/guides/mcp-quality-metrics.md` to include: how to run, how to read output, degradation thresholds, how to add new tools  
**Note**: Full CI integration (`.github/workflows/` changes) deferred to Sprint 2; this phase documents the CI design and produces a runbook so the circuit-breaker pattern (run on PR) can be implemented next sprint.  
**Depends on**: Phase 4 Review APPROVED  
**Gate**: Phase 5 Review does not start until deliverables committed  
**Status**: ⬜ Not started

**Acceptance criteria:**
- [ ] `docs/guides/mcp-quality-metrics.md` committed
- [ ] Runbook covers: run command, output interpretation, threshold definitions, degradation response
- [ ] CI design documented (even if not yet wired): which checks gate which PR stage

### Phase 5 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 5 Review Output` in scratchpad, verdict APPROVED  
**Depends on**: Phase 5 deliverables committed  
**Gate**: Phase 6 does not begin until APPROVED  
**Status**: ⬜ Not started

---

### Phase 6 — Commit & Push

**Agent**: GitHub  
**Deliverables**:
- All changes pushed to `feat/q2-baseline-infrastructure`
- PR opened: "feat(metrics): MCP quality metrics framework — #495 baseline"
- `Closes #495` in PR body  
**Depends on**: Phase 5 Review APPROVED  
**Gate**: Session closes when PR URL returned  
**Status**: ⬜ Not started

---

## Deferred to Sprint 2

- #494 E2E integration test suite (shares infrastructure with #495 but scoped separately to keep optimizations independently measurable)
- Full CI wiring (`.github/workflows/mcp-quality-check.yml`)
- #493 format optimization baseline (depends on #495 adherence metrics)
- #496 RAG integration (depends on #495 + #494)

## Open Questions (from issues)

1. **Usability quantitative proxy**: rubric enum vs float proxy — resolved by Phase 1 research
2. **Per-tool vs aggregate**: both; per-tool primary, aggregate summary in report
3. **Baseline thresholds**: TBD from Phase 4 data; set after first baseline run, not before
4. **Token usage for non-LLM tools**: record execution time + subprocess timing; mark as N/A for token metrics where inapplicable
5. **CI latency ceiling**: TBD from Phase 3/4 execution data

## Issue Updates Required at Completion

- #495: mark all checkboxes complete; post progress comment with PR link
- #497: update with Sprint 1 completion status; next sprint (#494) planned

## Estimated Effort

| Phase | Effort | Agent |
|-------|--------|-------|
| Phase 1 Research | M | Executive Researcher |
| Phase 2 Design | S | Executive Scripter |
| Phase 3 Implementation | M | Executive Scripter |
| Phase 4 Baseline Capture | S | Executive Scripter |
| Phase 5 Documentation | S | Executive Docs |
| Phase 6 Commit | XS | GitHub |

Total: ~2–3 sessions depending on research phase depth.
