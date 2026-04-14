---
title: "DogmaMCP as Open Harness Architecture"
status: Accepted
date: 2026-04-13
deciders: EndogenAI core team
closes_issue: 551
---

# ADR-011: DogmaMCP as Open Harness Architecture

## Title
DogmaMCP as Open Harness Architecture

## Status
Accepted

## Context

Research from issue #550 ([harness-memory-governance.md](../research/harness-memory-governance.md)) identified a critical lock-in vector in agentic systems: **proprietary harnesses create vendor lock-in via memory enclosure**. As harnesses have evolved from simple scaffolding to sophisticated orchestration platforms (RAG → LangGraph → full agent coordination), memory management has become an inseparable harness responsibility. Platforms that control the harness control the memory — and memory creates experiential lock-in stronger than API stickiness because it embeds user preferences, learned behavior, and accumulated context.

Issue #551 asked: **Does DogmaMCP architecture align with the "open harness" pattern?** Phase 1 research ([dogmamcp-open-harness-validation.md](../research/dogmamcp-open-harness-validation.md)) validated DogmaMCP against six open harness criteria:

1. **Model-Agnostic**: MCP abstraction layer; no hard-coded model provider
2. **Standards-Based**: MCP (Model Context Protocol), agents.md, agentskills.io
3. **User-Owned Memory**: File-based scratchpad (`.tmp/<branch>/<date>.md`) with local persistence
4. **Portable**: Scratchpad is plain Markdown; MCP server is Python + standard libraries
5. **Self-Hostable**: No external service dependencies; runs entirely local
6. **Open Source**: Apache 2.0 license

**Verdict**: DogmaMCP qualifies as an open harness — all six criteria met, with two partial gaps (schema enforcement, structured export) tracked in issue #552.

This ADR formalizes the architectural decision to position DogmaMCP as an **open harness** and documents the implications for system design, governance encoding, and adopter migration stories.

## Decision Drivers

- **Vendor Lock-in Prevention**: Users must own their harness and memory to avoid experiential lock-in (per Harrison Chase email assistant example — deleting an agent means losing months of learned preferences)
- **MANIFESTO.md § Local-Compute-First**: External service dependencies create structural lock-in; self-hostable architecture preserves user optionality
- **Standards Compliance**: MCP, agents.md, agentskills.io adoption ensures interoperability with VS Code, Claude Desktop, and future MCP-compatible tools
- **Governance-as-Substrate**: DogmaMCP differentiates from memory-first platforms (Letta, mem0) by encoding values (Endogenous-First, Algorithms-Before-Tokens) directly into agent workflows

## Decision

### Core Assertion

**DogmaMCP IS an open harness** with the following architectural properties:

1. **Model-Agnostic Orchestration**: MCP serves as harness abstraction layer; agents.md/CLAUDE.md system prompts load into any MCP-compatible LLM (Claude Desktop, VS Code Copilot, Claude CLI); no model provider lock-in
2. **Standards-Based Integration**: MCP (Model Context Protocol) for tool calling; agents.md for agent metadata; agentskills.io for skill packaging; no proprietary agent format
3. **User-Owned Memory Substrate**: File-based scratchpad (`.tmp/<branch>/<date>.md`) persists locally as plain Markdown; user has full read/write access; Git tracks all changes; no remote server dependencies
4. **Portable Architecture**: Scratchpad files are human-readable and machine-parsable; migration to any agent framework requires only reading `.tmp/` directory
5. **Self-Hostable Deployment**: MCP server + scratchpad + agent files + scripts run entirely local; no external API dependencies except optional model provider calls
6. **Open Source Licensing**: Apache 2.0 license; full source code public; no proprietary components

### Differentiation from Competitors

