# Working with Agents

A guide to authoring, using, and extending the VS Code Copilot agent fleet.

---

## What Are Agents?

Roles (`.agent.md` files — VS Code: Custom Agents) are reusable, governed AI personas that appear in the Copilot Chat dropdown. Each agent:

- Has a **defined scope and posture** (what it can do and what tools it can use)
- Reads **endogenous sources** before acting (project docs, existing scripts, session scratchpad)
- Follows **documented conventions** (AGENTS.md hierarchy)
- **Hands off** to downstream agents rather than overreaching its scope

Agents are not magic — they are documented, reviewable, constrained workers. The value is in the constraints and the encoded knowledge they read before acting.

---

## Using Agents

### In VS Code Copilot Chat

Invoke an agent by name in the chat input:

```
@Executive Scripter audit scripts/ for gaps
@Executive Automator set up a file watcher for docs/
```

### Session Start Ritual

1. Open the repo in VS Code
2. Open Copilot Chat
3. Start the scratchpad watcher: `uv run python scripts/watch_scratchpad.py`
4. Initialize today's session file: `uv run python scripts/prune_scratchpad.py --init`
5. Invoke the appropriate agent for your task

### Agent Selection Guide

| Task | Agent to invoke |
|------|----------------|
| Start a research session on any topic | **Executive Researcher** |
| Gather raw sources for a research topic | **Research Scout** |
| Synthesize research findings into a draft | **Research Synthesizer** |
| Review a research draft before archiving | **Research Reviewer** |
| Commit a finalised research doc | **Research Archivist** |
| Update or create documentation and guides | **Executive Docs** |
| Task you've done >2 times interactively | **Executive Scripter** |
| Need a file watcher, hook, or CI job | **Executive Automator** |
| Review changes before committing | **Review** |
| Commit and push approved changes | **GitHub** |
| Unsure which agent to use | Describe the task; ask Copilot Chat for a recommendation |

---

## Characters: Specialized Agents with Narrow Scope

A **Character** is a type of agent designed for narrow domain expertise with explicit decision authority and escalation protocols. Characters operate in a single domain and are designed to act autonomously within defined scope, while flagging decisions that require human oversight.

### Character vs. Broader Agents

| Aspect | Character | Broader Agent (Executive, Research, etc.) |
|--------|-----------|-------------------------------------------|
| **Scope** | Single domain (business, comms, engagement) | Orchestration or functional area |
| **Decision Authority** | Autonomous within scope; Conor flagging review | Orchestrates others; higher-level decisions |
| **Escalation** | Flags specific decisions for Conor approval | Delegates to specialists; handles meta-coordination |
| **Use Case** | Ongoing specialist function (e.g., "track consulting pipeline") | One-time orchestration or broad domains |
| **Examples** | Business Lead, Comms Strategist, Public Engagement | Executive Researcher, Executive Docs, Review |

### Current Characters (Month 1)

During the initial EndogenAI product discovery phase, three specialist Characters are being drafted:

1. **Business Lead Character** — Tracks consulting pipeline, synthesizes customer insights, informs pricing strategy, identifies revenue opportunities. Month 1: discovery/facilitation. Month 2+: autonomous pipeline management with Conor review loop.

2. **Comms Strategist Character** — Defines messaging framework, proposes content calendar, establishes brand voice, manages community messaging. Month 1: discovery/facilitation. Month 2+: autonomous content planning with Conor approval on major campaigns.

3. **Public Engagement Officer Character** — Facilitates GitHub community presence, monitors discussions, identifies speaker opportunities, co-hosts events. Month 1: community facilitation scope. Month 2+: expands to outreach + advocacy with Conor oversight.

### Invoking a Character

Characters are invoked the same way as any agent:

```
@Business Lead synthesize customer feedback from GitHub discussions into quarterly trends
@Comms Strategist draft messaging for the new init wizard launch
@Public Engagement Officer flag upcoming conferences for speaker submissions
```

---

## Agent Posture

Every agent operates at one of three postures:

| Posture | What it can do | Examples |
|---------|---------------|---------|
| **Read-only** | Read files, search codebase, audit | Review agents, plan agents |
| **Read + create** | Read + write new files | Scaffold agents |
| **Full execution** | Read + write + run commands + invoke other agents | Executive agents |

Agents should never carry more tools than their posture requires. If an agent is attempting something outside its posture, it should escalate rather than try to force it.

---

## Handoff Patterns

