---
title: Client Adoption Pattern — Dogma Governance Framework
description: Minimum-viable adoption path for a new client team deploying dogma governance across all four deployment tiers.
applies_to: client deployments, deployment layer, governance cascade
---

# Client Adoption Pattern — Dogma Governance Framework

This guide encodes the minimum-viable adoption path for a new client team deploying dogma governance. It follows the four-phase pattern documented in [`docs/research/client-manifesto-adoption-pattern.md`](../research/client-manifesto-adoption-pattern.md).

**Governing axiom**: Endogenous-First — scaffold from existing system knowledge before reaching outward.

---

## Phase 1 — Readiness Layer Configuration

**Issue**: #456

Establish the minimum viable Deployment Layer structure before any governance cascade begins. The Deployment Layer is the client-scoped configuration envelope that specialises Core Layer constraints without overriding them.

### Required Fields

Three fields in `client-values.yml` must be populated before the governance cascade can initialise:

1. `project_name` — identifies the client project in all governance tooling output
2. `domain` — classifies the regulatory and operational context (e.g. fintech, healthtech)
3. `mission` — a single sentence encoding the project purpose; used by agents to contextualise decisions

### Minimum Viable `client-values.yml` Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_name` | string | Yes | Human-readable project name |
| `domain` | string | Yes | Primary domain (e.g. fintech, healthtech) |
| `mission` | string | Yes | One-sentence project purpose |
| `team_size` | string | No | Approximate team size (xs/s/m/l) |
| `priorities` | list | Recommended | Ordered top concerns (security, cost, etc.) |
| `axiom_emphasis` | list | Recommended | Dogma axioms to amplify |
| `constraints` | list | Optional | Domain-specific guardrails |

### Validation

After populating `client-values.yml`, run:

```bash
uv run python scripts/validate_cascade.py --tier 1 client-values.yml
```

A passing result confirms the Deployment Layer is structurally sound and prepared for cascade integration.

### Deployment Layer Directory Template

```
<project-root>/
  client-values.yml          # Required: populated before governance cascade
  AGENTS.md                  # Optional: project-scope overrides (DO NOT override MANIFESTO.md)
  docs/
    guides/                  # Project-specific guides (can reference dogma guides)
  .github/
    agents/                  # Client agents (must include instruction hierarchy)
```

### Acceptance Criteria

- Team can author and validate `client-values.yml` without external guidance
- Validation command passes: `uv run python scripts/validate_cascade.py --tier 1 client-values.yml`

---

## Phase 2 — Governance Cascade Integration

**Issue**: #457

The T1→T5 cascade validates the encoding chain at each layer boundary. Every tier must reference the tier above it; gaps produce orphaned constraints that agents silently ignore.

### Cascade Table

| Tier | Layer | Inputs | Outputs | Validation Gate |
|------|-------|--------|---------|-----------------|
| T1 | MANIFESTO.md (Core Layer) | Foundational axioms | Governing constraints | MANIFESTO.md unchanged; all agents cite ≥2 axioms |
| T2 | AGENTS.md (Fleet Layer) | T1 axioms | Fleet constraints + decision gates | Every constraint references a T1 axiom; no orphaned rules |
| T3 | .agent.md (Role Layer) | T2 constraints | Role-specific posture + toolsets | Every `<constraints>` block references AGENTS.md |
| T4 | SKILL.md (Procedure Layer) | T3 posture | Reusable procedures | Every skill references governing axiom |
| T5 | Session behavior (Enacted Layer) | T4 procedures | Actual agent decisions | Session start names axiom; scratchpad records decisions |

### Pre-commit Hook

The `validate-deployment-cascade` pre-commit hook (candidate: `scripts/validate_cascade.py`) enforces cascade integrity on every commit that touches agent, skill, or governance files.

### Cascade Gap Examples (Anti-Patterns)

- **T1 axiom not cited in T2 constraint** → encoding gap; constraint is unanchored
- **T2 constraint present in AGENTS.md but absent from all `.agent.md` files** → cascade failure; the constraint has no enacted expression
- **T3 agent file references a skill that doesn't exist** → broken reference; skill is inaccessible at runtime

### Acceptance Criteria

Any encoding gap (T1 not cited in T2, T2 constraint missing from T3) is detected by `scripts/validate_cascade.py`.

---

## Phase 3 — Validation Gates and False-Positive Prevention

**Issue**: #458

Prevent adoption false-positives by requiring end-to-end capability tests at each tier boundary. An adoption may not be signed off until all five integration checkpoints pass and the deployment contract is endorsed.

### Five Integration Checkpoints

| Checkpoint | Transition | Required Evidence |
|------------|-----------|-------------------|
| CP-1 | T1 → T2 | AGENTS.md cites ≥3 MANIFESTO.md sections with `§` references |
| CP-2 | T2 → T3 | All `.agent.md` files have `<constraints>` block referencing AGENTS.md |
| CP-3 | T3 → T4 | All SKILL.md files have governing axiom reference in first section |
| CP-4 | T4 → T5 | Session start names governing axiom; scratchpad has `## Session Start` |
| CP-5 | Pre-deployment | `client-values.yml` valid + deployment contract signed off |

### Deployment Contract

See [Deployment Contract template](./deployment-contract.md) for the standard sign-off template. Use `scripts/check_readiness_matrix.py` on the completed contract before marking the deployment ready.

### Acceptance Criteria

No adoption can be marked complete until all 5 checkpoints pass and the deployment contract is signed off.

---

## Phase 4 — Orchestration Guardrails and Autonomous Safety

**Issue**: #459

Prevent orchestrator autopilot failures by encoding instruction hierarchy and interrupt guards into every client agent file. Autonomous sessions that ignore user interrupt signals are an encoding failure, not a runtime edge case.

### Minimum Required `<constraints>` Block

Every client agent deploying dogma governance must include the following in its `<constraints>` section:

```yaml
# Minimum required constraints for any client agent deploying dogma governance:
# 1. Instruction Hierarchy Override (from AGENTS.md § Instruction Hierarchy):
#    - User real-time interruption signals (STOP, ABORT, etc.) override all phase gates
#    - On interrupt: exit immediately, write scratchpad checkpoint, return control to user
# 2. Verification-First (from AGENTS.md § Guardrails):
#    - Before invoking any script: run --help or read docstring first
# 3. Readiness Language Guard (from AGENTS.md § Readiness Language Guard):
#    - No unqualified "ready/complete/done" without capability matrix + demo artifact
```

### Integration with Tracks A/B

- **Track A (Instruction Hierarchy)**: See [AGENTS.md § Instruction Hierarchy](../../AGENTS.md#instruction-hierarchy) for the full interrupt signal keyword list and exit protocol.
- **Track B (User Interrupt Signal Handler)**: MCP `detect_user_interrupt()` tool is available for all client sessions; invoke before each phase gate.

### Acceptance Criteria

- Client agent files include explicit instruction hierarchy + interrupt handler sections
- Agents check for interrupts before each phase
