# `seed\_research\_recommendations`

scripts/seed_research_recommendations.py — Batch-create tracking issues from research doc recommendations.

Purpose
-------
Reads YAML frontmatter from one or more research Markdown docs (``docs/research/*.md``),
extracts recommendations that have no tracking issue yet (``linked_issue`` is ``null``
or starts with ``TBD``), and feeds a ``bulk_github_operations.py``-compatible JSON ops
spec into ``bulk_github_operations.py`` for batch issue creation.

This script implements the **source generator** side of the two-part batch-issue pipeline:
  1. **seed_research_recommendations.py** (this script) — reads research frontmatter → emits JSON ops spec
  2. **bulk_github_operations.py** — consumes the ops spec → calls ``gh issue create`` per op

Inputs
------
- One or more Markdown research docs (``--input FILE [FILE ...]``) with YAML frontmatter
  containing a ``recommendations`` list. Each recommendation may have:
  - ``id``: stable string identifier
  - ``title``: human-readable title (required; used as issue title)
  - ``status``: adoption status (e.g. ``accepted-for-adoption``)
  - ``linked_issue``: ``null``, ``TBD-*``, or an integer (existing issue number → skip)
  - ``area`` (optional): area label (e.g. ``docs``, ``scripts``, ``agents``, ``tests``)

Outputs
-------
- Without ``--output``: pipes the generated JSON ops spec to
  ``uv run python scripts/bulk_github_operations.py`` via stdin.
- With ``--output FILE``: writes the JSON ops spec to FILE and exits without invoking
  ``bulk_github_operations.py``. Caller can then inspect and invoke the engine separately.

Flags
-----
--input FILE [FILE ...]     One or more research Markdown docs to scan (required).
--milestone TITLE_OR_NUM    Milestone title or number to assign to all created issues.
--default-area LABEL        Area label (without the ``area:`` prefix) to use when a
                            recommendation has no ``area`` field. Required if any
                            recommendation in the input docs has no ``area`` field.
--critical-ids ID1,ID2,...  Comma-separated recommendation IDs that get
                            ``priority:critical`` instead of ``priority:high``.
--output FILE               Write the JSON ops spec to FILE instead of piping to
                            ``bulk_github_operations.py``.
--dry-run                   Generate the spec and pass ``--dry-run`` through to
                            ``bulk_github_operations.py`` (no issues created).
--repo OWNER/REPO           Target repository. Default: ``EndogenAI/dogma``.

Exit codes
----------
0  All operations succeeded (or --dry-run completed, or --output written).
1  Subprocess or I/O error during execution.
2  Parse/validation failure (malformed frontmatter, missing --default-area, etc.).

Usage examples
--------------
# Dry-run: preview which issues would be created (no API calls)
uv run python scripts/seed_research_recommendations.py \
    --input docs/research/my-research.md --dry-run

# Create tracking issues for all untracked recommendations in a doc
uv run python scripts/seed_research_recommendations.py \
    --input docs/research/my-research.md \
    --milestone "Sprint 20" \
    --default-area docs

# Scan multiple docs, mark two recommendations as critical priority
uv run python scripts/seed_research_recommendations.py \
    --input docs/research/doc-a.md docs/research/doc-b.md \
    --critical-ids intent-bound-readiness-contract,capability-matrix-requirement \
    --default-area scripts

# Write spec to file — inspect before executing
uv run python scripts/seed_research_recommendations.py \
    --input docs/research/my-research.md \
    --output /tmp/ops.json --dry-run
uv run python scripts/bulk_github_operations.py --input /tmp/ops.json --dry-run

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:c682e66b031871db -->
