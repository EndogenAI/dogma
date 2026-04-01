---
title: "Sprint 22 Baseline Stabilization: Research Synthesis"
status: Final
closes_issue: 497
sprint: 22
date: 2026-04-01
author: Executive Researcher
sources:
  - docs/research/sources/sprint-22-independent-optimization-effects.md
  - docs/research/sources/sprint-22-instruction-format-efficiency.md
  - docs/research/sources/sprint-22-metrics-kpi-interpretation.md
  - docs/research/sources/sprint-22-canonical-scripts-friction.md
  - docs/research/sources/sprint-22-observability-patterns.md
recommendations:
  - id: rec-sprint22-001
    title: "Treat optimization technique combinations as interaction experiments, not linear stacks (#497)"
    status: accepted
    linked_issue: 497
    decision_ref: ""
  - id: rec-sprint22-002
    title: "Retain hybrid Markdown+XML as canonical agent instruction format; enforce via validate_agent_files.py (#491)"
    status: accepted
    linked_issue: 491
    decision_ref: ""
  - id: rec-sprint22-003
    title: "Add noise-floor calibration test set to scripts/check_mcp_quality_gate.py (#482)"
    status: accepted
    linked_issue: 482
    decision_ref: ""
  - id: rec-sprint22-004
    title: "Implement deprecation convention and discoverability audit for scripts/ directory (#529)"
    status: accepted
    linked_issue: 529
    decision_ref: ""
  - id: rec-sprint22-005
    title: "Implement OTel instrumentation in dogma_server.py per ADR-008, version-pinned to semconv v1.40.0 (#534)"
    status: accepted
    linked_issue: 534
    decision_ref: ADR-008-mcp-quality-metrics-framework
  - id: rec-sprint22-006
    title: "Add structured JSON output to check_mcp_quality_gate.py for LLM-Modulo gate integration (#425)"
    status: accepted
    linked_issue: 425
    decision_ref: ""
  - id: rec-sprint22-007
    title: "Add Prometheus text format exposition to scripts/report_mcp_metrics.py (#534)"
    status: accepted
    linked_issue: 534
    decision_ref: ""
---

# Sprint 22 Baseline Stabilization: Research Synthesis

## Executive Summary

