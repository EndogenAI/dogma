# `weave\_links`

weave_links.py
--------------
Purpose:
    Programmatically injects Markdown cross-reference links across the
    EndogenAI/dogma documentation corpus. Reads a YAML concept registry
    (data/link_registry.yml) and wraps every unlinked occurrence of a registered
    concept name with [concept](canonical_source).

    Enacts the Documentation-First principle from AGENTS.md: every change to a
    workflow, agent, or script must be accompanied by clear, navigable
    documentation — and the documentation itself warrants tooling investment.

Inputs:
    --scope       File or directory path to process (default: docs/)
    --dry-run     Preview injections without writing files
    --scope-filter  Optional: limit rewriting to specific section heading names
                  (e.g., --scope-filter "references" processes only ## References sections)
    --registry    Path to link registry YAML (default: data/link_registry.yml)

Outputs:
    Prints "N injections in M files" to stdout.
    With --dry-run: also prints diff lines showing what would change.

Idempotency guarantee:
    Running weave_links.py twice on the same corpus produces no diff on the
    second run. Files already processed are marked with <!-- WOVEN_LINK_COMPLETE -->
    and skipped on subsequent runs. The is_already_linked() guard checks for an
    existing Markdown link before each injection.

Exit codes:
    0: success (files woven or skipped)
    1: registry not found or schema error

Usage examples:
    uv run python scripts/weave_links.py --dry-run
    uv run python scripts/weave_links.py --scope docs/guides/
    uv run python scripts/weave_links.py --scope docs/guides/testing.md --dry-run
    uv run python scripts/weave_links.py --scope-filter "references"
    uv run python scripts/weave_links.py --registry data/link_registry.yml

## Usage

```bash
    uv run python scripts/weave_links.py --dry-run
    uv run python scripts/weave_links.py --scope docs/guides/
    uv run python scripts/weave_links.py --scope docs/guides/testing.md --dry-run
    uv run python scripts/weave_links.py --scope-filter "references"
    uv run python scripts/weave_links.py --registry data/link_registry.yml
```

<!-- hash:c8833924c56fb8bc -->
