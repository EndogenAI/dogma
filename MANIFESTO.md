# Endogenic Development Manifesto

> We are not vibe coding. We are pioneering **endogenic / agentic product design and development**.

> *"Learning never exhausts the mind."* — Leonardo da Vinci

---

## What Is Endogenic Development?

Endogenic development is the practice of building AI-assisted systems from the inside out — while **standing on the shoulders of giants**.

Rather than prompting an agent from zero context and hoping for the best — the "vibe coding" anti-pattern — endogenic development:

- **Encodes knowledge as artifacts**: scripts, agent files, schemas, and seed documents that persist across sessions
- **Grows from a seed**: every new capability scaffolds from what the system already knows about itself *and* from the best of existing external practices
- **Makes agents smarter over time**: each session adds to a corpus of encoded operational knowledge
- **Reduces token burn**: context that is already encoded does not need to be re-discovered interactively
- **Integrates external wisdom**: open-source tools, established frameworks, research literature, and prior art are all first-class inputs to the endogenous scaffold

The name comes from biology: an endogenous process is one that originates from within the organism. Endogenic development means the system grows its own intelligence from its own substrate — but it does not grow in a vacuum. Like da Vinci synthesizing anatomy, engineering, art, and natural philosophy into a unified practice, endogenic development absorbs the best of what exists and integrates it into a coherent, self-extending system.

### The Balance: Inside Out, Not Inside Only

Endogenic development is **not isolationism**. The distinction is:

| Vibe Coding | Endogenic Development |
|-------------|----------------------|
| No persistent context — re-discovers everything each session | Encodes context as committed artifacts |
| No conventions — each prompt is freeform | Governed by documented conventions agents read before acting |
| Ignores external best practices | Researches, synthesizes, and integrates external practices into the encoded substrate |
| Output is ephemeral | Output is committed, reviewed, and grows the system |
| Depends entirely on the LLM's prior training | Combines LLM capability with project-specific encoded knowledge |

The endogenic system *starts* from within (the morphogenetic seed) and *grows outward* by absorbing and encoding external knowledge. External tools, libraries, frameworks, and research are not excluded — they are **digested** into the codebase as documented, governed, first-class citizens.

---

## The Core Dogmas

### 1. Endogenous-First (with External Integration)

> Scaffold from existing system knowledge. Absorb and encode the best of what exists externally.

Before writing any new agent, script, or document:
1. Read what the system already knows about itself (`AGENTS.md`, existing scripts, existing docs)
2. Research relevant external tools, frameworks, and prior art
3. Extend or adapt rather than create from zero — prefer existing well-maintained libraries over bespoke implementations
4. Encode the synthesized knowledge back into the project so the next session starts richer

**The da Vinci principle**: Leonardo did not invent anatomy, optics, or engineering — he synthesized them into a unified practice more powerful than any single discipline. Endogenic development does the same: it absorbs external knowledge and integrates it into a self-consistent, growing system.

**Anti-pattern (isolationism)**: Refusing to adopt an existing open-source tool because "we should build it ourselves." If a well-maintained external tool solves a problem correctly, adopt it, document it, and encode its usage patterns into the project's scripts and agents.

**Anti-pattern (vibe coding)**: Dropping into Copilot Chat without reading `AGENTS.md` and asking the agent to "write a script to do X" — the agent will re-invent the wheel, miss project conventions, and burn tokens discovering what is already documented.

### 2. Programmatic-First

> If you have done a task twice interactively, the third time is a script.

Any repeated or automatable task must be encoded as a committed script or automation before being performed a third time by hand. This is not optional — it is a constraint on the entire agent fleet.

**Why**: Interactive agent sessions are expensive (tokens, time, potential for error). Scripts are cheap, deterministic, and composable. Encoding knowledge as scripts is the primary mechanism by which the system grows its own intelligence.

See [`docs/guides/programmatic-first.md`](docs/guides/programmatic-first.md) for decision criteria and examples.

### 3. Documentation-First

> Every implementation change must be accompanied by clear documentation.

Documentation is not an afterthought — it is part of the change. A script without a docstring is incomplete. An agent without an `AGENTS.md` reference is incomplete. A feature without a guide is incomplete.

