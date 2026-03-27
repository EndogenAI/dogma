#!/usr/bin/env python3
"""Heuristically check that textual readiness claims are scoped by capability matrices.

Purpose:
    This script scans Markdown/text documents for unqualified readiness language
    (e.g., "ready", "complete", "done", "all tests pass") and verifies that
    the same document also contains capability-matrix-style scoping. It is a
    lightweight, text-level guardrail that complements the existing structured
    matrix validation performed by scripts/check_readiness_matrix.py.

    In other words:
      * scripts/check_readiness_matrix.py: validates the presence/shape/content
        of capability matrices themselves.
      * scripts/check_readiness_contract.py (this file): ensures that prose
        readiness statements in plans and docs are not left unscoped by such
        matrices.

Inputs:
    --scope <path>: Check specific file or directory (default: workspace root)

Outputs:
    Exit 0: All readiness claims are properly scoped with capability matrices
    Exit 1: Found unqualified readiness claims without matrices
    Exit 2: I/O error or invalid arguments

Usage:
    # Check entire workspace
    uv run python scripts/check_readiness_contract.py

    # Check specific file
    uv run python scripts/check_readiness_contract.py --scope docs/plans/workplan.md

    # Check directory
    uv run python scripts/check_readiness_contract.py --scope docs/plans/

Exit Codes:
    0: Compliant (no unqualified readiness claims found)
    1: Violations found (readiness claims without capability matrices)
    2: Error (I/O failure, invalid arguments)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


def find_readiness_claims(content: str, filepath: Path) -> List[Tuple[int, str]]:
    """Find lines containing unqualified readiness language.

    Returns list of (line_number, line_content) tuples.
    """
    claims = []
    readiness_patterns = [
        r"\b(ready|complete)\b(?!\s*—)",  # "ready" or "complete" not followed by em-dash
        r"\bAll tests pass\b",
        r"\b(done|finished)\b(?!\s*(—|:))",
    ]

    lines = content.split("\n")
    in_code_block = False

    for i, line in enumerate(lines, start=1):
        stripped = line.lstrip()

        # Track fenced code blocks (e.g., ```python ... ```). Ignore all lines inside.
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        # Skip any content that is inside a fenced code block.
        if in_code_block:
            continue

        # Skip lines that start with inline/pseudo-code backticks.
        if stripped.startswith("`"):
            continue

        for pattern in readiness_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                claims.append((i, line.strip()))
                break

    return claims


def has_capability_matrix(content: str) -> bool:
    """Check if content contains a capability matrix or scoped readiness statement."""
    # Look for capability matrix patterns
    matrix_patterns = [
        r"capability\s+matrix",
        r"✅.*✅",  # Multiple checkmarks suggesting a matrix
        r"\|\s*Capability\s*\|",  # Table header with "Capability"
        r"Retrieval.*Generation.*E2E",  # Common capability dimensions
        r"ready\s*—\s*capability",  # Properly scoped: "ready — capability..."
    ]

    for pattern in matrix_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True

    return False


def check_file(filepath: Path) -> List[str]:
    """Check a single file for readiness contract violations.

    Returns list of violation messages.
    """
    violations = []

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        raise

    # Find readiness claims
    claims = find_readiness_claims(content, filepath)

    if claims and not has_capability_matrix(content):
        violations.append(f"{filepath}: Found readiness claim(s) without capability matrix:")
        for line_num, line_content in claims:
            violations.append(f"  Line {line_num}: {line_content}")

    return violations


def check_scope(scope_path: Path) -> List[str]:
    """Check all markdown files in scope for violations."""
    violations = []

    if scope_path.is_file():
        if scope_path.suffix in [".md", ".txt"]:
            violations.extend(check_file(scope_path))
    elif scope_path.is_dir():
        for md_file in scope_path.rglob("*.md"):
            # Skip .cache and site directories
            if ".cache" in md_file.parts or "site" in md_file.parts:
                continue
            violations.extend(check_file(md_file))
    else:
        violations.append(f"Error: {scope_path} is not a file or directory")

    return violations


def main():
    parser = argparse.ArgumentParser(description="Check readiness claims are scoped with capability matrices")
    parser.add_argument(
        "--scope", type=Path, default=Path.cwd(), help="File or directory to check (default: current directory)"
    )

    args = parser.parse_args()

    if not args.scope.exists():
        print(f"Error: {args.scope} does not exist", file=sys.stderr)
        sys.exit(2)

    violations = check_scope(args.scope)

    if violations:
        print("Readiness contract violations found:\n")
        for violation in violations:
            print(violation)
        sys.exit(1)
    else:
        print("✓ All readiness claims properly scoped with capability matrices")
        sys.exit(0)


if __name__ == "__main__":
    main()
