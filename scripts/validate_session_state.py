"""scripts/validate_session_state.py

Validator for Phase/gate transitions in scratchpad session files.

Purpose:
    Enforce proper sequencing of phase execution and review gates. Detects
    phase skipping, missing review gates between domains, and FSM violations.

Checks:
    1. All phases follow numerically (no skipping: 1→2→3, not 1→3).
    2. Each Phase N is followed by a Review gate before proceeding to next domain.
    3. No duplicate phases.
    4. Session contains at least Phase 1 (session started).

Inputs:
    [file ...]         Path to session .md file (positional, optional).

Outputs:
    stdout: Human-readable pass/fail summary.

Exit codes:
    0  All checks passed.
    1  One or more checks failed.

Usage examples:
    uv run python scripts/validate_session_state.py .tmp/branch/2026-03-11.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def validate(file_path: Path) -> tuple[bool, list[str]]:
    """
    Validate session state FSM (phase sequencing and review gates).

    Returns:
        (passed, list_of_failure_messages)
    """
    failures: list[str] = []

    if not file_path.exists():
        return False, [f"File not found: {file_path}"]

    text = file_path.read_text(encoding="utf-8")

    # --- Check 1: Extract all phase numbers ---
    phase_pattern = re.compile(r"^###\s+Phase\s+(\d+)", re.MULTILINE)
    # Domain-only phases: exclude headings that contain "Review" after the number.
    domain_pattern = re.compile(r"^###\s+Phase\s+(\d+)(?!.*\bReview\b)", re.MULTILINE)
    domain_phase_nums = [int(m) for m in domain_pattern.findall(text)]
    # Check for duplicates among domain phases before de-duplicating
    seen: set[int] = set()
    for num in domain_phase_nums:
        if num in seen:
            failures.append(f"Duplicate Phase {num} heading found")
        seen.add(num)
    phases = sorted(set(int(m) for m in phase_pattern.findall(text)))

    if not phases:
        failures.append("No phases found (expected ### Phase N headings)")
        return len(failures) == 0, failures

    # --- Check 2: Phases must start at 1 ---
    if phases[0] != 1:
        failures.append(f"First phase must be Phase 1, not Phase {phases[0]}")

    # --- Check 3: Phases must be sequential (no skipping) ---
    for i, phase_num in enumerate(phases, 1):
        if phase_num != i:
            failures.append(f"Phase sequence broken at position {i}: expected Phase {i}, got Phase {phase_num}")

    # --- Check 4: Review gates between domains ---
    # Each phase should have a "## Phase N Review" heading or similar
    for phase_num in phases:
        review_pattern = re.compile(rf"^###\s+Phase\s+{phase_num}\s+.*?Review", re.MULTILINE | re.IGNORECASE)
        if not review_pattern.search(text):
            failures.append(
                f"Missing review gate marker for Phase {phase_num} "
                f"(expected '### Phase {phase_num} — ... Review' or similar)"
            )

    return len(failures) == 0, failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Phase/gate transitions in session files")
    parser.add_argument(
        "files",
        nargs="*",
        help="Path to session .md file(s) to validate",
    )

    args = parser.parse_args(argv)

    if not args.files:
        print("Please provide at least one session file to validate", file=sys.stderr)
        return 1

    files_to_check = [Path(f) for f in args.files]
    overall_exit_code = 0

    for file_path in files_to_check:
        passed, messages = validate(file_path)
        if not passed:
            overall_exit_code = 1
            print(f"{file_path}:")
            for msg in messages:
                print(f"  ✗ {msg}")
        else:
            print(f"{file_path}: ✓ OK")

    return overall_exit_code


if __name__ == "__main__":
    sys.exit(main())
