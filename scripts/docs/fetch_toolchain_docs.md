# `fetch\_toolchain\_docs`

fetch_toolchain_docs.py — Cache CLI tool help output as structured Markdown.

Purpose
-------
Run ``gh help`` and ``gh <subcommand> --help`` for every top-level subcommand,
convert the output to structured Markdown, and write it to the local
``.cache/toolchain/`` directory.  Agents can then read command syntax locally
without burning tokens or network round-trips.

Per the programmatic-first principle in AGENTS.md: agents repeatedly look up
``gh`` CLI syntax interactively (e.g. ``gh issue create``, ``gh pr merge``
flags).  That task has happened more than twice and is now encoded here.

Inputs
------
- Optional ``--tool gh``        Currently only ``gh`` is supported.  Default: ``gh``.
- Optional ``--output-dir PATH`` Where to write cache files.  Default: ``.cache/toolchain/``.
- Optional ``--check``          Skip refresh if cache files are < 24 hours old.
- Optional ``--force``          Always re-fetch, ignoring cache age.
- Optional ``--dry-run``        Print what would be written without writing anything.

Outputs
-------
- ``.cache/toolchain/gh/<subcommand>.md``  Per-subcommand structured Markdown.
- ``.cache/toolchain/gh/index.md``         All subcommands with one-line descriptions.
- ``.cache/toolchain/gh.md``               Single aggregate file (all subcommands).

Per-subcommand Markdown format::

    # gh <subcommand>
    > <description>

    ## Usage
    ## Flags  (table: Flag | Description)
    ## Examples

Usage Examples
--------------
# Fetch and cache gh CLI docs (writes to .cache/toolchain/)
uv run python scripts/fetch_toolchain_docs.py

# Explicitly specify tool and output dir
uv run python scripts/fetch_toolchain_docs.py --tool gh --output-dir .cache/toolchain/

# Skip refresh if cached within last 24 hours
uv run python scripts/fetch_toolchain_docs.py --tool all --check

# Force re-fetch even if recently cached
uv run python scripts/fetch_toolchain_docs.py --force

# Dry run — print what would be written without touching the filesystem
uv run python scripts/fetch_toolchain_docs.py --dry-run

Exit Codes
----------
0  Success (all subcommands cached or cache is fresh and --check used)
1  Error (tool not on PATH, no subcommands found, or usage error)

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:ae5b58e95a573e32 -->
