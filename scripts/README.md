# scripts/

Reusable endogenous scripts for the EndogenAI Workflows repo. All scripts are first-class repo
artifacts: committed, documented, and runnable. Per `AGENTS.md` conventions, every script opens
with a docstring describing its purpose, inputs, outputs, and usage examples.

---

## Directory Layout

```
scripts/
  prune_scratchpad.py   # Cross-agent scratchpad session file manager (--init, --annotate, --force)
  watch_scratchpad.py   # File watcher — auto-annotates .tmp/*.md on change (uses watchdog)
```

---

## scripts/prune_scratchpad.py

**Purpose**: Manage cross-agent scratchpad session files in `.tmp/<branch>/<date>.md`.
Initialises today's session file, annotates H2 headings with line ranges, and prunes
completed sections to one-line archive stubs when needed.

**Usage**:

```bash
# Initialise today's session file (creates .tmp/<branch>/<date>.md if absent)
uv run python scripts/prune_scratchpad.py --init

# Annotate H2 headings with line ranges [Lstart–Lend] (idempotent; run after writes)
uv run python scripts/prune_scratchpad.py --annotate
uv run python scripts/prune_scratchpad.py --annotate --file .tmp/my-branch/2026-03-05.md

# Dry-run prune — print result without writing
uv run python scripts/prune_scratchpad.py --dry-run

# Prune completed sections (only when file exceeds 200 lines, or use --force)
uv run python scripts/prune_scratchpad.py --force
```

**When to run**: at session start (`--init`), after agent writes to check line count, and at
session end (`--force`) to archive the session and update `_index.md`.

---

## scripts/watch_scratchpad.py

**Purpose**: File watcher (uses Python `watchdog`) that auto-annotates `.tmp/*.md` session
files on every change. Keeps H2 heading line-range annotations current without any manual
agent step. Includes a cooldown guard to prevent the annotator's own writes from re-triggering
a loop.

**Usage**:

```bash
# Start the watcher (Ctrl-C to stop)
uv run python scripts/watch_scratchpad.py

# Watch a custom directory
uv run python scripts/watch_scratchpad.py --tmp-dir .tmp
```

**Requirement**: `watchdog >= 4.0`. Install with:

```bash
uv add --group dev watchdog
uv sync
```

**VS Code task**: add a background task to `.vscode/tasks.json` to auto-start this watcher
when the workspace opens. Example:

```json
{
  "label": "Watch Scratchpad",
  "type": "shell",
  "command": "uv run python scripts/watch_scratchpad.py",
  "isBackground": true,
  "runOptions": { "runOn": "folderOpen" },
  "presentation": { "reveal": "silent", "panel": "dedicated" }
}
```

---

## Script Conventions

All scripts in this repo must follow these conventions (enforced by `Executive Scripter`):

1. **Module docstring** — purpose, inputs, outputs, usage examples, exit codes
2. **`--dry-run` flag** — any script that writes or deletes files must support it
3. **`uv run` invocation** — always invoke via `uv run python scripts/<name>.py`
4. **Committed** — scripts are first-class artifacts, committed with `chore(scripts): ...`
5. **Listed here** — every script must appear in this catalog

When adopting an external tool, document it here with usage notes and the rationale for adoption.

---

## References

- [`AGENTS.md` — Programmatic-First Principle](../AGENTS.md#programmatic-first-principle) — when and how to write scripts
- [`docs/guides/programmatic-first.md`](../docs/guides/programmatic-first.md) — extended guide
- [`docs/guides/session-management.md`](../docs/guides/session-management.md) — scratchpad and session protocols
