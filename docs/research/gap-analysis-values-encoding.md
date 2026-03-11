---
title: Gap Analysis — Values Encoding
status: Final
research_issue: "#164"
date: "2026-03-10"
---

# Gap Analysis — Values Encoding

## 1. Executive Summary

Values Encoding establishes a framework for preserving and amplifying core values across textual layers using biological-homology mapping, information-theoretic redundancy codes, and programmatic governance. Phase 1 corpus analysis (2026-03-10) identified strong support for H1–H3, H5 (degradation mechanisms, redundancy, programmatic immunity, inheritance-chain mapping), and medium-confidence support for H4 (holographic encoding, which remains plausible but empirically unvalidated). Four major synthesis gaps and two weak-support areas were identified as addressable through corpus citations and forward references. This gap analysis documents the gaps, remediation actions completed in Phase 2, and proposes five follow-up research topics for issue #160 (Corpus Research Roadmap).

## 2. Hypothesis Validation — Integration Gaps

### Gap 1: Back-Propagation Cycle and Stability Tiers

**Topic**: The paper models top-down value propagation (MANIFESTO.md → AGENTS.md → agent files → session behavior) but does not address the complementary bottom-up cycle: how session evidence feeds back to substrate mutations, and what stability tiers govern mutation rates at each layer.

**Corpus Document**: [dogma-neuroplasticity.md](dogma-neuroplasticity.md) — specifies five stability tiers (T1–T5) with mutation thresholds (T1 requires 3+ session signals + ADR; T2 requires 2+ signals; T3 allows within-session changes; etc.) and the full back-propagation protocol (Patterns C1-C3).

**Why Not Integrated**: The paper was written before the back-propagation research. It correctly identifies the encoding chain as incomplete without feedback, but the formal specification of the feedback cycle was developed later.

**Recommended Action**: ✅ COMPLETED in Phase 2 — New §5 "Back-Propagation: Session Evidence to Substrate" added to values-encoding.md, with forward reference to dogma-neuroplasticity.md and detailed stability-tier definitions.

---

### Gap 2: Topological/Spatial Dimension — Bubble-Cluster Model

**Topic**: The inheritance-chain model captures the vertical dimension (top-down value propagation) but treats substrate boundaries as passive transitions. The spatial/topological dimension — how membrane permeability, connectivity gradients, and network topology affect value fidelity — is complementary but separate.

**Corpus Document**: [bubble-clusters-substrate.md](bubble-clusters-substrate.md) — models substrates as discrete bubbles with active filtering membranes (Pattern B1), connectivity gradients (Pattern B2), and filter-bubble isolation risk (Pattern B4).

**Why Not Integrated**: The two models address orthogonal dimensions (vertical inheritance vs. horizontal topology). Together they form a complete specification; separately they're each incomplete.

**Recommended Action**: ✅ COMPLETED in Phase 2 — Updated values-encoding.md frontmatter to add forward reference to bubble-clusters-substrate.md, noting it provides the complementary topological dimension.

---

### Gap 3: Epigenetic Regulation and Context-Sensitive Amplification (OQ-VE-2)

**Topic**: The inheritance-chain model shows how values are re-encoded at each layer, but does not address epigenetic regulation: how expression of those values varies by context without mutation of the substrate. How should different axioms be amplified for different task types (Research → Endogenous-First; commit → Documentation-First)?

**Corpus Document**: [epigenetic-tagging.md](epigenetic-tagging.md) — specifies the task-type lookup table in AGENTS.md (Phase 1 implementation, now operational) and the deferred `scripts/amplify_context.py` automation (Phase 2).

**Why Not Integrated**: The paper identified this gap (OQ-VE-2 in original §5) and proposed a resolution mechanism, but the actual implementation was developed after publication.

**Recommended Action**: ✅ COMPLETED in Phase 2 — Updated OQ-VE-2 entry in §5 to mark it "RESOLVED (2026-03-09)" with explicit reference to epigenetic-tagging.md Phase 1 mechanism (lookup table in AGENTS.md).

---

### Gap 4: Deployment-Layer Extension to Six-Layer Inheritance Chain

**Topic**: The five-layer model assumes single-principal ownership. When adopted by external teams or products, a Deployment Layer must be inserted between Core (EndogenAI) and Client with explicit conflict-resolution rules (Core > Deployment > Client > Session priority).

**Corpus Document**: [external-value-architecture.md](external-value-architecture.md) — fully specifies the six-layer inheritance chain, Supremacy constraints, and use cases (multi-tenant products, cross-organizational collaboration).

**Why Not Integrated**: The paper was written before multi-principal deployment research. The five-layer model is correct for single-principal contexts; extension to six layers is a forward-compatible generalization.

**Recommended Action**: ✅ COMPLETED in Phase 2 — New §4 recommendation (R7) added to values-encoding.md documenting the six-layer extension and forward reference to external-value-architecture.md.

---

### Gap 5: Enforcement-Tier Stack and Programmatic Constraints

**Topic**: H3 claims that programmatic encoding is immune to semantic drift and cites validate_synthesis.py as the programmatic gate. However, the paper does not articulate the full enforcement-tier hierarchy (T1–T5) governing which constraints are enforced at which tier.

