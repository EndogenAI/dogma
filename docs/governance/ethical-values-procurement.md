---
title: Ethical Values Procurement Rubric
status: Active
---

# Ethical Values Procurement Rubric

## Purpose

Operationalize [`MANIFESTO.md § Ethical Values`](../../MANIFESTO.md#ethical-values) into a procurement checklist for any new tool, agent capability, or external service before adoption. This framework ensures that every externally adopted tool is vetted against core project values before integration, instantiating the endogenous-first principle.

## Procurement Checklist (5 Criteria)

Every tool integration must satisfy at least **three** of the following criteria before adoption:

### 1. Transparency

**Signal**: Can the system's decision-making be inspected and explained to a non-technical person in < 2 minutes?

**Rationale**: Tools that hide their reasoning behind black boxes prevent human oversight and violate the endogenous principle that all governance should be explainable to stakeholders. Transparency enables accountability.

### 2. Human Oversight

**Signal**: Does the tool provide mechanisms for human review or veto? Can a human stop execution without reimplementing the tool?

**Rationale**: Automation must remain under human control. If a tool cannot be paused or stopped by a human decision, it has escaped governance bounds. This criterion prevents tooling from becoming an autonomous adversary.

### 3. Reproducibility

**Signal**: Are outputs deterministic given the same inputs? Can a decision made on day one be reproduced on day 100 identically?

**Rationale**: Non-deterministic tools fail the auditability requirement. If the same input produces different outputs over time, reproducibility is lost and the tool cannot be trusted for critical decisions.

### 4. Auditability

**Signal**: Can we trace what the tool did, why it did it, and gather evidence for review? Is there a log?

**Rationale**: Governance requires evidence trails. Without logs and traces, no human can reconstruct the decision-making path or identify where a tool failure occurred. Logging is a prerequisite for accountability.

### 5. Reversibility

**Signal**: If the tool causes harm or violates a constraint, can we disable it or roll back its decisions?

**Rationale**: Irreversible tools cannot be safely governed. If a tool makes a mistake that cannot be undone, governance is only reactive (post-harm). Reversibility ensures governance can be proactive and corrective.

## Decision Tree

- **Does the tool pass ≥3 criteria?** → Proceed to Review gate for approval
- **Does the tool pass <3 criteria?** → Reject or send back for redesign

## Procurement Workflow

1. **Values Statement** — Draft what outcomes the tool must optimize for and what constraints it can never violate
2. **Rubric Evaluation** — Assess against all five criteria. Document the evidence for each assessment
3. **Threshold Check** — Count passing criteria. If ≥3, proceed; if <3, reject or request redesign
4. **Review Gate** — Route approved tools through the **Review** agent for final validation
5. **Adoption** — Only after Review APPROVED should the tool be integrated

## Precedent

Derived from [`docs/research/civic-ai-governance.md`](../research/civic-ai-governance.md) and [`MANIFESTO.md § Ethical Values`](../../MANIFESTO.md#ethical-values).
