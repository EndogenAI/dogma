---
title: "Endogenic Development Methodology: A Four-Layer Framework for AI-Assisted System Design Grounded in Software Engineering Tradition and Biological Self-Organisation"
status: Draft
---

# Endogenic Development Methodology: A Four-Layer Framework for AI-Assisted System Design Grounded in Software Engineering Tradition and Biological Self-Organisation

**Authors**: EndogenAI Research Team
**Venue**: [Target: ACM CHI / CSCW / FSE — TBD]
**Date**: 2026-03-07

## Executive Summary

EndogenAI is the first operationalised development methodology to connect a fifty-year
software engineering documentation tradition — literate programming → Architecture Decision
Records → living documentation — directly to a session-initialization discipline for AI-assisted
work across all domains (agents, scripting, documentation, knowledge management), grounded in
biological self-organisation theory and Engelbart's augmentation paradigm. The composite
four-hypothesis architecture (CS design lineage H4, encode-before-act H1, augmentive partnership
H3, morphogenetic system design H2) constitutes a prescriptive, CI-enforced operational
framework with no identified precedent in the academic literature.

## Abstract

AI-assisted systems for software development have proliferated rapidly, yet the methodological
principles governing how such systems should be designed, initialized, and maintained lack formal
treatment. Most frameworks address runtime behaviour — prompt chaining, tool selection, memory
retrieval — while neglecting the design-time question: what structured knowledge should a
system receive before it acts, and how should that knowledge be authored, validated, and sustained
over time? This question applies equally to agent fleets, scripting automation, documentation
practices, and knowledge management infrastructure.

We present Endogenic Development Methodology: a prescriptive operational framework built
on a four-hypothesis architecture spanning four distinct theoretical traditions. The methodology's
central claim is the *encode-before-act* principle: before issuing any action token, any system
component — whether an agent, script, or human practitioner — must be initialized from a
pre-authored structured knowledge base rather than reconstructing context interactively from
session history. This paper demonstrates the methodology by applying it to multi-agent coding
fleets, and describes its broader applicability across scripting, documentation, and knowledge
management domains.

Our primary contribution (C1) is the identification of a traceable intellectual lineage —
Knuth's literate programming (1984) → Nygard's Architecture Decision Records (2011) →
Martraire's living documentation (2019) → the AGENTS.md / CLAUDE.md artifact class used in
contemporary AI workflows. This chain has not been previously identified or published; drawing it
establishes AI agent context files as the most recent expression of a fifty-year software
engineering principle: human-readable specification asserts temporal and epistemic priority over
executable behaviour. We further contribute (C2) a four-hypothesis architecture — CS design
lineage (H4), encode-before-act discipline (H1), augmentive partnership (H3), and morphogenetic
system design (H2) — in which each hypothesis both requires and explains at least one other,
forming a mutually reinforcing structure whose composite novelty exceeds the sum of its parts.
We introduce (C3) four cross-hypothesis design patterns that are actionable engineering principles
derived from the architecture, and provide (C4) an operational implementation with CI-enforced
validation gates, scaffold scripts, and named roles demonstrating applicability across agent
fleets, scripting automation, and documentation workflows.

A four-sprint research investigation grounded these claims against the closest prior art from
context engineering, augmentation theory, multi-agent systems dynamics, and the CS
documentation tradition. Novelty verdicts range from Partially Novel (H1–H3) to Novel (H4);
H4 is the strongest single contribution and the correct anchoring point for the methodology's
CS legitimation claim.

## 1. Introduction

The design of effective AI-assisted systems for software development has emerged as a central
challenge in applied AI research. While considerable work addresses what systems should *do*
during execution — prompt chaining, tool selection, chain-of-thought reasoning, memory retrieval
— far less attention has been paid to how systems should be *designed* and *initialized* before
the first action token is issued. This design-time question applies across multiple domains:
multi-agent fleets, automation scripting, documentation practices, and knowledge management
infrastructure. Yet the underlying principle is the same: what structured knowledge should a
system receive before acting, and how should that knowledge be authored, validated, and sustained
over time?

We argue that this distinction — between reactive context reconstruction and principled
pre-session initialization — is the central design question for AI-assisted systems, and that it
has an answer grounded in a fifty-year tradition of software engineering thought. This paper
develops the methodology generally, then demonstrates its application to multi-agent coding
fleets.

