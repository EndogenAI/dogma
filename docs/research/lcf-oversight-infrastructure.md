---
title: "LCF as Oversight Infrastructure: Reframing Local-Compute-First as Structural Enabler"
status: "Final"
research_issue: "#209"
date: "2026-03-12"
---

# LCF as Oversight Infrastructure: Reframing Local-Compute-First as Structural Enabler

> **Research question**: Is the Local-Compute-First (LCF) axiom in `MANIFESTO.md §3` more
> accurately characterized as structural oversight infrastructure that enables the other axioms
> to function — rather than primarily a cost-optimization rule? Does this reframing warrant an
> amendment to `MANIFESTO.md §3`?
> **Date**: 2026-03-12
> **Research Issue**: #209
> **Related**: [`docs/research/lcf-programmatic-enforcement.md`](lcf-programmatic-enforcement.md)
> (F4 gap, #211); [`docs/research/values-encoding.md`](values-encoding.md) (encoding fidelity
> framework); [`docs/research/enforcement-tier-mapping.md`](enforcement-tier-mapping.md)
> (T0–T5 governor taxonomy); [`docs/research/programmatic-governors.md`](programmatic-governors.md)
> (governor design patterns); Issue #131 (Cognee/Local Compute Baseline)

---

## 1. Executive Summary

The current `MANIFESTO.md §3` frames Local-Compute-First (LCF) as a cost-minimization
directive: "Minimize token burn. Run locally whenever possible." This framing is not wrong —
cost optimization is a real and valid consequence of local compute — but it is causally
incomplete. This document argues that LCF is better understood as **oversight infrastructure**:
a structural property of the EndogenAI Workflows system that keeps enforcement authority,
iteration control, and governance mechanisms co-located with the compute substrate, thereby
*enabling* the other four axioms (Endogenous-First, Algorithms Before Tokens, Minimal Posture,
Documentation-First) to function as designed.

Evidence from four independent sources — Ink & Switch's local-first software architecture
research, the NIST AI Risk Management Framework, EU AI Act Articles 9–17, and Christiano
et al.'s oversight amplification model — converges on a structural principle: local residency
is not a cost tier, but an architectural property that determines whether oversight, enforcement,
and intervention remain accessible to the human and the organisation. The cost framing is
*downstream* of this structural guarantee, not the reason for it.

The document also addresses a specific tension: `MANIFESTO.md §3`'s claim that the absence of
a CI gate is "intentional" because full semantic enforcement of LCF is infeasible statically.
This claim is valid within its scope, but it requires narrowing in light of the #211 research
finding that observable-proxy signals *are* statically tractable. The two claims address
different enforcement surfaces and are resolved explicitly in Section 4.

**Verdict: Y — a MANIFESTO §3 amendment is warranted.** The amendment should add 2–3 sentences
characterizing LCF as oversight infrastructure and clarifying the scope of the
"intentional no-CI-gate" rationale. The existing cost framing is retained; it is accurate
but incomplete.

---

## 2. Hypothesis Validation

### H1 — LCF Is a Cost-Optimization Fallback

**Claim**: `MANIFESTO.md §3`'s current framing accurately characterizes LCF as a strategy for
choosing the least expensive compute option — a fallback that activates after Axioms 1 and 2
are exhausted.

**Evidence in favour**:

- The phrase "Minimize token burn" is an explicit cost signal. Token burn maps directly to API
  cost, latency, and context window consumption — all quantifiable metrics.
- The axiom priority ordering (§How to Read This Document) places LCF at position 3, after
  Endogenous-First and Algorithms Before Tokens, consistent with a "fall back to local if
  cheaper" interpretation.
- Running validators locally (e.g., `validate_synthesis.py`) is observably cheaper than
  equivalent cloud inference — the cost framing accurately predicts the behavior in normal cases.

**Counter-evidence**:

- The cost framing provides no principled guidance when local and cloud have comparable cost.
  If an agent could run a task via a free cloud tier, the cost framing would suggest cloud is
  acceptable — but this misses the governance guarantees (human-in-the-loop retention,
  enforcement proximity) that local residency provides and cloud cannot.
- Lock-in economics (Shapiro & Varian, *Information Rules*, 1998): the cost framing obscures
  the switching-cost gradient. A codebase whose inference layer is progressively outsourced to
  cloud APIs accumulates structural lock-in not reflected in per-token cost. An agent fleet
  dependent on cloud inference cannot be Endogenous-First in its oversight — this is a
  structural governance cost, invisible to a pure cost accounting.
