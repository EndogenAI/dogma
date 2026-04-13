---
title: "DogmaMCP Open Harness Validation"
status: Final
closes_issue: 551
x-governs: [endogenous-first, local-compute-first, minimal-posture]
sources:
  - https://blog.langchain.com/your-harness-your-memory/
  - https://x.com/sarahwooders/status/2040121230473457921
  - https://www.letta.com/
  - https://github.com/letta-ai/letta
  - https://github.com/mem0ai/mem0
  - https://docs.langchain.com/oss/python/deepagents/overview
  - https://agentskills.io/home
  - https://agentskills.io/specification
  - https://github.com/openai/agents.md
  - https://www.datadoghq.com/blog/ai/harness-first-agents/
recommendations:
  - id: rec-dogmamcp-open-harness-001
    title: "BENCHMARK scratchpad maturity against competitors"
    status: accepted
    linked_issue: 552
    decision_ref: "ADR-011"
  - id: rec-dogmamcp-open-harness-002
    title: "POSITION DogmaMCP as open harness in README/docs"
    status: accepted
    linked_issue: null
    decision_ref: "ADR-011"
  - id: rec-dogmamcp-open-harness-003
    title: "DOCUMENT migration paths from proprietary platforms"
    status: accepted
    linked_issue: null
    decision_ref: "ADR-011"
---

# DogmaMCP Open Harness Validation

---

## 1. Executive Summary

**Research Question**: Does DogmaMCP meet the criteria to qualify as an "open harness" — a model-agnostic, standards-based agent orchestration platform that preserves user memory ownership and prevents vendor lock-in?

