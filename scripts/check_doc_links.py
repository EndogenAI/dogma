"""
check_doc_links.py — Validate that relative file links in Markdown docs resolve.

Purpose
-------
Scan Markdown files for relative file links (e.g. `[text](../path/to/file.md)`)
and verify that each linked path exists on disk relative to the source file.

This catches the common failure mode where a doc in `docs/guides/` references
`.github/agents/AGENTS.md` (wrong — resolves to `docs/guides/.github/...`)
instead of `../../.github/agents/AGENTS.md` (correct).

Only checks file:// style relative links — skips http/https URLs, anchors (#),
and mailto: links. Those are the responsibility of lychee in CI.

Inputs
------
Positional arguments: one or more Markdown file paths to check.
If none given, scans docs/**/*.md and CONTRIBUTING.md README.md CHANGELOG.md.

Outputs
-------
Prints broken links to stderr. Exits 0 if all links resolve, 1 if any are broken.

Usage
-----
# Check specific files:
uv run python scripts/check_doc_links.py docs/research/agent-taxonomy.md

# Check all docs (default):
uv run python scripts/check_doc_links.py

# Used as pre-commit hook (filenames passed by pre-commit):
python3 scripts/check_doc_links.py docs/guides/agents.md docs/research/foo.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Regex to match Markdown links: [text](target) — captures only the target part.
# Excludes http/https, mailto, anchors, and empty targets.
_LINK_RE = re.compile(r"\[(?:[^\]]*)\]\(([^)]+)\)")

# Resolve the repo root relative to this script's location.
REPO_ROOT = Path(__file__).resolve().parent.parent


def is_relative_file_link(target: str) -> bool:
    """Return True if target is a relative filesystem path (not URL/anchor)."""
    if not target:
        return False
    if target.startswith(("http://", "https://", "mailto:", "#", "file://")):
        return False
    # Paths starting with '/' are absolute or site-root-relative (e.g. /api/...).
    # These are website URL patterns from externally-fetched content — skip them.
    if target.startswith("/"):
        return False
    return True


def strip_anchor(target: str) -> str:
    """Remove a trailing #anchor from a link target."""
    if "#" in target:
        return target.split("#", 1)[0]
    return target


def check_file(path: Path) -> list[tuple[int, str, str]]:
    """
    Check all relative file links in a Markdown file.

    Returns a list of (line_number, target, resolved_path) tuples for broken links.
    Skips links inside fenced code blocks (``` or ~~~) and links whose target is
    a placeholder like '...' or '#'.
    """
    broken = []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return broken

    in_code_fence = False
    fence_marker = ""

    for lineno, line in enumerate(content.splitlines(), start=1):
        # Detect code fence open/close (``` or ~~~, with optional language tag).
        stripped = line.strip()
        if not in_code_fence:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_code_fence = True
                fence_marker = stripped[:3]
                continue
        else:
            if stripped.startswith(fence_marker):
                in_code_fence = False
            continue  # Skip all lines inside a code fence.

        for match in _LINK_RE.finditer(line):
            target = match.group(1).strip()
            if not is_relative_file_link(target):
                continue
            # Skip placeholder targets like '...' or empty after stripping anchor.
            bare = strip_anchor(target)
            if not bare or bare in ("...", ".", ""):
                continue
            resolved = (path.parent / bare).resolve()
            if not resolved.exists():
                broken.append((lineno, target, str(resolved)))

    return broken


# Directories whose Markdown files are excluded from default scanning.
# docs/research/sources/ contains externally-fetched cached content with
# site-root-relative links (e.g. /api/...) that are not our authored links.
_EXCLUDED_DIRS = {
    REPO_ROOT / "docs" / "research" / "sources",
}


def collect_default_files() -> list[Path]:
    """Return the default set of Markdown files to check.

    Mirrors the lychee CI scope: docs/**/*.md plus top-level markdown files.
    Excludes docs/research/sources/ (external cached content).
    """
    docs_dir = REPO_ROOT / "docs"
    files = [p for p in docs_dir.rglob("*.md") if not any(p.is_relative_to(excl) for excl in _EXCLUDED_DIRS)]
    for extra in ("CONTRIBUTING.md", "README.md", "CHANGELOG.md"):
        p = REPO_ROOT / extra
        if p.exists():
            files.append(p)
    return files


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if args:
        files = [Path(a).resolve() for a in args]
    else:
        files = collect_default_files()

    any_broken = False
    for path in files:
        if not path.exists():
            print(f"check_doc_links: file not found: {path}", file=sys.stderr)
            any_broken = True
            continue
        broken = check_file(path)
        for lineno, target, resolved in broken:
            rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
            print(
                f"{rel}:{lineno}: broken relative link '{target}' → {resolved}",
                file=sys.stderr,
            )
            any_broken = True

    if any_broken:
        print(
            "\ncheck_doc_links: fix broken relative paths before committing.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