Every agent hands off to at least one downstream agent. The standard pattern:

```
Action agent → Review → GitHub (commit)
Executive → Sub-agent A → [Back to Executive] → Sub-agent B → Review → GitHub
```

The **takeback pattern** is recommended: each sub-agent returns control to the executive after completing its task, rather than chaining directly to the next sub-agent. This keeps the executive in oversight at every step.

---

## Linking Agents to Project Governance

**Every agent should encode a reference to the GitHub issue it implements or the milestone it belongs to.** This creates an audit trail and ensures agent behavior stays aligned with project decisions.

### In Frontmatter (Optional but Recommended)

```yaml
---
name: Executive PM
tier: Wave 1                    # Milestone this agent targets
effort: M                       # Effort estimate to implement
status: active                  # active | beta | deprecated | blocked
area: agents                    # Codebase domain
---
```

### In Endogenous Sources (Required)

Always include:

```markdown
## Endogenous Sources

This agent is defined by:
- **Issue**: #62 (Implement Remaining Agent Skills) — use the issue number and title
- **Milestone**: Wave 1: Agent Fleet Tier A+B
- **Labels**: type:feature, priority:high, area:agents
- **Acceptance criteria**: see the linked issue for completeness definition

[Read `AGENTS.md` before modifying this agent](../../AGENTS.md)
```

**Why**: This encoding ensures developers know:
1. Why the agent exists (the defining issue)
2. What milestone phase it belongs to (planning visibility)
3. What acceptance criteria define "done" (issue checklist)
4. How to update the agent if requirements change (reference loop back to issue)

---

## Authoring a New Agent

Before creating a new agent:

1. Check [`.github/agents/README.md`](../../.github/agents/README.md) — does an existing agent cover the need?
2. Determine if you're authoring a **Character** (narrow scope, single domain, autonomous operations) or a broader **Role** (orchestration, broader functional area)
3. Create or reference the GitHub issue that defines this agent's scope
4. Read [`.github/agents/AGENTS.md`](../../.github/agents/AGENTS.md) for the frontmatter schema, Character designation, and conventions
5. Choose the minimum posture that fulfils the agent's role
6. Follow the body structure: role statement → endogenous sources → workflow → guardrails

### Authoring a Character

If you're authoring a **Character**:

- **Scope statement**: Open with a clear one-sentence scope statement (a single domain)
- **Month 1 constraints**: If new, specify Month 1 constraints (discovery/facilitation, what requires human approval)
- **Escalation protocol**: Explicitly define which decisions are autonomous and which are flagged for Conor review
- **Endogenous sources**: Reference the GitHub issue defining the Character, the strategic roadmap (if applicable), and product discovery docs
- **Autonomy signals**: Document in Endogenous Sources what metrics or events trigger scope expansion in future months

**Example Character opening**:

```markdown
You are the **Business Lead Character** for the EndogenAI ecosystem.
Your role is to synthesize customer insights, track the consulting pipeline, 
and inform pricing strategy and revenue opportunities.

## Month 1 Scope

- Autonomous: Pipeline tracking via weekly spreadsheet reviews, customer inquiry synthesis
- Flag for review: Any customer feedback influencing product positioning, pricing changes, 
  new service offerings
- Escalate to Conor: Contracts >$25K, partnerships, strategic partnerships
```

---

```yaml
---
name: My Agent
description: One sentence ≤ 200 characters describing what this agent does.
tools:
  - search
  - read
handoffs:
  - label: Back to Executive
    agent: Executive Name
    prompt: "Task complete. Here is a summary: ..."
    send: false
---

You are the **My Agent** for the EndogenAI Workflows project.

## Endogenous Sources — Read Before Acting

1. [`AGENTS.md`](../../AGENTS.md)
2. (any other files this agent must read first)

## Workflow

1. Step one
2. Step two

## Guardrails

- Never do X
- Escalate to Y if Z
```

---

## Agent Skills

Skills are `SKILL.md` files stored in `.github/skills/<skill-name>/` and discovered automatically by GitHub Copilot. Only the `name` and `description` frontmatter (~100 tokens per skill) is loaded at startup; the full skill body loads only when a request matches its description. Skills sit at the tactical layer of the VS Code customization stack, beneath `.agent.md` files and above session behaviour.

