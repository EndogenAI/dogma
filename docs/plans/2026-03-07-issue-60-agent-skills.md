# Workplan: Issue #60 — Agent Skills Research & Integration

**Branch**: `main`
**Date**: 2026-03-07
**Orchestrator**: Executive Orchestrator
**Issue**: [#60](https://github.com/EndogenAI/dogma/issues/60)

---

## Objective

Research Agent Skills as a VS Code / open-standard primitive (agentskills.io),
analyse how they complement the existing `.agent.md` fleet, and produce a full
integration strategy: synthesis doc, ADR, first SKILL.md files, CI validation
extension, guide updates, and a follow-on implementation issue. Governed by the
*Algorithms Before Tokens* axiom: skills encode once, the fleet inherits across
all sessions and tools.

---

## Phase Plan

### Phase 1 — Research Synthesis ⬜
**Agent**: Executive Researcher
**Deliverables**:
- `docs/research/agent-skills-integration.md` (Status: Final)
- Seed sources fetched and cached (`.cache/sources/`)
- Issue #60 Q1–Q7 answered in synthesis

**Depends on**: nothing
**Status**: Not started

---

### Phase 2 — ADR-006 ⬜
**Agent**: Executive Docs
**Deliverables**:
- `docs/decisions/ADR-006-agent-skills-adoption.md`

**Depends on**: Phase 1 synthesis committed
**Status**: Not started

---

### Phase 3 — Skills Scaffold + CI Extension ⬜
**Agent**: Executive Scripter (CI) + Executive Docs (SKILL.md files)
**Deliverables**:
- `.github/skills/session-management/SKILL.md`
- `.github/skills/conventional-commit/SKILL.md`
- `.github/skills/validate-before-commit/SKILL.md`
- `scripts/validate_agent_files.py` extended to validate SKILL.md files
- Tests updated for new validation logic

**Depends on**: Phase 2 ADR committed
**Status**: Not started

---

### Phase 4 — Documentation Updates ⬜
**Agent**: Executive Docs
**Deliverables**:
- `docs/guides/agents.md` — skills section added
- `AGENTS.md` — skills conventions added

**Depends on**: Phase 3
**Status**: Not started

---

### Phase 5 — Follow-on Implementation Issue + Close ⬜
**Agent**: Executive PM
**Deliverables**:
- New GitHub issue: "Implement remaining Tier 1+2 Skills"
- Issue #60 closed with summary comment

**Depends on**: Phase 4
**Status**: Not started

---

## Acceptance Criteria

- [ ] `docs/research/agent-skills-integration.md` committed (Status: Final)
- [ ] `docs/decisions/ADR-006-agent-skills-adoption.md` committed
- [ ] At least 2 SKILL.md files committed to `.github/skills/`
- [ ] `validate_agent_files.py` extended; tests pass
- [ ] `docs/guides/agents.md` skills section present
- [ ] `AGENTS.md` skills conventions present
- [ ] Follow-on implementation issue filed
- [ ] Issue #60 closed with progress comment
