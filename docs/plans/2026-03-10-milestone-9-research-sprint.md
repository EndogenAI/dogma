# Workplan: Milestone 9 Research Sprint

**Milestone**: [#9 — Action Items from Research](https://github.com/EndogenAI/Workflows/milestone/9)  
**Research Issues**: #167–#185 (17 total)  
**Branch**: `main` (or dedicated research branches per phase)  
**Date Created**: 2026-03-10  
**Orchestrator**: Executive Researcher

---

## Objective

Execute a coordinated research sprint on 17 investigation and validation issues derived from gap-analysis documents for the three primary papers:
- `docs/research/endogenic-design-paper.md`
- `docs/research/values-encoding.md`
- `docs/research/bubble-clusters-substrate.md`

The sprint is organized into three research domains (Endogenic Design, Values Encoding, Bubble Clusters), each with dependent sub-phases (Literature Review → Operationalization → Empirical Validation → Peer Review / Case Study). The workplan enforces sequential gate stages: no operationalization begins until literature/corpus review is complete; no empirical validation begins until operationalization is specified; no external review begins until internal validation is complete.

---

## Research Domain Mapping

### Domain 1: Endogenic Design — Operational and Governance Completeness

**Primary Paper**: `endogenic-design-paper.md`  
**Gap Analysis**: `gap-analysis-endogenic-design.md`  
**Related Issues**: #167, #168, #172, #173, #174

| Issue # | Title | Type | Effort | Status |
|---------|-------|------|--------|--------|
| #167 | External Team Application Case Study | Case study | Medium | ⬜ |
| #168 | Morphogenetic System Design Operationalization | Operationalization | Medium–Large | ⬜ |
| #172 | H4 Novelty External Peer Review | Peer review | Medium | ⬜ |
| #173 | Multi-Principal Deployment Scenarios | Case study | Medium | ⬜ |
| #174 | Programmatic Governance Completeness Audit | Audit/mapping | Large | ⬜ |

### Domain 2: Values Encoding — Empirical Validation and Enforcement Operationalization

**Primary Paper**: `values-encoding.md`  
**Gap Analysis**: `gap-analysis-values-encoding.md`  
**Related Issues**: #176, #177, #178, #179

| Issue # | Title | Type | Effort | Status |
|---------|-------|------|--------|--------|
| #176 | Hermeneutics Implementation Completion | Doc synthesis | Medium | ⬜ |
| #177 | External-Values Conflict Resolution Operationalization | Operationalization | Medium | ⬜ |
| #178 | Context-Sensitive Amplification Threshold Calibration | Empirical validation | Medium | ⬜ |
| #179 | Enforcement-Tier Complete Mapping | Audit/mapping | Large | ⬜ |
| #169 | Fleet-Wide Holographic Encoding Measurement | Empirical validation | Large | ⬜ |

### Domain 3: Bubble Clusters — Topological Completeness and Empirical Properties

**Primary Paper**: `bubble-clusters-substrate.md`  
**Gap Analysis**: `gap-analysis-bubble-clusters.md`  
**Related Issues**: #170, #181, #182, #183, #184, #185

| Issue # | Title | Type | Effort | Status |
|---------|-------|------|--------|---------|
| #170 | Complete Topological Audit | Audit/mapping | Medium | ⬜ |
| #181 | Membrane Permeability Validation Script Implementation | Operationalization/scripting | Small | ⬜ |
| #182 | Provenance Audit CI Integration | Operationalization/CI | Small | ⬜ |
| #183 | Laplace Pressure Empirical Validation | Empirical validation | Medium | ⬜ |
| #184 | Filter-Bubble Threshold Calibration | Empirical validation | Medium | ⬜ |
| #185 | Deployment-Layer Topological Extension | Research/extension | Medium | ⬜ |

---

## Execution Phases

The sprint is organized into **three sequential domain phases**, each with internal **sub-phases** (Literature/Corpus Review → Operationalization → Empirical Validation → External Review/Case Study):

### **Phase 1 — Endogenic Design Research Domain**

#### Phase 1a: Corpus Review & Operationalization Foundation

**Agent**: Executive Researcher  
**Scope**: Validate Endogenic Design Paper claims against corpus; identify operationalization roadmap for H2, H3, H4  

**Seed Sources** (for corpus analysis and morphogenetic operationalization):
- Doursat, R., Sayama, H., & Michel, O. (2013). "A review of morphogenetic engineering." *Natural Computing*, 12(2), 357–373. doi:10.1007/s11047-013-9398-1 — Foundational theory on how emergent behaviors arise from simple agent rules and morphogenetic systems design patterns
- Toussaint, N., Norling, E., & Doursat, R. (2019). "Toward the self-organisation of emergency response teams based on morphogenetic network growth." *Artificial Life Conference Proceedings*, 31, 284–291. — Case study: morphogenetic fleet emergence in practice
- Green, D. G. (2023). "Emergence in complex networks of simple agents." *Journal of Economic Interaction and Coordination*, 18(1), 1–18. doi:10.1007/s11403-023-00385-w — Theoretical framework for measuring fleet emergence
- De Wolf, T., & Holvoet, T. (2006). "Design patterns for decentralised coordination in self-organising emergent systems." *Self-organizing systems*, 3464, 28–49. — Design patterns for coordinated agent behavior

**Deliverables**:
- [ ] #174 — Programmatic Governance Completeness Audit
  - Audit all constraints in codebase (AGENTS.md, scripts/, agent files, CI), map to enforcement tiers T0–T5
  - Produce: `docs/research/enforcement-tier-mapping.md` (D4 format) — scope of audit, gap list, remediation roadmap
  - Acceptance: Comprehensive table of all constraints with tier assignments; gaps identified
  - Estimated effort: 20–30 hours (large corpus read, 50+ constraints to classify)

- [ ] #168 — Morphogenetic System Design Operationalization (foundation phase)
  - Formalize fleet emergence model: define what "emergent fleet topology" means operationally
  - Study session history correlations between back-propagation cycle + agent role mutations + observed fleet behaviors
  - Produce: `docs/research/fleet-emergence-operationalization.md` — formal model spec + session-level metrics (citation density, role mutation rates, fleet topology changes)
  - Acceptance: Formal model definition with ≥3 session case studies showing metric correlations
  - Estimated effort: 25–35 hours (literature + corpus analysis + case study synthesisysis)

**Depends on**: Nothing  
**Gate**: Phase 1a deliverables must be committed before Phase 1b begins  
**Status**: ⬜ Not started

---

#### Phase 1b: Empirical Validation & Case Studies

**Agent**: Executive Researcher  
**Scope**: Validate operationalization specs via external case studies and empirical evidence  
**Deliverables**:
- [ ] #167 — External Team Application Case Study
  - Identify ≥1 external team (research collaborator, open-source maintainer) to test Endogenic Design methodology
  - Measure: adoption friction, learning time, design pattern alignment with H1–H4
  - Produce: `docs/research/external-team-case-study.md` (D4 format) — methodology, metrics, findings, lessons learned
  - Acceptance: Documented case study with ≥5 quantitative metrics (friction score, learning time, pattern adherence %); ≥3 qualitative insights
  - Estimated effort: 30–40 hours (team coordination + data collection + synthesis)

**Depends on**: Phase 1a (operationalization specs provide the evaluation framework)  
**Gate**: Phase 1b deliverables must be committed before Phase 1c begins  
**Status**: ⬜ Not started

---

#### Phase 1c: External Review & Multi-Principal Validation

**Agent**: Executive Researcher (orchestrates); may delegate peer-review coordination to Comms/DevRel  
**Scope**: External peer validation and multi-principal deployment scenarios  
**Deliverables**:
- [ ] #172 — H4 Novelty External Peer Review
  - H4 = "four-hypothesis mutual reinforcement produces system that is learnable and operable by teams unfamiliar with first principles"
  - Identify ≥2 CS community reviewers (e.g., program committee members from CHI/CSCW, OSS maintainers, academic collaborators)
  - Solicit structured review: Does the methodology as described satisfy the H4 claim? What evidence is missing?
  - Produce: `docs/research/h4-peer-review-synthesis.md` (D4 format) — reviewer sommaries, consensus findings, gap list for remediation
  - Acceptance: ≥2 independent reviewer reports; synthesized consensus summary with ≥3 evidence gaps identified
  - Estimated effort: 20–30 hours (outreach + review coordination + synthesis)

- [ ] #173 — Multi-Principal Deployment Scenarios
  - Case studies demonstrating six-layer deployment model from external-value-architecture.md in practice
  - Scenarios: (1) product team adopting methodology, (2) research collaborators with external constraints, (3) cross-organizational task force
  - Produce: `docs/research/multi-principal-deployment-scenarios.md` (D4 format) — scenario specs, topology diagrams, results from case studies
  - Acceptance: ≥1 documented scenario with topological diagram + ≥4 conflict-resolution decisions traced
  - Estimated effort: 25–35 hours (scenario design + case study execution + synthesis)

**Depends on**: Phase 1b (case study results inform peer review framing)  
**Gate**: Phase 1c deliverables must be committed before Review Phase 1 gate  
**Status**: ⬜ Not started

---

### Phase 1 Review — Review Gate ⬜

**Agent**: Review  
**Deliverables**: `## Phase 1 Review Output` section in scratchpad; verdict: APPROVED or REQUEST CHANGES  
**Depends on**: All Phase 1a–c deliverables committed  
**Gate**: Phase 2 does not begin until Review returns APPROVED  
**Status**: ⬜ Not started

---

### **Phase 2 — Values Encoding Research Domain**

#### Phase 2a: Empirical Measurement & Enforcement Audit

**Agent**: Executive Researcher  
**Scope**: Validate encoding fidelity hypotheses via corpus measurements; audit enforcement completeness  

**Seed Sources** (for encoding theory and information redundancy):
- Kieffer, J. C. (2002). "A survey of the theory of source coding with a fidelity criterion." *IEEE Transactions on Information Theory*, 39(5), 1473–1490. doi:10.1109/18.259635 — Foundational information theory on encoding fidelity and redundancy codes
- Shi, G., Gao, D., Song, X., Chai, J., Yang, M., & Xie, X. (2021). "A new communication paradigm: From bit accuracy to semantic fidelity." *arXiv preprint arXiv:2101.12649*. — Modern application of fidelity theory to semantic content preservation
- Zhang, Z., Yang, E. H., & Wei, V. K. (2002). "The redundancy of source coding with a fidelity criterion. 1. Known statistics." *IEEE Transactions on Information Theory*, 48(2), 564–581. — Formal analysis of redundancy in lossy encoding
- Watson, S., & Brezovec, E. (2025). "Autopoietic programs in an autopoietic ecology." *Bulletin of the Ecological Society of America*. — Application of programmatic governance to self-organizing systems

**Deliverables**:
- [ ] #179 — Enforcement-Tier Complete Mapping
  - Parallel to #174 but focused on VALUES (axiom citations, encoding preservation, degradation) rather than CONSTRAINTS (behavioral rules)
  - Audit: Every AGENTS.md / agent file / SKILL.md / MANIFESTO.md reference in the corpus
  - Map each constraint to T0–T5 enforcement tier (what programming/process layer enforces it)
  - Produce: `docs/research/values-enforcement-tier-mapping.md` (D4 format) — audit scope, tier assignments, gap analysis
  - Acceptance: Comprehensive table of ≥100 value constraints with tier assignments; ≥10 gaps identified with remediation plan
  - Estimated effort: 25–35 hours (comprehensive corpus read, constraint classification)

- [ ] #169 — Fleet-Wide Holographic Encoding Measurement
  - H4 assertion: "[4,1] repetition code" (strategic cite density of ≥4 MANIFESTO.md + ≥1 AGENTS.md cite) encodes endogenous values holographically
  - Measure across all `.agent.md` files, SKILL.md files, session records: what is actual cite density? Does it correlate with behavioral quality metrics?
  - Produce: `docs/research/holographic-encoding-empirics.md` (D4 format) — methodology, cross-ref density corpus data (histograms, correlations), validation of [4,1] code empirically
  - Acceptance: ≥5 quantitative metrics on cite density; ≥2 behavioral quality metrics showing correlation; >=80% of fleet > 2.5 average cite density
  - Estimated effort: 30–40 hours (corpus measurement + statistical analysis + writing)

- [ ] #178 — Context-Sensitive Amplification Threshold Calibration
  - Task-type lookup table in AGENTS.md specifies which axiom is "primary" per task (Research→ Endogenous-First, Commit→Documentation-First, etc.)
  - Validate empirically: Are agents actually producing higher-quality outputs when using context-amplified axioms vs. uniform? What is the "amplification threshold" (how much should weighting differ)?
  - Produce: `docs/research/context-amplification-calibration.md` (D4 format) — task taxonomy, output quality metrics, amplification thresholds (weight ratios), validation results
  - Acceptance: ≥3 task types tested; quality metrics show ≥10% improvement with context-amplified axioms; threshold weights specified (e.g., "Research: 70% Endogenous-First, 20% Documentation-First, 10% other")
  - Estimated effort: 25–35 hours (experiment design + agent execution + metric gathering + analysis)

**Depends on**: Phase 1 Review APPROVED  
**Gate**: Phase 2a deliverables must be committed before Phase 2b begins  
**Status**: ⬜ Not started

---

#### Phase 2b: Operationalization & Conflict Resolution

**Agent**: Executive Researcher  
**Scope**: Operationalize external-values layer; formalize conflict-resolution rules  
**Deliverables**:
- [ ] #177 — External-Values Conflict Resolution Operationalization
  - Six-layer model specifies priority (Core > Deployment > Client > Session). Define decision algorithms: when an external value conflicts with core axiom, how should agent decide?
  - Produce: `docs/research/external-values-decision-framework.md` (D4 format) — conflict taxonomy, decision tree, script examples, session case studies
  - Acceptance: ≥3 conflict types documented with decision rules; ≥2 session case study examples showing decision tree applied; pseudocode for `scripts/resolve_values_conflict.py` specified
  - Estimated effort: 20–30 hours (framework design + case study walkthrough + pseudocode)

- [ ] #176 — Hermeneutics Implementation Completion
  - Add "How to Read MANIFESTO.md" guide documenting interpretation framework: axiom priority ordering, novel-situation derivation, anti-pattern primacy
  - Produce: New section in `MANIFESTO.md` or standalone `docs/guides/manifesto-hermeneutics.md`
  - Acceptance: ≥3 worked examples showing interpretation framework applied to novel governance questions; clear priority ordering documented
  - Estimated effort: 15–20 hours (prose synthesis from existing backlog notes)

**Depends on**: Phase 2a (empirical validation informs conflict-resolution design)  
**Gate**: Phase 2b deliverables must be committed before Phase 2c begins  
**Status**: ⬜ Not started

---

#### Phase 2c: Integration & Documentation

**Agent**: Executive Docs  
**Scope**: Integrate Phase 2a–b findings into primary paper; update guidance docs  
**Deliverables**:
- Update `values-encoding.md` with links to three new research docs (#169, #177, #178, #179)
- Update `docs/guides/session-management.md` with context-amplification task-type lookup table (validated from #178)
- Update `docs/guides/external-value-architecture.md` conflict-resolution framework (from #177)
- Add hermeneutics guide to MANIFESTO.md or docs/guides/ (from #176)

**Depends on**: Phase 2b (operationalization specs finalized)  
**Gate**: Phase 2c deliverables must be committed before Review Phase 2 gate  
**Status**: ⬜ Not started

---

### Phase 2 Review — Review Gate ⬜

**Agent**: Review  
**Deliverables**: `## Phase 2 Review Output` section in scratchpad; verdict: APPROVED or REQUEST CHANGES  
**Depends on**: All Phase 2a–c deliverables committed  
**Gate**: Phase 3 does not begin until Review returns APPROVED  
**Status**: ⬜ Not started

---

### **Phase 3 — Bubble Clusters Research Domain**

#### Phase 3a: Topological Analysis & Properties Validation

**Agent**: Executive Researcher  
**Scope**: Formalize bubble topology; validate mathematical properties  

**Seed Sources** (for topological analysis, membrane theory, and filter bubble dynamics):
- Wang, X., Liu, Y., Wu, S., Zhao, Z., Hu, Y., Li, W., & others. (2026). "Ideological Isolation in Online Social Networks: A Survey of Computational Definitions, Metrics, and Mitigation Strategies." *arXiv preprint arXiv:2601.07884*. — Comprehensive survey on isolation risk metrics and threshold measurement
- Interian, R., Marzo, R. G., & Mendoza, I. (2023). "Network polarization, filter bubbles, and echo chambers: an annotated review of measures and reduction methods." *International Transactions in Operational Research*, 30(6), 2745–2778. doi:10.1111/itor.13224 — Synthesis of filter bubble thresholds and measurement methods
- Navascues, G. (1979). "Liquid surfaces: Theory of surface tension." *Reports on Progress in Physics*, 42(7), 1131–1193. doi:10.1088/0034-4885/42/7/002 — Classical theory of Laplace pressure and surface properties
- Popinet, S. (2018). "Numerical models of surface tension." *Annual Review of Fluid Mechanics*, 50, 49–78. doi:10.1146/annurev-fluid-122316-045034 — Mathematical formalization of Laplace pressure and topological dynamics
- Min, Y., Jiang, T., Jin, C., Li, Q., & Jin, X. (2019). "Endogenetic structure of filter bubble in social networks." *Royal Society Open Science*, 6(11), 190868. doi:10.1098/rsos.190868 — Empirical validation of filter bubble topology in networks
- Traxler, B., Boyd, D., & Beckwith, J. (1993). "The topological analysis of integral cytoplasmic membrane proteins." *The Journal of Membrane Biology*, 137(1), 1–10. doi:10.1007/BF00233047 — Classical topological membrane analysis methods

**Deliverables**:
- [ ] #170 — Complete Topological Audit
  - Map complete substrate topology: 3D vertices (agents, scripts, docs), 2D faces (subsystem boundaries), 1D edges (communication channels)
  - Currently only vertices/faces mapped; edges remain theoretical. Formalize edge semantics: control flow, data flow, metadata flow
  - Produce: `docs/research/complete-substrate-topology.md` (D4 format) — formal topological spec with diagrams, active/latent element classification, edge taxonomy
  - Acceptance: Complete topological map (vertices, faces, edges) with ≥3 worked examples (e.g., session→agent→script call stack traced through topology); active vs. latent elements classified
  - Estimated effort: 20–30 hours (topological analysis + diagramming)

- [ ] #183 — Laplace Pressure Empirical Validation
  - Bubble metaphor asserts pressure differential across membrane (internal vs. external). Does this hold empirically? Can we quantify "pressure" as citation density or constraint enforcement?
  - Measure: cross-reference density inside vs. outside specific boundaries (e.g., AGENTS.md vs. external docs, agent file vs. external scripts)
  - Produce: `docs/research/laplace-pressure-validation.md` (D4 format) — pressure quantification methodology, measured data, mathematical model validation
  - Acceptance: ≥3 pressure differentials quantified with ≥5 data points each; mathematical model (Laplace pressure equation) fit to data; R² > 0.7 correlation
  - Estimated effort: 25–35 hours (measurement design + data collection + statistical analysis)

**Depends on**: Phase 2 Review APPROVED  
**Gate**: Phase 3a deliverables must be committed before Phase 3b begins  
**Status**: ⬜ Not started

---

#### Phase 3b: Operationalization & Validation Scripts

**Agent**: Executive Researcher + Executive Scripter  
**Scope**: Operationalize membrane specs and provenance audit  
**Deliverables**:
- [ ] #181 — Membrane Permeability Validation Script Implementation
  - Automate validation of AGENTS.md boundary specifications (e.g., Scout→Synthesizer handoff must preserve "Canonical example" and axiom cites)
  - Produce: `scripts/validate_handoff_permeability.py` (new script) — checks boundary compliance; tests ≥80% coverage
  - Acceptance: Script runs CI-ready; ≥20 test cases covering all membrane types (Scout→Synthesizer, Synthesizer→Reviewer, Reviewer→Archivist); docstring + README entry complete
  - Estimated effort: 15–20 hours (script implementation + tests)

- [ ] #182 — Provenance Audit CI Integration
  - Integrate `audit_provenance.py` into GitHub Actions (currently manual)
  - Add weekly or per-commit lint job that flags agents with zero MANIFESTO.md cites in 30-day windows
  - Produce: CI configuration + audit result logging to PR/issue comments
  - Acceptance: CI job runs on every commit; produces structured audit report (JSON + Markdown); ≥5 test cases covering different provenance scenarios
  - Estimated effort: 10–15 hours (CI integration + job configuration + tests)

- [ ] #184 — Filter-Bubble Threshold Calibration
  - What cross-reference density minimum prevents filter-bubble isolation? Empirically calibrate threshold
  - Use audit_provenance.py measurements + fleet health metrics (issue response time, contributor retention, etc.)
  - Produce: `docs/research/filter-bubble-threshold-calibration.md` (D4 format) — threshold value, calibration methodology, validation against fleet health metrics
  - Acceptance: Minimum cite density threshold specified (e.g., "≥2.5 average MANIFESTO.md cites per agent file per 30 days"); ≥3 fleet health metrics correlated with threshold; ≥2 session case studies showing threshold application
  - Estimated effort: 20–25 hours (measurement setup + metric correlation + threshold calibration)

**Depends on**: Phase 3a (topological audit provides context for membrane/permeability specs)  
**Gate**: Phase 3b deliverables must be committed before Phase 3c begins (scripts must have passing tests)  
**Status**: ⬜ Not started

---

#### Phase 3c: Deployment-Layer Extension & Integration

**Agent**: Executive Researcher  
**Scope**: Extend bubble topology to six-layer deployment model  
**Deliverables**:
- [ ] #185 — Deployment-Layer Topological Extension
  - Current topology: nested three-cube model (MANIFESTO.md ↔ AGENTS.md ↔ agent files)
  - Six-layer model inserts Deployment Layer with new membranes. Formalize extended topology: new vertices, new faces, new boundaries
  - Produce: `docs/research/six-layer-topological-extension.md` (D4 format) — extended topological diagrams, new boundary specs, conflict-resolution junctions, case studies
  - Acceptance: Complete six-layer topology map with ≥3 topological diagrams; ≥2 new membranes formalized; ≥1 external team case study traced through extended topology
  - Estimated effort: 20–30 hours (topological analysis + diagramming + case study synthesis)

**Depends on**: Phase 3b (scripts provide operationalization foundation; topological audit in 3a provides context)  
**Gate**: Phase 3c deliverables must be committed before Review Phase 3 gate  
**Status**: ⬜ Not started

---

### Phase 3 Review — Review Gate ⬜

**Agent**: Review  
**Deliverables**: `## Phase 3 Review Output` section in scratchpad; verdict: APPROVED or REQUEST CHANGES  
**Depends on**: All Phase 3a–c deliverables committed (including passing tests for #181, #182)  
**Gate**: Session closes after Review returns APPROVED  
**Status**: ⬜ Not started

---

## Dependency Graph

```
Phase 1 Review APPROVED
    └── Phase 2a (empirical measurement) — #179, #169, #178
            └── Phase 2b (operationalization) — #177, #176
                    └── Phase 2c (docs integration)
                            └── Phase 2 Review APPROVED
                                    └── Phase 3a (topological audit) — #170, #183
                                            └── Phase 3b (scripts) — #181, #182, #184
                                                    └── Phase 3c (extension) — #185
                                                            └── Phase 3 Review APPROVED
                                                                    └── Research Sprint Complete
```

---

## Leadership and Delegation

| Phase | Primary Agent | Supporting Agents | Autonomous Scope |
|-------|---------------|-------------------|------------------|
| Phase 1a | Executive Researcher | — | Full research autonomy; delegate scripting only |
| Phase 1b | Executive Researcher | External team coordinators | Case study design and validation; external coordination at Executive Docs / Comms level |
| Phase 1c | Executive Researcher | Comms Strategist (peer review outreach) | Research synthesis; external review coordination delegated to Comms |
| Phase 2a | Executive Researcher | — | Full research autonomy |
| Phase 2b | Executive Researcher | — | Full research autonomy; framework design |
| Phase 2c | Executive Docs | Executive Researcher (reference support) | Docs updates; cite research docs from Phase 2a–b |
| Phase 3a | Executive Researcher | — | Full research autonomy |
| Phase 3b | Executive Scripter | Executive Researcher (specs) | Script implementation and testing; specs from 3a research |
| Phase 3c | Executive Researcher | — | Full research autonomy |

---

## Effort Estimation Summary

| Phase | Total Hours | Allocation |
|-------|-------------|-----------|
| Phase 1a | 45–65h | High effort (foundational) |
| Phase 1b | 30–40h | Medium effort |
| Phase 1c | 45–65h | High effort (external coordination) |
| Phase 2a | 80–110h | Very high effort (empirical work) |
| Phase 2b | 35–50h | Medium effort |
| Phase 2c | 20–30h | Low effort (docs integration) |
| Phase 3a | 45–65h | High effort (topological analysis) |
| Phase 3b | 45–60h | High effort (scripting + testing) |
| Phase 3c | 20–30h | Low–medium effort |
| **Total Sprint** | **365–515h** | **~9–13 weeks full-time** |

---

## Risk and Mitigation

| Risk | Mitigation |
|------|-----------|
| Empirical validation (Phase 2a, 3a) requires external data that may be noisy or insufficient | Start Phase 2a early; if measurement signal is weak after 10 hours, escalate to Conor for scope reduction |
| Case studies (#167, #173, #185) require external team coordination and may have scheduling delays | Start outreach in Phase 1a (parallel); confirm team availability before Phase 1b begins |
| Peer review (#172) may require months to complete if late outreach | Identify reviewers in Phase 1a; send solicitations by end of Phase 1b max |
| Scripting effort (#181, #182) may exceed estimate if testing is complex | Begin #181–#182 in parallel with 3a research; do not gate 3b on complete 3a if development path is clear |
| Topological mapping (#170, #185) may reveal missing dimensions/relationships | Allocate 10 hours buffer in Phase 3a for topology refinement after initial analysis |

---

## Acceptance Criteria

- [ ] All 17 research issues closed or merged to main
- [ ] Every research synthesis doc (D4 format) committed to `docs/research/`
- [ ] All new scripts (#181, #182) have ≥80% test coverage and are CI-integrated
- [ ] Three primary papers updated with forward references to new research docs
- [ ] Every phase has a Review gate with APPROVED verdict before next phase begins
- [ ] No phase advances without committed deliverables

---

## Notes

- **Cross-Domain References**: Values Encoding (#169, #177, #179) and Bubble Clusters (#183–#185) both reference six-layer deployment model and conflict-resolution rules. Phase 2b (#177) operationalizes the conflict-resolution framework; Phase 3c (#185) applies it topologically. Order matters: Phase 2 before Phase 3.

- **External Coordination**: Issues #167, #172, #173 require external teams/reviewers. Begin outreach immediately in Phase 1a (parallel with #174, #168 research) so confirmations arrive before Phase 1b/1c begin.

- **Scripting Dependencies**: #181 and #182 depend on AGENTS.md specs (#115 from milestone-9-action-items.md Phase 2). Confirm #115 is committed before Phase 3b begins. If not, note as blocker in scratchpad.

- **Parallel Execution Opportun ities**: Phases 1a and 2a are independent if external case studies (#167) are not the critical path. Consider running 1a and 2a in parallel with different Research Scout sub-agents if bandwidth allows. Flag in session scratchpad if attempting parallel tracks.

