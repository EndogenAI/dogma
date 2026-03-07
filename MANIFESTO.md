# Endogenic Development Manifesto

> We are not vibe coding. We are pioneering **endogenic / agentic product design and development**.

> *"If I have seen further, it is by standing on the shoulders of giants."* — Attributed to Isaac Newton (and before him, many others)

---

## What Is Endogenic Development?

Endogenic development is the practice of building AI-assisted systems from the inside out — while **standing on the shoulders of giants**.

Rather than prompting an agent from zero context and hoping for the best — the "vibe coding" anti-pattern — endogenic development:

- **Encodes knowledge as DNA** 🧬: scripts, agent files, schemas, and seed documents that persist across sessions. Like DNA, this is both blueprint and inheritance — what the system reads to inform every action, and what it passes forward to future sessions.
- **Grows from a seed** 🌱: every new capability scaffolds from what the system already knows about itself *and* from the best of existing external practices. A seed contains everything needed to grow; it just needs the right environment.
- **Adds tree rings of knowledge** 🌳: each session accumulates in the substrate. The tree grows stronger with each year, each ring is visible in git history, and we can see by the density of the rings how much the system was tested.
- **Makes agents smarter over time**: each session adds to a corpus of encoded operational knowledge.
- **Reduces token burn**: context that is already encoded does not need to be re-discovered interactively.
- **Integrates external wisdom**: open-source tools, established frameworks, research literature, and prior art are all first-class inputs to the endogenous scaffold. We are not inventing in a vacuum — we are synthesizing.

