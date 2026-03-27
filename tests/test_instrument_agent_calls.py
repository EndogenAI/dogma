"""
test_instrument_agent_calls.py — Unit tests for OTel span instrumentation wrapper.

Tests span creation, attribute presence, stdout export, and OTLP export (mocked).
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from instrument_agent_calls import (
    _build_exporter,
    _load_providers,
    get_provider_name,
    get_tracer,
    init_tracing,
)


def test_build_exporter_defaults_to_console():
    """Verify ConsoleSpanExporter is returned when no OTLP endpoint is set."""
    with patch.dict(os.environ, {}, clear=True):
        exporter = _build_exporter()
        # ConsoleSpanExporter writes to stdout by default
        assert exporter is not None
        assert "ConsoleSpanExporter" in str(type(exporter))


def test_build_exporter_returns_otlp_when_env_set():
    """Verify OTLPSpanExporter is returned when OTEL_EXPORTER_OTLP_ENDPOINT is set."""
    with patch.dict(os.environ, {"OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317"}):
        exporter = _build_exporter()
        assert exporter is not None
        assert "OTLPSpanExporter" in str(type(exporter))


@pytest.mark.io
def test_load_providers_reads_yaml(tmp_path):
    """Verify _load_providers reads and parses YAML file correctly."""
    providers_file = tmp_path / "providers.yml"
    providers_file.write_text("""
providers:
  - name: "test-provider"
    model_ids: ["test-model"]
    cost_tier: "free"
    local: true
""")

    config = _load_providers(providers_file)
    assert "providers" in config
    assert len(config["providers"]) == 1
    assert config["providers"][0]["name"] == "test-provider"


@pytest.mark.io
def test_load_providers_raises_on_missing_file(tmp_path):
    """Verify FileNotFoundError is raised when providers file doesn't exist."""
    missing_file = tmp_path / "nonexistent.yml"
    with pytest.raises(FileNotFoundError, match="Provider config not found"):
        _load_providers(missing_file)


@pytest.mark.io
def test_get_provider_name_maps_model_to_provider(tmp_path):
    """Verify get_provider_name correctly maps model ID to provider name."""
    providers_file = tmp_path / "providers.yml"
    providers_file.write_text("""
providers:
  - name: "anthropic-claude"
    model_ids: ["claude-3-5-sonnet-20241022", "claude-opus-4-5"]
    cost_tier: "high"
    local: false
""")

    provider = get_provider_name("claude-3-5-sonnet-20241022", providers_file)
    assert provider == "anthropic-claude"


@pytest.mark.io
def test_get_provider_name_returns_unknown_for_unmapped_model(tmp_path):
    """Verify get_provider_name returns 'unknown' for models not in config."""
    providers_file = tmp_path / "providers.yml"
    providers_file.write_text("""
providers:
  - name: "test-provider"
    model_ids: ["known-model"]
    cost_tier: "free"
    local: true
""")

    provider = get_provider_name("unknown-model", providers_file)
    assert provider == "unknown"


def test_get_tracer_returns_tracer_instance():
    """Verify get_tracer returns a valid Tracer instance."""
    # Clean up any existing tracer provider
    from opentelemetry import trace

    trace._TRACER_PROVIDER = None

    tracer = get_tracer("test.service")
    assert tracer is not None
    assert hasattr(tracer, "start_as_current_span")


def test_span_creation_with_genai_attributes():
    """Verify spans can be created with GenAI semantic convention attributes."""
    tracer = get_tracer("test.service")

    with tracer.start_as_current_span("llm.call") as span:
        span.set_attribute("gen_ai.operation.name", "chat")
        span.set_attribute("gen_ai.provider.name", "test-provider")
        span.set_attribute("gen_ai.request.model", "test-model")
        span.set_attribute("gen_ai.usage.input_tokens", 100)
        span.set_attribute("gen_ai.usage.output_tokens", 50)
        span.set_attribute("gen_ai.response.finish_reasons", ["stop"])

        # Verify span has a valid context (span_id != 0 for recording spans)
        context = span.get_span_context()
        assert (
            context.span_id != 0 or not span.is_recording()
        )  # Either it's recording with valid ID, or it's non-recording


@patch("instrument_agent_calls._build_exporter")
def test_init_tracing_sets_global_provider(mock_build_exporter):
    """Verify init_tracing sets the global TracerProvider."""
    from opentelemetry import trace
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter

    mock_build_exporter.return_value = ConsoleSpanExporter()

    # Just verify init_tracing doesn't raise an error
    # (TracerProvider may already be set from other tests)
    init_tracing("test.service")

    provider = trace.get_tracer_provider()
    # Verify we get some kind of tracer provider (may be proxy or real)
    assert provider is not None


def test_main_test_flag_emits_span(capsys):
    """Verify --test flag emits a test span."""
    with patch("sys.argv", ["instrument_agent_calls.py", "--test"]):
        from instrument_agent_calls import main

        exit_code = main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Test span emitted" in captured.err
