---
name: workplan-scaffold
description: |
  Encodes the pre-planning protocol from AGENTS.md: create a workplan doc before any multi-phase session execution, scaffold it with scripts/scaffold_workplan.py, and commit it before Phase 1 runs. USE FOR: any session with ≥3 phases or ≥2 agent delegations; any session spanning more than one day; creating an auditable plan history in git. DO NOT USE FOR: single-phase tasks with no delegation; quick one-off commits with no sub-agent orchestration.
argument-hint: "slug for the workplan (e.g. add-feature-x)"
---

# Workplan Scaffold

This skill enacts the *Algorithms Before Tokens* axiom from [`MANIFESTO.md`](../../MANIFESTO.md): the plan is encoded once as a committed document and referenced by every subsequent delegation — never re-derived from scratch mid-session. Workplan discipline is governed by [`AGENTS.md`](../../AGENTS.md) § Agent Communication → `docs/plans/`. When this skill and those documents conflict, the primary documents take precedence.

---

## 1. When to Create a Workplan

Create a workplan **before executing any phase** when the session meets one or more of these criteria:

| Criterion | Threshold |
|-----------|-----------|
| Number of phases | ≥ 3 |
| Number of agent delegations | ≥ 2 |
| Session spans multiple calendar days | Yes |
| Any change that renames or restructures committed files | Yes |

For single-phase, single-agent tasks with low risk, the scratchpad `## Session Start` section is sufficient. The workplan is the plan of record; the scratchpad is live inter-agent memory.

---

## 2. Scaffold the Workplan

Use the scaffold script to create a correctly named, pre-filled workplan:

```bash
uv run python scripts/scaffold_workplan.py <brief-slug>
# Example:
uv run python scripts/scaffold_workplan.py add-research-skill
# Creates: docs/plans/2026-03-07-add-research-skill.md
```

**Naming convention**: `docs/plans/YYYY-MM-DD-<brief-slug>.md` — date-first for chronological sorting.

If the file already exists, the script exits with an error rather than overwriting. Use the existing file.

The canonical template is [`docs/plans/2026-03-06-formalize-workflows.md`](../../docs/plans/2026-03-06-formalize-workflows.md).

---

## 3. Required Workplan Structure

Every committed workplan must include the following sections:

```markdown
# Workplan: <Title>

**Branch**: `<branch>`
**Date**: YYYY-MM-DD
**Orchestrator**: <Agent Name>

---

## Objective

<!-- One paragraph: what this session accomplishes and why -->

---

## Phase Plan

### Phase 1 — <Name> ⬜
**Agent**: <Agent Name>
**Deliverables**: <list>
**Depends on**: —
**Gate**: <acceptance test for this phase>
**Status**: ⬜ pending

### Phase 2 — <Name> ⬜
...

---

## Acceptance Criteria

- [ ] <criterion 1>
- [ ] <criterion 2>
```

**Status markers**: `⬜` pending, `✅` done. Update in-place as phases complete and commit the update.

---

## 4. Commit Before Phase 1

The workplan **must be committed before Phase 1 executes**. This creates an auditable plan history in git that is independent of the ephemeral `.tmp/` scratchpad.

```bash
git add docs/plans/YYYY-MM-DD-<slug>.md
git commit -m "docs(plans): add workplan for <slug>"
```

**Why commit first**: If the session is interrupted or compacted, the plan survives in git history. Uncommitted plans are lost on context reset.

---

## 5. Mirror in Scratchpad

After committing the workplan, write an `## Orchestration Plan` section in the active scratchpad (`.tmp/<branch-slug>/<today>.md`) that mirrors the phase list and links to the committed file. This gives delegated agents a single orientation point:

```markdown
## Orchestration Plan

Workplan: docs/plans/YYYY-MM-DD-<slug>.md

| Phase | Agent | Status |
|-------|-------|--------|
| 1 — <Name> | <Agent> | ⬜ |
| 2 — <Name> | <Agent> | ⬜ |
```

---

## 6. Update as Phases Complete

After each phase, update both the workplan and the scratchpad mirror:

1. In `docs/plans/YYYY-MM-DD-<slug>.md`: change `⬜` to `✅` for the completed phase.
2. Commit the update: `git commit -m "docs(plans): mark phase N complete — <slug>"`.
3. Update the scratchpad `## Orchestration Plan` table.

---

## 7. Session Self-Loop Handoff

After writing and committing the workplan, write the following line in the scratchpad before delegating Phase 1:

```
✓ Plan reviewed — begin execution
```

This serves as the signal that the planning gate is closed and execution may start.

---

## Guardrails

- **Never start Phase 1 without a committed workplan** when the session meets the threshold criteria above.
- **Never use heredoc or terminal writes for workplan content** — always use `create_file` or `replace_string_in_file` tools.
- Do not re-derive the plan interactively mid-session; reference the committed workplan file.
