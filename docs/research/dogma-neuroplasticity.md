---
title: "Dogma Neuroplasticity & Back-Propagation Protocol"
status: Final
---

# Dogma Neuroplasticity & Back-Propagation Protocol

> **Related issues**: [#82](https://github.com/EndogenAI/Workflows/issues/82), [#75](https://github.com/EndogenAI/Workflows/issues/75)
> **Date**: 2026-03-09
> **Research question**: How should accumulated session observations propagate back into the foundational substrate (`MANIFESTO.md`, `AGENTS.md`) in a governed, auditable way — without destabilizing the inheritance chain?

---

## Executive Summary

The endogenic substrate encodes values across four layers: `MANIFESTO.md` (axioms) → `AGENTS.md` (operational constraints) → agent files → session behavior. The inheritance chain is deliberately one-directional at runtime: values flow *downward* from axiom to action. However, the system must also support an *upward* feedback cycle — accumulated session evidence should refine the substrate, or the substrate will become stale and drift from actual practice.

This synthesis establishes the **dogma neuroplasticity protocol**: a governed framework for back-propagating session evidence into the substrate at the correct stability tier, with evidence thresholds, audit trails, and a coherence check to prevent inheritance-chain incoherence. It directly addresses the **Endogenous-First axiom** (`MANIFESTO.md` §1) by grounding all proposed edits in observed endogenous behavior rather than external theory alone.

**Hypotheses validated:**

- **H1** — Different substrate layers require different mutation rates and signal thresholds (CONFIRMED by Constitutional AI literature and living documentation theory).
- **H2** — A tiered stability model with evidence thresholds prevents both stasis (axioms never update) and noise-driven churn (operational constraints update every session) (CONFIRMED by double-loop learning framework and ADR precedent in this repo).
- **H3** — An ADR-style dogma edit template with coherence checks can prevent cross-layer incoherence during substrate evolution (CONFIRMED by ADR corpus analysis — 6 ADRs in `docs/decisions/`, all reference upstream inheritance layers).

---

## Hypothesis Validation

### H1 — Stability Varies by Layer

**Verdict: CONFIRMED** — convergent evidence from Constitutional AI, living documentation theory, and endogenous ADR corpus.

**Constitutional AI basis** (Bai et al., 2022): The RLAIF feedback loop operates on the "constitution" — a set of principles used for self-critique. The constitution itself is treated as stable anchoring, not as a live target of the feedback loop. This separation between *applying* values (T3 behavioral updates) and *revising* values (rare T1 rewrites) is the foundational architectural decision. The self-critique mechanism maps directly to session observation: each scratchpad retrospective is a self-critique pass against the current substrate.

**Argyris single/double-loop learning**: Single-loop learning fixes behavior within existing governing norms — equivalent to a T3 AGENTS.md edit that adjusts an operational constraint without questioning the principle behind it. Double-loop learning questions the governing norm itself — equivalent to a T1/T2 MANIFESTO.md edit that revises a principle or axiom. Argyris established that double-loop change requires more evidence accumulation and a different governance process than single-loop change. This maps directly to the T1 (formal ADR required) versus T3 (2-session-signal threshold only) distinction.

**Living specification basis** (Martraire, 2019; `docs/research/sprint-DE-h4-cs-lineage.md`): Living documentation co-evolves with its system but at different velocities per layer. Knuth's literate programming showed that code-level documentation changes with every commit; architectural decision records change with major architecture shifts; foundational axioms change only under paradigm revision. The MANIFESTO.md → AGENTS.md → agent-file hierarchy mirrors this velocity gradient exactly.

**Endogenous evidence** (`docs/decisions/`): All 6 ADRs in this repo demonstrate the pattern — each decision record modifies the `Consequences` layer (AGENTS.md guardrails) while referencing but not altering the axiom layer. ADR-005 (rebase strategy) cites Endogenous-First but does not propose editing it. This confirms the T1/T3 boundary as already-practiced, even before being formally articulated.

### H2 — Evidence Thresholds Prevent Both Stasis and Churn

**Verdict: CONFIRMED** by living specification mutation-rate analysis.

The risk in each direction:
- **Without a floor threshold**: every session observation triggers AGENTS.md edits → operational constraint churn, contradiction accumulation, inheritance-chain noise.
- **Without a ceiling threshold**: axioms never update even when session evidence consistently contradicts them → substrate stasis, drift between stated values and practiced behavior.

Stable vs. volatile policy layer mutation rates:
- **T1 (Axioms)**: mutation rate ≈ 1-2 per year; requires accumulated, cross-session, cross-session-type evidence plus formal ADR review.
- **T2 (Guiding Principles)**: mutation rate ≈ quarterly; requires multi-session evidence and a scratchpad retrospective.
- **T3 (Operational Constraints)**: mutation rate ≈ weekly; 2 independent session signals are sufficient.

The thresholds below encode this gradient.

### H3 — ADR Template Prevents Inheritance-Chain Incoherence

**Verdict: CONFIRMED** by ADR corpus structural analysis.

A review of all 6 ADRs in `docs/decisions/` reveals a consistent structural pattern: Context (establishing the governing constraint from which the problem derives), Decision (the proposed change), Consequences (the AGENTS.md + downstream edits required), and in ADR-005, an explicit `## Connection to Endogenic Values` section cross-referencing the axiom layer. This final section is the **coherence check** — it verifies that the proposed change is consistent with, rather than contradictory to, upstream inheritance layers.

The dogma edit template (Pattern C below) formalizes this pattern as a mandatory `## Coherence Check` step before any T1 or T2 substrate edit is accepted.

---

## Pattern Catalog

### Pattern C1 — Stability Tier Model

The substrate is divided into three tiers based on mutation velocity and evidence requirements:

| Tier | Layer | Location | Stability | Evidence threshold |
|------|-------|----------|-----------|-------------------|
| **T1** | Axioms | `MANIFESTO.md` §axioms (`### 1. Endogenous-First`, `### 2. Algorithms Before Tokens`, `### 3. Local Compute-First`) | Very stable | 3 independent session signals + formal ADR in `docs/decisions/` |
| **T2** | Guiding Principles | `MANIFESTO.md` non-axiom sections + `AGENTS.md` §1 | Moderately stable | 3 independent session signals + `## Reflection` or `## Heuristic` block in scratchpad retrospective |
| **T3** | Operational Constraints | `AGENTS.md` operational sections (§Agent Communication, §Guardrails, §Toolchain Reference, etc.) | Rapidly evolving | 2 independent session signals → AGENTS.md edit via PR |

**Signal definition**: A *signal* is any scratchpad section (`## Reflection`, `## Session Summary`, `## Heuristic`, `## Pre-Compact Checkpoint`) that contains an explicit observation about a constraint failing, succeeding unexpectedly, or being consistently worked around. Incidental mentions do not count. The observation must name the specific AGENTS.md section or MANIFESTO.md principle involved.

**Inheriting-layer constraint**: When a T1 or T2 edit is accepted, all inheriting layers must be audited for coherence. A T2 edit to a Guiding Principle invalidates all T3 operational constraints derived from it until they are reviewed. This is the purpose of the `## Coherence Check` in the ADR template (Pattern C3 below).

### Pattern C2 — Back-Propagation Protocol

The full protocol for accumulating and applying session evidence:

**Step 1 — Signal capture**: At every session close, the Executive writes `## Reflection` in the scratchpad. Any observation that names a specific constraint as failing, succeeding unexpectedly, or consistently bypassed is a *candidate signal*. Write it explicitly: `**Signal**: AGENTS.md §Focus-on-Descent — compression-on-ascent strips labeled canonical examples; observed in Phase 5 and Phase 6B archived docs.`

**Step 2 — Signal aggregation**: After each session, run `uv run python scripts/propose_dogma_edit.py --input .tmp/<branch>/<date>.md --tier T3|T2|T1 --affected-axiom "<section name>" --proposed-delta "<brief delta description>"`. This reads signals from the session file and produces a draft ADR-style proposal. The proposal is committed to a `docs/decisions/` branch but not merged until the threshold is reached.

**Step 3 — Threshold check**: The `propose_dogma_edit.py` CLI checks the evidence count against the tier threshold. If insufficient signals exist, it outputs a `Status: Pending — N signals collected, M required` note and exits 0. It does not block; it records.

**Step 4 — Coherence check**: When the threshold is reached, `propose_dogma_edit.py` runs the coherence check: does the proposed delta remove any `WATERMARK_PHRASES` from the affected section? Does the proposed delta contradict any T1 axiom? If either check fails for a T1 edit, exit code is 1 (blocking).

**Step 5 — ADR commit and review**: When the check passes, a formal ADR is committed to `docs/decisions/` (for T1/T2 edits). The Executive routes the ADR through the Review agent. Only after APPROVED is the substrate edit applied.

**Step 6 — Propagation**: After the substrate edit lands, `scripts/validate_agent_files.py --all` is run to check for inheritance-chain incoherence in downstream agent files. Any agent file that references the edited section is flagged for review.

**Canonical example**: Phase 5 + Phase 6B sessions each produced a signal that labeled `**Canonical example**:` and `**Anti-pattern**:` instances were 100% eliminated at the Synth→Archive boundary. Two independent sessions → T3 threshold (2 signals) met → AGENTS.md §Focus-on-Descent amended with 3 additive signal-preservation rules. This is a complete T3 back-propagation cycle: signal → aggregation → threshold check → coherence check (passes; additive-only) → substrate edit applied.

**Anti-pattern**: Discovering through ad-hoc inspection that agents are ignoring a constraint (e.g., missing canonical examples in archive docs) and patching the constraint once without recording the signal. Without `propose_dogma_edit.py` accumulating evidence citations, the next session has no record of *why* the constraint exists, and the next Synthesizer will compress it out again. Signal-free edits are the substrate equivalent of undocumented code: locally correct, globally fragile.

### Pattern C3 — ADR-Style Dogma Edit Template

All T1 and T2 substrate edits must use this template. T3 edits may use it optionally but are not required to.

```markdown
# DEP-<NNN>: <Brief title>

**Date**: YYYY-MM-DD
**Tier**: T1 | T2 | T3
**Affected section**: `MANIFESTO.md §<heading>` | `AGENTS.md §<heading>`
**Status**: Proposed | Accepted | Rejected

---

## Current Text

> [exact verbatim quote of the text being modified]

## Proposed Text

[unified-diff format or full replacement block]

## Evidence

Session file citations (≥2 for T2; ≥3 for T1):

- `.tmp/<branch>/<date>.md` — `## Reflection`: [quoted signal]
- `.tmp/<branch>/<date>.md` — `## Heuristic`: [quoted signal]

## Coherence Check

- **Watermark phrase preservation**: proposed delta removes/retains: [list]
- **Axiom consistency**: does the proposed text contradict any T1 axiom? [Yes/No + justification]
- **Inheriting layers requiring review**: [list downstream layers affected]
- **Result**: Passes | Fails

## Consequences

[What downstream layers must change; AGENTS.md guardrails; agent files]

## References

[Links to session files, related issues, prior ADRs]
```

---

## Recommendations

### R1 — Implement `scripts/propose_dogma_edit.py`

The programmatic enforcer of the back-propagation protocol. This implements **Algorithms Before Tokens** (`MANIFESTO.md` §2): the evidence threshold check and coherence validation are deterministic operations that should not require a human agent to compute manually.

**Specification** (derived from D21–D27 in [`docs/plans/2026-03-08-value-encoding-fidelity.md`](../plans/2026-03-08-value-encoding-fidelity.md)):

**Inputs:**
- `--input <session-file>`: Path to a scratchpad session Markdown file
- `--tier T1|T2|T3`: Target stability tier
- `--affected-axiom <str>`: Name or heading of the affected section
- `--proposed-delta <str or ->`: Proposed change text; `-` reads from stdin
- `--output <path>`: Output path for the ADR-style proposal (default: stdout)

**Outputs:**
- ADR-style Markdown proposal using the Pattern C3 template
- Exit code 0 on success; exit code 1 if `coherence_check["passes"] is False` and `tier == "T1"`

**Core functions:**

`load_stability_tiers() -> dict[str, dict]` — returns hardcoded tier metadata:
```python
{"T1": {"name": "Axioms", "session_threshold": 3, "requires_adr": True},
 "T2": {"name": "Guiding Principles", "session_threshold": 3, "requires_adr": False},
 "T3": {"name": "Operational Constraints", "session_threshold": 2, "requires_adr": False}}
```

`extract_evidence(session_text: str) -> list[str]` — imports `WATERMARK_PHRASES` from `scripts/detect_drift`; returns all lines in `session_text` containing any watermark phrase. Returns `[]` for empty input. Do not reimplement `WATERMARK_PHRASES` — import directly from `detect_drift`.

`check_coherence(tier: str, proposed_delta: str, tiers: dict) -> dict` — returns `{"passes": bool, "session_threshold": int, "inheriting_layers": list[str]}`. Sets `passes: False` if `proposed_delta` removes any `WATERMARK_PHRASES` entry. T1 edits always require `requires_adr: True`. Import `WATERMARK_PHRASES` from `detect_drift`; import `extract_manifesto_axioms` from `audit_provenance` for axiom-consistency checks.

`generate_proposal(tier, affected_axiom, current_text, proposed_delta, evidence_lines, coherence_result, today_date) -> str` — returns Markdown using the Pattern C3 template with all 7 headings: Date, Tier, Current Text, Proposed Text, Evidence, Coherence Check, Status.

`main(argv: list[str] | None = None) -> int` — argparse CLI. `--proposed-delta -` reads from stdin. Writes proposal to `--output` or stdout. Returns 0 on success; 1 if `coherence["passes"] is False` and tier is T1.

### R2 — Wire Evidence Aggregation into Session-Close Ritual

Add `propose_dogma_edit.py` to the Executive's session-close step: after writing `## Session Summary`, run the script against the session file for any T3 signals identified during the session. This transforms the session-close from a documentation step into a substrate-feedback step — the script accumulates evidence automatically rather than requiring the Executive to remember to run it separately.

### R3 — Phase 8 — External Value Survey Integration Point

Once the back-propagation protocol is operational, [issue #83](https://github.com/EndogenAI/Workflows/issues/83) (external values survey) becomes tractable: external literature signals can be treated as T2 evidence inputs. A formal external review would produce `## Evidence` citations from published literature rather than scratchpad sessions; the ADR template accepts both. The same `propose_dogma_edit.py` CLI handles external-literature proposals by treating the evidence section as free-text rather than session-file citations.

---

## Sources

- **Bai et al. (2022)** — *Constitutional AI: Harmlessness from AI Feedback* (Anthropic). Section on RLAIF feedback loop and constitutional self-critique mechanism. Cited in `docs/research/values-encoding.md` §H4.
- **Argyris, C. & Schön, D. (1978)** — *Organizational Learning: A Theory of Action Perspective*. Single-loop vs. double-loop learning. Maps T3 (single-loop behavioral adjustment) to T1 (double-loop governing-norm revision).
- **Martraire, C. (2019)** — *Living Documentation*. Living specifications co-evolve with the system at velocity gradients proportional to abstraction layer. Cited in `docs/research/sprint-DE-h4-cs-lineage.md`.
- **`docs/research/values-encoding.md`** — H4 (Holographic Encoding), Pattern 5 (Programmatic Governance), OQ-VE-5 (Value drift in multi-agent handoffs). Primary endogenous research foundation for this synthesis.
- **`docs/decisions/`** (ADR-001 through ADR-006) — Structural template for Pattern C3; establishes `## Consequences` and `## Connection to Endogenic Values` as canonical coherence-check mechanics already in practice.
- **`MANIFESTO.md` §1 (Endogenous-First)** — governing axiom: back-propagation protocol is grounded in endogenous session evidence before external literature input.
- **`MANIFESTO.md` §2 (Algorithms Before Tokens)** — `propose_dogma_edit.py` implements evidence threshold checking and coherence validation as deterministic scripts rather than interactive agent reasoning.
- **`scripts/detect_drift.py`** — `WATERMARK_PHRASES` constant reused by `propose_dogma_edit.py` coherence check.
- **`scripts/audit_provenance.py`** — `extract_manifesto_axioms()` function reused by `propose_dogma_edit.py` for T1 axiom-consistency checks.
