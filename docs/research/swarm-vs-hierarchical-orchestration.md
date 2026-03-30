---
title: "Swarm vs. Hierarchical Multi-Agent Orchestration"
status: Final
closes_issue: 415
x-governs:
  - endogenous-first
  - algorithms-before-tokens
created: 2026-03-30
sources:
  - url: "https://www.marktechpost.com/2026/03/20/a-coding-implementation-showcasing-clawteams-multi-agent-swarm-orchestration-with-openai-function-calling"
    title: "A Coding Implementation Showcasing ClawTeams Multi-Agent Swarm Orchestration with OpenAI Function Calling"
    type: blog_post
    note: "Fetched 2026-03-30 via MarkTechPost / HKUDS GitHub repo"
  - url: "https://platform.openai.com/docs/guides/function-calling"
    title: "OpenAI Function Calling"
    type: documentation
  - url: "https://github.com/openai/swarm"
    title: "OpenAI Swarm (educational framework)"
    type: repository
  - url: "https://github.com/HKUDS/ClawTeam"
    title: "ClawTeam — HKUDS Agent Swarm Intelligence Framework"
    type: repository
    note: "Fetched 2026-03-30; 4.1k stars, 567 forks, 24 contributors. Launched 2026-03-18."
recommendations:
  - id: rec-swarm-vs-hierarchical-orchestration-001
    title: "DOCUMENT swarm orchestration as a named anti-pattern for governance-sensitive workflows in AGENTS.md"
    status: deferred
    effort: Low
    linked_issue: null
    decision_ref: null
  - id: rec-swarm-vs-hierarchical-orchestration-002
    title: "ADOPT function-calling handoff primitive for lightweight sub-task dispatch within a single executive phase — not as a replacement for the full Scout→Synthesizer→Reviewer chain"
    status: deferred
    effort: Medium
    linked_issue: null
    decision_ref: null
  - id: rec-swarm-vs-hierarchical-orchestration-003
    title: "EVALUATE ClawTeams patterns again when the source article is available — refetch URL when 404 is resolved"
    status: completed
    effort: Low
    linked_issue: null
    decision_ref: null
---

# Swarm vs. Hierarchical Multi-Agent Orchestration

