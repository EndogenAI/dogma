---
title: "Harness-Memory Governance: Lock-in Risks and Open Architecture Strategies"
status: Final
closes_issue: 550
sources:
  - https://blog.langchain.com/your-harness-your-memory/
  - https://x.com/sarahwooders/status/2040121230473457921
  - https://www.letta.com/
  - https://github.com/letta-ai/letta
  - https://docs.langchain.com/oss/python/deepagents/overview
  - https://agentskills.io/home
  - https://github.com/openai/agents.md
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
  - https://www.datadoghq.com/blog/ai/harness-first-agents/
recommendations:
  - id: rec-harness-memory-governance-001
    title: "DogmaMCP Memory-Aware Harness Bindings"
    status: accepted
    linked_issue: null
    decision_ref: ""
  - id: rec-harness-memory-governance-002
    title: "Substrate Layering for Harness Governance"
    status: accepted
    linked_issue: null
    decision_ref: ""
  - id: rec-harness-memory-governance-003
    title: "Encode Memory-Governance Risk as Substrate Failure Mode"
    status: accepted
    linked_issue: null
    decision_ref: ""
---

# Harness-Memory Governance: Lock-in Risks and Open Architecture Strategies

---

## 1. Executive Summary

Agent harnesses — the scaffolding systems that mediate LLM interactions with tools and external data — are becoming the dominant architectural pattern for production agentic systems. As harness sophistication has increased (RAG → LangGraph → full agent orchestration), memory management has emerged as the **critical responsibility of the harness, not a separable plugin**. This interdependency creates a previously underappreciated lock-in vector: **platform lock-in via memory ownership**.

