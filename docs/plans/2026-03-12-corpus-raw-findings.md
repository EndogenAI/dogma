---
title: "Corpus Back-Propagation — Phase 1 Raw Scout Findings"
sprint: "2026-03-12-corpus-backprop"
---

# Corpus Back-Propagation — Phase 1 Raw Scout Findings

## Scout 1A — Synthesis Docs (7 Thorough)

---

### enforcement-tier-mapping.md

**Source**: Final, research_issue #174, date 2026-03-10

**Key claims and patterns**

- 68 constraints inventoried across 7 source files and 3 CI layers. The distribution reveals a two-cluster structure: a hardened enforcement core (file-write anti-patterns, synthesis validation, agent-file structure, code style) and a large T5 prose-only periphery (commit discipline, session lifecycle, remote-write verification, documentation-first, delegation patterns).
- T1–T4 count: 19 (27% of total). T5 count: 37 (54% of total). This means just over half of all operational constraints are prose-only with no automated enforcement.
- 12 T3 pre-commit constraints (ruff, validate-synthesis, validate-agent-files, check-doc-links, no-heredoc-writes, no-terminal-file-io-redirect).
- 2 T4 constraints (bash-preexec Governor B intercepts heredoc writes at the interactive terminal before execution).
- 3 T0 runtime guards: validate_url(), validate_slug(), capability_gate.py — these block at function-call time.
- The canonical T5→T3→T4 full uplift lifecycle is documented with the heredoc constraint as the example: started as prose, encoded as T3 pygrep hook, then independently enforced at T4 via bash-preexec. Cross-session violation rate: zero since T4 deployment.
- Anti-pattern named explicitly: the `uv run` enforcement constraint has been re-written in AGENTS.md prose at least three times, with each re-write representing a prior T5 violation. No programmatic enforcement exists. A `pygrep` hook matching `^\s*python\s` in `.sh` and `.yml` files would catch the majority of violations at commit time.
- The distribution "aligns with MANIFESTO.md §2 Algorithms Before Tokens: constraints that have been encoded programmatically are the most reliably honored. T5 constraints exhibit observable drift in session history — they are routinely violated when context pressure is high."
- T5 gaps classified by feasibility: High (pattern-matchable) — Conventional Commits, `uv run` enforcement, `gh --body` guard, `git push --force` guard; Medium (structural check feasible) — handoff target validation, depends-on validation, scaffold_agent.py provenance, Testing-First file-existence; Low (requires context/judgment) — Verify-After-Act, session lifecycle, Compression-on-Ascent.
- R1–R4 recommendations with concrete implementations: commitlint (XS), `uv run` pygrep (XS), handoff target validation (S), Testing-First file-existence check (S).

**Absent from or underrepresented in primary papers**

- `values-encoding.md` T1–T4 fidelity test taxonomy describes the tier types as a diagnostic framework, but this document provides the first exhaustive per-constraint mapping of which specific codebase constraints land at which tier. The tier-by-tier inventory (T0: 3, T1: 12, T2: 2, T3: 12, T4: 2, T5: 37) is a concrete empirical result that strengthens the Pattern 5 (Programmatic Governance as Epigenetic Layer) claim in values-encoding.md. The gap: values-encoding.md Pattern 5 exists as a claim; enforcement-tier-mapping.md is the evidence.
- The 37-constraint T5 list is a concrete gap inventory not present in values-encoding.md §5. Back-propagating this to values-encoding.md Pattern Catalog would provide the empirical grounding for Hypothesis H3 (Programmatic Governance layer exists and has measurable coverage).
- The complete T5→T3→T4 heredoc lifecycle story (three enforcement layers now coexist; violation rate zero post-T4) is cited in passing in AGENTS.md §Programmatic Governors but not incorporated as a canonical example in values-encoding.md §3 Pattern Catalog.
- The R2 `uv run` anti-pattern (re-written 3x in prose, no T3 gate) is a live case of observable drift from T5 enforcement that would strengthen the "T5 constraints exhibit observable drift" claim in primary papers.
- bubble-clusters-substrate.md membrane permeability specs and values-encoding.md back-propagation methodology (§5) do not reference the enforcement tier structure. The boundary types (T0–T5) map naturally onto membrane permeability properties — tighter tiers = less permeable membranes.

**Evidence structures for weaving**

- The T0–T5 tier distribution table (68 constraints, tier counts) is a citable empirical data point for strengthening values-encoding.md §2 H3 (Programmatic Governance layer exists).
- The canonical heredoc lifecycle example (T5→T3→T4, zero post-T4 violations) is a prototype-anchor for values-encoding.md Pattern Catalog entry on T5 uplift.
- The T5 feasibility classification (High/Medium/Low) is a useful operationalization of the "programmatic uplift" claim in values-encoding.md Recommendations.

