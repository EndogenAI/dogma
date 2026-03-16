# Workplan: Research Sprint — Intelligence & Architecture (Sprint 12)

**Branch**: `main`
**Date**: 2026-03-15
**Orchestrator**: Executive Orchestrator

---

## Objective

This sprint sequences 16 open research issues across the Intelligence & Architecture milestone into four dependency-ordered waves. Wave 1 establishes architecture vocabulary (MCP state, service module boundaries, substrate taxonomy) that all later waves depend on. Wave 2 builds on that foundation to explore local inference/RAG, platform agnosticism, and greenfield repo candidates. Wave 3 addresses emergent communication and evolution concerns that require substrate and platform clarity first. Wave 4 closes with content engineering and assessment tooling that can only be specified once the architecture is stable. A final synthesis phase integrates cross-cutting findings from all 16 issues into a single architecture recommendation document. Each wave is followed by a Review gate that must return APPROVED before the next wave begins.

---

## Phase Plan

### Phase 1 — Wave 1 Research ✅
**Agent**: Executive Researcher
**Issues**: #264, #265, #268
**Deliverables**:
- `docs/research/mcp-state-architecture.md` (Status: Final, committed) — closes #264
- `docs/research/custom-agent-service-modules.md` (Status: Final, committed) — closes #265
- `docs/research/substrate-atlas.md` (Status: Final, committed) — closes #268
**Depends on**: nothing
**Gate**: Wave 1 Review Gate does not start until all Wave 1 deliverables committed
**Status**: ✅ Complete — commits 9fa06cf, e0a2885, 8af8ac0 (+ fixes 4da838b, d38d291)

---

### Phase 2 — Wave 1 Review Gate ✅
**Agent**: Review
**Deliverables**: `## Wave 1 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 1 deliverables committed
**Gate**: Wave 2 does not start until APPROVED
**Status**: ✅ Complete — APPROVED (2026-03-15)

---

### Phase 3 — Wave 2 Research ✅
**Agent**: Executive Researcher
**Issues**: #269, #270, #271
**Deliverables**:
- `docs/research/local-inference-rag.md` (Status: Final, committed) — closes #269
- `docs/research/platform-agnosticism.md` (Status: Final, committed) — closes #270
- `docs/research/greenfield-repo-candidates.md` (Status: Final, committed) — closes #271
**Depends on**: Wave 1 Review Gate APPROVED
**Gate**: Wave 2 Review Gate does not start until all Wave 2 deliverables committed
**Status**: ✅ Complete — commits a02b24d, f6a6740, 99d634a

---

### Phase 4 — Wave 2 Review Gate ✅
**Agent**: Review
**Deliverables**: `## Wave 2 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 3 deliverables committed
**Gate**: Wave 3 does not start until APPROVED
**Status**: ✅ Complete — APPROVED (2026-03-15)

---

### Phase 5 — Wave 3 Research ✅
**Agent**: Executive Researcher
**Issues**: #272, #273, #277
**Deliverables**:
- `docs/research/agent-to-agent-communication-protocol.md` (Status: Final, committed) — closes #272 — `b240a9e`
- `docs/research/biological-evolution-dogma-propagation.md` (Status: Final, committed) — closes #273 — `01a1c95`
- `docs/research/semantic-encoding-modes-contextual-routing.md` (Status: Final, committed) — closes #277 — `a4401bf`
**Depends on**: Wave 2 Review Gate APPROVED ✅
**Gate**: Wave 3 Review Gate does not start until all Wave 3 deliverables committed
**Status**: ✅ Complete

---

