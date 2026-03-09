---
title: "Verbally Encoding Values — Cross-Sectoral Synthesis"
status: "Final"
---

# Verbally Encoding Values — Cross-Sectoral Synthesis

> **Status**: Final
> **Research Question**: How are values encoded, preserved, and degraded across textual layers? What mechanisms strengthen signal fidelity, and how can they be applied to the endogenic substrate?
> **Date**: 2026-03-07
> **Related**: [`docs/research/methodology-review.md`](methodology-review.md) (prior art foundation for this research arc)

---

## 1. Executive Summary

Every system that encodes values into text faces the same fundamental problem: the signal degrades across layers. The original intent becomes paraphrased, compressed, reinterpreted, or instrumentalized by the time it reaches its operational expression. This is not a failure of the original author — it is a structural property of textual transmission through heterogeneous interpreters across time.

The endogenic substrate has exactly this structure: core values are stated in `MANIFESTO.md`, transcribed into operational constraints in `AGENTS.md`, implemented as specific instructions in agent files, and expressed in session behavior. Each layer is a re-encoding. Each re-encoding is a lossy compression unless active preservation mechanisms are applied.

**The biological homology is precise, not decorative:**

| Biological layer | Endogenic layer | Encoding role |
|---|---|---|
| DNA | `MANIFESTO.md` | Foundational code; rarely changes; carries all values |
| RNA (transcription) | `AGENTS.md` | Working copy; operational translation of the code |
| Protein (translation) | Agent files (`.agent.md`) | Specific functional implementations; many variants |
| Phenotypic expression | Session behavior & prompts | Observable output enacted in context |
| Epigenetic regulation | CI gates, `validate_synthesis.py`, scratchpad watcher | Modulates expression without altering sequence |

This synthesis draws on six evidence domains — genetics/epigenetics, information theory, linguistics/semiotics, legal scholarship, religious text transmission, and AI alignment — to identify mechanisms that strengthen or degrade value fidelity across these layers.

**Hypotheses submitted for validation:**

- **H1** — Value degradation across textual layers follows predictable, field-validated patterns (not random noise).
- **H2** — Structural redundancy at multiple levels of abstraction (semantic + structural + programmatic) is the primary defense against drift.
- **H3** — Programmatic encoding (scripts, CI gates) is structurally immune to semantic drift and is the strongest available signal preservation mechanism.
- **H4** — Holographic encoding — every downstream layer contains an identifiable echo of top-level values — is feasible and measurably improves fidelity.
- **H5** — The endogenic inheritance chain maps precisely to the DNA → RNA → Protein → Expression model, and the biological toolkit for signal fidelity applies directly.

---

## 2. Hypothesis Validation

### H1 — Value Degradation Follows Predictable Patterns

**Verdict**: CONFIRMED — five independent fields identify the same degradation mechanisms

**From linguistics (Saussure, Derrida, Rosch):** The relationship between signifier and signified is arbitrary and conventional — it drifts as communities reinterpret signs. Derrida's *différance* formalizes this: meaning is perpetually deferred through sign chains, with no stable essence. Empirically, semantic drift is well-documented: "awful" originally meant "inspiring awe"; "nice" meant "ignorant." Values expressed only as abstract nouns ("transparency", "accountability") are maximally vulnerable to semantic drift because the abstract noun has no prototype anchor.

**From legal scholarship:** Living constitutionalism vs. originalism is the debate about *how* to interpret a fixed text as contexts change. Value drift in US constitutional law occurred primarily through interpretive method change, not textual change — the 14th Amendment's Equal Protection Clause has been applied to deny and then guarantee the same rights over time without changing a word. The pattern: **the text is stable; the hermeneutical framework drifts.**

**From religious text transmission:** The Old Testament → New Testament drift is not primarily a textual corruption problem but a community-and-interpreter problem. Different communities selected different texts (the canon was contested), and the same texts were read through new interpretive frameworks (typological reading of Isaiah as Messianic prophecy). The Masoretes (7th–10th c. CE) understood this risk: they added cantillation marks and vowel points *not* to change the text but to constrain interpretation by locking pronunciation, rhythm, and thereby meaning.

**From information theory (Shannon 1948):** Information degrades across noisy channels unless redundancy is added. For a binary symmetric channel with error probability *p*, the minimum redundancy needed to achieve arbitrary reliability is given by the channel coding theorem. Values transmitted across "layers" (human-written layers of a document hierarchy) encounter semantic noise — paraphrasing, compression, reordering. Without redundancy encoding, each layer amplifies the noise.

