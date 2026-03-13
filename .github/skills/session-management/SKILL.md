---
name: session-management
description: |
  Governs the full agent session lifecycle: scratchpad init/close, encoding checkpoint at session start, compaction guard, phase gate protocol, and session summary. USE FOR: starting a new session (prune_scratchpad.py --init); writing ## Session Start with governing axiom; managing cross-agent context in .tmp/<branch>/<date>.md; running the pre-compact checkpoint sequence; writing ## Session Summary and running prune_scratchpad.py --force at session end. DO NOT USE FOR: individual task execution (use the agent directly); committing changes (Orchestrator commits after Review approval); research synthesis (use the Research fleet).
argument-hint: "session phase (start|checkpoint|close)"
---

# Session Management

This skill enacts the *Algorithms Before Tokens* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md) by encoding the full session lifecycle as a deterministic procedure. Session management is governed by [`AGENTS.md`](../../../AGENTS.md) § Agent Communication — every rule in this skill derives from that section. Read `AGENTS.md` before deviating from any step below.

---

## 1. File Structure

The scratchpad lives in `.tmp/` at the workspace root. It is **gitignored** and never committed.

```
.tmp/
  <branch-slug>/          # branch name with / replaced by -
    _index.md             # one-line stubs of all closed sessions on this branch
    <YYYY-MM-DD>.md       # one file per session day — the active scratchpad
```

**`<branch-slug>`** examples:
- Branch `main` → `.tmp/main/`
- Branch `feat/agent-skills` → `.tmp/feat-agent-skills/`
- Branch `docs/update-guides` → `.tmp/docs-update-guides/`

The `_index.md` accumulates single-line stubs for every closed session on the branch. Future sessions read it for fast orientation without opening old files.

---

## 2. Session Start

### 2.1 Initialize the Scratchpad

At the beginning of every session, run:

```bash
uv run python scripts/prune_scratchpad.py --init
```

This creates `.tmp/<branch-slug>/<today>.md` if it does not exist. If the file already exists (resuming a session mid-day), it is unchanged.

Start the scratchpad watcher in a background terminal:

```bash
uv run python scripts/watch_scratchpad.py
```

The watcher auto-annotates every H2 heading with its current line range (`## My Section [L12–L47]`), enabling precise line-number references in agent delegations.

### 2.2 Session-Start Encoding Checkpoint

**Requirement**: The very first sentence written in `## Session Start` must name the governing axiom and one primary endogenous source — before any tool calls, file reads, or task execution.

**Format:**

```markdown
## Session Start

**Session-Start Checkpoint**: This session is governed by Axiom N (Name).
Primary endogenous source: `<path>` — <one sentence on why this source is consulted first>.
```

**Examples by session type:**

- *Research session*: "This session is governed by Axiom 1 (Endogenous-First). Primary endogenous source: `docs/research/OPEN_RESEARCH.md` — frames the research question before any web fetching."
- *Scripting session*: "This session is governed by Axiom 2 (Algorithms Before Tokens). Primary endogenous source: `scripts/watch_scratchpad.py` — canonical example of automating a repeated manual task."
- *Documentation session*: "This session is governed by Axiom 1 (Endogenous-First). Primary endogenous source: `docs/guides/workflows.md` — existing patterns to extend rather than re-author."

**Why this matters**: Low checkpoint-density in scratchpad history is a leading indicator of encoding drift. Auditors can verify whether the stated axiom is consistent with the actions taken. If it is not, the session has drifted from the governing constraint in [`AGENTS.md`](../../../AGENTS.md).

### 2.3 Read Before Acting

If this is a continuation session (an open branch with prior scratchpad entries), read the `_index.md` and today's scratchpad file before delegating:

```bash
# Orientation read — always do this before Phase 1
read_file .tmp/<branch-slug>/_index.md
read_file .tmp/<branch-slug>/<today>.md
```

If there is a workplan (`docs/plans/<date>-<slug>.md`), read it as well. The workplan is the plan of record; the scratchpad is the live inter-agent memory.

---

## 3. Phase Gate Protocol

### 3.1 Phase Output Headings

Each delegated agent appends findings under its own named section:

```markdown
## <AgentName> Output

<findings here>
```

Standard headings: `## Scout Output`, `## Synthesizer Output`, `## Reviewer Output`, `## Archivist Output`, `## Executive Output`.

**Section-scope isolation rule**: each agent writes only to its own heading and reads only its own prior section. The Executive is the sole integration point — it alone reads the full scratchpad across all agents. Subagents never read laterally across other sections.

### 3.2 Handoff Notes

When handing off to another agent, write a structured note:

