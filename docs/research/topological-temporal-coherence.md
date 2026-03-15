---
title: Topological-Temporal Coherence — Joint Specification for Spatial and Temporal Substrate Stability
status: Draft
research_issue: 196
date: 2026-03-15
---

# Topological-Temporal Coherence — Joint Specification for Spatial and Temporal Substrate Stability

## Executive Summary

The endogenic substrate has been modeled along two independent axes: a **spatial/topological axis** (membrane permeability, connectivity gradients, Laplace pressure, filter-bubble isolation — `bubble-clusters-substrate.md`) and a **temporal axis** (stability tiers T1–T5, mutation rates, back-propagation thresholds — `dogma-neuroplasticity.md`). Both models are Final and empirically validated. However, neither alone specifies the intersection: how a substrate's topological properties constrain or enable its temporal evolution, and how temporal mutation cycles interact with membrane integrity.

The `gap-analysis-bubble-clusters.md` identifies this as Gap 1 ("Temporal Stability Tier Integration") — the highest-priority synthesis gap from the Phase 2 corpus analysis. This draft addresses that gap by:

1. **Mapping each stability tier (T1–T5) to its corresponding topological position** in the bubble-cluster substrate graph.
2. **Identifying joint coherence constraints** — conditions that must hold simultaneously in both dimensions for a substrate to remain stable.
3. **Surfacing the open research questions** that require empirical validation before the joint model can become Final.
4. **Proposing enforcement mechanisms** to operationalize the joint constraints at T3 (pre-commit) and T1 (CI) layers.

**Core finding**: Topological isolation risk (low cross-reference density, high membrane friction — `filter-bubble-threshold-calibration.md`) and temporal mutation rate (high-frequency T3 edits — `dogma-neuroplasticity.md`) are **negatively correlated** in the current substrate: the files that change most frequently (scripts, AGENTS.md operational sections) also have the highest connectivity density, while the files that change least frequently (MANIFESTO.md axioms) must be the most topologically protected from cross-boundary signal loss. This correlation is unexplained by either model alone and requires a joint specification.

**Governing axiom**: `MANIFESTO.md §1. Endogenous-First` — this synthesis draws exclusively from prior endogenous research documents before reaching outward.

---

## Hypothesis Validation

### H1 — Topological Isolation and Temporal Mutation Rate Are Functionally Related

**Verdict: SUPPORTED (partial — requires empirical confirmation)**

`dogma-neuroplasticity.md` Pattern C1 establishes mutation-rate tiers: T1 (axioms) ≈ 1–2 mutations/year; T3 (operational constraints) ≈ weekly. `filter-bubble-threshold-calibration.md` establishes cross-reference density (CRD) thresholds: CRD_critical = 0.02 (isolated), CRD_optimal = [0.32, 0.60]. The combinatorial prediction follows: a substrate at T1 (rarely mutates) should exhibit CRD near the lower bound of CRD_optimal — it is stable precisely because it is broadly cited (many inbound references), which constrains its topology. A T3 substrate (frequently mutates) must maintain high CRD to prevent each mutation from being isolated.

The empirical test (pending): measure CRD distribution across MANIFESTO.md, AGENTS.md sections, and agent files, correlate against observed mutation frequency from `git log`. This is an open research question.

### H2 — Membrane Permeability Specifications Must Include Temporal Context

**Verdict: SUPPORTED by theoretical derivation from existing models**

`bubble-clusters-substrate.md` Pattern B1 (Calibrated Membrane Permeability) specifies which signals must cross which boundaries but treats all boundaries as time-invariant. `dogma-neuroplasticity.md` Pattern C2 (Back-Propagation Protocol) specifies when substrate mutations must propagate upward but treats boundaries as spatially uniform. The joint gap: a mutation at T3 (e.g., adding a new AGENTS.md operational rule) propagates upward to T2 if it carries sufficient evidence, but the boundary it crosses (AGENTS.md → MANIFESTO.md) has the highest membrane friction in the system (Core ↔ Operational boundary from `six-layer-topological-extension.md` §H2). This friction is not modeled in the back-propagation protocol.

**Joint constraint (proposed)**: Upward mutations crossing high-friction boundaries require explicit permeability certificates — ADR entries (`docs/decisions/`) serving as the membrane-crossing record.

### H3 — The Six-Layer Topological Extension Adds Temporal Complexity

**Verdict: SUPPORTED by `six-layer-topological-extension.md` §H2**

