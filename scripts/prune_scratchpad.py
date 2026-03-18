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

    The rule of thumb: prune when the active session file exceeds 2000 lines.

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

    # Force prune regardless of line count (also updates _index.md) — DEPRECATED
    # Prefer --init for new sessions; let each day's file persist intact.
    uv run python scripts/prune_scratchpad.py --force

    # Initialise a new session file for today (creates if absent)
    uv run python scripts/prune_scratchpad.py --init

    # Annotate H2 headings with line ranges (run after every write; idempotent)
    uv run python scripts/prune_scratchpad.py --annotate
    uv run python scripts/prune_scratchpad.py --annotate --file .tmp/my-branch/2026-03-05.md

    # Append a session summary block safely (no heredocs)
    uv run python scripts/prune_scratchpad.py --append-summary "Session closed. Phases 1-3 complete."

    # Corruption check only — exits 0 if clean, 1 if corruption found
    uv run python scripts/prune_scratchpad.py --check-only

Exit codes:
    0 — success (pruned, initialised, annotated, summary appended, or no pruning needed)
    1 — file not found, parse error, or corruption detected (--check-only)
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import date
from pathlib import Path

# Headings whose content is NOT archived (kept in full)
LIVE_KEYWORDS = frozenset(["active", "escalation", "plan", "session"])

# Headings whose content IS archived (compressed to one line)
ARCHIVE_KEYWORDS = frozenset(
    [
        "results",
        "complete",
        "completed",
        "summary",
        "archived",
        "handoff",
        "done",
        "output",
        "sweep",
        "gaps",
    ]
)

# If line count is below this threshold, skip pruning unless --force
SIZE_GUARD = 2000


