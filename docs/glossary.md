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
- [Substrates](#substrates)
- [Roles, Skills, and the Customization Taxonomy](#roles-skills-and-the-customization-taxonomy)
- [Mental Models and Metaphors](#mental-models-and-metaphors)
- [Ethical Values](#ethical-values)
- [Anti-patterns](#anti-patterns)

---

## Quick Reference Index

| Term | Section |
|------|---------|
| [Adopt Over Author](#adopt-over-author) | Guiding Principles |
| [Agent](#agent) | Roles, Skills, and the Customization Taxonomy |
| [Agent Fleet](#agent-fleet) | Roles, Skills, and the Customization Taxonomy |
| [Agent Posture](#agent-posture) | Roles, Skills, and the Customization Taxonomy |
| [Algorithms Before Tokens](#algorithms-before-tokens) | Core Axioms |
| [Anti-pattern](#anti-pattern) | Methodology Concepts |
| [Augmentive Partnership](#augmentive-partnership) | Foundational Principle |
| [Autopoiesis](#autopoiesis) | Mental Models |
| [Bubble-Cluster Model](#bubble-cluster-model) | Substrates |
| [Canonical Example](#canonical-example) | Methodology Concepts |
| [Commit Discipline](#commit-discipline) | Agent Fleet Concepts |
| [Compress Context, Not Content](#compress-context-not-content) | Guiding Principles |
| [Compression-on-Ascent](#focus-on-descent--compression-on-ascent) | Agent Fleet Concepts |
| [Context Rot](#context-rot) | Anti-patterns |
| [Context Window Alert Protocol](#context-window-alert-protocol) | Agent Fleet Concepts |
| [Cross-Reference Density](#cross-reference-density) | Methodology Concepts |
| [Custom Agent](#agent) | Roles, Skills, and the Customization Taxonomy |
| [D4 Research Document](#d4-research-document) | Methodology Concepts |
| [Delegation Decision Gate](#delegation-decision-gate) | Agent Fleet Concepts |
| [DNA Metaphor](#dna-metaphor) | Mental Models |
| [Documentation-First](#documentation-first) | Guiding Principles |
| [Encoded Substrate](#encoded-substrate) | Substrates |
| [Encoding Fidelity](#encoding-fidelity) | Methodology Concepts |
| [Encoding Inheritance Chain](#encoding-inheritance-chain) | Methodology Concepts |
| [Endogenous-First](#endogenous-first) | Core Axioms |
| [Endogenic Development](#endogenic-development) | Methodology Concepts |
| [Endogenic Flywheel](#endogenic-flywheel) | Methodology Concepts |
| [Evaluator-Optimizer Loop](#evaluator-optimizer-loop) | Agent Fleet Concepts |
| [Executable Documentation](#executable-documentation) | Methodology Concepts |
| [Executive Agent](#executive-agent-vs-sub-agent) | Roles, Skills, and the Customization Taxonomy |
| [Expansion → Contraction Pattern](#expansion--contraction-pattern) | Methodology Concepts |
| [Fetch-Before-Act](#fetch-before-act) | Agent Fleet Concepts |
| [Focus-on-Descent / Compression-on-Ascent](#focus-on-descent--compression-on-ascent) | Agent Fleet Concepts |
| [Handoff Drift](#handoff-drift) | Anti-patterns |
| [Isolate Invocations, Parallelize Safely](#isolate-invocations-parallelize-safely) | Guiding Principles |
| [Knowledge Substrate](#knowledge-substrate) | Substrates |
| [Local Compute-First](#local-compute-first) | Core Axioms |
| [Membrane (Substrate Boundary)](#membrane-substrate-boundary) | Substrates |
| [Minimal Posture](#minimal-posture) | Guiding Principles |
| [Morphogenetic Seed](#morphogenetic-seed) | Mental Models |
| [Phase Gate](#phase-gate) | Agent Fleet Concepts |
| [Programmatic-First](#programmatic-first) | Guiding Principles |
| [R-items](#r-items) | Methodology Concepts |
| [Role](#role) | Roles, Skills, and the Customization Taxonomy |
| [SECI Cycle](#seci-cycle) | Methodology Concepts |
| [Self-Governance and Guardrails](#self-governance-and-guardrails) | Guiding Principles |
| [Session-Start Encoding Checkpoint](#session-start-encoding-checkpoint) | Agent Fleet Concepts |
| [Signal Preservation](#signal-preservation) | Methodology Concepts |
| [Skill (SKILL.md)](#skill-skillmd) | Roles, Skills, and the Customization Taxonomy |
| [Scratchpad](#scratchpad) | Agent Fleet Concepts |
| [Sovereignty](#sovereignty) | Guiding Principles |
| [Sub-agent](#executive-agent-vs-sub-agent) | Roles, Skills, and the Customization Taxonomy |
| [Substrate](#substrate) | Substrates |
| [Testing-First](#testing-first) | Guiding Principles |
| [Takeback Pattern](#takeback-pattern) | Agent Fleet Concepts |
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

**Note**: The base word *endogenous* (from Greek *endo* = "within" + *genesis* = "origin") means "originating internally." See [Endogenous-First](#endogenous-first) for the axiom and [Endogenic Development](#endogenic-development) for the methodology.

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

### Sovereignty

The property of a system (or organization) where its own encoded values, constraints, and governance rules *govern its AI workflows* — rather than delegating that authority to an external policy server, vendor platform, or third-party service.

Sovereignty is sustained when:
- Governance constraints live in the repository (MANIFESTO.md, AGENTS.md, scripts/)
- Every agent reads those constraints before acting
- No external service can alter or override them unilaterally

**Key distinction from isolation**: Sovereignty does not mean refusing external tools or knowledge — it means the *decision authority* over how those tools are used remains internal. A sovereign system can adopt an external model provider while retaining full control over the guardrails it enforces.

**Related terms**: [Endogenous-First](#endogenous-first), [Encoded Substrate](#encoded-substrate), [Local Compute-First](#local-compute-first)

*Source: [`MANIFESTO.md` §What Is Endogenic Development?](../MANIFESTO.md#what-is-endogenic-development), [`README.md`](../README.md) tagline*

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

A synthesis document format used for research outputs in `docs/research/`. The format is enforced by `scripts/validate_synthesis.py` in CI. A valid D4 document must (per the validator):

- Have YAML frontmatter with at least a `title` and `status` field
- Contain a section matching `## 1. Executive Summary`
- Contain a section matching `## 2. Hypothesis Validation` (or with those keywords in the heading)
- Contain a section matching `## 3. Pattern Catalog` (or with those keywords in the heading)
- Include at least a minimum number of second-level headings (`##`) overall (see `scripts/validate_synthesis.py` for the current threshold)

Recommended (but not CI-enforced) conventions include annotating patterns in the Pattern Catalog section with `**Canonical example**:` and `**Anti-pattern**:` labels.

The name derives from the four-phase structure (Document, Discover, Distill, Deliver) that all research synthesis follows.

**Related terms**: [Signal Preservation](#signal-preservation), [SECI Cycle](#seci-cycle)

*Source: [`docs/guides/workflows.md` §Research Workflow](guides/workflows.md#research-workflow), [`scripts/validate_synthesis.py`](../scripts/validate_synthesis.py)*

---

### Encoding Fidelity

The degree to which a downstream re-encoding faithfully preserves the signal of the upstream source. Each layer in the [Encoding Inheritance Chain](#encoding-inheritance-chain) is a re-encoding; lossy re-encoding (paraphrase, omission, drift) degrades fidelity and erodes axiom adherence over time.

Measured as a proxy by [cross-reference density](#cross-reference-density).

**Related terms**: [Encoding Inheritance Chain](#encoding-inheritance-chain), [Cross-Reference Density](#cross-reference-density), [Signal Preservation](#signal-preservation)

*Source: [`AGENTS.md` §Guiding Constraints](../AGENTS.md#guiding-constraints), [`docs/research/values-encoding.md`](./research/methodology/values-encoding.md)*

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

### Signal Boundary

Any point in the substrate system at which information undergoes a transformation as it moves from one bounded context to another, regardless of whether that transition is vertical (layer-to-layer in the inheritance chain) or horizontal (substrate-to-substrate at a membrane). The signal boundary is the shared abstraction that both "encoding layer transition" (values-encoding.md) and "membrane" (bubble-clusters-substrate.md) instantiate.

**Related terms**: [Encoding Inheritance Chain](#encoding-inheritance-chain), [Transit Loss](#transit-loss), [Boundary Specification](#boundary-specification)

*Source: [`docs/research/vocabulary-bridge-encoding-models.md`](./research/methodology/vocabulary-bridge-encoding-models.md)*

---

### Transit Loss

The degradation or complete absence of a signal after it has crossed a signal boundary, quantified relative to the signal's state before the boundary event. Transit loss is boundary-scoped — it measures what was present before and absent after the crossing, not degradation that occurs within a single substrate. Bridges "lossy re-encoding" (values-encoding.md) and "membrane rejection/attenuation" (bubble-clusters-substrate.md).

**Related terms**: [Signal Boundary](#signal-boundary), [Encoding Fidelity](#encoding-fidelity), [Preservation Unit](#preservation-unit)

*Source: [`docs/research/vocabulary-bridge-encoding-models.md`](./research/methodology/vocabulary-bridge-encoding-models.md)*

---

### Preservation Unit

A discrete element of content explicitly designated — through labeling, structural encoding, or formal specification — as requiring intact transit through a signal boundary. In values-encoding.md, preservation units are the four [4,1]-encoded content forms (canonical examples, anti-patterns, axiom citations, programmatic hooks); in bubble-clusters-substrate.md, they are the signal types named in a membrane permeability specification.

**Related terms**: [Canonical Example](#canonical-example), [Anti-pattern](#anti-pattern), [Signal Boundary](#signal-boundary), [Boundary Specification](#boundary-specification)

*Source: [`docs/research/vocabulary-bridge-encoding-models.md`](./research/methodology/vocabulary-bridge-encoding-models.md)*

---

### Substrate Coherence

The compound health property of a substrate measuring both (a) its fidelity to inherited values from upstream sources and (b) its calibrated connectivity to adjacent substrates. A substrate can fail on either dimension independently: high fidelity with low connectivity is "isolated coherence"; high connectivity with low fidelity is "connected confusion." Full substrate health requires both, operationalized by values-encoding.md (fidelity dimension) and bubble-clusters-substrate.md (connectivity dimension).

**Related terms**: [Encoding Fidelity](#encoding-fidelity), [Cross-Reference Density](#cross-reference-density), [Encoding Inheritance Chain](#encoding-inheritance-chain)

*Source: [`docs/research/vocabulary-bridge-encoding-models.md`](./research/methodology/vocabulary-bridge-encoding-models.md)*

---

### Boundary Specification

The declarative act of stating, before a signal boundary event occurs, which preservation units must survive the crossing intact and under what conditions. In values-encoding.md, boundary specification is the source-side labeling that enables [4,1] redundancy encoding; in bubble-clusters-substrate.md, it is the membrane permeability policy that governs what the membrane must admit. Both models require this artifact be produced before the boundary event — they differ only in how the specification is enacted.

**Related terms**: [Signal Boundary](#signal-boundary), [Preservation Unit](#preservation-unit), [Encoding Inheritance Chain](#encoding-inheritance-chain)

*Source: [`docs/research/vocabulary-bridge-encoding-models.md`](./research/methodology/vocabulary-bridge-encoding-models.md)*

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

*Source: [`.github/agents/executive-orchestrator.agent.md` §Context Window Alert Protocol](../.github/agents/executive-orchestrator.agent.md#context-window-alert-protocol)*

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

### Takeback Pattern

The handoff pattern in which each sub-agent returns control to the executive after completing its task, rather than chaining directly to the next sub-agent. This keeps the executive in oversight at every step and ensures the scratchpad is updated before the next delegation begins.

```
Executive → Sub-agent A → [Back to Executive] → Sub-agent B → Review → GitHub
```

This pattern is recommended over direct agent-to-agent chaining because it maintains the executive as the sole integration point and prevents context from being lost between phases.

**Related terms**: [Executive Agent vs. Sub-agent](#executive-agent-vs-sub-agent), [Phase Gate](#phase-gate)

*Source: [`docs/guides/agents.md` §Handoff Patterns](guides/agents.md#handoff-patterns)*

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

*Source: [`AGENTS.md` §docs/plans/ — Tracked Workplans](../AGENTS.md#docsplans----tracked-workplans)*

---

## Substrates

A substrate is a discrete layer in the endogenic architecture — a bounded region of encoded knowledge with its own mutation rate, stability tier, and specificity level. The complete set of substrates forms the [Encoding Inheritance Chain](#encoding-inheritance-chain).

*Source: [`MANIFESTO.md` §What Is Endogenic Development?](../MANIFESTO.md#what-is-endogenic-development), [`docs/research/bubble-clusters-substrate.md`](./research/neuroscience/bubble-clusters-substrate.md)*

---

### Substrate

The complete system of encoded knowledge, documentation, scripts, and governance structures that persist across development sessions and guide agent behavior.

The components of the endogenic substrate are:

| Substrate | Role |
|-----------|------|
| `MANIFESTO.md` | Foundational axioms and values; highest stability, slowest mutation rate |
| `AGENTS.md` (root + subdirectory) | Operational constraints for the agent fleet |
| `.agent.md` role files | Per-agent persona, posture, tools, and handoff logic |
| `SKILL.md` files | Reusable tactical procedures |
| `scripts/` | Encoded deterministic work (the primary machinery of Algorithms Before Tokens) |
| `docs/` | Guides, research synthesis, toolchain references |
| Session scratchpads (`.tmp/`) | Ephemeral inter-session memory; not committed |
| CI gates | Programmatic enforcement of substrate health |

**Key quote**: *"Like all living systems, our endogenic substrate is built from inherited knowledge (standing on giants' shoulders) and continuous synthesis of external wisdom (tools, frameworks, best practices)."* — `MANIFESTO.md`

**Autopoietic property**: each session produces scripts, guides, and agent files that maintain the substrate, so future sessions start richer than the ones that preceded them.

**Related terms**: [Encoding Inheritance Chain](#encoding-inheritance-chain), [Bubble-Cluster Model](#bubble-cluster-model), [DNA Metaphor](#dna-metaphor)

*Source: [`MANIFESTO.md` §What Is Endogenic Development?](../MANIFESTO.md#what-is-endogenic-development)*

---

### Encoded Substrate

Knowledge, conventions, and procedures deliberately written into committed files so agents can read and reuse them across sessions rather than re-discovering them interactively. When something is "encoded" into the substrate, a future session starts richer without burning tokens to rediscover it.

**Examples**: Committed scripts, documented conventions in `AGENTS.md`, procedures in `SKILL.md` files, toolchain guides in `docs/toolchain/`

**The anti-pattern signal**: *"The substrate did not grow; the next session starts blind."* This phrase in `MANIFESTO.md` flags whenever work was done interactively without encoding the result.

**Related terms**: [Substrate](#substrate), [Programmatic-First](#programmatic-first), [Token Burn](#token-burn)

*Source: [`MANIFESTO.md` §Documentation-First](../MANIFESTO.md#documentation-first), [`MANIFESTO.md` §Programmatic-First](../MANIFESTO.md#programmatic-first)*

---

### Knowledge Substrate

The specific layer of substrate that encodes *operational knowledge* — what the system knows about how to perform its tasks. Includes guides, research synthesis documents, documented conventions in `AGENTS.md`, reusable procedures in `SKILL.md` files, and toolchain references.

The `docs/toolchain/` substrate is the canonical example: it encodes canonical safe patterns and known footguns for heavily-used CLI tools so agents look them up rather than reconstruct them — the [Algorithms Before Tokens](#algorithms-before-tokens) axiom applied to documentation.

**Related terms**: [Substrate](#substrate), [Encoded Substrate](#encoded-substrate), [Algorithms Before Tokens](#algorithms-before-tokens)

*Source: [`AGENTS.md` §Toolchain Reference](../AGENTS.md#toolchain-reference)*

---

### Membrane (Substrate Boundary)

In the [Bubble-Cluster Model](#bubble-cluster-model), the active boundary between two substrates that governs how information crosses between substrate layers. Membranes are not passive transitions — they are the primary site of signal fidelity loss and, when calibrated correctly, signal amplification.

**Membrane dynamics**:
- Too impermeable → the substrate drifts from the rest of the system (isolation)
- Too permeable → the substrate loses its distinct identity and collapses into the adjacent substrate
- Calibrated permeability → optimal signal fidelity across boundaries

**Endogenic equivalent of membrane**: the handoff prompt between agents, the cross-reference citation in a document, the explicit `## Source:` field in research docs. These are the designed permeability controls.

**Related terms**: [Bubble-Cluster Model](#bubble-cluster-model), [Signal Preservation](#signal-preservation), [Handoff Drift](#handoff-drift)

*Source: [`docs/research/bubble-clusters-substrate.md`](./research/neuroscience/bubble-clusters-substrate.md)*

---

### Bubble-Cluster Model

A mental model that frames the endogenic substrate as a collection of discrete "bubbles" — each with an active boundary membrane — rather than a flat stack of layers. The model adds a spatial and topological dimension to the [Encoding Inheritance Chain](#encoding-inheritance-chain).

**Metaphor mapping**:

| Bubble element | Endogenic analog |
|----------------|-----------------|
| **Bucket** | The user / practitioner — the containing environment that holds all substrates and supplies intent |
| **Soap** | Data, knowledge, research findings — reduces surface tension between substrates, enabling information transfer |
| **Bubbles** | Substrates (`MANIFESTO.md`, `AGENTS.md`, agent files, scripts, scratchpads) — discrete, bounded regions |
| **Air inside bubbles** | The AI agent fleet — the invisible pressurizing medium that gives each substrate its shape and internal coherence |

**Key insight**: *"Value fidelity is not only a question of faithful re-encoding at each layer — it is equally a question of membrane permeability and connectivity geometry."* A substrate that is too isolated drifts. A substrate with no membrane collapses into its neighbor. Optimal signal fidelity requires calibrated membrane dynamics.

**Relationship to inheritance-chain model**: The two models are additive. The inheritance chain describes the *vertical* dimension (top-down value propagation); the bubble-cluster model describes the *horizontal and topological* dimension (lateral signal dynamics, boundary permeability, inter-substrate connectivity gradients).

**Related terms**: [Substrate](#substrate), [Membrane (Substrate Boundary)](#membrane-substrate-boundary), [Encoding Inheritance Chain](#encoding-inheritance-chain)

*Source: [`docs/research/bubble-clusters-substrate.md`](./research/neuroscience/bubble-clusters-substrate.md)*

---

## Roles, Skills, and the Customization Taxonomy

The three first-class primitives in the repository's customization stack define *who does a task* (Roles), *what all agents must do* (AGENTS.md), and *how a task is done* (Skills).

| Primitive | File Format | Encodes |
|-----------|------------|---------|
| Fleet constraints | `AGENTS.md` files | Universal behaviors, guardrails, operational conventions |
| **Roles** | `.agent.md` in `.github/agents/` | Role-specific persona, posture, tool restrictions, endogenous sources, handoff graph |
| **Skills** | `SKILL.md` in `.github/skills/<name>/` | Reusable workflow procedures loadable on demand |

**Boundary decision rule**: Content belongs in a role file when it is exclusively about that agent's role. Content belongs in a `SKILL.md` when it describes *how a task is performed* and at least one other agent or AI tool could benefit from it. If the same procedure appears in two agent bodies, extract it to a skill before writing a third copy (Programmatic-First applied to instruction prose).

*Source: [`AGENTS.md` §VS Code Customization Taxonomy](../AGENTS.md#vs-code-customization-taxonomy), [`docs/guides/agents.md`](guides/agents.md)*

---

### Role

The identity concept that a `.agent.md` file encodes: *who does a task*. A Role is a discrete, bounded set of responsibilities with a unique posture, tool restrictions, and handoff logic. Roles appear as **Custom Agents** in VS Code Copilot Chat (invoked with `@<agent-name>`).

**Synonyms**: Custom Agent, `.agent.md` file. The term "Character" has been proposed informally as an alternative but is not yet canonical.

**Restaurant analogy** (from `docs/guides/mental-models.md`): Roles are *Job Descriptions* — the Chef de Cuisine, Maître d', and Sous Chef each have a different `.agent.md` file. All read the same `AGENTS.md` (Operations Manual); each has different specialized responsibilities, tool restrictions, and quality gates.

**Characteristics of a Role**:
- YAML frontmatter with `name` and `description`
- `## Endogenous Sources` section (what to read before acting)
- `## Action` section (what the role does)
- `## Quality-gate` section (acceptance criteria)
- Tool restriction declaration (read-only, read+create, or full execution)
- Handoff graph (downstream agents)

**vs. Skill**: Roles encode *who does a task*. Skills encode *how a task is done*. If a procedure could be used by more than one role without needing that role's posture, it belongs in a Skill.

**Related terms**: [Skill (SKILL.md)](#skill-skillmd), [Agent Posture](#agent-posture), [Agent Fleet](#agent-fleet), [Encoding Inheritance Chain](#encoding-inheritance-chain)

*Source: [`docs/guides/agents.md` §What Are Agents?](guides/agents.md#what-are-agents), [`MANIFESTO.md` §What Is Endogenic Development?](../MANIFESTO.md#what-is-endogenic-development)*

---

### Agent

The runtime instance of a Role: a governed AI persona that reads its endogenous sources before acting, follows documented conventions, and hands off to downstream agents rather than overreaching its scope.

> *"Agents are not magic — they are documented, reviewable, constrained workers. The value is in the constraints and the encoded knowledge they read before acting."* — `docs/guides/agents.md`

Each agent:
- Reads `AGENTS.md` and its own endogenous sources before taking any action
- Operates within its declared [posture](#agent-posture)
- Escalates decisions outside its scope rather than forcing them
- Commits before handoff (via Review → GitHub)

**In VS Code**: Agents are invoked as `@<agent-name>` in Copilot Chat. They appear as "Custom Agents."

**Related terms**: [Role](#role), [Agent Posture](#agent-posture), [Agent Fleet](#agent-fleet), [Executive Agent vs. Sub-agent](#executive-agent-vs-sub-agent)

*Source: [`docs/guides/agents.md` §What Are Agents?](guides/agents.md#what-are-agents)*

---

### Agent Fleet

The complete set of defined agents that work together following the endogenic methodology. The fleet is organized hierarchically — executive agents coordinate and delegate to specialist sub-agents.

**Pressurizing metaphor** (from [Bubble-Cluster Model](#bubble-cluster-model)): *"The agent fleet is the pressurizing medium — it gives each substrate coherent form but does not own the membrane or the bucket."* — `AGENTS.md`. The fleet is the air inside the bubbles: invisible, essential, the source of internal structure.

**Fleet management**: Automated via `scripts/generate_agent_manifest.py`. The catalog of all agents is at `.github/agents/README.md`. Fleet authoring, auditing, and deprecation is owned by the **Executive Fleet** agent.

**Named fleet architectures** (from `docs/research/agent-fleet-design-patterns.md`):
- Orchestrator-Workers
- Evaluator-Optimizer Loop
- Parallel Research Fleet
- Focus-Dispatch / Compression-Return
- Context-Isolated Sub-Fleet
- Hybrid (orchestrator + specialist sub-fleet)

**Related terms**: [Agent](#agent), [Role](#role), [Executive Agent vs. Sub-agent](#executive-agent-vs-sub-agent)

*Source: [`AGENTS.md` §Agent Fleet Overview](../AGENTS.md#agent-fleet-overview), [`docs/research/agent-fleet-design-patterns.md`](./research/agents/agent-fleet-design-patterns.md)*

---

### Executive Agent vs. Sub-agent

**Executive Agent**: An agent with full execution posture that coordinates, delegates, and synthesizes across sub-agents. The sole integration point that reads the full scratchpad and writes `## Session Summary`. Executive agents orchestrate; they do not do all the work themselves.

**Sub-agent**: An agent delegated by an executive to perform a specific, isolated task. Sub-agents do NOT read laterally across each other's scratchpad sections. They return results to the executive, which synthesizes them.

**Key rule**: *"The Executive is the sole integration point — it alone reads the full scratchpad to synthesise findings across all agents. Subagents do not read laterally."* — `AGENTS.md`

**Named executive agents**: Executive Orchestrator, Executive Researcher, Executive Docs, Executive Scripter, Executive Automator, Executive Fleet, Executive PM, Executive Planner.

**Related terms**: [Agent Fleet](#agent-fleet), [Takeback Pattern](#takeback-pattern), [Scratchpad](#scratchpad), [Delegation Decision Gate](#delegation-decision-gate)

*Source: [`AGENTS.md` §Agent Communication](../AGENTS.md#agent-communication)*

---

### Agent Posture

The set of tools and capabilities an agent is permitted to use. Three tiers exist, corresponding to increasing capability and risk surface:

| Posture | Permitted tools | Typical examples |
|---------|----------------|-----------------|
| **Read-only** | `search`, `read`, `changes`, `usages` | Review agent, plan agents |
| **Read + create** | Adds `edit`, `web` | Scaffold agents, documentation agents |
| **Full execution** | Adds `execute`, `terminal`, `agent` | Executive agents |

**Minimal Posture constraint**: Agents should never carry more tools than their posture requires. If an agent needs to do something outside its posture, it must escalate to an agent with the appropriate posture rather than forcing it.

**Related terms**: [Minimal Posture](#minimal-posture), [Role](#role), [Agent](#agent)

*Source: [`docs/guides/agents.md` §Agent Posture](guides/agents.md#agent-posture)*

---

### Skill (SKILL.md)

A `SKILL.md` file stored at `.github/skills/<skill-name>/SKILL.md` that encodes a reusable tactical workflow procedure. Skills are loaded on-demand only when relevant, making them token-efficient compared to always-on agent body instructions.

**Core distinction**: *"Agents encode **who does a task**; skills encode **how a task is done**."* — `AGENTS.md`

**When to extract to a Skill**: Any procedure in an agent body that a different agent or AI tool could also benefit from — without needing that agent's specific posture or tool restrictions — is a Skill candidate. If the same procedure appears in two agent bodies, extract it before writing a third copy (Programmatic-First applied to instruction prose).

**Restaurant analogy**: Skills are *Technique Cards* — "Perfect Béarnaise Sauce" is a reusable technique that the Chef de Cuisine, Sous Chef, and Senior Line Cook all execute. It is not a Role.

**Required frontmatter**:

```yaml
---
name: <skill-name>         # lowercase, hyphens only, matches parent directory
description: <one-line summary>
---
```

**Every SKILL.md must** cite `AGENTS.md` as its governing constraint in the body, to anchor it to the encoding inheritance chain and make encoding-fidelity auditable.

**Token efficiency**: At 20 registered skills, baseline overhead is ~2,000 tokens (metadata only) vs. the same knowledge always-on in agent bodies: ~20,000+ tokens. Per *Algorithms Before Tokens*, this is a meaningful reduction in session-time token burn.

**CI validation**: `uv run python scripts/validate_agent_files.py --skills`

**Related terms**: [Role](#role), [Agent](#agent), [Encoding Inheritance Chain](#encoding-inheritance-chain), [Minimal Posture](#minimal-posture)

*Source: [`AGENTS.md` §Agent Skills](../AGENTS.md#agent-skills), [`docs/guides/agents.md` §Skills](guides/agents.md), [`docs/decisions/ADR-006-agent-skills-adoption.md`](decisions/ADR-006-agent-skills-adoption.md)*

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
