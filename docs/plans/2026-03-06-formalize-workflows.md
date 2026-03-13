# Workplan: Formalize Workflows — Apply Research Learnings

**Branch**: `feat/issue-2-formalize-workflows`  
**PR**: [#11 — docs: formalize agent workflows, research fleet, and scaffold tooling](https://github.com/EndogenAI/dogma/pull/11)  
**Date**: 2026-03-06  
**Orchestrator**: Executive Orchestrator  

---

## Objective

Incorporate the findings from `docs/research/agentic-research-flows.md` (22-source synthesis, 2026-03-06) into all three layers of the project: documentation, agent files, and scripting/tooling.

---

## Phase Plan

### Phase 1 — Deepen MANIFESTO.md with Empirical Grounding ✅
**Agent**: Executive Docs  
**Deliverables**:
- Empirical basis paragraphs added to three axioms: "Compress Context, Not Content", "Isolate Invocations, Parallelize Safely", "Validate & Gate, Always"
- Each paragraph cites the specific source confirming the axiom empirically

**Commit**: `de20bff`  
**Status**: Complete

---

### Phase 2 — Documentation Updates ✅
**Agent**: Direct (Orchestrator)  
**Deliverables**:
- `docs/guides/session-management.md` — new "Design Rationale" section explaining the scratchpad as implementing Anthropic's lightweight context handoff pattern; write-discipline framed as non-optional
- `docs/research/OPEN_RESEARCH.md` — item 8 added: XML-Tagged Agent Instruction Format (priority: Very High), with 5 resource targets and 5 programmatic deliverables (migrate script, validate script, scaffold update, schema docs, guide update)

**Commit**: `699b6c3`  
**Status**: Complete

---

### Phase 3 — GitHub Issues ✅
**Agent**: Direct (gh CLI)  
**Deliverables**:
- Issue [#12 — [Research] XML-Tagged Agent Instruction Format](https://github.com/EndogenAI/dogma/issues/12) — Very High priority; migrate/validate/scaffold tooling required
- Issue [#13 — [Research] Episodic and Experiential Memory for Agent Sessions](https://github.com/EndogenAI/dogma/issues/13) — Low priority; deferred until #1 resolved
- Issue [#14 — [Research] AIGNE AFS Context Governance Layer Evaluation](https://github.com/EndogenAI/dogma/issues/14) — Medium priority; deferred until #1 resolved

**Status**: Complete

---

### Phase 4 — Extend `generate_agent_manifest.py` ✅
**Agent**: Executive Scripter  
**Deliverables**:
- `posture` field derived from tool set: `readonly` / `creator` / `full`
- `capabilities` list: 2–5 lowercase-hyphenated tags per agent extracted from description
- `handoffs` list: agent names from frontmatter `handoffs:` block
- `scripts/README.md` updated with new field documentation

**Commit**: `a624dc5`  
**Status**: Complete

---

### Phase 5 — Agent Output Examples Discipline Pass ✅
**Agent**: Executive Docs  
**Deliverables**:
- `## Output Examples` section added to ALL 15 agent files in `.github/agents/`
- Position: after `## Completion Criteria`, before `## Guardrails`
- Each section contains one annotated "good output" example appropriate to the agent's domain

**Target files** (15 total):
1. `executive-orchestrator.agent.md`
2. `executive-planner.agent.md`
3. `executive-docs.agent.md`
4. `executive-scripter.agent.md`
5. `executive-automator.agent.md`
6. `executive-fleet.agent.md`
7. `executive-pm.agent.md`
8. `executive-researcher.agent.md`
9. `research-scout.agent.md`
10. `research-synthesizer.agent.md`
11. `research-reviewer.agent.md`
12. `research-archivist.agent.md`
13. `review.agent.md`
14. `github.agent.md`
15. `executive-planner.agent.md` _(deduplicated — 14 unique files)_

**Commit**: `748a3e3`  
**Status**: Complete

---

### Phase 6 — Review & Final Push ✅
**Agent**: Review → GitHub  
**Deliverables**:
- All changes reviewed: 19 PASS, 3 WARN (non-blocking), 0 blockers
- Warnings addressed: `docs/AGENTS.md` table updated; `executive-fleet.agent.md` example corrected
- All commits verified Conventional Commits compliant
- All commits pushed to `origin feat/issue-2-formalize-workflows`

**Commits (this session)**: `de20bff`, `699b6c3`, `a624dc5`, `cbc2eca`, `748a3e3`, `[final]`  
**Depends on**: Phase 5  
**Status**: Complete

---

## Acceptance Criteria

- [x] All 6 phases complete and committed
- [x] MANIFESTO.md has empirical basis on all three cited axioms
- [x] `session-management.md` explains the Design Rationale for scratchpad convention
- [x] `OPEN_RESEARCH.md` item 8 present (XML format, Very High)
- [x] GitHub issues #12, #13, #14 open with full research specs
- [x] `generate_agent_manifest.py` emits `posture`, `capabilities`, `handoffs` for all 15 agents
- [x] All 14 agent files have `## Output Examples` section
- [x] All changes pushed and PR #11 is up to date
