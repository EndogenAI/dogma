# Agent Fleet Catalog

VS Code Copilot custom agents for the EndogenAI Workflows project.
Each `.agent.md` file appears in the Copilot chat agents dropdown automatically.

For authoring rules — frontmatter schema, posture table, handoff patterns — see [`.github/agents/AGENTS.md`](./AGENTS.md).

Typical workflow: **Plan → (approve) → Implement → (complete) → Review → GitHub (commit)**

---

## Scripting & Automation Agents

Enforce the programmatic-first principle — encode repeated tasks as scripts and non-agent automation before performing them a third time interactively.

| Agent | File | Posture | Trigger | Handoffs |
|-------|------|---------|---------|----------|
| **Executive Scripter** | `executive-scripter.agent.md` | full | Identify tasks done >2 times interactively; audit `scripts/` for gaps; write or extend scripts | Review, GitHub, Executive Automator |
| **Executive Automator** | `executive-automator.agent.md` | full | Design file watchers, pre-commit hooks, CI tasks, VS Code background tasks; first escalation for event-driven automation | Review, GitHub, Executive Scripter |

---

## Adding a New Agent

1. Read [`.github/agents/AGENTS.md`](./AGENTS.md) for the frontmatter schema and naming conventions.
2. Create `.github/agents/<name>.agent.md`.
3. Add the agent to the correct table above.
4. Commit: `feat(agents): add <name> agent`.

---

## Supporting Scripts

Scripts that back agents in this fleet. All scripts support `--dry-run`.

| Script | Purpose |
|--------|---------|
| `scripts/prune_scratchpad.py` | Manage cross-agent scratchpad session files in `.tmp/` |
| `scripts/watch_scratchpad.py` | File watcher — auto-annotates `.tmp/*.md` on change |
