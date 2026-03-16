"""scripts/validate_adr.py

Validates Architecture Decision Record (ADR) files in docs/decisions/.

Purpose:
    Enforce a consistent structure for ADR files: YAML frontmatter with required
    metadata fields, required section headings, and minimum body length.
    Designed for pre-commit pass_filenames: true (accepts nargs='+').

Inputs:
    files: One or more paths to ADR Markdown files.

Outputs:
    stdout: Per-file PASS/FAIL report with specific error messages.
    Exit 0 if all files pass, exit 1 if any file fails.

Exit codes:
    0  All files passed validation.
    1  One or more files failed validation.

Usage examples:
    # Validate a single ADR
    uv run python scripts/validate_adr.py docs/decisions/ADR-001-uv-package-manager.md

    # Validate all ADRs
    uv run python scripts/validate_adr.py docs/decisions/ADR-*.md

    # Used by pre-commit (pass_filenames: true)
    uv run python scripts/validate_adr.py docs/decisions/ADR-003-xml-hybrid-agent-format.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

import yaml

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------

REQUIRED_FRONTMATTER_FIELDS: list[str] = ["status", "date", "deciders"]
MIN_BODY_WORDS: int = 200

# Each section spec: name (for error messages), patterns (regex alternatives
# matched case-insensitively against heading text), description (human label).
REQUIRED_SECTIONS: list[dict] = [
    {
        "name": "Context",
        "patterns": [r"context"],
        "description": "Context and Problem Statement (or 'Context')",
    },
    {
        "name": "Decision Drivers",
        "patterns": [r"driver"],
        "description": "Decision Drivers (or 'Drivers')",
    },
    {
        "name": "Considered Options",
        "patterns": [r"option", r"alternative"],
        "description": "Considered Options (or 'Options' or 'Alternatives')",
    },
    {
        "name": "Decision Outcome",
        "patterns": [r"outcome", r"^decision$"],
        "description": "Decision Outcome (or exactly 'Decision')",
    },
    {
        "name": "Consequences",
        "patterns": [r"consequence", r"pros and con", r"consideration"],
        "description": "Consequences (or 'Pros and Cons of the Options')",
    },
]

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def parse_frontmatter(content: str) -> tuple[Optional[dict], str]:
    """Parse YAML frontmatter from content.

    Returns (frontmatter_dict, body_text).  If no valid frontmatter is found,
    returns (None, full_content).
    """
    if not content.startswith("---"):
        return None, content
    # Find the closing ---
    end = content.find("\n---", 3)
    if end == -1:
        return None, content
    fm_text = content[3:end].strip()
    body = content[end + 4 :].strip()
    try:
        fm = yaml.safe_load(fm_text)
        if not isinstance(fm, dict):
            return None, content
        return fm, body
    except yaml.YAMLError:
        return None, content


def get_section_headings(content: str) -> list[str]:
    """Return all ## / ### heading texts in *content* as lowercase stripped strings."""
    headings: list[str] = []
    for line in content.splitlines():
        if re.match(r"^#{2,}\s", line):
            text = re.sub(r"^#+\s+", "", line).strip().lower()
            headings.append(text)
    return headings


def section_present(headings: list[str], patterns: list[str]) -> bool:
    """Return True if any heading matches any of the given regex patterns."""
    for heading in headings:
        for pattern in patterns:
            if re.search(pattern, heading, re.IGNORECASE):
                return True
    return False


def count_body_words(text: str) -> int:
    """Return the word count of *text*."""
    return len(text.split())


# ---------------------------------------------------------------------------
# Per-file validation
# ---------------------------------------------------------------------------


def validate_file(filepath: Path) -> list[str]:
    """Validate one ADR file.

    Returns a list of error strings.  An empty list means the file passed.
    """
    errors: list[str] = []

    try:
        content = filepath.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"Cannot read file: {exc}"]

    # -- 1. YAML frontmatter -------------------------------------------------
    frontmatter, body = parse_frontmatter(content)
    if frontmatter is None:
        errors.append("MISSING: YAML frontmatter — expected '---' ... '---' block at top of file")
        body = content  # fall back to full content for remaining checks
    else:
        fm_lower = {k.lower(): v for k, v in frontmatter.items()}
        for field in REQUIRED_FRONTMATTER_FIELDS:
            if field not in fm_lower or fm_lower[field] is None or fm_lower[field] == "":
                errors.append(f"MISSING frontmatter field: '{field}'")

    # -- 2. Required section headings ----------------------------------------
    headings = get_section_headings(content)
    for section in REQUIRED_SECTIONS:
        if not section_present(headings, section["patterns"]):
            errors.append(f"MISSING section: {section['description']}")

    # -- 3. Minimum body length ----------------------------------------------
    word_count = count_body_words(body)
    if word_count < MIN_BODY_WORDS:
        errors.append(f"BODY TOO SHORT: {word_count} words (minimum: {MIN_BODY_WORDS})")

    return errors


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate Architecture Decision Record (ADR) files.",
        epilog="Exit 0 = all pass. Exit 1 = at least one failure.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="ADR file path(s) to validate.",
    )
    args = parser.parse_args()

    all_pass = True
    for file_path in args.files:
        filepath = Path(file_path)
        errors = validate_file(filepath)
        if errors:
            all_pass = False
            print(f"FAIL: {file_path}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"PASS: {file_path}")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
