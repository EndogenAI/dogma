---
title: "OpenTelemetry Agent Instrumentation Patterns"
status: Final
date: 2026-03-26
closes_issues: [334, 342, 346, 369]
recommendations:
- id: rec-otel-agent-instrumentation-001
  title: "Adopt OTel Python SDK span instrumentation for all LLM calls in agent scripts"
  status: accepted-for-adoption
  linked_issue: 334
  decision_ref: ""
- id: rec-otel-agent-instrumentation-002
  title: "Adopt GenAI semantic conventions (gen_ai.*) for all LLM span attributes"
  status: accepted-for-adoption
  linked_issue: 369
  decision_ref: ""
- id: rec-otel-agent-instrumentation-003
  title: "Define /health endpoint convention for future long-running Python services"
  status: accepted-for-adoption
  linked_issue: 342
  decision_ref: ""
- id: rec-otel-agent-instrumentation-004
  title: "Implement slow-error detection via span latency thresholds and token-ceiling breach signals"
  status: accepted-for-adoption
  linked_issue: 346
  decision_ref: ""
---

# OpenTelemetry Agent Instrumentation Patterns

## 1. Executive Summary

Agent workflows operating without structured telemetry accumulate invisible failure debt: token overruns, slow errors, and cascading retries that surface only after cost spikes. This synthesis documents four instrumentation clusters required for Q2 Wave 2 Phase 4A: (1) OTel Python SDK span creation patterns for LLM calls, (2) GenAI semantic conventions for span attributes, (3) `/health` endpoint conventions for long-running services, and (4) slow-error discovery via deferred-feedback detection. All patterns are designed for a **pluggable exporter** posture — stdout JSONL by default (no collector required), with OTLP via `OTEL_EXPORTER_OTLP_ENDPOINT` env var. No live services exist in `data/substrate-atlas.yml` and no OTel SDK is currently used in `scripts/` — this document establishes the conventions to adopt when instrumentation is introduced.

The governing axioms are **Endogenous-First** ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)) — synthesize from existing knowledge before reaching outward — and **Algorithms-Before-Tokens** ([MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens)) — prefer deterministic, encoded instrumentation over interactive token burn.

---

## 2. Hypothesis Validation

| Hypothesis | Status | Evidence |
|---|---|---|
| H1: The OTel Python SDK `tracer.start_as_current_span()` context manager provides idiomatic span creation for LLM calls | **Confirmed** | OTel Python instrumentation guide documents `with tracer.start_as_current_span("span-name") as span:` as the canonical pattern. Span closes automatically on block exit. |
| H2: GenAI semantic conventions define standard attribute names (`gen_ai.*`) that enable vendor-agnostic dashboards | **Confirmed** | OTel semconv gen-ai-spans spec defines `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons` as recommended attributes. Span name convention: `{gen_ai.operation.name} {gen_ai.request.model}`. |
| H3: A pluggable exporter can default to stdout JSONL and switch to OTLP via env var without code changes | **Confirmed** | `ConsoleSpanExporter` emits JSON to stdout; `OTLPSpanExporter` reads `OTEL_EXPORTER_OTLP_ENDPOINT`. Switching between them requires only a factory function change, not instrumented code changes. |
| H4: `/health` endpoint conventions (liveness vs readiness) are well-established from Kubernetes probes and can be adopted as a convention before live services exist | **Confirmed** | Kubernetes docs define liveness probe (is the process alive?) vs readiness probe (is it accepting traffic?). The convention is purely HTTP — applicable to FastAPI/Flask services without requiring Kubernetes deployment. |
| H5: Slow-error discovery is addressable via span-level latency thresholds and token-ceiling breach signals | **Confirmed** | `docs/research/ai-workload-observability.md` Pattern 3 documents invisible token debt via unobservable retries. `AGENTS.md § Async Process Handling` defines explicit timeout ceilings. These compose into a detection heuristic: span duration > timeout ceiling OR output tokens ≥ configured ceiling = slow-error signal. |

---

## 3. Pattern Catalog

### Pattern 1: OTel Python SDK Span Instrumentation for LLM Calls (#334)

**Summary**: Wrap every LLM call in a context-managed span using `tracer.start_as_current_span()`. Set GenAI semantic attributes on the span. Export via `ConsoleSpanExporter` (stdout JSONL) by default; switch to OTLP by setting `OTEL_EXPORTER_OTLP_ENDPOINT`.

