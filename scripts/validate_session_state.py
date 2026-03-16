"""scripts/validate_session_state.py

Validator for Phase/gate transitions in scratchpad session files, and YAML
phase-status block parser for structured session state tracking.

Purpose:
    Two modes of operation:

    1. FSM validation (default): Enforce proper sequencing of phase execution
       and review gates. Detects phase skipping, missing review gates between
       domains, and FSM violations.

    2. YAML phase-status (--yaml-state): Parse the ## Session State YAML block
       written by prune_scratchpad.py --init, validate its structure, and print
       a human-readable phase status table.

Checks (FSM mode):
    1. All phases follow numerically (no skipping: 1→2→3, not 1→3).
    2. Each Phase N is followed by a Review gate before proceeding to next domain.
    3. No duplicate phases.
    4. Session contains at least Phase 1 (session started).

YAML block schema (--yaml-state):
    branch:       string
    active_phase: string or null
    phases:       list of {name: str, status: str, commit: str}

Inputs:
    [file ...]         Path to session .md file (positional, optional).
    --yaml-state       Parse and display the ## Session State YAML block.

Outputs:
    stdout: Human-readable pass/fail summary (FSM) or phase table (--yaml-state).

Exit codes:
    0  All checks passed / YAML block valid.
    1  One or more checks failed / YAML block missing or malformed.

Usage examples:
    uv run python scripts/validate_session_state.py .tmp/branch/2026-03-11.md
    uv run python scripts/validate_session_state.py --yaml-state .tmp/branch/2026-03-16.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def extract_yaml_state_block(text: str) -> str | None:
    """
    Find and extract the YAML content inside the ## Session State fenced block.

    Looks for a pattern of the form:
        ## Session State

        ```yaml
        ...
        ```

    Returns the raw YAML content string (without the fence), or None if not found.
    """
    pattern = re.compile(
        r"^## Session State\s*\n+```yaml\n(.*?)```",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1) if match else None


def parse_yaml_block(yaml_content: str) -> tuple[dict | None, str | None]:
    """
    Parse YAML content and validate required keys.

    Expected schema:
        branch:       string
        active_phase: string or null
        phases:       list of {name, status, commit}

    Returns:
        (data_dict, error_message) — error_message is None on success.
    """
    try:
        import yaml  # type: ignore[import-untyped]

        data = yaml.safe_load(yaml_content)
    except Exception as exc:
        return None, f"YAML parse error: {exc}"

    if not isinstance(data, dict):
        return None, "Session State block must be a YAML mapping"
    for key in ("branch", "active_phase", "phases"):
        if key not in data:
            return None, f"Missing required key: {key}"
    if not isinstance(data["branch"], str) or not data["branch"]:
        return None, "'branch' must be a non-empty string"
    if data["active_phase"] is not None and not isinstance(data["active_phase"], str):
        return None, "'active_phase' must be a string or null"
    if not isinstance(data["phases"], list):
        return None, "'phases' must be a YAML list"
    for i, phase in enumerate(data["phases"]):
        if not isinstance(phase, dict):
            return None, f"phases[{i}] must be a YAML mapping"
        if "name" not in phase:
            return None, f"phases[{i}] is missing required field 'name'"

    return data, None


def display_phase_table(data: dict) -> None:
    """Print a human-readable phase status table from parsed YAML state data."""
    branch = data.get("branch") or "(unknown)"
    active_phase = data.get("active_phase")
    phases = data.get("phases", [])

    print(f"Branch: {branch}")
    print(f"Active phase: {active_phase or '(none)'}")
    print("Phases:")

    if not phases:
        print("  (none)")
        return

    for phase in phases:
        if not isinstance(phase, dict):
            continue
        name = phase.get("name", "(unnamed)")
        status = phase.get("status", "(unknown)")
        commit = phase.get("commit") or ""
        commit_str = f"  {commit}" if commit else ""
        print(f"  {name:<30} [{status}]{commit_str}")


def validate_yaml_state(file_path: Path) -> tuple[bool, str]:
    """
    Parse and validate the ## Session State YAML block in a scratchpad file.

    Returns:
        (success: bool, message: str)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    text = file_path.read_text(encoding="utf-8")
    yaml_content = extract_yaml_state_block(text)

    if yaml_content is None:
        return False, "## Session State block not found in scratchpad"

    data, error = parse_yaml_block(yaml_content)
    if error:
        return False, f"Invalid Session State block: {error}"

    display_phase_table(data)
    return True, "OK"


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
    parser.add_argument(
        "--yaml-state",
        action="store_true",
        help="Parse and display the ## Session State YAML block; exit 1 if missing or malformed",
    )

    args = parser.parse_args(argv)

    if not args.files:
        print("Please provide at least one session file to validate", file=sys.stderr)
        return 1

    files_to_check = [Path(f) for f in args.files]
    overall_exit_code = 0

    for file_path in files_to_check:
        if args.yaml_state:
            success, message = validate_yaml_state(file_path)
            if not success:
                print(f"ERROR: {message}", file=sys.stderr)
                overall_exit_code = 1
        else:
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
