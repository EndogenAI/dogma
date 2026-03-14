<!-- docstring-hash: 3e7a1f92 -->
# prune_scratchpad

**Source**: `scripts/prune_scratchpad.py`

---

## Purpose

Manages the cross-agent scratchpad files in `.tmp/<branch-slug>/`.
On each day a new session file is created: `.tmp/<branch-slug>/<YYYY-MM-DD>.md`.
An `_index.md` in the branch folder holds one-line stubs of all prior sessions.

Prunes the active session file by compressing completed H2 sections into one-line
archived summaries, preserving only active/live sections in full. Writes an
`## Active Context` header at the top summarising what remains live.

A section is considered "completed" when its heading contains any of the archive
keywords: Results, Complete, Completed, Summary, Archived, Handoff, Done, Output.
Sections whose heading contains "Active", "Escalation", "Session" (current), or
"Plan" are treated as live and left intact.

The rule of thumb: prune when the active session file exceeds 2000 lines.

---

## Path Resolution

When `--file` is not provided:

1. Read current git branch: `git rev-parse --abbrev-ref HEAD`
2. Slugify: replace `/` with `-`
3. Active file: `.tmp/<slug>/<YYYY-MM-DD>.md`
4. If the file does not exist, create it with a minimal header and exit 0.

---

## Inputs

- `.tmp/<branch-slug>/<YYYY-MM-DD>.md` (default) or a path passed via `--file`
- Falls back to `.tmp.md` at the workspace root if git is unavailable

---

## Outputs

Rewrites the active session file (or prints to stdout in `--dry-run` mode) with:

- A leading `## Active Context` block listing all compressed sections
- Full content of live sections
- One-line archive stubs replacing completed sections:
  ```
  ## <Original Heading> (archived <YYYY-MM-DD> — <first-line-of-content>)
  ```

When `--force` is used (session end), also appends a one-line stub to
`.tmp/<branch-slug>/_index.md` summarising the archived session.

---

## Usage

```bash
# Dry run — print result, do not write
uv run python scripts/prune_scratchpad.py --dry-run

# Prune active session file in place
uv run python scripts/prune_scratchpad.py

# Target a specific file (overrides auto-resolution)
uv run python scripts/prune_scratchpad.py --file .tmp/my-branch/2026-03-04.md

# Force prune regardless of line count (also updates _index.md)
uv run python scripts/prune_scratchpad.py --force

# Initialise a new session file for today (creates if absent)
uv run python scripts/prune_scratchpad.py --init

# Annotate H2 headings with line ranges (run after every write; idempotent)
uv run python scripts/prune_scratchpad.py --annotate
uv run python scripts/prune_scratchpad.py --annotate --file .tmp/my-branch/2026-03-05.md

# Append a session summary block safely (no heredocs)
uv run python scripts/prune_scratchpad.py --append-summary "Session closed. Phases 1-3 complete."

# Corruption check only — exits 0 if clean, 1 if corruption found
uv run python scripts/prune_scratchpad.py --check-only
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success (pruned, initialised, annotated, summary appended, or no pruning needed) |
| `1` | File not found, parse error, or corruption detected (`--check-only`) |

---

## Tests

[`tests/test_prune_scratchpad.py`](../../tests/test_prune_scratchpad.py)

```bash
uv run pytest tests/test_prune_scratchpad.py -v
uv run pytest tests/test_prune_scratchpad.py --cov=scripts
```
