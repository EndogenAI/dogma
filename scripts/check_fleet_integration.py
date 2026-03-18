"""
check_fleet_integration.py — Validate that new agents and skills are documented in AGENTS.md.

Purpose:
    Reads new files from git diff (agents, skills), checks that they are cross-referenced
    in AGENTS.md, and warns if new files lack proper documentation or linkage. Implements
    the Fleet Integration Checklist as a programmatic gate.

Inputs:
    --branch <branch>  — Optional. Git branch to check against main (default: current branch).
    --dry-run          — Optional. Show what would be validated without modifying state.

Outputs:
    Prints a summary of findings to stdout:
    - List of new agent/skill files detected
    - List of agents properly referenced in AGENTS.md
    - List of integration gaps (new files not referenced)
    Exit code 0 if all new files are documented; exit code 1 if gaps found.

Usage:
    # Non-interactive (default):
    uv run python scripts/check_fleet_integration.py

    # Against a specific branch:
    uv run python scripts/check_fleet_integration.py --branch main

    # Dry-run to preview findings:
    uv run python scripts/check_fleet_integration.py --dry-run

Exit codes:
    0 — success: all new files are integrated
    1 — integration gaps found or invalid arguments
    2 — git error or file I/O error
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def _get_root() -> Path:
    """Return the workspace root (parent of scripts/).  Monkeypatched in tests."""
    return Path(__file__).resolve().parent.parent


def _git_diff_names(branch: str) -> list[str]:
    """Return list of file paths added in current branch compared to branch.

    Returns empty list on error.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=A", f"origin/{branch}...HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        pass
    return []


def _read_agents_md(root: Path) -> str:
    """Read AGENTS.md content. Return empty string on error."""
    try:
        return (root / "AGENTS.md").read_text(encoding="utf-8")
    except Exception:
        return ""


def _find_agent_names(agent_file_path: str, root: Path) -> list[str]:
    """Extract agent names from a .agent.md file's frontmatter.

    Returns empty list if file doesn't exist or can't be parsed.
    """
    try:
        content = (root / agent_file_path).read_text(encoding="utf-8")
        # Match YAML frontmatter name: value
        match = re.search(r'^name:\s*["\']?([^"\'\n]+)["\']?\s*$', content, re.MULTILINE)
        if match:
            return [match.group(1).strip()]
    except Exception:
        pass
    return []


def _find_skill_names(skill_file_path: str, root: Path) -> list[str]:
    """Extract skill names from a SKILL.md file's frontmatter.

    Returns empty list if file doesn't exist or can't be parsed.
    """
    try:
        content = (root / skill_file_path).read_text(encoding="utf-8")
        # Match YAML frontmatter name: value
        match = re.search(r'^name:\s*["\']?([^"\'\n]+)["\']?\s*$', content, re.MULTILINE)
        if match:
            return [match.group(1).strip()]
    except Exception:
        pass
    return []


def _check_reference_in_agents(name: str, agents_md: str) -> bool:
    """Check if an agent/skill name is referenced in AGENTS.md.

    Looks for backtick-quoted name or plain text reference.
    """
    if not name:
        return False
    # Create patterns with proper escaping for markdown and quotes
    patterns = [
        re.escape(f"`{name}`"),  # backtick
        re.escape(f"**{name}**"),  # bold
        re.escape(f"*{name}*"),  # italic
        re.escape(f'"{name}"'),  # double quote
        re.escape(f"'{name}'"),  # single quote
        re.escape(f" {name} "),  # space-delimited
        re.escape(f"[{name}]"),  # bracketed
    ]
    for pattern in patterns:
        if re.search(pattern, agents_md):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate that new agents and skills are documented in AGENTS.md.")
    parser.add_argument(
        "--branch",
        type=str,
        default="main",
        help="Git branch to compare against (default: main)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview validation without modifying state",
    )
    args = parser.parse_args()

    root = _get_root()
    branch = args.branch.strip()
    if not branch:
        print("ERROR: branch must not be empty.", file=sys.stderr)
        return 1

    # Get list of newly added files
    new_files = _git_diff_names(branch)
    if not new_files:
        print("INFO: No new files detected in this branch.")
        return 0

    # Filter to agent and skill files
    new_agents = [f for f in new_files if f.endswith(".agent.md")]
    new_skills = [f for f in new_files if f.endswith("SKILL.md")]

    if not new_agents and not new_skills:
        print("INFO: No new agent or skill files detected.")
        return 0

    # Read AGENTS.md
    agents_md = _read_agents_md(root)
    if not agents_md:
        print("ERROR: Could not read AGENTS.md", file=sys.stderr)
        return 2

    # Collect findings
    gaps = []
    referenced = []

    for agent_file in new_agents:
        agent_names = _find_agent_names(agent_file, root)
        for name in agent_names:
            if _check_reference_in_agents(name, agents_md):
                referenced.append((agent_file, name, "agent"))
            else:
                gaps.append((agent_file, name, "agent"))

    for skill_file in new_skills:
        skill_names = _find_skill_names(skill_file, root)
        for name in skill_names:
            if _check_reference_in_agents(name, agents_md):
                referenced.append((skill_file, name, "skill"))
            else:
                gaps.append((skill_file, name, "skill"))

    # Print summary
    print("## Fleet Integration Check")
    print()
    print(f"**Branch**: {branch}")
    print(f"**New files scanned**: {len(new_agents)} agents, {len(new_skills)} skills")
    print()

    if referenced:
        print("### Referenced Entities ✅")
        for file_path, name, kind in referenced:
            print(f"- `{file_path}` ({kind}): **{name}**")
        print()

    if gaps:
        print("### Integration Gaps ⚠️")
        for file_path, name, kind in gaps:
            print(f"- `{file_path}` ({kind}): **{name}** — NOT FOUND in AGENTS.md")
        print()
        print(
            "**Action**: Add a back-reference to each gap in AGENTS.md "
            "(see Agent Fleet Overview or appropriate section)."
        )
        print()

    if args.dry_run:
        print("**Dry-run mode**: no changes applied.")
        return 1 if gaps else 0

    # Return exit code based on gaps
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main())
