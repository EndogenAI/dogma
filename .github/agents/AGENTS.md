# .github/agents/AGENTS.md

> This file narrows the constraints in the root [`AGENTS.md`](../../AGENTS.md).
> It does not contradict any root constraint — it only adds agent-authoring-specific rules.

---

## Programmatic-First

> The **programmatic-first** constraint from [root AGENTS.md](../../AGENTS.md#programmatic-first-principle) applies here without exception.

Before authoring, reviewing, or auditing agents interactively, check `scripts/` for existing scaffold, validation, or audit scripts.
Agent scaffolding, frontmatter validation, and fleet compliance checks should be encoded as scripts — extend them, don't repeat steps by hand.
Escalate scripting gaps to the `Executive Scripter`; automation design (watchers, hooks) to the `Executive Automator`.

**Research sessions**: before delegating to any Scout, pre-warm the source cache:

```bash
uv run python scripts/fetch_all_sources.py
```

This is the **fetch-before-act** posture. Scouts read cached `.md` files via `read_file` rather than re-fetching pages through the context window. See [`scripts/README.md`](../../scripts/README.md#scriptsfetch_all_sourcespy) for full usage.

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
Executive  →  sub-agents  →  [Back to Executive]  →  Review  →  GitHub
```

- An executive agent orchestrates its fleet and must hand off to Review before committing.
- Sub-agents return control to their executive via takeback — they do not chain directly to the next sub-agent.
- Read-only agents (review, plan, audit) hand off to action agents or GitHub.
- The `send: false` default is strongly preferred — avoid auto-submitting prompts.

### Takeback Gates (Recommended Pattern)

The most reliable delegation pattern is the **takeback**: a sub-agent's final handoff returns control to the executive.

```
Executive → Sub-agent A → [Back to Executive] → Sub-agent B → [Back to Executive] → Review
```

**Anti-pattern — free-chaining** (`A → B → C → D → Review`): loses the executive's oversight role.

### Evaluator-Optimizer Loop (Executive Pattern)

Executive agents should include handoff buttons that target **themselves** — one per phase boundary. These fire after a sub-agent returns and force a deliberate review step before the next delegation.

```yaml
- label: "✓ Scout done — review & decide"
  agent: Executive Researcher      # targets itself
  prompt: "Scout output is in the scratchpad. Review: ≥3–5 sources? No synthesis?
           If satisfied, delegate to Synthesizer. If not, re-delegate Scout."
  send: false
```

**Why evaluator-optimizer loop**: the executive absorbs the sub-agent's output, evaluates it against gates, and enriches the next prompt with that context before delegating again. The handoff button is the mechanism that enforces the review pause.

### Prompt Enrichment Chain

Each delegation level enriches the prompt with progressively denser project context:

```
Human (sparse intent)
  → Executive (reads scratchpad + OPEN_RESEARCH.md + AGENTS.md → richer, grounded prompt)
    → Sub-agent (reads specialist sources → precisely scoped instruction)
      → Specialist
```

This is the endogenous-first principle in practice: context already encoded in the repo is translated into each delegation, so agents do not re-discover it interactively.

**Implication for prompt authoring**: handoff `prompt:` fields on executive agents should leave room for interpretation at the receiving end — specific enough to convey context, general enough that the sub-agent can apply its own encoded knowledge.

### Quasi-Encapsulated Sub-Fleets

Sub-agents **default to returning to their executive** (takeback), but may escalate directly to another agent in exceptional cases — when the executive's context is insufficient or the issue crosses fleet boundaries.

```
Normal:     Sub-agent → [Back to Executive]
Escalation: Sub-agent → Executive Docs  (cross-fleet, exceptional)
Escalation: Sub-agent → Review          (quality issue requiring immediate gate)
```

This hybrid model gives fleets quasi-autonomy while preserving executive oversight as the default. Full encapsulation (sub-agents can never escalate) and full openness (sub-agents chain freely) are both anti-patterns.

---

## Body Structure Requirements

Every agent body must follow this structure:

1. **Bold role statement**: `You are the **X agent** for the EndogenAI Workflows project.`
2. **Endogenous sources section**: list every file the agent must read before acting, with relative links.
3. **Workflow or checklist**: numbered steps or a role-specific checklist.
4. **Guardrails section**: explicit list of what the agent must NOT do.

---

## Naming Conventions

### Convention Propagation Rule

When a new authoring convention is introduced for agent files, check whether it must also appear in the root `AGENTS.md` or `docs/AGENTS.md`:

- If it affects how **all agents communicate** (scratchpad, handoffs) → update root `AGENTS.md`
- If it affects **documentation structure** (how findings are written up) → update `docs/AGENTS.md`
- If it is **agent-file-authoring-only** (frontmatter, section order) → this file is sufficient

Run `find . -name 'AGENTS.md' | grep -v node_modules` to see all narrowing files before closing a PR that introduces a new convention.

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