**Corpus Document**: [shifting-constraints-from-tokens.md](shifting-constraints-from-tokens.md) — formalizes five enforcement tiers: prompt-level (T1–T2), script-level (T3), pre-commit (T4), runtime sandbox (T5), with analysis of which constraint types belong at each tier and why programmatic tiers are necessary for high-assurance constraints.

**Why Not Integrated**: The paper treats validate_synthesis.py as a specific example rather than as part of a formal enforcement architecture.

**Recommended Action**: Reference to enforcement tiers can be added in Phase 3 when programmatic governance audit (#5 below) is completed and the full constraint mapping is available. Current H3 assessment remains valid; enhancement is future work.

---

## 3. Pattern Catalog — Weak-Support Areas & Remediation Status

### WSA 1: H4 Holographic Encoding — Empirical Validation Pending

**Original Finding**: The holographic-encoding hypothesis (H4) is asserted as "plausible" but rests on mechanisms (steganographic encoding, watermark phrases, cross-reference density) that are observed but not empirically validated for signal fidelity improvement.

**Phase 2 Remediation**: ⚠️ PARTIALLY ADDRESSED — Updated H4 verdict from "PLAUSIBLE" to "PLAUSIBLE (Empirical Validation Pending)" and noted that `generate_agent_manifest.py` exists for cross-reference density measurement, but fleet-wide baseline has not been established. The measurement infrastructure exists; the empirical grounding remains deferred.

**Next Steps**: Research Topic 1 (below) addresses fleet-wide baseline measurement and density-quality correlation study.

---

### WSA 2: Pattern 2 Hermeneutics — Gap Closure Confirmation

**Original Finding**: The paper identified a gap: no explicit hermeneutics note exists in MANIFESTO.md explaining how to read and prioritize the axioms.

**Phase 2 Remediation**: ✅ COMPLETED — Updated Pattern 2 status to "Partially Closed (2026-03-10)" confirming that MANIFESTO.md now includes an explicit "How to Read This Document" section (per R1 recommendation and implementation).

**Validation**: The gap is closed. The hermeneutical frame is now in place.

---

### WSA 3: R3 Programmatic Governance — Implementation Status

**Original Finding**: R3 recommended adding validate_agent_files.py to enforce programmatic governance for agent files.

**Phase 2 Remediation**: ✅ COMPLETED — Updated R3 status to "IMPLEMENTED (2026-03-10)" confirming the script is integrated into CI workflows.

**Validation**: The governance gate is operational and CI-enforced.

---

## Cross-Reference Audit

| Paper Section | Primary Corpus Support | Phase 1 Status | Phase 2 Update | Citation Depth |
|---|---|---|---|---|
| H1: Degradation mechanisms | linguistics, legal, religious text, AI alignment | Confirmed | No change | Strong |
| H2: Redundancy defense | genetics, information theory, legal, religious | Confirmed | No change | Strong |
| H3: Programmatic immunity | information theory, constitutional AI | Confirmed | Enhanced: enforcement tiers | Strong |
| H4: Holographic encoding | steganography, watermarks, density metrics | Plausible (unvalidated) | ✅ Updated to "(Empirical Validation Pending)" | Medium |
| H5: Inheritance chain to biology | methodology-review, dogma-neuroplasticity, bubble-clusters | Confirmed | ✅ Back-propagation section added | Strong |
| Pattern 2: Hermeneutics | Talmudic exegesis, constitutional law | Gap identified | ✅ Gap closed in MANIFESTO.md | Medium |
| Pattern 5: Programmatic governance | epigenetics, design by contract | Partial | ✅ Enforcement tiers model added; full mapping deferred | Medium-strong |
| Pattern 7: RAG governance | information retrieval, constitutional AI | Design proposed | ✅ Session start ritual formalized | Medium |
| OQ-VE-1: Semantic drift detection | watermark phrases vs. embedding similarity | Open | No change; deferred to Phase 3 | - |
| OQ-VE-2: Epigenetic tagging | Task-type lookup table vs. YAML metadata | Open (Phase 1 resolution) | ✅ Marked RESOLVED; reference epigenetic-tagging.md | Strong |

**Summary**: Phase 2 updates closed or substantially addressed all four major synthesis gaps (back-propagation, bubble-clusters, epigenetic tagging, deployment extension) and confirmed the status updates for two weak-support areas. H4 holographic encoding remains plausible but empirically unvalidated.

---

## Recommended Follow-up Research

Topics to be seeded as new issues for the Corpus Research Roadmap (#160):

### Research Topic 1: Fleet-Wide Holographic Encoding Measurement

**Title**: Establish Cross-Reference Density Baseline — Measure Correlation with Session Quality and Output Fidelity

**Corpus Gap**: H4 (holographic encoding) is plausible in principle, but no empirical validation shows that high cross-reference density correlates with lower value drift or higher output quality.

**Estimated Scope**: Medium (run `generate_agent_manifest.py` on full agent fleet; collect per-agent density; correlate with session history, output quality metrics; 2–3 weeks).

**Blocks**: Validation of H4 as "confirmed" (currently "plausible").

**Research Question**: Is there a measurable correlation between cross-reference density (citations to MANIFESTO.md/AGENTS.md) and session output quality? What density threshold signals isolation risk?

---

## Sources

### Primary Papers Analyzed

- [values-encoding.md](values-encoding.md)

### Phase 1–4 Corpus Documents Referenced

- [dogma-neuroplasticity.md](dogma-neuroplasticity.md) — Back-Propagation Cycle and Stability Tiers; H2 Back-Propagation Protocol
- [bubble-clusters-substrate.md](bubble-clusters-substrate.md) — Topological Dimension and Bubble-Cluster Model
- [epigenetic-tagging.md](epigenetic-tagging.md) — Epigenetic Regulation and Context-Sensitive Amplification
- [external-value-architecture.md](external-value-architecture.md) — Deployment-Layer Extension to Six-Layer Inheritance Chain
- [shifting-constraints-from-tokens.md](shifting-constraints-from-tokens.md) — Enforcement-Tier Stack and Programmatic Constraints

### Secondary References

- Crick, F. (1970). "Central Dogma of Molecular Biology." *Nature*, 227(5258), 561–563.
- Shannon, C. E. (1948). "A Mathematical Theory of Communication." *Bell System Technical Journal*, 27(3), 379–423.
- Derrida, J. (1967). *De la grammatologie*. Éditions de Minuit. [*Of Grammatology*, trans. Gayatri Spivak, 1976]
- Hamming, R. W. (1950). "Error Detecting and Error Correcting Codes." *Bell System Technical Journal*, 29(2), 147–160.
- Rosch, E. (1975). "Cognitive Reference Points." *Cognitive Psychology*, 7(4), 532–547.

---

### Research Topic 2: Hermeneutics Implementation Completion

**Title**: Finish MANIFESTO.md Interpretation Framework — Add Examples and Test Coverage

**Corpus Gap**: The "How to Read This Document" section has been added to MANIFESTO.md (R1 completion), but enforcement through agent behavior and test coverage remains incomplete.

**Estimated Scope**: Small (add concrete examples to hermeneutics section; create test cases validating agents read the section correctly; 1 week).

**Blocks**: Full operationalization of Pattern 2.

**Research Question**: Can we write tests that verify agents have absorbed the interpretation rules (priority ordering, conflict resolution, novel-situation derivation)?

---

### Research Topic 3: External-Values Conflict Resolution Operationalization

**Title**: Formal Protocol for Multi-Principal Value Conflicts — Test with Simulated Deployment Scenarios

**Corpus Gap**: The external-value-architecture.md specifies conflict-resolution priority rules (Core > Deployment > Client > Session), but no operational protocol or tooling exists to apply them when conflicts arise in practice.

**Estimated Scope**: Large (design conflict-resolution protocol; implement configuration system for Client/Session layers; test with multi-principal scenarios; 4–6 weeks).

**Blocks**: Full adoption readiness for external teams.

**Research Question**: Can the Supremacy constraints be operationalized as a deterministic rule engine that resolves conflicts without human intervention?

---

### Research Topic 4: Context-Sensitive Amplification Threshold Calibration

**Title**: Empirical Study of Axiom-Weighting Lookup Table Effectiveness

**Corpus Gap**: Epigenetic tagging (OQ-VE-2) uses a task-type lookup table to amplify different axioms (Research → Endogenous-First; commit → Documentation-First). But optimal weighting is not yet empirically determined.

**Estimated Scope**: Medium–Large (collect session data categorized by task type; measure axiom-citation density and session quality by task type; identify optimal weighting; 3–4 weeks).

**Blocks**: Optimization of context-sensitive amplification for different agent roles and task contexts.

**Research Question**: For each task type (research, commit, documentation, automation), which axiom weight maximizes session quality and constraint adherence?

---

### Research Topic 5: Enforcement-Tier Complete Mapping

**Title**: Audit All Behavioral Constraints — Map to T0–T5 Enforcement Tiers; Identify Below-T3 Gaps

**Corpus Gap**: The enforcement-tier stack (shifting-constraints-from-tokens.md) is formalized for T1–T5, but not all endogenic behavioral constraints are mapped to their assigned tier. Constraints below T3 (script-level) may be at silent-drift risk.

**Estimated Scope**: Medium (systematic audit of MANIFESTO.md, AGENTS.md, agent files, scripts; dependency analysis; 1–2 weeks).

**Blocks**: Defense of programmatic-governance claims for constraint fidelity.

**Research Question**: Which constraints are currently T2-only (prompt/prose)? Can they be elevated to T3+ without excessive burden? Which constraints are genuinely unenforceable (trust-based T1) and should remain so?

---

## Path Forward

The five research topics constitute the critical path for Phase 2 corpus work (post-gap-analysis). Topic 1 (H4 baseline measurement) is the highest-priority blocker for holographic-encoding validation. Topic 5 (enforcement-tier audit) is critical for defending the programmatic-governance claims. The others strengthen the methodology's operationality without blocking publication but are important for adoption success.
