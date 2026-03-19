---
title: "LCF Axiom Positioning: Structural Enabler vs. Peer Priority Axiom"
status: "Final"
research_issue: "#245"
date: "2026-03-14"
---

# LCF Axiom Positioning: Structural Enabler vs. Peer Priority Axiom

> **Research question**: Should Local-Compute-First be repositioned as a structural
> enabler/prerequisite rather than a peer axiom ranked #3 below Endogenous-First and
> Algorithms Before Tokens? What are the downstream impacts on `MANIFESTO.md`, `AGENTS.md`,
> agent files, and guides?
> **Date**: 2026-03-14
> **Research Issue**: #245
> **Related**: [`docs/research/lcf-oversight-infrastructure.md`](../infrastructure/lcf-oversight-infrastructure.md)
> (primary source — LCF as oversight infrastructure, R1–R5); [`docs/research/lcf-programmatic-enforcement.md`](../infrastructure/lcf-programmatic-enforcement.md)
> (observable-proxy enforcement design); [`MANIFESTO.md §3`](../../../MANIFESTO.md) — Local
> Compute-First body; [`MANIFESTO.md §How to Read This Document`](../../../MANIFESTO.md) —
> axiom priority ordering; [`AGENTS.md §Guiding Constraints`](../../AGENTS.md)

---

## 1. Executive Summary

