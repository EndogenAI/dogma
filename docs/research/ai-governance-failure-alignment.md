---
x-governs: [endogenous-first, algorithms-before-tokens]
title: "AI Governance Failure in High-Stakes Targeting Systems"
status: Final
closes_issue: 570
date_synthesized: 2026-05-01
topics: [governance, military-ai, targeting-systems, endogenous-governance, accountability, algorithms-before-tokens]
sources:
  - theguardian-lavender-gaza-2024
  - theguardian-maven-iran-school-2026
  - minab-school-attack-wikipedia-2026
  - newyorker-project-maven-manson-2026
  - militarytimes-iran-school-strike-2026
  - democracynow-project-maven-interview-2026
  - gatech-us-military-ai-iran-2026
recommendations:
  - id: rec-ai-gov-failure-001
    title: "Governance infrastructure for high-stakes AI must include deterministic enforcement gates that cannot be bypassed under throughput pressure"
    status: accepted
    linked_issue: 570
    decision_ref: ''
  - id: rec-ai-gov-failure-002
    title: "Reject deliberation-as-latency framing at the architectural level"
    status: accepted
    linked_issue: 570
    decision_ref: ''
  - id: rec-ai-gov-failure-003
    title: "Implement external validation substrates for AI decision support systems"
    status: accepted
    linked_issue: 570
    decision_ref: ''
  - id: rec-ai-gov-failure-004
    title: "Research governance infrastructure requirements specifically for high-stakes AI deployment contexts"
    status: accepted
    linked_issue: 570
    decision_ref: ''
  - id: rec-ai-gov-failure-005
    title: "Track escalation arc as governance risk metric across deployment contexts"
    status: accepted
    linked_issue: 570
    decision_ref: ''
---

# AI Governance Failure in High-Stakes Targeting Systems

## Executive Summary

Two documented military deployments of AI targeting systems — Israel's Lavender system in Gaza (2024) and the US Pentagon's Maven Smart System in Iran (2026) — provide the clearest available empirical record of what AI governance failure looks like at scale. In both cases, the failure was not an algorithm malfunction. It was the deliberate architectural removal of the mechanisms that govern AI behavior: human oversight structures were eliminated, validation gates were bypassed, and the systems were optimized for throughput rather than accountability. The result, in both cases, was mass civilian death.

The governance failure pattern is consistent across both cases: AI systems were embedded inside compressed decision pipelines where speed was the primary design objective, where the humans nominally "in the loop" had their judgment stripped out by the architecture itself, and where no external validation mechanism existed to detect when the system's outputs had drifted from ground truth. This is not a failure of AI safety research or alignment theory. It is a failure of governance infrastructure — the absence of the structural substrate that would have enforced constraints even under pressure, even after oversight budgets were cut, even when commanders were demanding more targets faster.

These failures reveal structural requirements for what AI governance infrastructure would need to do: constraints must be architecturally embedded rather than organisationally maintained; validation must be automated and external rather than circular; oversight cannot depend on staffing levels that can be cut. EndogenAI and dogmaMCP represent an early attempt to think about some of these requirements in software development workflow contexts — not a response to military targeting, and not a claim to have answered the governance problem these cases surface. The purpose of this document is to understand the failures clearly enough to reason about what answers would need to provide, not to assert that any answer already exists.

## Hypothesis Validation

**Research question**: What do documented AI governance failures in military targeting systems reveal about the structural requirements for governance infrastructure in high-stakes AI contexts?

**Sources confirmed**:

The seven primary sources surveyed — the Guardian's Lavender investigation (2024), the Guardian/Baker analysis of the Maven/Iran school bombing (2026), the Wikipedia record of the Minab attack, the New Yorker's review of Katrina Manson's *Project Maven* (2026), the Military Times investigation, the Democracy Now interview with Manson, and the Georgia Tech analysis by Jon Lindsay — consistently support the following findings:

1. Both Lavender and Maven operated in contexts where human oversight had been architecturally compressed, not merely constrained by external pressure.
2. The Minab school strike resulted from a failure to validate a database record — not from an algorithm error. The building was classified as a military facility in a Defense Intelligence Agency database that had not been updated since 2016 at the latest, despite the building appearing in Iranian business directories and on Google Maps.
3. The framing of both incidents as "AI problems" systematically displaced the governance questions: who authorized these architectures, who eliminated the oversight structures, and who bears accountability when the enforcement layer is removed.
4. The Georgia Tech analysis independently validates the core finding: "AI systems are only as good as the organizations that use them" — organizational governance structures, not algorithm accuracy, determine outcomes.
5. No external validation substrate existed in either system: both could measure only their own performance, producing what the Guardian/Baker analysis calls "circular reporting" — an accumulation of apparent validations that amplified a single error.

## Pattern Catalog

