"""
scripts/validate_semantic_output.py
-------------------------------------
Validates agent return tokens against a declared output format and token ceiling.

Purpose:
    Enforces the Focus-on-Descent / Compression-on-Ascent contract from AGENTS.md:
    subagent output must match the declared format (bullets, table, single-line)
    and must not exceed the declared token ceiling.

    Tokens are approximated as: ceil(word_count / 0.75) — matches GPT-style
    tokenisation closely enough for ceiling enforcement without requiring a
    tokeniser library.

Inputs:
    --format <bullets|table|single-line>  Required. Declared format.
    --ceiling <N>                         Required. Maximum token count (integer).
    text positional arg or stdin          The agent output text to validate.

Outputs:
    Prints "OK: format=<format> tokens=<n> ceiling=<N>" on success.
    Prints "FORMAT MISMATCH: ..." on format violation.
    Prints "CEILING EXCEEDED: ..." on token overflow.

Usage example:
    echo "- item one\n- item two" | uv run python scripts/validate_semantic_output.py --format bullets --ceiling 50
    uv run python scripts/validate_semantic_output.py --format single-line --ceiling 20 "Done."

Exit codes:
    0 — format matches AND token count <= ceiling
    1 — format mismatch
    2 — ceiling exceeded (format matched but too many tokens)

References:
    - AGENTS.md § Agent Communication — Focus-on-Descent / Compression-on-Ascent
"""

from __future__ import annotations

import argparse
import math
import re
import sys

# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------


def estimate_tokens(text: str) -> int:
    """Approximate token count: ceil(word_count / 0.75).

    This closely tracks GPT-4 tokenisation for English prose without
    requiring the tiktoken library.
    """
    words = len(text.split())
    return math.ceil(words / 0.75)


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------


def _is_bullets(text: str) -> bool:
    """Return True if text contains at least one bullet line.

    Accepts: - item, * item, • item
    """
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return False
    bullet_pattern = re.compile(r"^[-*•]\s+\S")
    return any(bullet_pattern.match(line) for line in lines)


def _is_table(text: str) -> bool:
    """Return True if text contains at least one Markdown table row (| ... |) and a separator row."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    table_rows = [row for row in lines if row.startswith("|") and row.endswith("|")]
    if len(table_rows) < 2:
        return False
    # Check for separator row (e.g. |---| or | :--- |)
    has_separator = any(re.match(r"^\|[ :|-]+\|$", row) for row in table_rows)
    return has_separator and len(table_rows) >= 3  # header + separator + at least one data row


def _is_single_line(text: str) -> bool:
    """Return True if text is exactly one non-empty line."""
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    return len(lines) == 1


_FORMAT_CHECKS = {
    "bullets": _is_bullets,
    "table": _is_table,
    "single-line": _is_single_line,
}


def check_format(text: str, fmt: str) -> bool:
    """Return True if *text* matches *fmt*."""
    checker = _FORMAT_CHECKS.get(fmt)
    if checker is None:
        raise ValueError(f"Unknown format: {fmt!r}. Choose: {list(_FORMAT_CHECKS)}")
    return checker(text)


# ---------------------------------------------------------------------------
# Main validation
# ---------------------------------------------------------------------------


def validate(text: str, fmt: str, ceiling: int) -> int:
    """Validate *text* against *fmt* and *ceiling*.

    Returns:
        0 on full pass, 1 on format mismatch, 2 on ceiling exceeded.
    """
    format_ok = check_format(text, fmt)
    tokens = estimate_tokens(text)

    if not format_ok:
        print(
            f"FORMAT MISMATCH: expected={fmt!r} — text does not match that format.",
            file=sys.stderr,
        )
        return 1

    if tokens > ceiling:
        print(
            f"CEILING EXCEEDED: tokens={tokens} ceiling={ceiling} format={fmt!r}",
            file=sys.stderr,
        )
        return 2

    print(f"OK: format={fmt!r} tokens={tokens} ceiling={ceiling}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate agent output against a declared format and token ceiling.")
    p.add_argument(
        "--format",
        required=True,
        choices=list(_FORMAT_CHECKS),
        dest="fmt",
        help="Expected output format.",
    )
    p.add_argument(
        "--ceiling",
        required=True,
        type=int,
        help="Maximum token count (approximate).",
    )
    p.add_argument(
        "text",
        nargs="?",
        default=None,
        help="Text to validate. Reads from stdin if omitted.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.text is not None:
        text = args.text
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("ERROR: no input text provided.", file=sys.stderr)
        return 1

    return validate(text, args.fmt, args.ceiling)


if __name__ == "__main__":
    sys.exit(main())
