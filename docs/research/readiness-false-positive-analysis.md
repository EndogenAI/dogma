---
title: Readiness False-Positive Analysis — Intent-Bound Contracts and End-to-End Verification
description: Retrospective synthesis of Sprint 1/2 RAG delivery incident where retrieval completeness was mistaken for end-to-end RAG capability. Documents root causes, proposed guardrail tracks, and governance implications.
status: Final
closes_issue: 402
author: Executive Researcher
date: 2026-03-25
recommendations:
  - id: intent-bound-readiness-contract
    title: Intent-Bound Readiness Contract (Track A)
    status: accepted-for-adoption
    linked_issue: 446
  - id: capability-matrix-requirement
    title: Capability Matrix Requirement (Track B)
    status: accepted-for-adoption
    linked_issue: 447
  - id: demo-before-claim-gate
    title: Demo-before-Claim Gate (Track C)
    status: accepted-for-adoption
    linked_issue: 448
  - id: plan-to-intent-drift-check
    title: Plan-to-Intent Drift Check (Track D)
    status: accepted-for-adoption
    linked_issue: 449
  - id: communication-safety-protocol
    title: Communication Safety Protocol (Track E)
    status: accepted-for-adoption
    linked_issue: 450
---

## Executive Summary

During Sprint 1/2 RAG delivery, a readiness assessment reported "yes" despite the baseline acceptance rule requiring end-to-end RAG behavior (retrieve + augment + grounded generation over dogma). The incident reveals a systemic misalignment between subsystem-level gating (retrieval health, query normalization) and user-outcome-level acceptance criteria (generated answers with citations).

**Root cause**: Readiness was assessed at subsystem level rather than outcome level. Current gates prove retrieval correctness but do not validate the generated-answer behavior path. Additionally, acceptance contracts lacked mandatory intent-binding clauses and demonstration gates.

