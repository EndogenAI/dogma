#!/usr/bin/env python3
"""
Setup sprint milestones and assign issues to them.

Based on docs/plans/2026-03-25-next-sprint-recommendation.md, this script:
1. Defines Q2 Governance Wave milestones with phase-based issue assignments
2. Provides --dry-run preview of all assignments
3. Executes assignments with --apply flag via gh milestone API
4. Returns: 0 on success, 1 on API error, 2 on usage error

Usage:
    uv run python scripts/setup_sprint_milestones.py --dry-run
    uv run python scripts/setup_sprint_milestones.py --apply

Pre-populated from: docs/plans/2026-03-25-next-sprint-recommendation.md
Sprint Structure:
  - Q2 Governance Wave 1 (Apr 1–8): Phases 0–2
  - Q2 Governance Wave 2 (Apr 8–22): Phases 3–4 (future sprint)
  - Backlog — Research & Secondary: Bare-bones research + long-tail
"""

import argparse
import json
import subprocess
import sys

# Pre-populated milestone definitions (from sprint recommendation)
MILESTONES = {
    "Q2 Governance Wave 1": {
        "description": "Phase 0–2: Branch sync, security hardening, research infrastructure (Apr 1–8)",
        "due_on": "2026-04-08T00:00:00Z",
        "state": "open",
    },
    "Q2 Governance Wave 2": {
        "description": "Phase 3–4: Agent fleet standardization, observability metrics (Apr 8–22)",
        "due_on": "2026-04-22T00:00:00Z",
        "state": "open",
    },
    "Backlog — Research & Secondary": {
        "description": "Bare-bones research sprints, long-tail issues, and deferred work",
        "due_on": None,
        "state": "open",
    },
}

# Pre-populated phase-to-issues mapping (from sprint recommendation doc)
PHASE_ASSIGNMENTS = {
    "Q2 Governance Wave 1": {
        "Phase 0 (Blocking)": [388, 435],
        "Phase 1 (Security)": [424, 423, 360, 361, 357],
        "Phase 2 (Research)": [422, 410, 411, 402],
    },
    "Q2 Governance Wave 2": {
        "Phase 3 (Agent Fleet)": [332, 333, 335, 334, 331, 336],
        "Phase 4 (Observability)": [369, 376, 342, 343, 346, 345, 344],
    },
    "Backlog — Research & Secondary": {
        "Phase 5 (Skills & Automation)": [432],
        "Research Track": [414, 413, 421, 426, 415, 419],
        "Deferred (Q2 Wave 2 later waves)": [358, 352, 355, 359, 428, 350, 113, 283, 131, 128, 427, 430, 429, 425],
    },
}


