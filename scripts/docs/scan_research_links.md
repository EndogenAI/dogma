# `scan\_research\_links`

scan_research_links.py — Scan research docs and source cache for external URLs.

Purpose
-------
Programmatically scan three source tiers to discover external URLs and internal
cross-references relevant to ongoing research:

  1. docs/research/*.md             — committed research synthesis documents
  2. docs/research/sources/*.md     — committed source stub files
  3. .cache/sources/*.md            — locally cached fetched content (gitignored)

Deduplicates across all three tiers, filters out internal GitHub URLs and common
noise, and outputs a structured JSON report. The output can feed directly into
`scaffold_manifest.py` and `add_source_to_manifest.py` to populate sprint manifests.

Inputs
------
--scope     Which tiers to scan: all (default) | research_docs | sources | cache
--output    Where to write the JSON report. Default: stdout
            (use --output <path> to write to a file)
--filter    Optional regex to keep only URLs matching this pattern
--min-depth Minimum URL path depth to include (default: 1, removes bare domains)

Outputs
-------
JSON report to stdout or --output path:
{
  "scanned_files": 3,
  "total_url_occurrences": 142,
  "unique_urls": 87,
  "urls": [
    {
      "url": "https://example.com/paper",
      "sources": ["docs/research/methodology-review.md"],
      "tier": "research_docs"
    },
    ...
  ]
}

Usage Examples
--------------
# Scan all tiers, print to stdout
uv run python scripts/scan_research_links.py

# Scan only docs/research/*.md, write JSON to a file
uv run python scripts/scan_research_links.py \
  --scope research_docs \
  --output /tmp/scan-results.json

# Scan everything, filter to arxiv URLs only
uv run python scripts/scan_research_links.py --filter arxiv

# Scan cache only, minimum path depth 2
uv run python scripts/scan_research_links.py --scope cache --min-depth 2

Exit Codes
----------
0  Scan complete (even if 0 URLs found)
1  Error (I/O error, invalid arguments)

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:edb68f499ae3004f -->
