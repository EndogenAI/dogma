# Workplan: Back-Propagation Sprint — LCF + Vocabulary-Bridge Findings into Primary Papers

**Issues**: [#165](https://github.com/EndogenAI/dogma/issues/165), [#212](https://github.com/EndogenAI/dogma/issues/212)
**Branch**: `feat/issue-165-values-synthesis`
**Related PR**: #208 (open — this sprint completes before merge)
**Date Created**: 2026-03-12
**Orchestrator**: Executive Orchestrator

---

## Objective

Back-propagate findings from the LCF Research Sprint (Phase A of issue #212) into the three primary research papers, in dependency order:

1. **Phase A (parallel)**: Update `values-encoding.md` and `bubble-clusters-substrate.md` with vocabulary bridge terms, LCF structural-enabler framing, and `values-substrate-relationship.md` orthogonality findings.
2. **Phase B (sequential)**: Update `docs/research/endogenic-design-paper.md` using the updated Phase A papers as upstream grounding.

Only after Phase B is complete is MANIFESTO §3 back-propagation considered complete (per issue #212 sequencing constraint).

---

## Methodology

Back-propagation into primary papers follows three rules (encoded in `values-encoding.md` §5):
1. **Weave** — integrate findings into the paper's existing argument structure; do not append standalone paragraphs
2. **Link-out** — reference definitions and elaborations in source documents via cross-reference link; do not reproduce them in-place
3. **Consolidate** — the paper should be more coherent after the pass, not longer; annotation proliferation is a failure mode

---

## Endogenous Sources (read before any delegation)

1. `docs/research/vocabulary-bridge-encoding-models.md` — 5 bridge terms; orthogonality preservation verdict (primary source for A1+A2)
2. `docs/research/lcf-oversight-infrastructure.md` — structural-enabler framing for LCF (primary source for A1+B)
3. `docs/research/lcf-programmatic-enforcement.md` — F4 gap closure; check_model_usage.py WARN gate (primary source for A1+B)
4. `docs/research/values-substrate-relationship.md` — dimensional orthogonality claim, H1–H4 mapping table, C4 gap (primary source for A1+A2+B)
5. `MANIFESTO.md` §3 — updated structural-enabler text (2026-03-12) as reference for design paper alignment
6. `docs/research/values-encoding.md` — current state; §6 F4 gap entries and Priority-Ordered Gap List (target of A1)
7. `docs/research/bubble-clusters-substrate.md` — current state; §6 Gap Analysis and Pattern B1/B5 (target of A2)
8. `docs/research/endogenic-design-paper.md` — current state; §3.4, §5.2, §7 (target of B)

---

## Execution Phases

### Phase A1 — Update `values-encoding.md`

**Agent**: Executive Docs
**Effort**: M
**Depends on**: nothing (sprint research docs already committed)
**Status**: ⬜ Not started

**Specific changes required** (Executive Docs reads the source docs and applies these):

1. **F4 Gap entry — update "soft gate" language** (`## 6. Appendix — [4,1] Encoding Coverage Audit`, Priority-Ordered Gap List item #2):
   - Replace "soft gate only / candidate hard programmatic gate" framing with: the semantic-intent gate is now *deliberately* the human-judgment tier; observable-proxy WARN gate (`check_model_usage.py`) is now *recommended* (not deferred); LCF F4 status is "partially addressed — see `lcf-programmatic-enforcement.md`"

2. **F4 gap entry paragraph** (around line 446 — the "Soft gate only" paragraph):
   - Update the opening statement from "Soft gate only — ... No CI-enforced script" to reflect the two-surface split established in `lcf-programmatic-enforcement.md` and the MANIFESTO §3 revision; the forward link "*Addressed by*" is already there but the paragraph above it contradicts the current state

3. **Add vocabulary bridge reference** — in §5 Open Questions or §7 Gap Analysis, add a note that `vocabulary-bridge-encoding-models.md` proposes 5 bridge terms (Signal Boundary, Transit Loss, Preservation Unit, Substrate Coherence, Boundary Specification) that operationalize the interface between the [4,1] vertical model (this paper) and the bubble-clusters horizontal model

4. **Add `values-substrate-relationship.md` to Related section** — confirm it is referenced and describe its role: formal dimensional orthogonality analysis establishing that the two models are complementary not competing

5. **§5 Back-Propagation section** (around line 400) — add a note that the LCF Research Sprint (2026-03-12) is a concrete back-propagation event: values-encoding.md F4 gap evidence propagated into MANIFESTO §3 via issues #209/#211

**Deliverables**:
- D1: `docs/research/values-encoding.md` updated (F4 entries corrected, vocabulary bridge reference added, values-substrate-relationship referenced)
- D2: `validate_synthesis.py` confirms PASS after edits

**Gate**: D1 committed; validate_synthesis PASS

---

### Phase A2 — Update `bubble-clusters-substrate.md`

**Agent**: Executive Docs
**Effort**: S
**Depends on**: nothing (sprint research docs already committed)
**Status**: ⬜ Not started

**Specific changes required**:

1. **Pattern B1 (Calibrated Membrane Permeability)** — add reference: the vocabulary bridge paper formalises the shared vocabulary for membrane boundary events: Signal Boundary (the event itself), Preservation Unit (what must survive), Boundary Specification (the pre-declared policy). Reference `vocabulary-bridge-encoding-models.md`.

2. **§6 Gap Analysis — Forward References** — add:
   - `docs/research/vocabulary-bridge-encoding-models.md` — provides shared vocabulary (Signal Boundary, Transit Loss, Preservation Unit, Boundary Specification, Substrate Coherence) bridging membrane model concepts to the inheritance-chain model
   - `docs/research/values-substrate-relationship.md` — formal dimensional orthogonality analysis establishing that bubble-clusters (horizontal/topological) and values-encoding (vertical/inheritance) are complementary, non-competing models

3. **Substrate Coherence** — in Pattern B2 (Connectivity Atlas) or §6, add a note that `substrate-coherence` is now a formally defined term in `docs/glossary.md`, bridging the connectivity dimension (this paper) with the fidelity dimension (values-encoding.md)

**Deliverables**:
- D1: `docs/research/bubble-clusters-substrate.md` updated (Pattern B1 vocabulary reference, §6 forward refs)
- D2: `validate_synthesis.py` confirms PASS

**Gate**: D1 committed; validate_synthesis PASS

---

### Phase A Review — Review Gate

**Agent**: Review
**Depends on**: Phase A1 + A2 (both D1 committed)
**Status**: ⬜ Not started

Validate both papers: validate_synthesis PASS, MANIFESTO citations intact, no new D4 schema violations introduced by the edits.

**Gate**: APPROVED verdict for both papers before Phase B starts

---

### Phase B — Update `endogenic-design-paper.md`

**Agent**: Executive Docs
**Effort**: M
**Depends on**: Phase A Review APPROVED
**Status**: ⬜ Not started

**Specific changes required**:

1. **§7 Gap Analysis — Key Gaps**: Add or update LCF entry:
   - Note that LCF is now framed as oversight infrastructure (not merely cost tier) per `lcf-oversight-infrastructure.md`; MANIFESTO §3 amended 2026-03-12
   - Note check_model_usage.py WARN gate is recommended (F4 partially addressed); status: "in progress — see #131"

2. **§7 Gap Analysis — Forward References**: Add:
   - `docs/research/lcf-oversight-infrastructure.md` — structural-enabler framing for Local-Compute-First
   - `docs/research/lcf-programmatic-enforcement.md` — F4 observable-proxy gate design
   - `docs/research/vocabulary-bridge-encoding-models.md` — cross-model vocabulary bridge
   - `docs/research/values-substrate-relationship.md` — formal dimensional orthogonality analysis (already has a cross-reference at §4.3 — confirm it and add to forward refs list)

3. **§3.4 Pattern Catalog or §3.1 Encoding Chain**: Add or update an LCF pattern note — LCF is now a structural governance property (enforcement proximity, oversight co-location) not merely a cost-optimisation tier; reference `lcf-oversight-infrastructure.md` and the updated MANIFESTO §3

4. **§5.2 Limitations**: Update the LCF / programmatic enforcement para (if present) to note the F4 partial-resolution status

5. **§5.4 Open Empirical Questions**: If LCF enforcement tractability is listed, update to reflect check_model_usage.py recommendation

**Deliverables**:
- D1: `docs/research/endogenic-design-paper.md` updated (§3.4/§3.1, §5.2/§5.4, §7 all touched)
- D2: `validate_synthesis.py` confirms PASS

**Gate**: D1 committed; validate_synthesis PASS

---

### Phase B Review — Review Gate

**Agent**: Review
**Depends on**: Phase B D1 committed
**Status**: ⬜ Not started

Validate endogenic-design-paper.md: validate_synthesis PASS, no D4 schema violations, LCF structural-enabler framing correctly integrated.

**Gate**: APPROVED verdict before Phase C

---

### Phase C — Commit, Issue #165 Update, Push

**Agent**: Executive Orchestrator (GitHub operations)
**Depends on**: Phase B Review APPROVED
**Status**: ⬜ Not started

1. Commit all Phase A + B file changes
2. Update issue #165 body to add Phase 3 back-propagation deliverables checklist (checked off as complete)
3. Post session-close comment on #212 noting Phase A completion
4. Push

**Gate**: `git push` completes; `gh pr view 208` confirms Closes #165/#209/#210/#211

---

## Acceptance Criteria

- [ ] `docs/research/values-encoding.md`: F4 gap entry updated; vocabulary bridge reference added; values-substrate-relationship.md referenced in Related
- [ ] `docs/research/bubble-clusters-substrate.md`: Pattern B1 vocabulary reference added; §6 forward refs include vocabulary-bridge and values-substrate-relationship
- [ ] `docs/research/endogenic-design-paper.md`: §3.x LCF structural-enabler note; §7 forward refs include all 4 sprint docs; §5 F4 status updated
- [ ] `validate_synthesis.py` PASS on all three papers post-edit
- [ ] Issue #165 body updated with Phase 3 back-propagation deliverables
- [ ] All changes committed and pushed on `feat/issue-165-values-synthesis`
- [ ] Phase A of issue #212 confirmed complete via issue comment

---

## Back-Propagation Sequencing Note

Per user instruction (2026-03-12): Full back-propagation is considered complete only after:
1. This sprint (Phase A of #212) — updates two primary papers with sprint findings ✅
2. Phase B of #212 — targeted MANIFESTO §3 re-review against updated endogenic design paper
3. Phase C of #212 — full dogma propagation round (AGENTS.md, guides, agent files, skill files)

Phases B and C of #212 are deferred to a subsequent sprint.
