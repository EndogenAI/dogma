#!/usr/bin/env python3
"""
emit_otel_genai_spans.py — DEPRECATED: Use emit_genai_spans.py instead.

DEPRECATION NOTICE:
    This script has been renamed to `emit_genai_spans.py` to follow the action_target
    naming convention (issue #529). This stub redirects all imports and CLI invocations
    to the new module for backward compatibility.

    Please update your code to use:
        from scripts.emit_genai_spans import emit_genai_span

    Deprecated on: 2026-04-01
    See: scripts/DEPRECATED.md
"""

import sys
import warnings

warnings.warn(
    "emit_otel_genai_spans.py is deprecated. Use emit_genai_spans.py instead. See scripts/DEPRECATED.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export all public symbols from the new module for backward compatibility
from scripts.emit_genai_spans import (  # noqa: E402, F401
    GENAI_PROVIDER_ATTR,
    GENAI_PROVIDER_LEGACY_ATTR,
    emit_genai_span,
    get_provider_identity,
    validate_genai_span_attributes,
)


def main():
    """Redirect CLI invocation to new module."""
    from scripts.emit_genai_spans import main as new_main

    print(
        "Warning: emit_otel_genai_spans.py is deprecated. Use emit_genai_spans.py instead.",
        file=sys.stderr,
    )
    return new_main()


if __name__ == "__main__":
    sys.exit(main())
