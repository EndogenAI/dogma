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

---

## Scout 1B — Bridge/Integration + Sprint Docs (10 Thorough)

---

### doc-interweb.md

**Source**: Final, related issue #84, no date field

**Key claims and patterns**

- Validates three design decisions for a `scripts/weave_links.py` tool that programmatically injects Markdown links for registered concept names across the corpus. All three hypotheses confirmed.
- **Q1 (YAML-registry approach)**: YAML registry at `data/link_registry.yml` is confirmed as correct approach. Mirrors `data/labels.yml` precedent consumed by `seed_labels.py`. Scope field restricts injection to relevant paths (prevents self-referential injection). Concept-to-link mapping is reviewable in PRs and auditable by CI. Inline HTML annotations and per-file frontmatter were evaluated and rejected: inline HTML front-loads authoring overhead and produces non-standard Markdown; per-file frontmatter cannot express cross-document concepts and duplicates mappings across N files.
- **Q2 (Idempotency)**: Guaranteed by three mechanisms: (a) existing-link regex check before injection (`is_already_linked()` function scanning for `\[([^\]]+)\]\([^)]+\)` pattern), (b) first-occurrence-per-section rule (tracks concept-name → last-injected-section-index), (c) mandatory idempotency test in test suite. "Existing link wins" rule prevents overriding intentional custom links.
- **Q3 (Seed concepts)**: Six seed concepts confirmed for `data/link_registry.yml` bootstrap: C1=`Endogenous-First` → MANIFESTO.md#endogenous-first, C2=`Algorithms Before Tokens` → MANIFESTO.md#algorithms-before-tokens, C3=`Programmatic-First` → AGENTS.md#programmatic-first-principle, C4=`D4 synthesis` → docs/guides/deep-research.md, C5=`Conventional Commits` → CONTRIBUTING.md#commit-discipline, C6=`Documentation-First` → AGENTS.md#documentation-first. C1/C2 anchor the axiom layer; C3/C6 are operational principles; C4 normalizes a term of art; C5 ensures commit discipline links are consistent.
- Pattern Catalog includes: (1) YAML Registry as Single Source of Truth with aliases and scope fields; (2) Idempotency Guard with Python code fragment showing exact implementation; (3) First-Occurrence-Per-Section Rule with code fragment tracking `seen_in_section: dict[str, int]`; (4) Dry-Run Mode with diff output (`--dry-run` flag required); (5) Audit Integration — `scripts/check_doc_links.py` wired as post-weave CI check.
- Corpus size as of 2026-03-08: 124 `docs/**/*.md` + 33 `.github/agents/*.agent.md` = ~157 text files currently inconsistently cross-referenced.
- Cites `scripts/audit_provenance.py` as the implementation precedent pattern for corpus-reading scripts: `Path.glob` + `read_text` + regex.
- R1: Create `data/link_registry.yml` with 6 seed concepts. R2: Implement `scripts/weave_links.py` with `--dry-run`, idempotency guard, `--scope`. R3: Tests must cover idempotency, scope filtering, and alias matching with `@pytest.mark.io`.
- The governing principle invoked is **Documentation-First** from AGENTS.md — every change to a workflow must be accompanied by documentation; this paper applies that principle to documentation *tooling* itself.

**Absent from or underrepresented in primary papers**

- `values-encoding.md` has no representation of the link-registry / concept-interlinking substrate as an implementation of the Algorithms-Before-Tokens principle. The link registry is exactly the kind of programmatic encoding of a documentation concept (cross-reference density enforcement) that Algorithms-Before-Tokens prescribes. This is a missing canonical example for the "Encoding Inheritance Chain" pattern.
- `bubble-clusters-substrate.md` discusses membrane permeability and reference edges between nodes but has no treatment of how the cross-reference interlinking is maintained or enforced programmatically. The link registry plus weave_links.py is the practical substrate-level enforcement mechanism that gives the "reference edge" topology its implementation.
- `endogenic-design-paper.md` likely discusses Documentation-First as an operational principle but does not connect it to the programmatic interlinking toolchain as a concrete instantiation of the documentation-first posture applied to documentation itself. The reflexivity here (docs about docs, automation about automation standards) is a philosophically significant point about the endogenic methodology.
- The first-occurrence-per-section rule and scope-filtering patterns are DSL-adjacent encoding patterns not present in `workflow-formula-encoding-dsl.md` (which is the designated home for such patterns) — slight inconsistency in where pattern catalog lives.
- The `weave_links.py` script recommendation (R2) connects directly to `measure_cross_reference_density.py` from `values-encoding.md` §5 (Pattern 2 cross-reference density). The two tools together — weave then measure — would form a complete cross-reference feedback loop that neither paper addresses as a combined system.

**Evidence structures for weaving**

- The six seed concepts table (C1–C6) is a concrete, citable list of axiom-layer concepts and their canonical targets — directly usable as an illustrative example of the Algorithms-Before-Tokens principle in `values-encoding.md`.
- The Python `is_already_linked()` function code fragment is a canonical example of T3-style programmatic enforcement of a documentation standard — suitable for the Pattern Catalog of `values-encoding.md` or `endogenic-design-paper.md`.
- The corpus-size measurement (157 text files, inconsistently cross-referenced) is an empirical baseline for the "navigationally opaque" claim about cross-reference underrepresentation — usable in `endogenic-design-paper.md` or `values-encoding.md` to ground the Endogenous-First claim.

---

### topological-audit-substrate.md

**Source**: Final, research_issue #170, closes_issue #170, date 2026-03-10

**Key claims and patterns**

- Systematically maps the endogenic substrate as a three-dimensional topological structure using graph-theoretic formalism: $\mathcal{T} = (V, E, F)$ where V=vertices, E=edges, F=faces.
- **75 total vertices**: 8 agents (Executive Researcher, Scout, Synthesizer, Reviewer, Archivist, Orchestrator, Docs, Review), 41 scripts (categorized: source management ×4, validation/compliance ×6, agent/fleet tools ×5, session/execution ×6, scaffolding ×4, data processing ×3, migration/utilities ×5, documentation ×8), 22 documentation subsystems, 4 external systems (GitHub, open-source tools, academic databases, user/human operators).
- **52 documented edges** with full metadata. Five semantic edge types: (1) Control Flow (Agent→Script): trigger, parameters, return semantics, asynchrony; (2) Data Flow (Script↔Filesystem): operation, precondition, postcondition; (3) Reference (Document→Document): citation type (cite/extend/depends-on/supersedes); (4) Enforcement (Tier→Constraint): scope, mechanism, failure mode; (5) Dependency (Issue→Issue): direction (blocks/depends-on/subtask).
- **15 faces identified**: 9 structural (F1=Foundational axioms/MANIFESTO.md, F2=Operational constraints/AGENTS.md layer, F3=Role definitions/.github/agents/, F4=Skills/.github/skills/, F5=Execution layer/scripts/, F6=Testing/tests/, F7=Documentation/docs/, F8=CI/Automation/.github/workflows/, F9=Configuration/pyproject.toml etc.), 6 functional enforcement tier faces (T0–T5).
- **Structural coherence**: 67% of edges remain within subsystem boundaries; 33% cross subsystem boundaries. The paper notes optimal for well-engineered systems is 30–40% cross-boundary — the substrate is within that range.
- **Active vertex distribution**: 34 vertices (45%) show ≥5 edges/month (highly active); 23 vertices (31%) show <2 edges/month (latent/ceremonial). 0 isolated vertices.
- **Core integration hubs with highest edge counts**: validate_synthesis.py (18+ edges), validate_agent_files.py (16+ edges), prune_scratchpad.py (12+ edges), fetch_source.py (11+ edges). Executive Orchestrator agent has 20+ edges — highest single vertex.
- **Graph metrics**: Sparsity index s ≈ 0.019 (1.9% of possible edges, healthy for large systems). Mean edges per vertex: 6.9. Clustering coefficient: Execution layer ≈ 0.42, Guidance layer ≈ 0.38, Testing layer ≈ 0.55.
- **H1 (CONFIRMED)**: 75+ vertices, 52+ edges; structured topology is real and measurable.
- **H2 (CONFIRMED)**: Each face corresponds to distinct mutation rates — MANIFESTO.md changes monthly or less; AGENTS.md changes weekly; scripts change daily. Not accident but reflects roles.
- **H3 (CONFIRMED)**: Scripts with highest connectivity (validate_synthesis.py, validate_agent_files.py) are cross-subsystem validators. Information concentrates at guarded enforcement channels.
- Formal definitions provide edge preconditions and postconditions — e.g., Scout→fetch_source.py edge: Precondition=URL is https://, not private IP; Postcondition=.cache/sources/slug.md exists with _UNTRUSTED_HEADER.
- **Anti-pattern**: Isolated documentation subsystems — old ADRs and archived research stubs with <2 edges/month. Without active edges, they can drift from MANIFESTO.md without membrane pressure forcing reconciliation.
- Recommendation 2: Introduce "Executive Planner" to distribute Orchestrator's 20+ edge load. Recommendation 3: Formalize Interface Layer document specifying which AGENTS.md constraints map to which scripts/CI gates — explicitly identifying T5→T3 uplift pathway. Recommendation 4: CI check computing topological statistics on every commit (sparsity index, hub degree distribution, clustering coefficient) as drift-monitoring.
- A Mermaid topology diagram with six subsystem layers is included.

