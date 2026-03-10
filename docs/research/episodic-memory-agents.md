---
title: "Episodic and Experiential Memory for Agent Sessions"
research_issue: "#13"
status: Final
date: 2026-03-09
closes_issue: 13
sources_read: 8
---

# Episodic and Experiential Memory for Agent Sessions

> **Status**: Final
> **Research Question**: How can the EndogenAI agent fleet implement episodic/experiential memory — persistent session recall beyond the current scratchpad window — without requiring a third-party cloud memory provider?
> **Date**: 2026-03-09

---

## 1. Executive Summary

The EndogenAI agent fleet currently relies on a per-session scratchpad (`.tmp/<branch>/<date>.md`) as its sole persistence layer. Between sessions, agents re-discover context from scratch. This research evaluates four local-capable episodic memory libraries — **mem0**, **Letta** (MemGPT successor), **Cognee**, and **graphiti** — against the EndogenAI Local Compute-First axiom (`MANIFESTO.md §3`) and the current scratchpad-based session architecture.

**Core finding**: All four libraries offer episodic memory capability, but none integrate cleanly into the current file-based agent architecture without a dedicated local inference stack. The prerequisite — a confirmed local compute baseline (`OPEN_RESEARCH.md` item 1: local models via Ollama or LM Studio) — remains **open**. No library adoption should be approved before that baseline is established.

