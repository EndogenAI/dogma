# Agent Fleet Catalog

VS Code Copilot custom agents for the EndogenAI Workflows project.
Each `.agent.md` file appears in the Copilot chat agents dropdown automatically.

For authoring rules — frontmatter schema, posture table, handoff patterns — see [`.github/agents/AGENTS.md`](./AGENTS.md).

Typical workflow: **Plan → (approve) → Implement → (complete) → Review → GitHub (commit)**

---

## Milestone-Driven Agent Organization

Agents are organized by **project milestone phase**, reflecting the Endogenic Development Methodology buildout:

| Milestone | Purpose | Phase | Agents |
|-----------|---------|-------|--------|
| **Foundation: Endogenic Methodology** | Codify framework, research, strategy | Current | Executive Researcher fleet |
| **Wave 1: Agent Fleet Tier A+B** | Specialist research + engineering agents | **Focus** | Tier A (6 research agents), Tier B (5 engineering agents), Skills agents |
| **Wave 2: Agent Fleet Tier C+D** | Community + knowledge/governance agents | Planned | Tier C (3 community agents), Tier D (5 knowledge agents) |
| **Adoption: Scripts & Tooling** | Onboarding wizards, developer tools | Planned | Executive Scripter, adoption agents |
| **Hardening: Production Readiness** | Security, performance, CI gates | Queued | Security agents, CI Monitor, Test Coordinator |

Each agent in the catalog below is tagged with its milestone (`tier:`) and effort estimate (`effort:`).

---

## Research Agents

Orchestrate research sessions from question to committed synthesis. The Executive Researcher drives the fleet using the expansion→contraction pattern.

| Agent | File | Posture | Tier | Effort | Exec Tier | Terminal | Trigger |
|-------|------|---------|------|--------|----------|---------|---------|
| **Executive Researcher** | `executive-researcher.agent.md` | full | Foundation | L | Researcher | Y | Start a research session; orchestrate Scout→Synthesizer→Reviewer→Archivist; spawn new area agents |
| **Research Scout** | `research-scout.agent.md` | read + web | Foundation | M | (none) | N | Gather and catalogue raw sources for a topic — no synthesis |
| **Research Synthesizer** | `research-synthesizer.agent.md` | read + create | Foundation | L | (none) | N | Transform Scout findings into a structured synthesis draft in `docs/research/` |
| **Research Reviewer** | `research-reviewer.agent.md` | read-only | Foundation | M | (none) | N | Validate synthesis drafts against methodology standards; flag gaps and unsupported claims |
| **Research Archivist** | `research-archivist.agent.md` | read + create | Foundation | S | (none) | N | Finalise approved drafts, commit to `docs/research/`, update issue |

**Guardrail — Web Scouting is Mandatory**: Every research sprint must include an explicit Scout delegation to conduct aggressive web searches for external authoritative sources (academic papers, official documentation, standards, industry reports, practitioner knowledge). Skipping web searching to save time or tokens is an anti-pattern. Endogenous-First means local sources are consulted *first*, but web discovery is the core expansion activity. A research sprint with <7 primary external sources is incomplete. For detailed web scouting requirements, see [`research-scout.agent.md`](./research-scout.agent.md) and [`.github/skills/deep-research-sprint/SKILL.md`](../skills/deep-research-sprint/SKILL.md).

---

## Documentation Agents

Maintain and evolve all project documentation — encoding dogmatic values and methodology across every documentation layer.

| Agent | File | Posture | Tier | Effort | Exec Tier | Terminal | Trigger |
|-------|------|---------|------|--------|----------|---------|---------|
| **Executive Docs** | `executive-docs.agent.md` | read + create | Foundation | L | Docs | Y | Update guides, top-level docs, AGENTS.md, MANIFESTO.md; codify values across all documentation layers |

---

## Scripting & Automation Agents

Enforce the programmatic-first principle — encode repeated tasks as scripts and non-agent automation before performing them a third time interactively.

