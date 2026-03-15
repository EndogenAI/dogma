---
title: "H4 Novelty: CS Lineage of Encode-Before-Act (Literate Programming → ADRs → Living Documentation → AI Agent Context Files)"
status: Draft
---

# H4 Novelty: CS Lineage of Encode-Before-Act

## 1. Executive Summary

The H4 claim proposes that the encode-before-act principle has direct intellectual antecedents
in four recognised CS traditions: Knuth's literate programming (1984), Nygard's Architecture
Decision Records (2011), BDD/Specification-by-Example, and Martraire's living documentation
(2019). The claim is not merely that these traditions are *analogous* to encode-before-act —
it is that they constitute a traceable conceptual lineage that terminates in the AGENTS.md /
CLAUDE.md artifact class used in contemporary AI agent workflow design.

**Verdict: Novel — Medium-High Confidence.** The individual antecedents are each
well-documented and mutually connected in the literature. Martraire (2019) explicitly traces
living documentation to Knuth. AgenticAKM (Dhar et al. 2026) demonstrates LLMs generating
ADRs from codebases, proving the ADR connection to AI systems is *emerging*. What does not
exist anywhere in the surveyed literature is a paper that chains all four traditions together
and applies the resulting chain to justify AI agent context files as a principled CS artifact.
The terminal synthesis — literate programming → ADRs → living documentation → encode-before-act
for AI agents — is entirely absent. H4 is the most sharply novel finding of the methodology
deep-dive sprint precisely because the gap is not diffuse or scale-dependent: it is a specific
conceptual chain that no published work has attempted to close.

---

## 2. Hypothesis Validation

### 2.1 Is the lineage real?

Yes, and it is tighter than a loose analogy. Each step in the chain is documentable:

**Knuth (1984) → Nygard (2011)**: Knuth's literate programming established the foundational
claim that programs are written primarily for human readers; the machine is a secondary
audience. The artifact produced is simultaneously executable and explanatory — a document that
*is* the specification. Nygard's ADR format inherits this principle at the decision layer:
rather than encoding *what* the system does, ADRs encode *why* decisions were made, with
full context and rationale, before those decisions calcify into implicit assumptions. The
structural parallel is exact — both insist that human-readable rationale must be a first-class
artifact produced alongside (or before) the executable artifact.

**Nygard (2011) → Martraire (2019)**: Martraire's *Living Documentation* explicitly extends
the Knuth lineage into the continuous-delivery era. Living documentation is documentation that
is generated from, or co-evolves with, the system — it cannot fall out of sync because it is
derived from the same source. Martraire explicitly cites literate programming as the
intellectual progenitor and extends it to test suites, BDD scenarios, and code annotations.
ADRs appear in Martraire's taxonomy as decision-level living documents. The chain from Knuth
to Martraire is traceable within published sources.

**Martraire (2019) → Encode-Before-Act for AI Agents**: The AGENTS.md / CLAUDE.md artifact
class is a direct structural descendant of living documentation. These files co-evolve with
the system they describe; they are the executable specification that an AI agent reads before
issuing any action token. The analogy is not metaphorical — the *mechanism* is the same:
a human-readable artifact that governs agent behavior, lives in the repository alongside
the code, and must be read before any work begins. The single step that is absent from the
literature is the explicit identification of this structural descent.

**Czarnecki and Eisenecker (2000)** supply the generative programming frame that strengthens
the chain further: in generative programming, the specification IS the primary artifact and
generators derive executable code from it. In the endogenic methodology, the AGENTS.md and
accompanying guides are the specification from which agent behavior is derived. The conceptual
parallel is strong enough to constitute independent corroboration for the encode-before-act
direction of the chain.

### 2.2 Is the terminal step novel?

Unambiguously yes. The arXiv search — zero results for "literate programming AI agent
workflow", "living documentation encode context LLM", "AGENTS.md instructions design", or
"CLAUDE.md context file" — establishes that the AGENTS.md / CLAUDE.md artifact class has
no academic prior art as a named, analyzed artifact. AgenticAKM (Dhar et al. 2026) is the
nearest prior art: it demonstrates LLMs generating ADRs from codebases at scale, which
establishes that the ADR ↔ AI agent connection is an active research frontier. But AgenticAKM
operates in the *reverse direction* — mining existing codebases to produce ADRs after the
fact — and makes no reference to literate programming, living documentation, or a
pre-session encode-before-act discipline. The direction of the chain is inverted and the
lineage is not drawn. AgenticAKM is therefore best cited as evidence that the
encode-before-act lineage is *imminently discoverable* and likely to be closed by the
research community, which elevates the urgency of establishing it first.

### 2.3 Why does directionality matter?

