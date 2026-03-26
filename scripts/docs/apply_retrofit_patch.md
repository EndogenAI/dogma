# `apply\_retrofit\_patch`

Apply recommendation retrofit patches to research docs.

Purpose:
    Read YAML patch files from data/retrofit-patches/ and replace each target
    research document's ``recommendations:`` frontmatter list with the patch's
    authoritative recommendation list after removing patch-only metadata.

Inputs:
    .cache/retrofit-patches/*.yml   Patch files with an authoritative ``doc`` field.
    docs/research/*.md            Research documents with YAML frontmatter.

Outputs:
    Updated research documents with refreshed ``recommendations:`` frontmatter,
    or a dry-run preview of the files that would be rewritten.

Usage:
    uv run python scripts/apply_retrofit_patch.py
    uv run python scripts/apply_retrofit_patch.py --dry-run
    uv run python scripts/apply_retrofit_patch.py --patch-dir .cache/retrofit-patches

Exit codes:
    0   All eligible patches applied successfully, or dry-run completed without errors.
    1   One or more patches could not be applied because a patch file or target
        document was invalid.
    2   Invalid CLI usage (handled by argparse).

## Usage

```bash
    uv run python scripts/apply_retrofit_patch.py
    uv run python scripts/apply_retrofit_patch.py --dry-run
    uv run python scripts/apply_retrofit_patch.py --patch-dir .cache/retrofit-patches
```

<!-- hash:aa1fb7abcae4b4d4 -->
