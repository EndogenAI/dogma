"""
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
uv run python scripts/add_source_to_manifest.py \\
  --manifest docs/research/manifests/methodology-deep-dive.json \\
  --url "https://arxiv.org/abs/2303.12345" \\
  --title "Augmenting Human Cognition with LLMs" \\
  --sprint A \\
  --priority high \\
  --reason "Primary source for H1 novelty claim"

# Dry run — preview without writing
uv run python scripts/add_source_to_manifest.py \\
  --manifest docs/research/manifests/methodology-deep-dive.json \\
  --url "https://example.com/paper" \\
  --title "Example Paper" \\
  --sprint B \\
  --dry-run

Exit Codes
----------
0  Source added successfully (or dry-run completed)
1  Error (manifest not found, duplicate URL, invalid arguments, I/O error)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def make_slug(url: str) -> str:
    """Generate a short slug from a URL for display purposes."""
    slug = re.sub(r"^https?://", "", url)
    slug = re.sub(r"^www\.", "", slug)
    slug = re.sub(r"[/?.=&]", "-", slug)
    slug = re.sub(r"[^a-zA-Z0-9\-_]", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:60]


def load_manifest(path: Path) -> dict:
    """Load and validate a manifest JSON file. Exits on error."""
    if not path.exists():
        print(f"[add_source] Error: manifest not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[add_source] Error: invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(1)
    if "sources" not in data:
        print(f"[add_source] Error: manifest missing 'sources' key: {path}", file=sys.stderr)
        sys.exit(1)
    return data


def add_source(
    manifest_path: Path,
    url: str,
    title: str,
    sprint: str,
    priority: str,
    reason: str,
    dry_run: bool = False,
) -> None:
    """Add a source entry to an existing manifest. Rejects duplicates."""
    data = load_manifest(manifest_path)

    # Check for duplicate
    existing_urls = {s["url"] for s in data["sources"]}
    if url in existing_urls:
        print(f"[add_source] Error: URL already in manifest: {url}", file=sys.stderr)
        sys.exit(1)

    # Validate sprint
    valid_sprints = set(data.get("sprints", {}).keys())
    if valid_sprints and sprint not in valid_sprints:
        print(
            f"[add_source] Error: sprint '{sprint}' not in manifest sprints {sorted(valid_sprints)}",
            file=sys.stderr,
        )
        sys.exit(1)

    entry = {
        "url": url,
        "title": title,
        "sprint": sprint,
        "priority": priority,
        "reason": reason,
        "status": "pending",
    }

    slug = make_slug(url)

    if dry_run:
        print(f"[dry-run] Would add to sprint {sprint}:")
        print(f"  slug:     {slug}")
        print(f"  url:      {url}")
        print(f"  title:    {title}")
        print(f"  priority: {priority}")
        if reason:
            print(f"  reason:   {reason}")
        return

    data["sources"].append(entry)
    manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"[add_source] Added to sprint {sprint}: {slug}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="add_source_to_manifest.py",
        description="Append a source entry to an existing research manifest JSON file.",
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to the target manifest JSON file.",
    )
    parser.add_argument(
        "--url",
        required=True,
        help="The source URL to add.",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Human-readable title for this source.",
    )
    parser.add_argument(
        "--sprint",
        required=True,
        help="Sprint key this source belongs to (e.g. A, B, C, D, E).",
    )
    parser.add_argument(
        "--priority",
        choices=["high", "medium", "low"],
        default="medium",
        help="Priority level (default: medium).",
    )
    parser.add_argument(
        "--reason",
        default="",
        help="Brief note on why this source is relevant.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be added without writing to the manifest.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    add_source(
        manifest_path=Path(args.manifest),
        url=args.url,
        title=args.title,
        sprint=args.sprint,
        priority=args.priority,
        reason=args.reason,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
