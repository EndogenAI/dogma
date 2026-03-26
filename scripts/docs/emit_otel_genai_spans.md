# `emit\_otel\_genai\_spans`

emit_otel_genai_spans.py — Emit GenAI semantic convention attributes in OTel spans.

Purpose:
    Extends instrument_agent_calls.py with a convenience wrapper that enforces
    GenAI semantic convention attribute presence for LLM call spans.

    Required GenAI attributes (per OTel semconv gen-ai-spans spec):
    - gen_ai.system (e.g., "anthropic")
    - gen_ai.request.model (e.g., "claude-3-5-sonnet-20241022")
    - gen_ai.usage.input_tokens (int)
    - gen_ai.usage.output_tokens (int)
    - gen_ai.response.finish_reason (string or list)

Inputs:
    - model: Model identifier (e.g., "claude-3-5-sonnet-20241022")
    - input_tokens: Number of input tokens
    - output_tokens: Number of output tokens
    - finish_reason: Completion finish reason (e.g., "end_turn", "max_tokens")
    - temperature: Optional temperature parameter (default: 0.0)

Outputs:
    - Span emitted with all required GenAI attributes

Usage:
    from scripts.emit_otel_genai_spans import emit_genai_span

    with emit_genai_span(
        model="claude-3-5-sonnet-20241022",
        input_tokens=150,
        output_tokens=42,
        finish_reason="end_turn"
    ) as span:
        # Perform LLM call here
        # span is automatically populated with GenAI attributes
        pass

Exit codes:
    0 — success
    1 — configuration error

Reference:
    - docs/research/otel-agent-instrumentation.md § Pattern 1 (H2)
    - AGENTS.md § Programmatic-First Principle
    - MANIFESTO.md § 2 Algorithms-Before-Tokens

Closes: #369

## Usage

```bash
    from scripts.emit_otel_genai_spans import emit_genai_span

    with emit_genai_span(
        model="claude-3-5-sonnet-20241022",
        input_tokens=150,
        output_tokens=42,
        finish_reason="end_turn"
    ) as span:
        # Perform LLM call here
        # span is automatically populated with GenAI attributes
        pass
```

<!-- hash:840d57b2bfb2e0dc -->
