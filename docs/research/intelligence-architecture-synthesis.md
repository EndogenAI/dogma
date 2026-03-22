---
title: 'Intelligence & Architecture Synthesis: Cross-Cutting Findings from Sprint
  12'
status: Final
date: 2026-03-16
closes_issues:
- 264
- 265
- 266
- 267
- 268
- 269
- 270
- 271
- 272
- 273
- 274
- 275
- 276
- 277
- 230
- 232
governs:
- intelligence-architecture
- mcp-architecture
- substrate-governance
- platform-strategy
- evolutionary-propagation
- content-encoding
- fleet-coupling
recommendations:
- id: rec-intelligence-architecture-synthesis-001
  title: Rationale
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-002
  title: '-----------'
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-003
  title: 60–70% variance reduction; zero infrastructure cost; alre...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-004
  title: Extends existing script; closes gap where phases lack str...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-005
  title: Prevents reading-level gate from rejecting valid research...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-006
  title: 7 substrates have no programmatic validation; atlas is th...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-007
  title: Prevents silent divergence in companion repos; low-effort...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-008
  title: Rationale
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-009
  title: '-----------'
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-010
  title: Calibrate on 10–15 labeled docs before CI enforcement; `d...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-011
  title: Quarterly cadence; high-K nodes are structural risk; curr...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-012
  title: GPS-like contextual routing reduces agent selection error...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-013
  title: Required for HGT protocol; detects when derived repos hav...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-014
  title: 1,500× token reduction; zero-server footprint; deferred t...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-015
  title: Rationale
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-016
  title: '-----------'
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-017
  title: 23 hard-coupled artefacts identified; migration path docu...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-018
  title: Proof-of-concept for companion repo model; `companion-repos.
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-019
  title: Defers full A2A until security threat model is addressed;...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-intelligence-architecture-synthesis-020
  title: Long-term evolutionary health; task-regime annotation ena...
  status: deferred
  linked_issue: null
  decision_ref: ''
---

# Intelligence & Architecture Synthesis: Cross-Cutting Findings from Sprint 12

## Executive Summary

- **State is stratified, not singular.** MCP session negotiation, scratchpad append-only log, and git history form three distinct state layers with different consistency guarantees. Conflating them produces the coordination failures A2A adoption would amplify; respecting the boundaries preserves local-compute-first coherence.
- **Substrates govern legibility.** 23 substrate types across 9 functional tiers are identified; 7 have no programmatic validation. Reading-level complexity delta (observed − substrate baseline) is a reliable lagging indicator of under-encoding — structural regularity (tables, labeled blocks) bypasses prose scoring and should be the primary remediation lever.
- **Knowledge propagates evolutionarily, not uniformly.** Cookiecutter provides vertical inheritance (one-time replication); D4 research docs function as HGT plasmids for horizontal knowledge transfer across derivative repos. Without a designed HGT slot in the sprint-close checklist, derived repos diverge silently.
- **Local compute is a first-class architectural constraint, not a preference.** LanceDB + BGE-Small + H2-chunking achieves 1,500× token reduction vs. bulk corpus reads on Apple Silicon with zero-server footprint. Platform-agnosticism analysis confirms MCP servers are the primary portability bridge for the 26.4% of target audience outside VS Code + GitHub.
- **Fleet coupling is measurable and controllable.** The NK model (N=17, mean K≈3.2 in ordered regime below K_critical≈4.1) quantifies the fleet's coordination landscape. Orchestrator and GitHub Agent are high-K bottlenecks (K=9); structural intermediaries reduce K without sacrificing capability.
- **Output compression requires both format and ceiling.** Format constraint alone or token ceiling alone reduces variance by only 15–25%; specifying both drops returns from 3,000–8,000 tokens to 1,200–1,800 tokens (60–70% variance reduction). This is a tractable, immediately enforceable pre-delegation discipline.

---

## Hypothesis Validation

