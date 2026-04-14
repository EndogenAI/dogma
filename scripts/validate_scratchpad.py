"""scripts/validate_scratchpad.py

Programmatic quality gate for scratchpad files — enforces schema compliance
for .tmp/<branch>/<date>.md session state files.

Purpose:
    Validate scratchpad structural requirements to prevent encoding drift
    in session-state persistence, cross-agent coordination, and phase-gate
    compliance. Derived from AGENTS.md § Agent Communication and the
    session-management SKILL.md.

Checks:
    1. Required sections present (Session State, Audit Trail, Telemetry).
    2. Session State YAML block parses without errors.
    3. Session State contains required fields (branch, date, active_phase, etc.).
    4. Filename date matches Session State 'date:' field.
    5. Heading hierarchy is valid (no skipped levels: H1 → H2 → H3).
    6. Phase sections numbered consecutively (Phase 1, Phase 2, ...).
    7. Audit Trail and Telemetry sections contain tables (may be empty).

Inputs:
    <file>         Path to scratchpad file to validate.  (positional, optional)
    --all          Scan every *.md file in .tmp/*/ directories.
    --check-only   Exit 0/1 without output (for CI).
    --verbose      Show detailed validation steps.

Outputs:
    stdout:  Human-readable pass/fail summary with specific gap list.
    stderr:  Nothing (all output goes to stdout for easy capture).

Exit codes:
    0  All checks passed.
    1  One or more checks failed — specific gap(s) reported to stdout.
    2  Invalid usage — no file argument and --all not specified.

Usage examples:
    # Validate a single scratchpad file
    uv run python scripts/validate_scratchpad.py .tmp/feat-my-branch/2026-04-13.md

    # Validate all scratchpad files
    uv run python scripts/validate_scratchpad.py --all

    # CI mode (no output, just exit code)
    uv run python scripts/validate_scratchpad.py --all --check-only

Schema reference:
    data/scratchpad-schema.yml
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: uv sync", file=sys.stderr)
    sys.exit(2)

# ---------------------------------------------------------------------------
# Schema Constants (from data/scratchpad-schema.yml)
# ---------------------------------------------------------------------------

REQUIRED_SECTIONS = [
    "Session State",
    "Audit Trail",
    "Telemetry",
]

SESSION_STATE_REQUIRED_FIELDS = [
    "branch",
    "date",
    "active_phase",
    "active_issues",
    "blockers",
    "last_agent",
    "phases",
]

# Filename must be YYYY-MM-DD.md
FILENAME_DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")

# Session State date format: YYYY-MM-DD
SESSION_STATE_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Phase section heading patterns
PHASE_OUTPUT_PATTERN = re.compile(r"^## Phase (\d+) Output", re.MULTILINE)
PHASE_REVIEW_PATTERN = re.compile(r"^## (?:Phase (\d+) )?Review Output", re.MULTILINE)

# Heading level extraction
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

# YAML frontmatter or fenced block (```yaml ... ```)
YAML_BLOCK_PATTERN = re.compile(r"(?:^```ya?ml\n(.*?)\n```|^```\n(.*?)\n```)", re.MULTILINE | re.DOTALL)

# Markdown table detection (simple heuristic: | ... | on consecutive lines)
TABLE_PATTERN = re.compile(r"^\|.+\|$", re.MULTILINE)


# ---------------------------------------------------------------------------
# Validation Functions
# ---------------------------------------------------------------------------


def extract_session_state_yaml(content: str, section_start: int, section_end: int) -> dict[str, Any] | None:
    """
    Extract and parse the YAML block from the Session State section.

    Returns parsed dict on success, None if YAML block not found or invalid.
    """
    section_content = content[section_start:section_end]

    # Try to find YAML fenced block first
    match = YAML_BLOCK_PATTERN.search(section_content)
    if match:
        yaml_text = match.group(1) or match.group(2)
        try:
            return yaml.safe_load(yaml_text)
        except yaml.YAMLError:
            return None

    return None


def find_section_bounds(content: str, section_name: str) -> tuple[int, int] | None:
    """
    Find start and end positions of a section in the content.

    Returns (start_pos, end_pos) tuple or None if section not found.
    End position is the start of the next H2 section or end of file.
    """
    # Match "## Section Name" with optional trailing content
    pattern = re.compile(rf"^## {re.escape(section_name)}\s*$", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        return None

    start = match.start()

    # Find next H2 heading or end of file
    next_h2 = re.compile(r"^## ", re.MULTILINE)
    next_match = next_h2.search(content, match.end())
    end = next_match.start() if next_match else len(content)

    return (start, end)


def check_table_present(content: str, section_name: str) -> bool:
    """
    Check if a markdown table is present in the given section.

    Returns True if at least one table row is found, False otherwise.
    """
    bounds = find_section_bounds(content, section_name)
    if not bounds:
        return False

    section_content = content[bounds[0] : bounds[1]]
    return bool(TABLE_PATTERN.search(section_content))


def validate_heading_hierarchy(content: str) -> list[str]:
    """
    Validate that headings don't skip levels (e.g., H1 → H3).

    Returns list of error messages (empty if valid).
    """
    errors = []
    # Strip fenced code blocks so headings inside them are not evaluated
    content_no_fences = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    headings = HEADING_PATTERN.findall(content_no_fences)

    prev_level = 0
    for hashes, text in headings:
        level = len(hashes)

        # Allow first heading to be any level
        if prev_level == 0:
            prev_level = level
            continue

        # Check for skipped levels (e.g., H2 → H4)
        if level > prev_level + 1:
            errors.append(f"Heading hierarchy violation: skipped from H{prev_level} to H{level} ('{text}')")

        prev_level = level

    return errors


def validate_phase_numbering(content: str) -> list[str]:
    """
    Validate that Phase N sections are numbered consecutively.

    Returns list of error messages (empty if valid).
    """
    errors = []

    # Find all Phase N Output and Phase N Review sections
    phase_review_pattern = re.compile(r"^## Phase (\d+) Review\b", re.MULTILINE)
    matches = PHASE_OUTPUT_PATTERN.findall(content) + phase_review_pattern.findall(content)
    if not matches:
        # No Phase sections found — valid (e.g., pre-workplan session)
        return errors

    phase_numbers = sorted([int(m) for m in matches])

    # Check for gaps
    expected = 1
    for num in phase_numbers:
        if num != expected:
            errors.append(f"Phase numbering gap: found Phase {num} but expected Phase {expected}")
        expected = num + 1

    return errors


def validate_scratchpad(file_path: Path, verbose: bool = False) -> tuple[bool, list[str]]:
    """
    Validate a single scratchpad file against schema.

    Returns (is_valid, errors) tuple.
    """
    errors = []

    # Check file exists
    if not file_path.exists():
        return (False, [f"File not found: {file_path}"])

    if not file_path.is_file():
        return (False, [f"Not a file: {file_path}"])

    # Read content
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return (False, [f"Failed to read file: {e}"])

    if verbose:
        print(f"Validating: {file_path}")

    # Check 1: Required sections present
    for section in REQUIRED_SECTIONS:
        if not find_section_bounds(content, section):
            errors.append(f"Required section '{section}' not found")

    # Check 2: Session State YAML parses
    session_state_bounds = find_section_bounds(content, "Session State")
    session_state_data = None

    if session_state_bounds:
        session_state_data = extract_session_state_yaml(content, session_state_bounds[0], session_state_bounds[1])
        if session_state_data is None:
            errors.append("Session State YAML block not found or failed to parse")

    # Check 3: Session State required fields
    if session_state_data:
        for field in SESSION_STATE_REQUIRED_FIELDS:
            if field not in session_state_data:
                errors.append(f"Session State missing required field: '{field}'")

    # Check 4: Filename date matches Session State date
    filename_match = FILENAME_DATE_PATTERN.match(file_path.name)
    if filename_match:
        filename_date = filename_match.group(1)
        if session_state_data and "date" in session_state_data:
            state_date = str(session_state_data["date"])
            if filename_date != state_date:
                errors.append(f"Filename date '{filename_date}' does not match Session State date '{state_date}'")
    else:
        errors.append(f"Filename does not match pattern YYYY-MM-DD.md: {file_path.name}")

    # Check 5: Heading hierarchy
    hierarchy_errors = validate_heading_hierarchy(content)
    errors.extend(hierarchy_errors)

    # Check 6: Phase numbering
    phase_errors = validate_phase_numbering(content)
    errors.extend(phase_errors)

    # Check 7: Tables present in Audit Trail and Telemetry
    if not check_table_present(content, "Audit Trail"):
        # Note: Empty table is valid, so we just check for table structure
        # This is a soft check — will only fail if section exists but has no table at all
        if find_section_bounds(content, "Audit Trail"):
            # Section exists, now check if it has at least table header markers
            bounds = find_section_bounds(content, "Audit Trail")
            section_content = content[bounds[0] : bounds[1]]
            if "|" not in section_content:
                errors.append("Audit Trail section missing table structure")

    if not check_table_present(content, "Telemetry"):
        if find_section_bounds(content, "Telemetry"):
            bounds = find_section_bounds(content, "Telemetry")
            section_content = content[bounds[0] : bounds[1]]
            if "|" not in section_content:
                errors.append("Telemetry section missing table structure")

    return (len(errors) == 0, errors)


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate scratchpad files against schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python scripts/validate_scratchpad.py .tmp/feat-my-branch/2026-04-13.md
  uv run python scripts/validate_scratchpad.py --all
  uv run python scripts/validate_scratchpad.py --all --check-only
        """,
    )

    parser.add_argument("file", nargs="?", type=Path, help="Path to scratchpad file to validate")

    parser.add_argument("--all", action="store_true", help="Validate all .md files in .tmp/*/ directories")

    parser.add_argument("--check-only", action="store_true", help="Exit 0/1 without output (for CI)")

    parser.add_argument("--verbose", action="store_true", help="Show detailed validation steps")

    args = parser.parse_args()

    # Determine files to validate
    files_to_validate: list[Path] = []

    if args.all:
        # Scan .tmp/*/ for all .md files
        tmp_dir = Path(".tmp")
        if tmp_dir.exists():
            for branch_dir in tmp_dir.iterdir():
                if branch_dir.is_dir():
                    for md_file in branch_dir.glob("*.md"):
                        # Only validate YYYY-MM-DD.md files
                        if FILENAME_DATE_PATTERN.match(md_file.name):
                            files_to_validate.append(md_file)
    elif args.file:
        files_to_validate.append(args.file)
    else:
        parser.print_help()
        return 2

    if not files_to_validate:
        if not args.check_only:
            print("No scratchpad files found to validate")
        return 0

    # Validate each file
    all_valid = True
    results: list[tuple[Path, bool, list[str]]] = []

    for file_path in files_to_validate:
        is_valid, errors = validate_scratchpad(file_path, verbose=args.verbose)
        results.append((file_path, is_valid, errors))
        if not is_valid:
            all_valid = False

    # Report results
    if not args.check_only:
        for file_path, is_valid, errors in results:
            if is_valid:
                print(f"PASS — {file_path}")
            else:
                print(f"FAIL — {file_path}:")
                for error in errors:
                    print(f"  - {error}")

        # Summary
        passed = sum(1 for _, valid, _ in results if valid)
        failed = len(results) - passed
        print(f"\nSummary: {passed} passed, {failed} failed")

    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
