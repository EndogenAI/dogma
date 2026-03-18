---
name: sprint-planning
description: |
  Reviews all open GitHub issues, clusters them by theme and priority, proposes a
  coherent next sprint with selected issues, creates or updates the sprint milestone,
  and scaffolds a workplan in docs/plans/. USE FOR: end-of-sprint planning sessions;
  when the backlog has grown and needs a structured next-sprint proposal; before any
  multi-week work commitment. DO NOT USE FOR: triaging individual new issues (use
  Issue Triage agent); planning a single research epic (use research-epic-planning
  skill); writing individual workplan phases without a backlog review.
argument-hint: "optional sprint theme or focus keyword (e.g. 'scripting hygiene')"
applies-to:
  - Executive PM
  - Executive Planner
  - Executive Orchestrator
status: active
type: feature
effort: m
---

# Sprint Planning

This skill enacts the *Endogenous-First* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md):
before proposing any new sprint, the agent reads the full open-issue backlog, existing
milestones, and prior workplans — so the sprint is scaffolded from known committed context,
not invented interactively. Sprint planning discipline is governed by
[`AGENTS.md`](../../../AGENTS.md) § Sprint Phase Ordering Constraints and
§ Agent Communication → `docs/plans/`. When this skill and those documents conflict, the
primary documents take precedence.

**Canonical workplan template**: [`docs/plans/2026-03-08-value-encoding-fidelity.md`](../../../docs/plans/2026-03-08-value-encoding-fidelity.md)

---

## Beliefs & Context

This skill implements the sprint-planning workflow as a repeatable procedure for the
[`Executive PM`](../../../.github/agents/executive-pm.agent.md) and
[`Executive Planner`](../../../.github/agents/executive-planner.agent.md).

**Used by**:
- **Executive PM** — owns milestone creation, issue assignment, label taxonomy
- **Executive Planner** — owns phase decomposition and workplan authoring
- **Executive Orchestrator** — delegates when user requests "plan the next sprint"

**Foundation documents**:
- [`AGENTS.md`](../../../AGENTS.md) — sprint ordering constraints and commit discipline
- [`docs/guides/github-workflow.md`](../../../docs/guides/github-workflow.md) — labels, milestones, `gh` CLI patterns
- [`docs/plans/`](../../../docs/plans/) — prior workplans as canonical templates
- [`data/labels.yml`](../../../data/labels.yml) — canonical label taxonomy

---

## 1. When to Use This Skill

Use this skill when:

| Trigger | Description |
|---------|-------------|
| User requests a sprint plan | "Plan the next sprint", "what should we work on next?" |
| Current milestone is ≥ 80% closed | Time to scope the next sprint |
| Backlog has ≥ 5 unlabelled or unmilestoned open issues | Hygiene pass required before planning |
| A major new capability was delivered | Logical sprint boundary |

---

## 2. Read the Current State

### Step 2a — Scratchpad

```bash
ls .tmp/
# Read today's scratchpad if it exists
```

### Step 2b — Open Issues

```bash
# All open issues with labels, milestone, body
gh issue list --state open --limit 100 \
  --json number,title,labels,milestone,body,createdAt,updatedAt \
  | jq '.[] | {number, title, labels: [.labels[].name], milestone: .milestone.title, age_days: ((now - (.createdAt | fromdateiso8601)) / 86400 | floor)}'
```

### Step 2c — Milestone Overview

```bash
gh milestone list --state open
gh milestone list --state closed --limit 5
```

### Step 2d — Recent Merged PRs (since last sprint)

```bash
git --no-pager log --oneline --merges -20
```

### Step 2e — Prior Workplans

```bash
ls -lt docs/plans/ | head -10
```

Read the most recent `docs/plans/*.md` to understand the prior sprint's scope and what carried over.

---

## 3. Cluster and Classify the Backlog

Write a `## Sprint Planning Backlog` section in the scratchpad. For each open issue:

| Field | Source |
|-------|--------|
| `#number` | `gh issue list` |
| `title` | `gh issue list` |
| `type:` label | Existing label or inferred from title |
| `priority:` label | Existing label or inferred from urgency signals |
| `effort:` label | XS / S / M / L / XL estimate |
| `area:` label | Codebase domain touched |
| `cluster` | Theme grouping (see below) |
| `milestone` | Already assigned or `backlog` |

**Cluster taxonomy** (assign one per issue):

| Cluster | Examples |
|---------|----------|
| `scripting` | New scripts, script fixes, script tests |
| `agents` | Agent file changes, fleet additions/removals |
| `docs` | Guide updates, research docs, AGENTS.md |
| `ci` | GitHub Actions, pre-commit hooks, automation |
| `research` | Open questions, synthesis docs, source caching |
| `pm` | Labels, milestones, CHANGELOG, community health |
| `infra` | pyproject.toml, deps, .envrc, cookiecutter |

**Priority signals**:
- `priority:critical` / `priority:high` → must-have for this sprint
- `priority:medium` → include if sprint capacity allows
- `priority:low` / no priority → candidates for `backlog` milestone

