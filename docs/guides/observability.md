# Observability

**Closes #541**

Instrumentation and observability patterns for the dogma MCP server. This guide covers the OTel stack lifecycle, span instrumentation conventions, transport modes, and verification workflows.

---

## Contents

- [Stack Startup](#stack-startup)
- [Span Instrumentation Patterns](#span-instrumentation-patterns)
- [RAGAS Metrics](#ragas-metrics)
- [Transport Modes](#transport-modes)
- [Canonical Example](#canonical-example)
- [Anti-Pattern](#anti-pattern)
- [Verification Queries](#verification-queries)

---

## Stack Startup

The observability stack consists of an OTel Collector (receives spans/metrics), Jaeger (stores and visualizes traces), and Prometheus (stores metrics). The stack is orchestrated via Docker Compose.

### Start the Stack

```bash
uv run python scripts/start_otel_stack.py
```

Alternatively, use the VS Code task **Start OTel Stack** from the command palette.

### Confirm Healthy

Verify all containers are running:

```bash
docker ps
```

Expected output (3 containers):

```
CONTAINER ID   IMAGE                             STATUS
<id>           otel/opentelemetry-collector      Up
<id>           jaegertracing/all-in-one:latest   Up
<id>           prom/prometheus:latest            Up
```

Access the UIs:
- **Jaeger**: [http://localhost:16686](http://localhost:16686)
- **Prometheus**: [http://localhost:9090](http://localhost:9090)
- **OTel Collector Health**: [http://localhost:13133](http://localhost:13133)

### Stop the Stack

```bash
uv run python scripts/start_otel_stack.py --stop
```

Or use the VS Code task **Stop OTel Stack**.

---

## Span Patterns

The `mcp_server/dogma_server.py` implementation follows the OTel semantic conventions for GenAI and MCP operations. See [`mcp_server/dogma_server.py`](../../mcp_server/dogma_server.py) `_configure_telemetry()` for the full setup.

### Required Attributes

Every tool call span must include:

| Attribute | Type | Example | When Required |
|-----------|------|---------|---------------|
| `gen_ai.tool.name` | string | `"validate_agent_file"` | Always |
| `gen_ai.operation.name` | string | `"execute_tool"` | Always |
| `mcp.server.operation.duration` | float (seconds) | `0.142` | Always (via histogram) |
| `error.type` | string | `"tool_error"` or exception name | When `ok=False` or exception raised |
| `error.message` | string | Human-readable error summary | When `error.type` is set |

### Implementation Pattern

```python
from opentelemetry import trace

tracer = trace.get_tracer("dogma.mcp.server")

with tracer.start_as_current_span("mcp.server.execute_tool") as span:
    span.set_attribute("gen_ai.tool.name", tool_name)
    span.set_attribute("gen_ai.operation.name", "execute_tool")
    
    try:
        result = perform_tool_call()
        
        # Instrument error paths too
        if result.get("ok") is False:
            span.set_attribute("error.type", "tool_error")
            span.set_attribute("error.message", result.get("message", "Unknown error"))
        
        return result
    except Exception as exc:
        span.set_attribute("error.type", type(exc).__name__)
        span.set_attribute("error.message", str(exc))
        raise
```

**Key principle**: Instrument **all exit paths** — success, validation failures, timeouts, and exceptions. See [Anti-Pattern](#anti-pattern) for what happens when error paths are skipped.

### Histogram Recording

Duration metrics use the `mcp.server.operation.duration` histogram:

```python
from opentelemetry import metrics
import time

meter = metrics.get_meter("dogma.mcp.server")
duration_histogram = meter.create_histogram(
    "mcp.server.operation.duration",
    unit="s",
    description="Duration of MCP tool-call operations in seconds"
)

started = time.perf_counter()
try:
    result = perform_tool_call()
finally:
    duration_s = time.perf_counter() - started
    duration_histogram.record(duration_s, {"gen_ai.tool.name": tool_name})
```

---

## RAGAS Metrics

RAGAS (Retrieval-Augmented Generation Assessment) metrics are emitted as span attributes for every tool call via `_run_with_mcp_telemetry()` (Phase 9, #542). These metrics assess answer quality using structural heuristics rather than LLM-as-judge evaluation.

### Metric Attributes

| Attribute | Description | Range | Heuristic Tier |
|-----------|-------------|-------|----------------|
| `gen_ai.faithfulness` | Answer consistency with context sources | 0.0–1.0 | 3-tier (error/fast/slow) |
| `gen_ai.answer_relevancy` | Answer alignment with query intent | 0.0–1.0 | 3-tier |
| `gen_ai.context_precision` | Relevance of retrieved context chunks | 0.0–1.0 | 3-tier |
| `gen_ai.context_recall` | Coverage of required context | 0.0–1.0 | 3-tier |

All metrics are floats in `[0.0, 1.0]` range. Higher values indicate better quality.

### Emission Timing

RAGAS attributes are computed and attached to every tool call span after the operation completes. The 3-tier heuristic implementation:
- **Error tier**: Returns `0.0` if tool call failed (`ok=False` or exception raised)
- **Fast tier**: Returns `0.5` for successful calls with partial context
- **Slow tier**: Returns `1.0` for successful calls with full context and citations

See [`mcp_server/dogma_server.py`](../../mcp_server/dogma_server.py) `_run_with_mcp_telemetry()` for implementation details.

### Querying RAGAS Metrics in Jaeger

1. Open Jaeger UI: [http://localhost:16686](http://localhost:16686)
2. Select service: `dogma.mcp.server`, operation: `mcp.server.execute_tool`
3. Add tag filters for specific metrics:
   - `gen_ai.faithfulness`
   - `gen_ai.answer_relevancy`
   - `gen_ai.context_precision`
   - `gen_ai.context_recall`
4. Use range operators to filter by quality threshold (e.g., `gen_ai.faithfulness > 0.7`)

**Cross-reference**: Phase 9 implementation (#542) introduced the 3-tier heuristic pattern as an interim solution before full RAGAS library integration.

---

## Transport Modes

The OTel instrumentation supports two transport modes, controlled by the `DOGMA_OTEL_EXPORTER` environment variable.

### Mode 1: OTLP (Default)

Sends spans and metrics to the OTel Collector via gRPC.

```bash
export DOGMA_OTEL_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

**When to use**: Development and CI where the OTel stack is running (Docker Compose).

**Advantages**:
- Real-time trace visualization in Jaeger
- Prometheus metrics integration
- Full observability pipeline (collection → storage → query)

**Disadvantages**:
- Requires Docker stack to be running
- Network dependency

### Mode 2: JSONL (Fallback)

Writes spans to a local JSONL file (`.cache/mcp-metrics/tool_calls.jsonl`). No OTel Collector required.

```bash
export DOGMA_OTEL_EXPORTER=jsonl
```

**When to use**:
- CI environments where Docker is unavailable or rate-limited
- Local development without Docker
- Offline analysis and debugging

**Advantages**:
- No external dependencies
- Deterministic file-based output
- Easy to parse with standard tools (`jq`, `python`)

**Disadvantages**:
- No real-time visualization
- Requires manual conversion to import into Jaeger

### Switching Modes

Mode selection happens at process startup via `_configure_telemetry()`. To switch modes, set the environment variable before starting the MCP server:

```bash
# OTLP mode (requires stack running)
DOGMA_OTEL_EXPORTER=otlp uv run python -m mcp_server.dogma_server

# JSONL mode (no stack required)
DOGMA_OTEL_EXPORTER=jsonl uv run python -m mcp_server.dogma_server
```

---

## Canonical Example

A fully instrumented `validate_agent_file` tool call with all required attributes:

```json
{
  "trace_id": "0af7651916cd43dd8448eb211c80319c",
  "span_id": "b7ad6b7169203331",
  "parent_span_id": null,
  "name": "mcp.server.execute_tool",
  "kind": "INTERNAL",
  "start_time": "2026-04-01T10:42:17.234567Z",
  "end_time": "2026-04-01T10:42:17.376890Z",
  "status": {
    "status_code": "OK"
  },
  "attributes": {
    "gen_ai.tool.name": "validate_agent_file",
    "gen_ai.operation.name": "execute_tool",
    "mcp.server.operation.duration": 0.142
  },
  "events": [],
  "links": []
}
```

For error cases, the span includes error attributes:

```json
{
  "trace_id": "1bf8752027de54ee9559fc322d91429d",
  "span_id": "c8be7c8260314442",
  "parent_span_id": null,
  "name": "mcp.server.execute_tool",
  "kind": "INTERNAL",
  "start_time": "2026-04-01T10:45:23.123456Z",
  "end_time": "2026-04-01T10:45:23.265789Z",
  "status": {
    "status_code": "ERROR",
    "description": "tool_error"
  },
  "attributes": {
    "gen_ai.tool.name": "validate_agent_file",
    "gen_ai.operation.name": "execute_tool",
    "mcp.server.operation.duration": 0.142,
    "error.type": "tool_error",
    "error.message": "Missing required frontmatter field: name"
  },
  "events": [],
  "links": []
}
```

**Spec reference**: [OTel Semantic Conventions for GenAI v1.40.0](https://opentelemetry.io/docs/specs/semconv/gen-ai/)

---

## Anti-Pattern

### Instrumenting Only the Happy Path

**Problem**: Adding OTel spans only to successful tool calls but skipping error-path branches means that the highest-value telemetry — the signals that explain *why* something is failing — is never captured.

**Canonical failure scenario**:

```python
# ❌ Anti-pattern: only instrument success path
with tracer.start_as_current_span("mcp.server.execute_tool") as span:
    span.set_attribute("gen_ai.tool.name", tool_name)
    
    result = perform_tool_call()
    
    # Only set duration if successful
    if result.get("ok") is True:
        span.set_attribute("mcp.server.operation.duration", duration)
    
    # Error path has NO instrumentation
    return result
```

**What gets missed**:
- Validation failures (missing schema fields, malformed input)
- Empty responses (tool returned no data)
- Timeout conditions (operation took >5s and was abandoned)
- Partial failures (tool completed but with degraded quality)

**From the OTel Observability Primer**: "Observability is the ability to understand a system's internal state by examining its outputs." If error states produce no telemetry output, the system is not observable.

### Correct Pattern

Instrument **all exit paths**:

```python
# ✅ Correct: instrument every path
with tracer.start_as_current_span("mcp.server.execute_tool") as span:
    span.set_attribute("gen_ai.tool.name", tool_name)
    span.set_attribute("gen_ai.operation.name", "execute_tool")
    
    try:
        result = perform_tool_call()
        
        # Check for soft failures (ok=False but no exception)
        if result.get("ok") is False or result.get("errors"):
            span.set_attribute("error.type", "tool_error")
            error_msg = result.get("message") or result.get("errors")
            if error_msg:
                span.set_attribute("error.message", str(error_msg))
        
        return result
    except Exception as exc:
        # Hard failures
        span.set_attribute("error.type", type(exc).__name__)
        span.set_attribute("error.message", str(exc))
        raise
    finally:
        # Always record duration
        duration_s = time.perf_counter() - started
        histogram.record(duration_s, {"gen_ai.tool.name": tool_name})
```

**Citation**: Cluster 5 Pattern Catalog from [`docs/research/sprint-22-baseline-stabilization.md`](../research/sprint-22-baseline-stabilization.md#cluster-5-observability-patterns-534-425).

---

## Verification Queries

### Query Jaeger for Specific Tool Call Spans

1. Open Jaeger UI: [http://localhost:16686](http://localhost:16686)
2. Select service: `dogma.mcp.server`
3. Select operation: `mcp.server.execute_tool`
4. Add tag filter: `gen_ai.tool.name=<tool-name>` (e.g., `validate_agent_file`)
5. Click **Find Traces**

Filter traces by status:
- **Only errors**: Add tag `error.type` (any value)
- **Only successes**: Add tag `error.type` and use NOT operator

### Query by Duration

To find slow operations (P95 latency alert threshold):

1. In Jaeger search, set **Min Duration**: `2s` (ADR-008 threshold)
2. Set **Lookback**: `1h` or `24h`
3. Click **Find Traces**

### Read JSONL Exports

When running in JSONL mode, verify export file exists and contains valid records:

```bash
# Check file exists and has content
ls -lh .cache/mcp-metrics/tool_calls.jsonl

# Count total records
wc -l .cache/mcp-metrics/tool_calls.jsonl

# View last 10 tool calls
tail -10 .cache/mcp-metrics/tool_calls.jsonl | jq .

# Filter by tool name
jq 'select(.tool_name == "validate_agent_file")' .cache/mcp-metrics/tool_calls.jsonl

# Calculate error rate
jq -s 'map(select(.is_error == true)) | length' .cache/mcp-metrics/tool_calls.jsonl
```

### Convert JSONL to OTel Format (Future)

For importing JSONL files into Jaeger after the fact:

```bash
# Placeholder — implementation pending
uv run python scripts/convert_jsonl_to_otel.py \
  --input .cache/mcp-metrics/tool_calls.jsonl \
  --output .cache/mcp-metrics/spans.json
```

This script does not yet exist — tracked in Sprint 22 Phase 8 follow-up.

---

## See Also

- [ADR-008: MCP Quality Metrics Framework](../decisions/ADR-008-mcp-quality-metrics-framework.md)
- [Sprint 22 Baseline Stabilization Research](../research/sprint-22-baseline-stabilization.md)
- [MCP Server README](../../mcp_server/README.md)
- [OTel Semantic Conventions for GenAI v1.40.0](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
