# Workplan: Pre-45 Unblock Sprint

**Date**: 2026-03-07
**Branch**: feat/pre-45-unblock-sprint
**Slug**: pre-45-unblock-sprint
**Status**: Complete

---

## Objective

Complete all 7 items identified as prerequisites for unblocking issue #45 (Research: Product Definition). After completion, reassess deferred items to determine if any should be pulled forward before #45 is unblocked.

---

## Acceptance Criteria

### Wave A — Security Fixes
- [x] `#49` path traversal fixed in `fetch_source.py` — closed
- [x] `#50` SSRF fixed in `fetch_source.py` — closed
- [x] `#51` prompt injection guardrails added in `AGENTS.md` and `fetch_source.py` — closed
- [x] Tests cover all three security fixes

### Wave B — Dogma Hardening
- [x] `#53` `MANIFESTO.md` hermeneutics section added
- [x] `#53` [4,1] repetition code complete for all three core axioms
- [x] Issue #53 closed

### Wave C — Required Research
- [x] `#5` `docs/research/local-copilot-models.md` — Status: Draft, committed
- [x] Issue #5 closed
- [x] `#6` `docs/research/local-mcp-frameworks.md` — Status: Draft, committed
- [x] Issue #6 closed
- [x] `#47` `docs/research/onboarding-wizard-patterns.md` — Status: Draft, committed
- [x] Issue #47 closed

### Post-Sprint
- [x] Deferred items (#52, #54, #55, #41–#44, #48) reassessed
- [x] Issues #55 and #52 pulled into sprint
- [x] Issue #55 closed (session-start encoding checkpoint)
- [x] Issue #52 closed (`validate_agent_files.py`)
- [x] Implementation issues #56 and #57 created (gated on #45)
- [x] PR #58 opened against main

---

## Phase Plan

### Phase 1 — Wave A: Security Fixes (#49, #50, #51)

**Agent**: Orchestrator direct (well-scoped code fixes, no external research needed)
**Deliverables**: `scripts/fetch_source.py` hardened, `AGENTS.md` prompt-injection guardrails, tests updated, issues #49–#51 closed
**Depends on**: nothing
**Gate**: Phase 2 starts after Phase 1 committed and tests pass

---

### Phase 2 — Wave B: MANIFESTO Hermeneutics (#53)

**Agent**: Executive Docs
**Deliverables**: `MANIFESTO.md` hermeneutics section + [4,1] completion, issue #53 closed
**Depends on**: Phase 1 complete (no hard dependency, but clean branches first)
**Gate**: Phase 3 starts after Phase 2 committed

---

### Phase 3 — Wave C Research: Local Copilot Models (#5)

**Agent**: Executive Researcher
**Deliverables**: `docs/research/local-copilot-models.md` (Final), issue #5 closed
**Depends on**: nothing (can run after Phase 2)
**Gate**: Phase 4 starts after Phase 3 committed

---

### Phase 4 — Wave C Research: Local MCP Frameworks (#6)

**Agent**: Executive Researcher
**Deliverables**: `docs/research/local-mcp-frameworks.md` (Final), issue #6 closed
**Depends on**: nothing (can run after Phase 3)
**Gate**: Phase 5 starts after Phase 4 committed

---

### Phase 5 — Wave C Research: Onboarding Wizard (#47)

**Agent**: Executive Researcher
**Deliverables**: `docs/research/onboarding-wizard-patterns.md` (Final), issue #47 closed
**Depends on**: Phases 3 & 4 (benefits from local compute research context)
**Gate**: Post-sprint reassessment after Phase 5

---

### Phase 6 — Deferred Items Reassessment

**Agent**: Orchestrator direct
**Deliverables**: Decision documented in scratchpad, #45 label status updated if appropriate
**Depends on**: Phases 1–5 all complete

---

### Phase 7 — PR Open

**Agent**: Orchestrator direct
**Deliverables**: PR opened against main, CI passing
**Depends on**: Phase 6

---

## Notes

- Security fixes (Wave A) should be done directly — they are straightforward code patches, no ambiguity
- Run compact between Wave B and Wave C (research phases are token-heavy)
- All commits go to `feat/pre-45-unblock-sprint` — squash/rebase merge to main at end