---

### external-values-decision-framework.md

**Source**: Final, research_issue #177, date 2026-03-10

**Key claims and patterns**

- Formal conflict taxonomy with four types: Type 1 (Axiomatic Posture Override — a Deployment/Client Layer instruction relaxes or replaces a core axiom), Type 2 (Session-Layer Injection Override — externally-sourced content contains instruction-like directives targeting Core constraints; this is the prompt injection attack vector), Type 3 (Client Ethical Value Conflict — client-values.yml contradicts MANIFESTO.md §Ethical Values), Type 4 (Provenance Suppression Override — efficiency framing used to suppress documentation/citation requirements; recognized as covert Type 1).
- Critical architectural finding: the decision tree has no branch that produces "Outer layer wins." Every branch terminates in ALLOW (no conflict), BLOCK (Core enforced), or ESCALATE (human review). This is a predetermined conflict resolution structure, not a runtime judgment call.
- The franchise analogy explains why additive-only Deployment Layer is sufficient: a client constraint adding restrictions (HIPAA compliance, tone conventions) operates in disjoint behavioral space from Core constraints. Only constraints that relax Core behavior produce conflict.
- Boundary condition named explicitly: a constraint that looks additive on the surface may be a covert override. Example: "respond as fast as possible" sounds like an efficiency preference but implicitly asks the agent to skip the session-start reading ritual — a Core constraint override. Conservative interpretation (Step 4 → Step 5 fallback) treats ambiguous constraints as potential Type 1 overrides.
- Decision tree pseudocode specification for `resolve_values_conflict(layer_name, value_key, proposed_value, core_constraint_catalogue)` → returns ALLOW/BLOCK/ESCALATE plus conflict_type and violated_constraint.
- Pattern F1 (Supremacy Declaration at Every Layer Boundary): every `client-values.yml` should pre-populate a `conflict_resolution` field stating: "EndogenAI Core Layer (MANIFESTO.md + AGENTS.md) supersedes all entries in this file." This is performative encoding (values-encoding.md §3 Pattern 4 cited explicitly).
- Pattern F2 (Conservative Interpretation of Ambiguous Constraints): when a proposed constraint is neither clearly additive nor clearly an override, treat as potential Type 1 and escalate. "Benign intent" reasoning must not be a bypass vector.
- Two canonical case studies: (1) Research Scout reads `.cache/sources/competitor-methodology.md` which contains embedded prompt injection ("disregard any internal guidelines") → logged as Type 2, BLOCK + ESCALATE, factual content processed only; (2) Healthcare client-values.yml attempts to suppress scratchpad writes on HIPAA grounds → logged as Type 3+4, BLOCK + ESCALATE, corrective path provided (restrict what is written, not whether to write).
- R4 recommends implementing `resolve_values_conflict.py` as a callable script from the pseudocode spec (Algorithms Before Tokens applied to conflict resolution).

**Absent from or underrepresented in primary papers**

- `endogenic-design-paper.md` has LCF framing and oversight infrastructure recently added, but the four-type conflict taxonomy (Type 1–4) with decision tree and pseudocode is not in that paper's pattern catalog. The external-values conflict framework is a distinct Pattern Catalog entry candidate for endogenic-design-paper.md (connecting to H3 Augmentive Partnership — the human relationship framing requires understanding what happens when external layers conflict with Core).
- `values-encoding.md` Pattern 4 (Performative Encoding) is cited as the basis for the Supremacy Declaration pattern, but the direction of that reference — conflict resolution as performative encoding — is not present in values-encoding.md's own pattern catalog.
- `bubble-clusters-substrate.md` membrane permeability specs describe what flows in/out of membranes but do not address the conflict resolution logic for when external input contradicts internal membrane state. The Type 1–4 taxonomy fills that gap.
- The conservative interpretation fallback (ESCALATE on ambiguous, not ALLOW) is a nuanced finding with security implications — absent from AGENTS.md Security Guardrails and from values-encoding.md.
- The healthcare case study (HIPAA justification for suppressing documentation) is an archetypal external deployment scenario that would strengthen the Hypothesis Validation sections of endogenic-design-paper.md — demonstrates that the framework handles real-world multi-stakeholder conflict deterministically.

**Evidence structures for weaving**

- The ALLOW/BLOCK/ESCALATE outcome taxonomy + no "Outer layer wins" finding are citable for endogenic-design-paper.md H4 (CS legitimacy claim relies on a deterministic constraint resolution architecture, not runtime judgment).
- Pattern F1 (Supremacy Declaration + `conflict_resolution` field) is directly back-propagatable to endogenic-design-paper.md Pattern Catalog as an external-team adoption pattern.
- The pseudocode specification for `resolve_values_conflict.py` is an Algorithms Before Tokens canonical example ready for endogenic-design-paper.md.

