# Workplan: GitHub PM Codification, Issue Hygiene & Context Compaction

**Branch**: `feat/implement-research-findings`
**Date**: 2026-03-07
**Orchestrator**: Executive Orchestrator

---

## Objective

Apply the completed GitHub PM research synthesis to documentation and agent updates. Organize all open GitHub issues into thematic milestones. Ensure OPEN_RESEARCH.md is fully bidirectionally linked to issues, with completed research items moved to a footer section. Research and document best practices for VS Code Copilot's programmatic context compaction feature, encoding the best practices into `docs/guides/session-management.md` and relevant AGENTS.md files.

---

## Phase Plan

### Phase 1 — GitHub PM Codification ⬜
**Agent**: Executive Docs + Executive Fleet (via subagent delegation)
**Deliverables**:
- `docs/guides/github-workflow.md` — new guide summarising actionable GitHub PM patterns from the synthesis
- `.github/agents/executive-pm.agent.md` — updated Endogenous Sources list to reference `docs/research/github-project-management.md`
- Root `AGENTS.md` — GitHub-specific guardrail (verify-after-act for `gh` commands; label taxonomy conventions)

**Depends on**: `docs/research/github-project-management.md` (committed ✅)
**Status**: ✅ Complete

---

### Phase 2 — GitHub Issue Hygiene + Milestones ⬜
**Agent**: Orchestrator (direct `gh` operations)
**Deliverables**:
- 3 thematic milestones created: "Local Compute Foundation", "Methodology & Knowledge Infrastructure", "Research & Documentation Sprint"
- Issues #16–21 closed (research deliverables confirmed)
- Issue #7 body corrected (currently has wrong body — shows LLM tier strategy instead of async process handling)
- New issue: GitHub PM Sprint (replaces TBD reference in OPEN_RESEARCH.md)
- New issue: VS Code Agent Format Sprint (replaces TBD reference in OPEN_RESEARCH.md)
- New issue: Context Compaction Best Practices Research
- All open issues assigned to appropriate milestone

**Depends on**: nothing (can run in parallel with Phase 1)
**Status**: ✅ Complete

---

### Phase 3 — OPEN_RESEARCH.md Sync ⬜
**Agent**: Orchestrator (direct file edit)
**Deliverables**:
- All open research items updated with real GitHub issue numbers (no TBD)
- Completed sprint entries (#16–21, agent fleet, XML format, GitHub PM) moved to `## Completed Research` footer section
- Open items (#1–5, #7, #13–14) remain in main body with correct issue links

**Depends on**: Phase 2 (need final issue numbers from new issues created)
**Status**: ✅ Complete

---

### Phase 4 — Context Compaction Research + Documentation ⬜
**Agent**: Research (inline) + Executive Docs (guide update)
**Deliverables**:
- `docs/guides/session-management.md` — new "Context Compaction" section documenting VS Code Copilot compaction behaviour, best practices for content preservation, and the scratchpad-as-durable-record principle
- `AGENTS.md` — compaction-aware writing guidelines encoded as a guardrail
- `docs/research/` — optionally a new synthesis doc `context-compaction-best-practices.md` if research surface warrants it

**Depends on**: nothing (independent research track)
**Status**: ✅ Complete

---

### Phase 5 — Commit & Push ⬜
**Agent**: GitHub agent
**Deliverables**:
- All changes committed with Conventional Commit messages
- Branch pushed to origin; PR #15 up to date

**Depends on**: Phases 1–4
**Status**: ✅ Complete

---

## Acceptance Criteria

- [ ] `docs/guides/github-workflow.md` exists and is committed
- [ ] `executive-pm.agent.md` references `github-project-management.md` synthesis
- [ ] 3 milestones exist on the repo with all open issues assigned
- [ ] Issues #16–21 closed
- [ ] Issue #7 body corrected
- [ ] 3 new issues created (GitHub PM sprint, VS Code format sprint, context compaction)
- [ ] OPEN_RESEARCH.md has no TBD issue numbers; completed items in footer
- [ ] `session-management.md` has context compaction section
- [ ] All changes pushed to feat/implement-research-findings