| Agent | File | Posture | Tier | Effort | Exec Tier | Terminal | Trigger |
|-------|------|---------|------|--------|----------|---------|---------|
| **Executive Scripter** | `executive-scripter.agent.md` | full | Wave 1 | L | Scripter | Y | Identify tasks done >2 times interactively; audit `scripts/` for gaps; write or extend scripts |
| **Executive Automator** | `executive-automator.agent.md` | full | Wave 1 | L | Automator | Y | Design file watchers, pre-commit hooks, CI tasks, VS Code background tasks; first escalation for event-driven automation |

---

## Planning & Coordination Agents

Decompose and sequence complex multi-domain work before execution begins. Invoke these when a request spans multiple executive agents or requires explicit dependency ordering.

| Agent | File | Posture | Tier | Effort | Exec Tier | Terminal | Trigger |
|-------|------|---------|------|--------|----------|---------|---------|
| **Executive Orchestrator** | `executive-orchestrator.agent.md` | full | Foundation | XL | Orchestrator | Y | Coordinate multi-workflow sessions spanning research, docs, scripting, and fleet changes — sequence executive agents and maintain session coherence |
| **Executive Planner** | `executive-planner.agent.md` | read-only | Foundation | L | Planner | N | Decompose complex multi-step requests into structured plans with phases, gates, agent assignments, and dependency ordering — before any execution |

---

## Fleet Management Agents

Maintain the health and standards compliance of the agent fleet itself.

| Agent | File | Posture | Tier | Effort | Exec Tier | Terminal | Trigger |
|-------|------|---------|------|--------|----------|---------|---------|
| **Executive Fleet** | `executive-fleet.agent.md` | full | Wave 1 | L | Fleet | Y | Manage the agent fleet — create, audit, update, and deprecate `.agent.md` files and fleet documentation |

---

## Project Management Agents

Maintain the health of the repository as an open-source resource.

| Agent | File | Posture | Tier | Effort | Exec Tier | Terminal | Trigger |
|-------|------|---------|------|--------|----------|---------|---------|
| **Executive PM** | `executive-pm.agent.md` | full | Wave 1 | M | PM | N | Maintain issues, labels, milestones, changelog, contributing docs, and community health files following open-source best practices |

---

## Product Research Agents

Conduct lightweight, asynchronous user research using GitHub-native data sources.

| Agent | File | Posture | Tier | Effort | Trigger |
|-------|------|---------|------|--------|----------|
| **User Researcher** | `user-researcher.agent.md` | read + create | Wave 2 | M | Synthesize closed issues, PRs, and Discussions into JTBD summaries and friction reports — invoked quarterly or after >20 closed issues |

---

## Workflow Agents

Cross-cutting agents used at the end of every workflow for quality gating and committing.

| Agent | File | Posture | Tier | Effort | Trigger |
|-------|------|---------|------|--------|----------|
| **Review** | `review.agent.md` | read-only | Foundation | S | Validate any changed files against AGENTS.md constraints before committing |
| **GitHub** | `github.agent.md` | terminal | Foundation | S | Commit approved changes to the current branch following Conventional Commits |

---

## Specialist Research Agents

Domain-specific research agents that extend the core research fleet with focused expertise areas.

| Agent | File | Posture | Trigger | Handoffs |
|-------|------|---------|---------|----------|
| **Security Researcher** | `security-researcher.agent.md` | read + create | Threat-model agentic workflows; identify OWASP attack surfaces; evaluate CIA-triad exposure in agent designs; produce security synthesis docs | Research Synthesizer, Research Reviewer, Executive Researcher, Executive Docs, Review |
| **Local Compute Scout** | `local-compute-scout.agent.md` | read + create | Survey Ollama / LM Studio / llama.cpp stacks; benchmark local models; document hardware prereqs; maintain a local model registry | Research Synthesizer, Executive Researcher, Executive Scripter, Review |
| **MCP Architect** | `mcp-architect.agent.md` | read + create | Design locally-distributed MCP topologies (stdio, HTTP/SSE); evaluate server composition patterns; define project MCP deployment conventions | Research Synthesizer, Executive Scripter, Local Compute Scout, Review, Executive Researcher |
| **Values Researcher** | `values-researcher.agent.md` | read + create | Research value encoding via speech act theory, deontic logic, and constitutional AI; evaluate MANIFESTO.md against encoding principles | Research Synthesizer, Executive Docs, Review, Executive Researcher |
| **A5 Context Architect** | `a5-context-architect.agent.md` | read + analyze | Evaluate AFS context layers, semantic memory isolation patterns, and scratchpad vs repo-memory tradeoffs; design context layering conventions; produce ADR draft | Research Reviewer, Executive Orchestrator, Executive Docs |

