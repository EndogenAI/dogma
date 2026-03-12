# Workplan: Issue #165 — Values-Synthesis Research Sprint

**Issue**: [#165 — Research — Synthesis of Values-Encoding and Bubble-Clusters; Informing Endogenic Design](https://github.com/EndogenAI/dogma/issues/165)
**Branch**: `feat/issue-165-values-synthesis`
**Date Created**: 2026-03-11
**Orchestrator**: Executive Orchestrator

> **Predecessor context**: Issue #164 (corpus analysis + gap analyses for all three primary
> papers) merged via PR #166 on 2026-03-10. All three gap-analysis documents are Final
> and serve as the primary endogenous sources for this sprint.

---

## Objective

Synthesize `docs/research/values-encoding.md` (vertical/inheritance-chain model) and
`docs/research/bubble-clusters-substrate.md` (horizontal/topological model) into a coherent
relationship analysis; assess alignment with `docs/research/endogenic-design-paper.md`; and
evaluate whether all three papers together support or challenge MANIFESTO.md axioms.

Four Core Questions govern the sprint:

- **CQ1** — How do values-encoding.md and bubble-clusters-substrate.md relate?
- **CQ2** — Should they be merged into one document or kept orthogonal? (justification required)
- **CQ3** — How does the synthesis inform and enforce endogenic-design-paper.md?
- **CQ4** — Do the three papers support or challenge MANIFESTO.md axioms?

---

## Acceptance Criteria

- [ ] `docs/research/values-substrate-relationship.md` committed in D4 format
  (`title` + `status` frontmatter; §1 Executive Summary; §2 Hypothesis Validation;
  §3 Pattern Catalog; §4 Recommendations; §5 Sources)
- [ ] `validate_synthesis.py` exits 0 on deliverable
- [ ] All four CQs answered with evidence in the document
- [ ] Synthesis decision (CQ2) documented with ≥3 distinct justifications
- [ ] §4 Recommendations maps all 5 MANIFESTO.md axioms with an operationalization verdict
- [ ] §5 Sources lists ≥5 citeable sources
- [ ] Forward references added to all three primary papers
- [ ] `Closes #165` present in PR body; issue auto-closed on merge

---

## Endogenous Sources (read before any delegation)

1. `docs/plans/2026-03-10-milestone-9-research-sprint.md` — Phase 7 context
2. `docs/research/gap-analysis-values-encoding.md` — Gap 2: topological dimension missing
3. `docs/research/gap-analysis-bubble-clusters.md` — Gap 3: membrane permeability gap
4. `docs/research/gap-analysis-endogenic-design.md` — H2/H3 morphogenetic gaps
5. `docs/research/values-encoding.md` — primary: vertical/inheritance-chain model
6. `docs/research/bubble-clusters-substrate.md` — primary: horizontal/topological model
7. `docs/research/endogenic-design-paper.md` — primary: four-hypothesis integrative framework
8. `MANIFESTO.md` §1–§3 — axiom definitions for CQ4 mapping

---

## Execution Phases

### Phase 1 — Corpus Scout

**Agent**: Research Scout
**Effort**: M (15–20h)
**Depends on**: Nothing
**Status**: ⬜ Not started

Map all cross-references between the three primary papers and all three gap analyses.
Document dimensional-relationship evidence without interpretation. Flag any conflicting
claims between papers.

**Deliverables**:
- D1: `## Phase 1 Scout Output` in `.tmp/feat-issue-165-values-synthesis/<date>.md`
  — cross-reference map (vertical vs. horizontal dimension evidence; verbatim quotes
  from Gap 2 of gap-analysis-values-encoding.md and H5 verdict from bubble-clusters-substrate.md)
- D2: Bullet list of all claims in gap analyses bearing on CQ1–CQ4
- D3: Risk flags — any conflicting claims between the three papers

**Gate**: D1 present in scratchpad with explicit quotes from Gap 2 and H5 verdict
before Phase 2 begins.

---

### Phase 1 Review — Review Gate