### Pattern 1: Lavender AI System — Automation as Governance Collapse (Israel/Gaza, 2024)

**Canonical example**: The IDF's Lavender system, developed by Unit 8200, generated a database of 37,000 Palestinian men identified as potential Hamas or PIJ operatives. Officers were authorised to spend 20 seconds per target before approving strikes. One officer described their role: *"I had zero added-value as a human, apart from being a stamp of approval. It saved a lot of time."* Pre-authorised kill ratios permitted the deaths of 15–20 civilians per low-ranking militant. Unguided munitions ("dumb bombs") were used to destroy entire homes and all their occupants. The system was explicitly designed to operate with a nominal human in the loop whose function was throughput maintenance, not oversight. The accuracy rate — claimed at 90% by the unit — produced a system so large that it became, by its own design, impossible to verify: *"You have another 36,000 waiting."*

**Anti-pattern**: **Human-in-the-loop as rubber stamp.** Lavender did not remove humans from the targeting process — it reduced their role to a throughput function with a fixed time budget per decision. The governance guarantee nominally present (human review before each strike) was operationally absent because the architecture made meaningful review impossible. This is the "stamp of approval" anti-pattern: a governance mechanism preserved in name while its substance is engineered away. The result is that accountability without oversight creates a system that is maximally harmful and minimally correctable — errors propagate at the rate of 37,000 targets with no external brake.

**Anti-pattern**: **Collateral damage as a tunable parameter.** Pre-authorising civilian death ratios as a governance mechanism inverts the purpose of governance. Rather than constraining what the system may do, it codifies the maximum harm the system is permitted to cause. The result is that the governance infrastructure becomes a harm-amplification layer: by encoding acceptable collateral damage as a rule, the system removes the friction that would otherwise slow or halt harmful actions.

### Pattern 2: Project Maven / Minab School Attack — Escalation Without Accountability (Iran, 2026)

**Canonical example**: On 28 February 2026, a Tomahawk cruise missile struck Shajareh Tayyebeh primary school in Minab, southern Iran, during the first day of Operation Epic Fury. Between 156 and 180 people were killed, most of them girls aged 7–12. The school had been separated from an adjacent IRGC naval compound between 2013 and 2016. The DIA database used by Maven's targeting pipeline still classified the coordinates as a military facility. The building appeared on Google Maps, in Iranian business listings, and had an active website. Maven processed 1,000 targeting decisions in the first 24 hours of the campaign — approximately one every 3.6 seconds. The Civilian Protection Center of Excellence had been cut by 90% under the Hegseth administration. No human with the time or authority to check the underlying database record was in the pipeline. As Kevin T. Baker reported in the Guardian: *"The target package for the Shajareh Tayyebeh school presented a military facility... A search engine could have found it. Nobody searched. At 1,000 decisions an hour, nobody was going to."*

**Anti-pattern**: **Speed as the primary design objective.** The Scarlet Dragon exercises, which refined Maven over five years, benchmarked targeting throughput against the 2003 Iraq invasion, where 2,000 personnel managed targeting for the entire war. The goal of the exercises was to discover how few people could handle the same volume. By 2024, the stated objective was 1,000 targeting decisions per hour. The governance question — what validation mechanisms must be preserved at any throughput level — was not part of the benchmark. The result is what Baker calls "bureaucracy encoded in software": the procedural columns on the workflow board remained, but the deliberative work those columns formerly contained was systematically removed in the name of latency reduction. *"What Karp eliminated was the discretion the institution could never admit it depended on. What remains is a bureaucracy that can execute its rules but with no one left to interpret them. Bureaucracy encoded in software does not bend. It shatters."*

**Anti-pattern**: **Circular reporting — a system that measures only itself.** Maven's target packages were validated against prior target packages. The DIA database was treated as authoritative because it had always been treated as authoritative. There was no external validation substrate — no check against satellite imagery updated after 2016, no cross-reference against open-source data, no mechanism for ground truth to enter the pipeline. This pattern, which Baker traces back to Operation Igloo White in Vietnam and the Belgrade Chinese embassy strike in 1999, produces systems that are "confidently wrong" — the 2021 USAF targeting AI scored 25% accuracy in real conditions while rating its own confidence at 90% (Military Times). Systems that cannot be corrected from outside cannot be governed.

### Pattern 3: The Escalation Arc — When One Military Normalizes, Others Adopt

**Canonical example**: At the end of *Project Maven*, author Katrina Manson confronts Drew Cukor — the Marine colonel most responsible for building Maven — with the Gaza precedent. She tells him: *"The AI targeting machine makes possible the policy decision, enabling operational speed and volume."* Cukor, who had defended Maven as an intelligence platform rather than a weapon, concedes: *"This is correct."* This exchange documents the escalation arc explicitly: the Lavender system, deployed by the IDF in Gaza with US-supplied technology and doctrine, established the operational template that the Pentagon then applied at scale via Maven in Iran. NATO has its own Maven contract with Palantir; ten member nations have followed. The technology normalizes what each deployment makes permissible.

