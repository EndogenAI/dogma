# `instrument\_agent\_calls`

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

## Usage

```bash
    from scripts.instrument_agent_calls import get_tracer, call_llm

    tracer = get_tracer()
    with tracer.start_as_current_span("llm.call") as span:
        span.set_attribute("gen_ai.operation.name", "chat")
        span.set_attribute("gen_ai.request.model", "claude-3-5-sonnet-20241022")
        response = some_llm_api_call()
        span.set_attribute("gen_ai.usage.input_tokens", response["usage"]["input"])
        span.set_attribute("gen_ai.usage.output_tokens", response["usage"]["output"])
```

<!-- hash:157789eb9e3be96a -->
