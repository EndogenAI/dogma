---
title: "H4 Novelty External Peer Review: Evidence Synthesis and Reviewer Solicitation Framework"
status: Final
research_issue: "172"
closes_issue: "172"
date: "2026-03-10"
---

# H4 Novelty External Peer Review: Evidence Synthesis and Reviewer Solicitation Framework

> **Research question**: What constitutes valid peer review evidence for H4 ("the four-hypothesis
> system is learnable and operable by teams unfamiliar with first principles"), and what
> structured framework enables an external reviewer to evaluate this claim without prior project
> context?
> **Date**: 2026-03-10
> **Closes**: #172

---

## 1. Executive Summary

H4 — "the four-hypothesis system is learnable and operable by teams unfamiliar with first
principles" — currently holds a **PARTIALLY SUPPORTED** verdict based on internal proxy
evidence from Phase 1b (`external-team-case-study.md`). The internal record is substantive:
100% post-protocol session-start compliance (M2), 100% workplan phase-gate adoption (M4),
1,066-word CONTRIBUTING.md complexity score (M1) within the learnable range, and a T3/T4
enforcement stack that reduces learnability burden programmatically. However, none of these
proxies substitute for external team cold-start evidence.

This synthesis serves two purposes: (1) it formally defines the evidentiary criteria for
valid H4 peer review — what a reviewer must assess, what counts as confirming evidence, and
what counts as disconfirming — and (2) it provides a structured reviewer solicitation
framework consisting of five questions an external reviewer can answer without prior project
context, with explicit evaluation criteria for each response.

**Key finding**: The three most critical H4 evidence gaps are (a) absence of a controlled
external cold-start onboarding observation, (b) no ARM-equivalent measurement from an external
team's first sprint, and (c) no token-burn A/B comparison (H1's open empirical gap). The
reviewer solicitation framework addresses (a) directly; it establishes the measurement
infrastructure for (b); and it sets a precondition for designing (c). External validation
is not merely an academic nicety — it is the required closure step for a hypothesis that
claims *inter-team* replicability, which internal data structurally cannot provide.

**Governing axiom**: `MANIFESTO.md §1. Endogenous-First` — this synthesis reads `external-team-case-study.md`, `enforcement-tier-mapping.md`, `fleet-emergence-operationalization.md`, `AGENTS.md`, and `MANIFESTO.md` as its primary inputs; no external sources are invoked.

---

## 2. Hypothesis Validation

### H4 — the four-hypothesis system is learnable and operable by teams unfamiliar with first principles

**Current verdict: PARTIALLY SUPPORTED**
**Confidence qualifier**: Internal proxies only; external validation is the outstanding gap.

---

### 2.1 Defining Valid H4 Peer Review Evidence

Before cataloging existing evidence, we must define what *counts* as evidence capable of
confirming or disconfirming H4. Three evidentiary categories are required:

**Category A — Learnability signals**

A learnability signal is an observable behavior demonstrating that a practitioner with no
prior exposure to the methodology's theoretical foundations can follow its documented protocols
correctly from written guidance alone. Learnability is not about understanding the theory;
it is about following the template. This frames the measurement correctly: H4 is not claiming
practitioners will internalize `MANIFESTO.md §H1–H3` — it is claiming they can operate the
system from documented protocols.

Confirming evidence: A practitioner completes the session-start encoding checkpoint correctly
on their first session, using only `docs/guides/session-management.md` as input.
Disconfirming evidence: A practitioner fails to produce a valid encoding checkpoint sentence
after reading the protocol documentation; or requires iteration and clarification before
producing a valid output.

**Category B — Operability under no-prior-context**

Operability evidence demonstrates that a team can execute the methodology's core workflows
without requiring explanation from a methodology expert. This is the "unfamiliar with first
principles" constraint stated in H4. The distinction from Category A: operability includes
multi-step workflows (workplan creation, phase-gate execution, session closure) rather than
single protocols.

Confirming evidence: A team completes a full sprint (workplan → phase execution → session
summary) using only the repository documentation, with gate adoption ≥ 80% on first attempt.
Disconfirming evidence: A team requires more than one methodology-expert consultation per
sprint; or workplan gate adoption falls below 50%.

**Category C — Onboarding success rate**

Onboarding success combines learnability and operability: what fraction of practitioners reach
a point of independent operation — defined as completing a full sprint without consultation —
within a specified number of guided sessions? The internal proxy (M2 = 100% post-protocol)
suggests this fraction is high, but it measures intra-team, not cold-start, adoption.

