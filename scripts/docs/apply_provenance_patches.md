# `apply\_provenance\_patches`

Apply approved provenance annotation patches to finalized research docs.

Purpose:
    Read YAML patch files from data/retrofit-patches/ and apply approved patches
    to their target research documents. Patches update the recommendations: frontmatter
    field. This script filters patches by status (approved-for-adoption) and tracks
    success/failure with structured JSON output.

Inputs:
    data/retrofit-patches/*.yml   Patch files with doc target and status.
    docs/research/*.md            Research documents with YAML frontmatter.

Outputs:
    Modified research docs with updated recommendations: frontmatter.
    Structured JSON report: provenance-patches-applied-<date>.json
    Exit code: 0 on full success, 1 if any patches failed.

Usage:
    uv run python scripts/apply_provenance_patches.py
    uv run python scripts/apply_provenance_patches.py --dry-run
    uv run python scripts/apply_provenance_patches.py --status-filter approved-for-adoption

Exit codes:
    0   All eligible patches applied successfully, or dry-run completed.
    1   One or more patches could not be applied.
    2   Invalid CLI usage.

## Usage

```bash
    uv run python scripts/apply_provenance_patches.py
    uv run python scripts/apply_provenance_patches.py --dry-run
    uv run python scripts/apply_provenance_patches.py --status-filter approved-for-adoption
```

<!-- hash:b6a43469cb79e185 -->
