# Workplan: Full Corpus Back-Propagation into Primary Papers

**Issues**: [#165](https://github.com/EndogenAI/dogma/issues/165), [#212](https://github.com/EndogenAI/dogma/issues/212)
**Branch**: `feat/issue-165-values-synthesis`
**Related PR**: #208
**Date Created**: 2026-03-12
**Orchestrator**: Executive Orchestrator

---

## Objective

Survey the entire `docs/research/` corpus (all 72 documents) and back-propagate relevant findings into the three primary synthesis papers:

- `docs/research/values-encoding.md`
- `docs/research/bubble-clusters-substrate.md`
- `docs/research/endogenic-design-paper.md`

**Scope clarification**: The Phase 3A+3B/C pass (workplan `2026-03-12-lcf-backprop-primary-papers.md`) covered the LCF sprint findings only. This workplan covers the *whole corpus* — every research document that has findings worth weaving into the primary papers, regardless of when it was produced.

**Recency heuristic**: Older documents are *less likely* to have been incorporated into primary papers (which were authored early and updated sporadically). The sweep phase (Phase 0) determines which documents are already cited to avoid re-confirming existing references.

**Back-propagation discipline** (from `values-encoding.md` §5): Weave / Link-out / Consolidate — no annotation proliferation, no in-place definition reproduction, link to source docs for lossless access.

---

## Methodology Constraint

All back-propagation follows the three-rule discipline encoded in `values-encoding.md` §5:
1. **Weave** — integrate into existing argument structure, not appended standalone paragraphs
2. **Link-out** — cross-reference links to source docs; do not reproduce definitions in-place
3. **Consolidate** — each pass leaves the paper more coherent, not longer; annotation proliferation is a failure mode

---

## Phases

### Phase 0 — Organizational Sweep

**Agent**: Explore (read-only corpus analysis)
**Effort**: M
**Depends on**: nothing
**Status**: ⬜ Not started

**Task**: Produce `docs/plans/2026-03-12-corpus-sweep-table.md` — a structured reference table covering all 72 research docs in `docs/research/` with the following fields per document:

| Field | Values |
|-------|--------|
| Document name | filename |
| Recency tier | Old (< 2026-02) / Mid (2026-02) / Recent (2026-03) |
| Relevance to values-encoding.md | H / M / L / None + one-line rationale |
| Relevance to bubble-clusters-substrate.md | H / M / L / None + one-line rationale |
| Relevance to endogenic-design-paper.md | H / M / L / None + one-line rationale |
| Already cited in primary papers? | Yes / Partial / No — with which paper(s) |
| Recommended scout depth | Thorough / Skim / Skip + reason |

The sweep table is the Scout's guide. Depth allocations matter — it prevents the Scout from spending equal time on irrelevant docs and insufficient time on high-signal uncited ones.

**Deliverables**:
- `docs/plans/2026-03-12-corpus-sweep-table.md` committed

**Gate**: Sweep table committed; Phase 0 Review APPROVED

---

### Phase 0 Review — Review Gate

**Agent**: Review
**Depends on**: Phase 0 complete
**Status**: ⬜ Not started

**Check**: Sweep table covers all 72 docs (no omissions); relevance ratings are not uniformly L/None (would indicate under-reading); "Already cited" status is grounded in actual cross-reference checks against the three primary papers; scout-depth assignments are coherent with relevance+citation status.

**Deliverables**: APPROVED verdict in scratchpad

---

### Phase 1 — Corpus Scout (Raw Findings)

**Agent**: Research Scout
**Effort**: L
**Depends on**: Phase 0 APPROVED
**Status**: ⬜ Not started

**Task**: Using the sweep table as the guide, read all docs rated Thorough in detail; skim docs rated Skim; skip docs rated Skip. Produce `docs/plans/2026-03-12-corpus-raw-findings.md` — an unstructured findings catalogue: one section per source doc (Thorough/Skim only), listing raw observations about content that appears relevant to any of the three primary papers. Do NOT yet determine exact target sections or write proposal entries — that is Phase 2's job.

Each findings section format:
```
### [source-doc-filename]
- [observation]: [one-line description of what the doc says that may be relevant]
- [observation]: ...
```

Only include docs rated Thorough or Skim in the sweep table. Skip-rated docs get no section.

**Deliverables**:
- `docs/plans/2026-03-12-corpus-raw-findings.md` committed

**Gate**: Raw findings committed; Phase 1 Review APPROVED

---

### Phase 1 Review — Review Gate

**Agent**: Review
**Depends on**: Phase 1 complete
**Status**: ⬜ Not started

**Check**: All Thorough-rated docs have a findings section; no Skim-rated doc is missing without explanation; observations are specific (not "this doc is relevant") and grounded in actual content read; no proposal-level specificity leaking in (target sections, exact change descriptions belong in Phase 2).

**Deliverables**: APPROVED verdict in scratchpad

---

### Phase 2 — Proposal Synthesis

**Agent**: Research Synthesizer
**Effort**: M
**Depends on**: Phase 1 Review APPROVED
**Status**: ⬜ Not started

**Task**: Read `docs/plans/2026-03-12-corpus-raw-findings.md` and the current state of the three primary papers. For each raw finding, determine whether it warrants a proposal entry (absent from target paper + meaningful contribution). Produce `docs/plans/2026-03-12-backprop-proposal.md` — a structured proposal with one entry per candidate weave, grouped by target paper.

Each proposal entry format:
```
**Source doc**: [filename]
**Target paper**: [values-encoding.md | bubble-clusters-substrate.md | endogenic-design-paper.md]
**Target section**: [exact section heading as it appears in the paper]
**Proposed change**: [one sentence — update existing sentence / add forward ref bullet / extend existing list item]
**Link-out**: [proposed link anchor text → source doc section]
**Rationale**: [why this finding is absent and belongs here, one sentence]
```

Entries grouped by target paper. Filter out anything already cited (use sweep table "Already cited" field).

**Deliverables**:
- `docs/plans/2026-03-12-backprop-proposal.md` committed

**Gate**: Proposal committed; Phase 2 Review APPROVED

---

### Phase 2 Review — Review Gate

**Agent**: Review
**Depends on**: Phase 2 complete
**Status**: ⬜ Not started

**Check**: Each proposal entry names an exact target section (verifiable against the actual paper heading); proposed change follows weave/link/consolidate discipline (no entries that would add standalone paragraphs or in-place definitions); all source docs exist; no entry duplicates a reference already present in the target paper.

**Deliverables**: APPROVED verdict + any REQUEST CHANGES list in scratchpad

---

### Phase 3 — Back-Propagation

**Agent**: Executive Docs
**Effort**: L
**Depends on**: Phase 2 Review APPROVED
**Status**: ⬜ Not started

**Task**: Apply every approved proposal entry in `docs/plans/2026-03-12-backprop-proposal.md` to the three primary papers. Proposal doc is the sole authoritative specification — do not add entries not in the proposal; do not skip entries without noting the reason.

Run `validate_synthesis.py` on all three papers after all edits are complete.

**Deliverables**:
- All three primary papers updated per proposal
- `validate_synthesis.py` PASS on all three

**Gate**: ⛔ MANUAL STOP — do NOT commit; surface diffs to user for review before any commit

---

### Phase 3 Review — Manual Review (User)

**Gate**: User reviews diffs on all three papers and approves
**Status**: ⬜ Not started

After user approval:
- Commit with message `research(#165,#212): full corpus back-propagation into primary papers`
- Push
- Update issue #212 progress comment

---

## Acceptance Criteria

- [ ] Sweep table covers all 72 docs
- [ ] Raw findings doc covers all Thorough/Skim-rated docs
- [ ] Proposal has entries grouped by target paper with exact section targets
- [ ] All proposal entries follow weave/link/consolidate discipline
- [ ] All three primary papers validate_synthesis PASS after edits
- [ ] User has reviewed and approved diffs before commit
