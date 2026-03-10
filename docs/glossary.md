# Endogenic Development — Glossary

Canonical definitions for key concepts used throughout the EndogenAI Workflows repository.
Each entry cites the authoritative source where the term is introduced or most precisely defined.

---

## Contents

- [Quick Reference Index](#quick-reference-index)
- [Core Axioms](#core-axioms)
- [Foundational Principle](#foundational-principle)
- [Guiding Principles](#guiding-principles)
- [Methodology Concepts](#methodology-concepts)
- [Agent Fleet Concepts](#agent-fleet-concepts)
- [Mental Models and Metaphors](#mental-models-and-metaphors)
- [Ethical Values](#ethical-values)
- [Anti-patterns](#anti-patterns)

---

## Quick Reference Index

| Term | Section |
|------|---------|
| [Adopt Over Author](#adopt-over-author) | Guiding Principles |
| [Algorithms Before Tokens](#algorithms-before-tokens) | Core Axioms |
| [Anti-pattern](#anti-pattern) | Methodology Concepts |
| [Augmentive Partnership](#augmentive-partnership) | Foundational Principle |
| [Autopoiesis](#autopoiesis) | Mental Models |
| [Canonical Example](#canonical-example) | Methodology Concepts |
| [Commit Discipline](#commit-discipline) | Agent Fleet Concepts |
| [Compress Context, Not Content](#compress-context-not-content) | Guiding Principles |
| [Compression-on-Ascent](#focus-on-descent--compression-on-ascent) | Agent Fleet Concepts |
| [Context Rot](#context-rot) | Anti-patterns |
| [Context Window Alert Protocol](#context-window-alert-protocol) | Agent Fleet Concepts |
| [Cross-Reference Density](#cross-reference-density) | Methodology Concepts |
| [D4 Research Document](#d4-research-document) | Methodology Concepts |
| [Delegation Decision Gate](#delegation-decision-gate) | Agent Fleet Concepts |
| [DNA Metaphor](#dna-metaphor) | Mental Models |
| [Documentation-First](#documentation-first) | Guiding Principles |
| [Encoding Fidelity](#encoding-fidelity) | Methodology Concepts |
| [Encoding Inheritance Chain](#encoding-inheritance-chain) | Methodology Concepts |
| [Endogenous-First](#endogenous-first) | Core Axioms |
| [Endogenic Development](#endogenic-development) | Methodology Concepts |
| [Endogenic Flywheel](#endogenic-flywheel) | Methodology Concepts |
| [Evaluator-Optimizer Loop](#evaluator-optimizer-loop) | Agent Fleet Concepts |
| [Expansion → Contraction Pattern](#expansion--contraction-pattern) | Methodology Concepts |
| [Fetch-Before-Act](#fetch-before-act) | Agent Fleet Concepts |
| [Focus-on-Descent / Compression-on-Ascent](#focus-on-descent--compression-on-ascent) | Agent Fleet Concepts |
| [Handoff Drift](#handoff-drift) | Anti-patterns |
| [Isolate Invocations, Parallelize Safely](#isolate-invocations-parallelize-safely) | Guiding Principles |
| [Local Compute-First](#local-compute-first) | Core Axioms |
| [Minimal Posture](#minimal-posture) | Guiding Principles |
| [Morphogenetic Seed](#morphogenetic-seed) | Mental Models |
| [Phase Gate](#phase-gate) | Agent Fleet Concepts |
| [Programmatic-First](#programmatic-first) | Guiding Principles |
| [R-items](#r-items) | Methodology Concepts |
| [SECI Cycle](#seci-cycle) | Methodology Concepts |
| [Self-Governance and Guardrails](#self-governance-and-guardrails) | Guiding Principles |
| [Session-Start Encoding Checkpoint](#session-start-encoding-checkpoint) | Agent Fleet Concepts |
| [Signal Preservation](#signal-preservation) | Methodology Concepts |
| [Scratchpad](#scratchpad) | Agent Fleet Concepts |
| [Testing-First](#testing-first) | Guiding Principles |
| [Token Burn](#token-burn) | Methodology Concepts |
| [Tree Rings of Knowledge](#tree-rings-of-knowledge) | Mental Models |
| [Validate and Gate, Always](#validate-and-gate-always) | Guiding Principles |
| [Vibe Coding](#vibe-coding) | Anti-patterns |
| [Workplan](#workplan) | Agent Fleet Concepts |

---

## Core Axioms

The three core axioms are ordered by priority. When they conflict, Endogenous-First supersedes Algorithms Before Tokens, which supersedes Local Compute-First.

*Source: [`MANIFESTO.md` — The Three Core Axioms](../MANIFESTO.md#the-three-core-axioms)*

---

### Endogenous-First

> Scaffold from existing system knowledge. Absorb and encode the best of what exists externally.

The highest-priority axiom. Before writing any new agent, script, or document, an agent must:

1. Read what the system already knows about itself (`AGENTS.md`, existing scripts, existing docs).
2. Research relevant external tools, frameworks, and prior art.
3. Extend or adapt rather than create from zero.
4. Encode the synthesized knowledge back into the project.

**Key distinction**: Endogenous-First is not isolationism. The system *starts* from within and *grows outward* by absorbing and encoding external knowledge.

**Related terms**: [Encoding Inheritance Chain](#encoding-inheritance-chain), [Morphogenetic Seed](#morphogenetic-seed), [Fetch-Before-Act](#fetch-before-act)

*Source: [`MANIFESTO.md` §Endogenous-First](../MANIFESTO.md#1-endogenous-first)*

---

### Algorithms Before Tokens

> Prefer deterministic, encoded solutions over interactive token burn. Invest in automation early.

Every token spent in interactive sessions carries a cost (computational, financial, environmental). The strategy is to move work upstream: encode algorithms, scripts, and decision trees that prevent re-discovery at session time.

This axiom drives:
- Preference for scripts over interactive prompts
- Caching and pre-computation over re-fetching
- Deterministic workflows over adaptive ones
- Context compression and isolation over broad context loads

**Related terms**: [Token Burn](#token-burn), [Programmatic-First](#programmatic-first), [Endogenic Flywheel](#endogenic-flywheel)

*Source: [`MANIFESTO.md` §Algorithms Before Tokens](../MANIFESTO.md#2-algorithms-before-tokens)*

---

### Local Compute-First

> Minimize token burn. Run locally whenever possible.

Cloud LLM inference is expensive in tokens, money, and environmental cost. The endogenic approach prioritizes:
- Running models locally (Ollama, LM Studio, llama.cpp)
- Encoding context as scripts so it does not need to be re-derived each session
- Using free or cheaper tiers where local compute is insufficient
- Caching and pre-computing context rather than re-discovering it interactively

**Related terms**: [Token Burn](#token-burn), [Algorithms Before Tokens](#algorithms-before-tokens)

*Source: [`MANIFESTO.md` §Local Compute-First](../MANIFESTO.md#3-local-compute-first)*

---

## Foundational Principle

### Augmentive Partnership

The design principle that endogenic development is not about agent autonomy or reducing human involvement — it is about creating a **tight human-system partnership** where:

- The **human** provides direction, judgment, ethical guidance, and oversight.
- The **system** provides deterministic execution, encoding, memory, and automation.
- Neither works without the other — they form a unified cognitive system.
- The goal is to **amplify human judgment**, not replace it.

Descends directly from Douglas Engelbart's augmentation framework ("Augmenting Human Intellect", 1962), updated for the LLM context.

**Related terms**: [Phase Gate](#phase-gate), [Self-Governance and Guardrails](#self-governance-and-guardrails)

*Source: [`MANIFESTO.md` §Foundational Principle: Augmentive Partnership](../MANIFESTO.md#foundational-principle-augmentive-partnership)*

---

## Guiding Principles

Cross-cutting principles that reinforce the core axioms and guide all implementation decisions. They are not hierarchical but interconnected.

*Source: [`MANIFESTO.md` §Guiding Principles (Cross-Cutting)](../MANIFESTO.md#guiding-principles-cross-cutting)*

---

### Programmatic-First

> If you have done a task twice interactively, the third time is a script.

Any repeated or automatable task must be encoded as a committed script or automation before being performed a third time by hand. This is a constraint on the entire agent fleet, not an optional preference.

**Reinforces**: [Algorithms Before Tokens](#algorithms-before-tokens) + [Endogenous-First](#endogenous-first)

**Decision criteria** (from `AGENTS.md`):

| Situation | Action |
|-----------|--------|
| Task performed once interactively | Note it; consider scripting |
| Task performed twice interactively | Script it before the third time |
| Task is a validation or format check | Script it immediately; CI should enforce it too |
| Task involves reading many files to build context | Pre-compute and cache — encode as a script |
| Task generates boilerplate from a template | Generator script |
| Task could break something if done wrong | Script it with a `--dry-run` guard |
| Task is genuinely non-recurring | Interactive is acceptable — document the assumption |

**Related terms**: [Algorithms Before Tokens](#algorithms-before-tokens), [Token Burn](#token-burn)

*Source: [`MANIFESTO.md` §Programmatic-First](../MANIFESTO.md#programmatic-first), [`AGENTS.md` §Programmatic-First Principle](../AGENTS.md#programmatic-first-principle), [`docs/guides/programmatic-first.md`](guides/programmatic-first.md)*

---

### Documentation-First

> Every implementation change must be accompanied by clear documentation.

Documentation is not an afterthought — it is part of the change. A script without a docstring is incomplete. An agent without an `AGENTS.md` reference is incomplete. A feature without a guide is incomplete.

**Reinforces**: All three axioms.

The documentation *is* the knowledge the system encodes for future agents. It reflects what humans have decided; it guides future human decisions.

**Related terms**: [Encoding Inheritance Chain](#encoding-inheritance-chain), [Programmatic-First](#programmatic-first)

*Source: [`MANIFESTO.md` §Documentation-First](../MANIFESTO.md#documentation-first)*

---

### Adopt Over Author

> Use established open-source tools and frameworks when they solve a problem well. Do not rebuild what is already well-maintained externally.

Adoption is not dependency — it is standing on the shoulders of giants. Document the integrated tool, encode its usage patterns into scripts and agents, and let it become part of the endogenous substrate.

**Reinforces**: [Algorithms Before Tokens](#algorithms-before-tokens) + [Endogenous-First](#endogenous-first)

*Source: [`MANIFESTO.md` §Adopt Over Author (Avoid Reinventing the Wheel)](../MANIFESTO.md#adopt-over-author-avoid-reinventing-the-wheel)*

---

### Self-Governance and Guardrails

> Agents self-report deviations. Guardrails are validated programmatically, not just documented.

Governance occurs at three levels:
1. **Documented conventions** in `AGENTS.md` and `MANIFESTO.md`
2. **Programmatic validation** via scripts that check compliance
3. **Self-reporting by agents** when they detect deviations

**Reinforces**: All three axioms.

**Related terms**: [Phase Gate](#phase-gate), [Validate and Gate, Always](#validate-and-gate-always)

*Source: [`MANIFESTO.md` §Self-Governance & Guardrails](../MANIFESTO.md#self-governance--guardrails)*

---

### Compress Context, Not Content

> Minimize the context window burden through lazy loading, selective compression, and caching. Every token in context should serve a purpose; remove irrelevant history, not knowledge.

Techniques include:
- **Lazy loading**: load full agent bodies only when that agent is invoked
- **Selective compression**: summarize completed phases, retain decision rationale
- **Caching**: store pre-fetched sources, pre-computed vectors, and analysis results
- **Isolation**: strip irrelevant conversation history from agent prompts

**Reinforces**: [Algorithms Before Tokens](#algorithms-before-tokens) + [Local Compute-First](#local-compute-first)

**Related terms**: [Token Burn](#token-burn), [Scratchpad](#scratchpad), [Focus-on-Descent / Compression-on-Ascent](#focus-on-descent--compression-on-ascent)

*Source: [`MANIFESTO.md` §Compress Context, Not Content](../MANIFESTO.md#compress-context-not-content)*

---

### Isolate Invocations, Parallelize Safely

> Per-invocation context isolation eliminates context rot. Parallelize only when isolation can be maintained.

When agents process large batches, a single large invocation suffers "context rot" — early items degrade as the model processes later ones. Instead:
- Isolate each invocation to a single source or task
- Aggregate results afterward
- Parallelize independent invocations

**Reinforces**: [Algorithms Before Tokens](#algorithms-before-tokens) + [Endogenous-First](#endogenous-first)

**Related terms**: [Context Rot](#context-rot), [Focus-on-Descent / Compression-on-Ascent](#focus-on-descent--compression-on-ascent)

*Source: [`MANIFESTO.md` §Isolate Invocations, Parallelize Safely](../MANIFESTO.md#isolate-invocations-parallelize-safely)*

---

### Validate and Gate, Always

> Every phase has a gate. Every gate is checked before advancing. Evaluator-optimizer loops catch errors early.

Gates are the mechanism by which the system enforces governance without heavyweight process. Examples:
- Deliverables checklist before phase transition (research workflow)
- Review gate before commit (all changes)
- Completion criteria self-check before agent handoff

**Reinforces**: [Self-Governance and Guardrails](#self-governance-and-guardrails) + [Algorithms Before Tokens](#algorithms-before-tokens)

**Related terms**: [Phase Gate](#phase-gate), [Evaluator-Optimizer Loop](#evaluator-optimizer-loop)

*Source: [`MANIFESTO.md` §Validate & Gate, Always](../MANIFESTO.md#validate--gate-always)*

---

### Minimal Posture

> Every agent carries only the tools it needs. Every script only the dependencies it requires. Avoid over-provisioning.

Applies to:
- **Tools**: include only what an agent actually uses
- **Dependencies**: validate before adding; prefer well-maintained over feature-rich
- **Context**: load only what the task requires
- **Handoff information**: include enough for the next agent to succeed, nothing more

**Reinforces**: [Algorithms Before Tokens](#algorithms-before-tokens) + [Local Compute-First](#local-compute-first)

*Source: [`MANIFESTO.md` §Minimal Posture](../MANIFESTO.md#minimal-posture)*

---

### Testing-First

> Every script, agent, and automation must have automated tests before it ships. Tests prevent re-discovery of bugs; tests encode known-good behavior.

Tests are not optional — they are:
- **Specification**: Tests define what a script does (inputs, outputs, error cases)
- **Regression prevention**: if a script breaks, tests catch it immediately
- **Executable documentation**: a test shows exactly how a script is invoked

Every script in `scripts/` must have unit tests, integration tests (for network/file I/O), and at least 80% code coverage.

**Reinforces**: [Algorithms Before Tokens](#algorithms-before-tokens) + [Self-Governance and Guardrails](#self-governance-and-guardrails)

*Source: [`MANIFESTO.md` §Testing-First](../MANIFESTO.md#testing-first), [`docs/guides/testing.md`](guides/testing.md)*

---

## Methodology Concepts

---

### Anti-pattern

A labeled, canonical description of a behavior that violates one or more axioms or principles. Anti-patterns are the most resilient encoding form: they survive paraphrasing and drift. If a proposed action matches a stated anti-pattern, it must be rejected regardless of whether a cross-cutting principle appears to permit it.

Anti-patterns are marked with the prefix `**Anti-pattern**:` in the codebase.

**Related terms**: [Canonical Example](#canonical-example), [Encoding Fidelity](#encoding-fidelity)

*Source: [`MANIFESTO.md` §How to Read This Document](../MANIFESTO.md#how-to-read-this-document)*

---

### Canonical Example

A labeled, concrete, real-world illustration of a principle or axiom applied correctly. Canonical examples are preserved verbatim when compressing Scout findings; they must not be paraphrased away during compression because they carry the highest signal density.

Marked with the prefix `**Canonical example**:` in the codebase.

**Related terms**: [Anti-pattern](#anti-pattern), [Signal Preservation](#signal-preservation)

*Source: [`AGENTS.md` §Focus-on-Descent / Compression-on-Ascent](../AGENTS.md#focus-on-descent--compression-on-ascent)*

---

### Cross-Reference Density

A proxy measure for [encoding fidelity](#encoding-fidelity). Cross-reference density is the count of explicit back-references to `MANIFESTO.md` (by name and section) in an agent output or document. Low density signals likely drift from foundational axioms.

*Source: [`AGENTS.md` §Guiding Constraints](../AGENTS.md#guiding-constraints)*

---

### D4 Research Document

A synthesis document format used for research outputs in `docs/research/`. The format is enforced by `scripts/validate_synthesis.py` in CI. A valid D4 document must:

- Have YAML frontmatter with at least a `title` and `status` field
- Contain a section matching `## 2. Hypothesis Validation` (or with those keywords in the heading)
- Contain a section matching `## 3. Pattern Catalog` (or with those keywords in the heading)
- Include at least one `**Canonical example**:` and one `**Anti-pattern**:` in the Pattern Catalog section

The name derives from the four-phase structure (Document, Discover, Distill, Deliver) that all research synthesis follows.

**Related terms**: [Signal Preservation](#signal-preservation), [SECI Cycle](#seci-cycle)

*Source: [`docs/guides/workflows.md` §Research Workflow](guides/workflows.md#research-workflow), [`scripts/validate_synthesis.py`](../scripts/validate_synthesis.py)*

---

### Encoding Fidelity

The degree to which a downstream re-encoding faithfully preserves the signal of the upstream source. Each layer in the [Encoding Inheritance Chain](#encoding-inheritance-chain) is a re-encoding; lossy re-encoding (paraphrase, omission, drift) degrades fidelity and erodes axiom adherence over time.

Measured as a proxy by [cross-reference density](#cross-reference-density).

**Related terms**: [Encoding Inheritance Chain](#encoding-inheritance-chain), [Cross-Reference Density](#cross-reference-density), [Signal Preservation](#signal-preservation)

*Source: [`AGENTS.md` §Guiding Constraints](../AGENTS.md#guiding-constraints), [`docs/research/values-encoding.md`](research/values-encoding.md)*

---

### Encoding Inheritance Chain

The six-layer hierarchy through which values and operational constraints flow, each layer re-encoding the layer above:

```
MANIFESTO.md
  → AGENTS.md
    → subdirectory AGENTS.md files
      → .agent.md role files (VS Code Custom Agents)
        → SKILL.md files
          → session prompts (enacted behavior)
```

When layers conflict, the higher layer governs. When a lower layer is silent on a topic, behavior is derived from the layer above.

**Related terms**: [Encoding Fidelity](#encoding-fidelity), [Cross-Reference Density](#cross-reference-density)

*Source: [`MANIFESTO.md` §How to Read This Document](../MANIFESTO.md#how-to-read-this-document), [`AGENTS.md` §Guiding Constraints](../AGENTS.md#guiding-constraints)*

---

### Endogenic Development

A methodology for building AI-assisted systems — agents, scripts, documentation, and knowledge infrastructure — **from the inside out**, while standing on the shoulders of giants.

Key properties:
- **Encodes knowledge as DNA**: scripts, agent files, schemas, and seed documents that persist across sessions
- **Grows from a seed**: every new capability scaffolds from what the system already knows about itself and from best external practices
- **Adds tree rings of knowledge**: each session accumulates in the substrate
- **Reduces token burn**: encoded context does not need to be re-discovered interactively

The name comes from biology: an endogenous process originates from within the organism. Like all living systems, the endogenic substrate is built from inherited knowledge and continuous synthesis of external wisdom.

**Related terms**: [Morphogenetic Seed](#morphogenetic-seed), [Tree Rings of Knowledge](#tree-rings-of-knowledge), [DNA Metaphor](#dna-metaphor)

*Source: [`MANIFESTO.md` §What Is Endogenic Development?](../MANIFESTO.md#what-is-endogenic-development)*

---

### Endogenic Flywheel

The compounding growth loop that characterizes a healthy endogenic project:

```
Session 1: Agent discovers how to do X interactively
Session 2: Agent does X again; notes it was done twice
Session 3: Agent scripts X before doing it a third time (programmatic-first)
Session N: Future agents start sessions with X already encoded as a script
```

Over time, the system accumulates scripts, agents, and guides. New sessions start richer. Token burn decreases. Determinism increases.

**Related terms**: [Tree Rings of Knowledge](#tree-rings-of-knowledge), [Programmatic-First](#programmatic-first), [Token Burn](#token-burn)

*Source: [`MANIFESTO.md` §The Growth Model: Tree Rings of Knowledge](../MANIFESTO.md#the-growth-model-tree-rings-of-knowledge)*

---

### Expansion → Contraction Pattern

A research methodology principle: **expand broadly** in discovery (scout widely, gather sources, generate hypotheses), then **contract precisely** to vetted, sourced, high-signal outputs (synthesis document, committed scripts).

This pattern originates from design thinking methodology and is the governing rhythm of the [SECI Cycle](#seci-cycle) and deep research workflow.

**Related terms**: [SECI Cycle](#seci-cycle), [D4 Research Document](#d4-research-document)

*Source: [`docs/guides/workflows.md` §Research Workflow](guides/workflows.md#research-workflow)*

---

### R-items

Recommendations extracted from a completed `docs/research/` synthesis document that are ready for implementation. Each R-item is numbered (R1, R2, …) and tracked as a GitHub issue. The Implementation Workflow is triggered when a synthesis document reaches `status: Final` and contains at least one un-implemented R-item.

*Source: [`docs/guides/workflows.md` §Implementation Workflow](guides/workflows.md#implementation-workflow)*

---

### SECI Cycle

The knowledge-creation cycle (Socialization → Externalization → Combination → Internalization) adapted from Nonaka and Takeuchi for the endogenic research workflow:

| Phase | Endogenic equivalent |
|-------|---------------------|
| **Socialization** (tacit → tacit) | Scout agent gathers raw findings in the scratchpad |
| **Externalization** (tacit → explicit) | Synthesizer converts Scout notes into a structured synthesis document |
| **Combination** (explicit → explicit) | Reviewer and Archivist validate and commit the synthesis document |
| **Internalization** (explicit → tacit) | Updated `AGENTS.md`, guides, or scripts encode the new knowledge into the substrate |

**Related terms**: [D4 Research Document](#d4-research-document), [Expansion → Contraction Pattern](#expansion--contraction-pattern)

*Source: [`docs/guides/deep-research.md` §Core Principles](guides/deep-research.md#core-principles)*

---

### Signal Preservation

A set of rules governing what must **not** be discarded when compressing Scout findings or synthesizer outputs during the [Focus-on-Descent / Compression-on-Ascent](#focus-on-descent--compression-on-ascent) pattern:

1. All labeled `**Canonical example**:` and `**Anti-pattern**:` instances must be preserved verbatim.
2. At least 2 explicit `MANIFESTO.md` axiom citations (by name + section reference) must be retained as anchors.
3. Synthesizer D4 drafts must include at least one canonical example and one anti-pattern in the Pattern Catalog section.

**Related terms**: [Canonical Example](#canonical-example), [Anti-pattern](#anti-pattern), [Encoding Fidelity](#encoding-fidelity)

*Source: [`AGENTS.md` §Focus-on-Descent / Compression-on-Ascent](../AGENTS.md#focus-on-descent--compression-on-ascent)*

---

### Token Burn

The computational, financial, and environmental cost of interactive LLM inference. Token burn is minimized by:
- Encoding repeated work as scripts ([Programmatic-First](#programmatic-first))
- Caching external sources ([Fetch-Before-Act](#fetch-before-act))
- Compressing context efficiently ([Compress Context, Not Content](#compress-context-not-content))
- Running computations locally ([Local Compute-First](#local-compute-first))

**Related terms**: [Algorithms Before Tokens](#algorithms-before-tokens), [Local Compute-First](#local-compute-first)

*Source: [`MANIFESTO.md` §Algorithms Before Tokens](../MANIFESTO.md#2-algorithms-before-tokens)*

---

## Agent Fleet Concepts

---

### Commit Discipline

The requirement that all commits follow [Conventional Commits](https://www.conventionalcommits.org/) format, are small and incremental (one logical unit per commit), and are pushed frequently. Commit early, commit often — uncommitted changes are the most vulnerable to context-window loss.

Types used in this project: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `perf`

*Source: [`AGENTS.md` §Guiding Constraints](../AGENTS.md#guiding-constraints), [`CONTRIBUTING.md` §Commit Discipline](../CONTRIBUTING.md#commit-discipline)*

---

### Context Window Alert Protocol

A mandatory full-stop protocol triggered when context compaction is imminent or has occurred. When triggered:

1. Write `## Context Window Checkpoint` to the scratchpad with all active phase state
2. Commit all in-progress changes immediately
3. Present a session handoff prompt so the next session can resume cleanly

The protocol takes priority over all in-progress work because a session that exhausts context without a recoverable state record cannot be handed off.

**Related terms**: [Scratchpad](#scratchpad), [Phase Gate](#phase-gate)

*Source: [`AGENTS.md` §Context Window Alert Protocol](../AGENTS.md) (in Executive Orchestrator agent file)*

---

### Delegation Decision Gate

A routing table that maps task domains to the specialist agent responsible for them. The Orchestrator consults this table before every delegation to ensure domain work is not performed directly in the main context window.

| Task domain | Delegate to |
|-------------|-------------|
| Research, source gathering | Executive Researcher |
| Documentation writing/editing | Executive Docs |
| Scripting, automation design | Executive Scripter, Executive Automator |
| Fleet agent authoring/audit | Executive Fleet |
| Release coordination | Release Manager |
| Issue triage, labels, milestones | Issue Triage, Executive PM |

The Orchestrator acts directly only for coordination, verification reads, and state management (git, scratchpad writes).

**Related terms**: [Focus-on-Descent / Compression-on-Ascent](#focus-on-descent--compression-on-ascent), [Phase Gate](#phase-gate)

*Source: [`docs/guides/workflows.md` §Multi-Workflow Orchestration](guides/workflows.md#multi-workflow-orchestration)*

---

### Evaluator-Optimizer Loop

A self-referential review gate in which an executive agent reviews its own or a subagent's output before advancing to the next phase. The loop is the architecturally correct response to LLMs' comprehension-generation asymmetry (models understand complex context far better than they generate equivalently sophisticated long-form outputs). Structuring output generation as iterative evaluate-and-refine compensates for this asymmetry.

**Related terms**: [Phase Gate](#phase-gate), [Validate and Gate, Always](#validate-and-gate-always)

*Source: [`docs/guides/workflows.md` §Handoff Architecture](guides/workflows.md#handoff-architecture)*

---

### Fetch-Before-Act

The posture of populating the local source cache *before* any research agent begins work. The primary implementation is `scripts/fetch_all_sources.py`, which batch-fetches all URLs from `OPEN_RESEARCH.md` and existing research doc frontmatter and stores them in `.cache/sources/`. Agents then read from the local cache rather than fetching from the web, eliminating redundant network token burn.

Check-before-fetch: use `scripts/fetch_source.py <url> --check` on individual URLs to verify cache state before fetching.

**Related terms**: [Endogenous-First](#endogenous-first), [Algorithms Before Tokens](#algorithms-before-tokens)

*Source: [`AGENTS.md` §Programmatic-First Principle](../AGENTS.md#programmatic-first-principle)*

---

### Focus-on-Descent / Compression-on-Ascent

A dual constraint on agent communication that preserves the main-session context window:

- **Focus-on-Descent**: Outbound delegation prompts must be narrow and task-scoped — dispatch the minimum necessary context for the subagent to complete its task.
- **Compression-on-Ascent**: Returned results must target ≤ 2,000 tokens — subagents compress extensive exploration into a dense handoff; they do not return raw search histories or intermediate reasoning.

Both constraints serve the same purpose: a broad outbound prompt and a verbose return each consume context as if the work were done directly.

**Related terms**: [Signal Preservation](#signal-preservation), [Compress Context, Not Content](#compress-context-not-content), [Token Burn](#token-burn)

*Source: [`AGENTS.md` §Focus-on-Descent / Compression-on-Ascent](../AGENTS.md#focus-on-descent--compression-on-ascent)*

---

### Phase Gate

A formal checkpoint that must be passed before a workflow phase can advance. Each gate has a defined deliverable and a verification step. Common gate types:

- **Research gate**: synthesis document committed with `status: Final`
- **Review gate**: Review agent returns `APPROVED` verdict in the scratchpad
- **Commit gate**: all changes committed and CI passing before PR review

Skipping a phase gate is an anti-pattern equivalent to committing without CI.

**Related terms**: [Evaluator-Optimizer Loop](#evaluator-optimizer-loop), [Validate and Gate, Always](#validate-and-gate-always)

*Source: [`AGENTS.md` §Agent Communication](../AGENTS.md#agent-communication), [`docs/guides/workflows.md` §Gates Reference](guides/workflows.md#gates-reference)*

---

### Scratchpad

The per-session cross-agent communication file stored in `.tmp/<branch-slug>/<YYYY-MM-DD>.md`. It is gitignored and never committed. The scratchpad is the **only durable cross-agent memory** that survives a context window boundary within a session.

Key rules:
- Each delegated subagent **appends** findings under its own named section heading
- The **Executive is the sole integration point** — it alone reads the full scratchpad
- Subagents do not read laterally across each other's sections
- At session end, the Executive writes a `## Session Summary` for the next session

When a session file reaches 2,000 lines, run `scripts/prune_scratchpad.py` to compress it.

**Related terms**: [Session-Start Encoding Checkpoint](#session-start-encoding-checkpoint), [Focus-on-Descent / Compression-on-Ascent](#focus-on-descent--compression-on-ascent)

*Source: [`AGENTS.md` §Agent Communication](../AGENTS.md#agent-communication)*

---

### Session-Start Encoding Checkpoint

A mandatory ritual at the start of every session: the first sentence of `## Session Start` in the scratchpad must name the governing axiom and one primary endogenous source consulted before any tool calls or delegations.

Format: `"Governing axiom: [amplified principle] — primary endogenous source: [source name]."`

The purpose is to anchor each session to the encoding inheritance chain before any domain work begins, preventing sessions that start without reading the system's own knowledge.

**Related terms**: [Encoding Inheritance Chain](#encoding-inheritance-chain), [Endogenous-First](#endogenous-first), [Scratchpad](#scratchpad)

*Source: [`AGENTS.md` §Guiding Constraints](../AGENTS.md#guiding-constraints), [`docs/guides/session-management.md`](guides/session-management.md)*

---

### Workplan

A committed Markdown file in `docs/plans/` that captures the multi-phase execution plan for a session. Required for any session with ≥ 3 phases or ≥ 2 agent delegations.

**Naming convention**: `docs/plans/YYYY-MM-DD-<brief-slug>.md`

**Required contents**:
- Objective
- Phase plan with agent, deliverables, depends-on, and status fields
- A Review gate phase after every domain phase
- Acceptance criteria checklist

The workplan is committed at the start of the session (before Phase 1 executes) and updated as phases complete. It creates an auditable plan history in git, separate from the ephemeral scratchpad.

**Related terms**: [Phase Gate](#phase-gate), [Scratchpad](#scratchpad)

*Source: [`AGENTS.md` §docs/plans/ — Tracked Workplans](../AGENTS.md#docplans----tracked-workplans)*

---

## Mental Models and Metaphors

The endogenic methodology uses three core nature metaphors. These metaphors are not decoration — they reveal the structure and patterns that run through every level of the system.

*Source: [`docs/guides/mental-models.md`](guides/mental-models.md)*

---

### Autopoiesis

From Maturana and Varela (1972): a system is autopoietic if it produces and maintains its own components. An endogenic project is autopoietic — each session produces scripts, guides, and agent files that maintain the substrate, so future sessions start richer than the ones that preceded them.

Used in `MANIFESTO.md` to ground the [Endogenous-First](#endogenous-first) axiom in biological theory.

*Source: [`MANIFESTO.md` §Endogenous-First](../MANIFESTO.md#1-endogenous-first)*

---

### DNA Metaphor

The analogy between biological DNA and the project's encoded operational knowledge (scripts, agent files, guides, conventions). Just as DNA carries inherited evolutionary wisdom and is expressed through biochemical processes, the project's encoded knowledge is inherited across sessions and expressed through agent behavior.

Properties of DNA that map to the endogenic substrate:
- **Passed forward**: each session inherits scripts and conventions from all prior sessions
- **Not static**: principles can be refined without breaking what came before
- **Source of expression**: agents read encoded principles and execute against them
- **Replicated with fidelity**: version control ensures accurate replication across sessions

**Related terms**: [Encoding Inheritance Chain](#encoding-inheritance-chain), [Endogenic Development](#endogenic-development)

*Source: [`docs/guides/mental-models.md` §DNA: Encoding and Expression](guides/mental-models.md#dna-encoding-and-expression)*

---

### Morphogenetic Seed

The initial set of axioms, scripts, and documented conventions that a new project starts from. Like a biological seed, it contains everything needed to grow — the system just needs the right environment (human oversight, quality research inputs, project-specific constraints) to unfold correctly.

The term references Turing's morphogenesis (1952), which describes how complex structure can emerge from simple initial conditions.

**Related terms**: [Endogenic Development](#endogenic-development), [DNA Metaphor](#dna-metaphor), [Autopoiesis](#autopoiesis)

*Source: [`MANIFESTO.md` §What Is Endogenic Development?](../MANIFESTO.md#what-is-endogenic-development)*

---

### Tree Rings of Knowledge

The analogy between a tree's annual growth rings and the session-by-session accumulation of scripts, agents, and guides in a project.

Key properties:
- **Cumulative**: new growth builds on prior rings; nothing is discarded
- **Visible history**: `git log` tells the same story as cross-sectioning a tree
- **Progressive surface area**: each ring expands the fleet's capability surface
- **Load-bearing**: the system is strong because of *all* accumulated rings, not just the latest

Running `git log` should reveal readable tree rings — which sessions were productive, which focused on docs, which shipped features.

**Related terms**: [Endogenic Flywheel](#endogenic-flywheel), [DNA Metaphor](#dna-metaphor)

*Source: [`MANIFESTO.md` §The Growth Model: Tree Rings of Knowledge](../MANIFESTO.md#the-growth-model-tree-rings-of-knowledge), [`docs/guides/mental-models.md` §Tree Rings](guides/mental-models.md#tree-rings-recursive-encoding-of-knowledge)*

---

## Ethical Values

Five values that underpin all decisions and encode the project's commitment to responsible AI development. They are not aspirational — they are enforced through documentation, scripts, and governance.

*Source: [`MANIFESTO.md` §Ethical Values](../MANIFESTO.md#ethical-values)*

---

**Transparency** — All decisions are documented and traceable to a principle or axiom. No hidden heuristics or unexplained choices. Tests serve as transparent specification of behavior.

**Human Oversight** — Agents operate under governance and gates. Humans make strategic decisions; the system executes and surfaces information for those decisions. No unconstrained autonomy.

**Reproducibility** — Outputs are deterministic, reviewable, and auditable. A decision made on day one can be reproduced on day 100 with the same inputs.

**Sustainability** — Minimize computational cost, environmental impact, and token burn. The finite cost of local inference is a feature, not a bug — it incentivizes efficient design.

**Determinism** — Reduce randomness through encoding, scripts, and established practices. Vagueness is expensive; clarity is cheap.

---

## Anti-patterns

Named violations of axioms and principles. Anti-patterns are canonical veto rules: if a proposed action matches a stated anti-pattern, reject it regardless of whether a cross-cutting principle appears to permit it.

---

### Context Rot

The degradation of model output quality that occurs when a single large agent invocation processes too much content in one pass. Early items are "forgotten" or misrepresented as the model processes later ones. Mitigated by [Isolate Invocations, Parallelize Safely](#isolate-invocations-parallelize-safely).

*Source: [`MANIFESTO.md` §Isolate Invocations, Parallelize Safely](../MANIFESTO.md#isolate-invocations-parallelize-safely)*

---

### Handoff Drift

The progressive loss of signal fidelity as findings are passed between agents across multiple compression steps. Handoff drift is the cumulative result of lossy re-encoding at each phase boundary. Mitigated by [Signal Preservation](#signal-preservation) rules.

*Source: [`AGENTS.md` §Focus-on-Descent / Compression-on-Ascent](../AGENTS.md#focus-on-descent--compression-on-ascent)*

---

### Isolationism

The anti-pattern of refusing to adopt existing open-source tools and insisting on building everything from scratch. Violates [Adopt Over Author](#adopt-over-author) and [Endogenous-First](#endogenous-first) (the latter requires *absorbing* external wisdom, not ignoring it).

*Source: [`MANIFESTO.md` §Endogenous-First](../MANIFESTO.md#1-endogenous-first)*

---

### Vibe Coding

The practice of prompting an AI with a vague intention and accepting whatever it produces, iterating by feel until something works, without reading the system's existing encoded knowledge first. Produces:
- Non-deterministic outcomes
- Undocumented decisions
- Token-hungry sessions that re-discover context every time
- Agents that hallucinate conventions that don't exist

The canonical violation of [Endogenous-First](#endogenous-first): starting a session without reading `AGENTS.md` and asking the agent to "write a script to do X."

*Source: [`MANIFESTO.md` §What We Are Not Doing — Not Vibe Coding](../MANIFESTO.md#not-vibe-coding)*

---

*This glossary is a living document. When new terms are introduced in `MANIFESTO.md`, `AGENTS.md`, or major guides, add them here. Follow [Documentation-First](#documentation-first): update the glossary in the same commit that introduces the term.*
