"""
prune_scratchpad.py — Scratchpad size management for .tmp/<branch>/<date>.md

Purpose:
    Manages the cross-agent scratchpad files in .tmp/<branch-slug>/.
    On each day a new session file is created: .tmp/<branch-slug>/<YYYY-MM-DD>.md
    An _index.md in the branch folder holds one-line stubs of all prior sessions.

    Prunes the active session file by compressing completed H2 sections into one-line
    archived summaries, preserving only active/live sections in full. Writes an
    '## Active Context' header at the top summarising what remains live.

    A section is considered "completed" when its heading contains any of the archive
    keywords: Results, Complete, Completed, Summary, Archived, Handoff, Done, Output.
    Sections whose heading contains "Active", "Escalation", "Session" (current), or
    "Plan" are treated as live and left intact.

    The rule of thumb: prune when the active session file exceeds 200 lines.

Path resolution (when --file is not provided):
    1. Read current git branch: git rev-parse --abbrev-ref HEAD
    2. Slugify: replace '/' with '-'
    3. Active file: .tmp/<slug>/<YYYY-MM-DD>.md
    4. If the file does not exist, create it with a minimal header and exit 0.

Inputs:
    .tmp/<branch-slug>/<YYYY-MM-DD>.md (default) or a path passed via --file.
    Falls back to .tmp.md at the workspace root if git is unavailable.

Outputs:
    Rewrites the active session file (or prints to stdout in --dry-run mode) with:
    - A leading '## Active Context' block listing all compressed sections
    - Full content of live sections
    - One-line archive stubs replacing completed sections:
        ## <Original Heading> (archived <YYYY-MM-DD> — <first-line-of-content>)

    When --force is used (session end), also appends a one-line stub to
    .tmp/<branch-slug>/_index.md summarising the archived session.

Usage:
    # Dry run — print result, do not write
    uv run python scripts/prune_scratchpad.py --dry-run

    # Prune active session file in place
    uv run python scripts/prune_scratchpad.py

    # Target a specific file (overrides auto-resolution)
    uv run python scripts/prune_scratchpad.py --file .tmp/my-branch/2026-03-04.md

    # Force prune regardless of line count (also updates _index.md)
    uv run python scripts/prune_scratchpad.py --force

    # Initialise a new session file for today (creates if absent)
    uv run python scripts/prune_scratchpad.py --init

    # Annotate H2 headings with line ranges (run after every write; idempotent)
    uv run python scripts/prune_scratchpad.py --annotate
    uv run python scripts/prune_scratchpad.py --annotate --file .tmp/my-branch/2026-03-05.md

Exit codes:
    0 — success (pruned, initialised, or no pruning needed)
    1 — file not found or parse error
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

# Headings whose content is NOT archived (kept in full)
LIVE_KEYWORDS = frozenset(["active", "escalation", "plan", "session"])

# Headings whose content IS archived (compressed to one line)
ARCHIVE_KEYWORDS = frozenset(
    ["results", "complete", "completed", "summary", "archived",
     "handoff", "done", "output", "sweep", "gaps"]
)

# If line count is below this threshold, skip pruning unless --force
SIZE_GUARD = 200


def _git_branch() -> str:
    """Return current git branch slug (/ replaced with -), or 'default' on failure."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip().replace("/", "-")
    except Exception:
        pass
    return "default"


def resolve_active_file(base: Path | None = None) -> Path:
    """
    Resolve the active session scratchpad path.

    Returns .tmp/<branch-slug>/<YYYY-MM-DD>.md relative to the workspace root.
    Falls back to .tmp.md if git is unavailable.
    """
    today = date.today().isoformat()
    root = base or Path(__file__).parent.parent
    branch = _git_branch()
    if branch == "default":
        return root / ".tmp.md"
    folder = root / ".tmp" / branch
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{today}.md"


def init_session_file(path: Path) -> None:
    """Create a new session file with a minimal header if it does not exist."""
    if path.exists():
        return
    branch = path.parent.name
    today = path.stem
    path.write_text(
        f"# Session — {branch} / {today}\n\n"
        f"_Created by prune_scratchpad.py. Append findings under `## <Task> Results` headings._\n"
    )
    print(f"Initialised new session file: {path}")


def update_index(branch_folder: Path, session_path: Path, today: str) -> None:
    """Append a one-line stub to _index.md summarising the closed session."""
    index = branch_folder / "_index.md"
    if not index.exists():
        index.write_text(f"# Session Index — {branch_folder.name}\n\n")
    stub = f"- {session_path.stem} — archived {today} (session closed by --force)\n"
    with index.open("a") as f:
        f.write(stub)
    print(f"Updated index: {index}")


def _classify(heading: str) -> str:
    """Return 'live' or 'archive' based on heading text."""
    lower = heading.lower()
    for kw in LIVE_KEYWORDS:
        if kw in lower:
            return "live"
    for kw in ARCHIVE_KEYWORDS:
        if kw in lower:
            return "archive"
    return "live"


def _first_content_line(lines: list[str]) -> str:
    """Return the first non-empty, non-heading content line."""
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped[:80] + ("…" if len(stripped) > 80 else "")
    return "(no content)"


