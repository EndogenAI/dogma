---
title: "Agent Fleet Model Diversity and Structured Format Strategies"
status: Final
research_sprint: "Sprint 34 — Fleet Governance + Research Foundations"
closes_issue: 413
related_issue: 414
date: 2026-03-26
sources_scouted: 4
recommendations:
  - id: rec-agent-fleet-model-diversity-001
    title: 'Encode role-aligned model assignment in fleet agent files'
    status: completed
    linked_issue: 469
    decision_ref: ''
  - id: rec-agent-fleet-model-diversity-002
    title: 'Create data/deployment-registry.yml for multi-provider routing'
    status: deferred
    linked_issue: 470
    decision_ref: ''
  - id: rec-agent-fleet-model-diversity-003
    title: 'Adopt JSONL as canonical format for multi-Scout batch handoffs'
    status: completed
    linked_issue: 471
    decision_ref: ''
  - id: rec-agent-fleet-model-diversity-004
    title: 'Add XML attribute convention for large document injection'
    status: completed
    linked_issue: 472
    decision_ref: 'docs/research/agents/xml-agent-instruction-format.md'
  - id: rec-agent-fleet-model-diversity-005
    title: 'Update data/task-type-classifier.yml with model-tier routing column'
    status: deferred
    linked_issue: 473
    decision_ref: ''
  - id: rec-agent-fleet-model-diversity-006
    title: 'Track provider diversity in substrate health checks'
    status: deferred
    linked_issue: 474
    decision_ref: ''
---

# Agent Fleet Model Diversity and Structured Format Strategies

> **Status**: Final
> **Issues**: Closes #413 (model diversity in agent fleets); companion to #414 (JSONL/XML
> structured formats in substrate)
> **Date**: 2026-03-26

---

## 1. Executive Summary

Two related research questions are resolved in this document.

**Issue #413 — Model Diversity**: The EndogenAI fleet currently operates on a de facto
single-provider, single-model posture: Claude Sonnet for almost every role. Three
hypotheses submitted for validation all receive at least partial confirmation. Task-tier
routing (H1) is already encoded in principle via `llm-tier-strategy.md` and is confirmed by
Anthropic's own "Building effective agents" routing pattern. Multi-model assignment at fleet
level (H2) is strongly confirmed: Anthropic's production research system uses Opus 4 as
lead orchestrator and Sonnet 4 as subagents, outperforming single-agent Opus 4 by **90.2%**
— the mechanism is token-budget multiplication across isolated context windows, not model
monolithism. Provider diversity as a rate-limit mitigation strategy (H3) is confirmed via
the LiteLLM Router architecture: deployment-level cooldowns on 429 errors automatically
route subsequent requests to healthy providers, making multi-provider configuration a
structural resilience control rather than a fallback.

**Issue #414 — Structured Formats**: The XML hybrid analysis is already fully resolved in
`docs/research/agents/xml-agent-instruction-format.md` (Status: Final, ADOPTED). Reading
level conventions are covered in `docs/research/reading-level-assessment-framework.md`. This
document's new contribution is the **JSONL gap**: JSONL (JSON Lines) is confirmed as the
natural format for streamed, multi-item agent handoffs and batch subagent outputs — but is
absent from the substrate's current format conventions. XML attribute-based metadata is
partially confirmed by first-party vendor guidance as a complementary navigation layer.

**Priority action for EndogenAI**: Encode provider diversity configuration as a
`data/deployment-registry.yml` (litellm-style), encode JSONL as the canonical batch handoff
format in agent-output conventions, and extend the existing XML tag convention with
attribute-based metadata for large document prompts.

---

## 2. Research Questions

### Issue #413 — Model Diversity in Agent Fleets

| ID | Hypothesis |
|----|-----------|
| H1 | Explicit model-to-task alignment (task classifier → model tier selection) improves output quality and reduces frontier token cost compared to single-model defaults |
| H2 | Cross-provider model diversity (different providers or model families for different fleet roles) produces higher quality outcomes than a monolithic single-model fleet |
| H3 | Provider diversity functions as a structural rate-limit mitigation — distributing requests across providers reduces 429 exposure without requiring sleep/retry logic in session code |

