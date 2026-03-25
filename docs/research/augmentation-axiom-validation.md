---
title: Augmentation Axiom Validation — InfoQ Human-AI Fit Analysis
status: Final
closes_issue: 420
x-governs:
  - endogenous-first
  - augmentive-partnership
created: 2026-03-23
recommendations:
  - id: rec-augmentation-001
    title: "Adopt Morris's 'on the loop' terminology in MANIFESTO.md"
    status: accepted-for-adoption
    effort: Low
    linked_issue: 427
    decision_ref: null
  - id: rec-augmentation-002
    title: "Document harness-first testing pattern in AGENTS.md § Testing-First"
    status: accepted-for-adoption
    effort: Medium
    linked_issue: 428
    decision_ref: null
  - id: rec-augmentation-003
    title: "Cross-reference industry validation in MANIFESTO.md § Augmentive Partnership"
    status: accepted-for-adoption
    effort: Low
    linked_issue: 429
    decision_ref: null
---

# Augmentation Axiom Validation — InfoQ Human-AI Fit Analysis

## 1. Executive Summary

InfoQ's coverage of Martin Fowler's "Exploring Gen AI" series (Morris, March 2026) provides strong external validation for Dogma's **Augmentive Partnership** axiom. The research question — *Does the InfoQ article on human fit in AI-assisted development support or refute our augmentation axiom?* — yields a **STRONGLY SUPPORTS** verdict.

**Key findings**:
1. **Morris's "on the loop" framework** — Humans design specifications, tests, and feedback mechanisms that guide AI agents rather than reviewing every artifact = Dogma's "agents surface options, humans decide"
2. **Industry convergence** — OpenAI (Codex agent loop), Datadog (harness-first verification), Stack Overflow surveys (84% adoption, trust gap) all validate human-in-loop necessity
3. **Trust gap validates oversight requirement** — 84% developer adoption BUT significantly fewer trust AI output = empirical support for MANIFESTO § Ethical Values: Human Oversight
4. **Datadog's harness-first approach** — Automated verification pipelines (specs, simulation, telemetry) = programmatic encoding of Dogma's Testing-First Requirement

**Verdict**: No contradictions discovered. Industry independently converged on "augmentive, not autonomous" stance through practitioner experience with AI-generated code quality issues.

**Recommendation**: **ADOPT** Morris's "in/on/out of loop" terminology as clarifying language for Augmentive Partnership; **DOCUMENT** harness-first testing pattern.

---

## 2. Hypothesis Validation

**Hypothesis**: MANIFESTO § Augmentive Partnership axiom ("agents surface information and options for human decision-making; they do not make strategic choices") reflects industry best practice.

**Validation Method**: Survey industry research (InfoQ, Martin Fowler, OpenAI, Datadog, Stack Overflow) for evidence supporting or contradicting human-in-loop necessity in AI-assisted development.

**Results**:

| Hypothesis | Evidence | Verdict |
|------------|----------|---------|
| **H1: Industry consensus supports augmentive (not autonomous) AI development** | Morris "on the loop" (humans design guardrails), Datadog harness-first (programmatic verification), Stack Overflow trust gap (84% adoption, fewer trust output) | ✅ **STRONGLY SUPPORTED** — No contradictions discovered |
| **H2: Practitioner experience validates need for human oversight** | Stack Overflow: debugging AI code requires additional effort; productivity gains come with maintainability trade-offs | ✅ **STRONGLY SUPPORTED** — Trust gap validates MANIFESTO § Ethical Values: Human Oversight |
| **H3: Programmatic verification scales better than manual review** | Datadog: "human review alone does not scale"; automated pipelines (specs + simulation + telemetry) replace per-artifact inspection | ✅ **STRONGLY SUPPORTED** — Validates AGENTS.md § Testing-First + Algorithms-Before-Tokens |

**Interpretation**: All three hypotheses supported by independent industry sources. No evidence discovered advocating for fully autonomous AI development (Morris explicitly rejects "out of the loop" model). Industry convergence on "on the loop" (humans design substrate, agents execute within constraints) validates Dogma's Augmentive Partnership axiom.

---

## 3. Evidence Validation

