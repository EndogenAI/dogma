"""scripts/validate_session.py

Post-commit scratchpad audit validator for session files.

Purpose:
    Enforce a minimum structural bar on session scratchpad files (.tmp/*/*.md)
    to prevent encoding drift during multi-phase sessions. Validates that
    critical session metadata and checkpoint records are present.

Checks (7-point audit):
    1. ## Session Start present (mandatory session initialization).
    2. ## Session Start contains governing axiom citation (checks for "Governing axiom:" pattern).
    3. ## Session Start contains endogenous source citation (checks for MANIFESTO.md, AGENTS.md,
       docs/, or scripts/ references).
    4. ## Orchestration Plan present (tracks phases scheduled for this session).
    5. Phase records tracked (all planned phases have ### Phase N headings).
    6. Pre-Compact Checkpoint present (mandatory pre-compaction marker).
    7. ## Session Summary present (mandatory session close marker).

Inputs:
    [file ...]  One or more session .md files to audit (positional, optional).
    --all       Scan all session files in .tmp/*/*.md.
    --branch    Only scan files on the current git branch.

Outputs:
    stdout:  Human-readable pass/fail summary with specific gap list per file.

Exit codes:
    0  All checks passed.
    1  One or more structural checks failed.
    2  Encoding drift detected (e.g., axiom not explicitly cited, source not linked).

Usage examples:
    # Validate a single session file
    uv run python scripts/validate_session.py .tmp/feat-branch/2026-03-11.md

    # Validate all session files
    uv run python scripts/validate_session.py --all

    # Validate only current branch
    uv run python scripts/validate_session.py --branch
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def validate_session_file(file_path: Path) -> tuple[int, list[str]]:
    """
    Validate a session file.

    Returns:
        (exit_code, list_of_messages)
        exit_code:
            0 = all checks passed
            1 = structural checks failed (missing sections, wrong format)
            2 = encoding drift detected (axiom/source not cited)
    """
    messages: list[str] = []
    structuralFailures = []
    encodingDrift = []

    if not file_path.exists():
        return 1, [f"File not found: {file_path}"]

    text = file_path.read_text(encoding="utf-8")

    # --- Check 1: ## Session Start present ---
    if "## Session Start" not in text:
        structuralFailures.append("Missing '## Session Start' section")

    # --- Check 2: governing axiom citation in ## Session Start ---
    # Extract content between "## Session Start" and next "##" heading
    session_match = re.search(r"## Session Start(.+?)(?=\n##|\Z)", text, re.DOTALL)
    session_body = session_match.group(1) if session_match else ""

    if session_body:
        # Check for axiom citation (accepts both ** bold ** and plain formats)
        if not re.search(r"\*\*Governing axiom\*\*:|Governing axiom:", session_body, re.IGNORECASE):
            encodingDrift.append(
                "## Session Start missing explicit 'Governing axiom:' citation "
                "(required for encoding checkpoint; see AGENTS.md §Context-Sensitive-Amplification)"
            )
    else:
        structuralFailures.append("## Session Start section is empty or malformed")

    # --- Check 3: endogenous source citation in ## Session Start ---
    if session_body:
        endogenous_sources = (
            "MANIFESTO.md",
            "AGENTS.md",
            "docs/",
            "scripts/",
            ".github/",
        )
        if not any(source in session_body for source in endogenous_sources):
            encodingDrift.append(
                f"## Session Start missing endogenous source citation "
                f"(expected reference to one of: {', '.join(endogenous_sources)})"
            )

    # --- Check 4: ## Orchestration Plan present ---
    if "## Orchestration Plan" not in text:
        structuralFailures.append("Missing '## Orchestration Plan' section")

    # --- Check 5: Phase records tracked (Phase N headings) ---
    phase_pattern = re.compile(r"^###\s+Phase\s+\d+", re.MULTILINE)
    phases = phase_pattern.findall(text)
    if not phases:
        structuralFailures.append("No phase records found (expected ### Phase N headings)")

    # --- Check 6: ## Pre-Compact Checkpoint present ---
    if "## Pre-Compact Checkpoint" not in text and "## Context Window Checkpoint" not in text:
        structuralFailures.append("Missing '## Pre-Compact Checkpoint' section (required before compaction)")

    # --- Check 7: ## Session Summary present ---
    if "## Session Summary" not in text:
        structuralFailures.append("Missing '## Session Summary' section (required at session close)")

    # Compile results
    if structuralFailures:
        messages.extend([f"  ✗ {msg}" for msg in structuralFailures])
    if encodingDrift:
        messages.extend([f"  ⚠ {msg}" for msg in encodingDrift])

    # Determine exit code
    exit_code = 0
    if structuralFailures:
        exit_code = 1
    elif encodingDrift:
        exit_code = 2

    return exit_code, messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Post-commit scratchpad audit validator for session files")
    parser.add_argument("files", nargs="*", help="Session .md files to validate (optional if --all is used)")
    parser.add_argument("--all", action="store_true", help="Scan all session files in .tmp/*/*.md")
    parser.add_argument("--branch", action="store_true", help="Only scan current branch")

    args = parser.parse_args()

    files_to_check: list[Path] = []

    if args.all:
        tmp_dir = Path(".tmp")
        if tmp_dir.exists():
            files_to_check = sorted(tmp_dir.glob("*/*.md"))
    elif args.branch:
        # Get current branch name and scan only that branch's .tmp/ folder
        try:
            import subprocess

            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
            branch_dir = Path(f".tmp/{branch}")
            if branch_dir.exists():
                files_to_check = sorted(branch_dir.glob("*.md"))
        except Exception as e:
            print(f"Error getting current branch: {e}", file=sys.stderr)
            return 1
    else:
        # Validate specific files passed as arguments
        files_to_check = [Path(f) for f in args.files]

    if not files_to_check:
        print("No session files found to validate", file=sys.stderr)
        return 1

    overall_exit_code = 0
    for file_path in files_to_check:
        exit_code, messages = validate_session_file(file_path)
        if exit_code > 0:
            overall_exit_code = max(overall_exit_code, exit_code)
            print(f"{file_path}:")
            for msg in messages:
                print(msg)
        else:
            print(f"{file_path}: ✓ OK")

    return overall_exit_code


if __name__ == "__main__":
    sys.exit(main())
