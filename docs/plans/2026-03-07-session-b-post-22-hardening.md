# Workplan: Session B — Post-#22 Hardening & Research Kicks

**Branch**: `AccessiT3ch/issue22`
**Date**: 2026-03-07
**Orchestrator**: Executive Orchestrator
**PR**: #28

---

## Objective

Seven-item session triggered after closing #22: fix CI on PR #28 and respond to Copilot inline review comments; strengthen file-writing/heredoc guardrail across all 14 agent files; update OPEN_RESEARCH.md and assess automation; add CI-gate check to workflow SOPs; start two new research tracks (Copilot programmatic review + GitHub-as-memory substrate); audit repo settings; and queue all follow-up issues. Everything lands on branch `AccessiT3ch/issue22` → PR #28.

---

## Phase Plan

### Phase 1 — Fix CI + Respond to Copilot PR Comments ⬜
**Agent**: Direct execution
**Deliverables**:
- Atlassian URL added to `.lycheeignore` (lychee 202 error)
- `docs/plans/2026-03-07-issue22-github-pm-implementation.md`: branch corrected, phase statuses → ✅, acceptance criteria checked
- `CONTRIBUTING.md`: remove seed_labels from project-scope bullet (scope not needed)
- Respond to all 4 Copilot inline comments on PR #28

**Depends on**: nothing
**Status**: Not started

---

### Phase 2 — Start Research Workflows (parallel) ⬜
**Agent**: Executive Researcher (×2 in sequence)
**Deliverables**:
- GitHub issue #29: "Research: Programmatic Copilot Review Requests"
- GitHub issue #30: "Research: GitHub as Episodic & Long-term Memory Substrate"
- Both issues tracked in project #1
- Research sessions initiated or queued

**Depends on**: nothing
**Status**: Not started

---

### Phase 3 — Strengthen Heredoc/File-Writing Guardrail in Agent Fleet ⬜
**Agent**: Direct execution (file edits across all 14 .agent.md files)
**Deliverables**:
- All 14 `.agent.md` files have prominent `<file-writing>` constraint block near top of `<constraints>` section
- Block includes: explicit failure mode, decision table, worked example of correct approach
- Root `AGENTS.md` guardrail updated with "why agents keep getting this wrong" framing

**Depends on**: nothing (parallelisable with Phase 2)
**Status**: Not started

---

### Phase 4 — CI Gate Encoding in Workflows + OPEN_RESEARCH.md ⬜
**Agent**: Executive Docs (delegated)
**Deliverables**:
- `docs/guides/workflows.md`: CI-gate-check added as explicit gate criterion before PR review step
- `AGENTS.md`: CI-passing added to verify-after-act / commit discipline sections
- `docs/research/OPEN_RESEARCH.md`: GitHub PM sprint marked resolved; new research topics added (items 5 & 7)
- Automation assessment: is auto-update of OPEN_RESEARCH.md feasible? → issue opened if warranted

**Depends on**: Phase 2 (need issue numbers for OPEN_RESEARCH.md)
**Status**: Not started

---

### Phase 5 — Repo Settings Audit ⬜
**Agent**: Direct execution (gh API queries only — audit + report, no changes)
**Deliverables**:
- Settings audit report in scratchpad covering: branch protection, required reviews, status checks, merge strategies, Dependabot, secret scanning
- GitHub issue opened with findings and recommendations
- Added to project #1

**Depends on**: nothing (parallelisable)
**Status**: Not started

---

### Phase 6 — Commit, Push, Re-request Review ⬜
**Agent**: Direct execution
**Deliverables**:
- All changes committed to `AccessiT3ch/issue22`
- Pushed to origin
- CI passes (lychee fix in Phase 1 should resolve)
- Re-request Copilot PR review on #28

**Depends on**: Phases 1–5 all complete and committed
**Status**: Not started

---

## Acceptance Criteria

- [ ] Phase 1: CI green on PR #28; all 4 Copilot comments addressed
- [ ] Phase 2: 2 new research issues created and in project
- [ ] Phase 3: All 14 agent files have file-writing guardrail
- [ ] Phase 4: CI gate in workflows.md; OPEN_RESEARCH.md updated
- [ ] Phase 5: Repo settings audit issue opened
- [ ] Phase 6: PR #28 CI green; Copilot review re-requested