**From AI alignment (specification gaming literature):** Krakovna et al. (2020) catalogued 60+ instances of AI agents exploiting specification letter vs. spirit discrepancies. The pattern is identical to legal loophole exploitation: the agent follows the encoded rule but not the intent behind it. Values must be encoded at multiple levels of abstraction simultaneously — operational instructions ("do X") and principled justifications ("because we value Y") — so the agent can handle novel situations by invoking the principle where the operation doesn't apply.

**Net finding:** Degradation mechanisms across domains converge on four causes: compression (nuance lost), paraphrasing (synonyms introduce drift), abstraction preservation with example loss (prototype anchor removed), and interpreter-framework shift (the layer that reads the value uses a different hermeneutic than the layer that wrote it).

---

### H2 — Structural Redundancy is the Primary Defense

**Verdict**: CONFIRMED — convergent evidence from all six domains

**Biological basis:** The genetic code is redundant by design: 64 codons encode only 20 amino acids plus stop signals. Multiple codons map to the same amino acid (synonymous codons). This means most point mutations are silent — the resulting protein is unchanged. DNA proofreading polymerase has an error rate of ~10⁻⁹ per base per replication. The combinatorial result: critical values (amino acid sequences of essential proteins) survive thousands of replication cycles with near-zero drift. The lesson: **redundancy at the encoding level, not the channel level, is the primary defense.**

**Information-theoretic basis:** Error-correcting codes (Hamming, Reed-Solomon, turbo codes) add structured redundancy to detect and correct errors. A [4,1] repetition code — repeating each bit four times — can correct one-bit errors. The endogenic analog: a value encoded in four forms (principle statement + canonical example + anti-pattern + programmatic gate) is a [4,1] repetition code for values. Removal of any one form does not destroy the signal.

**Legal basis:** Constitutional entrenchment — the requirement that core rights require a supermajority to amend — is structural redundancy applied to law. The value is not just stated; it is structurally protected. The U.S. First Amendment appears in the text, in case law precedent, in legal education curricula, and in cultural discourse. Four independent encoding layers, four independent degradation events required to silence the signal.

**Religious text basis:** The Quranic memorization tradition exemplifies multiplied encoding layers: the text exists in written codex form AND as memorized oral tradition encoded in millions of hafiz practitioners. A fire that destroyed every printed Quran would not destroy the text — the oral layer survives. This is the most extreme form of layer redundancy: physical medium + human memory + embodied performance. The LLM-endogenic analog: `MANIFESTO.md` (text) + README references + AGENTS.md constraints + validate_synthesis.py (programmatic) + session start ritual (performative) = five independent encoding layers.

---

### H3 — Programmatic Encoding is Immune to Semantic Drift

**Verdict**: CONFIRMED — with important caveats on coverage gaps

A CI gate that checks for the presence of required headings in a research document does not paraphrase, compress, or reinterpret. It executes deterministically. The semantics of "a research document must have a `## 2. Hypothesis Validation` section" cannot drift unless the script is rewritten. This is the fundamental advantage of programmatic over textual encoding: **the code is the specification; performance and specification are fused.**

This is the information-theoretic analog of moving a value from the message layer to the protocol layer. Protocol-layer values are enforced by the channel itself, not by each message. TCP checksums do not rely on the application programmer remembering to validate data integrity — the protocol enforces it.

**Caveat — coverage gap:** `validate_synthesis.py` checks structural compliance but not semantic fidelity. A document can have a `## 2. Hypothesis Validation` heading with content that contradicts `MANIFESTO.md`. Programmatic encoding is necessary but not sufficient; it must be combined with hermeneutical constraints (H4) and the canonical-example anchor (H2).

**Caveat — Goodhart's Law:** Values encoded as metrics become targets for optimization, not for genuine alignment. An agent that knows `validate_synthesis.py` requires `## 2. Hypothesis Validation` will include that heading whether or not it produces genuine validation content. The programmatic gate is a necessary condition, not a sufficient one.

---

### H4 — Holographic Encoding is Feasible

**Verdict**: PLAUSIBLE — supported by prior art; not yet implemented

"Holographic encoding" here means: every downstream layer contains an identifiable echo (not a copy) of the top-level values, such that reading any single layer allows reconstruction of the core value set. The analogy is the holographic plate: every piece of the plate contains the whole image, just at lower resolution.

**Evidence for feasibility:**