| # | Hypothesis | Verdict | Evidence |
|---|-----------|---------|----------|
| H1 | MCP sessions are the correct unit of stateful agent coordination | **Partially Supported** | MCP sessions carry stateful capability negotiation but tool calls are stateless; scratchpad and git must carry cross-phase state. Three-layer model is correct; MCP alone is insufficient. ([mcp-state-architecture.md](mcp-state-architecture.md)) |
| H2 | Per-agent API layers (A2A-style) are the next required evolution | **Refuted** | A2A adoption is premature; the minimal viable surface is shared scratchpad + `validate_session_state.py` query layer. Security threat model (prompt injection, capability spoofing, SSRF) is substantial. Shared-state pattern already satisfies current coordination needs. ([agent-to-agent-communication-protocol.md](agent-to-agent-communication-protocol.md)) |
| H3 | High Flesch-Kincaid grade signals under-encoding and governance drift | **Partially Supported** | Absolute grade is a weak signal; complexity delta (observed − substrate baseline) is more reliable. FK Grade 14+ is a lagging indicator; structural regularity (tables, FSMs, decision tables) bypasses the scoring entirely and should be the primary remediation. ([high-reading-level-encoding-drift-signal.md](high-reading-level-encoding-drift-signal.md), [reading-level-assessment-framework.md](reading-level-assessment-framework.md)) |
| H4 | Cookiecutter inheritance is sufficient to propagate values to derivative repos | **Refuted** | Cookiecutter provides one-time vertical inheritance; derived repos diverge unless a Horizontal Gene Transfer (HGT) learning-flow is explicitly designed in. D4 docs serve as HGT plasmids. Punctuated equilibrium describes adoption tempo — stasis with rapid bursts at framework version upgrades. ([biological-evolution-dogma-propagation.md](biological-evolution-dogma-propagation.md)) |
| H5 | Service modules should be organized per-agent | **Refuted** | All major frameworks (LangChain, AutoGen, A2A) organize per-capability/domain, not per-agent. SKILL.md is the specification layer; `scripts/` is the implementation layer. Per-agent API layers create premature coupling. ([custom-agent-service-modules.md](custom-agent-service-modules.md)) |
| H6 | Fleet topology is operating in a disordered regime (K > K_critical) | **Refuted** | Mean K≈3.2 is below K_critical≈4.1, placing the fleet in the ordered regime with Q≈0.35–0.45 (modular). High-K bottlenecks exist at Orchestrator and GitHub Agent (K=9 each) but are localized rather than fleet-wide. ([h2-nk-model-formalization.md](h2-nk-model-formalization.md)) |

---

## Pattern Catalog

### Pattern 1: Three-Layer State Architecture

**Intent**: Assign each category of session state to the layer with the appropriate consistency guarantee, eliminating ad-hoc state proliferation.

**Structure**:

| Layer | Store | Consistency | Scope |
|-------|-------|------------|-------|
| MCP Session | Capability negotiation | Per-connection | Tool availability |
| Scratchpad | Append-only `.tmp/<branch>/<date>.md` | Eventual (per-write) | Cross-phase agent context |
| Git | Committed artefacts | Durable | Cross-session knowledge |

**Canonical example**: A Scout agent appends findings under `## Scout Output` in the scratchpad; the Executive reads the scratchpad before delegating; committed D4 docs become the durable tier. No agent reads another agent's scratchpad section (lateral isolation enforced). Git carries the finalized synthesis.

**Anti-pattern**: Treating the MCP session as the primary state store and attempting to reconstruct cross-phase context from tool-call history alone. This collapses when the session is reset, loses scratchpad-level detail, and forces redundant re-discovery.

**Source**: [mcp-state-architecture.md](mcp-state-architecture.md)

---

### Pattern 2: Service-Module-as-SKILL-Script-Pair

**Intent**: Decouple the *specification* of a capability (when and why to invoke it) from its *implementation* (how it executes), using SKILL.md + `scripts/` as a matched pair.

**Structure**:
- `SKILL.md` — declares context, constraints, invocation criteria, and return contract (specification layer)
- `scripts/<name>.py` — implements the deterministic execution path (implementation layer)
- MCP server (optional) — exposes stable tool-invocation surface for cross-platform access

**Canonical example**: `session-management` SKILL.md declares when and why to init/close a scratchpad; `scripts/prune_scratchpad.py` implements the mechanics. Any agent invoking the skill reads the SKILL.md to understand context, then runs the script for execution — no business logic lives in the agent file itself.

