---
governs: [endogenous-first, algorithms-before-tokens, local-compute-first, minimal-posture, programmatic-first, documentation-first]
---

# Endogenic Development Manifesto

> We are not vibe coding. We are pioneering **Endogenic Development Methodology** — a complete design framework for AI-assisted systems.

> *"If I have seen further, it is by standing on the shoulders of giants."* — Attributed to Isaac Newton (and before him, many others)

---

## What Is Endogenic Development?

Endogenic Development is a methodology for building AI-assisted systems — agents, scripts, documentation, and knowledge infrastructure — from the inside out, while **standing on the shoulders of giants**.

Rather than building each capability in isolation and hoping an AI agent will figure out your conventions — the "vibe coding" anti-pattern — Endogenic Development:

- **Encodes knowledge as DNA** 🧬: scripts, agent files, schemas, and seed documents that persist across sessions. Like DNA, this is both blueprint and inheritance — what the system reads to inform every action, and what it passes forward to future sessions.
- **Grows from a seed** 🌱: every new capability scaffolds from what the system already knows about itself *and* from the best of existing external practices. A seed contains everything needed to grow; it just needs the right environment.
- **Adds tree rings of knowledge** 🌳: each session accumulates in the substrate. The tree grows stronger with each year, each ring is visible in git history, and we can see by the density of the rings how much the system was tested.
- **Makes agents smarter over time**: each session adds to a corpus of encoded operational knowledge.
- **Reduces token burn**: context that is already encoded does not need to be re-discovered interactively.
- **Integrates external wisdom**: open-source tools, established frameworks, research literature, and prior art are all first-class inputs to the endogenous scaffold. We are not inventing in a vacuum — we are synthesizing.

