# `fetch\_all\_sources`

fetch_all_sources.py — Batch-fetch and cache all research sources referenced in this repo.

Purpose
-------
Scan all known source lists in the repo — OPEN_RESEARCH.md "Resources to Survey" sections,
docs/research/*.md YAML frontmatter `sources:` lists, and optional sprint manifest JSON files
— extract every URL, and fetch any that are not already cached in .cache/sources/ using
fetch_source.py.

Run this at the start of any research session so scouts can use read_file on cached .md paths
instead of re-fetching sources through the context window. Fetch once, read many times.

Per the programmatic-first principle in AGENTS.md: fetching the same URL interactively more
than twice is waste. This script pre-computes the cache so agents start from a fully populated
local store.

Inputs
------
- docs/research/OPEN_RESEARCH.md  — "Resources to Survey" bullet URLs (https:// lines)
- docs/research/*.md frontmatter  — `sources:` YAML list entries
- docs/research/manifests/*.json  — sprint manifest files (via --manifest)
- .cache/sources/manifest.json    — existing cache; URLs already cached are skipped

Outputs
-------
- Fetched .md files in .cache/sources/<slug>.md (via fetch_source.py)
- Updated .cache/sources/manifest.json
- Summary report to stdout: N already cached, N fetched, N failed

Usage Examples
--------------
# Dry run — show all URLs that would be fetched without fetching
uv run python scripts/fetch_all_sources.py --dry-run

# Fetch everything not yet cached
uv run python scripts/fetch_all_sources.py

# Force re-fetch even if already cached
uv run python scripts/fetch_all_sources.py --force

# Only scan OPEN_RESEARCH.md (skip docs/research/*.md frontmatter)
uv run python scripts/fetch_all_sources.py --open-research-only

# Only scan docs/research/*.md frontmatter (skip OPEN_RESEARCH.md)
uv run python scripts/fetch_all_sources.py --research-docs-only

# Fetch all sources in a sprint manifest JSON file
uv run python scripts/fetch_all_sources.py --manifest docs/research/manifests/methodology-deep-dive.json

# Dry run for a specific manifest
uv run python scripts/fetch_all_sources.py --manifest docs/research/manifests/methodology-deep-dive.json --dry-run

# Show what is currently cached
uv run python scripts/fetch_source.py --list

Exit Codes
----------
0  All fetches succeeded (or nothing to fetch)
1  One or more fetches failed (partial success still exits 1)

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:6afe7b8faee3d1f7 -->