**Governing axiom**: `MANIFESTO.md §3 — Local Compute-First` applies directly. Episodic memory with a cloud provider (e.g., mem0's managed `MemoryClient`) violates the axiom. Only local-first deployment modes are in scope.

**Provisional recommendation**: **Monitor — do not adopt yet.** Cognee is the most architecturally compatible option for future adoption once the local compute baseline is resolved. Graphiti offers the richest memory model but introduces a Neo4j dependency that conflicts with the project's zero-infrastructure preference. Letta (MemGPT) and mem0's local mode are viable second-tier options.

**Unlock condition for Phase 2**: Completion of `OPEN_RESEARCH.md` item 1 (local compute baseline). Once a local inference stack is confirmed and documented in `docs/guides/local-compute.md`, this research should be revisited with a concrete integration design.

---

## 2. Hypothesis Validation

### H1 — Local-only memory is possible without cloud providers

**Validated (conditional)**. All four libraries support local-only operation modes, but each requires a running local embedding model and/or local inference stack.

| Library | Local Mode | Cloud Option | Local Embedding Required |
|---------|-----------|--------------|--------------------------|
| mem0 | `Memory()` class (local SQLite + qdrant-local) | `MemoryClient` (managed, cloud) | Yes — local LLM + embedding model |
| Letta | Self-hosted Letta server | Letta Cloud | Yes — local model via `/v1/models` |
| Cognee | `cognee.config.set_llm_provider("ollama")` | OpenAI/Anthropic endpoint | Yes — Ollama provider supported |
| graphiti | Self-hosted Neo4j + embedding model | None documented | Yes — requires Neo4j + embedding |

**Anti-pattern**: Using `MemoryClient` from mem0's managed API, or Letta Cloud, because "it's faster to set up" — this violates Local Compute-First (`MANIFESTO.md §3`). The double-violation (cloud inference + cloud state) mirrors the canonical anti-pattern at `MANIFESTO.md §3 line 140–142`.

### H2 — Episodic memory can integrate with the existing scratchpad convention

**Partially validated**. The scratchpad (`.tmp/<branch>/<date>.md`) is file-based, human-readable, and git-managed. Any memory library integration would need to either:
- (a) Write structured episodic records to the scratchpad as additional sections, or
- (b) Maintain a separate local store (SQLite, graph DB) indexed by branch + date as the session key.

Option (a) preserves the file-only architecture at the cost of scratchpad bloat. Option (b) introduces a new infrastructure component outside the current zero-dependency model. Neither option is blocked — but option (b) requires the local compute baseline before it can be evaluated.

### H3 — Episodic memory reduces redundant research re-discovery

**Plausible but unverified**. The research scratchpad already serves as a written record of what was learned in a session. The gap is between sessions: today's scratchpad is read by tomorrow's session only because the Orchestrator's Session Start step explicitly re-reads it. Without that explicit step, context is lost.

A library-backed episodic store would allow retrieval-augmented recall (e.g., "what did we decide about X in previous sessions?") without requiring the agent to read every prior scratchpad linearly. This is a genuine capability gap. Whether the overhead of maintaining a local graph or vector store justifies the benefit for a project at this scale is an open question.

### H4 — graphiti's episodic/semantic/community layer model maps well to EndogenAI session types

**Validated in principle**. Graphiti's three-layer model (episodic — raw session events; semantic — extracted facts; community — cross-session clusters) maps directly to EndogenAI's three layers:
- Episodic layer ← per-session scratchpad entries
- Semantic layer ← extracted decisions, patterns, axiom citations
- Community layer ← cross-issue research themes (e.g., "value encoding" as a recurring cluster)

However, the Neo4j dependency makes this the most infrastructure-heavy option. For a single-developer project with a zero-infrastructure preference, this is a significant adoption cost.

---

## 3. Pattern Catalog

### Pattern M1 — Scratchpad-as-Episodic-Index (Zero Dependency)

**Context**: Session continuity is needed but no local memory library has been adopted yet.

**How it works**: The existing scratchpad convention already provides episodic memory at the session level. Cross-session continuity is provided by the Session Start step (re-reading the scratchpad from disk). For multi-session projects, a `## Session History` section in the scratchpad acts as a lightweight episodic index.

**Canonical example**:
```markdown
## Session History

| Date | Branch | Key decisions |
|------|--------|---------------|
| 2026-03-06 | feat/xml-migration | Adopted XML hybrid schema; OQ-12-1/2/3 resolved |
| 2026-03-09 | research/bubble-clusters | Phase A–C complete; episodic memory deferred |
```

**Anti-pattern**: Skipping the Session Start scratchpad re-read because "the compact summary should have it" — the compact summary is lossy; only the on-disk scratchpad is authoritative (`docs/guides/session-management.md`).

**Applicability**: All current sessions. No dependencies. Available immediately.

---

### Pattern M2 — Cognee Local Graph Memory (Deferred — Requires Local Compute Baseline)

**Context**: Local compute baseline (`OPEN_RESEARCH.md` item 1) is confirmed. An Ollama instance is running locally. Multiple research sessions have accumulated enough context that linear scratchpad reads are becoming costly.

**How it works**: Cognee with `cognee.config.set_llm_provider("ollama")` indexes session scratchpads into a local knowledge graph. The agent retrieves relevant prior context via `cognee.search(SearchType.INSIGHTS, "value encoding")` rather than parsing every prior scratchpad file.

**Canonical example**:
```python
import cognee
import asyncio

cognee.config.set_llm_provider("ollama")
cognee.config.set_embedding_model("ollama/nomic-embed-text")

async def index_session(scratchpad_path: str, session_id: str):
    with open(scratchpad_path) as f:
        content = f.read()
    await cognee.add(content, dataset_name=session_id)
    await cognee.cognify()

async def recall(query: str):
    results = await cognee.search(SearchType.INSIGHTS, query)
    return results
```

**Anti-pattern**: Using `cognee.config.set_llm_provider("openai")` or `"anthropic"` as "it works out of the box" — this violates Local Compute-First. The local provider configuration is mandatory.

**Applicability**: Deferred. Requires `OPEN_RESEARCH.md` item 1 resolved and `docs/guides/local-compute.md` published.

---

### Pattern M3 — mem0 Local Mode (Deferred — Requires Local Compute Baseline)

**Context**: Same prerequisite as M2. Preference for a simpler API than graph-based Cognee.

**How it works**: mem0's `Memory()` class (not `MemoryClient`) uses a local SQLite store and optional local vector database. Each significant decision or pattern from a session is added as a structured memory entry keyed by agent role.

**Canonical example**:
```python
from mem0 import Memory

config = {
    "llm": {"provider": "ollama", "config": {"model": "llama-3.2-3b-instruct"}},
    "embedder": {"provider": "ollama", "config": {"model": "nomic-embed-text"}},
    "vector_store": {"provider": "qdrant", "config": {"host": "localhost", "port": 6333}},
}

m = Memory.from_config(config)

# Add episodic record after session close
m.add(
    "Phase A complete: bubble-clusters-substrate.md committed. Pattern B1 (calibrated membrane permeability) defined.",
    user_id="executive-orchestrator",
    metadata={"branch": "research/bubble-clusters-phase-a-neuroanatomy", "date": "2026-03-09"}
)

# Retrieve before session start
relevant = m.search("bubble cluster substrate", user_id="executive-orchestrator")
```

**Anti-pattern**: Using `MemoryClient` (managed cloud API) instead of `Memory()` (local class).

**Applicability**: Deferred. Same prerequisites as M2. Simpler API but weaker cross-session graph reasoning than Cognee.

---

## 4. Recommendations

### R1 — Do not adopt any episodic memory library until local compute baseline is confirmed

The prerequisite (`OPEN_RESEARCH.md` item 1) remains open. All four libraries require a running local inference stack. Adopting any of them today means using cloud providers as the embedding/inference backend, which violates `MANIFESTO.md §3 — Local Compute-First`. This is a blocking constraint, not a preference.

**Action**: Defer all library adoption decisions until `docs/guides/local-compute.md` is published and an Ollama or LM Studio local stack is confirmed.

### R2 — Adopt Pattern M1 (Scratchpad-as-Episodic-Index) immediately

The `## Session History` table in the scratchpad is a zero-dependency, zero-infrastructure episodic memory layer. It should be added to the scratchpad template and to `docs/guides/session-management.md` as a recommended section for projects with multiple sessions on the same research theme.

**Effort**: XS. No code changes required. Editorial update to session-management.md.

### R3 — Cognee is the preferred library for future adoption

Once the local compute baseline is resolved, Cognee is the recommended library for the following reasons:
1. Native Ollama provider support (`cognee.config.set_llm_provider("ollama")`) — direct alignment with the local compute baseline.
2. Graph-based knowledge structure matches EndogenAI's session architecture (scratchpad → decision graph → cross-session clusters).
3. Local-first design philosophy documented by the maintainers.
4. No mandatory infrastructure dependencies beyond a local Ollama instance (unlike graphiti's Neo4j requirement).

### R4 — Graphiti: monitor, do not adopt

Graphiti's three-layer model (episodic/semantic/community) is theoretically the best fit for EndogenAI's session architecture. However, the Neo4j dependency is a significant adoption cost for a single-developer project. Monitor the project for a SQLite or DuckDB backend option; adopt if the infrastructure requirement is reduced.

### R5 — Letta (MemGPT): monitor, do not adopt

Letta's stateful agent architecture is designed for persistent long-running agents, not for the EndogenAI pattern of ephemeral per-session agents with file-based state. The self-hosted Letta server introduces a persistent background process that conflicts with the project's session-bounded model. Monitor for embedding-focused lightweight usage patterns.

---

## 5. Dependency Gap

This research is a soft prerequisite for the full multi-session drift detection feature described in `docs/research/llm-behavioral-testing.md §5 — Dependency Gap`. The `validate_session.py --drift-check` capability requires cross-session episodic memory to detect value drift over time. Until episodic memory is implemented, `validate_session.py` is limited to single-session Constitutional AI self-critique (Tier 1 + Tier 2 intra-session checks only).

**Unlock sequence**:
1. `OPEN_RESEARCH.md` item 1 resolved → `docs/guides/local-compute.md` published
2. Cognee local integration prototyped (Pattern M2 above)
3. `validate_session.py --drift-check` flag implemented using Cognee cross-session recall
4. Issue #74 (`docs/research/llm-behavioral-testing.md`) updated with full test-framework section

---

## Sources

1. mem0 documentation — local `Memory()` class and configuration: https://docs.mem0.ai/overview
2. Letta (MemGPT) documentation — self-hosted server and stateful agents: https://docs.letta.com
3. Cognee documentation — graph-based episodic memory, Ollama provider: https://github.com/topoteretes/cognee
4. graphiti documentation — episodic/semantic/community layers, Neo4j: https://github.com/getzep/graphiti
5. `docs/research/OPEN_RESEARCH.md` — item 1 (local compute baseline), item 7 (episodic memory): endogenous
6. `MANIFESTO.md §3 — Local Compute-First`: endogenous
7. `docs/guides/session-management.md` — scratchpad convention, Session Start re-read requirement: endogenous
8. `docs/research/llm-behavioral-testing.md §5 — Dependency Gap`: endogenous (this milestone)
