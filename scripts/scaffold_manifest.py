"""
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
uv run python scripts/scaffold_manifest.py \\
  --name my-sprint \\
  --description "Deep dive on topic X" \\
  --sprints '{"A": "Primary sources", "B": "Secondary sources"}'

# Scaffold to a custom path
uv run python scripts/scaffold_manifest.py --name test --output /tmp/test-manifest.json

Exit Codes
----------
0  Manifest created successfully
1  Error (manifest already exists, invalid arguments, I/O error)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFESTS_DIR = REPO_ROOT / "docs" / "research" / "manifests"

DEFAULT_SPRINTS = {
    "A": "H1 — Novelty verification and scientific grounding",
    "B": "H2 — Biological metaphors as precise mappings",
    "C": "H3 — Augmentive partnership lineage",
    "D": "H4 — Encode-before-act lineage",
    "E": "Cross-cutting: Pattern Catalog Adopt/Gap items",
}


def scaffold(
    name: str,
    description: str,
    sprints: dict[str, str],
    output_path: Path,
) -> None:
    """Write a blank manifest JSON to output_path. Raises if file already exists."""
    if output_path.exists():
        print(f"[scaffold_manifest] Error: {output_path} already exists.", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "name": name,
        "description": description,
        "created": str(date.today()),
        "sprints": sprints,
        "sources": [],
    }

    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[scaffold_manifest] Created: {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scaffold_manifest.py",
        description="Create a new blank research source manifest JSON file.",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Slug name for the manifest (e.g. 'methodology-deep-dive').",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Human-readable description of this research sprint's scope.",
    )
    parser.add_argument(
        "--sprints",
        default=None,
        help=(
            "JSON mapping sprint keys to descriptions. "
            "Defaults to A–E with hypothesis labels. "
            'Example: \'{"A": "H1 novelty", "B": "H2 bio"}\''
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        help=("Override output path. Defaults to docs/research/manifests/<name>.json"),
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Resolve sprints
    sprints = DEFAULT_SPRINTS
    if args.sprints is not None:
        try:
            sprints = json.loads(args.sprints)
        except json.JSONDecodeError as exc:
            print(f"[scaffold_manifest] Error: --sprints is not valid JSON: {exc}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(sprints, dict):
            print("[scaffold_manifest] Error: --sprints must be a JSON object.", file=sys.stderr)
            sys.exit(1)

    # Resolve output path
    if args.output is not None:
        output_path = Path(args.output)
    else:
        output_path = DEFAULT_MANIFESTS_DIR / f"{args.name}.json"

    scaffold(
        name=args.name,
        description=args.description,
        sprints=sprints,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()