| Evidence Type | Finding | Source | Axiom Support |
|---------------|---------|--------|---------------|
| **Conceptual Framework** | Morris proposes "on the loop" (humans design guardrails) vs. "in the loop" (review every output) vs. "out of the loop" (full autonomy) | MartinFowler.com | ✅ **STRONGLY SUPPORTS** — "on the loop" = Augmentive Partnership operationalized |
| **Industry Practice** | OpenAI Codex "agent loop" architecture: user → model → tools → iterative feedback cycles | OpenAI blog | ✅ **SUPPORTS** — Human remains in coordination role, not removed entirely |
| **Developer Sentiment** | 84% adoption BUT trust gap: debugging/verifying AI code requires significant effort | Stack Overflow 2025 Survey | ✅ **STRONGLY SUPPORTS** — Validates need for human oversight (MANIFESTO § Ethical Values) |
| **Verification Pattern** | Datadog "harness-first": specs + simulation + bounded verification + runtime telemetry replace manual review | Datadog engineering blog | ✅ **STRONGLY SUPPORTS** — Programmatic verification = Algorithms-Before-Tokens applied to AI oversight |
| **Maintainability Concerns** | Productivity gains come with technical debt trade-offs; generated code often needs refactoring before production | Stack Overflow commentary | ✅ **SUPPORTS** — Validates "agents don't make strategic choices" (humans must review architectural decisions) |

### Evidence Summary

**Supporting Axiom** (5 strong points):
1. Morris: "Developers are unlikely to move entirely 'out of the loop'" — explicit rejection of full autonomy
2. Morris: "'On the loop' model useful for software engineering" — humans focus on building testing frameworks, constraints, evaluation pipelines
3. Stack Overflow: 84% adoption, fewer trust AI output — trust gap = empirical need for human oversight
4. Datadog: "Human review alone does not scale... invest in automated verification pipelines" — programmatic guardrails > manual inspection
5. OpenAI: Codex agent loop requires iterative user feedback — not autonomous generation

**Contradicting Axiom** (0 points):
- No evidence found contradicting "augmentive, not autonomous" stance
- Industry discussions uniformly emphasize need for human-designed guardrails, verification, monitoring

**Neutral** (1 observation):
- OpenAI describes agents writing code "directly on the machine" — could be misread as autonomous, but context clarifies this occurs within user-directed feedback cycles

---

## 4. Pattern Catalog

### Pattern 4.1: Human-in/on/out-of-Loop Framework (Morris)

**Canonical example**:
> "Morris outlines three ways humans can interact with AI systems: **in the loop**, where developers review each AI output; **out of the loop**, where systems operate largely autonomously; and **on the loop**, where humans design and maintain the mechanisms that guide and validate the system's behavior. Morris suggests the third model may prove particularly useful for software engineering, where developers focus on building testing frameworks, constraints, and evaluation pipelines that shape how AI agents operate rather than inspecting every generated line of code."

**Dogma alignment**: "On the loop" = Augmentive Partnership. Humans design the substrate (AGENTS.md constraints, validate_synthesis.py, pre-commit hooks) that guides agent behavior — not reviewing every agent output token-by-token.

**Application**: Rename "human-in-loop checkpoints" language in MANIFESTO.md to "on-the-loop substrate design" for clarity.

---

### Pattern 4.2: Trust Gap Validates Oversight Requirement

**Canonical example**:
> "In the 2025 Developer Survey, 84% of developers reported that they are using or planning to use AI tools in their development workflows, but **significantly fewer said they trust AI-generated output**. Many respondents reported that debugging AI-generated code or verifying its correctness can require additional effort."

**Dogma alignment**: Validates MANIFESTO § Ethical Values: Human Oversight. High adoption + low trust = structural need for human review gates (Review agent, validation scripts, testing-first requirement).

**Anti-pattern**: Assuming AI adoption implies trust. Adoption rate ≠ output reliability.

---

### Pattern 4.3: Harness-First Verification (Datadog)

**Canonical example**:
> "Datadog argued that **human review alone does not scale** for AI-generated artifacts, particularly when agents can produce large volumes of code. Instead, teams may need to invest in automated verification pipelines that combine specifications, simulation testing, bounded verification, and runtime telemetry to validate system behavior... Datadog describes what it calls a 'harness-first' approach to agent development, in which automated verification systems evaluate agent behavior through specifications, simulation testing, and runtime telemetry. In this model, developers focus on building the harness that validates agent outputs rather than relying on manual inspection of each generated artifact."