**Setup** (`opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp-proto-grpc`, `opentelemetry-semantic-conventions`):

```python
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def _build_exporter():
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint:
        return OTLPSpanExporter(endpoint=endpoint)
    return ConsoleSpanExporter()

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(_build_exporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("dogma.agent")
```

**Endogenous note**: No OTel SDK is currently used in `scripts/`; `data/substrate-atlas.yml` lists 23 substrate types with no live services — a collector endpoint is not required in this phase. The `ConsoleSpanExporter` default produces stdout JSONL that can be piped to `.cache/traces/`.

**Canonical example**:

```python
def call_llm(model: str, prompt: str, temperature: float = 0.0) -> dict:
    with tracer.start_as_current_span("llm.call") as span:
        span.set_attribute("gen_ai.operation.name", "chat")
        span.set_attribute("gen_ai.provider.name", "anthropic")
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("gen_ai.request.temperature", temperature)
        response = _invoke_api(model=model, prompt=prompt)
        span.set_attribute("gen_ai.usage.input_tokens", response["usage"]["input_tokens"])
        span.set_attribute("gen_ai.usage.output_tokens", response["usage"]["output_tokens"])
        span.set_attribute("gen_ai.response.finish_reasons", [response["stop_reason"]])
        return response
```

This is the **Algorithms-Before-Tokens** ([MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens)) pattern: span instrumentation makes token spend deterministically observable per call, eliminating post-hoc budget guesswork.

**Anti-pattern**: Logging LLM call metadata to stdout via `print()` or `logging.info()` without structured span context. Unstructured logs cannot be correlated across phases, cannot be aggregated into histograms, and are lost when context is compacted. A `print(f"LLM call: {model}, tokens={n}")` line tells you nothing about which agent phase produced the call, what the parent span was, or how to group calls into session-level totals.

---

### Pattern 2: GenAI Semantic Conventions for Span Attributes (#369)

**Summary**: Use the canonical `gen_ai.*` attribute names from the OTel GenAI semantic conventions spec. These ensure vendor-agnostic observability dashboards and eliminate re-instrumentation cost when switching model providers.

**Spec status**: Development (OTel semconv). Instrumentations using v1.36.0 or prior must not change the emitted version by default; opt in to latest experimental via `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`.

**All Required / Recommended attributes for LLM inference spans**:

| Attribute | Level | Type | Description | Example |
|---|---|---|---|---|
| `gen_ai.operation.name` | Required | string | Operation type | `chat` |
| `gen_ai.provider.name` | Required | string | Provider identifier (new spec ≥ v1.36.0) | `anthropic` |
| `gen_ai.system` | Required (prior v1.36.0) | string | Deprecated alias for `gen_ai.provider.name`; used by older instrumentation | `anthropic` |
| `gen_ai.request.model` | Conditionally Required | string | Model name requested | `claude-3-5-sonnet-20241022` |
| `gen_ai.request.temperature` | Recommended | double | Sampling temperature | `0.0` |
| `gen_ai.request.max_tokens` | Recommended | int | Max tokens ceiling | `4096` |
| `gen_ai.usage.input_tokens` | Recommended | int | Input (prompt) token count | `1200` |
| `gen_ai.usage.output_tokens` | Recommended | int | Output (completion) token count | `340` |
| `gen_ai.response.finish_reasons` | Recommended | string[] | Stop reason(s) | `["end_turn"]` |
| `gen_ai.response.model` | Recommended | string | Actual model used (may differ from requested) | `claude-3-5-sonnet-20241022` |
| `error.type` | Conditionally Required | string | Error class if span ended in error | `rate_limit_error` |

**Span name convention**: `{gen_ai.operation.name} {gen_ai.request.model}` — e.g. `chat claude-3-5-sonnet-20241022`.

**Span kind**: `CLIENT` (recommended; `INTERNAL` only when model runs in-process).

**Migration note**: `gen_ai.system` (pre-v1.36.0) and `gen_ai.provider.name` (v1.36.0+) are functionally equivalent. Emit `gen_ai.system` for backward compatibility with existing dashboards that already reference it (see `docs/research/ai-workload-observability.md` Recommendation 4). Emit `gen_ai.provider.name` in new instrumentation. Bridge pattern: set both during transition period.

