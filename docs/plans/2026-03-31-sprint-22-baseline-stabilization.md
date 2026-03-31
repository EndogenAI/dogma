# Workplan: Sprint 22 Baseline Stabilization

**Branch**: `feat/sprint-22-baseline-stabilization`
**Date**: 2026-03-31
**Orchestrator**: Executive Orchestrator

---

## Objective

Sprint 22 establishes empirical baselines and strategic groundwork for the dogma project by executing a formal deep-dive research phase (corpus + external web) that directly informs all downstream planning and implementation decisions. The sprint closes 9 open issues spanning: strategic repositioning of dogma as a framework-agnostic validator (#527), optimization effects research (#497), instruction format study (#491), KPI interpretation docs (#482), canonical scripts friction audit (#529), observability maturation (#534, #425, #430), and CORS hardening (#506). The final deliverable is a PR with a cross-fleet review gate validating all outputs.

**Chicken-and-Egg decision**: Phase 1 research is placed before Phase 2 planning because the research output (#497) directly informs which implementation phases are needed and how they should be sequenced. Documentation phases that encode new guidance precede the implementation phases that depend on them.

---

## Phase Plan

### Phase 0 — Workplan Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Workplan Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: nothing (workplan committed)
**CI**: Tests, Lint, Auto-validate
**Status**: Not started

---

### Phase 1 — Deep-Dive Research & D4 Synthesis ⬜
**Agent**: Executive Researcher → Research Scout → Research Synthesizer → Research Reviewer → Research Archivist
**Deliverables**:
- Corpus sweep of `docs/research/` for prior optimization and instruction-format work
- External web scouting (≥5 authoritative sources) covering: independent optimization effects, instruction format efficiency, framework-agnostic governance validators
- `docs/research/sprint-22-baseline-stabilization.md` — committed D4 synthesis doc (status: Final) with formal Recommendations section covering all Milestone 38 themes
- Closes #497

**Depends on**: Phase 0 Review APPROVED
**CI**: Tests, Lint, Auto-validate
**Status**: Not started

### Phase 1 Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 1 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 1 D4 doc committed
**CI**: Auto-validate (synthesis schema)
**Status**: Not started

---

### Phase 2 — Sprint Planning (informed by Phase 1) ⬜
**Agent**: Executive Planner
**Deliverables**:
- `## Sprint Execution Plan` section added to this workplan (Phases 3–N) with agent assignments, effort estimates (XS/S/M/L), and sequencing rationale derived from Phase 1 recommendations
- Specific phases for: Strategic Repositioning Docs (#527), Instruction Format (#491), KPI Guide (#482), Scripts Audit (#529), Observability (#534, #425, #430), CORS (#506)
- Any new issues seeded if Phase 1 reveals untracked gaps

**Depends on**: Phase 1 Review APPROVED
**CI**: Tests, Lint, Auto-validate
**Status**: Not started

### Phase 2 Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 2 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 2 sprint execution plan committed
**CI**: Tests, Lint, Auto-validate
**Status**: Not started

---

### Phases 3–N — Implementation (TBD after Phase 2) ⬜
**Agent**: TBD — assigned by Phase 2 planning output
**Deliverables**:
- TBD — at minimum the following thematic phases will be defined:
  - **Phase 3: Strategic Repositioning Docs** — closes #527 (Executive Docs)
  - **Phase 4: Instruction Format + KPI Guide** — closes #491, #482 (Executive Docs)
  - **Phase 5: Scripts Audit + Observability** — closes #529, #534, #425, #430 (Executive Scripter)
  - **Phase 6: CORS + Integration Cleanup** — closes #506 (Executive Scripter)
  - Each domain phase immediately followed by a Review gate

**Depends on**: Phase 2 Review APPROVED
**CI**: Tests, Lint, Auto-validate
**Status**: Not started — populated by Phase 2

---

### Final Review Phase — Cross-Fleet Intensive Review ⬜
**Agent**: Review + Executive Docs + Executive Scripter + Executive Researcher + Executive Fleet
**Deliverables**:
- All five agents independently validate the sprint deliverables against their domain standards
- `## Final Cross-Fleet Review Output` appended to scratchpad with aggregate verdict
- All blocking findings resolved and re-validated before GitHub phase begins

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

- [ ] Phase 0 Review APPROVED before Phase 1 begins
- [ ] Phase 1 D4 synthesis doc committed with status: Final
- [ ] Phase 1 Review APPROVED before Phase 2 begins
- [ ] Phase 2 sprint execution plan committed to this workplan
- [ ] Phase 2 Review APPROVED before implementation phases begin
- [ ] All implementation phases complete, reviewed, and committed
- [ ] Final cross-fleet review APPROVED by all five agents
- [ ] All changes pushed and PR opened against main

## PR Description Template

<!-- Copy to PR description when opening the PR -->

Closes #497, Closes #527, Closes #491, Closes #482, Closes #529, Closes #430, Closes #425, Closes #534, Closes #506
