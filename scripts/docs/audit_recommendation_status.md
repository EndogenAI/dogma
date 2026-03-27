# `audit\_recommendation\_status`

scripts/audit_recommendation_status.py

Audits the recommendation status across all finalized synthesis documents in
docs/research/, cross-references them against GitHub issues with the
``source:research`` label, and writes suggested frontmatter patch files to
data/retrofit-patches/<doc-slug>.yml.

Purpose:
    Implements Phase 4 of the Recommendation Provenance sprint (issue #409).
    Reads each finalized D4 document, extracts its ``## Recommendations``
    section (body text, not frontmatter), fuzzy-matches each item against
    GitHub issues that carry the ``source:research`` label, and suggests a
    status (completed, accepted, deferred) for each recommendation.  Outputs
    patch files to data/retrofit-patches/ for human review before Phase 6
    patch application.

Inputs:
    docs/research/*.md       — all finalized synthesis docs (status: Final)
    GitHub issues            — issues with label 'source:research' (via gh CLI)
    --dry-run                — print suggestions to stdout; do not write files
    --doc <path>             — audit a single doc instead of all docs
    --no-github              — skip GitHub API calls; mark all recs as deferred
    --docs-dir <path>        — override docs/research directory (default: repo root)
    --patches-dir <path>     — override data/retrofit-patches directory

Outputs:
    data/retrofit-patches/<doc-slug>.yml   — one patch suggestion file per doc
    stdout: audit summary table at end of run

Exit codes:
    0   Audit completed successfully (--dry-run also exits 0).
    1   Fatal error (docs-dir not found, --doc path not found, etc.).

Usage examples:
    # Audit all finalized docs and write patch files
    uv run python scripts/audit_recommendation_status.py

    # Preview without writing files
    uv run python scripts/audit_recommendation_status.py --dry-run

    # Audit a single doc
    uv run python scripts/audit_recommendation_status.py --doc docs/research/civic-ai-governance.md

    # Offline / CI mode — skip GitHub API calls
    uv run python scripts/audit_recommendation_status.py --no-github

## Usage

```bash
    # Audit all finalized docs and write patch files
    uv run python scripts/audit_recommendation_status.py

    # Preview without writing files
    uv run python scripts/audit_recommendation_status.py --dry-run

    # Audit a single doc
    uv run python scripts/audit_recommendation_status.py --doc docs/research/civic-ai-governance.md

    # Offline / CI mode — skip GitHub API calls
    uv run python scripts/audit_recommendation_status.py --no-github
```

<!-- hash:142d6afb2b4e7921 -->