**Agent**: Review
**Effort**: XS
**Depends on**: Phase 1 deliverables logged to scratchpad
**Status**: ⬜ Not started

**Gate**: APPROVED verdict recorded before Phase 2 begins.

---

### Phase 2 — Relationship Analysis & Synthesis Decision (CQ1 + CQ2)

**Agent**: Executive Researcher
**Effort**: M (15–20h)
**Depends on**: Phase 1 Review APPROVED
**Status**: ⬜ Not started

Using Scout findings, analyze the dimensional structure of the two encoding models.
Determine the synthesis decision with ≥3 justifications. Produce D4 doc §1–§2.

**Deliverables**:
- D1: `docs/research/values-substrate-relationship.md` §1 Executive Summary
  — dimensional structure claim + synthesis decision with justifications
- D2: `docs/research/values-substrate-relationship.md` §2 Hypothesis Validation
  — vertical dimension table; horizontal dimension table; two worked examples;
  B8 Degradation Table interpretation
- D3: Scratchpad `## Phase 2 Synthesis Decision` — rationale summary (≤500 tokens)

**Gate**: D1 + D2 committed; `validate_synthesis.py` passes format preamble check.

---

### Phase 2 Review — Review Gate

**Agent**: Review
**Effort**: XS
**Depends on**: Phase 2 deliverables committed
**Status**: ⬜ Not started

**Gate**: APPROVED verdict recorded before Phase 3 begins.

---

### Phase 3 — Endogenic Design Alignment (CQ3)

**Agent**: Executive Researcher
**Effort**: S (8–12h)
**Depends on**: Phase 2 Review APPROVED
**Status**: ⬜ Not started

Map the Phase 2 relationship finding onto endogenic-design-paper.md's four hypotheses
(H1–H4) and four contributions (C1–C4).

**Deliverables**:
- D1: `docs/research/values-substrate-relationship.md` §3 Pattern Catalog
  — per-hypothesis mapping table (H1–H4, C1–C4 cross-referenced to model)
- D2: Explicit statement for any CQ3 evidence gaps not covered by existing papers

**Gate**: §3 committed; `validate_synthesis.py` passes before Phase 4.

---

### Phase 3 Review — Review Gate

**Agent**: Review
**Effort**: XS
**Depends on**: Phase 3 deliverables committed
**Status**: ⬜ Not started

**Gate**: APPROVED verdict recorded before Phase 4 begins.

---

### Phase 4 — MANIFESTO.md Dogma Assessment (CQ4)

**Agent**: Executive Researcher
**Effort**: S (8–12h)
**Depends on**: Phase 3 Review APPROVED
**Status**: ⬜ Not started

Map all 5 MANIFESTO.md axioms against the three-paper synthesis. Classify each:
fully operationalized / partially operationalized / challenged / not addressed.

**Deliverables**:
- D1: `docs/research/values-substrate-relationship.md` §4 Recommendations
  — axiom coverage table (5 rows); any amendments proposed
- D2: `docs/research/values-substrate-relationship.md` §5 Sources (≥5 entries)
- D3: Scratchpad `## Dogma Assessment` — 5-row axiom verdict (≤200 tokens)

**⚠️ Hard stop**: If any axiom is classified "challenged" or "not addressed",
STOP and surface to user before proposing MANIFESTO.md edits.

**Gate**: §4 + §5 committed; `validate_synthesis.py` exits 0; all 5 axioms present;
bibliography ≥5 entries. If axiom amendment proposed: gate on explicit user approval.

---

### Phase 4 Review — Review Gate

**Agent**: Review
**Effort**: XS
**Depends on**: Phase 4 deliverables committed
**Status**: ⬜ Not started

**Full review checklist**:
- [ ] `validate_synthesis.py` exits 0 on `values-substrate-relationship.md`
- [ ] All 4 CQs answered with explicit section-bounded evidence
- [ ] Synthesis decision has ≥3 justifications documented
- [ ] §4 Recommendations contains all 5 MANIFESTO axioms with verdicts
- [ ] §5 Sources ≥5 entries

