# Programmatic-First Principle

> *"If you have done a task twice interactively, the third time is a script."*

---

## What Is Programmatic-First?

The programmatic-first principle is a constraint on the entire agent fleet: **any repeated or automatable task must be encoded as a committed script or automation before it is performed a third time interactively.**

This is not a preference — it is a rule. More layers of encoding produce more deterministic sessions, reduce token usage, and make future agents smarter because they start with that knowledge already baked in.

---

## Why It Matters

### Token Economics

Every interactive agent session costs tokens. When an agent re-discovers how to do something that has been done before — reads the same files, runs the same commands, reconstructs the same context — those tokens are wasted. A script encodes that discovery once. Future sessions start with it free.

### Determinism

Interactive agent steps are probabilistic. The same instruction to an agent may produce slightly different results on different runs. A script is deterministic — it does exactly what it says, every time.

### Standing on the Shoulders of Giants

The best scripts are not written from scratch — they adopt and wrap well-maintained external tools. `watchdog` for file watching, `pre-commit` for hooks, `uv` for Python environments — these are the giants. The programmatic-first principle says: adopt them, document them, and encode their usage into the project's knowledge base.

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Task performed once interactively | Note it; consider scripting |
| Task performed twice interactively | Script it before the third time |
| Task is a validation or format check | Script it immediately; CI should enforce it too |
| Task involves reading many files to build context | Pre-compute and cache — encode as a script |
| Task generates boilerplate from a template | Generator script is more reliable than prompting |
| Task could break something if done wrong | Script it with a `--dry-run` guard |
| Task requires ongoing event-driven execution | Encode as a file watcher, hook, or CI job |
| Task is one-off and genuinely non-recurring | Interactive is acceptable — document the assumption |

---

## Script vs. Automation

Not all programmatic encoding is a one-shot script. There are two categories:

### One-Shot Scripts (`Executive Scripter`)

Run on demand. Called with `uv run python scripts/<name>.py`. Examples:
- Validation scripts (`--dry-run` flag required for destructive operations)
- Scaffolding generators
- Context pre-computation scripts

### Event-Driven Automation (`Executive Automator`)

Run automatically in response to events. Examples:
- **File watchers** — react to file changes (uses Python `watchdog`)
- **Pre-commit hooks** — enforce quality gates on every commit (uses `pre-commit` framework)
- **CI jobs** — run on every push/PR (uses GitHub Actions)
- **VS Code background tasks** — auto-start dev helpers (`.vscode/tasks.json`)

If a task needs to run continuously or in response to events, it belongs in automation — hand off to **Executive Automator** rather than **Executive Scripter**.

---

## The Canonical Example: Scratchpad Auto-Annotator

The scratchpad watcher (`scripts/watch_scratchpad.py`) is the canonical demonstration of programmatic-first:

1. **The repeated task**: annotating H2 headings with line-range numbers after every write to a session file
2. **The interactive approach**: after every write, an agent ran `--annotate` manually
3. **The programmatic solution**: a file watcher that runs the annotator automatically whenever a `.tmp/*.md` file changes

Result:
- Agents do not need to remember to run the annotator
- The annotations are always current
- Zero agent tokens spent on annotation after the initial encoding

```bash
# Start the watcher (runs in background)
uv run python scripts/watch_scratchpad.py

# Or as a VS Code task that auto-starts with the workspace
# See .vscode/tasks.json — "Watch Scratchpad"
```

---

## What Agents Must Do

### Before Acting

```bash
# Check what scripts already exist
ls scripts/

# Read the catalog
cat scripts/README.md
```

Never re-implement something that already exists as a script.

### After Identifying a Repeated Task

1. Check `scripts/README.md` for an existing script that partially covers the need
2. If one exists: extend it, don't create a new one
3. If none exists: check for external tools that solve the problem; adopt them if appropriate
4. Write the script following the [script conventions](#script-conventions)
5. Update `scripts/README.md`
6. Commit: `chore(scripts): add <name> script`

### Script Conventions

Every script must:

- Open with a **module docstring** (purpose, inputs, outputs, usage, exit codes)
- Support **`--dry-run`** for any operation that writes or deletes files
- Be invoked via **`uv run python scripts/<name>.py`**
- Be **committed** to the repo as a first-class artifact
- Be **listed in `scripts/README.md`**

---

## Escalation Paths

| Need | Agent to invoke |
|------|----------------|
| One-shot or on-demand script | **Executive Scripter** |
| File watcher, hook, or CI job | **Executive Automator** |
| Unclear which category | Start with **Executive Scripter**; it will escalate |
