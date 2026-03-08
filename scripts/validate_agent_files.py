"""scripts/validate_agent_files.py

Programmatic encoding-fidelity gate for agent files — equivalent to
validate_synthesis.py but for `.agent.md` files in `.github/agents/`.

Purpose:
    Enforce a minimum structural bar on agent files to prevent encoding drift
    in the MANIFESTO → AGENTS.md → agent files → session prompts chain.

Checks:
    1. Valid YAML frontmatter with required fields: ``name``, ``description``.
    2. Required section headings present (fuzzy keyword matching):
       - Endogenous Sources section (confirms the agent reads before acting)
       - Action section (Workflow, Checklist, Conventions, or equivalent)
       - Quality-gate section (Completion Criteria or Guardrails)
    3. At least one back-reference to MANIFESTO.md or AGENTS.md (cross-reference
       density ≥ 1).  Low density signals likely encoding drift.
    4. No heredoc-based file writes (``cat >> ... << 'EOF'`` patterns), which
       silently corrupt Markdown content containing backticks.

Inputs:
    [file ...]    One or more .agent.md files to validate.  (positional, optional)
    --all         Scan every *.agent.md in .github/agents/ (excluding AGENTS.md
                  and README.md).
    --strict      Reserved for future use — currently a no-op flag.

Outputs:
    stdout:  Human-readable pass/fail summary with specific gap list per file.
    stderr:  Nothing (all output goes to stdout for easy capture).

Exit codes:
    0  All checks passed.
    1  One or more checks failed — specific gap(s) reported to stdout.

Usage examples:
    # Validate a single agent file
    uv run python scripts/validate_agent_files.py .github/agents/executive-orchestrator.agent.md

    # Validate all agent files in .github/agents/
    uv run python scripts/validate_agent_files.py --all

    # Integrate into CI (non-zero exit blocks the job)
    for f in .github/agents/*.agent.md; do
        uv run python scripts/validate_agent_files.py "$f"
    done
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AGENTS_DIR = Path(".github/agents")

# YAML frontmatter fields that must be present and non-empty in every agent file.
REQUIRED_FRONTMATTER: list[str] = ["name", "description"]

# Required section categories.  Each entry is (human label, [keywords]).
# A section passes if any heading contains any of its keywords (case-insensitive).
REQUIRED_SECTIONS: list[tuple[str, list[str]]] = [
    ("Endogenous Sources", ["endogenous", "read before acting"]),
    (
        "Action section (Workflow/Checklist/Conventions/Scope/Methodology)",
        ["workflow", "checklist", "conventions", "playbook", "scope", "methodology"],
    ),
    ("Quality-gate section (Completion Criteria or Guardrails)", ["completion criteria", "guardrails"]),
]

# Negation words that indicate a heredoc pattern is being *prohibited*, not instructed.
_HEREDOC_NEGATIONS = frozenset(["never", "avoid", "don't", "dont", "do not", "wrong", "prohibited", "not use"])

# Regex matching the core heredoc cat-append pattern.
_HEREDOC_PATTERN = re.compile(r"cat\s*>>?\s*\S+\s*<<\s*['\"]?EOF", re.IGNORECASE)

# Pattern for MANIFESTO.md or AGENTS.md cross-references.
_CROSSREF_RE = re.compile(r"MANIFESTO\.md|AGENTS\.md")

# Frontmatter block pattern.
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def parse_frontmatter(text: str) -> dict[str, str]:
    """Return a flat dict of YAML frontmatter key → raw string value."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fm: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.strip().startswith("-"):
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm


def extract_headings(text: str) -> list[str]:
    """Return all Markdown H2 headings (## ...) from the document body."""
    body_start = 0
    fm_match = _FRONTMATTER_RE.match(text)
    if fm_match:
        body_start = fm_match.end()
    body = text[body_start:]
    return [line.rstrip() for line in body.splitlines() if line.startswith("## ")]


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------


def validate(file_path: Path) -> tuple[bool, list[str]]:
    """Validate *file_path*. Returns (passed, list_of_failure_messages)."""
    failures: list[str] = []

    # --- Check 0: file exists ---
    if not file_path.exists():
        return False, [f"File not found: {file_path}"]
    if not file_path.is_file():
        return False, [f"Path is not a file: {file_path}"]

    text = file_path.read_text(encoding="utf-8")

    # --- Check 1: YAML frontmatter ---
    fm = parse_frontmatter(text)
    if not fm:
        failures.append("No YAML frontmatter found (expected --- block at top of file)")
    else:
        for key in REQUIRED_FRONTMATTER:
            if not fm.get(key):
                failures.append(f"Missing or empty frontmatter field: '{key}'")

    # --- Check 2: required sections ---
    headings_lower = [h.lower() for h in extract_headings(text)]
    for section_label, keywords in REQUIRED_SECTIONS:
        matched = any(kw in h for kw in keywords for h in headings_lower)
        if not matched:
            failures.append(
                f"Missing required section '{section_label}' (expected a heading matching one of: {keywords})"
            )

    # --- Check 3: cross-reference density ---
    if not _CROSSREF_RE.search(text):
        failures.append(
            "Cross-reference density too low: no back-reference to MANIFESTO.md or AGENTS.md found "
            "(add at least one link to maintain encoding fidelity)"
        )

    # --- Check 4: no heredoc file writes (negation-aware) ---
    # A line is only flagged if the cat >> pattern appears WITHOUT a clear
    # negation marker on the same line (e.g. guardrail warnings are not flagged).
    for line in text.splitlines():
        if _HEREDOC_PATTERN.search(line):
            lower = line.lower()
            if not any(neg in lower for neg in _HEREDOC_NEGATIONS):
                failures.append(
                    "Heredoc file write detected (cat >> ... << 'EOF' pattern) outside a negation context — "
                    "use create_file / replace_string_in_file built-in tools instead "
                    "(heredocs silently corrupt Markdown containing backticks)"
                )
                break

    passed = len(failures) == 0
    return passed, failures


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate agent files for encoding fidelity.",
        epilog="Exit 0 = all pass. Exit 1 = one or more checks failed.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="file",
        help="One or more .agent.md files to validate.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="scan_all",
        help=f"Scan every *.agent.md in {AGENTS_DIR}/ (excluding AGENTS.md and README.md).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Reserved for future use.",
    )
    args = parser.parse_args()

    targets: list[Path] = []

    if args.scan_all:
        targets = [p for p in sorted(AGENTS_DIR.glob("*.agent.md"))]
    elif args.files:
        targets = [Path(f) for f in args.files]
    else:
        parser.print_help()
        sys.exit(0)

    if not targets:
        print(f"No agent files found in {AGENTS_DIR}/ — nothing to validate.")
        sys.exit(0)

    overall_pass = True
    failed_count = 0
    for file_path in targets:
        passed, failures = validate(file_path)
        if passed:
            print(f"PASS  {file_path}")
        else:
            overall_pass = False
            failed_count += 1
            print(f"FAIL  {file_path}")
            for msg in failures:
                print(f"      • {msg}")

    print()
    if overall_pass:
        print(f"All {len(targets)} agent file(s) passed.")
    else:
        print(f"{failed_count} of {len(targets)} agent file(s) failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