### Issue #414 — JSONL/XML Structured Formats in Substrate

| ID | Hypothesis |
|----|-----------|
| H1 | XML tags improve instruction parsing fidelity in agent files (**answered in existing corpus** — see §5) |
| H2 | JSONL (JSON Lines) is the appropriate format for multi-item structured agent outputs, batch handoffs, and streamed context pipelines |
| H3 | Reading level differentiation (guidance-prose vs. protocol-text) is a structural formatting concern (**answered in existing corpus** — see §5) |
| H4 | XML attributes (key-value metadata within tags) provide a navigation layer for large document injection with lower parsing overhead than repeated element nesting |

---

## 3. Hypothesis Validation

### #413 H1 — Model-to-task alignment

**Verdict: CONFIRMED (cost dimension confirmed; quality dimension partially confirmed)**

**Evidence**:

Anthropic's "Building effective agents" (2024) names this pattern explicitly as a
**routing workflow**: *"Routing easy/common questions to smaller, cost-efficient models like
Claude Haiku 4.5 and hard/unusual questions to more capable models like Claude Sonnet 4.5
to optimize for best performance."* The routing decision is categorical: the agent
classifies the task before model selection, not after.

This confirms and extends H1 of `llm-tier-strategy.md` (Status: Final): that document
established the 3-tier topology and confirmed that 50–65% of fleet work does not require
frontier reasoning depth. The new evidence adds that Anthropic's own production guidance
encodes task-tier routing not as a cost optimization but as a *quality* optimization — the
smaller model performs *better* on the smaller task because it receives focused attention.
"LLMs generally perform better when each consideration is handled by a separate LLM call,
allowing focused attention on each specific aspect."

**Scope constraint**: This addresses task classification within the fleet (single-provider
multi-tier routing). Cross-provider quality comparison (e.g., Claude Haiku vs. GPT-4o-mini
for the same task) remains an open question — see §8.

**Cross-reference**: `docs/research/models/llm-tier-strategy.md` § H1–H3 (confirmed
majority of tasks do not require frontier depth) and `data/task-type-classifier.yml`.

---

### #413 H2 — Cross-provider model diversity at fleet level

**Verdict: CONFIRMED**

**Evidence**:

Anthropic's production Research feature (published June 2025) provides the strongest direct
evidence. The production architecture assigns **different models to different fleet roles**:
Claude Opus 4 as the lead orchestrating agent, Claude Sonnet 4 as the executing subagents.
The performance gap is quantified: *"a multi-agent system with Claude Opus 4 as the lead
agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our
internal research eval."*

Three factors explained 95% of performance variance: token usage (80%), number of tool
calls, and **model choice**. The model-choice variable validates H2 directly: the optimum
is not to deploy the same frontier model uniformly, but to match model capability class to
role requirements — orchestration (Opus) vs. execution (Sonnet).

**Canonical example**: See §4.

The mechanism is architectural: the orchestrator requires cross-source synthesis,
planning, and long-context coherence (frontier territory). The subagents require focused
single-query execution and result compression (mid-tier adequate). The combination is 1.9×
better than using Opus for everything.

**EndogenAI relevance**: The current fleet assigns the same model to Executive Orchestrator
and Research Scout. This is the monolithic anti-pattern. The evidence supports role-aligned
model assignment: frontier model for executives, mid-tier for scouts and file editors.

---

### #413 H3 — Provider diversity as rate-limit mitigation

**Verdict: CONFIRMED**

**Evidence**:

LiteLLM's production Router (v1 architecture, widely adopted for multi-provider agent
systems) encodes this as the **deployment cooldown pattern**. When a request to a deployment
returns HTTP 429 (RateLimitError), the router immediately cools down that deployment for 5
seconds (default) and routes the next request to a healthy alternative deployment. Cooldown
also triggers on >50% failure rate in the current minute.