**Anti-pattern**: **Governance by precedent — letting the prior deployment define the envelope.** Each deployment expands what is considered operationally normal. Lavender established 20 seconds of human review per target. Maven reduced that further. The escalation arc is not a bug in the adoption curve — it is a structural consequence of deploying governance-light systems: once the system is operational and producing results, the pressure to reduce remaining oversight mechanisms grows. The only intervention that interrupts this arc is governance infrastructure that is architecturally immune to efficiency pressure — constraints that cannot be removed by cutting staff, compressing timelines, or reconfiguring workflows.

## What the Failures Reveal About Governance Infrastructure Requirements

The Lavender and Maven failures are, at their core, infrastructure failures. The governance mechanisms that should have constrained these systems were either never built, or were built as advisory overlays that could be overridden, cut, or compressed into irrelevance. Each failure pattern surfaces a structural requirement for what governance infrastructure in high-stakes AI contexts would need to do. The four-substrate model (Policy Docs, Design Docs, Agent Files, Enforcement Scripts) represents an early attempt to address some of these requirements in software development workflow contexts — whether and how it generalises to higher-stakes contexts is an open question.

**Pattern 1 (Lavender's absent constitutional layer) reveals a requirement: governance constraints must be authored, committed, and version-controlled — not encoded as operational preferences that can be overridden.** Lavender had no equivalent to a constitutional document encoding what the system must NOT do, against which runtime decisions could be validated. Maven's rules of engagement were encoded as columns on a workflow board — advisory structure, not enforceable constraint. Governance infrastructure must establish the ethical and operational envelope in a form that cannot be edited away by a budget cut or a commander's instruction. The four-substrate model's Policy Docs layer is an attempt to address this requirement in software development contexts, grounded in [MANIFESTO.md §1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first). Whether a committed document constitutes meaningful governance at these stakes is a question the research does not answer.

**Pattern 2 (Maven's database staleness failure) reveals a requirement: ground truth validation must be automated, external, and run before consequential action — not assumed from prior use.** The DIA database was treated as authoritative because it had always been treated as authoritative. Governance infrastructure must include mechanisms that detect drift between an internal record and external reality, and must halt or escalate when that validation cannot be confirmed. The four-substrate model's Design Docs layer is an attempt to encode validation patterns in software development contexts; the [Endogenous-First axiom (MANIFESTO.md §1)](../../MANIFESTO.md#1-endogenous-first) requires reading what the system already knows before acting. Whether these patterns translate to contexts where the "database" is a targeting record and the "ground truth" is a building occupied by schoolchildren is not answered here.

**Pattern 2 (Maven's role boundary collapse) reveals a requirement: role definitions must encode escalation paths, halt conditions, and governance triggers — not just task scope.** The "stamp of approval" anti-pattern results from a system that defines who does what but omits the conditions under which execution must stop. Governance infrastructure must make human oversight a structural requirement, not an operational preference. The four-substrate model's Agent Files layer encodes escalation and halt conditions in software development workflow contexts. The gap between a role definition file governing a software agent and the governance structures that would be required to halt a targeting pipeline under throughput pressure is large and undocumented.

**Pattern 3 (deliberation-as-latency) reveals a requirement: enforcement gates must be deterministic and architecturally immune to efficiency pressure.** Baker writes that "friction is also where judgment forms" and that Maven's architecture "compressed the time" until "the friction does not disappear — you just stop noticing it." Governance infrastructure must include enforcement mechanisms that execute before consequential action and cannot be removed by cutting staff, compressing timelines, or reconfiguring workflows. The [Algorithms Before Tokens axiom (MANIFESTO.md §2)](../../MANIFESTO.md#2-algorithms-before-tokens) is a software-development encoding of this insight: encode the constraint once as a deterministic algorithm, and it enforces regardless of throughput targets. The four-substrate model's Enforcement Scripts layer is this pattern applied to software development workflow contexts.

The honest conclusion from this mapping is narrow: the four failure patterns surface requirements that governance infrastructure in any context — not only military — would need to address. The four-substrate model is an early attempt to reason about some of these requirements in software development contexts, where the stakes are lower and the reversibility is higher. The cases documented here involve the deaths of hundreds of civilians. The right posture is to let these failures inform how governance infrastructure requirements are framed — including in lower-stakes contexts where there is time to iterate — rather than to treat the current work as having provided an answer. The escalation arc documented in Pattern 3 makes this posture more urgent, not less: the governance approaches normalised in lower-stakes deployments today become the templates for higher-stakes deployments tomorrow.

## Recommendations

1. **Governance infrastructure for high-stakes AI contexts requires deterministic enforcement gates that execute before consequential action and cannot be removed under throughput pressure.** Advisory governance — policies written in documents that agents may ignore, oversight structures that can be cut when budgets shrink — has been empirically demonstrated to fail under pressure. The Maven/Minab failure was not caused by insufficient policy documentation; the DIA database staleness rules existed. It was caused by the absence of automated validation gates that ran before each targeting decision and halted execution when ground truth could not be confirmed. The structural requirement this surfaces: governance enforcement cannot be architecturally bypassed — not by budget cuts, staffing reductions, or throughput targets.

2. **Reject the "deliberation as latency" framing at the architectural level.** Any AI deployment roadmap that frames governance checkpoints as throughput bottlenecks to be optimized away should be treated as a governance-failure precursor. The Maven-pattern kill-chain compression — anywhere a human review step has been reduced to a time-bounded approval click — is the structural mechanism by which governance collapses under pressure. Governance architecture must treat validation friction as a feature, not a bottleneck; any workflow in which oversight budget is a variable to be optimised is a workflow in which the Lavender/Maven failure mode is latent.

3. **Any AI system used to inform consequential decisions must include an external validation substrate that is automated, auditable, and architecturally required.** The circular reporting failure — systems that can only measure their own performance — is the structural precondition for both the Lavender and Maven failures. External validation must be maintained as a documented, automated path that cannot be bypassed by throughput pressure. The pattern this surfaces: internal confidence is not a substitute for external ground truth, and governance infrastructure must enforce the distinction programmatically, not procedurally.

4. **Research governance infrastructure requirements specifically for high-stakes AI deployment contexts.** The failures documented here — human-in-the-loop collapse, database staleness, circular validation, escalation arc — surface requirements that software-development governance thinking can inform but cannot address at the stakes involved. A sustained research agenda on what makes governance enforcement robust when institutional incentives systematically favour throughput over accountability is a prerequisite for principled deployment of AI in high-stakes contexts. Work in software development workflow contexts is a starting point for this reasoning, not a destination.

5. **Track the escalation arc as a governance risk metric across AI deployment contexts.** The normalization pattern documented in Pattern 3 — each deployment expanding the envelope of what is operationally acceptable — is a governance risk that compounds across the ecosystem, not just within a single organization. AI deployment precedents in high-stakes contexts (military, criminal justice, immigration enforcement, medical triage) should be monitored as leading indicators of the governance pressures that downstream adopters will face. The mechanisms that normalise reduced oversight in one context become the templates for the next.

## Sources

1. **Lavender AI system in Gaza** — Yuval Abraham, *The Guardian*, 3 April 2024. "'The machine did it coldly': Israel used AI to identify 37,000 Hamas targets." <https://www.theguardian.com/world/2024/apr/03/israel-gaza-ai-database-hamas-airstrikes>

2. **Maven / Minab school attack analysis** — Kevin T. Baker, *The Guardian*, 26 March 2026. "AI got the blame for the Iran school bombing. The truth is far more worrying." <https://www.theguardian.com/news/2026/mar/26/ai-got-the-blame-for-the-iran-school-bombing-the-truth-is-far-more-worrying>

3. **2026 Minab school attack** — Wikipedia contributors, *Wikipedia*, retrieved May 2026. "2026 Minab school attack." <https://en.wikipedia.org/wiki/2026_Minab_school_attack>

4. **Project Maven — book review** — Gideon Lewis-Kraus, *The New Yorker*, 2026. "How Project Maven Put AI Into the Kill Chain." Review of Katrina Manson, *Project Maven: A Marine Colonel, His Team, and the Dawn of AI Warfare* (Norton, 2026). <https://www.newyorker.com/books/under-review/how-project-maven-put-ai-into-the-kill-chain>

5. **Maven / Iran targeting investigation** — Katie Livingstone, *Military Times*, 24 March 2026. "Deadly Iran school strike casts shadow over Pentagon's AI targeting push." <https://www.militarytimes.com/news/your-military/2026/03/24/deadly-iran-school-strike-casts-shadow-over-pentagons-ai-targeting-push/>

6. **Project Maven interview with Katrina Manson** — *Democracy Now!*, 31 March 2026. "The AI War on Iran: Project Maven, a Secretive Palantir-Run System, Helps Pentagon Pick Bomb Targets." <https://www.democracynow.org/2026/3/31/project_maven_manson_bloomberg_ai_warfare>

7. **US military AI and human judgment** — Jon R. Lindsay (Georgia Institute of Technology), *The Conversation*, republished by Georgia Tech Research, 11 March 2026. "US Military Leans Into AI for Attack on Iran, But the Tech Doesn't Lessen the Need for Human Judgment In War." <https://research.gatech.edu/us-military-leans-ai-attack-iran-tech-doesnt-lessen-need-human-judgment-war>
