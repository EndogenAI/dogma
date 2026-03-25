# Workplan: User Handle Correction

**Branch**: `feat/issue-435-branch-sync-gate`
**Date**: 2026-03-25
**Orchestrator**: Executive Orchestrator

---

## Objective

This workplan corrects the user handle throughout the project. Specifically, we'll replace the incorrect `@conor` username with `@accessit3ch` and `@ckellydesign`. We'll also establish a governance constraint to prevent referencing unverified users.

**Chicken-and-Egg Resolution**: Research-First (Phase 2) is prioritized over Documentation-First (Phase 3) as the governance guidance and corrections are entirely dependent on first identifying the scope of incorrect handle usage.

---

## Phase Plan

### Phase 1 — Workplan Review Gate ⬜
**Agent**: Review
**Deliverables**:
- Workplan APPROVED verdict in scratchpad.

**Depends on**: nothing
**CI**: Tests, Auto-validate
**Status**: Not started

### Phase 2 — Username Scan & Triage (Research) ⬜
**Agent**: Executive PM
**Deliverables**:
- Search for `@conor` in docs, agents, and GitHub Issues.
- List of file and issue paths containing the incorrect handle.
- List of appropriate re-assignments for `@accessit3ch` and `@ckellydesign`.

**Depends on**: Phase 1
**Gate**: Phase 2 is a research phase and is NOT parallel with any subsequent phase it informs.
**CI**: Tests, Auto-validate
**Status**: Not started

### Phase 3 — Governance & Enforcement ⬜
**Agent**: Executive Docs
**Deliverables**:
- Update `AGENTS.md` and `docs/guides/github-workflow.md` to include a constraint: "Do NOT mention users unless explicitly verified."
- Propose a programmatic check for username mention verification (L3 status).

**Depends on**: Phase 2
**CI**: Tests, Auto-validate
**Status**: Not started

### Phase 4 — Username Correction ⬜
**Agent**: GitHub
**Deliverables**:
- Update file content to replace `@conor` with the correct handle.
- Update GitHub issue bodies, labels, and metadata as identified by Task 2.
- Commit all changes following [Conventional Commits](https://www.conventionalcommits.org/).

**Depends on**: Phase 2, Phase 3
**CI**: Tests, Auto-validate
**Status**: Not started

### Phase 5 — Fleet Integration ⬜
**Agent**: Executive Fleet
**Deliverables**:
- Fleet integration (if adding new agents/skills: run `uv run python scripts/check_fleet_integration.py --dry-run`)
- Session close (archive session, update scratchpad summary, push branch)

**Depends on**: Phase 4
**CI**: Tests, Auto-validate
**Status**: Not started

---

## Acceptance Criteria

- [ ] All `@conor` mentions are removed from code, docs, and the current session.
- [ ] No unconfirmed `@` mentions are made going forward.
- [ ] GitHub issues are updated with correct user metadata.
- [ ] All phases complete and committed.
- [ ] All changes pushed and PR is up to date.
