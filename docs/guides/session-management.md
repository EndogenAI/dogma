# Session Management & Cross-Agent Scratchpad

---

## Overview

When multiple agents collaborate across a session, they need a shared scratchpad to preserve context, pass handoff notes, and avoid re-discovering information. The `.tmp/` directory serves this purpose.

`.tmp/` is **gitignored** — it is never committed. It exists only on your local machine during active development.

---

## Workplans (`docs/plans/`)

For any session with ≥ 3 phases or ≥ 2 agent delegations, create a **workplan file** in `docs/plans/` and commit it _before_ execution begins.

**Naming**: `YYYY-MM-DD-<brief-slug>.md`

A workplan captures:
- **Objective** — one paragraph stating what the session accomplishes
- **Phase plan** — each phase with agent assignment, deliverables, dependencies, and a status marker (`✅` / `⬜`)
- **Acceptance criteria** — a checkbox list the Orchestrator ticks off at session close

Workplans are **committed to git** (not gitignored). They serve as the durable, auditable record of multi-phase sessions. The ephemeral `.tmp/` scratchpad is for live inter-agent handoff data; the workplan is the plan of record.

See [`docs/plans/2026-03-06-formalize-workflows.md`](../plans/2026-03-06-formalize-workflows.md) for the canonical example.

---

## Design Rationale

The scratchpad convention implements the **lightweight context handoff** pattern from the Anthropic multi-agent research system. When an agent completes a phase, it writes a summary to the scratchpad; the next agent (or the same agent in a new invocation) reads that summary as its starting context rather than re-deriving it from scratch. This prevents the token cost of re-discovery and maintains fidelity across context window boundaries.

The `.tmp/<branch>/` structure implements two levels of this pattern:

- **`<YYYY-MM-DD>.md`** — the active scratchpad; the only durable cross-agent memory that survives a context window boundary within a session. When agents skip writing to this file, the next agent starts blind. This is not a theoretical risk: live session experience confirmed that scout outputs not written to the scratchpad had to be reconstructed at full token cost when the context window turned over. Write discipline is the primary operational requirement — see [`docs/research/sources/session-synthesis-2026-03-06-a.md`](../research/sources/session-synthesis-2026-03-06-a.md).
- **`_index.md`** — the reference layer; one-line stubs of all closed sessions. Implements the session-reference layer from the same pattern, enabling future sessions to orient in seconds without opening old files.

**Write-back is not optional.** The scratchpad only works as a memory substrate if agents write to it consistently. Every agent file should encode this as a requirement — not just a recommendation.

For the theoretical grounding of this convention in the context engineering literature, see [`docs/research/agentic-research-flows.md`](../research/agentic-research-flows.md) (Memory Architecture and Token Offloading sections).

---

## Directory Structure

```
.tmp/
  <branch-slug>/
    _index.md             # One-line stubs of all closed sessions on this branch
    <YYYY-MM-DD>.md       # One file per session day — the active scratchpad
```

**`<branch-slug>`** = branch name with `/` replaced by `-`

Example: branch `feat/my-feature` → `.tmp/feat-my-feature/2026-03-05.md`

---

## Starting a Session

At the beginning of every session, initialize today's scratchpad file:

```bash
uv run python scripts/prune_scratchpad.py --init
```

This creates `.tmp/<branch-slug>/<today>.md` if it does not exist. If it already exists (e.g., resuming a session), the file is unchanged.

Also start the scratchpad watcher so H2 headings stay annotated automatically:

```bash
uv run python scripts/watch_scratchpad.py
```

If this is a research session, pre-warm the source cache before delegating to any scout:

```bash
# Preview what will be fetched (safe dry run)
uv run python scripts/fetch_all_sources.py --dry-run

# Fetch all uncached sources (idempotent — skips already-cached URLs)
uv run python scripts/fetch_all_sources.py
```

This implements the **fetch-before-act** posture: scouts read cached `.md` files with `read_file`
rather than re-fetching pages through the context window, saving tokens every session.

---

## During a Session

### Writing to the Scratchpad

Each agent appends findings under a named heading:

```markdown
## <Task Name> Results

<findings here>
```

**Never overwrite another agent's section.** Always append.

Standard heading keywords:

| Keyword in heading | Classification |
|--------------------|---------------|
| `Results`, `Output`, `Done`, `Completed`, `Summary`, `Handoff` | Archived when pruned |
| `Active`, `Plan`, `Session`, `Escalation` | Kept live when pruned |

### Handoff Notes

When handing off to another agent, leave a structured note:

```markdown
## Handoff to <Next Agent>

- **Completed**: <what was done>
- **Next steps**: <what the receiving agent should do>
- **Files changed**: <list>
- **Open questions**: <anything unresolved>
```

### Escalation Notes

When a sub-agent cannot complete a task, it writes an escalation note and returns control:

```markdown
## <AgentName> Escalation

- **Current state**: <what was completed>
- **Blocking issue**: <what requires elevated posture or specialist knowledge>
- **Recommended action**: <which agent to invoke, or what to do>
- **Instructions**: <step-by-step for the receiving agent>
```

---

## Size Management

| Situation | Action |
|-----------|--------|
| Session file < 2000 lines | No action needed |
| Session file ≥ 2000 lines | Run `uv run python scripts/prune_scratchpad.py` |
| Session end | Write `## Session Summary`, then run `uv run python scripts/prune_scratchpad.py --force` |
| New session day | Run `uv run python scripts/prune_scratchpad.py --init` |

### What Pruning Does

- Compresses "archived" sections (see keyword table above) to a single-line stub
- Preserves "live" sections in full
- Adds an `## Active Context` header summarising what remains live
- On `--force`: appends a one-line stub to `_index.md` for the closed session

### Dry-Run First

Always check what will be pruned before writing:

```bash
uv run python scripts/prune_scratchpad.py --dry-run
```

---

## Ending a Session

1. The executive agent writes a `## Session Summary` section
2. Run `uv run python scripts/prune_scratchpad.py --force` to archive and update `_index.md`
3. Stop the scratchpad watcher (Ctrl-C)

The `_index.md` accumulates one-line stubs of all closed sessions on the branch. Future sessions can read it to orient quickly without opening old session files.

---

## Annotations

The scratchpad watcher (`watch_scratchpad.py`) automatically annotates every H2 heading with its line range:

```markdown
## My Section [L12–L47]
```

This allows agents to reference sections by exact line number in delegations:

> "Read `.tmp/feat-my-feature/2026-03-05.md` lines L12–L47 for context on the prior research."

Annotations are stripped and recalculated by `--annotate` on every change, so they are always current.

---

## Quick Reference

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
