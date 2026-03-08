# Workplan: Follow Up Review Gate Items

**Branch**: `feat/follow-up-review-gate-items`
**Date**: 2026-03-08
**Orchestrator**: Executive Orchestrator
**Source**: `docs/sessions/2026-03-08-review-gate-inter-phase.md` § Recommended Follow-ups

---

## Objective

Action the five follow-up items identified during the inter-phase review-gate session (PR #66). Four scripting tasks extend `validate_agent_files.py` and `scaffold_workplan.py` with new checks and prompts; one docs task adds a pre-review grep sweep step to `executive-orchestrator.agent.md`. All scripting changes require tests; the agent file change requires `validate_agent_files.py --all` passing before commit.

---

## Phase Plan

### Phase 1 — Scripting: validate_agent_files + scaffold_workplan ⬜
**Agent**: Executive Scripter
**Deliverables**:
- `scripts/validate_agent_files.py`: new check — flag `Fetch-before-check` label ordering
- `scripts/validate_agent_files.py`: new check — flag literal `## Phase N Review Output` in `.github/`
- `scripts/scaffold_workplan.py`: CI field fixed vocab (`Tests`, `Auto-validate`, `Lint`)
- `scripts/scaffold_workplan.py`: prompt for linked issues, emit `Closes #N` in PR template
- `tests/test_validate_agent_files.py`: tests for both new checks
- `tests/test_remaining_scripts.py`: tests for both scaffold_workplan changes
**Depends on**: nothing
**CI**: Tests, Auto-validate
**Status**: Not started

### Phase 1 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 1 changes committed
**Gate**: Phase 2 does not start until Review returns APPROVED
**Status**: Not started

### Phase 2 — Docs: executive-orchestrator.agent.md ⬜
**Agent**: Executive Docs
**Deliverables**:
- `.github/agents/executive-orchestrator.agent.md`: pre-review grep sweep step added to per-phase sequence
**Depends on**: Phase 1 Review APPROVED
**CI**: Auto-validate, Lint
**Status**: Not started

### Phase 2 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 2 changes committed
**Gate**: Phase 3 does not start until Review returns APPROVED
**Status**: Not started

### Phase 3 — Commit & Push ⬜
**Agent**: Orchestrator (direct)
**Deliverables**: All changes pushed; PR opened
**Depends on**: Phase 2 Review APPROVED
**Status**: Not started

---

## Acceptance Criteria

- [ ] `validate_agent_files.py` flags `Fetch-before-check` label ordering across `.github/`
- [ ] `validate_agent_files.py` flags literal `## Phase N Review Output` in `.github/`
- [ ] `scaffold_workplan.py` CI field uses `Tests | Auto-validate | Lint` fixed vocab
- [ ] `scaffold_workplan.py` prompts for linked issue numbers and emits `Closes #N`
- [ ] `executive-orchestrator.agent.md` per-phase sequence includes pre-review grep sweep
- [ ] All new checks covered by tests (≥80% coverage on changed code)
- [ ] `validate_agent_files.py --all` passes (42/42)
- [ ] All phases complete and committed
- [ ] PR opened on `feat/follow-up-review-gate-items`