Our motivating observation is that the AGENTS.md and CLAUDE.md files now appearing in
AI-oriented repositories are, structurally, living documentation artifacts in the sense that
Martraire (2019) defined: documents that co-evolve with the system they describe and govern
the behaviour of any reader. That they are read by AI agents rather than human developers does
not change their structural role — they are human-readable specifications with temporal and
epistemic priority over the executable behaviour they govern. This is precisely the claim that
Knuth made for literate programs in 1984, that Nygard made for Architecture Decision Records
in 2011, and that Martraire synthesized into the living documentation paradigm in 2019. The
chain has not been identified as such in the published literature; drawing it is our primary
contribution.

The Endogenic Development Methodology operationalizes this insight as a complete design framework.
It specifies not only the artifact class — AGENTS.md-style files, guides, workplans, and
Architecture Decision Records — but the behavioural discipline (encode-before-act: read the
specification before any action), the system architecture (role-specialized components — agents,
scripts, automation — with low epistatic coupling), and the human-system relationship (agents
and scripts as co-authors of the structured knowledge substrate that governs their own future
behaviour). The methodology is validated by a four-sprint research investigation whose findings
we synthesize here. This paper focuses on agent fleet design as the primary demonstration domain,
though the methodology applies equally to scripting automation, documentation practices, and
knowledge management infrastructure.

**Contributions** — This paper makes four contributions:

- **C1 — CS Design Lineage**: We identify and formalize the intellectual chain Knuth (1984) →
  Nygard (2011) → Martraire (2019) → AGENTS.md-class files, demonstrating that AI agent
  context files are the most recent instantiation of a recurring principle: human-readable
  specification asserts temporal and epistemic priority over executable behaviour. This
  identification is absent from all surveyed literature.
- **C2 — Four-Hypothesis Architecture**: We present a mutually reinforcing four-hypothesis
  architecture (H4 → H1 → H3 → H2) in which each hypothesis occupies a distinct explanatory
  layer — CS legitimation, session-behavioural prescription, human-relationship framing, and
  fleet-dynamics theory — and in which the dependencies between hypotheses are structurally
  necessary rather than post-hoc justifications.
- **C3 — Cross-Hypothesis Design Patterns**: We derive four actionable design patterns —
  Encoding Chain as Organizational Closure Mechanism, Encode-Before-Act as Artifact Activation
  Discipline, Substrate-Creation as LAM/T Layer Maintenance, and Low-K Specialization as Fleet
  Health Criterion — each grounded in at least two of the four hypotheses and each carrying
  specific engineering implications.
- **C4 — Operational Implementation**: We document a working implementation including
  CI-enforced validation gates, scaffold scripts, and a fleet of specialized agents,
  demonstrating the framework's feasibility in a live software development context.

The remainder of this paper is structured as follows. Section 2 surveys prior art across the
four theoretical traditions the framework draws upon. Section 3 describes the EndogenAI
methodology operationally and introduces the cross-hypothesis design patterns. Section 4
develops the theoretical grounding and hypothesis validation. Section 5 discusses novelty,
limitations, and open empirical questions. Section 6 concludes.

## 2. Background and Related Work

The EndogenAI methodology synthesizes four distinct bodies of prior work. We characterize
what each establishes and the gap that the present framework addresses.

**Context engineering for AI agents.** Mei et al. (2025) provide the most comprehensive
taxonomy of context management for LLM agents to date, organizing it as an ongoing flow
problem: context is continuously fetched, filtered, compressed, and updated across an agent's
lifetime. Xu et al. (2025) introduce the Constructor → Loader → Evaluator pipeline, in which
the Constructor phase assembles context before reasoning begins — the closest structural
antecedent to encode-before-act identified in our survey. The critical gap is one of framing:
existing work treats context as a *retrieval* problem (what to fetch in response to a task
query) rather than an *initialization* problem (what to load unconditionally at session start,
from a specific knowledge layer, before any task-specific reasoning). Encode-before-act does
not appear in Mei et al.'s comprehensive taxonomy under any name; absence from a current,
wide-scope survey is meaningful evidence of a prior art gap rather than a search artifact.

