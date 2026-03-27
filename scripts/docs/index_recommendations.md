# `index\_recommendations`

scripts/index_recommendations.py

Scans all finalized synthesis documents in docs/research/ and writes a structured
registry of their ``recommendations:`` frontmatter entries to
``data/recommendations-registry.yml``.

Purpose:
    Provide a single, machine-readable index of every recommendation recorded in
    the synthesis corpus so that provenance can be queried programmatically — e.g.
    "which recommendations are untracked?", "which are still open?", "which issue
    closed rec-X?".  This implements the Programmatic-First principle from
    AGENTS.md: provenance data that was previously inferred interactively from
    issue threads is now encoded as structured YAML and kept in sync by CI.

Inputs:
    docs/research/*.md          — all finalized D4 synthesis documents
                                   (must have ``status: Final`` in frontmatter)
    --docs-dir <path>           — override the docs/research search root
                                   (default: <repo-root>/docs/research)

Outputs:
    data/recommendations-registry.yml  — YAML registry (written by default run)

Exit codes:
    0   Success (default / --dry-run / fresh --check)
    0   Warning printed for docs with malformed YAML frontmatter (warn-and-skip behavior)
    1   --check mode: registry is stale (or missing)

Usage examples:
    # Write the registry
    uv run python scripts/index_recommendations.py

    # Preview without writing
    uv run python scripts/index_recommendations.py --dry-run

    # CI gate: exit 1 if registry is stale
    uv run python scripts/index_recommendations.py --check

    # Override docs directory (useful for testing)
    uv run python scripts/index_recommendations.py --docs-dir /tmp/test-docs

## Usage

```bash
    # Write the registry
    uv run python scripts/index_recommendations.py

    # Preview without writing
    uv run python scripts/index_recommendations.py --dry-run

    # CI gate: exit 1 if registry is stale
    uv run python scripts/index_recommendations.py --check

    # Override docs directory (useful for testing)
    uv run python scripts/index_recommendations.py --docs-dir /tmp/test-docs
```

<!-- hash:c8471eeff320a71f -->
