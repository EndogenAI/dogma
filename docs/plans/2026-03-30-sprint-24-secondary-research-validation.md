# Workplan: Sprint 24 — Secondary Research & Validation Depth

**Branch**: `feat/sprint-24-secondary-research`
**Date**: 2026-03-30
**Orchestrator**: Executive Orchestrator
**Milestone**: Sprint 24 — Secondary Research & Validation Depth
**Issues**: #415, #419, #503, #478, #477

---

## Objective

Sprint 24 delivers two categories of work in dependency order. First, a rapid secondary
research trio (#415 ClawTeams swarm orchestration, #419 GitAgent framework analysis, #503
Vector Databases) runs the Scout → Synthesize → Archive pipeline; these three issues are
independent and can be parallelised within Phase 1. Second, a research-then-implement
sequence clears the validation depth gap: #478 researches correct xs–xxl threshold
calibration for `validate_synthesis.py`, and only after those findings are committed does
#477 (dynamic sizing implementation) begin — ensuring the feature is calibrated by evidence,
not guesswork. Together, the sprint establishes a hardened synthesis validation baseline
before any Q2 measurement study begins.

**Chicken-and-egg decision**: Research (#478) precedes implementation (#477) because the
implementation requires calibrated threshold values as input. #477 cannot be correctly
implemented without #478's findings.

**Blocker note**: #478 body states it is blocked by #477, but the dependency is inverted —
research should inform implementation. The blocker annotation is stale and has been cleared
in this sprint plan.

---

## Phase Plan

### Phase 0 — Workplan Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Workplan Review Output` appended to scratchpad, verdict: APPROVED

**Depends on**: nothing (runs before Phase 1)
**Status**: Not started

### Phase 1 — Secondary Research Trio (#415, #419, #503) ⬜
**Agent**: Executive Researcher → Research Scout fleet
**Deliverables**:
- `docs/research/swarm-vs-hierarchical-orchestration.md` — Status: Final (closes #415)
- `docs/research/gitagent-framework-analysis.md` — Status: Final (closes #419)
- `docs/research/vector-databases-explained.md` — Status: Final (closes #503)
- All three source URLs cached via `scripts/fetch_source.py`

**Depends on**: Phase 0 APPROVED
**Notes**: #415, #419, #503 are independent — delegate as a batched trio to Executive Researcher
**CI**: validate_synthesis, lychee
**Status**: Not started

### Phase 1 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase 1 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 1 deliverables committed
**Status**: Not started

### Phase 2 — Primary Research: Depth Threshold Standards (#478) ⬜
**Agent**: Executive Researcher → Research Scout + Synthesizer
**Deliverables**:
- `docs/research/primary-research-depth-thresholds.md` — Status: Final (closes #478)
- 3+ metrics for evaluating primary research depth identified
- Proposed xs–xxl tier mapping with rationale
- Breadth vs. depth tradeoff documented
- Source URLs cached

**Depends on**: Phase 1 Review APPROVED
**Notes**: Findings from this phase are the calibration source for Phase 3 (#477). Phase 3 must not begin until this doc is committed.
**CI**: validate_synthesis
**Status**: Not started

### Phase 2 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 2 deliverables committed
**Status**: Not started

### Phase 3 — Dynamic Sizing Implementation (#477) ⬜
**Agent**: Executive Scripter
**Deliverables**:
- `scripts/validate_synthesis.py` updated with xs–xxl dynamic sizing tiers
- Tier threshold values derived from Phase 2 (#478) research findings
- Tests updated/added in `tests/test_validate_synthesis.py`
- Passes `uv run pytest tests/test_validate_synthesis.py -x`
- Passes `uv run ruff check scripts/validate_synthesis.py`

**Depends on**: Phase 2 Review APPROVED (calibration source required before implementation)
**Additional informing source** (noted 2026-03-30): `docs/research/swarm-vs-hierarchical-orchestration.md` (closes #415) is also a direct input to this implementation. The swarm paper's hierarchical takeback pattern documents the same enforcement-proximity principle at play in synthesis validation — tiers that gate agent output belong at the same layer as the workplan phase gate (T2 static enforcement, not runtime suggestion). The Scripter must read both `primary-research-depth-thresholds.md` (#478) **and** `swarm-vs-hierarchical-orchestration.md` (#415) before implementing.
**CI**: pytest, ruff
**Status**: Not started

### Phase 3 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase 3 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 3 deliverables committed
**Status**: Not started

### Phase 4 — GitHub Ops & Sprint Close ⬜
**Agent**: Executive PM + GitHub
**Deliverables**:
- Sprint 24 milestone created: "Sprint 24 — Secondary Research & Validation Depth"
- #415, #419, #503, #478, #477 assigned to Sprint 24 milestone
- #478 blocker annotation removed (comment posted explaining inversion)
- Sprint-assignment comment posted on each issue
- Issue body checkboxes updated for all closed issues
- Branch pushed; PR opened with `Closes #415, #419, #503, #478, #477`

**Depends on**: Phase 3 Review APPROVED
**Status**: Not started

---

## Acceptance Criteria

- [ ] All five issues closed via PR merge
- [ ] Three secondary research docs committed to `docs/research/`, each Status: Final
- [ ] `docs/research/primary-research-depth-thresholds.md` committed with 3+ depth metrics and xs–xxl tier proposal
- [ ] `scripts/validate_synthesis.py` implements dynamic sizing with tier values from #478 findings
- [ ] All tests pass (`uv run pytest tests/ -x -m "not slow and not integration"`)
- [ ] Sprint 24 milestone exists and all five issues assigned
- [ ] PR open with all five `Closes #NNN` lines

---

## Sprint Effort Summary

| # | Title | Effort | Cluster |
|---|-------|--------|---------|
| #415 | ClawTeams swarm orchestration | S | research |
| #419 | GitAgent framework analysis | S | research |
| #503 | Vector Databases (secondary) | XS | research |
| #478 | Primary research depth thresholds | M | research |
| #477 | Dynamic sizing for synthesis validation | S | scripting |

**Total**: XS(1) + S(2+2+2) + M(3) = **10 effort units** — S-capacity sprint
**CI**: Tests, Auto-validate
**Status**: Not started

---

## Acceptance Criteria

- [ ] All phases complete and committed
- [ ] All changes pushed and PR is up to date

## PR Description Template

<!-- Copy to PR description when opening the PR -->

Closes #415, Closes #419, Closes #478, Closes #477, Closes #503