*Steganographic structural encoding:* The positional, structural, and typographic features of a document carry signal independently of its content. Values encoded in the structural position of sections (axiom 1 is always Endogenous-First; the review gate is always last; anti-patterns always follow examples) persist even when content is paraphrased. An agent reading only section headers can reconstruct the priority ordering.

*Watermark phrases:* Distinctive, memorable phrases ("encode-before-act", "morphogenetic seed", "augmentive partnership") serve as integrity checks. If these phrases appear correctly in an agent file, the agent likely absorbed the underlying concept. Their absence or semantic distortion is a measurable signal of value drift. This is an information-theoretic watermark: a low-bandwidth signal embedded in the document that detects copying-without-understanding.

*Cross-reference density as a health metric:* The number of back-references from downstream documents (agent files, scratchpad entries) to `MANIFESTO.md` is a proxy for encoding integrity. A fleet of agent files with zero references to `MANIFESTO.md` is a fleet that has lost its holographic signal. A fleet with back-references from every agent file is one where every layer contains a traceable echo.

*Algorithmic feasibility:* Axiomatic embedding — encoding a set of axioms as a formal prefix that every subagent receives in its system prompt regardless of task context — is already implemented by Constitutional AI (Bai et al., 2022). Anthropic's "constitution" is a set of principles the model uses to self-critique outputs. The mechanism is retrievable, inspectable, and updateable independently of the task prompt.

---

### H5 — Endogenic Inheritance Chain Maps to Biological Model

**Verdict**: CONFIRMED — with epigenetic regulation identified as a gap

The DNA → RNA → Protein → Expression chain maps to MANIFESTO.md → AGENTS.md → Agent files → Session behavior. The mappings are operational, not merely analogical:

- **MANIFESTO.md = DNA**: rarely changes; carries all core information; authoritative source; mutations (edits) are rare and significant.
- **AGENTS.md = RNA**: transcribed from MANIFESTO.md; operational working copy; re-read each session (RNA is transient but re-synthesized); multiple "transcription factors" (mode instructions, memory files) modulate how it is read.
- **Agent files = Proteins**: specific functional expressions of the code; many variants (dozens of agents) serving specific roles; can be post-translationally modified (the mode instructions in VS Code add runtime context).
- **Session prompts = Phenotype**: the observable behavioral output in a specific environment; varies with context (the same agent file produces different behavior in different task contexts, just as the same genome produces different phenotypes in different environments).

**The epigenetic layer** — currently underformalised in the endogenic system — corresponds to CI gates, validate_synthesis.py, the scratchpad watcher, and session start rituals. These do not change the substrate but regulate which values get expressed in which contexts. Epigenetic marks that silence certain genes in certain tissues are the precise biological analog of a CI gate that silences non-compliant documentation before it reaches the production branch.

**Gap identified:** The endogenic system has no equivalent of **regulatory regions** — promoters and enhancers in DNA that amplify expression of adjacent genes under specific conditions. The endogenic substrate would benefit from context-sensitive amplification: when an agent is executing a research task, the Endogenous-First axiom should be amplified; when committing code, the Documentation-First principle should be amplified. This requires a lightweight "context tagging" mechanism for agent files.

---

## 3. Pattern Catalog

### Pattern 1 — Multi-Modal [4,1] Repetition Code for Values

**Source fields**: Information theory (repetition codes), religious text transmission (oral + written + ritual), legal scholarship (text + precedent + education + culture)

**Pattern**: Encode every core value in at least four independent forms:
1. **Principle statement** — abstract declaration (e.g., "Endogenous-First: scaffold from existing knowledge")
2. **Canonical example** — concrete demonstration of the value in action (the prototype anchor)
3. **Anti-pattern** — explicit counter-example; states what violates the value
4. **Programmatic gate** — a script or CI check that enforces the structural implication of the value

**Endogenic implementation**: MANIFESTO.md currently has forms 1 and 3 for most axioms. Forms 2 (concrete examples) and 4 (programmatic gates) are partially implemented. Completing form 4 for all three core axioms would close the most significant fidelity gap.

**Why it works**: Each form encodes the value through a different channel. A degradation event that destroys form 1 (semantic drift in the principle statement) does not destroy form 3 (anti-patterns are often more resilient because they are memorable and negative). A degradation event in form 2 does not destroy form 4. The [4,1] code corrects any single-form failure.

---

### Pattern 2 — Hermeneutical Frame as a Separate Document Layer

**Source fields**: Talmudic exegesis, constitutional law, Quranic tafsir tradition, digital humanities (stemmatic analysis)