**Canonical example**: Multi-attribute span for a Claude API call satisfying all four AC3 attributes:

```python
span.set_attribute("gen_ai.system", "anthropic")          # backward compat
span.set_attribute("gen_ai.provider.name", "anthropic")   # v1.36.0+ spec
span.set_attribute("gen_ai.request.model", "claude-3-5-sonnet-20241022")
span.set_attribute("gen_ai.request.temperature", 0.0)
span.set_attribute("gen_ai.usage.input_tokens", 1200)
span.set_attribute("gen_ai.usage.output_tokens", 340)
span.set_attribute("gen_ai.response.finish_reasons", ["end_turn"])
span.set_attribute("gen_ai.operation.name", "chat")
```

**Anti-pattern**: Using ad hoc attribute names like `span.set_attribute("model", "claude")` or `span.set_attribute("tokens_in", 1200)`. Non-standard keys break vendor-agnostic dashboards and must be re-mapped for every observability backend. They are invisible to any tooling that queries by canonical `gen_ai.*` names.

---

### Pattern 3: `/health` Endpoint Convention for Long-Running Python Services (#342)

**Summary**: Every long-running Python service MUST expose `GET /health`. The endpoint returns HTTP 200 with a JSON body for healthy state and HTTP 503 for degraded state. Since `data/substrate-atlas.yml` lists no live services, this is a convention to adopt when services are introduced.

**Liveness vs readiness distinction** (from Kubernetes probe conventions):
- **Liveness** (`/health/live`): Is the process running and not deadlocked? Kubernetes restarts the container if this fails. Use only for unrecoverable failure detection.
- **Readiness** (`/health/readiness`): Is the process accepting traffic? Kubernetes removes the pod from load balancers if this probe fails. Use for service warm-up, dependency checks.
- **Combined** (`/health`): Single endpoint for deployments not using Kubernetes probes; returns the union signal (healthy = both live and accepting traffic).

**Minimal FastAPI /health endpoint**:

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import time

app = FastAPI()
_start_time = time.time()

@app.get("/health")
async def health() -> JSONResponse:
    uptime_s = int(time.time() - _start_time)
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "uptime_s": uptime_s,
            "checks": {
                "database": "ok",      # replace with real dependency check
                "model_loaded": True,
            }
        }
    )
```

**Response schema** (canonical minimal):
```json
{
  "status": "healthy" | "degraded" | "unhealthy",
  "uptime_s": 123,
  "checks": { "<dependency>": "ok" | "error" }
}
```

**AGENTS.md integration**: The `AGENTS.md § Async Process Handling` service readiness check table specifies `curl -sf http://localhost:<port>/health` as the canonical check command with success signal `exit 0`. The `/health` endpoint is the structural enabler for that pattern — agents gate `await_terminal` loops on a healthy `/health` response rather than on fixed `sleep` intervals. This implements **Local Compute-First** ([MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first)): readiness checks run locally (no external call), minimizing redundant polling tokens.

**Canonical example**: Ollama readiness check (from `AGENTS.md § Async Process Handling`):
```bash
curl -sf http://localhost:11434/ | grep "Ollama is running"
```
The `/health` convention generalizes this pattern to any local Python service — replacing service-specific checks with a uniform `GET /health → {status: healthy}` contract.

**Anti-pattern**: Using a fixed `sleep 10` before proceeding after service launch. A `sleep` hard-codes an assumption about startup time. A service that starts in 2 seconds wastes 8 seconds every invocation; a service that takes 15 seconds causes silent downstream failures. The `/health` endpoint converts startup time uncertainty into a deterministic observable.

---

### Pattern 4: Slow-Error Discovery via Deferred-Feedback Detection (#346)

**Summary**: Errors in token-heavy pipelines manifest slowly — the failure signal arrives long after the error occurred. Three heuristics convert deferred signals into early warnings: (1) span duration exceeds the AGENTS.md timeout ceiling for the operation type, (2) output token count approaches or exceeds the configured `gen_ai.request.max_tokens` ceiling, and (3) output entropy is anomalously low (repetition, truncation artefacts). All three are computable from span attributes without additional LLM calls.

