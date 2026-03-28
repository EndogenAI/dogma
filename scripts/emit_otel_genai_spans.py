#!/usr/bin/env python3
"""
emit_otel_genai_spans.py — Emit GenAI semantic convention attributes in OTel spans.

Purpose:
    Extends instrument_agent_calls.py with a convenience wrapper that enforces
    GenAI semantic convention attribute presence for LLM call spans.

    Canonical provider attribute policy:
    - Canonical key: gen_ai.provider.name (e.g., "anthropic")
    - Compatibility alias: gen_ai.system (legacy readers)

    Required GenAI attributes (per OTel semconv gen-ai-spans spec + compatibility policy):
    - gen_ai.provider.name (canonical provider identity)
    - gen_ai.request.model (e.g., "claude-3-5-sonnet-20241022")
    - gen_ai.usage.input_tokens (int)
    - gen_ai.usage.output_tokens (int)
    - gen_ai.response.finish_reasons (string or list)

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
"""

import logging
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Optional, Union
from uuid import uuid4

try:
    from scripts.instrument_agent_calls import get_provider_name, get_tracer
    from scripts.session_cost_log import log_session_cost
except ImportError as exc:
    print(
        "Error: failed to import required modules "
        "'scripts.instrument_agent_calls' or 'scripts.session_cost_log': "
        f"{exc}",
        file=sys.stderr,
    )
    sys.exit(1)


logger = logging.getLogger(__name__)

GENAI_PROVIDER_ATTR = "gen_ai.provider.name"
GENAI_PROVIDER_LEGACY_ATTR = "gen_ai.system"


