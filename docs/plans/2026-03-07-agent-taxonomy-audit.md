# Workplan: Agent Taxonomy Audit

**Branch**: `feature/skills-research-and-adaption` (or new branch)
**Date**: 2026-03-07
**Orchestrator**: Executive Orchestrator
**Linked issue**: #64

---

## Objective

Clarify the three-entity taxonomy of the VS Code customization stack — `AGENTS.md` (fleet constraints), `.agent.md` custom VS Code agent files (what to call them? cvAgents? personas? modes?), and `SKILL.md` skills — and where the lines between them should be drawn. Research the naming question, codify the taxonomy in documentation, then audit every existing `.agent.md` file and every `.github/skills/` file against the clarified definitions.

---

## Phase Plan

### Phase 1 — Targeted Research Sprint ✅
**Agent**: Executive Researcher
**Deliverables**:
- `docs/research/agent-taxonomy.md` (Status: Final) — commit `2a5c875` ✅
- Recommendation on naming: **"custom agents"** is the canonical VS Code term ✅
- Clarity on the AGENTS.md vs .agent.md vs SKILL.md boundary ✅
**Depends on**: nothing
**Gate**: Phase 2 does not start until research doc committed and Status: Final
**Status**: ✅ Complete — 2026-03-07

### Phase 2 — Documentation Update ✅
**Agent**: Executive Docs
**Deliverables**:
- `AGENTS.md`: six-layer chain + VS Code Customization Taxonomy table ✅
- `docs/guides/agents.md`: six-layer chain updated ✅
- `docs/decisions/ADR-006-agent-skills-adoption.md`: four→six layers updated ✅
**Depends on**: Phase 1
**Gate**: Phase 3 does not start until all three docs committed
**Status**: ✅ Complete — 2026-03-07 (commit `39881c7`)

### Phase 3 — Fleet Audit ⬜
**Agent**: Executive Fleet
**Deliverables**:
- Audit report for all `.github/agents/*.agent.md` files against clarified taxonomy
- Audit report for all `.github/skills/*/SKILL.md` files
- Any files that need updating: edited and committed
- validate_agent_files.py --all passing after all updates
**Depends on**: Phase 2 (needs canonical taxonomy to audit against)
**Gate**: Session close does not happen until all audit findings addressed
**Status**: ⬜ Not started

### Phase 4 — Commit & PR Update ⬜
**Agent**: GitHub (or Orchestrator direct action)
**Deliverables**:
- All changes committed and pushed
- PR body updated with new deliverables
- Issue checkboxes updated
**Depends on**: Phase 3
**Status**: ⬜ Not started

---

## Acceptance Criteria

- [ ] `docs/research/agent-taxonomy.md` (Status: Final) committed
- [ ] Naming for `.agent.md` VS Code custom agents is settled and consistent across all docs
- [ ] AGENTS.md boundary definitions updated
- [ ] `docs/guides/agents.md` updated
- [ ] Fleet audit complete — all `.agent.md` and `SKILL.md` files pass `validate_agent_files.py --all`
- [ ] All changes pushed, CI green