def _git_branch() -> str:
    """Return current git branch slug (/ replaced with -), or 'default' on failure."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
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


def _git_branch_raw() -> str:
    """Return current git branch name (un-slugified) from git branch --show-current.

    Returns empty string if not in a git repo or the command fails.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def init_session_file(path: Path) -> None:
    """Create a new session file with a minimal header and a Session State YAML block.

    If the file already exists, does nothing (safe to call multiple times).
    The ## Session State block is appended after the header line so that
    validate_session_state.py --yaml-state can parse it immediately.

    YAML schema (Candidate C):
        branch:        string — git branch name
        date:          string — ISO date (YYYY-MM-DD)
        active_phase:  string or null — current phase name
        active_issues: list — GitHub issue numbers actively worked
        blockers:      list — open blockers (strings)
        last_agent:    string or null — last delegated agent name
        phases:        list of {name, status, commit}
    """
    if path.exists():
        return
    branch = path.parent.name
    today = path.stem
    raw_branch = _git_branch_raw()
    try:
        import yaml  # type: ignore[import-untyped]

        branch_val = raw_branch or branch  # fall back to folder slug if detached HEAD
        yaml_block = yaml.safe_dump(
            {
                "branch": branch_val,
                "date": today,
                "active_phase": None,
                "active_issues": [],
                "blockers": [],
                "last_agent": None,
                "phases": [],
            },
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
    except Exception:
        branch_val = raw_branch or branch
        yaml_block = (
            f"branch: '{branch_val}'\n"
            f"date: '{today}'\n"
            f"active_phase: null\n"
            f"active_issues: []\n"
            f"blockers: []\n"
            f"last_agent: null\n"
            f"phases: []\n"
        )
    path.write_text(
        f"# Session — {branch} / {today}\n\n"
        f"_Created by prune_scratchpad.py. Append findings under `## <Task> Results` headings._\n\n"
        f"## Session State\n\n"
        f"```yaml\n"
        f"{yaml_block}"
        f"```\n"
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


def archive_to_sessions(
    session_path: Path,
    content: str,
    session_date: str,
    branch_slug: str,
    repo_root: Path | None = None,
) -> None:
    """Archive a pruned session file to docs/sessions/<branch>/<date>.md.

    Phase 2 of the session-archive pipeline: in addition to the .tmp/ index stub
    written by update_index(), this function commits a permanent copy of the pruned
    session to docs/sessions/ with YAML frontmatter for provenance tracking.

    The YAML frontmatter added at the top of the archived file:
        ---
        session: YYYY-MM-DD
        branch: <branch-slug>
        hash: <sha256 first 8 hex chars of content>
        ---

    Args:
        session_path: Path to the original .tmp scratchpad file (used only for
            context; the *content* arg is what gets archived).
        content: The pruned session content to archive.
        session_date: ISO date string (YYYY-MM-DD) for the session.
        branch_slug: Branch slug (/ replaced with -).
        repo_root: Workspace root Path; defaults to two directories above this script.
    """
    root = repo_root or Path(__file__).parent.parent
    dest_dir = root / "docs" / "sessions" / branch_slug
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{session_date}.md"
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
    frontmatter = f"---\nsession: {session_date}\nbranch: {branch_slug}\nhash: {content_hash}\n---\n\n"
    dest.write_text(frontmatter + content, encoding="utf-8")
    print(f"Archived session to: {dest}")


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


def detect_corruption(text: str) -> list[int]:
    """
    Scan text for lines that appear to be corrupted by concurrent write collisions.

    A line is considered corrupted if it contains a heading fragment repeated three
    or more times consecutively, e.g.:
        ### Phase 1### Phase 1### Phase 1
        ## Scout Output## Scout Output

    Returns a list of 1-based line numbers where corruption was detected.
    """
    corrupted: list[int] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if re.search(r"(#{1,3} \S{3,})\1{2,}", line):
            corrupted.append(i)
    return corrupted


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
                sections.append(
                    {
                        "heading": current_heading,
                        "level": current_level,
                        "lines": current_lines,
                    }
                )
                current_heading = heading
                current_level = level
                current_lines = []
                continue
        current_lines.append(line)

    sections.append(
        {
            "heading": current_heading,
            "level": current_level,
            "lines": current_lines,
        }
    )
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

    pruned = pre_content + "".join(active_header_lines) + "".join(p for p in output_parts[len(first_section_lines) :])
    return pruned, archived, kept


def append_summary(path: Path, summary: str, today: str) -> int:
    """
    Append a '## Session Summary — YYYY-MM-DD' block to the scratchpad file.

    If a summary block for today already exists, uses a counter suffix:
        ## Session Summary — YYYY-MM-DD (2)

    Uses Python file I/O only — no heredocs or shell string embedding.

    Returns 0 on success, 1 on error.
    """
    text = path.read_text(encoding="utf-8")

    # Count existing Session Summary blocks for today's date
    pattern = rf"^## Session Summary — {re.escape(today)}"
    existing = re.findall(pattern, text, re.MULTILINE)
    count = len(existing)

    if count == 0:
        heading = f"## Session Summary — {today}"
    else:
        heading = f"## Session Summary — {today} ({count + 1})"

    block = f"\n{heading}\n\n{summary}\n"

    with path.open("a", encoding="utf-8") as fh:
        fh.write(block)

    print(f"Appended session summary to {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Scratchpad size management for .tmp/<branch>/<date>.md")
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
        help=(
            "[DEPRECATED] Prune regardless of line count (bypasses size guard). "
            "Per-day session files make aggressive compression unnecessary. "
            "Use --init (new session) instead. --force still archives to "
            "docs/sessions/ for backward compatibility, but compression is "
            "discouraged — prefer letting each day's file persist intact."
        ),
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
    parser.add_argument(
        "--append-summary",
        metavar="TEXT",
        default=None,
        help=(
            "Append a '## Session Summary' block to today's scratchpad file. "
            "Uses Python file I/O — safe for content containing backticks or "
            "special characters that would corrupt heredoc writes."
        ),
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help=(
            "Run corruption detection only. Exits 0 if no corruption found, "
            "1 if corrupted lines are detected. Does not modify any file."
        ),
    )
    args = parser.parse_args()

    today = date.today().isoformat()

    if args.init:
        path = resolve_active_file()
        pre_exists = path.exists()
        init_session_file(path)
        # Warn about corruption if the file already existed (init does not overwrite)
        if pre_exists and path.exists():
            text = path.read_text(encoding="utf-8")
            corrupted = detect_corruption(text)
            if corrupted:
                line_nums = ", ".join(str(n) for n in corrupted)
                print(
                    f"WARNING: Possible scratchpad corruption detected in {path}\n"
                    f"Lines with repeated heading patterns: {line_nums}\n"
                    "Run with --check-only to inspect without modifying.",
                    file=sys.stderr,
                )
        # Warn if git stashes exist — pre-existing fixes may be stashed and missed
        try:
            import subprocess as _sp

            stash_out = _sp.run(
                ["git", "stash", "list"],
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.strip()
            if stash_out:
                stash_count = len(stash_out.splitlines())
                print(
                    f"\nWARNING: {stash_count} git stash(es) exist — review before proceeding:\n"
                    f"{stash_out}\n"
                    "Pre-existing fixes may be stashed. Run `git stash show -p stash@{0}` to inspect.",
                    file=sys.stderr,
                )
        except Exception:
            pass
        return 0

    if args.file:
        path = Path(args.file)
    else:
        path = resolve_active_file()

    # --check-only: corruption detection only, no modifications
    if args.check_only:
        if not path.exists():
            print(f"ERROR: {path} not found.", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        corrupted = detect_corruption(text)
        if corrupted:
            line_nums = ", ".join(str(n) for n in corrupted)
            print(
                f"WARNING: Possible scratchpad corruption detected in {path}\n"
                f"Lines with repeated heading patterns: {line_nums}\n"
                "Run with --check-only to inspect without modifying.",
                file=sys.stderr,
            )
            return 1
        print(f"OK: No corruption detected in {path}")
        return 0

    # --append-summary: safe Python-based session summary write
    if args.append_summary is not None:
        if not path.exists():
            print(f"ERROR: No scratchpad file found at {path}", file=sys.stderr)
            return 1
        return append_summary(path, args.append_summary, today)

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

    # Corruption check — warn but do not abort pruning
    corrupted = detect_corruption(text)
    if corrupted:
        line_nums = ", ".join(str(n) for n in corrupted)
        print(
            f"WARNING: Possible scratchpad corruption detected in {path}\n"
            f"Lines with repeated heading patterns: {line_nums}\n"
            "Run with --check-only to inspect without modifying.",
            file=sys.stderr,
        )

    line_count = text.count("\n")

    if not args.force and line_count < SIZE_GUARD:
        print(f"INFO: {path} has {line_count} lines (threshold: {SIZE_GUARD}). No pruning needed.")
        return 0

    if args.force:
        import warnings

        warnings.warn(
            "--force (compression) is deprecated. Per-day session files make "
            "aggressive pruning unnecessary. The archive step (docs/sessions/) "
            "still runs. Prefer --init for new sessions; let existing files persist intact.",
            DeprecationWarning,
            stacklevel=2,
        )
        print(
            "DEPRECATION WARNING: --force compression is discouraged. "
            "Session files are now per-day; let them persist intact. "
            "Archive step (docs/sessions/) will still run.",
            file=sys.stderr,
        )

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
        archive_to_sessions(path, pruned, path.stem, path.parent.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
