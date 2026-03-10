# Workplan: Issue 164 Corpus Analysis

**Branch**: `feat/issue-164-corpus-analysis`
**Date**: 2026-03-10
**Issue**: #164
**Orchestrator**: Executive Orchestrator

---

## Objective

Conduct a comprehensive gap analysis of how the corpus of `docs/research/**.md` supports, challenges, and fills gaps in the three primary research synthesis papers: `endogenic-design-paper.md`, `values-encoding.md`, and `bubble-clusters-substrate.md`. Produce updated primary papers with corpus citations and three new gap-analysis documents identifying synthesis gaps and recommending follow-up research.

---

## Phase Plan

### Phase 1 — Research & Corpus Analysis ⬜
**Agent**: Executive Researcher → Research Scout fleet
**Deliverables**:
- Source corpus inventory and categorization 
- Gap analysis findings logged to `.tmp/` scratchpad
- Weak-support and challenge areas identified for each paper
- Preliminary reference mappings

**Depends on**: nothing
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase 1 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Review Output` in scratchpad with verdict (APPROVED / REQUEST CHANGES)

**Depends on**: Phase 1 deliverables logged
**CI**: N/A
**Status**: Not started

---

### Phase 2 — Update Primary Papers & Create Gap Analyses ⬜
**Agent**: Executive Docs
**Deliverables**:
- `docs/research/endogenic-design-paper.md` updated with corpus citations
- `docs/research/values-encoding.md` updated with corpus citations
- `docs/research/bubble-clusters-substrate.md` updated with corpus citations
- `docs/research/gap-analysis-endogenic-design.md` (new, with D4 frontmatter)
- `docs/research/gap-analysis-values-encoding.md` (new, with D4 frontmatter)
- `docs/research/gap-analysis-bubble-clusters.md` (new, with D4 frontmatter)

**Depends on**: Phase 1 Review APPROVED
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase 2 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Review Output` in scratchpad with verdict (APPROVED / REQUEST CHANGES)

**Depends on**: Phase 2 deliverables committed
**CI**: N/A
**Status**: Not started

---

### Phase 3 — Commit & Push ⬜
**Agent**: GitHub
**Deliverables**:
- Branch pushed; PR opened
- Issue #164 checkboxes marked complete

**Depends on**: Phase 2 Review APPROVED
**CI**: N/A
**Status**: Not started

---

## Acceptance Criteria

- [x] Workplan created and committed
- [ ] Phase 1 corpus analysis complete and logged
- [ ] Phase 1 Review gate passed
- [ ] Phase 2 primary papers updated and gap-analyses written
- [ ] Phase 2 Review gate passed
- [ ] All changes committed and pushed
- [ ] PR open linking issue #164
- [ ] Issue #164 checkboxes all marked complete