- The Ink & Switch local-first analysis reveals that framing local residency as a cost
  optimization inverts the causal direction: systems are local for structural reasons (data
  sovereignty, offline operation, enforcement proximity), and cost reduction is a *consequence*,
  not the primary rationale.

**Verdict**: H1 is **not false** — cost optimization is a genuine and valid consequence of LCF.
However, it is **causally incomplete**: it characterizes a downstream effect as the upstream
rationale. The framing is approximately right in routine agent-task scenarios but generates
incorrect trade-off decisions precisely in the cases where the structural governance properties
of LCF are most critical: cost-parity scenarios, free-tier migrations, and cases where cloud
inference is operationally convenient.

---

### H2 — LCF Is Oversight Infrastructure That Enables the Other Axioms

**Claim**: LCF is a structural property of the EndogenAI Workflows system that keeps
enforcement authority, oversight mechanisms, and iteration control local, thereby enabling
Endogenous-First, Algorithms Before Tokens, Minimal Posture, and Documentation-First to
function as designed.

**Evidence in favour**:

**From NIST AI Risk Management Framework (AI 100-1, 2023):**
The NIST RMF "Govern" function specifies that trustworthy AI requires organisations to maintain
oversight and control — including the ability to intervene, audit, and adjust model behavior.
NIST characterizes this as a structural governance requirement, not a cost optimization. The
operative mechanism is keeping decision authority *local*: to the human, to the organisation,
to the deployment context. A system in which inference is cloud-resident requires API
availability, provider policy compliance, and network access to exercise oversight — all of
which degrade the "Govern" function in unpredictable ways. In the EndogenAI context:
pre-commit hooks, `validate_synthesis.py`, and `validate_agent_files.py` run locally with
zero external dependency. This is not merely cheaper — it means oversight is *structurally
guaranteed* regardless of API status, network conditions, or provider policy changes.

**From EU AI Act Articles 9–17:**
The enforcement proximity principle is implicit throughout the EU AI Act's high-risk AI
system requirements: designated human supervisors, technical override mechanisms, and audit
trails must be operationally close to the point of action. The closer the enforcement
mechanism to the compute locus, the shorter the intervention latency and the stronger the
structural governance guarantee. In the EndogenAI context: a pre-commit hook that runs
locally has sub-millisecond intervention latency — it fires at the exact boundary where a
change is about to be committed. A cloud-mediated equivalent would introduce round-trip
latency and a dependency on external API availability at the enforcement boundary. The
governance strength of the hook is a function of its local residency, not its cost.

**From Christiano et al. (2018) — Oversight Amplification:**
Human oversight amplification requires *low-latency access*: the human must be able to
observe, query, and correct the system at the pace of the system. Long-distance, cloud-
mediated oversight degrades amplification quality because the feedback loop becomes
asynchronous. The insight is that oversight quality is not purely a function of human skill —
it is a function of the human's *access latency* to the system. In the EndogenAI context:
local validators produce synchronous, in-editor feedback. A developer running
`validate_synthesis.py` locally sees errors at the edit boundary. A cloud CI equivalent
introduces asynchronous latency (commit → push → CI trigger → pipeline execution → notify):
the feedback arrives minutes later, by which point the developer has moved on. Local residency
of the validator is what enables oversight amplification to function — not its cost.

**From Ink & Switch, "Local-First Software" (2019):**
The local-first framing distinguishes local as an architectural residency property from local
as a cost tier. A system is local-first when it can operate correctly, maintain data integrity,
and enforce its guarantees without external service availability. This is a structural
correctness property, not an optimization. Cost reduction follows as a consequence, but a
system that is local *only for cost reasons* will abandon local residency when cloud becomes
cheaper — and in doing so, silently loses the structural governance guarantees it had. Applied
to EndogenAI: if LCF is framed only as cost optimization, the fleet would correctly conclude
that a free cloud inference tier satisfies the axiom. But the structural governance
guarantees — enforcement proximity, oversight amplification, lock-in resistance — are not
restored by a price change.

**Counter-evidence**:

