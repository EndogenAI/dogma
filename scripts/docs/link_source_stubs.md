# `link\_source\_stubs`

Scan docs/research/ for links to per-source stubs and write bidirectional
## Referenced By entries back into each stub.

PURPOSE
-------
Per-source stubs own the `## Referenced By` section. This script maintains it
automatically so agents never have to do it manually. It scans:

  - docs/research/*.md  (issue syntheses)
  - docs/research/sources/*.md  (stubs referencing each other)

For every markdown link that points to a stub (docs/research/sources/<slug>.md),
it ensures the target stub's `## Referenced By` section lists the referencing document.

INPUTS
------
  docs/research/*.md          — issue synthesis files
  docs/research/sources/*.md  — per-source stub files

OUTPUTS
-------
  docs/research/sources/<slug>.md — ## Referenced By sections updated in-place

USAGE
-----
  # Dry-run: show what would change without writing
  uv run python scripts/link_source_stubs.py --dry-run

  # Apply changes
  uv run python scripts/link_source_stubs.py

  # Verbose output
  uv run python scripts/link_source_stubs.py --verbose

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:71e255605f6afedf -->
