# AGENTS.md

Guidance for AI coding agents working in this repository.

---

## Guiding Constraints

These constraints govern all agent behavior. They derive from three core axioms in [`MANIFESTO.md`](MANIFESTO.md):

1. **Endogenous-First** — scaffold from existing system knowledge and external best practices
2. **Algorithms Before Tokens** — prefer deterministic, encoded solutions over interactive token burn
3. **Local Compute-First** — minimize token usage; run locally whenever possible

Additional operational constraints:

- **Minimal Posture** — agents carry only the tools required for their stated role
- **Programmatic-First** — if you have done a task twice interactively, the third time is a script. See [Programmatic-First Principle](#programmatic-first-principle).
- **Documentation-First** — every change to a workflow, agent, or script must be accompanied by clear documentation
- **Commit Discipline** — small, incremental commits following [Conventional Commits](https://www.conventionalcommits.org/) — see [`CONTRIBUTING.md#commit-discipline`](CONTRIBUTING.md#commit-discipline)

For a complete treatment of guiding principles and ethical values, read [`MANIFESTO.md#guiding-principles-cross-cutting`](MANIFESTO.md#guiding-principles-cross-cutting) and [`MANIFESTO.md#ethical-values`](MANIFESTO.md#ethical-values).

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
- **At the start of any research session, pre-warm the source cache** — run `uv run python scripts/fetch_all_sources.py` to batch-fetch all URLs from `OPEN_RESEARCH.md` and existing research doc frontmatter. This is the **fetch-before-act** posture: populate locally, then research.
- **Check `.cache/sources/` before fetching any individual URL** — use `uv run python scripts/fetch_source.py <url> --check` to see if a page is already cached as distilled Markdown. Re-fetching a cached source wastes tokens.
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
| Session file < 2000 lines | No action needed |
| Session file ≥ 2000 lines | Run `uv run python scripts/prune_scratchpad.py` |
| Session end | Write `## Session Summary`, then run `uv run python scripts/prune_scratchpad.py --force` |
| New session day | Run `uv run python scripts/prune_scratchpad.py --init` |

### `docs/plans/` — Tracked Workplans

For any multi-phase session, create a **workplan** before execution begins and commit it to `docs/plans/`.

**Naming**: `docs/plans/YYYY-MM-DD-<brief-slug>.md` (date-first for chronological sorting)

**When to create**:
- Any session with ≥ 3 phases or ≥ 2 agent delegations
- Any session spanning more than one day

**Contents** (use `docs/plans/2026-03-06-formalize-workflows.md` as the canonical template):
- Objective
- Phase plan: agent, deliverables, depends-on, status
- Acceptance criteria checklist

**Commit** the workplan at the start of the session (before Phase 1 executes), then update status markers as phases complete. This creates an auditable plan history in git, separate from the ephemeral `.tmp/` scratchpad.

### Scope-Narrowing in Delegations

When delegating with a restricted scope, **state exclusions explicitly** in the delegation prompt. Agents default to full scope; they need explicit constraints to narrow it.

Good example:
> "Edit `.md` files only — do not modify scripts, config, or agent files."

### Verify-After-Act for Remote Writes

Any command that creates or modifies a remote side effect must be immediately followed by a verification read:

| Command | Verification |
|---------|-------------|
| `gh issue create` | `gh issue list --state open --limit 5` |
| `git push` | `git log --oneline -1` |
| `gh pr create` | `gh pr view` |
| `gh issue close` | `gh issue view <number>` |

**Zero error output is not confirmation of success.** Output truncation, network timeouts, and silent API failures all produce clean exits. Always verify.

### Convention Propagation Rule

When a new convention is introduced, identify **every** `AGENTS.md` file it applies to and update them all in the same commit:

- Root `AGENTS.md` — applies to all agents
- `docs/AGENTS.md` — applies to any convention touching `docs/`
- `.github/agents/AGENTS.md` — applies to agent file authoring conventions

A convention documented only in the root file will be missed by agents operating under subdirectory scope. Check with:
```bash
find . -name 'AGENTS.md' | grep -v node_modules
```

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
| **Executive Researcher** | Start a research session; orchestrate Scout→Synthesizer→Reviewer→Archivist; spawn new area agents |
| **Executive Docs** | Update guides, top-level docs, AGENTS.md, MANIFESTO.md; codify values across documentation |
| **Executive Scripter** | Identify tasks done >2 times interactively; audit `scripts/` for gaps |
| **Executive Automator** | Design file watchers, pre-commit hooks, CI tasks |
| **Review** | Validate any changed files against AGENTS.md constraints before committing |
| **GitHub** | Commit approved changes following Conventional Commits |

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
