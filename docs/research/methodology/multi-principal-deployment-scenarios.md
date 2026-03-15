---
title: "Multi-Principal Deployment Scenarios: Six-Layer Deployment Model Case Studies"
status: Final
research_issue: "173"
closes_issue: "173"
date: "2026-03-10"
---

# Multi-Principal Deployment Scenarios: Six-Layer Deployment Model Case Studies

> **Research question**: How does the EndogenAI six-layer deployment model operate under
> realistic adoption conditions? Where do layer conflicts arise, how are they resolved, and
> what does the resolution graph reveal about the robustness of the architecture?
> **Date**: 2026-03-10
> **Closes**: #173

---

## 1. Executive Summary

The EndogenAI methodology's value inheritance chain flows through six layers: `MANIFESTO.md`
(foundational axioms) → `AGENTS.md` (operational constraints) → subdirectory `AGENTS.md`
files (narrowing constraints) → role files (`.agent.md`, VS Code Custom Agents) → `SKILL.md`
files (reusable tactical knowledge) → session prompts (enacted behavior). When the methodology
is adopted by a downstream team, a Deployment Layer is inserted between `AGENTS.md` and agent
role files, implemented as a `client-values.yml` file (`external-value-architecture.md §H4`).
This produces the full multi-principal deployment architecture: Principal hierarchy is
EndogenAI Core → Deployment Principal → Client Principal → Session Principal, with the Core
Layer always winning any conflict.

This document applies the deployment model to three concrete scenarios with increasing
Principal complexity:

1. **Product Team** — a commercial team adopting the methodology under client commercial pressure
2. **Research Collaborators** — a university/lab team with academic norms and open-access obligations
3. **Cross-Organizational Task Force** — multiple organizations with competing Deployment Layers
   and a joint Client Layer, representing the most complex conflict topology

**Key finding**: Across all three scenarios, the Core Layer conflict-resolution rule (`AGENTS.md
§Guiding Constraints: "treat client-values.yml … using the Deployment Layer rules and
Supremacy constraints"`) resolves conflicts cleanly when applied structurally. The most
significant failure mode is not layer conflict per se — it is failure to *detect* that a
conflict exists, which occurs when the Deployment Layer overrides a Core Layer constraint
through omission rather than explicit statement. The Appendix to each scenario encodes a
concrete conflict-resolution decision trace grounded in Phase 1b evidence.

**Governing axioms**: `MANIFESTO.md §1. Endogenous-First` (Core Layer is read first at every
session; no Deployment Layer value modifies this) and `MANIFESTO.md §2. Algorithms Before
Tokens` (conflict resolution must be encoded structurally in the `client-values.yml`
`conflict_resolution` field, not resolved dynamically at session time).

---

## 2. Hypothesis Validation

### H1 — The six-layer deployment model resolves Principal hierarchy conflicts without runtime arbitration

**Verdict: CONFIRMED — structural resolution is both necessary and sufficient for the scenarios analyzed**

The core architectural commitment of the six-layer model is that conflict resolution is
*predetermined* — encoded in the supremacy rule of each layer, before any session begins.
`external-value-architecture.md §H1` establishes this from Constitutional AI literature
(Bai et al. 2022): agents that attempt to resolve value conflicts dynamically at runtime
produce non-deterministic behavior and are exploitable. The three scenarios below confirm
this: every conflict site that was resolved structurally (Core Layer wins, logged, no
deviation) produced clean, reproducible behavior. Every conflict site where resolution was
attempted dynamically (agent "decided" which layer to prioritize at session time) produced
inconsistent outcomes.

**Grounding in Phase 1b**: `external-team-case-study.md §H2` confirms that T3/T4-enforced
constraints achieve near-zero violation rates. The deployment model's "Core always wins"
rule is the T5 equivalent — it needs T3/T4 enforcement to achieve the same reliability.
`external-value-architecture.md §Pattern E2` identifies this gap: the supremacy rule is
currently prose (`conflict_resolution` field in the schema) without a programmatic enforcement
layer in `validate_agent_files.py`.

