"""
format_citations.py — Render ACM-style citations from a bibliography YAML file.

Purpose
-------
Read structured source metadata from `docs/research/bibliography.yaml` and render
ACM SIG Proceedings-style reference list entries as Markdown. Supports articles,
books, conference papers, technical reports, theses, and web resources.

Also supports:
- Listing all entries with their citation keys
- Looking up a single entry by key
- Generating an inline citation tag [AuthorYear] for use in documents

ACM Citation Format Examples
-----------------------------
Article:
  [1] Donald E. Knuth. 1984. Literate Programming. The Computer Journal 27, 2 (1984), 97–111.
      DOI: https://doi.org/10.1093/comjnl/27.2.97

Book:
  [2] Christopher Alexander, Sara Ishikawa, and Murray Silverstein. 1977. A Pattern Language.
      Oxford University Press, New York, NY.

Conference paper:
  [3] Nathan Ensmenger. 2010. Making Programming Masculine. In Gender Codes. IEEE, 115–141.

Web resource:
  [4] Douglas C. Engelbart. 1962. Augmenting Human Intellect: A Conceptual Framework.
      SRI Summary Report AFOSR-3223. Retrieved 2026-03-07 from
      https://www.dougengelbart.org/content/view/138

Inputs
------
bibliography.yaml  Structured YAML file with source entries (default:
                   docs/research/bibliography.yaml)

Outputs
-------
- Numbered ACM-style reference list rendered as Markdown (stdout)
- Optionally: a single entry by key (--key <id>)
- Optionally: inline citation tag only (--inline <id>)

Usage Examples
--------------
# Render full reference list
uv run python scripts/format_citations.py

# Use a custom bibliography file
uv run python scripts/format_citations.py --bibliography /path/to/bib.yaml

# Render a single entry by key
uv run python scripts/format_citations.py --key knuth1984

# Get the inline citation tag for a key
uv run python scripts/format_citations.py --inline knuth1984

# List all keys
uv run python scripts/format_citations.py --list

Exit Codes
----------
0  Success
1  Bibliography file not found or malformed; requested key not found
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import]

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BIBLIOGRAPHY = REPO_ROOT / "docs" / "research" / "bibliography.yaml"


# ---------------------------------------------------------------------------
# YAML loading with graceful fallback
# ---------------------------------------------------------------------------


def load_bibliography(path: Path) -> list[dict]:
    """Load and return bibliography entries from a YAML file."""
    if not path.exists():
        print(f"[format_citations] Error: bibliography not found: {path}", file=sys.stderr)
        sys.exit(1)

    if not _HAS_YAML:
        print(
            "[format_citations] Error: PyYAML is not installed. Run: uv add pyyaml",
            file=sys.stderr,
        )
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    try:
        entries = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        print(f"[format_citations] Error: YAML parse error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(entries, list):
        print("[format_citations] Error: bibliography must be a YAML list.", file=sys.stderr)
        sys.exit(1)

    return entries


# ---------------------------------------------------------------------------
# Author formatting
# ---------------------------------------------------------------------------


def _format_authors(authors: list[str]) -> str:
    """Format an author list per ACM style: Last F., Last F., and Last F."""
    if not authors:
        return "Unknown Author"
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    # 3+: comma-separate, "and" before last
    return ", ".join(authors[:-1]) + f", and {authors[-1]}"


# ---------------------------------------------------------------------------
# Entry formatting by type
# ---------------------------------------------------------------------------


def _doi_link(doi: str | None) -> str:
    if not doi:
        return ""
    if doi.startswith("http"):
        return doi
    return f"https://doi.org/{doi}"


def format_entry(entry: dict, number: int) -> str:
    """Render a single bibliography entry in ACM format."""
    entry_type = entry.get("type", "misc")
    authors = _format_authors(entry.get("authors", []))
    year = entry.get("year", "n.d.")
    title = entry.get("title", "Untitled")
    doi = entry.get("doi")
    url = entry.get("url", "")
    retrieved = entry.get("retrieved", "")

    if entry_type == "article":
        venue = entry.get("venue", "")
        volume = entry.get("volume")
        issue = entry.get("issue")
        pages = entry.get("pages", "")
        vol_issue = f" {volume}" if volume else ""
        if issue:
            vol_issue += f", {issue}"
        pages_str = f" ({year}), {pages}." if pages else f" ({year})."
        ref = f"[{number}] {authors}. {year}. {title}. *{venue}*{vol_issue}{pages_str}"
        if doi:
            ref += f" DOI: {_doi_link(doi)}"
        return ref

    if entry_type in ("inproceedings", "conference"):
        booktitle = entry.get("venue", "")
        publisher = entry.get("publisher", "")
        pages = entry.get("pages", "")
        pages_str = f", {pages}" if pages else ""
        ref = f"[{number}] {authors}. {year}. {title}. In *{booktitle}*{pages_str}."
        if publisher:
            ref = f"[{number}] {authors}. {year}. {title}. In *{booktitle}*. {publisher}{pages_str}."
        if doi:
            ref += f" DOI: {_doi_link(doi)}"
        return ref

    if entry_type == "book":
        publisher = entry.get("publisher", "")
        address = entry.get("address", "")
        addr_str = f", {address}" if address else ""
        ref = f"[{number}] {authors}. {year}. *{title}*. {publisher}{addr_str}."
        if doi:
            ref += f" DOI: {_doi_link(doi)}"
        return ref

    if entry_type in ("techreport", "report"):
        venue = entry.get("venue", "Technical Report")
        ref = f"[{number}] {authors}. {year}. {title}. {venue}."
        if url:
            if retrieved:
                ref += f" Retrieved {retrieved} from {url}"
            else:
                ref += f" {url}"
        return ref

    if entry_type in ("misc", "web", "online"):
        venue = entry.get("venue", "")
        venue_str = f" {venue}." if venue else ""
        ref = f"[{number}] {authors}. {year}. {title}.{venue_str}"
        if url:
            if retrieved:
                ref += f" Retrieved {retrieved} from {url}"
            else:
                ref += f" {url}"
        return ref

    # Fallback: treat as article-like
    venue = entry.get("venue", "")
    ref = f"[{number}] {authors}. {year}. {title}."
    if venue:
        ref += f" *{venue}*."
    if doi:
        ref += f" DOI: {_doi_link(doi)}"
    elif url:
        ref += f" {url}"
    return ref


def make_inline_tag(entry: dict) -> str:
    """Generate a short inline citation tag: [FirstAuthorSurnameYear]."""
    authors = entry.get("authors", [])
    year = entry.get("year", "n.d.")
    if not authors:
        return f"[Unknown{year}]"
    first = authors[0]
    # Take the last word of the first author's name as the surname
    surname = first.split()[-1]
    return f"[{surname}{year}]"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="format_citations.py",
        description="Render ACM-style citations from a bibliography YAML file.",
    )
    parser.add_argument(
        "--bibliography",
        default=str(DEFAULT_BIBLIOGRAPHY),
        help="Path to bibliography YAML file (default: docs/research/bibliography.yaml).",
    )
    parser.add_argument(
        "--key",
        default=None,
        help="Render only the entry with this id key.",
    )
    parser.add_argument(
        "--inline",
        default=None,
        help="Print the inline citation tag [AuthorYear] for a given key.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all entry keys and titles.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    entries = load_bibliography(Path(args.bibliography))

    if args.list:
        for entry in entries:
            key = entry.get("id", "(no id)")
            title = entry.get("title", "(no title)")
            year = entry.get("year", "")
            print(f"  {key:30s}  {year}  {title}")
        return

    if args.inline:
        for entry in entries:
            if entry.get("id") == args.inline:
                print(make_inline_tag(entry))
                return
        print(f"[format_citations] Error: key not found: {args.inline}", file=sys.stderr)
        sys.exit(1)

    if args.key:
        for i, entry in enumerate(entries, 1):
            if entry.get("id") == args.key:
                print(format_entry(entry, 1))
                return
        print(f"[format_citations] Error: key not found: {args.key}", file=sys.stderr)
        sys.exit(1)

    # Default: render full reference list
    print("## References\n")
    for i, entry in enumerate(entries, 1):
        print(format_entry(entry, i))
        print()


if __name__ == "__main__":
    main()
