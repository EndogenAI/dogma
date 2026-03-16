---
title: "Custom Agent Service Modules — Per-Agent API Layers and the Skills/Service Boundary"
status: "Final"
research_issue: 265
closes_issue: 265
date: 2026-03-15
sources:
  - https://python.langchain.com/docs/concepts/tools/
  - https://a2aproject.github.io/A2A/latest/specification/
  - https://code.visualstudio.com/docs/copilot/chat/mcp-servers
  - https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tool-use.html
  - .github/skills/agent-file-authoring/SKILL.md
  - docs/decisions/ADR-006-agent-skills-adoption.md
  - AGENTS.md
---

# Custom Agent Service Modules — Per-Agent API Layers and the Skills/Service Boundary

> **Status**: Final
> **Research Question**: What is the right boundary between a VS Code Custom Agent (.agent.md), a SKILL.md, and a dedicated service module? When should an agent get its own API layer?
> **Date**: 2026-03-15
> **Related**: [`docs/decisions/ADR-006-agent-skills-adoption.md`](../decisions/ADR-006-agent-skills-adoption.md) · [`AGENTS.md` §Agent Fleet Overview](../AGENTS.md#agent-fleet-overview) · [`docs/research/agents/agent-skills-integration.md`](agents/agent-skills-integration.md) · [`docs/research/agents/skills-as-decision-logic.md`](agents/skills-as-decision-logic.md)

---

## 1. Executive Summary

As the EndogenAI fleet grows, agents accumulate domain-specific interactions with external systems: GitHub API, local file systems, inference endpoints, and vector DBs. Currently these interactions are encoded either as agent instructions, SKILL.md procedures, or scripts in `scripts/`. The question is whether a distinct "service module" layer is warranted — a programmatic API client scoped to one responsibility domain, analogous to the service files in frontend/backend architecture.

This research surveyed four frameworks (LangChain Tools, AutoGen Tool Use, A2A Agent Cards, VS Code MCP servers) and compared against the endogenic `scripts/` convention and the ADR-006-established SKILL.md standard. Five hypotheses were tested; three confirmed, one reframed, one deferred.

**Key finding**: A formal `services/` directory is **not yet warranted**. The three-layer boundary — SKILL.md (when/why), scripts/ (how), MCP server tools (what is callable) — covers the current fleet's needs without introducing a new architectural primitive. The escalation path from inline agent instructions → SKILL.md → scripts/ utility → MCP-exposed tool already models service complexity correctly. Per-agent API layers (as in A2A's Agent Card pattern) are premature until agent-to-agent REST communication is required; that is a Wave 3+ consideration.

The most actionable finding is the **SKILL-as-specification, script-as-implementation** boundary: when a workflow procedure in a SKILL.md references a specific external system call that runs more than twice interactively, that call must be encoded in a `scripts/` utility (Programmatic-First) and the SKILL.md updated to cite it. This prevents service logic from accumulating silently in agent instruction prose.

---

## 2. Hypothesis Validation

### H1 — Established agentic frameworks have a formal "service layer" concept

**Verdict**: CONFIRMED (with nuance) — the pattern exists but is per-capability, not per-agent

**Evidence**: 

**LangChain Tools** (LangChain, 2025): LangChain's primary service abstraction is the `Tool` — a Python function with a typed signature and description, registered with an agent. Tools are per-capability (e.g., `search`, `calculator`, `python_repl`) rather than per-agent. A tool IS a service module: it encapsulates a single capability behind a clean interface callable by any agent.

**AutoGen Tool Use** (Microsoft, 2025): AutoGen uses a decorator pattern (`@register_for_llm`, `@register_for_execution`) to expose Python functions as callable tools. Like LangChain, tools are per-capability. AutoGen's "service layer" is the set of registered functions — there is no per-agent API layer.