The architecture is explicit: *"Cooldowns apply to individual deployments, not entire model
groups. The router isolates failures to specific deployments while keeping healthy
alternatives available."*

The three-provider real-world example from LiteLLM's docs illustrates the mechanism:
Anthropic Direct → BYOK → Vertex AI (all running the same base model). A 429 on Anthropic
Direct cools it for 5 seconds; Vertex AI immediately serves the next request. No session
code sleeps; no manual retry logic.

This directly addresses the gap in `docs/research/rate-limit-detection-api.md` (Status:
Working), which notes that rate limits are scoped per API key and that model switching does
NOT reset counters. Provider diversity (different API keys, different infrastructure) is the
structural solution that key-level rate-limit tracking cannot provide.

**Cross-reference**: `docs/research/rate-limit-detection-api.md` §Revised Mitigation
Strategy (item 4: request serialization). Provider diversity supersedes serialization as a
resilience strategy — it eliminates the need to serialize by providing failover capacity.

---

### #414 H1 — XML tags for instruction parsing

**Verdict: CONFIRMED — fully resolved in existing corpus**

See `docs/research/agents/xml-agent-instruction-format.md` for the full analysis
(17 sources, Status: Final, ADOPTED). Summary: hybrid Markdown `##` headings + XML tag
wrappers is the canonical pattern for EndogenAI `.agent.md` files. Both Anthropic and
OpenAI's first-party guides recommend this hybrid. VS Code forwards the body verbatim
(conduit finding). Migration is in progress per Issue #12.

**This document does not repeat that analysis.** All new XML findings appear in §4 (H4
extension only).

---

### #414 H2 — JSONL for multi-item agent outputs and streamed context

**Verdict: PARTIALLY CONFIRMED**

**Evidence**:

JSON Lines (JSONL) is a serialization format where each line is a self-contained, independently
parseable JSON object. It is the natural format for three agent-system use cases that are
currently unaddressed in the EndogenAI substrate:

1. **Batch subagent outputs**: When multiple Research Scout subagents return independent
   findings, JSONL encodes one finding object per line — each carrying `source`, `excerpt`,
   `confidence`, and `relevance_to_question` fields. The lead agent can then stream-process
   findings as they arrive rather than waiting for all subagents to finish and
   joining a monolithic JSON array.

2. **Streamed structured context**: OpenAI's Structured Outputs guide documents streaming
   JSON as a first-class capability: *"You can use streaming to process model responses or
   function call arguments as they are being generated, and parse them as structured data.
   That way, you don't have to wait for the entire response to finish before handling
   it."* JSONL is the natural persistence format for streamed structured output written to
   `.cache/` — each response object writes a separate line, preserving append semantics
   without requiring atomic file writes.

3. **Audit logging and rate-limit telemetry**: `data/rate-limit-profiles.yml` defines
   provider policies, but there is no schema for per-delegation audit records. JSONL is the
   standard format for append-only audit logs: each delegation event is one line; logs are
   never fully loaded into memory; `jq` can process without parsing the full file.

**Partial confirmation caveat**: The evidence establishes JSONL as the appropriate format
for these use cases based on first-principles streaming properties, but no first-party
agent-system documentation explicitly mandates JSONL over JSON arrays for multi-item
handoffs. This remains a design recommendation grounded in streaming properties rather than
a vendor prescription.

**Distinction from OpenAI JSON Schema**: OpenAI's Structured Outputs (JSON Schema with
`strict: true`) enforces schema adherence for single-object responses. JSONL is a
*collection* format; each line may independently adhere to the same schema. These are
complementary, not competing.

---

### #414 H3 — Reading level differentiation for guidance vs. protocol text

**Verdict: CONFIRMED — fully resolved in existing corpus**

See `docs/research/reading-level-assessment-framework.md` and
`docs/research/high-reading-level-encoding-drift-signal.md`.

