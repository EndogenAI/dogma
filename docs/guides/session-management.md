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

### Session-Start Encoding Checkpoint

At the start of every session, before taking any first action, write which axiom governs the work and name one endogenous source you will consult first. This is the **first sentence** of the `## Session Start` scratchpad entry — before any tool calls.

**Format:**

> **Session-Start Checkpoint**: This session is governed by Axiom _N_ (_name_). Primary endogenous source: `<path>` — _one sentence on why_.

**When**: Required at the start of any session where the agent operates under `AGENTS.md` scope.

**Why**: Confirms axiom absorption before token spend begins. Creates an auditable drift signal — future reviewers can check whether the stated axiom is consistent with the actions taken in the session. Low checkpoint density → likely encoding drift.

**Examples:**

- _Research session_: "This session is governed by Axiom 1 (Endogenous-First). Primary endogenous source: `docs/research/OPEN_RESEARCH.md` — frames the research question before any web fetching."
- _Scripting session_: "This session is governed by Axiom 2 (Algorithms Before Tokens). Primary endogenous source: `scripts/watch_scratchpad.py` — canonical example of automating a repeated manual task."
- _Documentation session_: "This session is governed by Axiom 1 (Endogenous-First). Primary endogenous source: `docs/guides/workflows.md` — existing patterns to extend rather than re-author."

See [`MANIFESTO.md` → How to Read This Document](../../MANIFESTO.md) for axiom priority order and anti-pattern veto rules.

---

## During a Session

### Writing to the Scratchpad

Each agent appends findings under its **own named section heading** and reads only its own prior section:

```markdown
## <AgentName> Output

<findings here>
```

Standard heading patterns: `## Scout Output`, `## Synthesizer Output`, `## Reviewer Output`, `## Archivist Output`.

**Section-scope isolation rule**: each agent writes only to its own heading and reads only its own prior section. The **Executive is the sole integration point** — it alone reads the full scratchpad to coordinate across agents. Subagents do not read laterally across other agents' sections.

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

---

## Context Compaction

VS Code Copilot Chat has a built-in **context compaction** mechanism that reduces conversation history when the context window is filling up. It appears as:

- A **"Compact Conversation"** button in the context window summary popup
- The **`/compact`** slash command (type `/compact` in the chat input)
- An automatic **"Compacted conversation"** label when the conversation is compacted by the system

### What Compaction Does

Compaction replaces the detailed message history with a structured summary — a `<conversation-summary>` block injected into the context. This summary captures:

- The conversation's goal and key decisions
- Files that were modified and why
- Current state (what was done, what is pending)
- Critical open questions

What is **lost** after compaction:

- Specific intermediate conversation turns ("why did we decide X?")
- Terminal output history that wasn't explicitly noted
- Inline reasoning that was never synthesised to a file

What **survives** compaction (because it lives in files, not history):

- All committed and uncommitted file changes on disk
- The scratchpad (`.tmp/<branch>/<date>.md`) — **this is the key**
- `docs/plans/` workplan files
- `AGENTS.md`, guides, and research docs
- GitHub issues and their bodies

### The Scratchpad is Compaction-Proof

The scratchpad exists on disk. Compaction cannot touch it. This is the core reason write-back is non-negotiable: if a finding is in the scratchpad, it survives any compaction event. If it is only in the chat history, it is lost.

**Treat every important discovery as if the next token will trigger compaction.**

### Compaction Posture: Before It Happens

When you see the context window is above 80% or before running `/compact` manually:

1. **Write a `## Pre-Compact Checkpoint` in the scratchpad** — capture current state, open questions, next actions
2. **Commit all in-progress file changes** — anything uncommitted disappears from reliable context
3. **Update the workplan** — tick completed phases, note in-progress items
4. **Run `prune_scratchpad.py`** if the scratchpad is large (reduces what the agent needs to re-read)

```bash
# Safe pre-compact sequence
git add -A && git commit -m "chore: pre-compact checkpoint"
python scripts/prune_scratchpad.py --dry-run  # check first
python scripts/prune_scratchpad.py
# then run /compact in VS Code Copilot Chat
```

### Compaction Posture: After It Happens