**A2A Protocol** (Google, 2024): Agent-to-Agent protocol specifies an **Agent Card** — a JSON manifest at `/.well-known/agent.json` describing each agent's capabilities, API endpoint, and authentication requirements. Each agent runs as an HTTP service. This IS a per-agent service layer, but it is designed for agent-to-agent REST communication across organizational boundaries (different companies, different platforms). Not relevant for an intra-fleet, same-machine orchestration.

**VS Code MCP Servers**: An MCP server IS a service layer — it exposes a collection of tools (capabilities) via a defined protocol. MCP servers are per-domain (e.g., a filesystem server, a git server, a GitHub API server), not per-agent.

**Nuance**: In every framework, the service layer is organized **per capability or per domain**, never per-agent. Per-agent service layers emerge only at organizational API boundaries (e.g., A2A). This is the critical insight for EndogenAI.

---

### H2 — There is a clear boundary between SKILL.md (procedural) and a service module (programmatic)

**Verdict**: CONFIRMED — the boundary is specification vs. implementation

**Evidence**: [`ADR-006-agent-skills-adoption.md`](../decisions/ADR-006-agent-skills-adoption.md) states: "Agents encode *who does a task*; skills encode *how a task is done*." This decision established the SKILL.md as the **specification layer**: it encodes workflow procedures, conventions, and decision logic — the *what* and *when*.

A service module (script or MCP tool) is the **implementation layer**: deterministic code that executes a capability. The relationship is:

| Layer | Encodes | Format | Consumer |
|-------|---------|--------|----------|
| `.agent.md` | *Who* does the task, with what tools | YAML + Markdown | VS Code (runtime) |
| `SKILL.md` | *How* to orchestrate the task (step-by-step) | Markdown | LLM (via context loading) |
| `scripts/*.py` | *How* to execute a specific operation deterministically | Python | Shell / LLM tool call |
| MCP server tool | *What* capabilities are available programmatically | JSON+RPC | LLM tool call dispatcher |

