"""scripts/orientation_snapshot.py

Pre-computed session orientation digest for agent session start.

Purpose:
    Generate a concise (< 200 lines) orientation context snapshot at
    .cache/github/orientation-snapshot.md. Designed to be run once at session
    start so agents have pre-fetched orientation data without issuing multiple
    gh/git API calls during the session.

    Captures:
    - Open issues count by priority label
    - Last 5 commits on current branch
    - Active branches with last commit date
    - Current milestone summary (if any)
    - Latest ## Session Summary section from the active branch scratchpad (optional)

Inputs:
    --branch BRANCH    Include the active scratchpad session summary for this branch
    --output PATH      Override the output file path
                       (default: .cache/github/orientation-snapshot.md)
    --dry-run          Print the snapshot to stdout without writing the file

Outputs:
    .cache/github/orientation-snapshot.md   Pre-computed orientation digest

Usage:
    uv run python scripts/orientation_snapshot.py
    uv run python scripts/orientation_snapshot.py --branch feat/my-feature
    uv run python scripts/orientation_snapshot.py --dry-run

Exit codes:
    0   Snapshot written (or printed) successfully
    1   Unexpected error
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_DEFAULT_OUTPUT = Path(".cache/github/orientation-snapshot.md")


# ---------------------------------------------------------------------------
# Data collectors
# ---------------------------------------------------------------------------


def _run(cmd: list[str], cwd: str | None = None) -> str:
    """Run a subprocess command, returning stdout or empty string on failure."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except OSError:
        return ""


def _collect_issue_counts() -> str:
    """Return a Markdown section with open issue counts by priority label."""
    lines = ["## Open Issues by Priority\n"]
    for priority in ("critical", "high", "medium", "low"):
        label = f"priority:{priority}"
        raw = _run(["gh", "issue", "list", "--label", label, "--state", "open", "--json", "number"])
        count = raw.count('"number"') if raw else 0
        lines.append(f"- **{priority}**: {count}")
    # Total open
    total_raw = _run(["gh", "issue", "list", "--state", "open", "--json", "number", "--limit", "500"])
    total = total_raw.count('"number"') if total_raw else "?"
    lines.append(f"- **total open**: {total}")
    return "\n".join(lines)


def _collect_recent_commits() -> str:
    """Return a Markdown section with the last 5 commits."""
    raw = _run(["git", "log", "--oneline", "-5", "--no-color"])
    if not raw:
        return "## Recent Commits\n\n_(no commits found)_"
    lines = ["## Recent Commits (last 5)\n"]
    for line in raw.splitlines():
        lines.append(f"- `{line}`")
    return "\n".join(lines)


def _collect_active_branches() -> str:
    """Return a Markdown section with active branches and their last commit date."""
    raw = _run(
        [
            "git",
            "branch",
            "-r",
            "--sort=-committerdate",
            "--format=%(refname:short) %(committerdate:short)",
        ]
    )
    if not raw:
        # Fall back to local branches
        raw = _run(
            [
                "git",
                "branch",
                "--sort=-committerdate",
                "--format=%(refname:short) %(committerdate:short)",
            ]
        )
    if not raw:
        return "## Active Branches\n\n_(none found)_"
    lines = ["## Active Branches\n"]
    for entry in raw.splitlines()[:10]:  # cap at 10
        parts = entry.strip().split()
        if len(parts) >= 2:
            branch, date = parts[0], parts[1]
            lines.append(f"- `{branch}` — {date}")
        elif parts:
            lines.append(f"- `{parts[0]}`")
    return "\n".join(lines)


def _collect_milestone_summary() -> str:
    """Return a Markdown section with the current open milestone summary."""
    raw = _run(
        [
            "gh",
            "api",
            "repos/{owner}/{repo}/milestones",
            "--jq",
            (
                '.[] | select(.state=="open")'
                ' | "- **\\(.title)** — \\(.open_issues) open'
                ' / \\(.closed_issues) closed (due: \\(.due_on // "none"))"'
            ),
        ]
    )
    if not raw:
        return "## Current Milestones\n\n_(none open or gh unavailable)_"
    lines = ["## Current Milestones\n"]
    lines.extend(raw.splitlines())
    return "\n".join(lines)


def _extract_session_summary(branch: str) -> str:
    """
    Extract the latest ## Session Summary block from the branch scratchpad.

    Returns a Markdown section string, or a note if not found.
    """
    slug = branch.replace("/", "-")
    tmp_dir = Path(".tmp") / slug
    if not tmp_dir.exists():
        return f"## Scratchpad Session Summary\n\n_(no scratchpad directory for branch `{branch}`)_"

    # Find the most recent date file
    md_files = sorted(tmp_dir.glob("*.md"), reverse=True)
    if not md_files:
        return f"## Scratchpad Session Summary\n\n_(no scratchpad files for branch `{branch}`)_"

    content = md_files[0].read_text()
    # Find ## Session Summary (last occurrence)
    pattern = re.compile(r"(## Session Summary.*?)(?=\n## |\Z)", re.DOTALL)
    matches = pattern.findall(content)
    if not matches:
        return f"## Scratchpad Session Summary\n\n_(no `## Session Summary` found in `{md_files[0].name}`)_"

    summary = matches[-1].strip()
    return f"## Scratchpad Session Summary (from `{md_files[0].name}`)\n\n{summary}"


# ---------------------------------------------------------------------------
# Snapshot builder
# ---------------------------------------------------------------------------


def build_snapshot(branch: str | None = None) -> str:
    """
    Build the full orientation snapshot Markdown string.

    Args:
        branch: Optional branch name to include scratchpad session summary.

    Returns:
        Markdown string, always < 200 lines.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sections = [
        f"# Orientation Snapshot — {now}\n\n"
        "_Pre-computed at session start. Run `uv run python scripts/orientation_snapshot.py`"
        " to refresh._\n",
        _collect_issue_counts(),
        _collect_recent_commits(),
        _collect_active_branches(),
        _collect_milestone_summary(),
    ]
    if branch:
        sections.append(_extract_session_summary(branch))

    content = "\n\n".join(sections)
    lines = content.splitlines()
    if len(lines) > 198:
        # Hard-cap to stay < 200 lines; note truncation
        lines = lines[:196] + ["", "_(snapshot truncated to 198 lines)_"]
        content = "\n".join(lines)
    return content


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a pre-computed session orientation digest.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--branch",
        metavar="BRANCH",
        help="Include the latest scratchpad ## Session Summary for this branch",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        default=str(_DEFAULT_OUTPUT),
        help=f"Output file path (default: {_DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print snapshot to stdout without writing the file",
    )
    args = parser.parse_args(argv)

    snapshot = build_snapshot(branch=args.branch)

    if args.dry_run:
        print(snapshot)
        return 0

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(snapshot)
    print(f"[ok] Orientation snapshot written to {output_path} ({len(snapshot.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
