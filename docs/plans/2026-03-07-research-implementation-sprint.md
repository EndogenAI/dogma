# Workplan: Research Implementation Sprint

**Date**: 2026-03-07
**Branch**: `feat/implement-research-findings`
**Objective**: Implement documentation, fleet, and guide improvements derived from the 6 research deliverables completed earlier in this session (issues #16–#21).

---

## Phases

### Phase 1 — Immediate Documentation Quick Wins

**Agent**: Orchestrator (direct)
**Deliverables**:
- `CHANGELOG.md` created with `[Unreleased]` section
- `README.md` updated: CI badge + TOC
- `CONTRIBUTING.md` updated: dev-env setup section + legibility/idempotency checklist
**Depends on**: nothing
**Gate**: Phase 2 does not start until all three files are written and confirmed existing

**Status**: ⬜ Not started

---

### Phase 2 — Fleet Agent Updates

**Agent**: Executive Fleet
**Deliverables**:
- `executive-pm.agent.md` updated with PM research findings (issue templates, labels taxonomy, ADRs, GOVERNANCE.md, CHAOSS metrics, GitHub Discussions, Kanban-not-Scrum)
- `executive-docs.agent.md` updated with OSS docs findings (CHANGELOG-first, MkDocs Material recommendation, docs-as-code CI gate, CONTRIBUTING standards)
- `executive-automator.agent.md` updated with dev workflow findings (pre-commit stack, Taskfile.dev, CI anti-patterns)
- `review.agent.md` updated with testing research findings (coverage gate check, pytest-mock pattern validation)
- `user-researcher.agent.md` scaffolded as new specialist agent (from product research H3)
**Depends on**: nothing (parallel to Phase 1)
**Gate**: Phase 4 does not start until all agent files are confirmed written

**Status**: ⬜ Not started

---

### Phase 3 — Guide Updates

**Agent**: Executive Docs
**Deliverables**:
- `docs/guides/testing.md` updated with testing research recommendations R1–R6
- `docs/guides/workflows.md` PM workflow section updated with Kanban/ADR/team topology findings
**Depends on**: nothing (parallel to Phase 1 and 2)
**Gate**: Phase 4 does not start until both guides are confirmed updated

**Status**: ⬜ Not started

---

### Phase 4 — Commit & Push

**Agent**: GitHub
**Deliverables**: all changes committed in two logical commits and pushed to origin
**Depends on**: Phases 1, 2, 3 all confirmed complete
**Gate**: Session closes when push is confirmed

**Status**: ⬜ Not started

---

## Acceptance Criteria

- [ ] `CHANGELOG.md` exists at root
- [ ] `README.md` has CI badge and TOC
- [ ] `CONTRIBUTING.md` has dev-env setup section and legibility/idempotency checklist
- [ ] `executive-pm.agent.md` references PM research findings
- [ ] `executive-docs.agent.md` references OSS docs findings
- [ ] `executive-automator.agent.md` references dev workflow findings
- [ ] `review.agent.md` references testing research findings
- [ ] `user-researcher.agent.md` exists in `.github/agents/`
- [ ] `docs/guides/testing.md` includes R1–R6 from testing research
- [ ] `docs/guides/workflows.md` PM section reflects Kanban + ADR findings
- [ ] All changes committed and pushed

---

## Source Research Docs

| Research Doc | Key Recommendations Used |
|---|---|
| `testing-tools-and-frameworks.md` | R1 (cov gate), R2 (pytest-subprocess), R3 (urlopen mock), R4 (mocker.patch), R5 (xdist) |
| `dev-workflow-automations.md` | R1 (pre-commit), R2 (ruff-format), R3 (Taskfile), R4 (double-run fix), R5 (.python-version) |
| `oss-documentation-best-practices.md` | R1 (CHANGELOG), R2 (README badge+TOC), R3 (CONTRIBUTING dev setup), R4 (MkDocs Material) |
| `pm-and-team-structures.md` | R1 (GitHub Projects), R2 (labels), R3 (issue templates), R4 (ADRs), R5 (GOVERNANCE.md), R6 (Discussions) |
| `product-research-and-design.md` | R1 (JTBD in scripts README), R2 (idempotency in CONTRIBUTING), R3 (pinned Discussion) |
| `comms-marketing-bizdev.md` | R1 (contributor funnel), R4 (GitHub Sponsors), R5 (VS Code artifact) |
