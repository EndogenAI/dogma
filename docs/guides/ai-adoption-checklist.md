---
x-governs: [ai-tool-adoption, values-extraction, procurement-gates]
closes_issue: 379
---

# AI Tool Adoption Checklist

> **Closes issue #379.** Derived from [`docs/research/civic-ai-governance.md`](../research/civic-ai-governance.md) Recommendation 4 — the 30-day values extraction pattern from San Jose's Departmental AI Governance Mandate.

This checklist governs AI tool adoption in the EndogenAI Workflows project. No new AI tool, model, or agent capability may be adopted without completing this process. The output is a committed **Adoption Decision Record** (see [Week 4](#week-4-adoption-decision-record)) that becomes the acceptance criteria for the adoption Review gate.

**Governing axioms**: [MANIFESTO.md § Ethical Values](../../MANIFESTO.md#ethical-values) — values specification precedes tool selection; [MANIFESTO.md §1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — build from existing knowledge before reaching outward.

**Mandatory prerequisite**: Work through this checklist *before* writing any implementation code. See also [AGENTS.md § New Tool Encoding Gate](../../AGENTS.md#toolchain-reference) and [AGENTS.md § Ethical Values Procurement Rubric](../../AGENTS.md#ethical-values-procurement-rubric).

---

## Overview: 4-Week Schedule

| Week | Phase | Deliverable |
|------|-------|-------------|
| **Week 1** | Stakeholder Interviews | Interview notes in `.tmp/<branch>/` or `docs/research/sources/` |
| **Week 2** | Draft Values Statement | Written values statement answering 3 required questions |
| **Week 3** | Values-to-Proxy Mapping | Proxy mapping table committed to research doc |
| **Week 4** | Adoption Decision Record | Committed record; Review gate cleared |

> **Scope note**: For tool adoptions with clear internal overlap (≥60% use-case match with existing scripts), run [AGENTS.md § New Tool Encoding Gate](../../AGENTS.md#toolchain-reference) criterion 1 before starting Week 1. If overlap is confirmed, document it in the Decision Record rather than proceeding with adoption.

---

## Week 1: Stakeholder Interviews

**Goal**: Surface what outcomes this tool must optimize for and what constraints it cannot violate — from the people who will use or be affected by it.

**Who to consult**: Any contributor, agent role, or workflow that will interact with this tool. For fleet-wide tools: Executive Orchestrator, Executive Docs, Executive Scripter. For infrastructure tools: Executive Automator.

### Interview Guide (5–7 questions)

Ask each stakeholder:

1. **What problem does this tool solve that we cannot solve today without it?**
   *(Surfaces genuine need vs. novelty adoption)*

2. **What existing script or workflow does this tool come closest to replacing or overlapping with?**
   *(Implements Endogenous-First check — documents overlap before adoption)*

3. **What would it mean for this tool to fail us? Describe the worst-case outcome.**
   *(Extracts implicit constraints — what must the tool never do)*

4. **Who should have override authority if the tool produces an unacceptable result?**
   *(Operationalizes human oversight — identifies accountability chain)*

5. **How would you know, six months from now, that this tool is drifting from its original purpose?**
   *(Reveals proxy-drift risk — what early signals indicate misalignment)*

6. **Which of Dogma's core values (transparency, human oversight, reproducibility, auditability, reversibility) is most at risk if this tool behaves unexpectedly?**
   *(Maps tool to [AGENTS.md § Ethical Values Procurement Rubric](../../AGENTS.md#ethical-values-procurement-rubric) criteria)*

7. **What would make you recommend we remove this tool from the fleet?**
   *(Defines the exit condition — prevents lock-in)*

> **Record responses** in `.tmp/<branch>/` scratchpad or a `docs/research/sources/<tool-name>-stakeholder-notes.md` file. These notes feed directly into the Week 2 values statement.

---

## Week 2: Draft Values Statement

**Goal**: Synthesize interview notes into a written values statement. This statement becomes the acceptance criteria for the adoption Review gate.

### Required Questions (all three must be answered)

1. **What outcomes must this tool optimize for?**
   *(e.g., "Reduce per-query token cost by ≥30% without degrading synthesis quality")*

2. **What constraints can this tool never violate?**
   *(e.g., "Must not send request payloads containing file content outside our workspace to a third-party endpoint without an explicit user-visible disclosure")*

3. **Who has override authority?**
   *(e.g., "Executive Orchestrator may disable tool at session start; any contributor may raise a blocking issue")*

> **Format**: Write the values statement as a `## Values Statement` section in the research doc. It should be readable in < 2 minutes — if it requires a technical background to parse, rewrite it.

### Anti-pattern

Treating values as post-hoc justification: writing the values statement *after* you have already chosen the tool and are writing implementation code. The values statement is the procurement specification, not a retrospective description of what the tool happens to do.

---

## Week 3: Values-to-Proxy Mapping

**Goal**: For each stated value, identify a measurable proxy metric and document its drift risk.

### Proxy Mapping Table

| Value | Proxy Metric | Proxy-Drift Risk |
|-------|-------------|-----------------|
| Transparency | Non-technical description accurate in ≤ 2 min (binary Y/N, quarterly) | Fails if tool behavior complexity outpaces the plain-language description |
| Human Oversight | Kill-switch documented and tested: works without reimplementing the tool (binary Y/N) | Fails if tool dependency footprint grows to the point that removal requires rewriting dependents |
| Reproducibility | Given the same input twice, output is identical or within defined tolerance | Fails if tool introduces external state (remote API with changing models, unversioned cache) |
| Auditability | Invocation log exists with tool name, inputs, outputs, exit code (completeness %) | Fails if log format changes without migration, or log is gitignored and lost |
| Reversibility | Disable and revert to prior workflow within one session, without data loss (binary Y/N, tested at adoption) | Fails if tool introduces writes to shared state unreplicable by the prior workflow |

> **Customize this table** for the specific tool being evaluated. Add rows for tool-specific values raised during Week 1 interviews. Remove rows for values already covered by existing fleet guardrails.

### Drift Detection Protocol

At quarterly values alignment review, re-evaluate each proxy:
- Has the tool's behavior changed in a way that breaks the proxy assumption?
- Has the proxy itself become a gaming target (Goodhart's Law)?
- Does override authority still work as documented?

Any "no" answer triggers a Review gate before the tool continues in production.

---

## Week 4: Adoption Decision Record

**Goal**: Commit a formal record that serves as the gate artifact for the Review agent.

### Adoption Decision Record Format

```markdown
## Adoption Decision Record — [Tool Name]

**Date**: YYYY-MM-DD
**Author**: [Agent or contributor name]
**Review status**: [ ] Pending / [x] Approved / [ ] Rejected

---

### Purpose
One sentence: what problem this tool solves and why existing solutions are insufficient.

### Values Articulated
- Optimizes for: ...
- Must never violate: ...
- Override authority: ...

### Ethics Rubric Assessment
From AGENTS.md § Ethical Values Procurement Rubric (minimum 3 required):
- [ ] Transparency — inspectable in < 2 min by non-technical person?
- [ ] Human Oversight — kill-switch without reimplementation?
- [ ] Reproducibility — deterministic output given same inputs?
- [ ] Auditability — traceable log of what tool did and why?
- [ ] Reversibility — disable and revert within one session without data loss?

**Criteria met**: N/5

### Accepted Proxies
(Paste proxy mapping table from Week 3)

### Review Cadence
(e.g., Quarterly values alignment review — next: YYYY-MM-DD)

### Override Authority
(Name the role(s) with authority to disable or remove this tool)
```

> **Filing**: Commit the Decision Record as `docs/research/adoption-<tool-slug>.md` with `status: Pending` frontmatter until Review APPROVED. Update to `status: Final` after approval. The Review agent validates the record against [AGENTS.md § Ethical Values Procurement Rubric](../../AGENTS.md#ethical-values-procurement-rubric) and [AGENTS.md § New Tool Encoding Gate](../../AGENTS.md#toolchain-reference).

---

## Relationship to AGENTS.md Procurement Rubric

[AGENTS.md § Ethical Values Procurement Rubric](../../AGENTS.md#ethical-values-procurement-rubric) defines the **5 criteria** any tool must satisfy (minimum 3):

1. **Transparency** — inspectable in < 2 min by a non-technical person
2. **Human Oversight** — kill-switch that works without reimplementation
3. **Reproducibility** — deterministic output given same inputs
4. **Auditability** — traceable evidence of what happened and why
5. **Reversibility** — disable and revert within one session without data loss

**How this checklist and the rubric fit together**: The rubric is the *gate checkpoint* (minimum bar for adoption). This checklist is the *process* (how to surface enough knowledge to evaluate the rubric honestly). Week 1 interviews reveal which rubric criteria are at risk. The Decision Record documents which criteria were met and which were explicitly accepted as known gaps.

---

## See Also

- [AGENTS.md § New Tool Encoding Gate](../../AGENTS.md#toolchain-reference) — mandatory pre-adoption criteria (no internal overlap, ethics rubric pass, D4 research doc first)
- [AGENTS.md § Ethical Values Procurement Rubric](../../AGENTS.md#ethical-values-procurement-rubric) — 5-criterion procurement checklist
- [`docs/research/civic-ai-governance.md`](../research/civic-ai-governance.md) — source research (Recommendation 4: 30-day values extraction)
- [`docs/governance/ethical-values-procurement.md`](../governance/ethical-values-procurement.md) — detailed procurement rubric
- [`docs/guides/runtime-action-behaviors.md`](runtime-action-behaviors.md) — two-stage gate protocol for irreversible actions
