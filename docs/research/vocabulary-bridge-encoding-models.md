---
title: "Vocabulary Bridge for Vertical and Horizontal Encoding Models"
status: "Final"
research_issue: "#210"
date: "2026-03-12"
---

# Vocabulary Bridge for Vertical and Horizontal Encoding Models

## 1. Executive Summary

The endogenic substrate is described by two orthogonal models. `docs/research/values-encoding.md` operates on the **vertical dimension**: values propagate downward through a six-layer inheritance chain (MANIFESTO.md → AGENTS.md → agent files → session behavior), and fidelity degrades at each transcription step. `docs/research/bubble-clusters-substrate.md` operates on the **horizontal/topological dimension**: substrates exist as bounded regions whose active boundary membranes govern signal transit, and health is measured by membrane calibration and inter-substrate connectivity gradients.

These models are orthogonal and must remain so — confirmed by `docs/research/values-substrate-relationship.md` §2.1. A substrate can have high values-fidelity with low topological connectivity ("isolated coherence") or high connectivity with low values-fidelity ("connected confusion"); the failure modes are independent. **This document does not propose merging the models.** It proposes a minimal shared vocabulary — five bridge terms — that allows a reader fluent in one model to navigate the other without importing either model's geometry-specific framing.

The vocabulary problem is real: "signal loss" in the vertical model refers to within-layer degradation through lossy re-encoding; in the topological model it refers to boundary-level rejection by an under-calibrated membrane. Using the terms interchangeably conflates two distinct phenomena and two distinct remediation strategies. Five bridge terms are proposed — *signal boundary*, *transit loss*, *preservation unit*, *substrate coherence*, and *boundary specification* — each defined at a higher abstraction level than either model's domain vocabulary, in the spirit of Sowa's shared upper ontology. The bridge terms are usable in `docs/glossary.md` entries and in prose citations; they do not replace model-specific terms in their home documents.

**Orthogonality is preserved**: bridge terms serve as navigation aids, not synonyms. Using a bridge term in a cross-model sentence is a pointer to the reader that both models have something to say about the named phenomenon — not a claim that the two models explain it the same way.

---

## 2. Hypothesis Validation

### H1 — Can a Minimal Bridge Vocabulary (≤5 Terms) Make Cross-Model Navigation Tractable Without Collapsing Orthogonality?

**Verdict: CONFIRMED**

The theoretical justification is drawn from three complementary frameworks:

**Gentner's structure-mapping theory (1983)** establishes that productive analogies preserve relational structure, not object attributes. The most useful bridge between two structural metaphors is not a renamed object from one domain ("membrane → layer") but a relational property that exists in both. Both the vertical and horizontal models describe the same underlying relational structure at different resolution levels: *something (a signal) undergoes a transformation as it crosses from one bounded region to another, and the outcome of that transformation varies by preparedness and boundary configuration*. Bridge vocabulary should name that relational structure — "signal boundary," "transit loss," "preservation unit" — not attempt to identify the membrane with the layer.

**Hofstadter's fluid analogies framework (1995)** shows that creative analogy works by identifying structural invariants (what must stay fixed across domains) and naming the slippage (where the two metaphors diverge irreducibly). The structural invariant shared by both encoding models is: *some content must survive a transformation boundary intact for the system to function correctly*. The slippage is the geometry: the vertical model's "handoff layer" is a stage in a directed lineage; the topological model's "membrane" is a bidirectional filtering interface in a network. Bridge terms name the invariant; model-specific terms name the slippage. Conflating slippage with invariant produces false cognates.

**Sowa's shared upper ontology principle (2000)** establishes that ontology bridging works through vocabulary that is *semantically upstream* of both domain ontologies — terms that both models can instantiate without one importing the other's geometry. The five proposed terms satisfy this criterion: none presupposes hierarchy (vertical model's geometry) or network topology (horizontal model's geometry). Each can be defined without reference to directionality, layering, or spatial configuration.

**On the ≤5 limit**: The constraint is functional, not arbitrary. A larger vocabulary risks creating a pseudo-model that competes with the originals for interpretive authority. Five terms are sufficient to cover the three relational categories that both models address: (1) the site of transformation (*signal boundary*), (2) the outcome of transformation (*transit loss*), (3) the content that must survive (*preservation unit*), (4) the health property of a substrate (*substrate coherence*), and (5) the act of preparing for transit (*boundary specification*). These five categories exhaust the cross-model navigation needs identified in the vocabulary collision audit in §1.

