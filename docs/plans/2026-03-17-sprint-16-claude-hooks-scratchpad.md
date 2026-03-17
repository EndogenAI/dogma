# Sprint 16 — Claude Code Hooks & Scratchpad Evolution

**Date**: 2026-03-17
**Branch**: `feat/sprint-15-mcp-scratchpad-arch` (continuing Sprint 15 PR #306)
**Sprint milestone**: Sprint 16 — Claude Code Hooks & Scratchpad Evolution

## Objective

Sprint 16 implements the highest-leverage quick wins from Sprint 15 research, prioritising Claude Code integration (the project's exclusive model) and scratchpad evolution. Four phases in this sprint:

1. **Governance encoding** — PR merge gate and Research Doc gate in AGENTS.md + Review agent
2. **Claude Code integration** — `CLAUDE.md` + `.claude/settings.json` hook config binding dogma scripts to lifecycle events; `claude -p` print mode policy
3. **Candidate C scratchpad** — YAML-fronted scratchpad frontmatter in `prune_scratchpad.py --init`
4. **(deferred to Sprint 17)** — #305 governance pre-commit bundle (v0.9.0) and #129 B' SQLite index

**Governing axiom**: [Programmatic-First (MANIFESTO.md)](../../MANIFESTO.md#programmatic-first-principle-cross-cutting) — encoding the phase-gate-sequence as a Claude Code lifecycle hook is a textbook Programmatic-First escalation: task done interactively many times → encode as a hook so every agent gets it automatically.

**Chicken-and-egg resolution**: Phase 1 (governance encoding, no research needed) precedes Phase 2 (implementation). No cross-cutting research is required — Sprint 15's `claude-code-cli-productivity-patterns.md` already provides the research grounding for all phases.

---

## Phases

### Phase 1 — Governance: PR Merge Gate + Review Agent Checklist

**Status**: ✅ Complete

**Agent**: Executive Orchestrator (direct — governance text encoding, < 5 min per file)
**Deliverables**:
- [x] AGENTS.md: `Research Doc PR Merge Gate` bullet added to sprint-close protocol (after "Track follow-up items as issues")
- [x] `.github/agents/review.agent.md`: New "D4 Research Documents" checklist section added before "Pre-commit Gate Compliance"
- [x] Sprint 16 milestone created (#16)
- [x] Issues seeded: #307 (Claude Code hooks), #308 (Candidate C), #309 (claude -p policy), #310 (hook config ADR)
- [x] Issues updated: #129 (B' schema + priority upgrade), #297 (Tasks API AC checkbox + research AC marked complete), #303 (Tasks API + .well-known AC checkboxes)

**Depends on**: Nothing
**Gate**: Phase 1 Review does not start until deliverables committed
**Acceptance**:
- [ ] `grep -n "Research Doc PR Merge Gate" AGENTS.md` returns a match
- [ ] `grep -n "D4 Research Documents" .github/agents/review.agent.md` returns a match
- [ ] 4 new issues created (verified via `gh issue list --milestone "Sprint 16..."`)

---

### Phase 1 Review — Review Gate

**Status**: ⬜ Not started

**Agent**: Review
**Deliverables**: `## Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 1 deliverables committed
**Gate**: Phase 2 does not start until Review returns APPROVED

---

### Phase 2 — Claude Code Integration: CLAUDE.md + .claude/settings.json + print mode policy

**Status**: ⬜ Not started

**Agent**: Executive Orchestrator (direct — creating new project-level config files)
**Deliverables**:
- [ ] `CLAUDE.md` (repo root) — project-level instructions for Claude Code
- [ ] `.claude/settings.json` — hook configuration (SessionStart, Stop, PreCompact, PostCompact, SessionEnd)
- [ ] `docs/guides/claude-code-integration.md` — setup guide (≤ 5 steps to activate)
- [ ] `claude -p` print mode policy added to AGENTS.md (Toolchain Reference section or new subsection)

**Closes**: #307 (hooks integration), #309 (print mode policy)
**Depends on**: Phase 1 Review APPROVED
**Gate**: Phase 2 Review does not start until deliverables committed
**Acceptance**:
- [ ] All #307 AC checkboxes satisfied
- [ ] All #309 AC checkboxes satisfied
- [ ] `uv run pre-commit run --all-files` exits 0

---

### Phase 2 Review — Review Gate

**Status**: ⬜ Not started

**Agent**: Review
**Deliverables**: `## Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 2 deliverables committed
**Gate**: Phase 3 does not start until Review returns APPROVED

---

### Phase 3 — Candidate C: YAML-Fronted Scratchpad Frontmatter

**Status**: ⬜ Not started

**Agent**: Executive Scripter (code change to `prune_scratchpad.py` requires scripting expertise + test update)
**Deliverables**:
- [ ] `scripts/prune_scratchpad.py` — `--init` writes YAML frontmatter block
- [ ] `scripts/validate_session_state.py` — Q1/Q5 use frontmatter, not heading-grep
- [ ] `tests/test_prune_scratchpad.py` — updated to cover frontmatter write + backward compat
- [ ] `pyproject.toml` — `python-frontmatter` added to deps (or stdlib yaml — confirm which)

**Closes**: #308 (Candidate C)
**Depends on**: Phase 2 Review APPROVED
**Gate**: Phase 3 Review does not start until deliverables committed
**Acceptance**:
- [ ] All #308 AC checkboxes satisfied
- [ ] `uv run pytest tests/test_prune_scratchpad.py --cov=scripts/prune_scratchpad.py --cov-fail-under=80` passes
- [ ] `uv run pre-commit run --all-files` exits 0

---

### Phase 3 Review — Review Gate

**Status**: ⬜ Not started

**Agent**: Review
**Deliverables**: `## Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 3 deliverables committed
**Gate**: Session close does not start until Review returns APPROVED

---

### Session Close — Commit & Push

**Status**: ⬜ Not started

**Agent**: GitHub (or Orchestrator direct after all Review gates)
**Deliverables**:
- [ ] All changes committed with conventional commit messages
- [ ] Branch pushed to `origin/feat/sprint-15-mcp-scratchpad-arch`
- [ ] PR #306 updated with `Closes #307, #308, #309` in body
- [ ] Issue progress comments posted on #307, #308, #309
- [ ] Session Summary written to scratchpad

**Deferred to Sprint 17**:
- #305 governance pre-commit bundle (v0.9.0) — was in Sprint 15 scope, deferred due to complexity
- #129 B' SQLite FTS5 index — large scripting task, separate branch warranted
- #310 hook config ADR — low priority, backlog

---

## Issue Tracking

| Issue | Title | Sprint 16 Phase | Status |
|---|---|---|---|
| #307 | Claude Code hooks integration | Phase 2 | ⬜ |
| #308 | Candidate C YAML frontmatter | Phase 3 | ⬜ |
| #309 | claude -p print mode policy | Phase 2 | ⬜ |
| #310 | Hook config ADR | Backlog | deferred |

## Sprint 15 Follow-up Tracking Verification

All Sprint 15 D4 research doc recommendations are now tracked:

| Recommendation | Source | Issue |
|---|---|---|
| Adopt B' SQLite-as-index | #304 Rec 1 | #129 (updated) |
| Candidate C YAML frontmatter | #304 Rec 3 | #308 (new) |
| Tasks API AC gate for #297 | #285 Rec 2 | #297 (updated) |
| Tasks API AC gate for #303 | #285 Rec 2 | #303 (updated) |
| `.well-known` discovery stub | #285 Rec 3 | #303 (updated) |
| Stateless-first MCP constraint | #285 Rec 1 | #303 (workplan) |
| Claude Code hooks integration | #284 Rec 2+3 | #307 (new) |
| `claude -p` print mode policy | #284 Rec 1 | #309 (new) |
| Hook config management ADR | #284 Open Q | #310 (new) |
| #297 MCP server gate on B' | #304 Impact | #297 (updated) |
| #303 MCP server gate on B' | mcp-a2a Rec 1 | #303 (updated) |
| Subagent architecture migration path | #284 Rec 4 | Intentionally deferred — wait for Claude Code/VS Code integration to stabilise |
| `--no-session-persistence` for CI | #284 Open Q | Absorbed into #307 AC |
| `memory: project` vs SQLite overlap | #284 Open Q | Absorbed into #129 B' scope |
