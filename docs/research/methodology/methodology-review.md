---
title: "Endogenic Methodology — Prior Art and Literature Review"
status: "Final"
---

# Endogenic Methodology — Prior Art and Literature Review

> **Status**: Final
> **Research Question**: What existing methodologies, frameworks, and research most closely resemble or inform the endogenic approach? What can we learn from them?
> **Date**: 2026-03-07

---

## 1. Executive Summary

Endogenic development — scaffold from within, encode knowledge as persistent DNA, grow by absorbing external wisdom — did not emerge from a vacuum. Its three core axioms (Endogenous-First, Algorithms Before Tokens, Local Compute-First) and its biological metaphors (morphogenetic seed, tree rings, DNA) each map onto a body of prior art across computer science, systems biology, software engineering methodology, and design theory.

This review surveys six prior art domains identified in issue #9, identifies which well-validated patterns can be directly adopted into the endogenic substrate, and delineates what the endogenic approach contributes that is genuinely novel at the intersection of these traditions.

**Hypotheses submitted for validation:**

- **H1** — The endogenic approach is a synthesis of existing traditions, not a wholly original invention.
- **H2** — Biological self-organization metaphors (autopoiesis, morphogenesis, L-systems) map precisely onto endogenic concepts rather than being purely decorative.
- **H3** — The Augmentive Partnership principle is well-grounded in the augmentation tradition (Engelbart, Bush) and improves on models of autonomous agency.
- **H4** — The "encode once, reuse many" substrate strategy has an established prior art lineage in generative programming, living documentation, and literate programming.

---

## 2. Hypothesis Validation

### H1 — Endogenic Development as Synthesis

**Verdict**: CONFIRMED — with one genuinely novel contribution

The review finds that every individual component of the endogenic methodology has a prior art precedent: biological self-organization (autopoiesis, L-systems), knowledge persistence (literate programming, ADRs, living documentation), augmentive partnership (Engelbart), encode-before-act (generative programming), and local-first compute (homebrew AI stacks). Each tradition independently arrived at a version of one or more endogenic axioms.

What is **not** found in prior art is the specific synthesis: a software development methodology that (1) applies biological substrate-and-growth metaphors as *operational constraints* (not merely analogies), (2) applies them *specifically to AI-assisted development* where the agent fleet itself reads the encoded substrate, and (3) enforces these constraints through committed artifacts (scripts, agent files, CI gates) rather than through human discipline alone. The endogenic methodology is an original synthesis at this specific intersection, built on firm prior art shoulders.

### H2 — Biological Metaphors as Precise Mappings

**Verdict**: CONFIRMED — mappings are precise, not decorative

Alan Turing's morphogenesis paper (1952) established that complex, differentiated biological forms can emerge from simple, uniform initial states through reaction-diffusion dynamics. Maturana and Varela's autopoiesis (1972) established that living systems are distinguished by self-production — the system produces and maintains its own components. Lindenmayer's L-systems (1968) formalized how biological growth emerges from a seed string of rules via iterative symbol rewriting.

These three traditions map cleanly to endogenic concepts:

| Biological concept | Endogenic mapping |
|---|---|
| Turing morphogenesis — complex form from simple rules | Agent fleet capabilities emerge from simple encoded conventions in `AGENTS.md` |
| Autopoiesis — self-producing system | Each session adds artifacts (scripts, docs, guides) that the system uses to govern the *next* session |
| L-systems — growth from a seed grammar | The morphogenetic seed (AGENTS.md + scripts + agent files) is the initial string; each sprint rewrites it into richer form |
| Tree rings — density records stress and growth | Git history records decision density; dense commit weeks correspond to productive refinement sprints |
| DNA — heritable, encoding, functional | Committed agent files, scripts, and guides are heritable across sessions and directly functional |

The mappings are not analogies but operational isomorphisms — the biological concept predicts a specific behavior of the endogenic system.

### H3 — Augmentive Partnership vs. Autonomous Agency