**Verdict**: **YES — DogmaMCP qualifies as an open harness** across all six core criteria, with partial gaps in two areas (schema enforcement and structured export) that are addressed by planned work (issue #552).

DogmaMCP aligns with the open harness pattern defined in research synthesis [harness-memory-governance.md](./harness-memory-governance.md): it provides model-agnostic orchestration, uses standards-based protocols (MCP, agents.md, agentskills.io), implements user-owned memory via file-based scratchpad, is self-hostable, and ships under Apache 2.0 license. This positions DogmaMCP as a direct alternative to proprietary platforms (LangSmith, Claude Managed Agents) that create lock-in via memory enclosure.

The primary differentiation vector is **governance-as-substrate**: DogmaMCP encodes values (Endogenous-First [MANIFESTO.md § 1 Endogenous-First], Local-Compute-First [MANIFESTO.md § 3 Local-Compute-First]) directly into agent workflows and memory architecture, making governance constraints durable across sessions rather than left to prompt-level negotiation. This contrasts with competitor platforms (LangChain, Letta, mem0) that are memory-focused but governance-agnostic.

**Key Findings**:
1. **Model-Agnostic** ✅: DogmaMCP uses MCP as abstraction layer; supports any MCP-compatible LLM
2. **Standards-Based** ✅: MCP (Model Context Protocol), agents.md, agentskills.io
3. **User-Owned Memory** ⚠️: File-based scratchpad (`.tmp/<branch>/<date>.md`) with local persistence; lacks structured export (planned Phase 5, issue #552)
4. **Portable** ✅: Scratchpad is plain Markdown; MCP server is Python + Apache 2.0
5. **Self-Hostable** ✅: No external service dependencies; runs entirely local
6. **Open Source** ✅: Apache 2.0 license

**Gap Analysis** (from issue #552 scope):
- **Missing**: Schema enforcement (YAML frontmatter validation)
- **Missing**: Structured export (JSON/YAML output for migration)
- **Missing**: Programmatic cross-session query (FTS5 index planned but not implemented)
- **Missing**: Standards compliance metadata (no explicit agentskills.io manifest in scratchpad)

**Implications**: DogmaMCP should be positioned as an **open harness for governance-first agent workflows**, distinguishing from memory-first platforms (Letta/mem0) and proprietary orchestration platforms (LangSmith). Migration stories for adopters escaping proprietary lock-in should be documented as evidence of portability.

---

## 2. Hypothesis Validation

### Research Methodology

**Approach**: Comparative analysis of DogmaMCP against four competitor platforms (LangChain/Deep Agents, Letta, mem0, Semantic Kernel/AutoGPT) across six open harness criteria derived from [harness-memory-governance.md](./harness-memory-governance.md).

**Criteria Sources**:
1. **Model-Agnostic**: Industry consensus (Datadog "harness-first" blog, LangChain harness framing)
2. **Standards-Based**: agents.md (OpenAI), agentskills.io (Anthropic/community), MCP (Anthropic)
3. **User-Owned Memory**: Sarah Wooders quote (Letta CTO) — "you own the harness, you own the memory"
4. **Portable**: Inverse of Harrison Chase email assistant lock-in example (LangChain CEO)
5. **Self-Hostable**: MANIFESTO.md § Local-Compute-First (endogenous axiom)
6. **Open Source**: License audit (Apache 2.0 vs. proprietary)

**Evidence Sources**:
- **Endogenous corpus** (6 Dogma docs): harness-memory-governance.md, mcp-a2a-scratchpad-query.md, scratchpad-architecture-decision.md, mcp-state-architecture.md, platform-agnosticism.md, prune_scratchpad.py
- **External benchmarks** (9 sources): LangChain harness blog, Letta docs, agents.md spec, agentskills.io spec, Datadog harness-first blog, mem0 docs

---

### Hypothesis: DogmaMCP Architecture Aligns with Open Harness Pattern

| Criterion | DogmaMCP Status | Evidence | Verdict |
|-----------|----------------|----------|---------|
| **Model-Agnostic** | ✅ YES | MCP abstraction layer; no hard-coded model provider; agents.md + CLAUDE.md system prompt loading works with any MCP-compatible LLM | ✅ PASS |
| **Standards-Based** | ✅ YES | MCP (Model Context Protocol) for tool calling; agents.md for agent metadata; agentskills.io for skill packaging; no proprietary agent format | ✅ PASS |
| **User-Owned Memory** | ⚠️ PARTIAL | File-based scratchpad (`.tmp/<branch>/<date>.md`) persists locally; user has full read/write access; lacks structured export (JSON/YAML) for migration | ⚠️ PARTIAL PASS (gap tracked in #552) |
| **Portable** | ✅ YES | Scratchpad is plain Markdown; MCP server is Python + standard libraries; no external service lock-in; migration path to any agent framework is feasible | ✅ PASS |
| **Self-Hostable** | ✅ YES | No external service dependencies; runs entirely local; MCP server + scratchpad + agent files all version-controlled; MANIFESTO.md § Local-Compute-First axiom enforced | ✅ PASS |
| **Open Source** | ✅ YES | Apache 2.0 license; full source code available; no proprietary components; agentskills.io specification is CC BY-SA 4.0 (compatible) | ✅ PASS |

**Overall Verdict**: ✅ **DogmaMCP qualifies as an open harness** — 5/6 criteria fully met, 1/6 partially met with tracked mitigation (issue #552).

---

## 3. Pattern Catalog

### Pattern 1: File-Based Memory Substrate (Canonical Example)

**Definition**: Agent memory persists as plain-text Markdown files in a version-controlled directory (`.tmp/<branch>/<date>.md`), with write-back discipline enforced by agent workflow and session lifecycle hooks. Memory is user-owned, readable, and editable without proprietary tooling.

**Evidence**: DogmaMCP scratchpad architecture (from [scratchpad-architecture-decision.md](./scratchpad-architecture-decision.md)):
- **Per-branch, per-day files**: One file per session day, organized by Git branch slug
- **Append-only workflow**: Agents append findings under `## <AgentName> Output` headings
- **Write-back requirement**: All delegated agents must write findings to scratchpad before returning control (prevents context-window-only state loss)
- **Cross-session continuity**: Executive reads today's file first before delegating to avoid re-discovery
- **Programmatic annotation**: `prune_scratchpad.py --annotate` adds line-range anchors to headings for durable linking

**Quote from AGENTS.md**:
> "Use the active session file for inter-agent handoff notes, gap reports, and aggregated sub-agent results."

**Implications**:
- **No lock-in**: Memory is plain text; user can migrate to any system by reading `.tmp/` files
- **Auditability**: Every agent interaction leaves a durable trace; session summaries encode decision rationale
- **Governance-as-code**: Scratchpad conventions (heading structure, write-back discipline) are encoded in AGENTS.md and enforced by session-management skill
- **Tradeoff**: Lacks schema enforcement (YAML frontmatter not validated); lacks structured query (no FTS5 index yet)

**Contrast with proprietary harnesses**:
- **LangSmith** (LangChain's observability platform): State stored on LangSmith server; no local persistence; switching providers means abandoning traces
- **Claude Managed Agents**: Memory fully server-side; zero visibility into what is stored; no export mechanism documented

---

### Pattern 2: Proprietary Memory Enclosure (Anti-Pattern)

**Definition**: Agent harness stores memory in a proprietary format or remote server, preventing user inspection, export, or migration to alternative platforms. Memory becomes the lock-in vector — users cannot leave without abandoning accumulated context.

**Evidence**: Harrison Chase (LangChain CEO) email assistant lock-in example (from [harness-memory-governance.md](./harness-memory-governance.md)):

> "I have an email assistant internally. It's built on top of a template in Fleet... This platform has memory built in, so as I interacted with my email assistant over the past few months it built up memory. A few weeks ago, my agent got deleted by accident. I was pissed! I tried to create an agent from the same template - but the experience was so much worse. I had to reteach it all my preferences, my tone, everything."

**Escalation Ladder** (from LangChain harness blog):
1. **Mild**: Stateful APIs (OpenAI Responses API) — state stored on vendor server; switching models means abandoning threads
2. **Bad**: Closed harnesses (Claude Agent SDK) — harness behavior unknown; memory shape non-transferable
3. **Worst**: Full harness behind API (Claude Managed Agents) — zero visibility, zero control, zero portability

**Implications**:
- **Experiential lock-in**: User preferences, learned behavior, and accumulated context create switching costs beyond API stickiness
- **Vendor power asymmetry**: Platform controls memory lifecycle (retention, compaction, deletion) without user consent
- **Governance failure**: Organizations cannot audit what an agent "knows" or enforce memory policies (e.g., PII redaction, retention limits)

**DogmaMCP mitigation**: File-based scratchpad prevents this pattern — user always has read/write access to memory, can git-track changes, and can migrate by reading plain text.

---

### Pattern 3: MCP-as-Harness (Emerging Pattern)

**Definition**: Model Context Protocol (MCP) is used not just as a tool-calling interface, but as the **harness abstraction layer** — decoupling agent orchestration from model provider APIs. MCP servers expose domain-specific tools (scratchpad query, provenance lookup, source caching) that any MCP-compatible LLM can invoke, creating model-agnostic workflows.

**Evidence**: DogmaMCP integration (from Phase 1 corpus review):
- **MCP server** (`mcp_server/dogma_server.py`): Exposes 8 governance tools (check_substrate, validate_agent_file, scaffold_agent, query_docs, prune_scratchpad, etc.)
- **Tool-based memory access**: `prune_scratchpad(dry_run=true)` replaces manual `cat .tmp/...` calls — memory becomes MCP-mediated, not filesystem-direct
- **Audience isolation**: `audience:["user"]` pattern prevents prompt injection from externally-sourced content (from [mcp-a2a-scratchpad-query.md](./mcp-a2a-scratchpad-query.md))
- **Standards compliance**: MCP JSON-RPC 2.0, MCP Tools API, MCP Inspector integration (issues #504, #505)

**Quote from MCP spec** (via agentskills.io):
> "MCP is a open protocol that standardizes how applications interact with context and tools, enabling developers to build more capable and flexible AI systems."

**Implications**:
- **Model portability**: Any LLM that supports MCP can use DogmaMCP tools without code changes
- **Harness composability**: MCP servers can be mixed/matched — one for memory, one for observability, one for code search
- **Governance substrate**: Tools encode constraints (e.g., `validate_agent_file` enforces BDI structure before commit) — governance runs at tool layer, not prompt layer
- **Tradeoff**: MCP is Anthropic-led (vendor risk); not yet widely adopted outside Anthropic ecosystem (VS Code, Claude Desktop)

**Emerging adoption**:
- **agentskills.io**: Anthropic's skill packaging standard aligns with MCP (YAML frontmatter + Markdown body)
- **agents.md**: OpenAI's agent metadata spec is MCP-compatible (YAML frontmatter convention)
- **VS Code Custom Agents**: Microsoft's .agent.md format extends agents.md with tool scoping + handoff graph (MCP tool registry integration)

---

## 4. Comparative Analysis

### Competitor Platform Survey

| Platform | Model-Agnostic? | Memory Approach | Export Format? | Self-Hostable? | License | Open Harness? |
|----------|----------------|-----------------|----------------|----------------|---------|---------------|
| **LangChain/Deep Agents** | ✅ Yes (OpenAI/Anthropic/Google) | Short-term: conversation history; Long-term: optional (via LangSmith or custom retrieval) | ❌ Not documented | ⚠️ Partial (backend optional; LangSmith is SaaS) | MIT | ⚠️ PARTIAL (harness is open; observability is proprietary) |
| **Letta** (formerly MemGPT) | ✅ Yes | Stateful agents with explicit memory management; memory editing primitives; positions memory as core harness domain | ❌ Not documented | ✅ Yes | Apache 2.0 | ✅ YES (memory-first open harness) |
| **mem0** | ✅ Yes (memory layer, not full harness) | Cross-session memory store (user/agent/session scoped); memory-as-a-service | ❌ Not documented | ✅ Yes (self-hosted mode) | Apache 2.0 | ⚠️ PARTIAL (memory layer only; no orchestration) |
| **DogmaMCP** (this project) | ✅ Yes (MCP-based) | File-based scratchpad (`.tmp/` per-branch per-day); FTS5 index (planned); MCP query tools | ⚠️ Planned (issue #552) | ✅ Yes | Apache 2.0 | ✅ YES (governance-first open harness) |

**Key Differentiators**:
1. **Letta**: Memory-first architecture; explicit memory primitives (edit, summarize, forget); CTO quote positions memory as inseparable from harness
2. **mem0**: Memory-as-a-service (not a full harness); works with any LLM; focuses on retrieval optimization not orchestration
3. **LangChain/Deep Agents**: Production-grade harness with human-in-the-loop; observability via LangSmith (proprietary); no documented memory export
4. **DogmaMCP**: Governance-as-substrate; values encoded in agent workflows; MCP-mediated memory; scratchpad is plain Markdown

**DogmaMCP Positioning**: **Governance-first open harness** — distinguishes from memory-first (Letta/mem0) and proprietary (LangSmith) by encoding values (Endogenous-First [MANIFESTO.md § 1 Endogenous-First], Local-Compute-First [MANIFESTO.md § 3 Local-Compute-First]) directly into substrate.

---

## 5. Recommendations

### R1: BENCHMARK Scratchpad Maturity Against Competitors

**Action**: Implement four maturity features in issue #552 to achieve feature parity with Letta/mem0:
1. **Schema enforcement**: YAML frontmatter validation (session_id, date, branch, status)
2. **Structured export**: JSON/YAML output for migration (`prune_scratchpad.py --export json`)
3. **Programmatic query**: FTS5 index for cross-session retrieval (already designed in [mcp-a2a-scratchpad-query.md](./mcp-a2a-scratchpad-query.md))
4. **Standards compliance**: agentskills.io manifest metadata in scratchpad headers

**Target**: Feature parity with Letta memory primitives by end of Sprint 19.

**Success Criteria**:
- ✅ Scratchpad files pass schema validator
- ✅ `--export json` produces valid JSON with all session metadata
- ✅ FTS5 search returns relevant sessions for query `"rate-limit circuit-breaker"`
- ✅ agentskills.io manifest present in scratchpad frontmatter

**Linked Issue**: #552 (Scratchpad Memory Maturation Sprint)

---

### R2: POSITION DogmaMCP as Open Harness in README/Docs

**Action**: Update README.md and docs/ narrative to explicitly claim "open harness" positioning and contrast with proprietary alternatives.

**Narrative Elements**:
1. **Value Proposition**: "DogmaMCP is a governance-first open harness — model-agnostic, standards-based, user-owned memory, self-hostable, Apache 2.0"
2. **Lock-in Contrast**: Reference Harrison Chase email assistant example; position DogmaMCP as the lock-in-free alternative
3. **Standards Adoption**: Highlight MCP, agents.md, agentskills.io compliance
4. **Migration Stories**: Document real or hypothetical migration paths from LangSmith → DogmaMCP

**Target Artifacts**:
- `README.md` § "What is DogmaMCP?" section
- `docs/guides/getting-started.md` § "Why DogmaMCP?" comparison table
- `MANIFESTO.md` § Ethical Values — add "Open Harness" as instantiation of Local-Compute-First

**Success Criteria**:
- ✅ "Open harness" appears in README introduction
- ✅ Comparison table with LangChain/Letta/mem0/DogmaMCP
- ✅ At least one migration story documented

---

### R3: DOCUMENT Migration Paths from Proprietary Platforms

**Action**: Create migration guides for adopters escaping proprietary lock-in (LangSmith, Claude Managed Agents, OpenAI Assistants API).

**Guide Structure** (per source platform):
1. **Export Instructions**: How to extract memory/state from source platform (if possible)
2. **Conversion Script**: Map source format → DogmaMCP scratchpad Markdown
3. **Validation**: Verify converted data matches session structure
4. **Governance Overlay**: How to encode source platform's implicit policies as AGENTS.md constraints

**Example Migration**: **LangSmith → DogmaMCP**
- Export LangSmith traces via SDK (`langsmith.list_runs(project_name=...)`)
- Convert traces → scratchpad entries under `## Trace Import` heading
- Map LangSmith projects → Git branches
- Encode LangSmith retry policies as AGENTS.md constraints

**Target Artifact**: `docs/guides/migrating-from-proprietary-harnesses.md`

**Success Criteria**:
- ✅ At least one full migration example (LangSmith or Claude Managed Agents)
- ✅ Conversion script committed to `scripts/migrate_from_<platform>.py`
- ✅ Validation test ensures converted data passes scratchpad schema

---

## 6. Related Dogma Research

- [harness-memory-governance.md](./harness-memory-governance.md) — Core research validating open harness as lock-in mitigation; confirms memory is core harness responsibility (H2); defines proprietary lock-in via memory enclosure (H3)
- [mcp-a2a-scratchpad-query.md](./mcp-a2a-scratchpad-query.md) — MCP-mediated scratchpad query design; FTS5 index architecture; audience isolation for prompt injection prevention
- [scratchpad-architecture-decision.md](./scratchpad-architecture-decision.md) — Three-layer state architecture (MCP session / scratchpad / git); per-day file structure; write-back discipline
- [platform-agnosticism.md](./platform-agnosticism.md) — Hard vs. soft coupling audit; "Embrace + Document Migration" posture; .agent.md (hard-coupled to VS Code) vs. SKILL.md (portable)

---

## 7. Sources

### Endogenous Corpus (6 docs)
1. [harness-memory-governance.md](./harness-memory-governance.md)
2. [mcp-a2a-scratchpad-query.md](./mcp-a2a-scratchpad-query.md)
3. [scratchpad-architecture-decision.md](./scratchpad-architecture-decision.md)
4. [mcp-state-architecture.md](./mcp-state-architecture.md)
5. [platform-agnosticism.md](./platform-agnosticism.md)
6. [prune_scratchpad.py](../../scripts/prune_scratchpad.py) + [session-management.md](../../docs/guides/session-management.md)

### External Sources (9 cached)
1. https://blog.langchain.com/your-harness-your-memory/ — LangChain harness-memory framing; Harrison Chase email assistant lock-in example
2. https://x.com/sarahwooders/status/2040121230473457921 — Sarah Wooders (Letta CTO) quote: "memory is a core harness responsibility"
3. https://www.letta.com/ — Letta homepage (stateful agents)
4. https://github.com/letta-ai/letta — Letta GitHub repo
5. https://github.com/mem0ai/mem0 — mem0 GitHub repo (memory-as-a-service)
6. https://docs.langchain.com/oss/python/deepagents/overview — LangChain Deep Agents overview
7. https://agentskills.io/home — agentskills.io homepage
8. https://agentskills.io/specification — agentskills.io spec
9. https://github.com/openai/agents.md — agents.md standard (OpenAI)
10. https://www.datadoghq.com/blog/ai/harness-first-agents/ — Datadog harness-first blog

### Standards Referenced
- **MCP** (Model Context Protocol): Anthropic-led protocol for tool calling; JSON-RPC 2.0; MCP Tools API
- **agents.md**: OpenAI standard for agent metadata (YAML frontmatter + Markdown body)
- **agentskills.io**: Anthropic/community standard for skill packaging (compatible with agents.md)
