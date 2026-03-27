#!/usr/bin/env python3
"""Check for domain overlap between concurrent work sessions.

Purpose:
    Detects when a proposed branch or session might overlap with open PRs or
    active work to prevent duplicate effort and conflicting changes.

Inputs:
    --branch <name>: Check if this branch name overlaps with open PRs/work

Outputs:
    Exit 0: No overlap detected, safe to proceed
    Exit 1: Overlap detected with existing work
    Exit 2: Error (I/O failure, missing gh CLI)

Usage:
    # Check if a branch overlaps with open work
    uv run python scripts/check_domain_overlap.py --branch feat/governance

    # Check current branch
    uv run python scripts/check_domain_overlap.py

Exit Codes:
    0: Safe (no domain overlap detected)
    1: Overlap detected (concurrent work on same topic)
    2: Error (gh CLI not available, network failure)
"""

import argparse
import json
import re
import subprocess
import sys
from typing import Dict, List, Set


def get_current_branch() -> str:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def extract_keywords(branch_name: str) -> Set[str]:
    """Extract domain keywords from branch name.

    Returns set of meaningful keywords (excluding common prefixes).
    """
    # Remove common prefixes and split on separators
    cleaned = re.sub(r"^(feat|fix|chore|docs|test|refactor)/", "", branch_name)
    parts = re.split(r"[-_/]", cleaned)

    # Filter out short/common words
    stop_words = {"the", "a", "an", "and", "or", "for", "to", "in", "on", "at", "with"}
    keywords = {p.lower() for p in parts if len(p) > 2 and p.lower() not in stop_words}

    return keywords


def get_open_prs() -> List[Dict[str, str]]:
    """Get list of open PRs with their branch names and titles."""
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--json", "number,headRefName,title", "--limit", "50"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error fetching open PRs: {e}", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print("Error: gh CLI not found. Install via 'brew install gh'", file=sys.stderr)
        sys.exit(2)


def check_overlap(target_branch: str, open_prs: List[Dict[str, str]]) -> List[str]:
    """Check if target branch overlaps with any open PR.

    Returns list of overlap warnings.
    """
    warnings = []
    target_keywords = extract_keywords(target_branch)

    if not target_keywords:
        return []  # Can't meaningfully check empty keyword set

    for pr in open_prs:
        pr_branch = pr.get("headRefName", "")
        pr_title = pr.get("title", "")
        pr_num = pr.get("number", "?")

        # Skip if checking current branch against itself
        if pr_branch == target_branch:
            continue

        pr_keywords = extract_keywords(pr_branch)

        # Also extract keywords from PR title for better detection
        title_parts = re.findall(r"\b\w{3,}\b", pr_title.lower())
        pr_keywords.update(set(title_parts))

        # Check for keyword overlap
        overlap = target_keywords & pr_keywords

        if overlap:
            overlap_words = ", ".join(sorted(overlap))
            warnings.append(f"PR #{pr_num} ({pr_branch}): overlapping keywords [{overlap_words}]")

    return warnings


def main():
    parser = argparse.ArgumentParser(description="Check for domain overlap with concurrent work")
    parser.add_argument("--branch", type=str, help="Branch name to check (default: current branch)")

    args = parser.parse_args()

    target_branch = args.branch or get_current_branch()

    if not target_branch:
        print("Error: Could not determine branch name", file=sys.stderr)
        sys.exit(2)

    # Skip main branch
    if target_branch == "main":
        print("✓ Skipping overlap check for main branch")
        sys.exit(0)

    open_prs = get_open_prs()
    warnings = check_overlap(target_branch, open_prs)

    if warnings:
        print(f"⚠️  Domain overlap detected for branch '{target_branch}':\n")
        for warning in warnings:
            print(f"  {warning}")
        print("\nConsider coordinating with the PR author or choosing a different scope.")
        sys.exit(1)
    else:
        print(f"✓ No domain overlap detected for '{target_branch}'")
        sys.exit(0)


if __name__ == "__main__":
    main()