**Verdict**: CONFIRMED — with a stronger philosophical grounding than previously documented

Vannevar Bush's "As We May Think" (1945) articulated the memex: an associative trail machine that extends human memory and cognition without replacing human judgment. Douglas Engelbart's 1962 framework "Augmenting Human Intellect" specified that the goal of human-computer systems is *augmentation* — increasing the capability of humans to approach complex problems — not replacement. Engelbart's NLS (oN-Line System) encoded this as a requirement: the system must remain under continuous human steering at every step.

The endogenic Augmentive Partnership principle — humans provide direction and judgment; the system provides deterministic execution and memory; neither works without the other — is a direct descendant of Engelbart's framework, updated for the LLM context. The autonomous agent paradigm (systems that operate without continuous human oversight) is the exact failure mode Engelbart identified and designed NLS to avoid. Endogenic development's explicit rejection of autonomous agency is therefore not a limitation — it is a principled alignment with the strongest tradition in human-computer augmentation research.

### H4 — The Encode-Before-Act Substrate Pattern

**Verdict**: CONFIRMED — lineage spans literate programming through living documentation to IaC

Donald Knuth's Literate Programming (1984) established the principle that programs should be written for humans to read, with executable code as a byproduct. The program and its explanation are a single artifact. BDD / Specification by Example (Adzic, 2011) extended this: the specification *is* the test *is* the documentation — one artifact serves all three roles. Cyrille Martraire's Living Documentation (2019) generalized further: documentation that automatically stays in sync with the code it describes, generated from the code itself rather than written separately.

Infrastructure as Code (IaC — Ansible, Terraform, Pulumi) applies the same principle to infrastructure: the system's desired state is encoded in committed artifacts (Terraform files) rather than discovered interactively (SSH into a server and run commands). Each new provisioning run reads the committed files and executes deterministically, costing zero re-discovery tokens.

The endogenic `scripts/` directory, agent files, and `AGENTS.md` are the IaC-equivalent for AI-assisted development context. The fetch-before-act posture (pre-warm the source cache before researching) is Knuth's literate programming applied to token budgets: do the encoding work once, reuse many times. The lineage is clear. The endogenic system extends this tradition into the AI context-engineering domain.

---

## 3. Pattern Catalog

### Morphogenetic Computing and Self-Organizing Systems

**Prior art**: Turing (1952), Maturana & Varela (1972), Lindenmayer (1968), Kauffman (1993), Conway (1970), von Neumann self-replicating automata.

**Endogenic alignment**: The morphogenetic seed concept is the closest operational instantiation of Turing morphogenesis in software development: a compact initial state (seed files) from which large-scale, differentiated structure grows via repeated agent application. Kauffman's NK fitness landscapes (Origins of Order, 1993) are directly relevant to how the endogenic substrate evolves — short-range coupling between conventions creates local order (agents that read the same AGENTS.md behave consistently) while long-range decoupling enables fleet diversity.

**Adopt**: The notation "morphogenetic seed" is precise and should be treated as a defined term, not a loose metaphor. Document it formally in `docs/guides/mental-models.md` with an explicit mapping to Turing morphogenesis.

**Gap**: Endogenic development currently has no explicit analog to Turing's reaction-diffusion inhibition — the mechanism by which growth in one area suppresses unwanted growth in adjacent areas. This gap manifests as unbounded agent file proliferation without a pruning rule. A `max_fleet_size` convention or a fleet-audit step would close it.

### Generative Programming and Model-Driven Development

**Prior art**: Czarnecki & Eisenecker "Generative Programming" (2000), Simonyi's Intentional Programming, OMG Model-Driven Architecture (MDA), Domain-Specific Languages (Fowler, 2010), Software Product Lines (Clements & Northrop).

**Endogenic alignment**: Generative programming — generating diverse program family members from a high-level domain model — maps to `scaffold_agent.py`: the scaffold script is a domain model (agent role, description, posture) from which a concrete agent file is generated. Czarnecki's separation of problem space (what we want) from solution space (how it is achieved) is the `AGENTS.md` / `scripts/` split: `AGENTS.md` encodes the problem space (what agents must do), `scripts/` encodes the solution space (how they do it deterministically).