- The overhead of maintaining local infrastructure (Ollama, local model management, locally-
  validated-only scripts) is non-trivial. If the enabling-infrastructure pattern is adopted but
  local models systematically under-perform on key tasks, the governance benefit degrades: an
  oversight mechanism that is locally resident but unreliable does not deliver the structural
  guarantees asserted here.
- Issue #131 (Cognee baseline) is the empirical anchor for this concern: if local models cannot
  reliably perform the agent task classes for which they are invoked, the enabling-infrastructure
  framing loses operational grounding and requires exception documentation.

**Verdict**: H2 is **confirmed and well-supported** by four independent evidence streams. The
enabling relationships between LCF and the other four axioms are structurally coherent: LCF
is the substrate that keeps the enforcement, oversight, and tight-iteration mechanisms — which
are the *operational expression* of the other axioms — locally resident and structurally
available. The cost framing is downstream of this structural account; H2 provides the more
accurate causal description and generates correct prioritization decisions in all scenarios,
including cost-parity cases where H1 fails.

---

## 3. Pattern Catalog

### P1: Enforcement Proximity

**Definition**: Governance mechanisms must be co-located with what they govern. The closer the
enforcement mechanism to the compute locus, the shorter the intervention latency, the stronger
the structural guarantees, and the lower the probability that enforcement is bypassed by
external-dependency failure.

**Evidence**: NIST AI RMF "Govern" function; EU AI Act Articles 9–17 (enforcement proximity
implicit throughout high-risk system requirements, including override capability and audit
trail co-location).

**Canonical example**: `validate_synthesis.py`, `validate_agent_files.py`, and the pre-commit
hook stack all run locally. Their enforcement authority is structurally guaranteed — they
cannot be bypassed by API downtime, provider policy change, or network partition. A
cloud-resident equivalent would require availability of an external service at the exact moment
enforcement is needed. The local residency of the validator is what makes the enforcement
reliable as a governance mechanism; its speed and cost are secondary properties.

**Anti-pattern — Remote-only enforcement**: Delegating validation to a cloud CI service as the
*sole* enforcement point. This introduces a dependency on external service availability at the
enforcement boundary. When the CI service is unavailable (API outage, rate limit, network
partition), the enforcement gap is structural, not incidental — it is a predictable failure
mode of the architecture, not an edge case.

---

### P2: Oversight Residency

**Definition**: Effective human oversight requires low-latency access to the system being
overseen. Local compute provides synchronous feedback cycles; cloud-mediated oversight introduces
asynchronous latency that degrades human oversight amplification quality by decoupling the
observation event from the correction window.

**Evidence**: Christiano et al. (2018) — oversight amplification model establishes that a human
who cannot observe and correct at the pace of the system cannot amplify weak oversight signals
into strong governance, regardless of the human's skill level.

**Canonical example**: A developer running
`uv run python scripts/validate_synthesis.py docs/research/new-doc.md` sees validation errors
in-editor within milliseconds, at the edit boundary. The feedback loop is synchronous — the
human observer can act on the signal before the next keypress. Compare to a cloud CI round-trip
(push → CI trigger → pipeline → notify): intervention latency is several minutes, by which
point the developer has moved on or committed additional dependent changes. Local residency is
what makes the oversight *contemporaneous* with the action requiring oversight.

**Anti-pattern — CI-only feedback for synchronous gates**: Treating CI-only feedback as
adequate oversight for enforcement-critical boundaries. CI has a structural role at T3 (static
linting, cross-repository consistency checks) but cannot substitute for local-synchronous
enforcement at oversight-critical gates, because temporal distance degrades the human's
ability to act on the signal without incurring additional rework or cascading commits.

---

### P3: Axiom Enablement Cascade

**Definition**: LCF does not stand alone as a cost rule — it is the structural foundation that
keeps the enforcement, oversight, and iteration mechanisms of the other four axioms locally
resident and operationally available. Each of the four enabling relationships is a structural
dependency, not merely a co-occurrence.

**Evidence**: Analysis of the four enabling relationships identified in the research framing,
corroborated by structural reasoning from P1 and P2.

**Canonical example** (LCF → Endogenous-First): The Endogenous-First axiom requires that
knowledge, context, and design rationale remain within the system boundary. If an agent fleet's
inference layer is cloud-resident, every prompt and response crosses the system boundary —
including context that encodes internal design decisions, values, and architectural rationale.
Local inference keeps this knowledge endogenous by construction. A fleet that is not LCF
cannot, in practice, be fully Endogenous-First in its cognition; it has outsourced the inference
substrate that converts endogenous knowledge into action.

