---
name: session-retrospective
description: |
  Formalises the post-phase insight harvest and substrate encoding loop: articulate lessons learned, gap-analyse which are already encoded, route encoding gaps to the correct fleet agents, and commit the result. USE FOR: closing a phase with ≥2 novel patterns observed; ending a session where new techniques outperformed prior expectations; when a specialist agent produces unexpectedly clean output worth encoding; back-propagating new knowledge into AGENTS.md, guides, skills, and agent files. DO NOT USE FOR: mid-phase check-ins (wait until the phase produces a stable output); sessions under context-window pressure (schedule for next session); tasks that produced no new patterns or lessons.
argument-hint: "phase or session that just completed (e.g. 'Phase 2 fleet audit')"
---

# Session Retrospective — Insight Discovery and Substrate Encoding

This skill enacts the *Endogenous-First* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md): new knowledge discovered during a session must flow back into the substrate, not remain as ephemeral chat context. It is governed by [`AGENTS.md`](../../../AGENTS.md) § Per-Phase Execution Checklists and § Session-End Closing Steps. This skill is the session-level enactment of Issue #82 (Dogma Neuroplasticity — back-propagation protocol).

Read [`docs/guides/session-management.md`](../../../docs/guides/session-management.md) and [`docs/guides/workflows.md`](../../../docs/guides/workflows.md) before deviating from any step below.

---

## Endogenous Sources

This skill implements the back-propagation protocol: new patterns discovered interactively must be encoded durably before they can influence future sessions.

**Implements**: Issue #82 — Dogma Neuroplasticity — back-propagation protocol

**Governed by**:
- [`AGENTS.md`](../../../AGENTS.md) § Per-Phase Execution Checklists — retrospective runs as the close step after the final phase
- [`MANIFESTO.md`](../../../MANIFESTO.md) *Endogenous-First* axiom — endogenous knowledge compounds; chat-only knowledge evaporates

**Used by**:
- Executive Orchestrator (runs retrospective at session close)
- Executive Fleet (receives agent/skill encoding gaps)
- Executive Docs (receives AGENTS.md / guide encoding gaps)
- Orchestrator (commits via terminal after Review approval)
- Review agent (validates additions before commit)

**Companion skill**: [`session-management`](../session-management/SKILL.md) — retrospective runs during Session Close phase (Step 5 of that skill)

---

## When to Run

Trigger this skill when **any of the following conditions hold** after a phase or session:

| Trigger | Example |
|---------|---------|
| ≥2 novel patterns observed this phase | New delegation pattern worked; new anti-pattern avoided |
| New technique outperformed prior expectation | Skill invocation faster than direct agent call |
| Specialist agent produced unexpectedly clean output | Reviewer catches something the pattern didn't anticipate |
| Session produced a pattern not yet in any SKILL.md or AGENTS.md | A new compression trick, routing shortcut, or gap-fill strategy |
| A lesson was learned the hard way (anti-pattern hit) | Heredoc silently corrupted content; retry loop wasted tokens |

**Do NOT run** if:
- The context window is under pressure — write a `## Pre-Compact Checkpoint` note and schedule the retrospective for the next session instead.
- The phase produced no new patterns (routine execution of a well-encoded procedure).
- You are mid-phase and the output is not yet stable.

---

## Workflow

### Step 1 — Harvest

Articulate what was learned this phase or session. Write a `## Retrospective — <YYYY-MM-DD>` section in the active scratchpad (`.tmp/<branch-slug>/<today>.md`) with:

```markdown
## Retrospective — YYYY-MM-DD

### Lessons Learned
1. <Lesson: one sentence — what happened and why it matters>
2. ...

### Anti-patterns Avoided
1. <What was tempting but skipped — and why it would have failed>

### Efficiency Observations
1. <What took longer than expected / shorter than expected — why>
```

**Token target**: ≤400 tokens for the Harvest section. Compress observations; do not include raw session history.

**Inputs**: scratchpad, workplan phase status, your own session memory.
**Output**: a numbered lessons list with ≤10 items, written to the scratchpad.

---

### Step 2 — Gap-Analyse

Delegate to an **Explore subagent** with a narrow, scoped prompt:

> "For each lesson below, search `AGENTS.md`, `docs/guides/`, `.github/agents/*.agent.md`, and `.github/skills/*/SKILL.md` to identify whether it is already encoded. Return a table: Lesson | Already Encoded In | Gap (Yes/No). Return ≤800 tokens."

Pass the numbered lessons list as input. Do **not** pass the full scratchpad — Focus-on-Descent applies: narrow context in, compressed result out.