**Gate**: APPROVED verdict recorded before Phase 5 begins.

---

### Phase 5 — Cross-Reference Integration

**Agent**: Executive Docs
**Effort**: XS (2–4h)
**Depends on**: Phase 4 Review APPROVED
**Status**: ⬜ Not started

Add forward references from the three primary papers to `values-substrate-relationship.md`.
No structural changes — forward-reference additions only. Run `validate_synthesis.py`
on each modified file individually.

**Deliverables**:
- D1: `docs/research/values-encoding.md` — `Related` frontmatter updated; §1 gains
  forward reference note
- D2: `docs/research/bubble-clusters-substrate.md` — `Related` frontmatter updated
- D3: `docs/research/endogenic-design-paper.md` — cross-reference note added

**Gate**: All three edits committed; `validate_synthesis.py` exits 0 on each file.

---

### Phase 5 Review — Final Review Gate

**Agent**: Review
**Effort**: XS
**Depends on**: Phase 5 deliverables committed
**Status**: ⬜ Not started

**Final checklist** (adds to Phase 4 Review checklist):
- [ ] Forward references present in all 3 primary papers
- [ ] `validate_synthesis.py` passes on all 3 modified primary papers

**Gate**: APPROVED verdict recorded before Phase 6 (Sprint Wrapup).

---

### Phase 6 — Sprint Wrapup

**Agent**: GitHub
**Effort**: XS (1h)
**Depends on**: Phase 5 Review APPROVED
**Status**: ⬜ Not started

**Deliverables**:
- D1: PR created/updated with `Closes #165` in body
- D2: `gh issue comment 165` — progress comment with deliverables + commit SHAs
- D3: Session Summary in scratchpad; `uv run python scripts/prune_scratchpad.py --force`
- D4: `gh run list --limit 3` — CI green before requesting Copilot review

---

## Dependency Graph

```
Phase 1 — Corpus Scout (Research Scout)
     ↓ Review Gate
Phase 2 — Relationship Analysis + CQ1+CQ2 (Executive Researcher)
     ↓ Review Gate
Phase 3 — Endogenic Design Alignment CQ3 (Executive Researcher)
     ↓ Review Gate
Phase 4 — Dogma Assessment CQ4 + Doc Complete (Executive Researcher)
     ↓ Review Gate
Phase 5 — Cross-Reference Integration (Executive Docs)
     ↓ Final Review Gate
Phase 6 — Sprint Wrapup (GitHub)
```

All phases strictly sequential. No parallelisation.

---

## Effort Summary

| Phase | Agent | Effort | Hours Est. |
|-------|-------|--------|------------|
| 1 — Corpus Scout | Research Scout | M | 15–20h |
| 1 Review | Review | XS | 1h |
| 2 — Relationship Analysis | Executive Researcher | M | 15–20h |
| 2 Review | Review | XS | 1h |
| 3 — Endogenic Alignment | Executive Researcher | S | 8–12h |
| 3 Review | Review | XS | 1h |
| 4 — Dogma Assessment | Executive Researcher | S | 8–12h |
| 4 Review | Review | XS | 1h |
| 5 — Cross-Reference Update | Executive Docs | XS | 2–4h |
| 5 Review (Final) | Review | XS | 1h |
| 6 — Sprint Wrapup | GitHub | XS | 1h |
| **TOTAL** | | **L** | **54–73h** |

---

## Dependency Risks

1. **CQ2 synthesis decision gates all downstream phases** — orthogonality vs. merge
   changes the phase 3–4 arc. Low risk: gap analyses pre-confirm orthogonality.
2. **All three gap-analysis files must be `status: Final`** before Scout delegation.
   Verify before Phase 1: `grep 'status:' docs/research/gap-analysis-*.md`
3. **MANIFESTO.md amendment hard-stop in Phase 4** — if any axiom is "challenged",
   user approval required before Phase 5. Very low risk per gap analyses.
4. **Phase 5 validate_synthesis.py must run per-file** — not only at phase end.
