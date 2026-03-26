# `afs\_index`

scripts/afs_index.py — B' Hybrid SQLite FTS5 Keyword Index for Session Scratchpads

Purpose:
    Implements the B' hybrid scratchpad architecture: SQLite FTS5 as a
    query-optimised index over Markdown session files. Agents continue writing
    via ``replace_string_in_file``; this script maintains a queryable index for
    the two highest-frequency query patterns:

        Q1: active phase  — SELECT phase, status FROM sessions WHERE phase MATCH ?
        Q5: open blockers — SELECT content FROM sessions WHERE content MATCH 'blocker OR blocked'

    The ``.db`` file is gitignored; Markdown ``.md`` files remain the source of
    truth and continue to be committed as session records.

Design: Candidate B' (Sprint 15 scratchpad architecture research)
Reference: ``docs/research/scratchpad-architecture-decision.md``
Reference: GitHub issue #129

Inputs:
    COMMAND (positional):
        init   — create / migrate the .db file for the current branch's .tmp/ dir
        index  — (re)index all .md session files under a branch .tmp/ dir
        query  — run a keyword query against the FTS5 index
        status — show per-file index coverage stats

    --tmp-dir PATH   Base .tmp/ directory (default: .tmp/ at repo root)
    --branch  SLUG   Branch slug to use (default: auto-detect from git)
    --db-path PATH   Explicit .db path (overrides --tmp-dir/--branch derivation)
    --q TEXT         Keyword query string (required for ``query`` command)
    --field FIELD    Field to match against: phase|status|content (default: content)
    --format json|table  Output format for query results (default: table)

Outputs:
    init:   creates ``.tmp/<branch>/.scratchpad_index.db`` with FTS5 schema
    index:  populates / refreshes the FTS5 virtual table rows from .md files
    query:  prints matching rows (table or JSON)
    status: prints coverage stats (files indexed, total rows, last updated)

Exit codes:
    0 — success
    1 — argument error, DB error, or no matching files

Usage:
    uv run python scripts/afs_index.py init
    uv run python scripts/afs_index.py index
    uv run python scripts/afs_index.py query --q "Phase 3"
    uv run python scripts/afs_index.py query --q "blocker OR blocked" --field content
    uv run python scripts/afs_index.py status
    uv run python scripts/afs_index.py index --branch feat-my-branch

## Usage

```bash
    uv run python scripts/afs_index.py init
    uv run python scripts/afs_index.py index
    uv run python scripts/afs_index.py query --q "Phase 3"
    uv run python scripts/afs_index.py query --q "blocker OR blocked" --field content
    uv run python scripts/afs_index.py status
    uv run python scripts/afs_index.py index --branch feat-my-branch
```

<!-- hash:5616921964762438 -->
