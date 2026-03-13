---
title: "Sprint — Dogma Update: Backprop Propagation, GitHub Automation, Substrate Rebalancing"
sprint: "2026-03-13-dogma-update"
branch: "feat/sprint-2026-03-13-dogma-update"
generated: "2026-03-13"
issues: ["#212", "#221", "#239", "#240", "#243"]
---

# Sprint — Dogma Update (2026-03-13)

## Objective

Following the completion of the corpus back-propagation sprint (PR #208), this sprint propagates the encoded knowledge outward through the full dogma stack, automates GitHub substrate interactions, rebalances the content distribution across substrate layers, consolidates dogma bloat, and closes with a provenance/interlinking cleanup pass.

This is an **exploratory, multi-session sprint**. Preserve all scratchpad context for retrospectives.

> **⚠️ DO NOT PRUNE** — Multi-session sprint. Preserve all phase outputs. Run `prune_scratchpad.py` (no `--force`) only if > 2000 lines. Full `--force` prune at sprint close only, after retrospective is complete.

---

## Sprint Map

The five work streams below have a recommended sequencing, but some can run partially in parallel:

| Stream | Issue(s) | Dependency | Session |
|--------|----------|-----------|---------|
| A — GitHub Automation | #221 + sub-issues | None (independent) | Session 1–2 |
| B — Dogma Propagation | #212 Phase B+C | PR #208 merged ✅ | Session 1–2 |
| C — Substrate Rebalancing | #239 | Stream B complete | Session 2–3 |
| D — Substrate Consolidation | #240 | Stream C complete | Session 3–4 |
| E — Provenance & Interlinking | #243 | Stream D complete | Session 4–5 |

---

## Phase Plan

### Phase 0 — Sprint Setup (Session 1)

**Agent**: Executive Orchestrator (direct)
**Deliverables**:
- [x] Sprint branch created: `feat/sprint-2026-03-13-dogma-update`
- [x] Scratchpad initialized: `.tmp/feat-sprint-2026-03-13-dogma-update/2026-03-13.md`
- [x] Workplan committed: `docs/plans/2026-03-13-sprint-dogma-update.md`
- [x] Any missing tracking issues created (provenance/interlinking → #243)
- [x] Executive Planner consulted for per-phase checklists (output in scratchpad `## Phase 0 Output`)

**Depends on**: Nothing
**Status**: ✅ Complete

---

### Phase 1A — GitHub Automation Research & Implementation (#221)

**Agent**: Executive Researcher → Research Scout → Executive Scripter
**Deliverables**:
- [ ] Sub-issues #213–#220 triaged and ordered for execution
- [ ] `scripts/export_project_state.py` implemented and tested (#218 gap-filler)
- [ ] GitHub Actions CI workflows drafted for #214, #215, #216, #217
- [ ] `data/labels.yml` governance enforced via CI (#215)
- [ ] CHANGELOG automation wired (#216, #217)
- [ ] Issue corpus snapshot mechanism implemented (#213)
- [ ] AGENTS.md updated: orient-step references local cached artifacts before API calls
- [ ] Fleet/skills updated to use new tooling

**Depends on**: Phase 0 complete
**Gate**: Phase 1A Review does not start until all deliverables committed
**Status**: ✅ Complete

### Phase 1A Review — Review Gate

**Agent**: Review
**Deliverables**: `## Phase 1A Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 1A committed
**Gate**: Phase 1B does not start until APPROVED
**Status**: ✅ Complete — APPROVED

---

### Phase 1B — Dogma Propagation (#212 Phase B + C)

**Agent**: Executive Docs
**Deliverables**:
- [ ] MANIFESTO.md §3 re-reviewed against updated endogenic-design-paper.md (Phase B)
- [ ] AGENTS.md updated with LCF structural-enabler operational constraints (Phase C)
- [ ] `docs/guides/local-compute.md` updated with structural test + enforcement-proximity principle (Phase C)
- [ ] Relevant `.github/agents/` agent files updated (LLM Cost Optimizer, Executive Orchestrator) (Phase C)
- [ ] `docs/research/values-encoding.md` F4 section reviewed for any further updates (Phase C)
- [ ] Relevant skill files referencing LCF or cost-tier framing updated (Phase C)
- [ ] `validate_synthesis.py` passes on all updated research docs
- [ ] `validate_agent_files.py --all` passes

**Depends on**: Phase 0 complete (can run in parallel with Phase 1A)
**Gate**: Phase 1B Review does not start until all deliverables committed
**Status**: ✅ Complete

### Phase 1B Review — Review Gate

**Agent**: Review
**Deliverables**: `## Phase 1B Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 1B committed
**Gate**: Phase 2 does not start until APPROVED
**Status**: ✅ Complete — APPROVED

---

### Phase 2 — Substrate Rebalancing (#239)

**Agent**: Executive Researcher → Research Scout → Executive Docs
**Deliverables**:
- [ ] Substrate mapping table created (CSV/structured data): each layer × file × content type × token count × audience × cross-ref density × re-encoding frequency
- [ ] High-opportunity consolidation candidates identified (4+ encodings, >15% startup budget, CRD < 2)
- [ ] Agent wayfinding interviews completed (2–3 agents: pain points, first-read patterns, redundancy)
- [ ] Rebalancing recommendations report produced: top 3–5 ranked opportunities with current state / proposed state / estimated token savings / signal-preservation rationale
- [ ] `docs/research/substrate-rebalancing-2026-03-13.md` created (D4, status: Final)
- [ ] Issue #239 acceptance criteria fully checked off

**Depends on**: Phase 1B Review APPROVED
**Gate**: Phase 2 Review does not start until deliverable committed
**Status**: ✅ Complete — committed d9f7228

### Phase 2 Review — Review Gate

**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 2 committed
**Gate**: Phase 3 does not start until APPROVED
**Status**: ✅ Complete — APPROVED (commits d9f7228 + 1f6f429)

---

### Phase 3 — Substrate Consolidation (#240)

**Agent**: Executive Docs (with Executive Scripter for tooling)
**Deliverables**:
- [ ] Top 3–5 consolidation moves implemented (move/dedup/absorb content; updated cross-references; clarified ownership)
- [ ] Token count delta measured: before / after / per layer
- [ ] Startup context budget delta measured
- [ ] Signal preservation spot-check: 3–5 critical forward references confirmed intact
- [ ] `docs/research/substrate-consolidation-2026-03-13.md` created (D4, status: Final)
- [ ] `docs/context_budget_target.md` (or new `docs/context_sustainability.md`) updated with tracking metric
- [ ] CI substrate health check added (if feasible)
- [ ] `validate_agent_files.py --all` and `validate_synthesis.py` both pass

**Depends on**: Phase 2 Review APPROVED
**Gate**: Phase 3 Review does not start until all deliverables committed
**Status**: ✅ Complete — committed f98e6bb

### Phase 3 Review — Review Gate

**Agent**: Review
**Deliverables**: `## Phase 3 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 3 committed
**Gate**: Phase 4 does not start until APPROVED
**Status**: ✅ Complete — APPROVED (commit f98e6bb)

---

### Phase 4 — Provenance & Interlinking (TBD Issue)

**Agent**: Executive Scripter → Executive Docs
**Deliverables**:
- [ ] Provenance/interlinking issue created and number assigned (TBD#)
- [ ] `governs:` YAML frontmatter annotation adoption script implemented (complement to value-provenance.md P1 pattern; 0% fleet coverage at baseline)
- [ ] `data/link_registry.yml` audited and gaps in interlinking identified
- [ ] `scripts/weave_links.py` extended or a new script created to assist agents in provenance/interlinking tasks
- [ ] Fleet adoption: key docs updated with `governs:` annotations
- [ ] Agent orientation updated: references to provenance tooling in AGENTS.md / relevant guides
- [ ] Issue acceptance criteria fully checked off

**Depends on**: Phase 3 Review APPROVED
**Gate**: Phase 4 Review does not start until all deliverables committed
**Status**: ✅ Complete — commits 9d5c774 + 3da2149

### Phase 4 Review — Review Gate

**Agent**: Review
**Deliverables**: `## Phase 4 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 4 committed
**Gate**: Sprint Retrospective does not start until APPROVED
**Status**: ✅ Complete — APPROVED

---

### Phase 5A — GitHub Automation Research (#213, #214)

**Agent**: Executive Researcher → Research Scout
**Deliverables**:
- [x] `docs/research/issue-to-markdown-action.md` (D4, Status: Final) — **REJECT** — export_project_state.py already covers orient-step; no marketplace Action needed
- [x] `docs/research/issue-metrics-action.md` (D4, Status: Final) — **DEFER** — JSON snapshot sufficient; adopt github/issue-metrics only at >100 issues
- [x] Both docs pass `validate_synthesis.py`

**Depends on**: Phase 4 Review APPROVED ✅
**Gate**: Phase 5A Review APPROVED before any 5B phase starts
**Status**: ✅ Complete — commit ecef91d

### Phase 5A Review — Review Gate

**Agent**: Review
**Deliverables**: `## Phase 5A Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 5A committed
**Gate**: Phases 5B-Scripts and 5B-Docs do not start until APPROVED
**Status**: ✅ Complete — APPROVED (clean first pass, all 7 criteria)

---

### Phase 5B-Scripts — Workflow Implementation (#215, #216, #217, #218, #219, #220)

**Agent**: Executive Scripter
**Deliverables**:
- [x] `.github/workflows/label-sync.yml` — `EndBug/label-sync@v2`; trigger push+dispatch; replaces `no-label-drift.yml` stub (#215)
- [x] `.github/workflows/no-label-drift.yml` retired/deleted (#215)
- [x] `.github/workflows/changelog-on-merge.yml` stub replaced with full `conventional-changelog-action` implementation (#216)
- [x] `.github/workflows/release-changelog.yml` created — `release-changelog-builder-action`, tag-push trigger (#217)
- [ ] Issue #218 body checkboxes updated to `[x]` (`export_project_state.py` already implemented) — pending Phase N
- [x] `stale.yml` reviewed; issue #219 closed if adequate or updated if not — days-before-close 14, PR thresholds added
- [x] `.github/workflows/release-drafter.yml` + `.github/release-drafter.yml` config (#220)
- [x] `ruff check scripts/ tests/` + `pytest tests/ -x -m "not slow and not integration" -q` both pass

**Depends on**: Phase 5A Review APPROVED
**Note**: May run in parallel with Phase 5B-Docs
**Gate**: Phase 5B Review does not start until 5B-Scripts AND 5B-Docs both committed
**Status**: ✅ Complete — commit a7b7fbe

### Phase 5B-Docs — Orient-step + Documentation Updates (#213, #214, #215)

**Agent**: Executive Docs
**Deliverables**:
- [x] `AGENTS.md` Security Guardrails updated: `.cache/github/` classified as untrusted external content
- [x] `docs/issues/metrics.md` placeholder — **skipped** (#214 DEFER → not needed)
- [x] `scripts/seed_labels.py` docstring updated: CI supersedes it in production (#215)
- [x] `docs/guides/github-workflow.md` label management section updated: references `label-sync.yml` (#215)
- [x] #213 adopt: **REJECT** — no orient-step update needed
- [x] `validate_agent_files.py --all` + `validate_synthesis.py` pass

**Depends on**: Phase 5A Review APPROVED
**Note**: May run in parallel with Phase 5B-Scripts
**Gate**: Phase 5B Review does not start until 5B-Scripts AND 5B-Docs both committed
**Status**: ✅ Complete — commit a7b7fbe

### Phase 5B Review — Review Gate

**Agent**: Review
**Deliverables**: `## Phase 5B Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 5B-Scripts AND Phase 5B-Docs both committed
**Gate**: Phase N (Sprint Retrospective) does not start until APPROVED
**Status**: ✅ Complete — APPROVED (clean first pass, all 8 criteria)

---

### Phase N — Sprint Retrospective & Close

**Agent**: Executive Orchestrator + session-retrospective skill
**Deliverables**:
- [ ] `@session-retrospective` invoked: lessons encoded into substrate
- [ ] All issue body checkboxes updated to reflect completed deliverables
- [ ] Progress comments posted on all sprint issues (#212, #221, #239, #240, #243)
- [ ] PR opened with `Closes #212`, `Closes #221`, `Closes #213`, `Closes #214`, `Closes #215`, `Closes #216`, `Closes #217`, `Closes #218`, `Closes #219`, `Closes #220`, `Closes #239`, `Closes #240`, `Closes #243`
- [ ] CI green on PR
- [ ] Scratchpad `## Session Summary` written
- [ ] `prune_scratchpad.py --force` run after retrospective

**Depends on**: Phase 5B Review APPROVED
**Status**: ⬜ Not started

---

## Cross-Cutting Constraints

- Stream A (GitHub automation) and Stream B (dogma propagation) **may run in parallel**: they are independent until Phase 2.
- No phase begins without its predecessor's Review gate returning APPROVED in the scratchpad.
- Every session opens with a `## Session Start` encoding checkpoint citing the governing axiom and the workplan as the primary endogenous source.
- Retrospective checkpoints are planned into session cool-downs: before the final `prune_scratchpad.py --force`, run `@session-retrospective`.

---

## Acceptance Criteria (Sprint Level)

- [ ] Issue #212: MANIFESTO §3 re-reviewed and full dogma propagation complete
- [ ] Issue #221: GitHub automation implemented; local state representation auto-generated; AGENTS.md orient step uses cached artifacts
- [ ] Issues #213, #214, #215, #216, #217, #218, #219, #220: all sub-issues completed and closed
- [x] Issue #239: Substrate mapping table + rebalancing recommendations produced and committed
- [x] Issue #240: Top consolidation moves implemented; token + signal metrics documented
- [x] Issue #243: `governs:` annotation tooling implemented; fleet adoption begun
- [ ] All PRs green CI; all issues closed via PR body `Closes #N`
- [ ] Sprint retrospective lessons encoded into substrate

---

## Session Log

| Session | Date | Focus | Phase(s) |
|---------|------|-------|----------|
| 1 | 2026-03-13 | Sprint setup + kick off planning | Phase 0 ✅ + begin 1A/1B |
| 2 | 2026-03-13 | Substrate Rebalancing research + D4 doc | Phase 2 ⏳ |
| 3 | 2026-03-13 | Substrate Consolidation | Phase 3 (begin) |
| 4 | 2026-03-13 | Substrate Consolidation complete | Phase 3 ✅ |
| 5 | 2026-03-13 | Provenance & Interlinking | Phase 4 ✅ |
| 6 | 2026-03-13 | Plan recast: #213–#220 as Phase 5A/5B | Phase 5 planning ✅ |