**Canonical example** (LCF → Algorithms Before Tokens): Pre-commit hooks, validators, and
deterministic scripts are the primary operational expression of the Algorithms Before Tokens
axiom. All run locally. If the local compute substrate is deprioritized, the default path of
"just ask the model" becomes cheaper and more convenient than maintaining local scripts. LCF's
"local first" preference maintains the economic and operational incentive structure that keeps
the Algorithms Before Tokens default viable and preferred.

**Canonical example** (LCF → Minimal Posture): Local sandboxes have no blast radius beyond the
developer's machine. This structural property — a consequence of local residency, not a
procedural rule — enables fast, safe iteration without requiring elaborate rollback procedures.
A cloud-mediated workspace has a blast radius proportional to its network scope and API
permissions. Local residency is what makes Minimal Posture's "carry only required tools,
affect only required scope" achievable without constant procedural overhead.

**Canonical example** (LCF → Documentation-First): `validate_synthesis.py`,
`validate_agent_files.py`, and related validators run locally at zero marginal token cost.
The Documentation-First requirement therefore has a zero-cost enforcement mechanism. If
documentation quality gates required cloud inference, the Programmatic-First principle would
be undermined — every documentation commit would incur token cost, creating structural pressure
to batch-defer or skip the gate. Local validators remove this pressure entirely, making
Documentation-First compatible with high-frequency iteration.

---

### P4: Structural vs. Consequential Framing

**Definition**: The distinction between characterizing local residency as an architectural
property (structural framing) versus a cost optimization (consequential framing). The structural
framing generates correct prioritization decisions in all scenarios — including cost-parity
cases — because it reasons from causes, not effects.

**Evidence**: Ink & Switch, "Local-First Software" (2019) — local is not a cost tier; it is an
architectural residency property with distinct structural guarantees that cannot be substituted
by pricing. Shapiro & Varian, *Information Rules* (1998) — lock-in economics: control distance
from the user increases switching cost and reduces agency, regardless of short-term price parity.

**Canonical example**: An agent fleet adopts LCF purely as a cost rule. A new cloud provider
offers a free-tier inference API. Following the cost framing, fleet designers conclude that
local inference is no longer necessary and migrate. Months later, the provider changes its
terms of service. The fleet's governance mechanisms — pre-commit hooks calling local validators,
oversight loops operating at sub-second latency — now cross an external API boundary at runtime.
Enforcement proximity and oversight residency are lost. The structural framing at the point of
migration would have identified this as a governance-critical decision (does cloud residency
transfer enforcement authority to an external party?), not a pure cost decision.

---

### AP1: Anti-pattern — Cost-First Framing

**Definition**: Treating LCF primarily as a cost optimization leads to systematically incorrect
trade-off decisions when cost parity is achieved, when free-tier cloud is available, or when
the long-run structural governance properties — not short-run per-token price — are the
decisive factor.

**Evidence**: H1 counter-evidence above; Shapiro & Varian lock-in analysis; NIST RMF structural
governance framing.

**Anti-pattern**: "Cloud inference is cheap enough this month, so local doesn't matter." This
reasoning is internally consistent within the cost-optimization frame but systematically wrong
about what matters. The structural governance guarantees of local residency — enforcement
proximity, oversight residency, lock-in resistance, Endogenous-First compatibility — are not
functions of price. They are properties of where the compute lives. A system that makes LCF
trade-offs on price grounds alone will progressively externalize governance infrastructure
while believing it is making rational cost decisions. The externalization accumulates silently
until a provider policy change or API failure makes the governance gap visible.

**Resolution**: Frame LCF first as oversight infrastructure, then note cost as a beneficial
consequence. The correct trade-off logic is: "local residency is preferred *because* of
structural governance properties; cloud is acceptable *when* the structural test passes
(no enforcement authority or oversight access is transferred to an external party), *and*
cost is lower." This ordering generates the same decisions as the cost-first framing in
normal cases but makes the correct decision in governance-critical edge cases.

---

## 4. Recommendations

### R1 — MANIFESTO §3 Amendment: Verdict Y

