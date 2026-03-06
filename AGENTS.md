# AGENTS.md

Guidance for AI coding agents working in this repository.

---

## Guiding Constraints

- **Endogenous-first**: scaffold from existing system knowledge *and* from external best practices — do not author from scratch in isolation, and do not ignore well-maintained external tools. Synthesize external wisdom into the encoded substrate.
- **Programmatic-first**: prefer encoding repeated or automatable tasks as scripts over interactive agent steps.
  If you have done a task twice interactively, the third time is a script. See [Programmatic-First Principle](#programmatic-first-principle).
- **Documentation-first**: every change to a workflow, agent, or script must be accompanied by clear documentation.
- **Local compute first**: minimize token usage; prefer local models and pre-encoded scripts over re-discovering context interactively.
- **Minimal posture**: agents carry only the tools required for their stated role.
- **Commit discipline**: small, incremental commits following [Conventional Commits](https://www.conventionalcommits.org/).

---

## Programmatic-First Principle

**Every repeated or automatable task must be encoded as a script before it is performed a third time interactively.**

This is a constraint on the entire agent fleet, not an optional preference. More layers of encoding produce more value-adherence among agents, leading to more deterministic sessions and development cycles.

### Decision Criteria

| Situation | Action |
|-----------|--------|
| Task performed once interactively | Note it; consider scripting |
| Task performed twice interactively | Script it before the third time |
| Task is a validation or format check | Script it immediately; CI should enforce it too |
| Task involves reading many files to build context | Pre-compute and cache — encode as a script |
| Task generates boilerplate from a template | Generator script is more reliable than prompting |
| Task could break something if done wrong | Script it with a `--dry-run` guard |
| Task is one-off and genuinely non-recurring | Interactive is acceptable — document the assumption |

### What This Means for Agents

- **Check `scripts/` first** before performing a multi-step task interactively.
- **Extend, don't duplicate** — if a script partially covers your need, extend it.
- **Propose new scripts proactively** — if you perform an investigation or transformation that required significant context to execute, encapsulate it as a script and commit it so future sessions start with that knowledge encoded.
- **Automation ≠ agent** — file watchers, pre-commit hooks, and CI tasks are preferred over agent-initiated repetition. The `Executive Automator` agent is the first escalation point for automation design. The `Executive Scripter` agent is the first escalation point for scripting gaps.
- **Document at the top** — every script must open with a docstring or comment block describing its purpose, inputs, outputs, and usage example.

### Scratchpad Watcher — Canonical Example

The scratchpad auto-annotator (`scripts/watch_scratchpad.py`) exemplifies this principle:
- A repeated manual task (annotating H2 headings with line numbers after every write) is encoded as a file watcher.
- Agents do not run it — it runs automatically whenever a `.tmp/*.md` file changes.
- The result (line-range annotations in heading text) is durable even if links break.
- Run `uv run python scripts/watch_scratchpad.py` or start the VS Code task **Watch Scratchpad**.

---

## Python Tooling

**Always use `uv run` — never invoke Python or package executables directly.**

```bash
# Correct
uv run python scripts/prune_scratchpad.py --init
uv run python scripts/watch_scratchpad.py

# Wrong — do not do this
python scripts/prune_scratchpad.py
.venv/bin/python scripts/prune_scratchpad.py
```

`uv run` ensures the correct locked environment is used regardless of shell state.

---

## Commit Discipline

**Make small, incremental commits** — one logical change per commit, not one large commit at the end of a session.

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

| Type | When to use |
|------|-------------|
| `feat` | new functionality |
| `fix` | bug or correction |
| `docs` | documentation only |
| `refactor` | restructuring without behaviour change |
| `chore` | tooling, config, scripts |

Good commit cadence:
1. Docs change → commit
2. Script change → commit
3. Agent change → commit

---

## Agent Communication

### `.tmp/` — Per-Session Cross-Agent Scratchpad

`.tmp/` at the workspace root is the **designated scratchpad folder** for cross-agent context preservation. It is gitignored and never committed.

**Folder structure:**
```
.tmp/
  <branch-slug>/          # one folder per branch
    _index.md             # one-line stubs of all closed sessions on this branch
    <YYYY-MM-DD>.md       # one file per session day — the active scratchpad
```

**`<branch-slug>`** = branch name with `/` replaced by `-`

Rules:
- Each delegated agent **appends** findings under a named heading: `## <Phase> Results` or `## <Task> Output`. Never overwrite another agent's section.
- The executive **reads today's session file first** before delegating to avoid re-discovering context another agent already gathered.
- At session end, the executive writes a `## Session Summary` section so the next session starts with an orientation point.
- Use the active session file for inter-agent handoff notes, gap reports, and aggregated sub-agent results.

### Size Guard and Archive Convention

| Situation | Action |
|-----------|--------|
| Session file < 200 lines | No action needed |
| Session file ≥ 200 lines | Run `uv run python scripts/prune_scratchpad.py` |
| Session end | Write `## Session Summary`, then run `uv run python scripts/prune_scratchpad.py --force` |
| New session day | Run `uv run python scripts/prune_scratchpad.py --init` |

### Scope-Narrowing in Delegations

When delegating with a restricted scope, **state exclusions explicitly** in the delegation prompt. Agents default to full scope; they need explicit constraints to narrow it.

Good example:
> "Edit `.md` files only — do not modify scripts, config, or agent files."

---

## When to Ask vs. Proceed

**Default posture: stop and ask before any ambiguous or irreversible action.**

Ask when:
- Requirements or acceptance criteria are unclear
- A change would delete, rename, or restructure existing files
- The correct approach involves a genuine trade-off the user should decide

Proceed when:
- The task is unambiguous and reversible
- A best-practice default exists and is well-established in this codebase
- The action can be undone with `git revert` or a follow-up commit

When proceeding under ambiguity, **document the assumption inline** (code comment or commit message body) so it can be reviewed and corrected.

---

## Agent Fleet Overview

See [`.github/agents/README.md`](.github/agents/README.md) for the full agent catalog.

Key agents for this repo:

| Agent | Trigger |
|-------|---------|
| **Executive Scripter** | Identify tasks done >2 times interactively; audit `scripts/` for gaps |
| **Executive Automator** | Design file watchers, pre-commit hooks, CI tasks |

---

## Guardrails

**Never do these without explicit instruction:**

- Edit any lockfile by hand
- Commit secrets, API keys, or credentials of any kind
- `git push --force` to `main`
- Delete or rename committed script or agent files without a migration plan

**Prefer caution over assumption for:**

- Any change that renames or restructures existing documentation
- Adding new agents (follow the agent authoring guide in `.github/agents/AGENTS.md`)
- Any change to the `MANIFESTO.md` (it represents core project dogma)