```markdown
## Handoff to <Next Agent>

- **Completed**: <what was done>
- **Next steps**: <what the receiving agent should do>
- **Files changed**: <list>
- **Open questions**: <anything unresolved>
```

### 3.3 Escalation Notes

When a subagent cannot complete a task:

```markdown
## <AgentName> Escalation

- **Current state**: <what was completed>
- **Blocking issue**: <what requires elevated posture>
- **Recommended action**: <which agent to invoke>
- **Instructions**: <step-by-step for the receiving agent>
```

### 3.4 Workplan Phase Status

Update phase status markers in `docs/plans/<date>-<slug>.md` as phases complete. Use `✅` for done, `⬜` for pending. Commit the workplan after each phase marks complete — the workplan is a committed, auditable record, not ephemeral context.

---

## 4. Compaction Guard

VS Code Copilot Chat may compact conversation history at any time — automatically (context window full) or manually via `/compact`. Compaction replaces detailed history with a `<conversation-summary>` block. **The scratchpad survives compaction. The conversation history does not.**

### 4.1 Pre-Compact Checkpoint Sequence

When the context window is above 75%, or before running `/compact` manually:

1. Write a `## Pre-Compact Checkpoint` section to the scratchpad:

   ```markdown
   ## Pre-Compact Checkpoint

   - **Current state**: <what has been done so far>
   - **Next action**: <the single next step after compaction>
   - **Open questions**: <anything unresolved>
   - **Files in flight**: <uncommitted changes, if any>
   ```

2. Commit all in-progress file changes:

   ```bash
   git add -A && git commit -m "chore: pre-compact checkpoint"
   ```

3. Update the workplan — tick completed phases.
4. Optionally prune the scratchpad to keep the post-compact re-read fast:

   ```bash
   uv run python scripts/prune_scratchpad.py --dry-run   # check first
   uv run python scripts/prune_scratchpad.py
   ```

5. Run `/compact` in VS Code Copilot Chat.

### 4.2 Post-Compact Recovery

After compaction, the `<conversation-summary>` block is the only conversation context. Immediately re-orient from disk:

1. Re-read the scratchpad: `read_file .tmp/<branch-slug>/<today>.md`
2. Re-read the workplan: `read_file docs/plans/<current-plan>.md`
3. Run `git status` — confirm what is committed vs. in-flight
4. **Do not assume the compaction summary captured everything.** Trust files on disk, not the summary.

### 4.3 Compaction-Safe Writing Habits

| Anti-pattern | Compaction-safe alternative |
|---|---|
| "As I mentioned earlier, X" | Put X in the scratchpad |
| "The plan we discussed" | Write the plan to `docs/plans/` |
| "The open question about Y" | Add Y as a bullet in `## Pre-Compact Checkpoint` |
| Long terminal output referenced in chat | Extract key results to a file |
| Decisions made only in chat | Write the decision to the relevant `AGENTS.md` or guide |

**Rule**: treat every important finding as if the next token will trigger compaction. If it is not in the scratchpad, it is lost.

---

## 5. Size Management

| Situation | Action |
|-----------|--------|
| Session file < 2000 lines | No action needed |
| Session file ≥ 2000 lines | `uv run python scripts/prune_scratchpad.py` |
| Active multi-phase sprint | Do **NOT** run `--force` mid-sprint — preserve all Scout and phase output across phases; prune only after the sprint's highest Review gate is APPROVED |
| Session end | Write `## Session Summary`, then `uv run python scripts/prune_scratchpad.py --force` |
| New session day | `uv run python scripts/prune_scratchpad.py --init` |

Pruning compresses "archived" sections (headings containing: `Results`, `Output`, `Done`, `Completed`, `Summary`, `Handoff`) to single-line stubs, and preserves "live" sections (containing: `Active`, `Plan`, `Session`, `Escalation`) in full. It appends a one-line stub to `_index.md` on `--force`.

Always dry-run before pruning:

```bash
uv run python scripts/prune_scratchpad.py --dry-run
```

### 5.1 Tracked Workplans (`docs/plans/`)

For any multi-phase session (≥ 3 phases or ≥ 2 agent delegations, or spanning more than one day), create a **workplan** before execution begins and commit it to `docs/plans/`. Governed by [`AGENTS.md`](../../../AGENTS.md) § Agent Communication — Programmatic-First applied to session planning.

**Naming**: `docs/plans/YYYY-MM-DD-<brief-slug>.md` (date-first for chronological sorting)

**Required contents**:
- Objective
- Phase plan: agent, deliverables, depends-on, status — **with a Review gate phase after every domain phase**
- Acceptance criteria checklist