**Verdict**: **Amendment is warranted** on two grounds: (a) the current framing is causally
incomplete — it characterizes a downstream cost consequence as the upstream rationale, which
generates incorrect decisions in cost-parity scenarios; and (b) the current §3 text does not
equip agents or system designers with the structural reasoning needed to maintain LCF in cases
where the cost argument does not clearly dominate.

**Proposed amendment language** (sentences to add to `MANIFESTO.md §3`, following the existing
"Run locally whenever possible." line):

> Local compute is not merely a cost tier — it is oversight infrastructure. Keeping
> enforcement scripts, validators, and inference co-located with the development substrate
> maintains enforcement proximity (governance mechanisms operate at the point of action),
> enables tight-loop human oversight, and preserves optionality against external-dependency
> lock-in. The cost benefit of local compute is a *consequence* of these structural
> properties, not the reason for them. When choosing between local and cloud execution,
> apply the structural test first: does cloud residency transfer enforcement authority,
> oversight access, or governance guarantees to an external party? If yes, local is
> preferred regardless of cost.

The existing opening lines ("Minimize token burn. Run locally whenever possible.") are
**retained unchanged** — they are accurate and operationally useful; this amendment adds
the structural account that completes them, it does not replace them.

---

### R2 — Resolve the "Intentional No-CI-Gate" Tension with #211 Findings

There is a surface tension between two claims that must be made explicit:

1. `MANIFESTO.md §3` states: "The absence of a CI gate is intentional: cloud-model usage
   detection requires semantic context no static linter can evaluate."
2. The #211 research (`docs/research/lcf-programmatic-enforcement.md`) finds that
   observable-proxy signals *are* statically tractable — model name strings in configuration
   files, API endpoint declarations, and direct cloud-SDK imports (`import openai`,
   `import anthropic`) are detectable by static analysis without semantic inference.

**These claims are not contradictory — they address different enforcement surfaces:**

- The MANIFESTO §3 "intentional" framing applies to *semantic intent enforcement*: detecting
  whether cloud execution was chosen despite a viable local alternative requires understanding
  of context, task suitability, and local-model availability that no static linter can
  evaluate. This claim is correct and remains valid.
- Observable-proxy signals (hardcoded API endpoints, direct cloud-SDK imports, model-name
  strings in config) are statically detectable *regardless of semantic intent*. A WARN-only
  pre-commit gate for these signals (`scripts/check_model_usage.py`) is tractable and
  complementary to the human-judgment gate, not a substitute for it.

**Recommended addition** to the MANIFESTO §3 programmatic gate note (narrowing note):

> The "intentional absence of CI gate" framing applies to *semantic intent enforcement only* —
> determining whether cloud was chosen despite a viable local alternative requires semantic
> context no static linter can evaluate, and the human-judgment gate remains the correct
> tier-1 arbiter for this surface. Observable proxies (hardcoded API endpoint strings, direct
> cloud-SDK imports such as `import openai`) are statically tractable and are candidates for
> a WARN-only tier-0 gate (`scripts/check_model_usage.py`). These are different enforcement
> surfaces; conflating them mischaracterizes the intentional design as broader than it is.

---

### R3 — Empirical Grounding via Issue #131 (Cognee Baseline)

The enabling-infrastructure framing of LCF rests on the operational assumption that local
models can reliably perform the tasks for which they are invoked. If Issue #131
(Cognee/Local Compute Baseline) establishes that local models systematically under-perform on
key agent task classes, the oversight-infrastructure case requires qualification: an oversight
mechanism that is locally resident but unreliable degrades the governance guarantee to the
degree it must be bypassed in practice.

**Recommendation**: After #131 produces a baseline, revisit P1–P4 to confirm that local model
performance is sufficient to sustain the structural guarantees identified here. Where local
models fail reliably on a specific task class, document that as a named exception with an
explicit governance note qualifying the LCF preference — not a silent cloud substitution that
erodes the axiom without acknowledgment.

---

### R4 — Update Axiom Priority Explanatory Text in §How to Read This Document

The current priority ordering (Endogenous-First → Algorithms Before Tokens → LCF → ...) is
*correctly sequenced* for conflict resolution — when axioms pull in different directions, this
ordering determines which governs. However, the accompanying explanatory prose positions LCF
as a downstream cost fallback, which does not reflect the upstream structural role identified
here.

