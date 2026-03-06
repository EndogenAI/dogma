# .github/agents/AGENTS.md

> This file narrows the constraints in the root [`AGENTS.md`](../../AGENTS.md).
> It does not contradict any root constraint — it only adds agent-authoring-specific rules.

---

## Programmatic-First

> The **programmatic-first** constraint from [root AGENTS.md](../../AGENTS.md#programmatic-first-principle) applies here without exception.

Before authoring, reviewing, or auditing agents interactively, check `scripts/` for existing scaffold, validation, or audit scripts.
Agent scaffolding, frontmatter validation, and fleet compliance checks should be encoded as scripts — extend them, don't repeat steps by hand.
Escalate scripting gaps to the `Executive Scripter`; automation design (watchers, hooks) to the `Executive Automator`.

---

## Purpose

This file governs the authoring, review, and maintenance of VS Code Copilot custom agents (`.agent.md` files) in this directory. Every agent in the fleet must comply with both the root `AGENTS.md` and the rules below.

---

## Frontmatter Schema

Agent files begin with a YAML front-matter block. The allowed fields are:

```yaml
---
name: <Display Name>            # Required. Shown in the Copilot agents dropdown. Must be unique.
description: <One-line summary> # Required. ≤ 200 characters.
argument-hint: <hint>           # Optional. Placeholder shown in the chat input box.
tools:                          # Required. Minimal subset — see posture table below.
  - <tool-id>
agents:                         # Optional. List of agent `name` values this agent may invoke.
  - <Agent Name>                # Must match the `name` field of the target agent exactly.
handoffs:                       # Required. At least one handoff per agent.
  - label: <Button text>
    agent: <Target agent name>  # Must match the `name` field of the target exactly.
    prompt: <Pre-filled prompt>
    send: false
---
```

**Validation rules:**
- `name` must be unique across all `.agent.md` files in this directory.
- `description` must be one sentence, ≤ 200 characters.
- Every `handoffs[].agent` value must match an existing agent's `name` field exactly.
- `tools` must be the **minimum** set required for the agent's posture (see below).

---

## Tool Selection by Posture

Tools are specified as **toolsets** (named bundles provided by the VS Code Copilot API).

| Posture | Permitted toolsets |
|---------|-------------------|
| **Read-only** (review, plan, audit) | `search`, `read`, `changes`, `usages` |
| **Read + create** (scaffold) | adds `edit`, `web` |
| **Full execution** (implement, debug, executive) | adds `execute`, `terminal`, `agent` |

> **`web` toolset**: Never add `web` unless the agent body contains a step that explicitly fetches a remote URL. Omit it if the agent only reads local files or runs local commands.

**Toolset contents (reference):**

| Toolset | Individual tools bundled |
|---------|--------------------------|
| `search` | `codebase`, `findFiles`, `findTestFiles`, `grep` |
| `read` | `readFile`, `problems`, `terminalLastCommand`, `listDirectory` |
| `edit` | `editFiles`, `insertEdit` |
| `web` | `fetch` (+ web search) |
| `execute` | `runInTerminal`, `getTerminalOutput`, `runTests` |
| `terminal` | `runInTerminal`, `getTerminalOutput`, `terminalLastCommand` |
| `agent` | invoke other Copilot agents by name |

---

## Handoff Graph Patterns

Every agent must hand off to at least one downstream agent. Standard patterns:

```
Action agent  →  Review  →  GitHub
Scaffold agent  →  Review  →  GitHub
Executive  →  sub-agents  →  Review  →  GitHub
```

- An executive agent orchestrates its fleet and must hand off to Review before committing.
- Sub-agents should hand off back to their executive or directly to Review/GitHub.
- Read-only agents (review, plan, audit) hand off to action agents or GitHub.
- The `send: false` default is strongly preferred — avoid auto-submitting prompts.

### Takeback Gates (Recommended Pattern)

The most reliable delegation pattern is the **takeback**: a sub-agent's final handoff returns control to the executive.

```
Executive → Sub-agent A → [Back to Executive] → Sub-agent B → [Back to Executive] → Review
```

**Anti-pattern — free-chaining** (`A → B → C → D → Review`): loses the executive's oversight role.

---

## Body Structure Requirements

Every agent body must follow this structure:

1. **Bold role statement**: `You are the **X agent** for the EndogenAI Workflows project.`
2. **Endogenous sources section**: list every file the agent must read before acting, with relative links.
3. **Workflow or checklist**: numbered steps or a role-specific checklist.
4. **Guardrails section**: explicit list of what the agent must NOT do.

---

## Naming Conventions

| Agent type | File name pattern | `name` field |
|-----------|------------------|-------------|
| Fleet executive | `<area>-executive.agent.md` | `<Area> Executive` |
| Fleet sub-agent | `<area>-<role>.agent.md` | `<Area> <Role>` |
| Workflow agent | `<verb>.agent.md` or `<noun>.agent.md` | `<Verb>` or `<Noun>` |

Use lowercase kebab-case for filenames.

---

## Verification Gate

Before committing a new or modified agent file:

```bash
# Check for name uniqueness
grep -h "^name:" .github/agents/*.agent.md | sort | uniq -d

# Verify all handoff targets resolve (manual: every `agent:` field must match a `name:`)
```

> Any session that creates or modifies `.agent.md` files should be reviewed before committing.
