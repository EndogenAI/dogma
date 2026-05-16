#!/usr/bin/env python3
"""Tests for scripts/emit_otel_genai_spans.py (deprecated script).

This script is deprecated; tests verify that:
1. It exits with error code 1 when invoked as main
2. Imports still work (re-exports from emit_genai_spans.py)
"""

import subprocess
import sys


class TestDeprecatedScript:
    """Test deprecated emit_otel_genai_spans.py behavior."""

    def test_main_exits_with_error(self):
        """Test that running the script as main exits with code 1."""
        result = subprocess.run(
            [sys.executable, "scripts/emit_otel_genai_spans.py"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "deprecated" in result.stderr.lower()
        assert "emit_genai_spans.py" in result.stderr

    def test_deprecation_message_content(self):
        """Test that deprecation message contains necessary information."""
        result = subprocess.run(
            [sys.executable, "scripts/emit_otel_genai_spans.py"],
            capture_output=True,
            text=True,
        )

        # Message should guide users to the new script
        assert "emit_genai_spans.py" in result.stderr
        assert "deprecated" in result.stderr.lower()

    def test_compatibility_imports_work(self):
        """Test that re-exported functions are available for compatibility."""
        # Import should not raise
        from scripts.emit_otel_genai_spans import (
            emit_genai_span,
            validate_genai_span_attributes,
        )

        # Functions should be callable (not None)
        assert callable(emit_genai_span)
        assert callable(validate_genai_span_attributes)
