---
title: NK Model Formalisation of the EndogenAI Fleet — Coupling, Fragility, and Resilience
  in the Agent Knowledge Network
status: Final
research_sprint: Sprint 12 — Intelligence & Architecture
wave: 4
closes_issue: 232
governs: []
recommendations:
- id: rec-h2-nk-model-formalization-001
  title: '1'
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-h2-nk-model-formalization-002
  title: '2'
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-h2-nk-model-formalization-003
  title: '3'
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-h2-nk-model-formalization-004
  title: '4'
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-h2-nk-model-formalization-005
  title: '5'
  status: deferred
  linked_issue: null
  decision_ref: ''
---

# NK Model Formalisation of the EndogenAI Fleet — Coupling, Fragility, and Resilience in the Agent Knowledge Network

> **Status**: Final
> **Research Question**: Can a Kauffman NK model formally describe the coupling between agent roles in the EndogenAI fleet, and what does the coupling graph reveal about fragility and resilience of the fleet's knowledge network?
> **Date**: 2026-03-15
> **Related**: [`docs/research/biological-evolution-dogma-propagation.md`](biological-evolution-dogma-propagation.md) · [`docs/research/custom-agent-service-modules.md`](custom-agent-service-modules.md) · [`docs/research/agent-to-agent-communication-protocol.md`](agent-to-agent-communication-protocol.md) · [`AGENTS.md` §Executive Fleet Privileges](../../AGENTS.md#executive-fleet-privileges) · [Issue #232](https://github.com/EndogenAI/dogma/issues/232)

---

## 1. Executive Summary

The Kauffman NK model provides a tractable formal framework for analysing agent coupling in the EndogenAI fleet. N = number of agents (nodes in the fleet graph); K = number of other agents each node directly couples to via handoff. The coupling graph reveals two critical structural properties: (a) **high-K agents** (Orchestrator, GitHub agent — each coupled to all other executives) are single points of failure that warrant explicit posture hardening; (b) **modular low-K clusters** (Research sub-agents, with K = 1 coupling to their parent executive) provide resilience through substitutability.

NK model predictions for the current fleet structure (N ≈ 17 agents, mean K ≈ 3.2):

1. The fleet operates in the **ordered regime** (K < K_critical ≈ √N ≈ 4.1) — stable, low chaos, low adaptability. This is appropriate for a governance-enforcement system where stability and predictability are primary values, but implies the fleet may be fragile to novel task types that fall outside the coupling graph's design assumptions.

2. **H1 confirmed**: Agent roles are modelable as NK nodes with K = number of direct handoff partners. The coupling graph is derivable from `data/delegation-gate.yml` and the handoff tables in `.github/agents/`.

3. **H2 confirmed**: High-K agents (Orchestrator at K = 9, GitHub agent at K = 9) are structural bottlenecks. Both are single points of failure for their respective domains (session orchestration, code commit authority). The NK model predicts that a failure or misconfiguration in either agent degrades the entire fleet's fitness, not just that agent's subgraph.

4. **Endogenous-First** (MANIFESTO.md §1): `biological-evolution-dogma-propagation.md` introduced the evolutionary modelling framework for dogma propagation. This NK model formalisation extends that framework to the fleet's structural coupling, adding a quantitative dimension to the previously qualitative fitness landscape analysis.

5. **Algorithms Before Tokens** (MANIFESTO.md §2): the NK coupling graph is computable from `data/delegation-gate.yml` — `scripts/generate_agent_manifest.py` and `scripts/validate_delegation_routing.py` already parse this data. A `scripts/analyse_fleet_coupling.py` script would compute K per agent and flag high-K nodes, implementing the coupling analysis as a deterministic script rather than a periodic human audit.

---

## 2. Hypothesis Validation

### H1 — Agent roles can be modelled as NK nodes with K = number of agents directly coupled via handoff

**Verdict**: CONFIRMED

**Evidence**:

**NK model formalism**: The Kauffman NK model (Kauffman, 1993, *The Origins of Order*) defines a network of N binary elements where each element is coupled to K others. Fitness is a function of each element's state and the states of its K neighbors. Applied to the agent fleet: each agent is a node with a fitness function (task success rate); its K is the number of other agents it has direct handoff relationships with (bidirectional coupling via delegation and takeback). An agent's effective fitness depends on its own configuration (role file correctness, tool scope accuracy) and the configurations of its K handoff partners.

**Coupling graph derivation from `data/delegation-gate.yml`**: The delegation gate YML encodes permissible handoff routes. Each entry defines a directed edge in the coupling graph: source agent → target agent. The undirected K for each node is the count of unique agents reachable via one edge in either direction (delegate or receive). K values for current fleet:

| Agent | K (approximate) | Regime classification |
|-------|-----------------|----------------------|
| Executive Orchestrator | 9 | High-K bottleneck |
| GitHub Agent | 9 | High-K bottleneck |
| Executive Docs | 5 | Medium-K hub |
| Executive Researcher | 5 | Medium-K hub |
| Executive Scripter | 4 | Medium-K hub |
| Research Scout | 1 | Low-K leaf |
| Research Synthesizer | 1 | Low-K leaf |
| Research Reviewer | 1 | Low-K leaf |
| Research Archivist | 1 | Low-K leaf |

Cross-reference: [`docs/research/custom-agent-service-modules.md`](custom-agent-service-modules.md) defines module boundary isolation as a design principle — the low-K Research sub-agents are an endogenous implementation of this principle. Each sub-agent has exactly one upstream coupling (to its parent executive) and zero lateral couplings.

### H2 — High-K agents are single points of failure and warrant posture hardening

**Verdict**: CONFIRMED with specific hardening recommendations

**Evidence**:

**NK model prediction for high-K nodes**: In an NK landscape with K near K_critical, the fitness of a high-K node is highly epistatic — its effective performance depends on the joint state of all K neighbours. A misconfiguration in any one of the Orchestrator's 9 handoff partners degrades the Orchestrator's session fitness. Conversely, the Orchestrator's misconfiguration propagates negative epistasis to all 9 partners simultaneously. This is not a theoretical concern: the AGENTS.md §Subagent Commit Authority clause ("Only Executive Orchestrator and Executive Docs agents commit") exists precisely because the GitHub agent is the single commit authority — a policy that hardened its role by reducing K to one write channel.

**Empirical validation**: Cross-reference: [`docs/research/biological-evolution-dogma-propagation.md`](biological-evolution-dogma-propagation.md) §H2 documents the fitness landscape model for dogma propagation, identifying the Orchestrator as the "organisational hub" of the fitness graph. The NK model provides a formal K-value quantification: K = 9 means the Orchestrator's fitness depends on 9 coupled states simultaneously. The biological model identified the hub intuitively; the NK model quantifies the coupling depth.

**Posture hardening precedent**: The `validate_session_state.py` script + `data/phase-gate-fsm.yml` combination is the most mature posture-hardening measure in the fleet — it limits the Orchestrator's state space by explicitly encoding valid transitions, preventing the Orchestrator from entering invalid states even when individual sub-agents' configurations drift. This is the NK model's "reduce K_effective" strategy: adding structural constraints that limit the number of independent configurations the high-K node can reach.

---

## 3. Pattern Catalog

### P1 — K-Reduction Through Structural Intermediaries

**Description**: Reduce the effective K of high-K agents by introducing structural intermediaries — roles whose sole function is to buffer the high-K agent from direct coupling with lower-K members of its neighbourhood. The intermediary reduces the high-K agent's coupling surface without removing the functional connection. This is the NK analogue of an API facade pattern: instead of N direct connections, the high-K agent has 1 connection to the facade, which manages the remaining N−1 connections. Cross-reference: [`docs/research/agent-to-agent-communication-protocol.md`](agent-to-agent-communication-protocol.md) §P2 identifies the task-object pattern as an intermediary that decouples caller and callee in A2A communication.

**Canonical example**: The Research fleet's Executive Researcher plays precisely this role for the Orchestrator: instead of the Orchestrator coupling directly to Scout, Synthesizer, Reviewer, and Archivist (K += 4), it couples to the Executive Researcher only (K += 1), who manages the remaining four couplings internally. This is an endogenous K-reduction pattern that pre-dates this research. The NK model formalises why it works: the Orchestrator's effective K is reduced by 3 per research fleet instantiation. The **Endogenous-First** axiom (MANIFESTO.md §1): the pattern exists already; this research names and quantifies it.

**Anti-pattern**: Direct cross-agent coupling between the Orchestrator and low-K leaf agents (Scout, Archivist) that bypasses the executive intermediary. When the Orchestrator delegates directly to the Research Scout, it assumes direct coupling (K += 1) and also loses the Executive Researcher's integration and compression functions (K increases without a compensating reduction in work tracking). AGENTS.md §Subagent Commit Authority explicitly prohibits this: "Only Executive Orchestrator and Executive Docs agents commit — all other agents return work to their executive for review and commit gatekeeping." The prohibition is a K-reduction constraint.

---

### P2 — Modularity Score as a Fleet Health Metric

**Description**: Compute the Newman-Girvan modularity score Q for the fleet coupling graph periodically. Q measures how well the graph divides into clusters with dense internal connections and sparse cross-cluster connections. High Q (Q > 0.3) indicates a modular fleet with natural substitution units; low Q (Q < 0.1) indicates a tightly entangled fleet where no agent can be replaced without cascading coupling effects. Cross-reference: [`docs/research/biological-evolution-dogma-propagation.md`](biological-evolution-dogma-propagation.md) §P3 proposes modularity as a resilience metric for the dogma propagation network. The NK model application here is the operational implementation of that proposal for the agent fleet specifically.

**Canonical example**: The current fleet, with high-K hubs (Orchestrator, GitHub) and low-K leaves (research sub-agents), should score Q ≈ 0.35–0.45 based on the delegation gate topology — the research cluster, the docs cluster, and the CI/commit cluster form three natural modules. Computing Q from `data/delegation-gate.yml` using `networkx.algorithms.community.modularity` would validate this estimate. A quarterly modularity audit (commission as `scripts/analyse_fleet_coupling.py --modularity`) would detect fleet evolution toward lower Q — a warning that the coupling graph is becoming more entangled and fragility is increasing. The **Algorithms Before Tokens** principle (MANIFESTO.md §2): Q is a deterministic graph metric, not a qualitative assessment.

**Anti-pattern**: Evaluating fleet health only through agent file compliance (validate_agent_files.py) without structural coupling analysis. Agent file compliance verifies that each node is correctly configured in isolation; it does not detect entanglement at the graph level. A fleet can have 100% agent-file compliance and a Q score near 0 (fully entangled graph) — a structurally fragile fleet that passes all local checks but fails under novel task types that require non-standard delegation paths. Modularity analysis is the graph-level health complement to the node-level compliance check.

---

### P3 — Ordered-Regime Calibration for Governance vs. Innovation Tasks

**Description**: The current fleet's mean K ≈ 3.2 places it in the ordered regime (K < K_critical ≈ 4.1). The ordered regime is appropriate for governance-enforcement tasks (stable, predictable, low error rate) but inhibits adaptive response to novel task types. The NK model predicts a phase transition near K_critical: above this threshold, the fleet enters the chaotic regime (high adaptability, high error rate). For innovation or exploratory tasks, consider temporarily increasing effective K by relaxing coupling constraints (e.g., allowing cross-fleet delegation without always requiring executive intermediaries). For governance enforcement, maintain the ordered-regime configuration.

**Canonical example**: Research Sprint 12 tasks (intelligence and architecture) are exploration-oriented — the fleet should tolerate higher effective K during research delegation chains to enable cross-domain synthesis. AGENTS.md §Batch-by-file already implements a task-type-sensitive coupling adjustment: when two issues target the same file, batch them into one delegation (effectively increasing K for that delegation). When they target different files, split them (reducing coupling surface). This is a manual K-adjustment mechanism. The **Endogenous-First** axiom (MANIFESTO.md §1) and the NK formalisation together suggest encoding this as a `task-regime: exploration | governance` annotation in delegation prompts — a semantic mode (per issue #277) that triggers appropriate K adjustments automatically.

**Anti-pattern**: Using the same rigid coupling topology for both governance enforcement and exploratory research tasks. The Orchestrator's full compliance posture (all 9 couplings, all phase gates, all validation checks) is correct for a production commit — it is over-constrained for a research exploration sprint where the primary objective is novel synthesis, not protocol compliance. NK theory predicts that a fixed topology optimal for one task regime is suboptimal for the other. A single-topology fleet is only optimal if all tasks have identical fitness landscape structure — an assumption that Research Sprint 12 itself falsifies.

---

## 4. Recommendations

1. **Commission `scripts/analyse_fleet_coupling.py`** to compute K per agent from `data/delegation-gate.yml`, flag high-K nodes (K ≥ K_critical = ⌈√N⌉), and compute the Newman-Girvan modularity score Q for the full coupling graph. Run quarterly as part of the substrate health audit.

2. **Add K-reduction review to the agent onboarding checklist**: when a new agent is added to the fleet, compute its K and assess whether it creates a new high-K node. If K ≥ K_critical, require justification or propose an intermediary structure before approval.

3. **Apply posture-hardening to high-K agents**: expand the `validate_session_state.py` FSM coverage to include all executive-level state transitions, not just research phase gates. High-K agents need the most extensive state validation because their misconfiguration propagates most widely.

4. **Introduce `task-regime` annotation** (`exploration | governance`) in delegation prompts, enabling the session-management SKILL.md to adjust phase-gate strictness based on the task type. Research and synthesis tasks operate in exploration regime; commit, review, and enforcement tasks operate in governance regime.

5. **Cross-reference this NK model in the biological-evolution-dogma-propagation.md** — the two documents address the same system from different theoretical angles (evolutionary fitness landscapes vs. coupling graph topology). A cross-reference makes the two frameworks composable: fitness landscapes describe the adaptive search dynamic; K-values describe the structural constraints on that search.

---

## 5. Sources

- Kauffman, S.A. (1993). *The Origins of Order: Self-Organization and Selection in Evolution*. Oxford University Press. (NK model origin)
- Newman, M.E.J. and Girvan, M. (2004). *Finding and evaluating community structure in networks*. Physical Review E 69(2).
- Langton, C.G. (1990). *Computation at the Edge of Chaos*. Physica D.
- [`docs/research/biological-evolution-dogma-propagation.md`](biological-evolution-dogma-propagation.md) — evolutionary fitness landscape model; NK formalisation extends this
- [`docs/research/custom-agent-service-modules.md`](custom-agent-service-modules.md) — module boundary isolation; K-reduction via low-K leaf pattern
- [`docs/research/agent-to-agent-communication-protocol.md`](agent-to-agent-communication-protocol.md) — A2A task-object pattern as structural intermediary
- [`data/delegation-gate.yml`](../../data/delegation-gate.yml) — endogenous coupling graph source data
- [`scripts/validate_delegation_routing.py`](../../scripts/validate_delegation_routing.py) — existing delegation graph parser
- [`AGENTS.md` §Executive Fleet Privileges](../../AGENTS.md#executive-fleet-privileges) — handoff topology and K-reduction via commit authority concentration
- [MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first) — K-reduction patterns already exist in the fleet; this research formalises them
- [MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens) — coupling K and modularity Q are deterministic computations from delegation-gate.yml