The name comes from biology: an endogenous process is one that originates from within the organism. Like all living systems, our endogenic substrate is built from inherited knowledge (standing on giants' shoulders) and continuous synthesis of external wisdom (tools, frameworks, best practices). We grow from within, but we do not grow alone.

**Intellectual heritage**: Endogenic Development Methodology synthesizes several established traditions: Engelbart's augmentation framework (1962) supplies the Augmentive Partnership principle; Turing's morphogenesis (1952) and Maturana & Varela's autopoiesis (1972) supply the biological substrate metaphors; Knuth's literate programming (1984) and Martraire's living documentation (2019) supply the encode-once-reuse-many strategy; and Alexander's Pattern Language (1977) supplies the interconnected-principles architecture. The endogenic contribution is the synthesis of these traditions specifically for AI-assisted development across all domains, where LLM agents, scripts, and automation re-read the encoded substrate to orient each new session. See [`docs/research/methodology-review.md`](docs/research/methodology-review.md) for the full prior art survey.

For a deeper exploration of these metaphors and how they guide all endogenous practice, see [`docs/guides/mental-models.md`](docs/guides/mental-models.md). To see how these principles apply in a concrete organizational context — with Custom Agents as Roles and SKILL.md files as reusable Techniques — read the restaurant analogy in that same guide.

### The Balance: Inside Out, Not Inside Only

Endogenic development is **not isolationism**. The distinction is:

| Vibe Coding | Endogenic Development |
|-------------|----------------------|
| No persistent context — re-discovers everything each session | Encodes context as committed artifacts |
| No conventions — each prompt is freeform | Governed by documented conventions read before acting |
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

This principle is a direct descendant of Douglas Engelbart's augmentation framework ("Augmenting Human Intellect", 1962), updated for the LLM context. Engelbart's NLS required continuous human steering at every step; the endogenic fleet enforces this through phase gates and review checkpoints rather than through UI design.

This partnership is why we encode knowledge, minimize token burn, and enforce governance. Every axiom and principle serves this partnership. The system grows smarter so the human can make better decisions — not to work autonomously.

---

## How to Read This Document

This document is a **constitution**, not a guidebook — it defines what kind of system we are, not just how to act. Apply it accordingly.

**Axiom priority order**: The three core axioms are ordered by priority. When they appear to conflict, resolve as follows:
1. **Endogenous-First** supersedes all other axioms — read the system's own encoded knowledge before taking any action.
2. **Algorithms Before Tokens** supersedes Local Compute-First — prefer a deterministic encoded solution over an interactive session, even when a local model is available.
3. **Local Compute-First** governs compute residency decisions: prefer local execution for all enforcement, validation, and inference operations. *(Position 3 reflects conflict-resolution priority — when EF, ABT, and LCF appear to conflict, EF and ABT dominate. Structurally, LCF functions as an enabling substrate that keeps the enforcement and oversight mechanisms of Axioms 1 and 2 locally resident and operationally available. LCF is always active as a substrate property — not a fallback activated after the first two axioms are exhausted. See [`MANIFESTO.md §3`](#3-local-compute-first) and [`lcf-axiom-positioning.md`](docs/research/lcf-axiom-positioning.md).)*

**Guiding Principles are not hierarchical** — they reinforce and constrain the axioms together. When principles appear to conflict, derive behavior from the axioms (which are more fundamental) rather than from the principles alone.

**Novel situations**: When faced with a situation not explicitly covered, ask: *"What does a system that is Endogenous-First, Algorithms Before Tokens, and Local Compute-First do here?"* — derive from axioms, not from analogy.

**Anti-patterns are canonical veto rules**: If a proposed action matches a stated anti-pattern, reject it — regardless of whether a cross-cutting principle appears to permit it. Anti-patterns are the most resilient encoding form; they survive paraphrasing and drift.

**Encoding hierarchy**: MANIFESTO.md → AGENTS.md → agent files → SKILL.md files → session prompts. Each layer is a re-encoding of the layer above. When layers appear to conflict, the higher layer governs. When an AGENTS.md is silent on a topic, derive behavior from MANIFESTO.md.

For the evidence base underpinning this hermeneutical frame, see [`docs/research/values-encoding.md`](docs/research/values-encoding.md).

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

This inheritance principle has a precise biological grounding in Maturana and Varela's autopoiesis (1972): a system is autopoietic if it produces and maintains its own components. An endogenic project is autopoietic — each session produces scripts, guides, and agent files that maintain the substrate, so future sessions start richer than the ones that preceded them.

**Canonical example**: A session begins with the agent reading `AGENTS.md`, the active scratchpad (`.tmp/<branch>/<date>.md`), and the open research plan before taking any action — the agent knows the project's conventions, what prior work exists, and the current phase's scope without burning a single interactive token on discovery. Contrast with a session that opens directly in Copilot Chat asking "write me a script to do X" — the agent re-invents conventions already in `scripts/`, misses project patterns already encoded, and produces output that contradicts or duplicates what the system already knows. The before/after delta is not capability: it is the difference between reading your DNA before acting versus pretending it doesn't exist.

**Anti-pattern (isolationism)**: Refusing to adopt an existing open-source tool because "we should build it ourselves." If a well-maintained external tool solves a problem correctly, the DNA principle says: absorb it, document it, and encode its usage patterns into the project's scripts and agents.

**Anti-pattern (vibe coding)**: Dropping into Copilot Chat without reading `AGENTS.md` and asking the agent to "write a script to do X" — the agent will re-invent the wheel, miss project conventions, and burn tokens discovering what is already documented. You've forgotten your own genetic code.

**Programmatic gate**: `uv run python scripts/fetch_all_sources.py` — run at the start of every research session to batch-populate the local source cache from all committed URLs. This is the primary machinery of the "read-before-act" posture: the system reads what it already knows before any agent fetches anything. `scripts/generate_agent_manifest.py` keeps the agent inventory discoverable without runtime rediscovery. Together these scripts are the morphogenetic gatekeepers of the principle.

### 2. Algorithms Before Tokens

> Prefer deterministic, encoded solutions over interactive token burn. Invest in automation early.

Every token spent in interactive sessions comes at a cost — computational, financial, and environmental. The core strategy is to move work upstream: encode algorithms, scripts, and decision trees that prevent re-discovery at session time.

This axiom drives:
- Preference for scripts over interactive prompts
- Caching and pre-computation over re-fetching
- Deterministic workflows over adaptive ones
- Context compression and isolation over broad context loads

See [`docs/guides/programmatic-first.md`](docs/guides/programmatic-first.md) for decision criteria and examples.

**Canonical example**: `scripts/watch_scratchpad.py` — rather than asking an agent to annotate scratchpad headings with line numbers after every write (interactive token burn), a file watcher does this automatically with zero tokens. First-time cost: one scripting session. Per-session saving: hundreds of tokens across every scratchpad write, every day.

**Anti-pattern**: Using Copilot Chat to look up `gh` CLI syntax repeatedly instead of reading `docs/toolchain/gh.md` — burning tokens to re-discover information that is already deterministically encoded. "Let me ask the agent" when the answer is in a committed file is the canonical ABT violation. The same applies to re-running interactive research that `scripts/fetch_all_sources.py` could have pre-computed.

**Programmatic gate**: The decision table in `AGENTS.md#programmatic-first-principle` is the behavioral gate ("check `scripts/` first"). Pre-commit hooks (`ruff`, `uv sync`) and `scripts/prune_scratchpad.py` ensure session artifacts are compressed and committed, preventing context re-discovery next session. The CI test suite is the terminal gate: every committed script must have automated tests — the tests are the deterministic record of what the algorithm does.

### 3. Local Compute-First

> Minimize token burn. Run locally whenever possible.

Cloud LLM inference is expensive — in tokens, money, and environmental cost. The endogenic approach prioritizes:
- Running models locally (Ollama, LM Studio, llama.cpp)
- Encoding context as scripts so it does not need to be re-derived in each session
- Using free/cheaper tiers where local compute is insufficient
- Caching and pre-computing context rather than re-discovering it interactively

When tight feedback loops between human and system are required, local models enable the augmentive partnership to function without delays.

Local compute is not merely a cost tier — it is oversight infrastructure. Keeping enforcement scripts, validators, and inference co-located with the development substrate maintains enforcement proximity (governance mechanisms operate at the point of action), enables tight-loop human oversight, and preserves optionality against external-dependency lock-in. The cost benefit of local compute is a *consequence* of these structural properties, not the reason for them. When choosing between local and cloud execution, apply the structural test first: does cloud residency transfer enforcement authority, oversight access, or governance guarantees to an external party? If yes, local is preferred regardless of cost.

LCF is the structural foundation that keeps the operational expressions of all other axioms — Endogenous-First knowledge retrieval, Algorithms Before Tokens enforcement gates, Minimal Posture sandboxing, and Documentation-First quality validators — locally resident and available. Deprioritizing local compute does not merely increase cost; it degrades the structural substrate on which the entire governance architecture depends. LCF does not stand alone — it is the operational substrate that gives the other two axioms their local residency and thus their reliability. See [`docs/research/lcf-oversight-infrastructure.md`](docs/research/lcf-oversight-infrastructure.md) for the full axiom-enablement-cascade analysis and [`docs/research/lcf-axiom-positioning.md`](docs/research/lcf-axiom-positioning.md) for the axiom-positioning synthesis.

**Canonical example**: Running `ollama pull llama3.2:3b` for interactive annotation tasks — batch classification of research sources, draft section summaries, or quick schema validation queries that do not require frontier model capability. At $0 per inference versus $0.01–$0.15 per cloud API call, 1,000 such calls per month saves $10–$150/month while keeping the feedback loop local and fast.

**Anti-pattern**: Using a cloud frontier model to run a simple transformation because "it's faster to prompt than to script" — this simultaneously violates Local Compute-First (cloud inference was used) and Algorithms Before Tokens (it should have been a script). The double-axiom violation is the canonical signal: when two axioms converge on the same objection, the anti-pattern is unambiguous.

**Programmatic gate**: `docs/guides/local-compute.md` encodes the model selection decision tree. The `LLM Cost Optimizer` agent maintains the live model-tier table and surfaces cloud-model usage for tasks within local-model capability. Cloud-model usage detection splits across two enforcement surfaces with different tractability: *semantic intent* (was cloud chosen despite a viable local alternative?) requires operator-context no static linter can evaluate — the human-judgment gate via `docs/guides/local-compute.md` remains the correct tier-1 arbiter here, and the absence of a FAIL-blocking CI gate for this surface is intentional. *Observable proxies* (hardcoded cloud API endpoint strings, direct SDK imports such as `import openai`, YAML/TOML cloud-model name declarations) are statically tractable and are candidates for a WARN-only tier-0 gate (`scripts/check_model_usage.py`); this gate should stay in WARN mode until issue #131 (local compute baseline) produces usage telemetry to calibrate signal quality, after which a FAIL-blocking upgrade can be assessed.

---

## Guiding Principles (Cross-Cutting)

These principles reinforce the core axioms and guide all implementation decisions. Each principle serves one or more axioms — they are not hierarchical, but interconnected.

### Programmatic-First

**Reinforces**: Algorithms Before Tokens + Endogenous-First

> If you have done a task twice interactively, the third time is a script.

Any repeated or automatable task must be encoded as a committed script or automation before being performed a third time by hand. This is not optional — it is a constraint on the entire agent fleet.

**Why**: Interactive agent sessions are expensive (tokens, time, potential for error). Scripts are cheap, deterministic, and composable. Encoding knowledge as scripts is the primary mechanism by which the system grows its own intelligence and serves the human-system partnership.

**Canonical example**: `scripts/format_citations.py` — citation metadata extraction was run interactively in the first two research sessions, then encoded as a committed script on the third occurrence. Every subsequent session runs the script with zero tokens spent on the task. The script *is* the encoded knowledge; the interactive sessions that preceded it were its specification.

**Anti-pattern**: Running `gh issue list` or grepping through files manually in each session to check open issues and conventions, instead of encoding that check into a script. The information is re-discovered at token cost every session; the substrate did not grow.

### Documentation-First

**Reinforces**: All three axioms

> Every implementation change must be accompanied by clear documentation.

Documentation is not an afterthought — it is part of the change. A script without a docstring is incomplete. An agent without an `AGENTS.md` reference is incomplete. A feature without a guide is incomplete.

This principle exists because the documentation *is* the knowledge the system encodes for future agents. It reflects what humans have decided; it guides future human decisions.

**Canonical example**: `scripts/fetch_source.py` landed in a single commit that included: the script itself with a module-level docstring, an entry in `scripts/README.md`, and `tests/test_fetch_source.py`. All three completed simultaneously — the triple completion signal. The documentation was part of the change, not a follow-up.

**Anti-pattern**: Merging a working script with no docstring and no `scripts/README.md` entry. The script works, but its knowledge is invisible to the next agent or human who reads `scripts/README.md` for an inventory. The substrate did not grow; the next session starts blind.

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

**Canonical example**: Live session practice confirmed that when agents skip writing to `.tmp/`, the next agent starts blind — scout outputs existed only in the conversation summary and had to be reconstructed at token cost. The scratchpad is the only durable cross-agent memory that survives a context window boundary. Write discipline — not queryability — is the primary gap in practised context management; the write-back requirement has since been mechanically encoded into agent files. See [`docs/research/sources/session-synthesis-2026-03-06-a.md`](docs/research/sources/session-synthesis-2026-03-06-a.md).

### Isolate Invocations, Parallelize Safely

**Reinforces**: Algorithms Before Tokens + Endogenous-First

> Per-invocation context isolation eliminates context rot. Parallelize only when isolation can be maintained. One source per synthesizer invocation; one task per agent run; independent operations in parallel.

When agents process large batches (e.g., multiple sources in a research synthesis), a single large invocation suffers "context rot" — early items degrade as the model processes later ones. Instead:
- Isolate each invocation to a single source/task
- Aggregate results afterward
- Parallelize independent invocations

This maintains fidelity across the entire batch and enables safe parallelization without context interference.

**Canonical example**: Five independent orchestration traditions — Anthropic *Building Effective Agents*, ReAct (arXiv:2210.03629), AIGNE (arXiv:2512.05470), the Claude Agent SDK, and Claude Code Agent Teams — all independently enforce strict per-invocation scope isolation. The SDK states the invariant most precisely: *"the only channel from parent to subagent is the Task prompt string."* These teams did not coordinate their specifications; the convergence confirms that per-invocation isolation is a structural requirement for reliable multi-agent behaviour, not a stylistic preference. Confirmed empirically in this project: running a Synthesizer across 22 sources in a single invocation produced context rot; per-source isolation eliminated it. See [`docs/research/agentic-research-flows.md`](docs/research/agentic-research-flows.md).

### Validate & Gate, Always

**Reinforces**: Self-Governance & Guardrails + Algorithms Before Tokens

> Every phase has a gate. Every gate is checked before advancing. Evaluator-optimizer loops catch errors early. Early validation avoids wasted tokens and prevents bad outputs propagating downstream.

Gates are the mechanism by which the system enforces governance without heavyweight process. Examples include:
- Deliverables checklist before phase transition (research workflow)
- Review gate before commit (all changes)
- Completion criteria self-check before agent handoff

**Canonical example**: Mei et al.'s context engineering survey (arXiv:2507.13334, 1400+ papers) documents a fundamental comprehension-generation asymmetry across LLMs — models understand complex context far better than they generate equivalently sophisticated long-form outputs. This gap is structural, not model-family-specific. The evaluator-optimizer loop is the architecturally correct response: structuring output generation as iterative evaluate-and-refine compensates for models' relative weakness at long-form generation and independently validates the self-loop phase gate design. See [`docs/research/sources/arxiv-context-engineering-survey.md`](docs/research/sources/arxiv-context-engineering-survey.md).

### Minimal Posture

**Reinforces**: Algorithms Before Tokens + Local Compute-First

> Every agent carries only the tools it needs. Every script only the dependencies it requires. Avoid over-provisioning — minimize surface area, maximize efficiency.

Minimal posture extends beyond agents to all design decisions:
- Tools: include only what an agent actually uses (no "just in case" tools)
- Dependencies: validate before adding; prefer well-maintained over feature-rich
- Context: load only what the task requires
- Handoff information: include enough for the next agent to succeed, nothing more

**Canonical example**: `scripts/prune_scratchpad.py --init` — does one thing (initialise the daily scratchpad file), accepts one flag, returns one value (the file path), loads nothing it does not need. Every tool and dependency it uses is directly necessary to its single purpose.

**Anti-pattern**: An agent file that pre-loads all 42 sibling agents' instruction bodies into its system prompt "just in case" one is relevant to the current task. That is 42× context overhead for 0 marginal value per invocation — the opposite of minimal posture.

### Testing-First

**Reinforces**: Algorithms Before Tokens + Self-Governance & Guardrails

> Every script, agent, and automation must have automated tests before it ships. Tests prevent re-discovery of bugs; tests encode known-good behavior.

Automated testing is not optional — it is a constraint on the entire system:
- **Tests encode known-good behavior**: A test suite is a living specification of what a script does. Future developers (human or agent) read tests before modifying code.
- **Tests prevent regression**: When a script is modified, tests catch breakage immediately. This is cheaper than catching bugs in production.
- **Tests reduce review burden**: Code review moves from "does this look right?" (slow, error-prone) to "do tests pass?" (deterministic).
- **Tests are executable documentation**: A test shows exactly how a script is invoked, what inputs are valid, what outputs are expected.
- **Tests reduce token burn in sessions**: If a script is broken, an agent discovers it via test failure, not by re-discovering the bug interactively.

Every script in `scripts/` must have:
- Unit tests covering happy paths and error cases
- Integration tests (marked `@pytest.mark.integration`) for network/file I/O operations
- At least 80% code coverage (measured by `pytest-cov`)
- Exit code validation (every code path has a documented exit code)

See [`docs/guides/testing.md`](docs/guides/testing.md) for testing practices and procedures.

---

## Ethical Values

These values underpin all decisions and encode our commitment to responsible AI development. They are not aspirational — they are enforced through documentation, scripts, and governance.

- **Transparency**: All decisions are documented and traceable to a principle or axiom. No hidden heuristics or unexplained choices. Tests serve as transparent specification of behavior.
- **Human Oversight**: Agents operate under governance and gates. Humans make strategic decisions; the system executes and surfaces information for those decisions. No unconstrained autonomy. Tests validate that governance is enforced.
- **Reproducibility**: Outputs are deterministic, reviewable, and auditable. A decision made on day one can be reproduced on day 100 with the same inputs. Tests ensure reproducibility across sessions.
- **Sustainability**: Minimize computational cost, environmental impact, and token burn. The finite cost of local inference is a feature, not a bug — it incentivizes efficient design. Tests reduce debugging costs by catching errors early.
- **Determinism**: Reduce randomness through encoding, scripts, and established practices. Vagueness is expensive; clarity is cheap. Tests enforce clarity at the API level.

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

See the [GitHub Issues](https://github.com/EndogenAI/dogma/issues) for tracked research tasks.

---

*This manifesto is a living document. It should be updated as the methodology evolves. All changes must follow the documentation-first and commit-discipline dogmas.*
