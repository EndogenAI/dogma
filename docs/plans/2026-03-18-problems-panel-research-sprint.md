---
governs: [problems-panel-cleanup]
sprint: mini-sprint-389
issue: 389
branch: triage/problems-panel-cleanup
---

# Problems Panel Cleanup — Mini Sprint (Issue #389)

**Date**: 2026-03-18  
**Branch**: `triage/problems-panel-cleanup`  
**Objective**: Research VS Code Problems panel error categories A/B/C/D (issue #389) and implement all known fixes in a single mini sprint.

---

## Context

The branch currently has ~327 Problems panel errors in 3 categories:
- **Category A** (38 errors): `Attribute 'governs' is not supported` — Copilot Chat `prompts-diagnostics-provider` internal schema rejects the `governs:` frontmatter key
- **Category B** (8 errors): `Unknown tool 'dogma-governance/*'` — MCP tool names rejected when server not running
- **Category C** (281 errors — regression): `/`-rooted links in `.github/agents/` and `.github/skills/` resolve to filesystem root on macOS, not workspace root. A stash (`stash@{0}`) with the reversion already exists.

**Chicken-and-egg decision**: Research is needed for Categories A and B before we can decide whether to configure them away or accept them. Category C fix is known and ready to apply. Research is Phase 1; Category C implementation can proceed in Phase 2 regardless of research outcome.

---

## Phases

### Phase 1 — Research (RQ-A, B, C, D)

**Agent**: Executive Researcher → Research Scout → Synthesizer → Reviewer → Archivist  
**Deliverables**: `docs/research/vscode-problems-panel-diagnostics.md` committed, Status: Final  
**Depends on**: nothing  
**Gate**: Phase 1 Review does not start until deliverable is committed  
**Status**: ⬜ Not started

Research questions:
- **RQ-A**: Can Copilot Chat `prompts-diagnostics-provider` be extended/configured to accept `governs:`?
- **RQ-B**: Can MCP tool names be validated statically without a running server?
- **RQ-C**: What VS Code settings legitimately suppress diagnostics from a specific provider?
- **RQ-D**: What is the exact resolution behaviour of `prompts-diagnostics-provider` for `../../` vs `/`-rooted paths? (Partly answered: `/`-rooted = filesystem root on macOS)

### Phase 1 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 1 Review Output` in scratchpad, verdict: APPROVED  
**Depends on**: Phase 1 deliverable committed  
**Gate**: Phase 2 does not start until APPROVED  
**Status**: ⬜ Not started

### Phase 2 — Implementation

**Agent**: Executive Docs (convention doc updates) + direct implementation for pre-commit hook + stash pop  
**Deliverables**:
- [ ] `no-relative-traversal-in-agent-files` hook inverted (block `/`-rooted paths, not `../../`) or removed
- [ ] `stash@{0}` popped and committed (281 link reversions: 36 agents + 18 skills + 1 doc)
- [ ] `.github/skills/agent-file-authoring/SKILL.md` § Link Path Rule updated
- [ ] `.github/skills/skill-authoring/SKILL.md` § Link Path Rule updated
- [ ] `AGENTS.md` § Agent authoring conventions updated (remove `/`-rooted path carve-out)
- [ ] `docs/guides/agents.md` line 238 updated
- [ ] Any configuration fix from Phase 1 research applied to `.vscode/settings.json` or `.vscode/agent-frontmatter.schema.json`
- [ ] If no fix for Category A/B: note added to `docs/guides/agents.md` explaining expected IDE warnings are non-blocking

**Depends on**: Phase 1 Review APPROVED  
**Gate**: Phase 2 Review does not start until all deliverables committed  
**Status**: ⬜ Not started

### Phase 2 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 2 Review Output` in scratchpad, verdict: APPROVED  
**Depends on**: Phase 2 deliverables committed  
**Gate**: Phase 3 does not start until APPROVED  
**Status**: ⬜ Not started

### Phase 3 — Push + Issue Close

**Agent**: GitHub  
**Deliverables**: Branch pushed, PR updated, issue #389 acceptance criteria checked  
**Depends on**: Phase 2 Review APPROVED  
**Status**: ⬜ Not started

---

## Acceptance Criteria (from issue #389)

- [ ] Scout report produced with ≥ 3 external sources per research question (A, B, C)
- [ ] Deep-dive synthesis doc committed to `docs/research/` as Status: Final covering all three RQs (+ RQ-D)
- [ ] Clear recommendation in the synthesis doc: **accept as permanent** OR **fix path**
- [ ] If a configuration-based fix is found: tested and committed to `.vscode/settings.json` or `.vscode/agent-frontmatter.schema.json`
- [ ] If no fix exists: synthesis doc documents the missing VS Code/Copilot API; note added to `docs/guides/agents.md`
- [ ] Category C (281 link regression errors) eliminated via stash pop + hook fix + convention doc updates
