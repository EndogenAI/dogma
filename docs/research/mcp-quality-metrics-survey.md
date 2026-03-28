---
title: "MCP Quality Metrics Framework — Survey and Recommendations"
status: Final
closes_issue: 495
research_question: "What metrics framework should govern quality assurance for MCP tool calls in the dogma project, and how can qualitative usability constructs be operationalized as quantifiable thresholds?"
hypothesis: "A unified quality scorecard combining OTel MCP semantic conventions (latency/error surface) with RAGAS faithfulness metrics (semantic surface) and a Nielsen-inspired ordinal severity rubric (defect surface) provides a comprehensive, Local-Compute-First compatible quality framework for dogma's MCP tools."
recommendations:
  - id: rec-mcp-quality-metrics-survey-001
    title: "Instrument mcp_server/dogma_server.py with OTel spans per MCP Semconv v1.40.0"
    status: accepted
    linked_issue: 495
    decision_ref: ""
  - id: rec-mcp-quality-metrics-survey-002
    title: "Adopt DeepEval (not LangSmith or Braintrust) as the primary eval harness"
    status: accepted
    linked_issue: 495
    decision_ref: ""
  - id: rec-mcp-quality-metrics-survey-003
    title: "Implement scripts/capture_mcp_metrics.py and scripts/report_mcp_metrics.py"
    status: accepted
    linked_issue: 495
    decision_ref: ""
  - id: rec-mcp-quality-metrics-survey-004
    title: "Apply quality scorecard acceptance criteria thresholds (faithfulness >=0.80, error_rate <=5%)"
    status: accepted
    linked_issue: 495
    decision_ref: ""
  - id: rec-mcp-quality-metrics-survey-005
    title: "Implement CI phase gate: fail if faithfulness <0.75 OR tool_error_rate >5% per 100 calls"
    status: accepted
    linked_issue: 494
    decision_ref: ""
  - id: rec-mcp-quality-metrics-survey-006
    title: "Run RAGAS evaluation on a 5% weekly stratified sample"
    status: accepted
    linked_issue: 496
    decision_ref: ""
  - id: rec-mcp-quality-metrics-survey-007
    title: "Use UMUX-Lite as agent-facing quality perception proxy (target equivalent SUS >=68)"
    status: accepted
    linked_issue: 495
    decision_ref: ""
  - id: rec-mcp-quality-metrics-survey-008
    title: "Hard constraint: do not implement LangSmith or Braintrust integrations"
    status: accepted
    linked_issue: 495
    decision_ref: ""
---

# MCP Quality Metrics Framework — Survey and Recommendations

## Executive Summary

This document synthesizes Phase 2A research findings across three domains — HCD/HCI qualitative quantification frameworks, MCP-specific QA/evaluation tooling, and existing dogma scripting gaps — into a unified quality metrics framework for MCP tool calls. The central finding is that the hypothesis holds: OTel MCP semantic conventions, RAGAS faithfulness scoring, and a Nielsen-adapted ordinal severity rubric constitute a comprehensive, multi-surface quality profile (`{latency, error_rate, faithfulness, answer_relevance, context_precision, severity_level}`) that is fully Local-Compute-First compatible. Critically, no single existing framework covers all three surfaces; the cross-domain combination is the novel contribution. The primary recommendation is to instrument `mcp_server/dogma_server.py` with OTel per-span decorators, integrate DeepEval as the primary eval harness, and implement `scripts/capture_mcp_metrics.py` and `scripts/report_mcp_metrics.py` as the capture/reporting layer — with a CI gate that fails any phase where faithfulness drops below 0.75 or tool error rate exceeds 5% across the last 100 calls.

---

## Hypothesis Validation

### H1 — OTel MCP Semconv Covers the Latency/Error Surface