---

## Engineering & DevOps Agents

Operational agents for release coordination, environment validation, test coverage, and CI health.

| Agent | File | Posture | Trigger | Handoffs |
|-------|------|---------|---------|----------|
| **Release Manager** | `release-manager.agent.md` | full (no agent) | Orchestrate SemVer versioning, CHANGELOG entries, git tags, and GitHub Releases; milestone wrap-up | Review, GitHub, Executive PM, Executive Orchestrator |
| **Env Validator** | `env-validator.agent.md` | read-only | Read-only audit of `.python-version`, `uv.lock`, `pyproject.toml`, and CI matrix for consistency — advisory only | Executive Scripter, Executive Orchestrator |
| **B5 Dependency Auditor** | `b5-dependency-auditor.agent.md` | read-only | Audit `uv.lock` and `pyproject.toml` for CVEs, outdated packages, and version conflicts; output structured compatibility report | Executive Scripter, Security Researcher, Executive Orchestrator |
| **Test Coordinator** | `test-coordinator.agent.md` | read-only | Map pytest markers to CI phases; identify untested scripts; flag test anti-patterns — advisory only | Executive Scripter, Executive Orchestrator |
| **CI Monitor** | `ci-monitor.agent.md` | read + execute | Watch `gh run` history for failure patterns, flaky tests, and slow steps; categorise failures across CI failure modes; produce health report | Executive Scripter, Executive Automator, Executive Orchestrator |

---

## Community & Comms Agents

Agents that manage contributor relationships, developer relations, and community health signals.

| Agent | File | Posture | Trigger | Handoffs |
|-------|------|---------|---------|----------|
| **Issue Triage** | `issue-triage.agent.md` | read + execute | First-pass triage — suggest labels, priority, effort; flag duplicates; draft clarifying comments — advisory only, no close/merge authority | Executive PM, Executive Orchestrator |
| **DevRel Strategist** | `devrel-strategist.agent.md` | read + create | Plan blog cadence, tutorial pipeline, GitHub Discussions announcements, and DevEx narrative; 3-month content calendar; first-mile contributor experience audit | Executive Docs, Executive PM, Executive Orchestrator |
| **Community Pulse** | `community-pulse.agent.md` | read + execute | Aggregate GitHub health signals (stars, issue response time, PR velocity, contributor retention) via `gh api`; produce periodic health reports | Executive PM, DevRel Strategist, Executive Orchestrator |

---

## Knowledge & Governance Agents

Agents focused on cost governance, documentation quality enforcement, research queue management, and methodology compliance.

| Agent | File | Posture | Trigger | Handoffs |
|-------|------|---------|---------|----------|
| **LLM Cost Optimizer** | `llm-cost-optimizer.agent.md` | read + web | Build and maintain a model selection decision table (capability × cost × latency) per task type; track free/local tier options; recommend model tiers to reduce token spend | Executive Docs, Executive Orchestrator |
| **Docs Linter** | `docs-linter.agent.md` | read-only | Audit `docs/research/` for D4 heading gaps, dead source stubs, missing frontmatter, and `validate_synthesis.py` compliance — advisory only, never edits docs | Executive Docs, Review |
| **D5 Knowledge Base** | `d5-knowledge-base.agent.md` | read + edit | Manage `docs/research/OPEN_RESEARCH.md` as a living queue — retire completed items, prioritise next candidates, propose seed questions from synthesis gaps | Executive Researcher, Executive PM, Executive Orchestrator |
| **D4 Methodology Enforcer** | `d4-methodology-enforcer.agent.md` | read-only | Validate changes against MANIFESTO.md axioms — flag over-interactivity, token burn, and Programmatic-First violations; issue APPROVED / VIOLATIONS FOUND verdict | Executive Scripter, Executive Docs, Executive Orchestrator |

---

