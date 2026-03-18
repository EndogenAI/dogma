# Claude Code Hooks Configuration Guide

This guide documents how to configure Claude Code to run governance workflows automatically via two complementary patterns: **CLAUDE.md custom instructions** and **settings.json hook definitions**. Understanding when to use each pattern is essential for maintaining consistent, predictable agent behavior across Claude Code sessions.

---

## 1. Overview of Both Patterns

### CLAUDE.md — Session-Level Custom Instructions

**CLAUDE.md** is a project-root Markdown file read by Claude Code on session start. It encodes:
- Core operational constraints (governance axioms from `MANIFESTO.md` and `AGENTS.md`)
- Session lifecycle procedures (scratchpad init, phase gating, session close)
- Toolchain practices (when to use `uv run`, file-writing guardrails)
- Security and secrets hygiene

**Scope**: Text-based instructions that shape agent reasoning and behavior selection throughout the entire session. Acts as a persistent reference frame.

**Deployed via**: Claude Code reads the file automatically from the workspace root on session start. No configuration required.

### settings.json Hooks — Event-Driven Automation

**settings.json** defines structured event hooks that fire at predictable points in the Claude Code lifecycle:

| Hook | Event | Typical Use |
|------|-------|------------|
| `SessionStart` | Session opens | Auto-run `prune_scratchpad.py --init` |
| `PreCompact` | Before context compaction | Write `## Pre-Compact Checkpoint` to scratchpad |
| `PostCompact` | After context compaction | Re-read scratchpad from disk for reorientation |
| `Stop` | Agent requests to stop/end phase | Check pre-commit gates (no uncommitted changes, ruff pass, AC checkboxes marked) |
| `SessionEnd` | Session closes | Write `## Session Summary`, post issue comments |

**Scope**: Deterministic, time-triggered automation that executes external scripts or LLM-evaluated prompts at specific lifecycle moments.

**Deployed via**: Configuration file at `.claude/settings.json` (committed to repo) or `.claude/settings.local.json` (gitignored, developer-local).

---

## 2. Comparison Table: When to Use Each Pattern

| Dimension | CLAUDE.md | settings.json Hooks |
|-----------|-----------|-------------------|
| **Type of content** | Text instructions, procedures, guardrails | Structured event triggers + actions |
| **When it activates** | Session open; read once; persists throughout session | At specific lifecycle events (Start, PreCompact, Stop, etc.) |
| **Scope** | Entire session — influences reasoning & decision-making | Single event — executes a specific action at a trigger point |
| **Syntax** | Markdown with embedded code blocks | JSON with `hook`, `type`, `prompt`/`script` fields |
| **Persistence** | One copy per workspace; affects all sessions on all branches | Per-hook config; `.local.json` for dev overrides |
| **Typical payload** | 500–2000 words of governance text | ≤500 words per hook (brevity enforced) |
| **Example use case** | Explain Endogenous-First axiom, link to AGENTS.md, remind agent of file-writing guardrails | Auto-run scratchpad init on session open; check for uncommitted changes before stopping |
| **Modification frequency** | Rarely — only when core governance changes | Often — each project/session can customize hooks |
| **Who maintains** | Project lead / governance team | Devops / project-specific customizations |
| **What breaks if missing** | Agent forgets governance axioms; re-discovers constraints interactively (token waste) | Manual step omitted; e.g., agent forgets to run `prune_scratchpad.py --init` |

---

## 3. Decision Tree: When to Use Each Pattern

Use this tree to decide which pattern to reach for:

```
┌─ Is the content text instructions / guardrails?
│  ├─ Yes → Use CLAUDE.md
│  │        (e.g., "Here's the Endogenous-First axiom; read AGENTS.md first")
│  │
│  └─ No → Continue to step 2
│
├─ Does it need to fire automatically at a specific lifecycle event?
│  ├─ Yes → Use settings.json hook
│  │        (e.g., "Auto-run prune_scratchpad --init" on SessionStart)
│  │
│  └─ No → Continue to step 3
│
├─ Is it a one-time script execution (no LLM reasoning)?
│  ├─ Yes → Use `script` type hook
│  │        (e.g., `uv run ruff format` on Stop)
│  │
│  └─ No → Continue to step 4
│
└─ Does it require LLM evaluation of complex criteria?
   ├─ Yes → Use `prompt` type hook
   │        (e.g., Stop hook checking AC checkboxes, commit SHAs, etc.)
   │
   └─ No → Default to CLAUDE.md guardrail text
```

