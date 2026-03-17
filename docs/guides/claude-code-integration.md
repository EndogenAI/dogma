# Claude Code Integration Guide

This guide shows how to activate Claude Code's lifecycle hooks for dogma-based projects, binding the existing governance scripts to Claude Code's session events.

## What This Gives You

Instead of relying on text instructions to remind agents to run `prune_scratchpad.py` or check the phase gate, the hooks fire automatically:

| When | Hook | Dogma script / action |
|---|---|---|
| Session starts | `SessionStart` | `prune_scratchpad.py --init` |
| Agent wants to stop | `Stop` | Phase-gate checklist evaluation (LLM-evaluated, multi-criteria) |
| Before compaction | `PreCompact` | Pre-compact checkpoint written to scratchpad |
| After compaction | `PostCompact` | Scratchpad + workplan re-read, reorientation written |
| Session ends | `SessionEnd` | Session summary + issue comments posted |

**Why this matters**: The `Stop` hook (type: `prompt`) can evaluate complex multi-criteria gates — commit verification, AC checkbox confirmation, ruff/test pass — that are not expressible in simple pre-commit hooks. This is [Programmatic-First (MANIFESTO.md)](../../MANIFESTO.md#programmatic-first-principle-cross-cutting) applied at the agent lifecycle layer.

---

## Setup (5 Steps)

**Prerequisites**: Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)

### 1. Clone the repo (or use an existing checkout)

```bash
git clone https://github.com/EndogenAI/dogma.git
cd dogma
```

### 2. Install Python dependencies

```bash
uv sync
```

### 3. Verify the hook config exists

```bash
cat .claude/settings.json  # should show hooks for SessionStart, Stop, PreCompact, etc.
```

The hook configuration is committed to the repo at `.claude/settings.json`. No manual setup required — it activates automatically when Claude Code opens the project.

### 4. (Optional) Add per-developer overrides

Create `.claude/settings.local.json` (gitignored) for developer-specific settings:

```json
{
  "permissions": {
    "allow": [
      "Bash(brew *)",
      "Bash(open *)"
    ]
  }
}
```

### 5. Start a Claude Code session

```bash
claude
```

On first `Stop` event, you'll see the phase-gate-sequence prompt fire. The `SessionStart` hook initialises the scratchpad automatically.

---

## Hook Details

### `SessionStart` — Scratchpad Init

Runs `uv run python scripts/prune_scratchpad.py --init` on session open. Creates or reads today's scratchpad at `.tmp/<branch-slug>/$(date +%Y-%m-%d).md`.

### `Stop` — Phase Gate (type: prompt)

An LLM-evaluated phase gate that checks:
1. No uncommitted changes (`git status --porcelain`)
2. `## Pre-Compact Checkpoint` present in today's scratchpad since the last phase header
3. Ruff check passes on changed scripts
4. Any new D4 research docs have all `## Recommendations` items tracked as issues

Guards against infinite loops with `stop_hook_active` check.

### `PreCompact` — Compaction Guard

Before VS Code compacts the conversation: checks scratchpad size, then prompts the agent to write a `## Pre-Compact Checkpoint` with committed SHAs, next step, and blockers.

### `PostCompact` — Reorientation

After compaction: prompts the agent to re-read the scratchpad and workplan from disk before continuing. Prevents the post-compaction re-discovery loop.

### `SessionEnd` — Session Close

Prompts the agent to write `## Session Summary`, post issue progress comments, and confirm the branch is pushed clean.

---

## print mode (`claude -p`) Policy

For single-query tasks that don't need interactive sessions:

```bash
# Structured output — fastest, schema-validated
claude -p "Validate this research doc summary" \
  --output-format json \
  --max-turns 1 \
  --max-budget-usd 0.10

# CI context — no session persistence
claude -p "..." --no-session-persistence --output-format json
```

See [CLAUDE.md](../../CLAUDE.md) § claude -p Print Mode Policy for the full decision table (interactive vs. print mode).

---

## Configuration Location Decision

Hook configuration lives at `.claude/settings.json` (committed to git, fleet-wide) — NOT in `CLAUDE.md` prose or `settings.local.json` (per-developer, gitignored). See `docs/decisions/ADR-NNN-claude-hook-config-location.md` when that ADR is written (#310).

**Rule**: anything that must be consistent across the full agent fleet → `.claude/settings.json`. Developer preferences → `settings.local.json`.

---

## Companion Issues

- [#307](https://github.com/EndogenAI/dogma/issues/307) — full implementation AC for hooks integration
- [#309](https://github.com/EndogenAI/dogma/issues/309) — claude -p print mode policy
- [#310](https://github.com/EndogenAI/dogma/issues/310) — hook config location ADR (backlog)

## Source

`docs/research/claude-code-cli-productivity-patterns.md` (Sprint 15, commit 5f31715) — Recs 1–3 and Open Questions.
