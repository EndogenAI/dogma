# Workplan: Sprint 20 Observability Foundation

**Branch**: `feat/sprint-20-observability-foundation`
**Date**: 2026-03-30
**Orchestrator**: Executive Orchestrator
**Milestone**: #21 (Due: 2026-05-15)
**Effort**: M (medium — foundational work, moderate scope)

---

## Objective

Build observability infrastructure (CORS, eval harness, metrics capture, protocol compatibility, fleet audits) that Sprint 22 will use to establish baselines. This is foundational work, not measurement work — focus on infrastructure completeness and integration readiness. Covers 5 issues: #511 (fleet audit), #506 (CORS env var), #505 (inspector protocol), #500 (eval harness), #499 (metrics capture).

---

## Phase Plan

### Phase 0 — Workplan Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Workplan Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: nothing (pre-execution gate)
**Gate**: No Phase 1 begins until APPROVED
**Status**: Not started

### Phase 1 — Observability Foundation Gap Analysis ⬜
**Agent**: Research Scout
**Deliverables**:
- Gap analysis findings appended to scratchpad under `## Phase 1 Output`
- Bullets only, ≤2000 tokens
- Audit existing MCP observability infrastructure
- Identify gaps between current state and 5 issues' target scope
- Check for overlap/redundancy between #500 (eval harness) and #499 (metrics capture)
- Surface blocker dependencies (e.g., does #506 CORS block #505 protocol work?)
- Sequence recommendations

**Depends on**: Phase 0 APPROVED
**CI**: N/A (research phase)
**Status**: Not started

### Phase 1 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 1 Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 1 findings logged to scratchpad
**Gate**: Phase 2 does not start until APPROVED
**Status**: Not started

### Phase 2 — Sprint 20 Replanning ⬜
**Agent**: Executive Planner
**Deliverables**:
- Updated docs/plans/2026-03-30-sprint-20-observability-foundation.md with refined phases
- `## Phase 2 Output` appended to scratchpad
- Group 5 issues into logical implementation phases
- Adjust issue sequencing based on Phase 1 findings
- Return: "Workplan updated — [phase count] implementation phases, sequence: [phase names]"

**Depends on**: Phase 1 Review APPROVED
**CI**: N/A (planning phase)
**Status**: Not started

### Phase 2 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 2 Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 2 replanning complete, workplan committed
**Gate**: Phase 3 does not start until APPROVED
**Status**: Not started

### Phases 3–N — Implementation ⬜
**Agent**: To be determined by Executive Planner in Phase 2
**Deliverables**:
- Implementation of issues #511, #506, #505, #500, #499
- Each implementation phase followed by its own Review gate
- All changes committed with conventional commit messages

**Depends on**: Phase 2 Review APPROVED
**CI**: Tests, ruff, validate-agent-files (if agent files changed)
**Status**: Not started

### Phase N+1 — Cross-Agent Integration Review ⬜
**Agent**: Executive Orchestrator (self)
**Deliverables**:
- `## Phase N+1 Output` appended to scratchpad
- Verify all 5 issues' acceptance criteria satisfied
- Spot-check integration gaps (e.g., metrics capture feeding eval harness)
- Flag incomplete issues or new technical debt
- Return: Bullets only — "Issues ready" or "Issues flagged: [list with reason]"

**Depends on**: All implementation phases complete
**CI**: N/A (internal QA phase)
**Status**: Not started

### Phase N+2 — Final Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase N+2 Review Output` appended to scratchpad
- Verdict: APPROVED (gates session close)

**Depends on**: Phase N+1 integration review complete
**Gate**: Session close requires APPROVED
**Status**: Not started

### Phase N+3 — Session Close ⬜
**Agent**: Executive Orchestrator
**Deliverables**:
- Update all 5 issue bodies with checklist completeness (mark `[x]` for satisfied criteria)
- Post progress comment on each issue: "Completed in Sprint 20 — Observability Foundation"
- Write `## Session Summary` to scratchpad
- Run `uv run python scripts/prune_scratchpad.py --force`
- Push all commits

**Depends on**: Phase N+2 Review APPROVED
**CI**: N/A
**Status**: Not started

---

## Acceptance Criteria

- [ ] All 5 issues (#511, #506, #505, #500, #499) have acceptance criteria satisfied
- [ ] No integration gaps flagged in Phase N+1 cross-agent review
- [ ] All deliverables committed to feat/sprint-20-observability-foundation branch
- [ ] All changes pushed and PR opened
- [ ] Issue bodies updated with completed checkboxes
- [ ] Progress comments posted on all 5 issues

**Branch**: `main`
**Date**: 2026-03-30
**Orchestrator**: Executive Orchestrator

---

## Objective

<!-- One paragraph: what this session accomplishes -->

---

## Phase Plan

### Phase 1 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- <!-- list deliverables -->

**Depends on**: nothing
**CI**: Tests, Auto-validate
**Status**: Not started

### Phase 2 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- <!-- list deliverables -->

**Depends on**: Phase 1
**CI**: Tests, Auto-validate
**Status**: Not started

### Phase 3 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- <!-- list deliverables -->

**Depends on**: Phase 2
**CI**: Tests, Auto-validate
**Status**: Not started

### Phase 4 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- <!-- list deliverables -->

**Depends on**: Phase 3
**CI**: Tests, Auto-validate
**Status**: Not started

### Phase 5 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- Fleet integration (if adding new agents/skills: run `uv run python scripts/check_fleet_integration.py --dry-run`)
- Session close (archive session, update scratchpad summary, push branch)
- <!-- add other deliverables -->

**Depends on**: Phase 4
**CI**: Tests, Auto-validate
**Status**: Not started

---

## Acceptance Criteria

- [ ] All phases complete and committed
- [ ] All changes pushed and PR is up to date
