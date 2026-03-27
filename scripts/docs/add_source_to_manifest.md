# `add\_source\_to\_manifest`

add_source_to_manifest.py — Append a source entry to a research manifest.

Purpose
-------
Programmatically add a source URL and metadata to an existing research manifest
JSON file. Duplicate URLs are rejected. The source entry includes URL, title,
sprint assignment, priority, reason, and fetch status.

Feed the manifest to `fetch_all_sources.py --manifest <path>` to batch-fetch
all pending sources, and `format_citations.py` to render ACM-style citations.

Inputs
------
--manifest  Required. Path to the target manifest JSON file
--url       Required. The source URL to add
--title     Required. Human-readable title for this source
--sprint    Required. Sprint key this source belongs to (e.g. A, B, C, D, E)
--priority  Priority level: high, medium, low (default: medium)
--reason    Optional. Brief note on why this source is relevant
--dry-run   Show what would be added without writing to the manifest

Outputs
-------
- Updated manifest JSON with the new source appended
- Summary to stdout: source slug and sprint assignment

Usage Examples
--------------
# Add a high-priority source to Sprint A
uv run python scripts/add_source_to_manifest.py \
  --manifest docs/research/manifests/methodology-deep-dive.json \
  --url "https://arxiv.org/abs/2303.12345" \
  --title "Augmenting Human Cognition with LLMs" \
  --sprint A \
  --priority high \
  --reason "Primary source for H1 novelty claim"

# Dry run — preview without writing
uv run python scripts/add_source_to_manifest.py \
  --manifest docs/research/manifests/methodology-deep-dive.json \
  --url "https://example.com/paper" \
  --title "Example Paper" \
  --sprint B \
  --dry-run

Exit Codes
----------
0  Source added successfully (or dry-run completed)
1  Error (manifest not found, duplicate URL, invalid arguments, I/O error)

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:40867d6895e58b6b -->