After compaction, the new session starts with the `<conversation-summary>` block as context. To re-orient:

1. **Re-read the scratchpad** — `read_file .tmp/<branch>/<date>.md`
2. **Re-read the workplan** — `read_file docs/plans/<current-plan>.md`
3. **Run `git status`** — confirms what is committed vs. in-flight
4. **Do not assume the compaction summary captured everything** — verify from files, not from the summary

### Writing Habits for Compaction Resilience

These habits make sessions resilient to both compaction and context window rollovers:

| Anti-pattern | Compaction-safe alternative |
|---|---|
| "As I mentioned earlier, X" | Put X in the scratchpad |
| "The plan we discussed" | Write the plan to `docs/plans/` |
| "The open question about Y" | Add Y as a bullet in the scratchpad `## Active` section |
| Long terminal output referenced in chat | Extract the key result to a file or comment |
| Decisions made only in chat | Write the decision to the relevant `AGENTS.md` or guide |

### When to Run `/compact` Manually

Run `/compact` proactively (before being forced) when:

- The context window indicator is above 75%
- Starting a new major phase in a long session
- Switching domains (e.g., finishing research, starting implementation)
- Before delegating to a subagent that needs a clean context

**Do not** run `/compact` when:
- You have uncommitted changes that haven't been noted in the scratchpad
- You are mid-implementation and the chat history contains the only record of in-progress decisions
- The last scratchpad write was more than 20 minutes ago

### Relationship to `prune_scratchpad.py`

`prune_scratchpad.py` and `/compact` are complementary, not equivalent:

| Tool | What it compresses | Where the compressed content goes |
|---|---|---|
| `prune_scratchpad.py` | Scratchpad sections | `_index.md` stubs (on disk, permanent) |
| `/compact` | Conversation history | `<conversation-summary>` block (in VS Code context, ephemeral) |

Run `prune_scratchpad.py` to keep the scratchpad lean so the re-read after compaction is fast.
Run `/compact` when the conversation context window is full and you want the model to continue with a fresh context window.

---

## Starting a New Session

When opening a new chat on an existing branch (whether after compaction, after a break, or at the start of a new day), use the **session continuation handoff prompt**.

### Standard Continuation Prompt

```
@Executive Orchestrator Please continue the session on branch [branch-slug].
Read the active scratchpad at .tmp/[branch-slug]/[YYYY-MM-DD].md before delegating anything —
specifically the ## Executive Handoff and ## Session Summary sections.
Focus for this session: [one sentence from the handoff's "Recommended Next Session" section].
Write ## Session Start with a one-paragraph orientation before proceeding.
```

**How to fill it in:**
1. `[branch-slug]` — the branch name with `/` replaced by `-` (e.g., `feat-implement-research-findings`)
2. `[YYYY-MM-DD]` — today's date (`date +%Y-%m-%d` in a terminal)
3. `[one sentence...]` — copy from the `### Recommended Next Session` section of the prior `## Executive Handoff`, or from `### What Is Open` in the `## Session Summary`

### What the Orchestrator Should Do After Receiving This Prompt

1. Run `uv run python scripts/prune_scratchpad.py --init` to create today's file if needed
2. Read the scratchpad — specifically `## Executive Handoff` and `## Session Summary`
3. Write `## Session Start` with a one-paragraph orientation (branch, HEAD commit, what was done, what is next)
4. Write a committed workplan in `docs/plans/` if the session has ≥ 3 phases
5. Begin delegating — one phase at a time

### Writing a Useful Handoff Section

At the **end** of any session that will continue later, write a `## Executive Handoff — <date>` section in the scratchpad covering:

- **New Lessons Learned** — what went wrong or better than expected; not yet in AGENTS.md
- **Synthesis Recs Status** — table of R-items from research docs: done / not done / partial
- **Open Research Threads** — prioritized list of next research questions
- **Missing Workflows** — gaps in `docs/guides/workflows.md` needed before the next phase
- **Recommended Next Session Scope** — one paragraph per candidate session (Session A, Session B…)

The handoff section is the contract between sessions. Without it, the next session re-discovers at token cost what the prior session already knew.