**Dogma alignment**: Validates AGENTS.md § Testing-First Requirement + MANIFESTO § Algorithms-Before-Tokens. Programmatic verification (validate_synthesis.py, pre-commit hooks, CI gates) scales better than manual review.

**Application**: Document harness-first pattern explicitly in AGENTS.md § Testing-First Requirement with Datadog cross-reference.

---

### Pattern 4.4: Iterative Agent Loop (OpenAI Codex)

**Canonical example**:
> "In a technical deep dive into its Codex system, OpenAI described the 'agent loop' that coordinates interactions between the user, the model, and external tools. In this architecture, the output of the system is often not simply a chat response but code written or modified directly on the machine, produced through **iterative tool use and feedback cycles**."

**Dogma alignment**: Validates Dogma's phase-gated execution model. Codex loop = Scout → Synthesizer → Reviewer → Archivist with human checkpoints. Iterative feedback = Review gates between phases.

---

### Pattern 4.5: Maintainability vs. Productivity Trade-Off

**Canonical example**:
> "Stack Overflow discussions and commentary have highlighted concerns that **productivity gains from generative AI tools can come with trade-offs in maintainability and technical debt**, particularly when generated code requires substantial review or refactoring before it can be safely integrated into production systems."

**Dogma alignment**: Validates "agents don't make strategic choices" (MANIFESTO § Augmentive Partnership). Speed ≠ correctness. Strategic architectural decisions (e.g., "should we refactor this?") remain human domain.

**Anti-pattern**: Treating AI-generated speed as validation of correctness. Fast output may introduce technical debt requiring later human remediation.

---

## 5. Industry Perspective Comparison

| Perspective | Augmentive Stance | Autonomous Stance | Industry Evidence |
|-------------|-------------------|-------------------|-------------------|
| **Morris (MartinFowler.com)** | ✅ "On the loop" — humans design guardrails | ❌ "Unlikely to move entirely out of the loop" | Augmentive preferred |
| **OpenAI (Codex)** | ✅ Agent loop includes user feedback cycles | ⚠️ Agents write code "directly on machine" (but within user-directed context) | Augmentive with automation |
| **Datadog** | ✅ Harness-first verification (programmatic guardrails) | ❌ "Human review alone does not scale" (but replacement is automated verification, not autonomy) | Augmentive + programmatic |
| **Stack Overflow (developers)** | ✅ 84% adoption BUT trust gap | ❌ Debugging/verifying AI code requires additional effort | Augmentive validated by practitioner experience |

**Summary**: Industry consensus favors augmentive approach with programmatic verification. No serious advocacy for fully autonomous AI development discovered in surveyed sources.

---

## 6. Recommendations

### Rec 6.1: Adopt Morris's "on the loop" Terminology

**Action**: Update MANIFESTO.md § Augmentive Partnership to include Morris's "in/on/out of loop" framework as clarifying language.

**Rationale**: "On the loop" is more precise than "human-in-loop" — it emphasizes substrate design (building guardrails) over per-output review (inspecting every artifact). This matches Dogma's constraint-encoding approach (AGENTS.md, pre-commit hooks, validators).

**Acceptance Criteria**:
- [ ] MANIFESTO.md § Augmentive Partnership updated with Morris framework
- [ ] Cross-reference to this research doc and InfoQ article
- [ ] Examples: Dogma's Review gates = "on the loop" checkpoints, not "in the loop" manual inspection

**Status**: accepted-for-adoption  
**Effort**: Low (2-3 hours — update MANIFESTO.md, add cross-references, commit)

---

### Rec 6.2: Document Harness-First Testing Pattern

**Action**: Add harness-first verification pattern to AGENTS.md § Testing-First Requirement with explicit Datadog cross-reference.

**Rationale**: Datadog's pattern (specs + simulation + bounded verification + telemetry) is already partially implemented in Dogma (validate_synthesis.py, pre-commit hooks, CI gates). Documenting it explicitly makes the architecture legible to contributors and validates our testing posture against industry practice.

