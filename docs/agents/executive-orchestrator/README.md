# Executive Orchestrator — Extended Documentation

This document provides the canonical decision tree, tool matrix, and a worked session example for the Executive Orchestrator agent.

For BDI content (beliefs, workflow, guardrails), see [`.github/agents/executive-orchestrator.agent.md`](../../../.github/agents/executive-orchestrator.agent.md).

---

## 1. Delegation Decision Tree

Use this tree to decide whether to act directly or delegate. Delegation is the default.

```
┌─ Is there a specialist agent for this domain?
│  ├─ Yes  → Delegate to them (see Domain Routing table below)
│  └─ No   → Continue to step 2
│
├─ Would the output benefit from isolation (clean context, focused expertise)?
│  ├─ Yes  → Delegate
│  └─ No   → Continue to step 3
│
├─ Is this read-only (no persistent state changes)?
│  ├─ Yes  → OK to act directly, but keep it short
│  └─ No   → Continue to step 4
│
└─ Can you complete it in < 5 minutes without context burn?
   ├─ Yes  → OK to act directly; document in scratchpad
   └─ No   → Delegate
```

### Domain Routing Table

| Task domain | Delegate to |
|-------------|-------------|
| Research, source gathering | Executive Researcher → Research Scout fleet |
| Documentation writing / editing | Executive Docs |
| Scripting, automation design | Executive Scripter, Executive Automator |
| Fleet agent authoring / audit | Executive Fleet |
| Release coordination, versioning | Release Manager |
| Issue triage, labels, milestones | Issue Triage, Executive PM |
| Git and GitHub operations | GitHub Agent |
| CI health, test coverage gaps | CI Monitor, Test Coordinator |

### Act-Directly Allowlist

These actions are always OK for the Orchestrator to perform without delegating:

- `git status`, `git log --oneline`, `git branch -vv`
- `gh pr view`, `gh issue view`
- Writing `## Phase N Output` and `## Pre-Compact Checkpoint` to scratchpad
- Updating workplan status markers (`⬜` → `⏳` → `✅`)
- Temp file pre-use validation: `test -s /tmp/file`, `file /tmp/file | grep UTF-8`

### Act-Directly Anti-Patterns

Never do these directly:

- Edit docs, code, or config files (delegate to specialist)
- Execute research or synthesis (delegate to Researcher fleet)
- Interpret test failures or lint output (delegate to Review or Scripter)
- Author or audit agent files (delegate to Fleet)
- Run `git commit`, `git push`, `gh issue`, `gh pr` (delegate to GitHub Agent)

---

## 2. Tool Matrix

| Category | Tools used | Notes |
|----------|-----------|-------|
| State queries | `execute/runInTerminal` (read-only cmds) | `git status`, `gh issue view` |
| Scratchpad management | `edit/editFiles`, `edit/createFile` | `.tmp/<branch>/<date>.md` writes |
| Workplan updates | `edit/editFiles` | `docs/plans/*.md` status markers |
| Subagent invocation | `agent/runSubagent` | All domain work routes here |
| File verification | `read/readFile`, `search/listDirectory` | Confirming deliverable existence |
| Temp file validation | `execute/runInTerminal` | `test -s`, `file | grep UTF-8` |
| Source caching | `execute/runInTerminal` | `uv run python scripts/fetch_all_sources.py` |

The Orchestrator does **not** use search or web tools for research — those belong to the Research Scout.

---

## 3. Worked Example Session

This trace shows a complete Orchestrator session: Pre-Task Checkpoint → Delegate → Return Validation Gate.

### Scenario

Branch: `feat/add-new-guide`. Task: create `docs/guides/new-topic.md` via Executive Docs, then commit via GitHub Agent.

---

### Step 1 — Pre-Task Commitment Checkpoint

Before any action, the Orchestrator asks: "Is this substantive domain work or coordination?"

**Answer**: Writing a guide = substantive docs work → **delegate to Executive Docs**.

```bash
# Verify scratchpad is initialized
uv run python scripts/prune_scratchpad.py --init
```

Writes to scratchpad:
```markdown
## Session Start

Governing axiom: Endogenous-First. Primary endogenous source: docs/guides/ — existing
guide patterns to extend rather than re-author.
```

---

### Step 2 — Delegation (Focus-on-Descent)

The Orchestrator applies the Pre-Delegation Checklist:

- [x] **Scope Clarity** — "Create docs/guides/new-topic.md with sections X, Y, Z"
- [x] **Output Format Specified** — "Return: one bullet per section created, ≤500 tokens"
- [x] **Success Criteria Clear** — "File exists at path; validate_synthesis.py passes; no guardrails removed"

Delegation prompt (Layer 2 structure):

```
**Goal**: Create docs/guides/new-topic.md

**Scope**: New file only. Do not modify MANIFESTO.md, existing guides, or any script files.

**Tasks**:
1. Read docs/guides/workflows.md for structural patterns
2. Create docs/guides/new-topic.md with sections: Overview, Workflow, Guardrails
3. Validate: uv run python scripts/validate_synthesis.py docs/guides/new-topic.md

**Output Format**: Bullets only — "Created [file] with sections [list]". ≤500 tokens.

**Return Statement**: Return only: file path, section list, validation result.
```

---

### Step 3 — Return Validation Gate

Executive Docs returns:

```
Created docs/guides/new-topic.md with sections: Overview, Workflow, Guardrails.
validate_synthesis.py: exit 0.
```

The Orchestrator runs the Return Validation Gate:

| Check | Result |
|-------|--------|
| Token count | ~30 tokens — within ceiling ✅ |
| Format match | Bullets as specified ✅ |
| Signal preservation | File path + sections + validation result all present ✅ |
| Commit verification | Not yet committed — confirm after GitHub Agent |

**Decision**: Proceed to Review → GitHub Agent.

---

### Step 4 — Review Gate

Orchestrator delegates to Review agent with explicit acceptance criteria:

```
Validate docs/guides/new-topic.md against 3 criteria:
1. File contains Overview, Workflow, and Guardrails H2 headings
2. No guardrail from AGENTS.md has been silently removed or softened
3. validate_synthesis.py exits 0

Return: APPROVED or REQUEST CHANGES — [criterion number: one-line reason]
```

Review returns: `APPROVED`

---

### Step 5 — Commit via GitHub Agent

Orchestrator delegates to GitHub Agent:

```
Commit docs/guides/new-topic.md.
Message: "docs(guides): add new-topic guide"
Branch: feat/add-new-guide
Return: commit SHA
```

Orchestrator verifies:

```bash
git log --oneline -1
# Expected: <sha> docs(guides): add new-topic guide
```

Writes Phase Output to scratchpad and updates workplan.