> **Status**: Final
> **Research Question**: What can be learned from ClawTeams' multi-agent swarm orchestration with OpenAI function calling, and how does it compare to dogma's handoff topology?
> **Date**: 2026-03-30
> **Source**: MarkTechPost article by Michal Sutter (ClawTeams, 2026-03-20) + HKUDS/ClawTeam GitHub repository (fetched 2026-03-30). See also [`competitor-landscape-agentic-frameworks.md`](competitor-landscape-agentic-frameworks.md) and [`agent-to-agent-communication-protocol.md`](agent-to-agent-communication-protocol.md).
> **Related**: [Issue #415](https://github.com/EndogenAI/dogma/issues/415) · [`AGENTS.md`](../../AGENTS.md) · [`MANIFESTO.md`](../../MANIFESTO.md)

---

## 1. Executive Summary

ClawTeams (HKUDS, launched 2026-03-18; 4.1k stars, 567 forks) exemplifies the **swarm orchestration pattern** via a **leader/worker architecture**: a leader agent decomposes a high-level goal into sub-tasks on a shared task board; specialised workers execute those tasks autonomously via inter-agent messaging with real-time coordination. The task board encodes dependency chains using `blocked_by_indices` in the leader's plan JSON; `TaskBoard._resolve_dependencies` auto-unblocks tasks on completion. Four OpenAI function-calling tools implement the coordination interface: `task_update`, `inbox_send`, `inbox_receive`, `task_list` — exact counterparts of ClawTeam's CLI commands. A coordination protocol is auto-injected into every agent's system prompt at runtime: "We auto-inject a coordination protocol into every agent's system prompt, giving it awareness of its name, role, and the exact workflow it must follow." Worker agents run at `max_iterations=6, temperature=0.4`; the leader/synthesis agent at `temperature=0.3`. All state persists in `~/.clawteam/` as JSON files with atomic `tmp + rename` writes — no database, no server, no cloud. Each worker operates in its own git worktree (`clawteam/{team}/{agent}` branch naming) and tmux window. Pre-built team templates include an AI Hedge Fund (5 analysts + risk manager), a Research Swarm, and an Engineering Team. Transport defaults to file-based JSON with an optional ZeroMQ P2P layer (Redis targeted for v0.4). Plan Approval (v0.2.0) — agents submit plans for leader review before execution — is the closest structural analog to dogma's Review gate, though it validates plan text rather than schema compliance. ClawTeam's v1.0 roadmap explicitly acknowledges the governance gap: "auth, permissions, audit logs" are deferred. The swarm model prioritises dynamic routing, low-latency dispatch, and local-compute-first infrastructure at the cost of governance transparency and encoded constraint enforcement.

Dogma's handoff topology is explicitly hierarchical: a named chain (Executive → Scout → Synthesizer → Reviewer → Archivist → GitHub) where each transition is gated by a takeback handoff, a per-phase checklist, and an inter-phase Review gate. This structure instantiates [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) and [MANIFESTO.md § 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens): the routing decision is encoded into the substrate, not left to runtime token generation.

**Key findings**:

1. **Swarm advantage: dynamic task routing** — Swarm excels when task decomposition is uncertain at design time, the agent pool is homogeneous in trust level, and routing errors are cheaply recoverable (e.g., coding assistants, customer support triage).
2. **Hierarchical advantage: accountability and constraint enforcement** — Dogma's chain assigns roles, enforces gates, and creates an auditable record of every handoff. Swarm has no equivalent to the Review gate or the per-phase checklist.
3. **Function calling as a shared primitive** — Both models use tool/function calls as the handoff mechanism, but dogma encodes the *sequence* in AGENTS.md rather than relying on the model to select it dynamically.
4. **Convergence zone** — For intra-phase sub-task dispatch (e.g., an executive agent routing a formatting sub-task), the swarm function-calling pattern is a valid and lower-overhead option that does not compromise values governance.

**Recommendation**: Document swarm as a named external pattern; adopt function-calling dispatch as an intra-phase primitive; do not replace the hierarchical inter-phase chain with a swarm topology for governance-sensitive workflows.

---

## 2. Hypothesis Validation

| Hypothesis | Result | Evidence |
|------------|--------|----------|
| **H1**: Swarm orchestration trades governance transparency for routing flexibility | ✅ **SUPPORTED** | OpenAI Swarm exposes no equivalent to AGENTS.md constraints, validate_agent_files.py, or the Review gate. Agent selection is a model-time decision, not a substrate-encoded rule. |
| **H2**: Function calling is the shared handoff primitive in both models | ✅ **SUPPORTED** | ClawTeams and OpenAI Swarm both use OpenAI function calls to transfer control between agents. Dogma's `.agent.md` handoff buttons and MCP tool calls are semantically equivalent wrappers around the same primitive. |
| **H3**: Hierarchical topology is superior for audit trail and constraint enforcement | ✅ **SUPPORTED** | Dogma's chain produces a scratchpad entry per phase, a commit per deliverable, and a Review gate verdict. Swarm produces no analogous artifacts — the execution trace lives only in the context window. |
| **H4**: Swarm is advantageous for scenarios with unpredictable task sequences | ✅ **PARTIALLY SUPPORTED** | For exploratory tasks where the next step cannot be pre-determined (e.g., open-ended bug diagnosis), swarm routing avoids the overhead of a hand-crafted phase sequence. However, dogma's Planner role can construct a workplan that encodes this dynamism without sacrificing gates. |
| **H5**: Swarm primitives are compatible with dogma's intra-phase dispatch | ✅ **SUPPORTED** | Within a single executive phase (e.g., Executive Scripter dispatching three independent sub-tasks in parallel), function-calling-style dispatch is consistent with [MANIFESTO.md § 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens) — the routing logic is deterministic given the phase plan. |

---

## 3. Pattern Catalog

### Pattern 1: Swarm Triage-Handoff (OpenAI Swarm / ClawTeams Model)

**Problem**: A task arrives with an uncertain structure. The orchestrator does not know in advance whether the next step is research, code generation, data retrieval, or user clarification. A rigid static pipeline would force a predetermined sequence regardless of task type.

**Solution**: A triage agent uses function calling to route the task to the most appropriate specialist agent. Each specialist can itself call functions to transfer back or forward. The execution graph is emergent — it is constructed at runtime from model decisions, not pre-encoded in configuration.

**Canonical example**: ClawTeam 8-GPU autonomous ML research run (HKUDS/ClawTeam repository). A leader agent decomposes the research goal into 8 sub-tasks and spawns 8 worker agents, each assigned a dedicated GPU and research direction. Workers communicate via `inbox_send`/`inbox_receive`; the task board tracks dependencies via `blocked_by_indices`. The swarm cross-pollinates best-performing configurations across workers — emergent knowledge sharing without explicit orchestration rules. Over 2430+ experiments, the benchmark improved from val_bpb 1.044 → 0.977 with zero human intervention. Execution state lives in `~/.clawteam/` JSON files; there is no pre-defined state machine — the execution graph is constructed at runtime by the leader's decomposition.

**Dogma contrast**: This pattern lacks the per-phase checklist from [AGENTS.md § Per-Phase Execution Checklists](../../AGENTS.md#per-phase-checklists), the scratchpad annotation requirement, and the Review gate. It is appropriate for low-governance tasks (exploratory coding, LLM-assisted triage) where recovery from a wrong routing decision is trivial.

**Anti-pattern**: Using swarm triage routing for governance-critical workflows. The ClawTeam article's Colab demonstration routes tasks via `gpt-4o-mini` at `temperature=0.4` — no AGENTS.md constraints, no per-phase checklist, no commit-per-deliverable, and no Review gate. Recovery from bad decomposition means reinvoking the leader, which regenerates the plan from scratch with no rollback to the last clean commit and no equivalent of `git revert` on a task board entry. Applied to research synthesis, agent file authoring, or PR merges, a wrong routing decision can corrupt a committed artifact with no deterministic recovery path. Swarm runtime routing is not a substitute for substrate-encoded phase ordering — it transfers the routing decision from an encoded constraint to a model-generated token, increasing variance and eliminating the audit trail.

---

### Pattern 2: Hierarchical Takeback Handoff (Dogma Model)

**Problem**: A multi-phase research or implementation session must produce auditable, constraint-compliant artifacts. The execution order matters: research must precede implementation; review must precede commit. Ad-hoc routing would allow phases to execute out of order or skip gates under context pressure.

**Solution**: Each phase is a named, sequenced step in a committed workplan. The executive delegates to a subagent with an explicit takeback instruction; the subagent returns control to the executive before the next phase begins. The Review gate is a mandatory inter-phase checkpoint that cannot be bypassed by dynamic routing.

**Canonical example**: The Sprint 24 research pipeline in this repository. Executive Researcher delegates to Scout (fetch-before-act), Scout returns findings to scratchpad, Synthesizer produces a draft, Reviewer validates against D4 schema, Archivist commits after APPROVED verdict. No phase is skipped; each handoff is documented in the scratchpad. This chain is encoded in `.github/agents/executive-researcher.agent.md` — it is an algorithm, not a runtime model decision. ([MANIFESTO.md § 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens))

**Anti-pattern**: An executive that recombines phases dynamically ("I'll skip the Reviewer this time since the draft looks good to me") without committing a revised workplan. Dynamic elision of the Review gate is the hierarchical equivalent of swarm-style ad-hoc routing — it produces the same auditability gap.

---

## 4. Comparison Table

| Dimension | Swarm (ClawTeams / OpenAI Swarm) | Hierarchical (Dogma) |
|-----------|----------------------------------|----------------------|
| **Routing decision** | Model-time (function call) | Substrate-encoded (AGENTS.md, workplan) |
| **Execution graph** | Emergent — constructed at runtime | Pre-defined — committed in workplan |
| **Gate enforcement** | None | Per-phase checklist + Review gate |
| **Audit trail** | Context-window function-call log | Scratchpad + git commit per phase |
| **Parallelism** | Native — multiple agents callable simultaneously | Explicit — Orchestrator batches independent phases |
| **Constraint propagation** | None — each agent is independent | Via AGENTS.md encoding chain |
| **Recovery from wrong routing** | Re-invoke triage agent | Identify phase, re-run from last clean commit |
| **Best fit** | Low-governance, exploratory, rapid-dispatch tasks | Governance-critical, multi-phase, auditable workflows |
| **Values encoding** | Absent | MANIFESTO.md → AGENTS.md → role files → SKILL.md |
| **Intra-phase sub-task dispatch** | Native — low-overhead | Supported via batched delegation in phase plan |
| **State persistence** | `~/.clawteam/` JSON files; atomic `tmp + rename`; no database | `.tmp/<branch>/` scratchpad + committed research docs |
| **Worker isolation** | Per-worker git worktree (`clawteam/{team}/{agent}` branch) + tmux window | Per-session feature branch |
| **Plan approval** | v0.2.0: agents submit plans for leader review (text-based, pre-execution) | Review gate: schema compliance checklist (`validate_synthesis.py`) |
| **Governance gap** | Acknowledged upstream: "auth, permissions, audit logs" deferred to v1.0 | Encoded: AGENTS.md § Security Guardrails + pre-commit hooks |
| **Transport** | File-based JSON (default); ZeroMQ P2P optional; Redis roadmap (v0.4) | MCP local server + uv + git |

---

## 5. Recommendations

**R1 — DOCUMENT** swarm orchestration as a named external pattern in `docs/guides/` or a dedicated research note. Future agents encountering swarm-style frameworks should have an authoritative comparison to retrieve rather than re-deriving the tradeoffs. (Effort: Low)

**R2 — ADOPT** function-calling dispatch for intra-phase sub-task routing within a single executive phase where tasks are independent and low-governance (e.g., parallel file reads, parallel source fetches). This does not require a workplan phase entry and is consistent with [MANIFESTO.md § 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens). (Effort: Medium)

**R3 — DO NOT REPLACE** the inter-phase hierarchical chain with a swarm topology for governance-sensitive workflows. The takeback handoff + Review gate pattern is the substrate enforcement layer; eliding it in favour of dynamic routing transfers constraint enforcement from code to token generation. ([MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first)) (Effort: N/A — constraint, not a task)

**R4 — COMPLETED** (2026-03-30) — ClawTeams source article (MarkTechPost, Michal Sutter) and HKUDS/ClawTeam GitHub repository fetched and synthesised. ClawTeam **does** introduce primitives beyond standard OpenAI Swarm: a shared task board with `blocked_by_indices` dependency resolution, per-worker git worktree isolation, Plan Approval (v0.2.0), and a local-filesystem-first persistence model (`~/.clawteam/`). The governance gap is confirmed and acknowledged upstream (v1.0 roadmap: "auth, permissions, audit logs TBD"). Findings integrated into Sections 1, 3, and 4 above. (Effort: Low — completed)

---

## 6. Sources

1. Sutter, M. (2026-03-20). "A Coding Implementation Showcasing ClawTeams Multi-Agent Swarm Orchestration with OpenAI Function Calling." *MarkTechPost*. Fetched 2026-03-30. Pre-built templates: AI Hedge Fund (5 analysts + risk manager), Research Swarm, Engineering Team.
2. OpenAI Swarm repository (`github.com/openai/swarm`) — Educational multi-agent framework using function-calling handoffs; basis for ClawTeams' orchestration model.
3. OpenAI Platform docs — Function Calling reference — `https://platform.openai.com/docs/guides/function-calling`
4. [`docs/research/competitor-landscape-agentic-frameworks.md`](competitor-landscape-agentic-frameworks.md) — CrewAI, LangGraph, AutoGen comparative analysis (Sprint 16, Issue #301).
5. [`docs/research/agent-to-agent-communication-protocol.md`](agent-to-agent-communication-protocol.md) — Dogma's synchronous coordination model, serialised delegation rationale (Sprint 12, Issue #272).
6. [`AGENTS.md`](../../AGENTS.md) — Handoff topology, takeback pattern, and pre-phase delegation checklist — primary endogenous source.
7. [`MANIFESTO.md`](../../MANIFESTO.md) — Axioms: Endogenous-First (§1), Algorithms-Before-Tokens (§2) — governing constraints for this analysis.
8. HKUDS/ClawTeam GitHub repository — `https://github.com/HKUDS/ClawTeam` — 4.1k stars, 567 forks, 24 contributors as of 2026-03-30. Launched 2026-03-18. Primary source for: task board design, `blocked_by_indices` dependency chains, `~/.clawteam/` persistence model, per-worker git worktree isolation, Plan Approval (v0.2.0), ZeroMQ transport option, and v1.0 governance roadmap.
