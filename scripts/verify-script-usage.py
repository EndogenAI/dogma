"""verify-script-usage.py — Pre-commit hook that flags CLI invocations in agent/skill
markdown files without adjacent --help verification.

Inputs: one or more .md file paths (passed by pre-commit as positional args)
Outputs: exit 0 if clean (or advisory mode), exit 1 if violations found + --strict
Usage:
    uv run python scripts/verify-script-usage.py .github/agents/my-agent.agent.md
    uv run python scripts/verify-script-usage.py --strict .github/agents/my-agent.agent.md
    uv run python scripts/verify-script-usage.py --help
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Skip these directories when scanning
_SKIP_DIRS = frozenset(["vendor", "site"])

# Patterns that indicate a script invocation inside a fenced block
_SCRIPT_INVOCATION_RE = re.compile(r"(?:uv run python scripts/|python scripts/|python3 scripts/)\S+")

# Fenced code block start (```bash, ```shell, ``` with no language)
_FENCE_START_RE = re.compile(r"^```(bash|shell|sh)?\s*$")
_FENCE_END_RE = re.compile(r"^```\s*$")


def _should_skip(path: Path) -> bool:
    return any(part in _SKIP_DIRS for part in path.parts)


def _has_help_flag(text: str) -> bool:
    return "--help" in text


def _find_violations(filepath: str, lines: list[str]) -> list[tuple[int, str]]:
    """Return list of (line_number, message) for each violation found."""
    text = "".join(lines)
    if _has_help_flag(text):
        return []

    violations: list[tuple[int, str]] = []
    in_fence = False
    fence_has_invocation = False
    fence_start_line = 0

    for i, line in enumerate(lines, start=1):
        if not in_fence:
            if _FENCE_START_RE.match(line):
                in_fence = True
                fence_has_invocation = False
                fence_start_line = i
        else:
            if _FENCE_END_RE.match(line):
                in_fence = False
                fence_has_invocation = False
            elif _SCRIPT_INVOCATION_RE.search(line):
                fence_has_invocation = True
                if fence_has_invocation:
                    violations.append(
                        (
                            fence_start_line,
                            f"WARNING: {filepath}:{fence_start_line}: CLI invocation without "
                            "--help verification — see AGENTS.md § Guardrails",
                        )
                    )
                    # Only report each block once
                    fence_has_invocation = False

    return violations


def check_file(filepath: Path) -> list[tuple[int, str]]:
    if _should_skip(filepath):
        return []
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError:
        return []
    return _find_violations(str(filepath), lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag CLI invocations in agent/skill markdown files without --help verification."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Markdown file paths to check (passed by pre-commit)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 on violations (default: advisory, exits 0)",
    )
    args = parser.parse_args(argv)

    all_violations: list[tuple[int, str]] = []
    for f in args.files:
        path = Path(f)
        all_violations.extend(check_file(path))

    for _, msg in all_violations:
        print(msg)

    if all_violations and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