**For detailed skill authoring guidance**, see the [`skill-authoring` skill](../../.github/skills/skill-authoring/SKILL.md) — it parallels agent-file-authoring but documents the skill-specific YAML frontmatter (tier, type, effort, applies-to), relative path conventions (../../../ for skills vs ../../ for agents), and issue linkage patterns.

For the full decision record, see [`docs/decisions/ADR-006-agent-skills-adoption.md`](../../docs/decisions/ADR-006-agent-skills-adoption.md).

### Skills vs Agents — Composition Rule

**Agents encode *who does a task***; **skills encode *how a task is done***.

| Primitive | Encodes | When to use |
|-----------|---------|-------------|
| `.agent.md` | Persona, posture, tool restrictions, handoff graph | Unique posture, handoff logic, or tool restriction is required |
| `SKILL.md` | Workflow procedures, conventions, templates | The procedure is needed by more than one agent or AI tool |

**Extraction test**: if a procedure in an agent body would benefit a *different* agent or AI tool without requiring that agent's posture or tool restrictions, it belongs in a skill. Do not extract a procedure until the agent body has been updated to reference the new skill.

### File Structure

```
.github/skills/
  <skill-name>/
    SKILL.md          ← required
    scripts/          ← optional: helper scripts referenced by the skill
    examples/         ← optional: worked examples
```

The directory name must exactly match the `name` field in the frontmatter.

### Frontmatter Fields

**Required:**

| Field | Constraint |
|-------|------------|
| `name` | Lowercase, hyphens only, max 64 chars; must match parent directory name |
| `description` | Max 1024 chars; drives auto-loading — be precise |

**Optional (VS Code Copilot only; degrade gracefully on other agents):**

| Field | Use |
|-------|-----|
| `argument-hint` | Hints for the argument the skill accepts |
| `user-invocable` | `true` to allow direct user invocation via `/skill-name` |
| `disable-model-invocation` | `true` to prevent automatic loading; user must invoke explicitly |

### Encoding Inheritance and AGENTS.md Requirement

Skills extend the encoding inheritance chain to six layers (subdirectory `AGENTS.md` files are the fourth tier):

```
MANIFESTO.md              ← foundational axioms
AGENTS.md (root)          ← operational constraints
AGENTS.md (subdirectory)  ← narrowing constraints (docs/, .github/agents/)
.agent.md files           ← Roles (VS Code: Custom Agents)
SKILL.md files            ← reusable tactical knowledge
session behaviour         ← enacted output
```

Every `SKILL.md` body **must reference [`AGENTS.md`](../../AGENTS.md) as its governing constraint**. This anchors skills to the encoding inheritance chain and makes fidelity auditable via CI. The governing axiom citation must appear in the first substantive section of the body.

### Existing Skills

| Skill | Description |
|-------|-------------|
| [`session-management`](../../.github/skills/session-management/SKILL.md) | Full session lifecycle: scratchpad init/close, encoding checkpoints, session-start/end procedure |
| [`deep-research-sprint`](../../.github/skills/deep-research-sprint/SKILL.md) | Research sprint orchestration: Scout → Synthesizer → Reviewer → Archivist pipeline |
| [`conventional-commit`](../../.github/skills/conventional-commit/SKILL.md) | Conventional Commits format + endogenic commit discipline for this repository |

### CI Validation

Run before committing any `.github/skills/` change:

```bash
uv run python scripts/validate_agent_files.py --skills
# or validate everything at once:
uv run python scripts/validate_agent_files.py --all
```

CI enforces this check on every PR that touches `.github/skills/`.

---

## The Endogenous Sources Requirement

Every agent must list the files it reads **before acting**. This is not boilerplate — it is the mechanism by which the agent fleet bootstraps from encoded knowledge rather than from zero context.

Typical sources:
- Root `AGENTS.md` — guiding constraints
- `scripts/README.md` — what scripts already exist (check before creating new ones)
- Relevant `docs/guides/` — established best practices
- Active session scratchpad — context from the current session

---

## Escalation and Insufficient Posture

When a sub-agent cannot complete a task (posture limit, context too large, specialist knowledge needed), it must **not fail silently**. It must:

1. Write a structured escalation note to the session scratchpad:
   ```markdown
   ## <AgentName> Escalation
   - **Current state**: ...
   - **Blocking issue**: ...
   - **Recommended action**: ...
   ```
2. Use the "Back to [Executive]" handoff to return control

The executive reads the escalation note, decides what to do next (re-delegate, create a new specialist agent, or handle directly), and proceeds.

---

## Agent Hierarchy and Task Ownership

