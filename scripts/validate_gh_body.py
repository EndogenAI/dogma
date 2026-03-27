#!/usr/bin/env python3
"""Validate gh CLI commands use --body-file for multi-line content.

Purpose:
    Scans scripts and markdown files for gh CLI commands that pass multi-line
    content via --body "..." instead of the safer --body-file pattern.
    Multi-line strings in --body cause shell quoting issues and silent corruption.

Inputs:
    [paths]: Files or directories to check (default: scripts/ and docs/)

Outputs:
    Exit 0: All gh commands use --body-file correctly
    Exit 1: Found violations (--body with multi-line strings)
    Exit 2: I/O error

Usage:
    # Check default locations
    uv run python scripts/validate_gh_body.py

    # Check specific files
    uv run python scripts/validate_gh_body.py scripts/my_script.py

    # Check directory
    uv run python scripts/validate_gh_body.py .github/workflows/

Exit Codes:
    0: Compliant (no multi-line --body usage found)
    1: Violations found (gh commands using --body with multi-line content)
    2: Error (I/O failure)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def check_file_content(filepath: Path) -> List[Tuple[int, str]]:
    """Check file for gh CLI --body violations.

    Returns list of (line_number, violation_snippet) tuples.
    """
    violations = []

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return []

    lines = content.split("\n")

    # Pattern to detect gh issue/pr create with --body "..." on command line
    # This is fragile but catches the most common violations
    gh_body_pattern = re.compile(r'gh\s+(issue|pr)\s+create.*--body\s+"[^"]*\n', re.MULTILINE)

    # Also check for --body with variables that might be multi-line
    gh_body_var_pattern = re.compile(r'gh\s+(issue|pr)\s+create.*--body\s+"\$[^"]*"')

    for match in gh_body_pattern.finditer(content):
        # Find line number
        line_num = content[: match.start()].count("\n") + 1
        snippet = match.group(0).replace("\n", " ")[:80]
        violations.append((line_num, snippet))

    for i, line in enumerate(lines, start=1):
        # Check for --body with variable
        if gh_body_var_pattern.search(line):
            # Try to determine if this is likely multi-line
            # Look for clues like "body=" assignment with multi-line markers
            context_start = max(0, i - 3)
            context = "\n".join(lines[context_start:i])

            # If previous lines have HERE doc or multi-line assignment
            if re.search(r'<<|\\n|"""', context):
                violations.append((i, line.strip()[:80]))

    return violations


def scan_paths(paths: List[Path]) -> Dict[Path, List[Tuple[int, str]]]:
    """Scan all paths for violations.

    Returns dict of {filepath: violations}.
    """
    all_violations = {}

    for path in paths:
        if path.is_file():
            violations = check_file_content(path)
            if violations:
                all_violations[path] = violations
        elif path.is_dir():
            # Scan Python and shell scripts
            for pattern in ["*.py", "*.sh", "*.md"]:
                for filepath in path.rglob(pattern):
                    # Skip .cache and site directories
                    if ".cache" in filepath.parts or "site" in filepath.parts:
                        continue

                    violations = check_file_content(filepath)
                    if violations:
                        all_violations[filepath] = violations

    return all_violations


def main():
    parser = argparse.ArgumentParser(description="Validate gh CLI commands use --body-file for multi-line content")
    parser.add_argument(
        "paths", nargs="*", type=Path, help="Files or directories to check (default: scripts/ and docs/)"
    )

    args = parser.parse_args()

    # Default to scripts/ and docs/ if no paths provided
    if not args.paths:
        paths = [Path("scripts"), Path("docs")]
    else:
        paths = args.paths

    # Verify paths exist
    valid_paths = []
    for path in paths:
        if not path.exists():
            print(f"Warning: {path} does not exist, skipping", file=sys.stderr)
        else:
            valid_paths.append(path)

    if not valid_paths:
        print("Error: No valid paths to check", file=sys.stderr)
        sys.exit(2)

    all_violations = scan_paths(valid_paths)

    if all_violations:
        print("gh CLI --body violations found:\n")
        for filepath, violations in all_violations.items():
            print(f"{filepath}:")
            for line_num, snippet in violations:
                print(f"  Line {line_num}: {snippet}")
        print('\n⚠️  Use --body-file <path> instead of --body "..." for multi-line content')
        sys.exit(1)
    else:
        print("✓ All gh CLI commands use --body-file correctly")
        sys.exit(0)


if __name__ == "__main__":
    main()
