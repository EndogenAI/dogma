---
name: delegation-routing
description: |
  Encodes the Delegation Decision Gate routing table for executive-tier agents: which specialist agent handles each task domain, and when an agent may act directly instead of delegating.
  USE FOR: deciding which agent to delegate a phase to before execution begins; verifying a planned direct action is on the "act directly" list; onboarding a new executive-tier agent's delegation posture.
  DO NOT USE FOR: orchestrating the per-phase checkpoint sequence (use phase-gate-sequence); authoring agent files (use agent-file-authoring); session start/close lifecycle (use session-management).
argument-hint: "task domain description (e.g. 'write research synthesis', 'audit agent fleet')"
tier: Foundation
type: automation
effort: s
applies-to:
  - Executive Orchestrator
  - Executive Researcher
  - Executive Planner
status: active
---

# Delegation Routing

This skill enacts the *Algorithms-Before-Tokens* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md): a static routing table replaces per-session re-derivation of which agent handles which domain, eliminating redundant token burn and preventing scope drift into direct execution.

---

## Endogenous Sources

- **Governing axiom**: Axiom 2 — *Algorithms Before Tokens* — deterministic lookup over interactive re-derivation
- **GitHub issue**: [#79 — Skills as Decision Codifiers](https://github.com/EndogenAI/Workflows/issues/79)
- **Agents that use this skill**: Executive Orchestrator, Executive Researcher, Executive Planner
- **Foundation docs**:
  - [`AGENTS.md`](../../../AGENTS.md) — guiding constraints; Minimal Posture, Programmatic-First, delegation-first
  - [`executive-orchestrator.agent.md`](../../../.github/agents/executive-orchestrator.agent.md) — canonical Delegation Decision Gate (lines 137–165)

---

## Workflow

**Step 1 — Identify the task domain** from the incoming work item or phase description.

**Step 2 — Consult the routing table:**

| Task domain | Delegate to |
|-------------|-------------|
| Research, source gathering | Executive Researcher → Research Scout fleet |
| Documentation writing / editing | Executive Docs |
| Scripting, automation design | Executive Scripter, Executive Automator |
| Fleet agent authoring / audit | Executive Fleet |
| Release coordination, versioning | Release Manager |
| Issue triage, labels, milestones | Issue Triage, Executive PM |
| CI health, test coverage gaps | CI Monitor, Test Coordinator |
| Environment / dependency audit | Env Validator |
| Security threat modelling | Security Researcher |
| Docs compliance audit | Docs Linter |
| Model / cost optimisation | LLM Cost Optimizer |
| Community health, DevRel | Community Pulse, DevRel Strategist |

**Step 3 — Verify it is not on the "Act directly" list.** An agent may act directly only for:

- Reading files to confirm a deliverable exists
- Running `git status`, `git log --oneline`, `gh pr view`, `gh issue view`
- Writing scratchpad entries and workplan status updates
- Running `git add/commit/push` after a subagent returns
- Running `prune_scratchpad.py` or the pre-compact sequence

**If the work does not appear in the "Act directly" list, delegate it.**

**Step 4 — Form a narrow delegation prompt.** Outbound prompts must be task-scoped, not bulk session context. Inbound returns must be ≤ 2,000 tokens (Focus-on-Descent / Compression-on-Ascent — see [`AGENTS.md`](../../../AGENTS.md) § Agent Communication).

---

## Completion Criteria

An agent has applied this skill correctly when:

- [ ] The task domain matches exactly one row in the routing table, or is confirmed to be on the "Act directly" list.
- [ ] No substantive domain work was performed directly when a specialist agent exists for it.
- [ ] The outbound delegation prompt is narrow and task-scoped.
- [ ] Phases are delegated one at a time — no batching.