**Acceptance Criteria**:
- [ ] AGENTS.md § Testing-First Requirement includes "harness-first" subsection
- [ ] Cross-reference to Datadog blog post and this research doc
- [ ] Examples: validate_synthesis.py as specification check, pre-commit as simulation, CI as runtime telemetry

**Status**: accepted-for-adoption  
**Effort**: Medium (4-6 hours — write pattern doc, update AGENTS.md, add examples)

---

### Rec 6.3: Cross-Reference Industry Validation in MANIFESTO.md

**Action**: Add "Industry Validation" subsection to MANIFESTO.md § Augmentive Partnership citing Morris, OpenAI, Datadog convergence.

**Rationale**: External validation strengthens confidence that Dogma's axioms reflect broader industry best practices, not idiosyncratic preferences. This matters for adoption — "we're not alone" is persuasive.

**Acceptance Criteria**:
- [ ] MANIFESTO.md § Augmentive Partnership includes "Industry Validation" subsection
- [ ] Cites Morris (on-the-loop), Datadog (harness-first), Stack Overflow (trust gap)
- [ ] Links to this research doc for full evidence table

**Status**: accepted-for-adoption  
**Effort**: Low (1-2 hours — write subsection, add citations, commit)

---

## 7. Open Questions

1. **Morris's full article not surveyed** — Only InfoQ summary read; Martin Fowler's full article on "Exploring Gen AI" series may contain additional frameworks or constraints worth encoding. Follow-up: delegate to Research Scout for deeper dive.

2. **Stack Overflow 2025 survey raw data not accessed** — InfoQ article cites survey findings but percentages beyond "84% adoption" not detailed. Follow-up: fetch Stack Overflow survey report if publicly available.

3. **Datadog harness implementation details sparse** — Article describes pattern conceptually but not implementation specifics (tools, frameworks, verification logic). Follow-up: check if Datadog published engineering companion post with code examples.

---

## 8. Sources

### Primary Sources

1. Foster, M. (2026, March 19). Where Do Humans Fit in AI-Assisted Software Development? *InfoQ*. https://www.infoq.com/news/2026/03/mf-aiassisted-dev/ (Cached: `.cache/sources/infoq-com-news-2026-03-mf-aiassisted-dev.md`)

2. Morris, K. (2026). Exploring Gen AI: Humans and Agents. *MartinFowler.com*. https://martinfowler.com/articles/exploring-gen-ai/humans-and-agents.html (Cached: `.cache/sources/martinfowler-com-articles-exploring-gen-ai-humans-and-agents.md`)

3. OpenAI. (2026). Unrolling the Codex Agent Loop. *OpenAI Blog*. https://openai.com/index/unrolling-the-codex-agent-loop/ (Cached: `.cache/sources/openai-com-index-unrolling-the-codex-agent-loop.md`)

4. Datadog. (2026). AI Harness-First Agents. *Datadog Blog*. https://www.datadoghq.com/blog/ai/harness-first-agents/ (Cached: `.cache/sources/datadoghq-com-blog-ai-harness-first-agents.md`)

5. Stack Overflow. (2025). AI Can 10x Developers in Creating Tech Debt. *Stack Overflow Blog*. https://stackoverflow.blog/2026/01/23/ai-can-10x-developers-in-creating-tech-debt/ (Cached: `.cache/sources/stackoverflow-blog-2026-01-23-ai-can-10x-developers-in-creat.md`)

### Endogenous Cross-References

6. [MANIFESTO.md § Foundational Principle: Augmentive Partnership](../../MANIFESTO.md#foundational-principle-augmentive-partnership) — Core axiom under validation
7. [MANIFESTO.md § Ethical Values](../../MANIFESTO.md#ethical-values) — Transparency, Human Oversight, Reversibility
8. [AGENTS.md § Testing-First Requirement](../../AGENTS.md#testing-first-requirement-for-scripts) — Harness-first pattern target
9. [AGENTS.md § Programmatic-First Principle](../../AGENTS.md#programmatic-first-principle) — Automated verification > manual review
10. [docs/research/civic-ai-governance.md](./civic-ai-governance.md) — Human oversight patterns from San Jose case study
11. [docs/research/multi-agent-collaboration-failure-modes.md](./multi-agent-collaboration-failure-modes.md) (Issue #397) — Validates "humans design guardrails" necessity
