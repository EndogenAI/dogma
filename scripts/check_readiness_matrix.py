"""Check that files with readiness claims include a capability matrix.

Purpose:
    Validate that any file containing readiness/ready/complete claims includes
    a capability matrix. Implements AGENTS.md § Readiness Language Guard and
    readiness-false-positive-analysis.md Recommendation 2.

Inputs:
    files   : list of file paths to check (positional args)
    --fix   : no-op flag for pre-commit compatibility (reserved)
    --strict: fail if any dimension has status "partial" (default: only fail on missing)

Outputs:
    Exit 0  : no violations found
    Exit 1  : one or more files contain readiness claims without capability matrix
    Stdout  : list of violations with file path and line number

Usage:
    uv run python scripts/check_readiness_matrix.py docs/plans/*.md
    uv run python scripts/check_readiness_matrix.py --strict docs/plans/foo.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Patterns that indicate a readiness claim.
# Negations ("not ready", "not complete") are excluded via the negative-lookbehind.
READINESS_PATTERNS = [
    re.compile(r"(?<!\bnot\s)\bready\b", re.IGNORECASE),
    re.compile(r"(?<!\bnot\s)\bcomplete\b", re.IGNORECASE),
    re.compile(r"(?<!\bnot\s)\bdone\b", re.IGNORECASE),
]

# Negation prefix — lines containing these are skipped
NEGATION_RE = re.compile(r"\bnot\s+(ready|complete|done)\b", re.IGNORECASE)

# Patterns indicating a capability matrix is present
MATRIX_PATTERNS = [
    re.compile(r"capability_matrix:", re.IGNORECASE),
    re.compile(r"\|\s*Retrieval\s*\|", re.IGNORECASE),
    re.compile(r"\|\s*E2E\s*\|", re.IGNORECASE),
    re.compile(r"\|\s*End.to.End\s*\|", re.IGNORECASE),
    # Inline claim format: "capability matrix: Retrieval ✅"
    re.compile(r"capability matrix\s*:", re.IGNORECASE),
    # Markdown heading: "## Capability Matrix"
    re.compile(r"##\s*Capability Matrix", re.IGNORECASE),
    # Table with "Retrieval" in first column (wider match)
    re.compile(r"\|\s*Retrieval\s*(\([^)]*\))?\s*\|", re.IGNORECASE),
]

PARTIAL_RE = re.compile(r"\bpartial\b", re.IGNORECASE)


def _has_matrix(text: str) -> bool:
    return any(p.search(text) for p in MATRIX_PATTERNS)


def _has_partial_dimension(text: str) -> bool:
    for line in text.splitlines():
        # Only inspect lines that look like matrix entries
        if any(p.search(line) for p in MATRIX_PATTERNS):
            if PARTIAL_RE.search(line):
                return True
    # Also catch YAML-style entries: "  retrieval: partial"
    if re.search(r":\s*['\"]?partial['\"]?\b", text, re.IGNORECASE):
        return True
    return False


def _find_readiness_claim_line(lines: list[str]) -> int | None:
    """Return the 1-based line number of the first readiness claim, or None."""
    for i, line in enumerate(lines, start=1):
        if NEGATION_RE.search(line):
            continue
        if any(p.search(line) for p in READINESS_PATTERNS):
            return i
    return None


def check_file(path: Path, strict: bool) -> list[str]:
    """Return a list of violation strings for the given file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"{path}: could not read file — {exc}"]

    lines = text.splitlines()
    claim_line = _find_readiness_claim_line(lines)
    if claim_line is None:
        return []

    violations = []

    if not _has_matrix(text):
        violations.append(f"{path}:{claim_line}: unscoped readiness claim — capability matrix missing")
    elif strict and _has_partial_dimension(text):
        violations.append(f"{path}:{claim_line}: readiness claim with partial capability dimension (--strict)")

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check readiness claims have an accompanying capability matrix.")
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to check",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="No-op; reserved for pre-commit compatibility",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any capability dimension is 'partial'",
    )
    args = parser.parse_args(argv)

    if not args.files:
        parser.print_usage()
        return 0

    all_violations: list[str] = []
    for f in args.files:
        path = Path(f)
        if not path.exists():
            print(f"warning: {path} does not exist — skipped", file=sys.stderr)
            continue
        all_violations.extend(check_file(path, strict=args.strict))

    for v in all_violations:
        print(v)

    return 1 if all_violations else 0


if __name__ == "__main__":
    sys.exit(main())
