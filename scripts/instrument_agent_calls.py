#!/usr/bin/env python3
"""
instrument_agent_calls.py — Wrap LLM call sites with OpenTelemetry Python SDK spans.

Purpose:
    Provides context-managed span instrumentation for LLM calls with GenAI semantic conventions.
    Reads provider configuration from data/inference-providers.yml.
    Exports to stdout JSONL by default; switches to OTLP via OTEL_EXPORTER_OTLP_ENDPOINT env var.

Inputs:
    - Environment variable OTEL_EXPORTER_OTLP_ENDPOINT (optional): OTLP exporter endpoint
    - data/inference-providers.yml: provider configuration

Outputs:
    - Spans emitted to stdout (ConsoleSpanExporter) or OTLP endpoint
    - Returns tracer instance for use in agent scripts
        - When combined with scripts/emit_otel_genai_spans.py, span-close hooks append measured
            token usage to session_cost_log.json for model calls this repo controls directly

Usage:
    from scripts.instrument_agent_calls import get_tracer, call_llm

    tracer = get_tracer()
    with tracer.start_as_current_span("llm.call") as span:
        span.set_attribute("gen_ai.operation.name", "chat")
        span.set_attribute("gen_ai.request.model", "claude-3-5-sonnet-20241022")
        response = some_llm_api_call()
        span.set_attribute("gen_ai.usage.input_tokens", response["usage"]["input"])
        span.set_attribute("gen_ai.usage.output_tokens", response["usage"]["output"])

Exit codes:
    0 — success
    1 — configuration error (missing providers file)

Reference:
    - docs/research/otel-agent-instrumentation.md § Pattern 1
    - AGENTS.md § Programmatic-First Principle
    - MANIFESTO.md § 2 Algorithms-Before-Tokens

Closes: #334
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
except ImportError:
    print("Error: OpenTelemetry SDK not installed. Run: uv sync", file=sys.stderr)
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Error: pyyaml not installed. Run: uv sync", file=sys.stderr)
    sys.exit(1)


def _build_exporter():
    """Build span exporter based on environment configuration.

    Returns ConsoleSpanExporter (stdout JSONL) by default.
    Returns OTLPSpanExporter if OTEL_EXPORTER_OTLP_ENDPOINT is set.
    """
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint:
        return OTLPSpanExporter(endpoint=endpoint)
    return ConsoleSpanExporter()


def _load_providers(providers_file: Path) -> dict:
    """Load provider configuration from YAML file.

    Args:
        providers_file: Path to data/inference-providers.yml

    Returns:
        Parsed YAML dict with providers list

    Raises:
        FileNotFoundError: If providers file doesn't exist
        yaml.YAMLError: If providers file is invalid YAML
    """
    if not providers_file.exists():
        raise FileNotFoundError(f"Provider config not found: {providers_file}")

    with providers_file.open() as f:
        return yaml.safe_load(f)


def init_tracing(service_name: str = "dogma.agent") -> None:
    """Initialize OpenTelemetry tracing with configured exporter.

    Args:
        service_name: Service name for tracer identification

    Side effects:
        Sets global TracerProvider and adds BatchSpanProcessor
    """
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(_build_exporter()))
    trace.set_tracer_provider(provider)


def get_tracer(service_name: str = "dogma.agent") -> trace.Tracer:
    """Get or create tracer instance.

    Args:
        service_name: Service name for tracer identification

    Returns:
        Tracer instance for creating spans
    """
    # Check if provider already initialized
    provider = trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        init_tracing(service_name)

    return trace.get_tracer(service_name)


def get_provider_name(model: str, providers_file: Optional[Path] = None) -> str:
    """Map model identifier to provider name from inference-providers.yml.

    Args:
        model: Model identifier (e.g., "claude-3-5-sonnet-20241022")
        providers_file: Path to providers config (defaults to data/inference-providers.yml)

    Returns:
        Provider name (e.g., "anthropic-claude") or "unknown" if not found
    """
    if providers_file is None:
        providers_file = Path(__file__).parent.parent / "data" / "inference-providers.yml"

    try:
        config = _load_providers(providers_file)
        for provider in config.get("providers", []):
            if model in provider.get("model_ids", []):
                return provider["name"]
    except (FileNotFoundError, yaml.YAMLError):
        pass

    return "unknown"


def main():
    """CLI entry point for testing instrumentation setup."""
    import argparse

    parser = argparse.ArgumentParser(description="Initialize OpenTelemetry instrumentation for LLM agent calls")
    parser.add_argument("--test", action="store_true", help="Emit a test span to verify exporter configuration")
    parser.add_argument("--model", default="claude-3-5-sonnet-20241022", help="Model name for test span")

    args = parser.parse_args()

    if args.test:
        tracer = get_tracer()
        provider_name = get_provider_name(args.model)

        with tracer.start_as_current_span("llm.call.test") as span:
            span.set_attribute("gen_ai.operation.name", "chat")
            span.set_attribute("gen_ai.provider.name", provider_name)
            span.set_attribute("gen_ai.system", provider_name)
            span.set_attribute("gen_ai.request.model", args.model)
            span.set_attribute("gen_ai.request.temperature", 0.0)
            span.set_attribute("gen_ai.usage.input_tokens", 150)
            span.set_attribute("gen_ai.usage.output_tokens", 42)
            span.set_attribute("gen_ai.response.finish_reasons", ["end_turn"])

        print(f"Test span emitted for model={args.model}, provider={provider_name}", file=sys.stderr)
        return 0

    print("Use get_tracer() in your scripts to create instrumented spans.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
