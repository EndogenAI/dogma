# Workplan: Sprint 14 — Substrate & Tooling Improvements

**Branch**: `feat/sprint-14-substrate-tooling`
**Milestone**: Sprint 14 — Substrate & Tooling Improvements
**Date**: 2026-03-16
**Orchestrator**: Executive Orchestrator

---

## Objective

Sprint 14 consolidates the substrate and tooling layer: new scripts that analyse codebase
health (glossary coverage, doc quality, session state, fleet coupling), CI hooks that
enforce architectural decisions (ADR validation, reading-level targets), and agent/docs
improvements that tighten the pre-delegation checklist. The throughline is
*measurement and enforcement* — turning qualitative substrate guidance into runnable,
interpretable instrumentation. Priority-high items (#279, #281, #286) ship first; lower-
priority infrastructure work (#202, #206) closes the sprint.

**Capacity**: ~21 pts (19 confirmed + #293 backlog promotion, against 20pt medium target).

---

## Phase Plan

### Phase 1 — Priority Fixes & Substrate Atlas ⬜
**Agent**: Executive Scripter
**Issues**: #286 (effort:xs, priority:high), #281 (effort:s, priority:high), #279 (effort:m, priority:high)
**Deliverables**:
- `agents/AGENTS.md` / Pre-Delegation Checklist updated with format-ceiling dual mandate (#286)
- `data/adr-schema.json` (or equivalent) + CI hook `.github/workflows/validate-adrs.yml` (#281)
- `data/substrate-atlas.yml` scaffolded with initial node/edge schema (#279)

**Depends on**: nothing
**CI**: validate_agent_files, ruff, fast-tests
**Status**: Not started

---

### Phase 2 — Script Tools: Quality & Coverage ⬜
**Agent**: Executive Scripter
**Issues**: #290 (effort:s), #289 (effort:m), #280 (effort:m)
**Deliverables**:
- `scripts/check_glossary_coverage.py` + `tests/test_check_glossary_coverage.py` (#290)
- `scripts/assess_doc_quality.py` + `tests/test_assess_doc_quality.py` (#289)
- `scripts/validate_session_state.py` extended with YAML phase-status block parsing + tests (#280)

**Depends on**: Phase 1 (substrate-atlas.yml schema may inform doc-quality script)
**CI**: ruff, pytest ≥80% coverage per script
**Status**: Not started

---

### Phase 3 — CI / Automation & Divergence Check ⬜
**Agent**: Executive Automator + Executive Scripter
**Issues**: #287 (effort:s), #293 (effort:s, backlog promotion)
**Deliverables**:
- `.reading-level-targets.yml` config file + CI enforcement step in existing lint workflow (#287)
- `scripts/check_divergence.py` + `tests/test_check_divergence.py` (#293)

**Depends on**: Phase 2 (doc quality tooling informs reading-level targets spec)
**CI**: ruff, validate_synthesis, fast-tests
**Status**: Not started

---

### Phase 4 — Docs, Lowpri Scripts & Docsite ⬜
**Agent**: Executive Docs + Executive Scripter
**Issues**: #286 (if Phase 1 only partial), #288 (effort:xs), #253 (effort:s), #206 (no effort, priority:medium), #202 (priority:low)
**Deliverables**:
- Sprint-close checklist updated with HGT upstream learning slot (#288)
- `scripts/parse_fsm_to_graph.py` initial implementation (#253)
- FrankenBrAIn benchmark spec doc drafted (#206)
- MkDocs Material `mkdocs.yml` expanded + `docs/` index hierarchy (#202)

**Depends on**: Phase 3
**CI**: ruff, check_doc_links, validate_synthesis (if research docs touched)
**Status**: Not started

---

## Issue Clusters

| Cluster | Issues | Pts |
|---------|--------|-----|
| Priority Fixes | #286, #281, #279 | 6 |
| Script Tools | #290, #289, #280 | 8 |
| CI & Automation | #287, #293 | 4 |
| Docs / Infra | #288, #253, #206, #202 | 3+ |
| **Total** | **11 confirmed + 1 promotion** | **~21 pts** |

---

## Acceptance Criteria

- [ ] All Phase 1 priority:high issues (#279, #281, #286) committed and passing CI
- [ ] All new scripts have ≥80% test coverage and pass ruff
- [ ] No heredocs used in any file write (pre-commit hook passes)
- [ ] Workplan review completed and logged in scratchpad under `## Workplan Review Output`
- [ ] Sprint-assignment comments posted on priority:high issues (#279, #281, #286)
- [ ] Milestone `Sprint 14 — Substrate & Tooling Improvements` reflects all assigned issues
- [ ] CHANGELOG.md updated with Sprint 14 entries on sprint close

---

## Workplan Review Output

<!-- Review agent verdict logged here before Phase 1 begins -->

