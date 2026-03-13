# Workplan: Full Corpus Back-Propagation into Primary Papers

**Issues**: [#165](https://github.com/EndogenAI/dogma/issues/165), [#212](https://github.com/EndogenAI/dogma/issues/212), [#225](https://github.com/EndogenAI/dogma/issues/225), [#226](https://github.com/EndogenAI/dogma/issues/226), [#227](https://github.com/EndogenAI/dogma/issues/227)
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
**Status**: ✅ Complete — `docs/plans/2026-03-12-corpus-sweep-table.md` committed (3111a2d)

**Enhancement applied**: Added Doc Type / Synthesises / Status columns; generated programmatically via `scripts/generate_sweep_table.py` + `docs/plans/corpus-sweep-data.yml`; Phase 1 Scout strategy updated to read Synthesis docs first.

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
**Status**: ✅ Complete — APPROVED (2026-03-12)

**Check**: Sweep table covers all 72 docs (no omissions); relevance ratings are not uniformly L/None (would indicate under-reading); "Already cited" status is grounded in actual cross-reference checks against the three primary papers; scout-depth assignments are coherent with relevance+citation status.

**Deliverables**: APPROVED verdict in scratchpad

---

### Phase 1 — Corpus Scout (Raw Findings) [4 sequential groups, Orchestrator-mediated]

**Agents**: Executive Orchestrator (coordination) + 4× Research Scout (sequential: 1A → 1B → 1C → 1D)
**Effort**: L
**Depends on**: Phase 0 APPROVED
**Status**: ⬜ Not started

**Rationale for sequential, Orchestrator-mediated split**: 36 Thorough + 13 Skim docs is too large for a single Scout delegation without context loss. Splitting by doc type keeps each Scout's working set coherent and compact. Scouts run **sequentially** because later groups' observations should be framed by what earlier Scouts found — but the handoff is **always through the Orchestrator**, not Scout-to-Scout. Direct Scout-to-Scout handoff risks a telephone-game effect: lossy summarisation at each step drifts from the original intent. The Orchestrator is the integration point: it reads each Scout's output, distills a ≤200-token **guiding brief** highlighting what was already observed and what gaps remain, then delegates the next Scout with that brief as explicit context. The corpus does not collapse into a funnel; the Orchestrator preserves the full picture across the sequence.

**Reading order rationale**: Synthesis first (1A) establishes the highest-density signal layer; Bridge/Sprint (1B) shows how synthesis connects to constituent work; Enforcement/LCF (1C) covers the most operationally-dense raw research; remaining Thorough + Skim (1D) fills gaps. Each successive brief will narrow what the next Scout needs to flag (avoiding re-observation of already-captured signals).

**Orchestrator inter-scout brief format** (written to scratchpad before each delegation):
```
## Orchestrator Brief — Before Scout 1[X]
**Already observed** (≤5 bullets from prior output): ...
**Themes NOT yet seen** (gaps to watch for): ...
**Watch list for this group** (specific signals relevant to this doc type): ...
```

**Each Scout's task**: Read the Orchestrator's brief, then read its assigned docs (Thorough = full read; Skim = summary scan), then append its findings section to `docs/plans/2026-03-12-corpus-raw-findings.md`. Output format per doc: one section heading plus bullet observations. No proposal-level specificity (no target sections, no exact change descriptions — those are Phase 2).

---

#### Scout 1A — Synthesis Docs (7 Thorough)

**Receives**: Orchestrator brief summarising back-propagation goals and the three primary papers' current state (no prior Scout output yet — this is the opening pass).

**Doc list**:
- enforcement-tier-mapping.md
- external-values-decision-framework.md
- h4-peer-review-synthesis.md
- holographic-encoding-empirics.md
- laplace-pressure-empirical-validation.md
- methodology-synthesis.md
- values-enforcement-tier-mapping.md

**Output**: Section `## Scout 1A — Synthesis Docs` in `docs/plans/2026-03-12-corpus-raw-findings.md`

---

#### Scout 1B — Bridge/Integration + Sprint Docs (10 Thorough)

**Receives**: Orchestrator brief distilled from Scout 1A output — what themes the Synthesis layer already surfaced, and what signals to watch for in Bridge/Sprint material specifically.

**Doc list**:
- doc-interweb.md
- topological-audit-substrate.md
- value-provenance.md
- sprint-A-h1-novelty.md
- sprint-B-h2-morphogenetic.md
- sprint-C-h3-augmentive.md
- sprint-DE-h4-cs-lineage.md
- phase-5-recommendations-audit.md
- substrate-taxonomy-content-context.md
- workflow-formula-encoding-dsl.md

**Output**: Section `## Scout 1B — Bridge/Integration + Sprint Docs` in `docs/plans/2026-03-12-corpus-raw-findings.md`

---

#### Scout 1C — Enforcement/LCF/Query Raw Research (10 Thorough)

**Receives**: Orchestrator brief distilled from Scout 1A+1B output — cumulative theme map and gaps still unseen; watch list specific to enforcement, local-compute, and queryable-substrate material.

**Doc list**:
- programmatic-governors.md
- shell-preexec-governor.md
- llm-behavioral-testing.md
- context-amplification-calibration.md
- context-budget-balance.md
- queryable-substrate.md
- session-checkpoint-and-safeguard-patterns.md
- deterministic-agent-components.md
- multi-principal-deployment-scenarios.md
- six-layer-topological-extension.md

**Output**: Section `## Scout 1C — Enforcement/LCF/Query` in `docs/plans/2026-03-12-corpus-raw-findings.md`

---

#### Scout 1D — Remaining Thorough + All Skim (9 Thorough + 13 Skim)

**Receives**: Orchestrator brief distilled from Scout 1A+1B+1C output — full gap map; explicit list of signals not yet observed that are likely to appear in fleet/agent/context material.

**Doc list (Thorough)**:
- agent-skills-integration.md
- agent-taxonomy.md
- external-team-case-study.md
- filter-bubble-threshold-calibration.md
- fleet-emergence-operationalization.md
- holonomic-brain-theory-application.md
- local-copilot-models.md
- local-mcp-frameworks.md
- semantic-holography-language-encoding.md

**Doc list (Skim — summary scan only)**:
- agent-fleet-design-patterns.md
- agentic-research-flows.md
- aigne-afs-evaluation.md
- async-process-handling.md
- dev-workflow-automations.md
- endogenai-product-discovery.md
- episodic-memory-agents.md
- github-as-memory-substrate.md
- github-project-management.md
- iit-panpsychism-consciousness-bounds.md
- onboarding-wizard-patterns.md
- skills-as-decision-logic.md
- xml-agent-instruction-format.md

**Output**: Section `## Scout 1D — Remaining Thorough + Skim` in `docs/plans/2026-03-12-corpus-raw-findings.md`

---

**Orchestrator inter-scout steps** (between each delegation):
1. Read the completed Scout section in `docs/plans/2026-03-12-corpus-raw-findings.md`
2. Write `## Orchestrator Brief — Before Scout 1[X]` to the scratchpad (≤200 tokens; already-observed themes + unseen gaps + watch list for next group)
3. Commit completed Scout section before delegating next
4. Delegate next Scout with the brief as explicit context in the prompt

**Deliverables**:
- `docs/plans/2026-03-12-corpus-raw-findings.md` with all 4 Scout sections committed
- 3 Orchestrator briefs written to scratchpad (before 1B, 1C, 1D)

**Gate**: All 4 sections present; Phase 1 Review APPROVED

---

### Phase 1 Review — Review Gate

**Agent**: Review
**Depends on**: Phase 1 complete
**Status**: ⬜ Not started

**Check**: All 4 Scout sections present (1A/1B/1C/1D); all 36 Thorough-rated docs have a findings entry across the 4 sections; no Skim-rated doc is missing without explanation; observations are specific (not "this doc is relevant") and grounded in actual content read; no proposal-level specificity leaking in (target sections, exact change descriptions belong in Phase 2).

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

### Phase 4A — Docs Encoding: Issue #225 + #227 (workflows.md)

**Agent**: Executive Docs
**Effort**: M
**Depends on**: Phase 3 Review (user approval) — can be parallelised with Phase 3 at Orchestrator's discretion since target files differ
**Status**: ⬜ Not started
**Issues**: [#225](https://github.com/EndogenAI/dogma/issues/225), [#227](https://github.com/EndogenAI/dogma/issues/227)

**Task**: Apply both issues' changes to `docs/guides/workflows.md` in one pass:
- **#225**: Add doc-type taxonomy (Synthesis / Raw Research / Bridge / Operational) + programmatic sweep table pattern (YAML data file + generator script) + `--mark-read` status tracking CLI pattern to the org-sweep section
- **#227**: Add new back-propagation methodology subsection: weave/link/consolidate discipline, proposal-doc pattern (Scout → raw findings → Synthesizer → structured proposal → Docs → applied edits), and manual stop gate requirement for primary-paper edits

**Deliverables**:
- `docs/guides/workflows.md` updated and committed

**Gate**: Changes committed; Phase 4A Review (in shared Phase 4 Review gate) APPROVED

---

### Phase 4B — Docs Encoding: Issue #226 (AGENTS.md)

**Agent**: Executive Docs
**Effort**: S
**Depends on**: Phase 3 Review (user approval) — can be run in parallel with Phase 4A since different target file
**Status**: ⬜ Not started
**Issues**: [#226](https://github.com/EndogenAI/dogma/issues/226)

**Task**: Add explicit binary acceptance criteria requirement to `AGENTS.md` § Agent Communication → Review delegation guidance:
- Encode the lesson: generic "validate this" prompts produce generic reviews; explicit numbered pass/fail criteria per check item catch inconsistencies that are missed otherwise
- Add guidance with canonical example (first prompt = generic → missed 5 depth violations; second prompt = 7 numbered criteria = caught all 5)

**Deliverables**:
- `AGENTS.md` updated and committed

**Gate**: Changes committed; Phase 4 Review APPROVED

---

### Phase 4 Review — Review Gate

**Agent**: Review
**Depends on**: Phase 4A + Phase 4B both committed
**Status**: ⬜ Not started

**Check**:
1. `docs/guides/workflows.md` — doc-type taxonomy present in org-sweep section; back-prop methodology section present with weave/link/consolidate rules, proposal-doc pattern, and manual stop gate; no in-place definition reproduction (link-out discipline applies here too)
2. `AGENTS.md` — explicit binary acceptance criteria guidance present in Review delegation section with canonical counter-example (generic prompt vs. numbered criteria)
3. Both sections follow weave/link/consolidate discipline (no new isolated paragraphs appended without integration into surrounding context)

**Deliverables**: APPROVED verdict in scratchpad

---

## Acceptance Criteria

- [x] Sweep table covers all 72 docs
- [ ] Raw findings doc covers all Thorough/Skim-rated docs
- [ ] Proposal has entries grouped by target paper with exact section targets
- [ ] All proposal entries follow weave/link/consolidate discipline
- [ ] All three primary papers validate_synthesis PASS after edits
- [ ] User has reviewed and approved diffs before commit
- [ ] workflows.md updated with doc-type taxonomy + back-prop methodology section (#225, #227)
- [ ] AGENTS.md updated with explicit Review acceptance criteria guidance (#226)
- [ ] Phase 4 Review APPROVED
