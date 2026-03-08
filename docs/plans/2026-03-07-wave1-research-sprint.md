# Workplan: Wave 1 Research Sprint — Async, LLM Tiers, Security

**Date**: 2026-03-07
**Branch**: main
**Slug**: wave1-research-sprint
**Status**: In Progress

---

## Objective

Execute Wave 1 of the pre-flight research sequence for issue #45 (Research: Product Definition). Three independent research items — async process handling (#7), LLM tier strategy (#8), and security threat modelling (#33) — are batched and delegated to the Executive Researcher fleet in a single session. All three are `effort:M` (except #33 which is scoped but unlabelled) and have no inter-dependencies.

---

## Acceptance Criteria

- [x] `docs/research/async-process-handling.md` — Status: Final, committed to main (3b679d0)
- [x] `docs/research/llm-tier-strategy.md` — Status: Final, committed to main (d13f9f2)
- [x] `docs/research/security-threat-model.md` — Status: Final, committed to main (81b552f)
- [x] Issue #7 closed
- [x] Issue #8 closed
- [x] Issue #33 closed (D1–D3 gate deliverables met)
- [x] Remediation issues filed per #33 D2: #49 (path traversal), #50 (SSRF), #51 (prompt injection)
- [x] `AGENTS.md` updated with async handling guidelines (#7 D2) and Security Guardrails section (#33 D3)
- [ ] Wave 1 completion comment posted on #45

---

## Phase Plan

### Phase 1 — Research: Async Process Handling (#7)

**Agent**: Executive Researcher (→ Research Scout → Synthesizer → Reviewer → Archivist)
**Deliverables**:
- `docs/research/async-process-handling.md`, Status: Final
- `AGENTS.md` updated with D2 async handling guidelines
- Issue #7 closed

**Depends on**: nothing
**Gate**: Phase 2 may start in parallel; no dependency

---

### Phase 2 — Research: Free and Low-Cost LLM Tier Strategy (#8)

**Agent**: Executive Researcher
**Deliverables**:
- `docs/research/llm-tier-strategy.md`, Status: Final
- Model selection decision table by task type
- Monthly token budget strategy
- Issue #8 closed

**Depends on**: nothing (can run in parallel with Phase 1)
**Gate**: Phase 3 may start in parallel; no dependency

---

### Phase 3 — Research: Security Threat Modelling (#33)

**Agent**: Executive Researcher
**Deliverables**:
- `docs/research/security-threat-model.md`, Status: Final
- Remediation issues filed (one per finding)
- `AGENTS.md` guardrail additions (secrets hygiene, prompt injection)
- Issue #33 closed

**Depends on**: nothing (can run in parallel with Phases 1 & 2)
**Gate**: All three phases must complete before Wave 1 is declared done

---

### Phase 4 — Commit & Verify

**Agent**: GitHub (commit) + Orchestrator (verify)
**Deliverables**: All three research docs committed, issues closed, #45 comment posted
**Depends on**: Phases 1–3 all complete

---

## Notes

- Phases 1–3 are parallelisable but will be executed sequentially in this session due to single-agent context
- Sequencing order: #7 → #8 → #33 (simplest → most complex)
- All research output lands in `docs/research/`; no code changes except `AGENTS.md` additions
- After all three complete, update #45 with Wave 1 completion comment
