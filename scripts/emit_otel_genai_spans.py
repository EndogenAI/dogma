#!/usr/bin/env python3
"""
emit_otel_genai_spans.py — DEPRECATED: Use emit_genai_spans.py instead.

DEPRECATION NOTICE:
    This script has been renamed to `emit_genai_spans.py` to follow the action_target
    naming convention (issue #529).

    Please update your code to use:
        from scripts.emit_genai_spans import emit_genai_span

    Deprecated on: 2026-04-01
    See: scripts/DEPRECATED.md
"""

import sys

if __name__ == "__main__":
    print(
        "ERROR: emit_otel_genai_spans.py is deprecated and has been renamed to emit_genai_spans.py.\n"
        "Please update your scripts to use: uv run python scripts/emit_genai_spans.py\n"
        "See scripts/DEPRECATED.md for details.",
        file=sys.stderr,
    )
    sys.exit(1)