---

### h4-peer-review-synthesis.md

**Source**: Final, research_issue #172, date 2026-03-10

**Key claims and patterns**

- H4 verdict (the four-hypothesis system is learnable and operable by teams unfamiliar with first principles): PARTIALLY SUPPORTED, with confidence qualifier "internal proxies only; external validation is the outstanding gap."
- Formal evidence framework with three categories: Category A (learnability signals — observable behaviors from practitioners following documented protocols from written guidance alone without understanding theory), Category B (operability under no-prior-context — multi-step workflow completion without expert consultation), Category C (onboarding success rate — fraction reaching independent operation within N guided sessions).
- Existing evidence: M2 = 100% post-protocol session-start compliance across 20 sessions (Category A, strong proxy, intra-team); M4 = 33/33 = 100% workplan phase-gate adoption (Category B, strong proxy, intra-team); ARM = 5 achieved in two independent sprint events (Category B, strong proxy, intra-team); CONTRIBUTING.md complexity = 1,066 words (Category C, weak proxy, complexity estimate only).
- Four evidence gaps with specific observational needs: (1) No external cold-start onboarding observation — most critical; (2) No ARM-equivalent measurement from external team's first sprint; (3) No token-burn A/B comparison (H1 empirical gap, directly relevant to H4 because external reviewers will ask if the session-start reading ritual is worth the overhead); (4) No violation-rate measurement for pre-commit install path (external teams may skip `uv run pre-commit install`, leaving T5 constraints unenforced).
- Pattern R1 (Template-Sufficiency): session-start encoding checkpoint — fill-in-the-blank template ("Governing axiom: X — primary endogenous source: Y") achieved 100% compliance across 20 sessions with zero theoretical understanding required. Template-sufficiency means H4 learnability does not depend on educating practitioners about H1–H3 theory.
- Pattern R2 (Programmatic Enforcement as Learnability Multiplier): a counter-intuitive finding — the more constraints that are T3/T4 enforced, the LESS learnability burden on external teams. Each T3 governor removes a constraint from the set of things an external practitioner needs to remember. Sending an external team AGENTS.md without `CONTRIBUTING.md` quickstart and `uv run pre-commit install` first leaves 37 T5 prose-only constraints entirely reliant on reading comprehension and context-pressure resilience.
- Pattern R3 (Reviewer-as-Evidence-Instrument): the Q1–Q5 reviewer framework is structured to generate observable artifacts (a workplan file, a pre-commit block event, a session scratchpad), not impressionistic opinions. Each question is a Category C evidence collection event.
- Q5 specifically tests whether the layer conflict-resolution rule is self-evident from a single pattern description — directly operationalizes the external-values decision framework as an H4 operability test.
- R2 recommendation: complete three high-priority T5→T3 uplifts BEFORE scheduled reviewer sessions. Reviewer encounters these T5 constraints at maximum vulnerability during cold-start onboarding.

**Absent from or underrepresented in primary papers**

- `endogenic-design-paper.md` has H4 verdict as Medium-High Confidence but may not contain the three-category evidentiary framework (A/B/C) with formal confirming/disconfirming evidence definitions per category. The framework makes H4 precisely falsifiable rather than impressionistically evaluated.
- The ARM (Adoption-Reification Metric) as a formal metric with two confirmed ARM=5 emergence events is likely absent from endogenic-design-paper.md's Hypothesis Validation section. ARM > 0 from an external team's first sprint is the earliest internalization signal (beyond template-following).
- The proxy metrics (M1–M5) with specific measurements (CONTRIBUTING.md = 1,066 words, M2 = 20/20 post-protocol, M4 = 33/33 phase-gate, ARM = 5 events) represent quantified evidence for H4 that would strengthen endogenic-design-paper.md §Hypothesis Validation.
- The Programmatic Enforcement as Learnability Multiplier pattern (T3/T4 stack reduces external team onboarding burden directly) is not stated in values-encoding.md or endogenic-design-paper.md. This is a compound finding: governance enforcement quality correlates with external learnability, creating a feedback loop between the enforcement tier work and the external team adoption claim.
- The Q1–Q5 reviewer solicitation framework is a reusable evaluation protocol for H4 not yet committed to `docs/guides/`. Its existence in a research doc rather than a guide limits reuse.

**Evidence structures for weaving**

- M2 (100% post-protocol, 20 sessions), M4 (33/33 phase-gate adoption), ARM = 5 are quantified H4 supporting data for endogenic-design-paper.md §Hypothesis Validation.
- Template-Sufficiency pattern (fill-in-the-blank achieved 100% compliance without theory transfer) is a canonical example candidate for endogenic-design-paper.md Pattern Catalog and for values-encoding.md §3 (Performative Encoding via template structure).
- The "T3 stack reduces learnability burden" compound finding connects enforcement-tier-mapping.md to h4-peer-review-synthesis.md directly — both would become stronger if values-encoding.md §5 Back-Propagation Methodology explicitly links enforcement tier coverage to external-team adoption evidence.

