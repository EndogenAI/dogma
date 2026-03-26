# `scaffold\_manifest`

scaffold_manifest.py — Create a new blank research source manifest.

Purpose
-------
Scaffold a new JSON manifest file for a research sprint. The manifest tracks
source URLs, their sprint assignment, priority, fetch status, and citation
metadata. It feeds into `fetch_all_sources.py --manifest`, `add_source_to_manifest.py`,
and `format_citations.py`.

Manifests are committed to `docs/research/manifests/` so they are version-controlled
alongside the research documents they support.

Inputs
------
--name      Required. Slug name for the manifest (e.g. "methodology-deep-dive")
--description  Human-readable description of this research sprint's scope
--sprints    Optional JSON mapping sprint keys to descriptions. Defaults to A–E
             e.g. '{"A": "H1 novelty", "B": "H2 bio-metaphors"}'
--output    Optional. Override output path. Defaults to
            docs/research/manifests/<name>.json

Outputs
-------
- docs/research/manifests/<name>.json — blank manifest with metadata and empty
  sources list

Usage Examples
--------------
# Scaffold with default A–E sprints
uv run python scripts/scaffold_manifest.py --name methodology-deep-dive

# Scaffold with custom description and sprints
uv run python scripts/scaffold_manifest.py \
  --name my-sprint \
  --description "Deep dive on topic X" \
  --sprints '{"A": "Primary sources", "B": "Secondary sources"}'

# Scaffold to a custom path
uv run python scripts/scaffold_manifest.py --name test --output /tmp/test-manifest.json

Exit Codes
----------
0  Manifest created successfully
1  Error (manifest already exists, invalid arguments, I/O error)

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:a52003fa1cf3456f -->
