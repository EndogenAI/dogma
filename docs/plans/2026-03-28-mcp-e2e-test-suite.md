# Workplan: MCP E2E Test Suite

**Branch**: `feat/mcp-e2e-test-suite`
**Date**: 2026-03-28
**Orchestrator**: Executive Orchestrator
**Closes**: #494

---

## Objective

Build an end-to-end integration test suite for the 8 canonical dogma MCP governance tools (`check_substrate`, `validate_agent_file`, `validate_synthesis`, `scaffold_agent`, `scaffold_workplan`, `run_research_scout`, `query_docs`, `prune_scratchpad`). Tests call real tool callables against the live repository, covering happy-path, cross-tool workflow, and error/edge cases. The harness integrates with the Sprint 1 metrics capture pipeline and is marked `@pytest.mark.integration` for CI gating. A runbook is added to `docs/guides/` documenting E2E test execution and result interpretation.

**Phase ordering rationale**: The runbook (Phase 2) is strictly retrospective — it documents test execution commands and `pytest` marker usage for the harness built in Phase 1. It does NOT cover metrics pipeline integration (already in `docs/guides/mcp-quality-metrics.md`) or result interpretation criteria (already in metrics baseline files). Phase 1 inputs are fully specified as: (1) existing test patterns in `tests/test_mcp_server.py`, (2) `@pytest.mark.integration` marker already registered in `pyproject.toml`, and (3) tool signatures in `mcp_server/tools/`. Per AGENTS.md: "Retrospective documentation (consolidating completed work) is the natural exception and may trail its phase."

**Governing axiom**: Endogenous-First — survey existing test patterns in `tests/test_mcp_server.py` and `tests/test_mcp_server_telemetry.py` before designing the harness. Re-use baseline metric structure from `docs/metrics/mcp-quality-baseline-2026-03-27.*`.

---

## Phase Plan

### Phase 0 — Workplan Review ✅
**Agent**: Review  
**Deliverables**:
- `## Workplan Review Output` in scratchpad, APPROVED verdict

**Depends on**: workplan committed  
**CI**: n/a (review only)  
**Status**: Complete — APPROVED (commit `30518f8`)

### Phase 1 — E2E Test Suite Implementation ✅
**Agent**: Executive Scripter  
**Deliverables**:
- `tests/integration/__init__.py` — marks integration test package
- `tests/integration/test_mcp_e2e.py` — E2E tests for all 8 canonical tools, cross-tool workflow, and error/edge cases
- `@pytest.mark.integration` marker on all tests (already registered in `pyproject.toml`)
- Tests call tool callables directly (no subprocess); `tmp_path` fixture used for file I/O isolation
- Query corpus: ≥ 2 standardized queries per tool (8 tools × 2 = ≥ 16 test cases minimum)

**Depends on**: Phase 0 APPROVED  
**CI**: `uv run pytest tests/integration/ -m integration -v`  
**Status**: Complete — 21/21 passing (commit `7d9346e`)

### Phase 1 Review — Review Gate ✅
**Agent**: Review  
**Deliverables**:
- `## Review Output` in scratchpad, APPROVED verdict

**Depends on**: Phase 1 deliverables committed  
**Gate**: Phase 2 does not begin until APPROVED  
**Status**: Complete — APPROVED

### Phase 2 — Runbook Documentation ✅
**Agent**: Executive Docs  
**Deliverables**:
- `docs/guides/mcp-e2e-testing.md` — strictly retrospective runbook covering: how to run the E2E test suite (`pytest` invocation commands), marker usage (`-m integration`), and how to interpret test output (pass/fail signals, fixture setup). Cross-references to the existing `docs/guides/mcp-quality-metrics.md` for metrics pipeline integration — does NOT re-document the metrics pipeline or define result interpretation criteria (those are already encoded in `mcp-quality-metrics.md`).

**Depends on**: Phase 1 Review APPROVED  
**CI**: n/a  
**Status**: Complete (commit `ffa9857`)

### Phase 2 Review — Review Gate ✅
**Agent**: Review  
**Deliverables**:
- `## Review Output Phase 2` in scratchpad, APPROVED verdict

**Depends on**: Phase 2 committed  
**Gate**: Session close after this gate  
**Status**: Complete — APPROVED

### Phase 3 — Session Close ✅
**Agent**: Executive Orchestrator
**Deliverables**:
- Session summary in scratchpad
- Issue #494 body checkboxes updated
- Progress comment posted on #494
- Branch pushed, PR opened

**Depends on**: Phase 2 Review APPROVED  
**CI**: n/a  
**Status**: Complete — PR #502 opened

---

## Acceptance Criteria

- [ ] `tests/integration/test_mcp_e2e.py` covers all 8 canonical MCP tools
- [ ] ≥ 2 standardized queries per tool (≥ 16 test functions)
- [ ] Cross-tool workflow test (scaffold → validate flow)
- [ ] Error/edge case tests for malformed inputs
- [ ] All integration tests marked `@pytest.mark.integration`
- [ ] Tests pass: `uv run pytest tests/integration/ -m integration -v`
- [ ] `docs/guides/mcp-e2e-testing.md` retrospective runbook committed (pytest invocation, marker usage, test output interpretation)
- [ ] Issue #494 acceptance criteria checkboxes updated
- [ ] Progress comment posted on #494