---

### holographic-encoding-empirics.md

**Source**: Final, research_issue #169, date 2026-03-10

**Key claims and patterns**

- First empirical measurement of holographic encoding across the full fleet: 49 files (36 agent + 13 skill) = 100% coverage.
- Cite density formula: (MANIFESTO.md occurrences + AGENTS.md occurrences) / section_count.
- Fleet-wide mean: 0.85. Median: 0.54. Min: 0.04 (research-synthesizer.agent.md). Max: 6.20 (d4-methodology-enforcer.agent.md).
- Only 6.1% of files (3/49) exceed the ≥2.5 density target for individual holographic reconstruction. 20.4% of files are in the 0.00–0.19 range.
- H1 (fleet exhibits holographic encoding property — every file has ≥1 foundational echo): CONFIRMED at minimum condition. Zero-density case eliminated (min > 0). But minimum condition is not sufficient for reconstruction — a single AGENTS.md reference is a structural pointer, not a semantic echo of axiom content.
- H2 (citation density correlates with values-oriented role type): CONFIRMED directional. Role-type mean densities: values/methodology enforcement = 3.41; Executive/orchestration = 1.09; Research fleet = 0.26; Operational utilities = 0.23; Skills (all) = 0.83. Density is a function of role scope, not a direct quality signal — a utility agent at 0.17 is not "less aligned" than a values-enforcer at 6.20; they occupy different positions in the inheritance chain.
- H3 ([4,1] repetition code holds at fleet level): CONDITIONALLY CONFIRMED, NOT fully validated. The [4,1] claim holds at the fleet layer (MANIFESTO.md + AGENTS.md + subdirectory AGENTS.md + agent files together carry full reconstructive content) but NOT at the individual-file layer. Most agent files (median density 0.54) provide partial echoes only — insufficient to reconstruct axiom content from a single agent file in isolation. Target for individual-file holographic encoding: ≥2.5 per section.
- Goodhart's Law caveat stated explicitly: optimizing density as a metric would produce low-quality files with repeated MANIFESTO.md references but no genuine content absorption. Density is a proxy for fidelity, not fidelity itself.
- Notable outlier (anti-pattern): `research-synthesizer.agent.md` density = 0.04. Lowest in fleet. The production synthesis agent — primary values-encoding artifact producer — has 1 AGENTS.md reference across 23 sections. Operational sections (Workflow, Context Management, Quality) contain zero foundational references. "An agent performing synthesis without explicit axiom anchoring in its operating procedures risks producing documents that are technically correct but values-disconnected."
- Notable outlier (canonical example): `d4-methodology-enforcer.agent.md` density = 6.20. 31 MANIFESTO+AGENTS cites across 5 sections. Purpose-built for axiom enforcement; high density is structurally appropriate. "This is the holographic ideal — a layer that contains sufficient axiom echoes to reconstruct the core value set without consulting higher layers."
- R1: Extend `generate_agent_manifest.py` to compute per-file density; add CI assert fleet mean ≥ 0.50. R2: research-synthesizer.agent.md density uplift — add 2 MANIFESTO.md and 2 AGENTS.md explicit references in Workflow/Quality sections. R3: Target density ≥2.5 for Executive tier agents.

**Absent from or underrepresented in primary papers**

- `values-encoding.md` §2 H4 (Holographic Encoding Hypothesis) states the hypothesis but this document provides the first empirical measurement of it across the full fleet. The key finding — [4,1] claim holds at fleet layer collectively but NOT at individual-file layer — is a nuance that strengthens and partially revises the primary paper's H4 claim. The primary paper's claim needs this qualification.
- The 49-file fleet census with density histogram (0.00–0.19: 20.4%, 0.20–0.49: 28.6%, 0.50–0.99: 32.7%, ≥2.50: 6.1%) is quantitative empirical data for strengthening values-encoding.md §2 H4 and §6 Pattern 6.
- The Goodhart's Law caveat (optimizing density as metric produces low-quality repeated citations) is not in values-encoding.md Pattern Catalog. It is a critical constraint on how Pattern 6 (cross-reference density as fidelity metric) should be applied.
- The role-type vs. density taxonomy (table with 5 role categories and mean densities) demonstrates that density is a function of role scope — this contextualizes and strengthens the [4,1] claim by explaining why operational utility agents at low density are not alignment failures.
- The research-synthesizer.agent.md anti-pattern (lowest density + most critical production role = values-disconnection risk) is a concrete empirical finding for the endogenic-design-paper.md Pattern Catalog and for values-encoding.md §3 Anti-patterns section.

