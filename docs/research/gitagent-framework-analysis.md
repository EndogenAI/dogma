---
title: "GitAgent: Framework-Agnostic Agent Portability and Git-Native Supervision"
status: Final
closes_issue: 419
x-governs:
  - endogenous-first
  - algorithms-before-tokens
  - minimal-posture
created: 2026-03-30
sources:
  - url: "https://www.marktechpost.com/2026/03/22/meet-gitagent-the-docker-for-ai-agents-that-is-finally-solving-the-fragmentation-between-langchain-autogen-and-claude-code/"
    title: "Meet GitAgent: The Docker for AI Agents that is Finally Solving the Fragmentation between LangChain, AutoGen, and Claude Code"
    type: blog_post
    author: "Michal Sutter"
    date: "2026-03-22"
  - url: "https://github.com/open-gitagent/gitagent"
    title: "open-gitagent/gitagent — GitHub Repository (v0.1.8)"
    type: repository
    version: "v0.1.8"
    accessed: "2026-03-30"
recommendations:
  - id: rec-gitagent-framework-analysis-001
    title: "EXTRACT GitAgent's SOUL.md + DUTIES.md pattern as external validation of dogma's .agent.md (persona + constraints sections) — cite in agent-file-authoring SKILL.md"
    status: deferred
    effort: Low
    linked_issue: null
    decision_ref: null
  - id: rec-gitagent-framework-analysis-002
    title: "DOCUMENT Git-as-supervision-layer (state-change → PR) as an external reference pattern for dogma's Subagent Commit Authority rule in AGENTS.md"
    status: deferred
    effort: Low
    linked_issue: null
    decision_ref: null
  - id: rec-gitagent-framework-analysis-003
    title: "DO NOT ADOPT gitagent export workflow — dogma's Custom Agents are already VS Code-native; the multi-framework export adds switching-cost reduction for teams with no framework commitment, not a benefit here"
    status: deferred
    effort: Low
    linked_issue: null
    decision_ref: null
  - id: rec-gitagent-framework-analysis-004
    title: "EVALUATE GitAgent's DUTIES.md Segregation of Duties (SOD) as a model for encoding explicit permission matrices in dogma fleet agent files"
    status: deferred
    effort: Medium
    linked_issue: null
    decision_ref: null
---

# GitAgent: Framework-Agnostic Agent Portability and Git-Native Supervision