**Absent from or underrepresented in primary papers**

- `bubble-clusters-substrate.md` asserts membrane topology and bubble-cluster structure theoretically, but this document provides the first complete empirical vertex/edge/face inventory. The §5 Junction Specs in bubble-clusters-substrate.md (describing interface boundaries between clusters) now has quantitative grounding: 15 faces, 52 edges, T0–T5 functional faces. The junction specs map directly onto the functional face enumeration here.
- `bubble-clusters-substrate.md` discusses "Laplace pressure" and boundary stability, but no prior paper maps this to the enforcement tier structure. The functional faces (T0–T5) in this document are exactly the pressure layers that maintain membrane boundaries — T3 pre-commit as a membrane enforcer, T0 runtime gate as a boundary rejection mechanism.
- `values-encoding.md` discusses the encoding inheritance chain (MANIFESTO.md → AGENTS.md → agent files → session prompts) but has no topological quantification. This document provides the first measurement infrastructure for how many reference edges exist between those layers, what their direction is, and how many cross-subsystem vs. intra-subsystem edges exist.
- `endogenic-design-paper.md` likely does not have the formal graph-theoretic treatment ($\mathcal{T} = (V, E, F)$) as a framework for describing fleet topology. This is a distinct contribution: it gives the methodology a mathematical formalism beyond metaphor.
- The "latent vertex" anti-pattern (isolated documentation with <2 edges/month) is not called out in any primary paper as a source of substrate drift. This is an important gap in the bubble-clusters model — bubbles can go inert without active membrane pressure, and this document provides an empirical measurement for inertness.
- The ratio 67%/33% (intra/cross-subsystem edges) as a structural coherence metric is a new empirical result not present in any primary paper. Could anchor the "optimal architecture" discussion in endogenic-design-paper.md.

**Evidence structures for weaving**

- The 75-vertex, 52-edge, 15-face inventory table is a directly citable empirical data structure for bubble-clusters-substrate.md §2 or §5 (Hypothesis Validation and Junction Specs).
- The enforcement tier faces (T0–T5) as functional faces provide a bridge between enforcement-tier-mapping.md's constraint inventory and bubble-clusters-substrate.md's membrane topology model — they are the same structure described from two different analytical angles.
- The graph sparsity statistic (s ≈ 0.019) and the clustering coefficients by layer are quantitative evidence for the "coherent, multi-scale architecture" claim in endogenic-design-paper.md.
- The Mermaid topology diagram is a visualization asset for any primary paper that makes claims about the architecture.
- The formal $\mathcal{T} = (V, E, F)$ definition and five edge-type taxonomy are foundational vocabulary that values-encoding.md could adopt to describe the "value signal provenance" DAG (see value-provenance.md below).

---

### value-provenance.md

**Source**: Final, no research_issue, no date field

**Key claims and patterns**

