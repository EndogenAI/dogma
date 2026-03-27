#!/usr/bin/env python3
"""
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
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TypedDict

import yaml

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)


class ResearchDocRecord(TypedDict):
    """Record for a single research doc inventory entry."""

    filename: str
    status: str
    has_body_recommendations: bool
    recommendation_count: int


def parse_frontmatter(content: str) -> dict:
    """
    Extract YAML frontmatter from markdown.

    Uses a regex anchored to the start of the document to avoid matching
    thematic break (---) lines in the body. Parses the full YAML block so
    all frontmatter keys (including 'recommendations' lists) are available.
    Returns empty dict if no valid frontmatter found.
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}
    try:
        parsed = yaml.safe_load(match.group(1))
        return parsed if isinstance(parsed, dict) else {}
    except yaml.YAMLError:
        return {}


def extract_body_content(content: str) -> str:
    """
    Extract body content (everything after frontmatter).

    Uses a regex anchored to the start to avoid matching thematic breaks.
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return content
    return content[match.end() :].strip()


def has_recommendations_section(body_content: str) -> bool:
    """
    Check if the body contains a ## Recommendations heading.

    Looks for ## Recommendations (case-insensitive, allows variations like
    ## Recommendations, ## RECOMMENDATIONS, etc.)
    """
    # Pattern: ## followed by optional whitespace, then "Recommendations"
    pattern = r"^##\s+Recommendations"
    for line in body_content.split("\n"):
        if re.match(pattern, line, re.IGNORECASE):
            return True
    return False


def count_recommendations_in_frontmatter(frontmatter: dict) -> int:
    """
    Count recommendations if 'recommendations' key exists in frontmatter.

    Assumes recommendations is a list in YAML frontmatter.
    """
    if "recommendations" in frontmatter and isinstance(frontmatter["recommendations"], list):
        return len(frontmatter["recommendations"])
    return 0


def inventory_research_docs(research_dir: Path) -> list[ResearchDocRecord]:
    """
    Scan docs/research/ and inventory all D4 docs by status and Recommendations presence.

    Returns list of ResearchDocRecord dicts.
    """
    records: list[ResearchDocRecord] = []

    # Find all .md files recursively
    md_files = sorted(research_dir.rglob("*.md"))

    for fpath in md_files:
        try:
            content = fpath.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            print(f"Warning: Could not read {fpath}: {e}", file=sys.stderr)
            continue

        frontmatter = parse_frontmatter(content)
        status = frontmatter.get("status", "Unknown")

        # Skip non-Final docs per task
        if status != "Final":
            continue

        body = extract_body_content(content)
        has_recs = has_recommendations_section(body)
        rec_count = count_recommendations_in_frontmatter(frontmatter)

        # Get relative path for display
        try:
            rel_path = fpath.relative_to(research_dir.parent)
        except ValueError:
            rel_path = fpath

        records.append(
            {
                "filename": str(rel_path),
                "status": status,
                "has_body_recommendations": has_recs,
                "recommendation_count": rec_count,
            }
        )

    return records


def write_json_output(records: list[ResearchDocRecord], output_file: Path | None):
    """Write records as JSON to stdout or file."""
    output = json.dumps(records, indent=2)
    if output_file:
        output_file.write_text(output)
    else:
        print(output)


def write_csv_output(records: list[ResearchDocRecord], output_file: Path | None):
    """Write records as CSV to stdout or file."""
    import csv
    import io

    output_io = io.StringIO()
    writer = csv.DictWriter(
        output_io,
        fieldnames=[
            "filename",
            "status",
            "has_body_recommendations",
            "recommendation_count",
        ],
    )
    writer.writeheader()
    writer.writerows(records)

    output = output_io.getvalue()
    if output_file:
        output_file.write_text(output)
    else:
        print(output)


def main():
    """Run the inventory script."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--output",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=None,
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    # Path to docs/research directory
    research_dir = Path(__file__).parent.parent / "docs" / "research"

    if not research_dir.exists():
        print(f"Error: {research_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    # Run inventory
    records = inventory_research_docs(research_dir)

    # Write output
    if args.output == "json":
        write_json_output(records, args.output_file)
    elif args.output == "csv":
        write_csv_output(records, args.output_file)

    # Print summary to stderr
    missing_recs = [r for r in records if not r["has_body_recommendations"]]
    print(
        f"\nInventory complete: {len(records)} Final docs scanned; "
        f"{len(missing_recs)} missing body Recommendations section",
        file=sys.stderr,
    )

    # Exit with code 1 if any missing to signal to CI
    if missing_recs:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