Model providers (Anthropic, OpenAI) are increasingly moving harness functionality and memory management behind proprietary APIs (e.g., Claude Managed Agents, Anthropic's server-side compaction). This strategy creates structural lock-in: users build memory into their agents over time, and switching providers means abandoning that accumulated context. **Memory becomes the stickiest form of vendor lock-in** — more durable than model switching because it embeds user behavior and preferences.

This research validates that:
1. Harnesses are permanent architectural components (not absorbed by model providers)
2. Memory is inextricably tied to harness design (not a pluggable module)
3. Proprietary harnesses create lock-in via memory enclosure
4. **Open harnesses (model-agnostic, standards-based) are the governance solution**

For EndogenAI/Dogma, this has three architectural implications: (a) **DogmaMCP integration** must ship with memory-aware harness bindings to prevent lock-in; (b) **substrate layering** must encode harness contracts as L2/L3 governance policies; (c) **encoding risk** must account for memory governance as a failure mode (organizations defaulting to proprietary harnesses lose optionality).

---

## 2. Hypothesis Validation

### H1: Agent Harnesses are Permanent Infrastructure (Not Absorbed by LLMs)

**Claim**: Industry sentiment suggests that as models improve, they will absorb more scaffolding ("the model will become the harness"). This is false.

**Evidence**:
- Claude Code (Anthropic's harness) represents 512K lines of code — Anthropic has invested heavily in harness engineering despite owning the best model
- LangGraph → Deep Agents escalation (2023–2026): as model capabilities increase, the harness complexity *increases*, not decreases
- LangChain, Letta, OpenClaw, Pi, and dozens of independent harnesses all launched/matured in 2024–2026, suggesting convergence on harnesses as the standard, not a temporary scaffold

**Verdict**: ✅ **STRONGLY SUPPORTED** — Harnesses are permanent infrastructure.

---

### H2: Memory is a Core Harness Responsibility, Not a Pluggable Module

**Claim**: Memory should be separable from the harness — one could "plug memory in" to any harness.

**Evidence** (from Sarah Wooders, CTO of Letta — a stateful agent platform):

> "Asking to plug memory into an agent harness is like asking to plug driving into a car. Managing context, and therefore memory, is a core capability and responsibility of the agent harness."

**Supporting observations**:
- Short-term memory (conversation history, tool results) is entirely managed by the harness
- Long-term memory (cross-session state) must be written/read by the harness — the harness controls what is stored, how it is indexed, and what is passed to the LLM
- System instructions (agents.md/CLAUDE.md loading), skill metadata, and compaction strategies are all harness responsibilities
- No harness or memory system published to date has achieved clean separation — memory systems (Letta, mem0, Zep/Graphiti) all ship tightly coupled to their harness

**Verdict**: ✅ **STRONGLY SUPPORTED** — Memory is a core harness domain.

---

### H3: Proprietary Harnesses Create Lock-in via Memory Enclosure

**Claim**: If you do not own your harness, you do not own your memory. This creates material lock-in.

**Evidence** (escalation path):

1. **Mildly bad** — Stateful APIs (OpenAI Responses API): State stored on vendor server; switching models means abandoning conversation threads
2. **Bad** — Closed harnesses (Claude Agent SDK, which uses Claude Code): Harness behavior is unknown; memory shape is non-transferable
3. **Worst** — Full harness behind an API (Claude Managed Agents): Zero visibility into memory, zero control over what is stored, zero portability

**Canonical example** (from Harrison Chase, LangChain CEO — email assistant experiential lock-in):

> "I have an email assistant internally. It's built on top of a template in Fleet... This platform has memory built in, so as I interacted with my email assistant over the past few months it built up memory. A few weeks ago, my agent got deleted by accident. I was pissed! I tried to create an agent from the same template - but the experience was so much worse. I had to reteach it all my preferences, my tone, everything."

**Insight**: Memory creates lock-in through *experiential stickiness*, not just API stickiness. User preferences, learned behavior, and accumulated context become difficult to transfer.

**Vendor incentive**: Model providers are explicitly incentivized to move harness + memory behind proprietary APIs because memory creates lock-in that pure model switching does not.

**Verdict**: ✅ **STRONGLY SUPPORTED** — Memory ownership = vendor lock-in control.

---

### H4: Open Harnesses (Model-Agnostic, Standards-Based) Mitigate Lock-in

**Claim**: The solution to memory lock-in is open, standards-based harnesses. Users maintain ownership of their memory and can switch models without losing accumulated state.

**Evidence** (Deep Agents by LangChain — Open Alternative):

- **Open source** — Full codebase available; no proprietary black-box runtime
- **Model-agnostic** — Works with anthropic, openai, local models, etc.
- **Standards-based** — Uses industry standards (agents.md, agentskills.io) rather than proprietary schemas
- **Pluggable backends** — Memory can be stored in Postgres, Mongo, Redis, or any SQL DB
- **Self-hostable** — Can run behind any cloud hosting / on-premises
- **No vendor dependency** — Memory stored in user-controlled database; can migrate to any other harness that supports the same memory schema

**Verdict**: ✅ **SUPPORTED** — Open harnesses provide the governance mechanism for memory ownership.

---

## 3. Pattern Catalog

### Pattern 1: Experiential Lock-in (Email Assistant)

**Type**: Canonical Example  
**Harness**: Proprietary Fleet template (stateful, memory-enabled)

**Scenario**: A user builds an email assistant on top of a proprietary platform that includes memory. Over months, the agent accumulates user preferences, tone, and communication patterns. The agent is accidentally deleted.

**Problem**: When recreating the agent from the same template, the experience is dramatically degraded — the agent no longer "remembers" the user's preferences, communication style, or prior interactions. The user must reteach the agent everything.

**Lock-in Mechanism**: Memory is stored in the proprietary platform's opaque store. No export, no portability, no way to restore it to a new agent instance. The user's behavioral data is trapped in the platform.

**Governance Implication**: Users are incentivized to stay with the proprietary platform *not because of the model*, but because abandoning it means losing accumulated context. This is stickier than model lock-in.

**Application to Dogma**: When designing agent infrastructure, memory must be user-owned (exported, portable) from day one. If Dogma agents accumulate memory over time, that memory must not be trapped in DogmaMCP or any single platform.

---

### Pattern 2: Encrypted Cross-Session Compaction (OpenAI Codex)

**Type**: Anti-pattern  
**Vendor**: OpenAI  
**Component**: Codex (open source), with OpenAI-managed compaction

**Scenario**: OpenAI releases Codex as open source, suggesting users can run it independently. However, for production use, OpenAI compresses multi-session conversations into encrypted summaries. These summaries are:
- Not exportable
- Not usable outside the OpenAI ecosystem
- Not inspectable (encrypted, opaque)

**Lock-in Mechanism**: Partial enclosure — even though the model is open, the *memory* (compaction summaries) is proprietary and vendor-locked. A user could theoretically switch to a different model, but they would lose their compaction summaries (cross-session context).

**Governance Implication**: Open-sourcing a model while keeping memory proprietary is a sophisticated lock-in strategy. It creates the *appearance* of portability while maintaining full vendor control over the thing that matters (accumulated context).

**Anti-pattern Summary**: Avoid shipping a harness where memory is managed by the vendor even if the harness code itself is open.

---

### Pattern 3: Full API Enclosure (Claude Managed Agents)

**Type**: Anti-pattern  
**Vendor**: Anthropic  
**Component**: Claude Managed Agents API

**Scenario**: Anthropic launches Claude Managed Agents, positioning it as a fully managed agent runtime. Users ship their agents, and everything runs on Anthropic's servers:
- Agent execution (LLM calls)
- Tool orchestration
- Memory storage
- State persistence
- Cross-session context

**Lock-in Mechanism**: Zero user visibility, zero user control, zero portability. If memory becomes sticky (users build up context over weeks/months), switching away from Claude Managed Agents means starting from zero. The user's entire behavioral dataset is proprietary Anthropic data.

**Model Provider Incentive**: Anthropic has every incentive to move memory (long-term state) behind the API because it guarantees customer stickiness that model switching alone cannot provide. Even if OpenAI releases a better model, switching means abandoning all accumulated context.

**Governance Implication**: This is the "worst case" — it represents the limit of vendor lock-in via memory.

**Application to Dogma**: DogmaMCP must never become a full-service harness that abstracts away user memory ownership. If memory is involved, users must own and control it.

---

### Pattern 4: Open Harness Design (Deep Agents, Letta)

**Type**: Canonical Example  
**Platforms**: LangChain Deep Agents, Letta

**Scenario**: Projects ship open, model-agnostic harnesses that treat memory as a first-class concern. The harness provides:
- Clear memory interfaces (read/write/delete/export)
- Standards-based memory schemas (compatible with agents.md)
- Pluggable backends (any SQL database)
- No proprietary storage or formats
- Full user visibility into what is stored and how it is used

**Governance Properties**:
- Users own their memory (can export, migrate, audit)
- Model switching is viable (memory is stored independently)
- Standards compliance enables interoperability across harnesses
- Vendor lock-in is eliminated (users can defect without data loss)

**Application to Dogma**: The MCP harness should follow the Deep Agents / Letta model: memory interfaces that are user-owned, standards-compliant, and portable across models and harnesses.

---

## 4. Recommendations

### Recommendation 1: DogmaMCP Memory-Aware Harness Bindings

**Scope**: DogmaMCP integration layer for agents  
**Urgency**: Phase 1 (before agents reach production)

**Action**:
1. Define a memory interface contract for agents running under DogmaMCP
2. Ensure all memory is stored in user-owned, portable backends (SQLite, Postgres, etc.)
3. Do NOT use opaque proprietary memory systems; memory must be inspectable and exportable
4. Document the memory schema and provide export tooling
5. Make memory opt-in, not forced (agents should work without persistent memory if the user prefers stateless execution)

**Rationale**: This prevents agents from accumulating context in a way that locks users into DogmaMCP. If an agent built on DogmaMCP can be instantiated on any other harness (Deep Agents, Letta, custom), it maintains user optionality and defection capability.

**Encoding Requirements**:
- MANIFESTO.md § 1 (Endogenous-First): Design from existing standards (agents.md, agentskills.io) first, not from proprietary DogmaMCP extensions
- MANIFESTO.md § 3 (Local-Compute-First): Memory storage must be local/owned by default; no cloud or vendor-dependent memory stores

---

### Recommendation 2: Substrate Layering for Harness Governance

**Scope**: AGENTS.md and governance layer  
**Urgency**: Phase 2 (encode as L2/L3 policy)

**Action**:
1. Add a "Memory Governance" section to AGENTS.md that codifies:
   - What harness responsibilities include memory (required)
   - What memory must be user-owned (required)
   - What memory systems are approved (whitelist: SQLite, Postgres, open standards)
   - What memory enclosures are forbidden (blacklist: opaque vendor APIs, proprietary storage)
2. Document the memory-to-lock-in causal chain so future agents understand why memory policies exist
3. Update agent scaffolding templates to include memory governance checklist

**Rationale**: Makes memory governance *discoverable* and *programmable*, not just advisory. Future agents and scripts can trace back to policy and audit for violations.

**Encoding Requirements**:
- MANIFESTO.md § 2 (Algorithms-Before-Tokens): Encode memory governance rules procedurally, not just as advisory prompts
- AGENTS.md § Programmatic-First Principle: Memory violations should be caught by pre-commit hooks, not just code review

---

### Recommendation 3: Encode Memory-Governance Risk as Substrate Failure Mode

**Scope**: Dogma infrastructure and agent fleet design  
**Urgency**: Documentation + CI (Phase 2)

**Action**:
1. Document the trajectory: open harness → optional memory → users build context → default to proprietary vendor harness → memory becomes sticky → platform lock-in
2. Add this as a known failure mode in docs/research/ (cross-reference from AGENTS.md)
3. Create a CI gate that warns when agents are instantiated against only one vendor's harness (no alternative harness target documented)
4. Add a checklist for new agents: "Memory will be managed by: [local DB], [user-owned store], or [stateless]" — not "vendor API"

**Rationale**: This prevents silent drift. Without documentation and enforcement, future projects will naturally default to "vendor manages everything" (easiest path) and lose the optionality that Dogma is trying to preserve.

**Encoding Requirements**:
- MANIFESTO.md § 4 (Ethical Values): Memory governance is a transparency and user-control issue
- AGENTS.md § Security Guardrails: Memory lock-in is a governance boundary that should trigger escalation

---

## 5. References

### Primary Source
1. Harrison Chase. (2026). "Your Harness, Your Memory". *LangChain Blog*. Retrieved from https://blog.langchain.com/your-harness-your-memory/

### Supporting Sources
2. Sarah Wooders. "Memory isn't a plugin (it's the harness)". *X/Twitter*. Retrieved from https://x.com/sarahwooders/status/2040121230473457921
3. Letta AI. (2025). *Letta Documentation: Stateful Digital Agents*. Retrieved from https://www.letta.com/
4. LangChain. (2025). *Deep Agents: Open Source Agent Harness*. Retrieved from https://docs.langchain.com/oss/python/deepagents/overview
5. AgentSkills Working Group. (2025). *Agent Skills Specification*. Retrieved from https://agentskills.io/home
6. agents.md Community. (2025). *agents.md Standard*. Retrieved from http://agents.md/
7. Anthropic. (2025). *Claude Managed Agents API Documentation*. Retrieved from https://platform.claude.com/docs/en/managed-agents/overview
8. OpenAI. (2025). *Codex Documentation*. Retrieved from https://openai.com/codex/

### Related Dogma Research
9. [AGENTS.md § 1 Endogenous-First](../../AGENTS.md#1-endogenous-first)
10. [AGENTS.md § 3 Local-Compute-First](../../AGENTS.md#3-local-compute-first)
11. [MANIFESTO.md § Ethical Values](../../MANIFESTO.md#ethical-values)
12. [AI Platform Lock-in Risks](ai-platform-lock-in-risks.md) — Vendor ToS volatility and platform migration design; foundational lock-in analysis that this research extends to memory-specific vectors
13. [MCP State Architecture](mcp-state-architecture.md) — Three-layer state architecture (session/scratchpad/git); harness contracts map to L2/L3 governance policies
14. [Platform Agnosticism](platform-agnosticism.md) — VS Code/GitHub as deliberate infrastructure choices vs. lock-in; migration path documentation
15. [Substrate Atlas](substrate-atlas.md) — Substrate layering architecture; unvalidated substrates as encoding gaps (harness contracts should be validated)

---

## Encoding Fidelity — Axiom Citations

This document embeds the following core axioms from [MANIFESTO.md](../../MANIFESTO.md):

- **Axiom 1: Endogenous-First (§ 1)** — Memory governance solutions should be built from existing standards (agents.md, agentskills.io) before vendor-specific extensions. Recommendation 1 cites "Design from existing standards first."

- **Axiom 3: Local-Compute-First (§ 3)** — Memory storage should be local and user-owned by default, not delegated to cloud/vendor systems. Recommendation 1 requires "memory stored in user-owned, portable backends."

- **Axiom 4: Ethical Values (§ Ethical Values)** — User control and transparency over memory (where it is stored, how it is used) are governance requirements, not optional features. Recommendation 3 addresses memory governance as a "transparency and user-control issue."

---
