# `identify\_missing\_recommendations`

Inventory D4research docs: identify missing ## Recommendations sections.

Script identifies all finalized D4 research documents in docs/research/ and
checks whether each has a ## Recommendations section in the file body. This
detects gaps where the frontmatter lists recommendations but the body lacks
the required Recommendations section heading (which should describe or expand
on those recommendations beyond the YAML list).

Outputs JSON or CSV with: (filename, status, has_body_recommendations, count)

Usage:
    uv run python scripts/identify_missing_recommendations.py [--output json|csv] [--output-file PATH]

Examples:
    # Print to stdout (JSON)
    uv run python scripts/identify_missing_recommendations.py

    # Save to CSV
    uv run python scripts/identify_missing_recommendations.py --output csv --output-file inventory.csv

    # Save to JSON
    uv run python scripts/identify_missing_recommendations.py --output json --output-file inventory.json

## Usage

```bash
    uv run python scripts/identify_missing_recommendations.py [--output json|csv] [--output-file PATH]
```

<!-- hash:7ca1f6a421b8c01f -->
