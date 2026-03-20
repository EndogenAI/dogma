# Workplan: Inline Doc Context as Endogenic Content

**Branch**: `main`
**Date**: 2026-03-19
**Orchestrator**: Executive Orchestrator

---

## Objective

This session introduces the concept of **inline documentation as endogenic content** — documentation that makes the greater dogmic context explicit within the implementation itself. This strengthens the "connective tissue" between human and agent, enhancing transparency and deterministic behavior.

---

## Phase Plan

### Phase 1 — Issue Seeding ⬜
**Agent**: Executive PM
**Deliverables**:
- New GitHub issue: "feat(dogma): inline documentation as endogenic context"
- Issue labels (type:research, area:docs, priority:high)
- Acceptance criteria mapped to research and implementation goals

**Depends on**: nothing
**CI**: gh issue view
**Status**: Not started

### Phase 2 — Baseline Research ⬜
**Agent**: Executive Researcher
**Deliverables**:
- `docs/research/endogenic-inline-docs-baseline.md` (Status: Draft)
- Survey of existing research corpus (literate programming, LLM context retrieval)
- Patterns for "connective tissue" between code and dogma

**Depends on**: Phase 1
**CI**: validate_synthesis
**Status**: Not started

### Phase 3 — Synthesis & Recommendations ⬜
**Agent**: Executive Researcher
**Deliverables**:
- `docs/research/endogenic-inline-docs-synthesis.md` (Status: Final)
- Explicit recommendations for substrate encoding (comment headers, context markers)
- Tooling requirements for automated context enforcement

**Depends on**: Phase 2
**CI**: validate_synthesis
**Status**: Not started

### Phase 4 — Implementation Planning ⬜
**Agent**: Executive PM
**Deliverables**:
- Follow-up issues for recommended substrate implementations
- Milestone assignment

**Depends on**: Phase 3
**CI**: gh issue list
**Status**: Not started

### Phase 5 — Session Close ⬜
**Agent**: Executive Orchestrator
**Deliverables**:
- Fleet integration check
- Session summary in scratchpad
- Issue body checkboxes updated

**Depends on**: Phase 4
**CI**: Auto-validate
**Status**: Not started

---

## Acceptance Criteria

- [ ] All phases complete and committed
- [ ] All changes pushed and PR is up to date
