---
title: "Corpus Back-Propagation — Phase 2 Proposal"
sprint: "2026-03-12-corpus-backprop"
generated: "2026-03-12"
---

# Corpus Back-Propagation — Phase 2 Proposal

## Proposal Summary

| Target paper | Entry count | Top signal type |
|---|---|---|
| values-encoding.md | 6 | Quantitative empirical (H4 fleet-layer ground truth) |
| bubble-clusters-substrate.md | 5 | Quantitative empirical (CRD calibration constants) |
| endogenic-design-paper.md | 6 | Quantitative empirical (H2 formal emergence model) |

---

## values-encoding.md Proposals

---

**Source doc**: [holographic-encoding-empirics.md](../research/neuroscience/holographic-encoding-empirics.md)
**Target paper**: values-encoding.md
**Target section**: `### H4 — Holographic Encoding is Feasible`
**Proposed change**: Update the final paragraph (starting "Algorithmic feasibility: A measurement script exists...") to replace "empirical validation showing that density correlates with output quality remains pending. This prevents H4 from being validated as 'confirmed'; the hypothesis remains plausible but awaiting empirical grounding" with a one-sentence forward-reference to holographic-encoding-empirics.md establishing the fleet baseline (49-file census, mean density 0.85) and qualifying the [4,1] confirmation: holds at fleet layer collectively; individual-file holographic reconstruction requires density ≥2.5, currently achieved by 6.1% of the fleet.
**Link-out**: holographic-encoding-empirics.md § Fleet Density Distribution (mean 0.85, ≥2.5 threshold, 6.1% coverage)
**Rationale**: H4 currently says "empirical validation pending"; holographic-encoding-empirics.md (Final, 2026-03-10, research_issue #169) directly closes this gap with a fleet-wide census, making the "plausible but awaiting" qualifier factually stale and enabling a more precise hypothesis verdict.

---

**Source doc**: [semantic-holography-language-encoding.md](../research/neuroscience/semantic-holography-language-encoding.md)
**Target paper**: values-encoding.md
**Target section**: `### Pattern 6 — Cross-Reference Density as Fidelity Metric`
**Proposed change**: Extend the "Measurement approach" paragraph with a forward-reference sentence naming the calibrated density thresholds from semantic-holography-language-encoding.md: ≥0.4 = high fidelity, 0.2–0.4 = medium, <0.2 = drift risk — converting the existing qualitative density metric into a named threshold framework.
**Link-out**: semantic-holography-language-encoding.md § Pattern 2 (Holographic Density Formula with operational thresholds)
**Rationale**: Pattern 6 defines density as a measurement concept but provides no calibration thresholds; semantic-holography-language-encoding.md supplies the empirically derived operating ranges that make the pattern actionable rather than merely definitional.

---

**Source doc**: [values-enforcement-tier-mapping.md](../research/methodology/values-enforcement-tier-mapping.md)
**Target paper**: values-encoding.md
**Target section**: `### H3 — Programmatic Encoding is Immune to Semantic Drift`
**Proposed change**: Extend the "Caveat — coverage gap" paragraph with a forward-reference sentence quantifying the asymmetry: behavioral constraints = 54% T5 prose-only; values-specific constraints = 91% T5 prose-only — citing values-enforcement-tier-mapping.md for the complete inventory (112 constraints total, 77/112 = 69% T5) that gives the gap its empirical size.
**Link-out**: values-enforcement-tier-mapping.md § Critical Asymmetry (54% behavioral vs. 91% values T5 ratio)
**Rationale**: The H3 coverage-gap caveat correctly identifies the limitation but does not quantify it; values-enforcement-tier-mapping.md (Final, 2026-03-10, research_issue #179) provides the first exhaustive constraint enumeration showing values enforcement is structurally far weaker than behavioral enforcement, grounding H3's caveat in measurable terms rather than assertion.

---

**Source doc**: [agent-taxonomy.md](../research/agents/agent-taxonomy.md)
**Target paper**: values-encoding.md
**Target section**: `### H5 — Endogenic Inheritance Chain Maps to Biological Model`
**Proposed change**: In the "Gap identified" paragraph at the end of H5 (which discusses the missing regulatory-region equivalent), add a forward-reference sentence noting that agent-taxonomy.md formalizes a six-layer refinement of the inheritance chain (subdirectory AGENTS.md files as context-narrowing post-translational regulators; SKILL.md files as domain-specific enzymes), extending the primary paper's four-layer model to match the codebase's operational state.
**Link-out**: agent-taxonomy.md § Six-Layer Encoding Inheritance Chain (subdirectory AGENTS.md and SKILL.md as distinct layers)
**Rationale**: H5 maps only the original four biological layers; the operational AGENTS.md has adopted a six-layer chain since agent-taxonomy.md (Final, 2026-03-07) — the primary paper's model is now a simplification that needs a forward-reference to the complete specification to prevent readers from misapplying the four-layer count.

---

**Source doc**: [value-provenance.md](../research/methodology/value-provenance.md)
**Target paper**: values-encoding.md
**Target section**: `## 5. Open Questions` (item 1: Semantic drift detection)
**Proposed change**: Extend Open Questions item 1 with a forward-reference sentence introducing value-provenance.md as a complementary approach: while drift detection measures content alignment, the `governs:` YAML frontmatter annotation declares chain-of-custody (which axioms a file was derived from) — a distinct fidelity measurement dimension at 0% fleet adoption at baseline (`fleet_citation_coverage_pct = 0.0`), targeting 100% via an O(N) pure-stdlib audit pass.
**Link-out**: value-provenance.md § H3 baseline (0% fleet coverage) and Pattern P1 (`governs:` file-level provenance annotation)
**Rationale**: Open Questions item 1 covers semantic drift detection (content alignment) but does not mention chain-of-custody provenance as an orthogonal measurement dimension; value-provenance.md (Final) introduces this distinction with a concrete 0%-baseline measurement and 50-line implementation path absent from the fidelity taxonomy.

---

**Source doc**: [doc-interweb.md](../research/infrastructure/doc-interweb.md)
**Target paper**: values-encoding.md
**Target section**: `### Pattern 6 — Cross-Reference Density as Fidelity Metric`
**Proposed change**: In the "Implementation" paragraph (ending "...would provide a quantitative fidelity metric"), add a forward-reference sentence noting that doc-interweb.md addresses the complement: rather than measuring existing cross-references, `scripts/weave_links.py` + `data/link_registry.yml` programmatically inject concept links at corpus scale — the Algorithms-Before-Tokens enforcement complement to the measurement approach.
**Link-out**: doc-interweb.md § Q1 (YAML Registry approach) and R2 (weave_links.py implementation recommendation)
**Rationale**: Pattern 6 identifies cross-reference density as a fidelity metric and `generate_agent_manifest.py` as its measurement tool, but does not link to the programmatic *creation* mechanism; doc-interweb.md (Final, related issue #84) provides the missing enforcement complement that makes Pattern 6 actionable rather than only diagnostic.

---

## bubble-clusters-substrate.md Proposals

---

**Source doc**: [filter-bubble-threshold-calibration.md](../research/neuroscience/filter-bubble-threshold-calibration.md)
**Target paper**: bubble-clusters-substrate.md
**Target section**: `### Pattern B4 — Provenance Transparency as Echo-Chamber Antidote`
**Proposed change**: In the "Actionable implication" paragraph (which prescribes a 30-day rolling window audit), add a forward-reference sentence inserting the empirically calibrated CRD thresholds from filter-bubble-threshold-calibration.md as the operationalized isolation-risk levels for the flagging policy: CRD_critical=0.02 (high filter-bubble risk), CRD_warning=0.17 (drift risk), CRD_optimal=[0.32, 0.60] (Laplace equilibrium range) — from a 61-file fleet measurement.
**Link-out**: filter-bubble-threshold-calibration.md § Empirical Thresholds (CRD_critical, CRD_warning, CRD_optimal from n=61 corpus)
**Rationale**: Pattern B4 prescribes provenance auditing as the echo-chamber antidote but states no thresholds; filter-bubble-threshold-calibration.md (Final, research_issue #184) provides the only empirically measured CRD constants in the corpus, converting the pattern's actionable implication from aspirational to testably calibrated.

---

**Source doc**: [laplace-pressure-empirical-validation.md](../research/neuroscience/laplace-pressure-empirical-validation.md)
**Target paper**: bubble-clusters-substrate.md
**Target section**: `### H3 — Mathematical Bubble Properties Provide Formal Vocabulary for Substrate Stability`
**Proposed change**: At the end of the "Encoding implications" table's conclusion section, add a forward-reference sentence noting that laplace-pressure-empirical-validation.md provides R²-validated empirical confirmation of the stability formula (P2 Constraint Violation Pressure R²=0.72 vs. test pass rate p<0.001; P1 Citation Density Pressure R²=0.68 vs. task velocity) — establishing that the Laplace metaphor yields statistically predictive structural health metrics, not merely illustrative geometry.
**Link-out**: laplace-pressure-empirical-validation.md § Primary Finding (P1 R²=0.68, P2 R²=0.72, P3 R²=0.54 across 60-day, 36-file measurement)
**Rationale**: H3's Laplace pressure model is presented as structural vocabulary; laplace-pressure-empirical-validation.md (Final, research_issue #183) is the only source providing R²-grounded validation — the distinction between metaphor and predictive model depends on this citation.

---

**Source doc**: [fleet-emergence-operationalization.md](../research/agents/fleet-emergence-operationalization.md)
**Target paper**: bubble-clusters-substrate.md
**Target section**: `### H2 — Neuroanatomical Connectivity Gradients Map to Inter-Substrate Connectivity`
**Proposed change**: In the "Endogenous evidence" paragraph (which cites values-encoding.md §5 B8 Degradation Table), add a forward-reference bullet to fleet-emergence-operationalization.md as convergent endogenous evidence: the formal emergence model (`E(M) = 1 iff ≥3/4 substrate metrics exceed threshold`) with 157% fleet growth in 4 days and two independently confirmed emergence events operationalizes the "substrate differentiation under evolutionary pressure" mechanism in H2 with operational measurement independent of handoff-boundary loss data.
**Link-out**: fleet-emergence-operationalization.md § Formal Emergence Model and § Case Study Results (two confirmed, one negative control)
**Rationale**: H2's endogenous evidence cites only the B8 Degradation Table (boundary loss); fleet-emergence-operationalization.md (Final, research_issue #168) provides a distinct measurement angle (morphogenetic emergence detection) that quantifies the same connectivity-differentiation dynamic H2 asserts, strengthening the convergent evidence base.

---

**Source doc**: [topological-audit-substrate.md](../research/neuroscience/topological-audit-substrate.md)
**Target paper**: bubble-clusters-substrate.md
**Target section**: `## 5. Geometric Extension — The Nested-Cube Topology and Junction Specifications`
**Proposed change**: In the dimension table (3D/2D/1D/0D with substrate analogs), add a parenthetical forward-reference to topological-audit-substrate.md immediately after the "15 faces" row, citing the empirical face count (9 structural + 6 functional enforcement-tier faces) and 67%/33% intra/cross-subsystem edge ratio as quantitative grounding for the three-nested-cubes model's coherence claim.
**Link-out**: topological-audit-substrate.md § Structural Coherence (75V/52E/15F inventory; 67%/33% intra/cross-subsystem edges)
**Rationale**: §5's Geometric Extension describes the topology conceptually; topological-audit-substrate.md (Final, research_issue #170) provides the only complete empirical inventory of the actual face/edge/vertex structure — the mathematical model requires this measurement layer to move from assertion to grounded characterization.

---

**Source doc**: [substrate-taxonomy-content-context.md](../research/methodology/substrate-taxonomy-content-context.md)
**Target paper**: bubble-clusters-substrate.md
**Target section**: `### Pattern B3 — Evolutionary Pressure as Substrate Differentiation Rationale`
**Proposed change**: In the "Test for each substrate boundary" paragraph (after "Does each layer have a distinct stability tier, mutation rate, and authoring scope?"), add a forward-reference sentence noting that substrate-taxonomy-content-context.md formalizes a four-category orthogonal substrate classification (Content/Context/Hybrid/Regenerable Provenance) with regenerability scores and compaction policies — providing an operational taxonomy for answering the evolutionary pressure test's authoring-scope boundary question.
**Link-out**: substrate-taxonomy-content-context.md § Four-Category Orthogonal Taxonomy (Content/Context/Hybrid/Regenerable Provenance with regenerability scores)
**Rationale**: Pattern B3 prescribes the evolutionary pressure test but lacks a classification framework for executing it; substrate-taxonomy-content-context.md (Draft, research_issue #191) provides four non-overlapping substrate categories with formal closure properties that make the "distinct mutation rate and authoring scope" question answerable rather than open-ended.

---

## endogenic-design-paper.md Proposals

---

**Source doc**: [fleet-emergence-operationalization.md](../research/agents/fleet-emergence-operationalization.md)
**Target paper**: endogenic-design-paper.md
**Target section**: `### 4.2 Individual Hypothesis Assessments` (H2 paragraph)
**Proposed change**: Update the H2 assessment paragraph (ending "K-value mapping to agent role design remains qualitative pending formal empirical validation") to add a forward-reference to fleet-emergence-operationalization.md as the strongest available H2 empirical grounding: the formal emergence model `E(M) = 1 iff ≥3/4 metrics above threshold` with 157% fleet growth in 4 days and two independently confirmed emergence events — including a negative-control case (Case Study 3: only 2/4 metrics above threshold = evolution event, not emergence) that validates the multi-metric threshold structure.
**Link-out**: fleet-emergence-operationalization.md § Formal Emergence Model and § Case Study Results (Case Studies 1–3 with metric tables)
**Rationale**: H2's assessment concludes K-value mapping is qualitative pending validation; fleet-emergence-operationalization.md (Final, research_issue #168) provides formal multi-metric thresholds, three empirical case studies, and a rigorous negative-control result that elevate H2's evidentiary base from "theoretically grounded conjecture" to "empirically grounded at fleet layer" — the most significant single upgrade across all three papers.

---

**Source doc**: [external-team-case-study.md](../research/pm/external-team-case-study.md)
**Target paper**: endogenic-design-paper.md
**Target section**: `### 5.2 Limitations and Operational Breadth Gap`
**Proposed change**: In the paragraph "external team validation remains future work," extend the sentence to forward-reference external-team-case-study.md for the proxy study metrics (M2=100% post-protocol compliance across 20 sessions; M4=33/33 phase-gate adoption; ARM=5 in two independent sprint events; CONTRIBUTING.md=1,066 words), naming these as the strongest available internal-proxy evidence without removing the explicit caveat that external cold-start validation is the outstanding gap.
**Link-out**: external-team-case-study.md § Metrics M1–M5 (proxy study results; source citations for each metric)
**Rationale**: §5.2 states external validation is future work without citing any proxy data; external-team-case-study.md (Final, research_issue #167) provides five named proxy metrics that belong in the limitations section to distinguish "no evidence" from "strong internal proxies, one critical gap" — a material accuracy improvement with no argument-weakening effect.

---

**Source doc**: [external-team-case-study.md](../research/pm/external-team-case-study.md)
**Target paper**: endogenic-design-paper.md
**Target section**: `### 3.4 Pattern Catalog` (Encode-Before-Act as Artifact Activation Discipline entry)
**Proposed change**: Add a forward-reference bullet to the "Encode-Before-Act as Artifact Activation Discipline (H4 × H1)" pattern entry, linking to external-team-case-study.md Pattern 1 (Protocol-First Adoption Ladder): template-sufficiency — completing the fill-in-the-blank encoding checkpoint without theoretical understanding of H1–H3 — achieved 100% compliance across 20 sessions, providing the empirical operationalization that the H4×H1 pattern claims but does not demonstrate.
**Link-out**: external-team-case-study.md § Pattern 1 (Protocol-First Adoption Ladder — template sufficiency, NOT theory transfer)
**Rationale**: The H4×H1 pattern asserts encode-before-act as an artifact activation discipline but contains no adoption evidence; external-team-case-study.md Pattern 1 provides the empirical grounding showing that template sufficiency (not theory comprehension) is the correct operationalization mechanism for external-team H4 adoption.

---

**Source doc**: [episodic-memory-agents.md](../research/agents/episodic-memory-agents.md)
**Target paper**: endogenic-design-paper.md
**Target section**: `### 5.4 Open Empirical Questions` (Question 1: encode-before-act measured effect)
**Proposed change**: Extend Open Empirical Question #1 (effect of encode-before-act on token efficiency) to add that the controlled measurement is currently blocked by a 4-step prerequisite chain — LCF baseline (issue #131) → local compute stack → episodic memory integration (issue #13 closed with "wait" verdict) → cross-session drift detection (`validate_session.py --drift-check`) — forward-referencing episodic-memory-agents.md for the closed-with-wait verdict and naming the chain as an explicit open blocker, not merely an aspirational next step.
**Link-out**: episodic-memory-agents.md § R1 (wait verdict; prerequisite chain: LCF baseline → Cognee → validate_session.py --drift-check)
**Rationale**: Open Question #1 states the H1 empirical gap without explaining why closing it is currently impossible; the 4-step prerequisite chain from episodic-memory-agents.md (Final) makes the blockers explicit and traceable, converting an open question into a dependency-mapped priority with a clear unlock path.

---

**Source doc**: [workflow-formula-encoding-dsl.md](../research/methodology/workflow-formula-encoding-dsl.md)
**Target paper**: endogenic-design-paper.md
**Target section**: `### 3.4 Pattern Catalog` (Programmatic Governance Stack entry)
**Proposed change**: In the Programmatic Governance Stack entry (which lists validate_synthesis.py as T3 and pre-commit hooks as T4 implementation examples), add a forward-reference sentence noting that workflow-formula-encoding-dsl.md extends Algorithms-Before-Tokens to the workflow-specification layer: EBNF DSL encoding of decision logic with 81% semantic compression, deterministic round-trip validation, and ISO/IEC 14977 grammar — a protocol-level instantiation of the same principle, pending promotion from Draft status.
**Link-out**: workflow-formula-encoding-dsl.md § Case Study 1 (81% compression, EBNF grammar, round-trip validation)
**Rationale**: The Programmatic Governance Stack pattern cites CI-level check scripts as its canonical examples; workflow-formula-encoding-dsl.md provides the most quantitatively precise Algorithms-Before-Tokens demonstration in the corpus (81% compression with formal grammar) and belongs as a forward-reference in the Pattern Catalog — acknowledged as pending Draft-to-Final promotion.

---

**Source doc**: [external-values-decision-framework.md](../research/methodology/external-values-decision-framework.md)
**Target paper**: endogenic-design-paper.md
**Target section**: `## 7. Gap Analysis & Follow-Up Research` (Deployment-Layer Extension bullet)
**Proposed change**: In the "Deployment-Layer Extension" gap item (which cites external-value-architecture.md for the formal specification), extend the list item to also reference external-values-decision-framework.md as the document that formalizes the conflict taxonomy (Type 1 Axiomatic Override, Type 2 Session Injection, Type 3 Ethical Conflict, Type 4 Provenance Suppression) with an ALLOW/BLOCK/ESCALATE outcome tree — and note that this taxonomy is currently T5 prose-only governance, making programmatic enforcement (adopt-wizard + `resolve_values_conflict.py`) the outstanding gap.
**Link-out**: external-values-decision-framework.md § Four-Type Conflict Taxonomy and Decision Tree (ALLOW/BLOCK/ESCALATE; no "Outer layer wins" branch)
**Rationale**: The Deployment-Layer Extension gap item cites only the architectural specification without identifying the conflict-resolution logic layer; external-values-decision-framework.md (Final, research_issue #177) adds that logic as a distinct governance gap — making the gap item more actionable by distinguishing architecture (already specified) from conflict resolution (specified but T5-only, enforcement pending).

---

## Skipped Findings

- **methodology-synthesis.md cross-hypothesis pattern articulations** — Draft status; the four cross-hypothesis patterns (H4×H2, H4×H1, H3×H1, H2×H3) are already substantially represented in endogenic-design-paper.md §3.4 and §4.3 dependency structure; no absent gap.
- **IIT (Tononi 2012) / HBT (Pribram 2013) bibliography additions** — Sources are skim-level (iit-panpsychism) or their primary implications (spectral entropy R²=0.67) belong to ongoing empirical validation pending LCF baseline; peripheral philosophical grounding that cannot strengthen core CS legitimation claims without external validation.
- **Context amplification quantitative deltas (+40pp/+55pp/+50pp)** — Open Questions item 2 in values-encoding.md is already marked RESOLVED (2026-03-09); the calibration data strengthens a resolved item without opening a new gap; marginal value at the cost of inflating a closed resolution.
- **Sprint docs prior-art arXiv surveys (sprint-A, sprint-C, sprint-DE) for H1/H3/H4** — endogenic-design-paper.md already cites Mei et al. 2025, Xu et al. 2025, Tong 2026, and the zero-result arXiv search in §2 and §4.2; the key novelty arguments are present; adding sprint-doc-level detail would duplicate rather than weave.
- **Governor A/B/C/D four-tier taxonomy for values-encoding.md §H3** — programmatic-governors.md provides the taxonomy, but the 91% T5 ratio entry (VE-3) already captures the higher-signal empirical asymmetry from values-enforcement-tier-mapping.md at greater precision; the taxonomy table would add length without closing a gap VE-3 doesn't address.
- **Three E1/E2/E3 membrane type profiles from six-layer-topological-extension.md** — Weaving these into bubble-clusters-substrate.md Pattern B1 would extend the paper into six-layer deployment territory; the paper already acknowledges this as future work ("Deferred to Phase 2 post-adoption research"); pre-emptive specification violates scope boundaries.
- **Conservative merge principle** — No external citation found across all four Scout groups; the principle is an EndogenAI-proposed rule without independent grounding; adding an ungrounded claim to a primary paper would reduce rather than increase scientific credibility.
- **H4 external cold-start evidence** — Explicitly cannot be closed from endogenous sources; requires external validation outside current research scope.
- **BDD mid-chain link for H4 CS lineage** — Identified as an open gap in sprint-DE (between ADRs and living documentation); cannot be closed without dedicated BDD sourcing (Adzic, North) not currently in the corpus.
- **Episodic memory library (Cognee) as endogenic-design-paper.md §3 Methodology addition** — issue #13 closed with "wait for LCF baseline" verdict; proposing an architectural addition that is explicitly deferred would misrepresent the implementation state.