**Agent memory architectures.** Park et al.'s Generative Agents (2023) retrieve episodic
memories before behaviour planning, establishing a precedent for pre-action context loading.
H1's contribution is a precise distinction between episodic memory (what has this agent
experienced before?) and system knowledge (what does this agent know about its role,
conventions, and responsibility boundaries?). Encode-before-act loads system knowledge; this
is structurally distinct from episodic retrieval and from Ramirez's (2025) dynamic temporal
memory synthesis during operation, both of which are reactive and runtime-scoped.

**Human-computer augmentation theory.** The Engelbart-Bush augmentation lineage is
well-established [BUSH45, ENG62]. Tong (2026) provides the most recent mapping of this
tradition onto LLM-based agents, demonstrating coherent augmentation framing at the
user-performance level. H3's claim is orthogonal: we ask not what the AI augments but what
the AI *produces*. When the AI's primary deliverable is a substrate artifact — a guide, a
convention file, a validated encoding — and that artifact governs subsequent AI behaviour, the
relationship becomes co-authorship of the augmentation system itself. Berry (2025) addresses
productive augmentation as a cognitive mode but similarly operates within the user-performance
axis. The substrate-creation inversion is absent from all surveyed augmentation literature.

**Multi-agent system dynamics.** Fernandez (2016) applies autopoiesis as a modeling tool for
MAS dynamics. Wu and Or (2025) invoke it for human-AI collectives in a positional paper
without formal operationalization. Alicea and Parent (2021) apply morphogenetic theory to
individual agent cognition rather than fleet architecture. Franco and Gomes (2024) use NK
coevolution in social physics contexts unrelated to AI fleet design. What is absent from all
surveyed work is the joint operationalization of Turing's (1952) reaction-diffusion formalism,
Maturana and Varela's (1980) organizational closure, and Kauffman's (1993) NK fitness
landscape model as a *prescriptive design framework* — specifically one that treats the fleet
itself, rather than an external environment, as an autopoietic system whose designers must
respect organizational closure constraints.

**CS documentation tradition.** Knuth (1984), Nygard (2011), and Martraire (2019) form an
internally documented chain that Martraire makes explicit: living documentation traces its
lineage to literate programming and encompasses ADRs as decision-level living documents.
Czarnecki and Eisenecker (2000) provide an independent corroborating frame: in generative
programming, the specification is the primary artifact from which executable behaviour is
derived — structurally parallel to the encode-before-act direction. Dhar et al.'s AgenticAKM
(2026) demonstrate LLMs generating ADRs from codebases at scale, confirming the ADR ↔ AI
agent connection is an active research frontier, but operating in reverse direction and drawing
no lineage to literate programming. The chain from literate programming through living
documentation to AI agent context files has not been drawn.

## 3. The EndogenAI Methodology and Pattern Catalog

The EndogenAI methodology is a prescriptive operational framework for multi-agent AI coding
systems. Its defining orientation is *design-time*: the primary artifacts are structured
documents authored and validated before agents are invoked, not produced outputs of individual
agent sessions. The encode-before-act principle is the behavioural expression of this
orientation: agents consume the structured knowledge base unconditionally before the first
action token.

### 3.1 The Encoding Chain

The framework's primary organizational structure is a five-level cascade:

```
MANIFESTO.md → AGENTS.md → agent files → SKILL.md files → session prompts
```

Each level re-encodes the level above it, carrying values and constraints forward with lower
abstraction and higher specificity. MANIFESTO.md encodes foundational axioms. AGENTS.md
operationalizes those axioms as behavioural constraints for all agents in the fleet. Individual
agent files specialize the constraints for a given role — Executive Researcher, Scout,
Synthesizer, Archivist, and so forth. Session prompts enact role-specific constraints in the
context of a particular task.

