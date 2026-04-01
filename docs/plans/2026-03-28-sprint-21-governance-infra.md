# Workplan: Sprint 21 — Governance & Infrastructure

**Branch**: `feat/sprint-21-governance-infra`
**Date**: 2026-03-28
**Orchestrator**: Executive Orchestrator
**Milestone**: Sprint 21 — Governance & Infrastructure (#37)

---

## Objective

Deliver the remaining open Sprint 21 scope only: #487, #488, and #489. Sequence work so provider-attribute semconv alignment lands first (#487), idempotency/dedup protection builds on that normalized signal layer (#488), and retention/rotation policy codifies long-run operational posture on top of stable append semantics (#489).

**Total effort**: 12-14 units (must-have only)

---

## Phase Plan

### Phase 0 — Workplan Review ⬜
**Agent**: Review
**Deliverables**:
- APPROVED verdict logged under `## Workplan Review Output` in scratchpad
- Phase ordering validated for dependency chain #487 -> #488 -> #489
- All dependencies explicit and correct

**Depends on**: nothing
**Gate**: Phase 1 does not start until APPROVED verdict is recorded in scratchpad
**CI**: N/A (review only)
**Status**: ✅ Complete — APPROVED

---

### Phase 1 — Semconv Provider Alignment ⬜
**Agent**: Executive Scripter
**Issues**: #487
**Deliverables**:
- Inventory current `gen_ai.system` / `gen_ai.provider.name` usage in scripts and tests
- Adopt one canonical provider attribute policy and update emitters/tests accordingly
- Add backward-compat migration note where renamed fields affect downstream parsing
- Tests updated to verify provider-attribute consistency end-to-end for touched paths

**Depends on**: Phase 0 APPROVED
**Gate**: #487 implementation complete, tests pass, commits pushed
**CI**:
- `uv run pytest tests/test_emit_genai_spans.py -x -q`
- `uv run ruff check scripts/ tests/`
- `uv run ruff format --check scripts/ tests/`
**Status**: ✅ Complete (pending Phase 1 Review)

---

### Phase 1 Review — Validate #487 ⬜
**Agent**: Review
**Deliverables**:
- APPROVED verdict for Phase 1 changes
- Verification that provider-alignment behavior is covered by tests

**Depends on**: Phase 1
**Gate**: Phase 2 does not start until APPROVED verdict is recorded in scratchpad
**CI**: N/A (review only)
**Status**: ✅ Complete — APPROVED

---

### Phase 2 — Bridge Idempotency and Dedup Guard ⬜
**Agent**: Executive Scripter
**Issues**: #488
**Deliverables**:
- Define deterministic dedup key strategy for bridge-generated cost rows
- Implement duplicate suppression/idempotency guard in bridge or append path
- Add tests for duplicate replay and repeated instrumentation scenarios
- Document dedup tradeoffs and chosen strategy

**Depends on**: Phase 1 Review APPROVED
**Gate**: #488 implementation complete, tests pass, commits pushed
**CI**:
- `uv run pytest tests/test_session_cost_log.py tests/test_emit_genai_spans.py -x -q`
- `uv run ruff check scripts/ tests/`
- `uv run ruff format --check scripts/ tests/`
**Status**: ⏳ In progress

---

### Phase 2 Review — Validate #488 ⬜
**Agent**: Review
**Deliverables**:
- APPROVED verdict for Phase 2 changes
- Verification that idempotency guard prevents duplicates without suppressing distinct rows

**Depends on**: Phase 2
**Gate**: Phase 3 does not start until APPROVED verdict is recorded in scratchpad
**CI**: N/A (review only)
**Status**: ✅ Complete — APPROVED

---

### Phase 3 — Retention and Rotation Policy ⬜
**Agent**: Executive Docs + Executive Scripter
**Issues**: #489
**Deliverables**:
- Define retention window and archival strategy for historical `session_cost_log.json` rows
- Define rotation trigger (size/time) and implement script/procedure as scoped by issue
- Ensure aggregate scripts remain functional with rotated/archived data
- Document retention/rotation policy and operational guidance in scripts/docs

**Depends on**: Phase 2 Review APPROVED
**Gate**: #489 implementation and policy docs complete, tests/checks pass, commits pushed
**CI**:
- `uv run pytest tests/ -m "not slow and not integration" -x -q`
- `uv run ruff check scripts/ tests/`
- `uv run ruff format --check scripts/ tests/`
**Status**: ✅ Complete (commit `cbda352`)

---

### Phase 3 Review — Validate #489 ⬜
**Agent**: Review
**Deliverables**:
- APPROVED verdict for Phase 3 changes
- Confirmation that policy definition and implementation behavior are aligned

**Depends on**: Phase 3
**Gate**: Phase 4 does not start until APPROVED verdict
**CI**: N/A (review only)
**Status**: ✅ Complete — APPROVED

---

### Phase 4 — PR and Close ⬜
**Agent**: GitHub Agent + Executive Orchestrator
**Deliverables**:
- PR created on `feat/sprint-21-governance-infra` with `Closes #487`, `Closes #488`, `Closes #489`
- Copilot review retrieved and triaged (follow `.github/skills/pr-review-triage/SKILL.md`)
- All blocking review comments fixed and replied to (use `scripts/pr_review_reply.py`)
- CI passes (all checks green)
- PR merged
- All closed issues confirmed via `gh issue view <num>`
- Sprint 21 milestone closed
- Session summary written to scratchpad; session archived

**Depends on**: Phase 3 Review APPROVED
**Gate**: All issues closed, PR merged, session archived
**CI**: All automated checks must pass before merge
**Status**: ⏳ In progress

---

## Parallelisation Notes

No phases can be parallelized — strict dependency chain #487 -> #488 -> #489 with mandatory review gates between each domain phase.

---

## Capacity Decision

**Must-Have only**: Phases 1-3 represent full sprint scope and are required.
**Total**: 12-14 units — fixed-scope sprint, quality-first.

---

## Open Questions

1. Should #489 include script-level enforcement in this sprint, or policy/procedure docs only?

---

## References

- Sprint planning analysis: `.tmp/main/2026-03-27.md`
- Sprint 21 milestone: https://github.com/EndogenAI/dogma/milestone/37
- Reference workplan template: `docs/plans/2026-03-27-q2-wave1-phase1.md`

---

## Acceptance Criteria

- [ ] #487 delivered: provider-attribute semconv alignment implemented with updated tests and migration note.
- [ ] #487 review gate approved before #488 starts.
- [ ] #488 delivered: dedup/idempotency guard implemented with replay/duplicate coverage tests.
- [ ] #488 review gate approved before #489 starts.
- [ ] #489 delivered: retention/rotation policy defined, documented, and aligned with implemented append behavior.
- [ ] #489 review gate approved before PR phase.
- [ ] CI checks pass for all touched scripts/tests/docs.
- [ ] PR includes closure keywords for #487, #488, #489 and closes all three issues on merge.