**Adopt**: The term "feature model" from SPL theory labels what the `AGENTS.md` constraint system is: a feature model whose variants are agent configurations. This framing makes it easier to reason about which features are mandatory (endogenous-first), optional (web search), or mutually exclusive (no direct file-write + direct file-write).

**Gap**: The endogenic system does not yet have a feature model formal notation. A lightweight checklist in `.github/agents/AGENTS.md` specifying mandatory and optional agent capabilities would formalize what currently exists implicitly.

### Living Documentation Methodologies

**Prior art**: ADRs (Nygard, 2011), Living Documentation (Martraire, 2019), BDD/Specification by Example (Adzic, 2011), Literate Programming (Knuth, 1984), Design by Contract (Meyer), Doctest.

**Endogenic alignment**: Architecture Decision Records (ADRs) in `docs/decisions/` are the clearest prior art instantiation in the actual codebase. Each ADR encodes a decision with rationale, consequences, and status — exactly the tree-ring metaphor: the decision is visible in history, readable by any future agent, and self-describing. The `validate_synthesis.py` CI gate is a programmatic documentation contract: research documents must conform to a specified structure, enforced automatically — Design by Contract applied to documentation.

**Adopt**: Martraire's "Living Glossary" pattern — a glossary embedded in code annotations, auto-extracted at build time — applies directly to the agent manifest. `generate_agent_manifest.py` is a living glossary of agent roles. This should be surfaced explicitly in `docs/guides/agents.md` as the pattern it implements.

**Gap**: No equivalent of BDD's "Given/When/Then" for agent behavior specification. Agent files define what agents do but not the conditions under which they succeed or fail. Adding acceptance criteria in structured format (Even/When/Then or H1/H2/H3 hypothesis blocks) would close this gap and improve the evaluator-optimizer loop.

### Agent-Oriented Software Engineering (AOSE)

**Prior art**: Jennings & Wooldridge "Agent-Oriented Software Engineering" (2000), BDI model (Bratman 1987; Rao & Georgeff 1995), JADE framework, FIPA standards, Shoham's Agent-Oriented Programming (1993), Brooks' subsumption architecture (1986).