Summary: guidance text (narrative, instructional) benefits from lower Flesch-Kincaid
reading level (≤12); protocol text (structured commands, tool specs, XML instruction
blocks) should use dense technical precision regardless of reading level score. The two
registers serve different parsing modes in the model. Encoding-drift signal: when guidance
text drifts to protocol register, model instruction-following degrades; when protocol text
drifts to narrative, parsing errors increase.

---

### #414 H4 — XML attributes for prompt navigation

**Verdict: PARTIALLY CONFIRMED**

**Evidence**:

OpenAI's production prompt engineering guide explicitly names XML attributes as a metadata
layer: *"XML attributes can also be used to define metadata about content in the prompt."*
This extends the plain-tag convention (e.g., `<document>`) with navigable metadata (e.g.,
`<document index="1" source="arxiv" relevance="high">`).

The use case is most visible in large document injection patterns: when a prompt includes
multiple source documents for in-context retrieval, XML attributes allow the model to:
- Identify documents by index without counting elements
- Filter by source type or relevance tier without reading full document content
- Reference by attribute in downstream output (`"as in document index=3..."`)

**EndogenAI relevance**: The `.tmp/<branch>/<date>.md` scratchpad sections currently use
plain Markdown headings (`## Scout Output`). For large research sessions (5+ subagent
outputs), an XML wrapper with attributes — e.g.,
`<section agent="scout" phase="1" status="settled">` — would allow the Executive
Orchestrator to parse structural metadata without full content reads.

**Partial confirmation caveat**: The existing xml-agent-instruction-format.md ADOPTED
recommendation covers tag-level structure only. The attributes extension is additive and
not yet validated in the EndogenAI fleet context. Encoding as a recommendation (§6) rather
than confirmed practice.

---

## 4. Pattern Catalog

### #413 — Model Diversity Patterns

**Canonical example — Role-aligned model assignment (Anthropic Research, 2025)**:

> *"A multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents
> outperformed single-agent Claude Opus 4 by 90.2%."*
>
> Architecture: Orchestrator role → Opus 4 (frontier, synthesis, planning).
> Subagent roles → Sonnet 4 (focused execution, compression-on-ascent).
> Routing: task decomposition determines role assignment; role determines model tier.

**Anti-pattern — Monolithic single-model fleet**:

Deploying the same frontier model to all roles regardless of task complexity. In
Anthropic's production analysis, three factors explained 95% of performance variance;
model choice was one of them. Single-model deployment maximizes per-token cost and leaves
the model-choice optimization lever unused. The 90.2% gap is the quantified cost of the
anti-pattern.

**Canonical example — Deployment-level provider failover (LiteLLM Router)**:

```yaml
model_list:
  - model_name: sonnet-4          # Primary: Anthropic Direct
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      api_key: <anthropic-key>
  - model_name: sonnet-4          # Fallback: Vertex AI (different API key scope)
    litellm_params:
      model: vertex_ai/claude-sonnet-4-20250514
      vertex_project: my-project
```

On 429 from Anthropic Direct → 5-second cooldown → automatic routing to Vertex AI.
No session-level retry code needed; resilience is structural.

**Anti-pattern — Model switching as rate-limit mitigation**:

Switching between Claude Sonnet and Claude Haiku under the same API key as a rate-limit
workaround. This does not work: Claude API rate limits are scoped per API key, not per
model. Sonnet and Haiku share the same rate-limit window. See
`docs/research/rate-limit-detection-api.md` §Rate-Limit API Specification.

---

### #414 — Structured Format Patterns

**Canonical example — JSONL for batch subagent output**:

```jsonl
{"agent": "scout-1", "source": "arxiv:2512.05470", "confidence": 0.9, "finding": "AIGNE evaluator closes pipeline loop before downstream agent receives output"}
{"agent": "scout-2", "source": "anthropic-multi-agent", "confidence": 0.95, "finding": "Opus 4 lead + Sonnet 4 subagents outperforms single-agent by 90.2%"}
{"agent": "scout-3", "source": "litellm-router", "confidence": 0.85, "finding": "Deployment-level cooldown on 429 achieves provider failover without session sleep"}
```