The fleet is organised into four functional areas. Each executive owns a vertical slice of work
and orchestrates its sub-agents. Cross-cutting workflow agents (Review, GitHub) serve all areas.

```
┌─────────────────────────────────────────────────────────┐
│                   Human / User                          │
└──────────────┬────────────────────────┬─────────────────┘
               │                        │
   ┌───────────▼──────────┐  ┌──────────▼──────────────┐
   │  Executive Researcher│  │    Executive Docs        │
   └───────────┬──────────┘  └──────────┬──────────────┘
               │                        │
   ┌───────────▼──────────┐             │
   │  Research Scout      │             │
   │  Research Synthesizer│             │
   │  Research Reviewer   │             │
   │  Research Archivist  │             │
   └───────────┬──────────┘             │
               │                        │
   ┌───────────▼────────────────────────▼─────┐
   │  Executive Scripter / Executive Automator │
   └───────────────────────┬───────────────────┘
                           │
              ┌────────────▼─────────────┐
              │  Review  →  GitHub       │
              └──────────────────────────┘
```

### Task Ownership by Workflow Stage

| Workflow stage | Owned by | Escalates to |
|----------------|----------|--------------|
| Research question framing | Executive Researcher | Human |
| Source gathering | Research Scout | Executive Researcher |
| Synthesis drafting | Research Synthesizer | Executive Researcher |
| Draft validation | Research Reviewer | Executive Researcher |
| Final commit of research | Research Archivist | Review → GitHub |
| Guide and docs updates | Executive Docs | Review → GitHub |
| Script authoring | Executive Scripter | Review → GitHub |
| Automation design | Executive Automator | Review → GitHub |
| Pre-commit quality gate | Review | Originating agent |
| Commit and push | GitHub | — |

---

## Fleet Governance

The agent fleet is governed by the `AGENTS.md` hierarchy:

```
AGENTS.md (root)           — global constraints for all agents
  docs/AGENTS.md           — documentation work constraints
  .github/agents/AGENTS.md — agent authoring constraints
```

Any change to an existing agent should be reviewed by a peer before committing. Any new agent should be added to [`.github/agents/README.md`](../../.github/agents/README.md).

---

## Fleet Design Patterns

Eight patterns distilled from production multi-agent systems research. For the full academic treatment (Context / Forces / Solution / Consequences / Evidence), see [`docs/research/agent-fleet-design-patterns.md`](../../docs/research/agent-fleet-design-patterns.md).

### Pattern 1 — Orchestrator-Workers
**When to use**: A complex task that must be decomposed into parallel or sequentially dependent subtasks, each requiring different research or execution capabilities.
**Mechanism**: A lead orchestrator decomposes the problem and dispatches narrow task briefs to workers. Workers do not synthesise cross-task findings — the lead does. Worker context is discarded after completion, keeping the lead’s integration context clean.
**Trade-offs**: Parallel execution and focused worker context improve quality, but token cost scales with fleet size (~15× chat baseline) and the lead becomes a bottleneck if workers fail silently.

### Pattern 2 — Evaluator-Optimizer Loop
**When to use**: A generation task where iterative refinement demonstrably improves output and explicit quality criteria can be stated in advance.
**Mechanism**: Separate generation and evaluation into two distinct agents or passes. The generator produces output; the evaluator scores it against criteria and returns structured feedback; the generator revises. The loop exits when criteria are met or a maximum iteration count is reached.
**Trade-offs**: Quality improves each iteration but token cost is unbounded without a hard iteration ceiling — stopping conditions are mandatory.

### Pattern 3 — Parallel Research Fleet
**When to use**: A breadth-first question that decomposes into N distinct, independent sub-questions each resolvable by a standalone search-and-summarise agent.
**Mechanism**: The lead enumerates sub-questions, spawns N subagents in parallel with distinct search briefs, and receives only condensed 1,000–2,000 token summaries — not raw search outputs. Anthropic’s production system uses 3–5 agents for standard queries, up to 10+ for complex, hard-capped at 20.
**Trade-offs**: Wall-clock time is bounded by the slowest subagent, but vague sub-question briefs produce duplicated or circular searches.

