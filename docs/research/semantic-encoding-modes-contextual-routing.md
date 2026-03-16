---
title: "Semantic Encoding Modes & Contextual Routing — Priority Annotations and GPS-Like Delegation Sequencing"
status: Final
research_sprint: "Sprint 12 — Intelligence & Architecture"
wave: 3
closes_issue: 277
governs: []
---

# Semantic Encoding Modes & Contextual Routing — Priority Annotations and GPS-Like Delegation Sequencing

> **Status**: Final
> **Research Question**: Can metadata annotations amplify agent behaviour (severity, depth modes)? Can a script ingest a task description and suggest the optimal delegation sequence from `data/delegation-gate.yml`?
> **Date**: 2026-03-15
> **Related**: [`docs/research/platform-agnosticism.md`](platform-agnosticism.md) · [`docs/research/custom-agent-service-modules.md`](custom-agent-service-modules.md) · [`docs/research/mcp-state-architecture.md`](mcp-state-architecture.md) · [`AGENTS.md` §Context-Sensitive Amplification](../../AGENTS.md#context-sensitive-amplification) · [`data/delegation-gate.yml`](../../data/delegation-gate.yml) · [Issue #277](https://github.com/EndogenAI/dogma/issues/277)

---

## Executive Summary

Two related ideas — **Semantic Encoding Modes** and **GPS-Like Contextual Routing** — share a common substrate question: can we encode more intelligence into the planning and routing layer without increasing token burn? This research evaluates both.

**Semantic Encoding Modes** are metadata annotations attached to tasks, constraints, or agent invocations that shift an agent's operating stance. Examples: `depth:deep` expands a SKILL.md checklist to its full form; `depth:quick` collapses to essentials; `severity:critical` shifts the agent into higher-vigilance mode; `mode:dry-run` suppresses all writes. The conceptual analogues are CSS specificity (selector weight determines which rule wins), compiler warning levels (GCC `-O2` vs `-O3`), and OS process priority (`nice -n` values). An endogenous analogue already exists in AGENTS.md: the **Context-Sensitive Amplification table** maps task-type keywords to amplified principles — this is a semantic encoding mode operating at the session level.

**GPS-Like Contextual Routing** is a script-driven suggestion engine: given a task description string, ingest `data/delegation-gate.yml` and `data/phase-gate-fsm.yml`, and output the optimal delegation sequence with agent assignments. Analogous to a GPS route planner applying Dijkstra's shortest-path algorithm over a graph where nodes are agents and edges are permissible delegation routes.

Key findings:

1. **The endogenous substrate for both ideas is already partially in place**: the Context-Sensitive Amplification table is a semantic mode system; `data/delegation-gate.yml` is a routing graph. The gap is programmatic use — neither is currently queryable by a script.
2. **CSS specificity is the correct mental model** for annotation resolution: a `severity:critical` annotation on a task should override the base stance of AGENTS.md constraints, exactly as an ID selector overrides a class selector. The resolution order: task annotation > session-level context > base AGENTS.md constraint > MANIFESTO.md default.
3. **Topological sort** (not Dijkstra) is the correct graph algorithm for delegation sequencing — the delegation graph is a DAG (directed acyclic graph), and the objective is to find a valid execution order respecting dependency edges, not to find a minimum-cost path.
4. **`data/delegation-gate.yml` is a sufficient routing substrate** for a first-pass `suggest_routing.py` — it encodes which agents can delegate to which, and the `governance_boundaries` section provides task-domain tagging. The missing element is a task-type → domain mapping (analogous to what the Context-Sensitive Amplification table provides for session keywords).
5. **Algorithms Before Tokens** (MANIFESTO.md §2): a `suggest_routing.py` script that answers "which agents in which order?" deterministically replaces repeated Orchestrator-level reasoning about delegation sequences — the canonical ABT use case.

**Recommendation: Adopt a two-phase implementation — (1) extend the Context-Sensitive Amplification table with machine-readable annotation schema; (2) commission `suggest_routing.py` as a Phase 0 script in the Orchestrator's session-start checklist.**

---

## Hypothesis Validation

### H1 — Semantic annotation systems for AI instructions exist in current frameworks

**Verdict**: CONFIRMED — multiple frameworks implement priority/criticality annotations; the endogenous analogue is already present

**Evidence**: Three annotation systems surveyed:

**CSS Specificity** (MDN Web Docs): CSS resolves conflicting rules via a hierarchical weight system — inline styles > ID selectors > class selectors > element selectors. The resolution algorithm is deterministic and stateless per-element. Applied to agent instructions: `task-level annotation > session-context > AGENTS.md constraint > MANIFESTO.md default` mirrors the CSS specificity cascade exactly. The MANIFESTO.md axioms are the browser's UA stylesheet — lowest specificity, always overridable, never absent.

**Compiler warning levels** (GCC/Clang): `-W0` suppresses all warnings; `-Wall` enables common warnings; `-Wextra` enables additional checks; `-Werror` converts all warnings to errors. Each level is a semantic mode that changes how the same code is evaluated. Applied to agent behaviour: `mode:strict` could treat AGENTS.md advisory guidance as blocking constraints (analogous to `-Werror`); `mode:permissive` could treat them as suggestions only.

**OpenAI system prompt priority** (platform.openai.com): The assistant platform distinguishes system prompt instructions (highest authority), developer instructions (medium authority), and user messages (lowest authority) — a three-tier semantic priority stack. The Copilot custom agent `.agent.md` body is functionally equivalent to the system prompt; user messages sit at the lowest tier. Annotation systems that want to override `.agent.md` behaviour must be injected at the system prompt level, not the user message level.

The **endogenous analogue** is the Context-Sensitive Amplification table in AGENTS.md: five rows each mapping a task-type keyword to an amplified principle and an expression hint. This is a semantic encoding mode operating at the session level. It is written in prose and consumed by the LLM at inference time — it works, but it is not machine-readable, not composable, and not queryable by a routing script.

**Canonical example**: The AGENTS.md Context-Sensitive Amplification table row `research / survey / scout / synthesize → Endogenous-First → Read prior docs and cached sources before reaching outward` is a semantic encoding mode. When the Orchestrator writes `## Session Start` with `depth:deep` and `mode:research`, the correct expansion is: full checklist from `deep-research-sprint` SKILL.md + all source-caching checks before any web fetch. The `depth:deep` annotation shifts the agent from the default "read brief" posture to "read full SKILL.md" posture.

**Anti-pattern**: Encoding priority metadata only in natural language (`"This is a critical task — please be especially careful"`). The LLM treats this as a soft hint that can be overridden by later context. A machine-readable annotation (`severity:critical`) in a YAML frontmatter that the Orchestrator parses deterministically before delegating cannot be overridden by subsequent user messages — it is resolved at the system layer, not the inference layer.

### H2 — Graph routing algorithms apply to delegation sequencing

**Verdict**: CONFIRMED — topological sort is the correct algorithm; Dijkstra applies only for cost-optimised routing with edge weights

**Evidence**: The `data/delegation-gate.yml` routing table defines a directed graph: nodes are executive agents, edges are permissible delegation routes. Visualised:

```
Orchestrator → {Docs, Researcher, Scripter, Automator, PM, Fleet, Planner}
Docs         → {Researcher, Scripter, Automator}
Researcher   → {Scripter}
PM           → {}
Review       → {}
GitHub       → {}
```

This is a **DAG (directed acyclic graph)** — no cycles (an agent cannot delegate back to its delegator in the same phase). The correct algorithm for finding a valid execution order over a DAG is **topological sort** (Kahn's algorithm or DFS-based). Topological sort produces a linearised sequence of agents such that every delegation edge points forward — this is exactly the phase sequence the Orchestrator must follow.

**Dijkstra's shortest path** applies only if edges carry weights (e.g., estimated token cost per delegation step). Without weights, Dijkstra degenerates to BFS. For the current routing problem — "which agents in which order, given a task domain" — topological sort with a domain filter is simpler and sufficient.

**A* search** would apply if the graph were larger (> 20 nodes) and heuristic pruning were needed to avoid evaluating infeasible paths. At the current fleet size (9 agents), full topological enumeration is tractable without heuristics.

The topological-sort approach for `suggest_routing.py`:
1. Parse `delegation-gate.yml` → adjacency list
2. Accept task description → classify into domain (research / commit / script / agent / inference)
3. Apply `governance_boundaries` filter → remove edges irrelevant to the domain
4. Topological sort on the filtered subgraph → output linearised delegation sequence
5. Overlay phase-gate-fsm.yml → annotate each step with required FSM transition

**Canonical example**: Task description: `"Research LanceDB alternatives and update AGENTS.md with findings"`. Classification: mixed (research + commit). Full topological sort: `Orchestrator → Researcher → (Review) → Docs → (Review) → GitHub`. The `governance_boundaries` filter excludes `Scripter` (no pytest needed), `Automator` (no hooks), `PM` (no issue ops). Output is a 5-step delegation sequence with gate positions marked.

**Anti-pattern**: Using BFS on the full delegation graph without a domain filter — this produces a sequence that includes agents with no relevance to the task (e.g., routing a documentation update through `PM` and `Automator`). Over-delegation wastes tokens on unnecessary agent instantiations, violating Algorithms Before Tokens (MANIFESTO.md §2).

### H3 — `data/delegation-gate.yml` + `data/phase-gate-fsm.yml` are sufficient for a first-pass routing script

**Verdict**: CONFIRMED WITH GAP — the graph is present; task-type → domain classification mapping is missing

**Evidence**: `data/delegation-gate.yml` provides:
- `delegation_routes` — the adjacency list (which agent can delegate to which)
- `governance_boundaries` — domain-scoped exclusivity rules (which agent owns which operation type)

`data/phase-gate-fsm.yml` provides:
- FSM states with guard conditions
- Transition events and required preconditions
- Review gate integration points

Together these encode a complete routing graph plus execution ordering rules. The gap is the **task classification input**: `delegation-gate.yml` uses agent names as keys, not task-type keywords. A `suggest_routing.py` script needs a mapping from task description tokens (e.g., "research", "commit", "script") to the `governance_boundaries` operation categories (e.g., "guide documentation", "git commit", "pytest execution").

This mapping already exists in prose form in the Context-Sensitive Amplification table. Encoding it as a YAML data file (`data/task-type-classifier.yml`) would complete the substrate required for a fully programmatic routing script — no additional infrastructure needed.

### H4 — A VS Code MCP routing tool can expose `suggest_routing.py`

**Verdict**: INVESTIGATE — technically feasible but introducing an MCP server for a task this size conflicts with Local Compute-First

**Evidence**: The MCP architecture (modelcontextprotocol.io) allows any Python script to be wrapped as an MCP server exposing a single tool. A `suggest_routing_server.py` exposing `suggest_route(task_description: str) → List[str]` would be callable from any Copilot agent session via a tool invocation.

However, as the three-layer state architecture in [`mcp-state-architecture.md`](mcp-state-architecture.md) §H1 establishes, MCP tool calls are stateless request/response — appropriate for database queries and file reads, but introducing a continuously-running MCP server process for a lightweight routing suggestion introduces infrastructure over-engineering. The Local Compute-First axiom (MANIFESTO.md §3) recommends preferring a script invoked on-demand over a service running continuously.

The pragmatic path: implement `suggest_routing.py` as a standalone CLI first. If integration into VS Code agent sessions proves high-leverage (eliminating ≥3 Orchestrator-level delegation reasoning steps per sprint), promote it to an MCP server as a Phase 2 enhancement per the custom-agent-service-modules.md §R4 migration path.

---

## Pattern Catalog

### P1 — CSS Specificity Cascade for Instruction Priority

**Source**: MDN Web Docs — CSS Specificity; this research

The CSS specificity model provides a complete, proven resolution algorithm for competing instructions. Applied to agent annotation:

| Layer | Analogous to | Priority |
|-------|-------------|----------|
| Task-level annotation (`severity:critical`) | Inline `style=""` | Highest — overrides all below |
| Session context (AGENTS.md Amplification table row) | ID selector `#id {}` | High |
| Agent persona (`.agent.md` frontmatter) | Class selector `.class {}` | Medium |
| AGENTS.md base constraints | Element selector `p {}` | Low |
| MANIFESTO.md axioms | Browser UA stylesheet | Lowest — always present, always overridable |

Resolution algorithm: scan the instruction stack bottom-up; higher-specificity annotations win; ties broken by recency (most recently written annotation wins, analogous to CSS source order).

**Canonical example**: A task is annotated `severity:critical` in its YAML frontmatter. The Orchestrator's session context is `mode:research` (from the Amplification table). The effective stance is: full research checklist (from session context) + higher vigilance threshold (from `severity:critical`). The critical annotation does not override the research mode; it amplifies it — the same research checklist runs with stricter quality gates at each step.

**Anti-pattern**: Treating all instructions as equal-weight natural language and relying on the LLM to infer relative priority. When the session context says `mode:quick` and the task description says "be thorough", the LLM has no deterministic rule for resolution — it may alternate between quick and thorough stances mid-task depending on context window salience. The specificity model eliminates this indeterminacy.

### P2 — Topological Sort as Phase Sequencing Algorithm

**Source**: Kahn (1962) topological sorting; `data/delegation-gate.yml`

The delegation graph in `delegation-gate.yml` is a DAG. Topological sort produces all valid linearisations of the graph — each corresponds to a valid delegation sequence for a sprint. Domain filtering (applying `governance_boundaries`) produces the domain-specific subgraph; topological sort on the subgraph produces the minimal valid sequence.

The recommended `suggest_routing.py` algorithm:
```python
# Pseudocode
graph = load_delegation_gate("data/delegation-gate.yml")
domain = classify_task(task_description)  # maps to governance_boundaries keys
subgraph = filter_by_domain(graph, domain)
sequence = topological_sort(subgraph)  # Kahn's algorithm
return annotate_with_fsm_gates(sequence, "data/phase-gate-fsm.yml")
```

**Canonical example**: A commit-domain task (`"Fix validate_synthesis.py and push"`) filters the full graph to: `Orchestrator → Scripter → (Review gate) → GitHub`. The Researcher, Docs, PM, Fleet, and Planner branches are pruned. The output is a 3-agent sequence with a single Review gate — matching the Orchestrator's intuitive routing but produced deterministically in O(V+E) time.

**Anti-pattern**: Routing a simple script fix through the full delegation tree (`Orchestrator → Researcher → Scripter → Review → Docs → GitHub`) because the Orchestrator lacked a programmatic domain classifier and defaulted to the full AGENTS.md delegation table. This is the failure mode the script is designed to prevent — token-expensive over-delegation.

### P3 — Annotation Schema for AGENTS.md Constraints

**Source**: AGENTS.md §Context-Sensitive Amplification; compiler warning levels

Proposed annotation schema for constraint-level semantic modes:

```yaml
# In task frontmatter or session-start metadata
mode: research | commit | script | agent | inference   # maps to Amplification table
depth: quick | standard | deep                        # skill checklist expansion
severity: normal | elevated | critical                # quality gate strictness
dry_run: false | true                                 # suppress all writes
```

These annotations are not yet machine-readable in the AGENTS.md prose. Encoding them as a YAML schema in `data/amplification-table.yml` (already exists — check current content) would complete the machine-readable layer. The Context-Sensitive Amplification table in AGENTS.md becomes the canonical prose documentation; `data/amplification-table.yml` becomes the machine-readable source of truth.

**Canonical example**: A session starts with `mode:commit, severity:critical`. The Orchestrator loads `data/amplification-table.yml`, finds the row `mode:commit → Documentation-First → amplified principle: every changed workflow/agent/script must have accompanying docs`. The `severity:critical` amplifier adds: run `validate_synthesis.py` on all docs before staging, not just after commit. The combination produces a more rigorous commit checklist than either annotation alone.

---

## Recommendations

| # | Recommendation | Priority | Cross-ref |
|---|---------------|----------|-----------|
| R1 | **Commission `scripts/suggest_routing.py`** — inputs: task description string; outputs: suggested delegation sequence + FSM gate positions; reads `data/delegation-gate.yml` + `data/phase-gate-fsm.yml` | Adopt | MANIFESTO.md §2 Algorithms Before Tokens |
| R2 | **Add `data/task-type-classifier.yml`** — maps task description tokens to `governance_boundaries` operation categories; completes the missing classification input for `suggest_routing.py` | Adopt | data/delegation-gate.yml |
| R3 | **Encode annotation schema in `data/amplification-table.yml`** — make the Context-Sensitive Amplification table machine-readable; document `mode`, `depth`, `severity`, `dry_run` fields | Adopt | AGENTS.md §Context-Sensitive Amplification |
| R4 | **Update AGENTS.md §Session Start** to reference the annotation schema — add a step: "Load `data/amplification-table.yml` and set active mode before delegating Phase 1" | Adopt (via Docs) | AGENTS.md §Session-Start Encoding Checkpoint |
| R5 | **Add `suggest_routing.py --mode <mode>` flag** to allow mode pre-seeding before task classification runs | Investigate | R1 |
| R6 | **Defer MCP routing tool** — implement CLI first; promote to MCP server only if ≥3 sessions per sprint require delegation routing and CLI integration proves cumbersome | Defer | mcp-state-architecture.md §H1; custom-agent-service-modules.md §R4 |

---

## Sources

- MDN Web Docs — CSS Specificity — `developer.mozilla.org/en-US/docs/Web/CSS/Specificity` — hierarchical selector weight system; cascade resolution algorithm
- Wikipedia — Topological Sorting — `en.wikipedia.org/wiki/Topological_sorting` — Kahn (1962) algorithm; DAG linearisation; O(V+E) complexity
- Wikipedia — Dijkstra's Algorithm — `en.wikipedia.org/wiki/Dijkstra%27s_algorithm` — shortest-path over weighted graphs; applicability conditions
- [`data/delegation-gate.yml`](../../data/delegation-gate.yml) — routing graph adjacency list; governance_boundaries domain filter
- [`data/phase-gate-fsm.yml`](../../data/phase-gate-fsm.yml) — FSM states, transitions, review gate integration points
- [`data/amplification-table.yml`](../../data/amplification-table.yml) — existing amplification table YAML; candidate machine-readable annotation registry
- `scripts/validate_delegation_routing.py` — existing validator for delegation-gate.yml; canonical examples of graph structure traversal
- [`docs/research/platform-agnosticism.md`](platform-agnosticism.md) — Wave 2 embrace + document posture; 4-editor coupling surface; VS Code Chat participant surface area (Wave 2, Sprint 12)
- [`docs/research/custom-agent-service-modules.md`](custom-agent-service-modules.md) — Wave 1 SKILL=spec, scripts=impl, MCP=tool boundary; §R4 MCP promotion criteria (Wave 1, Sprint 12)
- [`docs/research/mcp-state-architecture.md`](mcp-state-architecture.md) — Wave 1 three-layer state; stateless MCP tool model; avoid continuously-running servers (Wave 1, Sprint 12)
- [`AGENTS.md` §Context-Sensitive Amplification](../../AGENTS.md#context-sensitive-amplification) — existing semantic mode table; 5-row task-type → amplified-principle mapping
- [`AGENTS.md` §Algorithms Before Tokens](../../AGENTS.md) — prefer deterministic, encoded solutions over interactive token burn (MANIFESTO.md §2)
- [`MANIFESTO.md` §2 Algorithms Before Tokens](../../MANIFESTO.md#2-algorithms-before-tokens) — encode solutions, prefer deterministic over LLM-generated each session
- [`MANIFESTO.md` §3 Local Compute-First](../../MANIFESTO.md#3-local-compute-first) — prefer scripts over services; no infrastructure per-sprint