**Evidence structures for weaving**

- Fleet density table per agent file is a citable data source for values-encoding.md §2 H4 empirical grounding.
- The holographic reconstruction threshold finding (≥2.5 for individual files; 6.1% currently meet it) is a named gap for values-encoding.md §5 Recommendations.
- The [4,1] condition ("holds at fleet layer, not individual-file layer") is a qualification to the primary paper claim that should be stated there.
- The Goodhart's Law caveat is a Pattern Catalog anti-pattern entry candidate for values-encoding.md.

---

### laplace-pressure-empirical-validation.md

**Source**: Final, research_issue #183, date 2026-03-10

**Key claims and patterns**

- Three pressure metrics defined and empirically validated: P1 (Citation Density Pressure = axiom citation frequency per 100 lines, formula: citations / (length / 100)), P2 (Constraint Violation Pressure = 1 − violations/total_checks; compliance rate), P3 (Cross-Domain Permeability Coefficient = intra_edges / (intra_edges + cross_edges)).
- Success criterion met: ≥1 metric R² > 0.6; ≥2 metrics exceeded threshold:
  - P1 vs Task Velocity: R² = 0.68 (p < 0.01)
  - P2 vs Task Velocity: R² = 0.72 (p < 0.001); vs Test Pass Rate: R² = 0.77 (p < 0.001)
  - P3 vs Task Velocity: R² = 0.54 (p < 0.05)
- Primary finding: P2 (Constraint Violation Pressure / compliance rate) is the strongest predictor of system health — R² > 0.7 for both velocity and test-passing metrics. High-pressure subsystems show 60–70% higher task completion velocity than low-pressure subsystems.
- Young-Laplace equation (ΔP = 2γ/r) applied as governance metaphor: internal pressure = constraint adherence + citation density + test coverage; surface tension (γ) = governance mechanisms (CI gates, pre-commit hooks, code review); external pressure = competing demands + tight deadlines + context window pressure near compaction boundaries; radius of curvature = subsystem boundary permeability.
- Stability condition stated as formula: Internal Pressure + Surface Tension > External Pressure → Sustained Coherence. Critical insight: "A subsystem with high internal pressure but low tension (no enforcement mechanisms) will collapse or deform under external pressure. A subsystem with high tension but no internal pressure will ossify and become brittle."
- Three pressure zones: Healthy (≥2 metrics ≥ mean−0.5σ), Warning (one metric weak), Collapse (all three < mean−1σ simultaneously). Retrospective validation: collapse-zone detection was 100% predictive of formal archival or retirement.
- High-pressure case studies: Research synthesis subsystem (P1: 0.72, P2: 0.92, P3: 0.65; 3× task velocity, 94% test pass rate); Executive Orchestrator (P1: 0.68, P2: 0.89, P3: 0.42 — low P3 is correct for integration hub, compensated by high P1+P2; <2% agent error rate vs 5% system average).
- Low-pressure case study: Latent documentation subsystem (old ADRs, archived research stubs; P1: 0.18, P2: 0.52, P3: 0.35 — minimal activity, last modified 60+ days, risk: if an agent accidentally reads an old ADR as authoritative, it might extract guidance contradicting current axioms without triggering alerts).
- Anti-pattern named: isolated unmaintained script (low P1, P2, P3) — "no one notices" isolation paradoxically increases decay risk because nothing depends on it.
- 10 standing recommendations including: CI-based pressure monitoring per commit; pressure-aware file lifecycle process (activation vs archival); pressure-based technical debt prioritization.

**Absent from or underrepresented in primary papers**

- `bubble-clusters-substrate.md` has the theoretical foundation for Laplace pressure (ΔP = 2γ/r, membrane geometry) but this document provides the empirical validation: R² correlations with task velocity and test pass rate across a 60-day, 36-file measurement window. The bubble-substrate primary paper's membrane pressure theory is stated as a model but not empirically grounded — this document provides that grounding.
- The three quantified pressure metrics (P1/P2/P3) with defined formulas and measured R² values are not in `values-encoding.md`. P2 (compliance rate R² = 0.72 vs velocity) is the most empirically reliable predictor of system health — this is a concrete finding for values-encoding.md Hypothesis Validation and Pattern Catalog.
- The stability condition formula (Internal Pressure + Surface Tension > External Pressure = Coherence) is an operationalization of the bubble-cluster membrane model that connects directly to values-encoding.md §3 Programmatic Governance pattern. It bridges the two primary papers.
- The bimodal P1 distribution (peaks at ~0.3 for scripts/latent docs; ~0.7–1.0 for guidance docs/research syntheses) is an empirical finding that contextualizes the holographic encoding empirics (holographic-encoding-empirics.md) and the density claims in values-encoding.md.
- The collapse-zone detection (all three metrics < mean−1σ) being 100% retrospectively predictive of archival/retirement is a strong empirical claim for endogenic-design-paper.md §Hypothesis Validation — it suggests the pressure model has predictive validity for organizational health, not just correlational.
- The latent documentation risk finding (old ADRs at low pressure → risk of contradicting current axioms undetected) is a concrete example for bubble-clusters-substrate.md §5 Junction Specs — what happens when a bubble falls below minimum internal pressure.

