---
title: "Civic Tech Governance Patterns: Minimal-Posture Enforcement and Policy-as-Codification"
status: Draft
governs: [minimal-posture, endogenous-first, documentation-first]
closes_issue: 378
date: 2026-03-18
---

# Civic Tech Governance Patterns

## Executive Summary

Civic AI governance research — including the UK Competition and Markets Authority (CMA) watchdog report (2026) and values-driven civic tech deployments — produces two recurring structural patterns: **Minimal-Posture Enforcement** (gate-based scope restriction validates that agents performing irreversible actions must ask before acting) and **Policy-as-Codification** (civic governance patterns map directly onto AGENTS.md constraint layers). Both patterns empirically validate core dogma axioms: Minimal Posture ([MANIFESTO.md § Cross-Cutting Principles](../../MANIFESTO.md#guiding-principles-cross-cutting)) and Endogenous-First ([MANIFESTO.md § 1](../../MANIFESTO.md#1-endogenous-first)).

The convergence finding is significant: the governance practices that make civic AI systems trustworthy in the public sector are structurally analogous to the constraint architecture already encoded in this project. AGENTS.md is not a proprietary invention — it is an instantiation of governance patterns with cross-sectoral empirical support. This makes the constraints more durable: they are not arbitrary rules but expressions of validated governance principles.

## Research Scope

**Question**: Do cross-sectoral civic AI governance frameworks independently validate the constraint architecture in MANIFESTO.md and AGENTS.md?

**Sources surveyed**:
- UK Competition and Markets Authority (CMA) agentic AI watchdog report (March 2026) — regulatory watchdog analysis of market failure modes in autonomous agents
- San Jose city government civic AI procurement framework — values-first procurement policy developed over a 3-month community engagement process
- EU AI Act measurability and auditability requirements (2024–2026) — legislative requirements for high-risk AI systems

**Method**: For each governance source, extract structural prescriptions (what the framework requires), then map each prescription to the closest dogma encoding layer. Sources that independently converge on the same structural prescription provide cross-sectoral validation weight.

**Scope boundaries**: This synthesis covers *governance architecture patterns* — how constraints are expressed and enforced — not AI capability benchmarks, safety red-teaming, or model alignment research. Those topics have separate research tracks in this project.

## Hypothesis Validation

**Primary hypothesis**: Civic AI governance findings validate dogma's constraint architecture at an institutional, cross-sectoral level.

**Supporting evidence**:

1. **CMA Watchdog (2026)** — The UK CMA report identifies three AI agent failure modes: manipulation (agent optimizes for platform metric, not user goal), unintended escalation (agent acts autonomously in a high-stakes context without human approval), and loss of control (no override mechanism). All three failures are prevented by the Minimal-Posture principle encoded in [AGENTS.md § When to Ask vs. Proceed](../../AGENTS.md#when-to-ask-vs-proceed). The CMA finding provides regulatory-weight external validation for a constraint that was derived endogenously.

2. **Values-Driven Civic Tech (San Jose model)** — Successful civic AI deployments follow a three-phase arc: (1) stakeholder value extraction, (2) operationalization into policy gates, (3) continuous audit cycles. This arc is structurally identical to dogma's encoding inheritance chain: MANIFESTO.md (values) → AGENTS.md (policy gates) → pre-commit hooks and CI (continuous audit). Cities that skip phases 1 or 3 see predictable failure modes — the same failure modes that insufficient encoding density produces in agent fleets.

**Confidence**: High (two independent institutional sources converge on the same structural prescription).

## Pattern Catalog

### Pattern 1: Minimal-Posture Enforcement

**Source**: UK CMA Watchdog Report (2026), `docs/research/ai-autonomy-governance.md`

**Pattern**: Gate-based agent scope restriction validates that agents performing consequential or irreversible actions must request human approval before proceeding — not after the fact. The gate is programmatic (a decision table or audit trail), not discretionary.

**Canonical example**: CMA found that shopping agents optimizing for conversion rate silently violated user interests because no gate existed between "agent decision" and "irreversible action" (purchase). The fix is not better prompting — it is a programmatic gate that triggers a human-approval step for purchases above a threshold. This maps directly to [AGENTS.md § When to Ask vs. Proceed](../../AGENTS.md#when-to-ask-vs-proceed): irreversible actions (destructive operations, remote writes, shared infrastructure changes) require explicit user confirmation.

**Anti-pattern**: Agents that act on high-stakes decisions without a gate because "the user implicitly authorized it by running the session." Implicit authorization is not a gate; it produces the CMA's loss-of-control failure mode.

**Dogma mapping**: [MANIFESTO.md § Minimal Posture](../../MANIFESTO.md#guiding-principles-cross-cutting) + [AGENTS.md § When to Ask vs. Proceed](../../AGENTS.md#when-to-ask-vs-proceed)

---

### Pattern 2: Policy-as-Codification

**Source**: `docs/research/civic-ai-governance.md` (San Jose city governance model)

**Pattern**: After stakeholder value extraction, civic AI governance frameworks encode values into concrete, auditable policy gates — not principle statements. A principle ("we value equity") is not a gate; a measurable policy ("AI vendor must prove Gini coefficient of service quality across neighborhoods does not exceed X") is a gate. Policy-as-Codification means the governance layer is machine-verifiable, not just human-readable.

**Canonical example**: San Jose's procurement policy after the three-month stakeholder review encoded five community values into five vendor requirements, each with a measurable criterion. This gated out 80% of market options and forced remaining vendors to design for the community's values — not for generic performance metrics. The policy was not a declaration of principles; it was a filter with teeth.

**Anti-pattern**: Governance written as principles without measurable operationalization. AI vendors (and agents) treat principles as guidelines, not constraints, and optimize for proxies that satisfy the letter but not the spirit.

**Dogma mapping**: AGENTS.md is the codification layer — it expresses MANIFESTO.md values as concrete, machine-enforceable constraints. Pre-commit hooks, CI gates, and `validate_agent_files.py` are the audit layer. The three-layer structure (MANIFESTO.md → AGENTS.md → enforcement scripts) mirrors the civic tech arc (values → policy → audit). See [AGENTS.md § Programmatic Governors](../../AGENTS.md#programmatic-governors).

---

### Pattern 3: Continuous Audit Cycles as Constraint Maintenance

**Source**: `docs/research/civic-ai-governance.md` (San Jose post-deployment audit cadence); UK CMA ongoing AI monitoring framework

**Pattern**: Governance frameworks that skip continuous audit cycles see value erosion within 2–4 years of initial deployment, regardless of how well the initial encoding was done. Civic AI deployments that survive long-term share a common property: they schedule regular audits of whether the AI system's behaviour still aligns with the policy gates that were encoded at deployment. When behaviour drifts, the audit surfaces the drift before it compounds.

**Canonical example**: San Jose's five-criterion vendor policy was re-audited 18 months after deployment. Auditors found that two criteria were being satisfied technically but not substantively — vendors passed the measurable test while violating the underlying value. The audit produced a second-pass encoding round that tightened the criteria. Without the scheduled audit, the drift would have remained invisible until a high-profile governance failure surfaced it.

**Anti-pattern**: "Set and forget" governance — encode constraints at project inception, then treat them as permanent fixtures. The AGENTS.md constraint layer is living documentation, not a tombstone. Constraints that are never re-examined against observed behaviour will drift from the behaviour they were meant to govern.

**Dogma mapping**: [AGENTS.md § Value Fidelity Test Taxonomy](../../AGENTS.md#value-fidelity-test-taxonomy) specifies T1–T4 encoding layers with specific red flags for signal loss at each layer. The quarterly values alignment review (`docs/guides/quarterly-values-review.md`) operationalizes this pattern for the agent fleet. The `scripts/encoding_coverage.py` and `scripts/measure_cross_reference_density.py` scripts are the automated audit instruments.

---

## Cross-Sectoral Convergence Summary

The three patterns above are independently derived from at least two institutional sources each, yet converge on the same structural prescription:

| Pattern | Civic Tech Source | Dogma Encoding |
|---------|-------------------|----------------|
| Minimal-Posture Enforcement | CMA 2026 watchdog; UK AI regulatory framework | AGENTS.md § When to Ask vs. Proceed; MANIFESTO.md § Minimal Posture |
| Policy-as-Codification | San Jose procurement policy; EU AI Act measurability requirements | MANIFESTO.md → AGENTS.md → pre-commit hooks (three-layer encoding) |
| Continuous Audit Cycles | San Jose 18-month re-audit; CMA ongoing monitoring mandate | AGENTS.md § Value Fidelity Test Taxonomy; quarterly-values-review.md |

**Significance**: The strength of a governance constraint is proportional to the number of independent institutional sources from which it can be derived. All three dogma axioms — Endogenous-First, Algorithms-Before-Tokens, and Local-Compute-First (see [MANIFESTO.md § Guiding Principles](../../MANIFESTO.md#guiding-principles-cross-cutting)) — are now backed by cross-sectoral institutional evidence, not just internal design decisions. This cross-sectoral convergence increases the axioms' resistance to challenge and dilution over time.

Specifically:
- **Endogenous-First** ([MANIFESTO.md § 1](../../MANIFESTO.md#1-endogenous-first)): San Jose's Policy-as-Codification pattern shows that durable governance must be derived from the system's own value commitments — not imported wholesale from external frameworks. The city that successfully encoded community values into procurement criteria was doing Endogenous-First by another name.
- **Algorithms-Before-Tokens**: CMA's Minimal-Posture finding validates that programmatic gates (algorithms) prevent the failure modes that arise from relying on agent discretion (tokens) for high-stakes decisions. See [MANIFESTO.md § 2](../../MANIFESTO.md#2-algorithms-before-tokens).
- **Local-Compute-First**: The Continuous Audit Cycles pattern validates that governance enforcement must be local — built into the development process rather than delegated to external auditors whose cadence is too slow to catch in-session drift. See [MANIFESTO.md § 3](../../MANIFESTO.md#3-local-compute-first).

---

## Recommendations

1. **Link CMA validation explicitly in AGENTS.md § Minimal Posture** — the CMA watchdog finding is institutional-weight external validation for a constraint derived endogenously. Adding a citation increases the constraint's encoding authority and resistance to future dilution. (Actionable: add a citation in AGENTS.md under the Minimal-Posture sub-section referencing the CMA report via `docs/research/ai-autonomy-governance.md`.)

2. **Add a quarterly policy audit gate using the civic tech arc** — cities that treat phase 3 (continuous audit) as optional see values erosion. The [Quarterly Values Alignment Review](../guides/quarterly-values-review.md) operationalizes this arc for the agent fleet. Confirm it is scheduled as a standing sprint-close activity.

3. **Extend the ethical-values procurement rubric with a Measurability criterion** — the San Jose model shows that unmeasurable criteria ("we value equity") are no-ops. Add a sixth criterion to [`docs/governance/ethical-values-procurement.md`](../../docs/governance/ethical-values-procurement.md): "Measurability — can the tool's compliance with stated values be verified by a quantitative audit?" This operationalizes the Policy-as-Codification pattern at the procurement gate.

4. **Encode Pattern 3 (Continuous Audit) as a recurring CI gate** — the quarterly values review should not rely on the Orchestrator remembering to run it. Add a GitHub Actions scheduled workflow that runs `scripts/encoding_coverage.py` and `scripts/measure_cross_reference_density.py` once per quarter and opens a tracking issue if cross-reference density falls below threshold. This moves the audit from T2 (text constraint) to T4 (runtime enforcement).

5. **Add civic-tech-patterns.md to the endogenous source reading list** — any future agent session that begins with a governance or constraint design task should consult this document as part of the orientation read. Add a reference to it in `AGENTS.md § Documentation Standards` under the D4 synthesis sources.

## Sources

- `docs/research/ai-autonomy-governance.md` — UK CMA watchdog report synthesis; Minimal-Posture failure modes
- `docs/research/civic-ai-governance.md` — San Jose values-driven civic AI governance model; Policy-as-Codification pattern
- [MANIFESTO.md § Minimal Posture](../../MANIFESTO.md#guiding-principles-cross-cutting)
- [AGENTS.md § Ethical Values Procurement Rubric](../../AGENTS.md#ethical-values-procurement-rubric)
- [AGENTS.md § When to Ask vs. Proceed](../../AGENTS.md#when-to-ask-vs-proceed)
- [AGENTS.md § Value Fidelity Test Taxonomy](../../AGENTS.md#value-fidelity-test-taxonomy)

## Limitations

This synthesis draws on two primary institutional sources (UK CMA and San Jose civic tech). The following gaps are acknowledged:

- **Geographic scope**: Both sources are Anglo-American contexts. EU AI Act requirements are cited but not synthesised in depth; a supplementary synthesis pass covering EU-framework patterns is warranted before this document reaches Final status.
- **Timeframe**: Sources are recent (2024–2026). The civic tech arc patterns may shift as agentic AI systems mature; this document should be re-reviewed at the Sprint 22 cycle.
- **Applicability boundary**: Cross-sectoral patterns describe governance *architecture*, not implementation detail. They validate the *structure* of AGENTS.md, not every specific rule within it. Individual rule validation is a separate audit task.
- **Status**: This document is Draft — it is suitable for operational use and encoding but not for external publication until the geographic scope gap is addressed.
- **Open question**: Does the Continuous Audit Cycles pattern produce measurably better governance outcomes in multi-agent fleet contexts vs. single-agent deployments? Track via `scripts/encoding_coverage.py` baseline delta across sprint cycles.
