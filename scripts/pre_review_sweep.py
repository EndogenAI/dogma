"""scripts/pre_review_sweep.py

Pre-review sweep: scans changed files for known bad patterns before CI.

Purpose:
    Catch common antipatterns before they reach CI or code review. Extracts
    known guardrails from AGENTS.md and enforces them programmatically
    on modified files.

Patterns checked:
    1. Heredoc file writes (cat >> file << 'EOF')
    2. Terminal file I/O redirection (> file, >> file, | tee file)
    3. Fetch-before-check guardrail label reversals
    4. Direct Python file operations without File tools

Inputs:
    --changed-files <file>  File containing list of changed paths (one per line)
    --branch <ref>          Git ref for diff baseline (default: main)
    --fix                   If set, report fixes rather than just failures

Outputs:
    stdout: Human-readable pattern report with file:line:pattern

Exit codes:
    0  No patterns found.
    1  Pattern(s) found.

Usage examples:
    git diff --name-only main > /tmp/changed.txt
    uv run python scripts/pre_review_sweep.py --changed-files /tmp/changed.txt

    uv run python scripts/pre_review_sweep.py --branch origin/main
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Known bad patterns (pattern_name, regex, file_extensions)
BAD_PATTERNS = [
    (
        "heredoc-write",
        re.compile(r"cat\s*>>?\s*\S+\s*<<\s*['\"]?EOF", re.IGNORECASE),
        [".py", ".sh"],
    ),
    (
        "terminal-redirection",
        re.compile(r"[|>]\s*(tee|cat)\s+\S+|\s*>\s*\S+|\s*>>\s*\S+"),
        [".sh", ".py"],
    ),
    (
        "fetch-before-check-reversed",
        re.compile(r"fetch.?before.?check", re.IGNORECASE),
        [".md", ".py"],
    ),
    (
        "python-file-open-write",
        re.compile(r"open\(['\"].*?['\"],\s*['\"]w"),
        [".py"],
    ),
]


def scan_file(file_path: Path) -> list[tuple[str, int, str]]:
    """
    Scan a single file for bad patterns.

    Returns:
        List of (pattern_name, line_number, line_content) tuples
    """
    findings: list[tuple[str, int, str]] = []

    if not file_path.exists():
        return findings

    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return findings

    suffix = file_path.suffix.lower()
    for pattern_name, regex, extensions in BAD_PATTERNS:
        if suffix not in extensions:
            continue

        for line_num, line in enumerate(text.splitlines(), 1):
            if regex.search(line):
                # Negation check: if line contains guardrail language, allow the pattern
                negation_words = {"never", "avoid", "do not", "dont", "don't", "prohibited"}
                line_lower = line.lower()
                if not any(neg in line_lower for neg in negation_words):
                    findings.append((pattern_name, line_num, line.strip()))

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pre-review sweep for known bad patterns"
    )
    parser.add_argument(
        "--changed-files",
        type=Path,
        help="File containing list of changed paths (one per line)",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Git ref for diff baseline (default: main)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Report fixes rather than just failures",
    )

    args = parser.parse_args(argv)

    files_to_check: list[Path] = []

    if args.changed_files:
        # Read list from file
        try:
            with open(args.changed_files, "r", encoding="utf-8") as f:
                files_to_check = [Path(line.strip()) for line in f if line.strip()]
        except OSError as e:
            print(f"ERROR: Cannot read changed files list: {e}", file=sys.stderr)
            return 1
    else:
        # Get changed files via git diff
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", args.branch],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                print(f"ERROR: git diff failed: {result.stderr}", file=sys.stderr)
                return 1
            files_to_check = [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
        except FileNotFoundError:
            print("ERROR: git not found", file=sys.stderr)
            return 1

    if not files_to_check:
        print("No files to scan")
        return 0

    overall_exit_code = 0
    for file_path in files_to_check:
        findings = scan_file(file_path)
        if findings:
            overall_exit_code = 1
            print(f"{file_path}:")
            for pattern_name, line_num, line_content in findings:
                print(f"  {line_num}: [{pattern_name}] {line_content}")

    return overall_exit_code


if __name__ == "__main__":
    sys.exit(main())