**Evidence structures for weaving**

- R² table (P1 = 0.68, P2 = 0.72, P3 = 0.54 vs task velocity) is a citable quantitative finding for strengthening both bubble-clusters-substrate.md and values-encoding.md hypothesis validation sections.
- The P1+P2+P3 formula definitions are precise operational translations of the bubble-substrate membrane model for values-encoding.md Pattern 5 (Programmatic Governance as Epigenetic Layer).
- The latent documentation case study is an anti-pattern candidate for bubble-clusters-substrate.md §3 Pattern Catalog.

---

### methodology-synthesis.md

**Source**: **Draft** (NOT Final) — note: only non-Final document in Scout 1A corpus; claims here are in-progress, not citable as Final research

**Key claims and patterns**

- Synthesis thesis: EndogenAI is the first operational AI agent design framework that connects the 50-year CS documentation tradition (H4: Knuth literate programming → Nygard ADRs → Martraire living documentation → AGENTS.md) to a session-initialization discipline (H1: encode-before-act), grounded in biological self-organization theory (H2: autopoiesis + NK model), and framed as human-computer augmentation (H3: Engelbart H-LAM/T).
- The four-hypothesis architecture is mutually reinforcing — each hypothesis "both requires and explains the others." Remove any one pillar and the others weaken structurally.
- Four cross-hypothesis dependency pairs with structural argument:
  - H4 × H1 (Encode-Before-Act as Artifact Activation Discipline): AGENTS.md files are literate-programming artifacts (H4); encode-before-act is the protocol that activates them at session scope (H1). "The agent encounters the artifact, reads it as a constitutive specification, and only then issues action tokens."
  - H4 × H2 (Encoding Chain as Organizational Closure Mechanism): the cascade MANIFESTO.md → AGENTS.md → agent files → session prompts is simultaneously a literate-programming artifact hierarchy (H4) AND an autopoietic organizational closure mechanism (H2). Scripts that scaffold or validate the chain are not convenience tooling — they are the fleet's regenerative machinery.
  - H3 × H1 (Substrate-Creation as LAM/T Layer Maintenance): sessions that produce guides/validated encoding updates/committed scripts augment the LAM/T layer; sessions that produce only task outputs consume it. H1 session metric: did encode-before-act posture correspond to a substrate-enhancement commitment at session end? Proxy: commits to `docs/`, `scripts/`, or `.github/agents/` per session.
  - H2 × H3 (Low-K Specialization as Fleet Health Criterion): Kauffman NK model (H2) predicts narrow-mandate agents with low epistatic coupling produce stable specializations. Co-equal LAM/T design pattern (H3) provides the constraint preventing high-K expansion — agents expand depth, not breadth. Single-responsibility agents (Scout, Synthesizer, Archivist) are low-K by design. An agent spanning multiple substrate domains shows measurable high-K drift — an early decoherence signal.
- AGENTS.md files have zero academic prior art as a distinct artifact type despite being directly traceable to Knuth (1984) and Nygard (2011). This is the clearest empirical finding of the four-sprint investigation.
- Novelty scores: H1 Partially Novel/Medium, H2 Partially Novel/Medium-High, H3 Partially Novel/High, H4 Novel/Medium-High. The composite novelty of the four-layer architecture exceeds the sum of individual claims.
- Key strategic concern: AgenticAKM (Dhar et al. 2026, arXiv:2602.04445) are active in the adjacent problem space (LLM-generated ADRs from codebases). "The window for establishing [the four-layer synthesis] first is limited" — estimated 12–18 months before the connection is independently discoverable.
- Open questions: H1 empirical gap (no controlled token-burn A/B comparison); H2 K-value formalization (NK application remains qualitative); BDD mid-chain link (intermediate H4 chain step between ADRs and living documentation lacks a directly synthesized source); H3 substrate ratio measurement (commits to docs/scripts/.github/agents/ per session as LAM/T contribution proxy — not yet validated against actual session logs).
- Recommendations include: formalize H4 lineage in MANIFESTO.md (add Knuth/Nygard/Engelbart citations to the augmentation axiom); extend validate_agent_files.py to check every fleet role has a scaffold template in scripts/ (operationalizing organizational closure as CI gate); state low-K mandate constraint in `docs/guides/agents.md` (fleet stability criterion, not just software hygiene); encode the substrate ratio as a session discipline; design and pre-register minimal H1 comparison study; monitor AgenticAKM trajectory.