**Validated.** OpenTelemetry MCP Semantic Conventions (v1.40.0, Development status) define `mcp.server.operation.duration` (Histogram, seconds) and `mcp.client.session.duration` (Histogram) as the canonical latency signals. The `error.type=tool_error` span attribute fires when `isError=true` on the MCP tool response, giving a direct, spec-compliant error surface. The `gen_ai.operation.name=execute_tool` span attribute enables per-tool-call isolation. Context propagation via `params._meta.traceparent` enables distributed trace correlation without additional instrumentation overhead.

Gap confirmed: `mcp_server/dogma_server.py` currently has zero OTel instrumentation. `emit_otel_metrics.py` covers token counts only; the tool-call quality surface is entirely unobserved.

### H2 — RAGAS Covers the Semantic/Faithfulness Surface

**Validated.** RAGAS (Es et al., 2023) is reference-free and operates on `{question, answer, contexts}` triples without requiring ground-truth labels. Its three primary metrics — Faithfulness (0–1), Answer Relevance (0–1), and Context Precision (0–1) — map directly to the MCP tool-call output quality concerns: does the tool response accurately reflect retrieved context (faithfulness), does it address the actual query (answer relevance), and was the correct context retrieved in the first place (context precision)? The existing dogma corpus has already validated RAGAS at `docs/research/local-rag-adoption-patterns.md` and established accept thresholds of faithfulness ≥0.80 and recall ≥0.75. No new external validation is required to adopt.

Gap confirmed: no RAGAS integration script exists in `scripts/` (grep of scripts/ confirms zero Python matches).

### H3 — Nielsen-Inspired Ordinal Rubric Covers the Defect Surface

**Validated with adaptation.** The Nielsen Severity Scale (0–4) provides an industry-standard ordinal defect vocabulary: frequency × impact × persistence, scored by ≥3 independent raters. No equivalent rubric exists for agent task completion quality (confirmed gap in Domain A findings). The cross-domain synthesis resolves this gap: the four-level MCP severity mapping (0=clean execution, 1=latency deviation, 2=incomplete/parseable output, 3=hallucination/factual error, 4=`isError=true`) preserves the Nielsen semantics while fitting the MCP tool-call lifecycle. The OTel `error.type` attribute is the instrumentable proxy for severity-4 events; RAGAS faithfulness below 0.80 is the instrumentable proxy for severity-3 events. This bridges the two frameworks without requiring a new rater panel.

### H4 — The Combined Framework Is Local-Compute-First Compatible

**Validated.** DeepEval (Apache 2.0, 14.3k GitHub stars) offers first-class MCP Metrics support, a Pytest-like `@observe` decorator API, per-span scoring, and is fully local-compatible. RAGAS is pip-installable and runs locally against any LLM endpoint. OTel is infra-level; `opentelemetry-sdk` is a pure-Python local dependency. No component of the recommended framework requires LangSmith, Braintrust, or any cloud-hosted eval service.

---

## Pattern Catalog

### **Canonical example**: OTel + RAGAS Per-Tool-Call Quality Profile

**Context**: A dogma MCP server handles tool calls from agent workflows. Each call produces a response that may be evaluated for latency, correctness, and semantic quality. No single framework captures all three dimensions; integrating them at the span level gives a full per-call record.

**Solution**: Instrument each `execute_tool` OTel span with the following attribute set:

```python
# At span open
span.set_attribute("gen_ai.tool.name", tool_name)
span.set_attribute("gen_ai.operation.name", "execute_tool")

# At span close — latency is automatic via Histogram
if response.isError:
    span.set_attribute("error.type", "tool_error")

# Post-call RAGAS evaluation (async, sampled at 5%)
ragas_scores = evaluate(
    dataset=Dataset.from_list([{
        "question": tool_input,
        "answer": tool_output,
        "contexts": retrieved_context,
    }]),
    metrics=[faithfulness, answer_relevance, context_precision],
)
span.set_attribute("ragas.faithfulness", ragas_scores["faithfulness"])
span.set_attribute("ragas.answer_relevance", ragas_scores["answer_relevance"])
span.set_attribute("ragas.context_precision", ragas_scores["context_precision"])
```