def parse_sections(text: str) -> list[dict]:
    """
    Split the scratchpad into a list of section dicts:
        { "heading": str, "level": int, "lines": list[str] }

    The leading content before the first H2 is stored as a special
    section with heading="" and level=0.
    """
    sections: list[dict] = []
    current_heading = ""
    current_level = 0
    current_lines: list[str] = []

    for line in text.splitlines(keepends=True):
        h_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if h_match:
            level = len(h_match.group(1))
            heading = h_match.group(2).strip()
            if level == 2:
                sections.append({
                    "heading": current_heading,
                    "level": current_level,
                    "lines": current_lines,
                })
                current_heading = heading
                current_level = level
                current_lines = []
                continue
        current_lines.append(line)

    sections.append({
        "heading": current_heading,
        "level": current_level,
        "lines": current_lines,
    })
    return sections


def annotate(text: str) -> str:
    """
    Annotate each H2 heading with its buffered line range in the file.

    Example:
        ## My Section
    becomes:
        ## My Section [L12–L47]

    Line numbers are 1-based. Any previous [Ldd–Ldd] annotation is stripped
    before recalculating, so this function is idempotent.
    """
    lines = text.splitlines(keepends=True)

    # First pass: strip any existing [L\d+–L\d+] annotations from H2 lines
    stripped: list[str] = []
    for line in lines:
        cleaned = re.sub(
            r"^(## .+?) \[L\d+[–-]L?\d+\](\s*)$",
            lambda m: m.group(1) + m.group(2),
            line.rstrip("\n"),
        )
        stripped.append(cleaned + "\n" if line.endswith("\n") else cleaned)

    # Second pass: annotate each H2 with its section's line range
    result: list[str] = []
    i = 0
    while i < len(stripped):
        line = stripped[i]
        h2_match = re.match(r"^(## .+?)\s*$", line.rstrip("\n"))
        if h2_match:
            heading_text = h2_match.group(1)
            start_line = i + 1
            j = i + 1
            while j < len(stripped) and not re.match(r"^## ", stripped[j]):
                j += 1
            end_line = j
            result.append(f"{heading_text} [L{start_line}–L{end_line}]\n")
            i += 1
        else:
            result.append(line)
            i += 1

    return "".join(result)


def prune(text: str, today: str) -> tuple[str, list[str], list[str]]:
    """
    Prune the scratchpad text.

    Returns:
        (pruned_text, archived_headings, kept_headings)
    """
    sections = parse_sections(text)
    archived: list[str] = []
    kept: list[str] = []
    output_parts: list[str] = []

    for section in sections:
        heading = section["heading"]
        lines = section["lines"]

        if not heading:
            output_parts.extend(lines)
            continue

        classification = _classify(heading)

        if classification == "archive":
            summary = _first_content_line(lines)
            stub = f"## {heading} (archived {today} — {summary})\n\n"
            output_parts.append(stub)
            archived.append(heading)
        else:
            output_parts.append(f"## {heading}\n")
            output_parts.extend(lines)
            kept.append(heading)

    # Build Active Context header
    active_header_lines = [
        "## Active Context\n",
        "\n",
        "**Live sections** (full content below):\n",
    ]
    for h in kept:
        active_header_lines.append(f"- {h}\n")
    active_header_lines.append("\n")
    if archived:
        active_header_lines.append("**Archived sections** (one-line stubs inline):\n")
        for h in archived:
            active_header_lines.append(f"- {h}\n")
        active_header_lines.append("\n")
    active_header_lines.append("---\n\n")

    first_section_lines = sections[0]["lines"] if sections else []
    pre_content = "".join(first_section_lines)

    pruned = pre_content + "".join(active_header_lines) + "".join(
        p for p in output_parts[len(first_section_lines):]
    )
    return pruned, archived, kept


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scratchpad size management for .tmp/<branch>/<date>.md"
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Path to scratchpad file (default: .tmp/<branch>/<today>.md)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the pruned content without writing the file",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Prune regardless of line count (bypasses size guard)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialise today's session file and exit",
    )
    parser.add_argument(
        "--annotate",
        action="store_true",
        help=(
            "Annotate each H2 heading with its line range [Lstart–Lend] "
            "then exit. Idempotent — safe to run after every write."
        ),
    )
    args = parser.parse_args()

    today = date.today().isoformat()

    if args.init:
        path = resolve_active_file()
        init_session_file(path)
        return 0

    if args.file:
        path = Path(args.file)
    else:
        path = resolve_active_file()

    if not path.exists():
        print(f"ERROR: {path} not found.", file=sys.stderr)
        return 1

    if args.annotate:
        text = path.read_text(encoding="utf-8")
        annotated = annotate(text)
        if annotated == text:
            return 0
        if args.dry_run:
            print(annotated)
            return 0
        path.write_text(annotated, encoding="utf-8")
        print(f"Annotated headings in {path}")
        return 0

    text = path.read_text(encoding="utf-8")
    line_count = text.count("\n")

    if not args.force and line_count < SIZE_GUARD:
        print(
            f"INFO: {path} has {line_count} lines (threshold: {SIZE_GUARD}). "
            "No pruning needed. Use --force to prune anyway."
        )
        return 0

    pruned, archived, kept = prune(text, today)

    if args.dry_run:
        print(pruned)
        print(
            f"\n--- DRY RUN ---\n"
            f"Would archive {len(archived)} sections, keep {len(kept)} sections live.\n"
            f"Archived: {archived}\n"
            f"Kept live: {kept}"
        )
        return 0

    path.write_text(pruned, encoding="utf-8")
    print(
        f"Pruned {path}:\n"
        f"  Archived {len(archived)} sections: {archived}\n"
        f"  Kept live {len(kept)} sections: {kept}\n"
        f"  New line count: {pruned.count(chr(10))}"
    )
    if args.force and ".tmp" in path.parts:
        update_index(path.parent, path, today)
    return 0


if __name__ == "__main__":
    sys.exit(main())