Across five source notes covering optimization interaction effects, instruction format efficiency,
KPI interpretation, scripts repository maintenance, and LLM observability, the central cross-cutting
finding is that **no dogma quality improvement is additive in isolation — every optimization
interacts with others, and every metric can be gamed by an agent with sufficient capability**.
The multi-surface architecture that dogma has already adopted (OTel + RAGAS + Nielsen + Programmatic-First)
is architecturally correct but has three implementation gaps: zero OTel instrumentation in
`dogma_server.py`, a `scripts/` deprecation/discoverability gap that grows with every new script,
and quality gate thresholds that lack a calibration baseline. The instruction format baseline is
confirmed (hybrid Markdown+XML is optimal for Claude agents); the optimization interaction evidence
confirms that combining prompt techniques requires controlled experimentation, not additive assumption.
The most urgent implementation deliverable is OTel instrumentation in `dogma_server.py` (#534), which
unblocks both the quality gate (#425) and the baseline metrics capture (#482).

---

## Hypothesis Validation

| Hypothesis | Issue | Status | Evidence Summary |
|-----------|-------|--------|-----------------|
| H1: Prompt optimization techniques stack additively | #497 | **REFUTED** | Anthropic, Weng (2023), OpenAI all document non-linear interactions between few-shot, CoT, XML, and output format constraints. "Chain of thought prompting can interfere with output structure requirements" (Anthropic). Interactions are not rare edge cases — they are the default. |
| H2: Hybrid Markdown+XML is the optimal instruction format for Claude agents | #491 | **CONFIRMED** | Anthropic purpose-based selector confirmed. Liu et al. (2023) "Lost in the Middle" quantifies recency/primacy bias — XML wrappers anchor critical content. Existing `docs/research/agents/xml-agent-instruction-format.md` (ADOPTED) is the definitive endogenous validation. |
| H3: The multi-surface KPI framework (OTel + RAGAS + Nielsen) is architecturally sound | #482 | **PARTIAL** | Framework is architecturally correct. Two gaps: (1) no noise-floor calibration control set (Anthropic Persuasiveness methodology); (2) specification gaming guard must be explicitly re-evaluated as agent capabilities improve (DeepMind Specification Gaming). |
| H4: Dogma's `scripts/` directory follows canonical maintenance practices | #529 | **PARTIAL** | Current practices (docstrings, `uv run`, verb-prefix naming, README catalog) are confirmed best practice. Three concrete gaps: no deprecation convention, no discoverability audit, no `--dry-run` coverage audit. Concrete AI Safety taxonomy (Amodei et al., 2016) validates existing guardrails. |
| H5: OTel MCP semconv provides production-grade observability for dogma | #534, #425 | **PARTIAL** | The OTel spec is correct and the ADR-008 design is validated. Two gaps: (1) zero OTel instrumentation in `dogma_server.py` (pre-production by the OTel Primer "properly instrumented" criterion); (2) GenAI semconv is in Development status — version-pinning to v1.40.0 is required to avoid breaking changes. |

---

## Pattern Catalog

### Cluster 1: Optimization Interaction Effects (#497)

**Canonical example**: Anthropic documents that "Chain of thought prompting can interfere with
output structure requirements" — when an agent must produce structured JSON output, enabling CoT
reasoning tokens competes for context space and the model prioritizes format compliance over
full reasoning. An agent optimized for both CoT and JSON output simultaneously may produce
lower-quality reasoning than one optimized for CoT alone, despite the naive expectation of
additive improvement.

**Anti-pattern**: Applying few-shot examples + XML structure + CoT + output format constraints
simultaneously and measuring combined output improvement against a single baseline, then attributing
delta to each technique individually. This violates the interaction evidence: each combination must
be tested as a distinct condition, not decomposed into independent effects post-hoc.

**Design implication for dogma**: Sprint 22 optimization experiments (#497) must be designed as
factorial experiments (or at minimum registered sequentially with stable baselines between
additions) — not as cumulative stack-and-measure sessions.

---

### Cluster 2: Instruction Format Efficiency (#491)

**Canonical example**: The hybrid Markdown + XML format in dogma `.agent.md` files correctly
implements the Anthropic purpose-based selector: Markdown headings give IDE/human navigation;
XML wrappers (`<context>`, `<instructions>`, `<constraints>`, `<output>`) give the Claude model
semantic signal. This is confirmed by `docs/research/agents/xml-agent-instruction-format.md`
(ADOPTED) and the external Anthropic guidance.

**Anti-pattern**: Using full Markdown formatting (headers, bold, bullet lists) for simple
single-purpose worker agents that perform one narrow task. "Avoid heavy formatting for
conversational or simple tasks — it can make responses feel overly formal and reduce
helpfulness" (Anthropic). Plain prose bodies are correct for sub-agents that receive narrow,
structured delegations — not all agents need the full hybrid format.

**Design implication for dogma**: `validate_agent_files.py` should enforce hybrid format only
for executive-tier agents (which have multiple BDI sections). Sub-agents with a single
`<instructions>` block may legitimately omit the hybrid structure without compliance failure.

---

### Cluster 3: KPI and Metrics Interpretation (#482)

**Canonical example**: The Anthropic Persuasiveness study uses an explicit "control condition"
(indisputable factual claims) to quantify the measurement noise floor — the degree to which
opinion changes are due to response bias rather than argument quality. This noise-floor
calibration method applied to dogma's MCP quality metrics: a set of known-correct tool calls
with pre-verified expected outputs serves as the control set. Score fluctuations larger than
the control-condition variance are signal; smaller fluctuations are noise.

**Anti-pattern**: Interpreting a drop in MCP faithfulness score from 0.83 to 0.78 as a
meaningful regression without a calibration baseline. Without a control set, this drop could
be measurement noise (sampling variation in RAGAS) rather than an actual quality degradation.
Acting on noise-level fluctuations wastes engineering time and trains false alarms.

**Design implication for dogma**: `scripts/check_mcp_quality_gate.py` should include a
"calibration run" step that executes 10–20 known-correct tool calls before each gate
evaluation, establishing the noise floor for that run. Gate triggers should require the
delta to exceed the calibration variance before failing.

---

### Cluster 4: Canonical Scripts Repository Friction (#529)

**Canonical example**: The dogma `scripts/README.md` catalog entry pattern — one line per
script with verb-prefix naming (`check_`, `validate_`, `scaffold_`, `wait_`) — is a correct
implementation of the discoverability principle. An agent can scan the catalog in a single
read, filter by verb prefix to find scripts relevant to a task, then read the docstring for
usage details. This layered-discovery pattern (catalog → docstring → `--help`) minimizes the
cognitive overhead of script discovery.

**Anti-pattern**: When a script becomes outdated or superseded, leaving it in `scripts/` with
no deprecation marker. An agent performing a pre-action lookup finds the deprecated script,
reads its docstring (which doesn't indicate deprecation), and invokes it — producing stale
output or failure. The cost is not one failed invocation; it is every future session that
encounters the script before the deprecation is discovered interactively. This is the
"zombie script" anti-pattern.

**Design implication for dogma**: Implement a two-step deprecation convention: (1) add
`# DEPRECATED: superseded by <new-script>` as line 2 of the deprecated script's docstring,
and (2) add a `sys.exit(1)` with a human-readable message on invocation. Maintain a
`scripts/DEPRECATED.md` register. This makes deprecation visible at the catalog, docstring,
and runtime layers simultaneously.

---

### Cluster 5: Observability Patterns (#534, #425)

**Canonical example**: The OTel Observability Primer's "properly instrumented" test: "an
application is properly instrumented when developers don't need to add more instrumentation
to troubleshoot an issue." Applied to `mcp_server/dogma_server.py`: if a `check_substrate`
tool call returns an unexpected result and the developer must add print statements to understand
why, the instrumentation is insufficient. The target instrumentation state is: each tool call
emits a span with `mcp.server.operation.duration`, `gen_ai.operation.name`, `error.type`
(when applicable), and sufficient event detail to replay the tool call's context — without
requiring code edits.

**Anti-pattern**: Instrumenting only the "happy path" — adding OTel spans to successful
tool calls but not to error-path branches. Error-path spans are the highest-value telemetry:
they are the signals that answer "Why is this happening?" (OTel Primer definition of
observability). An implementation that logs `error.type=tool_error` only on caught exceptions
but not on validation failures, empty responses, or timeout conditions is underinstrumenting
the error surface.

**Design implication for dogma**: The `dogma_server.py` OTel implementation (#534) must
instrument all exit paths for each tool handler (success, validation failure, timeout,
exception). The OTel span must be closed with appropriate status in all branches —
`StatusCode.ERROR` for any non-success path, not just raised exceptions.

---

## Recommendations

1. **Design optimization experiments as factorial conditions, not cumulative stacks** (#497):
   Before the next prompt optimization sprint, register a baseline session (no new techniques)
   and measure output quality on a consistent 10-case eval set. Add techniques one at a time
   with a stable interim measurement between each addition. If two techniques interact negatively,
   the sequential design will catch the interaction; a cumulative design will miss it.

2. **Add noise-floor calibration to the quality gate** (#482):
   Extend `scripts/check_mcp_quality_gate.py` to include a calibration run (10–20 known-correct
   tool calls) before each gate evaluation. Gate thresholds should be relative to the calibration
   variance, not absolute. Implement a `--calibration-set <path>` flag that accepts a JSONL
   file of (input, expected_output) pairs per tool.

3. **Implement OTel instrumentation in `dogma_server.py` per ADR-008** (#534):
   Version-pin to semconv v1.40.0. Instrument all exit paths (success + all error branches)
   for all 8 canonical MCP tools. Use API/SDK decoupling: instrumentation calls OTel SDK
   methods; SDK configuration (JSONL local exporter default, Prometheus escalation path) is
   environment-level. Add `OTEL_SEMCONV_STABILITY_OPT_IN` support for future spec migration.

4. **Add structured JSON output to `scripts/check_mcp_quality_gate.py`** (#425):
   The gate script currently emits pass/fail text. Add a machine-readable JSON output mode
   (`--output-format json`) that emits `{"pass": bool, "faithfulness": float, "error_rate": float,
   "latency_p95": float, "calibration_variance": float}`. This enables LLM-Modulo-style pipeline
   integration — the gate script becomes the external verifier that the pipeline can consume
   programmatically.

5. **Implement scripts/ deprecation convention** (#529):
   (a) Add `# DEPRECATED: superseded by <script>` as line 2 of deprecated script docstrings.
   (b) Add `sys.exit(1)` with human-readable message at the top of deprecated scripts.
   (c) Create `scripts/DEPRECATED.md` register with: original script name, date deprecated,
   superseding script, and reason. (d) Add a `check_script_conventions.py` script that enforces
   verb-prefix naming, docstring presence, and detects scripts missing from `scripts/README.md`.

6. **Add Prometheus text format exposition to `scripts/report_mcp_metrics.py`** (#534):
   Add a `--format prometheus` flag that emits the current metrics in Prometheus text format
   alongside the existing Markdown report. This is a low-cost escalation step that makes
   dogma's metrics Grafana-compatible without architectural change. Counter metrics:
   `mcp_tool_calls_total{tool}`. Histogram: `mcp_tool_call_duration_seconds{tool}`.

7. **Establish semi-annual quality gate threshold review** (#482, #425):
   Use accumulated `tool_calls.jsonl` data (90-day rolling window) to review whether the ADR-008
   thresholds (faithfulness ≥ 0.80, error rate ≤ 5%, P95 ≤ 2.0s) remain calibrated. Document
   the threshold review process in `docs/guides/mcp-quality-metrics.md` as a recurring maintenance
   step — not a one-time design decision.

---

## Open Questions

The following questions are unresolved and must be surfaced to the human before Phase 3 implementation:

**OQ-1**: Should `dogma_server.py` OTel instrumentation default to the JSONL local exporter
or the OTel Collector endpoint? The local exporter is immediately usable but requires a separate
`scripts/convert_jsonl_to_otel.py` bridge if the project ever adopts a Collector-based backend.
Starting with the Collector default (localhost:4317, no-op if not running) avoids a future
migration but adds a configuration dependency. **Human decision required before #534 implementation.**

**OQ-2**: Should the GenAI semconv Anthropic-specific track be adopted alongside the MCP track?
The OTel spec defines Anthropic-specific attributes for Claude API calls (model name, input/output
token counts, system prompts). Adopting these would add per-request Claude API telemetry alongside
MCP tool telemetry — a richer signal but more instrumentation surface. **Human decision required.**

**OQ-3**: The `scripts/` discoverability audit (Rec 5) would require renaming several non-conformant
scripts (e.g., `amplify_context.py`, `aggregate_session_costs.py`, `analyse_fleet_coupling.py`).
Renaming committed scripts breaks any external references (CI configs, docs, other scripts).
Should non-conformant scripts be renamed (breaking change, one-time cost) or grandfathered with
a note in `scripts/README.md` (no cost, but inconsistency persists)? **Human decision required.**

**OQ-4**: The calibration control set for `scripts/check_mcp_quality_gate.py` requires 10–20
known-correct tool call examples per tool (8 tools × ~15 examples = ~120 test cases). This is
a non-trivial authoring effort. Should this be (a) manually authored in this sprint, (b) deferred
to a dedicated issue, or (c) auto-generated using the current `dogma_server.py` tool responses
as provisional ground-truth? **Human decision required before #482 implementation.**

---

## Sources

### Primary Source Notes (This Sprint)

- `docs/research/sources/sprint-22-independent-optimization-effects.md` — Issue #497
- `docs/research/sources/sprint-22-instruction-format-efficiency.md` — Issue #491
- `docs/research/sources/sprint-22-metrics-kpi-interpretation.md` — Issue #482
- `docs/research/sources/sprint-22-canonical-scripts-friction.md` — Issue #529
- `docs/research/sources/sprint-22-observability-patterns.md` — Issues #534, #425

### Key External Citations

- Krakovna, V., et al. (2020). "Specification gaming: the flip side of AI ingenuity." DeepMind.
- Cochran, T. (2021). "Maximizing Developer Effectiveness." martinfowler.com.
- Portman, D. G. (2020). "Four Keys Project." Google Cloud Blog.
- Chen, M., et al. (2021). "Evaluating LLMs Trained on Code." OpenAI. arXiv:2107.03374.
- Anthropic. (2024). "Measuring the Persuasiveness of Language Models."
- OpenTelemetry. (2024). "Semantic conventions for generative AI systems." opentelemetry.io/docs/specs/semconv/gen-ai/.
- Kambhampati, S., et al. (2024). "LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks." ICML 2024. arXiv:2402.01817.
- Amodei, D., et al. (2016). "Concrete Problems in AI Safety." arXiv:1606.06565.
- Ganguli, D., et al. (2022). "Red Teaming Language Models to Reduce Harms." Anthropic. arXiv:2209.07858.
- Liu, N. F., et al. (2023). "Lost in the Middle: How Language Models Use Long Contexts." arXiv:2307.03172.

### Key Endogenous Sources

- `docs/research/mcp-quality-metrics-survey.md` (Status: Final, closes #495)
- `docs/decisions/ADR-008-mcp-quality-metrics-framework.md` (Status: Accepted)
- `data/mcp-metrics-schema.yml` (owner: #495)
- `docs/research/ai-workload-observability.md` (Status: Final, closes #316)
- `docs/research/agents/xml-agent-instruction-format.md` (Status: Final, ADOPTED)
- `AGENTS.md` § Programmatic-First Principle
- `scripts/README.md`