This cascade performs two inseparable functions. First, it is a *literate
programming-style artifact hierarchy*: each document is the human-readable primary artifact
from which behaviour is derived, and the machine-facing output (the agent's action trace) is
the derived artifact. Second, it is an *autopoietic organizational closure mechanism*: the
chain regenerates the fleet's organizational identity; every link is a regenerative artifact.
Scripts that scaffold and validate the chain (`scaffold_agent.py`, `validate_agent_files.py`)
are not convenience tooling — they are the fleet's closure machinery. A role that exists only
in documentation without a corresponding scaffold template violates organizational closure.

**Deployment-Layer Extension**: This five-layer model assumes a single principal (EndogenAI). When the methodology is adopted by external teams or products, the encoding chain extends to six layers, with explicit conflict-resolution rules governing value priority when Core-layer axioms, Deployment-layer policies, Client-specific values, and Session-scoped constraints diverge. Corpus reference: [external-value-architecture.md](external-value-architecture.md) specifies the Deployment Layer architecture and Supremacy constraints (Core > Deployment > Client > Session) governing multi-principal scenarios.

### 3.2 The Encode-Before-Act Discipline

The encode-before-act principle states: every agent session begins by reading the encoding
chain — from MANIFESTO.md through to the agent's own instruction file — before issuing any
action token. In the operational framework this is enforced as a pre-condition: CI-gated
validation scripts check cross-reference density, section completeness, and encoding fidelity
against the foundational documents.

The behavioural consequence is structurally significant. An agent that has read the encoding
chain begins each session from a principled specification of its role, responsibilities, and
governing constraints. An agent that reconstructs this from session context begins from an
approximation that degrades at each session boundary. The former is *initialization*; the
latter is *reconstruction*. This maps onto Xu et al.'s Constructor phase — but where Xu et al.
frame the Constructor as a context quality-optimization step, encode-before-act is a session
*contract*: the specification is loaded unconditionally before task-specific reasoning begins,
regardless of task type or prior state.

### 3.3 Fleet Architecture

The fleet is composed of single-responsibility agents with narrow, well-defined mandates:
Executive Orchestrator, Executive Researcher, Scout, Synthesizer, Archivist, Reviewer, GitHub
agent, and specialized executive agents for documentation, scripting, and automation. This
architecture operationalizes Kauffman's low-K specialization principle: agents with narrow
mandates and few inter-agent dependencies form modular, stable specializations. High-K agents
— broad mandate, many cross-dependencies — degrade fleet modularity and produce rugged
capability landscapes that resist stable specialization and require fleet-level coordination
to converge.

The fleet is governed by a human-authored authorization hierarchy. MANIFESTO.md expresses
foundational values; agents do not regenerate it from task context — they operate within it.
This is the architectural expression of Bush's (1945) limiting axiom: "for mature thought
there is no mechanical substitute." The constraint is asymmetric by design: agents read the
top layer; they do not write it. Allowing agents to rewrite top-level values from session
context would collapse the augmentation relationship into automation.

### 3.4 Pattern Catalog

Four cross-hypothesis design patterns emerge from the methodology. Each is grounded in at
least two of the four theoretical hypotheses and carries specific engineering implications.

**Encoding Chain as Organizational Closure Mechanism (H4 × H2)**: The cascade functions
simultaneously as a literate programming artifact hierarchy (H4) and an autopoietic closure
mechanism (H2). Scripts that scaffold and validate the chain are regenerative machinery. A
role without a scaffold template severs the closure loop; `validate_agent_files.py`'s
cross-reference density check operationalizes Turing's local-encoding-rule principle — each
agent following the local rule "cite foundational documents when invoking a foundational
principle" collectively produces coherent fleet topology without central coordination.

**Encode-Before-Act as Artifact Activation Discipline (H4 × H1)**: AGENTS.md-class files are
literate programming artifacts for agents (H4); encode-before-act is the protocol activating
them at session scope (H1). Together they constitute a discipline: the agent encounters the
artifact, reads it as a constitutive specification, and only then issues action tokens. This
is not retrieval — it is initialization. The specification governs the session the way an ADR
governs an architectural decision: unconditionally, before the work begins.

**Programmatic Governance Stack (H1 × H4 × C4)**: Behavioral constraints are encoded at multiple enforcement tiers (T1–T5), with higher tiers providing stronger assurance. Prompt-level constraints (T1–T2) state the values; script-level gates (T3) check structural compliance; pre-commit hooks (T4) prevent non-compliant commits; runtime sandboxing (T5) enforces boundaries at execution time. The endogenic implementation instantiates this pattern: MANIFESTO.md (T1 specification), AGENTS.md (T2 re-encoding), `validate_synthesis.py` (T3 structure check), pre-commit hooks (T4 push gate), and `.github/workflows/` CI validation (T5 integration testing). Corpus reference: [shifting-constraints-from-tokens.md](shifting-constraints-from-tokens.md) formalizes the enforcement tier hierarchy, demonstrating why programmatic encoding is superior to token-based guidance for high-assurance constraints.

**Substrate-Creation as LAM/T Layer Maintenance (H3 × H1)**: Sessions that produce substrate
artifacts — guides, validated encoding updates, committed scripts — directly augment the
Language-Artifacts-Methodology-Training (LAM/T) layer that governs subsequent agent behaviour.
Sessions that produce only task outputs consume it. Encode-before-act provides the session
metric: commits to `docs/`, `scripts/`, or `.github/agents/` are the operational proxy for
LAM/T layer contribution. Sessions with zero substrate commits warrant explicit justification.

**Low-K Specialization as Fleet Health Criterion (H2 × H3)**: Kauffman's NK model predicts
that agents with narrow mandates (low K) produce stable specializations and preserve
organizational identity under fleet churn. The co-equal LAM/T design pattern constrains
mandate breadth: agents deepen their specialization depth, not their mandate breadth. An agent
whose mandate has grown to span multiple substrate domains is exhibiting measurable high-K
drift — an early decoherence signal detectable before fleet instability manifests.

## 4. Theoretical Grounding and Hypothesis Validation

The four hypotheses are not independent validity probes. They form a mutually reinforcing
architecture in which each hypothesis both requires and explains at least one other; remove
any one and the remaining three weaken. We first describe the dependency structure, then
assess each hypothesis against the nearest prior art.

### 4.1 Four-Hypothesis Dependency Structure

**H4 provides CS legitimacy.** The chain Knuth (1984) → Nygard (2011) → Martraire (2019) →
AGENTS.md-class files establishes encode-before-act as the latest instantiation of a
fifty-year principle: human-readable specification asserts temporal and epistemic priority
over executable behaviour. Without H4, the methodology is a project-specific workflow
preference answerable by any reviewer who regards AGENTS.md files as informal workarounds.
With H4, it is a grounded argument in documented CS tradition. H4 is the methodology's
legitimation layer.

**H1 operationalizes H4.** The CS lineage identifies what AGENTS.md files *are*; it does not
specify when or how agents should read them. H1 supplies the behavioural prescription: before
the first action token, unconditionally, at session scope. H4 without H1 produces historical
analogy without operational force; H1 without H4 risks dismissal as an informal heuristic.
Together they constitute encode-before-act as a *grounded behavioural constraint* with both
a legitimation argument and a specific operationalization.

**H3 frames the human relationship.** The agent's primary output is not task completion but
substrate artifacts that reshape the LAM/T layer governing subsequent agent behaviour. This
inversion distinguishes *substrate-creation augmentation* from *user-performance augmentation*
— the axis described by Tong (2026). H3 also carries Bush's limiting axiom architecturally:
MANIFESTO.md is irreducibly human-authored; agents operate within it rather than regenerating
it from session context. H3 completes H2 by supplying the human role — co-author of the top
layer — that biological self-organization theory cannot generate from first principles.

**H2 explains the fleet dynamics.** H3's design values — substrate preservation, low-K
specialization, organizational closure — require a theoretical account of why they are
engineering predictions rather than preferences. Maturana and Varela's (1980) organizational
closure predicts that substrate decay produces detectable fleet decoherence. Kauffman's (1993)
NK model predicts that low-K fleet configurations outperform high-K configurations on stability
metrics. Turing's (1952) reaction-diffusion formalism predicts coherent fleet topology from
independent local encoding rules without central coordination. H2 converts H3's values into
falsifiable engineering claims with specific measurement apparatus.

### 4.2 Individual Hypothesis Assessments

**H4 — CS Design Lineage (Novel, Medium-High Confidence)**: Each step in the chain is
traceable in published sources. The terminal step — AGENTS.md as living documentation for AI
agents — has zero academic antecedent. An exhaustive arXiv search returned no results for
"literate programming AI agent workflow," "living documentation encode context LLM," or
"AGENTS.md instructions design." Dhar et al. (2026) confirm the ADR ↔ AI agent connection is
an active research frontier but operate in reverse direction — mining codebases to produce ADRs
after the fact — and draw no lineage to literate programming. H4 is the most precisely
falsifiable novelty finding: either a paper drawing this chain exists, or it does not. The
evidence strongly supports the latter.

**H3 — Augmentive Partnership (Partially Novel, High Confidence)**: The augmentation lineage
is established; Tong (2026) demonstrates it survives the transition to foundation models. H3's
gap is precise and at high confidence: no surveyed work asks what happens when AI agents
co-author the LAM/T layer that governs their own subsequent behaviour. The constraint
sub-claim is the sharpest formulation: encoding partnership as a session pre-condition —
the encode-before-act gate — distinguishes augmentation from automation at the architectural
level rather than the design aspiration level. This binary is checkable against any proposed
counterexample.

**H2 — Morphogenetic Substrate (Partially Novel, Medium-High Confidence)**: The three-framework
synthesis — Turing + Maturana and Varela + Kauffman — as a jointly applied, prescriptive fleet
design framework is absent from the surveyed literature. Fernandez (2016) applies autopoiesis
to MAS in the forward direction (fleet models an environment); H2's inversion (fleet *is* an
autopoietic system) is not present in any identified prior art. Wu and Or (2025) invoke
autopoiesis for human-AI collectives without formal operationalization of Turing or NK
mechanics. The NK model provides genuine mathematical structure for specialization tradeoffs;
K-value mapping to agent role design remains qualitative pending formal empirical validation.

