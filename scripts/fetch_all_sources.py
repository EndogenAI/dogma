"""
fetch_all_sources.py — Batch-fetch and cache all research sources referenced in this repo.

Purpose
-------
Scan all known source lists in the repo — OPEN_RESEARCH.md "Resources to Survey" sections
and docs/research/*.md YAML frontmatter `sources:` lists — extract every URL, and fetch any
that are not already cached in .cache/sources/ using fetch_source.py.

Run this at the start of any research session so scouts can use read_file on cached .md paths
instead of re-fetching sources through the context window. Fetch once, read many times.

Per the programmatic-first principle in AGENTS.md: fetching the same URL interactively more
than twice is waste. This script pre-computes the cache so agents start from a fully populated
local store.

Inputs
------
- docs/research/OPEN_RESEARCH.md  — "Resources to Survey" bullet URLs (https:// lines)
- docs/research/*.md frontmatter  — `sources:` YAML list entries
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

# Show what is currently cached
uv run python scripts/fetch_source.py --list

Exit Codes
----------
0  All fetches succeeded (or nothing to fetch)
1  One or more fetches failed (partial success still exits 1)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OPEN_RESEARCH_PATH = REPO_ROOT / "docs" / "research" / "OPEN_RESEARCH.md"
RESEARCH_DOCS_DIR = REPO_ROOT / "docs" / "research"
MANIFEST_PATH = REPO_ROOT / ".cache" / "sources" / "manifest.json"
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_source.py"

# Match bare https:// URLs in markdown bullet lines, stopping at whitespace or closing paren
_URL_RE = re.compile(r"https?://[^\s)\]>\"']+")


# ---------------------------------------------------------------------------
# URL extraction
# ---------------------------------------------------------------------------


def extract_urls_from_open_research(path: Path) -> list[str]:
    """Extract https:// URLs from 'Resources to Survey' bullet lines in OPEN_RESEARCH.md."""
    if not path.exists():
        print(f"[fetch_all_sources] Warning: {path} not found", file=sys.stderr)
        return []

    text = path.read_text(encoding="utf-8")
    urls: list[str] = []
    in_resources = False

    for line in text.splitlines():
        stripped = line.strip()
        # Enter/exit "Resources to Survey" sections
        if "Resources to Survey" in stripped or "Areas to Research" in stripped:
            in_resources = True
        elif stripped.startswith("## ") or stripped.startswith("### Gate"):
            in_resources = False

        if in_resources and stripped.startswith("- [ ]"):
            found = _URL_RE.findall(stripped)
            urls.extend(found)

    return urls


def extract_urls_from_research_frontmatter(docs_dir: Path) -> list[str]:
    """Extract URLs from the `sources:` YAML list in docs/research/*.md frontmatter."""
    urls: list[str] = []
    for md_file in sorted(docs_dir.glob("*.md")):
        if md_file.name == "OPEN_RESEARCH.md":
            continue
        text = md_file.read_text(encoding="utf-8")
        # Only look inside the frontmatter block (between first two ---)
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        frontmatter = text[3:end]
        # Find the sources: list
        in_sources = False
        for line in frontmatter.splitlines():
            stripped = line.strip()
            if stripped == "sources:":
                in_sources = True
            elif in_sources and stripped.startswith("-"):
                found = _URL_RE.findall(stripped)
                urls.extend(found)
            elif in_sources and not stripped.startswith("-") and stripped:
                in_sources = False

    return urls


def load_cached_urls() -> set[str]:
    """Return the set of URLs already in the manifest."""
    if not MANIFEST_PATH.exists():
        return set()
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        return {entry["url"] for entry in manifest.get("sources", {}).values()}
    except (json.JSONDecodeError, KeyError):
        return set()


# ---------------------------------------------------------------------------
# Slug generation (mirrors fetch_source.py — kept in sync manually)
# ---------------------------------------------------------------------------


def make_slug(url: str) -> str:
    slug = re.sub(r"^https?://", "", url)
    slug = re.sub(r"^www\.", "", slug)
    slug = re.sub(r"[/?.=&]", "-", slug)
    slug = re.sub(r"[^a-zA-Z0-9\-_]", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:60]


# ---------------------------------------------------------------------------
# Batch fetch
# ---------------------------------------------------------------------------


def fetch_all(urls: list[str], dry_run: bool = False, force: bool = False) -> tuple[int, int, int]:
    """Fetch all URLs. Returns (already_cached, newly_fetched, failed)."""
    cached_urls = load_cached_urls()
    already_cached = 0
    newly_fetched = 0
    failed = 0

    for url in urls:
        if not force and url in cached_urls:
            already_cached += 1
            if dry_run:
                print(f"  [cached]  {url}")
            continue

        if dry_run:
            print(f"  [fetch]   {url}")
            continue

        slug = make_slug(url)
        result = subprocess.run(
            [sys.executable, str(FETCH_SCRIPT), url, "--slug", slug],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            newly_fetched += 1
            print(f"  ✓  {slug}")
            if result.stderr.strip():
                # Surface cache-hit notes but not errors
                for line in result.stderr.strip().splitlines():
                    if "cache hit" in line:
                        already_cached += 1
                        newly_fetched -= 1
        else:
            failed += 1
            print(f"  ✗  {url}", file=sys.stderr)
            for line in result.stderr.strip().splitlines():
                print(f"     {line}", file=sys.stderr)

    return already_cached, newly_fetched, failed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fetch_all_sources.py",
        description=(
            "Batch-fetch all research source URLs referenced in OPEN_RESEARCH.md and "
            "docs/research/*.md frontmatter into the local .cache/sources/ store."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fetched without fetching anything.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-fetch even if already cached.",
    )
    parser.add_argument(
        "--open-research-only",
        action="store_true",
        help="Only scan OPEN_RESEARCH.md (skip docs/research/*.md frontmatter).",
    )
    parser.add_argument(
        "--research-docs-only",
        action="store_true",
        help="Only scan docs/research/*.md frontmatter (skip OPEN_RESEARCH.md).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Collect URLs from configured sources
    all_urls: list[str] = []

    if not args.research_docs_only:
        open_research_urls = extract_urls_from_open_research(OPEN_RESEARCH_PATH)
        print(f"OPEN_RESEARCH.md:        {len(open_research_urls)} URLs found")
        all_urls.extend(open_research_urls)

    if not args.open_research_only:
        frontmatter_urls = extract_urls_from_research_frontmatter(RESEARCH_DOCS_DIR)
        print(f"docs/research/*.md:      {len(frontmatter_urls)} URLs found")
        all_urls.extend(frontmatter_urls)

    # Deduplicate, preserve order
    seen: set[str] = set()
    unique_urls: list[str] = []
    for url in all_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    print(f"Total unique URLs:       {len(unique_urls)}")

    if not unique_urls:
        print("Nothing to fetch.")
        return

    if args.dry_run:
        print("\n[dry-run] Would process:\n")
    else:
        print()

    cached, fetched, failed = fetch_all(unique_urls, dry_run=args.dry_run, force=args.force)

    print()
    if args.dry_run:
        print(f"=== Dry run complete: {cached} already cached, {len(unique_urls) - cached} would be fetched ===")
    else:
        print(f"=== Done: {cached} already cached, {fetched} newly fetched, {failed} failed ===")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
