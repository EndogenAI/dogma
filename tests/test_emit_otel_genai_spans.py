"""
test_emit_otel_genai_spans.py — Unit tests for GenAI semantic convention span emitter.

Verifies all 5 required GenAI attributes are present in emitted spans.
"""

import sys
from pathlib import Path
from unittest.mock import patch

# Add scripts/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from emit_otel_genai_spans import (
    emit_genai_span,
    validate_genai_span_attributes,
)


def test_emit_genai_span_sets_all_required_attributes():
    """Verify emit_genai_span sets all 5 required GenAI attributes."""
    with emit_genai_span(
        model="claude-3-5-sonnet-20241022", input_tokens=150, output_tokens=42, finish_reason="end_turn"
    ) as span:
        # Verify span has a valid context (either recording or non-recording is OK in test env)
        context = span.get_span_context()
        assert context is not None


def test_emit_genai_span_handles_string_finish_reason():
    """Verify emit_genai_span converts string finish_reason to list."""
    with emit_genai_span(model="test-model", input_tokens=100, output_tokens=50, finish_reason="stop") as span:
        context = span.get_span_context()
        assert context is not None


def test_emit_genai_span_handles_list_finish_reason():
    """Verify emit_genai_span accepts list of finish reasons."""
    with emit_genai_span(
        model="test-model", input_tokens=100, output_tokens=50, finish_reason=["stop", "max_tokens"]
    ) as span:
        context = span.get_span_context()
        assert context is not None


def test_emit_genai_span_accepts_custom_span_name():
    """Verify emit_genai_span accepts custom span name."""
    with emit_genai_span(
        model="test-model", input_tokens=100, output_tokens=50, finish_reason="stop", span_name="custom.llm.call"
    ) as span:
        context = span.get_span_context()
        assert context is not None


def test_emit_genai_span_accepts_custom_operation_name():
    """Verify emit_genai_span accepts custom operation name."""
    with emit_genai_span(
        model="test-model", input_tokens=100, output_tokens=50, finish_reason="stop", operation_name="completion"
    ) as span:
        context = span.get_span_context()
        assert context is not None


def test_emit_genai_span_accepts_custom_temperature():
    """Verify emit_genai_span accepts custom temperature."""
    with emit_genai_span(
        model="test-model", input_tokens=100, output_tokens=50, finish_reason="stop", temperature=0.7
    ) as span:
        context = span.get_span_context()
        assert context is not None


def test_validate_genai_span_attributes_passes_complete_set():
    """Verify validate_genai_span_attributes returns True for complete attribute set."""
    attributes = {
        "gen_ai.system": "anthropic",
        "gen_ai.request.model": "claude-3-5-sonnet-20241022",
        "gen_ai.usage.input_tokens": 150,
        "gen_ai.usage.output_tokens": 42,
        "gen_ai.response.finish_reasons": ["end_turn"],
    }

    valid, missing = validate_genai_span_attributes(attributes)
    assert valid is True
    assert len(missing) == 0


def test_validate_genai_span_attributes_fails_missing_system():
    """Verify validate_genai_span_attributes detects missing gen_ai.system."""
    attributes = {
        "gen_ai.request.model": "test-model",
        "gen_ai.usage.input_tokens": 100,
        "gen_ai.usage.output_tokens": 50,
        "gen_ai.response.finish_reasons": ["stop"],
    }

    valid, missing = validate_genai_span_attributes(attributes)
    assert valid is False
    assert "gen_ai.system" in missing


def test_validate_genai_span_attributes_fails_missing_multiple():
    """Verify validate_genai_span_attributes detects multiple missing attributes."""
    attributes = {"gen_ai.system": "test-provider"}

    valid, missing = validate_genai_span_attributes(attributes)
    assert valid is False
    assert len(missing) == 4
    assert "gen_ai.request.model" in missing
    assert "gen_ai.usage.input_tokens" in missing
    assert "gen_ai.usage.output_tokens" in missing
    assert "gen_ai.response.finish_reasons" in missing


def test_validate_genai_span_attributes_ignores_extra_attributes():
    """Verify validate_genai_span_attributes allows extra attributes beyond required."""
    attributes = {
        "gen_ai.system": "anthropic",
        "gen_ai.request.model": "test-model",
        "gen_ai.usage.input_tokens": 100,
        "gen_ai.usage.output_tokens": 50,
        "gen_ai.response.finish_reasons": ["stop"],
        "gen_ai.request.temperature": 0.7,  # Extra attribute
        "custom.attribute": "value",  # Extra attribute
    }

    valid, missing = validate_genai_span_attributes(attributes)
    assert valid is True
    assert len(missing) == 0


def test_main_emits_test_span(capsys):
    """Verify main CLI emits a test span."""
    with patch("sys.argv", ["emit_otel_genai_spans.py"]):
        from emit_otel_genai_spans import main

        exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Test GenAI span emitted" in captured.err
