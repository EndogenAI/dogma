# Agent Documentation — Extended Standard

This directory contains per-role extended documentation for the agent fleet. It supplements the `.agent.md` role files in [`.github/agents/`](../../.github/agents/) with:

- **Canonical decision trees** — when to act directly vs. delegate; when to invoke this agent
- **Tool matrices** — what tools the agent uses for each category of work
- **Worked examples** — end-to-end session traces showing observable agent behavior in practice

---

## Why This Exists

`.agent.md` files encode *who* an agent is — their BDI structure (Beliefs, Desires, Intentions). Those files are intentionally concise and declarative. This documentation layer encodes *how* agents work in practice: the observable patterns, worked session examples, and decision criteria that are too long and concrete for a role file.

The two layers are complementary and non-redundant:

| Layer | File | Encodes |
|-------|------|---------|
| Role definition | `.github/agents/<name>.agent.md` | BDI: beliefs, desires, intentions — declarative |
| Extended documentation | `docs/agents/<name>/README.md` | Decision trees, tool matrix, worked examples — concrete |

Do not duplicate BDI content in extended docs. Cross-reference the role file instead.

---

## Index

| Agent | Extended Docs | Role File |
|-------|--------------|-----------|
| Executive Orchestrator | [executive-orchestrator/](executive-orchestrator/) | [.github/agents/executive-orchestrator.agent.md](../../.github/agents/executive-orchestrator.agent.md) |
| Review | [review/](review/) | [.github/agents/review.agent.md](../../.github/agents/review.agent.md) |

---

## Fleet Catalog

For the complete agent fleet catalog (all agents, roles, triggers, handoff topology), see [`.github/agents/README.md`](../../.github/agents/README.md).

---

## Adding a New Entry

To add extended documentation for a new agent:

1. Create `docs/agents/<name>/README.md`
2. Include at minimum: decision tree or invocation guide, tool matrix, one worked example
3. Cross-reference the `.agent.md` file for BDI content — do not repeat it
4. Keep the file under 400 lines
5. Add an entry to the Index table above
