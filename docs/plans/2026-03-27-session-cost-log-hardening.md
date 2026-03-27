# Workplan: Session Cost Log Hardening

**Branch**: `feat/session-cost-log-hardening` (create from `main` at Phase E start)
**Date**: 2026-03-27
**Orchestrator**: Executive Orchestrator
**Status**: Active

---

## Objective

Harden the session cost tracking substrate across three axes: (1) prevent silent pollution of `session_cost_log.json` with zero-token placeholder records by introducing a zero-guard with a `synthetic` flag, (2) wire the existing OTel instrumentation chain (`instrument_agent_calls` → `emit_otel_genai_spans`) to auto-append real token counts to the cost log for all model calls made by scripts we directly control, and (3) publish a clear operational guide formally defining the observability boundary between what the local substrate CAN capture and what it cannot (GitHub Copilot Chat, VS Code extension layer). This sprint closes issues #484, #485, and #486, which were seeded from the post-merge cooldown observation that zero-token records were being accepted without challenge.

---

## Design Decisions (Phase D — resolved before Phase E)

| Question | Decision |
|----------|----------|
| **Q1 — Schema change style** | Backward-compatible: `synthetic` is optional, defaults to `False`; `validate_record()` widened from exact-match to "at-least-required-keys-present". `REQUIRED_RECORD_KEYS` unchanged. |
| **Q2 — Instrumentation activation scope** | Always-on for all scripts already importing `instrument_agent_calls` — broadest coverage, no per-script opt-in required. |
| **Q3 — Observation boundary doc placement** | `docs/guides/observability-boundaries.md` — operational guide format; no D4 synthesis schema required. |
| **Q4 — Zero-guard error mode** | Raise `ValueError` as the primary signal, but with a failsafe: callers (e.g. span-close hooks) must catch and log `logging.warning` rather than crashing. Bridge does this automatically. |

---

## Phase Plan

### Phase A — Seed GitHub Issues ✅
**Agent**: Executive Orchestrator (direct — issue creation is coordination)
**Deliverables**:
- Issue #484: zero-guard for `session_cost_log.py`
- Issue #485: instrumentation bridge
- Issue #486: observability boundary guide
**Depends on**: nothing
**Gate**: All 3 issues confirmed open via `gh issue list`
**Status**: Complete

---

### Phase A-R — Review: Issue Seed Quality ⬜
**Agent**: Review
**Deliverables**: Verdict logged in scratchpad under `## Phase A-R Review Output`
**Depends on**: Phase A
**Gate**: APPROVED before Phase B begins
**Status**: Not started

---

### Phase B — Research Scouting & Synthesis ⬜
**Agent**: Executive Researcher (→ Research Scout → Synthesizer)
**Deliverables**:
- Scout notes covering: OTel span-close processor patterns, `synthetic` schema extension precedents, Copilot Chat API observability surface
- Synthesis summary (≤2000 tokens) appended to scratchpad under `## Phase B Output`
- `gh issue comment` posted on each of #484, #485, #486 with relevant findings