**Absent from or underrepresented in primary papers**

- `endogenic-design-paper.md` has H4 CS design lineage and recently added LCF structural-enabler framing, but the four-layer mutual-dependency argument (each hypothesis requires and explains the others; the architecture is stronger than the sum of parts) is the central claim of this synthesis. If this argument is not in endogenic-design-paper.md's Hypothesis Validation section, the paper reads as four independent claims rather than an integrated architecture.
- The H4 × H2 cross-hypothesis pattern (encoding chain = organizational closure mechanism simultaneously) explicitly names `validate_agent_files.py` and `scaffold_agent.py` as the fleet's regenerative machinery — not convenience tooling. This is a novel framing for endogenic-design-paper.md Pattern Catalog that connects the CS legitimation layer (H4) to the biological-dynamics layer (H2) in a single pattern.
- The H3 × H1 substrate ratio metric (commits to docs/scripts/.github/agents/ per session as LAM/T contribution proxy) is a proposed session-level measurement with an unvalidated proxy — this is an open research question that belongs in endogenic-design-paper.md §Open Questions.
- The "practice IS the theory" articulation ("each time an agent reads the encoding chain top-to-bottom, it instantiates all four hypotheses simultaneously") is a synthetic formulation of the methodology that could serve as the opening paragraph or thesis statement of endogenic-design-paper.md.
- The AGENTS.md zero-academic-prior-art finding is the most empirically clean claim from the four-sprint investigation — it should be prominently stated in endogenic-design-paper.md §Hypothesis Validation (H4).
- The AgenticAKM competitive monitoring concern (12–18 month window) is a strategic recommendation not in endogenic-design-paper.md. If the paper is targeting conference submission, this urgency should appear in Recommendations.

**Evidence structures for weaving**

- The four-layer dependency structure diagram/narration is the thesis of endogenic-design-paper.md and should be central, not peripheral.
- The AGENTS.md zero-prior-art finding is a citable empirical finding for H4.
- The four cross-hypothesis patterns (H4×H2, H4×H1, H3×H1, H2×H3) are Pattern Catalog entries for endogenic-design-paper.md.
- **Caveat**: methodology-synthesis.md has **Draft** status — claims should be treated as working hypotheses until this document is promoted to Final.

---

### values-enforcement-tier-mapping.md

**Source**: Final, research_issue #179, date 2026-03-10

**Key claims and patterns**

