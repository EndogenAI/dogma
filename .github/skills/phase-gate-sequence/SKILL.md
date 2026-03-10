---
name: phase-gate-sequence
description: |
  Encodes the mandatory 6-step inter-phase checkpoint sequence that executive-tier agents run after every domain phase and before delegating the next. Includes the context window alert trigger conditions and session handoff prompt template.
  USE FOR: running the post-phase prune → checkpoint → commit → grep sweep → review → compact sequence; triggering the context-window alert and generating a handoff prompt; ensuring no domain phase is skipped or batched without a gate record.
  DO NOT USE FOR: deciding which agent to delegate to (use delegation-routing); session start/close lifecycle (use session-management); individual script command syntax (see docs/toolchain/).
argument-hint: "current phase number and name (e.g. 'Phase 3 — Synthesis')"
tier: Foundation
type: automation
effort: m
applies-to:
  - Executive Orchestrator
  - Executive Researcher
  - Executive Fleet
  - Executive Docs
status: active
---

# Phase Gate Sequence

This skill enacts the *Algorithms-Before-Tokens* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md): the 6-step gate is a deterministic algorithm encoded once and shared across all executive agents, eliminating parallel re-derivation and enforcing consistent phase discipline fleet-wide.

---

## Endogenous Sources

- **Governing axiom**: Axiom 2 — *Algorithms Before Tokens* — deterministic procedure over repeated instruction
- **GitHub issue**: [#79 — Skills as Decision Codifiers](https://github.com/EndogenAI/Workflows/issues/79)
- **Formal FSM spec**: [`data/phase-gate-fsm.yml`](../../../data/phase-gate-fsm.yml) — machine-readable state specification for this gate loop (states: INIT, PHASE_RUNNING, GATE_CHECK, COMPACT_CHECK, COMMIT, CLOSED)
- **Agents that use this skill**: Executive Orchestrator, Executive Researcher, Executive Fleet, Executive Docs
- **Foundation docs**:
  - [`AGENTS.md`](../../../AGENTS.md) — compaction-aware writing, commit discipline, Programmatic-First
  - [`executive-orchestrator.agent.md`](../../../.github/agents/executive-orchestrator.agent.md) — canonical per-phase sequence (lines 169–196) and context window alert protocol (lines 198–242)

---

## Workflow

Run this sequence after every `## Phase N Output` write, **before** delegating the next domain phase.

### Step 1 — Prune

If the scratchpad exceeds 2000 lines:
```bash
uv run python scripts/prune_scratchpad.py
```

### Step 2 — Write Pre-Compact Checkpoint

Append `## Pre-Compact Checkpoint` to the scratchpad with:
- What is complete (include commit SHAs)
- What is next
- Any open questions or blockers

### Step 3 — Commit In-Progress Changes

```bash
git add -A && git commit -m "chore: pre-compact checkpoint — Phase N complete"
```

### Step 4 — Pre-Review Grep Sweep

Scans the entire `.github/` directory (all agent and skill files) for known heading-contract violations and erroneous patterns — not scoped to changed files only, since stale patterns can exist anywhere.

```bash
if grep -r "Phase N Review Output\|Fetch-before-check" .github/; then
  echo "ERROR: known pattern violations found — fix before requesting review"
elif [ $? -eq 1 ]; then
  echo "grep sweep clean"
else
  echo "ERROR: grep failed during sweep — investigate before requesting review"
fi
```

Fix any matches before invoking Review.

### Step 5 — Review Gate

Invoke the **Review** agent with the changed file list and scratchpad location. Append verdict to the scratchpad under `## Review Output`. **Do not advance to the next phase until APPROVED.**

### Step 6 — Compact Recommendation

If the completed phase was a long research, synthesis, or multi-file editing delegation, recommend `/compact` before the next delegation. After any compaction event: re-read the scratchpad and workplan from disk before continuing.

---

### Context Window Alert — Trigger Conditions

**Pause all delegation immediately** when any of the following is true:

- Compaction has occurred in this session, OR
- The user signals compaction is becoming frequent, OR
- You detect you are reconstructing already-explored context (re-reading the same file, re-running the same search)

**When triggered:**
1. Write `## Context Window Checkpoint` to the scratchpad: active phase + status, committed vs. in-progress deliverables (with SHAs), last agent delegated + ≤100-token return summary, single next concrete step, open blockers.
2. Commit and push all in-progress changes.
3. Present the session handoff prompt template from [`executive-orchestrator.agent.md`](../../../.github/agents/executive-orchestrator.agent.md) lines 215–236 — fill in bracketed fields from the scratchpad.
4. Do not proceed until the user resumes via the handoff prompt.

---

## Completion Criteria

The phase gate is correctly applied for a given phase when:

- [ ] `## Pre-Compact Checkpoint` exists in the scratchpad for every completed domain phase.
- [ ] `## Review Output` with APPROVED verdict exists before the next domain phase was delegated.
- [ ] All phase deliverables are committed at gate time — no in-progress changes left dangling.
- [ ] Grep sweep ran clean (or violations were fixed before review was requested).

**Exit condition**: The loop terminates when `## Session Summary` has been written and `uv run python scripts/prune_scratchpad.py --force` has run — see the `session-management` skill for the full session close sequence.
