# Workplan: Sprint 19 Governance Docs

**Branch**: `main`
**Date**: 2026-03-18
**Orchestrator**: Executive Orchestrator

---

## Objective

Sprint 19 encodes governance conventions, documentation guides, and maturity models that support the broader RAG, MCP, and security work in Sprints 20–22. Primary deliverables: L0–L3 maturity ladder in AGENTS.md, ethical-values procurement rubric, civic-tech-patterns.md, and a suite of updated docs/guides/ entries.

---

## Phase Plan

### Phase 1 — Core Governance Framework ⬜

**Agent**: Executive Docs
**Deliverables**:
- `docs/agents` section in AGENTS.md updated with L0–L3 maturity ladder and diagnostic checklist (#362, #365)
- `docs(agents)`: accountability-vs-execution distinction for L3 PM (#367)
- `docs(governance)`: ethical-values procurement rubric for Review gate (#374)
- `docs(governance)`: three governance effectiveness metrics per sprint (#377)
- `docs(agents)`: update "when to ask" decision boundary with governance levels (#339)
- `docs(agents)`: add CMA report citation to Minimal-Posture principle (#341)

**Depends on**: nothing
**Gate**: Phase 1 Review does not start until deliverables committed
**Status**: ⬜ Not started

### Phase 1 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 1 committed
**Gate**: Phase 2 does not start until APPROVED
**Status**: ⬜ Not started

---

### Phase 2 — Guides & Reference Docs ⬜

**Agent**: Executive Docs
**Deliverables**:
- `docs(guides)`: Copilot ecosystem limitations guide (#340)
- `docs(guides)`: prompt-templates.md registry (#363)
- `docs(guides)`: value density metric (commit count vs SPACE) as primary L3 success signal (#366)
- `docs(guides)`: adversarial-prompting pattern for trend-adjacent strategy (#372)
- `docs(guides)`: SPACE framework metrics for LLM strategic output phases (#373)
- `docs(guides)`: batch AI output review into 30-min deep-work windows (#383)
- `docs(agents)`: platform binding separation pattern (#347)
- `docs(agents)`: Copilot collaboration phase expectations (#348)
- `docs(mcp)`: deep method-level API docs for MCP server and governance package (#326)
- `docs`: T4-without-T1 trap squash merge pattern documented (#328)

**Depends on**: Phase 1 Review APPROVED
**Gate**: Phase 2 Review does not start until deliverables committed
**Status**: ⬜ Not started

### Phase 2 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 2 committed
**Gate**: Phase 3 does not start until APPROVED
**Status**: ⬜ Not started

---

### Phase 3 — Process, Research & Encoding ✅

**Agent**: Executive Docs (docs items) + Executive Scripter (#364)
**Deliverables**:
- `chore(process)`: audit all 2×-interactive repetitions and encode as scripts (#364) — **Executive Scripter**
- `chore(process)`: token overage attribution protocol before session close (#370)
- `chore(process)`: protocol-stability gate before adopting new AI integrations (#371)
- `chore(process)`: quarterly values alignment review cycle (#375)
- `docs(agents)`: new-tools-woven-into-fleet encoding gate (#327)
- `docs(research)`: civic-tech-patterns.md registry (#378)
- `docs`: platform-migration.md + MANIFESTO.md Platform Infrastructure section (#295)
- `docs`: greenfield-decision.md — 5-criterion framework guide (#296)
- `chore(process)`: HGT ingestion sprint cadence + task-regime annotation (#298)
- `feat(packages)`: InferenceEndpoint abstraction outline (#382)

**Depends on**: Phase 2 Review APPROVED
**Gate**: Phase 3 Review does not start until deliverables committed
**Status**: ✅ Complete — commit 27d0efd

### Phase 3 Review — Review Gate ✅

**Agent**: Review
**Deliverables**: `## Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 3 committed
**Gate**: Session close does not proceed until APPROVED
**Status**: ✅ APPROVED

---

## Acceptance Criteria

- [ ] All phases complete and committed to `main`
- [ ] All 27 Sprint 19 issues have `Closes #NNN` in a merged PR or are marked done
- [ ] CI green after each phase commit
- [ ] Review agent APPROVED after every domain phase
- [ ] L0–L3 maturity ladder present in AGENTS.md with diagnostic checklist
- [ ] Ethical-values procurement rubric document exists in `docs/governance/`
- [ ] `docs/research/civic-tech-patterns.md` committed
- [ ] `scripts/` audit complete — all 2×-interactive tasks either scripted or documented as non-recurring

## PR Description Template

<!-- Copy to PR description when opening the PR -->

Closes #295, Closes #296, Closes #298, Closes #326, Closes #327, Closes #328, Closes #339, Closes #340, Closes #341, Closes #347, Closes #348, Closes #362, Closes #363, Closes #364, Closes #365, Closes #366, Closes #367, Closes #370, Closes #371, Closes #372, Closes #373, Closes #374, Closes #375, Closes #377, Closes #378, Closes #382, Closes #383