Each line is independently parseable. Lead agent can begin synthesis before all scouts
written. Append-safe (no file locking). Naturally sorted by arrival time.

**Anti-pattern — Monolithic JSON array for multi-Scout handoff**:

```json
[
  {"agent": "scout-1", ...},
  {"agent": "scout-2", ...}
]
```

Requires all subagents to finish before the lead agent can begin parsing. Atomic write
semantics make partial reads impossible. Trailing-comma errors corrupt the entire payload.
For concurrent subagent pipelines, JSONL is structurally superior.

**Canonical example — XML attribute metadata for large document prompts**:

```xml
<documents>
  <document index="1" source="arxiv" type="primary" relevance="high">
    [AIGNE architecture paper content...]
  </document>
  <document index="2" source="anthropic-blog" type="secondary" relevance="medium">
    [Multi-agent research system post...]
  </document>
</documents>
```

Model can reference `document index="1"` in citations without re-reading content.
Attribute-based filtering (`relevance="high"`) guides model attention in long prompts
without requiring programmatic pre-filtering.

**Anti-pattern — Flat repeated `<document>` elements without attributes**:

```xml
<document>Content...</document>
<document>Content...</document>
```

No navigable distinction between documents. Model must read all content to determine
relevance. Citation tracking requires counting occurrences, not referencing by attribute.

---

## 5. Existing Corpus Integration

The following corpus documents directly answer hypotheses in this sprint and should not be
re-derived:

| Hypothesis | Answering Document | Status | Note |
|---|---|---|---|
| #413 H1 (task-tier routing, cost) | `docs/research/models/llm-tier-strategy.md` | Final | H1–H5 confirmed; 3-tier topology encoded |
| #413 H3 (rate limit per-key scope) | `docs/research/rate-limit-detection-api.md` | Working | Model switching confirmed non-mitigation |
| #414 H1 (XML hybrid for agent files) | `docs/research/agents/xml-agent-instruction-format.md` | Final | ADOPTED; 17 sources; migration in progress |
| #414 H3 (reading level differentiation) | `docs/research/reading-level-assessment-framework.md` | Final | Guidance vs. protocol register confirmed |
| Fleet coordination patterns | `docs/research/agents/agent-fleet-design-patterns.md` | Final | Compression-on-Ascent / Focus-on-Descent |

**New contributions in this document** (not in prior corpus):

1. **#413 H2 confirmed** with quantified evidence (90.2% improvement, Anthropic production
   Research 2025) — role-aligned model assignment as quality strategy, not just cost
2. **#413 H3 confirmed** via LiteLLM Router deployment-level cooldown architecture —
   provider diversity as structural rate-limit control (extends rate-limit-detection-api.md)
3. **#414 H2 (JSONL)** — new format convention for batch handoffs, streamed context, audit
   logging — absent from all prior corpus docs
4. **#414 H4 extended** — XML attribute metadata for large document prompts — additive to
   xml-agent-instruction-format.md tag-level adoption

---

## 6. Recommendations