| Platform | Category | Lock-in Vector | DogmaMCP Alternative |
|----------|----------|----------------|---------------------|
| **LangSmith** (LangChain observability) | Proprietary harness traces | State stored on LangSmith server; no local persistence | File-based scratchpad; session summaries in Git |
| **Claude Managed Agents** | Proprietary harness + memory | Memory fully server-side; zero visibility into what is stored | MCP-mediated memory; user owns `.tmp/` files |
| **OpenAI Assistants API** | Stateful API | Conversation state locked to OpenAI account | Per-branch session files; model-agnostic |
| **Letta** (memory-first harness) | Open harness, memory-first | No lock-in (Apache 2.0); memory primitives but governance-agnostic | Governance-first; values encoded in substrate |
| **mem0** (memory layer) | Open memory-as-a-service | No lock-in (Apache 2.0); memory-only (not full harness) | Scratchpad + orchestration + governance |

**DogmaMCP Positioning**: **Governance-first open harness** — distinguishes from memory-first (Letta/mem0) and proprietary (LangSmith) by encoding values (Endogenous-First, Local-Compute-First) as durable substrate constraints, not prompt-level negotiation.

### Architectural Implications

1. **MCP-as-Harness Pattern**: MCP is not just a tool-calling interface — it is the harness abstraction layer. MCP servers expose domain-specific governance tools (`check_substrate`, `validate_agent_file`, `query_docs`, `prune_scratchpad`) that any MCP-compatible LLM can invoke. This decouples orchestration from model provider APIs.

2. **Scratchpad-as-Memory Substrate**: The scratchpad (`.tmp/<branch>/<date>.md`) is the canonical memory layer. All cross-phase context flows through scratchpad write-back. Agents append findings under `## <AgentName> Output` headings; Executive reads session file first before delegating. This prevents context-window-only state loss and ensures memory is user-owned, auditable, and portable.

3. **Governance Encoding at Tool Layer**: Constraints run at MCP tool layer (e.g., `validate_agent_file` enforces BDI structure before commit), not prompt layer. This shifts governance from tokens (interactive negotiation per session) to algorithms (deterministic enforcement at tool invocation). Instantiates MANIFESTO.md § Algorithms-Before-Tokens.

4. **Standards Compliance as Portability Guarantee**: agents.md, agentskills.io, MCP compliance ensures DogmaMCP agents/skills can run in VS Code, Claude Desktop, or any future MCP-compatible environment. Migration from DogmaMCP to another platform requires only reading `.tmp/` + `.github/agents/` + `.github/skills/` directories.

## Considered Options

1. **Proprietary platform approach** — Adopt closed-source agent framework (LangChain LangSmith managed service, Claude Managed Agents, OpenAI Assistants API)
   - ❌ **Rejected**: Violates Local-Compute-First (MANIFESTO.md § 3) and user sovereignty principles; creates memory lock-in via server-side state; no local persistence or export mechanism; switching providers means abandoning accumulated context (per Harrison Chase email assistant example)
   
2. **Build custom non-standard harness** — Create bespoke architecture without standards alignment (proprietary agent format, custom protocol, no interoperability layer)
   - ❌ **Rejected**: Increases adoption friction (users must learn DogmaMCP-specific conventions); reduces portability (no migration path to/from other frameworks); contradicts Endogenous-First principle (reinvents rather than extends existing standards)
   
3. **Open harness with standards compliance** — DogmaMCP architecture (MCP for tool abstraction, agents.md for metadata, agentskills.io for skill packaging, file-based scratchpad for memory)
   - ✅ **Selected**: Aligns with MANIFESTO.md axioms (Endogenous-First § 1, Local-Compute-First § 3); enables migration stories for adopters escaping proprietary lock-in; differentiates from memory-first platforms (Letta/mem0) via governance-as-substrate positioning; preserves user sovereignty over memory and harness

## Consequences

### Positive

- **No Vendor Lock-in**: Users own harness, memory, and governance substrate; switching model providers requires no data migration (only MCP endpoint change)
- **Auditability**: Every agent interaction leaves durable trace in scratchpad; session summaries encode decision rationale; Git history tracks all memory changes
- **Governance Durability**: Values encoded in AGENTS.md, agent files, and MCP tools persist across sessions; new agents onboard via substrate, not re-prompting
- **Adopter Migration Stories**: DogmaMCP can position as escape path for users locked into LangSmith, Claude Managed Agents, or OpenAI Assistants API
- **Standards-Based Portability**: MCP/agents.md/agentskills.io compliance guarantees interoperability with future tooling