**H1 — Encode-Before-Act (Partially Novel, Medium Confidence)**: The technique has no named
precedent in the surveyed literature. Mei et al.'s (2025) comprehensive survey provides the
strongest novelty signal through absence: if encode-before-act existed under a standard name,
a current wide-scope taxonomy would surface it. The Constructor phase in Xu et al. (2025) is
the closest antecedent; H1 refines rather than replaces it by specifying source (system
knowledge, not task-driven retrieval), timing (session scope, not per-query), and target
outcomes (token efficiency and session coherence). The empirical dimension — measured
advantages over a reactive reconstruction baseline — remains an open conjecture; H1's novelty
claim is currently conceptual.

### 4.3 Four-Hypothesis Mutual Reinforcement and Dependency Chain

**Corpus validation of H4 ↔ H1 ↔ H3 ↔ H2 dependency structure**: The mutual reinforcement claim in C2 rests on a specific dependency order: H4 (CS legitimacy) → H1 (encode-before-act operationalization) → H3 (substrate co-authorship framing) → H2 (fleet dynamics explanation). Each dependency is grounded in corpus evidence:

- **H4 → H1**: The fifty-year lineage (Knuth → Nygard → Martraire → AGENTS.md) identifies *what* encode-before-act is; [agent-fleet-design-patterns.md](agent-fleet-design-patterns.md) operationalizes *when* and *how* it is invoked at session scope.