**Anti-pattern**: Proposing bridge terms that are simply renames of one model's vocabulary ("boundary = membrane"). This collapses the orthogonality by importing the topological model's geometry into the vertical model's context, or vice versa. The test for a legitimate bridge term: if substituting the bridge term for each model's domain term in a sentence produces a sentence that is equally meaningful to a reader of either model, the bridge term is domain-neutral. If it only sounds natural in one model's context, it is a false bridge.

**Canonical example**: The sentence "canonical examples must survive the transit boundary at Scout→Synthesizer" is equally interpretable by a reader of values-encoding.md (the boundary is a handoff layer in the inheritance chain where the [4,1] code must be preserved) and by a reader of bubble-clusters-substrate.md (the boundary is the Scout→Synthesizer membrane, which must be calibrated to admit labeled examples). Neither reader needs the other model to interpret the sentence; both can map it to their own domain vocabulary. This is the functional test for a working bridge term.

---

### H2 — Is docs/glossary.md the Right Artifact for the Bridge, or Is a Separate Mapping Table Needed?

**Verdict: CONFIRMED with qualification**

**`docs/glossary.md` is the correct primary location** for bridge term definitions for three reasons:

1. **Discoverability**: The glossary is the first-class reference for cross-cutting vocabulary in this repository. Readers arriving from either research document via a terminology question will reach the glossary. A separate mapping document would require an additional navigation step and risks being orphaned.

2. **Category fit**: The existing "Methodology Concepts" category in `docs/glossary.md` contains model-agnostic procedural terms (Encoding Fidelity, Signal Preservation, Cross-Reference Density) that are already used in citations to both models. Bridge terms belong in the same category alongside these terms.

3. **Boundary clarity**: Bridge terms defined in the glossary, with explicit "In values-encoding.md" / "In bubble-clusters-substrate.md" pointers in their entries, teach the reader the mapping *and* preserve the autonomy of each model. A separate mapping document would duplicate the definition prose without adding navigational value.

**Qualification — a cross-reference table is still needed, but it belongs in the research documents, not as a standalone artifact**: Each primary research document (`values-encoding.md`, `bubble-clusters-substrate.md`) should include a "Cross-Model Navigation" note in its introduction or Executive Summary that lists the bridge terms applicable to that document's domain vocabulary and points to the glossary. This approach distributes the mapping across the source documents rather than centralizing it in a third artifact that neither model natively cites. The bridge terms are anchors; the research documents provide the full context.

**Lakoff & Johnson structural metaphor implication**: The two models are structural metaphors — they map incompatible relational geometries (linear hierarchy vs. network topology) onto the same domain. Defining bridge terms in the glossary signals to readers that these terms are *cross-structural* — they do not belong to either metaphor's relational system. This is the correct framing. A standalone "mapping document" would inadvertently suggest a third model, creating interpretive confusion rather than resolving it.

---

## 3. Pattern Catalog

### Signal Boundary

**Definition**: Any point in the substrate system at which information undergoes a transformation as it moves from one bounded context to another, regardless of whether that transition is vertical (layer-to-layer in the inheritance chain) or horizontal (substrate-to-substrate at a membrane).

**In values-encoding.md**: A signal boundary corresponds to a *layer transition* in the Encoding Inheritance Chain — the point at which one substrate re-encodes content from the layer above (e.g., MANIFESTO.md → AGENTS.md). The B8 Degradation Table measures the cumulative fidelity impact across each signal boundary in the inheritance chain. Remediation focuses on source-side preparation: [4,1] redundancy encoding ensures that even after a lossy transformation, at least one of four redundant forms survives.

**In bubble-clusters-substrate.md**: A signal boundary corresponds to a *membrane* — the lower-dimensional interface at which a substrate's active filtering function determines which signals are admitted, attenuated, or blocked. The membrane is the primary site of signal loss; it applies lossy compression regardless of the intent of either side. Remediation focuses on membrane calibration: permeability specifications declare what must be admitted intact (labeled canonical examples, axiom citations) before the boundary event occurs.

**Bridge function**: A reader of values-encoding.md who encounters "membrane calibration" in bubble-clusters-substrate.md can map it to "boundary preparation for a layer transition." A reader of bubble-clusters-substrate.md who encounters "[4,1] encoding" in values-encoding.md can map it as "source-side preparation before a signal boundary." The term "signal boundary" names the phenomenon both models address, while leaving each model's specific mechanism and geometry untouched.

**Canonical example**: In the AGENTS.md §Membrane Permeability Specifications, the Scout→Synthesizer handoff is defined as requiring verbatim preservation of `**Canonical example**:` labels. From the vertical model: this is a signal boundary in the inheritance chain, and the permeability specification is the boundary-side expression of the [4,1] source-encoding requirement (Pattern 1). From the horizontal model: this is a membrane permeability calibration for the Scout→Synthesizer boundary. Both readers understand the same operational constraint; neither needs to adopt the other model's geometry.