### Phase 6 — Wave 3 Review Gate ✅
**Agent**: Review
**Deliverables**: `## Wave 3 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 5 deliverables committed ✅
**Gate**: Wave 4 does not start until APPROVED
**Status**: ✅ Complete — APPROVED (2026-03-15)

---

### Phase 7 — Wave 4 Research ✅
**Agent**: Executive Researcher
**Issues**: #266, #267, #274, #275, #276, #230, #232
**Deliverables**:
- `docs/research/classic-programmatic-patterns-dogma-legibility.md` (Status: Final, committed) — closes #266
- `docs/research/glossary-maintenance-strategy.md` (Status: Final, committed) — closes #267
- `docs/research/reading-level-assessment-framework.md` (Status: Final, committed) — closes #274
- `docs/research/programmatic-writing-assessment-tooling.md` (Status: Final, committed) — closes #275
- `docs/research/high-reading-level-encoding-drift-signal.md` (Status: Final, committed) — closes #276
- `docs/research/output-format-constraint-compressed-returns.md` (Status: Final, committed) — closes #230
- `docs/research/h2-nk-model-formalization.md` (Status: Final, committed) — closes #232
**Depends on**: Wave 3 Review Gate APPROVED ✅
**Gate**: Wave 4 Review Gate does not start until all Wave 4 deliverables committed
**Status**: ✅ Complete

**Acceptance criteria**:
- [x] All 7 D4 docs committed with `status: Final`
- [x] All 7 pass `uv run python scripts/validate_synthesis.py`
- [x] All 7 commits on `feat/sprint-12-intelligence-architecture`

---

### Phase 8 — Wave 4 Review Gate ✅
**Agent**: Review
**Deliverables**: `## Wave 4 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 7 deliverables committed ✅
**Gate**: Phase 9 does not start until APPROVED
**Status**: ✅ Complete

**Acceptance criteria**:
- [x] Review APPROVED verdict recorded under `## Wave 4 Review Output` in scratchpad
- [x] All 7 criteria passed for all 7 files

---

### Phase 9 — Synthesis & Architecture Recommendation ⬜
**Agent**: Executive Researcher
**Issues**: all 16 (cross-cutting synthesis)
**Deliverables**:
- `docs/research/intelligence-architecture-synthesis.md` (Status: Final, committed) — integrates findings across all 16 issues into a single architecture recommendation
**Depends on**: Wave 4 Review Gate APPROVED
**Gate**: Sprint is not closed until synthesis doc committed and pushed
**Status**: ⬜ Not started

---

## Acceptance Criteria

- [x] #264 — `docs/research/mcp-state-architecture.md` committed (Status: Final)
- [x] #265 — `docs/research/custom-agent-service-modules.md` committed (Status: Final)
- [x] #268 — `docs/research/substrate-atlas.md` committed (Status: Final)
- [x] Wave 1 Review Gate APPROVED recorded in scratchpad
- [x] #269 — `docs/research/local-inference-rag.md` committed (Status: Final)
- [x] #270 — `docs/research/platform-agnosticism.md` committed (Status: Final)
- [x] #271 — `docs/research/greenfield-repo-candidates.md` committed (Status: Final)
- [x] Wave 2 Review Gate APPROVED recorded in scratchpad
- [x] #272 — `docs/research/agent-to-agent-communication-protocol.md` committed (Status: Final)
- [x] #273 — `docs/research/biological-evolution-dogma-propagation.md` committed (Status: Final)
- [x] #277 — `docs/research/semantic-encoding-modes-contextual-routing.md` committed (Status: Final)
- [x] Wave 3 Review Gate APPROVED recorded in scratchpad
- [x] #266 — `docs/research/classic-programmatic-patterns-dogma-legibility.md` committed (Status: Final)
- [x] #267 — `docs/research/glossary-maintenance-strategy.md` committed (Status: Final)
- [x] #274 — `docs/research/reading-level-assessment-framework.md` committed (Status: Final)
- [x] #275 — `docs/research/programmatic-writing-assessment-tooling.md` committed (Status: Final)
- [x] #276 — `docs/research/high-reading-level-encoding-drift-signal.md` committed (Status: Final)
- [x] #230 — `docs/research/output-format-constraint-compressed-returns.md` committed (Status: Final)
- [x] #232 — `docs/research/h2-nk-model-formalization.md` committed (Status: Final)
- [x] Wave 4 Review Gate APPROVED recorded in scratchpad
- [ ] `docs/research/intelligence-architecture-synthesis.md` committed (Status: Final)