- **H1 → H3**: The encode-before-act gate ensures agents receive the substrate specification before acting, making substrate co-authorship possible. Corpus reference: [agent-fleet-design-patterns.md](agent-fleet-design-patterns.md) §H1.

- **H3 → H2**: When agents co-author the substrate, system dynamics shift: substrate changes become selection pressures on subsequent behavior. Corpus reference: [dogma-neuroplasticity.md](dogma-neuroplasticity.md) §H2 Back-Propagation Protocol formalizes this feedback loop.

- **H2 → H4**: The fleet exhibits self-organized dynamics only when constrained by design principles. [methodology-review.md](methodology-review.md) §H4 establishes that these principles express fifty years of documented software engineering tradition.

**Operationalization checkpoint**: The [4,1] repetition code ensures this dependency structure is preserved across encoding layers. Cross-reference density measurement provides an algorithmic check that the chain remains intact.

## 5. Discussion

### 5.1 Novelty Assessment and H4 Verdict Qualification

The composite novelty of the four-hypothesis architecture exceeds the sum of the individual
claims. No prior work presents a prescriptive AI agent design framework that simultaneously:
grounds AGENTS.md-class files in a fifty-year CS documentation lineage (H4); specifies the
behavioural constraint activating that lineage at session scope (H1); frames the resulting
human-AI relationship as substrate-creation rather than task-performance augmentation (H3);
and derives fleet design criteria from biological self-organization theory (H2). The four layers
are independently novel at varying confidence levels; their combination — and the structural
necessity of their dependencies — is novel at high confidence.