---

### Transit Loss

**Definition**: The degradation or complete absence of a signal after it has crossed a signal boundary, quantified relative to the signal's state before the boundary event. Transit loss is *boundary-scoped*: it describes what was present before and absent after the transit, not degradation that occurs within a single substrate.

**In values-encoding.md**: Transit loss is the lossy component of *re-encoding* at each layer transition — the degree to which a downstream encoding fails to faithfully reproduce the upstream source. The B8 Degradation Table measures transit loss empirically: ~85% of axiom citations are lost at the Scout→Synthesizer boundary; 100% of labeled canonical examples are lost at the Scout→Archive boundary. The mechanism is semantic reinterpretation: each re-encoding agent introduces paraphrase, compression, or omission.

**In bubble-clusters-substrate.md**: Transit loss is the filtering action of an *under-calibrated membrane* — the portion of incoming signal that the membrane rejects or attenuates. The model attributes this to implicit compression rules (the Synthesizer compresses by default; unlabeled content is not distinguished from dispensable context) rather than to bad faith. Under-calibration means the membrane has no rule instructing it to preserve a specific signal type; the signal is treated as fungible context.

**Bridge function**: The term "transit loss" allows a sentence like "transit loss was 100% for canonical examples at the Scout→Synthesizer boundary" to be read by practitioners of either model without importing geometry-specific framings. The vertical model reader interprets the number as a re-encoding fidelity metric; the horizontal model reader interprets it as a membrane rejection rate. Both reach the same operational conclusion: the boundary must be configured to admit canonical examples. The single term prevents readers from talking past each other when discussing the same empirical measurement.

**Canonical example**: The B8 Degradation Table (values-encoding.md §5) measured 100% transit loss for anti-patterns at the Scout→Archive boundary. Both models predicted this outcome: the vertical model because anti-patterns require explicit [4,1] encoding to survive compression (Pattern 1); the topological model because the Scout→Synthesizer membrane had no permeability specification for anti-pattern labels (Pattern B1). The remediation required both source-side preparation (vertical) and boundary specification (horizontal) to close the gap — the bridge term surfaces this dual dependency.

---

### Preservation Unit

**Definition**: A discrete element of content that has been explicitly designated — through labeling, structural encoding, or formal specification — as requiring intact transit through a signal boundary. Preservation units are the objects of both the [4,1] encoding strategy (vertical) and the membrane permeability specification (horizontal).

**In values-encoding.md**: Preservation units are the content forms that the [4,1] repetition code (Pattern 1) encodes redundantly: canonical examples labeled `**Canonical example**:`, anti-patterns labeled `**Anti-pattern**:`, MANIFESTO.md axiom citations (by name + section reference), and programmatic enforcement hooks. Each form is a structurally distinct encoding of the same informational signal, ensuring that even if three of four forms are stripped at a signal boundary, one survives. Preservation units require source-side preparation; they do not survive transit automatically.

**In bubble-clusters-substrate.md**: Preservation units are the signal types that membrane permeability specifications (Pattern B1) explicitly admit. The Scout→Synthesizer membrane specification in AGENTS.md §Membrane Permeability Specifications names two preservation units: `**Canonical example**:` instances (verbatim) and MANIFESTO.md axiom citations (≥2 per compressed output). An unlabeled sentence is not a preservation unit; the membrane has no rule to admit it intact, so it is compressed or discarded.

**Bridge function**: The term "preservation unit" decouples the question of *what must survive* from the question of *how survival is enforced* — the vertical model's concern — and from *where survival is enforced* — the topological model's concern. A cross-model discussion can use "preservation unit" to agree on the subject matter (what must survive) before each model contributes its mechanism. Without this term, cross-model discussions either conflate the two mechanisms or spend tokens resolving ambiguity about the subject.

**Canonical example**: The AGENTS.md §Focus-on-Descent / Compression-on-Ascent protocol specifies two preservation units by name: `**Canonical example**:` labels and MANIFESTO.md axiom citations. From the vertical model: these are the [4,1]-encoded forms that the Scout must encode before the boundary; their loss would represent transit loss at the source encoding stage. From the topological model: these are the membrane permeability criteria that the Synthesizer membrane must admit. Both models use the same two objects as their respective preservation targets — "preservation unit" names the shared object class.

---

### Substrate Coherence