**Recommendation**: After the MANIFESTO §3 amendment is approved, add a parenthetical or
footnote to the priority-ordering section that distinguishes *priority* (conflict-resolution
sequence) from *structural role* (where in the enabling dependency graph each axiom sits):
"Note that LCF's position at 3 reflects conflict-resolution priority; structurally, LCF
functions as an enabling substrate that keeps the enforcement and oversight mechanisms of
Axioms 1 and 2 locally resident and operationally available."

---

### R5 — Propagate the Axiom Enablement Cascade into the Encoding Inheritance Chain

The four canonical enabling relationships (P3) are not currently documented in agent files,
`AGENTS.md`, or operational guides. Agents operating under LCF today do so with only the cost
framing as guidance; the oversight-infrastructure framing exists only in source material and
the research doc being committed here.

**Recommendation**: After the MANIFESTO §3 amendment is approved, update the `AGENTS.md`
LCF section to include a brief reference to the enabling-infrastructure framing and the four
enabling relationships, with a backlink to this document. This propagates the structural framing
through the encoding inheritance chain (MANIFESTO.md → AGENTS.md → agent files → session
behavior) rather than leaving it visible only in a research doc.

## See Also

- [LCF Programmatic Enforcement](./lcf-programmatic-enforcement.md) — observable-proxy gate design for the Local Compute-First axiom; the enforcement surface this infrastructure is designed to enable
- [Vocabulary Bridge: Encoding Models](./vocabulary-bridge-encoding-models.md) — shared vocabulary bridging the vertical and horizontal encoding models; bridge terms used throughout this document's structural framing

---

## 5. Sources

1. **Boner, P., et al. (Ink & Switch).** "Local-First Software: You Own Your Data, in Spite
   of the Cloud." *Proceedings of the ACM SIGPLAN International Symposium on New Ideas, New
   Paradigms, and Reflections on Programming and Software (SPLASH / Onward!)*, October 2019,
   Athens, Greece. https://www.inkandswitch.com/local-first/

2. **National Institute of Standards and Technology.** *Artificial Intelligence Risk Management
   Framework (AI RMF 1.0).* NIST AI 100-1. Gaithersburg, MD: NIST, January 2023.
   https://doi.org/10.6028/NIST.AI.100-1

3. **European Union.** *Regulation (EU) 2024/1689 of the European Parliament and of the Council
   of 13 June 2024 laying down harmonised rules on artificial intelligence (Artificial
   Intelligence Act).* Official Journal of the European Union, L series, 2024. Articles 9–17
   (risk-management system, data governance, technical documentation, record-keeping, transparency,
   human oversight, and accuracy requirements for high-risk AI systems).

4. **Christiano, P., Shlegeris, B., & Amodei, D.** "Supervising Strong Learners by Amplifying
   Weak Experts." arXiv:1810.08575 [cs.AI], October 2018.
   https://arxiv.org/abs/1810.08575

5. **Shapiro, C., & Varian, H. R.** *Information Rules: A Strategic Guide to the Network
   Economy.* Boston: Harvard Business School Press, 1998.

6. **EndogenAI Workflows.** `MANIFESTO.md §3` — Local-Compute-First. Internal governance
   document. Current text: "Minimize token burn. Run locally whenever possible." Programmatic
   gate note: "The absence of a CI gate is intentional: cloud-model usage detection requires
   semantic context no static linter can evaluate."

7. **EndogenAI Workflows.** `docs/research/lcf-programmatic-enforcement.md` — "LCF
   Programmatic Enforcement: Closing the F4 Gap." Research Issue #211. 2026-03-12. Establishes
   the distinction between semantic-intent enforcement (infeasible statically) and
   observable-proxy enforcement (tractable via WARN-only pre-commit gate).

8. **EndogenAI Workflows.** `docs/research/values-encoding.md` — "Verbally Encoding Values:
   Cross-Sectoral Synthesis." F4 gap origin document. 2026-03-07.

9. **EndogenAI Workflows.** `docs/research/enforcement-tier-mapping.md` — "Programmatic
   Governance Completeness Audit: T0–T5 Enforcement Tier Mapping." Research Issue #174.
   2026-03-10. Establishes the T0–T5 governor taxonomy and identifies LCF as residing in the
   T5 prose-only periphery.

---

*Related issues: #209 (this document), #211 (F4 gap / observable-proxy enforcement surface),
#131 (Cognee / Local Compute Baseline — empirical grounding for local model reliability),
#152 (Fleet Guardrails Audit).*