This principle exists because the documentation *is* the knowledge the system encodes for future agents.

### 4. Local Compute First

> Minimize token burn. Run locally whenever possible.

Cloud LLM inference is expensive — in tokens, money, and environmental cost. The endogenic approach prioritizes:
- Running models locally (Ollama, LM Studio, llama.cpp)
- Encoding context as scripts so it does not need to be re-derived in each session
- Using free/cheaper tiers where local compute is insufficient
- Caching and pre-computing context rather than re-discovering it interactively

### 5. Commit Discipline

> Small, incremental commits. One logical change per commit.

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

| Type | When to use |
|------|-------------|
| `feat` | new functionality |
| `fix` | bug or correction |
| `docs` | documentation only |
| `chore` | tooling, config, scripts |
| `refactor` | restructuring without behavior change |

Good commit cadence: docs change → commit, script change → commit, agent change → commit. Never one giant commit at the end of a session.

---

## What We Are Not Doing

### Not Vibe Coding

Vibe coding is the practice of prompting an AI with a vague intention and accepting whatever it produces, iterating by feel until something works. It produces:
- Non-deterministic outcomes
- Undocumented decisions
- Token-hungry sessions that re-discover context every time
- Agents that hallucinate conventions that don't exist

Endogenic development is the opposite: every session starts from a rich, encoded knowledge base. The agent is constrained by documented conventions and backed by pre-computed scripts. The result is deterministic, reviewable, and grows smarter over time.

### Not Ignoring External Tooling

Endogenic development is emphatically **not** about rebuilding everything from scratch or ignoring the broader ecosystem. We:
- **Adopt** established open-source tools when they solve a problem well (e.g., `watchdog` for file watching, `uv` for Python environment management, `pre-commit` for hooks)
- **Research** existing methodologies and literature before designing new workflows
- **Synthesize** external best practices into the encoded substrate — they become part of the project's documented conventions and agents
- **Reference** external resources in documentation and agent files so future sessions can benefit from them

The goal is synthesis, not isolation.

### Not Prompt Engineering Alone

Prompt engineering — tuning the words you use to get better outputs — is a useful tactic but not a strategy. Endogenic development treats the prompt as the thin interface to a deep substrate of encoded knowledge. The value lives in the substrate, not the prompt.

### Not One-Shot Automation

Endogenic development is not "set it and forget it" automation. Agents operate under human oversight. The system grows iteratively. Every session is reviewed before it is committed. The agent fleet is governed by documented conventions, not by unconstrained autonomy.

---

## The Agent Fleet Philosophy

Agents in the endogenic model are:

- **Constrained by convention**: every agent reads `AGENTS.md` before acting, and every action traces to a documented rule
- **Backed by scripts**: auditable, automatable actions are encoded as scripts — agents call scripts, they don't re-invent them
- **Hierarchical**: executive agents orchestrate sub-agents; sub-agents escalate blockers back up; nothing proceeds without a checkpoint
- **Minimal-posture**: every agent carries only the tools it needs for its stated role — no over-provisioning
- **Commit before handoff**: changes are committed (via Review → GitHub) before control passes to the next agent

---

## The Growth Model

A healthy endogenic project grows like this:

```
Session 1: Agent discovers how to do X interactively
Session 2: Agent does X again; notes it was done twice
Session 3: Agent scripts X before doing it a third time (programmatic-first)
Session N: Future agents start sessions with X already encoded as a script
```

Over time, the system accumulates a library of scripts, agents, and guides that represent the project's operational intelligence. New sessions start richer. Token burn decreases. Determinism increases.

This is the endogenic flywheel.

---

## Open Questions and Research Directions

The endogenic methodology is young. Open research questions include:

- How do we optimally structure agent fleets for different project types?
- What is the right granularity for session scratchpad files?
- How do we distribute MCP frameworks across local network nodes?
- What are the best practices for running VS Code Copilot with local models?
- How do we handle async agent processes reliably?

See the [GitHub Issues](https://github.com/EndogenAI/Workflows/issues) for tracked research tasks.

---

*This manifesto is a living document. It should be updated as the methodology evolves. All changes must follow the documentation-first and commit-discipline dogmas.*