**Definition**: The compound health property of a substrate that measures both (a) its fidelity to the values and constraints inherited from upstream sources and (b) its productive connectivity to adjacent substrates. A substrate that scores high on both dimensions is coherent; deficiency in either dimension represents a distinct failure mode.

**In values-encoding.md**: Substrate coherence (vertical dimension) is approximated by *encoding fidelity* — the degree to which a substrate's content faithfully re-encodes the upstream source rather than paraphrasing, drifting, or omitting canonical constraints. High encoding fidelity without topological connectivity is "isolated coherence" (the substrate is internally consistent but self-referential). The vertical model provides the diagnostic vocabulary (B8 Degradation Table) and the remediation prescription ([4,1] encoding), but it cannot measure the connectivity dimension.

**In bubble-clusters-substrate.md**: Substrate coherence (horizontal dimension) is approximated by the compound of *membrane integrity* (the substrate is bounded; it has not collapsed into adjacent substrates) and *connectivity gradient health* (the substrate has calibrated inter-substrate projections proportional to the Allen Institute neuroanatomical parallel). High connectivity without encoding fidelity is "connected confusion" (the substrate cites MANIFESTO.md frequently but distorts its axioms). The topological model provides the diagnostic vocabulary (connectivity atlas, provenance transparency) but cannot measure the fidelity dimension.

**Bridge function**: The compound term "substrate coherence" provides a single health target that operationalizes both models simultaneously. When a substrate is diagnosed as incoherent, the bridge term prompts two diagnostic questions: (1) is this a fidelity failure (vertical — use B8 Degradation Table) or (2) a connectivity failure (horizontal — use connectivity density score)? Without the compound term, practitioners of each model may diagnose the same symptom as distinct problems requiring incompatible solutions, when in fact both remediations are required.

**Canonical example**: A Research Scout agent file that scores high on encoding fidelity (all canonical examples labeled, MANIFESTO.md axiom citations present) but has zero cross-references to AGENTS.md or any adjacent agent file is a case of low substrate coherence — specifically, a topological failure while the vertical metric is healthy. Conversely, a session scratchpad that extensively cross-references MANIFESTO.md but paraphrases axioms into vague statements has high connectivity and low fidelity — the reverse failure. "Substrate coherence" names the compound property that both models are required to fully diagnose.

---

### Boundary Specification

**Definition**: The declarative act of stating, before a signal boundary event occurs, which preservation units must survive the crossing intact and under what conditions. Boundary specification is the shared precondition for both source-side encoding (vertical) and membrane calibration (horizontal).

**In values-encoding.md**: Boundary specification is the *source-side encoding step* — the author or agent preparing to cross a layer transition must designate which content forms are preservation units (label them as `**Canonical example**:`, `**Anti-pattern**:`, or explicit MANIFESTO.md citations) so that the [4,1] repetition code can provide redundancy. Without source-side boundary specification, the [4,1] code cannot be applied: you cannot redundantly encode what you have not identified. Boundary specification precedes encoding.

**In bubble-clusters-substrate.md**: Boundary specification is the *membrane permeability calibration* — the membrane policy that names which signal types must be admitted intact. The AGENTS.md Scout→Synthesizer membrane specification is a boundary specification: it declares `**Canonical example**:` labels and ≥2 axiom citations as preservation units before any handoff occurs. Without this policy, the membrane's default behavior is lossy compression of all content equally. Boundary specification precedes transit.

**Bridge function**: The act of "boundary specification" is procedurally equivalent across both models: before a signal boundary event, declare what must survive. The vertical model answers that declaration with source-side preparation; the topological model answers it with membrane policy. A practitioner who has performed boundary specification in one model's terms can translate the result into the other model's operational expression. The bridge term eliminates the need to re-derive the intent of each model's preparatory step from first principles.

**Canonical example**: The AGENTS.md §Membrane Permeability Specifications section is a boundary specification in both models' terms simultaneously. In the vertical model: it names the preservation units that must be [4,1]-encoded in the source agent's output (Scout) before the layer transition. In the topological model: it is the membrane permeability policy for the Scout→Synthesizer boundary. Both models require exactly this artifact; they call it by different names. "Boundary specification" names the shared artifact type and allows both models to claim the same AGENTS.md section as their own instance of the concept.

---

## 4. Recommendations

- **Glossary integration (R1)**: Add all five bridge terms to `docs/glossary.md` under the "Methodology Concepts" section. Each entry should follow the format demonstrated in the Pattern Catalog above — with "In values-encoding.md" and "In bubble-clusters-substrate.md" pointers that map the bridge term to each model's domain vocabulary. This allows a reader to arrive from either model and immediately understand the cross-model mapping. Do not replace existing model-specific terms (Encoding Fidelity, Membrane, Signal Preservation) with bridge terms — the bridge terms are additive entries alongside the model-specific glossary entries.

