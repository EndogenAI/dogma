# `emit\_otel\_metrics`

Emit OTel metrics for LLM usage and system health.
Implements Phase 4D: OTel Metrics.

Usage:
    uv run python scripts/emit_otel_metrics.py --metric input_tokens --value 10 --model claude-3-sonnet
    uv run python scripts/emit_otel_metrics.py --metric status --value 1 --system phase-gate

## Usage

```bash
    uv run python scripts/emit_otel_metrics.py --metric input_tokens --value 10 --model claude-3-sonnet
    uv run python scripts/emit_otel_metrics.py --metric status --value 1 --system phase-gate
```

<!-- hash:fe58992504c26959 -->