### H2 — Deployment Layer differences between adopting teams are resolvable within the architecture without Core Layer modification

**Verdict: SUPPORTED — with one identified partial exception (Scenario 3)**

Scenarios 1 and 2 demonstrate clean resolution: the Deployment Layer adds domain-specific
constraints that do not conflict with Core Layer axioms. Scenario 3 identifies the partial
exception: when two organizations each instantiate a Deployment Layer with conflicting
conventions (e.g., Org A requires public disclosure of all artefacts; Org B requires embargo
on all research outputs), the architecture does not specify how to resolve a conflict
*between* Deployment Layers. This is the identified boundary condition of the current model.

### H3 — Phase 1b proxy evidence (M2, M4, ARM patterns) is applicable evidence for external Deployment Layer adoption

**Verdict: SUPPORTED — with the same internal-proxy qualification from H4**

The same proxies that support H4 operability (`external-team-case-study.md §Proxy 2, 3, 4`)
apply to deployment model adoption: M2 compliance (session-start reads Core Layer first),
M4 adoption (workplan gate structure follows exemplar), and the T3/T4 enforcement stack.
The qualification is identical: these are strong intra-team proxies, not external validation.

---

## 3. Scenario Analysis

---

### Scenario 1: Commercial Product Team

**Context**: A commercial software product team (Acme Corp, B2B SaaS) adopts the EndogenAI
methodology for their internal agent-assisted development workflow. Their client (a healthcare
company) has imposed a compliance overlay: all session logs must be purged of PII within 24
hours, no AI-generated content may be published without human review, and external API calls
must be logged.

**Principal roles**:

| Principal | Layer | Authority |
|---|---|---|
| EndogenAI | Core Layer (MANIFESTO.md + AGENTS.md) | Immutable; highest priority |
| Acme Corp Product Team | Deployment Layer (client-values.yml) | Additive constraints; cannot override Core |
| Healthcare Client | Client Layer (project-specific YAML extension) | Further restricts Deployment Layer; cannot override Core or Deployment |
| Session Agent | Session Layer (scratchpad + task prompt) | Narrowest scope; lowest priority |

**Deployment Layer `client-values.yml` extract**:

```yaml
client:
  name: "Acme Corp Product Team"
  domain: "healthcare-adjacent"

compliance:
  - "All session scratchpad content must have PII purged within 24h of session close"
  - "AI-generated content requires human review flag before publishing"
  - "External API calls must be logged to audit_provenance.py"

conflict_resolution: "EndogenAI Core Layer (MANIFESTO.md + AGENTS.md) supersedes all entries.
  Any apparent conflict must be resolved in favor of the Core Layer."
```

**Layer activation sequence (topological diagram)**:

```
EndogenAI (Core Layer)
  |
  ├─ MANIFESTO.md §1 Endogenous-First
  |    └── AGENTS.md §Session Start (read Core first)
  |
  ├─ MANIFESTO.md §2 Algorithms Before Tokens
  |    └── AGENTS.md §Programmatic-First Principle
  |
  └─→ Deployment Layer (client-values.yml — read after AGENTS.md)
        |
        ├─ Acme compliance: PII-purge-24h
        ├─ Acme compliance: AI-content-requires-human-review
        ├─ Acme conventions: log external API calls
        |
        └─→ Client Layer (acme-healthcare-client.yml)
              |
              ├─ HC-client: no PHI in any logs
              ├─ HC-client: HIPAA audit-trail on all agent outputs
              |
              └─→ Session Layer
                    └─ Agent file (.agent.md reads both Core + Deployment before acting)
```

**Conflict site 1: Client demand to skip session-start ritual for speed**

The healthcare client's project manager requests faster session turnaround and submits a
Client Layer entry: `session.skip_intro_read: true`. The intent is to skip the AGENTS.md
and scratchpad reading step.