**Expected output** (from the Explore subagent):

| # | Lesson | Already Encoded In | Gap? |
|---|--------|--------------------|------|
| 1 | ... | `AGENTS.md` § Foo | No |
| 2 | ... | — | **Yes** |

The subagent appends its output under `## Gap-Analysis Output` in the scratchpad.

**Compression target**: ≤800 tokens returned.

---

### Step 3 — Route

For each lesson with Gap = **Yes**, route to the correct fleet agent using the Routing Table below. Write a `## Routing Plan` section in the scratchpad listing each gap, its target agent, and the specific file(s) to update.

#### Routing Table

| Lesson domain | Target agent | Files to update |
|---------------|-------------|-----------------|
| Session lifecycle procedure | **Executive Fleet** (this agent) | `.github/skills/session-management/SKILL.md` |
| Agent posture or guardrail | **Executive Fleet** | `.github/agents/<slug>.agent.md` |
| New reusable workflow skill | **Executive Fleet** | `.github/skills/<new-slug>/SKILL.md` |
| AGENTS.md convention (fleet-wide) | **Executive Docs** | `AGENTS.md` (root) |
| Guide update (workflow, testing, github) | **Executive Docs** | `docs/guides/<guide>.md` |
| Subdirectory AGENTS.md | **Executive Docs** | `docs/AGENTS.md`, `.github/agents/AGENTS.md` |
| Research synthesis gap | **Executive Researcher** | `docs/research/<topic>.md` |
| Script or automation gap | **Executive Scripter** | `scripts/<script>.py` |

**Constraint**: route **one gap per delegation**. Do not batch all gaps into a single agent invocation — batching reduces accountability and makes Review harder. Each delegation gets a focused scope.

**Inputs to each downstream agent**: the specific lesson text + the target file(s) + the reasoning for the gap.
**Expected outputs**: a file edit (new section, new bullet, or new file) ready for Review.

---

### Step 4 — Verify

After all routing delegations complete, invoke the **Review agent** with:

> "Review the following additions for consistency with existing substrate. Confirm each addition: (1) does not duplicate existing content, (2) follows the formatting conventions of its host file, (3) maintains cross-reference density (links back to `MANIFESTO.md` or `AGENTS.md` where applicable), (4) introduces no TODO placeholders."

Pass the list of changed files. The Review agent returns a per-file verdict.

If Review approves all changes, **Orchestrator commits via `git` operations** following [Conventional Commits](../../../CONTRIBUTING.md):

```
docs(session): encode <topic> lessons from <date> retrospective
```

If Review flags any change, fix before committing — do not bypass the Review gate.

---

## Example Invocation Prompt

The canonical invocation for this skill is:

> "What lessons have we learned? Delegate querying which ones are encoded and which aren't, routing to the fleet to update the executive orchestrator and appropriate workflows."

This phrase is the trigger. When an orchestrator uses this phrasing (or a close variant), apply this skill's four-step procedure in sequence.

---

## Constraints

- **Never encode lessons as chat-only notes.** A lesson that exists only in conversation history will not survive compaction. Write it to the scratchpad first, then to the substrate.
- **Never batch all lessons into one delegation.** One gap → one delegation → one focused change → one Review checkpoint.
- **Always run the Review gate before committing.** Retrospective-sourced changes must be validated for consistency — they arrive from informal observation, not from a formal spec.
- **Do not run under context-window pressure.** If the context window is above 75%, write a `## Pre-Compact Checkpoint` note (see [`session-management`](../session-management/SKILL.md) § Compaction Guard) and defer the retrospective to the next session open.
- **Scope to genuine lessons.** Do not encode obvious, already-documented behaviour. The bar is: "a future agent would behave differently if this were encoded."
- **Do not modify `MANIFESTO.md` during a retrospective.** That document encodes foundational axioms. Retrospectives update operational substrate (AGENTS.md, guides, skills, agent files) — not axioms.

---

## Completion Criteria

The retrospective is complete when:

- [ ] `## Retrospective — <date>` section written to active scratchpad
- [ ] Gap-analysis table produced (Explore subagent output in scratchpad under `## Gap-Analysis Output`)
- [ ] All Yes-gap lessons routed to correct fleet agents, one per delegation
- [ ] Each delegated agent has produced a file edit
- [ ] Review agent has returned **Approved** verdict for all changed files
- [ ] Orchestrator has committed with a Conventional Commit message referencing the retrospective date
- [ ] Session summary notes that retrospective was run and which gaps were filled