**Depends on**: Phase A-R (APPROVED)
**Gate**: `## Phase B Output` present in scratchpad; comment posted on all 3 issues
**Note**: Phase B is cross-cutting (informs Phases C, E, and the doc in #486) — it is NOT marked parallel with any downstream phase
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase B-R — Review: Research Quality ⬜
**Agent**: Review
**Deliverables**: Verdict logged under `## Phase B-R Review Output`
**Depends on**: Phase B
**Gate**: APPROVED before Phase C begins
**Status**: Not started

---

### Phase C — Update Sprint Workplan ⬜
**Agent**: Executive Planner
**Deliverables**:
- This file (`docs/plans/2026-03-27-session-cost-log-hardening.md`) updated with Phase B research findings incorporated into Phase E deliverables and open questions table
- Any new issues seeded for recommendations not yet tracked
- File committed

**Depends on**: Phase B-R (APPROVED)
**Gate**: Updated workplan committed; confirmed via `git log --oneline -1`
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase C-R — Review: Workplan Compliance ⬜
**Agent**: Review
**Deliverables**: Verdict logged under `## Workplan Review Output`
**Criteria**:
1. Cross-cutting research (Phase B) not marked parallel with any phase it informs
2. Phase C research precedes Phase E implementation (N−1 pattern)
3. Phase D human gate separates research from implementation
4. Every dependent phase has `Depends on:` annotation

**Depends on**: Phase C
**Gate**: APPROVED logged before Phase D begins
**Status**: Not started

---

### Phase D — Human Gate: Design Decisions ⬜
**Agent**: Executive Orchestrator (surfaces to human; no execution)
**Deliverables**: Decision table in scratchpad under `## Phase D Decisions`; all open questions confirmed resolved (Phase B may surface new ones)

**Depends on**: Phase C-R (APPROVED)
**Gate**: Human explicitly confirms decisions before Phase E begins; no autonomous escalation
**Status**: Not started

---

### Phase E — Implementation ⬜
**Agent**: Executive Scripter
**Deliverables**:
- `scripts/session_cost_log.py` — zero-guard + optional `synthetic` field + `exclude_synthetic` filter in `read_log()`
- `scripts/emit_otel_genai_spans.py` — span-close bridge hook calling `log_session_cost()`; catches `ValueError`, emits `logging.warning`
- `docs/guides/observability-boundaries.md` — new operational guide (see Issue #486 AC)
- `tests/test_session_cost_log.py` — updated: zero-guard raise, synthetic-flag write, exclude_synthetic filter, backward-compat records
- `tests/test_emit_otel_genai_spans.py` — new/updated: integration test for bridge (mocked span → temp log write and zero-skip paths)

**Depends on**: Phase D (decisions confirmed by human)
**Gate**: `uv run pytest tests/test_session_cost_log.py tests/test_emit_otel_genai_spans.py -x -q` exits 0; `uv run ruff check scripts/ tests/` exits 0
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase E-R — Review: Implementation Quality ⬜
**Agent**: Review
**Deliverables**: Verdict logged under `## Phase E-R Review Output`; blocking findings enumerated
**Depends on**: Phase E
**Gate**: APPROVED before Phase G begins
**Status**: Not started

---

### Phase G — Cross-Review by Fleet Specialists ⬜
**Agent**: Executive Fleet + Executive Docs (non-overlapping files — safe to run sequentially same session)
**Deliverables**:
- Fleet review: script API surface, no tool-count or posture violations in any touched agent files
- Docs review: `observability-boundaries.md` headings, cross-references, link integrity
- All blocking findings fixed; fix commits logged in scratchpad under `## Phase G Output`

**Depends on**: Phase E-R (APPROVED)
**Gate**: `uv run python scripts/validate_agent_files.py --all` exits 0; doc link-check passes
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase G-R — Review: Final Pre-PR Gate ⬜
**Agent**: Review
**Deliverables**: Final APPROVED verdict covering all changed files; logged under `## Phase G-R Review Output`
**Depends on**: Phase G
**Gate**: APPROVED before Phase H begins
**Status**: Not started

---

### Phase H — Open Pull Request ⬜
**Agent**: GitHub Agent
**Deliverables**:
- Branch `feat/session-cost-log-hardening` pushed
- PR opened with body containing `Closes #484 / Closes #485 / Closes #486`
- PR URL recorded in scratchpad

**Depends on**: Phase G-R (APPROVED)
**Gate**: `gh pr view` returns open PR; Copilot review auto-triggered on open
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase I — CI & Review Polling (30s interval) ⬜
**Agent**: Executive Orchestrator
**Deliverables**:
- CI confirmed green
- Copilot review retrieved and all comments classified (Blocking / Suggestion / Nit / Question)
- Blocking comments fixed before any merge discussion

**Depends on**: Phase H
**Polling mechanism**:
```bash
uv run python scripts/wait_for_github_run.py --interval 30 --timeout 600
```
After CI green:
```bash
gh pr view <num> --json reviews,reviewThreads
gh api repos/EndogenAI/dogma/pulls/<num>/comments
```
Triage per `pr-review-triage` skill before merge.

**Gate**: CI passing + all Copilot review comments classified; blocking comments fixed
**CI**: Tests, Auto-validate
**Status**: Not started

---

## Acceptance Criteria

- [ ] Issue #484 closed: zero-guard implemented, backward-compatible `synthetic` field, `exclude_synthetic` filter, all tests green
- [ ] Issue #485 closed: span-close bridge in `emit_otel_genai_spans.py`; always-on for `instrument_agent_calls` importers; failsafe logging; integration tests green
- [ ] Issue #486 closed: `docs/guides/observability-boundaries.md` published, cross-referenced from `scripts/README.md`, lint-clean
- [ ] All existing tests continue to pass (no regressions in `tests/test_session_cost_log.py`, `tests/test_aggregate_session_costs.py`)
- [ ] `uv run ruff check scripts/ tests/` exits 0
- [ ] PR #H open with `Closes #484 / #485 / #486`; CI green; Copilot review triaged

---

## Dependency Map

| Phase | Depends on | Agent | Output type |
|-------|-----------|-------|-------------|
| A | — | Executive Orchestrator | 3 GitHub issues |
| A-R | A | Review | APPROVED |
| B | A-R | Executive Researcher | Scout notes + synthesis + issue comments |
| B-R | B | Review | APPROVED |
| C | B-R | Executive Planner | Updated workplan committed |
| C-R | C | Review | APPROVED |
| D | C-R | Executive Orchestrator | Decision table (human input) |
| E | D | Executive Scripter | 3 scripts + 2 test files changed |
| E-R | E | Review | APPROVED |
| G | E-R | Executive Fleet + Docs | Fixes committed |
| G-R | G | Review | APPROVED |
| H | G-R | GitHub Agent | Open PR |
| I | H | Executive Orchestrator | CI green + review triaged |

---

## PR Description Template

```
## Summary

Hardens the session cost tracking substrate across three axes:
- Zero-guard prevents silent acceptance of zero-token placeholder records
- OTel instrumentation bridge auto-appends real token counts to `session_cost_log.json`
- Observability boundary guide formally documents what is and isn't capturable locally

Closes #484
Closes #485
Closes #486
```
