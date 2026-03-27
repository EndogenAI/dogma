# Workplan: Q2 Wave 2 — Phase 0 + Phase 1

**Branch**: `feat/q2-wave2-phase0-phase1`
**Date**: 2026-03-26
**Orchestrator**: Executive Orchestrator
**Milestone**: Q2 Governance Wave 2 (#33)

---

## Objective

Q2 Wave 1 is fully merged. This workplan covers Wave 2 Phase 0 (pre-sprint
blockers cleared after Wave 1 close) and Phase 1 (Agent Fleet Standardization —
the highest-priority Wave 2 execution stream). Phase 0 clears a recurring CI
failure in the `Snapshot GitHub State` workflow before Phase 1 execution begins.

**Note**: Issues #388, #381, #386, #356, #408 referenced in the original sprint
recommendation are **already closed** (merged in PR #440, 2026-03-25). Wave 2
Phase 0 addresses new blockers discovered post-Wave-1-close.

---

## Phase Plan

### Phase 0 — Pre-Sprint Blockers ✅
**Agent**: CI Monitor + Executive Scripter
**Deliverables**:
- Fix `Snapshot GitHub State` recurring CI failure (3 days, `git push` to `main`
  was blocked by branch protection — resolved by switching to upload-artifact
  pattern so no `SNAPSHOT_PAT` secret or bypass actor config is needed)
- CI health check: confirm all other scheduled + pushed workflows are green

**Depends on**: nothing
**Issues**: (new — no existing issue; open one as part of this phase)
**CI**: Tests
**Status**: Not started

### Phase 0 Review ✅
**Agent**: Review
**Deliverables**: APPROVED verdict in scratchpad `## Phase 0 Review Output`
**Depends on**: Phase 0 committed
**Status**: Not started

### Phase 1 — Agent Fleet Standardization ✅
**Agent**: Executive Fleet + Executive Scripter
**Deliverables**:
- #332 — enforce approval gates / YAML governance in `validate_agent_files.py`
  **(GATE — must ship before #333–#336)**
- #368 — Miller's Law tool-count ceiling (≤9) enforcement in validator
- #335 — return compression ceiling per subagent (agent file + AGENTS.md update)
- Additional Phase 1 issues per Executive Planner decomposition

**Depends on**: Phase 0 Review APPROVED
**Issues**: #332, #368, #335 (plus others from Milestone #33 as decomposed)
**CI**: Tests, validate-agent-files, ruff
**Status**: Not started

### Phase 1 Review ✅
**Agent**: Review
**Deliverables**: APPROVED verdict in scratchpad `## Phase 1 Review Output`
**Depends on**: Phase 1 committed
**Status**: Not started

### Phase 2 — Research Recommendations Implementation ⬜
**Agent**: Executive Docs + Executive Researcher
**Deliverables**:
- Implementation tracks from Milestone #35: #446–#459 (Track A–E, Phases 1–4)
- Decomposed per Executive Planner in a follow-on session

**Depends on**: Phase 1 Review APPROVED
**Issues**: #446–#459
**Status**: Deferred to follow-on session

---

## Acceptance Criteria

- [ ] `Snapshot GitHub State` CI passes on every scheduled run after fix
- [ ] `validate_agent_files.py` enforces YAML consensus (#332) — CI gate active
- [ ] Miller's Law enforcement live (#368) — `--max-tools 9` check in validator
- [ ] Return compression ceiling encoded in AGENTS.md + agent files (#335)
- [ ] All Phase 0 + Phase 1 issues closed via PR merge
- [ ] Phase 0 Review + Phase 1 Review both APPROVED before merge
**CI**: Tests, Auto-validate
**Status**: Not started

### Phase 4 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- <!-- list deliverables -->

**Depends on**: Phase 3
**CI**: Tests, Auto-validate
**Status**: Not started

### Phase 5 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**:
- Fleet integration (if adding new agents/skills: run `uv run python scripts/check_fleet_integration.py --dry-run`)
- Session close (archive session, update scratchpad summary, push branch)
- <!-- add other deliverables -->

**Depends on**: Phase 4
**CI**: Tests, Auto-validate
**Status**: Not started

---

## Acceptance Criteria

- [ ] All phases complete and committed
- [ ] All changes pushed and PR is up to date
