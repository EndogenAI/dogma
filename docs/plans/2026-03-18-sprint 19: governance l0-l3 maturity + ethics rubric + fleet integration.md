# Workplan: Sprint 19: Governance L0 L3 Maturity + Ethics Rubric + Fleet Integration

**Branch**: `main`
**Date**: 2026-03-18
**Orchestrator**: Executive Orchestrator

---

## Objective

Encode governance maturity lanes into AGENTS.md by integrating three research-backed enhancements: L0–L3 adoption ladder (maps ad-hoc → scripted → skill → enforced), ethical values procurement rubric (formalizes tool adoption decisions), and fleet integration protocols (ensures new governance tools surface to all agents at session start). Closes #362, #374, #327.

---

## Phase Plan

### Phase 1A — Governance Docs Update ⬜
**Agent**: Executive Docs
**Deliverables**:
- `AGENTS.md` § Agent Fleet Maturity (L0–L3) — new section documenting four levels with gates
- `AGENTS.md` § Ethical Values Procurement Rubric — new subsection in "When to Ask vs. Proceed" section
- `AGENTS.md` § Fleet Integration Checklist — Phase 5 mandatory deliverable for new tool shipping
- `scripts/scaffold_workplan.py` Phase 5 template — updated to include fleet-integration deliverable checkboxes
- `scripts/check_fleet_integration.py` — new script for CI gate (checks new files → AGENTS.md cross-reference)
- `.github/agents/review.agent.md` — workplan validation criterion 8 added (fleet integration check)
- `docs/research/ramp-l0l3-framework.md` linked in all new AGENTS.md sections
- `docs/research/civic-ai-governance.md` linked in ethical-values section

**Depends on**: nothing
**CI**: ruff check, AGENTS.md audit, validate_agent_files.py
**Status**: Not started

---

### Phase 1A Review — Review Gate ⏳
**Agent**: Review
**Deliverables**: `## Phase 1A Review Output` — verdict: APPROVED or REQUEST CHANGES
**Depends on**: Phase 1A deliverables committed
**Gate**: Phase 1B does not begin until Phase 1A Review returns APPROVED
**Status**: Not started

---

### Phase 1B — Issue Close-Out ⬜
**Agent**: Executive PM / GitHub
**Deliverables**:
- Issue #362 body checkboxes updated & issue closed
- Issue #374 body checkboxes updated & issue closed
- Issue #327 body checkboxes updated & issue closed
- Pull request created for main if not yet open

**Depends on**: Phase 1A Review APPROVED
**Status**: Not started

---

## Acceptance Criteria

- [ ] All three issues (#362, #374, #327) closed with completed checkboxes
- [ ] All changes committed to main with Conventional Commits format
- [ ] `AGENTS.md` updated with L0–L3 ladder, ethics rubric, fleet integration
- [ ] New script `check_fleet_integration.py` passes tests (>80% coverage)
- [ ] Review agent validates workplan criterion 8 (fleet integration check)
- [ ] All pushes confirmed with `git log --oneline -5` verification
