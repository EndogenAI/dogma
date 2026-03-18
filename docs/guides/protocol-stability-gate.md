---
governs: [endogenous-first, local-compute-first]
---

# Protocol Stability Gate

> Governing axiom: [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — adopt integrations from a stable, validated substrate before reaching for new external ones. [MANIFESTO.md § 3 Local-Compute-First](../../MANIFESTO.md#3-local-compute-first) — an unstable external integration transfers governance authority to an external party.

Before adopting any new AI integration (model, API, SDK, or inference provider), all three criteria below must pass. Failure on any criterion means the integration is not ready: open a D4 research doc first, document the gap, and schedule re-evaluation.

---

## Three-Criterion Gate

### Criterion 1 — Production Stability ≥ 30 Days

The integration must have been stable in production use elsewhere for at least 30 days. Acceptable evidence:

- A public issue tracker showing no breaking changes in the last 30 days (cite URL or issue number in D4 doc)
- A stable release tag with a changelog entry confirming no breaking API changes in ≥ 30 days
- A committed D4 research doc in `docs/research/` recording the stability verification with source citations

**If evidence is absent**: Do not adopt. Open a D4 research doc in `docs/research/` with the stability question as an open hypothesis (`status: Draft`). Re-evaluate in 30 days.

### Criterion 2 — Prior Integration Formally Deprecated

If the new integration replaces an existing one, the prior integration must be formally deprecated with a documented migration path before the new one is activated. The migration path must:

1. List all internal scripts, agent files, and config entries that reference the prior integration
2. Specify replacement references for each
3. Be committed to `docs/guides/` or an ADR in `docs/decisions/` before the new integration is enabled

**If no prior integration exists**: This criterion passes automatically.

### Criterion 3 — Ethics Rubric Pass

The integration must satisfy ≥ 3 criteria from the ethical-values procurement rubric in [`docs/governance/ethical-values-procurement.md`](../../docs/governance/ethical-values-procurement.md). The qualifying criteria must be named explicitly in the D4 research doc or ADR before adoption proceeds.

---

## Failure Mode → Recovery Path

| Failure | Recovery |
|---------|----------|
| Criterion 1: stability evidence missing | Open D4 research doc; schedule re-evaluation in 30 days |
| Criterion 2: migration path undocumented | Draft migration guide to `docs/guides/` before activating new integration |
| Criterion 3: ethics rubric < 3 criteria | Reject integration or redesign until rubric passes |
| All three fail | Full stop; current integration remains active until criteria met |

---

## Governing References

- [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — integrate from a stable endogenous substrate before reaching for new external platforms
- [MANIFESTO.md § 3 Local-Compute-First](../../MANIFESTO.md#3-local-compute-first) — external dependency adoption transfers governance risk; validate stability before adoption
- [AGENTS.md § New Tool Encoding Gate](../../AGENTS.md#new-tool-encoding-gate) — companion gate that verifies internal-overlap and D4-research-first requirements
- [docs/governance/ethical-values-procurement.md](../../docs/governance/ethical-values-procurement.md) — ethics rubric used in Criterion 3
