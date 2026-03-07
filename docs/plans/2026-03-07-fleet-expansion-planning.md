# Plan: Fleet Expansion Planning Research
**Date**: 2026-03-07
**Branch**: research/fleet-expansion-planning
**Status**: In Progress

---

## Objective

Map the full desired agent fleet for EndogenAI Workflows — grounded in existing research synthesis docs and open issues — and document it as a GitHub issue tree: one tracking issue (D1: expansive fleet list as comment) and N sub-issues grouped by agent category (D2s), closing the tracker when all sub-issues are created (D3).

This is a **research and planning session only**. No `.agent.md` files will be created. Documentation and agent file changes are minimal.

---

## Acceptance Criteria

- [ ] Tracking GitHub issue created with correct labels
- [ ] Feature branch `research/fleet-expansion-planning` pushed to origin
- [ ] Workplan committed to `docs/plans/`
- [ ] Scratchpad populated with Session Start, research findings, and Orchestration Plan
- [ ] D1: Full fleet list posted as comment on tracking issue
- [ ] D2: Grouped sub-issues created for all new agent categories
- [ ] D3: Tracking issue closed once all sub-issues exist
- [ ] Session Summary written and scratchpad pruned

---

## Phase Plan

### Phase 1 — Setup (Orchestrator)

**Agent**: Executive Orchestrator (direct)
**Deliverables**:
- Branch `research/fleet-expansion-planning` created ✅
- Workplan `docs/plans/2026-03-07-fleet-expansion-planning.md` committed
- Scratchpad initialised ✅
- Tracking GitHub issue created
**Depends on**: nothing
**Gate**: Phase 2 does not start until tracking issue number confirmed

---

### Phase 2 — Research (Explore subagent, parallel queries)

**Agent**: Explore (subagent)
**Deliverables**: Dense summary of:
- All synthesis docs mentioning new agent types, workflow gaps, or specialist roles
- All open issues indicating agent needs
- Existing fleet inventory with posture/tool mapping
**Depends on**: Phase 1 (tracking issue number)
**Gate**: Phase 3 does not start until Explore returns synthesis

---

### Phase 3 — Fleet Synthesis (Orchestrator)

**Agent**: Executive Orchestrator (direct)
**Deliverables**:
- Full fleet list written to scratchpad under `## Fleet Map D1`
- Fleet list posted as comment on tracking issue (D1)
**Depends on**: Phase 2
**Gate**: Phase 4 does not start until comment is posted and confirmed

---

### Phase 4 — Sub-Issue Creation (Orchestrator direct via gh CLI)

**Agent**: Executive Orchestrator (direct)
**Deliverables**: One sub-issue per agent group, cross-referencing tracking issue (D2s)
**Depends on**: Phase 3 (fleet list confirmed)
**Gate**: Phase 5 does not start until all sub-issues confirmed created

---

### Phase 5 — Close Tracker + Session End

**Agent**: Executive Orchestrator (direct)
**Deliverables**:
- Tracking issue closed (D3)
- All work committed and pushed
- Session Summary written, scratchpad pruned
**Depends on**: Phase 4
**Gate**: Session ends when all items in Acceptance Criteria are checked

---

## Notes

- Sub-issues should be grouped by fleet tier: Executive, Research, Dev Workflow, Comms/GTM, Specialist/Domain
- Each sub-issue should describe the agent purpose, posture (read-only / read+create / full-exec), and suggested toolset
- Ground every proposed agent in at least one research doc citation or open issue signal
