---
name: research-epic-planning
description: |
  Orchestrates the full research epic planning workflow: scope analysis, dependency mapping, phased workplan authoring, commit, and orientation prompt generation. USE FOR: creating a phased, multi-issue research workplan doc for any milestone or epic with ≥3 issues; producing a committed docs/plans/ doc that future sessions can execute without additional context; generating a copy-pastable orientation prompt for the first phase. DO NOT USE FOR: single-issue tasks (use deep-research-sprint directly); workplans without research issues (use workplan-scaffold instead); planning a single session rather than a multi-session milestone.
argument-hint: "milestone name or anchor issue number (e.g. 'Value Encoding & Fidelity' or '#85')"
---

# Research Epic Planning

This skill enacts the *Endogenous-First* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md): before planning begins, the agent reads all prior research, existing issues, and endogenous sources — so the plan is scaffolded from known context, not guessed. Epic planning discipline is governed by [`AGENTS.md`](../../../AGENTS.md) § Agent Communication → `docs/plans/`. Read both documents before deviating from any step.

**Canonical template**: [`docs/plans/2026-03-08-value-encoding-fidelity.md`](../../../docs/plans/2026-03-08-value-encoding-fidelity.md) — the reference implementation of a well-formed research epic workplan.

---

## 1. When to Use This Skill

Use this skill when the session involves:

| Criterion | Threshold |
|-----------|-----------|
| Number of related research issues | ≥ 3 |
| Issues span multiple execution phases or agent types | Yes |
| A milestone exists or is being created | Yes |
| Future sessions need to pick up phases independently | Yes |

For a single research issue, use the `deep-research-sprint` skill instead.

---

## 2. Pre-Planning: Endogenous Source Gathering

**Before writing a single line of the workplan**, run this sequence. Record findings in the scratchpad under `## Epic Planning — Scope Analysis`.

### 2.1 Read All Relevant Issues

```bash
# Get all open issues (with labels for effort/priority/type)
gh issue list --state open --json number,title,labels --limit 80

# Read the anchor issue or each milestone issue in full
gh issue view <ISSUE_NUMBER>
```

For each issue, note:
- Core research question or deliverable
- Stated dependencies (`Depends on:` lines in body)
- Effort label: `xs` / `s` / `m` / `l` / `xl`
- Type: `research` / `feature` / `chore` / `docs`

### 2.2 Survey Existing Research Docs

```bash
ls docs/research/
```

Identify which `docs/research/*.md` docs are the primary endogenous sources. Read the abstract/executive summary of each relevant doc. Do **not** bulk-read the full corpus — targeted retrieval only.

### 2.3 Check for Existing Workplans on This Topic

```bash
ls docs/plans/ | sort -r | head -10
```

If a related workplan already exists, read it. Do not create a duplicate; extend or update the existing plan instead.

---

## 3. Scope Analysis (Scratchpad)

Write a `## Epic Planning — Scope Analysis` section in the scratchpad answering:

1. **Core research question**: what is the single sentence that unifies all issues in this epic?
2. **Dependency graph**: which issues gate which others? List explicit `A → B` dependencies.
3. **Parallelisable vs. sequential**: which issues can be worked in parallel (no shared artifacts)?
4. **Deferred issues**: which issues have external prerequisites not yet met? List the blocking condition.
5. **Phase grouping**: natural clusters of 1–4 issues that share a common output type and can form one branch+PR.
6. **Primary endogenous sources**: which existing docs/research files are the foundational reading for this epic?
7. **Recommended execution order**: ordered list of phases with rationale.

Do not begin writing the workplan until this analysis is complete in the scratchpad.

---

## 4. Workplan Document

### 4.1 Scaffold the File

```bash
uv run python scripts/scaffold_workplan.py <brief-slug>
# Creates: docs/plans/YYYY-MM-DD-<brief-slug>.md
```

Then populate using `replace_string_in_file` (never heredocs — see [`AGENTS.md`](../../../AGENTS.md) guardrails).

### 4.2 Required Structure

The workplan must contain these sections in order:

```markdown
# Workplan: <Epic Title>

**Milestone**: [<milestone name>](<github milestone url>)
**Date seeded**: YYYY-MM-DD
**Status**: Active — open for pick-up
**Governing axiom**: <axiom name> — <brief rationale>
**Orchestrator**: Executive Orchestrator (any session picking up this milestone)

---

## Objective
One paragraph: core research question + name of the primary source doc to read before acting.

---

## Dependency Map
ASCII diagram showing issue numbers and → arrows for dependencies.
Mark parallel issues with the same indent level.

---

## Recommended Execution Order
One ### section per phase. Each phase section contains:
- **Issues**: table with columns: Issue # | Title | Type | Effort
- **Branch convention**: `feat/<slug>-phase-N-<name>`
- **Agent**: which executive or specialist agent leads this phase
- **Depends on**: prior phase(s) that must be complete first, or "none"
- **Gate deliverables**: checklist of committed outputs required before the phase closes
- **Review gate**: one sentence describing what the Review agent validates

---

## Deferred / Dependent Issues
Table: Issue # | Title | Deferred until (blocking condition)

---

## Acceptance Criteria (Milestone Close)
Checklist of conditions required to close the milestone entirely.

---

## Session Start Checklist
5–6 numbered steps. Any future session picking up a phase must complete these
before acting. Always includes:
1. Read the primary source doc named in the Objective
2. Read this workplan and note which phase is active
3. Check branch status: git log --oneline -5
4. Read today's scratchpad
5. State the governing axiom
6. Run uv run python scripts/prune_scratchpad.py --init
```

### 4.3 Phase Design Rules

- **One phase = one branch + PR**. Never combine phases that produce different output types (research doc vs. script vs. agent file) in a single branch unless they are trivially small.
- **Every domain phase must be followed by a Review gate** before the next domain phase begins. The Review gate is not a separate phase section — it is the `**Review gate:**` line at the end of each phase section.
- **Effort-size phases appropriately**: if a phase contains `effort:l` or `effort:xl` issues, split into sub-phases or flag that the phase may itself need an internal workplan.
- **Name the executing agent explicitly**: use the delegation routing table in [`AGENTS.md`](../../../AGENTS.md) to identify the correct specialist. Do not assign domain work to the Orchestrator.

---

## 5. Review Before Commit

Before committing the workplan, delegate to the **Review** agent:

> "Please review `docs/plans/<filename>.md` against the workplan structure requirements in the `research-epic-planning` skill. Verify: (1) all required sections present, (2) every phase has a Review gate, (3) dependency order is internally consistent, (4) deferred issues have explicit blocking conditions. Return APPROVED or REQUEST CHANGES."

Fix any REQUEST CHANGES feedback, then proceed to commit.

---

## 6. Commit the Workplan

```bash
git add docs/plans/<YYYY-MM-DD-slug>.md
git commit -m "docs(plans): seed <epic title> workplan

<2-5 bullet summary of phases>

Milestone: <github milestone url>
Governs issues: #N, #N, ..."
git push
git log --oneline -3  # verify
```

---

## 7. Generate the Orientation Prompt

After committing, produce a copy-pastable session continuation prompt with this structure:

```
@Executive Orchestrator Please start a new session on the <Epic Title> milestone.

**Governing axiom**: <axiom name>.
**Primary source**: `<path to primary research doc>` — read this before acting.
**Workplan**: `docs/plans/<YYYY-MM-DD-slug>.md` — the plan of record.
**Milestone**: <github milestone url>

Before doing anything else:
1. Run `uv run python scripts/prune_scratchpad.py --init` and read today's scratchpad
2. Read the workplan to identify which phase to start or resume
3. Read `<primary source doc>`
4. Write `## Session Start` naming the governing axiom and workplan as the primary endogenous source

**Recommended starting point**: Phase 1 — <Phase 1 name>
- Issue #N: <title> (effort: <label>)
- Issue #N: <title> (effort: <label>)

<One sentence on why Phase 1 is the right entry point.>
After Phase 1, run through the workplan phases in order — each phase's gate deliverables must be committed before the next phase begins.
```

---

## Guardrails

- **Never write the workplan before the scratchpad scope analysis is complete.** The dependency map in the workplan must be derived from the scope analysis, not invented.
- **Do not create a workplan for a milestone that already has one** — check `docs/plans/` first (Step 2.3).
- **Every phase must name a specific agent from the fleet** — not "an agent" or "the orchestrator". Use the delegation routing table.
- **Deferred issues must state a concrete unblocking condition** — "deferred until later" is not acceptable. Name the specific prerequisite issue or external event.
- **The orientation prompt is a required output** — without it, the workplan cannot be handed off cleanly to a new session.
