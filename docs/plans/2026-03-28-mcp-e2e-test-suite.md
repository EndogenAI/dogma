# Workplan: MCP E2E Test Suite

**Branch**: `feat/mcp-e2e-test-suite`
**Date**: 2026-03-28
**Orchestrator**: Executive Orchestrator
**Closes**: #494

---

## Objective

Build an end-to-end integration test suite for the 8 canonical dogma MCP governance tools (`check_substrate`, `validate_agent_file`, `validate_synthesis`, `scaffold_agent`, `scaffold_workplan`, `run_research_scout`, `query_docs`, `prune_scratchpad`). Tests call real tool callables against the live repository, covering happy-path, cross-tool workflow, and error/edge cases. The harness integrates with the Sprint 1 metrics capture pipeline and is marked `@pytest.mark.integration` for CI gating. A runbook is added to `docs/guides/` documenting E2E test execution and result interpretation.

**Phase ordering rationale**: The runbook (Phase 2) is explicitly retrospective documentation — it consolidates the completed test harness into a guide for future operators. It does NOT provide guidance that Phase 1 needs; Phase 1 draws from existing test patterns in `tests/test_mcp_server.py` and the Sprint 1 metrics baseline (both already committed). Per AGENTS.md: "Retrospective documentation (consolidating completed work) is the natural exception and may trail its phase." Therefore Phase 2 (docs) follows Phase 1 (implementation) by design.

**Governing axiom**: Endogenous-First — survey existing test patterns in `tests/test_mcp_server.py` and `tests/test_mcp_server_telemetry.py` before designing the harness. Re-use baseline metric structure from `docs/metrics/mcp-quality-baseline-2026-03-27.*`.

---

## Phase Plan

### Phase 0 — Workplan Review ⬜
**Agent**: Review  
**Deliverables**:
- `## Workplan Review Output` in scratchpad, APPROVED verdict

**Depends on**: workplan committed  
**CI**: n/a (review only)  
**Status**: Not started

### Phase 1 — E2E Test Suite Implementation ⬜
**Agent**: Executive Scripter  
**Deliverables**:
- `tests/integration/__init__.py` — marks integration test package
- `tests/integration/test_mcp_e2e.py` — E2E tests for all 8 canonical tools, cross-tool workflow, and error/edge cases
- `@pytest.mark.integration` marker on all tests (already registered in `pyproject.toml`)
- Tests call tool callables directly (no subprocess); `tmp_path` fixture used for file I/O isolation
- Query corpus: ≥ 2 standardized queries per tool (8 tools × 2 = ≥ 16 test cases minimum)

**Depends on**: Phase 0 APPROVED  
**CI**: `uv run pytest tests/integration/ -m integration -v`  
**Status**: Not started

### Phase 1 Review — Review Gate ⬜
**Agent**: Review  
**Deliverables**:
- `## Review Output` in scratchpad, APPROVED verdict

**Depends on**: Phase 1 deliverables committed  
**Gate**: Phase 2 does not begin until APPROVED  
**Status**: Not started

### Phase 2 — Runbook Documentation ⬜
**Agent**: Executive Docs  
**Deliverables**:
- `docs/guides/mcp-e2e-testing.md` — runbook covering: test execution commands, marker usage, result interpretation, integration with metrics pipeline, CI workflow guidance

**Depends on**: Phase 1 Review APPROVED  
**CI**: `uv run python scripts/validate_synthesis.py` (if applicable)  
**Status**: Not started

### Phase 2 Review — Review Gate ⬜
**Agent**: Review  
**Deliverables**:
- `## Review Output Phase 2` in scratchpad, APPROVED verdict

**Depends on**: Phase 2 committed  
**Gate**: Session close after this gate  
**Status**: Not started

### Phase 3 — Session Close ⬜
**Agent**: <Agent Name>
**Deliverables**:
- Fleet integration (if adding new agents/skills: run `uv run python scripts/check_fleet_integration.py --dry-run`)
- Session close (archive session, update scratchpad summary, push branch)
- <!-- add other deliverables -->

**Agent**: Executive Orchestrator  
**Deliverables**:
- Session summary in scratchpad
- Issue #494 body checkboxes updated
- Progress comment posted on #494
- Branch pushed, PR opened

**Depends on**: Phase 2 Review APPROVED  
**CI**: n/a  
**Status**: Not started

---

## Acceptance Criteria

- [ ] `tests/integration/test_mcp_e2e.py` covers all 8 canonical MCP tools
- [ ] ≥ 2 standardized queries per tool (≥ 16 test functions)
- [ ] Cross-tool workflow test (scaffold → validate flow)
- [ ] Error/edge case tests for malformed inputs
- [ ] All integration tests marked `@pytest.mark.integration`
- [ ] Tests pass: `uv run pytest tests/integration/ -m integration -v`
- [ ] `docs/guides/mcp-e2e-testing.md` runbook committed
- [ ] Issue #494 acceptance criteria checkboxes updated
- [ ] Progress comment posted on #494