---

## 4. Canonical Patterns from the Codebase

### Pattern A: CLAUDE.md — Governance Encapsulation

**File**: [CLAUDE.md](../../CLAUDE.md) at repo root

**What it contains**:
- Governing constraint layers (MANIFESTO.md → AGENTS.md → agent roles)
- Session lifecycle checklist (start, during, end)
- Python toolchain discipline (`uv run` only)
- File writing guardrails (no heredocs)
- Commit discipline (Conventional Commits format)
- Pre-commit checks (ruff, tests, validation)

**When to read it**: Session open + before any first action

**Key excerpt** (from CLAUDE.md):
```markdown
## Session Start

1. Run `uv run python scripts/prune_scratchpad.py --init`
2. Read the active scratchpad — orient on branch, active phase, open issues
3. Write `## Session Start` to the scratchpad with governing axiom and primary endogenous source
4. Check for existing workplan in `docs/plans/` before creating a new one
```

**Derivatives**: Every session-specific prompts should cite CLAUDE.md or reference AGENTS.md and MANIFESTO.md. Custom instructions in Claude Desktop or Cursor should quote sections from CLAUDE.md rather than re-encoding them.

**Maintenance**: Updated when core governance changes (new axioms, phase gate logic, commit discipline rules). Updated once every 1–2 sprints; most sprints leave it stable.

### Pattern B: settings.json Hooks — Lifecycle Automation

**File**: [.claude/settings.json](../../.claude/settings.json) (committed); `.claude/settings.local.json` (gitignored)

**Hook structure** (example: SessionStart):
```json
{
  "hooks": [
    {
      "id": "SessionStart",
      "type": "script",
      "trigger": "on_session_start",
      "action": "uv run python scripts/prune_scratchpad.py --init"
    }
  ]
}
```

**Hook structure** (example: Stop — LLM-evaluated phase gate):
```json
{
  "hooks": [
    {
      "id": "Stop",
      "type": "prompt",
      "trigger": "on_request_stop",
      "action": "Check: 1. git status clean? 2. ## Pre-Compact Checkpoint present? 3. ruff passes? 4. New D4 research docs have issues tracked? APPROVED or REQUEST CHANGES — [criterion: reason]"
    }
  ]
}
```

**Maintenance**: Per-project at `.claude/settings.json`; developer overrides at `.claude/settings.local.json`.

### Pattern C: Agent Role Files — Declarative Tool Scope

Agent role files (`.github/agents/*.agent.md`) document tool restrictions via YAML frontmatter — a third layer distinct from CLAUDE.md execution rules and settings.json event hooks.

**Example** (from [executive-orchestrator.agent.md](../../.github/agents/executive-orchestrator.agent.md)):
```yaml
---
name: Executive Orchestrator
description: Coordinate multi-workflow sessions...
tools:
  [vscode/getProjectSetupInfo, vscode/installExtension, ..., execute/runInTerminal, ...]
handoffs:
  - label: Executive Planner
    agent: Executive Planner
    prompt: "Please create a detailed execution plan for: "
---
```

**What this does**: VS Code Custom Agents use the `tools` list to restrict what actions the agent can take. This is a **declarative**, per-agent constraint — separate from CLAUDE.md's session-wide text instructions and settings.json hooks.

**When to use agent role files**: When you need to create a new specialist agent with different tool scope than the default Orchestrator (narrower posture, fewer tools).

### Pattern D: SKILL.md Files — Reusable Procedural Knowledge

**File**: `.github/skills/<skill-name>/SKILL.md`

**Example** (from [session-management/SKILL.md](../../.github/skills/session-management/SKILL.md)):
```markdown
# Session Management

This skill enacts the *Algorithms Before Tokens* axiom...

## 1. File Structure
The scratchpad lives in `.tmp/` at the workspace root...

## 2. Session Start
At the beginning of every session, run:
```bash
uv run python scripts/prune_scratchpad.py --init
```
```

**Relationship to CLAUDE.md**: SKILL.md files encode **procedural knowledge** that can be reused across multiple agents or invoked on-demand. CLAUDE.md is the **session-initialization entry point**; SKILL.md files are the **focused reference** for a specific task domain.

**When to use**: When a procedure (e.g., session-management, rate-limit-resilience, phase-gate-sequence) could benefit more than one agent, extract it to a skill and link from CLAUDE.md or agent prompts.

---

## 5. Best Practice Patterns

### Best Practice 1: CLAUDE.md as the Session Entry Point

**Pattern**: Every Claude Code session should start by reading CLAUDE.md to set governing constraints.

**Implementation**:
1. CLAUDE.md lives in the repo root
2. On session open, the SessionStart hook runs `prune_scratchpad.py --init`
3. Agent reads `.tmp/<branch>/<date>.md` to check for a `## Session Start` section
4. Agent writes the encoding checkpoint (governing axiom + endogenous source) to the scratchpad

**Example** (from a prior session):
```
## Session Start

Governing axiom: Documentation-First — primary endogenous source: AGENTS.md § Commit Discipline.

Activated scratchpad at .tmp/docs-claude-code-hooks/2026-03-18.md. No prior checkpoints today.
Workplan exists at docs/plans/2026-03-17-sprint-18-research-consolidation.md — check for Phase assignments.
```

### Best Practice 2: settings.json Hooks for Deterministic Gate Enforcement

**Pattern**: Use `prompt` type hooks at Stop/PreCompact to enforce multi-criteria gates that simple pre-commit hooks cannot express.

**Example** (Stop hook for phase gating):
```json
{
  "id": "Stop",
  "type": "prompt",
  "trigger": "on_request_stop",
  "action": "Check before stopping:\n1. git status clean (no uncommitted changes)?\n2. ## Pre-Compact Checkpoint present in scratchpad since last phase?\n3. ruff check passes on scripts/?\n4. Any new D4 research docs have all ## Recommendations items tracked as issues?\nReturn: APPROVED:<phase-name> or REQUEST CHANGES — [criterion number: reason]"
}
```

**Why this matters**: The `Stop` hook can evaluate whether Pre-Compact Checkpoint was written, check AC checkboxes in the scratchpad, confirm PR status checks passed — logic that pure pre-commit hooks cannot reach.

### Best Practice 3: Don't Repeat Governance Instructions

**Anti-pattern**:
```
Agent prompt: "Before starting, read AGENTS.md § Commit Discipline.
Here's what it says: [200-word paraphrase]..."
```

**Canonical pattern**:
```
Agent prompt: "Before starting, read AGENTS.md § Commit Discipline.
It is linked in CLAUDE.md § Commit Discipline."
```

Why: CLAUDE.md is the single source of truth for governance references. Repeating governance text in agent prompts causes encoding drift (paraphrase erosion). Link to CLAUDE.md or AGENTS.md instead.

### Best Practice 4: Narrow Hooks, Compressed Returns

**Pattern**: Keep each hook action ≤ 200 words; return from hooks ≤ 1 line (for script hooks) or ≤ 5 lines (for prompt hooks).

**Example** (good SessionStart hook):
```json
{
  "id": "SessionStart",
  "type": "script",
  "action": "uv run python scripts/prune_scratchpad.py --init"
}
```
Returns: `Scratchpad ready: .tmp/<branch>/<date>.md (lines: 0)`

**Example** (bloated — anti-pattern):
```json
{
  "id": "SessionStart",
  "type": "prompt",
  "action": "Initialize the session. Check the active scratchpad. Read AGENTS.md and CLAUDE.md.
           Check if there's a workplan. If not, ask the user what phase to start. Then..."
}
```
Common result: agent writes a 50-line response; compaction pressure increases.

### Best Practice 5: Use `.claude/settings.local.json` for Dev Overrides

**Pattern**: Project-level hooks go in `.claude/settings.json` (committed). Developer-specific permissions or hooks go in `.claude/settings.local.json` (gitignored).

**Example** (.claude/settings.local.json):
```json
{
  "permissions": {
    "allow": [
      "Bash(brew *)",
      "Bash(open *)"
    ]
  },
  "hooks": [
    {
      "id": "SessionStart_DevOverride",
      "type": "script",
      "action": "open -a Terminal /Users/myname/my-iterm-profile.sh"
    }
  ]
}
```

**Why**: Committed `.claude/settings.json` defines the project governance; `.local.json` allows developers to customize their environment without affecting the team's shared configuration.

---

## 6. Copy-Paste-Ready Examples

### Example 1: Minimal CLAUDE.md for a New Project

```markdown
# CLAUDE.md — Project Governance

This file is read by Claude Code at session start.

## Governing Constraints

All agent behavior is governed by:
1. [AGENTS.md](AGENTS.md) — operational constraints
2. [MANIFESTO.md](MANIFESTO.md) — foundational axioms

Read [AGENTS.md](AGENTS.md) before your first action.

## Session Start

1. Run `uv run python scripts/prune_scratchpad.py --init`
2. Write `## Session Start` to scratchpad: "Axis: [axiom name] — Source: [doc name]"
3. Check `docs/plans/` for an existing workplan

## File Writing

Never use heredocs (`cat >> file << 'EOF'`). Use `create_file` or `replace_string_in_file` tools only.

## Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(scope): description
fix(scope): description
docs(scope): description
```

Scopes: `scripts`, `agents`, `docs`, `tests`, `ci`

## Pre-Commit

Run before git commit:
```bash
uv run ruff check scripts/ tests/
uv run pytest tests/ -x -q
```
```

### Example 2: Basic Hooks Configuration (.claude/settings.json)

```json
{
  "project": {
    "name": "dogma",
    "description": "EndogenAI Workflows governance framework"
  },
  "hooks": [
    {
      "id": "SessionStart",
      "type": "script",
      "trigger": "on_session_start",
      "description": "Initialize scratchpad at session open",
      "action": "uv run python scripts/prune_scratchpad.py --init"
    },
    {
      "id": "PreCompact",
      "type": "prompt",
      "trigger": "before_context_compaction",
      "description": "Write Pre-Compact Checkpoint before VS Code compacts context",
      "action": "Before compaction: write ## Pre-Compact Checkpoint to scratchpad with:\n1. Committed SHAs (git log --oneline -3)\n2. Next phase or blockers\n3. Any uncommitted changes (git status --porcelain)\n\nReturn only: 'Checkpoint written' or error message."
    },
    {
      "id": "Stop",
      "type": "prompt",
      "trigger": "on_request_stop",
      "description": "Phase gate: check prerequisites before stopping",
      "action": "Check these 3 criteria before stopping:\n1. git status clean? (no uncommitted changes)\n2. ## Pre-Compact Checkpoint written to scratchpad since last phase header?\n3. ruff format passes? (uv run ruff format --check scripts/ tests/)\n\nReturn APPROVED or REQUEST CHANGES — [criterion#: reason]"
    },
    {
      "id": "SessionEnd",
      "type": "prompt",
      "trigger": "on_session_end",
      "description": "Write session summary and close",
      "action": "At session close:\n1. Write ## Session Summary to scratchpad (3–5 bullet outcomes)\n2. Post progress comments on active issues (gh issue comment <num> --body-file <path>)\n3. Confirm git status clean (git log --oneline -1)\n\nReturn: 'Session closed — SHAs committed' or error."
    }
  ]
}
```

### Example 3: Advanced Phase-Gate Hook (LLM-Evaluated Prompt)

```json
{
  "id": "Stop_AdvancedGate",
  "type": "prompt",
  "trigger": "on_request_stop",
  "description": "Multi-criteria phase gate with Research-Doc gate",
  "action": "Before stopping, verify all 5 criteria:\n\n1. Git clean? Run: git status --porcelain\n   ✓ PASS: empty output\n   ✗ FAIL: any uncommitted files listed\n\n2. Pre-Compact Checkpoint written? Check scratchpad for ## Pre-Compact Checkpoint since last phase.\n   ✓ PASS: section exists with committed SHAs\n   ✗ FAIL: section missing or stale\n\n3. Ruff format clean? Run: uv run ruff format --check scripts/ tests/\n   ✓ PASS: exit code 0\n   ✗ FAIL: formatting violations listed\n\n4. if D4 research docs changed: verify ## Recommendations items are tracked.\n   Check each item: is it a GitHub issue (#NNN) or marked 'intentionally deferred'?\n   ✓ PASS: all items are tracked or marked deferred\n   ✗ FAIL: open uncovered items\n\n5. CI passed? Run: gh run list --limit 3\n   ✓ PASS: recent runs show 'completed successfully' (no red Xs)\n   ✗ FAIL: failed or pending runs\n\nReturn APPROVED or REQUEST CHANGES — list any failing criteria with remediation step."
}
```

### Example 4: Developer-Local Overrides (.claude/settings.local.json)

```json
{
  "permissions": {
    "allow": [
      "Bash(brew install *)",
      "Bash(brew upgrade *)",
      "Bash(open -a *)",
      "Git(git push origin main)"
    ]
  },
  "hooks": [
    {
      "id": "SessionStart_DevLocal",
      "type": "script",
      "trigger": "on_session_start",
      "action": "source ~/.bashrc && uv sync"
    }
  ],
  "preferences": {
    "context_budget_target": 80000,
    "scratchpad_prune_threshold": 3000,
    "allow_force_push": false
  }
}
```

---

## 7. Troubleshooting Common Hook Configuration Issues

### Issue: Hook Does Not Fire

**Symptom**: Agent reports `SessionStart` hook did not run; scratchpad not initialized.

**Diagnosis**:
1. Check `.claude/settings.json` exists at project root: `ls -la .claude/settings.json`
2. Validate JSON syntax: `jq . .claude/settings.json` (should return no errors)
3. Confirm hook `id` matches expected trigger name: look for `id: "SessionStart"` under `hooks`
4. Check Claude Code version: hooks require Claude Code v1.2+

**Fix**:
```bash
# Validate JSON
jq . .claude/settings.json

# If validation fails, fix the JSON and retry
# If .claude/ folder doesn't exist, create it:
mkdir -p .claude
touch .claude/settings.json

# Paste a minimal hooks config back (see Example 2 above)
```

### Issue: Hook Runs But Action Fails Silently

**Symptom**: SessionStart hook fires, but `prune_scratchpad.py --init` doesn't create the scratchpad file.

**Diagnosis**:
1. SSH into the workspace and run the command manually: `uv run python scripts/prune_scratchpad.py --init`
2. Check for Python path issues: `which python` vs. `which uv`
3. Check for script errors: `uv run python scripts/prune_scratchpad.py --help`

**Fix**:
```bash
# Test the script outside Claude Code
cd /path/to/dogma
uv run python scripts/prune_scratchpad.py --init --debug

# If it works locally, the issue is Claude Code's execution environment.
# Try using an absolute path in the hook:
"action": "cd /path/to/dogma && uv run python scripts/prune_scratchpad.py --init"
```

### Issue: Stop Hook Accepts Phase When AC Checkboxes Are Not Marked

**Symptom**: Stop hook returns APPROVED, but acceptance criteria are unchecked in the scratchpad.

**Diagnosis**:
1. The Stop hook prompt is evaluating `## Pre-Compact Checkpoint` but not reading the scratchpad directly
2. The hook is returning a generic APPROVED without AC verification

**Fix**: Update the Stop hook prompt to include:
```json
{
  "id": "Stop",
  "type": "prompt",
  "action": "Before approving, fetch scratchpad from disk with: cat .tmp/<branch>/<date>.md\nSearch for '[ ]' unchecked boxes. Count them.\nReturn APPROVED only if: all criteria checks pass AND no unchecked [ ] boxes found in AC section.\nIf unchecked boxes exist, return REQUEST CHANGES — [N unchecked AC items in section]"
}
```

### Issue: Compaction Lost Session Context — PostCompact Hook Not Firing

**Symptom**: After compaction, agent doesn't remember which phase was active or what the next step is.

**Diagnosis**:
1. PostCompact hook is missing or disabled in `.claude/settings.json`
2. Hook fires but agent doesn't execute the "re-read scratchpad" instruction

**Fix**: 
1. Add PostCompact hook:
```json
{
  "id": "PostCompact",
  "type": "prompt",
  "trigger": "after_context_compaction",
  "action": "After compaction, re-read from disk:\n1. cat .tmp/<branch>/<date>.md (get latest scratchpad state)\n2. cat docs/plans/*.md (get active workplan)\n3. git log --oneline -5 (get recent commits)\n\nThen write orientation bullet to scratchpad: 'Post-Compact Reorientation: [Active phase, next step, any blockers]'"
}
```

2. Verify compaction is NOT suppressed in workspace settings:
```json
// .vscode/settings.json
"[claude]": {
  "disableCompaction": false  // Ensure this is false or absent
}
```

### Issue: CLAUDE.md Changes Not Reflected in Session

**Symptom**: Agent says "CLAUDE.md says X", but you recently changed it to Y in the file.

**Diagnosis**: CLAUDE.md is read once at session start. Changes to CLAUDE.md during a session are not automatically re-read.

**Fix**: 
1. Read CLAUDE.md explicitly during session: `cat CLAUDE.md`
2. Or start a new Claude Code session to pick up the updated file
3. Or use a script hook to re-read CLAUDE.md at specific points (e.g., PreCompact):
```json
{
  "id": "PreCompact_RereadCLAUDE",
  "type": "script",
  "action": "cat CLAUDE.md | head -20"  // Force re-read
}
```

### Issue: .claude/settings.local.json Overrides Not Loading

**Symptom**: Developer-specific hooks defined in `.local.json` don't fire; only `.settings.json` hooks work.

**Diagnosis**: Claude Code loads `.settings.json` but may not load `.local.json` depending on the file precedence order.

**Fix**: Verify both files exist and are valid JSON:
```bash
ls -la .claude/settings*.json
jq . .claude/settings.json
jq . .claude/settings.local.json

# If .local.json is not loading, try explicit path in workspace settings:
# .vscode/settings.json:
{
  "claude.settings": {
    "configFiles": [".claude/settings.json", ".claude/settings.local.json"]
  }
}
```

---

## 8. Maintenance & Evolution

### When to Update CLAUDE.md

- Core governance constraints change (e.g., new axiom, new session lifecycle step)
- File-writing guardrails evolve (e.g., new heredoc patterns discovered)
- Toolchain commands change (new `uv` syntax, new script names)

**Cadence**: Once per 1–2 sprints; updated by project lead or governance team.

### When to Update .claude/settings.json

- New lifecycle event needs a hook (e.g., research review gate)
- Hook action becomes stale (e.g., script path changes)
- Threshold parameters need adjustment (e.g., scratchpad prune size)

**Cadence**: Per-sprint or as-needed; updated by DevOps or phase lead.

### When to Use Agent Role Files (.agent.md)

- Need to restrict a specific agent's tool scope
- Tool scope is different from the default Orchestrator
- Want to document handoff routing and inter-agent dependencies

**Cadence**: Per-agent role creation or massive tool scope shift; stable once defined.

### When to Use SKILL.md Files

- A procedural workflow is reused across 2+ agents or invoked on-demand
- The procedure is stable and well-tested (not experimental)
- The procedure can be explained as a standalone guide

**Cadence**: On-demand; typical skills are stable once written; rarely modified.

---

## 9. Summary: Quick Decision Reference

| Need | Pattern | File | Frequency |
|------|---------|------|-----------|
| Session-wide governance text | CLAUDE.md | `/CLAUDE.md` | 1–2 sprints |
| Auto-run script on session open | settings.json hook (script) | `.claude/settings.json` | Per-sprint |
| LLM-evaluated phase gate | settings.json hook (prompt) | `.claude/settings.json` | Per-sprint |
| Restrict agent tool scope | Agent role file | `.github/agents/*.agent.md` | Per-agent |
| Reusable procedural knowledge | SKILL.md | `.github/skills/*/SKILL.md` | On-demand |
| Developer-local overrides | .local.json | `.claude/settings.local.json` | Per-developer |

---

## 10. See Also

- [CLAUDE.md](../../CLAUDE.md) — Example CLAUDE.md at repo root
- [AGENTS.md](../../AGENTS.md) — Governance axioms and constraints
- [claude-code-integration.md](../guides/claude-code-integration.md) — Detailed hook activation walkthrough
- [session-management SKILL](../../.github/skills/session-management/SKILL.md) — Full session lifecycle procedure
- [Conventional Commits](https://www.conventionalcommits.org/) — Commit message format reference
