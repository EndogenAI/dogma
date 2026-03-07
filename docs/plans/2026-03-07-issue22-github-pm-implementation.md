# Workplan: Issue #22 — GitHub PM Implementation (R1–R6)

**Branch**: `AccessiT3ch/issue22`
**Date**: 2026-03-07
**Orchestrator**: Executive Orchestrator
**Closes**: #22

---

## Objective

Implement the six remaining action items (R1–R6) from `docs/research/github-project-management.md` to complete issue #22. Research is complete; this session closes the implementation gap. Work covers: label taxonomy cleanup, GitHub Project wiring in issue templates, and verification of all automation workflows.

---

## Phase Plan

### Phase 1 — R1: Label Sync + Legacy Cleanup ⬜
**Agent**: Direct execution
**Deliverables**:
- `uv run python scripts/seed_labels.py` syncs GitHub labels to match `data/labels.yml`
- `uv run python scripts/seed_labels.py --delete-legacy` removes 10 GitHub default labels
- GitHub shows exactly 21 namespaced labels

**Depends on**: nothing
**Status**: ✅ Complete

---

### Phase 2 — R2/R3: Wire issue templates to GitHub Project ✅
**Agent**: Direct execution (file edits + gh CLI)
**Deliverables**:
- All 3 templates (research.yml, new-agent.yml, workflow-improvement.yml) have `projects: ["EndogenAI/1"]`
- Existing open issues added to project #1 via `gh project item-add`

**Depends on**: Phase 1 (labels must be clean before project wiring)
**Status**: ✅ Complete

---

### Phase 3 — Commit, Push, Close #22 ✅
**Agent**: Direct execution
**Deliverables**:
- Workplan + template changes committed and pushed
- Issue #22 closed with summary comment

**Depends on**: Phase 2
**Status**: ✅ Complete

---

## Acceptance Criteria

- [x] R1: 21 namespaced labels on GitHub, 10 legacy defaults deleted
- [x] R2: Project "EndogenAI Backlog" (#1) has Priority field; existing issues added
- [x] R3: All 3 YAML templates have `projects: ["EndogenAI/1"]`
- [x] R4: `.github/workflows/labeler.yml` + `.github/labeler.yml` exist and correct
- [x] R5: `.github/workflows/stale.yml` exists and correct
- [x] R6: `gh auth refresh -s project` documented in `CONTRIBUTING.md`
- [x] Issue #22 closed
