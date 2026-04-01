---
title: "Sprint 22 Source Note: Production-Grade Observability Patterns for Agentic LLM Pipelines"
topic: "Established patterns for production-grade observability in agentic LLM pipelines — metrics collection, structured tracing, Gen AI semantic conventions, and quality gate integration"
research_question: "What are the established patterns for production-grade observability in agentic LLM pipelines — metrics collection, structured tracing, Gen AI semantic conventions, and quality gate integration — and what does 'production-grade' mean for an OSS project of dogma's maturity?"
relevance_issue:
  - 534
  - 425
date: 2026-04-01
author: Executive Researcher
endogenous_sources_checked:
  - docs/research/ai-workload-observability.md
  - docs/research/mcp-quality-metrics-survey.md
  - docs/decisions/ADR-008-mcp-quality-metrics-framework.md
  - docs/guides/mcp-quality-metrics.md
---

# Source Note: Production-Grade Observability Patterns for Agentic LLM Pipelines

## Corpus Check (Endogenous-First)

**`docs/research/ai-workload-observability.md`** (Status: Final, closes #316) establishes the
three-layer observability model for dogma:
- **Instrumentation layer**: trace collection (OTel spans, token counts)
- **Aggregation layer**: correlation across agents
- **Presentation layer**: observable APIs and dashboards
Key finding: "40–60% of AI session latency is upstream — waiting on external API rate limits or
cached failures re-fetched repeatedly." Observability surfaces this invisible cost.

**`docs/research/mcp-quality-metrics-survey.md`** (Status: Final, closes #495) provides the
definitive MCP-specific telemetry contract:
- `mcp.server.operation.duration` (Histogram) — latency per tool call
- `mcp.client.session.duration` (Histogram) — per-session duration
- `error.type=tool_error` — tool failure signal
- `gen_ai.operation.name=execute_tool` — per-tool isolation
- `params._meta.traceparent` — context propagation without instrumentation overhead
Gap confirmed: `mcp_server/dogma_server.py` has zero OTel instrumentation as of Sprint 20.

**`docs/decisions/ADR-008-mcp-quality-metrics-framework.md`** (Status: Accepted) establishes
the threshold contract:
- Fail gate: faithfulness < 0.75 over 100-call window
- Fail gate: tool error rate > 5.0% over 100-call window
- Performance target: P95 latency ≤ 2.0s
- Accepted/deferred: OTel instrumentation (#498); capture/report (#499); DeepEval/RAGAS (#500 deferred)

**`docs/guides/mcp-quality-metrics.md`** provides the operational runbook for the capture →
report → gate workflow using `capture_mcp_metrics.py`, `report_mcp_metrics.py`,
`check_mcp_quality_gate.py`.

**Endogenous baseline**: The OTel-based MCP telemetry contract and gate thresholds are fully
specified at the design level. The implementation gap (zero instrumentation in `dogma_server.py`)
is the blocking issue for #534. This source note addresses what external evidence adds about
*production-readiness definition* and *semantic convention completeness* beyond what #495 designed.

## External Sources

### 1. OpenTelemetry — Observability Primer
**Citation**: OpenTelemetry. "Observability primer." opentelemetry.io/docs/concepts/observability-primer/ (accessed April 2026). [Cached]
**Relevance**: Canonical definition of observability signals (traces, metrics, logs) and their relationship to reliability (SLI, SLO).

**Key claims**:
- Observability: "understand a system from the outside by letting you ask questions about that system without knowing its inner workings" — the goal is answering "Why is this happening?" for unknown unknowns.
- Three signals: **Traces** (request lifecycle), **Metrics** (aggregated numeric data), **Logs** (timestamped events).
- **SLI** (Service Level Indicator): measurement from user perspective. **SLO** (Service Level Objective): reliability communicated to organization by attaching SLIs to business value.
- "An application is properly instrumented when developers don't need to add more instrumentation to troubleshoot an issue." — The completeness criterion for instrumentation.

**Critical assessment**: The "properly instrumented" completeness criterion is directly applicable to `mcp_server/dogma_server.py`. The OTel Primer provides a clear test: can a developer diagnose a tool failure without adding new instrumentation? If not, the instrumentation is incomplete. The SLI/SLO framework is the appropriate structure for dogma's quality gate thresholds (faithfulness ≥ 0.80 is an SLO; faithfulness per-call is an SLI).

### 2. OpenTelemetry — Metrics Specification
**Citation**: OpenTelemetry. "OpenTelemetry Metrics." opentelemetry.io/docs/specs/otel/metrics/ (accessed April 2026). [Cached]
**Relevance**: Authoritative spec for the OTel Metrics API and SDK design goals; provides the coupling model to other signals.

**Key claims**:
- Design goal: connect metrics to other signals via exemplars (metrics ↔ traces) and Baggage/Context enrichment.
- API serves two purposes: (1) capturing raw measurements efficiently, (2) decoupling instrumentation from SDK.
- When no SDK is included, no telemetry is collected — instrumentation is inert without a running SDK.
- Full Prometheus compatibility: OTel SDK + Collector can export in Prometheus text format.
- StatsD collection supported via OTel Collector.

**Critical assessment**: The decoupling design is critical for dogma: the `mcp_server/` instrumentation (API calls) must be separable from the SDK configuration (which backend receives the data). This means `dogma_server.py` should call OTel SDK methods; the SDK configuration (OTLP endpoint, Prometheus exporter, or local JSONL) is an environment-level concern. This architectural separation makes the instrumentation testable without a live backend.

### 3. OpenTelemetry — Generative AI Blog Post (Robbins & Molkova, 2024)
**Citation**: Robbins, D., Molkova, L. (2024). "OpenTelemetry for Generative AI." opentelemetry.io/blog/2024/otel-generative-ai/ (accessed April 2026). [Cached]
**Relevance**: Announces the GenAI semantic conventions and the first instrumentation library (Python/OpenAI); confirms the production timeline and MCP coverage.

**Key claims**:
- Two primary assets: **Semantic Conventions** (structured guidelines for telemetry data) and **Instrumentation Libraries** (automate collection for specific APIs).
- Three primary signals for GenAI: Traces (model interaction lifecycle), Metrics (request volume, latency, token counts), Events (detailed model interaction moments — user prompts and responses).
- Events use the Logs API (`emit_an_event`) — important API surface detail.
- First release targets Python/OpenAI; Anthropic conventions are defined (separately cached).

**Critical assessment**: The Events signal (capturing prompt/response details) is the highest-sensitivity data — it constitutes PII if user data is in prompts. For dogma, MCP tool call inputs are governance artifacts (not user PII), but the principle holds: log event capture should be opt-in and size-bounded. The blog confirms the instrumentation library for the OpenAI API is available; for Anthropic/Claude (dogma's actual model), the Anthropic semantic conventions are the relevant spec.

### 4. OpenTelemetry — GenAI Semantic Conventions
**Citation**: OpenTelemetry. "Semantic conventions for generative AI systems." opentelemetry.io/docs/specs/semconv/gen-ai/ (accessed March 2026). [Cached]
**Relevance**: Defines the authoritative attribute set for LLM and agent telemetry, including Anthropic-specific and MCP-specific conventions.

**Key claims**:
- Status: **Development** — these conventions are not yet stable. A `OTEL_SEMCONV_STABILITY_OPT_IN` environment variable controls migration.
- Four signal types defined: Events, Metrics, Model spans, **Agent spans** — agent spans are a first-class signal type.
- Technology-specific conventions: Anthropic, Azure AI Inference, AWS Bedrock, OpenAI.
- **MCP semantic conventions** are defined separately at `/docs/specs/semconv/gen-ai/mcp/`.
- Important migration note: instrumentations on v1.36.0 should not change their emitted version by default.

**Critical assessment**: The "Development" status is a significant risk qualifier. Dogma's OTel instrumentation in `dogma_server.py` will be written against a moving specification. The mitigation is to use the MCP semconv exactly as specified in ADR-008 (v1.40.0 explicitly versioned) and to wrap the instrumentation in a version-gated block that can be toggled via `OTEL_SEMCONV_STABILITY_OPT_IN`. The Anthropic-specific conventions are the relevant track for dogma's Claude-based pipeline.

### 5. OpenTelemetry — LLM Observability Introduction (Jain, 2024)
**Citation**: Jain, I. (2024). "An Introduction to Observability for LLM-based applications using OpenTelemetry." Grafana/OpenTelemetry Blog. opentelemetry.io/blog/2024/llm-observability/ (accessed April 2026). [Cached]
**Relevance**: Practical guide for LLM observability using the OTel + Prometheus + Jaeger + Grafana stack; provides a concrete implementation reference.

**Key claims**:
- Three observability priorities for LLMs: (1) usage/cost tracking (request count, token counts), (2) latency tracking (response time varies with input), (3) rate limiting detection (API dependency failure).
- Stack: OpenLIT for auto-instrumentation → OTel Collector → Prometheus (metrics backend) + Jaeger (traces backend) → Grafana (visualization).
- "By keeping a close eye on these aspects, you can not only save costs but also avoid hitting request limits."
- Traces are essential for RAG applications where events chain before and after LLM calls.

**Critical assessment**: For dogma's maturity level (OSS, single-maintainer, CI-gate focus), the full Prometheus + Jaeger + Grafana stack is over-engineered as a production target. The relevant subset is: OTel SDK → JSONL local exporter (already pattern-matched in `docs/metrics/`) with a Prometheus-compatible exposition format for future escalation. The `scripts/capture_mcp_metrics.py` → `.cache/mcp-metrics/tool_calls.jsonl` pipeline already implements the local-first version of this pattern.

### 6. Prometheus — Exposition Formats
**Citation**: Prometheus. "Exposition formats." prometheus.io/docs/instrumenting/exposition_formats/ (accessed April 2026). [Cached]
**Relevance**: Defines the text format for Prometheus metric exposition — the escalation path for dogma's current JSONL-based metrics capture.

**Key claims**:
- Text format: human-readable, easy to assemble, UTF-8, `\n` line endings, `text/plain` content type.
- Supported primitives: Counter, Gauge, Histogram, Summary, Untyped.
- Limitations: verbose, no integral metric contract validation, parsing cost.
- Protobuf format is available behind HTTP content negotiation for performance.
- Inception: April 2014 — extremely stable specification.

**Critical assessment**: The Prometheus text format is the natural escalation path from dogma's current JSONL capture to a standardized metrics endpoint. `scripts/report_mcp_metrics.py` could emit a `/metrics` endpoint in Prometheus text format alongside the current Markdown report — a low-cost addition that makes dogma's metrics Grafana-compatible without requiring architectural changes.

### 7. arXiv:2402.01817 — LLM-Modulo Frameworks (Kambhampati et al., 2024)
**Citation**: Kambhampati, S., et al. (2024). "LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks." ICML 2024. arXiv:2402.01817.
**Relevance**: Argues that LLMs need external verifiers in a tighter bi-directional loop — directly relevant to dogma's quality gate integration with observability.

**Key claims**:
- LLMs cannot self-verify planning steps — they require external model-based verifiers.
- LLM-Modulo Framework: LLMs generate candidates; external verifiers evaluate correctness; verified outputs feed back into the LLM.
- LLMs are "universal approximate knowledge sources" — their role is generation, not verification.
- External verifiers can themselves be acquired with LLM assistance.

**Critical assessment**: This framework maps directly to dogma's observability architecture: `mcp_server/dogma_server.py` (LLM generation) must be coupled with `scripts/check_mcp_quality_gate.py` (external verifier) in a loop. The quality gate is not just a CI artifact — it is the verifier in the LLM-Modulo sense. For #534, this means the OTel instrumentation must surface data that the gate script can consume as a verifier input.

### 8. arXiv:2310.12931 — Eureka: Human-Level Reward Design (Ma et al., 2024)
**Citation**: Ma, Y. J., et al. (2024). "Eureka: Human-Level Reward Design via Coding Large Language Models." ICLR 2024. arXiv:2310.12931.
**Relevance**: Demonstrates automated reward function design using LLMs + external evaluators — a pattern for automated quality gate refinement.

**Key claims**:
- GPT-4 generates reward functions; RL evaluates them in simulation; results feed back for evolutionary optimization.
- Outperforms expert human-engineered rewards on 83% of 29 tasks.
- Gradient-free RLHF: human inputs improve reward quality without model weight updates.
- Curriculum learning enables progressive skill acquisition (pen spinning as example).

**Critical assessment**: The Eureka pattern is aspirational for dogma: automated refinement of quality gate thresholds via LLM-generated scoring functions evaluated against ground-truth test cases. Currently out of scope for #534. The relevant near-term takeaway: quality gate thresholds should be revisited periodically based on observational data (as Eureka iterates reward functions), not fixed permanently at design time.

### 9. arXiv:2209.07858 — Red Teaming Language Models (Ganguli et al., 2022)
**Citation**: Ganguli, D., et al. (2022). "Red Teaming Language Models to Reduce Harms." arXiv:2209.07858. Anthropic.
**Relevance**: Red teaming as a structured quality and safety evaluation methodology; provides the framework for what to measure beyond default metrics.

**Key claims**:
- RLHF models become increasingly difficult to red-team at scale (finding).
- 38,961 red team attacks released as a dataset — covers offensive language, subtle harmful outputs.
- Scaling behaviors vary across model types: flat scale trend for plain LMs, decreasing vulnerability for RLHF models.
- The hardest-to-detect harmful outputs are "more subtly harmful non-violent unethical outputs" — these are not captured by binary error metrics.

**Critical assessment**: For dogma's MCP tool quality, the red teaming analogy is: do any tool calls produce outputs that satisfy the quality gate metrics (faithfulness ≥ 0.80) while still being subtly incorrect or misleading? The Nielsen severity rubric (severity 3 = hallucination) is designed to catch this, but requires human evaluation for calibration. The Anthropic red teaming methodology (structured adversarial testing) is the appropriate process for periodic quality gate calibration.

### 10. DeepMind — Specification Gaming (Krakovna et al., 2020)
**Citation**: Krakovna, V., et al. (2020). "Specification gaming: the flip side of AI ingenuity." deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity (accessed April 2026). [Cached]
**Relevance**: Observability metrics must be designed to resist gaming — the same specification gaming dynamics that apply to RL reward functions apply to LLM quality metrics.

**Key claims** (see also Task A source note — same source):
- Specification gaming: satisfying literal specification without achieving intended outcome.
- Three root causes: reward shaping errors, misspecified final outcome, reward tampering.
- Solution approach: multi-surface metrics that make gaming one dimension visible on another.

**Critical assessment**: For observability specifically: an MCP tool that achieves low latency (OTel metric passes) while returning empty or truncated tool outputs would pass the latency gate but fail faithfulness. The multi-surface design (OTel + RAGAS + Nielsen) is the observability architecture that makes gaming visible. This source confirms the architectural decision in ADR-008.

## Summary Table

| Source | Topic | Relevance | Key Contribution |
|--------|-------|-----------|-----------------|
| OTel Observability Primer | SLI/SLO framework | Very High | "Properly instrumented" completeness criterion; SLI/SLO as gate structure |
| OTel Metrics Spec | API/SDK decoupling | High | Instrumentation decoupled from backend; SDK required for emission |
| OTel GenAI Blog (Robbins/Molkova) | GenAI signal types | High | Events are opt-in; Anthropic conventions are the relevant track |
| OTel GenAI Semconv | Attribute definitions | Very High | Development status risk; MCP semconv at separate path; versioning required |
| OTel LLM Observability (Jain) | Implementation guide | High | Local JSONL → Prometheus exposition is the dogma escalation path |
| Prometheus Exposition Formats | Metrics format spec | High | Text format is the Prometheus-compatible escalation step |
| arXiv:2402.01817 (LLM-Modulo) | Quality gate theory | High | Gate script is the external verifier in the LLM-Modulo sense |
| arXiv:2310.12931 (Eureka) | Automated reward design | Medium | Thresholds should be revisited periodically, not fixed at design time |
| arXiv:2209.07858 (Red Teaming) | Safety evaluation | Medium | Red teaming as periodic quality gate calibration for subtle failures |
| DeepMind Specification Gaming | Metric gaming theory | High | Multi-surface observability makes gaming visible across dimensions |

## Critical Assessment

The external sources confirm and extend the ADR-008 design in four concrete ways:

1. **Production-readiness definition** (OTel Primer): "Properly instrumented" means no new
   instrumentation is needed to diagnose a failure. The current state (zero OTel in
   `dogma_server.py`) is pre-production by this definition. The implementation in #498 is the
   threshold step.

2. **Semconv instability risk** (OTel GenAI Semconv): the GenAI conventions are in Development
   status — not stable. Dogma must version-pin (v1.40.0 as specified in ADR-008) and gate
   upgrades explicitly.

3. **Escalation path** (Jain + Prometheus): the current JSONL-based metrics capture
   (`tool_calls.jsonl`) is a valid local-first observability pattern. The natural escalation is
   adding a Prometheus text format endpoint to `scripts/report_mcp_metrics.py` — this adds
   Grafana compatibility without architectural refactoring.

4. **Gate script as verifier** (LLM-Modulo): `scripts/check_mcp_quality_gate.py` is not just
   a CI artifact — it is the external verifier in the LLM-Modulo sense. Its thresholds must
   be maintainable (periodically revisited) and its output must be consumable by the pipeline
   (structured JSON exit code, not just prose).

## Project Relevance

For `#534` (OTel instrumentation in `dogma_server.py`) and `#425` (quality gate integration):
- **Implement** OTel span decorators in `dogma_server.py` per ADR-008 attribute set, version-pinned
  to v1.40.0 of the GenAI semconv MCP spec. Use the API/SDK decoupling pattern: instrumentation
  code calls OTel SDK methods; SDK configuration (exporter target) is environment-level.
- **Add** `OTEL_SEMCONV_STABILITY_OPT_IN` support to allow migration when the spec reaches stable.
- **Accept** JSONL local exporter as the current production-grade backend; add Prometheus text
  format exposition as a follow-on (#424 escalation path).
- **Add** structured JSON output to `scripts/check_mcp_quality_gate.py` (PASS/FAIL + dimension
  scores) to enable LLM-Modulo-style pipeline integration.
- **Establish** a semi-annual quality gate threshold review process (Eureka-inspired) using
  accumulated `tool_calls.jsonl` data.
