# Workplan: Inline Doc Context as Endogenic Content

**Branch**: `main`
**Date**: 2026-03-19
**Orchestrator**: Executive Orchestrator

---

## Objective

This session introduces the concept of **inline documentation as endogenic content** — documentation that makes the greater dogmic context explicit within the implementation itself. This strengthens the "connective tissue" between human and agent, enhancing transparency and deterministic behavior.

---

## Phase Plan

### Phase 1 — Issue Seeding ✅
**Agent**: Executive PM
**Deliverables**:
- New GitHub issue: "feat(dogma): inline documentation as endogenic context" #401
- Issue labels (type:research, area:docs, priority:high)
- Acceptance criteria mapped to research and implementation goals

**Status**: ✅ Complete

### Phase 2 — Baseline Research ✅
**Agent**: Executive Researcher
**Deliverables**:
- [docs/research/endogenic-inline-docs-baseline.md](../research/endogenic-inline-docs-baseline.md) (Status: Final)
- Survey of existing research corpus (literate programming, LLM context retrieval)
- Patterns for "connective tissue" between code and dogma
- Terminology refactored: "Cotton Gin" -> "Substrate Distiller"

**Depends on**: Phase 1
**CI**: validate_synthesis
**Status**: ✅ Complete — APPROVED

### Phase 3 — Synthesis & Recommendations ✅
**Agent**: Executive Researcher
**Deliverables**:
- [docs/research/endogenic-inline-docs-synthesis.md](../research/endogenic-inline-docs-synthesis.md) (Status: Final)
- Explicit recommendations for substrate encoding (comment headers, context markers)
- Tooling requirements for automated context enforcement (the "Substrate Distiller")

**Depends on**: Phase 2
**CI**: validate_synthesis
**Status**: ✅ Complete — APPROVED

### Phase 4 — Implementation Planning ✅
**Agent**: Executive Planner / Scripter
**Deliverables**:
- Draft `scripts/substrate_distiller.py` requirements
- Integration plan for `Review` agent gates
- Definition of RDI (Rationale Density Indicator) metric calculation
- Implementation planning artifact: `docs/plans/2026-03-20-substrate-distiller-implementation-planning.md`

**Depends on**: Phase 3
**Status**: ✅ Complete

### Phase 5 — Implementation Follow-up ✅
**Agent**: Executive PM
**Deliverables**:
- Follow-up issues for recommended substrate implementations
- Milestone assignment
- Created follow-up issues: #403, #404
- Milestone assigned: Sprint 23+ Backlog on #401, #403, #404

**Depends on**: Phase 3
**CI**: gh issue list
**Status**: ✅ Complete

### Phase 6 — Session Close ⬜
**Agent**: Executive Orchestrator
**Deliverables**:
- Fleet integration check
- Session summary in scratchpad
- Issue body checkboxes updated

**Depends on**: Phase 5
**CI**: Auto-validate
**Status**: Not started

---

## Acceptance Criteria

- [x] Phases 1-5 complete and committed
- [x] All changes pushed and PR is up to date