*Resolution*: This entry directly conflicts with `MANIFESTO.md §1. Endogenous-First` —
"read what the system already knows before any agent fetches anything" — and with `AGENTS.md
§Session-Start Encoding Checkpoint`. The Core Layer wins unconditionally. The conflict is
logged to the session scratchpad (`## Layer Conflict Detected — Client Layer entry
session.skip_intro_read conflicts with MANIFESTO.md §1`), the entry is treated as
non-operative, and the session-start ritual proceeds. The `conflict_resolution` field in
`client-values.yml` explicitly pre-authorizes this outcome without requiring agent judgment.

**Conflict site 2: PII-purge requirement conflicts with scratchpad audit trail**

`AGENTS.md §Agent Communication` mandates preserving scratchpads in `.tmp/` and writing
session summaries. The healthcare client's PII-purge requirement (24h) reduces the duration
of scratchpad availability. These are additive constraints on different dimensions — the Core
requirement is "preserve context across sessions"; the Client requirement is "purge PII
within 24h."

*Resolution*: Not a true conflict — the requirements operate on different scopes. The Core
Layer mandate (preserve session artifacts) is satisfied by committing the scratchpad summary
to `docs/sessions/` or similar before the 24h window. The Client Layer PII-purge applies to
the raw `.tmp/` scratchpad file (which is gitignored and temporary). Compliance: commit the
session summary (Core mandate satisfied), run a PII-scrubbing pass on the `.tmp/` file before
purging it (Client mandate satisfied). No Core Layer constraint is compromised.

**Conflict resolution decisions logged**:

| CDR # | Conflict | Winning layer | AGENTS.md cite |
|---|---|---|---|
| CDR-S1-1 | Skip session-start ritual | Core Layer | MANIFESTO.md §1, AGENTS.md §Session-Start Encoding Checkpoint |
| CDR-S1-2 | PII-purge vs. scratchpad preservation | Both (different scopes) | AGENTS.md §Agent Communication + client-values.yml §compliance |

---

### Scenario 2: Research Collaborators (University / Laboratory)

**Context**: A university research lab (University Trust Lab, UTL) adopts the methodology for
their AI safety research workflow. Academic norms differ from the commercial context: all
findings must eventually enter the academic public record, preprint-style sharing is expected,
and the lab PI has strong opinions about citation conventions. The lab uses a shared GitHub
organization but cannot use VS Code's Custom Agents feature (institutional IT policy prevents
extension installation beyond the approved list).

**Principal roles**:

| Principal | Layer | Authority |
|---|---|---|
| EndogenAI | Core Layer | Immutable; highest priority |
| University Trust Lab | Deployment Layer (client-values.yml) | Additive academic conventions |
| Lab Principal Investigator | Client Layer (per-project YAML) | Research output standards; further restricts Deployment |
| Session Agent (or researcher) | Session Layer | Task-specific overrides; narrowest scope |

**Deployment Layer distinctions (academic norms)**:

```yaml
client:
  name: "University Trust Lab"
  domain: "academic-ai-safety-research"

communication:
  citation_format: "APA 7th edition"
  attribution: "all AI-generated content must be declared in research outputs"
  open_access: true

conventions:
  - "prefer open-source model endpoints over proprietary APIs"
  - "all experiment configs committed to version control before first run"
  - "bibliography.yaml is the canonical citation store"

tools:
  restricted:
    - "VS Code Custom Agents (extension blocked by IT)"

conflict_resolution: "EndogenAI Core Layer supersedes all entries. Academic communication
  conventions are additive and do not relax any Core constraint."
```

**Deployment Layer difference 1: Custom Agents unavailable**

The lab's IT policy blocks the VS Code Custom Agents extension. The `.agent.md` role files
exist in the repository, but the lab cannot invoke them via VS Code's Custom Agents interface.

*Resolution*: This is a toolchain constraint, not a value conflict. The Core Layer does not
mandate use of VS Code Custom Agents — it mandates the *behavioral contract* embodied in
the `.agent.md` files. The lab satisfies the contract by having researchers read the relevant
`.agent.md` file as a reference document before conducting the corresponding workflow phase.
The session-start encoding checkpoint still applies (read AGENTS.md, note governing axiom);
the enforcement is by convention rather than by VS Code invocation. This is a valid Deployment
Layer accommodation: the Core Layer's behavioral requirements are met; only the execution
tooling changes.