**Why errors are slow to discover in agent workflows**:
- **Deferred feedback**: A Synthesizer agent receives compressed Scout output that omits failure signals. The Synthesizer produces a plausible-looking draft. The failure surfaces only at the Review stage — 2 agent delegations later.
- **Compressed outputs**: AGENTS.md § Focus-on-Descent / Compression-on-Ascent mandates ≤300-token subagent returns. A failing agent compresses its output, dropping error signals. The executive receives a compact summary with no indication of the underlying failure.
- **Token-ceiling breach as proxy for failure**: An LLM response that hits `max_tokens` was cut off. Truncated output passed downstream without a truncation signal causes silent downstream failures — the next agent processes incomplete data as if it were fully formed.

**Heuristics** (all computable from span attributes):

| Signal | Attribute | Threshold | Interpretation |
|---|---|---|---|
| Latency overrun | span duration | > ceiling from `AGENTS.md § Async Process Handling` | API backoff, retry, or model overload |
| Token-ceiling breach | `gen_ai.usage.output_tokens` ≥ `gen_ai.request.max_tokens` | ≥ 98% of ceiling | Response truncated — verify completeness |
| Retry accumulation | retry count on span | > 1 | Transient failure hidden inside apparent success |
| Error finish reason | `gen_ai.response.finish_reasons` contains `max_tokens` or `error` | any error value | Explicit truncation or provider-side error |

**Integration with L1/L2 validation** (from `docs/research/agent-standardization-patterns.md` Pattern 3): Span attribute checks are an L1 rule-based gate (< 5 ms). Implement as a `_check_span_health(span_data: dict) -> list[str]` function that returns gap messages for each failing heuristic. This follows the same frozenset + hard-fail pattern already in `scripts/validate_agent_files.py`.

**Canonical example**:

```python
def _check_span_health(span_data: dict) -> list[str]:
    """L1 gate: check span attributes for slow-error signals. Returns gap list."""
    gaps = []
    input_tok = span_data.get("gen_ai.usage.input_tokens", 0)
    output_tok = span_data.get("gen_ai.usage.output_tokens", 0)
    max_tok = span_data.get("gen_ai.request.max_tokens")
    finish = span_data.get("gen_ai.response.finish_reasons", [])

    if max_tok and output_tok >= int(max_tok * 0.98):
        gaps.append(f"output_tokens {output_tok} ≥ 98% of max_tokens {max_tok} — likely truncated")
    if "max_tokens" in finish or "length" in finish:
        gaps.append(f"finish_reason indicates truncation: {finish}")
    return gaps
```

**Anti-pattern**: Using end-of-session token counts as the sole signal for slow errors. A session summary reporting `tokens spent: 21,000 vs planned 15,000` tells you nothing about which span caused the overrun or whether any output was truncated. Without span-level attribution (as documented in `docs/research/ai-workload-observability.md` Pattern 3), the 40% overrun is invisible during execution and only becomes visible after cost occurs. This is the **hidden technical debt** failure mode (Sculley et al., 2015).

---

## 4. Recommendations

### R1 — Adopt OTel Python SDK LLM Span Instrumentation (Issue #334)

Add `opentelemetry-api`, `opentelemetry-sdk`, and `opentelemetry-exporter-otlp-proto-grpc` to `pyproject.toml` optional extras (`[project.optional-dependencies] observability = [...]`). Create `scripts/_telemetry.py` implementing the `_build_exporter()` factory and `tracer` singleton. Wrap all LLM API calls in `with tracer.start_as_current_span("llm.call")`. Default: stdout JSONL via `ConsoleSpanExporter`. Upgrade path: set `OTEL_EXPORTER_OTLP_ENDPOINT` to route to any OTLP-compatible backend without code changes.

### R2 — Standardize on GenAI Semantic Convention Attributes (Issue #369)

Install `opentelemetry-semantic-conventions`. Set `gen_ai.system` (backward compat) and `gen_ai.provider.name` (spec v1.36.0+) on every LLM span. Require `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` as mandatory span attributes; `gen_ai.request.temperature`, `gen_ai.response.finish_reasons` as recommended. Add a CI lint check (extend `scripts/validate_synthesis.py` or a new script) that rejects LLM call spans missing the four mandatory attributes.

### R3 — Adopt `/health` Endpoint Convention for Future Services (Issue #342)