1. **Encode role-aligned model assignment in fleet agent files.** update executive
   orchestrator, executive docs, and executive researcher files to explicitly specify
   frontier-tier model selection. update research scout, env validator, and structured
   editing agents to specify mid-tier model selection. add a `preferred_model_tier`
   frontmatter field to `.agent.md` schema via the fleet agent. (tracked in #469)

2. **Create `data/deployment-registry.yml` for multi-provider routing.** encode the
   anthropic direct → vertex ai failover pattern as a data file (litellm-style deployment
   list). reference in `docs/guides/local-compute.md` and in the rate-limit-resilience
   skill. this closes the structural gap in `rate-limit-detection-api.md` §revised
   mitigation strategy. (tracked in #470)

3. **Adopt JSONL as the canonical format for multi-scout batch handoffs.** update
   `docs/guides/session-management.md` and the session-management skill.md to specify jsonl
   as the output format when 2+ subagents return concurrent findings. add a jsonl schema
   convention for scout output objects (`agent`, `source`, `confidence`, `finding`). (tracked in #471)

4. **Add XML attribute convention for large document injection.** extend the adopted hybrid
   pattern in `xml-agent-instruction-format.md` with an addendum covering attribute-based
   document metadata (`index`, `source`, `type`, `relevance`). target: any prompt injecting
   ≥3 external documents. file as a minor amendment to issue #12 follow-up. (tracked in #472)

5. **Update `data/task-type-classifier.yml` with model-tier routing column.** the existing
   classifier (task type → amplification principle) should add a `model_tier` column
   (frontier / mid / local) per task type. this encodes h1 of #413 as a data-driven
   decision rather than an implied instruction in individual agent files. (tracked in #473)

6. **Track provider diversity configuration in substrate health checks.** update
   `scripts/check_substrate_health.py` to warn when the deployment registry contains only
   one api key scope (monolithic provider configuration). a single-provider fleet has no
   structural rate-limit resilience. (tracked in #474)

---

## 7. Sources

External sources scouted for this sprint (4 sources):

1. **Anthropic Engineering — "Building effective agents"** (Dec 2024)
   `https://www.anthropic.com/engineering/building-effective-agents`
   *Key finding*: Routing workflow pattern; explicit recommendation to route easy tasks to
   Haiku, hard tasks to Sonnet for quality optimization. Parallelization via sectioning and
   voting. Agent-computer interface (ACI) as primary design concern.

2. **Anthropic Engineering — "How we built our multi-agent research system"** (Jun 2025)
   `https://www.anthropic.com/engineering/multi-agent-research-system`
   *Key finding*: Opus 4 lead + Sonnet 4 subagents → 90.2% improvement over single-agent
   Opus 4. Token usage explains 80% of performance variance; model choice is a separate
   factor. Subagent output to filesystem (not through coordinator) for structured results.
   Rainbow deployments for stateful agent system updates.

3. **LiteLLM Router — Load Balancing documentation**
   `https://docs.litellm.ai/docs/routing`
   *Key finding*: Deployment-level cooldown (429 → 5s cooldown → automatic failover to
   healthy deployment). Multi-provider configuration as structural rate-limit resilience.
   Routing strategies: simple-shuffle (default), rate-limit-aware, latency-based,
   cost-based. Pre-call context window checks. Traffic mirroring for silent A/B evaluation.

4. **OpenAI — Structured Outputs guide**
   `https://developers.openai.com/api/docs/guides/structured-outputs`
   *Key finding*: Structured Outputs (JSON Schema with `strict: true`) vs. JSON mode (valid
   JSON only). Streaming structured outputs: process JSON fields as generated. XML
   attributes named as metadata layer in prompt engineering guidance. Schema-divergence
   prevention: CI rules or Pydantic/Zod native SDKs.

---

## 8. Open Questions

1. **Cross-provider quality comparison** (requires primary research): Does Claude Haiku
   consistently outperform GPT-4o-mini on the same structured editing tasks within the
   EndogenAI substrate, or should the deployment registry include cross-family fallbacks
   (Claude → OpenAI)? No first-party comparative benchmark exists for EndogenAI task
   profiles. Flag for Sprint 35 primary research (H1 cross-provider extension).

2. **JSONL schema standardization across fleet**: Should all subagent handoffs conform to a
   shared JSONL schema, or is schema per-agent appropriate? The tradeoff is machine
   readability (shared schema) vs. flexibility (agent-specific schemas). No prior art in
   this codebase. Raises ADR-level decision.

3. **XML attribute parsing overhead**: For very large prompts (>100K tokens), do XML
   attributes add meaningful parsing efficiency for Claude, or does the model read entire
   tag contents regardless? Anthropic's prompt engineering guide recommends attributes but
   does not benchmark the attention savings. Requires empirical testing on long-context
   tasks.

4. **Deployment registry governance**: Who owns `data/deployment-registry.yml`? PM agent
   (provider cost decisions)? Executive Automator (infrastructure)? The LiteLLM pattern
   places this in a config file; the EndogenAI governance model requires ownership
   assignment before the file is created.
