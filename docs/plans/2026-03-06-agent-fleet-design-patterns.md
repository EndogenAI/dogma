# Workplan: Agent Fleet Design Patterns

**Branch**: `feat/issue-2-formalize-workflows`
**Date**: 2026-03-06
**Orchestrator**: Executive Orchestrator
**Closes**: [#10 — [Research] Agent fleet design patterns](https://github.com/EndogenAI/Workflows/issues/10)

---

## Objective

Synthesize external literature and the EndogenAI fleet's own emerging patterns into a formal catalog of hierarchical agent fleet design patterns. Validate three design hypotheses from the issue comment (self-loop handoffs, prompt enrichment chain, quasi-encapsulated sub-fleets) against external evidence. Produce a D4 synthesis, then update `docs/guides/agents.md` and `.github/agents/README.md` with the pattern catalog and decision heuristics. Close issue #10.

**Pre-condition**: 11 relevant D3s already exist in `docs/research/sources/`. Scout is scoped to gap-filling only.

---

## Phase Plan

### Phase 1 — Scout (gap-fill only) ✅
**Agent**: Research Scout
**Deliverables**:
- D1 manifest of any sources NOT yet synthesized, particularly: A2A Agent Card schema spec, context window management at handoff boundaries, any hierarchical fleet pattern sources not covered by existing D3s
- Explicit confirmation which existing D3s are in scope for D4

**Depends on**: nothing
**Status**: ✅ Complete — 11 existing D3s confirmed in scope; 3 gap sources identified

---

### Phase 2 — Fetch gap D2s ✅
**Agent**: `scripts/fetch_source.py` (direct, per gap URL)
**Deliverables**:
- D2 cache files for any new sources identified by Scout
- Expected: 0–3 new sources

**Depends on**: Phase 1 (gap manifest)
**Status**: ✅ Complete — 3 new D2s fetched (Anthropic context engineering, multi-agent system, A2A spec)

---

### Phase 3 — D3 synthesis for new sources only ✅
**Agent**: Research Synthesizer (one per new D2)
**Deliverables**:
- D3 synthesis reports for any new sources in `docs/research/sources/`
- Existing D3s reused — no re-synthesis

**Depends on**: Phase 2
**Status**: ✅ Complete — 3 D3s committed at 9bc8b38

---

### Phase 4 — D4 aggregate synthesis ✅
**Agent**: Research Synthesizer
**Deliverables**:
- `docs/research/agent-fleet-design-patterns.md` — Status: Draft
- Required sections: Executive Summary, Hypothesis Validation (3 hypotheses), Pattern Catalog (named patterns with context/forces/solution/consequences), Framework Comparison, Decision Heuristics (when to create new agent vs. extend), Open Questions

**Depends on**: Phase 3
**Status**: ✅ Complete — 435 lines, all sections present

---

### Phase 5 — Review ✅
**Agent**: Research Reviewer
**Deliverables**:
- PASS / CONDITIONAL PASS / FAIL verdict
- Hypothesis validation defensibility check

**Depends on**: Phase 4
**Status**: ✅ Complete — CONDITIONAL PASS, NB-2 applied by Archivist

---

### Phase 6 — Archive + guide/README update ✅
**Agent**: Executive Docs (via Orchestrator)
**Deliverables**:
- `docs/research/agent-fleet-design-patterns.md` → Status: Final, committed
- `docs/guides/agents.md` updated with pattern catalog and specialist-vs-extend decision table
- `.github/agents/README.md` updated with pattern documentation
- Issue #10 closed with link

**Depends on**: Phase 5 (PASS verdict)
**Status**: ✅ Complete — committed b2cf341, issue #10 CLOSED

---

## Acceptance Criteria

- [x] D4 `docs/research/agent-fleet-design-patterns.md` committed with `Status: Final`
- [x] All 3 design hypotheses explicitly validated or contradicted with evidence
- [x] Named pattern catalog (≥ 4 patterns) present in D4 — 8 patterns
- [x] `docs/guides/agents.md` updated with specialist-vs-extend decision heuristics
- [x] `.github/agents/README.md` updated with pattern documentation
- [x] Issue #10 closed with link to committed D4
- [x] All changes pushed and PR #11 up to date
