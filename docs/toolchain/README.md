# docs/toolchain/ — Curated Toolchain Reference Substrate

This directory contains **agent-readable, curated references** for heavily-used CLI tools in this repository.

---

## Purpose

Every session an agent spends re-deriving `gh` command syntax or re-encountering a known failure mode is wasted token burn. This substrate encodes that knowledge once, locally, so agents can look it up rather than reconstruct it.

Goals:
- **Reduce context burn**: agents read a dense local reference instead of querying memory or docs
- **Encode failure modes**: known footguns (silent API failures, `--body` corruption, Projects v2 auth) are captured once and reused
- **Endogenous-first posture**: local knowledge beats re-fetched external knowledge every time

---

## Tools Covered

| Tool | Reference | Scope |
|------|-----------|-------|
| `gh` | [`docs/toolchain/gh.md`](gh.md) | Issues, PRs, labels, milestones, Projects v2, REST/GraphQL API |
| `uv` | [`docs/toolchain/uv.md`](uv.md) | Run, sync, add, lock, pip, python, cache |
| `ruff` | [`docs/toolchain/ruff.md`](ruff.md) | Check (lint), format, rule lookup, CI patterns |
| `git` | [`docs/toolchain/git.md`](git.md) | Status, branch, commit, push, undo, Conventional Commits |
| `pytest` | [`docs/toolchain/pytest.md`](pytest.md) | Running tests, markers, coverage, test patterns |

---

## Agent Workflow

**Before constructing a command for any tool listed above, check that tool's reference file.**

1. Identify the tool you need to invoke (e.g. `gh`).
2. Open `docs/toolchain/<tool>.md`.
3. Find the relevant section (Issues, PRs, Labels, etc.).
4. Use the canonical safe pattern for this repo — do not reconstruct syntax from memory.
5. Check **Known Failure Modes** for that section before running.

---

## Two-Layer Architecture

| Layer | Location | Status | Purpose |
|-------|----------|--------|---------|
| Auto-generated raw reference | `.cache/toolchain/<tool>/` | Gitignored | Full flag inventory from `scripts/fetch_toolchain_docs.py` |
| Curated agent reference | `docs/toolchain/<tool>.md` | **Tracked** | Repo-specific patterns + failure modes; this is the layer agents use |

The `.cache/toolchain/` layer is regenerable and disposable. The `docs/toolchain/` layer is hand-curated and committed.

**Do not overwrite `docs/toolchain/` files with script output** — `scripts/fetch_toolchain_docs.py` writes to `.cache/`, not here.

---

## Update Workflow

### When you encounter a new failure mode

1. Add it to the **Known Failure Modes** subsection in `docs/toolchain/<tool>.md`.
2. If there is a corresponding section in `docs/guides/<tool>-workflow.md`, add it there too.
3. Commit both together: `docs: add <tool> failure mode — <brief description>`.

### When a new tool warrants a reference file

1. Run `uv run python scripts/fetch_toolchain_docs.py <tool>` to populate `.cache/toolchain/<tool>/`.
2. Create `docs/toolchain/<tool>.md` by hand — curated patterns and failure modes, not raw output.
3. Add the tool to the table in this README.
4. Reference `docs/toolchain/` in all three `AGENTS.md` files (Convention Propagation Rule).

### Refreshing the cache layer

```bash
# Check freshness for all tools
uv run python scripts/fetch_toolchain_docs.py --check

# Refresh specific tool caches
uv run python scripts/fetch_toolchain_docs.py --tool gh --force
uv run python scripts/fetch_toolchain_docs.py --tool uv --force
uv run python scripts/fetch_toolchain_docs.py --tool ruff --force
uv run python scripts/fetch_toolchain_docs.py --tool git --force
uv run python scripts/fetch_toolchain_docs.py --tool pytest --force
```
