# Workplan: Sprint 18A/18B — Research Sprint & Implementation Consolidation

**Date**: 2026-03-17  
**Branch**: `feat/sprint-18-research-consolidation`  
**Milestones**: [Sprint 18A — Research Sprint](https://github.com/EndogenAI/dogma/milestone/18) + [Sprint 18B — Implementation Consolidation](https://github.com/EndogenAI/dogma/milestone/19)  
**Orchestrator**: Executive Orchestrator

---

## Objective

Sprints 18A/18B form a coherent two-phase delivery cycle bridging research (9 cross-disciplinary topics) to implementation consolidation (1 carry-over docs item + rate-limit resilience foundation). The unifying throughline is **operational sustainability**: researching real-world governance patterns, observability constraints, and vendor lock-in risks while simultaneously executing the critical rate-limit resilience debt from Sprint 17, enabling multi-phase sessions without token exhaustion.

**Sprint Capacity**: 18A = 15 effort units (9 R issues); 18B = reactive consolidation + rate-limit foundation  
**Timeline**: 18A research phases parallel (3 per delegation) → Review gate → 18B implementation

---

## Phase Plan

### Phase 0 — Rate-Limit Resilience Foundation (CRITICAL GATE)

**Agent**: Executive Scripter + Executive Docs  
**Issues**: #322, #323, #324, #325  
**Scope**:
- #322: Fix strict sleep cap/floor conflict in `scripts/detect_rate_limit.py`
- #323: Implement provider-aware rate-limit policy profiles (Claude/GPT)
- #324: Implement adaptive escalation + circuit-breaker for repeated failures
- #325: Enforce pre-delegation rate-limit gate with audit logging

**Deliverables**:
- `scripts/detect_rate_limit.py` — revised with corrected sleep logic + provider profiles
- `scripts/rate_limit_config.py` — policy profile engine (Claude, GPT, multi-provider)
- `scripts/rate_limit_gate.py` — pre-delegation budget check + circuit-breaker
- `data/rate-limit-profiles.yml` — provider policy definitions
- `tests/test_rate_limit_*.py` — full test suite (≥80% coverage)
- `.github/skills/rate-limit-resilience/SKILL.md` — documented workflow for other agents
- Update to `AGENTS.md` — rate-limit gate section in Orchestrator constraints
- Update to `phase-gate-sequence` skill — integrate budget alert logic

**Depends on**: Nothing (blocking gate)  
**Gate**: Phase 0 Review APPROVED before any Phase 1 begins  
**Status**: ⬜ Not started  
**Critical Note**: All subsequent phases depend on Phase 0 completion. No Phase 1/3 delegation until Phase 0 Review returns APPROVED.

---

### Phase 0 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 0 Review Output` in scratchpad, verdict: APPROVED  
**Depends on**: Phase 0 committed  
**Gate**: Phase 1A/1B/1C do not begin until APPROVED  
**Status**: ⬜ Not started

---

### Phase 1A — Research: Issues #319, #318, #317

**Agent**: Executive Researcher → Research Scout fleet  
**Issues**: #319 (LLM strategic advice quality), #318 (AI autonomy governance), #317 (AI platform lock-in risks)  
**Scope**: 3 independent research questions; strategy & governance focus  
**Deliverables**: 3 D4 research docs (Status: Final) committed to `docs/research/`  
**Depends on**: Phase 0 Review APPROVED  
**Gate**: Phase 1 Review does not start until all 3 docs committed  
**Parallel**: Can run in parallel with Phase 1B/1C (independent topics)  
**Status**: ⬜ Not started

---

### Phase 1B — Research: Issues #316, #315, #314

**Agent**: Executive Researcher → Research Scout fleet  
**Issues**: #316 (AI workload observability), #315 (AI cognitive load), #314 (GitHub Copilot ecosystem)  
**Scope**: 3 independent research questions; infrastructure & tooling focus  
**Deliverables**: 3 D4 research docs (Status: Final) committed to `docs/research/`  
**Depends on**: Phase 0 Review APPROVED  
**Gate**: Phase 1 Review does not start until all 3 docs committed  
**Parallel**: Can run in parallel with Phase 1A/1C (independent topics)  
**Status**: ⬜ Not started

---

### Phase 1C — Research: Issues #313, #312, #294

**Agent**: Executive Researcher → Research Scout fleet  
**Issues**: #313 (NeMo Guardrails), #312 (Copilot collaboration effects), #294 (Local RAG adoption)  
**Scope**: 3 independent research questions; guardrails, patterns & local compute focus  
**Deliverables**: 3 D4 research docs (Status: Final) committed to `docs/research/`  
**Depends on**: Phase 0 Review APPROVED  
**Potential Cross-Cutting**: #294 (Local RAG) findings may inform implementation patterns for Phase 3  
**Gate**: Phase 1 Review does not start until all 3 docs committed  
**Parallel**: Can run in parallel with Phase 1A/1B (independent topics)  
**Status**: ⬜ Not started

---

### Phase 1 Review — Research Review Gate (MANDATORY)

**Agent**: Review  
**Deliverables**: `## Phase 1 Review Output` in scratchpad, verdict: APPROVED (all 9 research docs validated)  
**Validation Checklist**:
1. All 9 D4 docs present in `docs/research/` with Status: Final
2. Each doc has at least 2 canonical examples in Pattern Catalog
3. Each doc cites MANIFESTO.md axioms (≥2 citations per doc)
4. Cross-cutting findings (if any from #332–334) documented in dedicated section
5. All Recommendations sections link to actionable GitHub issues or marked "intentionally deferred"

**Depends on**: All Phase 1A/1B/1C deliverables committed  
**Gate**: Phase 3 (implementation) does NOT begin until this gate returns APPROVED  
**Critical Rule**: Research-First axiom — no implementation proceeds until research is reviewed  
**Status**: ⬜ Not started

---

### Phase 2 (Carry-Over) — Sprint 18B Documentation (#310)

**Agent**: Executive Docs  
**Issue**: #310 (Hook configuration management — CLAUDE.md vs VS Code settings patterns)  
**Scope**: Document CLAUDE.md vs settings.json patterns for Claude Code hook adoption  
**Deliverables**: `docs/guides/claude-code-hooks.md` or `docs/guides/hook-configuration.md`  
**Depends on**: Nothing (can run in parallel with Phase 1 research)  
**Gate**: Phase 2 Review validates doc quality against reading-level targets  
**Status**: ⬜ Not started  
**Note**: This is a light carry-over item; can start immediately or defer to after Phase 1 Review  

---

### Phase 2 Review — Docs Review Gate

**Agent**: Review  
**Deliverables**: Verdict: APPROVED  
**Depends on**: Phase 2 deliverables committed  
**Status**: ⬜ Not started

---

### Phase 3A — Integration & Rate-Limit Gate Injection

**Agent**: Executive Orchestrator + Executive Docs + Executive Fleet  
**Scope**:
- Weave Phase 1 research findings into `AGENTS.md`, `.github/agents/`, `.github/skills/`
- Inject rate-limit gate checks into `executive-orchestrator.agent.md` (from Phase 0)
- Update `phase-gate-sequence` skill to reference new rate-limit budget logic
- Cross-reference new rate-limit SKILL.md in onboarding guides

**Deliverables**:
- `AGENTS.md` — rate-limit gate section added + research findings woven (e.g., vendor lock-in patterns → agent design)
- `.github/agents/executive-orchestrator.agent.md` — pre-delegation budget check section
- `.github/skills/phase-gate-sequence/SKILL.md` — rate-limit alert integration
- `docs/guides/session-management.md` — rate-limit patterns for next-session handoff
- Updated cross-references in `docs/guides/workflows.md`

**Depends on**: Phase 1 Review APPROVED + Phase 0 Review APPROVED + Phase 2 Review APPROVED  
**Gate**: Phase 3A Review validates all integration points  
**Status**: ⬜ Not started

---

### Phase 3A Review — Integration Review Gate

**Agent**: Review  
**Deliverables**: Verdict: APPROVED  
**Validation**: All new rate-limit guidance woven into AGENTS.md without contradictions  
**Depends on**: Phase 3A deliverables committed  
**Status**: ⬜ Not started

---

### Phase 4 — Sprint Close & Release

**Agent**: GitHub Agent  
**Deliverables**:
- All phases committed to `feat/sprint-18-research-consolidation`
- PR opened: "feat(sprint-18): research sprint + rate-limit resilience foundation"
- PR body contains `Closes #322, Closes #323, Closes #324, Closes #325, Closes #310, Closes #326–#334`
- Release notes drafted
- Tag v0.11.0 (incremental after v0.10.0)

**Depends on**: Phase 3A Review APPROVED  
**Status**: ⬜ Not started

---

## Acceptance Criteria

- [ ] Phase 0 Review: APPROVED (rate-limit resilience gates all downstream)
- [ ] Phase 1 Review: APPROVED (all 9 research docs validated — #319, #318, #317, #316, #315, #314, #313, #312, #294)
- [ ] Phase 2 Review: APPROVED (hooks documentation validated)
- [ ] Phase 3A Review: APPROVED (integration points validated)
- [ ] All 14 sprint issues marked closed (#319–#313, #312, #294, #310 + #322–#325)
- [ ] PR #X merged
- [ ] v0.11.0 tagged and released

---

## Parallel Execution Strategy

**Phase 1 (Research)**: All three sub-phases (1A/1B/1C) can execute in parallel because:
- Topics are independent (no cross-phase dependencies among #319, #318, #317, #316, #315, #314, #313, #312, #294)
- Each delegation to Executive Researcher is isolated (different URL/topic)
- Review gate (Phase 1 Review) aggregates all 9 findings before Phase 3 begins

**Execution Recommendation**: Delegate Phase 1A (#319–#317), 1B (#316–#314), 1C (#313–#312, #294) simultaneously after Phase 0 Review APPROVED, with 30s sleeps between delegations to avoid rate-limit acceleration.

---

## Rate-Limit Resilience Debt Mapping

All four follow-up items from Sprint 17 are now scheduled:

| Issue | Sprint 18 Phase | Closure Target |
|-------|-----------------|----------------|
| #322 | Phase 0 (implementation) | Closes via Phase 4 PR |
| #323 | Phase 0 (implementation) | Closes via Phase 4 PR |
| #324 | Phase 0 (implementation) | Closes via Phase 4 PR |
| #325 | Phase 0 (implementation) | Closes via Phase 4 PR |

---

## Next Sprint Follow-Ups (Sprint 18B Continuations)

- [ ] #335 — Implement local compute inference wrapper (Ollama integration) — gated by #334 (Local RAG research)
- [ ] #336 — Extended research capacity for MCP framework evolution
- [ ] #337 — Agent ecosystem maturity assessment (post-#329 governance research)

---

## Notes

- **Research-First Axiom**: Phase 1 research is MANDATORY before Phase 3 implementation. No exceptions.
- **Rate-Limit Criticality**: Phase 0 must complete before any Phase 1/3 delegation. Single gatekeeping point ensures all sessions inherit rate-limit protections.
- **Parallel Research Execution**: Phase 1A/1B/1C can run in parallel given independent topics; use 30s sleeps between delegations.
- **Integration Feedback Loop**: Phase 3A weaves Phase 1 insights back into substrate (AGENTS.md, skills, guides), completing the Research-First → Implementation cycle.