The SKILL.md cites the script; the script is the service. A SKILL.md that embeds shell commands inline (rather than citing a script) has absorbed service logic into the specification layer — a violation of the [Programmatic-First principle](../AGENTS.md#programmatic-first-principle).

**Canonical example**: The `session-management` SKILL.md cites `prune_scratchpad.py` for session init/close operations. The SKILL encodes *when* to run it (session start, session end), what arguments to use, and how to interpret results. The script encodes the *how* — file system manipulation, heading parsing, archival. The boundary is clean: SKILL owns the protocol, script owns the implementation.

**Anti-pattern**: A SKILL.md that embeds a 20-line bash script inline to execute a GitHub API call. When the GitHub API endpoint changes, the script must be updated in every SKILL.md that embeds it — a documentation drift failure. The correct encoding: extract to `scripts/github_utils.py`, cite from the SKILL.md, update only the script when the API changes.

---

### H3 — Service modules should be per-domain, not per-agent

**Verdict**: CONFIRMED — per-domain aligns with Minimum Posture and fleet topology

**Evidence**: All surveyed frameworks (LangChain, AutoGen, MCP) organize capabilities per-domain. The [`AGENTS.md` §Agent Fleet Overview](../AGENTS.md#agent-fleet-overview) establishes 9 executive agents, each scoping to a domain (Research, Docs, Scripts, Fleet, PM, Planner, GitHub, Automator, Orchestrator). Service modules should align to these domain boundaries, not to individual agents:

| Domain | Service module (current `scripts/` pattern) | MCP server (future) |
|--------|---------------------------------------------|---------------------|
| GitHub | `bulk_github_operations.py`, `bulk_github_read.py` | `github-mcp-server` |
| File system | (implicit via VS Code tools) | `filesystem-mcp-server` |
| Research | `fetch_source.py`, `fetch_all_sources.py` | `source-cache-mcp-server` |
| Agent fleet | `validate_agent_files.py`, `generate_agent_manifest.py` | (scripts sufficient) |

Per-agent API layers would create 9 separate service files for 9 agents, with significant capability overlap. Per-domain reduces to 4–6 service modules with clear ownership.

**Canonical example**: The GitHub Agent and the Executive PM both need GitHub API access. A per-domain `scripts/bulk_github_operations.py` is shared by both, with each agent calling it with different arguments. A per-agent pattern would produce `github_agent_service.py` and `pm_agent_service.py` — near-identical files maintained redundantly.

**Anti-pattern**: Creating `github_executive_service.py`, `pm_executive_service.py`, and `orchestrator_github_service.py` as three separate files wrapping the same `gh` CLI calls. Violates DRY and the [Programmatic-First principle](../AGENTS.md#programmatic-first-principle) (three similar scripts created before scripting the shared capability once).

---

### H4 — VS Code MCP is the correct service layer for agent-callable capabilities

**Verdict**: PARTIALLY CONFIRMED — MCP is the right long-term layer; scripts/ is the correct present-day layer

**Evidence**: VS Code MCP servers provide clean tool invocation for any agent (per the [`local-mcp-frameworks.md`](agents/local-mcp-frameworks.md) research). For the current fleet (9 agents, 40+ scripts), the abstraction cost of wrapping all scripts as MCP tools exceeds the benefit. The scripts/ pattern is already well-tested, documented, and CI-validated.

The inflection point where MCP becomes preferable: when **more than 2 agents call the same script as part of their workflow** — at that point, surfacing the script as an MCP tool eliminates the subprocess overhead and provides a more ergonomic invocation interface for the LLM (tool call vs. shell command).

MCP is also the appropriate layer for **read-heavy, low-latency capabilities** (e.g., file search, git log) that are called many times per session and benefit from the structured tool-call interface over raw shell output.

---

### H5 — A new `services/` directory is needed for service modules

**Verdict**: NOT CONFIRMED — `scripts/` covers the current need; new directory is premature

**Evidence**: The `scripts/` directory already functions as the service layer. Adding a `services/` directory would fragment the convention without adding capability. The [Programmatic-First principle](../AGENTS.md#programmatic-first-principle) and `scripts/README.md` already enforce the "one-time interaction → SKILL → script" escalation path.

A `services/` directory becomes warranted only when a formal API client layer is needed — e.g., an async Python client for an external REST service that is too complex for a utility script. This is not the current fleet's situation.

---

## 3. Pattern Catalog

### P1 — SKILL-as-Specification, Script-as-Implementation

**Description**: SKILL.md files encode the *when*, *why*, and *orchestration sequence* for a capability. Scripts encode the *how*. The SKILL cites the script; the script is the service.

**Canonical example**: `session-management` SKILL.md §5 ("Size Management") cites `prune_scratchpad.py` with exact arguments for each use case. Any agent reading the SKILL knows exactly which script to call and when. The script handles file system operations; the SKILL handles the decision logic. When either changes independently, the other remains stable.

**Anti-pattern**: A SKILL.md paragraph that begins "Run the following commands in the terminal: `gh issue list --json ...`" and embeds API-specific flags inline. When `gh` CLI flags change, this SKILL.md degrades silently. The correct encoding: abstract behind a script with a stable interface (`scripts/bulk_github_read.py --query open-issues`).

---

### P2 — Domain-Scoped Service Modules in `scripts/`

**Description**: One service script per external system domain, shared across all agents that interact with that domain. Scripts expose a CLI interface (not a Python API) so they are agent-agnostic.

**Boundary rule**: A script becomes a service module when it (a) wraps external API calls, (b) is called by more than one agent or SKILL, and (c) has a stable input/output contract. Scripts that do only one of these remain utilities.

**Canonical example**: `scripts/bulk_github_operations.py` is the GitHub domain service module — it wraps `gh` CLI calls, handles pagination, and exposes a consistent JSON output. Both the PM domain and the GitHub agent domain call it. It is tested, documented, and discoverable via `scripts/README.md`.

**Anti-pattern**: Per-agent duplication — GitHub Agent has `github_agent_calls.py` and PM Agent has `pm_github_calls.py`, each re-implementing `gh issue list` with minor variations. When the GitHub CLI changes, both files must be updated independently.

---

### P3 — MCP Escalation Path

**Description**: Service capabilities escalate from inline → SKILL.md → scripts/ utility → MCP server tool, driven by usage frequency and multi-agent share.

**Escalation triggers**:
1. Done once interactively → note it
2. Done twice interactively → Note it in SKILL.md or encode in a script
3. Done 3+ times or in 2+ agent bodies → mandatory script (Programmatic-First)
4. Script called by 3+ agents OR called 10+ times per session → evaluate MCP server migration

**Canonical example**: The source-caching capability started as an informal `curl` command in a research guide. After the third research session, it was encoded as `scripts/fetch_source.py`. After the fetch script was called by both Research Scout and Executive Researcher agents, it was extended to `scripts/fetch_all_sources.py` with batch capability — the domain service module for the Research domain.

---

## 4. Recommendations

**R1 — Enforce SKILL-as-Specification by SKILL.md authoring convention (HIGH PRIORITY)**
Add to the `skill-authoring` SKILL.md: "If a SKILL step runs a shell command more than once interactively, that command must be encoded in a `scripts/` utility before the SKILL cites it." This closes the most common service-logic-accumulation failure mode.

**R2 — Document the current service module inventory in `scripts/README.md`**
Add a "Service Modules" subsection to `scripts/README.md` that identifies scripts meeting the service module criteria (external API wrapper, multi-agent, stable contract). Estimated 6–8 scripts currently qualify. This makes the service layer explicit without introducing a new directory.

**R3 — Establish MCP escalation criteria in `docs/guides/`**
Document the four-stage escalation path (inline → SKILL → script → MCP tool) in a guide (or extend `docs/guides/workflows.md`). Gate the MCP escalation on: script called by ≥3 agents OR ≥10 times per session. This prevents premature MCP adoption.

**R4 — Defer A2A Agent Card pattern (LOW PRIORITY)**
A2A per-agent service layers are appropriate only when EndogenAI agents need to communicate with external, independently-deployed agents via REST. This is not the current architecture. Revisit in Wave 3+ when cross-organizational agent communication is a requirement.

---

## 5. Sources

### Internal

- [`AGENTS.md` §Agent Fleet Overview](../AGENTS.md#agent-fleet-overview) — fleet topology, domain mapping for service module scoping
- [`AGENTS.md` §Programmatic-First Principle](../AGENTS.md#programmatic-first-principle) — escalation criteria, three-times rule, script-before-third-time
- [`docs/decisions/ADR-006-agent-skills-adoption.md`](../decisions/ADR-006-agent-skills-adoption.md) — SKILL.md adoption decision, agents-vs-skills boundary, encoding inheritance extension
- [`.github/skills/agent-file-authoring/SKILL.md`](../../.github/skills/agent-file-authoring/SKILL.md) — agent authoring conventions, posture-mapped toolsets
- [`docs/research/agents/agent-skills-integration.md`](agents/agent-skills-integration.md) — skills integration patterns
- [`docs/research/agents/local-mcp-frameworks.md`](agents/local-mcp-frameworks.md) — MCP server architecture, tool-call patterns

### External

- LangChain Tools Concepts (LangChain, 2025): [python.langchain.com/docs/concepts/tools/](https://python.langchain.com/docs/concepts/tools/) — per-capability tool design, typed signatures
- A2A Specification (Google, 2024): [a2aproject.github.io/A2A/latest/specification/](https://a2aproject.github.io/A2A/latest/specification/) — Agent Card pattern, per-agent HTTP service layer (organizational boundary use case)
- VS Code MCP Servers (Microsoft, 2025): [code.visualstudio.com/docs/copilot/chat/mcp-servers](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) — MCP server tool invocation in VS Code Copilot
- AutoGen Tool Use (Microsoft, 2025): [microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tool-use.html](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tool-use.html) — per-capability tool registration, decorator pattern