- Establishes chain-of-custody link between agent files and the specific MANIFESTO.md axioms that govern their instructions. This is distinct from cross-reference density (#54: how many lines reference foundational docs) and drift detection (#71: phrasal alignment with watermarks). Provenance tracing establishes a "derived from" relationship that is explicit and machine-checkable.
- **H1 (REFUTED/refined)**: Instruction-level provenance (linking each instruction paragraph to its governing axiom) would require semantic embedding or manual annotation of every instruction paragraph — out of scope. File-level provenance via `governs:` YAML frontmatter is feasible with pure stdlib ≤50 lines: extract frontmatter, parse `governs:` list, normalize to lowercase-hyphenated names, compare against MANIFESTO.md H2/H3 headings.
- **H2 (CONFIRMED)**: Frontmatter annotation (Format B) is the lowest-overhead viable format. Requires zero infrastructure changes; reuses existing frontmatter parsing from `validate_agent_files.py`; invisible in rendered output; compatible with existing CI gate. Evaluated against: Format A (inline HTML comment, higher authoring cost for equivalent coverage) and Format C (external JSON manifest, drifts out of sync).
- **H3 (CONFIRMED)**: All current agent files are provenance-orphaned. `fleet_citation_coverage_pct = 0.0` at baseline. Every agent lacks a `governs:` frontmatter field. This is the highest-priority follow-up: add `governs:` to agent file authoring standard and run audit in CI.
- **Pattern P1 — File-Level Provenance via `governs:` Annotation**: Cross-domain precedent in Shepard's Citations (LexisNexis), `pyproject.toml` `dependencies:` field, and RDF/PROV-O ontology (`prov:wasDerivedFrom` predicate). YAML frontmatter is the idiomatic analog. Controlled vocabulary (MANIFESTO.md H2/H3 headings) prevents citation drift to non-existent axioms.
- **Pattern P2 — Orphan Detection as First CI Gate**: Static analysis analogy — mypy F821 undefined-name check. Orphan detection is O(N) over filesystem, no semantic analysis required. `audit_provenance.py --format summary` as non-blocking CI report step (advisory first, blocking only after authoring standard updated).
- **Pattern P3 — Vocabulary-Constrained Citations**: Legal citator precedent (Blue Book abbreviations, Shepard's filed-case-only citations). `audit_provenance.py` validates `governs:` values against normalized MANIFESTO.md heading set; emits `unverifiable` list for unknown axiom names. Closes feedback loop: authoring → validation → rejection of unknowns.
- The distinction between H4 "holographic encoding" (Pattern 6 in values-encoding.md) and practical provenance tracking: holographic encoding means every file re-encodes all values; provenance tracing means each file *declares which axioms it was derived from*. Both are useful; only the latter is automatable without NLP at the current toolchain level.
- **R1 (Immediate)**: Add `governs:` to `.agent.md` authoring standard and as required key in `validate_agent_files.py`. Effort xs. R2 (Sprint 2): Run `audit_provenance.py` as non-blocking CI report; track `fleet_citation_coverage_pct` alongside `avg_cross_ref_density`. R3 (Sprint 3+): Soft warning for `unverifiable_count > 0`. R4 (Post-baseline): Combine with embedding-similarity drift (#71 Approach B) for instruction-level provenance traces.

**Absent from or underrepresented in primary papers**

- `values-encoding.md` Pattern 6 (Holographic Encoding, H4) describes every file re-encoding all values, but this document introduces a complementary and more tractable concept: *provenance declaration* (which axioms was this file derived from?). This distinction is absent from values-encoding.md and could anchor a new pattern or a clarifying distinction in the Pattern Catalog.
- `values-encoding.md` §5 (Fidelity Test Taxonomy) covers T1–T4 signal types but does not mention chain-of-custody as a measurement dimension. Provenance coverage (0% at baseline vs. 100% as target) is a new metric for the fidelity taxonomy.
- `endogenic-design-paper.md`'s methodology discussion presumably covers how the encoding chain is maintained, but it likely does not describe the `governs:` mechanism as a concrete implementation for making derivation relationships explicit and machine-checkable. The "100% orphaned at baseline" finding provides a stark quantitative gap baseline.
- The RDF/PROV-O (`prov:wasDerivedFrom`), Shepard's Citations, and package dependency graph precedents are cross-domain evidence for the value-provenance approach that would strengthen the "Endogenous-First draws from best external practices" claim in any primary paper.
- `bubble-clusters-substrate.md` discusses how values flow through membranes and substrates but has no treatment of provenance tracing as a mechanism for verifying that flow happened correctly. The `governs:` annotation is the verification mechanism for inter-layer value transmission.
- The "holographic encoding vs. provenance tracing" distinction (re-encoding all values vs. declaring which axioms you derive from) is a nuance absent from `values-encoding.md` that would clarify what Pattern 6 is and isn't claiming.

**Evidence structures for weaving**

- The `fleet_citation_coverage_pct = 0.0` baseline measurement is a stark empirical gap result for `values-encoding.md` §2 H3 (Programmatic Governance layer).
- The `prov:wasDerivedFrom` / legal citator cross-domain evidence provides a principled external framing for the governance-chain-of-custody concept applicable in `endogenic-design-paper.md` or `values-encoding.md` Recommendations.
- The file-level vs. instruction-level provenance tracing distinction is a precision-of-claim clarification that would improve `values-encoding.md`'s H4 (Holographic Encoding) articulation.
- Pattern P3 (vocabulary-constrained citations that prevent citation drift) maps directly onto `values-encoding.md`'s discussion of drift detection — provenance vocabulary constraint is the complement to drift detection's phrase-alignment approach.

---

### sprint-A-h1-novelty.md

**Source**: Draft, no research_issue/closes_issue

**Key claims and patterns**

- **H1 verdict: Partially Novel — Medium Confidence.** The encode-before-act pattern has no direct named antecedent in surveyed literature. Elements exist (pre-reasoning context assembly in Xu et al., ongoing context management in Mei et al.) but no work frames encode-before-act as a *coding-agent session-initialization discipline* targeting token efficiency and session coherence as primary outcomes.
- Five sources surveyed: ReAct (Yao et al. 2022, arXiv:2210.03629), Context Engineering Survey (Mei et al. 2025, arXiv:2507.13334), Everything is Context (Xu et al. 2025, arXiv:2512.05470), Generative Agents (Park et al. 2023, arXiv:2304.03442), Zep (Ramirez 2025, arXiv:2501.13956).
- **ReAct (foundational baseline)**: Explicitly reactive Thought→Action→Observation loop. No pre-session encoding phase. Useful as the baseline from which encode-before-act structurally diverges: ReAct accumulates context through action cycles; encode-before-act front-loads it. ReAct's absence of initialization framing is significant.
- **Mei et al. (Context Engineering Survey 2025)**: Most comprehensive treatment. Frames context as *ongoing management* — continuous process of fetching, filtering, compressing, updating across agent lifetime. Sharpest structural contrast with H1: Mei et al. = flow problem; H1 = initialization problem. Encode-before-act does not appear under any name in this survey. Absence from a current comprehensive survey is meaningful evidence of a prior art gap.
- **Xu et al. (Everything is Context 2025, arXiv:2512.05470)**: Constructor → Loader → Evaluator pipeline. Constructor phase explicitly assembles context before reasoning begins — closest prior art. Difference: Xu et al. are concerned with context *quality* (relevance, completeness, noise ratio); H1 is concerned with *when* and *from which knowledge layer* (system knowledge, not episodic memory or task-driven retrieval). Constructor phase is a mechanism; encode-before-act is a discipline.
- **Park et al. (Generative Agents)**: Retrieves episodic memories before behavior planning — superficially resembles pre-action context loading. Critical boundary: episodic (what did this agent experience?) vs. system knowledge (what does this agent know about its operating environment, tools, conventions?).
- **Gap confirmed**: No pattern in the corpus names, formalizes, or empirically measures the combination of (a) session-start timing, (b) system knowledge as source, (c) token waste and coherence as target metrics, specifically for coding agents.
- Three partially overlapping patterns identified but structurally distinct: Fetch-Before-Generate (reactive, task-triggered, external docs), Constructor Phase (quality optimization, not timing/source discipline), Episodic Pre-Planning Retrieval (episodic vs. system, social simulacra vs. coding agents).
- **Draft status**: "Do not assert quantitative advantages until a controlled comparison is designed and executed." Conceptual novelty established; empirical novelty deferred.
- Recommended next steps: (1) Formalize encode-before-act definition; incorporate into MANIFESTO.md §Endogenous-First and AGENTS.md Programmatic-First. (2) Design measurement protocol for controlled comparison. (3) Engage with Xu et al. Constructor phase as mechanism; encode-before-act as discipline applied at session scope.

**Absent from or underrepresented in primary papers**

- `endogenic-design-paper.md` likely asserts encode-before-act as H1 but this sprint document provides the full prior-art survey grounding. The absence from Mei et al.'s 2025 comprehensive survey is a high-quality evidentiary argument for novelty that should be cited explicitly in the primary paper.
- `values-encoding.md` describes the encoding inheritance chain but does not position it as a session-initialization discipline in the context engineering literature. The Constructor phase / fetch-before-generate terminology from the external literature is not present in any primary paper — this vocabulary bridge is absent.
- The distinction between encode-before-act *as a discipline* (timing + source + target) and the Constructor phase *as a mechanism* is a precision that strengthens the novelty claim and is absent from any primary paper.
- `endogenic-design-paper.md` likely does not formally defer the empirical claim — "reduces token waste" — to measurement protocol status. The sprint explicitly marks this as a DEFER. This epistemic discipline (conceptual novelty confirmed; empirical novelty needs controlled measurement) should be reflected in the primary paper.

**Evidence structures for weaving**

- The 5-source prior art survey with specific arXiv identifiers and verdict statements (absent, baseline, closest prior art, etc.) is directly citable content for `endogenic-design-paper.md` §2 Hypothesis Validation H1.
- The "absence from Mei et al.'s 2025 comprehensive survey" argument is the strongest single piece of evidence for H1 novelty — usable as an anchor sentence in any primary paper.
- The Constructor phase / encode-before-act boundary articulation ("mechanism vs. discipline") is a precision argument for both `endogenic-design-paper.md` and `values-encoding.md`.

---

### sprint-B-h2-morphogenetic.md

**Source**: Draft, no research_issue/closes_issue

**Key claims and patterns**

- **H2 verdict: Partially Novel — Medium-High Confidence.** Joint operationalization of Turing (1952) reaction-diffusion + Maturana & Varela (1980) autopoiesis/structural coupling + Kauffman (1993) NK fitness landscape as a *prescriptive fleet design framework* is absent from surveyed literature. Each source has prior art in isolation; the synthesis does not.
- Three primary sources, three prior art signals. Key prior art: Fernandez (2016, arXiv:1606.00799) applies autopoiesis to MAS as a *modeling tool* for systems modeling an external dynamical environment. H2's critical inversion: treating the fleet itself as an autopoietic system whose organizational closure must be preserved *by design*. This direction is not present in Fernandez or any identified successor.
- **Maturana & Varela (1980)**: Organizational closure criterion — autopoietic system continuously regenerates the components and boundaries that define it — maps onto fleet design precisely: when agents are added/removed/retooled, the fleet's organizational identity (role graph, coupling structure, value encoding) must be regenerated rather than merely updated. *Structural coupling* (adapts to perturbations while maintaining organization) provides theoretical basis for adaptive specialization without organizational drift.
- **Kauffman NK model**: K (epistatic connections per node) controls landscape ruggedness. Low K → modular stable optima accessible by local search. High K → correlated, deceptive landscapes. Applied to fleet: agents with narrow role (low K) form modular stable specializations locally optimizable; high-K agents (broad mandate, many dependencies) resist stable specialization, require fleet-level coordination. NK analysis not previously applied to AI fleet role design.
- **Turing (1952)**: Reaction-diffusion dynamics demonstrate stable global patterns (specialization gradients, role clusters) can arise purely from local activator-inhibitor rules without central coordination. AGENTS.md encoding chain functions as activator-inhibitor cascade: high-level values inhibit local drift while enabling local specialization. Cross-reference density metric in validate_agent_files.py is an operationalization of emergent coherence from local encoding rules.
- Prior art signals: Wu & Or (2025, arXiv:2505.00018) invoke autopoiesis for HAACS (human-AI agent collectives) as position paper with no formal operationalization. Alicea & Parent (2021, arXiv:2109.11938) apply morphogenesis to individual agent cognition, not fleet architecture. Both confirm vocabulary entry into discourse; neither operationalizes prescriptively or combines all three frameworks.
- **Four design patterns**: (1) Organizational Closure as Role-Boundary Constraint — every role must be regenerable from fleet's own processes (`scaffold_agent.py` and `validate_agent_files.py` are closure mechanisms); (2) Structural Coupling Without Organizational Drift — changes to agent files must propagate through encoding chain; direct edits sever coupling; (3) Low-K Specialization as Stability Strategy — single-responsibility agents are the NK principle enacted as architecture; (4) Emergent Coherence from Local Encoding Rules — cross-reference density is the operationalization.
- **Weakness**: H2 stronger on conceptual distinctiveness than formalization. The K-value → agent dependency graph mapping remains qualitative. "A rigorous H2 requires mapping agent dependency graphs to K-values and demonstrating that low-K fleet configurations outperform high-K configurations on stability and specialization metrics."
- **Recommended next steps**: (1) Formalize K-value mapping: define how agent dependency graph structure maps to Kauffman K; apply to current fleet to identify high-K agents warranting decomposition. (2) Operationalize organizational closure as CI check: validate_agent_files.py already checks encoding fidelity; extend to check every role has a corresponding scaffold template in scripts/ (closure of regenerative machinery). (3) Draft H2 design principles section for docs/guides/agents.md: three principles — closure, structural coupling, low-K specialization — stated operationally.

**Absent from or underrepresented in primary papers**

- `endogenic-design-paper.md` presumably contains the H2 hypothesis but this sprint document provides the systematic prior art survey with specific sources and a precise articulation of the novel contribution (direction of autopoiesis application). This survey backing is absent from the primary paper.
- `bubble-clusters-substrate.md`'s bubble-cluster model is architecturally convergent with the autopoietic closure concept — bubbles are bounded self-maintaining units — but does not cite Maturana & Varela's formalization or map organizational closure onto the bubble boundary concept.
- `endogenic-design-paper.md` and `bubble-clusters-substrate.md` presumably discuss single-responsibility roles without naming the NK landscape as the formal basis. Low-K specialization as a stability criterion (not merely a separation-of-concerns preference) provides quantitative grounding absent from both.
- The "emergent coherence from local encoding rules" pattern (Turing reaction-diffusion applied to AGENTS.md cascade) provides an explanation for *why* the encoding chain produces coherent fleet structure — this causal mechanism is likely stated as fact in primary papers without the theoretical grounding.
- `scaffold_agent.py` and `validate_agent_files.py` as "closure mechanisms" (the regenerative machinery that enables organizational closure) is a reframing of utility scripts as architecturally load-bearing structures. This is absent from primary papers.
- The prior art signal from Wu & Or (2025) and Alicea & Parent (2021) confirms the morphogenetic vocabulary is entering multi-agent discourse — a timeliness argument for establishing H2 now — absent from primary papers.

**Evidence structures for weaving**

- The three-framework combination table (Turing, Maturana & Varela, Kauffman NK) with specific paper citations and fleet-design applications is a directly citable structure for `endogenic-design-paper.md` §2 H2 Hypothesis Validation.
- The autopoiesis inversion argument (prior art uses autopoiesis to describe how MAS models external systems; H2 treats the fleet itself as autopoietic) is a falsifiable, precise novelty claim for the primary paper.
- The four design patterns — especially Organizational Closure as Role-Boundary Constraint with `scaffold_agent.py` as the concrete mechanism — are canonical examples for `endogenic-design-paper.md` §3 Pattern Catalog.
- The low-K = stability / high-K = ruggedness formalism from Kauffman NK could ground the "single-responsibility agent" design guidance in `endogenic-design-paper.md` §4 Recommendations.

---

### sprint-C-h3-augmentive.md

**Source**: Draft, no research_issue/closes_issue

**Key claims and patterns**

- **H3 verdict: Partially Novel — High Confidence.** Augmentation lineage (Engelbart/Bush) applied to contemporary AI is established (Tong 2026). The specific *substrate-creation inversion* — AI agents whose primary output is the structured knowledge substrate that then governs future agent behavior — is absent from all surveyed literature including Tong.
- Three primary sources, one prior art signal. Bush (1945) "As We May Think," Engelbart (1962) "Augmenting Human Intellect," Tong (2026, arXiv:2601.06030).
- **Bush (1945)**: Memex as "enlarged intimate supplement to memory" with associative trails. Trail-blazer profession explicitly named — someone whose primary work is building knowledge structures for others to traverse rather than producing first-order outputs. Limiting axiom: "for mature thought there is no mechanical substitute" — machines extend reach; they do not replace judgment. EndogenAI relevance: (1) trail-blazer maps onto agents producing AGENTS.md updates, research syntheses, workplans — building associative trails not completing tasks; (2) limiting axiom is enacted architecturally — human judgment encoded in MANIFESTO.md, agents operate within that encoding but do not regenerate it from first principles.
- **Engelbart (1962)**: H-LAM/T system (Human + Language + Artifacts + Methodology + Training). Language, artifacts, methodology, training are *co-equal components* of cognitive reach — not tools in service of the human but constitutive parts of augmented intellect. Improving methodology improves the intellect regardless of biological capacities. AGENTS.md cascade, scripts/, guides/ are the LAM/T layer — not supporting infrastructure, they *are* the work. When an agent updates AGENTS.md or commits a guide, it modifies the methodology component of the augmentation unit.
- **H3 contribution**: When agent outputs reshape the LAM/T layer that governs subsequent agents, the relationship is *co-authorship-of-the-augmentation-system-itself*, not standard performance augmentation. This feedback loop (agent outputs → LAM/T layer → future agent outputs) has no precedent in surveyed augmentation literature.
- **Tong (2026)**: Traces Licklider→Engelbart lineage to contemporary LLMs; demonstrates augmentation framing survives foundation model transition. Terminates at user-performance boundary: AI augments what humans do. H3 diverges here: "What does the AI produce?" When AI's primary deliverable is a substrate artifact (guide, convention file, validated encoding), and that artifact governs AI's own subsequent behavior, relationship is no longer augmentation-of-performance but co-authorship.
- **Four design patterns**: (1) Substrate-First Output Discipline (Bush) — agent work assessed by whether it produces durable trail artifacts, not just task completion. Sessions closing issues without updating guides/scripts/AGENTS.md produce task output without substrate output — consume tokens without augmenting LAM/T layer. Fetch-before-act and encode-before-act postures are concrete implementations. (2) Co-equal LAM/T Layer Design (Engelbart) — scripts, agent files, guides are not supporting infrastructure but components of the augmentation unit with same design status as human-facing outputs. Neglecting infrastructure is LAM/T degradation. (3) Judgment-Layer Separation (Bush) — encoding chain is the architectural expression of Bush's limiting axiom: human judgment irreducible. Agents read MANIFESTO.md but do not regenerate it. Allowing agents to rewrite top-level values from session context collapses augmentation into automation. Constraint is asymmetric by design. (4) Constraint-as-Partnership (Engelbart) — encoding partnership as a constraint (agents must read substrate before acting) is the mechanism by which LAM/T layer remains load-bearing rather than advisory. "An agent fleet that treats AGENTS.md as optional guidance is not operating as an augmentation unit; it is operating as a set of independent task executors."
- **Recommended next steps**: (1) Draft substrate-creation distinction as named section in docs/guides/mental-models.md; define user-performance augmentation vs. substrate-creation augmentation with H-LAM/T framing as anchor. (2) Audit session outputs for substrate ratio: commits to docs/, scripts/, .github/agents/ per session as proxy for LAM/T layer contribution. (3) Add Engelbart H-LAM/T citation to MANIFESTO.md's augmentation axiom.

**Absent from or underrepresented in primary papers**

- `endogenic-design-paper.md` likely discusses the augmentation lineage but this sprint document provides the precise prior art gap — Tong (2026) is the nearest precedent and the exact location where H3 diverges (user-performance vs. substrate-creation). This is absent from the primary paper.
- `endogenic-design-paper.md` may have Bush and Engelbart citations but is unlikely to have the specific argument that the trail-blazer profession maps onto agent work producing AGENTS.md updates — this precise mapping is absent.
- `values-encoding.md` discusses the encoding inheritance chain as a values-propagation mechanism but does not frame it through Engelbart's H-LAM/T as a co-equal augmentation architecture. The co-equal framing (scripts and guides are not supporting infrastructure but constitutive parts of the augmented intellect) would strengthen the "Endogenous-First" rationale: these files matter because they are the LAM/T layer.
- The "constraint-as-partnership" claim — that encoding the partnership as a pre-condition on agent action distinguishes an augmentation unit from a set of independent task executors — is the sharpest operational formulation in the corpus. This is likely not stated this precisely in any primary paper.
- Bush's limiting axiom ("for mature thought there is no mechanical substitute") as a design constraint — enacted through the asymmetric read-not-write access to MANIFESTO.md — provides a principled theoretical grounding for the judgment-layer separation that is absent from primary papers.
- The substrate ratio audit metric (commits to docs/, scripts/, .github/agents/ per session as a proxy for LAM/T contribution) is a new measurement proposal not present in any primary paper's recommendations.

**Evidence structures for weaving**

- The four patterns (Substrate-First Output, Co-equal LAM/T, Judgment-Layer Separation, Constraint-as-Partnership) with Bush/Engelbart citations are canonical examples with strong external theoretical grounding for `endogenic-design-paper.md` §3 Pattern Catalog.
- The Tong (2026) divergence argument ("terminates at user-performance boundary; H3 crosses it") is the single sharpest novelty argument across all four sprint documents — directly citable in `endogenic-design-paper.md` §2 H3 Hypothesis Validation.
- Bush's limiting axiom as architectural design criterion (asymmetric access to MANIFESTO.md) is a memorable formulation for `values-encoding.md` or `endogenic-design-paper.md` to anchor the judgment-layer arguments.
- The "co-authorship of the augmentation system itself" formulation is precisely the thesis statement that could distinguish `endogenic-design-paper.md` from prior work on AI augmentation.

---

### sprint-DE-h4-cs-lineage.md

**Source**: Draft, no research_issue/closes_issue

**Key claims and patterns**

- **H4 verdict: Novel — Medium-High Confidence.** The individual antecedents (Knuth 1984, Nygard 2011, Martraire 2019, Czarnecki & Eisenecker 2000) are documented and mutually connected. What does not exist is a paper chaining all four traditions together and applying the chain to justify AI agent context files (AGENTS.md / CLAUDE.md artifact class) as principled CS artifacts. The terminal synthesis is entirely absent.
- **H4 is the most sharply novel finding** because the gap is not diffuse or scale-dependent — it is a *specific conceptual chain that no published work has attempted to close*.
- **Lineage chain is tight and documentable**: Knuth (1984) → Nygard (2011): Literate programming established programs written primarily for human readers; machine is secondary audience. Artifact is simultaneously executable and explanatory. ADR format inherits this at the decision layer: encode *why* decisions were made with full context before they calcify into implicit assumptions. Nygard (2011) → Martraire (2019): Living Documentation explicitly extends Knuth lineage to continuous-delivery era. Martraire explicitly cites literate programming as intellectual progenitor; extends to test suites, BDD scenarios, code annotations. ADRs appear in Martraire's taxonomy as decision-level living documents. Martraire (2019) → Encode-Before-Act for AI Agents: AGENTS.md / CLAUDE.md artifact class is a direct structural descendant of living documentation. These files co-evolve with the system; are the executable specification that an AI agent reads before issuing any action token. Mechanism is identical: human-readable artifact governing agent behavior, living in repository, read before work begins. The explicit identification of this structural descent is absent from literature. Czarnecki & Eisenecker (2000) as independent corroboration: generative programming's specification IS the primary artifact; generators derive executable code from it. In endogenic methodology, AGENTS.md and guides are the specification from which agent behavior is derived.
- **Terminal step novelty**: arXiv search — zero results for "literate programming AI agent workflow", "living documentation encode context LLM", "AGENTS.md instructions design", "CLAUDE.md context file". AGENTS.md / CLAUDE.md artifact class has no academic prior art as a named, analyzed artifact.
- **AgenticAKM (Dhar et al. 2026, arXiv:2602.04445)**: Nearest prior art — LLMs generating ADRs from codebases at scale. Operates in *reverse direction* (mining codebases → produce ADRs after the fact) vs. H4's *encode-first direction*. No reference to literate programming, living documentation, or pre-session encode-before-act discipline. Best cited as evidence that the encode-before-act lineage is *imminently discoverable* — elevates urgency of establishing it first.
- **Directionality is the sharpest point**: All CS antecedents share encode-first-act-later direction: literate programming produces document before compiler runs; ADRs record decision before rationale calcifies; living documentation generates from specification as it evolves; encode-before-act reads specification before first action token. This recurring 50-year pattern had not been named as such.
- **Table mapping four CS antecedents**: Lists for each: Core Artifact, Encode-Before-Act Mechanism, Gap Before AI Application. Terminal row is Encode-Before-Act for AI Agents (EndogenAI 2026) with AGENTS.md/CLAUDE.md as the core artifact.
- **Why H4 is most novel**: H1–H3 face framing/combination gaps; H4 faces an *identification gap* — the chain exists but has never been drawn. Falsifiable: either a paper traces this chain or it does not. Exhaustive arXiv search produced zero results.
- **Open questions**: (a) BDD/Specification-by-Example mid-chain slot — Scout findings do not include direct BDD source; connection is implicit in Martraire; dedicated BDD source (Cucumber docs, Adzic/North writings) needed to strengthen chain; (b) Generative Programming weight — Czarnecki & Eisenecker specification artifacts are DSLs not natural-language guides; the natural-language register of AGENTS.md may be a meaningful distinction or surface difference; (c) AgenticAKM as threat or support to monitor.

**Absent from or underrepresented in primary papers**

- **The BDD mid-chain link** is explicitly identified as a gap in sprint-DE. This connects to Scout 1A's observation that `methodology-synthesis.md` notes "H4 lineage BDD mid-chain link (between ADRs and living documentation — gap in methodology-synthesis.md)." Sprint-DE confirms this gap is still open. `endogenic-design-paper.md` H4 section will be weak at this point unless a BDD source is obtained.
- The four CS antecedents table — specific paper citations, mechanisms, and gaps — is the evidence structure for `endogenic-design-paper.md` §2 H4 Hypothesis Validation but is likely absent from the primary paper itself.
- `values-encoding.md` encoding inheritance chain could be reframed through the literate programming lineage: the chain is the most recent expression of a 50-year CS pattern (Knuth → Nygard → Martraire → AGENTS.md). This historical grounding is absent.
- The "principled answer to the workaround objection" (AGENTS.md files are not informal tribal knowledge artifacts — they are the most recent expression of a 50-year encode-first CS pattern) is a defensive framing for `endogenic-design-paper.md` that is absent.
- AgenticAKM (Dhar et al. 2026) as the "reverse direction" prior art — mining codebases to produce ADRs after the fact — is an important contrast case for `endogenic-design-paper.md` that probably isn't cited.

**Evidence structures for weaving**

- The four-antecedent table (Knuth 1984/ADR 2011/Living Docs 2019/Generative Programming 2000 + encode-before-act terminal row) is the primary evidence table for `endogenic-design-paper.md` §2 H4.
- The zero-result arXiv search finding (four distinct search queries, zero results) is the falsifiability anchor — citable as direct evidence of identification gap.
- AgenticAKM (arXiv:2602.04445) as reverse-direction operation vs. encode-before-act's forward direction is a contrast case directly usable in `endogenic-design-paper.md`.
- The directionality claim ("all four antecedents share encode-first") is a unifying framework that organizes the 50-year pattern — strong anchor for any primary paper making the H4 claim.

---

### phase-5-recommendations-audit.md

**Source**: Complete, no research_issue/closes_issue, date 2026-03-10

**Key claims and patterns**

- **Audit finding**: 100% of Phase 1–4 recommendations tracked. Zero untracked gaps. Phase 6 preconditions satisfied.
- **Scope**: 68 total files in docs/research/ scanned; 21 Phase 1–4 deliverables analyzed; 20 distinct recommendations extracted; 25 GitHub issues mapped; 5 intentional duplicates for overlap coverage.
- **Phase domain breakdown**: Endogenic Design (3 papers) → 5 recommendations (#167–#174); Values Encoding (4 papers) → 5 recommendations (#169, #175–#179); Bubble Clusters (7 papers) → 6 recommendations (#170, #180–#186); Phase 4 Foundational Theory (4 papers) → 4 recommendations (#189–#192).
- **H1 (CONFIRMED)**: 20/20 recommendations found matching GitHub issues (100%). 5 intentional duplicates (#169↔#175: holographic encoding framework vs. empirical validation; #170↔#180: broad topological audit vs. bubble-cluster empirical deep-dive).
- **H2 (CONFIRMED)**: Phase 3b scripts operational — #181 (validate_handoff_permeability.py, 565 lines, 30 test functions, committed ed8a5fe); #182 (parse_audit_result.py, 365 lines, 25 test functions, CI workflow audit-provenance.yml). Both operational.
- **H3 (CONFIRMED)**: Zero untracked gaps implies Phase 4 writers demonstrated high discipline in forward-tracking. "A zero-gap audit is rare and indicates: (1) research question framing was precise; (2) Synthesizer→Reviewer handoff enforced tracking discipline; (3) Reviewer acceptance criteria included all-recommendations-have-issues as a gate."
- **Canonical example (100% Tracking Discipline)**: Issue #189 (Semantic Holography) emerges from recommendations in semantic-holography-language-encoding.md. Synthesizer identified the recommendation and seeded the issue during synthesis phase. Pattern: *Synthesis → Issue Seeding → Audit Validation → Next Phase Confident Execution*.
- **Anti-Pattern (Dangling Recommendations)**: Research paper with recommendations not tracked by GitHub issues. Creates orphaned work items invisible to project management, lost across session boundaries, difficult to prioritize.
- **Full recommendations table** (20 rows) includes: doc name, domain, recommendation text, issue number(s), status, phase. Covers all three domains plus Phase 4 foundational theory. Issues #181 and #182 are CLOSED; all others OPEN.
- **Phase 6 preconditions checklist**: 7 items, all PASS: Phase 4 papers reviewed/approved, recommendations tracked, Phase 3b scripts operational, corpus ready, issue tracking complete, CI GREEN, Phase 6 scope clear.
- **Phase 6 objectives**: Corpus validation (map Phase 1–4 findings onto three primary papers); Gap Analysis doc creation; Primary paper updates with backlinks from Phase 1–4.
- The anti-pattern emphasizes that untracked recommendations are "archaeological" — only rediscovered by re-reading all papers rather than surfacing naturally through issue system.

**Absent from or underrepresented in primary papers**

- `endogenic-design-paper.md` may discuss the methodology but likely does not describe the 100% recommendation-tracking discipline as an operational pattern that is itself a value-encoding mechanism. The traceability discipline (Synthesis→Issue Seeding→Audit→Next Phase) is a concrete implementation of Algorithms-Before-Tokens applied to research methodology.
- `values-encoding.md` Pattern Catalog does not include research methodology governance patterns (recommendation tracking, forward-traceability) as a domain where programmatic enforcement applies. The audit script + GitHub issue system together constitute a T2/T3-layer for research governance.
- `bubble-clusters-substrate.md` and `values-encoding.md` are among the "three primary papers" that Phase 6 will validate against — so this audit document is directly about the gap-analysis task at hand. The preconditions table and domain-by-domain breakdown are a systematic map of what should flow into each primary paper.
- The "zero-gap audit is rare" claim implies a quality standard for research methodology discipline that is not stated in any primary paper — it could be a Recommendation in `endogenic-design-paper.md`.

**Evidence structures for weaving**

- The 20-row recommendations table is a systematic cross-reference between Phase 1–4 research findings and tracking issues — usable as a provenance chain illustration in `endogenic-design-paper.md`.
- The Canonical Example pattern (Synthesis → Issue Seeding → Audit Validation → Next Phase Confident Execution) is a clean 4-step methodology pattern for `endogenic-design-paper.md` §3 Pattern Catalog.
- The Phase 6 preconditions checklist enumerates the exact pre-conditions under which corpus validation (the current task) can proceed — this is meta-evidence for the Scout 1B task itself.
- Issues #189–#192 (Phase 4 theories: IIT/panpsychism, semantic holography, substrate taxonomy, topological extension) are all Draft status — the audit identifies pushing these to Final as "high priority for Phase 6."

---

### substrate-taxonomy-content-context.md

**Source**: Draft, research_issue #191, closes_issue #191

**Key claims and patterns**

- Proposes a **four-category orthogonal substrate taxonomy** for EndogenAI/Workflows: (1) Content (never compact), (2) Context (always compact), (3) Hybrid (conditional compaction), (4) Regenerable Provenance (zero compaction cost, fully deterministic).
- **H1 (CONFIRMED)**: Four categories are empirically distinct with non-overlapping closure properties. Orthogonality proof: no substrate can simultaneously belong to two categories (6 impossible pairings argued).
- **Categorical definitions with examples**: Content: MANIFESTO.md, AGENTS.md, committed docs/research/*.md, git history. Loss impact: HIGH. Compaction: Never. Monotonically growing. Context: .tmp/<branch>/<date>.md scratchpad, terminal state, VS Code scratch buffers — session-local, gitignored, aggressively compacted at session-end. Hybrid: .cache/sources/.md (distilled external pages), test artifacts, build outputs. Regenerable with cost; conditional retention based on access frequency and regeneration cost. Regenerable Provenance (fourth category, novel): scripts/*.py, tests/*.py, .github/workflows/*.yml, .github/agents/*.agent.md — fully deterministic, zero loss if backed up in git, write-once-execute-many.
- **H2 (CONFIRMED)**: Optimal policies differ radically by category. Content=never compact/commit every edit. Context=aggressive compaction via prune_scratchpad.py --force. Hybrid=conditional rule. Regenerable=never compact, optimize for legibility.
- **H3 (CONFIRMED)**: Regenerability metric = (Fidelity + Determinism + Latency) / 3. Inversely predicts optimal compaction cost. Values: scripts/*.py = 1.00; .github/agents/*.agent.md = 1.00; .cache/sources/*.md = 0.65; .tmp/*.md = 0.50; terminal scrollback = 0.43. Decision thresholds: ≥0.95 = Never compact; 0.55–0.75 = Conditional; <0.50 = Aggressive.
- **H4 (CONFIRMED)**: Token-efficiency projections enable forward planning. A multi-phase session (MANIFESTO.md + AGENTS.md + phase specs) = ~17.7K tokens for startup alone. 12-session comparison: without compaction = 168K unnecessary tokens; with compaction = 3K tokens (56× more efficient).
- **Full substrate inventory table** (22 rows): all substrates enumerated with Type, Location, Compaction, Restoration, Example, Regenerability, Policy columns.
- **Alignment with MANIFESTO.md axioms**: H3 regenerability metric embodies "Algorithms Before Tokens" — deterministic cost models reusable across sessions rather than subjective estimates; H1 four-category taxonomy embodies "Endogenous-First" — scaffold retention strategy from substrate's intrinsic properties.
- **Pattern 1 (Four Orthogonal Categories)**: Content=permanent/irreplaceable; Context=ephemeral/session-local; Hybrid=regenerable-with-cost; Regenerable Provenance=fully deterministic/permanently archived.
- **Pattern 2 (Regenerability as Inverse Predictor)**: With Python pseudocode for each scoring dimension.
- **Pattern 3 (Token-Efficiency Compaction Protocol)**: 90%+ context overhead savings. Without compaction: 12 sessions × 50 KB = 168K tokens wasted at session start. With: 3.6 KB total, 3K tokens, 56× more efficient.
- **4th Category detail**: Distinct from Content (grows/edited over time vs. write-once-execute-many), from Hybrid (instant git restore vs. regeneration cost + latency), from Context (permanent if backed up vs. ephemeral).

**Absent from or underrepresented in primary papers**

- `values-encoding.md` has a fidelity test taxonomy (T1–T4 signal types) but no substrate classification model. The four-category taxonomy is a complementary dimension: not *how* values are encoded (via which tier) but *what kind of substrate* holds the encoding. The two frameworks are orthogonal and together would provide a complete encoding + preservation model.
- `bubble-clusters-substrate.md` discusses substrate topology but uses "substrate" in the bubble-cluster / membrane sense (physical structure carrying values) rather than the compaction-policy sense (what to keep vs. compact). The four-category taxonomy provides a preservation-policy dimension that is absent from bubble-clusters-substrate.md.
- The "Regenerable Provenance" fourth category is a novel contribution — scripts, tests, CI workflows, and agent files are neither pure content nor pure context. Treating them as a distinct category with zero compaction cost and full git-backed restoration is an insight not present in any primary paper about the substrate model.
- The token-efficiency calculation (168K tokens wasted without compaction vs. 3K with, based on the actual Milestone 9 session pattern) is an empirical result that concretizes the "Local Compute-First" / "Algorithms Before Tokens" claims in a way no primary paper does.
- The regenerability metric (Fidelity + Determinism + Latency) / 3 is a formalized decision procedure for compaction — a canonical example of Algorithms-Before-Tokens applied to session management that is absent from `values-encoding.md`.
- `endogenic-design-paper.md`'s H1 (encode-before-act) would be strengthened by the substrate taxonomy's insight that the substrate being read (AGENTS.md, guides) is Regenerable Provenance category — zero compaction cost, maximum fidelity, always the right thing to read at session start.

**Evidence structures for weaving**

- The 22-row substrate inventory table is a complete citable taxonomy for `bubble-clusters-substrate.md` §4 or §5 (Substrate Inventory or Junction Specs).
- The regenerability metric formula and decision thresholds (≥0.95=Never, 0.55–0.75=Conditional, <0.50=Aggressive) are a formal decision procedure directly usable in `values-encoding.md` Recommendations as an instantiation of Algorithms-Before-Tokens.
- The token-efficiency calculation (168K vs. 3K tokens, 56× efficiency gain) is an empirical anchor for the "Local Compute-First" axiom in any primary paper.
- The orthogonality proof (6 impossible pairings) is a precision argument for the four-category taxonomy that would survive scrutiny as a formal claim in `endogenic-design-paper.md`.

---

### workflow-formula-encoding-dsl.md

**Source**: Draft, research_issue #192, closes_issue #192

**Key claims and patterns**

- **Core hypothesis**: Holographic encoding principles from semantic-holography-language-encoding.md applied to workflow DSL design. Workflow semantics encoded as ultra-compact formulas analogous to chemical notation without loss of semantic fidelity.
- **H1 (CONFIRMED)**: Context-free grammar (BNF/EBNF) can express workflow decision logic with minimal production rules. Two encoder rules (E1: workflow → agent ":" decision-tree "*" [anti-pattern]; E2: decision-tree → "(" condition "→" actions ";" [branch] ")"), two decoder rules (D1: formula-agent → agent-name "{" decision-logic "}"; D2: formula-gate → [pre-condition] "?" decision ":" alt-decision). Rationale: EBNF is ISO/IEC 14977 standard; usage confirmed in Python, Java, SQL.
- **H2 (CONFIRMED)**: Encoder and decoder algorithms preserve decision logic fidelity. Both provided as full pseudocode (~50-60 lines each). Encoder: scan for agent declarations → parse conditional statements → serialize decision trees → append anti-patterns → return formula + debug state_map. Decoder: extract agent formulas → resolve tokens → expand to if-else pseudocode → decode anti-patterns → run round-trip validation.
- **H3 (CONFIRMED)**: Three case studies with encode→decode→re-encode show zero semantic loss. Case Study 1 (Session Orchestration): 3 agents, 5 decision points, 2 anti-patterns. Human formula (~420 tokens) → compact formula (~78 tokens). **81% reduction**. Case Study 2 (Agent Delegation Routing): 4 agents, 4 decision branches, 1 anti-pattern, zero semantic loss. Case Study 3 (Conflict Resolution): Three decision layers, 6-way conditional branching, 3 anti-patterns — encodes the six-layer deployment model conflict resolution protocol.
- **Full EBNF grammar** provided: workflow, agent-list, agent, decision-formula, decision-node, condition, action, anti-pattern-list with terminal symbol definitions.
- **Holographic encoding applied to DSL**: Four layers: Layer 1 = formula structure (grammar syntax), Layer 2 = canonical example (executed trace), Layer 3 = anti-pattern failure condition (negation symbols), Layer 4 = deterministic parser (round-trip validation). Mirrors [4,1] redundancy code from semantic-holography-language-encoding.md.
- **Recommendations**: (1) Adopt DSL for protocol-layer workflow enforcement; store critical workflows in `data/workflows.yml`. (2) Implement `scripts/encode_workflow.py` and `scripts/decode_workflow.py`. (3) Extend validate_synthesis.py for formula presence checks. (4) Apply holographic encoding discipline to formulas (4 layers). (5) Measure token efficiency on all current narrative workflows; target ≥70% compression.
- **Sources cited**: BNF (Backus/Naur 1960), EBNF (Wirth 1977), Dragon Book (Aho et al. 2006), Process Mining (van der Aalst 2016), BPMN v2.0.2 (ISO/IEC 19510), Petri nets (Petri 1962), holographic encoding (#189).
- Grounding in foundational axioms: MANIFESTO.md §1 Endogenous-First (absorbs BNF/BPMN/Petri nets as best external practices), §2 Algorithms Before Tokens (parser is context-free, encoder/decoder are linear-time, no NP-hard search), AGENTS.md §Programmatic-First (formula encoding operationalizes principle at protocol layer).

**Absent from or underrepresented in primary papers**

- `values-encoding.md` discusses Algorithms-Before-Tokens but has no concrete DSL example of that principle applied to workflow specification. The workflow formula DSL (with 81% compression, deterministic round-trip, formal grammar) is the canonical example of Algorithms-Before-Tokens that's missing from the Pattern Catalog.
- `endogenic-design-paper.md` discusses methodology but likely has no formula-level encoding of the methodology itself as executable protocols. The encode-before-act claim (H1) would be significantly strengthened if the actual workflow for encode-before-act could be expressed as a deterministic DSL formula.
- `bubble-clusters-substrate.md` discusses signal preservation through membranes, but the DSL's anti-pattern negation symbols encode signal-preservation rules as part of the formula. This is a DSL-level implementation of membrane permeability rules absent from bubble-clusters-substrate.md.
- The Petri net formalism cited in the DSL sources directly maps to bubble-clusters-substrate.md's membrane topology (Petri net transitions = DSL decision nodes; Petri net places = workflow states). This structural connection is absent from both papers.
- `values-encoding.md`'s holographic encoding principle (Pattern 6, [4,1] code) is the theoretical foundation that the DSL explicitly operationalizes — but this operationalization is absent from values-encoding.md itself. The DSL is the "canonical example" that values-encoding.md Pattern 6 needs.
- BPMN (ISO/IEC 19510) as an external standard that the DSL absorbs grounds the approach in an international standard — this external citation is absent from any primary paper.

**Evidence structures for weaving**

- The three case studies with compact formula representations, token-efficiency ratios (81% reduction), and round-trip validation results are canonical examples for `values-encoding.md` §3 Pattern Catalog (Algorithms-Before-Tokens applied to workflow specification).
- The EBNF grammar listing (ISO/IEC 14977 standard) is a citable formal specification for `endogenic-design-paper.md` §3 Pattern Catalog.
- The conflict-resolution Case Study 3 (six-layer deployment model, 3 anti-patterns) directly connects to the external-values architecture findings from Scout 1A — providing a formula-level encoding of the conflict taxonomy that was previously T5 prose-only.
- The 81% compression ratio is an empirical measurement of the Algorithms-Before-Tokens efficiency gain applicable to `values-encoding.md` Recommendations.
- The DSL's four holographic layers (structure/example/anti-pattern/gate) is the most operationally specific encoding of the holographic encoding principle — directly usable as a Pattern Catalog entry in `values-encoding.md`.

---

### Scout 1B — Theme Summary

1. **Sprint docs confirm H1–H4 novelty claims with specific prior-art survey grounding, but all four remain Draft status and none have been incorporated into the three primary synthesis papers.** The sprint docs (sprint-A through sprint-DE) provide the complete external literature survey layer that justifies each hypothesis — arXiv identifiers, precise prior-art gaps, falsifiability criteria — but this evidential backing is absent from `endogenic-design-paper.md`. The primary paper makes the four claims; the sprint docs make the case for them. The weaving task is the inverse of integration: pulling the survey evidence from Draft sprint docs into Final primary papers.

2. **The DSL and formula-encoding work (`workflow-formula-encoding-dsl.md`) is the canonical missing example for Algorithms-Before-Tokens across all three primary papers.** The `values-encoding.md` Pattern Catalog has no concrete encoding-as-formula example; `endogenic-design-paper.md` asserts the principle but has no DSL-level instantiation; `bubble-clusters-substrate.md` discusses membrane rules but not formula encodings of those rules. The 81% compression ratio, round-trip validation, EBNF grammar, and three case studies are all available for weaving. This is the densest single source of Algorithms-Before-Tokens canonical examples in the corpus.

3. **Topological audit + substrate taxonomy together provide the empirical measurement infrastructure that primary papers assert but do not measure.** `topological-audit-substrate.md` gives 75 vertices / 52 edges / 15 faces with formal graph metrics; `substrate-taxonomy-content-context.md` gives a four-category classification with regenerability scores and compaction policies. `bubble-clusters-substrate.md` asserts the architectural topology; neither primary paper provides the measurable quantities. The two Bridge/Integration docs are the empirical grounding layer.

4. **Value provenance chain (`value-provenance.md`) introduces a new measurement concept — chain-of-custody via `governs:` annotation — that is distinct from cross-reference density and drift detection but addresses the same question (are values encoded faithfully?).** The 100% orphaned fleet at baseline (`fleet_citation_coverage_pct = 0.0`) is a stark gap result that `values-encoding.md` §5 Fidelity Test Taxonomy does not account for. The Shepard's Citations / prov:wasDerivedFrom cross-domain evidence provides principled grounding. Weaving this into `values-encoding.md` would add a fourth measurement dimension alongside density, drift, and tier coverage.

5. **The doc-interweb / programmatic interlinking synthesis (`doc-interweb.md`) represents the Algorithms-Before-Tokens application to the cross-reference density problem itself — a reflexive system where the claim (cross-references improve value fidelity) is enforced programmatically via a YAML registry and link-injection script.** This reflexivity (documentation tooling applying Documentation-First to documentation standards) is absent from all three primary papers and represents a clean canonical example of the endogenic methodology applied to its own substrate.