## Fleet Architecture

### Fleet Topology Quick-Reference

| Topology | Use Case | Isolation | Notes |
|----------|----------|-----------|-------|
| **Flat peer-to-peer** | Simple single-pass queries | Single window; no isolation | Lowest cost; no parallelism |
| **Hierarchical (orchestrator-workers)** | Complex research; parallel sub-question execution | Per-worker isolated windows; lead integrates | ~15× chat token cost; lead is sole integration point |
| **Evaluator-optimizer loop** | Iterative refinement; synthesis validation | Same or split windows; evaluation objective decoupled | Requires hard iteration ceiling; convergence not guaranteed |
| **Parallel research fleet** | Breadth-first research; independent sub-questions | Full per-agent isolation; no lateral communication | Token cost scales with N agents; 3–20 agents typical |
| **Hybrid (orchestrator + specialist sub-fleet)** | Production pipelines; multi-phase long-horizon tasks | Per-specialist isolation; shared external memory for plan state | Highest cost; justified by quality requirements |

Full topology comparison with context handoff mechanisms and source evidence: [`docs/research/agent-fleet-design-patterns.md §4`](../../docs/research/agent-fleet-design-patterns.md).

---

### Named Patterns

Eight patterns derived from production multi-agent systems research. Full treatment (Context / Forces / Solution / Consequences) in [`docs/research/agent-fleet-design-patterns.md §3`](../../docs/research/agent-fleet-design-patterns.md).

- **Pattern 1 — Orchestrator-Workers**: lead decomposes task; workers execute in isolation; lead synthesises
- **Pattern 2 — Evaluator-Optimizer Loop**: generator + evaluator in a bounded feedback cycle with explicit stopping conditions
- **Pattern 3 — Parallel Research Fleet**: N independent subagents on distinct sub-questions; condensed summaries returned to lead
- **Pattern 4 — Focus-Dispatch / Compression-Return**: outbound brief is minimal and scoped; inbound result targets 1,000–2,000 tokens regardless of exploration depth
- **Pattern 5 — Context-Isolated Sub-Fleet**: each subagent in its own context; no lateral communication; lead is sole integration point
- **Pattern 6 — Agent Card Discovery**: structured capability manifests enable dynamic fleet composition without hardcoded registries
- **Pattern 7 — Memory-Write-Before-Truncation**: agent writes plan state to external memory before context limit; restores coherence on reset
- **Pattern 8 — Specialist-by-Separation (Citation Gate)**: synthesis and attribution separated into sequential single-responsibility agents

---

### Specialist-vs-Extend Decision Tree

If **any** of the following apply, **CREATE** a new specialist agent: (1) different objective function from the existing agent, (2) context budget pressure (new capability consumes >20% of existing agent’s budget), (3) error isolation needed (failure must not contaminate existing output), (4) tool set incompatibility (new capability needs tools the existing agent must never hold).

If **all** of the following apply, **EXTEND** an existing agent: (1) same objective function, (2) >70% shared task logic, (3) always invoked together in fixed sequence, (4) combined agent stays within context budget.

When in doubt, prefer CREATE — isolation is easier to undo than entanglement. Full 9-criterion table: [`docs/guides/agents.md §Specialist-vs-Extend Heuristics`](../../docs/guides/agents.md).

---

## Adding a New Agent

1. Read [`.github/agents/AGENTS.md`](./AGENTS.md) for the frontmatter schema and naming conventions.
2. Run the scaffold script: `uv run python scripts/scaffold_agent.py --name "<Name>" --description "<desc>" --posture <posture>`.
3. Fill in the generated stub's TODO sections.
4. Add the agent to the correct table above.
5. Commit: `feat(agents): add <name> agent`.

---

## Supporting Scripts

Scripts that back agents in this fleet. All scripts support `--dry-run`.

| Script | Purpose |
|--------|---------|
| `scripts/scaffold_agent.py` | Scaffold a new `.agent.md` stub from a validated template |
| `scripts/prune_scratchpad.py` | Manage cross-agent scratchpad session files in `.tmp/` |
| `scripts/watch_scratchpad.py` | File watcher — auto-annotates `.tmp/*.md` on change |