**Anti-pattern**: Embedding implementation logic directly in `.agent.md` files (e.g., inline `sed` commands, hardcoded paths). This prevents reuse across agents, fails the Programmatic-First principle (MANIFESTO.md §Programmatic-First), and makes validation impossible.

**Source**: [custom-agent-service-modules.md](custom-agent-service-modules.md)

---

### Pattern 3: Cookiecutter-as-Vertical-Inheritance + D4-as-HGT-Plasmid

**Intent**: Use Cookiecutter for one-time structural inheritance at repo creation; use D4 research docs as the mechanism for ongoing horizontal knowledge transfer to derivative repos.

**Structure**:
- **Vertical inheritance**: `cookiecutter.json` + `{{cookiecutter.project_slug}}/` render once at project creation, propagating AGENTS.md conventions, pyproject.toml structure, and initial scripts.
- **Horizontal Gene Transfer (HGT)**: D4 research docs (`docs/research/*.md`) are the plasmids — they carry distilled methodology updates that derivative repos can ingest via a structured "upstream learning slot" in the sprint-close checklist.
- **HGT cadence**: Every 3–6 months at framework version upgrade points (punctuated equilibrium tempo).

**Canonical example**: A companion repo created from Cookiecutter 18 months ago has diverged from current AGENTS.md conventions. An HGT sprint synthesizes the delta into a D4 doc, publishes it to the upstream registry, and the companion repo ingests it via `scripts/check_divergence.py` to identify which conventions need back-propagation.

**Anti-pattern**: Assuming that a Cookiecutter render at repo creation is sufficient for long-term values alignment. Without a designed HGT mechanism, derived repos diverge silently and the divergence only surfaces when an agent attempts to follow a convention that no longer exists in the derivative substrate.

**Source**: [biological-evolution-dogma-propagation.md](biological-evolution-dogma-propagation.md)

---

### Pattern 4: 5-Criterion Greenfield Decision Gate

**Intent**: Apply a structured 5-criterion evaluation before deciding whether a capability belongs in the main repo or warrants a standalone greenfield companion repo.

**Criteria**:

| Criterion | Question | Threshold for Greenfield |
|-----------|----------|------------------------|
| Audience gap | Does the capability serve an audience the main repo doesn't address? | Different primary consumer |
| Coupling depth | How tightly coupled is it to main repo internals? | Shallow coupling = greenfield candidate |
| Release cadence independence | Does it need to ship on its own timeline? | Yes → greenfield |
| Dogma inheritance cost | Is inheriting full AGENTS.md/MANIFESTO.md a burden? | Lightweight inheritance preferred → greenfield |
| MVD | Can a Minimum Viable Demo run independently? | Yes → greenfield |