This is the sharpest point of H4. The CS antecedents all share a common directionality:
*encode first, act later*. Literate programming produces the document before the compiler
runs. ADRs record the decision with full context before the team forgets the rationale.
Living documentation generates from the specification as it evolves, keeping human-readable
meaning in sync with machine-executable behavior. In every case, the human-readable artifact
has temporal and epistemic priority. The encode-before-act principle for AI agents is the
most recent instantiation of this recurring pattern. That pattern had not been named as such
before the endogenic methodology formalized it.

---

## 3. Pattern Catalog

The following table maps the four CS antecedents to the encode-before-act mechanism they
anticipate and the precise gap each one leaves before the terminal AI application step.

| Tradition | Core Artifact | Encode-Before-Act Mechanism | Gap Before AI Application |
|-----------|---------------|----------------------------|--------------------------|
| Literate Programming (Knuth 1984) | Woven document (code + prose) | Human-readable rationale is primary; machine-executable is derived | No agent-facing encoding; no session-initialization framing |
| Architecture Decision Records (Nygard 2011) | `doc/adr/NNNN-title.md` | Decision context encoded with rationale before assumptions calcify | No generalization to pre-session agent priming |
| Living Documentation (Martraire 2019) | Derived docs, annotated code, BDD scenarios | Documentation co-evolves with system; specification governs behavior | No identification of AGENTS.md as a living documentation artifact |
| Generative Programming (Czarnecki & Eisenecker 2000) | Domain-specific specification | Specification is primary; generators derive executable code | No agent-execution framing; no token economics argument |
| **Encode-Before-Act for AI Agents** (EndogenAI 2026) | `AGENTS.md`, `CLAUDE.md`, guides | Agent reads specification before issuing any action token | — (this is the terminal step) |

---

## 4. Why H4 Is the Most Novel Finding

H1, H2, and H3 each identify a gap between existing literature and the endogenic methodology,
but the gap in each case is a matter of *degree* or *framing*: the underlying concepts (context
engineering, morphogenetic development, Engelbart-style augmentation) exist in recognisable
form in published work. The novelty argument in H1–H3 rests on showing that the *specific
combination* or *application* is absent.

H4's novelty argument is structurally different: the CS lineage exists and is traceable, but
**no published work has drawn the chain**. This is not a framing gap or a combination gap —
it is an identification gap. The four traditions have been studied independently; their mutual
connection through the principle of encoding first has not been stated. The application of
that principle to AI agent context files has not been attempted. The claim is therefore
falsifiable in a much more precise way: either a paper exists that traces this chain, or it
does not. The exhaustive arXiv search produced zero results. That is a more confident
evidentiary basis than the medium-confidence assessments in H1–H3.

The practical implication is significant. If the CS lineage is established in a citable form,
it provides a principled answer to the objection that AGENTS.md-style files are informal
workarounds or tribal knowledge artifacts. They are not. They are the most recent expression
of a fifty-year pattern in software engineering in which human-readable specification is
asserted as the primary artifact and executable behavior as the derived artifact. That
argument is available now; it simply needs to be made.

---

## 5. Open Questions

- **BDD/Specification-by-Example slot**: The brief names BDD as a mid-chain link between
  ADRs and living documentation, but the Scout findings do not include a direct BDD source.
  The connection is implicit in Martraire (who dedicates significant coverage to BDD as
  living documentation in executable form). A dedicated BDD source (Cucumber docs,
  Adzic/North writings) would strengthen the chain and provide a citable intermediate step.

- **Generative Programming weight**: Czarnecki and Eisenecker (2000) provides independent
  corroboration but also raises a complication — generative programming's specification
  artifacts are domain-specific languages, not natural-language guides. The analogy holds
  structurally but the mechanism differs. A follow-up synthesis should interrogate whether
  the natural-language register of AGENTS.md files is a meaningful distinction or a
  surface-level difference.

- **AgenticAKM as threat or support**: Dhar et al. (2026) is currently cited as evidence
  that the encode-before-act lineage is *emerging*. As the LLM-generates-ADR research
  matures, it may produce papers that independently discover parts of this chain. Monitoring
  this line of work is recommended.

---

## 6. Sources

1. Knuth, D.E. (1984). Literate Programming. *The Computer Journal*, 27(2), 97–111.
2. Nygard, M. (2011). Documenting Architecture Decisions. Cognitect blog.
3. Martraire, C. (2019). *Living Documentation: Continuous Knowledge Sharing by Design*. Addison-Wesley.
4. Czarnecki, K., & Eisenecker, U.W. (2000). *Generative Programming: Methods, Tools, and Applications*. Addison-Wesley.
5. Dhar, S. et al. (2026). AgenticAKM: Automated Knowledge Management with LLM Agents. arXiv:2602.04445.
