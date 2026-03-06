# Working with Agents

A guide to authoring, using, and extending the VS Code Copilot agent fleet.

---

## What Are Agents?

VS Code Copilot custom agents (`.agent.md` files) are reusable, governed AI personas that appear in the Copilot Chat dropdown. Each agent:

- Has a **defined scope and posture** (what it can do and what tools it can use)
- Reads **endogenous sources** before acting (project docs, existing scripts, session scratchpad)
- Follows **documented conventions** (AGENTS.md hierarchy)
- **Hands off** to downstream agents rather than overreaching its scope

Agents are not magic — they are documented, reviewable, constrained workers. The value is in the constraints and the encoded knowledge they read before acting.

---

## Using Agents

### In VS Code Copilot Chat

Invoke an agent by name in the chat input:

```
@Executive Scripter audit scripts/ for gaps
@Executive Automator set up a file watcher for docs/
```

### Session Start Ritual

1. Open the repo in VS Code
2. Open Copilot Chat
3. Start the scratchpad watcher: `uv run python scripts/watch_scratchpad.py`
4. Initialize today's session file: `uv run python scripts/prune_scratchpad.py --init`
5. Invoke the appropriate agent for your task

### Agent Selection Guide

| Task | Agent to invoke |
|------|----------------|
| Task you've done >2 times interactively | **Executive Scripter** |
| Need a file watcher, hook, or CI job | **Executive Automator** |
| Unsure which agent to use | Describe the task; ask Copilot Chat for a recommendation |

---

## Agent Posture

Every agent operates at one of three postures:

| Posture | What it can do | Examples |
|---------|---------------|---------|
| **Read-only** | Read files, search codebase, audit | Review agents, plan agents |
| **Read + create** | Read + write new files | Scaffold agents |
| **Full execution** | Read + write + run commands + invoke other agents | Executive agents |

Agents should never carry more tools than their posture requires. If an agent is attempting something outside its posture, it should escalate rather than try to force it.

---

## Handoff Patterns

Every agent hands off to at least one downstream agent. The standard pattern:

```
Action agent → Review → GitHub (commit)
Executive → Sub-agent A → [Back to Executive] → Sub-agent B → Review → GitHub
```

The **takeback pattern** is recommended: each sub-agent returns control to the executive after completing its task, rather than chaining directly to the next sub-agent. This keeps the executive in oversight at every step.

---

## Authoring a New Agent

Before creating a new agent:

1. Check [`.github/agents/README.md`](../../.github/agents/README.md) — does an existing agent cover the need?
2. Read [`.github/agents/AGENTS.md`](../../.github/agents/AGENTS.md) for the frontmatter schema and conventions
3. Choose the minimum posture that fulfils the agent's role
4. Follow the body structure: role statement → endogenous sources → workflow → guardrails

### Minimum Viable Agent Template

```yaml
---
name: My Agent
description: One sentence ≤ 200 characters describing what this agent does.
tools:
  - search
  - read
handoffs:
  - label: Back to Executive
    agent: Executive Name
    prompt: "Task complete. Here is a summary: ..."
    send: false
---

You are the **My Agent** for the EndogenAI Workflows project.

## Endogenous Sources — Read Before Acting

1. [`AGENTS.md`](../../AGENTS.md)
2. (any other files this agent must read first)

## Workflow

1. Step one
2. Step two

## Guardrails

- Never do X
- Escalate to Y if Z
```

---

## The Endogenous Sources Requirement

Every agent must list the files it reads **before acting**. This is not boilerplate — it is the mechanism by which the agent fleet bootstraps from encoded knowledge rather than from zero context.

Typical sources:
- Root `AGENTS.md` — guiding constraints
- `scripts/README.md` — what scripts already exist (check before creating new ones)
- Relevant `docs/guides/` — established best practices
- Active session scratchpad — context from the current session

---

## Escalation and Insufficient Posture

When a sub-agent cannot complete a task (posture limit, context too large, specialist knowledge needed), it must **not fail silently**. It must:

1. Write a structured escalation note to the session scratchpad:
   ```markdown
   ## <AgentName> Escalation
   - **Current state**: ...
   - **Blocking issue**: ...
   - **Recommended action**: ...
   ```
2. Use the "Back to [Executive]" handoff to return control

The executive reads the escalation note, decides what to do next (re-delegate, create a new specialist agent, or handle directly), and proceeds.

---

## Fleet Governance

The agent fleet is governed by the `AGENTS.md` hierarchy:

```
AGENTS.md (root)           — global constraints for all agents
  docs/AGENTS.md           — documentation work constraints
  .github/agents/AGENTS.md — agent authoring constraints
```

Any change to an existing agent should be reviewed by a peer before committing. Any new agent should be added to [`.github/agents/README.md`](../../.github/agents/README.md).
