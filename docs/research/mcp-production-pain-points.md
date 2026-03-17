---
title: "MCP Production Pain Points — 2026 Roadmap Analysis"
status: "Final"
research_issue: 285
closes_issue: 285
date: 2026-03-17
sources:
  - https://thenewstack.io/mcps-biggest-growing-pains-for-production-use-will-soon-be-solved/
  - docs/research/mcp-state-architecture.md
  - docs/research/intelligence-architecture-synthesis.md
  - AGENTS.md
  - MANIFESTO.md
---

# MCP Production Pain Points — 2026 Roadmap Analysis

> **Status**: Final
> **Research Question**: Do the four documented MCP production pain points in the 2026 roadmap materially alter dogma's MCP integration plans, and does the roadmap direction validate or invalidate existing architecture stances?
> **Date**: 2026-03-17
> **Related**: [`docs/research/mcp-state-architecture.md`](mcp-state-architecture.md) · [`docs/research/intelligence-architecture-synthesis.md`](intelligence-architecture-synthesis.md) · [`AGENTS.md` §Agent Communication](../../AGENTS.md#agent-communication)

---

## Executive Summary

The MCP 2026 roadmap, authored by David Soria Parra (Anthropic MCP lead maintainer) and reported by The New Stack, identifies four production pain points: transport scalability (P1), agent communication / async task gaps (P2), governance bottlenecks (P3), and enterprise readiness (P4). Of the four, only P2 introduces a concrete deferral risk for dogma's planned MCP server implementations. P1 validates the architectural stance already encoded in [`docs/research/mcp-state-architecture.md`](mcp-state-architecture.md). P3 and P4 are effectively negligible for dogma at its current phase.

The roadmap's most strategically important signal for dogma is the explicit trend away from long-lived stateful sessions toward **stateless horizontal scaling via `.well-known` server discovery**. This is not a future risk — it is a present confirmation that dogma's proposed MCP servers (`scratchpad-query` #297, governance tools #303) should be designed as stateless stdio processes from the outset. The [Local Compute-First axiom (MANIFESTO.md §3)](../../MANIFESTO.md#3-local-compute-first) is directly aligned with this direction: local stdio processes have no horizontal-scaling burden by design.

The Tier 3 recommendation from [`docs/research/intelligence-architecture-synthesis.md`](intelligence-architecture-synthesis.md) — implementing an MCP-mediated scratchpad query pattern as the A2A-minimal viable surface (#297) — **remains the correct strategic direction**. The roadmap does not invalidate it. The only operational adjustment is to defer any use of the MCP `Tasks` API in dogma servers until the lifecycle regression (retry semantics, result persistence duration) is resolved upstream. Simple synchronous request/response patterns are sufficient for dogma's MVP MCP servers and are safer under [Algorithms Before Tokens (MANIFESTO.md §2)](../../MANIFESTO.md#2-algorithms-before-tokens): prefer the deterministic synchronous path over the partially-specified async one.

---

## Hypothesis Validation

### H1 — Current MCP production pain points materially risk dogma's MCP integration plans

**Verdict: Partially Supported**

The four pain points affect dogma unevenly:

- **P1 (Transport scalability)**: LOW risk. Dogma's planned MCP servers are stdio-based, single-instance, local. Horizontal scaling across pods is not a requirement now or in any near-term phase. The roadmap directly validates dogma's existing [stateless server architecture](mcp-state-architecture.md#p1-stateless-server-pattern) described in `mcp-state-architecture.md`. Risk: none.
- **P2 (Async task gaps)**: MEDIUM risk. If dogma MCP servers implement the `Tasks` API for long-running operations (RAG reindex, corpus scan), the undefined retry behavior and undefined result persistence duration would produce underdetermined failure modes. This is a genuine defer signal. Risk: real, manageable by architectural scope constraint.
- **P3 (Governance bottleneck)**: NEGLIGIBLE risk. Dogma is an MCP consumer, not a spec contributor. Governance reform benefits the ecosystem but does not gate any dogma deliverable.
- **P4 (Enterprise readiness)**: LOW-MEDIUM risk. Authentication and audit trails are out of scope for dogma's current open-source developer tool phase. However, the planned governance tools MCP server (#303) should be architected with auth-awareness for forward compatibility as cross-team adoption becomes Phase 2 scope.

**Support level**: The pain points partially affect dogma (P2 introduces a deferral constraint; P4 introduces a design consideration for #303) but do not block or invalidate any current sprint deliverable. "Material risk" in the strong sense is not supported.

---

### H2 — The 2026 roadmap changes the Tier 2/3 recommendations in `intelligence-architecture-synthesis.md`

**Verdict: Not Supported**

The `intelligence-architecture-synthesis.md` Tier 2 recommendation (validate_session_state.py FSM coverage check, Sprint 13-14) and Tier 3 recommendation (MCP-mediated scratchpad query as A2A-minimal surface, #297, Sprint 15+) are both **reinforced** by the roadmap, not contradicted.

The explicit roadmap movement toward stateless servers confirms that designing #297 as a stateless stdio tool server is the right architectural bet. The `.well-known` discovery endpoint (P1 resolution) may eventually enable multi-agent MCP architectures — making the scratchpad-query server (#297) a natural future integration point. No recommendation in `intelligence-architecture-synthesis.md` needs to be updated as a result of this research.

---

### H3 — Stateless + stdio design for dogma MCP servers is future-proof

**Verdict: Confirmed**

The MCP maintainers are explicitly solving P1 by evolving transport **toward** stateless horizontal scaling, not away from it. Parra's statement — "We are NOT adding new official transports this cycle — evolve existing transport instead" — signals that the spec will mature its existing transport model to eliminate the in-memory session-state constraint that prevents horizontal scaling. Dogma's planned stdio servers have never had that constraint, placing them structurally ahead of the problematic patterns the roadmap is resolving.

This is a direct empirical grounding for [Endogenous-First (MANIFESTO.md §1)](../../MANIFESTO.md#1-endogenous-first): the system's existing architectural choices — stateless tool calls, local stdio processes — are validated by external roadmap evidence, not derived from it. The architecture was encoded correctly. The roadmap is confirmation, not instruction.

---

## Pattern Catalog

### Pattern 1 — Stateless-First MCP Server Design

**Context**: The MCP specification defines stateful sessions at the protocol level (capability negotiation, subscription management). However, individual tool calls are stateless request/response exchanges. Production deployments running multi-instance MCP servers have discovered that in-memory session state prevents horizontal scaling.

**Pattern**: Design MCP tool servers so that **every tool call is a complete, self-contained operation**: input payload carries all required context, result is returned fully in the response, no state is stored between invocations. Sessions handle capability negotiation only — they carry no application-level agent state.

> **Canonical example**: A dogma `scratchpad-query` MCP server (#297) receives `{ "query": "session summary", "scratchpad_path": ".tmp/branch/2026-03-17.md" }` and returns the matching section as a complete JSON response. No session-level cache, no cross-call state. Each tool invocation is independently retryable.

> **Anti-pattern**: A `rag-index` MCP server that accumulates parsed document state in a server-side Python dict between calls, expecting the next call to have access to the intermediate parse results. This pattern fails immediately under any server restart and fails under horizontal scaling — and the MCP maintainers are actively removing spec affordances that enable it.

**Dogma stance**: ADOPT. This pattern is already the declared baseline in [`mcp-state-architecture.md` §P1](mcp-state-architecture.md). The 2026 roadmap independently reinforces it. All planned dogma MCP servers (#297, #303) must implement this pattern.

**Alignment**: [Local Compute-First (MANIFESTO.md §3)](../../MANIFESTO.md#3-local-compute-first) — local stdio processes have no horizontal-scaling surface by design; stateless-first eliminates the one architectural gap that could reintroduce it.

---

### Pattern 2 — Defer Tasks API Until Lifecycle Stabilizes

**Context**: MCP's `Tasks` API enables agents to start async work and retrieve results later. Production use in 2025-2026 exposed two critical gaps: retry behavior for failed tasks is undefined in the spec, and result persistence duration is undefined. These gaps produce underdetermined failure modes — a task client cannot know whether to retry, assume loss, or query for results after a server restart.

**Pattern**: For dogma MCP servers that handle long-running operations, **implement synchronous request/response patterns for MVP** and treat `Tasks` API adoption as explicitly deferred until the roadmap-promised lifecycle definitions ship and are validated in a minor release.

> **Canonical example**: A dogma `corpus-sweep` MCP tool that might take 30–60 seconds is initially implemented as a blocking synchronous call with a client-side timeout. The caller receives either a complete result or an error — no partial states, no async polling. This is slower for the interactive case but fully deterministic under failure.

> **Anti-pattern**: Adopting the `Tasks` API in a dogma MCP server during Sprint 13-14 to support a corpus-scan operation, discovering during integration testing that retry-on-failure behavior is undefined, and encoding compensatory logic that the spec will later contradict once lifecycle definitions land.

**Dogma stance**: DEFER. The [Algorithms Before Tokens axiom (MANIFESTO.md §2)](../../MANIFESTO.md#2-algorithms-before-tokens) applies directly: prefer the deterministic, fully-specified synchronous path over the partially-specified async one. Re-evaluate when the MCP roadmap marks Task lifecycle definitions as stable.

**Monitoring signal**: Watch the `modelcontextprotocol/specification` changelog for a `Task` lifecycle section addition. That is the gate event to re-evaluate.

---

## Gap & Differentiation Matrix

| Pain Point | Dogma Relevance | Recommended Action | Timeline |
|---|---|---|---|
| **P1 — Transport / session scalability** | LOW — stdio servers not affected; roadmap validates existing architecture | ADOPT stateless-first pattern for all planned MCP servers; note `.well-known` discovery in #303 design | Sprint 13 (design) |
| **P2 — Async Tasks lifecycle gaps** | MEDIUM — affects any dogma server handling long-running ops | DEFER Tasks API; use synchronous request/response for dogma MCP MVP | Revisit after MCP stable lifecycle spec ships |
| **P3 — Governance / SEP bottleneck** | NEGLIGIBLE — dogma is a consumer, not a spec contributor | No action required; passive beneficiary of governance reform | N/A |
| **P4 — Enterprise readiness / auth** | LOW-MEDIUM — out of scope now; relevant for #303 Phase 2 | Design #303 governance tools server with auth-awareness as a forward-compatibility hook | Sprint 15+ (Phase 2 design) |
| **Horizon: `.well-known` discovery** | MEDIUM-FUTURE — enables multi-agent MCP architectures | Note in #303 architecture doc; do not implement now | Sprint 16+ |

---

## Recommendations

**1. Codify stateless-first as a required design constraint for all dogma MCP servers.**

Update the `docs/research/mcp-state-architecture.md` and any forthcoming MCP server design docs (for #297, #303) to explicitly state that the stateless-first Pattern 1 is mandatory, not advisory. The [Endogenous-First axiom (MANIFESTO.md §1)](../../MANIFESTO.md#1-endogenous-first) is satisfied here: dogma arrived at this stance before the roadmap confirmed it. Encoding it formally prevents future implementers from treating it as optional.

**2. Add a "Tasks API" adoption gate to #297 and #303 issue acceptance criteria.**

Neither the `scratchpad-query` (#297) nor the governance tools (#303) MCP server should implement the `Tasks` API until the MCP roadmap specs stable lifecycle semantics for retry and result persistence. Add an explicit acceptance-criteria checkbox to both issues: "Does NOT use MCP Tasks API — uses synchronous request/response only (defer until MCP lifecycle semantics stable)." This prevents well-intentioned premature adoption of an underspecified API.

**3. Add a `.well-known` discovery note to the #303 governance tools MCP server design document.**

The MCP roadmap's transport evolution (P1) will land a `.well-known` metadata endpoint for server discovery. The governance tools server (#303) is the most likely candidate for multi-agent access patterns in Phase 2. While no implementation is warranted now, the design document for #303 should note that the server URL should be configurable and discoverable via this future endpoint — not hardcoded. This costs nothing architecturally and avoids a later refactor.

---

## Sources

1. Parra, D. S. (2026). "MCP's biggest growing pains for production use will soon be solved." *The New Stack*. <https://thenewstack.io/mcps-biggest-growing-pains-for-production-use-will-soon-be-solved/>

2. EndogenAI Workflows (2026-03-15). "MCP State Architecture — Stateless vs. Stateful Agent Coordination." *docs/research/mcp-state-architecture.md*. Status: Final. [`mcp-state-architecture.md`](mcp-state-architecture.md)

3. EndogenAI Workflows (2026). "Intelligence Architecture Synthesis." *docs/research/intelligence-architecture-synthesis.md*. Status: Final. [`intelligence-architecture-synthesis.md`](intelligence-architecture-synthesis.md)

4. EndogenAI Workflows. "MANIFESTO.md — Foundational Axioms." *MANIFESTO.md*. [`MANIFESTO.md`](../../MANIFESTO.md)

5. Typescript SDK GitHub issue #892 (referenced in The New Stack article): stateless MCP — client session IDs not reliably mapped to server event streams in multi-pod deployments.