### Negative

- **Scratchpad Maturity Gap**: Current implementation lacks (a) schema enforcement, (b) structured export (JSON/YAML), (c) programmatic cross-session query, (d) standards compliance metadata. All tracked in issue #552 but not yet implemented. DogmaMCP is functionally an open harness but feature parity with Letta/mem0 requires Sprint 19 work.
- **MCP Vendor Risk**: MCP is Anthropic-led; not yet widely adopted outside Anthropic ecosystem (VS Code, Claude Desktop). If MCP fails to achieve industry adoption, DogmaMCP's harness abstraction becomes Anthropic-specific lock-in. Mitigation: MCP is open specification; could fork or adopt alternative protocol.
- **Positioning is Marketing, Not Technical Novelty**: Letta also qualifies as an open harness (Apache 2.0, self-hostable, user-owned memory). DogmaMCP is not the *first* open harness — it is a *governance-first* open harness. Narrative positioning must emphasize differentiation (governance-as-substrate) not category creation.

### Neutral

- **Requires Documentation Updates**: README.md, docs/guides/getting-started.md, MANIFESTO.md must all be updated to claim "open harness" positioning and contrast with proprietary alternatives (tracked in recommendation R2 of [dogmamcp-open-harness-validation.md](../research/dogmamcp-open-harness-validation.md))
- **Migration Guides Needed**: Adopters escaping LangSmith/Claude Managed Agents need documented migration paths (export instructions, conversion scripts, validation tests). Tracked in recommendation R3.

## Implementation

### Phase 1: Scratchpad Maturation (Issue #552)
1. **Schema Enforcement**: YAML frontmatter validation (session_id, date, branch, status)
2. **Structured Export**: JSON/YAML output for migration (`prune_scratchpad.py --export json`)
3. **Programmatic Query**: FTS5 index for cross-session retrieval (already designed)
4. **Standards Compliance**: agentskills.io manifest metadata in scratchpad headers

**Target**: Feature parity with Letta memory primitives by end of Sprint 19.

### Phase 2: Positioning Narrative (Recommendation R2)
1. Update README.md § "What is DogmaMCP?" to claim "governance-first open harness"
2. Add comparison table to docs/guides/getting-started.md (LangChain/Letta/mem0/DogmaMCP)
3. Add "Open Harness" to MANIFESTO.md § Ethical Values as instantiation of Local-Compute-First

### Phase 3: Migration Guides (Recommendation R3)
1. Create docs/guides/migrating-from-proprietary-harnesses.md with at least one full example (LangSmith or Claude Managed Agents)
2. Commit conversion script to scripts/migrate_from_<platform>.py
3. Validation test ensures converted data passes scratchpad schema

## Related Decisions

- [ADR-006: Agent Skills Adoption](./ADR-006-agent-skills-adoption.md) — Establishes agentskills.io as skill packaging standard; aligns with open harness standards-based criterion
- [ADR-008: MCP Quality Metrics Framework](./ADR-008-mcp-quality-metrics-framework.md) — Establishes MCP metrics capture; supports MCP-as-harness pattern observability
- [ADR-010: MCP Inspector Session Replay](./ADR-010-inspector-session-replay.md) — MCP Inspector integration; harness debugging tooling for session replay

## References

- Research synthesis: [dogmamcp-open-harness-validation.md](../research/dogmamcp-open-harness-validation.md)
- Foundational research: [harness-memory-governance.md](../research/harness-memory-governance.md)
- Scratchpad architecture: [scratchpad-architecture-decision.md](../research/scratchpad-architecture-decision.md)
- MCP query design: [mcp-a2a-scratchpad-query.md](../research/mcp-a2a-scratchpad-query.md)
- MANIFESTO.md § Local-Compute-First: [MANIFESTO.md](../../MANIFESTO.md#3-local-compute-first)