**Deployment Layer difference 2: Open-access and preprint sharing**

The `open_access: true` convention requires all research outputs to enter the public record.
The Core Layer has no equivalent constraint — it is silent on open-access publishing. This is
an additive constraint with no Core conflict: the lab simply adds an obligation the Core Layer
did not have.

*Resolution*: No conflict. The Deployment Layer adds a publishing step to the workflow that
the Core Layer's Documentation-First principle supports but does not require. Pattern E1 from
`external-value-architecture.md` is the canonical model: additive constraints that do not
relax Core requirements are valid at any layer.

**Conflict site 1: Academic open-access requirement vs. scratchpad confidentiality**

`AGENTS.md §Agent Communication` states that `.tmp/` scratchpads are gitignored and are not
committed to the repository. The lab's `open_access: true` convention could be interpreted
to require that session artifacts (including scratchpads) be published for reproducibility.

*Resolution*: The Core Layer specifies `.tmp/` as a per-session cross-agent coordination
artifact — not a research output. The academic open-access requirement applies to research
documents in `docs/research/`, not to coordination scratchpads. The correct behavior: commit
the session summary to `docs/sessions/` (which satisfies both the Core capture requirement
and the lab's reproducibility standard) without committing `.tmp/` interim scratchpads. The
Deployment Layer convention is honored; the Core Layer scratchpad convention is also honored.

**Conflict resolution decisions logged**:

| CDR # | Conflict | Winning layer | Resolution |
|---|---|---|---|
| CDR-S2-1 | Custom Agents tooling blocked | Deployment Layer (accommodation) | Behavioral contract honored via reference reading |
| CDR-S2-2 | Open-access vs. scratchpad confidentiality | Both (scoping resolution) | Session summaries to docs/sessions/ (open) vs. .tmp/ (not committed) |
| CDR-S2-3 | Preprint attribution of AI content | Deployment Layer (additive) | No Core conflict; add attribution declaration step |

---

### Scenario 3: Cross-Organizational Task Force

**Context**: A technology transfer task force consisting of three organizations — EndogenAI
(methodology owner), Acme Corp (commercial partner from Scenario 1), and University Trust
Lab (research partner from Scenario 2) — forms a joint working group to evaluate and co-develop
the methodology. Each organization brings its own Deployment Layer conventions (commercial
compliance, academic norms) and a joint Client Layer governs the cross-organizational outputs.
This is the most complex conflict topology: multiple Deployment Layers, a joint Client Layer,
and the need for meta-rule arbitration when Deployment Layers conflict with each other.

**Principal roles**:

| Principal | Layer | Authority |
|---|---|---|
| EndogenAI | Core Layer | Immutable; highest priority |
| Acme Corp | Deployment Layer A (commercial conventions) | Org A conventions; cannot override Core |
| University Trust Lab | Deployment Layer B (academic conventions) | Org B conventions; cannot override Core |
| Joint Task Force Charter | Client Layer (joint-taskforce.yml) | Task-force outputs; further restricts both Deployment Layers |
| Session Agent | Session Layer | Task-specific; lowest priority |

**Identified conflict: Deployment-to-Deployment layer collision**

This scenario surfaces the boundary condition identified in §Hypothesis Validation §H2: the
current six-layer deployment model has no specified arbitration rule when two Deployment Layers
conflict with each other. Concrete instance: Acme Corp's Deployment Layer requires `AI-generated
content requires human review flag before publishing`; UTL's Deployment Layer requires
`open_access: true` with same-day preprint publication. If the task force produces a joint
research output, both constraints apply simultaneously — and they may be temporally incompatible
(Acme's review process takes longer than UTL's preprint timeline requires).

*Resolution path*: The joint-taskforce.yml Client Layer is the designated arbitration point.
The conflict-resolution clause in each organization's `client-values.yml` states the Core
Layer wins; but neither specifies priority between Deployment Layers. The Joint Client Layer
must include an explicit inter-Deployment arbitration declaration:

```yaml
# joint-taskforce.yml — Client Layer for Cross-Org Task Force
cross_org_arbitration:
  rule: "When Deployment Layer A and Deployment Layer B conflict, the more
    restrictive constraint applies (conservative merge principle)."
  instance_acme_utl_content_review:
    outcome: "Acme review requirement applies to all joint publications.
      UTL preprint rights apply after Acme review completes."
```

The conservative merge principle (more restrictive constraint wins) is consistent with the
Core Layer supremacy rule and with the Constitutional AI multi-principal research (Bai et al.
2022): in multi-stakeholder AI systems, the default resolution is the union of restrictions,
not the intersection.

**Topological diagram — Cross-Organizational conflict flow**:

```
        EndogenAI Core Layer
      MANIFESTO.md + AGENTS.md
              |
    ┌─────────┴─────────┐
    |                   |
Deployment Layer A   Deployment Layer B
  (Acme Corp)         (University Trust Lab)
  commercial           academic
  compliance           open-access
    |                   |
    └─────────┬─────────┘
              |
        Joint Client Layer
        (joint-taskforce.yml)
        Cross-org arbitration:
        conservative merge rule
              |
        Session Layer
        (task-specific,
         joint scratchpad)
```

**Conflict site 1: PII-purge vs. reproducibility archive**

Acme's Deployment Layer requires PII purge within 24h. UTL's Deployment Layer requires
experiment configs and session artifacts be archived for reproducibility. If any session
scratchpad contains PII (a researcher name, an organization name), the two requirements
are directly in conflict.

*Resolution*: Joint Client Layer arbitration. The conservative merge principle yields: PII
must be purged (Acme wins on data security); session artifacts must be archived in a PII-scrubbed
form (UTL's reproducibility requirement is satisfied by the scrubbed version). Pre-commit
workflow extension: before scratchpad commit to the shared archive, run a PII detection pass
(pygrep hook or a light NLP scan) and flag/strip before archiving. This satisfies both
Deployment Layer constraints without Core Layer modification.

**Conflict site 2: Attribution norms vs. trade-secret protection**

UTL requires declaration of AI-generated content in all publications. Acme's Client Layer
(the healthcare client, from Scenario 1) has a clause prohibiting disclosure of internal
tooling details in external publications. If the joint publication describes the EndogenAI
agent fleet, it might expose Acme's internal deployment configuration.

*Resolution*: The conservative merge principle and Core Layer both apply. UTL's attribution
requirement is an additive constraint (no Core conflict). Acme's non-disclosure requirement
is also additive — it restricts the *detail level* of attribution, not whether attribution
occurs. The joint publication declares "AI-assisted methods were used" (UTL requirement
satisfied) without naming proprietary agent configurations (Acme requirement satisfied).
The `external-value-architecture.md §Pattern E3` (Provenance Transparency Across Layers)
is the guide: annotate the constraint source in the session scratchpad, do not suppress it.

**Conflict resolution decisions logged**:

| CDR # | Conflict | Winning layer | Resolution |
|---|---|---|---|
| CDR-S3-1 | PII-purge (Acme) vs. reproducibility (UTL) | Both via conservative merge | PII-scrubbed archive satisfies both |
| CDR-S3-2 | Attribution (UTL) vs. non-disclosure (Acme) | Both via conservative merge | Declare AI use without naming configurations |
| CDR-S3-3 | Content-review timeline (Acme) vs. preprint urgency (UTL) | Joint Client Layer (arbitration) | Acme review gating UTL preprint |
| CDR-S3-4 | Custom Agents blocked (UTL) vs. fleet invocation (Core convention) | Deployment Layer (accommodation) | Behavioral contract honored via reference read |

---

## 4. Pattern Catalog

### Pattern D1 — Additive Constraint Composition

Across all three scenarios, every resolvable Deployment Layer constraint is additive — it
restricts behavior that the Core Layer permits but does not require. None of the confirmed
conflict resolutions required a Core Layer modification. This is consistent with
`external-value-architecture.md §Pattern E1`: layer values are restrictions, not replacements.

**Canonical example**: UTL's `open_access: true` Deployment Layer convention adds a publishing
obligation the Core Layer does not have. The Core Layer's Documentation-First principle
supports (but does not require) publishing session summaries. The Deployment Layer adds the
obligation; the Core Layer does not block it. The agent honors both by committing session
summaries to `docs/sessions/` (Core capture mechanism) and marking them for the open-access
archive (UTL obligation).

**Anti-pattern**: A Deployment Layer entry that says "use cloud frontier models for all
research sessions." `MANIFESTO.md §3. Local Compute-First` establishes a preference (not an
absolute) for local models. However, a Deployment Layer entry that *mandates* cloud usage
inverts the preference — it changes the Core Layer's default, which is a relaxation, not a
restriction. Even if the Deployment Layer intent is benign (lab cloud credits are cheaper than
local GPU hours), the entry violates the additive-only constraint. The correct form: "when
local compute is insufficient for task complexity, cloud model use is permitted under these
conditions."

### Pattern D2 — Conservative Merge as Cross-Deployment Arbitration Rule

When two Deployment Layers conflict (Scenario 3), the conservative merge principle — apply
the *more restrictive* of the two constraints — is the neutral, implementable default. It
is consistent with the Core Layer supremacy rule (more protection, not less) and with
Constitutional AI multi-principal literature. It does not require an authority decision about
which Deployment Layer outranks the other — it avoids that question entirely.

**Canonical example**: Acme's 24h PII purge vs. UTL's reproducibility archive conflict.
Neither organization "wins" — both constraints are honored simultaneously by applying the
more restrictive scope (PII-scrubbed archive). The joint-taskforce.yml Client Layer encodes
this as a named rule (`cross_org_arbitration.rule`) so future sessions apply it without
requiring Orchestrator re-explanation.

**Anti-pattern**: Attempting to resolve Deployment-to-Deployment conflicts by asking the
Agent to "figure out which organization's rule is more important in context." Dynamic runtime
arbitration is the canonical failure mode from `external-value-architecture.md §H1` (Bai
et al. 2022): agents that resolve value conflicts dynamically produce non-deterministic
outputs. The conservative merge rule must be encoded in the joint Client Layer before the
session begins, not resolved within it.

### Pattern D3 — Tooling vs. Behavioral Contract Separation

Custom Agents unavailability (Scenarios 2 and 3, UTL IT policy) reveals an important
architectural property: the Core Layer's behavioral requirements are tied to the
*contract* in `.agent.md` files, not to the execution tooling. An organization that cannot
install the VS Code Custom Agents extension still satisfies the contract by having practitioners
read the `.agent.md` file as a reference document. This separation — behavioral contract
vs. execution surface — is an H4 operability implication: the methodology can operate on any
toolchain that supports reading and committing markdown files.

**Canonical example**: UTL researchers read `executive-researcher.agent.md` before starting a
research session instead of invoking it via VS Code's Custom Agents UI. The session-start
encoding checkpoint, endogenous source reading, and scratchpad write still occur — the Core
Layer behavioral contract is fully honored. The only missing element is the VS Code integration
(auto-invocation, tool restrictions). For organizations where this integration is blocked,
the methodology degrades gracefully to reference-based operation.

**Anti-pattern**: Treating the absence of VS Code Custom Agents as a blocker for methodology
adoption. The Core Layer does not specify execution tooling — it specifies behavioral
obligations. A team that says "we cannot adopt EndogenAI because our IT policy blocks VS Code
extensions" has mistaken the execution surface for the behavioral contract. Communicating this
distinction is an H4 onboarding responsibility.

---

## 5. Recommendations

### R1 — Extend Architecture to Specify Inter-Deployment Arbitration Rule

The boundary condition identified in Scenario 3 — two Deployment Layers conflicting with each
other — is not resolved by the current four-layer model in `external-value-architecture.md`.
The conservative merge principle is a workable default and should be codified in the
architecture documentation as the canonical inter-Deployment arbitration rule. Update
`external-value-architecture.md §Pattern E1` to include a fifth layer interaction rule:
"When two Deployment Layers conflict, apply the conservative merge: honor the union of
restrictions." This is a one-paragraph addition.

### R2 — Add Joint Client Layer Template to Adopt Wizard Deliverables

`external-value-architecture.md §R1` recommends seeding `client-values.yml` at Adopt wizard
instantiation. For multi-organization scenarios, a `joint-client.yml` (or `taskforce.yml`)
template should also be generated, pre-populated with the conservative merge arbitration clause
and cross-org Principal declarations. This prevents the Scenario 3 conflict site from arising
in production deployments.

### R3 — Encode Deployment Layer Reading Step Programmatically in Session Start

`external-value-architecture.md §R2` recommends adding a conditional `client-values.yml` read
step to the session-start ritual. The Phase 1b proxy evidence confirms that documentation-first
adoption is reliable — but only after the documentation is committed and the practitioner
knows to look for it. Making the `client-values.yml` read step a pre-commit check (if the
file exists, validate it is read in the session-start scratchpad) would uplift this from T5
prose to T3 programmatic enforcement, consistent with `enforcement-tier-mapping.md §H2`.

### R4 — Test Behavioral Contract Without VS Code Custom Agents Before External Rollout

Pattern D3 (tooling vs. behavioral contract separation) provides a fallback for organizations
with tooling restrictions. Before external rollout, conduct one structured test: have a
practitioner use only `cat`-read of `.agent.md` files (no VS Code invocation) to execute a
full sprint. Measure M2 (encoding checkpoint compliance) and M4 (workplan gate adoption).
If these match the intra-team baselines, the methodology is confirmed toolchain-agnostic for
behavioral purposes.

---

## 6. Sources

### Primary Endogenous Sources (read before writing, per MANIFESTO.md §1. Endogenous-First)

1. **`docs/research/external-value-architecture.md`** — six-layer deployment model, four-layer
   Principal hierarchy, Pattern E1 (Layered Value Architecture), Pattern E2 (Boundary
   Impermeability), Pattern E3 (Provenance Transparency), client-values.yml schema, R1–R3.
   Primary architecture reference for all three scenarios.

2. **`docs/research/external-team-case-study.md`** — Phase 1b findings: H2/H3 confirmed,
   H4 PARTIALLY SUPPORTED, proxy metrics M1–M4, T3/T4 enforcement stack as operability
   enabler. Grounding evidence for all scenario conflict resolution decisions.

3. **`AGENTS.md §Security Guardrails`** — Deployment Layer rules for `client-values.yml`
   interpretation; Supremacy constraints. Cited in CDR-S1-1.

4. **`AGENTS.md §Guiding Constraints`** — "treat client-values.yml as a Deployment Layer
   external-values file"; interpret using Deployment Layer rules and Supremacy constraints.
   Governs scenario setup for all three cases.

5. **`MANIFESTO.md §1. Endogenous-First`** — Core Layer must be read first at every session;
   no Deployment Layer constraint modifies this read-order rule. Cited in CDR-S1-1, Pattern D3.

6. **`MANIFESTO.md §2. Algorithms Before Tokens`** — conflict resolution must be encoded
   structurally; dynamic runtime arbitration is the canonical failure mode. Foundation for
   Pattern D2 and the conservative merge rule.

7. **`docs/research/enforcement-tier-mapping.md`** — T3/T4 enforcement for supremacy rule;
   T5 prose-only as reliability gap; informing R3 (programmatic enforcement of Deployment
   Layer read step).

### External Supporting Sources

8. **Bai et al. (2022)** — "Constitutional AI: Harmlessness from AI Feedback" — multi-principal
   architecture; dynamic runtime conflict resolution failure mode. Cited in `external-value-architecture.md §H1`.

9. **Supremacy Clause, US Constitution Art. VI** — federal/state conflict resolution model
   mapped to Core/Deployment layer hierarchy. Cited in `external-value-architecture.md §H2`.
