"""
Scan docs/research/ for links to per-source stubs and write bidirectional
## Referenced By entries back into each stub.

PURPOSE
-------
Per-source stubs own the `## Referenced By` section. This script maintains it
automatically so agents never have to do it manually. It scans:

  - docs/research/*.md  (issue syntheses)
  - docs/research/sources/*.md  (stubs referencing each other)

For every markdown link that points to a stub (docs/research/sources/<slug>.md),
it ensures the target stub's `## Referenced By` section lists the referencing document.

INPUTS
------
  docs/research/*.md          — issue synthesis files
  docs/research/sources/*.md  — per-source stub files

OUTPUTS
-------
  docs/research/sources/<slug>.md — ## Referenced By sections updated in-place

USAGE
-----
  # Dry-run: show what would change without writing
  uv run python scripts/link_source_stubs.py --dry-run

  # Apply changes
  uv run python scripts/link_source_stubs.py

  # Verbose output
  uv run python scripts/link_source_stubs.py --verbose
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
SOURCES_DIR = REPO_ROOT / "docs" / "research" / "sources"
RESEARCH_DIR = REPO_ROOT / "docs" / "research"

# Heading that separates the referenced-by section
REFERENCED_BY_HEADING = "## Referenced By"
# Sentinel comment that marks auto-managed content — preserved on every write
SENTINEL = "<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def find_stub_links(content: str, from_path: Path) -> list[Path]:
    """Return absolute Paths to stubs linked from content at from_path."""
    stubs: list[Path] = []
    # Match both forms: [text](sources/slug.md) and [text](./sources/slug.md)
    # Also match relative paths like ../sources/slug.md from within sources/
    for raw in re.findall(r"\[(?:[^\]]*)\]\(([^)]+\.md)\)", content):
        # Strip anchors
        raw_path = raw.split("#")[0].strip()
        try:
            target = (from_path.parent / raw_path).resolve()
        except Exception:
            continue
        if target.is_relative_to(SOURCES_DIR) and target.suffix == ".md" and target.name != "README.md":
            stubs.append(target)
    return stubs


def relative_link(stub_path: Path, referencing_path: Path) -> str:
    """Return a relative markdown link from stub_path back to referencing_path."""
    rel = referencing_path.relative_to(SOURCES_DIR.parent)
    # Relative from sources/ to the referencing doc
    back = Path("..") / rel
    title = referencing_path.stem.replace("-", " ").title()
    return f"- [{title}]({back})"


def read_referenced_by(stub_content: str) -> tuple[str, list[str], str]:
    """
    Split stub content into three parts: before_section, existing_links, after_section.
    Returns (before, links_list, after).
    'before' includes everything up to and including the ## Referenced By heading line.
    'after' is everything from the next ## heading onward (or empty).
    """
    lines = stub_content.splitlines(keepends=True)
    heading_idx: int | None = None
    next_heading_idx: int | None = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == REFERENCED_BY_HEADING and heading_idx is None:
            heading_idx = i
        elif heading_idx is not None and stripped.startswith("## ") and i > heading_idx:
            next_heading_idx = i
            break

    if heading_idx is None:
        # No ## Referenced By section — entire file is 'before', nothing after
        return stub_content, [], ""

    before = "".join(lines[: heading_idx + 1])
    section_lines = lines[heading_idx + 1 : next_heading_idx]
    after = "".join(lines[next_heading_idx:]) if next_heading_idx else ""

    # Extract existing link lines (strip sentinel comment and blank lines)
    links: list[str] = []
    for line in section_lines:
        stripped = line.strip()
        if stripped.startswith("- [") or stripped.startswith("-["):
            links.append(stripped)

    return before, links, after


def write_referenced_by(stub_path: Path, links: list[str], dry_run: bool, verbose: bool) -> bool:
    """
    Rewrite ## Referenced By section in stub_path with the given links.
    Returns True if the file was (or would be) changed.
    """
    content = stub_path.read_text(encoding="utf-8")
    before, existing, after = read_referenced_by(content)

    # Deduplicate and sort
    merged = sorted(set(existing) | set(links))

    new_section = "\n" + SENTINEL + "\n" + ("\n".join(merged) + "\n" if merged else "")

    # Reconstruct — ensure single blank line between before and section
    new_content = before.rstrip("\n") + "\n" + new_section
    if after:
        new_content += "\n" + after

    if new_content == content:
        return False

    if verbose:
        print(f"  {'[dry-run] ' if dry_run else ''}updating {stub_path.relative_to(REPO_ROOT)}")
        for link in sorted(set(links) - set(existing)):
            print(f"    + {link}")

    if not dry_run:
        stub_path.write_text(new_content, encoding="utf-8")

    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def collect_references() -> dict[Path, list[str]]:
    """
    Return a mapping of stub_path -> [relative link strings] for all
    links found in issue syntheses and in other stubs.
    """
    refs: dict[Path, list[str]] = {}

    # Scan issue syntheses: docs/research/*.md (exclude OPEN_RESEARCH.md and README.md)
    issue_syntheses = [p for p in RESEARCH_DIR.glob("*.md") if p.name not in ("OPEN_RESEARCH.md", "README.md")]

    # Also scan stubs for cross-references between each other
    all_stubs = [p for p in SOURCES_DIR.glob("*.md") if p.name != "README.md"]

    doc_sources = issue_syntheses + all_stubs

    for doc_path in doc_sources:
        if not doc_path.exists():
            continue
        content = doc_path.read_text(encoding="utf-8")
        linked_stubs = find_stub_links(content, doc_path)
        for stub_path in linked_stubs:
            if not stub_path.exists():
                continue
            link_str = relative_link(stub_path, doc_path)
            refs.setdefault(stub_path, [])
            if link_str not in refs[stub_path]:
                refs[stub_path].append(link_str)

    return refs


def main() -> int:
    parser = argparse.ArgumentParser(description="Populate ## Referenced By sections in per-source stubs.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print each file processed.",
    )
    args = parser.parse_args()

    if not SOURCES_DIR.exists():
        print(f"ERROR: {SOURCES_DIR} does not exist.", file=sys.stderr)
        return 1

    refs = collect_references()

    if not refs:
        print("No stub links found in docs/research/. Nothing to update.")
        return 0

    changed = 0
    for stub_path, links in sorted(refs.items()):
        did_change = write_referenced_by(stub_path, links, dry_run=args.dry_run, verbose=args.verbose or args.dry_run)
        if did_change:
            changed += 1

    verb = "Would update" if args.dry_run else "Updated"
    print(f"{verb} {changed} stub(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