Confirming evidence: ≥ 2 of 3 external practitioners reach independent operation (no expert
consultation) by sprint 2.
Disconfirming evidence: ≥ 2 of 3 external practitioners still require consultation at sprint 3
or beyond.

---

### 2.2 Existing Evidence from Phase 1a/1b Mapped Against H4 Criteria

| H4 Criterion | Existing Evidence | Source | Strength |
|---|---|---|---|
| A — Learnability | M2 = 100% post-protocol: 20/20 sessions compliant after one guide commit | external-team-case-study.md §H4 | Strong proxy (intra-team) |
| A — Learnability | Protocol template is one declarative sentence: "Governing axiom: X — primary endogenous source: Y" | docs/guides/session-management.md | Supporting (template simplicity) |
| A — Learnability | 0 pre-commit rejections post-T3 activation: no learning curve for enforced constraints | enforcement-tier-mapping.md §H2 | Strong proxy (toolchain path) |
| B — Operability | M4 = 33/33 = 100%: all workplans contain phase gates; pattern propagated from single exemplar | external-team-case-study.md §Proxy 3 | Strong proxy (intra-team) |
| B — Operability | T3/T4 governor stack enforces 8 constraints at commit boundary; operability independent of deep doc-reading | enforcement-tier-mapping.md §Summary | Structural (toolchain) |
| B — Operability | ARM=5 achieved in two independent sprint events (VEF sprint, Phase 3) | fleet-emergence-operationalization.md §Case studies | Strong proxy (intra-team) |
| C — Onboarding success | CONTRIBUTING.md M1 = 1,066 words: within learnable range; "fewer than 10 lines" for toolchain quickstart | external-team-case-study.md §Proxy 1 | Weak (complexity estimate) |
| C — Onboarding success | Adoption was immediate with zero failed attempts post-protocol | external-team-case-study.md §H4 | Strong proxy (intra-team) |
| C — Onboarding success | No evidence of cold-start adoption by external team | — | Gap (disconfirming by absence) |

**Summary judgment**: Evidence for Categories A and B is strong within the internal team context.
Evidence for Category C (onboarding success rate for external teams) does not exist. H4 cannot
advance beyond PARTIALLY SUPPORTED without Category C evidence.

---

### 2.3 H4 Evidence Gaps

**Gap 1 — No external cold-start onboarding observation (Category C)**

The most critical gap. All M2 compliance data comes from agents operating within an established
session history. No record exists of a practitioner outside the project reading `CONTRIBUTING.md`
for the first time, running `uv run pre-commit install`, and completing a session. This is
required to separate "the methodology is adoptable by practitioners who live in the codebase"
from "the methodology is adoptable by a fresh external team."
*What is needed*: One structured cold-start session with a practitioner unfamiliar with the
project, measuring time-to-first-workplan, M2 compliance on session 1, and number of expert
consultations.

**Gap 2 — No ARM-equivalent measurement from external team adoption context**

The ARM = 5 emergence events both occurred within the EndogenAI team. ARM > 0 is the signal
that methodology adoption has moved from rule-following to co-authorship (internalization).
Without an ARM measurement from an external team's first sprint, we cannot claim H4 at the
internalization level — only at the template-following level.
*What is needed*: After an external team completes their first sprint, count whether they made
any edits to their own AGENTS.md, agent files, or workplan templates based on session
observations. Even ARM = 1 from an external team confirms the back-propagation path is
accessible to teams unfamiliar with first principles.

