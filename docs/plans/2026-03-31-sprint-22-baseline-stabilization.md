# Workplan: Sprint 22 Baseline Stabilization

**Branch**: `feat/sprint-22-baseline-stabilization`
**Date**: 2026-03-31
**Orchestrator**: Executive Orchestrator

---

## Objective

Sprint 22 establishes empirical baselines for the dogma project by executing a formal deep-dive research phase (per-topic source notes feeding a unified D4 synthesis) that directly informs all downstream planning and implementation decisions. The sprint closes 8 open issues: optimization effects research (#497), instruction format study (#491), KPI interpretation docs (#482), canonical scripts friction audit (#529), observability maturation (#534, #425), carry-in items (#430, #506). **#527 (Repositioning) is out of scope for this sprint.**

**Phase ordering decisions**:
- Phase 1 (Carry-ins) runs before research: #430 and #506 do not depend on research output
- Phase 2 (Research) is cross-cutting: per-topic source notes per issue cluster feed a single unified D4 synthesis; gates all implementation phases
- Phase 3 (Planning) is informed entirely by Phase 2 research and populates Phases 4-N
- Agents run **sequentially** (no parallel delegations) to manage rate-limit exposure
- All agents write findings directly to `.tmp/feat-sprint-22-baseline-stabilization/2026-03-31.md`
- **PAUSE POINT** after Phase 2 Review: Orchestrator surfaces findings to human; Phase 3 requires explicit human confirmation

---

## Phase Plan

### Phase 0 — Workplan Review Gate ✅
**Agent**: Review
**Verdict**: APPROVED

**Depends on**: nothing (workplan committed)
**Status**: Complete

---

### Phase 1 — Carry-Ins (#430, #506) ⬜
**Agent**: Executive Scripter (for #506 test verification); Executive Docs (for #430 closure)
**Deliverables**:
- Verify #506 CORS env var is fully implemented and tested in `web/server.py`; confirm test coverage passes
- Close #430 [ADOPTED] with a formal adoption-summary comment linking to PR #535; create `docs/guides/webmcp-integration.md` stub if not already present
- `## Phase 1 Output` written to scratchpad by each agent

**Depends on**: Phase 0 APPROVED
**CI**: Tests, Lint, Auto-validate
**Status**: Not started

### Phase 1 Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase 1 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 1 deliverables committed
**Status**: Not started

---

### Phase 2 — Deep-Dive Research: Per-Topic Source Notes + Unified D4 Synthesis ⬜
**Agent**: Executive Researcher -> Research Scout (per topic) -> Research Synthesizer -> Research Reviewer -> Research Archivist
**Deliverables**:
- Per-topic source notes in `docs/research/sources/` (one file per issue cluster):
  - `sprint-22-independent-optimization-effects.md` (for #497)
  - `sprint-22-instruction-format-efficiency.md` (for #491)
  - `sprint-22-metrics-kpi-interpretation.md` (for #482)
  - `sprint-22-canonical-scripts-friction.md` (for #529)
  - `sprint-22-observability-patterns.md` (for #534, #425)
- `docs/research/sprint-22-baseline-stabilization.md` — unified D4 synthesis (status: Final) drawing across all per-topic sources; formal Recommendations section
- `## Phase 2 Output` written to scratchpad: findings summary + key recommendations per topic
- Closes #497

**Depends on**: Phase 1 Review APPROVED
**CI**: Tests, Lint, Auto-validate (synthesis schema)
**Status**: Not started

### Phase 2 Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 2 D4 synthesis doc committed
**Status**: Not started

### PAUSE POINT — Surface Research Findings to Human
_After Phase 2 Review APPROVED_: Orchestrator reads `## Phase 2 Output` from scratchpad and surfaces findings summary, D4 Recommendations, and emergent decision points to the human. **Phase 3 does not begin without explicit human confirmation.**

---

### Phase 3 — Sprint Planning (informed by Phase 2) ⬜
**Agent**: Executive Planner
**Deliverables**:
- `## Sprint Execution Plan` section added to this workplan (Phases 4-N) with agent assignments, effort estimates (XS/S/M/L), sequencing rationale from Phase 2 D4 recommendations
- Specific phases for: #491, #482, #529, #534, #425
- New issues seeded if Phase 2 reveals untracked gaps
- `## Phase 3 Output` written to scratchpad

**Depends on**: Phase 2 Review APPROVED + human confirmation after PAUSE POINT
**CI**: Tests, Lint, Auto-validate
**Status**: Not started

### Phase 3 Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase 3 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 3 sprint execution plan committed
**Status**: Not started

---

### Phases 4-N — Implementation (TBD after Phase 3) ⬜
**Agent**: TBD — assigned by Phase 3 planning output
**Deliverables**: TBD — at minimum:
  - **Phase 4: Instruction Format + KPI Guide** — closes #491, #482 (Executive Docs)
  - **Phase 5: Scripts Audit + Observability** — closes #529, #534, #425 (Executive Scripter)
  - Each domain phase immediately followed by a Review gate

**Depends on**: Phase 3 Review APPROVED
**Status**: Not started — populated by Phase 3

---

### Final Review Phase — Cross-Fleet Intensive Review ⬜
**Agent**: Review + Executive Docs + Executive Scripter + Executive Researcher + Executive Fleet + Security Researcher + (additional topically relevant agents determined by Phase 3)
**Deliverables**:
- Each agent appends `## Final Review — <AgentName> Output` to scratchpad with their domain verdict
- All blocking findings resolved before GitHub phase begins
- `## Final Cross-Fleet Review Output` aggregated in scratchpad

**Depends on**: All implementation phases complete and committed
**CI**: Tests, Lint, Auto-validate
**Status**: Not started

### GitHub Phase — PR Open ⬜
**Agent**: GitHub
**Deliverables**:
- PR opened against `main` from `feat/sprint-22-baseline-stabilization`
- PR body links all `Closes` references
- Session scratchpad archived

**Depends on**: Final Cross-Fleet Review APPROVED
**CI**: Tests, Lint, Auto-validate
**Status**: Not started

---

## Acceptance Criteria

- [x] Phase 0 Workplan Review APPROVED
- [ ] Phase 1 carry-ins complete and committed (#430 closed, #506 verified)
- [ ] Phase 1 Review APPROVED
- [ ] Phase 2 D4 synthesis committed (status: Final) with per-topic source notes
- [ ] Phase 2 Review APPROVED
- [ ] Human confirmed continuation after PAUSE POINT
- [ ] Phase 3 sprint execution plan committed to this workplan
- [ ] Phase 3 Review APPROVED
- [ ] All implementation phases complete, reviewed, and committed
- [ ] Final cross-fleet review APPROVED (6+ agents)
- [ ] All changes pushed and PR opened against main

## PR Description Template

<!-- Copy to PR description when opening the PR -->

Closes #497, Closes #491, Closes #482, Closes #529, Closes #430, Closes #425, Closes #534, Closes #506
