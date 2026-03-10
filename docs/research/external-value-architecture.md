---
title: "External Value Architecture — Layered Value Encoding for Adoptions"
status: "Final"
---

# External Value Architecture — Layered Value Encoding for Adoptions

> **Status**: Final
> **Research Question**: When the EndogenAI methodology is adopted by a downstream product team or client, how do we encode their product-specific and client-specific values into the agent substrate alongside the EndogenAI core dogma — without contaminating, overriding, or diluting the foundational axioms?
> **Date**: 2026-03-09
> **Issue**: [#83](https://github.com/EndogenAI/Workflows/issues/83)
> **Related**: [`docs/research/values-encoding.md`](values-encoding.md) (inheritance chain foundation); [`docs/research/bubble-clusters-substrate.md`](bubble-clusters-substrate.md) (boundary-membrane model for inter-layer signal dynamics)

---

## 1. Executive Summary

When the EndogenAI methodology is adopted by a downstream team, the adopting team brings its own value hierarchy — brand voice, ethical constraints, domain conventions, HIPAA compliance, never-casual tone — that must co-exist with the EndogenAI foundational axioms. An agent operating in such a deployment must simultaneously serve two principals: EndogenAI (the methodology owner) and the adopting team (the deployment context).

The risk is bidirectional: (1) client values could silently override foundational axioms (a "respond as fast as possible" client value conflicting with "Algorithms Before Tokens"), or (2) foundational axioms could suppress legitimate client-specific behaviors, making the methodology unworkable in specialized domains.

This synthesis designs a **four-layer value architecture** that resolves this tension using a strict principal hierarchy and explicit conflict resolution rules:

```
Core Layer      (EndogenAI dogma)           — immutable per deployment; highest priority
  └── Deployment Layer  (product/domain)    — team conventions; overrides nothing in Core
        └── Client Layer    (project)       — client-specific constraints; overrides Deployment
              └── Session Layer   (task)    — task-specific overrides; lowest priority
```

**Key finding**: The conflict resolution rule is simple and absolute — Core always wins. Client values are additive constraints on top of the foundational axioms, never replacements for them. This maps directly to the bubble-cluster model's membrane permeability pattern (Pattern B1 from `bubble-clusters-substrate.md`): the boundary between the Core Layer and the Deployment Layer must be impermeable to overrides but fully permeable to additive constraints.

**Hypotheses validated:**

- **H1** — Constitutional AI multi-principal research (Bai et al. 2022) confirms that principal hierarchy with explicit conflict resolution is a tractable and well-studied architecture.
- **H2** — Legal analogies (federal/state law, franchise agreements) confirm that a layered structure with supreme-law precedence is stable and intuitive.
- **H3** — The current EndogenAI inheritance chain (MANIFESTO.md → AGENTS.md → agent files) requires one additional layer — a Deployment Layer — to support client value injection without contaminating the foundational substrate.
- **H4** — A `client-values.yml` file seeded at adoption time is the minimal viable encoding surface for client/deployment values.

---

## 2. Hypothesis Validation

### H1 — Constitutional AI Multi-Principal Architecture Is Tractable

**Verdict: CONFIRMED** — Bai et al. (2022) and multi-stakeholder AI ethics literature

**Constitutional AI basis**: Anthropic's Constitutional AI separates the "constitution" (universal principles) from task-level instructions. In multi-deployment contexts, Anthropic applies deployment-specific constitutions as an additive overlay — the universal principles remain in force; deployment-specific rules add further constraints but cannot relax core principles. This is the precise architecture needed: Core Layer = universal constitution; Deployment Layer = deployment-specific overlay.

**Principal hierarchy literature (OpenAI, Anthropic)**: Both labs publish explicit principal hierarchies — Lab > Operator > User — where each level can restrict but not relax the constraints of the level above. An operator can tell the model "don't mention competitor products"; an operator cannot tell the model "ignore safety guidelines." The EndogenAI equivalent: EndogenAI dogma > Deployment conventions > Client constraints > Session overrides.

**Multi-stakeholder value alignment (AI ethics literature)**: The core result from principal hierarchy research is that conflict resolution must be *predetermined* — agents that attempt to resolve value conflicts dynamically at runtime produce non-deterministic behavior and are exploitable (a sophisticated client prompt can make the agent "decide" Core Layer values are less relevant). Conflict resolution must be encoded structurally, not left to session-time inference.

**Connection to MANIFESTO.md — Axiom: Endogenous-First (§1)**: The Core Layer is the endogenic substrate — it must be read first, before any Deployment or Client layer context, in every session. The session-start ritual (read MANIFESTO.md, read AGENTS.md, read scratchpad) is the enforcement mechanism for Core Layer priority.

---

### H2 — Legal Analogies Confirm Principal Hierarchy Stability

**Verdict: CONFIRMED** — federal/state law and franchise agreements are proven implementations

**Federal/state law (Supremacy Clause, US Constitution Art. VI)**: Federal law is supreme; state law is valid where it adds restrictions or addresses areas federal law does not cover; state law is void where it contradicts federal law. No explicit runtime arbitration is needed — the hierarchy is constitutive. The schema maps cleanly: EndogenAI dogma = federal law, client constraints = state law, conflict resolution = Supremacy Clause.

**Franchise analogy**: A McDonald's franchisee must maintain core brand standards (Core Layer) but can adapt to local preferences within those standards (Deployment Layer). The franchisee cannot serve alcohol (client-prohibited at the Core Layer); the franchisee can adjust store hours (Deployment Layer, no Core conflict). A franchise agreement is literally a `client-values.yml` — the deployment-specific override file that operates under the parent brand's foundational constraints.

**Plugin/extension model (VS Code)**: VS Code core settings govern security, rendering, and workspace trust. Extensions can add commands, UI elements, and settings — but cannot disable security sandbox enforcement. The extension manifest (`package.json`) is the `client-values.yml` equivalent: it declares what the extension adds, and VS Code's loading mechanism enforces that extensions are additive, not override-capable.

---

### H3 — Current Inheritance Chain Requires a Deployment Layer Addition

**Verdict: CONFIRMED** — the current four-layer chain is insufficient for multi-tenant deployments

Current chain: `MANIFESTO.md` (T1) → `AGENTS.md` (T2/T3) → agent files → session behavior

For a client adoption deployment, this chain needs one additional layer between AGENTS.md and agent files:

```
MANIFESTO.md               (Core Layer — EndogenAI axioms)
  └── AGENTS.md            (Core Layer — operational EndogenAI constraints)
        └── client-values.yml / .client.agent.md   (Deployment/Client Layer — NEW)
              └── Agent files                       (Implementation layer, reads both)
                    └── Session behavior            (Enacted output)
```

The new Deployment Layer file is seeded when the Adopt wizard (#56) instantiates a new deployment. It contains only additive constraints — assertions about what the client cares about, not overrides of what EndogenAI requires. The agent file author reads `AGENTS.md` first (Core Layer priority), then `client-values.yml` (Deployment Layer additional context).

**Connection to MANIFESTO.md — Axiom: Algorithms Before Tokens (§2)**: The `client-values.yml` insertion point must be codified in the Adopt wizard as a scripted step, not a manual configuration instruction. The adoption script generates the file stub; the adopting team fills it in. Programming the injection point closes the gap between theory (layered architecture) and deployed behavior (agents that actually consult client values).

---

### H4 — client-values.yml Is the Minimal Viable Encoding Surface

**Verdict: CONFIRMED** — YAML format is low-friction, parseable, and consistent with existing data conventions (`data/labels.yml`)

A `client-values.yml` file at the root of the adopted repository encodes deployment-specific values as structured constraints. Proposed schema:

```yaml
# client-values.yml — Deployment Layer value encoding
# These constraints are ADDITIVE to the EndogenAI Core Layer (MANIFESTO.md + AGENTS.md).
# They restrict or extend Core behavior; they cannot override it.

client:
  name: "Acme Corp Product Team"
  domain: "healthcare-hipaa"

# Tone and communication constraints
communication:
  tone: "professional"     # never casual
  never_mention: []        # list of prohibited topics or entities

# Compliance and ethical hard stops (additive to MANIFESTO.md §Ethical Values)
compliance:
  - "HIPAA — no PII in logs, scratchpads, or agent file outputs"
  - "never suggest non-FDA-approved treatments"

# Domain conventions
conventions:
  - "use metric units throughout"
  - "prefer clinical terminology over colloquial phrasing"

# Conflict resolution declaration (informational — Core always wins)
conflict_resolution: "EndogenAI Core Layer (MANIFESTO.md + AGENTS.md) supersedes all entries in this file. Any apparent conflict must be resolved in favor of the Core Layer."
```

The `conflict_resolution` field is informational — it makes the supremacy principle explicit in the file itself, reducing the probability of an agent "deciding" to prioritize a compliance constraint over a Core axiom in an ambiguous case. Performative encoding (from `values-encoding.md` §3 Pattern 4) applied to the Deployment Layer.

---

## 3. Pattern Catalog

### Pattern E1 — Layered Value Architecture with Supremacy Declaration

**Source fields**: Constitutional AI (Bai et al. 2022), constitutional law (Supremacy Clause), franchise agreements

**Pattern**: Structure deployment values as four ordered layers. Each layer may restrict behavior but not relax constraints from higher layers. The supremacy rule is declared explicitly in each file, not inferred.

**Layer definitions**:
1. **Core Layer** — `MANIFESTO.md` + `AGENTS.md`: the EndogenAI foundational axioms and operational constraints; immutable per deployment; read first at every session
2. **Deployment Layer** — `client-values.yml`: additive domain, compliance, and tone constraints specific to the adopting team; seeded at adoption via Adopt wizard
3. **Client Layer** — per-project constraints (can be expressed as YAML extensions or in a `.client.agent.md` agent preamble); project-specific rules that further constrain the Deployment Layer
4. **Session Layer** — scratchpad and task-specific instructions; narrowest scope; lowest priority; cannot override any higher layer

**Canonical example**: A healthcare deployment adds a HIPAA compliance constraint in `client-values.yml`. An agent writing a session scratchpad sees the constraint and omits patient data from all logged outputs. The constraint is additive (HIPAA adds restrictions Core Layer doesn't have) and never conflicts with a Core axiom. The agent reads `AGENTS.md` first (Endogenous-First axiom satisfied), then checks `client-values.yml` for deployment-specific additions.

**Anti-pattern**: A client constraint that says "respond as fast as possible — skip the session-start reading ritual." This is a Core Layer override attempt: the reading ritual is mandated by the Endogenous-First axiom (MANIFESTO.md §1). Even if the client's intent is benign (they want faster sessions), the constraint violates the supremacy rule. The correct response: note the conflict in the session scratchpad, honor the Core Layer constraint, and optionally log a signal for the dogma neuroplasticity protocol (an accumulated signal that the session-start ritual has excessive overhead could eventually reach T2/T3 threshold and be addressed through the proper back-propagation channel).

**Actionable implication**: When implementing the Adopt wizard (#56), the wizard script must generate a `client-values.yml` stub with the `conflict_resolution` field pre-populated. The stub is committed to the adopted repository at initialization time, establishing the Deployment Layer before any agent files or session work begins.

---

### Pattern E2 — Boundary Impermeability for Core Layer

**Source fields**: Bubble-cluster model (Pattern B1), Constitutional AI principal hierarchy, federal law Supremacy Clause

**Pattern**: The membrane between the Core Layer and the Deployment Layer is impermeable to overrides and fully permeable to additive constraints. An agent processing a Deployment Layer file must treat any entry that conflicts with the Core Layer as non-operative — log it, do not honor it.

**Actionable implication**: `scripts/validate_agent_files.py` should be extended to check that agent files cite `MANIFESTO.md` or `AGENTS.md` as the first-priority source, and flag any agent file whose preamble cites a `client-values.yml` as a higher-priority source. This is the programmatic governance gate (MANIFESTO.md — Axiom: Algorithms Before Tokens §2) that enforces Core Layer impermeability.

---

### Pattern E3 — Provenance Transparency Across Layers

**Source fields**: Filter-bubble research (Pariser 2011), `values-encoding.md` §3 Pattern 7, `bubble-clusters-substrate.md` Pattern B4

**Pattern**: Every agent output that applies a constraint must be traceable to its source layer. An agent that applies a HIPAA constraint should note in the scratchpad: "Omitting PII — `client-values.yml` §compliance, HIPAA rule." An agent that applies an EndogenAI axiom should note: "Endogenous-First (MANIFESTO.md §1) — reading prior scratchpads before scouting."

**Actionable implication**: `audit_provenance.py` can be extended to trace value citations across layers — flagging agent outputs that apply constraints with no cited layer. Low-provenance outputs are high-drift-risk regardless of which layer they originate from.

---

## 4. Recommendations

Ordered by impact-to-cost:

### R1 — Seed client-values.yml at Adopt Wizard Instantiation (Pattern E1)

**Target**: `#56` (Adopt wizard) and prospective `scripts/adopt_wizard.py`
**Action**: The Adopt wizard script must generate a `client-values.yml` stub at the root of the adopted repository. The stub must include the `conflict_resolution` field pre-populated and a comment block explaining the Supremacy Rule.
**Rationale**: Without a seeded stub, adopting teams either omit deployment values entirely (encoding gap) or encode them ad hoc in agent files (fragmentation and Core Layer override risk). The stub makes the encoding surface explicit and structured.

### R2 — Add Deployment Layer Reading Step to Session Start Ritual

**Target**: `AGENTS.md` §Session Start Ritual
**Action**: Add a conditional step: "If a `client-values.yml` exists in the repository root, read it after `AGENTS.md` and before any agent files. Note the deployment-layer constraints in the `## Session Start` entry."
**Rationale**: The Deployment Layer is only effective if agents actually read it. The session-start ritual is the enforcement mechanism. Adding a conditional read step costs one bullet point in AGENTS.md and closes the entire Core→Deployment→agent-file handoff gap.

### R3 — Extend validate_agent_files.py for Core Layer Impermeability Check (Pattern E2)

**Target**: `scripts/validate_agent_files.py`
**Action**: Add a check that flags agent files which cite `client-values.yml` as a higher-priority source than `MANIFESTO.md` or `AGENTS.md`.
**Rationale**: Programmatic governance (MANIFESTO.md — Axiom: Algorithms Before Tokens §2) — the supremacy rule must be enforced by code, not by convention.

---

## Sources

**Endogenous (primary)**:
- `docs/research/values-encoding.md` — inheritance chain model, §H5, §3 Pattern 4 (performative encoding), §4 R7 (retrieval-augmented governance)
- `docs/research/bubble-clusters-substrate.md` — Pattern B1 (calibrated membrane permeability), Pattern B4 (provenance transparency), Core Layer impermeability rationale
- `MANIFESTO.md` — Axiom: Endogenous-First (§1), Axiom: Algorithms Before Tokens (§2)
- `AGENTS.md` — §Session Start Ritual, §Agent Communication
- `data/labels.yml` — schema consistency reference for YAML conventions

**External (supporting)**:
- Bai et al. (2022) — "Constitutional AI: Harmlessness from AI Feedback" — principal hierarchy, multi-context constitution deployment
- Eli Pariser (2011) — *The Filter Bubble* — filter-bubble dynamics, provenance transparency as counter-mechanism
- OpenAI Usage Policies, Anthropic Responsible Scaling Policy — operator/user principal hierarchy implementations
- Supremacy Clause, US Constitution Art. VI — federal/state conflict resolution model
- VS Code Extension API — plugin value architecture, additive-constraint model