---

## 4. Propose the Sprint

Write a `## Sprint Proposal — <Sprint Name>` section in the scratchpad.

### Sprint Name Convention

`Sprint NNN — <theme> (<YYYY-MM-DD>)`

Where `NNN` is the next sequential sprint number derived from existing milestones:

```bash
gh milestone list --state all --json title | jq '.[].title' | grep -i sprint | sort | tail -1
```

### Sprint Proposal Template

```markdown
## Sprint Proposal — Sprint NNN — <theme>

**Target start**: <date>
**Target end**: <date (typically 2 weeks)>
**Capacity**: <S/M/L — rough estimate of available effort>

### Must-Have (priority:high or priority:critical)
| # | Title | Type | Effort | Cluster |
|---|-------|------|--------|---------|
| #N | ... | ... | ... | ... |

### Should-Have (priority:medium, fits capacity)
| # | Title | Type | Effort | Cluster |
|---|-------|------|--------|---------|
| #N | ... | ... | ... | ... |

### Defer to Backlog
| # | Title | Reason |
|---|-------|--------|
| #N | ... | priority:low / blocked / out of scope |

### Sprint Total Effort: <XS×N + S×N + M×N ...>

### Milestone Name: Sprint NNN — <theme>

### Workplan slug: sprint-NNN-<theme-slug>
```

### Capacity Guidelines

| Capacity | Maximum effort units (XS=1, S=2, M=3, L=5, XL=8) |
|----------|--------------------------------------------------|
| S (light sprint) | ≤ 10 |
| M (normal sprint) | ≤ 20 |
| L (heavy sprint) | ≤ 30 |

---

## 5. Apply Labels and Milestone

After the proposal is reviewed (self-loop or human confirmation), apply changes:

```bash
# Create the sprint milestone
gh milestone create --title "Sprint NNN — <theme>" --due-date "<YYYY-MM-DD>"

# Assign issues to milestone
gh issue edit <number> --milestone "Sprint NNN — <theme>"

# Apply missing labels
gh issue edit <number> --add-label "priority:high,type:feature,area:scripts"
```

**Pre-use validation before each `gh issue edit`**:
```bash
gh issue view <number> --json number,title,labels,milestone | jq '{number, title, labels: [.labels[].name], milestone: .milestone.title}'
```

**Verify-after-act**:
```bash
gh issue list --milestone "Sprint NNN — <theme>" --json number,title,labels
```

---

## 6. Scaffold the Workplan

Once the milestone is confirmed, scaffold a workplan:

```bash
uv run python scripts/scaffold_workplan.py sprint-NNN-<theme-slug> \
  --issues "<comma-separated issue numbers>" \
  --ci "Tests,Auto-validate"
```

The scaffolded workplan is at `docs/plans/YYYY-MM-DD-sprint-NNN-<theme-slug>.md`.

Open it and fill in:
1. **Objective section** — one paragraph describing the sprint arc
2. **Phase Plan** — one phase per cluster (not per issue); assign agents and deliverables
3. **Acceptance Criteria** — what "sprint complete" means (all issues closed, CI green, CHANGELOG updated)

Commit the workplan before execution begins:
```bash
git add docs/plans/YYYY-MM-DD-sprint-NNN-<theme-slug>.md
git commit -m "docs(plans): scaffold Sprint NNN workplan"
```

---

## 7. Close the Planning Session

After the workplan is committed:

1. Write a `## Sprint Planning Summary` section in the scratchpad.
2. Post a comment on each selected must-have issue with:
   ```
   Added to Sprint NNN — <milestone name>. Workplan: docs/plans/YYYY-MM-DD-sprint-NNN-<slug>.md
   ```
3. Return to **Executive Orchestrator** with the sprint proposal.

---

## Completion Criteria

Sprint planning is **done** when:

- [ ] All open issues have at least one `type:` and one `priority:` label
- [ ] A sprint milestone exists for the proposed sprint
- [ ] All must-have issues are assigned to the sprint milestone
- [ ] Defer-to-backlog issues have `backlog` milestone or `priority:low` label
- [ ] `docs/plans/YYYY-MM-DD-sprint-NNN-<slug>.md` is committed
- [ ] Scratchpad contains `## Sprint Proposal` and `## Sprint Planning Summary` sections
- [ ] Each selected issue has a sprint-assignment comment
- [ ] Verify-after-act passes: `gh milestone list --state open` shows the new sprint

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Proposing a sprint without reading open issues first | Plans from memory miss unlabelled 'dark' issues | Always run Step 2b before Step 4 |
| Assigning every issue to the sprint | Overloads capacity; sprint fails | Enforce capacity limits from Step 4 |
| Creating milestone before proposal is confirmed | Hard to undo; confuses the board | Propose first (Step 4), create milestone after confirmation (Step 5) |
| Skipping the workplan scaffold | Sprint loses structural coherence after day 1 | Step 6 is mandatory before execution |
| Using `gh issue create` for triage notes | Bloats issue tracker | Write triage notes in scratchpad; only create issues for genuine new work items |