**Endogenic alignment**: The BDI (Belief-Desire-Intention) model is the closest AOSE analog to the endogenic agent model. BDI agents have: Beliefs (what the agent knows — maps to encoded `AGENTS.md` context), Desires (goals — maps to the task brief / research question), and Intentions (committed plans — maps to the agent file's instruction sequence). The endogenic approach implicitly implements BDI without inheriting the formal BDI notation.

Brooks' subsumption architecture — competency layers from reactive to deliberative, where higher layers subsume lower ones — maps to the endogenic fleet hierarchy: specialist agents (reactive, narrow-task) are subsumed by executive agents (deliberate, broad-scope). The hierarchy is not just an organogram; it is competency stratification.

**Adopt**: BDI terminology would clarify agent file authoring. An agent file has three sections: (1) Beliefs (what it knows going in — endogenous sources), (2) Desired outcomes (gate deliverables), (3) Intentions (step-by-step instructions). This aligns with existing structure but naming it explicitly aids new contributors.

**Gap**: AOSE literature emphasizes formal verification of agent interaction protocols (FIPA ACL, contract nets). The endogenic fleet has informal handoff conventions but no formal protocol verification. The `validate_synthesis.py` script is a partial analog but covers document structure, not interaction protocol. A lightweight protocol schema for `## Scout Output`, `## Synthesizer Output`, etc., in the scratchpad would be a minimal step toward formal protocol governance.

### AI in Science Fiction — Visionary Concepts

**Prior art**: Asimov's positronic robots and psychohistory (Foundation series), Vannevar Bush's memex vision ("As We May Think", Atlantic, 1945), Iain Banks' Culture Minds (Use of Weapons, 1990), Engelbart's "Mother of All Demos" (1968), Ted Nelson's Xanadu, Philip K. Dick's adaptive androids.

**Endogenic alignment**: Banks' Culture Minds are the clearest science fiction instantiation of the augmentive partnership ideal: hyperintelligent AI systems that choose to work alongside humans, providing capabilities humans cannot replicate, while humans provide ethical direction and meaning. The Culture does not optimize humans away — it amplifies what humans value. Asimov's psychohistory — encoding societal dynamics as mathematical laws that predict and constrain future evolution — is a precise metaphor for AGENTS.md: encoded behavioral laws that, applied consistently, make session outcomes predictable. Ursula Le Guin's ansible (The Left Hand of Darkness, 1969) — asynchronous point-to-point communication across light-years — maps to the scratchpad pattern: persistent, asynchronous, cross-session communication that bridges discontinuous contexts.

**Adopt**: The Culture Minds model deserves explicit documentation in `MANIFESTO.md` as a long-horizon vision target — not as an anthropomorphic aspiration, but as a specific capability profile: an AI system that enacts human values because those values are encoded in its substrate, not because it is constrained by external rules. This is what a mature endogenic substrate aspires to.

**Endogenic novelty**: No science fiction tradition anticipated the specific problem that endogenic development solves: LLM agents that lose context between sessions and must re-discover conventions every time. The "amnesia problem" unique to LLM-based development has no clean sci-fi precedent. Asimov's robots never forgot their Three Laws; Banks' Minds have perfect recall. The endogenic response to the amnesia problem — encode everything, commit everything, trust git — is a genuinely novel contribution.

### Other Strongly Relevant Prior Art

**Christopher Alexander — A Pattern Language (1977)**: 253 interconnected patterns for building environments, each with context, problem, and solution. Alexander's explicit attention to how patterns co-enable and co-require each other (a "language" of patterns vs. a list of patterns) is more sophisticated than most software pattern catalogs. The endogenic principle/axiom structure is closer to Alexander's interconnected language than to a flat checklist. Alexander's finding that patterns are self-reinforcing when applied together — the whole is more than the sum — explains why the endogenic axioms are not hierarchical but interconnected.

**The OODA Loop (Boyd, 1950s)**: Observe-Orient-Decide-Act, where Orientation (the most important node) means synthesizing prior experience, mental models, and cultural traditions before deciding. Boyd's key insight: actors with faster OODA loops and richer orientation frameworks outperform those with faster raw decision speed but thinner orientation. Endogenous-First is the Boyd Orientation node applied to agent sessions: read AGENTS.md, scratchpad, and OPEN_RESEARCH.md before acting is the OODA loop formalization for AI sessions.

**Nonaka & Takeuchi — The Knowledge-Creating Company (1995)**: The SECI model (Socialization → Externalization → Combination → Internalization) describes how tacit knowledge becomes explicit knowledge becomes organizational capability. The endogenic encode cycle is a direct SECI implementation: tacit session knowledge (Scout findings) → externalized in scratchpad → combined in synthesis document → internalized as committed AGENTS.md updates. Naming this cycle explicitly adds a validated organizational learning framework to the endogenic rationale.

**Infrastructure as Code (circa 2006–present)**: Declarative state specification (Terraform HCL, Ansible YAML) replaces interactive imperative commands (SSH + shell scripts). The key property: the committed artifact fully specifies the desired state; running it twice is idempotent; new operators can reproduce any environment. The endogenic `scripts/` directory is the IaC-equivalent for AI sessions: a committed artifact fully specifying desired context; running it twice is idempotent; a new contributor's session is reproducible from the committed files alone.

---

## 4. Recommendations

### D2 — Adopt vs. Novel Assessment

**Adopt from prior art (high-confidence, low-cost):**

1. **BDI framing for agent files** — rename sections to Beliefs / Desired outcomes / Intentions. Zero implementation cost; significant clarity gain for new contributors.
2. **Alexander's "pattern language" framing** — document that the endogenic principles form an interconnected language, not a hierarchy. Improves MANIFESTO.md comprehensibility.
3. **SECI cycle naming** — explicitly label the Scout → Synthesize → Commit cycle as a SECI instance in `docs/guides/session-management.md`. Grounds the workflow in organizational learning theory.
4. **Living Glossary pattern** — document `generate_agent_manifest.py` as an instance of Martraire's Living Glossary in `docs/guides/agents.md`.

**Genuinely novel — do not dilute:**

1. **Encode-before-act for AI sessions specifically** — no prior art source addressed LLM-specific amnesia and the response of encoding everything into committed artifacts the agent re-reads at session start. This is the core endogenic contribution.
2. **The morphogenetic seed as operational constraint** — prior art uses biological metaphors as analogies; the endogenic approach makes the morphogenetic seed a literal design requirement (you must have AGENTS.md + scripts as the seed before starting any new sprint).
3. **Agent fleet self-governance via documents agents read** — no prior AOSE framework mandated that agents read their own governance documents as the primary constraint mechanism. The endogenic practice of agents reading AGENTS.md pre-session has no precise prior art equivalent.
4. **Augmentive Partnership as a design constraint, not a value** — Engelbart articulated this as an aspiration; endogenic development encodes it as a constraint (no unconstrained autonomy, all gates require human review).

### D3 — Proposed MANIFESTO.md Additions

**Addition 1**: In the "What Is Endogenic Development?" section, after the paragraph beginning "The name comes from biology: an endogenous process is one that originates from within the organism.", add:

> **Intellectual heritage**: Endogenic development synthesizes several established traditions: Engelbart's augmentation framework (1962) supplies the Augmentive Partnership principle; Turing's morphogenesis (1952) and Maturana & Varela's autopoiesis (1972) supply the biological substrate metaphors; Knuth's literate programming (1984) and Martraire's living documentation (2019) supply the encode-once-reuse-many strategy; and Alexander's Pattern Language (1977) supplies the interconnected-principles architecture. The endogenic contribution is the synthesis of these traditions specifically for AI-assisted development, where LLM agents re-read the encoded substrate to orient each new session. See [`methodology-review.md`](./methodology-review.md) for the full prior art survey.

**Addition 2**: In the "Endogenous-First" axiom section, after the sentence "You stand on the shoulders of giants by encoding what they've built into your own substrate.", add:

> This inheritance principle has a precise biological grounding in Maturana and Varela's autopoiesis (1972): a system is autopoietic if it produces and maintains its own components. An endogenic project is autopoietic — each session produces scripts, guides, and agent files that maintain the substrate, so future sessions start richer than the ones that preceded them.

**Addition 3**: In the "Augmentive Partnership" section, after "Neither works without the other — they form a unified cognitive system", add footnote context:

> This principle is a direct descendant of Douglas Engelbart's augmentation framework ("Augmenting Human Intellect", 1962), updated for the LLM context. Engelbart's NLS required continuous human steering at every step; the endogenic fleet enforces this through phase gates and review checkpoints rather than through UI design.

### Issue #9 Close Comment

```
Resolved by docs/research/methodology-review.md (Status: Final).

Key findings:
- H1 confirmed: endogenic development is a synthesis of established traditions (autopoiesis, literate programming, living documentation, Engelbart augmentation, Alexander pattern language, IaC). All individual components have prior art.
- Genuinely novel at their intersection: encode-before-act for LLM amnesia, morphogenetic seed as operational constraint not analogy, agent self-governance via re-read documents.
- Three MANIFESTO.md additions proposed (intellectual heritage paragraph, autopoiesis note in Endogenous-First axiom, Engelbart footnote in Augmentive Partnership).
- Adopt recommendations: BDI framing for agent files, SECI cycle naming for session workflow, Living Glossary label for generate_agent_manifest.py.

Closes #9.
```