`MANIFESTO.md §3` has been materially amended since the original "Minimize token burn" framing:
the body of §3 now explicitly states that LCF is "oversight infrastructure," documents the
axiom-enablement cascade (LCF → Endogenous-First, LCF → Algorithms Before Tokens, LCF →
Minimal Posture, LCF → Documentation-First), and provides the structural test for choosing
between local and cloud execution. The core reframing from `docs/research/lcf-oversight-infrastructure.md`
(Research Issue #209, Status: Final) has been applied to `MANIFESTO.md §3`.

However, a residual tension remains unresolved: the **axiom priority ordering** in
`MANIFESTO.md §How to Read This Document` retains language that positions LCF as a downstream
cost fallback ("choose the least expensive compute option"), while the §3 body characterizes
it as a structural substrate. These two descriptions are not wrong in isolation — the
priority ordering correctly encodes *conflict-resolution sequence*, and the §3 body correctly
encodes *operational characterization*. The tension is in the **explanatory prose** of the
priority-ordering section, which uses "fallback" language that inadvertently imports the old
framing back into the document's most-read orientation section.

This document's central finding: **LCF must not be repositioned to a different rank in the
axiom table** — the 1-2-3 ordering is an accurate and necessary conflict-resolution ladder.
What is required is a **prose clarification** in the priority-ordering section that explicitly
distinguishes *conflict-resolution priority* (why LCF is at position 3) from *structural role*
(why LCF is an enabling substrate for positions 1 and 2). This distinction was recommended in
R4 of `lcf-oversight-infrastructure.md` and has not yet been implemented.

Downstream layer impacts are specific and bounded: two prose additions in `MANIFESTO.md`,
one line addition in `AGENTS.md`, and a guidance update in `docs/guides/local-compute.md`.
No agent file number-citations to "Axiom #3" were found in the current fleet — the numeric
citation risk is theoretical for this codebase, not yet materialized.

---

## 2. Hypothesis Validation

### H1 — The Current Priority Ordering Accurately Represents LCF's Role

**Claim**: The 1→2→3 priority ranking in `MANIFESTO.md §How to Read This Document` correctly
characterizes LCF as a peer axiom that activates last ("when no deterministic solution exists
and inference is required — choose the least expensive compute option").

**Evidence in favour**:

- The conflict-resolution framing IS correct for its stated purpose. There are genuine
  three-way axiom conflicts that the ladder resolves: if an existing endogenous knowledge
  source (EF) requires a cloud API to refresh, and a deterministic local script (ABT) exists
  to compute the same result, but a local model (LCF) would use fewer tokens interactively —
  the priority order correctly governs: ABT (deterministic script) supersedes LCF (local
  model inference). The 1-2-3 ordering generates correct decisions in this class of conflict.
- R4 in `lcf-oversight-infrastructure.md §4` explicitly validates the ordering: "the current
  priority ordering (Endogenous-First → Algorithms Before Tokens → LCF → ...) is *correctly
  sequenced* for conflict resolution." The Final-status research does not recommend changing
  the rank — only the accompanying explanatory prose.

**Evidence against**:

- The priority-ordering explanation at position 3 reads: "3. **Local Compute-First** applies
  when no deterministic solution exists and inference is required — choose the least expensive
  compute option." The phrase "choose the least expensive compute option" reintroduces the
  cost-fallback framing that §3's body has already superseded. A reader who reads only the
  priority-ordering section (the orientation section most commonly skimmed first) encounters
  the old framing, contradicting the structural framing in §3.
- The phrase "applies when no deterministic solution exists" mis-characterizes LCF as
  temporally sequenced — as if LCF only *activates* after Axioms 1 and 2 are exhausted.
  But the axiom-enablement cascade (P3 in `lcf-oversight-infrastructure.md`) demonstrates
  that LCF is *always active* as a substrate property. Endogenous-First knowledge retrieval
  depends on local residency; it does not "use up" LCF. Local compute is operating
  continuously in the background, not sequentially after the others finish.
- The cost-framing fallback is "approximately right in routine agent-task scenarios but
  generates incorrect trade-off decisions precisely in the cases where the structural
  governance properties of LCF are most critical: cost-parity scenarios, free-tier
  migrations" (`lcf-oversight-infrastructure.md §2 H1 verdict`).

**Verdict**: H1 is **confirmed for conflict-resolution sequencing, disconfirmed as a complete
characterization of LCF's operational role**. The priority ordering correctly ranks axioms
1-2-3 for resolving conflicts. It incorrectly implies that LCF is only a cost-fallback that
activates when the others are exhausted — a framing contradicted by the Final-status research
already committed to the repository.

---

### H2 — LCF Requires Repositioning as a Structural Enabler / Prerequisite

**Claim**: LCF should be repositioned in `MANIFESTO.md` to reflect its structural-enabler
character — either by changing its rank, creating a separate "Structural Layer" outside the
priority table, or by restructuring the axiom hierarchy.

**Evidence in favour**:

- The enabling-infrastructure framing in `lcf-oversight-infrastructure.md §2 H2` is
  well-supported: "LCF is the structural foundation that keeps the enforcement, oversight,
  and tight-iteration mechanisms — which are the *operational expression* of the other axioms
  — locally resident and structurally available." Structural foundations typically precede
  what they support in architectural documentation — a `MANIFESTO.md` that puts the
  structural prerequisite at position #3 inverts the dependency order for documentation
  readers.
- `MANIFESTO.md §3` body already contains: "LCF is the structural foundation that keeps the
  operational expressions of all other axioms — Endogenous-First knowledge retrieval,
  Algorithms Before Tokens enforcement gates, Minimal Posture sandboxing, and
  Documentation-First quality validators — locally resident and available." This claim is
  structurally stronger than "is one of three peer axioms ranked third."
- The EU AI Act and NIST RMF evidence (in `lcf-oversight-infrastructure.md §2 H2`) positions
  governance-residency as a structural prerequisite — not a choice tier — for trustworthy AI
  systems. A "Structural Layer" framing would make this distinction explicit to readers
  approaching the MANIFESTO as a governance document.

**Evidence against**:

- R4 in `lcf-oversight-infrastructure.md §4` explicitly recommends *not* changing the rank
  or creating a separate structural layer — instead recommending "a parenthetical or footnote
  to the priority-ordering section." The research that is the primary source for this question
  stops short of recommending a structural-hierarchy change. The recommended change is
  explanatory, not architectural.
- A separate "Structural Layer" in MANIFESTO.md would break the current `How to Read This
  Document` conflict-resolution algorithm, which relies on axiomatic ordering to resolve
  cases where EF, ABT, and LCF appear to conflict. If LCF exits the numbered table, no
  conflict-resolution rule governs the three-way scenario.
- MANIFESTO.md is explicitly described as a "constitution" (`§How to Read This Document`):
  "This document is a **constitution**, not a guidebook." Constitutional amendments must be
  minimal and precise — renumbering axioms or introducing structural layers risks cascading
  downstream invalidation of the encoding inheritance chain (MANIFESTO → AGENTS.md → agent
  files → SKILL.md files).
- No other guiding principle currently in the codebase — including Enforcement-Proximity,
  Minimal Posture, or Documentation-First — has been framed with sufficient evidence to
  occupy a co-equal "Structural Layer" position. Adding a structural tier for LCF alone
  creates a singleton category that may not compose well as the project evolves.

**Verdict**: H2 is **disconfirmed as a proposition about structural repositioning, partially
confirmed as a proposition about explanatory framing**. The rank should remain 3. No separate
"Structural Layer" outside the priority table is warranted at this time. What is warranted is
a prose clarification that distinguishes conflict-resolution rank from structural role, exactly
as R4 recommended. The substance of the repositioning argument is correct; the mechanism
should be explanatory prose, not architectural restructuring.

---

## 3. Pattern Catalog

### P1: Priority-Rank vs. Structural-Role Distinction

**Definition**: Axiom priority rank is a *conflict-resolution tie-breaker*: when two or more
axioms appear to pull in different directions, the higher-ranked axiom governs. Structural role
is an *architectural dependency description*: it characterizes which axioms depend on which
others to function correctly. These are orthogonal properties — an axiom can rank third in
conflict resolution while simultaneously being a structural prerequisite for the higher-ranked
axioms.

**Evidence**: The enabling-infrastructure analysis in `lcf-oversight-infrastructure.md §3 P3`
demonstrates the orthogonality concretely: Endogenous-First requires local compute as its
inference substrate ("A fleet that is not LCF cannot, in practice, be fully Endogenous-First
in its cognition; it has outsourced the inference substrate that converts endogenous knowledge
into action"). Yet in a specific conflict, EF overrides LCF — both claims are true
simultaneously because they describe *different properties* (what governs when axioms conflict
vs. what depends on what architecturally).

**Canonical example — correct applying the distinction**:
> "Should we re-fetch a cached source using a cloud API (lower latency) or use the local cache
> (higher trust, no network dependency)? Answer: Endogenous-First governs — use the local
> cache. Rationale: EF outranks LCF in the conflict-resolution ordering. This decision does
> not mean LCF is unimportant; local inference continues to operate in the background tracking
> every other aspect of the session."

**Anti-pattern — conflating the two**:
> "LCF is ranked #3, so we can ignore it until Axioms 1 and 2 have both been satisfied." This
> misreads priority rank as temporal activation. LCF operates continuously; the rank only
> governs when a conflict is being adjudicated. A developer who ignores LCF until "needing to
> choose an inference option" has already violated the axiom's structural requirements.

---

### P2: Why the Current Explanatory Prose Generates the Fallback Misreading

**Definition**: The priority-ordering explanation at position 3 uses the phrase "applies when
no deterministic solution exists and inference is required," implying a temporal sequence.
The misreading this generates is documented: LCF = "fallback of last resort after Axioms 1
and 2 are satisfied."

**Evidence**: The phrase structure "Axiom A supersedes Axiom B" (used for positions 1 and 2)
correctly implies a *comparative* relationship between axioms when they conflict. Position 3's
phrasing shifts to a *conditional* structure ("applies when..."), which implies activation
conditions rather than conflict resolution. This is the source of the fallback misreading —
the grammar of position 3 is categorically different from positions 1 and 2.

**Anti-pattern**: Retaining the position-3 explanatory text unchanged while the §3 body
asserts the opposite characterization. A document that says "structural foundation" in §3 and
"applies when" in the orientation section is internally inconsistent. The orientation section
is read first and will dominate the reader's framing.

**Canonical example — proposed replacement prose** (implementing R4 from `lcf-oversight-infrastructure.md §4`):
> "3. **Local Compute-First** governs compute residency decisions: prefer local execution
> for all enforcement, validation, and inference operations. *Note: position 3 reflects
> conflict-resolution priority — when EF, ABT, and LCF appear to conflict, EF and ABT
> dominate. Structurally, however, LCF functions as an enabling substrate that keeps the
> enforcement and oversight mechanisms of Axioms 1 and 2 locally resident and operationally
> available. LCF is always active as a substrate property — not a fallback activated after
> the first two axioms are exhausted.*"

---

### P3: Structural-Prerequisite Survey — Are Other Axioms/Principles also Structural?

**Research question**: Does LCF uniquely warrant the structural-prerequisite characterization,
or are other principles equally structural — which would justify a "Structural Layer"?

**Survey findings**:

| Principle / Axiom | Structural Character | Notes |
|---|---|---|
| **Local Compute-First** | Yes — enabling substrate for all four other axioms' operational expression | Documented in `lcf-oversight-infrastructure.md §3 P3` |
| **Enforcement-Proximity** (AGENTS.md guiding principle) | Yes — structural residency requirement for governance mechanisms | Already framed structurally in AGENTS.md; corollary to LCF |
| **Endogenous-First** | Partially — defines *what* the system reads; depends on LCF for the substrate | Logical prerequisite for knowledge retrieval but not an infrastructure layer |
| **Algorithms Before Tokens** | Operational, not structural — describes a decision preference within a session | Depends on LCF-resident scripts to execute, but is not itself infrastructure |
| **Minimal Posture** | Partially — scopes agent capabilities; overlaps with LCF's blast-radius reduction | Procedural rather than structural in the infrastructure sense |
| **Documentation-First** | Operational — requires documentation per change; validators enforce it | Depends on LCF-resident validators; is not itself infrastructure |

**Verdict**: LCF and Enforcement-Proximity are the only two candidates with strong
structural-prerequisite character. Enforcement-Proximity is already a named guiding principle
in AGENTS.md — not a core axiom — and its structural character is already documented there.
The survey finds **no basis for a multi-member "Structural Layer"** at the MANIFESTO level.
A structural tier with a single member (LCF) is better addressed as explanatory prose in
the existing priority-ordering section rather than a new architectural category. If
Enforcement-Proximity is later elevated to MANIFESTO status, revisiting a "Structural Layer"
framing would be warranted.

---

### P4: Downstream Layer Impact Analysis

**If the R4 prose clarification is implemented** (recommended path):

| Layer | Required Change | Scope |
|---|---|---|
| `MANIFESTO.md §How to Read This Document` | Replace position-3 explanatory text with P2 canonical example above | ~4 lines |
| `AGENTS.md §Guiding Constraints` | Add "LCF operates as structural oversight infrastructure (see `MANIFESTO.md §3`)" after "minimize token usage; run locally whenever possible" | ~1 line |
| `AGENTS.md` axiom amplification table | Add "(structural enabler)" qualifier to the `local / inference / model / cost` row expression hint | ~1 clause |
| `docs/guides/local-compute.md` | Add a cross-reference to the structural framing from `lcf-oversight-infrastructure.md §2 H2` | ~1 paragraph |
| Agent files citing "Axiom #3" | No current violations found; monitor in `validate_agent_files.py` | 0 immediate changes |

**If full structural-layer repositioning is implemented** (not recommended):

| Layer | Required Change | Risk |
|---|---|---|
| `MANIFESTO.md` | New "Structural Layers" section; remove LCF from numbered table | Medium — breaks existing conflict-resolution references |
| `AGENTS.md` | Rewrite guiding constraints section | High — encoding inheritance chain disruption |
| All `.agent.md` files | Search-and-replace "axiom priority" references | High — 36 agent files to audit |
| `SKILL.md` files | Update all LCF citations | Medium |
| CI validators | Update `validate_agent_files.py` to recognize new structural-layer section | Medium |

---

## 4. Recommendations

### R1 — Implement the R4 Prose Clarification in MANIFESTO.md (Not This Document)

**Recommendation**: In a future implementation issue (not this research phase), update
`MANIFESTO.md §How to Read This Document`, position-3 explanatory text to:

1. Replace "applies when no deterministic solution exists and inference is required — choose
   the least expensive compute option" with language that preserves the conflict-resolution
   purpose while adding the structural-role note.
2. The exact text is specified in P2 above (Canonical example — proposed replacement prose).

**Rationale**: The structural framing is already correct in MANIFESTO §3 body. The only
inconsistency is the priority-ordering prose. A targeted prose fix is the minimal, reversible
change that resolves the inconsistency. The Endogenic Development principle requires minimal
constitutional amendments — the proposed text is additive, not a restructuring.

**Scope constraint**: This research document recommends the change; it does not make it.
Per the brief: "Do NOT modify MANIFESTO.md... — research only; no implementation edits."
File the recommendation as an implementation issue; do not implement inline with this research
commit.

---

### R2 — Add One Line to AGENTS.md §Guiding Constraints for LCF (Not This Document)

**Recommendation**: In the same implementation issue, add a one-line structural framing note
immediately after the current AGENTS.md line: "**Local Compute-First** — minimize token
usage; run locally whenever possible."

Proposed addition: "LCF is structural oversight infrastructure: it keeps enforcement scripts,
validators, and inference locally resident, enabling the other axioms to function as designed.
See [MANIFESTO.md §3](../../../MANIFESTO.md#3-local-compute-first) and
[`lcf-oversight-infrastructure.md`](../infrastructure/lcf-oversight-infrastructure.md)."

**Rationale**: The AGENTS.md axiom amplification table entry for `local / inference / model / cost`
is currently correct but omits the structural framing. Agents reading AGENTS.md first
(as required by Endogenous-First) would encounter only the cost-framing summary. One line
closes this encoding gap within the inheritance chain (MANIFESTO → AGENTS.md).

---

### R3 — Do Not Reposition LCF in the Axiom Table

**Recommendation**: Retain the 1-2-3 conflict-resolution ordering without structural change.
Do not create a "Structural Layer." Do not change LCF's rank to #1 or #0.

**Rationale**: The axiom conflict-resolution ladder works correctly as a three-way sequenced
tie-breaker. Repositioning LCF to rank #1 would break the EF-supersedes-all guarantee for
knowledge-source decisions. Moving it to a separate layer outside the table breaks the
conflict-resolution algorithm. The problem is not the ordering; it is the description
of what the ordering means.

The `lcf-oversight-infrastructure.md §4 R4` — a Final-status document with four independent
evidence streams — does not recommend a rank change. This research document concurs.

---

### R4 — No "Structural Layer" Category at This Time

**Recommendation**: Do not introduce a "Structural Layer" framing in MANIFESTO.md.

**Rationale**: P3 survey above finds only two structural-prerequisite candidates (LCF and
Enforcement-Proximity). LCF already occupies an axiom slot; Enforcement-Proximity occupies
a guiding-principle slot in AGENTS.md. One-member structural tiers do not compose well and
create an architectural expectation of a second member that does not yet exist. The
structural character of LCF is better expressed through explanatory prose in the existing
framework than by introducing a new document-level category.

*Revisit condition*: If a future research sprint identifies a third or fourth principle with
genuine structural-prerequisite character, re-open this question. Until then, prose clarification
is the correct lever.

---

### R5 — Monitor for Numeric "Axiom #3" Citations in Agent Fleet

**Recommendation**: Add a validator check in `validate_agent_files.py` for the string literal
"Axiom #3" or "Axiom 3 " in `.agent.md` files. Numeric citations to LCF by rank create
implicit coupling to the priority-ordering position — if the explanatory prose is amended,
numeric citations will also propagate the original fallback framing.

The current fleet (36 agents) was audited and no numeric LCF citations were found. This is a
preventive recommendation for ongoing fleet growth.

---

## 5. Sources

1. **EndogenAI Workflows.** `MANIFESTO.md §3` — Local Compute-First. Current body text
   includes the R1 amendment from `lcf-oversight-infrastructure.md`: "Local compute is not
   merely a cost tier — it is oversight infrastructure." Axiom priority ordering still retains
   "choose the least expensive compute option" — the residual tension this document addresses.

2. **EndogenAI Workflows.** `MANIFESTO.md §How to Read This Document` — Axiom priority order:
   "3. **Local Compute-First** applies when no deterministic solution exists and inference is
   required — choose the least expensive compute option." Primary source for the residual
   cost-fallback framing identified in H1 counter-evidence.

3. **EndogenAI Workflows.** `docs/research/lcf-oversight-infrastructure.md` — "LCF as
   Oversight Infrastructure: Reframing Local-Compute-First as Structural Enabler." Research
   Issue #209, Status: Final, 2026-03-12. Primary endogenous source. R4 (§4) directly
   recommends the prose clarification this document formalizes. P3 (§3) establishes the
   axiom-enablement cascade. H2 verdict confirms structural-enabler characterization.

4. **EndogenAI Workflows.** `docs/research/lcf-programmatic-enforcement.md` — "LCF
   Programmatic Enforcement: Closing the F4 Gap." Research Issue #211, Status: Final,
   2026-03-12. Companion analysis establishing the observable-proxy enforcement surface;
   provides the enforcement-surface distinction that informs P2 and R1's scope constraint.

5. **EndogenAI Workflows.** `AGENTS.md §Guiding Constraints` — Current axiom amplification
   table entry: `local / inference / model / cost | **Local Compute-First** | Prefer local
   model invocation; document when external API is required.` The baseline from which R2
   proposes a one-line addition.

6. **Boner, P., et al. (Ink & Switch).** "Local-First Software: You Own Your Data, in Spite
   of the Cloud." *Proceedings of the ACM SIGPLAN Onward!*, 2019. Structural vs. cost-tier
   framing of local residency — key evidence for H2 and the P4 impact table.

7. **National Institute of Standards and Technology.** *AI Risk Management Framework (AI
   RMF 1.0).* NIST AI 100-1. January 2023. Governance-residency as a structural prerequisite
   for trustworthy AI "Govern" function — evidence base for the enabling-infrastructure claim
   in `lcf-oversight-infrastructure.md §2 H2`.

---

*Related issues: #245 (this document), #209 (lcf-oversight-infrastructure.md — primary
source, Status: Final), #211 (lcf-programmatic-enforcement.md — companion, Status: Final),
implementation of R1–R4 recommendations tracked as a separate issue.*
