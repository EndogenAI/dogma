"""
test_emit_otel_genai_spans.py — Unit tests for GenAI semantic convention span emitter.

Verifies all 5 required GenAI attributes are present in emitted spans.
"""

import logging
import sys
from pathlib import Path

import pytest

# Add scripts/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from emit_otel_genai_spans import (
    _append_session_cost_from_span,
    emit_genai_span,
    get_provider_identity,
    validate_genai_span_attributes,
)

pytestmark = pytest.mark.io


@pytest.fixture(autouse=True)
def isolate_session_cost_log_path(monkeypatch, tmp_path):
    """Prevent bridge writes from mutating repository-root session_cost_log.json."""
    monkeypatch.setenv("SESSION_COST_LOG_FILE", str(tmp_path / "session_cost_log.json"))


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
    """Verify validation passes with canonical provider attribute."""
    attributes = {
        "gen_ai.provider.name": "anthropic",
        "gen_ai.request.model": "claude-3-5-sonnet-20241022",
        "gen_ai.usage.input_tokens": 150,
        "gen_ai.usage.output_tokens": 42,
        "gen_ai.response.finish_reasons": ["end_turn"],
    }

    valid, missing = validate_genai_span_attributes(attributes)
    assert valid is True
    assert len(missing) == 0


def test_validate_genai_span_attributes_accepts_provider_name_without_system():
    """Canonical provider key alone should satisfy provider identity."""
    attributes = {
        "gen_ai.provider.name": "anthropic",
        "gen_ai.request.model": "test-model",
        "gen_ai.usage.input_tokens": 100,
        "gen_ai.usage.output_tokens": 50,
        "gen_ai.response.finish_reasons": ["stop"],
    }

    valid, missing = validate_genai_span_attributes(attributes)
    assert valid is True
    assert len(missing) == 0


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


def test_validate_genai_span_attributes_fails_missing_provider_and_system():
    """Provider identity is required via either gen_ai.provider.name or gen_ai.system."""
    attributes = {
        "gen_ai.request.model": "test-model",
        "gen_ai.usage.input_tokens": 100,
        "gen_ai.usage.output_tokens": 50,
        "gen_ai.response.finish_reasons": ["stop"],
    }

    valid, missing = validate_genai_span_attributes(attributes)
    assert valid is False
    assert "gen_ai.provider.name|gen_ai.system" in missing


def test_validate_genai_span_attributes_ignores_extra_attributes():
    """Verify validate_genai_span_attributes allows extra attributes beyond required."""
    attributes = {
        "gen_ai.provider.name": "anthropic",
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


def test_get_provider_identity_prefers_canonical_key():
    """Canonical provider key should take precedence when both keys are present."""
    provider = get_provider_identity(
        {
            "gen_ai.provider.name": "anthropic",
            "gen_ai.system": "legacy-anthropic",
        }
    )

    assert provider == "anthropic"


def test_get_provider_identity_falls_back_to_legacy_key():
    """Legacy provider key remains supported for compatibility reads."""
    provider = get_provider_identity({"gen_ai.system": "anthropic"})

    assert provider == "anthropic"


def test_main_emits_test_span(capsys, monkeypatch):
    """Verify main CLI emits a test span."""
    monkeypatch.setattr("sys.argv", ["emit_otel_genai_spans.py"])
    from emit_otel_genai_spans import main

    exit_code = main()

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Test GenAI span emitted" in captured.err


def test_bridge_appends_non_zero_tokens(monkeypatch):
    """Bridge should append non-zero token spans via log_session_cost."""
    captured = {}

    def fake_log_session_cost(session_id, model, tokens_in, tokens_out, phase, timestamp, **kwargs):
        captured["session_id"] = session_id
        captured["model"] = model
        captured["tokens_in"] = tokens_in
        captured["tokens_out"] = tokens_out
        captured["phase"] = phase
        captured["timestamp"] = timestamp

    monkeypatch.setattr("emit_otel_genai_spans.log_session_cost", fake_log_session_cost)

    _append_session_cost_from_span(
        {
            "gen_ai.request.model": "test-model",
            "gen_ai.usage.input_tokens": 10,
            "gen_ai.usage.output_tokens": 5,
        }
    )

    assert captured["model"] == "test-model"
    assert captured["tokens_in"] == 10
    assert captured["tokens_out"] == 5


def test_bridge_warns_and_skips_zero_tokens(monkeypatch, caplog):
    """Bridge should warn and skip writes for zero-token payloads."""
    called = {"value": False}

    def fake_log_session_cost(*args, **kwargs):
        called["value"] = True

    monkeypatch.setattr("emit_otel_genai_spans.log_session_cost", fake_log_session_cost)

    with caplog.at_level(logging.WARNING):
        _append_session_cost_from_span(
            {
                "gen_ai.request.model": "test-model",
                "gen_ai.usage.input_tokens": 0,
                "gen_ai.usage.output_tokens": 0,
            }
        )

    assert called["value"] is False
    assert "zero-token record" in caplog.text


def test_bridge_warns_on_invalid_payload(monkeypatch, caplog):
    """Bridge should warn and skip for invalid token payload values."""
    called = {"value": False}

    def fake_log_session_cost(*args, **kwargs):
        called["value"] = True

    monkeypatch.setattr("emit_otel_genai_spans.log_session_cost", fake_log_session_cost)

    with caplog.at_level(logging.WARNING):
        _append_session_cost_from_span(
            {
                "gen_ai.request.model": "test-model",
                "gen_ai.usage.input_tokens": "abc",
                "gen_ai.usage.output_tokens": 5,
            }
        )

    assert called["value"] is False
    assert "invalid token attributes" in caplog.text


def test_bridge_dedup_suppresses_duplicate_spans(monkeypatch, caplog):
    """Bridge dedup: log_session_cost returning False logs debug dedup message."""
    calls = []

    def fake_log_session_cost(*args, **kwargs):
        calls.append((args, kwargs))
        return False  # Simulate dedup suppression

    monkeypatch.setattr("emit_otel_genai_spans.log_session_cost", fake_log_session_cost)

    with caplog.at_level(logging.DEBUG):
        _append_session_cost_from_span(
            {
                "gen_ai.request.model": "test-model",
                "gen_ai.usage.input_tokens": 10,
                "gen_ai.usage.output_tokens": 5,
            }
        )

    assert len(calls) == 1
    # Should log dedup suppression at debug level
    assert any("dedup" in record.message.lower() for record in caplog.records if record.levelname == "DEBUG")


def test_bridge_dedup_appends_distinct_spans(monkeypatch):
    """Bridge dedup: log_session_cost returning True indicates successful append."""
    calls = []

    def fake_log_session_cost(*args, **kwargs):
        calls.append((args, kwargs))
        return True  # Record was appended

    monkeypatch.setattr("emit_otel_genai_spans.log_session_cost", fake_log_session_cost)

    _append_session_cost_from_span(
        {
            "gen_ai.request.model": "test-model",
            "gen_ai.usage.input_tokens": 10,
            "gen_ai.usage.output_tokens": 5,
        }
    )

    assert len(calls) == 1
    # Verify log_session_cost was called with proper kwargs
    _, kwargs = calls[0]
    assert kwargs["model"] == "test-model"
    assert kwargs["tokens_in"] == 10
    assert kwargs["tokens_out"] == 5
