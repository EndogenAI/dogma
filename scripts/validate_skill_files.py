"""scripts/validate_skill_files.py

Programmatic encoding-fidelity gate for skill files — equivalent to
validate_agent_files.py but for `.github/skills/*/SKILL.md` files.

Purpose:
    Enforce a minimum structural bar on skill files to prevent encoding drift
    in the MANIFESTO → AGENTS.md → skill files → session procedures chain.

Checks (5-point gate):
    1. Valid YAML frontmatter with required fields: ``name``, ``description``.
    2. Required section headings present (fuzzy keyword matching):
       - Governing Axiom section (documents which axiom/principle governs the skill)
       - Workflow section (Workflow, Procedure, Steps, or equivalent)
       - Output section (documents what the skill produces)
    3. At least one back-reference to MANIFESTO.md or AGENTS.md (cross-reference
       density ≥ 1). Low density signals likely encoding drift.
    4. No heredoc-based file writes (``cat >> ... << 'EOF'`` patterns), which
       silently corrupt Markdown content containing backticks.
    5. Inverse scope checks: file explicitly states what the skill does NOT
       handle (negation statements for scope boundaries). Typically uses "DO NOT",
       "AVOID", "NOT FOR" patterns in the frontmatter description or a dedicated section.

Inputs:
    [file ...]    One or more .md files to validate (positional, optional).
    --all         Scan every SKILL.md in .github/skills/*/SKILL.md.
    --check       If provided, exit cleanly with exit code 0 even if checks fail.
                  Useful for pre-flight validation without blocking. Default: fail on errors.

Outputs:
    stdout:  Human-readable pass/fail summary with specific gap list per file.

Exit codes:
    0  All checks passed.
    1  One or more checks failed — specific gap(s) reported to stdout.

Usage examples:
    # Validate a single skill file
    uv run python scripts/validate_skill_files.py .github/skills/delegation-routing/SKILL.md

    # Validate all skill files
    uv run python scripts/validate_skill_files.py --all

    # Check-only mode (do not block CI)
    uv run python scripts/validate_skill_files.py --check --all
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SKILLS_DIR = Path(".github/skills")

# YAML frontmatter fields that must be present and non-empty in every skill file.
REQUIRED_FRONTMATTER: list[str] = ["name", "description"]

# Required section categories. Each entry is (human label, [keywords]).
# A section passes if any heading contains any of its keywords (case-insensitive).
REQUIRED_SECTIONS: list[tuple[str, list[str]]] = [
    ("Governing Axiom", ["governing axiom", "governed by", "principle"]),
    (
        "Workflow section (Workflow/Procedure/Steps/Usage)",
        ["workflow", "procedure", "steps", "usage", "how to use"],
    ),
    ("Output section", ["output", "returns", "produces", "deliverable"]),
]

# Negation words that indicate a heredoc pattern is being *prohibited*, not instructed.
_HEREDOC_NEGATIONS = frozenset(["never", "avoid", "don't", "dont", "do not", "wrong", "prohibited", "not use"])

# Regex matching the core heredoc cat-append pattern.
_HEREDOC_PATTERN = re.compile(r"cat\s*>>?\s*\S+\s*<<\s*['\"]?EOF", re.IGNORECASE)

# Pattern for MANIFESTO.md or AGENTS.md cross-references.
_CROSSREF_RE = re.compile(r"MANIFESTO\.md|AGENTS\.md")

# Negation/scope boundary patterns for check 5
_SCOPE_NEGATION_RE = re.compile(r"(DO NOT|do not|AVOID|avoid|NOT FOR|not for|do not use|DON'T|don't)", re.IGNORECASE)

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
            v = val.strip()
            if len(v) >= 2 and v[0] in ('"', "'") and v[0] == v[-1]:
                v = v[1:-1]
            fm[key.strip()] = v
    return fm


def extract_headings(text: str) -> list[str]:
    """Return all Markdown H2 headings (## ...) from the document body."""
    body_start = 0
    fm_match = _FRONTMATTER_RE.match(text)
    if fm_match:
        body_start = fm_match.end()
    body = text[body_start:]
    return [line.rstrip() for line in body.splitlines() if line.startswith("## ")]


def _extract_body(text: str) -> str:
    """Return the document body after the frontmatter block."""
    fm_match = _FRONTMATTER_RE.match(text)
    return text[fm_match.end() :] if fm_match else text


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

    # --- Check 5: inverse scope checks (what skill does NOT handle) ---
    # Look for explicit negation patterns in frontmatter description or body
    frontmatter_text = fm.get("description", "")
    has_negation = _SCOPE_NEGATION_RE.search(frontmatter_text) is not None
    body_text = _extract_body(text)
    body_has_negation = _SCOPE_NEGATION_RE.search(body_text) is not None

    if not (has_negation or body_has_negation):
        failures.append(
            "Missing inverse scope statement (DO NOT, AVOID, NOT FOR, etc.) — "
            "skill should explicitly document what it does NOT do to establish clear boundaries"
        )

    return len(failures) == 0, failures


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Programmatic encoding-fidelity gate for skill files")
    parser.add_argument("files", nargs="*", help="Skill .md files to validate (optional if --all is used)")
    parser.add_argument("--all", action="store_true", help="Scan all SKILL.md files in .github/skills/*/")
    parser.add_argument(
        "--check", action="store_true", help="Check-only mode: do not block on failures (always exit 0)"
    )

    args = parser.parse_args(argv)

    files_to_check: list[Path] = []

    if args.all:
        if SKILLS_DIR.exists():
            files_to_check = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    else:
        files_to_check = [Path(f) for f in args.files]

    if not files_to_check:
        print("No skill files found to validate", file=sys.stderr)
        return 1 if not args.check else 0

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

    return 0 if args.check else overall_exit_code


if __name__ == "__main__":
    sys.exit(main())