**Gap 3 — No token-burn A/B comparison (H1's empirical gap, directly relevant to H4)**

H1's core claim — that encode-before-act reduces token burn vs. prompt-only approaches — is
unvalidated. External reviewers evaluating H4 will ask how much burden the session-start
reading ritual places on practitioners. Without an A/B comparison (same task, with vs. without
encoding checkpoint), we cannot answer "is the ritual worth the overhead?" for an external
audience. This gap feeds directly into H4 Category A evidence: the protocol must be learnable
*and* worth learning.
*What is needed*: A pre-registered minimal study — identical agentic task, same model, with
vs. without the encoding checkpoint — measuring task completion coherence and token cost. This
is the same R5 recommendation from `external-team-case-study.md §4`.

**Gap 4 — No formal violation-rate measurement for pre-commit install path**

The T3/T4 governor argument (operability independent of deep documentation) assumes external
teams will run `uv run pre-commit install`. There is no record of whether external adopters
follow this step. If they skip it, the T5 prose-only constraints remain unenforced, and
operability degrades.
*What is needed*: Structured onboarding protocol that captures whether the first action after
cloning the repository is `uv sync && uv run pre-commit install`, and what the violation rate
is for T5 constraints before and after that step.

---

## 3. Pattern Catalog

### Pattern R1 — Template-Sufficiency as H4 Proxy

The single most predictive H4 learnability indicator is template simplicity. `MANIFESTO.md
§1. Endogenous-First` encodes the principle: scaffold from existing system knowledge. When the
protocol is expressed as a fill-in-the-blank template, intra-team adoption is immediate and
universal. This pattern generalizes: for external teams, providing templates before theory is
the adoption accelerant.

**Canonical example**: The session-start encoding checkpoint — "Governing axiom: [axiom name]
— primary endogenous source: [source name]" — was adopted with 100% compliance across 20
sessions after a single commit. The template required no theoretical understanding of why
Endogenous-First matters; it required only the recognition that the first sentence of
`## Session Start` follows a fill-in pattern. Template-sufficiency means H4's learnability
claim does not depend on educating practitioners about H1–H3 theory. It depends on providing
copy-pasteable patterns.

**Anti-pattern**: Onboarding documentation that explains the theory of programmatic governance
before providing the pre-commit install command. An external practitioner reading
`enforcement-tier-mapping.md` before `CONTRIBUTING.md §Quick Start` is encountering theory
before template, which reverses the adoption accelerant. The correct order is: template first
(run this, copy that), theory after (here is why it works this way).

### Pattern R2 — Programmatic Enforcement as Learnability Multiplier

The T3/T4 enforcement stack (`enforcement-tier-mapping.md §Summary`) produces a counter-intuitive
H4 implication: the more constraints that are programmatically enforced, the *less* the
learnability burden on external teams. Each governor that enforces a constraint at
the commit or runtime boundary removes that constraint from the set of things an external
practitioner needs to remember. `MANIFESTO.md §2. Algorithms Before Tokens` states this
directly: prefer deterministic encoded solutions over interactive token burn. Applied to
onboarding, it means: prefer T3-enforced constraints over MUST statements in prose.

**Canonical example**: A new team member who has run `uv run pre-commit install` has 8
constraints enforced automatically — including `no-heredoc-writes`, `no-terminal-file-io-redirect`,
ruff format/lint, synthesis validation, and agent-file compliance. They can violate none of
these without a CI or pre-commit failure, regardless of whether they have read AGENTS.md.
The T3 stack is the minimum viable H4 enforcement layer.

**Anti-pattern**: Sending an external team a link to AGENTS.md without the `CONTRIBUTING.md`
quickstart and `uv run pre-commit install` first. The 37 T5 prose-only constraints become
entirely reliant on the external team's reading comprehension and context-pressure resilience.
Under context pressure (the conditions most demanding for H4), T5 constraints are the first
to drift — exactly the conditions where new teams are most likely to be operating.

### Pattern R3 — Reviewer-as-Evidence-Instrument

The reviewer solicitation framework (§Reviewer Framework below) is itself an H4 evidence
collection instrument. Each question is designed not just to elicit a subjective assessment
but to generate an observable event — a workplan file, a pre-commit hook intercept, a session
scratchpad — that can be measured against the H4 criteria. The reviewer observation is
Category C evidence: a cold-start practitioner following the questions is the onboarding
observation the internal record lacks.

**Canonical example**: Question Q3 in the framework below asks the reviewer to create a
workplan using the exemplar format. The workplan file they create is directly measurable:
does it contain phase rows with gate deliverables? Is the gate structure present? This is M4
applied to an external practitioner in real time.

**Anti-pattern**: Open-ended peer review questions like "does this methodology seem learnable
to you?" produce subjective assessments that cannot be triangulated across reviewers. The
reviewer framework must produce observable artifacts, not impressionistic opinions; otherwise
it generates Commentary, not Evidence.

---

## 4. Reviewer Solicitation Framework

The five questions below are designed for an external reviewer with no prior exposure to the
EndogenAI Methodology. Each question includes: the H4 criterion it addresses, the setup
instructions (what to read before answering), the observable artifact or action required, and
the evaluation criteria for the response.

---

**Q1 — Learnability: Encoding Checkpoint Protocol (Category A)**

*Setup*: Read only `docs/guides/session-management.md §Session-Start Encoding Checkpoint`
(approximately 400 words). No other documentation required.

*Task*: Open a new markdown file and write a `## Session Start` section for an imaginary
session on the branch `feat/example`. Your session is working on a Python scripting task.
Include the encoding checkpoint sentence.

*Evaluation criteria*:
- Pass: Sentence includes both "Governing axiom" label and a source name (any valid source
  from the codebase). No prompt engineering or rephrasing of the protocol is required.
- Partial: Sentence is present but uses wrong label format or omits the source name.
- Fail: No encoding checkpoint sentence; or reviewer reports the protocol is unclear after
  reading the designated section one time.

*H4 criterion*: Category A (learnability signal). A pass here means a zero-prior-exposure
practitioner can follow the core session protocol from a single documentation read.

---

**Q2 — Operability: Pre-commit Governor Intercept (Category B)**

*Setup*: Clone the repository. Do not read AGENTS.md yet. Run `uv sync && uv run pre-commit install`. Create a test Python file and attempt to write this exact line in it:

```
subprocess.run(["bash", "-c", "cat >> output.md << 'EOF'\nsome content\nEOF"])
```

Attempt to commit the file with `git add . && git commit -m "test: heredoc attempt"`.

*Task*: Record: (a) whether the commit was blocked, (b) what error message appeared, and (c)
whether the error message alone (without reading AGENTS.md) was sufficient to understand what
went wrong.

*Evaluation criteria*:
- Pass: Commit was blocked; error message identifies the prohibition and references the
  relevant constraint; reviewer reports the message was actionable without reading AGENTS.md.
- Partial: Commit was blocked but error message required AGENTS.md for interpretation.
- Fail: Commit was not blocked; or reviewer could not identify what caused the failure.

*H4 criterion*: Category B (operability under no-prior-context). A pass confirms that the
T3 enforcement layer protects operability even before the practitioner has read the methodology
documentation.

---

**Q3 — Operability: Workplan Creation from Exemplar (Categories B and C)**

*Setup*: Read only `docs/plans/2026-03-06-agent-fleet-design-patterns.md` as an exemplar
(any single workplan in `docs/plans/` may be used). Do not read AGENTS.md §Agent Communication
yet.

*Task*: Create a `docs/plans/2026-03-10-example-sprint.md` file for an imaginary three-phase
sprint (Phase 1: research, Phase 2: implementation, Phase 3: review). Include a phase table
with at least three columns. Add acceptance criteria at the bottom.

*Evaluation criteria*:
- Pass: Workplan contains a phase table with phase name, deliverables, and gate deliverables
  columns. Gate column is populated. Acceptance criteria checklist is present.
- Partial: Phase table is present but gate row is missing; or checklist is absent.
- Fail: No structured table; or workplan is free-form prose without phase structure.

*H4 criterion*: Categories B and C. Measures both operability (can the practitioner follow the
workplan pattern from one exemplar?) and onboarding cost (how much time was required? Did
reviewing one exemplar file suffice?).

---

**Q4 — Learnability: Back-Propagation Protocol (Category A)**

*Setup*: Complete a minimal sprint using any documented task in the repository (e.g., add a new
test to `tests/`, or write a research document stub in `docs/research/`). Use `CONTRIBUTING.md`
as your only operational guide. After completing the task, read `AGENTS.md §Programmatic-First
Principle §Decision Criteria`.

*Task*: Answer: Did any observation during your sprint suggest that a workflow step you
performed more than once manually should be encoded as a script? If yes, describe the
observation and what you would encode. If no, describe what step came closest to warranting it.

*Evaluation criteria*:
- Pass: Reviewer identifies at least one candidate for encoding and articulates the
  "twice interactively → encode before third" decision criteria correctly.
- Partial: Reviewer identifies a candidate but does not connect it to the programmatic-first
  principle.
- Fail: Reviewer identifies no candidates and reports not understanding the question after
  reading the designated section.

*H4 criterion*: Category A (learnability). Tests whether the Programmatic-First mental model
transfers from a single documentation section, without requiring end-to-end methodology
exposure.

---

**Q5 — Operability: Conflict Resolution Under Layer Ambiguity (Category B)**

*Setup*: Read `docs/research/external-value-architecture.md §Pattern E1` and the `client-values.yml`
schema. Imagine your team has added this entry to `client-values.yml`:

```yaml
session:
  skip_session_start_ritual: true  # we need fast sessions
```

*Task*: Explain what a methodology-compliant agent should do when it reads this entry. Does
it comply? Does it log something? Does it ignore the entry silently? Cite the specific layer
that governs this resolution.

*Evaluation criteria*:
- Pass: Answer identifies the Core Layer as governing (Endogenous-First axiom from MANIFESTO.md
  §1 or conflict_resolution field from client-values.yml schema), states the session-start
  ritual must be honored, and recommends logging the conflict rather than silently ignoring it.
- Partial: Answer identifies that the Core Layer wins but does not specify the logging mechanism
  or the governing axiom.
- Fail: Answer suggests the agent should comply with the client-values.yml entry; or answer
  is ambiguous about which layer wins.

*H4 criterion*: Category B (operability under no-prior-context). Tests whether the layer
conflict-resolution rule is self-evident from a single pattern description, without requiring
knowledge of the full methodology architecture.

---

## 5. Recommendations

### R1 — Conduct Q1–Q5 with ≥2 External Reviewers Before H4 Closure

The reviewer framework is not a proxy substitute — it is the Category C evidence collection
mechanism. Schedule structured solicitation sessions with ≥2 external practitioners. The
pass/partial/fail scores from Q1–Q5 constitute the first exogenous H4 evidence. All three
candidates identified in `external-team-case-study.md §Appendix` are suitable reviewers.

### R2 — Complete Three Priority T5→T3 Uplifts Before Reviewer Engagement

`enforcement-tier-mapping.md §Recommendations` identifies three high-priority T5→T3 remediations:
Conventional Commits commitlint hook, `uv run` pygrep enforcement, and `gh --body` shell guard.
Completing these before scheduled reviewer sessions maximizes the operability score on Q2 and
reduces the T5 maintenance burden reviewers encounter. Each uplift is tractable in a single
session.

### R3 — Add a Pre-Registered H1 Comparison Study as Appendix to H4 Evidence Record

H1's empirical gap (`external-team-case-study.md §R5`) is an open vulnerability in the
four-hypothesis architecture. An external peer reviewer with academic background will identify
it. Design and pre-register a minimal comparison study (see `external-team-case-study.md §R5`
for the protocol) before submitting for formal review. This does not block H4 solicitation —
it is complementary and addresses the H1 question that H4 reviewers will surface.

### R4 — Publish Proxy Metrics M1–M5 as Evaluation Protocol in `docs/guides/`

The five-metric proxy study design from `external-team-case-study.md` is a reusable H4
evaluation template. Committing it to `docs/guides/` as an `evaluation-protocol.md` enables
external reviewers to reproduce the measurement methodology independently, strengthening
inter-reviewer reliability.

### R5 — Track ARM After First External Sprint as Primary H4 Internalization Indicator

ARM > 0 from an external team's first sprint — any edit to their AGENTS.md or agent files
based on session observations — is the earliest measurable H4 internalization signal. Set
this as a tracked metric in the research issue for the post-reviewer-engagement synthesis.

---

## 6. Sources

### Primary Endogenous Sources (read before writing, per MANIFESTO.md §1. Endogenous-First)

1. **`docs/research/external-team-case-study.md`** — Phase 1b output. H4 verdict
   (PARTIALLY SUPPORTED), proxy metrics M1–M4, patterns 1–4, recommendations R1–R5. Primary
   evidence base for this synthesis.

2. **`docs/research/enforcement-tier-mapping.md`** — Phase 1a output. T0–T5 tier distribution,
   37 T5 constraints, 8 T3/T4 governors, three high-priority T5→T3 remediations. Primary source
   for Patterns R2 and the operability argument.

3. **`docs/research/fleet-emergence-operationalization.md`** — Phase 1a output. ARM metric
   formal definition, emergence threshold, two confirmed emergence events. Source for Gap 2
   (ARM-equivalent measurement need).

4. **`MANIFESTO.md §1. Endogenous-First`** — governing axiom for this synthesis;
   template-sufficiency pattern (see §3. Pattern Catalog).

5. **`MANIFESTO.md §2. Algorithms Before Tokens`** — programmatic-enforcement-as-learnability-multiplier
   argument (see Pattern R2); directly invoked in the Q2 framework design.

6. **`AGENTS.md §Agent Fleet Overview and §When to Ask vs. Proceed`** — evidence of
   operability documentation for teams working within the methodology; reference for the
   Programmatic-First decision table (Q4 setup).

7. **`docs/guides/session-management.md`** — session-start encoding checkpoint protocol
   template; primary Q1 evaluation source.

8. **`docs/research/external-value-architecture.md`** — Pattern E1, conflict-resolution rules;
   Q5 setup document.
