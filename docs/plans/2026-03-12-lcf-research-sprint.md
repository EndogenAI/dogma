# Workplan: LCF Research Sprint — Issues #209, #210, #211

**Issues**: [#209](https://github.com/EndogenAI/dogma/issues/209), [#210](https://github.com/EndogenAI/dogma/issues/210), [#211](https://github.com/EndogenAI/dogma/issues/211)
**Branch**: `feat/issue-165-values-synthesis`
**Related PR**: #208 (open, awaiting review — sprint runs in parallel)
**Date Created**: 2026-03-12
**Orchestrator**: Executive Orchestrator

---

## Objective

Deliver three D4 research documents addressing: (1) a programmatic enforcement gate for the Local-Compute-First axiom, closing the F4 gap (#211, S effort, independent); (2) a shared vocabulary bridge for the vertical/horizontal encoding models (#210, M effort, independent); and (3) a reframing of MANIFESTO.md §3 as structural oversight infrastructure rather than cost fallback (#209, M effort, high priority, consumes #211 F4 output). Phases exploit parallelism between #211 and #210 in Phase 1, gate the MANIFESTO §3 amendment on explicit user approval, cross-link all three documents, then close all three issues via PR #208.

---

## Endogenous Sources (read before any delegation)

1. `docs/research/values-encoding.md` — F4 gap definition (primary for #211 and #209)
2. `docs/research/values-substrate-relationship.md` §2, §4.3 — bridge model context (primary for #210, #209)
3. `docs/research/bubble-clusters-substrate.md` — horizontal/topological model (primary for #210)
4. `MANIFESTO.md` §3 — Local-Compute-First axiom definition (primary for #209)
5. `scripts/validate_agent_files.py`, `scripts/capability_gate.py` — enforcement pattern reference (#211)
6. `docs/glossary.md` — candidate vocabulary bridge artifact (#210)
7. `.tmp/feat-issue-165-values-synthesis/<date>.md` — active scratchpad; read before delegating

---

## Execution Phases

### Phase 1A — Research Sprint: #211 LCF Programmatic Enforcement

**Agent**: Executive Researcher (→ Research Scout → Synthesizer)
**Effort**: S
**Depends on**: nothing
**Status**: ⬜ Not started

Scout and synthesize a D4 research document analysing signals for LCF violation detection, candidate enforcement surfaces, and tractability of a static gate `scripts/check_model_usage.py`. Explicitly assess whether #131 baseline telemetry data is required for tractability. Record the F4 gap characterisation note in the scratchpad for Phase 3 consumption.

**External sources**: Fowler & Humble *Continuous Delivery* (2010); DORA *Accelerate* (2018); NIST SP 800-218; Anthropic *Responsible Scaling Policy* (2023)
**Internal sources**: `docs/research/values-encoding.md` (F4 section); `scripts/validate_agent_files.py`; `scripts/capability_gate.py`; #131; #152

**Deliverables**:
- D1: `docs/research/lcf-programmatic-enforcement.md` (status: Final)
- D2: Design spec for `scripts/check_model_usage.py` embedded in D1 (interface, inputs, outputs, enforcement surface)
- D3: `## Phase 1A — F4 Gap Note` in scratchpad (verbatim gap characterisation for Phase 3)

**Gate**: D1 committed with `status: Final`; D3 written to scratchpad before Phase 3 starts

---

### Phase 1B — Research Sprint: #210 Vocabulary Bridge *(runs in parallel with Phase 1A)*

**Agent**: Executive Researcher (→ Research Scout → Synthesizer)
**Effort**: M
**Depends on**: nothing
**Status**: ⬜ Not started

Scout and synthesize a D4 research document proposing a minimal shared vocabulary bridging values-encoding.md's vertical/inheritance model and bubble-clusters-substrate.md's horizontal/topological model. Assess whether `docs/glossary.md` can serve as the bridge artifact. Stage ≥ 3 bridge-term definitions in the scratchpad; glossary edits are applied in Phase 6 to avoid cross-phase conflicts.

**External sources**: Lakoff & Johnson *Metaphors We Live By* (1980); Hofstadter *Fluid Concepts* (1995); Gentner "Structure-mapping" (1983); Sowa *Knowledge Representation* (2000)
**Internal sources**: `docs/research/values-substrate-relationship.md` §2; `docs/research/values-encoding.md`; `docs/research/bubble-clusters-substrate.md`; `docs/glossary.md`

**Deliverables**:
- D1: `docs/research/vocabulary-bridge-encoding-models.md` (status: Final)
- D2: `## Phase 1B — Bridge Terms` in scratchpad: ≥ 3 bridge-term definitions staged for `docs/glossary.md`

**Gate**: D1 committed with `status: Final`; ≥ 3 bridge terms recorded in scratchpad before Phase 2 starts

---

### Phase 2 — Review Gate: Phases 1A + 1B

**Agent**: Review
**Depends on**: Phase 1A (D1 committed), Phase 1B (D1 committed)
**Status**: ⬜ Not started

Validate both D4 documents against AGENTS.md constraints and D4 schema. Confirm `validate_synthesis.py` exits 0 on each. Issue a single verdict per document.

**Deliverables**:
- D1: Verdict for `docs/research/lcf-programmatic-enforcement.md` — APPROVED or REQUEST CHANGES
- D2: Verdict for `docs/research/vocabulary-bridge-encoding-models.md` — APPROVED or REQUEST CHANGES

**Gate**: Both verdicts recorded as APPROVED in scratchpad; any REQUEST CHANGES items resolved and re-reviewed before Phase 3 starts

---

### Phase 3 — Research Sprint: #209 LCF as Oversight Infrastructure

**Agent**: Executive Researcher (→ Research Scout → Synthesizer)
**Effort**: M
**Depends on**: Phase 1A (F4 gap note from D3); Phase 2 (both APPROVED verdicts)
**Status**: ⬜ Not started

Scout and synthesize a D4 research document arguing the enabling-infrastructure framing for MANIFESTO §3 with evidence from the listed external sources. Consume the Phase 1A F4 gap note directly. Produce an explicit Y/N assessment: is MANIFESTO §3 amendment warranted? Record the assessment and, if Y, the proposed amendment text in the scratchpad. Do not edit MANIFESTO.md — that is Phase 5's gate.

**External sources**: Ink & Switch "Local-First Software" (2019); NIST AI RMF (AI 100-1); EU AI Act Articles 9–17; Christiano et al. (2018); Shapiro & Varian *Information Rules* (1998)
**Internal sources**: `MANIFESTO.md` §3; `docs/research/values-encoding.md` (F4 gap); `docs/research/values-substrate-relationship.md` §4.3; #131; #152; Phase 1A scratchpad F4 note

**Deliverables**:
- D1: `docs/research/lcf-oversight-infrastructure.md` (status: Final)
- D2: `## Phase 3 — MANIFESTO §3 Assessment` in scratchpad: Y or N + rationale; if Y, proposed amendment text

**Gate**: D1 committed; D2 written to scratchpad with explicit Y/N verdict before Phase 4 starts

---

### Phase 4 — Review Gate: Phase 3

**Agent**: Review
**Depends on**: Phase 3 (D1 committed, D2 in scratchpad)
**Status**: ⬜ Not started

**Deliverables**:
- D1: Verdict for `docs/research/lcf-oversight-infrastructure.md` — APPROVED or REQUEST CHANGES

**Gate**: Verdict recorded as APPROVED in scratchpad; REQUEST CHANGES items resolved before Phase 5 starts

---

### Phase 5 — ⚠️ MANIFESTO §3 Amendment Gate — HARD STOP

**Agent**: Executive Orchestrator (surfaces to user; no autonomous edits)
**Depends on**: Phase 4 (APPROVED verdict); Phase 3 D2 (assessment in scratchpad)
**Status**: ⬜ Not started

Read `## Phase 3 — MANIFESTO §3 Assessment` from scratchpad. If assessment = **Y**: surface the proposed amendment text to the user verbatim and block all further execution until explicit written approval is received. Record `## MANIFESTO §3 Gate — APPROVED` (with user confirmation) or `## MANIFESTO §3 Gate — HOLD` (if N or if user declines) in scratchpad. Do not proceed to Phase 6 until this entry exists.

**Deliverables**:
- D1: Scratchpad entry: `## MANIFESTO §3 Gate — APPROVED` (with user confirmation cited) **or** `## MANIFESTO §3 Gate — HOLD`

**Gate**: One of the two gate entries present in scratchpad before Phase 6 starts. If APPROVED: MANIFESTO.md edit may be scoped into Phase 6. If HOLD: Phase 6 proceeds without MANIFESTO.md edits.

---

### Phase 6 — Cross-Linking

**Agent**: Executive Docs
**Depends on**: Phase 4 (all three docs APPROVED); Phase 5 (gate resolved)
**Status**: ⬜ Not started

Add inter-doc references across all three new research docs. Apply the ≥ 3 bridge terms staged in Phase 1B to `docs/glossary.md`. Back-reference the F4 gap closure in `docs/research/values-encoding.md` and add §2/§4.3 forward links in `docs/research/values-substrate-relationship.md`. If Phase 5 returned APPROVED, apply the MANIFESTO §3 amendment in this phase.

**Deliverables**:
- D1: Each of the three new docs cites the other two where relevant (committed)
- D2: `docs/glossary.md` updated with ≥ 3 bridge terms from Phase 1B
- D3: `docs/research/values-encoding.md` F4 section links to `lcf-programmatic-enforcement.md` and `lcf-oversight-infrastructure.md`
- D4: `docs/research/values-substrate-relationship.md` §2 and §4.3 link to the relevant new docs
- D5 (conditional): MANIFESTO.md §3 edited per Phase 5 APPROVED amendment (only if gate = APPROVED)

**Gate**: All deliverables committed; `git diff --name-only` confirms all target files changed; docs committed before Phase 7 starts

---

### Phase 7 — Sprint Wrapup

**Agent**: Executive Orchestrator (GitHub operations via GitHub agent)
**Depends on**: Phase 6 (all cross-linking committed)
**Status**: ⬜ Not started

Check `gh pr view 208` status first. If open: add `Closes #209`, `Closes #210`, `Closes #211` to PR body via `--body-file`. If merged: open a new PR from the branch with the same closes lines. Post session-end comments on #209, #210, #211. Update this workplan: mark all completed phases ✅ Complete. Write `## Session Summary` to scratchpad and run `uv run python scripts/prune_scratchpad.py --force`.

**Deliverables**:
- D1: PR #208 body (or new PR) contains `Closes #209`, `Closes #210`, `Closes #211`
- D2: Session-end comment posted on each of #209, #210, #211 with deliverable path and phase outcomes
- D3: This workplan file updated with final phase statuses
- D4: `## Session Summary` in scratchpad; `prune_scratchpad.py --force` run

**Gate**: `gh pr view 208 --json body -q '.body' | grep "Closes #209"` exits 0; `gh issue view 209/210/211` each show a new comment; workplan committed

---

## Parallelisation Notes

Phases 1A and 1B share no file paths and have no output dependencies — they may execute concurrently. The Executive Researcher should delegate both sprints simultaneously if context budget permits. Phase 2 (Review) may not start until **both** Phase 1A D1 and Phase 1B D1 are committed. All subsequent phases are strictly sequential.

---

## Open Questions

1. **#208 merge timing**: If PR #208 merges before Phase 7, open a new PR from the same branch. Check `gh pr view 208 --json state` at Phase 7 start before any PR body edits.
2. **#131 dependency (#211)**: If the `check_model_usage.py` design requires baseline telemetry data from #131, Phase 1A must record this as a blocking dependency in D3 and note it in the D1 design spec. Phase 1A scout must assess tractability without #131 data and record a verdict explicitly.
3. **MANIFESTO §3 gate timing**: Alert the user at Phase 3 completion that Phase 5 is a hard stop requiring a decision. Do not allow the sprint to stall silently at Phase 5.

---

## Acceptance Criteria

### #211 — LCF Programmatic Enforcement

- [ ] `docs/research/lcf-programmatic-enforcement.md` exists with `status: Final`
- [ ] `uv run python scripts/validate_synthesis.py docs/research/lcf-programmatic-enforcement.md` exits 0
- [ ] F4 gap characterisation present with explicit LCF violation signals described
- [ ] Design spec for `scripts/check_model_usage.py` present (interface, inputs, outputs, enforcement surface)
- [ ] #131 dependency assessed: tractability without baseline data explicitly stated

### #210 — Vocabulary Bridge

- [ ] `docs/research/vocabulary-bridge-encoding-models.md` exists with `status: Final`
- [ ] `uv run python scripts/validate_synthesis.py docs/research/vocabulary-bridge-encoding-models.md` exits 0
- [ ] ≥ 3 bridge terms proposed, covering both vertical (inheritance) and horizontal (topological) models
- [ ] ≥ 3 bridge terms added to `docs/glossary.md`
- [ ] Doc affirms or justifies `docs/glossary.md` as the bridge artifact

### #209 — LCF Oversight Infrastructure

- [ ] `docs/research/lcf-oversight-infrastructure.md` exists with `status: Final`
- [ ] `uv run python scripts/validate_synthesis.py docs/research/lcf-oversight-infrastructure.md` exits 0
- [ ] Enabling-infrastructure framing argued with evidence from ≥ 3 of the listed external sources
- [ ] MANIFESTO §3 amendment assessment is explicit: Y or N with rationale in scratchpad
- [ ] If Y: proposed amendment text exists and `## MANIFESTO §3 Gate — APPROVED` is in scratchpad (user confirmed)
- [ ] If N: `## MANIFESTO §3 Gate — HOLD` recorded in scratchpad

### Cross-Sprint

- [ ] All three new docs cross-reference each other appropriately
- [ ] `docs/research/values-encoding.md` F4 section links to both `lcf-programmatic-enforcement.md` and `lcf-oversight-infrastructure.md`
- [ ] `docs/research/values-substrate-relationship.md` §2 and §4.3 updated with forward links to relevant new docs
- [ ] PR #208 body (or successor PR) contains `Closes #209`, `Closes #210`, `Closes #211`
- [ ] Session-end comment posted on each of #209, #210, #211
