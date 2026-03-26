# `generate\_sweep\_table`

Generate and maintain the corpus sweep table for back-propagation planning.

Reads docs/plans/corpus-sweep-data.yml (manual fields) and auto-detects:
  - Recency tier: from YAML frontmatter `date` field in each research doc
  - Already cited: by scanning primary papers for links/references to each doc

Usage:
  uv run python scripts/generate_sweep_table.py
      -> writes docs/plans/2026-03-12-corpus-sweep-table.md

  uv run python scripts/generate_sweep_table.py --output PATH
      -> writes to specified path

  uv run python scripts/generate_sweep_table.py --mark-read DOCNAME
      -> update status to ✅ in corpus-sweep-data.yml, then regenerate table

  uv run python scripts/generate_sweep_table.py --mark-in-progress DOCNAME
      -> update status to ⏳ in corpus-sweep-data.yml, then regenerate table

  uv run python scripts/generate_sweep_table.py --dry-run
      -> print table to stdout without writing files

Inputs:
  docs/plans/corpus-sweep-data.yml — manual fields data
  docs/research/*.md — source research docs (for recency detection)
  docs/research/values-encoding.md — primary paper (for citation scan)
  docs/research/bubble-clusters-substrate.md — primary paper
  docs/research/endogenic-design-paper.md — primary paper

Outputs:
  docs/plans/2026-03-12-corpus-sweep-table.md (or --output path)

Exit codes:
  0 — success
  1 — doc not found in YAML (--mark-read / --mark-in-progress), or primary paper missing

## Usage

```bash
  uv run python scripts/generate_sweep_table.py
      -> writes docs/plans/2026-03-12-corpus-sweep-table.md

  uv run python scripts/generate_sweep_table.py --output PATH
      -> writes to specified path

  uv run python scripts/generate_sweep_table.py --mark-read DOCNAME
      -> update status to ✅ in corpus-sweep-data.yml, then regenerate table

  uv run python scripts/generate_sweep_table.py --mark-in-progress DOCNAME
      -> update status to ⏳ in corpus-sweep-data.yml, then regenerate table

  uv run python scripts/generate_sweep_table.py --dry-run
      -> print table to stdout without writing files
```

<!-- hash:25f73809f428a6fb -->