### Pattern 4 — Focus-Dispatch / Compression-Return
**When to use**: Any delegation boundary where context must cross between agent windows in either direction.
**Mechanism**: Outbound (lead→subagent): compress the problem into the minimum necessary task brief. Inbound (subagent→lead): the subagent compresses its full exploration into a dense result summary targeting 1,000–2,000 tokens regardless of exploration depth. Design the result format explicitly (key findings, source references, confidence flags).
**Trade-offs**: Lead context grows with breadth (fleet size), not depth (per-subagent exploration), but aggressive compression risks losing nuanced findings — maximise recall first, then iterate for precision.

### Pattern 5 — Context-Isolated Sub-Fleet
**When to use**: A multi-agent fleet where more than one subagent executes simultaneously and correctness requires no inter-agent interference.
**Mechanism**: Each subagent operates in its own context window, receives only a task-specific brief, writes large artifacts to external storage, and returns lightweight references to the lead. Subagents do not communicate laterally — the lead is the sole integration point. Shared behavioural substrate comes from loaded agent instructions (e.g., `AGENTS.md`), not shared runtime state.
**Trade-offs**: Non-interference by construction, but write concurrency on shared files is an open problem — enforce file-level ownership boundaries.

### Pattern 6 — Agent Card Discovery
**When to use**: A growing fleet that requires new specialist agents to be composed dynamically without a hardcoded central registry.
**Mechanism**: Each agent publishes a structured capability manifest (an Agent Card at `/.well-known/agent-card.json` for network agents, or agent frontmatter for local fleets). An orchestrator bootstraps discovery by matching skill tags and media types to the current task. `scripts/generate_agent_manifest.py` generates the EndogenAI equivalent.
**Trade-offs**: Fleet can grow without modifying the orchestrator, but discovery is static — no real-time availability signals; skill versioning is absent from A2A v1.0.

### Pattern 7 — Memory-Write-Before-Truncation
**When to use**: A long-horizon task where the agent’s context window may be exhausted before completion and plan state must survive context resets.
**Mechanism**: Before the context window limit is reached, the agent writes its plan, key decisions, and unresolved open questions to external memory (`.tmp/` scratchpad, notes file, or structured store). After reset, reading this state is the first action. Trigger at a token threshold (200K tokens in Anthropic’s production system), at phase boundaries, or before any risky action.
**Trade-offs**: Plan coherence survives resets and memory writes create an audit trail, but over-conservative compression loses subtle context and memory stores accumulate stale state without pruning.

### Pattern 8 — Specialist-by-Separation (Citation Gate)
**When to use**: A pipeline whose output must meet both content quality criteria (accurate prose) and attribution quality criteria (correctly sourced claims).
**Mechanism**: Separate synthesis and citation into sequential single-responsibility agents. The synthesis agent produces uncited prose; a downstream citations agent adds citations at semantic-unit boundaries with hard constraints against text modification and fabrication. The citations agent validates its output against source texts.
**Trade-offs**: Both synthesis and citation quality improve, but the citations agent requires access to all source documents, which may be a context or access challenge.

---

## Specialist-vs-Extend Heuristics

When you need a new capability, decide whether to create a new agent or extend an existing one.

| Criterion | Signal | Decision |
|-----------|--------|----------|
| **Objective function conflict** | New behaviour requires a different primary goal from the existing agent | **CREATE** |
| **Context budget conflict** | New capability would consume >20% of the existing agent’s context budget | **CREATE** |
| **Single-responsibility preservation** | Existing agent handles one cohesive task; new capability is adjacent but not equivalent | **CREATE** downstream specialist |
| **Error blast-radius** | A failure in the new capability should not contaminate the existing agent’s output | **CREATE**; isolation limits blast-radius |
| **Tool set incompatibility** | New capability requires tools the existing agent must never use | **CREATE**; minimal-posture constraint |
| **Cross-fleet reusability** | New capability is useful independently of any existing agent | **CREATE** composable specialist |
| **Cognitive load** | Adding the capability requires the agent to disambiguate between two competing modes | **CREATE**; ambiguous decision points cause tool-selection failures |
| **Reuse of core task logic** | New behaviour shares >70% of operational steps with an existing agent | **EXTEND** via conditional fork |
| **Frequency of co-invocation** | New capability is always used together with the existing agent in fixed sequence | **EXTEND** if combined agent stays within context budget; **CREATE** otherwise |

**Decision tree**: If any of these apply, CREATE: (1) different objective function, (2) context budget pressure, (3) error isolation needed, (4) tool set incompatibility. If all of these apply, EXTEND: (1) same objective function, (2) >70% shared task logic, (3) always invoked together, (4) combined agent stays within context budget.
