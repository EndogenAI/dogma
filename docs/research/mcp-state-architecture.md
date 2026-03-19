---
title: "MCP State Architecture — Stateless vs. Stateful Agent Coordination"
status: "Final"
research_issue: 264
closes_issue: 264
date: 2026-03-15
sources:
  - https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle
  - https://langchain-ai.github.io/langgraph/concepts/persistence/
  - https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html
  - https://platform.openai.com/docs/assistants/overview
  - https://redux.js.org/introduction/motivation
  - docs/guides/session-management.md
  - AGENTS.md
  - .github/agents/executive-orchestrator.agent.md
---

# MCP State Architecture — Stateless vs. Stateful Agent Coordination

> **Status**: Final
> **Research Question**: Should MCP servers in the EndogenAI fleet be stateless or stateful? What state management patterns exist in multi-agent orchestration frameworks, and what coordination pattern best fits the endogenic architecture?
> **Date**: 2026-03-15
> **Related**: [`docs/guides/session-management.md`](../guides/session-management.md) · [`AGENTS.md` §Agent Communication](../AGENTS.md#agent-communication) · [`docs/research/agents/local-mcp-frameworks.md`](agents/local-mcp-frameworks.md) · [`docs/research/agents/agentic-research-flows.md`](agents/agentic-research-flows.md)

---

## 1. Executive Summary

MCP (Model Context Protocol, Anthropic 2024) defines **stateful sessions at the protocol level** — capability negotiation, sampling preferences, and resource subscriptions persist for the lifetime of a client-server connection. However, individual tool calls within a session are **stateless request/response exchanges**: no implicit agent-level state travels between tool invocations. The protocol was intentionally designed this way to allow stateless server implementations.

This research surveyed five state management approaches across leading multi-agent frameworks (LangGraph, AutoGen, OpenAI Assistants API, CrewAI) and compared against the EndogenAI fleet's current file-based state model. Four hypotheses were submitted for validation; three are confirmed, one requires reframing.

The key finding: **state should live at three distinct layers** in the EndogenAI fleet — (1) MCP session layer for capability/auth negotiation, (2) scratchpad layer for cross-phase orchestration progress, and (3) git layer for durable, committed knowledge. A fourth, transient layer — in-memory agent state — is appropriate only within a single agent invocation and must not be relied upon across invocations.

The Redux-analogue pattern is partially present: the `.tmp/` scratchpad functions as a de facto Redux store (single source of truth, append-only writes), but lacks type/shape enforcement, conflict detection for concurrent writers, and programmatic state query. Adding a lightweight programmatic query layer (`scripts/validate_session_state.py`) would close the primary coherence gap without requiring a full state management framework.

---

## 2. Hypothesis Validation

### H1 — MCP servers should be stateless within tool calls

**Verdict**: CONFIRMED — stateless servers are the idiomatic MCP pattern

**Evidence**: The MCP specification (2025-03-26 revision) describes the lifecycle as three phases: **Initialize** (capability negotiation, performed once), **Operation** (tool calls, resource access, prompting), and **Shutdown**. The Operation phase is explicitly request/response: each tool call carries its full input payload and returns a complete result. The server is not expected to hold intermediate state between calls.

In the EndogenAI fleet, MCP servers exposed via stdio (filesystem tools, git tools, script execution) should remain stateless: they receive a complete request, execute, and return a result. Session identity (which branch, which user) should be passed as part of the tool call arguments, not stored in server memory.

**Canonical example**: The `git` MCP server receives `{"op": "log", "args": ["--oneline", "-5"]}` and returns the output. No session state is needed because the working directory is implicitly scoped by how the server was launched. This is identical to a REST endpoint — stateless, idempotent, composable. This adheres to the **MANIFESTO.md §3** ([MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first)).

**Anti-pattern**: A MCP server that accumulates agent intent across multiple tool calls in a local Python dict and changes its behavior based on prior calls within the session. When a session is resumed from a new VS Code window, the server starts fresh with no memory of the prior session's accumulated state — silently producing inconsistent behavior.

---

### H2 — Cross-phase orchestration state belongs in the file layer, not the MCP session layer

**Verdict**: CONFIRMED — file-based scratchpad is the correct state layer for cross-phase coherence

**Evidence**: The primary state management challenge in the EndogenAI fleet is **cross-phase coherence**: the Orchestrator must remember what Phase 1 produced before delegating Phase 2, even if a context window boundary occurs between phases. This exceeds what any single MCP session can store — MCP sessions are per-connection, not per-sprint.

Comparison with external frameworks:

| Framework | State Mechanism | Persistence | Cross-phase |
|-----------|----------------|-------------|-------------|
| LangGraph | State graph + checkpointer (SQLite/Redis/Postgres) | Durable (configurable) | ✅ First-class |
| AutoGen  | Message history per agent | In-memory (session-local) | ❌ Lost on restart |
| OpenAI Assistants | Thread objects (cloud-hosted) | Durable (cloud) | ✅ But violates LCF |
| CrewAI | Task output chaining | In-memory | ❌ No cross-run persistence |
| EndogenAI | `.tmp/<branch>/<date>.md` | File (gitignored) | ✅ Survives context window boundary |

The endogenic scratchpad model outperforms AutoGen and CrewAI on cross-phase persistence, matches LangGraph on durability (file vs. DB), and respects Local Compute-First ([MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first)) (no cloud state ala Assistants API). The gap vs. LangGraph is in **state shape enforcement** and **programmatic queryability** — LangGraph can answer "what is the current state of Phase 3?" programmatically; the scratchpad requires LLM parsing.

**Canonical example**: An Orchestrator finishes Phase 2 Scout output and writes it under `## Scout Output` in the scratchpad. When the context window resets and Phase 3 Synthesizer begins, it reads `## Scout Output` and has full fidelity to what Phase 2 produced — without re-running Phase 2. This is the scratchpad-as-state pattern working correctly.

**Anti-pattern**: An Orchestrator stores Phase 2 results only in the context window (never writes to scratchpad), then delegates Phase 3 synthesis. When the context window compacts, Phase 3 starts blind. The Synthesizer must re-request Scout results at full token cost. Confirmed failure mode documented in [`docs/guides/session-management.md`](../guides/session-management.md#design-rationale).

---

### H3 — A Redux-analogue centralized state store would improve cross-phase coherence

**Verdict**: PARTIALLY CONFIRMED — the Redux structural insight is valid, but full Redux implementation is disproportionate to fleet complexity

**Evidence**: Redux's three principles map directly onto endogenic session management:

| Redux principle | EndogenAI equivalent | Gap |
|-----------------|---------------------|-----|
| Single source of truth | `.tmp/<branch>/<date>.md` | ✅ Already implemented |
| State is read-only (actions only) | Append-only section writes | ⚠️ Partially enforced (convention, not code) |
| Pure reducer functions | `prune_scratchpad.py` (compress) | ❌ No reducer pattern; writes are freeform |

The Redux insight that is most applicable: **state transitions should be explicit, named, and reversible** (via git history). In the scratchpad, phases should write named state transitions (`## Phase N Complete`, `## Phase N Output`), and `scripts/validate_session_state.py` already partially queries this (via heading grep). The gap is shape enforcement and conflict detection.

Full Redux (with selector subscriptions, time-travel debugging, middleware) would be over-engineered for a fleet of 9 executive agents using a Markdown scratchpad. The incremental improvement is: add a structured frontmatter block to the scratchpad that records phase completion status as machine-parseable YAML, queryable by scripts.

---

### H4 — State management patterns in leading multi-agent frameworks converge on a shared model

**Verdict**: INCONCLUSIVE — frameworks diverge significantly; no single convergent pattern exists

**Evidence**: LangGraph (graph-database state), AutoGen (message-history state), Assistants API (cloud-thread state), and CrewAI (in-memory chaining) reflect fundamentally different philosophies about where state should live. The only convergent property is that **all frameworks acknowledge the need for state persistence beyond a single model invocation** — they differ only on where and how.

For EndogenAI, the right lens is not "which framework's state model should we adopt?" but "which state layer is appropriate for each type of state?" — which H1-H3 answer directly.

---

## 3. Pattern Catalog

### P1 — Three-Layer State Architecture

**Description**: Organize all agent state into three explicit layers, each with a distinct scope and persistence model.

**Layers**:
1. **MCP Session Layer** (`stateless per tool call`) — capability negotiation, auth tokens, resource subscriptions. Scope: one client-server connection. No cross-invocation persistence required. Implemented in mcp.json config.
2. **Scratchpad Layer** (`cross-phase coherence`) — phase outputs, scout findings, handoff notes, session summaries. Scope: one sprint branch. Persists across context window boundaries. Implemented in `.tmp/<branch>/<date>.md`.
3. **Git Layer** (`durable knowledge`) — committed research docs, scripts, agent files. Scope: permanent. Survives all session and branch boundaries. The substrate.

**Canonical example**: Orchestrator begins Wave 1 research. MCP session establishes file-system and git tools (Layer 1). Scout outputs findings to scratchpad Phase 2 section (Layer 2). Archivist commits D4 doc to `docs/research/` (Layer 3). The three layers never overlap — no scratchpad state is committed to git, no MCP session state is written to the scratchpad.

**Anti-pattern**: Writing phase progress to both a `## Phase 2 Complete` scratchpad section AND a git commit message of `"chore: complete phase 2"` — creating two out-of-sync state representations that diverge when only one is updated.

---

### P2 — Scratchpad-as-Redux-Store

**Description**: Treat the scratchpad as a single-source-of-truth Redux store with named, append-only state transitions. Each appendable section is a dispatched "action" with a named type.

**Implementation conventions**:
- Named section headings = action types (`## Scout Output`, `## Phase N Review Output`)
- Writes are append-only, never overwrites (redux state immutability)
- `scripts/validate_session_state.py` is the "selector" layer — queries state by heading grep
- No agent reads another agent's sections directly (state isolation)

**Canonical example**: Executive PM dispatches `## Phase 1 Issue Seeding Output` to the scratchpad (analogous to dispatching `{type: 'PHASE_1_COMPLETE', payload: issues}`). The Orchestrator reads this section to determine Phase 2 inputs. No direct agent-to-agent communication occurs.

**Anti-pattern**: Two agents writing to the same scratchpad section concurrently (race condition analog). Mitigation: enforce one-agent-one-section conventions; each agent writes only to its own named section.

---

### P3 — Stateless-Out, Stateful-File-Back Server Architecture

**Description**: Design all MCP servers to be stateless (no in-memory session state between tool calls), while externalizing all persistent state to the file system or git.

**When to use**: Any MCP server exposed via stdio or HTTP to the EndogenAI fleet.

**Implementation**: Tool calls receive complete context in their arguments; results are complete in their return values. Any state that needs to persist to the next tool call is written to a file or git object as part of the tool's execution.

---

## 4. Recommendations

**R1 — Maintain file-based state; add programmatic query (HIGH PRIORITY)**
Extend `scripts/validate_session_state.py` to query scratchpad phase status via structured frontmatter YAML block. Add a `## Session State` YAML block to the scratchpad template in `prune_scratchpad.py --init`. This closes the LangGraph gap without adding a dependency. See [issue #264](https://github.com/EndogenAI/dogma/issues/264).

**R2 — Document the Three-Layer State model in session-management.md**
Add an explicit Three-Layer State section to `docs/guides/session-management.md` that names the MCP session layer, scratchpad layer, and git layer with their boundaries. This prevents agents from conflating layers.

**R3 — Keep MCP servers stateless**
Add a guardrail to `.github/agents/AGENTS.md` (or the MCP server authoring guide, once one exists): MCP server implementations must not store cross-invocation state in memory. Any persistent state must be externalized to the file system.

**R4 — Defer Redux-style middleware and time-travel (LOW PRIORITY)**
A full Redux middleware pipeline (for tracing, rollback, and debugging) is architecturally sound but not warranted until the fleet scales beyond 9 executives and 20+ sub-agents. Document as a Wave 4 consideration.

All four recommendations instantiate the **Endogenous-First** axiom ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)): they build from the existing scratchpad substrate rather than adopting external state stores, reinforcing that endogenous knowledge infrastructure is the primary medium for agent coordination.

---

## 5. Sources

### Internal

- [`AGENTS.md` §Agent Communication](../AGENTS.md#agent-communication) — `.tmp/` scratchpad as cross-agent memory substrate; section ownership rules
- [`docs/guides/session-management.md`](../guides/session-management.md) — scratchpad architecture, design rationale, confirmed failure modes
- [`.github/agents/executive-orchestrator.agent.md`](../../.github/agents/executive-orchestrator.agent.md) — Orchestrator session state management, context window alert protocol
- [`docs/research/agents/local-mcp-frameworks.md`](agents/local-mcp-frameworks.md) — MCP stateless session architecture, HTTP vs. stdio patterns
- [`scripts/validate_session_state.py`](../../scripts/validate_session_state.py) — programmatic session state query

### External

- MCP Specification (Anthropic, 2025-03-26): [modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle](https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle) — stateful session lifecycle, Operation phase request/response semantics
- LangGraph Persistence Concepts (LangChain, 2025): [langchain-ai.github.io/langgraph/concepts/persistence/](https://langchain-ai.github.io/langgraph/concepts/persistence/) — checkpointer API, state graph persistence, cross-invocation coherence
- AutoGen Memory Guide (Microsoft, 2025): [microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html) — per-agent message history, in-memory state limitations
- OpenAI Assistants API (OpenAI, 2025): [platform.openai.com/docs/assistants/overview](https://platform.openai.com/docs/assistants/overview) — Thread-based persistent state (cloud-hosted); contrast with LCF requirements
- Redux Motivation (Redux, 2025): [redux.js.org/introduction/motivation](https://redux.js.org/introduction/motivation) — single source of truth, state immutability, predictable state transitions; structural analogy for scratchpad design