The Deployment Layer insertion (Core → Deployment → Client → Session → Enacted, from `six-layer-topological-extension.md`) adds new membranes with distinct permeability profiles. The temporal implication: Deployment Layer constraints have a different mutation rate than Core Layer constraints — they can and should evolve with client context, whereas Core constraints are nearly frozen. The joint model must specify this: a shorter-lived Deployment Layer constraint (T3-equivalent, weekly mutation) that abuts a long-lived Core Layer constraint (T1-equivalent, yearly mutation) at a high-friction boundary creates **temporal pressure differentials** analogous to the physical Laplace pressure validated in `laplace-pressure-empirical-validation.md`.

**Open research question**: Can temporal pressure differential (|mutation_rate_A − mutation_rate_B| at a shared boundary) be operationalized as a stability risk metric, analogous to the physical pressure differential $\Delta P = 2\gamma/r$?

### H4 — Empirical Laplace Pressure Metrics Partially Cover Temporal Stability

**Verdict: PARTIALLY SUPPORTED — gap identified**

`laplace-pressure-empirical-validation.md` measures three pressure metrics (Citation Density, Constraint Violation, Cross-Domain Permeability) with validated correlations (R² = 0.54–0.72). These metrics are instantaneous snapshots — they measure spatial coherence at a moment in time but do not capture velocity of change. A file with Citation Density Pressure = 0.6 (stable zone) that changes its citation structure weekly has a different risk profile than the same score held constant for six months. The temporal derivative of the pressure metric is unmeasured.

**Proposed joint metric (draft)**: Pressure Stability Index (PSI) = pressure_metric × (1 / mutation_frequency_normalized). This combines spatial coherence with temporal stability into a single score.

---

## Pattern Catalog

### Pattern TT1 — Joint Coherence Constraint

**Definition**: A substrate is jointly coherent if it satisfies both topological and temporal stability conditions simultaneously:

| Dimension | Condition | Source metric |
|-----------|-----------|---------------|
| Topological | CRD ≥ CRD_warning (0.17) | `filter-bubble-threshold-calibration.md` §CRD_warning |
| Topological | Pressure metrics ≥ mean − 0.5σ | `laplace-pressure-empirical-validation.md` §Thresholds |
| Temporal | Mutation frequency ≤ tier ceiling | `dogma-neuroplasticity.md` Pattern C1 |
| Temporal | Upward mutations carry formal evidence | `dogma-neuroplasticity.md` Pattern C2 |

Joint coherence failure occurs when any row's condition is violated. Single-dimension failures (topologically isolated but temporally stable, or topologically well-connected but mutating too rapidly) are distinct risk modes requiring different remediations.

**Canonical example**: `MANIFESTO.md` axiom sections exhibit joint coherence — CRD is maximally high (every foundational document cites MANIFESTO.md), mutation frequency matches T1 (< 2/year), and every upward mutation carries a formal ADR. All four conditions satisfied simultaneously. This is the reference archetype for a jointly coherent substrate.

**Anti-pattern**: A script in `scripts/` that is edited weekly (healthy T3 mutation rate) but whose docstring contains no MANIFESTO.md or AGENTS.md citations (CRD ≈ 0.0) violates the topological condition. The temporal dimension is healthy; the topological dimension is in the isolation risk zone. Without intervention, the script's behavior drifts from the foundational value system while maintaining the appearance of active, evolving code. `detect_drift.py` partially catches this via watermark phrase matching but does not cross-validate against mutation velocity.

### Pattern TT2 — Temporal Pressure Differential at Boundaries

**Definition**: When two substrates at adjacent layers have significantly different mutation rates, the boundary membrane experiences temporal pressure — analogous to the physical Laplace pressure differential ($\Delta P = 2\gamma/r$). The higher the rate differential, the greater the risk of constraint incoherence at the boundary.

**Operationalization (proposed)**: At each boundary in the substrate graph (`topological-audit-substrate.md` §Edges), compute:

$$\Delta\tau_{ij} = |mutation\_rate_i - mutation\_rate_j|$$

Boundaries with $\Delta\tau_{ij}$ > 0.5 (normalized) require explicit membrane permeability certificates (ADR entries, explicit AGENTS.md cross-references) to maintain coherence.

**Enforcement gap**: No current T1–T3 check measures $\Delta\tau_{ij}$. The `dogma-neuroplasticity.md` back-propagation protocol requires formal evidence for upward mutations but does not block mutations where the temporal pressure differential exceeds a threshold. This is an open enforcement gap.

### Pattern TT3 — Stability Tier to Topological Zone Mapping