The resulting per-call record is `{latency_s, error_rate, faithfulness, answer_relevance, context_precision}` — a five-dimensional quality profile.

**Evidence**: OTel MCP Semconv v1.40.0 defines the span structure; RAGAS (Es et al., 2023, arXiv:2309.15217) defines the semantic metrics; integration pattern derived from DeepEval `@observe` decorator documentation.

**Citation**: OpenTelemetry MCP Semconv (https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/); RAGAS (arXiv:2309.15217); DeepEval (https://github.com/confident-ai/deepeval)

---

### **Canonical example**: Nielsen-to-MCP Severity Mapping

**Context**: HCI practitioners use the Nielsen Severity Scale (0–4) to communicate defect seriousness without requiring numerical performance data. MCP tool calls exhibit analogous defect gradations — from clean executions through total failures — but no standard vocabulary existed prior to this survey for describing them.

**Solution**: Map Nielsen levels to MCP tool-call outcomes as follows:

| Nielsen Level | Original Meaning | MCP Tool-Call Equivalent | Instrumentation Proxy |
|---|---|---|---|
| 0 | Not a usability problem | Clean execution; response structurally valid and semantically faithful | `error.type` absent; `ragas.faithfulness ≥ 0.80` |
| 1 | Cosmetic — fix if time permits | Latency deviation: `mcp.server.operation.duration` outlier (>P95) but correct output | Duration Histogram P95 breach |
| 2 | Minor — low priority fix | Incomplete but parseable output; tool returned a partial result the caller can still use | `ragas.faithfulness` 0.65–0.79; no `isError` |
| 3 | Major — important to fix | Hallucination or factual error; output structurally valid but semantically wrong | `ragas.faithfulness < 0.65` |
| 4 | Catastrophe — must fix before release | `isError=true`; tool failed to execute; caller cannot proceed | `error.type=tool_error` |

This mapping is scored on the same ordinal scale across ≥3 independent raters (using RAGAS automated scoring as Rater 1, DeepEval task completion as Rater 2, and OTel error flag as Rater 3). The mean severity per tool per evaluation window provides an auditable severity trend.

**Evidence**: Nielsen Severity Scale (Nielsen, 1994 — frequency × impact × persistence); cross-domain synthesis with OTel MCP Semconv error surface and RAGAS faithfulness thresholds from dogma corpus (`docs/research/local-rag-adoption-patterns.md`).

**Citation**: Nielsen, J. (1994). Usability Engineering. Morgan Kaufmann; OTel MCP Semconv v1.40.0; dogma corpus `docs/research/local-rag-adoption-patterns.md`

---

### **Anti-pattern**: Adopting Cloud-Hosted Eval Services (LangSmith / Braintrust) for MCP Quality Measurement

**Context**: LangSmith (LangChain) and Braintrust are polished, well-documented eval platforms with native LLM tracing and scoring dashboards. They are commonly recommended for LLM/agent quality measurement and appear prominently in Domain B survey results.

**Problem**: Both platforms are cloud-hosted and require exporting tool-call inputs, outputs, and retrieved context to external servers. This violates the [MANIFESTO.md §3 Local-Compute-First](../../MANIFESTO.md#3-local-compute-first) axiom: sensitive agent context (user queries, retrieved documents, proprietary schema) must not leave the local compute boundary without explicit authorization. In addition, both platforms introduce a vendor-lock dependency (cf. AI Platform Lock-In Risks research) — any pricing change, acquisition, or ToS update immediately affects the entire quality measurement pipeline.

**Solution**: Use DeepEval (Apache 2.0) as the primary eval harness and RAGAS with a local model endpoint for faithfulness scoring. Both run entirely within the local environment. OTel exports via the `opentelemetry-sdk` to a local collector (e.g., Jaeger or an in-process exporter). No eval data leaves the machine.

**Evidence**: Domain B survey confirms DeepEval has first-class MCP Metrics support and is local-compatible. LangSmith and Braintrust are explicitly cloud-only (no local eval mode at time of survey). Local-Compute-First axiom is a foundational constraint, not an optional preference.

**Citation**: MANIFESTO.md §3 Local-Compute-First; DeepEval (https://github.com/confident-ai/deepeval); `docs/research/ai-platform-lock-in-risks.md`

---

## Recommendations

1. **Instrument `mcp_server/dogma_server.py` with OTel spans per MCP Semconv v1.40.0.** Add `opentelemetry-sdk` to project dependencies. Wrap each `execute_tool` handler with a span that sets `gen_ai.tool.name`, `gen_ai.operation.name=execute_tool`, and `error.type=tool_error` when `isError=true`. Record `mcp.server.operation.duration` as a Histogram. This is the prerequisite for all other metric collection; zero other recommendations are actionable without it. Target: all tools in `dogma_server.py` instrumented before Phase 4 begins.

2. **Adopt DeepEval (not LangSmith or Braintrust) as the primary eval harness.** Install via `uv add deepeval`. Use the `@observe` decorator on MCP tool handlers to capture per-span scoring. Justification: DeepEval is Apache 2.0, Local-Compute-First compatible, has ≥14.3k GitHub stars indicating community stability, and provides first-class MCP Metrics support. LangSmith and Braintrust are cloud-hosted and violate MANIFESTO.md §3; they must not be adopted for this framework.

3. **Implement `scripts/capture_mcp_metrics.py` and `scripts/report_mcp_metrics.py` as the capture/reporting layer.** `capture_mcp_metrics.py` should: (a) consume OTel span data from a local collector or in-process exporter, (b) run RAGAS evaluation on a 5% random sample of tool calls (matching the existing corpus recommendation at `docs/research/local-rag-adoption-patterns.md`), and (c) write results to `.cache/mcp-metrics/YYYY-MM-DD.jsonl`. `report_mcp_metrics.py` should: read the jsonl store and emit a Markdown summary with per-tool severity distribution, RAGAS scorecard, and trend delta vs. prior week. Both scripts require tests in `tests/test_capture_mcp_metrics.py` and `tests/test_report_mcp_metrics.py` per the Testing-First Requirement in AGENTS.md.

4. **Apply the following metric thresholds as the quality scorecard acceptance criteria:**

   | Metric | Threshold | Rationale |
   |---|---|---|
   | `ragas.faithfulness` | ≥ 0.80 (accept) / 0.65–0.79 (warn) / <0.65 (fail) | Validated at `docs/research/local-rag-adoption-patterns.md`; Nielsen severity-3 boundary |
   | `ragas.answer_relevance` | ≥ 0.75 | Matched to existing recall ≥0.75 corpus threshold |
   | `ragas.context_precision` | ≥ 0.70 | SPACE framework precision benchmark (>70% specific claims) |
   | `mcp.server.operation.duration` P95 | ≤ 2.0 s baseline; Nielsen severity-1 alert at P95 breach | Proposed starting threshold; adjust per tool after 4 weeks of baseline data |
   | `tool_error` rate | ≤ 5% per 100 calls | Nielsen severity-4 events; any rate above 5% indicates a systemic failure mode requiring immediate intervention |
   | DeepEval task completion score | ≥ 0.75 | Aligns with RAGAS faithfulness accept threshold; provides a second independent rater |
   | Nielsen/MCP mean severity | ≤ 1.5 per evaluation window | Average over ≥3 raters; analogous to SUS mean ≥68 as "acceptable" |

5. **Implement a CI phase gate that fails any phase where faithfulness < 0.75 OR `tool_error` rate > 5% across the last 100 calls.** The gate should be implemented in `scripts/check_phase_gate.py` (extend the existing script) or as a new `scripts/check_mcp_quality_gate.py`. The gate reads from `.cache/mcp-metrics/` and exits 1 if either threshold is breached. This gate must run before any Phase 3 (schema design), Phase 4 (implementation), or Phase 5 (baseline capture) phase begins, following the sprint phase ordering constraints in AGENTS.md.

6. **Run RAGAS evaluation on a 5% weekly sample** (not every call). Rationale: RAGAS evaluation incurs model inference cost proportional to context length. Sampling at 5% per week with stratified sampling across tool types provides statistically representative coverage while keeping evaluation overhead below 10% of total token spend. This matches the existing dogma corpus recommendation at `docs/research/local-rag-adoption-patterns.md`. The sample seed must be stored to allow reproducibility audits.

7. **Use UMUX-Lite as the agent-facing quality perception proxy** to resolve the usability surface gap. At each weekly evaluation, compute UMUX-Lite from the two-item proxy (`SUS = 0.65 × ((item1+item2−2)×(100/12)) + 22.9`, Cronbach's α=0.86, r=0.83 with SUS). Agent-facing "items" are operationalized as: Item 1 = mean DeepEval task completion score rescaled 1–7; Item 2 = (1 − mean error_rate) rescaled 1–7. Target: UMUX-Lite equivalent ≥ 68 (SUS mean baseline) — below this, the MCP tool suite is assessed as providing sub-standard agent interaction quality. This closes the identified gap: no Nielsen-equivalent rubric existed for agent task completion quality prior to this framework.

8. **Do not implement LangSmith or Braintrust integrations.** This is a hard constraint, not a preference. Cloud-hosted eval services fail the MANIFESTO.md §3 Local-Compute-First criterion and the Ethical Values Procurement Rubric's Reversibility criterion (cannot be disabled without losing all historical eval data). Any script or agent file proposing cloud eval service adoption must be rejected at Review.

---

## Sources

1. **OpenTelemetry MCP Semantic Conventions v1.40.0**. (2024, Development status). OpenTelemetry specification: semantic conventions for generative AI — MCP. https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/

2. **Es, S., James, J., Espinosa-Anke, L., & Schockaert, S.** (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation. arXiv:2309.15217. https://arxiv.org/abs/2309.15217

3. **Confident AI.** (2024). DeepEval: The Open-Source LLM Evaluation Framework (v1.x, Apache 2.0). GitHub. https://github.com/confident-ai/deepeval

4. **Brooke, J.** (1986). SUS — A quick and dirty usability scale. In P. W. Jordan, B. Thomas, B. A. Weerdmeester, & A. L. McClelland (Eds.), *Usability Evaluation in Industry* (pp. 189–194). Taylor & Francis.

5. **Nielsen, J.** (1994). *Usability Engineering*. Morgan Kaufmann. (Nielsen Severity Scale, Chapter 8.)

6. **Lewis, J. R., & Sauro, J.** (2009). The factor structure of the System Usability Scale. In *Human Centered Design* (pp. 94–103). Springer.

7. **Finstad, K.** (2010). The Usability Metric for User Experience. *Interacting with Computers*, 22(5), 323–327. (UMUX-Lite: α=0.86, r=0.83 with SUS, regression formula.)

8. **Dogma Corpus — local-rag-adoption-patterns.md**. RAGAS thresholds: faithfulness ≥0.80, recall ≥0.75; 5% weekly sampling recommendation. `docs/research/local-rag-adoption-patterns.md`

9. **Dogma Corpus — space-framework-strategy.md**. SPACE precision benchmark (>70% specific claims), accuracy, convergence, evidence depth. `docs/guides/space-framework-strategy.md`

10. **Dogma Corpus — frankenbrain-benchmark-spec.md**. FrankenBrAIn 4-metric process benchmark: session coherence ≥85%, handoff quality ≥75%, token spend ≤60% baseline, architectural coherence ≤3 sessions. `docs/research/frankenbrain-benchmark-spec.md`

11. **Model Context Protocol.** (2024). MCP Inspector — Interactive tool for testing MCP servers. https://modelcontextprotocol.io/docs/tools/inspector

12. **Promptfoo.** (2024). Open-source LLM eval and red-teaming framework. https://www.promptfoo.dev/

13. **MANIFESTO.md §3 — Local-Compute-First**. EndogenAI Workflows project axiom. `MANIFESTO.md`