def _coerce_token_count(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _append_session_cost_from_span(span_attributes: dict[str, object]) -> None:
    """Append session cost from span via bridge path with idempotency/dedup guard.

    Idempotency strategy:
    - Dedup key is deterministic: hash(model, tokens_in, tokens_out, timestamp_hour)
    - Suppresses duplicate spans in same hour (replay resilience)
    - Spans with identical model/token counts in the same hour are treated as duplicates
    - Logs dedup suppression at debug level (expected behavior, not an error)
    """
    model = span_attributes.get("gen_ai.request.model")
    input_tokens = _coerce_token_count(span_attributes.get("gen_ai.usage.input_tokens"))
    output_tokens = _coerce_token_count(span_attributes.get("gen_ai.usage.output_tokens"))

    if not isinstance(model, str) or not model:
        logger.warning("session-cost bridge skipped: missing model attribute")
        return
    if input_tokens is None or output_tokens is None:
        logger.warning("session-cost bridge skipped: invalid token attributes")
        return
    if input_tokens == 0 and output_tokens == 0:
        logger.warning("session-cost bridge skipped: zero-token record without synthetic marker")
        return

    now = datetime.now(timezone.utc)
    session_id = f"bridge/{now.date()}/{uuid4().hex[:8]}"
    timestamp = now.isoformat().replace("+00:00", "Z")
    phase = "bridge: span-close token capture"

    try:
        appended = log_session_cost(
            session_id=session_id,
            model=model,
            tokens_in=input_tokens,
            tokens_out=output_tokens,
            phase=phase,
            timestamp=timestamp,
        )
        if not appended:
            logger.debug(
                "session-cost bridge dedup: duplicate record suppressed (model=%s, tokens=%d+%d)",
                model,
                input_tokens,
                output_tokens,
            )
    except ValueError as exc:
        logger.warning("session-cost bridge skipped due to validation error: %s", exc)
    except OSError as exc:
        logger.warning("session-cost bridge skipped due to write error: %s", exc)


def get_provider_identity(span_attributes: dict[str, object]) -> str | None:
    """Return provider identity with canonical-first fallback behavior.

    Policy:
        1) Prefer gen_ai.provider.name (canonical)
        2) Fall back to gen_ai.system (legacy alias)
    """
    provider = span_attributes.get(GENAI_PROVIDER_ATTR)
    if isinstance(provider, str) and provider:
        return provider

    legacy_provider = span_attributes.get(GENAI_PROVIDER_LEGACY_ATTR)
    if isinstance(legacy_provider, str) and legacy_provider:
        return legacy_provider

    return None


@contextmanager
def emit_genai_span(
    model: str,
    input_tokens: int,
    output_tokens: int,
    finish_reason: Union[str, List[str]],
    operation_name: str = "chat",
    temperature: float = 0.0,
    span_name: Optional[str] = None,
):
    """Context manager that emits a span with GenAI semantic convention attributes.

    Args:
        model: Model identifier (e.g., "claude-3-5-sonnet-20241022")
        input_tokens: Number of input tokens consumed
        output_tokens: Number of output tokens generated
        finish_reason: Completion finish reason (string or list of strings)
        operation_name: GenAI operation type (default: "chat")
        temperature: Sampling temperature (default: 0.0)
        span_name: Custom span name (default: "{operation_name} {model}")

    Yields:
        Active span with GenAI attributes set

    Example:
        with emit_genai_span(
            model="claude-3-5-sonnet-20241022",
            input_tokens=150,
            output_tokens=42,
            finish_reason="end_turn"
        ) as span:
            # LLM call happens here
            response = call_llm(...)
    """
    tracer = get_tracer()
    provider_name = get_provider_name(model)

    # Build span name from operation + model if not provided
    if span_name is None:
        span_name = f"{operation_name} {model}"

    # Normalize finish_reason to list
    if isinstance(finish_reason, str):
        finish_reason_list = [finish_reason]
    else:
        finish_reason_list = finish_reason

    with tracer.start_as_current_span(span_name) as span:
        # Required GenAI attributes
        span.set_attribute(GENAI_PROVIDER_ATTR, provider_name)
        # Compatibility alias for legacy readers still keyed on gen_ai.system.
        span.set_attribute(GENAI_PROVIDER_LEGACY_ATTR, provider_name)
        span.set_attribute("gen_ai.operation.name", operation_name)
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("gen_ai.usage.input_tokens", input_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", output_tokens)
        span.set_attribute("gen_ai.response.finish_reasons", finish_reason_list)

        # Optional attributes
        span.set_attribute("gen_ai.request.temperature", temperature)

        try:
            yield span
        finally:
            # Always-on bridge for scripts using this span helper.
            attributes = {
                "gen_ai.request.model": model,
                "gen_ai.usage.input_tokens": input_tokens,
                "gen_ai.usage.output_tokens": output_tokens,
            }
            _append_session_cost_from_span(attributes)


def validate_genai_span_attributes(span_attributes: dict) -> tuple[bool, list[str]]:
    """Validate that all required GenAI attributes are present.

    Args:
        span_attributes: Dictionary of span attributes

    Returns:
        Tuple of (valid: bool, missing_attrs: list[str])
    """
    required_attrs = [
        "gen_ai.request.model",
        "gen_ai.usage.input_tokens",
        "gen_ai.usage.output_tokens",
        "gen_ai.response.finish_reasons",
    ]

    missing = [attr for attr in required_attrs if attr not in span_attributes]
    if get_provider_identity(span_attributes) is None:
        missing.append("gen_ai.provider.name|gen_ai.system")

    return (len(missing) == 0, missing)


def main():
    """CLI entry point for testing GenAI span emission."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Emit a test span with GenAI semantic convention attributes")
    parser.add_argument("--model", default="claude-3-5-sonnet-20241022", help="Model name for test span")
    parser.add_argument("--input-tokens", type=int, default=150, help="Input token count")
    parser.add_argument("--output-tokens", type=int, default=42, help="Output token count")
    parser.add_argument("--finish-reason", default="end_turn", help="Finish reason (e.g., end_turn, max_tokens)")
    parser.add_argument("--dry-run", action="store_true", help="Print sample span JSON and exit 0")

    args = parser.parse_args()

    if args.dry_run:
        provider_name = get_provider_name(args.model)
        sample_span = {
            "name": f"chat {args.model}",
            "attributes": {
                "gen_ai.provider.name": provider_name,
                "gen_ai.system": provider_name,
                "gen_ai.request.model": args.model,
                "gen_ai.usage.input_tokens": args.input_tokens,
                "gen_ai.usage.output_tokens": args.output_tokens,
                "gen_ai.response.finish_reasons": [args.finish_reason],
                "gen_ai.operation.name": "chat",
                "gen_ai.request.temperature": 0.0,
            },
        }
        print(json.dumps(sample_span, indent=2))
        return 0

    with emit_genai_span(
        model=args.model,
        input_tokens=args.input_tokens,
        output_tokens=args.output_tokens,
        finish_reason=args.finish_reason,
    ):
        print(
            f"Test GenAI span emitted: model={args.model}, "
            f"input={args.input_tokens}, output={args.output_tokens}, "
            f"finish_reason={args.finish_reason}",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
