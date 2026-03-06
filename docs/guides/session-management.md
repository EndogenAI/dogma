# Session Management & Cross-Agent Scratchpad

---

## Overview

When multiple agents collaborate across a session, they need a shared scratchpad to preserve context, pass handoff notes, and avoid re-discovering information. The `.tmp/` directory serves this purpose.

`.tmp/` is **gitignored** — it is never committed. It exists only on your local machine during active development.

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
| Session file < 200 lines | No action needed |
| Session file ≥ 200 lines | Run `uv run python scripts/prune_scratchpad.py` |
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

# Prune in-place (when file exceeds 200 lines)
uv run python scripts/prune_scratchpad.py

# Force prune + archive session (at session end)
uv run python scripts/prune_scratchpad.py --force
```
