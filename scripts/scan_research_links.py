"""
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
uv run python scripts/scan_research_links.py \\
  --scope research_docs \\
  --output /tmp/scan-results.json

# Scan everything, filter to arxiv URLs only
uv run python scripts/scan_research_links.py --filter arxiv

# Scan cache only, minimum path depth 2
uv run python scripts/scan_research_links.py --scope cache --min-depth 2

Exit Codes
----------
0  Scan complete (even if 0 URLs found)
1  Error (I/O error, invalid arguments)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_DOCS_DIR = REPO_ROOT / "docs" / "research"
SOURCES_DIR = REPO_ROOT / "docs" / "research" / "sources"
CACHE_DIR = REPO_ROOT / ".cache" / "sources"

# Broad URL regex — matches http/https links in Markdown
_URL_RE = re.compile(r"https?://[^\s)\]>\"',]+")

# Noise filters — URLs to exclude from results
_NOISE_PATTERNS = [
    r"^https?://github\.com/EndogenAI/",  # Internal repo links
    r"^https?://github\.com/EndogenAI$",
    r"^https?://doi\.org/",  # Raw DOI links (tracked in bibliography.yaml)
    r"badge\.svg",  # Badge images
    r"img\.shields\.io",  # Shield badges
    r"githubusercontent\.com",  # Raw GitHub content (not source docs)
    r"gravatar\.com",  # Profile images
]
_NOISE_RE = re.compile("|".join(_NOISE_PATTERNS))

TIER_LABELS = {
    "research_docs": "docs/research/*.md",
    "sources": "docs/research/sources/*.md",
    "cache": ".cache/sources/*.md",
}


def _extract_urls(text: str) -> list[str]:
    """Return all https URLs found in text."""
    return _URL_RE.findall(text)


def _is_noise(url: str, min_depth: int) -> bool:
    """Return True if this URL should be excluded."""
    if _NOISE_RE.search(url):
        return True
    # Check minimum path depth
    path_part = re.sub(r"^https?://[^/]+", "", url).strip("/")
    depth = len([p for p in path_part.split("/") if p]) if path_part else 0
    return depth < min_depth


def scan_dir(
    directory: Path,
    tier: str,
    min_depth: int,
    url_sources: dict[str, list[dict]],
) -> int:
    """Scan all .md files in directory and collect URLs."""
    if not directory.exists():
        return 0

    scanned = 0
    for md_file in sorted(directory.glob("*.md")):
        if md_file.name in ("README.md", "OPEN_RESEARCH.md"):
            continue
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        scanned += 1
        rel_path = str(md_file.relative_to(REPO_ROOT))

        for url in _extract_urls(text):
            if _is_noise(url, min_depth):
                continue
            url_sources[url].append({"file": rel_path, "tier": tier})

    return scanned


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scan_research_links.py",
        description="Scan research docs and source cache for external URLs.",
    )
    parser.add_argument(
        "--scope",
        choices=["all", "research_docs", "sources", "cache"],
        default="all",
        help="Which tiers to scan (default: all).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write JSON report to this path instead of stdout.",
    )
    parser.add_argument(
        "--filter",
        default=None,
        help="Only include URLs matching this regex pattern.",
    )
    parser.add_argument(
        "--min-depth",
        type=int,
        default=1,
        help="Minimum URL path depth to include (default: 1).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    filter_re = None
    if args.filter:
        try:
            filter_re = re.compile(args.filter, re.IGNORECASE)
        except re.error as exc:
            print(f"[scan_research_links] Error: invalid --filter regex: {exc}", file=sys.stderr)
            sys.exit(1)

    # url -> list of {file, tier}
    url_sources: dict[str, list[dict]] = defaultdict(list)
    total_scanned = 0

    if args.scope in ("all", "research_docs"):
        n = scan_dir(RESEARCH_DOCS_DIR, "research_docs", args.min_depth, url_sources)
        total_scanned += n

    if args.scope in ("all", "sources"):
        n = scan_dir(SOURCES_DIR, "sources", args.min_depth, url_sources)
        total_scanned += n

    if args.scope in ("all", "cache"):
        n = scan_dir(CACHE_DIR, "cache", args.min_depth, url_sources)
        total_scanned += n

    # Apply filter
    if filter_re:
        url_sources = {url: srcs for url, srcs in url_sources.items() if filter_re.search(url)}

    # Build output
    urls_list = [
        {
            "url": url,
            "tier": srcs[0]["tier"],  # primary tier (first seen)
            "sources": [s["file"] for s in srcs],
        }
        for url, srcs in sorted(url_sources.items())
    ]

    report = {
        "scanned_files": total_scanned,
        "total_url_occurrences": sum(len(v) for v in url_sources.values()),
        "unique_urls": len(urls_list),
        "urls": urls_list,
    }

    output_text = json.dumps(report, indent=2) + "\n"

    if args.output:
        try:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(output_text, encoding="utf-8")
            print(
                f"[scan_research_links] Scanned {total_scanned} files, "
                f"found {len(urls_list)} unique URLs → {args.output}"
            )
        except OSError as exc:
            print(f"[scan_research_links] Error writing output: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        sys.stdout.write(output_text)


if __name__ == "__main__":
    main()