The name comes from biology: an endogenous process is one that originates from within the organism. Like all living systems, our endogenic substrate is built from inherited knowledge (standing on giants' shoulders) and continuous synthesis of external wisdom (tools, frameworks, best practices). We grow from within, but we do not grow alone.

For a deeper exploration of these metaphors and how they guide all endogenous practice, see [`docs/guides/mental-models.md`](docs/guides/mental-models.md).

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

## Foundational Principle: Augmentive Partnership

Endogenic development is not about agent autonomy or reducing human involvement. It is about creating a **tight human-system partnership** where:

- The **human** provides direction, judgment, ethical guidance, and oversight
- The **system** provides deterministic execution, encoding, memory, and automation
- Neither works without the other — they form a unified cognitive system
- The goal is to **amplify human judgment**, not replace it

This partnership is why we encode knowledge, minimize token burn, and enforce governance. Every axiom and principle serves this partnership. The system grows smarter so the human can make better decisions — not to work autonomously.

---

## The Three Core Axioms

### 1. Endogenous-First

> Scaffold from existing system knowledge. Absorb and encode the best of what exists externally.

Endogenous-First is not isolationism. It is the principle that your system **grows from within by absorbing external knowledge into its DNA**.

Before writing any new agent, script, or document:
1. Read what the system already knows about itself (`AGENTS.md`, existing scripts, existing docs) — know your genetic makeup
2. Research relevant external tools, frameworks, and prior art — identify the giants to stand on
3. Extend or adapt rather than create from zero — prefer existing well-maintained libraries over bespoke implementations
4. Encode the synthesized knowledge back into the project so the next session starts richer — update your DNA with what you've learned

**The inheritance principle**: Just as DNA carries billions of years of evolutionary wisdom, your project carries the accumulated knowledge of its external sources. Every adopted tool, every synthesized best practice, every documented convention is genetic material that makes the system stronger. You stand on the shoulders of giants by encoding what they've built into your own substrate.

**Anti-pattern (isolationism)**: Refusing to adopt an existing open-source tool because "we should build it ourselves." If a well-maintained external tool solves a problem correctly, the DNA principle says: absorb it, document it, and encode its usage patterns into the project's scripts and agents.

**Anti-pattern (vibe coding)**: Dropping into Copilot Chat without reading `AGENTS.md` and asking the agent to "write a script to do X" — the agent will re-invent the wheel, miss project conventions, and burn tokens discovering what is already documented. You've forgotten your own genetic code.

### 2. Algorithms Before Tokens

> Prefer deterministic, encoded solutions over interactive token burn. Invest in automation early.

Every token spent in interactive sessions comes at a cost — computational, financial, and environmental. The core strategy is to move work upstream: encode algorithms, scripts, and decision trees that prevent re-discovery at session time.

This axiom drives:
- Preference for scripts over interactive prompts
- Caching and pre-computation over re-fetching
- Deterministic workflows over adaptive ones
- Context compression and isolation over broad context loads

See [`docs/guides/programmatic-first.md`](docs/guides/programmatic-first.md) for decision criteria and examples.

### 3. Local Compute-First

> Minimize token burn. Run locally whenever possible.

Cloud LLM inference is expensive — in tokens, money, and environmental cost. The endogenic approach prioritizes:
- Running models locally (Ollama, LM Studio, llama.cpp)
- Encoding context as scripts so it does not need to be re-derived in each session
- Using free/cheaper tiers where local compute is insufficient
- Caching and pre-computing context rather than re-discovering it interactively

When tight feedback loops between human and system are required, local models enable the augmentive partnership to function without delays.

---

## Guiding Principles (Cross-Cutting)

These principles reinforce the core axioms and guide all implementation decisions. Each principle serves one or more axioms — they are not hierarchical, but interconnected.

### Programmatic-First

**Reinforces**: Algorithms Before Tokens + Endogenous-First

> If you have done a task twice interactively, the third time is a script.

Any repeated or automatable task must be encoded as a committed script or automation before being performed a third time by hand. This is not optional — it is a constraint on the entire agent fleet.

**Why**: Interactive agent sessions are expensive (tokens, time, potential for error). Scripts are cheap, deterministic, and composable. Encoding knowledge as scripts is the primary mechanism by which the system grows its own intelligence and serves the human-system partnership.

### Documentation-First

**Reinforces**: All three axioms

> Every implementation change must be accompanied by clear documentation.

Documentation is not an afterthought — it is part of the change. A script without a docstring is incomplete. An agent without an `AGENTS.md` reference is incomplete. A feature without a guide is incomplete.

This principle exists because the documentation *is* the knowledge the system encodes for future agents. It reflects what humans have decided; it guides future human decisions.

### Adopt Over Author (Avoid Reinventing the Wheel)

**Reinforces**: Algorithms Before Tokens + Endogenous-First

> Use established open-source tools and frameworks when they solve a problem well. Do not rebuild what is already well-maintained externally.

When evaluating whether to build or adopt:
- Does the external tool solve the problem correctly? Adopt it.
- Does it have active maintenance and community support? Adopt it.
- Would building it ourselves consume tokens better spent elsewhere? Adopt it.

Adoption is not dependency — it is standing on shoulders of giants. Document the integrated tool, encode its usage patterns into scripts and agents, and let it become part of the endogenous substrate.

### Self-Governance & Guardrails

**Reinforces**: All three axioms

> Agents self-report deviations. Guardrails are validated programmatically, not just documented.

Governance happens at three levels:
1. **Documented conventions** in `AGENTS.md` and `MANIFESTO.md` (what agents should know before acting)
2. **Programmatic validation** via scripts that check compliance (what scripts ensure happens)
3. **Self-reporting by agents** when they detect deviations (what agents communicate back to humans)

Governor modules and enforcement scripts are part of the architecture, not afterthoughts. They close the gap between principle and practice, reducing token waste and preventing bad outputs from propagating downstream.

### Compress Context, Not Content

**Reinforces**: Algorithms Before Tokens + Local Compute-First

> Minimize the context window burden through lazy loading, selective compression, and caching. Every token in context should serve a purpose; remove irrelevant history, not knowledge.

Context engineering is critical for token efficiency and bounded inference costs (especially on local hardware). Techniques include:
- Lazy loading: load full agent bodies only when that agent is invoked
- Selective compression: summarize completed phases, retain decision rationale
- Caching: store pre-fetched sources, pre-computed vectors, and analysis results
- Isolation: strip irrelevant conversation history from agent prompts

**Empirical basis**: Live session practice confirmed that when agents skip writing to `.tmp/`, the next agent starts blind — scout outputs existed only in the conversation summary and had to be reconstructed at token cost. The scratchpad is the only durable cross-agent memory that survives a context window boundary. Write discipline — not queryability — is the primary gap in practised context management; the write-back requirement has since been mechanically encoded into agent files. See [`docs/research/sources/session-synthesis-2026-03-06-a.md`](docs/research/sources/session-synthesis-2026-03-06-a.md).

### Isolate Invocations, Parallelize Safely

**Reinforces**: Algorithms Before Tokens + Endogenous-First

> Per-invocation context isolation eliminates context rot. Parallelize only when isolation can be maintained. One source per synthesizer invocation; one task per agent run; independent operations in parallel.

When agents process large batches (e.g., multiple sources in a research synthesis), a single large invocation suffers "context rot" — early items degrade as the model processes later ones. Instead:
- Isolate each invocation to a single source/task
- Aggregate results afterward
- Parallelize independent invocations

This maintains fidelity across the entire batch and enables safe parallelization without context interference.

**Empirical basis**: Five independent orchestration traditions — Anthropic *Building Effective Agents*, ReAct (arXiv:2210.03629), AIGNE (arXiv:2512.05470), the Claude Agent SDK, and Claude Code Agent Teams — all independently enforce strict per-invocation scope isolation. The SDK states the invariant most precisely: *"the only channel from parent to subagent is the Task prompt string."* These teams did not coordinate their specifications; the convergence confirms that per-invocation isolation is a structural requirement for reliable multi-agent behaviour, not a stylistic preference. Confirmed empirically in this project: running a Synthesizer across 22 sources in a single invocation produced context rot; per-source isolation eliminated it. See [`docs/research/agentic-research-flows.md`](docs/research/agentic-research-flows.md).

### Validate & Gate, Always

**Reinforces**: Self-Governance & Guardrails + Algorithms Before Tokens

> Every phase has a gate. Every gate is checked before advancing. Evaluator-optimizer loops catch errors early. Early validation avoids wasted tokens and prevents bad outputs propagating downstream.

Gates are the mechanism by which the system enforces governance without heavyweight process. Examples include:
- Deliverables checklist before phase transition (research workflow)
- Review gate before commit (all changes)
- Completion criteria self-check before agent handoff

**Empirical basis**: Mei et al.'s context engineering survey (arXiv:2507.13334, 1400+ papers) documents a fundamental comprehension-generation asymmetry across LLMs — models understand complex context far better than they generate equivalently sophisticated long-form outputs. This gap is structural, not model-family-specific. The evaluator-optimizer loop is the architecturally correct response: structuring output generation as iterative evaluate-and-refine compensates for models' relative weakness at long-form generation and independently validates the self-loop phase gate design. See [`docs/research/sources/arxiv-context-engineering-survey.md`](docs/research/sources/arxiv-context-engineering-survey.md).

### Minimal Posture

**Reinforces**: Algorithms Before Tokens + Local Compute-First

> Every agent carries only the tools it needs. Every script only the dependencies it requires. Avoid over-provisioning — minimize surface area, maximize efficiency.

Minimal posture extends beyond agents to all design decisions:
- Tools: include only what an agent actually uses (no "just in case" tools)
- Dependencies: validate before adding; prefer well-maintained over feature-rich
- Context: load only what the task requires
- Handoff information: include enough for the next agent to succeed, nothing more

---

## Ethical Values

These values underpin all decisions and encode our commitment to responsible AI development. They are not aspirational — they are enforced through documentation, scripts, and governance.

- **Transparency**: All decisions are documented and traceable to a principle or axiom. No hidden heuristics or unexplained choices.
- **Human Oversight**: Agents operate under governance and gates. Humans make strategic decisions; the system executes and surfaces information for those decisions. No unconstrained autonomy.
- **Reproducibility**: Outputs are deterministic, reviewable, and auditable. A decision made on day one can be reproduced on day 100 with the same inputs.
- **Sustainability**: Minimize computational cost, environmental impact, and token burn. The finite cost of local inference is a feature, not a bug — it incentivizes efficient design.
- **Determinism**: Reduce randomness through encoding, scripts, and established practices. Vagueness is expensive; clarity is cheap.

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

### Not Autonomous Agents

Endogenic development rejects the goal of "autonomous agents." This is not a technical limitation — it is a deliberate design choice based on the Augmentive Partnership principle.

We build agents that:
- Operate under human oversight at every gate
- Escalate decisions that require human judgment
- Self-report when they detect deviations from guidance
- Amplify human capabilities, not replace them

The system grows smarter so humans can make better decisions *faster*, not so humans can stop making decisions.

---

## The Agent Fleet Philosophy

Agents in the endogenic model are:

- **Constrained by convention**: every agent reads `AGENTS.md` before acting, and every action traces to a documented rule or principle
- **Backed by scripts**: auditable, automatable actions are encoded as scripts — agents call scripts, they don't re-invent them
- **Hierarchical with gates**: executive agents orchestrate sub-agents; sub-agents escalate blockers back up; nothing proceeds without a completed gate
- **Minimal-posture**: every agent carries only the tools it needs for its stated role — no over-provisioning
- **Self-reporting & governed**: agents detect and report deviations from guidance; governor modules validate compliance; guardrails prevent propagation of bad outputs
- **Augmentive, not autonomous**: agents surface information and options for human decision-making; they do not make strategic choices
- **Commit before handoff**: changes are committed (via Review → GitHub) before control passes to the next agent

---

## The Growth Model: Tree Rings of Knowledge

A healthy endogenic project grows like this:

```
Session 1: Agent discovers how to do X interactively
Session 2: Agent does X again; notes it was done twice
Session 3: Agent scripts X before doing it a third time (programmatic-first)
Session N: Future agents start sessions with X already encoded as a script
```

Over time, the system accumulates a library of scripts, agents, and guides that represent the project's operational intelligence. Each session adds a tree ring — visible in git history, dense with the conditions that shaped it, and contributing to the overall strength of the system.

**Tree ring properties**:
- Each ring is a complete, datable layer (one session = one ring)
- The outer rings are always the newest, the core is the original seed
- Surface area increases with each ring (more capability, more agents, more capacity)
- You can read the tree's biography in the rings — which years were productive, which were challenging, which brought new growth
- The tree is only strong because of all its rings accumulated over time
- If you cut the tree now, the rings don't disappear — they're part of the structure forever

New sessions start richer. Token burn decreases. Determinism increases. This is the endogenic flywheel.

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