The sharpest finding is H4's identification gap. This is not a framing difference or a
combination that is subtly absent — it is a specific conceptual chain, traceable through
published sources, that no published work has drawn. AGENTS.md-class files are the most
recent expression of Knuth's literate programming principle. That this statement can be made
with evidentiary support and has not been made before is the clearest empirical output of the
four-sprint investigation.

**Important qualification on H4**: The novelty verdict is a self-report grounded in an internal arXiv search and surveyed CS literature. External peer review by the software engineering and AI alignment research communities is required to validate that the Knuth → Nygard → Martraire → AGENTS.md lineage has not been previously identified. This is a genuine novelty claim but one that requires external validation before publication. The research record documents the identification process and search methodology; community vetting of the novelty claim is deferred to peer review.

### 5.2 Limitations and Operational Breadth Gap

**C4 Operational Implementation Breadth**: The paper claims applicability across three domains
(agent fleets, scripting automation, documentation workflows) but grounds the claim primarily
in agent fleet co-evolution within EndogenAI. External team validation remains future work: applying the full methodology to a greenfield scripting or documentation project would provide independent evidence of breadth and allow measurement of adoption barriers. The operational implementation is real; the evidence for breadth across three independent domains is partially theoretical pending external replication.

The central limitation is H1's empirical gap. The claim that encode-before-act reduces token
waste and improves session coherence is a design conjecture grounded in structural analysis of
the CS lineage, not a controlled measurement. No baseline comparison — identical task,
identical agent, with and without encode-before-act — exists in the literature or in the
present research record. Until this measurement exists, H1 is a theoretically grounded
conjecture, not an empirically validated finding. Asserting quantitative advantages without
this comparison would overstate the contribution.

H2's formalization has a parallel gap: the NK model's application to agent role design remains
qualitative. Mapping dependency graphs to Kauffman K-values and demonstrating that low-K
configurations outperform high-K configurations on stability metrics would make H2's
predictions rigorously testable. The cross-reference density check in `validate_agent_files.py`
approximates K-measurement; a formal coupling graph would constitute a rigorous
operationalization.

The H4 lineage also has one incompletely sourced link: the BDD/Specification-by-Example step
between ADRs and living documentation is present in Martraire (2019) but lacks an independent
primary source in the current corpus. Dedicated BDD sourcing — Adzic, North — would strengthen
the chain and provide a citable intermediate step.

### 5.3 Security Threat Model and Governance Gaps

**Threat Surface Acknowledgment**: Agent-driven workflows introduce new threat surfaces — fetch-source SSRF risk, prompt injection via externally-sourced content, and credential exposure through session context — that are orthogonal to the methodology's design contribution but critical for safe deployment. These are operational security concerns, not methodological flaws, but must be explicitly acknowledged as governance requirements. Corpus reference: [security-threat-model.md](security-threat-model.md) provides a formal threat catalog and mitigation strategies for agent-driven system threats. Any deployment of the endogenic methodology should incorporate the security framework as a complementary governance layer.

### 5.4 Open Empirical Questions

Five questions constitute the direct research agenda following from this framework:

1. What is the measured effect of encode-before-act on token efficiency and session coherence
   versus a reactive context reconstruction baseline?
2. Does a session's substrate ratio — commits to `docs/`, `scripts/`, or `.github/agents/` as
   a fraction of total session commits — correlate with measurable improvements in subsequent
   session quality over time?
3. Can agent dependency graphs be formally mapped to Kauffman K-values, and do low-K fleet
   configurations exhibit superior stability and specialization metrics in longitudinal study?
4. How does encoding chain fidelity, measured by cross-reference density to foundational
   documents, correlate with output quality and substrate contribution across large numbers
   of sessions?
5. At what rate is the H4 lineage being independently discovered by adjacent research
   communities? The AgenticAKM trajectory warrants active monitoring; the novelty window for
   H4 is finite.

## 6. Conclusion

