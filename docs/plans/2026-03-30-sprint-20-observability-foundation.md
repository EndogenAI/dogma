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

### Phase 3A — CORS Environment Variable Support (#506) ⬜
**Agent**: Executive Scripter
**Deliverables**:
- `mcp_server/dogma_server.py` updated with CORS env var handling
- `mcp_server/README.md` updated with CORS configuration instructions
- Test coverage for CORS env var parsing
- `## Phase 3A Output` appended to scratchpad

**Depends on**: Phase 2 Review APPROVED
**CI**: pytest, ruff
**Status**: Not started

### Phase 3A Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 3A Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 3A complete
**Gate**: Phase 3B does not start until APPROVED
**Status**: Not started

### Phase 3B — Inspector Protocol Integration (#505) ⬜
**Agent**: Executive Scripter
**Deliverables**:
- `.vscode/mcp.json` entry for HTTP server endpoint
- Integration test: browser inspector → MCP server
- Documentation: `docs/mcp/inspector-integration.md`
- `## Phase 3B Output` appended to scratchpad

**Depends on**: Phase 3A Review APPROVED (CORS must be working)
**CI**: pytest, ruff
**Status**: Not started

### Phase 3B Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 3B Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 3B complete
**Gate**: Phase 3C does not start until APPROVED
**Status**: Not started

### Phase 3C — Metrics Capture CI Gate (#499) ⬜
**Agent**: Executive Automator
**Deliverables**:
- CI workflow: `.github/workflows/metrics-quality-gate.yml`
- Quality threshold enforcement script (or extend existing metrics script)
- Alert mechanism documentation
- `## Phase 3C Output` appended to scratchpad

**Depends on**: Phase 3B Review APPROVED
**CI**: yaml-lint, workflow validation
**Status**: Not started

### Phase 3C Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 3C Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 3C complete
**Gate**: Phase 4 does not start until APPROVED
**Status**: Not started

### Phase 4 — Fleet Capability Audit Integration (#511) ⬜
**Agent**: Executive Fleet
**Deliverables**:
- Pre-commit hook or CI gate for fleet audit script
- Tool/capability drift detection integration
- Documentation: when and how the audit runs
- `## Phase 4 Output` appended to scratchpad

**Depends on**: Phase 3C Review APPROVED
**CI**: pre-commit config validation
**Status**: Not started

### Phase 4 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 4 Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 4 complete
**Gate**: Phase 5 does not start until APPROVED
**Status**: Not started

### Phase 5 — Cross-Agent Integration Review ⬜
**Agent**: Executive Orchestrator (self)
**Deliverables**:
- `## Phase 5 Output` appended to scratchpad
- Verify all 4 implemented issues' (#506, #505, #499, #511) acceptance criteria satisfied
- Spot-check integration: CORS → inspector protocol → metrics capture
- Flag incomplete issues or new technical debt
- Return: Bullets only — "Issues ready" or "Issues flagged: [list with reason]"

**Depends on**: Phase 4 Review APPROVED
**CI**: N/A (internal QA phase)
**Status**: Not started

### Phase 6 — Final Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 6 Review Output` appended to scratchpad
- Verdict: APPROVED (gates session close)

**Depends on**: Phase 5 integration review complete
**Gate**: Session close requires APPROVED
**Status**: Not started

### Phase 7 — Session Close ⬜
**Agent**: Executive Orchestrator
**Deliverables**:
- Update issue bodies (#506, #505, #499, #511) with completed checkboxes
- Post progress comment on each implemented issue
- Seed #500 as Sprint 21 deferred work
- Write `## Session Summary` to scratchpad
- Run `uv run python scripts/prune_scratchpad.py --force`
- Push all commits

**Depends on**: Phase 6 Review APPROVED
**CI**: N/A
**Status**: Not started

---

## Acceptance Criteria

- [ ] 4 issues (#506, #505, #499, #511) implemented with acceptance criteria satisfied
- [ ] #500 (eval harness) deferred to Sprint 21 — rationale: large effort per Phase 1; accepting incomplete metrics surfaces as tracked technical debt
- [ ] No integration gaps flagged in Phase 5 cross-agent review (CORS → inspector → metrics chain validated)
- [ ] All deliverables committed to feat/sprint-20-observability-foundation branch
- [ ] All changes pushed and PR opened
- [ ] Issue bodies updated with completed checkboxes for 4 implemented issues
- [ ] Progress comments posted on #506, #505, #499, #511
- [ ] #500 seeded with "Sprint 21 — deferred from Sprint 20" milestone/label

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