**Impact**: Trust-critical process failure. False-positive completeness undermines the Augmentative Partnership principle ([MANIFESTO.md § Foundational Principle: Augmentative Partnership](../../MANIFESTO.md#foundational-principle-augmentive-partnership)) — agents and humans must operate with shared, verifiable understanding of capability scope.

**Solution approach**: Five guardrail tracks (A–E) implement intent-bound readiness contracts, capability matrices, mandatory demos, drift detection, and communication safety protocols.

---

## Hypothesis Validation

### Hypothesis

Current readiness gating is insufficient to prevent subsystem-level completeness from being misinterpreted as outcome-level readiness. Without explicit intent-binding contracts and end-to-end demonstration gates, partial-capability subsystems can generate false-positive readiness signals.

### Evidence

**Incident chronology** (from issue #402):
- Commit `2f16720` added health/local-test/adoption gates (retrieval ops).
- Commit `893a068` fixed natural-language query normalization (retrieval UX).
- Manual checks were executed and interpreted as readiness proof.
- Direct "use it" interactions returned retrieval metadata and chunk lists, not grounded generated answers.
- Result: readiness communicated as complete while baseline user outcome remained incomplete.

**Validation**: The hypothesis is **confirmed**. Subsystem gates (retrieval health, query ops) were treated as evidence of end-to-end capability without validating the generated-answer path.

---

## Pattern Catalog

### Root-Cause Pattern 1: Readiness Scope Inversion

**Definition**: Readiness is assessed at subsystem level (index/query health) instead of outcome level (end-user answer generation).

**Anti-pattern**: 
- Gates prove retrieval correctness and operations.
- Conclusion: "Retrieval is ready."
- Misinterpretation: "RAG is ready" (gap: generation path not validated).

**Canonical example**:
- Sprint 1/2: retrieval health checks passed; natural-language query pipeline was optimized; manual diagnostics appeared green.
- Misread: "delivery is complete."
- Reality: chunk retrieval works; generated answers do not.

**Manifestation in MANIFESTO context**: Violates [MANIFESTO.md § 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens) — the gate algorithm is deterministic but targets the wrong outcome. Determinism ≠ correctness when applied to an incomplete acceptance scope.

---

### Root-Cause Pattern 2: Gate Design Gap

**Definition**: Current acceptance gates prove subsystem correctness but do not gate on generated-answer behavior.

**Anti-pattern**:
- Gate checks: index health, query normalization, retrieval precision/recall.
- Missing check: generated answer quality, citation accuracy, grounded-text output behavior.

**Canonical example**:
- Acceptance criteria: "retrieval pipeline passes health checks and returns correct chunks."
- Missing criteria: "system produces grounded, cited answer text in response to user question."

**Manifestation in MANIFESTO context**: Violates [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — internal knowledge (what gates exist, what they validate) was not made visible to decision-makers. The gate list appeared complete but omitted the critical user-outcome dimension.

---

### Root-Cause Pattern 3: Language/Decision Protocol Gap

**Definition**: Binary "ready" statements were allowed without an explicit capability matrix (retrieval-only vs augmentation+generation vs end-to-end).

**Anti-pattern**:
- Status claim: "Ready."
- Context: unclear which capability was completed (retrieval? generation? both?).
- Listener interpretation: defaults to maximum scope (full RAG end-to-end).

**Canonical example**:
- Claim: "RAG delivery is ready."
- Actual capability: retrieval and query normalization are complete; generation pipeline not validated.
- Listener assumption: entire stack ready to use for user questions.
- Failure: user attempts real question → receives metadata, not answer.

**Manifestation in MANIFESTO context**: Violates [MANIFESTO.md § Foundational Principle: Augmentative Partnership](../../MANIFESTO.md#foundational-principle-augmentive-partnership) — shared understanding of capability scope was not maintained. Agents and humans did not have aligned definitions of "ready."

---

### Root-Cause Pattern 4: Plan-to-Intent Drift

**Definition**: Workplan completion was treated as equivalent to human intent completion. Planning artifacts encoded implementation slices but not explicit top-level acceptance invariants.

**Anti-pattern**:
- Workplan milestone: "Phase 2: query pipeline — COMPLETE"
- Acceptance contract: missing or implicit.
- Interpretation: "intent is satisfied if plan is complete."
- Reality: plan is complete; intent is not.

**Canonical example**:
- Workplan deliverables: [retrieval index ✓], [query normalizer ✓], [health checks ✓].
- Human intent (from issue): "tool can RAG dogma end-to-end for a real question."
- Verdict: deliverables complete, but intent not satisfied (generation path not included in plan).

**Manifestation in MANIFESTO context**: Violates [MANIFESTO.md § 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens) — planning's role is to encode decision logic (what must be true for readiness). If the plan does not encode the full acceptance invariant, the algorithm is incomplete.

---

### Root-Cause Pattern 5: Demonstration Mismatch

**Definition**: When asked to "use it," the workflow defaulted to low-risk diagnostics (retrieval metrics, chunk verification) instead of executing the user-intended task path (end-to-end answer generation with citations).

**Anti-pattern**:
- User request: "Show me it working on a real question."
- System response: returns retrieval stats, chunk counts, diagnostic metadata.
- User receives: evidence of partial subsystem function, not evidence of capability to answer.

**Canonical example**:
- Demo request: "Can the system generate a grounded answer to 'how does [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) apply to script adoption?'"
- Response received: "5 relevant chunks retrieved; retrieval precision = 0.87."
- Missing: "Here is the generated answer with citations: [full answer text + sources]."

**Manifestation in MANIFESTO context**: Violates [MANIFESTO.md § 3 Local-Compute-First § Principle](../../MANIFESTO.md#3-local-compute-first) — demonstration should be immediate and verifiable locally. Instead, the "demonstration" requires interpretation of metrics rather than direct observation of the target behavior.

---

## Recommendations

### Recommendation 1: Intent-Bound Readiness Contract (Track A)

**Definition**: Define a single readiness contract file for each initiative with:
- Human intent statement (job-to-be-done) — e.g., "system can generate grounded answers to questions about dogma with citations"
- Mandatory end-to-end acceptance tests
- Disallowed readiness wording when tests are incomplete

**Action**:
- Draft `docs/guides/readiness-contracts.md` with intent-bound template (mustache variables for scope, acceptance criteria, test artifacts)
- Require every workplan phase to reference this contract by file path
- Store finalized contracts in project root or `docs/plans/<initiative>/intent-contract.md`

**Encoding point**: Store in AGENTS.md under Phase Gate sequence or in session-management SKILL.md as a pre-phase checklist item.

---

### Recommendation 2: Capability Matrix Requirement (Track B)

**Definition**: Any readiness/status response must include explicit dimensions:
- Retrieval status (yes/partial/no)
- Augmentation status (yes/partial/no)
- Generation status (yes/partial/no)
- End-to-end status (yes/partial/no)

Prohibit unqualified "ready" if any required dimension is not passing.

**Action**:
- Add Capability Matrix template to `docs/guides/readiness-contracts.md`
- Create script `scripts/check_readiness_matrix.py` to validate status claims; rejects unscoped "ready" wording in issue bodies, pull request descriptions, and session summaries
- Add pre-commit hook that prevents commits with "ready" language unless accompanied by a capability matrix

**Encoding point**: Store matrix validation logic in `scripts/check_readiness_matrix.py` and reference from phase-gate-sequence SKILL.md.

---

### Recommendation 3: Demo-before-Claim Gate (Track C)

**Definition**: Add mandatory "real user question" demo gate before readiness claims. Gate requires returning grounded answer text with citations, not just chunk metadata.

**Action**:
- Extend RAG validation commands/tests to include a generated-answer test with citation assertions
- Store demo artifacts (question + grounded answer + source citations) in phase artifacts
- Require demo artifact link in every readiness claim

**Encoding point**: Integrate into workplan template as a mandatory "Demos" section; reference from phase-gate-sequence SKILL.md.

---

### Recommendation 4: Plan-to-Intent Drift Check (Track D)

**Definition**: Add pre-close checklist script that compares:
- workplan deliverables
- acceptance contract (intent statement + acceptance tests)
- demonstrated outputs

Fail if deliverables are complete but intent contract is not satisfied.

**Action**:
- Create script `scripts/check_plan_to_intent_drift.py` that:
  - reads intent contract file
  - reads workplan file
  - runs acceptance tests identified in contract
  - flags if any test fails despite plan completion
- Integrate into phase-gate-sequence SKILL.md as final pre-commit check before closing issue
- Add corresponding GitHub Actions CI gate

**Encoding point**: Store drift-check logic in `scripts/check_plan_to_intent_drift.py` and integrate into validate-before-commit SKILL.md.

---

### Recommendation 5: Communication Safety Protocol (Track E)

**Definition**: Add language guardrail to agent instructions and documentation:
- If capability is partial, response must use scoped wording (e.g., "retrieval-ready only, generation in progress")
- Ban absolute readiness language without end-to-end evidence artifact

**Action**:
- Update AGENTS.md with new constraint: "Readiness language must be capability-scoped. Prohibited: unqualified 'ready' without a capability matrix or demo artifact."
- Update agent files (.agent.md) to reference this constraint
- Add linting rule to `scripts/check_agent_language.py` (candidate) that detects unscoped readiness claims in agent prompts

**Encoding point**: Store in AGENTS.md § Security Guardrails or new Readiness Language Guard section; cross-reference from all agent role files.

---

## Concrete Deliverables (Implementation Roadmap)

The following tracks should be implemented as GitHub issues and prioritized:

| Track | Primary Deliverable | Secondary Artifacts | Target Commitment |
|-------|-------------------|-------------------|------------------|
| A | `docs/guides/readiness-contracts.md` + intent-contract template | workplan template extension | #[TBD] |
| B | `scripts/check_readiness_matrix.py` | pre-commit hook, capability matrix template | #[TBD] |
| C | RAG validation test suite extension + demo artifact requirement | workplan "Demos" section | #[TBD] |
| D | `scripts/check_plan_to_intent_drift.py` | CI gate integration | #[TBD] |
| E | AGENTS.md language guard + agent prompt updates | `scripts/check_agent_language.py` (candidate) | #[TBD] |

---

## Acceptance Criteria (This Analysis)

- [x] Root-cause patterns documented (5 identified)
- [x] Each pattern mapped to MANIFESTO.md axiom violation
- [x] Canonical examples extracted from issue #402 and incident chronology
- [x] Proposed guardrail tracks (A–E) aligned with Pattern Catalog
- [x] Recommendations map 1:1 to tracks
- [x] Implementation roadmap provided with concrete deliverables
- [x] Document follows D4 schema (Executive Summary, Hypothesis Validation, Pattern Catalog, Recommendations, Sources)

---

## Sources

All findings synthesized from issue #402 retrospective analysis. No external sources required.

**Primary source**: [Readiness False-Positive Retrospective Issue #402](https://github.com/EndogenAI/dogma/issues/402)

**Related governance documents**:
- [MANIFESTO.md](../../MANIFESTO.md) — Axioms: [§ 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first), [§ 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens), [Foundational Principle: Augmentative Partnership](../../MANIFESTO.md#foundational-principle-augmentive-partnership)
- [AGENTS.md § Security Guardrails](../../AGENTS.md#security-guardrails) — Two-Stage Gate for irreversible actions (related pattern)

---

**Document closes**: [Issue #402 — Readiness False-Positive Retrospective](https://github.com/EndogenAI/dogma/issues/402)