We have presented the EndogenAI methodology: a prescriptive operational framework for AI agent
fleet design that connects a fifty-year software engineering documentation tradition to a
session-initialization behavioural discipline, grounded simultaneously in Engelbart's
augmentation paradigm and biological self-organization theory. The framework's primary
contribution is the identification of the CS design lineage — Knuth (1984) → Nygard (2011) →
Martraire (2019) → AGENTS.md-class files — a traceable conceptual chain establishing AI agent
context files as the most recent expression of the literate programming principle rather than
an informal workflow artifact.

The composite four-hypothesis architecture — H4 providing CS legitimacy, H1 operationalizing
it at session scope, H3 framing the human-AI relationship as substrate co-authorship, and H2
converting design values into falsifiable fleet dynamics predictions — is the framework's
structural core. No prior work presents anything resembling this combination with CI-enforced
gates, named artifact classes, and measurable fleet health criteria.

The practical consequence is immediate: AGENTS.md-class files are engineering artifacts with
a fifty-year lineage. Treating them as such — authoring them carefully, validating them in CI,
and reading them unconditionally before acting — is the operational enactment of that lineage.
The encode-before-act discipline is the mechanism by which an AI agent fleet maintains
coherence, contributes to rather than consuming its knowledge substrate, and produces outputs
whose value compounds across sessions rather than resetting at each session boundary.

## References

1. Bush, V. (1945). As We May Think. *The Atlantic Monthly*, 176(1), 101–108.
   https://www.theatlantic.com/magazine/archive/1945/07/as-we-may-think/303881/

2. Engelbart, D. C. (1962). *Augmenting Human Intellect: A Conceptual Framework*. SRI
   Summary Report AFOSR-3223. Stanford Research Institute.

3. Knuth, D. E. (1984). Literate Programming. *The Computer Journal*, 27(2), 97–111.

4. Maturana, H. R., & Varela, F. J. (1980). *Autopoiesis and Cognition: The Realization of
   the Living*. D. Reidel Publishing.

5. Kauffman, S. A. (1993). *The Origins of Order: Self-Organization and Selection in
   Evolution*. Oxford University Press.

6. Turing, A. M. (1952). The Chemical Basis of Morphogenesis. *Philosophical Transactions of
   the Royal Society B*, 237(641), 37–72.

7. Nygard, M. (2011). Documenting Architecture Decisions. Cognitect blog.

8. Czarnecki, K., & Eisenecker, U. W. (2000). *Generative Programming: Methods, Tools, and
   Applications*. Addison-Wesley.

9. Martraire, C. (2019). *Living Documentation: Continuous Knowledge Sharing by Design*.
   Addison-Wesley.

10. Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2022). ReAct:
    Synergizing Reasoning and Acting in Language Models. *arXiv*:2210.03629.
    https://arxiv.org/abs/2210.03629

11. Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S.
    (2023). Generative Agents: Interactive Simulacra of Human Behavior. *arXiv*:2304.03442.
    https://arxiv.org/abs/2304.03442

12. Fernandez, J. G. (2016). Autopoiesis and Cognition in Multi-Agent Systems.
    *arXiv*:1606.00799.

13. Alicea, B., & Parent, M. (2021). Morphogenetic Frameworks for Individual Agent Cognition.
    *arXiv*:2109.11938.

14. Xu, X., et al. (2025). Everything is Context: How Context Engineering Shapes Language
    Models. *arXiv*:2512.05470. https://arxiv.org/abs/2512.05470

15. Ramirez, D. (2025). Zep: A Temporal Knowledge Graph Architecture for Agent Memory.
    *arXiv*:2501.13956. https://arxiv.org/abs/2501.13956

16. Franco, R., & Gomes, L. (2024). NK Coevolution in Social Physics. *arXiv*:2408.06434.

17. Mei, H., et al. (2025). A Survey of Context Engineering for Large Language Models.
    *arXiv*:2507.13334. https://arxiv.org/abs/2507.13334

18. Berry, J. (2025). Productive Augmentation as Cognitive Mode in Human-AI Systems.
    *arXiv*:2512.12371.

19. Wu, C., & Or, Y. (2025). Autopoietic Human-AI Agent Collectives. *arXiv*:2505.00018.

20. Tong, M. (2026). From Engelbart to Foundation Models: The Augmentation Lineage in
    Contemporary AI. *arXiv*:2601.06030.

21. Dhar, S., et al. (2026). AgenticAKM: Automated Knowledge Management with LLM Agents.
    *arXiv*:2602.04445.