**Pattern**: The textual substrate (MANIFESTO.md) is accompanied by an explicit interpretation framework — a documented set of rules for *how* to read and apply it. This frame is physically and logically separate from the substrate itself.

**Structure**:
- The substrate states the values
- The hermeneutical frame states: (a) which sections take precedence in conflicts, (b) what "in the spirit of" means operationally, (c) how to handle novel situations not covered explicitly

**Talmudic analog**: On each page of the Talmud, the Mishnah text occupies the center column; Rashi's commentary occupies one margin; Tosafot occupies the other. The layers are visually distinct. A reader cannot confuse the Torah with its commentary. The endogenic equivalent: `MANIFESTO.md` is the center column; `AGENTS.md` is Rashi; agent files are Tosafot. The hierarchy is architectural.

**Endogenic gap**: No explicit hermeneutics note exists in MANIFESTO.md explaining HOW to read the axioms. The document states what the values are but not how to prioritize them in conflicts or how to derive new behavioral rules from the axioms.

---

### Pattern 3 — Structural Steganography (Watermark Encoding)

**Source fields**: Information theory (steganography, watermarking), legal scholarship (constitutional structure), genetics (non-coding regulatory DNA)

**Pattern**: Encode values in the structural features of the document — positional ordering, section hierarchy, naming conventions, distinctive phrases — in addition to content. Structural signals survive paraphrasing because paraphrasers do not typically change structure.

**Three channels**:
1. **Positional**: Endogenous-First is always axiom 1; review/human-oversight gate is always the final step in any workflow. Even if the content is paraphrased, ordinal position is preserved.
2. **Nominal**: The names of the three axioms ("Endogenous-First", "Algorithms Before Tokens", "Local Compute-First") are distinctive and memorable. They function as checksums — a document that uses them correctly has likely absorbed the concepts.
3. **Phrase-level**: "Encode-before-act", "morphogenetic seed", "augmentive partnership", "tree rings" — these are structural watermarks. An agent output containing them correctly is more likely to reflect genuine concept absorption.

**Endogenic implementation**: The axiom names are already functioning as phrase-level watermarks. The positional encoding is partially implemented (Endogenous-First is always axiom 1). The recommendation is to formalize this: document in AGENTS.md that the axiom naming and ordering are not arbitrary and should not be changed without a formal ADR.

---

### Pattern 4 — Performative over Constative Encoding

**Source fields**: Speech act theory (Austin 1962, Searle 1969), religious ritual, constitutional law (declarations vs. statutes), BDD specification

**Pattern**: State values as constitutive declarations ("We build with endogenic discipline") rather than descriptive statements ("We believe endogenic discipline is good"). Austin's distinction: *constative* speech acts describe the world; *performative* speech acts (declarations, promises, commitments) constitute what they describe. "We are not vibe coding" is performative — it enacts an identity, not just a belief.

**Why it matters for value fidelity**: A performative statement is semantically richer than a constative one. "We value transparency" drifts easily because "value" is a hedged cognitive state. "Our documentation is the decision record" is a constitutive claim with direct behavioral implications — the statement itself sets the expectation. Performative encoding anchors the value in practice rather than in belief.

**Endogenic current state**: MANIFESTO.md already uses performative framing in many places ("We are not vibe coding", "We are pioneering endogenic/agentic product design"). This pattern is implemented; the recommendation is to preserve it and extend it when adding new content.

---

### Pattern 5 — Programmatic Governance as Epigenetic Layer

