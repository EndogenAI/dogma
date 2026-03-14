---
title: "Dynamic AI Agent Navigation: Graph Routing Algorithms for Decision Workflows"
status: "Draft"
research_issue: "203"
date: "2026-03-14"
---

# Dynamic AI Agent Navigation: Graph Routing Algorithms for Decision Workflows

> **Research question**: Is it feasible to replace static "if/then" decision trees in
> agent workflows with navigable weighted knowledge graphs, enabling classical routing
> algorithms (A\*, Dijkstra) to determine the most efficient, cost-effective, or
> reliable path to a goal state?
>
> **Date**: 2026-03-14
> **Research Issue**: #203
> **Related**: [`data/phase-gate-fsm.yml`](../../data/phase-gate-fsm.yml) (endogenous FSM);
> [`data/delegation-gate.yml`](../../data/delegation-gate.yml) (endogenous routing table);
> [`docs/research/endogenic-design-paper.md`](endogenic-design-paper.md) (H1, H4 framework)

---

## Executive Summary

Graph routing algorithms — A\*, Dijkstra, shortest-path traversal — are a natural fit
for agent navigation when workflow state can be encoded as a weighted directed graph.
This synthesis evaluates three architectural options (LangGraph, NetworkX, and native
FSM/YAML) against the three core research questions from issue #203: state-as-coordinates,
dynamic weighting, and Markdown-to-Graph schema design.

**Key finding**: This codebase already instantiates the core primitives. `data/phase-gate-fsm.yml`
is a working navigable state graph; `data/delegation-gate.yml` is a working routing table.
The highest-value next step is not adopting LangGraph, but extending these endogenous artifacts
with edge weights and a NetworkX-backed path-analysis script.

The **Algorithms Before Tokens** axiom (`MANIFESTO.md §2`) is directly instantiated by this
approach: encoding workflow routing as a data structure (YAML graph) that a deterministic
algorithm can traverse is strictly superior to re-deriving routing logic via token burn each
session.

---

## Hypothesis Validation

### H1 — State-as-Coordinates is tractable with existing FSM artifacts

**Hypothesis**: An agent's current "position" in a workflow can be represented as a
coordinate in a multi-dimensional state space, enabling graph-based navigation.

**Assessment**: **Confirmed — endogenous evidence exists.**

`data/phase-gate-fsm.yml` already encodes agent state as labeled nodes:
`INIT → PHASE_RUNNING → GATE_CHECK → COMPACT_CHECK → COMMITTED → CLOSED`. Each node
has explicit guard conditions (e.g., `workplan_file_exists AND scratchpad_session_start_written`).
This IS state-as-coordinates: the current FSM node plus the set of satisfied guard conditions
defines the agent's exact position in the workflow state space.

To triangulate position in a *multi-dimensional* space (phase × context-budget ×
active-issue × last-verdict), extend the FSM state serialization with additional axes:

```yaml
# Extended state coordinate vector (proposed)
current_state: GATE_CHECK
context_budget_used_pct: 0.42
active_issue: 234
last_verdict: null   # awaiting Review
tokens_burned: 14200
```

