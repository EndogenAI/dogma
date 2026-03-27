# Workplan: Fleet Governance + Research Foundations

**Sprint name**: Fleet Governance + Research Foundations
**Milestone**: 34 — "Backlog — Research & Secondary"
**Branch**: `sprint/fleet-governance-research-foundations`
**Date**: 2026-03-26
**Status**: Active — open for pick-up
**Governing axiom**: Endogenous-First — read `docs/research/` prior docs before each research phase
**Orchestrator**: Executive Orchestrator

---

## Objective

This sprint executes a coherent 12-issue cut from the 33-issue Milestone 34 backlog,
targeting three layered goals: (1) fleet housekeeping — correcting tool-count ceiling
violations, review-gate encoding, and scratchpad schema gaps; (2) research foundations —
agent fleet model diversity, multi-agent coordination patterns, and local model
practitioner testimonials; (3) implementation from research — L1/L2 guardrail encoding,
phase-gating scripts, and a 30-day values extraction template for companion-repo adoption.
Issues #413 and #414 are now unblocked (blocker #422 closed 2026-03-26).
Rate-limit-sensitive research delegations are batched in Phase 2 with an intentional
rest gap between sub-delegations. Phase 3 depends on Phase 2 Delegation A outputs.

---

## Phase Plan

### Phase 1 — Fleet Housekeeping ⬜
**Agent**: Executive Fleet + Executive Docs
**Issues**: #461, #349, #376, #343
**Deliverables**:
- Fix Miller's Law tool-count ceiling violations in the 4 executive-tier agents identified by `validate_agent_files.py` audit (#461)
- Standardise review gates with numbered acceptance criteria across agent files (#349)
- Add `## Audit Trail` section to session scratchpad schema (#376)
- Add `## Telemetry` section to session scratchpad schema (#343)
- All changes pass `uv run python scripts/validate_agent_files.py --all`

**Depends on**: nothing
**Rate-limit risk**: None — pure file edits
**CI**: Tests, Auto-validate, Lint
**Status**: Not started

### Phase 1 Review ⬜
**Agent**: Review
**Deliverables**: APPROVED verdict logged under `## Review Output` in scratchpad
**Depends on**: Phase 1 deliverables committed
**Status**: Not started

---

### Phase 2 — Research Sprint ⬜
**Agent**: Executive Researcher → Research Scout → Research Synthesizer
**Issues**: #413, #414, #311, #426
**Deliverables**:
- **Delegation A** (#413 + #414 — same domain, one Scout pass):
  - `docs/research/agent-fleet-model-diversity.md` (Status: Final) covering agent fleet model diversity (#413)
  - Multi-agent coordination patterns findings incorporated (#414) — may be same doc or companion doc
- **Rate-limit rest gap**: 15–20 min between Delegation A and B (or end-of-session boundary)
- **Delegation B** (#311 + #426 — lighter secondary research):
  - Distilled findings from local model substitution practitioner testimonials added to relevant existing docs (#311)
  - Long-running Claude for scientific computing findings cached and noted (#426) — Scout-only, no full synthesis required

**Depends on**: Phase 1 Review APPROVED
**Rate-limit risk**: HIGH — Scout + Synthesizer each consume budget; batch deliberately
**CI**: Tests, Auto-validate, Lint
**Status**: Not started

### Phase 2 Review ⬜
**Agent**: Review
**Deliverables**: APPROVED verdict logged under `## Review Output` in scratchpad
**Depends on**: Phase 2 deliverables committed
**Status**: Not started

---

### Phase 3 — Implementation from Research ⬜
**Agent**: Executive Docs + Executive Scripter
**Issues**: #379, #337, #338, #344
**Deliverables**:
- 30-day values extraction template for pre-AI-adoption gate — `docs/guides/values-extraction-template.md` or equivalent (#379, priority:high)
- L1 semantic output validation guardrail — implementation informed by #413/#414 research outputs (#337)
- L2 constraints as schema-validated YAML — pairs with #337 (#338)
- Phase-gating orchestration logic encoded into scripts — Programmatic-First encoding of interactive patterns (#344)
- All new scripts have corresponding `tests/test_*.py` at ≥80% coverage

**Depends on**: Phase 2 Delegation A outputs committed (Phase 2 Review APPROVED)
**Rate-limit risk**: Low — file edits + scripting
**CI**: Tests, Auto-validate, Lint
**Status**: Not started

### Phase 3 Review ⬜
**Agent**: Review
**Deliverables**: APPROVED verdict logged under `## Review Output` in scratchpad
**Depends on**: Phase 3 deliverables committed
**Status**: Not started

---

### Phase 4 — Session Close ⬜
**Agent**: GitHub
**Deliverables**:
- All changes pushed to `sprint/fleet-governance-research-foundations`
- PR opened with `Closes #461, #349, #376, #343, #413, #414, #311, #426, #379, #337, #338, #344` in body
- Fleet integration check run: `uv run python scripts/check_fleet_integration.py --dry-run`
- Session scratchpad archived; `## Session Summary` written

**Depends on**: Phase 3 Review APPROVED
**CI**: Tests, Auto-validate, Lint
**Status**: Not started

---

## Acceptance Criteria

- [ ] #461 — Miller's Law violations fixed; validate_agent_files.py passes
- [ ] #349 — Review gate acceptance criteria standardised across agent files
- [ ] #376 — `## Audit Trail` section added to scratchpad schema
- [ ] #343 — `## Telemetry` section added to scratchpad schema
- [ ] #413 — Agent fleet model diversity research doc committed (Status: Final)
- [ ] #414 — Multi-agent coordination patterns findings committed
- [ ] #311 — Local model substitution practitioner testimonials distilled and linked
- [ ] #426 — Long-running Claude / scientific computing Scout findings cached
- [ ] #379 — 30-day values extraction template committed (priority:high)
- [ ] #337 — L1 semantic output validation implemented
- [ ] #338 — L2 constraints as schema-validated YAML implemented
- [ ] #344 — Phase-gating orchestration logic encoded as scripts
- [ ] All new scripts have tests at ≥80% coverage
- [ ] All changes pushed; PR open on sprint/fleet-governance-research-foundations
- [ ] CI passing (Tests, Auto-validate, Lint)

## PR Description Template

<!-- Copy to PR description when opening the PR -->

Closes #461, Closes #349, Closes #376, Closes #343, Closes #413, Closes #414, Closes #311, Closes #426, Closes #379, Closes #337, Closes #338, Closes #344

---

## Deferred to Next Sprint

| Issue | Reason |
|-------|--------|
| #333, #336 | Complex platform work (multi-provider inference, MCP refactor) — own sprint |
| #394 | Adoption agent — complex; needs #379 template first |
| #432 | PR review skill — medium complexity, no urgency |
| #399 | Upstream proposal — needs stakeholder discussion |
| #380 | Cross-domain conflict detection — no current blocker |
| #352–#355 | RAG follow-ups — batch into dedicated RAG maintenance sprint |
| #113, #128, #131 | Deferred/blocked |
| #415, #419, #234, #283 | Low-priority research, no immediate downstream implementations |

---

## Rate-Limit Timing Notes

| Gap | Recommendation |
|-----|----------------|
| Phase 1 → Phase 2 | Minimal — just commit + Review gate |
| Phase 2 Delegation A → Delegation B | Intentional rest: 15–20 min OR end-of-session boundary |
| Phase 2 → Phase 3 | Natural gap from Review gate + workplan write is sufficient |