Document the `/health` response schema in `docs/guides/service-conventions.md` (to be created). Require all new long-running Python services to implement `GET /health` returning the canonical `{status, uptime_s, checks}` JSON. Update `AGENTS.md § Async Process Handling` check table to reference the guide. This establishes the structural contract before any live services exist — **Endogenous-First** ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)): encode the pattern in the substrate before it is needed.

### R4 — Implement Slow-Error Detection via Span Health Checks (Issue #346)

Create `scripts/_telemetry.py::check_span_health()` as an L1 gate after every LLM span closes. Emit structured warnings (not silent) for: token-ceiling breach ≥ 98%, `finish_reason` containing `max_tokens` or `error`, span duration > operation ceiling from `AGENTS.md § Async Process Handling`. Integrate with the `session-retrospective` skill at sprint close: any session with ≥1 slow-error signal triggers a post-session attribution run per `docs/research/ai-workload-observability.md` Recommendation 3 (profile hidden technical debt via retry attribution).

---

## 5. Sources

### Endogenous Sources

- `docs/research/ai-workload-observability.md` — prior synthesis covering OTel distributed tracing for AI systems, GenAI attribute recommendations, and invisible token debt patterns (Pattern 3). Direct predecessor to this document.
- `AGENTS.md § Async Process Handling` — timeout ceilings and service readiness check table; directly informs slow-error latency thresholds.
- `docs/research/agent-standardization-patterns.md` Pattern 3 — L1/L2 validation pipeline (< 5 ms rule-based gate + classifier-assisted semantic gate); informs the `_check_span_health()` design.
- `data/substrate-atlas.yml` — confirms no live services exist; establishes that a collector endpoint is not required (Option C: pluggable exporter posture).
- `scripts/validate_agent_files.py` — reference implementation of the frozenset allowlist + hard-fail gap-accumulation pattern used in span health check design.

### External Sources

- OpenTelemetry Project. (2026). *Semantic conventions for generative client AI spans*. https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/ — Defines all `gen_ai.*` span attributes, span name convention, span kind. Fetched 2026-03-26.
- OpenTelemetry Project. (2026). *Semantic conventions for generative AI systems*. https://opentelemetry.io/docs/specs/semconv/gen-ai/ — Top-level GenAI semconv index; semconv stability opt-in via `OTEL_SEMCONV_STABILITY_OPT_IN`. Fetched 2026-03-26.
- OpenTelemetry Project. (2026). *Python manual instrumentation*. https://opentelemetry.io/docs/languages/python/instrumentation/ — `tracer.start_as_current_span()` pattern, `ConsoleSpanExporter` setup, `BatchSpanProcessor`. Fetched 2026-03-26.
- OpenTelemetry Project. (2026). *Python getting started*. https://opentelemetry.io/docs/languages/python/getting-started/ — `--traces_exporter console` flag; stdout JSONL output format. Fetched 2026-03-26.
- Kubernetes Project. (2026). *Configure Liveness, Readiness and Startup Probes*. https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ — Liveness vs readiness probe semantics; `/health` endpoint HTTP contract. Fetched 2026-03-26.
- OpenTelemetry Project. (2026). *Deploy the Collector*. https://opentelemetry.io/docs/collector/deployment/ — Agent and gateway deployment patterns; OTLP endpoint routing. Fetched 2026-03-26.
- Sculley, D., et al. (2015). "Hidden Technical Debt in Machine Learning Systems." *NeurIPS 2015*. https://proceedings.neurips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html — Invisible retry accumulation as hidden debt; cited in `ai-workload-observability.md` Pattern 3.

---

## Cross-References

- **MANIFESTO.md**: Endogenous-First (§1) — encode instrumentation patterns in the substrate before live services require them; read existing docs before reaching outward.
- **MANIFESTO.md**: Algorithms-Before-Tokens (§2) — span instrumentation makes token spend deterministically observable per call, eliminating post-hoc guesswork; `_check_span_health()` is a < 5 ms rule gate, not a secondary LLM call.
- **MANIFESTO.md**: Local-Compute-First (§3) — `ConsoleSpanExporter` default requires no external collector; `/health` endpoint readiness checks run locally.
- Related: `rate-limit-resilience` skill, `phase-gate-sequence` skill, `docs/research/ai-workload-observability.md`