This 5-tuple uniquely identifies position in the workflow graph and enables routing
decisions (e.g., "if context_budget_used_pct > 0.85, prefer COMPACT_CHECK over
COMMITTED even if review is approved").

### H2 — Dynamic weighting via conditional edges is feasible but requires instrumentation

**Hypothesis**: Real-time cost signals (API latency, token cost, failure probability) can
be used to reroute agents mid-session, analogous to traffic-aware GPS navigation.

**Assessment**: **Partially confirmed — primitive exists in LangGraph; endogenous instrumentation
gap exists.**

LangGraph's `conditional_edge` primitive evaluates a Python callable at runtime to select
the next node. This is the dynamic weighting mechanism: the callable can incorporate live
cost signals (token usage from the session state, error counts, latency measurements) to
select the cheapest or most reliable next state.

For the endogenous codebase, `data/delegation-gate.yml` currently encodes *static* routing
edges. Dynamic weighting would require adding a `weight_fn` field to each edge, evaluated
at runtime by a script analogous to `scripts/validate_delegation_routing.py`.

**Blocker**: No session-cost instrumentation (`session_cost_log.json`) exists yet. Issue #131
(Cognee / local compute baseline) is a prerequisite for reliable cost-signal collection.
Dynamic weighting is architecturally sound but cannot be validated empirically until
instrumentation is in place.

### H3 — Markdown-to-Graph via YAML schema is already proven in this codebase

**Hypothesis**: A lightweight YAML schema can represent navigable graph structures in
documentation, bridging Markdown authoring and programmatic graph traversal.

**Assessment**: **Confirmed — `data/phase-gate-fsm.yml` is the canonical existence proof.**

The FSM YAML file uses a clean schema: `states:` dict → per-state `transitions:` array →
each transition has `event:`, `guard:`, and `next_state:` fields. This schema is already
parseable into a NetworkX `DiGraph` with two lines of Python:

```python
import networkx as nx, yaml
G = nx.DiGraph()
fsm = yaml.safe_load(open("data/phase-gate-fsm.yml"))["fsm"]
for state, defn in fsm["states"].items():
    for t in defn.get("transitions", []):
        G.add_edge(state, t["next_state"], event=t["event"], guard=t.get("guard",""))
```

Mermaid.js is a secondary representation: the existing `phase-gate-fsm.yml` can be
auto-converted to a `graph TD` Mermaid diagram for documentation. NetworkX also exports
to DOT format for Graphviz rendering.

---

## Pattern Catalog

**Canonical example**: FSM-as-Navigable-Graph

**What it is**: `data/phase-gate-fsm.yml` with NetworkX integration for path analysis.

**Why it works**:
1. Author the workflow as YAML (human-readable, version-controlled, diffable)
2. Parse into NetworkX `DiGraph` at analysis or validation time (no extra deps in hot path)
3. Run `nx.shortest_path(G, "INIT", "CLOSED")` to find the nominal happy path
4. Run `nx.all_simple_paths(G, "PHASE_RUNNING", "CLOSED")` to enumerate all paths and
   validate every path passes through GATE_CHECK (enforces the review gate invariant)
5. Add edge weights post-instrumentation to enable Dijkstra/A\* cost-optimal routing

**Endogenous reference**: `data/phase-gate-fsm.yml` (already committed); no new
library dependency for the baseline — NetworkX is already in `pyproject.toml`
(if not, add it; it is a zero-overhead addition).

**MANIFESTO.md alignment**: Instantiates **Endogenous-First** (`§1`) — scaffold from
the existing FSM artifact rather than importing LangGraph. Instantiates
**Algorithms Before Tokens** (`§2`) — deterministic path enumeration replaces
token-burn reasoning about "what comes next."

---

**Anti-pattern**: Importing LangGraph for Static Workflow Graphs

**What it is**: Adding LangGraph as a runtime dependency to encode a workflow that has
fewer than 20 states and no live LLM invocations at routing decision points.

**Why it fails**:
- LangGraph is an *LLM orchestration runtime* (Pregel-inspired, cloud-deployable,
  LangSmith-integrated). Its overhead is appropriate when agents call LLMs at every node.
- For pure workflow state machines (INIT → PHASE_RUNNING → GATE_CHECK), LangGraph
  introduces ~500KB of dependency surface for a task that 30 lines of NetworkX handles.
- LangGraph's durable-execution and streaming features are irrelevant for the synchronous,
  human-supervised session loop this codebase uses.
- Adopting LangGraph for static routing violates **Local Compute-First** (`MANIFESTO.md §3`):
  its production deployment path is LangSmith (cloud), not local-first.

**When LangGraph IS appropriate**:
- Multi-agent graphs where each node invokes an LLM
- Workflows requiring durable execution across network partitions
- Human-in-the-loop interrupts at specific graph nodes
- Real-time streaming of intermediate node outputs

---

**Pattern**: Delegation Gate as Weighted Digraph

The existing `data/delegation-gate.yml` encodes agent delegation routes as a static
adjacency list. This can be promoted to a weighted digraph:

```yaml
# Proposed extension (additive, non-breaking)
delegation_routes:
  Orchestrator:
    - target: Docs
      weight: 1.0          # nominal weight
      cost_fn: null         # no dynamic cost yet
    - target: Researcher
      weight: 1.0
      cost_fn: "session_cost_log.tokens_burned_by_agent"   # post-#131
```

NetworkX then enables: "given the current session state, which delegation path minimizes
expected token cost to reach the next committed phase?" — a Dijkstra query over the
weighted delegation graph.

---

## Recommendations

1. **Immediate (no new dependencies)**: Write `scripts/parse_fsm_to_graph.py` that loads
   `data/phase-gate-fsm.yml` into a NetworkX `DiGraph` and validates that every path
   from INIT to CLOSED passes through GATE_CHECK. This is a zero-overhead correctness
   check encodable as a CI step.

2. **Near-term (post-#131 instrumentation)**: Add `weight` and `cost_fn` fields to
   `data/delegation-gate.yml`. Implement a `scripts/optimal_delegation_path.py` that
   reads live cost signals from `session_cost_log.json` and returns the lowest-cost
   next delegation step.

3. **Defer LangGraph adoption**: Do not adopt LangGraph until the codebase requires true
   durable-execution LLM graph orchestration (i.e., multiple LLM-invocation nodes in a
   single session graph). The current workflow is human-supervised and synchronous —
   LangGraph solves problems the current architecture does not have.

4. **Mermaid-as-secondary output**: Add a Mermaid export function to
   `scripts/parse_fsm_to_graph.py` so the FSM can be visualized in documentation without
   maintaining a separate Mermaid file. Single source of truth = `phase-gate-fsm.yml`;
   Mermaid is derived.

5. **State coordinate serialization**: Extend the scratchpad format to include a
   `## State Coordinate` block at each phase-gate checkpoint:

   ```yaml
   state: GATE_CHECK
   context_budget_pct: 0.42
   active_issue: 203
   last_verdict: null
   phase: 10
   ```

   This enables retroactive path analysis across sessions once instrumentation is in place.

---

## Sources

- **LangGraph Overview** (docs.langchain.com, fetched 2026-03-14):
  "LangGraph is a low-level orchestration framework and runtime for building, managing,
  and deploying long-running, stateful agents… inspired by Pregel and Apache Beam."
  Source: `docs-langchain-com-oss-python-langgraph-overview.md`

- **NetworkX Documentation 3.6.1** (networkx.org, fetched 2026-03-14):
  "NetworkX is a Python package for the creation, manipulation, and study of the
  structure, dynamics, and functions of complex networks."
  Source: `networkx-org-documentation-stable.md`

- **LangChain Agents Concepts** (python.langchain.com, fetched 2026-03-07):
  "Use LangGraph, our low-level agent orchestration framework and runtime, when you have
  more advanced needs that require a combination of deterministic and agentic workflows."
  Source: `python-langchain-com-docs-concepts-agents.md`

- **Endogenous FSM** (endogenous artifact):
  `data/phase-gate-fsm.yml` — phase-gate-loop FSM with 6 states, 9 transitions, guard conditions.

- **Endogenous Delegation Graph** (endogenous artifact):
  `data/delegation-gate.yml` — static adjacency list of executive delegation routes
  with governance boundary constraints.

- **MANIFESTO.md** — Axiom 1: Endogenous-First (`§1`); Axiom 2: Algorithms Before
  Tokens (`§2`); Axiom 3: Local Compute-First (`§3`).