def run_gh_command(args: list, capture_output: bool = True) -> tuple[int, str, str]:
    """Run a gh CLI command and return (exit_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=capture_output,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "gh command timed out (30s)"
    except FileNotFoundError:
        return 1, "", "gh CLI not found. Install with: brew install gh"


def get_current_milestones() -> dict:
    """Fetch current milestones from GitHub API."""
    exit_code, stdout, stderr = run_gh_command(
        ["api", "repos/EndogenAI/dogma/milestones", "--jq", ".[] | {title, state, open_issues, closed_issues, due_on}"]
    )
    if exit_code != 0:
        print(f"Error fetching milestones: {stderr}", file=sys.stderr)
        return {}

    milestones = {}
    for line in stdout.strip().split("\n"):
        if line:
            try:
                data = json.loads(line)
                milestones[data["title"]] = data
            except json.JSONDecodeError:
                pass
    return milestones


def get_open_issues() -> dict:
    """Fetch all open issues. Returns {issue_number: {number, title, milestone}}."""
    exit_code, stdout, stderr = run_gh_command(
        [
            "issue",
            "list",
            "--repo",
            "EndogenAI/dogma",
            "--state",
            "open",
            "--limit",
            "500",
            "--json",
            "number,title,milestone",
        ]
    )
    if exit_code != 0:
        print(f"Error fetching issues: {stderr}", file=sys.stderr)
        return {}

    issues = {}
    try:
        data = json.loads(stdout)
        for issue in data:
            issues[issue["number"]] = issue
    except json.JSONDecodeError:
        print(f"Error parsing issues JSON: {stdout[:100]}", file=sys.stderr)
    return issues


def assign_issue_to_milestone(issue_number: int, milestone_title: str, dry_run: bool = False) -> bool:
    """Assign an issue to a milestone. Returns True on success."""
    if dry_run:
        return True

    exit_code, stdout, stderr = run_gh_command(
        ["issue", "edit", str(issue_number), "--repo", "EndogenAI/dogma", "--milestone", milestone_title]
    )
    return exit_code == 0


def create_or_update_milestone(title: str, milestone_def: dict, dry_run: bool = False) -> bool:
    """Create or update a milestone. Returns True on success."""
    if dry_run:
        return True

    # Check if milestone exists
    exit_code, stdout, stderr = run_gh_command(
        [
            "api",
            "repos/EndogenAI/dogma/milestones",
            "--jq",
            f'.[] | select(.title == "{title}") | .number',
        ]
    )

    milestone_number = None
    if exit_code == 0 and stdout.strip():
        try:
            milestone_number = int(stdout.strip())
        except ValueError:
            pass

    if milestone_number:
        # Update existing milestone
        exit_code, stdout, stderr = run_gh_command(
            [
                "api",
                f"repos/EndogenAI/dogma/milestones/{milestone_number}",
                "-X",
                "PATCH",
                "-f",
                f"title={title}",
                "-f",
                f"description={milestone_def.get('description', '')}",
                "-f",
                f"state={milestone_def.get('state', 'open')}",
            ]
            + (["-f", f"due_on={milestone_def['due_on']}"] if milestone_def.get("due_on") else [])
        )
    else:
        # Create new milestone
        exit_code, stdout, stderr = run_gh_command(
            [
                "api",
                "repos/EndogenAI/dogma/milestones",
                "-X",
                "POST",
                "-f",
                f"title={title}",
                "-f",
                f"description={milestone_def.get('description', '')}",
                "-f",
                f"state={milestone_def.get('state', 'open')}",
            ]
            + (["-f", f"due_on={milestone_def['due_on']}"] if milestone_def.get("due_on") else [])
        )

    return exit_code == 0


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview all milestone operations without making changes",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute all milestone operations",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        parser.print_help()
        return 2

    dry_run = args.dry_run
    print(f"\n{'=' * 80}")
    print(f"Sprint Milestone Setup: {'DRY-RUN' if dry_run else 'APPLY'}")
    print(f"{'=' * 80}\n")

    # Fetch current state
    print("Fetching current milestone and issue state...")
    current_milestones = get_current_milestones()
    current_issues = get_open_issues()
    print(f"  Current milestones: {len(current_milestones)}")
    print(f"  Open issues: {len(current_issues)}\n")

    # Milestone Operations
    print("Milestone Operations:")
    print("-" * 80)
    milestone_ops = []
    for title, definition in MILESTONES.items():
        if title in current_milestones:
            status = "UPDATE"
        else:
            status = "CREATE"
        milestone_ops.append((title, status, definition))
        due_str = definition.get("due_on", "N/A")
        print(f"  {status:6} | {title:40} | Due: {due_str}")

    print("\n")

    # Issue Assignments
    print("Issue Assignments by Milestone:")
    print("-" * 80)
    total_assigned = 0
    assignment_plan = {}

    for milestone_title, phases in PHASE_ASSIGNMENTS.items():
        assignment_plan[milestone_title] = {}
        issues_in_milestone = []

        for phase_name, issue_numbers in phases.items():
            valid_issues = [num for num in issue_numbers if num in current_issues]
            assignment_plan[milestone_title][phase_name] = valid_issues
            issues_in_milestone.extend(valid_issues)

            print(f"  {milestone_title} > {phase_name}")
            print(f"    Issues: {', '.join(str(n) for n in valid_issues)}")
            if len(valid_issues) < len(issue_numbers):
                missing = [n for n in issue_numbers if n not in current_issues]
                print(f"    Missing (closed?): {', '.join(str(n) for n in missing)}")

        total_assigned += len(issues_in_milestone)
        print()

    print(f"Total issues to assign: {total_assigned} of {len(current_issues)} open issues")
    print("Unassigned will remain in current milestone or backlog.\n")

    # Execute if --apply
    if not dry_run:
        print("=" * 80)
        print("EXECUTING OPERATIONS")
        print("=" * 80 + "\n")

        success_count = 0
        error_count = 0

        # Create/update milestones
        print("Creating/updating milestones...")
        for title, status, definition in milestone_ops:
            if create_or_update_milestone(title, definition, dry_run=False):
                print(f"  ✓ {status} milestone: {title}")
                success_count += 1
            else:
                print(f"  ✗ FAILED to {status} milestone: {title}")
                error_count += 1

        print()

        # Assign issues
        print("Assigning issues to milestones...")
        for milestone_title, phases in assignment_plan.items():
            for phase_name, issue_numbers in phases.items():
                for issue_num in issue_numbers:
                    if assign_issue_to_milestone(issue_num, milestone_title, dry_run=False):
                        print(f"  ✓ #{issue_num} → {milestone_title}")
                        success_count += 1
                    else:
                        print(f"  ✗ FAILED: #{issue_num} → {milestone_title}")
                        error_count += 1

        print()
        print("=" * 80)
        print(f"Results: {success_count} successful, {error_count} errors")
        print("=" * 80 + "\n")

        return 0 if error_count == 0 else 1
    else:
        # Dry-run: just show the plan
        print("=" * 80)
        print("DRY-RUN COMPLETE (no changes made)")
        print("=" * 80)
        print("\nRun with --apply to execute these operations:\n")
        print("  uv run python scripts/setup_sprint_milestones.py --apply\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