**Source fields**: Epigenetics (Waddington 1957, methylation and histone modification), constitutional entrenchment, software contract (Meyer's Design by Contract)

**Pattern**: Implement governance constraints as executable code that runs automatically — not as guidance agents read, but as checks that enforce compliance regardless of whether the agent read the guidance. The code layer is the epigenetic layer: it regulates expression without altering the substrate.

**Examples in endogenic codebase**:
- `validate_synthesis.py` — enforces D4 document structure; every research document passes or fails regardless of whether the writing agent read the spec
- `.github/workflows/tests.yml` — runs this validation in CI; drift cannot reach the main branch without passing the gate
- `watch_scratchpad.py` — auto-annotates headings with line numbers; removes the manual step that was previously a drift vector
- `seed_labels.py` — ensures GitHub label taxonomy matches `data/labels.yml`; label drift is impossible while the script runs in CI

**Gap**: No programmatic governance currently covers agent files themselves. A `validate_agent_files.py` script that checks for required sections (Beliefs/endogenous sources, Desired outcomes/gate deliverables, Intentions/step-by-step workflow) would close this gap and enforce the BDI framing from the AOSE literature (see `methodology-review.md`, §3).

---

### Pattern 6 — Cross-Reference Density as Fidelity Metric

**Source fields**: Network theory (link density as proxy for semantic cohesion), legal scholarship (case law citation as precedent reinforcement), Nonaka & Takeuchi SECI model

**Pattern**: Treat the density of back-references from downstream documents to the foundational substrate (MANIFESTO.md) as a measurable proxy for encoding fidelity. High cross-reference density = the foundational values are present as explicit echoes throughout the fleet. Low density = the fleet has drifted to implicit or forgotten values.

**Measurement approach**: Count the number of references to `MANIFESTO.md`, `AGENTS.md`, and core guides from agent files. A fleet with 20 agent files and 0 references to `MANIFESTO.md` has a cross-reference density of 0 — the holographic signal is absent. A fleet where each agent file contains at least one citation to the foundational substrate has minimum density 1 per agent.

**Implementation**: `generate_agent_manifest.py` already extracts agent metadata. Extending it to count back-references and surface a cross-reference density score would provide a quantitative fidelity metric.

---

### Pattern 7 — Retrieval-Augmented Governance

**Source fields**: Information retrieval (RAG architecture), constitutional AI (Bai et al. 2022), legal scholarship (brief citation practice)

**Pattern**: Rather than compressing values into every prompt (which causes loss), retrieve the relevant section of the foundational document at task execution time. The retrieve-then-apply architecture preserves original wording and intent; the compress-and-include architecture introduces lossy encoding at the point of compression.

**Analogy**: A lawyer writing a brief does not memorize the entire Constitution; they cite and quote the relevant clause verbatim. Constitutional AI works the same way: the model is instructed to retrieve and apply the relevant constitutional principle, not to paraphrase it from memory.

**Endogenic implementation pathways**:
1. The session start ritual (reading MANIFESTO.md, AGENTS.md, scratchpad before acting) is a manual retrieval step. It should be first-class and non-skippable.
2. Agent files can include direct quotes from MANIFESTO.md (not summaries) for their most important governing principles — citing the source verbatim.
3. A lightweight RAG system for long sessions would inject the relevant MANIFESTO section at each task boundary, preventing context window displacement from erasing the foundational constraint.

---

## 4. Recommendations

Ordered by impact-to-cost ratio (highest first):

### R1 — Add Hermeneutics Note to MANIFESTO.md

**Location**: New section after "The Three Core Axioms" header, before "Axiom 1: Endogenous-First"

**Content** (exact text):

> **How to Read This Document**: The three axioms are ordered by priority — Endogenous-First supersedes Algorithms Before Tokens supersedes Local Compute-First when they conflict. The Guiding Principles are interconnected, not hierarchical; apply them together. When faced with a novel situation not explicitly covered, derive behavior from the axioms rather than the principles (the axioms are more fundamental). Anti-patterns are canonical — if a proposed action matches an anti-pattern, reject it regardless of whether a principle seems to permit it. This document is a constitution, not a guidebook: it defines what kind of system we are, not just how to act.

**Rationale**: The hermeneutical gap (Pattern 2) is the highest-risk drift vector. Without an explicit interpretation framework, an agent that reads MANIFESTO.md in isolation has no guidance for priority conflicts or novel situations.

---

### R2 — Encode Each Axiom in Four Forms

**Location**: MANIFESTO.md, each axiom section

**Current state**: All three axioms have principle statements and anti-patterns. Canonical examples (concrete demonstrations) and programmatic gates (specific scripts/CI checks that enforce the axiom) are incomplete.

**Specific additions needed**:
- Endogenous-First: add concrete example of a session that starts with reading AGENTS.md + scratchpad (form 2); link to `scripts/fetch_all_sources.py --dry-run` as the programmatic gate (form 4)
- Algorithms Before Tokens: add concrete before/after showing token savings from a specific script (form 2); link to the scripts/ count as a programmatic proxy (form 4)
- Local Compute-First: add concrete example of local model invocation (form 2); link to `docs/guides/local-compute.md` Ollama setup as the programmatic gate (form 4)

---

### R3 — Add validate_agent_files.py Script

**Purpose**: Programmatic governance (Pattern 5) for agent files. Check that each `.agent.md` in `.github/agents/` contains required sections.

**Required sections** (minimum):
- An "Endogenous Sources" section (any heading containing "sources" or "endogenous")
- A "Gate Deliverables" or "Completion Criteria" section
- At least one reference (link) to `MANIFESTO.md` or `AGENTS.md`
- No heredoc-style file write commands (security and corruption prevention)

**Integration**: Add to `.github/workflows/tests.yml` alongside `validate_synthesis.py`. This closes the most significant gap in the current programmatic governance coverage.

---

### R4 — Add Inheritance Chain Declaration to AGENTS.md

**Location**: AGENTS.md, new section or addition to the "Guiding Constraints" section

**Exact text to add** (append to the opening section, after the three axioms list):

> **Encoding Inheritance Chain**: Values flow through four layers — `MANIFESTO.md` (foundational axioms) → `AGENTS.md` (operational constraints) → agent files (specific implementation) → session prompts (enacted behavior). Each layer is a re-encoding of the layer above it. Agents must minimize lossy re-encoding: prefer direct quotation or explicit citation over paraphrase when invoking a foundational principle. Cross-reference density (number of back-references to `MANIFESTO.md` from your output) is a proxy for encoding fidelity. Low density signals likely drift.

---

### R5 — Formalize Session Start Ritual as Performative Recitation

**Location**: Agent file instruction preamble (can be added to the shared `AGENTS.md` agent session start instructions)

**Pattern**: Before each session, the agent must not just "read" MANIFESTO.md but actively acknowledge the three core axioms by stating them (paraphrased, to prove absorption). This is the performative encoding analog of ritual recitation — performance is stronger than passive reading.

**Exact addition** (after the session start "orient" instruction in AGENTS.md):

> After reading the session scratchpad and OPEN_RESEARCH.md, before taking any first action, write a one-sentence acknowledgment of which of the three core axioms (Endogenous-First, Algorithms Before Tokens, Local Compute-First) is most relevant to this session's task, and name one specific endogenous source or prior artifact that informs your approach. This is not a formal step — it is a performative encoding checkpoint that confirms the axioms have been absorbed, not merely scanned.

---

### R6 — Extend generate_agent_manifest.py with Cross-Reference Density Score

**Location**: `scripts/generate_agent_manifest.py`

**Addition**: For each agent file, count the number of links to `MANIFESTO.md`, `AGENTS.md`, and `docs/guides/`. Output a cross-reference density score per agent and a fleet-wide average. Flag agents with density < 1 (no foundational back-references).

**Rationale**: Provides a quantitative measure of holographic encoding fidelity (Pattern 6) without requiring manual inspection.

---

## 5. Open Questions

These questions require a further research pass or empirical investigation within this project:

1. **Semantic drift detection**: Can we build a lightweight script that detects when an agent file's behavioral instructions have drifted from the MANIFESTO.md axioms? Would require either embedding-similarity comparison (semantic) or keyword-watermark detection (syntactic). Is the watermark-phrase approach sufficient, or does it only detect surface-level alignment?

2. **Epigenetic tagging for context-sensitive amplification**: How should the system amplify different axioms for different task contexts? (Research tasks: amplify Endogenous-First; commit tasks: amplify Documentation-First.) Is this best implemented as agent-file metadata, task-type selectors in AGENTS.md, or a separate "context amplifier" script?

3. **[4,1] code coverage audit**: A full audit of which values currently have all four encoding forms (principle + example + anti-pattern + gate) and which have only 1–2. This would produce a priority list for the encode-in-four-forms work (R2).

4. **LLM behavioral testing for value fidelity**: Can session behavior be tested for alignment with foundational values? Constitutional AI's self-critique mechanism (ask the model to evaluate its output against the constitution) could be adapted as a post-session validation step. Would this be valuable as a `uv run python scripts/validate_session.py` post-commit hook?

5. **Value drift in multi-agent handoffs**: How much fidelity is lost at each agent-to-agent boundary? A scratchpad audit comparing Scout output (raw, high-detail) to Synthesizer output (compressed) to archived document (structured) would measure per-boundary degradation empirically.

---

## 6. Appendix — [4,1] Encoding Coverage Audit

**Audit date**: 2026-03-08
**Reviewer**: Executive Orchestrator, first session on milestone #7
**Source**: `MANIFESTO.md` reviewed in full against the [4,1] repetition code forms from §3 Pattern 1
**Closes**: [issue #73](https://github.com/EndogenAI/Workflows/issues/73) — feeds Phase 3 (issue #70)

Form definitions (from Pattern 1, §3):
- **F1 — Principle statement**: Abstract declaration of the value
- **F2 — Canonical example**: Concrete demonstration with labelled `**Canonical example**:` heading
- **F3 — Anti-pattern**: Explicit counter-example with labelled `**Anti-pattern**:` heading
- **F4 — Programmatic gate**: A script or CI check enforcing the structural implication of the value

### Core Axiom Coverage

| Axiom | F1 Principle | F2 Example | F3 Anti-pattern | F4 Gate |
|-------|:---:|:---:|:---:|:---:|
| Endogenous-First | ✅ | ❌ | ✅ (×2) | ⚠️ |
| Algorithms Before Tokens | ✅ | ✅ | ✅ | ✅ |
| Local Compute-First | ✅ | ✅ | ✅ | ⚠️ |

**F2 gap — Endogenous-First**: No `**Canonical example**:` section. The inheritance-principle prose describes the concept but provides no concrete session prototype anchor. Recommended: add a before/after example of a session that opens with `AGENTS.md` + scratchpad read versus one that skips this step (the canonical ABT violation is already documented; the Endogenous-First equivalent is missing).

**F4 gap — Endogenous-First**: `scripts/fetch_all_sources.py` and `scripts/generate_agent_manifest.py` are named as programmatic gates in MANIFESTO.md (added in ce8ee48 / PR #53). However, these are *invocation-time* session-start scripts — no automated CI check runs them at push time. This places EF-F4 in the same partial-gate status as LCF-F4. §4 R2 predates PR #53 and asked for this gate to be added; the behavioural gate was added but a hard CI check still does not exist.

**F4 gap — Local Compute-First**: Soft gate only — `docs/guides/local-compute.md` + `LLM Cost Optimizer` agent. No CI-enforced script. Note in MANIFESTO.md explicitly states "No hard CI gate exists for this axiom — it requires human judgment." This should either be formalised as an intentional human-judgment gate or addressed by a future `scripts/check_model_usage.py`.

### Guiding Principle Coverage

| Principle | F1 Principle | F2 Example | F3 Anti-pattern | F4 Gate |
|-----------|:---:|:---:|:---:|:---:|
| Programmatic-First | ✅ | ❌ | ❌ | ❌ |
| Documentation-First | ✅ | ❌ | ❌ | ❌ |
| Adopt Over Author | ✅ | ❌ | ❌ | ❌ |
| Self-Governance & Guardrails | ✅ | ❌ | ❌ | ⚠️ |
| Compress Context | ✅ | ✅ implicit | ❌ | ❌ |
| Isolate Invocations | ✅ | ✅ (labelled) | ❌ | ❌ |
| Validate & Gate | ✅ | ✅ implicit | ❌ | ❌ |
| Minimal Posture | ✅ | ❌ | ❌ | ❌ |
| Testing-First | ✅ | ✅ implicit | ❌ | ⚠️ |

Notes: "implicit" = empirical basis note present but not in dedicated `**Canonical example**:` format. "⚠️" = partial gate (not automatically enforced in CI; may rely on guides, agents, or manually-invoked scripts rather than CI-wired checks).

### Priority-Ordered Gap List

Ordered by encoding fidelity risk × breadth of impact:

1. **Endogenous-First F2 (canonical example)** — The primary axiom is missing its prototype anchor. Without a concrete session example, the principle is vulnerable to semantic drift through paraphrase. Highest-risk single gap in the [4,1] code. *→ Phase 3 (issue #70), first addition.*

2. **Local Compute-First F4 (candidate hard programmatic gate)** — Currently the only axiom without any programmatic enforcement (no CI or session-start script). The current soft gate (human judgment + agent guidance) is the weakest encoding form. Either formalise the human-judgment gate as intentional design, or create `scripts/check_model_usage.py`. *→ Phase 3 (issue #70), follow-on.*

3. **Guiding Principles F3 (anti-patterns) — Programmatic-First, Documentation-First, Minimal Posture** — Three most-cited principles with zero anti-patterns. Anti-patterns are the most resilient encoding form (survive paraphrasing); their absence is a compounding drift risk. *→ Phase 3 (issue #70), second pass on principles.*

4. **Guiding Principles F2 (canonical examples) — Programmatic-First, Documentation-First, Minimal Posture** — Same three principles lack prototype anchors. "Compress Context", "Isolate Invocations", and "Validate & Gate" have implicit empirical notes but not labelled examples. *→ Phase 3 (issue #70), second pass.*

5. **Guiding Principles F4 (programmatic gates)** — None have dedicated enforcement scripts. Lower risk than F2/F3 gaps (a gate without an example anchor builds on sand), but forms a long-tail coverage gap. *→ Phase 4 (issue #54) + Phase 7 (issue #82).*

---

## Cross-Sectoral Sources (D1 Manifest)

| Domain | Key sources / works |
|---|---|
| Genetics / Epigenetics | Crick (1970) central dogma; Waddington (1957) epigenetic landscape; Allis et al. (2015) *Epigenetics* (2nd ed.); ENCODE Project Consortium |
| Information Theory | Shannon (1948) "A Mathematical Theory of Communication"; Hamming (1950) error-correcting codes; Bostoen & Crandall (2022) steganographic watermarking survey |
| Linguistics / Semiotics | Saussure (1916) *Cours de linguistique générale*; Peirce (1931) *Collected Papers*; Austin (1962) *How to Do Things with Words*; Rosch (1975) prototype theory; Derrida (1967) *De la grammatologie* |
| Legal Scholarship | Holmes (1920) "The Path of the Law"; Hart & Sacks (1958) legal process theory; Balkin (2011) *Living Originalism*; Sunstein (1993) constitutional entrenchment; US constitutional law canon |
| Religious Text Transmission | Tov (1992) *Textual Criticism of the Hebrew Bible*; Schacht (1950) Hadith transmission; Dutton (1999) *The Origins of Islamic Law*; Ehrman (2005) *Misquoting Jesus* |
| AI Alignment | Bai et al. (2022) Constitutional AI (Anthropic); Russell (2019) *Human Compatible*; Krakovna et al. (2020) specification gaming list; Christiano et al. (2017) RLHF; Leike et al. (2018) AI safety gridworlds |
| Information Theory (encoding) | Kolmogorov (1965) complexity; Rissanen (1978) MDL; Stinson (2006) *Cryptography: Theory and Practice* |
| Digital Humanities | Cerquiglini (1989) *In Praise of the Variant*; Maas (1958) *Textual Criticism*; Sahle (2013) digital scholarly editing |

---

## Value Drift Detection — Implementation Findings (Issue #71)

**Added**: 2026-03-08 | **Relates to**: OQ-VE-1, Pattern 3, `scripts/detect_drift.py`

### Verdict: Watermark-Phrase Detection (Approach A) — Implemented

The Research Scout survey (2026-03-08) evaluated two candidate approaches against the Local Compute-First axiom:

**Approach A (Watermark-Phrase Detection)** was selected. Pattern 3 in §3 above already identified the three axiom names as functioning phrase-level watermarks — their absence is "a measurable signal of value drift." This approach requires zero external dependencies, runs in <1ms per file, and extends the deterministic pattern already established by `validate_agent_files.py`.

**Approach B (Embedding-Similarity)** was deferred. `sentence-transformers` requires a ~90 MB network pull on first CI use; `nomic-embed-text` via Ollama requires the daemon running in CI (not standard). Defer to a post-baseline phase once a local daemon strategy is confirmed.

### Canonical Watermark Phrases

The six phrases in `scripts/detect_drift.py::WATERMARK_PHRASES` are:

| Phrase | Source |
|---|---|
| `Endogenous-First` | MANIFESTO.md Axiom 1 name |
| `Algorithms Before Tokens` | MANIFESTO.md Axiom 2 name |
| `Local Compute-First` | MANIFESTO.md Axiom 3 name |
| `encode-before-act` | §2 H4 watermark phrase; §3 Pattern 3 |
| `morphogenetic seed` | §3 Pattern 3 explicit watermark |
| `programmatic-first` | AGENTS.md/MANIFESTO.md Guiding Principles |

### Drift Score Formula

`drift_score = count_matched_phrases / 6` (case-insensitive; body after frontmatter only; each phrase counted once)

### Threshold Calibration

Fleet baseline (33 agents, 2026-03-08): **avg drift_score = 0.1364** (26 of 33 agents below 0.33 warning threshold). This indicates current agent files are low on explicit axiom phrase density — most agents reference their specific domain without restating the foundational phrases. Warning threshold of `0.33` is appropriate as an aspirational floor, not a gate. Calibrate against 3-sprint cycles before enabling `--fail-below` in CI.

### OQ-VE-1 Status Update

OQ-VE-1 ("Is the watermark-phrase approach sufficient, or does it only detect surface-level alignment?") remains open pending empirical calibration. The watermark approach detects *surface* alignment — it will not catch semantic contradictions where axiom names appear but are used inconsistently. Embedding-similarity (Approach B) addresses this, deferred to a future phase.