- **When to use model-specific vs. bridge vocabulary (R2)**: Use model-specific vocabulary when writing **within** a model's home document or when the mechanism matters (e.g., explaining that [4,1] encoding is the *source-side* preparation, not just "doing boundary specification"). Use bridge vocabulary when **crossing** between models in the same sentence or section — in cross-references, in AGENTS.md operational instructions that both models inform, and in any new research document that synthesizes across the two models. The test: if a reader of only one model needs to understand the sentence, use that model's vocabulary; if a reader of either model should understand it, use bridge vocabulary.

- **Terms that must NOT be used as bridges — false cognates (R3)**: Three terms from the existing vocabulary are false cognates — they appear in both models but with critically different meanings, and using them cross-model without qualification causes interpretive error: (a) *"signal loss"* — in values-encoding.md this refers to within-layer fidelity degradation through paraphrase or omission (a gradient phenomenon); in bubble-clusters-substrate.md it refers to boundary-level membrane rejection (a threshold phenomenon). These are at different resolution levels and require different remediations. (b) *"encoding"* (standalone, without model-specific qualifier) — in the vertical model, encoding is the transcription act at each layer of the inheritance chain; in the topological model, encoding is the labeling that makes a signal element membrane-permeability-eligible. Using "encoding" without qualification in a cross-model sentence invites the false inference that [4,1] encoding and membrane permeability specification are the same mechanism. (c) *"fidelity"* (standalone) — "encoding fidelity" is a vertical-model, within-layer measure (how well a downstream layer re-encodes its parent); in the topological model, "membrane fidelity" would refer to how accurately the membrane applies its permeability rules. These are distinct operations. Use "substrate coherence" when both dimensions must be named.

- **Cross-reference updates to primary research documents (R4)**: Each primary research document should add a brief "Cross-Model Navigation" note — a single paragraph pointing from its domain vocabulary to the bridge terms in this glossary. `values-encoding.md` should note that "signal boundary," "transit loss," and "preservation unit" serve as bridge vocabulary connecting its layer-transition concepts to the topological model. `bubble-clusters-substrate.md` should note that "signal boundary," "boundary specification," and "substrate coherence" bridge its membrane and connectivity concepts to the inheritance-chain model. These notes keep the bridge terms visible to readers arriving at either primary document without requiring those documents to import each other's vocabulary.

---

## 5. Sources

- Lakoff, G., & Johnson, M. (1980). *Metaphors We Live By*. University of Chicago Press. — Structural metaphors impose incompatible relational geometries; cross-structural bridge vocabulary must not be committed to either metaphor's geometry.

- Hofstadter, D. (1995). *Fluid Concepts and Creative Analogies*. Basic Books. — Creative analogy identifies structural invariants across domains and names the slippage where metaphors diverge irreducibly; bridge vocabulary names the invariant, not the slippage.

- Gentner, D. (1983). Structure-mapping: A theoretical framework for analogy. *Cognitive Science*, 7(2), 155–170. — Productive analogies preserve relational structure, not object attributes; bridge terms name relational properties shared at the right structural level.

- Sowa, J. F. (2000). *Knowledge Representation: Logical, Philosophical, and Computational Foundations*. Brooks/Cole. — Ontology bridging works through shared upper ontology; bridge terms must be semantically upstream of both domain ontologies.

- `docs/research/values-encoding.md` — B8 Degradation Table (empirical transit loss measurements); [4,1] repetition code (Pattern 1); hermeneutical frame (Pattern 2); programmatic immunity (H3-Pattern 5). Primary vertical model source.

- `docs/research/bubble-clusters-substrate.md` — H1 membrane hypothesis (active filtering); H4 echo-chamber/isolation risk; Pattern B1 (membrane permeability calibration); Pattern B4 (provenance transparency). Primary horizontal/topological model source.

- `docs/research/values-substrate-relationship.md` — §2.1 Dimensional Structure; orthogonality confirmation; B8 integration table; layer-governed remediation strategies. Primary source for the orthogonality constraint used throughout this document.

- `docs/glossary.md` — Existing definitions for Encoding Fidelity, Encoding Inheritance Chain, Signal Preservation, Membrane (Substrate Boundary), Cross-Reference Density. Bridge terms proposed here are additive to these entries.

- `AGENTS.md` §Membrane Permeability Specifications, §Focus-on-Descent / Compression-on-Ascent — Canonical endogenous example of boundary specification appearing as membrane policy and as source-side encoding requirement simultaneously.