**Canonical example**: Local RAG scores 5/5 on the criteria (distinct audience of developers who don't use the full dogma workflow, shallow coupling via MCP interface, independent release cadence, inherits only the RAG-relevant subset of conventions, MVD is a standalone index + query tool). First greenfield companion repo launched.

**Anti-pattern**: Defaulting to in-repo placement for every new capability without evaluation. This bloats the main repo, increases mean K in the fleet coupling model, and constrains release cadence for capabilities that serve different audiences.

**Source**: [greenfield-repo-candidates.md](greenfield-repo-candidates.md)

---

### Pattern 5: Complexity-Delta-as-Drift-Signal

**Intent**: Use the delta between observed reading-level grade and a substrate-specific baseline — not the absolute grade — as the primary signal for under-encoding and governance drift.

**Structure**:
- `delta = observed_grade − substrate_baseline`
- `delta > +2` → WARN (encoding prose is substituting for missing structure)
- `delta > +4` → FAIL (structural encoding deficit is significant)
- Recovery: inject structural regularity (decision tables, FSMs, labeled blocks) before prose editing

**Canonical example**: `AGENTS.md` has a baseline target of Grade 10–12. If `assess_doc_quality.py` reports Grade 15.3 after a sprint that added three new constraint sections, `delta = +3.3` triggers a WARN. The remediation is converting the new prose constraints into a decision table — not simplifying vocabulary.

**Anti-pattern**: Using absolute reading-level grade as a merge gate before calibrating per-substrate baselines. A research synthesis doc (`docs/research/`) legitimately targets Grade 14–16; blocking it at Grade 12 rejects valid content and incentivizes authors to write shallower analysis.

**Sources**: [high-reading-level-encoding-drift-signal.md](high-reading-level-encoding-drift-signal.md), [reading-level-assessment-framework.md](reading-level-assessment-framework.md), [programmatic-writing-assessment-tooling.md](programmatic-writing-assessment-tooling.md)

---

### Pattern 6: Format-Ceiling Dual Mandate

**Intent**: Require both an explicit output format type *and* a token ceiling in every delegation prompt; each alone is insufficient to control return size and variance.

**Evidence**:

| Constraint Applied | Typical Return Size | Variance Reduction |
|-------------------|--------------------|--------------------|
| None | 3,000–8,000 tokens | baseline |
| Format type only | 2,500–5,000 tokens | ~15–25% |
| Token ceiling only | 2,000–4,000 tokens | ~20–30% |
| **Format + ceiling (dual)** | **1,200–1,800 tokens** | **60–70%** |

**Canonical example**: "Return only: bullets (issue# — gap), ≤2000 tokens. No prose, no preamble." — specifies format (bullets with schema) and ceiling (2000 tokens). Layer 3 Return Validation Gate catches returns that exceed the ceiling and triggers recompression.

**Anti-pattern**: "Return your findings." No format, no ceiling. Produces 3,000–8,000 token returns that consume context budget and obscure signal within verbose prose — even when the agent's actual findings could fit in 400 tokens.

**Source**: [output-format-constraint-compressed-returns.md](output-format-constraint-compressed-returns.md)

---

### Pattern 7: K-Reduction via Structural Intermediaries

**Intent**: Buffer high-K nodes (Orchestrator, GitHub Agent with K=9 each) using structural tier layers rather than reducing their functional scope. Intermediaries absorb coordination without adding new bottlenecks.

**NK Model Context**:
- N=17 agents; K = mean number of agents an agent directly coordinates with
- Fleet mean K≈3.2 (ordered regime, below K_critical≈4.1)
- Orchestrator and GitHub Agent at K=9 are local bottlenecks, not systemic disorder
- Executive tier (Researcher, Docs, Scripter, Automator) buffers Orchestrator from Scout/Synthesizer traffic

**Canonical example**: Executive Researcher sits between Orchestrator and the Scout/Synthesizer/Reviewer/Archivist chain. Orchestrator delegates one task to Executive Researcher (K contribution: +1); Executive Researcher coordinates the four-agent chain (absorbing K=4 locally). Without the Executive tier, Orchestrator's K would be +4 for every research task. K-reduction is structural, not functional.

**Anti-pattern**: Flattening the fleet to reduce "complexity" by eliminating the Executive tier. This pushes all cross-agent coordination onto the Orchestrator, raising its K toward the critical threshold and increasing the probability of cascading coordination failures.

**Source**: [h2-nk-model-formalization.md](h2-nk-model-formalization.md)

---

### Pattern 8: Topological-Sort Delegation Sequencing

**Intent**: Sequence delegation chains by topological sort on the dependency DAG, not by shortest-path (Dijkstra) or arbitrary ordering. Dependency direction — not distance — determines execution order.

**Why not Dijkstra**: Dijkstra minimizes path cost in a weighted graph; delegation DAGs are not distance-minimization problems. The constraint is *dependency satisfaction*, not *path efficiency*. Topological sort respects dependency direction and detects cycles (invalid plans) that Dijkstra silently routes around.

**Algorithm**:
1. Model phases as DAG nodes; dependency arrows point from required→dependent.
2. Run topological sort (Kahn's algorithm or DFS post-order).
3. Phases with in-degree 0 are parallelizable; others must wait for their dependencies.
4. Cycle detection is a plan validation gate — circular dependencies signal a workplan design error.

**Canonical example**: In a research sprint, the Scout (Phase 2) must complete before the Synthesizer (Phase 3), which must complete before the Reviewer (Phase 4). Phase 2 → Phase 3 → Phase 4 is the topological ordering. Phases 2A and 2B (two parallel Scout delegations) both have in-degree 0 and execute concurrently. CSS specificity model (task annotation > session context > base AGENTS.md > MANIFESTO.md) applies the same ordered-precedence logic to context resolution.

**Anti-pattern**: Ordering delegation phases by "intuitive" sequence without explicit dependency mapping, then discovering mid-sprint that Phase 4 required Phase 3 output that was deferred to Phase 6. Retrospective re-ordering is expensive; topological pre-validation is cheap.

**Source**: [semantic-encoding-modes-contextual-routing.md](semantic-encoding-modes-contextual-routing.md)

---

## Architecture Recommendations

### Tier 1 — Immediate (Sprint 13)

| Action | Rationale | Source(s) |
|--------|-----------|-----------|
| Enforce Format-Ceiling Dual Mandate in Pre-Delegation Checklist (AGENTS.md update) | 60–70% variance reduction; zero infrastructure cost; already proven in corpus back-propagation sprint | [output-format-constraint-compressed-returns.md](output-format-constraint-compressed-returns.md) |
| Add `validate_session_state.py` FSM phase coverage check | Extends existing script; closes gap where phases lack structured state transitions | [mcp-state-architecture.md](mcp-state-architecture.md), [classic-programmatic-patterns-dogma-legibility.md](classic-programmatic-patterns-dogma-legibility.md) |
| Define per-substrate reading-level targets in `.reading-level-targets.yml` | Prevents reading-level gate from rejecting valid research docs; required before any CI enforcement | [reading-level-assessment-framework.md](reading-level-assessment-framework.md) |
| Create `data/substrate-atlas.yml` as machine-readable registry | 7 substrates have no programmatic validation; atlas is the prerequisite for gap-closing CI additions | [substrate-atlas.md](substrate-atlas.md) |
| Add "upstream HGT learning slot" to sprint-close checklist in AGENTS.md | Prevents silent divergence in companion repos; low-effort checklist addition with high long-term fidelity payoff | [biological-evolution-dogma-propagation.md](biological-evolution-dogma-propagation.md) |

### Tier 2 — Near-term (Sprint 13–14)

| Action | Rationale | Source(s) |
|--------|-----------|-----------|
| Commission `scripts/assess_doc_quality.py` with composite score (readability 30%, structural regularity 40%, encoding completeness 30%) | Calibrate on 10–15 labeled docs before CI enforcement; `delta` mode for drift detection | [programmatic-writing-assessment-tooling.md](programmatic-writing-assessment-tooling.md), [high-reading-level-encoding-drift-signal.md](high-reading-level-encoding-drift-signal.md) |
| Commission `scripts/analyse_fleet_coupling.py` (compute K per agent, flag K > 6, compute modularity Q) | Quarterly cadence; high-K nodes are structural risk; currently no automated visibility | [h2-nk-model-formalization.md](h2-nk-model-formalization.md) |
| Commission `scripts/suggest_routing.py` + `data/task-type-classifier.yml` | GPS-like contextual routing reduces agent selection errors; annotation schema feeds amplification-table.yml | [semantic-encoding-modes-contextual-routing.md](semantic-encoding-modes-contextual-routing.md) |
| Commission `scripts/check_divergence.py` (cookiecutter template divergence detector) | Required for HGT protocol; detects when derived repos have drifted from current conventions | [biological-evolution-dogma-propagation.md](biological-evolution-dogma-propagation.md) |
| Adopt LanceDB + BGE-Small-EN-v1.5 + H2-chunking as standard RAG stack; add `rag-index/` to .gitignore | 1,500× token reduction; zero-server footprint; deferred to greenfield companion repo decision | [local-inference-rag.md](local-inference-rag.md), [greenfield-repo-candidates.md](greenfield-repo-candidates.md) |

### Tier 3 — Strategic (Sprint 15+)

| Action | Rationale | Source(s) |
|--------|-----------|-----------|
| Add "Platform Infrastructure" section to MANIFESTO.md; publish `docs/guides/platform-migration.md` | 23 hard-coupled artefacts identified; migration path documentation is prerequisite for cross-platform adoption | [platform-agnosticism.md](platform-agnosticism.md) |
| Launch Local RAG as first greenfield companion repo (scores 5/5 on decision gate) | Proof-of-concept for companion repo model; `companion-repos.yml` registry establishes pattern for future greenfields | [greenfield-repo-candidates.md](greenfield-repo-candidates.md), [local-inference-rag.md](local-inference-rag.md) |
| Implement MCP-mediated scratchpad query pattern as A2A-minimal viable surface | Defers full A2A until security threat model is addressed; scratchpad query layer satisfies current coordination needs | [agent-to-agent-communication-protocol.md](agent-to-agent-communication-protocol.md) |
| Schedule HGT ingestion sprints every 3–6 months; add `task-regime` annotation to phase-gate FSM | Long-term evolutionary health; task-regime annotation enables adaptive phase-gate strictness | [biological-evolution-dogma-propagation.md](biological-evolution-dogma-propagation.md), [h2-nk-model-formalization.md](h2-nk-model-formalization.md) |

---

## Cross-Cutting Themes

### Theme 1: State & Communication Architecture

**Issues**: #264 (MCP State), #272 (A2A Protocol)

MCP sessions, scratchpads, and git represent three fundamentally different state consistency models that must not be conflated. MCP provides per-connection capability negotiation; scratchpad provides append-only cross-phase context; git provides durable committed artefacts. The Endogenous-First axiom (MANIFESTO.md §1) applies directly here: the existing three-layer scratchpad + `validate_session_state.py` pattern is the correct first-resort coordination mechanism before reaching for external protocols. The Three-Layer State Architecture (Pattern 1) renders full A2A adoption unnecessary for current coordination requirements. A2A's JSON-RPC HTTP model introduces a substantial security threat surface (prompt injection, capability spoofing, SSRF) without delivering coordination capabilities that the existing scratchpad + `validate_session_state.py` pattern cannot already provide. The strategic path is MCP-mediated scratchpad query, not peer-to-peer agent messaging.

**Key scripts affected**: `scripts/validate_session_state.py` (extend with FSM phase query); `scripts/prune_scratchpad.py` (Three-Layer anchor)

---

### Theme 2: Substrate Governance & Legibility

**Issues**: #268 (Substrate Atlas), #267 (Glossary), #274 (Reading Level), #275 (Programmatic Writing Assessment), #276 (Drift Signal), #266 (Programmatic Patterns)

23 substrate types exist across 9 functional tiers; 7 have no programmatic validation. Legibility is not primarily a prose problem — it is a structural encoding problem. Decision tables, FSMs, guard clauses, and Design-by-Contract patterns reduce ambiguity more reliably than vocabulary simplification. Complexity delta (observed − substrate baseline) is the correct drift signal; absolute reading level is not actionable without per-substrate baselines. The composite scoring model (readability 30%, structural regularity 40%, encoding completeness 30%) operationalizes these principles as a machine-checkable metric. A canonical `docs/glossary.md` with programmatic drift detection closes the definition-divergence vector that currently exists across 23 substrate types.

**Key scripts affected**: `scripts/check_substrate_health.py` (add reading-level baseline snapshot); `scripts/assess_doc_quality.py` (commission); `scripts/check_glossary_coverage.py` (commission); `data/substrate-atlas.yml` (create)

---

### Theme 3: Evolutionary Propagation

**Issues**: #273 (Biological Evolution), #277 (Semantic Encoding Modes), #230 (Output Format Constraints)

Values propagate through the fleet the same way genetic information propagates through organisms: vertical inheritance at creation (Cookiecutter render), horizontal transfer for ongoing adaptation (D4 docs as HGT plasmids). Without a designed HGT slot, derived repos drift — silently and irreversibly absent an active divergence check. Semantic encoding modes (task-type annotations in the amplification table) enable the fleet to shift collectively rather than drifting individually, because annotation is read by all agents rather than requiring per-agent instruction updates. Output format constraints are themselves a form of encoding that must be inherited: the Format-Ceiling Dual Mandate (Pattern 6) is a concrete HGT target — companion repos that inherit it immediately reduce their inter-agent token overhead by 60–70%.

**Key scripts affected**: `scripts/check_divergence.py` (commission); `data/amplification-table.yml` (extend with task-type annotations); `scripts/suggest_routing.py` (commission)

---

### Theme 4: Local-Compute & Platform Strategy

**Issues**: #269 (Local RAG), #270 (Platform Agnosticism), #271 (Greenfield Candidates), #265 (Service Modules)

Local-compute-first is not merely a cost preference — it is a structural reliability principle (MANIFESTO.md §3). A RAG stack that requires a remote vector database introduces a network dependency that violates this principle; LanceDB + BGE-Small with zero-server footprint eliminates it. Platform agnosticism analysis reveals that VS Code + GitHub covers 73.6% of the target audience, but the 26.4% outside this pairing requires explicit migration documentation and MCP server wrappers as the portability bridge. The 5-Criterion Greenfield Decision Gate (Pattern 4) provides a principled framework for deciding when a capability is better served as a companion repo — preventing both premature extraction (greenfield overhead too high) and premature consolidation (coupling depth stifles independent evolution).

**Key scripts affected**: `scripts/README.md` (document service module inventory); RAG index scripts (new, greenfield repo); `data/companion-repos.yml` (create)

---

### Theme 5: Fleet Coupling & Routing Intelligence

**Issues**: #232 (NK Model), #277 (Semantic Encoding Modes), #230 (Output Format Constraints)

The fleet's NK profile (N=17, K≈3.2 < K_critical≈4.1) confirms modular ordered-regime operation, but the two K=9 bottlenecks (Orchestrator, GitHub Agent) are structural risks that require active management via the K-Reduction via Structural Intermediaries pattern (Pattern 7). Routing intelligence — the ability to select the correct agent and phase sequence for a given task — is currently implicit; `scripts/suggest_routing.py` with `data/task-type-classifier.yml` would make it explicit and machine-verifiable. Topological-Sort Delegation Sequencing (Pattern 8) closes the workplan design gap where implicit phase ordering creates deferred-dependency failures mid-sprint. Together, these three mechanisms (K-reduction, routing intelligence, topological sequencing) constitute a coherent fleet coordination upgrade that does not require A2A or any cross-agent communication infrastructure beyond what already exists.

**Key scripts affected**: `scripts/analyse_fleet_coupling.py` (commission); `scripts/suggest_routing.py` (commission); `scripts/validate_delegation_routing.py` (extend)

---

## Sources

| # | Document | Closes |
|---|----------|--------|
| 1 | [mcp-state-architecture.md](mcp-state-architecture.md) | #264 |
| 2 | [custom-agent-service-modules.md](custom-agent-service-modules.md) | #265 |
| 3 | [classic-programmatic-patterns-dogma-legibility.md](classic-programmatic-patterns-dogma-legibility.md) | #266 |
| 4 | [glossary-maintenance-strategy.md](glossary-maintenance-strategy.md) | #267 |
| 5 | [substrate-atlas.md](substrate-atlas.md) | #268 |
| 6 | [local-inference-rag.md](local-inference-rag.md) | #269 |
| 7 | [platform-agnosticism.md](platform-agnosticism.md) | #270 |
| 8 | [greenfield-repo-candidates.md](greenfield-repo-candidates.md) | #271 |
| 9 | [agent-to-agent-communication-protocol.md](agent-to-agent-communication-protocol.md) | #272 |
| 10 | [biological-evolution-dogma-propagation.md](biological-evolution-dogma-propagation.md) | #273 |
| 11 | [reading-level-assessment-framework.md](reading-level-assessment-framework.md) | #274 |
| 12 | [programmatic-writing-assessment-tooling.md](programmatic-writing-assessment-tooling.md) | #275 |
| 13 | [high-reading-level-encoding-drift-signal.md](high-reading-level-encoding-drift-signal.md) | #276 |
| 14 | [semantic-encoding-modes-contextual-routing.md](semantic-encoding-modes-contextual-routing.md) | #277 |
| 15 | [output-format-constraint-compressed-returns.md](output-format-constraint-compressed-returns.md) | #230 |
| 16 | [h2-nk-model-formalization.md](h2-nk-model-formalization.md) | #232 |