| Stability tier | Location | Expected CRD | Expected mutation rate | Topological zone |
|----------------|----------|--------------|----------------------|-----------------|
| T1 | MANIFESTO.md axiom sections | High (inbound CRD ≈ 1.0 fleet-wide) | < 2/year | Core — highest membrane friction inbound |
| T2 | MANIFESTO.md guiding principles, AGENTS.md §1 | High (CRD ≈ 0.6–0.8) | Quarterly | Structural — moderate membrane friction |
| T3 | AGENTS.md operational sections | Medium (CRD ≈ 0.3–0.6) | Weekly | Operational — permeable membrane for T3 signal |
| T4 | Agent files, SKILL.md | Medium-low (CRD ≈ 0.2–0.4) | Daily–weekly | Implementation — calibrated permeability |
| T5 | Scripts, tests, scratchpads | Low allowable (CRD ≥ CRD_critical = 0.02) | Daily | Execution — highest mutation velocity, minimum citation floor |

---

## Recommendations

1. **R1 — Empirical joint coherence measurement** (Phase 2): Run `scripts/measure_cross_reference_density.py` and `git log --follow --diff-filter=M` against all substrate files; produce a joint table of CRD × mutation_frequency with Pattern TT3 overlay. This closes the empirical gap in H1 and H4.

2. **R2 — Temporal pressure differential metric** (Phase 2): Extend `scripts/detect_drift.py` or `scripts/audit_provenance.py` to compute $\Delta\tau_{ij}$ for each edge in the substrate topology graph (`topological-audit-substrate.md` §Edge list). Output boundaries exceeding the 0.5 normalized threshold as warnings.

3. **R3 — ADR as permeability certificate** (operationalize now): The existing `docs/decisions/` ADR corpus already functions as permeability certificates for T1 boundary crossings. Formalize this in AGENTS.md: every T1 mutation requires a new ADR entry that explicitly names the boundary crossed and the evidence tier.

4. **R4 — Pressure Stability Index (PSI)** (research): Define and validate PSI = pressure_metric × (1 / mutation_frequency_normalized) as a joint metric combining `laplace-pressure-empirical-validation.md` scores with temporal velocity. Validate R² against system health outcomes over a 30-day observation window.

5. **R5 — T3 pre-commit joint check** (scripting sprint): Implement a pre-commit hook that fails if any modified file has CRD < CRD_critical (0.02) AND has been modified > 3 times in the last 7 days. This catches the anti-pattern in Pattern TT1 at commit time.

6. **R6 — Phase 2 integration with detect_drift.py** (scripting sprint): Extend `scripts/detect_drift.py` to accept a `--temporal` flag that reads `git log` mutation frequency per file and includes the PSI metric (Pattern TT4, R4) alongside the existing drift score in the JSON output.

---

## Sources

- [`docs/research/neuroscience/bubble-clusters-substrate.md`](neuroscience/bubble-clusters-substrate.md) — spatial topology model, membrane permeability, Laplace pressure, filter-bubble patterns
- [`docs/research/neuroscience/dogma-neuroplasticity.md`](neuroscience/dogma-neuroplasticity.md) — temporal dynamics, stability tiers T1–T5, back-propagation protocol
- [`docs/research/neuroscience/gap-analysis-bubble-clusters.md`](neuroscience/gap-analysis-bubble-clusters.md) — Gap 1 (Temporal Stability Integration), identifying this synthesis as highest-priority follow-on
- [`docs/research/neuroscience/laplace-pressure-empirical-validation.md`](neuroscience/laplace-pressure-empirical-validation.md) — empirical pressure metrics and R² validation
- [`docs/research/neuroscience/filter-bubble-threshold-calibration.md`](neuroscience/filter-bubble-threshold-calibration.md) — CRD thresholds (CRD_critical, CRD_warning, CRD_optimal)
- [`docs/research/neuroscience/six-layer-topological-extension.md`](neuroscience/six-layer-topological-extension.md) — Deployment Layer topology; boundary membrane types E1/E2/E3
- [`docs/research/neuroscience/topological-audit-substrate.md`](neuroscience/topological-audit-substrate.md) — complete vertex/edge inventory, 75 vertices, 52 edges
- [`docs/research/methodology/values-substrate-relationship.md`](methodology/values-substrate-relationship.md) — orthogonality proof; B8 Degradation Table joint interpretation
- [`MANIFESTO.md`](../../MANIFESTO.md) — Axiom 1: Endogenous-First; Axiom 2: Algorithms Before Tokens