Use `docs/plans/2026-03-06-formalize-workflows.md` as the canonical template.

**Commit** the workplan at the start of the session (before Phase 1 executes), then update status markers (`⬜ Not started`, `⏳ In progress`, `✅ Complete`) as phases complete. See § 3.4 for the phase status update pattern.

**Fleet coherence mechanism**: a committed workplan gives every downstream execution agent (Scout, Synthesizer, Reviewer) a shared written specification to verify against — without the Orchestrator re-explaining scope at each handoff. Coherence emerges from the artifact, not from the Orchestrator's presence at every step.

### 5.2 Per-Phase Execution Checklists

Before delegating any multi-step execution phase, the Orchestrator delegates a detailed per-phase checklist to the **Executive Planner** first. The Planner's checklist functions as a shared coherence artifact: every downstream execution agent independently verifies their output against it, eliminating interpretive drift without requiring the Orchestrator to re-explain scope mid-phase.

**Flow**:
- Workplan created → delegate checklist creation to Executive Planner
- Checklist committed to scratchpad or workplan doc before Phase 1 begins
- Each execution phase invocation references the checklist as its acceptance criteria

**Hard gate (≥3 phases or ≥2 delegations)**: The Executive Planner must produce per-phase checklists before the first domain phase delegation begins. This is not optional. Skipping this step produces a ~1 audit-round overhead to recover mid-phase scope gaps — observed twice in the 2026-03-13 Dogma Update Sprint (Phase 5 recast, Phase 1A sub-issue gap). Write "Planner checklist received" in the scratchpad before delegating Phase 1.

---

## 6. Session Close

### 6.1 Session Summary

The executive agent writes a `## Session Summary` section to the scratchpad:

```markdown
## Session Summary

**Branch**: <branch-slug>
**Date**: <YYYY-MM-DD>
**Phases completed**: <list>
**Key decisions**: <bullet list>
**Files committed**: <list>
**Recommended next session**: <one sentence>
```

### 6.2 Issue Progress Comments

Post a progress comment on every GitHub issue actively worked during the session. Write the body to a temp file — never use `--body "..."` with multi-line content:

```bash
# Validate temp file before consumption
test -s /tmp/session_close_<num>.md || { echo "ERROR: temp file empty"; exit 1; }
file /tmp/session_close_<num>.md | grep -q "UTF-8\|ASCII" || { 
  echo "ERROR: file not valid UTF-8"; exit 1; 
}

# Safe to use
gh issue comment <num> --body-file /tmp/session_close_<num>.md

# Verify the comment landed:
gh issue view <num> --json comments -q '.comments[-1].body[:80]'
```

### 6.3 Issue Checkbox Updates

Update the issue body checkboxes to reflect completed deliverables:

```bash
# Validate temp file before consumption
test -s /tmp/issue_<num>_body.md || { echo "ERROR: temp file empty"; exit 1; }
file /tmp/issue_<num>_body.md | grep -q "UTF-8\|ASCII" || { 
  echo "ERROR: file not valid UTF-8"; exit 1; 
}
grep -q "- \[.\]" /tmp/issue_<num>_body.md || { 
  echo "WARNING: no checkbox patterns found"; 
}

# Safe to use
gh issue edit <num> --body-file /tmp/issue_<num>_body.md

# Verify
gh issue view <num> --json body -q '.body' | grep -E '\[x\]|\[ \]'
```

### 6.4 Archive and Stop

```bash
uv run python scripts/prune_scratchpad.py --force
# Stop the scratchpad watcher (Ctrl-C in its terminal)
```

---

## 7. Quick Reference

```bash
# Initialize today's session file
uv run python scripts/prune_scratchpad.py --init

# Start auto-annotator (keep running in background)
uv run python scripts/watch_scratchpad.py

# Dry-run prune (check what will be compressed)
uv run python scripts/prune_scratchpad.py --dry-run

# Prune in-place (when file exceeds 2000 lines)
uv run python scripts/prune_scratchpad.py

# Force prune + archive session (at session end)
uv run python scripts/prune_scratchpad.py --force
```

---

## 8. Governing Constraint

This skill is governed by [`AGENTS.md`](../../../AGENTS.md) § Agent Communication. All rules in this skill are re-encodings of that section. When `AGENTS.md` and this skill conflict, `AGENTS.md` takes precedence. The encoding inheritance chain is:

[`MANIFESTO.md`](../../../MANIFESTO.md) → [`AGENTS.md`](../../../AGENTS.md) → agent files → this skill → session behaviour.

Cross-reference density (back-references to `MANIFESTO.md` or `AGENTS.md` in session output) is a proxy for encoding fidelity. Low density signals likely drift.