- Extends the behavioral constraint inventory from enforcement-tier-mapping.md (#174, 68 constraints) to cover values constraints — axiom-preserving, encoding-fidelity, and layer-supremacy rules from MANIFESTO.md, values-encoding.md, epigenetic-tagging.md, external-value-architecture.md, and all agent/skill files.
- 112 constraints total: 68 behavioral (from #174) + 44 values-specific new rows.
- Critical asymmetry: Behavioral T5 ratio = 54% (37/68). Values-specific T5 ratio = 91% (40/44). Values constraints are structurally MORE T5 (prose-only) than behavioral constraints. This is the primary finding.
- Combined T5 total: 77/112 = 69% of all constraints are prose-only.
- Only 4 values constraints are T1/T3: cross-reference ≥1 per agent file, D4 frontmatter, D4 required headings, D4 minimum line count (enforced by validate_agent_files.py and validate_synthesis.py). All other values constraints — including holographic encoding, [4,1] repetition code, axiom positional ordering, watermark phrase integrity, layer supremacy, performative framing, skill cite density — are T5 prose-only.
- 13 T5 values gaps identified with one-line remediations; 6 tractable at T3 with low effort: holographic encoding baseline (G1), D4 Pattern Catalog content check — example + anti-pattern strings (G2, the Goodhart failure), D4 MANIFESTO reference check (G3), axiom positional ordering (G4), watermark phrase integrity (G5), SKILL.md cite density threshold (G6).
- Critical Goodhart failure (rows 88–89): validate_synthesis.py verifies heading `## Pattern Catalog` is present but does NOT verify the section contains a canonical example and anti-pattern. "A document with an empty Pattern Catalog section passes CI." This is the Goodhart's Law encoding failure: the metric (heading presence) is validated without validating the value it proxies (knowledge encoded as concrete examples).
- Adopt wizard gaps (rows 100–106): Core Layer supremacy is NOT validated programmatically at adoption. No `adopt_wizard.py` script exists yet. `client-values.yml` `conflict_resolution` field is informational, not CI-enforced. These are T5 gaps directly connecting to external-values-decision-framework.md recommendations.
- OQ-VE-2 Phase 2 amplify_context.py (rows 93–98): the Phase 2 script that would prepend axiom verbatim (not paraphrased) to session context based on task type is not yet built. Five amplification type-to-axiom mappings are T5 prose in the AGENTS.md lookup table.
- Row 82 is an example of partial uplift: ≥1 density is T1+T3 enforced, eliminating the zero-density case. But the target ≥2.5 threshold for holographic reconstruction is unenforced. "Partial enforcement is better than none — it eliminated the zero-density fleet state — but the gap between minimum and target is not closed."
- R1 (D4 Pattern Catalog content gate, XS effort): extend validate_synthesis.py to check Pattern Catalog section body for "Canonical example" + "Anti-pattern" substrings. R2 (fleet-wide holographic encoding measurement, S effort): extend generate_agent_manifest.py. R3 (MANIFESTO axiom watermark check, XS effort): pygrep hook ensuring D4 docs contain ≥1 axiom name string.

**Absent from or underrepresented in primary papers**

- `values-encoding.md` T1–T4 fidelity test taxonomy (already well-represented per the brief) provides the diagnostic tier structure. But this document reveals the 91% T5 ratio for values-specific constraints — the fact that values enforcement is structurally far weaker than behavioral enforcement is NOT stated in values-encoding.md. This asymmetry (54% behavioral T5 vs 91% values T5) is a key finding for strengthening values-encoding.md §2 H3 (Programmatic Governance as Epigenetic Layer exists) — the current state is that the governance layer is extensively developed for behavioral constraints but embryonic for values constraints.
- The Goodhart failure (D4 Pattern Catalog heading present but content not checked) is a concrete anti-pattern that belongs in values-encoding.md Pattern Catalog as a named pattern of failed encoding — it illustrates how structural proxies can satisfy CI while the underlying value is unenforced.
- The Adopt wizard gaps (rows 100–106) — specifically that Core Layer supremacy and multi-principal hierarchy are T5 prose-only at adoption time — connect the external-values-decision-framework.md conflict taxonomy to the governance gap analysis. This connection is not present in endogenic-design-paper.md, which cites external values architecture but may not name the specific T5 enforcement gaps in that domain.
- The 40 values-specific T5 constraints are a more exhaustive accounting of the governance gap than anything in values-encoding.md §5 Recommendations. The primary paper's back-propagation methodology (weave/link/consolidate) should reference this inventory as the source of gap identifications.
- Row 107 (every SKILL.md must reference AGENTS.md in first section — T5 gap, not enforced at first-section level) and row 108 (SKILL.md cite density ≥0.5 per section — T5 gap) are specific enforcement gaps for the values-encoding.md Pattern 6 (cross-reference density as fidelity metric) that would strengthen that pattern's recommendations.

**Evidence structures for weaving**

- 91% T5 ratio (values constraints) vs 54% T5 ratio (behavioral constraints) is a citable asymmetry for values-encoding.md §2 H3 hypothesis validation — demonstrates the governance gap is larger for values constraints than behavioral ones, confirming H3's urgency.
- The 13 T5 gaps table with one-line remediations is a concrete back-propagatable enumeration for values-encoding.md §5 Recommendations.
- The Goodhart failure (Pattern Catalog heading present, content unchecked) is a named anti-pattern for both values-encoding.md and endogenic-design-paper.md Pattern Catalogs.

---

### Scout 1A — Theme Summary

1. **Enforcement tier asymmetry (behavioral vs values)**: behavioral constraints = 54% T5; values constraints = 91% T5. The governance architecture is robust operationally and embryonic for values fidelity. This asymmetry is absent from `values-encoding.md` and is the largest gap between theoretical claims and actual programmatic state.

2. **Three convergent empirical data sources**: `holographic-encoding-empirics.md` (fleet density census, 49 files), `laplace-pressure-empirical-validation.md` (P1/P2/P3 R² correlations), and `h4-peer-review-synthesis.md` (M1–M5 proxy metrics) all provide quantified measurements of claims stated theoretically in primary papers — direct candidates for Hypothesis Validation sections.

3. **External-values architecture underrepresented**: conflict taxonomy (Type 1–4), ALLOW/BLOCK/ESCALATE outcome tree, Adopt wizard gaps, conservative-interpretation fallback — these are T5 prose-only with no programmatic enforcement. `endogenic-design-paper.md` has LCF framing but not the formal conflict-resolution pattern catalog.

4. **Cross-hypothesis mutual-dependency argument** (note: source is Draft): `methodology-synthesis.md` articulates four cross-hypothesis patterns as the integrated architecture thesis. If `endogenic-design-paper.md` treats the four hypotheses as independent, its central strength is undertold.

5. **Programmatic enforcement as adoption leverage**: `h4-peer-review-synthesis.md` Pattern R2 — T3/T4 enforcement stack directly reduces external team learnability burden — creates a causal link between governance tier work and H4 adoption evidence not stated in any primary paper.