> **Status**: Final
> **Research Question**: What can be learned from GitAgent's approach to solving AI agent fragmentation across LangChain, AutoGen, and Claude Code?
> **Date**: 2026-03-30
> **Source**: MarkTechPost (Michal Sutter, 2026-03-22) — full article fetched and cached.
> **Related**: [Issue #419](https://github.com/EndogenAI/dogma/issues/419) · [`AGENTS.md`](../../AGENTS.md) · [`MANIFESTO.md`](../../MANIFESTO.md) · [`docs/research/competitor-landscape-agentic-frameworks.md`](competitor-landscape-agentic-frameworks.md)

---

## 1. Executive Summary

GitAgent is an open-source specification and CLI tool that addresses the **AI agent fragmentation problem**: developers building autonomous agents must currently commit to one of five incompatible ecosystems (LangChain, AutoGen, CrewAI, OpenAI Assistants, Claude Code), each with proprietary methods for agent logic, memory persistence, and tool execution. Switching frameworks requires near-total rewrites.

GitAgent's solution is a **universal directory-based format** stored in a Git repository. An agent is defined once as a structured folder containing `agent.yaml` (manifest), `SOUL.md` (identity/persona), `DUTIES.md` (responsibilities and segregation of duties), `skills/`, `tools/`, `rules/`, and `memory/`. The `gitagent export -f [framework_name]` command generates framework-specific boilerplate from this canonical definition.

**Key findings**:

1. **Structural convergence with dogma** — GitAgent's `SOUL.md` (persona) + `DUTIES.md` (constraints) + `rules/` (guardrails) maps directly to dogma's `.agent.md` file structure: the BDI sections (Beliefs & Context, Workflow & Intentions, Desired Outcomes) encode the same concerns. Both projects independently reached repository-as-agent-definition.
2. **Git-as-supervision layer** — GitAgent uses Git branches and Pull Requests as the *human review mechanism* for agent state changes. When an agent updates its memory or persona, it creates a PR. This is the same principle as dogma's [AGENTS.md § Subagent Commit Authority](../../AGENTS.md#subagent-commit-authority): all state changes route through a review gate before merge.
3. **Framework portability vs. values governance** — GitAgent solves the framework-switching problem but does not address values governance. There is no equivalent to MANIFESTO.md, validate_agent_files.py, or the L0–L3 maturity enforcement chain.
4. **Segregation of Duties (SOD)** — GitAgent's `DUTIES.md` and the `gitagent validate` compliance check for regulated industries is a notable external reference for dogma's [AGENTS.md § Executive Fleet Privileges](../../AGENTS.md#executive-fleet-privileges) permission model.
5. **Memory as human-readable Markdown** — GitAgent stores long-term agent state in `memory/context.md` and `memory/dailylog.md` — inspectable, version-controlled, and revertible via `git revert`. Dogma's equivalent is the session scratchpad in `.tmp/<branch>/<date>.md`.
6. **Deterministic workflow execution** (v0.1.8) — The new `workflows/` directory defines step sequences as YAML with `depends_on` ordering and `${{ }}` data flow; the execution engine enforces ordering so there is "no LLM discretion on execution order." This independently converges with dogma's [`data/phase-gate-fsm.yml`](../../data/phase-gate-fsm.yml) and [MANIFESTO.md § 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens): both encode sequencing as a deterministic dependency graph rather than model inference.

**Verdict**: Extract patterns; do not adopt the full framework. GitAgent validates dogma's agent-file architecture from an independent team at production scale. The export workflow adds no value for a VS Code-committed fleet.

---

## 2. Hypothesis Validation

| Hypothesis | Result | Evidence |
|------------|--------|----------|
| **H1**: GitAgent's universal format maps to dogma's `.agent.md` conventions | ✅ **STRONGLY SUPPORTED** | `SOUL.md` = persona/tone section; `DUTIES.md` = constraints section; `rules/` = guardrails; `skills/` = skill references. The structural equivalence is direct. An independent team reached the same agent-as-repository-directory solution. |
| **H2**: Git-as-supervision matches dogma's commit authority model | ✅ **SUPPORTED** | GitAgent routes agent state changes (memory updates, persona drift) to a PR for human review. Dogma's Subagent Commit Authority rule routes all committed changes through the GitHub Agent after Review APPROVED. Both use Git's diff + review mechanism as the human-in-the-loop enforcement layer. |
| **H3**: GitAgent introduces a framework-agnostic portability mechanism absent in dogma | ✅ **SUPPORTED** | The `gitagent export` CLI is not a dogma capability. Dogma's fleet is VS Code Custom Agents-native. GitAgent's export mechanism would only provide value if dogma targeted multiple orchestration frameworks simultaneously, which contradicts [MANIFESTO.md § 3 Local Compute-First](../../MANIFESTO.md#3-local-compute-first) (vendor lock-in is already managed by maintaining a Local-first posture, not by multi-framework export). |
| **H4**: GitAgent's compliance layer (SOD) is complementary to dogma's permission model | ✅ **PARTIALLY SUPPORTED** | GitAgent's `DUTIES.md` SOD + `gitagent validate` provides FINRA/SEC compliance checks. Dogma's executive permission matrix ([AGENTS.md § Executive Fleet Privileges](../../AGENTS.md#executive-fleet-privileges)) covers the same concern but is defined in natural language, not as a machine-checkable constraint matrix. The GitAgent approach is more rigorous for regulated industries; dogma's is more expressive for governance policy. |
| **H5**: GitAgent's memory model (Markdown files) maps to dogma's scratchpad | ✅ **SUPPORTED** | GitAgent stores state in `memory/context.md` + `memory/dailylog.md` — human-readable, version-controlled, revertible. Dogma's `.tmp/<branch>/<date>.md` scratchpad pattern serves the same cross-session memory function. Both reject opaque vector database memory in favour of inspectable text files. |

---

## 3. Pattern Catalog

### Pattern 1: Agent-as-Repository-Directory (GitAgent Universal Format)

**Problem**: AI agent definitions are scattered across Python files, system prompt strings, tool lists buried in framework-specific config, and memory schemas in opaque databases. No single artifact captures the agent's identity, capabilities, constraints, and state in a form that is portable, inspectable, and version-controlled.

**Solution**: Define the agent as a structured directory under Git. Identity lives in `SOUL.md`, capabilities in `skills/` and `tools/`, guardrails in `rules/`, memory in `memory/`, and compliance constraints in `DUTIES.md`. The root `agent.yaml` provides the manifest (model provider, version, dependencies). The entire agent can be diffed, branched, forked, and shared as an open-source repository.

**Canonical example**: GitAgent format (`open-gitagent/gitagent`, v0.1.8, 2026). `gitagent init myagent` produces a folder with `SOUL.md`, `DUTIES.md`, `skills/greet.md`, `tools/search.py`, `rules/guardrails.md`, `memory/context.md`. Running `gitagent export -f claude-code` adapts the structure to an Anthropic CLAUDE.md + tools directory; `gitagent export -f langchain` produces a LangGraph node graph. One source of truth; twelve deployment targets (v0.1.8 adapters: `system-prompt`, `claude-code`, `openai`, `crewai`, `lyzr`, `github`, `git`, `opencode`, `gemini`, `openclaw`, `nanobot`, `cursor`).

**Canonical example (multi-agent)**: GitAgent NVIDIA Deep Researcher port (v0.1.8 README). A 3-agent hierarchy — orchestrator, planner, researcher — where each agent is a subdirectory under `agents/`. The root-level `skills/` and `tools/` directories are automatically shared across all three agents. `gitagent validate --compliance` blocks deployment when the planner agent's `DUTIES.md` grants permissions that conflict with the orchestrator's role constraints (Segregation of Duties enforcement at deploy time, not runtime). `gitagent export --format claude-code` generates a `CLAUDE.md` capturing the full multi-agent hierarchy. Bidirectional: `gitagent import --from claude-code` can reconstruct a GitAgent directory layout from an existing `CLAUDE.md`.

**Dogma mapping**: This is [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) applied to agent portability: the agent's definition is the endogenous source from which all framework-specific artifacts are generated. Dogma's `.agent.md` file is the equivalent endogenous source for the VS Code Custom Agents runtime; `validate_agent_files.py` is the equivalent of `gitagent validate` for schema compliance.

**Anti-pattern**: Generating framework-specific agent code directly (e.g., writing a CrewAI `Agent()` constructor inline) without an upstream canonical definition. This makes the agent definition framework-coupled from birth — any future migration requires reconstructing the canonical form from the framework-specific output, reversing the generation direction at high cost.

---

### Pattern 2: Git-Native Supervision via State-Change Pull Requests

**Problem**: Agent memory and persona drift are invisible. When an autonomous agent updates its `context.md` or learns a new skill, the change is applied silently to the running agent. There is no mechanism for a human to inspect, approve, or revert behavioral changes without inspecting opaque database state.

**Solution**: Treat every agent state change as a code change. When the agent modifies its memory or persona, the framework creates a new Git branch and a Pull Request containing the diff. Human reviewers apply standard code review practices: inspect the diff, confirm the change is intended, approve or request changes. `git revert` rolls back any unwanted behavioral drift.

**Canonical example**: GitAgent supervision layer (2026). An agent processing financial data updates its `context.md` with a new risk assessment heuristic it derived from market data. GitAgent creates a branch `agent/memory-update-2026-03-22` and opens a PR titled "Memory update: new risk heuristic derived from Q1 2026 data." A compliance reviewer inspects the diff — the new heuristic is a three-sentence Markdown addition — approves the PR, and the change is merged. If the heuristic later proves incorrect, `git revert` restores the prior state.

**Dogma mapping**: This directly implements [AGENTS.md § Subagent Commit Authority](../../AGENTS.md#subagent-commit-authority): "Only Executive Orchestrator and Executive Docs agents commit to the repository. All other agents return work to their executive for review and commit gatekeeping." The GitAgent PR-per-state-change is a finer-grained version of this principle applied to agent memory, not only code.

**Anti-pattern**: Agents that update memory via direct database writes or in-context accumulation with no Git trace. The authoritative state of the agent is dispersed across a vector store, a model's context, and a running process — none of which support `git revert` or PR-style review. Memory drift accumulates silently and is only detectable when behaviour degrades visibly.

---

### Pattern 3: Deterministic Workflow Execution (No LLM Discretion on Ordering)

**Problem**: Multi-step agent tasks involve sequencing decisions — which step runs first, what data flows between steps, when to branch. If ordering is left to LLM inference it is non-deterministic: the same task may execute differently on re-run, and causal attribution (which step produced which output) is ambiguous. Compliance-sensitive tasks require reproducible execution order.

**Solution**: GitAgent's `workflows/` directory (v0.1.8) defines task sequences as YAML files with explicit `depends_on` declarations and `${{ }}` template expressions for controlled data flow. LLMs are invoked for reasoning *within* each step; sequencing *between* steps is the execution engine's responsibility alone.

**Canonical example**: GitAgent `workflows/research.yml` (v0.1.8 README). A workflow specifies three steps: `fetch`, `summarise` (depends_on: fetch), `compile_report` (depends_on: summarise). The `${{ steps.fetch.output.sources }}` template expression injects the upstream artifact into the downstream prompt. The engine guarantees `summarise` never runs until `fetch` completes and its output resolves. Execution order is a data structure property, not a model judgment call.

**Dogma mapping**: Independent convergence with [`data/phase-gate-fsm.yml`](../../data/phase-gate-fsm.yml) — dogma's phase-gate FSM encodes the same principle as a directed graph with explicit predecessor gates; no phase may run until its gate dependencies are satisfied. Both instantiate [MANIFESTO.md § 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens). Dogma implements this at the multi-agent session level (AGENTS.md sprint-phase ordering constraints); GitAgent implements it at the single-agent workflow-step level. The two are complementary layers of the same principle, not competing implementations.

**Anti-pattern**: Free-form ReAct loops where the LLM decides "what to do next" without a declared dependency graph. Non-deterministic step ordering makes debugging, compliance auditing, and reproducibility intractable — and cannot satisfy a `depends_on` contract because the dependency graph exists only inside the model's context window.

---

## 4. Comparison Table: GitAgent Abstractions vs. Dogma Fleet Patterns

| GitAgent Abstraction | Dogma Equivalent | Key Difference |
|----------------------|-----------------|----------------|
| `SOUL.md` (identity, persona, tone) | `.agent.md` §Beliefs & Context | Dogma uses BDI XML sections; GitAgent uses freeform Markdown file per concern |
| `DUTIES.md` (responsibilities, SOD constraints) | `.agent.md` §Constraints + AGENTS.md § Executive Fleet Privileges | GitAgent's SOD is machine-checkable via `gitagent validate`; dogma's is natural language governance |
| `rules/guardrails.md` | AGENTS.md § Guardrails | AGENTS.md governs the entire fleet; GitAgent's rules are per-agent |
| `skills/` (behavioural patterns) | `.github/skills/<name>/SKILL.md` | Both encode reusable procedures; dogma skills are cross-agent; GitAgent skills are per-agent-repo |
| `tools/` (Python functions/API defs) | MCP tools in `mcp_server/tools/` | Architectural equivalents; dogma uses MCP protocol; GitAgent uses raw Python callables |
| `memory/context.md` | `.tmp/<branch>/<date>.md` (scratchpad) | Dogma scratchpad is session-scoped; GitAgent memory is persistent across sessions |
| `agent.yaml` (manifest, model, deps) | `.agent.md` frontmatter (name, description, tools, tier) | Both are manifest files; GitAgent's includes model provider binding; dogma's specifies VS Code tool access |
| `gitagent export -f [framework]` | No equivalent | Dogma is VS Code Custom Agents-native; multi-framework export is not a current requirement |
| `gitagent validate` (SOD compliance) | `scripts/validate_agent_files.py` | Both validate agent files against a schema; GitAgent's targets compliance regulations; dogma's targets governance conventions |
| PR-per-state-change (Git supervision) | AGENTS.md § Subagent Commit Authority | GitAgent applies this to agent memory; dogma applies it to code/doc artifacts |
| `workflows/` directory (YAML, `depends_on`, `${{ }}` data flow) | [`data/phase-gate-fsm.yml`](../../data/phase-gate-fsm.yml) + AGENTS.md § Sprint Phase Ordering Constraints | Both encode execution sequencing as a deterministic dependency graph; GitAgent at workflow-step level, dogma at multi-agent session-phase level |
| `gitagent import --from <fmt>` (claude, cursor, crewai, opencode) | No equivalent (dogma agents are produced endogenously from `.agent.md`) | Bidirectional portability: reconstructs a GitAgent layout from an existing Claude Code, Cursor, or CrewAI config; whether the importer handles dogma's XML BDI tags (`<context>`, `<instructions>`, etc.) is unknown — open question |
| `gitagent skills` sub-command (registry search/install) | No equivalent (dogma skills are committed to `.github/skills/`) | GitAgent skills fetched from external registry on demand; dogma skills are endogenous artefacts — stronger governance traceability, weaker external discoverability |
| `hooks/` directory (`bootstrap.md`, `teardown.md`) | No equivalent (dogma lifecycle encoded in AGENTS.md session-management prose and scratchpad conventions) | GitAgent makes agent lifecycle events explicit as named Markdown files; both solve the same problem at different traceability levels |
| `agents/` sub-directory (recursive sub-agent nesting) | `.github/agents/<name>.agent.md` (flat fleet) | GitAgent sub-agents are nested directories within a parent; dogma agents are flat files in a central fleet — flat structure simplifies fleet-wide governance scripts; recursive structure may better support deeply hierarchical multi-agent systems |

---

## 5. Interoperability Assessment with Dogma Custom Agents

**Direct compatibility**: High structural overlap. A dogma `.agent.md` file could be mapped to a GitAgent repository layout with low effort:
- Frontmatter `name` + `description` → `agent.yaml`
- `## Beliefs & Context` → `SOUL.md`
- `## Constraints` → `DUTIES.md` + `rules/`
- Referenced skill files → `skills/`
- MCP tool references → `tools/`

**Export compatibility**: The `gitagent export -f claude-code` target would generate a `CLAUDE.md` file, which overlaps with dogma's `CLAUDE.md`. A dogma repository is already a Claude Code-compatible project; the export adds nothing.

**Divergence point**: Dogma's fleet governance (L0–L3, validate_agent_files.py, AGENTS.md encoding chain, pre-commit hooks) has no analog in GitAgent. GitAgent does not implement a programmatic enforcement hierarchy. For a team committed to values governance as a structural property, dogma's substrate is not replaceable by GitAgent's portability layer.

**Adoption recommendation**: **Extract patterns, not the framework.** The `SOUL.md` + `DUTIES.md` naming convention is a useful external reference. The PR-per-state-change supervision mechanism validates dogma's commit authority model. The SOD matrix in `DUTIES.md` is worth evaluating as a model for encoding explicit permission matrices in agent files.

**Deployment Layer gap** (v0.1.8 finding): GitAgent's `agent.yaml` supports a `compliance:` field for regulatory constraints (SOD, FINRA), but has no equivalent to dogma's `client-values.yml` Deployment Layer — a mechanism for external-values override without modifying agent files. For multi-tenant deployments where different clients require different constraint sets on the same fleet, GitAgent would require forking the repository or overriding `agent.yaml` at deploy time. Dogma's Deployment Layer is currently more fully developed for multi-tenant governance. If R4 (machine-checkable SOD permission matrices) is evaluated, the implementation should accommodate Deployment Layer overrides rather than introducing a static `compliance:` block that conflates fleet-wide and client-specific constraints.

**`gitagent import` and XML BDI tags (open question)**: `gitagent import --from claude-code` reconstructs a GitAgent directory layout from an existing `CLAUDE.md`. Dogma's `.agent.md` files use XML BDI wrappers (`<context>`, `<instructions>`, `<constraints>`, `<output>`) that are not standard Claude Code conventions. It is unknown whether the importer preserves, ignores, or strips these tags. If dogma ever evaluates GitAgent portability, this must be tested — the BDI structure is a load-bearing governance convention, not decorative markup.

---

## 6. Recommendations

**R1 — EXTRACT** (Low effort): Cite GitAgent's `SOUL.md` + `DUTIES.md` pattern in the `agent-file-authoring` SKILL.md as external validation of dogma's `.agent.md` persona-constraints structure. This strengthens the endogenous case for the current authoring conventions without adopting any external dependency.

**R2 — DOCUMENT** (Low effort): Add GitAgent's PR-per-state-change supervision mechanism as an external reference in `AGENTS.md § Subagent Commit Authority`. It validates the principle that all agent state changes — not just code — should route through a human review gate.

**R3 — DO NOT ADOPT** the `gitagent export` workflow. Dogma's fleet is VS Code Custom Agents-native. Multi-framework export adds operational surface without governance benefit. Introducing an external CLI dependency for framework portability is inconsistent with [MANIFESTO.md § 3 Local Compute-First](../../MANIFESTO.md#3-local-compute-first) unless a concrete multi-framework requirement emerges.

**R4 — EVALUATE** (Medium effort): GitAgent's `DUTIES.md` SOD constraint matrix + `gitagent validate` is more rigorous than dogma's natural-language permission tables. For regulated-industry deployments or future client-values.yml use cases, encoding explicit permission matrices as machine-checkable YAML (analogous to `gitagent validate`) may provide stronger compliance guarantees than narrative governance prose.

---

## 7. Sources

1. Sutter, M. (2026-03-22). "Meet GitAgent: The Docker for AI Agents that is Finally Solving the Fragmentation between LangChain, AutoGen, and Claude Code." MarkTechPost. `https://www.marktechpost.com/2026/03/22/meet-gitagent-the-docker-for-ai-agents-that-is-finally-solving-the-fragmentation-between-langchain-autogen-and-claude-code/`
2. `open-gitagent/gitagent` v0.1.8 (accessed 2026-03-30): `https://github.com/open-gitagent/gitagent` — primary source for v0.1.8 adapter list (12 targets), `workflows/` directory pattern, `gitagent import`, `gitagent skills`, `hooks/`, and NVIDIA Deep Researcher canonical example.
3. [`docs/research/competitor-landscape-agentic-frameworks.md`](competitor-landscape-agentic-frameworks.md) — BMAD Method, Kiro, CrewAI, LangGraph, OpenHands comparative analysis (Sprint 16, Issue #301).
4. [`docs/research/agentic-platform-engineering-github-copilot.md`](agentic-platform-engineering-github-copilot.md) — External validation of dogma's `.agent.md` conventions via Microsoft Cluster Doctor pattern (Sprint 18, Issue #433).
5. [`docs/research/agent-to-agent-communication-protocol.md`](agent-to-agent-communication-protocol.md) — Dogma's synchronous coordination and serialised delegation model (Sprint 12, Issue #272).
6. [`AGENTS.md`](../../AGENTS.md) — Subagent Commit Authority, Executive Fleet Privileges, agent authoring conventions — primary endogenous source.
7. [`MANIFESTO.md`](../../MANIFESTO.md) — Axioms: Endogenous-First (§1), Algorithms-Before-Tokens (§2), Local Compute-First (§3) — governing constraints.
